# Theme System Architecture
## Comprehensive Design Document for MERN LMS Platform

**Version:** 1.0.0
**Date:** 2025-11-25
**Status:** Design Phase
**Author:** Claude AI Architecture Team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current System Analysis](#current-system-analysis)
3. [Core Architecture Design](#core-architecture-design)
4. [Theme Structure & File System](#theme-structure--file-system)
5. [Theme Discovery & Activation](#theme-discovery--activation)
6. [Configuration System](#configuration-system)
7. [Component Override Patterns](#component-override-patterns)
8. [Styling Strategy](#styling-strategy)
9. [Developer Experience](#developer-experience)
10. [User Experience](#user-experience)
11. [Performance Optimization](#performance-optimization)
12. [Migration Roadmap](#migration-roadmap)
13. [Risk Analysis](#risk-analysis)
14. [Implementation Estimates](#implementation-estimates)
15. [Appendices](#appendices)

---

## Executive Summary

### Vision

Create a WordPress-like theme system for the MERN LMS platform that enables non-technical administrators to switch themes with zero downtime while empowering developers to create and distribute custom themes with minimal effort.

### Key Goals

- **Ease of Use**: Theme switching should be a single click
- **Developer Friendly**: Creating themes should be as easy as WordPress
- **No Vendor Lock-in**: Themes should be portable and standards-based
- **Production Ready**: Hot-swappable with zero downtime
- **Extensible**: Support for child themes and hooks
- **Performance**: No compromise on load times or bundle size

### Design Principles

1. **Convention over Configuration** - Sensible defaults, minimal boilerplate
2. **Progressive Enhancement** - Works out of the box, customizable when needed
3. **Separation of Concerns** - Clear boundaries between theme, content, and logic
4. **API-First Design** - All theme operations available via REST API
5. **Backward Compatibility** - Graceful fallbacks for legacy code

---

## Current System Analysis

### Existing Infrastructure

#### Current Theme Implementation
```javascript
// client/src/context/ThemeContext.jsx
- Basic theme context with settings
- CSS variable injection for primary color
- Settings fetched from API endpoint
- Manual logo uploads
- Limited customization options
```

#### Current Styling Approach
```css
/* client/src/styles/index.css */
@import "tailwindcss"; // Tailwind CSS v4
```

**Strengths:**
- ✅ Tailwind CSS v4 already in use
- ✅ CSS custom properties for theming
- ✅ React Context API for state management
- ✅ API-driven settings system
- ✅ Puck page builder already integrated

**Limitations:**
- ❌ No theme packaging/distribution system
- ❌ Hard-coded component styles
- ❌ No component override mechanism
- ❌ Settings stored in database only (no theme files)
- ❌ No theme preview capability
- ❌ No child theme support

### Technology Stack
```json
{
  "frontend": {
    "framework": "React 18.3.1",
    "routing": "react-router-dom 7.8.2",
    "state": "Redux Toolkit 2.9.0",
    "styling": "Tailwind CSS 4.1.13",
    "pageBuilder": "@measured/puck 0.20.2",
    "bundler": "Vite 7.1.2"
  },
  "backend": {
    "runtime": "Node.js",
    "framework": "Express 5.1.0",
    "database": "MongoDB (Mongoose 8.18.1)",
    "storage": "MinIO 8.0.6"
  }
}
```

---

## Core Architecture Design

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        THEME SYSTEM                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Theme      │  │   Theme      │  │  Component   │         │
│  │   Registry   │──│   Loader     │──│  Resolver    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                  │                  │                 │
│         ├──────────────────┼──────────────────┤                 │
│         │                  │                  │                 │
│  ┌──────▼──────┐  ┌────────▼────────┐  ┌─────▼──────┐         │
│  │   Theme     │  │    Settings     │  │   Asset    │         │
│  │   Storage   │  │    Manager      │  │   Manager  │         │
│  └─────────────┘  └─────────────────┘  └────────────┘         │
│         │                  │                  │                 │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────────┐
│                      APPLICATION LAYER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   React      │  │   Express    │  │   MongoDB    │         │
│  │   Context    │  │   Routes     │  │   Models     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. Theme Registry
**Purpose**: Central repository tracking all available themes

**Responsibilities:**
- Discover themes from `themes/` directory
- Validate theme structure and dependencies
- Maintain theme metadata cache
- Handle theme versioning

**API:**
```javascript
class ThemeRegistry {
  // Get all available themes
  async getThemes(): Promise<Theme[]>

  // Get specific theme details
  async getTheme(themeId: string): Promise<Theme>

  // Register new theme
  async register(themePath: string): Promise<void>

  // Unregister theme
  async unregister(themeId: string): Promise<void>

  // Validate theme structure
  async validate(themePath: string): Promise<ValidationResult>
}
```

#### 2. Theme Loader
**Purpose**: Load and activate themes at runtime

**Responsibilities:**
- Dynamic module loading
- Dependency resolution
- Hot module replacement (HMR)
- Fallback to default theme on errors

**API:**
```javascript
class ThemeLoader {
  // Load theme into memory
  async load(themeId: string): Promise<LoadedTheme>

  // Unload theme from memory
  async unload(themeId: string): Promise<void>

  // Activate theme
  async activate(themeId: string): Promise<void>

  // Get currently active theme
  getActiveTheme(): LoadedTheme
}
```

#### 3. Component Resolver
**Purpose**: Resolve component overrides at render time

**Responsibilities:**
- Map component requests to theme implementations
- Handle component inheritance (parent/child themes)
- Provide fallback components
- Cache resolved components

**API:**
```javascript
class ComponentResolver {
  // Resolve component from active theme
  resolve(componentName: string): ComponentType

  // Check if theme provides component
  has(componentName: string): boolean

  // Get component with fallback chain
  resolveWithFallback(componentName: string): ComponentType
}
```

#### 4. Settings Manager
**Purpose**: Manage theme configuration and customization

**Responsibilities:**
- Store/retrieve theme settings
- Validate setting values
- Provide default values
- Trigger live preview updates

**API:**
```javascript
class SettingsManager {
  // Get all settings for active theme
  async getSettings(): Promise<Settings>

  // Update specific setting
  async setSetting(key: string, value: any): Promise<void>

  // Reset to theme defaults
  async resetToDefaults(): Promise<void>

  // Import/export settings
  async importSettings(json: string): Promise<void>
  async exportSettings(): Promise<string>
}
```

#### 5. Asset Manager
**Purpose**: Handle theme assets (CSS, fonts, images)

**Responsibilities:**
- Asset bundling and optimization
- CDN integration
- Cache busting
- Lazy loading

**API:**
```javascript
class AssetManager {
  // Get asset URL with cache busting
  getAssetUrl(path: string): string

  // Preload critical assets
  preloadCritical(): Promise<void>

  // Load theme stylesheet
  loadStyles(): Promise<void>

  // Unload theme assets
  unloadAssets(themeId: string): Promise<void>
}
```

---

## Theme Structure & File System

### Standard Theme Package Structure

```
my-theme/
├── theme.json                 # Theme metadata and manifest
├── README.md                  # Documentation
├── screenshot.png             # Theme preview (1200x900px)
├── LICENSE.md                 # Theme license
│
├── components/                # Component overrides
│   ├── layout/
│   │   ├── Header.jsx
│   │   ├── Footer.jsx
│   │   └── Sidebar.jsx
│   ├── common/
│   │   ├── Button.jsx
│   │   ├── Card.jsx
│   │   └── Modal.jsx
│   └── index.js              # Component exports
│
├── layouts/                   # Page layout templates
│   ├── default.jsx
│   ├── full-width.jsx
│   ├── sidebar-left.jsx
│   └── sidebar-right.jsx
│
├── styles/                    # Theme styles
│   ├── theme.css             # Main theme stylesheet
│   ├── variables.css         # CSS custom properties
│   ├── utilities.css         # Utility classes
│   └── components/           # Component-specific styles
│       ├── header.css
│       └── footer.css
│
├── assets/                    # Static assets
│   ├── images/
│   │   ├── logo.svg
│   │   ├── hero-bg.jpg
│   │   └── patterns/
│   ├── fonts/
│   │   ├── primary.woff2
│   │   └── secondary.woff2
│   └── icons/
│       └── custom-icons.svg
│
├── hooks/                     # Custom React hooks
│   ├── useThemeConfig.js
│   ├── useMediaQuery.js
│   └── index.js
│
├── utils/                     # Utility functions
│   ├── colors.js
│   ├── typography.js
│   └── index.js
│
├── patterns/                  # Reusable content patterns
│   ├── hero-section.json
│   ├── feature-grid.json
│   └── testimonials.json
│
├── templates/                 # Page templates for Puck
│   ├── home.json
│   ├── about.json
│   └── contact.json
│
└── config/                    # Theme configuration
    ├── settings.json         # Customizer settings schema
    ├── menus.json           # Default menu locations
    └── widgets.json         # Widget areas configuration
```

### theme.json Specification

```json
{
  "name": "Modern Education",
  "slug": "modern-education",
  "version": "1.0.0",
  "description": "A clean, modern theme for educational institutions",
  "author": {
    "name": "Theme Developer",
    "email": "dev@example.com",
    "url": "https://example.com"
  },
  "license": "MIT",
  "screenshot": "screenshot.png",
  "tags": ["education", "modern", "clean", "responsive"],

  "compatibility": {
    "lmsVersion": ">=1.0.0",
    "react": ">=18.0.0",
    "node": ">=18.0.0"
  },

  "parent": null,
  "childThemes": [],

  "support": {
    "childThemes": true,
    "customizer": true,
    "gutenberg": false,
    "puck": true
  },

  "features": {
    "responsive": true,
    "darkMode": true,
    "rtl": false,
    "accessibility": "WCAG-AA"
  },

  "settings": {
    "colors": {
      "primary": {
        "type": "color",
        "default": "#4F46E5",
        "label": "Primary Color",
        "description": "Main brand color used throughout the theme"
      },
      "secondary": {
        "type": "color",
        "default": "#10B981",
        "label": "Secondary Color"
      },
      "accent": {
        "type": "color",
        "default": "#F59E0B",
        "label": "Accent Color"
      }
    },
    "typography": {
      "fontFamily": {
        "type": "select",
        "default": "inter",
        "options": [
          { "value": "inter", "label": "Inter" },
          { "value": "roboto", "label": "Roboto" },
          { "value": "poppins", "label": "Poppins" }
        ],
        "label": "Font Family"
      },
      "fontSize": {
        "type": "range",
        "default": 16,
        "min": 14,
        "max": 20,
        "step": 1,
        "unit": "px",
        "label": "Base Font Size"
      }
    },
    "layout": {
      "containerWidth": {
        "type": "select",
        "default": "1280px",
        "options": [
          { "value": "1024px", "label": "Narrow (1024px)" },
          { "value": "1280px", "label": "Standard (1280px)" },
          { "value": "1536px", "label": "Wide (1536px)" }
        ],
        "label": "Container Width"
      },
      "headerStyle": {
        "type": "select",
        "default": "default",
        "options": [
          { "value": "default", "label": "Default Header" },
          { "value": "transparent", "label": "Transparent Header" },
          { "value": "sticky", "label": "Sticky Header" }
        ],
        "label": "Header Style"
      }
    },
    "branding": {
      "logo": {
        "type": "image",
        "default": null,
        "label": "Logo",
        "description": "Upload your logo (recommended: 200x60px)"
      },
      "favicon": {
        "type": "image",
        "default": null,
        "label": "Favicon",
        "description": "Upload favicon (recommended: 32x32px)"
      }
    }
  },

  "menus": {
    "primary": {
      "label": "Primary Navigation",
      "description": "Main navigation menu in header"
    },
    "footer": {
      "label": "Footer Menu",
      "description": "Links in footer area"
    },
    "mobile": {
      "label": "Mobile Menu",
      "description": "Mobile navigation menu"
    }
  },

  "widgets": {
    "sidebar-main": {
      "label": "Main Sidebar",
      "description": "Primary sidebar for blog and pages"
    },
    "footer-1": {
      "label": "Footer Column 1",
      "description": "First footer widget area"
    },
    "footer-2": {
      "label": "Footer Column 2",
      "description": "Second footer widget area"
    }
  },

  "assets": {
    "styles": [
      "styles/theme.css",
      "styles/variables.css"
    ],
    "scripts": [
      "scripts/theme.js"
    ],
    "fonts": [
      "assets/fonts/primary.woff2"
    ]
  },

  "puck": {
    "componentOverrides": {
      "Hero": "components/Hero.jsx",
      "Button": "components/Button.jsx"
    },
    "newComponents": [
      "components/TestimonialCarousel.jsx",
      "components/PricingTable.jsx"
    ]
  }
}
```

---

## Theme Discovery & Activation

### Discovery Process

#### 1. File System Discovery
```javascript
// server/services/ThemeDiscovery.js
class ThemeDiscovery {
  async scanThemes() {
    const themesDir = path.join(process.cwd(), 'themes');
    const themeDirectories = await fs.readdir(themesDir);

    const themes = [];
    for (const dir of themeDirectories) {
      const themePath = path.join(themesDir, dir);
      const manifestPath = path.join(themePath, 'theme.json');

      if (await this.isValidTheme(manifestPath)) {
        const theme = await this.parseTheme(manifestPath);
        themes.push(theme);
      }
    }

    return themes;
  }

  async isValidTheme(manifestPath) {
    try {
      await fs.access(manifestPath);
      const manifest = await fs.readFile(manifestPath, 'utf8');
      const parsed = JSON.parse(manifest);

      return this.validateManifest(parsed);
    } catch (error) {
      return false;
    }
  }

  validateManifest(manifest) {
    const required = ['name', 'slug', 'version'];
    return required.every(field => manifest[field]);
  }
}
```

#### 2. Database Storage
```javascript
// server/models/Theme.js
const ThemeSchema = new mongoose.Schema({
  slug: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  name: String,
  version: String,
  description: String,
  author: {
    name: String,
    email: String,
    url: String
  },

  // Status
  status: {
    type: String,
    enum: ['active', 'inactive', 'broken'],
    default: 'inactive'
  },

  // Installation details
  installedAt: Date,
  activatedAt: Date,

  // File system location
  path: String,

  // Parsed manifest
  manifest: mongoose.Schema.Types.Mixed,

  // Settings (merged defaults + user customizations)
  settings: mongoose.Schema.Types.Mixed,

  // Metadata
  downloadCount: { type: Number, default: 0 },
  rating: { type: Number, default: 0 },

  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// Ensure only one active theme at a time
ThemeSchema.pre('save', async function(next) {
  if (this.status === 'active') {
    await this.constructor.updateMany(
      { _id: { $ne: this._id }, status: 'active' },
      { status: 'inactive' }
    );
  }
  next();
});

export default mongoose.model('Theme', ThemeSchema);
```

### Installation Methods

#### Method 1: ZIP Upload (Recommended)
```javascript
// server/controllers/themeController.js
export const uploadTheme = async (req, res) => {
  try {
    const zipFile = req.file;
    const extractPath = path.join(process.cwd(), 'themes', 'temp');

    // Extract ZIP
    await extractZip(zipFile.path, extractPath);

    // Validate theme structure
    const validation = await validateThemeStructure(extractPath);
    if (!validation.valid) {
      return res.status(400).json({
        success: false,
        errors: validation.errors
      });
    }

    // Read manifest
    const manifest = await readThemeManifest(extractPath);

    // Check for conflicts
    const existingTheme = await Theme.findOne({ slug: manifest.slug });
    if (existingTheme) {
      return res.status(409).json({
        success: false,
        message: 'Theme already installed'
      });
    }

    // Move to permanent location
    const finalPath = path.join(process.cwd(), 'themes', manifest.slug);
    await fs.move(extractPath, finalPath);

    // Register in database
    const theme = await Theme.create({
      slug: manifest.slug,
      name: manifest.name,
      version: manifest.version,
      description: manifest.description,
      author: manifest.author,
      path: finalPath,
      manifest: manifest,
      settings: manifest.settings || {},
      installedAt: new Date()
    });

    res.json({
      success: true,
      theme
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
};
```

#### Method 2: NPM Package
```javascript
// Install theme as npm package
npm install @lms-themes/modern-education

// server/services/ThemeNpmInstaller.js
class ThemeNpmInstaller {
  async install(packageName) {
    // Install package
    await exec(`npm install ${packageName}`);

    // Find package in node_modules
    const packagePath = path.join(
      process.cwd(),
      'node_modules',
      packageName
    );

    // Symlink to themes directory
    const themesPath = path.join(process.cwd(), 'themes');
    const manifest = require(path.join(packagePath, 'theme.json'));

    await fs.symlink(
      packagePath,
      path.join(themesPath, manifest.slug)
    );

    // Register in database
    return await this.registerTheme(manifest, packagePath);
  }
}
```

#### Method 3: Git Repository
```javascript
// server/services/ThemeGitInstaller.js
class ThemeGitInstaller {
  async install(repoUrl) {
    const tempPath = path.join(process.cwd(), 'themes', 'temp-git');

    // Clone repository
    await exec(`git clone ${repoUrl} ${tempPath}`);

    // Validate and install
    return await this.processGitTheme(tempPath);
  }
}
```

### Activation Process

```javascript
// server/controllers/themeController.js
export const activateTheme = async (req, res) => {
  try {
    const { themeId } = req.params;

    // Find theme
    const theme = await Theme.findById(themeId);
    if (!theme) {
      return res.status(404).json({
        success: false,
        message: 'Theme not found'
      });
    }

    // Deactivate current theme
    await Theme.updateMany(
      { status: 'active' },
      { status: 'inactive' }
    );

    // Activate new theme
    theme.status = 'active';
    theme.activatedAt = new Date();
    await theme.save();

    // Clear cache
    await cacheManager.clearThemeCache();

    // Notify clients via WebSocket
    io.emit('theme:activated', {
      themeId: theme._id,
      slug: theme.slug
    });

    res.json({
      success: true,
      theme
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
};
```

---

## Configuration System

### Visual Customizer Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Customizer Interface                   │
│  ┌───────────────┐              ┌──────────────────┐   │
│  │   Settings    │              │   Live Preview   │   │
│  │   Sidebar     │◄────────────►│   iFrame         │   │
│  │               │              │                  │   │
│  │  - Colors     │              │  Real-time       │   │
│  │  - Typography │              │  Updates         │   │
│  │  - Layout     │              │                  │   │
│  │  - Branding   │              │                  │   │
│  └───────────────┘              └──────────────────┘   │
│         │                               │               │
│         └───────────┬───────────────────┘               │
│                     │                                   │
│              ┌──────▼──────┐                           │
│              │   Settings  │                           │
│              │   Manager   │                           │
│              └─────────────┘                           │
└─────────────────────────────────────────────────────────┘
```

### Customizer Component

```jsx
// client/src/pages/admin/ThemeCustomizer.jsx
import React, { useState, useEffect } from 'react';
import { useTheme } from '@/context/ThemeContext';
import SettingsPanel from '@/components/theme/SettingsPanel';
import LivePreview from '@/components/theme/LivePreview';

const ThemeCustomizer = () => {
  const { activeTheme, settings, updateSetting } = useTheme();
  const [previewUrl, setPreviewUrl] = useState('/');
  const [isDirty, setIsDirty] = useState(false);

  const handleSettingChange = (key, value) => {
    updateSetting(key, value);
    setIsDirty(true);
  };

  const handleSave = async () => {
    try {
      await saveSettings(settings);
      setIsDirty(false);
      toast.success('Settings saved successfully');
    } catch (error) {
      toast.error('Failed to save settings');
    }
  };

  const handleReset = async () => {
    if (confirm('Reset all settings to theme defaults?')) {
      await resetToDefaults();
      setIsDirty(false);
    }
  };

  return (
    <div className="theme-customizer">
      <div className="customizer-header">
        <h1>Customize {activeTheme.name}</h1>
        <div className="actions">
          <button onClick={handleReset} disabled={!isDirty}>
            Reset
          </button>
          <button onClick={handleSave} disabled={!isDirty}>
            Save Changes
          </button>
        </div>
      </div>

      <div className="customizer-body">
        <SettingsPanel
          schema={activeTheme.manifest.settings}
          values={settings}
          onChange={handleSettingChange}
        />

        <LivePreview
          url={previewUrl}
          settings={settings}
          onNavigate={setPreviewUrl}
        />
      </div>
    </div>
  );
};

export default ThemeCustomizer;
```

### Settings Panel Component

```jsx
// client/src/components/theme/SettingsPanel.jsx
import React from 'react';
import ColorPicker from './controls/ColorPicker';
import RangeControl from './controls/RangeControl';
import SelectControl from './controls/SelectControl';
import ImageUpload from './controls/ImageUpload';

const SettingsPanel = ({ schema, values, onChange }) => {
  const renderControl = (key, config) => {
    const value = values[key];

    switch (config.type) {
      case 'color':
        return (
          <ColorPicker
            label={config.label}
            value={value}
            onChange={(val) => onChange(key, val)}
            description={config.description}
          />
        );

      case 'range':
        return (
          <RangeControl
            label={config.label}
            value={value}
            min={config.min}
            max={config.max}
            step={config.step}
            unit={config.unit}
            onChange={(val) => onChange(key, val)}
          />
        );

      case 'select':
        return (
          <SelectControl
            label={config.label}
            value={value}
            options={config.options}
            onChange={(val) => onChange(key, val)}
          />
        );

      case 'image':
        return (
          <ImageUpload
            label={config.label}
            value={value}
            onChange={(val) => onChange(key, val)}
            description={config.description}
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="settings-panel">
      {Object.entries(schema).map(([category, settings]) => (
        <div key={category} className="setting-category">
          <h3>{category}</h3>
          {Object.entries(settings).map(([key, config]) => (
            <div key={key} className="setting-control">
              {renderControl(key, config)}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default SettingsPanel;
```

### Live Preview Component

```jsx
// client/src/components/theme/LivePreview.jsx
import React, { useRef, useEffect } from 'react';

const LivePreview = ({ url, settings, onNavigate }) => {
  const iframeRef = useRef(null);

  useEffect(() => {
    // Inject settings into iframe
    if (iframeRef.current) {
      const iframe = iframeRef.current;
      const iframeWindow = iframe.contentWindow;

      if (iframeWindow.__THEME_PREVIEW__) {
        iframeWindow.__THEME_PREVIEW__.updateSettings(settings);
      }
    }
  }, [settings]);

  const handleLoad = () => {
    // Setup preview mode
    const iframe = iframeRef.current;
    const iframeDocument = iframe.contentDocument;

    // Inject preview CSS
    const style = iframeDocument.createElement('style');
    style.textContent = generatePreviewCSS(settings);
    iframeDocument.head.appendChild(style);

    // Capture navigation
    iframeDocument.addEventListener('click', (e) => {
      const link = e.target.closest('a');
      if (link) {
        e.preventDefault();
        onNavigate(link.href);
      }
    });
  };

  return (
    <div className="live-preview">
      <div className="preview-toolbar">
        <div className="device-selector">
          <button>Desktop</button>
          <button>Tablet</button>
          <button>Mobile</button>
        </div>

        <div className="url-bar">
          <input
            type="text"
            value={url}
            onChange={(e) => onNavigate(e.target.value)}
          />
        </div>
      </div>

      <iframe
        ref={iframeRef}
        src={`${url}?preview=true`}
        onLoad={handleLoad}
        className="preview-iframe"
      />
    </div>
  );
};

const generatePreviewCSS = (settings) => {
  // Convert settings to CSS variables
  let css = ':root {\n';

  Object.entries(settings).forEach(([key, value]) => {
    css += `  --${key}: ${value};\n`;
  });

  css += '}';

  return css;
};

export default LivePreview;
```

### Settings Storage

```javascript
// server/controllers/themeSettingsController.js
export const updateSettings = async (req, res) => {
  try {
    const { settings } = req.body;
    const activeTheme = await Theme.findOne({ status: 'active' });

    if (!activeTheme) {
      return res.status(404).json({
        success: false,
        message: 'No active theme found'
      });
    }

    // Validate settings against schema
    const validation = validateSettings(
      settings,
      activeTheme.manifest.settings
    );

    if (!validation.valid) {
      return res.status(400).json({
        success: false,
        errors: validation.errors
      });
    }

    // Update theme settings
    activeTheme.settings = {
      ...activeTheme.settings,
      ...settings
    };

    activeTheme.updatedAt = new Date();
    await activeTheme.save();

    // Clear cache
    await cacheManager.clearThemeSettingsCache();

    res.json({
      success: true,
      settings: activeTheme.settings
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
};

export const exportSettings = async (req, res) => {
  try {
    const activeTheme = await Theme.findOne({ status: 'active' });

    const exportData = {
      theme: activeTheme.slug,
      version: activeTheme.version,
      exportedAt: new Date().toISOString(),
      settings: activeTheme.settings
    };

    res.setHeader('Content-Type', 'application/json');
    res.setHeader(
      'Content-Disposition',
      `attachment; filename="${activeTheme.slug}-settings.json"`
    );

    res.json(exportData);
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
};

export const importSettings = async (req, res) => {
  try {
    const { settings, theme } = req.body;
    const activeTheme = await Theme.findOne({ status: 'active' });

    // Warn if importing from different theme
    if (theme !== activeTheme.slug) {
      return res.status(400).json({
        success: false,
        message: 'Settings are from a different theme',
        warning: true
      });
    }

    // Validate and merge
    const validated = validateSettings(
      settings,
      activeTheme.manifest.settings
    );

    if (validated.valid) {
      activeTheme.settings = settings;
      await activeTheme.save();

      res.json({
        success: true,
        settings: activeTheme.settings
      });
    } else {
      res.status(400).json({
        success: false,
        errors: validated.errors
      });
    }
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
};
```

---

## Component Override Patterns

### Comparison of Approaches

| Approach | Pros | Cons | Score |
|----------|------|------|-------|
| **A. Component Mapping Registry** | - Centralized control<br>- Easy to debug<br>- Type-safe | - Manual registration<br>- Boilerplate code | 7/10 |
| **B. File Convention** | - Zero config<br>- WordPress-like<br>- Intuitive | - Less type-safe<br>- Runtime errors | 8/10 |
| **C. Higher-Order Component** | - Composable<br>- React patterns<br>- Middleware support | - Complex nesting<br>- Performance overhead | 6/10 |
| **D. Render Props** | - Flexible<br>- Explicit | - Verbose<br>- Callback hell | 5/10 |

**Recommendation: Hybrid Approach (B + A)**

Use file-based convention as primary with component registry as fallback and for advanced use cases.

### Implementation: File-Based Convention

```javascript
// client/src/components/ThemeProvider.jsx
import React, { createContext, useContext, lazy } from 'react';
import { useTheme } from '@/context/ThemeContext';

const ThemeComponentContext = createContext(null);

export const ThemeProvider = ({ children }) => {
  const { activeTheme } = useTheme();

  const resolveComponent = (componentName) => {
    // Try to load from active theme
    try {
      const ThemeComponent = lazy(() =>
        import(`../../../themes/${activeTheme.slug}/components/${componentName}.jsx`)
      );
      return ThemeComponent;
    } catch (error) {
      // Fall back to default component
      const DefaultComponent = lazy(() =>
        import(`@/components/${componentName}.jsx`)
      );
      return DefaultComponent;
    }
  };

  const value = {
    resolveComponent,
    activeTheme
  };

  return (
    <ThemeComponentContext.Provider value={value}>
      {children}
    </ThemeComponentContext.Provider>
  );
};

export const useThemedComponent = (componentName) => {
  const context = useContext(ThemeComponentContext);
  if (!context) {
    throw new Error('useThemedComponent must be used within ThemeProvider');
  }
  return context.resolveComponent(componentName);
};
```

### Using Themed Components

```jsx
// Example: Using themed component
import React, { Suspense } from 'react';
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

export default HomePage;
```

### Component Registry (Advanced)

```javascript
// client/src/theme/ComponentRegistry.js
class ComponentRegistry {
  constructor() {
    this.components = new Map();
    this.aliases = new Map();
  }

  register(name, component, options = {}) {
    this.components.set(name, {
      component,
      priority: options.priority || 10,
      override: options.override || false
    });

    // Register aliases
    if (options.alias) {
      this.aliases.set(options.alias, name);
    }
  }

  resolve(name) {
    // Check alias
    const actualName = this.aliases.get(name) || name;

    // Get registered component
    const entry = this.components.get(actualName);

    if (!entry) {
      throw new Error(`Component "${name}" not found in registry`);
    }

    return entry.component;
  }

  has(name) {
    return this.components.has(name) || this.aliases.has(name);
  }

  // Get all components for a category
  getByCategory(category) {
    return Array.from(this.components.entries())
      .filter(([name]) => name.startsWith(`${category}/`))
      .map(([name, entry]) => ({ name, ...entry }));
  }
}

export const registry = new ComponentRegistry();

// Usage in theme
registry.register('Hero', MyCustomHero, {
  priority: 20,
  override: true,
  alias: 'HeroBanner'
});
```

### Child Theme Support

```javascript
// client/src/theme/ThemeInheritance.js
class ThemeInheritance {
  constructor(childTheme, parentTheme) {
    this.child = childTheme;
    this.parent = parentTheme;
  }

  async resolveComponent(componentName) {
    // Try child theme first
    try {
      const childComponent = await import(
        `../../../themes/${this.child.slug}/components/${componentName}.jsx`
      );
      return childComponent.default;
    } catch (error) {
      // Fall back to parent theme
      try {
        const parentComponent = await import(
          `../../../themes/${this.parent.slug}/components/${componentName}.jsx`
        );
        return parentComponent.default;
      } catch (error) {
        // Fall back to default
        const defaultComponent = await import(
          `@/components/${componentName}.jsx`
        );
        return defaultComponent.default;
      }
    }
  }

  mergeSettings() {
    // Merge parent and child settings
    return {
      ...this.parent.settings,
      ...this.child.settings
    };
  }
}
```

---

## Styling Strategy

### Recommended Approach: Tailwind CSS + CSS Variables

**Rationale:**
- ✅ Already using Tailwind CSS v4
- ✅ Utility-first approach reduces CSS bloat
- ✅ CSS variables for dynamic theming
- ✅ Component-scoped styles when needed
- ✅ Best performance characteristics

### Architecture Layers

```
┌─────────────────────────────────────────────────┐
│         Layer 4: Component Styles               │
│  (Component-specific overrides)                 │
├─────────────────────────────────────────────────┤
│         Layer 3: Theme Utilities                │
│  (Theme-specific utility classes)               │
├─────────────────────────────────────────────────┤
│         Layer 2: Design Tokens                  │
│  (CSS variables for colors, spacing, etc.)      │
├─────────────────────────────────────────────────┤
│         Layer 1: Tailwind Base                  │
│  (Core Tailwind utilities)                      │
└─────────────────────────────────────────────────┘
```

### Theme Styles Structure

```css
/* themes/modern-education/styles/theme.css */

/* Import base theme variables */
@import './variables.css';

/* Import component styles */
@import './components/header.css';
@import './components/footer.css';
@import './components/hero.css';

/* Theme-specific utilities */
@layer utilities {
  .theme-gradient {
    background: linear-gradient(
      135deg,
      var(--color-primary),
      var(--color-secondary)
    );
  }

  .theme-shadow {
    box-shadow: 0 10px 40px rgba(var(--color-primary-rgb), 0.1);
  }
}

/* Custom animations */
@keyframes theme-fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### Design Tokens (CSS Variables)

```css
/* themes/modern-education/styles/variables.css */

:root {
  /* Colors - Primary Palette */
  --color-primary: #4F46E5;
  --color-primary-50: #EEF2FF;
  --color-primary-100: #E0E7FF;
  --color-primary-200: #C7D2FE;
  --color-primary-300: #A5B4FC;
  --color-primary-400: #818CF8;
  --color-primary-500: #6366F1;
  --color-primary-600: #4F46E5;
  --color-primary-700: #4338CA;
  --color-primary-800: #3730A3;
  --color-primary-900: #312E81;

  /* Colors - Secondary */
  --color-secondary: #10B981;
  --color-accent: #F59E0B;

  /* Typography */
  --font-family-primary: 'Inter', system-ui, sans-serif;
  --font-family-secondary: 'Poppins', system-ui, sans-serif;
  --font-family-mono: 'Fira Code', monospace;

  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;

  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;
  --spacing-3xl: 4rem;

  /* Layout */
  --container-max-width: 1280px;
  --container-padding: var(--spacing-lg);

  --header-height: 80px;
  --footer-height: auto;

  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-2xl: 1rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-base: 250ms ease-in-out;
  --transition-slow: 350ms ease-in-out;

  /* Z-index Scale */
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-popover: 1060;
  --z-tooltip: 1070;
}

/* Dark mode variables */
@media (prefers-color-scheme: dark) {
  :root {
    --color-background: #0F172A;
    --color-foreground: #F8FAFC;
    --color-muted: #334155;
  }
}
```

### Tailwind Configuration

```javascript
// themes/modern-education/tailwind.config.js
export default {
  content: [
    './components/**/*.{js,jsx}',
    './layouts/**/*.{js,jsx}',
    './patterns/**/*.{js,jsx}'
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: 'var(--color-primary-50)',
          100: 'var(--color-primary-100)',
          200: 'var(--color-primary-200)',
          300: 'var(--color-primary-300)',
          400: 'var(--color-primary-400)',
          500: 'var(--color-primary-500)',
          600: 'var(--color-primary-600)',
          700: 'var(--color-primary-700)',
          800: 'var(--color-primary-800)',
          900: 'var(--color-primary-900)',
        },
        secondary: 'var(--color-secondary)',
        accent: 'var(--color-accent)'
      },
      fontFamily: {
        sans: ['var(--font-family-primary)'],
        serif: ['var(--font-family-secondary)'],
        mono: ['var(--font-family-mono)']
      },
      spacing: {
        'xs': 'var(--spacing-xs)',
        'sm': 'var(--spacing-sm)',
        'md': 'var(--spacing-md)',
        'lg': 'var(--spacing-lg)',
        'xl': 'var(--spacing-xl)',
        '2xl': 'var(--spacing-2xl)',
        '3xl': 'var(--spacing-3xl)'
      }
    }
  }
};
```

### Dynamic Style Injection

```javascript
// client/src/services/ThemeStyleManager.js
class ThemeStyleManager {
  constructor() {
    this.styleElement = null;
  }

  async loadThemeStyles(theme) {
    // Remove previous theme styles
    this.removeStyles();

    // Load theme CSS
    const cssUrl = `/themes/${theme.slug}/styles/theme.css`;

    this.styleElement = document.createElement('link');
    this.styleElement.rel = 'stylesheet';
    this.styleElement.href = cssUrl;
    this.styleElement.id = `theme-${theme.slug}`;

    document.head.appendChild(this.styleElement);

    // Inject CSS variables from settings
    this.injectVariables(theme.settings);
  }

  injectVariables(settings) {
    const root = document.documentElement;

    Object.entries(settings).forEach(([key, value]) => {
      if (typeof value === 'object') {
        // Nested settings
        Object.entries(value).forEach(([subKey, subValue]) => {
          root.style.setProperty(`--${key}-${subKey}`, subValue);
        });
      } else {
        root.style.setProperty(`--${key}`, value);
      }
    });
  }

  removeStyles() {
    if (this.styleElement) {
      this.styleElement.remove();
      this.styleElement = null;
    }
  }

  updateVariable(key, value) {
    document.documentElement.style.setProperty(`--${key}`, value);
  }
}

export const styleManager = new ThemeStyleManager();
```

### CSS-in-JS Alternative (Optional)

For themes requiring runtime styling:

```javascript
// themes/modern-education/utils/styled.js
import { css } from '@emotion/react';

export const getThemeStyles = (settings) => css`
  .hero {
    background: linear-gradient(
      135deg,
      ${settings.colors.primary},
      ${settings.colors.secondary}
    );
    padding: ${settings.layout.heroPadding}px;
  }

  .button-primary {
    background-color: ${settings.colors.primary};
    color: ${settings.colors.buttonText};
    border-radius: ${settings.layout.borderRadius}px;

    &:hover {
      background-color: ${darken(0.1, settings.colors.primary)};
    }
  }
`;
```

---

## Developer Experience

### Theme Starter Kit (CLI Tool)

```bash
# Create new theme from starter template
npx create-lms-theme my-awesome-theme

# Options
npx create-lms-theme my-theme --template=modern
npx create-lms-theme my-theme --typescript
npx create-lms-theme my-theme --child-of=modern-education
```

### CLI Implementation

```javascript
#!/usr/bin/env node
// packages/create-lms-theme/index.js

import fs from 'fs-extra';
import path from 'path';
import prompts from 'prompts';
import chalk from 'chalk';

async function createTheme() {
  console.log(chalk.blue('🎨 LMS Theme Generator\n'));

  const answers = await prompts([
    {
      type: 'text',
      name: 'name',
      message: 'Theme name:',
      validate: (value) => value.length > 0
    },
    {
      type: 'text',
      name: 'slug',
      message: 'Theme slug:',
      initial: (prev) => prev.toLowerCase().replace(/\s+/g, '-')
    },
    {
      type: 'text',
      name: 'description',
      message: 'Description:'
    },
    {
      type: 'select',
      name: 'template',
      message: 'Choose template:',
      choices: [
        { title: 'Blank (minimal)', value: 'blank' },
        { title: 'Modern (feature-rich)', value: 'modern' },
        { title: 'Classic (traditional)', value: 'classic' }
      ]
    },
    {
      type: 'confirm',
      name: 'typescript',
      message: 'Use TypeScript?',
      initial: false
    },
    {
      type: 'text',
      name: 'parent',
      message: 'Parent theme (leave empty for standalone):',
      initial: ''
    }
  ]);

  const themePath = path.join(process.cwd(), answers.slug);

  console.log(chalk.blue('\n📦 Creating theme structure...'));

  // Create directory structure
  await createDirectoryStructure(themePath);

  // Copy template files
  await copyTemplateFiles(themePath, answers.template);

  // Generate theme.json
  await generateManifest(themePath, answers);

  // Initialize git
  await initGit(themePath);

  console.log(chalk.green('\n✅ Theme created successfully!'));
  console.log(chalk.blue('\nNext steps:'));
  console.log(`  cd ${answers.slug}`);
  console.log(`  npm install`);
  console.log(`  npm run dev`);
}

async function createDirectoryStructure(basePath) {
  const dirs = [
    'components',
    'components/layout',
    'components/common',
    'layouts',
    'styles',
    'styles/components',
    'assets/images',
    'assets/fonts',
    'assets/icons',
    'hooks',
    'utils',
    'patterns',
    'templates',
    'config'
  ];

  for (const dir of dirs) {
    await fs.ensureDir(path.join(basePath, dir));
  }
}

async function generateManifest(basePath, answers) {
  const manifest = {
    name: answers.name,
    slug: answers.slug,
    version: '1.0.0',
    description: answers.description,
    author: {
      name: '',
      email: '',
      url: ''
    },
    license: 'MIT',
    screenshot: 'screenshot.png',
    tags: [],
    compatibility: {
      lmsVersion: '>=1.0.0',
      react: '>=18.0.0',
      node: '>=18.0.0'
    },
    parent: answers.parent || null,
    support: {
      childThemes: true,
      customizer: true,
      puck: true
    },
    settings: {
      colors: {
        primary: {
          type: 'color',
          default: '#4F46E5',
          label: 'Primary Color'
        }
      }
    }
  };

  await fs.writeJSON(
    path.join(basePath, 'theme.json'),
    manifest,
    { spaces: 2 }
  );
}

createTheme().catch(console.error);
```

### Development Workflow

```javascript
// themes/my-theme/package.json
{
  "name": "@lms-themes/my-theme",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext js,jsx",
    "format": "prettier --write .",
    "validate": "node scripts/validate-theme.js",
    "package": "node scripts/package-theme.js"
  },
  "peerDependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^5.0.0",
    "vite": "^7.0.0",
    "eslint": "^9.0.0",
    "prettier": "^3.0.0"
  }
}
```

### Theme Validation Script

```javascript
// themes/my-theme/scripts/validate-theme.js
import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';

async function validateTheme() {
  const errors = [];
  const warnings = [];

  // Check theme.json exists
  if (!await fs.pathExists('theme.json')) {
    errors.push('theme.json not found');
  } else {
    const manifest = await fs.readJSON('theme.json');

    // Validate required fields
    const required = ['name', 'slug', 'version'];
    for (const field of required) {
      if (!manifest[field]) {
        errors.push(`Missing required field: ${field}`);
      }
    }

    // Validate version format
    if (manifest.version && !/^\d+\.\d+\.\d+$/.test(manifest.version)) {
      errors.push('Invalid version format (use semver: 1.0.0)');
    }
  }

  // Check for screenshot
  if (!await fs.pathExists('screenshot.png')) {
    warnings.push('No screenshot.png found');
  }

  // Check for README
  if (!await fs.pathExists('README.md')) {
    warnings.push('No README.md found');
  }

  // Validate component structure
  if (await fs.pathExists('components')) {
    const components = await fs.readdir('components');
    if (components.length === 0) {
      warnings.push('No components found');
    }
  }

  // Report results
  console.log(chalk.blue('\n🔍 Theme Validation Results\n'));

  if (errors.length > 0) {
    console.log(chalk.red('❌ Errors:'));
    errors.forEach(err => console.log(`  - ${err}`));
  }

  if (warnings.length > 0) {
    console.log(chalk.yellow('\n⚠️  Warnings:'));
    warnings.forEach(warn => console.log(`  - ${warn}`));
  }

  if (errors.length === 0 && warnings.length === 0) {
    console.log(chalk.green('✅ Theme validation passed!'));
  }

  process.exit(errors.length > 0 ? 1 : 0);
}

validateTheme().catch(console.error);
```

### Hot Reload Development

```javascript
// client/vite.config.js (updated for theme development)
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => {
  const isDevelopment = mode === 'development';

  return {
    plugins: [
      react(),
      // Custom plugin for theme hot reload
      {
        name: 'theme-hot-reload',
        handleHotUpdate({ file, server }) {
          if (file.includes('/themes/')) {
            // Notify clients to reload theme
            server.ws.send({
              type: 'custom',
              event: 'theme-updated',
              data: { file }
            });
          }
        }
      }
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@themes': path.resolve(__dirname, '../themes')
      }
    },
    server: {
      watch: {
        // Watch theme directories
        ignored: ['!**/themes/**']
      }
    }
  };
});
```

### Documentation Generator

```javascript
// scripts/generate-theme-docs.js
import fs from 'fs-extra';
import path from 'path';
import { marked } from 'marked';

async function generateDocs(themePath) {
  const manifest = await fs.readJSON(
    path.join(themePath, 'theme.json')
  );

  let docs = `# ${manifest.name}\n\n`;
  docs += `${manifest.description}\n\n`;

  // Settings documentation
  docs += '## Customization Options\n\n';
  docs += '### Colors\n\n';

  Object.entries(manifest.settings.colors || {}).forEach(([key, config]) => {
    docs += `#### ${config.label}\n`;
    docs += `- **Default:** ${config.default}\n`;
    docs += `- **Description:** ${config.description || 'N/A'}\n\n`;
  });

  // Component documentation
  docs += '## Component Overrides\n\n';
  const componentsDir = path.join(themePath, 'components');

  if (await fs.pathExists(componentsDir)) {
    const components = await findComponents(componentsDir);
    components.forEach(comp => {
      docs += `- \`${comp}\`\n`;
    });
  }

  // Write documentation
  await fs.writeFile(
    path.join(themePath, 'DOCUMENTATION.md'),
    docs
  );

  console.log('Documentation generated successfully!');
}

async function findComponents(dir, prefix = '') {
  const components = [];
  const entries = await fs.readdir(dir, { withFileTypes: true });

  for (const entry of entries) {
    if (entry.isDirectory()) {
      const nested = await findComponents(
        path.join(dir, entry.name),
        `${prefix}${entry.name}/`
      );
      components.push(...nested);
    } else if (entry.name.endsWith('.jsx')) {
      components.push(`${prefix}${entry.name}`);
    }
  }

  return components;
}
```

---

## User Experience

### Theme Browser Interface

```jsx
// client/src/pages/admin/ThemeBrowser.jsx
import React, { useState, useEffect } from 'react';
import { useTheme } from '@/context/ThemeContext';
import ThemeCard from '@/components/theme/ThemeCard';
import ThemePreview from '@/components/theme/ThemePreview';

const ThemeBrowser = () => {
  const [themes, setThemes] = useState([]);
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [previewMode, setPreviewMode] = useState(false);
  const { activeTheme, activateTheme } = useTheme();

  useEffect(() => {
    fetchThemes();
  }, []);

  const fetchThemes = async () => {
    const response = await fetch('/api/themes');
    const data = await response.json();
    setThemes(data.themes);
  };

  const handleActivate = async (theme) => {
    if (confirm(`Activate "${theme.name}" theme?`)) {
      await activateTheme(theme.id);
      toast.success('Theme activated successfully');
    }
  };

  const handlePreview = (theme) => {
    setSelectedTheme(theme);
    setPreviewMode(true);
  };

  return (
    <div className="theme-browser">
      <div className="browser-header">
        <h1>Themes</h1>
        <div className="actions">
          <button onClick={() => navigate('/admin/themes/upload')}>
            Upload Theme
          </button>
          <button onClick={() => window.open('/theme-marketplace')}>
            Browse Marketplace
          </button>
        </div>
      </div>

      {previewMode && (
        <ThemePreview
          theme={selectedTheme}
          onClose={() => setPreviewMode(false)}
          onActivate={() => handleActivate(selectedTheme)}
        />
      )}

      <div className="themes-grid">
        {themes.map(theme => (
          <ThemeCard
            key={theme.id}
            theme={theme}
            isActive={theme.id === activeTheme.id}
            onActivate={() => handleActivate(theme)}
            onPreview={() => handlePreview(theme)}
            onCustomize={() => navigate(`/admin/theme/customize/${theme.id}`)}
          />
        ))}
      </div>
    </div>
  );
};

export default ThemeBrowser;
```

### Theme Card Component

```jsx
// client/src/components/theme/ThemeCard.jsx
import React from 'react';

const ThemeCard = ({ theme, isActive, onActivate, onPreview, onCustomize }) => {
  return (
    <div className={`theme-card ${isActive ? 'active' : ''}`}>
      <div className="theme-screenshot">
        <img
          src={theme.screenshot || '/placeholder-theme.png'}
          alt={theme.name}
        />
        {isActive && (
          <div className="active-badge">
            Active Theme
          </div>
        )}
      </div>

      <div className="theme-info">
        <h3>{theme.name}</h3>
        <p className="version">v{theme.version}</p>
        <p className="description">{theme.description}</p>

        <div className="theme-meta">
          <span className="author">By {theme.author.name}</span>
          {theme.rating && (
            <span className="rating">
              ⭐ {theme.rating.toFixed(1)}
            </span>
          )}
        </div>

        <div className="theme-tags">
          {theme.tags.map(tag => (
            <span key={tag} className="tag">{tag}</span>
          ))}
        </div>
      </div>

      <div className="theme-actions">
        {isActive ? (
          <>
            <button
              onClick={onCustomize}
              className="btn-primary"
            >
              Customize
            </button>
          </>
        ) : (
          <>
            <button
              onClick={onPreview}
              className="btn-secondary"
            >
              Preview
            </button>
            <button
              onClick={onActivate}
              className="btn-primary"
            >
              Activate
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default ThemeCard;
```

### Live Theme Preview

```jsx
// client/src/components/theme/ThemePreview.jsx
import React, { useRef, useEffect } from 'react';

const ThemePreview = ({ theme, onClose, onActivate }) => {
  const iframeRef = useRef(null);

  useEffect(() => {
    // Inject theme styles into preview iframe
    const iframe = iframeRef.current;
    if (iframe) {
      iframe.onload = () => {
        const iframeDoc = iframe.contentDocument;
        const link = iframeDoc.createElement('link');
        link.rel = 'stylesheet';
        link.href = `/themes/${theme.slug}/styles/theme.css`;
        iframeDoc.head.appendChild(link);
      };
    }
  }, [theme]);

  return (
    <div className="theme-preview-modal">
      <div className="preview-header">
        <div className="theme-info">
          <h2>{theme.name}</h2>
          <span className="version">v{theme.version}</span>
        </div>

        <div className="preview-actions">
          <button onClick={onActivate} className="btn-primary">
            Activate This Theme
          </button>
          <button onClick={onClose} className="btn-secondary">
            Close Preview
          </button>
        </div>
      </div>

      <div className="preview-toolbar">
        <div className="device-selector">
          <button className="active">
            🖥️ Desktop
          </button>
          <button>
            📱 Tablet
          </button>
          <button>
            📱 Mobile
          </button>
        </div>
      </div>

      <div className="preview-frame">
        <iframe
          ref={iframeRef}
          src={`/?preview_theme=${theme.slug}`}
          title={`Preview ${theme.name}`}
          className="preview-iframe"
        />
      </div>
    </div>
  );
};

export default ThemePreview;
```

### Mobile-Responsive Customizer

```css
/* Responsive customizer layout */
.theme-customizer {
  display: grid;
  grid-template-columns: 320px 1fr;
  height: 100vh;
}

@media (max-width: 1024px) {
  .theme-customizer {
    grid-template-columns: 1fr;
  }

  .settings-panel {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    width: 320px;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: 1000;
  }

  .settings-panel.open {
    transform: translateX(0);
  }

  .live-preview {
    grid-column: 1;
  }
}
```

---

## Performance Optimization

### Code Splitting Strategy

```javascript
// client/src/router/ThemeRoutes.jsx
import { lazy, Suspense } from 'react';

const loadThemeComponent = (themeslug, componentName) => {
  return lazy(() =>
    import(`../../../themes/${themeSlug}/components/${componentName}.jsx`)
      .catch(() => import(`@/components/${componentName}.jsx`))
  );
};

// Dynamic imports for theme components
const routes = [
  {
    path: '/',
    component: lazy(() =>
      import('../../../themes/active/pages/Home.jsx')
        .catch(() => import('@/pages/Home.jsx'))
    )
  }
];
```

### Asset Optimization

```javascript
// server/middleware/themeAssets.js
import sharp from 'sharp';
import { minify } from 'terser';

export const optimizeThemeAssets = async (req, res, next) => {
  const { themeSlug, assetPath } = req.params;
  const fullPath = path.join(
    process.cwd(),
    'themes',
    themeSlug,
    'assets',
    assetPath
  );

  // Check cache first
  const cached = await cache.get(`theme:asset:${themeSlug}:${assetPath}`);
  if (cached) {
    return res.send(cached);
  }

  let optimized;

  // Optimize based on file type
  if (assetPath.match(/\.(jpg|jpeg|png|webp)$/i)) {
    // Image optimization
    optimized = await sharp(fullPath)
      .resize(1920, null, { withoutEnlargement: true })
      .webp({ quality: 85 })
      .toBuffer();

  } else if (assetPath.endsWith('.js')) {
    // JS minification
    const code = await fs.readFile(fullPath, 'utf8');
    const minified = await minify(code);
    optimized = minified.code;

  } else if (assetPath.endsWith('.css')) {
    // CSS minification
    const css = await fs.readFile(fullPath, 'utf8');
    optimized = await cssnano.process(css);
  }

  // Cache optimized asset
  await cache.set(
    `theme:asset:${themeSlug}:${assetPath}`,
    optimized,
    { ttl: 3600 }
  );

  res.send(optimized);
};
```

### Lazy Loading Theme Assets

```javascript
// client/src/services/ThemeAssetLoader.js
class ThemeAssetLoader {
  constructor() {
    this.loadedAssets = new Set();
  }

  async loadCritical(theme) {
    // Load critical CSS immediately
    await this.loadStylesheet(
      `/themes/${theme.slug}/styles/critical.css`,
      true
    );
  }

  async loadDeferred(theme) {
    // Load non-critical assets after page load
    requestIdleCallback(() => {
      this.loadStylesheet(
        `/themes/${theme.slug}/styles/theme.css`,
        false
      );
    });
  }

  async loadStylesheet(url, critical = false) {
    if (this.loadedAssets.has(url)) return;

    return new Promise((resolve, reject) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = url;

      if (!critical) {
        link.media = 'print';
        link.onload = () => {
          link.media = 'all';
        };
      }

      link.onload = () => {
        this.loadedAssets.add(url);
        resolve();
      };

      link.onerror = reject;

      document.head.appendChild(link);
    });
  }

  preloadImage(src) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = resolve;
      img.onerror = reject;
      img.src = src;
    });
  }

  async preloadThemeAssets(theme) {
    const assets = theme.manifest.assets || {};

    // Preload fonts
    if (assets.fonts) {
      assets.fonts.forEach(font => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'font';
        link.type = 'font/woff2';
        link.href = `/themes/${theme.slug}/${font}`;
        link.crossOrigin = 'anonymous';
        document.head.appendChild(link);
      });
    }

    // Preload critical images
    if (assets.criticalImages) {
      await Promise.all(
        assets.criticalImages.map(img =>
          this.preloadImage(`/themes/${theme.slug}/${img}`)
        )
      );
    }
  }
}

export const assetLoader = new ThemeAssetLoader();
```

### Caching Strategy

```javascript
// server/services/ThemeCacheManager.js
import Redis from 'ioredis';

class ThemeCacheManager {
  constructor() {
    this.redis = new Redis(process.env.REDIS_URL);
    this.ttl = {
      theme: 3600,        // 1 hour
      settings: 1800,     // 30 minutes
      assets: 86400,      // 24 hours
      components: 7200    // 2 hours
    };
  }

  async cacheTheme(theme) {
    await this.redis.setex(
      `theme:${theme.slug}`,
      this.ttl.theme,
      JSON.stringify(theme)
    );
  }

  async getTheme(slug) {
    const cached = await this.redis.get(`theme:${slug}`);
    return cached ? JSON.parse(cached) : null;
  }

  async cacheSettings(themeSlug, settings) {
    await this.redis.setex(
      `theme:settings:${themeSlug}`,
      this.ttl.settings,
      JSON.stringify(settings)
    );
  }

  async getSettings(themeSlug) {
    const cached = await this.redis.get(`theme:settings:${themeSlug}`);
    return cached ? JSON.parse(cached) : null;
  }

  async clearThemeCache(themeSlug) {
    const keys = await this.redis.keys(`theme:*:${themeSlug}:*`);
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }

  async clearAllThemeCaches() {
    const keys = await this.redis.keys('theme:*');
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }
}

export const cacheManager = new ThemeCacheManager();
```

### Bundle Size Monitoring

```javascript
// vite.config.js - Bundle analysis
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: './dist/stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true
    })
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom', 'react-router-dom'],
          'theme-system': [
            './src/context/ThemeContext.jsx',
            './src/services/ThemeLoader.js'
          ]
        }
      }
    }
  }
});
```

---

## Migration Roadmap

### Phase 1: Extract Base Theme (Week 1-2)

**Objective:** Create a default theme from existing codebase

**Tasks:**
1. Create `themes/default/` directory structure
2. Move existing components to `themes/default/components/`
3. Extract styles to `themes/default/styles/`
4. Create `theme.json` manifest
5. Document all components

**Deliverables:**
- ✅ Default theme package
- ✅ Component inventory
- ✅ Style audit complete

**Risk:** Medium - Requires careful refactoring

### Phase 2: Theme Abstraction Layer (Week 3-4)

**Objective:** Build core theme system infrastructure

**Tasks:**
1. Implement Theme Registry
2. Create Theme Loader service
3. Build Component Resolver
4. Develop Settings Manager
5. Create Asset Manager

**Deliverables:**
- ✅ Theme system core (`/src/theme/`)
- ✅ API endpoints (`/api/themes/`)
- ✅ Database models
- ✅ Unit tests

**Risk:** High - Complex architecture changes

### Phase 3: Theme Discovery & Loading (Week 5-6)

**Objective:** Enable theme discovery and activation

**Tasks:**
1. Implement theme scanning
2. Build theme validation
3. Create activation mechanism
4. Develop hot-reloading
5. Add error handling

**Deliverables:**
- ✅ Theme discovery system
- ✅ Admin theme browser UI
- ✅ Theme activation flow
- ✅ Integration tests

**Risk:** Medium - Requires thorough testing

### Phase 4: Customizer Implementation (Week 7-8)

**Objective:** Build visual theme customizer

**Tasks:**
1. Create customizer UI
2. Implement live preview
3. Build settings controls
4. Add import/export
5. Mobile responsive design

**Deliverables:**
- ✅ Theme customizer page
- ✅ Settings controls library
- ✅ Live preview system
- ✅ Export/import functionality

**Risk:** Medium - Complex UI requirements

### Phase 5: Developer Tools (Week 9-10)

**Objective:** Create developer-friendly tools

**Tasks:**
1. Build CLI tool (`create-lms-theme`)
2. Create theme starter templates
3. Develop validation scripts
4. Build documentation generator
5. Add hot-reload support

**Deliverables:**
- ✅ Theme CLI tool
- ✅ Starter templates
- ✅ Developer documentation
- ✅ Theme best practices guide

**Risk:** Low - Independent of core system

### Phase 6: Child Theme Support (Week 11-12)

**Objective:** Enable theme inheritance

**Tasks:**
1. Implement theme inheritance
2. Build override resolution
3. Add settings merging
4. Create parent/child linking
5. Test edge cases

**Deliverables:**
- ✅ Child theme system
- ✅ Inheritance documentation
- ✅ Example child theme
- ✅ Migration guide

**Risk:** High - Complex inheritance logic

### Phase 7: Performance Optimization (Week 13-14)

**Objective:** Optimize theme loading and rendering

**Tasks:**
1. Implement code splitting
2. Add asset optimization
3. Set up caching
4. Lazy load components
5. Bundle size optimization

**Deliverables:**
- ✅ Performance benchmarks
- ✅ Caching strategy
- ✅ Asset pipeline
- ✅ Bundle analysis

**Risk:** Medium - Performance trade-offs

### Phase 8: Testing & Documentation (Week 15-16)

**Objective:** Comprehensive testing and docs

**Tasks:**
1. Write integration tests
2. Add E2E tests
3. Complete API documentation
4. Create video tutorials
5. Build theme marketplace (optional)

**Deliverables:**
- ✅ Test coverage >80%
- ✅ Complete documentation
- ✅ Migration guide
- ✅ Video tutorials

**Risk:** Low - Final polish

### Migration Timeline

```
Month 1          Month 2          Month 3          Month 4
├─────────────┼─────────────┼─────────────┼─────────────┤
│  Phase 1-2  │  Phase 3-4  │  Phase 5-6  │  Phase 7-8  │
│             │             │             │             │
│ Extract     │ Discovery   │ Dev Tools   │ Optimize    │
│ Base Theme  │ & Loader    │ & Child     │ & Polish    │
│             │             │ Themes      │             │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### Backward Compatibility Strategy

**Approach:** Gradual migration with feature flags

```javascript
// Feature flag system
const FEATURES = {
  THEME_SYSTEM_ENABLED: process.env.ENABLE_THEME_SYSTEM === 'true',
  LEGACY_MODE: process.env.LEGACY_MODE === 'true'
};

// Component resolution with fallback
const getComponent = (name) => {
  if (FEATURES.THEME_SYSTEM_ENABLED) {
    return resolveThemeComponent(name);
  }
  return resolveLegacyComponent(name);
};
```

**Migration Path for Users:**

1. **No action required** - Default theme maintains existing look
2. **Optional upgrade** - New themes available but not mandatory
3. **Gradual adoption** - Customize at own pace
4. **Zero downtime** - Theme switching instant

---

## Risk Analysis

### Technical Risks

#### 1. Performance Impact
**Risk Level:** HIGH
**Probability:** Medium
**Impact:** High

**Description:** Theme loading could slow initial page load

**Mitigation:**
- Implement aggressive caching
- Use code splitting
- Lazy load non-critical components
- Set bundle size budgets
- Monitor with real-user metrics

#### 2. Breaking Changes
**Risk Level:** HIGH
**Probability:** Medium
**Impact:** High

**Description:** Theme system could break existing functionality

**Mitigation:**
- Comprehensive testing suite
- Feature flags for gradual rollout
- Maintain legacy mode
- Thorough documentation
- Beta testing period

#### 3. Browser Compatibility
**Risk Level:** MEDIUM
**Probability:** Low
**Impact:** Medium

**Description:** Dynamic imports may not work in older browsers

**Mitigation:**
- Polyfills for older browsers
- Fallback to static imports
- Progressive enhancement
- Browser support matrix

#### 4. Security Vulnerabilities
**Risk Level:** HIGH
**Probability:** Low
**Impact:** Critical

**Description:** User-uploaded themes could contain malicious code

**Mitigation:**
- Theme validation and sandboxing
- Code review for marketplace themes
- Content Security Policy (CSP)
- Input sanitization
- Regular security audits

### Business Risks

#### 1. Development Time
**Risk Level:** MEDIUM
**Probability:** High
**Impact:** Medium

**Description:** Implementation may take longer than estimated

**Mitigation:**
- Phased rollout approach
- MVP first, iterate later
- Parallel development tracks
- Regular progress reviews

#### 2. User Adoption
**Risk Level:** LOW
**Probability:** Low
**Impact:** Low

**Description:** Users may not want to switch themes

**Mitigation:**
- Make default theme excellent
- Showcase theme benefits
- Provide easy customization
- Gradual feature introduction

#### 3. Maintenance Burden
**Risk Level:** MEDIUM
**Probability:** Medium
**Impact:** Medium

**Description:** Supporting multiple themes increases maintenance

**Mitigation:**
- Clear theme standards
- Automated testing
- Version compatibility checks
- Deprecation policy

---

## Implementation Estimates

### Development Effort (Person-Hours)

| Phase | Tasks | Hours | Complexity |
|-------|-------|-------|------------|
| Phase 1 | Extract Base Theme | 80 | Medium |
| Phase 2 | Abstraction Layer | 120 | High |
| Phase 3 | Discovery & Loading | 100 | High |
| Phase 4 | Customizer | 80 | Medium |
| Phase 5 | Developer Tools | 60 | Low |
| Phase 6 | Child Themes | 80 | High |
| Phase 7 | Performance | 60 | Medium |
| Phase 8 | Testing & Docs | 60 | Low |
| **Total** | | **640 hours** | |

**Team Composition:**
- 1 Senior Full-Stack Developer (Lead)
- 1 Frontend Developer
- 1 Backend Developer
- 1 QA Engineer (part-time)

**Timeline:** 16 weeks (4 months)

### Cost Breakdown

| Item | Cost (USD) |
|------|------------|
| Development (640 hrs @ $100/hr) | $64,000 |
| QA/Testing (160 hrs @ $75/hr) | $12,000 |
| Design/UX (40 hrs @ $120/hr) | $4,800 |
| DevOps (20 hrs @ $150/hr) | $3,000 |
| Documentation (40 hrs @ $80/hr) | $3,200 |
| **Total** | **$87,000** |

### ROI Projections

**Benefits:**
- Easier rebranding for white-label clients: $50k/year
- Premium theme marketplace revenue: $30k/year
- Reduced customization requests: $20k/year
- Faster client onboarding: $15k/year

**Total Annual Benefit:** $115k/year
**Payback Period:** 9 months
**5-Year ROI:** 561%

---

## Appendices

### Appendix A: API Reference

#### Theme API Endpoints

```
GET    /api/themes                    # List all themes
GET    /api/themes/:id                # Get theme details
POST   /api/themes                    # Upload new theme
PUT    /api/themes/:id                # Update theme
DELETE /api/themes/:id                # Delete theme
POST   /api/themes/:id/activate       # Activate theme
GET    /api/themes/:id/preview        # Preview theme
GET    /api/themes/active             # Get active theme
GET    /api/themes/active/settings    # Get theme settings
PUT    /api/themes/active/settings    # Update settings
POST   /api/themes/settings/export    # Export settings
POST   /api/themes/settings/import    # Import settings
POST   /api/themes/settings/reset     # Reset to defaults
```

### Appendix B: Component Naming Conventions

**Layout Components:**
- `layout/Header.jsx`
- `layout/Footer.jsx`
- `layout/Sidebar.jsx`
- `layout/Navigation.jsx`

**Common Components:**
- `common/Button.jsx`
- `common/Card.jsx`
- `common/Modal.jsx`
- `common/Input.jsx`

**Page Components:**
- `pages/HomePage.jsx`
- `pages/AboutPage.jsx`
- `pages/CoursePage.jsx`

### Appendix C: Best Practices

#### Theme Development Checklist

- [ ] Follow file structure conventions
- [ ] Use semantic component names
- [ ] Implement responsive design
- [ ] Add accessibility features
- [ ] Optimize images and assets
- [ ] Test in multiple browsers
- [ ] Document customization options
- [ ] Include screenshot (1200x900px)
- [ ] Write comprehensive README
- [ ] Add license information

#### Performance Targets

- First Contentful Paint (FCP): < 1.8s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.8s
- Cumulative Layout Shift (CLS): < 0.1
- First Input Delay (FID): < 100ms

### Appendix D: Resources

**Documentation:**
- React Lazy Loading: https://react.dev/reference/react/lazy
- Tailwind CSS: https://tailwindcss.com/docs
- Vite: https://vitejs.dev/guide/

**Tools:**
- Theme Validator: `npm run validate`
- Bundle Analyzer: `npm run analyze`
- Performance Monitor: Chrome DevTools

**Community:**
- Theme Developer Forum: (to be created)
- Discord Channel: #theme-development
- GitHub Discussions: Theme System

---

## Conclusion

This theme system architecture provides a comprehensive blueprint for implementing a WordPress-like theme experience in the MERN LMS platform. The design prioritizes:

1. **Developer Experience** - Easy theme creation with CLI tools
2. **User Experience** - Simple theme switching and customization
3. **Performance** - Optimized loading and caching
4. **Flexibility** - Support for child themes and overrides
5. **Maintainability** - Clear conventions and documentation

**Next Steps:**

1. Review this document with the development team
2. Prioritize features for MVP
3. Create detailed task breakdowns for Phase 1
4. Set up development environment
5. Begin implementation

**Success Metrics:**

- Theme activation time < 2 seconds
- Customizer updates in real-time
- Zero breaking changes for existing users
- 5+ community themes within 6 months
- 90%+ developer satisfaction score

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-25
**Status:** Ready for Review
**Approval Required:** Technical Lead, Product Manager, CTO
