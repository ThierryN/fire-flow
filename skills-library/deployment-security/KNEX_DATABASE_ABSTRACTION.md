# Knex.js Database Abstraction Layer for Multi-DB Support

## Overview
A database abstraction layer using Knex.js that supports both PostgreSQL and MySQL with a unified API. Uses the adapter pattern for database-specific operations.

## Architecture

### Directory Structure
```
server/database/
├── index.js           # Factory and singleton export
├── config.js          # Database configuration with auto-detection
├── cli.js             # Migration CLI tool
├── migrations/        # SQL migration files
│   ├── 001_users.sql
│   ├── 002_courses.sql
│   └── ...
└── adapters/
    ├── BaseAdapter.js       # Abstract base with common operations
    ├── PostgresAdapter.js   # PostgreSQL-specific features
    └── MySQLAdapter.js      # MySQL-specific features
```

## Configuration (config.js)

```javascript
import 'dotenv/config';

const dbType = process.env.DB_TYPE || 'pg';
const isSupabase = process.env.DATABASE_URL?.includes('supabase');

// Parse DATABASE_URL if provided (Supabase, Heroku, etc.)
function parseConnectionUrl(url) {
  if (!url) return null;
  const parsed = new URL(url);
  return {
    host: parsed.hostname,
    port: parseInt(parsed.port),
    database: parsed.pathname.slice(1),
    user: parsed.username,
    password: parsed.password
  };
}

export function getConfig() {
  const urlConfig = parseConnectionUrl(process.env.DATABASE_URL);

  const connection = urlConfig || {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT) || (dbType === 'mysql' ? 3306 : 5432),
    database: process.env.DB_NAME || 'lms_db',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASS || ''
  };

  // SSL for Supabase and cloud providers
  if (isSupabase || process.env.DB_SSL === 'true') {
    connection.ssl = { rejectUnauthorized: false };
  }

  return {
    client: dbType === 'mysql' ? 'mysql2' : 'pg',
    connection,
    pool: { min: 2, max: 10 },
    acquireConnectionTimeout: 10000
  };
}

export { dbType, isSupabase };
```

## Base Adapter (BaseAdapter.js)

```javascript
export default class BaseAdapter {
  constructor(knex) {
    this.db = knex;
  }

  // Standard CRUD operations
  async findAll(table, options = {}) {
    let query = this.db(table);
    if (options.where) query = query.where(options.where);
    if (options.orderBy) query = query.orderBy(options.orderBy);
    if (options.limit) query = query.limit(options.limit);
    if (options.offset) query = query.offset(options.offset);
    return query;
  }

  async findById(table, id) {
    return this.db(table).where('id', id).first();
  }

  async findOne(table, where) {
    return this.db(table).where(where).first();
  }

  async create(table, data) {
    const [result] = await this.db(table).insert(data).returning('*');
    return result;
  }

  async update(table, id, data) {
    const [result] = await this.db(table)
      .where('id', id)
      .update({ ...data, updated_at: new Date() })
      .returning('*');
    return result;
  }

  async delete(table, id) {
    return this.db(table).where('id', id).del();
  }

  async count(table, where = {}) {
    const [{ count }] = await this.db(table).where(where).count('* as count');
    return parseInt(count);
  }

  async exists(table, where) {
    const result = await this.db(table).where(where).first();
    return !!result;
  }

  // Transaction support
  async transaction(callback) {
    return this.db.transaction(callback);
  }

  // Raw query
  async raw(sql, bindings = []) {
    return this.db.raw(sql, bindings);
  }

  // Abstract methods - must be implemented by subclasses
  async search(table, column, query) {
    throw new Error('search() must be implemented by subclass');
  }

  async upsert(table, data, conflictColumns) {
    throw new Error('upsert() must be implemented by subclass');
  }

  getJsonColumn(column) {
    throw new Error('getJsonColumn() must be implemented by subclass');
  }
}
```

## PostgreSQL Adapter (PostgresAdapter.js)

