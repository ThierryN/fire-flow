# Podcast Progress Tracking - Three Root Causes & Fixes

## The Problem

"Resume where you left off" for podcast episodes was completely broken. Every save attempt returned HTTP 500, every load returned 404, and progress was never persisted. Users could not resume playback from their last position.

### Why It Was Hard

Three independent root causes were stacked on top of each other, making diagnosis extremely difficult:
1. Database column type mismatch (UUID vs TEXT) caused silent 500 errors
2. RSS GUID whitespace corruption made IDs unmatchable
3. Express `%2F` decoding broke URL-type route parameters

Each fix alone appeared to "not work" because the other two were still failing. Only after fixing all three simultaneously did the feature start working.

### Impact

- Zero podcast progress was ever saved to the database
- Users always started episodes from the beginning
- Console showed `[useSavePodcastProgress] Failed to save progress` on every playback tick
- POST `/api/podcast-progress` => 500 (every time)
- GET `/api/podcast-progress/:episodeId` => 404 (every time)

---

## Root Cause 1: UUID Column vs URL Episode IDs

### The Problem

The `podcast_progress` table was created with `episode_id UUID NOT NULL`. But RSS episode GUIDs are URLs like:
```
https://permalink.castos.com/podcast/31199/episode/2313538
```

PostgreSQL rejected every INSERT because a URL string is not a valid UUID.

### The Fix

Migration to change column type from UUID to TEXT:

```sql
-- Migration 136: Fix podcast_progress.episode_id column type
ALTER TABLE podcast_progress DROP CONSTRAINT IF EXISTS podcast_progress_user_id_episode_id_key;
ALTER TABLE podcast_progress ALTER COLUMN episode_id TYPE TEXT USING episode_id::TEXT;
ALTER TABLE podcast_progress ADD CONSTRAINT podcast_progress_user_id_episode_id_key UNIQUE (user_id, episode_id);
```

