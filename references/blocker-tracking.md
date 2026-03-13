# Dominion Flow Blocker Tracking Reference

> **Origin:** NEW for Dominion Flow v2.0 - Centralized blocker management system.

## Overview

Centralized blocker tracking across all phases and plans. Blockers are obstacles that prevent task completion. They are tracked in a living document (`BLOCKERS.md`) that persists across sessions and phases.

---

## BLOCKERS.md Location

```
.planning/BLOCKERS.md
```

Created automatically by `/fire-1a-new`. Updated by execution commands when blockers are encountered.

---

## Blocker Priority Levels

| Priority | Label | Impact | Response |
|----------|-------|--------|----------|
| **P0** | Critical | Blocks entire phase/milestone | Stop. Fix immediately. Escalate to user. |
| **P1** | High | Blocks 2+ tasks or downstream plans | Fix before continuing blocked tasks |
| **P2** | Medium | Blocks 1 task, workaround exists | Document workaround, continue |
| **P3** | Low | Quality concern, not blocking | Track for later improvement |

---

## Blocker Lifecycle

```
OPEN -> IN_PROGRESS -> RESOLVED
                    -> WONTFIX (with justification)
                    -> DEFERRED (moved to future phase)
```

---

## BLOCKERS.md Format

```markdown
# Project Blockers

## Summary
| Status | P0 | P1 | P2 | P3 | Total |
|--------|----|----|----|----|-------|
| Open   | 0  | 1  | 2  | 0  | 3     |
| Resolved | 0 | 2 | 1 | 1 | 4    |

## Open Blockers

### BLOCKER-005 [P1] Stripe webhook signature verification fails in production
- **Phase:** 04-checkout
- **Plan:** 04-02
- **Task:** Task 3 - Webhook handler
- **Opened:** 2026-02-07
- **Blocks:** Tasks 04-02-T4, 04-02-T5, Plan 04-03
- **Description:** Webhook signature verification passes locally with Stripe CLI but fails when deployed. Raw body parsing differs between local and Vercel.
- **Root Cause:** (investigating)
- **Workaround:** None yet
- **Assigned:** Next execution session

### BLOCKER-006 [P2] Image upload exceeds 4.5MB Vercel limit
- **Phase:** 05-media
- **Plan:** 05-01
- **Task:** Task 2 - Upload handler
- **Opened:** 2026-02-07
- **Blocks:** Task 05-01-T2
- **Description:** Users uploading high-res images hit Vercel's 4.5MB body size limit.
- **Root Cause:** Vercel serverless function body size limit
- **Workaround:** Client-side resize before upload (implemented as temporary fix)
- **Assigned:** Future optimization phase

## Resolved Blockers

### BLOCKER-001 [P1] Database connection pool exhaustion (RESOLVED)
- **Phase:** 02-auth
- **Plan:** 02-03
- **Resolved:** 2026-02-06
- **Resolution:** Switched to PgBouncer connection pooling via Supabase
- **Skill Created:** database-solutions/CONNECTION_POOL_EXHAUSTION_FIX.md
```

---

## When to Create Blockers

| Trigger | Priority | Action |
|---------|----------|--------|
| Task cannot complete due to external dependency | P1 | Create blocker, skip task, continue |
| Task cannot complete due to missing prerequisite | P1 | Create blocker, check if prerequisite was missed |
| Test fails and cannot be fixed in 2 attempts | P1 | Create blocker, run `/fire-diagnose` |
| Performance issue discovered during execution | P2 | Create blocker, continue with current plan |
| Code smell or tech debt identified | P3 | Create blocker, continue |
| Architectural concern surfaces during execution | P0/P1 | Create blocker, STOP, present to user |

---

## Integration Points

### During Plan Execution (`/fire-execute-plan`)

When a task encounters a blocker:
1. Create entry in BLOCKERS.md with unique ID
2. Record which tasks/plans it blocks
3. If P0/P1: Present to user immediately
4. If P2/P3: Log and continue

### During Phase Transition (`/fire-transition`)

Before transitioning to next phase:
1. Check BLOCKERS.md for open P0/P1 blockers
2. If open P0: BLOCK transition, must resolve first
3. If open P1: WARN, allow transition with acknowledgment
4. Report blocker resolution rate in phase metrics

### During Verification (`/fire-4-verify`)

Verification checks blocker status:
- All P0 blockers resolved? (required)
- All P1 blockers resolved or deferred? (required)
- P2/P3 tracked for future phases? (recommended)

### In CONSCIENCE.md

```markdown
## Blocker Status
- Open: 3 (0 P0, 1 P1, 2 P2)
- Resolved this phase: 4
- Resolution rate: 57%
```

---

## Blocker-to-Skill Pipeline

When a blocker is resolved with a novel solution:
1. Auto-skill extraction detects the pattern
2. Prompts: "Blocker BLOCKER-001 resolved with novel approach. Save as skill?"
3. If approved: Creates skill with Problem/Solution/Prevention sections
4. Links skill back to blocker entry

---

## Commands

| Command | Action |
|---------|--------|
| Create blocker | Add entry during execution |
| Resolve blocker | Update status, add resolution |
| List blockers | Show open blockers by priority |
| Blocker report | Summary for phase transition |
