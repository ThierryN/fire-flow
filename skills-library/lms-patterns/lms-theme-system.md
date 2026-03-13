# LMS Theme System Design Patterns

## Problem
Creating a WordPress-like theme system for a React LMS that allows non-developers to switch between visual themes without code changes.

---

## Solution: CSS Variables + Component Override Pattern

### Architecture Overview
```
themes/
├── classic/                    # Default theme (night/day mode)
│   ├── theme.json             # Theme metadata
│   ├── variables.css          # CSS custom properties
│   ├── components/            # Component overrides (optional)
│   └── assets/                # Theme-specific images
├── colorful-modern/           # Vibrant modern theme
│   ├── theme.json
│   ├── variables.css
│   └── assets/
└── theme-loader.js            # Dynamic theme loading
```

---

## Theme Configuration (theme.json)

```json
{
  "name": "Classic",
  "slug": "classic",
  "version": "1.0.0",
  "description": "Clean, professional theme with light/dark mode support",
  "author": "LMS Team",
  "screenshot": "screenshot.png",
  "supports": {
    "darkMode": true,
    "customColors": true,
    "customFonts": false
  },
  "defaults": {
    "primaryColor": "#3B82F6",
    "mode": "light"
  },
  "colorPresets": [
    { "name": "Blue", "primary": "#3B82F6", "secondary": "#1E40AF" },
    { "name": "Green", "primary": "#10B981", "secondary": "#047857" },
    { "name": "Purple", "primary": "#8B5CF6", "secondary": "#6D28D9" },
    { "name": "Rose", "primary": "#F43F5E", "secondary": "#BE123C" }
  ]
}
```

---

## CSS Variables System

### Classic Theme (Light Mode)
```css
/* themes/classic/variables.css */
:root {
  /* Primary Colors */
  --color-primary: #3B82F6;
  --color-primary-light: #60A5FA;
  --color-primary-dark: #2563EB;

  /* Background */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F3F4F6;
  --bg-tertiary: #E5E7EB;

  /* Text */
  --text-primary: #111827;
  --text-secondary: #6B7280;
  --text-muted: #9CA3AF;

  /* Borders */
  --border-color: #E5E7EB;
  --border-radius: 8px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);

  /* Spacing */
  --spacing-unit: 4px;

  /* Typography */
  --font-family: 'Inter', system-ui, sans-serif;
  --font-size-base: 16px;
  --line-height-base: 1.5;
}

/* Dark Mode */
[data-theme="dark"] {
  --bg-primary: #111827;
  --bg-secondary: #1F2937;
  --bg-tertiary: #374151;
  --text-primary: #F9FAFB;
  --text-secondary: #D1D5DB;
  --text-muted: #9CA3AF;
  --border-color: #374151;
}
```

### Colorful Modern Theme
```css
/* themes/colorful-modern/variables.css */
:root {
  /* Gradient-based primary */
  --color-primary: #8B5CF6;
  --color-secondary: #3B82F6;
  --gradient-primary: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);

  /* Vibrant backgrounds */
  --bg-primary: #FAFBFF;
  --bg-secondary: #F0F4FF;
  --bg-tertiary: #E8EDFF;

  /* Glassmorphism */
  --glass-bg: rgba(255, 255, 255, 0.8);
  --glass-blur: blur(10px);
  --glass-border: 1px solid rgba(255, 255, 255, 0.3);

  /* Enhanced shadows */
  --shadow-sm: 0 2px 8px rgba(139, 92, 246, 0.1);
  --shadow-md: 0 4px 16px rgba(139, 92, 246, 0.15);
  --shadow-lg: 0 8px 32px rgba(139, 92, 246, 0.2);

  /* Border radius (more rounded) */
  --border-radius: 16px;
  --border-radius-lg: 24px;

  /* Animation */
  --transition-fast: 150ms ease;
  --transition-normal: 300ms ease;
}
```

---

## Theme Loader

```javascript
// client/src/theme/ThemeLoader.js
import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('classic');
  const [mode, setMode] = useState('light');
  const [customColors, setCustomColors] = useState({});

  // Load theme CSS
  useEffect(() => {
    const loadTheme = async () => {
      // Remove old theme stylesheet
      const oldLink = document.getElementById('theme-styles');
      if (oldLink) oldLink.remove();

      // Load new theme
      const link = document.createElement('link');
      link.id = 'theme-styles';
      link.rel = 'stylesheet';
      link.href = `/themes/${theme}/variables.css`;
      document.head.appendChild(link);
    };

    loadTheme();
  }, [theme]);

  // Apply mode (light/dark)
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', mode);
  }, [mode]);

  // Apply custom colors
  useEffect(() => {
    Object.entries(customColors).forEach(([key, value]) => {
      document.documentElement.style.setProperty(`--color-${key}`, value);
    });
  }, [customColors]);

  const toggleMode = () => {
    setMode(m => m === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{
      theme,
      setTheme,
      mode,
      setMode,
      toggleMode,
      customColors,
      setCustomColors
    }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);
```

