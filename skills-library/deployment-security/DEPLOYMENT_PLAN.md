# MERN Community LMS - Production Deployment Plan

**Created:** November 27, 2025
**Status:** Planning Phase
**Last Updated:** November 27, 2025

---

## Executive Summary

This document outlines three deployment strategies for the MERN Community LMS application, with parallel work tracks for implementation.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURRENT ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React + Vite)    →  Backend (Express 5)              │
│  Port 3000/5173             →  Port 5000                        │
│                                                                  │
│  Database: Supabase PostgreSQL (hosted)                         │
│  Storage: MinIO/S3 (configurable)                               │
│  Email: Nodemailer (SMTP)                                       │
│  Payments: Stripe                                               │
│  PDF: Puppeteer                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Deployment Options

### Option A: Vercel + Railway (Recommended for Quick Deployment)

**Pros:** Fastest to deploy, auto-scaling, SSL included, great DX
**Cons:** Monthly costs scale with usage, less control
**Best For:** MVP launch, testing, small-medium traffic

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   VERCEL        │     │   RAILWAY       │     │   SUPABASE      │
│   (Frontend)    │────▶│   (Backend)     │────▶│   (Database)    │
│   React/Vite    │     │   Express API   │     │   PostgreSQL    │
│   CDN + SSL     │     │   Node.js       │     │   Already Setup │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Option B: Self-Hosted VPS (Full Control)

**Pros:** Full control, fixed monthly cost, no vendor lock-in
**Cons:** More setup, manual scaling, server maintenance
**Best For:** Production at scale, specific compliance needs

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR SERVER (VPS)                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│  │ NGINX   │   │ Frontend│   │ Backend │   │ MinIO   │        │
│  │ Reverse │──▶│ Static  │──▶│ Express │──▶│ Storage │        │
│  │ Proxy   │   │ Files   │   │ API     │   │ (S3)    │        │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘        │
│       │                           │                            │
│       ▼                           ▼                            │
│  ┌─────────┐              ┌─────────────┐                     │
│  │SSL/TLS  │              │ Supabase    │                     │
│  │Certbot  │              │ (External)  │                     │
│  └─────────┘              └─────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

### Option C: Docker + Docker Compose (Portable)

**Pros:** Reproducible, portable, easy to move between hosts
**Cons:** Docker overhead, complexity
**Best For:** Multi-environment deployment, team development

---

## Implementation Plan

### TRACK 1: VERCEL DEPLOYMENT (Frontend Only)

**Estimated Time:** 1-2 hours
**Can Run In Parallel:** Yes

#### Step 1.1: Create vercel.json in project root
```json
{
  "version": 2,
  "buildCommand": "cd client && npm run build",
  "outputDirectory": "client/dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

#### Step 1.2: Environment Variables for Vercel
```
VITE_API_URL=https://your-backend.railway.app/api
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_...
VITE_APP_NAME=School of the Holy Spirit
```

#### Step 1.3: Deploy Commands
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy from client directory
cd client
vercel --prod
```

---

### TRACK 2: RAILWAY DEPLOYMENT (Backend)

**Estimated Time:** 2-3 hours
**Can Run In Parallel:** Yes (with Track 1)

#### Step 2.1: Create railway.json
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd server && npm start",
    "healthcheckPath": "/api/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### Step 2.2: Environment Variables for Railway
```
NODE_ENV=production
PORT=5000
DATABASE_URL=postgresql://postgres:YOUR_DB_PASSWORD_HERE@db.jpfrnunodkjplslfouqw.supabase.co:5432/postgres
JWT_SECRET=[generate-new-secret]
JWT_EXPIRE=30d

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=admin@schooloftheholyspirit.church
EMAIL_PASS=[app-password]
EMAIL_FROM=admin@schooloftheholyspirit.church

# Client URL for CORS
CLIENT_URL=https://your-vercel-app.vercel.app

# Optional: MinIO/S3 for file storage
MINIO_ENDPOINT=s3.amazonaws.com
MINIO_ACCESS_KEY=...
MINIO_SECRET_KEY=...
MINIO_BUCKET=lms-uploads
```

#### Step 2.3: Puppeteer Configuration for Railway
Add to package.json:
```json
"engines": {
  "node": ">=20.0.0"
}
```

