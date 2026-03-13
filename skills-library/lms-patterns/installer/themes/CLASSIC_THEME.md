# Classic Theme Specification

**Theme Name:** Classic
**Theme Slug:** `classic`
**Version:** 1.0.0
**Category:** Professional / Traditional
**Status:** Production-Ready (Current Default)

## Overview

The Classic theme is the default theme bundled with the MERN Community LMS. It provides a clean, professional appearance with customizable primary colors and an optional dark mode capability. The theme is designed to be timeless and trustworthy, making it ideal for traditional churches, seminaries, educational institutions, and ministry organizations seeking a professional online presence.

### Key Characteristics

- Clean, minimalist design with generous whitespace
- Typography-focused with clear hierarchy
- Customizable primary color via admin settings
- Dark gray/black accent color for buttons and emphasis
- Light backgrounds (white/gray-50) for content areas
- Subtle shadows and rounded corners
- Smooth transitions and hover effects

---

## 1. Color System

### Primary Color (Customizable)

The primary color is fully customizable via the Admin Settings panel. The default value is `#4F46E5` (indigo).

**How It Works:**

The theme uses CSS custom properties (variables) that are dynamically set by the ThemeContext. When an admin changes the primary color, the system automatically generates a complete color palette using lighten/darken functions.

**CSS Variable Mapping:**

```css
/* Primary color palette - generated from admin-selected color */
--color-primary-50:   /* 95% lightened */
--color-primary-100:  /* 85% lightened */
--color-primary-200:  /* 70% lightened */
--color-primary-300:  /* 50% lightened */
--color-primary-400:  /* 25% lightened */
--color-primary:      /* Base color (500 level) */
--color-primary-600:  /* 10% darkened */
--color-primary-700:  /* 25% darkened */
--color-primary-800:  /* 40% darkened */
--color-primary-900:  /* 55% darkened */
--color-primary-950:  /* 70% darkened */
```

**Palette Generation Algorithm:**

```javascript
// Lighten: Mix with white
lightenColor(hex, percent) {
  factor = percent / 100;
  r = rgb.r + (255 - rgb.r) * factor;
  g = rgb.g + (255 - rgb.g) * factor;
  b = rgb.b + (255 - rgb.b) * factor;
}

// Darken: Reduce RGB values
darkenColor(hex, percent) {
  factor = (100 - percent) / 100;
  r = rgb.r * factor;
  g = rgb.g * factor;
  b = rgb.b * factor;
}
```

### Secondary Color (Static)

The secondary color is a fixed fuchsia/purple palette used for accent elements and gradients:

```javascript
secondary: {
  50:  '#fdf4ff',
  100: '#fae8ff',
  200: '#f5d0fe',
  300: '#f0abfc',
  400: '#e879f9',
  500: '#d946ef',
  600: '#c026d3',
  700: '#a21caf',
  800: '#86198f',
  900: '#701a75',
  950: '#4a044e',
}
```

### Neutral Colors (Tailwind Gray Scale)

The theme uses Tailwind's default gray scale for text, backgrounds, and borders:

| Token | Hex | Usage |
|-------|-----|-------|
| gray-50 | #f9fafb | Page backgrounds, cards |
| gray-100 | #f3f4f6 | Alternate backgrounds |
| gray-200 | #e5e7eb | Borders, dividers |
| gray-300 | #d1d5db | Input borders |
| gray-400 | #9ca3af | Placeholder text |
| gray-500 | #6b7280 | Muted text |
| gray-600 | #4b5563 | Secondary text |
| gray-700 | #374151 | Body text |
| gray-800 | #1f2937 | Button hover |
| gray-900 | #111827 | Headings, primary buttons |

### Status Colors