For production (where you can't run migration files directly), create a one-time migration endpoint:

```javascript
// server/routes/migrations.js
router.post('/fix-podcast-progress-column', async (req, res) => {
  try {
    await sql`ALTER TABLE podcast_progress DROP CONSTRAINT IF EXISTS podcast_progress_user_id_episode_id_key`;
    await sql`ALTER TABLE podcast_progress ALTER COLUMN episode_id TYPE TEXT USING episode_id::TEXT`;
    await sql`ALTER TABLE podcast_progress ADD CONSTRAINT podcast_progress_user_id_episode_id_key UNIQUE (user_id, episode_id)`;
    res.json({ success: true, message: 'episode_id changed from UUID to TEXT' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});
```

### Lesson

Never use UUID columns for externally-sourced identifiers. RSS GUIDs, OAuth tokens, external API IDs, etc. are arbitrary strings. Always use TEXT for IDs you don't control.

---

## Root Cause 2: RSS GUID Whitespace

### The Problem

The `rss-parser` npm package returns `item.guid` with leading whitespace (newline + 20 spaces):

```
\n                    https://permalink.castos.com/podcast/31199/episode/2313538
```

This invisible whitespace meant:
- Saving used the dirty ID: `\n                    https://...`
- Loading compared against clean IDs: no match
- URL-encoding produced: `%0A++++++++++++++++++++https%3A%2F%2F...`

### The Fix

Trim GUIDs at the source (RSS parser output):

```javascript
// server/services/podcastService.js - Episode mapping
id: (item.guid || `episode-${index}`).trim(),
```

Also trim on the server controller side as defense-in-depth:

```javascript
// server/controllers/podcastProgressController.js
const cleanEpisodeId = String(episodeId).trim();
```

### Lesson

Always `.trim()` external string data at ingestion boundaries. RSS feeds, API responses, and user input commonly contain invisible whitespace.

---

## Root Cause 3: Express `%2F` Decoding Breaks URL Route Params

### The Problem

Route params containing URLs break because Express automatically decodes `%2F` to `/`:

```
GET /podcast-progress/https%3A%2F%2Fpermalink.castos.com%2Fpodcast%2F31199
```

Express decodes this to:
```
GET /podcast-progress/https://permalink.castos.com/podcast/31199
```

Which splits into multiple path segments, causing a 404.

### The Fix

Use query parameters instead of route parameters for URL-type IDs:

**Before (broken):**
```javascript
// Routes
router.get('/:episodeId', controller.getEpisodeProgress);
router.delete('/:episodeId', controller.deleteProgress);

// Controller
const episodeId = req.params.episodeId;

// Client
api.get(`/podcast-progress/${encodeURIComponent(episodeId)}`);
```

**After (working):**
```javascript
// Routes
router.get('/episode', controller.getEpisodeProgress);
router.delete('/episode', controller.deleteProgress);

// Controller
const episodeId = String(req.query.id || '').trim();

// Client
api.get('/podcast-progress/episode', { params: { id: episodeId } });
api.delete('/podcast-progress/episode', { params: { id: episodeId } });
```

### Lesson

Never use Express route parameters for values that may contain forward slashes. Query parameters handle URL-type IDs correctly because they're part of the query string, not the path.

---

## Bonus: Debounce vs Throttle for Playback Progress

### The Problem

The save hook used a 10-second **debounce**, but the `handleListen` callback fires every ~250ms during playback, resetting the debounce timer each time. Progress was never saved during continuous playback.

### The Fix

Use a **throttle** (via `useRef` timestamp) instead of debounce for periodic saves during playback:

```javascript
const lastSaveTimeRef = useRef(0);

const handleListen = useCallback(() => {
  const now = Date.now();
  if (now - lastSaveTimeRef.current >= 15000) { // 15-second throttle
    lastSaveTimeRef.current = now;
    saveImmediate({ episodeId, positionSeconds, durationSeconds });
  }
}, [episodeId, positionSeconds, durationSeconds]);
```

Use **immediate save** (no debounce) for explicit user actions:

```javascript
const handlePause = () => {
  saveImmediate({ episodeId, positionSeconds, durationSeconds });
};
```

Use `fetch` with `keepalive: true` for `beforeunload` (not `navigator.sendBeacon` which doesn't support Authorization headers):

```javascript
window.addEventListener('beforeunload', () => {
  fetch('/api/podcast-progress', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ episodeId, positionSeconds, durationSeconds }),
    keepalive: true,
  });
});
```

---

## Testing the Fix

### Verification via Playwright

1. Navigate to podcast page, select an episode
2. Monitor network requests for POST `/api/podcast-progress`
3. Verify POST returns 200 (not 500)
4. Reload page, navigate back to same episode
5. Verify GET `/api/podcast-progress/episode?id=...` returns 200 with saved position
6. Verify audio player resumes at saved position (check console for `[PodcastPlayer] Resuming at Xs`)

### Expected Results

```
POST /api/podcast-progress => 200 (saves every 15 seconds)
GET /api/podcast-progress/episode?id=<cleanId> => 200 (returns position)
Console: [PodcastPlayer] Resuming at 491.0s of 2831.7s
Player position: 08:12 (not 00:00)
```

---

## Prevention

1. **Use TEXT for external IDs** - Never assume external systems use UUIDs
2. **Trim all external strings** - RSS, APIs, webhooks all produce dirty data
3. **Use query params for URL-type IDs** - Express `%2F` decoding is a known gotcha
4. **Throttle, don't debounce, periodic saves** - Debounce resets on every tick
5. **Test with real data via Playwright** - Unit tests with clean mock data miss these edge cases

---

## Related Patterns

- [RSS Podcast Integration](../integrations/rss-podcast-integration.md) - Full RSS podcast setup
- [Express Route Ordering](EXPRESS_ROUTE_ORDERING_MIDDLEWARE_INTERCEPTION.md) - Express routing gotchas
- [Supabase Connection Fix](../database-solutions/supabase-connection-pooler-fix.md) - Database connection issues

## Common Mistakes to Avoid

- Using UUID columns for non-UUID identifiers from external systems
- Assuming `rss-parser` returns clean strings (it doesn't)
- Using `encodeURIComponent()` for route params with slashes (Express decodes `%2F` anyway)
- Using debounce for periodic saves during continuous playback (use throttle)
- Using `navigator.sendBeacon()` when you need Authorization headers (use `fetch` + `keepalive`)

---

## Resources

- [Express %2F issue](https://github.com/expressjs/express/issues/3552)
- [rss-parser npm](https://www.npmjs.com/package/rss-parser)
- [MDN: fetch keepalive](https://developer.mozilla.org/en-US/docs/Web/API/fetch#keepalive)

## Time to Implement

**30-45 minutes** for all three fixes (if you know the root causes). **6+ hours** to diagnose from scratch.

## Difficulty Level

Diagnosis: ⭐⭐⭐⭐⭐ (5/5) - Three stacked root causes make this extremely hard to diagnose
Fix: ⭐⭐ (2/5) - Each individual fix is simple once identified

---

**Author Notes:**
This bug took multiple sessions and Playwright browser automation to diagnose. The key insight was using Playwright to observe actual network requests on the live site, which revealed the 500/404 pattern. From there, tracing the episode ID format in the URL (`%0A++++++++++++++++++++https%3A%2F%2F...`) immediately revealed the whitespace issue, and checking the database schema revealed the UUID mismatch. The Express `%2F` issue was found by testing what happened after fixing the first two.

The stacking effect is the real danger: each fix alone makes you think "it's still broken" when really it's a different bug now. Always enumerate all possible failure points before concluding a fix didn't work.
