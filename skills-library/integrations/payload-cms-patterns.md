# Payload CMS Patterns

> Production patterns for Payload CMS v3: collections, access control, hooks, and deployment — the TypeScript-first embedded CMS for Next.js apps.

**When to use:** Building a content platform with Next.js where you want a CMS that's part of your codebase (not a separate service), with full TypeScript control over schema, access, and business logic.
**Stack:** Payload CMS v3, Next.js 14+ (App Router), PostgreSQL (with Payload's Postgres adapter), TypeScript

---

## What Makes Payload Different

| Feature | Payload | Strapi | Directus |
|---------|---------|--------|----------|
| Config style | TypeScript code | JSON/TypeScript | JSON/GUI |
| Embeds in Next.js | Yes (v3) | No | No |
| Type safety | Full (generated types) | Partial | No |
| Database | PostgreSQL, SQLite, MongoDB | PostgreSQL, MySQL, SQLite | Any DB |
| Admin UI | Built-in, customizable | Built-in | Built-in |
| Local API | Yes (no HTTP round-trip) | No | No |
| Lexical editor | Yes (v3) | No (custom) | No |

**Payload's killer feature:** The **Local API** — you can call `payload.find()`, `payload.create()`, etc. directly in your Next.js server components. No HTTP request. Blazing fast, fully typed.

---

## Project Structure

```
my-app/
├── app/
│   ├── (app)/              # Your actual app routes
│   ├── (payload)/          # Payload admin UI routes (auto-generated)
│   │   ├── admin/
│   │   └── api/
│   ├── layout.tsx
│   └── page.tsx
├── payload.config.ts        # Main Payload configuration
├── collections/
│   ├── Posts.ts
│   ├── Authors.ts
│   ├── Categories.ts
│   └── Media.ts
├── globals/
│   ├── Settings.ts
│   └── Navigation.ts
└── payload-types.ts         # Auto-generated (run: npm run generate:types)
```

---

## Payload Config

```typescript
// payload.config.ts
import { buildConfig } from 'payload';
import { postgresAdapter } from '@payloadcms/db-postgres';
import { lexicalEditor } from '@payloadcms/richtext-lexical';
import { nodemailerAdapter } from '@payloadcms/email-nodemailer';
import sharp from 'sharp';

import { Posts } from './collections/Posts';
import { Authors } from './collections/Authors';
import { Categories } from './collections/Categories';
import { Media } from './collections/Media';
import { Settings } from './globals/Settings';

export default buildConfig({
  // Admin UI settings
  admin: {
    user: 'users',
    meta: {
      titleSuffix: '— My CMS',
    },
  },

  // Collections = content types (like database tables)
  collections: [Posts, Authors, Categories, Media],

  // Globals = single-instance settings
  globals: [Settings],

  // Database adapter
  db: postgresAdapter({
    pool: {
      connectionString: process.env.DATABASE_URL,
    },
  }),

  // Rich text editor
  editor: lexicalEditor({}),

  // Media handling
  sharp,

  // Secret for JWTs
  secret: process.env.PAYLOAD_SECRET!,

  // TypeScript type generation
  typescript: {
    outputFile: 'payload-types.ts',
  },

  // Email (optional)
  email: nodemailerAdapter({
    defaultFromAddress: 'noreply@yourdomain.com',
    defaultFromName: 'My CMS',
    transportOptions: {
      host: process.env.SMTP_HOST,
      port: 587,
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
      },
    },
  }),
});
```

---

## Collection Definition: Posts

```typescript
// collections/Posts.ts
import type { CollectionConfig } from 'payload';
import { isEditor, isAdmin, isAuthorOrEditor } from '../access/roles';

export const Posts: CollectionConfig = {
  slug: 'posts',
  labels: {
    singular: 'Post',
    plural: 'Posts',
  },

  // Admin UI configuration
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'status', 'author', 'publishedAt'],
    group: 'Content',
  },

  // Access control — collection level
  access: {
    read:   ({ req }) => req.user?.role === 'admin' || { status: { equals: 'published' } },
    create: isAuthorOrEditor,
    update: isAuthorOrEditor,
    delete: isAdmin,
  },

  // Hooks — lifecycle callbacks
  hooks: {
    beforeChange: [setAuthorOnCreate, generateSlug, computeReadingTime],
    afterChange:  [invalidateCacheOnPublish],
    beforeRead:   [],
    afterRead:    [],
    beforeDelete: [preventDeletingPublished],
  },

  // Timestamps (auto-managed)
  timestamps: true,

  // Fields = columns
  fields: [
    {
      name: 'title',
      type: 'text',
      required: true,
      admin: { description: 'The post title — used for SEO and display' },
    },
    {
      name: 'slug',
      type: 'text',
      unique: true,
      admin: {
        position: 'sidebar',
        description: 'URL-friendly identifier (auto-generated from title)',
      },
      hooks: {
        beforeValidate: [({ value, data }) => value ?? slugify(data?.title ?? '')],
      },
    },
    {
      name: 'status',
      type: 'select',
      required: true,
      defaultValue: 'draft',
      options: [
        { label: 'Draft',       value: 'draft' },
        { label: 'In Review',   value: 'in_review' },
        { label: 'Scheduled',   value: 'scheduled' },
        { label: 'Published',   value: 'published' },
        { label: 'Archived',    value: 'archived' },
      ],
      admin: { position: 'sidebar' },
      access: {
        // Only editors and admins can change status
        update: isEditor,
      },
    },
    {
      name: 'publishedAt',
      type: 'date',
      admin: {
        position: 'sidebar',
        date: { displayFormat: 'MMM d, yyyy h:mm a' },
        condition: (data) => data.status === 'published' || data.status === 'scheduled',
      },
    },
    {
      name: 'author',
      type: 'relationship',
      relationTo: 'users',
      required: true,
      admin: { position: 'sidebar' },
      access: {
        // Authors can't change their own author field
        update: isEditor,
      },
    },
    {
      name: 'categories',
      type: 'relationship',
      relationTo: 'categories',
      hasMany: true,
      admin: { position: 'sidebar' },
    },
    {
      name: 'tags',
      type: 'array',
      fields: [
        {
          name: 'tag',
          type: 'text',
        },
      ],
    },
    {
      name: 'excerpt',
      type: 'textarea',
      admin: { description: 'Short summary (150-300 chars). Used for SEO meta and previews.' },
    },
    {
      name: 'featuredImage',
      type: 'upload',
      relationTo: 'media',
    },
    {
      name: 'content',
      type: 'richText',
      required: true,
      // Uses Payload's Lexical editor by default
    },

    // SEO group
    {
      name: 'seo',
      type: 'group',
      admin: {
        description: 'Search engine optimization fields. Defaults to title and excerpt.',
      },
      fields: [
        { name: 'title',       type: 'text',     admin: { description: 'Overrides post title for <title> tag' } },
        { name: 'description', type: 'textarea', admin: { description: 'Overrides excerpt for <meta description>' } },
        { name: 'ogImage',     type: 'upload',   relationTo: 'media' },
      ],
    },

    // Computed/readonly fields
    {
      name: 'readingTimeMinutes',
      type: 'number',
      admin: { position: 'sidebar', readOnly: true },
    },
    {
      name: 'wordCount',
      type: 'number',
      admin: { readOnly: true },
    },
  ],
};
```

---

## Field Types Reference

```typescript
// All Payload field types and when to use them:

// Basic
{ type: 'text' }            // short string, one line
{ type: 'textarea' }        // multi-line text
{ type: 'number' }          // integer or float
{ type: 'checkbox' }        // boolean
{ type: 'date' }            // date/time picker
{ type: 'email' }           // validated email
{ type: 'code' }            // code with syntax highlighting
{ type: 'json' }            // raw JSON

// Choice
{ type: 'select', options: [...] }                // single select
{ type: 'select', hasMany: true, options: [...] } // multi-select
{ type: 'radio', options: [...] }                 // radio buttons

// Rich content
{ type: 'richText' }        // Lexical (v3) or Slate (v2) editor
{ type: 'upload', relationTo: 'media' }  // file/image upload

// Relational
{ type: 'relationship', relationTo: 'posts' }            // single relation
{ type: 'relationship', relationTo: 'posts', hasMany: true } // many relation
{ type: 'relationship', relationTo: ['posts', 'pages'] } // polymorphic

// Structural
{ type: 'group', fields: [...] }            // inline group of fields
{ type: 'array', fields: [...] }            // repeating group (like a table)
{ type: 'blocks', blocks: [...] }           // flexible content blocks (Gutenberg-style)
{ type: 'tabs', tabs: [{ label, fields }] } // tabbed layout in admin

// Special
{ type: 'point' }           // lat/lng coordinates
{ type: 'collapsible', fields: [...] }      // collapsible section in admin
{ type: 'row', fields: [...] }              // side-by-side fields in admin
{ type: 'ui' }              // custom React component in admin (display only)
```

---

## Access Control

```typescript
// access/roles.ts
import type { AccessArgs, FieldAccess } from 'payload';

type User = { id: string; role: 'admin' | 'editor' | 'author' | 'member' };

// Collection-level access functions
export const isAdmin = ({ req }: AccessArgs) =>
  req.user?.role === 'admin';

export const isEditor = ({ req }: AccessArgs) =>
  ['admin', 'editor'].includes(req.user?.role);

export const isAuthorOrEditor = ({ req }: AccessArgs) =>
  ['admin', 'editor', 'author'].includes(req.user?.role);

// Return a Payload access filter to read only your own content
export const isOwnContent = ({ req }: AccessArgs) => {
  if (!req.user) return false;
  if (['admin', 'editor'].includes(req.user.role)) return true;
  return { author: { equals: req.user.id } };
};

// Field-level access — hide sensitive fields from non-admins
export const adminOnly: FieldAccess = ({ req }) =>
  req.user?.role === 'admin';

// Example: hide the rejection_reason field from authors
{
  name: 'rejectionReason',
  type: 'textarea',
  access: {
    read:   adminOnly,
    update: adminOnly,
  },
}
```

---

## Hooks: beforeChange, afterChange, beforeRead

```typescript
// collections/hooks/post-hooks.ts
import type { CollectionBeforeChangeHook, CollectionAfterChangeHook } from 'payload';

// Set author on create (don't let API override it)
export const setAuthorOnCreate: CollectionBeforeChangeHook = ({ data, req, operation }) => {
  if (operation === 'create' && req.user) {
    return { ...data, author: req.user.id };
  }
  return data;
};

// Auto-generate slug from title
export const generateSlug: CollectionBeforeChangeHook = ({ data }) => {
  if (data.title && !data.slug) {
    return {
      ...data,
      slug: data.title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, ''),
    };
  }
  return data;
};

// Compute reading time and word count before save
export const computeReadingTime: CollectionBeforeChangeHook = ({ data }) => {
  if (data.content) {
    // Extract plain text from Lexical JSON
    const text = extractTextFromLexical(data.content);
    const wordCount = text.split(/\s+/).filter(Boolean).length;
    const readingTimeMinutes = Math.max(1, Math.ceil(wordCount / 200));
    return { ...data, wordCount, readingTimeMinutes };
  }
  return data;
};

// After publish: invalidate cache
export const invalidateCacheOnPublish: CollectionAfterChangeHook = async ({
  doc,
  previousDoc,
  req,
}) => {
  const justPublished =
    doc.status === 'published' && previousDoc?.status !== 'published';

  if (justPublished && doc.slug) {
    // Fire webhook to Next.js revalidation endpoint
    try {
      await fetch(`${process.env.FRONTEND_URL}/api/revalidate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-webhook-secret': process.env.REVALIDATION_SECRET!,
        },
        body: JSON.stringify({ slug: doc.slug, event: 'content.published' }),
      });
    } catch (err) {
      req.payload.logger.error(`Cache invalidation failed for ${doc.slug}: ${err}`);
    }
  }

  return doc;
};

