# Video Progress Tracking - Complete Documentation

## Overview

The video progress tracking system automatically saves student progress while watching videos, displays completion status in the sidebar, and shows overall course progress. This feature works seamlessly with all three video types: custom uploads (MinIO), YouTube, and Vimeo.

## Features Implemented

### 1. Video Progress Tracking
- **Auto-save every 5 seconds** during video playback
- **Resume functionality** - videos resume from last watched position
- **Auto-completion** - lessons automatically marked complete at 90% watch time
- **Works with all video types**: Custom (MinIO), YouTube, Vimeo

### 2. Completion Checkmarks
- **Green checkmark** - Lesson completed
- **Blue progress circle** - Lesson in progress (shows %)
- **Gray circle** - Lesson not started
- **Real-time updates** - Progress reflects immediately

### 3. Course Progress Bar
- **Visual progress bar** in sidebar header
- **Completion stats** - "X of Y lessons complete (Z%)"
- **Auto-updates** as lessons are completed

### 4. Mark as Complete Button
- **For text lessons** - Manual completion button
- **Auto-hide** - Disappears once marked complete
- **Updates all indicators** instantly

## Database Schema

### Tables Created

#### `video_progress`
Tracks video playback progress.

```sql
CREATE TABLE video_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,

  -- All times stored as BIGINT milliseconds for performance
  playback_position_ms BIGINT NOT NULL DEFAULT 0,
  video_duration_ms BIGINT NOT NULL DEFAULT 0,
  total_watch_time_ms BIGINT NOT NULL DEFAULT 0,

  -- Auto-calculated by trigger
  completion_percentage INTEGER NOT NULL DEFAULT 0,
  is_completed BOOLEAN NOT NULL DEFAULT FALSE,
  completed_at TIMESTAMPTZ,

  last_accessed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  UNIQUE(user_id, lesson_id)
);
```

#### `lesson_progress`
Tracks completion for all lesson types (video, text, quiz, etc.).

```sql
CREATE TABLE lesson_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,

  is_completed BOOLEAN NOT NULL DEFAULT FALSE,
  completion_percentage INTEGER NOT NULL DEFAULT 0,
  completed_at TIMESTAMPTZ,

  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  UNIQUE(user_id, lesson_id)
);
```

### Indexes

```sql
-- Performance indexes
CREATE INDEX idx_video_progress_user_course ON video_progress(user_id, course_id);
CREATE INDEX idx_video_progress_completed ON video_progress(is_completed) WHERE is_completed = TRUE;
CREATE INDEX idx_lesson_progress_user_course ON lesson_progress(user_id, course_id);
CREATE INDEX idx_lesson_progress_completed ON lesson_progress(is_completed) WHERE is_completed = TRUE;
```

### Triggers

#### Auto-completion Trigger
Automatically calculates completion percentage and marks lessons complete at 90%.

```sql
CREATE TRIGGER trigger_auto_complete_video_lesson
  BEFORE INSERT OR UPDATE ON video_progress
  FOR EACH ROW
  EXECUTE FUNCTION auto_complete_video_lesson();
```

### Row Level Security (RLS)

All tables have RLS enabled with policies:
- Users can only view their own progress
- Users can only update their own progress
- Instructors can view all progress for their courses

## API Endpoints

### Video Progress

#### Update Video Progress
```
POST /api/video-progress/:lessonId
```

**Body:**
```json
{
  "currentTime": 125.5,      // seconds
  "duration": 300,            // seconds
  "watchTime": 5              // seconds watched since last update
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "playback_position": 125.5,     // converted to seconds
    "video_duration": 300,
    "total_watch_time": 130.5,
    "completion_percentage": 42,
    "is_completed": false
  }
}
```

#### Get Video Progress
```
GET /api/video-progress/:lessonId
```

Returns current progress for resume functionality.

#### Get Course Progress Summary
```
GET /api/video-progress/course/:courseId/summary
```

**Response:**
```json
{
  "success": true,
  "data": {
    "totalLessons": 20,
    "completedLessons": 8,
    "completionPercentage": 40
  }
}
```

