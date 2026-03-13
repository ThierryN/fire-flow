# Skill: Importing YouTube Videos as Course Lessons

**Date:** 2024-10-24
**Context:** MERN Community LMS - School of the Priests
**Status:** ✅ Validated & Working

---

## Overview

This skill documents the complete process for importing YouTube videos as course lessons in the LMS, including all required database fields and common pitfalls to avoid.

---

## Problem Statement

When importing YouTube videos as lessons, the frontend may show:
- "No lessons" despite lessons existing in database
- Text content only instead of video player
- "No video with supported format and MIME type found" error
- Backend streaming errors (500 Internal Server Error)

---

## Root Causes & Solutions

### Issue 1: Lessons Not Visible in Frontend

**Root Cause:**
- Lessons imported with `section_id = NULL` (directly under course)
- Frontend CourseContent.jsx expects lessons to be organized in sections/modules

**Solution:**
- Always import lessons within a section structure
- Set `section_id` to a valid section UUID

**Migration Pattern:**
```sql
-- Step 1: Create section
WITH new_section AS (
  INSERT INTO sections (id, course_id, title, description, order_index, is_published)
  VALUES (gen_random_uuid(), 'course-uuid', 'Section Title', 'Description', 1, TRUE)
  RETURNING id, course_id
)
-- Step 2: Import lessons with section_id
INSERT INTO lessons (id, course_id, section_id, ...)
SELECT gen_random_uuid(), (SELECT course_id FROM new_section), (SELECT id FROM new_section), ...
```

---

### Issue 2: Video Player Not Rendering

**Root Cause:**
- Missing or incorrect `content_type` field
- Frontend checks: `if (activeLesson.contentType === 'video')` before rendering video player

**Solution:**
- Always set `content_type = 'video'` for video lessons

**Fix Migration:**
```sql
UPDATE lessons
SET content_type = 'video'
WHERE video_url IS NOT NULL;
```

---

### Issue 3: Backend Streaming Error (500)

**Root Cause:**
- `video_provider = 'custom'` or `NULL`
- Frontend tries to stream from backend: `/api/videos/stream/{lesson_id}`
- Backend streaming endpoint only works for uploaded files, not YouTube URLs

**Frontend Logic (CourseContent.jsx:609-642):**
```javascript
if (activeLesson.video_provider === 'custom' || !activeLesson.video_provider) {
  // Uses <video> tag with backend streaming endpoint
  <video src={`/api/videos/stream/${lesson_id}`} />
} else {
  // Uses YouTube iframe embed
  <iframe src={getYouTubeEmbedUrl(video_url)} />
}
```

**Solution:**
- Set `video_provider = 'youtube'` for YouTube videos
- Set `video_provider = 'vimeo'` for Vimeo videos
- Only use `video_provider = 'custom'` for uploaded MP4/WebM files

**Fix Migration:**
```sql
UPDATE lessons
SET video_provider = 'youtube'
WHERE video_url LIKE '%youtube.com%' OR video_url LIKE '%youtu.be%';
```

---

## Complete YouTube Import Template

### Required Fields for YouTube Video Lessons

```sql
INSERT INTO lessons (
  id,                    -- UUID (gen_random_uuid())
  course_id,             -- UUID of parent course
  section_id,            -- UUID of parent section (NOT NULL!)
  module_id,             -- UUID of parent module (or NULL)
  title,                 -- Lesson title
  description,           -- Short description
  content,               -- Full description (markdown supported)
  content_type,          -- MUST be 'video'
  video_url,             -- Full YouTube URL
  video_provider,        -- MUST be 'youtube'
  duration,              -- Duration in minutes (integer)
  order_index,           -- Display order (1, 2, 3...)
  is_published,          -- TRUE or FALSE
  is_free,               -- TRUE or FALSE
  created_at,            -- now()
  updated_at             -- now()
)
VALUES (
  gen_random_uuid(),
  'course-uuid-here',
  'section-uuid-here',
  NULL,
  'Lesson Title',
  'Short description',
  '## Overview\nFull lesson content here',
  'video',                                    -- ✅ Critical!
  'https://www.youtube.com/watch?v=VIDEO_ID',
  'youtube',                                  -- ✅ Critical!
  60,
  1,
  TRUE,
  FALSE,
  now(),
  now()
);
```

---

## Complete Working Migration Example

**File:** `server/migrations/020_reimport_fire_school_with_section.sql`

