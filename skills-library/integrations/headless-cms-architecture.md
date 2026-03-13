# Headless CMS Architecture

> Comprehensive guide to decoupled content architecture: content API design, cache invalidation, multi-channel delivery, and integration patterns for Next.js and beyond.

**When to use:** Designing or evaluating a content platform that needs to serve content to multiple frontends (web, mobile, email, voice), or migrating from a monolithic CMS (WordPress) to a headless architecture.
**Stack:** Node.js/Express or Bun, Next.js, PostgreSQL, any CDN (Cloudflare/Vercel/Fastly)

---

## What "Headless" Means

**Traditional (monolithic) CMS:**
```
[CMS Backend + Database]
         |
    [Template Engine]      ← CMS controls how content looks
         |
    [HTML to Browser]
```

**Headless CMS:**
```
[CMS Backend + Database]
         |
    [Content API]          ← CMS only provides structured content
    /           \
[Web Frontend]  [Mobile App]  [Email]  [Voice]  [Any Consumer]
```

The CMS becomes a **content repository** with an API. Every consumer fetches the same structured data and renders it however it needs to.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Content Platform                       │
│                                                           │
│  ┌──────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │ Author   │    │  CMS Admin  │    │   Media Storage  │  │
│  │ Workflow │───►│    UI       │    │  (S3 / R2 / CDN) │  │
│  └──────────┘    └──────┬──────┘    └────────┬────────┘  │
│                          │                    │           │
│                   ┌──────▼──────┐             │           │
│                   │  PostgreSQL  │◄────────────┘           │
│                   │  (content)  │                          │
│                   └──────┬──────┘                          │
│                          │                                 │
│                   ┌──────▼──────┐                          │
│                   │ Content API  │ ← REST or GraphQL        │
│                   │  /api/v1/   │                          │
│                   └──────┬──────┘                          │
└──────────────────────────┼──────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
    ┌─────────▼─┐  ┌───────▼───┐  ┌────▼──────────┐
    │   CDN /   │  │  Mobile   │  │  Newsletter /  │
    │  Next.js  │  │  App API  │  │   Email ESP    │
    │  (ISR)    │  │ (React N) │  │  (Resend etc)  │
    └─────────┬─┘  └───────────┘  └───────────────┘
              │
    ┌─────────▼──────────┐
    │   End User Browser  │
    └─────────────────────┘
```

---

## REST vs GraphQL Content API

### Use REST when:
- Your content types are simple and relatively fixed
- Consumers are varied (mobile devs, third-party integrators) — REST is universally understood
- You want CDN-cacheable responses (GET requests with predictable URLs)
- Team is not yet familiar with GraphQL

### Use GraphQL when:
- Different consumers need different subsets of the same content (web wants full post, mobile wants summary only)
- Content is deeply relational (post → author → bio → social links → recent posts)
- You want to avoid over-fetching or under-fetching
- You're building a developer platform where external devs write their own queries

### REST Content API Design

```typescript
// REST endpoints for a content API
GET    /api/v1/posts                    // list (paginated, filterable)
GET    /api/v1/posts/:slug              // single post by slug
GET    /api/v1/posts/:slug/related      // related posts
GET    /api/v1/categories               // all categories
GET    /api/v1/categories/:slug/posts   // posts in category
GET    /api/v1/authors/:id              // author profile
GET    /api/v1/search?q=...            // full-text search
GET    /api/v1/tags                     // all tags
GET    /api/v1/feed.rss                 // RSS feed

// Query parameters for list endpoints:
// ?page=1&limit=20
// ?category=typescript
// ?tag=tutorial,beginner
// ?status=published        (admin only)
// ?sort=published_at:desc  // or views:desc, title:asc
// ?fields=id,title,slug,excerpt  // field selection (reduces payload)
```

### Response envelope pattern:

```json
{
  "data": {
    "id": "uuid",
    "title": "My Post",
    "slug": "my-post",
    "excerpt": "...",
    "published_at": "2026-03-08T10:00:00Z",
    "author": { "id": "uuid", "name": "Thierry", "avatar": "..." },
    "categories": [{ "id": "uuid", "name": "TypeScript", "slug": "typescript" }],
    "tags": ["tutorial", "beginner"],
    "reading_time_minutes": 5
  },
  "meta": {}
}

