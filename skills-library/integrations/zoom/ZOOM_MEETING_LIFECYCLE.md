# Zoom Meeting Lifecycle - Complete Example
**Last Updated**: October 26, 2025
**Purpose**: Demonstrate complete meeting workflow from creation to recording retrieval

---

## 📚 Table of Contents
1. [Meeting Creation](#meeting-creation)
2. [Meeting Management](#meeting-management)
3. [Student Participation](#student-participation)
4. [Recording & Analytics](#recording--analytics)
5. [Real-World Scenarios](#real-world-scenarios)

---

## 🎯 Meeting Creation

### Scenario: Teacher Creates a New Course Meeting

**API Endpoint**: `POST /api/zoom/meetings`
**Authentication**: JWT Token (Teacher/Instructor role)
**Database**: Links meeting to course and instructor

#### Request Example
```bash
curl -X POST http://localhost:5000/api/zoom/meetings \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Advanced Bible Study - Week 5",
    "description": "In-depth study of Psalm 42-43 with commentary",
    "startTime": "2025-11-22T19:00:00Z",
    "duration": 120,
    "type": "meeting",
    "courseId": "550e8400-e29b-41d4-a716-446655440000",
    "timezone": "America/Chicago"
  }'
```

#### Response (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": "db-meeting-uuid-1",
    "title": "Advanced Bible Study - Week 5",
    "description": "In-depth study of Psalm 42-43 with commentary",
    "host_id": "teacher-uuid",
    "course_id": "550e8400-e29b-41d4-a716-446655440000",
    "zoom_meeting_id": 1234567890,
    "join_url": "https://zoom.us/j/1234567890",
    "start_url": "https://zoom.us/s/1234567890",
    "password": "secure_password_123",
    "start_time": "2025-11-22T19:00:00Z",
    "duration": 120,
    "type": "meeting",
    "created_at": "2025-10-26T14:30:00Z"
  }
}
```

#### What Happened Behind the Scenes
1. ✅ Verified teacher is authenticated and authorized
2. ✅ Checked subscription has available Zoom minutes
3. ✅ Called Zoom API to create meeting: `/users/me/meetings`
4. ✅ Zoom returned meeting number, URLs, and password
5. ✅ Saved meeting record to database with Zoom ID reference
6. ✅ Linked meeting to course and instructor

---

## 📊 Meeting Management

### Scenario 1: Teacher Updates Meeting Time

**API Endpoint**: `PUT /api/zoom/meetings/:id`
**Authorization**: Only meeting host or admin

#### Request
```bash
MEETING_ID="db-meeting-uuid-1"

curl -X PUT http://localhost:5000/api/zoom/meetings/$MEETING_ID \
  -H "Authorization: Bearer TEACHER_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "startTime": "2025-11-23T20:00:00Z",
    "title": "Advanced Bible Study - Week 5 (RESCHEDULED)"
  }'
```

#### Response (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": "db-meeting-uuid-1",
    "title": "Advanced Bible Study - Week 5 (RESCHEDULED)",
    "start_time": "2025-11-23T20:00:00Z",
    "updated_at": "2025-10-26T14:35:00Z"
  }
}
```

#### Behind the Scenes
1. ✅ Verified user is meeting host
2. ✅ Called Zoom API `PATCH /meetings/{meetingId}` with new time
3. ✅ Updated database record
4. ✅ Zoom automatically notifies registered participants via email

---

### Scenario 2: Get All Teacher Meetings

**API Endpoint**: `GET /api/zoom/meetings`
**Returns**: All meetings created by current user

#### Request
```bash
curl -X GET http://localhost:5000/api/zoom/meetings \
  -H "Authorization: Bearer TEACHER_JWT"
```

#### Response (200 OK)
```json
{
  "status": "success",
  "results": 5,
  "data": [
    {
      "id": "meeting-1",
      "title": "Advanced Bible Study - Week 5",
      "course_id": "course-uuid",
      "course_title": "School of the Priests",
      "start_time": "2025-11-22T19:00:00Z",
      "duration": 120,
      "host_id": "teacher-uuid",
      "zoom_meeting_id": 1234567890,
      "join_url": "https://zoom.us/j/1234567890",
      "participants_count": 0,
      "status": "upcoming"
    },
    {
      "id": "meeting-2",
      "title": "Q&A Session",
      "start_time": "2025-11-15T15:00:00Z",
      "duration": 60,
      "participants_count": 23,
      "status": "ended"
    }
  ]
}
```

---

### Scenario 3: Cancel a Meeting

**API Endpoint**: `DELETE /api/zoom/meetings/:id`
**Authorization**: Only meeting host or admin

#### Request
```bash
MEETING_ID="db-meeting-uuid-2"

curl -X DELETE http://localhost:5000/api/zoom/meetings/$MEETING_ID \
  -H "Authorization: Bearer TEACHER_JWT"
```

#### Response (200 OK)
```json
{
  "status": "success",
  "data": null,
  "message": "Meeting deleted successfully. Participants have been notified."
}
```

#### Behind the Scenes
1. ✅ Verified authorization
2. ✅ Called Zoom API to delete meeting
3. ✅ Removed from database
4. ✅ Zoom sent cancellation email to all registered participants

---

## 👥 Student Participation

### Scenario 1: Student Joins Meeting

**Flow**: Student clicks "Join Meeting" button on lesson page

#### Step 1: Request Join Permission
**API Endpoint**: `POST /api/zoom/meetings/:id/join`
**Authorization**: Any authenticated user

```bash
MEETING_ID="db-meeting-uuid-1"

curl -X POST http://localhost:5000/api/zoom/meetings/$MEETING_ID/join \
  -H "Authorization: Bearer STUDENT_JWT" \
  -H "Content-Type: application/json"
```

#### Step 2: Server Validates Access
- ✅ Check if student is enrolled in the course
- ✅ Check if meeting has started (or within 15 minutes)
- ✅ Generate secure Zoom signature for the student

#### Step 3: Response with Join Credentials
```json
{
  "status": "success",
  "data": {
    "signature": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "meetingNumber": 1234567890,
    "apiKey": "API_KEY_HERE",
    "userName": "Ahmed Student",
    "userEmail": "ahmed@example.com",
    "password": "meeting_password",
    "role": 0
  }
}
```

#### Step 4: Frontend Uses Signature
```javascript
// client/src/pages/CourseContent.jsx example
import { ZoomMtg } from '@zoomus/websdk';

async function joinZoomMeeting(meetingId) {
  // Get signature from backend
  const response = await fetch(`/api/zoom/meetings/${meetingId}/join`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });

  const { data } = await response.json();

  // Configure Zoom
  ZoomMtg.init({
    leaveUrl: '/dashboard',
    isSupportAV: true,
    success: () => {
      ZoomMtg.join({
        signature: data.signature,
        meetingNumber: data.meetingNumber,
        userName: data.userName,
        userEmail: data.userEmail,
        passWord: data.password
      });
    }
  });
}
```

---

### Scenario 2: Attendance Tracking

**API Endpoint**: `POST /api/zoom/meetings/:id/attendance`
**Purpose**: Record when students join/leave (for analytics)

#### Teacher Starts Meeting - System Auto-Tracks

```javascript
// When student joins, Zoom SDK fires event
ZoomMtg.onmeetingstatuschange = (status) => {
  if (status === 'in_meeting') {
    // Send attendance record to backend
    await fetch(`/api/zoom/meetings/${meetingId}/attendance`, {
      method: 'POST',
      body: JSON.stringify({
        action: 'join',
        userId: studentId
      }),
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
};
```

#### Request Format
```bash
curl -X POST http://localhost:5000/api/zoom/meetings/meeting-1/attendance \
  -H "Authorization: Bearer TEACHER_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "join",
    "userId": "550e8400-e29b-41d4-a716-446655440001"
  }'
```

#### Response
```json
{
  "status": "success",
  "data": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440001",
      "user_name": "Ahmed Student",
      "join_time": "2025-11-22T19:05:00Z",
      "leave_time": null,
      "duration_minutes": 55,
      "attended": true
    },
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440002",
      "user_name": "Sara Student",
      "join_time": "2025-11-22T19:00:00Z",
      "leave_time": "2025-11-22T20:50:00Z",
      "duration_minutes": 110,
      "attended": true
    }
  ]
}
```

---

## 📹 Recording & Analytics

### Scenario 1: Get Meeting Recording

**API Endpoint**: `GET /api/zoom/meetings/:id/recordings`
**When Available**: 1-2 hours after meeting ends

#### Request
```bash
curl -X GET http://localhost:5000/api/zoom/meetings/meeting-1/recordings \
  -H "Authorization: Bearer STUDENT_JWT"
```

#### Response (Recording Available)
```json
{
  "status": "success",
  "data": {
    "recordingAvailable": true,
    "recordingUrl": "https://zoom.us/rec/share/...",
    "password": "recording_password",
    "duration_minutes": 115,
    "recording_type": "video",
    "size_mb": 450,
    "created_at": "2025-11-22T21:00:00Z"
  }
}
```

#### Response (Recording Not Ready)
```json
{
  "status": "success",
  "data": {
    "recordingAvailable": false,
    "message": "Recording is being processed. Please check again in 30 minutes."
  }
}
```

---

### Scenario 2: Add Questions During Meeting

**API Endpoint**: `POST /api/zoom/meetings/:id/questions`
**Purpose**: Students ask questions in chat, saved for later review

#### Request
```bash
curl -X POST http://localhost:5000/api/zoom/meetings/meeting-1/questions \
  -H "Authorization: Bearer STUDENT_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does 'gnosis' mean in verse 3?",
    "isPublic": true
  }'
```

#### Response (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": "question-uuid-1",
    "user_id": "student-uuid",
    "user_name": "Ahmed Student",
    "question": "What does 'gnosis' mean in verse 3?",
    "isPublic": true,
    "timestamp": "2025-11-22T19:25:00Z",
    "answer": null,
    "isAnswered": false
  }
}
```

---

### Scenario 3: Teacher Answers Questions

**API Endpoint**: `PUT /api/zoom/meetings/:id/questions/:questionId`
**Can Be Done**: During meeting or after via recorded review

#### Request
```bash
curl -X PUT http://localhost:5000/api/zoom/meetings/meeting-1/questions/question-uuid-1 \
  -H "Authorization: Bearer TEACHER_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "answer": "Gnosis (Greek: γνῶσις) means 'knowledge' or 'understanding' in a spiritual sense..."
  }'
