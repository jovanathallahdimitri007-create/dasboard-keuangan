/**
 * DASHBOARD KEUANGAN MODERN - CORE LOGIC & STATE MANAGEMENT
 * Modules: Multi-Account, Transactions, Budget & Alerts, Net Worth, Recurring, AI Insights
 * Accuracy: Integer arithmetic (IDR), zero float errors, deduplication, atomic balance tracking
 */

const STORAGE_KEYS = {
  ACCOUNTS: 'df_accounts_v2',
  TRANSACTIONS: 'df_transactions_v2',
  BUDGETS: 'df_budgets_v2',
  ASSETS_LIABILITIES: 'df_assets_liab_v2',
  RECURRING: 'df_recurring_v2',
  SAVINGS_GOALS: 'df_savings_goals_v2',
  SETTINGS: 'df_settings_v2'
};

// Initial Seed Data (Only loaded on first launch if storage is empty)
const INITIAL_ACCOUNTS = [
  { id: 'acc_1', name: 'BCA Utama', type: 'bank', balance: 25000000, number: '8271-9920-11', color: '#00529b', icon: '🏦' },
  { id: 'acc_2', name: 'Mandiri Operasional', type: 'bank', balance: 18500000, number: '142-00-192837', color: '#003366', icon: '🏛️' },
  { id: 'acc_3', name: 'GoPay / OVO', type: 'ewallet', balance: 1450000, number: '0812-3456-7890', color: '#00aed6', icon: '📱' },
  { id: 'acc_4', name: 'Kas Tunai / Dompet', type: 'cash', balance: 750000, number: '-', color: '#10b981', icon: '💵' },
  { id: 'acc_5', name: 'Bibit Reksadana', type: 'investment', balance: 15000000, number: 'INV-9921', color: '#10b981', icon: '📈' }
];

const INITIAL_ASSETS_LIABILITIES = [
  // Non-liquid physical & investment assets (Liquid balances are computed directly from accounts)
  { id: 'ast_1', name: 'Rumah Tinggal', type: 'asset', category: 'property', value: 450000000, acquisitionDate: '2022-01-15', notes: 'Nilai pasar estimasi 2026' },
  { id: 'ast_2', name: 'Mobil Honda HR-V', type: 'asset', category: 'vehicle', value: 240000000, acquisitionDate: '2023-05-10', notes: 'Kondisi mulus' },
  { id: 'ast_3', name: 'Portofolio Saham BBCA & BMRI', type: 'asset', category: 'investment', value: 65000000, acquisitionDate: '2024-02-01', notes: 'Ajaib Sekuritas' },
  { id: 'ast_4', name: 'Tabungan Emas Antam (25g)', type: 'asset', category: 'gold', value: 37500000, acquisitionDate: '2023-11-20', notes: 'Brankas safe deposit box' },
  // Liabilities
  { id: 'lia_1', name: 'KPR Rumah Bank Mandiri', type: 'liability', category: 'mortgage', value: 185000000, dueDate: '2032-12-01', notes: 'Sisa tenor 6 tahun' },
  { id: 'lia_2', name: 'Kartu Kredit BCA Everyday', type: 'liability', category: 'credit_card', value: 4200000, dueDate: '2026-11-15', notes: 'Tagihan bulan berjalan' }
];

const INITIAL_BUDGETS = [
  { id: 'bg_1', category: 'Makanan & Minuman', limit: 4500000, period: '2026-10' },
  { id: 'bg_2', category: 'Transportasi & Bensin', limit: 1800000, period: '2026-10' },
  { id: 'bg_3', category: 'Tagihan & Utilitas', limit: 2500000, period: '2026-10' },
  { id: 'bg_4', category: 'Belanja & Hiburan', limit: 2000000, period: '2026-10' },
  { id: 'bg_5', category: 'Kesehatan & Asuransi', limit: 1500000, period: '2026-10' }
];

