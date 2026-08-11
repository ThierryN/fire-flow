---
name: sql-ddl-generator
category: database-solutions
version: 1.0.0
contributed: 2026-03-09
contributor: fire-research
tags: [sql, ddl, postgresql, mysql, sqlite, code-generation, database, schema, migration]
difficulty: medium
usage_count: 0
success_rate: 100
---

# SQL DDL Generator


## Problem

You need to generate correct, dialect-specific SQL DDL (Data Definition Language) from a schema model. Each database engine has different syntax for auto-increment, UUIDs, booleans, JSON, and constraints. Manually writing DDL for multiple targets is error-prone and repetitive — especially when converting between dialects or maintaining parallel schemas for PostgreSQL (production) and SQLite (testing).

## CREATE DATABASE Template

```sql
-- PostgreSQL
CREATE DATABASE university_system
  WITH ENCODING = 'UTF8'
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       TEMPLATE = template0;

-- MySQL
CREATE DATABASE IF NOT EXISTS university_system
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- SQLite (databases are just files)
-- No CREATE DATABASE — open/create with: sqlite3 university_system.db
```

## CREATE TABLE Template

Full annotated template showing every DDL element:

```sql
CREATE TABLE table_name (
  -- Column definitions: name  type  [column_constraints]
  column_name    DATA_TYPE    [NOT NULL] [DEFAULT value] [UNIQUE] [CHECK (expr)]
                              [PRIMARY KEY]
                              [REFERENCES other_table(column) [ON DELETE action] [ON UPDATE action]],

  -- More columns...
  another_col    DATA_TYPE    NOT NULL DEFAULT 'value',

  -- Table-level constraints (named, reusable, shown in error messages)
  CONSTRAINT pk_table          PRIMARY KEY (column_name),
  CONSTRAINT fk_table_other    FOREIGN KEY (other_id) REFERENCES other_table(id)
                               ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT uq_table_email    UNIQUE (email),
  CONSTRAINT ck_table_age      CHECK (age >= 0 AND age <= 150),

  -- Composite constraints
  CONSTRAINT uq_table_compound UNIQUE (org_id, slug),
  CONSTRAINT pk_junction       PRIMARY KEY (left_id, right_id)
);
```

**Rule of thumb:** Use table-level (named) constraints for anything you will reference in error handling, migration rollbacks, or documentation. Use inline constraints for simple NOT NULL / DEFAULT on single columns.

## Column Constraints Reference

| Constraint | Syntax | Example | Notes |
|-----------|--------|---------|-------|
| NOT NULL | `col TYPE NOT NULL` | `email VARCHAR(255) NOT NULL` | Rejects NULL inserts/updates |
| DEFAULT | `col TYPE DEFAULT val` | `status VARCHAR(20) DEFAULT 'draft'` | Value when column omitted |
| UNIQUE | `col TYPE UNIQUE` | `slug VARCHAR(100) UNIQUE` | Creates unique index |
| CHECK | `col TYPE CHECK (expr)` | `age INT CHECK (age >= 0)` | Row-level validation |
| PRIMARY KEY | `col TYPE PRIMARY KEY` | `id SERIAL PRIMARY KEY` | Inline PK (single column only) |
| REFERENCES | `col TYPE REFERENCES tbl(col)` | `user_id INT REFERENCES users(id)` | Inline FK |

**DEFAULT value types:**
```sql
DEFAULT 'string_literal'          -- text
DEFAULT 0                         -- numeric
DEFAULT TRUE                      -- boolean (PG); DEFAULT 1 (MySQL)
DEFAULT CURRENT_TIMESTAMP         -- all dialects
DEFAULT (UUID())                  -- MySQL 8+
DEFAULT gen_random_uuid()         -- PostgreSQL 13+
```

## Table Constraints Reference

### PRIMARY KEY
```sql
-- Single column
CONSTRAINT pk_users PRIMARY KEY (id)

-- Composite (junction tables)
CONSTRAINT pk_enrollment PRIMARY KEY (student_id, course_id)
```

