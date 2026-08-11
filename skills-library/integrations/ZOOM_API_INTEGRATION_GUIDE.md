# Zoom API Integration Guide - Server-to-Server OAuth
**Last Updated**: October 26, 2025
**API Type**: Account-Level OAuth (Server-to-Server)
**Status**: Configured & Ready to Implement

---

## 🎯 YOUR ZOOM API TYPE

### ✅ You Have: **Server-to-Server OAuth** (Account-Level)

**Credentials Type:**
```
Account ID (JWT Subject):  YOUR_ZOOM_ACCOUNT_ID
Client ID:                  YOUR_ZOOM_S2S_CLIENT_ID
Client Secret:              YOUR_ZOOM_S2S_CLIENT_SECRET
```

**What This Means:**
- Uses OAuth 2.0 authentication
- Server-to-server communication (backend only)
- Not user-specific OAuth (no user login required)
- Direct API calls from your backend
- Perfect for: Creating meetings on behalf of users, automatic meeting scheduling

---

## 🔐 HOW SERVER-TO-SERVER OAUTH WORKS

### Authentication Flow
```
1. Your server generates a JWT token
   ├─ Include: Account ID, Client ID
   ├─ Sign with: Client Secret
   └─ Expiry: Usually 1 hour

2. Send JWT to Zoom OAuth endpoint
   ├─ Endpoint: https://zoom.us/oauth/token
   ├─ Grant Type: urn:ietf:params:oauth:grant-type:jwt-bearer
   └─ Response: Access Token

3. Use Access Token for API calls
   ├─ Header: Authorization: Bearer ACCESS_TOKEN
   ├─ Valid for: 1 hour
   └─ Auto-refresh when needed

4. Make API requests
   ├─ Create meetings
   ├─ Update meetings
   ├─ Get user details
   └─ Add participants
```

---

## 📚 COMPARISON: ZOOM API TYPES

### Your Option: Server-to-Server OAuth ✅
**When to Use:**
- Backend calls Zoom API directly
- No user login needed
- Automated meeting creation
- Batch operations
- Admin functions

**Pros:**
- ✅ No user authentication required
- ✅ Direct server communication
- ✅ Can schedule for anyone
- ✅ Perfect for e-commerce (auto-create meetings on purchase)
- ✅ Most secure for backend

**Cons:**
- ❌ Can't access user's personal meetings
- ❌ Works at account level only

**Best For**: Creating meetings for purchased courses/events

---

### Other Options (Not What You Have)

**Option 1: OAuth 2.0 (User Login)**
```
Credentials: Client ID + Client Secret (without Account ID)
When: User needs to login with Zoom
How: Redirect to Zoom login → User grants permission → Get access token
Uses: User's personal Zoom account, access user's meetings
```

**Option 2: JWT (Legacy - Deprecated)**
```
Credentials: API Key + API Secret (different format)
When: Legacy Zoom apps
Status: Being phased out (Zoom recommends Server-to-Server OAuth instead)
```

**Option 3: API Key + Secret (Direct)**
```
Credentials: API Key + API Secret
When: Simple authentication
Uses: Direct API calls without OAuth flow
```

---

## 🔧 IMPLEMENTATION GUIDE

### Step 1: Install Required Package
```bash
npm install jsonwebtoken
```

### Step 2: Create Zoom Configuration File
**File**: `server/config/zoom.js`

