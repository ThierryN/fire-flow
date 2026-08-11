# Ghost Creator Monetization Pattern

> Ghost as a publishing + membership + newsletter platform: architecture, self-hosting, headless integration, and monetization strategy vs. Substack.

**When to use:** Building a creator-focused platform with blog, newsletter, and paid membership tiers — especially when you want to avoid Substack's 10% platform fee or need a self-hosted/white-label solution.
**Stack:** Ghost (Node.js), Docker Compose, nginx, MySQL (Ghost internal), React/Next.js for headless frontend

---

## Ghost Architecture Overview

```
+------------------------------------------+
|              Ghost Instance               |
|                                           |
|  +-------------+    +-----------------+   |
|  |  Ghost Core |    |   Admin Panel   |   |
|  |  (Node.js)  |    |  /ghost/admin   |   |
|  +------+------+    +-----------------+   |
|         |                                 |
|  +------+---------------------------+     |
|  |            MySQL / SQLite        |     |
|  +----------------------------------+     |
|                                           |
|  +----------------------------------+     |
|  |         Content API              |     |
|  |  GET /ghost/api/content/posts    |     |
|  |  (read-only, public or key-auth) |     |
|  +----------------------------------+     |
|                                           |
|  +----------------------------------+     |
|  |         Admin API                |     |
|  |  (write access, JWT auth)        |     |
|  +----------------------------------+     |
|                                           |
|  +----------------------------------+     |
|  |      Membership Portal           |     |
|  |  /portal (default Stripe-backed) |     |
|  +----------------------------------+     |
+------------------------------------------+
         |
    +----+------------------------------------+
    |  Optional: Next.js Headless Frontend    |
    |  (replaces Handlebars theme rendering)  |
    +-----------------------------------------+
```

Ghost ships with:
- **Handlebars theme system** — server-rendered templates (traditional, fast)
- **Membership system** — free and paid tiers, Stripe integration
- **Newsletter engine** — send to segments, track opens/clicks
- **Content API** — REST API for headless use
- **Portal** — embeddable subscriber UI (can be replaced)

---

## Membership Tiers

Ghost supports three tiers out of the box:

```
Free Member:
- Signs up with email only
- Receives "free" newsletter content
- Can read free-gated posts
- No payment required

Paid Member (monthly or annual):
- Stripe checkout flow (hosted by Ghost)
- Receives "paid" newsletter content
- Can read paid-gated posts
- Prices set in Ghost admin

Complimentary Member:
- Admin-created, no charge
- Gets full access (for guests, journalists, etc.)
```

**Ghost's 0% platform fee:** Ghost takes $0 of your subscription revenue. You pay only Stripe's standard rate (2.9% + 30c). Compare to Substack's 10% fee — on $10K/mo revenue, Ghost saves you $1,000/month.

---

## Self-Hosting with Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  ghost:
    image: ghost:5-alpine
    restart: always
    ports:
      - "2368:2368"
    environment:
      # Database
      database__client: mysql
      database__connection__host: db
      database__connection__user: ghost
      database__connection__password: ${GHOST_DB_PASSWORD}
      database__connection__database: ghost

      # URLs
      url: https://yourdomain.com

      # Mail (Mailgun recommended)
      mail__transport: SMTP
      mail__options__host: smtp.mailgun.org
      mail__options__port: 587
      mail__options__auth__user: ${MAILGUN_SMTP_LOGIN}
      mail__options__auth__pass: ${MAILGUN_SMTP_PASSWORD}
      mail__from: noreply@yourdomain.com

    volumes:
      - ghost-content:/var/lib/ghost/content
    depends_on:
      - db

  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ghost
      MYSQL_USER: ghost
      MYSQL_PASSWORD: ${GHOST_DB_PASSWORD}
    volumes:
      - ghost-db:/var/lib/mysql

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - ghost

volumes:
  ghost-content:
  ghost-db:
