---
name: ordered-detector-pipeline-graceful-fallback
category: patterns-standards
version: 1.0.0
contributed: 2026-02-17
contributor: my-other-project
last_updated: 2026-02-17
contributors:
  - my-other-project
tags: [detection, pipeline, graceful-degradation, postgresql, try-catch, incremental-rollout, milestone, feature-flags]
difficulty: medium
usage_count: 1
success_rate: 100
---

# Ordered Detector Pipeline with Graceful Fallback

## Problem

You need to detect multiple conditions (milestones, achievements, alerts, etc.) by querying **different database tables** — but some tables may not exist yet because they belong to future phases that haven't shipped. A single missing table would crash the entire detection system.

### Why It Was Hard

- Standard approaches (one big JOIN, CTE chain) fail if **any** table is missing
- Feature-flag systems add complexity and state management overhead
- Incremental rollouts mean tables arrive over time (Phase 18 ships before Phase 19)
- Detectors have **different priorities** — the most impressive milestone should surface first
- Need cooldown, deduplication, and conversion tracking alongside detection
- Must work with zero configuration changes when new tables appear later

### Impact

Without this pattern, adding a milestone detector that references a not-yet-created table (`user_progress`) would crash the entire `/api/milestones/check` endpoint, preventing all milestone celebrations — even for tables that DO exist.

---

## Solution Pattern

**Ordered Detector Array** — define detectors as an array of `{ type, detect }` objects sorted by priority. Each `detect` function runs its own SQL query inside its own `try/catch`. If the table doesn't exist or the query fails, it returns `null` gracefully. The pipeline iterates until it finds a match.

### Root Cause

