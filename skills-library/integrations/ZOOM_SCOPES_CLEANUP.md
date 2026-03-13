# Zoom Scopes Cleanup Guide
**Purpose**: Remove unnecessary scopes, keep only what the LMS needs
**Date**: October 26, 2025

---

## ⭐ Scopes You MUST Keep (Minimum Required)

These are the ONLY scopes needed for the LMS to work:

```
✅ KEEP THESE 4:
  • meeting:write      - Create/update/delete meetings
  • meeting:read       - View meeting details
  • user:read          - Read user account info
  • recording:read     - Access meeting recordings
```

---

## 🗑️ Scopes You CAN Safely Remove

All of these can be removed safely (they won't affect LMS functionality):

### Admin/User Management (Remove)
```
❌ REMOVE:
  • user:write:user:admin
  • user:update:user:admin
  • user:delete:user:admin
  • user:update:status:admin
  • user:update:password:admin
  • user:read:list_users:admin
  • user:read:list_users:master
  • (all other user:* scopes)
```

### Assistant Management (Remove)
```
❌ REMOVE:
  • user:read:list_assistants:admin
  • user:write:assistant:admin
  • user:delete:assistant:admin
  • (all other assistant scopes)
```

### Profile/Account Management (Remove)
```
❌ REMOVE:
  • user:write:profile_picture:admin
  • user:delete:profile_picture:admin
  • user:read:token:admin
  • user:delete:token:admin
  • user:read:zak:admin
  • (all other user profile scopes)
```

### Webinar Scopes (Remove if not using webinars)
```
❌ REMOVE:
  • webinar:read (if not hosting webinars)
  • webinar:write (if not hosting webinars)
  • webinar:* (all webinar scopes)
```

### Chat/Team Chat (Remove)
```
❌ REMOVE:
  • team_chat:* (all chat scopes)
  • message:* (all message scopes)
```

### Event Management (Remove)
```
❌ REMOVE:
  • zoom_events:* (all event scopes)
```

### Dashboard/Reporting (Remove if not needed)
```
❌ REMOVE (OPTIONAL):
  • dashboard:* (if you don't need detailed analytics)
  • report:* (if you don't need usage reports)
```

### Cloud Recording Advanced (Remove)
```
❌ REMOVE:
  • cloud_recording:* (keep only the basic ones)
  • archiving:* (if not using)
```

### Other Scopes (Remove)
```
❌ REMOVE:
  • device:*
  • group:*
  • tsp:*
  • calendar:*
  • sip_phone:*
  • visitor_management:*
  • tracking_field:*
  • zoom_node:*
  • qss:*
  • video_mgmt:*
  • division:*
  • data_request:*
  • clips:*
  • workflow:*
  • whiteboard:*
  • scheduler:*
  • imchat:*
  • app:*
  • role:*
  • information_barrier:*
  • billing:*
  • pac:*
  • archiving:*
```

---

## 📋 How to Clean Up Scopes

### Step 1: Go to Zoom Marketplace
```
https://developers.zoom.us/marketplace
```

### Step 2: Click Your App
Find: "School of the Priests LMS"

### Step 3: Go to Scopes Tab
Click "Scopes" in the left menu

### Step 4: Uncheck Unnecessary Scopes

**Process**:
1. Look through all enabled (checked) scopes
2. For each scope NOT in the "KEEP" list above
3. Uncheck it
4. Click Save after each section

**Scopes Section** (typically organized by category):
- User Scopes → uncheck all except user:read
- Meeting Scopes → KEEP meeting:write and meeting:read, uncheck others
- Recording Scopes → KEEP recording:read, uncheck others
- Webinar → uncheck all (unless you use webinars)
- Chat → uncheck all
- Team Chat → uncheck all
- Events → uncheck all
- Dashboard → uncheck all (optional)
- Reports → uncheck all (optional)
- Everything else → uncheck all

### Step 5: Final Check

After cleanup, you should have ONLY:
```
✅ meeting:write
✅ meeting:read
✅ user:read
✅ recording:read
```

---

## 🧪 Testing After Cleanup

Once cleaned up, test again:

```bash
cd server
node test-zoom-connection.js
```

Should still work perfectly because you kept all essential scopes.

---

## 💡 Why Clean Up?

**Benefits**:
- ✅ Better security (fewer permissions granted)
- ✅ Principle of least privilege
- ✅ Cleaner app configuration
- ✅ Easier to understand what your app does
- ✅ Reduces attack surface if credentials leak

**No Downside**:
- The LMS will work exactly the same
- No functionality lost
- Easier to manage long-term

---

## 📊 Before & After

**Before Cleanup**:
```
Scopes: 400+ enabled
Includes: Admin controls, chat, events, webinars, etc.
```

**After Cleanup**:
```
Scopes: 4 enabled
- meeting:write (create meetings)
- meeting:read (view meetings)
- user:read (verify account)
- recording:read (access recordings)
```

---

## ⚠️ Don't Remove These!

```
🚨 CRITICAL - DO NOT REMOVE:
✅ meeting:write
✅ meeting:read
✅ user:read
✅ recording:read
```

If you remove any of these, Zoom integration will break!

---

## 🔄 If You Remove by Mistake

If you accidentally remove a scope:

1. Go back to Zoom Marketplace
2. Click your app
3. Go to Scopes
4. Re-enable the scope
5. Click Save
6. Test: `node server/test-zoom-connection.js`

---

## 📝 Quick Reference

**Remove Everything EXCEPT**:
- [ ] ✅ meeting:write
- [ ] ✅ meeting:read
- [ ] ✅ user:read
- [ ] ✅ recording:read

Uncheck everything else.

---

## ✨ Summary

1. Keep 4 essential scopes
2. Remove 400+ unnecessary scopes
3. Test with: `node server/test-zoom-connection.js`
4. Platform works exactly the same
5. Much more secure

**Estimated Time**: 10 minutes

---

**Ready to Clean Up?** Go to https://developers.zoom.us/marketplace and start unchecking! 🎯
