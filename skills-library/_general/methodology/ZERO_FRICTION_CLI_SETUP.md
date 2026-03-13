---
name: ZERO_FRICTION_CLI_SETUP
category: methodology
description: Auto-install all CLI tools a project needs based on locked VISION.md — vibe coders provide ideas, Claude handles tooling
version: 1.0.0
tags: [cli, tooling, setup, vibe-coder, zero-friction, npx, automation]
---

# Zero-Friction CLI Setup

Reference skill for `/fire-1a-new` Step 4b. After VISION.md is locked, Claude reads the technology stack table and auto-installs every CLI tool, SDK, and service the project needs. The vibe coder should never manually install anything.

> **Philosophy:** Ideas in → working tools out. If a beginner has to Google "how to install Supabase," the flow failed.

---

## Process

1. Read locked `.planning/VISION.md` Technology Stack table
2. Match each technology to its CLI setup commands (see matrix below)
3. Run installations in dependency order (framework → database → services → tooling)
4. Verify each install succeeded (version check or health check)
5. Log results to `.planning/TOOLING-LOG.md`
6. If any install fails, log the failure and suggest alternative

---

## Master CLI Tool Matrix

### Deployment & Hosting

| Tool | Install Command | What It Does | Free Tier | Status |
|------|----------------|-------------|-----------|--------|
| **Vercel** | `npm i -g vercel` then `vercel` | Deploy frontend + serverless, preview URLs per PR | Yes (hobby) | Rising — best DX for Next.js |
| **Netlify** | `npm i -g netlify-cli` then `netlify init` | Deploy static/Jamstack, serverless functions | Yes | Stable |
| **Cloudflare Pages** | `npm i -g wrangler` then `wrangler pages` | Edge deployment, Workers, R2 storage | Yes (generous) | Rising — fastest edge network |
| **Railway** | `npm i -g @railway/cli` then `railway init` | Deploy anything (Node, Python, Docker), managed Postgres | Yes ($5 credit) | Rising — simplest full-stack deploy |
| **Fly.io** | `curl -L https://fly.io/install.sh \| sh` | Deploy Docker containers globally, edge compute | Yes (3 shared VMs) | Stable |
| **Render** | No CLI — Git push deploy | Auto-deploy from GitHub, managed services | Yes | Stable |

### Databases & Backend-as-a-Service

| Tool | Install Command | What It Does | Free Tier | Status |
|------|----------------|-------------|-----------|--------|
| **Supabase** | Windows: `scoop install supabase` / Mac: `brew install supabase/tap/supabase` then `supabase init && supabase start` | Local Postgres + Auth + Storage + Realtime + Edge Functions | Yes (2 projects) | Dominant — best open-source BaaS |
| **Firebase** | `npm i -g firebase-tools` then `firebase init` | Firestore, Auth, Hosting, Cloud Functions | Yes (Spark plan) | Stable — Google ecosystem |
| **Neon** | `npm i -g neonctl` then `neonctl connect` | Serverless Postgres with branching | Yes (generous) | Rising fast — best serverless Postgres for Vercel |
| **Turso** | Binary: `curl -sSfL https://get.tur.so/install.sh \| bash` (not npm) | Embedded SQLite at the edge (libSQL) | Yes (500 DBs, 9GB) | Rising — edge-first |
| **PlanetScale** | Binary from planetscale.com (no free tier) | Serverless MySQL with branching | No | Declining — avoid for new projects |
| **MongoDB Atlas** | `npm i -g mongosh` | MongoDB cloud, document database | Yes (512MB) | Stable — MERN stack standard |
| **Redis/Upstash** | `npm install @upstash/redis` | Serverless Redis for caching, rate limiting, queues | Yes (10K/day) | Rising — serverless Redis leader |

### Payments & Commerce

| Tool | Install Command | What It Does | Free Tier | Status |
|------|----------------|-------------|-----------|--------|
| **Stripe** | SDK: `npm install stripe @stripe/stripe-js` / CLI: Go binary from stripe.com/docs/stripe-cli (not npm) | Payments, subscriptions, invoicing, webhook testing | Pay-per-use | Standard — #1 payment processor |
| **PayPal** | `npm install @paypal/checkout-server-sdk @paypal/react-paypal-js` | PayPal payments, checkout buttons | Pay-per-use | Stable — highest consumer trust |
| **Lemon Squeezy** | `npm install @lemonsqueezy/lemonsqueezy.js` | Merchant of record — handles tax, billing, compliance | Pay-per-use | Rising — Stripe alternative for SaaS |
| **Polar** | `npm install @polar-sh/sdk` | Open-source friendly payments, sponsorships | Pay-per-use | Rising — dev-focused |

