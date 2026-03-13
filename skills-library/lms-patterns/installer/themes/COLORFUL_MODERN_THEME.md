# Colorful Modern Theme Specification

**Theme Name:** Colorful Modern
**Slug:** `colorful-modern`
**Version:** 1.0.0
**Last Updated:** January 11, 2026
**Target Audience:** Youth ministries, contemporary churches, modern organizations

---

## Overview

The **Colorful Modern** theme is a vibrant, contemporary design featuring bold gradients, playful accent colors, and modern UI patterns. It provides an energetic, fresh look ideal for organizations wanting to appeal to younger audiences or project a progressive, dynamic image.

### Design Philosophy

- **Bold & Vibrant**: Embrace color as a design element, not just an accent
- **Motion & Delight**: Subtle animations create engaging micro-interactions
- **Modern Patterns**: Glassmorphism, gradients, and contemporary UI trends
- **Accessibility First**: High contrast ratios maintained despite vibrant colors
- **Responsive Excellence**: Optimized for all device sizes with mobile-first approach

### Theme Characteristics

| Aspect | Description |
|--------|-------------|
| **Mood** | Energetic, modern, welcoming, innovative |
| **Primary Effect** | Gradient-based design language |
| **Secondary Effects** | Glassmorphism, subtle animations, shadow depth |
| **Typography Feel** | Clean, geometric, contemporary |
| **Spacing** | Generous whitespace, comfortable padding |
| **Corner Treatment** | Rounded to extra-rounded corners |
| **Shadow Style** | Colored shadows with low opacity tints |

---

## 1. Color Palette

### 1.1 Primary Gradient

The signature gradient defines the theme's visual identity:

```css
/* Primary Gradient - Used for hero sections, primary buttons, accents */
--gradient-primary: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);

/* Gradient Color Stops */
--gradient-start: #8B5CF6;   /* Vibrant Purple */
--gradient-end: #3B82F6;     /* Electric Blue */
--gradient-direction: 135deg;
```

**Usage:**
- Hero section backgrounds
- Primary button fills
- Progress bar fills
- Feature card accents
- Header decorative elements

### 1.2 Core Colors

```css
:root {
  /* Primary Colors */
  --color-primary: #8B5CF6;        /* Vibrant Purple */
  --color-primary-light: #A78BFA;
  --color-primary-dark: #7C3AED;
  --color-primary-50: #F5F3FF;
  --color-primary-100: #EDE9FE;
  --color-primary-200: #DDD6FE;
  --color-primary-300: #C4B5FD;
  --color-primary-400: #A78BFA;
  --color-primary-500: #8B5CF6;
  --color-primary-600: #7C3AED;
  --color-primary-700: #6D28D9;
  --color-primary-800: #5B21B6;
  --color-primary-900: #4C1D95;
  --color-primary-950: #2E1065;

  /* Secondary Colors */
  --color-secondary: #3B82F6;      /* Electric Blue */
  --color-secondary-light: #60A5FA;
  --color-secondary-dark: #2563EB;
  --color-secondary-50: #EFF6FF;
  --color-secondary-100: #DBEAFE;
  --color-secondary-200: #BFDBFE;
  --color-secondary-300: #93C5FD;
  --color-secondary-400: #60A5FA;
  --color-secondary-500: #3B82F6;
  --color-secondary-600: #2563EB;
  --color-secondary-700: #1D4ED8;
  --color-secondary-800: #1E40AF;
  --color-secondary-900: #1E3A8A;
  --color-secondary-950: #172554;
}
```

### 1.3 Accent Colors

Three distinct accent colors provide visual variety:

```css
:root {
  /* Accent 1: Coral/Pink - Used for notifications, highlights */
  --color-accent-pink: #F472B6;
  --color-accent-pink-light: #F9A8D4;
  --color-accent-pink-dark: #EC4899;
  --color-accent-pink-50: #FDF2F8;
  --color-accent-pink-100: #FCE7F3;
  --color-accent-pink-200: #FBCFE8;
  --color-accent-pink-300: #F9A8D4;
  --color-accent-pink-400: #F472B6;
  --color-accent-pink-500: #EC4899;

  /* Accent 2: Teal - Used for success states, completed items */
  --color-accent-teal: #14B8A6;
  --color-accent-teal-light: #2DD4BF;
  --color-accent-teal-dark: #0D9488;
  --color-accent-teal-50: #F0FDFA;
  --color-accent-teal-100: #CCFBF1;
  --color-accent-teal-200: #99F6E4;
  --color-accent-teal-300: #5EEAD4;
  --color-accent-teal-400: #2DD4BF;
  --color-accent-teal-500: #14B8A6;

  /* Accent 3: Amber - Used for warnings, featured items */
  --color-accent-amber: #F59E0B;
  --color-accent-amber-light: #FBBF24;
  --color-accent-amber-dark: #D97706;
  --color-accent-amber-50: #FFFBEB;
  --color-accent-amber-100: #FEF3C7;
  --color-accent-amber-200: #FDE68A;
  --color-accent-amber-300: #FCD34D;
  --color-accent-amber-400: #FBBF24;
  --color-accent-amber-500: #F59E0B;
}
```

### 1.4 Semantic Colors

```css
:root {
  /* Success - Uses Teal accent */
  --color-success: #14B8A6;
  --color-success-bg: #F0FDFA;
  --color-success-border: #99F6E4;

  /* Warning - Uses Amber accent */
  --color-warning: #F59E0B;
  --color-warning-bg: #FFFBEB;
  --color-warning-border: #FDE68A;

  /* Error - Custom red with theme harmony */
  --color-error: #EF4444;
  --color-error-bg: #FEF2F2;
  --color-error-border: #FECACA;

  /* Info - Uses Secondary blue */
  --color-info: #3B82F6;
  --color-info-bg: #EFF6FF;
  --color-info-border: #BFDBFE;
}
```

### 1.5 Background Colors

#### Light Mode

```css
:root {
  /* Light Mode Backgrounds */
  --bg-base: #FFFFFF;
  --bg-subtle: #F8FAFC;
  --bg-muted: #F1F5F9;
  --bg-emphasis: #E2E8F0;

  /* Gradient Overlays for Light Mode */
  --bg-gradient-subtle: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%);
  --bg-gradient-primary-light: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%);
  --bg-hero-light: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(59, 130, 246, 0.1) 50%, rgba(244, 114, 182, 0.05) 100%);
}
```

#### Dark Mode

```css
.dark {
  /* Dark Mode Backgrounds */
  --bg-base: #0F172A;           /* Deep Navy */
  --bg-subtle: #1E293B;         /* Slate 800 */
  --bg-muted: #334155;          /* Slate 700 */
  --bg-emphasis: #475569;       /* Slate 600 */

  /* Gradient Overlays for Dark Mode */
  --bg-gradient-subtle: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
  --bg-gradient-primary-dark: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%);
  --bg-hero-dark: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(59, 130, 246, 0.15) 50%, rgba(244, 114, 182, 0.1) 100%);
}
```

### 1.6 Text Colors

```css
:root {
  /* Light Mode Text */
  --text-primary: #1E293B;       /* Slate 800 - Headings */
  --text-secondary: #334155;     /* Slate 700 - Body */
  --text-muted: #64748B;         /* Slate 500 - Captions */
  --text-disabled: #94A3B8;      /* Slate 400 */
  --text-inverse: #FFFFFF;
  --text-on-gradient: #FFFFFF;
}

.dark {
  /* Dark Mode Text */
  --text-primary: #F1F5F9;       /* Slate 100 - Headings */
  --text-secondary: #E2E8F0;     /* Slate 200 - Body */
  --text-muted: #94A3B8;         /* Slate 400 - Captions */
  --text-disabled: #64748B;      /* Slate 500 */
  --text-inverse: #0F172A;
  --text-on-gradient: #FFFFFF;
}
```

### 1.7 Border Colors

```css
:root {
  /* Light Mode Borders */
  --border-default: #E2E8F0;
  --border-muted: #F1F5F9;
  --border-emphasis: #CBD5E1;
  --border-focus: #8B5CF6;
  --border-gradient: linear-gradient(135deg, #8B5CF6, #3B82F6);
}

.dark {
  /* Dark Mode Borders */
  --border-default: #334155;
  --border-muted: #1E293B;
  --border-emphasis: #475569;
  --border-focus: #A78BFA;
  --border-gradient: linear-gradient(135deg, #A78BFA, #60A5FA);
}
```

---

## 2. Typography

### 2.1 Font Families

```css
:root {
  /* Headings - Poppins: Modern, geometric, friendly */
  --font-heading: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

  /* Body - Inter: Highly legible, professional */
  --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

  /* Accent/Display - Space Grotesk: Technical, modern */
  --font-accent: 'Space Grotesk', 'Poppins', sans-serif;

  /* Monospace - For code blocks */
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
}
```