```javascript
import BaseAdapter from './BaseAdapter.js';

export default class PostgresAdapter extends BaseAdapter {
  // Case-insensitive search using ILIKE
  async search(table, column, query) {
    return this.db(table).where(column, 'ilike', `%${query}%`);
  }

  // Full-text search
  async fullTextSearch(table, columns, query) {
    const tsVector = columns.map(c => `coalesce(${c}, '')`).join(" || ' ' || ");
    return this.db(table)
      .whereRaw(`to_tsvector('english', ${tsVector}) @@ plainto_tsquery('english', ?)`, [query]);
  }

  // Upsert with ON CONFLICT
  async upsert(table, data, conflictColumns = ['id']) {
    const conflict = conflictColumns.join(', ');
    return this.db(table)
      .insert(data)
      .onConflict(this.db.raw(conflict))
      .merge()
      .returning('*');
  }

  // JSONB column operations
  getJsonColumn(column) {
    return this.db.raw(`?? ::jsonb`, [column]);
  }

  async jsonContains(table, column, value) {
    return this.db(table).whereRaw(`?? @> ?::jsonb`, [column, JSON.stringify(value)]);
  }

  async jsonArrayAppend(table, id, column, value) {
    return this.db(table)
      .where('id', id)
      .update({
        [column]: this.db.raw(`?? || ?::jsonb`, [column, JSON.stringify([value])])
      });
  }

  // Array operations (PostgreSQL native arrays)
  async arrayContains(table, column, value) {
    return this.db(table).whereRaw(`? = ANY(??)`, [value, column]);
  }

  // Bulk insert with RETURNING
  async bulkInsert(table, rows) {
    return this.db(table).insert(rows).returning('*');
  }
}
```

## MySQL Adapter (MySQLAdapter.js)

```javascript
import BaseAdapter from './BaseAdapter.js';

export default class MySQLAdapter extends BaseAdapter {
  // Case-insensitive search using LIKE (MySQL is case-insensitive by default)
  async search(table, column, query) {
    return this.db(table).where(column, 'like', `%${query}%`);
  }

  // Full-text search (requires FULLTEXT index)
  async fullTextSearch(table, columns, query) {
    const columnList = columns.join(', ');
    return this.db(table)
      .whereRaw(`MATCH(${columnList}) AGAINST(? IN NATURAL LANGUAGE MODE)`, [query]);
  }

  // Upsert with INSERT ... ON DUPLICATE KEY UPDATE
  async upsert(table, data, conflictColumns = ['id']) {
    const updateColumns = Object.keys(data)
      .filter(k => !conflictColumns.includes(k))
      .map(k => `${k} = VALUES(${k})`)
      .join(', ');

    const insertQuery = this.db(table).insert(data).toString();
    return this.db.raw(`${insertQuery} ON DUPLICATE KEY UPDATE ${updateColumns}`);
  }

  // JSON column operations
  getJsonColumn(column) {
    return this.db.raw(`JSON_UNQUOTE(??)`, [column]);
  }

  async jsonContains(table, column, value) {
    return this.db(table)
      .whereRaw(`JSON_CONTAINS(??, ?, '$')`, [column, JSON.stringify(value)]);
  }

  async jsonArrayAppend(table, id, column, value) {
    return this.db(table)
      .where('id', id)
      .update({
        [column]: this.db.raw(`JSON_ARRAY_APPEND(??, '$', ?)`, [column, JSON.stringify(value)])
      });
  }

  // Simulated array contains using JSON
  async arrayContains(table, column, value) {
    return this.db(table)
      .whereRaw(`JSON_CONTAINS(??, ?)`, [column, JSON.stringify(value)]);
  }

  // Bulk insert - MySQL doesn't support RETURNING, so fetch after
  async bulkInsert(table, rows) {
    await this.db(table).insert(rows);
    const ids = rows.map((_, i) => this.db.raw('LAST_INSERT_ID() + ?', [i]));
    return this.db(table).whereIn('id', ids);
  }

  // MySQL-specific: GROUP_CONCAT
  async groupConcat(table, groupBy, concatColumn, separator = ',') {
    return this.db(table)
      .select(groupBy)
      .select(this.db.raw(`GROUP_CONCAT(?? SEPARATOR ?) as items`, [concatColumn, separator]))
      .groupBy(groupBy);
  }
}
```

