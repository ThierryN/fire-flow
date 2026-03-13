# PHP Installer Wizard for Node.js Applications

## Overview
A WordPress-style PHP installer wizard that allows non-technical users to deploy Node.js applications on shared cPanel hosting. The installer handles database configuration, admin account creation, .env file generation, and initial setup.

## Architecture

### Directory Structure
```
install/
├── index.php              # Main entry with AJAX handlers
├── includes/
│   ├── requirements.php   # System requirements checker
│   └── functions.php      # Helper functions (DB test, .env gen)
├── steps/
│   ├── step1.php          # Welcome screen
│   ├── step2.php          # Requirements check
│   ├── step3.php          # License key (optional)
│   ├── step4.php          # Database configuration
│   ├── step5.php          # Admin account creation
│   ├── step6.php          # Run installation
│   └── step7.php          # Completion screen
└── assets/
    ├── installer.css      # Responsive styles
    └── installer.js       # AJAX validation
```

### Key Features
1. **Requirements Checking** - PHP version, Node.js, extensions, disk space
2. **Database Support** - MySQL and PostgreSQL with toggle selection
3. **Connection Testing** - Real-time database connection validation
4. **Admin Account** - Secure password with strength indicator
5. **Progress Tracking** - Visual progress bar during installation
6. **Error Handling** - Clear error messages for troubleshooting

## Implementation

### Main Entry Point (index.php)
```php
<?php
session_start();
error_reporting(0);
ini_set('display_errors', '0');

// AJAX request handler
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action'])) {
    header('Content-Type: application/json');

    switch ($_POST['action']) {
        case 'test_database':
            // Test database connection
            $result = testDatabaseConnection($_POST);
            echo json_encode($result);
            exit;

        case 'save_step':
            // Save step data to session
            $_SESSION['install_config'][$_POST['step']] = $_POST['data'];
            echo json_encode(['success' => true]);
            exit;

        case 'run_install':
            // Execute installation
            $result = runInstallation($_SESSION['install_config']);
            echo json_encode($result);
            exit;
    }
}

// Step routing
$step = isset($_GET['step']) ? (int)$_GET['step'] : 1;
$step = max(1, min(7, $step));
?>
```

### Requirements Checker
```php
function checkRequirements() {
    $requirements = [];

    // PHP Version
    $requirements['php_version'] = [
        'name' => 'PHP Version',
        'required' => '7.4+',
        'current' => phpversion(),
        'passed' => version_compare(phpversion(), '7.4.0', '>=')
    ];

    // Node.js Check
    $nodeVersion = shell_exec('node --version 2>&1');
    $requirements['nodejs'] = [
        'name' => 'Node.js',
        'required' => '18.0+',
        'current' => $nodeVersion ? trim($nodeVersion) : 'Not found',
        'passed' => $nodeVersion && version_compare(trim($nodeVersion, 'v'), '18.0.0', '>=')
    ];

    // PHP Extensions
    $extensions = ['pdo', 'pdo_mysql', 'json', 'mbstring'];
    foreach ($extensions as $ext) {
        $requirements["ext_$ext"] = [
            'name' => "PHP Extension: $ext",
            'required' => 'Installed',
            'current' => extension_loaded($ext) ? 'Installed' : 'Missing',
            'passed' => extension_loaded($ext)
        ];
    }

    // Disk Space
    $freeSpace = disk_free_space('.');
    $requirements['disk_space'] = [
        'name' => 'Disk Space',
        'required' => '100MB',
        'current' => formatBytes($freeSpace),
        'passed' => $freeSpace >= 100 * 1024 * 1024
    ];

    return $requirements;
}
```

### Database Connection Test
```php
function testDatabaseConnection($config) {
    try {
        $dbType = $config['db_type'] ?? 'mysql';
        $host = $config['db_host'] ?? 'localhost';
        $port = $config['db_port'] ?? ($dbType === 'mysql' ? 3306 : 5432);
        $name = $config['db_name'];
        $user = $config['db_user'];
        $pass = $config['db_pass'];

        if ($dbType === 'mysql') {
            $dsn = "mysql:host=$host;port=$port;dbname=$name;charset=utf8mb4";
        } else {
            $dsn = "pgsql:host=$host;port=$port;dbname=$name";
        }

        $pdo = new PDO($dsn, $user, $pass, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_TIMEOUT => 5
        ]);

        return ['success' => true, 'message' => 'Connection successful!'];
    } catch (PDOException $e) {
        return ['success' => false, 'message' => $e->getMessage()];
    }
}
```

