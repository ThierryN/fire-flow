# Multi-Account Bank Management with Balance Auto-Sync - Solution & Implementation

## The Problem

A budget app needed users to manage multiple bank accounts (USAA Checking, Service CU, etc.) with:
1. Dynamic tabs filtering transactions per account
2. Automatic balance recalculation when transactions change
3. Drag-and-drop account reordering
4. Primary account designation per type
5. Account visibility toggling

### Why It Was Hard

- **Balance sync timing**: Must recalculate after every CRUD operation (create, update, delete, bulk delete, CSV import) without causing re-render storms
- **React 18 + drag-and-drop**: `react-beautiful-dnd` is incompatible with React 18 StrictMode (double-rendering breaks draggable element tracking)
- **CSV format diversity**: Different banks export wildly different CSV column names (`Date` vs `Posting Date` vs `Effective Date`)
- **Flickering on tab switch**: Unstable function references in hooks caused cascading re-renders
- **Primary uniqueness**: Must enforce one-primary-per-account-type without database constraints

### Impact

- Users couldn't track multiple bank accounts separately
- Manual balance entry was error-prone and tedious
- No way to organize or prioritize accounts

---

## The Solution

### Architecture: Reuse Existing personal_assets Table

Bank accounts already existed in `personal_assets` table (where `asset_type='bank_account'`). Instead of creating a new accounts table, we:
1. Added `account_id UUID REFERENCES personal_assets(id)` FK to `transactions` table
2. Added `display_order`, `is_primary`, `is_hidden` columns to `personal_assets`
3. Built UI components that filter by account and manage these new fields

### Key Pattern: Balance Recalculation via Callback Props

Instead of coupling hooks together, pass `recalculateBalance` as a callback prop:

```typescript
// In usePersonalAssets hook
const recalculateBalance = useCallback(async (accountId: string) => {
  const { data } = await supabase
    .from('transactions')
    .select('amount, type')
    .eq('account_id', accountId)
    .eq('is_deleted', false);

  const balance = (data || []).reduce((sum, t) => {
    if (t.type === 'income') return sum + Number(t.amount);
    if (t.type === 'expense') return sum - Number(t.amount);
    return sum;
  }, 0);

  await supabase
    .from('personal_assets')
    .update({ current_value: balance })
    .eq('id', accountId);
}, []);

// In TransactionsTabContent (wiring layer)
const { recalculateBalance } = usePersonalAssets();
<Transactions accountId={activeAccountId} onBalanceChange={recalculateBalance} />
<TransactionImport accountId={activeAccountId} onBalanceChange={recalculateBalance} />

// In Transactions component - after each CRUD operation
if (onBalanceChange && transactionData.account_id) {
  await onBalanceChange(transactionData.account_id);
}
```

### Critical Fix: react-beautiful-dnd -> @hello-pangea/dnd

`react-beautiful-dnd` is **unmaintained** and broken with React 18 StrictMode:

```
react-beautiful-dnd Unable to find draggable with id: xxx
```

**Fix**: Replace with `@hello-pangea/dnd` - a maintained fork with identical API:

```bash
npm install @hello-pangea/dnd
npm uninstall react-beautiful-dnd @types/react-beautiful-dnd
```

```typescript
// Change only the import - API is identical
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
```

### Critical Fix: Memoize fetchTransactions to Prevent Flickering

Unmemoized functions in custom hooks cause cascading re-renders:

```typescript
// BAD - creates new reference every render
const fetchTransactions = async (limit, offset, accountId) => { ... };

// GOOD - stable reference
const fetchTransactions = useCallback(async (limit = 100, offset = 0, accountId) => {
  // ... query logic
}, []); // Empty deps - supabase client is module-scoped
```

Without this, any component depending on `fetchTransactions` rebuilds every render, causing visible flickering.

### Critical Fix: Don't Clear Data on Tab Switch

```typescript
// BAD - causes empty-state flash
useEffect(() => {
  setLoadedTransactions([]); // Users see "No transactions" briefly
  setCurrentPage(0);
}, [accountId]);

// GOOD - keep stale data visible until fresh data arrives
useEffect(() => {
  setCurrentPage(0); // This triggers loadTransactions which replaces data
  setSelectedTransactions(new Set());
}, [accountId]);
```

### CSV Column Name Mapping for Multiple Banks

Banks export CSV with different headers. Map all known variants:

