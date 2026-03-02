# Summary Template (Dominion Flow Enhanced)

> **Origin:** Ported from Dominion Flow `summary.md` with metrics collection for trend analysis.

Template for `.planning/phases/XX-name/{phase}-{plan}-RECORD.md`

---

## File Template

```markdown
---
phase: XX-name
plan: NN
subsystem: [primary subsystem]
tags: [tech tags]
requires:
  - [prior phases this builds on]
provides:
  - [what this delivers for future phases]
affects:
  - [future phases that may need to reference this]
tech-stack:
  added: [new dependencies]
  patterns: [new patterns established]
key-files:
  created: [new files]
  modified: [changed files]
key-decisions:
  - [decision: rationale]

# Dominion Flow Metrics (for bottleneck detection + trend analysis)
metrics:
  duration_minutes: [N]
  tasks_completed: [N]
  tasks_blocked: [N]
  files_created: [N]
  files_modified: [N]
  lines_added: [N]
  lines_removed: [N]
  tests_added: [N]
  test_coverage_delta: "[+/-N%]"
  skills_applied: [N]
  honesty_checkpoints: [N]
  commits: [N]
  blocker_count: [N]
  execution_mode: sequential|subagent|swarm
  mode_reason: "[why this mode was selected]"
  agents_spawned: [N]
---

## Quick Summary

[One substantive sentence. Not "completed plan" - what was actually built.]

## Task Commits

| # | Hash | Description | Files |
|---|------|-------------|-------|
| 1 | abc1234 | feat(XX-NN): [task 1] | src/file1.ts, src/file2.ts |
| 2 | def5678 | feat(XX-NN): [task 2] | src/file3.ts |
| 3 | ghi9012 | test(XX-NN): [task 3] | src/__tests__/file.test.ts |

## Deviations from Plan

[If none: "None - executed as planned."]

| Deviation | Rule | Detail |
|-----------|------|--------|
| [what changed] | Rule 1 - Bug | [why] |

## Test Results

| Segment | Tests Run | Passed | Failed | New Tests |
|---------|-----------|--------|--------|-----------|
| 1 | 24 | 24 | 0 | 3 |
| 2 | 27 | 27 | 0 | 3 |

## Decisions Made

- **[Decision]:** [Choice made] — [Rationale]

## Blockers Encountered

- **BLOCKER-XXX [PX]:** [Description] — [Status: Resolved/Open]

## Skills Applied

- [skill-library/category/SKILL_NAME.md] — [how it helped]

## Honesty Checkpoints

- **Gap identified:** [what was uncertain]
- **Research conducted:** [what was looked up]
- **Resolution:** [what was decided]
- **Confidence after research:** [High/Medium/Low]

## Next Step

[More plans in phase? Phase complete? What comes next?]

## Performance

- **Duration:** [N] minutes
- **Started:** [timestamp]
- **Completed:** [timestamp]
- **Tasks:** [completed]/[total]
- **Files:** [created] created, [modified] modified
- **Branch:** feature/phase-XX-description
```

---

## Writing Guidelines

- **Quick Summary:** Substantive. "Built JWT auth with refresh tokens" not "Completed plan 02"
- **Task Commits:** Include actual git hashes for traceability
- **Deviations:** Categorize by Rule (1-Bug, 2-Critical, 3-Blocking, 4-Architectural)
- **Metrics:** Fill accurately - these feed into bottleneck detection and trend analysis
- **Skills Applied:** Reference exact skill file path for future reuse tracking
- **Honesty Checkpoints:** Document any research conducted during execution

---

## Metrics Collection

The `metrics` frontmatter is consumed by:
- `/fire-transition` — aggregates into phase-level metrics in CONSCIENCE.md
- `/fire-analytics` — historical trend analysis
- `/fire-dashboard` — visual project health display
- `references/metrics-and-trends.md` — bottleneck detection algorithm
