# LMS Student Progress Dashboard - Architecture & Implementation Pattern

## The Problem

Instructors and admins need a centralized dashboard to track student progress across courses, identify at-risk students, view detailed analytics per student, and take action (grade, message, enroll). Most LMS platforms (Thinkific, Canvas, Teachable) provide this as a core feature, but building it from scratch requires careful architecture to avoid performance issues and ensure the data is actionable.

### Why It Was Hard

- **Data already exists but is scattered** across 6+ tables (enrollments, lesson_progress, video_progress, student_assessment_attempts, assignment_submissions, profiles)
- **At-risk detection** requires multi-factor SQL logic (inactivity + low scores + stalled progress)
- **3-level drill-down** (Course List -> Student List -> Student Detail) means 3 separate pages with different data needs
- **Performance risk** from N+1 queries when aggregating progress across many students
- **Role-based access** (admin=all, instructor=own courses) must be enforced at every level

### Impact

Without this dashboard, instructors have no visibility into which students are struggling, falling behind, or disengaged. They can't intervene early, which leads to higher dropout rates.

---

## The Solution

### Architecture: 3-Level Drill-Down

```
/admin/student-progress              -> Course List (summary stats per course)
/admin/student-progress/:courseId     -> Student List (table with progress, charts)
/admin/student-progress/:courseId/students/:studentId -> Student Detail (4 tabs)
```

### Database Strategy: No New Tables Needed

The key insight: **all progress data already exists** in a well-designed LMS. You don't need new tables — you need new queries that aggregate existing data.

| Existing Table | What It Provides |
|----------------|-----------------|
| `enrollments` | user_id, course_id, progress %, enrolled_at |
| `lesson_progress` | Per-lesson completion, time_spent, first/last accessed |
| `video_progress` | Video playback position, completion % |
| `student_assessment_attempts` | Quiz scores, pass/fail, submitted_at |
| `assignment_submissions` | Assignment grades, status, submitted_at |
| `profiles` | Student name, email, avatar |

### At-Risk Detection: Multi-Factor SQL Pattern

This was the hardest query to get right. Three independent criteria, any of which flags a student:

```sql
CASE
  WHEN e.progress >= 100 THEN 'completed'
  WHEN (
    -- Criterion 1: No activity in 7+ days AND not completed
    MAX(lp.last_accessed_at) < NOW() - INTERVAL '7 days'
    AND e.progress < 100
  ) OR (
    -- Criterion 2: Most recent quiz score < 50%
    EXISTS (
      SELECT 1 FROM student_assessment_attempts saa
      JOIN assessments a ON saa.assessment_id = a.id
      WHERE saa.student_id = p.id
        AND a.course_id = e.course_id
        AND saa.score < 50
        AND saa.submitted_at = (
          SELECT MAX(submitted_at) FROM student_assessment_attempts
          WHERE student_id = p.id AND assessment_id = saa.assessment_id
        )
    )
  ) OR (
    -- Criterion 3: No progress in 14 days AND <50% done
    MAX(lp.last_accessed_at) < NOW() - INTERVAL '14 days'
    AND e.progress < 50
  ) THEN 'at-risk'
  ELSE 'active'
END as status
```

**Why 3 criteria:** Single-factor detection (just inactivity) has too many false positives. A student on vacation isn't at-risk. But a student who's inactive AND scoring poorly AND stalled — that's actionable.

### Backend Pattern: 5 API Endpoints

```
GET /api/student-progress/courses                          -- Course list with stats
GET /api/student-progress/courses/:courseId/students        -- Student table (paginated)
GET /api/student-progress/courses/:courseId/students/:id    -- Student detail (4 tabs)
GET /api/student-progress/courses/:courseId/activity-trend  -- 30-day daily activity
GET /api/student-progress/courses/:courseId/students/:id/progress-timeline -- Completion over time
GET /api/student-progress/courses/:courseId/export          -- CSV download
```

**Role-based filtering pattern:**
```javascript
// Admin: see all courses
// Instructor: see only their courses
let courseFilter = '';
const params = [];

if (req.user.role === 'instructor') {
  courseFilter = 'WHERE c.instructor_id = $1';
  params.push(req.user.id);
}

const courses = await sql.unsafe(`
  SELECT c.id, c.title, ...
  FROM courses c
  ${courseFilter}
`, params);
```

### Frontend Pattern: Recharts + Dark Theme Admin

**Charting library:** Recharts (React-native, lightweight, no Node 18 concerns)

```jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Dark theme tooltip style (matches admin panel)
const tooltipStyle = {
  backgroundColor: '#1E293B',
  border: '1px solid rgba(55, 65, 81, 0.5)',
  borderRadius: '0.5rem',
  color: '#E5E7EB'
};
```

**4 chart types used:**
1. **Completion Distribution (BarChart)** — Students grouped by 0-25%, 25-50%, 50-75%, 75-100%
2. **Activity Trend (LineChart)** — Daily activity count for last 30 days
3. **Progress Timeline (LineChart)** — Individual student's completion % over time
4. **Quiz Scores (BarChart)** — Per-assessment scores with passing line

### Student Detail: 4-Tab Architecture

