# Skill: REST API Basics

**Category:** Basics
**Difficulty:** Beginner
**Applies to:** Node.js/Express, Python/Flask, any backend

---

## What is a REST API?

A REST API is how two programs talk to each other over the internet. Your frontend sends a request; your backend sends back data. Every request has:

- **Method** — what action to take (GET, POST, PUT, DELETE)
- **URL** — what resource to act on
- **Body** — data sent with the request (POST/PUT only)
- **Status code** — whether it worked

---

## The 4 Methods

| Method | Action | Example |
|--------|--------|---------|
| `GET` | Read data | Get a list of users |
| `POST` | Create new data | Create a new user |
| `PUT` / `PATCH` | Update existing data | Update a user's email |
| `DELETE` | Remove data | Delete a user |

---

## URL Design

Good URLs describe resources (nouns), not actions (verbs):

```
# GOOD
GET    /api/users          → list all users
GET    /api/users/42       → get user with id 42
POST   /api/users          → create a new user
PUT    /api/users/42       → update user 42
DELETE /api/users/42       → delete user 42

# BAD
GET    /api/getUsers
POST   /api/createUser
GET    /api/deleteUser?id=42
```

---

## Building a REST API (Express)

```js
const express = require('express');
const router = express.Router();

// GET all users
router.get('/', async (req, res) => {
  const users = await db.query('SELECT id, name, email FROM users');
  res.json(users);
});

// GET single user
router.get('/:id', async (req, res) => {
  const user = await db.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
  if (!user) return res.status(404).json({ error: 'User not found' });
  res.json(user);
});

// POST create user
router.post('/', async (req, res) => {
  const { name, email } = req.body;
  if (!name || !email) return res.status(400).json({ error: 'name and email required' });
  const user = await db.query(
    'INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *',
    [name, email]
  );
  res.status(201).json(user);
});

// PUT update user
router.put('/:id', async (req, res) => {
  const { name, email } = req.body;
  const user = await db.query(
    'UPDATE users SET name=$1, email=$2 WHERE id=$3 RETURNING *',
    [name, email, req.params.id]
  );
  if (!user) return res.status(404).json({ error: 'User not found' });
  res.json(user);
});

// DELETE user
router.delete('/:id', async (req, res) => {
  await db.query('DELETE FROM users WHERE id = $1', [req.params.id]);
  res.status(204).send();
});

module.exports = router;
```

```js
// In app.js
app.use('/api/users', require('./routes/users'));
```

---

## Calling an API (Frontend)

```js
// GET
const response = await fetch('/api/users');
const users = await response.json();

// POST
const response = await fetch('/api/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Jane', email: 'jane@example.com' })
});
const newUser = await response.json();

// DELETE
await fetch(`/api/users/${userId}`, { method: 'DELETE' });
```

---

## Always Return Consistent JSON

```js
// Success
res.status(200).json({ data: user });

// Error
res.status(400).json({ error: 'Email is required' });

// Created
res.status(201).json({ data: newUser, message: 'User created' });
```

Pick a format and use it everywhere. Inconsistent responses break the frontend.

---

## Testing Your API Without a Frontend

Use these tools to send requests manually:
- **Thunder Client** — VS Code extension, simplest option
- **Postman** — full-featured GUI
- **curl** — terminal, always available:

```bash
curl http://localhost:3000/api/users
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane","email":"jane@example.com"}'
```

---

*Fire Flow Skills Library — MIT License*
