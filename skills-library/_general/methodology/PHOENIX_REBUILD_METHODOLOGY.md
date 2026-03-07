---
name: PHOENIX_REBUILD_METHODOLOGY
category: methodology
version: 1.0.0
contributed: 2026-03-06
contributor: dominion-flow
last_updated: 2026-03-06
tags: [phoenix, rebuild, refactor, intent-extraction, vibe-code, technical-debt, reverse-engineering]
difficulty: hard
sources:
  - "Fred Brooks — No Silver Bullet (1986) — Essential vs Accidental Complexity"
  - "Martin Fowler — Refactoring: Improving the Design of Existing Code"
  - "Michael Feathers — Working Effectively with Legacy Code"
  - "Refactoring.Guru — Design Pattern Catalog"
---

# Phoenix Rebuild Methodology

> **Core insight:** Don't refactor the mess — reverse-engineer the INTENT, then build clean from scratch. A phoenix burns the old and rises new. The ashes carry the knowledge; the new form carries none of the accidental complexity.

---

## 1. How to Extract Intent from Messy Code

### Reading Order (Critical — Do NOT Read Code First)

```
1. README / docs          → What the developer SAID the app does
2. Route / endpoint files → The API surface reveals feature boundaries
3. Database schema/models → The data model reveals domain concepts
4. Tests (if any)         → Tests encode intended behavior
5. Git commit messages    → The narrative of how the code evolved
6. The code itself        → LAST — read implementation after you understand intent
```

**Why this order:** Reading code first biases toward "what it does" instead of "what it was meant to do." Surrounding artifacts reveal intent more clearly than tangled implementation.

### Intent Extraction Patterns

| Pattern | What to Look For | What It Reveals |
|---------|-----------------|-----------------|
| **Naming Intent** | Function/variable names vs their behavior | Gap between name and behavior = accidental complexity |
| **Comment Intent** | Comments saying "should", "TODO", "HACK", "FIXME" | Unfulfilled intent — developer knew what they wanted |
| **Test Intent** | What tests assert (if tests exist) | The behaviors the developer cared about verifying |
| **Error Handling Intent** | What errors are caught vs thrown | What the developer thought could go wrong |
| **Commit Message Intent** | "fix:", "feat:", "hack:" prefixes | The sequence of intentions over time |
| **Dead Code Intent** | Commented-out code, unreachable branches | Abandoned attempts — replaced or forgotten? |
| **Copy-Paste Intent** | Duplicated blocks with minor variations | "I needed this to work like THAT but slightly different" |
| **Magic Number Intent** | Hardcoded values with no explanation | A business rule or config never extracted |
| **Import Intent** | Imported but unused libraries | Features planned but never implemented |
| **Overengineering Intent** | Complex abstractions wrapping simple logic | Developer anticipated needs that never materialized |

### The "Squint Test"

For any module, ask: **"If I squint past the implementation mess, what is this module's job in ONE sentence?"**

If you cannot answer in one sentence, the module violates Single Responsibility and should be split during rebuild. The squint test produces the "intent statement" for each feature.

---

## 2. Accidental vs Essential Complexity (Fred Brooks)

### Essential Complexity — Keep and Rewrite Clean

Complexity inherent to the PROBLEM itself. Cannot be removed without changing what the application does.

**Examples:**
- Tax calculation rules (complex because taxes are complex)
- Multi-currency arithmetic (complex because currencies are complex)
- Role-based permissions with inheritance (complex because access control is nuanced)
- Content repurposing logic (complex because each platform has different format requirements)

**During rebuild:** Preserve ALL essential complexity. Rewrite it cleaner, add tests, add comments — but do NOT simplify away the business rules.

### Accidental Complexity — Remove Entirely

Complexity introduced by the IMPLEMENTATION, not the problem. CAN and SHOULD be eliminated.