// Prevent deletion of published posts
export const preventDeletingPublished: CollectionBeforeChangeHook = async ({
  req,
  id,
  collection,
}) => {
  const doc = await req.payload.findByID({ collection: 'posts', id });
  if (doc?.status === 'published' && req.user?.role !== 'admin') {
    throw new Error('Cannot delete a published post. Archive it first.');
  }
};

// Helper: extract text from Lexical JSON
function extractTextFromLexical(lexicalJson: object): string {
  const texts: string[] = [];
  function walk(node: { text?: string; children?: object[] }) {
    if (node.text) texts.push(node.text);
    if (node.children) node.children.forEach(child => walk(child as typeof node));
  }
  walk(lexicalJson as { children?: object[] });
  return texts.join(' ');
}
```

---

## Local API vs REST API vs GraphQL

```typescript
// Local API — use in Next.js server components, server actions, route handlers
// FASTEST: no HTTP round-trip, runs in same process
import { getPayload } from 'payload';
import config from '../payload.config';

const payload = await getPayload({ config });

// Find published posts
const { docs, totalDocs } = await payload.find({
  collection: 'posts',
  where: { status: { equals: 'published' } },
  sort: '-publishedAt',
  limit: 20,
  depth: 2,     // resolve relationships 2 levels deep
});

