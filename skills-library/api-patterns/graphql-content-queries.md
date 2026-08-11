# GraphQL Content Queries

> Production GraphQL patterns for content platforms: schema design, N+1 prevention with DataLoader, cursor pagination, mutations, and Apollo Client setup.

**When to use:** Building a content API where different consumers (web, mobile, third-party) need different shapes of the same data, or when content is deeply relational (posts → authors → categories → related posts).
**Stack:** Node.js/Express, graphql-yoga or Apollo Server, DataLoader, PostgreSQL, Apollo Client (React)

---

## Schema: Content Types

```graphql
# schema.graphql

scalar DateTime
scalar JSON    # for TipTap's body_json

type Post {
  id:             ID!
  title:          String!
  slug:           String!
  excerpt:        String
  bodyHtml:       String
  bodyJson:       JSON
  featuredImage:  MediaAsset
  status:         PostStatus!
  publishedAt:    DateTime
  scheduledAt:    DateTime
  readingTimeMinutes: Int
  wordCount:      Int
  tags:           [String!]!

  # Relationships — these trigger DataLoader
  author:         Author!
  categories:     [Category!]!
  relatedPosts:   [Post!]!
}

type Author {
  id:       ID!
  name:     String!
  email:    String!
  bio:      String
  avatar:   String
  posts(first: Int, after: String): PostConnection!
}

type Category {
  id:       ID!
  name:     String!
  slug:     String!
  posts(first: Int, after: String, status: PostStatus): PostConnection!
}

type MediaAsset {
  url:     String!
  alt:     String
  width:   Int
  height:  Int
  mimeType: String
}

enum PostStatus {
  DRAFT
  IN_REVIEW
  SCHEDULED
  PUBLISHED
  ARCHIVED
}

# Cursor-based pagination (Relay spec)
type PostConnection {
  edges:    [PostEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PostEdge {
  node:   Post!
  cursor: String!
}

type PageInfo {
  hasNextPage:     Boolean!
  hasPreviousPage: Boolean!
  startCursor:     String
  endCursor:       String
}
```

---

## Query Schema

```graphql
type Query {
  # Single post
  post(slug: String!): Post
  postById(id: ID!): Post

  # List posts
  posts(
    first:    Int = 20
    after:    String
    last:     Int
    before:   String
    filter:   PostFilter
    orderBy:  PostOrderBy
  ): PostConnection!

  # Search
  searchPosts(query: String!, first: Int = 20, after: String): PostConnection!

  # Authors
  author(id: ID!): Author
  authors(first: Int = 20, after: String): AuthorConnection!

  # Categories
  category(slug: String!): Category
  categories: [Category!]!
}

input PostFilter {
  status:     PostStatus
  categoryId: ID
  tag:        String
  authorId:   ID
  publishedAfter:  DateTime
  publishedBefore: DateTime
}

enum PostOrderBy {
  PUBLISHED_AT_DESC
  PUBLISHED_AT_ASC
  TITLE_ASC
  CREATED_AT_DESC
}
```

---

## Mutation Schema

```graphql
type Mutation {
  createPost(input: CreatePostInput!): PostMutationResult!
  updatePost(id: ID!, input: UpdatePostInput!): PostMutationResult!
  publishPost(id: ID!): PostMutationResult!
  schedulePost(id: ID!, scheduledAt: DateTime!): PostMutationResult!
  archivePost(id: ID!): PostMutationResult!
  deletePost(id: ID!): DeleteResult!
}

input CreatePostInput {
  title:      String!
  slug:       String
  excerpt:    String
  bodyJson:   JSON
  tags:       [String!]
  categoryIds: [ID!]
  featuredImageId: ID
}

input UpdatePostInput {
  title:      String
  slug:       String
  excerpt:    String
  bodyJson:   JSON
  tags:       [String!]
  categoryIds: [ID!]
}

# GraphQL errors live in the result type, not HTTP status codes
type PostMutationResult {
  post:   Post
  errors: [UserError!]
}

type DeleteResult {
  id:      ID
  errors:  [UserError!]
}

type UserError {
  field:   String
  message: String!
  code:    String
}
```