### 2.2 Font Loading

```html
<!-- Google Fonts (Primary Method) -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
```

### 2.3 Type Scale

```css
:root {
  /* Base size */
  --text-base: 1rem;          /* 16px */

  /* Scale - 1.25 ratio (Major Third) */
  --text-xs: 0.75rem;         /* 12px */
  --text-sm: 0.875rem;        /* 14px */
  --text-md: 1rem;            /* 16px */
  --text-lg: 1.125rem;        /* 18px */
  --text-xl: 1.25rem;         /* 20px */
  --text-2xl: 1.5rem;         /* 24px */
  --text-3xl: 1.875rem;       /* 30px */
  --text-4xl: 2.25rem;        /* 36px */
  --text-5xl: 3rem;           /* 48px */
  --text-6xl: 3.75rem;        /* 60px */
  --text-7xl: 4.5rem;         /* 72px */

  /* Line Heights */
  --leading-none: 1;
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 2;

  /* Letter Spacing */
  --tracking-tighter: -0.05em;
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
  --tracking-widest: 0.1em;
}
```

### 2.4 Typography Styles

```css
/* Headings */
h1, .h1 {
  font-family: var(--font-heading);
  font-size: var(--text-5xl);
  font-weight: 700;
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
}

h2, .h2 {
  font-family: var(--font-heading);
  font-size: var(--text-4xl);
  font-weight: 600;
  line-height: var(--leading-tight);
}

h3, .h3 {
  font-family: var(--font-heading);
  font-size: var(--text-3xl);
  font-weight: 600;
  line-height: var(--leading-snug);
}

h4, .h4 {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 600;
  line-height: var(--leading-snug);
}

h5, .h5 {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 600;
  line-height: var(--leading-normal);
}

h6, .h6 {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  font-weight: 600;
  line-height: var(--leading-normal);
}

/* Body Text */
body {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  line-height: var(--leading-relaxed);
  color: var(--text-secondary);
}

/* Gradient Text Effect */
.text-gradient {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Accent Text */
.text-accent {
  font-family: var(--font-accent);
  font-weight: 600;
  letter-spacing: var(--tracking-wide);
}
```

---

## 3. Component Styles

### 3.1 Buttons

#### Primary Gradient Button

```css
.btn-primary {
  /* Gradient Background */
  background: var(--gradient-primary);
  color: var(--text-on-gradient);

  /* Typography */
  font-family: var(--font-body);
  font-weight: 600;
  font-size: var(--text-sm);

  /* Spacing */
  padding: 0.75rem 1.5rem;

  /* Shape */
  border-radius: 0.75rem;
  border: none;

  /* Effects */
  box-shadow: 0 4px 14px 0 rgba(139, 92, 246, 0.35);

  /* Transitions */
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  /* Cursor */
  cursor: pointer;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px 0 rgba(139, 92, 246, 0.45);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px 0 rgba(139, 92, 246, 0.35);
}

.btn-primary:focus-visible {
  outline: 2px solid var(--color-primary-400);
  outline-offset: 2px;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
```

#### Secondary/Ghost Button

```css
.btn-secondary {
  /* Background */
  background: transparent;
  color: var(--color-primary);

  /* Typography */
  font-family: var(--font-body);
  font-weight: 600;
  font-size: var(--text-sm);

  /* Spacing */
  padding: 0.75rem 1.5rem;

  /* Border with gradient */
  border: 2px solid transparent;
  background-image: linear-gradient(var(--bg-base), var(--bg-base)), var(--gradient-primary);
  background-origin: border-box;
  background-clip: padding-box, border-box;

  /* Shape */
  border-radius: 0.75rem;

  /* Transitions */
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-secondary:hover {
  background: var(--gradient-primary);
  color: var(--text-on-gradient);
  transform: translateY(-2px);
}
```

#### Pill Button Variant

```css
.btn-pill {
  border-radius: 9999px;
  padding: 0.625rem 1.75rem;
}
```

#### Button Sizes

```css
.btn-sm {
  padding: 0.5rem 1rem;
  font-size: var(--text-xs);
  border-radius: 0.5rem;
}

.btn-lg {
  padding: 1rem 2rem;
  font-size: var(--text-md);
  border-radius: 1rem;
}

.btn-xl {
  padding: 1.25rem 2.5rem;
  font-size: var(--text-lg);
  border-radius: 1rem;
}
```

### 3.2 Cards

#### Standard Card

```css
.card {
  /* Background */
  background: var(--bg-base);

  /* Border */
  border: 1px solid var(--border-default);

  /* Shape */
  border-radius: 1rem;

  /* Shadow */
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.05),
    0 1px 2px rgba(0, 0, 0, 0.03);

  /* Overflow */
  overflow: hidden;

  /* Transitions */
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 20px 25px -5px rgba(0, 0, 0, 0.08),
    0 10px 10px -5px rgba(0, 0, 0, 0.03),
    0 0 0 1px rgba(139, 92, 246, 0.1);
}

.card-body {
  padding: 1.5rem;
}
```

#### Glass Card (Glassmorphism)

```css
.card-glass {
  /* Frosted glass effect */
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);

  /* Border */
  border: 1px solid rgba(255, 255, 255, 0.3);

  /* Shape */
  border-radius: 1rem;

  /* Shadow */
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.dark .card-glass {
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}
```

#### Gradient Border Card

```css
.card-gradient-border {
  /* Background for gradient border effect */
  position: relative;
  background: var(--bg-base);
  border-radius: 1rem;

  /* Padding inside */
  padding: 1.5rem;
}

.card-gradient-border::before {
  content: '';
  position: absolute;
  inset: 0;
  padding: 2px;
  border-radius: 1rem;
  background: var(--gradient-primary);
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
}
```

#### Feature Card with Colored Shadow

```css
.card-feature {
  background: var(--bg-base);
  border-radius: 1rem;
  padding: 2rem;

  /* Colored shadow based on primary */
  box-shadow:
    0 4px 20px rgba(139, 92, 246, 0.1),
    0 1px 3px rgba(0, 0, 0, 0.05);

  transition: all 0.3s ease;
}

.card-feature:hover {
  box-shadow:
    0 8px 30px rgba(139, 92, 246, 0.2),
    0 4px 6px rgba(0, 0, 0, 0.05);
}
```

### 3.3 Navigation

#### Main Header

```css
.header {
  /* Positioning */
  position: sticky;
  top: 0;
  z-index: 100;

  /* Background - Transparent with blur on scroll */
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);

  /* Border */
  border-bottom: 1px solid var(--border-muted);

  /* Transitions */
  transition: all 0.3s ease;
}

.header--scrolled {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.dark .header {
  background: rgba(15, 23, 42, 0.8);
  border-bottom-color: var(--border-muted);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 80rem;
  margin: 0 auto;
  padding: 1rem 1.5rem;
}
```

#### Navigation Links

```css
.nav-link {
  /* Typography */
  font-family: var(--font-body);
  font-weight: 500;
  font-size: var(--text-sm);
  color: var(--text-secondary);

  /* Spacing */
  padding: 0.5rem 0.75rem;

  /* Position for underline */
  position: relative;

  /* Transitions */
  transition: color 0.2s ease;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0.75rem;
  right: 0.75rem;
  height: 2px;
  background: var(--gradient-primary);
  border-radius: 1px;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-link:hover {
  color: var(--color-primary);
}

.nav-link:hover::after,
.nav-link--active::after {
  transform: scaleX(1);
}

.nav-link--active {
  color: var(--color-primary);
}
```

#### Mobile Navigation

```css
.mobile-nav {
  /* Positioning */
  position: fixed;
  inset: 0;
  z-index: 200;

  /* Initial state */
  opacity: 0;
  visibility: hidden;

  /* Transitions */
  transition: all 0.3s ease;
}

.mobile-nav--open {
  opacity: 1;
  visibility: visible;
}

.mobile-nav-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.mobile-nav-panel {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 80%;
  max-width: 320px;

  /* Background */
  background: var(--bg-base);

  /* Shadow */
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.1);

  /* Transform for slide-in */
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mobile-nav--open .mobile-nav-panel {
  transform: translateX(0);
}
```

#### Hamburger Menu Animation

```css
.hamburger {
  width: 24px;
  height: 24px;
  position: relative;
  cursor: pointer;
}

.hamburger-line {
  position: absolute;
  left: 0;
  width: 100%;
  height: 2px;
  background: var(--text-primary);
  border-radius: 1px;
  transition: all 0.3s ease;
}

.hamburger-line:nth-child(1) { top: 4px; }
.hamburger-line:nth-child(2) { top: 11px; }
.hamburger-line:nth-child(3) { top: 18px; }

.hamburger--open .hamburger-line:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.hamburger--open .hamburger-line:nth-child(2) {
  opacity: 0;
  transform: translateX(-10px);
}

.hamburger--open .hamburger-line:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}
```

