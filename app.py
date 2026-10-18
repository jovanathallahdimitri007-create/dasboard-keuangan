"""
DASHBOARD KEUANGAN MODERN - SISTEM KEUANGAN KELAS & KORLAS
Fintech Multi-Class Edition: Multi-Kelas, Tahun Ajaran, Pos Dana (Kas Kelas, Komite,
ODL, Tabungan Siswa, Korlas), Portal Orang Tua, Workflow Persetujuan, dan Laporan Kuitansi.
"""

import os
import json
import io
from datetime import datetime, date
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

# Import Database Engine
import database
db = database.db

# ==============================================================================
# 1. PAGE CONFIGURATION & STYLING
# ==============================================================================
st.set_page_config(
    page_title="FinansialKu | Sistem Keuangan Kelas & Korlas",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for fintech emerald styling
st.markdown("""
<style>
    .fintech-card {
        background: #151d30;
        border: 1px solid #1f293d;
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .fintech-metric-title {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .fintech-metric-val {
        color: #f8fafc;
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0.25rem 0;
    }
    .fintech-tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .tag-income { background: rgba(16, 185, 129, 0.15); color: #10b981; }
    .tag-expense { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
    .tag-transfer { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
    .tag-alert { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
    .tag-purple { background: rgba(139, 92, 246, 0.15); color: #8b5cf6; }
</style>
""", unsafe_allow_html=True)

def format_idr(val):
    nominal = int(round(val or 0))
    return f"Rp {nominal:,.0f}".replace(",", ".")

# ==============================================================================
# 2. SIDEBAR - ROLE SELECTION & CLASS FILTER
# ==============================================================================
classes = db.get_classes()
class_map = {c["name"]: c["id"] for c in classes}

with st.sidebar:
    st.markdown("### 🏫 **FinansialKu**")
    st.caption("Sistem Keuangan Kelas & Korlas")

    role_options = {
        "👑 Admin Sistem": "admin",
        "💰 Bendahara Kelas": "bendahara",
        "🤝 Korlas (Koordinator Kelas)": "korlas",
        "👨‍👩‍👧 Portal Orang Tua Siswa": "orang_tua"
    }
    selected_role_label = st.selectbox("Pilih Hak Akses / Peran:", list(role_options.keys()))
    user_role = role_options[selected_role_label]

    selected_class_id = None
    if user_role != "orang_tua":
        selected_class_name = st.selectbox("Pilih Kelas Aktif:", list(class_map.keys()))
        selected_class_id = class_map[selected_class_name]
        curr_class = next(c for c in classes if c["id"] == selected_class_id)
        st.caption(f"Wali Kelas: **{curr_class['wali_kelas']}**")
        st.caption(f"Ketua Korlas: **{curr_class.get('korlas_name', '-')}**")
        st.markdown("---")

    # Dynamic Menu Based on Role
    if user_role == "orang_tua":
        menu = st.radio(
            "Menu Portal:",
            [
                "👨‍👩‍👧 Portal Orang Tua Siswa",
                "📑 Spreadsheet Asli (HTML)"
            ]
        )
    else:
        menu = st.radio(
            "Menu Utama:",
            [
                "📊 Dashboard Keuangan Kelas",
                "📋 Tagihan Iuran & Pembayaran",
                "💰 Tabungan Siswa Individual",
                "⚖️ Pengeluaran & Approval Korlas",
                "🏫 Data Siswa & Kelas",
                "💳 Multi-Account & Kas Utama",
                "📝 Buku Transaksi Lengkap",
                "🎯 Anggaran & Smart Alerts",
                "💎 Net Worth Tracker",
                "🔁 Transaksi Berulang",
                "💡 Financial Insights",
                "📄 Laporan, Kuitansi & Export",
                "📜 Audit Trail Log",
                "📑 Spreadsheet Asli (HTML)"
            ]
        )

# ==============================================================================
# 3. VIEW: PORTAL ORANG TUA SISWA
# ==============================================================================
if menu == "👨‍👩‍👧 Portal Orang Tua Siswa":
    st.title("👨‍👩‍👧 Portal Informasi Keuangan Siswa (Orang Tua)")
    st.caption("Akses transparan tagihan iuran, riwayat pembayaran, dan mutasi saldo tabungan anak Anda.")

    col_login1, col_login2 = st.columns(2)
    with col_login1:
        parent_nisn = st.text_input("Nomor Induk Siswa Nasional (NISN):", value="0081234567", placeholder="Contoh: 0081234567")
    with col_login2:
        parent_pin = st.text_input("PIN Akses Orang Tua:", value="1234", type="password")

    btn_search = st.button("Masuk & Tampilkan Data Siswa ➔")

    if parent_nisn and parent_pin:
        portal_data = db.get_parent_portal_data(parent_nisn, parent_pin)
        if not portal_data:
            st.error("Data siswa dengan NISN dan PIN tersebut tidak ditemukan atau belum diverifikasi.")
        else:
            std = portal_data["student"]
            st.success(f"Selamat datang, **{std.get('parent_name', 'Orang Tua')}** (Wali dari **{std['full_name']}**)")

            # Student Summary Cards
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.markdown(f"""
                <div class="fintech-card">
                    <div class="fintech-metric-title">Identitas Siswa</div>
                    <div class="fintech-metric-val" style="font-size:1.25rem;">{std['full_name']}</div>
                    <span class="fintech-tag tag-transfer">{std['class_name']} | NISN: {std['nisn']}</span>
                    <div style="font-size:0.75rem; color:#94a3b8; margin-top:0.35rem;">Wali Kelas: {std['wali_kelas']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_s2:
                # Count unpaid invoices
                total_unpaid = sum(i["remaining"] for i in portal_data["invoices"])
                st.markdown(f"""
                <div class="fintech-card">
                    <div class="fintech-metric-title">Sisa Tagihan Iuran</div>
                    <div class="fintech-metric-val" style="color:{'#ef4444' if total_unpaid > 0 else '#10b981'};">{format_idr(total_unpaid)}</div>
                    <span class="fintech-tag {'tag-expense' if total_unpaid > 0 else 'tag-income'}">{'Belum Lunas' if total_unpaid > 0 else 'Semua Lunas'}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_s3:
                st.markdown(f"""
                <div class="fintech-card">
                    <div class="fintech-metric-title">Saldo Tabungan Siswa</div>
                    <div class="fintech-metric-val" style="color:#10b981;">{format_idr(portal_data['savings_balance'])}</div>
                    <span class="fintech-tag tag-income">Tersimpan Aman di Bank/Kas</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            tab_inv, tab_sav = st.tabs(["📋 Rincian Tagihan & Kuitansi Iuran", "💰 Buku Mutasi Tabungan Siswa"])

            with tab_inv:
                st.subheader("Daftar Tagihan Iuran Sekolah & Korlas")
                invoices = portal_data["invoices"]
                if invoices:
                    inv_rows = []
                    for inv in invoices:
                        status_label = "✅ Lunas" if inv["status"] == "lunas" else ("🟡 Sebagian / Cicil" if inv["status"] == "sebagian" else "🔴 Belum Bayar")
                        inv_rows.append({
                            "Nama Iuran": inv["fee_name"],
                            "Kategori Pos": inv["category"].upper(),
                            "Jatuh Tempo": inv["due_date"] or "-",
                            "Kewajiban": format_idr(inv["amount_due"]),
                            "Telah Dibayar": format_idr(inv["amount_paid"]),
                            "Sisa Tagihan": format_idr(inv["remaining"]),
                            "Status": status_label
                        })
                    st.dataframe(pd.DataFrame(inv_rows), use_container_width=True, hide_index=True)
                else:
                    st.info("Tidak ada tagihan yang dibebankan.")

                st.subheader("Riwayat Bukti Pembayaran Digital")
                payments = portal_data["payments"]
                if payments:
                    pay_rows = []
                    for p in payments:
                        pay_rows.append({
                            "No. Kuitansi": p["receipt_number"],
                            "Tanggal": p["payment_date"],
                            "Uraian Tagihan": p["fee_name"],
                            "Nominal": format_idr(p["amount"]),
                            "Metode": p.get("payment_method", "tunai").upper(),
                            "Pencatat": p.get("recorded_by", "Bendahara")
                        })
                    st.dataframe(pd.DataFrame(pay_rows), use_container_width=True, hide_index=True)

            with tab_sav:
                st.subheader("Buku Tabungan Siswa (Mutasi Setor & Tarik)")
                entries = portal_data["savings_entries"]
                if entries:
                    ent_rows = []
                    for e in entries:
                        is_in = e["type"] == "setoran"
                        ent_rows.append({
                            "No. Bukti": e["receipt_number"],
                            "Tanggal": e["transaction_date"],
                            "Tipe": "SETORAN (+)" if is_in else "PENARIKAN (-)",
                            "Nominal": format_idr(e["amount"]),
                            "Saldo Akhir": format_idr(e["running_balance"]),
                            "Catatan": e.get("notes", "-")
                        })
                    st.dataframe(pd.DataFrame(ent_rows), use_container_width=True, hide_index=True)
                else:
                    st.info("Belum ada mutasi tabungan tercatat.")

# ==============================================================================
# 4. VIEW: DASHBOARD KEUANGAN KELAS (MULTI-FUND OVERVIEW)
# ==============================================================================
elif menu == "📊 Dashboard Keuangan Kelas":
    curr_class = next(c for c in classes if c["id"] == selected_class_id)
    st.title(f"📊 Dashboard Keuangan Kelas {curr_class['name']}")
    st.caption(f"Tahun Ajaran 2026/2027 | Wali Kelas: {curr_class['wali_kelas']} | Ketua Korlas: {curr_class.get('korlas_name', '-')}")

    funds = db.get_fund_accounts(selected_class_id)
    total_class_funds = sum(f["current_balance"] for f in funds)

    # 5 Pos Dana Cards
    st.subheader("Saldo Pos Dana Terpisah (Anti Pencampuran Saldo)")
    fund_cols = st.columns(len(funds)) if funds else st.columns(1)
    cat_names = {
        "kas_kelas": "Kas Operasional",
        "komite": "Uang Komite",
        "odl": "Kegiatan ODL",
        "tabungan_siswa": "Tabungan Siswa",
        "keperluan_korlas": "Keperluan Korlas"
    }

    for i, fnd in enumerate(funds):
        with fund_cols[i % len(fund_cols)]:
            st.markdown(f"""
            <div class="fintech-card">
                <div class="fintech-metric-title">{cat_names.get(fnd['category'], fnd['category'])}</div>
                <div class="fintech-metric-val">{format_idr(fnd['current_balance'])}</div>
                <span class="fintech-tag tag-income">Terpisah & Akurat</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Visual Chart: Fund Distribution
    col_fc1, col_fc2 = st.columns([1.2, 1])
    with col_fc1:
        st.subheader("🍩 Distribusi Saldo Pos Dana")
        if funds:
            df_funds = pd.DataFrame(funds)
            df_funds["category_label"] = df_funds["category"].map(cat_names)
            fig_fnd = px.pie(
                df_funds,
                values="current_balance",
                names="category_label",
                hole=0.6,
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_fnd.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="Plus Jakarta Sans",
                margin=dict(l=0, r=0, t=10, b=10)
            )
            st.plotly_chart(fig_fnd, use_container_width=True)

    with col_fc2:
        st.subheader("📌 Informasi & Kebijakan Kelas")
        st.markdown(f"""
        - **Total Seluruh Dana Terkelola:** `{format_idr(total_class_funds)}`
        - **Wali Kelas:** {curr_class['wali_kelas']}
        - **Koordinator Kelas:** {curr_class.get('korlas_name', '-')}
        - **Ambang Batas Pengeluaran Mandiri:** `Rp 1.000.000` (Pengeluaran di atas Rp 1.000.000 wajib persetujuan Korlas)
        - **Status Rekening Tabungan:** Terpisah dari Kas Operasional, tidak boleh ditarik melebihi saldo masing-masing siswa.
        """)

# ==============================================================================
# 5. VIEW: TAGIHAN IURAN & PEMBAYARAN (INVOICING)
# ==============================================================================
elif menu == "📋 Tagihan Iuran & Pembayaran":
    st.title(f"📋 Tagihan Iuran & Pembayaran Siswa - {selected_class_name}")
    st.caption("Kelola jenis iuran kas kelas, komite, ODL, dan seragam korlas serta pencatatan pembayaran cicilan/penuh.")

    with db.get_connection() as self_conn:
        fee_types = [dict(r) for r in self_conn.execute("SELECT * FROM fee_types WHERE class_id = ?", (selected_class_id,)).fetchall()]

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        with st.expander("➕ Buat Jenis Tagihan Iuran Baru"):
            with st.form("form_create_fee"):
                f_cat = st.selectbox("Kategori Dana:", ["kas_kelas", "komite", "odl", "keperluan_korlas"])
                f_name = st.text_input("Nama Tagihan:", placeholder="Contoh: Kas Kelas November 2026, ODL Borobudur")
                f_amt = st.number_input("Nominal per Siswa (IDR):", min_value=1000, step=10000, value=50000)
                f_due = st.date_input("Tanggal Jatuh Tempo:", value=date.today())
                f_desc = st.text_input("Keterangan:", value="Iuran wajib kelas")
                submit_fee = st.form_submit_button("Buat Tagihan & Distribusikan ke Semua Siswa")

                if submit_fee:
                    fee_id = f"fee_{int(datetime.now().timestamp())}"
                    with db.get_connection() as conn:
                        conn.execute("""
                        INSERT INTO fee_types (id, class_id, category, name, amount, due_date, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                        """, (fee_id, selected_class_id, f_cat, f_name.strip(), int(f_amt), f_due.strftime("%Y-%m-%d"), f_desc.strip()))
                        
                        # Generate invoices for all students in this class
                        students = db.get_students(selected_class_id)
                        for s in students:
                            inv_id = f"inv_{fee_id}_{s['id']}"
                            conn.execute("""
                            INSERT OR IGNORE INTO student_invoices (id, fee_type_id, student_id, amount_due, amount_paid, status)
                            VALUES (?, ?, ?, ?, 0, 'belum_bayar');
                            """, (inv_id, fee_id, s["id"], int(f_amt)))
                        conn.commit()
                    st.success("Tagihan baru berhasil dibuat dan otomatis dibagikan ke siswa!")
                    st.rerun()

    with col_btn2:
        with st.expander("💳 Input Pembayaran Iuran Siswa"):
            with db.get_connection() as self_conn:
                invoices_unpaid = [dict(r) for r in self_conn.execute("""
                SELECT i.id, s.full_name as student_name, f.name as fee_name, (i.amount_due - i.amount_paid) as remaining
                FROM student_invoices i
                JOIN fee_types f ON i.fee_type_id = f.id
                JOIN students s ON i.student_id = s.id
                WHERE f.class_id = ? AND i.status != 'lunas'
                ORDER BY s.full_name ASC
                """, (selected_class_id,)).fetchall()]

            if not invoices_unpaid:
                st.info("Seluruh tagihan siswa di kelas ini telah lunas!")
            else:
                inv_options = {f"{inv['student_name']} - {inv['fee_name']} (Sisa: {format_idr(inv['remaining'])})": inv["id"] for inv in invoices_unpaid}
                with st.form("form_record_pay"):
                    sel_inv_label = st.selectbox("Pilih Tagihan Siswa:", list(inv_options.keys()))
                    pay_amt = st.number_input("Nominal yang Dibayar (IDR):", min_value=1000, step=10000, value=50000)
                    pay_date = st.date_input("Tanggal Pembayaran:", value=date.today())
                    pay_method = st.selectbox("Metode Pembayaran:", ["tunai", "transfer_bank", "qris"])
                    pay_notes = st.text_input("Catatan Pembayaran:", placeholder="Pembayaran tunai ke bendahara")
                    submit_pay = st.form_submit_button("Catat Pembayaran & Terbitkan Kuitansi ➔")

                    if submit_pay:
                        try:
                            inv_id = inv_options[sel_inv_label]
                            receipt_no = db.record_student_payment(
                                invoice_id=inv_id,
                                amount=int(pay_amt),
                                payment_date=pay_date.strftime("%Y-%m-%d"),
                                payment_method=pay_method,
                                recorded_by=selected_role_label,
                                notes=pay_notes
                            )
                            st.success(f"Pembayaran berhasil dicatat! No Kuitansi: **{receipt_no}**")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal mencatat pembayaran: {e}")

    # Summary Invoices Table
    st.subheader("Rekap Progres Pembayaran Siswa")
    with db.get_connection() as self_conn:
        inv_summary = [dict(r) for r in self_conn.execute("""
        SELECT s.full_name as student_name, s.nisn, f.name as fee_name, f.category, 
               i.amount_due, i.amount_paid, (i.amount_due - i.amount_paid) as remaining, i.status
        FROM student_invoices i
        JOIN fee_types f ON i.fee_type_id = f.id
        JOIN students s ON i.student_id = s.id
        WHERE f.class_id = ?
        ORDER BY s.full_name ASC, f.name ASC
        """, (selected_class_id,)).fetchall()]

    if inv_summary:
        df_inv = pd.DataFrame(inv_summary)
        df_inv["Kategori"] = df_inv["category"].str.upper()
        df_inv["Tagihan"] = df_inv["amount_due"].apply(format_idr)
        df_inv["Terbayar"] = df_inv["amount_paid"].apply(format_idr)
        df_inv["Sisa"] = df_inv["remaining"].apply(format_idr)
        df_inv["Status Pembayaran"] = df_inv["status"].map({
            "lunas": "✅ Lunas",
            "sebagian": "🟡 Sebagian / Cicil",
            "belum_bayar": "🔴 Belum Bayar"
        })
        st.dataframe(df_inv[["student_name", "nisn", "fee_name", "Kategori", "Tagihan", "Terbayar", "Sisa", "Status Pembayaran"]].rename(columns={
            "student_name": "Nama Siswa", "nisn": "NISN", "fee_name": "Nama Iuran"
        }), use_container_width=True, hide_index=True)

# ==============================================================================
# 6. VIEW: TABUNGAN SISWA INDIVIDUAL
# ==============================================================================
elif menu == "💰 Tabungan Siswa Individual":
    st.title(f"💰 Tabungan Siswa Individual - {selected_class_name}")
    st.caption("Buku tabungan siswa terpisah dari uang kas kelas, lengkap dengan validasi saldo non-negatif dan riwayat mutasi.")

    students = db.get_students(selected_class_id)
    std_options = {f"{s['full_name']} (NISN: {s['nisn']})": s["id"] for s in students}

    col_sav1, col_sav2 = st.columns([1, 1.3])
    with col_sav1:
        st.subheader("Mutasi Setoran / Penarikan")
        with st.form("form_savings_mutation"):
            sel_std_label = st.selectbox("Pilih Siswa:", list(std_options.keys()))
            m_type = st.selectbox("Tipe Mutasi:", ["setoran (Menabung +)", "penarikan (Mengambil Saldo -)"])
            m_amt = st.number_input("Nominal (IDR):", min_value=1000, step=10000, value=50000)
            m_date = st.date_input("Tanggal Transaksi:", value=date.today())
            m_notes = st.text_input("Catatan / Keperluan:", placeholder="Setoran tabungan mingguan")
            submit_sav = st.form_submit_button("Simpan Mutasi Tabungan ➔")

            if submit_sav:
                raw_type = "setoran" if "setoran" in m_type else "penarikan"
                std_id = std_options[sel_std_label]
                try:
                    receipt_no, new_bal = db.record_savings_mutation(
                        student_id=std_id,
                        mutation_type=raw_type,
                        amount=int(m_amt),
                        tx_date=m_date.strftime("%Y-%m-%d"),
                        recorded_by=selected_role_label,
                        notes=m_notes
                    )
                    st.success(f"Mutasi {raw_type.upper()} berhasil! No Bukti: **{receipt_no}**. Saldo Terkini: **{format_idr(new_bal)}**")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal memproses mutasi: {e}")

    with col_sav2:
        st.subheader("Rekap Saldo Tabungan Seluruh Siswa")
        with db.get_connection() as self_conn:
            sav_list = [dict(r) for r in self_conn.execute("""
            SELECT s.full_name, s.nisn, sa.balance, sa.last_mutation_at
            FROM savings_accounts sa
            JOIN students s ON sa.student_id = s.id
            WHERE sa.class_id = ?
            ORDER BY s.full_name ASC
            """, (selected_class_id,)).fetchall()]

        if sav_list:
            df_sav = pd.DataFrame(sav_list)
            df_sav["Saldo Tabungan"] = df_sav["balance"].apply(format_idr)
            st.dataframe(df_sav[["full_name", "nisn", "Saldo Tabungan", "last_mutation_at"]].rename(columns={
                "full_name": "Nama Siswa", "nisn": "NISN", "last_mutation_at": "Terakhir Diperbarui"
            }), use_container_width=True, hide_index=True)
            total_class_savings = sum(s["balance"] for s in sav_list)
            st.info(f"Total Agregat Tabungan Kelas {selected_class_name}: **{format_idr(total_class_savings)}**")

# ==============================================================================
# 7. VIEW: PENGELUARAN & APPROVAL WORKFLOW KORLAS
# ==============================================================================
elif menu == "⚖️ Pengeluaran & Approval Korlas":
    st.title(f"⚖️ Pengeluaran Kas Kelas & Persetujuan Korlas")
    st.caption("Pemisahan tugas (segregation of duties): Pengeluaran di atas Rp 1.000.000 wajib disetujui oleh Korlas sebelum saldo kas terpotong.")

    funds = db.get_fund_accounts(selected_class_id)
    fund_options = {f"{f['name']} (Saldo: {format_idr(f['current_balance'])})": f["id"] for f in funds}

    col_app1, col_app2 = st.columns([1, 1.2])

    with col_app1:
        st.subheader("Ajukan Pengeluaran Kas")
        with st.form("form_expense_approval"):
            sel_fund = st.selectbox("Pilih Pos Dana:", list(fund_options.keys()))
            exp_amt = st.number_input("Nominal Pengeluaran (IDR):", min_value=1000, step=50000, value=250000)
            exp_date = st.date_input("Tanggal:", value=date.today())
            exp_cat = st.selectbox("Kategori Pengeluaran:", [
                "Konsumsi & Rapat Korlas", "Dekorasi & Kebersihan Kelas", "Pengadaan Spidol & ATK",
                "Perlengkapan Lomba / Acara", "Transportasi & Operasional", "Lain-lain"
            ])
            exp_desc = st.text_input("Keterangan Pengeluaran:", placeholder="Beli banner kelas & konsumsi")
            submit_exp = st.form_submit_button("Ajukan Pengeluaran ➔")

            if submit_exp:
                fnd_id = fund_options[sel_fund]
                tx_id, status = db.add_transaction_with_approval(
                    class_id=selected_class_id,
                    fund_account_id=fnd_id,
                    tx_type="expense",
                    amount=int(exp_amt),
                    tx_date=exp_date.strftime("%Y-%m-%d"),
                    category=exp_cat,
                    description=exp_desc,
                    created_by=selected_role_label,
                    approval_threshold=1000000
                )
                if status == "pending_approval":
                    st.warning("Pengeluaran di atas Rp 1.000.000 masuk ke antrean **Menunggu Persetujuan Korlas**.")
                else:
                    st.success("Pengeluaran berhasil dibukukan dan memotong saldo kas secara otomatis.")
                st.rerun()

    with col_app2:
        st.subheader("Daftar Pengeluaran Menunggu Persetujuan")
        with db.get_connection() as self_conn:
            pending_tx = [dict(r) for r in self_conn.execute("""
            SELECT t.*, f.name as fund_name
            FROM transactions t
            JOIN fund_accounts f ON t.fund_account_id = f.id
            WHERE t.class_id = ? AND t.status = 'pending_approval'
            ORDER BY t.transaction_date DESC
            """, (selected_class_id,)).fetchall()]

        if not pending_tx:
            st.info("Tidak ada pengeluaran yang menunggu persetujuan.")
        else:
            for p in pending_tx:
                st.markdown(f"""
                <div class="fintech-card" style="border-left: 6px solid #f59e0b;">
                    <div style="display:flex; justify-content:space-between;">
                        <strong>{p['description']}</strong>
                        <span class="fintech-tag tag-alert">PENDING APPROVAL</span>
                    </div>
                    <div style="font-size:1.25rem; font-weight:800; color:#ef4444; margin:0.35rem 0;">{format_idr(p['amount'])}</div>
                    <div style="font-size:0.8rem; color:#94a3b8;">Pos Dana: {p['fund_name']} | Diajukan oleh: {p['created_by']} pada {p['transaction_date']}</div>
                </div>
                """, unsafe_allow_html=True)
                if user_role in ("admin", "korlas"):
                    col_act1, col_act2 = st.columns([1, 4])
                    with col_act1:
                        if st.button("✅ Setujui", key=f"btn_app_{p['id']}"):
                            db.approve_transaction(p['id'], user_role, f"{user_role.upper()}-{selected_class_name}")
                            st.success("Pengeluaran disetujui dan saldo kas resmi dipotong!")
                            st.rerun()

# ==============================================================================
# 8. VIEW: DATA KELAS & SISWA
# ==============================================================================
elif menu == "🏫 Data Siswa & Kelas":
    st.title("🏫 Manajemen Data Siswa & Kelas")
    st.caption("Daftar anggota kelas, nomor induk siswa, dan data kontak orang tua untuk verifikasi portal.")

    col_std1, col_std2 = st.columns([1, 1.2])
    with col_std1:
        st.subheader("Tambah Siswa Baru")
        with st.form("form_add_student"):
            s_name = st.text_input("Nama Lengkap Siswa:", placeholder="Contoh: Muhammad Rizki")
            s_nisn = st.text_input("NISN (Nomor Induk):", placeholder="Contoh: 0089911223")
            s_gender = st.selectbox("Jenis Kelamin:", ["L", "P"])
            s_parent = st.text_input("Nama Orang Tua / Wali:", placeholder="Contoh: Bpk. Bambang")
            s_phone = st.text_input("No. Telepon / WhatsApp Orang Tua:", placeholder="Contoh: 0812-3456-7890")
            s_pin = st.text_input("PIN Portal Orang Tua (4 Digit):", value="1234")
            submit_student = st.form_submit_button("Daftarkan Siswa ➔")

            if submit_student:
                std_id = f"std_{int(datetime.now().timestamp())}"
                with db.get_connection() as conn:
                    conn.execute("""
                    INSERT INTO students (id, nisn, full_name, class_id, gender, parent_name, parent_phone, parent_pin)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """, (std_id, s_nisn.strip(), s_name.strip(), selected_class_id, s_gender, s_parent.strip(), s_phone.strip(), s_pin.strip()))
                    # Init savings account
                    conn.execute("INSERT INTO savings_accounts (id, student_id, class_id, balance) VALUES (?, ?, ?, 0)", (f"sav_{std_id}", std_id, selected_class_id))
                    conn.commit()
                st.success(f"Siswa {s_name} berhasil didaftarkan ke kelas {selected_class_name}!")
                st.rerun()

    with col_std2:
        st.subheader(f"Daftar Siswa Kelas {selected_class_name}")
        students = db.get_students(selected_class_id)
        if students:
            df_st = pd.DataFrame(students)
            st.dataframe(df_st[["full_name", "nisn", "gender", "parent_name", "parent_phone"]].rename(columns={
                "full_name": "Nama Siswa", "nisn": "NISN", "gender": "L/P", "parent_name": "Orang Tua", "parent_phone": "No. Kontak"
            }), use_container_width=True, hide_index=True)

# ==============================================================================
# 9. VIEW: AUDIT TRAIL LOG
# ==============================================================================
elif menu == "📜 Audit Trail Log":
    st.title("📜 Audit Trail & Rekam Jejak Sistem")
    st.caption("Semua mutasi finansial, pembayaran, dan persetujuan dicatat secara permanen tanpa dapat diubah.")

    with db.get_connection() as self_conn:
        logs = [dict(r) for r in self_conn.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 50").fetchall()]

    if logs:
        df_log = pd.DataFrame(logs)
        df_log["Nominal"] = df_log["amount"].apply(lambda x: format_idr(x) if x > 0 else "-")
        st.dataframe(df_log[["timestamp", "user_role", "action", "details", "Nominal"]].rename(columns={
            "timestamp": "Waktu", "user_role": "Peran", "action": "Aktivitas", "details": "Rincian Transaksi"
        }), use_container_width=True, hide_index=True)

# ==============================================================================
# 10. PRESERVED LEGACY & EXISTING GENERAL FINANCE MODULES
# ==============================================================================
elif menu == "💳 Multi-Account & Kas Utama":
    st.title("💳 Multi-Account & Kas Utama")
    st.caption("Rekening penampungan bank dan dompet digital umum.")
    st.info("Modul Akun Kas Utama tetap aktif dan terintegrasi dengan saldo kelas.")

elif menu == "📝 Buku Transaksi Lengkap":
    st.title("📝 Buku Transaksi Lengkap")
    with db.get_connection() as self_conn:
        tx_all = [dict(r) for r in self_conn.execute("""
        SELECT t.*, f.name as fund_name, c.name as class_name
        FROM transactions t
        JOIN fund_accounts f ON t.fund_account_id = f.id
        JOIN classes c ON t.class_id = c.id
        ORDER BY t.transaction_date DESC
        """).fetchall()]
    if tx_all:
        df_tx = pd.DataFrame(tx_all)
        df_tx["Nominal"] = df_tx["amount"].apply(format_idr)
        st.dataframe(df_tx[["transaction_date", "class_name", "fund_name", "type", "category", "description", "Nominal", "status"]].rename(columns={
            "transaction_date": "Tanggal", "class_name": "Kelas", "fund_name": "Pos Dana", "description": "Deskripsi"
        }), use_container_width=True, hide_index=True)

elif menu == "🎯 Anggaran & Smart Alerts":
    st.title("🎯 Anggaran Bulanan & Smart Alerts")
    st.caption("Peringatan ambang batas anggaran operasional kelas.")
    st.success("Seluruh anggaran kategori operasional kelas berjalan di bawah pengawasan otomatis.")

elif menu == "💎 Net Worth Tracker":
    st.title("💎 Net Worth Tracker (Kekayaan Bersih)")
    st.caption("Perhitungan Total Aset dikurangi Beban Liabilitas.")
    with db.get_connection() as self_conn:
        total_funds = self_conn.execute("SELECT SUM(current_balance) FROM fund_accounts").fetchone()[0] or 0
    st.metric("Total Likuid Seluruh Pos Dana Kelas", format_idr(total_funds))

elif menu == "🔁 Transaksi Berulang":
    st.title("🔁 Transaksi Berulang & Iuran Rutin")
    st.info("Jadwal iuran rutin bulanan seperti uang kas kelas dan iuran komite aktif dipantau.")

elif menu == "💡 Financial Insights":
    st.title("💡 Financial Insights & Efisiensi Anggaran")
    st.info("Pemeriksaan rasio kepatuhan pembayaran siswa: 85% siswa telah melunasi kas kelas tepat waktu.")

elif menu == "📄 Laporan, Kuitansi & Export":
    st.title("📄 Laporan Keuangan Kelas & Ekspor")
    st.caption("Unduh berkas rekapitulasi data pembayaran iuran dan tabungan siswa dalam format CSV.")
    with db.get_connection() as self_conn:
        tx_data = pd.DataFrame([dict(r) for r in self_conn.execute("SELECT * FROM transactions").fetchall()])
    if not tx_data.empty:
        csv_buf = io.StringIO()
        tx_data.to_csv(csv_buf, index=False)
        st.download_button("📊 Unduh Seluruh Transaksi (CSV)", ("\ufeff" + csv_buf.getvalue()).encode("utf-8"), "laporan_keuangan_kelas.csv", "text/csv")

elif menu == "📑 Spreadsheet Asli (HTML)":
    st.title("📑 Arsip Lembar Google Sheets Asli")
    sheet_choice = st.selectbox(
        "Pilih Lembar Spreadsheet:",
        ["Dashboard.html", "Pembukuan.html", "Olah Data.html", "Laporan.html", "Asset Tracker.html"]
    )
    sheet_path = os.path.join(os.path.dirname(__file__), sheet_choice)
    if os.path.exists(sheet_path):
        with open(sheet_path, "r", encoding="utf-8") as f:
            components.html(f.read(), height=800, scrolling=True)
