# Skill: Security Checklist

**Category:** Quality & Safety
**Difficulty:** Beginner
**Applies to:** Every web project

---

## The 10 Most Common Security Mistakes

Based on the OWASP Top 10 — the industry-standard list of web vulnerabilities.

---

### 1. SQL Injection

**What it is:** An attacker puts SQL code in your input fields to steal or destroy your data.

```js
// VULNERABLE — never do this
const query = `SELECT * FROM users WHERE email = '${req.body.email}'`;
// Attacker sends: ' OR '1'='1 — returns ALL users

// SAFE — always use parameterized queries
const result = await db.query('SELECT * FROM users WHERE email = $1', [req.body.email]);
```

**Rule:** Never build SQL strings by concatenating user input.

---

### 2. Hardcoded Secrets

**What it is:** API keys, passwords, or tokens written directly in code and committed to git.

```js
// WRONG
const stripe = require('stripe')('sk_live_abc123realkey');

// RIGHT
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
```

**Rule:** Every secret lives in `.env`. `.env` is in `.gitignore`. See [env-variables.md](../basics/env-variables.md).

---

### 3. Missing Authentication on Routes

**What it is:** Forgetting to protect routes that should require login.

```js
// WRONG — anyone can delete any user
router.delete('/users/:id', async (req, res) => { ... });

// RIGHT
router.delete('/users/:id', requireAuth, async (req, res) => { ... });
```

**Rule:** Every route that reads private data or makes changes must have auth middleware.

---

### 4. Plain Text Passwords

**What it is:** Storing user passwords as plain text in the database. One breach = all accounts compromised.

```js
// WRONG
await db.query('INSERT INTO users (password) VALUES ($1)', [password]);

// RIGHT — always hash with bcrypt
const hash = await bcrypt.hash(password, 12);
await db.query('INSERT INTO users (password_hash) VALUES ($1)', [hash]);
```

**Rule:** Never store, log, or transmit plain text passwords. Hash with bcrypt.

---

### 5. No Input Validation

**What it is:** Trusting whatever the user sends without checking it.

```js
// WRONG — user could send a negative price, or a 10MB JSON body
app.post('/products', async (req, res) => {
  await db.query('INSERT INTO products (price) VALUES ($1)', [req.body.price]);
});

// RIGHT
app.use(express.json({ limit: '10kb' })); // limit body size
app.post('/products', async (req, res) => {
  const price = parseFloat(req.body.price);
  if (isNaN(price) || price < 0) return res.status(400).json({ error: 'Invalid price' });
  await db.query('INSERT INTO products (price) VALUES ($1)', [price]);
});
```

**Rule:** Validate every input on the server. See [form-validation.md](../common-tasks/form-validation.md).

---

### 6. Exposing Error Details to Users

**What it is:** Sending stack traces or database errors to the frontend, exposing your internal structure.

```js
// WRONG
res.status(500).json({ error: err.stack }); // shows file paths, table names

// RIGHT
console.error(err); // log full error on server
res.status(500).json({ error: 'Something went wrong. Please try again.' });
```

**Rule:** Log errors on the server. Send only generic messages to the client.

---

### 7. Missing HTTPS

**What it is:** Sending data over HTTP allows anyone on the network to read it (passwords, tokens, everything).

**Rule:** Always use HTTPS in production. Most hosting providers (Vercel, Railway, Render) do this automatically. For VPS, use Let's Encrypt (free SSL) via Certbot.

---

### 8. CORS Misconfiguration

**What it is:** Allowing any website to call your API.

```js
// WRONG — allows any origin
app.use(cors());

// RIGHT — only allow your own frontend
app.use(cors({
  origin: process.env.FRONTEND_URL, // e.g. 'https://myapp.com'
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));
```

**Rule:** Set CORS to your specific frontend domain in production.

---

### 9. Broken Access Control

**What it is:** A logged-in user can access or edit another user's data.

```js
// WRONG — user can request any profile by changing the ID
router.get('/profile/:id', requireAuth, async (req, res) => {
  const user = await db.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
  res.json(user.rows[0]);
});

// RIGHT — only return the logged-in user's own data
router.get('/profile', requireAuth, async (req, res) => {
  const user = await db.query('SELECT * FROM users WHERE id = $1', [req.user.userId]);
  res.json(user.rows[0]);
});
```

**Rule:** When fetching user-specific data, always filter by the authenticated user's ID from the token — not from the URL.

---

### 10. Outdated Dependencies

**What it is:** Old packages often have known security vulnerabilities.

```bash
# Check for vulnerabilities
npm audit

# Fix automatically (safe fixes only)
npm audit fix

# See outdated packages
npm outdated
```

**Rule:** Run `npm audit` before every deployment. Update dependencies regularly.

---

## Quick Pre-Launch Checklist

- [ ] All secrets are in `.env`, not in code
- [ ] `.env` is in `.gitignore`
- [ ] All write routes require authentication
- [ ] Passwords are hashed with bcrypt
- [ ] All user input is validated on the server
- [ ] CORS is set to the production frontend domain
- [ ] HTTPS is enabled
- [ ] `npm audit` shows no critical vulnerabilities
- [ ] Error messages sent to users contain no internal details

---

*Fire Flow Skills Library — MIT License*