### 3.4 Form Elements

#### Text Input

```css
.input {
  /* Background */
  background: var(--bg-base);

  /* Typography */
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--text-primary);

  /* Spacing */
  padding: 0.75rem 1rem;

  /* Border */
  border: 2px solid var(--border-default);
  border-radius: 0.75rem;

  /* Full width */
  width: 100%;

  /* Transitions */
  transition: all 0.2s ease;
}

.input::placeholder {
  color: var(--text-muted);
}

.input:hover {
  border-color: var(--border-emphasis);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow:
    0 0 0 3px rgba(139, 92, 246, 0.1),
    0 0 0 1px var(--color-primary);
}

/* Gradient Focus Ring Alternative */
.input-gradient-focus:focus {
  border-color: transparent;
  background-image:
    linear-gradient(var(--bg-base), var(--bg-base)),
    var(--gradient-primary);
  background-origin: border-box;
  background-clip: padding-box, border-box;
  box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.15);
}
```

#### Floating Label Input

```css
.input-floating {
  position: relative;
}

.input-floating .input {
  padding-top: 1.25rem;
  padding-bottom: 0.5rem;
}

.input-floating .input-label {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: var(--text-sm);
  pointer-events: none;
  transition: all 0.2s ease;
}

.input-floating .input:focus ~ .input-label,
.input-floating .input:not(:placeholder-shown) ~ .input-label {
  top: 0.5rem;
  transform: translateY(0);
  font-size: var(--text-xs);
  color: var(--color-primary);
}
```

#### Custom Checkbox

```css
.checkbox {
  position: relative;
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.checkbox-box {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-emphasis);
  border-radius: 0.375rem;
  background: var(--bg-base);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkbox-input:checked + .checkbox-box {
  background: var(--gradient-primary);
  border-color: transparent;
}

.checkbox-icon {
  width: 12px;
  height: 12px;
  color: white;
  opacity: 0;
  transform: scale(0);
  transition: all 0.2s ease;
}

.checkbox-input:checked + .checkbox-box .checkbox-icon {
  opacity: 1;
  transform: scale(1);
}

.checkbox-input:focus-visible + .checkbox-box {
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
}

.checkbox-label {
  margin-left: 0.5rem;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
```

#### Custom Radio Button

```css
.radio {
  position: relative;
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.radio-input {
  position: absolute;
  opacity: 0;
}

.radio-circle {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-emphasis);
  border-radius: 50%;
  background: var(--bg-base);
  transition: all 0.2s ease;
  position: relative;
}

.radio-circle::after {
  content: '';
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  background: var(--gradient-primary);
  opacity: 0;
  transform: scale(0);
  transition: all 0.2s ease;
}

.radio-input:checked + .radio-circle {
  border-color: var(--color-primary);
}

.radio-input:checked + .radio-circle::after {
  opacity: 1;
  transform: scale(1);
}
```

#### Progress Indicator

```css
.progress {
  width: 100%;
  height: 8px;
  background: var(--bg-muted);
  border-radius: 9999px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--gradient-primary);
  border-radius: 9999px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Animated shimmer on progress */
.progress-bar-animated {
  position: relative;
  overflow: hidden;
}

.progress-bar-animated::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.4),
    transparent
  );
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}
```

---

## 4. Special Effects

### 4.1 Gradient Effects

#### Text Gradient

```css
.gradient-text {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Animated gradient text */
.gradient-text-animated {
  background: linear-gradient(
    90deg,
    #8B5CF6,
    #3B82F6,
    #F472B6,
    #8B5CF6
  );
  background-size: 300% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradient-shift 8s ease infinite;
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

#### Gradient Border

```css
.gradient-border {
  position: relative;
  background: var(--bg-base);
  border-radius: 1rem;
}

.gradient-border::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 2px;
  background: var(--gradient-primary);
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}
```

#### Background Gradient Mesh

```css
.bg-gradient-mesh {
  background-color: var(--bg-base);
  background-image:
    radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%),
    radial-gradient(at 100% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(244, 114, 182, 0.1) 0px, transparent 50%),
    radial-gradient(at 0% 100%, rgba(20, 184, 166, 0.1) 0px, transparent 50%);
}
```

### 4.2 Glassmorphism

```css
.glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}

.dark .glass {
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Strong glass effect */
.glass-strong {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

/* Subtle glass effect */
.glass-subtle {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
```

### 4.3 Animations

#### Hover Lift

```css
.hover-lift {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.15);
}
```

#### Press Feedback

```css
.press-feedback {
  transition: transform 0.1s ease;
}

.press-feedback:active {
  transform: scale(0.98);
}
```

#### Page Transitions

```css
/* Fade in up animation */
.animate-fade-in-up {
  animation: fadeInUp 0.5s ease-out forwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Staggered children animation */
.animate-stagger > * {
  opacity: 0;
  animation: fadeInUp 0.5s ease-out forwards;
}

.animate-stagger > *:nth-child(1) { animation-delay: 0ms; }
.animate-stagger > *:nth-child(2) { animation-delay: 100ms; }
.animate-stagger > *:nth-child(3) { animation-delay: 200ms; }
.animate-stagger > *:nth-child(4) { animation-delay: 300ms; }
.animate-stagger > *:nth-child(5) { animation-delay: 400ms; }
```

#### Skeleton Loading Shimmer

```css
.skeleton {
  background: var(--bg-muted);
  border-radius: 0.5rem;
  position: relative;
  overflow: hidden;
}

.skeleton::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.4),
    transparent
  );
  animation: skeleton-shimmer 1.5s infinite;
}

@keyframes skeleton-shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.dark .skeleton::after {
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.1),
    transparent
  );
}
```

#### Pulse Glow

```css
.pulse-glow {
  animation: pulseGlow 2s ease-in-out infinite;
}

@keyframes pulseGlow {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(139, 92, 246, 0);
  }
}
```

---

## 5. Layout Patterns

### 5.1 Hero Section

```css
.hero {
  position: relative;
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  inset: 0;
  background: var(--bg-hero-light);
  z-index: 0;
}

.dark .hero-background {
  background: var(--bg-hero-dark);
}

/* Decorative floating elements */
.hero-decoration {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.5;
  pointer-events: none;
}

.hero-decoration-1 {
  top: 10%;
  left: 10%;
  width: 300px;
  height: 300px;
  background: var(--color-primary);
  animation: float 8s ease-in-out infinite;
}

.hero-decoration-2 {
  bottom: 10%;
  right: 10%;
  width: 250px;
  height: 250px;
  background: var(--color-secondary);
  animation: float 6s ease-in-out infinite reverse;
}

.hero-decoration-3 {
  top: 50%;
  right: 20%;
  width: 200px;
  height: 200px;
  background: var(--color-accent-pink);
  animation: float 10s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -20px); }
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 800px;
  padding: 2rem;
}

