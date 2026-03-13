# Production Deployment Guide
**Status**: Ready for deployment
**Date**: October 26, 2025
**Checklist**: Pre-deployment verification

---

## 🚀 Pre-Deployment Checklist

Before deploying to production, verify all items:

### Environment Configuration
- [ ] `.env` file configured for production
- [ ] All secrets stored securely (not in git)
- [ ] Database backups configured
- [ ] SSL/TLS certificates ready
- [ ] Domain configured and pointing to server

### Application Setup
- [ ] All npm dependencies installed: `npm install`
- [ ] Build verified: `npm run build`
- [ ] No TypeScript errors
- [ ] No console warnings
- [ ] All tests passing: `npm run test`

### Zoom Integration
- [ ] Zoom credentials verified
- [ ] Zoom API tests passing
- [ ] Scopes cleaned up (only 4 essential)
- [ ] OAuth 2.0 configured (optional)
- [ ] Meeting creation tested

### Database
- [ ] All migrations applied
- [ ] Database backups created
- [ ] Row-level security (RLS) enabled
- [ ] Indexes created for performance
- [ ] Connection pooling configured

### Payment Processing
- [ ] PayPal live credentials configured
- [ ] Stripe configured (if using)
- [ ] Webhook endpoints secured
- [ ] Payment logging enabled
- [ ] Refund process tested

### Email & Notifications
- [ ] SMTP configured
- [ ] Email templates tested
- [ ] User notifications working
- [ ] Admin alerts configured
- [ ] Error notifications enabled

### Security
- [ ] HTTPS enforced
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Input validation working
- [ ] SQL injection prevention
- [ ] XSS protection enabled

### Monitoring & Logging
- [ ] Error logging configured
- [ ] User activity logging
- [ ] Performance monitoring
- [ ] Uptime monitoring
- [ ] Backup verification

---

## 📋 Deployment Checklist (Before Going Live)

### Code Preparation
```bash
# 1. Clean up any debug files
rm server/test-zoom-connection.js
rm server/debug-zoom-auth.js

# 2. Verify all changes committed
git status
git log --oneline -10

# 3. Create deployment branch
git checkout -b deploy/production
```

### Database Preparation
```bash
# 1. Create backup
pg_dump database_name > backup_$(date +%Y%m%d).sql

# 2. Verify all migrations applied
npm run migrate:status

# 3. Test database connection
npm run test:db
```

### Environment Setup
```
# Create production .env with:
NODE_ENV=production
PORT=5000
DATABASE_URL=postgresql://...
JWT_SECRET=[generate new secure key]
ZOOM_ACCOUNT_ID=YOUR_ZOOM_ACCOUNT_ID
ZOOM_CLIENT_ID=YOUR_ZOOM_CLIENT_ID
ZOOM_CLIENT_SECRET=YOUR_ZOOM_CLIENT_SECRET
PAYPAL_MODE=live
PAYPAL_CLIENT_ID=[live credentials]
PAYPAL_CLIENT_SECRET=[live credentials]
[... all other secrets]
```

### Build Verification
```bash
# 1. Install dependencies
npm install --production

# 2. Build application
npm run build

# 3. Verify build output
ls -la dist/
```

### Testing Pre-Deployment
```bash
# 1. Run all tests
npm test

# 2. Test Zoom integration
node server/test-zoom-connection.js

# 3. Test database
npm run test:db

# 4. Test payment processing
npm run test:payments
```

---

## 🌐 Deployment Steps

### Option 1: Deploy to VPS/Dedicated Server

#### Step 1: Connect to Server
```bash
ssh user@your-domain.com
cd /var/www/your-app
```

#### Step 2: Pull Latest Code
```bash
git clone https://github.com/your-org/my-other-project.git
cd my-other-project
git checkout deploy/production
```

#### Step 3: Install Dependencies
```bash
npm install --production
```

#### Step 4: Configure Environment
```bash
# Copy production .env
cp .env.production .env

# Set correct permissions
chmod 600 .env
```

#### Step 5: Run Database Migrations
```bash
npm run migrate:latest
```

#### Step 6: Build Application
```bash
npm run build
```

#### Step 7: Start Application
```bash
# Using PM2 (recommended)
npm install -g pm2
pm2 start npm --name "lms" -- start
pm2 save
pm2 startup

# Or using systemd
sudo systemctl start lms
sudo systemctl enable lms
```

#### Step 8: Configure Nginx
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### Option 2: Deploy to Docker

#### Step 1: Create Dockerfile
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .
RUN npm run build

EXPOSE 5000

CMD ["npm", "start"]
```

#### Step 2: Create Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://...
      # ... all other env vars
    depends_on:
      - db
      - redis

  db:
    image: postgres:14-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=lms

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### Step 3: Deploy
```bash
docker-compose up -d
```

### Option 3: Deploy to Vercel/AWS/Heroku

#### Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

#### AWS
```bash
# Using Elastic Beanstalk
eb init
eb create production-env
eb deploy
```

#### Heroku
```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set NODE_ENV=production
heroku config:set DATABASE_URL=...

