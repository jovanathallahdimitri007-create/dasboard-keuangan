"""
DATABASE & FINANCIAL ENGINE - SISTEM KEUANGAN KELAS & KORLAS
Atomic transaction execution, multi-class fund accounts, student savings,
invoicing, approval workflow, and audit logging.
"""

import os
import sqlite3
import json
import uuid
from datetime import datetime, date

try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "school_finance.db")

class SchoolFinanceDB:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.supabase_client = self._init_supabase()
        self.init_database()

    def _init_supabase(self):
        if not HAS_SUPABASE:
            return None
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")
        try:
            import streamlit as st
            if not url and hasattr(st, "secrets"):
                url = st.secrets.get("SUPABASE_URL")
                key = st.secrets.get("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_KEY")
        except Exception:
            pass

        if url and key:
            try:
                return create_client(url, key)
            except Exception as e:
                print(f"[Supabase] Warning: gagal inisialisasi client: {e}")
        return None

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Academic Years
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS academic_years (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            );
            """)

            # 2. Classes
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                academic_year_id TEXT NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
                wali_kelas TEXT NOT NULL,
                korlas_name TEXT,
                notes TEXT,
                is_archived INTEGER DEFAULT 0,
                UNIQUE(name, academic_year_id)
            );
            """)

            # 3. Students
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                nisn TEXT NOT NULL UNIQUE,
                full_name TEXT NOT NULL,
                class_id TEXT NOT NULL REFERENCES classes(id) ON DELETE RESTRICT,
                gender TEXT CHECK (gender IN ('L', 'P')),
                parent_name TEXT,
                parent_phone TEXT,
                parent_pin TEXT DEFAULT '1234',
                status TEXT DEFAULT 'aktif' CHECK (status IN ('aktif', 'mutasi', 'alumni')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 4. Fund Accounts (Kas Kelas, Komite, ODL, Tabungan Siswa, Keperluan Korlas)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fund_accounts (
                id TEXT PRIMARY KEY,
                class_id TEXT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
                category TEXT NOT NULL CHECK (category IN ('kas_kelas', 'komite', 'odl', 'tabungan_siswa', 'keperluan_korlas')),
                name TEXT NOT NULL,
                current_balance INTEGER DEFAULT 0,
                description TEXT,
                UNIQUE(class_id, category, name)
            );
            """)

            # 5. Fee Types (Jenis Iuran)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fee_types (
                id TEXT PRIMARY KEY,
                class_id TEXT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
                category TEXT NOT NULL CHECK (category IN ('kas_kelas', 'komite', 'odl', 'keperluan_korlas')),
                name TEXT NOT NULL,
                amount INTEGER NOT NULL CHECK (amount > 0),
                due_date TEXT,
                description TEXT
            );
            """)

            # 6. Student Invoices (Tagihan Siswa)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_invoices (
                id TEXT PRIMARY KEY,
                fee_type_id TEXT NOT NULL REFERENCES fee_types(id) ON DELETE CASCADE,
                student_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                amount_due INTEGER NOT NULL CHECK (amount_due > 0),
                amount_paid INTEGER DEFAULT 0 CHECK (amount_paid >= 0),
                status TEXT DEFAULT 'belum_bayar' CHECK (status IN ('belum_bayar', 'sebagian', 'lunas')),
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fee_type_id, student_id)
            );
            """)

            # 7. Payments (Pembayaran Iuran)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                invoice_id TEXT NOT NULL REFERENCES student_invoices(id) ON DELETE CASCADE,
                student_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                fund_account_id TEXT NOT NULL REFERENCES fund_accounts(id),
                amount INTEGER NOT NULL CHECK (amount > 0),
                payment_date TEXT NOT NULL,
                receipt_number TEXT NOT NULL UNIQUE,
                idempotency_key TEXT UNIQUE,
                payment_method TEXT DEFAULT 'tunai',
                recorded_by TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 8. Student Savings Accounts
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS savings_accounts (
                id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL UNIQUE REFERENCES students(id) ON DELETE CASCADE,
                class_id TEXT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
                balance INTEGER DEFAULT 0 CHECK (balance >= 0),
                last_mutation_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 9. Savings Entries (Mutasi Tabungan Siswa)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS savings_entries (
                id TEXT PRIMARY KEY,
                savings_account_id TEXT NOT NULL REFERENCES savings_accounts(id) ON DELETE CASCADE,
                student_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                fund_account_id TEXT NOT NULL REFERENCES fund_accounts(id),
                type TEXT NOT NULL CHECK (type IN ('setoran', 'penarikan')),
                amount INTEGER NOT NULL CHECK (amount > 0),
                running_balance INTEGER NOT NULL CHECK (running_balance >= 0),
                transaction_date TEXT NOT NULL,
                receipt_number TEXT NOT NULL UNIQUE,
                recorded_by TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 10. General & Korlas Transactions (Pengeluaran / Pemasukan Kas Kelas)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                class_id TEXT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
                fund_account_id TEXT NOT NULL REFERENCES fund_accounts(id),
                to_fund_account_id TEXT REFERENCES fund_accounts(id),
                type TEXT NOT NULL CHECK (type IN ('income', 'expense', 'transfer', 'reversal')),
                amount INTEGER NOT NULL CHECK (amount > 0),
                transaction_date TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'posted' CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected', 'posted', 'voided')),
                approval_threshold INTEGER DEFAULT 1000000,
                created_by TEXT,
                approved_by TEXT,
                reversal_of_id TEXT REFERENCES transactions(id),
                receipt_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 11. Transaction Approvals
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction_approvals (
                id TEXT PRIMARY KEY,
                transaction_id TEXT NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
                approver_role TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')),
                decision_notes TEXT,
                decided_at TEXT
            );
            """)

            # 12. Audit Logs
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                user_role TEXT,
                action TEXT NOT NULL,
                details TEXT,
                amount INTEGER
            );
            """)

            conn.commit()
            self._seed_default_data(cursor)
            conn.commit()

    def _seed_default_data(self, cursor):
        cursor.execute("SELECT COUNT(*) FROM classes")
        if cursor.fetchone()[0] > 0:
            return  # Already seeded

        # Seed Academic Year
        ay_id = "ay_2026_2027"
        cursor.execute("""
        INSERT OR IGNORE INTO academic_years (id, name, start_date, end_date, is_active)
        VALUES (?, '2026/2027', '2026-07-01', '2027-06-30', 1);
        """, (ay_id,))

        # Seed Classes
        classes = [
            ("cls_1", "X-MIPA-1", ay_id, "Dra. Siti Rahayu, M.Pd", "Ibu Anita Dewi", "Kelas Unggulan Sains"),
            ("cls_2", "X-MIPA-2", ay_id, "Budi Santoso, S.Pd", "Bpk. Hendra Gunawan", "Kelas Digital Riset"),
            ("cls_3", "XI-MIPA-1", ay_id, "Nurul Hidayah, M.Pd", "Ibu Ratna Sari", "Kelas Olimpiade")
        ]
        cursor.executemany("""
        INSERT OR IGNORE INTO classes (id, name, academic_year_id, wali_kelas, korlas_name, notes)
        VALUES (?, ?, ?, ?, ?, ?);
        """, classes)

        # Seed Fund Accounts for each class
        categories = [
            ('kas_kelas', 'Kas Operasional Kelas', 3500000),
            ('komite', 'Dana Komite Siswa', 5000000),
            ('odl', 'Dana Kegiatan ODL', 8500000),
            ('tabungan_siswa', 'Kas Penampung Tabungan Siswa', 6250000),
            ('keperluan_korlas', 'Kas Keperluan Korlas', 2100000)
        ]
        for c_id, _, _, _, _, _ in classes:
            for cat, name, bal in categories:
                f_id = f"fnd_{c_id}_{cat}"
                cursor.execute("""
                INSERT OR IGNORE INTO fund_accounts (id, class_id, category, name, current_balance, description)
                VALUES (?, ?, ?, ?, ?, ?);
                """, (f_id, c_id, cat, f"{name} {c_id}", bal, f"Rekening pos {cat}"))

        # Seed Students for Class X-MIPA-1
        students_cls1 = [
            ("std_01", "0081234567", "Ahmad Fauzi", "cls_1", "L", "Bpk. Suryanto", "0812-9988-1122", "1234"),
            ("std_02", "0081234568", "Nabila Putri", "cls_1", "P", "Ibu Wulandari", "0813-8877-2233", "1234"),
            ("std_03", "0081234569", "Rizky Pratama", "cls_1", "L", "Bpk. Gunawan", "0815-7766-3344", "1234"),
            ("std_04", "0081234570", "Siti Aisyah", "cls_1", "P", "Bpk. Rahman", "0816-6655-4433", "1234"),
            ("std_05", "0081234571", "Dimas Anggara", "cls_1", "L", "Ibu Kartika", "0817-5544-3322", "1234")
        ]
        cursor.executemany("""
        INSERT OR IGNORE INTO students (id, nisn, full_name, class_id, gender, parent_name, parent_phone, parent_pin)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, students_cls1)

        # Seed Student Savings Accounts
        for std in students_cls1:
            sav_id = f"sav_acc_{std[0]}"
            cursor.execute("""
            INSERT OR IGNORE INTO savings_accounts (id, student_id, class_id, balance)
            VALUES (?, ?, ?, 0);
            """, (sav_id, std[0], std[3]))

        # Initial savings entries for std_01
        cursor.execute("""
        INSERT OR IGNORE INTO savings_entries (id, savings_account_id, student_id, fund_account_id, type, amount, running_balance, transaction_date, receipt_number, recorded_by, notes)
        VALUES 
        ('se_1', 'sav_acc_std_01', 'std_01', 'fnd_cls_1_tabungan_siswa', 'setoran', 200000, 200000, '2026-10-02', 'TAB-202610-001', 'Bendahara', 'Setoran Tabungan Awal'),
        ('se_2', 'sav_acc_std_01', 'std_01', 'fnd_cls_1_tabungan_siswa', 'setoran', 150000, 350000, '2026-10-09', 'TAB-202610-002', 'Bendahara', 'Setoran Mingguan'),
        ('se_3', 'sav_acc_std_01', 'std_01', 'fnd_cls_1_tabungan_siswa', 'penarikan', 50000, 300000, '2026-10-15', 'TAB-202610-003', 'Bendahara', 'Penarikan Buku Mandiri');
        """)
        cursor.execute("UPDATE savings_accounts SET balance = 300000 WHERE student_id = 'std_01'")

        # Seed Fee Types for Class X-MIPA-1
        fee_types = [
            ("fee_1", "cls_1", "kas_kelas", "Uang Kas Kelas Oktober 2026", 50000, "2026-10-31", "Iuran kas operasional bulanan"),
            ("fee_2", "cls_1", "komite", "Uang Komite Semester Ganjil", 250000, "2026-11-15", "Iuran pengembangan komite sekolah"),
            ("fee_3", "cls_1", "odl", "Biaya Outdoor Learning (ODL) Museum", 350000, "2026-11-20", "Tiket masuk & bus pariwisata"),
            ("fee_4", "cls_1", "keperluan_korlas", "Seragam Kelas & Banner Korlas", 120000, "2026-10-25", "Baju polo kelas & atribut")
        ]
        cursor.executemany("""
        INSERT OR IGNORE INTO fee_types (id, class_id, category, name, amount, due_date, description)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """, fee_types)

        # Generate Student Invoices for all students in X-MIPA-1
        for std in students_cls1:
            for fee in fee_types:
                inv_id = f"inv_{fee[0]}_{std[0]}"
                cursor.execute("""
                INSERT OR IGNORE INTO student_invoices (id, fee_type_id, student_id, amount_due, amount_paid, status)
                VALUES (?, ?, ?, ?, 0, 'belum_bayar');
                """, (inv_id, fee[0], std[0], fee[4]))

        # Seed Sample Payments for Ahmad Fauzi (std_01)
        # 1. Kas Kelas: Full Payment (50,000)
        cursor.execute("""
        UPDATE student_invoices SET amount_paid = 50000, status = 'lunas' 
        WHERE id = 'inv_fee_1_std_01';
        """)
        cursor.execute("""
        INSERT OR IGNORE INTO payments (id, invoice_id, student_id, fund_account_id, amount, payment_date, receipt_number, recorded_by, notes)
        VALUES ('pay_1', 'inv_fee_1_std_01', 'std_01', 'fnd_cls_1_kas_kelas', 50000, '2026-10-05', 'KWT-202610-001', 'Bendahara', 'Lunas Kas Kelas');
        """)

        # 2. Komite: Partial Payment (150,000 of 250,000)
        cursor.execute("""
        UPDATE student_invoices SET amount_paid = 150000, status = 'sebagian' 
        WHERE id = 'inv_fee_2_std_01';
        """)
        cursor.execute("""
        INSERT OR IGNORE INTO payments (id, invoice_id, student_id, fund_account_id, amount, payment_date, receipt_number, recorded_by, notes)
        VALUES ('pay_2', 'inv_fee_2_std_01', 'std_01', 'fnd_cls_1_komite', 150000, '2026-10-08', 'KWT-202610-002', 'Bendahara', 'Cicilan Pertama Komite');
        """)

        # Log Audit Trail
        cursor.execute("""
        INSERT INTO audit_logs (id, user_role, action, details, amount)
        VALUES ('log_init', 'System', 'Inisialisasi Database Sistem Keuangan Kelas', 'Seed kelas, pos dana, siswa, dan tagihan awal', 0);
        """)

    # ==========================================================================
    # BUSINESS LOGIC & ATOMIC OPERATIONS
    # ==========================================================================

    def log_audit(self, role, action, details, amount=0):
        with self.get_connection() as conn:
            conn.execute("""
            INSERT INTO audit_logs (id, timestamp, user_role, action, details, amount)
            VALUES (?, ?, ?, ?, ?, ?);
            """, (str(uuid.uuid4()), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), role, action, details, amount))
            conn.commit()

    def get_classes(self):
        with self.get_connection() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM classes WHERE is_archived = 0 ORDER BY name ASC").fetchall()]

    def get_students(self, class_id=None):
        with self.get_connection() as conn:
            query = "SELECT s.*, c.name as class_name FROM students s JOIN classes c ON s.class_id = c.id"
            params = []
            if class_id:
                query += " WHERE s.class_id = ?"
                params.append(class_id)
            query += " ORDER BY s.full_name ASC"
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def get_fund_accounts(self, class_id):
        with self.get_connection() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM fund_accounts WHERE class_id = ?", (class_id,)).fetchall()]

    def record_student_payment(self, invoice_id, amount, payment_date, payment_method, recorded_by, notes=""):
        """
        Atomic payment recording:
        - Updates student_invoices (paid & status)
        - Inserts into payments
        - Atomically increases destination fund_account balance
        - Writes to audit_logs
        """
        amount = int(amount)
        if amount <= 0:
            raise ValueError("Nominal pembayaran harus lebih dari 0.")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Fetch invoice
            inv = cursor.execute("""
            SELECT i.*, f.category, f.class_id, f.name as fee_name, s.full_name as student_name
            FROM student_invoices i
            JOIN fee_types f ON i.fee_type_id = f.id
            JOIN students s ON i.student_id = s.id
            WHERE i.id = ?
            """, (invoice_id,)).fetchone()
            
            if not inv:
                raise ValueError("Tagihan tidak ditemukan.")

            amount_due = inv["amount_due"]
            current_paid = inv["amount_paid"]
            remaining = amount_due - current_paid

            if amount > remaining:
                raise ValueError(f"Nominal pembayaran (Rp {amount:,}) melebihi sisa tagihan (Rp {remaining:,}).")

            new_paid = current_paid + amount
            new_status = "lunas" if new_paid >= amount_due else "sebagian"

            # Determine fund account
            fund_acc = cursor.execute("""
            SELECT id FROM fund_accounts WHERE class_id = ? AND category = ?
            """, (inv["class_id"], inv["category"])).fetchone()

            if not fund_acc:
                raise ValueError(f"Akun pos dana untuk kategori '{inv['category']}' tidak ditemukan.")

            fund_acc_id = fund_acc["id"]
            receipt_no = f"KWT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

            # 1. Update invoice
            cursor.execute("""
            UPDATE student_invoices 
            SET amount_paid = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (new_paid, new_status, invoice_id))

            # 2. Insert Payment Record
            payment_id = str(uuid.uuid4())
            cursor.execute("""
            INSERT INTO payments (id, invoice_id, student_id, fund_account_id, amount, payment_date, receipt_number, payment_method, recorded_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (payment_id, invoice_id, inv["student_id"], fund_acc_id, amount, payment_date, receipt_no, payment_method, recorded_by, notes))

            # 3. Increase Fund Account balance atomically
            cursor.execute("""
            UPDATE fund_accounts SET current_balance = current_balance + ? WHERE id = ?
            """, (amount, fund_acc_id))

            # 4. Record in class general transactions (type = income)
            cursor.execute("""
            INSERT INTO transactions (id, class_id, fund_account_id, type, amount, transaction_date, category, description, status, created_by)
            VALUES (?, ?, ?, 'income', ?, ?, ?, ?, 'posted', ?)
            """, (str(uuid.uuid4()), inv["class_id"], fund_acc_id, amount, payment_date, inv["category"], f"Pembayaran Iuran: {inv['fee_name']} - {inv['student_name']}", recorded_by))

            # 5. Audit Log
            cursor.execute("""
            INSERT INTO audit_logs (id, timestamp, user_role, action, details, amount)
            VALUES (?, ?, ?, 'Pembayaran Iuran Siswa', ?, ?)
            """, (str(uuid.uuid4()), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), recorded_by, f"{inv['student_name']} membayar {inv['fee_name']} (No: {receipt_no})", amount))

            conn.commit()
            return receipt_no

    def record_savings_mutation(self, student_id, mutation_type, amount, tx_date, recorded_by, notes=""):
        """
        Atomic student savings mutation:
        - Checks non-negative balance on withdrawal
        - Inserts into savings_entries
        - Updates savings_accounts.balance
        - Atomically adjusts class fund_account 'tabungan_siswa'
        - Logs audit trail
        """
        amount = int(amount)
        if amount <= 0:
            raise ValueError("Nominal mutasi tabungan harus lebih dari 0.")
        if mutation_type not in ('setoran', 'penarikan'):
            raise ValueError("Tipe mutasi tidak valid.")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Find savings account & student info
            sav = cursor.execute("""
            SELECT sa.*, s.class_id, s.full_name
            FROM savings_accounts sa
            JOIN students s ON sa.student_id = s.id
            WHERE sa.student_id = ?
            """, (student_id,)).fetchone()

            if not sav:
                raise ValueError("Akun tabungan siswa tidak ditemukan.")

            current_balance = sav["balance"]
            class_id = sav["class_id"]

            if mutation_type == "penarikan":
                if amount > current_balance:
                    raise ValueError(f"Saldo tabungan tidak mencukupi. Saldo saat ini: Rp {current_balance:,}, penarikan: Rp {amount:,}.")
                new_balance = current_balance - amount
            else:
                new_balance = current_balance + amount

            # Get fund account tabungan_siswa
            fund_acc = cursor.execute("""
            SELECT id FROM fund_accounts WHERE class_id = ? AND category = 'tabungan_siswa'
            """, (class_id,)).fetchone()

            if not fund_acc:
                raise ValueError("Akun penampung tabungan kelas tidak ditemukan.")

            fund_acc_id = fund_acc["id"]
            receipt_no = f"TAB-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

            # 1. Update savings account
            cursor.execute("""
            UPDATE savings_accounts SET balance = ?, last_mutation_at = CURRENT_TIMESTAMP WHERE id = ?
            """, (new_balance, sav["id"]))

            # 2. Insert savings entry
            entry_id = str(uuid.uuid4())
            cursor.execute("""
            INSERT INTO savings_entries (id, savings_account_id, student_id, fund_account_id, type, amount, running_balance, transaction_date, receipt_number, recorded_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (entry_id, sav["id"], student_id, fund_acc_id, mutation_type, amount, new_balance, tx_date, receipt_no, recorded_by, notes))

            # 3. Update fund_account balance atomically
            delta = amount if mutation_type == "setoran" else -amount
            cursor.execute("""
            UPDATE fund_accounts SET current_balance = current_balance + ? WHERE id = ?
            """, (delta, fund_acc_id))

            # 4. Audit Log
            cursor.execute("""
            INSERT INTO audit_logs (id, timestamp, user_role, action, details, amount)
            VALUES (?, ?, ?, 'Mutasi Tabungan Siswa', ?, ?)
            """, (str(uuid.uuid4()), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), recorded_by, f"{mutation_type.upper()} {sav['full_name']} Rp {amount:,} (No: {receipt_no})", amount))

            conn.commit()
            return receipt_no, new_balance

    def get_parent_portal_data(self, nisn, pin):
        """
        Fetches student details, invoices, payments, and savings history for verified parent
        """
        with self.get_connection() as conn:
            student = conn.execute("""
            SELECT s.*, c.name as class_name, c.wali_kelas, c.korlas_name
            FROM students s
            JOIN classes c ON s.class_id = c.id
            WHERE s.nisn = ? AND s.parent_pin = ?
            """, (nisn.strip(), pin.strip())).fetchone()

            if not student:
                return None

            s_id = student["id"]
            
            # Invoices
            invoices = [dict(r) for r in conn.execute("""
            SELECT i.*, f.name as fee_name, f.category, f.due_date, (i.amount_due - i.amount_paid) as remaining
            FROM student_invoices i
            JOIN fee_types f ON i.fee_type_id = f.id
            WHERE i.student_id = ?
            ORDER BY f.due_date ASC
            """, (s_id,)).fetchall()]

            # Payments
            payments = [dict(r) for r in conn.execute("""
            SELECT p.*, f.name as fee_name
            FROM payments p
            JOIN student_invoices i ON p.invoice_id = i.id
            JOIN fee_types f ON i.fee_type_id = f.id
            WHERE p.student_id = ?
            ORDER BY p.payment_date DESC
            """, (s_id,)).fetchall()]

            # Savings
            savings_acc = conn.execute("SELECT * FROM savings_accounts WHERE student_id = ?", (s_id,)).fetchone()
            savings_entries = [dict(r) for r in conn.execute("""
            SELECT * FROM savings_entries WHERE student_id = ? ORDER BY transaction_date DESC
            """, (s_id,)).fetchall()]

            return {
                "student": dict(student),
                "invoices": invoices,
                "payments": payments,
                "savings_balance": savings_acc["balance"] if savings_acc else 0,
                "savings_entries": savings_entries
            }

    def add_transaction_with_approval(self, class_id, fund_account_id, tx_type, amount, tx_date, category, description, created_by, approval_threshold=1000000):
        """
        Creates a transaction. If expense > threshold, sets to 'pending_approval'.
        Otherwise posts atomically.
        """
        amount = int(amount)
        needs_approval = (tx_type == 'expense' and amount >= approval_threshold)
        status = 'pending_approval' if needs_approval else 'posted'
        tx_id = str(uuid.uuid4())

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO transactions (id, class_id, fund_account_id, type, amount, transaction_date, category, description, status, approval_threshold, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tx_id, class_id, fund_account_id, tx_type, amount, tx_date, category, description, status, approval_threshold, created_by))

            if needs_approval:
                cursor.execute("""
                INSERT INTO transaction_approvals (id, transaction_id, approver_role, status)
                VALUES (?, ?, 'korlas', 'pending')
                """, (str(uuid.uuid4()), tx_id))
            else:
                # Deduct / increase balance immediately
                delta = amount if tx_type == 'income' else -amount
                cursor.execute("""
                UPDATE fund_accounts SET current_balance = current_balance + ? WHERE id = ?
                """, (delta, fund_account_id))

            cursor.execute("""
            INSERT INTO audit_logs (id, timestamp, user_role, action, details, amount)
            VALUES (?, ?, ?, 'Pencatatan Transaksi Kas', ?, ?)
            """, (str(uuid.uuid4()), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), created_by, f"{tx_type.upper()} {description} (Status: {status})", amount))

            conn.commit()
            return tx_id, status

    def approve_transaction(self, tx_id, approver_role, approver_name, decision_notes=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            tx = cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,)).fetchone()
            if not tx or tx["status"] != "pending_approval":
                raise ValueError("Transaksi tidak ditemukan atau tidak dalam status pending_approval.")

            # Update approval
            cursor.execute("""
            UPDATE transaction_approvals 
            SET status = 'approved', decision_notes = ?, decided_at = CURRENT_TIMESTAMP
            WHERE transaction_id = ?
            """, (decision_notes, tx_id))

            # Post transaction
            cursor.execute("""
            UPDATE transactions 
            SET status = 'posted', approved_by = ? 
            WHERE id = ?
            """, (approver_name, tx_id))

            # Update balance
            delta = tx["amount"] if tx["type"] == 'income' else -tx["amount"]
            cursor.execute("""
            UPDATE fund_accounts SET current_balance = current_balance + ? WHERE id = ?
            """, (delta, tx["fund_account_id"]))

            cursor.execute("""
            INSERT INTO audit_logs (id, timestamp, user_role, action, details, amount)
            VALUES (?, ?, ?, 'Persetujuan Transaksi', ?, ?)
            """, (str(uuid.uuid4()), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), approver_role, f"Persetujuan pengeluaran {tx['description']} oleh {approver_name}", tx["amount"]))

            conn.commit()

# Global Singleton DB Instance
db = SchoolFinanceDB()
