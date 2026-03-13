# Video Progress & Drip Feed Implementation Guide

**Date:** January 20, 2025
**Status:** 🚧 In Progress
**Features:** Video Progress Tracking, Lesson Completion, Drip Feed Content

---

## 📋 Overview

This guide documents the implementation of:
1. **Video Progress Tracking** - Track watch time, resume position, completion
2. **Lesson Completion** - Mark lessons complete, show progress in sidebar
3. **Drip Feed Content** - Control when lessons become available to students

---

## ✅ Completed Backend Work

### 1. Database Schema
**File:** [server/migrations/video_progress_tracking.sql](server/migrations/video_progress_tracking.sql)

**New Tables Created:**

#### video_progress
Tracks individual video watch progress for each student
```sql
- id (UUID Primary Key)
- user_id (UUID) - Student watching the video
- lesson_id (UUID) - Lesson being watched
- course_id (UUID) - Course containing the lesson
- current_time (DECIMAL) - Current playback position in seconds
- duration (DECIMAL) - Total video duration in seconds
- watch_time (DECIMAL) - Total time watched (cumulative)
- completion_percentage (DECIMAL) - 0 to 100
- is_completed (BOOLEAN) - TRUE when >= 90% watched
- completed_at (TIMESTAMP) - When video was completed
- last_watched_at (TIMESTAMP) - Last update time
```

#### lesson_progress
Tracks completion of ALL lesson types (video, text, quiz, assignment)
```sql
- id (UUID Primary Key)
- user_id (UUID)
- lesson_id (UUID)
- course_id (UUID)
- section_id (UUID)
- is_completed (BOOLEAN)
- completed_at (TIMESTAMP)
- time_spent (INTEGER) - Total time in seconds
- first_accessed_at (TIMESTAMP)
- last_accessed_at (TIMESTAMP)
```

**Features:**
- ✅ Automatic video completion at 90% watch
- ✅ Trigger to auto-update lesson_progress when video completes
- ✅ course_progress_summary view for aggregate stats
- ✅ Indices for performance
- ✅ Unique constraints to prevent duplicates

### 2. Backend API
**Files Created:**
- [server/controllers/videoProgressController.js](server/controllers/videoProgressController.js)
- [server/routes/videoProgressRoutes.js](server/routes/videoProgressRoutes.js)

**API Endpoints:**

#### POST /api/video-progress/:lessonId
Update video progress (called periodically during playback)
```json
Body: {
  "currentTime": 120.5,  // seconds
  "duration": 300.0,     // seconds
  "watchTime": 5.0       // optional: incremental watch time
}

Response: {
  "success": true,
  "data": {
    "id": "...",
    "completion_percentage": 40.17,
    "is_completed": false,
    ...
  },
  "message": "Progress updated"
}
```

#### GET /api/video-progress/:lessonId
Get current progress for a lesson (for resume functionality)
```json
Response: {
  "success": true,
  "data": {
    "current_time": 120.5,
    "duration": 300.0,
    "completion_percentage": 40.17,
    ...
  }
}
```

#### GET /api/video-progress/course/:courseId
Get all video progress for a course
```json
Response: {
  "success": true,
  "data": [ /* array of progress records */ ],
  "count": 10
}
```

#### GET /api/video-progress/course/:courseId/summary
Get aggregate course completion stats
```json
Response: {
  "success": true,
  "data": {
    "totalLessons": 30,
    "completedLessons": 12,
    "completionPercentage": 40,
    "totalTimeSpent": 3600,  // seconds
    "remainingLessons": 18
  }
}
```

#### POST /api/video-progress/lesson/:lessonId/complete
Manually mark lesson as complete (for non-video lessons)
```json
Response: {
  "success": true,
  "data": { /* lesson_progress record */ },
  "message": "Lesson marked as complete"
}
```

### 3. Server Configuration
**File:** [server/server.js](server/server.js)

**Changes:**
- Line 36: Added `import videoProgressRoutes`
- Line 82: Added `app.use('/api/video-progress', videoProgressRoutes)`

---

## 🚧 Pending Frontend Work

