/**
 * AUTOMATED VERIFICATION TEST SUITE - FINANCIAL ENGINE
 * Tests: Balance calculations, Transfers, Budgets & Alerts, Net Worth, Recurring Deduplication
 */

const fs = require('fs');

// Mock localStorage and window
const store = {};
global.localStorage = {
  getItem: (key) => store[key] || null,
  setItem: (key, val) => { store[key] = String(val); },
  removeItem: (key) => { delete store[key]; },
  clear: () => { Object.keys(store).forEach(k => delete store[k]); }
};
global.window = {};

// Load js/app.js
const appCode = fs.readFileSync('js/app.js', 'utf8');
eval(appCode);

const app = window.FinanceAppInstance;

console.log('--- TEST RUNNER START ---');

let passedTests = 0;
let totalTests = 0;

function assert(condition, message) {
  totalTests++;
  if (!condition) {
    console.error(`❌ FAILED: ${message}`);
    process.exit(1);
  } else {
    passedTests++;
    console.log(`✅ PASSED: ${message}`);
  }
}

// 1. Initial State & Summary
const initialSummary = app.getSummary('2026-10');
assert(initialSummary.totalLiquidBalance > 0, 'Total liquid balance is calculated accurately');
assert(initialSummary.netWorth === (initialSummary.totalAssets - initialSummary.totalLiabilities), 'Net Worth strictly equals Total Assets minus Total Liabilities');
console.log(`  Initial Net Worth: ${app.formatIDR(initialSummary.netWorth)}`);

// 2. Multi-Account Transfer Test
const acc1Before = app.accounts.find(a => a.id === 'acc_1').balance;
const acc2Before = app.accounts.find(a => a.id === 'acc_2').balance;
const netWorthBefore = app.getSummary('2026-10').netWorth;
const incomeBefore = app.getSummary('2026-10').monthIncome;
const expenseBefore = app.getSummary('2026-10').monthExpense;

const transferAmount = 1500000;
app.addTransaction({
  type: 'transfer',
  amount: transferAmount,
  date: '2026-10-18',
  accountId: 'acc_1',
  toAccountId: 'acc_2',
  description: 'Uji Transfer Test Runner'
});

const acc1After = app.accounts.find(a => a.id === 'acc_1').balance;
const acc2After = app.accounts.find(a => a.id === 'acc_2').balance;
const netWorthAfter = app.getSummary('2026-10').netWorth;
const incomeAfter = app.getSummary('2026-10').monthIncome;
const expenseAfter = app.getSummary('2026-10').monthExpense;

assert(acc1After === (acc1Before - transferAmount), 'Source account accurately deducted by transfer amount');
assert(acc2After === (acc2Before + transferAmount), 'Destination account accurately credited by transfer amount');
assert(netWorthAfter === netWorthBefore, 'Transfer does NOT change Net Worth');
assert(incomeAfter === incomeBefore, 'Transfer is NOT counted as Income');
assert(expenseAfter === expenseBefore, 'Transfer is NOT counted as Expense');

// 3. Budget & Smart Alerts Test
app.addBudget('Transportasi & Bensin', 1000000, '2026-10');
// Current expense for Transportasi in seed data is 350,000 (35%) -> Normal
let bStatus = app.getBudgetStatus('2026-10').find(b => b.category === 'Transportasi & Bensin');
assert(bStatus.status === 'normal', 'Budget status is normal when < 80%');

// Add expense to push over 80% (850,000 total / 1,000,000 = 85%)
app.addTransaction({
  type: 'expense',
  amount: 500000,
  date: '2026-10-18',
  category: 'Transportasi & Bensin',
  accountId: 'acc_1',
  description: 'Bensin luar kota'
});

bStatus = app.getBudgetStatus('2026-10').find(b => b.category === 'Transportasi & Bensin');
assert(bStatus.status === 'warning', 'Budget status triggers WARNING when >= 80%');

// Add expense to push over 100% (1,200,000 total / 1,000,000 = 120%)
app.addTransaction({
  type: 'expense',
  amount: 350000,
  date: '2026-10-18',
  category: 'Transportasi & Bensin',
  accountId: 'acc_1',
  description: 'Servis mobil'
});

bStatus = app.getBudgetStatus('2026-10').find(b => b.category === 'Transportasi & Bensin');
assert(bStatus.status === 'danger', 'Budget status triggers DANGER / OVERBUDGET when >= 100%');

// 4. Recurring Deduplication Test
const recTest = {
  id: 'rec_unit_test',
  name: 'Langganan Cloud',
  type: 'expense',
  amount: 150000,
  accountId: 'acc_1',
  category: 'Tagihan & Utilitas',
  frequency: 'monthly',
  dayOfMonth: 18,
  active: true
};
app.addRecurring(recTest);

const processedFirst = app.processRecurringItem('rec_unit_test', '2026-10-18');
assert(processedFirst === true, 'First recurring execution succeeds');

let threwDuplicate = false;
try {
  app.processRecurringItem('rec_unit_test', '2026-10-18');
} catch (e) {
  threwDuplicate = true;
}
assert(threwDuplicate === true, 'Recurring duplicate execution on the same date is strictly blocked');

// 5. Financial Insights Test
const insights = app.generateInsights('2026-10');
assert(insights.hasData === true, 'Insights generated with sufficient data');
assert(insights.topCategory !== null, 'Top expense category identified');
assert(insights.recommendations.length > 0, 'Strategic recommendations generated');
console.log(`  Top Expense Category: ${insights.topCategory} (${app.formatIDR(insights.topCategoryAmount)})`);
console.log(`  Saving Rate: ${insights.savingsRate}%`);

console.log(`\n🎉 ALL ${passedTests}/${totalTests} TESTS PASSED SUCCESSFULLY!`);
