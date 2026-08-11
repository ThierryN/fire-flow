# Dominion Flow Execution Mode Intelligence

## Overview

Dominion Flow automatically determines whether to use **Swarm Mode** (multi-agent parallel teams), **Subagent Mode** (Task tool parallelism), or **Sequential Mode** based on plan/task characteristics. The Team Lead never needs to manually choose — the system analyzes the work and selects the optimal execution strategy.

---

## Execution Modes

| Mode | How It Works | Best For |
|------|-------------|----------|
| **Swarm** | Team Lead spawns specialist teammates via Agent Teams | Multi-file features, full-stack plans, parallel debugging |
| **Subagent** | Task tool spawns focused executor agents per plan | Breath-based phase execution, isolated plan work |
| **Sequential** | Single agent executes tasks one at a time | Decision-dependent work, small plans, high-risk changes |

---

## Decision Algorithm

### Phase-Level Decision (in `/fire-3-execute`)

When executing a phase with multiple plans grouped into breaths:

```
FOR each breath in phase:
  independent_plans = plans in this breath (all can run in parallel)

  IF independent_plans.count == 1:
    MODE = SEQUENTIAL (single plan, no parallelism needed)

  ELIF independent_plans.count >= 3 AND no_file_overlap(plans):
    MODE = SWARM (many independent plans, dedicated agents per specialty)
    REASON: "3+ independent plans with no file overlap — swarm is optimal"

  ELIF independent_plans.count >= 2 AND no_file_overlap(plans):
    MODE = SUBAGENT (Task tool spawns executor per plan)
    REASON: "2 parallel plans — subagent execution is sufficient"

  ELIF independent_plans.count >= 2 AND has_file_overlap(plans):
    MODE = SEQUENTIAL (file conflicts require serialization)
    REASON: "File overlap detected — sequential prevents merge conflicts"

  ELSE:
    MODE = SEQUENTIAL (default safe mode)
```

### Plan-Level Decision (in `/fire-execute-plan`)

When executing a single plan with multiple tasks:

```
FOR plan:
  tasks = all tasks in plan
  auto_tasks = tasks where type == "auto"
  checkpoint_tasks = tasks where type starts with "checkpoint:"

  IF checkpoint_tasks has type "checkpoint:decision":
    MODE = SEQUENTIAL (decisions require user interaction in main context)
    REASON: "Decision checkpoint requires main context"

  ELIF auto_tasks.count >= 3 AND tasks_are_independent(auto_tasks):
    AND plan.risk_level != "high":
    MODE = SWARM (multiple independent auto tasks, spawn specialist team)
    REASON: "3+ independent tasks — Team Lead delegates to specialists"
    TEAM:
      - Backend specialist (API/DB tasks)
      - Frontend specialist (UI/component tasks)
      - Test specialist (test writing tasks)

  ELIF auto_tasks.count >= 2 AND tasks_are_independent(auto_tasks):
    MODE = SUBAGENT (2 parallel segments possible)
    REASON: "2 independent segments — subagent per segment"

  ELIF plan.risk_level == "high":
    MODE = SEQUENTIAL (high-risk needs careful, serial attention)
    REASON: "High-risk plan — sequential for careful execution"

  ELSE:
    MODE = SEQUENTIAL (default)
```

---

## Independence Checks

### File Overlap Detection

```
no_file_overlap(plans) =
  FOR each pair of plans (A, B):
    files_A = A.frontmatter.files_modified
    files_B = B.frontmatter.files_modified
    IF intersection(files_A, files_B) is not empty:
      RETURN false
  RETURN true
```

### Task Independence Detection

```
tasks_are_independent(tasks) =
  FOR each pair of tasks (A, B):
    IF A.files overlaps B.files:
      RETURN false
    IF B references output of A:
      RETURN false
  RETURN true
```

### Specialty Detection (for Swarm team composition)

