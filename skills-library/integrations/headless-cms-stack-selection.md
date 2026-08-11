# Headless CMS Stack Selection Guide

> Decision flowchart and comparison matrix for selecting the right headless CMS — Payload, Strapi, Directus, Sanity, Contentful, Ghost, and niche picks.

**When to use:** Starting a new content platform project and needing to choose a CMS, or evaluating a migration from one CMS to another.
**Stack:** Any — this is a technology selection guide, not stack-specific

---

## Decision Flowchart

```
START: What type of project is this?
│
├── "I'm building a Next.js / React app in TypeScript and want the CMS
│    embedded in my codebase — one deployment, one repo"
│   └── → PAYLOAD CMS ✓
│
├── "I need non-technical editors with a visual drag-drop interface
│    and block-based editing (no-code page builder style)"
│   ├── "Budget: $0-30/mo self-host is fine"
│   │   └── → STORYBLOK (free tier) or TINACMS (git-based)
│   └── "Budget: $50-200/mo SaaS is OK"
│       └── → STORYBLOK or BUILDER.IO
│
├── "I'm wrapping an existing database and don't want to recreate the schema"
│   └── → DIRECTUS ✓ (introspects your existing tables)
│
├── "I need a blog + newsletter + membership/paywall in one product"
│   └── → GHOST ✓ (see ghost-creator-monetization-pattern.md)
│
├── "My team needs Git-based content (Markdown files in repo, no DB)"
│   ├── Small team, Next.js
│   │   └── → KEYSTATIC or TINACMS
│   └── Any framework
│       └── → DECAP CMS (formerly Netlify CMS) or FRONT MATTER
│
├── "Enterprise: compliance, SSO, audit logs, SLA required"
│   └── → CONTENTSTACK or KONTENT.AI (Kentico)
│
├── "I want a mature ecosystem with plugins, and I'm comfortable with
│    JavaScript but not TypeScript-obsessed"
│   └── → STRAPI ✓
│
└── "I need a great content editing experience with real-time collaboration
│    and I'm OK paying $12-25/mo per user"
    └── → SANITY ✓
```

---

## Comparison Matrix

| | Payload | Strapi | Directus | Sanity | Contentful | Ghost |
|--|---------|--------|----------|--------|------------|-------|
| **Self-hosted** | Yes | Yes | Yes | Optional | No | Yes |
| **Free tier (self-host)** | Yes | Yes | Yes | Yes* | Limited | Yes |
| **TypeScript-first** | Full | Partial | No | Partial | No | No |
| **Embeds in Next.js** | Yes (v3) | No | No | No | No | No |
| **GraphQL built-in** | Yes (auto) | Yes (plugin) | Yes | Yes | Yes | No |
| **REST API** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Visual block editor** | Basic | Basic | Basic | Excellent | Good | Good |
| **Real-time collab** | No | No | No | Yes | No | No |
| **Git-based content** | No | No | No | No | No | No |
| **Newsletter built-in** | No | No | No | No | No | Yes |
| **Membership/paywall** | No | No | No | No | No | Yes |
| **Plugin ecosystem** | Growing | Large | Medium | Large | Large | Large |
| **GitHub stars (2025)** | ~28K | ~60K | ~27K | ~12K | N/A | ~46K |
| **Self-host complexity** | Medium | Medium | Low | N/A | N/A | Medium |
| **DB options** | PG/SQLite/Mongo | PG/MySQL/SQLite | Any | Sanity's cloud | Contentful cloud | MySQL/SQLite |

*Sanity has a generous free tier (3 users, 10GB bandwidth)

---

## Budget Tiers

### $0/month (Self-host on your existing infrastructure)
- **Payload** — unlimited, MIT license
- **Strapi** — Community edition, MIT license
- **Directus** — BSL license (free for non-competing products)
- **Ghost** — MIT license (self-host on a $5-10/mo VPS)
- **Keystatic** — free, git-based
- **TinaCMS** — free self-hosted

### $15-50/month
- **Ghost Pro Starter** — $15/mo, up to 500 members
- **Sanity Growth** — $15/mo + usage
- **Storyblok Starter** — $23/mo
- **Contentful Basic** — $300/mo (actually expensive at scale — start free, then steep)

