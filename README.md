# 💰 Dashboard Keuangan & Pembukuan

Sistem Dashboard Finansial, Pembukuan, Olah Data, Laporan, dan Asset Tracker interaktif berbasis web.

🌐 **Live Demo (GitHub Pages):**  
👉 [https://jovanathallahdimitri007-create.github.io/dasboard-keuangan/](https://jovanathallahdimitri007-create.github.io/dasboard-keuangan/)

---

## 📑 Modul & Halaman

1. **📊 Dashboard Arus Keuangan (`Dashboard.html`)**
   - Ringkasan Total Pendapatan, Pengeluaran, Profit, & Target Keuangan.
   - Neraca & Rincian Total Aset, Total Hutang, dan Kekayaan Bersih.
   - Grafik interaktif Margin Profit vs Target dan Arus Kas.

2. **📖 Pembukuan (`Pembukuan.html`)**
   - Pencatatan transaksi pemasukan dan pengeluaran secara terperinci.
   - Kategori akun, tanggal transaksi, deskripsi, dan mutasi saldo.

3. **⚙️ Olah Data (`Olah Data.html`)**
   - Rekapitulasi per kategori pengeluaran dan pos pendapatan.
   - Analisis perbandingan arus kas periodik.

4. **📑 Laporan (`Laporan.html`)**
   - Ringkasan Laporan Laba Rugi dan Neraca Keuangan.
   - Format siap cetak dan siap dievaluasi secara berkala.

5. **💎 Asset Tracker (`Asset Tracker.html`)**
   - Pemantauan alokasi aset (Tabungan, Saham, Reksadana, Crypto, Properti, Emas, Deposito).
   - Perhitungan otomatis net worth / kekayaan bersih.

---

## 🚀 Cara Menjalankan Secara Lokal

Cukup jalankan server lokal sederhana dengan Python:

```bash
# Jalankan web server di port 8000
python3 -m http.server 8000
```

Buka browser di alamat:
```
http://localhost:8000
```

---

## 📂 Struktur Berkas

```
dasboard-keuangan/
├── index.html            # Portal utama navigasi terpadu (Tabs Shell)
├── Dashboard.html        # Lembar Dashboard Utama
├── Pembukuan.html        # Lembar Pembukuan Transaksi
├── Olah Data.html        # Lembar Olah & Analisis Data
├── Laporan.html          # Lembar Laporan Keuangan
├── Asset Tracker.html    # Lembar Pemantauan Aset
├── resources/            # Aset CSS styling, Charts JS, dan gambar
└── README.md             # Dokumentasi proyek
```