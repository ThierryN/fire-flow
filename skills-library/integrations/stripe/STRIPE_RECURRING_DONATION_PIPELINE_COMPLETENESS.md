# Stripe Recurring Donation Pipeline Completeness - Solution & Implementation

## The Problem

After implementing Stripe recurring donations (subscriptions), the donation pipeline had **5 silent bugs** that only manifested in production:

1. **Wrong status**: All recurring donations saved as `'pending'` even when Stripe already charged the card successfully
2. **Wrong type**: All recurring donations saved as `'monthly'` regardless of actual interval (weekly, biweekly, yearly)
3. **No receipt**: Recurring donations never generated or sent tax receipts (one-time donations did)
4. **Admin invisible**: Recurring donations without receipts didn't appear in admin receipt management page
5. **Missing ENUM values**: Database only had `one_time` and `monthly` — no `weekly`, `biweekly`, `yearly`

### Why It Was Hard

- Each bug was **silent** — no errors thrown, no crashes. Data just wrong.
- The `'pending'` status looked plausible ("maybe Stripe hasn't confirmed yet?") but was actually hardcoded.
- Receipt generation worked perfectly for one-time donations, so nobody noticed it was missing for recurring.
- The admin receipts page `WHERE receipt_issued = TRUE` filter silently excluded donations without receipts — the page loaded fine, just showed fewer results.
- PostgreSQL ENUM types require explicit `ALTER TYPE ... ADD VALUE` migrations — you can't just insert a new value.

### Impact

- Donors charged but shown as "pending" in admin dashboard (confusing for admin)
- Guest donors received no tax-deductible receipt for recurring donations (legal/compliance issue)
- Admin couldn't manually generate receipts for recurring donations (they didn't appear in the list)
- All recurring donations labeled "Monthly" even if bi-weekly or yearly

---

## The Solution

### Bug 1: Hardcoded `'pending'` Status

**Root Cause:** `createRecurringDonation()` always inserted `'pending'` without checking Stripe's actual subscription status.

**Before (broken):**
```javascript
// Line in INSERT statement
VALUES (..., 'pending', ...)
```

**After (fixed):**
```javascript
// Check Stripe subscription status
const subStatus = subscriptionData.subscription.status;
const donationStatus = (subStatus === 'active' || subStatus === 'trialing') ? 'completed' : 'pending';

// Use in INSERT
VALUES (..., '${donationStatus}', ...)
```

**Key insight:** When Stripe creates a subscription and charges immediately (no trial), `subscription.status` returns `'active'`. Map this to your app's `'completed'` status.

### Bug 2: Hardcoded `'monthly'` Donation Type

**Root Cause:** `createRecurringDonation()` always inserted `'monthly'` regardless of the `interval` and `interval_count` parameters.

**After (fixed):**
```javascript
const intervalToDonationType = {
  week: interval_count == 2 ? 'biweekly' : 'weekly',
  month: 'monthly',
  year: 'yearly'
};
const donationType = intervalToDonationType[interval] || 'monthly';
```

**Key insight:** Stripe uses `interval` (`week`/`month`/`year`) + `interval_count` to define frequency. `week` with `interval_count: 2` = biweekly.

### Bug 3: Missing Receipt Generation

**Root Cause:** `saveDonation()` (one-time) called `ReceiptEmailService.generateAndSendReceipt()` but `createRecurringDonation()` never did.

**Fix — add after donation INSERT:**
```javascript
// Generate and send receipt for recurring donation (don't block the response)
const receiptType = interval === 'year' ? 'yearly' : 'monthly';
try {
  await ReceiptEmailService.generateAndSendReceipt(donation[0].id, receiptType);
  console.log(`Receipt sent for recurring donation ${donation[0].id} (type: ${receiptType})`);
} catch (receiptError) {
  console.error(`Receipt generation failed for recurring donation ${donation[0].id}:`, receiptError);
  // Don't fail the donation - receipt can be retried through admin interface
}
```

