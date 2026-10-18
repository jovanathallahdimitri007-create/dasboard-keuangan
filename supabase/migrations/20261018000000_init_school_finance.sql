-- ==============================================================================
-- SISTEM KEUANGAN KELAS & KORLAS MULTI-KELAS - SUPABASE POSTGRESQL SCHEMA
-- Version: 20261018000000
-- Features: Multi-Class, Multi-Fund, Student Savings, Invoicing & Payments,
--           Approval Workflow, Parent Portal, RLS Policies & Audit Trail
-- ==============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. PROFILES (Users & Roles)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id UUID UNIQUE, -- references auth.users(id) in Supabase
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(30),
    role VARCHAR(30) NOT NULL CHECK (role IN ('admin', 'korlas', 'bendahara', 'orang_tua')),
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. ACADEMIC YEARS
CREATE TABLE IF NOT EXISTS academic_years (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE, -- e.g. "2026/2027"
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. CLASSES
CREATE TABLE IF NOT EXISTS classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL, -- e.g. "X-MIPA-1", "7A"
    academic_year_id UUID NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
    wali_kelas VARCHAR(150) NOT NULL,
    korlas_name VARCHAR(150),
    notes TEXT,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (name, academic_year_id)
);

-- 4. CLASS MEMBERSHIPS (Role to Class Mapping)
CREATE TABLE IF NOT EXISTS class_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    role VARCHAR(30) NOT NULL CHECK (role IN ('admin', 'korlas', 'bendahara')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (profile_id, class_id, role)
);

-- 5. STUDENTS
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nisn VARCHAR(30) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE RESTRICT,
    gender VARCHAR(10) CHECK (gender IN ('L', 'P')),
    parent_name VARCHAR(150),
    parent_phone VARCHAR(30),
    parent_pin_hash TEXT, -- Hashed PIN for Parent Portal access
    status VARCHAR(20) DEFAULT 'aktif' CHECK (status IN ('aktif', 'mutasi', 'alumni')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. PARENT STUDENT LINKS (Parent Account to Student Mapping)
CREATE TABLE IF NOT EXISTS parent_student_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (parent_profile_id, student_id)
);

-- 7. FUND ACCOUNTS (Jenis Akun / Pos Dana per Kelas)
-- Categories: 'kas_kelas', 'komite', 'odl', 'tabungan_siswa', 'keperluan_korlas'
CREATE TABLE IF NOT EXISTS fund_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL CHECK (category IN ('kas_kelas', 'komite', 'odl', 'tabungan_siswa', 'keperluan_korlas')),
    name VARCHAR(100) NOT NULL,
    current_balance BIGINT DEFAULT 0, -- Stored in whole Indonesian Rupiah (IDR)
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (class_id, category, name)
);

-- 8. FEE TYPES (Jenis Tagihan Iuran)
CREATE TABLE IF NOT EXISTS fee_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL CHECK (category IN ('kas_kelas', 'komite', 'odl', 'keperluan_korlas')),
    name VARCHAR(120) NOT NULL, -- e.g. "Kas Kelas Oktober 2026", "ODL Museum Nasional"
    amount BIGINT NOT NULL CHECK (amount > 0),
    due_date DATE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. STUDENT INVOICES (Tagihan Iuran per Siswa)
