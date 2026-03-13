# Skill: Form Validation

**Category:** Common Tasks
**Difficulty:** Beginner
**Applies to:** Any full-stack project

---

## The Rule

**Always validate on the server. Frontend validation is convenience, not security.**

A user can bypass any frontend check by using curl or editing the browser. The server is your last line of defense.

---

## Layer 1: Frontend Validation (User Experience)

Give instant feedback without a round-trip to the server:

```html
<form id="signup-form">
  <input type="text" id="name" required minlength="2" maxlength="100" />
  <input type="email" id="email" required />
  <input type="password" id="password" required minlength="8" />
  <button type="submit">Sign Up</button>
  <p id="error-msg" style="color:red; display:none;"></p>
</form>
```

```js
document.getElementById('signup-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const error = document.getElementById('error-msg');
  error.style.display = 'none';

  const name = document.getElementById('name').value.trim();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;

  // Client-side checks
  if (name.length < 2) {
    error.textContent = 'Name must be at least 2 characters';
    error.style.display = 'block';
    return;
  }
  if (password.length < 8) {
    error.textContent = 'Password must be at least 8 characters';
    error.style.display = 'block';
    return;
  }

  // Send to server
  const res = await fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password })
  });

  const data = await res.json();
  if (!res.ok) {
    error.textContent = data.error;
    error.style.display = 'block';
  }
});
```

---

## Layer 2: Server Validation (Security)

```js
// Simple manual validation
router.post('/register', async (req, res) => {
  const { name, email, password } = req.body;
  const errors = [];

  if (!name || name.trim().length < 2)
    errors.push('Name must be at least 2 characters');

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
    errors.push('Valid email required');

  if (!password || password.length < 8)
    errors.push('Password must be at least 8 characters');

  if (errors.length > 0)
    return res.status(400).json({ error: errors[0] }); // or send all: errors

  // Proceed with registration...
});
```

---

## Layer 2 (Alternative): Using a Validation Library

For larger projects, use [Zod](https://zod.dev) (Node.js):

```bash
npm install zod
```

```js
const { z } = require('zod');

const registerSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.string().email(),
  password: z.string().min(8),
});

router.post('/register', async (req, res) => {
  const result = registerSchema.safeParse(req.body);

  if (!result.success) {
    const message = result.error.errors[0].message;
    return res.status(400).json({ error: message });
  }

  const { name, email, password } = result.data;
  // Proceed...
});
```

---

## Common Fields and Their Rules

| Field | Rules |
|-------|-------|
| Name | Min 2 chars, max 100, no HTML tags |
| Email | Valid format, lowercase, max 255 chars |
| Password | Min 8 chars, at least 1 number or symbol |
| Phone | Digits only after stripping spaces/dashes |
| URL | Must start with `http://` or `https://` |
| Price | Number, min 0, max 2 decimal places |
| Date | Valid date, not in the past (for future events) |

---

## What NOT to Validate On

- **Never trust `Content-Type` headers alone** — read and validate the actual body
- **Never trust `req.params.id`** — always parse as integer: `parseInt(req.params.id, 10)`
- **Never trust file extensions** — check MIME type server-side for uploads

---

## Sanitization vs Validation

- **Validation** — reject bad input ("this email is invalid")
- **Sanitization** — clean input before using it (`name.trim()`, strip HTML tags)

Do both. Validate first, then sanitize before storing.

---

*Fire Flow Skills Library — MIT License*