```javascript
import jwt from 'jsonwebtoken';
import axios from 'axios';

class ZoomConfig {
  constructor() {
    this.accountId = process.env.ZOOM_ACCOUNT_ID;
    this.clientId = process.env.ZOOM_CLIENT_ID;
    this.clientSecret = process.env.ZOOM_CLIENT_SECRET;
    this.userEmail = process.env.ZOOM_USER_EMAIL;

    this.baseURL = 'https://zoom.us/oauth/token';
    this.apiBaseURL = 'https://api.zoom.us/v2';
    this.accessToken = null;
    this.tokenExpiry = null;
  }

  /**
   * Generate JWT Token
   * This token proves to Zoom that you are who you claim to be
   */
  generateJWT() {
    const payload = {
      iss: this.clientId,      // Issuer = Your Client ID
      sub: this.accountId,      // Subject = Your Account ID
      aud: 'https://api.zoom.us',
      exp: Math.floor(Date.now() / 1000) + 3600 // Expires in 1 hour
    };

    return jwt.sign(payload, this.clientSecret, { algorithm: 'HS256' });
  }

  /**
   * Get Access Token
   * Exchange JWT for short-lived access token
   */
  async getAccessToken() {
    try {
      // Check if we have a valid cached token
      if (this.accessToken && this.tokenExpiry && Date.now() < this.tokenExpiry) {
        return this.accessToken;
      }

      const jwtToken = this.generateJWT();

      const response = await axios.post(this.baseURL, null, {
        params: {
          grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
          assertion: jwtToken
        }
      });

      this.accessToken = response.data.access_token;
      // Token is valid for 3600 seconds, refresh 5 minutes before expiry
      this.tokenExpiry = Date.now() + (3600 - 300) * 1000;

      return this.accessToken;
    } catch (error) {
      console.error('Error getting Zoom access token:', error.response?.data || error.message);
      throw new Error('Failed to authenticate with Zoom');
    }
  }

  /**
   * Make API Request to Zoom
   */
  async request(method, endpoint, data = null) {
    try {
      const token = await this.getAccessToken();

      const config = {
        method,
        url: `${this.apiBaseURL}${endpoint}`,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      };

      if (data) {
        config.data = data;
      }

      const response = await axios(config);
      return response.data;
    } catch (error) {
      console.error(`Zoom API Error (${method} ${endpoint}):`, error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Create a Meeting
   */
  async createMeeting(options) {
    const meetingData = {
      topic: options.topic || 'New Meeting',
      type: 2, // 2 = Scheduled meeting
      start_time: options.startTime, // ISO 8601 format: 2025-10-26T14:00:00Z
      duration: options.duration || 60, // minutes
      timezone: options.timezone || 'UTC',
      settings: {
        host_video: true,
        participant_video: true,
        join_before_host: true,
        waiting_room: false,
        audio: 'both' // 'both' = phone + computer audio
      }
    };

    const response = await this.request('POST', '/users/me/meetings', meetingData);
    return response;
  }

  /**
   * Get Meeting Details
   */
  async getMeeting(meetingId) {
    return await this.request('GET', `/meetings/${meetingId}`);
  }

  /**
   * Update Meeting
   */
  async updateMeeting(meetingId, options) {
    const updateData = {
      topic: options.topic,
      start_time: options.startTime,
      duration: options.duration
    };

    return await this.request('PUT', `/meetings/${meetingId}`, updateData);
  }

  /**
   * Delete/Cancel Meeting
   */
  async deleteMeeting(meetingId) {
    return await this.request('DELETE', `/meetings/${meetingId}`);
  }

  /**
   * Get Meeting Registrants
   */
  async getMeetingRegistrants(meetingId) {
    return await this.request('GET', `/meetings/${meetingId}/registrants`);
  }

  /**
   * Add Meeting Registrant
   */
  async addRegistrant(meetingId, registrant) {
    const data = {
      email: registrant.email,
      first_name: registrant.firstName,
      last_name: registrant.lastName,
      action: 'create' // 'create' = send join link automatically
    };

    return await this.request('POST', `/meetings/${meetingId}/registrants`, data);
  }
}

export default new ZoomConfig();
```

### Step 3: Create Zoom Controller
**File**: `server/controllers/zoomMeetingsController.js`

```javascript
import asyncHandler from '../middleware/asyncHandler.js';
import { ApiError } from '../middleware/errorHandler.js';
import zoomConfig from '../config/zoom.js';
import sql from '../config/sql.js';

/**
 * Create Zoom Meeting
 * POST /api/zoom-meetings
 */
export const createZoomMeeting = asyncHandler(async (req, res, next) => {
  const { topic, startTime, duration, courseId, productId } = req.body;
  const userId = req.user.id;

  if (!topic || !startTime || !courseId) {
    return next(new ApiError('Topic, startTime, and courseId are required', 400));
  }

  try {
    // Create meeting on Zoom
    console.log('Creating Zoom meeting:', {
      topic,
      startTime,
      duration
    });

    const meeting = await zoomConfig.createMeeting({
      topic,
      startTime: new Date(startTime).toISOString(),
      duration: duration || 60
    });

    console.log('✅ Zoom meeting created:', meeting.id);

    // Save to database
    const dbMeeting = await sql`
      INSERT INTO virtual_meetings (
        created_by,
        course_id,
        product_id,
        meeting_type,
        provider,
        title,
        description,
        scheduled_at,
        duration_minutes,
        zoom_meeting_id,
        zoom_join_url,
        status
      )
      VALUES (
        ${userId},
        ${courseId},
        ${productId || null},
        'course',
        'zoom',
        ${topic},
        ${topic},
        ${new Date(startTime).toISOString()},
        ${duration || 60},
        ${meeting.id},
        ${meeting.join_url},
        'scheduled'
      )
      RETURNING *
    `;

    res.status(201).json({
      success: true,
      data: dbMeeting[0],
      message: 'Zoom meeting created successfully'
    });
  } catch (error) {
    console.error('Error creating Zoom meeting:', error);
    return next(new ApiError(error.message || 'Failed to create Zoom meeting', 500));
  }
});

/**
 * Get Zoom Meeting Details
 * GET /api/zoom-meetings/:meetingId
 */
export const getZoomMeeting = asyncHandler(async (req, res, next) => {
  const { meetingId } = req.params;

  try {
    // Get from Zoom
    const meeting = await zoomConfig.getMeeting(meetingId);

    res.status(200).json({
      success: true,
      data: meeting
    });
  } catch (error) {
    console.error('Error fetching Zoom meeting:', error);
    return next(new ApiError('Failed to fetch Zoom meeting', 500));
  }
});

/**
 * Add Registrant to Meeting
 * POST /api/zoom-meetings/:meetingId/registrants
 */
export const addRegistrant = asyncHandler(async (req, res, next) => {
  const { meetingId } = req.params;
  const { email, firstName, lastName } = req.body;

  if (!email || !firstName || !lastName) {
    return next(new ApiError('Email, firstName, and lastName are required', 400));
  }

  try {
    const registrant = await zoomConfig.addRegistrant(meetingId, {
      email,
      firstName,
      lastName
    });

    res.status(201).json({
      success: true,
      data: registrant,
      message: 'Registrant added successfully'
    });
  } catch (error) {
    console.error('Error adding registrant:', error);
    return next(new ApiError('Failed to add registrant', 500));
  }
});
```

