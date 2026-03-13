# Node 18 Dependency Compatibility - CRITICAL Deployment Safety Rules

## The Problem

Production server crashed with `ReferenceError: File is not defined` after deploying code that included `open-graph-scraper@6.11.0`. The package pulled in `undici@7.20.0` which uses the `File` global — only available in Node 20+. Server runs Node 18.20.8 on shared hosting (cPanel + PM2).

### The Crash Chain
```
open-graph-scraper@6.11.0
  └── cheerio@1.2.0
       └── undici@7.20.0  ← Requires Node 20+
            └── Uses `File` global (Node 20+ only)
```

### Error Message
```
ReferenceError: File is not defined
    at node_modules/.pnpm/undici@7.20.0/node_modules/undici/lib/web/webidl/index.js:534
    at node_modules/.pnpm/undici@7.20.0/node_modules/undici/lib/web/fetch/util.js:12
```

### Why It Was Hard

1. **Silent installation** — `npm install` only WARNS about engine mismatches, it doesn't block
2. **Transitive dependency** — The breaking package (`undici`) was 3 levels deep, not directly installed
3. **Worked locally** — Development machine runs Node 20+, so it worked fine
4. **Ghost in package-lock.json** — Even after removing the package from `package.json`, `package-lock.json` retained the dependency tree
5. **Branch divergence** — The package was removed from `postgresql-dev` but `student-beautification` still had it because the deletion was never committed as a discrete change to that branch
6. **Orphaned import files** — `linkPreviewService.js` still imported `open-graph-scraper` even after the package was "removed", causing `ERR_MODULE_NOT_FOUND`

### Impact

- **Production site completely down** — all API calls failed
- **PM2 crash loop** — server process kept restarting and failing
- **Required emergency SSH intervention** — delete node_modules, package-lock.json, clean install
- **~30 minutes of downtime** for a live educational platform

---

## DO's and DON'T's

### DO

1. **Always check Node engine requirements BEFORE installing any package**
   ```bash
   npm info <package-name> engines
   # or check the package's package.json on npm/GitHub
   ```

2. **Check the FULL dependency tree for Node version requirements**
   ```bash
   npm ls --all | grep -i "engine"
   # or check transitive deps manually
   npm info <package> dependencies
   ```

3. **Delete BOTH `package-lock.json` AND `node_modules/` when debugging dependency issues**
   ```bash
   rm -f package-lock.json
   rm -rf node_modules
   npm install --omit=dev  # Clean install, production only
   ```

4. **Ensure file deletions are committed and merged across ALL branches**
   ```bash
   # After removing a file on branch A:
   git checkout branch-B
   git merge branch-A  # Ensure deletions propagate
   # OR cherry-pick the deletion commit specifically
   ```

5. **Remove ALL references when uninstalling a package** — not just `package.json`:
   - Import statements in `.js` files
   - Route registrations in `server.js`
   - Controller files
   - Service files
   - Test files

6. **Test deployment in a staging environment first** when adding new dependencies

7. **Pin major versions** for critical dependencies to prevent surprise breaking changes:
   ```json
   "open-graph-scraper": "6.8.0"  // exact version, not ^6.8.0
   ```

8. **Use `npm install --omit=dev`** on production servers (not `npm install`)

### DON'T

1. **DON'T install packages requiring Node 20+ on Node 18 servers**
   - npm only warns, it does NOT prevent installation
   - The app will crash at runtime, not at install time

2. **DON'T trust `npm install` to respect engine requirements**
   ```
   npm warn EBADENGINE Unsupported engine
   npm warn EBADENGINE   required: { node: '>=20' }
   npm warn EBADENGINE   current:  { node: 'v18.20.8' }
   ```
   These are WARNINGS, not ERRORS. Installation proceeds anyway.

3. **DON'T assume branch merges include file deletions from other branches**
   - If you deleted files on `branch-A` but never merged that commit to `branch-B`, `branch-B` still has those files
   - Merging unrelated commits does NOT retroactively include deletions

4. **DON'T just remove a package from `package.json` and assume it's gone**
   - `package-lock.json` still references it
   - `node_modules/` still contains it
   - Import statements still reference it

5. **DON'T deploy without checking server Node version first**
   ```bash
   # On server:
   node -v  # Know your version!
   ```

6. **DON'T add packages to the project without verifying they work on the PRODUCTION Node version**
   - Dev machine may run Node 20+
   - CI may run Node 20+
   - Production shared hosting may be locked to Node 18

---

## The Solution

### Root Cause

`open-graph-scraper@6.11.0` was in `server/package.json` on the `student-beautification` production branch. It was previously removed from `postgresql-dev` (development branch), but the removal never propagated to the production branch. During deployment, `npm install` pulled in `undici@7.20.0` as a transitive dependency, which crashed on Node 18.

