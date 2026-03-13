# Completion-Based Drip Content (Sequential Section Unlock) - Solution & Implementation

## The Problem

Students need to progress through course sections sequentially - each section unlocks only after completing all lessons in the previous section. This requires coordinating:
- Database schema changes (course-level feature flag)
- Backend service with efficient section-completion checking
- API middleware enforcing access at the route level
- Frontend UI showing lock state, progress bars, and unlock toasts

### Why It Was Hard

- **Completion definition is multi-dimensional**: A lesson is "complete" differently depending on type:
  - Video lessons: 90%+ watch progress
  - Quiz lessons: Must have a passing assessment attempt
  - Regular lessons: Explicit `lesson_progress.completed = true`
- **N+1 query risk**: Naive approach = 1 query per section per lesson. With 10 sections x 10 lessons = 100+ queries per page load.
- **Assessment linkage**: Quiz completion lives in `student_assessment_attempts` table, linked through `lessons.assessment_id → assessments.id`, NOT through a direct lesson_id on assessments.
- **Fail-open vs fail-closed**: Middleware must not block legitimate access if data is missing or queries fail.
- **Multiple route patterns**: Lesson ID comes from `req.params.id`, `req.params.lessonId`, `req.body.lesson_id`, or `req.body.lessonId` depending on the route.

### Impact

Without this feature, courses have no pacing mechanism. Students can skip ahead, miss foundational content, and instructors have no way to enforce learning progression.

---

## The Solution

### Architecture: 4-Layer System

```
┌──────────────────────────────────────────────────────┐
│ Layer 1: Database Migration                          │
│ courses.sequential_unlock_enabled (BOOLEAN)          │
├──────────────────────────────────────────────────────┤
│ Layer 2: Backend Service (sectionCompletionService)  │
│ Single JOIN query → section access map               │
├──────────────────────────────────────────────────────┤
│ Layer 3: Middleware (requireSectionUnlocked)          │
│ Route-level enforcement with fail-open               │
├──────────────────────────────────────────────────────┤
│ Layer 4: Frontend (useSectionAccess hook + UI)       │
│ React Query caching + lock icons + progress bars     │
└──────────────────────────────────────────────────────┘
```

### Root Cause of Complexity

The completion state spans 4 tables: `lessons`, `lesson_progress`, `assessments`, and `student_assessment_attempts`. Each lesson type has different completion criteria, and the data must be aggregated per-section efficiently.

---

## Layer 1: Database Migration

Simple but critical - a course-level boolean flag with a partial index.

```sql
ALTER TABLE courses ADD COLUMN IF NOT EXISTS
  sequential_unlock_enabled BOOLEAN DEFAULT FALSE;

-- Partial index: only index courses where feature is enabled
CREATE INDEX IF NOT EXISTS idx_courses_sequential_unlock
  ON courses(sequential_unlock_enabled)
  WHERE sequential_unlock_enabled = TRUE;
```

**Key decisions:**
- Course-level, not section-level (simpler, covers 95% of use cases)
- `DEFAULT FALSE` preserves existing behavior (all sections unlocked)
- Partial index keeps the index small since most courses won't use this

---

## Layer 2: Backend Service (The Hard Part)

### Single JOIN Query Pattern

The core insight: fetch ALL sections + lessons + progress + assessment data in ONE query, then compute in JavaScript.

```javascript
// sectionCompletionService.js
const rows = await sql`
  SELECT
    s.id AS section_id,
    s.title AS section_title,
    s.order_index AS section_order,
    l.id AS lesson_id,
    l.title AS lesson_title,
    l.content_type,
    l.assessment_id,
    lp.completed AS lesson_completed,
    lp.video_progress,
    CASE
      WHEN l.assessment_id IS NOT NULL THEN
        EXISTS (
          SELECT 1 FROM student_assessment_attempts saa
          WHERE saa.assessment_id = l.assessment_id
            AND saa.student_id = ${userId}
            AND saa.passed = true
        )
      ELSE NULL
    END AS quiz_passed
  FROM sections s
  LEFT JOIN lessons l ON l.section_id = s.id
  LEFT JOIN lesson_progress lp
    ON lp.lesson_id = l.id AND lp.user_id = ${userId}
  WHERE s.course_id = ${courseId}
  ORDER BY s.order_index, l.order_index
