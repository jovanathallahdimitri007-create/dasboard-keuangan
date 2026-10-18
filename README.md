# 🏫 FinansialKu - Sistem Keuangan Kelas, Korlas & Portal Siswa Multi-Kelas

Aplikasi manajemen keuangan online terpadu untuk sekolah, koordinator kelas (**Korlas**), bendahara, dan orang tua siswa dengan sinkronisasi online (Supabase PostgreSQL / SQLite), arsitektur multi-kelas, alur persetujuan, dan buku tabungan siswa individual.

- 🚀 **Live Streamlit App:** [https://dasboard-keuangan-ku.streamlit.app/](https://dasboard-keuangan-ku.streamlit.app/)
- 🌐 **Live Demo (GitHub Pages):** [https://jovanathallahdimitri007-create.github.io/dasboard-keuangan/](https://jovanathallahdimitri007-create.github.io/dasboard-keuangan/)
- 📦 **GitHub Repository:** [https://github.com/jovanathallahdimitri007-create/dasboard-keuangan](https://github.com/jovanathallahdimitri007-create/dasboard-keuangan)

---email author jovan.athallah@mail.sman2sby.com,indri@mail.sman2sby.com,mustakim@mail.sman2sby.com

## 🌟 Fitur Utama Sistem Keuangan Sekolah

### 1. 🏫 Multi-Kelas & Multi-Tahun Ajaran
- Mengelola banyak kelas sekaligus (contoh: `X-MIPA-1`, `X-MIPA-2`, `XI-MIPA-1`, dll.).
- Terhubung dengan data wali kelas, ketua korlas, dan tahun ajaran aktif (`2026/2027`).
- Isolasi data antar-kelas: pengguna hanya mengakses data kelas sesuai hak kewenangannya.

### 2. 💰 5 Pos Kategori Dana Terpisah (Anti Pencampuran Saldo)
1. **Kas Operasional Kelas:** Pengeluaran harian/mingguan (spidol, kebersihan, ATK, konsumsi piket).
2. **Uang Komite Sekolah:** Iuran resmi pengembangan fasilitas dan kegiatan kesiswaan.
3. **Kegiatan ODL (Outdoor Learning):** Study tour edukasi, tiket museum, transportasi bus pariwisata.
4. **Tabungan Siswa Individual:** Rekening penampungan titipan tabungan siswa yang terpisah dari kas bebas kelas.
5. **Keperluan Korlas:** Pengadaan seragam kelas, banner kegiatan, dekorasi panggung lomba, konsumsi rapat wali murid.

### 3. 📋 Tagihan Iuran & Pembayaran Fleksibel (Penuh / Cicilan)
- Pembuatan tagihan terdistribusi otomatis ke seluruh siswa dalam satu kelas.
- Pencatatan pembayaran sebagian (cicilan) dan lunas.
- Menghitung sisa tagihan secara real-time.
- Nomor kuitansi digital unik anti-duplikasi (`KWT-YYYYMMDD-XXXXXX`).

### 4. 💎 Buku Tabungan Siswa Individual
- Setiap siswa memiliki buku mutasi tabungan sendiri.
- Pencatatan setoran (+) dan penarikan (-) dengan saldo berjalan real-time.
- **Validasi Saldo Non-Negatif:** Penarikan yang melebihi saldo tabungan otomatis ditolak oleh sistem.
- Mutasi tabungan langsung tersinkronisasi secara atomik dengan pos kas penampungan tabungan kelas.

### 5. 👨‍👩‍👧 Portal Transparan untuk Orang Tua Siswa
- Akses cepat dan aman menggunakan **NISN + PIN** siswa.
- Orang tua dapat memantau:
  - Profil siswa dan kelas.
  - Status tagihan iuran yang sudah dibayar, sisa cicilan, dan jatuh tempo.
  - Riwayat tanda terima kuitansi pembayaran digital.
  - Saldo tabungan anak dan riwayat mutasi setor/tarik.
- **Privasi Terjaga:** Orang tua hanya dapat melihat data anaknya sendiri.

### 6. ⚖️ Alur Persetujuan Pengeluaran (*Approval Workflow*)
- Prinsip pemisahan tugas (*segregation of duties*).
- Pengeluaran kas kelas di atas ambang batas (default: `Rp 1.000.000`) otomatis masuk antrean **"Menunggu Persetujuan Korlas"**.
- Saldo kas tidak akan terpotong sebelum disetujui secara resmi oleh Korlas atau Admin.
- Transaksi pembalik (*void / reversal*) untuk membatalkan pengeluaran tanpa menghapus riwayat audit.

### 7. 📜 Audit Trail & Integritas Data
- Seluruh mutasi uang kas, pembayaran siswa, persetujuan transaksi, dan perubahan data dicatat permanen di tabel `audit_logs`.

---

## 👥 Peran Pengguna (Role-Based Access Control)

| Peran | Hak Akses Utama |
| :--- | :--- |
| **👑 Admin Sistem** | Akses penuh seluruh kelas, konfigurasi tahun ajaran, kelola pengguna, audit log lengkap. |
| **💰 Bendahara Kelas** | Input pembayaran siswa, mutasi tabungan, pengeluaran kas operasional, cetak kuitansi. |
| **🤝 Korlas (Koordinator Kelas)** | Memantau kas kelas, mengelola pos ODL & keperluan korlas, menyetujui pengeluaran kas kelas. |
| **👨‍👩‍👧 Orang Tua Siswa** | Portal mandiri untuk memeriksa tagihan, kuitansi digital, dan tabungan anak sendiri. |

---

## 🗄️ Backend & Arsitektur Database

Sistem mendukung arsitektur ganda yang fleksibel:
1. **Supabase PostgreSQL (Online Cloud DB):**
   - File migrasi lengkap: [`supabase/migrations/20261018000000_init_school_finance.sql`](file:///Users/jevin/Downloads/dasboard%20keuangan/dasboard-keuangan/supabase/migrations/20261018000000_init_school_finance.sql)
   - Tabel: `profiles`, `academic_years`, `classes`, `students`, `fund_accounts`, `fee_types`, `student_invoices`, `payments`, `savings_accounts`, `savings_entries`, `transactions`, `transaction_approvals`, `audit_logs`.
   - Dilengkapi *Row Level Security (RLS)*, constraints integritas, foreign keys, dan UUID primary keys.
2. **SQLite Relational Engine (Lokal / Failover):**
   - Tersimpan di `data/school_finance.db` dengan eksekusi transaksi atomik dan foreign keys aktif.

---

## 🚀 Cara Menjalankan & Menjalankan Tes

### Menjalankan Aplikasi (NPM / Streamlit):
```bash
# Menggunakan npm shortcut
npm run dev

# Atau langsung via streamlit
streamlit run app.py
```

### Menjalankan Pengujian Otomatis (36/36 Passed):
```bash
npm test
```
*Menguji isolasi data kelas, pembayaran iuran, mutasi tabungan non-negatif, alur persetujuan korlas, otentikasi portal orang tua, dan audit trail.*

---

## 📂 Struktur Berkas

```
dasboard-keuangan/
├── app.py                     # Aplikasi Streamlit (Keuangan Kelas, Korlas & Portal Siswa)
├── database.py                # Database Manager (SQLite atomik & Supabase connector)
├── package.json               # NPM scripts (dev, test, serve)
├── requirements.txt           # Dependensi Python (streamlit, supabase, plotly, pandas)
├── .env.example               # Contoh konfigurasi environment Supabase
├── .streamlit/
│   └── config.toml            # Konfigurasi tema Fintech Emerald untuk Streamlit
├── supabase/
│   └── migrations/
│       └── 20261018000000_init_school_finance.sql # Migrasi skema PostgreSQL & RLS
├── tests/
│   ├── test_school_finance_engine.py  # Uji otomatis sistem sekolah (21/21 Pass)
│   └── test_financial_engine.js       # Uji otomatis kalkulasi inti (15/15 Pass)
├── index.html                 # Web SPA & Portal Navigasi
├── css/style.css              # Design system & visual stylesheet
├── js/                        # Logika frontend, visualisasi chart, & export
├── Dashboard.html             # Arsip Spreadsheet Asli
├── Pembukuan.html             # Arsip Spreadsheet Asli
├── Olah Data.html             # Arsip Spreadsheet Asli
├── Laporan.html               # Arsip Spreadsheet Asli
├── Asset Tracker.html         # Arsip Spreadsheet Asli
└── README.md                  # Dokumentasi resmi proyek
```