// Find by slug
const post = await payload.find({
  collection: 'posts',
  where: { slug: { equals: 'my-post-slug' } },
  limit: 1,
});

// Create a post
const newPost = await payload.create({
  collection: 'posts',
  data: {
    title: 'My Post',
    status: 'draft',
    author: userId,
  },
});

// Update a post
const updated = await payload.update({
  collection: 'posts',
  id: postId,
  data: { status: 'published', publishedAt: new Date() },
});

// Delete
await payload.delete({ collection: 'posts', id: postId });
```

```typescript
// REST API — use from external clients, mobile apps, or when you can't use Local API
// Base URL: /api (configured in payload.config.ts)

GET    /api/posts?where[status][equals]=published&sort=-publishedAt&limit=20
GET    /api/posts?where[slug][equals]=my-post-slug&depth=2
POST   /api/posts                    // create
PATCH  /api/posts/:id                // update
DELETE /api/posts/:id                // delete
POST   /api/users/login              // auth
POST   /api/users/logout
GET    /api/users/me

// GraphQL — use when clients need flexible queries
// Available at: /api/graphql
```

**Rule:** Use Local API for all server-side code in Next.js. Use REST API for external consumers, webhooks, and testing with curl. Use GraphQL only if you have a specific need for it (Payload's GraphQL is auto-generated from your collection config).

---

## Deploying to Vercel with PostgreSQL

```typescript
// Deployment checklist:

// 1. Environment variables needed:
// DATABASE_URL=postgresql://...
// PAYLOAD_SECRET=<random-64-char-string>
// NEXT_PUBLIC_SERVER_URL=https://yourdomain.com
// REVALIDATION_SECRET=<random-string>
// SMTP_* (if using email)

// 2. vercel.json — optional, for region pinning:
{
  "regions": ["iad1"],   // match your Supabase/Neon region
  "functions": {
    "app/api/**": { "maxDuration": 30 }
  }
}

// 3. next.config.ts — required for Payload v3:
import { withPayload } from '@payloadcms/next/withPayload';

const nextConfig = {
  // your config
};

export default withPayload(nextConfig);

// 4. Database migrations:
// payload migrate:create   -- create a new migration
// payload migrate          -- run pending migrations
// payload migrate:status   -- check migration status

// In production (Vercel), add to build command:
// "build": "payload migrate && next build"
```

---

## Payload vs Strapi vs Directus: Decision Guide

```
Need TypeScript-first config (everything is code)?
  → Payload

Need mature plugin ecosystem (25,000+ GitHub stars, 200+ plugins)?
  → Strapi

Wrapping an existing database (want DB to stay the authority)?
  → Directus (it introspects your DB and builds the API around it)

Need to embed CMS directly inside Next.js app (same deployment)?
  → Payload (v3 is the ONLY major headless CMS that does this)

Team prefers GUI-based config over code?
  → Directus (fully GUI) or Strapi (GUI + code)

Need commercial support / enterprise SLA?
  → Strapi Enterprise or Directus Enterprise

Want to get started in 5 minutes with minimal config?
  → Strapi (more scaffolding, more generators)
```

---

## Migrating from Strapi to Payload: Schema Translation

```
Strapi concept → Payload equivalent

Content Type → Collection
Single Type  → Global
Component    → Array or Group field
Dynamic Zone → Blocks field
Relation     → Relationship field
Media        → Upload field (with Media collection)
Plugin       → Custom collection + hooks + endpoints
Lifecycle hooks (beforeCreate, afterUpdate) → beforeChange, afterChange hooks
Policies     → Access control functions
Routes       → Payload custom endpoints or Next.js API routes
```

```typescript
// Strapi lifecycle hook:
module.exports = {
  async beforeCreate(event) {
    event.params.data.slug = slugify(event.params.data.title);
  },
};

// Payload equivalent:
export const Posts: CollectionConfig = {
  hooks: {
    beforeChange: [
      ({ data }) => ({ ...data, slug: data.slug ?? slugify(data.title ?? '') }),
    ],
  },
};
```

---

## Lexical Rich Text Output Rendering in React

```tsx
// Payload v3 uses Lexical editor. To render in your frontend:

// Option 1: Use Payload's built-in React renderer
import { RichText } from '@payloadcms/richtext-lexical/react';

function PostContent({ content }: { content: object }) {
  return (
    <div className="prose prose-slate max-w-none">
      <RichText content={content} />
    </div>
  );
}

// Option 2: Generate HTML server-side (for email, RSS, etc.)
import { convertLexicalToHTML } from '@payloadcms/richtext-lexical/html';

const html = await convertLexicalToHTML({
  converters: defaultHTMLConverters,
  data: post.content,
});

// Option 3: For Next.js App Router (RSC-safe)
// Payload's RichText component works in server components in v3
```

---

## Common Gotchas

1. **`payload.config.ts` is NOT a regular module** — it's read at build time by Next.js. Don't import from it in client components. Always use the Local API in server components.
2. **`depth` parameter is expensive** — `depth: 2` resolves relationships 2 levels deep. For each level, Payload runs additional queries. Use only the depth you need.
3. **Migrations are required for PostgreSQL** — unlike MongoDB, schema changes require running `payload migrate`. Always run migrations before deploying schema changes.
4. **Admin UI at `/admin` conflicts with your own routes** — if you have an `/admin` route in your Next.js app, configure Payload's admin to use a different path: `admin: { buildPath: '/cms' }`.
5. **Generated types drift if you forget to regenerate** — run `npm run generate:types` after every collection schema change. Add it to your `prebuild` script to automate.
6. **Local API bypasses access control by default** — when using `payload.find()` server-side, pass `overrideAccess: false` if you need access control enforced. Default is `overrideAccess: true` (admin-level access).
