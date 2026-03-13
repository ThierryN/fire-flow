# Zoom API Testing Guide
**Last Updated**: October 26, 2025
**Status**: ✅ Ready for Testing

---

## 📋 Overview

This guide provides comprehensive instructions for testing the Zoom Server-to-Server OAuth integration with your School of the Priests LMS.

**Current Configuration**:
- API Type: Server-to-Server OAuth (Account Credentials Grant)
- Authentication: Basic Auth with Client ID:Client Secret (base64 encoded)
- Credentials Status: ✅ Configured in `.env`

---

## 🔐 Credentials Verification

### Current Configuration (.env)
```env
ZOOM_ACCOUNT_ID=YOUR_ZOOM_ACCOUNT_ID
ZOOM_CLIENT_ID=YOUR_ZOOM_S2S_CLIENT_ID
ZOOM_CLIENT_SECRET=YOUR_ZOOM_S2S_CLIENT_SECRET
ZOOM_USER_EMAIL=admin@schooloftheholyspirit.club
```

### Required Scopes (Verify in Zoom Dashboard)
Go to https://developers.zoom.us/marketplace and check your app has these scopes:
- ✅ `meeting:write` - Create meetings
- ✅ `meeting:read` - Read meeting details
- ✅ `meeting:write:admin` - Modify meetings as admin
- ✅ `user:read` - Read user information
- ✅ `webinar:write` - Create webinars (optional)
- ✅ `recording:read` - Access recordings

---

## 🚀 Quick Start Testing (5 minutes)

### Test 1: API Connection Test
```bash
# 1. Start your server
npm run dev

# 2. Test connection endpoint
curl -X GET http://localhost:5000/api/zoom/user \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"

# Expected Response (200):
{
  "status": "success",
  "data": {
    "id": "your_zoom_user_id",
    "email": "admin@schooloftheholyspirit.club",
    "first_name": "Your",
    "last_name": "Name"
  }
}
```

### Test 2: Create Meeting
```bash
curl -X POST http://localhost:5000/api/zoom/meetings \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Meeting - School of Priests",
    "startTime": "2025-11-15T14:00:00Z",
    "duration": 60,
    "type": "meeting"
  }'

# Expected Response (201):
{
  "status": "success",
  "data": {
    "id": "meeting_id_from_db",
    "title": "Test Meeting - School of Priests",
    "zoom_meeting_id": "zoom_meeting_number",
    "join_url": "https://zoom.us/j/...",
    "start_time": "2025-11-15T14:00:00Z",
    "duration": 60,
    "password": "meeting_password"
  }
}
```

### Test 3: Get Meeting
```bash
curl -X GET http://localhost:5000/api/zoom/meetings/MEETING_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected Response (200):
{
  "status": "success",
  "data": {
    "id": "meeting_id",
    "title": "Test Meeting - School of Priests",
    "zoom_meeting_id": "zoom_meeting_number",
    "host_id": "user_id",
    "start_time": "2025-11-15T14:00:00Z"
  }
}
```

---

## 🧪 Full Testing Workflow (30 minutes)

### Phase 1: Authentication Testing

#### Test 1.1: Verify Credentials
```javascript
// server/test-zoom-credentials.js
import axios from 'axios';

const ZOOM_ACCOUNT_ID = 'YOUR_ZOOM_ACCOUNT_ID';
const ZOOM_CLIENT_ID = 'YOUR_ZOOM_S2S_CLIENT_ID';
const ZOOM_CLIENT_SECRET = 'YOUR_ZOOM_S2S_CLIENT_SECRET';

async function testAuthentication() {
  try {
    const credentials = Buffer.from(
      `${ZOOM_CLIENT_ID}:${ZOOM_CLIENT_SECRET}`
    ).toString('base64');

    const response = await axios.post(
      `https://zoom.us/oauth/token?grant_type=account_credentials&account_id=${ZOOM_ACCOUNT_ID}`,
      {},
      {
        headers: {
          'Authorization': `Basic ${credentials}`,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );

    console.log('✅ Authentication Successful');
    console.log('Access Token:', response.data.access_token.substring(0, 20) + '...');
    console.log('Expires In:', response.data.expires_in, 'seconds');
    return response.data.access_token;
  } catch (error) {
    console.error('❌ Authentication Failed');
    console.error('Status:', error.response?.status);
    console.error('Error:', error.response?.data);
    throw error;
  }
}