---

## Resolvers with DataLoader (N+1 Prevention)

### The N+1 Problem

```graphql
# This query looks innocent but causes 1 + N DB queries without DataLoader:
query {
  posts(first: 20) {
    edges {
      node {
        title
        author {     # This fires a SELECT for EACH of the 20 posts = 21 queries total
          name
        }
      }
    }
  }
}
```

### DataLoader Solution

```typescript
// lib/data-loaders.ts
import DataLoader from 'dataloader';  // npm install dataloader
import { Pool } from 'pg';

export function createLoaders(db: Pool) {
  return {
    // Batch-load authors by ID — fires ONE query for all unique author IDs
    authorLoader: new DataLoader<string, Author>(async (authorIds) => {
      const { rows } = await db.query(
        'SELECT * FROM users WHERE id = ANY($1::uuid[])',
        [authorIds]
      );
      // DataLoader requires results in the same order as the input keys
      const authorMap = new Map(rows.map(r => [r.id, r]));
      return authorIds.map(id => authorMap.get(id) ?? new Error(`Author not found: ${id}`));
    }),

    // Batch-load categories by post ID
    postCategoriesLoader: new DataLoader<string, Category[]>(async (postIds) => {
      const { rows } = await db.query(`
        SELECT pc.post_id, c.id, c.name, c.slug
        FROM post_categories pc
          JOIN categories c ON c.id = pc.category_id
        WHERE pc.post_id = ANY($1::uuid[])
        ORDER BY c.name
      `, [postIds]);

      // Group categories by post_id
      const categoryMap = new Map<string, Category[]>();
      postIds.forEach(id => categoryMap.set(id, []));
      rows.forEach(row => {
        categoryMap.get(row.post_id)?.push({ id: row.id, name: row.name, slug: row.slug });
      });
      return postIds.map(id => categoryMap.get(id) ?? []);
    }),

    // Batch-load related posts (last 3 posts in same category)
    // Uses ROW_NUMBER() OVER PARTITION to get top 3 per base post — not a
    // global LIMIT which would return at most 3 rows total across all posts.
    relatedPostsLoader: new DataLoader<string, Post[]>(async (postIds) => {
      const { rows } = await db.query(`
        SELECT base_post_id, id, title, slug, excerpt, published_at, reading_time_minutes
        FROM (
          SELECT
            base.id AS base_post_id,
            p.id, p.title, p.slug, p.excerpt, p.published_at, p.reading_time_minutes,
            ROW_NUMBER() OVER (PARTITION BY base.id ORDER BY p.published_at DESC) AS rn
          FROM content base
            JOIN post_categories pc_base ON pc_base.post_id = base.id
            JOIN post_categories pc ON pc.category_id = pc_base.category_id AND pc.post_id != base.id
            JOIN content p ON p.id = pc.post_id
          WHERE base.id = ANY($1::uuid[])
            AND p.status = 'published'
        ) ranked
        WHERE rn <= 3
        ORDER BY base_post_id, published_at DESC
      `, [postIds]);

      const relatedMap = new Map<string, Post[]>();
      postIds.forEach(id => relatedMap.set(id, []));
      rows.forEach(row => {
        const list = relatedMap.get(row.base_post_id) ?? [];
        if (list.length < 3) {
          list.push(row);
          relatedMap.set(row.base_post_id, list);
        }
      });
      return postIds.map(id => relatedMap.get(id) ?? []);
    }),
  };
}

export type Loaders = ReturnType<typeof createLoaders>;
```

### Resolver Implementation