```

#### Response (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": "question-uuid-1",
    "question": "What does 'gnosis' mean in verse 3?",
    "answer": "Gnosis (Greek: γνῶσις) means 'knowledge'...",
    "isAnswered": true,
    "answered_at": "2025-11-22T20:45:00Z"
  }
}
```

---

## 🌍 Real-World Scenarios

### Complete Flow: Weekly Class Setup

**Timeline**: Monday-Friday leading up to Saturday class

#### Monday: Teacher Creates Meeting for Upcoming Saturday

```bash
# Create meeting for Saturday 7 PM
curl -X POST http://localhost:5000/api/zoom/meetings \
  -H "Authorization: Bearer TEACHER_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "School of the Priests - Week 42 Class",
    "startTime": "2025-11-22T19:00:00",
    "duration": 120,
    "courseId": "school-of-priests-uuid",
    "type": "meeting"
  }'
```

#### Saturday: Before Class - Students See Meeting Link
- Student logs in and sees meeting in dashboard
- Clicks "Join Meeting" button 5 minutes before start
- System validates enrollment and generates signature
- Student joins via Zoom

#### Saturday: During Class (Real-Time)
- Teacher lectures for 90 minutes
- Students ask questions in chat
- Attendance automatically tracked
- Meeting recorded by Zoom

