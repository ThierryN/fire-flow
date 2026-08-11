# Bottleneck Detection & Trend Analysis

## Overview

Tracks execution performance across phases and plans to identify bottlenecks, predict durations, and surface improvement opportunities.

## Metrics Collection Points

### Per-Plan Metrics (collected in RECORD.md frontmatter)

```yaml
---
metrics:
  duration_minutes: 12
  tasks_completed: 4
  tasks_blocked: 0
  files_created: 3
  files_modified: 5
  lines_added: 245
  lines_removed: 30
  tests_added: 6
  test_coverage_delta: "+3%"
  skills_applied: 2
  honesty_checkpoints: 1
  commits: 4
  blocker_count: 0
---
```

### Per-Phase Metrics (aggregated in CONSCIENCE.md)

```yaml
## Phase Metrics
| Phase | Plans | Duration | Avg/Plan | Trend | Bottleneck |
|-------|-------|----------|----------|-------|------------|
| 3     | 4     | 45m      | 11m      | -     | None       |
| 3.1   | 3     | 35m      | 12m      | +8%   | Breath 3     |
| 3.2   | 3     | 28m      | 9m       | -25%  | None       |
| 3.4   | 6     | 72m      | 12m      | +33%  | Plan 05    |
```

### Per-Milestone Metrics (in MILESTONES.md)

```yaml
## Milestone: v1.0 LMS Core
- Total phases: 12
- Total plans: 49
- Total duration: ~430m (~7.2 hours)
- Average phase: 36m
- Average plan: 8.8m
- Longest phase: Phase 3.4 (72m, 6 plans)
- Shortest phase: Phase 3.2 (28m, 3 plans)
- Blocker rate: 2/49 plans (4%)
- Skill reuse rate: 35% (skills applied from library vs new)
```

### Per-Iteration Turn Rewards (v6.0 — AgentPRM)

> enabling fine-grained learning signals beyond binary success/fail.

```yaml
## Turn-Level Metrics (collected in dominion-flow.local.md per loop session)
iteration_rewards:
  - iteration: 1
    reward: 4.2
    task: "fix auth bug in login controller"
    completion: 5       # task fully completed first try
    quality: 4          # 1 retry needed
    efficiency: 4       # ~25k tokens used

  - iteration: 2
    reward: 2.1
    task: "add input validation to API"
    completion: 3       # partial completion
    quality: 2          # 3 retries needed
    efficiency: 2       # ~60k tokens used

session_summary:
  total_iterations: 5
  average_reward: 3.4
  lowest_reward: {iteration: 2, reward: 2.1, task: "add input validation"}
  highest_reward: {iteration: 4, reward: 4.8, task: "update test fixtures"}
  reward_trend: "stable"  # improving | stable | declining
```

**Reward Formula:**
```
turn_reward = (0.5 * task_completion) + (0.3 * approach_quality) + (0.2 * context_efficiency)

task_completion:   0-5  (5=complete, 0=no progress)
approach_quality:  0-5  (5=first try success, 1=4+ retries)
context_efficiency: 0-5 (5=<20k tokens, 1=>80k tokens)
```

**Downstream Uses:**
1. **Handoff:** Session average reward stored in WARRIOR handoff for cross-session trending
2. **Skill pre-loading:** Low-reward task types trigger proactive skill search on next occurrence
3. **Approach rotation:** Declining reward trend triggers earlier rotation in Step 9 classification
4. **Episodic recall boost:** When similar task type found in memory, inject reward context:
   "Previous sessions scored {avg_reward} on {task_type}. Common issue: {lowest_reward_task}"

---

## Bottleneck Detection Algorithm

### What Constitutes a Bottleneck

A plan or phase is flagged as a bottleneck when:

1. **Duration Outlier:** Plan takes >2x the average duration for its phase
2. **Blocker Rate:** >20% of tasks in a plan are blocked
3. **Rework Rate:** Plan requires >1 verification cycle (failed then re-executed)
4. **Dependency Chain:** Plan blocks 2+ downstream plans
5. **Complexity Spike:** Lines changed >3x average for similar plans

### Detection Rules

