# WordPress-Style Theme Component System - Complete Implementation Guide

**Created:** January 17, 2026
**Updated:** January 18, 2026
**Status:** ✅ COMPLETE & TESTED

> ⚠️ **IMPORTANT**: This document is now SUPERSEDED by the comprehensive guide:
> **`docs/THEME_COMPLETE_DEVELOPER_GUIDE.md`** - Single Source of Truth for theme development
>
> This file is kept for reference but the new guide includes all content plus:
> - Tailwind CSS v4 production fixes
> - Manual CSS fallback requirements
> - Updated deployment procedures

---

## 🎯 Problem Statement

**Challenge:** Traditional theme systems only change colors/fonts - need WordPress-style complete UI transformation
**Goal:** Allow themes to override ANY component (Header, Footer, Hero, etc.) without modifying core code
**Solution:** Dynamic component loading with theme-specific overrides via a centralized ThemeManager

---

## 🏗️ Architecture Overview

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

---

## 📁 File Structure

```
project-root/
├── client/
│   ├── src/
│   │   ├── services/
│   │   │   └── ThemeManager.js        # Core theme loading logic
│   │   ├── contexts/
│   │   │   └── ThemeContext.jsx       # React context for themes
│   │   ├── layouts/
│   │   │   └── MainLayout.jsx         # Uses component resolver
│   │   └── components/
│   │       └── layout/
│   │           ├── Header.jsx         # Default Header
│   │           └── Footer.jsx         # Default Footer
│   └── vite.config.js                 # Alias and fs.allow config
│
└── themes/
    └── celestial/                     # Example theme
        ├── theme.json                 # Theme metadata
        ├── components/
        │   ├── index.js               # Component exports (CRITICAL)
        │   └── layout/
        │       ├── Header.jsx         # Theme-specific Header
        │       └── Footer.jsx         # Theme-specific Footer
        ├── puck/
        │   └── index.jsx              # Puck editor components
        └── styles/
            └── theme.css              # CSS variables & animations
```

---

## 🔧 Core Implementation

### 1. Vite Configuration (vite.config.js)

**CRITICAL:** Themes live outside `client/src`, so Vite needs special config:

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      // CRITICAL: Alias for themes folder
      '@themes': path.resolve(__dirname, '../themes'),
    },
  },
  server: {
    fs: {
      // CRITICAL: Allow Vite to serve files from themes folder
      allow: ['..'],
    },
    proxy: {
      // Optional: Serve theme assets
      '/themes': {
        target: 'http://localhost:5173',
        rewrite: (path) => path.replace(/^\/themes/, '/../themes'),
      },
    },
  },
});
```

### 2. ThemeManager Service (ThemeManager.js)

```javascript
class ThemeManager {
  constructor() {
    this.currentTheme = null;
    this.themeConfig = null;
    this.componentOverrides = new Map();
  }

  // Dynamic imports using Vite's import.meta.glob
  async loadThemeComponents(themeName) {
    try {
      // Use @themes alias to access themes folder
      const themeModules = import.meta.glob('@themes/*/components/index.js');
      const modulePath = `../themes/${themeName}/components/index.js`;
      
      // Find the matching module path (glob returns relative to project root)
      const matchingKey = Object.keys(themeModules).find(key => 
        key.includes(`/${themeName}/components/index.js`)
      );

      if (matchingKey && themeModules[matchingKey]) {
        const module = await themeModules[matchingKey]();
        
        // Register each exported component
        if (module.Header) this.componentOverrides.set('Header', module.Header);
        if (module.Footer) this.componentOverrides.set('Footer', module.Footer);
        if (module.Hero) this.componentOverrides.set('Hero', module.Hero);
        
        console.log(`[ThemeManager] Loaded ${this.componentOverrides.size} component overrides`);
      }
    } catch (error) {
      console.warn(`[ThemeManager] No components found for theme: ${themeName}`, error);
    }
  }

  // Get component with fallback to default
  getComponent(componentName) {
    return this.componentOverrides.get(componentName) || null;
  }

  // Load Puck editor components (MUST use .jsx extension)
  async loadPuckComponents(themeName) {
    const puckModules = import.meta.glob('@themes/*/puck/index.jsx');
    // ... similar pattern
  }
}

