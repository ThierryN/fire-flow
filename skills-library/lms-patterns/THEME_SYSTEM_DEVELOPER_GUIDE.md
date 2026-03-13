# Church LMS Theme System Developer Guide

**Version:** 2.2
**Last Updated:** January 18, 2026
**Platform:** MERN Stack (Node.js / Express / PostgreSQL / React / Vite / Tailwind CSS v4)

---

## Document Information

This comprehensive guide is designed for developers who want to create custom themes for the MERN Community LMS platform. The theme system follows a WordPress-inspired architecture, allowing for complete visual transformation of your Church LMS installation.

**Target Audience:** Theme Developers, Frontend Developers, UI/UX Designers

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Architecture Overview](#2-architecture-overview)
3. [Getting Started](#3-getting-started)
4. [Theme File Structure](#4-theme-file-structure)
5. [Theme Manifest (theme.json)](#5-theme-manifest-themejson)
6. [Component Override System](#6-component-override-system)
7. [CSS Variables & Styling](#7-css-variables--styling)
8. [Puck Editor Integration](#8-puck-editor-integration)
9. [ThemeManager Service](#9-thememanager-service)
10. [ThemeContext Provider](#10-themecontext-provider)
11. [Admin Interface](#11-admin-interface)
12. [Complete Example: Celestial Theme](#12-complete-example-celestial-theme)
13. [API Reference](#13-api-reference)
14. [Best Practices](#14-best-practices)
15. [Troubleshooting](#15-troubleshooting)
16. [Critical Mistakes to Avoid](#16-critical-mistakes-to-avoid)
17. [CSS Architecture & Text Visibility Best Practices](#17-css-architecture--text-visibility-best-practices) **(NEW)**
18. [Appendix: Screenshots](#18-appendix-screenshots)

---

## 1. Introduction

### What is a Theme?

A theme is a self-contained package that controls the visual appearance and layout of the Church LMS. Unlike plugins which add functionality, themes focus on:

- **Visual Design** - Colors, typography, spacing, and overall aesthetics
- **Layout Structure** - Header, footer, sidebar, content arrangement
- **Component Styling** - How Puck visual builder components render
- **User Experience** - Responsive design, dark mode, accessibility

### WordPress-Style Architecture

Our theme system is inspired by WordPress's proven theme architecture:

| Concept | WordPress | Church LMS |
|---------|-----------|------------|
| Theme Manifest | `style.css` header | `theme.json` |
| Entry Point | `functions.php` | `components/index.js` |
| Templates | PHP templates | React/JSX components |
| Customizer | WP Customizer | ThemeCustomizer.jsx |
| Component Overrides | Template hierarchy | `componentOverrides` Map |
| CSS Loading | `wp_enqueue_style` | Dynamic `<link>` injection |

### Key Features

1. **Dynamic Component Overrides** - Replace Header, Footer, Hero without code changes
2. **Live Preview** - See customizations before saving
3. **CSS Variable System** - Comprehensive design token support
4. **Puck Integration** - Theme-specific visual builder components
5. **ZIP Installation** - Upload themes through admin interface

---

## 2. Architecture Overview

### System Components Diagram

```
+---------------------------------------------------------------------+
|                        Church LMS Client                             |
+---------------------------------------------------------------------+
|                                                                     |
|   +-----------------+    +-------------------+    +---------------+ |
|   | ThemeContext    |<---| ThemeManager      |----| Database      | |
|   | (React Context) |    | (Lifecycle Mgmt)  |    | (themes,      | |
|   +--------+--------+    +---------+---------+    | theme_settings)| |
|            |                       |              +---------------+ |
|            |          +------------+------------+                   |
|            |          |                         |                   |
|   +--------v--------+ |  +-----------------+    |                   |
|   | Puck Editor     | |  | Theme A         |    |                   |
|   | (uses theme     | |  | (celestial/)    |    |                   |
|   |  components)    | |  +-----------------+    |                   |
|   +-----------------+ |  +-----------------+    |                   |
|                       |  | Theme B         |    |                   |
|                       |  | (classic/)      |    |                   |
|                       |  +-----------------+    |                   |
|                       +-------------------------+                   |
|                           themes/ directory                         |
+---------------------------------------------------------------------+
```

### Theme Loading Flow

```
User Visits Page
       |
       v
+--------------------+
| ThemeContext       |
| (loads active      |
|  theme via API)    |
+---------+----------+
          |
          v
+--------------------+     +--------------------+
| ThemeManager       |---->| Dynamic Import     |
| loadTheme()        |     | import.meta.glob() |
+---------+----------+     +--------------------+
          |
          +---> Apply CSS Variables
          |
          +---> Register Component Overrides
          |
          +---> Load Puck Components
          |
          v
+--------------------+
| App Renders with   |
| Theme Components   |
+--------------------+
```

---

## 3. Getting Started

### Quick Start: Create Your First Theme

**Step 1: Create Theme Directory**

```bash
mkdir -p themes/my-first-theme
mkdir -p themes/my-first-theme/components
mkdir -p themes/my-first-theme/styles
```

**Step 2: Create theme.json**

```json
{
  "name": "My First Theme",
  "displayName": "My First Theme",
  "slug": "my-first-theme",
  "version": "1.0.0",
  "description": "A simple custom theme for learning",
  "author": "Your Name",
  "category": "Custom",
  "tags": ["custom", "starter"],

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
    "stickyHeader": true
  },

  "stylesheets": [
    "styles/theme.css"
  ],

  "features": {
    "customizer": true,
    "darkMode": true
  }
}
```

**Step 3: Create Component Index**

```javascript
// themes/my-first-theme/components/index.js

/**
 * My First Theme - Component Exports
 *
 * Export components here to override the default LMS components.
 */

// Uncomment when you have custom components:
// export { default as Header } from './Header';
// export { default as Footer } from './Footer';

// For now, export empty (inherits defaults)
export {};
```

**Step 4: Create Theme CSS**

```css
/* themes/my-first-theme/styles/theme.css */

/* Custom properties for this theme */
:root {
  --theme-custom-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.1);
  --theme-custom-gradient: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
}

/* Theme-specific styles */
.theme-my-first-theme .hero-section {
  background: var(--theme-custom-gradient);
}

.theme-my-first-theme .card {
  box-shadow: var(--theme-custom-shadow);
}
```

**Step 5: Activate Theme**

1. Navigate to **Admin Panel > Settings > Themes**
2. Find your theme in the theme gallery
3. Click "Activate"
4. The page will reload with the new theme

---

## 4. Theme File Structure

### Minimum Required Structure

```
themes/
└── my-theme/
    └── theme.json      # Required: Theme manifest
```

### Recommended Full Structure

```
themes/
└── my-theme/
    ├── theme.json              # Required: Theme manifest
    ├── README.md               # Documentation for theme users
    ├── preview.png             # Preview image (400x300px recommended)
    │
    ├── components/             # Component overrides
    │   ├── index.js            # Main export file
    │   ├── layout/
    │   │   ├── Header.jsx      # Custom header
    │   │   └── Footer.jsx      # Custom footer
    │   └── Hero.jsx            # Custom hero component
    │
    ├── puck/                   # Puck visual builder components
    │   └── index.jsx           # Puck component exports
    │
    ├── styles/                 # Theme stylesheets
    │   └── theme.css           # Main theme CSS
    │
    └── assets/                 # Static assets (optional)
        ├── images/
        ├── fonts/
        └── icons/
```

### Real Example: Celestial Theme Structure

```
themes/
└── celestial/
    ├── theme.json
    ├── README.md
    ├── components/
    │   ├── index.js
    │   ├── layout/
    │   │   ├── Header.jsx      # Luxurious header with gold accents
    │   │   └── Footer.jsx      # Elegant footer
    │   └── Hero.jsx            # Full-width hero variants
    ├── puck/
    │   └── index.jsx           # CelestialHero, CelestialCard, CelestialButton
    └── styles/
        └── theme.css           # Celestial styling with CSS variables
```

---

## 5. Theme Manifest (theme.json)

### Complete Schema Reference

```json
{
  "name": "Theme Display Name",
  "displayName": "Theme Display Name",
  "slug": "theme-slug",
  "version": "1.0.0",
  "description": "A brief description of your theme",
  "author": "Author Name",
  "category": "Category Name",
  "tags": ["tag1", "tag2"],

  "preview": {
    "thumbnail": "/themes/theme-slug/preview.png",
    "screenshots": [
      {
        "path": "/themes/theme-slug/screenshots/home.png",
        "title": "Home Page"
      }
    ]
  },

  "stylesheets": [
    "styles/theme.css"
  ],

  "components": {
    "overrides": ["Header", "Footer", "Hero"],
    "puck": ["CustomHero", "CustomCard", "CustomButton"]
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
    "headingFont": "'Playfair Display', Georgia, serif",
    "bodyFont": "'Source Sans Pro', Inter, system-ui, sans-serif",
    "baseFontSize": "16px"
  },

  "layout": {
    "maxWidth": "1280px",
    "headerStyle": "elegant",
    "stickyHeader": true,
    "headerTransparent": true,
    "sidebarNavigation": true
  },

  "settings": {
    "cardRadius": "16px",
    "buttonRadius": "10px"
  },

  "features": {
    "customizer": true,
    "darkMode": false
  }
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Theme name for internal use |
| `displayName` | string | No | Human-readable display name |
| `slug` | string | Yes | URL-safe unique identifier (must match folder name) |
| `version` | string | Yes | Semantic version (e.g., "1.0.0") |
| `description` | string | No | Brief description |
| `author` | string | No | Developer name |
| `category` | string | No | Theme category for filtering |
| `tags` | array | No | Keywords for search |
| `stylesheets` | array | No | CSS files to load (relative to theme folder) |
| `components.overrides` | array | No | List of components this theme overrides |
| `components.puck` | array | No | Puck components this theme provides |
| `colors` | object | Yes | Color palette |
| `typography` | object | No | Font settings |
| `layout` | object | No | Layout settings |
| `features` | object | No | Feature flags |

---

## 6. Component Override System

### How It Works

The ThemeManager maintains a `componentOverrides` Map that stores theme-specific component implementations. When the theme loads, it dynamically imports components from the theme's `components/index.js` file.

### Component Index File

```javascript
// themes/celestial/components/index.js

/**
 * Celestial Theme Component Exports
 *
 * This file exports all theme components for the ThemeManager to register.
 * Each component here can override the default LMS component.
 */

// Layout components
export { default as Header } from './layout/Header';
export { default as Footer } from './layout/Footer';

// Hero components
export {
    CelestialHeroFullWidth,
    CelestialHeroSplit,
    CelestialHeroMinimal,
    default as Hero
} from './Hero';
```

### Using Theme Components in Layouts

```jsx
// In MainLayout.jsx or any layout file
import { useTheme } from '@/context/ThemeContext';
import DefaultHeader from '@/components/layout/Header';

const MainLayout = ({ children }) => {
  const { getComponent } = useTheme();

  // Get theme Header or fall back to default
  const Header = getComponent('Header', DefaultHeader);

  return (
    <div>
      <Header />
      <main>{children}</main>
    </div>
  );
};
```

### ThemeManager Implementation

The ThemeManager uses Vite's `import.meta.glob` for dynamic imports:

```javascript
// From ThemeManager.js (simplified)

async loadThemeComponents(themeSlug) {
  try {
    // Dynamic import using Vite's glob pattern
    const modules = import.meta.glob('@themes/*/components/index.js');

    // Find matching module for this theme
    let matchedModule = null;
    for (const [path, loader] of Object.entries(modules)) {
      if (path.includes(`/${themeSlug}/components/index.js`)) {
        matchedModule = loader;
        break;
      }
    }

    if (matchedModule) {
      const componentModule = await matchedModule();

      // Register each exported component
      Object.entries(componentModule).forEach(([name, component]) => {
        if (name !== 'default') {
          this.componentOverrides.set(name, component);
          console.log(`[ThemeManager] Registered component override: ${name}`);
        }
      });
    }
  } catch (error) {
    console.log(`[ThemeManager] No component overrides for theme: ${themeSlug}`);
  }
}
```

### Creating a Theme Component

> **⚠️ CRITICAL:** Theme components CANNOT import npm packages or use path aliases (@/).
> See "Fatal Mistake #3" above for the required compatibility layer pattern.

```jsx
// themes/celestial/components/layout/Header.jsx

import React, { useState, useEffect } from 'react';

/**
 * THEME COMPATIBILITY LAYER - Required for all theme components
 * See Fatal Mistake #3 for full implementation
 */
const Link = ({ to, children, className, style, onClick }) => (
    <a href={to} className={className} style={style} onClick={onClick}>{children}</a>
);
const useNavigate = () => (path) => { window.location.href = path; };
const useLocation = () => ({ pathname: window.location.pathname });
const useAuth = () => { /* ... see Fatal Mistake #3 ... */ };
const useThemeSettings = () => { /* ... see Fatal Mistake #3 ... */ };
const performLogout = async () => { /* ... see Fatal Mistake #3 ... */ };

const CelestialHeader = () => {
  const [scrolled, setScrolled] = useState(false);
  const { isAuthenticated, user } = useAuth();  // ✅ Uses local hook
  const { settings } = useThemeSettings();       // ✅ Uses local hook

  // Theme-specific colors (can be moved to theme.json)
  const colors = {
    primary: '#1E1B4B',      // Deep midnight blue
    secondary: '#D4AF37',    // Rich gold
    accent: '#B8860B',       // Dark gold
    background: '#FDF8F0',   // Warm ivory
    surface: '#FFFEF5',      // Elegant cream
  };

  // Scroll effect - header becomes solid
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 w-full z-50 transition-all duration-500 ${
        scrolled ? 'shadow-lg' : ''
      }`}
      style={{
        backgroundColor: scrolled ? colors.primary : 'transparent',
        borderBottom: scrolled ? `1px solid ${colors.secondary}40` : 'none'
      }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <img
              src={settings.primary_logo || '/logo.png'}
              alt={settings.site_name}
              className="h-auto max-h-[70px] w-auto"
              style={{ filter: scrolled ? 'brightness(1.2)' : 'none' }}
            />
          </Link>

          {/* Navigation... */}
        </div>
      </div>
    </header>
  );
};

export default CelestialHeader;
```

---

## 7. CSS Variables & Styling

### Core CSS Variables

The ThemeManager applies the following CSS variables to `:root`:

#### Colors
```css
--color-primary        /* Primary brand color */
--color-primary-50     /* Lightest shade */
--color-primary-100
--color-primary-200
--color-primary-300
--color-primary-400
--color-primary-600
--color-primary-700
--color-primary-800
--color-primary-900
--color-primary-950    /* Darkest shade */

--color-secondary      /* Secondary color (same shade scale) */
--color-accent         /* Accent color */
--color-background     /* Page background */
--color-surface        /* Card/component backgrounds */
--color-text           /* Primary text */
--color-muted          /* Muted text */
--color-border         /* Border color */
```

#### Typography
```css
--font-heading         /* Heading font family */
--font-body            /* Body font family */
--font-size-base       /* Base font size */
```

#### Layout
```css
--max-width            /* Maximum container width */
--header-height        /* Header height */
--radius-card          /* Card border radius */
--radius-button        /* Button border radius */
```

### Theme CSS File Example

```css
/* themes/celestial/styles/theme.css */

/* ==============================================
   CELESTIAL THEME - CUSTOM PROPERTIES
   ============================================== */

:root {
  /* Theme-specific variables */
  --celestial-gold: #D4AF37;
  --celestial-midnight: #1E1B4B;
  --celestial-ivory: #FDF8F0;

  /* Custom shadows with gold tint */
  --celestial-shadow-sm: 0 1px 2px rgba(212, 175, 55, 0.1);
  --celestial-shadow-md: 0 4px 6px rgba(212, 175, 55, 0.15);
  --celestial-shadow-lg: 0 10px 15px rgba(212, 175, 55, 0.2);
}

/* ==============================================
   CELESTIAL THEME - GLOBAL STYLES
   ============================================== */

/* All theme styles should be scoped or use theme-specific classes */
body {
  font-family: var(--font-body);
  background-color: var(--color-background);
  color: var(--color-text);
}

/* Gold accent lines */
.celestial-accent-line {
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--celestial-gold),
    transparent
  );
}

/* ==============================================
   CELESTIAL THEME - COMPONENT STYLES
   ============================================== */

/* Buttons */
.btn-celestial {
  background: var(--celestial-gold);
  color: var(--celestial-midnight);
  border-radius: var(--radius-button);
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 600;
  padding: 0.75rem 1.5rem;
  transition: all 0.3s ease;
}

.btn-celestial:hover {
  transform: translateY(-2px);
  box-shadow: var(--celestial-shadow-lg);
}

/* Cards */
.card-celestial {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: var(--celestial-shadow-md);
}

/* Typography */
.heading-celestial {
  font-family: 'Playfair Display', Georgia, serif;
  color: var(--celestial-midnight);
}
```

### CSS Injection System

The ThemeContext automatically injects theme CSS files:

```javascript
// From ThemeContext.jsx (simplified)

const injectThemeStylesheet = useCallback((themeSlug, cssPath) => {
  const linkId = `theme-css-${themeSlug}-${cssPath.replace(/[^a-z0-9]/gi, '-')}`;

  // Check if already injected
  if (document.getElementById(linkId)) return;

  const link = document.createElement('link');
  link.id = linkId;
  link.rel = 'stylesheet';
  link.type = 'text/css';
  link.href = `/themes/${themeSlug}/${cssPath}`;
  link.setAttribute('data-theme', themeSlug);

  document.head.appendChild(link);
  console.log(`[ThemeContext] Injected stylesheet: ${link.href}`);
}, []);
```

---

## 8. Puck Editor Integration

### What is Puck?

Puck is a visual page builder that allows users to drag-and-drop components to build pages. Themes can provide custom Puck components with unique styling.

### Theme Puck Components

```jsx
// themes/celestial/puck/index.jsx

import React from 'react';

// ==============================================
// CELESTIAL HERO COMPONENT
// ==============================================

const CelestialHero = ({
  title = "Welcome",
  subtitle = "",
  backgroundImage,
  height = "large",
  showOverlay = true
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
      {showOverlay && (
        <div
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(135deg, rgba(30,27,75,0.85), rgba(30,27,75,0.6))'
          }}
        />
      )}
      <div className="relative z-10 text-center text-white max-w-4xl mx-auto px-4">
        <h1
          className="text-4xl md:text-6xl font-bold mb-4"
          style={{ fontFamily: "'Playfair Display', Georgia, serif" }}
        >
          {title}
        </h1>
        {subtitle && (
          <p
            className="text-xl md:text-2xl"
            style={{
              color: '#D4AF37',
              fontFamily: "'Source Sans Pro', sans-serif"
            }}
          >
            {subtitle}
          </p>
        )}
      </div>
    </section>
  );
};

// Puck configuration for CelestialHero
export const CelestialHeroConfig = {
  render: CelestialHero,
  label: "Celestial Hero",
  fields: {
    title: { type: 'text', label: 'Title' },
    subtitle: { type: 'text', label: 'Subtitle' },
    backgroundImage: {
      type: 'text',
      label: 'Background Image URL'
    },
    height: {
      type: 'select',
      label: 'Height',
      options: [
        { value: 'small', label: 'Small' },
        { value: 'medium', label: 'Medium' },
        { value: 'large', label: 'Large' },
        { value: 'full', label: 'Full Screen' }
      ]
    },
    showOverlay: {
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
    showOverlay: true
  }
};

// ==============================================
// CELESTIAL CARD COMPONENT
// ==============================================

const CelestialCard = ({ title, description, icon }) => (
  <div
    className="p-6 rounded-2xl border"
    style={{
      backgroundColor: '#FFFEF5',
      borderColor: '#E2D5BB',
      boxShadow: '0 4px 6px rgba(212, 175, 55, 0.1)'
    }}
  >
    {icon && (
      <div
        className="w-12 h-12 rounded-full flex items-center justify-center mb-4"
        style={{ backgroundColor: 'rgba(212, 175, 55, 0.1)' }}
      >
        <span style={{ color: '#D4AF37', fontSize: '1.5rem' }}>{icon}</span>
      </div>
    )}
    <h3
      className="text-xl font-semibold mb-2"
      style={{
        fontFamily: "'Playfair Display', serif",
        color: '#1E1B4B'
      }}
    >
      {title}
    </h3>
    <p style={{ color: '#64748B' }}>{description}</p>
  </div>
);

export const CelestialCardConfig = {
  render: CelestialCard,
  label: "Celestial Card",
  fields: {
    title: { type: 'text', label: 'Title' },
    description: { type: 'textarea', label: 'Description' },
    icon: { type: 'text', label: 'Icon (emoji or character)' }
  },
  defaultProps: {
    title: 'Card Title',
    description: 'Card description goes here.',
    icon: '✨'
  }
};

// ==============================================
// EXPORTS
// ==============================================

export { CelestialHero, CelestialCard };
```

### Loading Puck Components

The ThemeManager automatically loads Puck components:

```javascript
// From ThemeManager.js

async loadPuckComponents(themeSlug) {
  try {
    const modules = import.meta.glob('@themes/*/puck/index.jsx');

    let matchedModule = null;
    for (const [path, loader] of Object.entries(modules)) {
      if (path.includes(`/${themeSlug}/puck/index.jsx`)) {
        matchedModule = loader;
        break;
      }
    }

    if (matchedModule) {
      const puckModule = await matchedModule();

      Object.entries(puckModule).forEach(([name, config]) => {
        if (name !== 'default') {
          this.puckComponents.set(name, config);
          console.log(`[ThemeManager] Registered Puck component: ${name}`);
        }
      });
    }
  } catch (error) {
    console.log(`[ThemeManager] No Puck components for theme: ${themeSlug}`);
  }
}
```

---

## 9. ThemeManager Service

### Overview

The ThemeManager is a singleton service that handles:
- Loading and activating themes
- Component override registration
- Puck component integration
- CSS variable application
- Live preview functionality

### Key Methods

```javascript
class ThemeManager {
  // Load and activate a theme
  async loadTheme(themeSlug, themeData)

  // Get a component with potential theme override
  getComponent(name, defaultComponent)

  // Get all registered Puck components
  getPuckComponents()

  // Apply CSS variables to document root
  applyCSSVariables(settings)

  // Preview mode (for customizer)
  enterPreviewMode()
  exitPreviewMode()
  previewChange(key, value)

  // Subscribe to theme changes
  subscribe(callback)
}
```

### Color Variations

The ThemeManager automatically generates color shades:

```javascript
applyColorWithVariations(root, name, color) {
  root.style.setProperty(`--color-${name}`, color);

  // Lighter shades (50-400)
  root.style.setProperty(`--color-${name}-50`, this.lightenColor(color, 95));
  root.style.setProperty(`--color-${name}-100`, this.lightenColor(color, 85));
  root.style.setProperty(`--color-${name}-200`, this.lightenColor(color, 70));
  root.style.setProperty(`--color-${name}-300`, this.lightenColor(color, 50));
  root.style.setProperty(`--color-${name}-400`, this.lightenColor(color, 25));

  // Darker shades (600-950)
  root.style.setProperty(`--color-${name}-600`, this.darkenColor(color, 10));
  root.style.setProperty(`--color-${name}-700`, this.darkenColor(color, 25));
  root.style.setProperty(`--color-${name}-800`, this.darkenColor(color, 40));
  root.style.setProperty(`--color-${name}-900`, this.darkenColor(color, 55));
  root.style.setProperty(`--color-${name}-950`, this.darkenColor(color, 70));
}
```

---

## 10. ThemeContext Provider

### Overview

ThemeContext wraps the entire application and provides:
- Current theme data
- Component resolution via `getComponent()`
- Theme settings
- Dark mode toggle
- CSS stylesheet injection

### Usage

```jsx
// In any component
import { useTheme } from '@/context/ThemeContext';

const MyComponent = () => {
  const {
    theme,           // Current theme object
    settings,        // Legacy settings (branding, etc.)
    getComponent,    // Get theme component or default
    darkMode,        // Dark mode state
    toggleDarkMode,  // Toggle dark mode
    isLoading        // Loading state
  } = useTheme();

  // Get a themed component
  const Header = getComponent('Header', DefaultHeader);

  return <Header />;
};
```

### The getComponent Function

```jsx
// Returns theme component if available, otherwise default
const getComponent = useCallback((name, defaultComponent) => {
  return themeManager.getComponent(name, defaultComponent);
}, []);
```

---

## 11. Admin Interface

### Theme Manager Page

Navigate to: **Admin Panel > Settings > Themes**

Features:
- View all installed themes in a gallery
- See theme previews and descriptions
- Activate/deactivate themes
- Upload new themes (ZIP)
- Access theme customizer

### Theme Customizer

Navigate to: **Admin Panel > Settings > Theme Customizer**

Tabs:
1. **Branding** - Logo, site name, tagline
2. **Colors** - Primary, secondary, accent colors
3. **Typography** - Heading and body fonts

Features:
- Live preview of changes
- Color picker for brand colors
- Font selection dropdowns
- Save/Reset buttons

---

## 12. Complete Example: Celestial Theme

### theme.json

```json
{
  "name": "Celestial",
  "displayName": "Celestial Royal Theme",
  "slug": "celestial",
  "version": "2.0.0",
  "description": "A luxurious, regal theme with deep midnight blue and rich gold accents.",
  "author": "School of the Priests",
  "category": "Luxury",
  "tags": ["royal", "elegant", "gold", "luxury", "spiritual", "celestial"],

  "preview": {
    "thumbnail": "/themes/celestial/preview.png"
  },

  "stylesheets": [
    "styles/theme.css"
  ],

  "components": {
    "overrides": ["Header", "Footer", "Hero"],
    "puck": ["CelestialHero", "CelestialCard", "CelestialButton"]
  },

  "colors": {
    "primary": "#1E1B4B",
    "secondary": "#D4AF37",
    "accent": "#B8860B",
    "background": "#FDF8F0",
    "surface": "#FFFEF5",
    "text": "#1F1F2E",
    "muted": "#64748B",
    "border": "#E2D5BB"
  },

  "typography": {
    "headingFont": "'Playfair Display', Georgia, serif",
    "bodyFont": "'Source Sans Pro', Inter, system-ui, sans-serif",
    "baseFontSize": "16px"
  },

  "layout": {
    "maxWidth": "1280px",
    "headerStyle": "elegant",
    "stickyHeader": true,
    "headerTransparent": true,
    "sidebarNavigation": true
  },

  "settings": {
    "cardRadius": "16px",
    "buttonRadius": "10px"
  },

  "features": {
    "customizer": true,
    "darkMode": false
  }
}
```

### Design Characteristics

- **Color Palette:** Deep midnight blue (#1E1B4B) with rich gold (#D4AF37)
- **Typography:** Playfair Display for headings, Source Sans Pro for body
- **Background:** Warm ivory (#FDF8F0) creating an elegant canvas
- **Accents:** Gold borders, shadows, and decorative elements
- **Header:** Transparent on scroll, transitions to solid midnight blue
- **Sidebar:** Unique slide-out navigation panel

---

## 13. API Reference

### Theme Management Endpoints

**Base URL:** `/api/themes`

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

**Get Active Theme:**
```bash
curl -X GET http://localhost:5000/api/themes/active \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Activate Theme:**
```bash
curl -X POST http://localhost:5000/api/themes/celestial/activate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Update Settings:**
```bash
curl -X PUT http://localhost:5000/api/themes/celestial/settings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "colors": {
      "primary": "#2563eb"
    }
  }'
```

---

## 14. Best Practices

### Design Principles

1. **Use CSS Variables** - Always use `var(--color-primary)` instead of hardcoded colors
2. **Mobile First** - Design for mobile, then enhance for desktop
3. **Accessibility** - Ensure sufficient color contrast (WCAG 2.1 AA minimum)
4. **Performance** - Minimize CSS, optimize images, lazy load when possible
5. **Consistency** - Follow the design token system throughout

### Code Organization

**DO:**
```javascript
// Separate concerns into modules
export { default as Header } from './layout/Header';
export { default as Footer } from './layout/Footer';
```

**DON'T:**
```javascript
// Don't put all components in one file
export const Header = () => { /* 500 lines */ };
export const Footer = () => { /* 300 lines */ };
```

### CSS Best Practices

**DO:**
```css
/* Use CSS custom properties */
.button {
  background-color: var(--color-primary);
  border-radius: var(--radius-button);
}
```

**DON'T:**
```css
/* Avoid hardcoded values */
.button {
  background-color: #4F46E5;
  border-radius: 8px;
}
```

### File Naming

- Use kebab-case for folders: `my-theme/`
- Use PascalCase for React components: `Header.jsx`
- Use camelCase for JavaScript utilities: `themeUtils.js`
- Use lowercase for CSS files: `theme.css`

---

## 15. Troubleshooting

### Theme Not Loading

**Symptoms:** Theme doesn't appear in admin gallery

**Checklist:**
1. Verify `theme.json` is valid JSON (use a JSON validator)
2. Check `slug` matches directory name exactly
3. Ensure theme folder is in correct location (`themes/`)
4. Restart development server (`npm run dev`)
5. Check browser console for errors

### Styles Not Applying

**Symptoms:** CSS changes have no effect

**Checklist:**
1. Verify CSS file path in `theme.json` `stylesheets` array
2. Check that stylesheet is being injected (Network tab in DevTools)
3. Check CSS selector specificity
4. Clear browser cache
5. Check for Tailwind CSS purge issues in production

### Component Overrides Not Working

**Symptoms:** Default components show instead of theme versions

**Checklist:**
1. Verify `components/index.js` exports components correctly
2. Check component names match exactly (case-sensitive)
3. Look for import errors in browser console
4. Ensure theme is activated (not just enabled)
5. Check for JavaScript errors in component code

### HMR (Hot Module Replacement) Issues

**Known Issues:**
- CSS file changes may require manual page refresh
- New theme folders require Vite dev server restart
- Component changes should hot-reload automatically

### Common Errors

**"Theme manifest not found"**
```
Solution: Ensure theme.json exists in theme root directory
and contains valid JSON
```

**"Failed to load theme module"**
```
Solution: Check for syntax errors in components/index.js
Run: node --check themes/my-theme/components/index.js
```

**"CSS not loading (404)"**
```
Solution:
1. Check stylesheet path in theme.json
2. Ensure themes folder is served statically in production
3. Verify Vite alias configuration in vite.config.js
```

---

## 16. Critical Mistakes to Avoid

> **IMPORTANT:** This section documents real-world issues found in theme submissions. These mistakes caused themes to fail completely after installation despite having beautiful preview images.

### The Preview vs Reality Gap

One of the most common issues is creating a static HTML preview file that looks perfect, but React components that don't work in the actual LMS environment.

**The Problem:**
- Theme author creates `PREVIEW.html` with inline CSS - looks beautiful
- Theme author creates React components with incompatible syntax
- Preview and actual components have different styling approaches
- Theme installs but renders without styles or crashes

**The Solution:**
- Always test components in the actual LMS development environment
- Don't create standalone previews that differ from your React code
- Use the same styling approach in previews as in components

---

### Fatal Mistake #1: Using Next.js styled-jsx

**This is the #1 cause of theme failures.**

The Church LMS uses **Vite + React**, NOT Next.js. The `<style jsx>` syntax is a Next.js-specific feature that does NOT work in Vite/React.

**WRONG (styled-jsx - doesn't work):**
```jsx
const Header = () => {
  return (
    <header className="my-header">
      {/* content */}

      <style jsx>{`
        .my-header {
          background: blue;
          padding: 1rem;
        }
      `}</style>
    </header>
  );
};
```

**CORRECT (inline styles):**
```jsx
const Header = () => {
  return (
    <header style={{
      background: 'blue',
      padding: '1rem'
    }}>
      {/* content */}
    </header>
  );
};
```

**CORRECT (CSS file):**
```jsx
// In your component - no style tag needed
const Header = () => {
  return (
    <header className="my-header">
      {/* content */}
    </header>
  );
};

// In styles/theme.css
.my-header {
  background: blue;
  padding: 1rem;
}
```

---

### Fatal Mistake #2: Using `<a href>` Instead of React Router

**WRONG:**
```jsx
<a href="/courses">View Courses</a>
```

**CORRECT:**
```jsx
import { Link } from 'react-router-dom';

<Link to="/courses">View Courses</Link>
```

**Why this matters:**
- `<a href>` causes full page reloads
- Loses application state (user login, cart, etc.)
- Breaks Single Page Application (SPA) behavior
- Poor user experience

---

### Fatal Mistake #3: Importing NPM Packages or Path Aliases (CRITICAL - #1 BUILD FAILURE CAUSE)

**THIS IS THE #1 CAUSE OF PRODUCTION BUILD FAILURES.**

Theme components live in `/themes/` folder, which is **OUTSIDE** the client workspace. Vite/Rollup **CANNOT resolve npm packages or path aliases** for files outside the workspace during production build.

**WRONG (causes build failure):**
```jsx
// ❌ These imports will CRASH production builds
import React, { useState, useEffect } from 'react';  // OK - React is aliased
import { Link, useNavigate, useLocation } from 'react-router-dom';  // ❌ FAILS
import { useDispatch, useSelector } from 'react-redux';  // ❌ FAILS
import { logout } from '@/store/slices/authSlice';  // ❌ FAILS - path alias
import { useTheme } from '@/context/ThemeContext';  // ❌ FAILS - path alias
import axios from 'axios';  // ❌ FAILS
```

**Build Error You'll See:**
```
[rollup] Could not resolve "react-router-dom" from "themes/my-theme/components/layout/Header.jsx"
This is most likely unintended because it can break your application at runtime.
```

**CORRECT (Theme Component Compatibility Layer):**
```jsx
/**
 * THEME COMPATIBILITY LAYER
 * ========================
 * Theme files CANNOT import npm packages (react-redux, axios, etc.) or use path aliases (@/)
 * because Vite/Rollup cannot resolve them during production build.
 *
 * Instead, we use:
 * - Browser APIs (fetch, window.location) for data fetching and navigation
 * - Window globals set by the main app for auth state and settings
 * - Local wrapper components for Link functionality
 */

import React, { useState, useEffect } from 'react';  // ✅ React is aliased in vite.config.js

// ✅ Use regular anchor tags instead of react-router-dom Link
const Link = ({ to, children, className, style, onClick }) => (
    <a href={to} className={className} style={style} onClick={onClick}>{children}</a>
);

// ✅ Replacement hooks using browser APIs
const useNavigate = () => (path) => { window.location.href = path; };
const useLocation = () => ({ pathname: window.location.pathname });

// ✅ Hook to get auth state from window global (set by main app)
const useAuth = () => {
    const [auth, setAuth] = useState({ isAuthenticated: false, user: null });

    useEffect(() => {
        const checkAuth = () => {
            if (window.__LMS_AUTH__) {
                setAuth(window.__LMS_AUTH__);
            } else {
                // Fallback: check localStorage token
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

// ✅ Hook to get theme settings from window global
const useThemeSettings = () => {
    const [settings, setSettings] = useState({});
    useEffect(() => {
        if (window.__LMS_THEME_SETTINGS__) {
            setSettings(window.__LMS_THEME_SETTINGS__);
        }
    }, []);
    return { settings };
};

// ✅ Logout function using fetch API (instead of axios + redux dispatch)
const performLogout = async () => {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
    } catch (e) { /* ignore */ }
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
};

// Now use these in your component:
const MyThemeHeader = () => {
  const { isAuthenticated, user } = useAuth();
  const { settings } = useThemeSettings();
  const location = useLocation();
  
  // Use fetch instead of axios
  const [menuItems, setMenuItems] = useState([]);
  useEffect(() => {
    fetch('/api/menus?location=header')
      .then(res => res.json())
      .then(data => setMenuItems(data.data || []));
  }, []);
  
  return (
    <header>
      <Link to="/">Home</Link>  {/* Uses our local Link component */}
      {isAuthenticated && <button onClick={performLogout}>Logout</button>}
    </header>
  );
};
```

**Reference:** See `themes/celestial/components/layout/Header.jsx` for the complete working pattern.

---

### Fatal Mistake #4: Hardcoded Navigation Links

**WRONG:**
```jsx
const navigationLinks = [
  { name: 'Home', href: '/' },
  { name: 'Courses', href: '/courses' },
  // ... hardcoded
];
```

**CORRECT (fetch from API):**
```jsx
const [menuItems, setMenuItems] = useState([]);

useEffect(() => {
  const fetchMenuItems = async () => {
    try {
      const { data } = await axios.get('/api/menus', {
        params: { location: 'header' }
      });
      if (data.success && data.data.length > 0) {
        const headerMenu = data.data[0];
        const menuResponse = await axios.get(`/api/menus/${headerMenu.id}`);
        if (menuResponse.data.success) {
          setMenuItems(menuResponse.data.data.items || []);
        }
      }
    } catch (error) {
      console.error('Failed to fetch menu items:', error);
    }
  };
  fetchMenuItems();
}, []);
```

---

### Fatal Mistake #5: External Dependencies Without Checking

**WRONG:**
```jsx
import { Menu, X, Flame, Bell } from 'lucide-react';
```

If `lucide-react` is not in the LMS's `package.json`, this import will CRASH the entire application.

**CORRECT (use inline SVG):**
```jsx
const FlameIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
    <path d="M12 23c-3.866 0-7-3.358-7-7.5..."/>
  </svg>
);
```

**Or check existing packages:**
```bash
# Check what's already available
cat client/package.json | grep -E "icon|lucide|heroicon"
```

---

### Fatal Mistake #6: Wrong Puck Component Export Format

**WRONG (attaching config to component):**
```jsx
export const MyComponent = ({ title }) => <div>{title}</div>;

MyComponent.config = {
  label: "My Component",
  fields: { title: { type: 'text' } },
  defaultProps: { title: 'Hello' }
};
```

**CORRECT (separate config export):**
```jsx
const MyComponent = ({ title }) => <div>{title}</div>;

export const MyComponentConfig = {
  render: MyComponent,
  label: "My Component",
  fields: {
    title: { type: 'text', label: 'Title' }
  },
  defaultProps: {
    title: 'Hello'
  }
};
```

---

### Fatal Mistake #7: Not Using ThemeContext

**WRONG (hardcoded):**
```jsx
const Header = () => (
  <header>
    <img src="/logo.png" alt="My Site" />
    <span>My Site Name</span>
  </header>
);
```

**CORRECT (using theme settings):**
```jsx
import { useTheme } from '@/context/ThemeContext';

const Header = () => {
  const { settings } = useTheme();

  return (
    <header>
      <img
        src={settings.primary_logo || '/logo.png'}
        alt={settings.site_name || 'Site'}
      />
      <span>{settings.site_name}</span>
    </header>
  );
};
```

---

### Fatal Mistake #9: Tailwind Classes Purged in Production (lg:hidden, etc.)

**Problem:** Theme uses Tailwind classes like `lg:hidden`, `md:flex`, etc., but they don't work in production builds.

**Root Cause:** 
- **Tailwind CSS v3:** The `content` array in `tailwind.config.js` only scans `./src/**/*` by default
- **Tailwind CSS v4:** Uses CSS-based `@source` directive, NOT tailwind.config.js for content sources
- Theme files in `/themes/` folder are **outside** the scan path, so Tailwind doesn't see their classes and **purges them** in production

**Symptoms:**
- Mobile sidebar shows on desktop (lg:hidden purged)
- Responsive layouts break in production but work in dev
- Classes work locally but not after `npm run build`

**FOR TAILWIND v3 (tailwind.config.js):**
```javascript
// ❌ WRONG - Themes folder not included
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,css}",
  ],
};

// ✅ CORRECT - Include themes folder
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,css}",
    "../themes/**/*.{js,jsx,ts,tsx}",  // Include themes folder!
  ],
};
```

**FOR TAILWIND v4 (CSS-based config):**
Tailwind v4 uses `@source` directives in CSS, NOT the tailwind.config.js content array:

```css
/* client/src/styles/index.css */
@import "tailwindcss";

/* Tell Tailwind v4 to scan the themes folder */
@source "../../themes";

/* CRITICAL: Manual CSS fallback for lg:hidden */
/* The @source directive may not reliably include all classes */
@media (min-width: 1024px) {
  .lg\:hidden {
    display: none !important;
  }
}
```

**Why Manual CSS Fallback is Needed:**
1. The `@source` directive may not work reliably for all classes
2. The `@source inline("lg:hidden")` safelist syntax may not be recognized
3. Manual CSS is 100% guaranteed to work regardless of Tailwind scanning

**Key Point:** For critical responsive classes that MUST work in production (like `lg:hidden` for mobile sidebars), always add a manual CSS fallback. Don't rely solely on Tailwind scanning.

---

### Fatal Mistake #8: Mobile Sidebar Showing on Desktop

**WRONG (sidebar visible on all screen sizes):**
```jsx
{/* Toggle button always visible */}
<button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2">
  <MenuIcon />
</button>

{/* Sidebar panel - no responsive hiding */}
<div className={`fixed top-0 right-0 h-full z-40 ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'}`}>
  {/* sidebar content */}
</div>

{/* Backdrop - no responsive hiding */}
{sidebarOpen && (
  <div className="fixed inset-0 z-30" onClick={() => setSidebarOpen(false)} />
)}
```

**Result:** Mobile sidebar appears on desktop alongside the horizontal nav, creating duplicate navigation.

**CORRECT (sidebar hidden on desktop with `lg:hidden`):**
```jsx
{/* Toggle button - mobile only */}
<button
  onClick={() => setSidebarOpen(!sidebarOpen)}
  className="lg:hidden p-2"  {/* ✅ Hidden on desktop */}
>
  <MenuIcon />
</button>

{/* Sidebar panel - mobile only */}
<div
  className={`lg:hidden fixed top-0 right-0 h-full z-40 ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'}`}  {/* ✅ Hidden on desktop */}
>
  {/* sidebar content */}
</div>

{/* Backdrop - mobile only */}
{sidebarOpen && (
  <div
    className="lg:hidden fixed inset-0 z-30"  {/* ✅ Hidden on desktop */}
    onClick={() => setSidebarOpen(false)}
  />
)}
```

**Key Classes:**
- `lg:hidden` - Hides element on screens ≥1024px (desktop)
- Apply to: toggle button, sidebar panel, AND backdrop overlay

**Why this matters:**
- Desktop already has horizontal navigation bar
- Mobile sidebar duplicates the navigation
- Creates confusing UX with two menus visible

---

### Pre-Submission Checklist

Before submitting your theme, verify:

- [ ] **Mobile sidebar has `lg:hidden`** - Toggle button, sidebar panel, AND backdrop
- [ ] **NO npm package imports** - Search for `from 'react-router-dom'`, `from 'react-redux'`, `from 'axios'`
- [ ] **NO path alias imports** - Search for `from '@/`
- [ ] **Uses Theme Compatibility Layer** - Local Link, useAuth, useThemeSettings, performLogout
- [ ] **Uses fetch API** - Not axios for API calls
- [ ] **Uses window globals** - `window.__LMS_AUTH__`, `window.__LMS_THEME_SETTINGS__`
- [ ] **No `<style jsx>` tags** - Search your code for "style jsx"
- [ ] **Menu items fetched via fetch()** - Not hardcoded, not axios
- [ ] **No external icon libraries** - Use inline SVG
- [ ] **Puck components use Config exports** - Not attached properties
- [ ] **Tested with production build** - Run `npm run build` to verify
- [ ] **CSS in separate files** - Not styled-jsx blocks
- [ ] **Mobile sidebar hidden on desktop** - `lg:hidden` on toggle, panel, and backdrop

---

### Reference: Working Theme Structure

Study the **Celestial theme** (`themes/celestial/`) as your reference:

```
celestial/
├── theme.json                 # Correct manifest
├── components/
│   ├── index.js               # Correct exports
│   ├── layout/
│   │   ├── Header.jsx         # Uses COMPATIBILITY LAYER (no npm imports)
│   │   └── Footer.jsx         # Same pattern
│   └── Hero.jsx               # Inline styles, proper props
├── puck/
│   └── index.jsx              # Correct Config exports
└── styles/
    └── theme.css              # All styles here, no styled-jsx
```

**Key patterns from Celestial Header (UPDATED January 2026):**
1. **NO npm imports** - No react-router-dom, react-redux, axios
2. **Local Link component** - `<a href>` wrapper for navigation
3. **useAuth() hook** - Reads from `window.__LMS_AUTH__` global
4. **useThemeSettings() hook** - Reads from `window.__LMS_THEME_SETTINGS__` global  
5. **performLogout()** - Uses fetch API + localStorage, not Redux dispatch
6. **fetch() for API calls** - Not axios
7. Uses inline styles (no styled-jsx)

---

### Error Analysis Document

For a complete analysis of a failed theme submission with all errors documented, see:

**[THEME_ERROR_ANALYSIS_PROPHETIC_ACADEMY.md](THEME_ERROR_ANALYSIS_PROPHETIC_ACADEMY.md)**

This document provides detailed before/after comparisons and fix recommendations.

---

## 17. CSS Architecture & Text Visibility Best Practices

> **CRITICAL:** This section documents real-world lessons learned from fixing production theme text visibility issues. Following these practices will prevent invisible text, broken layouts, and CSS cascade conflicts.

### Table of Contents for Section 17

1. [The Critical CSS Cascade Layer Issue](#171-the-critical-css-cascade-layer-issue)
2. [Universal Selector Prohibition](#172-universal-selector-prohibition)
3. [Text Contrast Decision Tree](#173-text-contrast-decision-tree)
4. [Glassmorphism Implementation Guide](#174-glassmorphism-implementation-guide)
5. [Component-Specific Styling Patterns](#175-component-specific-styling-patterns)
6. [Nested Component Color Inheritance](#176-nested-component-color-inheritance)
7. [High-Specificity Selector Strategies](#177-high-specificity-selector-strategies)
8. [Debugging Text Visibility Issues](#178-debugging-text-visibility-issues)

---

### 17.1 The Critical CSS Cascade Layer Issue

**Platform:** Tailwind CSS v4 with CSS Cascade Layers

Tailwind CSS v4 uses the `@layer` directive to organize CSS into layers (`base`, `components`, `utilities`). Understanding this is **CRITICAL** because:

> **Unlayered CSS (your theme stylesheet) has HIGHER precedence than layered CSS (Tailwind utilities), regardless of specificity.**

#### How CSS Cascade Layers Work

```
CSS Cascade Order (lowest to highest priority):
┌──────────────────────────────────────┐
│ 1. @layer base (Tailwind Preflight)  │ ← Lowest
├──────────────────────────────────────┤
│ 2. @layer components                 │
├──────────────────────────────────────┤
│ 3. @layer utilities (Tailwind utils) │
├──────────────────────────────────────┤
│ 4. UNLAYERED CSS (your theme.css)    │ ← Highest
└──────────────────────────────────────┘
```

#### Real-World Impact

**Example: The `mx-auto` Problem**

```css
/* ❌ WRONG - This breaks Tailwind utilities */
/* In your theme.css (unlayered) */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
```

**What happens:**
1. Developer adds `className="mx-auto"` to center content
2. Tailwind generates `.mx-auto { margin-left: auto; margin-right: auto; }`
3. But your `* { margin: 0 }` is unlayered, so it wins
4. Result: `margin-left: 0px` instead of `auto` - content stays left-aligned

**Browser DevTools Evidence:**
```
Element: <div class="mx-auto">
  Computed Styles:
    margin-left: 0px     ← Your theme CSS (unlayered, wins)
    margin-right: 0px

  Overridden Styles:
    margin-left: auto    ← Tailwind utility (layered, loses)
    margin-right: auto
```

#### The Fix

```css
/* ✅ CORRECT - Only box-sizing, no margin/padding reset */
* {
  box-sizing: border-box;
}

/* Tailwind's Preflight (in @layer base) provides proper CSS reset */
/* Don't fight it with your own reset */
```

#### Golden Rule

**NEVER override Tailwind utilities with unlayered CSS unless absolutely necessary.**

If you must override, use:
1. **Higher specificity selectors** (target specific elements)
2. **The `!important` flag** (sparingly, for intentional overrides)
3. **Component-specific classes** (not universal selectors)

---

### 17.2 Universal Selector Prohibition

**The most common mistake in theme CSS: Using `*` (universal selector) for resets.**

#### Prohibited Patterns

```css
/* ❌ BREAKS EVERYTHING - Never do this */
* {
  margin: 0;
  padding: 0;
}

/* ❌ BREAKS TAILWIND SPACING - No */
* {
  margin: 0 !important;
  padding: 0 !important;
}

/* ❌ BREAKS LAYOUT - Don't */
*:not(script):not(style) {
  margin: 0;
  padding: 0;
}
```

#### Why These Break Everything

1. **Breaks Tailwind utilities:** All `m-*`, `p-*`, `mx-*`, `px-*` classes stop working
2. **Breaks component spacing:** Cards, buttons, forms lose all spacing
3. **Breaks responsive design:** `sm:px-4`, `md:py-8` utilities ignored
4. **Breaks third-party components:** Any library using margin/padding fails

#### Allowed Universal Selectors

```css
/* ✅ SAFE - These properties don't conflict */
* {
  box-sizing: border-box;
}

* {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

* {
  outline-color: var(--color-primary);
}
```

#### The Right Approach

Instead of universal resets, target specific elements:

```css
/* ✅ CORRECT - Target specific needs */
body {
  margin: 0;
  padding: 0;
  font-family: var(--font-body);
}

h1, h2, h3, h4, h5, h6 {
  margin-top: 0;
  font-family: var(--font-heading);
}

img {
  max-width: 100%;
  height: auto;
}
```

---

### 17.3 Text Contrast Decision Tree

Use this decision tree to determine correct text color for ANY element:

```
┌─────────────────────────────────┐
│  What is the element's          │
│  background color?              │
└────────────┬────────────────────┘
             │
    ┌────────┴─────────┐
    │                  │
    ▼                  ▼
┌───────┐          ┌───────┐
│ DARK  │          │ LIGHT │
│ BG    │          │ BG    │
└───┬───┘          └───┬───┘
    │                  │
    │                  │
    ▼                  ▼
Use LIGHT text    Use DARK text
#F3F4F6 - #FFFFFF  #1F2937 - #111827
```

#### Dark Backgrounds (Use Light Text)

**Triggers:**
- Glassmorphism cards: `rgba(31, 41, 55, 0.9)`
- Header/Footer: `rgba(15, 15, 26, 0.95)`
- Hero sections: Gradient overlays
- Cards with `bg-gray-800`, `bg-slate-900`
- Any `background: linear-gradient(...)` with dark colors

**CSS Pattern:**
```css
/* Dark glassmorphism cards */
[class*="rounded-"][class*="shadow"],
.card,
header,
footer,
[role="banner"],
[role="contentinfo"] {
  color: #F3F4F6 !important;
}

/* All children inherit light text */
[class*="rounded-"][class*="shadow"] *,
.card *,
header *,
footer * {
  color: #F3F4F6 !important;
}
```

#### Light Backgrounds (Use Dark Text)

**Triggers:**
- Main page container: `bg-white`, `bg-gray-50`, `bg-gray-100`
- `.min-h-screen` containers (often have light computed background)
- Sections without explicit background classes
- Forms, input fields (usually white background)

**CSS Pattern:**
```css
/* Light background sections */
.bg-white,
.bg-gray-50,
.bg-gray-100,
.min-h-screen,
main > div:not([class*="bg-"]):not([class*="dark"]) {
  color: #1F2937 !important;
}

/* All children inherit dark text */
.bg-white *,
.bg-gray-50 *,
.bg-gray-100 *,
.min-h-screen * {
  color: #1F2937 !important;
}
```

#### WCAG Color Contrast Requirements

Always test contrast ratios:

| Level | Normal Text | Large Text (18px+ or 14px bold) |
|-------|-------------|----------------------------------|
| **AA (Minimum)** | 4.5:1 | 3:1 |
| **AAA (Enhanced)** | 7:1 | 4.5:1 |

**Tools:**
- Chrome DevTools → Inspect → Accessibility pane
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Coolors Contrast Checker](https://coolors.co/contrast-checker)

**Example:**
```
Dark Text (#1F2937) on Light Background (#FFFFFF)
Contrast Ratio: 16.1:1 ✅ AAA

Light Text (#F3F4F6) on Dark Background (#1E1B4B)
Contrast Ratio: 8.2:1 ✅ AAA
```

---

### 17.4 Glassmorphism Implementation Guide

**Glassmorphism:** Design pattern with semi-transparent backgrounds, backdrop blur, and subtle borders.

#### Complete Glassmorphism Pattern

```css
/* ==========================================================================
   GLASSMORPHISM CARDS - Support ALL rounded variants
   ========================================================================== */

/* Target all rounded variants with shadows */
.card,
[class*="rounded-lg"][class*="shadow"],
[class*="rounded-xl"][class*="shadow"],
[class*="rounded-2xl"][class*="shadow"],
[class*="rounded-3xl"][class*="shadow"],
[class*="bg-white"][class*="rounded"],
.sticky[class*="shadow"],
.sticky[class*="rounded"] {
  /* Dark semi-transparent background */
  background: rgba(31, 41, 55, 0.9) !important;

  /* Blur effect (critical for glassmorphism) */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);

  /* Subtle glow border */
  border: 1px solid rgba(167, 139, 250, 0.2) !important;

  /* Soft shadow */
  box-shadow:
    0 8px 32px 0 rgba(31, 38, 135, 0.37),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset !important;

  /* Light text for readability */
  color: #F3F4F6 !important;
}

/* All text inside glassmorphism cards must be light */
.card *,
[class*="rounded-lg"][class*="shadow"] *,
[class*="rounded-xl"][class*="shadow"] *,
[class*="rounded-2xl"][class*="shadow"] *,
[class*="rounded-3xl"][class*="shadow"] * {
  color: #F3F4F6 !important;
}

/* Links inside glassmorphism cards - lighter blue */
[class*="rounded-"][class*="shadow"] a,
.card a {
  color: #A5B4FC !important;
}

[class*="rounded-"][class*="shadow"] a:hover,
.card a:hover {
  color: #06B6D4 !important;
}
```

#### Why Support All Rounded Variants?

**Real-World Issue: The Courses Page Sidebar**

Original CSS only targeted `rounded-lg` and `rounded-xl`:
```css
/* ❌ INCOMPLETE - Misses rounded-2xl */
[class*="rounded-lg"][class*="shadow"],
[class*="rounded-xl"][class*="shadow"] {
  background: rgba(31, 41, 55, 0.9) !important;
}
```

But the Courses page sidebar uses `rounded-2xl`:
```jsx
<div className="bg-white rounded-2xl shadow-md p-6 sticky top-24">
  {/* Filters content */}
</div>
```

**Result:** Sidebar had light background but no glassmorphism → light text invisible.

**Fix:** Add ALL rounded variants:
```css
/* ✅ COMPLETE - Covers all cases */
[class*="rounded-lg"][class*="shadow"],
[class*="rounded-xl"][class*="shadow"],
[class*="rounded-2xl"][class*="shadow"],
[class*="rounded-3xl"][class*="shadow"] {
  background: rgba(31, 41, 55, 0.9) !important;
  /* ... rest of glassmorphism styles */
}
```

#### Attribute Selector Pattern

**Using `[class*="..."]` for pattern matching:**

```css
/* Matches ANY class containing "rounded-2xl" */
[class*="rounded-2xl"] { }

/* Examples that match: */
/* class="rounded-2xl" ✓ */
/* class="bg-white rounded-2xl shadow-md" ✓ */
/* class="sticky rounded-2xl p-4" ✓ */
```

**Combining attribute selectors (AND logic):**

```css
/* Matches elements with BOTH patterns in class */
[class*="rounded-2xl"][class*="shadow"] { }

/* Matches: */
/* class="rounded-2xl shadow-md" ✓ */
/* class="bg-white rounded-2xl shadow-lg p-6" ✓ */

/* Does NOT match: */
/* class="rounded-2xl" ✗ (no shadow) */
/* class="shadow-md" ✗ (no rounded-2xl) */
```

#### Glassmorphism Variants

**Light Glassmorphism (for dark-mode themes):**
```css
.card-light-glass {
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #1F2937 !important;
}
```

**Heavy Glassmorphism (more opaque):**
```css
.card-heavy-glass {
  background: rgba(31, 41, 55, 0.95) !important;
  backdrop-filter: blur(16px);
  border: 1px solid rgba(167, 139, 250, 0.3);
}
```

---

### 17.5 Component-Specific Styling Patterns

Different components require different CSS strategies. Here's the proven pattern for each major component type.

#### Header / Navigation

**Requirements:**
- Dark background (branding/visual hierarchy)
- White text (contrast)
- Transparent when not scrolled (optional)
- Very high specificity (overrides Tailwind utility classes)

**Complete Pattern:**
```css
/* ==========================================================================
   HEADER / NAVIGATION - Force dark background with light text
   ========================================================================== */

/* Dark glassmorphism background */
header,
[role="banner"],
nav,
[role="banner"] > div,
[role="banner"] > div > div {
  background: rgba(15, 15, 26, 0.95) !important;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

/* Force all navigation elements to white text */
[role="banner"] *,
header *,
nav * {
  color: #FFFFFF !important;
  background: transparent !important;
}

/* Navigation links - High specificity to override .text-sm.font-medium */
[role="banner"] nav a,
[role="banner"] a.text-sm,
[role="banner"] nav a.text-sm.font-medium,
header nav a,
header nav a.text-sm.font-medium,
nav a.text-sm.font-medium,
[role="banner"] a[class*="text-sm"],
header a[class*="text-sm"] {
  color: #FFFFFF !important;
}

/* Logo styling */
[role="banner"] img,
header img {
  filter: brightness(1.1);
}

/* Mobile menu button */
[role="banner"] button,
header button {
  color: #FFFFFF !important;
}
```

**Why So Many Selectors?**

Tailwind generates utility classes like:
```html
<a class="text-sm font-medium text-gray-900">Link</a>
```

The `.text-gray-900` class has high specificity. To override it, you need:
```css
/* High specificity chain */
[role="banner"] nav a.text-sm.font-medium {
  color: #FFFFFF !important;
}
```

#### Footer

**Requirements:**
- Dark background (visual closure)
- Light text
- Gradient headings (branding)
- Link hover effects

**Complete Pattern:**
```css
/* ==========================================================================
   FOOTER - Force dark background with light text
   ========================================================================== */

/* Dark background */
footer,
[role="contentinfo"],
[class*="footer"] {
  background: rgba(15, 15, 26, 0.98) !important;
  color: #F3F4F6 !important;
}

/* All text light */
footer *,
[role="contentinfo"] *,
[class*="footer"] * {
  color: #F3F4F6 !important;
}

/* Links - Lighter blue */
footer a,
[role="contentinfo"] a,
[class*="footer"] a {
  color: #A5B4FC !important;
  transition: color 0.2s ease;
}

/* Link hover - Cyan accent */
footer a:hover,
[role="contentinfo"] a:hover,
[class*="footer"] a:hover {
  color: #06B6D4 !important;
}

/* Footer headings - Gradient text */
footer h1, footer h2, footer h3, footer h4, footer h5, footer h6,
[role="contentinfo"] h1,
[role="contentinfo"] h2,
[role="contentinfo"] h3 {
  background: linear-gradient(
    135deg,
    var(--color-primary, #A78BFA) 0%,
    var(--color-secondary, #22D3EE) 100%
  ) !important;
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  background-clip: text !important;
}

/* Copyright text - Slightly muted */
footer small,
[role="contentinfo"] small {
  color: #9CA3AF !important;
}
```

#### Hero Sections

**Requirements:**
- Dark backgrounds (usually gradients or images)
- Light text
- Large, prominent typography
- Overlay support (for background images)

**Complete Pattern:**
```css
/* ==========================================================================
   HERO SECTIONS - Dark backgrounds with light text
   ========================================================================== */

/* Target hero sections */
[class*="bg-gradient"],
[class*="bg-primary"],
[class*="bg-secondary"],
section:first-child,
.hero,
[class*="hero"],
[class*="Hero"] {
  color: #F3F4F6 !important;
}

/* All children inherit light text */
[class*="bg-gradient"] *,
[class*="bg-primary"] *,
[class*="bg-secondary"] *,
.hero *,
[class*="hero"] *,
[class*="Hero"] * {
  color: #F3F4F6 !important;
}

/* Hero headings - Extra large, bold */
.hero h1,
[class*="hero"] h1,
section:first-child h1 {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 700;
  line-height: 1.1;
  background: linear-gradient(
    135deg,
    #FFFFFF 0%,
    var(--color-secondary, #22D3EE) 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Hero CTAs - High contrast buttons */
.hero button,
.hero a.btn,
[class*="hero"] button {
  background: var(--color-secondary, #22D3EE);
  color: #111827;
  font-weight: 600;
}
```

#### Forms / Input Fields

**Requirements:**
- Light backgrounds (readability)
- Dark text (contrast)
- Clear focus states
- Error states (red text, visible)

**Complete Pattern:**
```css
/* ==========================================================================
   FORMS - Light backgrounds, dark text, clear states
   ========================================================================== */

/* Input fields - light background, dark text */
input,
textarea,
select,
[type="text"],
[type="email"],
[type="password"],
[type="search"] {
  background: #FFFFFF !important;
  color: #1F2937 !important;
  border: 1px solid #D1D5DB;
}

/* Labels - dark text */
label {
  color: #374151 !important;
  font-weight: 500;
}

/* Placeholder text - muted */
input::placeholder,
textarea::placeholder {
  color: #9CA3AF !important;
}

/* Focus state - primary color border */
input:focus,
textarea:focus,
select:focus {
  outline: none;
  border-color: var(--color-primary, #4F46E5);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

/* Error state - red border, visible error text */
input.error,
textarea.error {
  border-color: #EF4444 !important;
}

.error-message {
  color: #EF4444 !important;
  font-size: 0.875rem;
}
```

---

### 17.6 Nested Component Color Inheritance

**The Problem:** Cards with dark glassmorphism backgrounds appear inside light background sections.

#### Scenario: "Our Core Beliefs" Card

```html
<section class="bg-gray-50">  <!-- Light background, dark text -->
  <div class="rounded-lg shadow-md">  <!-- Glassmorphism card: dark bg -->
    <h3>Our Core Beliefs</h3>  <!-- ❌ Inherits dark text from section -->
    <p>We believe...</p>
  </div>
</section>
```

**Without nested rules:**
1. Section `bg-gray-50` applies dark text to all children
2. Card has dark glassmorphism background (from global card rules)
3. Text inherits dark color from section
4. Result: Dark text on dark background → invisible

#### The Fix: Override Inheritance

```css
/* ==========================================================================
   NESTED COMPONENTS - Cards inside light sections
   ========================================================================== */

/* CRITICAL: Cards inside light sections still have dark glassmorphism backgrounds
   So text inside them must be LIGHT, overriding the light-section dark text rules */

.bg-gray-50 .bg-white *,
.bg-gray-50 [class*="rounded-lg"][class*="shadow"] *,
.bg-gray-50 [class*="rounded-xl"][class*="shadow"] *,
.bg-gray-50 [class*="rounded-2xl"][class*="shadow"] *,
.bg-gray-50 .card *,
.bg-gray-100 .bg-white *,
.bg-gray-100 [class*="rounded-lg"][class*="shadow"] *,
.bg-gray-100 [class*="rounded-xl"][class*="shadow"] *,
.bg-gray-100 [class*="rounded-2xl"][class*="shadow"] *,
.bg-gray-100 .card *,
.min-h-screen .bg-white *,
.min-h-screen [class*="rounded-lg"][class*="shadow"] *,
.min-h-screen [class*="rounded-xl"][class*="shadow"] *,
.min-h-screen [class*="rounded-2xl"][class*="shadow"] *,
.min-h-screen .card *,
main [class*="rounded-lg"][class*="shadow"] *,
main [class*="rounded-xl"][class*="shadow"] *,
main .bg-white[class*="rounded"] * {
  color: #F3F4F6 !important;
}
```

#### Specificity Math

```
.bg-gray-50                                           → 010 (1 class)
.bg-gray-50 *                                         → 010 (1 class, universal)
.bg-gray-50 [class*="rounded-lg"][class*="shadow"] * → 030 (1 class + 2 attributes)
```

The nested rule has **higher specificity**, so it wins.

#### Testing Nested Components

**Checklist:**
1. Home page stats cards inside `.min-h-screen` container
2. Course cards inside `section.bg-gray-50`
3. Sidebar filters inside `main.bg-white`
4. Testimonial cards inside light sections
5. Feature cards on About page

**Browser DevTools Check:**
```
Element: <h3> inside .rounded-lg.shadow-md inside .bg-gray-50

  Applied Styles:
    color: #F3F4F6 !important;  ✅ From nested rule

  Overridden Styles:
    color: #1F2937 !important;  ✗ From .bg-gray-50 * rule
```

---

### 17.7 High-Specificity Selector Strategies

**When you need to override Tailwind utility classes, specificity is your weapon.**

#### Specificity Calculation

```
Inline styles               → 1000
IDs (#header)               → 0100
Classes (.btn, [role])      → 0010
Elements (div, h1)          → 0001
```

**Combining selectors adds specificity:**
```css
div                         → 0001
div.card                    → 0011 (1 element + 1 class)
[role="banner"] nav a       → 0031 (1 attribute + 1 element + 1 element)
[role="banner"] nav a.text-sm.font-medium
                            → 0051 (1 attribute + 2 elements + 2 classes)
```

#### Tailwind Utility Class Specificity

```html
<a class="text-sm font-medium text-gray-900">Link</a>
```

Generated CSS:
```css
.text-sm { font-size: 0.875rem; }         → 0010
.font-medium { font-weight: 500; }        → 0010
.text-gray-900 { color: #111827; }        → 0010
```

To override `.text-gray-900` with specificity (no `!important`):
```css
/* ❌ Too weak - same specificity, but loaded earlier */
nav a { color: #FFFFFF; }  → 0011 (1 element + 1 element)

/* ✅ Stronger - higher specificity */
[role="banner"] nav a { color: #FFFFFF; }  → 0031

/* ✅ Even stronger - chain utility classes */
nav a.text-sm.font-medium { color: #FFFFFF; }  → 0041
```

#### When to Use `!important`

**Legitimate use cases:**
1. **Theme overrides:** Intentionally overriding Tailwind defaults site-wide
2. **Third-party CSS:** Fighting external stylesheets you can't modify
3. **Utility classes:** Creating your own utility classes that should always win

**Pattern:**
```css
/* Theme color overrides - always win */
[role="banner"] * {
  color: #FFFFFF !important;
}

/* Glassmorphism cards - always dark background */
[class*="rounded-"][class*="shadow"] {
  background: rgba(31, 41, 55, 0.9) !important;
}
```

**Avoid `!important` when:**
- You can achieve the same with higher specificity
- It's a temporary hack
- You're fighting your own CSS

#### The Specificity Ladder

**Level 1: Element Selectors (weakest)**
```css
a { color: blue; }  /* Loses to .text-gray-900 */
```

**Level 2: Single Class**
```css
.nav-link { color: blue; }  /* Ties with .text-gray-900 (last one wins) */
```

**Level 3: Attribute Selector**
```css
[role="banner"] a { color: blue; }  /* Beats .text-gray-900 */
```

**Level 4: Multiple Classes**
```css
a.text-sm.font-medium { color: blue; }  /* Beats single class */
```

**Level 5: Attribute + Class Chain**
```css
[role="banner"] a.text-sm.font-medium { color: blue; }  /* Very strong */
```

**Level 6: !important (nuclear option)**
```css
a { color: blue !important; }  /* Always wins (but use sparingly) */
```

---

### 17.8 Debugging Text Visibility Issues

**Step-by-step process for diagnosing invisible text.**

#### Step 1: Visual Inspection

**Signs of invisible text:**
- Empty white boxes where cards should have content
- Navigation menu appears blank
- Buttons with no labels (but still clickable)
- Form fields with no visible labels

#### Step 2: Browser DevTools Investigation

**Open Chrome DevTools:**
1. Right-click invisible element → Inspect
2. Go to **Computed** tab
3. Check these properties:

**Critical properties to check:**
```
color: [value]
  ↓
  If rgb(31, 41, 55) on dark background → PROBLEM
  If rgb(243, 244, 246) on light background → PROBLEM

background-color: [value]
  ↓
  Compare to text color for contrast

opacity: [value]
  ↓
  If 0 → Element is invisible

display: [value]
  ↓
  If "none" → Element is hidden
```

#### Step 3: Check Cascade Layers

**In DevTools Styles panel:**

Look for crossed-out styles (overridden):
```css
Element: <div class="mx-auto">

Styles:
  /* Applied */
  margin-left: 0px;  ← From your theme CSS (unlayered)

  /* Overridden */
  margin-left: auto; ← From Tailwind utility (layered)
```

**Diagnosis:** Your unlayered CSS is winning due to cascade layers.

#### Step 4: Test Contrast Ratio

**Using DevTools:**
1. Inspect element
2. Click color swatch in Styles panel
3. DevTools shows contrast ratio

**Expected:**
```
Contrast: 4.5 AA ✓
         ^^^^^
         Should be green checkmark
```

**If failed:**
```
Contrast: 1.2 ✗
         ^^^^
         Red X = invisible text
```

#### Step 5: Identify Specificity Conflicts

**In DevTools Styles panel:**

Scroll down to see which rules are applied vs. overridden:

```css
/* Applied (higher specificity) */
.text-gray-900 {
  color: rgb(17, 24, 39);  ✓ (specificity: 0010)
}

/* Overridden (lower specificity) */
a {
  color: rgb(255, 255, 255);  ✗ (specificity: 0001)
}
```

**Fix:** Increase specificity of your rule:
```css
[role="banner"] a {
  color: rgb(255, 255, 255);  ✓ (specificity: 0021)
}
```

#### Step 6: Check for Missing Selectors

**Common pattern:** CSS targets `rounded-lg` but element uses `rounded-2xl`

**How to find:**
1. Inspect invisible element
2. Check its classes: `class="rounded-2xl shadow-md"`
3. Search your theme CSS for `rounded-2xl`
4. If not found → that's your bug

**Fix:** Add missing variant:
```css
/* Before (incomplete) */
[class*="rounded-lg"][class*="shadow"] {
  background: rgba(31, 41, 55, 0.9);
}

/* After (complete) */
[class*="rounded-lg"][class*="shadow"],
[class*="rounded-xl"][class*="shadow"],
[class*="rounded-2xl"][class*="shadow"],
[class*="rounded-3xl"][class*="shadow"] {
  background: rgba(31, 41, 55, 0.9);
}
```

#### Debugging Checklist

**For every invisible text issue:**

- [ ] Checked computed `color` vs. `background-color` contrast
- [ ] Verified no unlayered universal selectors breaking Tailwind
- [ ] Confirmed CSS selector matches element's actual classes
- [ ] Checked all rounded variants (lg, xl, 2xl, 3xl) are covered
- [ ] Tested nested components (cards inside light sections)
- [ ] Verified specificity is high enough to override Tailwind utilities
- [ ] Confirmed no `opacity: 0` or `display: none` hiding element
- [ ] Checked responsive breakpoints (sm, md, lg) for visibility changes

#### Quick Fix Template

**When you find invisible text:**

```css
/* 1. Identify the component */
[THE_SELECTOR] {
  /* 2. Determine background color */
  background: [LIGHT or DARK];

  /* 3. Set contrasting text color */
  color: [DARK if light bg, LIGHT if dark bg] !important;
}

/* 4. Apply to all children */
[THE_SELECTOR] * {
  color: [SAME_AS_ABOVE] !important;
}

/* 5. If nested in opposite-color parent, override inheritance */
[PARENT_SELECTOR] [THE_SELECTOR] * {
  color: [CONTRASTING_COLOR] !important;
}
```

---

### Summary: Golden Rules for Theme CSS

1. **NEVER use universal selector resets** (`* { margin: 0 }`) - breaks Tailwind
2. **Support ALL rounded variants** (lg, xl, 2xl, 3xl) - don't miss components
3. **Use the Text Contrast Decision Tree** - dark bg → light text, light bg → dark text
4. **Override nested component inheritance** - cards in light sections need light text
5. **Use high specificity for Tailwind overrides** - attribute selectors + class chains
6. **Test with DevTools Computed panel** - verify colors and contrast ratios
7. **Check cascade layers** - unlayered CSS beats Tailwind utilities
8. **Use semantic selectors** - `[role="banner"]`, `[role="contentinfo"]`

**Before deploying any theme, systematically check:**
- ✅ All pages render with visible text
- ✅ All rounded card variants have proper styling
- ✅ Header/footer navigation links are visible
- ✅ Forms have visible labels and placeholders
- ✅ Buttons have visible text
- ✅ No Tailwind utilities are broken (mx-auto, px-4, etc.)

---

## 18. Appendix: Screenshots

The following screenshots are available for documentation:

### Theme Gallery
- `theme-gallery-full.png` - Complete theme gallery showing all installed themes
- `theme-gallery-top.png` - Top portion of theme gallery

### Theme Customizer
- `theme-customizer-branding.png` - Branding settings (logo, site name)
- `theme-customizer-colors.png` - Color customization panel
- `theme-customizer-typography.png` - Typography settings

### Theme Examples
- `theme-home-classic.png` - Homepage with Classic theme
- `theme-home-celestial.png` - Homepage with Celestial theme activated
- `admin-dashboard.png` - Admin dashboard view

### Screenshot Locations
All screenshots are stored in:
- `.playwright-mcp/docs/screenshots/` - Theme documentation screenshots
- `.playwright-mcp/` - General application screenshots
- `themes/classic/screenshots/` - Classic theme preview images

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.2 | 2026-01-18 | Claude AI | Added Section 17: CSS Architecture & Text Visibility Best Practices (based on Gemini theme fixes - comprehensive guide to CSS cascade layers, text contrast, glassmorphism, nested components, and debugging) |
| 2.1 | 2026-01-17 | Claude AI | Added Section 16: Critical Mistakes to Avoid (based on Prophetic Academy theme analysis) |
| 2.0 | 2026-01-17 | Claude AI | Comprehensive rewrite with component system |
| 1.0 | 2026-01-11 | Claude AI | Initial documentation |

---

## References

- [WordPress Theme Developer Handbook](https://developer.wordpress.org/themes/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Puck Editor Documentation](https://github.com/measuredco/puck)
- [Vite Dynamic Import](https://vitejs.dev/guide/features.html#glob-import)

---

*This document is designed for export to Microsoft Word format for distribution to theme developers.*
