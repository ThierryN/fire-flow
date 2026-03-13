# YouTube OAuth Setup Guide - Quick Steps

**Goal:** Access your 11 private YouTube videos from Fire School channel
**Time Required:** 5-10 minutes

---

## ✅ What You'll Get:

1. **YOUTUBE_CLIENT_ID** - Your app identifier
2. **YOUTUBE_CLIENT_SECRET** - Your app password
3. **YOUTUBE_REFRESH_TOKEN** - Access key to your private videos

---

## 🚀 Step-by-Step Instructions

### **STEP 1: Create OAuth Client Credentials**

**Link:** https://console.cloud.google.com/apis/credentials

1. **Select your project** (top dropdown)
   - If you don't have one, create: "Fire School LMS" or similar

2. **Click the big "+ CREATE CREDENTIALS" button** (top of page)

3. **Select "OAuth client ID"**

4. **If prompted about consent screen:**
   - Click "CONFIGURE CONSENT SCREEN"
   - Choose **"External"**
   - App name: `Fire School LMS`
   - User support email: Your email
   - Developer contact: Your email
   - Click **"SAVE AND CONTINUE"** (3 times, skip optional sections)
   - Go back to credentials page

5. **Create the OAuth client:**
   - Click "+ CREATE CREDENTIALS" → "OAuth client ID" again
   - Application type: **"Desktop app"**
   - Name: `Fire School YouTube Access`
   - Click **"CREATE"**

6. **Copy your credentials:**
   - ✅ **Client ID:** Copy this (ends with `.apps.googleusercontent.com`)
   - ✅ **Client secret:** Copy this (starts with `GOCSPX-`)
   - Click **"DOWNLOAD JSON"** (save for backup)

---

### **STEP 2: Add YouTube API Scope**

**Link:** https://console.cloud.google.com/apis/credentials/consent

1. Click **"EDIT APP"**

2. Scroll to **"Scopes"** section

3. Click **"ADD OR REMOVE SCOPES"**

4. **Search for:** `youtube`

5. **Check these boxes:**
   - ☑️ `https://www.googleapis.com/auth/youtube.readonly` (View your YouTube account)
   - ☑️ `https://www.googleapis.com/auth/youtube` (Manage your YouTube account) - Optional, for uploads

6. Click **"UPDATE"** → **"SAVE AND CONTINUE"** → **"SAVE AND CONTINUE"**

7. **Add test user:**
   - Scroll to "Test users" section
   - Click **"+ ADD USERS"**
   - Enter your YouTube channel email: `_________________`
   - Click **"SAVE"**

---

### **STEP 3: Get Refresh Token** (Most Important!)

**Link:** https://developers.google.com/oauthplayground/

1. **Click the ⚙️ gear icon** (top right corner)

2. **Check the box:** ☑️ "Use your own OAuth credentials"

3. **Paste your credentials:**
   - OAuth Client ID: `YOUR_CLIENT_ID_FROM_STEP_1`
   - OAuth Client secret: `YOUR_CLIENT_SECRET_FROM_STEP_1`

4. **Close the settings** (click ⚙️ again or click outside)

5. **On the left sidebar, find "YouTube Data API v3"**
   - Expand it (click the arrow)

6. **Check this scope:**
   - ☑️ `https://www.googleapis.com/auth/youtube.readonly`

7. **Click the blue "Authorize APIs" button**

8. **Sign in with your YouTube channel account**
   - Use the email that OWNS the Fire School channel
   - Grant all permissions

9. **Click "Exchange authorization code for tokens"** button

10. **Copy the Refresh token:**
    - Look for: `"refresh_token": "1//..."`
    - ✅ **Copy this entire value** (starts with `1//`)

---

## 📝 Update Your MCP Configuration

Open: `C:\Users\Thier\source\repos\my-other-project\.vscode\mcp.json`

Find the `mcp-youtube` section and paste your credentials:

```json
"mcp-youtube": {
  "command": "npx",
  "args": ["-y", "youtube-data-mcp-server"],
  "env": {
    "YOUTUBE_API_KEY": "YOUR_YOUTUBE_API_KEY",
    "YOUTUBE_CLIENT_ID": "123456-abcdef.apps.googleusercontent.com",
    "YOUTUBE_CLIENT_SECRET": "GOCSPX-abc123xyz",
    "YOUTUBE_REFRESH_TOKEN": "1//abc123xyz..."
  }
}
```

**Save the file!**

---

## 🔄 Activate the Changes

1. **Reload VS Code:**
   - Press `Ctrl+Shift+P`
   - Type: `Developer: Reload Window`
   - Press Enter

2. **Test it:**
   - After reload, I'll be able to access your 11 private videos!

---

## ✅ Verification Checklist

Before reloading VS Code, make sure:
- [ ] You have all 3 credentials (Client ID, Secret, Refresh Token)
- [ ] You added the YouTube scope in consent screen
- [ ] You added yourself as a test user
- [ ] You pasted all values into `.vscode/mcp.json`
- [ ] You saved the file
- [ ] You're ready to reload VS Code

---

## 🆘 Troubleshooting

### "Access blocked: This app's request is invalid"
**Fix:** Go back to Step 2, make sure you added the YouTube scope and yourself as a test user

### "Invalid client" error in OAuth Playground
**Fix:** Make sure you clicked "Use your own OAuth credentials" in the ⚙️ settings

### No refresh token appears
**Fix:**
1. Make sure you're using "Desktop app" type (not "Web application")
2. If it still doesn't work, try creating a new OAuth client

### "Redirect URI mismatch"
**Fix:** You might have selected "Web application" instead of "Desktop app" - create a new one as Desktop app

---

## 📧 Need Help?

If you get stuck:
1. Take a screenshot of the error
2. Note which step you're on
3. Ask me for help!

---

## 🎯 What Happens After Setup?

Once configured and VS Code is reloaded:
- ✅ I can see all 19 videos (9 public + 10 private)
- ✅ I can catalog the private video titles
- ✅ I can get metadata for course integration
- ✅ You can embed private videos in courses (visible only to enrolled students)

---

**Ready to start? Begin with Step 1!**

**Quick Links:**
- **Step 1:** https://console.cloud.google.com/apis/credentials
- **Step 2:** https://console.cloud.google.com/apis/credentials/consent
- **Step 3:** https://developers.google.com/oauthplayground/
