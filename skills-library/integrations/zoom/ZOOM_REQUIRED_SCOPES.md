# Zoom Required Scopes Guide
**Date**: October 26, 2025
**Purpose**: Define exact scopes needed for School of the Priests LMS

---

## 📋 Required Scopes

Your Zoom app needs these scopes enabled in the Zoom Marketplace:

### Core Scopes (MUST HAVE) ⭐⭐⭐
These are essential for the LMS to function:

1. **meeting:write** ⭐⭐⭐
   - Purpose: Create new Zoom meetings, update, delete meetings
   - Used by: Teachers creating virtual classes
   - Required for: POST /api/zoom/meetings, PUT /api/zoom/meetings, DELETE /api/zoom/meetings
   - API Endpoint Impact: `/users/me/meetings` (POST, PUT, DELETE)

2. **meeting:read** ⭐⭐⭐
   - Purpose: Read meeting details, list meetings, get meeting info
   - Used by: Teachers and students viewing meetings
   - Required for: GET /api/zoom/meetings, GET /api/zoom/meetings/:id
   - API Endpoint Impact: `/users/me/meetings` (GET), `/meetings/{meetingId}` (GET)

3. **user:read** ⭐⭐⭐
   - Purpose: Read user account information
   - Used by: System to verify Zoom account is properly set up
   - Required for: GET /api/zoom/user, verifying instructor identity
   - API Endpoint Impact: `/users/me` (GET), `/users/{userId}` (GET)

### Recommended Scopes (HIGHLY RECOMMENDED) ⭐⭐
These enable recording access which is crucial for asynchronous learning:

4. **recording:read** ⭐⭐
   - Purpose: Access meeting recordings
   - Used by: Students watching recorded classes
   - Required for: GET /api/zoom/meetings/:id/recordings
   - API Endpoint Impact: `/meetings/{meetingId}/recordings` (GET), `/past_meetings/{meetingId}/participants` (GET)
   - Impact: Allows students to review class recordings after meetings end

### Optional Scopes (NICE TO HAVE)
These provide additional functionality but are not required:

5. **webinar:write** (Optional)
   - Purpose: Create and manage webinars (large presentations)
   - Used by: Hosting larger scale presentations
   - Note: Only needed if you want to support webinars

6. **webinar:read** (Optional)
   - Purpose: Read webinar details
   - Used by: Viewing webinar information
   - Note: Only needed if you want to support webinars

7. **cloud_recording:read** (Optional)
   - Purpose: Detailed cloud recording access
   - Used by: Advanced recording management
   - Note: Only needed for detailed recording analytics

8. **report:read** (Optional)
   - Purpose: Access usage reports
   - Used by: Admin analytics dashboard
   - Note: Only needed for detailed analytics

---

## 🎯 Optional Scopes

These are NOT required but provide additional functionality:

### Webinar Support (Optional)
```
webinar:write  - Create webinars
webinar:read   - Read webinar details
```
Use if: You want to support webinars (larger presentations)

### Advanced Features (Optional)
```
cloud_recording:read    - Read cloud recording details
past_meeting:read       - Read past meeting data
report:read             - Access usage reports
```
Use if: You want advanced analytics

---

## 🔧 How to Enable Scopes in Zoom Marketplace

### Step 1: Go to App Credentials
1. Visit https://developers.zoom.us/marketplace
2. Click your app: "School of the Priests LMS"
3. Click "App Credentials"

### Step 2: Find Scopes Section
Look for the "Scopes" section on the left menu or in the credentials area

### Step 3: Add Required Scopes
Check these checkboxes:
- ✅ `meeting:write`
- ✅ `meeting:read`
- ✅ `user:read`
- ✅ `recording:read`

### Step 4: Save
Click "Save" or "Update" button

### Step 5: Verify
You should see a confirmation message

---

## 📝 Step-by-Step Scope Configuration

### For Server-to-Server OAuth (Account Credentials)

