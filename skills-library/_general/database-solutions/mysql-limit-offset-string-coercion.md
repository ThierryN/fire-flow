---
name: mysql-limit-offset-string-coercion
category: database-solutions
version: 1.0.0
contributed: 2026-03-07
contributor: ministry-lms
last_updated: 2026-03-07
contributors:
  - ministry-lms
tags: [mysql, mariadb, postgresql, limit, offset, pagination, express, req-query, type-coercion]
difficulty: easy
usage_count: 0
success_rate: 100
---

# MySQL LIMIT/OFFSET String Coercion

## Problem

When porting a PostgreSQL application to MySQL, paginated endpoints break with SQL syntax errors. The root cause: Express `req.query` parameters are always strings (`'20'`, not `20`). PostgreSQL silently auto-casts `LIMIT '20'` to `LIMIT 20`. MySQL strictly rejects string values in LIMIT/OFFSET clauses.

**Symptoms:**
- `You have an error in your SQL syntax` on any paginated endpoint
- Works fine in PostgreSQL, breaks in MySQL
- Only affects endpoints that pass `req.query.limit` or `req.query.page` into SQL
- Error appears as `LIMIT '20' OFFSET 0` in the generated SQL

## Solution Pattern

Fix this **systemically** in the SQL compatibility/translation layer, not per-controller. Any runtime SQL translation layer that converts PG queries to MySQL should coerce LIMIT/OFFSET values from strings to integers before query execution.

**Why systemic:** Fixing in every controller/model is fragile — each new paginated endpoint would need the same fix. One fix in the SQL layer covers all endpoints, past and future.

## Code Example

```javascript
// Before (broken on MySQL)
// req.query.limit = '20' (string from Express)
const result = await sql`
  SELECT * FROM meetings
  ORDER BY created_at DESC
  LIMIT ${limit} OFFSET ${offset}
`;
// Generated SQL: SELECT * FROM meetings ORDER BY created_at DESC LIMIT '20' OFFSET 0
// MySQL error: You have an error in your SQL syntax

// After (works on both PG and MySQL)
// Option A: Fix in SQL compatibility layer (RECOMMENDED — one fix for all endpoints)
// In the template literal parser, detect LIMIT/OFFSET context and coerce to int:
const precedingSQL = sql.trimEnd().toUpperCase();
if (typeof value === 'string' && /\b(LIMIT|OFFSET)\s*\??\s*$/.test(precedingSQL)) {
  const parsed = parseInt(value, 10);
  if (!isNaN(parsed)) value = parsed;
}

// Option B: Fix per-controller (NOT recommended — must repeat everywhere)
const limit = parseInt(req.query.limit, 10) || 50;
const offset = parseInt(req.query.page, 10) * limit || 0;
```

## Implementation Steps

1. Locate the SQL template literal parser in your compatibility layer (the function that processes tagged template literals and generates parameterized queries)
2. In the section that handles parameter values, check if the preceding SQL text ends with `LIMIT` or `OFFSET`
3. If the value is a string and the context is LIMIT/OFFSET, coerce it to an integer with `parseInt(value, 10)`
4. Only apply the coercion if `parseInt` produces a valid number (not `NaN`)
5. Restart the server and test any paginated endpoint

## When to Use

- Porting a PostgreSQL Express app to MySQL/MariaDB
- Building a SQL compatibility layer between PG and MySQL
- Any scenario where `req.query` values pass through to LIMIT/OFFSET in MySQL
- When you see `LIMIT '20'` style errors in MySQL logs

## When NOT to Use

- If your app already uses an ORM (Prisma, Sequelize, Knex) that handles type coercion
- If you're only targeting PostgreSQL (PG handles this automatically)
- If LIMIT/OFFSET values come from validated/parsed sources (not raw req.query)
- If you're using prepared statements where the driver handles type binding

## Common Mistakes

- Fixing in individual controllers instead of the SQL layer (fragile, doesn't scale)
- Using `Number()` instead of `parseInt()` (Number('') returns 0, parseInt('') returns NaN — different edge cases)
- Forgetting OFFSET (same issue as LIMIT — both need coercion)
- Not checking for NaN before coercing (could turn invalid input into NaN parameter)
- Assuming `req.query` values are numbers (they are ALWAYS strings in Express)

## Related Skills

- [pg-to-mysql-schema-migration-methodology](../database-solutions/pg-to-mysql-schema-migration-methodology.md) - Schema-level PG to MySQL migration
- [sql-injection-prevention-postgresjs](../../security/sql-injection-prevention-postgresjs.md) - Safe SQL parameter handling

## References

- MySQL LIMIT syntax: requires integer expressions, not string literals
- Express req.query: all values are strings (parsed from URL query string)
- Discovered during: MINISTRY-LMS PG-to-MySQL migration — meetings endpoint broke with LIMIT '20'
- Fix applied in: `server/database/sql-compat.js` _parseTemplate method
- Contributed from: ministry-lms
