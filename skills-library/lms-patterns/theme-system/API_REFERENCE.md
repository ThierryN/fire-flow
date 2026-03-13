# Theme System API Reference

## REST API Endpoints

### Themes

#### List All Themes
```http
GET /api/themes
```

**Response:**
```json
{
  "success": true,
  "themes": [
    {
      "id": "507f1f77bcf86cd799439011",
      "slug": "modern-education",
      "name": "Modern Education",
      "version": "1.0.0",
      "description": "A clean, modern theme for educational institutions",
      "author": {
        "name": "Theme Developer",
        "email": "dev@example.com",
        "url": "https://example.com"
      },
      "status": "active",
      "screenshot": "/themes/modern-education/screenshot.png",
      "tags": ["education", "modern", "clean"],
      "rating": 4.8,
      "downloadCount": 1523,
      "installedAt": "2025-01-15T10:30:00Z",
      "activatedAt": "2025-01-15T11:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 10
}
```

#### Get Theme Details
```http
GET /api/themes/:id
```

**Response:**
```json
{
  "success": true,
  "theme": {
    "id": "507f1f77bcf86cd799439011",
    "slug": "modern-education",
    "name": "Modern Education",
    "version": "1.0.0",
    "manifest": {
      "name": "Modern Education",
      "slug": "modern-education",
      "version": "1.0.0",
      "compatibility": {
        "lmsVersion": ">=1.0.0",
        "react": ">=18.0.0"
      },
      "settings": {
        "colors": {
          "primary": {
            "type": "color",
            "default": "#4F46E5",
            "label": "Primary Color"
          }
        }
      }
    },
    "settings": {
      "colors": {
        "primary": "#4F46E5",
        "secondary": "#10B981"
      }
    }
  }
}
```

#### Upload New Theme
```http
POST /api/themes
Content-Type: multipart/form-data
```

**Request:**
```
theme: <file.zip>
```

**Response:**
```json
{
  "success": true,
  "theme": {
    "id": "507f1f77bcf86cd799439012",
    "slug": "new-theme",
    "name": "New Theme",
    "status": "inactive"
  },
  "message": "Theme uploaded successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Theme validation failed",
  "errors": [
    {
      "field": "theme.json",
      "message": "Missing required field: name"
    }
  ]
}
```

#### Activate Theme
```http
POST /api/themes/:id/activate
```

**Response:**
```json
{
  "success": true,
  "theme": {
    "id": "507f1f77bcf86cd799439011",
    "slug": "modern-education",
    "status": "active",
    "activatedAt": "2025-11-25T14:30:00Z"
  },
  "previousTheme": {
    "id": "507f1f77bcf86cd799439010",
    "slug": "default-theme",
    "status": "inactive"
  }
}
```

#### Delete Theme
```http
DELETE /api/themes/:id
```

**Response:**
```json
{
  "success": true,
  "message": "Theme deleted successfully"
}
```

**Error (Cannot Delete Active Theme):**
```json
{
  "success": false,
  "message": "Cannot delete active theme. Activate another theme first."
}
```

### Theme Settings

#### Get Active Theme Settings
```http
GET /api/themes/active/settings
```

**Response:**
```json
{
  "success": true,
  "theme": {
    "id": "507f1f77bcf86cd799439011",
    "slug": "modern-education",
    "name": "Modern Education"
  },
  "settings": {
    "colors": {
      "primary": "#4F46E5",
      "secondary": "#10B981",
      "accent": "#F59E0B"
    },
    "typography": {
      "fontFamily": "inter",
      "fontSize": 16
    },
    "layout": {
      "containerWidth": "1280px",
      "headerStyle": "sticky"
    },
    "branding": {
      "logo": "/uploads/logo.png",
      "favicon": "/uploads/favicon.png"
    }
  }
}
```

#### Update Theme Settings
```http
PUT /api/themes/active/settings
Content-Type: application/json
```

**Request:**
```json
{
  "settings": {
    "colors": {
      "primary": "#6366F1"
    },
    "typography": {
      "fontSize": 18
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "settings": {
    "colors": {
      "primary": "#6366F1",
      "secondary": "#10B981",
      "accent": "#F59E0B"
    },
    "typography": {
      "fontFamily": "inter",
      "fontSize": 18
    }
  }
}
```

#### Export Settings
```http
GET /api/themes/settings/export
```

**Response:**
```json
{
  "theme": "modern-education",
  "version": "1.0.0",
  "exportedAt": "2025-11-25T14:30:00Z",
  "settings": {
    "colors": {
      "primary": "#4F46E5",
      "secondary": "#10B981"
    },
    "typography": {
      "fontFamily": "inter",
      "fontSize": 16
    }
  }
}
```

#### Import Settings
```http
POST /api/themes/settings/import
Content-Type: application/json
```