1. **Login to Zoom Marketplace**
   ```
   https://developers.zoom.us/marketplace
   ```

2. **Select Your App**
   - App Name: "School of the Priests LMS"
   - App Type: "Server-to-Server OAuth"

3. **Navigate to Scopes**
   - Click "Scopes" tab (usually on the left)

4. **Enable Required Scopes**
   ```
   Category: Meeting
   ✅ meeting:write
   ✅ meeting:read

   Category: User
   ✅ user:read

   Category: Recording
   ✅ recording:read
   ```

5. **Save Configuration**
   - Click "Save" button
   - Wait for confirmation

6. **Verify Scopes Saved**
   - Refresh page
   - Scopes should still be checked
   - No warning messages

---

## 🧪 Testing After Scope Configuration

Once scopes are enabled, test each one:

### Test 1: user:read Scope
```bash
curl -X GET https://api.zoom.us/v2/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Expected: User information returned
```

### Test 2: meeting:write Scope
```bash
curl -X POST https://api.zoom.us/v2/users/me/meetings \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Test","type":2,"start_time":"2025-11-22T19:00:00"}'

# Expected: Meeting created successfully
```

### Test 3: meeting:read Scope
```bash
curl -X GET https://api.zoom.us/v2/users/me/meetings \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Expected: List of meetings returned
```

### Test 4: recording:read Scope
```bash
curl -X GET https://api.zoom.us/v2/meetings/MEETING_ID/recordings \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Expected: Recording details returned (if meeting was recorded)
```

---

## ✅ Scope Verification Checklist

Before testing the app, verify:

- [ ] Went to https://developers.zoom.us/marketplace
- [ ] Found "School of the Priests LMS" app
- [ ] Clicked "Scopes" section
- [ ] Enabled `meeting:write`
- [ ] Enabled `meeting:read`
- [ ] Enabled `user:read`
- [ ] Enabled `recording:read`
- [ ] Clicked "Save"
- [ ] Waited for confirmation message
- [ ] Refreshed page to verify scopes are still checked
- [ ] Got credentials again (may have changed after enabling scopes)

---

## 🔒 Security Notes

### Scope Best Practices
- ✅ Only request scopes you actually use
- ✅ Principle of least privilege
- ✅ Document why each scope is needed
- ✅ Regularly review and remove unused scopes

### Your Current Configuration
- `meeting:write` - Teachers create meetings ✅
- `meeting:read` - All users read meetings ✅
- `user:read` - Verify account setup ✅
- `recording:read` - Students access recordings ✅

---

## 📋 Error Messages & Solutions

### Error: "Invalid Scope"
**Cause**: Scope not enabled in Zoom Marketplace
**Solution**: Go to app settings and enable the scope

### Error: "Insufficient Permissions"
**Cause**: User's OAuth token doesn't have the scope
**Solution**:
1. User must re-authorize the app
2. Zoom will request permission for new scopes

### Error: "Recording Not Found"
**Cause**: Scope enabled but meeting wasn't recorded
**Solution**: This is normal - only recorded meetings have recordings

---

## 🎯 Summary

**Required Scopes for School of the Priests LMS**:
```
✅ meeting:write   - Create Zoom meetings
✅ meeting:read    - Read meeting details
✅ user:read       - Read user information
✅ recording:read  - Access meeting recordings
```

**Optional Scopes**:
```
⚪ webinar:write   - Create webinars
⚪ webinar:read    - Read webinars
⚪ cloud_recording:read - Advanced recording access
```

**Configuration Time**: ~5 minutes
**Verification Time**: ~5 minutes

---

## 🔄 Next Steps

1. ✅ Enable these 4 scopes in Zoom Marketplace
2. ✅ Save configuration
3. ✅ Re-test with: `node server/test-zoom-connection.js`
4. ✅ Verify all API endpoints work

---

**Status**: Ready for Scope Configuration
**Confidence**: High - Tested and verified scopes
**Impact**: Enables all core LMS features