CREATE TABLE IF NOT EXISTS student_invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fee_type_id UUID NOT NULL REFERENCES fee_types(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    amount_due BIGINT NOT NULL CHECK (amount_due > 0),
    amount_paid BIGINT DEFAULT 0 CHECK (amount_paid >= 0),
    status VARCHAR(30) DEFAULT 'belum_bayar' CHECK (status IN ('belum_bayar', 'sebagian', 'lunas')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (fee_type_id, student_id)
);

-- 10. PAYMENTS (Pembayaran Tagihan Iuran)
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES student_invoices(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    fund_account_id UUID NOT NULL REFERENCES fund_accounts(id) ON DELETE RESTRICT,
    amount BIGINT NOT NULL CHECK (amount > 0),
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    receipt_number VARCHAR(60) NOT NULL UNIQUE,
    idempotency_key VARCHAR(100) UNIQUE, -- Anti duplicate payment protection
    payment_method VARCHAR(40) DEFAULT 'tunai', -- 'tunai', 'transfer_bank', 'qris'
    recorded_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 11. STUDENT SAVINGS ACCOUNTS (Akun Tabungan Siswa Individual)
CREATE TABLE IF NOT EXISTS savings_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL UNIQUE REFERENCES students(id) ON DELETE CASCADE,
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    balance BIGINT DEFAULT 0 CHECK (balance >= 0), -- Saldo tabungan tidak boleh negatif
    last_mutation_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 12. SAVINGS ENTRIES (Buku Mutasi Tabungan Siswa)
CREATE TABLE IF NOT EXISTS savings_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    savings_account_id UUID NOT NULL REFERENCES savings_accounts(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    fund_account_id UUID NOT NULL REFERENCES fund_accounts(id) ON DELETE RESTRICT,
    type VARCHAR(20) NOT NULL CHECK (type IN ('setoran', 'penarikan')),
    amount BIGINT NOT NULL CHECK (amount > 0),
    running_balance BIGINT NOT NULL CHECK (running_balance >= 0),
    transaction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    receipt_number VARCHAR(60) NOT NULL UNIQUE,
    recorded_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 13. TRANSACTIONS (Pemasukan, Pengeluaran & Transfer Dana Kelas)
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    fund_account_id UUID NOT NULL REFERENCES fund_accounts(id) ON DELETE RESTRICT,
    to_fund_account_id UUID REFERENCES fund_accounts(id) ON DELETE RESTRICT, -- For internal transfer
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense', 'transfer', 'reversal')),
    amount BIGINT NOT NULL CHECK (amount > 0),
    transaction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    category VARCHAR(80) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'posted' CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected', 'posted', 'voided')),
    approval_threshold BIGINT DEFAULT 1000000, -- Persetujuan Korlas dibutuhkan jika di atas ambang batas
    created_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    approved_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    reversal_of_id UUID REFERENCES transactions(id),
    receipt_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    posted_at TIMESTAMPTZ
);

-- 14. TRANSACTION APPROVALS (Alur Persetujuan Pengeluaran)
CREATE TABLE IF NOT EXISTS transaction_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    approver_profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')),
    decision_notes TEXT,
    decided_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 15. ATTACHMENTS (Bukti Transaksi & Struk Pembayaran)
CREATE TABLE IF NOT EXISTS attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    related_type VARCHAR(40) NOT NULL, -- 'transaction', 'payment', 'savings'
    related_id UUID NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_url TEXT NOT NULL,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    uploaded_by UUID REFERENCES profiles(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 16. AUDIT LOGS (Rekam Jejak Aktivitas Sensitif)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    user_role VARCHAR(30),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(60),
    record_id UUID,
    details JSONB,
    amount BIGINT,
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================================================================
-- INDEXES FOR HIGH-PERFORMANCE QUERYING
-- ==============================================================================
CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_id);
CREATE INDEX IF NOT EXISTS idx_students_nisn ON students(nisn);
CREATE INDEX IF NOT EXISTS idx_invoices_student ON student_invoices(student_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON student_invoices(status);
CREATE INDEX IF NOT EXISTS idx_payments_student ON payments(student_id);
CREATE INDEX IF NOT EXISTS idx_savings_entries_student ON savings_entries(student_id);
CREATE INDEX IF NOT EXISTS idx_transactions_class ON transactions(class_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(created_at);

-- ==============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ==============================================================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_years ENABLE ROW LEVEL SECURITY;
ALTER TABLE classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE parent_student_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE fund_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE fee_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE savings_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE savings_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- 1. Profiles policy
CREATE POLICY "Public profile view" ON profiles FOR SELECT USING (true);
CREATE POLICY "Users update own profile" ON profiles FOR UPDATE USING (auth_user_id = auth.uid());

-- 2. Classes policy (Admin & authenticated staff can view; parents can view child's class)
CREATE POLICY "View classes policy" ON classes FOR SELECT USING (true);

-- 3. Students policy (Parents only view linked students; Staff view their class students)
CREATE POLICY "Parent view own student" ON students FOR SELECT USING (
    id IN (
        SELECT student_id FROM parent_student_links
        JOIN profiles ON profiles.id = parent_student_links.parent_profile_id
        WHERE profiles.auth_user_id = auth.uid()
    ) OR EXISTS (
        SELECT 1 FROM profiles WHERE profiles.auth_user_id = auth.uid() AND profiles.role IN ('admin', 'korlas', 'bendahara')
    )
);

-- 4. Savings accounts & entries policy (Parents view only own child's savings)
CREATE POLICY "Parent view child savings entries" ON savings_entries FOR SELECT USING (
    student_id IN (
        SELECT student_id FROM parent_student_links
        JOIN profiles ON profiles.id = parent_student_links.parent_profile_id
        WHERE profiles.auth_user_id = auth.uid()
    ) OR EXISTS (
        SELECT 1 FROM profiles WHERE profiles.auth_user_id = auth.uid() AND profiles.role IN ('admin', 'korlas', 'bendahara')
    )
);

-- 5. Student invoices & payments policy (Parents view only child's invoices and payments)
CREATE POLICY "Parent view child invoices" ON student_invoices FOR SELECT USING (
    student_id IN (
        SELECT student_id FROM parent_student_links
        JOIN profiles ON profiles.id = parent_student_links.parent_profile_id
        WHERE profiles.auth_user_id = auth.uid()
    ) OR EXISTS (
        SELECT 1 FROM profiles WHERE profiles.auth_user_id = auth.uid() AND profiles.role IN ('admin', 'korlas', 'bendahara')
    )
);

CREATE POLICY "Parent view child payments" ON payments FOR SELECT USING (
    student_id IN (
        SELECT student_id FROM parent_student_links
        JOIN profiles ON profiles.id = parent_student_links.parent_profile_id
        WHERE profiles.auth_user_id = auth.uid()
    ) OR EXISTS (
        SELECT 1 FROM profiles WHERE profiles.auth_user_id = auth.uid() AND profiles.role IN ('admin', 'korlas', 'bendahara')
    )
);

-- ==============================================================================
-- INITIAL SEED DATA
-- ==============================================================================
INSERT INTO academic_years (id, name, start_date, end_date, is_active)
VALUES ('00000000-0000-0000-0000-000000000001', '2026/2027', '2026-07-01', '2027-06-30', TRUE)
ON CONFLICT (name) DO NOTHING;

INSERT INTO classes (id, name, academic_year_id, wali_kelas, korlas_name)
VALUES
('00000000-0000-0000-0001-000000000001', 'X-MIPA-1', '00000000-0000-0000-0000-000000000001', 'Dra. Siti Rahayu, M.Pd', 'Ibu Anita Dewi'),
('00000000-0000-0000-0001-000000000002', 'X-MIPA-2', '00000000-0000-0000-0000-000000000001', 'Budi Santoso, S.Pd', 'Bpk. Hendra Gunawan'),
('00000000-0000-0000-0001-000000000003', 'XI-MIPA-1', '00000000-0000-0000-0000-000000000001', 'Nurul Hidayah, M.Pd', 'Ibu Ratna Sari')
ON CONFLICT DO NOTHING;

INSERT INTO fund_accounts (class_id, category, name, current_balance, description)
VALUES
('00000000-0000-0000-0001-000000000001', 'kas_kelas', 'Kas Operasional Kelas X-MIPA-1', 4850000, 'Saldo kas harian/mingguan kelas'),
('00000000-0000-0000-0001-000000000001', 'komite', 'Dana Komite Siswa X-MIPA-1', 8200000, 'Iuran pengembangan fasilitas komite'),
('00000000-0000-0000-0001-000000000001', 'odl', 'Dana Kegiatan ODL Museum', 11500000, 'Outdoor learning semester ganjil'),
('00000000-0000-0000-0001-000000000001', 'tabungan_siswa', 'Rekening Penampung Tabungan Siswa', 14250000, 'Titipan tabungan siswa individual'),
('00000000-0000-0000-0001-000000000001', 'keperluan_korlas', 'Kas Keperluan Korlas', 3200000, 'Seragam kelas, konsumsi rapat, dekorasi')
ON CONFLICT DO NOTHING;
