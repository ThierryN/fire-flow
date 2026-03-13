---
description: Execute a single plan with segment-based routing, per-task atomic commits, and test enforcement
---

# /fire-execute-plan

> Execute one BLUEPRINT.md with intelligent segmentation, atomic commits per task, and enforced test gates.

---

## Arguments

```yaml
arguments:
  plan_id:
    required: false
    type: string
    description: "Plan ID (e.g., 03-02). If omitted, auto-detects next unexecuted plan."

optional_flags:
  --continue: "Resume from .continue-here.md"
  --branch: "Custom feature branch name"
  --no-branch: "Execute on current branch"
  --dry-run: "Parse segments without executing"
  --main-only: "Force all segments to main context"
```

---

## Process

### Step 1: Load Project State

```
+---------------------------------------------------------------+
|               DOMINION FLOW >>> PLAN EXECUTION                    |
+---------------------------------------------------------------+
```

Load CONSCIENCE.md: current phase, accumulated decisions, blockers/concerns.

### Step 2: Identify Plan

If plan_id provided: locate directly. If omitted: find first BLUEPRINT.md without matching RECORD.md.

### Step 3: Create Feature Branch

Unless `--no-branch`:
```bash
git checkout -b "feat/${PHASE}-${PLAN}-${PLAN_NAME_SLUG}"
```

### Step 4: Parse Segments and Select Execution Mode

**Parse segments** based on checkpoints:

| Pattern | Condition | Segment Strategy |
|---------|-----------|-----------------|
| A - Autonomous | No checkpoints | Single executor, entire plan |
| B - Segmented | Verify-only checkpoints | Executor per segment, main for checkpoints |
| C - Decision-Dependent | Decision/action checkpoints | All in main context |

**Auto-select execution mode** (see `@references/execution-mode-intelligence.md`):

```
auto_tasks = tasks where type == "auto"
checkpoint_tasks = tasks where type starts with "checkpoint:"
specialties = detect_specialties(auto_tasks)

IF checkpoint_tasks has "checkpoint:decision":
  MODE = SEQUENTIAL
  REASON: "Decision checkpoint requires user interaction"

ELIF auto_tasks.count >= 3 AND tasks_are_independent(auto_tasks)
     AND plan.risk_level != "high":
  MODE = SWARM
  REASON: "3+ independent tasks — Team Lead delegates to specialists"
  TEAM: compose from detected specialties (backend/frontend/test)

ELIF auto_tasks.count >= 2 AND tasks_are_independent(auto_tasks):
  MODE = SUBAGENT
  REASON: "2 independent segments — parallel subagent execution"

ELIF plan.risk_level == "high":
  MODE = SEQUENTIAL
  REASON: "High-risk plan — careful serial execution"

ELSE:
  MODE = SEQUENTIAL (default)
```

**Display:**
```
+---------------------------------------------------------------+
|  PLAN EXECUTION MODE: [SWARM/SUBAGENT/SEQUENTIAL]              |
+---------------------------------------------------------------+
|  Plan: {phase}-{plan}  |  Tasks: {N}  |  Risk: {level}        |
|  Segments: {pattern A/B/C}                                     |
|  Rationale: {why this mode}                                    |
|                                                                 |
|  [If SWARM:] Team: Backend + Frontend + Test specialists       |
+-----------------------------------------------------------------+
```

### Step 5: Execute Segments with Per-Task Commits

**Per-Task Atomic Commit Protocol:**

1. Complete task and verify
2. Stage ONLY task-related files (never `git add .`)
3. Commit: `{type}({phase}-{plan}): {task description}`
4. Record commit hash for SUMMARY

**Deviation Rules:**
- Rule 1 - Auto-fix bugs
- Rule 2 - Auto-add missing critical (error handling, validation, auth)
- Rule 3 - Auto-fix blockers (missing dep, wrong types)
- Rule 4 - ASK about architectural changes (new table, schema change)

### Step 6: Test Enforcement After Each Segment

```bash
npm test || yarn test || pytest || go test ./...
```

If tests fail:
- Option A: Auto-fix (attempt 2x, then manual)
- Option B: Skip (tracked in SUMMARY)
- Option C: Stop execution

### Step 7: Generate RECORD.md

Create `.planning/phases/XX-name/{phase}-{plan}-RECORD.md` using `templates/summary.md` format.

Include: task commits table, deviations, test results, decisions, metrics frontmatter.

### Step 8: Update Planning Artifacts

- CONSCIENCE.md: position, progress, decisions
- VISION.md: plan count
- BLOCKERS.md: any new blockers

### Step 9: Commit Metadata

```bash
git add .planning/phases/XX-name/{phase}-{plan}-RECORD.md
git add .planning/CONSCIENCE.md .planning/VISION.md
git commit -m "docs({phase}-{plan}): complete {plan-name}

Tasks completed: {N}/{N}
SUMMARY: .planning/phases/XX-name/{phase}-{plan}-RECORD.md"
```

### Step 10: Route Next Action

| Condition | Next Action |
|-----------|------------|
| More plans in phase | `/fire-execute-plan` for next plan |
| Phase complete | `/fire-verify-uat {phase}` |
| Phase verified | `/fire-transition` |

---

## Success Criteria

- [ ] Plan identified and loaded
- [ ] Feature branch created (unless --no-branch)
- [ ] Each task committed atomically
- [ ] Tests passed after each segment
- [ ] RECORD.md created with metrics
- [ ] CONSCIENCE.md and VISION.md updated
- [ ] User knows next action

---

## References

- **Execution Mode:** `@references/execution-mode-intelligence.md`
- **Protocol:** `@references/honesty-protocols.md`
- **Testing:** `@references/testing-enforcement.md`
- **Git:** `@references/git-integration.md`
- **Checkpoints:** `@references/checkpoints.md`
