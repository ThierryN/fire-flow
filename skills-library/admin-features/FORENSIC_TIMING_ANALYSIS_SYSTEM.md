# Forensic Timing Analysis System - LMS Student Engagement Detection

## The Problem

Instructors had no way to detect students who were gaming the LMS completion system by rapidly clicking through lessons without actually engaging with content. Students could mark all lessons as "complete" in seconds, getting 100% course completion without watching videos or reading materials.

### Why It Was Hard

- No single metric can determine engagement — requires combining multiple signals
- Video lessons vs text lessons require different analysis logic
- Time tracking data (`time_spent`) was initially broken (always 0) due to a trigger bug
- Rapid-fire detection needs temporal analysis across lesson completions
- Must present complex data clearly without overwhelming instructors
- Architecture needed to work across two different admin pages (detail + course list)

### Impact

- Students could cheat course completion requirements
- Instructors couldn't identify disengaged students
- Course completion metrics were unreliable
- No data-driven way to flag academic dishonesty

---

## The Solution

### Architecture Overview

A **client-side forensic analysis system** that processes existing lesson progress data (already returned by `getStudentDetail` API) to compute per-lesson engagement verdicts.

```
┌─────────────────────────────────────────────────────────────┐
│  getStudentDetail API  →  Already returns all needed data:  │
│  first_accessed_at, completed_at, time_spent,               │
│  video_duration_ms, video_completion (per lesson)           │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│  computeForensicData(sections)  →  Shared Utility           │
│  • Per-lesson verdict (suspicious / warning / clean)        │
│  • Rapid-fire detection (temporal)                          │
│  • Summary stats + engagement score                         │
└─────────────┬───────────────────────────────────────────────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
┌──────────┐   ┌──────────────────┐
│  Modal   │   │  Batch Messaging │
│  (Detail)│   │  (Course List)   │
└──────────┘   └──────────────────┘
```

### Key Design Decision: No Backend Changes Needed

All forensic data is computed client-side from existing API response data. This avoids:
- New API endpoints
- Database schema changes
- Additional server load
- Migration complexity

### Verdict Logic (3-tier system)

#### Video/Audio Lessons
```javascript
// Calculate gap = completed_at - first_accessed_at
// Calculate ratio = gap / video_duration

// RED - SUSPICIOUS
if (gap < 10 seconds)           → "Instant click"
if (ratio < 10%)                → "X% of duration"
if (video_completion === 0%)    → "0% video watched"

// AMBER - WARNING
if (ratio < 50%)                → "X% of duration"
if (time_spent === 0)           → "No time tracked"
if (video >= 80% but ratio < 50% && time_spent === 0) → "No time tracked"

// GREEN - CLEAN
if (video >= 80% && time_spent > 0)  → "OK"
if (ratio >= 50%)                     → "OK"
```

#### Text/Quiz Lessons
```javascript
// AMBER - WARNING
if (gap < 3 seconds)                        → "Instant click"
if (time_spent === 0 && gap < 10 seconds)   → "Very fast"

// GREEN - CLEAN
everything else                             → "OK"
```

#### Rapid-Fire Detection (Cross-Lesson)
```javascript
// Sort completed lessons by completed_at timestamp
// If lesson N completed within 10 seconds of lesson N-1:
//   → Mark as rapid-fire
//   → Upgrade "clean" to "warning" with label "Rapid-fire"
```

### Engagement Score Formula
```javascript
engagementScore = Math.round((cleanCount / completedCount) * 100)
// 100% = all completed lessons are clean
// 0% = no completed lessons are clean
```

### Shared Utility Pattern

Created `client/src/utils/forensicAnalysis.js` with two exported functions:

```javascript
// Returns { rows: Array, summary: Object }
export function computeForensicData(sections) { ... }

// Returns plain-text string for messaging
export function buildForensicSummaryText(forensicData, studentName, courseTitle) { ... }
```

**Usage in Detail page:**
```javascript
import { computeForensicData, buildForensicSummaryText } from '../../utils/forensicAnalysis';

const forensicData = useMemo(() => computeForensicData(data?.lessons), [data?.lessons]);
```

**Usage in Course page (batch):**
```javascript
import { computeForensicData, buildForensicSummaryText } from '../../utils/forensicAnalysis';

const forensic = computeForensicData(detailRes.data?.lessons || []);
const summaryText = buildForensicSummaryText(forensic, student.name, courseTitle);
```

### Modal UI Design

- **Max width:** `max-w-6xl` (table needs horizontal space)
- **Dark theme:** `bg-[#1E293B]`, `border-slate-700/50`
- **Summary stats bar:** Color-coded counts (red/amber/green) + engagement score
- **Table columns:** Section, Lesson, Type, First Access, Completed, Gap, Expected Duration, Time Spent, Video %, Verdict
- **Verdict badges:** Color-coded (red/amber/green/gray)
- **Section grouping:** Lessons grouped by course sections
- **Actions:** Print, Export CSV, Attach to Message