```
RULE 1: Slow Plan
  IF plan.duration > (phase.avg_plan_duration * 2)
  THEN flag as BOTTLENECK:SLOW
  SUGGEST: Break into smaller plans, check for missing skills

RULE 2: Blocked Plan
  IF plan.tasks_blocked > (plan.tasks_total * 0.2)
  THEN flag as BOTTLENECK:BLOCKED
  SUGGEST: Review dependencies, check BLOCKERS.md, missing prerequisites

RULE 3: Failed Verification
  IF plan.verification_attempts > 1
  THEN flag as BOTTLENECK:QUALITY
  SUGGEST: Add more specific must-haves, improve assumption validation

RULE 4: Fan-Out Blocker
  IF plan.blocks_count >= 2
  THEN flag as BOTTLENECK:CRITICAL_PATH
  SUGGEST: Prioritize this plan, consider breaking dependencies

RULE 5: Complexity Spike
  IF plan.lines_changed > (phase.avg_lines * 3)
  THEN flag as BOTTLENECK:COMPLEXITY
  SUGGEST: Split into sub-plans, review scope creep
```

### Output Format

After each phase completion, `/fire-transition` outputs:

```markdown
## Bottleneck Report

### Flagged Plans
| Plan | Flag | Duration | Detail | Suggestion |
|------|------|----------|--------|------------|
| 03.4-05 | SLOW | 18m (avg: 12m) | Frontend + testing | Break integration tests into separate plan |
| 03.4-04 | COMPLEXITY | 380 lines (avg: 120) | Multiple components | Consider splitting UI into sub-plans |

### Phase Health Score
- Speed: 7/10 (2 plans exceeded 1.5x average)
- Quality: 9/10 (all verifications passed first attempt)
- Efficiency: 8/10 (35% skill reuse, 2 new skills discovered)
- Overall: 8/10
```

## Trend Analysis

### What Trends Are Tracked

1. **Duration Trend:** Are plans getting faster or slower over time?
2. **Quality Trend:** Are verification pass rates improving?
3. **Skill Reuse Trend:** Is the skills library being used more effectively?
4. **Blocker Trend:** Are blockers decreasing over time?
5. **Complexity Trend:** Is plan complexity stable or growing?

### Trend Calculation

```
For each metric across last 5 phases:
  values = [phase_N-4, phase_N-3, phase_N-2, phase_N-1, phase_N]
  trend = linear_regression_slope(values)

  IF trend > +10%: "Increasing" (bad for duration/blockers, good for skill reuse)
  IF trend < -10%: "Decreasing" (good for duration/blockers, bad for quality)
  ELSE: "Stable"
```

### Trend Dashboard (in CONSCIENCE.md)

```markdown
## Trends (Last 5 Phases)

| Metric | P3 | P3.1 | P3.2 | P3.3 | P3.4 | Trend |
|--------|-----|------|------|------|------|-------|
| Avg Plan Duration | 11m | 12m | 9m | 10m | 12m | Stable |
| Verification Pass Rate | 100% | 100% | 100% | 100% | 100% | Stable |
| Skill Reuse | 20% | 25% | 30% | 35% | 35% | Improving |
| Blocker Rate | 10% | 5% | 0% | 0% | 0% | Improving |
| Lines/Plan | 150 | 120 | 100 | 180 | 145 | Stable |

Overall Trajectory: POSITIVE (efficiency improving, blockers decreasing)
```

## Integration Points

### Where Metrics Are Collected

1. **RECORD.md frontmatter** — Plan-level metrics (written by executor agent)
2. **CONSCIENCE.md** — Phase-level aggregations (written by transition command)
3. **MILESTONES.md** — Milestone-level summaries (written by complete-milestone)
4. **BLOCKERS.md** — Blocker frequency tracking

### Where Metrics Are Displayed

1. **`/fire-dashboard`** — Visual project health dashboard
2. **`/fire-transition`** — Post-phase bottleneck report
3. **`/fire-analytics`** — Historical trend analysis
4. **CONSCIENCE.md** — Always-visible trend table

### Automated Actions

```
IF blocker_trend == "Increasing" for 3+ phases:
  SUGGEST: "Blocker rate rising. Consider: assumption validation before planning,
            dependency review, breaking phases into smaller chunks."

IF duration_trend == "Increasing" for 3+ phases:
  SUGGEST: "Plans taking longer. Consider: scope reduction, better skill reuse,
            splitting complex plans, more parallel breaths."

IF skill_reuse < 20% for 3+ phases:
  SUGGEST: "Low skill reuse. Consider: /fire-search before implementation,
            adding auto-skill extraction markers, reviewing skills index."
```