| Color | Usage | Example Classes |
|-------|-------|-----------------|
| Green | Success, free courses, completed | `bg-green-500`, `bg-green-600`, `text-green-600` |
| Yellow | Warnings, intermediate level | `bg-yellow-500`, `text-yellow-600` |
| Red | Errors, danger zone, advanced level | `bg-red-500`, `text-red-600`, `bg-red-50` |
| Blue | Info, progress, highlights | `bg-blue-600`, `text-blue-600`, `bg-blue-100` |

---

## 2. Typography

### Font Stack

```javascript
fontFamily: {
  sans: ['Inter var', 'Inter', 'system-ui', 'sans-serif'],
}
```

The theme uses Inter as the primary typeface, falling back to system fonts for performance. Inter provides excellent readability at all sizes and includes variable font support.

### Type Scale (Tailwind Default)

| Class | Size | Usage |
|-------|------|-------|
| text-xs | 0.75rem (12px) | Labels, badges, fine print |
| text-sm | 0.875rem (14px) | Body text (secondary), form labels |
| text-base | 1rem (16px) | Body text (primary) |
| text-lg | 1.125rem (18px) | Subheadings, emphasis |
| text-xl | 1.25rem (20px) | Section subheadings |
| text-2xl | 1.5rem (24px) | Card headings |
| text-3xl | 1.875rem (30px) | Page headings |
| text-4xl | 2.25rem (36px) | Hero subheadings |
| text-5xl | 3rem (48px) | Hero headings (mobile) |
| text-6xl | 3.75rem (60px) | Hero headings (tablet) |
| text-7xl | 4.5rem (72px) | Hero headings (desktop) |

### Font Weights

| Weight | Class | Usage |
|--------|-------|-------|
| 300 | font-light | Hero headlines (large text) |
| 400 | font-normal | Body text |
| 500 | font-medium | Navigation links, buttons |
| 600 | font-semibold | Card headings, subheadings |
| 700 | font-bold | Page headings, emphasis |

### Line Heights

- `leading-tight` - Headings
- `leading-normal` - Body text
- `leading-relaxed` - Long-form content, descriptions

---

## 3. Component Styles

### Buttons

**Primary Button (Dark)**
```jsx
className="inline-flex items-center px-4 py-2 bg-gray-900 text-white
           text-sm font-medium rounded-lg hover:bg-gray-800
           transition-colors duration-200"
```

**Primary Button (Large)**
```jsx
className="inline-flex items-center px-8 py-4 bg-gray-900 text-white
           text-lg font-medium rounded-lg hover:bg-gray-800
           transition-colors duration-200"
```

**Secondary/Outline Button**
```jsx
className="inline-flex items-center px-4 py-2 border border-gray-300
           text-gray-700 font-medium rounded-lg hover:bg-gray-50
           transition-colors duration-200"
```

**Inverted Button (on dark backgrounds)**
```jsx
className="inline-flex items-center px-8 py-4 bg-white text-gray-900
           font-medium rounded-lg hover:bg-gray-100
           transition-colors duration-200"
```

**Accent Button (Green - Donate)**
```jsx
className="text-sm font-semibold px-5 py-2 bg-green-600 text-white
           rounded-lg hover:bg-green-700 transition-colors duration-200
           shadow-sm"
```

**Disabled State**
```jsx
className="... disabled:opacity-50 disabled:cursor-not-allowed"
```

### Cards

**Standard Card**
```jsx
className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
```

**Course Card**
```jsx
className="group relative bg-white rounded-2xl overflow-hidden shadow-lg
           hover:shadow-2xl transition-all duration-500 hover:scale-105"
```

**Interactive Card**
```jsx
className="bg-white rounded-lg shadow-sm hover:shadow-lg
           transition-shadow duration-300"
```

### Navigation

**Header**
- Fixed position with z-index 50
- White background with optional shadow on scroll
- Height: 6rem (96px / h-24)
- Border-bottom on scroll: `border-b border-gray-200`

