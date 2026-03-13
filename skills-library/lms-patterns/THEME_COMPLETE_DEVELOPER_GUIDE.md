# MERN Community LMS - Complete Theme Developer Guide

**Version:** 3.2.0
**Last Updated:** January 18, 2026
**Platform:** Node.js / Express / PostgreSQL / React / Vite / Tailwind CSS v4.1.13

---

## Document Purpose

This is the **SINGLE SOURCE OF TRUTH** for theme development in the MERN Community LMS. It consolidates all theme-related documentation, including critical production fixes discovered through real-world deployment.

**This document supersedes:**
- `THEME_DEVELOPER_HANDBOOK.md`
- `THEME_SYSTEM_DEVELOPER_GUIDE.md`
- `THEME_DEVELOPMENT.md`
- `wordpress-style-theme-components.md`

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Architecture Overview](#2-architecture-overview)
3. [Getting Started](#3-getting-started)
4. [Theme File Structure](#4-theme-file-structure)
5. [Theme Manifest (theme.json)](#5-theme-manifest-themejson)
6. [Component Override System](#6-component-override-system)
7. [Theme Compatibility Layer (CRITICAL)](#7-theme-compatibility-layer-critical)
8. [CSS Variables & Styling](#8-css-variables--styling)
9. [Tailwind CSS v4 Configuration (CRITICAL)](#9-tailwind-css-v4-configuration-critical)
10. [Mobile Sidebar Responsiveness](#10-mobile-sidebar-responsiveness)
11. [Puck Editor Integration](#11-puck-editor-integration)
12. [Production Build Requirements](#12-production-build-requirements)
13. [Fatal Mistakes to Avoid](#13-fatal-mistakes-to-avoid)
14. [AI Agent Theme Generation Checklist](#14-ai-agent-theme-generation-checklist)
15. [Testing & Deployment](#15-testing--deployment)
16. [Reference: Celestial Theme](#16-reference-celestial-theme)

---

## 1. Introduction

### What is a Theme?

A theme is a self-contained package that controls the visual appearance and layout of the MERN Community LMS. Unlike plugins which add functionality, themes focus on:

- **Visual Design** - Colors, typography, spacing, and overall aesthetics
- **Layout Structure** - Header, footer, sidebar, content arrangement
- **Component Styling** - How Puck visual builder components render
- **User Experience** - Responsive design, dark mode, accessibility

### WordPress-Style Architecture

| Concept | WordPress | MERN LMS |
|---------|-----------|----------|
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
┌─────────────────────────────────────────────────────────────────────┐
│                         Theme System Flow                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. App Startup                                                      │
│     └─> ThemeManager.loadTheme('celestial')                         │
│          └─> Loads theme.json for config                            │
│          └─> Loads components/index.js for overrides                │
│          └─> Registers overrides in componentOverrides Map          │
│                                                                      │
│  2. Component Resolution (via ThemeContext)                         │
│     └─> getComponent('Header') called                               │
│          └─> Check componentOverrides Map                           │
│          └─> Return theme's Header OR fallback to default           │
│                                                                      │
│  3. MainLayout renders                                              │
│     └─> Uses resolved Header, Footer from getComponent()           │
│     └─> Wrapped in React.Suspense for lazy loading                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
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
mkdir -p themes/my-first-theme/components/layout
mkdir -p themes/my-first-theme/styles
```

**Step 2: Create theme.json**

```json
{
  "name": "my-first-theme",
  "displayName": "My First Theme",
  "slug": "my-first-theme",
  "version": "1.0.0",
  "description": "A simple custom theme for learning",
  "author": "Your Name",
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
    "headingFont": "Inter, sans-serif",
    "bodyFont": "Inter, sans-serif",
    "baseFontSize": "16px"
  },
  "features": {
    "componentOverrides": true
  },
  "stylesheets": ["styles/theme.css"]
}
```

**Step 3: Create components/index.js**

```javascript
// Export components here to override defaults
// export { default as Header } from './layout/Header';
// export { default as Footer } from './layout/Footer';

export {};  // Empty export for now
```

**Step 4: Create styles/theme.css**

```css
/* IMPORTANT: Only box-sizing reset - let Tailwind handle other resets */
* {
  box-sizing: border-box;
}

/* Theme-specific custom styles */
.theme-my-first-theme {
  /* Custom styles here */
}
```

**Step 5: Activate Theme**

1. Navigate to **Admin Panel > Settings > Themes**
2. Find your theme in the gallery
3. Click "Activate"

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
    ├── preview.png             # Preview image (400x300px)
    ├── README.md               # Documentation
    │
    ├── components/             # Component overrides
    │   ├── index.js            # Main export file (CRITICAL)
    │   └── layout/
    │       ├── Header.jsx      # Custom header
    │       └── Footer.jsx      # Custom footer
    │
    ├── puck/                   # Puck visual builder components
    │   └── index.jsx           # Puck component exports
    │
    ├── styles/                 # Theme stylesheets
    │   └── theme.css           # Main theme CSS
    │
    └── assets/                 # Static assets (optional)
        ├── images/
        └── fonts/
```

### Files to NEVER Include

- ❌ `index.jsx` - Not used by theme system
- ❌ `screenshot.png` - Use `preview.png` instead
- ❌ `node_modules/` - Never include dependencies

---

## 5. Theme Manifest (theme.json)

### Required Fields

| Field | Format | Example |
|-------|--------|---------|
| `name` | lowercase-slug | `"my-theme"` |
| `displayName` | Human readable | `"My Theme"` |
| `version` | Semantic | `"1.0.0"` |
| `description` | String | `"A custom theme"` |
| `colors` | Object at ROOT level | See below |

### Colors Object (MUST be at ROOT level)

```json
{
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

### Common Mistakes to Avoid

- ❌ `themeSettings.colors` - WRONG, use `colors` at root
- ❌ `{ "primary": { "default": "#..." } }` - WRONG, use simple hex strings
- ❌ `entryPoint`, `screenshot`, `supports` array - NOT USED

### Complete Example

```json
{
  "name": "my-theme",
  "displayName": "My Theme",
  "slug": "my-theme",
  "version": "1.0.0",
  "description": "A custom theme",
  "author": "Your Name",
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
    "headingFont": "Inter, sans-serif",
    "bodyFont": "Inter, sans-serif",
    "baseFontSize": "16px"
  },
  "features": {
    "componentOverrides": true
  },
  "stylesheets": ["styles/theme.css"]
}
```

---

## 6. Component Override System

### How It Works

The ThemeManager maintains a `componentOverrides` Map. When a theme loads, it dynamically imports components from `components/index.js`.

### Component Index File

```javascript
// themes/celestial/components/index.js

export { default as Header } from './layout/Header';
export { default as Footer } from './layout/Footer';
export { default as Hero } from './Hero';

// Metadata for discovery
export const themeComponents = {
  Header: { description: 'Custom header component' },
  Footer: { description: 'Custom footer component' },
};
```

### Using Theme Components in Layouts

```jsx
// In MainLayout.jsx
import { useTheme } from '@/context/ThemeContext';
import DefaultHeader from '@/components/layout/Header';

const MainLayout = ({ children }) => {
  const { getComponent } = useTheme();
  
  // Get theme Header or fall back to default
  const Header = getComponent('Header') || DefaultHeader;

  return (
    <div className="min-h-screen flex flex-col">
      <Suspense fallback={<div className="h-16 bg-gray-100 animate-pulse" />}>
        <Header />
      </Suspense>
      <main className="flex-1">{children}</main>
    </div>
  );
};
```

---

## 7. Theme Compatibility Layer (CRITICAL)

### ⚠️ THE #1 CAUSE OF PRODUCTION BUILD FAILURES

Theme components live in `/themes/` folder, which is **OUTSIDE** the client workspace. Vite/Rollup **CANNOT resolve npm packages or path aliases** for files outside the workspace.

### FORBIDDEN Imports

```jsx
// ❌ These imports will CRASH production builds
import { Link, useNavigate } from 'react-router-dom';  // ❌ FAILS
import { useSelector } from 'react-redux';              // ❌ FAILS
import { logout } from '@/store/slices/authSlice';     // ❌ FAILS - path alias
import axios from 'axios';                              // ❌ FAILS
```

### Required Compatibility Layer

Every theme component MUST include this at the top:

```jsx
import React, { useState, useEffect } from 'react';  // ✅ React is aliased

/**
 * THEME COMPATIBILITY LAYER
 * Theme files CANNOT import npm packages or path aliases.
 */

// ✅ Local Link component (replaces react-router-dom Link)
const Link = ({ to, children, className, style, onClick }) => (
    <a href={to} className={className} style={style} onClick={onClick}>{children}</a>
);

// ✅ Navigation hooks using browser APIs
const useNavigate = () => (path) => { window.location.href = path; };
const useLocation = () => ({ pathname: window.location.pathname });

// ✅ Auth from window global (set by main app)
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
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
    } catch (e) { /* ignore */ }
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
};

// Now your actual component:
const Header = () => {
    const { isAuthenticated, user } = useAuth();
    const { settings } = useThemeSettings();
    const [menuItems, setMenuItems] = useState([]);
    
    // ✅ Use fetch() for API calls, not axios
    useEffect(() => {
        fetch('/api/menus?location=header')
            .then(r => r.json())
            .then(d => setMenuItems(d.data?.[0]?.items || []));
    }, []);

    return (
        <header>
            <Link to="/">Home</Link>
            {isAuthenticated ? (
                <button onClick={performLogout}>Logout</button>
            ) : (
                <Link to="/login">Login</Link>
            )}
        </header>
    );
};

export default Header;
```

---

## 8. CSS Variables & Styling

### CSS Variables Applied by ThemeManager

```javascript
// ThemeManager.applyCSSVariables() sets these on :root
const cssVariables = {
  // Colors
  '--color-primary': '#1E1B4B',
  '--color-primary-50': '#f5f3ff',
  '--color-primary-900': '#1e1b4b',
  '--color-secondary': '#D4AF37',
  '--color-background': '#FDF8F0',
  '--color-surface': '#FFFEF5',
  '--color-text': '#1F1F2E',
  '--color-muted': '#64748B',
  '--color-border': '#E2D5BB',
  
  // Typography
  '--font-heading': 'Playfair Display, serif',
  '--font-body': 'Inter, sans-serif',
  '--font-size-base': '16px',
  
  // Layout
  '--max-width': '1280px',
  '--header-height': '80px',
  
  // Components
  '--radius-card': '12px',
  '--radius-button': '8px'
};
```

### Theme CSS Requirements

**CRITICAL: Never use CSS resets in theme files**

```css
/* ✅ CORRECT - Only box-sizing */
* {
  box-sizing: border-box;
}

/* ❌ WRONG - Conflicts with Tailwind v4 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
```

**Why this matters:** Tailwind CSS v4 uses CSS `@layer` directives. Unlayered CSS (like theme CSS) has HIGHER precedence than layered CSS, so `margin: 0` will override Tailwind's `mx-auto`.

---

## 9. Tailwind CSS v4 Configuration (CRITICAL)

### ⚠️ PRODUCTION-VERIFIED ISSUE (January 18, 2026)

This project uses **Tailwind CSS v4.1.13**, which has a completely different configuration system than v3.

### Key Difference: v3 vs v4

| Feature | Tailwind v3 | Tailwind v4 |
|---------|-------------|-------------|
| Content config | `tailwind.config.js` `content` array | CSS `@source` directive |
| Import syntax | `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| Safelist | `safelist` in config | `@source inline()` in CSS |

### Current Production Configuration

Located in `client/src/styles/index.css`:

```css
/* DEVELOPMENTAL HISTORY:
 * GC1 - 2025-09-30: Fixed Tailwind CSS v4 setup
 * GC2 - 2026-01-18: Added @source directive for themes folder
 */

@import "tailwindcss";

/* CRITICAL: Tell Tailwind v4 to scan the themes folder for classes */
@source "../../themes";

/* SAFELIST: Force lg:hidden to be generated */
@source inline("lg:hidden");

/* FALLBACK: Manual CSS for lg:hidden (GUARANTEED to work) */
@media (min-width: 1024px) {
    .lg\:hidden {
        display: none !important;
    }
}
```

### Why Manual CSS Fallback is Required

Through production testing on schooloftheprophets.club (January 18, 2026), we discovered:

1. **`@source "../../themes"`** - May not reliably scan all theme files
2. **`@source inline("lg:hidden")`** - Safelist syntax may not be recognized
3. **Manual CSS** - 100% guaranteed to work regardless of Tailwind scanning

**Lesson Learned:** For critical responsive classes that MUST work in production, always add a manual CSS fallback.

### Adding New Critical Classes

If you need other responsive classes guaranteed in production:

```css
/* Add to client/src/styles/index.css */

/* Manual fallbacks for critical responsive classes */
@media (min-width: 1024px) {
    .lg\:hidden { display: none !important; }
    .lg\:block { display: block !important; }
    .lg\:flex { display: flex !important; }
}

@media (min-width: 768px) {
    .md\:hidden { display: none !important; }
    .md\:block { display: block !important; }
}
```

---

## 10. Mobile Sidebar Responsiveness (CRITICAL)

### ⚠️ PRODUCTION-VERIFIED FIX (January 18, 2026)

Mobile slide-out sidebars require **FOUR critical requirements** to work properly:

### Requirement 1: The Three Elements Rule

**ALL THREE elements must have `lg:hidden`:**

```jsx
{/* 1. Toggle button - MUST have lg:hidden */}
<button 
  className="lg:hidden p-2" 
  onClick={() => setSidebarOpen(!sidebarOpen)}
>
  <MenuIcon />
</button>

{/* 2. Sidebar panel - MUST have lg:hidden */}
<div className={`lg:hidden fixed top-0 right-0 h-full z-40 
  ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'}`}
>
  {/* sidebar content */}
</div>

{/* 3. Backdrop overlay - MUST have lg:hidden */}
{sidebarOpen && (
  <div 
    className="lg:hidden fixed inset-0 z-30 bg-black/50" 
    onClick={() => setSidebarOpen(false)} 
  />
)}
```

### Requirement 2: CSS Transform Fallbacks (CRITICAL)

Tailwind v4 may not compile `translate-x-full` and `translate-x-0` from theme files. **Without these classes, the sidebar will be visible on page load!**

Add to `client/src/styles/theme-overrides.css`:

```css
/* CRITICAL: Mobile sidebar transform classes
 * Without these, sidebar appears open on page load!
 * Tailwind v4 may not scan theme files properly.
 */
.translate-x-full {
    transform: translateX(100%) !important;
}

.translate-x-0 {
    transform: translateX(0) !important;
}

.-translate-x-full {
    transform: translateX(-100%) !important;
}
```

### Requirement 3: Link Component with Navigation Delay

Theme Link components must delay navigation to allow sidebar close animation:

```jsx
// ✅ CORRECT - Delays navigation to allow sidebar to close
const Link = ({ to, children, className, style, onClick }) => {
    const handleClick = (e) => {
        if (onClick) {
            onClick(e);  // This calls setSidebarOpen(false)
        }
        // For internal links, delay navigation
        if (to && !to.startsWith('http') && !to.startsWith('//')) {
            e.preventDefault();
            setTimeout(() => {
                window.location.href = to;
            }, 100);  // 100ms delay for sidebar close animation
        }
    };
    return (
        <a href={to} className={className} style={style} onClick={handleClick}>
            {children}
        </a>
    );
};

// ❌ WRONG - Navigation happens immediately, sidebar stays open
const Link = ({ to, children, className, style, onClick }) => (
    <a href={to} className={className} style={style} onClick={onClick}>
        {children}
    </a>
);
```

### Requirement 4: State Initialization

Sidebar state MUST initialize to `false`:

```jsx
// ✅ CORRECT - Sidebar starts closed
const [sidebarOpen, setSidebarOpen] = useState(false);

// ❌ WRONG - Sidebar starts open
const [sidebarOpen, setSidebarOpen] = useState(true);
```

### Why Sidebar Opens on Page Load (Common Bug)

If your mobile sidebar is visible when the page first loads, check:

1. **Missing `translate-x-full` CSS** - The transform class isn't being applied
2. **State initialized to `true`** - `useState(true)` instead of `useState(false)`
3. **CSS not loaded** - The theme-overrides.css isn't imported in main.jsx

### Verified Working Pattern

From `themes/celestial/components/layout/Header.jsx`:

```jsx
// State initialization (line ~87)
const [sidebarOpen, setSidebarOpen] = useState(false);

// Toggle button (line ~470)
<button
  onClick={() => setSidebarOpen(!sidebarOpen)}
  className="lg:hidden relative z-50 p-2 ..."
>

// Sidebar panel (line ~492) - Note the conditional transform class
<div className={`lg:hidden fixed top-0 right-0 h-full w-80 z-40 
  ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'}`}
>

// Backdrop (line ~685)
{sidebarOpen && (
  <div
    className="lg:hidden fixed inset-0 bg-black/60 z-30"
    onClick={() => setSidebarOpen(false)}
  />
)}
```

### Required CSS File Import

In `client/src/main.jsx`:

```jsx
import './styles/index.css';
import './styles/theme-overrides.css';  // CRITICAL for mobile sidebar
```

---

## 11. Puck Editor Integration

### Puck Component Structure

```jsx
// themes/[theme]/puck/index.jsx

export const CelestialHero = {
  label: 'Celestial Hero',
  
  fields: {
    variant: {
      type: 'select',
      label: 'Style Variant',
      options: [
        { label: 'Full Width', value: 'fullWidth' },
        { label: 'Split Layout', value: 'split' },
      ]
    },
    title: { type: 'text', label: 'Title' },
    subtitle: { type: 'textarea', label: 'Subtitle' },
  },
  
  defaultProps: {
    variant: 'fullWidth',
    title: 'Welcome',
    subtitle: 'Discover transformative teaching',
  },
  
  render: ({ variant, title, subtitle }) => (
    <section className="min-h-[70vh] flex items-center justify-center">
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </section>
  )
};
```

### Important: JSX Files Must Use .jsx Extension

Vite's `import.meta.glob` doesn't parse JSX in `.js` files.

```javascript
// ❌ WRONG
import.meta.glob('@themes/*/puck/index.js');

// ✅ CORRECT
import.meta.glob('@themes/*/puck/index.jsx');
```

---

## 12. Production Build Requirements

### ⚠️ CRITICAL: Mandatory Vite Configuration

**IMPORTANT:** The following configurations are REQUIRED for theme compilation. Missing ANY of these will cause production build failures or runtime errors.

📄 **Complete details:** See [THEME_VITE_REQUIREMENTS.md](./THEME_VITE_REQUIREMENTS.md)

### Quick Checklist (Verify Your vite.config.js Has ALL of These)

- [ ] **React plugin includes themes folder** - JSX transform for theme files
- [ ] **React modules aliased to client** - Prevents multiple React instances
- [ ] **CommonJS options include themes** - Production build resolution
- [ ] **File system allows themes folder** - Dev server access

### 1. React Plugin Configuration (CRITICAL)

```javascript
// client/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

const themesDir = path.resolve(__dirname, '../themes')

export default defineConfig({
  plugins: [react({
    // ⚠️ CRITICAL: Include themes folder in React JSX transform
    include: [
      /\.[jt]sx?$/,
      new RegExp(themesDir.replace(/\\/g, '\\\\') + '.*\\.[jt]sx?$')
    ]
  })],
})
```

**Without this:** `Failed to parse source for import analysis because the content contains invalid JS syntax`

### 2. React Module Aliasing (CRITICAL)

```javascript
export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@themes': path.resolve(__dirname, '../themes'),

      // ⚠️ CRITICAL: Force themes to use client's React modules
      'react': path.resolve(__dirname, 'node_modules/react'),
      'react/jsx-runtime': path.resolve(__dirname, 'node_modules/react/jsx-runtime'),
      'react-dom': path.resolve(__dirname, 'node_modules/react-dom')
    }
  }
})
```

**Without this:** `Invalid hook call. Hooks can only be called inside the body of a function component`

### 3. CommonJS Options (CRITICAL)

```javascript
export default defineConfig({
  build: {
    commonjsOptions: {
      include: [/themes/, /node_modules/]
    }
  }
})
```

**Without this:** Production builds may fail with module resolution errors

### 4. File System Access

```javascript
export default defineConfig({
  server: {
    fs: {
      allow: ['..'],  // Allow themes folder outside client
    },
  },
});
```

**Without this:** `The request url "/themes/..." is outside of Vite serving allow list`

### Server Static File Serving

Theme CSS files are NOT bundled - they're loaded at runtime:

```javascript
// server/app.js
app.use('/themes', express.static(path.join(__dirname, '../themes')));
```

### Build Verification

After `npm run build`, verify critical classes:

```bash
# Check lg:hidden is in CSS
grep "lg.hidden" dist/assets/index*.css

# Should output something like:
# @media(min-width:1024px){.lg\:hidden{display:none!important}}
```

---

## 13. Fatal Mistakes to Avoid

### Fatal Mistake #1: Using Next.js styled-jsx

```jsx
// ❌ WRONG - styled-jsx doesn't work in Vite/React
<style jsx>{`.my-class { color: blue; }`}</style>

// ✅ CORRECT - Use CSS file or inline styles
<div style={{ color: 'blue' }}>
```

### Fatal Mistake #2: Importing NPM Packages

```jsx
// ❌ WRONG - Crashes production build
import { Link } from 'react-router-dom';
import axios from 'axios';

// ✅ CORRECT - Use compatibility layer
const Link = ({ to, children }) => <a href={to}>{children}</a>;
// Use fetch() instead of axios
```

### Fatal Mistake #3: Path Alias Imports

```jsx
// ❌ WRONG - Can't resolve path aliases from themes folder
import { useTheme } from '@/context/ThemeContext';

// ✅ CORRECT - Use window globals
const useThemeSettings = () => {
  const [settings, setSettings] = useState({});
  useEffect(() => {
    if (window.__LMS_THEME_SETTINGS__) {
      setSettings(window.__LMS_THEME_SETTINGS__);
    }
  }, []);
  return { settings };
};
```

### Fatal Mistake #4: CSS Resets in Theme Files

```css
/* ❌ WRONG - Breaks Tailwind utilities */
* { margin: 0; padding: 0; }

/* ✅ CORRECT - Only box-sizing */
* { box-sizing: border-box; }
```

### Fatal Mistake #5: Missing lg:hidden on Mobile Sidebar

```jsx
// ❌ WRONG - Sidebar shows on desktop
<div className="fixed top-0 right-0">

// ✅ CORRECT - Hidden on desktop
<div className="lg:hidden fixed top-0 right-0">
```

### Fatal Mistake #6: Relying on Tailwind Scanning Alone

```css
/* ❌ WRONG - May not work in production */
@source "../../themes";

/* ✅ CORRECT - Add manual fallback */
@source "../../themes";
@media (min-width: 1024px) {
  .lg\:hidden { display: none !important; }
}
```

### Fatal Mistake #7: Missing Transform Classes for Mobile Sidebar

```jsx
// ❌ WRONG - Sidebar visible on page load (translate-x-full not compiled)
<div className={`fixed ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'}`}>

// ✅ CORRECT - Requires CSS fallback in theme-overrides.css
// Add to client/src/styles/theme-overrides.css:
// .translate-x-full { transform: translateX(100%) !important; }
// .translate-x-0 { transform: translateX(0) !important; }
```

### Fatal Mistake #8: Link Component Without Navigation Delay

```jsx
// ❌ WRONG - Sidebar stays open because page navigates immediately
const Link = ({ to, children, onClick }) => (
    <a href={to} onClick={onClick}>{children}</a>
);

// ✅ CORRECT - Delay navigation to allow sidebar close
const Link = ({ to, children, onClick }) => {
    const handleClick = (e) => {
        if (onClick) onClick(e);
        if (to && !to.startsWith('http')) {
            e.preventDefault();
            setTimeout(() => { window.location.href = to; }, 100);
        }
    };
    return <a href={to} onClick={handleClick}>{children}</a>;
};
```

---

## 14. AI Agent Theme Generation Checklist

**MANDATORY for AI agents generating themes. Verify BEFORE output.**

### Package.json Requirements

**Required Minimum Versions:**

- [ ] `"react": "^18.3.1"` - JSX transform compatibility
- [ ] `"react-dom": "^18.3.1"` - React rendering
- [ ] `"tailwindcss": "^4.1.13"` - CSS v4 import syntax
- [ ] `"@tailwindcss/postcss": "^4.1.13"` - PostCSS plugin
- [ ] `"@vitejs/plugin-react": "^5.0.3"` - Theme folder JSX transform
- [ ] `"vite": "^7.1.2"` - External folder support

**Critical:** Tailwind v3 will NOT work - must be v4.1.13+ for `@import "tailwindcss"` syntax.

### Vite Configuration Requirements

- [ ] React plugin includes themes folder in `include` array
- [ ] React modules aliased to client's node_modules (prevents "multiple React instances" error)
- [ ] CommonJS options include `/themes/` pattern
- [ ] File system allows parent directory (`..`)

📄 **See:** [THEME_VITE_REQUIREMENTS.md](./THEME_VITE_REQUIREMENTS.md) for complete configuration details.

### Component Compatibility

- [ ] **NO npm package imports** - No react-router-dom, react-redux, axios
- [ ] **NO path alias imports** - No `from '@/`
- [ ] **Uses local Link component with navigation delay** - See Fatal Mistake #8
- [ ] **Uses useAuth() hook** - Reads from `window.__LMS_AUTH__`
- [ ] **Uses useThemeSettings() hook** - Reads from `window.__LMS_THEME_SETTINGS__`
- [ ] **Uses performLogout()** - fetch + localStorage, not Redux
- [ ] **Uses fetch() for API calls** - NOT axios

### theme.json Requirements

- [ ] Has `name`, `displayName`, `version`, `description`
- [ ] `colors` object at ROOT level (NOT under `themeSettings`)
- [ ] All 8 color keys: primary, secondary, accent, background, surface, text, muted, border
- [ ] Color values are HEX STRINGS like `"#4F46E5"`

### theme.css Requirements

- [ ] Contains ONLY `* { box-sizing: border-box; }`
- [ ] NO `margin: 0` or `padding: 0` on universal selector
- [ ] NO CSS reset imports

### File Structure

- [ ] `theme.json` at root
- [ ] `styles/theme.css` exists
- [ ] `components/index.js` exists
- [ ] `preview.png` is real image (NOT placeholder)
- [ ] NO `index.jsx` or `screenshot.png`

### Mobile Sidebar (ALL REQUIRED)

- [ ] Toggle button has `lg:hidden`
- [ ] Sidebar panel has `lg:hidden`  
- [ ] Backdrop has `lg:hidden`
- [ ] State initialized to `false`: `useState(false)`
- [ ] Uses `translate-x-full` / `translate-x-0` for slide animation
- [ ] Link component delays navigation by 100ms (allows sidebar to close)

---

## 15. Testing & Deployment

### Local Testing

```bash
# 1. Start development server
cd client && npm run dev

# 2. Set theme in browser console
localStorage.setItem('activeTheme', 'my-theme');
location.reload();

# 3. Check console for theme loading
# Should see: [ThemeManager] Loaded X component overrides
```

### Production Build Testing

```bash
# 1. Build
cd client && npm run build

# 2. Verify lg:hidden in CSS
grep "min-width.*1024.*hidden" dist/assets/index*.css

# 3. Test with preview server
npm run preview
```

### Deployment Checklist

```bash
# SSH to server
ssh user@server

# Pull latest
cd ~/mern-app && git pull

# Build
cd client && npm run build

# Copy to public_html
/bin/cp -rf dist/* ~/public_html/

# Restart server
pm2 restart all

# Verify CSS on server
grep "lg.hidden" ~/public_html/assets/index*.css
```

---

## 16. Reference: Celestial Theme

The Celestial theme (`themes/celestial/`) is the reference implementation:

```
celestial/
├── theme.json              # Complete manifest
├── preview.png             # Theme preview
├── components/
│   ├── index.js            # Exports Header, Footer, Hero
│   └── layout/
│       ├── Header.jsx      # Complete compatibility layer implementation
│       └── Footer.jsx      # Same pattern
├── puck/
│   └── index.jsx           # Puck components
└── styles/
    └── theme.css           # Theme styles (no CSS reset)
```

### Key Files to Study

1. **Header.jsx** - Lines 1-100 contain the complete compatibility layer
2. **Header.jsx** - Lines 470, 492, 685 show `lg:hidden` pattern
3. **Header.jsx** - Link component with navigation delay (lines 24-40)
4. **theme.json** - Shows correct color and typography structure
5. **theme.css** - Shows proper CSS without resets

### Critical CSS Files

1. **client/src/styles/index.css** - Tailwind v4 config with `@source` directive
2. **client/src/styles/theme-overrides.css** - Manual CSS fallbacks for:
   - `lg:hidden` responsive class
   - `translate-x-full` / `translate-x-0` transform classes
   - Other critical classes that must work in production

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-09-30 | Initial theme system |
| 2.0.0 | 2026-01-17 | WordPress-style component overrides |
| 3.0.0 | 2026-01-18 | Tailwind v4 production fix, manual CSS fallbacks |
| 3.1.0 | 2026-01-18 | Mobile sidebar complete fix: transform classes, Link navigation delay |
| 3.2.0 | 2026-01-18 | **Added critical Vite configuration requirements and package.json dependencies** |

---

*This document is the single source of truth for theme development. When in doubt, test in production.*
