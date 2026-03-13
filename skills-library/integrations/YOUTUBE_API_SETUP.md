# YouTube API Setup Guide

This guide will help you set up the YouTube Data API v3 for importing YouTube playlists into your LMS.

## Prerequisites

- Google Account
- Google Cloud Platform (GCP) access

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter project name (e.g., "MERN-LMS")
5. Click "Create"

### 2. Enable YouTube Data API v3

1. In the Google Cloud Console, make sure your project is selected
2. Go to **APIs & Services** > **Library**
3. Search for "YouTube Data API v3"
4. Click on it
5. Click **Enable**

### 3. Create API Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **API Key**
3. Your API key will be created and displayed
4. **Important**: Click **Restrict Key** to secure it

### 4. Restrict the API Key (Recommended)

#### Application Restrictions:
- **None** (or HTTP referrers if you want to restrict to your domain)

#### API Restrictions:
- Select "Restrict key"
- Check only "YouTube Data API v3"
- Click "Save"

### 5. Add API Key to Your Environment

1. Copy the API key
2. Open `server/.env` file
3. Add or update the following line:
   ```
   YOUTUBE_API_KEY=YOUR_API_KEY_HERE
   ```

### 6. Test the API

Run the test script to verify everything works:

```bash
cd server
node test-youtube-api.js
```

You should see:
```
✅ All tests passed!
```

## Usage Limits

### Free Tier Quota:
- **10,000 units per day** (quota resets at midnight Pacific Time)

### Cost Per Operation:
- List playlist items: **1 unit per request** (50 videos)
- Get playlist metadata: **1 unit per request**

### Example:
- Importing a 50-video playlist = **2 units**
- Importing a 200-video playlist = **6 units** (4 paginated requests + 1 metadata)

**You can import approximately 2,500 playlists per day within the free tier.**

## Troubleshooting

### Error: "API key not valid"
**Solution:**
1. Make sure YouTube Data API v3 is enabled
2. Check that the API key is copied correctly
3. Wait a few minutes after creating the key (can take time to activate)
4. Verify API restrictions don't block your requests

### Error: "The request cannot be completed because you have exceeded your quota"
**Solution:**
1. Wait 24 hours for quota reset
2. Request a quota increase in Google Cloud Console:
   - Go to **APIs & Services** > **Quotas**
   - Find "YouTube Data API v3"
   - Click "Edit Quotas"
   - Submit quota increase request

### Error: "Playlist not found or is private"
**Solution:**
- Make sure the playlist is public or unlisted
- Private playlists cannot be imported

### Error: "Access Not Configured"
**Solution:**
- Ensure YouTube Data API v3 is enabled in your project
- Try disabling and re-enabling the API

## Security Best Practices

1. **Never commit API keys to version control**
   - Add `.env` to `.gitignore`
   - Use environment variables in production

2. **Restrict API key usage**
   - Set application restrictions (HTTP referrers, IP addresses)
   - Limit to YouTube Data API v3 only
   - Rotate keys periodically

3. **Monitor usage**
   - Check quota usage in Google Cloud Console
   - Set up billing alerts if using paid quota

## Alternative: Vimeo Showcase Import

If you prefer not to use YouTube or need an alternative, the LMS also supports Vimeo showcases:

1. Get a Vimeo access token from [Vimeo Developer](https://developer.vimeo.com/apps)
2. Add to `.env`:
   ```
   VIMEO_ACCESS_TOKEN=YOUR_TOKEN_HERE
   ```

## Support

For more help:
- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [Google Cloud Console](https://console.cloud.google.com/)
- [API Key Best Practices](https://cloud.google.com/docs/authentication/api-keys)
