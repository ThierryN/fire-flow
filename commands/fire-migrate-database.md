---
name: fire-migrate-database
description: Interactive database migration assistant — assess, plan, execute, and verify migrations between PostgreSQL, MySQL, SQLite, and SQL Server
arguments:
  - name: direction
    description: "Migration direction: pg-to-mysql, mysql-to-pg, sqlite-to-pg, pg-to-sqlite, or auto-detect"
    required: false
    type: string
  - name: source
    description: "Source connection string, file path (SQLite), or project path to analyze"
    required: false
    type: string
  - name: target
    description: "Target connection string or 'plan-only' for assessment without execution"
    required: false
    type: string
triggers:
  - "migrate database"
  - "database migration"
  - "transfer database"
  - "switch database"
  - "convert database"
  - "port to postgres"
  - "port to mysql"
  - "move to postgresql"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
---

# /fire-migrate-database — Database Migration Assistant

> Guided migration between PostgreSQL, MySQL, SQLite, and SQL Server — powered by battle-tested dialect translation skills.

## Purpose

Take a database migration from "I need to switch databases" to "migration verified and complete" through a structured 6-step pipeline. Uses the Dominion Flow database-solutions skills library as its knowledge base.

**What this command does NOT do:**
- It does NOT touch your source database (read-only unless you explicitly approve a backup dump)
- It does NOT execute destructive operations without confirmation
- It does NOT guess — it audits first, then proposes

---

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `direction` | No | `auto-detect` | Migration path: `pg-to-mysql`, `mysql-to-pg`, `sqlite-to-pg`, `pg-to-sqlite`, `auto` |
| `source` | No | Interactive | Connection string, SQLite file path, or project directory to analyze |
| `target` | No | Interactive | Target connection string, or `plan-only` for assessment without execution |

## Usage

```bash
# Fully interactive (guided wizard)
/fire-migrate-database

# Specify direction
/fire-migrate-database mysql-to-pg

# Full specification
/fire-migrate-database --direction mysql-to-pg --source "mysql://user:pass@localhost/mydb" --target "postgresql://user:pass@localhost/mydb_pg"

# Assessment only — no execution
/fire-migrate-database --direction sqlite-to-pg --source ./mydb.sqlite --target plan-only

# Auto-detect from project code
/fire-migrate-database --source C:/Projects/my-app
```

---

## Process

### Step 1: Determine Migration Context

```
+---------------------------------------------------------------+
|          DATABASE MIGRATION ASSISTANT                           |
+---------------------------------------------------------------+
|                                                                 |
|  This wizard will guide you through a database migration.      |
|                                                                 |
|  Pipeline:                                                     |
|    1. DETECT   — Identify source and target databases          |
|    2. AUDIT    — Analyze schema, find breaking changes         |
|    3. PLAN     — Generate migration plan with translations     |
|    4. PREPARE  — Create migration scripts and app code patches |
|    5. EXECUTE  — Run the migration (with your approval)        |
|    6. VERIFY   — Validate data integrity and completeness      |
|                                                                 |
|  Safety: Source database is READ-ONLY throughout.              |
|                                                                 |
+---------------------------------------------------------------+
```

**IF direction not provided — auto-detect:**

```
Scan project directory for database indicators:

  PostgreSQL signals:
    - package.json: "pg", "postgres", "knex" with pg config, prisma with postgresql
    - .env: DATABASE_URL containing "postgres://" or "postgresql://"
    - prisma/schema.prisma: provider = "postgresql"
    - docker-compose.yml: postgres image

  MySQL signals:
    - package.json: "mysql2", "mysql", knex with mysql config
    - .env: DATABASE_URL containing "mysql://"
    - prisma/schema.prisma: provider = "mysql"
    - docker-compose.yml: mysql/mariadb image

  SQLite signals:
    - package.json: "better-sqlite3", "sql.js", "sqlite3"
    - .env: DATABASE_URL containing "file:" or ".sqlite" or ".db"
    - prisma/schema.prisma: provider = "sqlite"
    - *.db or *.sqlite files in project root

  SQL Server signals:
    - package.json: "mssql", "tedious"
    - .env: containing "sqlserver://" or "Server="
```

**IF auto-detect finds source but not target:**

```
Detected source: {database} ({version if available})

What database are you migrating TO?

  1. PostgreSQL  — Best for: complex queries, JSONB, full-text search, extensions
  2. MySQL       — Best for: WordPress, read-heavy, hosting compatibility
  3. SQLite      — Best for: embedded, serverless, edge, prototypes
  4. SQL Server  — Best for: .NET ecosystem, enterprise

Select target (1-4): >
```