The problem occurs because:
1. SQL JOINs across non-existent tables throw fatal errors
2. A single `try/catch` around multiple queries loses granularity
3. Priority ordering requires sequential evaluation (can't parallelize)

### Architecture

```
                    checkMilestones(userId)
                           │
                    ┌──────▼──────┐
                    │ canShow?     │  ← 24h cooldown check
                    │ (cooldown)   │
                    └──────┬──────┘
                           │ yes
              ┌────────────▼────────────────┐
              │  MILESTONE_DETECTORS array   │
              │  (ordered by impressiveness) │
              └────────────┬────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                   ▼
  ┌───────────┐    ┌───────────┐      ┌───────────┐
  │ Detector 1│    │ Detector 2│ ...  │ Detector N│
  │ try/catch │    │ try/catch │      │ try/catch │
  │ → null ok │    │ → null ok │      │ → null ok │
  └─────┬─────┘    └─────┬─────┘      └─────┬─────┘
        │                │                    │
        ▼                ▼                    ▼
   {data,context}     null              {data,context}
        │                                     │
        ▼                                     │
  alreadyCelebrated? ─── yes ─── skip ────────┘
        │ no                                  │
        ▼                                     ▼
  getCelebrationConfig ──── inactive ─── continue
        │ active
        ▼
  recordCelebration → return milestone
```

### How to Fix / Implement

**Step 1: Define the detector array with priority ordering**

```javascript
// Ordered by "impressiveness" — most meaningful surfaces first
const MILESTONE_DETECTORS = [
  { type: 'learning_path_complete', detect: detectLearningPathComplete },
  { type: 'lesson_100',            detect: detectLesson100 },
  { type: 'certificate_earned',    detect: detectCertificateEarned },
  { type: 'first_course_complete', detect: detectFirstCourseComplete },
  { type: 'streak_7_days',         detect: detectStreak7 },  // table from Phase 19
];
```

**Step 2: Each detector is an independent function with its own try/catch**

```javascript
// This table exists now (Phase 15) — works immediately
async function detectFirstCourseComplete(userId) {
  try {
    const [row] = await sql`
      SELECT ep.course_id, c.title AS course_title
      FROM enrollment_progress ep
      JOIN courses c ON c.id = ep.course_id
      WHERE ep.user_id = ${userId}
        AND (ep.progress_percentage >= 100 OR ep.status = 'completed')
      ORDER BY ep.updated_at ASC
      LIMIT 1
    `;
    if (!row) return null;
    return {
      data: { course_id: row.course_id },      // for deduplication
      context: row.course_title,                 // human-readable
    };
  } catch { return null; }  // table missing or query error → skip
}

// This table doesn't exist yet (Phase 19) — gracefully returns null
async function detectStreak7(userId) {
  try {
    const [row] = await sql`
      SELECT current_streak FROM user_progress
      WHERE user_id = ${userId} AND current_streak >= 7
    `;
    if (!row) return null;
    return {
      data: { streak: row.current_streak },
      context: `${row.current_streak}-day streak`,
    };
  } catch {
    // user_progress table may not exist yet (Phase 19 creates it)
    return null;
  }
}
```

**Step 3: Pipeline iterates, deduplicates, and respects cooldown**

```javascript
static async checkMilestones(userId) {
  // Cooldown: max 1 celebration per 24 hours
  const canShow = await canShowCelebration(userId);
  if (!canShow) return null;

  for (const { type, detect } of MILESTONE_DETECTORS) {
    const result = await detect(userId);
    if (result) {
      // Check if already celebrated this exact achievement
      const alreadyShown = await alreadyCelebrated(userId, type, result.data);
      if (!alreadyShown) {
        // Check if this milestone type is active (admin toggle)
        const config = await getCelebrationConfig(type);
        if (!config || !config.is_active) continue;

        // Record and return
        const celebration = await recordCelebration(userId, type, result.data);
        return {
          id: celebration.id,
          milestoneType: type,
          config,
          context: result.context,
        };
      }
    }
  }
  return null;
}
```

**Step 4: Deduplication via JSONB comparison**

```sql
-- Each detector returns { data } which becomes milestone_data
-- UNIQUE constraint prevents duplicate celebrations
UNIQUE(user_id, milestone_type, milestone_data)

-- Check uses JSONB cast for exact comparison
SELECT 1 FROM milestone_celebrations
WHERE user_id = $1
  AND milestone_type = $2
  AND milestone_data = $3::jsonb
LIMIT 1
```

**Step 5: Cooldown via SQL interval**

```sql
-- No celebration shown in last 24 hours
SELECT 1 FROM milestone_celebrations
WHERE user_id = $1
  AND shown_at > now() - interval '24 hours'
LIMIT 1
```

---

## Key Design Decisions

| Decision | Why |
|----------|-----|
| Per-detector try/catch (not global) | Missing table X doesn't block table Y detection |
| Priority ordering (array, not parallel) | Most impressive milestone surfaces first |
| Each detector returns `{ data, context }` | `data` for dedup, `context` for UI display |
| Cooldown at pipeline level (not detector) | One celebration per 24h regardless of type |
| Config-driven messages | Admin can customize per milestone type without code changes |
| ON CONFLICT upsert for recording | Idempotent — re-showing updates `shown_at` |

---

## Database Schema (Supporting Infrastructure)

```sql
-- Admin-configurable celebration messages
CREATE TABLE milestone_configs (
  milestone_type VARCHAR(50) PRIMARY KEY,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  emoji VARCHAR(10) DEFAULT '🎉',
  suggested_amounts JSONB DEFAULT '[10, 25, 50]',
  is_active BOOLEAN DEFAULT true,
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Tracks shown/dismissed/converted celebrations per user
CREATE TABLE milestone_celebrations (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES profiles(id),
  milestone_type VARCHAR(50) REFERENCES milestone_configs(milestone_type),
  milestone_data JSONB DEFAULT '{}',
  shown_at TIMESTAMPTZ DEFAULT now(),
  dismissed_at TIMESTAMPTZ,
  converted BOOLEAN DEFAULT false,
  converted_at TIMESTAMPTZ,
  donation_amount NUMERIC(10,2) DEFAULT 0,
  UNIQUE(user_id, milestone_type, milestone_data)
);

-- Partial index for analytics queries
CREATE INDEX idx_celebrations_converted
  ON milestone_celebrations(milestone_type) WHERE converted = true;
```

---

## Testing the Pattern

### Verify Graceful Fallback
```sql
-- Drop a table that a detector references
DROP TABLE IF EXISTS user_progress;

-- Call the endpoint — should NOT crash, just skip that detector
GET /api/milestones/check
-- Expected: returns milestone from another detector or null
```

### Verify Priority Ordering
```sql
-- Give user both a completed course AND a certificate
-- The certificate detector has higher priority
-- Expected: certificate milestone returned, not course completion
```

### Verify Cooldown
```sql
-- Trigger a celebration, then call check again within 24h
-- Expected: null (cooldown active)
```

### Verify Deduplication
```sql
-- Complete the same course twice
-- Expected: celebration shown only once (UNIQUE constraint)
```

---

## When to Use

- Building achievement/milestone detection across multiple feature phases
- Any detection pipeline where data sources ship incrementally
- Multi-table aggregation where some tables are optional
- Feature rollouts where backend tables appear in different sprints
- Gamification systems (badges, streaks, levels) built across phases
- Alert/notification systems checking diverse conditions

## When NOT to Use

- All data sources exist and are guaranteed present (just use a JOIN)
- Single-table detection (overkill — just write a simple query)
- Real-time streaming events (use an event bus, not polling)
- Detection order doesn't matter (use `Promise.allSettled` instead)

## Common Mistakes

- Wrapping ALL detectors in one `try/catch` — defeats the purpose, one failure kills all
- Running detectors in parallel — breaks priority ordering (highest first matters)
- Forgetting to return `null` in the catch — undefined bubbles up as truthy
- Using `SELECT *` in detectors — return only what's needed for dedup and display
- Skipping cooldown — users get spammed with celebrations on every page load
- Hardcoding celebration messages — use a config table so admins can customize

---

## Related Skills

- [ERROR_RESILIENCE_IMPLEMENTATION.md](./ERROR_RESILIENCE_IMPLEMENTATION.md) - Database trigger error handling
- [CONDITIONAL_SQL_MIGRATION_PATTERN.md](../database-solutions/CONDITIONAL_SQL_MIGRATION_PATTERN.md) - Idempotent migrations
- [GAMIFICATION_SYSTEM.md](../advanced-features/GAMIFICATION_SYSTEM.md) - Points, badges, achievements

## References

- Phase 18 — Milestone Giving (Harvest Offering) implementation
- postgres.js tagged template literals: https://github.com/porsager/postgres
- PostgreSQL JSONB comparison: https://www.postgresql.org/docs/current/datatype-json.html

## Time to Implement

**2-3 hours** for full pipeline (detectors + config table + cooldown + deduplication + conversion tracking)
**30 minutes** to add a new detector to an existing pipeline

## Difficulty Level

⭐⭐⭐ (3/5) - Conceptually simple, but requires discipline: every detector MUST be isolated, return format MUST be consistent, and the pipeline MUST handle all edge cases (missing tables, cooldown, dedup).

---

**Author Notes:**
The key insight is treating each detector as a **completely independent unit** that can fail without affecting others. This is the database equivalent of microservice isolation — but within a single service. The pattern scales beautifully: adding Phase 19's streak detector required zero changes to existing code, just appending to the array. When the `user_progress` table appears, the detector automatically starts working.