Create `.puppeteerrc.cjs`:
```javascript
module.exports = {
  cacheDirectory: '/tmp/.cache/puppeteer'
};
```

---

### TRACK 3: SELF-HOSTED VPS DEPLOYMENT

**Estimated Time:** 4-6 hours
**Can Run In Parallel:** No (requires Track 1 & 2 learnings)

#### Step 3.1: Server Requirements
- Ubuntu 22.04 LTS (recommended)
- Minimum: 2GB RAM, 2 vCPU, 40GB SSD
- Recommended: 4GB RAM, 4 vCPU, 80GB SSD

#### Step 3.2: Initial Server Setup Script
```bash
#!/bin/bash
# server-setup.sh

# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2 globally
sudo npm install -g pm2

# Install Nginx
sudo apt install -y nginx

# Install Certbot for SSL
sudo apt install -y certbot python3-certbot-nginx

# Install Git
sudo apt install -y git

# Create app directory
sudo mkdir -p /var/www/lms
sudo chown $USER:$USER /var/www/lms
```

#### Step 3.3: Nginx Configuration
```nginx
# /etc/nginx/sites-available/lms.conf

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend - Static files
    location / {
        root /var/www/lms/client/dist;
        try_files $uri $uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeout settings for long operations
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Uploads directory
    location /uploads {
        alias /var/www/lms/server/uploads;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Webhook endpoint (no timeout)
    location /api/webhooks {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
```

#### Step 3.4: PM2 Ecosystem File
```javascript
// ecosystem.config.cjs
module.exports = {
  apps: [{
    name: 'lms-server',
    script: './server/server.js',
    cwd: '/var/www/lms',
    instances: 'max',
    exec_mode: 'cluster',
    env_production: {
      NODE_ENV: 'production',
      PORT: 5000
    },
    error_file: '/var/log/pm2/lms-error.log',
    out_file: '/var/log/pm2/lms-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    max_memory_restart: '1G',
    watch: false,
    autorestart: true,
    max_restarts: 10,
    restart_delay: 4000
  }]
};
```

---

### TRACK 4: CI/CD FOR REMOTE UPDATES

**Estimated Time:** 2-3 hours
**Depends On:** Track 1, 2, or 3 completion

#### Step 4.1: GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml

name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: client/package-lock.json

      - name: Install dependencies
        run: cd client && npm ci

      - name: Build
        run: cd client && npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}
          VITE_STRIPE_PUBLISHABLE_KEY: ${{ secrets.VITE_STRIPE_PUBLISHABLE_KEY }}

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
          working-directory: ./client

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Railway
        uses: berviantoleo/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: lms-backend

  # Alternative: Self-hosted deployment
  deploy-vps:
    runs-on: ubuntu-latest
    if: github.event_name == 'workflow_dispatch'
    steps:
      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /var/www/lms
            git pull origin main
            cd server && npm ci --production
            cd ../client && npm ci && npm run build
            pm2 restart lms-server
```

#### Step 4.2: Webhook-based Deployment (Alternative)
```javascript
// server/routes/deployRoutes.js
import express from 'express';
import { exec } from 'child_process';
import crypto from 'crypto';

const router = express.Router();

router.post('/webhook', (req, res) => {
  const signature = req.headers['x-hub-signature-256'];
  const payload = JSON.stringify(req.body);

  const expectedSignature = 'sha256=' + crypto
    .createHmac('sha256', process.env.DEPLOY_SECRET)
    .update(payload)
    .digest('hex');

  if (signature !== expectedSignature) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  exec('/var/www/lms/deploy.sh', (error, stdout, stderr) => {
    if (error) {
      console.error('Deploy failed:', error);
      return res.status(500).json({ error: 'Deploy failed' });
    }
    res.json({ success: true, output: stdout });
  });
});

export default router;
```

---

### TRACK 5: DOCKER CONTAINERIZATION

**Estimated Time:** 3-4 hours
**Can Run In Parallel:** Yes

#### Step 5.1: Dockerfile for Backend
```dockerfile
# server/Dockerfile
FROM node:20-slim

# Install Chromium dependencies for Puppeteer
RUN apt-get update && apt-get install -y \
    chromium \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app

