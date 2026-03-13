# Cross-Table Analytics with Composite Health Scoring

## The Problem

Generic analytics tools (Google Analytics, Mixpanel) track isolated metrics: page views, signups, conversions. But the real insights live in **cross-table correlations** — connecting learning behavior to giving patterns, community engagement to course completion, podcast listening to enrollment. No off-the-shelf tool provides these ministry-specific (or domain-specific) cross-correlations.

### Why It Was Hard

- Querying 10+ tables in parallel without deadlocks or timeout cascading
- Designing a weighted composite score that's meaningful (not just a vanity number)
- Handling missing tables gracefully (tables may not exist if migrations haven't run)
- Period-over-period comparison requires careful date math (current vs previous window)
- Engagement tier classification needs CTE with correlated subqueries per user across multiple tables
- "First ever in this period" milestone queries require `NOT EXISTS` anti-joins
- TIMESTAMP vs TIMESTAMPTZ columns need explicit `::timestamp` casts in community tables
- Frontend SVG gauge without any chart library dependency

### Impact

- Admins get a single "health score" instead of hunting through 5 separate tabs
- Cross-correlations reveal actionable insights (e.g., "community participants complete 40% more courses")
- Engagement tiers enable targeted outreach (wake up dormant users, reward torchbearers)
- Journey milestones track conversion funnel from signup → first lesson → first course → first donation

---

## The Solution

### Architecture Overview

```
GET /api/site-analytics/community-pulse?period=30d

6 Query Groups (individual try/catch, parallel where possible):
1. Health Score Components   → 6 parallel queries → weighted 0-100 score
2. Period-over-Period        → 2 queries (current vs previous) → 7 metrics with deltas
3. Engagement Tiers          → 1 CTE query → classify all users into 4 tiers
4. Cross-Correlations        → 4 parallel queries → intersection percentages
5. Journey Milestones        → 4 parallel queries → "first ever" counts
6. Session Depth             → 1 CTE query → avg pages/session, duration, bounce rate
```

### Key Pattern 1: Resilient Parallel Queries with Graceful Degradation

**Every query group has its own try/catch.** If one table is missing or a query fails, the others still return data.

```javascript
export const getCommunityPulse = async (req, res) => {
  const days = parsePeriodDays(req.query.period);
  const startDate = getStartDate(days);
  const prevStartDate = getStartDate(days * 2);  // Previous period = same length, earlier window
  const errors = [];

  // Each section has independent try/catch
  let healthComponents = { /* defaults */ };
  try {
    const [learning, community, podcast, giving, growthCurrent, growthPrevious] = await Promise.all([
      sql`SELECT ... FROM lesson_progress ...`,
      sql`SELECT ... FROM timeline_posts UNION post_comments UNION post_reactions ...`,
      sql`SELECT ... FROM podcast_plays ...`,
      sql`SELECT ... FROM donations ...`,
      sql`SELECT COUNT(*) FROM profiles WHERE created_at >= ${startDate}`,
      sql`SELECT COUNT(*) FROM profiles WHERE created_at >= ${prevStartDate} AND created_at < ${startDate}`
    ]);
    healthComponents = { /* parsed results */ };
  } catch (e) { errors.push('healthComponents: ' + e.message); }

  // ... more sections, each with own try/catch ...

  res.json({
    success: true,
    data: {
      healthScore, periodComparison, engagementTiers,
      crossCorrelations, milestones, sessionDepth,
      errors: errors.length > 0 ? errors : undefined  // Surface errors for debugging
    }
  });
};
```

**Why this matters:** If `page_views` table doesn't exist yet (migration not run), the session depth section returns zeros but everything else still works. The `errors` array in the response tells the admin what's degraded.

### Key Pattern 2: Weighted Composite Health Score (0-100)

```javascript
// Safe division that caps at 100%
const safeDiv = (a, b) => b > 0 ? Math.min((a / b) * 100, 100) : 0;

// Component scores (each 0-100)
const learningScore = safeDiv(activeLearners, totalEnrolled || totalUsers);
const communityScore = safeDiv(communityParticipants, totalUsers);
const listeningScore = safeDiv(podcastListeners, totalUsers);
const givingScore = safeDiv(donors, totalUsers);

// Growth score: normalized around 50 (no change = 50, decline = <50, growth = >50)
let growthScore = 0;
if (newUsersPrevPeriod > 0) {
  const growthRate = ((newUsersThisPeriod - newUsersPrevPeriod) / newUsersPrevPeriod) * 100;
  growthScore = Math.min(Math.max(growthRate + 50, 0), 100);  // Clamp 0-100
} else if (newUsersThisPeriod > 0) {
  growthScore = 100;  // Infinite growth from zero
}

// Weighted composite
const healthScore = Math.round(
  (learningScore * 0.30) +   // Learning is primary mission
  (communityScore * 0.20) +  // Community engagement
  (listeningScore * 0.15) +  // Content consumption
  (givingScore * 0.15) +     // Financial sustainability
  (growthScore * 0.20)       // Growth trajectory
);
```

**Tuning the weights:** Adjust weights based on organizational priorities. A commerce site might weight giving at 0.30. A social platform might weight community at 0.35.

### Key Pattern 3: Period-over-Period Comparison

Use `prevStartDate = getStartDate(days * 2)` to create two equal-length windows:

```
Timeline:  |---- previous period ----|---- current period ----|
           prevStartDate          startDate               now
```

```javascript
const [currentMetrics, previousMetrics] = await Promise.all([
  sql`SELECT
    (SELECT COUNT(*) FROM profiles WHERE created_at >= ${startDate}) AS new_users,
    (SELECT COUNT(*) FROM enrollments WHERE enrollment_date >= ${startDate}) AS enrollments,
    ...
  `,
  sql`SELECT
    (SELECT COUNT(*) FROM profiles WHERE created_at >= ${prevStartDate} AND created_at < ${startDate}) AS new_users,
    (SELECT COUNT(*) FROM enrollments WHERE enrollment_date >= ${prevStartDate} AND enrollment_date < ${startDate}) AS enrollments,
    ...
  `
]);
```

**Frontend delta calculation:**

```javascript
const DeltaIndicator = ({ current, previous, label, prefix = '', isCurrency = false }) => {
  const delta = previous > 0 ? ((current - previous) / previous) * 100 : (current > 0 ? 100 : 0);
  const isUp = delta > 0;
  const isFlat = delta === 0;
  return (
    <div className="bg-[#0F172A]/70 border border-gray-700/50 rounded-xl p-4">
      <p className="text-gray-400 text-xs uppercase">{label}</p>
      <p className="text-2xl font-bold text-white">{prefix}{displayValue}</p>
      <div className={`text-sm ${isUp ? 'text-emerald-400' : isFlat ? 'text-gray-500' : 'text-rose-400'}`}>
        {isUp ? '+' : ''}{delta.toFixed(1)}% vs prev
      </div>
    </div>
  );
};
```

### Key Pattern 4: Engagement Tier Classification (CTE)

Classify every user into exactly one tier using a CTE with correlated subqueries:

```sql
WITH user_activity AS (
  SELECT
    p.id AS user_id,
    (SELECT COUNT(DISTINCT DATE(pv.created_at))
     FROM page_views pv WHERE pv.user_id = p.id AND pv.created_at >= $startDate
    ) AS active_days,
    (SELECT COUNT(*) FROM lesson_progress lp
     WHERE lp.user_id = p.id AND lp.is_completed = true AND lp.completed_at >= $startDate
    ) AS lessons_completed,
    (SELECT COUNT(*) FROM timeline_posts tp
     WHERE tp.user_id = p.id AND tp.created_at >= $startDate::timestamp AND tp.deleted_at IS NULL
    ) AS community_posts,
    (SELECT COUNT(*) FROM lesson_progress lp
     WHERE lp.user_id = p.id AND lp.last_accessed_at >= $startDate
    ) AS lesson_activity,
    (SELECT COUNT(*) FROM login_history lh
     WHERE lh.user_id = p.id AND lh.login_at >= $startDate AND lh.success = true
    ) AS logins
  FROM profiles p
)
SELECT
  COUNT(*) FILTER (WHERE active_days >= 5
    AND (lessons_completed > 0 OR community_posts > 0)) AS torchbearers,
  COUNT(*) FILTER (WHERE
    (active_days >= 2 OR lesson_activity > 0)
    AND NOT (active_days >= 5 AND (lessons_completed > 0 OR community_posts > 0))
  ) AS seekers,
  COUNT(*) FILTER (WHERE
    (active_days >= 1 OR logins > 0)
    AND NOT (active_days >= 2 OR lesson_activity > 0)
  ) AS visitors,
  COUNT(*) FILTER (WHERE
    active_days = 0 AND logins = 0 AND lesson_activity = 0
  ) AS dormant
FROM user_activity
```

**Tier definitions (mutually exclusive, ordered by priority):**

| Tier | Name | Criteria |
|------|------|----------|
| Power | Torchbearers | 5+ active days AND (completed lessons OR community posts) |
| Active | Seekers | 2+ active days OR some lesson progress (but NOT torchbearer) |
| Casual | Visitors | Logged in or 1+ active day (but NOT seeker+) |
| Inactive | Dormant | No activity, no logins, no lesson access |

**FILTER clause:** PostgreSQL's `COUNT(*) FILTER (WHERE ...)` is more readable and performant than `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`.

### Key Pattern 5: Cross-Correlation Insights

Find users who exist in the **intersection** of two behavior sets:

```sql
-- "Learners Who Give" — active learners who also donated
SELECT
  COUNT(DISTINCT d.user_id) AS learner_donors,
  (SELECT COUNT(DISTINCT user_id) FROM enrollment_progress
   WHERE last_accessed_at >= $startDate) AS total_active_learners
FROM donations d
WHERE d.status = 'completed' AND d.created_at >= $startDate
  AND d.user_id IN (
    SELECT DISTINCT user_id FROM enrollment_progress WHERE last_accessed_at >= $startDate
  )
```

```sql
-- "Community Completion Boost" — do community participants complete more?
WITH community_users AS (
  SELECT DISTINCT user_id FROM (
    SELECT user_id FROM timeline_posts WHERE created_at >= $startDate::timestamp AND deleted_at IS NULL
    UNION
    SELECT user_id FROM post_comments WHERE created_at >= $startDate::timestamp AND deleted_at IS NULL
  ) cu
)
SELECT
  ROUND(AVG(CASE WHEN cu.user_id IS NOT NULL THEN ep.completion_percentage ELSE NULL END), 1) AS with_community,
  ROUND(AVG(CASE WHEN cu.user_id IS NULL THEN ep.completion_percentage ELSE NULL END), 1) AS without_community
FROM enrollment_progress ep
LEFT JOIN community_users cu ON cu.user_id = ep.user_id
WHERE ep.last_accessed_at >= $startDate
```

### Key Pattern 6: "First Ever in Period" Milestones (NOT EXISTS)

Find users who did something for the **first time** within the current period:

```sql
-- Users who completed their FGTAT lesson during this period
SELECT COUNT(DISTINCT lp.user_id) AS cnt
FROM lesson_progress lp
WHERE lp.is_completed = true AND lp.completed_at >= $startDate
  AND NOT EXISTS (
    SELECT 1 FROM lesson_progress lp2
    WHERE lp2.user_id = lp.user_id AND lp2.is_completed = true AND lp2.completed_at < $startDate
  )
```

**Why NOT EXISTS:** This is the canonical SQL anti-join pattern. It says "find users who have activity in the period AND no prior activity before the period." Much cleaner than `LEFT JOIN ... WHERE ... IS NULL` and often faster.

### Key Pattern 7: SVG Circular Gauge (Zero Dependencies)

```jsx
const HealthScoreGauge = ({ score, components }) => {
  const radius = 70, stroke = 10;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 70 ? '#34d399' : score >= 40 ? '#fbbf24' : '#f87171';

  return (
    <svg width="180" height="180" className="mx-auto">
      {/* Background circle */}
      <circle cx="90" cy="90" r={radius} fill="none" stroke="#1e293b" strokeWidth={stroke} />
      {/* Progress arc */}
      <circle cx="90" cy="90" r={radius} fill="none" stroke={color} strokeWidth={stroke}
        strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={offset}
        transform="rotate(-90 90 90)" style={{ transition: 'stroke-dashoffset 1s ease' }} />
      {/* Score text */}
      <text x="90" y="85" textAnchor="middle" fill="white" fontSize="32" fontWeight="bold">
        {score}
      </text>
      <text x="90" y="108" textAnchor="middle" fill="#94a3b8" fontSize="12">
        Health Score
      </text>
    </svg>
  );
};
```

**Why SVG, not a chart library:** It's 20 lines. No bundle size increase. Full control over colors and animation. Works in dark mode.

### Key Pattern 8: Session Depth from Page Views CTE

```sql
WITH session_stats AS (
  SELECT session_id,
    COUNT(*) AS page_count,
    EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) AS duration_seconds
  FROM page_views
  WHERE created_at >= $startDate
  GROUP BY session_id
)
SELECT
  ROUND(AVG(page_count), 1) AS avg_pages,
  ROUND(AVG(duration_seconds), 0) AS avg_duration,
  ROUND((COUNT(*) FILTER (WHERE page_count = 1)::numeric / NULLIF(COUNT(*), 0)) * 100, 1) AS bounce_rate
FROM session_stats
```

**Bounce rate:** Sessions with only 1 page view divided by total sessions. Use `NULLIF` to avoid division by zero.

---

## Frontend Component Structure

```
CommunityPulseTab
  |-- HealthScoreGauge (SVG circle)
  |   |-- Component score bars (5 colored progress bars)
  |-- DeltaIndicator cards grid (7 metrics)
  |-- LazyPieChart donut (engagement tiers)
  |-- Cross-correlation insight cards (4 cards)
  |-- Journey milestone cards (4 cards)
  |-- Session depth cards (3 cards)
```

**Styling pattern (dark admin dashboard):**
```jsx
// Card container
<div className="bg-[#0F172A]/70 border border-gray-700/50 rounded-xl p-5">
  {/* Accent border by type */}
  <div className="border-l-4 border-emerald-500/50 pl-4">
    <p className="text-gray-400 text-xs uppercase tracking-wider">{label}</p>
    <p className="text-2xl font-bold text-white">{value}</p>
  </div>
</div>
```

---

## Testing the Implementation

### Backend Verification
```bash
# Hit the endpoint (requires admin JWT)
curl -H "Authorization: Bearer $TOKEN" \
  "https://yoursite.com/api/site-analytics/community-pulse?period=30d"

# Expected: JSON with healthScore, periodComparison, engagementTiers, etc.
# Check errors array: should list missing tables (page_views, etc.) if migration hasn't run
```

### Frontend Verification
1. Navigate to `/admin/site-analytics?tab=pulse`
2. Health score gauge should show 0-100 with colored ring
3. Period comparison cards should show delta arrows
4. Engagement tier donut chart renders (all "Dormant" is OK if no activity data)
5. No console errors

### Build Verification
```bash
cd client && npm run build
# Must complete with zero errors
```

---

## Prevention & Maintenance

### Adding New Metrics
1. Add new query in its own try/catch block
2. Add default values in the `let` declaration above the try
3. Add to the response `data` object
4. Add frontend card/section in the tab component

### Performance Considerations
- The engagement tier CTE does correlated subqueries per user — can be slow with 10k+ users
- Consider materializing tier classification nightly if user count grows
- `Promise.all` keeps total query time to the longest single query, not the sum

### TIMESTAMP vs TIMESTAMPTZ Gotcha
Community tables (`timeline_posts`, `post_comments`, `post_reactions`) use `TIMESTAMP` (no timezone), while analytics tables (`page_views`, `podcast_plays`) use `TIMESTAMPTZ`. When comparing dates:
```sql
-- For TIMESTAMP columns (community tables), cast the parameter:
WHERE created_at >= ${startDate}::timestamp

-- For TIMESTAMPTZ columns (analytics tables), no cast needed:
WHERE created_at >= ${startDate}
```

---

## Common Mistakes to Avoid

- **Not wrapping each query group in try/catch** — One missing table kills the entire endpoint
- **Using SUM(CASE WHEN) instead of COUNT(*) FILTER** — PostgreSQL FILTER clause is cleaner
- **Forgetting NOT EXISTS for milestone queries** — Without the anti-join, you count ALL completions, not FGTAT completions
- **Hardcoding period math** — Always derive `prevStartDate` from the same `days` parameter
- **Importing a chart library for a simple gauge** — SVG circle with `stroke-dashoffset` is 20 lines
- **Missing `::timestamp` cast** — TIMESTAMP columns silently return wrong results without explicit cast

---

## Files Reference (MERN LMS Implementation)

| File | What Was Added |
|------|---------------|
| `server/controllers/siteAnalyticsController.js` | `getCommunityPulse` endpoint (~380 lines) |
| `server/routes/siteAnalyticsRoutes.js` | 1 route line |
| `client/src/pages/admin/SiteAnalytics.jsx` | `CommunityPulseTab`, `HealthScoreGauge`, `DeltaIndicator` (~300 lines) |

## Related Patterns

- [Forensic Timing Analysis](./FORENSIC_TIMING_ANALYSIS_SYSTEM.md) — Another admin analytics system
- [Database Schema](../database-solutions/DATABASE_SCHEMA.md) — Full table reference
- [Student Progress Dashboard](../lms-patterns/STUDENT_PROGRESS_DASHBOARD_ARCHITECTURE.md) — Related analytics UI

---

## Time to Implement

**3-4 hours** for full backend + frontend with 6 query groups and all UI components.

## Difficulty Level

⭐⭐⭐⭐ (4/5) — Requires deep SQL knowledge, understanding of PostgreSQL-specific features (FILTER, CTEs, EXTRACT), parallel query orchestration, and SVG for the gauge. The individual patterns are straightforward but combining 10+ tables with graceful degradation and meaningful scoring is the real challenge.

---

**Author Notes:**
The key insight that made this work: every query group is independent with its own try/catch and default values. This means the feature is immediately useful even before all tables exist (migration 137 for page_views hadn't been run when first deployed). The `errors` array in the response acts as a built-in diagnostic — admins see which data sources are degraded.

The weighted health score formula is inherently subjective. The weights (learning 30%, community 20%, listening 15%, giving 15%, growth 20%) reflect a ministry LMS where learning is the primary mission. Adjust weights for your domain.
