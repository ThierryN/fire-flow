# LMS Theme System - Product Requirements Document Template

Version: 1.0.0
Last Updated: 2025-11-25
Platform: MERN Community LMS

---

## Table of Contents

1. [Overview](#overview)
2. [Theme Metadata Specification](#theme-metadata-specification)
3. [File Structure Template](#file-structure-template)
4. [Component Override System](#component-override-system)
5. [Styling Specification](#styling-specification)
6. [Layout System](#layout-system)
7. [Configuration Schema](#configuration-schema)
8. [Hook System](#hook-system)
9. [Content Type Support](#content-type-support)
10. [Testing Requirements](#testing-requirements)
11. [Documentation Requirements](#documentation-requirements)
12. [Deployment & Integration](#deployment--integration)

---

## Overview

This document provides complete specifications for creating a fully compatible theme for the MERN Community LMS platform. Any AI assistant with NO prior context should be able to use this document to create a production-ready theme.

### System Architecture Summary

The LMS uses:
- **Frontend**: React 18.3.1 + Vite 7.1.2
- **Styling**: Tailwind CSS 4.1.13
- **State Management**: Redux Toolkit 2.9.0
- **Routing**: React Router DOM 7.8.2
- **Page Builder**: Puck 0.20.2
- **Backend**: Node.js + Express 5.1.0 + PostgreSQL

### Theme Integration Points

Themes can customize:
1. **Global Styles**: Colors, typography, spacing
2. **Component Overrides**: Custom implementations of core components
3. **Layout Templates**: Header, footer, sidebar configurations
4. **Page Templates**: Custom layouts for specific content types
5. **Settings Panel**: Theme-specific customization options

---

## Theme Metadata Specification

### Required Fields

Every theme MUST include a `theme.json` file in the theme root with these required fields:

```json
{
  "name": "string",              // Unique theme identifier (lowercase, hyphenated)
  "displayName": "string",       // Human-readable name
  "version": "string",           // Semantic version (e.g., "1.0.0")
  "author": "string",            // Author name or organization
  "description": "string",       // Brief description (max 200 chars)
  "compatibility": "string",     // Platform version (e.g., "^1.0.0")
  "license": "string",           // License type (e.g., "MIT", "GPL-3.0")
  "repository": "string"         // Git repository URL
}
```

### Optional Fields

```json
{
  "homepage": "string",          // Theme website/documentation URL
  "bugs": "string",              // Issue tracker URL
  "keywords": ["string"],        // Search keywords
  "contributors": ["string"],    // Additional contributors
  "screenshot": "string",        // Path to theme screenshot (relative)
  "preview": "string",           // Live preview URL
  "category": "string",          // Theme category (e.g., "Education", "Corporate")
  "features": ["string"],        // List of key features
  "demo": {                      // Demo configuration
    "url": "string",
    "credentials": {
      "username": "string",
      "password": "string"
    }
  }
}
```

### Screenshot Requirements

- **File**: `screenshot.png` or `screenshot.jpg` in theme root
- **Dimensions**: 1200x900px (4:3 aspect ratio)
- **Format**: PNG or JPEG
- **File Size**: Max 500KB
- **Content**: Show homepage or most distinctive theme feature

### Demo Data Specifications

If including demo data, provide:

```
themes/your-theme/
  └── demo/
      ├── demo-data.json       // Sample content
      ├── images/              // Demo images
      └── README.md            // Demo setup instructions
```

---

## File Structure Template

### Required Directory Structure

```
themes/
  └── your-theme-name/
      ├── theme.json                    // REQUIRED: Theme metadata
      ├── screenshot.png                // REQUIRED: Theme preview
      ├── README.md                     // REQUIRED: Documentation
      ├── LICENSE                       // REQUIRED: License file
      │
      ├── src/                          // Source files
      │   ├── index.js                  // REQUIRED: Theme entry point
      │   ├── config.js                 // REQUIRED: Theme configuration
      │   │
      │   ├── styles/                   // Styles directory
      │   │   ├── index.css             // Main stylesheet
      │   │   ├── variables.css         // CSS custom properties
      │   │   ├── globals.css           // Global overrides
      │   │   ├── components/           // Component-specific styles
      │   │   └── utilities.css         // Utility classes
      │   │
      │   ├── components/               // Component overrides
      │   │   ├── layout/               // Layout components
      │   │   │   ├── Header.jsx
      │   │   │   ├── Footer.jsx
      │   │   │   └── Sidebar.jsx
      │   │   ├── pages/                // Page templates
      │   │   │   ├── CourseDetail.jsx
      │   │   │   ├── LessonView.jsx
      │   │   │   └── UserProfile.jsx
      │   │   └── common/               // Common components
      │   │       ├── Button.jsx
      │   │       ├── Card.jsx
      │   │       └── Modal.jsx
      │   │
      │   ├── hooks/                    // Custom hooks
      │   │   ├── useThemeSettings.js
      │   │   └── useResponsive.js
      │   │
      │   ├── utils/                    // Utility functions
      │   │   ├── colors.js
      │   │   └── helpers.js
      │   │
      │   └── puck/                     // Puck page builder components
      │       ├── components.jsx        // Custom Puck components
      │       └── config.jsx            // Puck configuration
      │
      ├── assets/                       // Static assets
      │   ├── images/                   // Theme images
      │   ├── fonts/                    // Custom fonts (if any)
      │   └── icons/                    // Custom icons
      │
      ├── demo/                         // Demo data (optional)
      │   ├── demo-data.json
      │   └── images/
      │
      └── tests/                        // Test files (optional but recommended)
          ├── components/
          └── integration/
```

### Entry Point Structure

The `src/index.js` file MUST export:

```javascript
export default {
  name: 'your-theme-name',
  config: themeConfig,           // From src/config.js
  styles: './styles/index.css',  // Main stylesheet path
  components: componentOverrides, // Component map
  hooks: themeHooks,             // Lifecycle hooks
  settings: settingsSchema       // Theme settings
};
```

### Naming Conventions

- **Files**: camelCase for JS/JSX, kebab-case for CSS
- **Components**: PascalCase (e.g., `Header.jsx`, `CourseCard.jsx`)
- **Styles**: kebab-case (e.g., `main-header.css`, `course-grid.css`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `THEME_VERSION`, `DEFAULT_COLOR`)
- **Functions**: camelCase (e.g., `getThemeColor`, `applyStyles`)

### Import/Export Patterns

**Named Exports** (preferred for utilities and hooks):
```javascript
export const getThemeColor = (color) => { /* ... */ };
export const useThemeSettings = () => { /* ... */ };
```

**Default Exports** (for components and main files):
```javascript
export default function Header({ ...props }) { /* ... */ }
```

**Barrel Exports** (for component directories):
```javascript
// src/components/layout/index.js
export { default as Header } from './Header';
export { default as Footer } from './Footer';
export { default as Sidebar } from './Sidebar';
```

---

## Component Override System

### Override Methods

The theme system supports three override methods:

#### 1. Full Component Replacement

Replace an entire component:

```javascript
// src/components/layout/Header.jsx
import React from 'react';
import { useTheme } from '../../../context/ThemeContext';

export default function Header() {
  const { settings } = useTheme();

  return (
    <header className="theme-custom-header">
      {/* Your custom implementation */}
    </header>
  );
}
```

#### 2. Component Composition (Wrapping)

Wrap existing component with additional functionality:

```javascript
// src/components/common/Button.jsx
import React from 'react';
import { Button as BaseButton } from '@core/components';

export default function Button({ children, variant, ...props }) {
  return (
    <BaseButton
      {...props}
      className={`theme-button theme-button-${variant}`}
    >
      {children}
    </BaseButton>
  );
}
```

#### 3. Configuration-Based Customization

Customize via configuration without replacing component:

```javascript
// src/config.js
export const componentConfig = {
  Header: {
    height: '80px',
    transparent: false,
    sticky: true,
    showLogo: true,
    showSearch: true
  }
};
```

### Overridable Components

#### Layout Components

| Component | Path | Override Priority | Props Interface |
|-----------|------|-------------------|-----------------|
| Header | `components/layout/Header.jsx` | High | `{ user, isAuthenticated, settings }` |
| Footer | `components/layout/Footer.jsx` | High | `{ settings }` |
| Sidebar | `components/layout/Sidebar.jsx` | Medium | `{ isOpen, onClose, navigation }` |
| MainLayout | `layouts/MainLayout.jsx` | High | `{ children }` |
| AdminLayout | `layouts/AdminLayout.jsx` | Medium | `{ children }` |
| AuthLayout | `layouts/AuthLayout.jsx` | Medium | `{ children }` |

#### Page Components

| Component | Path | Override Priority | Props Interface |
|-----------|------|-------------------|-----------------|
| Home | `pages/Home.jsx` | High | `{}` |
| CourseDetail | `pages/CourseDetail.jsx` | High | `{ course }` |
| CourseContent | `pages/CourseContent.jsx` | High | `{ lesson, course }` |
| UserProfile | `pages/dashboard/Profile.jsx` | Medium | `{ user }` |
| Dashboard | `pages/dashboard/Dashboard.jsx` | Medium | `{ user, stats }` |

#### Common Components

| Component | Path | Props Interface |
|-----------|------|-----------------|
| Button | `components/common/Button.jsx` | `{ variant, size, disabled, onClick, children }` |
| Card | `components/common/Card.jsx` | `{ title, image, description, link }` |
| Modal | `components/common/Modal.jsx` | `{ isOpen, onClose, title, children }` |
| Loader | `components/common/Loader.jsx` | `{ size, color }` |

### Component Registration

Register overrides in `src/config.js`:

```javascript
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import CourseCard from './components/common/CourseCard';

export const componentOverrides = {
  'layout/Header': Header,
  'layout/Footer': Footer,
  'common/CourseCard': CourseCard
};
```

### Fallback Behavior

- If theme component fails to load, system falls back to default component
- Console warning logged but app continues functioning
- Error boundary catches component errors
- Props interface remains consistent across all overrides

### Props Interface Documentation

#### Header Component
```typescript
interface HeaderProps {
  user: {
    id: string;
    name: string;
    email: string;
    role: 'student' | 'instructor' | 'admin';
  } | null;
  isAuthenticated: boolean;
  settings: {
    site_name: string;
    primary_logo: string;
    primary_color: string;
  };
}
```

#### Footer Component
```typescript
interface FooterProps {
  settings: {
    site_name: string;
    footer_text: string;
  };
}
```

#### CourseCard Component
```typescript
interface CourseCardProps {
  course: {
    id: string;
    title: string;
    description: string;
    thumbnail: string;
    instructor: string;
    price: number;
    duration: string;
  };
  onClick?: () => void;
}
```

---

## Styling Specification

### Design Token System

Define design tokens in `src/styles/variables.css`:

```css
:root {
  /* Colors - Brand */
  --theme-color-primary: #4F46E5;
  --theme-color-primary-hover: #4338CA;
  --theme-color-primary-light: #EEF2FF;

  --theme-color-secondary: #EC4899;
  --theme-color-secondary-hover: #DB2777;
  --theme-color-secondary-light: #FCE7F3;

  /* Colors - Neutral */
  --theme-color-text: #1F2937;
  --theme-color-text-light: #6B7280;
  --theme-color-text-muted: #9CA3AF;

  --theme-color-background: #FFFFFF;
  --theme-color-background-alt: #F9FAFB;
  --theme-color-background-dark: #111827;

  --theme-color-border: #E5E7EB;
  --theme-color-border-light: #F3F4F6;

  /* Colors - Semantic */
  --theme-color-success: #10B981;
  --theme-color-warning: #F59E0B;
  --theme-color-error: #EF4444;
  --theme-color-info: #3B82F6;

  /* Typography */
  --theme-font-sans: 'Inter var', 'Inter', system-ui, sans-serif;
  --theme-font-serif: 'Georgia', serif;
  --theme-font-mono: 'Fira Code', monospace;

  --theme-font-size-xs: 0.75rem;      /* 12px */
  --theme-font-size-sm: 0.875rem;     /* 14px */
  --theme-font-size-base: 1rem;       /* 16px */
  --theme-font-size-lg: 1.125rem;     /* 18px */
  --theme-font-size-xl: 1.25rem;      /* 20px */
  --theme-font-size-2xl: 1.5rem;      /* 24px */
  --theme-font-size-3xl: 1.875rem;    /* 30px */
  --theme-font-size-4xl: 2.25rem;     /* 36px */

  --theme-font-weight-normal: 400;
  --theme-font-weight-medium: 500;
  --theme-font-weight-semibold: 600;
  --theme-font-weight-bold: 700;

  --theme-line-height-tight: 1.25;
  --theme-line-height-normal: 1.5;
  --theme-line-height-relaxed: 1.75;

  /* Spacing */
  --theme-space-xs: 0.25rem;    /* 4px */
  --theme-space-sm: 0.5rem;     /* 8px */
  --theme-space-md: 1rem;       /* 16px */
  --theme-space-lg: 1.5rem;     /* 24px */
  --theme-space-xl: 2rem;       /* 32px */
  --theme-space-2xl: 3rem;      /* 48px */
  --theme-space-3xl: 4rem;      /* 64px */

  /* Layout */
  --theme-container-sm: 640px;
  --theme-container-md: 768px;
  --theme-container-lg: 1024px;
  --theme-container-xl: 1280px;
  --theme-container-2xl: 1536px;

  --theme-header-height: 80px;
  --theme-footer-height: 200px;
  --theme-sidebar-width: 256px;

  /* Border Radius */
  --theme-radius-sm: 0.25rem;   /* 4px */
  --theme-radius-md: 0.5rem;    /* 8px */
  --theme-radius-lg: 0.75rem;   /* 12px */
  --theme-radius-xl: 1rem;      /* 16px */
  --theme-radius-full: 9999px;

  /* Shadows */
  --theme-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --theme-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --theme-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --theme-shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

  /* Transitions */
  --theme-transition-fast: 150ms ease-in-out;
  --theme-transition-base: 250ms ease-in-out;
  --theme-transition-slow: 350ms ease-in-out;

  /* Z-index layers */
  --theme-z-base: 0;
  --theme-z-dropdown: 10;
  --theme-z-sticky: 20;
  --theme-z-fixed: 30;
  --theme-z-modal-backdrop: 40;
  --theme-z-modal: 50;
  --theme-z-popover: 60;
  --theme-z-tooltip: 70;
}
```

### CSS Architecture

The theme follows a modular CSS architecture:

**1. Variables** (`variables.css`) - Design tokens
**2. Globals** (`globals.css`) - Base styles and resets
**3. Components** (`components/*.css`) - Component-specific styles
**4. Utilities** (`utilities.css`) - Utility classes

### Global Styles Approach

```css
/* src/styles/globals.css */

/* Base reset extensions */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* Body defaults */
body {
  font-family: var(--theme-font-sans);
  font-size: var(--theme-font-size-base);
  line-height: var(--theme-line-height-normal);
  color: var(--theme-color-text);
  background-color: var(--theme-color-background);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Typography scale */
h1 { font-size: var(--theme-font-size-4xl); }
h2 { font-size: var(--theme-font-size-3xl); }
h3 { font-size: var(--theme-font-size-2xl); }
h4 { font-size: var(--theme-font-size-xl); }
h5 { font-size: var(--theme-font-size-lg); }
h6 { font-size: var(--theme-font-size-base); }

/* Link defaults */
a {
  color: var(--theme-color-primary);
  text-decoration: none;
  transition: color var(--theme-transition-fast);
}

a:hover {
  color: var(--theme-color-primary-hover);
}

/* Focus styles for accessibility */
:focus-visible {
  outline: 2px solid var(--theme-color-primary);
  outline-offset: 2px;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--theme-color-background-alt);
}

::-webkit-scrollbar-thumb {
  background: var(--theme-color-border);
  border-radius: var(--theme-radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--theme-color-text-muted);
}
```

### Responsive Breakpoints

```css
/* Mobile First Approach */

/* Extra Small (default) - Mobile portrait */
/* 0px - 639px */

/* Small - Mobile landscape */
@media (min-width: 640px) {
  /* sm: styles */
}

/* Medium - Tablet portrait */
@media (min-width: 768px) {
  /* md: styles */
}

/* Large - Tablet landscape / Small desktop */
@media (min-width: 1024px) {
  /* lg: styles */
}

/* Extra Large - Desktop */
@media (min-width: 1280px) {
  /* xl: styles */
}

/* 2XL - Large desktop */
@media (min-width: 1536px) {
  /* 2xl: styles */
}
```

### Dark Mode Support

```css
/* Dark mode variables */
[data-theme="dark"] {
  --theme-color-text: #F9FAFB;
  --theme-color-text-light: #D1D5DB;
  --theme-color-text-muted: #9CA3AF;

  --theme-color-background: #111827;
  --theme-color-background-alt: #1F2937;
  --theme-color-background-dark: #030712;

  --theme-color-border: #374151;
  --theme-color-border-light: #1F2937;
}

/* Auto dark mode based on system preference */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --theme-color-text: #F9FAFB;
    --theme-color-text-light: #D1D5DB;
    --theme-color-text-muted: #9CA3AF;

    --theme-color-background: #111827;
    --theme-color-background-alt: #1F2937;
    --theme-color-background-dark: #030712;

    --theme-color-border: #374151;
    --theme-color-border-light: #1F2937;
  }
}
```

### Tailwind Integration

Extend Tailwind config to use theme variables:

```javascript
// tailwind.config.js (theme-specific)
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'var(--theme-color-primary)',
          hover: 'var(--theme-color-primary-hover)',
          light: 'var(--theme-color-primary-light)',
        },
        secondary: {
          DEFAULT: 'var(--theme-color-secondary)',
          hover: 'var(--theme-color-secondary-hover)',
          light: 'var(--theme-color-secondary-light)',
        }
      },
      fontFamily: {
        sans: 'var(--theme-font-sans)',
        serif: 'var(--theme-font-serif)',
        mono: 'var(--theme-font-mono)',
      },
      spacing: {
        'xs': 'var(--theme-space-xs)',
        'sm': 'var(--theme-space-sm)',
        'md': 'var(--theme-space-md)',
        'lg': 'var(--theme-space-lg)',
        'xl': 'var(--theme-space-xl)',
        '2xl': 'var(--theme-space-2xl)',
        '3xl': 'var(--theme-space-3xl)',
      }
    }
  }
};
```

---

## Layout System

### Available Layout Slots

The LMS provides these layout slots for customization:

#### 1. Header Slot
- **Position**: Top of all pages
- **Height**: Variable (default: 80px)
- **Sticky**: Configurable
- **Elements**: Logo, Navigation, User Menu, Search, Cart

#### 2. Footer Slot
- **Position**: Bottom of all pages
- **Height**: Variable (default: auto)
- **Columns**: Flexible (1-4 columns)
- **Elements**: Links, Social, Newsletter, Copyright

#### 3. Sidebar Slot (Admin/Dashboard)
- **Position**: Left side (collapsible)
- **Width**: 256px (default)
- **Behavior**: Slide-in on mobile
- **Elements**: Navigation menu, User info

#### 4. Content Slot
- **Position**: Main content area
- **Width**: Container-based (responsive)
- **Max Width**: Configurable
- **Padding**: Configurable

#### 5. Alert/Banner Slot
- **Position**: Above header (optional)
- **Height**: Auto
- **Dismissible**: Yes
- **Use**: Announcements, notifications

### Layout Composition Patterns

#### Pattern 1: Standard Page Layout

```jsx
<MainLayout>
  <Header />
  <AlertBanner />
  <main>
    <Container>
      {children}
    </Container>
  </main>
  <Footer />
</MainLayout>
```

#### Pattern 2: Admin Layout with Sidebar

```jsx
<AdminLayout>
  <Header />
  <div className="flex">
    <Sidebar />
    <main className="flex-1">
      <Container>
        {children}
      </Container>
    </main>
  </div>
  <Footer />
</AdminLayout>
```

#### Pattern 3: Full Width Layout

```jsx
<MainLayout>
  <Header />
  <main className="w-full">
    {children}
  </main>
  <Footer />
</MainLayout>
```

#### Pattern 4: Centered Content Layout

```jsx
<MainLayout>
  <Header />
  <main className="flex items-center justify-center min-h-screen">
    <div className="max-w-md w-full">
      {children}
    </div>
  </main>
  <Footer />
</MainLayout>
```

### Responsive Behavior Rules

1. **Mobile (<768px)**
   - Single column layout
   - Sidebar collapses to hamburger menu
   - Navigation stacks vertically
   - Footer columns stack

2. **Tablet (768px-1023px)**
   - 2-column layouts where appropriate
   - Sidebar remains visible on large tablets
   - Navigation can be horizontal or vertical
   - Footer uses 2-column grid

3. **Desktop (≥1024px)**
   - Multi-column layouts
   - Full sidebar always visible
   - Horizontal navigation
   - Footer uses 3-4 column grid

### Content Width Constraints

```javascript
export const layoutConfig = {
  container: {
    sm: '640px',    // Forms, auth pages
    md: '768px',    // Blog posts, articles
    lg: '1024px',   // Standard pages
    xl: '1280px',   // Wide content
    '2xl': '1536px', // Full width
    full: '100%'    // No constraint
  },

  contentWidth: {
    narrow: '640px',    // Reading content
    normal: '768px',    // Standard content
    wide: '1024px',     // Dashboard, admin
    full: '100%'        // Hero sections
  },

  padding: {
    mobile: '16px',     // 1rem
    tablet: '24px',     // 1.5rem
    desktop: '32px'     // 2rem
  }
};
```

---

## Configuration Schema

### Theme Settings JSON Schema

```javascript
// src/config/settings-schema.js
export const settingsSchema = {
  // General Settings
  general: {
    label: 'General Settings',
    fields: {
      darkMode: {
        type: 'toggle',
        label: 'Enable Dark Mode',
        default: false,
        description: 'Allow users to toggle dark mode'
      },
      containerWidth: {
        type: 'select',
        label: 'Container Width',
        options: [
          { value: 'sm', label: 'Small (640px)' },
          { value: 'md', label: 'Medium (768px)' },
          { value: 'lg', label: 'Large (1024px)' },
          { value: 'xl', label: 'Extra Large (1280px)' },
          { value: '2xl', label: '2XL (1536px)' }
        ],
        default: 'xl'
      }
    }
  },

  // Colors
  colors: {
    label: 'Color Scheme',
    fields: {
      primaryColor: {
        type: 'color',
        label: 'Primary Color',
        default: '#4F46E5',
        description: 'Main brand color'
      },
      secondaryColor: {
        type: 'color',
        label: 'Secondary Color',
        default: '#EC4899',
        description: 'Accent color'
      },
      backgroundColor: {
        type: 'color',
        label: 'Background Color',
        default: '#FFFFFF',
        description: 'Page background'
      },
      textColor: {
        type: 'color',
        label: 'Text Color',
        default: '#1F2937',
        description: 'Primary text color'
      }
    }
  },

  // Typography
  typography: {
    label: 'Typography',
    fields: {
      fontFamily: {
        type: 'select',
        label: 'Font Family',
        options: [
          { value: 'inter', label: 'Inter' },
          { value: 'roboto', label: 'Roboto' },
          { value: 'open-sans', label: 'Open Sans' },
          { value: 'lato', label: 'Lato' },
          { value: 'system', label: 'System Default' }
        ],
        default: 'inter'
      },
      baseFontSize: {
        type: 'number',
        label: 'Base Font Size (px)',
        min: 14,
        max: 20,
        step: 1,
        default: 16
      },
      headingFontWeight: {
        type: 'select',
        label: 'Heading Font Weight',
        options: [
          { value: '400', label: 'Normal' },
          { value: '500', label: 'Medium' },
          { value: '600', label: 'Semibold' },
          { value: '700', label: 'Bold' }
        ],
        default: '700'
      }
    }
  },

  // Header
  header: {
    label: 'Header Settings',
    fields: {
      headerStyle: {
        type: 'select',
        label: 'Header Style',
        options: [
          { value: 'default', label: 'Default' },
          { value: 'transparent', label: 'Transparent' },
          { value: 'minimal', label: 'Minimal' },
          { value: 'centered', label: 'Centered' }
        ],
        default: 'default'
      },
      headerSticky: {
        type: 'toggle',
        label: 'Sticky Header',
        default: true
      },
      showSearch: {
        type: 'toggle',
        label: 'Show Search Bar',
        default: true
      },
      headerHeight: {
        type: 'number',
        label: 'Header Height (px)',
        min: 60,
        max: 120,
        step: 5,
        default: 80
      }
    }
  },

  // Footer
  footer: {
    label: 'Footer Settings',
    fields: {
      footerColumns: {
        type: 'number',
        label: 'Number of Columns',
        min: 1,
        max: 4,
        step: 1,
        default: 4
      },
      showSocial: {
        type: 'toggle',
        label: 'Show Social Links',
        default: true
      },
      showNewsletter: {
        type: 'toggle',
        label: 'Show Newsletter Signup',
        default: true
      }
    }
  },

  // Course Display
  courses: {
    label: 'Course Display',
    fields: {
      gridColumns: {
        type: 'select',
        label: 'Grid Columns',
        options: [
          { value: 2, label: '2 Columns' },
          { value: 3, label: '3 Columns' },
          { value: 4, label: '4 Columns' }
        ],
        default: 3
      },
      showInstructor: {
        type: 'toggle',
        label: 'Show Instructor',
        default: true
      },
      showProgress: {
        type: 'toggle',
        label: 'Show Progress Bar',
        default: true
      },
      cardStyle: {
        type: 'select',
        label: 'Card Style',
        options: [
          { value: 'default', label: 'Default' },
          { value: 'minimal', label: 'Minimal' },
          { value: 'elevated', label: 'Elevated' },
          { value: 'bordered', label: 'Bordered' }
        ],
        default: 'default'
      }
    }
  }
};
```

### Setting Types

1. **text**: Single-line text input
2. **textarea**: Multi-line text input
3. **number**: Numeric input with min/max/step
4. **color**: Color picker
5. **toggle**: Boolean switch
6. **select**: Dropdown menu
7. **radio**: Radio button group
8. **checkbox**: Checkbox group
9. **image**: Image uploader
10. **range**: Slider input

### Default Values

All settings MUST have default values to ensure theme works out of the box.

### Validation Rules

```javascript
export const validationRules = {
  primaryColor: {
    pattern: /^#[0-9A-F]{6}$/i,
    message: 'Must be a valid hex color'
  },
  headerHeight: {
    min: 60,
    max: 120,
    message: 'Header height must be between 60-120px'
  },
  baseFontSize: {
    min: 14,
    max: 20,
    message: 'Font size must be between 14-20px'
  }
};
```

---

## Hook System

### Available Lifecycle Hooks

The theme system provides hooks at key lifecycle points:

#### 1. Theme Initialization
```javascript
export const hooks = {
  onThemeInit: async (themeConfig) => {
    // Called when theme is first loaded
    // Setup custom fonts, external resources, etc.
    console.log('Theme initialized:', themeConfig);
  }
};
```

#### 2. Theme Activation
```javascript
onThemeActivate: async () => {
  // Called when theme becomes active
  // Apply global styles, load settings, etc.
}
```

#### 3. Theme Deactivation
```javascript
onThemeDeactivate: async () => {
  // Called when theme is switched
  // Cleanup, save state, etc.
}
```

#### 4. Settings Change
```javascript
onSettingsChange: async (settingKey, newValue, oldValue) => {
  // Called when theme setting is modified
  // Update styles, recompute values, etc.
  if (settingKey === 'primaryColor') {
    updateColorScheme(newValue);
  }
}
```

#### 5. Page Load
```javascript
onPageLoad: async (routeInfo) => {
  // Called on route change
  // Setup page-specific configurations
  console.log('Route:', routeInfo.path);
}
```

### Data Hooks for Content Customization

#### Course Data Hook
```javascript
hooks: {
  transformCourseData: (course) => {
    // Modify course data before rendering
    return {
      ...course,
      customField: calculateCustomValue(course)
    };
  }
}
```

#### User Data Hook
```javascript
transformUserData: (user) => {
  // Add custom user properties
  return {
    ...user,
    displayName: `${user.firstName} ${user.lastName}`,
    avatar: user.avatar || generateAvatar(user.name)
  };
}
```

#### Menu Data Hook
```javascript
transformMenuData: (menuItems) => {
  // Customize navigation menu
  return menuItems.map(item => ({
    ...item,
    icon: getIconForMenuItem(item.label)
  }));
}
```

### Event Hooks for Behavior Customization

#### Before/After Navigation
```javascript
hooks: {
  beforeNavigate: async (from, to) => {
    // Check permissions, save state, etc.
    if (needsConfirmation(from)) {
      return confirm('Leave without saving?');
    }
    return true;
  },

  afterNavigate: (from, to) => {
    // Analytics, scroll behavior, etc.
    trackPageView(to.path);
  }
}
```

#### Form Submission
```javascript
beforeFormSubmit: async (formData, formType) => {
  // Validate, transform, or enhance form data
  return {
    ...formData,
    source: 'theme-custom'
  };
}
```

#### Error Handling
```javascript
onError: (error, errorInfo) => {
  // Custom error handling
  logErrorToService(error, errorInfo);
}
```

### Hook Execution Order

1. `onThemeInit` (once on app start)
2. `onThemeActivate` (when theme is activated)
3. `onPageLoad` (on each route change)
4. `beforeNavigate` → Navigation → `afterNavigate`
5. Data transform hooks (on data fetch)
6. `onSettingsChange` (on settings update)
7. `onThemeDeactivate` (when theme is switched)

---

## Content Type Support

### Course Display Templates

#### Course Card Component
```jsx
// src/components/course/CourseCard.jsx
export default function CourseCard({ course }) {
  const { settings } = useThemeSettings();

  return (
    <div className="theme-course-card">
      <div className="course-thumbnail">
        <img src={course.thumbnail} alt={course.title} />
        {settings.courses.showProgress && (
          <ProgressBar progress={course.progress} />
        )}
      </div>

      <div className="course-info">
        <h3>{course.title}</h3>
        <p>{course.description}</p>

        {settings.courses.showInstructor && (
          <div className="instructor">
            <img src={course.instructor.avatar} />
            <span>{course.instructor.name}</span>
          </div>
        )}

        <div className="course-meta">
          <span>{course.duration}</span>
          <span>{course.lessons} lessons</span>
          <span>${course.price}</span>
        </div>
      </div>
    </div>
  );
}
```

#### Course Grid Layout
```jsx
// src/components/course/CourseGrid.jsx
export default function CourseGrid({ courses }) {
  const { settings } = useThemeSettings();
  const columns = settings.courses.gridColumns || 3;

  return (
    <div
      className="course-grid"
      style={{
        gridTemplateColumns: `repeat(${columns}, 1fr)`
      }}
    >
      {courses.map(course => (
        <CourseCard key={course.id} course={course} />
      ))}
    </div>
  );
}
```

### Lesson Layouts

#### Video Lesson Layout
```jsx
// src/components/lesson/VideoLesson.jsx
export default function VideoLesson({ lesson }) {
  return (
    <div className="video-lesson-container">
      <div className="video-player">
        <VideoPlayer url={lesson.videoUrl} />
      </div>

      <div className="lesson-sidebar">
        <h2>{lesson.title}</h2>
        <p>{lesson.description}</p>

        <div className="lesson-resources">
          <h3>Resources</h3>
          <ResourceList resources={lesson.resources} />
        </div>

        <div className="lesson-navigation">
          <button>Previous Lesson</button>
          <button>Next Lesson</button>
        </div>
      </div>
    </div>
  );
}
```

#### Text Lesson Layout
```jsx
// src/components/lesson/TextLesson.jsx
export default function TextLesson({ lesson }) {
  return (
    <article className="text-lesson">
      <header>
        <h1>{lesson.title}</h1>
        <div className="lesson-meta">
          <span>{lesson.readTime} min read</span>
          <span>{lesson.author}</span>
        </div>
      </header>

      <div
        className="lesson-content prose"
        dangerouslySetInnerHTML={{ __html: lesson.content }}
      />

      <footer className="lesson-footer">
        <button>Mark as Complete</button>
        <button>Take Quiz</button>
      </footer>
    </article>
  );
}
```

### User Profile Templates

#### Profile Header
```jsx
// src/components/profile/ProfileHeader.jsx
export default function ProfileHeader({ user }) {
  return (
    <div className="profile-header">
      <div className="profile-cover">
        <img src={user.coverImage} alt="Cover" />
      </div>

      <div className="profile-info">
        <img
          src={user.avatar}
          alt={user.name}
          className="profile-avatar"
        />

        <div className="profile-details">
          <h1>{user.name}</h1>
          <p>{user.bio}</p>

          <div className="profile-stats">
            <div className="stat">
              <span className="value">{user.coursesCompleted}</span>
              <span className="label">Courses</span>
            </div>
            <div className="stat">
              <span className="value">{user.totalHours}</span>
              <span className="label">Hours</span>
            </div>
            <div className="stat">
              <span className="value">{user.certificates}</span>
              <span className="label">Certificates</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### Dashboard Layouts

#### Student Dashboard
```jsx
// src/components/dashboard/StudentDashboard.jsx
export default function StudentDashboard({ user, stats, courses }) {
  return (
    <div className="dashboard">
      <DashboardHeader user={user} />

      <div className="dashboard-grid">
        <StatCard
          title="Courses In Progress"
          value={stats.inProgress}
          icon="📚"
        />
        <StatCard
          title="Completed"
          value={stats.completed}
          icon="✅"
        />
        <StatCard
          title="Total Hours"
          value={stats.totalHours}
          icon="⏱️"
        />
        <StatCard
          title="Certificates"
          value={stats.certificates}
          icon="🎓"
        />
      </div>

      <div className="dashboard-content">
        <section>
          <h2>Continue Learning</h2>
          <CourseGrid courses={courses.inProgress} />
        </section>

        <section>
          <h2>Recommended</h2>
          <CourseGrid courses={courses.recommended} />
        </section>
      </div>
    </div>
  );
}
```

### Landing Page Templates

#### Hero Section
```jsx
// Defined in Puck components
// See puck/components.jsx for full implementation
```

---

## Testing Requirements

### Required Test Coverage

Themes MUST include tests covering:

1. **Component Rendering** - 80% minimum
2. **Responsive Behavior** - All breakpoints
3. **Accessibility** - WCAG 2.1 AA compliance
4. **Performance** - Lighthouse scores

### Visual Regression Testing

Use Playwright for visual regression tests:

```javascript
// tests/visual/header.spec.js
import { test, expect } from '@playwright/test';

test('Header displays correctly on desktop', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await expect(page.locator('header')).toHaveScreenshot('header-desktop.png');
});

test('Header displays correctly on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('http://localhost:3000');
  await expect(page.locator('header')).toHaveScreenshot('header-mobile.png');
});
```

### Accessibility Requirements

Themes MUST meet these accessibility standards:

#### WCAG 2.1 AA Compliance
- Color contrast ratio ≥ 4.5:1 for text
- Color contrast ratio ≥ 3:1 for UI components
- All interactive elements keyboard accessible
- Focus indicators visible
- ARIA labels on interactive elements
- Semantic HTML structure

#### Testing Tools
```javascript
// tests/a11y/accessibility.spec.js
import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

test('Homepage is accessible', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await injectAxe(page);
  await checkA11y(page);
});
```

### Performance Benchmarks

Theme MUST meet these performance targets:

| Metric | Target | Measurement |
|--------|--------|-------------|
| First Contentful Paint | < 1.5s | Lighthouse |
| Largest Contentful Paint | < 2.5s | Lighthouse |
| Total Blocking Time | < 300ms | Lighthouse |
| Cumulative Layout Shift | < 0.1 | Lighthouse |
| Time to Interactive | < 3.5s | Lighthouse |

### Test Script Template

```javascript
// tests/integration/theme.test.js
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '../src/context/ThemeProvider';
import Header from '../src/components/layout/Header';

describe('Theme Integration', () => {
  it('renders header with theme settings', () => {
    render(
      <ThemeProvider>
        <Header />
      </ThemeProvider>
    );

    expect(screen.getByRole('banner')).toBeInTheDocument();
  });

  it('applies primary color from theme settings', () => {
    const { container } = render(
      <ThemeProvider>
        <Header />
      </ThemeProvider>
    );

    const headerElement = container.querySelector('header');
    const styles = window.getComputedStyle(headerElement);
    expect(styles.backgroundColor).toBe('rgb(79, 70, 229)'); // #4F46E5
  });
});
```

---

## Documentation Requirements

### README Template

```markdown
# [Theme Name]

[Brief description of theme]

![Theme Screenshot](screenshot.png)

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

\`\`\`bash
# Installation instructions
\`\`\`

## Configuration

[Configuration options]

## Customization

[How to customize]

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

[License]

## Credits

[Credits and attributions]
```

### Setup Instructions

Documentation MUST include:

1. **Prerequisites**
   - Node.js version
   - Platform version
   - Dependencies

2. **Installation Steps**
   - Step-by-step guide
   - Code examples
   - Expected output

3. **Configuration**
   - All available settings
   - Default values
   - Usage examples

4. **Troubleshooting**
   - Common issues
   - Solutions
   - Support links

### Customization Guide

Include guides for:

1. **Changing Colors**
   ```javascript
   // Example of customizing theme colors
   ```

2. **Modifying Typography**
   ```css
   /* Example CSS for typography changes */
   ```

3. **Overriding Components**
   ```jsx
   // Example component override
   ```

4. **Adding Custom Puck Components**
   ```javascript
   // Example Puck component
   ```

### Troubleshooting Section

Common issues template:

```markdown
## Troubleshooting

### Issue: Theme not loading

**Symptoms**: Default theme displays instead of custom theme

**Solution**:
1. Check theme is in correct directory
2. Verify theme.json syntax
3. Clear cache and restart

### Issue: Styles not applying

**Symptoms**: Custom styles don't appear

**Solution**:
1. Check CSS import order
2. Verify CSS custom properties
3. Check for CSS specificity issues
```

---

## Deployment & Integration

### Theme Activation Process

1. **Copy theme to themes directory**
   ```bash
   cp -r your-theme themes/
   ```

2. **Install theme dependencies**
   ```bash
   cd themes/your-theme
   npm install
   ```

3. **Build theme (if required)**
   ```bash
   npm run build
   ```

4. **Activate via admin panel**
   - Navigate to Admin → Theme
   - Select theme from dropdown
   - Click "Activate"

### Integration Checklist

- [ ] Theme files in correct directory structure
- [ ] theme.json validates successfully
- [ ] All required dependencies installed
- [ ] No console errors on activation
- [ ] All pages render correctly
- [ ] Responsive behavior works across breakpoints
- [ ] Dark mode (if supported) functions correctly
- [ ] Settings panel displays and functions
- [ ] All tests pass
- [ ] Performance benchmarks met
- [ ] Accessibility standards met

### Build Process

If theme requires build step:

```json
// package.json
{
  "scripts": {
    "build": "vite build",
    "dev": "vite",
    "preview": "vite preview"
  }
}
```

### Environment Variables

Theme-specific environment variables:

```env
# .env.theme
THEME_NAME=your-theme-name
THEME_VERSION=1.0.0
THEME_CDN_URL=https://cdn.example.com
THEME_API_KEY=your-api-key (if needed)
```

### API Integration

If theme needs backend API:

```javascript
// src/api/theme-api.js
import axios from 'axios';

export const getThemeSettings = async () => {
  const response = await axios.get('/api/theme/settings');
  return response.data;
};

export const updateThemeSetting = async (key, value) => {
  const response = await axios.put(`/api/theme/settings/${key}`, { value });
  return response.data;
};
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-25 | Initial PRD template |

---

## Support & Resources

- **Documentation**: [Link to full documentation]
- **Issue Tracker**: [Link to issues]
- **Community Forum**: [Link to forum]
- **Email Support**: support@example.com

---

## Notes for AI Assistants

When creating a theme using this PRD:

1. Read this document completely before starting
2. Follow all required specifications exactly
3. Use the file structure template as-is
4. Include all required files (theme.json, README, LICENSE)
5. Implement at minimum the required override components
6. Test thoroughly before considering complete
7. Document all customization options
8. Provide clear installation instructions

**Remember**: The goal is to create a theme that works perfectly without any prior knowledge of the codebase. All information needed should be in this document and the theme files themselves.