#### Get All Lesson Progress
```
GET /api/video-progress/course/:courseId
```

Returns progress for all lessons (for sidebar checkmarks).

#### Mark Lesson Complete
```
POST /api/video-progress/lesson/:lessonId/complete
```

Manually marks a lesson complete (for text/quiz/assignment lessons).

## Frontend Implementation

### CourseContent.jsx

#### State Management

```javascript
const [lessonProgress, setLessonProgress] = useState({});  // Progress by lesson_id
const [courseProgress, setCourseProgress] = useState(null); // Overall stats
const [videoProgress, setVideoProgress] = useState(null);   // Current video
const progressIntervalRef = useRef(null);                   // Debounce timer
const videoRef = useRef(null);                              // Video element ref
```

#### Video Element

```jsx
<video
  ref={videoRef}
  onTimeUpdate={handleVideoTimeUpdate}
  onLoadedMetadata={(e) => {
    // Resume from saved position
    if (videoProgress?.playback_position_ms) {
      e.target.currentTime = videoProgress.playback_position_ms / 1000;
    }
  }}
  controls
  src={videoUrl}
/>
```

#### Progress Tracking Handler

```javascript
const handleVideoTimeUpdate = (e) => {
  const video = e.target;
  const currentTime = video.currentTime;
  const duration = video.duration;

  // Debounced API call every 5 seconds
  if (!progressIntervalRef.current) {
    progressIntervalRef.current = setTimeout(async () => {
      await api.post(`/video-progress/${lessonId}`, {
        currentTime,
        duration,
        watchTime: 5
      });

      // Reload progress indicators
      await loadVideoProgress();
      await loadAllLessonProgress();
      await loadCourseProgress();

      progressIntervalRef.current = null;
    }, 5000);
  }
};
```

#### Sidebar Progress Indicators

```jsx
{lessonProgress[lesson.id]?.is_completed ? (
  // Green checkmark
  <svg className="w-5 h-5 text-green-600" fill="currentColor">
    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
) : completionPercentage > 0 ? (
  // Blue progress circle
  <svg className="w-5 h-5 text-blue-600 transform -rotate-90">
    <circle cx="12" cy="12" r="10" fill="none" stroke="#e5e7eb" strokeWidth="2" />
    <circle
      cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="2"
      strokeDasharray={`${completionPercentage * 0.628} 62.8`}
    />
  </svg>
) : (
  // Gray circle with number
  <div className="w-5 h-5 border border-gray-300 rounded-full">
    {lessonIndex + 1}
  </div>
)}
```

#### Progress Bar

```jsx
{courseProgress && (
  <div className="mt-3">
    <div className="flex items-center justify-between text-sm mb-1">
      <span>{courseProgress.completedLessons} of {courseProgress.totalLessons} complete</span>
      <span className="font-medium">{courseProgress.completionPercentage}%</span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div
        className="bg-green-600 h-full transition-all duration-300"
        style={{ width: `${courseProgress.completionPercentage}%` }}
      />
    </div>
  </div>
)}
```

## Admin Features

### Video Preview in Course Builder

Instructors and admins can now preview videos directly in the course builder without switching to student view.

#### Features:
- **Preview button** for each video lesson
- **Supports all video types**: Custom (MinIO), YouTube, Vimeo
- **Toggle view** - Show/hide video player
- **Inline display** - No need to switch views

#### Implementation:

```jsx
{showPreview && lesson.contentType === 'video' && (
  <div className="border-t border-gray-200 p-4 bg-gray-50">
    <div className="aspect-video bg-gray-900 rounded-lg overflow-hidden">
      {isCustomVideo ? (
        <video controls src={`/api/videos/stream/${lesson._id}`} />
      ) : (
        <iframe src={getEmbedUrl(lesson.videoUrl)} allowFullScreen />
      )}
    </div>
  </div>
)}
```

## Security Considerations

### Database Security

