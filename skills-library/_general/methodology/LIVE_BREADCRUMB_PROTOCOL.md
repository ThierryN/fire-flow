---
name: LIVE_BREADCRUMB_PROTOCOL
category: methodology
description: Automatic breadcrumb trail that makes each Claude instance smarter than the last
version: 1.0.0
tags: [reflexion, breadcrumbs, learning, memory, cross-session]
---

# Live Breadcrumb Protocol — Institutional Memory

Each Claude instance drops breadcrumbs as it works. The next instance reads them and starts smarter. Over time, the project accumulates institutional knowledge that no single session could hold.

> **Military analogy:** After-action reports. Every unit debriefs. The lessons go into doctrine. The next unit deploys with that doctrine baked in — they've never been to that battlefield, but they know what works there.

---

## Architecture

```
.planning/
  breadcrumbs/
    LESSONS.md           ← Living document: solutions that worked (READ FIRST)
    FAILURES.md          ← What was tried and failed (READ SECOND)
    PATTERNS.md          ← Project-specific patterns discovered during execution
    DEPENDENCIES.md      ← Gotchas with specific libraries/versions
```

### Why 4 files (not 1)

- **LESSONS.md** — "Do this" (positive knowledge, solutions)
- **FAILURES.md** — "Don't do this" (negative knowledge, dead ends)
- **PATTERNS.md** — "This is how things work here" (project conventions)
- **DEPENDENCIES.md** — "Watch out for this" (library/version gotchas)

Separating them lets agents read only what's relevant. A planner needs LESSONS + FAILURES. An executor needs PATTERNS + DEPENDENCIES. A researcher needs all four.

---

## When Breadcrumbs Are Written (Automatic Triggers)

### Trigger 1: After Solving a Non-Trivial Problem (> 2 attempts)
**Who writes:** fire-executor, fire-debugger → `LESSONS.md`
```markdown
### JWT refresh token not persisting
Root cause: httpOnly cookie not set on response — missing `credentials: 'include'`
Fix: add `credentials: 'include'` to fetch AND `cors({ credentials: true })` on server
```

### Trigger 2: After Verification Failure
**Who writes:** fire-verifier → `FAILURES.md`
```markdown
### Phase 2: Custom auth middleware approach FAILED
Tried: rolling own JWT validation middleware
Why: race condition on token refresh — 2 concurrent requests both try to refresh
Don't retry unless: switching to a battle-tested auth library (better-auth, lucia)
```

### Trigger 3: After Discovering a Project Pattern
**Who writes:** fire-executor, fire-planner → `PATTERNS.md`
```markdown
### API routes use camelCase, not snake_case
Example: `server/routes/userProgress.js` — `getUserProgress`, not `get_user_progress`
Breaks: frontend expects camelCase from API responses
```

### Trigger 4: After Hitting a Dependency Gotcha
**Who writes:** fire-executor, fire-researcher → `DEPENDENCIES.md`
```markdown
### next@15 — cookies() is now async
Symptom: `cookies()` returns Promise, not CookieStore
Fix: `const cookieStore = await cookies()` — must await in App Router
```

**Notice: every example above is 3-4 lines. That's the target.**

---

## When Breadcrumbs Are Read (Automatic Injection)

### On Session Start (via hooks)
When `/fire-6-resume` or a new session starts on an existing project:
```
1. Check if .planning/breadcrumbs/ exists
2. If yes: Read LESSONS.md (always) + FAILURES.md (always)
3. Inject as context: "Previous instances learned these lessons..."
4. PATTERNS.md and DEPENDENCIES.md are read on-demand by agents
```

### Before Planning (fire-planner, Step 1)
```
Read .planning/breadcrumbs/LESSONS.md
  → "Previous instances found these solutions..."
Read .planning/breadcrumbs/FAILURES.md
  → "Previous instances tried these and they FAILED..."

This prevents re-planning with approaches already proven to fail.
```

### Before Execution (fire-executor, start of each plan)
```
Read .planning/breadcrumbs/PATTERNS.md
  → "This project follows these conventions..."
Read .planning/breadcrumbs/DEPENDENCIES.md
  → "Watch out for these library gotchas..."
```

### During Recovery Research (fire-researcher, recovery mode)
```
Read ALL 4 breadcrumb files
  → "Here's everything previous instances learned about this project"
  → Cross-reference with FAILURES.md to avoid repeating dead ends
```

---

## File Templates (Slim — 2-line headers, 3-4 line entries)