COPY package*.json ./
RUN npm ci --production

COPY . .

EXPOSE 5000

CMD ["node", "server.js"]
```

#### Step 5.2: Dockerfile for Frontend
```dockerfile
# client/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
ARG VITE_API_URL
ARG VITE_STRIPE_PUBLISHABLE_KEY
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Step 5.3: Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./client
      args:
        VITE_API_URL: ${VITE_API_URL}
        VITE_STRIPE_PUBLISHABLE_KEY: ${VITE_STRIPE_PUBLISHABLE_KEY}
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/certs:/etc/nginx/certs:ro
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    build: ./server
    environment:
      - NODE_ENV=production
      - PORT=5000
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET=${JWT_SECRET}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - EMAIL_HOST=${EMAIL_HOST}
      - EMAIL_USER=${EMAIL_USER}
      - EMAIL_PASS=${EMAIL_PASS}
    volumes:
      - ./server/uploads:/app/uploads
      - ./server/storage:/app/storage
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

---

## Production Readiness Checklist

### Security
- [ ] Generate new JWT_SECRET for production (min 64 chars)
- [ ] Enable HTTPS/SSL on all endpoints
- [ ] Configure CORS for production domains only
- [ ] Audit rate limiting settings
- [ ] Review helmet.js configuration
- [ ] Sanitize all user inputs (XSS protection)
- [ ] Enable CSP headers

### Environment Variables
- [ ] Create `.env.production` template
- [ ] Remove all hardcoded credentials
- [ ] Set up secrets in deployment platform
- [ ] Verify DATABASE_URL uses SSL

### Performance
- [ ] Enable gzip compression in Nginx
- [ ] Configure CDN for static assets
- [ ] Optimize bundle size (code splitting)
- [ ] Enable connection pooling for DB

### Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Configure application logging
- [ ] Set up health check endpoints
- [ ] Configure uptime monitoring

### Backups
- [ ] Enable Supabase automatic backups
- [ ] Configure file upload backups
- [ ] Document recovery procedures

---

## Parallel Work Tracks Summary

| Track | Task | Can Parallelize | Dependencies |
|-------|------|-----------------|--------------|
| 1 | Vercel Frontend Setup | Yes | None |
| 2 | Railway Backend Setup | Yes | None |
| 3 | VPS Self-Hosted | No | Tracks 1 & 2 learnings |
| 4 | CI/CD Pipeline | No | Track 1, 2, or 3 |
| 5 | Docker Containerization | Yes | None |

### Recommended Parallel Execution:
```
Phase 1 (Parallel):
├── Track 1: Vercel Frontend
├── Track 2: Railway Backend
└── Track 5: Docker Setup (preparation)

Phase 2 (Sequential):
├── Track 4: CI/CD Pipeline
└── Integration Testing

Phase 3 (Optional):
└── Track 3: VPS Migration (if needed)
```

---

## Quick Start Commands

### Deploy to Vercel + Railway
```bash
# Frontend
cd client && vercel --prod

# Backend (Railway auto-deploys from GitHub)
```

### Self-Hosted Deploy Script
```bash
#!/bin/bash
# deploy.sh

set -e

echo "📦 Pulling latest code..."
git pull origin main

echo "📦 Installing backend dependencies..."
cd server && npm ci --production

echo "🏗️ Building frontend..."
cd ../client && npm ci && npm run build

echo "🔄 Restarting services..."
pm2 restart lms-server

echo "✅ Deployment complete!"
```

---

## Cost Estimates

| Option | Monthly Cost | Notes |
|--------|-------------|-------|
| Vercel + Railway | $20-50 | Scales with usage |
| Self-Hosted VPS | $20-40 | Fixed cost (DigitalOcean/Linode) |
| Docker on VPS | $20-40 | Same as VPS |
| Supabase | Free-$25 | Database already hosted |

---

## Next Steps

1. **Choose deployment option** (A, B, or C)
2. **Execute parallel tracks** for faster deployment
3. **Configure environment variables** for production
4. **Set up CI/CD** for automated deployments
5. **Test deployment** in staging environment
6. **Go live** with production domain

---

**Document Status:** Ready for Implementation
**Approved By:** [Pending]
**Target Go-Live:** [TBD]