### 1. Run Database Migration
**Priority:** HIGH - Must complete before testing

**Steps:**
```powershell
# Option 1: Using psql
psql -U postgres -d mern_lms -f "C:\Users\Thier\source\repos\my-other-project\server\migrations\video_progress_tracking.sql"

# Option 2: Using pgAdmin
# 1. Open pgAdmin
# 2. Connect to mern_lms database
# 3. Tools → Query Tool
# 4. File → Open → Select video_progress_tracking.sql
# 5. Execute (F5)
```

**Verification:**
```sql
-- Check if tables were created
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('video_progress', 'lesson_progress');

-- Should return both table names
```

### 2. Add Video Progress Tracking to Player
**File to modify:** `client/src/pages/CourseContent.jsx`

**Implementation:**
```javascript
// At the top of the component
const [videoProgress, setVideoProgress] = useState(null);
const progressIntervalRef = useRef(null);

// Load existing progress when lesson changes
useEffect(() => {
  if (activeLesson && activeLesson.content_type === 'video') {
    loadVideoProgress();
  }
}, [activeLesson]);

const loadVideoProgress = async () => {
  try {
    const res = await api.get(`/video-progress/${activeLesson.id}`);
    if (res.data.data) {
      setVideoProgress(res.data.data);
    }
  } catch (error) {
    console.error('Error loading video progress:', error);
  }
};

// Track progress every 5 seconds during playback
const handleVideoTimeUpdate = (e) => {
  const video = e.target;
  const currentTime = video.currentTime;
  const duration = video.duration;

  // Update local state
  setVideoProgress(prev => ({
    ...prev,
    current_time: currentTime,
    duration,
    completion_percentage: (currentTime / duration) * 100
  }));

  // Debounced API call every 5 seconds
  if (!progressIntervalRef.current) {
    progressIntervalRef.current = setTimeout(async () => {
      try {
        await api.post(`/video-progress/${activeLesson.id}`, {
          currentTime,
          duration,
          watchTime: 5 // or calculate actual watch time
        });
      } catch (error) {
        console.error('Error updating progress:', error);
      }
      progressIntervalRef.current = null;
    }, 5000);
  }
};

// Update video element
<video
  className="w-full h-full bg-black"
  controls
  controlsList="nodownload"
  src={`/api/videos/stream/${activeLesson.id || activeLesson._id}`}
  onTimeUpdate={handleVideoTimeUpdate}
  onLoadedMetadata={(e) => {
    // Resume from last position
    if (videoProgress?.current_time) {
      e.target.currentTime = videoProgress.current_time;
    }
  }}
>
  Your browser does not support the video tag.
</video>
```

### 3. Add Completion Checkmarks to Sidebar
**File to modify:** `client/src/pages/CourseContent.jsx`

**Implementation:**
```javascript
// Load lesson progress for the course
const [lessonProgress, setLessonProgress] = useState({});

useEffect(() => {
  if (course) {
    loadLessonProgress();
  }
}, [course]);

const loadLessonProgress = async () => {
  try {
    const res = await api.get(`/video-progress/course/${courseId}`);
    const progressMap = {};
    res.data.data.forEach(p => {
      progressMap[p.lesson_id] = p;
    });
    setLessonProgress(progressMap);
  } catch (error) {
    console.error('Error loading lesson progress:', error);
  }
};

// In the lesson rendering, add checkmark
{module.lessons?.map((lesson, lessonIndex) => {
  const progress = lessonProgress[lesson.id || lesson._id];
  const isCompleted = progress?.is_completed;

  return (
    <div
      key={lesson.id || lesson._id}
      className={`flex items-center justify-between p-3 cursor-pointer ... ${
        isCompleted ? 'bg-green-50' : ''
      }`}
      onClick={() => {
        setActiveLesson(lesson);
        setActiveModule(module);
      }}
    >
      <div className="flex items-center gap-3">
        {/* Completion checkmark */}
        {isCompleted && (
          <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        )}

        {/* Lesson content type icon */}
        <div className="text-gray-500">
          {/* ... existing icon code ... */}
        </div>

        {/* Lesson title */}
        <span className="text-sm">{lesson.title}</span>
      </div>

      {/* Progress percentage for videos */}
      {progress && !isCompleted && lesson.content_type === 'video' && (
        <span className="text-xs text-gray-500">
          {Math.round(progress.completion_percentage)}%
        </span>
      )}
    </div>
  );
})}
```

