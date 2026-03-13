# Zoom Recordings Implementation Guide

**Date**: January 17, 2026
**Status**: Complete
**Branch**: student-beautification

---

## Overview

This guide documents the Zoom cloud recordings integration for the MERN Community LMS, allowing students to watch past class recordings directly within their enrolled courses.

---

## Architecture

### Backend Components

| File | Purpose |
|------|---------|
| `server/config/zoom.js` | OAuth-based Zoom API configuration with recordings endpoints |
| `server/controllers/zoomController.js` | Controller with recording endpoints |
| `server/routes/zoomRoutes.js` | API routes for recordings |

### Frontend Components

| File | Purpose |
|------|---------|
| `client/src/components/video/ZoomRecordingPlayer.jsx` | Main recordings display component |
| `client/src/pages/CourseContent.jsx` | Course page with recordings tab |

---

## API Endpoints

### Get Meeting Recordings
```
GET /api/zoom/meetings/:id/recordings
```
- **Access**: Authenticated users (host, admin, or enrolled students)
- **Returns**: Recording files with play URLs

### Get Course Recordings
```
GET /api/zoom/courses/:courseId/recordings
```
- **Access**: Enrolled students, instructors, admins
- **Returns**: All recordings for a course's past Zoom meetings

### Toggle Recording Settings
```
PATCH /api/zoom/meetings/:id/recording
```
- **Access**: Host or Admin only
- **Body**: `{ enabled: boolean, type: 'cloud' | 'local' | 'none' }`
- **Purpose**: Enable/disable auto-recording for a scheduled meeting

### Control Live Recording
```
POST /api/zoom/meetings/:id/recording/control
```
- **Access**: Host or Admin only
- **Body**: `{ action: 'start' | 'pause' | 'resume' | 'stop' }`
- **Purpose**: Control recording during an active meeting

---

## How It Works

### 1. Recording Storage
Recordings are stored in Zoom Cloud (Zoom's servers). The LMS only stores:
- Meeting metadata in `zoom_meetings` table
- `zoom_meeting_id` reference for API calls

### 2. Playback Flow
```
1. Student clicks "Class Recordings" in sidebar
2. Frontend calls GET /api/zoom/courses/:courseId/recordings
3. Backend queries zoom_meetings table for ended meetings
4. For each meeting, calls Zoom API to get recording files
5. Returns formatted list with play URLs
6. Student clicks "Watch" - opens Zoom's hosted player
```

### 3. Recording Toggle Options
When creating or updating meetings:
```javascript
// Enable cloud recording
{ enableRecording: true }  // or { auto_recording: 'cloud' }

// Enable local recording (host's computer)
{ auto_recording: 'local' }

// Disable recording
{ enableRecording: false }  // or { auto_recording: 'none' }
```

---

## Zoom API Functions

### getMeetingRecordings(meetingId)
```javascript
// In server/config/zoom.js
export const getMeetingRecordings = async (meetingId) => {
  const accessToken = await getAccessToken();
  const response = await axios.get(
    `${ZOOM_API_BASE}/meetings/${meetingId}/recordings`,
    { headers: { 'Authorization': `Bearer ${accessToken}` } }
  );
  return response.data;
};
```

### updateMeetingRecordingSettings(meetingId, autoRecording)
```javascript
// Options: 'cloud', 'local', 'none'
export const updateMeetingRecordingSettings = async (meetingId, autoRecording = 'cloud') => {
  await axios.patch(
    `${ZOOM_API_BASE}/meetings/${meetingId}`,
    { settings: { auto_recording: autoRecording } },
    { headers: { 'Authorization': `Bearer ${accessToken}` } }
  );
};
```

### controlLiveRecording(meetingId, action)
```javascript
// Actions: 'start', 'pause', 'resume', 'stop'
export const controlLiveRecording = async (meetingId, action) => {
  const actionMap = {
    start: 'recording.start',
    pause: 'recording.pause',
    resume: 'recording.resume',
    stop: 'recording.stop',
  };

  await axios.patch(
    `${ZOOM_API_BASE}/live_meetings/${meetingId}/events`,
    { method: actionMap[action] },
    { headers: { 'Authorization': `Bearer ${accessToken}` } }
  );
};
```

### Convenience Functions
```javascript
export const enableRecording = (meetingId) => updateMeetingRecordingSettings(meetingId, 'cloud');
export const disableRecording = (meetingId) => updateMeetingRecordingSettings(meetingId, 'none');
```

---

## Required Zoom Scopes

For Server-to-Server OAuth apps:

| Scope | Purpose |
|-------|---------|
| `recording:read` | Access meeting recordings |
| `meeting:read` | Read meeting details |
| `meeting:write` | Create/update meetings |
| `user:read` | Verify account setup |

---

## Frontend Component Usage

### In Course Content Page
```jsx
import ZoomRecordingPlayer from '../components/video/ZoomRecordingPlayer';

// Show recordings for a course
<ZoomRecordingPlayer courseId={courseId} />

// Show recordings for a specific meeting
<ZoomRecordingPlayer meetingId={meetingId} />
```

### Component Features
- Lists all available recordings
- Shows meeting title, date, duration
- Displays password if protected
- Expandable to show individual recording files
- Opens Zoom's hosted player for playback

---

## Testing

### Toggle Recording via API
```bash
# Enable cloud recording for a meeting
curl -X PATCH "http://localhost:5000/api/zoom/meetings/MEETING_ID/recording" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "type": "cloud"}'

# Disable recording
curl -X PATCH "http://localhost:5000/api/zoom/meetings/MEETING_ID/recording" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### Control Live Recording
```bash
# Start recording (meeting must be in progress)
curl -X POST "http://localhost:5000/api/zoom/meetings/MEETING_ID/recording/control" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'

# Pause recording
curl -X POST "..." -d '{"action": "pause"}'

# Resume recording
curl -X POST "..." -d '{"action": "resume"}'

# Stop recording
curl -X POST "..." -d '{"action": "stop"}'
```

### Get Course Recordings
```bash
curl -X GET "http://localhost:5000/api/zoom/courses/COURSE_ID/recordings" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Troubleshooting

### "No recordings available"
- Meeting must be ended (status = 'ended')
- Recordings take 1-2 hours to process after meeting ends
- Meeting must have been recorded (`auto_recording: 'cloud'`)

### "Scope errors"
- Verify `recording:read` scope is enabled in Zoom Marketplace
- Regenerate access token after adding scopes

### "Meeting is not currently in progress"
- Live recording control only works during active meetings
- Check meeting status before attempting to control recording

### "Invalid access token"
- Check ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, ZOOM_ACCOUNT_ID in .env
- Token may have expired - system auto-refreshes but check logs

---

## Security Considerations

1. **Access Control**: Only enrolled students can view course recordings
2. **Password Protection**: Recording passwords are displayed for protected content
3. **No Direct Downloads**: We link to Zoom's player, not raw files
4. **Authorization Flow**: Each API call verifies user enrollment
5. **Host/Admin Only**: Recording toggle requires host or admin role

---

## Files Reference

```
server/config/zoom.js                              - Zoom API functions
server/controllers/zoomController.js               - API endpoints
server/routes/zoomRoutes.js                        - Route definitions
client/src/components/video/ZoomRecordingPlayer.jsx - Frontend component
client/src/pages/CourseContent.jsx                 - Course page integration
```

---

**Status**: Ready for Testing
**Next Step**: Create a test meeting with cloud recording enabled, conduct it, let it end, wait for processing, and verify recordings appear in course content.