```
┌──────────────────────────────────────────────────────────┐
│ Student Header (name, email, stats, action buttons)      │
├──────────────────────────────────────────────────────────┤
│ [Charts Row: Progress Timeline | Quiz Scores | Heatmap]  │
├──────────────────────────────────────────────────────────┤
│ [Lessons] [Quizzes] [Assignments] [Activity Log]         │
│ ═══════                                                  │
│ Tab content area (section-grouped lessons, scores, etc.) │
└──────────────────────────────────────────────────────────┘
```

**Inline grading pattern** (Assignments tab):
```javascript
// Use existing grading API - don't rebuild
import { gradeSubmission } from '../../services/assignmentApi';

const handleGrade = async (submissionId, grade, feedback) => {
  await gradeSubmission(submissionId, { grade, feedback });
  toast.success('Assignment graded');
  refreshData(); // Re-fetch student detail
};
```

### 30-Day Calendar Heatmap (Custom, No Library)

Built with CSS Grid — no library needed:

```jsx
// 30 cells, 7 columns (week view), color intensity by activity count
const CalendarHeatmap = ({ activityDays }) => (
  <div className="grid grid-cols-7 gap-1">
    {last30Days.map(day => {
      const count = activityDays[day] || 0;
      const intensity = count === 0 ? 'bg-gray-800'
        : count <= 2 ? 'bg-emerald-900'
        : 'bg-emerald-500';
      return <div key={day} className={`w-4 h-4 rounded-sm ${intensity}`} title={`${day}: ${count} activities`} />;
    })}
  </div>
);
```

### Export Strategy

- **CSV:** Server-side generation (reuse existing analytics export pattern)
- **PDF:** `window.print()` with `@media print` CSS (zero dependencies, works everywhere)
  - Add `className="no-print"` to action buttons, sidebars
  - Override dark theme to white background for print
  - `break-inside: avoid` on chart containers

---

## Testing the Fix

### Verification Checklist
1. Navigate to `/admin/student-progress` — see course cards
2. Click a course — see student table with status badges
3. Filter by "At-Risk" — only flagged students shown
4. Click a student — see 4 tabs with data
5. Grade an assignment inline — toast confirms, data refreshes
6. Export CSV — file downloads with correct columns
7. Send message — navigates to messaging system
8. Switch to instructor account — only own courses visible

---

## Prevention

### Performance Optimization
- Use `Promise.all()` for parallel queries (not sequential)
- Whitelist sort columns to prevent SQL injection
- Enforce pagination (max 100 per page)
- Add indexes on `lesson_progress.last_accessed_at` and `enrollments.progress` if queries exceed 500ms

### Common Gotchas
- **enrollments.progress vs enrollment_progress table** — Use `enrollments.progress` (trigger-maintained), not the separate table
- **N+1 queries in student detail** — Fetch all 4 tab datasets in a single `Promise.all()`, not per-tab
- **Recharts imports** — Use named imports (`import { BarChart } from 'recharts'`), NOT `import * as Recharts` (huge bundle)
- **Admin page pattern** — Use `useState` + `useEffect`, NOT react-query (consistency with existing admin pages)

---

## Related Patterns

- `lms-patterns/VIDEO_PROGRESS_DRIP_FEED_IMPLEMENTATION.md` — Video progress tracking
- `lms-patterns/QUIZ_INTEGRATION_GUIDE.md` — Quiz system architecture
- `database-solutions/CONDITIONAL_SQL_MIGRATION_PATTERN.md` — SQL query patterns
- `methodology/MERN_QUICK_REFERENCE.md` — Express route/controller patterns

---

## Common Mistakes to Avoid

- ❌ **Creating new database tables** for data that already exists in lesson_progress/video_progress
- ❌ **Using react-query in admin pages** when existing admin pages use useState+useEffect
- ❌ **Installing heavy PDF libraries** when window.print() works for the use case
- ❌ **Single-factor at-risk detection** (just "inactive 7 days" has too many false positives)
- ❌ **Fetching tab data on tab switch** — Fetch all at once, render the active tab
- ❌ **Forgetting role-based filtering** — Instructors must only see their own courses

---

## Resources

- [Thinkific Progress Reports](https://support.thinkific.com/hc/en-us/articles/360030369974-Progress-Reports)
- [Canvas LMS Analytics](https://www.instructure.com/canvas)
- [Recharts Documentation](https://recharts.org/)
- [LMS Reporting Best Practices (2026)](https://www.educate-me.co/blog/lms-reporting)

---

## Time to Implement

**5 plans, 3 breaths:**
- Breath 1 (Backend): ~30-45 minutes
- Breath 2 (Course List + Student List): ~45-60 minutes (parallel)
- Breath 3 (Student Detail + Actions): ~60-90 minutes (parallel)
- **Total: ~3-4 hours**

## Difficulty Level

⭐⭐⭐ (3/5) — Medium complexity. The SQL queries and multi-tab UI are non-trivial, but all data sources exist. The challenge is aggregation and UX, not infrastructure.

---

**Author Notes:**
The biggest insight was that ~60% of the backend already existed in `analyticsController.js`. Before planning, always run a thorough codebase research to discover existing endpoints, views, and models. The research agent found course-level analytics, student listing with progress, and CSV export — all pre-built. This turned a 10-plan phase into a 5-plan phase.

The at-risk detection SQL was the most complex piece. Three criteria give much better signal than one. Test it against real data early — false positives erode instructor trust quickly.

**Created:** 2026-02-10
**Context:** MERN Community LMS Phase 13 planning session