const INITIAL_RECURRING = [
  { id: 'rec_1', name: 'Gaji Bulanan', type: 'income', amount: 32000000, category: 'Gaji & Pendapatan', accountId: 'acc_1', frequency: 'monthly', dayOfMonth: 25, active: true, lastRun: '2026-09-25' },
  { id: 'rec_2', name: 'Cicilan KPR', type: 'expense', amount: 4850000, category: 'Tagihan & Utilitas', accountId: 'acc_2', frequency: 'monthly', dayOfMonth: 5, active: true, lastRun: '2026-10-05' },
  { id: 'rec_3', name: 'Internet & WiFi Fiber', type: 'expense', amount: 450000, category: 'Tagihan & Utilitas', accountId: 'acc_1', frequency: 'monthly', dayOfMonth: 15, active: true, lastRun: '2026-10-15' },
  { id: 'rec_4', name: 'Langganan Netflix & Spotify', type: 'expense', amount: 215000, category: 'Belanja & Hiburan', accountId: 'acc_3', frequency: 'monthly', dayOfMonth: 12, active: true, lastRun: '2026-10-12' }
];

const INITIAL_TRANSACTIONS = [
  { id: 'tx_1', date: '2026-10-01', type: 'income', amount: 32000000, category: 'Gaji & Pendapatan', accountId: 'acc_1', description: 'Gaji Pokok Oktober 2026' },
  { id: 'tx_2', date: '2026-10-02', type: 'transfer', amount: 5000000, accountId: 'acc_1', toAccountId: 'acc_2', description: 'Alokasi Rekening Operasional' },
  { id: 'tx_3', date: '2026-10-03', type: 'transfer', amount: 2000000, accountId: 'acc_1', toAccountId: 'acc_3', description: 'Top Up E-Wallet Bulanan' },
  { id: 'tx_4', date: '2026-10-05', type: 'expense', amount: 4850000, category: 'Tagihan & Utilitas', accountId: 'acc_2', description: 'Bayar Cicilan KPR Mandiri' },
  { id: 'tx_5', date: '2026-10-07', type: 'expense', amount: 1250000, category: 'Makanan & Minuman', accountId: 'acc_3', description: 'Belanja Supermarket Mingguan' },
  { id: 'tx_6', date: '2026-10-09', type: 'expense', amount: 350000, category: 'Transportasi & Bensin', accountId: 'acc_3', description: 'Isi Bensin Pertamax Full Tank' },
  { id: 'tx_7', date: '2026-10-10', type: 'expense', amount: 650000, category: 'Makanan & Minuman', accountId: 'acc_4', description: 'Makan Malam Keluarga Akhir Pekan' },
  { id: 'tx_8', date: '2026-10-12', type: 'expense', amount: 215000, category: 'Belanja & Hiburan', accountId: 'acc_3', description: 'Langganan Netflix & Spotify' },
  { id: 'tx_9', date: '2026-10-14', type: 'income', amount: 4500000, category: 'Investasi & Bonus', accountId: 'acc_5', description: 'Dividen Saham BBCA Semester 2' },
  { id: 'tx_10', date: '2026-10-15', type: 'expense', amount: 450000, category: 'Tagihan & Utilitas', accountId: 'acc_1', description: 'Tagihan Internet MyRepublic' },
  { id: 'tx_11', date: '2026-10-16', type: 'expense', amount: 820000, category: 'Kesehatan & Asuransi', accountId: 'acc_1', description: 'Medical Checkup & Vitamin' },
  { id: 'tx_12', date: '2026-10-17', type: 'expense', amount: 540000, category: 'Belanja & Hiburan', accountId: 'acc_3', description: 'Beli Buku & Kebutuhan Kantor' }
];

// App State Manager
class FinanceApp {
  constructor() {
    this.accounts = this.loadData(STORAGE_KEYS.ACCOUNTS, INITIAL_ACCOUNTS);
    this.transactions = this.loadData(STORAGE_KEYS.TRANSACTIONS, INITIAL_TRANSACTIONS);
    this.budgets = this.loadData(STORAGE_KEYS.BUDGETS, INITIAL_BUDGETS);
    this.assetsLiabilities = this.loadData(STORAGE_KEYS.ASSETS_LIABILITIES, INITIAL_ASSETS_LIABILITIES);
    this.recurring = this.loadData(STORAGE_KEYS.RECURRING, INITIAL_RECURRING);
    this.settings = this.loadData(STORAGE_KEYS.SETTINGS, { theme: 'dark', currency: 'IDR' });
    
    // Sort transactions latest first
    this.transactions.sort((a, b) => new Date(b.date) - new Date(a.date));
    this.recalculateAccountBalances();
  }