### FOREIGN KEY
```sql
CONSTRAINT fk_tasks_project FOREIGN KEY (project_id)
  REFERENCES projects(id)
  ON DELETE CASCADE        -- delete children when parent deleted
  ON UPDATE CASCADE        -- update FK when parent PK changes

-- ON DELETE options:
--   CASCADE    — delete child rows
--   SET NULL   — set FK column to NULL (column must be nullable)
--   SET DEFAULT — set FK to its DEFAULT value
--   RESTRICT   — block delete if children exist (checked immediately)
--   NO ACTION  — block delete if children exist (checked at txn end, default)
```

### UNIQUE
```sql
-- Single column
CONSTRAINT uq_users_email UNIQUE (email)

-- Composite (e.g., unique slug per organization)
CONSTRAINT uq_posts_org_slug UNIQUE (organization_id, slug)
```

### CHECK
```sql
CONSTRAINT ck_products_price CHECK (price >= 0)
CONSTRAINT ck_users_role CHECK (role IN ('admin', 'instructor', 'student'))
CONSTRAINT ck_events_dates CHECK (end_date > start_date)
```

### Naming Conventions

| Prefix | Constraint Type | Example |
|--------|----------------|---------|
| `pk_` | Primary Key | `pk_users` |
| `fk_` | Foreign Key | `fk_tasks_project` |
| `uq_` | Unique | `uq_users_email` |
| `ck_` | Check | `ck_products_price` |
| `idx_` | Index | `idx_tasks_status_created` |

Pattern: `{prefix}_{table}_{column(s)}` — keeps constraint names deterministic and greppable.

## Data Type Cross-Reference

| Concept | PostgreSQL | MySQL | SQLite | MSSQL |
|---------|-----------|-------|--------|-------|
| Auto-increment PK | `SERIAL` / `BIGSERIAL` | `INT AUTO_INCREMENT` | `INTEGER PRIMARY KEY` | `INT IDENTITY(1,1)` |
| UUID PK | `UUID DEFAULT gen_random_uuid()` | `CHAR(36) DEFAULT (UUID())` | `TEXT` | `UNIQUEIDENTIFIER DEFAULT NEWID()` |
| Short text | `VARCHAR(n)` | `VARCHAR(n)` | `TEXT` | `NVARCHAR(n)` |
| Long text | `TEXT` | `TEXT` / `LONGTEXT` | `TEXT` | `NVARCHAR(MAX)` |
| Integer | `INTEGER` | `INT` | `INTEGER` | `INT` |
| Big integer | `BIGINT` | `BIGINT` | `INTEGER` | `BIGINT` |
| Small integer | `SMALLINT` | `SMALLINT` | `INTEGER` | `SMALLINT` |
| Decimal | `NUMERIC(p,s)` | `DECIMAL(p,s)` | `REAL` | `DECIMAL(p,s)` |
| Float | `DOUBLE PRECISION` | `DOUBLE` | `REAL` | `FLOAT` |
| Boolean | `BOOLEAN` | `TINYINT(1)` | `INTEGER` (0/1) | `BIT` |
| Date | `DATE` | `DATE` | `TEXT` (ISO 8601) | `DATE` |
| Time | `TIME` | `TIME` | `TEXT` | `TIME` |
| Timestamp (tz) | `TIMESTAMPTZ` | `DATETIME` | `TEXT` (ISO 8601) | `DATETIMEOFFSET` |
| Timestamp (no tz) | `TIMESTAMP` | `DATETIME` | `TEXT` | `DATETIME2` |
| JSON | `JSONB` | `JSON` | `TEXT` | `NVARCHAR(MAX)` |
| Binary | `BYTEA` | `BLOB` / `LONGBLOB` | `BLOB` | `VARBINARY(MAX)` |
| Array | `TYPE[]` (native) | `JSON` (workaround) | `TEXT` (JSON) | `NVARCHAR(MAX)` (JSON) |
| Enum | `CREATE TYPE ... AS ENUM` | `ENUM('a','b','c')` | `TEXT + CHECK` | `NVARCHAR + CHECK` |

