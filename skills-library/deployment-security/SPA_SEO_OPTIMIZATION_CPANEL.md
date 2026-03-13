# React SPA SEO Optimization on cPanel Shared Hosting

## The Problem

Client-side React SPAs render zero content for search engine crawlers. Google sees:
- Title: "Loading..." or generic title
- Content: 0 words, 0 headings, 0 links
- No structured data, no OG tags, no sitemap

This results in Grade F (40-50/100) on SEO audits.

### Why It Was Hard

- SPA architecture fundamentally conflicts with SEO — content is JavaScript-rendered
- cPanel shared hosting with nginx reverse proxy adds complexity for security headers
- `.htaccess` rules must coexist with WebSocket proxy, API proxy, and PHP handler rules
- `cp -rf dist/*` during deployment silently skips dotfiles (`.htaccess`)
- No SSR/pre-rendering infrastructure available on shared hosting

### Impact

- Zero Google visibility — site effectively invisible to search engines
- No rich results (missing structured data)
- No social sharing previews (missing OG tags)
- Security headers only on API routes (Express/Helmet), not on static files

---

## The Solution

### Strategy: Quick Wins Without SSR

Instead of adding SSR infrastructure, use these techniques to go from Grade F → Grade C:

1. **Static SEO in `index.html`** — title, description, canonical, OG tags, JSON-LD
2. **`<noscript>` fallback** — crawlable HTML with nav, content sections, footer
3. **Visible SEO footer** — privacy/legal links outside `<noscript>` (hidden by React on mount)
4. **Static `sitemap.xml`** — list all public routes for crawler discovery
5. **`.htaccess` security headers** — CSP, HSTS, X-Frame-Options for Apache-served files
6. **CSP `<meta http-equiv>` fallback** — browsers honor CSP via meta tag
7. **Vite code splitting** — `manualChunks` to reduce main bundle size

### Implementation

#### 1. index.html — Complete SEO Head

```html
<head>
  <title>Site Name - Description (under 60 chars)</title>
  <meta name="description" content="Under 160 chars..." />
  <link rel="canonical" href="https://yoursite.com/" />

  <!-- Robot Control -->
  <meta name="robots" content="index, follow, noarchive, nocache, noimageindex" />

  <!-- CSP meta fallback (for static hosting without HTTP header control) -->
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; ..." />

  <!-- Open Graph -->
  <meta property="og:type" content="website" />
  <meta property="og:title" content="..." />
  <meta property="og:image" content="https://yoursite.com/og-image.jpg" />

  <!-- JSON-LD Structured Data -->
  <script type="application/ld+json">
  { "@context": "https://schema.org", "@type": "EducationalOrganization", ... }
  </script>
</head>
```

#### 2. Noscript Fallback + SEO Footer

```html
<body>
  <div id="root"></div>

  <!-- Visible to crawlers, removed by React on mount -->
  <footer id="seo-footer" class="text-xs text-gray-500 text-center p-4">
    <a href="/privacy">Privacy Policy</a> |
    <a href="/terms">Terms of Service</a>
  </footer>

  <noscript>
    <header><h1>Site Title</h1></header>
    <nav><ul><!-- all public page links --></ul></nav>
    <main><!-- content sections --></main>
    <footer><!-- legal links --></footer>
  </noscript>
</body>
```

In main.jsx, remove the SEO footer when React loads:
```javascript
const seoFooter = document.getElementById('seo-footer');
if (seoFooter) seoFooter.remove();
```

#### 3. .htaccess — Merged Configuration

**CRITICAL:** On cPanel, `.htaccess` likely already has WebSocket proxy, API proxy, and PHP handler rules. **Never overwrite** — always merge.

```apache
# Security Headers (add BEFORE existing rules)
<IfModule mod_headers.c>
  Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
  Header always set X-Frame-Options "SAMEORIGIN"
  Header always set X-Content-Type-Options "nosniff"
  Header always set Content-Security-Policy "default-src 'self'; ..."
</IfModule>

# KEEP EXISTING: WebSocket proxy, API proxy, SPA routing, PHP handler
```

#### 4. Deploy Script Fix

Bash `cp -rf dist/*` skips dotfiles. Add explicit copy:

```bash
cp -rf client/dist/* ~/public_html/
cp -f client/dist/.htaccess ~/public_html/.htaccess 2>/dev/null || true
```

#### 5. Vite Code Splitting

```javascript
// vite.config.js
rollupOptions: {
  output: {
    manualChunks: {
      'vendor-react': ['react', 'react-dom', 'react-router-dom'],
      'vendor-redux': ['@reduxjs/toolkit', 'react-redux'],
      'vendor-ui': ['@headlessui/react', 'lucide-react'],
    }
  }
}
```

---

## Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Overall Score | 47 (F) | 73 (C) | +26 |
| Security | 64 | 97 | +33 |
| Legal Compliance | -- | 100 | +100 |
| Structured Data | 0 | 100 | +100 |
| Social Media | 0 | 100 | +100 |
| Content | 0 | 75 | +75 |
| Crawlability | 50 | 95 | +45 |
| Core SEO | 43 | 81 | +38 |

---

## Common Mistakes to Avoid

- ❌ **Overwriting production `.htaccess`** — always SSH and check existing rules first
- ❌ **Using `/privacy-policy` when React route is `/privacy`** — verify actual route names
- ❌ **Relying on `.htaccess` alone for security** — nginx may bypass Apache; add CSP meta tag as fallback
- ❌ **Forgetting dotfile copy in deploy scripts** — `cp dist/*` skips `.htaccess`
- ❌ **Adding `noimageindex` without understanding impact** — blocks ALL image indexing, OG images still work for social sharing
- ❌ **Setting `nofollow` in robots meta** — blocks Google from following ANY links on the page

## Content Protection Without Hurting SEO

- `noarchive` — prevents cached copies (Google Cache)
- `nocache` — prevents snippet caching
- `noimageindex` — blocks image search indexing (OG images still work)
- robots.txt AI bot blocks (GPTBot, ClaudeBot, etc.) — prevents AI training
- `nofollow` in robots meta is **NOT** for content protection — it kills SEO

---

## Tools

- **squirrelscan CLI** — `squirrel audit <url> --format llm --coverage surface`
- Install: https://squirrelscan.com/download
- Use `--refresh` flag to bypass cache after changes

## Remaining Limitations (Require SSR)

- Duplicate titles across all pages (SPA serves same index.html)
- Thin content (noscript provides ~130 words, not full page content)
- No per-page meta descriptions
- To reach Grade A (90+), need SSR (Next.js) or pre-rendering

---

## Time to Implement

**1-2 hours** for all quick wins (no SSR)

## Difficulty Level

⭐⭐⭐ (3/5) — Conceptually simple but many gotchas with cPanel/nginx/.htaccess

---

**Author Notes:**
The biggest insight was that cPanel shared hosting uses nginx as a reverse proxy in front of Apache. The `.htaccess` IS processed (Apache handles it), but you have to actually get the file deployed. The `cp dist/*` glob silently skipping dotfiles cost us an entire debug cycle. Also, always SSH and check the existing `.htaccess` before deploying — it likely has critical proxy rules you don't want to overwrite.
