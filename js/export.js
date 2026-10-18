/**
 * DASHBOARD KEUANGAN MODERN - EXPORT & REPORTING MODULE
 * Supports: CSV/Excel Export (RFC-4180 with UTF-8 BOM), Print/PDF Report, Full JSON Backup & Restore
 */

class FinanceExporter {
  constructor(app) {
    this.app = app;
  }

  /**
   * Export transactions to CSV formatted with UTF-8 BOM for Microsoft Excel compatibility
   */
  exportTransactionsToCSV(filterOptions = {}) {
    const txList = this.app.transactions.filter(tx => {
      if (filterOptions.type && filterOptions.type !== 'all' && tx.type !== filterOptions.type) return false;
      if (filterOptions.accountId && filterOptions.accountId !== 'all' && tx.accountId !== filterOptions.accountId && tx.toAccountId !== filterOptions.accountId) return false;
      if (filterOptions.month && !tx.date.startsWith(filterOptions.month)) return false;
      return true;
    });

    if (txList.length === 0) {
      throw new Error('Tidak ada data transaksi yang cocok dengan filter untuk diekspor.');
    }

    // CSV Headers
    const headers = ['ID Transaksi', 'Tanggal', 'Tipe', 'Kategori', 'Nominal (IDR)', 'Akun Asal', 'Akun Tujuan', 'Deskripsi'];
    
    const accountMap = {};
    this.app.accounts.forEach(a => accountMap[a.id] = a.name);

    const rows = txList.map(tx => {
      const typeLabel = tx.type === 'income' ? 'Pemasukan' : (tx.type === 'expense' ? 'Pengeluaran' : 'Transfer');
      const fromAcc = accountMap[tx.accountId] || tx.accountId;
      const toAcc = tx.toAccountId ? (accountMap[tx.toAccountId] || tx.toAccountId) : '-';
      const cleanDesc = (tx.description || '').replace(/"/g, '""');

      return [
        `"${tx.id}"`,
        `"${tx.date}"`,
        `"${typeLabel}"`,
        `"${tx.category || '-'}"`,
        tx.amount,
        `"${fromAcc}"`,
        `"${toAcc}"`,
        `"${cleanDesc}"`
      ].join(',');
    });

    // Prepend UTF-8 BOM (\uFEFF) so Excel opens UTF-8 properly
    const csvContent = '\uFEFF' + [headers.join(','), ...rows].join('\r\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    const dateStr = new Date().toISOString().slice(0, 10);
    link.download = `laporan_transaksi_keuangan_${dateStr}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    return txList.length;
  }

  /**
   * Generates a clean, professional print/PDF report
   */
  generatePrintReport(monthStr) {
    const summary = this.app.getSummary(monthStr);
    const budgets = this.app.getBudgetStatus(monthStr);
    const insights = this.app.generateInsights(monthStr);

    const monthFormatted = new Date((monthStr || summary.currentMonth) + '-01')
      .toLocaleDateString('id-ID', { month: 'long', year: 'numeric' });

    // Build print HTML content in an invisible iframe
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      throw new Error('Pop-up window diblokir oleh browser. Izinkan pop-up untuk mencetak laporan.');
    }

    const html = `
      <!DOCTYPE html>
      <html lang="id">
      <head>
        <meta charset="UTF-8">
        <title>Laporan Keuangan Eksekutif - ${monthFormatted}</title>
        <style>
          @page { size: A4 portrait; margin: 15mm; }
          body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            color: #1e293b;
            line-height: 1.4;
            padding: 20px;
          }
          .report-header {
            border-bottom: 2px solid #10b981;
            padding-bottom: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
          }
          .report-header h1 { margin: 0; color: #0f172a; font-size: 22px; }
          .report-header p { margin: 4px 0 0; color: #64748b; font-size: 13px; }
          .badge {
            background: #ecfdf5;
            color: #059669;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
          }
          .metrics-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
          }
          .metrics-table td {
            padding: 12px 14px;
            border: 1px solid #e2e8f0;
            vertical-align: top;
          }
          .metric-label { font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; }
          .metric-val { font-size: 16px; font-weight: bold; margin-top: 4px; color: #0f172a; }
          .val-income { color: #10b981; }
          .val-expense { color: #ef4444; }
          .val-networth { color: #2563eb; }

          h2 { font-size: 14px; color: #0f172a; margin-top: 20px; margin-bottom: 8px; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; }
          table.data-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 12px;
          }
          table.data-table th {
            background: #f1f5f9;
            padding: 8px 10px;
            text-align: left;
            border: 1px solid #cbd5e1;
            font-weight: bold;
            color: #475569;
          }
          table.data-table td {
            padding: 7px 10px;
            border: 1px solid #e2e8f0;
          }
          .text-right { text-align: right; }
          .footer-note {
            margin-top: 30px;
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
            border-top: 1px dashed #cbd5e1;
            padding-top: 10px;
          }
        </style>
      </head>
      <body>
        <div class="report-header">
          <div>
            <h1>LAPORAN KEUANGAN & NERACA BERSIH</h1>
            <p>Periode Pelaporan: <strong>${monthFormatted}</strong> | Dicetak: ${new Date().toLocaleDateString('id-ID', { dateStyle: 'full' })}</p>
          </div>
          <div>
            <span class="badge">FINTECH RESMI</span>
          </div>
        </div>

        <table class="metrics-table">
          <tr>
            <td>
              <div class="metric-label">Total Pemasukan</div>
              <div class="metric-val val-income">${this.app.formatIDR(summary.monthIncome)}</div>
            </td>
            <td>
              <div class="metric-label">Total Pengeluaran</div>
              <div class="metric-val val-expense">${this.app.formatIDR(summary.monthExpense)}</div>
            </td>
            <td>
              <div class="metric-label">Surplus / Defisit Arus Kas</div>
              <div class="metric-val">${this.app.formatIDR(summary.netProfit)}</div>
            </td>
          </tr>
          <tr>
            <td>
              <div class="metric-label">Total Aset (Likuid + Non-Likuid)</div>
              <div class="metric-val">${this.app.formatIDR(summary.totalAssets)}</div>
            </td>
            <td>
              <div class="metric-label">Total Liabilitas (Utang/Cicilan)</div>
              <div class="metric-val">${this.app.formatIDR(summary.totalLiabilities)}</div>
            </td>
            <td>
              <div class="metric-label">Kekayaan Bersih (Net Worth)</div>
              <div class="metric-val val-networth">${this.app.formatIDR(summary.netWorth)}</div>
            </td>
          </tr>
        </table>

        <h2>1. KINERJA ANGGARAN & REALISASI (BUDGET)</h2>
        <table class="data-table">
          <thead>
            <tr>
              <th>Kategori</th>
              <th class="text-right">Batas Anggaran</th>
              <th class="text-right">Realisasi Pengeluaran</th>
              <th class="text-right">Sisa Anggaran</th>
              <th class="text-right">Utilisasi (%)</th>
            </tr>
          </thead>
          <tbody>
            ${budgets.map(b => `
              <tr>
                <td><strong>${b.category}</strong></td>
                <td class="text-right">${this.app.formatIDR(b.limit)}</td>
                <td class="text-right">${this.app.formatIDR(b.spent)}</td>
                <td class="text-right">${this.app.formatIDR(b.remaining)}</td>
                <td class="text-right" style="font-weight: bold; color: ${b.percentage >= 100 ? '#ef4444' : (b.percentage >= 80 ? '#f59e0b' : '#10b981')}">${b.percentage}%</td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <h2>2. SALDO REKENING & DOMPET (ASET LIKUID)</h2>
        <table class="data-table">
          <thead>
            <tr>
              <th>Nama Akun / Bank</th>
              <th>Tipe</th>
              <th>Nomor Rekening</th>
              <th class="text-right">Saldo Terkini</th>
            </tr>
          </thead>
          <tbody>
            ${this.app.accounts.map(a => `
              <tr>
                <td>${a.icon} ${a.name}</td>
                <td>${a.type.toUpperCase()}</td>
                <td>${a.number}</td>
                <td class="text-right"><strong>${this.app.formatIDR(a.balance)}</strong></td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <h2>3. REKAPITULASI ASET FISIK & UTANG</h2>
        <table class="data-table">
          <thead>
            <tr>
              <th>Deskripsi Aset / Liabilitas</th>
              <th>Klasifikasi</th>
              <th class="text-right">Nilai / Saldo</th>
              <th>Catatan</th>
            </tr>
          </thead>
          <tbody>
            ${this.app.assetsLiabilities.map(item => `
              <tr>
                <td>${item.name}</td>
                <td><strong>${item.type === 'asset' ? 'ASET' : 'LIABILITAS / UTANG'}</strong> (${item.category})</td>
                <td class="text-right">${this.app.formatIDR(item.value)}</td>
                <td>${item.notes || '-'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <div class="footer-note">
          Laporan ini dihasilkan secara otomatis oleh Dashboard Keuangan Modern pada ${new Date().toLocaleString('id-ID')}. Dokumen rahasia untuk penggunaan pribadi & evaluasi finansial.
        </div>
      </body>
      </html>
    `;

    printWindow.document.open();
    printWindow.document.write(html);
    printWindow.document.close();

    // Trigger browser print
    setTimeout(() => {
      printWindow.focus();
      printWindow.print();
    }, 400);
  }

  /**
   * Export full JSON backup of all financial data
   */
  exportJSONBackup() {
    const backupData = {
      appVersion: '2.0.0',
      exportedAt: new Date().toISOString(),
      accounts: this.app.accounts,
      transactions: this.app.transactions,
      budgets: this.app.budgets,
      assetsLiabilities: this.app.assetsLiabilities,
      recurring: this.app.recurring,
      settings: this.app.settings
    };

    const jsonStr = JSON.stringify(backupData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    const dateStr = new Date().toISOString().slice(0, 10);
    link.download = `backup_keuangan_lengkap_${dateStr}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * Import & validate JSON backup file
   */
  async importJSONBackup(file) {
    return new Promise((resolve, reject) => {
      if (!file) {
        return reject(new Error('Pilih file backup JSON terlebih dahulu.'));
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const parsed = JSON.parse(e.target.result);
          
          // Schema validation
          if (!parsed.accounts || !Array.isArray(parsed.accounts)) {
            throw new Error('Format file backup tidak valid: atribut accounts tidak ditemukan.');
          }
          if (!parsed.transactions || !Array.isArray(parsed.transactions)) {
            throw new Error('Format file backup tidak valid: atribut transactions tidak ditemukan.');
          }

          // Restore state
          this.app.accounts = parsed.accounts;
          this.app.transactions = parsed.transactions;
          if (parsed.budgets && Array.isArray(parsed.budgets)) this.app.budgets = parsed.budgets;
          if (parsed.assetsLiabilities && Array.isArray(parsed.assetsLiabilities)) this.app.assetsLiabilities = parsed.assetsLiabilities;
          if (parsed.recurring && Array.isArray(parsed.recurring)) this.app.recurring = parsed.recurring;
          if (parsed.settings) this.app.settings = parsed.settings;

          this.app.recalculateAccountBalances();
          this.app.saveAll();

          resolve({
            accountsCount: this.app.accounts.length,
            txCount: this.app.transactions.length
          });
        } catch (err) {
          reject(new Error(`Gagal membaca file backup: ${err.message}`));
        }
      };

      reader.onerror = () => reject(new Error('Gagal membaca file backup.'));
      reader.readAsText(file);
    });
  }
}

window.FinanceExporterInstance = new FinanceExporter(window.FinanceAppInstance);