  loadData(key, fallback) {
    try {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : fallback;
    } catch (e) {
      console.error(`Gagal membaca ${key} dari localStorage:`, e);
      return fallback;
    }
  }

  saveData(key, data) {
    try {
      localStorage.setItem(key, JSON.stringify(data));
    } catch (e) {
      console.error(`Gagal menyimpan ${key} ke localStorage:`, e);
    }
  }

  saveAll() {
    this.saveData(STORAGE_KEYS.ACCOUNTS, this.accounts);
    this.saveData(STORAGE_KEYS.TRANSACTIONS, this.transactions);
    this.saveData(STORAGE_KEYS.BUDGETS, this.budgets);
    this.saveData(STORAGE_KEYS.ASSETS_LIABILITIES, this.assetsLiabilities);
    this.saveData(STORAGE_KEYS.RECURRING, this.recurring);
    this.saveData(STORAGE_KEYS.SETTINGS, this.settings);
  }

  // ==========================================
  // 1. FINANCIAL ARITHMETIC & ATOMIC BALANCE
  // ==========================================

  /**
   * Recalculates all account balances starting from their initial baseline
   * Strictly avoids double-counting and floating-point errors
   */
  recalculateAccountBalances() {
    // Map initial baseline
    const balanceMap = {};
    this.accounts.forEach(acc => {
      // Keep baseline in initialBalance if available, or initialize
      if (acc.initialBalance === undefined) {
        acc.initialBalance = Math.round(acc.balance || 0);
      }
      balanceMap[acc.id] = acc.initialBalance;
    });

    // Apply transactions chronologically
    const sortedTx = [...this.transactions].sort((a, b) => new Date(a.date) - new Date(b.date));
    
    sortedTx.forEach(tx => {
      const amt = Math.round(Number(tx.amount) || 0);
      if (tx.type === 'income') {
        if (balanceMap[tx.accountId] !== undefined) {
          balanceMap[tx.accountId] += amt;
        }
      } else if (tx.type === 'expense') {
        if (balanceMap[tx.accountId] !== undefined) {
          balanceMap[tx.accountId] -= amt;
        }
      } else if (tx.type === 'transfer') {
        // Source account decreases
        if (balanceMap[tx.accountId] !== undefined) {
          balanceMap[tx.accountId] -= amt;
        }
        // Destination account increases
        if (balanceMap[tx.toAccountId] !== undefined) {
          balanceMap[tx.toAccountId] += amt;
        }
      }
    });

    // Write updated balance back to accounts
    this.accounts.forEach(acc => {
      acc.balance = balanceMap[acc.id] !== undefined ? balanceMap[acc.id] : 0;
    });
    this.saveData(STORAGE_KEYS.ACCOUNTS, this.accounts);
  }

  formatIDR(nominal) {
    const val = Math.round(Number(nominal) || 0);
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(val).replace('Rp', 'Rp ');
  }

  // ==========================================
  // 2. DASHBOARD & SUMMARY CALCULATIONS
  // ==========================================

  getSummary(monthStr) {
    // monthStr format: 'YYYY-MM' (e.g., '2026-10')
    const currentMonth = monthStr || new Date().toISOString().slice(0, 7);
    
    let totalLiquidBalance = 0;
    this.accounts.forEach(acc => {
      totalLiquidBalance += Math.round(acc.balance || 0);
    });

    let monthIncome = 0;
    let monthExpense = 0;
    let totalLifetimeIncome = 0;
    let totalLifetimeExpense = 0;

    this.transactions.forEach(tx => {
      const amt = Math.round(Number(tx.amount) || 0);
      const txMonth = tx.date.slice(0, 7);

      if (tx.type === 'income') {
        totalLifetimeIncome += amt;
        if (txMonth === currentMonth) monthIncome += amt;
      } else if (tx.type === 'expense') {
        totalLifetimeExpense += amt;
        if (txMonth === currentMonth) monthExpense += amt;
      }
      // Note: Transfers are strictly ignored in Income/Expense totals!
    });

    const netProfit = monthIncome - monthExpense;

    // Net Worth Calculation: Total Aset - Total Liabilitas
    // Liquid assets (bank/ewallet/cash) + Non-liquid physical & investment assets
    let totalNonLiquidAssets = 0;
    let totalLiabilities = 0;

    this.assetsLiabilities.forEach(item => {
      const val = Math.round(Number(item.value) || 0);
      if (item.type === 'asset') {
        totalNonLiquidAssets += val;
      } else if (item.type === 'liability') {
        totalLiabilities += val;
      }
    });

    const totalAssets = totalLiquidBalance + totalNonLiquidAssets;
    const netWorth = totalAssets - totalLiabilities;

    // Month-End Balance Prediction (Mathematical Run-rate)
    const today = new Date();
    const daysInMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
    const currentDay = Math.min(today.getDate(), daysInMonth);
    const daysRemaining = Math.max(0, daysInMonth - currentDay);

    const avgDailyIncome = currentDay > 0 ? (monthIncome / currentDay) : 0;
    const avgDailyExpense = currentDay > 0 ? (monthExpense / currentDay) : 0;
    const dailyNet = avgDailyIncome - avgDailyExpense;
    const projectedEndOfMonth = Math.round(totalLiquidBalance + (dailyNet * daysRemaining));

    return {
      currentMonth,
      totalLiquidBalance,
      monthIncome,
      monthExpense,
      netProfit,
      totalAssets,
      totalNonLiquidAssets,
      totalLiabilities,
      netWorth,
      projectedEndOfMonth,
      daysRemaining,
      avgDailyExpense: Math.round(avgDailyExpense)
    };
  }