`;
```

**Why this works:**
- 1 query instead of N+1
- `EXISTS` subquery for quiz pass is efficient (stops at first match)
- `LEFT JOIN` ensures sections with no lessons still appear
- `ORDER BY` gives us sections in sequence for sequential logic

### Completion Logic Per Lesson Type

```javascript
function isLessonComplete(lesson) {
  // Video: 90%+ progress
  if (lesson.content_type === 'video') {
    return (lesson.video_progress || 0) >= 0.9 && lesson.lesson_completed;
  }
  // Quiz: must have passing attempt
  if (lesson.content_type === 'quiz' && lesson.assessment_id) {
    return lesson.quiz_passed === true;
  }
  // Default: explicit completion flag
  return lesson.lesson_completed === true;
}
```

### Section Access Map Output

```javascript
// Returns array like:
[
  {
    section_id: 'uuid-1',
    title: 'Introduction',
    order_index: 0,
    unlocked: true,          // Section 1 always unlocked
    completion_percent: 100,
    total_lessons: 3,
    completed_lessons: 3,
    missing_items: []
  },
  {
    section_id: 'uuid-2',
    title: 'Advanced Topics',
    order_index: 1,
    unlocked: true,          // Previous section 100% → unlocked
    completion_percent: 50,
    total_lessons: 4,
    completed_lessons: 2,
    missing_items: ['Lesson 3: Quiz not passed', 'Lesson 4: Not started']
  },
  {
    section_id: 'uuid-3',
    title: 'Final Project',
    order_index: 2,
    unlocked: false,         // Previous section < 100% → locked
    completion_percent: 0,
    total_lessons: 2,
    completed_lessons: 0,
    missing_items: ['Lesson 1: Not started', 'Lesson 2: Not started']
  }
]
```

### Critical Edge Cases

```javascript
// Section 1 is ALWAYS unlocked (no predecessor to complete)
if (i === 0) { unlocked = true; }

// Empty sections auto-complete (don't block progress)
if (lessons.length === 0) { return { complete: true, percent: 100 }; }

// Feature disabled → all sections unlocked
if (!course.sequential_unlock_enabled) { unlocked = true; }
```

---

## Layer 3: Middleware (Fail-Open Pattern)

```javascript
export const requireSectionUnlocked = async (req, res, next) => {
  try {
    // 1. Extract lesson ID from multiple possible locations
    const lessonId = req.params.id || req.params.lessonId
      || req.body?.lesson_id || req.body?.lessonId;
    if (!lessonId) return next(); // No lesson ID → skip

    // 2. Look up lesson → section → course
    const [lesson] = await sql`
      SELECT l.id, l.section_id, s.course_id
      FROM lessons l JOIN sections s ON l.section_id = s.id
      WHERE l.id = ${lessonId}
    `;
    if (!lesson) return next(); // Not found → let 404 handler deal with it

    // 3. Check feature flag
    const [course] = await sql`
      SELECT sequential_unlock_enabled FROM courses WHERE id = ${lesson.course_id}
    `;
    if (!course || !course.sequential_unlock_enabled) return next();

    // 4. Role bypass - admins and instructors always pass
    if (req.user?.role === 'admin' || req.user?.role === 'instructor') return next();

    // 5. Check section access
    const accessMap = await getSectionAccessMap(lesson.course_id, req.user.id);
    const sectionAccess = accessMap.find(s => s.section_id === lesson.section_id);
    if (!sectionAccess || sectionAccess.unlocked) return next();

    // 6. LOCKED → return 403 with helpful context
    return res.status(403).json({
      success: false,
      error: 'Section locked',
      message: 'Complete all lessons in the previous section to access this content',
      locked_section: sectionAccess.title,
      required_section: prevSection?.title,
      required_completion_percent: prevSection?.completion_percent ?? 0,
    });
  } catch (error) {
    // FAIL OPEN - never block on errors
    console.error('[SectionAccess Middleware] Error:', error);
    next();
  }
};
```