### .env File Generator
```php
function generateEnvFile($config) {
    $dbType = $config['database']['db_type'] ?? 'mysql';
    $port = $config['database']['db_port'] ?? ($dbType === 'mysql' ? 3306 : 5432);

    $envContent = "# Database Configuration\n";
    $envContent .= "DB_TYPE=" . $dbType . "\n";
    $envContent .= "DB_HOST=" . ($config['database']['db_host'] ?? 'localhost') . "\n";
    $envContent .= "DB_PORT=" . $port . "\n";
    $envContent .= "DB_NAME=" . ($config['database']['db_name'] ?? '') . "\n";
    $envContent .= "DB_USER=" . ($config['database']['db_user'] ?? '') . "\n";
    $envContent .= "DB_PASS=" . ($config['database']['db_pass'] ?? '') . "\n\n";

    $envContent .= "# Application Settings\n";
    $envContent .= "SITE_NAME=\"" . ($config['database']['site_name'] ?? 'My LMS') . "\"\n";
    $envContent .= "NODE_ENV=production\n";
    $envContent .= "PORT=5000\n\n";

    $envContent .= "# Security\n";
    $envContent .= "JWT_SECRET=" . bin2hex(random_bytes(32)) . "\n";
    $envContent .= "SESSION_SECRET=" . bin2hex(random_bytes(32)) . "\n";

    return $envContent;
}
```

## CSS Styling (Mobile-First)
```css
:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.installer-container {
    min-height: 100vh;
    background: var(--background);
    padding: 2rem 1rem;
}

.installer-card {
    max-width: 600px;
    margin: 0 auto;
    background: white;
    border-radius: 1rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    padding: 2rem;
}

.step-indicator {
    display: flex;
    justify-content: space-between;
    margin-bottom: 2rem;
}

.step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}

.step-item.active .step-icon {
    background: var(--primary);
    color: white;
}

.step-item.completed .step-icon {
    background: var(--success);
    color: white;
}
```

## JavaScript (AJAX Handling)
```javascript
// Database connection test
async function testDatabaseConnection() {
    const form = document.getElementById('db-form');
    const formData = new FormData(form);
    formData.append('action', 'test_database');

    const statusEl = document.getElementById('connection-status');
    statusEl.innerHTML = '<div class="alert alert-info">Testing connection...</div>';

    try {
        const response = await fetch('', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (result.success) {
            statusEl.innerHTML = `<div class="alert alert-success">
                ✅ ${result.message}
            </div>`;
        } else {
            statusEl.innerHTML = `<div class="alert alert-danger">
                ❌ ${result.message}
            </div>`;
        }
    } catch (error) {
        statusEl.innerHTML = `<div class="alert alert-danger">
            ❌ Connection test failed: ${error.message}
        </div>`;
    }
}

// Run installation with progress
async function runInstallation() {
    const progressFill = document.querySelector('.progress-fill');
    const logEl = document.getElementById('install-log');

    const steps = [
        { action: 'create_env', label: 'Creating configuration...' },
        { action: 'install_deps', label: 'Installing dependencies...' },
        { action: 'run_migrations', label: 'Setting up database...' },
        { action: 'create_admin', label: 'Creating admin account...' },
        { action: 'finalize', label: 'Finalizing installation...' }
    ];

    for (let i = 0; i < steps.length; i++) {
        const step = steps[i];
        const progress = ((i + 1) / steps.length) * 100;

        logEl.innerHTML += `<div class="log-item">${step.label}</div>`;
        progressFill.style.width = `${progress}%`;

        // Execute step via AJAX
        await executeInstallStep(step.action);
    }

    // Redirect to completion
    window.location.href = '?step=7';
}
```

## Best Practices

### Security
1. **Session-based storage** - Never store passwords in files
2. **CSRF protection** - Add tokens to forms
3. **Input validation** - Sanitize all user inputs
4. **Error suppression** - Hide PHP errors in production
5. **Delete after install** - Remind users to remove /install folder

### User Experience
1. **Progress feedback** - Show clear progress indicators
2. **Error messages** - Provide actionable error descriptions
3. **Mobile responsive** - Works on tablets and phones
4. **Back navigation** - Allow users to go back and change settings

### Compatibility
1. **Multiple DB support** - MySQL, PostgreSQL
2. **PHP 7.4+** - Broad hosting compatibility
3. **No composer** - Self-contained PHP files
4. **AJAX fallback** - Works without JavaScript (basic mode)

## Related Resources
- `docs/installer/IMPLEMENTATION_VISION.md` - Full implementation plan
- `docs/installer/DATABASE_ABSTRACTION.md` - Knex.js layer
- `server/database/README.md` - Node.js database abstraction
