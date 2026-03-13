---
name: deployment-changes-not-applying
category: deployment-security
version: 1.0.0
contributed: 2026-01-24
contributor: my-other-project
last_updated: 2026-01-24
tags: [deployment, pm2, cpanel, ssh, version, cache, mern, troubleshooting]
difficulty: easy
---

# Deployment Changes Not Applying

## Problem

After deploying changes to production server (git pull, npm run build), the application still shows old content. Common symptoms:

- App shows old version number in footer/settings
- Update check claims "You are up to date!" but it's showing an old version
- Stripe/PayPal still in TEST MODE after deploying live keys
- .env changes seem to "revert" after deployment
- UI changes don't appear despite successful git pull
- API behavior unchanged despite controller updates

**Why this happens:** There are multiple independent systems that need updating, and missing ANY of them causes stale content.

## Solution Pattern

### The 5-Point Deployment Checklist

Every deployment must address ALL of these:

| # | Item | What Goes Wrong | Fix |
|---|------|-----------------|-----|
| 1 | **Git Pull** | Code not updated | `git pull origin branch` |
| 2 | **.env Update** | Environment vars unchanged | Manual edit via `nano server/.env` |
| 3 | **Client Build** | Old JS/CSS served | `cd client && npm run build` |
| 4 | **Copy Files** | Old files in public_html | `cp -r dist/* ~/public_html/` AND `cp version.json ~/public_html/` |
| 5 | **PM2 Restart** | Server running old code | `pm2 restart all` |

### Critical Understanding

**.env files are NOT in git!**
- `git pull` does NOT update `.env` files
- `.env` files are in `.gitignore` (for security)
- You must manually edit `server/.env` on the production server
- This is why "Stripe live keys" don't appear after deploy

**version.json must be copied separately!**
- It's in the repo root, not in `client/dist/`
- If not copied to `public_html/`, version check always says "up to date"
- The update system reads `https://yourdomain.com/version.json`

## Code Example

### Before (Incomplete - Changes Won't Apply)

```bash
# This deployment is INCOMPLETE
ssh user@server.example.com
cd ~/mern-app
git pull origin main
cd client && npm run build
cp -r client/dist/* ~/public_html/
# Done? NO! Missing critical steps:
# - .env not updated (still has test keys)
# - version.json not copied (version check broken)
# - PM2 not restarted (server running old code)
```

### After (Complete Deployment)

```bash
# COMPLETE deployment process
ssh user@server.example.com

# 1. Navigate to project
cd ~/mern-app

# 2. Pull latest code
git pull origin student-beautification

# 3. UPDATE .ENV (critical - not in git!)
nano server/.env
# Update: STRIPE_SECRET_KEY, JWT_SECRET, etc.
# Save and exit

# 4. Rebuild client
cd client && npm run build && cd ..

# 5. Copy ALL files to public_html
cp -r client/dist/* ~/public_html/
cp version.json ~/public_html/    # DON'T FORGET THIS!

# 6. Restart server (picks up .env changes)
pm2 restart all

# 7. Verify deployment
pm2 logs --lines 20
curl https://yourdomain.com/version.json
```

## Diagnostic Commands

When changes aren't appearing, run these diagnostics:

```bash
# Check what version the public sees
curl https://yourdomain.com/version.json

# Check what version is in the repo
cat ~/mern-app/version.json

# Check if PM2 is running latest code
pm2 status
pm2 logs --lines 50

# Check .env has correct values (without exposing secrets)
grep "NODE_ENV" ~/mern-app/server/.env
grep "STRIPE_SECRET_KEY" ~/mern-app/server/.env | cut -c1-30
# Should show: STRIPE_SECRET_KEY=sk_live_... (not sk_test_)

# Check file timestamps in public_html
ls -la ~/public_html/version.json
ls -la ~/public_html/index.html
```

## Common Root Causes

### 1. Version Check Says "Up to Date" But Wrong Version

**Cause:** `version.json` not copied to `public_html/`

**Fix:**
```bash
cp ~/mern-app/version.json ~/public_html/
```

### 2. Stripe/PayPal Still in Test Mode

**Cause:** `.env` file not updated on server (it's not in git)

**Fix:**
```bash
nano ~/mern-app/server/.env
# Change: STRIPE_SECRET_KEY=sk_test_...
# To:     STRIPE_SECRET_KEY=sk_live_...
pm2 restart all
```

### 3. UI Changes Not Showing

**Cause:** Browser cache OR build not copied

**Fix:**
```bash
# Rebuild and copy
cd ~/mern-app/client && npm run build && cd ..
cp -r client/dist/* ~/public_html/

# Then hard refresh browser: Ctrl+Shift+R
# Or test in incognito window
```

### 4. API Behavior Unchanged

**Cause:** PM2 not restarted (still running old code in memory)

**Fix:**
```bash
pm2 restart all
pm2 logs --lines 20  # Verify new code loaded
```

### 5. "Changes Keep Reverting"

**Cause:** Misunderstanding - .env is NOT in git. Each server has its own .env.

**Reality:**
- Local `.env` ≠ Production `.env`
- `git pull` never touches `.env` files
- You must maintain production `.env` separately
- Create `.env.productionbackup` locally as reference

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│           DEPLOYMENT QUICK REFERENCE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ssh user@server                                            │
│  cd ~/mern-app                                              │
│  git pull origin [branch]                                   │
│  nano server/.env                    # Update if needed     │
│  cd client && npm run build && cd ..                        │
│  cp -r client/dist/* ~/public_html/                         │
│  cp version.json ~/public_html/      # DON'T FORGET!        │
│  pm2 restart all                                            │
│  pm2 logs --lines 20                 # Verify               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  VERIFY:                                                    │
│  curl https://yourdomain.com/version.json                   │
│  Test in incognito window (bypass cache)                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## When to Use

- After deploying but app shows old version
- "Changes aren't sticking" after deployment
- Update check says up-to-date but version is outdated
- Payment processor stuck in test mode after deploy
- Debugging why production doesn't match local

## When NOT to Use

- Local development issues (use `npm run dev`)
- CI/CD automated deployments (pipelines handle this)
- Docker/Kubernetes deployments (different paradigm)
- Issues with code itself (not deployment)

## Common Mistakes

1. **Assuming git pull updates .env** - It doesn't. .env is in .gitignore.
2. **Forgetting version.json** - It's separate from client/dist.
3. **Not restarting PM2** - Server keeps running old code in memory.
4. **Testing without clearing cache** - Browser shows cached content.
5. **Editing wrong .env** - Server has its own .env, not synced with local.

## Related Skills

- [env-file-management-production-local](./env-file-management-production-local.md) - Managing .env files
- [react-production-deployment-desktop-guide](./react-production-deployment-desktop-guide.md) - Full deployment guide

## References

- PM2 Documentation: https://pm2.keymetrics.io/docs/usage/quick-start/
- Contributed from: my-other-project project
