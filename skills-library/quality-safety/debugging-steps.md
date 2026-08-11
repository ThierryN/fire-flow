# Skill: Debugging Steps

**Category:** Quality & Safety
**Difficulty:** Beginner
**Applies to:** Every project

---

## The Problem

Most developers debug by guessing — changing random things until it works. This wastes hours and often introduces new bugs. Systematic debugging finds the problem in minutes.

---

## The 5-Step Method

### Step 1 — Read the Error Message

The error message tells you exactly what went wrong. Read the whole thing, including the stack trace.

```
TypeError: Cannot read properties of undefined (reading 'email')
    at getUserEmail (routes/users.js:24:23)
    at router.get (/routes/users.js:18:20)
```

This tells you:
- **What:** Trying to read `.email` from something that is `undefined`
- **Where:** `routes/users.js` line 24
- **How it got there:** Called from line 18

Go to line 24. `user` is `undefined` — the database returned no rows.

---

### Step 2 — Reproduce it Reliably

Before fixing, make sure you can make the bug happen on purpose.

- What exact steps trigger it?
- Does it happen every time, or randomly?
- Does it happen in development but not production (or vice versa)?

A bug you can reproduce consistently is a bug you can fix.

---

### Step 3 — Isolate Where It Breaks

Narrow down where in the code the problem starts. Use `console.log` to trace values:

```js
router.get('/users/:id', async (req, res) => {
  console.log('1. Request received, id:', req.params.id);

  const result = await db.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
  console.log('2. DB result:', result.rows);

  const user = result.rows[0];
  console.log('3. User:', user); // if undefined, the query returned nothing

  res.json({ email: user.email }); // crashes if user is undefined
});
```

Work from the outside in. Log at the start, then in the middle, then closer to the crash until you find where the data goes wrong.

---

### Step 4 — Form a Hypothesis and Test It

Once you know where, make a specific prediction about why:

> "I think the user query returns nothing because the ID from the URL is a string, but the database expects an integer."

Test it:
```js
console.log(typeof req.params.id); // 'string' — confirmed!
// Fix: parseInt(req.params.id, 10)
```

If your hypothesis is wrong, form a new one. Don't just try random fixes.

---

### Step 5 — Fix, Verify, and Clean Up

- Make the smallest change that fixes the problem
- Verify the original bug is gone
- Check that nothing else broke
- Remove all the `console.log` statements you added
- Write a test so it can't come back silently

---

## Common Bug Patterns and Their Fixes

| Symptom | Likely Cause | How to Check |
|---------|-------------|--------------|
| `undefined` where you expect an object | Database returned 0 rows | Log the query result |
| `Cannot read property of null` | Accessing a property before data loads | Check for null before accessing |
| Fetch returns HTML instead of JSON | API route not found (404) | Check the URL and router setup |
| Changes not showing up | Old code cached / wrong file edited | Hard refresh, check file path |
| Works locally, breaks in production | Missing env variable | Check production env config |
| CORS error in browser | Backend not allowing your frontend origin | Check CORS middleware |
| `jwt malformed` | Token corrupted or wrong format | Log the raw Authorization header |

---

## The Console is Your Friend

```js
// Log an object clearly
console.log('user:', JSON.stringify(user, null, 2));

// Log with a timestamp
console.log(new Date().toISOString(), 'step reached');

// Log type and value
console.log('id type:', typeof id, 'value:', id);

// Trace where a function is called from
console.trace('Called from:');
```

---

## When You've Been Stuck for 20 Minutes

1. **Explain the problem out loud** (rubber duck debugging) — saying it out loud often reveals the answer
2. **Take a 10-minute break** — your brain keeps working
3. **Search the exact error message** in quotes on Google or Stack Overflow
4. **Read the documentation** for the library you're using — check if your usage matches the examples
5. **Ask for help** — share the error, the code, and what you've already tried

---

## What Not to Do

- Don't comment out code randomly hoping the bug disappears
- Don't change multiple things at once — you won't know what fixed it
- Don't ignore warnings in the console — they often point to the real problem
- Don't assume the library is broken — it's almost always your code

---

*Fire Flow Skills Library — MIT License*
