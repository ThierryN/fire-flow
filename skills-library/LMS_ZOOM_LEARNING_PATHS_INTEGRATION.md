# LMS Zoom & Learning Paths Integration Guide

**Created:** January 19, 2026
**Category:** LMS Features / Video Integration
**Complexity:** Medium-High

---

## Overview

This skill documents the implementation of Learning Paths (career tracks/course bundles) and Zoom recording integration for the MERN Community LMS. It covers CRUD operations, drag-and-drop course reordering, video playback with proxy streaming, and a comprehensive feature roadmap for Zoom recordings.

---

## Part 1: Learning Paths Implementation

### Database Schema (Migration 107)

Three tables power the Learning Paths system:

```sql
-- Main learning paths table
CREATE TABLE learning_paths (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  slug VARCHAR(255) UNIQUE NOT NULL,
  description TEXT,
  short_description VARCHAR(500),
  thumbnail_url TEXT,
  banner_url TEXT,
  pricing_type VARCHAR(20) DEFAULT 'both', -- 'bundle', 'individual', 'both'
  bundle_price DECIMAL(10,2) DEFAULT 0,
  bundle_compare_price DECIMAL(10,2),
  prerequisite_enforcement VARCHAR(20) DEFAULT 'recommended', -- 'strict', 'recommended', 'none'
  enrollment_type VARCHAR(20) DEFAULT 'auto', -- 'auto', 'manual', 'gated'
  max_students INTEGER,
  status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'published', 'archived'
  is_featured BOOLEAN DEFAULT false,
  estimated_duration_hours INTEGER,
  difficulty_level VARCHAR(20),
  tags TEXT[],
  meta_title VARCHAR(255),
  meta_description TEXT,
  created_by UUID REFERENCES profiles(id),
  updated_by UUID REFERENCES profiles(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  published_at TIMESTAMP
);

-- Junction table for courses in paths
CREATE TABLE learning_path_courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  learning_path_id UUID REFERENCES learning_paths(id) ON DELETE CASCADE,
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  order_index INTEGER DEFAULT 0,
  is_required BOOLEAN DEFAULT true,
  unlock_after_days INTEGER,
  prerequisite_course_id UUID REFERENCES courses(id),
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(learning_path_id, course_id)
);

-- Student enrollment tracking
CREATE TABLE learning_path_enrollments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  learning_path_id UUID REFERENCES learning_paths(id) ON DELETE CASCADE,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  status VARCHAR(20) DEFAULT 'active', -- 'active', 'paused', 'completed', 'cancelled'
  progress_percentage DECIMAL(5,2) DEFAULT 0,
  completed_courses INTEGER DEFAULT 0,
  total_courses INTEGER DEFAULT 0,
  payment_type VARCHAR(20), -- 'free', 'bundle', 'individual'
  enrolled_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  last_accessed_at TIMESTAMP,
  certificate_issued BOOLEAN DEFAULT false,
  UNIQUE(learning_path_id, user_id)
);
```

### Backend API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/learning-paths` | List paths (paginated, filterable) | Optional |
| GET | `/api/learning-paths/:identifier` | Get by ID or slug | Optional |
| POST | `/api/learning-paths` | Create new path | Admin/Instructor |
| PUT | `/api/learning-paths/:id` | Update path | Admin/Instructor |
| DELETE | `/api/learning-paths/:id` | Delete path | Admin only |
| POST | `/api/learning-paths/:id/courses` | Add courses | Admin/Instructor |
| DELETE | `/api/learning-paths/:id/courses/:courseId` | Remove course | Admin/Instructor |
| PATCH | `/api/learning-paths/:id/courses/reorder` | Reorder courses | Admin/Instructor |
| POST | `/api/learning-paths/:id/enroll` | Enroll user | Authenticated |
| GET | `/api/learning-paths/user/my-paths` | Get user's paths | Authenticated |
| PATCH | `/api/learning-paths/:id/progress` | Update progress | Authenticated |

### Route Ordering Critical Issue

**Problem:** Express route ordering matters. If `/:identifier` comes before `/user/my-paths`, the latter will never match because "user" gets captured as the identifier.

