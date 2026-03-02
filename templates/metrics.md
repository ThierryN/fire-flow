# Metrics Template

> **Origin:** NEW for Dominion Flow v2.0 - Metrics collection for trend analysis.

Template for metrics frontmatter in RECORD.md files and aggregation in CONSCIENCE.md.

---

## Per-Plan Metrics (in RECORD.md frontmatter)

```yaml
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
```

---

## Per-Phase Metrics (in CONSCIENCE.md)

```markdown
## Phase Metrics
| Phase | Plans | Duration | Avg/Plan | Trend | Bottleneck |
|-------|-------|----------|----------|-------|------------|
| 01    | 3     | 30m      | 10m      | -     | None       |
| 02    | 4     | 45m      | 11m      | +10%  | None       |
| 03    | 6     | 72m      | 12m      | +9%   | Plan 05    |
```

---

## Trend Dashboard (in CONSCIENCE.md)

```markdown
## Trends (Last 5 Phases)
| Metric | P1 | P2 | P3 | P4 | P5 | Trend |
|--------|----|----|----|----|-----|-------|
| Avg Duration | 10m | 11m | 12m | 10m | 11m | Stable |
| Pass Rate | 100% | 100% | 100% | 100% | 100% | Stable |
| Skill Reuse | 20% | 25% | 30% | 35% | 40% | Improving |
| Blocker Rate | 10% | 5% | 0% | 0% | 0% | Improving |

Trajectory: POSITIVE
```

---

## Bottleneck Flags

| Flag | Trigger | Suggestion |
|------|---------|------------|
| SLOW | Duration > 2x average | Break into smaller plans |
| BLOCKED | >20% tasks blocked | Review dependencies |
| QUALITY | Failed verification | Better must-haves |
| CRITICAL_PATH | Blocks 2+ plans | Prioritize this plan |
| COMPLEXITY | Lines > 3x average | Split into sub-plans |