```typescript
// resolvers/post-resolvers.ts
import { buildCursor, parseCursor, applyPagination } from '../lib/pagination';

export const postResolvers = {
  Query: {
    post: async (_: unknown, { slug }: { slug: string }, { db }) => {
      const { rows } = await db.query(
        'SELECT * FROM content WHERE slug = $1 AND status = $2',
        [slug, 'published']
      );
      return rows[0] ?? null;
    },

    posts: async (_: unknown, args: PostsArgs, { db }) => {
      const { first = 20, after, filter = {}, orderBy = 'PUBLISHED_AT_DESC' } = args;

      const conditions: string[] = ["c.status = 'published'"];
      const params: unknown[] = [];
      let paramIdx = 1;

      if (filter.categoryId) {
        conditions.push(`EXISTS (
          SELECT 1 FROM post_categories pc
          WHERE pc.post_id = c.id AND pc.category_id = $${paramIdx++}
        )`);
        params.push(filter.categoryId);
      }

      if (filter.tag) {
        conditions.push(`$${paramIdx++} = ANY(c.tags)`);
        params.push(filter.tag);
      }

      // Cursor pagination
      if (after) {
        const cursor = parseCursor(after);
        conditions.push(`(c.published_at, c.id) < ($${paramIdx++}, $${paramIdx++})`);
        params.push(cursor.publishedAt, cursor.id);
      }

      const orderClause = {
        PUBLISHED_AT_DESC: 'c.published_at DESC, c.id DESC',
        PUBLISHED_AT_ASC:  'c.published_at ASC, c.id ASC',
        TITLE_ASC:         'c.title ASC, c.id ASC',
        CREATED_AT_DESC:   'c.created_at DESC, c.id DESC',
      }[orderBy];

      params.push(first + 1);   // fetch one extra to check hasNextPage

      const { rows } = await db.query(`
        SELECT c.*, COUNT(*) OVER() AS total_count
        FROM content c
        WHERE ${conditions.join(' AND ')}
        ORDER BY ${orderClause}
        LIMIT $${paramIdx}
      `, params);

      const hasNextPage = rows.length > first;
      const edges = rows.slice(0, first).map(row => ({
        node: row,
        cursor: buildCursor({ publishedAt: row.published_at, id: row.id }),
      }));

      return {
        edges,
        totalCount: rows[0]?.total_count ? parseInt(rows[0].total_count, 10) : 0,
        pageInfo: {
          hasNextPage,
          hasPreviousPage: !!after,
          startCursor: edges[0]?.cursor ?? null,
          endCursor: edges[edges.length - 1]?.cursor ?? null,
        },
      };
    },

    searchPosts: async (_: unknown, { query, first = 20, after }: SearchArgs, { db }) => {
      const { rows } = await db.query(`
        SELECT *, ts_rank(search_vector, q) AS rank, COUNT(*) OVER() AS total_count
        FROM content, websearch_to_tsquery('english', $1) AS q
        WHERE status = 'published' AND search_vector @@ q
        ORDER BY rank DESC, published_at DESC
        LIMIT $2
      `, [query, first + 1]);

      const hasNextPage = rows.length > first;
      const edges = rows.slice(0, first).map(row => ({
        node: row,
        cursor: buildCursor({ rank: row.rank, id: row.id }),
      }));

      return {
        edges,
        totalCount: rows[0]?.total_count ? parseInt(rows[0].total_count, 10) : 0,
        pageInfo: {
          hasNextPage,
          hasPreviousPage: false,   // search doesn't support backwards pagination
          startCursor: edges[0]?.cursor ?? null,
          endCursor: edges[edges.length - 1]?.cursor ?? null,
        },
      };
    },
  },

  // Field resolvers — these use DataLoader for batching
  Post: {
    author: (post: Post, _: unknown, { loaders }: { loaders: Loaders }) =>
      loaders.authorLoader.load(post.author_id),

    categories: (post: Post, _: unknown, { loaders }: { loaders: Loaders }) =>
      loaders.postCategoriesLoader.load(post.id),

    relatedPosts: (post: Post, _: unknown, { loaders }: { loaders: Loaders }) =>
      loaders.relatedPostsLoader.load(post.id),

    // Computed fields
    bodyHtml: (post: Post) => post.body_html ?? '',
    bodyJson: (post: Post) => post.body_json ?? null,
  },

  // Mutations
  Mutation: {
    publishPost: async (_: unknown, { id }: { id: string }, { db, user }) => {
      if (!user) return { post: null, errors: [{ message: 'Unauthorized', code: 'UNAUTHORIZED' }] };

      const { rows } = await db.query(
        'UPDATE content SET status = $1, published_at = NOW() WHERE id = $2 AND status = $3 RETURNING *',
        ['published', id, 'in_review']
      );

      if (!rows[0]) {
        return { post: null, errors: [{ message: 'Post not found or not in review', code: 'NOT_FOUND' }] };
      }

      return { post: rows[0], errors: [] };
    },
  },
};
```

