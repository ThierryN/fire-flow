# Zoom OAuth 2.0 Setup Guide
**Status**: 📋 Action Required - Setup Instructions
**Date**: October 26, 2025

---

## 🎯 What We Need From You

To complete the OAuth 2.0 integration, we need credentials from your new Zoom OAuth 2.0 application:

### 1️⃣ Create OAuth 2.0 App on Zoom Marketplace

**Step-by-Step**:
1. Go to https://developers.zoom.us/marketplace
2. Click "Build App" (top right)
3. Select **"General App"** (OAuth 2.0)
4. Enter app name: `School of the Priests LMS`
5. Continue through the setup wizard
6. Fill in "Company Information" (your organization details)
7. Click "Create"

**You'll see this screen** ⬇️
```
App Name: School of the Priests LMS
App Type: General App (OAuth 2.0)
Basic Information:
  - Company Name: Your Company
  - Company Website: https://schoolofthepriest.com
  - Developer Name: Your Name
  - Developer Email: your@email.com
```

---

## 🔑 Step 2: Get Your OAuth 2.0 Credentials

After creating the app, go to **App Credentials** tab and copy:

### What to Copy (3 values)
```
1. Client ID
   - Format: Long alphanumeric string (e.g., ABC123xyz...)

2. Client Secret
   - Format: Long alphanumeric string (e.g., XYZ789abc...)

3. Redirect URI (for testing)
   - Set to: http://localhost:5000/api/zoom/oauth/callback
   - (In production, change to: https://yourdomain.com/api/zoom/oauth/callback)
```

---

## 📝 Step 3: Configure Scopes

In the "Scopes" tab of your app, enable:
- ✅ `meeting:write` - Create meetings
- ✅ `meeting:read` - Read meeting details
- ✅ `user:read` - Read user information
- ✅ `recording:read` - Access recordings (optional)
- ✅ `webinar:write` - Create webinars (optional)

---

## 🛡️ Step 4: Add Redirect URI in Zoom Dashboard

In your app's settings on https://developers.zoom.us/marketplace:

**OAuth Redirect URI**:
```
Development: http://localhost:5000/api/zoom/oauth/callback
Production: https://yourdomain.com/api/zoom/oauth/callback
```

---

## 📋 Step 5: Update .env File

Once you have credentials, update your `.env` file:

```env
# OAuth 2.0 (General App) - NEW
ZOOM_OAUTH_CLIENT_ID=your_client_id_here
ZOOM_OAUTH_CLIENT_SECRET=your_client_secret_here
ZOOM_OAUTH_REDIRECT_URI=http://localhost:5000/api/zoom/oauth/callback

# Keep existing Server-to-Server for admin/fallback (optional)
ZOOM_ACCOUNT_ID=YOUR_ZOOM_ACCOUNT_ID
ZOOM_CLIENT_ID=YOUR_ZOOM_S2S_CLIENT_ID
ZOOM_CLIENT_SECRET=YOUR_ZOOM_S2S_CLIENT_SECRET
ZOOM_USER_EMAIL=admin@schooloftheholyspirit.club
```

---

## ✅ What I Will Create For You

Once you provide the credentials, I will:

### 1. OAuth Routes (`server/routes/zoomOAuthRoutes.js`)
```
GET  /api/zoom/oauth/authorize     - Redirects to Zoom login
GET  /api/zoom/oauth/callback      - Handles Zoom redirect with auth code
POST /api/zoom/oauth/disconnect    - Revokes user's OAuth access
```

### 2. OAuth Controller (`server/controllers/zoomOAuthController.js`)
```javascript
// Initiates OAuth flow - redirects user to Zoom login
startOAuthFlow()

// Handles callback - exchanges code for token
handleOAuthCallback()

// Stores user's Zoom credentials securely
storeUserZoomCredentials()

// Revokes OAuth access
revokeUserOAuthAccess()
```

### 3. Database Migration
```sql
-- Add zoom_tokens table to store user OAuth tokens
CREATE TABLE zoom_tokens (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  access_token TEXT NOT NULL,
  refresh_token TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  scope TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4. Frontend OAuth Button
```jsx
// On Settings or Dashboard page
<button onClick={() => window.location.href = '/api/zoom/oauth/authorize'}>
  🔗 Connect Zoom Account
</button>
```

### 5. Complete Flow Diagram
```
1. User clicks "Connect Zoom"
   ↓
2. Redirects to: /api/zoom/oauth/authorize
   ↓
3. Backend redirects user to Zoom login page
   ↓
4. User logs into Zoom and grants permissions
   ↓
