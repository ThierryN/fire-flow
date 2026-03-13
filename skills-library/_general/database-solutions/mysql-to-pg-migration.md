---
name: mysql-to-pg-migration
category: database-solutions
version: 1.0.0
contributed: 2026-03-10
contributor: research
last_updated: 2026-03-10
tags: [mysql, postgresql, migration, pgloader, schema-conversion]
difficulty: hard
---

# MySQL to PostgreSQL Migration

## Problem

Migrating from MySQL to PostgreSQL is the most common enterprise database migration direction (validated by the $480K/year savings case study, 2026). Despite tooling like pgloader, 20% of translations require manual intervention — type mappings, stored procedure rewrites, and application code changes that tools miss.
## Solution Pattern

### Phase 1: Assessment

Before any migration, audit the source MySQL database:

```sql
-- Count tables, views, procedures, triggers
SELECT 'tables' AS type, COUNT(*) FROM information_schema.tables WHERE table_schema = 'mydb'
UNION ALL
SELECT 'views', COUNT(*) FROM information_schema.views WHERE table_schema = 'mydb'
UNION ALL
SELECT 'procedures', COUNT(*) FROM information_schema.routines WHERE routine_schema = 'mydb'
UNION ALL
SELECT 'triggers', COUNT(*) FROM information_schema.triggers WHERE trigger_schema = 'mydb';

-- Find unsigned columns (require upsizing)
SELECT table_name, column_name, column_type
FROM information_schema.columns
WHERE table_schema = 'mydb' AND column_type LIKE '%unsigned%';

-- Find ENUM columns (require CREATE TYPE)
SELECT table_name, column_name, column_type
FROM information_schema.columns
WHERE table_schema = 'mydb' AND data_type = 'enum';

-- Find zero-date values (will become NULL)
SELECT table_name, column_name
FROM information_schema.columns
WHERE table_schema = 'mydb' AND (data_type = 'datetime' OR data_type = 'timestamp');
```

### Phase 2: Schema Conversion

#### Core Type Translations

| MySQL | PostgreSQL | Notes |
|---|---|---|
| `INT AUTO_INCREMENT` | `SERIAL` or `GENERATED ALWAYS AS IDENTITY` | IDENTITY is SQL standard |
| `BIGINT AUTO_INCREMENT` | `BIGSERIAL` | |
| `TINYINT(1)` / `BOOL` | `BOOLEAN` | Validate no values > 1 |
| `TINYINT` (other) | `SMALLINT` | |
| `INT UNSIGNED` | `BIGINT` | Upsize for unsigned range |
| `DOUBLE` | `DOUBLE PRECISION` | |
| `DATETIME` | `TIMESTAMP` or `TIMESTAMPTZ` | Choose based on timezone needs |
| `ENUM('a','b','c')` | `CREATE TYPE myenum AS ENUM('a','b','c')` | One type per unique enum set |
| `` `backtick_quoted` `` | `"double_quoted"` | PG preserves case in quotes |
| `JSON` | `JSONB` | Upgrade to binary for indexing |

#### Syntax Translations (Application Code)

| MySQL | PostgreSQL | Notes |
|---|---|---|
| `IFNULL(a, b)` | `COALESCE(a, b)` | COALESCE is SQL standard |
| `IF(cond, a, b)` | `CASE WHEN cond THEN a ELSE b END` | |
| `LIMIT k, n` | `LIMIT n OFFSET k` | Argument order reverses! |
| `DATE_FORMAT(d, '%Y-%m')` | `TO_CHAR(d, 'YYYY-MM')` | Different format tokens |
| `GROUP_CONCAT(col)` | `STRING_AGG(col, ',')` | PG requires explicit separator |
| `CONCAT(a, b)` | `a \|\| b` | PG also supports CONCAT() |
| `NOW()` | `NOW()` | Same |
| `LOCATE(sub, str)` | `POSITION(sub IN str)` | |
| `json_extract(col, '$.key')` | `col->>'key'` | Simpler syntax in PG |
| `ON DUPLICATE KEY UPDATE` | `ON CONFLICT (col) DO UPDATE SET` | Different upsert syntax |
| `VALUES(col)` (in upsert) | `EXCLUDED.col` | Reference to proposed row |
| `INSERT IGNORE INTO` | `ON CONFLICT DO NOTHING` | |

### Phase 3: Automated Migration with pgloader