**Desktop Nav Links**
```jsx
className="text-sm font-medium text-gray-600 hover:text-gray-900
           transition-colors duration-200"
// Active state
className="text-sm font-medium text-gray-900"
```

**User Dropdown**
```jsx
className="bg-white rounded-lg shadow-lg border border-gray-200 py-1"
// Items
className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
```

### Forms

**Input Fields**
```jsx
className="mt-1 block w-full px-3 py-2 border border-gray-300
           rounded-md shadow-sm focus:outline-none
           focus:ring-gray-900 focus:border-gray-900"
```

**Select Dropdowns**
```jsx
className="block w-full px-3 py-2 border border-gray-300
           rounded-md shadow-sm focus:outline-none
           focus:ring-gray-900 focus:border-gray-900"
```

**Checkboxes**
```jsx
className="h-4 w-4 text-gray-900 focus:ring-gray-900
           border-gray-300 rounded"
```

**Toggle Switches**
```jsx
// Container
className="relative inline-flex items-center cursor-pointer"
// Track
className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-gray-300
           rounded-full peer peer-checked:bg-gray-900"
// Thumb
className="after:absolute after:top-[2px] after:left-[2px]
           after:bg-white after:rounded-full after:h-5 after:w-5
           after:transition-all peer-checked:after:translate-x-full"
```

**Form Labels**
```jsx
className="block text-sm font-medium text-gray-700 mb-2"
```

### Tables

Tables use standard Tailwind patterns with:
- `divide-y divide-gray-200` for row separators
- `bg-gray-50` for header backgrounds
- `hover:bg-gray-50` for row hover states
- `text-sm text-gray-900` for primary content
- `text-sm text-gray-500` for secondary content

### Modals

```jsx
// Overlay
className="fixed inset-0 bg-black bg-opacity-50 flex items-center
           justify-center z-50 p-4"
// Modal Container
className="bg-white rounded-lg p-8 max-w-md w-full shadow-lg"
// Modal with Transition
className="transition-all duration-300 ease-out"
```

### Badges

**Level Badges**
```jsx
// Beginner
className="px-2 py-1 rounded-full text-xs font-semibold bg-green-500 text-white"
// Intermediate
className="px-2 py-1 rounded-full text-xs font-semibold bg-yellow-500 text-white"
// Advanced
className="px-2 py-1 rounded-full text-xs font-semibold bg-red-500 text-white"
```

**Status Badges**
```jsx
// Generic
className="inline-flex px-2 py-1 text-xs font-medium rounded-full
           bg-blue-100 text-blue-800"
```

---

## 4. Dark Mode Status

### Current Implementation: Not Implemented

Dark mode is **not currently implemented** in the Classic theme. While Tailwind CSS supports dark mode through the `dark:` prefix, only a few components (TemplateLibrary, QuestionnaireManager, PuckComponents, and PluginManager) have sporadic dark mode classes that are not consistently applied.

### Components with Partial Dark Mode Support

Based on code analysis, the following components have some `dark:` classes but are not systematically styled:
- `client/src/pages/admin/TemplateLibrary.jsx`
- `client/src/pages/admin/QuestionnaireManager.jsx`
- `client/src/components/questionnaire/*.jsx` (multiple files)
- `client/src/components/puck/PuckComponents.jsx`
- `client/src/pages/admin/PluginManager.jsx`

### What's Needed for Complete Dark Mode

See Section 11 for the implementation plan.

---

## 5. CSS Variables

### Currently Defined Variables

The theme dynamically sets the following CSS custom properties on `document.documentElement`:

```css
:root {
  /* Primary Color Palette (dynamic - set by ThemeContext) */
  --color-primary: #4F46E5;        /* Default indigo */
  --color-primary-50: /* calculated */
  --color-primary-100: /* calculated */
  --color-primary-200: /* calculated */
  --color-primary-300: /* calculated */
  --color-primary-400: /* calculated */
  --color-primary-600: /* calculated */
  --color-primary-700: /* calculated */
  --color-primary-800: /* calculated */
  --color-primary-900: /* calculated */
  --color-primary-950: /* calculated */
}
```