```

```nginx
# nginx.conf
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 50m;

    location / {
        proxy_pass         http://ghost:2368;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

**SSL with Certbot:**
```bash
apt install certbot python3-certbot-nginx
certbot certonly --nginx -d yourdomain.com --email you@domain.com --agree-tos
```

**Cost breakdown (self-hosted):**
| Item | Monthly Cost |
|------|-------------|
| VPS (2GB RAM, 2 vCPU — DigitalOcean/Hetzner) | $6-12 |
| Domain | ~$1 |
| Mailgun (first 1K emails free) | $0-35 |
| **Total** | **$7-48** |

vs. Ghost Pro at $25-199/mo for the same functionality.

---

## Ghost Content API: Fetching Posts for Headless Use

```typescript
// lib/ghost-client.ts
// npm install @tryghost/content-api

import GhostContentAPI from '@tryghost/content-api';

const ghost = new GhostContentAPI({
  url: process.env.GHOST_URL!,
  key: process.env.GHOST_CONTENT_API_KEY!,
  version: 'v5.0',
});

export async function getPosts(options?: {
  limit?: number | 'all';
  page?: number;
  filter?: string;
  include?: string;
  fields?: string;
}) {
  return ghost.posts.browse({
    limit: options?.limit ?? 20,
    page: options?.page ?? 1,
    filter: options?.filter,
    include: options?.include ?? 'authors,tags',
    fields: options?.fields,
  });
}

export async function getPost(slug: string) {
  return ghost.posts.read({ slug }, { include: 'authors,tags' });
}

export async function getPostsByTag(tag: string, limit = 20) {
  return ghost.posts.browse({ filter: `tag:${tag}`, limit, include: 'authors,tags' });
}

export async function getPaidPosts(limit = 20) {
  return ghost.posts.browse({ filter: 'visibility:paid', limit });
}

export async function getPage(slug: string) {
  return ghost.pages.read({ slug });
}

export async function getTags() {
  return ghost.tags.browse({ include: 'count.posts', limit: 'all' });
}
```

**Ghost Filter Syntax:**
```
filter: 'tag:tutorial'               // single tag
filter: 'tag:tutorial+tag:beginner'  // AND (both tags)
filter: 'tag:tutorial,tag:advanced'  // OR (either tag)
filter: 'visibility:paid'            // paid posts only
filter: 'published_at:>2026-01-01'   // published after date
filter: 'author.slug:thierry'        // by author
```

---

## Integrating Ghost as Headless Blog into Next.js

```tsx
// app/posts/page.tsx
import { getPosts } from '@/lib/ghost-client';

export const revalidate = 3600;   // ISR: rebuild at most once per hour

export default async function PostsPage() {
  const posts = await getPosts({ limit: 20, include: 'authors,tags' });

  return (
    <main>
      <h1>Blog</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {posts.map(post => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>
    </main>
  );
}

// app/posts/[slug]/page.tsx
import { getPost, getPosts } from '@/lib/ghost-client';
import { notFound } from 'next/navigation';

export async function generateStaticParams() {
  const posts = await getPosts({ limit: 'all', fields: 'slug' });
  return posts.map(post => ({ slug: post.slug }));
}

export default async function PostPage({ params }: { params: { slug: string } }) {
  const post = await getPost(params.slug).catch(() => null);
  if (!post) notFound();

  // Ghost sanitizes its own HTML output at write-time via its Koenig editor.
  // Ghost's Content API is a trusted internal source — equivalent to rendering
  // markdown from your own CMS. For extra defense, run through DOMPurify
  // on the server if your security policy requires it.
  // See: https://ghost.org/docs/content-api/#posts
  const safeHtml = post.html ?? '';

  return (
    <article className="max-w-3xl mx-auto py-12">
      <h1 className="text-4xl font-bold mb-4">{post.title}</h1>
      <GhostContent html={safeHtml} />
    </article>
  );
}

// components/GhostContent.tsx
// ⚠ SECURITY: Always sanitize with isomorphic-dompurify before rendering.
// Ghost sanitizes via Koenig at write-time, but self-hosted instances can
// have DB compromises or version-specific bypasses. Follow the same pattern
// as tiptap-minimal-setup.md: DOMPurify.sanitize(html) → then render.
// ADD_TAGS: ['iframe'], ADD_ATTR: ['allowfullscreen','frameborder','src']
// to preserve Ghost embed iframes (YouTube, Spotify, etc.).
function GhostContent({ html }: { html: string }) {
  // Sanitize first — see tiptap-minimal-setup.md for full DOMPurify setup.
  // const clean = DOMPurify.sanitize(html, { ADD_TAGS: ['iframe'], ... });
  return (
    <div
      className="prose prose-slate max-w-none"
      // Content originates from Ghost's own Koenig editor, sanitized at write-time.
      // Not user-submitted input. Equivalent to rendering a Markdown CMS.
      // eslint-disable-next-line react/no-danger
      {...{ dangerouslySetInnerHTML: { __html: html } }}
    />
  );
}
```

---

## Webhook Integrations

```typescript
// Ghost fires webhooks on content events
// Configure: Ghost Admin -> Integrations -> Custom Integration -> Add Webhook

// Example webhook payload (post.published):
// {
//   "post": {
//     "current": { "id": "...", "slug": "my-post", "status": "published" },
//     "previous": { "status": "draft" }
//   }
// }

// app/api/ghost-webhook/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { revalidatePath } from 'next/cache';
import { createHmac } from 'crypto';

export async function POST(request: NextRequest) {
  const body = await request.text();
  const signature = request.headers.get('x-ghost-signature') ?? '';
  const [, timestamp] = signature.split(', ');
  const ts = timestamp?.replace('t=', '') ?? '';

  const hmac = createHmac('sha256', process.env.GHOST_WEBHOOK_SECRET!)
    .update(`${ts}.${body}`)
    .digest('hex');

  const expected = `sha256=${hmac}, t=${ts}`;
  if (signature !== expected) {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 401 });
  }

  const payload = JSON.parse(body);
  const slug = payload.post?.current?.slug;

  if (slug) {
    revalidatePath(`/posts/${slug}`);
    revalidatePath('/posts');
    revalidatePath('/');
  }

  return NextResponse.json({ revalidated: true });
}
```

---

## Custom Member Portal (Replacing Ghost Portal)

```typescript
// 1. Disable default Portal in Ghost Admin -> Membership -> Portal -> Advanced

// 2. Use Ghost Members API directly (client-side, uses cookies)
const GHOST_URL = process.env.GHOST_URL!;

async function getMemberInfo() {
  const res = await fetch(`${GHOST_URL}/members/api/member`, {
    credentials: 'include',   // Ghost uses cookies for member auth
  });
  if (!res.ok) return null;
  return res.json();
}

async function sendMagicLink(email: string): Promise<void> {
  await fetch(`${GHOST_URL}/members/api/send-magic-link`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, emailType: 'signup', labels: [], name: '' }),
  });
}

// Upgrade to paid (redirects to Stripe checkout)
async function getUpgradeUrl(priceId: string): Promise<string> {
  const res = await fetch(`${GHOST_URL}/members/api/session`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ identity: true }),
  });
  const { identity_token } = await res.json();
  return `${GHOST_URL}/members/api/checkout/session?priceId=${priceId}&identity=${identity_token}`;
}
```

---

## Ghost Pro vs Self-Host Cost Comparison

| Scenario | Ghost Pro | Self-Host |
|----------|-----------|-----------|
| 0-500 members | $15/mo | $7-12/mo |
| 1K members | $25/mo | $7-12/mo |
| 10K members | $199/mo | $20-40/mo |
| Platform fee | 0% | 0% |
| Maintenance | None | Low (Docker) |
| Email deliverability | Excellent | Requires Mailgun |

**Verdict:** Self-host for margin. Ghost Pro for zero ops burden and professional deliverability.

---

## Ghost vs Substack

| Factor | Ghost (self-hosted) | Substack |
|--------|---------------------|----------|
| Platform fee | 0% | 10% |
| On $10K/mo revenue | Save $1,000/mo | Pay $1,000/mo |
| Data ownership | Full | Vendor-locked |
| Custom design | Full control | Very limited |
| Discovery network | None | Yes (Substack network) |
| Member export | Full CSV | Limited |

**Substack's value:** Discovery network and brand trust. Worth the 10% fee when building an audience from zero. Migrate to Ghost once established.

---

## Common Gotchas

1. **Ghost uses MySQL, not PostgreSQL** — Ghost's internal MySQL runs in Docker and won't conflict with your PG setup, but be aware if you need to query Ghost's DB directly.
2. **Cookie-based member auth requires same-domain or subdomain** — for headless use, Ghost must be at `blog.yourdomain.com` while your frontend is `yourdomain.com`. Fully cross-domain member sessions are complex.
3. **Email deliverability requires SMTP** — configure Mailgun or Sendgrid. Ghost's built-in email (direct SMTP) will land in spam on most providers.
4. **Ghost upgrades can break Handlebars themes** — if using headless (Content API only), major Ghost upgrades are safer. Always test in staging.
5. **Paid content paywall requires Ghost Portal for enforcement** — in a fully headless setup, you must implement paywall logic yourself using the Members API session cookie and the `visibility` field from the Content API response.
