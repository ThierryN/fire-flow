---
name: sqlite-to-pg-migration
category: database-solutions
version: 1.0.0
contributed: 2026-03-10
contributor: research
last_updated: 2026-03-10
tags: [sqlite, postgresql, migration, prototype, production]
difficulty: medium
---

# SQLite to PostgreSQL Migration

## Problem

Applications that start on SQLite for simplicity need to graduate to PostgreSQL for concurrency, scale, and production features. This is the most common "prototype to production" migration path (n8n, many Next.js apps, self-hosted tools). The challenge: SQLite's dynamic typing, file-based storage, and limited ALTER TABLE make the migration non-trivial.
## Solution Pattern

### Step 0: Should You Even Migrate?

Before migrating, consider whether SQLite is actually insufficient:

| Stay on SQLite if... | Migrate to PG if... |
|---|---|
| Single-user or read-heavy workload | Multiple concurrent writers |
| < 1GB database | > 1GB or growing fast |
| Edge/embedded deployment | Centralized server |
| Litestream/LiteFS replication is sufficient | Need full ACID with concurrent transactions |
| Simple queries, no joins across large tables | Complex queries, full-text search, JSON indexing |

### Step 1: Audit SQLite Schema

```bash
# List all tables
sqlite3 mydb.db ".tables"

# Dump schema
sqlite3 mydb.db ".schema"

# Check for dynamic typing issues
sqlite3 mydb.db "SELECT typeof(col), COUNT(*) FROM mytable GROUP BY typeof(col);"
```

**Dynamic typing audit:** SQLite allows any value in any column regardless of declared type. Before migration, verify actual stored types match intended types:

```sql
-- Find columns with mixed types (SQLite-specific problem)
SELECT 'users' AS tbl, 'age' AS col,
  SUM(CASE WHEN typeof(age) = 'integer' THEN 1 ELSE 0 END) AS int_count,
  SUM(CASE WHEN typeof(age) = 'text' THEN 1 ELSE 0 END) AS text_count,
  SUM(CASE WHEN typeof(age) = 'null' THEN 1 ELSE 0 END) AS null_count
FROM users;
```

### Step 2: Type Mapping

| SQLite | PostgreSQL | Notes |
|---|---|---|
| `INTEGER` (any size) | `INTEGER` or `BIGINT` | Check max values to choose |
| `INTEGER PRIMARY KEY` | `SERIAL PRIMARY KEY` | SQLite auto-increment via ROWID |
| `REAL` | `DOUBLE PRECISION` | |
| `TEXT` | `TEXT` or `VARCHAR(n)` | Add length constraints as needed |
| `BLOB` | `BYTEA` | |
| `TEXT` (storing dates) | `TIMESTAMPTZ` | Parse ISO 8601 strings |
| `INTEGER` (storing booleans 0/1) | `BOOLEAN` | Cast during migration |
| `TEXT` (storing JSON) | `JSONB` | Parse and validate during migration |
| `TEXT` (storing UUIDs) | `UUID` | Validate format during migration |

### Step 3: Migration with pgloader

```lisp
-- pgloader-sqlite.conf
LOAD DATABASE
  FROM sqlite:///path/to/mydb.db
  INTO postgresql://user:pass@localhost/mydb_pg

WITH
  include drop,
  create tables,
  create indexes,
  reset sequences

-- Override dynamic types
CAST
  type string to text,
  type integer to bigint when (> 2147483647 max-value)

AFTER LOAD DO
  $$ VACUUM ANALYZE; $$
;
```

```bash
pgloader pgloader-sqlite.conf
```

### Step 4: Manual Migration (Alternative)

If pgloader is unavailable or you need more control:

```bash
# 1. Dump SQLite as SQL
sqlite3 mydb.db .dump > dump.sql

# 2. Clean up for PG compatibility
sed -i 's/INTEGER PRIMARY KEY AUTOINCREMENT/SERIAL PRIMARY KEY/g' dump.sql
sed -i 's/PRAGMA.*//g' dump.sql
sed -i 's/BEGIN TRANSACTION/BEGIN/g' dump.sql

# 3. Create PG database and import
createdb mydb_pg
psql -d mydb_pg -f dump.sql
```

**Better approach — use Python for type-aware migration:**

