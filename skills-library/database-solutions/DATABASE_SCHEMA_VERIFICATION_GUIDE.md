# Database Schema Verification Guide - Critical Debugging Lesson

## 📋 Overview

**Issue**: Admin donations detail endpoint returned 500 error: `column p.first_name does not exist`

**Root Cause**: Assumed profiles table structure without verifying actual schema

**Resolution**: Always verify database schema before writing queries

**Session**: 2025-11-23 (Admin Donations Fix)

---

## ⚠️ Critical Lesson

### The Mistake We Made

```javascript
// ❌ WRONG: Assumed schema without verification
const donations = await sql`
  SELECT
    p.first_name as user_first_name,  // ❌ Column doesn't exist!
    p.last_name as user_last_name     // ❌ Column doesn't exist!
  FROM donations d
  LEFT JOIN profiles p ON d.user_id = p.id
  WHERE d.id = ${id}
`;
```

**Why this was wrong:**
1. Made assumption about column names based on common patterns
2. Didn't verify the profiles table structure before writing code
3. Looked at guest_donor_profiles (which HAS first_name/last_name) and assumed profiles had the same
4. Took 3 iterations to fix because I didn't verify first

### The Correct Approach

```sql
-- ✅ ALWAYS do this FGTAT before writing queries
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'profiles'
ORDER BY ordinal_position;
```

**Actual profiles table columns:**
- `id` (UUID)
- `name` (TEXT) ← Single field for full name
- `email` (TEXT)
- `avatar_url` (TEXT)
- `bio` (TEXT)
- `role` (TEXT)
- `email_verified` (BOOLEAN)
- `location` (TEXT)
- `password` (TEXT)
- `last_login_at` (TIMESTAMPTZ)
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)

---

## 🔍 Schema Verification Checklist

Before writing ANY database query, verify:

### 1. Table Exists
```sql
-- Check if table exists
SELECT EXISTS (
  SELECT FROM information_schema.tables
  WHERE table_schema = 'public' AND table_name = 'your_table_name'
);
```

### 2. Columns Exist
```sql
-- List all columns in table
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'your_table_name'
ORDER BY ordinal_position;
```

### 3. Foreign Keys Correct
```sql
-- Check foreign key relationships
SELECT constraint_name, table_name, column_name
FROM information_schema.key_column_usage
WHERE table_name = 'your_table_name' AND column_name LIKE '%_id';
```

### 4. Verify Data Types
```sql
-- Ensure columns have expected data types
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'your_table_name';
```

---

## 🛠️ Key Tables in This Project

### profiles Table
```
Column Name              | Data Type | Nullable | Default
id                      | UUID      | NO       | gen_random_uuid()
name                    | TEXT      | NO       | -
email                   | TEXT      | NO UNIQUE| -
avatar_url              | TEXT      | YES      | -
bio                     | TEXT      | YES      | -
role                    | TEXT      | YES      | 'user'
email_verified          | BOOLEAN   | YES      | false
location                | TEXT      | YES      | -
password                | TEXT      | YES      | -
last_login_at           | TIMESTAMPTZ | YES    | -
created_at              | TIMESTAMPTZ | YES    | now()
updated_at              | TIMESTAMPTZ | YES    | now()
```

**Important**: NO `first_name` or `last_name` columns. Use `name` field instead.

### guest_donor_profiles Table (Migration 051)
```
Column Name              | Data Type | Nullable | Default
id                      | UUID      | NO       | gen_random_uuid()
email                   | TEXT      | NO UNIQUE| -
phone_number            | TEXT      | YES      | -
first_name              | TEXT      | YES      | -
last_name               | TEXT      | YES      | -
total_donations_count   | INTEGER   | YES      | 0
total_donated_cents     | BIGINT    | YES      | 0
first_donation_at       | TIMESTAMPTZ | YES    | -
last_donation_at        | TIMESTAMPTZ | YES    | -
receive_receipts        | BOOLEAN   | YES      | true
receive_updates         | BOOLEAN   | YES      | true
language                | CHAR(2)   | YES      | 'en'
tags                    | JSONB     | YES      | '[]'::jsonb
notes                   | TEXT      | YES      | -
created_at              | TIMESTAMPTZ | NO     | NOW()
updated_at              | TIMESTAMPTZ | NO     | NOW()
```

**Important**: This table HAS separate `first_name` and `last_name` columns.

### donations Table
```
Column Name              | Data Type | Nullable | Default
id                      | UUID      | NO       | gen_random_uuid()
user_id                 | UUID      | YES      | - (FK → profiles)
guest_donor_id          | UUID      | YES      | - (FK → guest_donor_profiles)
donor_name              | TEXT      | YES      | -
donor_email             | TEXT      | YES      | -
amount_cents            | BIGINT    | NO       | -
currency                | CHAR(3)   | NO       | 'USD'
donation_type           | ENUM      | NO       | 'one_time'
stripe_payment_intent_id| TEXT      | YES      | -
stripe_charge_id        | TEXT      | YES      | -
stripe_customer_id      | TEXT      | YES      | -
stripe_subscription_id  | TEXT      | YES      | -
paypal_order_id         | TEXT      | YES      | -
paypal_subscription_id  | TEXT      | YES      | -
status                  | ENUM      | NO       | 'pending'
payment_method          | ENUM      | YES      | -
message                 | TEXT      | YES      | -
anonymous               | BOOLEAN   | NO       | false
created_at              | TIMESTAMPTZ | NO     | now()
updated_at              | TIMESTAMPTZ | NO     | now()
metadata                | JSONB     | NO       | '{}'::jsonb
recurring_day_of_month  | INTEGER   | YES      | -
```

