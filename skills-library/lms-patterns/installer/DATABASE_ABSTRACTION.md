# Database Abstraction Layer Specification

## Overview

This document specifies the database abstraction layer for supporting both PostgreSQL (current) and MySQL (shared hosting) in the MERN Community LMS platform.

**Target Environment:** Budget cPanel hosting ($5-15/month)
**Current Database:** PostgreSQL via Supabase (postgres.js library)
**Target Addition:** MySQL 5.7+/8.0 for shared hosting compatibility

---

## Table of Contents

1. [Current State Analysis](#1-current-state-analysis)
2. [Abstraction Strategy](#2-abstraction-strategy)
3. [Database Adapter Interface](#3-database-adapter-interface)
4. [Migration System](#4-migration-system)
5. [Schema Definitions](#5-schema-definitions)
6. [Query Translation Examples](#6-query-translation-examples)
7. [Connection Configuration](#7-connection-configuration)
8. [Implementation Plan](#8-implementation-plan)
9. [Testing Strategy](#9-testing-strategy)
10. [Compatibility Matrix](#10-compatibility-matrix)
11. [Complete Migration Files](#11-complete-migration-files)

---

## 1. Current State Analysis

### 1.1 Current postgres.js Usage Patterns

The application currently uses the **postgres.js** library (`postgres` npm package v3.4.7) with tagged template literals for SQL queries.

#### Connection Configuration (`server/config/sql.js`)

```javascript
import postgres from 'postgres';

let sql = null;

function initializeConnection() {
  if (!sql) {
    const connectionString = process.env.DATABASE_URL || process.env.VITE_SUPABASE_DB_URL;

    sql = postgres(connectionString, {
      max: 20,                    // Connection pool size
      idle_timeout: 30,           // 30 seconds
      connect_timeout: 30,        // For Supabase cold starts
      max_lifetime: 60 * 30,      // 30 minutes
      ssl: 'require',             // Supabase requires SSL
      prepare: false,             // Better Supabase compatibility
    });
  }
  return sql;
}

// Proxy pattern for lazy initialization
export default new Proxy(function() {}, {
  get(target, prop) {
    return getSql()[prop];
  },
  apply(target, thisArg, args) {
    return getSql()(...args);
  }
});
```

### 1.2 Query Patterns in Use

#### Pattern 1: Tagged Template Literals (Most Common)

```javascript
// Simple SELECT
const result = await sql`SELECT * FROM profiles WHERE email = ${email}`;

// SELECT with JOIN
const courses = await sql`
  SELECT c.*
  FROM courses c
  JOIN enrollments e ON c.id = e.course_id
  WHERE e.user_id = ${userId}
  ORDER BY c.created_at DESC
`;

// INSERT with RETURNING
await sql`
  INSERT INTO enrollments (user_id, course_id, enrolled_at)
  VALUES (${userId}, ${courseId}, NOW())
  ON CONFLICT (user_id, course_id) DO NOTHING
`;

// UPDATE
await sql`UPDATE profiles SET last_login_at = NOW() WHERE id = ${user.id}`;

// DELETE
await sql`DELETE FROM courses WHERE id = ${id}`;
```

#### Pattern 2: Dynamic Query Building

```javascript
// Building queries conditionally
let query = sql`SELECT * FROM courses`;

if (filters.is_published !== undefined) {
  query = sql`${query} WHERE is_published = ${filters.is_published}`;
}

if (filters.category) {
  query = sql`${query} AND category = ${filters.category}`;
}

query = sql`${query} ORDER BY created_at DESC`;
```

#### Pattern 3: sql.unsafe() for Dynamic SQL

```javascript
// Dynamic column/table names (used in models)
const result = await sql.unsafe(
  `INSERT INTO courses (${columnList}) VALUES (${placeholders}) RETURNING *`,
  values
);

// Dynamic SET clause
const result = await sql.unsafe(
  `UPDATE courses SET ${setClause} WHERE id = $${values.length + 1} RETURNING *`,
  [...values, id]
);
```

#### Pattern 4: Complex Queries with CTEs

```javascript
const result = await sql`
  WITH last_activity AS (
    SELECT
      vp.lesson_id,
      vp.course_id,
      vp.playback_position_ms,
      vp.last_watched_at
    FROM video_progress vp
    WHERE vp.user_id = ${userId}
    ORDER BY vp.last_watched_at DESC
    LIMIT 1
  )
  SELECT
    c.id as course_id,
    c.title as course_title,
    l.id as lesson_id,
    l.title as lesson_title,
    la.playback_position_ms
  FROM last_activity la
  JOIN courses c ON c.id = la.course_id
  JOIN lessons l ON l.id = la.lesson_id
`;
```

### 1.3 Tables and Schemas in Use

The application uses **49+ tables** organized into the following categories:

#### Core Tables
| Table | Purpose | PostgreSQL-Specific Features |
|-------|---------|------------------------------|
| `profiles` | User accounts | UUID, TIMESTAMPTZ |
| `courses` | Course content | UUID, TEXT[], TSVECTOR |
| `sections` | Course sections | UUID, TIMESTAMPTZ |
| `modules` | Course modules | UUID |
| `lessons` | Course lessons | UUID, JSONB, TSVECTOR |
| `enrollments` | User enrollments | UUID, composite unique |
| `lesson_progress` | Progress tracking | UUID |

#### E-Commerce Tables
| Table | Purpose | PostgreSQL-Specific Features |
|-------|---------|------------------------------|
| `payments` | Payment records | UUID, JSONB |
| `subscriptions` | Membership plans | UUID, JSONB |
| `products` | Store products | UUID, JSONB |
| `orders` | Purchase orders | UUID, JSONB |
| `cart_items` | Shopping cart | UUID |

#### Community Tables
| Table | Purpose | PostgreSQL-Specific Features |
|-------|---------|------------------------------|
| `community_discussions` | Forum threads | UUID, JSONB, full-text search |
| `community_replies` | Thread replies | UUID, JSONB |
| `groups` | User groups | UUID, JSONB |
| `timeline_posts` | Activity feed | UUID, JSONB |

#### Feature Tables
| Table | Purpose | PostgreSQL-Specific Features |
|-------|---------|------------------------------|
| `certificates` | Course certificates | UUID, SEQUENCE |
| `assessments` | Quizzes/tests | UUID, JSONB |
| `lesson_notes` | Student notes | UUID, TIMESTAMPTZ |
| `video_progress` | Video tracking | UUID |
| `donations` | Donation system | UUID, JSONB |

---

## 2. Abstraction Strategy

### Recommended Approach: Knex.js Query Builder

**Why Knex.js?**
- Mature, well-maintained library (10+ years)
- Native support for PostgreSQL and MySQL
- Built-in migration system
- Query builder that generates DB-specific SQL
- Transaction support
- Connection pooling
- TypeScript support

### Option A: Knex.js (Recommended)

```javascript
// Unified query builder syntax
const users = await db('profiles')
  .select('id', 'email', 'name')
  .where('role', 'student')
  .orderBy('created_at', 'desc');

// Equivalent to:
// PostgreSQL: SELECT "id", "email", "name" FROM "profiles" WHERE "role" = 'student' ORDER BY "created_at" DESC
// MySQL: SELECT `id`, `email`, `name` FROM `profiles` WHERE `role` = 'student' ORDER BY `created_at` DESC

// Complex JOIN
const enrolledCourses = await db('courses as c')
  .join('enrollments as e', 'c.id', 'e.course_id')
  .where('e.user_id', userId)
  .select('c.*', 'e.enrolled_at', 'e.progress')
  .orderBy('e.enrolled_at', 'desc');

// INSERT with returning
const [newUser] = await db('profiles')
  .insert({
    name: 'John Doe',
    email: 'john@example.com',
    role: 'student'
  })
  .returning('*'); // PostgreSQL returns full row
                   // MySQL returns insertId only

// Transaction example
await db.transaction(async (trx) => {
  const [enrollment] = await trx('enrollments')
    .insert({ user_id: userId, course_id: courseId })
    .returning('*');

  await trx('courses')
    .where('id', courseId)
    .increment('enrollment_count', 1);

  return enrollment;
});
```

### Option B: Raw SQL with Adapters

```javascript
// Adapter pattern for DB-specific queries
class DatabaseAdapter {
  async query(sql, params) {
    // PostgreSQL: Uses $1, $2 placeholders
    // MySQL: Uses ? placeholders
    const adaptedSql = this.adaptPlaceholders(sql);
    return this.client.query(adaptedSql, params);
  }

  adaptPlaceholders(sql) {
    if (this.dialect === 'mysql') {
      // Convert $1, $2 to ?
      return sql.replace(/\$(\d+)/g, '?');
    }
    return sql;
  }
}

// Usage
const users = await db.query(
  'SELECT id, email, name FROM profiles WHERE role = ? ORDER BY created_at DESC',
  ['student']
);
```

### Decision Matrix

| Criteria | Knex.js | Raw SQL + Adapters |
|----------|---------|-------------------|
| Development Speed | Fast | Slower |
| Learning Curve | Medium | Low |
| Type Safety | Good (with TS) | Manual |
| Migration Support | Built-in | Manual |
| Query Complexity | High | Full Control |
| Performance | Good | Best |
| Maintenance | Low | High |

**Recommendation:** Use Knex.js for new development, with raw SQL escape hatch for complex PostgreSQL-specific queries.

---

## 3. Database Adapter Interface

### 3.1 TypeScript Interface

```typescript
interface DatabaseConfig {
  client: 'pg' | 'mysql2';
  connection: {
    host: string;
    port: number;
    user: string;
    password: string;
    database: string;
    ssl?: boolean | object;
  };
  pool?: {
    min: number;
    max: number;
    idleTimeoutMillis?: number;
  };
}

interface Transaction {
  commit(): Promise<void>;
  rollback(): Promise<void>;
  query<T>(sql: string, params?: any[]): Promise<T[]>;
}

interface QueryResult<T> {
  rows: T[];
  rowCount: number;
  insertId?: number; // MySQL only
}

interface DatabaseAdapter {
  // Connection Management
  connect(config: DatabaseConfig): Promise<void>;
  disconnect(): Promise<void>;
  isConnected(): boolean;

  // Query Execution
  query<T>(sql: string, params?: any[]): Promise<T[]>;
  queryOne<T>(sql: string, params?: any[]): Promise<T | null>;
  execute(sql: string, params?: any[]): Promise<QueryResult<any>>;

  // Transaction Support
  transaction<T>(fn: (trx: Transaction) => Promise<T>): Promise<T>;

  // Migration Support
  migrate(direction: 'up' | 'down'): Promise<void>;
  migrateLatest(): Promise<void>;
  migrateRollback(): Promise<void>;
  getMigrationStatus(): Promise<MigrationStatus[]>;

  // Schema Operations
  hasTable(tableName: string): Promise<boolean>;
  hasColumn(tableName: string, columnName: string): Promise<boolean>;

  // Utility
  getDialect(): 'postgresql' | 'mysql';
  raw(sql: string): any;
}

interface MigrationStatus {
  name: string;
  batch: number;
  migration_time: Date;
}
```

### 3.2 Abstract Base Implementation

```javascript
// server/db/adapters/BaseAdapter.js
export class BaseAdapter {
  constructor(config) {
    this.config = config;
    this.knex = null;
    this.dialect = null;
  }

  async connect() {
    throw new Error('connect() must be implemented by subclass');
  }

  async disconnect() {
    if (this.knex) {
      await this.knex.destroy();
      this.knex = null;
    }
  }

  isConnected() {
    return this.knex !== null;
  }

  async query(sql, params = []) {
    return this.knex.raw(sql, params).then(result => {
      // Normalize result format between PostgreSQL and MySQL
      return this.normalizeResult(result);
    });
  }

  async queryOne(sql, params = []) {
    const rows = await this.query(sql, params);
    return rows[0] || null;
  }

  async transaction(fn) {
    return this.knex.transaction(fn);
  }

  normalizeResult(result) {
    // PostgreSQL returns { rows: [...] }
    // MySQL returns [[...], fields]
    if (Array.isArray(result)) {
      return result[0]; // MySQL
    }
    return result.rows || result; // PostgreSQL
  }

  // UUID generation (DB-specific)
  generateUUID() {
    throw new Error('generateUUID() must be implemented by subclass');
  }

  // Current timestamp
  now() {
    throw new Error('now() must be implemented by subclass');
  }
}
```

### 3.3 PostgreSQL Adapter

```javascript
// server/db/adapters/PostgresAdapter.js
import knex from 'knex';
import { BaseAdapter } from './BaseAdapter.js';

export class PostgresAdapter extends BaseAdapter {
  constructor(config) {
    super(config);
    this.dialect = 'postgresql';
  }

  async connect() {
    this.knex = knex({
      client: 'pg',
      connection: {
        host: this.config.host,
        port: this.config.port || 5432,
        user: this.config.user,
        password: this.config.password,
        database: this.config.database,
        ssl: this.config.ssl || { rejectUnauthorized: false }
      },
      pool: {
        min: 2,
        max: this.config.poolSize || 20,
        idleTimeoutMillis: 30000
      }
    });

    // Test connection
    await this.knex.raw('SELECT 1');
    console.log('[PostgreSQL] Connected successfully');
  }

  generateUUID() {
    return this.knex.raw('gen_random_uuid()');
  }

  now() {
    return this.knex.raw('NOW()');
  }

  // PostgreSQL-specific: JSONB operations
  jsonbContains(column, value) {
    return this.knex.raw(`${column} @> ?::jsonb`, [JSON.stringify(value)]);
  }

  jsonbExtract(column, path) {
    return this.knex.raw(`${column} -> ?`, [path]);
  }

  jsonbExtractText(column, path) {
    return this.knex.raw(`${column} ->> ?`, [path]);
  }

  // Full-text search
  textSearch(column, query) {
    return this.knex.raw(
      `to_tsvector('english', ${column}) @@ plainto_tsquery('english', ?)`,
      [query]
    );
  }

  // Array operations
  arrayContains(column, value) {
    return this.knex.raw(`? = ANY(${column})`, [value]);
  }

  // RETURNING clause support
  async insertReturning(table, data) {
    const [row] = await this.knex(table).insert(data).returning('*');
    return row;
  }
}
```

### 3.4 MySQL Adapter

```javascript
// server/db/adapters/MySQLAdapter.js
import knex from 'knex';
import { v4 as uuidv4 } from 'uuid';
import { BaseAdapter } from './BaseAdapter.js';

export class MySQLAdapter extends BaseAdapter {
  constructor(config) {
    super(config);
    this.dialect = 'mysql';
  }

  async connect() {
    this.knex = knex({
      client: 'mysql2',
      connection: {
        host: this.config.host,
        port: this.config.port || 3306,
        user: this.config.user,
        password: this.config.password,
        database: this.config.database,
        charset: 'utf8mb4',
        timezone: 'Z' // UTC
      },
      pool: {
        min: 2,
        max: this.config.poolSize || 10, // cPanel typically limits connections
        idleTimeoutMillis: 30000
      }
    });

    // Test connection
    await this.knex.raw('SELECT 1');
    console.log('[MySQL] Connected successfully');
  }

  generateUUID() {
    // MySQL doesn't have gen_random_uuid(), generate in app
    return uuidv4();
  }

  now() {
    return this.knex.raw('CURRENT_TIMESTAMP');
  }

  // MySQL JSON operations (different syntax from JSONB)
  jsonContains(column, value) {
    return this.knex.raw(
      `JSON_CONTAINS(${column}, ?)`,
      [JSON.stringify(value)]
    );
  }

  jsonExtract(column, path) {
    return this.knex.raw(`JSON_EXTRACT(${column}, ?)`, [`$.${path}`]);
  }

  jsonExtractText(column, path) {
    return this.knex.raw(`JSON_UNQUOTE(JSON_EXTRACT(${column}, ?))`, [`$.${path}`]);
  }

  // Full-text search (MySQL FULLTEXT)
  textSearch(column, query) {
    return this.knex.raw(
      `MATCH(${column}) AGAINST(? IN NATURAL LANGUAGE MODE)`,
      [query]
    );
  }

  // MySQL doesn't have native arrays - use JSON
  arrayContains(column, value) {
    return this.knex.raw(
      `JSON_CONTAINS(${column}, ?)`,
      [JSON.stringify(value)]
    );
  }

  // MySQL doesn't support RETURNING - need separate query
  async insertReturning(table, data) {
    // Generate UUID before insert
    if (!data.id) {
      data.id = this.generateUUID();
    }

    await this.knex(table).insert(data);

    // Fetch the inserted row
    const [row] = await this.knex(table).where('id', data.id);
    return row;
  }

  // UPSERT equivalent (MySQL ON DUPLICATE KEY UPDATE)
  async upsert(table, data, conflictColumns, updateColumns) {
    const insertStr = this.knex(table).insert(data).toString();
    const updateStr = updateColumns
      .map(col => `${col} = VALUES(${col})`)
      .join(', ');

    await this.knex.raw(`${insertStr} ON DUPLICATE KEY UPDATE ${updateStr}`);
    return this.knex(table).where('id', data.id).first();
  }
}
```

### 3.5 Adapter Factory

```javascript
// server/db/index.js
import { PostgresAdapter } from './adapters/PostgresAdapter.js';
import { MySQLAdapter } from './adapters/MySQLAdapter.js';

let dbInstance = null;

export function createDatabaseAdapter(config) {
  const dialect = config.client || process.env.DB_DIALECT || 'pg';

  switch (dialect) {
    case 'pg':
    case 'postgresql':
      return new PostgresAdapter(config);

    case 'mysql':
    case 'mysql2':
      return new MySQLAdapter(config);

    default:
      throw new Error(`Unsupported database dialect: ${dialect}`);
  }
}

export async function initializeDatabase() {
  if (dbInstance && dbInstance.isConnected()) {
    return dbInstance;
  }

  const config = {
    client: process.env.DB_DIALECT || 'pg',
    host: process.env.DB_HOST,
    port: parseInt(process.env.DB_PORT, 10),
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
    ssl: process.env.DB_SSL === 'true'
  };

  dbInstance = createDatabaseAdapter(config);
  await dbInstance.connect();

  return dbInstance;
}

export function getDatabase() {
  if (!dbInstance) {
    throw new Error('Database not initialized. Call initializeDatabase() first.');
  }
  return dbInstance;
}

export async function closeDatabase() {
  if (dbInstance) {
    await dbInstance.disconnect();
    dbInstance = null;
  }
}

export default { initializeDatabase, getDatabase, closeDatabase, createDatabaseAdapter };
```

---

## 4. Migration System

### 4.1 Migration File Format

```javascript
// server/db/migrations/20250111_001_create_profiles_table.js
export const up = async (knex) => {
  const isMySQL = knex.client.config.client === 'mysql2';

  await knex.schema.createTable('profiles', (table) => {
    // UUID primary key
    if (isMySQL) {
      table.string('id', 36).primary();
    } else {
      table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    }

    table.string('name', 255).notNullable();
    table.string('email', 255).notNullable().unique();
    table.string('password', 255);
    table.string('role', 20).defaultTo('user');
    table.text('avatar_url');
    table.text('bio');
    table.boolean('email_verified').defaultTo(false);
    table.string('email_verification_token', 255);
    table.timestamp('email_verification_expire');
    table.string('reset_password_token', 255);
    table.timestamp('reset_password_expire');
    table.timestamp('last_login_at');

    // Timestamps
    if (isMySQL) {
      table.timestamp('created_at').defaultTo(knex.raw('CURRENT_TIMESTAMP'));
      table.timestamp('updated_at').defaultTo(knex.raw('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'));
    } else {
      table.timestamp('created_at', { useTz: true }).defaultTo(knex.fn.now());
      table.timestamp('updated_at', { useTz: true }).defaultTo(knex.fn.now());
    }

    // Indexes
    table.index('email');
    table.index('role');
    table.index('created_at');
  });

  // PostgreSQL-specific: Add updated_at trigger
  if (!isMySQL) {
    await knex.raw(`
      CREATE OR REPLACE FUNCTION update_updated_at_column()
      RETURNS TRIGGER AS $$
      BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
      END;
      $$ LANGUAGE plpgsql;
    `);

    await knex.raw(`
      CREATE TRIGGER profiles_updated_at
      BEFORE UPDATE ON profiles
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
    `);
  }
};

export const down = async (knex) => {
  const isMySQL = knex.client.config.client === 'mysql2';

  if (!isMySQL) {
    await knex.raw('DROP TRIGGER IF EXISTS profiles_updated_at ON profiles');
  }

  await knex.schema.dropTableIfExists('profiles');
};
```

### 4.2 Migration Runner

```javascript
// server/db/migrator.js
import path from 'path';
import { getDatabase } from './index.js';

export async function runMigrations(direction = 'latest') {
  const db = getDatabase();
  const knex = db.knex;

  const migrationConfig = {
    directory: path.resolve('./server/db/migrations'),
    tableName: 'knex_migrations',
    extension: 'js',
    loadExtensions: ['.js']
  };

  switch (direction) {
    case 'latest':
      console.log('Running all pending migrations...');
      const [batchNo, log] = await knex.migrate.latest(migrationConfig);
      console.log(`Batch ${batchNo}: ${log.length} migrations completed`);
      log.forEach(m => console.log(`  - ${m}`));
      break;

    case 'up':
      console.log('Running next migration...');
      const [batch, files] = await knex.migrate.up(migrationConfig);
      console.log(`Batch ${batch}: ${files.length} migration(s) run`);
      break;

    case 'down':
      console.log('Rolling back last migration...');
      const [rollbackBatch, rollbackFiles] = await knex.migrate.down(migrationConfig);
      console.log(`Batch ${rollbackBatch}: ${rollbackFiles.length} migration(s) rolled back`);
      break;

    case 'rollback':
      console.log('Rolling back last batch...');
      const [rb, rbFiles] = await knex.migrate.rollback(migrationConfig);
      console.log(`Batch ${rb}: ${rbFiles.length} migration(s) rolled back`);
      break;

    case 'status':
      console.log('Migration status:');
      const [completed, pending] = await Promise.all([
        knex.migrate.list(migrationConfig),
      ]);
      console.log('Completed:', completed[0]);
      console.log('Pending:', completed[1]);
      break;

    default:
      throw new Error(`Unknown migration direction: ${direction}`);
  }
}

// CLI entry point
if (process.argv[1].includes('migrator')) {
  const direction = process.argv[2] || 'latest';

  import('./index.js').then(async ({ initializeDatabase }) => {
    await initializeDatabase();
    await runMigrations(direction);
    process.exit(0);
  }).catch(err => {
    console.error('Migration failed:', err);
    process.exit(1);
  });
}
```

### 4.3 Schema Versioning Table

```sql
-- Knex migrations table (auto-created)
CREATE TABLE knex_migrations (
  id SERIAL PRIMARY KEY,          -- PostgreSQL
  -- id INT AUTO_INCREMENT PRIMARY KEY,  -- MySQL
  name VARCHAR(255) NOT NULL,
  batch INT NOT NULL,
  migration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE knex_migrations_lock (
  index SERIAL PRIMARY KEY,
  is_locked INT NOT NULL DEFAULT 0
);
```

---

## 5. Schema Definitions

### 5.1 profiles Table

```sql
-- PostgreSQL
CREATE TABLE profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255),
  role VARCHAR(20) DEFAULT 'user',
  avatar_url TEXT,
  bio TEXT,
  skills TEXT[] DEFAULT '{}',
  location VARCHAR(255),
  email_verified BOOLEAN DEFAULT false,
  email_verification_token VARCHAR(255),
  email_verification_expire TIMESTAMPTZ,
  reset_password_token VARCHAR(255),
  reset_password_expire TIMESTAMPTZ,
  last_login_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_profiles_email ON profiles(email);
CREATE INDEX idx_profiles_role ON profiles(role);

-- MySQL
CREATE TABLE profiles (
  id CHAR(36) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255),
  role VARCHAR(20) DEFAULT 'user',
  avatar_url TEXT,
  bio TEXT,
  skills JSON DEFAULT '[]',
  location VARCHAR(255),
  email_verified TINYINT(1) DEFAULT 0,
  email_verification_token VARCHAR(255),
  email_verification_expire TIMESTAMP NULL,
  reset_password_token VARCHAR(255),
  reset_password_expire TIMESTAMP NULL,
  last_login_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_profiles_email (email),
  INDEX idx_profiles_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.2 courses Table

```sql
-- PostgreSQL
CREATE TABLE courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  slug VARCHAR(255) UNIQUE NOT NULL,
  short_description TEXT,
  description TEXT NOT NULL,
  level VARCHAR(20) DEFAULT 'beginner',
  category VARCHAR(100),
  topics TEXT[] DEFAULT '{}',
  thumbnail TEXT,
  cover_image TEXT,
  price DECIMAL(10,2) DEFAULT 0,
  discount_price DECIMAL(10,2),
  discount_expire_date TIMESTAMPTZ,
  duration INTEGER,
  requirements TEXT[] DEFAULT '{}',
  learning_objectives TEXT[] DEFAULT '{}',
  instructor_id UUID REFERENCES profiles(id),
  is_published BOOLEAN DEFAULT false,
  is_approved BOOLEAN DEFAULT false,
  is_featured BOOLEAN DEFAULT false,
  enrollment_count INTEGER DEFAULT 0,
  rating DECIMAL(3,2) DEFAULT 0,
  num_reviews INTEGER DEFAULT 0,
  membership_required VARCHAR(20) DEFAULT 'none',
  completion_mode VARCHAR(20) DEFAULT 'flexible',
  search_vector TSVECTOR,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_courses_instructor ON courses(instructor_id);
CREATE INDEX idx_courses_category ON courses(category);
CREATE INDEX idx_courses_published ON courses(is_published);
CREATE INDEX idx_courses_featured ON courses(is_featured);
CREATE INDEX idx_courses_search ON courses USING GIN(search_vector);

-- MySQL
CREATE TABLE courses (
  id CHAR(36) PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  slug VARCHAR(255) UNIQUE NOT NULL,
  short_description TEXT,
  description TEXT NOT NULL,
  level VARCHAR(20) DEFAULT 'beginner',
  category VARCHAR(100),
  topics JSON DEFAULT '[]',
  thumbnail TEXT,
  cover_image TEXT,
  price DECIMAL(10,2) DEFAULT 0.00,
  discount_price DECIMAL(10,2),
  discount_expire_date TIMESTAMP NULL,
  duration INT,
  requirements JSON DEFAULT '[]',
  learning_objectives JSON DEFAULT '[]',
  instructor_id CHAR(36),
  is_published TINYINT(1) DEFAULT 0,
  is_approved TINYINT(1) DEFAULT 0,
  is_featured TINYINT(1) DEFAULT 0,
  enrollment_count INT DEFAULT 0,
  rating DECIMAL(3,2) DEFAULT 0.00,
  num_reviews INT DEFAULT 0,
  membership_required VARCHAR(20) DEFAULT 'none',
  completion_mode VARCHAR(20) DEFAULT 'flexible',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (instructor_id) REFERENCES profiles(id) ON DELETE SET NULL,
  INDEX idx_courses_instructor (instructor_id),
  INDEX idx_courses_category (category),
  INDEX idx_courses_published (is_published),
  INDEX idx_courses_featured (is_featured),
  FULLTEXT INDEX idx_courses_search (title, short_description, description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.3 sections Table

```sql
-- PostgreSQL
CREATE TABLE sections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  order_index INTEGER NOT NULL DEFAULT 0,
  is_published BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sections_course ON sections(course_id);
CREATE INDEX idx_sections_order ON sections(course_id, order_index);

-- MySQL
CREATE TABLE sections (
  id CHAR(36) PRIMARY KEY,
  course_id CHAR(36) NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  order_index INT NOT NULL DEFAULT 0,
  is_published TINYINT(1) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  INDEX idx_sections_course (course_id),
  INDEX idx_sections_order (course_id, order_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.4 lessons Table

```sql
-- PostgreSQL
CREATE TABLE lessons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  section_id UUID REFERENCES sections(id) ON DELETE CASCADE,
  module_id UUID REFERENCES modules(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  content TEXT,
  order_index INTEGER NOT NULL DEFAULT 0,
  content_type VARCHAR(20) DEFAULT 'text',
  video JSONB DEFAULT '{}',
  attachments JSONB DEFAULT '[]',
  is_free BOOLEAN DEFAULT false,
  is_published BOOLEAN DEFAULT false,
  is_preview BOOLEAN DEFAULT false,
  available_after TIMESTAMPTZ,
  duration INTEGER,
  search_vector TSVECTOR,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_lessons_course ON lessons(course_id);
CREATE INDEX idx_lessons_section ON lessons(section_id);
CREATE INDEX idx_lessons_order ON lessons(section_id, order_index);
CREATE INDEX idx_lessons_search ON lessons USING GIN(search_vector);

-- MySQL
CREATE TABLE lessons (
  id CHAR(36) PRIMARY KEY,
  course_id CHAR(36) NOT NULL,
  section_id CHAR(36),
  module_id CHAR(36),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  content LONGTEXT,
  order_index INT NOT NULL DEFAULT 0,
  content_type VARCHAR(20) DEFAULT 'text',
  video JSON DEFAULT '{}',
  attachments JSON DEFAULT '[]',
  is_free TINYINT(1) DEFAULT 0,
  is_published TINYINT(1) DEFAULT 0,
  is_preview TINYINT(1) DEFAULT 0,
  available_after TIMESTAMP NULL,
  duration INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE,
  INDEX idx_lessons_course (course_id),
  INDEX idx_lessons_section (section_id),
  INDEX idx_lessons_order (section_id, order_index),
  FULLTEXT INDEX idx_lessons_search (title, description, content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.5 enrollments Table

```sql
-- PostgreSQL
CREATE TABLE enrollments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  payment_id UUID REFERENCES payments(id),
  enrolled_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
  last_accessed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT enrollments_user_course_unique UNIQUE(user_id, course_id)
);

CREATE INDEX idx_enrollments_user ON enrollments(user_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);

-- MySQL
CREATE TABLE enrollments (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  course_id CHAR(36) NOT NULL,
  payment_id CHAR(36),
  enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP NULL,
  progress INT DEFAULT 0,
  last_accessed_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  UNIQUE KEY unique_enrollment (user_id, course_id),
  INDEX idx_enrollments_user (user_id),
  INDEX idx_enrollments_course (course_id),
  CONSTRAINT chk_progress CHECK (progress >= 0 AND progress <= 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.6 lesson_notes Table

```sql
-- PostgreSQL
CREATE TABLE lesson_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  timestamp_seconds INTEGER DEFAULT 0,
  is_bookmark BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT chk_content_or_bookmark CHECK (
    (is_bookmark = true) OR
    (is_bookmark = false AND LENGTH(TRIM(content)) > 0)
  )
);

CREATE INDEX idx_lesson_notes_user ON lesson_notes(user_id);
CREATE INDEX idx_lesson_notes_lesson ON lesson_notes(lesson_id);
CREATE INDEX idx_lesson_notes_course ON lesson_notes(course_id);
CREATE INDEX idx_lesson_notes_user_course ON lesson_notes(user_id, course_id);

-- MySQL
CREATE TABLE lesson_notes (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  lesson_id CHAR(36) NOT NULL,
  course_id CHAR(36) NOT NULL,
  content TEXT NOT NULL,
  timestamp_seconds INT DEFAULT 0,
  is_bookmark TINYINT(1) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE,
  FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  INDEX idx_lesson_notes_user (user_id),
  INDEX idx_lesson_notes_lesson (lesson_id),
  INDEX idx_lesson_notes_course (course_id),
  INDEX idx_lesson_notes_user_course (user_id, course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.7 certificates Table

```sql
-- PostgreSQL
CREATE TABLE certificates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  certificate_number TEXT UNIQUE NOT NULL,
  student_name TEXT NOT NULL,
  course_title TEXT NOT NULL,
  instructor_name TEXT NOT NULL,
  completion_date DATE NOT NULL DEFAULT CURRENT_DATE,
  pdf_url TEXT,
  is_generated BOOLEAN NOT NULL DEFAULT false,
  verification_code TEXT UNIQUE NOT NULL,
  template_id UUID REFERENCES certificate_templates(id) ON DELETE SET NULL,
  issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT unique_user_course_certificate UNIQUE(user_id, course_id)
);

CREATE INDEX idx_certificates_user ON certificates(user_id);
CREATE INDEX idx_certificates_course ON certificates(course_id);
CREATE INDEX idx_certificates_date ON certificates(completion_date DESC);

-- MySQL
CREATE TABLE certificates (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  course_id CHAR(36) NOT NULL,
  certificate_number VARCHAR(50) UNIQUE NOT NULL,
  student_name VARCHAR(255) NOT NULL,
  course_title VARCHAR(255) NOT NULL,
  instructor_name VARCHAR(255) NOT NULL,
  completion_date DATE NOT NULL DEFAULT (CURRENT_DATE),
  pdf_url TEXT,
  is_generated TINYINT(1) NOT NULL DEFAULT 0,
  verification_code VARCHAR(64) UNIQUE NOT NULL,
  template_id CHAR(36),
  issued_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
  UNIQUE KEY unique_user_course_cert (user_id, course_id),
  INDEX idx_certificates_user (user_id),
  INDEX idx_certificates_course (course_id),
  INDEX idx_certificates_date (completion_date DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5.8 payments Table

```sql
-- PostgreSQL
CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  course_id UUID REFERENCES courses(id) ON DELETE SET NULL,
  subscription_id UUID REFERENCES subscriptions(id),
  amount DECIMAL(10,2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  status VARCHAR(20) DEFAULT 'pending',
  payment_method VARCHAR(50),
  stripe_payment_intent_id TEXT UNIQUE,
  stripe_charge_id TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_stripe ON payments(stripe_payment_intent_id);

-- MySQL
CREATE TABLE payments (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  course_id CHAR(36),
  subscription_id CHAR(36),
  amount DECIMAL(10,2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  status VARCHAR(20) DEFAULT 'pending',
  payment_method VARCHAR(50),
  stripe_payment_intent_id VARCHAR(255) UNIQUE,
  stripe_charge_id VARCHAR(255),
  metadata JSON DEFAULT '{}',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE,
  INDEX idx_payments_user (user_id),
  INDEX idx_payments_status (status),
  INDEX idx_payments_stripe (stripe_payment_intent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 6. Query Translation Examples

### 6.1 UUID Generation

```javascript
// PostgreSQL (native)
await sql`INSERT INTO profiles (id, name, email)
          VALUES (gen_random_uuid(), ${name}, ${email})`;

// MySQL (application-generated)
import { v4 as uuidv4 } from 'uuid';
const id = uuidv4();
await db('profiles').insert({ id, name, email });

// Knex.js (abstracted)
const [user] = await db('profiles')
  .insert({
    id: db.dialect === 'mysql' ? uuidv4() : db.raw('gen_random_uuid()'),
    name,
    email
  })
  .returning('*');
```

### 6.2 JSON/JSONB Operations

```javascript
// PostgreSQL JSONB
await sql`SELECT * FROM lessons WHERE video->>'provider' = 'youtube'`;
await sql`SELECT * FROM courses WHERE topics @> ARRAY['javascript']`;
await sql`UPDATE lessons SET video = video || '{"duration": 120}'::jsonb WHERE id = ${id}`;

// MySQL JSON
await db.raw("SELECT * FROM lessons WHERE JSON_UNQUOTE(JSON_EXTRACT(video, '$.provider')) = 'youtube'");
await db.raw("SELECT * FROM courses WHERE JSON_CONTAINS(topics, '\"javascript\"')");
await db.raw("UPDATE lessons SET video = JSON_SET(video, '$.duration', 120) WHERE id = ?", [id]);

// Knex.js (abstracted)
const adapter = getDatabase();
await db('lessons').where(
  adapter.jsonExtractText('video', 'provider'),
  'youtube'
);
```

### 6.3 Date/Time Functions

```javascript
// PostgreSQL
await sql`SELECT * FROM enrollments WHERE enrolled_at > NOW() - INTERVAL '30 days'`;
await sql`UPDATE profiles SET last_login_at = NOW() WHERE id = ${id}`;

// MySQL
await db.raw("SELECT * FROM enrollments WHERE enrolled_at > DATE_SUB(NOW(), INTERVAL 30 DAY)");
await db.raw("UPDATE profiles SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?", [id]);

// Knex.js (abstracted)
await db('enrollments')
  .where('enrolled_at', '>', db.raw("NOW() - INTERVAL '30' DAY"));
```

### 6.4 UPSERT (ON CONFLICT)

```javascript
// PostgreSQL
await sql`
  INSERT INTO enrollments (user_id, course_id, enrolled_at)
  VALUES (${userId}, ${courseId}, NOW())
  ON CONFLICT (user_id, course_id) DO UPDATE SET last_accessed_at = NOW()
  RETURNING *
`;

// MySQL
await db.raw(`
  INSERT INTO enrollments (id, user_id, course_id, enrolled_at)
  VALUES (?, ?, ?, CURRENT_TIMESTAMP)
  ON DUPLICATE KEY UPDATE last_accessed_at = CURRENT_TIMESTAMP
`, [uuidv4(), userId, courseId]);

// Knex.js (with onConflict - PostgreSQL only, need adapter for MySQL)
await db('enrollments')
  .insert({ user_id: userId, course_id: courseId })
  .onConflict(['user_id', 'course_id'])
  .merge({ last_accessed_at: db.fn.now() });
```

### 6.5 Array Operations

```javascript
// PostgreSQL
await sql`SELECT * FROM profiles WHERE 'javascript' = ANY(skills)`;
await sql`UPDATE profiles SET skills = array_append(skills, 'typescript') WHERE id = ${id}`;

// MySQL (using JSON arrays)
await db.raw("SELECT * FROM profiles WHERE JSON_CONTAINS(skills, '\"javascript\"')");
await db.raw("UPDATE profiles SET skills = JSON_ARRAY_APPEND(skills, '$', 'typescript') WHERE id = ?", [id]);

// Knex.js (abstracted via adapter)
const adapter = getDatabase();
await db('profiles').where(
  adapter.arrayContains('skills', 'javascript')
);
```

### 6.6 Full-Text Search

```javascript
// PostgreSQL
await sql`
  SELECT *, ts_rank(search_vector, plainto_tsquery('english', ${query})) as rank
  FROM courses
  WHERE search_vector @@ plainto_tsquery('english', ${query})
  ORDER BY rank DESC
`;

// MySQL
await db.raw(`
  SELECT *, MATCH(title, short_description, description) AGAINST(? IN NATURAL LANGUAGE MODE) as relevance
  FROM courses
  WHERE MATCH(title, short_description, description) AGAINST(? IN NATURAL LANGUAGE MODE)
  ORDER BY relevance DESC
`, [query, query]);

// Knex.js (abstracted)
const adapter = getDatabase();
if (adapter.dialect === 'postgresql') {
  await db('courses')
    .whereRaw("search_vector @@ plainto_tsquery('english', ?)", [query])
    .orderByRaw("ts_rank(search_vector, plainto_tsquery('english', ?)) DESC", [query]);
} else {
  await db('courses')
    .whereRaw("MATCH(title, short_description, description) AGAINST(? IN NATURAL LANGUAGE MODE)", [query])
    .orderByRaw("MATCH(title, short_description, description) AGAINST(? IN NATURAL LANGUAGE MODE) DESC", [query]);
}
```

### 6.7 RETURNING Clause

```javascript
// PostgreSQL (native support)
const [newCourse] = await sql`
  INSERT INTO courses (title, description, instructor_id)
  VALUES (${title}, ${description}, ${instructorId})
  RETURNING *
`;

// MySQL (no RETURNING - need LAST_INSERT_ID or application ID)
const id = uuidv4();
await db('courses').insert({ id, title, description, instructor_id: instructorId });
const newCourse = await db('courses').where('id', id).first();

// Knex.js (handles this automatically for PostgreSQL)
const [newCourse] = await db('courses')
  .insert({ title, description, instructor_id: instructorId })
  .returning('*');
// Note: In MySQL, returning() only returns the insertId, need separate query
```

---

## 7. Connection Configuration

### 7.1 Environment Variables

```bash
# .env - PostgreSQL (Supabase)
DB_DIALECT=pg
DB_HOST=db.xxxxxxxx.supabase.co
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_NAME=postgres
DB_SSL=true

# .env - MySQL (cPanel)
DB_DIALECT=mysql2
DB_HOST=localhost
DB_PORT=3306
DB_USER=cpanel_username
DB_PASSWORD=your-password
DB_NAME=cpanel_dbname
DB_SSL=false

# Common
DB_POOL_MIN=2
DB_POOL_MAX=10
```

### 7.2 Configuration Object

```javascript
// server/config/database.config.js
const config = {
  postgresql: {
    client: 'pg',
    connection: {
      host: process.env.DB_HOST,
      port: parseInt(process.env.DB_PORT, 10) || 5432,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_NAME,
      ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false
    },
    pool: {
      min: parseInt(process.env.DB_POOL_MIN, 10) || 2,
      max: parseInt(process.env.DB_POOL_MAX, 10) || 20,
      idleTimeoutMillis: 30000,
      createTimeoutMillis: 30000,
      acquireTimeoutMillis: 30000
    },
    migrations: {
      tableName: 'knex_migrations',
      directory: './server/db/migrations'
    },
    seeds: {
      directory: './server/db/seeds'
    }
  },

  mysql: {
    client: 'mysql2',
    connection: {
      host: process.env.DB_HOST,
      port: parseInt(process.env.DB_PORT, 10) || 3306,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_NAME,
      charset: 'utf8mb4',
      timezone: 'Z',
      multipleStatements: true // Required for migrations
    },
    pool: {
      min: parseInt(process.env.DB_POOL_MIN, 10) || 2,
      max: parseInt(process.env.DB_POOL_MAX, 10) || 10, // cPanel limits
      idleTimeoutMillis: 30000
    },
    migrations: {
      tableName: 'knex_migrations',
      directory: './server/db/migrations'
    },
    seeds: {
      directory: './server/db/seeds'
    }
  }
};

export function getConfig() {
  const dialect = process.env.DB_DIALECT || 'pg';
  return config[dialect === 'mysql2' ? 'mysql' : 'postgresql'];
}

export default config;
```

### 7.3 Knex Configuration File

```javascript
// knexfile.js
import { config } from 'dotenv';
config();

export default {
  development: {
    client: process.env.DB_DIALECT || 'pg',
    connection: {
      host: process.env.DB_HOST,
      port: parseInt(process.env.DB_PORT, 10),
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_NAME
    },
    migrations: {
      directory: './server/db/migrations'
    },
    seeds: {
      directory: './server/db/seeds'
    }
  },

  production: {
    client: process.env.DB_DIALECT || 'pg',
    connection: {
      host: process.env.DB_HOST,
      port: parseInt(process.env.DB_PORT, 10),
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_NAME,
      ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false
    },
    pool: {
      min: 2,
      max: parseInt(process.env.DB_POOL_MAX, 10) || 10
    },
    migrations: {
      directory: './server/db/migrations'
    }
  }
};
```

---

## 8. Implementation Plan

### Phase 1: Foundation (Week 1-2)

1. **Install Dependencies**
   ```bash
   npm install knex pg mysql2 uuid
   ```

2. **Create Database Adapter Layer**
   - `server/db/adapters/BaseAdapter.js`
   - `server/db/adapters/PostgresAdapter.js`
   - `server/db/adapters/MySQLAdapter.js`
   - `server/db/index.js` (factory)

3. **Create Migration Framework**
   - `server/db/migrations/` directory
   - `server/db/migrator.js`
   - `knexfile.js`

### Phase 2: Schema Migration Files (Week 2-3)

4. **Convert Existing Schema to Migrations**
   - Write migration files for all 49+ tables
   - Handle PostgreSQL/MySQL differences in each migration
   - Test migrations on both databases

5. **Create Seed Files**
   - Default roles
   - Admin user
   - Sample data (optional)

### Phase 3: Query Conversion (Week 3-5)

6. **Update Model Layer**
   - Convert `*.pg.js` models to use Knex adapter
   - Create helper methods for DB-specific operations
   - Maintain backward compatibility during transition

7. **Update Controllers**
   - Replace direct `sql` usage with model methods
   - Use abstracted query patterns

### Phase 4: Testing & Validation (Week 5-6)

8. **Create Test Suite**
   - Unit tests for adapters
   - Integration tests with both databases
   - Migration tests (up/down)

9. **Performance Testing**
   - Query performance comparison
   - Connection pooling validation
   - Load testing on shared hosting

### Phase 5: Documentation & Deployment (Week 6)

10. **Documentation**
    - Update installation guide
    - Database configuration guide
    - Troubleshooting guide

11. **Installer Integration**
    - Add database selection to installer
    - Auto-detect MySQL on cPanel
    - Connection testing

---

## 9. Testing Strategy

### 9.1 Unit Tests for Adapters

```javascript
// server/db/__tests__/PostgresAdapter.test.js
import { PostgresAdapter } from '../adapters/PostgresAdapter.js';

describe('PostgresAdapter', () => {
  let adapter;

  beforeAll(async () => {
    adapter = new PostgresAdapter({
      host: process.env.TEST_PG_HOST || 'localhost',
      port: 5432,
      user: 'test',
      password: 'test',
      database: 'test_db'
    });
    await adapter.connect();
  });

  afterAll(async () => {
    await adapter.disconnect();
  });

  test('should connect successfully', () => {
    expect(adapter.isConnected()).toBe(true);
    expect(adapter.getDialect()).toBe('postgresql');
  });

  test('should execute simple query', async () => {
    const result = await adapter.query('SELECT 1 as value');
    expect(result[0].value).toBe(1);
  });

  test('should generate UUID', () => {
    const uuid = adapter.generateUUID();
    expect(uuid.toString()).toContain('gen_random_uuid');
  });

  test('should handle transactions', async () => {
    await adapter.transaction(async (trx) => {
      await trx.raw('SELECT 1');
      // Transaction will be auto-committed
    });
  });
});
```

### 9.2 Integration Tests

```javascript
// server/db/__tests__/integration.test.js
import { initializeDatabase, closeDatabase } from '../index.js';

describe('Database Integration', () => {
  let db;

  beforeAll(async () => {
    db = await initializeDatabase();
  });

  afterAll(async () => {
    await closeDatabase();
  });

  test('should create and fetch profile', async () => {
    const id = db.dialect === 'mysql' ? require('uuid').v4() : null;

    // Insert
    const insertData = {
      ...(id && { id }),
      name: 'Test User',
      email: `test-${Date.now()}@example.com`,
      role: 'user'
    };

    const inserted = await db.insertReturning('profiles', insertData);
    expect(inserted.name).toBe('Test User');

    // Fetch
    const [fetched] = await db.knex('profiles')
      .where('id', inserted.id);
    expect(fetched.email).toBe(insertData.email);

    // Cleanup
    await db.knex('profiles').where('id', inserted.id).delete();
  });

  test('should handle JSON operations', async () => {
    // Create test lesson with video JSON
    const lessonData = {
      id: db.dialect === 'mysql' ? require('uuid').v4() : undefined,
      course_id: 'test-course-id', // Needs valid FK
      title: 'Test Lesson',
      video: JSON.stringify({ provider: 'youtube', video_id: 'abc123' })
    };

    // Test JSON extraction based on dialect
    // ...
  });
});
```

### 9.3 Migration Tests

```javascript
// server/db/__tests__/migrations.test.js
import { runMigrations } from '../migrator.js';
import { initializeDatabase, closeDatabase } from '../index.js';

describe('Migrations', () => {
  beforeAll(async () => {
    await initializeDatabase();
  });

  afterAll(async () => {
    await closeDatabase();
  });

  test('should run all migrations up', async () => {
    await runMigrations('latest');
    // Verify tables exist
    const db = getDatabase();
    expect(await db.knex.schema.hasTable('profiles')).toBe(true);
    expect(await db.knex.schema.hasTable('courses')).toBe(true);
    expect(await db.knex.schema.hasTable('enrollments')).toBe(true);
  });

  test('should rollback migrations', async () => {
    await runMigrations('rollback');
    // Some tables may not exist after rollback
  });

  test('should re-run migrations', async () => {
    await runMigrations('latest');
    // Verify idempotent
  });
});
```

### 9.4 Docker Test Environment

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: test_db
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]
      interval: 5s
      timeout: 5s
      retries: 5

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_USER: test
      MYSQL_PASSWORD: test
      MYSQL_DATABASE: test_db
    ports:
      - "3307:3306"
    command: --default-authentication-plugin=mysql_native_password
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 5s
      retries: 5
```

---

## 10. Compatibility Matrix

| Feature | PostgreSQL | MySQL | Abstraction Strategy |
|---------|------------|-------|---------------------|
| **UUID native** | Yes (`gen_random_uuid()`) | No (use CHAR(36)) | Generate in app for MySQL |
| **JSONB** | Yes (binary, indexed) | JSON (text-based) | Use JSON functions, no GIN indexes in MySQL |
| **Full-text search** | TSVECTOR + GIN | FULLTEXT indexes | Separate query strategies |
| **Array columns** | TEXT[] native | No (use JSON) | Store as JSON in both |
| **UPSERT** | ON CONFLICT DO UPDATE | ON DUPLICATE KEY | Adapter method |
| **RETURNING** | Yes | No (use LAST_INSERT_ID) | Adapter method |
| **Sequences** | SERIAL, SEQUENCE | AUTO_INCREMENT | Table per sequence in MySQL |
| **Boolean** | BOOLEAN | TINYINT(1) | Knex handles automatically |
| **TIMESTAMPTZ** | Yes (timezone-aware) | No (TIMESTAMP is UTC) | Store UTC, convert in app |
| **CHECK constraints** | Yes | Yes (8.0.16+) | Use in both, fallback to app validation |
| **Row-Level Security** | Yes | No | Application-level enforcement |
| **Triggers** | PLPGSQL | SQL | Different syntax per DB |
| **CTEs (WITH)** | Yes | Yes (8.0+) | Use with MySQL 8.0+ requirement |
| **Window functions** | Yes | Yes (8.0+) | Use with MySQL 8.0+ requirement |
| **Partial indexes** | Yes | No | Full indexes in MySQL |
| **Expression indexes** | Yes | Generated columns (8.0) | Different strategies |
| **ENUM types** | CREATE TYPE | ENUM column type | Different syntax |
| **Connection pooling** | pg-pool | mysql2 pool | Configured per adapter |

### MySQL Version Requirements

- **Minimum:** MySQL 5.7.8 (JSON support)
- **Recommended:** MySQL 8.0+ (CTEs, window functions, better JSON)
- **cPanel typical:** MySQL 5.7 or 8.0

### Feature Degradation in MySQL

1. **No JSONB indexes** - Full table scan for JSON queries
2. **No partial indexes** - May need covering indexes
3. **No RLS** - Must enforce access control in application
4. **No RETURNING** - Requires extra SELECT after INSERT
5. **Array emulation** - JSON arrays with JSON_CONTAINS

---

## 11. Complete Migration Files

### Migration: 001_create_profiles_table.js

```javascript
// server/db/migrations/20250111_001_create_profiles_table.js
export const up = async (knex) => {
  const isMySQL = knex.client.config.client === 'mysql2';

  await knex.schema.createTable('profiles', (table) => {
    if (isMySQL) {
      table.string('id', 36).primary();
    } else {
      table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    }

    table.string('name', 255).notNullable();
    table.string('email', 255).notNullable().unique();
    table.string('password', 255);
    table.string('role', 20).defaultTo('user');
    table.text('avatar_url');
    table.text('bio');

    if (isMySQL) {
      table.json('skills').defaultTo('[]');
    } else {
      table.specificType('skills', 'TEXT[]').defaultTo('{}');
    }

    table.string('location', 255);

    if (isMySQL) {
      table.tinyint('email_verified').defaultTo(0);
    } else {
      table.boolean('email_verified').defaultTo(false);
    }

    table.string('email_verification_token', 255);
    table.timestamp('email_verification_expire');
    table.string('reset_password_token', 255);
    table.timestamp('reset_password_expire');
    table.timestamp('last_login_at');

    if (isMySQL) {
      table.timestamp('created_at').defaultTo(knex.raw('CURRENT_TIMESTAMP'));
      table.timestamp('updated_at').defaultTo(knex.raw('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'));
    } else {
      table.timestamp('created_at', { useTz: true }).defaultTo(knex.fn.now());
      table.timestamp('updated_at', { useTz: true }).defaultTo(knex.fn.now());
    }

    table.index('email');
    table.index('role');
    table.index('created_at');
  });

  // PostgreSQL: Add updated_at trigger
  if (!isMySQL) {
    await knex.raw(`
      CREATE OR REPLACE FUNCTION update_updated_at_column()
      RETURNS TRIGGER AS $$
      BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
      END;
      $$ LANGUAGE plpgsql;
    `);

    await knex.raw(`
      CREATE TRIGGER profiles_updated_at
      BEFORE UPDATE ON profiles
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
    `);
  }
};

export const down = async (knex) => {
  const isMySQL = knex.client.config.client === 'mysql2';

  if (!isMySQL) {
    await knex.raw('DROP TRIGGER IF EXISTS profiles_updated_at ON profiles');
  }

  await knex.schema.dropTableIfExists('profiles');
};
```

### Migration: 002_create_courses_table.js

```javascript
// server/db/migrations/20250111_002_create_courses_table.js
export const up = async (knex) => {
  const isMySQL = knex.client.config.client === 'mysql2';

  await knex.schema.createTable('courses', (table) => {
    if (isMySQL) {
      table.string('id', 36).primary();
    } else {
      table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    }

    table.string('title', 255).notNullable();
    table.string('slug', 255).notNullable().unique();
    table.text('short_description');
    table.text('description').notNullable();
    table.string('level', 20).defaultTo('beginner');
    table.string('category', 100);

    if (isMySQL) {
      table.json('topics').defaultTo('[]');
    } else {
      table.specificType('topics', 'TEXT[]').defaultTo('{}');
    }

    table.text('thumbnail');
    table.text('cover_image');
    table.decimal('price', 10, 2).defaultTo(0);
    table.decimal('discount_price', 10, 2);
    table.timestamp('discount_expire_date');
    table.integer('duration');

    if (isMySQL) {
      table.json('requirements').defaultTo('[]');
      table.json('learning_objectives').defaultTo('[]');
    } else {
      table.specificType('requirements', 'TEXT[]').defaultTo('{}');
      table.specificType('learning_objectives', 'TEXT[]').defaultTo('{}');
    }

    if (isMySQL) {
      table.string('instructor_id', 36).references('id').inTable('profiles').onDelete('SET NULL');
    } else {
      table.uuid('instructor_id').references('id').inTable('profiles').onDelete('SET NULL');
    }

    if (isMySQL) {
      table.tinyint('is_published').defaultTo(0);
      table.tinyint('is_approved').defaultTo(0);
      table.tinyint('is_featured').defaultTo(0);
    } else {
      table.boolean('is_published').defaultTo(false);
      table.boolean('is_approved').defaultTo(false);
      table.boolean('is_featured').defaultTo(false);
    }

    table.integer('enrollment_count').defaultTo(0);
    table.decimal('rating', 3, 2).defaultTo(0);
    table.integer('num_reviews').defaultTo(0);
    table.string('membership_required', 20).defaultTo('none');
    table.string('completion_mode', 20).defaultTo('flexible');

    if (isMySQL) {
      table.timestamp('created_at').defaultTo(knex.raw('CURRENT_TIMESTAMP'));
      table.timestamp('updated_at').defaultTo(knex.raw('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'));
    } else {
      table.timestamp('created_at', { useTz: true }).defaultTo(knex.fn.now());
      table.timestamp('updated_at', { useTz: true }).defaultTo(knex.fn.now());
    }

    table.index('instructor_id');
    table.index('category');
    table.index('is_published');
    table.index('is_featured');
  });

  // Full-text search
  if (isMySQL) {
    await knex.raw('ALTER TABLE courses ADD FULLTEXT INDEX idx_courses_search (title, short_description, description)');
  } else {
    await knex.raw(`
      ALTER TABLE courses ADD COLUMN search_vector TSVECTOR;
      CREATE INDEX idx_courses_search ON courses USING GIN(search_vector);

      CREATE OR REPLACE FUNCTION courses_search_trigger()
      RETURNS TRIGGER AS $$
      BEGIN
        NEW.search_vector :=
          setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
          setweight(to_tsvector('english', COALESCE(NEW.short_description, '')), 'B') ||
          setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'C');
        RETURN NEW;
      END;
      $$ LANGUAGE plpgsql;

      CREATE TRIGGER courses_search_update
      BEFORE INSERT OR UPDATE ON courses
      FOR EACH ROW
      EXECUTE FUNCTION courses_search_trigger();
    `);
  }

  // PostgreSQL: Add updated_at trigger
  if (!isMySQL) {
    await knex.raw(`
      CREATE TRIGGER courses_updated_at
      BEFORE UPDATE ON courses
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
    `);
  }
};

export const down = async (knex) => {
  const isMySQL = knex.client.config.client === 'mysql2';

  if (!isMySQL) {
    await knex.raw('DROP TRIGGER IF EXISTS courses_search_update ON courses');
    await knex.raw('DROP TRIGGER IF EXISTS courses_updated_at ON courses');
    await knex.raw('DROP FUNCTION IF EXISTS courses_search_trigger()');
  }

  await knex.schema.dropTableIfExists('courses');
};
```

### Additional Migrations

For brevity, the remaining migration files follow the same pattern:

- `003_create_sections_table.js`
- `004_create_modules_table.js`
- `005_create_lessons_table.js`
- `006_create_enrollments_table.js`
- `007_create_lesson_progress_table.js`
- `008_create_payments_table.js`
- `009_create_subscriptions_table.js`
- `010_create_certificates_table.js`
- `011_create_assessments_table.js`
- `012_create_lesson_notes_table.js`
- `013_create_video_progress_table.js`
- `014_create_community_tables.js`
- `015_create_ecommerce_tables.js`
- `016_create_donations_table.js`
- `017_create_site_settings_table.js`
- ... (remaining 32+ tables)

---

## Summary

This database abstraction layer provides:

1. **Dual Database Support** - PostgreSQL and MySQL with a unified API
2. **Query Builder Abstraction** - Knex.js for portable queries
3. **Migration System** - Version-controlled schema with rollback support
4. **Adapter Pattern** - DB-specific implementations behind common interface
5. **Gradual Migration Path** - Can convert queries incrementally
6. **Testing Framework** - Docker-based testing for both databases
7. **Compatibility Documentation** - Clear mapping between PostgreSQL and MySQL features

The implementation prioritizes:
- Minimal changes to existing application code
- Maximum compatibility with cPanel shared hosting
- Performance optimization for both database systems
- Clear documentation for future maintenance
