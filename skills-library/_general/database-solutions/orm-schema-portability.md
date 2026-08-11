---
name: orm-schema-portability
category: database-solutions
version: 1.0.0
contributed: 2026-03-10
contributor: research
last_updated: 2026-03-10
tags: [orm, prisma, knex, drizzle, typeorm, sequelize, django, portability, migration]
difficulty: medium
---

# ORM Schema Portability

## Problem

Developers assume ORMs abstract away database differences. They don't. Every ORM leaks dialect-specific behavior for arrays, enums, JSON querying, full-text search, and migrations. Switching databases after building on ORM-specific features requires significant rework that isn't obvious until migration day.
## ORM Portability Comparison

| Dimension | Prisma | Knex.js | Drizzle | TypeORM | Sequelize | Django |
|---|---|---|---|---|---|---|
| **Schema portability** | Single provider | N/A (query builder) | Separate per dialect | Mostly portable | Mostly portable | Fully portable |
| **Migration portability** | None (SQL files) | Partial (schema builder) | None (dialect SQL) | Partial (auto-gen) | Low | High (Python) |
| **Array support** | PG only | N/A | Dialect-specific | PG only | PG only | PG only |
| **JSON support** | PG, MySQL (recent SQLite) | N/A | Dialect-specific | All (simple-json) | PG, MySQL, SQLite | All (since 3.1) |
| **Enum support** | PG, MySQL | N/A | Dialect-specific | PG, MySQL | PG, MySQL, SQLite | All (CharField) |
| **Raw SQL portability** | None | None | Param only | None | None | Partial |
| **Switching effort** | **High** | **Medium** | **Very High** | **Medium** | **Medium** | **Low** |
| **Best for multi-DB** | No | Yes | No | Moderate | Moderate | **Yes** |

## Per-ORM Details

### Prisma — Single Provider, No Switching

**What it abstracts:** CRUD, relations, connection pooling, type generation.

**What breaks when switching:**
- Schema is inherently single-provider (`provider = "postgresql"` in schema.prisma)
- No `provider = "universal"` — community request since 2020, still unresolved
- Enum, JSON, scalar list support varies by provider
- Migrations generate provider-specific SQL — not reusable across databases
- `$queryRaw` uses `$1` for PG, `?` for MySQL — dialect-dependent

**Portable pattern:** Maintain separate schema files per provider. Share application code.

### Knex.js — Best JS/TS Option for Portability

**What it abstracts:** Query building, schema builder DDL, connection pooling, parameter binding.

**What breaks when switching:**
- SQLite's limited ALTER TABLE (Knex emulates with temp table + copy)
- `RETURNING` is PG/SQLite only
- `knex.raw()` completely kills portability
- Result shape differs by dialect (`{ rows: [...] }` vs `[[...], fields]`)
- LIMIT/OFFSET string values accepted by PG, rejected by MySQL

**Portable pattern:** Use schema builder API exclusively. Avoid `knex.raw()`. Coerce LIMIT/OFFSET to integers.

**MINISTRY-LMS approach:** Knex migrations with conditional DDL:
```javascript
const isPostgres = knex.client.config.client === 'pg';
if (isPostgres) {
  table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
  table.jsonb('settings');
} else {
  table.uuid('id').primary();
  table.json('settings');
}
```

### Drizzle — Intentionally Non-Portable

**What it abstracts:** Type-safe query building, relational queries, driver adapters.

**What breaks when switching:**
- **Schema definitions are NOT portable.** Separate imports: `pgTable`, `mysqlTable`, `sqliteTable`
- Column types differ per dialect (e.g., `serial` in PG vs `int` + `autoIncrement` in MySQL)
- Migrations generate dialect-specific SQL

**Why it's designed this way:** Drizzle is "SQL with types" — it deliberately exposes dialect differences for maximum control and type safety. The trade-off is zero cross-dialect portability.

**Portable pattern:** Share column definitions via spread syntax; rewrite table definitions per dialect.

### TypeORM — Moderate Portability

**What it abstracts:** Entity decorators map to appropriate types, repository pattern, QueryBuilder.

**What breaks when switching:**
- `array: true` is PG/CockroachDB only
- `jsonb` is PG only; MySQL uses `json`; SQLite stores as text
- `unsigned` modifier is MySQL only
- Enum+Array combination is problematic on PG
- `@CreateDateColumn` precision differs

**Portable pattern:** Use `simple-array`, `simple-json`, `simple-enum` types (stored as strings). Avoid native types.

