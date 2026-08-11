# 🚨 SCHEMA VERIFICATION - QUICK REFERENCE

## ONE MISTAKE THAT COST US 3 ITERATIONS

**Problem**: Assumed `profiles` table had `first_name` and `last_name` columns
**Reality**: It only has a single `name` column
**Error**: `column p.first_name does not exist`
**Fix**: Changed to use `p.name` instead

---

## ⚡ BEFORE WRITING ANY DATABASE QUERY

### Step 1: Run This Command (2 seconds)
```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'YOUR_TABLE_NAME'
ORDER BY ordinal_position;
```

### Step 2: Copy Output (5 seconds)
See actual column names and types

### Step 3: THEN Write Code (with accurate names)

---

## 🔴 CRITICAL COLUMN NAMES IN THIS PROJECT

| Table | Column Name | ⚠️ WRONG | ✅ RIGHT |
|-------|-------------|----------|----------|
| `profiles` | user name | `first_name`, `last_name` | `name` |
| `profiles` | avatar | `profile_picture` | `avatar_url` |
| `guest_donor_profiles` | first name | ❌ N/A | `first_name` ✅ |
| `guest_donor_profiles` | last name | ❌ N/A | `last_name` ✅ |

---

## 🛑 MISTAKES TO AVOID

```javascript
// ❌ NEVER DO THIS
SELECT p.first_name FROM profiles p     // Column doesn't exist!
SELECT * FROM donations d               // Might fail on schema changes

// ✅ DO THIS INSTEAD
SELECT p.name FROM profiles p           // Correct column name
SELECT d.id, d.amount_cents FROM donations d  // Explicit columns
```

---

## 🔍 IF YOU GET "column X does not exist" ERROR

**Immediate steps:**
1. Run schema verification query above
2. Check actual column name
3. Fix the query
4. Move on

**Don't waste time guessing!**

---

## 📍 WHERE TO FIND THIS

- `.claude/skills/DATABASE_SCHEMA_VERIFICATION_GUIDE.md` - Full guide
- `.claude/skills/WARRIOR_WORKFLOW_DEBUGGING_PROTOCOL.md` - Workflow update
- `ADMIN_DONATIONS_FIX.md` - Original fix documentation

---

## ✅ CHECKBOX FOR EVERY QUERY

- [ ] Verified table exists
- [ ] Listed actual columns
- [ ] Tested query in SQL editor first
- [ ] Used correct column names
- [ ] Added comments showing table sources
- [ ] Handled NULL values properly

---

## 💾 Related Files

- `server/controllers/adminController.js` - Fixed getDonation function
- `server/migrations/051_guest_donor_tracking_system.sql` - Schema definitions

---

## ⏱️ Time Impact

**Without verification**: 3 iterations × 10 minutes = 30 minutes wasted
**With verification**: 1 iteration × 2 minutes = 2 minutes total

**Save 28 minutes by verifying schema first!** ⚡

---

**Session**: 2025-11-23
**Lesson**: Schema verification is NOT optional
**Motto**: Verify first, code second

