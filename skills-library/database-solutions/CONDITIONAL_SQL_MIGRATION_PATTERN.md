# Conditional SQL Migration Pattern - Idempotent Database Migrations

## The Problem

Running migrations multiple times causes errors or duplicates. Need migrations that can run safely whether or not the changes already exist.

### Error Messages
```
ERROR: relation "table_name" already exists
ERROR: column "column_name" of relation "table_name" already exists
ERROR: duplicate key value violates unique constraint
```

---

## The Solution

### Pattern 1: CREATE TABLE IF NOT EXISTS

```sql
CREATE TABLE IF NOT EXISTS time_slots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Pattern 2: ADD COLUMN IF NOT EXISTS

```sql
ALTER TABLE time_slots
ADD COLUMN IF NOT EXISTS default_duration_minutes INTEGER DEFAULT 60;
```

### Pattern 3: INSERT Only If Empty (Seed Data)

```sql
INSERT INTO time_slots (code, display_name, typical_time, display_order)
SELECT code, display_name, typical_time, display_order
FROM (VALUES
    ('morning', 'Morning Intimacy', '10:00 AM EST', 1),
    ('noon', 'Noon Day', '1:00 PM - 4:00 PM', 2),
    ('evening', 'Evening Incense', '7:30 PM EST', 3)
) AS v(code, display_name, typical_time, display_order)
WHERE NOT EXISTS (SELECT 1 FROM time_slots LIMIT 1);
```

### Pattern 4: UPSERT (Insert or Update)

```sql
INSERT INTO time_slots (code, display_name)
VALUES ('morning', 'Morning Intimacy')
ON CONFLICT (code) DO UPDATE SET display_name = EXCLUDED.display_name;
```

### Pattern 5: Conditional UPDATE

```sql
-- Only update if value is still the default
UPDATE time_slots
SET default_duration_minutes = 90
WHERE code = 'morning' AND default_duration_minutes = 60;
```

### Pattern 6: DROP IF EXISTS

```sql
DROP TABLE IF EXISTS old_table;
DROP INDEX IF EXISTS old_index;
ALTER TABLE my_table DROP COLUMN IF EXISTS old_column;
```

---

## Complete Migration Example

```sql
-- Migration: 075b_seed_time_slots.sql
-- Idempotent: Safe to run multiple times

-- 1. Ensure table exists
CREATE TABLE IF NOT EXISTS time_slots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- 2. Seed only if empty
INSERT INTO time_slots (code, display_name, display_order)
SELECT * FROM (VALUES
    ('morning', 'Morning', 1),
    ('evening', 'Evening', 2)
) AS v(code, display_name, display_order)
WHERE NOT EXISTS (SELECT 1 FROM time_slots LIMIT 1);

-- 3. Verify
SELECT COUNT(*) as count FROM time_slots;
```

---

## Key Rules

1. Always use `IF NOT EXISTS` / `IF EXISTS` clauses
2. Use `ON CONFLICT` for upserts instead of checking first
3. For seed data, check if table is empty before inserting
4. Add comments explaining the migration purpose

## Difficulty Level
⭐⭐ (2/5)

---

**Author Notes:**
Idempotent migrations save hours of debugging. If a migration can run twice without error, deployment becomes much safer.