### Step 2: AUDIT — Analyze Source Schema

```
Load the appropriate skill based on direction:

  mysql-to-pg    → @skills-library/_general/database-solutions/mysql-to-pg-migration.md
  sqlite-to-pg   → @skills-library/_general/database-solutions/sqlite-to-pg-migration.md
  pg-to-mysql    → @skills-library/_general/database-solutions/pg-to-mysql-schema-migration-methodology.md
  any direction  → @skills-library/_general/database-solutions/sql-dialect-compatibility-matrix.md
  any direction  → @skills-library/_general/database-solutions/data-type-mapping-reference.md
```

**IF source is a connection string — query the database directly:**

```sql
-- Table inventory
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = '{schema}';

-- Column details with types
SELECT table_name, column_name, data_type, column_type,
       is_nullable, column_default, character_maximum_length
FROM information_schema.columns
WHERE table_schema = '{schema}'
ORDER BY table_name, ordinal_position;

-- Foreign keys
SELECT constraint_name, table_name, column_name,
       referenced_table_name, referenced_column_name
FROM information_schema.key_column_usage
WHERE table_schema = '{schema}' AND referenced_table_name IS NOT NULL;

-- Indexes
SELECT index_name, table_name, column_name, non_unique
FROM information_schema.statistics
WHERE table_schema = '{schema}';
```

**IF source is a project path — analyze ORM/migration files:**

```
Scan for schema definitions:
  - prisma/schema.prisma → Parse models, relations, enums
  - knex migration files → Parse createTable calls
  - sequelize models → Parse define() calls
  - typeorm entities → Parse @Entity decorators
  - drizzle schema files → Parse pgTable/mysqlTable/sqliteTable calls
  - raw SQL migration files → Parse CREATE TABLE statements
  - Django models.py → Parse Model class definitions
```

**IF source is a SQLite file:**

```bash
sqlite3 {source} ".schema"
sqlite3 {source} ".tables"
# Dynamic typing audit (SQLite-specific)
sqlite3 {source} "SELECT typeof(col), COUNT(*) FROM {table} GROUP BY typeof(col);"
```

**Generate audit report:**

```markdown
-------------------------------------------------------------
SCHEMA AUDIT: {source_name}
-------------------------------------------------------------

Database: {type} {version}
Tables: {count}
Views: {count}
Indexes: {count}
Foreign Keys: {count}
Stored Procedures: {count}

-------------------------------------------------------------
BREAKING CHANGES DETECTED
-------------------------------------------------------------

| # | Table | Column | Issue | Severity | Auto-Fix? |
|---|-------|--------|-------|----------|-----------|
| 1 | users | role | ENUM → needs CREATE TYPE | MEDIUM | Yes |
| 2 | orders | total | UNSIGNED INT → needs BIGINT | LOW | Yes |
| 3 | posts | body | LONGTEXT → TEXT (size OK) | LOW | Yes |
| 4 | events | start | DATETIME → TIMESTAMPTZ | HIGH | Partial |
| 5 | users | settings | JSON → JSONB (reindex) | MEDIUM | Yes |

-------------------------------------------------------------
APPLICATION CODE CHANGES NEEDED
-------------------------------------------------------------

| # | Pattern | Occurrences | Translation |
|---|---------|-------------|-------------|
| 1 | ? placeholders | 47 | → $1, $2, $3 |
| 2 | IFNULL() | 3 | → COALESCE() |
| 3 | LIMIT k, n | 12 | → LIMIT n OFFSET k |
| 4 | DATE_FORMAT() | 5 | → TO_CHAR() |
| 5 | ON DUPLICATE KEY | 2 | → ON CONFLICT DO UPDATE |
| 6 | GROUP_CONCAT() | 4 | → STRING_AGG() |
| 7 | backtick quotes | 31 | → remove or double-quote |
| 8 | LAST_INSERT_ID() | 8 | → RETURNING clause |

-------------------------------------------------------------
ORM ASSESSMENT
-------------------------------------------------------------

ORM detected: {name} {version}
Portability rating: {from orm-schema-portability skill}
ORM-specific changes needed: {list}

Migration state table: {name} — {N} migrations tracked
Strategy: Copy migration files → point at new DB → run migrate:latest

-------------------------------------------------------------
COMPLEXITY SCORE
-------------------------------------------------------------

  Schema changes:    {N} ({N auto-fixable}, {N manual})
  Code changes:      {N} patterns across {N} files
  Stored procedures: {N} (require manual rewrite)
  Data volume:       {N} rows across {N} tables

  Overall: {SIMPLE | MODERATE | COMPLEX}

  Estimated effort:
    SIMPLE   — < 1 hour with pgloader, mostly automated
    MODERATE — 2-4 hours, some manual type mapping and code changes
    COMPLEX  — 1-2 days, stored procedure rewrites, extensive testing
-------------------------------------------------------------
```

