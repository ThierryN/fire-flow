---
name: debugging-workflow
category: awesome-workflows
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
last_updated: 2026-02-24
tags: [debugging, hypothesis, reflexTree, failure-taxonomy]
difficulty: medium
---

# Debugging Workflow

## Problem

Flat debugging (try random fixes until something works) wastes time and teaches nothing. Without structure, agents repeat the same failed approaches, miss root causes, and create fragile patches instead of real fixes.

## Solution Pattern

Structured hypothesis-driven debugging with a tree of evidence, failure taxonomy classification, and persistent memory for future reference.

## Workflow Steps

### 1. Classify the Failure

Use the AgentDebug failure taxonomy to categorize:

| Type | Symptoms | Example |
|------|----------|---------|
| MEMORY | Agent forgets context, repeats work | "I already tried that approach" |
| REFLECTION | Agent doesn't learn from failures | Same error 3 times in a row |
| PLANNING | Wrong approach chosen | Editing wrong file, wrong API |
| ACTION | Correct plan, bad execution | Typo in code, wrong parameter |
| SYSTEM | External failure | DB down, API rate limit, build tool crash |

### 2. Build Hypothesis Tree (ReflexTree v9.1)

Structure debugging as a branching tree, not a flat list:

```markdown
# Hypothesis Tree: {bug-slug}

## H1: Database connection timeout [ACTIVE]
  Evidence for: Error log shows "ETIMEDOUT" at 30s
  Evidence against: Other queries work fine
  ### H1.1: Connection pool exhausted [ACTIVE]
    Evidence for: 50 active connections in pg_stat_activity
    Evidence against: Pool limit is 100
  ### H1.2: Slow query blocking pool [PRUNED]
    Evidence for: None found
    Evidence against: pg_stat_activity shows no long-running queries

## H2: Network firewall blocking port [PRUNED]
  Evidence for: None
  Evidence against: telnet to DB host:5432 succeeds
```

### 3. Investigate with Evidence Collection

For each ACTIVE hypothesis:
1. Design a test that would CONFIRM or ELIMINATE it
2. Run the test
3. Update evidence for/against
4. If eliminated → mark PRUNED (never delete)
5. If narrowing → branch into sub-hypotheses

### 4. Fix and Verify

When CONFIRMED:
1. Implement the fix
2. Write a test that would catch regression
3. Verify the original symptom is gone
4. Run full test suite to check for side effects

### 5. Record for Future Reference

Save debug resolution to `.planning/debug/{slug}.md` for indexing into Qdrant:

```yaml
---
slug: {bug-slug}
category: {MEMORY|REFLECTION|PLANNING|ACTION|SYSTEM}
status: resolved
resolved_date: YYYY-MM-DD
---

## Trigger
{What symptom triggered this debug session}

## Root Cause
{The actual problem}

## Fix
{What was changed}

## Lesson
{What to do differently next time}
```

## Rules

1. Maximum tree depth: 3 levels (H1 → H1.1 → H1.1.1)
2. Never delete pruned hypotheses — they're evidence of what was eliminated
3. Each investigation step MUST update at least one hypothesis
4. Stop branching when CONFIRMED — proceed to fix
5. If all hypotheses pruned → step back and generate new top-level hypotheses

## When to Use

- Any bug that isn't immediately obvious (> 5 minutes to understand)
- Recurring bugs (check Qdrant for past similar failures first)
- Production incidents (structured approach prevents panic-driven fixes)
- Flaky tests (multiple possible root causes)

## When NOT to Use

- Typos and obvious syntax errors
- Known issues with documented fixes
- Build/config issues with clear error messages

## Related Skills

- [parallel-debug/parallel-debug.md](../parallel-debug/) — 3-agent competing hypothesis pattern
- [methodology/](../methodology/) — Process standards