// List response:
{
  "data": [...],
  "pagination": {
    "total": 142,
    "page": 1,
    "limit": 20,
    "pages": 8,
    "next_cursor": "abc123"
  }
}
```

---

## Content Modeling

Design content types to be **channel-agnostic** — the same content should work on web, mobile, email, and voice without transformation.

```
Content Type: Post
├── id (UUID)
├── title (string, required)
├── slug (string, unique, URL-safe)
├── excerpt (string, 150-300 chars — used as email preview, social meta)
├── body_json (TipTap/ProseMirror JSON — lossless, renderable anywhere)
├── body_html (string — cached render of body_json)
├── featured_image (object: { url, alt, width, height })
├── author (relationship → Author)
├── categories (relationship → Category[])
├── tags (string[])
├── status (enum: draft|in_review|scheduled|published|archived)
├── published_at (timestamp UTC)
├── scheduled_at (timestamp UTC)
├── seo_title (string — overrides title for <title> tag)
├── seo_description (string — overrides excerpt for <meta description>)
├── og_image (string — overrides featured_image for Open Graph)
├── reading_time_minutes (computed)
├── word_count (computed)
└── created_at, updated_at (timestamps)
```

**Key principle:** Store content in the most flexible format (JSON), cache the rendered format (HTML). Compute derived fields (reading_time, word_count) on write, not on read.

---

## Cache Invalidation Strategy

The hardest problem in headless CMS. When content changes, cached pages must be invalidated.

### Strategy 1: Time-Based (ISR — Incremental Static Regeneration)

```typescript
// Next.js page with ISR
export async function getStaticProps({ params }) {
  const post = await fetch(`${process.env.CMS_API_URL}/posts/${params.slug}`).then(r => r.json());

  return {
    props: { post },
    revalidate: 60,    // Regenerate this page at most once per 60 seconds
  };
}
```

Simple but stale up to `revalidate` seconds. Acceptable for blogs, not acceptable for breaking news.

### Strategy 2: On-Demand Revalidation (Webhook → Next.js)

```typescript
// CMS side: fire webhook when content is published/updated
async function notifyFrontend(contentId: string, slug: string, event: string) {
  const webhookSecret = process.env.REVALIDATION_SECRET;

  await fetch(`${process.env.FRONTEND_URL}/api/revalidate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-webhook-secret': webhookSecret,
    },
    body: JSON.stringify({ contentId, slug, event }),
  });
}

// Next.js side: /api/revalidate route
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from 'next/cache';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const secret = request.headers.get('x-webhook-secret');

  if (secret !== process.env.REVALIDATION_SECRET) {
    return NextResponse.json({ error: 'Invalid secret' }, { status: 401 });
  }

  const { slug, event } = await request.json();

  // Revalidate specific paths
  revalidatePath(`/posts/${slug}`);
  revalidatePath('/posts');                // index page
  revalidatePath('/');                     // home page (if it shows recent posts)
  revalidateTag('posts');                  // all pages tagged "posts"

  return NextResponse.json({
    revalidated: true,
    now: Date.now(),
    slug,
    event,
  });
}
```

### Strategy 3: CDN Purge (Cloudflare/Fastly)

```typescript
// Purge specific URLs from Cloudflare cache on publish
async function purgeCloudflareCache(urls: string[]): Promise<void> {
  const response = await fetch(
    `https://api.cloudflare.com/client/v4/zones/${process.env.CF_ZONE_ID}/purge_cache`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.CF_API_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ files: urls }),
    }
  );

  if (!response.ok) {
    throw new Error(`Cloudflare purge failed: ${response.statusText}`);
  }
}

// Call this in the onPublishSuccess callback:
onPublishSuccess: async (id, title) => {
  const { rows } = await db.query('SELECT slug FROM content WHERE id = $1', [id]);
  if (rows[0]?.slug) {
    await purgeCloudflareCache([
      `https://yourdomain.com/posts/${rows[0].slug}`,
      `https://yourdomain.com/posts`,
      `https://yourdomain.com/`,
    ]);
  }
}
```

---

## Webhook Pattern: CMS → Frontend

```typescript
// lib/webhooks.ts

interface WebhookEvent {
  event: 'content.published' | 'content.updated' | 'content.archived' | 'content.scheduled';
  contentId: string;
  contentType: string;
  slug?: string;
  timestamp: string;
}

async function fireWebhooks(event: WebhookEvent): Promise<void> {
  const webhooks = await db.query(
    "SELECT url, secret FROM webhooks WHERE events @> ARRAY[$1]::text[] AND active = true",
    [event.event]
  );

  const payload = JSON.stringify(event);
  const timestamp = Date.now().toString();

  await Promise.allSettled(
    webhooks.rows.map(async (webhook) => {
      const signature = createHmacSignature(payload, webhook.secret, timestamp);

      try {
        const res = await fetch(webhook.url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'X-Webhook-Timestamp': timestamp,
          },
          body: payload,
          signal: AbortSignal.timeout(10_000),  // 10s timeout
        });

        if (!res.ok) {
          console.error(`Webhook ${webhook.url} responded ${res.status}`);
        }
      } catch (err) {
        console.error(`Webhook delivery failed to ${webhook.url}:`, err);
      }
    })
  );
}

import { createHmac } from 'crypto';

function createHmacSignature(payload: string, secret: string, timestamp: string): string {
  return createHmac('sha256', secret)
    .update(`${timestamp}.${payload}`)
    .digest('hex');
}
```

---

## Multi-Channel Delivery

Same content, different rendering:

```typescript
// Each channel gets what it needs from the same API response

// WEB: Full HTML rendering via TipTap generateHTML
import { generateHTML } from '@tiptap/html';

const webContent = generateHTML(post.body_json, extensions);