### "Attach to Message" Flow

```javascript
// 1. Build plain-text summary
const summary = buildForensicSummaryText(forensicData, studentName, courseTitle);

// 2. Start or get conversation with student
const convResult = await startConversation(studentId);
const conversationId = convResult.data?.conversationId;

// 3. Send the forensic report as a message
await sendMessage(conversationId, { content: summary });

// 4. Navigate to the conversation
navigate(`/messages/${conversationId}`);
```

---

## Database Prerequisites

### Migration 131: Fix time_spent Tracking

The forensic analysis depends on accurate `time_spent` data in `lesson_progress`. Migration 131 fixes the `auto_complete_video_lesson()` trigger to always sync `total_watch_time_ms` from `video_progress` into `lesson_progress.time_spent`:

```sql
-- Trigger now ALWAYS upserts lesson_progress with time_spent
INSERT INTO lesson_progress (user_id, lesson_id, course_id, time_spent, ...)
VALUES (NEW.user_id, NEW.lesson_id, NEW.course_id,
        GREATEST(ROUND(NEW.total_watch_time_ms / 1000)::INTEGER, 0), ...)
ON CONFLICT (user_id, lesson_id) DO UPDATE SET
  time_spent = GREATEST(ROUND(NEW.total_watch_time_ms / 1000)::INTEGER, 0);

-- Backfill existing data
UPDATE lesson_progress lp SET time_spent = GREATEST(ROUND(vp.total_watch_time_ms / 1000)::INTEGER, 0)
FROM video_progress vp
WHERE vp.user_id = lp.user_id AND vp.lesson_id = lp.lesson_id
  AND vp.total_watch_time_ms > 0 AND lp.time_spent = 0;
```

---

## Testing the System

### Manual Testing Checklist
1. Navigate to Student Progress > select a course > click a student
2. Click "Forensic Analysis" button in header
3. Verify summary stats match expectations
4. Check video lessons with instant completions show "Suspicious" (red)
5. Check text lessons with fast completions show "Warning" (amber)
6. Check legitimately completed lessons show "OK" (green)
7. Test Print button (opens browser print dialog)
8. Test Export CSV (downloads .csv file)
9. Test Attach to Message (sends to student's inbox)
10. Test with student who has zero completions (empty state)

### Test Cases
- Student who clicked through everything → Low engagement score, many red/amber
- Student who watched all videos → High engagement score, mostly green
- Student with rapid-fire completions → Warning badges with "Rapid-fire" labels
- Student with no completions → "Not Completed" gray badges, 100% engagement (vacuously true)

---

## Prevention & Future Improvements

- Consider server-side enforcement (e.g., minimum lesson viewing time)
- Add forensic data to PDF report exports
- Trend analysis: track engagement score over time
- Automated alerts when engagement score drops below threshold

---

## Files Involved

| File | Role |
|------|------|
| `client/src/utils/forensicAnalysis.js` | Shared utility (verdict logic + text builder) |
| `client/src/pages/admin/StudentProgressDetail.jsx` | Modal UI + Attach to Message |
| `client/src/pages/admin/StudentProgressCourse.jsx` | Batch send + checkbox selection |
| `client/src/services/messagingApi.js` | startConversation + sendMessage API |
| `client/src/services/studentProgressApi.js` | getStudentDetail API |
| `server/controllers/studentProgressController.js` | Backend data (already had all fields) |
| `server/migrations/131_fix_time_spent_tracking.sql` | Fix time_spent trigger + backfill |

---

## Common Mistakes to Avoid

- Do NOT compute forensics on the server — frontend already has all the data
- Do NOT use `time_spent` alone — it was 0 for many records before migration 131
- Do NOT mark non-completed lessons as suspicious — they're simply "Not Completed"
- Do NOT treat rapid-fire as suspicious — it's a warning (could be quiz answers)
- Do NOT forget `useMemo` — forensic computation is O(n) per render

---

## Time to Implement

**6-8 hours** total across all features (utility + modal + batch + checkboxes)

## Difficulty Level

### Forensic Logic: 3/5
### Modal + Actions: 3/5
### Batch Messaging: 3/5
### Overall System: 4/5 (complexity comes from integration across pages)

---

**Author Notes:**
The key insight was that ALL forensic data was already returned by the existing `getStudentDetail` API. No backend changes were needed — just client-side analysis. The shared utility pattern (`forensicAnalysis.js`) was critical for enabling both the detail modal and batch messaging features without code duplication.

The verdict thresholds (10s instant, 10% ratio suspicious, 50% ratio warning) were calibrated against real production data from Carol Moultrie's SOZO course completions.