### Step 3: PLAN — Generate Migration Plan

```markdown
-------------------------------------------------------------
MIGRATION PLAN: {source_type} → {target_type}
-------------------------------------------------------------

## Phase 1: Schema Translation

{For each table, generate CREATE TABLE in target dialect}
{Apply type mappings from data-type-mapping-reference skill}
{Apply syntax rules from sql-dialect-compatibility-matrix skill}

## Phase 2: Data Migration Strategy

Option A: pgloader (recommended for mysql-to-pg, sqlite-to-pg)
  - Generate pgloader.conf with custom CAST rules
  - Handles type conversion, zero-dates, boolean mapping
  - Parallel workers for large datasets

Option B: Dump and Transform
  - mysqldump / pg_dump / sqlite3 .dump
  - sed/awk transformations for syntax differences
  - psql / mysql import

Option C: Application-Level ETL
  - Read from source with source driver
  - Transform in application code (type conversion, validation)
  - Write to target with target driver
  - Best for: complex transformations, data cleaning during migration

Recommended: {A, B, or C based on direction and complexity}

## Phase 3: Application Code Patches

{For each code change pattern from audit:}
  File: {path}
  Line: {number}
  Before: {original code}
  After: {translated code}
  Rule: {which skill rule applies}

## Phase 4: ORM Migration

{Based on orm-schema-portability skill:}
  - Update connection config
  - Update provider in schema file (if Prisma/Drizzle)
  - Regenerate types/client
  - Run existing migrations against new database

## Phase 5: Verification Queries

{Generate verification queries for target database:}
  - Row count comparison per table
  - Sequence/auto-increment verification
  - Foreign key constraint validation
  - Index existence check
  - Sample data spot-checks (first/last/random rows)
```

**Present plan to user:**

```
Migration plan generated with {N} schema changes, {N} code patches.

Options:
  A) Execute migration now (with confirmations at each phase)
  B) Export plan to file (review offline, execute later)
  C) Modify plan (adjust specific translations)
  D) Cancel

Select: >
```

**IF target == "plan-only":** Auto-select B, save plan, display path, STOP.

### Step 4: PREPARE — Create Migration Artifacts

Based on direction, generate the appropriate files:

```
{project}/.migration/
  ├── README.md                    — Migration overview and instructions
  ├── audit-report.md              — Full audit from Step 2
  ├── migration-plan.md            — Full plan from Step 3
  ├── schema/
  │   ├── source-schema.sql        — Current schema (for reference)
  │   └── target-schema.sql        — Translated schema for target DB
  ├── config/
  │   ├── pgloader.conf            — pgloader config (if applicable)
  │   └── connection.env           — Target connection template
  ├── patches/
  │   ├── 001-parameter-placeholders.patch  — ? → $1,$2,$3
  │   ├── 002-function-translations.patch   — IFNULL → COALESCE, etc.
  │   └── 003-syntax-translations.patch     — LIMIT, UPSERT, etc.
  └── verify/
      ├── count-comparison.sql     — Row count queries for both databases
      ├── sequence-check.sql       — Sequence/auto-increment verification
      └── spot-check.sql           — Sample data comparison queries
```

### Step 5: EXECUTE — Run Migration (With Approval)

```
⚠️  EXECUTION PHASE — This will modify the TARGET database.
    Source database remains READ-ONLY.

Proceed with migration to {target}? [Y/N]: >
```

**IF approved:**

```
Step 5.1: Create target database (if needed)
  createdb {dbname} / CREATE DATABASE {dbname}

Step 5.2: Apply schema
  psql -d {dbname} -f .migration/schema/target-schema.sql

Step 5.3: Migrate data
  IF pgloader: pgloader .migration/config/pgloader.conf
  IF dump: Import transformed dump
  IF ETL: Run migration script

Step 5.4: Apply post-migration fixes
  - Reset sequences (PostgreSQL)
  - VACUUM ANALYZE (PostgreSQL)
  - Optimize tables (MySQL)

Step 5.5: Apply application code patches
  Display each patch, ask for confirmation before applying
```

### Step 6: VERIFY — Validate Migration

