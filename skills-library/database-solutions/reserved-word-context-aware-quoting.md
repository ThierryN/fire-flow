---
name: reserved-word-context-aware-quoting
category: database-solutions
version: 1.0.0
contributed: 2026-02-20
contributor: pg2mysql
last_updated: 2026-02-20
tags: [mysql, mariadb, reserved-words, sql-translation, quoting, backticks]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Reserved Word Context-Aware Quoting

## Problem

When translating SQL between dialects, MySQL reserved words used as column/table names must be backtick-quoted. However, blindly quoting every occurrence of a reserved word breaks SQL keywords that happen to appear before the reserved word in a syntactic role.

**Example:** `KEY` is a MySQL reserved word. Column named `key` needs quoting: `` `key` ``. But `ON DUPLICATE KEY UPDATE` must NOT become `` ON DUPLICATE `KEY` UPDATE `` -- that's a syntax error.

**Error message:**
```
You have an error in your SQL syntax; check the manual... near '`KEY` UPDATE ...'
```

## Solution Pattern

Maintain a **SAFE_BEFORE** set of SQL keywords that, when found immediately before a reserved word, indicate the reserved word is being used as a SQL keyword (not an identifier). Skip quoting in these contexts.

The key insight: certain keyword combinations are unambiguous. `DUPLICATE KEY`, `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE KEY`, `INDEX KEY` always use `KEY` as a keyword, never as an identifier.

## Code Example

```python
# BEFORE (broken) -- blindly quotes all reserved words
RESERVED = {'KEY', 'STATUS', 'ORDER', 'GROUP', 'INDEX', ...}

def quote_reserved(sql):
    for word in RESERVED:
        sql = re.sub(
            rf'\b{word}\b',
            f'`{word}`',
            sql, flags=re.IGNORECASE
        )
    return sql
# "ON DUPLICATE KEY UPDATE" -> "ON DUPLICATE `KEY` UPDATE"  BROKEN

# AFTER (fixed) -- context-aware quoting
SAFE_BEFORE = {'DUPLICATE', 'PRIMARY', 'FOREIGN', 'UNIQUE', 'INDEX'}

def _quote_reserved_columns(self, sql: str) -> str:
    result = sql
    for word in RESERVED_WORDS:
        pattern = re.compile(
            r'(?<!\w)' + re.escape(word) + r'(?!\w)',
            re.IGNORECASE
        )
        new_result = []
        last_end = 0
        for m in pattern.finditer(result):
            # Look at the word immediately before this match
            before_text = result[:m.start()].rstrip()
            preceding_word = before_text.split()[-1].upper() if before_text.split() else ''

            if preceding_word in SAFE_BEFORE:
                # This is a SQL keyword in context, don't quote
                new_result.append(result[last_end:m.end()])
            else:
                # This is an identifier, quote it
                new_result.append(result[last_end:m.start()])
                new_result.append(f'`{m.group()}`')
            last_end = m.end()
        new_result.append(result[last_end:])
        result = ''.join(new_result)
    return result
```

```javascript
// JavaScript equivalent:
const SAFE_BEFORE = new Set(['DUPLICATE', 'PRIMARY', 'FOREIGN', 'UNIQUE', 'INDEX']);

function quoteReserved(sql, word) {
  const re = new RegExp('(?<!\\w)' + word + '(?!\\w)', 'gi');
  return sql.replace(re, (match, offset) => {
    const before = sql.substring(0, offset).trimEnd();
    const prevWord = before.split(/\s+/).pop().toUpperCase();
    if (SAFE_BEFORE.has(prevWord)) return match; // keyword context
    return '`' + match + '`'; // identifier context
  });
}
```

## Implementation Steps

1. Build a set of MySQL reserved words that commonly appear as column names
2. Build a SAFE_BEFORE set of keywords that indicate syntactic (non-identifier) usage
3. For each reserved word occurrence, check the preceding word
4. If preceding word is in SAFE_BEFORE, skip quoting
5. Otherwise, wrap in backticks

## When to Use

- Building SQL translators that target MySQL/MariaDB
- PostgreSQL to MySQL migration tools (PG uses double-quotes, MySQL uses backticks)
- Any runtime SQL rewriting that needs to protect reserved word columns
- Code generators that produce MySQL DDL or DML

## When NOT to Use

- When using parameterized queries with a query builder (Knex, Sequelize, etc.) -- they handle quoting
- When the SQL is hand-written and you control the column names
- When targeting only PostgreSQL or SQLite (different reserved word lists)

## Common Mistakes

- Only checking for `DUPLICATE` but missing `PRIMARY`, `FOREIGN`, `UNIQUE`, `INDEX`
- Not handling case-insensitive matching (SQL keywords can be any case)
- Quoting inside string literals (`'some KEY value'` should NOT be touched)
- Not accounting for multiple spaces or newlines between the preceding keyword and the reserved word

## SAFE_BEFORE Reference

| Before Word | Context | Example |
|------------|---------|---------|
| DUPLICATE | ON DUPLICATE KEY UPDATE | Upsert syntax |
| PRIMARY | PRIMARY KEY | Table constraint |
| FOREIGN | FOREIGN KEY | Reference constraint |
| UNIQUE | UNIQUE KEY | Unique constraint |
| INDEX | INDEX/KEY | Index definition |

## Related Skills

- [regex-alternation-ordering-sql-types](regex-alternation-ordering-sql-types.md) - Type cast translation
- [mariadb-aggregate-function-replacement](mariadb-aggregate-function-replacement.md) - Aggregate translation

## References

- MySQL Reserved Words: https://dev.mysql.com/doc/refman/8.0/en/keywords.html
- Discovered during: pg2mysql tool development
- File: `pg2mysql/translator.py`, `_quote_reserved_columns()` method
- Contributed from: pg2mysql
