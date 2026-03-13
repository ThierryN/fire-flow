# Installer Wizard Patterns for Web Applications

## Problem
Creating a web-based installer wizard that allows non-technical users to install a Node.js application on cPanel shared hosting without command-line access.

---

## Solution: WordPress-Style 5-Minute Install Pattern

### Core Principles
1. **Single entry point** - One URL to start installation
2. **Progressive disclosure** - Show only what's needed at each step
3. **Auto-detection** - Check requirements automatically
4. **Fallback options** - Multiple paths to success
5. **Clear feedback** - Show progress and errors clearly

---

## Installer Flow (7 Steps)

### Step 1: Welcome & Requirements Check
```javascript
// server/installer/requirements.js
const checkRequirements = async () => {
  return {
    nodeVersion: process.version,
    nodeOk: semver.gte(process.version, '18.0.0'),
    phpVersion: await getPhpVersion(), // For cPanel Node.js selector
    diskSpace: await getDiskSpace(),
    diskOk: diskSpace > 500 * 1024 * 1024, // 500MB minimum
    writableDir: await checkWritable(process.cwd()),
    dbConnectable: await testDbConnection()
  };
};
```

### Step 2: License Key Validation
```javascript
// License format: XXXX-XXXX-XXXX-XXXX
// Checksum: Modified Luhn algorithm with 32-char alphabet
const LICENSE_CHARS = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';

const validateLicenseKey = (key) => {
  const clean = key.replace(/-/g, '').toUpperCase();
  if (clean.length !== 16) return false;

  // Extract checksum (last char)
  const payload = clean.slice(0, 15);
  const checksum = clean[15];

  // Calculate expected checksum
  let sum = 0;
  for (let i = 0; i < payload.length; i++) {
    let val = LICENSE_CHARS.indexOf(payload[i]);
    if (i % 2 === 0) val *= 2;
    sum += val % 32 + Math.floor(val / 32);
  }
  const expected = LICENSE_CHARS[(32 - (sum % 32)) % 32];

  return checksum === expected;
};
```

### Step 3: Database Configuration
```javascript
// Support both PostgreSQL and MySQL via Knex.js
// server/db/knex.js
const knex = require('knex');

const getKnexConfig = (dbType, connectionString) => {
  const configs = {
    postgresql: {
      client: 'pg',
      connection: connectionString,
      pool: { min: 2, max: 10 }
    },
    mysql: {
      client: 'mysql2',
      connection: connectionString,
      pool: { min: 2, max: 10 }
    }
  };
  return configs[dbType];
};
```

### Step 4: Admin Account Creation
```javascript
// Validate admin credentials before creation
const validateAdminSetup = (data) => {
  const errors = [];

  if (!data.email || !isValidEmail(data.email)) {
    errors.push('Valid email required');
  }
  if (!data.password || data.password.length < 8) {
    errors.push('Password must be 8+ characters');
  }
  if (data.password !== data.confirmPassword) {
    errors.push('Passwords do not match');
  }

  return { valid: errors.length === 0, errors };
};
```

### Step 5: Site Configuration
```javascript
// Basic site settings
const siteConfig = {
  siteName: 'My Learning Platform',
  siteUrl: 'https://learn.example.com',
  adminEmail: 'admin@example.com',
  timezone: 'America/New_York',
  language: 'en'
};
```

### Step 6: Optional Features
```javascript
// Feature flags for optional modules
const optionalFeatures = {
  podcasts: true,
  blog: true,
  certificates: true,
  payments: false, // Requires Stripe setup
  emailNotifications: false // Requires SMTP setup
};
```

### Step 7: Installation & Verification
```javascript
// Run migrations and seed data
const runInstallation = async (config) => {
  // 1. Write .env file
  await writeEnvFile(config);

  // 2. Run database migrations
  await knex.migrate.latest();

  // 3. Create admin user
  await createAdminUser(config.admin);

  // 4. Seed starter content (optional)
  if (config.seedContent) {
    await knex.seed.run();
  }

  // 5. Remove installer (security)
  await disableInstaller();

  return { success: true, loginUrl: '/login' };
};
```

---

## Security Considerations

### Disable After Installation
```javascript
// server/middleware/installerGuard.js
const installerGuard = (req, res, next) => {
  const installed = fs.existsSync('.installed');

  if (installed && req.path.startsWith('/installer')) {
    return res.redirect('/login');
  }

  next();
};
```

### Secure .env Generation
```javascript
// Generate secure random secrets
const crypto = require('crypto');

const generateSecrets = () => ({
  JWT_SECRET: crypto.randomBytes(64).toString('hex'),
  SESSION_SECRET: crypto.randomBytes(32).toString('hex'),
  ENCRYPTION_KEY: crypto.randomBytes(32).toString('hex')
});
```

---

## Database Abstraction with Knex.js

### Migration Example
```javascript
// migrations/001_users.js
exports.up = function(knex) {
  return knex.schema.createTable('users', (table) => {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    table.string('email').unique().notNullable();
    table.string('password').notNullable();
    table.string('name');
    table.enum('role', ['student', 'instructor', 'admin']).defaultTo('student');
    table.timestamps(true, true);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('users');
};
```

### Query Abstraction
```javascript
// Use Knex query builder for database-agnostic queries
const findUserByEmail = async (email) => {
  return knex('users').where({ email }).first();
};

const createUser = async (userData) => {
  const [user] = await knex('users')
    .insert(userData)
    .returning('*');
  return user;
};
```

---

## cPanel Node.js Selector Setup

### Instructions for Non-Technical Users
1. Log into cPanel
2. Find "Setup Node.js App" under Software
3. Click "Create Application"
4. Settings:
   - Node.js version: 18.x or higher
   - Application mode: Production
   - Application root: public_html/lms (or subdirectory)
   - Application URL: your-domain.com/lms
   - Application startup file: server/index.js
5. Click "Create"
6. Click "Run NPM Install"
7. Visit your URL to start installer wizard

---

## References
- Full documentation: `docs/installer/INSTALLER_ARCHITECTURE.md`
- Implementation roadmap: `docs/installer/IMPLEMENTATION_VISION.md`
- Database abstraction: `docs/installer/DATABASE_ABSTRACTION.md`
- Licensing system: `docs/installer/LICENSING_SYSTEM.md`
- WordPress installer analysis: `docs/installer/research/WORDPRESS_INSTALLER_ANALYSIS.md`
