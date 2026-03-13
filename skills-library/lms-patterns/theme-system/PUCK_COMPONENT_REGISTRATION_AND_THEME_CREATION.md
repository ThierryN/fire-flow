# Puck Component Registration & Theme Creation - Complete Guide

## The Problem

When creating theme-specific Puck page builder components (e.g., MountainHero, AuroraButton), the components appear to register correctly in the theme's `puck/index.jsx` but **never appear in the Puck editor sidebar**. Users cannot find or use the components despite the code looking correct.

### Error Symptoms
- Component files exist in `themes/<name>/puck/index.jsx`
- ThemeManager logs show "Registered Puck component: MountainHero" in console
- But the component does NOT appear in the PageEditor sidebar
- No error messages - just silently missing

### Why It Was Hard
- The ThemeManager registration path and PageEditor rendering path are **two separate systems**
- ThemeManager loads theme puck components dynamically at runtime
- But PageEditor uses `puckConfig.jsx` which is a **static build-time configuration**
- The two systems never merge - theme puck components loaded by ThemeManager are available for runtime rendering of saved pages, but the PageEditor sidebar only shows components from `puckConfig.jsx`
- This dual-system architecture is not obvious from reading either file in isolation

### Impact
- Theme developers waste hours wondering why components don't appear
- The pattern is undocumented and requires reading multiple files to understand
- Previous agents got stuck on this exact issue (Feb 2026)

---

## The Solution

### Root Cause

There are **TWO registration paths** for Puck components:

1. **Theme path** (`themes/<name>/puck/index.jsx`) - Loaded by `ThemeManager.js` at runtime. These components are available for **rendering saved pages** but do NOT appear in the editor sidebar.

2. **Editor path** (`client/src/components/puck/puckConfig.jsx`) - Static configuration consumed by the `PageEditor`. Only components registered HERE appear in the editor sidebar.

**To make components visible in the Puck editor, you MUST register in BOTH paths.**

### How to Fix: The 4-Step Registration Process

#### Step 1: Create Component File in `client/src/components/puck/components/`

Each component MUST have a `.schema` property with `fields` and `defaultProps`:

```jsx
// client/src/components/puck/components/MountainHero.jsx
import React from 'react';

const colors = {
    primary: '#735611',
    secondary: '#B39700',
    // ... theme palette
};

export const MountainHero = ({ title, subtitle, variant = 'fullWidth' }) => {
    // ... render logic
    return <div>...</div>;
};

// CRITICAL: .schema property is what puckConfig reads
MountainHero.schema = {
    fields: {
        variant: {
            type: 'select',
            label: 'Style Variant',
            options: [
                { value: 'fullWidth', label: 'Full Width' },
                { value: 'minimal', label: 'Minimal' }
            ]
        },
        title: { type: 'text', label: 'Title' },
        subtitle: { type: 'textarea', label: 'Subtitle' }
    },
    defaultProps: {
        variant: 'fullWidth',
        title: 'Welcome',
        subtitle: ''
    }
};
```

#### Step 2: Export from `PuckComponents.jsx`

```jsx
// client/src/components/puck/PuckComponents.jsx
// Add after existing exports:

// The Mountain Theme Components
export { MountainHero } from './components/MountainHero';
export { MountainCard } from './components/MountainCard';
export { MountainButton } from './components/MountainButton';
export { MountainSection } from './components/MountainSection';
export { MountainDivider } from './components/MountainDivider';
```

#### Step 3: Register in `puckConfig.jsx`

```jsx
// client/src/components/puck/puckConfig.jsx
// In the components object:

MountainHero: {
    render: Components.MountainHero,
    fields: Components.MountainHero.schema.fields,
    defaultProps: Components.MountainHero.schema.defaultProps,
},
MountainCard: {
    render: Components.MountainCard,
    fields: Components.MountainCard.schema.fields,
    defaultProps: Components.MountainCard.schema.defaultProps,
},
// ... etc for all components
```

#### Step 4: Add to a Category for Sidebar Visibility

```jsx
// In puckConfig.jsx categories object:
categories: {
    // ... existing categories
    mountain: {
        title: 'The Mountain Theme',
        components: [
            'MountainHero',
            'MountainCard',
            'MountainButton',
            'MountainSection',
            'MountainDivider'
        ],
    },
}
```

### Key Architectural Files

| File | Purpose |
|------|---------|
| `client/src/components/puck/puckConfig.jsx` | **Editor sidebar** - what users see and can drag |
| `client/src/components/puck/PuckComponents.jsx` | Component exports barrel file |
| `client/src/components/puck/components/*.jsx` | Individual component files with `.schema` |
| `themes/<name>/puck/index.jsx` | Theme-specific components for **runtime rendering** |
| `client/src/services/ThemeManager.js` | Loads theme puck components dynamically |