```sql
BEGIN;

-- STEP 1: Delete old lessons (if reimporting)
DELETE FROM lessons
WHERE course_id = (SELECT id FROM courses WHERE slug = 'course-slug')
AND section_id IS NULL;

-- STEP 2: Create section
WITH course AS (
  SELECT id FROM courses WHERE slug = 'course-slug' LIMIT 1
),
new_section AS (
  INSERT INTO sections (
    id, course_id, title, description, order_index, is_published, created_at, updated_at
  )
  SELECT
    gen_random_uuid(),
    c.id,
    'Section Title',
    'Section description',
    1,
    TRUE,
    now(),
    now()
  FROM course c
  RETURNING id, course_id
)

-- STEP 3: Insert lessons
INSERT INTO lessons (
  id, course_id, section_id, title, description, content,
  video_url, content_type, video_provider, duration, order_index,
  is_published, created_at, updated_at
)
SELECT * FROM (
  VALUES
    (
      gen_random_uuid(),
      (SELECT course_id FROM new_section),
      (SELECT id FROM new_section),
      'Lesson 1 Title',
      'Short description',
      '## Overview\nLesson content here',
      'https://www.youtube.com/watch?v=VIDEO_ID_1',
      'video',
      'youtube',
      60,
      1,
      TRUE,
      now(),
      now()
    ),
    (
      gen_random_uuid(),
      (SELECT course_id FROM new_section),
      (SELECT id FROM new_section),
      'Lesson 2 Title',
      'Short description',
      '## Overview\nLesson content here',
      'https://www.youtube.com/watch?v=VIDEO_ID_2',
      'video',
      'youtube',
      75,
      2,
      TRUE,
      now(),
      now()
    )
) AS lesson_data(
  id, course_id, section_id, title, description, content,
  video_url, content_type, video_provider, duration, order_index,
  is_published, created_at, updated_at
);

COMMIT;
```

---

## Verification Queries

### Check Lesson Structure
```sql
SELECT
  id,
  title,
  content_type,
  video_provider,
  video_url,
  section_id IS NOT NULL AS has_section
FROM lessons
WHERE course_id = (SELECT id FROM courses WHERE slug = 'course-slug')
ORDER BY order_index;
```

**Expected Results:**
- `content_type` = `'video'` ✅
- `video_provider` = `'youtube'` ✅
- `has_section` = `true` ✅

### Check Section Structure
```sql
SELECT
  c.id AS course_id,
  c.title AS course_title,
  (SELECT COUNT(*) FROM sections WHERE course_id = c.id) AS section_count,
  (SELECT COUNT(*) FROM lessons WHERE course_id = c.id) AS lesson_count,
  (SELECT COUNT(*) FROM lessons WHERE course_id = c.id AND section_id IS NOT NULL) AS lessons_in_sections
FROM courses c
WHERE c.slug = 'course-slug';
```

**Expected Results:**
- `section_count` > 0 ✅
- `lesson_count` > 0 ✅
- `lessons_in_sections` = `lesson_count` ✅

---

## Frontend Checklist

After importing, verify in the browser:

**Course Detail Page (`/courses/:id`)**
- [ ] Course shows "X sections • Y lessons" (not "0 sections • 0 lessons")
- [ ] "Enroll for Free" button works
- [ ] After enrollment, modal shows "Start Course" button

**Course Content Page (`/course-content/:id`)**
- [ ] Sidebar shows section title with lesson count
- [ ] All lessons are listed under the section
- [ ] Clicking a lesson shows YouTube video player (not error message)
- [ ] Video thumbnail loads correctly
- [ ] Video can play when clicked

---

## Common Pitfalls & Fixes

### ❌ Pitfall 1: Using DEFAULT values
```sql
-- DON'T DO THIS - database defaults may be wrong
INSERT INTO lessons (course_id, title, video_url)
VALUES ('uuid', 'Title', 'https://youtube.com/...');
```

**Why it fails:**
- `content_type` defaults to `NULL` or `'text'`
- `video_provider` defaults to `'custom'` or `NULL`
- `section_id` defaults to `NULL`

**✅ Solution:** Always explicitly set all required fields

---

### ❌ Pitfall 2: Forgetting section structure
```sql
-- DON'T DO THIS - no section
INSERT INTO lessons (course_id, section_id, ...)
VALUES ('course-uuid', NULL, ...);
```

**Why it fails:** Frontend expects lessons in sections

**✅ Solution:** Always create section first, then insert lessons with `section_id`

---

### ❌ Pitfall 3: Wrong video_provider
```sql
-- DON'T DO THIS - wrong provider for YouTube
UPDATE lessons SET video_provider = 'custom'
WHERE video_url LIKE '%youtube.com%';
```

**Why it fails:** Frontend tries to stream from backend instead of YouTube embed

**✅ Solution:** Use `video_provider = 'youtube'` for YouTube URLs

---

## Database Schema Reference