**Request:**
```json
{
  "theme": "modern-education",
  "version": "1.0.0",
  "settings": {
    "colors": {
      "primary": "#4F46E5"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "settings": {
    "colors": {
      "primary": "#4F46E5",
      "secondary": "#10B981"
    }
  }
}
```

#### Reset Settings to Defaults
```http
POST /api/themes/settings/reset
```

**Response:**
```json
{
  "success": true,
  "settings": {
    "colors": {
      "primary": "#4F46E5",
      "secondary": "#10B981"
    }
  },
  "message": "Settings reset to theme defaults"
}
```

### Theme Preview

#### Preview Theme
```http
GET /api/themes/:id/preview
```

**Query Parameters:**
- `settings` (optional): JSON string of settings to preview

**Response:**
```json
{
  "success": true,
  "previewUrl": "/preview?theme=modern-education&token=abc123",
  "expiresAt": "2025-11-25T15:30:00Z"
}
```

---

## JavaScript/React API

### Theme Context

#### useTheme Hook

```jsx
import { useTheme } from '@/context/ThemeContext';

const MyComponent = () => {
  const {
    activeTheme,      // Current active theme object
    settings,         // Current theme settings
    loading,          // Loading state
    error,           // Error state
    updateSetting,   // Function to update a setting
    reloadSettings   // Function to reload settings
  } = useTheme();

  return (
    <div style={{ color: settings.colors.primary }}>
      <h1>{activeTheme.name}</h1>
    </div>
  );
};
```

#### Theme Provider

```jsx
import { ThemeProvider } from '@/context/ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <YourApp />
    </ThemeProvider>
  );
}
```

### Component Resolution

#### useThemedComponent Hook

```jsx
import { useThemedComponent } from '@/components/ThemeProvider';

const HomePage = () => {
  const Header = useThemedComponent('layout/Header');
  const Hero = useThemedComponent('Hero');
  const Footer = useThemedComponent('layout/Footer');

  return (
    <div>
      <Suspense fallback={<div>Loading...</div>}>
        <Header />
        <Hero title="Welcome" />
        <Footer />
      </Suspense>
    </div>
  );
};
```

#### Component Registry

```javascript
import { registry } from '@/theme/ComponentRegistry';

// Register component
registry.register('Hero', MyCustomHero, {
  priority: 20,
  override: true,
  alias: 'HeroBanner'
});

// Resolve component
const Hero = registry.resolve('Hero');

// Check if component exists
if (registry.has('Hero')) {
  // Use custom hero
}
```

### Settings Manager

#### Get Settings

```javascript
import { settingsManager } from '@/theme/SettingsManager';

// Get all settings
const settings = await settingsManager.getSettings();

// Get specific setting
const primaryColor = settings.colors.primary;
```

#### Update Settings

```javascript
// Update single setting
await settingsManager.setSetting('colors.primary', '#6366F1');

// Update multiple settings
await settingsManager.updateSettings({
  'colors.primary': '#6366F1',
  'colors.secondary': '#10B981'
});
```

#### Reset Settings

```javascript
await settingsManager.resetToDefaults();
```

### Asset Manager

#### Load Theme Assets

```javascript
import { assetManager } from '@/theme/AssetManager';

// Load critical CSS
await assetManager.loadCritical(theme);

// Load deferred assets
await assetManager.loadDeferred(theme);

// Get asset URL
const logoUrl = assetManager.getAssetUrl('images/logo.svg');

// Preload image
await assetManager.preloadImage('/themes/my-theme/hero-bg.jpg');
```

### Theme Loader

#### Load Theme

```javascript
import { themeLoader } from '@/theme/ThemeLoader';

// Load theme into memory
const loadedTheme = await themeLoader.load('modern-education');

// Activate theme
await themeLoader.activate('modern-education');

// Get active theme
const activeTheme = themeLoader.getActiveTheme();

// Unload theme
await themeLoader.unload('old-theme');
```

---

## Node.js/Express API

### Theme Registry

#### Scan for Themes

```javascript
import { ThemeRegistry } from './services/ThemeRegistry';

const registry = new ThemeRegistry();

// Scan themes directory
const themes = await registry.scanThemes();

// Get specific theme
const theme = await registry.getTheme('modern-education');

// Validate theme
const validation = await registry.validate('/path/to/theme');
```

### Theme Controller

```javascript
import {
  getAllThemes,
  getThemeById,
  uploadTheme,
  activateTheme,
  deleteTheme
} from './controllers/themeController';

// Express routes
app.get('/api/themes', getAllThemes);
app.get('/api/themes/:id', getThemeById);
app.post('/api/themes', uploadTheme);
app.post('/api/themes/:id/activate', activateTheme);
app.delete('/api/themes/:id', deleteTheme);
```

### Cache Manager

```javascript
import { cacheManager } from './services/ThemeCacheManager';

// Cache theme
await cacheManager.cacheTheme(theme);

// Get cached theme
const cachedTheme = await cacheManager.getTheme('modern-education');

// Clear cache
await cacheManager.clearThemeCache('modern-education');
await cacheManager.clearAllThemeCaches();
```