# Deploy
git push heroku main
```

---

## 🔍 Post-Deployment Verification

### Application Health
```bash
# Check app is running
curl https://your-domain.com/api/health

# Expected: { "status": "ok" }
```

### Zoom Integration
```bash
# Verify Zoom is connected
curl https://your-domain.com/api/zoom/user \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: User info returned
```

### Database Connection
```bash
# Check database is accessible
npm run test:db

# Expected: Connection successful
```

### Payment Processing
```bash
# Test PayPal webhook
curl -X POST https://your-domain.com/api/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{"event_type": "PAYMENT.COMPLETED"}'
```

### SSL Certificate
```bash
# Verify SSL
curl -I https://your-domain.com

# Expected: HTTP/2 200
```

---

## 📊 Monitoring Setup

### Application Monitoring
```bash
# Install PM2 monitoring
pm2 install pm2-auto-pull

# View logs
pm2 logs
pm2 monit
```

### Error Tracking
```
# Setup Sentry (optional)
npm install @sentry/node

# Configure in app
import * as Sentry from "@sentry/node";
Sentry.init({ dsn: "YOUR_SENTRY_DSN" });
```

### Performance Monitoring
```
# Setup New Relic (optional)
npm install newrelic

# Configure in app.js
require('newrelic');
```

### Uptime Monitoring
- Use: UptimeRobot, Pingdom, or similar
- Monitor: https://your-domain.com/api/health
- Alert on: Downtime > 5 minutes

---

## 🔐 Security Hardening

### Before Going Live

1. **SSL/TLS**
   ```bash
   # Use Let's Encrypt
   certbot certonly --standalone -d your-domain.com
   ```

2. **Environment Variables**
   - Never commit .env to git
   - Use `.env.example` for reference
   - All secrets stored securely

3. **Database Security**
   - Disable public access
   - Use VPC/private subnets
   - Strong password
   - Regular backups

4. **API Security**
   - Rate limiting enabled
   - CORS configured
   - Input validation
   - SQL injection prevention
   - XSS protection

5. **Backup Strategy**
   - Daily database backups
   - Store off-site
   - Test restore procedure
   - Document recovery time

---

## 📈 Performance Optimization

Before production:

1. **Database**
   ```sql
   -- Create indexes
   CREATE INDEX idx_user_email ON users(email);
   CREATE INDEX idx_course_instructor ON courses(instructor_id);
   CREATE INDEX idx_enrollment_user ON enrollments(user_id);
   ```

2. **Caching**
   ```bash
   # Enable Redis caching
   REDIS_URL=redis://localhost:6379
   ```

3. **CDN**
   - Use Cloudflare or similar
   - Cache static assets
   - Enable compression

4. **Database Pooling**
   ```js
   // Pool config in database.js
   const pool = new Pool({
     max: 20,
     idleTimeoutMillis: 30000,
     connectionTimeoutMillis: 2000,
   });
   ```

---

## 🚨 Rollback Plan

If deployment fails:

```bash
# 1. Stop application
pm2 stop lms

# 2. Revert code
git revert HEAD
git push

# 3. Restore database backup
psql database_name < backup_YYYYMMDD.sql

# 4. Restart application
pm2 start lms

# 5. Verify health
curl https://your-domain.com/api/health
```

---

## 📝 Post-Deployment Tasks

After going live:

- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Test user workflows
- [ ] Verify emails sending
- [ ] Test payment processing
- [ ] Check Zoom integration
- [ ] Monitor database size
- [ ] Review security logs
- [ ] Update status page
- [ ] Notify stakeholders

---

## 📋 Deployment Checklist Template

```
Date: __________
Deployed by: __________
Version: __________

Pre-Deployment:
☐ Code reviewed
☐ Tests passing
☐ Database backed up
☐ Environment variables set
☐ SSL certificate valid

Deployment:
☐ Code deployed
☐ Migrations run
☐ Build successful
☐ Application started
☐ Health check passing

Post-Deployment:
☐ Zoom integration verified
☐ Payments tested
☐ Videos accessible
☐ Users can login
☐ Emails sending
☐ No errors in logs
☐ Performance acceptable

Issues Found: __________
Resolution: __________
Approved by: __________
```

---

## 🎯 Success Criteria

Production deployment is successful when:

✅ Application loads without errors
✅ All features functional
✅ API endpoints responding
✅ Database queries fast
✅ Zoom integration working
✅ Payments processing
✅ Emails sending
✅ Security measures active
✅ Monitoring configured
✅ No critical issues in logs

---

## 📞 Support

**During Deployment**:
- Check logs: `pm2 logs`
- Verify health: `curl https://domain/api/health`
- Check database: `psql -l`
- Monitor resources: `top`, `df -h`

**After Issues**:
- Review error logs
- Check recent deployments
- Verify configuration
- Test in staging first
- Rollback if necessary

---

**Ready to Deploy?** Follow this guide step by step! 🚀