**Detection heuristics:**
```
IF removing the pattern changes WHAT the app does    → ESSENTIAL (keep)
IF removing the pattern only changes HOW it does it  → ACCIDENTAL (remove)
IF the pattern exists because "that's how the tutorial did it" → ACCIDENTAL
IF the pattern exists because "the business rule requires it" → ESSENTIAL
IF the pattern appears in "common anti-patterns" lists → likely ACCIDENTAL
```

**Common accidental complexity indicators:**
- Global state mutations instead of state management
- Callback nesting instead of async/await
- Raw SQL strings instead of parameterized queries / ORM
- No separation between routes, business logic, and data access
- Duplicated code instead of shared functions
- Inconsistent error handling (some try/catch, some not)
- No type safety (everything is `any`)
- Hardcoded configuration values
- No environment separation (dev/staging/prod)

---

## 3. Edge Case Preservation Protocol

### The 5-Step Protocol

Every edge case in the original code must be:

```
1. IDENTIFIED  — Found in the code (conditional branches, special cases)
2. DOCUMENTED  — Recorded in INTENT.md with WHY it exists
3. CLASSIFIED  — Is this edge case still needed in the rebuild?
4. CARRIED     — If needed, it MUST appear in the rebuild BLUEPRINT
5. VERIFIED    — The rebuilt project must handle this edge case (test it)
```

### Where Edge Cases Hide (Top 10 Locations)

```
 1. if/else branches with non-obvious conditions
 2. try/catch blocks with specific error type handling
 3. Database query filters with multiple conditions
 4. Validation rules with specific ranges or patterns
 5. Timeout/retry logic
 6. Date/time/timezone handling
 7. Currency/precision arithmetic (rounding rules)
 8. Null/undefined guards (especially nested: user?.profile?.settings?.theme)
 9. Migration/compatibility code (backwards compat shims)
10. Feature flags / A/B test branches
```

### Kill or Keep Decision Framework

```
KEEP if:
  - It handles a real business scenario (even rare ones)
  - It prevents data corruption or data loss
  - It handles an external API quirk (rate limits, format variations)
  - It was added in response to a bug report (check git blame)
  - Removing it would change user-visible behavior

KILL if:
  - It handles a bug in code that is being rewritten anyway
  - It works around a library limitation that no longer exists
  - It exists because of poor architecture (which the rebuild fixes)
  - It is dead code (no execution path reaches it)
  - It was a temporary hack with a TODO to remove
```

---

## 4. Vibe-Coder Anti-Pattern Replacement Map

| Anti-Pattern | Detection Signal | Production Replacement |
|-------------|-----------------|----------------------|
| **God File** | Single file > 500 LOC with mixed concerns | Split by responsibility: routes, services, models, utils |
| **Copy-Paste Variation** | Near-identical blocks (>80% similar) | Extract shared function with parameters for variations |
| **Callback Hell** | Nested callbacks > 3 levels deep | async/await with proper error handling |
| **Global State Spaghetti** | `global`, `window.`, module-level mutation | State management (Redux, Zustand, Context) or DI |
| **No Error Handling** | No try/catch, uncaught promise rejections | Error middleware + typed error classes + logging |
| **Inline Everything** | SQL in route handlers, HTML in logic | Layered architecture: controller → service → repository |
| **Magic Strings/Numbers** | Hardcoded values throughout | Named constants, enums, config files |
| **No Types** | `any` everywhere, no interfaces | TypeScript strict mode with proper type definitions |
| **No Tests** | Zero test files | Test-first rebuild (write tests from INTENT.md before code) |
| **Security Ignorance** | Hardcoded secrets, no input validation, raw SQL | .env, validation schemas, parameterized queries, auth middleware |
| **No Config Separation** | URLs, ports, keys mixed in code | Environment-specific config with validation |
| **Monolith Route File** | All routes in one file | Route module per resource with controller pattern |

---

## 5. The Intent Graph

A three-column mapping that serves as the translation layer between messy source and clean target:

```
CODE (what exists)  →  INTENT (what was meant)  →  CLEAN (what to build)
```

### Why the Intent Graph Matters