### $100-400/month
- **Ghost Pro Creator** — $25/mo
- **Ghost Pro Team** — $50/mo
- **Sanity Team** — $15/user/mo
- **Storyblok Team** — $90/mo
- **Contentful** — $300+/mo for serious usage

### Enterprise ($500+/month)
- **Contentstack** — custom pricing
- **Kontent.ai** — custom pricing
- **Contentful** — custom pricing
- **Sanity Enterprise** — custom pricing

---

## Use Case Matching

| Use Case | Best Pick | Why |
|----------|-----------|-----|
| TypeScript Next.js product | Payload | Embedded, type-safe, Local API |
| Agency delivering to non-technical clients | Storyblok or Sanity | Best visual editing UX |
| Wrapping existing database | Directus | Introspects schema, no migration |
| Blog + newsletter + memberships | Ghost | Built-in, 0% platform fee |
| Enterprise compliance (SOC2, SSO, audit) | Contentstack or Kontent.ai | Enterprise-grade features |
| Git-based, no database | Keystatic or TinaCMS | Markdown in repo |
| Real-time collaborative editing | Sanity | Only major CMS with live collab |
| Plugin-heavy, large community | Strapi | 200+ plugins, 60K GitHub stars |
| Multi-language / i18n at scale | Contentful or Storyblok | Best i18n tooling |
| E-commerce content + commerce | Sanity | Excellent Shopify/commerce integrations |

---

## Red Flags: When NOT to Pick Each Platform

**Payload**
- You need to support non-developer content editors who will configure fields via GUI (Payload's admin is for content entry, not schema management — schema is code)
- You're not using TypeScript or Next.js
- You need a proven plugin ecosystem on day one

**Strapi**
- You need TypeScript throughout (types are partial, not generated)
- You want to embed the CMS in your Next.js app (separate deployment required)
- You need real-time collaboration

**Directus**
- You're starting from scratch (no existing DB to wrap)
- You need deep TypeScript integration
- Your content model will change frequently (GUI-based schema changes can drift from code)

**Sanity**
- Budget is tight (per-seat pricing adds up fast for teams)
- You need self-hosted data sovereignty
- You want everything in one deployment

**Contentful**
- Budget under $300/mo for any serious usage
- You want self-hosting or data control
- Your team is TypeScript-heavy (tooling is OK but not TypeScript-first)

**Ghost**
- You need custom content types beyond blog posts/pages (Ghost's data model is opinionated)
- You need complex user roles and permissions
- You want to build a general-purpose CMS (Ghost is publishing-specific)

---

## Migration Cost Matrix

Switching headless CMSes is painful. Here's a relative cost estimate:

| From | To | Cost |
|------|----|------|
| WordPress | Any headless | High — export content, reformat, rebuild frontend |
| Strapi | Payload | Medium — schema translation, hooks migration |
| Contentful | Sanity | Medium — export via API, remap schema |
| Contentful | Self-hosted | High — rebuild all integrations |
| Ghost (headless) | Payload | Low — Ghost Content API to Payload migration script exists |
| Directus | Any | Medium — DB is yours, but Directus-specific API calls need updating |
| Any | Ghost | High (if using memberships/newsletters) — member data migration is complex |

**Rule:** Budget 1-2 weeks of engineering time for any CMS migration. Test content rendering thoroughly before cutting over DNS.

---

## Quick Decision Rules

1. **Building a product (not an agency site), Next.js, TypeScript?** → Payload. Full stop.
2. **Client needs to manage content without touching code?** → Strapi or Directus. Both have excellent admin UIs that non-developers can operate.
3. **"I need this live in a weekend"** → Strapi (most generators/scaffolding) or Sanity (best DX for rapid setup).
4. **"I'm writing a newsletter and want to monetize subscribers"** → Ghost. Nothing else comes close to the subscription + newsletter + 0% fee combination.
5. **"We have an existing PostgreSQL database and just need a GUI + API on top"** → Directus. It introspects and works with what you have.
6. **"Our legal team requires data never leaves our servers"** → Self-host Payload, Strapi, or Directus. Disqualifies all SaaS options.
