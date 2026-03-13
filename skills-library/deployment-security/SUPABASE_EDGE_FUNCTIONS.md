# Supabase Edge Functions Deployment Guide

**Date Created:** October 27, 2025
**Project:** BoltBudgetApp
**Supabase Project Ref:** `ovigezezdnacnhxhtsbx`
**Supabase URL:** `https://ovigezezdnacnhxhtsbx.supabase.co`

---

## 📋 Quick Reference

**Problem:** Edge Functions exist locally but need to be deployed to Supabase cloud

**Solution:** Use Supabase CLI to deploy functions

**Time to Deploy:** ~2-5 minutes

---

## 🚀 Installation Options (Choose One)

### Option 1: Local npm (RECOMMENDED - Easiest)
No additional software needed. Install in your project:

```bash
cd C:\Users\Thier\source\repos\BoltBudgetApp
npm install -D supabase
```

Then use with `npx` prefix:
```bash
npx supabase login
npx supabase link --project-ref ovigezezdnacnhxhtsbx
npx supabase functions deploy
```

---

### Option 2: Scoop (Windows Package Manager)
```bash
# Install Scoop (if you don't have it)
iwr -useb get.scoop.sh | iex

# Install Supabase CLI
scoop install supabase

# Then use normally (no npx needed)
supabase login
supabase link --project-ref ovigezezdnacnhxhtsbx
supabase functions deploy
```

---

### Option 3: Chocolatey (Windows Package Manager)
```bash
# Install Chocolatey (if you don't have it)
# See: https://chocolatey.org/install

# Install Supabase CLI
choco install supabase

# Then use normally (no npx needed)
supabase login
supabase link --project-ref ovigezezdnacnhxhtsbx
supabase functions deploy
```

---

