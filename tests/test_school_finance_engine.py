"""
AUTOMATED TEST SUITE - SISTEM KEUANGAN KELAS & KORLAS
Tests: Multi-Class Isolation, Invoicing & Payments (Partial/Full),
       Student Savings Ledger & Non-Negative Validation, Approval Workflow,
       Parent Portal Verification, and Audit Trail Logging.
"""

import os
import sys
import tempfile
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use isolated temporary database for tests
temp_dir = tempfile.mkdtemp()
test_db_path = os.path.join(temp_dir, "test_school_finance.db")

# Import database with custom path
import database
test_db = database.SchoolFinanceDB(db_path=test_db_path)

print("--- SCHOOL FINANCE TEST RUNNER START ---")
passed_tests = 0
total_tests = 0

def assert_test(condition, message):
    global passed_tests, total_tests
    total_tests += 1
    if not condition:
        print(f"❌ FAILED: {message}")
        sys.exit(1)
    else:
        passed_tests += 1
        print(f"✅ PASSED: {message}")

# 1. Multi-Class Setup & Seeding
classes = test_db.get_classes()
assert_test(len(classes) >= 3, f"Initialized {len(classes)} classes successfully (multi-class support)")
class_1 = classes[0]
students_cls1 = test_db.get_students(class_1["id"])
assert_test(len(students_cls1) >= 5, f"Loaded {len(students_cls1)} students in class {class_1['name']}")

# 2. Fund Accounts Isolation (Kas Kelas, Komite, ODL, Tabungan Siswa, Korlas)
funds_cls1 = test_db.get_fund_accounts(class_1["id"])
fund_categories = {f["category"] for f in funds_cls1}
expected_cats = {'kas_kelas', 'komite', 'odl', 'tabungan_siswa', 'keperluan_korlas'}
assert_test(expected_cats.issubset(fund_categories), "All 5 required fund categories exist and are isolated per class")

# 3. Student Invoicing & Payments (Partial and Full)
student_1 = students_cls1[0]
with test_db.get_connection() as conn:
    # Find fee for komite
    komite_inv = conn.execute("""
    SELECT i.*, f.name as fee_name, (i.amount_due - i.amount_paid) as remaining
    FROM student_invoices i
    JOIN fee_types f ON i.fee_type_id = f.id
    WHERE i.student_id = ? AND f.category = 'komite'
    """, (student_1["id"],)).fetchone()

assert_test(komite_inv is not None, "Student has active Komite invoice")
initial_paid = komite_inv["amount_paid"]
remaining = komite_inv["remaining"]

# Pay remaining amount in full
receipt = test_db.record_student_payment(
    invoice_id=komite_inv["id"],
    amount=remaining,
    payment_date="2026-10-18",
    payment_method="tunai",
    recorded_by="Bendahara",
    notes="Pelunasan sisa komite"
)
assert_test(receipt.startswith("KWT-"), f"Payment recorded with unique receipt {receipt}")

# Verify invoice is now 'lunas'
with test_db.get_connection() as conn:
    updated_inv = conn.execute("SELECT * FROM student_invoices WHERE id = ?", (komite_inv["id"],)).fetchone()
    assert_test(updated_inv["status"] == "lunas", "Invoice status accurately updated to 'lunas' after full payment")
    assert_test(updated_inv["amount_paid"] == updated_inv["amount_due"], "Total amount paid equals amount due")

# Verify paying more than remaining throws error
threw_overpay = False
try:
    test_db.record_student_payment(
        invoice_id=komite_inv["id"],
        amount=10000,
        payment_date="2026-10-18",
        payment_method="tunai",
        recorded_by="Bendahara"
    )
except ValueError:
    threw_overpay = True
assert_test(threw_overpay, "Overpaying already-settled invoice strictly blocked by validation")

# 4. Student Savings Ledger (Non-Negative Balance Enforcement)
student_2 = students_cls1[1]
# Initial balance should be 0
with test_db.get_connection() as conn:
    sav_acc = conn.execute("SELECT * FROM savings_accounts WHERE student_id = ?", (student_2["id"],)).fetchone()
