# Skill: JWT Authentication Basics

**Category:** Common Tasks
**Difficulty:** Beginner–Intermediate
**Applies to:** Node.js/Express

---

## What is JWT?

JWT (JSON Web Token) is a way to prove a user is logged in without checking the database on every request. When a user logs in, you give them a token. They send that token with every future request. You verify the token — no database lookup needed.

A JWT looks like this:
```
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjQyfQ.sFlKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```
It has three parts separated by dots: Header . Payload . Signature

---

## Setup

```bash
npm install jsonwebtoken bcryptjs
```

```
# .env
JWT_SECRET=use-a-long-random-string-minimum-32-characters
JWT_EXPIRES_IN=7d
```

---

## Step 1 — Register (Create a User)

```js
const bcrypt = require('bcryptjs');

router.post('/register', async (req, res) => {
  const { name, email, password } = req.body;

  if (!name || !email || !password)
    return res.status(400).json({ error: 'All fields required' });

  // Check if email already exists
  const existing = await db.query('SELECT id FROM users WHERE email = $1', [email]);
  if (existing.rows.length > 0)
    return res.status(409).json({ error: 'Email already in use' });

  // Hash the password — never store plain text
  const hash = await bcrypt.hash(password, 12);

  const result = await db.query(
    'INSERT INTO users (name, email, password_hash) VALUES ($1, $2, $3) RETURNING id, name, email',
    [name, email, hash]
  );

  res.status(201).json({ user: result.rows[0] });
});
```

---

## Step 2 — Login (Issue a Token)

```js
const jwt = require('jsonwebtoken');

router.post('/login', async (req, res) => {
  const { email, password } = req.body;

  const result = await db.query('SELECT * FROM users WHERE email = $1', [email]);
  const user = result.rows[0];

  // Use a vague error — don't tell attacker which part was wrong
  if (!user || !(await bcrypt.compare(password, user.password_hash)))
    return res.status(401).json({ error: 'Invalid email or password' });

  const token = jwt.sign(
    { userId: user.id, email: user.email },
    process.env.JWT_SECRET,
    { expiresIn: process.env.JWT_EXPIRES_IN }
  );

  res.json({ token, user: { id: user.id, name: user.name, email: user.email } });
});
```

---

## Step 3 — Auth Middleware (Protect Routes)

```js
// middleware/auth.js
const jwt = require('jsonwebtoken');

function requireAuth(req, res, next) {
  const header = req.headers.authorization;
  if (!header || !header.startsWith('Bearer '))
    return res.status(401).json({ error: 'No token provided' });

  const token = header.split(' ')[1];

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded; // now available in route as req.user
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Token invalid or expired' });
  }
}

module.exports = requireAuth;
```

---

## Step 4 — Protect a Route

```js
const requireAuth = require('../middleware/auth');

// Public route — anyone can access
router.get('/public', (req, res) => res.json({ message: 'Hello world' }));

// Protected route — must be logged in
router.get('/profile', requireAuth, async (req, res) => {
  const user = await db.query('SELECT id, name, email FROM users WHERE id = $1', [req.user.userId]);
  res.json(user.rows[0]);
});
```

---

## Step 5 — Frontend: Sending the Token

```js
// Save token after login
localStorage.setItem('token', data.token);

// Send token with every protected request
const response = await fetch('/api/profile', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
});
```

---

## Security Rules

| Do | Don't |
|----|-------|
| Use a long random JWT_SECRET | Use a short or guessable secret |
| Hash passwords with bcrypt (cost 10–14) | Store plain text or MD5 passwords |
| Give vague login error messages | Say "wrong password" vs "wrong email" |
| Set token expiry (7d or less) | Create tokens that never expire |
| Use HTTPS in production | Send tokens over plain HTTP |

---

*Fire Flow Skills Library — MIT License*
