# Skill: Deployment Checklist

**Category:** Quality & Safety
**Difficulty:** Beginner
**Applies to:** Every web project going to production

---

## Before You Deploy — Run Through This List

Going live with something broken is worse than not going live at all. This checklist catches the most common deployment failures.

---

## 1. Environment & Secrets

- [ ] All secrets are in production environment variables (not in code)
- [ ] `NODE_ENV=production` is set
- [ ] Database URL points to the **production** database, not localhost
- [ ] JWT secret in production is different from your development secret
- [ ] No `.env` file is committed to git
- [ ] All required env variables are documented in `.env.example`

**How to verify:**
```bash
# List your production env vars (on Railway, Render, etc.)
# Or test locally with production values:
NODE_ENV=production node -e "console.log(process.env.DATABASE_URL)"
```

---

## 2. Database

- [ ] All migrations have been run on the production database
- [ ] Production database has been backed up before this deployment
- [ ] Seed data (categories, default settings) is in place if needed
- [ ] Database indexes exist on frequently queried columns
- [ ] Connection pooling is configured for production load

```bash
# Run migrations
npm run db:migrate

# Verify tables exist
psql $DATABASE_URL -c "\dt"
```

---

## 3. Code Quality

- [ ] All tests pass
- [ ] No `console.log` debug statements left in production code
- [ ] No hardcoded localhost URLs — use env variables for all service URLs
- [ ] Error handling is in place for all API routes
- [ ] `npm audit` shows no critical vulnerabilities

```bash
npm test
npm audit
grep -r "localhost" src/ --include="*.js" | grep -v ".env"
```

---

## 4. Security

- [ ] HTTPS is enabled (SSL certificate is valid)
- [ ] CORS is restricted to your production frontend domain
- [ ] Rate limiting is in place on auth endpoints
- [ ] Sensitive routes require authentication
- [ ] File uploads are validated and size-limited

---

## 5. Performance

- [ ] Images are compressed and sized appropriately
- [ ] Frontend assets are minified and bundled (run `npm run build`)
- [ ] Database queries use indexes where needed
- [ ] Caching is in place for data that doesn't change often (if applicable)

---

## 6. Frontend Build

- [ ] Production build completed without errors (`npm run build`)
- [ ] Build output points to production API URL, not localhost
- [ ] 404 page exists and looks professional
- [ ] Favicon is set
- [ ] Page titles are set correctly (`<title>App Name</title>`)

---

## 7. Monitoring

- [ ] Error logging is in place (console.error at minimum)
- [ ] You know how to view production logs
- [ ] You have a way to be alerted if the app goes down

**Simple health check endpoint:**
```js
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});
```

Set up an uptime monitor at [uptimerobot.com](https://uptimerobot.com) (free) to ping this every 5 minutes.

---

## 8. Post-Deployment Smoke Test

After deploying, manually test these in the browser:

- [ ] Home page loads
- [ ] User can register
- [ ] User can log in
- [ ] Core feature works end-to-end
- [ ] Logout works
- [ ] No JavaScript errors in browser console (press F12)

---

## Rollback Plan

Before every deployment, know how to roll back:

```bash
# Git: revert to previous commit
git revert HEAD
git push origin main

# Or: deploy the previous version manually
git checkout <previous-commit-hash>
git push origin main --force
```

If you changed the database schema, have a down migration ready.

---

## Deployment Platforms (Beginner-Friendly)

| Platform | Best For | Free Tier |
|----------|---------|-----------|
| [Railway](https://railway.app) | Node.js + PostgreSQL together | Yes |
| [Render](https://render.com) | Web services + databases | Yes (sleeps after inactivity) |
| [Vercel](https://vercel.com) | Frontend + serverless functions | Yes |
| [Fly.io](https://fly.io) | Dockerized apps | Yes |

---

*Fire Flow Skills Library — MIT License*
