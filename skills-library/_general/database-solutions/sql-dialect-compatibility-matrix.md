---
name: sql-dialect-compatibility-matrix
category: database-solutions
version: 1.0.0
contributed: 2026-03-10
contributor: MINISTRY-LMS, research
last_updated: 2026-03-10
tags: [postgresql, mysql, sqlite, sql-server, mariadb, migration, dialect, translation]
difficulty: hard
---

# SQL Dialect Compatibility Matrix

## Problem

When migrating between databases or building cross-database applications, developers hit dialect differences that cause silent data corruption, runtime errors, or lost functionality. No single reference covers the practical translation rules needed for AI-assisted migration.
## Solution Pattern

Use this matrix as a lookup table during migration planning and execution. Each section is organized by **task** ("what do you want to do?") rather than by database, following the Wikibooks SQL Dialects Reference structure.

**Critical principle:** Always verify translations by running against the target database. Rules handle the deterministic 80%; the remaining 20% requires human judgment or LLM-assisted review with verification.

## SQL Syntax Translation Rules

### Auto-Increment / Sequential IDs

| PostgreSQL | MySQL/MariaDB | SQLite | SQL Server |
|---|---|---|---|
| `SERIAL` | `INT AUTO_INCREMENT` | `INTEGER PRIMARY KEY` (implicit ROWID) | `INT IDENTITY(1,1)` |
| `BIGSERIAL` | `BIGINT AUTO_INCREMENT` | same (64-bit ROWID) | `BIGINT IDENTITY(1,1)` |
| `GENERATED ALWAYS AS IDENTITY` | N/A | N/A | `IDENTITY(start, increment)` |

**Gotcha:** MySQL `LAST_INSERT_ID()` returns 0 for UUID primary key tables (`CHAR(36) DEFAULT (UUID())`). Generate UUID in application code and include `id` in INSERT.

### Boolean

| PostgreSQL | MySQL/MariaDB | SQLite | SQL Server |
|---|---|---|---|
| `BOOLEAN` (native) | `TINYINT(1)` / `BOOL` alias | `INTEGER` (0/1) | `BIT` |

**Gotcha:** MySQL `BOOL` is literally `TINYINT(1)` — stores 0-127, not just 0/1. Validate value ranges when migrating to PG.

### Text / String Types

| PostgreSQL | MySQL | SQLite | SQL Server |
|---|---|---|---|
| `VARCHAR(n)` up to 10M | `VARCHAR(n)` up to 65K | `TEXT` (all strings) | `VARCHAR(n)` up to 8K; `VARCHAR(MAX)` |
| `TEXT` (unlimited) | `TINYTEXT/TEXT/MEDIUMTEXT/LONGTEXT` | `TEXT` | `TEXT`/`NTEXT` |

**Gotcha:** MySQL silently truncates in some SQL modes; PG raises error. pgloader maps all MySQL TEXT variants to PG `TEXT`.

### Date / Time Types

| PostgreSQL | MySQL | SQLite | SQL Server |
|---|---|---|---|
| `TIMESTAMP` | `DATETIME` | `TEXT` (ISO 8601) | `DATETIME2(p)` |
| `TIMESTAMPTZ` | `TIMESTAMP` (auto UTC) | `TEXT` | `DATETIMEOFFSET(p)` |
| `INTERVAL` | N/A | N/A | N/A |

**Gotcha:** MySQL allows `0000-00-00` dates; PG rejects them. pgloader converts to NULL. **HIGH data loss risk** for timezone conversions.

### UUID

| PostgreSQL | MySQL/MariaDB | SQLite | SQL Server |
|---|---|---|---|
| `UUID` (native) | `CHAR(36)` / `VARCHAR(36)` | `TEXT` | `UNIQUEIDENTIFIER` |
| `gen_random_uuid()` | `UUID()` | N/A (app-side) | `NEWID()` |

### JSON

| PostgreSQL | MySQL | SQLite | SQL Server | MariaDB |
|---|---|---|---|---|
| `JSONB` (binary, indexable) | `JSON` (validated) | `JSON` (3.45+ JSONB) | `NVARCHAR(MAX)` | `JSON` (alias for `LONGTEXT`) |
| `col->>'key'` | `JSON_UNQUOTE(JSON_EXTRACT(col, '$.key'))` | `json_extract(col, '$.key')` | `JSON_VALUE(col, '$.key')` | same as MySQL |
| `col->'key'` | `JSON_EXTRACT(col, '$.key')` | `json_extract(col, '$.key')` | `JSON_QUERY(col, '$.key')` | same as MySQL |
| `col @> '{"k":"v"}'` | N/A | N/A | N/A | N/A |
| GIN index on JSONB | Generated column + B-tree | N/A | Computed column + index | N/A |

