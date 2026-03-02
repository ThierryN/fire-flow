# Skill: Database Schema Design

**Category:** Common Tasks
**Difficulty:** Beginner–Intermediate
**Applies to:** PostgreSQL, MySQL, SQLite

---

## The Problem

A poorly designed schema causes bugs that are painful to fix later — duplicate data, broken relationships, impossible queries. Getting it right at the start saves enormous time.

---

## The Core Rules

### 1. Every table needs a primary key

```sql
-- Every row needs a unique identifier
CREATE TABLE users (
  id SERIAL PRIMARY KEY,  -- auto-incrementing integer
  -- or use UUID:
  -- id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Use foreign keys to link tables

```sql
-- posts belong to users
CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  body TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

`ON DELETE CASCADE` means: if the user is deleted, delete their posts too.
`ON DELETE RESTRICT` means: refuse to delete a user who has posts.

### 3. Don't repeat data — normalize it

```sql
-- BAD: storing category name in every post (repeats data, hard to rename)
posts: id | title | category_name

-- GOOD: categories in their own table
CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  category_id INTEGER REFERENCES categories(id)
);
```

### 4. Many-to-Many relationships need a join table

```sql
-- A post can have many tags. A tag can be on many posts.

CREATE TABLE tags (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE post_tags (
  post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
  tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (post_id, tag_id)  -- prevents duplicates
);
```

---

## Column Types Cheat Sheet

| Type | Use For |
|------|---------|
| `SERIAL` / `INTEGER` | Auto-increment IDs, counts |
| `UUID` | IDs when you don't want guessable numbers |
| `VARCHAR(n)` | Short text with a max length |
| `TEXT` | Long text, no length limit |
| `BOOLEAN` | True/false flags |
| `INTEGER` | Whole numbers |
| `DECIMAL(10,2)` | Money (never use FLOAT for money) |
| `TIMESTAMP` | Date + time |
| `DATE` | Date only |
| `JSONB` | Flexible data (PostgreSQL only) |

---

## A Complete Example

```sql
-- Users
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Products
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
  stock_count INTEGER DEFAULT 0 CHECK (stock_count >= 0),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Orders
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  total DECIMAL(10,2) NOT NULL,
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'shipped', 'cancelled')),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Order line items
CREATE TABLE order_items (
  id SERIAL PRIMARY KEY,
  order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id INTEGER NOT NULL REFERENCES products(id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  price_at_purchase DECIMAL(10,2) NOT NULL  -- snapshot price, not live price
);
```

---

## Indexes — Speed Up Queries

```sql
-- Add indexes on columns you frequently search or filter by
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_users_email ON users(email);  -- usually covered by UNIQUE
```

---

## Questions to Ask Before Creating a Table

1. What is the primary key?
2. What other tables does this relate to?
3. What columns should be NOT NULL?
4. What columns need to be UNIQUE?
5. What should happen when a related record is deleted?

---

*Fire Flow Skills Library — MIT License*