---

## Component Using Theme

```jsx
// client/src/components/Card.jsx
const Card = ({ children, className }) => {
  return (
    <div
      className={`card ${className}`}
      style={{
        backgroundColor: 'var(--bg-primary)',
        borderRadius: 'var(--border-radius)',
        boxShadow: 'var(--shadow-md)',
        border: '1px solid var(--border-color)',
        padding: 'calc(var(--spacing-unit) * 4)'
      }}
    >
      {children}
    </div>
  );
};
```

---

## Theme Selector UI

```jsx
// client/src/components/ThemeSelector.jsx
import { useTheme } from '../theme/ThemeLoader';

const ThemeSelector = () => {
  const { theme, setTheme, mode, toggleMode } = useTheme();

  const themes = [
    { slug: 'classic', name: 'Classic', preview: '/themes/classic/preview.png' },
    { slug: 'colorful-modern', name: 'Colorful Modern', preview: '/themes/colorful-modern/preview.png' }
  ];

  return (
    <div className="theme-selector">
      <h3>Choose Theme</h3>

      <div className="theme-grid">
        {themes.map(t => (
          <button
            key={t.slug}
            className={`theme-card ${theme === t.slug ? 'active' : ''}`}
            onClick={() => setTheme(t.slug)}
          >
            <img src={t.preview} alt={t.name} />
            <span>{t.name}</span>
          </button>
        ))}
      </div>

      <div className="mode-toggle">
        <label>
          <input
            type="checkbox"
            checked={mode === 'dark'}
            onChange={toggleMode}
          />
          Dark Mode
        </label>
      </div>
    </div>
  );
};
```

---

## Color Customization

```javascript
// Generate color palette from primary color
const generatePalette = (primaryHex) => {
  const hsl = hexToHSL(primaryHex);

  return {
    primary: primaryHex,
    primaryLight: hslToHex({ ...hsl, l: Math.min(hsl.l + 15, 90) }),
    primaryDark: hslToHex({ ...hsl, l: Math.max(hsl.l - 15, 10) }),
    primaryBg: hslToHex({ ...hsl, s: 30, l: 95 }),
    primaryBorder: hslToHex({ ...hsl, s: 40, l: 85 })
  };
};

// Usage
const palette = generatePalette('#8B5CF6');
// { primary: '#8B5CF6', primaryLight: '#A78BFA', primaryDark: '#6D28D9', ... }
```

---

## Theme Installation (Installer Integration)

```javascript
// server/installer/themes.js
const installTheme = async (themeSlug) => {
  // 1. Copy theme files to public directory
  const themePath = path.join(__dirname, 'themes', themeSlug);
  const publicPath = path.join(__dirname, '../public/themes', themeSlug);

  await fs.copy(themePath, publicPath);

  // 2. Read theme.json
  const themeJson = await fs.readJson(path.join(publicPath, 'theme.json'));

  // 3. Register in database
  await db('themes').insert({
    slug: themeSlug,
    name: themeJson.name,
    version: themeJson.version,
    config: JSON.stringify(themeJson),
    is_active: false
  });

  return themeJson;
};

const activateTheme = async (themeSlug) => {
  // Deactivate all themes
  await db('themes').update({ is_active: false });

  // Activate selected theme
  await db('themes').where({ slug: themeSlug }).update({ is_active: true });

  // Update site settings
  await db('settings').where({ key: 'active_theme' }).update({ value: themeSlug });
};
```

---

## Seed Themes

### Classic Theme
- Clean, professional design
- Light/dark mode toggle
- Customizable primary color
- Minimal animations
- Works on all devices
- Best for: Professional training, corporate LMS

### Colorful Modern Theme
- Vibrant gradients (purple to blue)
- Glassmorphism effects
- Smooth animations
- Bold typography
- Rounded corners
- Best for: Youth ministry, creative courses, modern audiences

---

## References
- Full documentation: `docs/installer/THEME_INSTALLER_INTEGRATION.md`
- Classic theme spec: `docs/installer/themes/CLASSIC_THEME.md`
- Colorful modern spec: `docs/installer/themes/COLORFUL_MODERN_THEME.md`
- Theme architecture: `docs/theme-system/THEME_SYSTEM_ARCHITECTURE.md`