> **Stripe CLI** is essential for local webhook testing: `stripe listen --forward-to localhost:3000/api/webhooks/stripe` (install the Go binary from stripe.com/docs/stripe-cli — on Windows: `scoop install stripe`, Mac: `brew install stripe/stripe-cli/stripe`)

### Authentication

| Tool | Install Command | What It Does | Free Tier | Status |
|------|----------------|-------------|-----------|--------|
| **better-auth** | `npm install better-auth` then `npx @better-auth/cli generate` | Framework-agnostic auth, social login, 2FA, org support | Free (OSS) | Rising — best DX 2025-2026 |
| **NextAuth/Auth.js** | `npm install next-auth` | Auth for Next.js, multiple providers | Free (OSS) | Stable — Next.js ecosystem standard |
| **Clerk** | `npm install @clerk/nextjs` | Drop-in auth UI components, user management | Yes (10K MAU) | Rising — fastest to implement |
| **Supabase Auth** | Included with `npx supabase init` | Auth bundled with Supabase, RLS integration | Yes | Rising — bundled with Supabase |
| **Passport.js** | `npm install passport passport-local passport-google-oauth20` | Express middleware auth, 500+ strategies | Free (OSS) | Stable — Express/MERN standard |

### ORM & Database Tools

| Tool | Install Command | What It Does | Free Tier | Status |
|------|----------------|-------------|-----------|--------|
| **Prisma** | `npm install prisma @prisma/client` then `npx prisma init` | Type-safe ORM, migrations, studio GUI | Free (OSS) | Stable — most popular Node ORM |
| **Drizzle** | `npm install drizzle-orm` + `npm install -D drizzle-kit` | Lightweight TypeScript ORM, SQL-like syntax | Free (OSS) | Rising — Prisma alternative |
| **Mongoose** | `npm install mongoose` | MongoDB ODM, schemas, validation | Free (OSS) | Stable — MERN standard |

### UI & Components

| Tool | Install Command | What It Does | Free Tier | Status |
|------|----------------|-------------|-----------|--------|
| **shadcn/ui** | `npx shadcn@latest init` then `npx shadcn@latest add button card ...` | Copy-paste component library (Radix + Tailwind) | Free (OSS) | Rising — #1 React component system |
| **Tailwind CSS** | `npm install -D tailwindcss @tailwindcss/vite` | Utility-first CSS framework | Free (OSS) | Standard — dominant CSS framework |
| **Radix UI** | `npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu` | Accessible headless UI primitives | Free (OSS) | Stable — shadcn foundation |
| **Framer Motion** | `npm install framer-motion` | Animation library for React | Free (OSS) | Stable |
| **Lucide Icons** | `npm install lucide-react` | Beautiful open-source icon set | Free (OSS) | Rising — replacing Heroicons |

### Testing

| Tool | Install Command | What It Does | Free Tier | Status |
|------|----------------|-------------|-----------|--------|
| **Playwright** | `npm install -D @playwright/test` then `npx playwright install chromium firefox` | E2E testing + MCP visual verification (THE BEST) | Free (OSS) | Rising — #1 E2E framework |
| **Vitest** | `npm install -D vitest` | Unit/integration testing, Vite-native | Free (OSS) | Rising — replacing Jest |
| **Testing Library** | `npm install -D @testing-library/react @testing-library/jest-dom` | Component testing utilities | Free (OSS) | Stable |

### Email & Notifications

| Tool | Install Command | What It Does | Free Tier | Status |
|------|----------------|-------------|-----------|--------|
| **Resend** | `npm install resend` | Modern email API, React Email templates | Yes (100/day) | Rising — best email DX |
| **React Email** | `npx create-email@latest` | Build emails with React components | Free (OSS) | Rising — pairs with Resend |
| **Nodemailer** | `npm install nodemailer` | Send email from Node.js (any SMTP) | Free (OSS) | Stable — battle-tested |
| **SendGrid** | `npm install @sendgrid/mail` | Email API, templates, analytics | Yes (100/day) | Stable |

### File Storage & Media

