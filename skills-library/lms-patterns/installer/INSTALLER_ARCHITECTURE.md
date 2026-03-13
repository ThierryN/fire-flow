# Church LMS Installer - Architecture Specification

**Version:** 1.0
**Last Updated:** January 11, 2026
**Status:** DESIGN PHASE
**Related Documents:**
- [Implementation Roadmap](./IMPLEMENTATION_VISION.md)
- [cPanel Installation Guide](./CPANEL_INSTALLATION_GUIDE.md)

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Installer Package Structure](#2-installer-package-structure)
3. [Installation Flow](#3-installation-flow)
4. [Requirements Checker Module](#4-requirements-checker-module)
5. [Database Configuration Module](#5-database-configuration-module)
6. [Environment Configuration](#6-environment-configuration)
7. [Security Considerations](#7-security-considerations)
8. [Error Handling & Recovery](#8-error-handling--recovery)
9. [Post-Installation](#9-post-installation)
10. [Technical Specifications](#10-technical-specifications)

---

## 1. System Overview

### 1.1 High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                              USER'S BROWSER                                        |
|  +-----------------------------------------------------------------------------+  |
|  |                        Web-Based Installation Wizard                         |  |
|  |  [Welcome] -> [Requirements] -> [Database] -> [Config] -> [Admin] -> [Done] |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
                                        |
                                        | HTTP/HTTPS
                                        v
+-----------------------------------------------------------------------------------+
|                              CPANEL SHARED HOSTING                                 |
|  +-----------------------------------------------------------------------------+  |
|  |                           install.php (Entry Point)                          |  |
|  |                                     |                                        |  |
|  |          +----------------------------------------------------------+        |  |
|  |          |                   PHP Installer Engine                    |        |  |
|  |          |  +----------------+  +------------------+  +----------+  |        |  |
|  |          |  | Requirements   |  | Database         |  | Env      |  |        |  |
|  |          |  | Checker        |  | Connector        |  | Writer   |  |        |  |
|  |          |  +----------------+  +------------------+  +----------+  |        |  |
|  |          |  +----------------+  +------------------+  +----------+  |        |  |
|  |          |  | License        |  | Theme            |  | Content  |  |        |  |
|  |          |  | Validator      |  | Manager          |  | Importer |  |        |  |
|  |          |  +----------------+  +------------------+  +----------+  |        |  |
|  |          +----------------------------------------------------------+        |  |
|  |                                     |                                        |  |
|  |          +----------------------------------------------------------+        |  |
|  |          |                    Application Layer                      |        |  |
|  |          |  +------------------------+  +------------------------+  |        |  |
|  |          |  |    Node.js Backend     |  |   React Frontend       |  |        |  |
|  |          |  |    (server/)           |  |   (client/build/)      |  |        |  |
|  |          |  +------------------------+  +------------------------+  |        |  |
|  |          +----------------------------------------------------------+        |  |
|  |                                     |                                        |  |
|  |          +----------------------------------------------------------+        |  |
|  |          |                     Database Layer                        |        |  |
|  |          |        +------------------+  +------------------+         |        |  |
|  |          |        |   PostgreSQL     |  |     MySQL        |         |        |  |
|  |          |        |   (preferred)    |  |   (fallback)     |         |        |  |
|  |          |        +------------------+  +------------------+         |        |  |
|  |          +----------------------------------------------------------+        |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
                                        |
                                        | License Validation (HTTPS)
                                        v
+-----------------------------------------------------------------------------------+
|                           LICENSE SERVER (External)                                |
|  +-----------------------------------------------------------------------------+  |
|  |  Activation API  |  Validation API  |  Feature Flags  |  Usage Analytics   |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### 1.2 Component Responsibilities

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| **install.php** | Entry point, session management, step routing | PHP 8.1+ |
| **RequirementsChecker** | Validate server environment meets minimum specs | PHP |
| **DatabaseConnector** | Test connections, create schemas, run migrations | PHP + SQL |
| **EnvWriter** | Generate and secure .env configuration file | PHP |
| **LicenseValidator** | Validate license keys against remote server | PHP + cURL |
| **ThemeManager** | Install and configure selected theme | PHP |
| **ContentImporter** | Import starter content packs | PHP + Node.js |
| **Node.js Backend** | Main application server | Node.js 18+ |
| **React Frontend** | Pre-built user interface | React (static build) |

### 1.3 Data Flow During Installation

```
+--------+     +----------+     +----------+     +----------+     +--------+
| Step 1 | --> | Step 2   | --> | Step 3   | --> | Step 4   | --> | Step 5 |
| Welcome|     | Require- |     | Database |     | Site     |     | Admin  |
| License|     | ments    |     | Config   |     | Config   |     | Setup  |
+--------+     +----------+     +----------+     +----------+     +--------+
    |               |               |               |               |
    v               v               v               v               v
+--------+     +----------+     +----------+     +----------+     +--------+
| Validate|    | Check    |     | Test     |     | Write    |     | Create |
| License |    | PHP,     |     | Connection|    | .env     |     | Admin  |
| Key     |    | Node,    |     | Create   |     | File     |     | User   |
|         |    | Disk,    |     | Tables   |     | Set Paths|     | Hash   |
|         |    | Perms    |     |          |     |          |     | Pass   |
+--------+     +----------+     +----------+     +----------+     +--------+
    |               |               |               |               |
    v               v               v               v               v
[Session]      [Session]       [Session]       [.env File]     [Database]
 Store          Store           Store
 License        Results         DB Creds
```

---

## 2. Installer Package Structure

### 2.1 Complete Package Layout

```
lms-installer-v1.0.0.zip
|
+-- install.php                    # Entry point - redirects to installer/
+-- .htaccess                       # Security rules, URL rewriting
+-- README.txt                      # Quick start instructions
|
+-- installer/                      # PHP Installation Wizard
|   +-- bootstrap.php               # Autoloader, session init, helpers
|   +-- config.php                  # Installer configuration constants
|   +-- functions.php               # Utility functions
|   |
|   +-- classes/                    # Core installer classes
|   |   +-- Installer.php           # Main orchestrator class
|   |   +-- RequirementsChecker.php # Server requirements validation
|   |   +-- DatabaseConnector.php   # DB connection and schema management
|   |   +-- EnvWriter.php           # .env file generation
|   |   +-- LicenseValidator.php    # License key validation
|   |   +-- ThemeManager.php        # Theme installation
|   |   +-- ContentImporter.php     # Starter content installation
|   |   +-- NodeManager.php         # Node.js detection and npm runner
|   |   +-- Logger.php              # Installation logging
|   |   +-- SecurityManager.php     # CSRF, sanitization, cleanup
|   |
|   +-- views/                      # Step templates (PHP + HTML)
|   |   +-- layout.php              # Main HTML wrapper
|   |   +-- header.php              # Step progress header
|   |   +-- footer.php              # Navigation buttons
|   |   +-- welcome.php             # Step 1: Welcome + license
|   |   +-- requirements.php        # Step 2: System check
|   |   +-- database.php            # Step 3: Database setup
|   |   +-- site-config.php         # Step 4: Site configuration
|   |   +-- admin-setup.php         # Step 5: Admin account
|   |   +-- theme-select.php        # Step 6: Theme selection
|   |   +-- content-options.php     # Step 7: Starter content
|   |   +-- installing.php          # Step 8: Progress display
|   |   +-- complete.php            # Step 9: Success + login
|   |   +-- error.php               # Error display template
|   |
|   +-- assets/                     # Static files for installer UI
|   |   +-- css/
|   |   |   +-- installer.css       # Installer styles
|   |   |   +-- progress.css        # Progress bar styles
|   |   +-- js/
|   |   |   +-- installer.js        # Form validation, AJAX
|   |   |   +-- progress.js         # Real-time progress updates
|   |   +-- images/
|   |       +-- logo.png            # Installer logo
|   |       +-- icons/              # UI icons
|   |
|   +-- migrations/                 # Database schema files
|   |   +-- postgresql/
|   |   |   +-- 001_initial_schema.sql
|   |   |   +-- 002_seed_data.sql
|   |   +-- mysql/
|   |       +-- 001_initial_schema.sql
|   |       +-- 002_seed_data.sql
|   |
|   +-- templates/                  # Configuration templates
|   |   +-- env.template            # .env file template
|   |   +-- htaccess.template       # .htaccess for production
|   |
|   +-- logs/                       # Installation logs (created at runtime)
|       +-- .gitkeep
|
+-- server/                         # Node.js Backend Application
|   +-- server.js                   # Main entry point
|   +-- package.json                # Dependencies
|   +-- package-lock.json           # Locked versions
|   +-- .env.example                # Environment template
|   +-- config/                     # Configuration files
|   +-- controllers/                # Route handlers
|   +-- middleware/                 # Express middleware
|   +-- models/                     # Database models
|   +-- routes/                     # API routes
|   +-- services/                   # Business logic
|   +-- utils/                      # Utility functions
|
+-- client/                         # Pre-built React Frontend
|   +-- build/                      # Production build (static files)
|   |   +-- index.html
|   |   +-- static/
|   |       +-- css/
|   |       +-- js/
|   |       +-- media/
|   +-- package.json                # For reference only
|
+-- themes/                         # Bundled Theme Packages
|   +-- classic/
|   |   +-- theme.json              # Theme metadata
|   |   +-- preview.png             # Theme preview image
|   |   +-- variables.css           # CSS custom properties
|   |   +-- overrides.css           # Component overrides
|   +-- colorful-modern/
|       +-- theme.json
|       +-- preview.png
|       +-- variables.css
|       +-- overrides.css
|
+-- content/                        # Optional Starter Content
    +-- starter-pack/
    |   +-- manifest.json           # Content package definition
    |   +-- courses/                # Sample courses
    |   +-- media/                  # Sample images/videos
    +-- demo-data/
        +-- manifest.json
        +-- users.json              # Demo user accounts
        +-- posts.json              # Sample community posts
```

### 2.2 File Size Estimates

| Component | Estimated Size | Notes |
|-----------|---------------|-------|
| installer/ | ~500 KB | PHP installer engine |
| server/ | ~2 MB | Node.js backend (without node_modules) |
| client/build/ | ~5 MB | Pre-built React app |
| themes/ | ~1 MB | 2 bundled themes |
| content/ | ~10 MB | Starter content (optional) |
| **Total (minimal)** | **~8 MB** | Without starter content |
| **Total (full)** | **~18 MB** | With starter content |

---

## 3. Installation Flow

### 3.1 Step-by-Step Process

```
+===========================================================================+
|                         INSTALLATION FLOW                                  |
+===========================================================================+

STEP 1: WELCOME & LICENSE
+----------------------------------+
|  [Church LMS Logo]               |
|                                  |
|  Welcome to Church LMS!          |
|                                  |
|  Enter your license key:         |
|  [________________________]      |
|                                  |
|  [ ] I accept the terms of       |
|      service and privacy policy  |
|                                  |
|  [Get a License Key] [Continue]  |
+----------------------------------+
     |
     | Validate license key against server
     | Store license tier in session
     v

STEP 2: REQUIREMENTS CHECK
+----------------------------------+
|  System Requirements             |
|  ================================|
|  [x] PHP 8.1+         (8.2.12)   |
|  [x] Node.js 18+      (20.10.0)  |
|  [x] Disk Space       (2.1 GB)   |
|  [x] Write Permissions (OK)      |
|  [x] PHP Extensions:             |
|      [x] PDO                     |
|      [x] JSON                    |
|      [x] cURL                    |
|      [x] OpenSSL                 |
|  [ ] PostgreSQL       (Not Found)|
|  [x] MySQL 8+         (8.0.35)   |
|                                  |
|  [Back]              [Continue]  |
+----------------------------------+
     |
     | All critical requirements must pass
     | Warnings allowed, errors block
     v

STEP 3: DATABASE CONFIGURATION
+----------------------------------+
|  Database Setup                  |
|  ================================|
|  Database Type:                  |
|  ( ) PostgreSQL (Recommended)    |
|  (x) MySQL                       |
|                                  |
|  Host: [localhost____________]   |
|  Port: [3306_________________]   |
|  Database: [gracefc_lms______]   |
|  Username: [gracefc_lmsuser__]   |
|  Password: [******************]  |
|                                  |
|  [Test Connection]               |
|  Status: Connected Successfully  |
|                                  |
|  [Back]              [Continue]  |
+----------------------------------+
     |
     | Test connection
     | Create tables if empty database
     | Run migrations
     v

STEP 4: SITE CONFIGURATION
+----------------------------------+
|  Site Settings                   |
|  ================================|
|  Organization Name:              |
|  [Grace Fellowship Church____]   |
|                                  |
|  Site URL:                       |
|  [https://lms.gracefc.org___]    |
|                                  |
|  Logo: [Choose File] logo.png    |
|                                  |
|  Primary Color:                  |
|  [#3B82F6] [Color Picker]        |
|                                  |
|  Timezone:                       |
|  [America/New_York__________]    |
|                                  |
|  [Back]              [Continue]  |
+----------------------------------+
     |
     | Save settings to session
     | Upload logo to temp directory
     v

STEP 5: ADMIN ACCOUNT
+----------------------------------+
|  Create Admin Account            |
|  ================================|
|  Full Name:                      |
|  [Pastor John Smith__________]   |
|                                  |
|  Email Address:                  |
|  [pastor@gracefc.org_________]   |
|                                  |
|  Password:                       |
|  [************************]      |
|  Strength: Strong [==========]   |
|                                  |
|  Confirm Password:               |
|  [************************]      |
|                                  |
|  [Back]              [Continue]  |
+----------------------------------+
     |
     | Validate password strength
     | Store hashed password
     v

STEP 6: THEME SELECTION
+----------------------------------+
|  Choose Your Theme               |
|  ================================|
|  +-------------+ +-------------+ |
|  | [Preview]   | | [Preview]   | |
|  | Classic     | | Colorful    | |
|  | Clean and   | | Modern and  | |
|  | professional| | vibrant     | |
|  | (o) Select  | | ( ) Select  | |
|  +-------------+ +-------------+ |
|                                  |
|  [Back]              [Continue]  |
+----------------------------------+
     |
     | Record theme selection
     v

STEP 7: CONTENT OPTIONS
+----------------------------------+
|  Starter Content                 |
|  ================================|
|  [ ] Install Sample Course       |
|      "Getting Started with LMS"  |
|      Includes 5 lessons and quiz |
|                                  |
|  [ ] Install Demo Data           |
|      Sample users and posts      |
|      (For testing purposes)      |
|                                  |
|  [Back]              [Install]   |
+----------------------------------+
     |
     | Begin installation process
     v

STEP 8: INSTALLATION PROGRESS
+----------------------------------+
|  Installing Church LMS...        |
|  ================================|
|  [=============>      ] 65%      |
|                                  |
|  [x] Writing configuration...    |
|  [x] Creating database tables... |
|  [x] Installing Node.js deps...  |
|  [>] Building application...     |
|  [ ] Installing theme...         |
|  [ ] Creating admin account...   |
|  [ ] Importing starter content...|
|  [ ] Finalizing...               |
|                                  |
|  Please wait, do not close       |
|  this window.                    |
+----------------------------------+
     |
     | Real-time progress via AJAX polling
     | Each step updates database/files
     v

STEP 9: INSTALLATION COMPLETE
+----------------------------------+
|  [Success Icon]                  |
|                                  |
|  Installation Complete!          |
|  ================================|
|  Your Church LMS is ready.       |
|                                  |
|  Site URL:                       |
|  https://lms.gracefc.org         |
|                                  |
|  Admin Login:                    |
|  pastor@gracefc.org              |
|                                  |
|  IMPORTANT: Delete the           |
|  installer/ folder for security  |
|                                  |
|  [Delete Installer] [Go to Site] |
+----------------------------------+
```

### 3.2 Installation State Machine

```
                    +----------+
                    |  START   |
                    +----+-----+
                         |
                         v
+----------+       +----------+       +----------+
| LICENSE  | ----> | REQUIRE- | ----> | DATABASE |
| INVALID  |       | MENTS    |       | CONFIG   |
+----------+       | FAIL     |       +----+-----+
     ^             +----------+            |
     |                  ^                  v
     |                  |            +----------+
     +------------------+            | DB TEST  |
                                     | FAIL     |
                                     +----+-----+
                                          |
                    +---------------------+
                    |
                    v
              +----------+       +----------+       +----------+
              | SITE     | ----> | ADMIN    | ----> | THEME    |
              | CONFIG   |       | SETUP    |       | SELECT   |
              +----------+       +----------+       +----+-----+
                                                        |
                                                        v
                                                  +----------+
                                                  | CONTENT  |
                                                  | OPTIONS  |
                                                  +----+-----+
                                                       |
                    +----------------------------------+
                    |
                    v
              +----------+       +----------+       +----------+
              | INSTALL- | ----> | INSTALL  | ----> | COMPLETE |
              | ING      |       | FAIL     |       +----------+
              +----------+       +----+-----+            |
                    |                 |                  v
                    |                 v            +----------+
                    |            +----------+      | CLEANUP  |
                    +----------->| ROLLBACK |      +----------+
                                 +----------+
```

---

## 4. Requirements Checker Module

### 4.1 Check Categories

| Category | Check | Minimum | Recommended | Blocking |
|----------|-------|---------|-------------|----------|
| **PHP** | Version | 8.1 | 8.2+ | Yes |
| **PHP** | memory_limit | 128M | 256M | Yes |
| **PHP** | max_execution_time | 120 | 300 | No |
| **PHP** | upload_max_filesize | 32M | 64M | No |
| **PHP** | post_max_size | 32M | 64M | No |
| **Node.js** | Version | 18.0.0 | 20.x LTS | Yes |
| **npm** | Available | Yes | Yes | Yes |
| **Disk** | Free Space | 500MB | 2GB | Yes |
| **Disk** | Writable directories | Yes | Yes | Yes |
| **Database** | PostgreSQL OR MySQL | 14+ / 8+ | 15+ / 8.0+ | Yes |
| **Extensions** | PDO | Yes | Yes | Yes |
| **Extensions** | pdo_mysql OR pdo_pgsql | Yes | Yes | Yes |
| **Extensions** | json | Yes | Yes | Yes |
| **Extensions** | curl | Yes | Yes | Yes |
| **Extensions** | openssl | Yes | Yes | Yes |
| **Extensions** | mbstring | Yes | Yes | Yes |
| **Extensions** | fileinfo | Yes | Yes | No |
| **Extensions** | gd OR imagick | Yes | Yes | No |

### 4.2 RequirementsChecker Class

```php
<?php
/**
 * RequirementsChecker.php
 * Validates server environment for LMS installation
 */

namespace Installer;

class RequirementsChecker
{
    private array $results = [];
    private array $errors = [];
    private array $warnings = [];

    // Minimum requirements
    private const MIN_PHP_VERSION = '8.1.0';
    private const MIN_NODE_VERSION = '18.0.0';
    private const MIN_DISK_SPACE_MB = 500;
    private const MIN_MEMORY_MB = 128;

    // Required PHP extensions
    private const REQUIRED_EXTENSIONS = [
        'pdo', 'json', 'curl', 'openssl', 'mbstring'
    ];

    // Optional but recommended extensions
    private const OPTIONAL_EXTENSIONS = [
        'fileinfo', 'gd', 'imagick', 'zip'
    ];

    // Directories that must be writable
    private const WRITABLE_PATHS = [
        '../server/.env',
        '../server/uploads',
        '../client/build',
        '../themes',
        './logs'
    ];

    /**
     * Run all requirement checks
     * @return array Results with pass/fail status
     */
    public function checkAll(): array
    {
        $this->checkPhpVersion();
        $this->checkPhpMemory();
        $this->checkPhpExtensions();
        $this->checkNodeJs();
        $this->checkDiskSpace();
        $this->checkWritePermissions();
        $this->checkDatabases();

        return [
            'passed' => empty($this->errors),
            'results' => $this->results,
            'errors' => $this->errors,
            'warnings' => $this->warnings
        ];
    }

    /**
     * Check PHP version meets minimum requirement
     */
    private function checkPhpVersion(): void
    {
        $current = PHP_VERSION;
        $passed = version_compare($current, self::MIN_PHP_VERSION, '>=');

        $this->results['php_version'] = [
            'name' => 'PHP Version',
            'required' => self::MIN_PHP_VERSION . '+',
            'current' => $current,
            'passed' => $passed,
            'blocking' => true
        ];

        if (!$passed) {
            $this->errors[] = "PHP {$current} is installed but {self::MIN_PHP_VERSION}+ is required.";
        }
    }

    /**
     * Check PHP memory limit
     */
    private function checkPhpMemory(): void
    {
        $memoryLimit = ini_get('memory_limit');
        $memoryMB = $this->convertToMB($memoryLimit);
        $passed = $memoryMB >= self::MIN_MEMORY_MB || $memoryMB === -1;

        $this->results['php_memory'] = [
            'name' => 'PHP Memory Limit',
            'required' => self::MIN_MEMORY_MB . 'M',
            'current' => $memoryLimit,
            'passed' => $passed,
            'blocking' => true
        ];

        if (!$passed) {
            $this->errors[] = "PHP memory_limit is {$memoryLimit} but " . self::MIN_MEMORY_MB . "M is required.";
        }
    }

    /**
     * Check required and optional PHP extensions
     */
    private function checkPhpExtensions(): void
    {
        // Required extensions
        foreach (self::REQUIRED_EXTENSIONS as $ext) {
            $loaded = extension_loaded($ext);

            $this->results["ext_{$ext}"] = [
                'name' => "PHP Extension: {$ext}",
                'required' => 'Yes',
                'current' => $loaded ? 'Installed' : 'Missing',
                'passed' => $loaded,
                'blocking' => true
            ];

            if (!$loaded) {
                $this->errors[] = "Required PHP extension '{$ext}' is not installed.";
            }
        }

        // Database extensions (at least one required)
        $hasPdoMysql = extension_loaded('pdo_mysql');
        $hasPdoPgsql = extension_loaded('pdo_pgsql');

        $this->results['ext_database'] = [
            'name' => 'Database Extension (pdo_mysql or pdo_pgsql)',
            'required' => 'At least one',
            'current' => $this->formatDbExtensions($hasPdoMysql, $hasPdoPgsql),
            'passed' => $hasPdoMysql || $hasPdoPgsql,
            'blocking' => true
        ];

        if (!$hasPdoMysql && !$hasPdoPgsql) {
            $this->errors[] = "No database extension found. Install pdo_mysql or pdo_pgsql.";
        }

        // Optional extensions
        foreach (self::OPTIONAL_EXTENSIONS as $ext) {
            $loaded = extension_loaded($ext);

            $this->results["ext_{$ext}_opt"] = [
                'name' => "PHP Extension: {$ext}",
                'required' => 'Recommended',
                'current' => $loaded ? 'Installed' : 'Missing',
                'passed' => $loaded,
                'blocking' => false
            ];

            if (!$loaded) {
                $this->warnings[] = "Optional PHP extension '{$ext}' is not installed.";
            }
        }
    }

    /**
     * Check Node.js availability and version
     */
    private function checkNodeJs(): void
    {
        $nodePath = $this->findNodePath();
        $nodeVersion = null;
        $npmAvailable = false;

        if ($nodePath) {
            $nodeVersion = $this->getNodeVersion($nodePath);
            $npmAvailable = $this->checkNpmAvailable();
        }

        $versionPassed = $nodeVersion &&
            version_compare($nodeVersion, self::MIN_NODE_VERSION, '>=');

        $this->results['nodejs'] = [
            'name' => 'Node.js',
            'required' => self::MIN_NODE_VERSION . '+',
            'current' => $nodeVersion ?: 'Not Found',
            'passed' => $versionPassed,
            'blocking' => true,
            'path' => $nodePath
        ];

        $this->results['npm'] = [
            'name' => 'npm (Node Package Manager)',
            'required' => 'Yes',
            'current' => $npmAvailable ? 'Available' : 'Not Found',
            'passed' => $npmAvailable,
            'blocking' => true
        ];

        if (!$versionPassed) {
            $this->errors[] = $nodeVersion
                ? "Node.js {$nodeVersion} found but " . self::MIN_NODE_VERSION . "+ required."
                : "Node.js not found. Enable via cPanel's 'Setup Node.js App'.";
        }

        if (!$npmAvailable) {
            $this->errors[] = "npm not found. Ensure Node.js is properly installed.";
        }
    }

    /**
     * Find Node.js binary path (cPanel compatibility)
     */
    private function findNodePath(): ?string
    {
        // Common cPanel Node.js paths
        $possiblePaths = [
            '/usr/local/bin/node',
            '/usr/bin/node',
            '/opt/cpanel/ea-nodejs18/bin/node',
            '/opt/cpanel/ea-nodejs20/bin/node',
            '/opt/alt/alt-nodejs18/root/usr/bin/node',
            '/opt/alt/alt-nodejs20/root/usr/bin/node',
            getenv('HOME') . '/nodevenv/*/bin/node'
        ];

        foreach ($possiblePaths as $path) {
            if (strpos($path, '*') !== false) {
                // Handle glob patterns for virtual environments
                $matches = glob($path);
                foreach ($matches as $match) {
                    if (is_executable($match)) {
                        return $match;
                    }
                }
            } elseif (is_executable($path)) {
                return $path;
            }
        }

        // Try which command
        $output = shell_exec('which node 2>/dev/null');
        if ($output) {
            return trim($output);
        }

        return null;
    }

    /**
     * Get Node.js version from binary
     */
    private function getNodeVersion(string $nodePath): ?string
    {
        $output = shell_exec("{$nodePath} --version 2>/dev/null");
        if ($output) {
            // Remove 'v' prefix (e.g., v20.10.0 -> 20.10.0)
            return ltrim(trim($output), 'v');
        }
        return null;
    }

    /**
     * Check if npm is available
     */
    private function checkNpmAvailable(): bool
    {
        $output = shell_exec('which npm 2>/dev/null || where npm 2>nul');
        return !empty(trim($output ?? ''));
    }

    /**
     * Check available disk space
     */
    private function checkDiskSpace(): void
    {
        $path = dirname(__DIR__);
        $freeBytes = disk_free_space($path);
        $freeMB = $freeBytes ? round($freeBytes / 1024 / 1024) : 0;
        $passed = $freeMB >= self::MIN_DISK_SPACE_MB;

        $this->results['disk_space'] = [
            'name' => 'Available Disk Space',
            'required' => self::MIN_DISK_SPACE_MB . ' MB',
            'current' => $freeMB . ' MB',
            'passed' => $passed,
            'blocking' => true
        ];

        if (!$passed) {
            $this->errors[] = "Only {$freeMB}MB disk space available. " .
                self::MIN_DISK_SPACE_MB . "MB required.";
        }
    }

    /**
     * Check write permissions for required directories
     */
    private function checkWritePermissions(): void
    {
        $allWritable = true;
        $issues = [];

        foreach (self::WRITABLE_PATHS as $relativePath) {
            $absolutePath = realpath(dirname(__DIR__) . '/' . $relativePath)
                ?: dirname(__DIR__) . '/' . $relativePath;

            $parentDir = dirname($absolutePath);
            $writable = is_writable($parentDir) || is_writable($absolutePath);

            if (!$writable) {
                $allWritable = false;
                $issues[] = $relativePath;
            }
        }

        $this->results['write_permissions'] = [
            'name' => 'Write Permissions',
            'required' => 'Writable directories',
            'current' => $allWritable ? 'OK' : 'Issues: ' . implode(', ', $issues),
            'passed' => $allWritable,
            'blocking' => true
        ];

        if (!$allWritable) {
            $this->errors[] = "Cannot write to: " . implode(', ', $issues) .
                ". Check file permissions (755 for directories, 644 for files).";
        }
    }

    /**
     * Check for available database servers
     */
    private function checkDatabases(): void
    {
        $postgresAvailable = extension_loaded('pdo_pgsql');
        $mysqlAvailable = extension_loaded('pdo_mysql');

        $this->results['database_postgresql'] = [
            'name' => 'PostgreSQL Support',
            'required' => 'Recommended',
            'current' => $postgresAvailable ? 'Available' : 'Not Available',
            'passed' => $postgresAvailable,
            'blocking' => false
        ];

        $this->results['database_mysql'] = [
            'name' => 'MySQL Support',
            'required' => 'Alternative',
            'current' => $mysqlAvailable ? 'Available' : 'Not Available',
            'passed' => $mysqlAvailable,
            'blocking' => false
        ];

        if (!$postgresAvailable && $mysqlAvailable) {
            $this->warnings[] = "PostgreSQL recommended but MySQL will be used.";
        }
    }

    /**
     * Convert PHP memory notation to MB
     */
    private function convertToMB(string $value): int
    {
        $value = trim($value);
        $last = strtolower($value[strlen($value) - 1]);
        $num = (int) $value;

        switch ($last) {
            case 'g': $num *= 1024; break;
            case 'm': break;
            case 'k': $num /= 1024; break;
        }

        return $num;
    }

    /**
     * Format database extension status
     */
    private function formatDbExtensions(bool $mysql, bool $pgsql): string
    {
        $parts = [];
        if ($mysql) $parts[] = 'MySQL';
        if ($pgsql) $parts[] = 'PostgreSQL';
        return empty($parts) ? 'None' : implode(', ', $parts);
    }

    /**
     * Get list of blocking errors
     */
    public function getErrors(): array
    {
        return $this->errors;
    }

    /**
     * Get list of non-blocking warnings
     */
    public function getWarnings(): array
    {
        return $this->warnings;
    }

    /**
     * Check if installation can proceed
     */
    public function canProceed(): bool
    {
        return empty($this->errors);
    }
}
```

---

## 5. Database Configuration Module

### 5.1 Supported Databases

| Database | Versions | Priority | cPanel Availability |
|----------|----------|----------|---------------------|
| PostgreSQL | 14, 15, 16 | Primary (Preferred) | ~40% of hosts |
| MySQL | 8.0+ | Secondary (Fallback) | ~95% of hosts |
| MariaDB | 10.6+ | Secondary (MySQL-compatible) | ~60% of hosts |

### 5.2 Auto-Detection Logic

```
+------------------+
| Start Detection  |
+--------+---------+
         |
         v
+------------------+     Yes    +------------------+
| PostgreSQL ext   +----------->| Check PG Server  |
| installed?       |            | on localhost     |
+--------+---------+            +--------+---------+
         | No                            |
         v                               v
+------------------+            +------------------+
| MySQL ext        |     Yes    | PostgreSQL       |
| installed?       +-----+----->| Available        |
+--------+---------+     |      +------------------+
         | No            |               |
         v               |               v
+------------------+     |      +------------------+
| No database      |     +----->| MySQL Available  |
| support - ERROR  |            +------------------+
+------------------+
```

### 5.3 DatabaseConnector Class

```php
<?php
/**
 * DatabaseConnector.php
 * Handles database connection testing, creation, and schema installation
 */

namespace Installer;

use PDO;
use PDOException;

class DatabaseConnector
{
    private ?PDO $connection = null;
    private string $type;
    private array $config;
    private array $errors = [];

    // Supported database types
    public const TYPE_POSTGRESQL = 'postgresql';
    public const TYPE_MYSQL = 'mysql';

    /**
     * Available database configurations detected
     */
    public static function detectAvailable(): array
    {
        $available = [];

        if (extension_loaded('pdo_pgsql')) {
            $available[] = [
                'type' => self::TYPE_POSTGRESQL,
                'name' => 'PostgreSQL',
                'recommended' => true,
                'default_port' => 5432
            ];
        }

        if (extension_loaded('pdo_mysql')) {
            $available[] = [
                'type' => self::TYPE_MYSQL,
                'name' => 'MySQL / MariaDB',
                'recommended' => !extension_loaded('pdo_pgsql'),
                'default_port' => 3306
            ];
        }

        return $available;
    }

    /**
     * Constructor
     */
    public function __construct(string $type, array $config)
    {
        $this->type = $type;
        $this->config = array_merge([
            'host' => 'localhost',
            'port' => $type === self::TYPE_POSTGRESQL ? 5432 : 3306,
            'database' => '',
            'username' => '',
            'password' => ''
        ], $config);
    }

    /**
     * Test database connection
     * @return array Result with success status and message
     */
    public function testConnection(): array
    {
        try {
            $dsn = $this->buildDsn(false); // Without database name first
            $pdo = new PDO($dsn, $this->config['username'], $this->config['password'], [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_TIMEOUT => 5
            ]);

            // Try to connect to specific database
            $dsn = $this->buildDsn(true);
            $this->connection = new PDO($dsn, $this->config['username'], $this->config['password'], [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
            ]);

            // Get server version
            $version = $this->getServerVersion();

            return [
                'success' => true,
                'message' => "Connected successfully to {$this->config['database']}",
                'version' => $version,
                'database_exists' => true
            ];

        } catch (PDOException $e) {
            // Check if it's a "database doesn't exist" error
            if ($this->isDatabaseNotFoundError($e)) {
                return [
                    'success' => false,
                    'message' => "Database '{$this->config['database']}' does not exist.",
                    'database_exists' => false,
                    'can_create' => $this->canCreateDatabase()
                ];
            }

            return [
                'success' => false,
                'message' => $this->formatConnectionError($e),
                'database_exists' => null
            ];
        }
    }

    /**
     * Build PDO DSN string
     */
    private function buildDsn(bool $includeDatabase = true): string
    {
        $host = $this->config['host'];
        $port = $this->config['port'];
        $db = $this->config['database'];

        if ($this->type === self::TYPE_POSTGRESQL) {
            $dsn = "pgsql:host={$host};port={$port}";
            if ($includeDatabase && $db) {
                $dsn .= ";dbname={$db}";
            }
        } else {
            $dsn = "mysql:host={$host};port={$port};charset=utf8mb4";
            if ($includeDatabase && $db) {
                $dsn .= ";dbname={$db}";
            }
        }

        return $dsn;
    }

    /**
     * Check if error indicates database doesn't exist
     */
    private function isDatabaseNotFoundError(PDOException $e): bool
    {
        $code = $e->getCode();
        $message = strtolower($e->getMessage());

        // PostgreSQL: database "X" does not exist
        if (strpos($message, 'does not exist') !== false) {
            return true;
        }

        // MySQL: Unknown database 'X'
        if ($code === 1049 || strpos($message, 'unknown database') !== false) {
            return true;
        }

        return false;
    }

    /**
     * Format connection error for user display
     */
    private function formatConnectionError(PDOException $e): string
    {
        $message = $e->getMessage();

        // Common error translations
        $translations = [
            'Connection refused' => 'Database server is not running or not accepting connections.',
            'Access denied' => 'Invalid username or password.',
            'Unknown host' => 'Database host not found. Check the hostname.',
            'Connection timed out' => 'Database server did not respond. Check firewall settings.',
            'authentication failed' => 'Invalid username or password.',
        ];

        foreach ($translations as $pattern => $friendly) {
            if (stripos($message, $pattern) !== false) {
                return $friendly;
            }
        }

        return "Connection failed: {$message}";
    }

    /**
     * Get database server version
     */
    private function getServerVersion(): string
    {
        if (!$this->connection) {
            return 'Unknown';
        }

        try {
            if ($this->type === self::TYPE_POSTGRESQL) {
                $stmt = $this->connection->query('SELECT version()');
                $result = $stmt->fetchColumn();
                // Extract version number from "PostgreSQL 15.4 on ..."
                if (preg_match('/PostgreSQL (\d+\.\d+(\.\d+)?)/', $result, $matches)) {
                    return $matches[1];
                }
            } else {
                $stmt = $this->connection->query('SELECT VERSION()');
                $result = $stmt->fetchColumn();
                // Extract version from "8.0.35-MySQL Community Server"
                if (preg_match('/^(\d+\.\d+\.\d+)/', $result, $matches)) {
                    return $matches[1];
                }
            }
            return $result;
        } catch (PDOException $e) {
            return 'Unknown';
        }
    }

    /**
     * Check if user has permissions to create databases
     */
    private function canCreateDatabase(): bool
    {
        try {
            $dsn = $this->buildDsn(false);
            $pdo = new PDO($dsn, $this->config['username'], $this->config['password']);

            if ($this->type === self::TYPE_POSTGRESQL) {
                // Check for CREATEDB privilege
                $stmt = $pdo->query("SELECT rolcreatedb FROM pg_roles WHERE rolname = current_user");
                return (bool) $stmt->fetchColumn();
            } else {
                // Check MySQL grants
                $stmt = $pdo->query("SHOW GRANTS FOR CURRENT_USER()");
                $grants = $stmt->fetchAll(PDO::FETCH_COLUMN);
                foreach ($grants as $grant) {
                    if (stripos($grant, 'ALL PRIVILEGES') !== false ||
                        stripos($grant, 'CREATE') !== false) {
                        return true;
                    }
                }
            }
        } catch (PDOException $e) {
            // Assume no permission if we can't check
        }

        return false;
    }

    /**
     * Create database if it doesn't exist
     */
    public function createDatabase(): array
    {
        try {
            $dsn = $this->buildDsn(false);
            $pdo = new PDO($dsn, $this->config['username'], $this->config['password'], [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
            ]);

            $dbName = $this->config['database'];

            if ($this->type === self::TYPE_POSTGRESQL) {
                // PostgreSQL: Check if exists first
                $stmt = $pdo->prepare("SELECT 1 FROM pg_database WHERE datname = ?");
                $stmt->execute([$dbName]);

                if (!$stmt->fetchColumn()) {
                    $pdo->exec("CREATE DATABASE \"{$dbName}\" ENCODING 'UTF8'");
                }
            } else {
                // MySQL: CREATE DATABASE IF NOT EXISTS
                $pdo->exec("CREATE DATABASE IF NOT EXISTS `{$dbName}`
                           CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
            }

            return [
                'success' => true,
                'message' => "Database '{$dbName}' created successfully."
            ];

        } catch (PDOException $e) {
            return [
                'success' => false,
                'message' => "Failed to create database: " . $e->getMessage()
            ];
        }
    }

    /**
     * Install database schema from migration files
     */
    public function installSchema(): array
    {
        if (!$this->connection) {
            $testResult = $this->testConnection();
            if (!$testResult['success']) {
                return $testResult;
            }
        }

        try {
            $migrationPath = __DIR__ . "/../migrations/{$this->type}/";

            if (!is_dir($migrationPath)) {
                throw new \Exception("Migration files not found for {$this->type}");
            }

            // Get migration files in order
            $files = glob($migrationPath . '*.sql');
            sort($files);

            $this->connection->beginTransaction();

            foreach ($files as $file) {
                $sql = file_get_contents($file);

                // Split into individual statements
                $statements = $this->splitSqlStatements($sql);

                foreach ($statements as $statement) {
                    $statement = trim($statement);
                    if (!empty($statement)) {
                        $this->connection->exec($statement);
                    }
                }
            }

            $this->connection->commit();

            return [
                'success' => true,
                'message' => 'Database schema installed successfully.',
                'tables_created' => $this->getTableCount()
            ];

        } catch (\Exception $e) {
            if ($this->connection->inTransaction()) {
                $this->connection->rollBack();
            }

            return [
                'success' => false,
                'message' => "Schema installation failed: " . $e->getMessage()
            ];
        }
    }

    /**
     * Split SQL file into individual statements
     */
    private function splitSqlStatements(string $sql): array
    {
        // Remove comments
        $sql = preg_replace('/--.*$/m', '', $sql);
        $sql = preg_replace('/\/\*.*?\*\//s', '', $sql);

        // Split on semicolons (but not inside strings)
        $statements = [];
        $current = '';
        $inString = false;
        $stringChar = '';

        for ($i = 0; $i < strlen($sql); $i++) {
            $char = $sql[$i];

            if ($inString) {
                $current .= $char;
                if ($char === $stringChar && ($i === 0 || $sql[$i-1] !== '\\')) {
                    $inString = false;
                }
            } else {
                if ($char === "'" || $char === '"') {
                    $inString = true;
                    $stringChar = $char;
                    $current .= $char;
                } elseif ($char === ';') {
                    $statements[] = $current;
                    $current = '';
                } else {
                    $current .= $char;
                }
            }
        }

        if (trim($current)) {
            $statements[] = $current;
        }

        return $statements;
    }

    /**
     * Get count of tables in database
     */
    private function getTableCount(): int
    {
        try {
            if ($this->type === self::TYPE_POSTGRESQL) {
                $stmt = $this->connection->query(
                    "SELECT COUNT(*) FROM information_schema.tables
                     WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
                );
            } else {
                $stmt = $this->connection->query(
                    "SELECT COUNT(*) FROM information_schema.tables
                     WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE'"
                );
            }
            return (int) $stmt->fetchColumn();
        } catch (PDOException $e) {
            return 0;
        }
    }

    /**
     * Generate connection string for .env file
     */
    public function getConnectionString(): string
    {
        $host = $this->config['host'];
        $port = $this->config['port'];
        $db = $this->config['database'];
        $user = $this->config['username'];
        $pass = urlencode($this->config['password']);

        if ($this->type === self::TYPE_POSTGRESQL) {
            return "postgresql://{$user}:{$pass}@{$host}:{$port}/{$db}";
        } else {
            return "mysql://{$user}:{$pass}@{$host}:{$port}/{$db}";
        }
    }

    /**
     * Get PDO connection instance
     */
    public function getConnection(): ?PDO
    {
        return $this->connection;
    }
}
```

---

## 6. Environment Configuration

### 6.1 Environment Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `NODE_ENV` | Runtime environment | `production` | Yes |
| `PORT` | Server port | `5000` | Yes |
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@localhost/db` | Yes |
| `JWT_SECRET` | Token signing secret | `random-64-char-string` | Yes |
| `JWT_EXPIRE` | Token expiration | `7d` | No |
| `SITE_URL` | Public site URL | `https://lms.church.org` | Yes |
| `SITE_NAME` | Organization name | `Grace Fellowship Church` | Yes |
| `ADMIN_EMAIL` | Admin contact email | `admin@church.org` | Yes |
| `SMTP_HOST` | Email server host | `smtp.gmail.com` | No |
| `SMTP_PORT` | Email server port | `587` | No |
| `SMTP_USER` | Email username | `noreply@church.org` | No |
| `SMTP_PASS` | Email password | `app-password` | No |
| `UPLOAD_PATH` | File upload directory | `./uploads` | No |
| `MAX_UPLOAD_SIZE` | Max file size (bytes) | `52428800` | No |
| `LICENSE_KEY` | Product license | `XXXX-XXXX-XXXX-XXXX` | Yes |

### 6.2 EnvWriter Class

```php
<?php
/**
 * EnvWriter.php
 * Generates and secures .env configuration file
 */

namespace Installer;

class EnvWriter
{
    private string $templatePath;
    private string $outputPath;
    private array $values = [];

    /**
     * Constructor
     */
    public function __construct(string $outputPath = null)
    {
        $this->templatePath = __DIR__ . '/../templates/env.template';
        $this->outputPath = $outputPath ?? dirname(__DIR__, 2) . '/server/.env';
    }

    /**
     * Set configuration values
     */
    public function setValues(array $values): self
    {
        $this->values = array_merge($this->values, $values);
        return $this;
    }

    /**
     * Generate secure random string for secrets
     */
    public static function generateSecret(int $length = 64): string
    {
        $bytes = random_bytes($length / 2);
        return bin2hex($bytes);
    }

    /**
     * Generate JWT secret
     */
    public static function generateJwtSecret(): string
    {
        return self::generateSecret(64);
    }

    /**
     * Detect site URL from current request
     */
    public static function detectSiteUrl(): string
    {
        $protocol = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off')
            ? 'https' : 'http';
        $host = $_SERVER['HTTP_HOST'] ?? 'localhost';

        // Remove installer path from URL
        $path = dirname($_SERVER['SCRIPT_NAME']);
        $path = preg_replace('#/installer.*$#', '', $path);

        return rtrim("{$protocol}://{$host}{$path}", '/');
    }

    /**
     * Detect Node.js path for cPanel environments
     */
    public static function detectNodePath(): string
    {
        $paths = [
            '/usr/local/bin/node',
            '/usr/bin/node',
            '/opt/cpanel/ea-nodejs20/bin/node',
            '/opt/cpanel/ea-nodejs18/bin/node',
        ];

        // Check cPanel virtual environment
        $home = getenv('HOME');
        if ($home) {
            $venvPaths = glob("{$home}/nodevenv/*/bin/node");
            $paths = array_merge($venvPaths, $paths);
        }

        foreach ($paths as $path) {
            if (is_executable($path)) {
                return $path;
            }
        }

        // Fallback to PATH
        $which = trim(shell_exec('which node 2>/dev/null') ?? '');
        return $which ?: '/usr/bin/node';
    }

    /**
     * Write .env file
     */
    public function write(): array
    {
        try {
            // Ensure required values have defaults
            $defaults = [
                'NODE_ENV' => 'production',
                'PORT' => '5000',
                'JWT_SECRET' => self::generateJwtSecret(),
                'JWT_EXPIRE' => '7d',
                'SITE_URL' => self::detectSiteUrl(),
                'UPLOAD_PATH' => './uploads',
                'MAX_UPLOAD_SIZE' => '52428800',
                'SESSION_SECRET' => self::generateSecret(32),
                'COOKIE_SECRET' => self::generateSecret(32),
            ];

            $this->values = array_merge($defaults, $this->values);

            // Build .env content
            $content = $this->buildEnvContent();

            // Backup existing .env if present
            if (file_exists($this->outputPath)) {
                $backupPath = $this->outputPath . '.backup.' . date('Y-m-d-His');
                copy($this->outputPath, $backupPath);
            }

            // Write new .env file
            $result = file_put_contents($this->outputPath, $content);

            if ($result === false) {
                throw new \Exception("Failed to write to {$this->outputPath}");
            }

            // Secure file permissions (readable only by owner)
            chmod($this->outputPath, 0600);

            return [
                'success' => true,
                'message' => 'Configuration file created successfully.',
                'path' => $this->outputPath
            ];

        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => $e->getMessage()
            ];
        }
    }

    /**
     * Build .env file content
     */
    private function buildEnvContent(): string
    {
        $sections = [
            'Application' => ['NODE_ENV', 'PORT', 'SITE_URL', 'SITE_NAME'],
            'Database' => ['DATABASE_URL', 'DATABASE_TYPE'],
            'Security' => ['JWT_SECRET', 'JWT_EXPIRE', 'SESSION_SECRET', 'COOKIE_SECRET'],
            'Email (SMTP)' => ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASS', 'SMTP_FROM'],
            'File Uploads' => ['UPLOAD_PATH', 'MAX_UPLOAD_SIZE'],
            'License' => ['LICENSE_KEY'],
            'Optional Services' => ['STRIPE_KEY', 'PAYPAL_CLIENT_ID', 'AWS_ACCESS_KEY']
        ];

        $lines = [
            "# Church LMS Configuration",
            "# Generated by installer on " . date('Y-m-d H:i:s'),
            "# WARNING: Keep this file secure and never commit to version control",
            ""
        ];

        foreach ($sections as $sectionName => $keys) {
            $sectionHasValues = false;
            $sectionLines = ["# {$sectionName}"];

            foreach ($keys as $key) {
                if (isset($this->values[$key]) && $this->values[$key] !== '') {
                    $value = $this->escapeEnvValue($this->values[$key]);
                    $sectionLines[] = "{$key}={$value}";
                    $sectionHasValues = true;
                }
            }

            if ($sectionHasValues) {
                $lines = array_merge($lines, $sectionLines, ['']);
            }
        }

        return implode("\n", $lines);
    }

    /**
     * Escape value for .env file
     */
    private function escapeEnvValue(string $value): string
    {
        // Quote if contains spaces, special chars, or starts with quote
        if (preg_match('/[\s#"\'\\\\]/', $value) || $value === '') {
            // Escape existing quotes and backslashes
            $value = str_replace(['\\', '"'], ['\\\\', '\\"'], $value);
            return '"' . $value . '"';
        }

        return $value;
    }

    /**
     * Validate .env file exists and is readable
     */
    public function validate(): array
    {
        if (!file_exists($this->outputPath)) {
            return [
                'valid' => false,
                'message' => 'Configuration file does not exist.'
            ];
        }

        if (!is_readable($this->outputPath)) {
            return [
                'valid' => false,
                'message' => 'Configuration file is not readable.'
            ];
        }

        // Parse and check required keys
        $content = file_get_contents($this->outputPath);
        $required = ['DATABASE_URL', 'JWT_SECRET', 'SITE_URL'];
        $missing = [];

        foreach ($required as $key) {
            if (!preg_match("/^{$key}=/m", $content)) {
                $missing[] = $key;
            }
        }

        if (!empty($missing)) {
            return [
                'valid' => false,
                'message' => 'Missing required configuration: ' . implode(', ', $missing)
            ];
        }

        return [
            'valid' => true,
            'message' => 'Configuration file is valid.'
        ];
    }
}
```

### 6.3 Environment Template

```
# env.template
# Church LMS Configuration Template

# Application
NODE_ENV={{NODE_ENV}}
PORT={{PORT}}
SITE_URL={{SITE_URL}}
SITE_NAME={{SITE_NAME}}

# Database
DATABASE_URL={{DATABASE_URL}}
DATABASE_TYPE={{DATABASE_TYPE}}

# Security (Auto-generated during install)
JWT_SECRET={{JWT_SECRET}}
JWT_EXPIRE={{JWT_EXPIRE}}
SESSION_SECRET={{SESSION_SECRET}}
COOKIE_SECRET={{COOKIE_SECRET}}

# Email Configuration
SMTP_HOST={{SMTP_HOST}}
SMTP_PORT={{SMTP_PORT}}
SMTP_USER={{SMTP_USER}}
SMTP_PASS={{SMTP_PASS}}
SMTP_FROM={{SMTP_FROM}}

# File Uploads
UPLOAD_PATH={{UPLOAD_PATH}}
MAX_UPLOAD_SIZE={{MAX_UPLOAD_SIZE}}

# License
LICENSE_KEY={{LICENSE_KEY}}
```

---

## 7. Security Considerations

### 7.1 Security Checklist

| Category | Measure | Implementation |
|----------|---------|----------------|
| **CSRF Protection** | Token per session | Random token in hidden form field |
| **Input Sanitization** | All user inputs | htmlspecialchars, prepared statements |
| **Password Security** | Strong hashing | bcrypt with cost 12 |
| **File Permissions** | Restrictive | .env: 600, dirs: 755, files: 644 |
| **Directory Listing** | Disabled | .htaccess DirectoryIndex |
| **Installer Cleanup** | Post-install | Delete installer/ directory |
| **Error Display** | Production mode | Log errors, don't display |
| **HTTPS** | Enforced | Redirect HTTP to HTTPS |
| **SQL Injection** | Prevented | PDO prepared statements only |
| **Path Traversal** | Blocked | Validate all file paths |

### 7.2 SecurityManager Class

```php
<?php
/**
 * SecurityManager.php
 * Handles security measures for the installer
 */

namespace Installer;

class SecurityManager
{
    private const CSRF_TOKEN_NAME = 'installer_csrf_token';
    private const CSRF_TOKEN_LENGTH = 32;

    /**
     * Initialize security measures
     */
    public static function init(): void
    {
        // Start session if not started
        if (session_status() === PHP_SESSION_NONE) {
            session_start([
                'cookie_httponly' => true,
                'cookie_secure' => self::isHttps(),
                'cookie_samesite' => 'Strict',
                'use_strict_mode' => true
            ]);
        }

        // Generate CSRF token if not exists
        if (!isset($_SESSION[self::CSRF_TOKEN_NAME])) {
            $_SESSION[self::CSRF_TOKEN_NAME] = bin2hex(random_bytes(self::CSRF_TOKEN_LENGTH));
        }

        // Set security headers
        self::setSecurityHeaders();
    }

    /**
     * Set HTTP security headers
     */
    private static function setSecurityHeaders(): void
    {
        header('X-Content-Type-Options: nosniff');
        header('X-Frame-Options: DENY');
        header('X-XSS-Protection: 1; mode=block');
        header('Referrer-Policy: strict-origin-when-cross-origin');

        if (self::isHttps()) {
            header('Strict-Transport-Security: max-age=31536000; includeSubDomains');
        }
    }

    /**
     * Check if request is HTTPS
     */
    public static function isHttps(): bool
    {
        return (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off')
            || ($_SERVER['SERVER_PORT'] ?? 80) == 443
            || (!empty($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https');
    }

    /**
     * Get CSRF token for forms
     */
    public static function getCsrfToken(): string
    {
        return $_SESSION[self::CSRF_TOKEN_NAME] ?? '';
    }

    /**
     * Generate hidden CSRF input field
     */
    public static function csrfField(): string
    {
        $token = self::getCsrfToken();
        return '<input type="hidden" name="csrf_token" value="' . htmlspecialchars($token) . '">';
    }

    /**
     * Validate CSRF token from request
     */
    public static function validateCsrf(): bool
    {
        $submitted = $_POST['csrf_token'] ?? $_GET['csrf_token'] ?? '';
        $stored = $_SESSION[self::CSRF_TOKEN_NAME] ?? '';

        if (empty($submitted) || empty($stored)) {
            return false;
        }

        return hash_equals($stored, $submitted);
    }

    /**
     * Sanitize string input
     */
    public static function sanitize(string $input): string
    {
        return htmlspecialchars(trim($input), ENT_QUOTES, 'UTF-8');
    }

    /**
     * Sanitize email input
     */
    public static function sanitizeEmail(string $email): string
    {
        $email = filter_var(trim($email), FILTER_SANITIZE_EMAIL);
        return filter_var($email, FILTER_VALIDATE_EMAIL) ? $email : '';
    }

    /**
     * Sanitize URL input
     */
    public static function sanitizeUrl(string $url): string
    {
        $url = filter_var(trim($url), FILTER_SANITIZE_URL);
        return filter_var($url, FILTER_VALIDATE_URL) ? $url : '';
    }

    /**
     * Validate password strength
     */
    public static function validatePassword(string $password): array
    {
        $errors = [];

        if (strlen($password) < 8) {
            $errors[] = 'Password must be at least 8 characters.';
        }

        if (!preg_match('/[A-Z]/', $password)) {
            $errors[] = 'Password must contain at least one uppercase letter.';
        }

        if (!preg_match('/[a-z]/', $password)) {
            $errors[] = 'Password must contain at least one lowercase letter.';
        }

        if (!preg_match('/[0-9]/', $password)) {
            $errors[] = 'Password must contain at least one number.';
        }

        return [
            'valid' => empty($errors),
            'errors' => $errors,
            'strength' => self::calculatePasswordStrength($password)
        ];
    }

    /**
     * Calculate password strength score (0-100)
     */
    private static function calculatePasswordStrength(string $password): int
    {
        $score = 0;

        // Length scoring
        $score += min(30, strlen($password) * 3);

        // Character variety
        if (preg_match('/[a-z]/', $password)) $score += 10;
        if (preg_match('/[A-Z]/', $password)) $score += 10;
        if (preg_match('/[0-9]/', $password)) $score += 10;
        if (preg_match('/[^a-zA-Z0-9]/', $password)) $score += 20;

        // Penalty for common patterns
        if (preg_match('/^[a-zA-Z]+$/', $password)) $score -= 10;
        if (preg_match('/^[0-9]+$/', $password)) $score -= 20;

        return max(0, min(100, $score));
    }

    /**
     * Hash password using bcrypt
     */
    public static function hashPassword(string $password): string
    {
        return password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);
    }

    /**
     * Clean up installer files after installation
     */
    public static function cleanupInstaller(): array
    {
        $installerPath = dirname(__DIR__);
        $results = [];

        // Files/directories to remove
        $toRemove = [
            $installerPath,
            dirname($installerPath) . '/install.php'
        ];

        foreach ($toRemove as $path) {
            if (is_dir($path)) {
                $result = self::deleteDirectory($path);
            } elseif (is_file($path)) {
                $result = @unlink($path);
            } else {
                $result = true; // Already gone
            }

            $results[$path] = $result;
        }

        return $results;
    }

    /**
     * Recursively delete directory
     */
    private static function deleteDirectory(string $dir): bool
    {
        if (!is_dir($dir)) {
            return true;
        }

        $files = array_diff(scandir($dir), ['.', '..']);

        foreach ($files as $file) {
            $path = $dir . DIRECTORY_SEPARATOR . $file;

            if (is_dir($path)) {
                self::deleteDirectory($path);
            } else {
                @unlink($path);
            }
        }

        return @rmdir($dir);
    }

    /**
     * Validate file path is within allowed directory
     */
    public static function validatePath(string $path, string $baseDir): bool
    {
        $realPath = realpath($path);
        $realBase = realpath($baseDir);

        if ($realPath === false || $realBase === false) {
            return false;
        }

        return strpos($realPath, $realBase) === 0;
    }
}
```

---

## 8. Error Handling & Recovery

### 8.1 Error Categories

| Category | Severity | User Action | System Action |
|----------|----------|-------------|---------------|
| **Blocking** | Critical | Cannot proceed | Stop installation |
| **Recoverable** | High | Retry step | Rollback partial changes |
| **Warning** | Medium | Can proceed | Log and continue |
| **Info** | Low | Informational | Display and continue |

### 8.2 Error Messages (User-Friendly)

| Error Code | Technical Cause | User Message |
|------------|-----------------|--------------|
| `DB_CONN_REFUSED` | Connection refused | "Cannot reach database server. Please verify it's running." |
| `DB_AUTH_FAILED` | Invalid credentials | "Database username or password is incorrect." |
| `DB_NOT_FOUND` | Database doesn't exist | "Database not found. Would you like to create it?" |
| `PHP_VERSION` | PHP < 8.1 | "Your server has PHP X.X but 8.1 or newer is required." |
| `NODE_NOT_FOUND` | Node.js missing | "Node.js not found. Enable it in cPanel's Node.js Selector." |
| `PERM_DENIED` | Write permission | "Cannot write files. Check folder permissions are set to 755." |
| `DISK_FULL` | Insufficient space | "Not enough disk space. Need at least 500MB free." |
| `LICENSE_INVALID` | Bad license key | "License key not recognized. Please check and try again." |
| `LICENSE_EXPIRED` | Expired license | "Your license has expired. Please renew at [URL]." |
| `NETWORK_ERROR` | Connection timeout | "Cannot reach license server. Check internet connection." |

### 8.3 Rollback Capabilities

```php
<?php
/**
 * InstallationRecovery.php
 * Handles installation rollback and recovery
 */

namespace Installer;

class InstallationRecovery
{
    private string $checkpointFile;
    private array $checkpoints = [];

    public function __construct()
    {
        $this->checkpointFile = __DIR__ . '/../logs/install_checkpoint.json';
        $this->loadCheckpoints();
    }

    /**
     * Save checkpoint before critical operation
     */
    public function saveCheckpoint(string $step, array $data): void
    {
        $this->checkpoints[$step] = [
            'timestamp' => time(),
            'data' => $data,
            'completed' => false
        ];

        $this->persistCheckpoints();
    }

    /**
     * Mark checkpoint as completed
     */
    public function completeCheckpoint(string $step): void
    {
        if (isset($this->checkpoints[$step])) {
            $this->checkpoints[$step]['completed'] = true;
            $this->persistCheckpoints();
        }
    }

    /**
     * Get last incomplete checkpoint for resume
     */
    public function getResumePoint(): ?array
    {
        foreach ($this->checkpoints as $step => $checkpoint) {
            if (!$checkpoint['completed']) {
                return [
                    'step' => $step,
                    'data' => $checkpoint['data'],
                    'timestamp' => $checkpoint['timestamp']
                ];
            }
        }
        return null;
    }

    /**
     * Rollback to specific checkpoint
     */
    public function rollbackTo(string $step): array
    {
        $results = [];

        // Find steps after the target
        $found = false;
        foreach (array_keys($this->checkpoints) as $checkpointStep) {
            if ($checkpointStep === $step) {
                $found = true;
                continue;
            }

            if ($found) {
                $result = $this->undoStep($checkpointStep);
                $results[$checkpointStep] = $result;
                unset($this->checkpoints[$checkpointStep]);
            }
        }

        $this->persistCheckpoints();

        return $results;
    }

    /**
     * Undo specific installation step
     */
    private function undoStep(string $step): array
    {
        switch ($step) {
            case 'database_schema':
                return $this->undoDatabaseSchema();

            case 'env_file':
                return $this->undoEnvFile();

            case 'admin_user':
                return $this->undoAdminUser();

            case 'theme_install':
                return $this->undoThemeInstall();

            default:
                return ['success' => true, 'message' => 'Nothing to undo'];
        }
    }

    /**
     * Drop all created tables
     */
    private function undoDatabaseSchema(): array
    {
        try {
            $dbConfig = $_SESSION['db_config'] ?? null;
            if (!$dbConfig) {
                return ['success' => false, 'message' => 'No database config found'];
            }

            $connector = new DatabaseConnector($dbConfig['type'], $dbConfig);
            $testResult = $connector->testConnection();

            if (!$testResult['success']) {
                return $testResult;
            }

            $pdo = $connector->getConnection();

            // Drop all tables (dangerous - only during install)
            if ($dbConfig['type'] === DatabaseConnector::TYPE_POSTGRESQL) {
                $pdo->exec("DROP SCHEMA public CASCADE; CREATE SCHEMA public;");
            } else {
                $pdo->exec("SET FOREIGN_KEY_CHECKS = 0");
                $tables = $pdo->query("SHOW TABLES")->fetchAll(\PDO::FETCH_COLUMN);
                foreach ($tables as $table) {
                    $pdo->exec("DROP TABLE IF EXISTS `{$table}`");
                }
                $pdo->exec("SET FOREIGN_KEY_CHECKS = 1");
            }

            return ['success' => true, 'message' => 'Database schema rolled back'];

        } catch (\Exception $e) {
            return ['success' => false, 'message' => $e->getMessage()];
        }
    }

    /**
     * Remove .env file
     */
    private function undoEnvFile(): array
    {
        $envPath = dirname(__DIR__, 2) . '/server/.env';
        $backupPath = $envPath . '.backup.' . date('Y-m-d');

        // Restore backup if exists
        $backups = glob($envPath . '.backup.*');
        if (!empty($backups)) {
            rsort($backups); // Most recent first
            if (copy($backups[0], $envPath)) {
                return ['success' => true, 'message' => 'Restored previous .env'];
            }
        }

        // Otherwise just remove
        if (file_exists($envPath) && unlink($envPath)) {
            return ['success' => true, 'message' => '.env file removed'];
        }

        return ['success' => false, 'message' => 'Could not remove .env'];
    }

    /**
     * Remove admin user from database
     */
    private function undoAdminUser(): array
    {
        try {
            $dbConfig = $_SESSION['db_config'] ?? null;
            $adminEmail = $_SESSION['admin_email'] ?? null;

            if (!$dbConfig || !$adminEmail) {
                return ['success' => true, 'message' => 'No admin to remove'];
            }

            $connector = new DatabaseConnector($dbConfig['type'], $dbConfig);
            $pdo = $connector->getConnection();

            $stmt = $pdo->prepare("DELETE FROM users WHERE email = ?");
            $stmt->execute([$adminEmail]);

            return ['success' => true, 'message' => 'Admin user removed'];

        } catch (\Exception $e) {
            return ['success' => false, 'message' => $e->getMessage()];
        }
    }

    /**
     * Remove installed theme
     */
    private function undoThemeInstall(): array
    {
        // Theme installation is non-destructive, nothing to undo
        return ['success' => true, 'message' => 'Theme changes are non-destructive'];
    }

    /**
     * Load checkpoints from file
     */
    private function loadCheckpoints(): void
    {
        if (file_exists($this->checkpointFile)) {
            $content = file_get_contents($this->checkpointFile);
            $this->checkpoints = json_decode($content, true) ?? [];
        }
    }

    /**
     * Save checkpoints to file
     */
    private function persistCheckpoints(): void
    {
        $dir = dirname($this->checkpointFile);
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }

        file_put_contents(
            $this->checkpointFile,
            json_encode($this->checkpoints, JSON_PRETTY_PRINT)
        );
    }

    /**
     * Clear all checkpoints (after successful install)
     */
    public function clearCheckpoints(): void
    {
        $this->checkpoints = [];
        if (file_exists($this->checkpointFile)) {
            unlink($this->checkpointFile);
        }
    }
}
```

### 8.4 Installation Log

```php
<?php
/**
 * Logger.php
 * Installation logging for debugging and support
 */

namespace Installer;

class Logger
{
    private static ?string $logFile = null;

    public const LEVEL_DEBUG = 'DEBUG';
    public const LEVEL_INFO = 'INFO';
    public const LEVEL_WARNING = 'WARNING';
    public const LEVEL_ERROR = 'ERROR';

    /**
     * Initialize logger
     */
    public static function init(): void
    {
        $logDir = __DIR__ . '/../logs';

        if (!is_dir($logDir)) {
            mkdir($logDir, 0755, true);
        }

        self::$logFile = $logDir . '/install_' . date('Y-m-d_His') . '.log';

        // Write header
        self::write(self::LEVEL_INFO, 'Installation started', [
            'php_version' => PHP_VERSION,
            'server_software' => $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown',
            'timestamp' => date('c')
        ]);
    }

    /**
     * Write log entry
     */
    public static function write(string $level, string $message, array $context = []): void
    {
        if (!self::$logFile) {
            self::init();
        }

        $entry = [
            'timestamp' => date('Y-m-d H:i:s'),
            'level' => $level,
            'message' => $message,
        ];

        if (!empty($context)) {
            // Sanitize sensitive data
            $context = self::sanitizeContext($context);
            $entry['context'] = $context;
        }

        $line = json_encode($entry) . "\n";
        file_put_contents(self::$logFile, $line, FILE_APPEND);
    }

    /**
     * Log debug message
     */
    public static function debug(string $message, array $context = []): void
    {
        self::write(self::LEVEL_DEBUG, $message, $context);
    }

    /**
     * Log info message
     */
    public static function info(string $message, array $context = []): void
    {
        self::write(self::LEVEL_INFO, $message, $context);
    }

    /**
     * Log warning message
     */
    public static function warning(string $message, array $context = []): void
    {
        self::write(self::LEVEL_WARNING, $message, $context);
    }

    /**
     * Log error message
     */
    public static function error(string $message, array $context = []): void
    {
        self::write(self::LEVEL_ERROR, $message, $context);
    }

    /**
     * Remove sensitive data from context
     */
    private static function sanitizeContext(array $context): array
    {
        $sensitive = ['password', 'secret', 'key', 'token', 'credential'];

        array_walk_recursive($context, function (&$value, $key) use ($sensitive) {
            foreach ($sensitive as $term) {
                if (stripos($key, $term) !== false) {
                    $value = '[REDACTED]';
                    break;
                }
            }
        });

        return $context;
    }

    /**
     * Get log file path
     */
    public static function getLogPath(): ?string
    {
        return self::$logFile;
    }

    /**
     * Generate support information package
     */
    public static function generateSupportInfo(): array
    {
        return [
            'php_version' => PHP_VERSION,
            'php_extensions' => get_loaded_extensions(),
            'server_software' => $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown',
            'document_root' => $_SERVER['DOCUMENT_ROOT'] ?? 'Unknown',
            'memory_limit' => ini_get('memory_limit'),
            'max_execution_time' => ini_get('max_execution_time'),
            'upload_max_filesize' => ini_get('upload_max_filesize'),
            'disk_free_space' => disk_free_space(dirname(__DIR__)),
            'installer_version' => '1.0.0',
            'log_file' => self::$logFile
        ];
    }
}
```

---

## 9. Post-Installation

### 9.1 Post-Install Tasks

| Task | Priority | Automated | Description |
|------|----------|-----------|-------------|
| Redirect to admin | Required | Yes | Send user to login page |
| Delete installer | Required | Prompted | Remove installer/ directory |
| Send welcome email | Optional | Yes | Email admin with getting started info |
| Analytics ping | Optional | Opt-in | Report successful installation |
| Create .htaccess | Required | Yes | Security rules for production |
| Set file permissions | Required | Yes | Secure sensitive files |
| Clear temp files | Required | Yes | Remove uploaded logos, etc. |

### 9.2 Welcome Email Template

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Welcome to Church LMS</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #3B82F6;">Welcome to Church LMS!</h1>

        <p>Hello {{ADMIN_NAME}},</p>

        <p>Your Church LMS has been successfully installed at:</p>

        <p style="font-size: 18px; font-weight: bold;">
            <a href="{{SITE_URL}}">{{SITE_URL}}</a>
        </p>

        <h2>Getting Started</h2>
        <ol>
            <li><strong>Log in</strong> using your admin credentials</li>
            <li><strong>Complete your profile</strong> in Settings</li>
            <li><strong>Create your first course</strong> from the Admin Dashboard</li>
            <li><strong>Invite your members</strong> to join</li>
        </ol>

        <h2>Important Security Reminder</h2>
        <p style="background: #FEF3C7; padding: 15px; border-radius: 5px;">
            Please ensure you have <strong>deleted the installer/ folder</strong>
            from your server. Leaving it in place is a security risk.
        </p>

        <h2>Need Help?</h2>
        <ul>
            <li><a href="{{DOCS_URL}}">Documentation</a></li>
            <li><a href="{{SUPPORT_URL}}">Support Center</a></li>
            <li>Email: support@churchlms.com</li>
        </ul>

        <p>God bless your ministry!</p>

        <p>The Church LMS Team</p>
    </div>
</body>
</html>
```

### 9.3 Production .htaccess

```apache
# Church LMS Production .htaccess
# Generated by installer

# Prevent directory listing
Options -Indexes

# Protect sensitive files
<FilesMatch "^\.env|\.git|composer\.(json|lock)|package(-lock)?\.json">
    Order allow,deny
    Deny from all
</FilesMatch>

# Protect directories
RedirectMatch 403 ^/\.
RedirectMatch 403 ^/node_modules/
RedirectMatch 403 ^/server/(config|models|middleware|services)/

# Force HTTPS
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Remove www (or add www - choose one)
RewriteCond %{HTTP_HOST} ^www\.(.*)$ [NC]
RewriteRule ^(.*)$ https://%1/$1 [R=301,L]

# Node.js reverse proxy (cPanel Passenger)
PassengerAppRoot /home/username/public_html/lms
PassengerAppType node
PassengerStartupFile server/server.js

# Security headers
<IfModule mod_headers.c>
    Header set X-Content-Type-Options "nosniff"
    Header set X-Frame-Options "SAMEORIGIN"
    Header set X-XSS-Protection "1; mode=block"
    Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>

# Compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/css text/javascript application/javascript application/json
</IfModule>

# Cache static assets
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>
```

---

## 10. Technical Specifications

### 10.1 Minimum Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **PHP Version** | 8.1 | 8.2+ | Required for modern syntax |
| **Node.js Version** | 18.x LTS | 20.x LTS | For ES modules support |
| **npm Version** | 9.x | 10.x | Comes with Node.js |
| **PostgreSQL** | 14 | 15+ | Preferred database |
| **MySQL** | 8.0 | 8.0+ | Alternative database |
| **MariaDB** | 10.6 | 10.11+ | MySQL-compatible |
| **Disk Space** | 500 MB | 2 GB | With content packs |
| **RAM (PHP)** | 128 MB | 256 MB | memory_limit setting |
| **RAM (Node)** | 256 MB | 512 MB | For npm install |

### 10.2 Required PHP Extensions

| Extension | Purpose | Check Command |
|-----------|---------|---------------|
| `pdo` | Database abstraction | `php -m | grep pdo` |
| `pdo_mysql` | MySQL connectivity | `php -m | grep pdo_mysql` |
| `pdo_pgsql` | PostgreSQL connectivity | `php -m | grep pdo_pgsql` |
| `json` | JSON encoding/decoding | `php -m | grep json` |
| `curl` | HTTP requests | `php -m | grep curl` |
| `openssl` | Encryption/SSL | `php -m | grep openssl` |
| `mbstring` | Multibyte strings | `php -m | grep mbstring` |
| `fileinfo` | File type detection | `php -m | grep fileinfo` |
| `gd` OR `imagick` | Image processing | `php -m | grep -E "gd|imagick"` |
| `zip` | Archive handling | `php -m | grep zip` |

### 10.3 cPanel Node.js Paths

```
Standard cPanel Node.js Locations:
==================================

CloudLinux (most shared hosts):
  /opt/alt/alt-nodejs18/root/usr/bin/node
  /opt/alt/alt-nodejs20/root/usr/bin/node

EasyApache 4:
  /opt/cpanel/ea-nodejs18/bin/node
  /opt/cpanel/ea-nodejs20/bin/node

Virtual Environment (per-app):
  ~/nodevenv/{app-name}/18/bin/node
  ~/nodevenv/{app-name}/20/bin/node

System-wide:
  /usr/local/bin/node
  /usr/bin/node

Detection Priority:
1. Virtual environment (most reliable for cPanel apps)
2. CloudLinux/EasyApache paths
3. System paths
4. `which node` fallback
```

### 10.4 Database Schema Summary

| Table Category | Count | Examples |
|----------------|-------|----------|
| **User Management** | 5 | users, profiles, roles, permissions, sessions |
| **Course Content** | 8 | courses, lessons, modules, assessments, questions |
| **Progress Tracking** | 4 | enrollments, progress, completions, certificates |
| **Community** | 6 | posts, comments, reactions, categories, tags |
| **E-commerce** | 5 | products, orders, payments, subscriptions, coupons |
| **Media** | 3 | files, folders, media_library |
| **Communication** | 4 | notifications, messages, newsletters, email_logs |
| **System** | 8 | settings, themes, licenses, activity_log, migrations |
| **Total** | ~43 | Full schema in migrations/ |

### 10.5 API Endpoints Used by Installer

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/install/requirements` | GET | Check server requirements |
| `/api/install/database/test` | POST | Test database connection |
| `/api/install/database/create` | POST | Create database schema |
| `/api/install/admin` | POST | Create admin user |
| `/api/install/complete` | POST | Finalize installation |
| `https://license.churchlms.com/validate` | POST | Validate license key |
| `https://license.churchlms.com/activate` | POST | Activate license |

---

## Appendix A: File Checksums

The installer package includes a `checksums.json` file for integrity verification:

```json
{
  "version": "1.0.0",
  "algorithm": "sha256",
  "files": {
    "install.php": "abc123...",
    "installer/bootstrap.php": "def456...",
    "server/server.js": "ghi789...",
    "client/build/index.html": "jkl012..."
  }
}
```

---

## Appendix B: Troubleshooting Reference

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Blank white page | PHP error display off | Check `error_log` in cPanel |
| 500 Internal Server Error | .htaccess issue | Check syntax, disable mod_security |
| Database connection timeout | Wrong host | Use `localhost`, not domain name |
| Node.js not found | Not enabled in cPanel | Use "Setup Node.js App" |
| Permission denied | Wrong file permissions | Set directories to 755, files to 644 |
| License validation failed | Firewall blocking | Allow outbound HTTPS to license server |
| npm install hangs | Low memory | Increase Node.js memory or use `--max-old-space-size` |
| Assets not loading | Wrong SITE_URL | Check .env SITE_URL matches domain |

---

## Document History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-11 | 1.0 | Initial architecture specification | AI Assistant |

---

*This document defines the technical architecture for the Church LMS Installer. It should be updated as implementation progresses and requirements evolve.*
