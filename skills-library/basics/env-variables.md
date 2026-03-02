# Skill: Environment Variables

**Category:** Basics
**Difficulty:** Beginner
**Applies to:** Every project

---

## The Problem

You need a database password, an API key, or a secret token in your code.
If you type it directly into your code and push to GitHub, **anyone can see it**.
Even if you delete it later, it stays in the git history forever.

---

## The Solution: `.env` Files

Store secrets in a `.env` file. Never commit that file to git.

### Step 1 — Create `.env` in your project root

```
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
JWT_SECRET=some-long-random-string-here
STRIPE_KEY=sk_live_abc123
PORT=3000
```

### Step 2 — Add `.env` to `.gitignore`

```
# .gitignore
.env
.env.local
.env.production
```

Do this **before** your first commit. Once a secret is committed, you must rotate it (generate a new one) — the old one is compromised.

### Step 3 — Read variables in your code

**Node.js:**
```js
// Install: npm install dotenv
require('dotenv').config();

const dbUrl = process.env.DATABASE_URL;
const port = process.env.PORT || 3000;
```

**Python:**
```python
# Install: pip install python-dotenv
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv('DATABASE_URL')
```

### Step 4 — Create `.env.example` for teammates

This file IS committed. It shows what variables are needed, but with no real values:

```
DATABASE_URL=postgresql://user:password@localhost:5432/yourdb
JWT_SECRET=replace-with-a-long-random-string
STRIPE_KEY=sk_live_your-key-here
PORT=3000
```

---

## Rules to Never Break

| Rule | Why |
|------|-----|
| Never commit `.env` | Secrets in git are permanent |
| Always commit `.env.example` | Teammates need to know what variables exist |
| Rotate any key that was ever committed | Assume it was seen the moment it was pushed |
| Use different secrets for dev and production | A leaked dev key should not touch production |

---

## Quick Check

Before every commit, run:
```bash
git diff --cached | grep -i "password\|secret\|key\|token"
```
If you see real values, stop and move them to `.env`.

---

*Fire Flow Skills Library — MIT License*