### LESSONS.md
```markdown
# Lessons — {Project Name}
> Solutions that worked. Max 20 entries. Merge or archive when full.

### {title}
Root cause: {why}
Fix: {what to do}
```

### FAILURES.md
```markdown
# Dead Ends — {Project Name}
> What failed. If you're about to try something here, STOP.

### {approach that failed}
Tried: {what}
Why it failed: {root cause}
Don't retry unless: {condition}
```

### PATTERNS.md
```markdown
# Patterns — {Project Name}
> Follow these conventions. Breaks stuff if you don't.

### {pattern name}
Example: `{file:line}`
Breaks: {what goes wrong if ignored}
```

### DEPENDENCIES.md
```markdown
# Gotchas — {Project Name}
> Library-specific traps. Check before debugging weird errors.

### {package}@{version} — {title}
Symptom: {what you see}
Fix: {what to do}
```

---

## Breadcrumb Hygiene

### Size Limits — Breadcrumbs, Not a Loaf

**Hard caps per file:**
| File | Max entries | Max lines | Entry max |
|------|-------------|-----------|-----------|
| LESSONS.md | 20 | 80 lines | 4 lines |
| FAILURES.md | 15 | 60 lines | 4 lines |
| PATTERNS.md | 15 | 60 lines | 3 lines |
| DEPENDENCIES.md | 15 | 60 lines | 4 lines |

**Each breadcrumb is a CRUMB — 3-4 lines max.** If you need more than 4 lines to explain it, you're writing documentation, not a breadcrumb.

**Compact format (use this, not the verbose templates above):**
```markdown
### Prisma findMany returns empty on new schema
Root cause: forgot `npx prisma generate` after schema change
Fix: always run `prisma generate` after editing schema.prisma
```

**When a file hits the cap:**
1. Merge related entries (3 Prisma gotchas → 1 consolidated entry)
2. Delete entries that are obvious in hindsight (not worth preserving)
3. Only then archive to `.planning/breadcrumbs/archive/{filename}-{date}.md`
4. **Never let breadcrumbs exceed the cap** — an agent reading 80+ lines of "lessons" is wasting tokens on context it probably won't use

### Deduplication
Before writing a breadcrumb, check if a similar one already exists:
```
Grep pattern="{key phrase from new breadcrumb}" path=".planning/breadcrumbs/"
IF match found:
  → Update existing entry instead of creating duplicate
  → Add "Confirmed again on {date}" to show it's a recurring pattern
```

### Quality Check
Every breadcrumb must have:
- [ ] A clear **search term** (how would a future instance find this?)
- [ ] The **root cause** (not just the symptom)
- [ ] The **solution** or **warning** (actionable, not just descriptive)
- [ ] A **date** (to know how fresh this knowledge is)

Breadcrumbs without root causes are symptoms — not lessons. Don't write "X broke" without "because Y."

---

## Integration Points

| Agent | Reads | Writes |
|-------|-------|--------|
| **fire-planner** | LESSONS.md, FAILURES.md | PATTERNS.md (when discovering conventions during planning) |
| **fire-executor** | PATTERNS.md, DEPENDENCIES.md | LESSONS.md (after solving problems), PATTERNS.md (after discovering conventions), DEPENDENCIES.md (after hitting gotchas) |
| **fire-verifier** | — | FAILURES.md (after verification failure) |
| **fire-researcher** | All 4 files | DEPENDENCIES.md (after discovering version issues) |
| **fire-debugger** | LESSONS.md, FAILURES.md, DEPENDENCIES.md | LESSONS.md (after resolution), FAILURES.md (for dead ends tried) |
| **fire-6-resume** | LESSONS.md, FAILURES.md | — (read-only injection) |

---

## The Compounding Effect

```
Session 1:  Claude knows nothing about the project
            → Hits 5 problems, solves them
            → Writes 5 breadcrumbs

Session 2:  Claude reads 5 breadcrumbs
            → Avoids 3 of those problems entirely
            → Hits 2 new problems, solves them
            → Writes 2 new breadcrumbs (total: 7)

Session 3:  Claude reads 7 breadcrumbs
            → Avoids 5 problems, solves 1 new one
            → Total: 8 breadcrumbs

Session 10: Claude reads 15+ breadcrumbs
            → Knows every gotcha, every pattern, every dead end
            → Executes like a senior developer on the project
```

Each instance is disposable. The breadcrumbs are permanent. The knowledge compounds.
