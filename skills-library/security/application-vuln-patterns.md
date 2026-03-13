---
name: application-vuln-patterns
category: security
version: 1.0.0
contributed: 2026-02-20
contributor: dominion-flow
last_updated: 2026-02-20
tags: [owasp, security, mern, mongodb, express, react, nodejs, xss, injection, authentication]
difficulty: hard
usage_count: 0
success_rate: 100
---

# Application Vulnerability Patterns (MERN Stack)

Reference patterns for `/fire-vuln-scan` — OWASP Top 10 mapped to MongoDB, Express, React, Node.js.

---

## A01: Broken Access Control

### Missing Auth Middleware on Routes

```javascript
// VULNERABLE — admin route with no authentication
router.get('/api/admin/users', adminController.getAllUsers);
router.delete('/api/admin/users/:id', adminController.deleteUser);

// SAFE — auth + role check middleware
router.get('/api/admin/users', protect, authorize('admin'), adminController.getAllUsers);
router.delete('/api/admin/users/:id', protect, authorize('admin'), adminController.deleteUser);
```

### IDOR (Insecure Direct Object Reference)

```javascript
// VULNERABLE — any authenticated user can access any user's data
router.get('/api/users/:id', protect, async (req, res) => {
  const user = await User.findById(req.params.id);
  res.json(user);
});

// SAFE — verify ownership or admin role
router.get('/api/users/:id', protect, async (req, res) => {
  if (req.params.id !== req.user._id.toString() && req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Not authorized' });
  }
  const user = await User.findById(req.params.id);
  res.json(user);
});
```

### Privilege Escalation via Mass Assignment

```javascript
// VULNERABLE — user can set their own role
router.put('/api/users/:id', protect, async (req, res) => {
  const user = await User.findByIdAndUpdate(req.params.id, req.body, { new: true });
  res.json(user);
});
// Attack: PUT /api/users/123 { "role": "admin" }

// SAFE — whitelist allowed fields
router.put('/api/users/:id', protect, async (req, res) => {
  const { name, email, avatar } = req.body; // Only allowed fields
  const user = await User.findByIdAndUpdate(req.params.id, { name, email, avatar }, { new: true });
  res.json(user);
});
```

### Missing CORS Configuration

```javascript
// VULNERABLE — allows any origin
app.use(cors());
// or
app.use(cors({ origin: '*' }));

// SAFE — explicit allowlist
app.use(cors({
  origin: ['https://yourdomain.com', 'https://admin.yourdomain.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
}));
```

---

## A02: Cryptographic Failures

### Hardcoded Secrets

```javascript
// VULNERABLE — secrets in source code
const JWT_SECRET = 'my-super-secret-key-12345';
const STRIPE_KEY = 'sk_live_abc123...';
const DB_URI = 'mongodb://admin:password123@prod-server:27017/mydb';

// SAFE — environment variables
const JWT_SECRET = process.env.JWT_SECRET;
const STRIPE_KEY = process.env.STRIPE_SECRET_KEY;
const DB_URI = process.env.MONGODB_URI;
```

### Weak Password Hashing

```javascript
// VULNERABLE — MD5 or SHA1 for passwords
const crypto = require('crypto');
const hash = crypto.createHash('md5').update(password).digest('hex');

// SAFE — bcrypt with sufficient rounds
const bcrypt = require('bcryptjs');
const hash = await bcrypt.hash(password, 12);
```

### Sensitive Data in Logs

```javascript
// VULNERABLE — logging passwords and tokens
console.log('Login attempt:', { email, password });
console.log('Token generated:', token);

// SAFE — redact sensitive fields
console.log('Login attempt:', { email, password: '[REDACTED]' });
console.log('Token generated for:', email);
```

---

## A03: Injection

### NoSQL Injection (MongoDB)

```javascript
// VULNERABLE — user input directly in query object
router.post('/api/login', async (req, res) => {
  const user = await User.findOne({
    username: req.body.username,
    password: req.body.password,
  });
});
// Attack: { "username": {"$gt": ""}, "password": {"$gt": ""} } → bypasses auth

// SAFE — type coercion + bcrypt comparison
router.post('/api/login', async (req, res) => {
  const user = await User.findOne({ username: String(req.body.username) });
  if (!user || !(await bcrypt.compare(String(req.body.password), user.password))) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
});
```

