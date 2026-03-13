---
name: regex-alternation-ordering-sql-types
category: database-solutions
version: 1.0.0
contributed: 2026-02-20
contributor: ministry-lms
last_updated: 2026-02-20
tags: [regex, postgresql, mysql, type-casting, mariadb, sql-translation]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Regex Alternation Ordering for SQL Type Casts

## Problem

When stripping PostgreSQL type casts (e.g., `::timestamp`, `::timestamptz`) using regex alternation, shorter prefixes match before longer ones, leaving residual characters. This causes silent data corruption that is extremely hard to debug.

**Symptom:** `NULL::timestamptz` becomes `NULLtz` instead of `NULL`. No error thrown -- the `tz` residue silently passes through to MySQL, causing downstream failures or corrupted data.

**Error message (downstream):**
```
Unknown column 'NULLtz' in 'field list'
```
or simply wrong data in results with no error at all.

## Solution Pattern

**Always order regex alternation from longest match to shortest.** When multiple alternatives share a common prefix, the longer one must come first. Regex engines try alternatives left-to-right and stop at the first match.

This is a universal regex principle but is especially dangerous in SQL translation layers where partial matches produce valid-looking but semantically wrong output.

## Code Example

```javascript
// BEFORE (buggy) -- timestamp matches before timestamptz gets a chance
s = s.replace(/::(timestamp|timestamptz|date|time)/gi, '');
// Input:  "NULL::timestamptz"
// Match:  "::timestamp" (first alternative matches)
// Output: "NULLtz"  <-- WRONG

// AFTER (fixed) -- longest prefix first
s = s.replace(/::(timestamptz|timestamp|date|time)/gi, '');
// Input:  "NULL::timestamptz"
// Match:  "::timestamptz" (first alternative matches the full word)
// Output: "NULL"  <-- CORRECT
```

## Implementation Steps

1. Identify all regex alternation groups that strip or translate SQL tokens
2. Sort alternatives by length (longest first) within each group
3. Test with the longest variant of each prefix group (e.g., `timestamptz` not just `timestamp`)

## When to Use

- Building SQL dialect translation layers (PG -> MySQL, PG -> SQLite, etc.)
- Stripping type casts, function names, or keywords with regex
- Any regex alternation where alternatives share a common prefix
- Runtime SQL rewriting in middleware or compat layers

## When NOT to Use

- When alternatives don't share prefixes (no risk of partial match)
- When using a proper SQL parser (AST-based) instead of regex -- parsers handle this correctly
- Single-alternative replacements (no alternation involved)

## Common Mistakes

- Alphabetically ordering alternatives (`date|time|timestamp|timestamptz`) -- this guarantees the bug
- Not testing with the longest variant of shared-prefix groups
- Assuming the regex engine will "prefer" a longer match -- it won't; it takes the first match left-to-right

## The Debugging Trap

This bug is uniquely hard to find because:
- No error is thrown at the translation layer
- The residue (`tz`) looks like a typo, not a regex bug
- The failure appears at the database layer, far from the regex code
- Adding debug logging at the regex shows the wrong match but you must know to look there

## Related Skills

- [KNEX_DATABASE_ABSTRACTION](../deployment-security/KNEX_DATABASE_ABSTRACTION.md) - Database abstraction layer
- [CONDITIONAL_SQL_MIGRATION_PATTERN](CONDITIONAL_SQL_MIGRATION_PATTERN.md) - Safe SQL migration patterns

## References

- Discovered during: MINISTRY-LMS PostgreSQL to MySQL migration
- File: `server/database/sql-compat.js` line 76
- Contributed from: ministry-lms
