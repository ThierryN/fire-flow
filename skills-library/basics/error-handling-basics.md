# Skill: Error Handling Basics

**Category:** Basics
**Difficulty:** Beginner
**Applies to:** Node.js, Python, any backend

---

## The Problem

When code crashes, users see a blank screen or a raw error message with your file paths exposed. Worse — you have no idea it happened because nothing was logged.

---

## The Solution: Catch, Log, Respond

Three things happen when an error occurs:
1. **Catch** it — don't let it bubble up and crash the app
2. **Log** it — record enough detail to debug later
3. **Respond** — send a clean message to the user, never the raw error

---

## Pattern 1: Try/Catch (Node.js)

```js
// BAD — no error handling
app.get('/users/:id', async (req, res) => {
  const user = await db.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
  res.json(user);
});

// GOOD — caught, logged, clean response
app.get('/users/:id', async (req, res) => {
  try {
    const user = await db.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
    if (!user) return res.status(404).json({ error: 'User not found' });
    res.json(user);
  } catch (err) {
    console.error('GET /users/:id failed:', err.message);
    res.status(500).json({ error: 'Something went wrong. Please try again.' });
  }
});
```

---

## Pattern 2: Global Error Middleware (Express)

Catch every unhandled error in one place instead of repeating try/catch everywhere:

```js
// Put this LAST in your app, after all routes
app.use((err, req, res, next) => {
  console.error(`[${new Date().toISOString()}] ${req.method} ${req.path}:`, err);

  const status = err.status || 500;
  const message = err.isOperational ? err.message : 'Something went wrong';
  res.status(status).json({ error: message });
});
```

Then in your routes, just call `next(err)` to hand off to this handler:

```js
app.get('/users/:id', async (req, res, next) => {
  try {
    const user = await db.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
    res.json(user);
  } catch (err) {
    next(err); // passes to global handler
  }
});
```

---

## Pattern 3: Try/Except (Python)

```python
# BAD
def get_user(user_id):
    return db.query(f"SELECT * FROM users WHERE id = {user_id}")

# GOOD
def get_user(user_id):
    try:
        user = db.query("SELECT * FROM users WHERE id = %s", (user_id,))
        if not user:
            raise ValueError(f"User {user_id} not found")
        return user
    except ValueError as e:
        print(f"[WARNING] {e}")
        raise
    except Exception as e:
        print(f"[ERROR] get_user({user_id}) failed: {e}")
        raise RuntimeError("Could not retrieve user") from e
```

---

## HTTP Status Codes to Know

| Code | Meaning | Use When |
|------|---------|---------|
| 200 | OK | Success |
| 201 | Created | New resource created |
| 400 | Bad Request | User sent invalid data |
| 401 | Unauthorized | Not logged in |
| 403 | Forbidden | Logged in but no permission |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Your code broke |

---

## Rules

- **Never send raw error objects to the client** — they expose file paths and stack traces
- **Always log server errors** — you need to know when things break
- **Distinguish user errors (4xx) from server errors (5xx)** — user errors are their fault; server errors are yours
- **Never swallow errors silently** — `catch (err) {}` with nothing inside is worse than no try/catch

---

*Fire Flow Skills Library — MIT License*
