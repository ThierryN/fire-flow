# 🚢 Deployment Guide

This guide covers deploying the Melchizedek Priests Ministry MERN stack application to production.

## 📋 Prerequisites

- Node.js 18+ installed
- MongoDB database (MongoDB Atlas recommended)
- Domain name (optional but recommended)
- Git repository

## 🚀 Quick Deployment Options

### Option 1: Vercel + Railway (Recommended)

#### Frontend Deployment (Vercel)
1. **Connect to Vercel**
   ```bash
   # Install Vercel CLI
   npm i -g vercel

   # Login to Vercel
   vercel login

   # Deploy frontend
   cd client
   vercel --prod
   ```

2. **Configure Environment Variables**
   In Vercel dashboard, add:
   ```
   VITE_API_URL=https://your-backend-url.vercel.app/api
   VITE_STRIPE_PUBLISHABLE_KEY=pk_live_...
   ```

#### Backend Deployment (Railway)
1. **Connect to Railway**
   - Go to [Railway.app](https://railway.app)
   - Connect your GitHub repository
   - Railway will auto-detect and deploy

2. **Environment Variables**
   Set these in Railway:
   ```
   NODE_ENV=production
   PORT=5000
   MONGO_URI=mongodb+srv://...
   JWT_SECRET=your-secret-key
   STRIPE_SECRET_KEY=sk_live_...
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASS=your-app-password
   ```

### Option 2: Netlify + Render

#### Frontend Deployment (Netlify)
1. **Connect Repository**
   - Go to [Netlify.com](https://netlify.com)
   - Connect GitHub repository
   - Set build command: `npm run build`
   - Set publish directory: `client/dist`

2. **Environment Variables**
   ```
   VITE_API_URL=https://your-backend.onrender.com/api
   VITE_STRIPE_PUBLISHABLE_KEY=pk_live_...
   ```

#### Backend Deployment (Render)
1. **Create Web Service**
   - Go to [Render.com](https://render.com)
   - Create new Web Service
   - Connect GitHub repository
   - Set build command: `npm install`
   - Set start command: `npm start`

2. **Environment Variables**
   Same as Railway configuration above.

## 🔧 Manual Deployment

### 1. Environment Setup

Create `.env` files in both `client/` and `server/` directories:

**server/.env**
```env
NODE_ENV=production
PORT=5000
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/dbname
JWT_SECRET=your-super-secret-jwt-key
JWT_EXPIRE=30d
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
EMAIL_FROM=noreply@melchizedekpriests.com
```

**client/.env**
```env
VITE_API_URL=https://your-domain.com/api
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_...
VITE_APP_NAME=Melchizedek Priests Ministry
```

### 2. Build Application

```bash
# Install all dependencies
npm run install-all

# Build frontend
npm run build

# Start production servers
npm start
```

### 3. Server Configuration

For production servers, configure:

**Nginx Configuration** (`/etc/nginx/sites-available/melchizedekpriests.com`)
```nginx
server {
    listen 80;
    server_name melchizedekpriests.com www.melchizedekpriests.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**PM2 Configuration** (`ecosystem.config.js`)
```javascript
module.exports = {
  apps: [
    {
      name: 'melchizedek-client',
      script: 'npm start',
      cwd: '/path/to/client',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    },
    {
      name: 'melchizedek-server',
      script: 'npm start',
      cwd: '/path/to/server',
      env: {
        NODE_ENV: 'production',
        PORT: 5000
      }
    }
  ]
};
```

## 🔒 Security Checklist

- [ ] HTTPS enabled (Let's Encrypt recommended)
- [ ] Environment variables properly set
- [ ] Database secured with IP whitelisting
- [ ] JWT secrets are strong and unique
- [ ] CORS configured for production domain
- [ ] Rate limiting implemented
- [ ] Security headers set (helmet.js)
- [ ] Regular security updates scheduled

## 📊 Monitoring & Maintenance

### Health Checks
- Frontend: `https://yourdomain.com/health`
- Backend: `https://yourdomain.com/api/health`

### Logs
```bash
# PM2 logs
pm2 logs

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Backups
```bash
# MongoDB Atlas automatic backups recommended
# Or manual backup script
mongodump --db yourdb --out /path/to/backup/$(date +%Y%m%d)
```

## 🚨 Troubleshooting

### Common Issues

**Build Fails**
```bash
# Clear cache and rebuild
rm -rf node_modules client/node_modules server/node_modules
npm run install-all
npm run build
```

**Database Connection Issues**
- Check MongoDB Atlas IP whitelist
- Verify connection string format
- Test connection with MongoDB Compass

**Environment Variables**
```bash
# Check if variables are loaded
node -e "console.log(process.env)"
```

**CORS Issues**
- Update CORS origins in server config
- Check for http vs https mismatches

## 📞 Support

For deployment issues:
- Check application logs
- Verify environment variables
- Test API endpoints with Postman
- Contact [support@melchizedekpriests.com](mailto:support@melchizedekpriests.com)

## 🔄 Updates & Rollbacks

### Zero-Downtime Updates
```bash
# Update code
git pull origin main

# Install dependencies
npm run install-all

# Build and restart
npm run build
pm2 restart all
```

### Rollback
```bash
# Rollback to previous commit
git log --oneline -10
git checkout <commit-hash>
npm run install-all
npm run build
pm2 restart all
```