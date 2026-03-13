---
name: env-file-management-production-local
category: deployment-security
version: 1.0.0
contributed: 2026-01-24
contributor: my-other-project
last_updated: 2026-01-24
tags: [environment, dotenv, security, deployment, vite, production, secrets, mern]
difficulty: medium
---

# Environment File Management: Production vs Local

## Problem

Production server uses wrong environment (e.g., TEST Stripe keys instead of LIVE keys). Common symptoms:

- Stripe checkout shows "TEST MODE" badge in production
- Checkout session URLs contain `cs_test_` instead of `cs_live_`
- Payment processors reject transactions
- API keys suddenly "stop working" after deployment

**Root Cause**: Developers assume `.env` files are deployed with git, but they are NOT tracked in version control. Production server's `.env` must be manually configured via SSH.

## Solution Pattern

### 1. File Structure (Server)

```
server/
├── .env                    # Current environment (NOT in git)
├── .env.local              # Local dev overrides (NOT in git)
├── .env.productionbackup   # Backup of prod config (NOT in git)
├── .env.localbackup        # Backup of local config (NOT in git)
└── .env.example            # Template with placeholders (IN git)
```

### 2. File Structure (Client/Vite)

```
client/
├── .env                    # Local development (NOT in git)
├── .env.production         # Production build values (IN git - PUBLIC keys only!)
└── .env.example            # Template for developers (IN git)
```

### 3. Critical Rules

**Server .env files (NEVER in git):**
- Contains SECRET keys (sk_live_, client_secret, JWT_SECRET)
- Must be manually configured on each server via SSH
- Create backups: `.env.productionbackup`, `.env.localbackup`

**Client .env.production (IN git):**
- Contains ONLY publishable/public keys (pk_live_, client_id)
- Used by Vite during `npm run build`
- Safe to commit because these are public-facing

**VITE_ Prefix Required:**
- All client-side variables MUST have `VITE_` prefix
- Without prefix, Vite will NOT expose the variable to the frontend

### 4. .gitignore Configuration

```gitignore
# Environment files - NEVER commit secrets
.env
.env.local
.env.development
.env.development.local
.env.test
.env.test.local
.env.production.local
*.local

# Explicit backups
server/.env.productionbackup
server/.env.localbackup
client/.env.productionbackup
```

**Note:** `client/.env.production` is intentionally NOT in .gitignore because it contains only public keys.

## Code Example

### Before (Problematic - secrets exposed)

```env
# client/.env.production (WRONG - secrets in client!)
VITE_STRIPE_SECRET_KEY=sk_live_xxx    # NEVER do this!
VITE_PAYPAL_SECRET=EIhBzb...          # NEVER do this!
```

### After (Correct - public keys only)

```env
# client/.env.production (CORRECT - public keys only)
VITE_API_URL=https://yourdomain.com/api
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_51KFrTBB...
VITE_PAYPAL_CLIENT_ID=AVPCNK2OFrV3Wx46...
VITE_SITE_NAME=My App
```

```env
# server/.env (CORRECT - secrets on server only)
STRIPE_SECRET_KEY=sk_live_51KFrTBB...
PAYPAL_CLIENT_SECRET=EIhBzb...
JWT_SECRET=y2300cd87b131c28...
```

## Manual Deployment Process (SSH)

When deploying, you must manually update the production server's `.env`:

```bash
# 1. SSH into production server
ssh user@server.example.com

# 2. Navigate to app directory
cd ~/mern-app

# 3. Pull code changes (does NOT include .env)
git pull origin main

# 4. Edit server .env with production values
nano server/.env

# 5. Update these values:
#    - STRIPE_SECRET_KEY=sk_live_...
#    - JWT_SECRET=your-secure-secret
#    - NODE_ENV=production
#    - All other production-specific values

# 6. Rebuild client
cd client && npm run build && cd ..

# 7. Copy built files to public directory
cp -r client/dist/* ~/public_html/

# 8. Restart application
pm2 restart all

# 9. Verify
pm2 logs --lines 20
```

## Debugging "Wrong Environment" Issues

### Step 1: Check Server Key Prefix

```bash
# On production server
grep STRIPE_SECRET_KEY ~/mern-app/server/.env
# Should show: sk_live_... NOT sk_test_...
```

### Step 2: Check Client Build Keys

```bash
# In client/.env.production (local repo)
grep VITE_STRIPE ~/client/.env.production
# Should show: pk_live_... NOT pk_test_...
```

### Step 3: Verify Checkout Session

- `cs_test_` in URL = Server using TEST key
- `cs_live_` in URL = Server using LIVE key

The checkout session prefix is determined by the SERVER's secret key, not the client's publishable key.

## When to Use

- Setting up new MERN/Vite projects
- Debugging "wrong environment" issues (test vs live keys)
- After losing .env configuration
- Training new team members on environment management
- Creating deployment documentation

## When NOT to Use

- Projects using cloud secrets managers (AWS Secrets Manager, HashiCorp Vault)
- Containerized deployments with environment injection (Docker secrets, K8s ConfigMaps)
- Single-environment projects with no prod/dev separation

## Common Mistakes

1. **Assuming .env deploys with git** - It doesn't. Manual SSH update required.
2. **Putting secrets in client .env** - Client code is public. Never put secrets there.
3. **Forgetting VITE_ prefix** - Variable won't be exposed to frontend.
4. **Not creating backups** - One wrong edit loses all your config.
5. **Hardcoding fallback keys in code** - These override environment variables.

## Related Skills

- [stripe-payment-integration-complete](../integrations/stripe-payment-integration-complete.md)
- [react-production-deployment-desktop-guide](./react-production-deployment-desktop-guide.md)

## References

- Vite Environment Variables: https://vitejs.dev/guide/env-and-mode
- dotenv Best Practices: https://www.npmjs.com/package/dotenv
- OWASP Secrets Management: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