**Key design decisions:**
- **Fail-open**: On ANY error, `next()` is called. This prevents the middleware from accidentally locking students out due to a bug or database issue.
- **Multi-source lesson ID**: Different routes use different parameter names. The middleware handles all patterns.
- **Role bypass**: Admin/instructor always pass through. Check happens BEFORE the expensive `getSectionAccessMap` call.
- **Helpful 403**: Returns which section is locked and what needs completion, so the frontend can show meaningful UI.

### Route Integration

Apply middleware to content-access routes only:

```javascript
// lessonRoutes.js
router.get('/:id', protect, requireSectionUnlocked, getLesson);
router.post('/:id/complete', protect, requireSectionUnlocked, markLessonComplete);

// videoProgressRoutes.js
router.post('/:lessonId', protect, requireSectionUnlocked, updateVideoProgress);
router.get('/:lessonId', protect, requireSectionUnlocked, getVideoProgress);
```

**Do NOT apply to**: listing routes, course metadata, enrollment endpoints.

---

## Layer 4: Frontend (React Query + UI)

### useSectionAccess Hook

```javascript
export const useSectionAccess = (courseId, sequentialUnlockEnabled) => {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['sectionAccess', courseId],
    queryFn: () => CourseService.fetchSectionAccess(courseId),
    enabled: !!courseId && sequentialUnlockEnabled === true,
    staleTime: 30 * 1000,        // Cache for 30s
    refetchOnWindowFocus: false,  // Don't spam API on tab switch
  });

  const isSectionLocked = (sectionId) => {
    if (!sequentialUnlockEnabled || !data?.data) return false;
    const section = data.data.find(s => s.section_id === sectionId);
    return section ? !section.unlocked : false;
  };

  const getSectionProgress = (sectionId) => {
    if (!data?.data) return null;
    return data.data.find(s => s.section_id === sectionId) || null;
  };

  return { sectionAccess: data?.data, isLoading, refetch, isSectionLocked, getSectionProgress };
};
```

**Key pattern:** `enabled: sequentialUnlockEnabled === true` means the hook makes ZERO API calls for courses without the feature. No wasted network requests.

### Section Header UI

```jsx
{/* Lock icon or checkmark based on unlock status */}
{sequentialUnlockEnabled && (
  <span className="ml-2">
    {isSectionLocked(section.id) ? (
      <LockClosedIcon className="h-4 w-4 text-gray-400" />
    ) : getSectionProgress(section.id)?.completion_percent === 100 ? (
      <CheckCircleIcon className="h-4 w-4 text-green-500" />
    ) : null}
  </span>
)}

{/* Progress bar for unlocked sections */}
{sequentialUnlockEnabled && !isSectionLocked(section.id) && (
  <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
    <div
      className="bg-blue-600 h-1.5 rounded-full"
      style={{ width: `${getSectionProgress(section.id)?.completion_percent || 0}%` }}
    />
  </div>
)}
```

### Unlock Toast on Completion

```javascript
const markCompleteAndContinue = async () => {
  await markComplete(lessonId);

  if (sequentialUnlockEnabled) {
    const { data: newAccess } = await refetchSectionAccess();
    // Check if completing this lesson unlocked the next section
    const nextSection = newAccess?.find(s => s.order_index === currentSectionOrder + 1);
    if (nextSection?.unlocked) {
      toast.success(`Section "${nextSection.title}" is now unlocked!`);
    }
  }
};
```

---

## Testing the Fix

### Manual Test Cases

1. **Feature disabled**: All sections visible and accessible (no locks)
2. **Feature enabled, new student**: Only Section 1 unlocked, rest locked with lock icons
3. **Complete Section 1**: Section 2 unlocks with toast notification
4. **Direct API bypass attempt**: `GET /api/lessons/:lockedLessonId` returns 403
5. **Admin override**: Admin can access any lesson regardless of lock state
6. **Empty section**: Auto-completes, doesn't block progression
7. **Video lesson**: Requires 90%+ watch progress
8. **Quiz lesson**: Requires passing assessment attempt

