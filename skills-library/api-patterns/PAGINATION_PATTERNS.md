---
name: pagination-patterns
category: api-patterns
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [pagination, api, cursor, offset, rest, graphql]
difficulty: medium
---

# Pagination Patterns

## Problem

APIs that return unbounded lists kill performance, waste bandwidth, and crash clients. Offset-based pagination breaks under concurrent writes. Choosing the wrong pattern early means painful migration later.

## Three Patterns

### 1. Offset/Limit (Simple, Fragile)

```javascript
// GET /api/courses?page=2&limit=20
router.get('/courses', async (req, res) => {
  const page = Math.max(1, parseInt(req.query.page) || 1)
  const limit = Math.min(100, parseInt(req.query.limit) || 20)
  const offset = (page - 1) * limit

  const [courses, total] = await Promise.all([
    db.query('SELECT * FROM courses ORDER BY id LIMIT ? OFFSET ?', [limit, offset]),
    db.query('SELECT COUNT(*) as total FROM courses'),
  ])

  res.json({
    data: courses,
    pagination: {
      page,
      limit,
      total: total[0].total,
      totalPages: Math.ceil(total[0].total / limit),
      hasNext: page * limit < total[0].total,
      hasPrev: page > 1,
    }
  })
})
```

**Pros:** Easy to implement, supports "jump to page 5."
**Cons:** Skips/duplicates rows when data changes between pages. Slow on large offsets (DB must scan and discard rows).

### 2. Cursor-Based (Robust, Recommended)

```javascript
// GET /api/courses?cursor=eyJpZCI6MTAwfQ&limit=20
router.get('/courses', async (req, res) => {
  const limit = Math.min(100, parseInt(req.query.limit) || 20)
  const cursor = req.query.cursor
    ? JSON.parse(Buffer.from(req.query.cursor, 'base64').toString())
    : null

  const whereClause = cursor ? 'WHERE id > ?' : ''
  const params = cursor ? [cursor.id, limit + 1] : [limit + 1]

  const courses = await db.query(
    `SELECT * FROM courses ${whereClause} ORDER BY id LIMIT ?`,
    params
  )

  const hasNext = courses.length > limit
  if (hasNext) courses.pop()  // Remove the extra row

  const nextCursor = hasNext
    ? Buffer.from(JSON.stringify({ id: courses[courses.length - 1].id })).toString('base64')
    : null

  res.json({
    data: courses,
    pagination: {
      nextCursor,
      hasNext,
      limit,
    }
  })
})
```

**Pros:** Consistent results under concurrent writes. Fast (uses index seek, not offset scan).
**Cons:** Can't jump to arbitrary page. Cursor is opaque to client.

### 3. Keyset (Cursor + Sort)

```javascript
// When sorting by non-unique fields (e.g., created_at)
// Use composite cursor: (created_at, id) for uniqueness
const cursor = { created_at: '2026-02-24T10:00:00Z', id: 150 }

const courses = await db.query(`
  SELECT * FROM courses
  WHERE (created_at, id) > (?, ?)
  ORDER BY created_at, id
  LIMIT ?
`, [cursor.created_at, cursor.id, limit + 1])
```

## Which to Choose

| Scenario | Pattern | Why |
|----------|---------|-----|
| Admin dashboard, small dataset | Offset | Jump-to-page needed |
| Public API, large dataset | Cursor | Consistent, scalable |
| Real-time feed (chat, activity) | Cursor | Data changes constantly |
| Search results | Offset | Users expect page numbers |
| Infinite scroll UI | Cursor | Natural fit |

## Response Envelope

```json
{
  "data": [...],
  "pagination": {
    "nextCursor": "abc123",
    "hasNext": true,
    "limit": 20
  }
}
```

Always include `hasNext` — clients shouldn't have to guess.

## When to Use

- Any list endpoint returning more than 50 items
- APIs consumed by mobile apps (bandwidth matters)

## When NOT to Use

- Endpoints that always return small, bounded lists (e.g., user roles)
- Aggregation endpoints (return a single summary, not a list)