```
Running verification suite...

-------------------------------------------------------------
VERIFICATION REPORT
-------------------------------------------------------------

| Check | Status | Details |
|-------|--------|---------|
| Row counts match | {PASS/FAIL} | {N}/{N} tables match |
| Sequences correct | {PASS/FAIL} | {N}/{N} sequences aligned |
| Foreign keys valid | {PASS/FAIL} | {N}/{N} constraints hold |
| Indexes created | {PASS/FAIL} | {N}/{N} indexes exist |
| Sample data matches | {PASS/FAIL} | {N}/{N} spot checks pass |
| App connects | {PASS/FAIL} | Connection test result |
| Basic queries work | {PASS/FAIL} | SELECT/INSERT/UPDATE/DELETE |

-------------------------------------------------------------
VERDICT: {MIGRATION COMPLETE | ISSUES FOUND}
-------------------------------------------------------------

{If issues found:}
  Issue 1: {description}
    Fix: {recommended action}

  Issue 2: {description}
    Fix: {recommended action}

{If all pass:}
  Migration from {source_type} to {target_type} is COMPLETE.

  Next steps:
    1. Update .env with new connection string
    2. Run application test suite
    3. Remove .migration/ directory when satisfied
    4. Update deployment configs
```

---

## Safety Guarantees

```
ENFORCED throughout migration:

  1. Source is READ-ONLY — no writes to source database ever
  2. No execution without explicit user approval at Step 5
  3. plan-only mode available for assessment without risk
  4. All generated SQL shown before execution
  5. Rollback guidance provided (target can be dropped, source unchanged)
  6. Connection strings are NEVER logged or committed to files
     — .migration/config/connection.env uses placeholders
  7. Patches shown before application to source code
```

---

## Supported Migration Directions

| Direction | Skill Used | Tool Support |
|-----------|-----------|-------------|
| MySQL → PostgreSQL | `mysql-to-pg-migration` | pgloader (recommended) |
| SQLite → PostgreSQL | `sqlite-to-pg-migration` | pgloader or Python ETL |
| PostgreSQL → MySQL | `pg-to-mysql-schema-migration-methodology` | Manual + sql-compat.js patterns |
| PostgreSQL → SQLite | `data-type-mapping-reference` + `sql-dialect-compatibility-matrix` | Manual (downgrade path — generic skills only) |
| MySQL → SQLite | `data-type-mapping-reference` + `sql-dialect-compatibility-matrix` | Manual (downgrade path — generic skills only) |
| Any → Any | `sql-dialect-compatibility-matrix` | Translation rules |

**Note:** Downgrade paths (→ SQLite) use generic translation skills only — no direction-specific guide exists because SQLite-as-target is rare. The compatibility matrix and type mapping reference provide sufficient coverage.

**ORM-aware migrations** use `orm-schema-portability` to handle migration table continuity (knex_migrations, _prisma_migrations, etc.).

---

## Integration with fire-resurrect

When `/fire-resurrect` reaches Phase 2 (DATABASE), it can delegate to this command:

```
IF database_strategy == CLONE:
  Run /fire-migrate-database with:
    --source {source project database}
    --target {target project database}
    --direction auto-detect

IF database_strategy == REUSE:
  Skip migration — point target at existing database

IF database_strategy == FRESH:
  Skip migration — create schema from INTENT.md
```

---

## Examples

```bash
# Interactive wizard — answers questions, builds plan
/fire-migrate-database

# MySQL to PostgreSQL with connection strings
/fire-migrate-database mysql-to-pg \
  --source "mysql://root:pass@localhost/myapp" \
  --target "postgresql://user:pass@localhost/myapp_pg"

# SQLite prototype to PostgreSQL production
/fire-migrate-database sqlite-to-pg --source ./dev.sqlite

# Assessment only — see what would break, no execution
/fire-migrate-database --source C:/Projects/my-app --target plan-only

# Reverse direction (less common)
/fire-migrate-database pg-to-mysql --source "postgresql://..." --target "mysql://..."
```

---

## Success Criteria

- [ ] Source database type auto-detected or specified
- [ ] Target database type selected
- [ ] Correct skill(s) loaded based on migration direction
- [ ] Schema audit identifies all breaking changes with severity
- [ ] Application code changes enumerated with file/line references
- [ ] ORM migration state continuity addressed
- [ ] Migration plan generated with all phases
- [ ] plan-only mode stops after plan generation (no execution)
- [ ] Migration artifacts created in .migration/ directory
- [ ] Execution requires explicit user approval
- [ ] Source database never modified
- [ ] Verification queries confirm data integrity
- [ ] Connection strings use placeholders (never logged)

---

*Dominion Flow v12.8 — Database migrations with the knowledge of 516 skills and the caution of a production DBA.*