### lessons table (relevant columns)
```sql
- id: UUID PRIMARY KEY
- course_id: UUID NOT NULL
- section_id: UUID (should NOT be NULL for visibility)
- module_id: UUID (nullable)
- title: VARCHAR(255) NOT NULL
- description: TEXT
- content: TEXT
- content_type: VARCHAR(50) -- 'video', 'text', 'quiz', etc.
- video_url: VARCHAR(500)
- video_provider: VARCHAR(50) -- 'youtube', 'vimeo', 'custom'
- duration: INTEGER -- in minutes
- order_index: INTEGER
- is_published: BOOLEAN
- is_free: BOOLEAN
```

---

## Related Files

**Frontend:**
- `client/src/pages/CourseContent.jsx` - Main video player logic (lines 604-642)
- `client/src/pages/CourseDetail.jsx` - Course detail page with enrollment

**Backend:**
- `server/routes/courseRoutes.js` - Course API endpoints
- `server/controllers/courseController.js` - Course business logic

**Migrations:**
- `server/migrations/020_reimport_fire_school_with_section.sql` - Section structure
- `server/migrations/021_fix_fire_school_content_type.sql` - content_type fix
- `server/migrations/022_fix_fire_school_video_provider.sql` - video_provider fix

---

## Testing Checklist

### Database Level
- [ ] Lessons have `section_id` populated
- [ ] `content_type = 'video'`
- [ ] `video_provider = 'youtube'`
- [ ] `video_url` contains valid YouTube URL
- [ ] Section has `is_published = TRUE`
- [ ] Lessons have `is_published = TRUE`

### API Level
```bash
# Test course detail endpoint (should be public)
curl http://localhost:5000/api/courses/COURSE_ID

# Verify response includes:
# - sections array with lessons
# - totalLessons count > 0
```

### Frontend Level
- [ ] Course card shows correct lesson count
- [ ] Course detail page shows "X sections • Y lessons"
- [ ] Enrollment flow works
- [ ] "Start Course" button appears after enrollment
- [ ] Video player renders with YouTube iframe
- [ ] No console errors about video format/MIME type

---

## Success Metrics

✅ **You know it's working when:**
1. Course detail shows: "1 sections • 10 lessons" (actual counts)
2. Course content sidebar lists all lessons under section
3. Clicking lesson shows YouTube video thumbnail
4. Video plays when clicked
5. No backend streaming errors (500)
6. No "supported format" errors

---

## Emergency Fixes

If lessons are imported but not showing:

```sql
-- Fix #1: Add section structure
BEGIN;

WITH course AS (SELECT id FROM courses WHERE slug = 'course-slug'),
new_section AS (
  INSERT INTO sections (id, course_id, title, order_index, is_published)
  SELECT gen_random_uuid(), id, 'Course Lessons', 1, TRUE
  FROM course
  RETURNING id
)
UPDATE lessons
SET section_id = (SELECT id FROM new_section)
WHERE course_id = (SELECT id FROM course)
AND section_id IS NULL;

COMMIT;
```

```sql
-- Fix #2: Set content_type and video_provider
UPDATE lessons
SET
  content_type = 'video',
  video_provider = CASE
    WHEN video_url LIKE '%youtube.com%' OR video_url LIKE '%youtu.be%' THEN 'youtube'
    WHEN video_url LIKE '%vimeo.com%' THEN 'vimeo'
    ELSE 'custom'
  END
WHERE course_id = (SELECT id FROM courses WHERE slug = 'course-slug');
```

---

## Lessons Learned (2024-10-24)

### Issues Encountered & Fixed

1. **React Error**: "Objects are not valid as React child"
   - **Fix**: Changed `{error}` to `{error?.message}` in CourseDetail.jsx:74

2. **Course Detail 401 Error**: Endpoint required authentication
   - **Fix**: Moved `router.get('/:id')` before `router.use(protect)` in courseRoutes.js

3. **Empty Section Created**: User accidentally created empty section
   - **Fix**: DELETE query to remove it

4. **Lessons Not Showing**: Imported without `section_id`
   - **Fix**: Migration 020 to re-import with section structure

5. **Text Only (No Video Player)**: Missing `content_type`
   - **Fix**: Migration 021 to set `content_type = 'video'`

6. **Backend Streaming Error**: Wrong `video_provider`
   - **Fix**: Migration 022 to set `video_provider = 'youtube'`

---

## Summary

**Critical Fields for YouTube Videos:**
```
✅ section_id (NOT NULL)
✅ content_type = 'video'
✅ video_provider = 'youtube'
✅ video_url (valid YouTube URL)
```

**Migration Strategy:**
1. Create section first (with CTE)
2. Insert lessons with all required fields explicitly set
3. Verify with SELECT queries
4. Test in frontend before marking complete

**Remember:** Database defaults are often wrong. Always explicitly set all fields!

---

**End of Skill Document**
