---
name: data-type-mapping-reference
category: database-solutions
version: 1.0.0
contributed: 2026-03-10
contributor: research
last_updated: 2026-03-10
tags: [postgresql, mysql, sqlite, sql-server, data-types, migration, type-mapping]
difficulty: medium
---

# Data Type Mapping Reference

## Problem

Database migrations fail silently when type mappings are wrong. Unsigned integers overflow, booleans store unexpected values, dates corrupt, and JSON loses indexability. Developers need a precise, copy-pasteable mapping table for every common type across PostgreSQL, MySQL, SQLite, and SQL Server.
## Complete Type Mapping Table

### Numeric Types

| PostgreSQL | MySQL | SQLite | SQL Server | Migration Notes |
|---|---|---|---|---|
| `SMALLINT` | `SMALLINT` | `INTEGER` | `SMALLINT` | Direct mapping |
| `INTEGER` | `INT` | `INTEGER` | `INT` | Direct mapping |
| `BIGINT` | `BIGINT` | `INTEGER` | `BIGINT` | SQLite uses 8-byte INTEGER for all |
| N/A | `TINYINT` (signed, -128 to 127) | `INTEGER` | `TINYINT` (unsigned, 0-255) | PG has no TINYINT — use SMALLINT |
| N/A | `INT UNSIGNED` | `INTEGER` | N/A | PG: upsize to `BIGINT` for range |
| `NUMERIC(p,s)` | `DECIMAL(p,s)` | `REAL` or `TEXT` | `DECIMAL(p,s)` | Validate precision alignment for financial data |
| `REAL` (4 bytes) | `FLOAT` | `REAL` | `REAL` | Direct mapping |
| `DOUBLE PRECISION` | `DOUBLE` | `REAL` | `FLOAT(53)` | Direct mapping |
| `MONEY` | `DECIMAL(19,2)` | N/A | `MONEY` | Avoid PG MONEY — use NUMERIC(19,2) |

**Unsigned integer rule:** MySQL `UNSIGNED INT` → PG `BIGINT` (upsize to accommodate 0-4.29B range). pgloader does this automatically.

### String Types

| PostgreSQL | MySQL | SQLite | SQL Server | Migration Notes |
|---|---|---|---|---|
| `CHAR(n)` | `CHAR(n)` (max 255) | `TEXT` | `CHAR(n)` (max 8000) | Check length limits |
| `VARCHAR(n)` | `VARCHAR(n)` (max 65535) | `TEXT` | `VARCHAR(n)` / `VARCHAR(MAX)` | PG max ~10M; MySQL max 65K |
| `TEXT` | `TEXT` (64KB) | `TEXT` | `TEXT` | MySQL TEXT is 64KB; use LONGTEXT for larger |
| `TEXT` | `MEDIUMTEXT` (16MB) | `TEXT` | `VARCHAR(MAX)` | pgloader maps all → PG TEXT |
| `TEXT` | `LONGTEXT` (4GB) | `TEXT` | `VARCHAR(MAX)` | pgloader maps all → PG TEXT |

**Charset gotcha:** MySQL defaults to `latin1` in older versions. Always specify `utf8mb4` for full Unicode. PG is always UTF-8.

### Boolean

| PostgreSQL | MySQL | SQLite | SQL Server |
|---|---|---|---|
| `BOOLEAN` | `TINYINT(1)` / `BOOL` | `INTEGER` (0/1) | `BIT` |

**pgloader rule:** MySQL `TINYINT(1)` → PG `BOOLEAN` (only when display width = 1).
**Validation:** MySQL TINYINT(1) can store 0-127. Values > 1 have no boolean mapping — validate before migration.

### Date / Time

| PostgreSQL | MySQL | SQLite | SQL Server | Migration Notes |
|---|---|---|---|---|
| `DATE` | `DATE` | `TEXT` | `DATE` | Direct |
| `TIME` | `TIME` | `TEXT` | `TIME(p)` | Direct |
| `TIMESTAMP` | `DATETIME` | `TEXT` | `DATETIME2(p)` | MySQL DATETIME has no timezone |
| `TIMESTAMPTZ` | `TIMESTAMP` | `TEXT` | `DATETIMEOFFSET(p)` | MySQL TIMESTAMP auto-converts UTC |
| `INTERVAL` | N/A | N/A | N/A | PG-only — convert to seconds or use app logic |

**Critical gotchas:**
- MySQL `0000-00-00` and `0000-00-00 00:00:00` → PG: **rejected**. Convert to NULL.
- MySQL `TIMESTAMP` range: 1970-2038. PG `TIMESTAMPTZ` range: 4713 BC - 294276 AD.
- SQL Server `DATETIME2` precision 0-7; PG max precision 6 (microseconds truncated).
- **pgloader rule:** MySQL `DATETIME`/`TIMESTAMP` → PG `TIMESTAMPTZ`.

### Binary

| PostgreSQL | MySQL | SQLite | SQL Server |
|---|---|---|---|
| `BYTEA` | `BINARY(n)` / `VARBINARY(n)` | `BLOB` | `BINARY(n)` / `VARBINARY(n)` |
| `BYTEA` | `TINYBLOB/BLOB/MEDIUMBLOB/LONGBLOB` | `BLOB` | `IMAGE` (deprecated) |