// EMAIL: Strip complex blocks, inline styles, simplify for email clients
function contentToEmailHtml(bodyJson: object): string {
  // Use a simplified extension set for email compatibility
  return generateHTML(bodyJson, [StarterKit, Link]);
  // Then run through an email CSS inliner (juice npm package)
}

// MOBILE (React Native): Pass JSON, render natively
// The mobile app receives body_json and renders each node type
// with its own native components (no HTML string needed)

// RSS: Use excerpt or truncated body as text
const rssDescription = post.excerpt || post.body_html?.slice(0, 500);

// VOICE (text-to-speech): Extract plain text
function contentToPlainText(bodyJson: object): string {
  return editor.getText();  // or walk the JSON tree
}

// SOCIAL: Use og_image + excerpt + title
const socialPreview = {
  title: post.seo_title ?? post.title,
  description: post.seo_description ?? post.excerpt,
  image: post.og_image ?? post.featured_image?.url,
};
```

---

## Next.js Integration Patterns

### Static Generation with ISR (blog posts)

```typescript
// app/posts/[slug]/page.tsx
import { Metadata } from 'next';

// Generate static params for all published posts (SSG)
export async function generateStaticParams() {
  const res = await fetch(`${process.env.CMS_API_URL}/posts?fields=slug&limit=1000`);
  const { data } = await res.json();
  return data.map((post: { slug: string }) => ({ slug: post.slug }));
}

// Generate metadata for SEO
export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const post = await getPost(params.slug);
  return {
    title: post.seo_title ?? post.title,
    description: post.seo_description ?? post.excerpt,
    openGraph: { images: [post.og_image ?? post.featured_image?.url] },
  };
}

// Page component
export default async function PostPage({ params }: { params: { slug: string } }) {
  const post = await getPost(params.slug);
  return <PostTemplate post={post} />;
}

async function getPost(slug: string) {
  const res = await fetch(`${process.env.CMS_API_URL}/posts/${slug}`, {
    next: { revalidate: 60, tags: ['posts', `post-${slug}`] },  // ISR + tag-based invalidation
  });
  if (!res.ok) throw new Error('Post not found');
  const { data } = await res.json();
  return data;
}
```

### Content Preview Mode (Drafts)

```typescript
// app/api/preview/route.ts
// Enables preview mode so editors can see draft content

import { draftMode } from 'next/headers';
import { redirect } from 'next/navigation';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const secret = searchParams.get('secret');
  const slug   = searchParams.get('slug');

  if (secret !== process.env.PREVIEW_SECRET || !slug) {
    return new Response('Invalid preview request', { status: 401 });
  }

  // Enable Draft Mode — all fetch() calls will bypass ISR cache
  draftMode().enable();

  redirect(`/posts/${slug}`);
}

// In the post page, check for draft mode and fetch unpublished content:
import { draftMode } from 'next/headers';

export default async function PostPage({ params }) {
  const { isEnabled: isDraft } = draftMode();

  const url = isDraft
    ? `${process.env.CMS_API_URL}/posts/${params.slug}?status=any`   // includes drafts
    : `${process.env.CMS_API_URL}/posts/${params.slug}`;              // published only

  const res = await fetch(url, {
    headers: isDraft ? { 'Authorization': `Bearer ${process.env.CMS_PREVIEW_TOKEN}` } : {},
    cache: isDraft ? 'no-store' : 'default',
  });

  const { data: post } = await res.json();
  return <PostTemplate post={post} isDraft={isDraft} />;
}
```

---

## Self-Hosted vs SaaS Decision Guide

| Factor | Self-Hosted (Payload, Strapi, Directus) | SaaS (Contentful, Sanity, Storyblok) |
|--------|-----------------------------------------|---------------------------------------|
| Monthly cost | VPS cost only (~$10-40) | $0-300+ depending on plan |
| Data control | Full — your DB, your server | Vendor-controlled |
| Setup time | 1-4 hours | 15 minutes |
| Ops burden | You manage updates, backups | Vendor handles it |
| Scaling | You handle it | Auto-scales |
| Custom logic | Full access | API only (webhooks, plugins) |
| Best for | Products, sensitive data | Agencies, rapid launch |

**Rule:** If you're building a product (not an agency deliverable), self-host. You control the roadmap and data. If you need to launch in an afternoon for a client, use SaaS.

---

## Common Gotchas

1. **The frontend is not part of the CMS** — headless means you choose your own frontend. The CMS provides data, not views. Don't let the CMS dictate your frontend stack.
2. **Cache invalidation is the hard part** — "there are only two hard things in CS..." The webhook → revalidate pattern is the right approach. Build it from day one, not as an afterthought.
3. **Content preview requires a special auth token** — your CMS API should have a preview token that bypasses the `status = 'published'` filter. Keep this token secret (server-side only, never expose to browser).
4. **Media assets need their own CDN** — don't serve images from your CMS API server. Upload to S3/R2 and serve via CDN. Add a `cdn_url` field to your media records.
5. **Reading time is not optional** — compute and store it on write. Every content platform's UI shows reading time, and computing it on every read is wasteful.