---

## Cursor-Based Pagination Utilities

```typescript
// lib/pagination.ts

interface CursorData {
  [key: string]: string | number | Date;
}

// Cursors are base64-encoded JSON — opaque to clients
export function buildCursor(data: CursorData): string {
  return Buffer.from(JSON.stringify(data)).toString('base64url');
}

export function parseCursor(cursor: string): CursorData {
  try {
    return JSON.parse(Buffer.from(cursor, 'base64url').toString('utf-8'));
  } catch {
    throw new Error('Invalid cursor');
  }
}
```

---

## Error Handling in GraphQL

**CRITICAL: Do NOT throw HTTP errors in GraphQL resolvers.** Return errors in the result type.

```typescript
// Wrong:
throw new Error('Unauthorized');    // This returns a 200 with an error in the "errors" array (GraphQL spec)
                                    // but breaks client error handling

// Correct pattern: UserError in the result type
return {
  post: null,
  errors: [
    {
      field: 'id',
      message: 'Post not found',
      code: 'NOT_FOUND',
    }
  ]
};

// For unrecoverable/unexpected errors, throwing IS correct:
// (GraphQL will catch it and put it in the top-level "errors" array)
throw new Error('Database connection failed');  // OK for internal errors
```

---

## Caching: GET Requests for CDN Cacheability

```typescript
// GraphQL over GET (persisted queries) — CDN-cacheable
// Client sends query hash, server returns response

// Apollo Server: Automatic Persisted Queries (APQ)
import { ApolloServer } from '@apollo/server';
import { createPersistedQueryLink } from '@apollo/client/link/persisted-queries';
import { generatePersistedQueryIdsFromOperation } from '@apollo/generate-persisted-query-manifest';

// This converts POST /graphql to GET /graphql?extensions={"persistedQuery":{...}}
// CDNs can cache GET requests — POST requests are never cached

// Client setup:
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { createPersistedQueryLink } from '@apollo/client/link/persisted-queries';
import { sha256 } from 'crypto-hash';

const persistedQueriesLink = createPersistedQueryLink({ sha256 });
const httpLink = createHttpLink({ uri: '/api/graphql', useGETForQueries: true });

export const apolloClient = new ApolloClient({
  link: persistedQueriesLink.concat(httpLink),
  cache: new InMemoryCache({
    typePolicies: {
      Post: { keyFields: ['id'] },
      PostConnection: {
        keyArgs: ['filter', 'orderBy'],
        merge(existing, incoming, { args }) {
          const existingEdges = existing?.edges ?? [];
          const incomingEdges = incoming.edges ?? [];
          return {
            ...incoming,
            edges: args?.after ? [...existingEdges, ...incomingEdges] : incomingEdges,
          };
        },
      },
    },
  }),
});
```

---

## Apollo Client React Setup

```tsx
// lib/apollo-provider.tsx
'use client';
import { ApolloProvider } from '@apollo/client';
import { apolloClient } from './apollo-client';

export function ApolloClientProvider({ children }: { children: React.ReactNode }) {
  return <ApolloProvider client={apolloClient}>{children}</ApolloProvider>;
}

// hooks/usePosts.ts
import { useQuery, gql } from '@apollo/client';

const POST_LIST_FRAGMENT = gql`
  fragment PostListItem on Post {
    id
    title
    slug
    excerpt
    publishedAt
    readingTimeMinutes
    author {
      id
      name
      avatar
    }
    categories {
      id
      name
      slug
    }
    tags
  }
