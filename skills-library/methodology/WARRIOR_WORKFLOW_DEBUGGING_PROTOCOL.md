# Warrior Workflow - Debugging Protocol

## Critical Lesson: Schema Verification (2025-11-23)

**Session Issue**: Admin donations endpoint returned 500 error due to incorrect column name assumptions

**Key Takeaway**: Always verify database schema before writing queries

---

## Updated Warrior Workflow - Database Query Pattern

### Phase 1: Research (VERIFY SCHEMA FGTAT)
```bash
# ALWAYS do this first:
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'target_table'
ORDER BY ordinal_position;
```

**What to look for:**
- ✅ Exact column names (case-sensitive)
- ✅ Data types (BIGINT vs INTEGER, TEXT vs VARCHAR)
- ✅ NULL constraints
- ✅ Foreign key relationships

### Phase 2: Plan (TEST QUERY BEFORE CODING)
```sql
-- Write and test in SQL editor FGTAT
-- Don't assume column names
-- Don't use SELECT *
-- Explicitly list needed columns
```

### Phase 3: Code (DOCUMENT COLUMN SOURCES)
```javascript
// Include comments showing which table each column comes from
const result = await sql`
  SELECT
    d.id,                          // donations table
    d.amount_cents,                // donations table (BIGINT)
    p.name,                        // profiles table (not first_name!)
    g.first_name,                  // guest_donor_profiles table
    g.last_name                    // guest_donor_profiles table
  FROM donations d
  LEFT JOIN profiles p ON d.user_id = p.id
  LEFT JOIN guest_donor_profiles g ON d.guest_donor_id = g.id
`;
```

### Phase 4: Verify (GET ACTUAL ERROR IF ISSUES)
When debugging, request:
- ✅ Full error message from server console
- ✅ Error stack trace
- ✅ Database error details
- ✅ Actual column names from schema

---

## Common Database Patterns in This Project

### Pattern 1: User (Logged-In) Queries
```javascript
// ✅ Correct - use 'name' not 'first_name'/'last_name'
SELECT p.name, p.email FROM profiles p WHERE p.id = ${userId}
```

### Pattern 2: Guest Donor Queries
```javascript
// ✅ Correct - guest_donor_profiles has separate fields
SELECT g.first_name, g.last_name, g.email
FROM guest_donor_profiles g WHERE g.id = ${guestId}
```

### Pattern 3: Joins (User vs Guest)
```javascript
// ✅ Correct - verify both FKs exist before joining
SELECT
  p.name as user_name,              // profiles.name
  g.first_name as guest_first_name  // guest_donor_profiles.first_name
FROM donations d
LEFT JOIN profiles p ON d.user_id = p.id              // Check this FK
LEFT JOIN guest_donor_profiles g ON d.guest_donor_id = g.id  // Check this FK
```

### Pattern 4: NULL Handling
```javascript
// ✅ Remember: columns can be NULL
// Structure response to handle both user and guest donors
user_donor: donation.user_id ? { ... } : null,
guest_donor: donation.guest_donor_id ? { ... } : null,
```

---

## Error Pattern Recognition

### Error: "column X does not exist"
**Immediate Action:**
```sql
SELECT column_name FROM information_schema.columns
WHERE table_name = 'target_table';
```

**Root Cause**: Usually one of:
1. Wrong table name
2. Column name doesn't match (first_name vs name)
3. Column was not created in migration
4. Recent migration changed column names

**Solution**: Verify actual columns and update query

### Error: "relation X does not exist"
**Immediate Action:**
```sql
SELECT EXISTS (
  SELECT FROM information_schema.tables
  WHERE table_schema = 'public' AND table_name = 'table_name'
);
```

**Root Cause**: Usually:
1. Migration not applied
2. Table name misspelled
3. Wrong schema (not 'public')

**Solution**: Apply migration or check table name

### Error: Foreign key constraint violation
**Immediate Action:**
```sql
SELECT constraint_name, column_name
FROM information_schema.key_column_usage
WHERE table_name = 'your_table';
```

**Root Cause**: Usually:
1. FK relationship doesn't exist
2. Referenced table/column name wrong
3. Data type mismatch on FK columns

**Solution**: Verify FK relationships exist and column names match

---

## Pre-Code Checklist (ALWAYS DO THIS FGTAT)

Before writing ANY query:

- [ ] Verified table exists
- [ ] Listed all columns in table
- [ ] Confirmed column names and data types
- [ ] Checked foreign key relationships
- [ ] Tested query in SQL editor
- [ ] Documented column sources in code
- [ ] Considered NULL handling
- [ ] Verified joins are correct

---

## Documentation Requirements

Every database-related code should include:

```javascript
/**
 * Query: Get donation details
 *
 * Tables accessed:
 * - donations: id, amount_cents, status (join source)
 * - profiles: name, email (LEFT JOIN on donations.user_id)
 * - guest_donor_profiles: first_name, last_name, email (LEFT JOIN on donations.guest_donor_id)
 *
 * Important notes:
 * - profiles.name is full name (not separate first/last)
 * - guest_donor_profiles has separate first/last name fields
 * - Both joins are LEFT to support both user and guest donations
 *
 * @throws ApiError if donation not found (404)
 */
export const getDonation = asyncHandler(async (req, res, next) => {
  // ... implementation
});
```

---

## Warrior Workflow Integration

### Existing Steps (Keep These)
1. ✅ Read the code
2. ✅ Understand what's broken
3. ✅ Implement fix
4. ✅ Test solution
5. ✅ Commit with message

### New Step (Add This)
**Before Step 3 (Implement fix):**
- **VERIFY SCHEMA**: If query involves database, verify actual schema first
- Run information_schema queries
- Document findings
- THEN write code

This prevents assumption-based bugs.

---

## Real Example: The Admin Donations Fix

### ❌ What We Did Wrong (First Attempt)
```javascript
// Assumed column names without verification
SELECT p.first_name, p.last_name FROM profiles p
// Error: column p.first_name does not exist
```

### ✅ What We Should Have Done (New Protocol)
1. Check profiles table schema:
   ```sql
   SELECT column_name FROM information_schema.columns
   WHERE table_name = 'profiles';
   ```
2. See that `name` exists, not `first_name`/`last_name`
3. Write correct query:
   ```sql
   SELECT p.name FROM profiles p
   ```
4. Then code implementation

**Time saved**: 3 iterations → 1 iteration

---

## References

- `.claude/skills/DATABASE_SCHEMA_VERIFICATION_GUIDE.md` - Complete guide
- `ADMIN_DONATIONS_FIX.md` - Original fix documentation
- `server/migrations/051_guest_donor_tracking_system.sql` - Schema definitions

---

## Status

✅ **Protocol Created**: 2025-11-23
✅ **Applied To**: adminController.js getDonation function
✅ **Future Sessions**: Use this protocol for all database work

---

**Remember**: Verify schema first. Always. No assumptions. 🎯