### 4. Mark Text Lessons as Complete
**File to modify:** `client/src/pages/CourseContent.jsx`

**Add a "Mark as Complete" button for text lessons:**
```javascript
{(activeLesson.contentType || activeLesson.content_type) === 'text' && (
  <div className="prose prose-lg max-w-none">
    <div dangerouslySetInnerHTML={{ __html: activeLesson.content || 'Content not available' }} />

    {/* Mark as Complete button */}
    {!lessonProgress[activeLesson.id]?.is_completed && (
      <div className="mt-8 text-center">
        <button
          onClick={async () => {
            try {
              await api.post(`/video-progress/lesson/${activeLesson.id}/complete`);
              await loadLessonProgress(); // Refresh progress
              toast.success('Lesson marked as complete!');
            } catch (error) {
              console.error('Error marking lesson complete:', error);
              toast.error('Failed to mark lesson complete');
            }
          }}
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          Mark as Complete
        </button>
      </div>
    )}
  </div>
)}
```

### 5. Add Progress Bar to Course Header
**File to modify:** `client/src/pages/CourseContent.jsx`

**Add course progress summary:**
```javascript
const [courseProgress, setCourseProgress] = useState(null);

useEffect(() => {
  if (course) {
    loadCourseProgress();
  }
}, [course]);

const loadCourseProgress = async () => {
  try {
    const res = await api.get(`/video-progress/course/${courseId}/summary`);
    setCourseProgress(res.data.data);
  } catch (error) {
    console.error('Error loading course progress:', error);
  }
};

// In the header section
<div className="bg-white border-b border-gray-200 p-6">
  <h1 className="text-2xl font-bold">{course.title}</h1>

  {/* Progress bar */}
  {courseProgress && (
    <div className="mt-4">
      <div className="flex justify-between text-sm text-gray-600 mb-2">
        <span>{courseProgress.completed_lessons} of {courseProgress.total_lessons} lessons complete</span>
        <span>{courseProgress.completion_percentage}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-green-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${courseProgress.completion_percentage}%` }}
        />
      </div>
    </div>
  )}
</div>
```

---

## 🎨 UI Enhancements

### Sidebar Improvements

#### 1. Lesson Status Icons
```javascript
// Completed: Green checkmark
<svg className="w-5 h-5 text-green-600" />

// In Progress: Yellow play icon
<svg className="w-5 h-5 text-yellow-600" />

// Locked (drip feed): Gray lock icon
<svg className="w-5 h-5 text-gray-400" />

