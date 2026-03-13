---
name: accessibility-essentials
category: ui-ux-pro-max
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [accessibility, a11y, aria, wcag, screen-reader, keyboard]
difficulty: medium
---

# Accessibility Essentials

## Problem

Accessibility is often treated as an afterthought, resulting in inaccessible apps that exclude users and violate WCAG guidelines. Retrofitting a11y is 10x harder than building it in from the start.

## Solution Pattern

Follow these 5 rules and you cover 80% of accessibility issues.

## The 5 Rules

### Rule 1: Semantic HTML First

```html
<!-- BAD: div soup -->
<div class="btn" onclick="submit()">Submit</div>

<!-- GOOD: native elements -->
<button type="submit">Submit</button>
```

Native elements give you keyboard support, focus management, and screen reader announcements for free. Use `<button>`, `<a>`, `<input>`, `<select>`, `<nav>`, `<main>`, `<header>`, `<footer>`.

### Rule 2: Every Image Has Alt Text

```html
<!-- Informative image -->
<img src="chart.png" alt="Revenue grew 40% in Q3 2025" />

<!-- Decorative image -->
<img src="divider.png" alt="" role="presentation" />
```

- **Informative:** Describe what the image conveys, not what it looks like
- **Decorative:** Empty `alt=""` so screen readers skip it

### Rule 3: Keyboard Navigation Works

```javascript
// Every interactive element must be reachable with Tab
// Every action must be triggerable with Enter or Space

// Test: unplug your mouse and use the app for 5 minutes
```

Common fixes:
- Add `tabindex="0"` to custom interactive elements
- Add `onKeyDown` handlers for Enter/Space on non-button elements
- Never remove `outline` without providing a visible focus indicator

```css
/* BAD */
*:focus { outline: none; }

/* GOOD */
*:focus-visible {
  outline: 2px solid #1971c2;
  outline-offset: 2px;
}
```

### Rule 4: Color Is Not the Only Indicator

```html
<!-- BAD: only color indicates error -->
<input style="border-color: red" />

<!-- GOOD: color + icon + text -->
<input style="border-color: red" aria-invalid="true" aria-describedby="error-msg" />
<span id="error-msg" role="alert">Email is required</span>
```

### Rule 5: ARIA Is a Last Resort

```html
<!-- If you can use native HTML, do that instead -->
<!-- ARIA is for when you MUST build a custom widget -->

<!-- Custom combobox (when <select> won't work) -->
<div role="combobox" aria-expanded="false" aria-haspopup="listbox">
  ...
</div>
```

**First rule of ARIA:** Don't use ARIA. Use semantic HTML.
**Second rule of ARIA:** If you must, follow the WAI-ARIA Authoring Practices exactly.

## Quick Audit Checklist

- [ ] Page has exactly one `<h1>`
- [ ] Heading levels don't skip (no h1 → h3)
- [ ] All form inputs have associated `<label>` elements
- [ ] Color contrast ratio is at least 4.5:1 (text) / 3:1 (large text)
- [ ] Skip-to-content link exists
- [ ] Tab order follows visual reading order

## When to Use

- Every web project, from the start
- Code reviews — check for a11y before approving

## When NOT to Use

- Not applicable — always apply these 5 rules