### How to Fix (Emergency Recovery)

```bash
# SSH into server
ssh user@server

# 1. Remove the offending package from package.json
# (edit manually or use sed)

# 2. Remove ALL files that import the package
git rm server/services/linkPreviewService.js
git rm server/routes/linkPreviewRoutes.js
git rm server/controllers/linkPreviewController.js

# 3. Remove import/use from server.js
# Edit server.js to remove import and app.use() lines

# 4. Nuclear clean install
rm -f package-lock.json
rm -rf node_modules
npm install --omit=dev

# 5. Restart PM2
pm2 restart LMS-SERVER --update-env

# 6. Verify
pm2 logs LMS-SERVER --lines 20
curl -s http://localhost:5000/api/health
```

### Prevention: Pre-Deploy Dependency Check

Add this to your deployment script:
```bash
# Check for Node 20+ only packages before deploying
echo "Checking dependency compatibility with Node 18..."
npm ls --all 2>&1 | grep -i "EBADENGINE" && {
  echo "ERROR: Found packages incompatible with production Node version!"
  echo "Fix dependency issues before deploying."
  exit 1
}
```

---

## Testing the Fix

### Before (Broken)
```
pm2 logs:
ReferenceError: File is not defined
    at undici/lib/web/webidl/index.js:534
Process restarting... (crash loop)
```

### After (Fixed)
```
pm2 logs:
API available at: http://localhost:5000/api
DATABASE Connection successful!
All scheduled jobs started
```

### Verification Steps
```bash
# 1. Check no undici warnings
npm ls 2>&1 | grep undici  # Should return nothing

# 2. Check server starts
pm2 restart LMS-SERVER
pm2 logs LMS-SERVER --lines 10  # Should show "DATABASE Connection successful!"

# 3. Check API responds
curl http://localhost:5000/api/health

# 4. Check site loads
curl -s https://yoursite.com | head -20
```

---

## Known Node 18 Incompatible Packages (2025-2026)

| Package | Version | Reason | Alternative |
|---------|---------|--------|-------------|
| `undici` | >= 7.0.0 | Uses `File` global (Node 20+) | Use `undici@6.x` or `node-fetch` |
| `open-graph-scraper` | >= 6.10.0 | Pulls `undici@7` via `cheerio` | Pin to `6.8.0` or remove |
| `cheerio` | >= 1.1.0 | Pulls `undici@7` | Pin to `1.0.x` |

Add to this list as you discover more.

---

## Prevention

1. **Add `engines` field to your `package.json`:**
   ```json
   {
     "engines": {
       "node": ">=18.0.0 <20.0.0"
     }
   }
   ```

2. **Set `.npmrc` to enforce engine checks:**
   ```ini
   engine-strict=true
   ```
   This makes `npm install` FAIL instead of warn when engine requirements don't match.

3. **Document server Node version in README/CLAUDE.md**

4. **Check dependencies before every deploy** (see script above)

---

## Related Patterns

- [PM2_ENVIRONMENT_VARIABLE_CACHING.md](./PM2_ENVIRONMENT_VARIABLE_CACHING.md) - PM2 restart gotchas
- [deployment-changes-not-applying.md](./deployment-changes-not-applying.md) - Stale deployment debugging
- [env-file-management-production-local.md](./env-file-management-production-local.md) - Environment management

---

## Common Mistakes to Avoid

- Assuming `npm install` will prevent incompatible packages (it won't)
- Only removing the package from `package.json` without cleaning `node_modules` and `package-lock.json`
- Forgetting to remove import statements and route registrations for deleted packages
- Not checking that file deletions propagated across git branches
- Testing only on dev machine (Node 20+) and assuming production (Node 18) will work
- Running `npm install` instead of `npm install --omit=dev` on production

---

## Resources

- [Node.js Releases](https://nodejs.org/en/about/releases/) - EOL dates and version info
- [npm engine-strict](https://docs.npmjs.com/cli/v10/using-npm/config#engine-strict) - Enforce engine checks
- [undici breaking changes](https://github.com/nodejs/undici/releases) - Version requirements

---

## Difficulty Level

Diagnosing: ⭐⭐⭐⭐ (4/5) - Transitive dependency 3 levels deep, silent installation, works locally
Fixing: ⭐⭐ (2/5) - Once identified, nuclear clean install resolves it
Preventing: ⭐ (1/5) - Add `.npmrc` with `engine-strict=true`

---

**Author Notes:**
This crashed a live educational platform (schooloftheprophets.club) on February 2, 2026. The package had been "removed" from the development branch weeks earlier but the deletion never made it to the production branch. The deploy script ran `npm install` which happily installed the incompatible dependency. PM2 went into a crash loop. ~30 minutes of downtime.

The key lesson: **npm is not your safety net on Node version compatibility. YOU are.**
