---
name: sql-injection-prevention-postgresjs
category: security
version: 1.0.0
contributed: 2026-02-19
contributor: my-other-project
last_updated: 2026-02-19
tags: [sql-injection, postgres.js, security, dynamic-queries, input-validation]
difficulty: medium
usage_count: 0
success_rate: 100
---

# SQL Injection Prevention for postgres.js

## Problem

When using postgres.js (`postgres` npm package) with dynamic queries, two common patterns introduce SQL injection:

1. **Dynamic column names in UPDATE** — Using `sql.unsafe()` with `Object.keys(userInput)` concatenated into the query. An attacker passing `"name; DROP TABLE profiles;--"` as a field key achieves injection.

2. **Dynamic ORDER BY from query params** — Passing `?sort=name;DROP TABLE profiles` directly into `ORDER BY ${sort}` in a template string fed to `sql.unsafe()`.

Both bypass postgres.js tagged template literal protection because column/table names can't be parameterized in standard SQL.

### Symptoms
- `sql.unsafe()` calls with string concatenation
- `Object.keys()` from request body used in SQL
- `req.query.sort` passed directly to ORDER BY
- Any raw string interpolation in SQL queries

## Solution Pattern

### Pattern 1: Column Whitelist for Dynamic UPDATE

Replace `sql.unsafe()` with postgres.js `sql()` helper and a Set-based whitelist:

```javascript
// BEFORE (VULNERABLE)
export const updateUser = async (id, updateData) => {
  const fields = Object.keys(updateData);
  const sets = fields.map((f, i) => `${f} = $${i + 1}`).join(', ');
  const values = fields.map(f => updateData[f]);
  const result = await sql.unsafe(
    `UPDATE profiles SET ${sets} WHERE id = $${fields.length + 1} RETURNING *`,
    [...values, id]
  );
  return result[0];
};

// AFTER (SAFE)
const ALLOWED_COLUMNS = new Set([
  'name', 'email', 'bio', 'website', 'location', 'skills',
  'role', 'avatar_url', 'phone', 'full_name', 'dark_mode'
]);

export const updateUser = async (id, updateData) => {
  const safeData = {};
  for (const [key, val] of Object.entries(updateData)) {
    if (ALLOWED_COLUMNS.has(key)) safeData[key] = val;
  }
  if (Object.keys(safeData).length === 0) return null;

  // postgres.js sql() helper safely handles dynamic columns
  const result = await sql`
    UPDATE profiles SET ${sql(safeData, ...Object.keys(safeData))}
    WHERE id = ${id} RETURNING *
  `;
  return result[0];
};
```

### Pattern 2: sanitizeSort() for Dynamic ORDER BY

Create a reusable utility that validates sort input against a whitelist:

```javascript
// server/middleware/inputValidation.js
export const sanitizeSort = (sortInput, allowedColumns, defaultSort = 'created_at DESC') => {
  if (!sortInput || typeof sortInput !== 'string') return defaultSort;
  const parts = sortInput.trim().split(/\s+/);
  const column = parts[0].replace(/^[a-z]+\./i, ''); // Strip table prefix
  const direction = (parts[1] || 'ASC').toUpperCase();
  if (!allowedColumns.includes(column)) return defaultSort;
  if (direction !== 'ASC' && direction !== 'DESC') return defaultSort;
  // Preserve original table prefix if present (e.g., "p.created_at")
  const prefix = sortInput.trim().match(/^([a-z]+\.)/i)?.[1] || '';
  return `${prefix}${column} ${direction}`;
};
```

Usage in models:

```javascript
import { sanitizeSort } from '../middleware/inputValidation.js';

const ALLOWED_SORT = ['created_at', 'name', 'email', 'role', 'updated_at'];

export const getUsers = async (options = {}) => {
  const validSort = sanitizeSort(options.sort, ALLOWED_SORT);
  const limit = Number(options.limit) || 20;
  const offset = Number(options.offset) || 0;

  // validSort is guaranteed safe — use in sql.unsafe for ORDER BY only
  const result = await sql.unsafe(
    `SELECT * FROM profiles ORDER BY ${validSort} LIMIT $1 OFFSET $2`,
    [limit, offset]
  );
  return result;
};
```

## Implementation Steps

1. Identify all `sql.unsafe()` calls with string interpolation
2. For UPDATE queries: create column whitelist Set, use `sql()` helper
3. For ORDER BY: create `sanitizeSort()`, define model-specific allowed columns
4. For LIMIT/OFFSET: cast to `Number()` — never interpolate raw strings
5. Test with injection payloads: `name;DROP TABLE x--`, `name UNION SELECT *`

## When to Use

- Any postgres.js project with dynamic UPDATE queries
- Any endpoint accepting `?sort=` query parameters
- Models that build SQL from user-provided field names
- REST APIs with sortable list endpoints

## When NOT to Use

- If using an ORM (Prisma, Sequelize) — they handle parameterization
- Static SQL with no dynamic parts — tagged templates are already safe
- If column names come from trusted server-side code only

## Common Mistakes

- Trusting `Object.keys()` from request body — attackers control key names
- Using `sql.unsafe()` when `sql` tagged template would work
- Forgetting to whitelist new columns after schema changes
- Allowing table prefixes without validation (e.g., `information_schema.columns`)
- Only validating column name but not direction (`ASC`/`DESC`)

## Related Skills

- [POSTGRES_SQL_TEMPLATE_BINDING_ERROR](../database-solutions/POSTGRES_SQL_TEMPLATE_BINDING_ERROR.md) - Template binding issues
- [PRODUCTION_HARDENING_DOCUMENTATION](../deployment-security/PRODUCTION_HARDENING_DOCUMENTATION.md) - General hardening

## References

- postgres.js docs: https://github.com/porsager/postgres#dynamic-columns
- OWASP SQL Injection: https://owasp.org/www-community/attacks/SQL_Injection
- Contributed from: my-other-project (Feb 2026 security audit)
