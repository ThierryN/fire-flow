# Recurring Donation Amount Update - Separating Historical from Recurring

## The Problem

When a user updates their recurring donation amount (e.g., from $1.00 to $2.55), the system was overwriting the historical `amount_cents` column. This made it appear that the original $1.00 donation was $2.55, corrupting receipts, admin views, and tax records.

### Error/Symptom
```
User changes recurring donation from $1.00 to $2.55
Expected: History shows $1.00 charged, recurring shows $2.55 commitment
Actual:   History shows $2.55, receipts show $2.55, even though only $1.00 was ever charged
```

### Why It Was Hard

- The initial implementation seemed correct - "update the amount in the database"
- The corruption is invisible until someone checks receipts or admin donation history
- Stripe dashboard shows the correct information, so the bug only affects the LMS UI
- Financial data corruption has legal/tax implications

### Impact

- Receipts showed wrong amounts (potential tax/legal issue)
- Admin donation history showed inflated amounts
- Trust issue: users see amounts they never actually gave

---

## The Solution

### Root Cause

Single column (`amount_cents`) was being used for two different purposes:
1. **Historical charge**: What was actually charged at the time of payment (immutable)
2. **Recurring commitment**: What the user wants to be charged going forward (mutable)

### Architecture Fix

Add a separate column `recurring_amount_cents` for the mutable commitment:

```sql
-- Migration: Add recurring_amount_cents column
ALTER TABLE donations ADD COLUMN IF NOT EXISTS recurring_amount_cents INTEGER;

-- Backfill: set recurring_amount_cents = amount_cents for existing recurring donations
UPDATE donations
SET recurring_amount_cents = amount_cents
WHERE donation_type != 'one_time'
  AND recurring_amount_cents IS NULL;
```

### Column Semantics

| Column | Meaning | Mutability |
|--------|---------|-----------|
| `amount_cents` | What was actually charged (historical record) | IMMUTABLE after payment |
| `recurring_amount_cents` | Current recurring commitment going forward | MUTABLE (updated when user changes amount) |

### Controller Fix

```javascript
// BAD - Updates historical charge
await sql`UPDATE donations SET amount_cents = ${newAmountCents} WHERE id = ${donationId}`;

// GOOD - Updates only the recurring commitment
await sql`UPDATE donations SET recurring_amount_cents = ${newAmountCents} WHERE id = ${donationId}`;
```

### Frontend Display Fix

```javascript
// Active Recurring section - show current commitment
{formatCurrency(donation.recurring_amount || donation.amount)}

// Donation History / Receipts - show historical charge (never recurring_amount)
{formatCurrency(donation.amount)}
```

### Stripe Integration

The Stripe subscription update uses `proration_behavior: 'none'` so the new amount only takes effect at the next billing cycle:

```javascript
// Create new price with updated amount
const newPrice = await stripe.prices.create({
  currency,
  unit_amount: newAmountCents,
  recurring: {
    interval: currentPrice.recurring.interval,
    interval_count: currentPrice.recurring.interval_count,
  },
  product: currentPrice.product,
});

// Swap subscription to new price, no proration
await stripe.subscriptions.update(subscriptionId, {
  items: [{ id: item.id, price: newPrice.id }],
  proration_behavior: 'none',
});
```

---

## Data Recovery

If historical amounts were already corrupted, you need to restore them. Check Stripe for the actual charge amounts:

```sql
-- Example: Restore original charge amount for a specific subscription
UPDATE donations
SET amount_cents = 100  -- $1.00 (the actual charge)
WHERE stripe_subscription_id = 'sub_xxx'
  AND amount_cents = 255;  -- was incorrectly set to $2.55
```

---

## Testing the Fix

1. Create a recurring donation for $5.00
2. Update amount to $10.00
3. Verify:
   - `amount_cents` still shows 500 (original $5.00)
   - `recurring_amount_cents` shows 1000 (new $10.00)
   - Donation history shows "$5.00"
   - Active recurring section shows "$10.00"
   - Receipts show "$5.00"
   - Stripe dashboard shows $10.00/period

---

## Prevention

### Design Principle: Immutable Financial Records

**NEVER update a financial record after it represents a completed transaction.**

When you need to track "current" vs "historical" values:
1. Add a separate column for the mutable value
2. Keep the original column immutable
3. Display the correct one based on context (history vs active status)

### Columns to NEVER Update After Payment:
- `amount_cents` - The actual charge amount
- `currency` - The currency of the charge
- `payment_intent_id` - Stripe's record of the transaction
- `donated_at` - When the original donation was made

### Columns That CAN Be Updated:
- `recurring_amount_cents` - Current commitment
- `status` - Active/cancelled/etc.
- `updated_at` - Last modification timestamp

---

## Related Patterns

- Stripe subscription updates: Create new Price, swap subscription item
- `proration_behavior: 'none'` for next-cycle-only changes
- Receipt generation should always use `amount_cents` (historical)

---

## Common Mistakes to Avoid

- Don't use `amount_cents` for both historical and current recurring amounts
- Don't update financial records after they represent completed transactions
- Don't assume Stripe proration is desirable - donors expect changes at next cycle
- Don't forget to backfill `recurring_amount_cents` for existing recurring donations

---

## Resources

- Stripe Docs: [Update a subscription](https://stripe.com/docs/billing/subscriptions/upgrade-downgrade)
- Stripe Docs: [Proration behavior](https://stripe.com/docs/billing/subscriptions/prorations)

## Time to Implement

**30 minutes** - Migration + controller fix + frontend display fix

## Difficulty Level

Stars: 3/5 - The fix is straightforward, but the bug is subtle and has financial implications

---

**Author Notes:**
This was caught by the project owner who noticed his receipt showed $2.55 instead of the $1.00 he actually gave. The Stripe dashboard correctly showed only $1.00 was charged, which confirmed the bug was in our database/UI layer. The key lesson: financial records are sacred - always use separate columns for "what happened" vs "what's planned."