**Solution:** Always define specific routes BEFORE parameterized routes:

```javascript
// CORRECT ORDER
router.get('/', optionalAuth, getLearningPaths);
router.get('/user/my-paths', protect, getMyLearningPaths);  // BEFORE /:identifier
router.get('/:identifier', optionalAuth, getLearningPath);  // AFTER specific routes
```

### Frontend: Drag-and-Drop with @dnd-kit

The admin UI uses `@dnd-kit` for course reordering:

```jsx
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

// Sortable item component
const SortableCourse = ({ course, onRemove }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: course.course_id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      {/* Course content */}
    </div>
  );
};

// Usage in parent component
<DndContext
  sensors={sensors}
  collisionDetection={closestCenter}
  onDragEnd={handleCourseDragEnd}
>
  <SortableContext items={courseIds} strategy={verticalListSortingStrategy}>
    {courses.map((course) => (
      <SortableCourse key={course.id} course={course} onRemove={handleRemove} />
    ))}
  </SortableContext>
</DndContext>
```

---

## Part 2: Zoom Recording Integration

### Video Playback Architecture

The system uses server-side proxy streaming to bypass Zoom's CORS restrictions:

```
[Student] → [LMS Server] → [Zoom API] → [Video Stream]
   ↑            ↓
   └── Proxied stream with proper headers
```

**Why Proxy?**
- Zoom's `play_url` has X-Frame-Options and CORS headers that prevent direct embedding
- URLs expire after 24 hours
- Proxy allows for access control, analytics, and URL refresh

### Key Endpoints

```javascript
// Stream proxy - bypasses CORS
GET /api/zoom/recordings/:id/stream

// Refresh expired URLs
GET /api/zoom/recordings/:id/refresh-urls

// Sync recordings from Zoom cloud
POST /api/zoom/recordings/sync
POST /api/zoom/recordings/sync-single
```

### URL Caching Strategy

```javascript
const urlCache = new Map();
const CACHE_TTL = 60 * 60 * 1000; // 1 hour

// Check cache first
const cached = urlCache.get(cacheKey);
if (cached && (Date.now() - cached.fetchedAt < CACHE_TTL)) {
  return cached.data;
}

// Fetch fresh from Zoom API
const recordingsData = await zoomConfig.getMeetingRecordings(zoomMeetingId);

// Cache for 1 hour
urlCache.set(cacheKey, {
  data: responseData,
  fetchedAt: Date.now()
});
```

### Common Issue: Missing Database Columns

**Symptom:** "Failed to sync recording" error

**Cause:** Controller references columns not in migration (e.g., `timezone`)

**Fix:** Create migration to add missing column:

```sql
-- Migration: Add timezone column to zoom_meetings
ALTER TABLE zoom_meetings
ADD COLUMN IF NOT EXISTS timezone VARCHAR(100) DEFAULT 'UTC';
```

### Video Player Error Handling

Use the proxy endpoint, not direct Zoom URLs:

```jsx
// WRONG - will fail due to CORS
<video src={recording.playUrl} />

// CORRECT - use server proxy
<video src={`/api/zoom/recordings/${recording.id}/stream`} />
```

---

## Part 3: Zoom Features Roadmap

### Tier 1: High Impact, Implement First

1. **Transcript Sync & Display**
   - Fetch VTT files from Zoom API
   - Searchable transcript alongside video
   - Timeline with clickable timestamps
   - Effort: 2-3 days

2. **Video Chapter Markers**
   - Instructor-created segments
   - Click-to-seek navigation
   - Auto-generate from transcript
   - Effort: 3-4 days

3. **Enhanced Analytics Dashboard**
   - Completion heatmap
   - Engagement timeline
   - Dropout point identification
   - Effort: 2-3 days

4. **Auto-Publishing Webhook**
   - Listen for `recording.completed`
   - Auto-link to course lessons
   - Effort: 1-2 days

### Tier 2: Moderate Impact

5. **Speaker Identification** (via Nylas/AssemblyAI)
6. **Searchable Clips/Bookmarks**
7. **Fine-grained Access Control**

