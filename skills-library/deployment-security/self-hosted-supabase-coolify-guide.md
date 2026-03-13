# Self-Hosted Supabase with Coolify: Complete Setup & Migration Guide

## Table of Contents

1. [Overview](#overview)
2. [Why Self-Host Supabase?](#why-self-host-supabase)
3. [Requirements](#requirements)
4. [Installation: Setting Up Coolify](#installation-setting-up-coolify)
5. [Deploying Supabase on Coolify](#deploying-supabase-on-coolify)
6. [Migrating from Hosted Supabase](#migrating-from-hosted-supabase)
7. [Cost Comparison](#cost-comparison)
8. [Alternative Self-Hosting Solutions](#alternative-self-hosting-solutions)
9. [Best Practices](#best-practices)
10. [Security Considerations](#security-considerations)
11. [Troubleshooting](#troubleshooting)
12. [Resources](#resources)

---

## Overview

### What is Coolify?

**Coolify** is an open-source, self-hostable alternative to Heroku, Netlify, and Vercel. It helps you manage servers, applications, and databases on your own hardware with just an SSH connection.

**Key Features:**
- 🐳 **Docker-based**: All services run in containers
- 🎨 **Beautiful UI**: No need to write Dockerfiles
- 🔒 **Auto-SSL**: Automatic Let's Encrypt certificate setup and renewal
- 🔄 **Git Integration**: Works with GitHub, GitLab, Bitbucket, Gitea
- 📊 **One-Click Services**: Deploy databases, apps, and services instantly
- 🆓 **100% Free**: All features included, no premium tiers

### What is Supabase?

**Supabase** is an open-source Firebase alternative that provides:
- 🗄️ **PostgreSQL Database**: Full-featured relational database
- 🔐 **Authentication**: Built-in user authentication system
- 📦 **Storage**: File storage and CDN
- ⚡ **Real-time**: Live database subscriptions
- 🔧 **Auto-generated APIs**: RESTful and GraphQL APIs
- 🎛️ **Studio**: Web-based database management interface

### Why This Combination?

Coolify + Supabase = **Full-stack backend infrastructure** you control:
- Deploy Supabase with a single click in Coolify
- Manage everything through a beautiful web interface
- Avoid vendor lock-in and reduce costs significantly
- Complete control over your data and infrastructure

---

## Why Self-Host Supabase?

### Cost Savings (50-80% reduction)

**Supabase Cloud Pricing:**
- Free tier: Limited to 500MB database, paused after 7 days inactivity
- Pro tier: $25/month (includes 8GB database, 100GB bandwidth)
- Team tier: $599/month
- Enterprise: Custom pricing (can exceed $410/month for high specs)

**Self-Hosted VPS Costs:**

| VPS Specs | Provider Examples | Monthly Cost | Best For |
|-----------|------------------|--------------|----------|
| 2 vCPU, 4GB RAM, 80GB SSD | DigitalOcean, Linode, Vultr | $12-20 | Development/Testing |
| 4 vCPU, 8GB RAM, 160GB SSD | Hetzner, OVH | $20-30 | Small Production Apps |
| 8 vCPU, 32GB RAM, 320GB SSD | Hetzner | ~$50 | Large Production Apps |
| 16 vCPU, 64GB RAM, 640GB SSD | Dedicated servers | $80-150 | Enterprise Scale |

**Real-World Example:**
- Supabase Cloud (100GB database + moderate traffic): **$200+/month**
- Self-hosted (same specs): **$40-60/month**
- **Savings: $140-160/month = $1,680-1,920/year** 💰

### Full Control & Privacy

- **Data sovereignty**: Your data stays on servers you control
- **Custom configurations**: Tune PostgreSQL, adjust resource limits
- **No rate limits**: No artificial API throttling or connection limits
- **Backup control**: Implement your own backup strategy
- **Compliance**: Meet specific regulatory requirements (HIPAA, GDPR, etc.)

### No Vendor Lock-In

- **Portable**: Move to any server or cloud provider
- **Predictable costs**: No surprise bills from bandwidth overages
- **Long-term stability**: Not dependent on Supabase's pricing changes
- **Integration freedom**: Connect to any tools or services

### When to Self-Host vs. Use Cloud

**Use Supabase Cloud if:**
- ✅ Just getting started with a prototype/MVP
- ✅ Don't want to manage infrastructure
- ✅ Need enterprise support and SLA guarantees
- ✅ Database is small (<8GB) and traffic is low

**Self-host if:**
- ✅ Your app has moderate to high usage (>1000 users)
- ✅ Database >10GB or growing rapidly
- ✅ You need full control over data and infrastructure
- ✅ You have DevOps knowledge or want to learn
- ✅ Want to reduce costs by 50-80%

---

## Requirements

### Hardware Requirements

**Minimum Specs (Development/Testing):**
- CPU: 2 vCPU cores
- RAM: 4 GB
- Storage: 40 GB SSD
- Network: 1 Gbps connection
- **Cost: $12-20/month**

**Recommended Specs (Small Production):**
- CPU: 4 vCPU cores
- RAM: 8 GB
- Storage: 80-160 GB SSD
- Network: 1 Gbps connection
- **Cost: $20-40/month**

**Production Specs (Larger Apps):**
- CPU: 8+ vCPU cores
- RAM: 16-32 GB
- Storage: 160-320 GB SSD
- Network: 1 Gbps connection
- **Cost: $50-100/month**

### Software Requirements

**Operating System (VPS):**
- ✅ Ubuntu 20.04/22.04/24.04 LTS (recommended)
- ✅ Debian 11/12
- ✅ CentOS 8+
- ✅ AlmaLinux, Rocky Linux
- ✅ Fedora

**Prerequisites:**
- SSH access to your VPS
- Root or sudo privileges
- Domain name (optional but recommended for SSL)
- Docker Engine 24+ (Coolify installer handles this)

**Important Notes:**
- ⚠️ Docker installed via **snap is NOT supported**
- ⚠️ Non-LTS Ubuntu versions (e.g., 24.10) require manual installation
- ⚠️ AlmaLinux requires Docker to be pre-installed

### VPS Provider Recommendations

**Budget-Friendly:**
- [Hetzner](https://www.hetzner.com/cloud) - €3.29/mo (4GB RAM) - **Best value**
- [Vultr](https://www.vultr.com/) - $12/mo (4GB RAM)
- [DigitalOcean](https://www.digitalocean.com/) - $18/mo (4GB RAM)

**Developer-Focused:**
- [Linode (Akamai)](https://www.linode.com/) - $12/mo (4GB RAM)
- [Hostinger VPS](https://www.hostinger.com/vps) - Starting at $5.99/mo

**Enterprise:**
- [AWS EC2](https://aws.amazon.com/ec2/)
- [Google Cloud Compute](https://cloud.google.com/compute)
- [Azure Virtual Machines](https://azure.microsoft.com/en-us/products/virtual-machines)

---

## Installation: Setting Up Coolify

### Step 1: Prepare Your VPS

**1.1. Connect to your VPS via SSH:**

```bash
ssh root@your-server-ip
# or
ssh username@your-server-ip
```

**1.2. Update system packages:**

```bash
# For Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# For CentOS/RHEL/AlmaLinux
sudo yum update -y
```

**1.3. Set up firewall (optional but recommended):**

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # Coolify dashboard
sudo ufw enable

# firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### Step 2: Install Coolify (Automatic)

**2.1. Run the official installation script:**

```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

The installer will:
- ✅ Check system requirements
- ✅ Install Docker Engine 24+
- ✅ Install Docker Compose
- ✅ Set up Coolify containers
- ✅ Configure networking

**Installation time: ~2-5 minutes**

**2.2. Verify installation:**

```bash
docker ps
```

You should see Coolify containers running:
```
CONTAINER ID   IMAGE                    STATUS
xxxxx          ghcr.io/coollabsio/coolify   Up 2 minutes
```

### Step 3: Access Coolify Dashboard

**3.1. Open your browser and navigate to:**

```
http://your-server-ip:8000
```

**3.2. Create your admin account:**

⚠️ **CRITICAL**: Register immediately! The first person to access the registration page becomes the admin. If someone else accesses it first, they gain full control of your server.

Fill in:
- Email address
- Password (strong password recommended)
- Server name (optional)

**3.3. (Optional) Set up custom domain:**

If you have a domain name (e.g., `coolify.yourdomain.com`):

1. Create an A record pointing to your server IP:
   ```
   A    coolify    your-server-ip
   ```

2. In Coolify dashboard:
   - Go to **Settings** → **Configuration**
   - Set **Instance Domain** to `coolify.yourdomain.com`
   - Enable **Auto-SSL** for automatic Let's Encrypt certificate

3. Access Coolify at: `https://coolify.yourdomain.com`

### Step 4: Configure Coolify Settings

**4.1. Set up email notifications (optional):**

Go to **Settings** → **Notifications**:
- SMTP server for alerts
- Deployment notifications
- Error notifications

**4.2. Configure backup storage (optional):**

Go to **Settings** → **Backups**:
- S3-compatible storage (AWS S3, MinIO, Backblaze B2)
- Automated backup schedules

**4.3. Add SSH keys (if deploying to multiple servers):**

Go to **Settings** → **SSH Keys**:
- Add private keys for accessing remote servers
- Enable multi-server deployments

---

## Deploying Supabase on Coolify

### Step 1: Create a New Project

**1.1. In Coolify dashboard, click the "Projects" tab**

**1.2. Click "+ Add" button**

**1.3. Provide project details:**
- **Project Name**: `supabase` (or your preferred name)
- **Description**: `Self-hosted Supabase backend`

**1.4. Create or select environment:**
- **Environment Name**: `production` (or `development`, `staging`)
- Click **Continue**

### Step 2: Deploy Supabase Service

**2.1. Inside your project, click "+ Add New Resource"**

**2.2. Select "Services" → "Supabase"**

Coolify provides a pre-configured Supabase template with all required services:
- 🗄️ **PostgreSQL 15** (supabase-db)
- ⚡ **Kong API Gateway** (supabase-kong)
- 🔐 **GoTrue Auth** (supabase-auth)
- 📡 **Realtime Server** (supabase-realtime)
- 🔧 **PostgREST API** (supabase-rest)
- 📦 **Storage Server** (supabase-storage)
- 🎨 **Supabase Studio** (supabase-studio)
- 📊 **Meta API** (supabase-meta)

**2.3. Configure Supabase settings:**

**Required Environment Variables** (Coolify auto-generates most):
- `POSTGRES_PASSWORD` - Database password (auto-generated)
- `JWT_SECRET` - JWT signing secret (auto-generated)
- `ANON_KEY` - Anonymous API key (auto-generated)
- `SERVICE_ROLE_KEY` - Service role API key (auto-generated)
- `SITE_URL` - Your app URL (e.g., `https://yourdomain.com`)
- `DASHBOARD_USERNAME` - Studio login username
- `DASHBOARD_PASSWORD` - Studio login password

**Optional Settings:**
- Custom domain for Studio
- SMTP configuration for auth emails
- Storage bucket settings

**2.4. Click "Deploy" (top-right corner)**

Deployment process:
1. ✅ Pulls Docker images (~2-5 minutes)
2. ✅ Creates Docker network
3. ✅ Starts all services
4. ✅ Initializes PostgreSQL database
5. ✅ Generates API keys and secrets

**Total deployment time: ~5-10 minutes**

### Step 3: Access Supabase Studio

**3.1. Get your Supabase Studio URL:**

In Coolify, go to **Resource Details** → **Domains**:
```
https://supabase-studio-xxxxx.coolify.app
```

Or set up custom domain (recommended):
```
https://supabase.yourdomain.com
```

**3.2. Log in to Supabase Studio:**

- Username: `DASHBOARD_USERNAME` (set in environment variables)
- Password: `DASHBOARD_PASSWORD` (set in environment variables)

⚠️ **IMPORTANT**: Change default credentials immediately after first login!

**3.3. Access your API endpoints:**

```bash
# API URL
https://api-xxxxx.coolify.app

# Anonymous Key (for client-side)
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS...

# Service Role Key (for server-side)
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS...
```

Find these in **Resource Details** → **Environment Variables**

### Step 4: Connect Your Application

**4.1. Install Supabase client library:**

```bash
# JavaScript/TypeScript
npm install @supabase/supabase-js

# Python
pip install supabase

# Dart/Flutter
flutter pub add supabase_flutter
```

**4.2. Initialize Supabase client:**

```typescript
// JavaScript/TypeScript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://api-xxxxx.coolify.app'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

```python
# Python
from supabase import create_client, Client

supabase_url = "https://api-xxxxx.coolify.app"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

supabase: Client = create_client(supabase_url, supabase_key)
```

**4.3. Test connection:**

```typescript
// JavaScript/TypeScript
const { data, error } = await supabase
  .from('test_table')
  .select('*')

console.log('Connection successful:', data)
```

### Step 5: Configure PostgreSQL External Access (Optional)

If you need to connect to PostgreSQL directly (e.g., for migrations, pgAdmin):

**5.1. Edit Docker Compose file:**

In Coolify:
- Go to **Resource Details** → **Configuration**
- Click **"Edit Compose File"**

**5.2. Locate `supabase-db` service and expose port 5432:**

```yaml
supabase-db:
  image: supabase/postgres:15
  ports:
    - "5432:5432"  # Add this line
  environment:
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

**5.3. Open firewall port:**

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 5432/tcp

# firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=5432/tcp
sudo firewall-cmd --reload
```

**5.4. Connect with connection string:**

```
postgresql://postgres:your-password@your-server-ip:5432/postgres
```

⚠️ **Security Warning**: Only expose PostgreSQL port if absolutely necessary. Use SSH tunneling instead:

```bash
# SSH tunnel (more secure)
ssh -L 5432:localhost:5432 username@your-server-ip

# Then connect locally
postgresql://postgres:your-password@localhost:5432/postgres
```

---

## Migrating from Hosted Supabase

### Prerequisites

Before migration:
- ✅ Self-hosted Supabase deployed on Coolify
- ✅ Hosted Supabase project accessible
- ✅ Database backup downloaded
- ✅ PostgreSQL client installed (pg_restore, psql)

### Step 1: Backup Hosted Supabase Database

**1.1. In hosted Supabase dashboard:**

Go to **Settings** → **Database** → **Backups**

**1.2. Download latest backup:**

Click **"Download"** next to the most recent backup:
```
your-project-backup-20251029.backup
```

This is a PostgreSQL custom format backup file.

**1.3. (Alternative) Create manual backup:**

If no recent backup exists:

```bash
# Install PostgreSQL tools
sudo apt install postgresql-client

# Create backup
pg_dump -h db.xxxxxxxxxxxx.supabase.co \
  -U postgres \
  -d postgres \
  -F c \
  -f supabase-backup-$(date +%Y%m%d).backup
```

Enter your database password when prompted.

### Step 2: Prepare Self-Hosted Database for Migration

**2.1. Temporarily expose PostgreSQL port (if not already):**

Follow [Step 5: Configure PostgreSQL External Access](#step-5-configure-postgresql-external-access-optional) above.

**2.2. Get connection details from Coolify:**

Go to **Resource Details** → **Environment Variables**:
- `POSTGRES_HOST`: Your server IP
- `POSTGRES_PORT`: `5432`
- `POSTGRES_USER`: `postgres`
- `POSTGRES_PASSWORD`: (copy this)
- `POSTGRES_DB`: `postgres`

### Step 3: Restore Database

**3.1. Clean existing database (optional, for fresh start):**

```bash
# Connect to database
psql -h your-server-ip -U postgres -d postgres

# Drop all tables in public schema
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

# Exit
\q
```

**3.2. Restore backup:**

```bash
pg_restore -h your-server-ip \
  -U postgres \
  -d postgres \
  --verbose \
  --no-owner \
  --no-acl \
  your-project-backup-20251029.backup
```

Enter password when prompted.

**Restoration time:** Depends on database size (1GB ≈ 5-10 minutes)

**3.3. Verify restoration:**

```bash
# Connect to database
psql -h your-server-ip -U postgres -d postgres

# List tables
\dt

# Count rows in a table (example)
SELECT COUNT(*) FROM your_table_name;

# Exit
\q
```

### Step 4: Migrate Storage Files

**4.1. Download storage files from hosted Supabase:**

There's no official bulk export, so you'll need to:

**Option A: Use Supabase CLI:**

```bash
# Install Supabase CLI
npm install -g supabase

# Login to hosted Supabase
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Download storage files (requires custom script)
# Note: This is a conceptual example
supabase storage download --bucket my-bucket --output ./storage-backup
```

**Option B: Write custom script:**

```typescript
// download-storage.ts
import { createClient } from '@supabase/supabase-js'
import fs from 'fs'
import path from 'path'

const hostedSupabase = createClient(
  'https://xxxxxxxxxxxx.supabase.co',
  'your-service-role-key'
)

async function downloadBucket(bucketName: string) {
  const { data: files, error } = await hostedSupabase
    .storage
    .from(bucketName)
    .list()

  for (const file of files || []) {
    const { data, error } = await hostedSupabase
      .storage
      .from(bucketName)
      .download(file.name)

    if (data) {
      fs.writeFileSync(
        path.join('./storage-backup', bucketName, file.name),
        Buffer.from(await data.arrayBuffer())
      )
    }
  }
}

// Run for each bucket
downloadBucket('avatars')
downloadBucket('documents')
```

**4.2. Upload files to self-hosted Supabase:**

```typescript
// upload-storage.ts
import { createClient } from '@supabase/supabase-js'
import fs from 'fs'
import path from 'path'

const selfHostedSupabase = createClient(
  'https://api-xxxxx.coolify.app',
  'your-service-role-key'
)

async function uploadBucket(bucketName: string, localPath: string) {
  const files = fs.readdirSync(localPath)

  for (const file of files) {
    const fileBuffer = fs.readFileSync(path.join(localPath, file))

    const { data, error } = await selfHostedSupabase
      .storage
      .from(bucketName)
      .upload(file, fileBuffer, {
        cacheControl: '3600',
        upsert: true
      })

    console.log(`Uploaded: ${file}`)
  }
}

// Run for each bucket
uploadBucket('avatars', './storage-backup/avatars')
uploadBucket('documents', './storage-backup/documents')
```

### Step 5: Update Application Configuration

**5.1. Update environment variables in your app:**

```bash
# .env or .env.local

# OLD (Hosted Supabase)
# NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
# NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# NEW (Self-hosted on Coolify)
NEXT_PUBLIC_SUPABASE_URL=https://api-xxxxx.coolify.app
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**5.2. Redeploy your application:**

```bash
npm run build
npm run start
# or
vercel --prod
# or
git push (if using CI/CD)
```

**5.3. Test all functionality:**

- ✅ User authentication (login, signup, logout)
- ✅ Database queries (read, write, update, delete)
- ✅ Real-time subscriptions
- ✅ File uploads and downloads
- ✅ Edge Functions (if using)

### Step 6: Update DNS (If Using Custom Domains)

**6.1. For API domain:**

Update your DNS A record:
```
A    api    your-server-ip
```

**6.2. For Supabase Studio domain:**

```
A    supabase    your-server-ip
```

**6.3. Wait for DNS propagation (5-60 minutes)**

**6.4. Verify with:**

```bash
nslookup api.yourdomain.com
nslookup supabase.yourdomain.com
```

### Step 7: Clean Up Hosted Supabase (Optional)

⚠️ **Only after verifying everything works on self-hosted!**

**7.1. In hosted Supabase dashboard:**

Go to **Settings** → **General** → **Pause Project**

**7.2. After 30 days of verification:**

Go to **Settings** → **General** → **Delete Project**

This will:
- Stop all billing
- Delete all data permanently
- Free up your project slot

---

## Cost Comparison

### Real-World Cost Analysis

Let's compare costs for a typical production application:

**Application Profile:**
- Database: 25 GB
- Monthly active users: 5,000
- API requests: 10 million/month
- Storage: 50 GB files
- Bandwidth: 500 GB/month

### Supabase Cloud Costs

**Pro Plan ($25/month base) + Overages:**

| Resource | Included | Used | Overage Cost | Total |
|----------|----------|------|--------------|-------|
| Base price | - | - | - | $25 |
| Database | 8 GB | 25 GB | $0.125/GB × 17 GB | $2.13 |
| Bandwidth | 250 GB | 500 GB | $0.09/GB × 250 GB | $22.50 |
| Storage | 100 GB | 50 GB | Included | $0 |
| API requests | Unlimited | 10M | Included | $0 |

**Total: ~$50/month** (for this moderate usage)

For larger applications (100GB database, 2TB bandwidth): **$200-400/month**

### Self-Hosted Costs

**VPS Cost (Hetzner CPX31):**

| Specs | Monthly Cost |
|-------|-------------|
| 4 vCPU | |
| 8 GB RAM | |
| 160 GB SSD | |
| 20 TB bandwidth | **€15.90 (~$17.50)** |

**Additional Costs:**
- Domain name: $12/year = $1/month
- Backups (optional): $5/month (Backblaze B2)
- **Total: ~$24/month**

### Savings Summary

| Scenario | Supabase Cloud | Self-Hosted | Savings/Year |
|----------|---------------|-------------|--------------|
| Small app (5GB DB) | $25/mo | $12/mo | **$156** |
| Medium app (25GB DB) | $50/mo | $24/mo | **$312** |
| Large app (100GB DB) | $200/mo | $50/mo | **$1,800** |
| Enterprise (500GB DB) | $600+/mo | $100/mo | **$6,000+** |

**ROI Calculation:**

Even accounting for ~5 hours/month of DevOps maintenance:
- Cost savings: $26/month
- Time invested: 5 hours × $50/hr = $250 setup + $20/mo maintenance
- Break-even: Month 10
- **Year 1 net savings: ~$62**
- **Year 2+ net savings: ~$312/year** (no setup cost)

For larger applications, savings are even more dramatic.

---

## Alternative Self-Hosting Solutions

### Comparison Table

| Platform | Best For | Pros | Cons | Cost |
|----------|----------|------|------|------|
| **Coolify** | Modern UI, ease of use | Beautiful dashboard, active development, Docker Compose support | Younger project (less mature) | Free (open-source) |
| **CapRover** | Stability, multi-server | Mature (100M+ downloads), extensive app library, auto-scaling | Basic UI, limited features vs Coolify | Free (open-source) |
| **Dokploy** | Lightweight, Git-based | Simple, good Docker integration, lightweight | Smaller community | Free (open-source) |
| **Dokku** | Minimalism | Smallest footprint, Heroku-like | Command-line only, less features | Free (open-source) |
| **Portainer** | Docker management | Excellent container management, visual interface | Not a full PaaS | Free + Paid tiers |

### Detailed Alternatives

#### 1. CapRover

**What it is:** A mature, stable PaaS with 100M+ Docker Hub downloads.

**Strengths:**
- ✅ Battle-tested stability
- ✅ One-click app deployments (100+ apps)
- ✅ Multi-server clustering with Docker Swarm
- ✅ Built-in load balancer
- ✅ Excellent for production

**Weaknesses:**
- ❌ Basic UI (functional but dated)
- ❌ Limited documentation
- ❌ Less active development than Coolify
- ❌ Custom deployment format (captain files)

**Installation:**

```bash
docker run -p 80:80 -p 443:443 -p 3000:3000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /captain:/captain \
  caprover/caprover
```

Access at: `http://your-server-ip:3000`

**Best for:** Teams prioritizing stability over modern UI.

#### 2. Dokploy

**What it is:** A lightweight, Git-focused deployment platform.

**Strengths:**
- ✅ Excellent Docker Compose support
- ✅ Simple, clean interface
- ✅ Good Git integration
- ✅ Lightweight resource usage
- ✅ Native multi-server support

**Weaknesses:**
- ❌ Smaller community
- ❌ Fewer built-in services
- ❌ Limited monitoring compared to Coolify

**Installation:**

```bash
curl -sSL https://dokploy.com/install.sh | sh
```

Access at: `http://your-server-ip:3000`

**Best for:** Developers who prioritize simplicity and Git workflows.

#### 3. Dokku

**What it is:** The smallest PaaS you've ever seen (Heroku-inspired).

**Strengths:**
- ✅ Minimal resource footprint
- ✅ Heroku-like buildpack support
- ✅ Simple git push deployments
- ✅ Mature and stable

**Weaknesses:**
- ❌ Command-line only (no web UI)
- ❌ Manual configuration
- ❌ Steeper learning curve
- ❌ No visual monitoring

**Installation:**

```bash
wget -NP . https://dokku.com/install/v0.32.3/bootstrap.sh
sudo DOKKU_TAG=v0.32.3 bash bootstrap.sh
```

**Best for:** Terminal enthusiasts and minimalists.

#### 4. Direct Docker Compose

**What it is:** Managing Supabase directly with Docker Compose (no PaaS layer).

**Strengths:**
- ✅ Full control over every configuration
- ✅ No abstraction layer
- ✅ Lightest resource usage
- ✅ Official Supabase method

**Weaknesses:**
- ❌ No web UI
- ❌ Manual SSL certificate setup
- ❌ Requires Docker/DevOps knowledge
- ❌ Manual updates and monitoring

**Installation:**

```bash
# Clone Supabase repository
git clone --depth 1 https://github.com/supabase/supabase
cd supabase/docker

# Copy example env
cp .env.example .env

# Edit environment variables
nano .env

# Start services
docker compose up -d
```

Access Studio at: `http://localhost:3000`

**Best for:** DevOps engineers who want direct control.

### Recommendation Matrix

| Your Priority | Recommended Platform |
|--------------|---------------------|
| 🎨 **Modern UI & ease of use** | **Coolify** |
| 🛡️ **Stability & maturity** | CapRover |
| 🪶 **Lightweight & simple** | Dokploy |
| 💻 **Terminal-only, minimal** | Dokku |
| 🔧 **Full control, no PaaS** | Direct Docker Compose |

**Our Recommendation:** **Coolify** strikes the best balance for most teams:
- Modern, intuitive interface
- Active development and community
- Docker Compose support
- Suitable for production

---

## Best Practices

### 1. Security Hardening

**Change default credentials immediately:**

```bash
# In Coolify, update Supabase environment variables:
DASHBOARD_USERNAME=your-secure-username
DASHBOARD_PASSWORD=your-strong-password-here

# Regenerate API keys (after initial setup)
JWT_SECRET=<new-random-64-char-string>
```

**Enable firewall:**

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

**Restrict PostgreSQL access:**

```yaml
# In docker-compose.yml, do NOT expose port 5432 publicly
# Use SSH tunnel instead:
ssh -L 5432:localhost:5432 username@your-server-ip
```

**Use strong passwords:**

```bash
# Generate secure passwords
openssl rand -base64 32
```

### 2. Backup Strategy

**Automated PostgreSQL backups:**

```bash
# Create backup script
cat > /root/backup-supabase.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/supabase"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
docker exec supabase-db pg_dump -U postgres postgres > \
  $BACKUP_DIR/postgres-$TIMESTAMP.sql

# Compress backup
gzip $BACKUP_DIR/postgres-$TIMESTAMP.sql

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
EOF

chmod +x /root/backup-supabase.sh
```

**Schedule with cron:**

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /root/backup-supabase.sh
```

**Offsite backup (S3):**

```bash
# Install AWS CLI
sudo apt install awscli

# Configure AWS credentials
aws configure

# Upload to S3 (add to backup script)
aws s3 cp $BACKUP_DIR/postgres-$TIMESTAMP.sql.gz \
  s3://your-bucket/supabase-backups/
```

### 3. Monitoring & Alerts

**Set up health checks in Coolify:**

Go to **Resource Details** → **Health Checks**:
- HTTP endpoint: `https://api-xxxxx.coolify.app/health`
- Check interval: 60 seconds
- Failure threshold: 3 consecutive failures

**Monitor disk usage:**

```bash
# Check disk space
df -h

# Set up alert (example with simple script)
cat > /root/check-disk.sh << 'EOF'
#!/bin/bash
THRESHOLD=80
USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

if [ $USAGE -gt $THRESHOLD ]; then
  echo "Disk usage is $USAGE% (threshold: $THRESHOLD%)" | \
    mail -s "Disk Space Alert" your-email@example.com
fi
EOF
```

**Docker container monitoring:**

```bash
# Check container health
docker ps --filter "name=supabase"

# View logs
docker logs supabase-db --tail 100 -f
docker logs supabase-kong --tail 100 -f
```

### 4. Performance Optimization

**Increase PostgreSQL shared_buffers:**

In Coolify, edit Docker Compose → `supabase-db` service:

```yaml
supabase-db:
  image: supabase/postgres:15
  command: >
    postgres
    -c shared_buffers=512MB
    -c effective_cache_size=2GB
    -c maintenance_work_mem=128MB
    -c max_connections=200
```

**Enable Redis caching (optional):**

Add Redis to your Coolify project:
- Go to **Resource** → **Add Database** → **Redis**
- Update Supabase environment variables to use Redis

**Use CDN for storage:**

```typescript
// Configure Supabase storage with CDN
const { data, error } = await supabase
  .storage
  .from('avatars')
  .getPublicUrl('avatar.png', {
    transform: {
      width: 200,
      height: 200
    }
  })
```

### 5. Update Management

**Update Coolify:**

```bash
# Coolify auto-updates by default
# To manually trigger update:
docker exec coolify php artisan coolify:update
```

**Update Supabase:**

In Coolify:
1. Go to **Resource Details**
2. Edit **Docker Compose file**
3. Update image tags to latest versions:
   ```yaml
   supabase-db:
     image: supabase/postgres:15.1.0.147  # Update version
   ```
4. Click **"Redeploy"**

**Test updates in staging first:**

Create a separate Coolify project:
- Name: `supabase-staging`
- Environment: `staging`
- Restore database backup
- Test thoroughly before updating production

### 6. Scaling Strategies

**Vertical Scaling (increase resources):**

Upgrade your VPS:
- Hetzner: Can resize without data loss
- DigitalOcean: Resize droplet
- AWS: Change EC2 instance type

**Horizontal Scaling (multiple servers):**

Use Coolify's multi-server support:
1. Add additional servers in **Settings** → **Servers**
2. Deploy read replicas for PostgreSQL
3. Use load balancer (Kong is included in Supabase)

**Database Connection Pooling:**

Supabase includes PgBouncer for connection pooling:
```
# Connection string for pooled connections
postgresql://postgres:password@your-server:6543/postgres
```

---

## Security Considerations

### 1. Network Security

**Use SSL/TLS everywhere:**

In Coolify:
- Enable **Auto-SSL** for all domains
- Force HTTPS redirects
- Use Let's Encrypt certificates (auto-renewed)

**Implement IP whitelisting (optional):**

```bash
# UFW example - allow only specific IPs to access PostgreSQL
sudo ufw deny 5432/tcp
sudo ufw allow from 203.0.113.100 to any port 5432
```

**Use SSH keys instead of passwords:**

```bash
# Disable password authentication
sudo nano /etc/ssh/sshd_config

# Set:
PasswordAuthentication no
PubkeyAuthentication yes

# Restart SSH
sudo systemctl restart sshd
```

### 2. Database Security

**Enable Row Level Security (RLS):**

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY "Users can only see their own data"
ON users
FOR SELECT
USING (auth.uid() = id);
```

**Use service role key only on server-side:**

```typescript
// ❌ NEVER expose service role key in client-side code
const supabase = createClient(url, serviceRoleKey) // DANGEROUS!

// ✅ Use anonymous key on client-side
const supabase = createClient(url, anonKey) // SAFE
```

**Encrypt sensitive data:**

```sql
-- Use pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt column
UPDATE users
SET ssn = pgp_sym_encrypt(ssn, 'encryption-key');

-- Decrypt when querying
SELECT pgp_sym_decrypt(ssn::bytea, 'encryption-key')
FROM users;
```

### 3. Authentication Security

**Configure JWT expiration:**

In Coolify environment variables:

```bash
JWT_EXP=3600  # 1 hour (default)
```

**Enable MFA (Multi-Factor Authentication):**

```typescript
// Enable MFA for a user
const { data, error } = await supabase.auth.mfa.enroll({
  factorType: 'totp',
  friendlyName: 'My Phone'
})
```

**Configure password requirements:**

In Supabase Studio:
- Go to **Authentication** → **Settings**
- Set minimum password length
- Require special characters

### 4. API Security

**Rate limiting (Kong includes this):**

```yaml
# In Coolify, edit Kong configuration
_format_version: "2.1"
services:
  - name: supabase-rest
    plugins:
      - name: rate-limiting
        config:
          minute: 100
          hour: 1000
```

**CORS configuration:**

```bash
# In Coolify environment variables
ADDITIONAL_REDIRECT_URLS=https://yourdomain.com,https://app.yourdomain.com
```

**API key rotation:**

```bash
# Periodically regenerate JWT_SECRET
# Then update all client applications
JWT_SECRET=<new-64-char-secret>
```

### 5. Compliance & Data Privacy

**GDPR Compliance:**

```typescript
// Implement data export
const { data, error } = await supabase
  .from('users')
  .select('*')
  .eq('id', userId)

// Implement right to deletion
const { error } = await supabase
  .from('users')
  .delete()
  .eq('id', userId)
```

**Audit logging:**

```sql
-- Create audit log table
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  action TEXT,
  table_name TEXT,
  record_id UUID,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Create trigger function
CREATE OR REPLACE FUNCTION log_audit()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_logs (user_id, action, table_name, record_id)
  VALUES (auth.uid(), TG_OP, TG_TABLE_NAME, NEW.id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach to tables
CREATE TRIGGER users_audit
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION log_audit();
```

---

## Troubleshooting

### Common Issues & Solutions

#### 1. Coolify Installation Fails

**Error:** `Docker installation failed`

**Solution:**
```bash
# Manually install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verify installation
docker --version

# Re-run Coolify installer
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

**Error:** `Permission denied (Docker socket)`

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker
```

#### 2. Supabase Deployment Issues

**Error:** `Service health check failed`

**Solution:**
```bash
# Check container logs
docker logs supabase-db
docker logs supabase-kong

# Common causes:
# - Insufficient RAM (need 4GB+)
# - Port conflicts (5432, 8000, 8443)
# - Invalid environment variables

# Check port usage
sudo netstat -tulpn | grep LISTEN
```

**Error:** `Database initialization failed`

**Solution:**
```bash
# Restart PostgreSQL container
docker restart supabase-db

# Check PostgreSQL logs
docker logs supabase-db --tail 100

# If corrupted, redeploy:
# In Coolify: Resource → Force Redeploy
```

#### 3. Connection Issues

**Error:** `Could not connect to Supabase`

**Solution:**

Check firewall:
```bash
sudo ufw status
# Ensure ports 80 and 443 are allowed
```

Check DNS:
```bash
nslookup api-xxxxx.coolify.app
# Should return your server IP
```

Check SSL certificate:
```bash
curl -I https://api-xxxxx.coolify.app
# Should return 200 OK
```

**Error:** `CORS policy blocked`

**Solution:**

Update environment variables in Coolify:
```bash
ADDITIONAL_REDIRECT_URLS=https://yourdomain.com,https://app.yourdomain.com
```

Restart Supabase services.

#### 4. Performance Issues

**Error:** `Database queries are slow`

**Solution:**

Increase shared_buffers:
```yaml
# Edit Docker Compose
supabase-db:
  command: postgres -c shared_buffers=512MB -c effective_cache_size=2GB
```

Add indexes:
```sql
-- Find missing indexes
SELECT schemaname, tablename, attname
FROM pg_stats
WHERE correlation < 0.1
  AND n_distinct > 100;

-- Create index
CREATE INDEX idx_users_email ON users(email);
```

**Error:** `Server running out of disk space`

**Solution:**

Clean Docker:
```bash
# Remove unused containers, images, volumes
docker system prune -a --volumes

# Check disk usage
df -h
```

Resize VPS storage (depends on provider).

#### 5. Migration Issues

**Error:** `pg_restore: error: could not connect`

**Solution:**

Verify PostgreSQL is accessible:
```bash
# Test connection
psql -h your-server-ip -U postgres -d postgres

# If fails, check:
# 1. Port 5432 exposed in Docker Compose
# 2. Firewall allows port 5432
# 3. Correct password
```

**Error:** `Restore failed: permission denied`

**Solution:**

Use `--no-owner` and `--no-acl` flags:
```bash
pg_restore \
  --no-owner \
  --no-acl \
  -h your-server-ip \
  -U postgres \
  -d postgres \
  backup.backup
```

#### 6. SSL Certificate Issues

**Error:** `Certificate validation failed`

**Solution:**

Regenerate certificate in Coolify:
1. Go to **Resource Details** → **Domains**
2. Click **"Generate Certificate"**
3. Wait 1-2 minutes

Check Let's Encrypt rate limits:
```bash
# Let's Encrypt limits: 5 certificates per domain per week
# If hit limit, wait 7 days or use staging environment
```

---

## Resources

### Official Documentation

- **Coolify Docs**: https://coolify.io/docs
- **Supabase Docs**: https://supabase.com/docs
- **Supabase Self-Hosting**: https://supabase.com/docs/guides/self-hosting

### Tutorials & Guides

- [How to self-host Supabase with Coolify](https://msof.me/blog/how-to-self-host-supabase-with-coolify-and-migrate-your-project-from-the-official-supabase-platform/)
- [Coolify + Supabase on DEV.to](https://dev.to/musayazlik/harnessing-the-power-of-self-hosted-supabase-on-coolify-a-complete-guide-to-server-setup-and-oauth-34c5)
- [Self-host Supabase for $3](https://blog.melbournedev.com/blog/post/how-to-self-host-supabase-for-3-dollars)

### GitHub Repositories

- **Coolify**: https://github.com/coollabsio/coolify
- **Supabase**: https://github.com/supabase/supabase
- **Supabase Docker**: https://github.com/supabase/supabase/tree/master/docker

### Community

- **Coolify Discord**: https://discord.com/invite/coollabs
- **Supabase Discord**: https://discord.supabase.com
- **Supabase GitHub Discussions**: https://github.com/orgs/supabase/discussions

### VPS Providers

- **Hetzner**: https://www.hetzner.com/cloud (Best value)
- **DigitalOcean**: https://www.digitalocean.com
- **Vultr**: https://www.vultr.com
- **Linode**: https://www.linode.com
- **Hostinger**: https://www.hostinger.com/vps

### Tools

- **PostgreSQL Tools**: https://www.postgresql.org/download/
- **Docker**: https://docs.docker.com/get-docker/
- **Supabase CLI**: https://github.com/supabase/cli

---

## Summary

### Key Takeaways

1. **Coolify + Supabase = powerful self-hosted backend** with minimal complexity
2. **Cost savings: 50-80%** compared to Supabase Cloud for production apps
3. **Full data control** and no vendor lock-in
4. **One-click deployment** in Coolify (5-10 minutes)
5. **Migration from hosted Supabase** is straightforward (backup/restore)
6. **Alternative solutions** exist (CapRover, Dokploy, Dokku) depending on your needs

### Quick Start Checklist

- [ ] Purchase VPS (4GB RAM minimum, recommend 8GB for production)
- [ ] Install Coolify (2-5 minutes with automated script)
- [ ] Deploy Supabase in Coolify (5-10 minutes)
- [ ] Configure custom domains and SSL
- [ ] Migrate data from hosted Supabase (if applicable)
- [ ] Update application configuration
- [ ] Set up automated backups
- [ ] Configure monitoring and alerts
- [ ] Implement security hardening

### When to Self-Host

✅ **Self-host if:**
- Database >10GB or rapidly growing
- >1,000 monthly active users
- Want full control over data
- Looking to reduce costs by 50-80%
- Have basic DevOps knowledge

❌ **Use Supabase Cloud if:**
- Just prototyping/MVP
- Small database (<5GB)
- No DevOps experience
- Need enterprise support/SLA
- Want zero infrastructure management

### Next Steps

1. **Experiment**: Start with a small VPS ($12/mo) and test deployment
2. **Learn**: Familiarize yourself with Coolify and Docker basics
3. **Migrate staging**: Move a non-production environment first
4. **Validate**: Test thoroughly before migrating production
5. **Monitor**: Set up proper monitoring and backups
6. **Optimize**: Fine-tune performance after initial deployment

---

**Ready to take control of your backend?** 🚀

Start with a Hetzner VPS (€3.29/mo), install Coolify, deploy Supabase, and enjoy full ownership of your infrastructure with significant cost savings!

