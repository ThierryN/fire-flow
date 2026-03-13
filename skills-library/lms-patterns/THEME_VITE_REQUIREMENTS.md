# Theme System - Critical Vite Configuration Requirements

**IMPORTANT:** These configurations are MANDATORY for theme components to compile properly.

---

## Required package.json Dependencies

### Core Dependencies (Minimum Versions)
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "tailwindcss": "^4.1.13",
    "@tailwindcss/postcss": "^4.1.13"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^5.0.3",
    "vite": "^7.1.2"
  }
}
```

**Why these matter:**
- **React 18.3.1+** - Required for JSX transform in theme files
- **Tailwind 4.1.13** - Uses CSS `@import` syntax (v3 won't work)
- **Vite 7.1.2+** - Supports themes folder outside client workspace
- **@vitejs/plugin-react 5.0.3+** - Can include external folders in JSX transform

---

## Required vite.config.js Configuration

### 1. React Plugin with Themes Folder Inclusion (CRITICAL)

**Location:** `client/vite.config.js`

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

const themesDir = path.resolve(__dirname, '../themes')

export default defineConfig({
  plugins: [react({
    // ⚠️ CRITICAL: Include themes folder in React JSX transform
    // Without this, theme .jsx files will NOT compile!
    include: [
      /\.[jt]sx?$/,
      new RegExp(themesDir.replace(/\\/g, '\\\\') + '.*\\.[jt]sx?$')
    ]
  })],

  // ... rest of config
})
```

**What this does:**
- Tells Vite's React plugin to transform JSX in the `../themes/` folder
- Without this, you get: `Failed to parse source for import analysis because the content contains invalid JS syntax`
- The regex escapes backslashes for Windows path compatibility

---

### 2. React Module Aliasing (CRITICAL)

**Location:** `client/vite.config.js` under `resolve.alias`

```javascript
export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@themes': fileURLToPath(new URL('../themes', import.meta.url)),

      // ⚠️ CRITICAL: Force themes to use client's React modules
      // Prevents "multiple React instances" errors
      'react': path.resolve(__dirname, 'node_modules/react'),
      'react/jsx-runtime': path.resolve(__dirname, 'node_modules/react/jsx-runtime'),
      'react-dom': path.resolve(__dirname, 'node_modules/react-dom')
    }
  }
})
```

**What this does:**
- Forces theme components to import React from `client/node_modules/react`
- Prevents duplicate React instances (causes "Hooks can only be called inside the body of a function component" errors)
- Required because themes folder is outside the client workspace

**Without this alias, you get:**
```
Error: Invalid hook call. Hooks can only be called inside the body of a function component.
This could happen for one of the following reasons:
1. You might have mismatching versions of React and the renderer (such as React DOM)
2. You might be breaking the Rules of Hooks
3. You might have more than one copy of React in the same app
```

---

### 3. CommonJS Options for Themes (CRITICAL)

**Location:** `client/vite.config.js` under `build.commonjsOptions`

```javascript
export default defineConfig({
  build: {
    commonjsOptions: {
      // ⚠️ CRITICAL: Include themes folder in CommonJS resolution
      include: [/themes/, /node_modules/]
    }
  }
})
```

**What this does:**
- Tells Rollup (Vite's production bundler) to process CommonJS modules from themes folder
- Required if any theme components use `require()` or CommonJS syntax
- Without this, production builds may fail with module resolution errors

---

### 4. File System Access (Already documented, but included for completeness)

**Location:** `client/vite.config.js` under `server.fs.allow`

```javascript
export default defineConfig({
  server: {
    fs: {
      allow: [
        '.',  // Default search paths
        path.resolve(__dirname, '../themes')  // Allow themes folder
      ]
    }
  }
})
```

**What this does:**
- Allows Vite dev server to serve files from the themes folder
- Without this: `The request url "/themes/..." is outside of Vite serving allow list`

---

## Complete vite.config.js Template for Theme Support

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'
import path from 'node:path'

const themesDir = path.resolve(__dirname, '../themes')

export default defineConfig({
  // 1. React plugin with themes folder inclusion
  plugins: [react({
    include: [
      /\.[jt]sx?$/,
      new RegExp(themesDir.replace(/\\/g, '\\\\') + '.*\\.[jt]sx?$')
    ]
  })],

  // 2. Optimize dependencies
  optimizeDeps: {
    exclude: ['lucide-react'],
    include: ['@measured/puck', '@headlessui/react', 'react', 'react-dom']
  },

  // 3. Build configuration with CommonJS options
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    commonjsOptions: {
      include: [/themes/, /node_modules/]
    }
  },

  // 4. Resolve aliases
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@themes': fileURLToPath(new URL('../themes', import.meta.url)),
      // Force themes to use client's React
      'react': path.resolve(__dirname, 'node_modules/react'),
      'react/jsx-runtime': path.resolve(__dirname, 'node_modules/react/jsx-runtime'),
      'react-dom': path.resolve(__dirname, 'node_modules/react-dom')
    }
  },

  // 5. Dev server configuration
  server: {
    port: 3000,
    fs: {
      allow: [
        '.',
        path.resolve(__dirname, '../themes')
      ]
    },
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/themes': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
```

---

## Verification Checklist

After configuring Vite, verify theme compilation works:

### Development Mode
```bash
cd client && npm run dev

# Check console for:
# ✅ "vite v7.x.x dev server running"
# ✅ No JSX parse errors
# ✅ No "invalid hook call" warnings
```

### Production Build
```bash
cd client && npm run build

# Check for:
# ✅ Build completes without errors
# ✅ No "Failed to resolve" errors for theme files
# ✅ Theme components included in bundle (grep for component names in dist/assets/*.js)
```

### Browser Console
```javascript
// Open dev console and check:
localStorage.setItem('activeTheme', 'celestial');
location.reload();

// Should see:
// ✅ [ThemeManager] Loaded X component overrides
// ✅ No React hook errors
// ✅ Theme components render correctly
```

---

## Common Configuration Errors

| Error Message | Missing Config | Fix |
|---------------|----------------|-----|
| "Failed to parse source... invalid JS syntax" | React plugin `include` | Add themes regex to `react({ include: [...] })` |
| "Invalid hook call" / "multiple React instances" | React module alias | Add `'react'` alias to resolve config |
| "Outside of Vite serving allow list" | `fs.allow` | Add themes folder to `server.fs.allow` |
| "Cannot find module" in production build | `commonjsOptions.include` | Add `/themes/` to build config |

---

## Integration with THEME_COMPLETE_DEVELOPER_GUIDE.md

This configuration should be added to Section 12 ("Production Build Requirements") of the main theme guide.

**Suggested addition location:**
After the existing Vite configuration section, add:

```markdown
### Critical Configuration Requirements

⚠️ **IMPORTANT:** The following Vite configuration is MANDATORY for theme compatibility.

See [THEME_VITE_REQUIREMENTS.md](./THEME_VITE_REQUIREMENTS.md) for complete details.

**Quick Checklist:**
- [ ] React plugin includes themes folder in JSX transform
- [ ] React modules aliased to client's node_modules
- [ ] CommonJS options include themes folder
- [ ] File system allows themes folder access
```

---

*Created: January 18, 2026*
*For: MERN Community LMS Theme System*
