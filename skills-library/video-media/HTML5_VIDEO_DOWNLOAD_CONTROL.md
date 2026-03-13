# HTML5 Video Download Control - Full-Stack Toggle Implementation

## The Problem

Admin sets "Allow Downloads" to OFF for a recording, but students can still download the video using the browser's native video player context menu (right-click > Save Video) and the three-dot "hamburger" menu download option.

### Why It Was Hard

- The admin toggle persisted correctly in the database (`allow_download` column)
- The API returned the correct value (`allowDownload: false`)
- The issue was spread across THREE layers:
  1. **Database field name mismatch**: Backend used `allow_download` (snake_case) but frontend sent `allowDownload` (camelCase) - toggle appeared to work but never persisted
  2. **Course linking used `parseInt()` on UUIDs**: Dropdown silently failed because `parseInt('a3f2b...')` returns `NaN`
  3. **Missing HTML5 `controlsList` attribute**: Even after fixing persistence, the `<video>` element didn't enforce the restriction

### Impact

- Content creators couldn't protect their recordings from unauthorized downloads
- Admin UI appeared to work (toggle flipped) but changes were silently lost
- Students could always download regardless of admin settings

---

## The Solution

### Layer 1: Fix Database Field Name (Backend)

**Root Cause**: The update endpoint expected `allow_download` but the frontend sent `allowDownload`.

**Fix** in the recording update controller:

```javascript
// BEFORE - only accepted snake_case
const allow_download = req.body.allow_download;

// AFTER - accept both camelCase and snake_case
const allow_download = req.body.allow_download ?? req.body.allowDownload;
```

### Layer 2: Fix Course Linking with UUIDs

**Root Cause**: `parseInt()` on a UUID string returns `NaN`.

```javascript
// BEFORE - breaks with UUID primary keys
const courseId = parseInt(selectedCourse);

// AFTER - UUIDs are strings, pass directly
const courseId = selectedCourse;
```

### Layer 3: Enforce Download Restriction in Video Player (Frontend)

**Root Cause**: HTML5 `<video>` element has a `controlsList` attribute that controls browser UI features.

```jsx
// BEFORE - no download control
<video
  ref={videoRef}
  controls
  src={playbackUrl}
>

// AFTER - conditionally disable download button
<video
  ref={videoRef}
  controls
  controlsList={recordingInfo?.allowDownload === false ? 'nodownload' : undefined}
  src={playbackUrl}
>
```

### Key Details About `controlsList`

- `controlsList="nodownload"` removes the download option from the browser's video controls
- It removes both the three-dot menu download option AND suppresses right-click "Save Video As"
- Set to `undefined` (not `""`) when downloads ARE allowed, so the attribute isn't rendered at all
- Check for `=== false` explicitly, not just falsy, to handle `undefined`/`null` (default = allow)
- This is a **hint** to the browser, not DRM - determined users can still access the source URL

---

## Testing the Fix

### Manual Test Procedure

1. **Admin side**: Edit a recording, toggle "Allow Downloads" OFF, save
2. **Verify persistence**: Refresh the admin page, confirm toggle is still OFF
3. **Student side**: Open the recording lesson as a student
4. **Check video controls**: The download button should be missing from the video player
5. **Right-click test**: Context menu should not show "Save Video As"
6. **Re-enable**: Toggle downloads back ON, verify download option returns

### Verification Query (PostgreSQL)

```sql
SELECT id, title, allow_download
FROM zoom_meetings
WHERE id = '<recording-uuid>';
-- Should show allow_download = false after admin saves
```

### API Response Check

```
GET /api/zoom/recordings/:id/refresh-urls
Response should include: { allowDownload: false }
```

---

## Prevention

1. **Always check field name conventions** between frontend (camelCase) and backend (snake_case)
2. **Accept both conventions** in API endpoints: `req.body.snake_case ?? req.body.camelCase`
3. **Never use `parseInt()` on UUIDs** - check if your DB uses UUID or integer PKs
4. **Always enforce UI restrictions client-side** when there's a server-side setting
5. **Test the full round-trip**: Admin saves -> DB persists -> API returns -> Player enforces

## Related Patterns

- [Video Player Enhancements](VIDEO_PLAYER_ENHANCEMENTS.md)
- [Complete Video Implementation](COMPLETE_VIDEO_IMPLEMENTATION.md)

## Common Mistakes to Avoid

- Using `controlsList=""` instead of `undefined` when downloads ARE allowed (empty string still sets the attribute)
- Checking `!allowDownload` instead of `=== false` (catches `undefined`/`null` which should default to allowed)
- Using `parseInt()` on UUID primary keys (returns NaN silently)
- Only fixing one layer (e.g., fixing persistence but not the player, or vice versa)
- Assuming camelCase/snake_case conversion happens automatically

---

## Resources

- [MDN: HTMLMediaElement.controlsList](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/controlsList)
- [HTML Spec: controlsList](https://html.spec.whatwg.org/multipage/media.html#attr-media-controlslist)

## Difficulty Level

Stars: 3/5 - The individual fixes are simple, but diagnosing the three-layer problem is the hard part.

---

**Author Notes:**
This is a classic "works in the UI but doesn't actually work" bug. The admin toggle animated correctly, the API returned 200, but the value never persisted because of a field name mismatch. Always test the full round-trip: UI -> API -> DB -> API -> UI enforcement. The three-dot menu download button in HTML5 video is controlled by `controlsList="nodownload"` - this is easy to miss because most developers don't know the attribute exists.