#### Saturday: After Class - Within 2 Hours
- Zoom finishes processing recording
- Recording available in meeting details
- Students can review the recording
- Students can see answers to Q&A

#### Sunday: Teacher Review
- Teacher reviews attendance report
- Checks which students attended and for how long
- Can see Q&A exchange
- Can mark attendance as complete for grading

#### For Next Week
- Teacher uses same course meeting link
- Updates time and topic for next session
- Meeting automatically available to all enrolled students

---

### Integration with Student Dashboard

**What Students See**:
```json
{
  "upcomingMeetings": [
    {
      "id": "meeting-1",
      "title": "Advanced Bible Study - Week 5",
      "course": "School of the Priests",
      "startTime": "2025-11-22T19:00:00Z",
      "status": "in_progress",
      "actionButton": "Join Now",
      "timeLeft": "30 minutes"
    }
  ],
  "pastMeetings": [
    {
      "id": "meeting-2",
      "title": "Q&A Session",
      "course": "School of the Priests",
      "endTime": "2025-11-15T16:00:00Z",
      "status": "ended",
      "actionButton": "Watch Recording",
      "recordingUrl": "https://zoom.us/rec/share/...",
      "questionsAsked": 12,
      "questionsAnswered": 11
    }
  ]
}
```

---

## 🔄 Error Handling Examples