```python
import sqlite3
import psycopg2

# Connect to both
sqlite_conn = sqlite3.connect('mydb.db')
pg_conn = psycopg2.connect('postgresql://user:pass@localhost/mydb_pg')

# For each table: read from SQLite, insert into PG
cursor = sqlite_conn.execute("SELECT * FROM users")
columns = [d[0] for d in cursor.description]
placeholders = ','.join(['%s'] * len(columns))

pg_cur = pg_conn.cursor()
for row in cursor:
    pg_cur.execute(f"INSERT INTO users ({','.join(columns)}) VALUES ({placeholders})", row)

pg_conn.commit()
```

### Step 5: Application Code Changes

1. **Connection:** `better-sqlite3` / `sql.js` → `pg` / `postgres.js`
2. **Parameters:** `?` → `$1, $2, $3`
3. **Boolean values:** `0/1` → `true/false`
4. **Date handling:** Parse TEXT dates into proper TIMESTAMP values
5. **JSON columns:** TEXT → JSONB (add validation)
6. **RETURNING:** Now available natively (SQLite 3.35+ also has it)
7. **Concurrent access:** Remove `PRAGMA journal_mode=WAL` and similar

### Step 6: Post-Migration Health Check

```sql
-- Run ANALYZE on all tables
ANALYZE;

-- Verify row counts match
SELECT relname, n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC;

-- Check for NULL where not expected (dynamic typing cleanup)
SELECT COUNT(*) FROM users WHERE email IS NULL;  -- should be 0 if required

-- Verify sequences
SELECT sequencename, last_value FROM pg_sequences;

-- Test indexes are working
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

### SQLite File Safety

When copying SQLite databases:

```bash
# WRONG: copying while app is running risks corruption
cp mydb.db backup.db  # ❌

# RIGHT: close all connections first, then copy ALL files
# SQLite may have -wal (write-ahead log) and -shm (shared memory) files
cp mydb.db mydb.db-wal mydb.db-shm /backup/  # ✅

# BEST: use sqlite3 backup command
sqlite3 mydb.db ".backup /backup/mydb.db"  # ✅

# VERIFY backup integrity
sqlite3 /backup/mydb.db "PRAGMA integrity_check;"  # Should return "ok"
```

## Common Pitfalls

1. **Dynamic typing:** SQLite column "age" might contain strings, integers, and NULLs. PG will reject mixed types.
2. **Missing constraints:** SQLite doesn't enforce CHECK constraints by default. Data may violate PG constraints.
3. **Foreign keys off:** SQLite FKs are OFF by default (`PRAGMA foreign_keys = ON`). Data may have orphaned references.
4. **Date strings:** SQLite stores dates as TEXT. Must parse and validate every date value during migration.
5. **Boolean ambiguity:** SQLite has no BOOLEAN. Values could be 0/1, 'true'/'false', 'yes'/'no', or anything else.
6. **AUTOINCREMENT behavior:** SQLite AUTOINCREMENT prevents reuse of deleted IDs. PG SERIAL allows reuse. If your app depends on never-reused IDs, use `GENERATED ALWAYS AS IDENTITY`.

## When to Use

- Graduating a prototype from SQLite to PostgreSQL
- Migrating self-hosted tools (n8n, etc.) to managed databases
- Building the DATABASE phase of `/fire-resurrect` for SQLite sources

## When NOT to Use

- Staying on SQLite (edge deployments, read-heavy, small data)
- Migrating between client-server databases (use mysql-to-pg-migration or pg-to-mysql)
- Migrating to MySQL (rare — use the compatibility matrix)

## Related Skills

- [sql-dialect-compatibility-matrix](sql-dialect-compatibility-matrix.md)
- [data-type-mapping-reference](data-type-mapping-reference.md)
- [mysql-to-pg-migration](mysql-to-pg-migration.md)

## References

- Render — "How to Migrate from SQLite to PostgreSQL" (2025)
- Bytebase — "Database Migration: SQLite to PostgreSQL" (2025)
- n8n Community — SQLite to PostgreSQL migration thread (2025)
- SitePoint — "Is SQLite on the Edge Production Ready?" (2026)
- pgloader SQLite source documentation
- sqlite3_rsync — SQLite safe remote copy tool
