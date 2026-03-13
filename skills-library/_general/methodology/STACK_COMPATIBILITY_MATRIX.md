---
name: STACK_COMPATIBILITY_MATRIX
category: methodology
description: Reference data for proven stack combinations, known incompatibilities, and project-type mapping
version: 1.0.0
tags: [architecture, stack, compatibility, vision]
---

# Stack Compatibility Matrix

Reference data for the `fire-vision-architect` agent. Contains proven combinations, known conflicts, and project-type recommendations.

---

## Proven Stack Combinations

### MERN (MongoDB + Express + React + Node.js)
- **Best for:** Rapid prototyping, real-time apps, flexible-schema projects
- **Industry:** Netflix, Uber (parts), Instagram (early)
- **Auth pairing:** Passport.js, JWT custom, Auth0
- **Hosting:** Heroku, Railway, DigitalOcean, AWS EC2
- **DB extensions:** Redis (caching), Mongoose ODM
- **Strengths:** Single language (JS) everywhere, huge npm ecosystem, fast iteration
- **Weaknesses:** No ACID by default, schema discipline required, callback complexity

### PERN (PostgreSQL + Express + React + Node.js)
- **Best for:** Data-integrity-critical apps, financial, CRM, LMS
- **Industry:** Many YC startups, internal tools
- **Auth pairing:** Passport.js, JWT custom, better-auth
- **Hosting:** Heroku, Railway, Render, AWS RDS + EC2
- **DB extensions:** Prisma ORM, Drizzle ORM, pg-promise
- **Strengths:** ACID compliance, complex queries, relational integrity, mature tooling
- **Weaknesses:** Schema migrations needed, slightly slower prototyping than MongoDB

### Next.js + Supabase
- **Best for:** Solo devs, MVPs, startups wanting speed-to-market
- **Industry:** cal.com, Resend, many indie SaaS
- **Auth pairing:** Supabase Auth (built-in), NextAuth
- **Hosting:** Vercel (native), Netlify, Cloudflare Pages
- **DB extensions:** Supabase Realtime, Edge Functions, Row Level Security
- **Strengths:** Fastest time-to-market, built-in auth/storage/realtime, generous free tier
- **Weaknesses:** Vendor lock-in risk, limited custom backend logic, Supabase scaling costs

### Next.js + PostgreSQL + Prisma
- **Best for:** Full-stack teams wanting type safety and control
- **Industry:** Vercel apps, many B2B SaaS
- **Auth pairing:** NextAuth/Auth.js, better-auth, Clerk
- **Hosting:** Vercel + Neon/Supabase DB, Railway
- **DB extensions:** Prisma Studio, connection pooling (PgBouncer)
- **Strengths:** Type-safe DB access, excellent DX, SSR/SSG flexibility, full control
- **Weaknesses:** More setup than Supabase all-in-one, Prisma cold start in serverless

### NestJS + PostgreSQL + Redis
- **Best for:** Enterprise, microservices, teams > 5 developers
- **Industry:** Enterprise Node.js projects, fintech
- **Auth pairing:** Passport.js (NestJS module), custom JWT, Keycloak
- **Hosting:** AWS ECS/EKS, GCP Cloud Run, DigitalOcean Kubernetes
- **DB extensions:** TypeORM, MikroORM, Bull (job queues via Redis)
- **Strengths:** Angular-like structure, dependency injection, microservice-ready, testable
- **Weaknesses:** Steeper learning curve, more boilerplate, overkill for small projects

### Django + PostgreSQL + React/Vue
- **Best for:** Content-heavy apps, admin-intensive, rapid CRUD
- **Industry:** Instagram (early), Pinterest, Eventbrite
- **Auth pairing:** Django Auth (built-in), django-allauth
- **Hosting:** Heroku, Railway, AWS Elastic Beanstalk, DigitalOcean
- **DB extensions:** Django ORM, django-rest-framework, Celery (async tasks)
- **Strengths:** Batteries-included, admin panel free, excellent ORM, security defaults
- **Weaknesses:** Python + JS split, frontend integration friction, monolith tendency

### Rails + PostgreSQL + Hotwire/React
- **Best for:** Rapid development, startups, content platforms
- **Industry:** GitHub, Shopify, Basecamp, Airbnb (early)
- **Auth pairing:** Devise, OmniAuth
- **Hosting:** Heroku, Render, Fly.io, Hatchbox
- **DB extensions:** ActiveRecord, Sidekiq (background jobs), ActionCable (WebSockets)
- **Strengths:** Convention over configuration, fastest scaffolding, mature ecosystem
- **Weaknesses:** Ruby learning curve, performance ceiling, fewer JS devs know it

### Remix + PostgreSQL + Prisma
- **Best for:** Form-heavy apps, progressive enhancement, accessibility-first
- **Industry:** Shopify (Hydrogen), newer startups
- **Auth pairing:** Remix Auth, custom session-based
- **Hosting:** Fly.io, Vercel, Cloudflare Workers
- **Strengths:** Web standards first, nested routing, excellent forms, progressive enhancement
- **Weaknesses:** Smaller ecosystem than Next.js, fewer tutorials, less community support

