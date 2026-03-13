---
name: safari-sw-cache-poisoning
category: frontend
version: 1.0.0
contributed: 2026-02-26
contributor: my-other-project
last_updated: 2026-02-26
tags: [safari, service-worker, pwa, caching, ios, debugging]
difficulty: hard
---

# Safari Service Worker Cache Poisoning

## Problem

Safari caches service worker files according to HTTP caching headers (e.g., `ExpiresByType application/javascript "access plus 1 year"`). When a stale SW is cached for months/years, it continues intercepting ALL requests (API calls, navigation, static assets) even after the server-side SW file is updated.

**Symptoms:**
- "Network Error" on ALL API calls in Safari (axios reports no response)
- Site loads HTML/CSS but can't communicate with server
- Chrome works fine (separate SW registration)
- Login, CMS data loading, and all authenticated features broken
- Safari DevTools shows SW intercepting requests

**Root Cause Chain:**
1. Apache `ExpiresByType application/javascript` applies to `sw.js` too
2. Safari respects the 1-year cache and never checks for SW updates
3. Old SW's `fetch` handler intercepts API calls and either fails or returns stale data
4. No amount of server-side fixes help because the browser never fetches the updated SW

## Solution Pattern

### 1. Prevent Future Cache Poisoning (.htaccess)

Add a specific no-cache rule for `sw.js` BEFORE the general JS caching rule:

```apache
# Prevent caching of service worker (must always fetch fresh)
<FilesMatch "sw\.js$">
    Header set Cache-Control "no-cache, no-store, must-revalidate"
    Header set Pragma "no-cache"
    Header set Expires 0
</FilesMatch>

# General JS caching (sw.js excluded by rule above)
<IfModule mod_expires.c>
  ExpiresByType application/javascript "access plus 1 year"
</IfModule>
```

### 2. Nuclear SW Purge (main entry point)

Add to your app's entry point (e.g., `main.jsx`). This runs on every page load, unregisters ALL stale SWs, purges ALL caches, then registers fresh:

```javascript
// Nuclear SW cleanup — force-purge stale SWs + caches, then register fresh.
// Safari cached old sw.js for 1 year, causing stale SW to intercept API calls.
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      // Step 1: Unregister ALL existing service workers
      const regs = await navigator.serviceWorker.getRegistrations();
      await Promise.all(regs.map(reg => reg.unregister()));

      // Step 2: Purge all SW caches
      const cacheNames = await caches.keys();
      await Promise.all(cacheNames.map(name => caches.delete(name)));

      // Step 3: Register fresh SW (production only)
      if (import.meta.env.PROD) {
        navigator.serviceWorker.register('/sw.js', {
          updateViaCache: 'none'  // Bypass HTTP cache for SW fetch
        }).catch(() => {});
      }
    } catch (e) {
      // SW API failures are non-fatal — site works fine without SW
    }
  });
}
```

### 3. Use `updateViaCache: 'none'`

Always register SWs with `updateViaCache: 'none'` to tell the browser to bypass HTTP cache when checking for SW updates:

```javascript
navigator.serviceWorker.register('/sw.js', { updateViaCache: 'none' });
```

## Key Insight: Safari Private Mode

Safari Private Browsing **completely disables service workers**. If the site works in regular Safari but breaks in Private Mode (or vice versa), the SW is likely NOT the issue. Check:
- CSP headers
- `theme-color` meta tag
- Content blockers / ad blockers (Safari-only on iOS)
- Cookie handling differences

## When to Use

- Site works in Chrome but breaks in Safari with "Network Error"
- API calls fail but HTML/CSS loads fine
- SW was registered before proper cache headers were set
- Deploying to shared hosting where Apache serves SW files
- Any PWA where `ExpiresByType` or `Cache-Control` applies to JS broadly

## When NOT to Use

- If the issue reproduces in Chrome too (not SW-specific)
- If Safari Private Mode also fails (SWs are disabled there — look elsewhere)
- If the server itself is down (check `/api/health` first)
- For sites that don't use service workers

## Debugging Checklist

1. `curl -s https://yoursite.com/api/health` — Server alive?
2. `curl -s -I https://yoursite.com/sw.js` — Check Cache-Control headers
3. `curl -v -X OPTIONS -H "Origin: https://yoursite.com" https://yoursite.com/api/endpoint` — CORS preflight works?
4. Check if Safari has website data stored (Settings > Safari > Advanced > Website Data)
5. Test in Safari Private Mode — if it works there, SW is the culprit

## Common Mistakes

- Assuming `sw.js` is exempt from `ExpiresByType` rules (it's not)
- Using `Header set` instead of `Header always set` in .htaccess
- Forgetting that unregistering a SW doesn't stop it controlling the CURRENT page (only takes effect on next navigation)
- Not wrapping SW API calls in try-catch (throws SecurityError in Private Mode)
- Using `caches` API without checking it exists (throws in some contexts)

## Related Skills

- CSP header synchronization (keep .htaccess and Helmet in sync)
- Safari theme-color meta tag (affects browser chrome appearance)

## References

- MDN: Service Worker Lifecycle — https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers
- MDN: updateViaCache — https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerRegistration/updateViaCache
- Contributed from: my-other-project Safari debugging session (Feb 26, 2026)
