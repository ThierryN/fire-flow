# Course Completion Mode Migration - Implementation Guide

## 📋 Overview

Added `completion_mode` field to the `courses` table to allow instructors to choose between:
- **Automatic**: Requires 90% video watch time for completion
- **Manual**: Student must click "Mark Complete" button

## ✅ What Was Fixed

**File:** `server/migrations/010_add_course_completion_mode.sql`

**Issues in Previous Version:**
- ❌ CHECK constraint was inline with ALTER TABLE statement (PostgreSQL doesn't support this syntax)
- ❌ RAISE NOTICE was at global scope (should be inside block)

**Fixed Version:**
- ✅ CHECK constraint as separate named constraint: `chk_courses_completion_mode`
- ✅ All statements properly scoped in PL/pgSQL block
- ✅ Proper error handling with IF NOT EXISTS

## 🚀 How to Apply the Migration

### Option 1: Using pgAdmin or SQL Client
```sql
-- 1. Open your PostgreSQL client (pgAdmin, DBeaver, psql, etc.)
-- 2. Connect to your database
-- 3. Open the file: server/migrations/010_add_course_completion_mode.sql
-- 4. Run the entire script
```

### Option 2: Using Node.js Script (Recommended)
Create file: `server/run-migration.js`

```javascript
const { sql } = require('./config/database');
const fs = require('fs');
const path = require('path');

async function runMigration() {
  try {
    const migrationPath = path.join(__dirname, 'migrations', '010_add_course_completion_mode.sql');
    const migrationSQL = fs.readFileSync(migrationPath, 'utf-8');
    
    console.log('🚀 Running course completion mode migration...');
    await sql.unsafe(migrationSQL);
    console.log('✅ Migration completed successfully!');
  } catch (error) {
    console.error('❌ Migration failed:', error.message);
    process.exit(1);
  }
}

runMigration();
```

Then run: `node server/run-migration.js`

### Option 3: From Within Server Startup
Add to `server.js` or database initialization:

```javascript
const fs = require('fs');
const path = require('path');

async function initializeMigrations() {
  try {
    const migrationFile = path.join(__dirname, 'migrations', '010_add_course_completion_mode.sql');
    const migrationSQL = fs.readFileSync(migrationFile, 'utf-8');
    await sql.unsafe(migrationSQL);
    console.log('✅ Completion mode migration initialized');
  } catch (error) {
    console.warn('⚠️ Migration error (may already exist):', error.message);
  }
}

// Call during server startup
initializeMigrations();
```

## 🔍 Verification Steps

### Quick Verification (Recommended)
Run the quick test from `VERIFY_COMPLETION_MODE.sql`:

```sql
-- This will output all checks
DO $$
DECLARE
  v_column_exists BOOLEAN;
  v_constraint_exists BOOLEAN;
  v_index_exists BOOLEAN;
BEGIN
  SELECT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'courses'
      AND column_name = 'completion_mode'
  ) INTO v_column_exists;

  SELECT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE table_schema = 'public'
      AND table_name = 'courses'
      AND constraint_name = 'chk_courses_completion_mode'
  ) INTO v_constraint_exists;

  SELECT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname = 'public'
      AND tablename = 'courses'
      AND indexname = 'idx_courses_completion_mode'
  ) INTO v_index_exists;

  RAISE NOTICE '=== COURSE COMPLETION MODE MIGRATION VERIFICATION ===';
  RAISE NOTICE 'Column exists: %', CASE WHEN v_column_exists THEN '✅ YES' ELSE '❌ NO' END;
  RAISE NOTICE 'Constraint exists: %', CASE WHEN v_constraint_exists THEN '✅ YES' ELSE '❌ NO' END;
  RAISE NOTICE 'Index exists: %', CASE WHEN v_index_exists THEN '✅ YES' ELSE '❌ NO' END;
  RAISE NOTICE '=====================================================';
  
  IF v_column_exists AND v_constraint_exists AND v_index_exists THEN
    RAISE NOTICE '✅ ALL CHECKS PASSED - Migration is complete!';
  ELSE
    RAISE NOTICE '❌ SOME CHECKS FAILED - Check migration status';
  END IF;
END
$$ LANGUAGE plpgsql;
```

### Detailed Verification

**1. Check Column Properties:**
```sql
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'courses' 
  AND column_name = 'completion_mode';
```
Expected output:
```
column_name       | data_type | column_default     | is_nullable
completion_mode   | text      | 'automatic'::text  | NO
```

**2. Check Constraint:**
```sql
SELECT constraint_name, constraint_type, check_clause
FROM information_schema.table_constraints
WHERE table_schema = 'public' AND table_name = 'courses'
  AND constraint_name = 'chk_courses_completion_mode';
```
Expected output:
```
constraint_name              | constraint_type | check_clause
chk_courses_completion_mode  | CHECK           | (completion_mode IN ('automatic', 'manual'))
```

**3. Check Index:**
```sql
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public' AND tablename = 'courses'
  AND indexname = 'idx_courses_completion_mode';
```
Expected output:
```
schemaname | tablename | indexname                    | indexdef
public     | courses   | idx_courses_completion_mode  | CREATE INDEX idx_courses_completion_mode ON public.courses USING btree (completion_mode)
```

**4. Check Data:**
```sql
SELECT id, title, completion_mode, created_at
FROM public.courses
LIMIT 5;
```
Expected: All courses should show `completion_mode` with either 'automatic' or 'manual'

## 🧪 Test the Constraint

### Test 1: Valid Value (Should Succeed)
```sql
-- This should work fine
INSERT INTO public.courses (title, instructor_id, completion_mode)
VALUES ('Test Course', 1, 'manual')
RETURNING id, title, completion_mode;
```

### Test 2: Invalid Value (Should Fail)
```sql
-- This should fail with constraint violation
INSERT INTO public.courses (title, instructor_id, completion_mode)
VALUES ('Bad Course', 1, 'invalid_mode');
-- ERROR: new row for relation "courses" violates check constraint "chk_courses_completion_mode"
```

## 📊 Query Examples for Development

### Get All Automatic Courses
```sql
SELECT id, title, instructor_id, completion_mode
FROM public.courses
WHERE completion_mode = 'automatic';
```

### Get All Manual Courses
```sql
SELECT id, title, instructor_id, completion_mode
FROM public.courses
WHERE completion_mode = 'manual';
```

### Count by Mode
```sql
SELECT completion_mode, COUNT(*) as count
FROM public.courses
GROUP BY completion_mode
ORDER BY completion_mode;
```

### Update Course Completion Mode
```sql
UPDATE public.courses
SET completion_mode = 'manual'
WHERE id = $1
RETURNING id, title, completion_mode;
```

## 🛠️ Schema Details

### Column Definition
```sql
completion_mode TEXT DEFAULT 'automatic' NOT NULL
```

- **Type:** TEXT (allows 'automatic' or 'manual')
- **Default:** 'automatic' (new courses default to automatic tracking)
- **NOT NULL:** All courses must have a completion mode
- **Constraint:** CHECK constraint ensures only valid values

### Constraint Definition
```sql
ALTER TABLE public.courses
ADD CONSTRAINT chk_courses_completion_mode
CHECK (completion_mode IN ('automatic', 'manual'));
```

- **Name:** `chk_courses_completion_mode` (for referencing/removing if needed)
- **Type:** CHECK constraint
- **Valid values:** 'automatic' or 'manual'

### Index Definition
```sql
CREATE INDEX idx_courses_completion_mode
ON public.courses(completion_mode);
```

- **Purpose:** Speeds up queries filtering by completion_mode
- **Use cases:** Getting all automatic or manual courses, reporting

## 🔄 Rollback Instructions (If Needed)

If you need to revert this migration:

```sql
-- Drop index
DROP INDEX IF EXISTS idx_courses_completion_mode;

-- Drop constraint
ALTER TABLE public.courses
DROP CONSTRAINT IF EXISTS chk_courses_completion_mode;

-- Drop column
ALTER TABLE public.courses
DROP COLUMN IF EXISTS completion_mode;

-- Verify rollback
SELECT column_name FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'courses'
  AND column_name = 'completion_mode';
-- Should return no results
```

## 📝 Frontend Integration Points

These queries will be used in:

### Course Builder Component
```javascript
// Get completion mode for current course
const course = await api.get(`/courses/${courseId}`);
console.log(course.completion_mode); // 'automatic' or 'manual'

// Update completion mode
await api.put(`/courses/${courseId}`, {
  completion_mode: 'manual' // or 'automatic'
});
```

### Course Listing
```javascript
// Filter courses by completion mode
const automaticCourses = courses.filter(c => c.completion_mode === 'automatic');
const manualCourses = courses.filter(c => c.completion_mode === 'manual');
```

## ✨ Benefits

- **Flexibility:** Instructors can choose completion tracking method
- **Performance:** Index enables fast filtering
- **Data Integrity:** CHECK constraint prevents invalid values
- **Documentation:** Column comment explains purpose
- **Idempotency:** Migration safely handles re-runs

## 📞 Troubleshooting

**Error: "relation 'chk_courses_completion_mode' already exists"**
- Migration was already run
- This is safe - the DO block checks IF NOT EXISTS
- Run again and it will skip

**Error: "column 'completion_mode' already exists"**
- Column already in table from previous run
- This is expected - the DO block handles this
- Just verify it has correct properties

**Error: "invalid input syntax for type text"**
- An invalid value was passed (not 'automatic' or 'manual')
- The CHECK constraint is working correctly
- Use only: 'automatic' or 'manual'

## 📞 Questions?

Refer to:
- `VERIFY_COMPLETION_MODE.sql` - All verification queries
- `server/migrations/010_add_course_completion_mode.sql` - Full migration code
- Schema migration documentation in `server/migrations/README.md`

---

**Status:** ✅ Ready for implementation
**Last Updated:** 2025-10-20
