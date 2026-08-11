---
name: BACKWARD_PLANNING_INTERVIEW
category: methodology
description: Structured questioning protocol for extracting project end-state from beginners who don't know technical terminology
version: 1.0.0
tags: [backward-planning, interview, vision, beginners, vibe-coder]
---

# Backward Planning Interview Protocol

Reference skill for `fire-vision-architect` (backward mode) and `fire-1-new` (adaptive questioning). Provides structured question sequences that extract the mission objective from users who don't know what questions to ask.

> **Origin:** Military backward planning doctrine — fix the end-state first, then derive every checkpoint from it. Adapted for software project initialization.

---

## Mode Gate

This interview activates when the user answers the mode gate question:

> **"Have you already started building this, or are we starting from scratch?"**

If they say "from scratch," "just an idea," or anything that reveals no existing tech context — this protocol runs. Never ask "What tech stack are you using?" — it forces beginners to bluff or freeze.

---

## Core Principle

Beginners describe products in terms of **what they can see and do**, not in technical terms. Every question below is designed to extract a hidden technical requirement from a plain-language answer.

**Never ask:** "Do you need WebSockets?" (they don't know what that is)
**Always ask:** "Should users see changes from other people instantly, like Google Docs?" (they know exactly what that means)

---

## Phase 0: Visual Input (Show, Don't Tell)

*Goal: Let users show what they're building instead of describing it. A picture extracts more requirements in 5 seconds than 10 minutes of questions.*

### Question 0: The Visual
> **"Do you have anything visual — a screenshot, a wireframe, a Figma link, a hand-drawn sketch, or even a photo of a napkin drawing? Drop it here and I'll extract the technical requirements from it."**

*What this reveals:* UI complexity, navigation patterns, data models, feature scope — all at once.

**Accepted formats:**
| Input Type | How to Share | What Claude Extracts |
|-----------|-------------|---------------------|
| Screenshot of similar app | Paste image or file path | UI patterns, features to clone, complexity level |
| Figma/design tool export | Export as PNG and share | Component hierarchy, page count, navigation flow |
| Hand-drawn wireframe | Photo of paper sketch | Screen count, data relationships, user flow |
| Napkin drawing | Phone photo | Core screens, rough feature scope |
| Figma link | Share the URL (needs MCP) | Full design system, components, variants |
| Excalidraw export | Share PNG or `.excalidraw` file | Architecture diagrams, flow charts, wireframes |

**Visual Extraction Protocol:**

When the user provides a visual, Claude reads the image and extracts:

```markdown
## Visual Analysis

**Screens identified:** {count}
**Screen list:**
1. {screen name} — {what it shows}
2. {screen name} — {what it shows}

**UI Elements detected:**
- Navigation: {sidebar / topbar / tabs / hamburger}
- Forms: {login / signup / settings / data entry}
- Data displays: {tables / cards / lists / charts / maps}
- Interactive: {drag-drop / editor / canvas / video player}
- Social: {comments / chat / feed / profiles}

**Derived capabilities from visual:**
| Visual Element | → Technical Requirement |
|---------------|----------------------|
| Login screen | Auth system |
| Dashboard with charts | Data aggregation + visualization library |
| User avatar / profile | Image upload + user profiles |
| Chat sidebar | Real-time messaging (WebSockets) |
| Payment/pricing page | Stripe integration |
| Admin panel | Role-based access control |
| Search bar | Search index (full-text or Algolia) |
| Map view | Geolocation API + maps SDK |
| Video player | Video hosting / streaming |
| File list / upload area | Object storage (S3/R2/Supabase) |
| Mobile layout visible | Responsive design required |
```

**After visual extraction:**
- Skip any interview questions already answered by the visual
- Use remaining questions to fill gaps the visual didn't reveal
- Reference the visual analysis in the Capability Summary output

> **Pro tip:** Even a rough sketch reveals navigation structure, screen count, and data relationships that take 5+ questions to extract verbally. Always ask for visuals first.

---

## Phase 1: The Walkthrough (Mission Objective)

*Goal: Get the user to narrate what their finished product looks like in use.*

### Question 1: The Elevator Pitch
> **"In one sentence, what does your app do for the person using it?"**

*What this reveals:* Core value proposition, primary user type, product category.

| Answer Pattern | Hidden Requirement |
|---------------|-------------------|
| "Helps teachers manage courses" | LMS, role-based auth (teacher/student), content management |
| "Lets people sell handmade goods" | E-commerce, payments, seller/buyer roles, product catalog |
| "Tracks my workouts" | Personal data, mobile-friendly, charts/visualization |
| "Connects freelancers with clients" | Marketplace, messaging, payments, reviews |

### Question 2: The First 60 Seconds
> **"A new user just signed up. Walk me through their first 60 seconds — what do they see, what do they click?"**

*What this reveals:* Onboarding flow, auth requirements, initial data structure, primary navigation.

| Answer Pattern | Hidden Requirement |
|---------------|-------------------|
| "They fill out a profile with their photo" | User profiles, image upload, storage |
| "They see a feed of posts from people they follow" | Social graph, feed algorithm, follow system |
| "They get a dashboard showing their stats" | Data aggregation, charts, dashboard UI |
| "They pick a plan and enter payment" | Subscription billing, payment gateway, plan tiers |

### Question 3: The Money Screen
> **"What's the ONE screen where your app delivers the most value? Describe it like you're showing it to a friend."**

*What this reveals:* Core feature complexity, data relationships, UI sophistication needed.

| Answer Pattern | Hidden Requirement |
|---------------|-------------------|
| "A drag-and-drop board like Trello" | Complex UI interactions, state management, real-time sync |
| "A clean editor where you write and format text" | Rich text editor (Tiptap/ProseMirror), content blocks |
| "A map showing nearby services" | Geolocation, maps API, location-based queries |
| "A video player with comments on the side" | Video hosting/streaming, threaded comments, timestamps |

---

## Phase 2: The Users (Personnel & Roles)

*Goal: Discover user roles, permissions, and access patterns.*

### Question 4: Who's Involved?
> **"Besides the main user, who else uses this? Does anyone have special powers — like an admin, a manager, a teacher?"**

*What this reveals:* Role-based access control (RBAC), permission tiers, multi-tenant needs.

| Answer Pattern | Hidden Requirement |
|---------------|-------------------|
| "Just me" | Single user, no auth needed or simple auth |
| "Users and admins" | 2-role RBAC, admin dashboard |
| "Teachers, students, and school admins" | 3+ role RBAC, organization/tenant model |
| "Anyone can view, only members can post" | Public/private content, auth-gated actions |

### Question 5: Solo or Social?
> **"Do users interact with each other, or is it a solo experience? Can they see each other's stuff?"**

*What this reveals:* Social features, real-time needs, content visibility model.

| Answer Pattern | Hidden Requirement |
|---------------|-------------------|
| "Totally solo, it's a personal tool" | Simple data model, no sharing infrastructure |
| "They can share links to their work" | Public URLs, sharing permissions |
| "They message each other" | Messaging system, notifications, possibly real-time |
| "They collaborate on the same document" | Real-time collaboration (WebSockets/CRDT), conflict resolution |

---

## Phase 3: The Capabilities (Equipment & Logistics)

*Goal: Discover technical requirements the user doesn't know they have.*

### Question 6: The Similar App
> **"Name 1-2 apps that feel closest to what you're building. What do you like about them? What would you change?"**

*What this reveals:* Feature benchmark, UI expectations, implicit technical requirements.

| Reference App | Implied Stack Needs |
|--------------|-------------------|
| "Like Notion" | Rich text, content blocks, flexible schema, collaborative editing |
| "Like Shopify" | E-commerce engine, payments, inventory, multi-vendor possible |
| "Like Duolingo" | Gamification, progress tracking, spaced repetition, mobile-first |
| "Like Airbnb" | Marketplace, search/filter, maps, booking/calendar, reviews |
| "Like Slack" | Real-time messaging, channels, file sharing, notifications |
| "Like Canva" | Canvas editor, templates, asset library, export pipeline |

### Question 7: The Deal-Breakers
> **"Which of these does your app NEED to do? (Just say yes or no to each)"**
>
> - Users log in with email/password or Google?
> - Accept payments or subscriptions?
> - Users upload files (images, videos, documents)?
> - Send emails or notifications?
> - Work well on phones (not just desktop)?
> - Show real-time updates (like a live chat or live dashboard)?

*What this reveals:* Direct capability mapping. Each "yes" locks in a technical requirement.

| "Yes" Answer | Technical Requirement |
|-------------|---------------------|
| Login | Auth system (Supabase Auth, NextAuth, better-auth, Passport) |
| Payments | Stripe integration, webhook handling, subscription model |
| File uploads | Object storage (S3, Supabase Storage, Cloudflare R2) |
| Emails | Email service (Resend, SendGrid, AWS SES) |
| Mobile | Responsive design (Tailwind) or React Native |
| Real-time | WebSockets (Socket.io, Supabase Realtime) or SSE |

### Question 8: The Scale Question
> **"In your dream scenario, how many people are using this? Just you? Hundreds? Thousands? Millions?"**

*What this reveals:* Infrastructure scaling needs, database choice implications, hosting tier.

| Answer | Infrastructure Implication |
|--------|--------------------------|
| "Just me / a few people" | SQLite or free-tier Supabase, simple hosting |
| "Hundreds" | Standard PostgreSQL, single-server hosting |
| "Thousands" | PostgreSQL + connection pooling, CDN, caching layer |
| "Millions" | Horizontal scaling, Redis, CDN, queue system, microservices |

---

## Phase 4: The Timeline (Mission Calendar)

*Goal: Understand urgency and what "done" means to them.*

### Question 9: The Deadline
> **"When do you need this working? Is there a hard deadline (like a launch event) or is it flexible?"**

*What this reveals:* Scope constraints, MVP vs full-build, phase prioritization.

### Question 10: The MVP Gate
> **"If you could only ship THREE features and nothing else, which three?"**

*What this reveals:* True priorities stripped of nice-to-haves. This becomes Phase 1.

---

## Capability-to-Stack Derivation Table

After the interview, map collected capabilities to stack constraints:

| Collected Capabilities | Rules Out | Points Toward |
|-----------------------|-----------|---------------|
| Rich text editor + collaboration | Static sites, simple CRUD | Next.js + Supabase Realtime, or MERN + Socket.io |
| Payments + subscriptions | Frontend-only, static | Full-stack with Stripe SDK (Next.js, Express, Rails) |
| File uploads (images only) | Nothing major | Supabase Storage, S3, Cloudflare R2 |
| File uploads (video) | Serverless-only (size limits) | Dedicated upload service, container hosting |
| Real-time (chat/collab) | Pure REST APIs | WebSocket-capable stack (Supabase, Socket.io, Ably) |
| Mobile-first | Desktop-heavy frameworks | React Native, or responsive Next.js/Remix |
| 3+ user roles | Simple auth | RBAC system, role middleware, admin dashboard |
| Multi-tenant (orgs) | Simple data model | PostgreSQL RLS, tenant isolation, org-scoped queries |
| ML/AI features | Frontend-only | Python backend or API calls to Claude/Gemini |
| Offline support | Server-dependent stacks | PWA, local-first (SQLite + sync), service workers |

---

## Interview Anti-Patterns

**Don't do these:**

| Anti-Pattern | Why It Fails | Do Instead |
|-------------|-------------|------------|
| "What's your tech stack?" | Beginners freeze or guess wrong | Ask about the product, derive the stack |
| "Do you need a relational database?" | Jargon — they don't know | "Does your data have relationships? Like courses have lessons, lessons have students?" |
| "SSR or CSR?" | Meaningless to beginners | "Should Google be able to find your pages? Like a blog?" (→ SSR) |
| "REST or GraphQL?" | Implementation detail | Never ask. Derive from data complexity |
| "Monolith or microservices?" | Architecture astronautics | Never ask. Default monolith, split later if needed |
| Asking all 10 questions mechanically | Feels like an interrogation | Adapt — skip questions already answered in earlier responses |

---

## Output: Capability Summary

After the interview, produce a structured summary that feeds into branch generation:

```markdown
## Capability Summary (from Backward Planning Interview)

**Product:** {elevator pitch}
**Similar to:** {reference apps}
**Primary user:** {who}
**User roles:** {list}
**Visual provided:** {yes/no — if yes, include extracted screen count and key findings}

### Required Capabilities
- [ ] Auth: {type}
- [ ] Payments: {yes/no, type}
- [ ] File uploads: {type, size}
- [ ] Real-time: {yes/no, what kind}
- [ ] Email/notifications: {yes/no}
- [ ] Mobile: {responsive or native}
- [ ] Scale target: {users}

### Derived Constraints
| Capability | Constraint | Eliminates |
|-----------|-----------|------------|
| {cap} | {what this means technically} | {stacks ruled out} |

### MVP Features (Phase 1)
1. {feature}
2. {feature}
3. {feature}

→ Feed this into fire-vision-architect Step B2 (Backward Mode)
```