---

## Complete Theme Creation Workflow

### Theme Directory Structure

```
themes/the-mountain/
  theme.json              # Manifest (colors, fonts, layout, components list)
  styles/theme.css        # Custom CSS (@import fonts, variables, animations)
  components/
    index.js              # Exports Header, Footer, Hero
    layout/
      Header.jsx          # Header component override
      Footer.jsx          # Footer component override
  puck/
    index.jsx             # Theme puck components for runtime rendering
```

### Critical Rules for Theme Components

**Theme files in `/themes/` are OUTSIDE the Vite workspace.** They CANNOT use npm imports.

```jsx
// FORBIDDEN in theme component files:
import { Link } from 'react-router-dom';        // BREAKS BUILD
import axios from 'axios';                        // BREAKS BUILD
import { useTheme } from '@/context/ThemeContext'; // BREAKS BUILD

// REQUIRED: Use compatibility layer
import React, { useState, useEffect } from 'react'; // OK (aliased in vite.config)

const Link = ({ to, children, className }) =>
    <a href={to} className={className}>{children}</a>;

const useAuth = () => {
    const [auth, setAuth] = useState({ isAuthenticated: false, user: null });
    useEffect(() => {
        if (window.__LMS_AUTH__) setAuth(window.__LMS_AUTH__);
    }, []);
    return auth;
};

// Use fetch() for API calls, NOT axios
fetch('/api/menus').then(r => r.json()).then(d => setMenuItems(d.data));
```

**BUT** - Puck component files in `client/src/components/puck/components/` ARE inside the workspace. They CAN use standard React patterns. They just don't need npm imports since they're self-contained UI components.

### Mobile Sidebar Must Have `lg:hidden`

```jsx
<button className="lg:hidden" ... />                           // Toggle
<div className="lg:hidden fixed ..." ... />                    // Sidebar panel
{sidebarOpen && <div className="lg:hidden fixed inset-0" />}  // Backdrop
```

### Force-Adding Theme Files to Git

The `.gitignore` contains `themes/*/` but existing themes ARE tracked. Force-add:

```bash
git add -f themes/the-mountain/theme.json
git add -f themes/the-mountain/styles/theme.css
git add -f themes/the-mountain/components/index.js
git add -f themes/the-mountain/components/layout/Header.jsx
git add -f themes/the-mountain/components/layout/Footer.jsx
git add -f themes/the-mountain/puck/index.jsx
```

---

## Testing the Registration

1. Run `cd client && npm run build` - must pass without errors
2. Start dev server and navigate to Page Editor
3. Check the sidebar for the new category (e.g., "The Mountain Theme")
4. Verify all 5 components appear and can be dragged onto canvas
5. Verify each component's fields appear in the right panel when selected
6. Save a page and verify it renders correctly on the public site

---

## Prevention

- Always register in BOTH paths (theme puck/index.jsx AND client puckConfig.jsx)
- Use the `.schema` pattern on every Puck component (fields + defaultProps)
- Add to a `categories` group or the component won't show in the sidebar
- Check the AuroraButton component as a working reference

## Common Mistakes to Avoid

- Registering ONLY in `themes/<name>/puck/index.jsx` (won't show in editor)
- Forgetting the `.schema` property on the component (puckConfig reads it)
- Not adding to `categories` in puckConfig (component exists but is invisible)
- Using npm imports in theme files (build failure)
- Forgetting `git add -f` for gitignored theme directory

---

## Related Patterns

- [Puck Page Templates System](../PUCK_PAGE_TEMPLATES_SYSTEM.md)
- [Home Page Builder Guide](../../advanced-features/HOME_PAGE_BUILDER_GUIDE.md)
- [Theme System Architecture](./THEME_SYSTEM_ARCHITECTURE.md)

## Resources

- Reference implementation: `client/src/components/puck/components/AuroraButton.jsx`
- Theme reference: `themes/celestial/` (Header ~988 lines, Footer ~378 lines)
- Theme dev guide: `docs/THEME_COMPLETE_DEVELOPER_GUIDE.md`

## Time to Implement

- **New theme (Header + Footer + CSS + theme.json):** 2-3 hours
- **Puck components (5 components with color selectors):** 1-2 hours
- **Registration in puckConfig (if you know the pattern):** 15 minutes

## Difficulty Level

Stars: 4/5 - Hard to discover the dual-registration pattern; straightforward once known

---

**Author Notes:**
The Feb 2026 Mountain theme session burned ~45 minutes discovering why components weren't visible. The user had to hint "look at the skills folder" and "there was a rule about placing something ahead for puck to appear." The root cause is architectural: ThemeManager and PageEditor are decoupled systems. Once you know to register in client/src/components/puck/ (not just themes/), it takes 15 minutes. This skill should save the next agent that entire debugging cycle.