### MongoDB $where Injection

```javascript
// VULNERABLE — JavaScript execution in query
db.users.find({ $where: `this.name === '${userInput}'` });

// SAFE — use standard query operators
db.users.find({ name: String(userInput) });
```

### Command Injection

```javascript
// VULNERABLE — user input in shell command
const { exec } = require('child_process');
exec(`convert ${req.body.filename} output.pdf`);

// SAFE — use execFile with argument array
const { execFile } = require('child_process');
execFile('convert', [sanitizedFilename, 'output.pdf']);
```

### Path Traversal

```javascript
// VULNERABLE — user controls file path
router.get('/api/files/:filename', (req, res) => {
  res.sendFile(path.join(uploadDir, req.params.filename));
});
// Attack: GET /api/files/../../etc/passwd

// SAFE — validate and restrict path
router.get('/api/files/:filename', (req, res) => {
  const filename = path.basename(req.params.filename); // Strip directory traversal
  const filePath = path.join(uploadDir, filename);
  if (!filePath.startsWith(path.resolve(uploadDir))) {
    return res.status(400).json({ error: 'Invalid path' });
  }
  res.sendFile(filePath);
});
```

### SSRF (Server-Side Request Forgery)

```javascript
// VULNERABLE — user controls URL
router.post('/api/fetch-url', async (req, res) => {
  const response = await fetch(req.body.url);
  res.json(await response.json());
});
// Attack: { "url": "http://169.254.169.254/latest/meta-data/" } → AWS metadata

// SAFE — URL allowlist
const ALLOWED_HOSTS = ['api.stripe.com', 'api.example.com'];
router.post('/api/fetch-url', async (req, res) => {
  const url = new URL(req.body.url);
  if (!ALLOWED_HOSTS.includes(url.hostname)) {
    return res.status(400).json({ error: 'URL not allowed' });
  }
  const response = await fetch(req.body.url);
  res.json(await response.json());
});
```

---

## A05: Security Misconfiguration

### Missing Security Headers (Helmet.js)

```javascript
// VULNERABLE — no security headers
const app = express();
app.use(cors());
app.use(express.json());

// SAFE — Helmet sets 15+ security headers
const helmet = require('helmet');
const app = express();
app.use(helmet());
app.use(cors({ origin: allowedOrigins }));
app.use(express.json({ limit: '10mb' }));
```

### Verbose Error Messages in Production

```javascript
// VULNERABLE — stack traces sent to client
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack,
    query: err.query,
  });
});

// SAFE — generic message in production
app.use((err, req, res, next) => {
  console.error(err); // Log full error server-side
  res.status(500).json({
    error: process.env.NODE_ENV === 'production'
      ? 'Internal server error'
      : err.message,
  });
});
```

### Missing Rate Limiting

```javascript
// VULNERABLE — no rate limiting
router.post('/api/auth/login', authController.login);
router.post('/api/auth/forgot-password', authController.forgotPassword);

// SAFE — rate limiting on sensitive endpoints
const rateLimit = require('express-rate-limit');
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  message: { error: 'Too many attempts. Try again in 15 minutes.' },
});
router.post('/api/auth/login', authLimiter, authController.login);
router.post('/api/auth/forgot-password', authLimiter, authController.forgotPassword);
```

### Missing Input Sanitization

```javascript
// VULNERABLE — raw user input passed to MongoDB
app.use(express.json());

// SAFE — sanitize MongoDB operators from input
const mongoSanitize = require('express-mongo-sanitize');
app.use(express.json());
app.use(mongoSanitize()); // Strips $ and . from req.body/query/params
```

---

## A07: XSS (Cross-Site Scripting)

### React dangerouslySetInnerHTML

```jsx
// VULNERABLE — unsanitized user HTML
function Comment({ content }) {
  return <div dangerouslySetInnerHTML={{ __html: content }} />;
}

// SAFE — sanitize with DOMPurify
import DOMPurify from 'dompurify';
function Comment({ content }) {
  return <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(content) }} />;
}
```

### Server-Side Rendering XSS