  // ==========================================
  // 3. MONTHLY BUDGET & SMART ALERTS
  // ==========================================

  getBudgetStatus(monthStr) {
    const currentMonth = monthStr || new Date().toISOString().slice(0, 7);
    
    // Sum expense per category for the selected month
    const expensePerCategory = {};
    this.transactions.forEach(tx => {
      if (tx.type === 'expense' && tx.date.startsWith(currentMonth)) {
        const cat = tx.category || 'Lain-lain';
        expensePerCategory[cat] = (expensePerCategory[cat] || 0) + Math.round(Number(tx.amount) || 0);
      }
    });

    const today = new Date();
    const daysInMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
    const currentDay = Math.min(today.getDate(), daysInMonth);
    const daysRemaining = Math.max(0, daysInMonth - currentDay);

    return this.budgets.map(b => {
      const spent = expensePerCategory[b.category] || 0;
      const limit = Math.round(Number(b.limit) || 0);
      const remaining = limit - spent;
      const percentage = limit > 0 ? Math.min(Math.round((spent / limit) * 100), 999) : 0;

      // Run-rate projection to detect potential overbudget
      const dailySpend = currentDay > 0 ? (spent / currentDay) : 0;
      const projectedTotal = Math.round(spent + (dailySpend * daysRemaining));
      const isProjectedOverbudget = projectedTotal > limit;

      let status = 'normal'; // 'normal', 'warning' (>=80%), 'danger' (>=100%)
      if (percentage >= 100) {
        status = 'danger';
      } else if (percentage >= 80) {
        status = 'warning';
      }

      return {
        ...b,
        spent,
        remaining,
        percentage,
        status,
        projectedTotal,
        isProjectedOverbudget
      };
    });
  }

  addBudget(category, limit, period) {
    if (!category || !limit || Number(limit) <= 0) {
      throw new Error('Kategori dan batas nominal anggaran harus diisi dengan benar.');
    }
    const cleanLimit = Math.round(Number(limit));
    // Check if category already has a budget for this period
    const existing = this.budgets.find(b => b.category.toLowerCase() === category.toLowerCase());
    if (existing) {
      existing.limit = cleanLimit;
      existing.period = period || new Date().toISOString().slice(0, 7);
    } else {
      this.budgets.push({
        id: 'bg_' + Date.now(),
        category,
        limit: cleanLimit,
        period: period || new Date().toISOString().slice(0, 7)
      });
    }
    this.saveData(STORAGE_KEYS.BUDGETS, this.budgets);
  }

  deleteBudget(id) {
    this.budgets = this.budgets.filter(b => b.id !== id);
    this.saveData(STORAGE_KEYS.BUDGETS, this.budgets);
  }

  // ==========================================
  // 4. NET WORTH & ASSETS/LIABILITIES
  // ==========================================

