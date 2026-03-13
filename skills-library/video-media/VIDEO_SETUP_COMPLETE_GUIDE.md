# Video Setup Complete Guide

**Date:** January 20, 2025
**Status:** ✅ Ready to Test

---

## ✅ What's Been Completed

### 1. MinIO Installation ✅
- Downloaded MinIO server (`C:\minio\minio.exe`)
- Downloaded MinIO client (`C:\minio\mc.exe`)
- Created start script (`C:\minio\start-minio.bat`)
- Created bucket setup script (`C:\minio\setup-bucket.bat`)
- Configured backend `.env` with MinIO credentials

### 2. Database Migration Created ✅
- Created migration file: `database_migration_add_video_provider.sql`
- This adds `video_provider` column to support YouTube/Vimeo links

### 3. Backend Configuration ✅
- MinIO environment variables added to `server/.env`
- Backend will automatically detect MinIO when running
- YouTube/Vimeo support implemented in controller

---

## 🚀 Quick Start (3 Steps)

### Step 1: Run Database Migration

Open your Supabase SQL Editor:
1. Go to: https://app.supabase.com/project/jpfrnunodkjplslfouqw/sql
2. Copy contents of `database_migration_add_video_provider.sql`
3. Click "Run"
4. Verify: You should see "Migration completed successfully!"

### Step 2: Start MinIO Server

Open a NEW PowerShell window:
```powershell
C:\minio\start-minio.bat
```

Leave this window open - MinIO runs in the foreground.

You should see:
```
MinIO Console: http://localhost:9001
MinIO API:     http://localhost:9000
Default credentials:
Username: minioadmin
Password: minioadmin
```

### Step 3: Create MinIO Bucket

Option A - Via Web Console (RECOMMENDED):
1. Open: http://localhost:9001
2. Login: `minioadmin` / `minioadmin`
3. Click "Buckets" → "Create Bucket"
4. Name: `lms-videos`
5. Click "Create Bucket"
6. Click bucket → "Access" tab → Set to "Public" (for development)

Option B - Via Command Line:
```powershell
C:\minio\setup-bucket.bat
```

---

## 🎥 Testing Videos

Now you have **TWO ways** to add videos to lessons:

### Method 1: YouTube/Vimeo Links (No MinIO needed)

1. In Course Builder, create a lesson
2. Select "Video" content type
3. Choose "YouTube" or "Vimeo" from dropdown
4. Paste URL (e.g., `https://youtu.be/dQw4w9WgXcQ`)
5. Save lesson

**YouTube videos work immediately - no upload needed!**

### Method 2: Upload Videos (Requires MinIO)

1. In Course Builder, create a lesson
2. Select "Video" content type
3. Choose "Upload (Storage)" from dropdown
4. Save lesson
5. Click "Upload Video" button
6. Select your video file
7. Watch progress bar reach 100%
8. Video is stored in MinIO!

---

## 🔍 Verification Checklist

- [ ] **Database Migration**: Run SQL migration successfully
- [ ] **MinIO Running**: `http://localhost:9001` opens and you can login
- [ ] **Bucket Created**: `lms-videos` bucket exists in MinIO console
- [ ] **Backend Running**: Server starts without errors
- [ ] **Frontend Running**: UI loads at `http://localhost:5173`
- [ ] **YouTube Test**: Create lesson with YouTube URL, verify it saves
- [ ] **Upload Test**: Upload actual video file, verify progress bar works
- [ ] **MinIO Test**: Check `http://localhost:9001` → Buckets → lms-videos → See uploaded file

---

## 📁 Files Created/Modified

### New Files:
1. `MINIO_SETUP.md` - Detailed MinIO documentation
2. `setup-minio.ps1` - Automated MinIO installer
3. `database_migration_add_video_provider.sql` - Database migration
4. `VIDEO_SETUP_COMPLETE_GUIDE.md` - This file
5. `C:\minio\start-minio.bat` - Start MinIO server
6. `C:\minio\setup-bucket.bat` - Create bucket automatically

### Modified Files:
1. `server/.env` - Added MinIO configuration (lines 56-62)
2. `server/services/storageService.js` - Use env variable for bucket name (line 9)

---

## 🎯 Current Status

### ✅ Working:
- MinIO server installation complete
- Backend configured to use MinIO
- YouTube/Vimeo URL support (once migration runs)
- Video upload UI with progress bar
- Mock mode for testing without MinIO

### ⚠️ Requires User Action:
1. Run database migration (Step 1 above)
2. Start MinIO server (Step 2 above)
3. Create lms-videos bucket (Step 3 above)

### 🔄 Then Ready to Test:
- YouTube video links
- Video file uploads to MinIO
- Video playback from storage

---

## 🐛 Troubleshooting

### MinIO won't start
```powershell
# Check if port 9000 is in use
netstat -ano | findstr "9000"

# Kill process using port 9000 (replace PID)
taskkill /F /PID <PID>

# Try starting again
C:\minio\start-minio.bat
```

### Backend shows "MinIO not configured"
- Make sure MinIO is running (`start-minio.bat`)
- Check `server/.env` has `MINIO_ENDPOINT=localhost`
- Restart backend server

### Upload button disabled
- Make sure you selected a video file
- Check browser console for errors (F12)
- Verify MinIO is running at http://localhost:9001

### YouTube URL not saving
- Make sure you ran the database migration first!
- Check backend logs for errors
- Verify URL format: `https://youtu.be/...` or `https://www.youtube.com/watch?v=...`

---

##Human: continue