---
description: Display visual project dashboard with status and progress
---

# /fire-dashboard

> Visual CLI dashboard for real-time project status and progress monitoring

---

## Purpose

Display a comprehensive visual dashboard showing project status, phase progress, breath execution, validation status, skills usage, and recent activity. Provides at-a-glance situational awareness for Dominion Flow projects.

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--compact` | No | Single-line status bar for minimal output |
| `--watch` | No | Auto-refresh dashboard every 5 seconds |
| `--json` | No | JSON output for integrations and scripting |
| `--no-color` | No | Disable ANSI colors for plain terminals |

---

## Process

### Step 1: Load Project State

Read current project state from .planning/CONSCIENCE.md and related files.

```bash
# Check for required state files
if [ ! -f ".planning/CONSCIENCE.md" ]; then
  echo "Error: No .planning/CONSCIENCE.md found. Run /fire-1-new first."
  exit 1
fi
```

Read and parse:
- `.planning/CONSCIENCE.md` - Current position, phase, breath, progress
- `.planning/VISION.md` - Milestone and phase definitions
- `.planning/SKILLS-INDEX.md` - Skills applied tracking
- `.planning/phases/*/` - Phase-specific summaries

### Step 2: Compute Metrics

Calculate dashboard metrics:

```
Project Metrics:
- Project name (from PROJECT.md or directory name)
- Milestone (from CONSCIENCE.md)
- Current phase / total phases
- Current breath / total breaths
- Overall progress percentage
- Skills applied count
- Validation status per category
```

### Step 3: Display Dashboard

#### Default Mode (Full Dashboard)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                              POWER ► DASHBOARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

╔══════════════════════════════════════════════════════════════════════════════╗
║                           PROJECT STATUS                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Project:    my-project                  Milestone: v1.0                   ║
║  Phase:      3 of 9 (Pattern Computation)  Status:    ◆ Executing            ║
║  Started:    2026-01-15                    Last:      2026-01-22 14:32       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE PROGRESS                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Overall:    ████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░ 40%                │
│                                                                             │
│  By Phase:                                                                  │
│  ├─ Phase 1: ████████████████████████████████████████ 100% ✓               │
│  ├─ Phase 2: ████████████████████████████████████████ 100% ✓               │
│  ├─ Phase 3: ██████████████████░░░░░░░░░░░░░░░░░░░░░░  45% ◆               │
│  ├─ Phase 4: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% ○               │
│  └─ ...                                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────┬────────────────────────────────────────┐
│ BREATH EXECUTION                     │ VALIDATION STATUS                       │
├────────────────────────────────────┼────────────────────────────────────────┤
│                                    │                                        │
│  Breath 1: ✓ Complete (3 plans)     │  Code Quality    ████████████████ ✓    │
│  Breath 2: ✓ Complete (2 plans)     │  Testing         ████████████████ ✓    │
│  Breath 3: ◆ In Progress (2 plans)  │  Security        ████████████████ ✓    │
│  Breath 4: ○ Pending (1 plan)       │  Performance     ████████████░░░░ ⏳   │
│                                    │  Documentation   ████████████████ ✓    │
│  Current: Plan 03-05               │                                        │
│  Agent: fire-executor             │  Score: 65/70 (93%)                    │
│                                    │                                        │
└────────────────────────────────────┴────────────────────────────────────────┘

┌────────────────────────────────────┬────────────────────────────────────────┐
│ SKILLS APPLIED                     │ RECENT ACTIVITY                         │
├────────────────────────────────────┼────────────────────────────────────────┤
│                                    │                                        │
│  Total: 12 skills                  │  14:32  Plan 03-05 started            │
│                                    │  14:15  Skill: api-patterns/pagination │
│  Top Skills:                       │  13:45  Breath 2 verification passed     │
│  ├─ n-plus-1          (5x)        │  13:30  Plan 03-04 completed           │
│  ├─ input-validation  (4x)        │  12:15  Plan 03-03 completed           │
│  └─ pagination        (3x)        │  11:00  Breath 1 verification passed     │
│                                    │                                        │
│  Categories:                       │  Commits today: 8                      │
│  ├─ database-solutions (5)        │  Files changed: 24                     │
│  ├─ security          (4)         │  Lines added: 1,847                    │
│  └─ api-patterns      (3)         │                                        │
│                                    │                                        │
└────────────────────────────────────┴────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ NEXT UP                                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  → Complete Plan 03-05 (Heptadic Timeline)                                  │
│  → Execute Breath 4: Plan 03-06 (Pattern Export)                              │
│  → Run /fire-4-verify 3 when complete                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

╠══════════════════════════════════════════════════════════════════════════════╣
║ Commands: [1] Plans  [2] Execute  [3] Skills  [4] Verify  [5] Handoff  [q]   ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

#### Compact Mode (`--compact`)

Single-line status bar for minimal footprint:

```
⚡ my-project | Phase 3/9 | Breath 3/4 | ████████░░ 40% | Skills: 12 | ✓65/70
```

Format: `⚡ {project} | Phase {N}/{M} | Breath {W}/{T} | {progress_bar} {pct}% | Skills: {count} | {validation}`

#### Watch Mode (`--watch`)

Auto-refresh every 5 seconds with clear screen:

```bash
# Watch mode loop
while true; do
  clear
  # Display full dashboard
  echo "[Auto-refresh: 5s | Press Ctrl+C to exit]"
  sleep 5
done
```

Shows timestamp and refresh indicator:

```
━━━ POWER ► DASHBOARD ━━━  [Last refresh: 14:32:15 | Next: 5s]
```

#### JSON Mode (`--json`)

Machine-readable output for integrations:

```json
{
  "project": {
    "name": "my-project",
    "milestone": "v1.0",
    "status": "executing"
  },
  "progress": {
    "overall_percent": 40,
    "current_phase": 3,
    "total_phases": 9,
    "current_wave": 3,
    "total_breaths": 4
  },
  "phases": [
    {"id": 1, "name": "Setup", "status": "complete", "percent": 100},
    {"id": 2, "name": "Typology", "status": "complete", "percent": 100},
    {"id": 3, "name": "Patterns", "status": "in_progress", "percent": 45}
  ],
  "breaths": [
    {"id": 1, "status": "complete", "plans": 3},
    {"id": 2, "status": "complete", "plans": 2},
    {"id": 3, "status": "in_progress", "plans": 2},
    {"id": 4, "status": "pending", "plans": 1}
  ],
  "validation": {
    "score": 56,
    "total": 60,
    "percent": 93,
    "categories": {
      "code_quality": {"status": "pass", "score": 6, "total": 6},
      "testing": {"status": "pass", "score": 5, "total": 5},
      "security": {"status": "pass", "score": 8, "total": 8},
      "performance": {"status": "partial", "score": 5, "total": 6},
      "documentation": {"status": "pass", "score": 4, "total": 4}
    }
  },
  "skills": {
    "total_applied": 12,
    "top_skills": [
      {"name": "n-plus-1", "count": 5},
      {"name": "input-validation", "count": 4},
      {"name": "pagination", "count": 3}
    ],
    "categories": {
      "database-solutions": 5,
      "security": 4,
      "api-patterns": 3
    }
  },
  "recent_activity": [
    {"time": "14:32", "event": "Plan 03-05 started"},
    {"time": "14:15", "event": "Skill applied: api-patterns/pagination"},
    {"time": "13:45", "event": "Breath 2 verification passed"}
  ],
  "timestamp": "2026-01-22T14:32:15Z"
}
```

---

## ASCII Components Reference

### Box Characters Used

| Character | Name | Usage |
|-----------|------|-------|
| `╔ ╗ ╚ ╝` | Double corners | Checkpoint/important boxes |
| `╠ ╣ ═ ║` | Double lines | Major separators |
| `┌ ┐ └ ┘` | Single corners | Standard boxes |
| `├ ┤ ─ │` | Single lines | Tree structures, dividers |
| `━` | Heavy horizontal | Stage banners |

### Status Symbols

| Symbol | Meaning |
|--------|---------|
| `✓` | Complete/Success |
| `✗` | Failed/Error |
| `◆` | In Progress |
| `○` | Pending |
| `⚡` | Active/Running |
| `⏳` | Waiting/Partial |

### Progress Bar Characters

| Character | Usage |
|-----------|-------|
| `█` | Filled progress |
| `░` | Empty progress |

---

## State Reading Logic

### Parse CONSCIENCE.md

```markdown
Extract from CONSCIENCE.md:
- Project Reference → project name, core value
- Current Position → phase, breath, status, progress
- WARRIOR Integration → skills applied, validation status
- Performance Metrics → time estimates, completion rates
```

### Calculate Overall Progress

```
overall_progress = (completed_phases / total_phases) * 100

For current phase:
phase_progress = (completed_plans / total_plans_in_phase) * 100
```

### Determine Validation Status

Read from most recent VERIFICATION.md or compute from validation-config.yml results:

```
Categories:
- Code Quality: TypeScript, ESLint, Prettier
- Testing: Unit, Integration, Coverage
- Security: Audit, Secrets, SAST
- Performance: Bundle, Load time
- Documentation: Comments, API docs
```

---

## Error Handling

### No Project Initialized

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ ✗ ERROR: No Dominion Flow Project Found                                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Could not find .planning/CONSCIENCE.md in current directory.                    ║
║                                                                              ║
║  To initialize a new project:                                               ║
║    /fire-1-new                                                             ║
║                                                                              ║
║  To resume an existing project:                                             ║
║    /fire-6-resume                                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Corrupted State

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ⚠ WARNING: State file may be corrupted                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  .planning/CONSCIENCE.md exists but could not be parsed.                        │
│                                                                             │
│  Showing available data. Some fields may be incomplete.                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Integration Points

- **CONSCIENCE.md**: Primary source of project state
- **VISION.md**: Phase and milestone definitions
- **SKILLS-INDEX.md**: Skills usage tracking
- **VERIFICATION.md**: Validation scores
- **Git**: Recent commits and file changes

---

## Success Criteria

- [ ] Dashboard displays without errors when CONSCIENCE.md exists
- [ ] All four modes work correctly (default, compact, watch, json)
- [ ] Progress bars accurately reflect project state
- [ ] Validation status shows correct category scores
- [ ] Skills section shows accurate counts and top skills
- [ ] Recent activity shows last 5-10 events
- [ ] Box-drawing characters render correctly on target terminal
- [ ] JSON output is valid and parseable

---

## Related Commands

- `/fire-analytics` - Detailed skills usage analytics
- `/fire-discover` - AI pattern discovery
- `/fire-4-verify` - Run validation checks
- `/fire-6-resume` - Resume from handoff

---

*Dashboard provides at-a-glance project status. Run /fire-dashboard --watch for continuous monitoring.*