`;

const GET_POSTS = gql`
  ${POST_LIST_FRAGMENT}
  query GetPosts($first: Int, $after: String, $filter: PostFilter) {
    posts(first: $first, after: $after, filter: $filter) {
      edges {
        node { ...PostListItem }
        cursor
      }
      pageInfo {
        hasNextPage
        endCursor
      }
      totalCount
    }
  }
`;

export function usePosts(filter?: PostFilter) {
  const { data, loading, error, fetchMore } = useQuery(GET_POSTS, {
    variables: { first: 20, filter },
  });

  const loadMore = () => {
    const { endCursor, hasNextPage } = data?.posts.pageInfo ?? {};
    if (!hasNextPage) return;

    fetchMore({
      variables: { after: endCursor },
      updateQuery: (prev, { fetchMoreResult }) => {
        if (!fetchMoreResult) return prev;
        return {
          posts: {
            ...fetchMoreResult.posts,
            edges: [...prev.posts.edges, ...fetchMoreResult.posts.edges],
          },
        };
      },
    });
  };

  return {
    posts: data?.posts.edges.map(e => e.node) ?? [],
    totalCount: data?.posts.totalCount ?? 0,
    hasNextPage: data?.posts.pageInfo.hasNextPage ?? false,
    loading,
    error,
    loadMore,
  };
}
```

---

## Fragment Reuse

```graphql
# Consistent content shapes across queries — no divergence between list and detail views
fragment PostCard on Post {
  id
  title
  slug
  excerpt
  publishedAt
  readingTimeMinutes
  featuredImage { url alt width height }
  author { id name avatar }
  tags
}

fragment PostDetail on Post {
  ...PostCard
  bodyHtml
  categories { id name slug }
  relatedPosts { ...PostCard }
}

query GetPost($slug: String!) {
  post(slug: $slug) {
    ...PostDetail
  }
}
```

---

## Code-First vs SDL-First

| Approach | Tools | When to use |
|----------|-------|-------------|
| SDL-first | `graphql-tag`, `graphql-tools` | Schema is the contract, multiple implementations |
| Code-first | `nexus`, `pothos`, `type-graphql` | TypeScript-first, single implementation, want type safety |

**Code-first with Pothos (recommended for TypeScript projects):**

```typescript
// schema.ts
import SchemaBuilder from '@pothos/core';

const builder = new SchemaBuilder<{ Context: AppContext }>({});

builder.queryType({
  fields: (t) => ({
    post: t.field({
      type: PostRef,
      nullable: true,
      args: { slug: t.arg.string({ required: true }) },
      resolve: async (_, { slug }, { db }) => {
        const { rows } = await db.query('SELECT * FROM content WHERE slug = $1', [slug]);
        return rows[0] ?? null;
      },
    }),
  }),
});

const PostRef = builder.objectRef<Post>('Post').implement({
  fields: (t) => ({
    id:    t.exposeID('id'),
    title: t.exposeString('title'),
    slug:  t.exposeString('slug'),
    author: t.field({
      type: AuthorRef,
      resolve: (post, _, { loaders }) => loaders.authorLoader.load(post.author_id),
    }),
  }),
});

export const schema = builder.toSchema();
```

---

## Common Gotchas

1. **N+1 is silent** — it won't error, it just makes your server slow. Always use DataLoader for any field resolver that makes a DB query. Log query counts in development to catch N+1 early.
2. **DataLoader caches per request, not globally** — create a new DataLoader instance per GraphQL request (in the context factory), not once at startup. Otherwise data leaks between requests.
3. **`errors` array ≠ HTTP error** — GraphQL always returns 200 OK. Even completely failed operations return 200 with `{"errors": [...]}`. Your API gateway or client must check the `errors` array, not the HTTP status.
4. **Don't expose internal error messages** — use a custom `formatError` function to sanitize errors before they reach the client. Log the original, return a generic message.
5. **File uploads require multipart** — GraphQL doesn't natively support file uploads. Use `graphql-upload` or handle uploads as REST endpoints and pass URLs to GraphQL.
6. **Mutations should return the mutated object** — always return the full post/entity in mutation results so clients can update their Apollo cache without a separate refetch.