### Step 4: Create Routes
**File**: `server/routes/zoomRoutes.js`

```javascript
import express from 'express';
import * as zoomController from '../controllers/zoomMeetingsController.js';
import { protect } from '../middleware/auth.js';

const router = express.Router();

// All routes require authentication
router.use(protect);

/**
 * Create Zoom meeting
 * POST /api/zoom-meetings
 */
router.post('/', zoomController.createZoomMeeting);

/**
 * Get meeting details
 * GET /api/zoom-meetings/:meetingId
 */
router.get('/:meetingId', zoomController.getZoomMeeting);

/**
 * Add registrant to meeting
 * POST /api/zoom-meetings/:meetingId/registrants
 */
router.post('/:meetingId/registrants', zoomController.addRegistrant);

export default router;
```

### Step 5: Register Routes in server.js
```javascript
import zoomRoutes from './routes/zoomRoutes.js';

// ... in your app setup
app.use('/api/zoom-meetings', zoomRoutes);
```

---

## 📝 IMPLEMENTATION EXAMPLES

### Create a Meeting When Course Is Purchased
```javascript
// In your payment controller
async function createMeetingForPurchase(courseId, productId, userId) {
  try {
    // Get course details
    const course = await sql`
      SELECT * FROM courses WHERE id = ${courseId}
    `;

    // Create Zoom meeting
    const meeting = await zoomConfig.createMeeting({
      topic: `${course[0].title} - Live Session`,
      startTime: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days from now
      duration: 60
    });

    // Save to database
    await sql`
      INSERT INTO virtual_meetings (...)
      VALUES (...)
    `;

    // Send confirmation email with join link
    await sendEmail({
      to: user.email,
      subject: `Join ${course[0].title}`,
      html: `<a href="${meeting.join_url}">Join Meeting</a>`
    });

  } catch (error) {
    console.error('Error creating meeting:', error);
  }
}
```

### Get User's Upcoming Meetings
```javascript
async function getUserMeetings(userId) {
  const meetings = await sql`
    SELECT * FROM virtual_meetings
    WHERE created_by = ${userId}
      AND scheduled_at > NOW()
    ORDER BY scheduled_at ASC
  `;

  return meetings;
}
```

---

## 🧪 TESTING YOUR INTEGRATION

### Test 1: Can We Get Access Token?
```bash
curl -X POST https://zoom.us/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer" \
  -d "assertion=YOUR_JWT_TOKEN_HERE"

# Should return: { "access_token": "..." }
```

### Test 2: Can We Create a Meeting?
```javascript
// In Node.js
import zoomConfig from './server/config/zoom.js';

const meeting = await zoomConfig.createMeeting({
  topic: 'Test Meeting',
  startTime: new Date().toISOString(),
  duration: 30
});

console.log('Meeting created:', meeting);
console.log('Join URL:', meeting.join_url);
```

### Test 3: Can We Get Meeting Details?
```javascript
const meeting = await zoomConfig.getMeeting('123456789');
console.log('Meeting details:', meeting);
```

---

## 🔐 SECURITY BEST PRACTICES

