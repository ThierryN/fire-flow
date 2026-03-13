# Zoom Credential Fix - Step by Step
**Status**: 🔴 URGENT - Credentials Don't Match
**Issue**: Account ID and Client Secret are identical (they shouldn't be)

---

## 🚨 Problem Identified

Your current credentials:
```
Account ID:    YOUR_ZOOM_CLIENT_SECRET
Client ID:     YOUR_ZOOM_CLIENT_ID
Client Secret: YOUR_ZOOM_CLIENT_SECRET
                ↑
         SAME AS ACCOUNT ID! This is wrong.
```

**Why It's Failing**:
- Account ID and Client Secret must be DIFFERENT
- Zoom rejected the request with "invalid_request" error
- The credentials are likely copied incorrectly

---

## ✅ How to Fix (5 minutes)

### Step 1: Go to Zoom Marketplace
```
https://developers.zoom.us/marketplace
```

### Step 2: Click Your App
Look for: "School of the Priests LMS"

### Step 3: Go to App Credentials Tab
Click "App Credentials" on the left menu

### Step 4: Find These 3 Values

**Look for a section that says "Credentials" or "OAuth" with:**

```
📋 Account ID
   └─ Format: Long alphanumeric (like: ABC123xyzDEF456...)
   └─ Location: Copy this field labeled "Account ID"

📋 Client ID
   └─ Format: Alphanumeric (like: YOUR_ZOOM_CLIENT_ID)
   └─ Location: Copy this field labeled "Client ID"

📋 Client Secret
   └─ Format: Long string (NOT the same as Account ID!)
   └─ Location: Copy this field labeled "Client Secret"
   └─ ⚠️ This should look DIFFERENT from Account ID
```

### Step 5: Copy Exact Values
- **Important**: Copy with NO extra spaces
- **Paste directly** into .env
- **Verify** they are different from each other

### Step 6: Update .env File
```env
ZOOM_ACCOUNT_ID=<paste Account ID here>
ZOOM_CLIENT_ID=<paste Client ID here>
ZOOM_CLIENT_SECRET=<paste Client Secret here>
```

**Example** (NOT real values):
```env
ZOOM_ACCOUNT_ID=YOUR_ZOOM_ACCOUNT_ID
ZOOM_CLIENT_ID=YOUR_ZOOM_S2S_CLIENT_ID
ZOOM_CLIENT_SECRET=YOUR_ZOOM_S2S_CLIENT_SECRET
```

Notice: All three values are DIFFERENT

---

## 🔍 Verification Checklist

Before testing again:

- [ ] Went to https://developers.zoom.us/marketplace
- [ ] Found "School of the Priests LMS" app
- [ ] Clicked "App Credentials"
- [ ] Found the correct credentials section
- [ ] Copied Account ID (not the same as any other value)
- [ ] Copied Client ID (not the same as any other value)
- [ ] Copied Client Secret (NOT the same as Account ID!)
- [ ] Pasted all 3 into .env file
- [ ] Verified no extra spaces or characters
- [ ] Saved .env file
- [ ] All 3 values are DIFFERENT from each other

---

## 🧪 Test After Fixing

Once you've updated credentials:

```bash
cd server
node debug-zoom-auth.js
```

**Expected Output**:
```
✅ SUCCESS!

Response Data:
  Access Token: eyJhbGc...
  Token Type: Bearer
  Expires In: 3600 seconds
  Scope: meeting:write meeting:read user:read
```

---

## 🎯 Quick Reference

### What Each Credential Is

**Account ID**:
- Identifies your Zoom account
- Used to authenticate "account" level access
- Different from user ID
- Look for field labeled "Account ID"

**Client ID**:
- Identifies your app
- Generated when you create the app
- Short alphanumeric string
- Look for field labeled "Client ID"

**Client Secret**:
- Secret password for your app
- Keep this private!
- Long alphanumeric string
- MUST be different from Account ID
- Look for field labeled "Client Secret"

---

## ⚠️ Common Mistakes

❌ **Mistake 1**: Copying Account ID twice
- Account ID: ABC123...
- Client Secret: ABC123... (same!)

✅ **Fix**: Each field should have a different value

❌ **Mistake 2**: Copying with extra spaces
- Account ID: " ABC123... " (with spaces)

✅ **Fix**: Copy without leading/trailing spaces

❌ **Mistake 3**: Wrong field from wrong app
- Check you're in the right app
- Make sure it's "School of the Priests LMS"
- Make sure it's "Server-to-Server OAuth" type

✅ **Fix**: Double-check app name and type

---

## 💡 If You Can't Find the Credentials

If the credentials section looks different:

1. Look for these tabs/sections:
   - "App Credentials"
   - "OAuth"
   - "Authentication"
   - "Server-to-Server OAuth"

2. If still can't find:
   - Try refreshing the page
   - Try a different browser
   - Clear browser cache

3. If app shows as inactive:
   - Click "Activate"
   - Wait 2 minutes
   - Then go back to credentials

---

## 🔄 Next Steps

1. ✅ Get correct credentials from Zoom
2. ✅ Update .env file (all 3 different values)
3. ✅ Run: `node server/debug-zoom-auth.js`
4. ✅ Verify: "SUCCESS!" message appears
5. ✅ Run: `node server/test-zoom-connection.js`
6. ✅ Start server: `npm run dev`

---

## 📞 Support

**For help finding credentials**:
- Zoom Docs: https://developers.zoom.us/docs/api/rest/using-oauth/

**For help with Zoom Marketplace**:
- Zoom Marketplace: https://developers.zoom.us/marketplace

---

**Status**: 🔴 Waiting for Credential Fix
**Time to Fix**: ~5 minutes
**Urgency**: HIGH - Blocking Zoom integration
