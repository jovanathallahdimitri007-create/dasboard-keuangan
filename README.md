# 💎 FinansialKu - Dashboard Keuangan Modern (Fintech Edition)

Sistem Finansial & Dashboard Keuangan Modern all-in-one yang mendukung deployment langsung ke **Streamlit Cloud** serta **GitHub Pages**.

- 🚀 **Live Streamlit App:** [https://dasboard-keuangan-ku.streamlit.app/](https://dasboard-keuangan-ku.streamlit.app/)
- 🌐 **Live Demo (GitHub Pages):** [https://jovanathallahdimitri007-create.github.io/dasboard-keuangan/](https://jovanathallahdimitri007-create.github.io/dasboard-keuangan/)

---

## 🌟 5 Fitur Finansial Unggulan

### 1. 🎯 Monthly Budget + Smart Alerts
- Penetapan anggaran bulanan per kategori pengeluaran (Makanan, Transportasi, Tagihan, Belanja, Kesehatan).
- Visual progress bar real-time (0–100%).
- **Smart Alerts:** Notifikasi otomatis saat anggaran menyentuh **80% (Waspada)** dan **100% (Overbudget)**.
- **Run-Rate Projection:** Prediksi dini kategori yang berpotensi melampaui limit di akhir bulan berdasarkan laju pengeluaran harian.

### 2. 💎 Net Worth Tracker (Kekayaan Bersih)
- Formula Finansial Akurat:  
  $$\text{Net Worth} = \text{Total Aset (Likuid + Fisik/Investasi)} - \text{Total Liabilitas (Utang/Beban)}$$
- Mendukung pencatatan rekening bank, dompet digital, kas tunai, portofolio saham, reksadana, emas batangan, properti, kendaraan, serta kewajiban (KPR, kartu kredit, cicilan).
- **Anti Double-Counting:** Pemisahan tegas saldo kas likuid dan aset fisik agar tidak terhitung ganda.
- Grafik visual perkembangan kekayaan dari waktu ke waktu.

### 3. 💡 Financial Insights & Evaluasi Finansial
- Evaluasi pola pengeluaran berbasis data transaksi nyata.
- Identifikasi otomatis **Kategori Pengeluaran Terbesar** dan persentasenya terhadap arus kas.
- Perhitungan perubahan belanja bulanan dibandingkan bulan sebelumnya (*Month-over-Month / MoM*).
- Analisis **Tingkat Tabungan (*Savings Rate*)** dengan tolok ukur ideal (≥ 20%).
- Rekomendasi strategis penghematan konkret tanpa data palsu/halusinasi.

### 4. 🔁 Transaksi Berulang (Recurring Transactions)
- Jadwal berkala untuk pemasukan dan pengeluaran (Gaji bulanan, cicilan KPR, internet WiFi, langganan Netflix/Spotify).
- Pilihan frekuensi fleksibel: **Harian, Mingguan, Bulanan, dan Tahunan**.
- **Anti-Duplikasi:** Sistem pencegahan pencatatan ganda pada tanggal eksekusi yang sama.
- Tombol aksi cepat *"⚡ Catat Sekarang"* langsung ke buku transaksi.

### 5. 📄 Export PDF & Excel/CSV
- **Spreadsheet CSV:** Format RFC-4180 dengan UTF-8 BOM sehingga langsung terbaca rapi di Microsoft Excel dan Google Sheets.
- **Laporan PDF / Cetak:** Layout formal eksekutif lengkap dengan ringkasan laba rugi, neraca aset, performa anggaran, dan catatan kaki legal.
- **Backup & Restore JSON:** Pencadangan data menyeluruh dan pemulihan instan dengan validasi skema data.

---

## 💳 Fitur Inti Lainnya

- **Multi-Account & Transfer Antar-Rekening:** Kelola banyak rekening bank (BCA, Mandiri, BRI, dll.), e-wallet (GoPay, OVO, Dana), dan kas tunai. Pemindahan saldo internal tidak dicatat sebagai pemasukan maupun pengeluaran.
- **Buku Kas & Transaksi:** Filter pencarian teks, kategori, tipe transaksi, akun, dan sorting nominal/tanggal.
- **Dark Mode & Light Mode:** Palet tema modern Emerald & Slate yang nyaman di mata.
- **Arsip Spreadsheet Asli:** Seluruh berkas HTML spreadsheet asli (`Dashboard.html`, `Pembukuan.html`, `Olah Data.html`, `Laporan.html`, `Asset Tracker.html`) tetap dipertahankan 100% dan dapat dibuka kapan saja.

---

## 🚀 Panduan Menjalankan Aplikasi

### Opsi A: Jalankan Menggunakan Streamlit (Direkomendasikan untuk Streamlit Cloud)

1. Pasang dependensi yang dibutuhkan:
```bash
pip install -r requirements.txt
```

2. Jalankan aplikasi:
```bash
streamlit run app.py
```

3. Buka peramban di `http://localhost:8501`.

### Opsi B: Jalankan Web Static (GitHub Pages)

Cukup gunakan server HTTP bawaan Python:
```bash
python3 -m http.server 8000
```
Buka peramban di `http://localhost:8000`.

---

## ☁️ Langkah Deployment ke Streamlit Cloud

1. Buka [share.streamlit.io](https://share.streamlit.io/) dan login dengan akun GitHub Anda.
2. Klik tombol **"New app"**.
3. Pilih repository: `jovanathallahdimitri007-create/dasboard-keuangan`.
4. Branch: `main`.
5. Main file path: `app.py`.
6. Klik **"Deploy!"**. Aplikasi akan aktif secara online dalam hitungan detik.

---

## 📂 Struktur Repositori

```
dasboard-keuangan/
├── app.py                # Aplikasi utama Streamlit (Streamlit Cloud Ready)
├── requirements.txt      # Dependensi Python (streamlit, pandas, plotly, dll.)
├── .streamlit/
│   └── config.toml       # Konfigurasi tema Fintech Emerald untuk Streamlit
├── index.html            # Aplikasi web single-page (GitHub Pages Ready)
├── css/
│   └── style.css         # Design system & stylesheet modern
├── js/
│   ├── app.js            # Engine logika finansial, storage, & state management
│   ├── charts.js         # Visualisasi grafik interaktif (Chart.js)
│   └── export.js         # Generator CSV, PDF report, & JSON backup/restore
├── tests/
│   └── test_financial_engine.js # Unit test otomatis (15/15 Passed)
├── Dashboard.html        # Lembar Spreadsheet Asli (Dashboard)
├── Pembukuan.html        # Lembar Spreadsheet Asli (Pembukuan)
├── Olah Data.html        # Lembar Spreadsheet Asli (Olah Data)
├── Laporan.html          # Lembar Spreadsheet Asli (Laporan)
├── Asset Tracker.html    # Lembar Spreadsheet Asli (Asset Tracker)
├── resources/            # Aset CSS, JS, dan gambar bawaan spreadsheet
└── README.md             # Dokumentasi proyek
```

---

## ✅ Hasil Pengujian & Verifikasi

Semua fungsi kalkulasi keuangan dan ambang batas telah diuji secara otomatis melalui `node tests/test_financial_engine.js`:
- ✅ Total saldo likuid terhitung akurat.
- ✅ Net Worth secara ketat mengikuti rumus: $\text{Total Aset} - \text{Total Liabilitas}$.
- ✅ Transfer antar-akun mengurang dan menambah saldo rekening secara tepat tanpa mengubah Net Worth atau terhitung sebagai pendapatan/beban.
- ✅ Ambang batas Anggaran (Budget Alert) memicu status Waspada pada $\ge 80\%$ dan Bahaya pada $\ge 100\%$.
- ✅ Pencegahan transaksi berulang ganda (deduplikasi tanggal eksekusi) bekerja 100%.
- ✅ Rekomendasi financial insights dihasilkan dengan akurat berbasis data riil.