It prevents two failure modes:

**Failure Mode 1: Literal Translation**
Rebuilding the mess exactly as it is, just with better formatting. The intent graph forces you to go THROUGH intent, not directly from code to code.

**Failure Mode 2: Intent Loss**
Rebuilding something clean but missing features because the developer's hidden knowledge was not extracted. The graph forces you to document every code pattern before discarding it.

### Building the Intent Graph

```
FOR each source code module:
  1. Read the code → document WHAT it does (observable behavior)
  2. Read surrounding context → document WHY (intent)
  3. Look up best practice → document HOW to do it right
  4. Record all three columns in INTENT-GRAPH.md
  5. Cross-check: does the "clean" column preserve all behaviors
     from the "code" column? If not, something was lost.
```

### Example Intent Graph Entries

| Source Code (Messy) | Developer Intent | Clean Implementation |
|---------------------|-----------------|---------------------|
| 200-line auth middleware with inline SQL | Role-based access control | passport.js + RBAC middleware + DB-backed roles |
| Global error handler that catches everything | Don't crash the app | Express error middleware + typed error classes + Sentry |
| 15 API routes in one file | CRUD for users + products + orders | Separate route modules + controller layer + service layer |
| Hardcoded `PORT=3000` in 5 files | Environment-specific config | dotenv + typed config loader + validation |
| Copy-pasted validation in every route | Input validation | Zod/Joi schema per endpoint, shared validation middleware |
| `setTimeout(fn, 5000)` retry loops | Handle transient API failures | Exponential backoff utility with configurable retries |
| `if (user.role === 'admin' \|\| user.id === 1)` | Admin access + superuser bypass | RBAC with permissions table + superuser flag in DB |

---

## 6. Rebuild Order Strategy

When rebuilding from INTENT.md, build in this order:

```
1. FOUNDATION     — Project scaffold, config, types, database schema
2. CORE           — Highest-uniqueness features (CRITICAL and HIGH)
3. SUPPORT        — Medium-uniqueness features
4. STANDARD       — Low-uniqueness and boilerplate (often auto-generated)
5. INTEGRATION    — Wire everything together, cross-module flows
6. HARDENING      — Error handling, logging, security, edge cases
7. TESTING        — Tests written from INTENT.md assertions
8. DOCUMENTATION  — README, API docs, deployment guide
```

**Rationale:** Build what is UNIQUE first. Boilerplate is easiest to add later and lowest risk. If context runs out, you want the unique business logic done, not the boilerplate. This is the opposite of how vibe coders build (scaffold first, unique logic last — which is why their unique logic is always the messiest part).

---

## 7. Feature Uniqueness Classification

| Score | Definition | Rebuild Strategy |
|-------|-----------|-----------------|
| **BOILERPLATE** | Standard framework code, no custom logic | Regenerate from best practices (don't even read the original) |
| **LOW** | Minor customization of standard patterns | Use standard pattern, apply customizations from INTENT.md |
| **MEDIUM** | Meaningful business logic using common patterns | Rewrite with proper architecture, preserve all business rules |
| **HIGH** | Custom algorithms, domain-specific rules | Carefully extract logic, rewrite with tests, preserve edge cases |
| **CRITICAL** | Core business differentiator, proprietary logic | Extract verbatim, wrap in clean architecture, comprehensive tests |

---

## When Agents Should Reference This Skill

- **fire-phoenix-analyst:** Primary reference — use reading order, intent extraction patterns, squint test, uniqueness classification
- **fire-phoenix (command):** Reference rebuild order strategy when creating phase breakdown from INTENT.md
- **fire-planner:** When planning rebuild phases, use uniqueness scores to prioritize task order
- **fire-executor:** When rebuilding modules, check anti-pattern map to avoid reintroducing accidental complexity
- **fire-verifier:** When verifying rebuild, check that accidental complexity items are absent and edge cases are preserved
- **fire-researcher:** When researching alternatives for a stuck rebuild, check intent graph for original intent
