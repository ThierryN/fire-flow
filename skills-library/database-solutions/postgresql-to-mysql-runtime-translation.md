---
name: postgresql-to-mysql-runtime-translation
category: database-solutions
version: 2.0.0
contributed: 2026-02-20
contributor: ministry-lms
last_updated: 2026-03-06
tags: [postgresql, mysql, mariadb, sql-translation, migration, runtime, knex, mern]
difficulty: hard
usage_count: 0
success_rate: 100
---

# PostgreSQL to MySQL Runtime SQL Translation Layer

## Problem

Migrating a large application from PostgreSQL to MySQL/MariaDB is not just a schema migration. The application code contains thousands of PG-specific SQL patterns embedded in queries: type casts (`::text`), `RETURNING` clauses, `ON CONFLICT ... DO UPDATE`, `ILIKE`, `json_agg()`, `gen_random_uuid()`, interval arithmetic, `DATE_TRUNC()`, and more.

Rewriting every query in the application is impractical for a 709K-line codebase. A **runtime translation layer** intercepts SQL before it hits the database and rewrites PG syntax to MySQL syntax, allowing gradual migration without touching every file.

**Scale of the problem:** A scan of MINISTRY-LMS found 2,639 PG-specific patterns across the server code:
- 671 RETURNING clauses
- 659 type casts (::text, ::int, etc.)
- 281 gen_random_uuid() calls
- 280 ON CONFLICT clauses
- 185 INTERVAL expressions
- 179 FILTER (WHERE) clauses
- 161 ILIKE operators
- 157 JSON operators (->>, #>>)

## Solution Pattern

Build a **sql-compat.js** middleware that sits between the application's database calls and the actual database driver. It intercepts every query, applies a chain of regex-based translations, and forwards the rewritten SQL to MySQL via Knex.

**Architecture:**
```
Application Code (PG syntax)
       |
   sql-compat.js (translation layer)
       |
   Knex Query Builder (MySQL driver)
       |
   MySQL/MariaDB
```

**Key design decisions:**
1. **Intercept at the tagged template level** -- PostgreSQL's `postgres.js` uses tagged template syntax. The compat layer mimics this API.
2. **Translation chain order matters** -- Some translations must run before others (e.g., strip type casts before parsing function calls).
3. **RETURNING handled via separate SELECT** -- MySQL doesn't support RETURNING; execute the INSERT/UPDATE, then SELECT the affected rows.
4. **Use depth-tracking for nested functions** -- Regex `[^)]+` fails on nested parens; use a parenthesis-counting loop.

## Code Example

```javascript
// sql-compat.js -- Core translation function (20+ rules)
function translateToMySQL(sql) {
  let s = sql;

  // 1. Strip PG type casts (longest first!)
  s = s.replace(/::(timestamptz|timestamp|date|time|text|varchar|integer|int|bigint|boolean|bool|numeric|decimal|float|double precision|json|jsonb|uuid|bytea|smallint|real|regclass|oid|interval)/gi, '');

  // 2. gen_random_uuid() -> UUID()
  s = s.replace(/\bgen_random_uuid\(\)/gi, 'UUID()');

  // 3. ILIKE -> LIKE (MySQL is case-insensitive by default with ci collation)
  s = s.replace(/\bILIKE\b/gi, 'LIKE');

  // 4. || string concat -> CONCAT()
  // (careful: don't touch || inside quotes)
  s = s.replace(/(\w+(?:\.\w+)?)\s*\|\|\s*('[^']*'|\w+(?:\.\w+)?)/g, 'CONCAT($1, $2)');

  // 5. NOW() + INTERVAL '7 days' -> DATE_ADD(NOW(), INTERVAL 7 DAY)
  s = s.replace(/(\w+)\s*\+\s*INTERVAL\s+'(\d+)\s+(\w+)'/gi,
    (_, expr, num, unit) => `DATE_ADD(${expr}, INTERVAL ${num} ${unit.replace(/s$/i, '')})`);

  // 6. NOW() - INTERVAL -> DATE_SUB
  s = s.replace(/(\w+)\s*-\s*INTERVAL\s+'(\d+)\s+(\w+)'/gi,
    (_, expr, num, unit) => `DATE_SUB(${expr}, INTERVAL ${num} ${unit.replace(/s$/i, '')})`);

  // 7. DATE_TRUNC('month', col) -> DATE_FORMAT(col, '%Y-%m-01')
  s = translateDateTrunc(s);

  // 8. ON CONFLICT ... DO UPDATE -> ON DUPLICATE KEY UPDATE
  s = translateOnConflict(s);

  // 9. RETURNING clause -> strip (handled separately)
  s = s.replace(/\s+RETURNING\s+.*/gi, '');

  // 10. json_agg/array_agg -> GROUP_CONCAT wrapper (MariaDB 10.4)
  s = replaceAggFunc(s, 'json_agg');
  s = replaceAggFunc(s, 'array_agg');

  // 11. json_build_object -> JSON_OBJECT
  s = s.replace(/\bjson_build_object\s*\(/gi, 'JSON_OBJECT(');

  // 12. COALESCE with jsonb default -> COALESCE with JSON string
  s = s.replace(/'(\[\])'/g, "'$1'");

  // 13. Boolean literals
  s = s.replace(/\btrue\b/gi, '1');
  s = s.replace(/\bfalse\b/gi, '0');

  // 14. EXTRACT(EPOCH FROM ...) -> UNIX_TIMESTAMP(...)
  s = s.replace(/EXTRACT\s*\(\s*EPOCH\s+FROM\s+(\w+)\s*\)/gi, 'UNIX_TIMESTAMP($1)');

  // 15. Double-quoted identifiers -> backticks
  s = translateQuotedIdentifiers(s);

  // ... more rules as needed

  return s;
}
```

## Implementation Steps

1. **Audit the codebase** -- Run a scanner to find all PG-specific patterns and their frequency
2. **Create the translation function** -- Start with the top 5 most frequent patterns
3. **Wire into the database layer** -- Replace the PG driver import with the compat layer
4. **Test endpoint by endpoint** -- Hit each API route and verify the translated SQL works
5. **Handle RETURNING separately** -- After INSERT/UPDATE, run a SELECT to get affected rows
6. **Add depth-tracking** for any function replacement (not just regex)
7. **Order translations carefully** -- Type cast stripping must happen before function translation

## The 20+ Translation Rules (Priority Order)

| # | PG Pattern | MySQL Equivalent | Frequency |
|---|-----------|-----------------|-----------|
| 1 | `::type` casts | Strip entirely | 659 |
| 2 | `RETURNING *` | Separate SELECT after INSERT/UPDATE | 671 |
| 3 | `gen_random_uuid()` | `UUID()` | 281 |
| 4 | `ON CONFLICT ... DO UPDATE` | `ON DUPLICATE KEY UPDATE` | 280 |
| 5 | `+ INTERVAL '7 days'` | `DATE_ADD(..., INTERVAL 7 DAY)` | 185 |
| 6 | `FILTER (WHERE ...)` | `CASE WHEN ... THEN ... END` inside aggregate | 179 |
| 7 | `ILIKE` | `LIKE` (with ci collation) | 161 |
| 8 | `->>`/`#>>` JSON | `JSON_UNQUOTE(JSON_EXTRACT(...))` | 157 |
| 9 | `json_agg()` | `CONCAT('[', GROUP_CONCAT(...), ']')` | ~50 |
| 10 | `array_agg()` | `CONCAT('[', GROUP_CONCAT(...), ']')` | ~30 |
| 11 | `DATE_TRUNC('unit', col)` | `DATE_FORMAT(col, pattern)` | ~40 |
| 12 | `string \|\| string` | `CONCAT(a, b)` | ~30 |
| 13 | Boolean `true`/`false` | `1`/`0` | ~100 |
| 14 | `EXTRACT(EPOCH FROM)` | `UNIX_TIMESTAMP()` | ~10 |
| 15 | `json_build_object()` | `JSON_OBJECT()` | ~20 |
| 16 | `to_jsonb(expr)` | `JSON_QUOTE(expr)` | ~5 |
| 17 | `TO_CHAR(date, fmt)` | `DATE_FORMAT(date, fmt)` | ~20 |
| 18 | `split_part(str, d, n)` | `SUBSTRING_INDEX()` nesting | ~10 |
| 19 | `NULLS LAST/FIRST` | Strip (MySQL default) | ~15 |
| 20 | `LATERAL` | Strip keyword | ~5 |
| 21 | Full-text `@@` search | `LIKE '%term%'` fallback | ~10 |

## When to Use

- Migrating a large application from PostgreSQL to MySQL/MariaDB
- When rewriting every query is impractical (1000+ queries)
- As a temporary bridge during gradual migration
- When the application uses raw SQL (not just ORM/query builder)
- For cPanel shared hosting where only MySQL is available

## When NOT to Use

- New applications (use the target database from the start)
- When the application uses only ORM-generated queries (ORM handles dialect)
- When PostgreSQL-specific features are core to the architecture (PostGIS, full-text search, CTEs heavily)
- For high-performance systems where translation overhead matters

## Runtime Compatibility Fixes (v2.0 — March 2026)

These critical fixes address **driver-level behavioral differences** between PostgreSQL's `pg` driver and MySQL's `mysql2`/`knex`. They are not SQL syntax translations — they fix how JavaScript values are handled by the drivers.

### Fix 1: Undefined → Null Binding Conversion

**Problem:** PostgreSQL's `pg` driver silently converts `undefined` JavaScript values to `NULL`. MySQL's `mysql2` driver throws: `"Undefined binding(s) detected for keys [5, 19]"`. This surfaces in any INSERT/UPDATE with optional fields.

**Root cause:** Application code passes `undefined` for optional parameters (e.g., `req.body.tribute_name` when not provided). PG tolerates this; MySQL rejects it.

**Solution:** Convert `undefined → null` systemically in the compat layer — both in the tagged template parser and the `unsafe()` method:

```javascript
// In tagged template parser (_parseTemplate):
else {
  sql += '?';
  let safeVal = value === undefined ? null : value;
  // ... (also handle object serialization, see Fix 2)
  params.push(safeVal);
}

// In unsafe() method:
async unsafe(query, values = []) {
  const safeValues = values.map(v => v === undefined ? null : v);
  // ... rest of method uses safeValues
}
```

**Why systemic > per-call:** There are hundreds of INSERT/UPDATE calls across 32 plugins. Fixing each caller is impractical. The compat layer is the single chokepoint.

### Fix 2: Object Auto-Serialization for JSON Columns

**Problem:** PostgreSQL's `pg` driver auto-serializes JavaScript objects to `jsonb` columns. MySQL's `mysql2` driver passes the raw object, which fails or produces `[object Object]`.

**Solution:** In the tagged template parser, detect objects/arrays and JSON.stringify() them:

```javascript
// In _parseTemplate, after undefined→null conversion:
if (safeVal !== null && typeof safeVal === 'object' && !Array.isArray(safeVal) && !(safeVal instanceof Date)) {
  safeVal = JSON.stringify(safeVal);
} else if (Array.isArray(safeVal)) {
  safeVal = JSON.stringify(safeVal);
}
params.push(safeVal);
```

**Date exclusion:** `Date` objects must NOT be stringified — MySQL expects them as Date objects for DATETIME columns.

### Fix 3: 4-Strategy RETURNING Emulation

**Problem:** PostgreSQL's `RETURNING *` returns the affected row(s) after INSERT/UPDATE/DELETE. MySQL has no equivalent.

**Solution:** Strip RETURNING from the SQL, execute the mutation, then re-SELECT the affected row using one of 4 strategies (tried in order):

| Strategy | Trigger | Method |
|----------|---------|--------|
| 1. UUID lookup | INSERT has `id` column with UUID value | `SELECT * FROM table WHERE id = ?` using the UUID from params |
| 2. Unique key | ON DUPLICATE KEY UPDATE present | `SELECT * FROM table WHERE first_col = ? LIMIT 1` |
| 3. LAST_INSERT_ID | Auto-increment table | `SELECT LAST_INSERT_ID()` then lookup |
| 4. Most recent | Fallback (has `created_at`) | `SELECT * FROM table ORDER BY created_at DESC LIMIT 1` |

For UPDATE: extract the WHERE clause and params, re-SELECT with the same WHERE.

### Fix 4: JSON Column Auto-Parsing on Read

**Problem:** PostgreSQL returns `jsonb` columns as parsed JavaScript objects. MySQL returns them as JSON strings (`'{"key":"value"}'`).

**Solution:** After every MySQL query result, auto-parse string values that look like JSON:

```javascript
_parseJSONColumns(rows) {
  return rows.map(row => {
    const parsed = { ...row };
    for (const key in parsed) {
      const val = parsed[key];
      if (typeof val === 'string' && val.length > 1) {
        const first = val[0];
        if (first === '{' || first === '[') {
          try { parsed[key] = JSON.parse(val); } catch (e) {}
        }
      }
    }
    return parsed;
  });
}
```

## Common Mistakes

- Regex alternation ordering (see companion skill: regex-alternation-ordering-sql-types)
- Simple `[^)]+` for function argument matching (see: mariadb-aggregate-function-replacement)
- Forgetting that RETURNING needs a separate SELECT (can't just strip it)
- Not killing stale processes after code changes (old code keeps running on the same port)
- Quoting reserved words without context awareness (see: reserved-word-context-aware-quoting)
- **Forgetting to exclude Date objects** from JSON serialization — MySQL needs Date objects for DATETIME columns
- **Fixing undefined→null per-call** instead of systemically — there are too many call sites
- **Not auto-parsing JSON on read** — causes `Object.entries()` to iterate character-by-character (see: POSTGRESQL_JSONB_DOUBLE_STRINGIFY_FIX)

## Companion Tool: pg2mysql

A complete Python tool was built alongside this pattern:
- **Location:** `C:\path\to\repos\pg2mysql\`
- **Commands:** `migrate` (full migration), `schema` (DDL only), `scan` (find PG patterns), `translate` (convert single query)
- **Scan report:** Found 2,639 PG-specific patterns in MINISTRY-LMS

## Related Skills

- [regex-alternation-ordering-sql-types](regex-alternation-ordering-sql-types.md) - Critical regex bug pattern
- [mariadb-aggregate-function-replacement](mariadb-aggregate-function-replacement.md) - Aggregate function translation
- [reserved-word-context-aware-quoting](reserved-word-context-aware-quoting.md) - Safe reserved word handling
- [KNEX_DATABASE_ABSTRACTION](../deployment-security/KNEX_DATABASE_ABSTRACTION.md) - Knex as the MySQL driver
- [CONDITIONAL_SQL_MIGRATION_PATTERN](CONDITIONAL_SQL_MIGRATION_PATTERN.md) - Schema migration patterns

## References

- PostgreSQL to MySQL compatibility: https://dev.mysql.com/doc/refman/8.0/en/sql-function-reference.html
- MariaDB 10.4 function reference: https://mariadb.com/kb/en/built-in-functions/
- Discovered during: MINISTRY-LMS migration from Supabase PostgreSQL to XAMPP MariaDB 10.4
- Files: `server/database/sql-compat.js`, `C:\path\to\repos\pg2mysql\`
- Contributed from: ministry-lms