### When Student Tries to Join Before Meeting Starts

```bash
curl -X POST http://localhost:5000/api/zoom/meetings/meeting-1/join \
  -H "Authorization: Bearer STUDENT_JWT"
```

**Response (400 Bad Request)** - More than 15 minutes early:
```json
{
  "status": "error",
  "message": "This meeting has not started yet. You can join 15 minutes before the scheduled start time.",
  "meetingStartsAt": "2025-11-22T19:00:00Z",
  "minutesUntilStart": 45
}
```

---

### When Student Not Enrolled in Course

```bash
curl -X POST http://localhost:5000/api/zoom/meetings/meeting-1/join \
  -H "Authorization: Bearer OTHER_STUDENT_JWT"
```

**Response (403 Forbidden)**:
```json
{
  "status": "error",
  "message": "You are not authorized to join this meeting. Please enroll in the course first.",
  "requiredCourse": "School of the Priests",
  "enrollmentUrl": "/courses/550e8400-e29b-41d4-a716-446655440000/enroll"
}
```

---

## 📈 Monitoring & Troubleshooting

### View All Meetings (Admin Dashboard)
```bash
curl -X GET http://localhost:5000/api/zoom/meetings?limit=50&page=1 \
  -H "Authorization: Bearer ADMIN_JWT"
```

### Check API Health
```bash
# Test Zoom connectivity
curl -X GET http://localhost:5000/api/zoom/user \
  -H "Authorization: Bearer ADMIN_JWT"
```

Expected: Returns admin user info from Zoom

### Monitor Failed Meetings
Check application logs for:
- `Zoom create meeting error:` - Meeting creation failed
- `Zoom authentication error:` - Credentials issue
- `Zoom API rate limit:` - Too many requests

---

## ✅ Meeting Lifecycle Checklist

- [ ] Create meeting (teacher initiates)
- [ ] Students enroll in course
- [ ] Students see meeting in dashboard
- [ ] 15 minutes before: Students can join
- [ ] During: Attendance tracked, questions recorded
- [ ] After: Recording processed and available
- [ ] Students access recording
- [ ] Teacher reviews Q&A
- [ ] Teacher can update future meeting times
- [ ] Administrator can view all meetings and analytics

---

**Status**: ✅ Complete Meeting Lifecycle Documented