### Tier 3: Advanced Features

8. **AI Summaries** (OpenAI/Claude)
9. **Closed Captions** (VTT rendering)
10. **Interactive Polls/Quizzes**
11. **Peer Collaboration** (watch parties)

### Database Extensions Needed

```sql
-- Transcripts
CREATE TABLE zoom_recording_transcripts (
  id UUID PRIMARY KEY,
  recording_id UUID REFERENCES zoom_meetings(id),
  transcript_url TEXT,
  vtt_content TEXT,
  status VARCHAR(20),
  language VARCHAR(10)
);

-- Chapters
CREATE TABLE zoom_recording_chapters (
  id UUID PRIMARY KEY,
  recording_id UUID REFERENCES zoom_meetings(id),
  start_time INTEGER,
  end_time INTEGER,
  title VARCHAR(255),
  description TEXT,
  is_auto_generated BOOLEAN DEFAULT false
);

-- Student clips/bookmarks
CREATE TABLE zoom_recording_clips (
  id UUID PRIMARY KEY,
  recording_id UUID REFERENCES zoom_meetings(id),
  user_id UUID REFERENCES profiles(id),
  start_time INTEGER,
  end_time INTEGER,
  title VARCHAR(255),
  notes TEXT,
  visibility VARCHAR(20)
);
```

### Webhook Implementation

```javascript
// POST /api/webhooks/zoom
export const handleZoomWebhook = asyncHandler(async (req, res) => {
  const { event, payload } = req.body;

  switch (event) {
    case 'recording.completed':
      await syncRecordingToLesson(payload.object.id);
      break;
    case 'recording.transcript_completed':
      await fetchAndStoreTranscript(payload.object.id);
      break;
  }

  res.status(200).json({ status: 'success' });
});
```

---

## Troubleshooting Guide

### Issue: Delete button not working

**Check:**
1. Console for `[Delete]` log messages
2. Network tab for API response
3. If error says "active enrollment(s)", archive instead

**Common causes:**
- Route ordering issue (fixed above)
- Missing auth token
- Active enrollments blocking deletion

### Issue: Video won't play

**Check:**
1. Use proxy endpoint, not direct Zoom URL
2. Recording must be synced to database
3. Check `zoom_meeting_id` exists in table

### Issue: Recording sync fails

**Check:**
1. All required columns exist in `zoom_meetings`
2. Zoom API credentials valid
3. Meeting has cloud recording enabled

### Issue: Learning path courses don't save

**Check:**
1. Courses added via separate API call after path creation
2. Order is maintained via `order_index`
3. Unique constraint on `(learning_path_id, course_id)`

---

## Files Reference

### Learning Paths
- `server/migrations/107_create_learning_paths.sql`
- `server/controllers/learningPathController.js`
- `server/routes/learningPathRoutes.js`
- `server/utils/slugUtils.js`
- `client/src/pages/admin/LearningPaths.jsx`
- `client/src/pages/LearningPaths.jsx`
- `client/src/pages/LearningPathDetail.jsx`

### Zoom Integration
- `server/controllers/zoomController.js`
- `server/controllers/zoomRecordingManagement.js`
- `server/routes/zoomRoutes.js`
- `client/src/components/video/ZoomRecordingPlayer.jsx`
- `client/src/pages/admin/ZoomRecordings.jsx`
- `client/src/pages/admin/ZoomCloudLibrary.jsx`

---

## Summary

This skill covers:
1. **Learning Paths** - Complete CRUD with drag-and-drop course management
2. **Route ordering** - Critical Express.js pattern for parameterized routes
3. **Video proxy streaming** - Bypass CORS for embedded playback
4. **URL caching** - Handle 24-hour expiration
5. **Feature roadmap** - Prioritized list of enhancements

The biggest ROI improvements for Zoom are: transcripts, chapters, analytics, and webhooks.

---

**Tags:** `lms`, `zoom`, `learning-paths`, `video-streaming`, `drag-and-drop`, `dnd-kit`, `express-routing`
