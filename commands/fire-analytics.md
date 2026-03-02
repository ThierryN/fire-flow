---
description: View skills usage analytics and effectiveness metrics
---

# /fire-analytics

> Skills usage analytics with effectiveness metrics and learning insights

---

## Purpose

Analyze skills library usage patterns across the project. Shows which skills have been applied, their effectiveness, time savings, success rates, and identifies gaps in the skills repertoire. Helps optimize skill selection for future phases.

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--category [name]` | No | Filter to specific category (e.g., `database-solutions`) |
| `--time-saved` | No | Focus on time savings report |
| `--gaps` | No | Identify missing skills and recommendations |
| `--period [days]` | No | Limit analysis to last N days (default: all time) |
| `--export [format]` | No | Export report as `md`, `json`, or `csv` |

---

## Process

### Step 1: Load Analytics Data

Read skills usage data from project state files.

```bash
# Required files
SKILLS_INDEX=".planning/SKILLS-INDEX.md"
STATE_FILE=".planning/CONSCIENCE.md"
SUMMARIES=".planning/phases/*/RECORD.md"

if [ ! -f "$SKILLS_INDEX" ]; then
  echo "No skills data found. Run /fire-search or /fire-3-execute first."
  exit 1
fi
```

Parse:
- `.planning/SKILLS-INDEX.md` - Skills applied per phase/plan
- `.planning/CONSCIENCE.md` - Analytics section with usage stats
- `.planning/phases/*/RECORD.md` - Skills applied per execution
- Git history - Time between commits for duration estimates

### Step 2: Compute Analytics

Calculate usage statistics and effectiveness metrics:

```
Usage Statistics:
- Skills by usage count (descending)
- Category distribution
- Skills per phase average
- Unique skills count

Effectiveness Metrics:
- Time saved estimates (based on skill complexity ratings)
- Success rate (skills that led to passing verification)
- Impact score (performance improvements, bug prevention)

Learning Insights:
- Patterns in skill usage
- Skills that tend to be used together
- Gaps based on phase requirements vs available skills
```

### Step 3: Display Analytics

#### Default Mode (Full Analytics)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                            POWER ► ANALYTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

╔══════════════════════════════════════════════════════════════════════════════╗
║                           USAGE SUMMARY                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Total Skills Applied:    12                 Unique Skills:     8           ║
║  Categories Used:         4                  Avg Skills/Phase:  3.0         ║
║  Time Period:             2026-01-15 to 2026-01-22 (7 days)                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ SKILLS BY USAGE COUNT                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Rank  Skill                           Category              Count  Bar    │
│  ────  ──────────────────────────────  ──────────────────    ─────  ───    │
│   1    n-plus-1                        database-solutions      5   █████   │
│   2    input-validation                security                4   ████    │
│   3    pagination                      api-patterns            3   ███     │
│   4    jwt-authentication              security                2   ██      │
│   5    indexing                        database-solutions      2   ██      │
│   6    rate-limiting                   api-patterns            1   █       │
│   7    connection-pooling              database-solutions      1   █       │
│   8    error-boundary                  frontend                1   █       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ CATEGORY DISTRIBUTION                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  database-solutions    ████████████████████████░░░░░░░░░░░░░░░░  8  (40%)  │
│  security              ████████████████░░░░░░░░░░░░░░░░░░░░░░░░  6  (30%)  │
│  api-patterns          ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  4  (20%)  │
│  frontend              ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  2  (10%)  │
│                                                                             │
│  Not Used: testing (0), performance (0), infrastructure (0)                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ TIME SAVED ESTIMATES                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Skill                        Base Time    Actual    Saved    % Saved      │
│  ────────────────────────────  ─────────   ──────    ─────    ───────      │
│  n-plus-1 (5x)                  4h 10m      50m     3h 20m      80%        │
│  input-validation (4x)          2h 00m      30m     1h 30m      75%        │
│  jwt-authentication (2x)        3h 00m      45m     2h 15m      75%        │
│  pagination (3x)                1h 30m      20m     1h 10m      78%        │
│  indexing (2x)                  1h 00m      15m       45m       75%        │
│  ────────────────────────────  ─────────   ──────    ─────    ───────      │
│  TOTAL                         11h 40m    2h 40m    9h 00m      77%        │
│                                                                             │
│  * Estimates based on skill complexity ratings and industry benchmarks     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ EFFECTIVENESS METRICS                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ MOST EFFECTIVE SKILL                                               │    │
│  │                                                                     │    │
│  │   n-plus-1 (database-solutions)                                    │    │
│  │   ├─ Used: 5 times across 3 phases                                 │    │
│  │   ├─ Impact: 83% average query performance improvement            │    │
│  │   ├─ Success Rate: 100% (all verifications passed)                │    │
│  │   └─ Time Saved: 3h 20m total                                      │    │
│  │                                                                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ MOST USED CATEGORY                                                 │    │
│  │                                                                     │    │
│  │   database-solutions                                               │    │
│  │   ├─ Skills Applied: 8 (40% of all applications)                  │    │
│  │   ├─ Unique Skills: 3 (n-plus-1, indexing, connection-pooling)    │    │
│  │   ├─ Phases Touched: 3 of 4 completed phases                      │    │
│  │   └─ Avg Impact: High (database queries optimized)                │    │
│  │                                                                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Success Rates by Category:                                                │
│  ├─ database-solutions:  100% ████████████████████                        │
│  ├─ security:            100% ████████████████████                        │
│  ├─ api-patterns:         95% ███████████████████░                        │
│  └─ frontend:             90% ██████████████████░░                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ LEARNING INSIGHTS                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Patterns Detected:                                                        │
│  ├─ Skills n-plus-1 and indexing often used together (80% co-occurrence) │
│  ├─ security skills applied early in phases (good practice!)             │
│  └─ frontend skills underutilized relative to project scope              │
│                                                                             │
│  Recommendations:                                                          │
│  ├─ Consider bundling n-plus-1 + indexing as compound skill              │
│  ├─ Explore testing skills (0 applications - potential gap)              │
│  └─ Review performance skills for upcoming optimization phases           │
│                                                                             │
│  Trend: Skills usage increasing 25% per phase (knowledge compounding)     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Category Mode (`--category database-solutions`)

```
━━━ POWER ► ANALYTICS: database-solutions ━━━

╔══════════════════════════════════════════════════════════════════════════════╗
║                    CATEGORY: database-solutions                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Total Applications:  8              Available Skills:  15                  ║
║  Unique Skills Used:  3              Usage Rate:        20%                 ║
║  Success Rate:        100%           Time Saved:        5h 05m              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ SKILLS IN THIS CATEGORY                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USED:                                                                      │
│  ├─ n-plus-1            5x  ████████████████████  Phase 2, 3              │
│  ├─ indexing            2x  ████████              Phase 2                  │
│  └─ connection-pooling  1x  ████                  Phase 3                  │
│                                                                             │
│  AVAILABLE (not yet used):                                                 │
│  ├─ query-optimization       - Optimize slow queries with EXPLAIN          │
│  ├─ denormalization          - Strategic data duplication                  │
│  ├─ migrations               - Safe database migration patterns            │
│  ├─ transactions             - ACID transaction handling                   │
│  ├─ deadlock-prevention      - Avoid database deadlocks                    │
│  ├─ sharding                 - Horizontal partitioning                     │
│  ├─ replication              - Read replicas setup                         │
│  ├─ backup-strategies        - Automated backup patterns                   │
│  ├─ schema-versioning        - Database schema evolution                   │
│  ├─ soft-deletes             - Logical deletion patterns                   │
│  ├─ audit-logging            - Change tracking                             │
│  └─ connection-retry         - Resilient connection handling               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ USAGE TIMELINE                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 2: ████ n-plus-1, indexing, indexing                                │
│  Phase 3: ████████ n-plus-1, n-plus-1, n-plus-1, n-plus-1, conn-pooling   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Time Saved Mode (`--time-saved`)

```
━━━ POWER ► ANALYTICS: TIME SAVINGS REPORT ━━━

╔══════════════════════════════════════════════════════════════════════════════╗
║                         TIME SAVINGS SUMMARY                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Total Time Saved:      9h 00m                                              ║
║  Without Skills:       11h 40m (estimated)                                  ║
║  With Skills:           2h 40m (actual)                                     ║
║  Efficiency Gain:       77%                                                 ║
║                                                                              ║
║  ████████████████████████████████████████████████████████████░░░░░░░░░░░░░  ║
║  │◄─────────────── 9h saved ───────────────►│◄── 2h 40m ──►│               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ SAVINGS BY SKILL (Sorted by Time Saved)                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   #  Skill                  Uses   Base Time   Actual   Saved    Impact    │
│  ──  ────────────────────   ────   ─────────   ──────   ──────   ──────    │
│   1  n-plus-1                 5      4h 10m     50m    3h 20m    HIGH      │
│   2  jwt-authentication       2      3h 00m     45m    2h 15m    HIGH      │
│   3  input-validation         4      2h 00m     30m    1h 30m    MEDIUM    │
│   4  pagination               3      1h 30m     20m    1h 10m    MEDIUM    │
│   5  indexing                 2      1h 00m     15m      45m     MEDIUM    │
│   6  rate-limiting            1        30m      10m      20m     LOW       │
│   7  connection-pooling       1        20m       5m      15m     LOW       │
│   8  error-boundary           1        10m       5m       5m     LOW       │
│                                                                             │
│  Note: Base time estimated from skill complexity and industry benchmarks   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ SAVINGS BY CATEGORY                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  database-solutions  ████████████████████████████████░░░░░░  4h 20m  (48%) │
│  security            ██████████████████████░░░░░░░░░░░░░░░░  3h 45m  (42%) │
│  api-patterns        ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    50m   (9%) │
│  frontend            █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░     5m   (1%) │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PROJECTED SAVINGS (Remaining Phases)                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  If current skill usage patterns continue:                                 │
│                                                                             │
│  Remaining phases: 6                                                       │
│  Expected skill applications: ~18                                          │
│  Projected additional savings: ~13h 30m                                    │
│  Total project savings: ~22h 30m                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Gaps Mode (`--gaps`)

```
━━━ POWER ► ANALYTICS: SKILLS GAP ANALYSIS ━━━

╔══════════════════════════════════════════════════════════════════════════════╗
║                         SKILLS GAP DETECTION                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Categories with Zero Usage:  3                                             ║
║  Underutilized Categories:    2                                             ║
║  Potential Missing Skills:    5                                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ UNUSED CATEGORIES                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✗ testing (0 skills used)                                                 │
│    └─ Available: unit-testing, integration-testing, mocking,               │
│       snapshot-testing, e2e-testing, coverage-analysis                     │
│    └─ Recommendation: HIGH PRIORITY - Add testing skills in Phase 4       │
│                                                                             │
│  ✗ performance (0 skills used)                                             │
│    └─ Available: caching, bundle-optimization, lazy-loading,               │
│       code-splitting, image-optimization, cdn-configuration               │
│    └─ Recommendation: MEDIUM - Consider for optimization phase            │
│                                                                             │
│  ✗ infrastructure (0 skills used)                                          │
│    └─ Available: docker-compose, kubernetes, ci-cd-pipelines,              │
│       environment-management, secrets-management, monitoring              │
│    └─ Recommendation: LOW - May not be needed for current scope           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ UNDERUTILIZED CATEGORIES                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ⚠ frontend (1 skill used, 12 available)                                   │
│    └─ Used: error-boundary                                                 │
│    └─ Consider: react-memo, state-management, form-validation,             │
│       accessibility, responsive-design                                     │
│    └─ Usage Rate: 8% (below 20% threshold)                                │
│                                                                             │
│  ⚠ api-patterns (3 skills used, 10 available)                              │
│    └─ Used: pagination, rate-limiting, [unknown]                           │
│    └─ Consider: error-handling, versioning, caching-headers,               │
│       documentation, retry-patterns                                        │
│    └─ Usage Rate: 30% (acceptable but could improve)                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ POTENTIAL MISSING SKILLS                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Based on project patterns and common needs:                               │
│                                                                             │
│  1. GraphQL patterns (no skills exist)                                     │
│     └─ Detected: GraphQL queries in codebase                               │
│     └─ Action: /fire-contribute to add GraphQL skills                    │
│                                                                             │
│  2. WebSocket handling (no skills exist)                                   │
│     └─ Detected: Real-time features planned                                │
│     └─ Action: /fire-contribute or search external sources               │
│                                                                             │
│  3. Bible/Theological domain (no skills exist)                             │
│     └─ Detected: Domain-specific patterns in codebase                      │
│     └─ Action: Create project-specific skills category                    │
│                                                                             │
│  4. TypeScript strict patterns (no skills exist)                           │
│     └─ Detected: Frequent type errors in verification                      │
│     └─ Action: Consider adding typescript-patterns category               │
│                                                                             │
│  5. Prisma optimization (beyond n-plus-1)                                  │
│     └─ Detected: Prisma-specific patterns recurring                        │
│     └─ Action: Extend database-solutions with Prisma skills               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ RECOMMENDATIONS                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Priority Actions:                                                         │
│                                                                             │
│  [1] HIGH: Add testing skills before Phase 4                               │
│      Run: /fire-search "testing" to explore available skills             │
│                                                                             │
│  [2] MEDIUM: Create GraphQL skills from current patterns                   │
│      Run: /fire-contribute after completing GraphQL work                 │
│                                                                             │
│  [3] LOW: Consider performance skills for optimization phase               │
│      Run: /fire-search "performance caching" when ready                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Time Estimation Logic

Skills have complexity ratings that estimate time saved:

| Complexity | Base Time | With Skill | Saved | Examples |
|------------|-----------|------------|-------|----------|
| LOW | 10-30m | 5-10m | 50-65% | error-boundary, logging |
| MEDIUM | 30m-1h | 10-20m | 65-75% | pagination, validation |
| HIGH | 1-2h | 15-30m | 75-85% | auth, n-plus-1 |
| VERY_HIGH | 2-4h | 30-60m | 75-85% | full auth flow, caching layer |

Formula:
```
time_saved = (base_time * usage_count) - (actual_time * usage_count)
```

---

## Export Formats

### Markdown (`--export md`)

Generates a full report in `.planning/analytics/YYYY-MM-DD-analytics.md`

### JSON (`--export json`)

```json
{
  "summary": {
    "total_skills_applied": 12,
    "unique_skills": 8,
    "categories_used": 4,
    "time_period": {
      "start": "2026-01-15",
      "end": "2026-01-22"
    }
  },
  "skills": [
    {"name": "n-plus-1", "category": "database-solutions", "count": 5, "time_saved_minutes": 200}
  ],
  "categories": {
    "database-solutions": {"count": 8, "percent": 40},
    "security": {"count": 6, "percent": 30}
  },
  "time_savings": {
    "total_saved_minutes": 540,
    "efficiency_gain_percent": 77
  },
  "gaps": {
    "unused_categories": ["testing", "performance", "infrastructure"],
    "underutilized": ["frontend", "api-patterns"],
    "missing_skills": ["graphql", "websocket"]
  },
  "generated_at": "2026-01-22T14:45:00Z"
}
```

### CSV (`--export csv`)

```csv
skill,category,count,time_saved_minutes,success_rate
n-plus-1,database-solutions,5,200,100
input-validation,security,4,90,100
pagination,api-patterns,3,70,95
```

---

## Success Criteria

- [ ] Analytics display without errors when SKILLS-INDEX.md exists
- [ ] All modes work correctly (default, category, time-saved, gaps)
- [ ] Time saved estimates are reasonable and documented
- [ ] Category distribution percentages sum to 100%
- [ ] Gaps detection identifies unused and underutilized categories
- [ ] Recommendations are actionable and reference correct commands
- [ ] Export formats generate valid files

---

## Related Commands

- `/fire-dashboard` - Visual project status
- `/fire-discover` - AI pattern discovery
- `/fire-search` - Search skills library
- `/fire-contribute` - Add new skills

---

*Analytics help optimize skill selection. Run /fire-analytics --gaps to identify improvement opportunities.*
