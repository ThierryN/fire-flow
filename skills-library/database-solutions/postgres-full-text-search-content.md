# PostgreSQL Full-Text Search for Content Platforms

> Production-ready FTS using PostgreSQL's built-in tsvector/tsquery — no Elasticsearch required.

**When to use:** Building search for blogs, knowledge bases, docs, LMS, or any content-heavy app where you want relevance ranking without external infrastructure.
**Stack:** PostgreSQL 14+, Node.js/Express or Bun, TypeScript

---

## Why PostgreSQL FTS First

Before reaching for Elasticsearch or Typesense, ask:
- Fewer than ~1 million documents? → PG FTS handles it fine.
- Already using PostgreSQL? → Zero new infrastructure.
- Need relevance ranking, phrase search, prefix matching? → All built in.
- Need faceting, synonyms, ML-powered re-ranking? → Then add a search engine.

Rule of thumb: **PG FTS is production-ready up to ~1M rows** with proper GIN indexing. At 5M+ rows with complex relevance needs, evaluate Typesense or Elasticsearch.

---

## Core Concepts

| Concept | What it is |
|---------|-----------|
| `tsvector` | Preprocessed document representation (stemmed, stop-words removed) |
| `tsquery` | Search query in tsvector-compatible form |
| `GIN index` | Generalized Inverted Index — makes FTS fast at scale |
| `ts_rank` | Relevance score function (0.0–1.0) |
| `setweight` | Assigns A/B/C/D weight to parts of a document |
| `to_tsvector` | Converts text to tsvector |
| `to_tsquery` | Converts user input to tsquery (exact phrase match) |
| `plainto_tsquery` | Converts plain text (AND behavior, no operators needed) |
| `websearch_to_tsquery` | Converts Google-style queries (quotes, minus, OR) |

---

## Schema: Content Table with FTS

```sql
-- Content table with FTS support
CREATE TABLE content (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title       TEXT NOT NULL,
  body        TEXT NOT NULL,
  excerpt     TEXT,
  tags        TEXT[],                    -- array of tag strings
  author_id   UUID REFERENCES users(id),
  status      TEXT NOT NULL DEFAULT 'draft',
  published_at TIMESTAMPTZ,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Weighted search vector: stored, updated by trigger
  search_vector TSVECTOR GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(title, '')),   'A') ||
    setweight(to_tsvector('english', coalesce(excerpt, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(body, '')),    'C') ||
    setweight(to_tsvector('english', coalesce(array_to_string(tags, ' '), '')), 'B')
  ) STORED
);

-- GIN index on the stored vector — this is what makes it fast
CREATE INDEX idx_content_search_vector ON content USING GIN(search_vector);

-- Index for common filter combos
CREATE INDEX idx_content_status_published ON content(status, published_at DESC);
CREATE INDEX idx_content_author ON content(author_id);
```

### Why GENERATED ALWAYS AS STORED?

PostgreSQL 12+ supports stored generated columns. The `search_vector` column is automatically recomputed on every INSERT/UPDATE. No trigger needed. This is the cleanest approach — one source of truth, no sync lag.

**Alternative: Trigger-based (for older PG or more control)**

```sql
-- If you need PG 11 or want trigger-based updates:
ALTER TABLE content ADD COLUMN search_vector TSVECTOR;

CREATE OR REPLACE FUNCTION content_search_vector_update()
RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', coalesce(NEW.title, '')),   'A') ||
    setweight(to_tsvector('english', coalesce(NEW.excerpt, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(NEW.body, '')),    'C') ||
    setweight(to_tsvector('english', coalesce(array_to_string(NEW.tags, ' '), '')), 'B');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER content_search_vector_trigger
BEFORE INSERT OR UPDATE ON content
FOR EACH ROW EXECUTE FUNCTION content_search_vector_update();

-- Backfill existing rows after adding trigger
UPDATE content SET updated_at = updated_at;
```

---

## Weight Strategy: A > B > C > D

```
Weight A — Title (highest relevance)
Weight B — Excerpt, Tags
Weight C — Body (lowest, largest volume)
Weight D — (available for metadata, rarely used)
```

`ts_rank` uses these weights when computing relevance scores. A document where the query matches the title ranks higher than one where it only matches the body.

---

## Query Patterns

### 1. Simple Search (AND behavior)

```sql
-- All words must appear somewhere in the document
SELECT
  id,
  title,
  published_at,
  ts_rank(search_vector, query) AS rank
FROM content,
  plainto_tsquery('english', 'postgresql performance') AS query
WHERE
  status = 'published'
  AND search_vector @@ query
ORDER BY rank DESC, published_at DESC
LIMIT 20;
```

`plainto_tsquery` treats the input as "postgresql AND performance" — no operators needed from the user.

### 2. Phrase Search (exact phrase)

```sql
-- Words must appear together in order
SELECT id, title, ts_rank(search_vector, query) AS rank
FROM content,
  phraseto_tsquery('english', 'database index') AS query
WHERE status = 'published'
  AND search_vector @@ query
ORDER BY rank DESC;
```

