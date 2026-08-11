# VPS Deployment Skill

## Overview
This skill documents the deployment process for the my-other-project application to the VPS at example.com.

## Key Discovery: Shared Hosting Architecture

**Critical:** The VPS uses shared hosting (cPanel/Apache), NOT nginx directly.

### Directory Structure
```
~/your-app/                    # Application source code
~/your-app/client/dist/        # Vite build output (NOT served directly)
~/public_html/                 # Apache web root (ACTUALLY served to users)
~/public_html/assets/          # Where JS/CSS bundles must be deployed
```

### The Problem
When running `npm run build`, Vite outputs to `~/your-app/client/dist/`. However, the web server (Apache) serves files from `~/public_html/`. If you don't copy the build output to public_html, users will continue seeing the old cached version.

## Complete Deployment Process

### 1. Pull Latest Code
```bash
ssh deploy@your-server.example.com
cd ~/your-app
git pull origin feature-branch
```

### 2. Build the Client
```bash
cd ~/your-app/client
rm -rf dist node_modules/.vite .vite   # Clear all caches
npm run build
```

### 3. Deploy to Web Root (CRITICAL STEP)
```bash
cp -r ~/your-app/client/dist/* ~/public_html/
```

### 4. Restart Server
```bash
pm2 restart all
```

### One-Liner Command
```bash
ssh deploy@your-server.example.com "cd ~/your-app && git pull origin feature-branch && cd client && rm -rf dist node_modules/.vite && npm run build && cp -r dist/* ~/public_html/ && pm2 restart all"
```

## Debugging Deployment Issues

### Symptoms of Missing Deployment
- UI changes don't appear despite successful build
- "Hard refresh" doesn't help
- Different bundle hash in browser vs server

### Diagnostic Commands

**Check what's being served vs what's on disk:**
```bash
# On disk (build output)
head -c 200 ~/your-app/client/dist/assets/index-*.js

# What Apache serves
curl -s https://example.com/assets/index-*.js | head -c 200
```

**Verify bundle contains your code:**
```bash
grep "your-search-term" ~/your-app/client/dist/assets/ComponentName-*.js
```

**Check index.html references correct bundles:**
```bash
cat ~/public_html/index.html | grep -o 'index-[^"]*'
```

## Update version.json
After deployment, update version.json to reflect the current commit:
```bash
cd ~/your-app
COMMIT=$(git rev-parse HEAD)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
cat > version.json << EOF
{
  "version": "1.0.X",
  "commit": "$COMMIT",
  "branch": "$BRANCH",
  "updatedAt": "$(date -Iseconds)",
  "environment": "production"
}
EOF
```

## .htaccess Configuration
The `~/public_html/.htaccess` handles:
- API proxy to Node.js on port 5000
- SPA routing fallback to index.html
- Cache headers for HTML files

```apache
RewriteEngine On

# Proxy API requests to Node.js
RewriteCond %{REQUEST_URI} ^/api [NC,OR]
RewriteCond %{REQUEST_URI} ^/uploads [NC]
RewriteRule ^(.*)$ http://localhost:5000/$1 [P,L]

# SPA fallback
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]
```

## Server Details
- **Host:** deploy@your-server.example.com
- **Application:** ~/your-app
- **Web Root:** ~/public_html
- **Node Process:** PM2 (your-app-server)
- **Port:** 5000 (proxied via Apache)

## Cleanup Old Bundles
Old bundles accumulate in public_html/assets. Periodically clean up:
```bash
# List old Updates bundles
ls -la ~/public_html/assets/Updates-*.js

# Remove old bundles (keep only current)
# Be careful - only remove bundles not referenced by current index.html
```

## Lesson Learned
**Always copy build output to public_html after building.** The build step alone is not sufficient for deployment on this shared hosting setup.