```typescript
const dateStr = String(
  row.date || row.Date || row.DATE ||
  row['Posting Date'] || row['posting_date'] ||
  row['Effective Date'] || row['effective_date'] ||
  row['Post Date'] || row['post_date'] ||
  row['Transaction Date'] || row.transaction_date || ''
);

const rawAmount = row.amount ?? row.Amount ?? row.AMOUNT ?? row.value ?? row.Value
  ?? row['Debit'] ?? row['Credit'] ?? undefined;

const description = String(row.description || row.Description || row.DESCRIPTION ||
  row.memo || row.Memo || row.MEMO ||
  row['Extended Description'] || 'Unknown transaction');
```

### Supabase Query Builder Gotcha

Supabase query builder returns new instances - conditional `.eq()` doesn't modify in place:

```typescript
// BAD - clearQuery is not modified
const clearQuery = supabase.from('personal_assets').update({...}).eq('user_id', id);
if (condition) {
  clearQuery.eq('account_type', type); // Returns new instance, clearQuery unchanged!
}
await clearQuery; // Missing the .eq filter!

// GOOD - reassign the variable
let clearQuery = supabase.from('personal_assets').update({...}).eq('user_id', id);
if (condition) {
  clearQuery = clearQuery.eq('account_type', type);
}
await clearQuery;
```

---

## Database Migrations

### Migration 1: Link transactions to accounts
```sql
ALTER TABLE transactions ADD COLUMN account_id UUID REFERENCES personal_assets(id) ON DELETE SET NULL;
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_no_account ON transactions(user_id) WHERE account_id IS NULL;
```

### Migration 2: Account management fields
```sql
ALTER TABLE personal_assets ADD COLUMN display_order INTEGER DEFAULT 0;
ALTER TABLE personal_assets ADD COLUMN is_primary BOOLEAN DEFAULT false;
ALTER TABLE personal_assets ADD COLUMN is_hidden BOOLEAN DEFAULT false;

-- Backfill display_order from creation order
WITH ordered AS (
  SELECT id, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at ASC) - 1 AS new_order
  FROM personal_assets WHERE deleted_at IS NULL
)
UPDATE personal_assets SET display_order = ordered.new_order
FROM ordered WHERE personal_assets.id = ordered.id;
```

---

## Testing the Fix

1. Import CSV on specific account tab -> balance auto-updates in Personal Assets
2. Add/edit/delete transaction -> affected account balance recalculates
3. Open Account Manager (gear icon) -> drag accounts to reorder -> tabs reflect new order
4. Toggle visibility -> account disappears from tabs, reappears when toggled
5. Set primary -> star badge appears on tab and in assets list
6. Switch tabs rapidly -> no flickering or empty-state flash

---

## Prevention

- Always `useCallback` for functions returned from custom hooks
- Always use `@hello-pangea/dnd` instead of `react-beautiful-dnd` for React 18+
- Always use `let` + reassignment with Supabase conditional query building
- Always map multiple CSV column name variants for bank imports
- Never clear displayed data before new data is ready (stale > empty)

## Common Mistakes to Avoid

- ❌ Using `react-beautiful-dnd` with React 18 StrictMode
- ❌ Unmemoized functions in hooks causing cascading re-renders
- ❌ Clearing state on tab switch (causes empty-state flash)
- ❌ Assuming Supabase query builder mutates in place
- ❌ Hardcoding CSV column names for one bank format
- ❌ Coupling hooks directly instead of using callback props

---

## Files Involved

| File | Purpose |
|------|---------|
| `src/hooks/usePersonalAssets.ts` | recalculateBalance, setPrimary, reorderAssets, toggleVisibility |
| `src/hooks/useTransactions.tsx` | fetchTransactions with useCallback, account filtering |
| `src/components/Transactions/AccountTabs.tsx` | Dynamic tab bar with visibility/primary |
| `src/components/Transactions/AccountManager.tsx` | DnD reorder + visibility + primary UI |
| `src/components/Transactions/TransactionsTabContent.tsx` | Wiring layer for balance callbacks |
| `src/components/Transactions/TransactionImport.tsx` | CSV import with multi-bank column mapping |

## Time to Implement

**Full feature set**: ~3 hours (migrations + hooks + 3 new components + wiring)

## Difficulty Level

⭐⭐⭐⭐ (4/5) - Multiple interconnected concerns, React performance pitfalls, library compatibility issues

---

**Author Notes:**
The hardest part was the flickering bug - tracing through useCallback dependency chains to find the unstable reference took investigation across 3 files. The react-beautiful-dnd incompatibility with React 18 was also non-obvious until you see the "Unable to find draggable" console error. @hello-pangea/dnd is a perfect drop-in replacement.