### 3. Prefix Search (autocomplete / partial words)

```sql
-- Match words beginning with a prefix (great for autocomplete)
SELECT id, title, ts_rank(search_vector, query) AS rank
FROM content,
  to_tsquery('english', 'postgr:*') AS query   -- matches postgresql, postgres, etc.
WHERE status = 'published'
  AND search_vector @@ query
ORDER BY rank DESC
LIMIT 10;
```

### 4. Google-Style Input (quotes, minus, OR)

```sql
-- Accepts: "exact phrase" postgres -mysql OR nosql
SELECT id, title, ts_rank(search_vector, query) AS rank
FROM content,
  websearch_to_tsquery('english', $1) AS query
WHERE status = 'published'
  AND search_vector @@ query
ORDER BY rank DESC;
```

`websearch_to_tsquery` is the right choice for user-facing search boxes. It handles:
- `"exact phrase"` → phrase search
- `-word` → exclude word
- `word1 OR word2` → either word
- Everything else → AND

### 5. Combined FTS + Regular Filters

```sql
-- Search within a specific author's published posts, after a date
SELECT
  c.id,
  c.title,
  c.published_at,
  c.tags,
  u.name AS author_name,
  ts_rank(c.search_vector, query) AS rank
FROM content c
  JOIN users u ON u.id = c.author_id,
  websearch_to_tsquery('english', $1) AS query
WHERE
  c.status = 'published'
  AND c.author_id = $2
  AND c.published_at >= $3
  AND c.search_vector @@ query
ORDER BY rank DESC, c.published_at DESC
LIMIT $4 OFFSET $5;
```

### 6. Search with Snippet Highlighting

```sql
-- Return highlighted excerpts showing matched terms in context
SELECT
  id,
  title,
  ts_headline(
    'english',
    body,
    query,
    'MaxWords=50, MinWords=15, ShortWord=3, HighlightAll=false,
     MaxFragments=3, FragmentDelimiter='' ... '''
  ) AS headline,
  ts_rank(search_vector, query) AS rank
FROM content,
  websearch_to_tsquery('english', $1) AS query
WHERE status = 'published'
  AND search_vector @@ query
ORDER BY rank DESC
LIMIT 20;
```

`ts_headline` is expensive — only use it on the final result set (after LIMIT), never in a WHERE clause or subquery.

---

## Node.js / Express Query Helper

```typescript
// lib/content-search.ts
import { Pool } from 'pg';

interface SearchOptions {
  query: string;
  authorId?: string;
  tags?: string[];
  status?: string;
  limit?: number;
  offset?: number;
  highlight?: boolean;
}

interface SearchResult {
  id: string;
  title: string;
  excerpt: string | null;
  tags: string[];
  published_at: string | null;
  author_name: string;
  rank: number;
  headline?: string;
}

export async function searchContent(
  db: Pool,
  options: SearchOptions
): Promise<{ results: SearchResult[]; total: number }> {
  const {
    query,
    authorId,
    tags,
    status = 'published',
    limit = 20,
    offset = 0,
    highlight = false,
  } = options;

  if (!query || query.trim().length < 2) {
    return { results: [], total: 0 };
  }

  const params: unknown[] = [query, status, limit, offset];
  let paramIndex = 5;

  const authorFilter = authorId
    ? `AND c.author_id = $${paramIndex++}`
    : '';
  if (authorId) params.push(authorId);

  const tagsFilter = tags && tags.length > 0
    ? `AND c.tags && $${paramIndex++}::text[]`
    : '';
  if (tags && tags.length > 0) params.push(tags);

  const headlineSelect = highlight
    ? `, ts_headline('english', c.body, query,
        'MaxWords=40, MinWords=10, MaxFragments=2, FragmentDelimiter='' ... '''
      ) AS headline`
    : '';

  const sql = `
    SELECT
      c.id,
      c.title,
      c.excerpt,
      c.tags,
      c.published_at,
      u.name AS author_name,
      ts_rank(c.search_vector, query) AS rank
      ${headlineSelect},
      COUNT(*) OVER() AS total_count
    FROM content c
      JOIN users u ON u.id = c.author_id,
      websearch_to_tsquery('english', $1) AS query
    WHERE
      c.status = $2
      AND c.search_vector @@ query
      ${authorFilter}
      ${tagsFilter}
    ORDER BY rank DESC, c.published_at DESC NULLS LAST
    LIMIT $3 OFFSET $4
  `;

  const { rows } = await db.query(sql, params);

  const total = rows.length > 0 ? parseInt(rows[0].total_count, 10) : 0;
  const results = rows.map(({ total_count, ...rest }) => rest);

  return { results, total };
}
```

**Express route using the helper:**