**Gotcha:** PG `->` uses plain key names; MySQL uses JSONPath (`$.key`). Completely different path syntax.

### Arrays

| PostgreSQL | MySQL | SQLite | SQL Server | MariaDB |
|---|---|---|---|---|
| `TEXT[]`, `INT[]` (native) | N/A (use JSON) | N/A | N/A | N/A |

**PG-only.** Must denormalize to JSON array or junction table for other databases.

### Enums

| PostgreSQL | MySQL/MariaDB | SQLite | SQL Server |
|---|---|---|---|
| `CREATE TYPE status AS ENUM(...)` (type-level) | `ENUM(...)` (column-level inline) | N/A (use CHECK) | N/A (use CHECK) |

**Gotcha:** pgloader creates separate `CREATE TYPE` for each MySQL inline ENUM.

## SQL Syntax Differences

### RETURNING Clause

| Database | Support | Syntax |
|---|---|---|
| PostgreSQL | Full (INSERT/UPDATE/DELETE) | `INSERT ... RETURNING *` |
| MySQL | **None** | Use `LAST_INSERT_ID()` or re-SELECT |
| SQLite | Full (3.35+) | `INSERT ... RETURNING *` |
| SQL Server | Full | `OUTPUT inserted.*` / `OUTPUT deleted.*` |
| MariaDB | Partial (INSERT/DELETE only) | `INSERT ... RETURNING *` |

**MINISTRY-LMS pattern:** 4-strategy fallback chain:
1. UUID lookup (best for UUID PKs)
2. Unique column lookup (for upserts)
3. `LAST_INSERT_ID()` (auto-increment only — returns 0 for UUID!)
4. Most recent row by `created_at` (race condition risk)

### UPSERT / Merge

| Database | Syntax |
|---|---|
| PostgreSQL | `INSERT ... ON CONFLICT (col) DO UPDATE SET ...` |
| MySQL/MariaDB | `INSERT ... ON DUPLICATE KEY UPDATE ...` |
| SQLite | `INSERT ... ON CONFLICT (col) DO UPDATE SET ...` (same as PG) |
| SQL Server | `MERGE INTO ... USING ... WHEN MATCHED THEN UPDATE ...` |

**Translation:** `ON CONFLICT ... DO UPDATE` → `ON DUPLICATE KEY UPDATE`, `EXCLUDED.col` → `VALUES(col)`, `DO NOTHING` → `INSERT IGNORE INTO`.

### LIMIT / OFFSET

| Database | Syntax |
|---|---|
| PostgreSQL | `LIMIT n OFFSET k` |
| MySQL/MariaDB | `LIMIT n OFFSET k` or `LIMIT k, n` |
| SQLite | `LIMIT n OFFSET k` |
| SQL Server | `OFFSET k ROWS FETCH NEXT n ROWS ONLY` (requires ORDER BY) |

**Gotcha:** MySQL rejects `LIMIT '20'` (string); PG silently casts. Always `parseInt()` LIMIT/OFFSET from Express `req.query`.

### String Concatenation

| Database | Syntax |
|---|---|
| PostgreSQL | `'a' \|\| 'b'` |
| MySQL | `CONCAT('a', 'b')` (`\|\|` means OR by default) |
| SQLite | `'a' \|\| 'b'` |
| SQL Server | `'a' + 'b'` |

### Identifier Quoting

| Database | Quote Character |
|---|---|
| PostgreSQL | `"double quotes"` (case-preserving) |
| MySQL/MariaDB | `` `backticks` `` |
| SQLite | `"double quotes"` or `` `backticks` `` |
| SQL Server | `[brackets]` or `"double quotes"` |

### NULL Sort Order

| Database | Default ASC | Default DESC |
|---|---|---|
| PostgreSQL | NULLs LAST | NULLs FIRST |
| MySQL | NULLs FIRST | NULLs LAST |
| SQLite | NULLs FIRST | NULLs LAST |
| SQL Server | NULLs FIRST | NULLs LAST |

