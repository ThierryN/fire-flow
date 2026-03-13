# MERN Community LMS - Theme Developer Handbook

**Version:** 1.0.0
**Last Updated:** January 11, 2026
**Platform:** Node.js / Express / PostgreSQL / React / Vite / Tailwind CSS

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started](#2-getting-started)
3. [Theme Architecture Overview](#3-theme-architecture-overview)
4. [Theme File Structure](#4-theme-file-structure)
5. [Theme Manifest (theme.json)](#5-theme-manifest-themejson)
6. [Theme Hooks System](#6-theme-hooks-system)
7. [Styling with Tailwind CSS](#7-styling-with-tailwind-css)
8. [Puck Editor Integration](#8-puck-editor-integration)
9. [Database Schema](#9-database-schema)
10. [Admin Interface](#10-admin-interface)
11. [Complete Example Theme](#11-complete-example-theme)
12. [API Reference](#12-api-reference)
13. [Best Practices](#13-best-practices)
14. [Troubleshooting](#14-troubleshooting)
15. [Appendix: Implementation Roadmap](#15-appendix-implementation-roadmap)

---

## 1. Introduction

### What is a Theme?

A theme is a self-contained package that controls the visual appearance and layout of the MERN Community LMS. Unlike plugins which add functionality, themes focus on:

- **Visual Design** - Colors, typography, spacing, and overall aesthetics
- **Layout Structure** - Header, footer, sidebar, content arrangement
- **Component Styling** - How Puck components render
- **User Experience** - Responsive design, dark mode, accessibility

### WordPress-Style Architecture

Our theme system is inspired by WordPress's proven theme architecture:

| Concept | WordPress | MERN LMS |
|---------|-----------|----------|
| Theme Manifest | `style.css` header | `theme.json` |
| Entry Point | `functions.php` | `index.jsx` / `functions.js` |
| Templates | PHP templates | React/JSX components |
| Customizer | WP Customizer | ThemeCustomizer.jsx |
| Hooks | `add_action/add_filter` | `hooks.addAction/addFilter` |
| Child Themes | Child theme directory | Theme extends base |

### Why Use Themes?

1. **Separation of Concerns** - Design stays separate from functionality
2. **Easy Switching** - Change look without losing content
3. **Customization** - Users can personalize without coding
4. **Reusability** - Share themes across installations
5. **Marketplace** - Build and distribute custom themes

---

## 2. Getting Started

### Quick Start: Create Your First Theme

**Step 1: Create Theme Directory**

```bash
mkdir -p client/src/themes/my-first-theme
```

**Step 2: Create theme.json**

```json
{
  "name": "My First Theme",
  "slug": "my-first-theme",
  "version": "1.0.0",
  "description": "A simple custom theme for learning",
  "author": "Your Name",
  "entryPoint": "index.jsx",
  "supports": ["custom-colors", "dark-mode"],
  "themeSettings": {
    "colors": {
      "primary": {
        "label": "Primary Color",
        "default": "#4F46E5",
        "type": "color"
      }
    }
  }
}
```

**Step 3: Create index.jsx**

```jsx
/**
 * My First Theme
 * Entry point for theme components and exports
 */

import './styles/theme.css';

// Theme metadata
export const themeMeta = {
  name: 'My First Theme',
  slug: 'my-first-theme',
  version: '1.0.0'
};

// Theme layouts
export { default as DefaultLayout } from './layouts/DefaultLayout';
export { default as HomeLayout } from './layouts/HomeLayout';

// Theme components (optional overrides)
export { default as Header } from './components/Header';
export { default as Footer } from './components/Footer';

// Theme activation function
export async function activate({ hooks, config, themeId }) {
  console.log('[My First Theme] Activated!');

  // Register hooks here
  hooks.addFilter('theme.colors.primary', (color) => {
    return config.colors?.primary || color;
  }, 10, 1, themeId);
}

// Theme deactivation function
export async function deactivate({ hooks, themeId }) {
  console.log('[My First Theme] Deactivated!');
}
```

**Step 4: Create Basic Styles**

```css
/* client/src/themes/my-first-theme/styles/theme.css */

:root {
  --theme-primary: var(--color-primary, #4F46E5);
  --theme-secondary: var(--color-secondary, #d946ef);
  --theme-font-family: 'Inter', sans-serif;
}

/* Theme-specific styles */
.theme-my-first-theme {
  font-family: var(--theme-font-family);
}

.theme-my-first-theme .hero {
  background: linear-gradient(135deg, var(--theme-primary), var(--theme-secondary));
}
```

**Step 5: Activate Theme**

Navigate to **Admin Panel > Appearance > Themes** and click "Activate" on your theme.

---

## 3. Theme Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        MERN LMS Client                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────────┐    ┌───────────────┐  │
│   │ThemeContext │◄───│  ThemeManager   │───►│   Database    │  │
│   │  (React)    │    │  (Lifecycle)    │    │   (themes,    │  │
│   └──────┬──────┘    └────────┬────────┘    │theme_settings)│  │
│          │                    │              └───────────────┘  │
│          │         ┌──────────┴──────────┐                     │
│          │         │                     │                     │
│   ┌──────▼──────┐  │  ┌───────────────┐  │                     │
│   │ Puck Editor │  │  │ Theme A       │  │                     │
│   │ (uses theme │  │  │ (index.jsx)   │  │                     │
│   │  components)│  │  └───────────────┘  │                     │
│   └─────────────┘  │  ┌───────────────┐  │                     │
│                    │  │ Theme B       │  │                     │
│                    │  │ (index.jsx)   │  │                     │
│                    │  └───────────────┘  │                     │
│                    └─────────────────────┘                     │
│                         themes/installed/                       │
└─────────────────────────────────────────────────────────────────┘
```

### Theme Loading Flow

```
User Visits Page
       │
       ▼
┌─────────────────┐
│ ThemeContext    │
│ (loads active   │
│  theme)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Theme Module    │────►│ Apply CSS       │
│ (index.jsx)     │     │ Variables       │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Theme Layouts   │────►│ Puck Components │
│ (Header/Footer) │     │ (with overrides)│
└─────────────────┘     └─────────────────┘
```

---

## 4. Theme File Structure

### Minimum Required Structure

```
client/src/themes/
└── my-theme/
    ├── theme.json      # Required: Theme manifest
    └── index.jsx       # Required: Entry point
```

### Recommended Full Structure

```
client/src/themes/
└── my-theme/
    ├── theme.json              # Theme manifest
    ├── index.jsx               # Main entry point
    ├── README.md               # Documentation
    ├── screenshot.png          # Preview image (1200x900px)
    │
    ├── /layouts/               # Page layouts
    │   ├── DefaultLayout.jsx   # Base layout
    │   ├── HomeLayout.jsx      # Homepage layout
    │   ├── PageLayout.jsx      # Standard page
    │   ├── BlogLayout.jsx      # Blog post layout
    │   └── CourseLayout.jsx    # Course detail layout
    │
    ├── /components/            # Theme components
    │   ├── Header.jsx          # Site header
    │   ├── Footer.jsx          # Site footer
    │   ├── Navigation.jsx      # Main navigation
    │   ├── Sidebar.jsx         # Sidebar component
    │   └── Breadcrumbs.jsx     # Breadcrumb navigation
    │
    ├── /puck-overrides/        # Puck component overrides
    │   ├── Hero.jsx            # Custom Hero component
    │   ├── Card.jsx            # Custom Card styling
    │   └── puckConfig.js       # Extended Puck config
    │
    ├── /styles/                # Theme stylesheets
    │   ├── theme.css           # Main theme CSS
    │   ├── variables.css       # CSS custom properties
    │   ├── components.css      # Component styles
    │   └── dark-mode.css       # Dark mode styles
    │
    ├── /hooks/                 # Custom React hooks
    │   └── useThemeSettings.js
    │
    └── /assets/                # Static assets
        ├── /images/
        ├── /fonts/
        └── /icons/
```

### File Descriptions

| File | Purpose | Required |
|------|---------|----------|
| `theme.json` | Theme metadata and settings schema | Yes |
| `index.jsx` | Entry point, exports, activate/deactivate | Yes |
| `screenshot.png` | Theme preview image | Recommended |
| `README.md` | Documentation for theme users | Recommended |
| `layouts/*.jsx` | Page layout components | Optional |
| `components/*.jsx` | UI components | Optional |
| `puck-overrides/*.jsx` | Puck component customizations | Optional |
| `styles/*.css` | Theme stylesheets | Recommended |

---

## 5. Theme Manifest (theme.json)

### Complete Schema

```json
{
  "name": "Professional Theme",
  "slug": "professional-theme",
  "version": "1.0.0",
  "description": "A clean, professional theme for educational platforms",
  "author": "Theme Developer",
  "authorUri": "https://developer-website.com",
  "themeUri": "https://github.com/developer/professional-theme",
  "license": "GPL-2.0-or-later",
  "entryPoint": "index.jsx",
  "screenshot": "screenshot.png",

  "requires": {
    "lmsVersion": "1.0.0",
    "nodeVersion": "18.0.0"
  },

  "supports": [
    "custom-colors",
    "custom-logo",
    "custom-header",
    "custom-footer",
    "dark-mode",
    "puck-editor",
    "responsive",
    "accessibility"
  ],

  "themeSettings": {
    "colors": {
      "primary": {
        "label": "Primary Brand Color",
        "default": "#4F46E5",
        "type": "color",
        "description": "Main brand color used throughout the site"
      },
      "secondary": {
        "label": "Secondary Color",
        "default": "#d946ef",
        "type": "color"
      },
      "accent": {
        "label": "Accent Color",
        "default": "#f59e0b",
        "type": "color"
      },
      "background": {
        "label": "Background Color",
        "default": "#ffffff",
        "type": "color"
      },
      "text": {
        "label": "Text Color",
        "default": "#1f2937",
        "type": "color"
      }
    },
    "typography": {
      "fontFamily": {
        "label": "Body Font",
        "default": "Inter",
        "type": "select",
        "options": ["Inter", "Poppins", "Open Sans", "Roboto", "Lato"]
      },
      "headingFontFamily": {
        "label": "Heading Font",
        "default": "Poppins",
        "type": "select",
        "options": ["Poppins", "Playfair Display", "Montserrat", "Oswald"]
      },
      "baseFontSize": {
        "label": "Base Font Size",
        "default": "16px",
        "type": "select",
        "options": ["14px", "15px", "16px", "17px", "18px"]
      }
    },
    "layout": {
      "containerWidth": {
        "label": "Max Container Width",
        "default": "1280px",
        "type": "select",
        "options": ["1024px", "1152px", "1280px", "1440px", "full"]
      },
      "headerStyle": {
        "label": "Header Style",
        "default": "standard",
        "type": "select",
        "options": ["standard", "centered", "minimal", "transparent"]
      },
      "footerColumns": {
        "label": "Footer Columns",
        "default": 4,
        "type": "select",
        "options": [2, 3, 4]
      }
    }
  },

  "templates": {
    "home": {
      "label": "Home Page",
      "description": "Landing page with hero and features"
    },
    "page": {
      "label": "Default Page",
      "description": "Standard content page"
    },
    "blog": {
      "label": "Blog Post",
      "description": "Single blog post layout"
    },
    "course": {
      "label": "Course Detail",
      "description": "Course information page"
    },
    "archive": {
      "label": "Archive",
      "description": "List of posts or courses"
    }
  },

  "puckComponents": [
    "Hero",
    "FeaturesGrid",
    "Testimonial",
    "CallToAction",
    "CourseGrid"
  ],

  "dependencies": []
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Human-readable theme name |
| `slug` | string | Yes | URL-safe unique identifier |
| `version` | string | Yes | Semantic version (e.g., "1.0.0") |
| `description` | string | No | Brief description |
| `author` | string | No | Developer name |
| `entryPoint` | string | Yes | Main JSX file |
| `supports` | array | No | Supported features |
| `themeSettings` | object | No | Customizable settings schema |
| `templates` | object | No | Available page templates |
| `puckComponents` | array | No | Puck components this theme provides |

---

## 6. Theme Hooks System

Themes can use the same hooks system as plugins to modify behavior:

### Registering Hooks in Theme

```javascript
// In theme's index.jsx or functions.js

export async function activate({ hooks, config, themeId }) {

  // Filter: Modify primary color
  hooks.addFilter('theme.colors', (colors) => {
    return {
      ...colors,
      primary: config.colors?.primary || colors.primary
    };
  }, 10, 1, themeId);

  // Filter: Modify Puck component
  hooks.addFilter('puck.component.Hero', (componentConfig) => {
    return {
      ...componentConfig,
      defaultProps: {
        ...componentConfig.defaultProps,
        height: 'large'  // Theme prefers large heroes
      }
    };
  }, 10, 1, themeId);

  // Action: Theme activated
  hooks.doAction('theme.activated', themeId);
}
```

### Available Theme Hooks

#### Filters

| Hook Name | Value | Description |
|-----------|-------|-------------|
| `theme.colors` | `{primary, secondary, ...}` | Modify color palette |
| `theme.typography` | `{fontFamily, ...}` | Modify typography settings |
| `theme.layout` | `{containerWidth, ...}` | Modify layout settings |
| `puck.component.{Name}` | Component config | Modify Puck component |
| `puck.config` | Full Puck config | Modify entire Puck config |

#### Actions

| Hook Name | Arguments | Description |
|-----------|-----------|-------------|
| `theme.activated` | `themeId` | Theme was activated |
| `theme.deactivated` | `themeId` | Theme was deactivated |
| `theme.settings.saved` | `{themeId, settings}` | Settings were saved |

---

## 7. Styling with Tailwind CSS

### CSS Custom Properties

Themes should use CSS custom properties for dynamic styling:

```css
/* styles/variables.css */

:root {
  /* Colors - These can be overridden via ThemeCustomizer */
  --color-primary: #4F46E5;
  --color-primary-50: #eef2ff;
  --color-primary-100: #e0e7ff;
  --color-primary-200: #c7d2fe;
  --color-primary-500: #6366f1;
  --color-primary-600: #4f46e5;
  --color-primary-700: #4338ca;
  --color-primary-900: #312e81;

  --color-secondary: #d946ef;
  --color-accent: #f59e0b;

  /* Typography */
  --font-family-body: 'Inter', sans-serif;
  --font-family-heading: 'Poppins', sans-serif;
  --font-size-base: 16px;

  /* Layout */
  --container-max-width: 1280px;
  --header-height: 64px;
  --sidebar-width: 280px;

  /* Spacing */
  --spacing-section: 4rem;
  --spacing-content: 2rem;
}

/* Dark mode */
[data-theme="dark"] {
  --color-background: #111827;
  --color-text: #f9fafb;
  --color-card-bg: #1f2937;
}
```

### Tailwind Configuration

Themes can extend the Tailwind configuration:

```javascript
// tailwind.theme.config.js

export default {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'var(--color-primary)',
          50: 'var(--color-primary-50)',
          // ... all shades
        }
      },
      fontFamily: {
        body: ['var(--font-family-body)', 'sans-serif'],
        heading: ['var(--font-family-heading)', 'sans-serif'],
      },
      maxWidth: {
        container: 'var(--container-max-width)',
      }
    }
  }
}
```

### Component Styling

```jsx
// components/Button.jsx

const Button = ({ variant = 'primary', size = 'md', children, ...props }) => {
  const variants = {
    primary: 'bg-primary-600 hover:bg-primary-700 text-white',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800',
    outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50'
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  return (
    <button
      className={`rounded-lg font-medium transition-colors ${variants[variant]} ${sizes[size]}`}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;
```

---

## 8. Puck Editor Integration

### Overriding Puck Components

Themes can provide custom versions of Puck components:

```jsx
// puck-overrides/Hero.jsx

const ThemeHero = ({
  title,
  subtitle,
  backgroundImage,
  height = 'large',
  overlay = true
}) => {
  const heightClasses = {
    small: 'h-64',
    medium: 'h-96',
    large: 'h-[600px]',
    full: 'h-screen'
  };

  return (
    <section
      className={`relative ${heightClasses[height]} flex items-center justify-center`}
      style={{
        backgroundImage: backgroundImage ? `url(${backgroundImage})` : undefined,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}
    >
      {overlay && (
        <div className="absolute inset-0 bg-gradient-to-b from-primary-900/70 to-primary-600/50" />
      )}
      <div className="relative z-10 text-center text-white max-w-4xl mx-auto px-4">
        <h1 className="text-4xl md:text-6xl font-heading font-bold mb-4">
          {title}
        </h1>
        {subtitle && (
          <p className="text-xl md:text-2xl text-white/90">
            {subtitle}
          </p>
        )}
      </div>
    </section>
  );
};

export default ThemeHero;
```

### Theme Puck Configuration

```javascript
// puck-overrides/puckConfig.js

import ThemeHero from './Hero';
import ThemeCard from './Card';

export const themePuckConfig = {
  components: {
    // Override Hero with theme version
    Hero: {
      render: ThemeHero,
      fields: {
        title: { type: 'text', label: 'Title' },
        subtitle: { type: 'text', label: 'Subtitle' },
        backgroundImage: { type: 'custom', label: 'Background', render: ImageField },
        height: {
          type: 'select',
          label: 'Height',
          options: [
            { value: 'small', label: 'Small' },
            { value: 'medium', label: 'Medium' },
            { value: 'large', label: 'Large (Theme Default)' },
            { value: 'full', label: 'Full Screen' }
          ]
        },
        overlay: {
          type: 'radio',
          label: 'Show Overlay',
          options: [
            { value: true, label: 'Yes' },
            { value: false, label: 'No' }
          ]
        }
      },
      defaultProps: {
        title: 'Welcome',
        subtitle: '',
        height: 'large',
        overlay: true
      }
    },

    // Add theme-specific component
    ThemeCard: {
      render: ThemeCard,
      fields: { /* ... */ },
      defaultProps: { /* ... */ }
    }
  }
};
```

---

## 9. Database Schema

### Themes Table

```sql
CREATE TABLE IF NOT EXISTS themes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug VARCHAR(100) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  version VARCHAR(20) NOT NULL,
  description TEXT,
  author VARCHAR(255),
  author_uri VARCHAR(500),
  screenshot_url VARCHAR(500),

  -- Status
  enabled BOOLEAN DEFAULT FALSE,
  active BOOLEAN DEFAULT FALSE,

  -- Metadata
  manifest JSONB NOT NULL,
  entry_point VARCHAR(255) DEFAULT 'index.jsx',

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  activated_at TIMESTAMPTZ
);
```

### Theme Settings Table

```sql
CREATE TABLE IF NOT EXISTS theme_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  theme_id UUID NOT NULL REFERENCES themes(id) ON DELETE CASCADE,
  setting_key VARCHAR(100) NOT NULL,
  setting_value JSONB,
  setting_type VARCHAR(50),

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(theme_id, setting_key)
);
```

---

## 10. Admin Interface

### Theme Manager Page

Navigate to: **Admin Panel > Appearance > Themes** (`/admin/themes`)

Features:
- View all installed themes
- See theme previews (screenshots)
- Activate/deactivate themes
- Access theme customizer
- Upload new themes (ZIP)
- Delete themes

### Theme Customizer

Navigate to: **Admin Panel > Appearance > Customize** (`/admin/theme-customizer`)

Features:
- Live preview of changes
- Color picker for brand colors
- Typography selection
- Layout options
- Export/import settings

---

## 11. Complete Example Theme

### Professional Theme

A complete theme example showing all features:

**theme.json:**
```json
{
  "name": "Professional",
  "slug": "professional",
  "version": "1.0.0",
  "description": "Clean, professional theme for educational platforms",
  "author": "MERN LMS Team",
  "entryPoint": "index.jsx",
  "supports": ["custom-colors", "dark-mode", "puck-editor"],
  "themeSettings": {
    "colors": {
      "primary": { "label": "Primary", "default": "#2563eb", "type": "color" },
      "secondary": { "label": "Secondary", "default": "#7c3aed", "type": "color" }
    },
    "layout": {
      "headerStyle": {
        "label": "Header Style",
        "default": "standard",
        "type": "select",
        "options": ["standard", "centered", "minimal"]
      }
    }
  }
}
```

**index.jsx:**
```jsx
import './styles/theme.css';

export const themeMeta = {
  name: 'Professional',
  slug: 'professional',
  version: '1.0.0'
};

// Layouts
export { default as DefaultLayout } from './layouts/DefaultLayout';
export { default as HomeLayout } from './layouts/HomeLayout';

// Components
export { default as Header } from './components/Header';
export { default as Footer } from './components/Footer';

// Puck overrides
export { themePuckConfig } from './puck-overrides/puckConfig';

// Lifecycle
export async function activate({ hooks, config, themeId }) {
  console.log('[Professional Theme] Activated');

  // Apply theme colors
  hooks.addFilter('theme.colors', (colors) => ({
    ...colors,
    primary: config.colors?.primary || '#2563eb',
    secondary: config.colors?.secondary || '#7c3aed'
  }), 10, 1, themeId);
}

export async function deactivate({ hooks, themeId }) {
  console.log('[Professional Theme] Deactivated');
}
```

---

## 12. API Reference

### Theme Management Endpoints

**Base URL:** `/api/themes`
**Authentication:** Admin required for most endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/themes` | List all themes |
| GET | `/api/themes/:slug` | Get theme details |
| GET | `/api/themes/active` | Get active theme |
| POST | `/api/themes/:slug/activate` | Activate theme |
| POST | `/api/themes/:slug/deactivate` | Deactivate theme |
| GET | `/api/themes/:slug/settings` | Get theme settings |
| PUT | `/api/themes/:slug/settings` | Update theme settings |
| POST | `/api/themes/upload` | Upload theme (ZIP) |
| DELETE | `/api/themes/:slug` | Remove theme |

### Example API Calls

**List Themes:**
```bash
curl -X GET http://localhost:5000/api/themes \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Activate Theme:**
```bash
curl -X POST http://localhost:5000/api/themes/professional/activate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Update Settings:**
```bash
curl -X PUT http://localhost:5000/api/themes/professional/settings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "colors": {
      "primary": "#2563eb"
    },
    "layout": {
      "headerStyle": "centered"
    }
  }'
```

---

## 13. Best Practices

### CRITICAL: Theme Component Compatibility Layer

> **⚠️ THIS IS THE #1 CAUSE OF PRODUCTION BUILD FAILURES**

Theme components live in `/themes/` folder, which is **OUTSIDE** the client workspace. Vite/Rollup **CANNOT resolve npm packages or path aliases** for files outside the workspace during production build.

#### Forbidden Imports (Will Break Production Build)

```jsx
// ❌ ALL OF THESE WILL CAUSE BUILD FAILURES
import { Link, useNavigate, useLocation } from 'react-router-dom';  // ❌ FAILS
import { useDispatch, useSelector } from 'react-redux';  // ❌ FAILS
import { logout } from '@/store/slices/authSlice';  // ❌ FAILS - path alias
import { useTheme } from '@/context/ThemeContext';  // ❌ FAILS - path alias
import axios from 'axios';  // ❌ FAILS
```

**Build Error:**
```
[rollup] Could not resolve "react-router-dom" from "themes/my-theme/components/layout/Header.jsx"
```

#### Required: Theme Compatibility Layer Pattern

Every theme component MUST include this compatibility layer at the top:

```jsx
import React, { useState, useEffect } from 'react';  // ✅ React is aliased

/**
 * THEME COMPATIBILITY LAYER
 * Theme files CANNOT import npm packages or use path aliases (@/)
 */

// ✅ Local Link component (replaces react-router-dom Link)
const Link = ({ to, children, className, style, onClick }) => (
    <a href={to} className={className} style={style} onClick={onClick}>{children}</a>
);

// ✅ Navigation hooks using browser APIs
const useNavigate = () => (path) => { window.location.href = path; };
const useLocation = () => ({ pathname: window.location.pathname });

// ✅ Auth state from window global (set by main app)
const useAuth = () => {
    const [auth, setAuth] = useState({ isAuthenticated: false, user: null });
    useEffect(() => {
        const checkAuth = () => {
            if (window.__LMS_AUTH__) {
                setAuth(window.__LMS_AUTH__);
            } else {
                const token = localStorage.getItem('token');
                const user = localStorage.getItem('user');
                setAuth({
                    isAuthenticated: !!token,
                    user: user ? JSON.parse(user) : null
                });
            }
        };
        checkAuth();
        window.addEventListener('auth-change', checkAuth);
        return () => window.removeEventListener('auth-change', checkAuth);
    }, []);
    return auth;
};

// ✅ Theme settings from window global
const useThemeSettings = () => {
    const [settings, setSettings] = useState({});
    useEffect(() => {
        if (window.__LMS_THEME_SETTINGS__) {
            setSettings(window.__LMS_THEME_SETTINGS__);
        }
    }, []);
    return { settings };
};

// ✅ Logout using fetch (not axios + redux dispatch)
const performLogout = async () => {
    try { await fetch('/api/auth/logout', { method: 'POST' }); } catch (e) {}
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
};
```

#### API Calls: Use fetch(), Not axios

```jsx
// ❌ WRONG - axios import will fail
import axios from 'axios';
const { data } = await axios.get('/api/menus');

// ✅ CORRECT - use native fetch
const response = await fetch('/api/menus?location=header');
const data = await response.json();
```

#### Reference Implementation

See `themes/celestial/components/layout/Header.jsx` for the complete working pattern.

---

### Tailwind Content Configuration (CRITICAL)

Theme files live in `/themes/` folder, which is **outside** the default Tailwind scan path. You MUST add themes to `tailwind.config.js`:

```javascript
// client/tailwind.config.js
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,css}",
    "../themes/**/*.{js,jsx,ts,tsx}",  // ✅ CRITICAL - without this, theme classes get purged!
  ],
  // ...
};
```

**Without this:** Classes like `lg:hidden`, `md:flex`, etc. used in theme components will be **purged** in production builds, causing responsive layouts to break.

---

### Mobile Sidebar Responsiveness (CRITICAL)

When creating mobile slide-out sidebars, **ALL three elements must have `lg:hidden`**:

1. **Toggle button** - The hamburger menu button
2. **Sidebar panel** - The slide-out navigation drawer
3. **Backdrop overlay** - The dark overlay behind the sidebar

**WRONG (shows on desktop too):**
```jsx
{/* ❌ Missing lg:hidden - sidebar shows on desktop */}
<button onClick={() => setSidebarOpen(!sidebarOpen)}>Menu</button>

<div className={`fixed right-0 ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'}`}>
  {/* sidebar */}
</div>

{sidebarOpen && <div className="fixed inset-0" onClick={close} />}
```

**CORRECT:**
```jsx
{/* ✅ All three have lg:hidden */}
<button className="lg:hidden" onClick={() => setSidebarOpen(!sidebarOpen)}>Menu</button>

<div className={`lg:hidden fixed right-0 ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'}`}>
  {/* sidebar */}
</div>

{sidebarOpen && <div className="lg:hidden fixed inset-0" onClick={close} />}
```

**Why:** Desktop has horizontal navigation - mobile sidebar would duplicate it.

---

### Design Principles

1. **Mobile First** - Design for mobile, then enhance for desktop
2. **Accessibility** - Use semantic HTML, proper contrast, keyboard navigation
3. **Performance** - Minimize CSS, lazy load images, optimize fonts
4. **Consistency** - Use design tokens (CSS variables) throughout

### Code Organization

**DO:**
```jsx
// Separate concerns into modules
import { useThemeSettings } from '../hooks/useThemeSettings';
import { applyColorVariables } from '../utils/colors';

export function ThemeProvider({ children }) {
  const settings = useThemeSettings();
  // Clean, organized code
}
```

**DON'T:**
```jsx
// Avoid monolithic components with inline everything
export function ThemeProvider({ children }) {
  // 500 lines of mixed logic...
}
```

### CSS Best Practices

**DO:**
```css
/* Use CSS custom properties for theming */
.button {
  background-color: var(--color-primary);
  color: var(--color-primary-contrast);
}

/* Dark mode using data attribute */
[data-theme="dark"] .button {
  background-color: var(--color-primary-dark);
}
```

**DON'T:**
```css
/* Avoid hardcoded colors */
.button {
  background-color: #4F46E5; /* Hard to customize */
}
```

### CSS Cascade Layers & Tailwind v4 (CRITICAL)

**IMPORTANT:** This platform uses Tailwind CSS v4 with `@layer` directives. Theme CSS is loaded as external stylesheets (unlayered), which means **unlayered CSS has HIGHER precedence than Tailwind's layered utilities**, regardless of specificity.

**DO:**
```css
/* Safe universal selector - only box-sizing */
* {
  box-sizing: border-box;
}

/* Use specific selectors for theme styles */
.theme-my-theme .hero {
  background: var(--color-primary);
}
```

**DON'T:**
```css
/* ❌ NEVER use CSS resets in theme files */
* {
  margin: 0;      /* Breaks mx-auto, my-*, margin utilities */
  padding: 0;     /* Breaks px-*, py-*, padding utilities */
  box-sizing: border-box;
}

/* This unlayered CSS BEATS Tailwind's .mx-auto even though
   .mx-auto has higher specificity than * */
```

**Why This Matters:**
- Tailwind's `mx-auto` class is in `@layer utilities`
- Your theme's `* { margin: 0 }` is unlayered
- CSS Cascade Layers: unlayered > layered (regardless of specificity)
- Result: Content won't center, padding/margin utilities ignored

**Rule:** Let Tailwind's Preflight handle CSS resets. Only style specific elements in your theme CSS.

### Hooks Usage

**DO:**
```javascript
// Always include themeId for cleanup
hooks.addFilter('theme.colors', callback, 10, 1, themeId);
```

**DON'T:**
```javascript
// Missing themeId prevents cleanup
hooks.addFilter('theme.colors', callback);
```

---

## 14. Troubleshooting

### Theme Not Loading

**Symptoms:** Theme doesn't appear in admin

**Checklist:**
1. Verify `theme.json` is valid JSON
2. Check `slug` matches directory name
3. Verify `entryPoint` file exists
4. Check browser console for import errors
5. Restart development server

### Styles Not Applying

**Symptoms:** CSS changes have no effect

**Checklist:**
1. Verify CSS file is imported in `index.jsx`
2. Check CSS selector specificity
3. Verify CSS custom properties are defined
4. Clear browser cache
5. Check for Tailwind purge issues

### Puck Components Not Overriding

**Symptoms:** Default components show instead of theme versions

**Checklist:**
1. Verify `themePuckConfig` is exported from `index.jsx`
2. Check component name matches exactly
3. Verify component renders without errors
4. Check theme is activated (not just enabled)

### Common Errors

**Error: "Theme manifest not found"**
```
Solution: Ensure theme.json exists in theme root directory
```

**Error: "Invalid theme entry point"**
```
Solution: Check entryPoint in theme.json matches actual file
```

**Error: "Failed to load theme module"**
```
Solution: Check for syntax errors in index.jsx
Run: node --check client/src/themes/my-theme/index.jsx
```

### Tailwind Utilities Not Working (mx-auto, px-*, py-*)

**Symptoms:**
- Content appears left-aligned despite `mx-auto` class
- Padding/margin utilities have no effect
- Computed styles show `margin: 0px` instead of `auto`

**Cause:** Theme CSS uses universal selector reset that conflicts with Tailwind v4's CSS Layers.

**Diagnosis:**
1. Open browser DevTools
2. Select an element with `mx-auto` class
3. Check Computed tab for `margin-left` value
4. If it shows `0px` instead of `auto`, you have a CSS conflict

**Solution:**
Search your theme's CSS files for:
```css
* {
  margin: 0;
  padding: 0;
}
```

Change to:
```css
* {
  box-sizing: border-box;
  /* Remove margin: 0 and padding: 0 */
}
```

**Explanation:** Tailwind v4 uses `@layer utilities` for classes like `mx-auto`. External theme CSS is unlayered, giving it higher cascade precedence regardless of specificity. See "CSS Cascade Layers & Tailwind v4" in Best Practices.

---

## 15. Appendix: Implementation Roadmap

### Current State (January 2026)

The system currently has:
- Basic ThemeContext with color customization
- ThemeCustomizer admin page
- CSS custom properties for primary color
- Static theme configuration

### Phase 1: Foundation

- [ ] Create ThemeManager class
- [ ] Database schema for themes
- [ ] Theme manifest validation
- [ ] Basic theme loading

### Phase 2: Core Features

- [ ] Theme activation/deactivation
- [ ] ThemeContext enhancement
- [ ] Theme settings persistence
- [ ] Admin UI for theme management

### Phase 3: Advanced Features

- [ ] Puck component override system
- [ ] Theme hooks registration
- [ ] Live preview in customizer
- [ ] Theme import/export

### Phase 4: Developer Experience

- [ ] Theme scaffold generator
- [ ] Documentation completion
- [ ] Example themes
- [ ] Theme marketplace preparation

---

## 16. Appendix: Theme Creation Template

Use this template as a starting point for creating a complete theme ZIP file. This section provides all the files you need with proper structure.

### Complete Theme ZIP Structure

```
my-theme/
├── theme.json              # Required: Theme manifest
├── preview.png             # Recommended: 400x300 preview image
├── styles/
│   └── theme.css           # Custom CSS (Tailwind v4 compatible)
├── components/
│   └── index.js            # React component exports
├── templates/              # Optional: Puck page templates
│   └── home.json
└── README.md               # Theme documentation
```

### CRITICAL: theme.json Requirements for AI Agents

**READ THIS SECTION CAREFULLY.** These requirements are mandatory for theme installation to succeed.

#### Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | **YES** | Lowercase slug with hyphens (e.g., `"my-theme"`) |
| `displayName` | string | **YES** | Human-readable name (e.g., `"My Theme"`) |
| `version` | string | **YES** | Semantic version (e.g., `"1.0.0"`) |
| `description` | string | **YES** | Brief description of the theme |
| `colors` | object | **YES** | Color palette (see format below) |

#### Colors Object Format - CRITICAL

**The `colors` object MUST be at the ROOT level of theme.json, NOT nested under other keys.**

✅ **CORRECT FORMAT:**
```json
{
  "name": "my-theme",
  "colors": {
    "primary": "#4F46E5",
    "secondary": "#10B981",
    "accent": "#F59E0B",
    "background": "#FFFFFF",
    "surface": "#F9FAFB",
    "text": "#1F2937",
    "muted": "#6B7280",
    "border": "#E5E7EB"
  }
}
```

❌ **WRONG - Nested under themeSettings:**
```json
{
  "themeSettings": {
    "colors": { ... }
  }
}
```

❌ **WRONG - Complex objects instead of hex strings:**
```json
{
  "colors": {
    "primary": { "label": "Primary", "default": "#4F46E5", "type": "color" }
  }
}
```

❌ **WRONG - Missing required color keys:**
```json
{
  "colors": {
    "primary": "#4F46E5",
    "secondary": "#10B981"
  }
}
```

#### All Required Color Keys

Every theme MUST define ALL of these color keys with hex values:

| Key | Purpose | Example |
|-----|---------|---------|
| `primary` | Main brand color, buttons, links | `"#4F46E5"` |
| `secondary` | Secondary actions, accents | `"#10B981"` |
| `accent` | Highlights, CTAs, warnings | `"#F59E0B"` |
| `background` | Page background | `"#FFFFFF"` |
| `surface` | Cards, modals, panels | `"#F9FAFB"` |
| `text` | Primary text color | `"#1F2937"` |
| `muted` | Secondary/dimmed text | `"#6B7280"` |
| `border` | Borders, dividers | `"#E5E7EB"` |

#### Fields NOT to Include

Do NOT include these fields (they are not used by this system):

- `entryPoint` - Not used
- `screenshot` - Use `preview.thumbnail` instead
- `supports` array - Use `features` object instead
- `themeSettings` - Use flat structure instead

#### preview.png Requirements

- **Size:** 400x300 pixels (landscape orientation)
- **Format:** PNG or JPG
- **Content:** Must be a real screenshot, NOT a 1x1 placeholder
- **Location:** Root of theme folder

### theme.json Template

```json
{
  "name": "my-theme",
  "displayName": "My Custom Theme",
  "slug": "my-theme",
  "version": "1.0.0",
  "description": "A professional theme for the MERN Community LMS",
  "author": "Your Name",
  "authorUrl": "https://yourwebsite.com",
  "license": "MIT",
  "category": "Professional",
  "tags": ["education", "professional", "modern"],

  "preview": {
    "thumbnail": "/themes/my-theme/preview.png"
  },

  "colors": {
    "primary": "#4F46E5",
    "secondary": "#10B981",
    "accent": "#F59E0B",
    "background": "#FFFFFF",
    "surface": "#F9FAFB",
    "text": "#1F2937",
    "muted": "#6B7280",
    "border": "#E5E7EB"
  },

  "typography": {
    "headingFont": "Inter, system-ui, sans-serif",
    "bodyFont": "Inter, system-ui, sans-serif",
    "baseFontSize": "16px"
  },

  "layout": {
    "maxWidth": "1280px",
    "headerStyle": "default",
    "stickyHeader": true
  },

  "components": {
    "cardRadius": "8px",
    "buttonRadius": "8px"
  },

  "features": {
    "customizer": true,
    "darkMode": false,
    "componentOverrides": true
  },

  "stylesheets": [
    "styles/theme.css"
  ]
}
```

### CRITICAL: theme.css Requirements for AI Agents

**This platform uses Tailwind CSS v4. Theme CSS MUST follow these rules or layouts will break.**

#### The #1 Rule: NO CSS RESETS

✅ **CORRECT - Only box-sizing:**
```css
* {
  box-sizing: border-box;
}
```

❌ **WRONG - This BREAKS the entire layout:**
```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
```

**Why this matters:** Tailwind v4 uses CSS Cascade Layers (`@layer`). Theme CSS is unlayered and has HIGHER precedence than Tailwind utilities. If your theme sets `margin: 0` on `*`, it overrides Tailwind's `mx-auto` class, breaking all centering.

#### Forbidden Patterns

NEVER include any of these in theme CSS:

```css
/* ❌ FORBIDDEN - Breaks Tailwind utilities */
* { margin: 0; }
* { padding: 0; }
*::before, *::after { margin: 0; padding: 0; }
html, body { margin: 0; padding: 0; }

/* ❌ FORBIDDEN - CSS resets */
@import 'normalize.css';
@import 'reset.css';
```

#### Safe Patterns

These are safe to use:

```css
/* ✅ SAFE - box-sizing only */
* { box-sizing: border-box; }

/* ✅ SAFE - Scoped to theme class */
.theme-my-theme .hero { padding: 2rem; }

/* ✅ SAFE - Using CSS variables */
.btn-primary { background: var(--color-primary); }

/* ✅ SAFE - Google Fonts import */
@import url('https://fonts.googleapis.com/css2?family=Inter&display=swap');
```

### styles/theme.css Template

```css
/* ==========================================================================
   MY THEME - Custom Styles
   MERN Community LMS Theme
   ========================================================================== */

/* CRITICAL: DO NOT add margin:0 or padding:0 to universal selectors.
   It breaks Tailwind utilities. Tailwind's Preflight handles resets. */

* {
  box-sizing: border-box;
}

/* --------------------------------------------------------------------------
   CSS Custom Properties
   These integrate with the theme system's color variables
   -------------------------------------------------------------------------- */

:root {
  /* These are set dynamically by ThemeContext based on theme.json colors */
  /* You can reference them in your styles */
}

/* --------------------------------------------------------------------------
   Typography
   -------------------------------------------------------------------------- */

.theme-my-theme h1,
.theme-my-theme h2,
.theme-my-theme h3,
.theme-my-theme h4,
.theme-my-theme h5,
.theme-my-theme h6 {
  font-family: var(--font-heading, inherit);
  font-weight: 600;
  line-height: 1.2;
}

/* --------------------------------------------------------------------------
   Buttons
   -------------------------------------------------------------------------- */

.theme-my-theme .btn-primary {
  background-color: var(--color-primary);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-button, 8px);
  font-weight: 500;
  transition: all 0.2s ease;
}

.theme-my-theme .btn-primary:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

/* --------------------------------------------------------------------------
   Cards
   -------------------------------------------------------------------------- */

.theme-my-theme .card {
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-card, 8px);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* --------------------------------------------------------------------------
   Hero Section
   -------------------------------------------------------------------------- */

.theme-my-theme .hero-section {
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  color: white;
  padding: 4rem 2rem;
}

/* --------------------------------------------------------------------------
   Header Customization
   -------------------------------------------------------------------------- */

.theme-my-theme header {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

/* --------------------------------------------------------------------------
   Footer Customization
   -------------------------------------------------------------------------- */

.theme-my-theme footer {
  background: var(--color-text);
  color: var(--color-surface);
}

/* --------------------------------------------------------------------------
   Course Cards
   -------------------------------------------------------------------------- */

.theme-my-theme .course-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.theme-my-theme .course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

/* --------------------------------------------------------------------------
   Responsive Adjustments
   -------------------------------------------------------------------------- */

@media (max-width: 768px) {
  .theme-my-theme .hero-section {
    padding: 2rem 1rem;
  }
}
```

### components/index.js Template

```javascript
/**
 * Theme Component Overrides
 *
 * Export custom React components to override default platform components.
 * Component names must match the platform's expected component names.
 *
 * Available overrides:
 * - Header: Main navigation header
 * - Footer: Global footer
 * - Hero: Homepage hero section
 * - CourseCard: Course listing cards
 * - Button: Primary button component
 */

// Example: Custom Header component
// import CustomHeader from './Header.jsx';

// Example: Custom Footer component
// import CustomFooter from './Footer.jsx';

// Export components you want to override
export {
  // Header: CustomHeader,
  // Footer: CustomFooter,
};

// Default export for themes without component overrides
export default {};
```

### README.md Template

```markdown
# My Custom Theme

A professional theme for the MERN Community LMS platform.

## Installation

1. Download the theme ZIP file
2. Go to Admin > Settings > Themes
3. Click "Install Theme"
4. Upload the ZIP file
5. Click "Activate" on the installed theme

## Customization

### Colors

Edit `theme.json` to change the color scheme:

- `primary`: Main brand color (buttons, links, accents)
- `secondary`: Secondary actions and highlights
- `accent`: Special highlights and call-to-action elements
- `background`: Page background color
- `surface`: Card and component backgrounds
- `text`: Primary text color
- `muted`: Secondary text color
- `border`: Border and divider color

### Typography

Modify the `typography` section in `theme.json`:

- `headingFont`: Font for headings (h1-h6)
- `bodyFont`: Font for body text
- `baseFontSize`: Base font size (default: 16px)

### Custom CSS

Add custom styles to `styles/theme.css`. Use the CSS variables
for consistency with the theme system.

## Support

For support, please contact: your-email@example.com

## License

MIT License
```

### AI Agent Pre-Flight Checklist

**MANDATORY VERIFICATION** - Check EVERY item before generating a theme:

#### theme.json Validation

- [ ] `name` field exists (lowercase with hyphens: `"my-theme"`)
- [ ] `displayName` field exists (human-readable: `"My Theme"`)
- [ ] `version` field exists (semantic: `"1.0.0"`)
- [ ] `description` field exists (brief description)
- [ ] `colors` object is at ROOT level (NOT under `themeSettings`)
- [ ] `colors` contains ALL 8 required keys:
  - [ ] `primary` (hex string like `"#4F46E5"`)
  - [ ] `secondary` (hex string)
  - [ ] `accent` (hex string)
  - [ ] `background` (hex string)
  - [ ] `surface` (hex string)
  - [ ] `text` (hex string)
  - [ ] `muted` (hex string)
  - [ ] `border` (hex string)
- [ ] Color values are SIMPLE HEX STRINGS, not objects
- [ ] NO `themeSettings` key exists
- [ ] NO `entryPoint` key exists
- [ ] NO `screenshot` key exists (use `preview.thumbnail` instead)

#### theme.css Validation

- [ ] File contains `* { box-sizing: border-box; }` ONLY
- [ ] File does NOT contain `* { margin: 0; }`
- [ ] File does NOT contain `* { padding: 0; }`
- [ ] File does NOT contain `html, body { margin: 0; padding: 0; }`
- [ ] File does NOT import normalize.css or reset.css
- [ ] No universal selector (`*`) sets margin or padding

#### File Structure Validation

- [ ] Theme folder contains `theme.json` at root
- [ ] Theme folder contains `styles/theme.css`
- [ ] Theme folder contains `components/index.js`
- [ ] Theme folder contains `preview.png` (real image, not placeholder)
- [ ] NO `index.jsx` file (not used by this system)
- [ ] NO `screenshot.png` file (use `preview.png` instead)

#### preview.png Validation

- [ ] File is a real PNG/JPG image (not 1x1 placeholder)
- [ ] Dimensions are 400x300 pixels
- [ ] File size is > 1KB (placeholder files are typically < 100 bytes)

### CSS Variables Reference

Your theme CSS can use these CSS custom properties:

| Variable | Description |
|----------|-------------|
| `--color-primary` | Primary brand color |
| `--color-primary-50` to `--color-primary-950` | Primary color shades |
| `--color-secondary` | Secondary color |
| `--color-accent` | Accent color |
| `--color-background` | Page background |
| `--color-surface` | Card/component backgrounds |
| `--color-text` | Primary text color |
| `--color-muted` | Muted text color |
| `--color-border` | Border color |
| `--font-heading` | Heading font family |
| `--font-body` | Body font family |
| `--font-size-base` | Base font size |
| `--max-width` | Maximum content width |
| `--header-height` | Header height |
| `--radius-card` | Card border radius |
| `--radius-button` | Button border radius |

---

## Document Information

**Document:** MERN Community LMS Theme Developer Handbook
**Version:** 1.0.0
**Created:** January 11, 2026
**Author:** Claude AI Assistant
**Platform:** Node.js / Express / PostgreSQL / React / Vite / Tailwind CSS

**References:**
- [WordPress Theme Developer Handbook](https://developer.wordpress.org/themes/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Puck Editor Documentation](https://github.com/measuredco/puck)

---

*This document is designed for export to Word/PDF format for distribution to theme developers.*
