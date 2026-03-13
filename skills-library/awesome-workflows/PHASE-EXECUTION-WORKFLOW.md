---
name: phase-execution-workflow
category: awesome-workflows
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
last_updated: 2026-02-24
tags: [execution, phases, waves, breath, parallel]
difficulty: medium
---

# Phase Execution Workflow

## Problem

Large features require coordinated changes across many files. Sequential editing is slow and error-prone. Without structure, agents make conflicting changes or miss dependencies between tasks.

## Solution Pattern

Break execution into **waves** (groups of parallel tasks with no file overlap). Each wave completes fully before the next begins. This prevents merge conflicts while maximizing parallelism.

## Workflow Steps

### 1. Plan with File Overlap Analysis

Before executing, map which files each task touches:

```
Task A: models/user.js, routes/auth.js, middleware/auth.js
Task B: models/course.js, routes/courses.js
Task C: routes/auth.js, tests/auth.test.js
```

Tasks A and C overlap on `routes/auth.js` — they CANNOT run in parallel.

### 2. Group into Waves

```
Wave 1: Task A + Task B (no overlap → parallel)
Wave 2: Task C (depends on Task A's changes to auth.js)
Wave 3: Integration tests (depends on all prior waves)
```

### 3. Execute Each Wave

For each wave:
1. Spawn parallel agents (one per task in the wave)
2. Wait for ALL agents to complete
3. Verify no conflicts: `git diff --check`
4. Commit the wave: `git commit -m "feat: wave {N} — {description}"`
5. Run tests to confirm nothing broke
6. Proceed to next wave

### 4. Wave Completion Gates

Between waves, verify:
- [ ] All tasks in wave completed without errors
- [ ] Tests pass
- [ ] No unintended file changes
- [ ] Wave committed to git (checkpoint for recovery)

### 5. Final Verification

After all waves:
- Run full test suite
- Run credential filter
- Generate RECORD.md for the phase

## When to Use

- Any phase with 3+ tasks
- Cross-cutting changes (API + frontend + tests)
- Refactoring across multiple modules
- Database migrations with dependent code changes

## When NOT to Use

- Single-file changes
- Tasks with no parallelism opportunity
- Exploratory/research work (use research workflow instead)

## Real Example

Dominion Flow v9.0 execution:
- Wave 1: Scoring fixes + naming cleanup (5 files, parallel)
- Wave 2: 3 new agents created (5 files, parallel)
- Wave 3: Already existed — skipped
- Wave 4: Docs overhaul (3 files, parallel)
- Wave 5: Resilience upgrades (3 files, parallel)
- Security: Credential scrub (19 files, single agent)

Total: 35+ files, 5 waves, all committed with checkpoints.

## Related Skills

- [methodology/](../methodology/) — Planning methodology
- [patterns-standards/](../patterns-standards/) — Code quality standards
