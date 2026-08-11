---
name: pg-to-mysql-schema-migration-methodology
category: database-solutions
version: 1.0.0
contributed: 2026-03-06
contributor: ministry-lms
last_updated: 2026-03-06
contributors:
  - ministry-lms
tags: [postgresql, mysql, mariadb, migration, schema, uuid, returning, xampp]
difficulty: medium
usage_count: 0
success_rate: 100
---

# PG to MySQL Schema Migration Methodology

## Problem

When porting a PostgreSQL application to MySQL, the runtime SQL translation layer (sql-compat.js) handles syntax differences. But tables and columns still need to exist in MySQL. PG migrations use PG-specific DDL (UUID, BOOLEAN, TEXT[], JSONB, TIMESTAMP WITH TIME ZONE, partial indexes) that MySQL doesn't support. The result: 500 errors at runtime when controllers reference tables or columns that were never created in MySQL.

**Symptoms:**
- 500 Internal Server Error on specific endpoints
- `Table 'db.tablename' doesn't exist` in server logs
- `Unknown column 'col' in 'field list'` errors
- RETURNING * emulation returns empty/wrong rows (Strategy 3 returns 0 for UUID tables)

## Solution Pattern

Systematic 4-step process per feature area:

### Step 1: Identify the 500

Trace the error: endpoint URL -> route file -> controller -> model/query -> table name + columns.

### Step 2: Check Table/Column Existence

```javascript
// Quick check script
import sql from './config/sql.js';
try {
  const cols = await sql.unsafe('DESCRIBE tablename');
  console.log(cols.map(c => c.Field));
} catch(e) {
  console.log('TABLE MISSING:', e.message);
}
```

### Step 3: Create MySQL Migration Script

Convert PG DDL to MySQL DDL with these type mappings:

| PostgreSQL | MySQL |
|------------|-------|
| `UUID PRIMARY KEY DEFAULT gen_random_uuid()` | `CHAR(36) PRIMARY KEY DEFAULT (UUID())` |
| `BOOLEAN DEFAULT true` | `TINYINT(1) DEFAULT 1` |
| `TIMESTAMP WITH TIME ZONE` | `DATETIME` |
| `TEXT[]` (array) | `JSON DEFAULT NULL` |
| `JSONB` | `JSON` |
| `INTEGER[]` | `JSON DEFAULT NULL` |
| `SERIAL` | `INT AUTO_INCREMENT` |
| `DECIMAL(10,2)` | `DECIMAL(10,2)` (same) |
| `VARCHAR(255)` | `VARCHAR(255)` (same) |
| `REFERENCES table(id) ON DELETE CASCADE` | Omit FK constraints (simpler with UUID tables) |
| Partial index `WHERE condition` | Regular index (MySQL doesn't support partial) |
| `CREATE TYPE ... AS ENUM` | `VARCHAR(50)` with application validation |
| `NOW()` | `CURRENT_TIMESTAMP` (in DEFAULT) or `NOW()` (in queries) |

### Step 4: Fix RETURNING * for UUID Tables

When a table uses `CHAR(36) DEFAULT (UUID())` as primary key:
- `LAST_INSERT_ID()` returns 0 (only works for AUTO_INCREMENT)
- The RETURNING emulation Strategy 1 needs `id` in the INSERT column list
- **Fix:** Generate UUID in JavaScript and include it explicitly

```javascript
import { v4 as uuidv4 } from 'uuid';

// Before (broken — RETURNING can't find the row)
const result = await sql`
  INSERT INTO courses (title, description)
  VALUES (${title}, ${desc})
  RETURNING *
`;

// After (works — Strategy 1 finds row by id)
const id = uuidv4();
const result = await sql`
  INSERT INTO courses (id, title, description)
  VALUES (${id}, ${title}, ${desc})
  RETURNING *
`;
```

## Migration Script Template

Use idempotent JS migrations with existence checks:

```javascript
/**
 * MySQL Migration: {description}
 * Run with: node --env-file=.env.local migrations/{number}_{name}.js
 */
import sql from '../config/sql.js';

async function addColumnIfMissing(table, column, definition) {
  const cols = await sql.unsafe(`DESCRIBE ${table}`);
  const colNames = cols.map(c => c.Field);
  if (!colNames.includes(column)) {
    await sql.unsafe(`ALTER TABLE ${table} ADD COLUMN ${column} ${definition}`);
    console.log(`  Added ${table}.${column}`);
    return true;
  }
  console.log(`  ${table}.${column} already exists`);
  return false;
}

async function migrate() {
  try {
    // CREATE TABLE IF NOT EXISTS for new tables
    await sql.unsafe(`
      CREATE TABLE IF NOT EXISTS tablename (
        id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
        -- columns here
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_name (column)
      )
    `);

    // ALTER TABLE for missing columns on existing tables
    await addColumnIfMissing('existing_table', 'new_col', 'VARCHAR(255) DEFAULT NULL');

    console.log('Migration complete!');
  } catch (error) {
    console.error('Migration error:', error.message);
  } finally {
    await sql.end();
  }
}

migrate();
```

## Diagnostic Cheat Sheet

| HTTP Status | Likely Cause | Check |
|-------------|-------------|-------|
| 500 on GET | Missing table or column | `DESCRIBE tablename` |
| 500 on POST | Missing column in INSERT | Compare INSERT columns vs DESCRIBE |
| 401 instead of 500 | Table exists, auth works | Fixed! |
| Empty response on POST | RETURNING emulation failed | Check if `id` is in INSERT columns |
| Wrong row returned | Strategy 4 race condition | Add explicit UUID to INSERT |

## When to Use

- Porting a PostgreSQL app to MySQL/MariaDB/XAMPP
- When you see 500 errors on endpoints that work in PG
- When the sql-compat runtime layer handles syntax but tables are missing
- When RETURNING * returns empty or wrong rows on UUID tables
- When multiple PG migrations need to be consolidated into MySQL equivalents

## When NOT to Use

- For SQL syntax translation at runtime (use postgresql-to-mysql-runtime-translation)
- When the app uses an ORM that handles schema (Prisma, Sequelize)
- For new applications (design for MySQL from the start)
- When PG-specific features have no MySQL equivalent (PostGIS, row-level security)

## Common Mistakes

- Forgetting `ON UPDATE CURRENT_TIMESTAMP` for `updated_at` columns (PG uses triggers)
- Using `LAST_INSERT_ID()` with UUID tables (returns 0)
- Not making migrations idempotent (crashes on re-run if table/column exists)
- Copying PG foreign key constraints (keep it simple — omit FKs for UUID tables)
- Not restarting the server after migration (Node.js caches modules)
- Using `BOOLEAN` in MySQL DDL without realizing it becomes `TINYINT(1)` (functional, but explicit is clearer)

## Related Skills

- [postgresql-to-mysql-runtime-translation](../database-solutions/postgresql-to-mysql-runtime-translation.md) - Runtime SQL translation layer
- [reserved-word-context-aware-quoting](../database-solutions/reserved-word-context-aware-quoting.md) - Quoting reserved words
- [regex-alternation-ordering-sql-types](../database-solutions/regex-alternation-ordering-sql-types.md) - Type cast regex ordering

## References

- MySQL 8.0 CREATE TABLE: https://dev.mysql.com/doc/refman/8.0/en/create-table.html
- MySQL UUID(): https://dev.mysql.com/doc/refman/8.0/en/miscellaneous-functions.html#function_uuid
- Discovered during: MINISTRY-LMS migration (15+ tables ported in 3 sessions)
- Contributed from: ministry-lms