  addAssetLiability(item) {
    if (!item.name || !item.value || Number(item.value) <= 0) {
      throw new Error('Nama aset/utang dan nilai nominal harus diisi dengan benar.');
    }
    const cleanItem = {
      id: item.id || ('ast_' + Date.now()),
      name: item.name.trim(),
      type: item.type === 'liability' ? 'liability' : 'asset',
      category: item.category || 'general',
      value: Math.round(Number(item.value)),
      acquisitionDate: item.acquisitionDate || new Date().toISOString().slice(0, 10),
      notes: item.notes || ''
    };

    if (item.id) {
      const idx = this.assetsLiabilities.findIndex(a => a.id === item.id);
      if (idx !== -1) {
        this.assetsLiabilities[idx] = cleanItem;
      } else {
        this.assetsLiabilities.push(cleanItem);
      }
    } else {
      this.assetsLiabilities.push(cleanItem);
    }
    this.saveData(STORAGE_KEYS.ASSETS_LIABILITIES, this.assetsLiabilities);
  }

  deleteAssetLiability(id) {
    this.assetsLiabilities = this.assetsLiabilities.filter(a => a.id !== id);
    this.saveData(STORAGE_KEYS.ASSETS_LIABILITIES, this.assetsLiabilities);
  }

  // ==========================================
  // 5. RECURRING TRANSACTIONS & AUTO-RUNNER
  // ==========================================

  addRecurring(rec) {
    if (!rec.name || !rec.amount || Number(rec.amount) <= 0 || !rec.accountId) {
      throw new Error('Nama, nominal, dan akun transaksi berulang harus diisi.');
    }
    const newRec = {
      id: rec.id || ('rec_' + Date.now()),
      name: rec.name.trim(),
      type: rec.type || 'expense',
      amount: Math.round(Number(rec.amount)),
      category: rec.category || 'Lain-lain',
      accountId: rec.accountId,
      toAccountId: rec.toAccountId || null,
      frequency: rec.frequency || 'monthly', // 'daily', 'weekly', 'monthly', 'yearly'
      dayOfMonth: Number(rec.dayOfMonth) || 1,
      active: rec.active !== undefined ? rec.active : true,
      lastRun: rec.lastRun || null,
      notes: rec.notes || ''
    };

    if (rec.id) {
      const idx = this.recurring.findIndex(r => r.id === rec.id);
      if (idx !== -1) this.recurring[idx] = newRec;
      else this.recurring.push(newRec);
    } else {
      this.recurring.push(newRec);
    }
    this.saveData(STORAGE_KEYS.RECURRING, this.recurring);
  }

  deleteRecurring(id) {
    this.recurring = this.recurring.filter(r => r.id !== id);
    this.saveData(STORAGE_KEYS.RECURRING, this.recurring);
  }

  toggleRecurringActive(id) {
    const rec = this.recurring.find(r => r.id === id);
    if (rec) {
      rec.active = !rec.active;
      this.saveData(STORAGE_KEYS.RECURRING, this.recurring);
    }
  }

  /**
   * Execute a recurring item into actual transactions with deduplication check
   */
  processRecurringItem(recId, executionDateStr) {
    const rec = this.recurring.find(r => r.id === recId);
    if (!rec || !rec.active) return false;

    const date = executionDateStr || new Date().toISOString().slice(0, 10);

    // Prevent double execution on the same date for this recurring item
    const alreadyLogged = this.transactions.some(tx => 
      tx.recurringId === rec.id && tx.date === date
    );
    if (alreadyLogged) {
      throw new Error(`Transaksi berulang "${rec.name}" sudah pernah dicatat untuk tanggal ${date}.`);
    }

    const newTx = {
      id: 'tx_rec_' + Date.now(),
      date,
      type: rec.type,
      amount: rec.amount,
      category: rec.category,
      accountId: rec.accountId,
      toAccountId: rec.toAccountId,
      description: `[Otomatis: ${rec.name}] ${rec.notes || ''}`.trim(),
      recurringId: rec.id
    };

    this.transactions.unshift(newTx);
    rec.lastRun = date;

    this.recalculateAccountBalances();
    this.saveData(STORAGE_KEYS.TRANSACTIONS, this.transactions);
    this.saveData(STORAGE_KEYS.RECURRING, this.recurring);
    return true;
  }

  // ==========================================
  // 6. TRANSACTIONS CRUD & TRANSFERS
  // ==========================================