### 1. Never Expose Client Secret
```javascript
// ❌ BAD
const secret = 'YOUR_ZOOM_S2S_CLIENT_SECRET';
res.json({ secret }); // NEVER!

// ✅ GOOD
// Keep in .env, only used server-side
const secret = process.env.ZOOM_CLIENT_SECRET;
```

### 2. Validate All Inputs
```javascript
if (!topic || topic.trim().length === 0) {
  throw new Error('Topic cannot be empty');
}

if (new Date(startTime) < new Date()) {
  throw new Error('Start time must be in the future');
}

if (duration < 15 || duration > 720) {
  throw new Error('Duration must be between 15 and 720 minutes');
}
```

### 3. Refresh Tokens Automatically
```javascript
// Caching + auto-refresh (already implemented in config/zoom.js)
if (this.accessToken && this.tokenExpiry && Date.now() < this.tokenExpiry) {
  return this.accessToken; // Reuse cached token
}
// Otherwise get new token
```

### 4. Use HTTPS Only
```javascript
if (process.env.NODE_ENV === 'production') {
  // Ensure all Zoom API calls are HTTPS
  // Zoom API is HTTPS by default
}
```

---

## 🐛 TROUBLESHOOTING

### "Invalid client_id"
```
❌ Check: Is ZOOM_CLIENT_ID correct in .env?
✅ Fix: Copy from Zoom Marketplace exactly, no extra spaces
```

### "Invalid client secret"
```
❌ Check: Is ZOOM_CLIENT_SECRET correct?
✅ Fix: Copy from Zoom Marketplace exactly, no extra spaces
```

### "Invalid JWT format"
```
❌ Check: Is JWT signing algorithm correct? (Must be HS256)
✅ Fix: Use jwt.sign(payload, secret, { algorithm: 'HS256' })
```

### "Meeting creation failed with 4xx error"
```
❌ Check: Is start_time in correct format? (ISO 8601: 2025-10-26T14:00:00Z)
✅ Fix: Use new Date(startTime).toISOString()

❌ Check: Is duration within 15-720 minutes?
✅ Fix: Validate duration before sending
```

### "Token expired while creating meeting"
```
❌ Check: Are you caching and reusing tokens?
✅ Fix: Token caching is automatic in zoom.js config
```

---

## 📚 USEFUL ZOOM API ENDPOINTS

### Meetings
- `POST /users/me/meetings` - Create meeting
- `GET /meetings/{meetingId}` - Get meeting
- `PUT /meetings/{meetingId}` - Update meeting
- `DELETE /meetings/{meetingId}` - Delete meeting
- `GET /users/{userId}/meetings` - List user's meetings
- `GET /meetings/{meetingId}/registrants` - Get registrants
- `POST /meetings/{meetingId}/registrants` - Add registrant

### Users
- `GET /users/{userId}` - Get user info
- `GET /users` - List users

### Reports
- `GET /report/meetings` - Get meeting reports
- `GET /report/users/{userId}/meetings` - Get user's meeting reports

---

## 🎯 INTEGRATION WITH E-COMMERCE

### Use Case: Virtual Course Meeting
```
1. Student purchases "Live Course" product
   ↓
2. Payment processing succeeds
   ↓
3. Create Zoom meeting automatically
   ├─ Topic: Course name
   ├─ Start Time: Next week same time
   └─ Duration: 2 hours
   ↓
4. Store meeting details in database
   ├─ zoom_meeting_id
   ├─ zoom_join_url
   └─ course_id
   ↓
5. Send confirmation email with join link
   ├─ Join URL
   ├─ Meeting time
   └─ Passcode
   ↓
6. Student clicks link → Joins Zoom meeting
   ↓
7. Post-meeting: Send recording to student
```

---

## ✅ CHECKLIST

- [ ] Account ID in .env: `YOUR_ZOOM_ACCOUNT_ID`
- [ ] Client ID in .env: `YOUR_ZOOM_S2S_CLIENT_ID`
- [ ] Client Secret in .env: `YOUR_ZOOM_S2S_CLIENT_SECRET`
- [ ] Create `server/config/zoom.js`
- [ ] Create `server/controllers/zoomMeetingsController.js`
- [ ] Create `server/routes/zoomRoutes.js`
- [ ] Register routes in `server/server.js`
- [ ] Install `jsonwebtoken` package
- [ ] Test createMeeting() function
- [ ] Add meeting database triggers
- [ ] Create Zoom meeting on purchase (payment controller)
- [ ] Send join link to customer (email)
- [ ] Test with real meeting creation

---

**Status**: ✅ **READY TO IMPLEMENT**
**API Type**: Server-to-Server OAuth ✅
**Next Step**: Create config/zoom.js file