**Translation:** PG `NULLS LAST` → MySQL `ORDER BY col IS NULL, col DESC`. PG `NULLS FIRST` → MySQL `ORDER BY col IS NOT NULL, col ASC`.

### Type Casting

| Database | Shorthand | Standard |
|---|---|---|
| PostgreSQL | `x::type` | `CAST(x AS type)` |
| MySQL | N/A | `CAST(x AS type)` / `CONVERT(x, type)` |
| SQLite | N/A | `CAST(x AS type)` |
| SQL Server | N/A | `CAST(x AS type)` / `CONVERT(type, x)` |

**Translation:** Strip all PG `::type` patterns for MySQL/SQLite. Use `CAST()` for portability.

## Function Translation

### Date Functions

| Operation | PostgreSQL | MySQL | SQLite | SQL Server |
|---|---|---|---|---|
| Current time | `NOW()` | `NOW()` | `datetime('now')` | `GETDATE()` |
| Extract part | `EXTRACT(YEAR FROM d)` | `YEAR(d)` | `strftime('%Y', d)` | `DATEPART(year, d)` |
| Date add | `d + INTERVAL '1 day'` | `DATE_ADD(d, INTERVAL 1 DAY)` | `datetime(d, '+1 day')` | `DATEADD(day, 1, d)` |
| Date diff | `d1 - d2` (interval) | `DATEDIFF(d1, d2)` (days) | `julianday(d1) - julianday(d2)` | `DATEDIFF(day, d1, d2)` |
| Format | `TO_CHAR(d, 'YYYY-MM-DD')` | `DATE_FORMAT(d, '%Y-%m-%d')` | `strftime('%Y-%m-%d', d)` | `FORMAT(d, 'yyyy-MM-dd')` |
| Truncate | `DATE_TRUNC('month', d)` | `DATE_FORMAT(d, '%Y-%m-01')` | `strftime('%Y-%m-01', d)` | `DATETRUNC(month, d)` |

**Format token mapping (PG → MySQL):** `YYYY→%Y`, `MM→%m`, `DD→%d`, `HH24→%H`, `MI→%i`, `SS→%s`.

### String Functions

| Operation | PostgreSQL | MySQL | SQLite | SQL Server |
|---|---|---|---|---|
| Length | `LENGTH(s)` | `LENGTH(s)` | `LENGTH(s)` | `LEN(s)` |
| Position | `POSITION(sub IN s)` | `LOCATE(sub, s)` | `INSTR(s, sub)` | `CHARINDEX(sub, s)` |
| Regex match | `~ 'pattern'` | `REGEXP 'pattern'` | N/A | N/A |
| Case-insensitive LIKE | `ILIKE` | `LIKE` (CI by default) | `LIKE` (CI for ASCII) | `LIKE` (collation) |
| String split | `split_part(s, ',', 2)` | `SUBSTRING_INDEX(SUBSTRING_INDEX(s, ',', 2), ',', -1)` | N/A | N/A |

### Aggregate Functions

| Operation | PostgreSQL | MySQL | SQLite | SQL Server |
|---|---|---|---|---|
| String agg | `STRING_AGG(col, ',')` | `GROUP_CONCAT(col SEPARATOR ',')` | `GROUP_CONCAT(col, ',')` | `STRING_AGG(col, ',')` (2017+) |
| JSON agg | `json_agg(col)` | `CONCAT('[', GROUP_CONCAT(col), ']')` | `json_group_array(col)` | N/A |
| Filtered agg | `COUNT(*) FILTER (WHERE x)` | `SUM(CASE WHEN x THEN 1 ELSE 0 END)` | N/A | N/A |
| JSON object | `jsonb_build_object('k', v)` | `JSON_OBJECT('k', v)` | `json_object('k', v)` | N/A |

## Constraints & Indexing

### Constraint Support

| Feature | PostgreSQL | MySQL (InnoDB) | SQLite | SQL Server |
|---|---|---|---|---|
| CHECK constraints | Full | Enforced 8.0.16+ (ignored before!) | Full | Full |
| Deferred constraints | `DEFERRABLE INITIALLY DEFERRED` | **Not supported** | Supported | **Not supported** |
| EXCLUDE constraints | Full (GiST) | **Not supported** | **Not supported** | **Not supported** |
| Multiple cascade paths | Allowed | Allowed | Allowed | **Not allowed** |

