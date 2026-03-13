# Plugin System Architecture - MERN Community LMS

## Overview

This document details the WordPress-style plugin/hook system implemented for the MERN Community LMS application. The system enables extensibility through actions (side effects) and filters (data modification) without modifying core application code.

## Research Sources

- [LearnPress Hooks System](https://learnpresslms.com/docs/learnpress-developer-documentation/hooks-and-filters-actions-filters/)
- [Node.js Plugin Architecture](https://medium.com/codeelevation/node-js-plugin-architecture-build-your-own-plugin-system-with-es-modules-5b9a5df19884)
- [React Pluggable Library](https://react-pluggable.github.io/)
- [SurveyJS Node.js + PostgreSQL Demo](https://github.com/surveyjs/surveyjs-nodejs-postgresql)

---

## Architecture Overview

```
server/
├── plugins/
│   ├── core/
│   │   ├── HookSystem.js         # WordPress-style hooks/filters
│   │   └── PluginManager.js      # Plugin lifecycle management
│   ├── installed/                # Installed plugin packages
│   │   └── <plugin-slug>/
│   │       ├── plugin.json       # Plugin manifest
│   │       └── index.js          # Plugin entry point
│   └── index.js                  # Plugin system entry point
├── models/
│   ├── PluginConfig.pg.js        # Plugin CRUD operations
│   └── PluginEvent.pg.js         # Hook registration & logging
├── controllers/
│   └── pluginController.js       # Admin API handlers
├── routes/
│   └── pluginRoutes.js           # REST endpoints
└── migrations/
    └── 073_create_plugins_system.sql

client/src/
└── pages/admin/
    └── PluginManager.jsx         # Admin UI
```

---

## Database Schema

### Migration: 073_create_plugins_system.sql

```sql
-- 1) plugins table (installed plugin registry)
CREATE TABLE IF NOT EXISTS plugins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL UNIQUE,
  slug VARCHAR(100) NOT NULL UNIQUE,
  version VARCHAR(20) NOT NULL,
  description TEXT,
  author VARCHAR(100),
  author_url TEXT,
  plugin_url TEXT,
  enabled BOOLEAN NOT NULL DEFAULT FALSE,
  config JSONB NOT NULL DEFAULT '{}'::jsonb,
  dependencies JSONB NOT NULL DEFAULT '[]'::jsonb,
  entry_point VARCHAR(255) NOT NULL DEFAULT 'index.js',
  installed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  enabled_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2) plugin_hooks table (hook subscriptions)
CREATE TABLE IF NOT EXISTS plugin_hooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plugin_id UUID NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
  hook_name VARCHAR(100) NOT NULL,
  hook_type VARCHAR(20) NOT NULL DEFAULT 'action', -- 'action' or 'filter'
  priority INTEGER NOT NULL DEFAULT 10,
  callback_path VARCHAR(255) NOT NULL,
  accepted_args INTEGER NOT NULL DEFAULT 1,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(plugin_id, hook_name, callback_path)
);

-- 3) plugin_logs table (execution history)
CREATE TABLE IF NOT EXISTS plugin_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plugin_id UUID REFERENCES plugins(id) ON DELETE SET NULL,
  hook_name VARCHAR(100),
  level VARCHAR(20) NOT NULL DEFAULT 'info',
  message TEXT NOT NULL,
  context JSONB DEFAULT '{}'::jsonb,
  execution_time_ms INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Key Indexes
```sql
CREATE INDEX plugins_enabled_idx ON plugins (enabled) WHERE enabled = TRUE;
CREATE INDEX plugins_slug_idx ON plugins (slug);
CREATE INDEX plugin_hooks_plugin_idx ON plugin_hooks (plugin_id);
CREATE INDEX plugin_hooks_name_idx ON plugin_hooks (hook_name);
CREATE INDEX plugin_hooks_active_idx ON plugin_hooks (is_active, hook_name, priority);
CREATE INDEX plugin_logs_plugin_idx ON plugin_logs (plugin_id);
CREATE INDEX plugin_logs_level_idx ON plugin_logs (level, created_at DESC);
CREATE INDEX plugins_config_gin ON plugins USING gin (config);
```

---

## Core Components

### 1. HookSystem.js - WordPress-style Actions & Filters

**Location:** `server/plugins/core/HookSystem.js`

```javascript
class HookSystem {
  constructor() {
    this.actions = new Map();
    this.filters = new Map();
    this.executionLog = [];
    this.debugMode = process.env.PLUGIN_DEBUG === 'true';
    this.currentHook = null;
  }

  // Add action callback
  addAction(hookName, callback, priority = 10, acceptedArgs = 1, pluginId = null) {
    // Store callback with priority sorting
  }

  // Execute action hook (async)
  async doAction(hookName, ...args) {
    // Execute all registered callbacks
  }

  // Add filter callback
  addFilter(hookName, callback, priority = 10, acceptedArgs = 1, pluginId = null) {
    // Store filter callback
  }

  // Apply filters to a value (async)
  async applyFilters(hookName, value, ...args) {
    // Chain callbacks, each modifying the value
    return filteredValue;
  }

  // Sync versions available: doActionSync, applyFiltersSync
}

// Singleton export
const hooks = new HookSystem();
export { HookSystem };
export default hooks;
```

**Key Features:**
- Priority-based execution (lower = earlier, default 10)
- Async/sync variants for both actions and filters
- Plugin ID tracking for cleanup on disable
- Execution logging for debugging
- `acceptedArgs` controls how many arguments callbacks receive

### 2. PluginManager.js - Lifecycle Management

**Location:** `server/plugins/core/PluginManager.js`

```javascript
class PluginManager {
  constructor(hooksInstance) {
    this.hooks = hooksInstance;
    this.plugins = new Map();    // In-memory plugin registry
    this.pluginsDir = path.join(process.cwd(), 'server/plugins/installed');
  }

  async initialize() {
    // 1. Scan plugins/installed/ directory
    // 2. Load plugin.json manifests
    // 3. Sync with database
    // 4. Activate enabled plugins
  }

  async loadPlugin(pluginDir) {
    // Read plugin.json, validate, return config
  }

  async activatePlugin(pluginId, pluginConfig) {
    // Dynamic import entry point
    // Call plugin's activate() function
    // Register hooks
  }

  async deactivatePlugin(pluginId) {
    // Call plugin's deactivate() function
    // Remove hooks from HookSystem
  }

  async enablePlugin(slug) {
    // Set enabled=true in DB
    // Activate plugin
  }

  async disablePlugin(slug) {
    // Set enabled=false in DB
    // Deactivate plugin
  }
}
```

**Plugin Manifest (plugin.json):**
```json
{
  "name": "My Plugin",
  "slug": "my-plugin",
  "version": "1.0.0",
  "description": "Plugin description",
  "author": "Author Name",
  "authorUrl": "https://example.com",
  "pluginUrl": "https://github.com/example/my-plugin",
  "entryPoint": "index.js",
  "dependencies": ["other-plugin-slug"],
  "config": {
    "defaultSetting": "value"
  }
}
```

### 3. Plugin Entry Point (index.js)

**Location:** `server/plugins/installed/<slug>/index.js`

```javascript
// Plugin must export activate and optionally deactivate
export async function activate(hooks, config, pluginId) {
  // Register hooks
  hooks.addAction('user.registered', async (user) => {
    console.log('New user registered:', user.email);
    // Send welcome email, create audit log, etc.
  }, 10, 1, pluginId);

  hooks.addFilter('course.price', async (price, course) => {
    // Apply discount
    return price * 0.9;
  }, 10, 2, pluginId);
}

export async function deactivate(hooks, pluginId) {
  // Cleanup (hooks are auto-removed by pluginId)
  console.log('Plugin deactivated');
}
```

---

## Available Core Hooks

### Actions (Side Effects)

| Hook Name | Arguments | Description | Location |
|-----------|-----------|-------------|----------|
| `user.registered` | `user` | After user registration | authController.js |
| `user.login` | `user` | After successful login | authController.js |
| `course.enrolled` | `{userId, courseId, course}` | After course enrollment | courseController.js |

### Filters (Data Modification)

| Hook Name | Value | Extra Args | Description |
|-----------|-------|------------|-------------|
| `course.price` | `price` | `course` | Modify course pricing |
| `enrollment.access` | `hasAccess` | `{userId, courseId}` | Modify enrollment access |

---

## API Endpoints

**Base URL:** `/api/plugins`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all plugins |
| GET | `/:slug` | Get single plugin |
| POST | `/` | Register new plugin |
| POST | `/:slug/enable` | Enable plugin |
| POST | `/:slug/disable` | Disable plugin |
| PUT | `/:slug/config` | Update plugin config |
| DELETE | `/:slug` | Uninstall plugin |
| GET | `/hooks` | Get all registered hooks |
| GET | `/logs` | Get plugin execution logs |

All endpoints require admin authentication.

---

## Adding Hooks to Controllers

**Pattern for adding hooks to existing controllers:**

```javascript
// Import at top of controller
import { hooks } from '../plugins/index.js';

// In controller function (after successful operation):
hooks.doAction('hook.name', data).catch(err => {
  console.error('Plugin hook error:', err);
});

// For filters (use returned value):
const modifiedValue = await hooks.applyFilters('filter.name', originalValue, context);
```

**Example from authController.js:**
```javascript
// After user registration
hooks.doAction('user.registered', newUser).catch(err => {
  console.error('Plugin hook user.registered error:', err);
});

// After login
hooks.doAction('user.login', user).catch(err => {
  console.error('Plugin hook user.login error:', err);
});
```

---

## Frontend Admin UI

**Location:** `client/src/pages/admin/PluginManager.jsx`

**Features:**
- **Plugins Tab:** View installed plugins, enable/disable, configure, uninstall
- **Hooks Tab:** View registered actions and filters with callback counts
- **Logs Tab:** View plugin execution logs for debugging
- **Config Modal:** Edit plugin configuration as JSON

**Route:** `/admin/plugins`

---

## Troubleshooting

### Plugin Not Loading
1. Check `server/plugins/installed/<slug>/plugin.json` exists and is valid JSON
2. Verify `entryPoint` file exists
3. Check server logs for import errors
4. Ensure plugin exports `activate` function

### Hooks Not Firing
1. Verify plugin is enabled in database (`enabled = true`)
2. Check Hooks tab in admin UI for registration
3. Enable debug mode: `PLUGIN_DEBUG=true`
4. Check plugin_logs table for errors

### Database Issues
1. Run migration: `073_create_plugins_system.sql`
2. Verify tables exist: `plugins`, `plugin_hooks`, `plugin_logs`
3. Check for FK constraint violations

---

## Testing the Plugin System

1. **Create test plugin:**
   ```bash
   mkdir -p server/plugins/installed/test-plugin
   ```

2. **Add plugin.json:**
   ```json
   {
     "name": "Test Plugin",
     "slug": "test-plugin",
     "version": "1.0.0",
     "description": "A test plugin",
     "author": "Developer",
     "entryPoint": "index.js"
   }
   ```

3. **Add index.js:**
   ```javascript
   export async function activate(hooks, config, pluginId) {
     hooks.addAction('user.login', async (user) => {
       console.log('🔌 Test plugin: User logged in:', user.email);
     }, 10, 1, pluginId);
   }
   ```

4. **Restart server** - plugin auto-discovered

5. **Enable via admin UI** at `/admin/plugins`

6. **Login to trigger hook** - check server logs

---

## Files Reference

| File | Purpose |
|------|---------|
| `server/migrations/073_create_plugins_system.sql` | Database schema |
| `server/plugins/core/HookSystem.js` | Actions/Filters implementation |
| `server/plugins/core/PluginManager.js` | Plugin lifecycle |
| `server/plugins/index.js` | Entry point, initialization |
| `server/models/PluginConfig.pg.js` | Plugin CRUD model |
| `server/models/PluginEvent.pg.js` | Hook/log model |
| `server/controllers/pluginController.js` | API handlers |
| `server/routes/pluginRoutes.js` | REST routes |
| `client/src/pages/admin/PluginManager.jsx` | Admin UI |

---

## Future Enhancements

1. **Frontend Plugin Slots** - React component injection points
2. **Plugin Marketplace** - Install plugins from remote registry
3. **Plugin Dependencies** - Automatic dependency resolution
4. **Plugin Updates** - Version checking and auto-update
5. **Sandboxing** - Isolate plugin execution for security

---

## Related Skills

- [Questionnaire System](../form-solutions/SURVEYJS_QUESTIONNAIRE_SYSTEM.md)
- [Database Patterns](../database-solutions/)
- [API Patterns](../api-patterns/)

---

*Last Updated: January 8, 2026*
*Author: Claude AI Assistant*
*Project: MERN Community LMS*