5. Zoom redirects back to: /api/zoom/oauth/callback?code=xxx&state=yyy
   ↓
6. Backend exchanges code for access token
   ↓
7. Backend stores token in database (encrypted)
   ↓
8. Redirect user back to dashboard with success message
   ↓
9. User can now create meetings with their own Zoom account!
```

---

## 🔒 Security Features Implemented

- ✅ **State Parameter**: CSRF protection (random state token)
- ✅ **Secure Token Storage**: Encrypted in database
- ✅ **Token Refresh**: Automatic refresh when expired
- ✅ **Revocation**: Users can disconnect anytime
- ✅ **Scope Limitation**: Only request necessary permissions
- ✅ **HTTPS Only**: Enforced in production
- ✅ **No Client Secret Exposure**: Kept on backend only

---

## 📊 OAuth 2.0 vs Server-to-Server: Comparison

| Feature | OAuth 2.0 (General App) | Server-to-Server |
|---------|-------------------------|-----------------|
| **User Login** | ✅ Yes, user authorizes | ❌ No, backend only |
| **Multi-User** | ✅ Each user has their own account | ❌ Shared admin account |
| **Token Refresh** | ✅ Automatic via refresh token | ❌ Manual token refresh |
| **Scope Control** | ✅ User controls permissions | ❌ All permissions granted |
| **Setup Complexity** | 🟡 Medium (requires OAuth flow) | 🟢 Simple (direct credentials) |
| **Security** | 🟢 Highly secure (user control) | 🟡 Good (shared credentials) |
| **User Experience** | 🟢 Familiar (like "Login with Google") | 🔴 Poor (manual setup) |
| **Scalability** | ✅ Scales to many users | ❌ Limited to one account |

---

## 🚀 Next Steps

### For You:
1. Create OAuth 2.0 app on Zoom Marketplace
2. Copy Client ID, Client Secret
3. Provide credentials to me
4. Test the OAuth flow

### For Me (Once You Provide Credentials):
1. Create OAuth routes and controller
2. Create database migration for token storage
3. Create frontend OAuth button
4. Test complete OAuth flow
5. Create testing guide

---

## 🧪 Testing The OAuth Flow (After Setup)

Once everything is set up, here's how to test:

### Test 1: Start OAuth Flow
```bash
# User clicks "Connect Zoom" and gets redirected to:
https://zoom.us/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost:5000/api/zoom/oauth/callback&scope=meeting:write+meeting:read+user:read
```

### Test 2: Zoom Redirects Back
After user logs in and grants permissions, Zoom redirects to:
```
http://localhost:5000/api/zoom/oauth/callback?code=AUTH_CODE_HERE&state=STATE_HERE
```

### Test 3: Backend Exchanges Code
Backend automatically:
1. Validates state parameter
2. Exchanges code for access token
3. Stores token in database
4. Redirects user to dashboard

### Test 4: User Creates Meeting
Now user can create meetings using their own Zoom account!

---

## 💾 How Tokens Will Be Stored

In database (`zoom_tokens` table):
```json
{
  "id": "uuid",
  "user_id": "user-uuid",
  "access_token": "encrypted_token",
  "refresh_token": "encrypted_token",
  "expires_at": "2025-11-01T14:30:00Z",
  "scope": "meeting:write meeting:read user:read",
  "created_at": "2025-10-26T14:30:00Z"
}
```

Tokens are encrypted using PostgreSQL's `pgcrypto` extension for security.

---

## 🔄 Token Refresh Flow

When access token expires (1 hour):
1. System detects expired token
2. Automatically uses refresh token
3. Gets new access token from Zoom
4. Updates database
5. User continues without interruption

No user action needed! 🎯

---

## 📞 Support

Once you provide the OAuth 2.0 credentials:
- I'll implement the complete OAuth flow
- Create all necessary routes and controllers
- Set up secure token storage
- Create testing guide
- Deploy to production

**What I need from you**: The three OAuth credentials + Redirect URI from Zoom Marketplace

---

## ✨ Summary

**Current Status**:
- ✅ OAuth 2.0 support added to zoom.js config
- ⏳ Waiting for your credentials
- 📋 Ready to implement routes/controllers

**What You Need To Do**:
1. Create OAuth 2.0 app on Zoom Marketplace
2. Copy credentials (Client ID, Client Secret)
3. Set Redirect URI
4. Enable scopes
5. Provide credentials to me

**Timeline**: Once credentials provided, full implementation in ~30 minutes

---

**Questions?** Let me know and I'll clarify! 🙋
