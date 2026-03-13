---
name: mariadb-aggregate-function-replacement
category: database-solutions
version: 1.0.0
contributed: 2026-02-20
contributor: ministry-lms
last_updated: 2026-02-20
tags: [mariadb, mysql, json_arrayagg, group_concat, aggregate, sql-translation, nested-parentheses]
difficulty: hard
usage_count: 0
success_rate: 100
---

# MariaDB 10.4 Aggregate Function Replacement with Depth-Tracking

## Problem

MariaDB 10.4 does not support `JSON_ARRAYAGG()` (added in 10.5+). When translating PostgreSQL `json_agg()` or `array_agg()` to MariaDB, a naive regex replacement to `JSON_ARRAYAGG()` fails silently on MariaDB 10.4.

Additionally, simple regex like `json_agg\(([^)]+)\)` **cannot handle nested function calls** inside the aggregate. For example: `json_agg(JSON_OBJECT('month', DATE_FORMAT(...)))` -- the `[^)]+` pattern stops at the first `)` inside `DATE_FORMAT`, breaking the translation.

**Error message:**
```
FUNCTION ministry_lms.JSON_ARRAYAGG does not exist
```

## Solution Pattern

Replace aggregate functions using a **parenthesis-depth-tracking loop** instead of regex. Walk the string character by character, counting open/close parentheses to find the correct closing paren. Then wrap with the MariaDB-compatible equivalent: `CONCAT('[', IFNULL(GROUP_CONCAT(...), ''), ']')`.

This produces valid JSON arrays using only features available in MariaDB 10.4.

## Code Example

```javascript
// BEFORE (broken) -- simple regex fails on nested parens
s = s.replace(/\bjson_agg\(([^)]+)\)/gi, "JSON_ARRAYAGG($1)");
// Fails: JSON_ARRAYAGG not in MariaDB 10.4
// Also fails: nested parens like json_agg(JSON_OBJECT('k', func(x)))

// AFTER (working) -- depth-tracking function
function replaceAggFunc(sql, funcName) {
  const re = new RegExp('\\b' + funcName + '\\s*\\(', 'gi');
  let match;
  let result = sql;
  const matches = [];

  // Collect all match positions first
  while ((match = re.exec(sql)) !== null) {
    matches.push(match.index);
  }

  // Process from end to start (so indices stay valid)
  for (let i = matches.length - 1; i >= 0; i--) {
    const startIdx = matches[i];
    const parenStart = result.indexOf('(', startIdx);
    if (parenStart === -1) continue;

    // Depth-tracking: find the matching close paren
    let depth = 1;
    let pos = parenStart + 1;
    while (pos < result.length && depth > 0) {
      if (result[pos] === '(') depth++;
      else if (result[pos] === ')') depth--;
      pos++;
    }
    if (depth !== 0) continue; // unbalanced -- skip

    const innerContent = result.substring(parenStart + 1, pos - 1);
    const replacement = `CONCAT('[', IFNULL(GROUP_CONCAT(${innerContent}), ''), ']')`;
    result = result.substring(0, startIdx) + replacement + result.substring(pos);
  }
  return result;
}

// Usage in translation layer:
s = replaceAggFunc(s, 'json_agg');
s = replaceAggFunc(s, 'array_agg');
```

```python
# Python equivalent for pg2mysql tool:
def _replace_agg_func(self, sql: str, func_name: str) -> str:
    pattern = re.compile(r'\b' + re.escape(func_name) + r'\s*\(', re.IGNORECASE)
    positions = [m.start() for m in pattern.finditer(sql)]
    result = sql
    for start_idx in reversed(positions):
        paren_start = result.index('(', start_idx)
        depth, pos = 1, paren_start + 1
        while pos < len(result) and depth > 0:
            if result[pos] == '(': depth += 1
            elif result[pos] == ')': depth -= 1
            pos += 1
        if depth != 0: continue
        inner = result[paren_start + 1:pos - 1]
        replacement = f"CONCAT('[', IFNULL(GROUP_CONCAT({inner}), ''), ']')"
        result = result[:start_idx] + replacement + result[pos:]
    return result
```

## Implementation Steps

1. Identify all aggregate functions that need MariaDB 10.4 compatibility (`json_agg`, `array_agg`, `json_arrayagg`)
2. Implement `replaceAggFunc()` with depth-tracking (not regex)
3. Process matches from END to START so string indices remain valid after each replacement
4. Wrap inner content with `CONCAT('[', IFNULL(GROUP_CONCAT(...), ''), ']')`
5. Test with nested function calls: `json_agg(JSON_OBJECT('k', DATE_FORMAT(col, '%Y')))`

## When to Use

- Targeting MariaDB 10.4 or earlier (before JSON_ARRAYAGG support)
- Translating PostgreSQL json_agg/array_agg to MySQL/MariaDB
- Any SQL function replacement where arguments may contain nested function calls
- Runtime SQL translation layers where the inner expression is arbitrary

## When NOT to Use

- MariaDB 10.5+ or MySQL 8.0+ (these support JSON_ARRAYAGG natively)
- When using an AST-based SQL parser (handles nesting correctly by design)
- When aggregate arguments are always simple column references (regex would work)

## Common Mistakes

- Using `[^)]+` regex to match function arguments -- breaks on any nested call
- Processing matches front-to-back instead of back-to-front (invalidates string indices)
- Forgetting `IFNULL(..., '')` -- GROUP_CONCAT returns NULL for empty sets, producing `CONCAT('[', NULL, ']')` = `NULL`
- Not escaping the function name in the regex pattern

## Why GROUP_CONCAT Works

MariaDB's `GROUP_CONCAT()` has been available since early versions. It concatenates values with a separator (default `,`). Combined with `CONCAT('[', ..., ']')`, it produces valid JSON arrays. The `IFNULL` wrapper handles the empty-set case where GROUP_CONCAT returns NULL.

**Limitation:** GROUP_CONCAT has a default max length of 1024 bytes (`group_concat_max_len`). For large result sets, you may need `SET SESSION group_concat_max_len = 1000000;`.

## Related Skills

- [regex-alternation-ordering-sql-types](regex-alternation-ordering-sql-types.md) - Companion skill for type cast translation
- [KNEX_DATABASE_ABSTRACTION](../deployment-security/KNEX_DATABASE_ABSTRACTION.md) - Database abstraction patterns

## References

- MariaDB 10.5 changelog: JSON_ARRAYAGG added
- Discovered during: MINISTRY-LMS PostgreSQL to MySQL migration
- File: `server/database/sql-compat.js`, `replaceAggFunc()` function
- Contributed from: ministry-lms