testAuthentication();
```

**Run Test**:
```bash
node server/test-zoom-credentials.js
```

**Expected Output**:
```
✅ Authentication Successful
Access Token: eyJhbGciOiJIUzI1NiIsInR5cCI...
Expires In: 3600 seconds
```

---

#### Test 1.2: Verify API Access
```bash
# Get user info to verify API access
curl -X GET https://api.zoom.us/v2/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"

# Expected Response:
{
  "id": "user_id",
  "email": "admin@schooloftheholyspirit.club",
  "first_name": "Admin",
  "last_name": "User",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Phase 2: Meeting Management Testing

#### Test 2.1: Create a Test Meeting
```bash
MEETING_DETAILS=$(curl -X POST https://api.zoom.us/v2/users/me/meetings \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "School of Priests - Test Meeting",
    "type": 2,
    "start_time": "2025-11-15T14:00:00",
    "duration": 60,
    "timezone": "UTC",
    "settings": {
      "host_video": true,
      "participant_video": true,
      "join_before_host": false,
      "mute_upon_entry": false,
      "waiting_room": true
    }
  }')

echo "$MEETING_DETAILS" | jq .

# Expected Fields:
# - id (meeting number)
# - join_url
# - start_url
# - password
```

#### Test 2.2: List All Meetings
```bash
curl -X GET https://api.zoom.us/v2/users/me/meetings \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"

# Response should include:
# - meetings (array of meeting objects)
# - total_records (number of meetings)
# - page_count
```

#### Test 2.3: Get Specific Meeting
```bash
MEETING_ID="YOUR_MEETING_ID"

curl -X GET https://api.zoom.us/v2/meetings/$MEETING_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Expected Response includes:
# - Meeting details
# - Participants count
# - Recording status
# - Settings
```

#### Test 2.4: Update Meeting
```bash
MEETING_ID="YOUR_MEETING_ID"

curl -X PATCH https://api.zoom.us/v2/meetings/$MEETING_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Updated Meeting Title",
    "start_time": "2025-11-16T15:00:00",
    "duration": 90,
    "settings": {
      "waiting_room": false
    }
  }'

# Expected: 204 No Content (success)
```

#### Test 2.5: Delete Meeting
```bash
MEETING_ID="YOUR_MEETING_ID"

curl -X DELETE https://api.zoom.us/v2/meetings/$MEETING_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Expected: 204 No Content (success)
```

---

### Phase 3: Application-Level Testing

#### Test 3.1: Create Meeting via API
```bash
# Generate a JWT token first (use your auth mechanism)
JWT_TOKEN="your_app_jwt_token"

curl -X POST http://localhost:5000/api/zoom/meetings \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Advanced Bible Study - Week 5",
    "startTime": "2025-11-20T19:00:00Z",
    "duration": 120,
    "type": "meeting",
    "courseId": "course-uuid-here"
  }'
```

**Expected Response** (201):
```json
{
  "status": "success",
  "data": {
    "id": "db-meeting-id",
    "title": "Advanced Bible Study - Week 5",
    "host_id": "user-id",
    "course_id": "course-uuid",
    "zoom_meeting_id": "meeting-number",
    "join_url": "https://zoom.us/j/...",
    "password": "meeting-password",
    "start_time": "2025-11-20T19:00:00Z",
    "duration": 120,
    "type": "meeting"
  }
}
```

#### Test 3.2: Join Meeting
```bash
JWT_TOKEN="your_app_jwt_token"
MEETING_ID="db-meeting-id-from-test-3-1"

curl -X POST http://localhost:5000/api/zoom/meetings/$MEETING_ID/join \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response** (200):
```json
{
  "status": "success",
  "data": {
    "signature": "signature_for_zoom_sdk",
    "meetingNumber": "zoom-meeting-number",
    "apiKey": "your-api-key",
    "userName": "Your Name",
    "userEmail": "user@example.com",
    "password": "meeting-password",
    "role": 0
  }
}
```

#### Test 3.3: Get Meetings List
```bash
JWT_TOKEN="your_app_jwt_token"

curl -X GET http://localhost:5000/api/zoom/meetings \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Response** (200):
```json
{
  "status": "success",
  "results": 3,
  "data": [
    {
      "id": "meeting-1",
      "title": "Meeting 1",
      "zoom_meeting_id": "123456789",
      "host_id": "user-id",
      "start_time": "2025-11-20T19:00:00Z",
      "duration": 60
    },
    // ... more meetings
  ]
}
```

---

## 🔍 Troubleshooting

### Issue: "Zoom credentials not configured"
**Cause**: Missing environment variables
**Solution**:
```bash
# Check .env file has these variables:
echo $ZOOM_ACCOUNT_ID
echo $ZOOM_CLIENT_ID
echo $ZOOM_CLIENT_SECRET
echo $ZOOM_USER_EMAIL

# If missing, add to .env:
ZOOM_ACCOUNT_ID=YOUR_ZOOM_ACCOUNT_ID
ZOOM_CLIENT_ID=YOUR_ZOOM_S2S_CLIENT_ID
ZOOM_CLIENT_SECRET=YOUR_ZOOM_S2S_CLIENT_SECRET
ZOOM_USER_EMAIL=admin@schooloftheholyspirit.club
```

### Issue: "Failed to authenticate with Zoom"
**Cause**: Invalid credentials or network issue
**Solution**:
1. Verify credentials in Zoom Dashboard: https://developers.zoom.us/marketplace
2. Check if Basic Auth base64 encoding is correct:
   ```bash
   echo -n "CLIENT_ID:CLIENT_SECRET" | base64
   ```
3. Verify API endpoint is correct: `https://zoom.us/oauth/token`

### Issue: "Unauthorized to access meeting"
**Cause**: User doesn't have permission
**Solution**:
- Verify meeting host_id matches current user
- Check admin role has access to all meetings
- Verify course enrollment for course meetings

### Issue: "Access token expired"
**Cause**: Token older than 1 hour
**Solution**:
- getAccessToken() automatically refreshes tokens
- Check token expiration logic in zoom.js (line 32-34)
- Tokens expire in 1 hour, with 5-minute buffer for safety

---

## ✅ Testing Checklist

### Basic Setup
- [ ] .env file has all 4 Zoom variables
- [ ] npm packages installed: `axios`, `jwt-decode`
- [ ] Server can start without Zoom errors
- [ ] No console warnings about missing credentials

### Authentication
- [ ] Zoom credentials are valid
- [ ] Can generate access tokens from Zoom API
- [ ] Token expires properly after 1 hour
- [ ] Token auto-refresh works on subsequent requests

### Meeting Operations
- [ ] Can create new meetings via Zoom API
- [ ] Can retrieve meeting details
- [ ] Can list all user meetings
- [ ] Can update meeting information
- [ ] Can delete meetings

### Application Integration
- [ ] Can create meeting via `/api/zoom/meetings` endpoint
- [ ] Can retrieve meeting via `/api/zoom/meetings/:id`
- [ ] Can join meeting and get signature
- [ ] Can list user meetings
- [ ] Proper error handling for invalid meetings

### Authorization
- [ ] Students can only join enrolled courses' meetings
- [ ] Instructors can create/modify their own meetings
- [ ] Admins can manage all meetings
- [ ] Non-authorized users get 403 errors

### Database Integration
- [ ] Meeting created in database when Zoom API succeeds
- [ ] Meeting ID linked to Zoom meeting ID
- [ ] Meeting accessible via database queries
- [ ] Meeting deleted from database when removed from Zoom

---

## 🛠️ Test Scripts

### Create Test Meeting Script
**File**: `server/test-create-zoom-meeting.js`
```javascript
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE = 'https://api.zoom.us/v2';
const ZOOM_ACCOUNT_ID = process.env.ZOOM_ACCOUNT_ID;
const ZOOM_CLIENT_ID = process.env.ZOOM_CLIENT_ID;
const ZOOM_CLIENT_SECRET = process.env.ZOOM_CLIENT_SECRET;

async function getAccessToken() {
  const credentials = Buffer.from(
    `${ZOOM_CLIENT_ID}:${ZOOM_CLIENT_SECRET}`
  ).toString('base64');

  try {
    const response = await axios.post(
      `https://zoom.us/oauth/token?grant_type=account_credentials&account_id=${ZOOM_ACCOUNT_ID}`,
      {},
      {
        headers: {
          'Authorization': `Basic ${credentials}`,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    return response.data.access_token;
  } catch (error) {
    console.error('Failed to get access token:', error.response?.data);
    throw error;
  }
}

async function createTestMeeting() {
  try {
    console.log('🔄 Getting access token...');
    const accessToken = await getAccessToken();
    console.log('✅ Access token obtained');

    console.log('\n🔄 Creating meeting...');
    const response = await axios.post(
      `${API_BASE}/users/me/meetings`,
      {
        topic: `School of Priests Test Meeting - ${new Date().toLocaleString()}`,
        type: 2,
        start_time: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
        duration: 60,
        timezone: 'UTC',
        settings: {
          host_video: true,
          participant_video: true,
          join_before_host: false,
          mute_upon_entry: false,
          waiting_room: true,
          auto_recording: 'none'
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    );

    console.log('✅ Meeting created successfully!');
    console.log('\nMeeting Details:');
    console.log('- Meeting ID:', response.data.id);
    console.log('- Topic:', response.data.topic);
    console.log('- Join URL:', response.data.join_url);
    console.log('- Start URL:', response.data.start_url);
    console.log('- Password:', response.data.password);
    console.log('- Start Time:', response.data.start_time);
    console.log('- Duration:', response.data.duration, 'minutes');

    return response.data;
  } catch (error) {
    console.error('❌ Error:', error.response?.data || error.message);
    throw error;
  }
}

// Run test
createTestMeeting()
  .then(() => console.log('\n✅ Test completed successfully'))
  .catch(error => {
    console.error('\n❌ Test failed');
    process.exit(1);
  });
```

**Run Test**:
```bash
node server/test-create-zoom-meeting.js
```

---

## 📊 Monitoring

### Check Recent Meetings
```bash
curl https://api.zoom.us/v2/users/me/meetings \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" | jq '.meetings | sort_by(-.start_time) | .[0:5]'
```

### Check API Usage
Monitor API calls in Zoom Dashboard:
1. Go to https://developers.zoom.us/marketplace
2. Select your app
3. View "Usage" tab for API call metrics
4. Check rate limits (typically 100 calls/second)

---

## 🔒 Security Checklist

- [ ] Never expose Client Secret in frontend code
- [ ] Store credentials in `.env`, not in version control
- [ ] Add `.env` to `.gitignore`
- [ ] Rotate credentials regularly (recommended every 6 months)
- [ ] Use HTTPS for all API communications
- [ ] Validate user authorization before creating meetings
- [ ] Log API errors for debugging (don't expose to clients)
- [ ] Implement rate limiting on meeting creation endpoint
- [ ] Verify webhook signatures if using Zoom webhooks

---

## 📞 Support Resources

- **Zoom API Documentation**: https://developers.zoom.us/docs/api/
- **OAuth Documentation**: https://developers.zoom.us/docs/internal-apps/s2s-oauth/
- **API Reference**: https://developers.zoom.us/docs/api/rest/reference/
- **Troubleshooting Guide**: https://support.zoom.us/hc/en-us/articles/206175806

---

**Status**: ✅ Zoom API Integration Ready for Production Testing