```typescript
// routes/content.ts
router.get('/content/search', async (req, res) => {
  const { q, author, tags, page = '1', limit = '20' } = req.query as Record<string, string>;

  if (!q) return res.status(400).json({ error: 'q parameter required' });

  const pageNum = Math.max(1, parseInt(page, 10));
  const limitNum = Math.min(100, Math.max(1, parseInt(limit, 10)));

  try {
    const { results, total } = await searchContent(db, {
      query: q,
      authorId: author,
      tags: tags ? tags.split(',') : undefined,
      limit: limitNum,
      offset: (pageNum - 1) * limitNum,
      highlight: true,
    });

    res.json({
      results,
      pagination: {
        total,
        page: pageNum,
        limit: limitNum,
        pages: Math.ceil(total / limitNum),
      },
    });
  } catch (err) {
    console.error('Search error:', err);
    res.status(500).json({ error: 'Search failed' });
  }
});
```

---

## Hybrid: FTS Relevance + Recency Boost

Pure `ts_rank` ignores recency. For content platforms, blend rank with freshness:

```sql
SELECT
  id,
  title,
  published_at,
  ts_rank(search_vector, query) AS text_rank,
  -- Recency score: 1.0 for today, decays exponentially
  EXP(-EXTRACT(EPOCH FROM (NOW() - published_at)) / (86400 * 30)) AS recency_score,
  -- Blended score: 70% text relevance, 30% recency
  (0.7 * ts_rank(search_vector, query) +
   0.3 * EXP(-EXTRACT(EPOCH FROM (NOW() - published_at)) / (86400 * 30))
  ) AS blended_score
FROM content,
  websearch_to_tsquery('english', $1) AS query
WHERE status = 'published'
  AND search_vector @@ query
ORDER BY blended_score DESC
LIMIT 20;
```

Tune the `86400 * 30` (30-day half-life) to match your freshness requirements.

---

## Pagination with Search

Never use `OFFSET` for deep pagination on large datasets — it degrades linearly. Use cursor-based pagination after the first page:

```sql
-- Page 1 (always):
SELECT id, title, ts_rank(search_vector, query) AS rank, published_at
FROM content, websearch_to_tsquery('english', $1) AS query
WHERE status = 'published' AND search_vector @@ query
ORDER BY rank DESC, id DESC   -- id as tiebreaker for stable cursor
LIMIT 20;

-- Subsequent pages (cursor = { rank, id } from last item):
SELECT id, title, ts_rank(search_vector, query) AS rank, published_at
FROM content, websearch_to_tsquery('english', $1) AS query
WHERE status = 'published'
  AND search_vector @@ query
  AND (ts_rank(search_vector, query), id) < ($2, $3)  -- cursor
ORDER BY rank DESC, id DESC
LIMIT 20;
```

---

## Performance Notes

| Scenario | Performance |
|----------|-------------|
| 10K rows, no index | ~50ms |
| 100K rows, GIN index | ~5-15ms |
| 1M rows, GIN index | ~20-80ms |
| 10M rows, GIN index | ~200-500ms (consider partitioning or external search) |

**Index maintenance:** GIN indexes are slower to update than B-tree. On write-heavy tables (>1K updates/sec), consider `fastupdate = off` or a separate search indexing worker.

```sql
-- Disable fastupdate if you see GIN pending list slowdowns
CREATE INDEX idx_content_search_vector ON content USING GIN(search_vector)
WITH (fastupdate = off);
```

---

## FTS vs External Search Engine Decision Guide

| Need | PG FTS | Typesense | Elasticsearch |
|------|--------|-----------|---------------|
| < 1M docs | Yes | Overkill | Overkill |
| 1M–10M docs | Maybe | Yes | Yes |
| Typo tolerance (fuzzy) | No | Yes | Yes |
| Synonym expansion | Limited | Yes | Yes |
| Faceted filters | No | Yes | Yes |
| ML re-ranking | No | Yes | Yes |
| Zero extra infra | Yes | No | No |
| Already in PG stack | Yes | No | No |
| Real-time updates | Yes | Yes | Slower |

**Decision rule:** Start with PG FTS. Add Typesense when you hit one of: typo tolerance needed, faceted search UI, >2M documents with sub-50ms P95 requirement.

---

## Migrations

```sql
-- Migration: add FTS to existing content table
BEGIN;

-- Add the search vector column if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'content' AND column_name = 'search_vector'
  ) THEN
    ALTER TABLE content ADD COLUMN search_vector TSVECTOR
      GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(excerpt, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(body, '')), 'C')
      ) STORED;
  END IF;
END $$;

-- Create GIN index (CONCURRENTLY to avoid locking production)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_search_vector
  ON content USING GIN(search_vector);

COMMIT;
```

---

## Common Gotchas

1. **`to_tsquery` crashes on bad input** — user-typed queries with unmatched quotes or special chars will throw. Always use `websearch_to_tsquery` for user input.
2. **Stop words are stripped** — "the", "is", "in" are ignored. Searching for "the" returns nothing. Expected behavior.
3. **Language matters** — use `'english'` consistently. Mixing `'simple'` and `'english'` in the same column causes index mismatches.
4. **`ts_headline` on full body is slow** — run it only on the final paginated result, never in a subquery or CTE that returns all rows.
5. **Generated columns can't reference other generated columns** — if you need to combine multiple generated vectors, use a trigger instead.
6. **Array tags need special handling** — `array_to_string(tags, ' ')` before `to_tsvector`. Don't pass arrays directly.
