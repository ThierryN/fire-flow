# DECISION_LOG.md Template

> **Origin:** Dominion Flow v3.2 - Research-backed improvement.
> cross-phase contradictions occur when rationale is buried in old handoffs.
> See: references/research-improvements.md (GAP-1, GAP-3, BLIND-SPOT-A)

Template for `.planning/DECISION_LOG.md` — created by `/fire-1a-new`.

---

## Why This Exists

Without an explicit decision log:
- Session 4 can contradict Session 1 decisions without realizing it
- "Why did we choose X?" requires reverse-engineering git history
- Deferred decisions get lost between phases
- Assumption conflicts across phases go undetected

---

## File Template

```markdown
# Decision Log

> Tracks architectural and design decisions across all phases.
> Each entry captures WHAT was decided, WHY, and WHAT IT AFFECTS.
> Review this log at the start of each new phase to catch contradictions.

## Quick Reference

| ID | Date | Decision | Phase | Status |
|----|------|----------|-------|--------|
<!-- Auto-populated as decisions are added below -->

---

## Decisions

### DEC-001: [Short title]
- **Date:** YYYY-MM-DD
- **Phase:** Phase N - [name]
- **Plan:** Plan N-NN (if applicable)
- **Category:** Architecture | Database | API | Auth | UI | Infrastructure | Integration
- **Decision:** [What was decided]
- **Options Considered:**
  1. [Option A] - [pros/cons]
  2. [Option B] - [pros/cons]
  3. [Option C] - [pros/cons]
- **Rationale:** [Why this option was chosen]
- **Trade-offs Accepted:** [What we gave up]
- **Affects:**
  - Phases: [which future phases depend on this]
  - Files: [key files implementing this decision]
  - Assumptions: [ASSUMPTION-XXX if linked]
- **Status:** ACTIVE | SUPERSEDED by DEC-XXX | DEFERRED to Phase N
- **Owner:** [who made the decision - human or agent]

---

## Superseded Decisions

> Decisions that were later overridden. Kept for audit trail.

### DEC-XXX: [title] (SUPERSEDED)
- **Superseded by:** DEC-YYY
- **Reason for change:** [what changed]
- **Migration needed:** [yes/no - what needs updating]

---

## Deferred Decisions

> Decisions postponed to a future phase. Review before that phase starts.

### DEC-XXX: [title] (DEFERRED)
- **Deferred to:** Phase N
- **Reason:** [not enough information / not critical yet / blocked by X]
- **Impact of delay:** [what happens if we defer too long]
- **Decision needed by:** [deadline or trigger event]
```

---

## When to Add Entries

- During `/fire-1a-discuss` — when architectural questions are resolved
- During `/fire-2-plan` — when plan requires technology/approach choices
- During `/fire-3-execute` — when executor makes runtime decisions
- During `/fire-debug` — when root cause reveals a design choice was wrong
- During `/fire-4-verify` — when verification finds gaps requiring decisions

---

## Cross-Phase Validation

At the start of each new phase, the planner should:

1. Read all ACTIVE decisions
2. Check for contradictions with the new plan
3. Verify no DEFERRED decisions have reached their deadline
4. Flag any SUPERSEDED decisions that still have unreversed code

---

## Integration Points

| Command | How it uses Decision Log |
|---------|------------------------|
| `/fire-1a-discuss` | Creates initial architectural decisions |
| `/fire-2-plan` | Reviews existing decisions, adds new ones |
| `/fire-3-execute` | Executor references decisions, adds runtime decisions |
| `/fire-4-verify` | Verifier checks code matches documented decisions |
| `/fire-5-handoff` | Handoff references key decisions from this session |
| `/fire-debug` | Links root causes to original decisions |
