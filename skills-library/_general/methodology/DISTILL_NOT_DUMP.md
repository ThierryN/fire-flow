---
name: DISTILL_NOT_DUMP
category: methodology
description: Handoffs and context transfers must distill decisions, not dump exploration reasoning
version: 1.0.0
tags: [handoff, context-management, session-continuity, warrior, planning-execution-gap]
---

# DISTILL — NOT DUMP

## Problem

A handoff or context file contains:
- Full planning discussion transcripts
- "We considered A, B, C... decided on B because..."
- Every intermediate hypothesis from debugging
- All the reasoning that led to the current architecture

A fresh Claude instance reads this and now has a **planning-contaminated context**.
It knows WHY decisions were made, which makes it second-guess WHAT to execute.
Execution quality degrades because the agent is still in planning mode.

**Goose (Block) research finding:** Planning context actively degrades execution.
An agent that knows all the alternatives considered will hedge, caveat, and
reconsider instead of executing decisively.

## Solution

Separate WHAT WAS DECIDED from HOW WE GOT THERE. Handoffs capture only the first.

### What to INCLUDE

```
- Final decision: "Use JWT with 15-minute expiry + refresh tokens"
- Current phase and task: "Phase 3 / Task 2 — implement refresh endpoint"
- Known constraints: "MySQL 8.0, no Redis available in this environment"
- Blockers: "migration 096 must run before this task"
- File paths and exact names: "auth/refreshToken.js — does not exist yet"
```

### What to PRUNE

```
- Why we chose JWT over sessions (exploration history)
- The 3 approaches we considered for token storage
- The failed experiment with cookies
- "We discussed whether to use..."
- "Originally we thought... but then decided..."
```

## Implementation: Context Pruning Step

Add this step to handoff creation commands (fire-5-handoff.md, warrior-handoff.md):

```markdown
### Step 2.5: Context Pruning Discipline

Before writing the handoff, classify each piece of context:

KEEP (execution-critical):
  - Current task and next action
  - Final decisions made (what, not why)
  - Constraints that affect implementation
  - Known blockers or prerequisites
  - File paths, names, and state

PRUNE (planning artifacts):
  - Reasoning chains that led to decisions
  - Alternatives that were rejected
  - Exploration history and "we tried X"
  - Hypothesis chains from debugging (keep SOLUTION, prune PATH TO SOLUTION)
  - Discussion summaries

Rule: If removing this information would not prevent a fresh agent from
executing the next task correctly → PRUNE IT.
```

## The Litmus Test

For every sentence in a handoff, ask:

> "Does a fresh agent NEED this to execute the next task, or does it just help
> understand HOW WE GOT HERE?"

If the answer is "understand how we got here" → prune it.

## Why This Matters for Dominion Flow

The WARRIOR handoff cycle is the core continuity mechanism. Its value is **session
velocity** — a fresh instance should be able to pick up exactly where we left off
at full speed. Verbose handoffs slow this down:
- Fresh agent must read more before acting
- Planning context bleeds into execution mode
- Hedging and reconsideration appear in execution output

A distilled handoff of 200 lines outperforms a comprehensive dump of 2000 lines
every time.

## Related Patterns

- `TIERED_CONTEXT_ARCHITECTURE.md` — Context hierarchy: project → phase → task

## Research Basis

> **Goose (Block) history-clear pattern** — Planning context degrades execution quality.
> Agents with full planning history in context hedge and reconsider during execution.
> Applied: Step 2.5 (Context Pruning Discipline) added to fire-5-handoff.md in v12.3.
> Core principle: WARRIOR handoff must DISTILL not DUMP.
