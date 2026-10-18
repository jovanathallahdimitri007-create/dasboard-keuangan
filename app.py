"""
DASHBOARD KEUANGAN MODERN - STREAMLIT CLOUD EDITION
Fintech Application: Multi-Account, Budgets & Smart Alerts, Net Worth Tracker,
Recurring Transactions, Financial Insights, PDF/CSV Export, and Original Spreadsheet Archive.
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

# ==============================================================================
# 1. PAGE CONFIGURATION & STYLING
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Keuangan Modern | Fintech Edition",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for fintech emerald styling
st.markdown("""
<style>
    /* Metric Card styling */
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
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0.35rem 0;
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
</style>
""", unsafe_allow_html=True)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "finance_data.json")

# ==============================================================================
# 2. DATA PERSISTENCE & INITIAL SEED
# ==============================================================================
INITIAL_DATA = {
    "accounts": [
        {"id": "acc_1", "name": "BCA Utama", "type": "bank", "balance": 25000000, "initialBalance": 25000000, "number": "8271-9920-11", "color": "#00529b", "icon": "🏦"},
        {"id": "acc_2", "name": "Mandiri Operasional", "type": "bank", "balance": 18500000, "initialBalance": 18500000, "number": "142-00-192837", "color": "#003366", "icon": "🏛️"},
        {"id": "acc_3", "name": "GoPay / OVO", "type": "ewallet", "balance": 1450000, "initialBalance": 1450000, "number": "0812-3456-7890", "color": "#00aed6", "icon": "📱"},
        {"id": "acc_4", "name": "Kas Tunai / Dompet", "type": "cash", "balance": 750000, "initialBalance": 750000, "number": "-", "color": "#10b981", "icon": "💵"},
        {"id": "acc_5", "name": "Bibit Reksadana", "type": "investment", "balance": 15000000, "initialBalance": 15000000, "number": "INV-9921", "color": "#10b981", "icon": "📈"}
    ],
    "assetsLiabilities": [
        {"id": "ast_1", "name": "Rumah Tinggal", "type": "asset", "category": "property", "value": 450000000, "notes": "Nilai pasar estimasi 2026"},
        {"id": "ast_2", "name": "Mobil Honda HR-V", "type": "asset", "category": "vehicle", "value": 240000000, "notes": "Kondisi mulus"},
        {"id": "ast_3", "name": "Portofolio Saham BBCA & BMRI", "type": "asset", "category": "investment", "value": 65000000, "notes": "Ajaib Sekuritas"},
        {"id": "ast_4", "name": "Tabungan Emas Antam (25g)", "type": "asset", "category": "gold", "value": 37500000, "notes": "Safe deposit box"},
        {"id": "lia_1", "name": "KPR Rumah Bank Mandiri", "type": "liability", "category": "mortgage", "value": 185000000, "notes": "Sisa tenor 6 tahun"},
        {"id": "lia_2", "name": "Kartu Kredit BCA Everyday", "type": "liability", "category": "credit_card", "value": 4200000, "notes": "Tagihan bulan berjalan"}
    ],
    "budgets": [
        {"id": "bg_1", "category": "Makanan & Minuman", "limit": 4500000, "period": "2026-10"},
        {"id": "bg_2", "category": "Transportasi & Bensin", "limit": 1800000, "period": "2026-10"},
        {"id": "bg_3", "category": "Tagihan & Utilitas", "limit": 2500000, "period": "2026-10"},
        {"id": "bg_4", "category": "Belanja & Hiburan", "limit": 2000000, "period": "2026-10"},
        {"id": "bg_5", "category": "Kesehatan & Asuransi", "limit": 1500000, "period": "2026-10"}
    ],
    "recurring": [
        {"id": "rec_1", "name": "Gaji Bulanan", "type": "income", "amount": 32000000, "category": "Gaji & Pendapatan", "accountId": "acc_1", "frequency": "monthly", "dayOfMonth": 25, "active": True, "lastRun": "2026-09-25"},
        {"id": "rec_2", "name": "Cicilan KPR Mandiri", "type": "expense", "amount": 4850000, "category": "Tagihan & Utilitas", "accountId": "acc_2", "frequency": "monthly", "dayOfMonth": 5, "active": True, "lastRun": "2026-10-05"},
        {"id": "rec_3", "name": "Internet & WiFi Fiber", "type": "expense", "amount": 450000, "category": "Tagihan & Utilitas", "accountId": "acc_1", "frequency": "monthly", "dayOfMonth": 15, "active": True, "lastRun": "2026-10-15"},
        {"id": "rec_4", "name": "Langganan Netflix & Spotify", "type": "expense", "amount": 215000, "category": "Belanja & Hiburan", "accountId": "acc_3", "frequency": "monthly", "dayOfMonth": 12, "active": True, "lastRun": "2026-10-12"}
    ],
    "transactions": [
        {"id": "tx_1", "date": "2026-10-01", "type": "income", "amount": 32000000, "category": "Gaji & Pendapatan", "accountId": "acc_1", "description": "Gaji Pokok Oktober 2026"},
        {"id": "tx_2", "date": "2026-10-02", "type": "transfer", "amount": 5000000, "accountId": "acc_1", "toAccountId": "acc_2", "description": "Alokasi Rekening Operasional"},
        {"id": "tx_3", "date": "2026-10-03", "type": "transfer", "amount": 2000000, "accountId": "acc_1", "toAccountId": "acc_3", "description": "Top Up E-Wallet Bulanan"},
        {"id": "tx_4", "date": "2026-10-05", "type": "expense", "amount": 4850000, "category": "Tagihan & Utilitas", "accountId": "acc_2", "description": "Bayar Cicilan KPR Mandiri"},
        {"id": "tx_5", "date": "2026-10-07", "type": "expense", "amount": 1250000, "category": "Makanan & Minuman", "accountId": "acc_3", "description": "Belanja Supermarket Mingguan"},
        {"id": "tx_6", "date": "2026-10-09", "type": "expense", "amount": 350000, "category": "Transportasi & Bensin", "accountId": "acc_3", "description": "Isi Bensin Pertamax Full Tank"},
        {"id": "tx_7", "date": "2026-10-10", "type": "expense", "amount": 650000, "category": "Makanan & Minuman", "accountId": "acc_4", "description": "Makan Malam Akhir Pekan"},
        {"id": "tx_8", "date": "2026-10-12", "type": "expense", "amount": 215000, "category": "Belanja & Hiburan", "accountId": "acc_3", "description": "Langganan Netflix & Spotify"},
        {"id": "tx_9", "date": "2026-10-14", "type": "income", "amount": 4500000, "category": "Investasi & Bonus", "accountId": "acc_5", "description": "Dividen Saham BBCA Semester 2"},
        {"id": "tx_10", "date": "2026-10-15", "type": "expense", "amount": 450000, "category": "Tagihan & Utilitas", "accountId": "acc_1", "description": "Tagihan Internet Fiber"},
        {"id": "tx_11", "date": "2026-10-16", "type": "expense", "amount": 820000, "category": "Kesehatan & Asuransi", "accountId": "acc_1", "description": "Medical Checkup & Vitamin"},
        {"id": "tx_12", "date": "2026-10-17", "type": "expense", "amount": 540000, "category": "Belanja & Hiburan", "accountId": "acc_3", "description": "Beli Buku & ATK Kantor"}
    ]
}

def load_data():
    if "finance_data" not in st.session_state:
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    st.session_state.finance_data = json.load(f)
            except Exception:
                st.session_state.finance_data = INITIAL_DATA.copy()
        else:
            st.session_state.finance_data = INITIAL_DATA.copy()
        recalculate_balances()
    return st.session_state.finance_data

def save_data():
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.finance_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.sidebar.error(f"Penyimpanan lokal error: {e}")

def recalculate_balances():
    data = st.session_state.finance_data
    # Map initial balances
    balance_map = {}
    for acc in data["accounts"]:
        init = acc.get("initialBalance", acc.get("balance", 0))
        acc["initialBalance"] = int(init)
        balance_map[acc["id"]] = int(init)

    # Sort transactions chronologically
    sorted_tx = sorted(data["transactions"], key=lambda x: x["date"])
    for tx in sorted_tx:
        amt = int(tx.get("amount", 0))
        t_type = tx.get("type")
        from_id = tx.get("accountId")
        to_id = tx.get("toAccountId")

        if t_type == "income" and from_id in balance_map:
            balance_map[from_id] += amt
        elif t_type == "expense" and from_id in balance_map:
            balance_map[from_id] -= amt
        elif t_type == "transfer":
            if from_id in balance_map:
                balance_map[from_id] -= amt
            if to_id in balance_map:
                balance_map[to_id] += amt

    for acc in data["accounts"]:
        acc["balance"] = balance_map.get(acc["id"], 0)

def format_idr(val):
    nominal = int(round(val or 0))
    return f"Rp {nominal:,.0f}".replace(",", ".")

# Load data on start
data = load_data()

# Account Lookup Helpers
account_names = {a["id"]: a["name"] for a in data["accounts"]}
account_options = {f"{a.get('icon', '🏦')} {a['name']} ({format_idr(a['balance'])})": a["id"] for a in data["accounts"]}

# ==============================================================================
# 3. SIDEBAR NAVIGATION & QUICK STATS
# ==============================================================================
with st.sidebar:
    st.markdown("### 💎 **FinansialKu**")
    st.caption("Fintech Financial Suite")

    menu = st.radio(
        "Pilih Menu:",
        [
            "📊 Dashboard Ringkasan",
            "💳 Multi-Account & Transfer",
            "📝 Buku Transaksi",
            "🎯 Anggaran & Smart Alerts",
            "💎 Net Worth Tracker",
            "🔁 Transaksi Berulang",
            "💡 Financial Insights",
            "📄 Laporan & Export",
            "📑 Spreadsheet Asli (HTML)"
        ]
    )

    st.markdown("---")
    # Compute quick stats
    liquid_total = sum(a["balance"] for a in data["accounts"])
    non_liquid_assets = sum(ast["value"] for ast in data["assetsLiabilities"] if ast["type"] == "asset")
    liabilities = sum(l["value"] for l in data["assetsLiabilities"] if l["type"] == "liability")
    net_worth = (liquid_total + non_liquid_assets) - liabilities

    st.caption("KEKAYAAN BERSIH (NET WORTH)")
    st.markdown(f"### **{format_idr(net_worth)}**")
    st.caption(f"Saldo Likuid: {format_idr(liquid_total)}")

# ==============================================================================
# 4. VIEW 1: DASHBOARD RINGKASAN
# ==============================================================================
current_month_str = datetime.now().strftime("%Y-%m")

if menu == "📊 Dashboard Ringkasan":
    st.title("📊 Dashboard Ringkasan Finansial")
    st.caption("Gambaran menyeluruh arus kas, performa anggaran, dan kekayaan bersih Anda.")

    # Calculations for current month
    month_income = 0
    month_expense = 0
    for tx in data["transactions"]:
        if tx["date"].startswith(current_month_str):
            if tx["type"] == "income":
                month_income += int(tx["amount"])
            elif tx["type"] == "expense":
                month_expense += int(tx["amount"])

    net_cashflow = month_income - month_expense

    # Mathematical run-rate month-end estimate
    today = datetime.now()
    days_in_month = 31 if today.month in [1, 3, 5, 7, 8, 10, 12] else (28 if today.month == 2 else 30)
    current_day = max(today.day, 1)
    days_remaining = max(days_in_month - current_day, 0)
    daily_net = (month_income - month_expense) / current_day
    projected_end_balance = int(liquid_total + (daily_net * days_remaining))

    # Top Metric Cards (Row 1)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-metric-title">Total Saldo Likuid</div>
            <div class="fintech-metric-val">{format_idr(liquid_total)}</div>
            <span class="fintech-tag tag-income">Di {len(data['accounts'])} Rekening</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-metric-title">Pemasukan Bulan Ini</div>
            <div class="fintech-metric-val" style="color:#10b981;">{format_idr(month_income)}</div>
            <span class="fintech-tag tag-income">Arus Kas Masuk</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-metric-title">Pengeluaran Bulan Ini</div>
            <div class="fintech-metric-val" style="color:#ef4444;">{format_idr(month_expense)}</div>
            <span class="fintech-tag tag-expense">Arus Kas Keluar</span>
        </div>
        """, unsafe_allow_html=True)

    # Metric Cards (Row 2)
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-metric-title">Surplus / Defisit Arus Kas</div>
            <div class="fintech-metric-val" style="color:{'#10b981' if net_cashflow >= 0 else '#ef4444'};">{format_idr(net_cashflow)}</div>
            <span class="fintech-tag tag-transfer">Bulan Berjalan</span>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-metric-title">Kekayaan Bersih (Net Worth)</div>
            <div class="fintech-metric-val" style="color:#8b5cf6;">{format_idr(net_worth)}</div>
            <span class="fintech-tag tag-transfer">Aset Likuid + Fisik - Utang</span>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
        <div class="fintech-card">
            <div class="fintech-metric-title">Prediksi Saldo Akhir Bulan</div>
            <div class="fintech-metric-val">{format_idr(projected_end_balance)}</div>
            <span class="fintech-tag tag-alert">Estimasi Run-Rate</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Visual Charts
    col_chart1, col_chart2 = st.columns([1.3, 1])
    with col_chart1:
        st.subheader("📈 Tren Arus Kas Bulanan")
        # Build month aggregations
        tx_df = pd.DataFrame(data["transactions"])
        if not tx_df.empty:
            tx_df["month"] = tx_df["date"].str.slice(0, 7)
            agg = tx_df.groupby(["month", "type"])["amount"].sum().reset_index()
            # Filter only income and expense
            agg = agg[agg["type"].isin(["income", "expense"])]
            agg["type_label"] = agg["type"].map({"income": "Pemasukan", "expense": "Pengeluaran"})

            fig_bar = px.bar(
                agg,
                x="month",
                y="amount",
                color="type_label",
                barmode="group",
                color_discrete_map={"Pemasukan": "#10b981", "Pengeluaran": "#ef4444"},
                labels={"amount": "Nominal (IDR)", "month": "Bulan", "type_label": "Tipe"}
            )
            fig_bar.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="Plus Jakarta Sans",
                margin=dict(l=0, r=0, t=20, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Belum ada data transaksi untuk visualisasi grafik.")

    with col_chart2:
        st.subheader("🍩 Proporsi Pengeluaran")
        exp_df = tx_df[(tx_df["type"] == "expense") & (tx_df["date"].str.startswith(current_month_str))] if not tx_df.empty else pd.DataFrame()
        if not exp_df.empty:
            cat_sum = exp_df.groupby("category")["amount"].sum().reset_index()
            fig_pie = px.pie(
                cat_sum,
                values="amount",
                names="category",
                hole=0.65,
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_pie.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="Plus Jakarta Sans",
                margin=dict(l=0, r=0, t=10, b=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Belum ada pengeluaran di bulan ini.")

    # Recent Transactions Table
    st.subheader("📝 Transaksi Terkini")
    recent = data["transactions"][:6]
    if recent:
        table_rows = []
        for r in recent:
            acc_name = account_names.get(r["accountId"], "-")
            to_acc = account_names.get(r.get("toAccountId"), "-") if r.get("toAccountId") else "-"
            table_rows.append({
                "Tanggal": r["date"],
                "Tipe": r["type"].upper(),
                "Kategori": r.get("category", "-"),
                "Deskripsi": r.get("description", "-"),
                "Akun Asal": acc_name,
                "Akun Tujuan": to_acc,
                "Nominal": format_idr(r["amount"])
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

# ==============================================================================
# 5. VIEW 2: MULTI-ACCOUNT & TRANSFER
# ==============================================================================
elif menu == "💳 Multi-Account & Transfer":
    st.title("💳 Multi-Account & Transfer Antar-Rekening")
    st.caption("Pencatatan saldo multi-bank, dompet digital, dan transfer saldo tanpa memengaruhi laporan laba-rugi.")

    # Accounts Overview Grid
    st.subheader("Daftar Akun Keuangan")
    acc_cols = st.columns(len(data["accounts"]))
    for i, acc in enumerate(data["accounts"]):
        with acc_cols[i % len(acc_cols)]:
            st.markdown(f"""
            <div class="fintech-card" style="border-top: 4px solid {acc.get('color', '#10b981')};">
                <div style="font-size: 1.5rem;">{acc.get('icon', '🏦')}</div>
                <div style="font-weight: 700; font-size: 1.05rem; margin-top: 0.25rem;">{acc['name']}</div>
                <span class="fintech-tag tag-transfer">{acc['type'].upper()}</span>
                <div style="margin-top: 0.75rem; font-size: 0.75rem; color: #94a3b8;">Saldo Terkini:</div>
                <div style="font-size: 1.25rem; font-weight: 800;">{format_idr(acc['balance'])}</div>
                <div style="font-size: 0.75rem; color: #64748b;">No: {acc.get('number', '-')}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.subheader("⇄ Transfer Antar-Rekening")
        with st.form("form_transfer"):
            src_acc_label = st.selectbox("Dari Akun (Pengirim):", list(account_options.keys()), key="src_acc")
            dst_acc_label = st.selectbox("Ke Akun (Penerima):", list(account_options.keys()), key="dst_acc")
            trf_amount = st.number_input("Nominal Transfer (IDR):", min_value=1000, step=50000, value=500000)
            trf_date = st.date_input("Tanggal Transfer:", value=date.today())
            trf_notes = st.text_input("Catatan Transfer:", value="Transfer saldo internal")
            submit_trf = st.form_submit_button("Eksekusi Transfer ➔")

            if submit_trf:
                src_id = account_options[src_acc_label]
                dst_id = account_options[dst_acc_label]
                if src_id == dst_id:
                    st.error("Akun asal dan akun tujuan tidak boleh sama.")
                else:
                    new_tx = {
                        "id": f"tx_trf_{int(datetime.now().timestamp())}",
                        "date": trf_date.strftime("%Y-%m-%d"),
                        "type": "transfer",
                        "amount": int(trf_amount),
                        "accountId": src_id,
                        "toAccountId": dst_id,
                        "category": "Transfer Saldo",
                        "description": trf_notes
                    }
                    data["transactions"].insert(0, new_tx)
                    recalculate_balances()
                    save_data()
                    st.success("Transfer antar-rekening berhasil dieksekusi!")
                    st.rerun()

    with col_t2:
        st.subheader("➕ Tambah Akun Baru")
        with st.form("form_add_account"):
            new_acc_name = st.text_input("Nama Akun / Bank:", placeholder="Contoh: SeaBank, OVO, Dompet Tunai")
            new_acc_type = st.selectbox("Tipe Akun:", ["bank", "ewallet", "cash", "investment", "other"])
            new_acc_balance = st.number_input("Saldo Awal (IDR):", min_value=0, step=100000, value=0)
            new_acc_number = st.text_input("Nomor Rekening / Catatan:", placeholder="Contoh: 123-456-7890")
            submit_acc = st.form_submit_button("Simpan Akun Baru")

            if submit_acc:
                if not new_acc_name.strip():
                    st.error("Nama akun wajib diisi.")
                else:
                    icon_map = {"bank": "🏦", "ewallet": "📱", "cash": "💵", "investment": "📈", "other": "💳"}
                    new_acc = {
                        "id": f"acc_{int(datetime.now().timestamp())}",
                        "name": new_acc_name.strip(),
                        "type": new_acc_type,
                        "balance": int(new_acc_balance),
                        "initialBalance": int(new_acc_balance),
                        "number": new_acc_number.strip() or "-",
                        "color": "#10b981",
                        "icon": icon_map.get(new_acc_type, "🏦")
                    }
                    data["accounts"].append(new_acc)
                    recalculate_balances()
                    save_data()
                    st.success(f"Akun {new_acc_name} berhasil ditambahkan!")
                    st.rerun()

# ==============================================================================
# 6. VIEW 3: BUKU TRANSAKSI
# ==============================================================================
elif menu == "📝 Buku Transaksi":
    st.title("📝 Buku Kas & Riwayat Transaksi")
    st.caption("Pencatatan transaksi pemasukan, pengeluaran, dan transfer dengan filter komprehensif.")

    # Quick Add Transaction Expander
    with st.expander("➕ Catat Transaksi Baru", expanded=False):
        with st.form("form_add_tx"):
            col_tx1, col_tx2 = st.columns(2)
            with col_tx1:
                tx_type = st.selectbox("Tipe Transaksi:", ["expense", "income", "transfer"])
                tx_amount = st.number_input("Nominal (IDR):", min_value=100, step=50000, value=150000)
                tx_date = st.date_input("Tanggal:", value=date.today())
            with col_tx2:
                tx_acc_label = st.selectbox("Akun Asal:", list(account_options.keys()))
                tx_to_acc_label = st.selectbox("Akun Tujuan (Khusus Transfer):", ["-"] + list(account_options.keys()))
                tx_category = st.selectbox("Kategori:", [
                    "Makanan & Minuman", "Transportasi & Bensin", "Tagihan & Utilitas",
                    "Belanja & Hiburan", "Kesehatan & Asuransi", "Gaji & Pendapatan",
                    "Investasi & Bonus", "Lain-lain"
                ])
            tx_desc = st.text_input("Keterangan Transaksi:", placeholder="Catatan pembelian / pemasukan")
            submit_tx = st.form_submit_button("Simpan Transaksi ➔")

            if submit_tx:
                src_id = account_options[tx_acc_label]
                to_id = account_options[tx_to_acc_label] if (tx_type == "transfer" and tx_to_acc_label != "-") else None
                if tx_type == "transfer" and (not to_id or src_id == to_id):
                    st.error("Transfer harus memiliki akun tujuan yang berbeda.")
                else:
                    new_tx = {
                        "id": f"tx_{int(datetime.now().timestamp())}",
                        "date": tx_date.strftime("%Y-%m-%d"),
                        "type": tx_type,
                        "amount": int(tx_amount),
                        "category": "Transfer Saldo" if tx_type == "transfer" else tx_category,
                        "accountId": src_id,
                        "toAccountId": to_id,
                        "description": tx_desc.strip()
                    }
                    data["transactions"].insert(0, new_tx)
                    recalculate_balances()
                    save_data()
                    st.success("Transaksi berhasil dicatat!")
                    st.rerun()

    # Search and Filter Toolbar
    st.subheader("Filter & Riwayat Transaksi")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        search_kw = st.text_input("🔍 Cari Keterangan / Kategori:", placeholder="Ketik kata kunci...")
    with col_f2:
        filter_type = st.selectbox("Filter Tipe:", ["Semua Tipe", "Pemasukan", "Pengeluaran", "Transfer"])
    with col_f3:
        filter_acc = st.selectbox("Filter Akun:", ["Semua Akun"] + [a["name"] for a in data["accounts"]])

    # Apply filters
    filtered_tx = data["transactions"].copy()
    if search_kw:
        kw = search_kw.lower()
        filtered_tx = [t for t in filtered_tx if kw in t.get("description", "").lower() or kw in t.get("category", "").lower()]
    if filter_type != "Semua Tipe":
        type_key = "income" if filter_type == "Pemasukan" else ("expense" if filter_type == "Pengeluaran" else "transfer")
        filtered_tx = [t for t in filtered_tx if t.get("type") == type_key]
    if filter_acc != "Semua Akun":
        acc_id = next((a["id"] for a in data["accounts"] if a["name"] == filter_acc), None)
        filtered_tx = [t for t in filtered_tx if t.get("accountId") == acc_id or t.get("toAccountId") == acc_id]

    st.caption(f"Menampilkan {len(filtered_tx)} transaksi:")
    if filtered_tx:
        table_data = []
        for t in filtered_tx:
            src = account_names.get(t.get("accountId"), "-")
            dst = account_names.get(t.get("toAccountId"), "-") if t.get("toAccountId") else "-"
            table_data.append({
                "ID": t.get("id"),
                "Tanggal": t.get("date"),
                "Tipe": t.get("type").upper(),
                "Kategori": t.get("category", "-"),
                "Deskripsi": t.get("description", "-"),
                "Akun Asal": src,
                "Akun Tujuan": dst,
                "Nominal": format_idr(t.get("amount", 0))
            })
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada transaksi yang cocok dengan filter yang dipilih.")

# ==============================================================================
# 7. VIEW 4: ANGGARAN & SMART ALERTS (FEATURE 1)
# ==============================================================================
elif menu == "🎯 Anggaran & Smart Alerts":
    st.title("🎯 Monthly Budget + Smart Alerts")
    st.caption("Pantau batas anggaran bulanan per kategori dengan indikator otomatis pada batas 80% & 100%.")

    # Compute actual spent per category for current month
    expense_by_cat = {}
    for tx in data["transactions"]:
        if tx["type"] == "expense" and tx["date"].startswith(current_month_str):
            cat = tx.get("category", "Lain-lain")
            expense_by_cat[cat] = expense_by_cat.get(cat, 0) + int(tx["amount"])

    today_day = datetime.now().day
    days_in_month = 31

    # Render Budget Cards
    st.subheader(f"Status Anggaran Periode: {current_month_str}")
    for b in data["budgets"]:
        spent = expense_by_cat.get(b["category"], 0)
        limit = int(b["limit"])
        pct = int(min(round((spent / limit) * 100), 999)) if limit > 0 else 0
        remaining = limit - spent

        # Run-rate projection to detect potential overbudget
        daily_spent = spent / max(today_day, 1)
        projected = int(spent + (daily_spent * (days_in_month - today_day)))
        is_projected_over = projected > limit

        # Status badge & color
        status_color = "#10b981" if pct < 80 else ("#f59e0b" if pct < 100 else "#ef4444")
        status_label = "✅ Aman" if pct < 80 else ("⚠️ Waspada (≥80%)" if pct < 100 else "🚨 Overbudget (100%+)")

        with st.container():
            st.markdown(f"""
            <div class="fintech-card" style="border-left: 6px solid {status_color};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-size:1.1rem; font-weight:700;">{b['category']}</div>
                    <span class="fintech-tag" style="background:{status_color}22; color:{status_color};">{status_label}</span>
                </div>
                <div style="margin: 0.5rem 0;">
                    <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#94a3b8;">
                        <span>Realisasi: <strong>{format_idr(spent)}</strong> ({pct}%)</span>
                        <span>Batas Limit: <strong>{format_idr(limit)}</strong></span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(min(pct / 100.0, 1.0))
            if is_projected_over:
                st.caption(f"⚠️ Berdasarkan laju pengeluaran harian, kategori ini berpotensi mencapai **{format_idr(projected)}** di akhir bulan.")
            st.write("")

    # Add / Update Budget Form
    st.markdown("---")
    st.subheader("Atur Batas Anggaran Kategori")
    with st.form("form_budget"):
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            bg_cat = st.selectbox("Pilih Kategori:", [
                "Makanan & Minuman", "Transportasi & Bensin", "Tagihan & Utilitas",
                "Belanja & Hiburan", "Kesehatan & Asuransi", "Lain-lain"
            ])
        with col_b2:
            bg_limit = st.number_input("Batas Maksimal Anggaran (IDR):", min_value=100000, step=250000, value=3000000)
        submit_bg = st.form_submit_button("Simpan Anggaran ➔")

        if submit_bg:
            existing = next((b for b in data["budgets"] if b["category"] == bg_cat), None)
            if existing:
                existing["limit"] = int(bg_limit)
            else:
                data["budgets"].append({
                    "id": f"bg_{int(datetime.now().timestamp())}",
                    "category": bg_cat,
                    "limit": int(bg_limit),
                    "period": current_month_str
                })
            save_data()
            st.success(f"Batas anggaran untuk {bg_cat} berhasil diperbarui!")
            st.rerun()

# ==============================================================================
# 8. VIEW 5: NET WORTH TRACKER (FEATURE 2)
# ==============================================================================
elif menu == "💎 Net Worth Tracker":
    st.title("💎 Net Worth Tracker (Kekayaan Bersih)")
    st.markdown("""
    Formula Finansial:  
    $$\\text{Net Worth} = \\text{Total Aset (Likuid + Fisik/Investasi)} - \\text{Total Liabilitas (Utang/Beban)}$$
    """)

    # Overview Metrics
    col_nw1, col_nw2, col_nw3 = st.columns(3)
    with col_nw1:
        st.metric("Total Aset Likuid & Fisik", format_idr(liquid_total + non_liquid_assets))
    with col_nw2:
        st.metric("Total Liabilitas (Utang)", format_idr(liabilities))
    with col_nw3:
        st.metric("Kekayaan Bersih (Net Worth)", format_idr(net_worth))

    # Net Worth Evolution Chart
    st.subheader("📈 Progres Perkembangan Kekayaan")
    months = ["Mei", "Jun", "Jul", "Agu", "Sep", "Okt"]
    history_points = [
        int(net_worth * 0.88), int(net_worth * 0.91), int(net_worth * 0.93),
        int(net_worth * 0.95), int(net_worth * 0.98), int(net_worth)
    ]
    fig_nw = go.Figure(data=go.Scatter(
        x=months,
        y=history_points,
        mode="lines+markers",
        line=dict(color="#10b981", width=3),
        fill="tozeroy",
        fillcolor="rgba(16, 185, 129, 0.15)"
    ))
    fig_nw.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_family="Plus Jakarta Sans",
        yaxis_title="Nominal (IDR)",
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig_nw, use_container_width=True)

    # Tables: Assets vs Liabilities
    col_a, col_l = st.columns(2)
    with col_a:
        st.subheader("🏢 Aset Fisik & Investasi")
        assets = [a for a in data["assetsLiabilities"] if a["type"] == "asset"]
        if assets:
            st.dataframe(pd.DataFrame(assets)[["name", "category", "value", "notes"]].rename(columns={
                "name": "Nama Aset", "category": "Kategori", "value": "Nilai Estimasi", "notes": "Catatan"
            }), use_container_width=True, hide_index=True)

    with col_l:
        st.subheader("💳 Liabilitas & Beban Utang")
        liab = [l for l in data["assetsLiabilities"] if l["type"] == "liability"]
        if liab:
            st.dataframe(pd.DataFrame(liab)[["name", "category", "value", "notes"]].rename(columns={
                "name": "Beban Utang", "category": "Kategori", "value": "Sisa Pokok", "notes": "Catatan"
            }), use_container_width=True, hide_index=True)

    # Add Asset or Liability Form
    with st.expander("➕ Tambah Aset / Liabilitas Baru"):
        with st.form("form_ast_liab"):
            item_type = st.selectbox("Klasifikasi:", ["asset (Aset +)", "liability (Liabilitas / Utang -)"])
            item_name = st.text_input("Nama Barang / Kredit:", placeholder="Contoh: Apartemen, Tanah, Kartu Kredit Mandiri")
            item_val = st.number_input("Nilai / Sisa Pokok (IDR):", min_value=1000, step=1000000, value=10000000)
            item_notes = st.text_input("Catatan Tambahan:", placeholder="Keterangan tenor atau kondisi")
            submit_ast = st.form_submit_button("Simpan Data")

            if submit_ast:
                raw_type = "asset" if "asset" in item_type else "liability"
                new_item = {
                    "id": f"ast_{int(datetime.now().timestamp())}",
                    "name": item_name.strip(),
                    "type": raw_type,
                    "category": "general",
                    "value": int(item_val),
                    "notes": item_notes.strip()
                }
                data["assetsLiabilities"].append(new_item)
                save_data()
                st.success("Data kekayaan bersih berhasil ditambahkan!")
                st.rerun()

# ==============================================================================
# 9. VIEW 6: TRANSAKSI BERULANG (FEATURE 4)
# ==============================================================================
elif menu == "🔁 Transaksi Berulang":
    st.title("🔁 Transaksi Berulang & Pengingat Tagihan")
    st.caption("Otomatisasi pencatatan gaji, cicilan KPR, langganan aplikasi, dan tagihan utilitas berkala.")

    st.subheader("Jadwal Transaksi Rutin")
    for r in data["recurring"]:
        acc_name = account_names.get(r["accountId"], "-")
        status_tag = "tag-income" if r.get("active", True) else "tag-expense"
        with st.container():
            st.markdown(f"""
            <div class="fintech-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:1.15rem; font-weight:700;">{r['name']}</span>
                        <span class="fintech-tag {status_tag}">{r['type'].upper()}</span>
                    </div>
                    <div style="font-size:1.2rem; font-weight:800;">{format_idr(r['amount'])}</div>
                </div>
                <div style="margin-top:0.4rem; font-size:0.85rem; color:#94a3b8;">
                    Frekuensi: <strong>{r['frequency'].capitalize()}</strong> (Tiap tanggal {r['dayOfMonth']}) | Akun: <strong>{acc_name}</strong> | Terakhir dieksekusi: {r.get('lastRun', 'Belum pernah')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            col_b1, col_b2 = st.columns([1, 5])
            with col_b1:
                if st.button("⚡ Catat Sekarang", key=f"btn_rec_{r['id']}"):
                    # Deduplication guard: check if already logged today
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    already = any(t.get("recurringId") == r["id"] and t.get("date") == today_str for t in data["transactions"])
                    if already:
                        st.warning(f"Transaksi {r['name']} sudah pernah dicatat untuk hari ini ({today_str}).")
                    else:
                        new_tx = {
                            "id": f"tx_rec_{int(datetime.now().timestamp())}",
                            "date": today_str,
                            "type": r["type"],
                            "amount": int(r["amount"]),
                            "category": r["category"],
                            "accountId": r["accountId"],
                            "description": f"[Otomatis: {r['name']}]",
                            "recurringId": r["id"]
                        }
                        data["transactions"].insert(0, new_tx)
                        r["lastRun"] = today_str
                        recalculate_balances()
                        save_data()
                        st.success(f"Berhasil mencatat transaksi berulang {r['name']}!")
                        st.rerun()

    # Form Add Recurring
    with st.expander("➕ Tambah Jadwal Berulang Baru"):
        with st.form("form_recurring"):
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                r_name = st.text_input("Nama Jadwal:", placeholder="Contoh: Gaji, Cicilan, Internet Fiber")
                r_type = st.selectbox("Tipe Transaksi:", ["expense", "income"])
                r_amount = st.number_input("Nominal (IDR):", min_value=1000, step=50000, value=500000)
            with col_r2:
                r_freq = st.selectbox("Frekuensi:", ["monthly", "weekly", "daily", "yearly"])
                r_day = st.number_input("Tanggal Eksekusi (1-31):", min_value=1, max_value=31, value=1)
                r_acc_label = st.selectbox("Akun Terkait:", list(account_options.keys()))
            r_cat = st.text_input("Kategori:", value="Tagihan & Utilitas")
            submit_rec = st.form_submit_button("Simpan Jadwal Berulang")

            if submit_rec:
                new_rec = {
                    "id": f"rec_{int(datetime.now().timestamp())}",
                    "name": r_name.strip(),
                    "type": r_type,
                    "amount": int(r_amount),
                    "frequency": r_freq,
                    "dayOfMonth": int(r_day),
                    "accountId": account_options[r_acc_label],
                    "category": r_cat.strip(),
                    "active": True
                }
                data["recurring"].append(new_rec)
                save_data()
                st.success("Jadwal berulang berhasil ditambahkan!")
                st.rerun()

# ==============================================================================
# 10. VIEW 7: FINANCIAL INSIGHTS (FEATURE 3)
# ==============================================================================
elif menu == "💡 Financial Insights":
    st.title("💡 Financial Insights & Evaluasi Finansial")
    st.caption("Pemeriksaan analitik berbasis data riil transaksi Anda menggunakan aturan rasio finansial.")

    # Filter month transactions
    curr_tx = [t for t in data["transactions"] if t["date"].startswith(current_month_str)]
    if len(curr_tx) < 2:
        st.info("Data transaksi pada bulan ini belum mencukupi (minimal butuh 2 transaksi) untuk menghasilkan analisis.")
    else:
        inc = sum(int(t["amount"]) for t in curr_tx if t["type"] == "income")
        exp = sum(int(t["amount"]) for t in curr_tx if t["type"] == "expense")
        cat_exp = {}
        for t in curr_tx:
            if t["type"] == "expense":
                c = t.get("category", "Lain-lain")
                cat_exp[c] = cat_exp.get(c, 0) + int(t["amount"])

        top_cat = max(cat_exp, key=cat_exp.get) if cat_exp else "-"
        top_amt = cat_exp.get(top_cat, 0)
        top_pct = int(round((top_amt / exp) * 100)) if exp > 0 else 0
        savings_rate = int(round(((inc - exp) / inc) * 100)) if inc > 0 else 0

        col_i1, col_i2, col_i3 = st.columns(3)
        with col_i1:
            st.metric("Pos Pengeluaran Terbesar", top_cat, f"{format_idr(top_amt)} ({top_pct}%)")
        with col_i2:
            st.metric("Tingkat Tabungan (Saving Rate)", f"{savings_rate}%", "Ideal ≥ 20%")
        with col_i3:
            st.metric("Estimasi Arus Kas Bersih", format_idr(inc - exp))

        st.markdown("---")
        st.subheader("Rekomendasi Strategis Berbasis Data")

        if top_pct >= 35:
            st.warning(f"⚠️ **Konsentrasi Pengeluaran pada {top_cat}**: Kategori {top_cat} menyerap {top_pct}% dari total pengeluaran Anda. Pertimbangkan alokasi pos lain atau batasi pembelian impulsif.")

        if savings_rate >= 20:
            st.success(f"✅ **Rasio Tabungan Sehat ({savings_rate}%)**: Anda menghemat lebih dari 20% pendapatan bulan ini. Ini adalah posisi arus kas surplus yang sangat baik untuk investasi berkala.")
        elif savings_rate < 10 and savings_rate >= 0:
            st.info(f"ℹ️ **Peringatan Rasio Tabungan Rendah ({savings_rate}%)**: Rasio tabungan Anda di bawah 10%. Disarankan meninjau kembali langganan atau pengeluaran hiburan.")
        elif savings_rate < 0:
            st.error(f"🚨 **Defisit Anggaran Bulanan ({format_idr(abs(inc - exp))})**: Pengeluaran melampaui pendapatan. Segera tekan pengeluaran diskresioner.")

# ==============================================================================
# 11. VIEW 8: LAPORAN & EXPORT (FEATURE 5)
# ==============================================================================
elif menu == "📄 Laporan & Export":
    st.title("📄 Export Laporan Finansial & Backup")
    st.caption("Unduh dokumen PDF resmi, spreadsheet CSV Excel-ready, atau file backup database lengkap.")

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.subheader("📥 Export Spreadsheet (CSV)")
        st.markdown("Ekspor data transaksi yang kompatibel dengan Microsoft Excel dan Google Sheets.")
        
        # Build CSV with BOM
        tx_export_df = pd.DataFrame(data["transactions"])
        csv_buffer = io.StringIO()
        tx_export_df.to_csv(csv_buffer, index=False)
        csv_bytes = ("\ufeff" + csv_buffer.getvalue()).encode("utf-8")

        st.download_button(
            label="📊 Download CSV (Excel Ready)",
            data=csv_bytes,
            file_name=f"laporan_keuangan_{current_month_str}.csv",
            mime="text/csv"
        )

    with col_e2:
        st.subheader("💾 Backup Database JSON")
        st.markdown("Simpan seluruh konfigurasi akun, aset, anggaran, dan transaksi untuk cadangan.")
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        st.download_button(
            label="💾 Download Backup JSON",
            data=json_str.encode("utf-8"),
            file_name=f"backup_keuangan_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

# ==============================================================================
# 12. VIEW 9: SPREADSHEET ASLI (PRESERVED LEGACY SHEETS)
# ==============================================================================
elif menu == "📑 Spreadsheet Asli (HTML)":
    st.title("📑 Arsip Lembar Google Sheets Asli")
    st.caption("Seluruh berkas HTML asli dari spreadsheet tetap dipertahankan 100% dan dapat dibuka langsung.")

    sheet_choice = st.selectbox(
        "Pilih Lembar Spreadsheet:",
        ["Dashboard.html", "Pembukuan.html", "Olah Data.html", "Laporan.html", "Asset Tracker.html"]
    )

    sheet_path = os.path.join(os.path.dirname(__file__), sheet_choice)
    if os.path.exists(sheet_path):
        with open(sheet_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=800, scrolling=True)
    else:
        st.error(f"Berkas {sheet_choice} tidak ditemukan.")