### Sequelize — Moderate Portability

**What it abstracts:** Model definition, query interface, associations, transactions.

**What breaks when switching:**
- `DataTypes.ARRAY` is PG only
- `DataTypes.JSONB` is PG only
- `CITEXT` is PG/SQLite only
- ENUM storage differs (PG: CREATE TYPE, MySQL: inline, SQLite: CHECK)
- v7 moved dialects to separate packages (breaking change from v6)

**Portable pattern:** Stick to `DataTypes.STRING`, `INTEGER`, `BOOLEAN`, `DATE`, `JSON` (not JSONB), `TEXT`.

### Django — Most Portable

**What it abstracts:** Model definitions, QuerySet API, migration framework, admin interface.

**What breaks when switching:**
- `ArrayField` is PG only (`django.contrib.postgres`)
- `HStoreField` is PG only
- Full-text search (`SearchVector`, `SearchRank`) is PG only
- Range fields are PG only

**Portable pattern:** Avoid `django.contrib.postgres`. Use `JSONField` (cross-DB since 3.1). Use `CharField(choices=...)` instead of custom ENUM types.

**Why Django wins:** Python-based migrations (not raw SQL) are inherently backend-agnostic. `%s` parameter placeholders are translated internally by Django.

## The Safest Portable Subset

These ORM types work identically across PG, MySQL, SQLite with zero translation in ANY ORM:

```
string / VARCHAR(n)     — where n ≤ 255
integer / INT           — signed 32-bit
float / DOUBLE          — 8-byte floating point
boolean / BOOLEAN       — true/false (ORM handles TINYINT mapping)
text / TEXT             — unlimited string
timestamp / DATETIME    — ORM handles dialect differences
uuid-as-string / CHAR(36) — generate in app code
json-as-text / JSON     — basic JSON (no JSONB indexing)
```

**Avoid for portability:** Arrays, JSONB, native ENUM, range types, full-text search, geometric types, HSTORE.

## Decision Matrix: Choosing an ORM for Multi-DB

| If you need... | Use... | Why |
|---|---|---|
| Maximum portability (Python) | **Django** | Python migrations, internal param translation |
| Maximum portability (JS/TS) | **Knex.js** | Query builder, not ORM — minimal abstraction leak |
| Type safety over portability | **Drizzle** | Explicit dialect awareness, best TypeScript DX |
| Quick prototyping | **Prisma** | Best DX, but locked to one provider |
| Legacy enterprise | **TypeORM** or **Sequelize** | Broad dialect support, mature ecosystem |

## Migration State Continuity

When rebuilding an app (e.g., `/fire-resurrect`), the ORM's migration tracking table lives IN the database:

| ORM | Migration Table | What It Tracks |
|---|---|---|
| Prisma | `_prisma_migrations` | Applied migration names + timestamps |
| Knex | `knex_migrations` | Batch number + migration name |
| Sequelize | `SequelizeMeta` | Migration filenames |
| TypeORM | `migrations` | Timestamp + name |
| Django | `django_migrations` | App + name + applied timestamp |

**Key insight:** If you point a new project at an existing database with the same migration files, the ORM knows which migrations have already run. No re-creation, no data loss.

**For "reuse" strategy in fire-resurrect:** Copy migration files to new project → point at existing DB → `migrate:latest` runs only NEW migrations.

## When to Use

- Choosing an ORM for a new multi-database project
- Auditing existing ORM schema for portability issues before migration
- Planning the VISION phase of `/fire-resurrect` with `--migrate`
- Understanding why a database switch broke application code

## When NOT to Use

- Single-database projects with no migration plans
- Raw SQL projects (use sql-dialect-compatibility-matrix instead)
- NoSQL ORMs (Mongoose, etc.)

## Related Skills

- [sql-dialect-compatibility-matrix](sql-dialect-compatibility-matrix.md)
- [data-type-mapping-reference](data-type-mapping-reference.md)
- [pg-to-mysql-schema-migration-methodology](pg-to-mysql-schema-migration-methodology.md)

## References

- Prisma multiple database support limitations (issue #1487)
- Bytebase — "Drizzle vs Prisma" (2026)
- TheDataGuy — "Node.js ORMs in 2025" (Dec 2025)
- MINISTRY-LMS Knex migration patterns (production-proven, 2026)
- Django ORM comparison (Paolo Melchiorre, 2025)
- Drizzle ORM schema declaration docs
- Sequelize v7 dialect-specific documentation
