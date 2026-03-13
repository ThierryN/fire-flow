# Open Graph Image Generator
## Description

Generate dynamic Open Graph (OG) images programmatically for social media previews. Covers two production approaches: Satori + @vercel/og for edge deployment, and Sharp + Canvas for any Node.js server. Includes social card templates, caching strategies, meta tags, and testing workflows.

## When to Use

- Building a blog, course platform, or content site that needs unique social preview images per page
- Generating branded cards with dynamic text (title, author, date) for link sharing
- Creating consistent OG images across hundreds or thousands of pages without manual design
- Need to control how your links appear on Twitter/X, Facebook, LinkedIn, Discord, Slack

---

## Approach A: Satori + @vercel/og (Edge / Vercel)

### How It Works

Satori converts JSX (HTML/CSS subset) to SVG entirely in JavaScript/WebAssembly. The `@vercel/og` package wraps Satori with PNG rendering via Resvg-WASM. The entire pipeline runs on the edge with no server, no headless browser, no native dependencies.

**Pipeline:** JSX template --> Satori (SVG) --> Resvg-WASM (PNG) --> Response

### Installation

```bash
npm install @vercel/og
# Satori is included as a dependency
```

### Limitations

Satori supports a **subset** of CSS. Know these constraints before designing:

- Only `display: flex` (no `grid`, no `block`, no `inline`)
- No `position: absolute` or `position: fixed`
- No CSS animations or transitions
- No `box-shadow` (use border or SVG filters)
- No pseudo-elements (`::before`, `::after`)
- Fonts must be loaded explicitly (no system fonts on edge)
- Background images work via `backgroundImage: url(...)` but must be absolute URLs

### Custom Font Loading

```javascript
// Fetch font file at build time or on first request
async function loadFont() {
  const fontData = await fetch(
    'https://cdn.example.com/fonts/Inter-Bold.ttf'
  ).then(res => res.arrayBuffer());

  return fontData;
}
```

### Complete API Route (Next.js App Router)

```javascript
// app/api/og/route.jsx
import { ImageResponse } from '@vercel/og';

export const runtime = 'edge';

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const title = searchParams.get('title') || 'Default Title';
  const author = searchParams.get('author') || '';
  const date = searchParams.get('date') || '';
  const category = searchParams.get('category') || '';

  // Load custom font
  const interBold = await fetch(
    new URL('../../assets/fonts/Inter-Bold.ttf', import.meta.url)
  ).then(res => res.arrayBuffer());

  const interRegular = await fetch(
    new URL('../../assets/fonts/Inter-Regular.ttf', import.meta.url)
  ).then(res => res.arrayBuffer());

  return new ImageResponse(
    (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          padding: '60px',
          background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
          color: 'white',
          fontFamily: 'Inter',
        }}
      >
        {/* Top: Category badge */}
        {category && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <span
              style={{
                background: '#3b82f6',
                color: 'white',
                padding: '8px 20px',
                borderRadius: '20px',
                fontSize: '20px',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '1px',
              }}
            >
              {category}
            </span>
          </div>
        )}

        {/* Middle: Title */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          }}
        >
          <h1
            style={{
              fontSize: title.length > 60 ? '42px' : '56px',
              fontWeight: 700,
              lineHeight: 1.2,
              margin: 0,
              color: '#f8fafc',
            }}
          >
            {title}
          </h1>
        </div>

        {/* Bottom: Author + Date + Logo */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {author && (
              <span style={{ fontSize: '24px', color: '#94a3b8' }}>
                {author}
              </span>
            )}
            {date && (
              <span style={{ fontSize: '18px', color: '#64748b' }}>
                {date}
              </span>
            )}
          </div>
          <span
            style={{
              fontSize: '28px',
              fontWeight: 700,
              color: '#3b82f6',
            }}
          >
            YourBrand
          </span>
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
      fonts: [
        { name: 'Inter', data: interBold, weight: 700, style: 'normal' },
        { name: 'Inter', data: interRegular, weight: 400, style: 'normal' },
      ],
    }
  );
}
```

**Usage:** `https://yoursite.com/api/og?title=My+Course&author=Thierry&category=React`

### Satori Standalone (without Vercel)