**Gotcha:** MySQL CHECK constraints were silently ignored for years. Data may violate constraints after PG migration.

### Index Types

| Feature | PostgreSQL | MySQL | SQLite | SQL Server |
|---|---|---|---|---|
| Partial index | `WHERE condition` | **No** | Yes (3.8+) | Yes (filtered) |
| Expression index | `ON (lower(col))` | **No** (use generated column) | Yes (3.9+) | Computed column |
| GIN (inverted) | Yes | **No** | **No** | **No** |
| Covering (INCLUDE) | Yes (11+) | **No** | **No** | Yes |
| Concurrent creation | `CONCURRENTLY` | `ALGORITHM=INPLACE` | **No** | `ONLINE = ON` |

## Automatable vs Human Judgment

### Fully Automatable (lookup table)
- Basic type mappings (INT, VARCHAR, TEXT, DATE)
- Auto-increment syntax
- LIMIT/OFFSET syntax
- String concatenation
- Identifier quoting
- UPSERT templates
- RETURNING clause templates
- Type cast stripping (`::type`)
- ILIKE → LIKE
- Interval syntax (`INTERVAL '30 days'` → `INTERVAL 30 DAY`)

### Partially Automatable (rules + validation)
- Unsigned integer upsizing (MySQL UNSIGNED INT → PG BIGINT)
- BOOLEAN conversion (validate TINYINT(1) value ranges)
- Zero-date handling (`0000-00-00` → NULL)
- ENUM extraction (inline → CREATE TYPE)
- Text encoding conversion (detect charset first)

### Requires Human Judgment
- ARRAY type decomposition (JSON vs junction table — depends on access patterns)
- Timezone semantics (TIMESTAMP vs TIMESTAMPTZ behavior)
- DECIMAL precision alignment for financial data
- Index strategy redesign (GIN/GiST have no equivalents)
- Stored procedure rewriting (procedural syntax differs fundamentally)
- Collation and case-sensitivity behavior
- Constraint validation (lax MySQL CHECK → strict PG)

## Tools Reference

| Tool | Direction | Type | Best For |
|------|-----------|------|----------|
| **SQLGlot** | 31+ dialects | Deterministic (Python) | Automated SQL transpiling |
| **pgloader** | MySQL/SQLite → PG | Declarative config | One-shot migration with type mapping |
| **SQLines** | 10+ dialects | Rule-based | DDL + DML + stored procedures |
| **AWS SCT** | Any → AWS DB | Assessment + conversion | Migration complexity scoring |
| **sql-compat.js** (MINISTRY-LMS) | PG → MySQL | Runtime layer | Live bilingual applications |

## When to Use

- Planning a database migration (any direction)
- Building cross-database applications
- Writing the DATABASE phase of `/fire-resurrect`
- Reviewing ORM migration portability
- Auditing SQL for dialect-specific constructs before migration

## When NOT to Use

- Single-database projects with no migration plans
- NoSQL databases (MongoDB, Redis, DynamoDB)
- Data warehouse migrations (Snowflake, BigQuery — different paradigm)

## Related Skills

- [pg-to-mysql-schema-migration-methodology](pg-to-mysql-schema-migration-methodology.md)
- [mysql-limit-offset-string-coercion](mysql-limit-offset-string-coercion.md)
- [mysql-to-pg-migration](mysql-to-pg-migration.md)
- [sqlite-to-pg-migration](sqlite-to-pg-migration.md)
- [orm-schema-portability](orm-schema-portability.md)
- [data-type-mapping-reference](data-type-mapping-reference.md)

## References

- PARROT Benchmark (NeurIPS 2025) — SQL translation accuracy evaluation
- CrackSQL (SIGMOD 2025) — Hybrid rule+LLM dialect translation
- RISE (arXiv 2601.05579, 2026) — Rule-driven SQL dialect translation
- SQLGlot (github.com/tobymao/sqlglot) — Python SQL transpiler, 31+ dialects
- pgloader (pgloader.readthedocs.io) — MySQL/SQLite to PostgreSQL migration
- Troels Arvin — SQL implementation comparison (troels.arvin.dk/db/rdbms/)
- Wikibooks SQL Dialects Reference
- MINISTRY-LMS sql-compat.js — 27 production-proven translation rules