1. **Row Level Security (RLS)** - All tables protected
2. **SECURITY DEFINER functions** - Proper privilege management
3. **Query plan caching** - Using `(SELECT auth.uid())` wrapper
4. **Search path safety** - `SET search_path = public, pg_temp`
5. **EXECUTE privileges revoked** from PUBLIC

### Frontend Security

1. **No exposed credentials** - All API calls authenticated
2. **User isolation** - Can only see own progress
3. **Input validation** - All data validated on backend
4. **XSS protection** - React handles escaping

## Performance Optimizations

### Database
- **BIGINT milliseconds** instead of NUMERIC seconds (faster arithmetic)
- **Partial indexes** on completed lessons only
- **Composite indexes** on (user_id, course_id)
- **Trigger-based calculations** - No client computation

### Frontend
- **Debounced API calls** - Every 5 seconds, not on every timeupdate
- **Batched state updates** - React optimizes re-renders
- **Conditional rendering** - Only load progress when needed
- **Cleanup on unmount** - Clear timers to prevent memory leaks

## Testing

### Backend Testing

```bash
# Test database migration
psql -U postgres -d mern_lms -f server/migrations/video_progress_FINAL_SECURE.sql

# Verify tables created
psql -U postgres -d mern_lms -c "\dt video_progress"
psql -U postgres -d mern_lms -c "\dt lesson_progress"

# Check RLS policies
psql -U postgres -d mern_lms -c "SELECT * FROM pg_policies WHERE tablename IN ('video_progress', 'lesson_progress');"
```

### API Testing

```bash
# Update progress
curl -X POST http://localhost:5000/api/video-progress/LESSON_ID \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"currentTime": 60, "duration": 300, "watchTime": 5}'

# Get progress
curl http://localhost:5000/api/video-progress/LESSON_ID \
  -H "Authorization: Bearer TOKEN"

# Get course summary
curl http://localhost:5000/api/video-progress/course/COURSE_ID/summary \
  -H "Authorization: Bearer TOKEN"
```

## Troubleshooting

### Progress Not Saving

**Check:**
1. Video element has `onTimeUpdate` handler
2. API calls succeeding (check Network tab)
3. User is authenticated
4. Lesson ID is correct

### Progress Not Resuming

**Check:**
1. Video element has `onLoadedMetadata` handler
2. `videoProgress` state is populated
3. Progress exists in database
4. Time conversion (ms to seconds) is correct

### Checkmarks Not Showing

**Check:**
1. `loadAllLessonProgress()` is called on mount
2. `lessonProgress` state is populated
3. Lesson IDs match between progress and lessons
4. React re-renders after progress updates

### Progress Bar Not Updating

**Check:**
1. `loadCourseProgress()` is called
2. API endpoint returns correct data
3. `courseProgress` state is set
4. Component re-renders after state change

## Future Enhancements

### Potential Features:
- [ ] Video quiz integration at specific timestamps
- [ ] Watch time analytics for instructors
- [ ] Playback speed tracking
- [ ] Video notes/bookmarks
- [ ] Certificate generation on course completion
- [ ] Email notifications on milestone completion
- [ ] Mobile app progress sync
- [ ] Offline progress tracking
- [ ] Video engagement heatmaps
- [ ] Peer comparison stats

## Files Modified/Created

### Backend:
- `server/migrations/video_progress_FINAL_SECURE.sql` - Database schema
- `server/controllers/videoProgressController.js` - API endpoints
- `server/routes/videoProgressRoutes.js` - Route definitions
- `server/server.js` - Route registration

### Frontend:
- `client/src/pages/CourseContent.jsx` - Student view with progress tracking
- `client/src/pages/teacher/CourseBuilder.jsx` - Admin video preview

### Documentation:
- `docs/VIDEO_PROGRESS_TRACKING.md` - This file

## Related Documentation

- [Lesson CRUD Operations](./LESSON_CRUD.md)
- [Video Playlist Import](./PLAYLIST_IMPORT.md)
- [API Setup Summary](./API_SETUP_RECORD.md)
