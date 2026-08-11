---
name: responsive-layout-patterns
category: ui-ux-pro-max
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [responsive, css, layout, grid, flexbox, mobile-first, breakpoints]
difficulty: medium
---

# Responsive Layout Patterns

## Problem

Building layouts that work across mobile, tablet, and desktop without duplicating components or writing fragile media queries. Most responsive bugs come from desktop-first thinking.

## Solution Pattern

Mobile-first CSS with a consistent breakpoint system and layout primitives.

## Breakpoint System

```css
/* Mobile-first: base styles ARE mobile */
/* sm: 640px  — large phones / small tablets */
/* md: 768px  — tablets */
/* lg: 1024px — small desktops */
/* xl: 1280px — large desktops */

/* Tailwind uses these by default */
```

**Rule: Never write `max-width` media queries.** Always build up from mobile with `min-width`.

## Layout Primitives

### 1. Stack (vertical flow)

```css
.stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
```

### 2. Cluster (horizontal wrap)

```css
.cluster {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}
```

### 3. Sidebar Layout

```css
.with-sidebar {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.with-sidebar > :first-child {
  flex-basis: 250px;
  flex-grow: 1;
}
.with-sidebar > :last-child {
  flex-basis: 0;
  flex-grow: 999;
  min-inline-size: 60%;
}
```

### 4. Auto Grid (responsive without media queries)

```css
.auto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(250px, 100%), 1fr));
  gap: 1rem;
}
```

This is the most powerful pattern — cards automatically reflow from 1 column on mobile to 3-4 on desktop with zero media queries.

### 5. Container Queries (2025+)

```css
.card-container {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .card { flex-direction: row; }
}
```

Container queries let components respond to their container, not the viewport. Better for reusable components.

## Common Mistakes

- **Fixed widths** — Use `max-width` with percentage fallbacks, never `width: 960px`
- **Overflow hiding** — `overflow: hidden` masks layout bugs. Fix the root cause.
- **Viewport units for text** — `font-size: 5vw` is unreadable on extremes. Use `clamp()`.
- **Forgetting touch targets** — Minimum 44x44px for interactive elements on mobile.

## When to Use

- Any project with a web frontend
- Starting a new layout system
- Debugging responsive issues

## When NOT to Use

- Electron/native apps with fixed viewports
- Print stylesheets (different paradigm)