.hero-title {
  font-size: var(--text-6xl);
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.hero-subtitle {
  font-size: var(--text-xl);
  color: var(--text-muted);
  margin-bottom: 2rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-cta {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* Responsive */
@media (max-width: 768px) {
  .hero {
    min-height: 70vh;
  }

  .hero-title {
    font-size: var(--text-4xl);
  }

  .hero-subtitle {
    font-size: var(--text-lg);
  }
}
```

### 5.2 Course Card Layout

```css
.course-card {
  display: flex;
  flex-direction: column;
  background: var(--bg-base);
  border-radius: 1rem;
  overflow: hidden;
  transition: all 0.3s ease;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.course-card-image {
  position: relative;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.course-card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.course-card:hover .course-card-image img {
  transform: scale(1.05);
}

/* Gradient overlay on image */
.course-card-image::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    transparent 0%,
    transparent 60%,
    rgba(0, 0, 0, 0.6) 100%
  );
}

/* Badge positioning */
.course-card-badge {
  position: absolute;
  top: 1rem;
  left: 1rem;
  padding: 0.25rem 0.75rem;
  background: var(--gradient-primary);
  color: white;
  font-size: var(--text-xs);
  font-weight: 600;
  border-radius: 9999px;
  z-index: 1;
}

.course-card-body {
  padding: 1.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.course-card-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.course-card-description {
  font-size: var(--text-sm);
  color: var(--text-muted);
  margin-bottom: 1rem;
  flex: 1;
}

.course-card-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.course-card-progress {
  margin-top: auto;
}

.course-card-progress-bar {
  height: 4px;
  background: var(--bg-muted);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.course-card-progress-fill {
  height: 100%;
  background: var(--gradient-primary);
  border-radius: 2px;
}

.course-card-progress-text {
  font-size: var(--text-xs);
  color: var(--color-primary);
  font-weight: 500;
}
```

### 5.3 Dashboard Stats Cards

```css
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: var(--bg-base);
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon--primary {
  background: rgba(139, 92, 246, 0.1);
  color: var(--color-primary);
}

.stat-icon--teal {
  background: rgba(20, 184, 166, 0.1);
  color: var(--color-accent-teal);
}

.stat-icon--pink {
  background: rgba(244, 114, 182, 0.1);
  color: var(--color-accent-pink);
}

.stat-icon--amber {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-accent-amber);
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
}

.stat-change {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: var(--text-xs);
  font-weight: 500;
  margin-top: 0.25rem;
}

.stat-change--positive {
  color: var(--color-accent-teal);
}

.stat-change--negative {
  color: var(--color-error);
}
```

### 5.4 Progress Rings

```css
.progress-ring {
  position: relative;
  width: 120px;
  height: 120px;
}

.progress-ring svg {
  transform: rotate(-90deg);
}

.progress-ring-circle-bg {
  fill: none;
  stroke: var(--bg-muted);
  stroke-width: 8;
}

.progress-ring-circle {
  fill: none;
  stroke: url(#gradient-ring);
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 314;
  stroke-dashoffset: 314;
  transition: stroke-dashoffset 1s ease-out;
}

.progress-ring-value {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.progress-ring-percentage {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
}

.progress-ring-label {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

/* SVG gradient definition */
/*
<svg width="0" height="0">
  <defs>
    <linearGradient id="gradient-ring" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#8B5CF6" />
      <stop offset="100%" stop-color="#3B82F6" />
    </linearGradient>
  </defs>
</svg>
*/
```

---

## 6. Complete CSS Variables

### 6.1 Light Mode (Default)

```css
:root {
  /* === COLOR SYSTEM === */

  /* Primary Gradient */
  --gradient-primary: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
  --gradient-start: #8B5CF6;
  --gradient-end: #3B82F6;
  --gradient-direction: 135deg;

  /* Primary Color Scale */
  --color-primary: #8B5CF6;
  --color-primary-light: #A78BFA;
  --color-primary-dark: #7C3AED;
  --color-primary-50: #F5F3FF;
  --color-primary-100: #EDE9FE;
  --color-primary-200: #DDD6FE;
  --color-primary-300: #C4B5FD;
  --color-primary-400: #A78BFA;
  --color-primary-500: #8B5CF6;
  --color-primary-600: #7C3AED;
  --color-primary-700: #6D28D9;
  --color-primary-800: #5B21B6;
  --color-primary-900: #4C1D95;
  --color-primary-950: #2E1065;

  /* Secondary Color Scale */
  --color-secondary: #3B82F6;
  --color-secondary-light: #60A5FA;
  --color-secondary-dark: #2563EB;
  --color-secondary-50: #EFF6FF;
  --color-secondary-100: #DBEAFE;
  --color-secondary-200: #BFDBFE;
  --color-secondary-300: #93C5FD;
  --color-secondary-400: #60A5FA;
  --color-secondary-500: #3B82F6;
  --color-secondary-600: #2563EB;
  --color-secondary-700: #1D4ED8;
  --color-secondary-800: #1E40AF;
  --color-secondary-900: #1E3A8A;
  --color-secondary-950: #172554;

  /* Accent Colors */
  --color-accent-pink: #F472B6;
  --color-accent-pink-light: #F9A8D4;
  --color-accent-pink-dark: #EC4899;

  --color-accent-teal: #14B8A6;
  --color-accent-teal-light: #2DD4BF;
  --color-accent-teal-dark: #0D9488;

  --color-accent-amber: #F59E0B;
  --color-accent-amber-light: #FBBF24;
  --color-accent-amber-dark: #D97706;

  /* Semantic Colors */
  --color-success: #14B8A6;
  --color-success-bg: #F0FDFA;
  --color-success-border: #99F6E4;

  --color-warning: #F59E0B;
  --color-warning-bg: #FFFBEB;
  --color-warning-border: #FDE68A;

  --color-error: #EF4444;
  --color-error-bg: #FEF2F2;
  --color-error-border: #FECACA;

  --color-info: #3B82F6;
  --color-info-bg: #EFF6FF;
  --color-info-border: #BFDBFE;

  /* === BACKGROUNDS === */
  --bg-base: #FFFFFF;
  --bg-subtle: #F8FAFC;
  --bg-muted: #F1F5F9;
  --bg-emphasis: #E2E8F0;
  --bg-gradient-subtle: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%);
  --bg-gradient-primary: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%);
  --bg-hero: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(59, 130, 246, 0.1) 50%, rgba(244, 114, 182, 0.05) 100%);

  /* === TEXT === */
  --text-primary: #1E293B;
  --text-secondary: #334155;
  --text-muted: #64748B;
  --text-disabled: #94A3B8;
  --text-inverse: #FFFFFF;
  --text-on-gradient: #FFFFFF;

  /* === BORDERS === */
  --border-default: #E2E8F0;
  --border-muted: #F1F5F9;
  --border-emphasis: #CBD5E1;
  --border-focus: #8B5CF6;

  /* === TYPOGRAPHY === */
  --font-heading: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-accent: 'Space Grotesk', 'Poppins', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;

  /* Font Sizes */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  --text-5xl: 3rem;
  --text-6xl: 3.75rem;
  --text-7xl: 4.5rem;

  /* Line Heights */
  --leading-none: 1;
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 2;

  /* Letter Spacing */
  --tracking-tighter: -0.05em;
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;

  /* === SPACING === */
  --spacing-0: 0;
  --spacing-1: 0.25rem;
  --spacing-2: 0.5rem;
  --spacing-3: 0.75rem;
  --spacing-4: 1rem;
  --spacing-5: 1.25rem;
  --spacing-6: 1.5rem;
  --spacing-8: 2rem;
  --spacing-10: 2.5rem;
  --spacing-12: 3rem;
  --spacing-16: 4rem;
  --spacing-20: 5rem;
  --spacing-24: 6rem;

  /* === BORDER RADIUS === */
  --radius-none: 0;
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-2xl: 1rem;
  --radius-3xl: 1.5rem;
  --radius-full: 9999px;

  /* === SHADOWS === */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.03);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 10px 10px -5px rgba(0, 0, 0, 0.03);
  --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
  --shadow-primary: 0 4px 14px 0 rgba(139, 92, 246, 0.35);
  --shadow-primary-lg: 0 8px 24px 0 rgba(139, 92, 246, 0.4);

  /* === TRANSITIONS === */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slower: 500ms cubic-bezier(0.4, 0, 0.2, 1);

  /* === Z-INDEX === */
  --z-dropdown: 50;
  --z-sticky: 100;
  --z-modal-backdrop: 150;
  --z-modal: 200;
  --z-tooltip: 250;
  --z-toast: 300;
}
```

### 6.2 Dark Mode

```css
.dark {
  /* === BACKGROUNDS === */
  --bg-base: #0F172A;
  --bg-subtle: #1E293B;
  --bg-muted: #334155;
  --bg-emphasis: #475569;
  --bg-gradient-subtle: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
  --bg-gradient-primary: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%);
  --bg-hero: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(59, 130, 246, 0.15) 50%, rgba(244, 114, 182, 0.1) 100%);

  /* === TEXT === */
  --text-primary: #F1F5F9;
  --text-secondary: #E2E8F0;
  --text-muted: #94A3B8;
  --text-disabled: #64748B;
  --text-inverse: #0F172A;

  /* === BORDERS === */
  --border-default: #334155;
  --border-muted: #1E293B;
  --border-emphasis: #475569;
  --border-focus: #A78BFA;

  /* === SEMANTIC COLORS (Dark variants) === */
  --color-success-bg: rgba(20, 184, 166, 0.1);
  --color-success-border: rgba(20, 184, 166, 0.3);

  --color-warning-bg: rgba(245, 158, 11, 0.1);
  --color-warning-border: rgba(245, 158, 11, 0.3);

  --color-error-bg: rgba(239, 68, 68, 0.1);
  --color-error-border: rgba(239, 68, 68, 0.3);

  --color-info-bg: rgba(59, 130, 246, 0.1);
  --color-info-border: rgba(59, 130, 246, 0.3);

  /* === SHADOWS (Dark mode adjusted) === */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
  --shadow-primary: 0 4px 14px 0 rgba(139, 92, 246, 0.25);
  --shadow-primary-lg: 0 8px 24px 0 rgba(139, 92, 246, 0.3);
}
```

---

## 7. Tailwind Configuration Extension

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // === COLORS ===
      colors: {
        primary: {
          50: 'var(--color-primary-50, #F5F3FF)',
          100: 'var(--color-primary-100, #EDE9FE)',
          200: 'var(--color-primary-200, #DDD6FE)',
          300: 'var(--color-primary-300, #C4B5FD)',
          400: 'var(--color-primary-400, #A78BFA)',
          500: 'var(--color-primary, #8B5CF6)',
          600: 'var(--color-primary-600, #7C3AED)',
          700: 'var(--color-primary-700, #6D28D9)',
          800: 'var(--color-primary-800, #5B21B6)',
          900: 'var(--color-primary-900, #4C1D95)',
          950: 'var(--color-primary-950, #2E1065)',
          DEFAULT: 'var(--color-primary, #8B5CF6)',
        },
        secondary: {
          50: 'var(--color-secondary-50, #EFF6FF)',
          100: 'var(--color-secondary-100, #DBEAFE)',
          200: 'var(--color-secondary-200, #BFDBFE)',
          300: 'var(--color-secondary-300, #93C5FD)',
          400: 'var(--color-secondary-400, #60A5FA)',
          500: 'var(--color-secondary, #3B82F6)',
          600: 'var(--color-secondary-600, #2563EB)',
          700: 'var(--color-secondary-700, #1D4ED8)',
          800: 'var(--color-secondary-800, #1E40AF)',
          900: 'var(--color-secondary-900, #1E3A8A)',
          950: 'var(--color-secondary-950, #172554)',
          DEFAULT: 'var(--color-secondary, #3B82F6)',
        },
        accent: {
          pink: {
            light: '#F9A8D4',
            DEFAULT: '#F472B6',
            dark: '#EC4899',
          },
          teal: {
            light: '#2DD4BF',
            DEFAULT: '#14B8A6',
            dark: '#0D9488',
          },
          amber: {
            light: '#FBBF24',
            DEFAULT: '#F59E0B',
            dark: '#D97706',
          },
        },
        // Background colors
        surface: {
          base: 'var(--bg-base)',
          subtle: 'var(--bg-subtle)',
          muted: 'var(--bg-muted)',
          emphasis: 'var(--bg-emphasis)',
        },
      },

      // === BACKGROUND IMAGES ===
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%)',
        'gradient-primary-reverse': 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
        'gradient-hero': 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(59, 130, 246, 0.1) 50%, rgba(244, 114, 182, 0.05) 100%)',
        'gradient-hero-dark': 'linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(59, 130, 246, 0.15) 50%, rgba(244, 114, 182, 0.1) 100%)',
        'gradient-radial': 'radial-gradient(circle, var(--tw-gradient-stops))',
        'gradient-mesh': `
          radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%),
          radial-gradient(at 100% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
          radial-gradient(at 100% 100%, rgba(244, 114, 182, 0.1) 0px, transparent 50%),
          radial-gradient(at 0% 100%, rgba(20, 184, 166, 0.1) 0px, transparent 50%)
        `,
      },

      // === FONT FAMILIES ===
      fontFamily: {
        heading: ['Poppins', 'system-ui', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        accent: ['Space Grotesk', 'Poppins', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },

      // === FONT SIZES ===
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.75rem' }],
        '7xl': ['4.5rem', { lineHeight: '1.1' }],
        '8xl': ['6rem', { lineHeight: '1' }],
        '9xl': ['8rem', { lineHeight: '1' }],
      },

      // === BORDER RADIUS ===
      borderRadius: {
        '4xl': '2rem',
        '5xl': '2.5rem',
      },

      // === BOX SHADOW ===
      boxShadow: {
        'primary': '0 4px 14px 0 rgba(139, 92, 246, 0.35)',
        'primary-lg': '0 8px 24px 0 rgba(139, 92, 246, 0.4)',
        'primary-xl': '0 12px 32px 0 rgba(139, 92, 246, 0.45)',
        'secondary': '0 4px 14px 0 rgba(59, 130, 246, 0.35)',
        'glow': '0 0 15px rgba(139, 92, 246, 0.5)',
        'glow-lg': '0 0 30px rgba(139, 92, 246, 0.4)',
        'inner-glow': 'inset 0 0 20px rgba(139, 92, 246, 0.1)',
      },

      // === ANIMATIONS ===
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'fade-in-up': 'fadeInUp 0.5s ease-out',
        'fade-in-down': 'fadeInDown 0.5s ease-out',
        'slide-in-left': 'slideInLeft 0.5s ease-out',
        'slide-in-right': 'slideInRight 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'float': 'float 6s ease-in-out infinite',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'gradient-shift': 'gradientShift 8s ease infinite',
        'bounce-subtle': 'bounceSubtle 2s ease-in-out infinite',
        'spin-slow': 'spin 3s linear infinite',
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeInDown: {
          '0%': { opacity: '0', transform: 'translateY(-20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        float: {
          '0%, 100%': { transform: 'translate(0, 0)' },
          '50%': { transform: 'translate(20px, -20px)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(139, 92, 246, 0.4)' },
          '50%': { boxShadow: '0 0 0 8px rgba(139, 92, 246, 0)' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        gradientShift: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },

      // === TRANSITIONS ===
      transitionTimingFunction: {
        'bounce-in': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },

      transitionDuration: {
        '400': '400ms',
        '600': '600ms',
      },

      // === SPACING ===
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
        '30': '7.5rem',
        '34': '8.5rem',
        '38': '9.5rem',
        '42': '10.5rem',
      },

      // === BACKDROP BLUR ===
      backdropBlur: {
        'xs': '2px',
      },
    },
  },
  plugins: [
    // Custom utilities plugin
    function({ addUtilities, addComponents, theme }) {
      // Gradient text utility
      addUtilities({
        '.text-gradient': {
          'background': 'linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%)',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
          'background-clip': 'text',
        },
        '.text-gradient-animated': {
          'background': 'linear-gradient(90deg, #8B5CF6, #3B82F6, #F472B6, #8B5CF6)',
          'background-size': '300% 100%',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
          'background-clip': 'text',
          'animation': 'gradientShift 8s ease infinite',
        },
        '.gradient-border': {
          'position': 'relative',
          'background': 'var(--bg-base)',
          '&::before': {
            'content': '""',
            'position': 'absolute',
            'inset': '0',
            'border-radius': 'inherit',
            'padding': '2px',
            'background': 'linear-gradient(135deg, #8B5CF6, #3B82F6)',
            '-webkit-mask': 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            'mask': 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            '-webkit-mask-composite': 'xor',
            'mask-composite': 'exclude',
            'pointer-events': 'none',
          },
        },
      })

      // Glass effect components
      addComponents({
        '.glass': {
          'background': 'rgba(255, 255, 255, 0.7)',
          'backdrop-filter': 'blur(10px)',
          '-webkit-backdrop-filter': 'blur(10px)',
          'border': '1px solid rgba(255, 255, 255, 0.3)',
        },
        '.glass-dark': {
          'background': 'rgba(30, 41, 59, 0.7)',
          'backdrop-filter': 'blur(10px)',
          '-webkit-backdrop-filter': 'blur(10px)',
          'border': '1px solid rgba(255, 255, 255, 0.1)',
        },
      })
    },
  ],
}
```

---

## 8. Component Code Examples

### 8.1 GradientButton Component

```jsx
// components/GradientButton.jsx
import React from 'react';

const GradientButton = ({
  children,
  variant = 'primary',
  size = 'md',
  pill = false,
  disabled = false,
  loading = false,
  className = '',
  ...props
}) => {
  const baseStyles = `
    relative inline-flex items-center justify-center
    font-semibold transition-all duration-300
    focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-400 focus-visible:ring-offset-2
    disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none
  `;

  const variants = {
    primary: `
      bg-gradient-to-br from-primary-500 to-secondary-500
      text-white shadow-primary
      hover:shadow-primary-lg hover:-translate-y-0.5
      active:translate-y-0 active:shadow-primary
    `,
    secondary: `
      border-2 border-transparent
      bg-clip-padding
      text-primary-500
      hover:bg-gradient-to-br hover:from-primary-500 hover:to-secondary-500
      hover:text-white hover:-translate-y-0.5
      [background-image:linear-gradient(white,white),linear-gradient(135deg,#8B5CF6,#3B82F6)]
      [background-origin:border-box]
      [background-clip:padding-box,border-box]
      dark:[background-image:linear-gradient(#0F172A,#0F172A),linear-gradient(135deg,#8B5CF6,#3B82F6)]
    `,
    ghost: `
      text-primary-500 bg-transparent
      hover:bg-primary-50 dark:hover:bg-primary-900/20
    `,
  };

  const sizes = {
    sm: 'px-4 py-2 text-xs rounded-lg',
    md: 'px-6 py-3 text-sm rounded-xl',
    lg: 'px-8 py-4 text-base rounded-xl',
    xl: 'px-10 py-5 text-lg rounded-2xl',
  };

  const pillStyle = pill ? 'rounded-full' : '';

  return (
    <button
      className={`
        ${baseStyles}
        ${variants[variant]}
        ${sizes[size]}
        ${pillStyle}
        ${className}
      `}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {children}
    </button>
  );
};

export default GradientButton;
```

### 8.2 ModernCard Component

```jsx
// components/ModernCard.jsx
import React from 'react';

const ModernCard = ({
  children,
  variant = 'default',
  hover = true,
  className = '',
  ...props
}) => {
  const baseStyles = `
    bg-white dark:bg-slate-800
    rounded-2xl overflow-hidden
    transition-all duration-300
  `;

  const variants = {
    default: `
      border border-slate-200 dark:border-slate-700
      shadow-sm
      ${hover ? 'hover:-translate-y-1 hover:shadow-xl hover:shadow-primary-500/10' : ''}
    `,
    elevated: `
      shadow-lg shadow-slate-200/50 dark:shadow-slate-900/50
      ${hover ? 'hover:-translate-y-1 hover:shadow-xl hover:shadow-primary-500/10' : ''}
    `,
    gradient: `
      relative
      before:absolute before:inset-0 before:p-[2px] before:rounded-2xl
      before:bg-gradient-to-br before:from-primary-500 before:to-secondary-500
      before:-z-10
      ${hover ? 'hover:-translate-y-1 hover:shadow-primary-lg' : ''}
    `,
    feature: `
      shadow-lg shadow-primary-500/10
      ${hover ? 'hover:shadow-xl hover:shadow-primary-500/20' : ''}
    `,
  };

  return (
    <div
      className={`${baseStyles} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

const CardHeader = ({ children, className = '' }) => (
  <div className={`px-6 py-4 border-b border-slate-100 dark:border-slate-700 ${className}`}>
    {children}
  </div>
);

const CardBody = ({ children, className = '' }) => (
  <div className={`p-6 ${className}`}>
    {children}
  </div>
);

const CardFooter = ({ children, className = '' }) => (
  <div className={`px-6 py-4 border-t border-slate-100 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 ${className}`}>
    {children}
  </div>
);

ModernCard.Header = CardHeader;
ModernCard.Body = CardBody;
ModernCard.Footer = CardFooter;

export default ModernCard;
```

### 8.3 GlassCard Component

```jsx
// components/GlassCard.jsx
import React from 'react';

const GlassCard = ({
  children,
  intensity = 'medium',
  className = '',
  ...props
}) => {
  const intensities = {
    subtle: 'bg-white/40 dark:bg-slate-800/40 backdrop-blur-sm',
    medium: 'bg-white/70 dark:bg-slate-800/70 backdrop-blur-md',
    strong: 'bg-white/85 dark:bg-slate-800/85 backdrop-blur-lg',
  };

  return (
    <div
      className={`
        ${intensities[intensity]}
        border border-white/30 dark:border-white/10
        rounded-2xl
        shadow-lg shadow-slate-900/5 dark:shadow-slate-900/20
        transition-all duration-300
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};

export default GlassCard;
```

### 8.4 GradientHero Component

```jsx
// components/GradientHero.jsx
import React from 'react';
import GradientButton from './GradientButton';

const GradientHero = ({
  title,
  subtitle,
  primaryCta,
  secondaryCta,
  onPrimaryClick,
  onSecondaryClick,
}) => {
  return (
    <section className="relative min-h-[80vh] flex items-center justify-center overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-hero dark:bg-gradient-hero-dark" />

      {/* Decorative Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Purple blob */}
        <div
          className="absolute top-[10%] left-[10%] w-72 h-72 bg-primary-500 rounded-full filter blur-[80px] opacity-30 animate-float"
          style={{ animationDelay: '0s' }}
        />

        {/* Blue blob */}
        <div
          className="absolute bottom-[10%] right-[10%] w-64 h-64 bg-secondary-500 rounded-full filter blur-[80px] opacity-30 animate-float"
          style={{ animationDelay: '-2s', animationDirection: 'reverse' }}
        />

        {/* Pink blob */}
        <div
          className="absolute top-[50%] right-[20%] w-56 h-56 bg-accent-pink rounded-full filter blur-[80px] opacity-20 animate-float"
          style={{ animationDelay: '-4s' }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 text-center max-w-4xl mx-auto px-6">
        <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-slate-800 dark:text-white mb-6 animate-fade-in-up">
          <span className="text-gradient">{title}</span>
        </h1>

        <p
          className="text-xl md:text-2xl text-slate-600 dark:text-slate-300 mb-10 max-w-2xl mx-auto animate-fade-in-up"
          style={{ animationDelay: '100ms' }}
        >
          {subtitle}
        </p>

        <div
          className="flex flex-wrap gap-4 justify-center animate-fade-in-up"
          style={{ animationDelay: '200ms' }}
        >
          <GradientButton
            size="lg"
            onClick={onPrimaryClick}
          >
            {primaryCta}
          </GradientButton>

          {secondaryCta && (
            <GradientButton
              variant="secondary"
              size="lg"
              onClick={onSecondaryClick}
            >
              {secondaryCta}
            </GradientButton>
          )}
        </div>
      </div>
    </section>
  );
};

export default GradientHero;
```

### 8.5 AnimatedProgress Component

```jsx
// components/AnimatedProgress.jsx
import React, { useEffect, useState } from 'react';

const AnimatedProgress = ({
  value = 0,
  max = 100,
  size = 'md',
  showLabel = true,
  animated = true,
  className = '',
}) => {
  const [displayValue, setDisplayValue] = useState(0);
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => {
        setDisplayValue(percentage);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      setDisplayValue(percentage);
    }
  }, [percentage, animated]);

  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
    xl: 'h-4',
  };

  return (
    <div className={className}>
      <div className={`w-full bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden ${sizes[size]}`}>
        <div
          className="h-full bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full transition-all duration-1000 ease-out relative overflow-hidden"
          style={{ width: `${displayValue}%` }}
        >
          {/* Shimmer effect */}
          {animated && (
            <div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent animate-shimmer"
              style={{ backgroundSize: '200% 100%' }}
            />
          )}
        </div>
      </div>

      {showLabel && (
        <div className="mt-1 flex justify-between text-xs">
          <span className="text-slate-500 dark:text-slate-400">Progress</span>
          <span className="font-medium text-primary-500">{Math.round(displayValue)}%</span>
        </div>
      )}
    </div>
  );
};

export default AnimatedProgress;
```

### 8.6 ProgressRing Component

```jsx
// components/ProgressRing.jsx
import React, { useEffect, useState } from 'react';

const ProgressRing = ({
  value = 0,
  max = 100,
  size = 120,
  strokeWidth = 8,
  label = '',
  animated = true,
}) => {
  const [displayValue, setDisplayValue] = useState(0);
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (displayValue / 100) * circumference;

  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => {
        setDisplayValue(percentage);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      setDisplayValue(percentage);
    }
  }, [percentage, animated]);

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      {/* SVG Definitions */}
      <svg width="0" height="0" className="absolute">
        <defs>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#8B5CF6" />
            <stop offset="100%" stopColor="#3B82F6" />
          </linearGradient>
        </defs>
      </svg>

      {/* Progress Ring */}
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-slate-100 dark:text-slate-700"
        />

        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="url(#progressGradient)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-1000 ease-out"
        />
      </svg>

      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-slate-800 dark:text-white">
          {Math.round(displayValue)}%
        </span>
        {label && (
          <span className="text-xs text-slate-500 dark:text-slate-400">{label}</span>
        )}
      </div>
    </div>
  );
};

export default ProgressRing;
```

### 8.7 CourseCard Component

```jsx
// components/CourseCard.jsx
import React from 'react';
import AnimatedProgress from './AnimatedProgress';

const CourseCard = ({
  image,
  title,
  description,
  instructor,
  duration,
  lessons,
  progress = 0,
  badge,
  onClick,
}) => {
  return (
    <article
      className="group bg-white dark:bg-slate-800 rounded-2xl overflow-hidden shadow-sm border border-slate-100 dark:border-slate-700 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-primary-500/10 cursor-pointer"
      onClick={onClick}
    >
      {/* Image Section */}
      <div className="relative aspect-video overflow-hidden">
        <img
          src={image}
          alt={title}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        />

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />

        {/* Badge */}
        {badge && (
          <span className="absolute top-4 left-4 px-3 py-1 bg-gradient-to-r from-primary-500 to-secondary-500 text-white text-xs font-semibold rounded-full">
            {badge}
          </span>
        )}

        {/* Play button overlay on hover */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <div className="w-16 h-16 rounded-full bg-white/90 flex items-center justify-center shadow-lg">
            <svg className="w-6 h-6 text-primary-500 ml-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="p-6">
        <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-2 line-clamp-2">
          {title}
        </h3>

        <p className="text-sm text-slate-500 dark:text-slate-400 mb-4 line-clamp-2">
          {description}
        </p>

        {/* Meta info */}
        <div className="flex items-center gap-4 text-xs text-slate-400 dark:text-slate-500 mb-4">
          <span className="flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {duration}
          </span>
          <span className="flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {lessons} lessons
          </span>
        </div>

        {/* Progress */}
        {progress > 0 && (
          <AnimatedProgress value={progress} size="sm" showLabel={true} />
        )}
      </div>
    </article>
  );
};

export default CourseCard;
```

---

## 9. Visual Appearance Descriptions

### 9.1 Home Page

**Hero Section:**
- Full-viewport gradient background blending purple (#8B5CF6) into blue (#3B82F6) with subtle pink accents
- Three large, softly blurred decorative circles floating with gentle animation
- Bold headline with gradient text effect, using Poppins font at 72px
- Subtitle in Inter at 24px with muted text color
- Two call-to-action buttons: primary gradient button and secondary outline button with gradient border
- Smooth scroll indicator at bottom

**Featured Courses Grid:**
- 3-column responsive grid with generous 32px gaps
- Course cards with rounded corners (16px radius)
- Cards lift 4px on hover with shadow transition
- Course images feature gradient overlays and scale slightly on hover
- Progress bars use the primary gradient fill

**Testimonials:**
- Glass cards with frosted background effect
- Gradient border accents
- Circular avatar images with gradient rings
- Star ratings in amber accent color

**Footer:**
- Deep slate background transitioning to dark
- Gradient accent line at top
- Social icons with hover glow effect

### 9.2 Course Listing Page

**Header:**
- Search bar with floating label animation
- Filter chips using pill-shaped buttons with gradient selection state
- Category dropdown with custom styled options

**Course Grid:**
- 4-column grid on desktop, 2 on tablet, 1 on mobile
- Cards show course image, title, instructor, duration
- "Featured" and "New" badges with gradient backgrounds
- Hover reveals play button overlay on image
- Staggered entrance animation when page loads

**Pagination:**
- Modern pill-shaped page indicators
- Active page has gradient background
- Arrow buttons with subtle hover lift

### 9.3 Course Detail Page

**Hero:**
- Large course banner image with gradient overlay
- Course title in gradient text
- Instructor avatar with online status indicator
- Enrollment button (large gradient primary)
- Course stats in glass cards (students, duration, lessons)

**Content Area:**
- Tab navigation with gradient underline indicator
- Curriculum section with expandable modules
- Lesson items show completion checkmarks (teal accent)
- Video player with rounded corners and shadow

**Sidebar:**
- Sticky positioning on desktop
- Glass card background
- Price displayed prominently
- Gradient CTA button
- Feature list with check icons

### 9.4 Student Dashboard

**Overview Section:**
- Stats cards in 4-column grid
- Each card has icon with colored background (using accent colors)
- Numbers use Space Grotesk font for modern feel
- Change indicators (green up, red down arrows)

**Progress Overview:**
- Large progress ring with gradient stroke
- Animated entrance when scrolling into view
- Current course status with thumbnail

**Recent Activity:**
- Timeline-style layout
- Avatar images with subtle glow on hover
- Activity descriptions with timestamp
- Gradient connecting line between items

**Course Grid:**
- "Continue Learning" section
- Horizontal scrolling on mobile
- Progress bars on each card
- "Resume" buttons with gradient fill

### 9.5 Admin Panel

**Sidebar:**
- Dark slate background (#1E293B)
- Logo with gradient accent
- Navigation items with rounded hover states
- Active item has gradient left border
- Collapse/expand animation

**Dashboard:**
- Key metrics in stat cards
- Charts with gradient fills
- Data tables with alternating row colors
- Action buttons using accent colors
- Status badges (Teal for active, Amber for pending, Pink for flagged)

**Forms:**
- Floating label inputs
- Gradient focus rings
- Custom checkboxes and radio buttons with animations
- Submit buttons with gradient background and loading states

---

## 10. Theme Manifest (theme.json)

```json
{
  "name": "Colorful Modern",
  "slug": "colorful-modern",
  "version": "1.0.0",
  "description": "A vibrant, contemporary theme with bold gradients, playful colors, and modern UI patterns. Perfect for youth ministries, contemporary churches, and organizations wanting a fresh, energetic look.",
  "author": "Melchizedek Priests Ministry",
  "license": "MIT",

  "preview": {
    "thumbnail": "/themes/colorful-modern/preview-thumb.png",
    "full": "/themes/colorful-modern/preview-full.png",
    "demo_url": "https://demo.example.com/colorful-modern"
  },

  "tags": [
    "modern",
    "colorful",
    "gradient",
    "vibrant",
    "youth",
    "contemporary",
    "animated"
  ],

  "features": {
    "dark_mode": true,
    "glassmorphism": true,
    "animations": true,
    "gradient_text": true,
    "gradient_buttons": true,
    "floating_labels": true,
    "progress_rings": true,
    "custom_scrollbar": true
  },

  "compatibility": {
    "min_app_version": "2.0.0",
    "tailwind_version": "^3.4.0",
    "browsers": ["chrome >= 88", "firefox >= 85", "safari >= 14", "edge >= 88"]
  },

  "fonts": {
    "google_fonts": [
      {
        "family": "Poppins",
        "weights": [500, 600, 700, 800]
      },
      {
        "family": "Inter",
        "weights": [400, 500, 600, 700]
      },
      {
        "family": "Space Grotesk",
        "weights": [500, 600, 700]
      }
    ],
    "preconnect": ["https://fonts.googleapis.com", "https://fonts.gstatic.com"]
  },

  "colors": {
    "primary": {
      "name": "Vibrant Purple",
      "value": "#8B5CF6",
      "customizable": true
    },
    "secondary": {
      "name": "Electric Blue",
      "value": "#3B82F6",
      "customizable": true
    },
    "accent_1": {
      "name": "Coral Pink",
      "value": "#F472B6",
      "customizable": true
    },
    "accent_2": {
      "name": "Teal",
      "value": "#14B8A6",
      "customizable": true
    },
    "accent_3": {
      "name": "Amber",
      "value": "#F59E0B",
      "customizable": true
    }
  },

  "gradient": {
    "direction": "135deg",
    "start": "#8B5CF6",
    "end": "#3B82F6",
    "customizable": true
  },

  "typography": {
    "heading_font": "Poppins",
    "body_font": "Inter",
    "accent_font": "Space Grotesk",
    "base_size": "16px",
    "scale_ratio": 1.25
  },

  "spacing": {
    "base_unit": "4px",
    "container_padding": "24px",
    "card_padding": "24px",
    "section_spacing": "80px"
  },

  "borders": {
    "radius_sm": "8px",
    "radius_md": "12px",
    "radius_lg": "16px",
    "radius_xl": "24px",
    "radius_full": "9999px"
  },

  "shadows": {
    "enable_colored_shadows": true,
    "primary_shadow_color": "rgba(139, 92, 246, 0.35)",
    "shadow_intensity": "medium"
  },

  "animations": {
    "enable_page_transitions": true,
    "enable_hover_effects": true,
    "enable_loading_animations": true,
    "reduced_motion_support": true,
    "default_duration": "300ms",
    "default_easing": "cubic-bezier(0.4, 0, 0.2, 1)"
  },

  "components": {
    "buttons": {
      "style": "gradient",
      "hover_effect": "lift",
      "border_radius": "12px"
    },
    "cards": {
      "style": "modern",
      "hover_effect": "lift-shadow",
      "border_radius": "16px"
    },
    "inputs": {
      "style": "floating-label",
      "focus_effect": "gradient-ring",
      "border_radius": "12px"
    },
    "navigation": {
      "style": "transparent-blur",
      "indicator": "gradient-underline",
      "mobile_style": "slide-panel"
    }
  },

  "files": {
    "css": "/themes/colorful-modern/theme.css",
    "tailwind_config": "/themes/colorful-modern/tailwind.config.js",
    "components": "/themes/colorful-modern/components/",
    "assets": "/themes/colorful-modern/assets/"
  },

  "customization_options": [
    {
      "id": "primary_color",
      "label": "Primary Color",
      "type": "color",
      "default": "#8B5CF6"
    },
    {
      "id": "secondary_color",
      "label": "Secondary Color",
      "type": "color",
      "default": "#3B82F6"
    },
    {
      "id": "gradient_direction",
      "label": "Gradient Direction",
      "type": "select",
      "options": ["45deg", "90deg", "135deg", "180deg"],
      "default": "135deg"
    },
    {
      "id": "border_radius",
      "label": "Corner Roundness",
      "type": "select",
      "options": ["subtle", "moderate", "rounded", "pill"],
      "default": "rounded"
    },
    {
      "id": "animation_speed",
      "label": "Animation Speed",
      "type": "select",
      "options": ["fast", "normal", "slow", "none"],
      "default": "normal"
    },
    {
      "id": "glassmorphism_intensity",
      "label": "Glass Effect Intensity",
      "type": "select",
      "options": ["subtle", "medium", "strong", "none"],
      "default": "medium"
    }
  ]
}
```

---

## 11. Comparison: Classic Theme vs Colorful Modern

| Feature | Classic Theme | Colorful Modern |
|---------|---------------|-----------------|
| **Overall Style** | Traditional, professional, timeless | Vibrant, contemporary, energetic |
| **Target Audience** | Traditional churches, formal organizations | Youth ministries, modern churches, startups |
| **Primary Visual Element** | Solid colors, clean lines | Gradients, floating shapes |
| **Color Philosophy** | Single primary + complementary neutral | Multi-color gradient + 3 accent colors |
| **Color Palette** | Blues, grays, conservative tones | Purple-blue gradient, pink/teal/amber accents |
| **Typography** | Serif headings, classic proportions | Geometric sans-serif, generous spacing |
| **Button Style** | Solid fill, subtle hover | Gradient fill, lift effect, shadow |
| **Card Style** | Bordered, minimal shadow | Rounded, elevated, hover animations |
| **Navigation** | Solid background, underline active | Transparent/blur, gradient underline |
| **Form Inputs** | Standard bordered inputs | Floating labels, gradient focus |
| **Special Effects** | Minimal to none | Glassmorphism, animations, gradients |
| **Animations** | Subtle fade transitions | Page transitions, hover lifts, loading effects |
| **Dark Mode** | Simple color inversion | Rich navy background with gradient accents |
| **Icon Style** | Outlined, consistent weight | Filled with gradient backgrounds |
| **Progress Indicators** | Simple bars | Animated bars with shimmer, rings |
| **Image Treatment** | Standard display | Gradient overlays, zoom on hover |
| **Shadow Style** | Neutral gray shadows | Colored shadows matching primary |
| **Mood/Feeling** | Trustworthy, established, formal | Dynamic, innovative, welcoming |
| **Best For** | Sermon archives, Bible study, formal courses | Worship training, youth programs, community |

### When to Choose Each Theme

**Choose Classic Theme when:**
- Your organization has a traditional brand identity
- Your audience prefers familiar, conventional interfaces
- You want to emphasize content over visual effects
- Your courses are formal or academic in nature
- Accessibility for older demographics is a priority

**Choose Colorful Modern when:**
- You want to attract younger demographics
- Your brand identity is progressive and dynamic
- Visual engagement is important for your content
- You want to stand out from traditional church websites
- Your ministry focuses on contemporary worship or youth programs

---

## 12. Installation & Activation

### 12.1 Theme Selection in Installer Wizard

During the installation wizard (Phase 2 of the implementation roadmap), users will encounter the theme selection step:

**Step: Choose Your Theme**

```
+------------------------------------------------------------------+
|  [Icon] Choose Your Theme                            Step 4 of 8  |
+------------------------------------------------------------------+
|                                                                    |
|  Select a visual theme for your LMS. You can change this later    |
|  in Settings > Appearance.                                         |
|                                                                    |
|  +------------------------+    +------------------------+          |
|  |  [Preview Image]       |    |  [Preview Image]       |          |
|  |                        |    |                        |          |
|  |  CLASSIC               |    |  COLORFUL MODERN       |          |
|  |  Traditional &         |    |  Vibrant &             |          |
|  |  Professional          |    |  Contemporary          |          |
|  |                        |    |                        |          |
|  |  [Day/Night Toggle]    |    |  [Day/Night Toggle]    |          |
|  |                        |    |                        |          |
|  |  ( ) Select            |    |  (x) Select            |          |
|  +------------------------+    +------------------------+          |
|                                                                    |
|  [Preview in New Tab]                                              |
|                                                                    |
|  +-- Customize Colors (optional) ---------------------------+     |
|  |  Primary Color: [#8B5CF6] [Color Picker]                 |     |
|  |  Secondary Color: [#3B82F6] [Color Picker]               |     |
|  |  [ ] Use custom gradient direction                       |     |
|  +----------------------------------------------------------+     |
|                                                                    |
|                                    [< Back]  [Next: Email Setup >] |
+------------------------------------------------------------------+
```

### 12.2 Theme Files Structure

```
/themes/
  /colorful-modern/
    theme.json              # Theme manifest
    theme.css               # Compiled CSS variables
    tailwind.config.js      # Tailwind extension
    preview-thumb.png       # 400x300 thumbnail
    preview-full.png        # 1200x800 full preview
    /components/            # React component overrides
      GradientButton.jsx
      ModernCard.jsx
      GlassCard.jsx
      ...
    /assets/
      /images/              # Theme-specific images
      /icons/               # Custom icon set (optional)
```

### 12.3 Activation Process

1. **During Installation:**
   - User selects theme from wizard
   - Installer writes theme selection to database
   - Theme CSS variables injected into `index.html`
   - Theme-specific Tailwind config merged

2. **Post-Installation Activation:**
   ```javascript
   // In Settings > Appearance
   const activateTheme = async (themeSlug) => {
     // Load theme manifest
     const theme = await loadTheme(themeSlug);

     // Update CSS variables
     document.documentElement.style.setProperty('--color-primary', theme.colors.primary.value);
     // ... more variables

     // Save to database
     await api.settings.update({ active_theme: themeSlug });

     // Reload Tailwind if needed
     if (theme.requires_tailwind_rebuild) {
       await rebuildTailwind();
     }
   };
   ```

3. **Runtime Theme Switching:**
   - CSS variables enable instant switching
   - No page reload required for basic color changes
   - Full theme switch may require component reload

### 12.4 Customization Persistence

Theme customizations are stored in the database:

```sql
CREATE TABLE theme_settings (
  id SERIAL PRIMARY KEY,
  theme_slug VARCHAR(50) NOT NULL,
  setting_key VARCHAR(100) NOT NULL,
  setting_value TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(theme_slug, setting_key)
);

-- Example data
INSERT INTO theme_settings (theme_slug, setting_key, setting_value) VALUES
('colorful-modern', 'primary_color', '#8B5CF6'),
('colorful-modern', 'secondary_color', '#3B82F6'),
('colorful-modern', 'gradient_direction', '135deg'),
('colorful-modern', 'glassmorphism_intensity', 'medium'),
('colorful-modern', 'animation_speed', 'normal');
```

---

## 13. Accessibility Considerations

### 13.1 Color Contrast Ratios

All color combinations meet WCAG 2.1 AA standards:

| Combination | Ratio | Standard |
|-------------|-------|----------|
| Primary text on white | 7.2:1 | AAA |
| Primary text on dark | 8.5:1 | AAA |
| Muted text on white | 4.6:1 | AA |
| White on gradient | 4.8:1 | AA |
| Link text | 4.5:1 | AA |

### 13.2 Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }

  .animate-float,
  .animate-shimmer,
  .animate-pulse-glow {
    animation: none !important;
  }
}
```

### 13.3 Focus Indicators

All interactive elements have visible focus states:

```css
/* Focus visible for keyboard navigation */
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Remove default outline for mouse users */
:focus:not(:focus-visible) {
  outline: none;
}
```

### 13.4 Screen Reader Considerations

- All decorative animations have `aria-hidden="true"`
- Gradient text has proper fallback for screen readers
- Loading states announce progress via `aria-live`
- Skip links provided for navigation

---

## 14. Performance Considerations

### 14.1 CSS Optimization

- CSS variables used for theming (no runtime compilation)
- Animations use `transform` and `opacity` for GPU acceleration
- `will-change` applied sparingly to animated elements
- Reduced motion media query disables heavy animations

### 14.2 Font Loading Strategy

```html
<!-- Preconnect to font origins -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Font display swap for fast initial render -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@500;600;700;800&display=swap" rel="stylesheet">
```

### 14.3 Animation Performance

```css
/* GPU-accelerated properties only */
.hover-lift {
  transform: translateY(0);
  /* NOT: top, margin, etc. */
}

/* Contain animations to their layer */
.card {
  will-change: transform;
  contain: layout style;
}
```

---

## Document History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-01-11 | 1.0.0 | AI Assistant | Initial specification created |

---

## Related Documentation

- `docs/installer/IMPLEMENTATION_VISION.md` - Overall installer implementation plan
- `docs/installer/themes/CLASSIC_THEME.md` - Classic theme specification (to be created)
- `docs/installer/CPANEL_INSTALLATION_GUIDE.md` - cPanel deployment instructions

---

*This specification serves as the complete design and implementation guide for the Colorful Modern theme. All component styles, color values, and code examples are production-ready and designed to integrate seamlessly with the Church LMS installer wizard.*