```javascript
import satori from 'satori';
import { Resvg } from '@resvg/resvg-js';
import fs from 'fs';

const fontData = fs.readFileSync('./fonts/Inter-Bold.ttf');

const svg = await satori(
  {
    type: 'div',
    props: {
      style: { width: '100%', height: '100%', display: 'flex', background: '#1a1a2e', color: 'white', alignItems: 'center', justifyContent: 'center', fontSize: '48px' },
      children: 'Hello OG Image',
    },
  },
  {
    width: 1200,
    height: 630,
    fonts: [{ name: 'Inter', data: fontData, weight: 700 }],
  }
);

const resvg = new Resvg(svg, { fitTo: { mode: 'width', value: 1200 } });
const pngData = resvg.render();
fs.writeFileSync('og.png', pngData.asPng());
```

---

## Approach B: Sharp + Canvas (Any Node.js Server)

Works on any hosting provider. No edge runtime required. Uses `@napi-rs/canvas` (faster, prebuilt) or `canvas` (node-canvas, requires native deps).

### Installation

```bash
npm install sharp @napi-rs/canvas
```

### Complete Express Route

```javascript
import express from 'express';
import sharp from 'sharp';
import { createCanvas, GlobalFonts } from '@napi-rs/canvas';
import path from 'path';

const app = express();

// Register custom fonts
GlobalFonts.registerFromPath(
  path.resolve('./fonts/Inter-Bold.ttf'),
  'InterBold'
);
GlobalFonts.registerFromPath(
  path.resolve('./fonts/Inter-Regular.ttf'),
  'InterRegular'
);

function wrapText(ctx, text, maxWidth) {
  const words = text.split(' ');
  const lines = [];
  let currentLine = '';

  for (const word of words) {
    const testLine = currentLine ? `${currentLine} ${word}` : word;
    const { width } = ctx.measureText(testLine);
    if (width > maxWidth && currentLine) {
      lines.push(currentLine);
      currentLine = word;
    } else {
      currentLine = testLine;
    }
  }
  if (currentLine) lines.push(currentLine);
  return lines;
}

async function generateOgImage({ title, author, date, category }) {
  const WIDTH = 1200;
  const HEIGHT = 630;
  const PADDING = 60;

  const canvas = createCanvas(WIDTH, HEIGHT);
  const ctx = canvas.getContext('2d');

  // Background gradient (simulated with rectangles)
  const gradient = ctx.createLinearGradient(0, 0, WIDTH, HEIGHT);
  gradient.addColorStop(0, '#0f172a');
  gradient.addColorStop(0.5, '#1e293b');
  gradient.addColorStop(1, '#0f172a');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

  // Decorative accent line
  ctx.fillStyle = '#3b82f6';
  ctx.fillRect(PADDING, PADDING, 80, 6);

  // Category badge
  if (category) {
    ctx.font = '18px InterBold';
    const badgeText = category.toUpperCase();
    const badgeWidth = ctx.measureText(badgeText).width + 32;
    ctx.fillStyle = '#3b82f6';
    roundRect(ctx, PADDING, PADDING + 30, badgeWidth, 36, 18);
    ctx.fill();
    ctx.fillStyle = '#ffffff';
    ctx.fillText(badgeText, PADDING + 16, PADDING + 54);
  }

  // Title
  const titleY = category ? PADDING + 100 : PADDING + 60;
  ctx.fillStyle = '#f8fafc';
  ctx.font = `${title.length > 60 ? 42 : 56}px InterBold`;
  const titleLines = wrapText(ctx, title, WIDTH - PADDING * 2);
  const lineHeight = title.length > 60 ? 52 : 68;
  titleLines.forEach((line, i) => {
    ctx.fillText(line, PADDING, titleY + (i + 1) * lineHeight);
  });

  // Author
  if (author) {
    ctx.fillStyle = '#94a3b8';
    ctx.font = '24px InterRegular';
    ctx.fillText(author, PADDING, HEIGHT - PADDING - 30);
  }

  // Date
  if (date) {
    ctx.fillStyle = '#64748b';
    ctx.font = '18px InterRegular';
    ctx.fillText(date, PADDING, HEIGHT - PADDING);
  }

  // Brand logo text (bottom right)
  ctx.fillStyle = '#3b82f6';
  ctx.font = '28px InterBold';
  ctx.textAlign = 'right';
  ctx.fillText('YourBrand', WIDTH - PADDING, HEIGHT - PADDING);
  ctx.textAlign = 'left';  // Reset

  // Convert canvas to PNG buffer, then optimize with Sharp
  const rawPng = canvas.toBuffer('image/png');
  const optimized = await sharp(rawPng)
    .png({ quality: 90, compressionLevel: 6 })
    .toBuffer();

  return optimized;
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

app.get('/api/og', async (req, res) => {
  const { title, author, date, category } = req.query;

  if (!title) {
    return res.status(400).json({ error: 'title parameter is required' });
  }

  try {
    const imageBuffer = await generateOgImage({
      title,
      author: author || '',
      date: date || '',
      category: category || '',
    });

    res.setHeader('Content-Type', 'image/png');
    res.setHeader('Cache-Control', 'public, max-age=86400, s-maxage=604800');
    res.send(imageBuffer);
  } catch (err) {
    console.error('OG generation failed:', err);
    res.status(500).json({ error: 'Failed to generate image' });
  }
});
```