**Key insight:** Always wrap receipt generation in try/catch so a receipt failure doesn't block the donation response. The admin can retry manually later.

### Bug 4: Admin Receipts Query Too Restrictive

**Root Cause:** The admin receipts endpoint filtered `WHERE d.receipt_issued = TRUE`, which excluded all donations that hadn't received a receipt yet — making it impossible to discover and manually generate missing receipts.

**Before:**
```sql
WHERE d.receipt_issued = TRUE
```

**After:**
```sql
WHERE (d.receipt_issued = TRUE OR d.status = 'completed')
```

Also updated the status filter mapping:
```javascript
// 'sent' = has receipt
if (status === 'sent') query += ` AND d.receipt_issued = TRUE`;
// 'pending' = completed donation WITHOUT receipt (needs one)
if (status === 'pending') query += ` AND d.receipt_issued = FALSE AND d.status = 'completed'`;
```

**Key insight:** The admin receipt page should show ALL completed donations, with visual distinction between those with receipts and those without.

### Bug 5: Missing PostgreSQL ENUM Values

**Root Cause:** The `donation_type_enum` only had `one_time` and `monthly`. Inserting `'biweekly'` caused: `invalid input value for enum donation_type_enum: "biweekly"`.

**Migration:**
```sql
ALTER TYPE donation_type_enum ADD VALUE IF NOT EXISTS 'weekly';
ALTER TYPE donation_type_enum ADD VALUE IF NOT EXISTS 'biweekly';
ALTER TYPE donation_type_enum ADD VALUE IF NOT EXISTS 'yearly';
```

**Key insight:** PostgreSQL ENUM `ADD VALUE` cannot run inside a transaction. Run these statements outside `BEGIN/COMMIT` blocks, or use `IF NOT EXISTS` for idempotency.

---

## The Checklist: Recurring Donation Pipeline Audit

Use this checklist when implementing or auditing a Stripe recurring donation system:

### Data Integrity
- [ ] Donation status reflects Stripe subscription status (not hardcoded)
- [ ] Donation type maps from Stripe interval + interval_count (not hardcoded)
- [ ] Database ENUM/type has all frequency values (weekly, biweekly, monthly, yearly)
- [ ] `interval_count` stored in metadata for bi-weekly detection

### Receipt Pipeline
- [ ] Receipt auto-generated after recurring donation creation
- [ ] Receipt type mapped correctly (monthly vs yearly)
- [ ] Receipt generation wrapped in try/catch (non-blocking)
- [ ] Admin can see donations WITHOUT receipts for manual generation

### Admin UI
- [ ] Type badge/label handles all frequency values
- [ ] Type filter dropdown includes all frequency values
- [ ] Status display reflects actual Stripe status
- [ ] Recurring details section shows for ALL non-one-time types (not just `=== 'monthly'`)

### Frontend
- [ ] Success page displays correct donation type from URL params
- [ ] Recurring info box shows correct frequency description
- [ ] Statistics/charts handle all donation types with distinct colors

---

## Testing the Fix

### Verify Database State
```sql
-- Check that the donation has correct type and status
SELECT id, donor_name, amount_cents, donation_type, status, receipt_issued
FROM donations
WHERE stripe_subscription_id IS NOT NULL
ORDER BY created_at DESC;
```

### Verify Admin Receipts
```sql
-- Should return completed donations WITHOUT receipts
SELECT id, donor_name, amount_cents, receipt_issued, status
FROM donations
WHERE status = 'completed' AND receipt_issued = FALSE;
```

### Verify ENUM Values
```sql
SELECT unnest(enum_range(NULL::donation_type_enum));
-- Should show: one_time, monthly, weekly, biweekly, yearly
```

---

## Prevention