### Option 4: Download Installer
Download directly from [Supabase CLI Releases](https://github.com/supabase/cli/releases)

---

## 📝 Complete Deployment Steps

### Step 1: Install Supabase CLI

**Using local npm (recommended):**
```bash
cd C:\Users\Thier\source\repos\BoltBudgetApp
npm install -D supabase
```

---

### Step 2: Login to Supabase

**Using local npm:**
```bash
npx supabase login
```

**Using Scoop/Chocolatey:**
```bash
supabase login
```

This will open a browser window asking you to authenticate.
- Use your Supabase account credentials
- Allow access when prompted

---

### Step 3: Link Your Project

**Using local npm:**
```bash
npx supabase link --project-ref ovigezezdnacnhxhtsbx
```

**Using Scoop/Chocolatey:**
```bash
supabase link --project-ref ovigezezdnacnhxhtsbx
```

This links your local repository to your Supabase cloud project.

---

### Step 4: Deploy Edge Functions

**Using local npm:**
```bash
npx supabase functions deploy
```

**Using Scoop/Chocolatey:**
```bash
supabase functions deploy
```

This deploys all functions from `supabase/functions/` to your Supabase project.

**Expected output:**
```
Deploying function document-extract...
Functions deployed successfully ✓
```

---

## 📁 Functions to Deploy

Your project has these Edge Functions that need deployment:

1. **`supabase/functions/document-extract/index.ts`**
   - Purpose: Extract tables from PDFs/images using LandingAI
   - Endpoint: `/functions/v1/document-extract`
   - Status: ✅ Ready to deploy

2. **`supabase/functions/document-analyze/index.ts`**
   - Purpose: AI analysis using Claude/GPT/Gemini
   - Endpoint: `/functions/v1/document-analyze`
   - Status: ✅ Ready to deploy

3. **`supabase/functions/document-convert/index.ts`**
   - Purpose: Convert tables to JSON/HTML
   - Endpoint: `/functions/v1/document-convert`
   - Status: ✅ Ready to deploy (optional)

4. **`supabase/functions/document-export/index.ts`**
   - Purpose: Export to Excel/Google Sheets
   - Endpoint: `/functions/v1/document-export`
   - Status: ✅ Ready to deploy (optional)

---

## 🔐 Environment Variables for Edge Functions

After deployment, you need to set API keys in Supabase dashboard.

**Steps:**
1. Go to [Supabase Dashboard](https://app.supabase.com/)
2. Select your project: `ovigezezdnacnhxhtsbx`
3. Go to **Project Settings → Edge Functions → Secrets**
4. Add these secrets:

### For Claude/Anthropic:
```
ANTHROPIC_API_KEY = your_anthropic_api_key
```

### For OpenAI/GPT:
```
OPENAI_API_KEY = your_openai_api_key
```

### For Google/Gemini:
```
GOOGLE_API_KEY = your_google_api_key
```

### For LandingAI (Document Extraction):
```
LANDINGAI_API_KEY = your_landingai_api_key
```

---

## ✅ Verify Deployment

After deploying, verify the functions are working:

1. **Check Supabase Dashboard:**
   - Go to `https://app.supabase.com/`
   - Select project `ovigezezdnacnhxhtsbx`
   - Go to **Edge Functions**
   - Should see: `document-extract`, `document-analyze`, `document-convert`, `document-export`

2. **Test from Browser:**
   - Open app at `http://localhost:5180`
   - Login to your account
   - Upload a document
   - Click "Analyze with AI"
   - Should work without CORS errors

3. **Check Browser Console:**
   - Open DevTools (F12)
   - Should NOT see: `Cross-Origin Request Blocked` error
   - Should see extraction working

---

## 🔧 Troubleshooting

### Error: "CORS preflight response did not succeed"
**Cause:** Edge Functions not deployed
**Fix:** Run `supabase functions deploy` again

### Error: "No user session"
**Cause:** User not authenticated
**Fix:** Login to app in browser first

### Error: "LANDINGAI_API_KEY not found"
**Cause:** Environment variable not set
**Fix:** Add secret in Supabase Dashboard → Edge Functions → Secrets

### Error: "Cross-Origin Request Blocked 404"
**Cause:** Function endpoint doesn't exist
**Fix:** Deploy functions again with `supabase functions deploy`

---

## 📚 Useful Commands

```bash
# View all functions
npx supabase functions list

# View logs for a function
npx supabase functions logs document-extract

# Deploy specific function
npx supabase functions deploy document-extract

# View deployment status
npx supabase status

# Link to different project
npx supabase link --project-ref different-project-ref
```

---

## ⚠️ Important Notes

1. **CLI vs Global Install**
   - Supabase CLI doesn't support global npm install on Windows
   - Use local npm (`npm install -D supabase`) or Scoop/Chocolatey instead

2. **Authentication Required**
   - Must have Supabase account with access to the project
   - `supabase login` must succeed

3. **Project Linking**
   - Must run `supabase link` before deploying
   - Ensures local functions sync with cloud project

4. **API Keys**
   - Set environment variables in Supabase Dashboard after deployment
   - Functions need these to call AI providers

5. **Deployment Location**
   - Must be in project root where `supabase/` folder exists
   - `supabase functions deploy` command looks for `supabase/functions/`

---

## 🎯 When to Re-Deploy

Deploy functions again when:
- ✅ You modify any Edge Function code
- ✅ You add a new Edge Function
- ✅ You update dependencies in function code
- ✅ You add new environment variables

**Command:**
```bash
npx supabase functions deploy
```

---

## 📞 Reference

- **Supabase Docs:** https://supabase.com/docs
- **Edge Functions Guide:** https://supabase.com/docs/guides/functions
- **CLI Documentation:** https://github.com/supabase/cli
- **Project Dashboard:** https://app.supabase.com/

---

## 📝 Quick Copy-Paste Commands

**For Local npm (Option 1):**
```bash
cd C:\Users\Thier\source\repos\BoltBudgetApp
npm install -D supabase
npx supabase login
npx supabase link --project-ref ovigezezdnacnhxhtsbx
npx supabase functions deploy
```

**For Scoop:**
```bash
scoop install supabase
supabase login
supabase link --project-ref ovigezezdnacnhxhtsbx
supabase functions deploy
```

---

**Last Updated:** October 27, 2025
**Status:** Ready for deployment