export const themeManager = new ThemeManager();
export default themeManager;
```

### 3. Theme Context (ThemeContext.jsx)

```javascript
import React, { createContext, useContext, useState, useEffect } from 'react';
import themeManager from '../services/ThemeManager';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initTheme = async () => {
      // Load from localStorage or API
      const savedTheme = localStorage.getItem('activeTheme') || 'default';
      await themeManager.loadTheme(savedTheme);
      setTheme(themeManager.themeConfig);
      setLoading(false);
    };
    initTheme();
  }, []);

  // CRITICAL: This is what components use to get overridden components
  const getComponent = (componentName) => {
    return themeManager.getComponent(componentName);
  };

  return (
    <ThemeContext.Provider value={{ theme, loading, getComponent, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);
```

### 4. MainLayout with Component Resolver (MainLayout.jsx)

```javascript
import React, { Suspense } from 'react';
import { useTheme } from '../contexts/ThemeContext';

// Default components (fallbacks)
import DefaultHeader from '../components/layout/Header';
import DefaultFooter from '../components/layout/Footer';

const MainLayout = ({ children }) => {
  const { getComponent } = useTheme();
  
  // CRITICAL: Resolve components with fallback
  const Header = getComponent('Header') || DefaultHeader;
  const Footer = getComponent('Footer') || DefaultFooter;

  return (
    <div className="min-h-screen flex flex-col">
      {/* CRITICAL: Suspense handles lazy-loaded theme components */}
      <Suspense fallback={<div className="h-16 bg-gray-100 animate-pulse" />}>
        <Header />
      </Suspense>
      
      <main className="flex-1">
        {children}
      </main>
      
      <Suspense fallback={<div className="h-64 bg-gray-100 animate-pulse" />}>
        <Footer />
      </Suspense>
    </div>
  );
};

export default MainLayout;
```

### 5. Theme Component Exports (themes/celestial/components/index.js)

**CRITICAL:** This file is what ThemeManager loads - exports must match expected names:

```javascript
// Re-export all theme components
export { default as Header } from './layout/Header';
export { default as Footer } from './layout/Footer';
export { default as Hero } from './Hero';

// Export metadata for discovery
export const themeComponents = {
  Header: { description: 'Luxury transparent-to-solid header' },
  Footer: { description: 'Four-column footer with gold accents' },
  Hero: { description: 'Multiple hero variants with animations' },
};
```

---

## 🚨 Critical Gotchas & Solutions

### 1. JSX Files Must Use .jsx Extension

**Problem:** Vite's `import.meta.glob` doesn't parse JSX in `.js` files

**Error:**
```
[vite] Internal server error: Failed to parse source for import analysis 
because the content contains invalid JS syntax. If you are using JSX, 
make sure to name the file with the .jsx extension.
```

**Solution:** 
- Rename files with JSX to `.jsx`
- Update glob pattern: `import.meta.glob('@themes/*/puck/index.jsx')`

### 2. External vs Internal Links in Theme Components

**Problem:** Using `<Link to="/external-url">` breaks for external URLs

**Solution:** Create helper functions:

```javascript
const isExternalLink = (url) => {
  if (!url) return false;
  return url.startsWith('http://') || 
         url.startsWith('https://') || 
         url.startsWith('//');
};

// In render:
{isExternalLink(item.url) ? (
  <a href={item.url} target="_blank" rel="noopener noreferrer">
    {item.label}
  </a>
) : (
  <Link to={item.url}>{item.label}</Link>
)}
```

### 3. Dashboard Route Paths

**Problem:** Links like `/my-courses` get caught by CMS PageRenderer, causing 404

**Solution:** Use full dashboard paths:
```javascript
// ❌ WRONG - caught by CMS
<Link to="/my-courses">My Courses</Link>

// ✅ CORRECT - matches React Router
<Link to="/dashboard/my-courses">My Courses</Link>
```

**Standard dashboard routes:**
- `/dashboard` - Main dashboard
- `/dashboard/my-courses` - Enrolled courses
- `/dashboard/orders` - Order history
- `/dashboard/settings` - User settings

### 4. Vite fs.allow Error

**Problem:** Vite refuses to serve files outside project root

**Error:**
```
The request url "/themes/celestial/..." is outside of Vite serving allow list.
```

**Solution:** Add to vite.config.js:
```javascript
server: {
  fs: {
    allow: ['..'],  // Allow parent directory
  },
}
```

### 5. Dynamic Import Path Resolution

**Problem:** `import.meta.glob` paths must be statically analyzable

**Solution:** Use the alias in glob pattern:
```javascript
// ✅ WORKS - Vite can analyze at build time
const modules = import.meta.glob('@themes/*/components/index.js');

// ❌ FAILS - Dynamic string
const themeName = 'celestial';
const modules = import.meta.glob(`@themes/${themeName}/components/index.js`);
```

### 6. CSS Cascade Layers & Tailwind v4 Conflict (CRITICAL)

**Problem:** Theme CSS universal selectors override Tailwind utility classes

**Background:** Tailwind CSS v4 uses CSS `@layer` directives (base, components, utilities). In CSS Cascade Layers, **unlayered CSS has HIGHER precedence than layered CSS**, regardless of specificity.

**Symptoms:**
- `mx-auto` doesn't center content (computed margin is `0px` instead of `auto`)
- `px-*`, `py-*` padding utilities are ignored
- Content appears left-aligned instead of centered
- Tailwind classes seem to have no effect

**Root Cause:**
```css
/* ❌ BAD - Theme CSS (unlayered) */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
```

This unlayered CSS **beats** Tailwind's layered `.mx-auto { margin-left: auto; margin-right: auto; }` even though `.mx-auto` has higher specificity than `*`.

**Solution:**
```css
/* ✅ GOOD - Only keep box-sizing, let Tailwind's Preflight handle resets */
* {
  box-sizing: border-box;
}

/* Note: Tailwind's Preflight (in @layer base) provides proper CSS reset */
```

**Debug Steps:**
1. Check computed styles in DevTools - if `marginLeft: 0px` on elements with `mx-auto` class
2. Search theme CSS for `* {` or universal selectors with `margin` or `padding`
3. Remove `margin: 0` and `padding: 0` from universal selectors
4. Test centering works after change

**Prevention:** Never use CSS resets in theme files - Tailwind's Preflight handles this. Only use specific selectors in theme CSS.

---

## 🤖 AI Agent Theme Generation Checklist

**MANDATORY for AI agents generating themes. Verify BEFORE output.**

### ⚠️ CRITICAL: Component Compatibility Layer (CHECK FGTAT)

This is the **#1 cause of production build failures**. Theme components live OUTSIDE the client workspace, so Vite/Rollup CANNOT resolve npm packages or path aliases.

- [ ] **NO npm package imports** - Search for `from 'react-router-dom'`, `from 'react-redux'`, `from 'axios'`
- [ ] **NO path alias imports** - Search for `from '@/`
- [ ] **Uses local Link component** - `const Link = ({ to, children }) => <a href={to}>{children}</a>;`
- [ ] **Uses useAuth() hook** - Reads from `window.__LMS_AUTH__` global
- [ ] **Uses useThemeSettings() hook** - Reads from `window.__LMS_THEME_SETTINGS__` global
- [ ] **Uses performLogout()** - fetch + localStorage, not Redux dispatch
- [ ] **Uses fetch() for API calls** - NOT axios

### theme.json Requirements
- [ ] Has `name` (lowercase-slug), `displayName`, `version`, `description`
- [ ] `colors` object at ROOT level (NOT under `themeSettings`)
- [ ] All 8 color keys present: `primary`, `secondary`, `accent`, `background`, `surface`, `text`, `muted`, `border`
- [ ] Color values are HEX STRINGS like `"#4F46E5"` (NOT objects)
- [ ] NO `themeSettings`, `entryPoint`, `screenshot`, or `supports` array

### theme.css Requirements
- [ ] Contains ONLY `* { box-sizing: border-box; }`
- [ ] NO `margin: 0` or `padding: 0` on universal selector
- [ ] NO CSS reset imports (normalize.css, reset.css)
- [ ] NO `html, body { margin: 0; padding: 0; }`

### File Structure Requirements
- [ ] `theme.json` at root
- [ ] `styles/theme.css` exists
- [ ] `components/index.js` exists (can export empty object)
- [ ] `preview.png` is real 400x300 image (NOT 1x1 placeholder)
- [ ] NO `index.jsx` file
- [ ] NO `screenshot.png` file

---

## 📋 Theme Component Checklist

When creating a new theme component:

- [ ] **Include compatibility layer** at top of file (useAuth, useThemeSettings, Link with navigation delay, performLogout)
- [ ] Create in `themes/[theme-name]/components/` folder
- [ ] Use `.jsx` extension if file contains JSX
- [ ] Export from `components/index.js`
- [ ] Match export name to expected component (Header, Footer, Hero)
- [ ] Use local `<Link>` wrapper with 100ms setTimeout delay, NOT react-router-dom Link
- [ ] Use `fetch()` for API calls, NOT axios

**Mobile Sidebar (6 Requirements):**
- [ ] **`lg:hidden` on toggle button** - Hamburger menu hidden on desktop
- [ ] **`lg:hidden` on sidebar panel** - Slide-out menu hidden on desktop
- [ ] **`lg:hidden` on backdrop** - Dark overlay hidden on desktop
- [ ] **Transform classes** - `translate-x-full` and `translate-x-0` in component
- [ ] **Navigation delay** - Link component has 100ms setTimeout before window.location.href
- [ ] **Initial state** - `useState(false)` for sidebar closed on load

**Build & Test:**
- [ ] Test with React.Suspense for lazy loading
- [ ] Include responsive design (mobile sidebar, etc.)
- [ ] **Test production build** - Run `npm run build` to verify no resolution errors
- [ ] **Verify on both desktop and mobile** - No duplicate menus, sidebar closes on link click

---

## ⚙️ Tailwind Content Configuration (CRITICAL)

Theme files in `/themes/` folder are **outside** the default Tailwind scan path. Without proper config, theme Tailwind classes get **purged** in production!

```javascript
// client/tailwind.config.js - MUST include themes folder
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,css}",
    "../themes/**/*.{js,jsx,ts,tsx}",  // ✅ CRITICAL!
  ],
};
```

**Symptoms of missing config:**
- `lg:hidden` doesn't hide elements on desktop
- Responsive classes work in dev but break in production
- Mobile sidebar visible on all screen sizes

---

## 📱 Mobile Sidebar Responsiveness (CRITICAL)

### The 4 Mobile Sidebar Requirements

When implementing mobile slide-out navigation, you MUST follow these 4 requirements to ensure proper functionality:

#### 1. Three Elements Rule - ALL need `lg:hidden`

**ALL THREE elements must have `lg:hidden`** class:

```jsx
{/* 1. Toggle button - MUST have lg:hidden */}
<button
  className="lg:hidden p-2"
  onClick={() => setSidebarOpen(!sidebarOpen)}
  aria-label="Toggle navigation"
>
  <MenuIcon />
</button>

{/* 2. Sidebar panel - MUST have lg:hidden */}
<div className={`lg:hidden fixed top-0 right-0 h-full z-40 transition-transform duration-300 ${
  sidebarOpen ? 'translate-x-0' : 'translate-x-full'
}`}>
  {/* sidebar content with links */}
</div>

{/* 3. Backdrop overlay - MUST have lg:hidden */}
{sidebarOpen && (
  <div
    className="lg:hidden fixed inset-0 z-30 bg-black/50"
    onClick={() => setSidebarOpen(false)}
  />
)}
```

#### 2. CSS Transform Fallbacks (Tailwind v4)

**CRITICAL:** Tailwind v4 may not compile transform classes for themes folder. Add manual fallbacks:

```css
/* client/src/styles/theme-overrides.css */
.translate-x-full {
  transform: translateX(100%) !important;
}

.translate-x-0 {
  transform: translateX(0) !important;
}

.-translate-x-full {
  transform: translateX(-100%) !important;
}

/* Also add in client/src/styles/index.css for desktop responsiveness */
@media (min-width: 1024px) {
  .lg\:hidden {
    display: none !important;
  }
}
```

**Import in main.jsx:**
```javascript
import './styles/index.css';
import './styles/theme-overrides.css';  // Add this
```

#### 3. Link Navigation Delay (Sidebar Closing Issue)

**Problem:** Clicking menu links didn't close sidebar because browser navigated before `setSidebarOpen(false)` could execute.

**Solution:** Modified Link component with 100ms delay:

```javascript
const Link = ({ to, children, className, style, onClick }) => {
  const handleClick = (e) => {
    // Call any custom onClick handler
    if (onClick) onClick(e);

    // For internal links, delay navigation to allow sidebar to close
    if (to && !to.startsWith('http') && !to.startsWith('//')) {
      e.preventDefault();
      setTimeout(() => {
        window.location.href = to;
      }, 100);
    }
    // External links navigate immediately (no preventDefault)
  };

  return (
    <a
      href={to}
      className={className}
      style={style}
      onClick={handleClick}
    >
      {children}
    </a>
  );
};
```

**Usage in sidebar links:**
```jsx
<Link
  to="/courses"
  className="block py-2"
  onClick={() => setSidebarOpen(false)}  // This now has time to execute
>
  Courses
</Link>
```

#### 4. State Initialization

```javascript
const [sidebarOpen, setSidebarOpen] = useState(false);  // Starts closed
```

### Common Mistakes & Solutions

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Missing `lg:hidden` on toggle | Hamburger menu shows on desktop | Add `lg:hidden` to button |
| Missing `lg:hidden` on panel | Sidebar visible on desktop | Add `lg:hidden` to sidebar div |
| Missing `lg:hidden` on backdrop | Dark overlay on desktop | Add `lg:hidden` to backdrop div |
| No transform fallback | Sidebar visible on page load (mobile) | Add `translate-x-full` CSS to theme-overrides.css |
| No navigation delay | Sidebar doesn't close on link click | Add 100ms setTimeout in Link onClick |
| Wrong initial state | Sidebar open on page load | Set `useState(false)` |

### Tailwind CSS v4 Key Differences

**IMPORTANT:** This project uses Tailwind CSS v4.1.13, which has different configuration:

- Uses `@import "tailwindcss"` (NOT `@tailwind base/components/utilities`)
- Content scanning via `@source` directive in CSS (NOT `tailwind.config.js`)
- `@source` may NOT reliably scan external folders like `/themes/`
- **Always add manual CSS fallbacks** for critical responsive classes

```css
/* client/src/styles/index.css */
@import "tailwindcss";

/* Tell Tailwind to scan themes folder */
@source "../../themes";

/* CRITICAL: Manual fallback for lg:hidden */
@media (min-width: 1024px) {
  .lg\:hidden { display: none !important; }
}
```

### Testing Checklist

- [ ] Desktop (≥1024px): Only horizontal nav visible, no hamburger menu
- [ ] Mobile (<1024px): Only hamburger menu visible, no horizontal nav
- [ ] Mobile sidebar starts closed on page load
- [ ] Clicking hamburger opens sidebar with smooth slide-in
- [ ] Clicking backdrop closes sidebar
- [ ] Clicking link closes sidebar THEN navigates
- [ ] Sidebar doesn't flash visible on desktop
- [ ] Build succeeds without errors (`npm run build`)

### Reference Implementation

**See:** `themes/celestial/components/layout/Header.jsx` for complete working example.

**Why this matters:**
- Desktop (≥1024px) already has horizontal nav in `<nav className="hidden lg:flex">`
- Mobile sidebar without `lg:hidden` creates duplicate navigation
- Confusing UX with two menus visible
- Transform classes need manual fallbacks for Tailwind v4

---

## 🧪 Testing Theme Components

### Manual Test Steps

1. **Set active theme:**
   ```javascript
   localStorage.setItem('activeTheme', 'celestial');
   location.reload();
   ```

2. **Check browser console:**
   ```
   [ThemeManager] Loading theme: celestial
   [ThemeManager] Loaded 3 component overrides
   ```

3. **Verify component replacement:**
   - Open React DevTools
   - Find MainLayout
   - Confirm Header/Footer are from theme folder

### Quick Debug Commands

```javascript
// In browser console:
import.meta.glob('@themes/*/components/index.js')  // See available themes
themeManager.componentOverrides  // See registered overrides
```

---

## 📝 Example: Creating a New Theme

### Step 1: Create folder structure
```
themes/
└── my-theme/
    ├── theme.json
    ├── components/
    │   ├── index.js
    │   └── layout/
    │       └── Header.jsx
    └── styles/
        └── theme.css
```

### Step 2: Create theme.json

**⚠️ CRITICAL FOR AI AGENTS: Follow this EXACT format. Common mistakes break theme installation.**

#### Required Fields (ALL mandatory):
| Field | Format | Example |
|-------|--------|---------|
| `name` | lowercase-slug | `"my-theme"` |
| `displayName` | Human readable | `"My Theme"` |
| `version` | Semantic | `"1.0.0"` |
| `description` | String | `"A custom theme"` |
| `colors` | Object at ROOT level | See below |

#### Colors Object - MUST be at ROOT level with ALL 8 keys:
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

#### ❌ DO NOT use these patterns:
- `themeSettings.colors` - WRONG, use `colors` at root
- `{ "primary": { "default": "#..." } }` - WRONG, use simple hex strings
- `entryPoint`, `screenshot`, `supports` array - NOT USED

#### Complete theme.json Example:
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

### Step 3: Create components/index.js
```javascript
export { default as Header } from './layout/Header';
// Add more exports as needed
```

### Step 4: Create Header.jsx (WITH COMPATIBILITY LAYER)

> **⚠️ CRITICAL:** Theme components CANNOT import npm packages or path aliases.
> This is the #1 cause of production build failures.

```javascript
import React, { useState, useEffect } from 'react';  // ✅ React is aliased

/**
 * THEME COMPATIBILITY LAYER - Required for ALL theme components
 * 
 * Theme files live OUTSIDE client workspace, so Vite/Rollup cannot resolve:
 * - npm packages (react-router-dom, react-redux, axios)
 * - path aliases (@/store, @/context)
 */

// ❌ FORBIDDEN - These will break production builds:
// import { Link } from 'react-router-dom';
// import { useSelector } from 'react-redux';
// import axios from 'axios';
// import { useTheme } from '@/context/ThemeContext';

// ✅ Local Link component
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
        if (window.__LMS_AUTH__) {
            setAuth(window.__LMS_AUTH__);
        } else {
            const token = localStorage.getItem('token');
            const user = localStorage.getItem('user');
            setAuth({ isAuthenticated: !!token, user: user ? JSON.parse(user) : null });
        }
        const handler = () => { /* re-check auth */ };
        window.addEventListener('auth-change', handler);
        return () => window.removeEventListener('auth-change', handler);
    }, []);
    return auth;
};

// ✅ Theme settings from window global
const useThemeSettings = () => {
    const [settings, setSettings] = useState({});
    useEffect(() => {
        if (window.__LMS_THEME_SETTINGS__) setSettings(window.__LMS_THEME_SETTINGS__);
    }, []);
    return { settings };
};

// ✅ Logout using fetch (not axios + redux dispatch)
const performLogout = async () => {
    try { await fetch('/api/auth/logout', { method: 'POST' }); } catch(e) {}
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
};

// Now the actual component:
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
        <header className="your-custom-styles">
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

**Reference:** See `themes/celestial/components/layout/Header.jsx` for complete implementation.

### Step 5: Test
```javascript
localStorage.setItem('activeTheme', 'my-theme');
location.reload();
```

---

## 🔗 Related Files in This Project

- [client/src/services/ThemeManager.js](../../client/src/services/ThemeManager.js)
- [client/src/contexts/ThemeContext.jsx](../../client/src/contexts/ThemeContext.jsx)
- [client/src/layouts/MainLayout.jsx](../../client/src/layouts/MainLayout.jsx)
- [client/vite.config.js](../../client/vite.config.js)
- [themes/celestial/](../../themes/celestial/)

---

## 📚 Key Concepts

| Concept | Description |
|---------|-------------|
| **Component Override** | Theme provides replacement for core component |
| **Fallback Pattern** | `getComponent('X') \|\| DefaultX` |
| **Lazy Loading** | Theme components loaded via `import.meta.glob` |
| **Suspense Boundary** | React.Suspense wraps lazy components |
| **Alias Resolution** | `@themes` → `../themes` in Vite config |

---

## 🔌 Puck Editor Integration

Theme-specific Puck components allow the page builder to use themed blocks.

### Puck Component Structure (themes/[theme]/puck/index.jsx)

```jsx
/**
 * Each Puck component export is an object with:
 * - label: Display name in Puck sidebar
 * - fields: Form fields for the editor
 * - defaultProps: Initial values
 * - render: React component to render
 */
export const CelestialHero = {
  label: 'Celestial Hero',
  
  // Field definitions for the Puck editor sidebar
  fields: {
    variant: {
      type: 'select',
      label: 'Style Variant',
      options: [
        { label: 'Full Width with Overlay', value: 'fullWidth' },
        { label: 'Split Layout', value: 'split' },
        { label: 'Minimal Centered', value: 'minimal' }
      ]
    },
    title: {
      type: 'text',
      label: 'Title'
    },
    subtitle: {
      type: 'textarea',
      label: 'Subtitle'
    },
    backgroundImage: {
      type: 'text',
      label: 'Background Image URL'
    },
    primaryButtonText: {
      type: 'text',
      label: 'Primary Button Text'
    },
    primaryButtonLink: {
      type: 'text',
      label: 'Primary Button Link'
    }
  },
  
  // Default values when component is first added
  defaultProps: {
    variant: 'fullWidth',
    title: 'Welcome to Our Ministry',
    subtitle: 'Discover transformative teaching',
    backgroundImage: '',
    primaryButtonText: 'Get Started',
    primaryButtonLink: '/register'
  },
  
  // The actual React component
  render: ({ variant, title, subtitle, backgroundImage, primaryButtonText, primaryButtonLink }) => {
    return (
      <section className="min-h-[70vh] flex items-center justify-center">
        <h1>{title}</h1>
        <p>{subtitle}</p>
        <a href={primaryButtonLink}>{primaryButtonText}</a>
      </section>
    );
  }
};

// Export more components...
export const CelestialCard = { /* ... */ };
export const CelestialButton = { /* ... */ };
```

### Accessing Puck Components in ThemeContext

```javascript
// ThemeContext provides getPuckComponents()
const { getPuckComponents } = useTheme();

// Returns merged object of all theme Puck components
const themePuckComponents = getPuckComponents();

// Use in Puck editor config
const puckConfig = {
  components: {
    ...defaultComponents,
    ...themePuckComponents  // Theme components override/extend defaults
  }
};
```

### Puck Field Types Reference

| Type | Description | Options |
|------|-------------|---------|
| `text` | Single line input | - |
| `textarea` | Multi-line input | - |
| `number` | Numeric input | `min`, `max`, `step` |
| `select` | Dropdown | `options: [{ label, value }]` |
| `radio` | Radio buttons | `options: [{ label, value }]` |
| `external` | External data | `fetchList`, `mapRow` |
| `custom` | Custom component | `render` function |

---

## 🎨 Theme CSS Loading System

CSS stylesheets are dynamically injected into the document head.

### How It Works (ThemeContext.jsx)

```javascript
// Track injected stylesheets for cleanup
let injectedStylesheets = [];

/**
 * Inject theme CSS stylesheet into document head
 */
const injectThemeStylesheet = (themeSlug, cssPath) => {
  const linkId = `theme-css-${themeSlug}-${cssPath.replace(/[^a-z0-9]/gi, '-')}`;
  
  // Prevent duplicate injection
  if (document.getElementById(linkId)) return;
  
  const link = document.createElement('link');
  link.id = linkId;
  link.rel = 'stylesheet';
  link.type = 'text/css';
  link.href = `/themes/${themeSlug}/${cssPath}`;
  link.setAttribute('data-theme', themeSlug);
  
  document.head.appendChild(link);
  injectedStylesheets.push(linkId);
};

/**
 * Remove theme stylesheets on theme change
 */
const removeThemeStylesheets = (themeSlug = null) => {
  const selector = themeSlug
    ? `link[data-theme="${themeSlug}"]`
    : 'link[data-theme]';
  
  document.querySelectorAll(selector).forEach(link => link.remove());
};

/**
 * Load CSS from theme settings or default path
 */
const loadThemeCSS = (themeSlug, themeSettings) => {
  // Clean up previous theme CSS
  removeThemeStylesheets();
  
  if (!themeSlug || themeSlug === 'default') return;
  
  // Check for explicit stylesheets in theme.json settings
  if (themeSettings?.stylesheets) {
    const sheets = Array.isArray(themeSettings.stylesheets)
      ? themeSettings.stylesheets
      : [themeSettings.stylesheets];
    
    sheets.forEach(cssPath => injectThemeStylesheet(themeSlug, cssPath));
  } else {
    // Default: look for styles/theme.css
    injectThemeStylesheet(themeSlug, 'styles/theme.css');
  }
};
```

### Theme.json Stylesheet Configuration

```json
{
  "name": "Celestial",
  "slug": "celestial",
  "settings": {
    "stylesheets": [
      "styles/theme.css",
      "styles/animations.css"
    ]
  }
}
```

### CSS Variables Applied by ThemeManager

```javascript
// ThemeManager.applyCSSVariables() sets these on :root
const cssVariables = {
  // Colors
  '--color-primary': '#1E1B4B',
  '--color-primary-50': '#f5f3ff',   // Auto-generated lighter
  '--color-primary-900': '#1e1b4b',  // Auto-generated darker
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

---

## 💾 Server-Side Theme Storage

### Database Schema (themes table)

```sql
CREATE TABLE themes (
  id SERIAL PRIMARY KEY,
  slug VARCHAR(100) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  version VARCHAR(20),
  author VARCHAR(255),
  is_active BOOLEAN DEFAULT false,  -- Only one theme active at a time
  settings JSONB DEFAULT '{}',
  customizations JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints

```javascript
// Get active theme (public)
GET /api/themes/active
// Response: { success: true, data: { slug, name, settings, customizations } }

// List all themes (admin)
GET /api/themes

// Activate a theme (admin)
PUT /api/themes/:slug/activate

// Update theme customizations (admin)
PUT /api/themes/:slug/customizations
// Body: { colors: { primary: '#...' }, typography: { ... } }
```

### Frontend Theme Loading

```javascript
// ThemeContext.jsx - loadActiveTheme()
const loadActiveTheme = async () => {
  try {
    const response = await api.get('/themes/active');
    if (response.data.success) {
      const themeData = response.data.data;
      
      // Load into ThemeManager
      await themeManager.loadTheme(themeData.slug, themeData);
      
      // Load CSS stylesheets
      loadThemeCSS(themeData.slug, themeData.settings);
      
      setTheme(themeData);
    }
  } catch (error) {
    console.error('Failed to load theme:', error);
    // Fall back to default theme
  }
};
```

### Per-User Theme Preference (Partial Implementation)

```javascript
// User preferences stored in profiles.settings JSONB
// Query example:
await db.queryJSON('profiles', 'settings', '$.theme', 'dark');

// To implement user preference override:
// 1. Check user.settings.theme on login
// 2. If set, use that instead of site-wide active theme
// 3. Store preference: PUT /api/users/preferences { theme: 'celestial' }
```

---

## 🔥 Hot Module Replacement (HMR) Gotchas

### What Works

| Change Type | HMR Behavior |
|-------------|--------------|
| Theme component JSX | ✅ Hot reloads |
| Theme component styles (inline/Tailwind) | ✅ Hot reloads |
| Theme CSS variables in JS | ✅ Hot reloads |
| Export names in index.js | ⚠️ May need manual refresh |

### What Requires Manual Refresh

| Change Type | Workaround |
|-------------|------------|
| Theme CSS files (theme.css) | Injected via `<link>`, not Vite pipeline |
| New theme folder added | `import.meta.glob` is static, restart Vite |
| theme.json changes | Reload page to refetch from API |
| Puck field definitions | Restart Puck editor page |

### Development Tips

```bash
# If HMR seems stuck, try:
# 1. Save the file again (triggers re-evaluation)
# 2. Clear browser cache and hard reload (Ctrl+Shift+R)
# 3. Restart Vite dev server

# Watch for this console message indicating theme loaded:
# [ThemeManager] Loaded 3 component overrides
# [ThemeContext] Injected stylesheet: /themes/celestial/styles/theme.css
```

### Vite HMR Debug

```javascript
// Add to component for HMR debugging
if (import.meta.hot) {
  import.meta.hot.accept(() => {
    console.log('Theme component hot updated');
  });
}
```

---

## 📦 Production Build Considerations

### Vite Build Output

```bash
npm run build
# Outputs to client/dist/
# Theme JS components are bundled via import.meta.glob
```

### Critical: Serve Themes Folder

Theme CSS files are NOT bundled - they're loaded at runtime. Your server must serve them:

```javascript
// server/app.js - Add this line
const path = require('path');

// Serve theme static files (CSS, images, fonts)
app.use('/themes', express.static(path.join(__dirname, '../themes')));

// Or with options:
app.use('/themes', express.static(path.join(__dirname, '../themes'), {
  maxAge: '1d',  // Cache for 1 day
  etag: true,
  lastModified: true
}));
```

### Nginx Configuration (if using)

```nginx
# Serve themes folder
location /themes/ {
    alias /var/www/app/themes/;
    expires 1d;
    add_header Cache-Control "public, immutable";
}
```

### Docker Considerations

```dockerfile
# Ensure themes folder is copied
COPY themes/ /app/themes/

# Or mount as volume in docker-compose.yml
volumes:
  - ./themes:/app/themes:ro
```

### Verify Build Includes Theme Components

```bash
# After build, check that theme components are in the bundle
grep -r "CelestialHero" client/dist/assets/*.js
# Should find minified references to theme components
```

---

## 🌙 Dark Mode Integration

### Current Implementation: Separate Themes

Dark mode is currently a separate theme (`dark-mode`) rather than a toggle:

```json
// themes/dark-mode/theme.json
{
  "name": "Dark Mode",
  "slug": "dark-mode",
  "settings": {
    "colors": {
      "background": "#1a1a2e",
      "surface": "#16213e",
      "text": "#eaeaea",
      "primary": "#4a9eff"
    },
    "features": {
      "darkMode": true
    }
  }
}
```

### Per-Theme Dark Mode Support

Some themes support internal dark mode via settings:

```json
// themes/classic/theme.json
{
  "settings": {
    "features": {
      "darkMode": {
        "enabled": true,
        "colors": {
          "background": "#1f2937",
          "text": "#f9fafb"
        }
      }
    }
  }
}
```

### Implementing Universal Dark Mode Toggle

```javascript
// Option 1: CSS class toggle (recommended)
const toggleDarkMode = () => {
  document.documentElement.classList.toggle('dark');
  localStorage.setItem('darkMode', document.documentElement.classList.contains('dark'));
};

// In theme CSS:
:root {
  --color-background: #ffffff;
  --color-text: #1f1f2e;
}

:root.dark {
  --color-background: #1a1a2e;
  --color-text: #eaeaea;
}

// Option 2: Theme variant switching
const setThemeVariant = (variant) => {
  // Load dark variant of current theme
  await themeManager.loadTheme(`${currentTheme}-dark`, themeData);
};
```

### Respecting System Preference

```javascript
// Check system preference on load
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

// Listen for changes
window.matchMedia('(prefers-color-scheme: dark)')
  .addEventListener('change', (e) => {
    if (e.matches) {
      enableDarkMode();
    } else {
      disableDarkMode();
    }
  });
```

---

## 🛡️ Error Boundaries for Theme Components

### Problem

If a theme component throws an error, it can crash the entire page.

### Solution: Wrap Theme Components

```jsx
// client/src/layouts/MainLayout.jsx
import ErrorBoundary from '../components/common/ErrorBoundary';

const MainLayoutInner = () => {
  const { getComponent } = useTheme();
  
  const Header = getComponent('Header', DefaultHeader);
  const Footer = getComponent('Footer', DefaultFooter);
  
  return (
    <div className="min-h-screen flex flex-col">
      {/* Wrap header with fallback */}
      <ErrorBoundary 
        fallback={<DefaultHeader />}
        onError={(error) => console.error('Theme Header crashed:', error)}
      >
        <Suspense fallback={<ComponentLoader type="header" />}>
          <Header />
        </Suspense>
      </ErrorBoundary>
      
      <main className="flex-1">
        {children}
      </main>
      
      {/* Wrap footer with fallback */}
      <ErrorBoundary 
        fallback={<DefaultFooter />}
        onError={(error) => console.error('Theme Footer crashed:', error)}
      >
        <Suspense fallback={<ComponentLoader type="footer" />}>
          <Footer />
        </Suspense>
      </ErrorBoundary>
    </div>
  );
};
```

### Enhanced ErrorBoundary with Reset

```jsx
// components/common/ThemeErrorBoundary.jsx
import React from 'react';

class ThemeErrorBoundary extends React.Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error(`[ThemeErrorBoundary] ${this.props.componentName} failed:`, error);
    
    // Optional: Report to error tracking service
    // errorReporter.captureException(error, { componentName: this.props.componentName });
  }
  
  render() {
    if (this.state.hasError) {
      // Render fallback component
      const Fallback = this.props.fallback;
      return Fallback ? <Fallback /> : (
        <div className="p-4 bg-red-50 text-red-700 text-center">
          Failed to load {this.props.componentName}. Using default.
        </div>
      );
    }
    
    return this.props.children;
  }
}

export default ThemeErrorBoundary;
```

### Usage Pattern

```jsx
<ThemeErrorBoundary componentName="Header" fallback={DefaultHeader}>
  <ThemedHeader />
</ThemeErrorBoundary>
```

---

## 📊 Implementation Status Summary

| Feature | Status | Location |
|---------|--------|----------|
| Component Overrides | ✅ Complete | ThemeManager.js, MainLayout.jsx |
| Puck Components | ✅ Complete | ThemeManager.loadPuckComponents() |
| CSS Loading | ✅ Complete | ThemeContext.jsx |
| CSS Variables | ✅ Complete | ThemeManager.applyCSSVariables() |
| API Persistence | ✅ Complete | /api/themes/active |
| User Preferences | ⚠️ Partial | DB ready, needs frontend wiring |
| HMR Support | ⚠️ Works with gotchas | See notes above |
| Production Build | ⚠️ Needs static serving | Configure Express/Nginx |
| Dark Mode | ⚠️ Separate themes only | No universal toggle |
| Error Boundaries | ❌ Not implemented | Should wrap theme components |

---

*Last Updated: January 17, 2026*