---

## 🚫 Common Mistakes to Avoid

### Mistake 1: Assuming Column Names
```javascript
// ❌ DON'T assume column names without verification
SELECT p.first_name, p.last_name FROM profiles p

// ✅ DO verify first
// Check information_schema.columns to see actual column names
// Then use: SELECT p.name FROM profiles p
```

### Mistake 2: Using SELECT *
```javascript
// ❌ Can cause issues with schema changes
SELECT d.* FROM donations d

// ✅ Explicitly list needed columns
SELECT d.id, d.amount_cents, d.status FROM donations d
```

### Mistake 3: Incorrect Foreign Key Joins
```javascript
// ❌ If FK relationship is wrong, query will return NULL
SELECT * FROM donations d
LEFT JOIN profiles p ON d.user_id = p.id  // Verify this relationship exists!

// ✅ Check FK constraints first
SELECT constraint_name FROM information_schema.table_constraints
WHERE table_name = 'donations' AND constraint_type = 'FOREIGN KEY';
```

### Mistake 4: Incorrect Data Types
```javascript
// ❌ May not work if data type is different
WHERE amount_cents = '1000'  // If BIGINT, needs numeric not string

// ✅ Match the actual data type
WHERE amount_cents = 1000  // BIGINT - numeric value
```

---

## ✅ Best Practices

### 1. Always Create Schema Verification Script

Before working with a table:

```bash
#!/bin/bash
# Verify table schema before writing queries

SCHEMA_CHECK=$(
  psql -h your-host -U your-user -d your-db -c "
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'profiles'
    ORDER BY ordinal_position;
  "
)

echo "Profiles table schema:"
echo "$SCHEMA_CHECK"
```

### 2. Document Table Structures

Keep this guide updated with actual schema:
- Run verification queries regularly
- Update when migrations are applied
- Share with team

### 3. Add Comments in Code

```javascript
// ✅ Document which columns you're using and why
const result = await sql`
  SELECT
    d.id,
    d.amount_cents,        // Amount in cents (BIGINT)
    p.email,               // User email (TEXT) - profiles table
    p.name,                // User full name (TEXT, not separate first/last)
    g.first_name,          // Guest first name (guest_donor_profiles)
    g.last_name            // Guest last name (guest_donor_profiles)
  FROM donations d
  LEFT JOIN profiles p ON d.user_id = p.id
  LEFT JOIN guest_donor_profiles g ON d.guest_donor_id = g.id
`;
```

### 4. Test Query Before Integration

```sql
-- Test in SQL editor FGTAT before putting in code
SELECT p.name, g.first_name, g.last_name
FROM donations d
LEFT JOIN profiles p ON d.user_id = p.id
LEFT JOIN guest_donor_profiles g ON d.guest_donor_id = g.id
LIMIT 1;
```

---

## 📊 Debugging Process (What We Did)

1. ❌ **Initial assumption**: profiles has first_name/last_name
2. ✅ **Created fix**: Explicit column selection
3. ❌ **Tested**: Still 500 error
4. ❌ **Restart**: Didn't help
5. ✅ **Get error**: Got actual error message: "column p.first_name does not exist"
6. ✅ **Verify schema**: Checked information_schema
7. ✅ **Found mismatch**: profiles uses "name" not "first_name"/"last_name"
8. ✅ **Fixed**: Updated column names
9. ✅ **Tested**: Works!

**Key insight**: Steps 1-4 wasted time. Step 5 (actual error) should have been step 1.

---

## 🎯 Action Items for Future Sessions

When working on database queries:

- [ ] Run schema verification query BEFORE writing code
- [ ] Document which table each column comes from
- [ ] Test query in SQL editor first
- [ ] Add comments explaining column names
- [ ] Verify foreign key relationships exist
- [ ] Check data types match query expectations
- [ ] Never assume schema without verification
- [ ] Get actual error messages if issues occur

---

## 📞 When to Ask for Help

If you see this error:
```
PostgresError: column [table].[column] does not exist
```

**Immediately run:**
```sql
SELECT column_name FROM information_schema.columns
WHERE table_name = '[table_name]';
```

Then share the actual column names so we can fix the query.

---

## Related Files

- `server/controllers/adminController.js` - getDonation function (FIXED)
- `server/migrations/051_guest_donor_tracking_system.sql` - guest_donor_profiles table
- `ADMIN_DONATIONS_FIX.md` - Detailed fix documentation
- `ADMIN_DONATIONS_FIX_DIAGNOSTIC.md` - Troubleshooting guide

---

## Session Reference

- **Date**: 2025-11-23
- **Issue**: Admin donations 500 error
- **Root Cause**: Column name assumption
- **Fix**: Used correct 'name' column instead of 'first_name'/'last_name'
- **Commits**: 503e952

---

**Remember**: Always verify the schema. Assumptions cause bugs. 🐛