// Not Started: Hollow circle
<svg className="w-5 h-5 text-gray-300" />
```

#### 2. Section Progress Summary
```javascript
{sections.map(section => {
  const sectionLessons = section.lessons || [];
  const completedCount = sectionLessons.filter(l =>
    lessonProgress[l.id]?.is_completed
  ).length;
  const totalCount = sectionLessons.length;
  const sectionPercentage = totalCount > 0
    ? Math.round((completedCount / totalCount) * 100)
    : 0;

  return (
    <div key={section.id}>
      <div className="flex items-center justify-between p-3 bg-gray-100">
        <h3 className="font-semibold">{section.title}</h3>
        <span className="text-sm text-gray-600">
          {completedCount}/{totalCount} • {sectionPercentage}%
        </span>
      </div>
      {/* Lessons... */}
    </div>
  );
})}
```

#### 3. Estimated Time Remaining
```javascript
// Add to course progress summary
{courseProgress && (
  <div className="text-sm text-gray-600">
    <span>{formatTime(courseProgress.total_time_spent)} watched</span>
    <span className="mx-2">•</span>
    <span>{courseProgress.remaining_lessons} lessons remaining</span>
  </div>
)}
```

---

## 🔒 Drip Feed Implementation

### Database Schema (Already Exists)
**File:** [server/migrations/002_lms_drip_feed_content.sql](server/migrations/002_lms_drip_feed_content.sql)

**Note:** This migration uses `modules` instead of `sections`. Need to create adapted version.

### Drip Feed Types

#### 1. Absolute Date
Lesson available on specific date
```javascript
drip_feed_type: 'absolute'
drip_feed_absolute_date: '2025-02-01T00:00:00Z'
```

#### 2. Relative Days (After Enrollment)
Lesson available N days after student enrolls
```javascript
drip_feed_type: 'relative_days'
drip_feed_relative_days: 7  // Available 7 days after enrollment
```

#### 3. Relative Lessons (After Completion)
Lesson available after completing N previous lessons
```javascript
drip_feed_type: 'relative_lessons'
drip_feed_relative_lessons: 5  // Available after completing 5 lessons
```

### Instructor UI (Course Builder)
**File to create/modify:** `client/src/pages/teacher/CourseBuilder.jsx`

**Add drip feed controls to lesson form:**
```javascript
{/* Drip Feed Settings */}
<div className="border-t pt-4 mt-4">
  <label className="flex items-center gap-2 mb-3">
    <input
      type="checkbox"
      checked={lessonForm.dripFeedEnabled}
      onChange={(e) => setLessonForm({
        ...lessonForm,
        dripFeedEnabled: e.target.checked
      })}
    />
    <span className="font-medium">Enable Drip Feed</span>
  </label>

  {lessonForm.dripFeedEnabled && (
    <>
      <div className="mb-3">
        <label className="block text-sm font-medium mb-2">Release Type</label>
        <select
          value={lessonForm.dripFeedType}
          onChange={(e) => setLessonForm({
            ...lessonForm,
            dripFeedType: e.target.value
          })}
          className="w-full px-3 py-2 border rounded-md"
        >
          <option value="absolute">Specific Date</option>
          <option value="relative_days">Days After Enrollment</option>
          <option value="relative_lessons">After Completing Lessons</option>
        </select>
      </div>

      {lessonForm.dripFeedType === 'absolute' && (
        <div>
          <label className="block text-sm font-medium mb-2">Release Date</label>
          <input
            type="datetime-local"
            value={lessonForm.dripFeedAbsoluteDate}
            onChange={(e) => setLessonForm({
              ...lessonForm,
              dripFeedAbsoluteDate: e.target.value
            })}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
      )}

      {lessonForm.dripFeedType === 'relative_days' && (
        <div>
          <label className="block text-sm font-medium mb-2">Days After Enrollment</label>
          <input
            type="number"
            min="0"
            value={lessonForm.dripFeedRelativeDays}
            onChange={(e) => setLessonForm({
              ...lessonForm,
              dripFeedRelativeDays: parseInt(e.target.value)
            })}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
      )}

      {lessonForm.dripFeedType === 'relative_lessons' && (
        <div>
          <label className="block text-sm font-medium mb-2">Lessons to Complete First</label>
          <input
            type="number"
            min="0"
            value={lessonForm.dripFeedRelativeLessons}
            onChange={(e) => setLessonForm({
              ...lessonForm,
              dripFeedRelativeLessons: parseInt(e.target.value)
            })}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
      )}
    </>
  )}
</div>
```

### Student UI (Locked Lessons)
**File to modify:** `client/src/pages/CourseContent.jsx`

**Check if lesson is locked:**
```javascript
const isLessonLocked = (lesson) => {
  if (!lesson.drip_feed_enabled) return false;

  const now = new Date();

  switch (lesson.drip_feed_type) {
    case 'absolute':
      return new Date(lesson.drip_feed_absolute_date) > now;

    case 'relative_days':
      const enrollmentDate = new Date(enrollment.enrolled_at);
      const unlockDate = new Date(enrollmentDate);
      unlockDate.setDate(unlockDate.getDate() + lesson.drip_feed_relative_days);
      return unlockDate > now;

    case 'relative_lessons':
      const completedCount = Object.values(lessonProgress)
        .filter(p => p.is_completed).length;
      return completedCount < lesson.drip_feed_relative_lessons;

    default:
      return false;
  }
};