**Critical gotcha (from MINISTRY-LMS migration):** MySQL `CHAR(36) DEFAULT (UUID())` returns `LAST_INSERT_ID() = 0` because MySQL only tracks auto-increment IDs. When using UUID PKs in MySQL, generate the UUID in application code and include `id` in the INSERT column list. See skill: `pg-to-mysql-schema-migration-methodology.md`.

## Dialect-Specific Syntax

### PostgreSQL

```sql
-- Auto-increment (preferred: IDENTITY in PG 10+)
CREATE TABLE users (
  id    INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  -- or legacy: id SERIAL PRIMARY KEY
  name  VARCHAR(100) NOT NULL
);

-- UUID primary key
CREATE TABLE documents (
  id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title      TEXT NOT NULL,
  metadata   JSONB DEFAULT '{}',
  tags       TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Generated/computed columns (PG 12+)
ALTER TABLE products ADD COLUMN
  search_vector TSVECTOR GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
  ) STORED;

-- Partial index
CREATE INDEX idx_tasks_active ON tasks (status) WHERE deleted_at IS NULL;

-- ENUM type
CREATE TYPE user_role AS ENUM ('admin', 'instructor', 'student');
CREATE TABLE users (
  id   SERIAL PRIMARY KEY,
  role user_role NOT NULL DEFAULT 'student'
);
```

### MySQL

```sql
-- Auto-increment
CREATE TABLE users (
  id    INT AUTO_INCREMENT PRIMARY KEY,
  name  VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- UUID primary key (generate in app code, not DEFAULT)
CREATE TABLE documents (
  id         CHAR(36) NOT NULL PRIMARY KEY,
  title      TEXT NOT NULL,
  metadata   JSON DEFAULT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Boolean (stored as TINYINT)
ALTER TABLE users ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1;

-- Inline ENUM
CREATE TABLE tasks (
  id     INT AUTO_INCREMENT PRIMARY KEY,
  status ENUM('draft', 'active', 'done') NOT NULL DEFAULT 'draft'
);

-- Full-text index
ALTER TABLE articles ADD FULLTEXT INDEX ft_articles_content (title, body);

-- IMPORTANT: Always specify ENGINE=InnoDB for FK support
-- IMPORTANT: Use utf8mb4 (not utf8) — utf8 is only 3 bytes, misses emoji
```

### SQLite

```sql
-- Auto-increment (INTEGER PRIMARY KEY is implicit rowid alias)
CREATE TABLE users (
  id    INTEGER PRIMARY KEY,  -- auto-increments automatically
  name  TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE
);

-- AUTOINCREMENT keyword (prevents rowid reuse, slightly slower)
CREATE TABLE audit_log (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  action  TEXT NOT NULL,
  ts      TEXT DEFAULT (datetime('now'))
);

-- Type affinity: SQLite stores any type in any column
-- These declarations are hints, not enforced:
--   TEXT, INTEGER, REAL, BLOB, NUMERIC

-- Boolean emulation
CREATE TABLE tasks (
  id        INTEGER PRIMARY KEY,
  is_done   INTEGER NOT NULL DEFAULT 0 CHECK (is_done IN (0, 1))
);

-- Date/time as ISO 8601 text
CREATE TABLE events (
  id         INTEGER PRIMARY KEY,
  start_date TEXT NOT NULL,  -- '2026-03-09'
  created_at TEXT DEFAULT (datetime('now'))
);

-- FK enforcement (OFF by default!)
PRAGMA foreign_keys = ON;
```

## Generated DDL Example

A complete `university_system` schema with multiple tables, foreign keys, and constraints:

