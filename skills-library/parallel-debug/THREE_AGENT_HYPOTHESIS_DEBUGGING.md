---
name: three-agent-hypothesis-debugging
category: parallel-debug
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [debugging, parallel, hypothesis, agents, competing]
difficulty: hard
---

# Three-Agent Competing Hypothesis Debugging

## Problem

Single-agent debugging follows one hypothesis at a time. If the first hypothesis is wrong, the agent wastes time before trying alternatives. Complex bugs with multiple possible root causes need parallel investigation.

## Solution Pattern

Spawn 3 agents, each investigating a DIFFERENT hypothesis simultaneously. The first agent to find a confirmed root cause wins. Others are terminated. This is 2-3x faster than sequential debugging for complex issues.

## Workflow

### Step 1: Generate 3 Hypotheses

From symptoms, generate 3 distinct hypotheses:

```
Bug: "API returns 500 on course enrollment"

H1: Database constraint violation — enrollment table FK or unique constraint
H2: Middleware auth issue — token parsing fails silently, null user reaches handler
H3: Race condition — concurrent enrollments for same user/course
```

### Step 2: Spawn 3 Parallel Agents

```
Agent 1 (H1): "Investigate database constraints. Check enrollment table schema,
  run the INSERT manually, check for FK violations, check for duplicate keys."

Agent 2 (H2): "Investigate auth middleware. Add logging to token parsing,
  check if user object is null when reaching enrollment handler."

Agent 3 (H3): "Investigate race conditions. Check if enrollment INSERT has
  ON CONFLICT handling, test with 2 concurrent requests."
```

### Step 3: Collect Results

Each agent returns:
```
{
  hypothesis: "H1: Database constraint violation",
  verdict: "CONFIRMED" | "ELIMINATED" | "INCONCLUSIVE",
  evidence: ["FK on course_id references non-existent course 999"],
  fix: "Validate course exists before INSERT" | null
}
```

### Step 4: Choose Winner

| Scenario | Action |
|----------|--------|
| 1 CONFIRMED | Apply that agent's fix |
| 0 CONFIRMED, 3 ELIMINATED | Generate 3 new hypotheses from new evidence |
| 1+ INCONCLUSIVE | Give inconclusive agent more time/context |
| 2+ CONFIRMED | Compound bug — apply both fixes |

## Key Rules

1. **Hypotheses must be independent** — Each agent investigates a different root cause
2. **No shared state** — Agents don't read each other's investigation
3. **Time-boxed** — If no agent confirms within 10 minutes, stop and reassess
4. **Evidence required** — CONFIRMED needs reproducible proof, not speculation
5. **Don't fix what isn't broken** — Only CONFIRMED hypotheses get fixes

## When to Use
- Bugs with 3+ plausible root causes
- Production incidents where speed matters
- Flaky tests with non-deterministic behavior
- Bugs that have resisted sequential debugging

## When NOT to Use
- Obvious bugs (typos, missing imports)
- Bugs with a single clear hypothesis
- Issues where file access would conflict between agents