---

## Social Card Dimensions

| Platform | Dimensions | Aspect Ratio | Card Type |
|----------|-----------|--------------|-----------|
| Twitter/X | 1200 x 628 | ~1.91:1 | `summary_large_image` |
| Facebook | 1200 x 630 | ~1.91:1 | Default link preview |
| LinkedIn | 1200 x 627 | ~1.91:1 | Article/link share |
| Discord | 1200 x 630 | ~1.91:1 | Embed preview |
| Slack | 1200 x 630 | ~1.91:1 | Unfurl preview |
| Instagram | 1080 x 1080 | 1:1 | Shared post (not OG) |
| WhatsApp | 1200 x 630 | ~1.91:1 | Link preview |
| Pinterest | 1000 x 1500 | 2:3 | Pin image |

**Safe zone:** Keep critical text and logos at least 60px from any edge. Some platforms crop slightly or add rounded corners.

**Universal recommendation:** Use 1200 x 630 for all OG images. It works across every major platform.

---

## Dynamic Data Injection

Pattern for generating course/article-specific OG images:

```javascript
// In your page's metadata (Next.js App Router example)
export async function generateMetadata({ params }) {
  const course = await getCourse(params.slug);

  const ogUrl = new URL('/api/og', process.env.NEXT_PUBLIC_SITE_URL);
  ogUrl.searchParams.set('title', course.title);
  ogUrl.searchParams.set('author', course.instructor.name);
  ogUrl.searchParams.set('date', new Date(course.publishedAt).toLocaleDateString());
  ogUrl.searchParams.set('category', course.category);

  return {
    title: course.title,
    description: course.excerpt,
    openGraph: {
      title: course.title,
      description: course.excerpt,
      images: [{ url: ogUrl.toString(), width: 1200, height: 630 }],
    },
    twitter: {
      card: 'summary_large_image',
      title: course.title,
      description: course.excerpt,
      images: [ogUrl.toString()],
    },
  };
}
```

For Express/non-Next.js apps, inject the URL into your HTML template:

```javascript
app.get('/courses/:slug', async (req, res) => {
  const course = await getCourse(req.params.slug);
  const ogImageUrl = `${process.env.SITE_URL}/api/og?title=${encodeURIComponent(course.title)}&author=${encodeURIComponent(course.instructor)}`;

  res.render('course', { course, ogImageUrl });
});
```

```html
<!-- In your template (EJS, Handlebars, etc.) -->
<meta property="og:image" content="<%= ogImageUrl %>" />
```

---

## Caching Strategy

OG images are fetched by crawlers (Twitterbot, facebookexternalhit, etc.), not by every user. Caching is critical to avoid re-generating on every crawl.

### Option 1: HTTP Cache Headers (simplest)

```javascript
res.setHeader('Cache-Control', 'public, max-age=86400, s-maxage=604800');
// max-age: browser caches for 1 day
// s-maxage: CDN caches for 7 days
```

### Option 2: Pre-generate and Store

```javascript
import fs from 'fs/promises';
import path from 'path';
import crypto from 'crypto';

async function getOrGenerateOgImage(params) {
  // Create deterministic cache key from params
  const cacheKey = crypto
    .createHash('md5')
    .update(JSON.stringify(params))
    .digest('hex');

  const cachePath = path.resolve(`./cache/og/${cacheKey}.png`);

  try {
    // Return cached version if it exists
    const cached = await fs.readFile(cachePath);
    return cached;
  } catch {
    // Generate fresh
    const buffer = await generateOgImage(params);
    await fs.mkdir(path.dirname(cachePath), { recursive: true });
    await fs.writeFile(cachePath, buffer);
    return buffer;
  }
}

// Invalidation: delete cached file when content changes
async function invalidateOgCache(params) {
  const cacheKey = crypto
    .createHash('md5')
    .update(JSON.stringify(params))
    .digest('hex');

  const cachePath = path.resolve(`./cache/og/${cacheKey}.png`);
  await fs.unlink(cachePath).catch(() => {});  // Ignore if not found
}
```

### Option 3: CDN with Purge on Content Update

If using Cloudflare, Fastly, or similar:

```javascript
// After updating a course title:
await fetch(`https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/purge_cache`, {
  method: 'POST',
  headers: { Authorization: `Bearer ${CF_TOKEN}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    files: [`https://yoursite.com/api/og?title=${encodeURIComponent(oldTitle)}`],
  }),
});
```

---

## HTML Meta Tags (Complete Set)

Include these in your `<head>` for full social media coverage:

```html
<!-- Open Graph (Facebook, LinkedIn, Discord, Slack, WhatsApp) -->
<meta property="og:type" content="article" />
<meta property="og:title" content="Advanced React Patterns — Full Course" />
<meta property="og:description" content="Learn compound components, render props, and custom hooks with real-world examples." />
<meta property="og:image" content="https://yoursite.com/api/og?title=Advanced+React+Patterns" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="Course card: Advanced React Patterns" />
<meta property="og:url" content="https://yoursite.com/courses/react-patterns" />
<meta property="og:site_name" content="YourBrand" />
<meta property="og:locale" content="en_US" />

<!-- Twitter/X Card -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:site" content="@yourbrand" />
<meta name="twitter:creator" content="@instructor" />
<meta name="twitter:title" content="Advanced React Patterns — Full Course" />
<meta name="twitter:description" content="Learn compound components, render props, and custom hooks with real-world examples." />
<meta name="twitter:image" content="https://yoursite.com/api/og?title=Advanced+React+Patterns" />
<meta name="twitter:image:alt" content="Course card: Advanced React Patterns" />

<!-- Article-specific (optional, improves rich previews) -->
<meta property="article:author" content="https://yoursite.com/instructors/thierry" />
<meta property="article:published_time" content="2025-11-15T09:00:00Z" />
<meta property="article:section" content="React" />
<meta property="article:tag" content="React" />
<meta property="article:tag" content="Patterns" />
```

**Key rules:**
- `og:image` must be an **absolute URL** (not relative)
- Image must be accessible without authentication
- Minimum recommended size: 1200 x 630
- Maximum file size: 8MB (Facebook), 5MB (Twitter) — aim for under 500KB
- Use `og:image:alt` for accessibility

---

## Testing OG Images

### Online Validators

| Tool | URL | Tests |
|------|-----|-------|
| **opengraph.xyz** | https://opengraph.xyz | Preview across all platforms, shows raw tags |
| **Twitter Card Validator** | https://cards-dev.twitter.com/validator | Official Twitter/X preview |
| **Facebook Sharing Debugger** | https://developers.facebook.com/tools/debug/ | Facebook preview + cache purge |
| **LinkedIn Post Inspector** | https://www.linkedin.com/post-inspector/ | LinkedIn-specific rendering |
| **metatags.io** | https://metatags.io | Multi-platform preview with editor |

### Local Testing

```javascript
// Quick visual test: save to file and open
import open from 'open';  // npm install open
import fs from 'fs/promises';

const buffer = await generateOgImage({
  title: 'Advanced React Patterns — Full Course',
  author: 'Thierry N.',
  date: 'March 2026',
  category: 'React',
});

await fs.writeFile('/tmp/og-test.png', buffer);
await open('/tmp/og-test.png');
```

### Automated Visual Regression

```javascript
// In your test suite (Vitest/Jest)
import { describe, it, expect } from 'vitest';
import sharp from 'sharp';

describe('OG Image Generation', () => {
  it('generates correct dimensions', async () => {
    const buffer = await generateOgImage({ title: 'Test Title' });
    const meta = await sharp(buffer).metadata();
    expect(meta.width).toBe(1200);
    expect(meta.height).toBe(630);
    expect(meta.format).toBe('png');
  });

  it('handles long titles without overflow', async () => {
    const buffer = await generateOgImage({
      title: 'This Is an Extremely Long Course Title That Should Still Render Correctly Without Overflowing the Image Boundaries',
    });
    const meta = await sharp(buffer).metadata();
    expect(meta.width).toBe(1200);
    // Visual check: save to snapshots dir for manual review
  });

  it('file size stays under 500KB', async () => {
    const buffer = await generateOgImage({ title: 'Size Check' });
    expect(buffer.length).toBeLessThan(500 * 1024);
  });
});
```

### Force Social Platform Re-scrape

Platforms cache OG data aggressively. After updating an image:

- **Facebook:** Use the Sharing Debugger "Scrape Again" button
- **Twitter:** The Card Validator re-fetches automatically
- **LinkedIn:** Use Post Inspector to force refresh
- **Slack:** Edit the message or re-paste the link
- **Discord:** Append `?v=2` to the URL (cache buster)

---