  addTransaction(tx) {
    if (!tx.amount || Number(tx.amount) <= 0) {
      throw new Error('Nominal transaksi harus lebih dari 0.');
    }
    if (!tx.accountId) {
      throw new Error('Pilih akun transaksi.');
    }
    if (tx.type === 'transfer') {
      if (!tx.toAccountId) {
        throw new Error('Pilih akun tujuan untuk transfer antar-rekening.');
      }
      if (tx.accountId === tx.toAccountId) {
        throw new Error('Akun asal dan akun tujuan tidak boleh sama.');
      }
    }

    const cleanTx = {
      id: tx.id || ('tx_' + Date.now()),
      date: tx.date || new Date().toISOString().slice(0, 10),
      type: tx.type || 'expense',
      amount: Math.round(Number(tx.amount)),
      category: tx.category || (tx.type === 'transfer' ? 'Transfer Saldo' : 'Lain-lain'),
      accountId: tx.accountId,
      toAccountId: tx.type === 'transfer' ? tx.toAccountId : null,
      description: (tx.description || '').trim(),
      recurringId: tx.recurringId || null
    };

    if (tx.id) {
      const idx = this.transactions.findIndex(t => t.id === tx.id);
      if (idx !== -1) this.transactions[idx] = cleanTx;
      else this.transactions.unshift(cleanTx);
    } else {
      this.transactions.unshift(cleanTx);
    }

    // Re-sort transactions
    this.transactions.sort((a, b) => new Date(b.date) - new Date(a.date));
    this.recalculateAccountBalances();
    this.saveData(STORAGE_KEYS.TRANSACTIONS, this.transactions);
  }

  deleteTransaction(id) {
    this.transactions = this.transactions.filter(t => t.id !== id);
    this.recalculateAccountBalances();
    this.saveData(STORAGE_KEYS.TRANSACTIONS, this.transactions);
  }

  // ==========================================
  // 7. ACCOUNTS CRUD
  // ==========================================

  addAccount(acc) {
    if (!acc.name || acc.balance === undefined) {
      throw new Error('Nama akun dan saldo awal wajib diisi.');
    }
    const cleanAcc = {
      id: acc.id || ('acc_' + Date.now()),
      name: acc.name.trim(),
      type: acc.type || 'bank',
      balance: Math.round(Number(acc.balance)),
      initialBalance: Math.round(Number(acc.balance)),
      number: acc.number || '-',
      color: acc.color || '#10b981',
      icon: acc.icon || '🏦'
    };

    if (acc.id) {
      const idx = this.accounts.findIndex(a => a.id === acc.id);
      if (idx !== -1) {
        cleanAcc.balance = this.accounts[idx].balance; // Preserve running balance
        cleanAcc.initialBalance = this.accounts[idx].initialBalance;
        this.accounts[idx] = { ...this.accounts[idx], ...cleanAcc };
      } else {
        this.accounts.push(cleanAcc);
      }
    } else {
      this.accounts.push(cleanAcc);
    }

    this.recalculateAccountBalances();
    this.saveData(STORAGE_KEYS.ACCOUNTS, this.accounts);
  }

  deleteAccount(id) {
    if (this.accounts.length <= 1) {
      throw new Error('Minimal harus memiliki satu akun aktif.');
    }
    // Check if any transactions reference this account
    const hasTx = this.transactions.some(tx => tx.accountId === id || tx.toAccountId === id);
    if (hasTx) {
      throw new Error('Akun ini memiliki riwayat transaksi terkait. Hapus transaksi terkait terlebih dahulu.');
    }
    this.accounts = this.accounts.filter(a => a.id !== id);
    this.saveData(STORAGE_KEYS.ACCOUNTS, this.accounts);
  }

  // ==========================================
  // 8. ALGORITHMIC FINANCIAL INSIGHTS
  // ==========================================