// In lesson rendering
{module.lessons?.map((lesson) => {
  const locked = isLessonLocked(lesson);

  return (
    <div
      className={`... ${locked ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      onClick={() => {
        if (!locked) {
          setActiveLesson(lesson);
        }
      }}
    >
      {/* Lock icon for locked lessons */}
      {locked && (
        <svg className="w-5 h-5 text-gray-400">
          <path d="M5 11v-1a7 7 0 1114 0v1M5 11a2 2 0 00-2 2v7a2 2 0 002 2h14a2 2 0 002-2v-7a2 2 0 00-2-2M5 11h14" />
        </svg>
      )}

      {/* Lesson title */}
      <span>{lesson.title}</span>

      {/* Lock reason */}
      {locked && (
        <span className="text-xs text-gray-500">
          {getLockReason(lesson)}
        </span>
      )}
    </div>
  );
})}
```

---

## 📝 Implementation Checklist

### Phase 1: Video Progress Tracking
- ✅ Create database schema
- ✅ Create backend API controller
- ✅ Create backend routes
- ✅ Register routes in server.js
- ⏳ **Run migration on database** (NEXT STEP)
- ⏳ Add progress tracking to video player
- ⏳ Add completion checkmarks to sidebar
- ⏳ Add "Mark as Complete" for text lessons
- ⏳ Add course progress bar to header
- ⏳ Test video resume functionality
- ⏳ Test auto-completion at 90%

### Phase 2: UI Polish
- ⏳ Add lesson status icons (completed, in progress, locked)
- ⏳ Add section progress summaries
- ⏳ Add estimated time remaining
- ⏳ Improve sidebar visual design
- ⏳ Add animations for progress updates
- ⏳ Add confetti or celebration on course completion

### Phase 3: Drip Feed (Optional)
- ⏳ Adapt drip feed migration for sections
- ⏳ Run drip feed migration
- ⏳ Add drip feed UI to course builder
- ⏳ Implement lock logic in student view
- ⏳ Add lock icons and tooltips
- ⏳ Test all drip feed types
- ⏳ Create cron job for schedule processing

---

## 🧪 Testing Guide

### Test Video Progress Tracking

1. **Login as student**
2. **Start watching a video**
3. **Watch for 30 seconds**
4. **Refresh the page**
5. **Expected:** Video resumes from 30 seconds
6. **Watch until 90% complete**
7. **Expected:** Green checkmark appears in sidebar

### Test Text Lesson Completion

1. **Open a text lesson**
2. **Click "Mark as Complete" button**
3. **Expected:** Green checkmark appears
4. **Expected:** Progress percentage increases

### Test Progress Bar

1. **Complete 5 out of 10 lessons**
2. **Expected:** Progress bar shows 50%
3. **Expected:** "5 of 10 lessons complete" displayed

---

## 🚀 Next Steps

**Immediate:**
1. Run the video progress migration (see instructions above)
2. Restart backend server
3. Test the API endpoints with Postman/curl
4. Implement frontend video progress tracking
5. Add completion checkmarks to sidebar

**Short Term:**
- Polish sidebar UI
- Add progress animations
- Test all completion scenarios

**Long Term:**
- Implement drip feed functionality
- Add course completion certificates
- Add progress analytics for instructors

---

## 📚 Related Files

- [VIDEO_PLAYBACK_FIX_COMPLETE.md](VIDEO_PLAYBACK_FIX_COMPLETE.md) - Video playback implementation
- [SESSION_COMPLETE_VIDEO_SYSTEM_WORKING.md](SESSION_COMPLETE_VIDEO_SYSTEM_WORKING.md) - Video system summary
- [server/migrations/video_progress_tracking.sql](server/migrations/video_progress_tracking.sql) - Database schema
- [server/controllers/videoProgressController.js](server/controllers/videoProgressController.js) - Backend API
- [server/routes/videoProgressRoutes.js](server/routes/videoProgressRoutes.js) - API routes
- [server/migrations/002_lms_drip_feed_content.sql](server/migrations/002_lms_drip_feed_content.sql) - Drip feed schema

---

**Ready to proceed with frontend implementation!** 🎯
