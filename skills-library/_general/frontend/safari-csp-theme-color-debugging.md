---
name: safari-csp-theme-color-debugging
category: frontend
version: 1.0.0
contributed: 2026-02-26
contributor: my-other-project
last_updated: 2026-02-26
tags: [safari, csp, theme-color, ios, mobile, debugging, helmet]
difficulty: medium
---

# Safari CSP & Theme-Color Debugging

## Problem

Safari on iOS renders differently from Chrome on iOS due to:
1. **Dual CSP headers** — Apache .htaccess and Node.js Helmet can get out of sync
2. **theme-color meta tag** — Safari paints the status bar and browser chrome with this color, creating visible colored bars above/below the page content
3. **CSP enforcement differences** — Safari can be stricter about CSP violations than Chrome

**Symptoms:**
- Purple/colored bars at top and bottom of the page in Safari
- Content blocked in Safari but not Chrome (CSP mismatch)
- `@headlessui/react` Transition leaving elements at `opacity-0` (Safari animation bug)
- Site showing fallback content instead of dynamic CMS content

## Solution Pattern

### 1. Keep CSP in Sync (Apache + Helmet)

When using both Apache .htaccess CSP AND Node.js Helmet CSP, they MUST match. Check which CSP applies to which responses:

```
HTML pages (SPA routes):     Apache .htaccess CSP
API responses (proxied):     Helmet CSP (Node.js)
Static files (JS/CSS/imgs):  Apache .htaccess CSP
```

Verify with curl:
```bash
# Check HTML page CSP
curl -s -I https://yoursite.com/ | grep -i content-security

# Check API response CSP
curl -s -I https://yoursite.com/api/health | grep -i content-security
```

### 2. Fix theme-color for Dark Themes

The `<meta name="theme-color">` controls Safari's status bar and browser chrome color. It must match your active theme:

```html
<!-- Before: Purple for old theme -->
<meta name="theme-color" content="#7C3AED" />

<!-- After: Dark for Aurora Borealis theme -->
<meta name="theme-color" content="#030712" />
```

For dynamic themes, update via React Helmet:
```jsx
<Helmet>
  <meta name="theme-color" content={theme.backgroundColor} />
</Helmet>
```

### 3. Safari Animation Fix

`@headlessui/react` `<Transition appear={true}>` can fail silently on Safari, leaving elements stuck at `opacity-0`. Replace with CSS keyframe animations:

```css
/* In overrides.css */
@keyframes heroFadeUp {
    from { opacity: 0; transform: translateY(2rem); }
    to { opacity: 1; transform: translateY(0); }
}
```

```jsx
{/* Before: Transition that fails on Safari */}
<Transition appear={true} show={true} enter="..." enterFrom="opacity-0" enterTo="opacity-100">
  <h1>Content</h1>
</Transition>

{/* After: CSS animation that works everywhere */}
<h1 style={{ animation: 'heroFadeUp 1s ease-out both' }}>Content</h1>
```

## Debugging Workflow

1. **Verify API is alive:** `curl -s https://yoursite.com/api/health`
2. **Compare CSP headers:** Check both Apache and Helmet CSPs match
3. **Test CORS preflight:** `curl -v -X OPTIONS -H "Origin: https://yoursite.com" https://yoursite.com/api/endpoint`
4. **Check theme-color:** View source or `curl -s https://yoursite.com/ | grep theme-color`
5. **Test Safari Private Mode:** If Private Mode fails but regular doesn't, check SW. If both fail, check CSP/CORS.
6. **Check for content blockers:** Safari supports iOS content blockers that Chrome doesn't

## When to Use

- Site looks different in Safari vs Chrome on iOS
- Colored bars appearing in Safari browser chrome
- Content blocked or missing in Safari
- Animations not playing in Safari
- Dual Apache + Node.js server setup

## When NOT to Use

- Issue reproduces identically in both browsers
- Desktop-only rendering issues
- Server-side errors (check logs first)

## Common Mistakes

- Updating .htaccess CSP but forgetting Helmet CSP (or vice versa)
- Setting theme-color to old brand color after theme change
- Using `@headlessui/react` Transition for critical above-fold content
- Not testing in Safari Private Mode (different behavior than regular)
- Assuming Chrome on iOS = Safari on iOS (they share WebKit but have different extensions, storage, and privacy features)

## References

- MDN: theme-color — https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta/name/theme-color
- MDN: CSP — https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
- Contributed from: my-other-project Safari debugging session (Feb 26, 2026)