## Factory (index.js)

```javascript
import knex from 'knex';
import { getConfig, dbType } from './config.js';
import PostgresAdapter from './adapters/PostgresAdapter.js';
import MySQLAdapter from './adapters/MySQLAdapter.js';

let dbInstance = null;
let adapterInstance = null;

export function getDatabase() {
  if (!dbInstance) {
    dbInstance = knex(getConfig());
  }
  return dbInstance;
}

export function getAdapter() {
  if (!adapterInstance) {
    const db = getDatabase();
    adapterInstance = dbType === 'mysql'
      ? new MySQLAdapter(db)
      : new PostgresAdapter(db);
  }
  return adapterInstance;
}

export async function closeDatabase() {
  if (dbInstance) {
    await dbInstance.destroy();
    dbInstance = null;
    adapterInstance = null;
  }
}

// Named exports for convenience
export { dbType };
export const db = getDatabase();
export const adapter = getAdapter();
```

## CLI Tool (cli.js)

```javascript
#!/usr/bin/env node
import 'dotenv/config';
import { getDatabase, closeDatabase, dbType } from './index.js';
import fs from 'fs';
import path from 'path';

const db = getDatabase();
const migrationsDir = path.join(process.cwd(), 'server/database/migrations');

async function ensureMigrationTable() {
  const exists = await db.schema.hasTable('migrations');
  if (!exists) {
    await db.schema.createTable('migrations', (table) => {
      table.increments('id');
      table.string('name').notNullable();
      table.timestamp('executed_at').defaultTo(db.fn.now());
    });
  }
}

async function getExecutedMigrations() {
  await ensureMigrationTable();
  const rows = await db('migrations').select('name').orderBy('id');
  return rows.map(r => r.name);
}

async function runMigrations() {
  const executed = await getExecutedMigrations();
  const files = fs.readdirSync(migrationsDir)
    .filter(f => f.endsWith('.sql'))
    .sort();

  let count = 0;
  for (const file of files) {
    if (!executed.includes(file)) {
      console.log(`Running: ${file}`);
      const sql = fs.readFileSync(path.join(migrationsDir, file), 'utf8');
      await db.raw(sql);
      await db('migrations').insert({ name: file });
      count++;
    }
  }

  console.log(`Executed ${count} migration(s)`);
}

async function showStatus() {
  const executed = await getExecutedMigrations();
  const files = fs.readdirSync(migrationsDir)
    .filter(f => f.endsWith('.sql'))
    .sort();

  console.log(`\nDatabase: ${dbType.toUpperCase()}\n`);
  for (const file of files) {
    const status = executed.includes(file) ? '✓' : '○';
    console.log(`  ${status} ${file}`);
  }
}

// Command dispatch
const command = process.argv[2];
switch (command) {
  case 'migrate':
    runMigrations().then(() => closeDatabase());
    break;
  case 'status':
    showStatus().then(() => closeDatabase());
    break;
  default:
    console.log('Usage: node cli.js [migrate|status]');
}
```

## Usage Examples

```javascript
import { adapter } from './database/index.js';

// Find all active users
const users = await adapter.findAll('users', {
  where: { active: true },
  orderBy: 'created_at',
  limit: 10
});

// Search courses (uses ILIKE for PG, LIKE for MySQL)
const courses = await adapter.search('courses', 'title', 'javascript');

// Upsert setting
await adapter.upsert('settings', {
  key: 'site_name',
  value: 'My LMS'
}, ['key']);

// Transaction
await adapter.transaction(async (trx) => {
  await trx('users').insert({ name: 'John' });
  await trx('enrollments').insert({ user_id: 1, course_id: 1 });
});
```

## Environment Variables

```env
# PostgreSQL
DB_TYPE=pg
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lms_db
DB_USER=postgres
DB_PASS=password

# MySQL
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=lms_db
DB_USER=root
DB_PASS=password

# Supabase (auto-detected)
DATABASE_URL=postgres://user:pass@db.supabase.co:5432/postgres
```