### Astro + Headless CMS
- **Best for:** Content sites, blogs, documentation, marketing
- **Industry:** Content-focused startups, developer docs
- **Auth pairing:** Usually not needed; if needed, Auth.js
- **Hosting:** Vercel, Netlify, Cloudflare Pages
- **CMS options:** Sanity, Contentful, Strapi, WordPress headless
- **Strengths:** Zero JS by default, island architecture, fastest page loads
- **Weaknesses:** Not for app-like interactivity, limited client-side state

---

## Known Incompatibilities

### Database Conflicts
| Combination | Problem | Resolution |
|-------------|---------|------------|
| MongoDB + PostgreSQL (both as primary) | Redundant primary DBs, split data model, double migration burden | Pick one based on data shape: relational → PostgreSQL, flexible → MongoDB |
| Firebase Firestore + PostgreSQL | Two databases with different paradigms, sync nightmares | Use Firebase only for real-time features alongside PostgreSQL, or go all-in on one |
| SQLite + production multi-user | SQLite has write-locking, not suitable for concurrent production use | SQLite for dev/embedded only; PostgreSQL or MySQL for production |

### Frontend Conflicts
| Combination | Problem | Resolution |
|-------------|---------|------------|
| React + Vue (same project) | Two virtual DOMs, double bundle size, conflicting state management | Pick one. React has larger ecosystem; Vue has simpler API |
| React + jQuery | jQuery DOM manipulation conflicts with React's virtual DOM | Remove jQuery; use React refs for DOM access |
| Next.js + Create React App | CRA is client-only; Next.js handles routing and SSR differently | Use Next.js alone (it supersedes CRA) |

### Auth Conflicts
| Combination | Problem | Resolution |
|-------------|---------|------------|
| Firebase Auth + Auth0 + custom JWT | Three auth systems = three user tables, token confusion | Pick one: Firebase Auth (free tier), Auth0 (enterprise), or custom (full control) |
| Supabase Auth + NextAuth | Both manage sessions; double middleware, token conflicts | Use one: Supabase Auth if using Supabase DB, NextAuth if using custom DB |

### Hosting Conflicts
| Combination | Problem | Resolution |
|-------------|---------|------------|
| Serverless (Vercel/Netlify) + long-running processes | Serverless has execution time limits (10-60s), can't run background jobs | Use a separate worker service (Railway, Render background) or switch to container hosting |
| Static hosting + server-side rendering | Static hosts (GitHub Pages, S3) can't run SSR | Use Vercel/Netlify/Cloudflare which support both, or go pure static |

---

## Project-Type → Stack Mapping

### Simple Projects (≤3 features, 1 user role)
| Type | Recommended Stack | Why |
|------|------------------|-----|
| Portfolio/Landing | Astro + Tailwind + Vercel | Zero JS, fast loads, cheap hosting |
| Blog | Astro + Headless CMS + Vercel | Content-first, markdown support |
| Todo/Notes | Next.js + Supabase | Quick CRUD with auth, free tier |

### Standard Projects (4-10 features, multiple roles)
| Type | Recommended Stack | Why |
|------|------------------|-----|
| SaaS | Next.js + PostgreSQL + Prisma + Vercel | Type safety, SSR, scalable |
| E-commerce | Next.js + Supabase + Stripe | Built-in auth, real-time inventory |
| LMS | PERN or Next.js + PostgreSQL | Relational data (courses→lessons→users) |
| CRM | PERN + Redis | Complex queries, caching for dashboards |

### Enterprise/Complex (10+ features, compliance, scale)
| Type | Recommended Stack | Why |
|------|------------------|-----|
| Multi-tenant SaaS | NestJS + PostgreSQL + Redis + AWS | Row-level security, job queues, horizontal scale |
| Real-time Collab | Next.js + Supabase Realtime or Socket.io | Built-in WebSocket support |
| ML Pipeline | Django + PostgreSQL + Celery + Redis | Python ML ecosystem, async task processing |
| Marketplace | NestJS + PostgreSQL + Stripe Connect + S3 | Complex payment splits, file storage |

---

## 2026 Industry Trends

### Rising
- **Supabase** — Replacing Firebase for new projects (open source, PostgreSQL-based)
- **Drizzle ORM** — Lighter alternative to Prisma, better serverless performance
- **better-auth** — Rising auth library for Node.js (simpler than NextAuth)
- **Bun** — Faster Node.js alternative, gaining production adoption
- **Cloudflare Workers** — Edge-first deployment for global latency
- **Turso/LibSQL** — SQLite for production (embedded replicas, edge-ready)

### Stable
- **Next.js** — Dominant full-stack React framework
- **PostgreSQL** — Default database for new projects
- **Tailwind CSS** — Default styling approach
- **Vercel/Railway** — Default hosting for Node.js apps
- **Stripe** — Default payment processing

### Declining
- **Create React App** — Deprecated, replaced by Vite or Next.js
- **Firebase (for new projects)** — Supabase taking market share
- **Heroku (free tier)** — Gone; Railway/Render filling the gap
- **Webpack (manual config)** — Vite/Turbopack replacing
- **MongoDB (as default)** — PostgreSQL preferred unless schema flexibility is critical