```
detect_specialties(tasks) =
  specialties = {}
  FOR each task:
    IF task.files match "src/api/*" OR "src/models/*" OR "prisma/*":
      specialties.add("backend")
    IF task.files match "src/components/*" OR "src/app/*" OR "*.css":
      specialties.add("frontend")
    IF task.files match "*test*" OR "*spec*":
      specialties.add("testing")
    IF task.files match "*.sql" OR "prisma/migrations/*":
      specialties.add("database")
  RETURN specialties
```

---

## Mode Display

When execution mode is selected, display to user:

```
+---------------------------------------------------------------+
|  EXECUTION MODE: SWARM                                         |
+---------------------------------------------------------------+
|                                                                 |
|  Breath 1: 3 independent plans                                  |
|  File overlap: None detected                                   |
|  Risk level: Low                                               |
|                                                                 |
|  Team Lead will delegate to:                                   |
|    Backend Agent:  Plan 03-01 (API endpoints)                  |
|    Frontend Agent: Plan 03-02 (Dashboard UI)                   |
|    Test Agent:     Plan 03-03 (Integration tests)              |
|                                                                 |
|  Rationale: 3+ independent plans with no file overlap          |
|             and complementary specialties                       |
+-----------------------------------------------------------------+
```

```
+---------------------------------------------------------------+
|  EXECUTION MODE: SEQUENTIAL                                    |
+---------------------------------------------------------------+
|                                                                 |
|  Plan 04-02: Checkout flow                                     |
|  Decision checkpoint at Task 2 (payment provider)              |
|  Risk level: High (payment processing)                         |
|                                                                 |
|  Rationale: Decision checkpoint requires user interaction       |
|             + high-risk plan benefits from careful execution    |
+-----------------------------------------------------------------+
```

---

## Swarm Team Composition

When SWARM mode is selected, compose the team based on detected specialties:

| Detected Specialty | Agent Role | Assignment |
|-------------------|------------|------------|
| backend | Backend Specialist | API routes, middleware, database queries |
| frontend | Frontend Specialist | React components, pages, styles |
| testing | Test Specialist | Unit tests, integration tests, E2E |
| database | Database Specialist | Migrations, schema changes, seeds |
| mixed (single plan) | Full-Stack Agent | Entire plan execution |

### Swarm Prompt Template

```
"Execute Phase {N}, Breath {W} as a team.

Team composition:
- Backend Agent: Execute Plan {N}-01 (API endpoints for {feature})
  Context: @.planning/phases/{N}-name/{N}-01-BLUEPRINT.md

- Frontend Agent: Execute Plan {N}-02 (UI components for {feature})
  Context: @.planning/phases/{N}-name/{N}-02-BLUEPRINT.md

- Test Agent: Execute Plan {N}-03 (Tests for {feature})
  Context: @.planning/phases/{N}-name/{N}-03-BLUEPRINT.md

Rules:
- Each agent commits atomically per task
- Each agent creates their own RECORD.md
- Coordinate on shared types/interfaces
- Flag any dependency discoveries immediately
"
```

---

## Override Flags

Users can override the automatic decision:

```yaml
optional_flags:
  --swarm: "Force swarm mode regardless of analysis"
  --sequential: "Force sequential mode regardless of analysis"
  --subagent: "Force subagent mode (Task tool parallelism)"
```

---

## Fallback Rules

| Situation | Fallback |
|-----------|----------|
| Swarm mode not available (env var not set) | Fall back to Subagent mode |
| Subagent hits permission error | Fall back to Sequential mode |
| File overlap detected mid-execution | Pause, serialize remaining tasks |
| Swarm agent fails | Retry as Subagent, then Sequential |

---

## Metrics Tracking

Each execution records the mode used in RECORD.md:

```yaml
metrics:
  execution_mode: swarm|subagent|sequential
  mode_reason: "3+ independent plans with no file overlap"
  agents_spawned: 3
  parallel_efficiency: "42% faster than sequential estimate"
```

This data feeds into trend analysis for optimizing future mode decisions.