```sql
-- ============================================================
-- University System DDL — PostgreSQL dialect
-- ============================================================

CREATE TABLE departments (
  id           SERIAL PRIMARY KEY,
  name         VARCHAR(100) NOT NULL,
  code         CHAR(4) NOT NULL,
  budget       NUMERIC(12, 2) DEFAULT 0.00,
  created_at   TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT uq_departments_code  UNIQUE (code),
  CONSTRAINT ck_departments_budget CHECK (budget >= 0)
);

CREATE TABLE instructors (
  id             SERIAL PRIMARY KEY,
  department_id  INT NOT NULL,
  first_name     VARCHAR(50) NOT NULL,
  last_name      VARCHAR(50) NOT NULL,
  email          VARCHAR(255) NOT NULL,
  hire_date      DATE NOT NULL DEFAULT CURRENT_DATE,

  CONSTRAINT fk_instructors_department FOREIGN KEY (department_id)
    REFERENCES departments(id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT uq_instructors_email UNIQUE (email)
);

CREATE TABLE courses (
  id              SERIAL PRIMARY KEY,
  department_id   INT NOT NULL,
  instructor_id   INT,
  code            VARCHAR(10) NOT NULL,
  title           VARCHAR(200) NOT NULL,
  credits         SMALLINT NOT NULL DEFAULT 3,
  max_enrollment  INT NOT NULL DEFAULT 30,
  description     TEXT,
  is_active       BOOLEAN NOT NULL DEFAULT TRUE,

  CONSTRAINT fk_courses_department FOREIGN KEY (department_id)
    REFERENCES departments(id) ON DELETE RESTRICT,
  CONSTRAINT fk_courses_instructor FOREIGN KEY (instructor_id)
    REFERENCES instructors(id) ON DELETE SET NULL,
  CONSTRAINT uq_courses_code UNIQUE (code),
  CONSTRAINT ck_courses_credits CHECK (credits BETWEEN 1 AND 6),
  CONSTRAINT ck_courses_enrollment CHECK (max_enrollment > 0)
);

CREATE TABLE students (
  id           SERIAL PRIMARY KEY,
  first_name   VARCHAR(50) NOT NULL,
  last_name    VARCHAR(50) NOT NULL,
  email        VARCHAR(255) NOT NULL,
  gpa          NUMERIC(3, 2) DEFAULT 0.00,
  enrolled_at  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT uq_students_email UNIQUE (email),
  CONSTRAINT ck_students_gpa CHECK (gpa >= 0.00 AND gpa <= 4.00)
);

CREATE TABLE enrollments (
  student_id   INT NOT NULL,
  course_id    INT NOT NULL,
  enrolled_at  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  grade        CHAR(2),

  CONSTRAINT pk_enrollments PRIMARY KEY (student_id, course_id),
  CONSTRAINT fk_enrollments_student FOREIGN KEY (student_id)
    REFERENCES students(id) ON DELETE CASCADE,
  CONSTRAINT fk_enrollments_course FOREIGN KEY (course_id)
    REFERENCES courses(id) ON DELETE CASCADE,
  CONSTRAINT ck_enrollments_grade CHECK (
    grade IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F', 'W', 'I')
  )
);

-- Indexes for common queries
CREATE INDEX idx_instructors_department ON instructors (department_id);
CREATE INDEX idx_courses_department ON courses (department_id);
CREATE INDEX idx_courses_instructor ON courses (instructor_id);
CREATE INDEX idx_enrollments_course ON enrollments (course_id);
CREATE INDEX idx_students_email ON students (email);
```

## AI-Assisted Dialect Conversion

When you need to convert DDL between dialects, use an LLM prompt template based on ChartDB's approach (schema as structured JSON, LLM generates target dialect):

### Prompt Template

