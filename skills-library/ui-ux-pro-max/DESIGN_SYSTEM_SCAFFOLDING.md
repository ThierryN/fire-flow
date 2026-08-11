---
name: design-system-scaffolding
category: ui-ux-pro-max
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [design-system, tokens, components, theming, tailwind, css-variables]
difficulty: medium
---

# Design System Scaffolding

## Problem

Projects start with ad-hoc colors, spacing, and typography. By week 3, there are 47 different blues and 12 font sizes. A minimal design system prevents this drift.

## Solution Pattern

Start with design tokens (CSS variables), a type scale, and a spacing scale. Add components as needed.

## Step 1: Design Tokens

```css
:root {
  /* Colors — semantic names, not visual */
  --color-primary: #1971c2;
  --color-primary-light: #e7f5ff;
  --color-secondary: #099268;
  --color-danger: #e03131;
  --color-warning: #f08c00;
  --color-text: #1e1e1e;
  --color-text-muted: #868e96;
  --color-surface: #ffffff;
  --color-border: #dee2e6;

  /* Spacing — 4px base unit */
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  --space-12: 3rem;    /* 48px */

  /* Typography */
  --font-sans: system-ui, -apple-system, sans-serif;
  --font-mono: 'Fira Code', monospace;
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;

  /* Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
}
```

## Step 2: Dark Mode (Free with Tokens)

```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-text: #e9ecef;
    --color-text-muted: #adb5bd;
    --color-surface: #1a1b1e;
    --color-border: #373a40;
  }
}

/* OR manual toggle */
[data-theme="dark"] {
  --color-text: #e9ecef;
  --color-surface: #1a1b1e;
}
```

## Step 3: Component Patterns

```jsx
// Button — uses tokens, supports variants
function Button({ variant = 'primary', size = 'md', children, ...props }) {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      {...props}
    >
      {children}
    </button>
  )
}
```

```css
.btn {
  font-family: var(--font-sans);
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-primary { background: var(--color-primary); color: white; }
.btn-sm { padding: var(--space-1) var(--space-3); font-size: var(--text-sm); }
.btn-md { padding: var(--space-2) var(--space-4); font-size: var(--text-base); }
```

## Rules

1. **Never use raw color values in components** — always reference tokens
2. **Spacing uses the scale** — no `margin: 13px`
3. **Typography uses the scale** — no `font-size: 0.9375rem`
4. **New tokens require justification** — why isn't an existing one sufficient?

## When to Use

- Starting any project with a UI
- When you notice color/spacing inconsistencies growing
- When adding dark mode support

## When NOT to Use

- Projects using an established design system (Material UI, shadcn/ui)
- Backend-only projects
