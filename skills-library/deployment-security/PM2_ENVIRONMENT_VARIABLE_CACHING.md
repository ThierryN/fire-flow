# PM2 Environment Variable Caching - Root Cause & Solution

## The Problem

Environment variables in `.env` files are not being reloaded when you restart a PM2 process.
After editing `.env` on the server and running `pm2 restart`, the application still uses the OLD values.

### Common Error Messages

```
Error: Stripe is not configured. Please set STRIPE_SECRET_KEY environment variable.
```

```
Error: DATABASE_URL not set
```

```
Error: JWT_SECRET missing
```

### Why It Was Hard

- **Silent failure** - No errors during restart, app runs but uses wrong values
- **Intermittent appearance** - Works after fresh `pm2 start`, breaks after `pm2 restart`
- **Misleading debugging** - You check `.env`, see correct values, but app doesn't use them
- **Confidence trap** - "I definitely set that env var" but PM2 ignores it

### Impact

- Production services fail silently
- Payment processing stops (Stripe)
- Auth fails (JWT_SECRET)
- Database connections fail
- Hours wasted re-editing `.env` files that aren't actually the problem

---

## The Solution

### Root Cause

**PM2 caches environment variables when a process is first started.**

When you run `pm2 restart`:
1. PM2 stops the process
2. PM2 starts a NEW process
3. PM2 uses the **CACHED** environment from the original `pm2 start`
4. Your `.env` file changes are **IGNORED**

This is by design for performance, but causes this exact issue.

### How to Fix

**Always use `--update-env` flag when restarting:**

```bash
# WRONG - does NOT reload .env
pm2 restart app-name

# CORRECT - reloads .env file
pm2 restart app-name --update-env
```

### Alternative: Full Stop/Start Cycle

If `--update-env` doesn't work (rare edge cases):

```bash
# Nuclear option - delete and restart fresh
pm2 delete app-name
cd /path/to/app
pm2 start server.js --name app-name
pm2 save
```

### Code Example: Deploy Script Fix

**Before (broken):**
```bash
# Restart PM2 processes
echo "Restarting PM2..."
pm2 restart LMS-SERVER
```

**After (working):**
```bash
# Restart PM2 processes with --update-env to reload .env file
# IMPORTANT: Without --update-env, PM2 uses cached environment variables!
echo "Restarting PM2 with updated environment..."
pm2 restart LMS-SERVER --update-env
```

---

## Testing the Fix

### Verify Environment is Loaded

```bash
# Check what env vars PM2 process is actually using
pm2 env <app-id>

# Or check logs for initialization messages
pm2 logs app-name --lines 30 | grep -E "(Loaded|initialized|configured)"
```

### Test Procedure

1. SSH to server
2. Edit `.env` file - change a visible value (like `NODE_ENV=test`)
3. Run `pm2 restart app-name --update-env`
4. Check logs to verify new value is used
5. Restore original value and restart again with `--update-env`

### Expected Output

```
[Server] Loaded environment from: .env
✅ Stripe initialized successfully
✅ Database connected
```

---

## Prevention

### 1. Update All Deploy Scripts

Find and replace all `pm2 restart` commands:

```bash
# Find all occurrences
grep -r "pm2 restart" scripts/

# Replace with --update-env version
sed -i 's/pm2 restart all/pm2 restart all --update-env/g' scripts/*.sh
```

### 2. Use Ecosystem File

Create `ecosystem.config.js` with explicit env vars:

```javascript
module.exports = {
  apps: [{
    name: 'LMS-SERVER',
    script: 'server.js',
    env_file: '.env',  // Some PM2 versions support this
    watch: false,
    instances: 1,
    autorestart: true,
  }]
};
```

Then restart with:
```bash
pm2 restart ecosystem.config.js --update-env
```

### 3. Document in Project README

Add this to your deployment docs:

```markdown
## PM2 Restart Commands

⚠️ **CRITICAL:** Always use `--update-env` when restarting PM2!

```bash
# Correct way to restart (reloads .env)
pm2 restart LMS-SERVER --update-env

# WRONG - does NOT reload .env
pm2 restart LMS-SERVER
```
```

### 4. Add to CLAUDE.md

Ensure AI agents know about this:

```markdown
### PM2 Commands (on server)
```bash
pm2 restart LMS-SERVER --update-env     # USE THIS!
# ⚠️ Plain 'pm2 restart' does NOT reload .env!
```
```

---

## Related Patterns

- [Node.js dotenv Configuration](../patterns-standards/DOTENV_BEST_PRACTICES.md)
- [Production Deployment Checklist](./PRODUCTION_DEPLOYMENT_CHECKLIST.md)
- [Environment Variable Security](./ENV_VAR_SECURITY.md)

---

## Common Mistakes to Avoid

- ❌ **Using `pm2 restart` without `--update-env`** - The #1 cause of this issue
- ❌ **Assuming `.env` changes take effect immediately** - They don't with PM2
- ❌ **Re-editing `.env` when it's already correct** - Check PM2's cached env instead
- ❌ **Blaming dotenv package** - The package works fine, PM2 caches the result
- ❌ **Using `pm2 reload`** - This also doesn't reload env vars

---

## PM2 Commands Reference

| Command | Reloads .env? | Use Case |
|---------|--------------|----------|
| `pm2 restart app` | ❌ No | Quick restart, no env changes |
| `pm2 restart app --update-env` | ✅ Yes | After editing .env file |
| `pm2 reload app` | ❌ No | Zero-downtime restart |
| `pm2 reload app --update-env` | ✅ Yes | Zero-downtime + env reload |
| `pm2 delete app && pm2 start` | ✅ Yes | Nuclear option, always fresh |

---

## Resources

- [PM2 Documentation: Environment Variables](https://pm2.keymetrics.io/docs/usage/environment/)
- [PM2 GitHub Issue: env vars not updating](https://github.com/Unitech/pm2/issues/2252)
- [Node.js dotenv Documentation](https://www.npmjs.com/package/dotenv)

---

## Time to Implement

**5 minutes** - Just add `--update-env` to your restart commands

## Difficulty Level

⭐ (1/5) - Trivial fix once you know about it, but VERY hard to diagnose

---

**Author Notes:**

This issue cost hours of debugging before discovering the root cause. The symptoms are extremely misleading - you see correct values in `.env`, you restart PM2, and it still doesn't work. Natural instinct is to check the `.env` file again, or suspect the application code.

The key insight: **PM2 is a process manager that caches state.** Once you understand that, the fix is obvious.

Every deployment script, every runbook, every piece of documentation that mentions `pm2 restart` should include `--update-env`. Make it muscle memory.

**Discovery date:** January 2026
**Project:** MERN Community LMS
**Symptom:** "Stripe is not configured" error persisting after fixing .env

---

*When in doubt: `pm2 restart --update-env`*