```
You are a SQL DDL expert. Convert the following {source_dialect} DDL
to valid {target_dialect} DDL.

Rules:
1. Map data types using standard equivalents (SERIAL → AUTO_INCREMENT, etc.)
2. Preserve all constraints with equivalent syntax
3. Preserve all naming conventions (pk_, fk_, uq_, ck_ prefixes)
4. Add dialect-specific requirements (ENGINE=InnoDB for MySQL, PRAGMA for SQLite)
5. Comment any features that have NO equivalent in the target dialect
6. For UUID columns in MySQL: add a comment noting app-side generation is required

Source DDL ({source_dialect}):
```sql
{paste_ddl_here}
```

Generate the equivalent {target_dialect} DDL.
```

### ChartDB's JSON Schema Approach

ChartDB feeds the schema as structured JSON to an AI agent, which generates dialect-specific DDL. This is more reliable than raw SQL→SQL conversion because the intermediate representation is unambiguous:

```json
{
  "tables": [
    {
      "name": "users",
      "columns": [
        { "name": "id", "type": "auto_increment_pk" },
        { "name": "email", "type": "varchar", "length": 255, "nullable": false, "unique": true },
        { "name": "created_at", "type": "timestamp_tz", "default": "now" }
      ],
      "constraints": [
        { "type": "pk", "columns": ["id"], "name": "pk_users" }
      ]
    }
  ],
  "target_dialect": "mysql"
}
```

### dbdiagram.io DBML as Intermediate DSL

DBML (Database Markup Language) is a human-readable intermediate format. Write once, export to any dialect:

```dbml
Table users {
  id int [pk, increment]
  email varchar(255) [not null, unique]
  role user_role [not null, default: 'student']
  created_at timestamptz [default: `CURRENT_TIMESTAMP`]
}

Table courses {
  id int [pk, increment]
  instructor_id int [ref: > users.id]
  title varchar(200) [not null]
  credits smallint [not null, default: 3]
}

Enum user_role {
  admin
  instructor
  student
}
```

## Migration Generation Patterns

### Knex.js Migration (from quick-erd pattern)

```javascript
// migrations/20260309_create_users.js
export async function up(knex) {
  await knex.schema.createTable('users', (table) => {
    table.increments('id').primary();
    table.string('email', 255).notNullable().unique();
    table.string('first_name', 50).notNullable();
    table.string('last_name', 50).notNullable();
    table.decimal('gpa', 3, 2).defaultTo(0.00);
    table.timestamp('created_at').defaultTo(knex.fn.now());
  });

  await knex.schema.createTable('enrollments', (table) => {
    table.integer('student_id').unsigned().notNullable();
    table.integer('course_id').unsigned().notNullable();
    table.string('grade', 2);
    table.timestamp('enrolled_at').defaultTo(knex.fn.now());

    table.primary(['student_id', 'course_id']);
    table.foreign('student_id').references('users.id').onDelete('CASCADE');
    table.foreign('course_id').references('courses.id').onDelete('CASCADE');
  });
}

export async function down(knex) {
  await knex.schema.dropTableIfExists('enrollments');
  await knex.schema.dropTableIfExists('users');
}
```

### Raw SQL Migration (ERFlow checkpoint pattern)

```sql
-- migrations/V001__create_users.sql
-- Up
CREATE TABLE IF NOT EXISTS users (
  id    SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  name  VARCHAR(100) NOT NULL
);

-- migrations/V001__create_users_down.sql
-- Down
DROP TABLE IF EXISTS users;
```

### Drizzle Schema (TypeScript-first)

```typescript
// schema/users.ts
import { pgTable, serial, varchar, timestamp, boolean } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id:        serial('id').primaryKey(),
  email:     varchar('email', { length: 255 }).notNull().unique(),
  firstName: varchar('first_name', { length: 50 }).notNull(),
  lastName:  varchar('last_name', { length: 50 }).notNull(),
  isActive:  boolean('is_active').notNull().default(true),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
});
```

### Idempotent ALTER Migration (MySQL safe pattern)

