---
name: review-fix-loop
category: methodology
version: 1.0.0
contributed: 2026-03-08
contributor: dominion-flow
last_updated: 2026-03-08
tags: [review, subagent, circuit-breaker, quality-gate, fix-loop, multi-agent]
difficulty: hard
---

# Review-Fix Loop — Automated Subagent Quality Gate

## Problem

After implementing changes (research findings, feature code, refactors), there's no automated quality gate. Errors ship silently because:
- The implementing agent has blind spots from its own context
- Manual review is slow and inconsistent
- Without structured feedback, the same mistakes recur across sessions
- No circuit breaker prevents infinite fix-review cycles

## Solution Pattern

Spawn parallel reviewer subagents after each implementation breath. Collect findings, classify by severity, fix in a loop with circuit breaker escapes. The pattern separates concerns (correctness vs consistency) across independent reviewers, uses weight-based stuck detection, and maps dead-end types to specific interventions.

```
FOR each completed breath:

  1. SPAWN 2+ parallel reviewer agents (code-reviewer subagent_type)
     - Reviewer A: Implementation Correctness (linting, tests, citations)
     - Reviewer B: Integration & Consistency (cross-file, naming, numbering)

  2. COLLECT findings, classify severity: CRITICAL / IMPORTANT / MINOR

  3. FIX-LOOP (max 3 attempts, weight-based circuit breaker):
     - Fix all CRITICAL first, then IMPORTANT
     - Re-run reviewers on changed files only
     - Track accumulated_weight: CRITICAL=1.0, IMPORTANT=0.5
     - IF weight > 5.0: classify stuck state and escape

  4. EXIT CONDITIONS:
     - CLEAN: all CRITICAL+IMPORTANT resolved → proceed
     - FIXATION: same findings recur → log as deferred, proceed
     - LOGIC: fixes create new problems → rollback once, retry
     - ARCHITECTURE: structural issue → stop pipeline, escalate
```

## Implementation Steps

1. After completing a unit of work (breath, wave, phase), identify all modified files
2. Launch 2+ reviewer agents in a SINGLE message for true parallelism
3. Each reviewer returns structured findings: `{severity, summary, file, line}`
4. Merge findings, display counts by severity
5. Enter fix loop — apply fixes, re-review, track circuit breaker weight
6. On clean exit, proceed. On dead-end, classify and route appropriately

## When to Use

- After implementing research findings (`/fire-research` Step 6.5)
- After any multi-file implementation where cross-file consistency matters
- When changes touch coordination protocols (naming, taxonomies, step numbering)
- After porting code between projects (ministry-lms porting pattern)
- Any time you want automated quality validation before moving to the next task

## When NOT to Use

- Single-line fixes or trivial changes (overhead exceeds benefit)
- When the change is already covered by existing test suites with high coverage
- During exploratory/research phases where code isn't being committed
- When circuit breaker has already tripped on this exact scope (don't re-enter)

## Must Do

- Separate reviewers by concern (correctness vs consistency)
- Use severity classification — MINOR findings NEVER block progression
- Track accumulated weight across fix attempts (not just attempt count)
- Classify dead-end type BEFORE choosing intervention
- Re-run reviewers on CHANGED FILES ONLY (not full codebase)

## Must Not Do

- Do not let MINOR findings block the pipeline
- Do not retry more than 3 times without dead-end classification
- Do not use a single reviewer for both correctness and consistency
- Do not skip the circuit breaker — infinite fix loops waste tokens
- Do not rollback more than once for LOGIC errors (tag as DEAD_END on second attempt)

## Common Mistakes

- Using a single "general review" agent instead of separating concerns
- Treating all findings equally (no severity classification)
- No escape mechanism — the loop runs forever burning tokens
- Fixing MINOR issues while CRITICAL ones remain
- Re-reviewing the entire codebase instead of just changed files

## Proven Results

First use (v13.0 multi-agent coordination, 2026-03-08):
- 3 parallel code-reviewer agents spawned
- 18 findings collected (7 critical, 9 important, 2 informational)
- 11 fixes applied in one pass
- Caught: TRANSIENT naming collision, missing SWARM awareness in executor,
  broken JSON fences, unspecified DAG reorder, verdict arbitration gaps

## Related Skills

- [CIRCUIT_BREAKER_INTELLIGENCE](./CIRCUIT_BREAKER_INTELLIGENCE.md) — stuck-state classification feeds dead-end routing
- [MULTI_AGENT_COORDINATION](./MULTI_AGENT_COORDINATION.md) — structured envelope and cascade prevention
- [CONTEXT_ROTATION](./CONTEXT_ROTATION.md) — fresh-eyes pattern for FIXATION-type dead-ends
- [SELF_TESTING_FEEDBACK_LOOP](./SELF_TESTING_FEEDBACK_LOOP.md) — related self-validation pattern

## References

- Dominion Flow v13.0 — first implementation in `/fire-research` Step 6.5
- biome `handler.rs` — catch_unwind isolation pattern (MIT)
- oxc `service.rs` — cumulative warning thresholds (MIT)
- Contributed from: dominion-flow internal session 2026-03-08
