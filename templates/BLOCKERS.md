# BLOCKERS.md Template

> **Origin:** NEW for Dominion Flow v2.0 - Centralized blocker tracking.

Template for `.planning/BLOCKERS.md` — created by `/fire-1-new`.

---

## File Template

```markdown
# Project Blockers

## Summary
| Status | P0 | P1 | P2 | P3 | Total |
|--------|----|----|----|----|-------|
| Open   | 0  | 0  | 0  | 0  | 0     |
| Resolved | 0 | 0 | 0 | 0 | 0    |

---

## Open Blockers

[None currently]

---

## Resolved Blockers

[None yet]

---

## Deferred Blockers

[None yet]
```

---

## Blocker Entry Format

```markdown
### BLOCKER-[NNN] [P0/P1/P2/P3] [Short description]
- **Phase:** [phase identifier]
- **Plan:** [plan identifier]
- **Task:** [task identifier]
- **Opened:** [date]
- **Blocks:** [what this prevents - tasks, plans, or phases]
- **Description:** [detailed description of the obstacle]
- **Root Cause:** [identified root cause or "investigating"]
- **Workaround:** [temporary workaround if available, or "None"]
- **Assigned:** [who/what will resolve - "Next session", "User action required", etc.]
```

## Resolved Entry Addition

```markdown
- **Resolved:** [date]
- **Resolution:** [how it was fixed]
- **Skill Created:** [if solution was extracted to skills library]
```

---

## Priority Guide

| Priority | Criteria | Response Time |
|----------|----------|---------------|
| P0 | Blocks entire phase/milestone | Immediate - stop everything |
| P1 | Blocks 2+ tasks or downstream plans | Fix before continuing blocked work |
| P2 | Blocks 1 task, workaround exists | Document workaround, continue |
| P3 | Quality concern, not blocking | Track for later |