From MINISTRY-LMS lessons — always check before adding columns to prevent "column already exists" crashes on re-run:

```javascript
async function addColumnIfMissing(knex, table, column, alterSQL) {
  const [rows] = await knex.raw(`DESCRIBE \`${table}\``);
  const exists = rows.some((r) => r.Field === column);
  if (!exists) {
    await knex.raw(alterSQL);
    console.log(`  Added ${table}.${column}`);
  }
}

// Usage in migration
export async function up(knex) {
  await addColumnIfMissing(
    knex, 'users', 'avatar_url',
    "ALTER TABLE `users` ADD COLUMN `avatar_url` VARCHAR(500) DEFAULT NULL"
  );
}
```

## Implementation: Multi-Dialect DDL Generator

A TypeScript generator function that takes a dialect-agnostic schema model and outputs DDL for any target. Based on DrawDB's separate-generator-per-dialect pattern:

```typescript
// ddl-generator.ts

type Dialect = 'postgresql' | 'mysql' | 'sqlite' | 'mssql';

interface Column {
  name: string;
  type: string;          // abstract type: 'auto_pk', 'uuid_pk', 'varchar', 'text', 'int', 'decimal', 'boolean', 'date', 'timestamptz', 'jsonb'
  length?: number;       // for varchar
  precision?: number;    // for decimal
  scale?: number;        // for decimal
  nullable?: boolean;    // default: true
  unique?: boolean;
  default?: string | number | boolean | null;
  check?: string;        // raw SQL expression
}

interface Constraint {
  type: 'pk' | 'fk' | 'unique' | 'check';
  name: string;
  columns: string[];
  // FK-specific
  refTable?: string;
  refColumns?: string[];
  onDelete?: 'CASCADE' | 'SET NULL' | 'RESTRICT' | 'NO ACTION' | 'SET DEFAULT';
  onUpdate?: 'CASCADE' | 'SET NULL' | 'RESTRICT' | 'NO ACTION' | 'SET DEFAULT';
  // CHECK-specific
  expression?: string;
}

interface TableDef {
  name: string;
  columns: Column[];
  constraints: Constraint[];
}

// Data type mapping
const TYPE_MAP: Record<string, Record<Dialect, string>> = {
  auto_pk:     { postgresql: 'SERIAL',          mysql: 'INT AUTO_INCREMENT',  sqlite: 'INTEGER',  mssql: 'INT IDENTITY(1,1)' },
  uuid_pk:     { postgresql: 'UUID DEFAULT gen_random_uuid()', mysql: 'CHAR(36)', sqlite: 'TEXT', mssql: 'UNIQUEIDENTIFIER DEFAULT NEWID()' },
  varchar:     { postgresql: 'VARCHAR',         mysql: 'VARCHAR',             sqlite: 'TEXT',     mssql: 'NVARCHAR' },
  text:        { postgresql: 'TEXT',            mysql: 'TEXT',                sqlite: 'TEXT',     mssql: 'NVARCHAR(MAX)' },
  int:         { postgresql: 'INTEGER',         mysql: 'INT',                sqlite: 'INTEGER',  mssql: 'INT' },
  bigint:      { postgresql: 'BIGINT',          mysql: 'BIGINT',             sqlite: 'INTEGER',  mssql: 'BIGINT' },
  decimal:     { postgresql: 'NUMERIC',         mysql: 'DECIMAL',            sqlite: 'REAL',     mssql: 'DECIMAL' },
  boolean:     { postgresql: 'BOOLEAN',         mysql: 'TINYINT(1)',         sqlite: 'INTEGER',  mssql: 'BIT' },
  date:        { postgresql: 'DATE',            mysql: 'DATE',               sqlite: 'TEXT',     mssql: 'DATE' },
  timestamptz: { postgresql: 'TIMESTAMPTZ',     mysql: 'DATETIME',           sqlite: 'TEXT',     mssql: 'DATETIMEOFFSET' },
  jsonb:       { postgresql: 'JSONB',           mysql: 'JSON',               sqlite: 'TEXT',     mssql: 'NVARCHAR(MAX)' },
};