| Tool | Install Command | What It Does | Free Tier | Status |
|------|----------------|-------------|-----------|--------|
| **Uploadthing** | `npm install uploadthing @uploadthing/react` | File uploads for Next.js/React, S3-backed | Yes (2GB) | Rising — simplest file uploads |
| **Supabase Storage** | Included with `npx supabase init` | S3-compatible object storage | Yes (1GB) | Rising — bundled |
| **Cloudflare R2** | Via `wrangler` CLI | S3-compatible, zero egress fees | Yes (10GB) | Rising — cheapest storage |
| **AWS S3** | `npm install @aws-sdk/client-s3` | Industry-standard object storage | Yes (5GB, 12 months) | Standard |

### Video & Media APIs

| Tool | Install Command | What It Does | Free Tier | Status |
|------|----------------|-------------|-----------|--------|
| **YouTube Data API** | `npm install googleapis` then use `google.youtube('v3')` | Search, playlists, video metadata, channel info | Yes (10K units/day) | Standard — essential for content apps |
| **Mux** | `npm install @mux/mux-node @mux/mux-player-react` | Video hosting, streaming, HLS, analytics | Pay-per-use | Rising — best video API |
| **Cloudflare Stream** | Via `wrangler` | Video streaming at the edge | Pay-per-use | Rising |

### AI & LLM Integration

| Tool | Install Command | What It Does | Free Tier | Status |
|------|----------------|-------------|-----------|--------|
| **Anthropic SDK** | `npm install @anthropic-ai/sdk` | Claude API — chat, vision, tool use | Pay-per-use | Rising — best reasoning |
| **Google AI SDK** | `npm install @google/generative-ai` | Gemini API — chat, vision, code | Pay-per-use | Rising — best multimodal |
| **Vercel AI SDK** | `npm install ai @ai-sdk/anthropic @ai-sdk/google` | Unified streaming AI interface, works with Claude + Gemini | Free (OSS) | Rising — best AI DX |

> **Never use OpenAI** — per project rules, always use Claude (Anthropic) or Gemini (Google).

### Monitoring & Analytics

| Tool | Install Command | What It Does | Free Tier | Status |
|------|----------------|-------------|-----------|--------|
| **Sentry** | `npx @sentry/wizard@latest -i nextjs` | Error tracking, performance monitoring | Yes (5K errors/mo) | Standard — #1 error tracking |
| **PostHog** | `npm install posthog-js posthog-node` | Product analytics, feature flags, session replay | Yes (1M events/mo) | Rising — open-source analytics |
| **Vercel Analytics** | `npm install @vercel/analytics` | Web vitals, page views (Vercel-hosted) | Yes (basic) | Rising — zero-config |

### Code Quality

| Tool | Install Command | What It Does | Free Tier | Status |
|------|----------------|-------------|-----------|--------|
| **Biome** | `npm install -D @biomejs/biome` then `npx @biomejs/biome init` | Linter + formatter in ONE Rust binary (replaces ESLint + Prettier) | Free (OSS) | Rising fast — 20x faster, single config |
| **oxlint** | `npm install -D oxlint` | Ultra-fast linter (50-100x faster than ESLint, lint-only) | Free (OSS) | Rising |
| **ESLint** | `npm install -D eslint @eslint/js` | JavaScript/TypeScript linting | Free (OSS) | Stable — declining vs Biome |
| **Prettier** | `npm install -D prettier eslint-config-prettier` | Code formatting | Free (OSS) | Stable — declining vs Biome |
| **Husky** | `npx husky init` | Git hooks (pre-commit, pre-push) | Free (OSS) | Stable |

> **2026 recommendation:** Use **Biome** for new projects (replaces both ESLint and Prettier). Use ESLint+Prettier only for existing codebases that already have them configured.

---

## Stack-to-CLI Mapping (Common Combos)

When VISION.md contains these stacks, install these tool sets:

### MERN Stack (MongoDB + Express + React + Node)
```bash
npm install express mongoose cors dotenv
npm install -D nodemon vitest
npx create-vite@latest client --template react
cd client && npm install axios react-router-dom
npm install passport passport-local
npm install -D @playwright/test && npx playwright install chromium firefox
```

### Next.js + Supabase (Modern Full-Stack)
```bash
npx create-next-app@latest --typescript --tailwind --app
npx supabase init && npx supabase start
npx shadcn@latest init
npm install @supabase/supabase-js @supabase/ssr
npm install -D @playwright/test && npx playwright install chromium
npm i -g vercel
```