### Build Verification

```bash
cd client && npm run build  # Must succeed with no errors
```

---

## Prevention

### Avoid These Mistakes

- **Don't query per-lesson**: Use a single JOIN query for the entire course
- **Don't forget the assessment_id FK**: Quiz completion links through `lessons.assessment_id → assessments.id`, NOT a direct `lesson_id` on assessments
- **Don't fail-closed in middleware**: Always `next()` on errors to avoid blocking legitimate access
- **Don't forget role bypass**: Check admin/instructor BEFORE expensive queries
- **Don't refetch on every render**: Use `staleTime: 30000` and `refetchOnWindowFocus: false`
- **Don't apply middleware to listing routes**: Only protect content-access endpoints

### Course Model Field Mapping

When adding new boolean columns to courses, remember to update the field mapping:

```javascript
// Course.pg.js - fieldMapping object
sequentialUnlockEnabled: 'sequential_unlock_enabled',
```

Without this, the camelCase→snake_case conversion fails silently and the column never gets set.

---

## Related Patterns

- `database-solutions/CONDITIONAL_SQL_MIGRATION_PATTERN.md` - Idempotent migrations
- `database-solutions/POSTGRES_SQL_TEMPLATE_BINDING_ERROR.md` - postgres.js tagged templates
- `patterns-standards/ES_MODULE_IMPORT_HOISTING_DOTENV.md` - ES Module import patterns
- `video-media/MEDIA_PLAYBACK_RESUME_PATTERN.md` - Video progress tracking

---

## Common Mistakes to Avoid

- ❌ **N+1 queries** - Don't query completion per-lesson. Use single JOIN.
- ❌ **Wrong assessment FK** - `lessons.assessment_id` links to `assessments.id`, not vice versa
- ❌ **Fail-closed middleware** - Always fail-open; let auth middleware handle unauthenticated
- ❌ **Forgetting Course.pg.js fieldMapping** - New columns need camelCase mapping entries
- ❌ **Applying middleware to all routes** - Only content-access routes, not listings
- ❌ **Ignoring empty sections** - Must auto-complete or they block forever
- ❌ **Missing Section 1 always-unlocked rule** - First section must always be accessible

---

## Resources

- postgres.js tagged template documentation
- React Query (TanStack Query) - staleTime/enabled patterns
- Express middleware best practices - fail-open vs fail-closed

---

## File Manifest

| File | Purpose |
|------|---------|
| `server/migrations/130_add_sequential_unlock_to_courses.sql` | Database column + index |
| `server/services/sectionCompletionService.js` | Core completion logic (3 exports) |
| `server/controllers/sectionAccessController.js` | API handler |
| `server/routes/sectionAccessRoutes.js` | Route definition |
| `server/middleware/sectionAccess.js` | Route-level enforcement |
| `server/models/Course.pg.js` | Field mapping addition |
| `client/src/hooks/useSectionAccess.js` | React Query hook |
| `client/src/pages/CourseContent.jsx` | Lock UI + progress bars |
| `client/src/pages/teacher/CourseBuilder.jsx` | Admin toggle |
| `client/src/services/course.js` | API service method |

## Time to Implement

4 plans, 12 commits, executed in 2 parallel breaths.

## Difficulty Level

⭐⭐⭐ (3/5) - Medium-hard. The single JOIN query and assessment FK linkage are the tricky parts. The rest follows standard patterns.

---

**Author Notes:**
The biggest gotcha was the assessment linkage. The naive assumption is that assessments have a `lesson_id`, but in this schema, lessons have an `assessment_id`. This means the JOIN direction and the EXISTS subquery for quiz completion must go through `lessons.assessment_id → assessments.id → student_assessment_attempts.assessment_id`. Getting this wrong means quiz lessons never show as complete, and sections never unlock past quizzes.

The fail-open middleware pattern was a deliberate architectural choice. In an LMS, it's better for a student to accidentally access content early than to be locked out of content they've legitimately completed. The frontend UI handles the "soft" gating; the middleware is a backup enforcement layer.