### Recommended Additional Variables (for future enhancement)

```css
:root {
  /* Background Colors */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f9fafb;
  --color-bg-tertiary: #f3f4f6;

  /* Text Colors */
  --color-text-primary: #111827;
  --color-text-secondary: #4b5563;
  --color-text-muted: #6b7280;

  /* Border Colors */
  --color-border-default: #e5e7eb;
  --color-border-dark: #d1d5db;

  /* Focus Ring */
  --color-focus: var(--color-primary);
}
```

---

## 6. Tailwind Configuration

### Current Configuration

**File:** `client/tailwind.config.js`

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,css}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: 'var(--color-primary-50, #f0f9ff)',
          100: 'var(--color-primary-100, #e0f2fe)',
          200: 'var(--color-primary-200, #bae6fd)',
          300: 'var(--color-primary-300, #7dd3fc)',
          400: 'var(--color-primary-400, #38bdf8)',
          500: 'var(--color-primary, #0ea5e9)',
          600: 'var(--color-primary-600, #0284c7)',
          700: 'var(--color-primary-700, #0369a1)',
          800: 'var(--color-primary-800, #075985)',
          900: 'var(--color-primary-900, #0c4a6e)',
          950: 'var(--color-primary-950, #082f49)',
        },
        secondary: {
          50: '#fdf4ff',
          100: '#fae8ff',
          200: '#f5d0fe',
          300: '#f0abfc',
          400: '#e879f9',
          500: '#d946ef',
          600: '#c026d3',
          700: '#a21caf',
          800: '#86198f',
          900: '#701a75',
          950: '#4a044e',
        },
      },
      fontFamily: {
        sans: ['Inter var', 'Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
```

### Notable Patterns

1. **CSS Variable Fallbacks:** Each primary color shade has a fallback value (sky blue palette) in case variables aren't set
2. **Extended, Not Replaced:** Colors are added via `extend`, preserving Tailwind's default colors
3. **No Dark Mode Config:** `darkMode` is not configured (could be 'class' or 'media')
4. **No Plugins:** No Tailwind plugins are currently used

---

## 7. Admin Customization Options

### Currently Available via Admin Panel

Administrators can customize the following through the Settings page:

#### Branding Tab (Theme Customizer)
| Setting | Key | Description |
|---------|-----|-------------|
| Primary Logo | `primary_logo` | Main site logo (header) |
| Admin Logo | `admin_logo` | Logo for admin panel |
| Auth Logo | `auth_logo` | Logo for login/register pages |
| Primary Color | `primary_color` | Main theme color (hex) |
| Site Name | `site_name` | Name shown in header/title |
| Site Tagline | `site_tagline` | Subtitle/tagline |
| Footer Text | `footer_text` | Copyright/footer message |
| Favicon | `favicon` | Browser tab icon |

#### SEO Settings
- Meta Title, Description, Keywords
- Open Graph settings (title, description, image, site name)
- Twitter Card settings (card type, title, description, image, handle)
- Canonical URL
- Site verification codes (Google, Bing)
- Organization name

### Settings Storage

Settings are stored in the database and fetched via `/api/settings`. The ThemeContext provides these values to components throughout the application.

```javascript
// ThemeContext default settings structure
{
  site_name: 'School of the Priests',
  site_tagline: 'Ministry',
  primary_logo: '/logo.png',
  admin_logo: '/logo.png',
  auth_logo: '/logo.png',
  primary_color: '#4F46E5',
  footer_text: '...',
  favicon: '/favicon.ico',
  // SEO fields...
}
```

---

## 8. Theme Manifest (theme.json)

Create the following manifest file to package the Classic theme for the installer's theme system:

**File:** `themes/classic/theme.json`

```json
{
  "name": "classic",
  "displayName": "Classic",
  "version": "1.0.0",
  "description": "A clean, professional theme with customizable primary colors and optional dark mode. Perfect for traditional churches, seminaries, and educational institutions seeking a timeless, trustworthy appearance.",
  "author": "MERN Community LMS Team",
  "category": "Professional",
  "tags": ["professional", "clean", "minimalist", "traditional", "church", "education"],
  "preview": {
    "thumbnail": "/themes/classic/preview.png",
    "screenshots": [
      "/themes/classic/screenshots/home.png",
      "/themes/classic/screenshots/courses.png",
      "/themes/classic/screenshots/dashboard.png",
      "/themes/classic/screenshots/admin.png"
    ]
  },
  "colors": {
    "primary": {
      "default": "#4F46E5",
      "customizable": true
    },
    "secondary": {
      "default": "#d946ef",
      "customizable": false
    },
    "accent": {
      "default": "#111827",
      "customizable": false
    }
  },
  "typography": {
    "fontFamily": "Inter var, Inter, system-ui, sans-serif",
    "headingWeight": "light",
    "bodyWeight": "normal"
  },
  "features": {
    "darkMode": false,
    "customColors": true,
    "customFonts": false,
    "animations": true,
    "gradients": true
  },
  "components": {
    "header": {
      "style": "fixed",
      "height": "96px",
      "background": "white"
    },
    "footer": {
      "style": "gradient",
      "columns": 4
    },
    "buttons": {
      "borderRadius": "8px",
      "style": "solid"
    },
    "cards": {
      "borderRadius": "8px",
      "shadow": "sm",
      "hoverEffect": true
    }
  },
  "installer": {
    "default": true,
    "recommended": true,
    "order": 1
  },
  "compatibility": {
    "minVersion": "1.0.0",
    "tailwind": "4.x"
  }
}
```

---

## 9. Page Appearance Descriptions

### Home Page

**Hero Section:**
- Large, light-weight typography (font-light) on white background
- Two-line headline with emphasis on second line (font-medium)
- Generous padding (py-24 to py-32)
- Two CTA buttons: primary (dark gray) and secondary (outline)
- Subtle scroll indicator animation at bottom

**Stats Section:**
- Gray background (bg-gray-50)
- 4-column grid with large numbers (text-3xl to text-4xl font-bold)
- Centered text alignment

**Features Section:**
- White background
- 3-column grid on larger screens
- Centered text with headings (font-semibold) and descriptions
- No icons (text-focused design)

**Featured Courses:**
- Gray background (bg-gray-50)
- Course cards with image placeholder, title, description, price
- Hover effect: slight scale and shadow increase

**Testimonials:**
- White background
- Cards with avatar (initials), name, role, and quoted content
- Gray-50 card background for subtle contrast

**CTA Section:**
- Dark background (bg-gray-900 text-white)
- Large heading with description
- Two buttons: inverted primary (white) and outline (white border)

### Course Listing Page

**Hero Section:**
- Dark background (bg-gray-900)
- Search input with blur effect background
- Title with accent color span

**Sidebar Filters:**
- White card with shadow
- Category, level, and price filter buttons
- Active state: dark background (bg-gray-900 text-white)
- Sticky positioning

**Course Grid:**
- 3-column layout on desktop
- Cards with image, badges (level, new), price tag
- Rating stars, instructor avatar, lesson count
- Full-width CTA button at card bottom

**Pagination:**
- Rounded buttons with active state highlighting

### Course Detail Page

**Hero Section:**
- Full-width dark background (bg-gray-900)
- Two-column layout: content left, image right
- Level and "New" badges
- Course metadata (duration, lessons, rating)
- Enroll button and wishlist button

**Tab Navigation:**
- Border-bottom style tabs
- Overview, Curriculum, Instructor, Reviews tabs
- Animated tab content transitions

### Student Dashboard

**Layout:**
- Full-width with max-w-7xl container
- Light gray page background

**Components:**
- Welcome message with user name
- "Resume Learning" gradient card (blue to indigo)
- Stats cards in 4-column grid (white cards with icons)
- Recent courses list with progress bars
- My Groups section with group cards
- Quick actions grid with icon + text links

### Admin Panel

**Layout:**
- Similar to student dashboard
- Full-width with max-w-7xl container

**Components:**
- Stats cards showing users, enrollments, courses, revenue
- Activity feed with type-specific icons
- Top courses list with rankings
- Quick actions grid (5-column on large screens)
- Tab-based settings interface

---

## 10. Strengths and Limitations

### Strengths

1. **Clean, Professional Aesthetic:** The minimalist design with generous whitespace creates a trustworthy, professional appearance suitable for educational and ministry contexts.

2. **Dynamic Primary Color:** Administrators can change the primary color without code modifications, allowing brand customization.

3. **Strong Typography Foundation:** Inter font family provides excellent readability and professional appearance across all sizes.

4. **Consistent Component Patterns:** Buttons, cards, and forms follow consistent styling patterns throughout the application.

5. **Responsive Design:** Components adapt well to different screen sizes with proper breakpoints.

6. **Smooth Transitions:** Hover effects and transitions (duration-200 to duration-500) provide a polished feel.

7. **Accessibility-Friendly Colors:** The dark-on-light contrast ratios generally meet WCAG standards.

8. **Tailwind CSS Integration:** Full utilization of Tailwind's utility classes makes customization straightforward.

### Limitations / Future Improvements

1. **No Dark Mode:** Currently, the theme only supports light mode. Users in low-light environments don't have an alternative.

2. **Limited Color Customization:** Only the primary color is customizable; secondary and accent colors are fixed.

3. **No Font Customization:** The Inter font is hardcoded; administrators cannot change typography.

4. **Inconsistent Dark Mode Classes:** Some components have sporadic dark: classes that don't form a complete system.

5. **No Theme Presets:** There's no way to save or load color preset configurations.

6. **Footer Not Customizable:** Footer content, sections, and social links are hardcoded rather than admin-configurable.

7. **No CSS Variable Consistency:** While primary colors use CSS variables, other semantic colors (backgrounds, text) do not.

8. **Missing Component Variants:** No official "outline," "ghost," or "link" button variants defined.

9. **No Animation Preferences:** No support for reduced-motion preferences.

10. **Static Secondary Color:** The fuchsia secondary palette may not suit all brand identities.

---

## 11. Dark Mode Implementation Plan

### Phase 1: Configuration Setup

1. **Enable Dark Mode in Tailwind:**
   ```javascript
   // tailwind.config.js
   export default {
     darkMode: 'class', // or 'media' for system preference
     // ...rest of config
   }
   ```

2. **Add Dark Mode Toggle to ThemeContext:**
   ```javascript
   const [darkMode, setDarkMode] = useState(false);

   useEffect(() => {
     if (darkMode) {
       document.documentElement.classList.add('dark');
     } else {
       document.documentElement.classList.remove('dark');
     }
   }, [darkMode]);
   ```

3. **Persist Preference:**
   - Store in localStorage
   - Optionally sync with user preferences in database

### Phase 2: CSS Variable Definitions

```css
:root {
  /* Light Mode */
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --text-primary: #111827;
  --text-secondary: #4b5563;
  --border-color: #e5e7eb;
}

.dark {
  /* Dark Mode */
  --bg-primary: #111827;
  --bg-secondary: #1f2937;
  --text-primary: #f9fafb;
  --text-secondary: #d1d5db;
  --border-color: #374151;
}
```

### Phase 3: Component Updates

Update key components with dark mode variants:

```jsx
// Example: Card Component
className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700
           text-gray-900 dark:text-gray-100"

// Example: Input Field
className="border-gray-300 dark:border-gray-600
           bg-white dark:bg-gray-700
           text-gray-900 dark:text-gray-100"
```

### Phase 4: Component Priority List

1. **High Priority (Core Layout):**
   - Header/Navigation
   - Footer
   - Main content containers
   - Sidebar (filters)

2. **Medium Priority (Common Components):**
   - Cards (course, group, stats)
   - Buttons (all variants)
   - Forms (inputs, selects, toggles)
   - Modals
   - Badges

3. **Lower Priority (Page-Specific):**
   - Dashboard widgets
   - Admin tables
   - Settings panels
   - Auth pages

### Phase 5: Testing Checklist

- [ ] All text has sufficient contrast (4.5:1 for normal, 3:1 for large)
- [ ] Images and icons are visible in both modes
- [ ] Form controls are clearly distinguishable
- [ ] Focus states are visible
- [ ] Transitions between modes are smooth
- [ ] User preference persists across sessions
- [ ] System preference detection works (if using 'media')

---

## 12. Integration with Installer Wizard

### Default Theme Selection

The Classic theme will be the **default and pre-selected** theme during installation. The installer wizard should:

1. **Theme Selection Step:**
   - Display Classic theme prominently as "Recommended"
   - Show preview thumbnail and key features
   - Allow selection of alternative themes (when available)

2. **Customization Step:**
   - Allow primary color selection during installation
   - Provide color preset options (indigo, blue, green, red, etc.)
   - Show live preview of selected color

3. **Initial Settings:**
   The installer should pre-populate these ThemeContext defaults:
   ```javascript
   {
     primary_color: '#4F46E5', // Or user-selected color
     site_name: '[User Input]',
     site_tagline: '[User Input]',
     // Other branding from installer wizard
   }
   ```

### Theme File Structure

For the installer to properly recognize and apply the Classic theme:

```
themes/
  classic/
    theme.json          # Theme manifest
    preview.png         # Thumbnail for selection UI
    screenshots/        # Preview images
      home.png
      courses.png
      dashboard.png
      admin.png
    README.md           # Theme documentation
```

### Installer API Integration

The installer should call the settings API to apply theme configuration:

```javascript
// During installation
await axios.post('/api/settings/primary_color', { value: selectedColor });
await axios.post('/api/settings/site_name', { value: siteName });
// ... other settings
```

---

## Appendix A: Color Palette Reference

### Default Primary (Indigo) - #4F46E5

| Shade | Hex | Preview |
|-------|-----|---------|
| 50 | #f2f1fe | Very light |
| 100 | #e6e4fd | Light |
| 200 | #c9c5fa | |
| 300 | #a79ff5 | |
| 400 | #7f75ed | |
| 500 | #4F46E5 | **Base** |
| 600 | #473fce | |
| 700 | #3b34ab | |
| 800 | #2f2989 | |
| 900 | #231f66 | |
| 950 | #171547 | Very dark |

### Secondary (Fuchsia)

| Shade | Hex |
|-------|-----|
| 500 | #d946ef |
| 600 | #c026d3 |
| 700 | #a21caf |

---

## Appendix B: Common Class Combinations

### Page Container
```
max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8
```

### Section Spacing
```
py-16 sm:py-24  // Standard section
py-24 sm:py-32  // Hero/featured section
```

### Card Base
```
bg-white rounded-lg shadow-sm border border-gray-200 p-6
```

### Button Base
```
inline-flex items-center justify-center px-4 py-2
text-sm font-medium rounded-md
transition-colors duration-200
focus:outline-none focus:ring-2 focus:ring-offset-2
```

### Form Input Base
```
block w-full px-3 py-2
border border-gray-300 rounded-md shadow-sm
focus:outline-none focus:ring-gray-900 focus:border-gray-900
```

---

*Document Version: 1.0.0*
*Last Updated: January 2026*
*For: MERN Community LMS Installer Wizard*