```lisp
-- pgloader.conf
LOAD DATABASE
  FROM mysql://user:pass@localhost/mydb
  INTO postgresql://user:pass@localhost/mydb_pg

WITH
  include drop,
  create tables,
  create indexes,
  reset sequences,
  workers = 4,
  concurrency = 2

-- Custom type overrides
CAST
  type tinyint when (= 1 precision) to boolean using tinyint-to-boolean,
  type int when unsigned to bigint,
  type year to integer,
  type datetime to timestamptz

-- Handle zero-dates
BEFORE LOAD DO
  $$ ALTER DATABASE mydb_pg SET datestyle TO 'ISO, MDY'; $$

AFTER LOAD DO
  $$ VACUUM ANALYZE; $$
;
```

```bash
# Run pgloader
pgloader pgloader.conf

# Verify
psql -d mydb_pg -c "SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'public';"
```

### Phase 4: Application Code Changes

1. **Connection driver:** `mysql2` → `pg` (or `postgres.js`)
2. **Parameter placeholders:** `?` → `$1, $2, $3` (numbered)
3. **Identifier quoting:** Backticks → double quotes (or remove)
4. **Boolean values:** `1/0` → `true/false`
5. **JSON access:** `JSON_EXTRACT(col, '$.key')` → `col->>'key'`
6. **Date formatting:** `DATE_FORMAT(d, '%Y-%m-%d')` → `TO_CHAR(d, 'YYYY-MM-DD')`
7. **String aggregation:** `GROUP_CONCAT(col SEPARATOR ',')` → `STRING_AGG(col::text, ',')`
8. **UPSERT:** `ON DUPLICATE KEY UPDATE` → `ON CONFLICT ... DO UPDATE SET`
9. **LIMIT syntax:** `LIMIT offset, count` → `LIMIT count OFFSET offset`
10. **RETURNING:** Can now use `INSERT ... RETURNING *` natively (was emulated)

### Phase 5: Post-Migration Validation

```bash
# Compare table counts
mysql -u user -p mydb -e "SELECT COUNT(*) FROM users;"
psql -d mydb_pg -c "SELECT COUNT(*) FROM users;"

# Compare row counts for all tables
psql -d mydb_pg -c "
  SELECT schemaname, relname, n_live_tup
  FROM pg_stat_user_tables
  ORDER BY n_live_tup DESC;
"

# Run VACUUM ANALYZE on all tables
psql -d mydb_pg -c "VACUUM ANALYZE;"

# Verify sequences are correct
psql -d mydb_pg -c "
  SELECT sequencename, last_value
  FROM pg_sequences
  WHERE schemaname = 'public';
"
```

## Common Breakage Points

1. **Timezone drift:** MySQL DATETIME has no timezone; PG TIMESTAMPTZ is UTC-aware. Audit trail timestamps may shift.
2. **Zero-dates:** MySQL `0000-00-00` → NULL in PG. Application code expecting these dates will break.
3. **Case sensitivity:** MySQL table names are case-insensitive on Windows; PG is always case-sensitive. Verify all table references.
4. **ENUM ordering:** MySQL ENUMs have implicit ordering; PG ENUMs have explicit ordering. Sorts may change.
5. **Implicit type casts:** MySQL silently casts strings to numbers in comparisons; PG raises errors.
6. **GROUP BY strictness:** PG requires all non-aggregated columns in GROUP BY; MySQL's `ONLY_FULL_GROUP_BY` is optional.

## When to Use

- Migrating from MySQL to PostgreSQL (any direction)
- Planning a database migration for `/fire-resurrect --migrate`
- Evaluating migration complexity before committing

## When NOT to Use

- MySQL-to-MySQL upgrades (different problem)
- Migrating to/from NoSQL
- Small SQLite databases (use sqlite-to-pg-migration instead)

## Related Skills

- [sql-dialect-compatibility-matrix](sql-dialect-compatibility-matrix.md)
- [data-type-mapping-reference](data-type-mapping-reference.md)
- [pg-to-mysql-schema-migration-methodology](pg-to-mysql-schema-migration-methodology.md) — reverse direction
- [sqlite-to-pg-migration](sqlite-to-pg-migration.md)

## References

- "The MySQL-to-Postgres Migration That Saved $480K/Year" (Medium, 2026)
- "I Migrated 400M Rows — Here's What Actually Broke" (Medium, 2026)
- pgloader documentation (pgloader.readthedocs.io)
- AI2sql MySQL-to-PostgreSQL conversion guide (2026)
- Percona pgloader guide (percona.com/blog)