---

## WebSocket Events

### Client-Side Listeners

```javascript
import { io } from 'socket.io-client';

const socket = io();

// Listen for theme activation
socket.on('theme:activated', (data) => {
  console.log('Theme activated:', data.themeId);
  // Reload theme
  window.location.reload();
});

// Listen for settings update
socket.on('theme:settings:updated', (data) => {
  console.log('Settings updated:', data.settings);
  // Apply new settings without reload
  applySettings(data.settings);
});
```

### Server-Side Emitters

```javascript
import { io } from './server';

// Emit theme activation
io.emit('theme:activated', {
  themeId: theme._id,
  slug: theme.slug
});

// Emit settings update
io.emit('theme:settings:updated', {
  settings: updatedSettings
});
```

---

## CLI Commands

### Theme Creation

```bash
# Create new theme
npx create-lms-theme <theme-name> [options]

# Options:
#   --template <name>     Template to use (blank|modern|classic)
#   --typescript         Use TypeScript
#   --child-of <slug>    Create as child theme
#   --no-git            Skip git initialization

# Examples:
npx create-lms-theme my-theme --template=modern
npx create-lms-theme child-theme --child-of=modern-education
```

### Theme Validation

```bash
# Validate theme structure
npm run validate

# Validate specific theme
npm run validate -- --theme=/path/to/theme
```

### Theme Packaging

```bash
# Create distribution package
npm run package

# Create package with specific name
npm run package -- --output=my-theme-v1.0.0.zip
```

### Theme Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## Hooks & Filters

### React Hooks

#### useThemeConfig

```jsx
import { useThemeConfig } from '@/hooks/useThemeConfig';

const MyComponent = () => {
  const config = useThemeConfig();

  return (
    <div style={{
      maxWidth: config.layout.containerWidth,
      fontFamily: config.typography.fontFamily
    }}>
      Content
    </div>
  );
};
```

#### useThemeAsset

```jsx
import { useThemeAsset } from '@/hooks/useThemeAsset';

const Logo = () => {
  const logoUrl = useThemeAsset('images/logo.svg');

  return <img src={logoUrl} alt="Logo" />;
};
```

### Server-Side Hooks

#### beforeThemeActivate

```javascript
import { hooks } from './services/ThemeHooks';

hooks.register('beforeThemeActivate', async (theme) => {
  console.log('About to activate theme:', theme.slug);

  // Validate theme compatibility
  if (!isCompatible(theme)) {
    throw new Error('Theme not compatible');
  }
});
```

#### afterThemeActivate

```javascript
hooks.register('afterThemeActivate', async (theme) => {
  console.log('Theme activated:', theme.slug);

  // Clear caches
  await clearCache();

  // Notify users
  await notifyUsers(theme);
});
```

#### beforeSettingsUpdate

```javascript
hooks.register('beforeSettingsUpdate', async (settings) => {
  console.log('Updating settings:', settings);

  // Validate settings
  const validation = validateSettings(settings);
  if (!validation.valid) {
    throw new Error('Invalid settings');
  }
});
```

---

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| `THEME_NOT_FOUND` | Theme not found | Requested theme does not exist |
| `THEME_INVALID` | Invalid theme structure | Theme failed validation |
| `THEME_INCOMPATIBLE` | Incompatible theme version | Theme requires different LMS version |
| `THEME_ALREADY_EXISTS` | Theme already installed | Theme with same slug exists |
| `THEME_ACTIVE` | Cannot modify active theme | Deactivate theme first |
| `SETTINGS_INVALID` | Invalid settings | Settings failed validation |
| `UPLOAD_FAILED` | Theme upload failed | File upload error |
| `ACTIVATION_FAILED` | Theme activation failed | Error during activation |

---

## Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `GET /api/themes` | 100 requests | 1 minute |
| `POST /api/themes` | 5 requests | 1 hour |
| `PUT /api/themes/*/settings` | 30 requests | 1 minute |
| `POST /api/themes/*/activate` | 10 requests | 1 minute |

---

## Versioning

The Theme System API follows semantic versioning (semver):

- **Major version** (X.0.0): Breaking changes
- **Minor version** (1.X.0): New features, backward compatible
- **Patch version** (1.0.X): Bug fixes

**Current Version:** 1.0.0

**Deprecated Endpoints:**
- None (initial release)

**Planned Deprecations:**
- None currently

---

## Authentication

All theme management endpoints require admin authentication:

```http
Authorization: Bearer <jwt-token>
```

**Required Permissions:**
- `theme:read` - View themes
- `theme:write` - Install/delete themes
- `theme:activate` - Activate themes
- `theme:settings` - Modify settings

---

## Support

For API questions or issues:
- Documentation: https://docs.lms.example.com/api
- GitHub Issues: https://github.com/lms/themes/issues
- Email: api@lms.example.com
