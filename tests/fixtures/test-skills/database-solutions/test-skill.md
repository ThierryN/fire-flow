# Test Database Skill

## Overview

This is a test skill file used for validating Dominion Flow skills functionality. It demonstrates the standard skill file format and contains sample content for testing search, sync, and contribution features.

---

## Keywords

test, database, fixture, validation, postgresql, mysql, sqlite, orm, query

---

## When to Use

- Testing Dominion Flow skills search functionality
- Validating skills library synchronization
- Demonstrating skill file format
- Integration testing of skills features

---

## Prerequisites

- Dominion Flow plugin installed
- Skills library directory exists
- Test environment configured

---

## Steps

### Step 1: Verify Skill Discovery

Ensure this skill can be found using `/fire-search`:

```bash
# In Claude Code session:
/fire-search database

# Expected: This skill should appear in results
```

### Step 2: Validate Skill Format

Check that all required sections are present:

1. Title (H1 heading)
2. Overview section
3. Keywords section
4. When to Use section
5. Steps section

### Step 3: Test Skill Loading

Verify the skill can be read and used in planning:

```bash
# In Claude Code session:
/fire-2-plan 1
# When prompted, reference database setup
# This skill should be identified as relevant
```

---

## Code Examples

### PostgreSQL Connection Test

```typescript
import { Pool } from 'pg';

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'test_db',
  user: 'test_user',
  password: 'test_password'
});

async function testConnection() {
  const client = await pool.connect();
  try {
    const result = await client.query('SELECT NOW()');
    console.log('Connected:', result.rows[0].now);
  } finally {
    client.release();
  }
}
```

### MySQL Query Example

```typescript
import mysql from 'mysql2/promise';

async function queryExample() {
  const connection = await mysql.createConnection({
    host: 'localhost',
    user: 'test',
    database: 'test_db'
  });

  const [rows] = await connection.execute('SELECT * FROM users');
  return rows;
}
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Skill not found | Check keywords match search terms |
| Format validation fails | Ensure all required sections present |
| Sync fails | Verify write permissions to skills directory |

---

## Related Skills

- `database-solutions/prisma-setup.md`
- `database-solutions/mongodb-aggregation.md`
- `patterns-standards/connection-pooling.md`

---

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Prisma Documentation](https://www.prisma.io/docs/)

---

## Metadata

| Field | Value |
|-------|-------|
| Created | 2026-01-22 |
| Author | Dominion Flow Test Suite |
| Version | 1.0.0 |
| Category | database-solutions |
| Status | Test Fixture |