**pgloader rule:** All MySQL binary/BLOB variants → PG `BYTEA`.

### UUID

| PostgreSQL | MySQL | SQLite | SQL Server |
|---|---|---|---|
| `UUID` (native, 16 bytes) | `CHAR(36)` | `TEXT` | `UNIQUEIDENTIFIER` |
| `gen_random_uuid()` | `UUID()` | N/A (app-side) | `NEWID()` |

**MINISTRY-LMS lesson:** MySQL `LAST_INSERT_ID()` returns 0 for `CHAR(36)` PKs. Generate UUID in JavaScript with `uuidv4()` and include `id` in INSERT column list.

### JSON

| PostgreSQL | MySQL | SQLite | SQL Server | MariaDB |
|---|---|---|---|---|
| `JSON` (text, validated) | `JSON` (binary since 8.0) | `TEXT` or `JSON` (3.45+) | `NVARCHAR(MAX)` | `LONGTEXT` alias |
| `JSONB` (binary, indexable) | N/A | `JSONB` (3.45+) | N/A | N/A |

**Key difference:** PG JSONB supports containment (`@>`), existence (`?`), and GIN indexing. MySQL JSON requires generated columns + B-tree for indexing. MariaDB JSON is just LONGTEXT with no binary optimization.

### Enum

| PostgreSQL | MySQL | SQLite | SQL Server |
|---|---|---|---|
| `CREATE TYPE x AS ENUM(...)` | `ENUM(...)` inline on column | N/A | N/A |

**pgloader rule:** MySQL inline ENUM → PG `CREATE TYPE enum_table_column AS ENUM(...)` + column reference.
**Reverse (PG→MySQL):** Flatten CREATE TYPE into inline ENUM on each column that uses it.

### PostgreSQL-Only Types (No Direct Equivalent)

| PG Type | MySQL Workaround | SQLite Workaround | SQL Server Workaround |
|---|---|---|---|
| `TEXT[]` / `INT[]` | `JSON` (array) | `TEXT` (JSON) | `NVARCHAR(MAX)` (JSON) |
| `JSONB` | `JSON` (lose GIN indexing) | `TEXT` | `NVARCHAR(MAX)` |
| `CIDR` / `INET` | `VARCHAR(43)` | `TEXT` | `VARCHAR(43)` |
| `MACADDR` | `VARCHAR(17)` | `TEXT` | `VARCHAR(17)` |
| `TSVECTOR` / `TSQUERY` | FULLTEXT index (different API) | FTS5 extension | Full-text catalog |
| `HSTORE` | `JSON` | `TEXT` | `NVARCHAR(MAX)` |
| Geometric types | Spatial extensions | N/A | `GEOMETRY` |

## pgloader Default Casting Rules (MySQL → PostgreSQL)

```
TINYINT(1)           → BOOLEAN
TINYINT (other)      → SMALLINT
INT UNSIGNED         → BIGINT
INT AUTO_INCREMENT   → SERIAL
BIGINT AUTO_INCREMENT → BIGSERIAL
BIT(1)               → BOOLEAN
DATETIME/TIMESTAMP   → TIMESTAMPTZ
YEAR                 → INTEGER
All TEXT variants    → TEXT
All BLOB variants   → BYTEA
ENUM(...)            → CREATE TYPE + column
SET(...)             → TEXT
0000-00-00 dates     → NULL
```

## Safest Portable Type Subset

These types work identically across PG, MySQL, SQLite, and SQL Server with zero translation:

```
STRING:    VARCHAR(n) where n ≤ 255
INTEGER:   INT / INTEGER
FLOAT:     REAL / DOUBLE PRECISION
BOOLEAN:   Use INTEGER 0/1 (universally supported)
TEXT:      TEXT (for unlimited strings)
TIMESTAMP: Store as ISO 8601 TEXT for max portability
UUID:      CHAR(36) (string representation)
JSON:      TEXT containing valid JSON (parse in app layer)
```

**Trade-off:** This subset sacrifices database-specific optimizations (JSONB indexing, native UUID, array types) for portability.

## When to Use

- Planning any database migration
- Choosing column types for cross-database applications
- Configuring pgloader / SQLines custom type mappings
- Reviewing ORM schema definitions for portability issues
- Building the DATABASE phase of `/fire-resurrect`

## When NOT to Use

- Single-database projects committed to one vendor
- NoSQL databases
- Data warehouse columns (different optimization concerns)

## Related Skills

- [sql-dialect-compatibility-matrix](sql-dialect-compatibility-matrix.md)
- [pg-to-mysql-schema-migration-methodology](pg-to-mysql-schema-migration-methodology.md)
- [mysql-to-pg-migration](mysql-to-pg-migration.md)

## References

- pgloader MySQL documentation — default casting rules
- MySQL Workbench PostgreSQL type mapping reference
- SQLines data type mapping configuration
- MINISTRY-LMS sql-compat.js — production-proven type handling
- "I Migrated 400M Rows" (Medium, 2026) — type mapping breakage points