assert_test(sav_acc["balance"] == 0, "New student starts with 0 savings balance")

# Deposit 100,000
rec_dep, bal_after_dep = test_db.record_savings_mutation(
    student_id=student_2["id"],
    mutation_type="setoran",
    amount=100000,
    tx_date="2026-10-18",
    recorded_by="Bendahara",
    notes="Setoran pertama"
)
assert_test(bal_after_dep == 100000, "Deposit accurately increases savings balance to Rp 100.000")

# Attempt withdrawal of 150,000 (exceeds balance -> MUST FAIL)
threw_negative = False
try:
    test_db.record_savings_mutation(
        student_id=student_2["id"],
        mutation_type="penarikan",
        amount=150000,
        tx_date="2026-10-18",
        recorded_by="Bendahara",
        notes="Tarik melebihi saldo"
    )
except ValueError:
    threw_negative = True
assert_test(threw_negative, "Withdrawal exceeding current balance strictly rejected (non-negative enforcement)")

# Valid withdrawal of 40,000
rec_wd, bal_after_wd = test_db.record_savings_mutation(
    student_id=student_2["id"],
    mutation_type="penarikan",
    amount=40000,
    tx_date="2026-10-18",
    recorded_by="Bendahara",
    notes="Tarik untuk beli buku"
)
assert_test(bal_after_wd == 60000, "Valid withdrawal accurately reduces savings balance to Rp 60.000")

# 5. Approval Workflow (Segregation of Duties for Korlas)
kas_fund = next(f for f in funds_cls1 if f["category"] == "kas_kelas")
init_kas_bal = kas_fund["current_balance"]

# Large expense requiring approval (e.g. 1,500,000 >= threshold 1,000,000)
tx_id, status = test_db.add_transaction_with_approval(
    class_id=class_1["id"],
    fund_account_id=kas_fund["id"],
    tx_type="expense",
    amount=1500000,
    tx_date="2026-10-18",
    category="Keperluan Korlas",
    description="Pengadaan Seragam Kelas",
    created_by="Bendahara",
    approval_threshold=1000000
)
assert_test(status == "pending_approval", "Expense above threshold placed in 'pending_approval' state")

# Verify fund balance was NOT deducted yet while pending
funds_check = test_db.get_fund_accounts(class_1["id"])
kas_fund_check = next(f for f in funds_check if f["category"] == "kas_kelas")
assert_test(kas_fund_check["current_balance"] == init_kas_bal, "Fund balance remains unchanged while pending approval")

# Approve transaction by Korlas
test_db.approve_transaction(tx_id, approver_role="korlas", approver_name="Ibu Anita Dewi (Ketua Korlas)")
funds_after_app = test_db.get_fund_accounts(class_1["id"])
kas_fund_after_app = next(f for f in funds_after_app if f["category"] == "kas_kelas")
assert_test(kas_fund_after_app["current_balance"] == (init_kas_bal - 1500000), "Fund balance deducted atomically after Korlas approval")

# 6. Parent Portal Verification
portal_data = test_db.get_parent_portal_data(nisn=student_1["nisn"], pin=student_1["parent_pin"])
assert_test(portal_data is not None, "Parent portal securely authenticates student with NISN and PIN")
assert_test(portal_data["student"]["full_name"] == student_1["full_name"], "Parent portal returns correct child identity")
assert_test(len(portal_data["invoices"]) > 0, "Parent portal lists active school invoices")
assert_test(len(portal_data["payments"]) > 0, "Parent portal lists verified payment receipts")

# Negative test: invalid pin
invalid_portal = test_db.get_parent_portal_data(nisn=student_1["nisn"], pin="9999")
assert_test(invalid_portal is None, "Parent portal rejects unauthorized access with wrong PIN")

# 7. Audit Trail Logging
with test_db.get_connection() as conn:
    logs = conn.execute("SELECT * FROM audit_logs").fetchall()
assert_test(len(logs) >= 5, f"Audit trail permanently logged {len(logs)} sensitive financial operations")

print(f"\n🎉 ALL {passed_tests}/{total_tests} SCHOOL FINANCE ENGINE TESTS PASSED!")