function resolveType(col: Column, dialect: Dialect): string {
  const base = TYPE_MAP[col.type]?.[dialect] ?? col.type.toUpperCase();

  // Append length/precision
  if (col.type === 'varchar' && col.length && dialect !== 'sqlite') {
    return `${base}(${col.length})`;
  }
  if (col.type === 'decimal' && col.precision) {
    if (dialect === 'sqlite') return 'REAL';
    return `${base}(${col.precision},${col.scale ?? 0})`;
  }
  return base;
}

function generateColumnDDL(col: Column, dialect: Dialect): string {
  const parts: string[] = [col.name, resolveType(col, dialect)];

  // auto_pk columns get PK inline for SQLite
  if (col.type === 'auto_pk' && dialect === 'sqlite') {
    return `${col.name} INTEGER PRIMARY KEY`;
  }

  if (col.nullable === false) parts.push('NOT NULL');
  if (col.unique) parts.push('UNIQUE');

  if (col.default !== undefined && col.default !== null) {
    if (typeof col.default === 'string' && col.default.startsWith('$RAW:')) {
      parts.push(`DEFAULT ${col.default.slice(5)}`);
    } else if (typeof col.default === 'string') {
      parts.push(`DEFAULT '${col.default}'`);
    } else if (typeof col.default === 'boolean') {
      parts.push(`DEFAULT ${dialect === 'mysql' ? (col.default ? '1' : '0') : col.default}`);
    } else {
      parts.push(`DEFAULT ${col.default}`);
    }
  }

  if (col.check) parts.push(`CHECK (${col.check})`);

  return parts.join(' ');
}

function generateConstraintDDL(c: Constraint): string {
  switch (c.type) {
    case 'pk':
      return `CONSTRAINT ${c.name} PRIMARY KEY (${c.columns.join(', ')})`;
    case 'fk':
      return [
        `CONSTRAINT ${c.name} FOREIGN KEY (${c.columns.join(', ')})`,
        `  REFERENCES ${c.refTable}(${c.refColumns!.join(', ')})`,
        c.onDelete ? `  ON DELETE ${c.onDelete}` : '',
        c.onUpdate ? `  ON UPDATE ${c.onUpdate}` : '',
      ].filter(Boolean).join('\n    ');
    case 'unique':
      return `CONSTRAINT ${c.name} UNIQUE (${c.columns.join(', ')})`;
    case 'check':
      return `CONSTRAINT ${c.name} CHECK (${c.expression})`;
    default:
      return `-- Unknown constraint type: ${c.type}`;
  }
}

export function generateDDL(tables: TableDef[], dialect: Dialect): string {
  const output: string[] = [];

  // SQLite foreign key pragma
  if (dialect === 'sqlite') {
    output.push('PRAGMA foreign_keys = ON;\n');
  }

  for (const table of tables) {
    const lines: string[] = [];

    for (const col of table.columns) {
      lines.push(`  ${generateColumnDDL(col, dialect)}`);
    }

    for (const constraint of table.constraints) {
      // Skip inline PK for auto_pk in SQLite (already handled)
      if (constraint.type === 'pk' && dialect === 'sqlite'
          && constraint.columns.length === 1
          && table.columns.find(c => c.name === constraint.columns[0])?.type === 'auto_pk') {
        continue;
      }
      lines.push(`  ${generateConstraintDDL(constraint)}`);
    }

    let createStmt = `CREATE TABLE ${table.name} (\n${lines.join(',\n')}\n)`;

    // MySQL table options
    if (dialect === 'mysql') {
      createStmt += ' ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci';
    }

    output.push(`${createStmt};\n`);
  }

  return output.join('\n');
}