### Next.js + PostgreSQL + Prisma
```bash
npx create-next-app@latest --typescript --tailwind --app
npm install prisma @prisma/client && npx prisma init
npx shadcn@latest init
npm install better-auth
npm install -D @playwright/test && npx playwright install chromium
npm i -g vercel
```

### Express + PostgreSQL + React (PERN)
```bash
npm install express pg cors dotenv
npm install -D nodemon prisma && npx prisma init
npx create-vite@latest client --template react-ts
cd client && npm install -D tailwindcss @tailwindcss/vite
npm install -D vitest @playwright/test && npx playwright install chromium firefox
```

---

## Installation Order

Always install in this sequence to avoid dependency conflicts:

```
1. Framework scaffold    (create-next-app, create-vite, express init)
2. Database / BaaS       (supabase init, prisma init, mongoose)
3. Auth                  (better-auth, next-auth, passport)
4. UI components         (tailwind, shadcn, radix)
5. Service integrations  (stripe, resend, uploadthing, youtube API)
6. Testing               (playwright, vitest)
7. Code quality          (eslint, prettier, husky)
8. Deployment            (vercel, wrangler)
9. Monitoring            (sentry, posthog)
```

---

## DevTools Quick Reference (for beginners)

Save to `.planning/DEVTOOLS-GUIDE.md` during backward mode init:

```
F12 / Ctrl+Shift+I — Open DevTools

Console tab   → Errors (red) and warnings (yellow) appear here
                Copy red errors → paste to Claude for instant diagnosis

Network tab   → API calls show here, filter by "Fetch/XHR"
                Red = failed request, click to see response body

Elements tab  → Inspect any element's HTML/CSS
                Click 🔍 → click element → see/edit styles live

Application tab → Check cookies, localStorage, session tokens
                  Useful for debugging auth issues

Pro tip: Screenshot the Console tab when something breaks.
         This is 10x faster than describing the error in words.
```

---

## Failure Handling

If a CLI install fails:

1. Check if it's a network issue (retry once)
2. Check if it's a version conflict (try `--legacy-peer-deps`)
3. Log the failure to `.planning/TOOLING-LOG.md`
4. Suggest manual install command to the user
5. Continue with remaining installations (don't block on one failure)

---

## Verification Checklist

After all installations, verify:

```bash
# Framework running
npm run dev  # Should start without errors

# Database connected
npx prisma db push  # OR npx supabase status

# Auth working
# Check /api/auth or auth callback URL responds

# Playwright ready
npx playwright test --list  # Should list test files

# Deployment CLI authenticated
vercel whoami  # OR wrangler whoami
```

---

## 2026 Category Winners (Quick Reference)

| Category | Winner | Avoid |
|----------|--------|-------|
| Hosting | **Vercel** (Next.js) + **Railway** (full-stack) | Heroku |
| Database | **Supabase** / **Neon** | PlanetScale (no free tier) |
| ORM | **Drizzle** (edge) / **Prisma** (teams) | Sequelize, TypeORM |
| Auth | **Clerk** (fastest) / **better-auth** (most control) | Passport.js for new projects |
| UI | **shadcn/ui** + **Tailwind v4** | Chakra UI, Material UI |
| Linting | **Biome** (single binary) | ESLint + Prettier combo |
| E2E Testing | **Playwright** + MCP | Selenium, Cypress |
| Unit Testing | **Vitest** | Jest (legacy) |
| Email | **Resend** + **React Email** | SendGrid |
| AI SDK | **Vercel AI SDK** + Anthropic/Google providers | OpenAI (never use) |
| Payments | **Stripe** (standard) / **Lemon Squeezy** (MoR) | — |
| Video | **YouTube API** (content) / **Mux** (hosting) | — |

---

Log all results to `.planning/TOOLING-LOG.md`:

```markdown
# Tooling Installation Log

| Tool | Version | Status | Notes |
|------|---------|--------|-------|
| Next.js | 15.x | ✅ Installed | — |
| Supabase CLI | 1.x | ✅ Installed | Local instance running |
| Stripe | 15.x | ✅ Installed | Webhook forwarding ready |
| Playwright | 1.x | ✅ Installed | Chromium + Firefox |
| Vercel CLI | 37.x | ✅ Installed | Authenticated |
```
