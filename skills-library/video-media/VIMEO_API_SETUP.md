# Vimeo API Setup Guide

This guide will help you generate an access token for your existing Vimeo app "MelchizedekPriest Playlist importing" to enable Vimeo showcase importing.

## You Already Have a Vimeo App! 🎉

Good news - you already have a Vimeo app set up called **"MelchizedekPriest Playlist importing"**. You just need to generate an access token.

## Generate Access Token

### Step 1: Go to Your Vimeo App

1. Visit [Vimeo Developer Apps](https://developer.vimeo.com/apps)
2. Click on your app: **"MelchizedekPriest Playlist importing"**

### Step 2: Navigate to Authentication Tab

1. In your app page, click on the **"Authentication"** tab
2. Scroll down to **"Personal Access Tokens"** section

### Step 3: Generate a New Token

1. Click **"Generate Token"** button
2. You'll see a form to select scopes

### Step 4: Select Required Scopes

Check these scopes (minimum required):
- ✅ **Public** - Access public data
- ✅ **Private** - Access private data (needed to access your own showcases)

Optional scopes (for future features):
- ✅ **Video Files** - Access video files (useful for download features)
- ✅ **Edit** - Edit videos (if you want to allow editing from the LMS)

### Step 5: Name Your Token (Optional)

Give it a descriptive name like:
- "LMS Playlist Import"
- "Production Server"
- "Development"

### Step 6: Generate and Copy

1. Click **"Generate"**
2. **IMPORTANT**: Copy the token immediately! It won't be shown again.
3. The token will look like: `588f634f9dd390d43e7f41bb66bb042794280b76`

### Step 7: Add to Environment Variables

1. Open `server/.env` file
2. Find the line:
   ```
   VIMEO_ACCESS_TOKEN=
   ```
3. Paste your token:
   ```
   VIMEO_ACCESS_TOKEN=588f634f9dd390d43e7f41bb66bb042794280b76
   ```
4. Save the file

### Step 8: Test the API

Run the test script:

```bash
cd server
node test-vimeo-api.js
```

You should see:
```
✅ All tests passed!
```

## Your App Details

Based on what you mentioned, your app has:
- **Name**: MelchizedekPriest Playlist importing
- **Client Identifier**: (your app ID)
- **API Version**: 3.4 (latest version - perfect!)

## Usage Limits

### Rate Limits:
- **Authenticated Requests**: 1,000 requests per hour
- **Unauthenticated**: 100 requests per hour

### Cost Per Operation:
- List showcase videos: **1 request** per 100 videos (paginated)
- Get showcase metadata: **1 request**

### Example:
- Importing a 50-video showcase = **2 requests**
- Importing a 300-video showcase = **5 requests**

**You can import ~500 showcases per hour** with authenticated access.

## Supported URL Formats

The LMS accepts these Vimeo URL formats:

### Showcase URLs:
- `https://vimeo.com/showcase/12345678`
- `https://vimeo.com/album/12345678` (old format)
- `12345678` (just the ID)

### Finding Showcase ID:
1. Go to your Vimeo profile
2. Click on "Showcases" or "Albums"
3. Open a showcase
4. Look at the URL: `vimeo.com/showcase/[ID]`

## Troubleshooting

### Error: "401 Unauthorized"
**Solution:**
- Make sure you generated a personal access token (not just API credentials)
- Verify the token is copied correctly to `.env`
- Ensure "Public" and "Private" scopes are selected

### Error: "404 Not Found"
**Solution:**
- Verify the showcase ID is correct
- Make sure the showcase is public or you own it
- Check that the showcase isn't deleted

### Error: "403 Forbidden"
**Solution:**
- The showcase may be private and you don't have access
- Try with a public showcase first
- Regenerate your token with proper scopes

### Token Not Working After Generation?
**Solution:**
- Wait 1-2 minutes for the token to activate
- Make sure you're using the correct token (not the client ID)
- Verify `.env` file is saved and reloaded

## Security Best Practices

1. **Never commit tokens to version control**
   - `.env` should be in `.gitignore`
   - Use different tokens for development/production

2. **Rotate tokens periodically**
   - Generate new tokens every few months
   - Revoke old tokens in Vimeo dashboard

3. **Use minimal scopes**
   - Only enable scopes you need
   - Start with Public + Private
   - Add more as needed

4. **Monitor usage**
   - Check rate limits in Vimeo dashboard
   - Watch for unusual activity

## Vimeo vs YouTube

### When to use Vimeo:
- ✅ Better video quality and player
- ✅ No ads
- ✅ More professional look
- ✅ Privacy controls
- ✅ Embeddable anywhere

### When to use YouTube:
- ✅ Wider reach and discoverability
- ✅ Free unlimited storage
- ✅ Better SEO
- ✅ Live streaming support
- ✅ Automatic captions

**The LMS supports both!** You can mix and match in the same course.

## Quick Reference

### Generate Token:
```
https://developer.vimeo.com/apps
→ Click your app
→ Authentication tab
→ Generate Token
→ Select: Public + Private
→ Copy token
```

### Test Token:
```bash
cd server
node test-vimeo-api.js
```

### Import Showcase:
1. Go to Course Builder
2. Click purple "Import Playlist" button on any section
3. Paste Vimeo showcase URL
4. Select "Vimeo" or "Auto-detect"
5. Click "Import Playlist"

## Support

For more help:
- [Vimeo API Documentation](https://developer.vimeo.com/api/reference)
- [Vimeo Developer Apps](https://developer.vimeo.com/apps)
- [Authentication Guide](https://developer.vimeo.com/api/authentication)