// ---- Usage Example ----
const schema: TableDef[] = [
  {
    name: 'users',
    columns: [
      { name: 'id', type: 'auto_pk' },
      { name: 'email', type: 'varchar', length: 255, nullable: false, unique: true },
      { name: 'name', type: 'varchar', length: 100, nullable: false },
      { name: 'is_active', type: 'boolean', nullable: false, default: true },
      { name: 'created_at', type: 'timestamptz', default: '$RAW:CURRENT_TIMESTAMP' },
    ],
    constraints: [
      { type: 'pk', name: 'pk_users', columns: ['id'] },
    ],
  },
];

// Generate for each dialect
for (const dialect of ['postgresql', 'mysql', 'sqlite'] as Dialect[]) {
  console.log(`-- ===== ${dialect.toUpperCase()} =====`);
  console.log(generateDDL(schema, dialect));
}
```

## OSS Tools Reference

| Tool | What It Does | Use When |
|------|-------------|----------|
| **node-sql-parser** | Parse SQL → AST, `sqlify(ast)` back to SQL. Supports PG, MySQL, SQLite, MSSQL. | You need programmatic SQL manipulation or dialect conversion at the AST level |
| **sql-ddl-to-json-schema** | Parse DDL into JSON Schema using nearley grammar. Extensible for custom dialects. | You need to extract a machine-readable schema from existing DDL |
| **quick-erd** | Generate Knex migrations + TypeScript types from an ERD model. | Rapid prototyping — go from diagram to running migrations in minutes |
| **ChartDB** | AI agent converts DDL between dialects by feeding schema JSON to an LLM. | One-off dialect conversions where precision matters more than automation |
| **ERFlow** | Checkpoint-based migration generation for PG, MySQL, Laravel, Phinx. | When you need versioned migrations alongside your schema design tool |
| **DrawDB** | Visual ERD designer with separate code generator per dialect. | Non-technical stakeholders need to see/edit the schema visually |
| **dbdiagram.io** | DBML DSL for defining schemas, exports to multiple SQL dialects. | Quick schema documentation and sharing with a team |

## When to Use

- Generating CREATE TABLE statements for a new feature
- Converting DDL from PostgreSQL to MySQL (or vice versa) during a migration
- Creating Knex/Drizzle/Prisma migrations from a design document
- Building a code generator that outputs DDL for multiple database targets
- Teaching/documenting SQL DDL syntax and constraint naming conventions

## When NOT to Use

- Schema already exists and you only need to ALTER it — use the migration pattern directly
- You are using an ORM that generates DDL from models (Prisma, TypeORM) — define in the ORM, not raw DDL
- Performance tuning (indexes, partitioning, tablespaces) — that is a separate concern from DDL generation
- For runtime SQL translation between dialects — see `postgresql-to-mysql-runtime-translation.md`

## Related Skills

- `database-schema-designer.md` — full schema design process from requirements to migrations
- `postgresql-to-mysql-runtime-translation.md` — runtime SQL rewriting for dialect portability
- `pg-to-mysql-schema-migration-methodology.md` — battle-tested migration methodology
- `mysql-limit-offset-string-coercion.md` — MySQL LIMIT/OFFSET string handling
- `reserved-word-context-aware-quoting.md` — identifier quoting across dialects
- `erd-creator-textbook-research.md` — ERD design fundamentals

## References

- LibreTexts "Database Design" — CREATE DATABASE, CREATE TABLE, constraint syntax
- DrawDB GitHub — separate generator per dialect pattern
- ChartDB GitHub — AI-assisted schema-to-DDL via JSON intermediate
- ERFlow — checkpoint migration generation (PG, MySQL, Laravel, Phinx)
- dbdiagram.io — DBML DSL specification
- node-sql-parser npm — AST-based SQL parsing and generation
- sql-ddl-to-json-schema npm — nearley grammar DDL parser
- quick-erd npm — ERD → Knex + TypeScript generation
- MINISTRY-LMS migration logs — real-world PG→MySQL DDL conversion lessons
