# Production Recovery: Cherry-Pick Pattern for Dependency Crashes

## The Problem

Production server crashed with 503 error after deployment due to a missing npm dependency (`openai` package). The server code imported a package that wasn't installed, causing immediate crash on startup.

### Error Message
```
Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'openai' imported from
/home/schoolo2/mern-app/server/services/ai/EmbeddingService.js
```

### Why It Was Hard

- The full branch (`student-beautification`) contained both:
  - **Client-side changes** - Safe, already built into static files
  - **Server-side changes** - Introduced the breaking dependency
- Couldn't simply revert everything - would lose valid client features
- Production was DOWN while debugging
- Needed to separate "what's safe to deploy" from "what's breaking"

### Impact

- **503 error** - Site completely inaccessible
- **PM2 restart loops** - Server kept crashing on startup
- **User-facing downtime** - Production site offline

---

## The Solution

### Strategy: Separate Client and Server Deployments

When server code breaks but client changes are safe:
1. Revert server to last known stable commit
2. Cherry-pick ONLY client-side commits
3. Build client separately
4. Deploy static files to public_html
5. Leave server on stable code

### Root Cause

The `student-beautification` branch had AI service commits that imported `openai`:
```javascript
// server/services/ai/EmbeddingService.js
import OpenAI from 'openai';  // Package NOT in package.json!
```

When `git reset --hard origin/student-beautification` pulled this code, the server crashed because `openai` wasn't installed.

### Step-by-Step Recovery

```bash
# 1. SSH into production
ssh schoolo2@server1.tiberiusprimus.com
cd ~/mern-app

# 2. Check PM2 logs to identify the error
pm2 logs --lines 50

# 3. Find last stable commit (before breaking changes)
git log --oneline -20
# Identify commit before problematic code (e.g., 426ec7c)

# 4. Revert server to stable commit
git fetch origin
git reset --hard 426ec7c

# 5. Cherry-pick ONLY client-side commits (use --no-commit to batch)
git cherry-pick --no-commit 30dc240  # Client change 1
git cherry-pick --no-commit 33c5b5e  # Client change 2

# 6. Build the client (generates static files)
cd client
npm run build

# 7. Deploy static files to public_html
cd ..
cp -r client/dist/* ~/public_html/
cp version.json ~/public_html/

# 8. Reset working directory (don't keep cherry-picked server changes)
git checkout -- .

# 9. Restart server (now on stable code)
pm2 restart LMS-SERVER --update-env

# 10. Verify
curl -I https://yoursite.com
pm2 status
```

### Key Insight

**Client builds are independent of server runtime.** Even if server code has issues, you can:
- Build client with new features locally or in a clean environment
- Copy the built static files (`dist/`) to production
- Keep server on older, stable code

---

## Testing the Fix

### Before Recovery
```bash
pm2 status
# LMS-SERVER: errored (restart loop)

curl -I https://schooloftheprophets.club
# HTTP/1.1 503 Service Unavailable
```

### After Recovery
```bash
pm2 status
# LMS-SERVER: online

curl -I https://schooloftheprophets.club
# HTTP/1.1 200 OK
```

### Verification Checklist
- [ ] PM2 shows server "online" (not errored/stopped)
- [ ] Site responds with 200, not 503
- [ ] New client features visible (the cherry-picked changes)
- [ ] Server logs clean (no crash loops)

---

## Prevention

### Before Deploying Server Code

1. **Check new dependencies exist in package.json**
   ```bash
   # On dev machine before pushing
   grep '"openai"' server/package.json
   ```

2. **Test server startup locally**
   ```bash
   cd server && npm install && npm start
   ```

3. **Check for Node version compatibility**
   ```bash
   npm info <package> engines
   # Ensure compatible with Node 18.20.8 (production)
   ```

### Deployment Checklist

- [ ] All imported packages are in package.json
- [ ] `npm install` runs clean on fresh clone
- [ ] Server starts without errors locally
- [ ] Node version compatibility verified

---

## When to Use This Pattern

| Scenario | Use This Pattern? |
|----------|-------------------|
| Server crashes due to missing dependency | Yes |
| Server crashes due to code bug | Yes |
| Client build fails | No (fix client first) |
| Database migration issue | No (different recovery) |
| Need to rollback everything | No (just `git reset --hard`) |

---

## Related Patterns

- [NODE18_DEPENDENCY_COMPATIBILITY.md](./NODE18_DEPENDENCY_COMPATIBILITY.md) - Checking package compatibility

---

## Common Mistakes to Avoid

- **Don't `git reset --hard` blindly** - Check what's in the target commit first
- **Don't forget to rebuild client** - Cherry-picking changes working directory, need fresh build
- **Don't leave cherry-pick state open** - Either commit or `git checkout -- .` to clean up
- **Don't assume server restart fixes everything** - Check logs first to understand the error

---

## Time to Implement

**5-15 minutes** once you identify the stable commit and breaking commits

## Difficulty Level

**3/5** - Requires understanding of git operations and deployment pipeline

---

**Author Notes:**
This pattern saved us during a production crash on Feb 4, 2026. The key realization was that client static files are completely independent of server runtime - you can build them anywhere and just copy them over. This separation is powerful for recovery scenarios.

The original issue was AI services importing `openai` without it being in package.json. The services were removed entirely since they weren't needed. But this pattern works for ANY server-side dependency or code issue.

**Remember:** When production is down, speed matters. Have this pattern in your toolkit.