1. **Never hardcode status or type** in INSERT statements — always derive from Stripe response
2. **Copy the receipt generation pattern** from one-time to recurring when adding new donation flows
3. **Audit admin queries** — `WHERE x = TRUE` filters can silently hide data that needs attention
4. **Add ENUM values BEFORE writing code** that uses them — migration first, code second
5. **Use a checklist** (above) when adding new recurring intervals or donation types
6. **Test the full pipeline** end-to-end: create donation → check DB → verify receipt email → check admin page

---

## Related Patterns

- [Stripe Donations Complete Implementation](./STRIPE_DONATIONS_COMPLETE_IMPLEMENTATION.md)
- [Stripe Elements Fix](./STRIPE_ELEMENTS_FIX.md)
- [GTA 501c3 Donation Receipt Requirements](../../ecommerce/GTA_501C3_DONATION_RECEIPT_REQUIREMENTS.md)
- [Donation Receipt Implementation Guide](../../ecommerce/DONATION_RECEIPT_IMPLEMENTATION_GUIDE.md)
- [ES Module Import Hoisting (PayPal lazy-load fix)](../../patterns-standards/ES_MODULE_IMPORT_HOISTING_DOTENV.md)

---

## Common Mistakes to Avoid

- **Hardcoding `'pending'`** — Stripe charges immediately for most subscriptions; check `subscription.status`
- **Hardcoding `'monthly'`** — Map from `interval` + `interval_count` dynamically
- **Forgetting receipt generation** — Every payment flow needs its own receipt call
- **`WHERE receipt_issued = TRUE`** — This hides the exact records that need admin attention
- **Adding ENUM values inside transactions** — PostgreSQL won't allow it; run outside `BEGIN/COMMIT`
- **Checking `=== 'monthly'`** for "is recurring" — Use `!== 'one_time'` to catch all recurring types
- **Stripe `billing_cycle_anchor`** — Don't use with `week` intervals; Stripe rejects it. Only works with `month`/`year`

---

## Stripe-Specific Gotchas

### billing_cycle_anchor
```javascript
// DON'T use billing_cycle_anchor for weekly/bi-weekly plans
// Stripe error: "billing_cycle_anchor is not supported for plans with interval 'week'"
if (interval === 'month' || interval === 'year') {
  subscriptionParams.billing_cycle_anchor = anchorTimestamp;
}
```

### paymentMethodCreation
```javascript
// REQUIRED for Stripe Elements with SetupIntent flow
const elements = stripe.elements({
  clientSecret,
  appearance,
  paymentMethodCreation: 'manual'  // Without this, confirmSetup fails
});
```

### Apple Pay + Setup Mode
```javascript
// Apple Pay ONLY works with payment mode, NOT setup mode
// For recurring donations, use payment mode with setup_future_usage
// instead of setup mode with SetupIntent
```

---

## Resources

- [Stripe Subscriptions API](https://docs.stripe.com/api/subscriptions)
- [Stripe Billing Portal](https://docs.stripe.com/customer-management/integrate-customer-portal)
- [PostgreSQL ALTER TYPE](https://www.postgresql.org/docs/current/sql-altertype.html)

## Time to Implement

- **Finding all 5 bugs:** ~3 hours (spread across debugging sessions)
- **Fixing all 5 bugs:** ~45 minutes (once root causes identified)
- **Total with testing/deploy:** ~4.5 hours

## Difficulty Level

⭐⭐⭐⭐ (4/5) — Each bug individually is simple, but finding them all requires systematic auditing of the entire pipeline. Silent data bugs are the hardest to catch.

---

**Author Notes:**
The hardest part was that none of these bugs threw errors. The system "worked" — donations went through, Stripe charged cards, money arrived. But the internal state was wrong everywhere. The lesson: after implementing any payment flow, audit the ENTIRE pipeline from Stripe response → DB insert → receipt generation → admin visibility → frontend display. Every step is a potential silent failure point.

**Session:** February 13-14, 2026
**Commits:** `0b564e5`, `7533fb9`
**Deployed:** schooloftheprophets.club (v1.0.4)