```javascript
// VULNERABLE — unescaped user content in HTML response
app.get('/profile/:username', (req, res) => {
  res.send(`<h1>Welcome, ${req.params.username}</h1>`);
});
// Attack: /profile/<script>alert('xss')</script>

// SAFE — escape HTML entities
const escapeHtml = require('escape-html');
app.get('/profile/:username', (req, res) => {
  res.send(`<h1>Welcome, ${escapeHtml(req.params.username)}</h1>`);
});
```

---

## MERN-Specific Patterns

### Prototype Pollution

```javascript
// VULNERABLE — deep merge with user input
function merge(target, source) {
  for (const key in source) {
    if (typeof source[key] === 'object') {
      target[key] = merge(target[key] || {}, source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}
merge({}, JSON.parse(userInput));
// Attack: {"__proto__": {"isAdmin": true}}

// SAFE — block prototype keys
function safeMerge(target, source) {
  for (const key in source) {
    if (key === '__proto__' || key === 'constructor' || key === 'prototype') continue;
    if (typeof source[key] === 'object' && source[key] !== null) {
      target[key] = safeMerge(target[key] || {}, source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}
```

### Mongoose populate() Data Leakage

```javascript
// VULNERABLE — populates ALL fields including sensitive ones
const order = await Order.findById(id).populate('user');
// Exposes: user.password, user.resetToken, user.role, etc.

// SAFE — select only needed fields
const order = await Order.findById(id).populate('user', 'name email avatar');
```

### JWT Without Expiration

```javascript
// VULNERABLE — token never expires
const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET);

// SAFE — short expiration + refresh token pattern
const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '15m' });
const refreshToken = jwt.sign({ id: user._id }, process.env.JWT_REFRESH_SECRET, { expiresIn: '7d' });
```

### Unhandled Promise Rejections

```javascript
// VULNERABLE — unhandled rejection crashes server
app.get('/api/data', async (req, res) => {
  const data = await SomeModel.find(); // If DB is down, crashes
  res.json(data);
});

// SAFE — express-async-handler or try/catch
const asyncHandler = require('express-async-handler');
app.get('/api/data', asyncHandler(async (req, res) => {
  const data = await SomeModel.find();
  res.json(data);
}));

// ALSO: Global unhandled rejection handler
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection:', reason);
  // Graceful shutdown instead of crash
});
```

### Sensitive Data in Client-Side Code

```javascript
// VULNERABLE — API keys in React client code
const STRIPE_SECRET = 'sk_live_abc123'; // This ships to browser!
const API_KEY = process.env.REACT_APP_SECRET_KEY; // Still in bundle!

// SAFE — only publishable keys client-side, secrets server-side only
const STRIPE_PUBLIC = 'pk_live_xyz789'; // Publishable key is OK
// Secret operations happen via server API calls, never in client
```

---

## Quick Reference: Security Middleware Stack

```javascript
// Recommended Express security middleware order
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const mongoSanitize = require('express-mongo-sanitize');
const xss = require('xss-clean');
const hpp = require('hpp');

const app = express();

// 1. Security headers
app.use(helmet());

// 2. CORS with explicit origins
app.use(cors({ origin: allowedOrigins, credentials: true }));

// 3. Rate limiting
app.use('/api/', rateLimit({ windowMs: 10 * 60 * 1000, max: 100 }));

// 4. Body parsing with size limits
app.use(express.json({ limit: '10kb' }));

// 5. NoSQL injection prevention
app.use(mongoSanitize());

// 6. XSS prevention
app.use(xss());

// 7. HTTP parameter pollution prevention
app.use(hpp());
```

---

## When to Use This Skill

- Running `/fire-vuln-scan` against a MERN codebase
- Reviewing code for security issues
- Planning security hardening for a phase
- Building new API endpoints (check patterns before committing)

## When NOT to Use

- Agent security (prompt injection, MCP poisoning) → use `agent-security-scanner.md`
- Infrastructure security (Docker, cloud config) → separate domain
- Compliance (HIPAA, PCI-DSS) → requires specialized audit

## References

- OWASP Top 10 2021: https://owasp.org/Top10/
- Express Security Best Practices: https://expressjs.com/en/advanced/best-practice-security.html
- Mongoose Security: https://mongoosejs.com/docs/security.html
- Node.js Security Checklist: https://blog.risingstack.com/node-js-security-checklist/
- React Security: https://snyk.io/blog/10-react-security-best-practices/