  generateInsights(monthStr) {
    const currentMonth = monthStr || new Date().toISOString().slice(0, 7);
    
    // Previous month string
    const d = new Date(currentMonth + '-01');
    d.setMonth(d.getMonth() - 1);
    const prevMonth = d.toISOString().slice(0, 7);

    const currentMonthTx = this.transactions.filter(t => t.date.startsWith(currentMonth));
    const prevMonthTx = this.transactions.filter(t => t.date.startsWith(prevMonth));

    if (currentMonthTx.length < 2) {
      return {
        hasData: false,
        message: 'Data transaksi pada bulan ini belum mencukupi (minimal butuh 2 transaksi) untuk menghasilkan analisis finansial yang akurat.'
      };
    }

    // Current month calculations
    let currentIncome = 0;
    let currentExpense = 0;
    const catExpense = {};

    currentMonthTx.forEach(tx => {
      const amt = Math.round(Number(tx.amount) || 0);
      if (tx.type === 'income') currentIncome += amt;
      else if (tx.type === 'expense') {
        currentExpense += amt;
        const cat = tx.category || 'Lain-lain';
        catExpense[cat] = (catExpense[cat] || 0) + amt;
      }
    });

    // Previous month calculations
    let prevExpense = 0;
    prevMonthTx.forEach(tx => {
      if (tx.type === 'expense') {
        prevExpense += Math.round(Number(tx.amount) || 0);
      }
    });

    // Find top expense category
    let topCategory = null;
    let topCategoryAmount = 0;
    for (const [cat, amt] of Object.entries(catExpense)) {
      if (amt > topCategoryAmount) {
        topCategoryAmount = amt;
        topCategory = cat;
      }
    }

    const topCategoryPercent = currentExpense > 0 
      ? Math.round((topCategoryAmount / currentExpense) * 100) 
      : 0;

    // Month-over-Month change
    let momChangePercent = 0;
    let momChangeType = 'same';
    if (prevExpense > 0) {
      momChangePercent = Math.round(((currentExpense - prevExpense) / prevExpense) * 100);
      momChangeType = momChangePercent > 0 ? 'increase' : (momChangePercent < 0 ? 'decrease' : 'same');
    }

    // Savings Rate (Rasio Tabungan)
    const savingsRate = currentIncome > 0 
      ? Math.round(((currentIncome - currentExpense) / currentIncome) * 100) 
      : 0;

    // Actionable Recommendations
    const recommendations = [];

    if (topCategory && topCategoryPercent >= 35) {
      recommendations.push({
        type: 'warning',
        title: `Dominasi Pengeluaran pada ${topCategory}`,
        detail: `Kategori ${topCategory} memakan ${topCategoryPercent}% (${this.formatIDR(topCategoryAmount)}) dari seluruh pengeluaran bulan ini. Pertimbangkan untuk membatasi belanja non-esensial di kategori ini.`
      });
    }

    if (savingsRate >= 20) {
      recommendations.push({
        type: 'positive',
        title: `Tingkat Tabungan Sehat (${savingsRate}%)`,
        detail: `Anda berhasil menyisihkan ${savingsRate}% dari pendapatan bulan ini ke arus kas positif. Pertimbangkan mengalokasikan sebagian ke instrumen investasi berimbal hasil stabil.`
      });
    } else if (savingsRate < 10 && savingsRate >= 0) {
      recommendations.push({
        type: 'info',
        title: `Rasio Tabungan Rendah (${savingsRate}%)`,
        detail: `Rasio tabungan Anda saat ini berada di bawah rekomendasi ideal (20%). Usahakan menekan pengeluaran tersier agar memiliki bantalan dana darurat minimal 3 bulan.`
      });
    } else if (savingsRate < 0) {
      recommendations.push({
        type: 'danger',
        title: `Defisit Arus Kas (${this.formatIDR(Math.abs(currentIncome - currentExpense))})`,
        detail: `Pengeluaran bulan ini melebihi total pendapatan Anda. Periksa pos tagihan dan batasi pembelian sekunder untuk menghindari pengikisan saldo pokok.`
      });
    }

    // Budget overruns alert check
    const budgetStatus = this.getBudgetStatus(currentMonth);
    const overBudgets = budgetStatus.filter(b => b.status === 'danger' || b.status === 'warning');
    if (overBudgets.length > 0) {
      const names = overBudgets.map(b => `${b.category} (${b.percentage}%)`).join(', ');
      recommendations.push({
        type: 'alert',
        title: `Peringatan Batas Anggaran`,
        detail: `${overBudgets.length} kategori telah mendekati atau melampaui limit anggaran: ${names}.`
      });
    }

    return {
      hasData: true,
      currentMonth,
      currentIncome,
      currentExpense,
      topCategory,
      topCategoryAmount,
      topCategoryPercent,
      prevExpense,
      momChangePercent: Math.abs(momChangePercent),
      momChangeType,
      savingsRate,
      recommendations
    };
  }
}

// Global App Instance
window.FinanceAppInstance = new FinanceApp();
