---
name: persistent-analysis-storage
category: database-solutions
version: 1.0.0
contributed: 2026-03-01
contributor: scribe-bible
last_updated: 2026-03-01
contributors:
  - scribe-bible
tags: [prisma, postgresql, persistence, favorites, sharing, nanoid, cursor-pagination, dual-storage]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Persistent Analysis Storage

## Problem

AI-powered analysis features (deep research, recursive reasoning, multi-step pipelines) produce expensive results that take 30-120+ seconds and significant API cost. Users need to:

1. **Save results permanently** to their account (not just browser localStorage)
2. **Favorite** important analyses for quick access
3. **Share publicly** via short links (without requiring recipient login)
4. **Browse history** with filtering and pagination
5. **Maintain anonymous fallback** — localStorage history works without login

Without DB persistence, results vanish on browser clear. Without dual-storage, unauthenticated users get no history at all.

## Solution Pattern

Implement a **dual-storage architecture** with localStorage as the anonymous/immediate layer and PostgreSQL (via Prisma) as the authenticated persistent layer. Each layer serves a different purpose:

- **localStorage**: Instant, no-auth, limited to ~50 items, browser-scoped
- **Database**: Permanent, auth-required, unlimited, supports sharing/favorites

The key insight is these layers are **complementary, not competing** — localStorage provides instant gratification while DB provides permanence. The UI presents both via a tabbed sidebar.

## Code Example

### Prisma Model

```prisma
model RlmAnalysis {
  id              String   @id @default(uuid())
  userId          String
  query           String
  analysisType    String
  result          String   @db.Text
  trajectoryId    String
  trajectory      String?  @db.Text    // JSON stringified steps
  tokenUsage      String?              // JSON stringified usage
  durationSeconds Float
  translation     String   @default("kjv")
  isFavorite      Boolean  @default(false)
  isPublic        Boolean  @default(false)
  shareSlug       String?  @unique     // nanoid(8) generated on first share
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  user            User     @relation(fields: [userId], references: [id])

  @@index([userId, createdAt])
  @@index([userId, isFavorite])
  @@index([analysisType])
}
```

### Storage Service (CRUD + Sharing)

```typescript
// Toggle public sharing — generates a short slug on first share
export async function toggleShare(id: string, userId: string) {
  const analysis = await prisma.analysis.findUnique({ where: { id } });
  if (!analysis || analysis.userId !== userId) return null;

  const isPublic = !analysis.isPublic;
  const shareSlug = isPublic && !analysis.shareSlug ? nanoid(8) : analysis.shareSlug;

  return prisma.analysis.update({
    where: { id },
    data: { isPublic, shareSlug },
  });
}

// Cursor-based pagination (better than offset for large sets)
export async function listAnalyses(options: ListOptions) {
  const { userId, type, favoritesOnly, limit = 20, cursor } = options;
  const where: any = { userId };
  if (type) where.analysisType = type;
  if (favoritesOnly) where.isFavorite = true;

  const analyses = await prisma.analysis.findMany({
    where,
    orderBy: { createdAt: 'desc' },
    take: limit + 1,  // Fetch one extra to detect hasMore
    ...(cursor ? { cursor: { id: cursor }, skip: 1 } : {}),
    select: { id: true, query: true, analysisType: true, /* ... */ },
  });

  const hasMore = analyses.length > limit;
  const items = hasMore ? analyses.slice(0, limit) : analyses;
  return { items, nextCursor: hasMore ? items[items.length - 1].id : null, hasMore };
}
```

### API Endpoints (7 routes)

```typescript
// Auth-required endpoints
router.post('/saved', authenticateToken, saveHandler);        // Save analysis
router.get('/saved', authenticateToken, listHandler);         // List with filters
router.get('/saved/:id', authenticateToken, getHandler);      // Get single
router.delete('/saved/:id', authenticateToken, deleteHandler);// Delete
router.post('/saved/:id/favorite', authenticateToken, favHandler);  // Toggle favorite
router.post('/saved/:id/share', authenticateToken, shareHandler);   // Toggle share

// Public endpoint (no auth)
router.get('/shared/:slug', sharedHandler);  // View shared analysis
```

### Frontend Hook (Dual Storage)

```typescript
// localStorage for anonymous history
const [history, setHistory] = useState<HistoryItem[]>(loadHistory);

// DB-backed for authenticated persistence
const saveToDb = useCallback(async (result: AnalysisResult) => {
  const res = await fetch(`${API_BASE}/api/saved`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(result),
  });
  if (!res.ok) return null;
  // Mark in local history as saved (cross-reference)
  setHistory(prev => prev.map(h =>
    h.trajectoryId === result.trajectoryId ? { ...h, savedToDb: true } : h
  ));
  return (await res.json()).data;
}, []);
```

### Tabbed Sidebar UI

```tsx
{/* Tab buttons */}
<button onClick={() => setSidebarTab('recent')}
  className={sidebarTab === 'recent' ? 'active' : ''}>
  Recent ({history.length})
</button>
<button onClick={() => { setSidebarTab('saved'); loadSavedAnalyses(); }}
  className={sidebarTab === 'saved' ? 'active' : ''}>
  Saved ({savedAnalyses.length})
</button>

{/* Tab content */}
{sidebarTab === 'recent' ? (
  // localStorage items with "saved" badge
  history.map(item => <HistoryItem key={item.id} item={item} />)
) : (
  // DB-backed items with favorite/share/delete actions
  savedAnalyses.map(item => <SavedItem key={item.id} item={item} />)
)}
```

## Implementation Steps

1. Add Prisma model with indexes on userId+createdAt, userId+isFavorite, and unique shareSlug
2. Create storage service with CRUD + toggleFavorite + toggleShare (nanoid for slugs)
3. Add 7 API routes (6 auth-required + 1 public shared endpoint)
4. Extend frontend hook with DB persistence methods alongside existing localStorage
5. Add tabbed sidebar UI (Recent/Saved) with action buttons on saved items
6. Cross-reference: mark localStorage items as "savedToDb" when saved to DB

## When to Use

- AI analysis features that produce expensive, non-reproducible results
- Any feature where users want to bookmark/favorite results for later
- When public sharing via short links is needed (portfolios, collaboration)
- Dual anonymous + authenticated experience (localStorage fallback)
- Large result sets needing cursor-based pagination

## When NOT to Use

- Simple caching (use AI_RESPONSE_DATABASE_CACHING skill instead)
- Ephemeral data that doesn't need user ownership (use Redis/in-memory)
- When results are cheap to recompute (no persistence needed)
- Single-user apps with no sharing requirement (localStorage may suffice)

## Common Mistakes

- Using offset pagination instead of cursor-based (degrades at scale)
- Generating share slugs eagerly instead of on first share toggle (wasted IDs)
- Forgetting to handle the "not found OR not authorized" case (leaks existence info)
- Not providing localStorage fallback for unauthenticated users
- Storing large JSON blobs (trajectory, tokenUsage) as regular String instead of @db.Text

## Related Skills

- [AI_RESPONSE_DATABASE_CACHING](AI_RESPONSE_DATABASE_CACHING.md) - Cache-first pattern for avoiding recomputation
- cursor-pagination - Efficient large dataset browsing pattern

## References

- nanoid: https://github.com/ai/nanoid — short unique ID generation
- Prisma cursor pagination: https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination
- Contributed from: scribe-bible (Phase 2 — Persistent Analysis Storage)
