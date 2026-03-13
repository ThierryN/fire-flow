---
name: crash-resilient-recording
category: video-media
version: 2.0.0
contributed: 2026-02-25
contributor: my-other-project
last_updated: 2026-02-25
contributors:
  - my-other-project
tags: [mediarecorder, audio, crash-recovery, incremental-save, sendbeacon, heartbeat, webm, opus, indexeddb, offline-first]
difficulty: hard
usage_count: 1
success_rate: 100
---

# Crash-Resilient Browser Recording

## Problem

Browser-based recording (audio/video + transcript) stores all data in memory until the user clicks "Stop." If the computer crashes, browser tab closes, or network drops during a long recording session (1+ hours), **ALL data is lost** — zero recovery possible.

**Root cause:** MediaRecorder accumulates blobs in a JS array. The single upload happens only on explicit stop. No intermediate saves occur.

**Symptoms:**
- Session created on server but shows 0 words, 00:00 duration after crash
- PM2/server logs show POST to create session but zero PUT auto-save requests
- User loses hours of recorded content with no recovery path

## Solution Pattern

**6-layer crash resilience architecture** (v2.0 — IndexedDB + 10s chunks):

1. **10-second audio chunks** — `MediaRecorder.start(10000)` timeslice emits `ondataavailable` every 10 seconds. Upload triggered directly inside the callback (no separate timer = no race condition). Max data loss: 10 seconds.

2. **IndexedDB audio buffer** — Every chunk is stored in IndexedDB FGTAT (crash-proof, persists through power outages), then uploaded to server. If offline, chunks queue in IndexedDB and flush on reconnect.

3. **Aggressive transcript auto-save** — Auto-save interval at 10s with immediate first-save when first speech segment arrives.

4. **sendBeacon emergency saves** — `visibilitychange` + `beforeunload` events fire `navigator.sendBeacon()` with current transcript. Fire-and-forget — survives tab close.

5. **localStorage crash recovery** — Every segment change backs up to localStorage. On page reload, detect stale data and offer recovery banner.

6. **Server-side heartbeat + abandoned session sweep** — Every auto-save updates `last_heartbeat`. If heartbeat stale >90 seconds, server auto-completes the session. Sweep runs on page load (getSessions) and during auto-save.

## Code Example

### Before (problematic — single upload on stop)

```javascript
// Audio stored entirely in browser memory
const chunks = [];
recorder.ondataavailable = (e) => chunks.push(e.data);
recorder.start(5000); // 5s timeslice but never uploaded

// Only uploaded when user clicks "Stop"
const handleStop = async () => {
  const blob = new Blob(chunks, { type: 'audio/webm' });
  await uploadBlob(blob); // CRASH HERE = TOTAL LOSS
};

// Auto-save every 30 seconds — too slow, no first-save
setInterval(saveTranscript, 30000);
```

### After (crash-resilient — IndexedDB + incremental saves)

```javascript
// === CLIENT: IndexedDB Audio Buffer ===
const IDB_NAME = 'lt_audio_buffer';
const IDB_STORE = 'chunks';

async function storeAudioChunk(sessionId, chunkNumber, blob, mimeType) {
  const db = await openAudioDb();
  const tx = db.transaction(IDB_STORE, 'readwrite');
  tx.objectStore(IDB_STORE).add({
    sessionId, chunkNumber, blob, mimeType,
    uploaded: false, timestamp: Date.now(),
  });
  await new Promise((res, rej) => { tx.oncomplete = res; tx.onerror = rej; });
  db.close();
}

async function flushAudioChunksToServer(sessionId) {
  const chunks = await getUnuploadedChunks(sessionId);
  let flushed = 0;
  for (const chunk of chunks) {
    const ext = chunk.mimeType.includes('webm') ? '.webm' : '.mp4';
    const formData = new FormData();
    formData.append('audio', chunk.blob, `chunk-${chunk.chunkNumber}${ext}`);
    formData.append('chunk_number', String(chunk.chunkNumber));
    await api.post(`/session/${sessionId}/audio-chunk`, formData);
    await markChunkUploaded(chunk.id);
    flushed++;
  }
  return flushed;
}

// === CLIENT: Incremental chunk upload (10s) ===
const AUDIO_CHUNK_INTERVAL = 10_000; // 10 seconds for crash resilience
let chunkCount = 0;
const uploadingRef = { current: false };

const uploadChunk = async () => {
  if (uploadingRef.current || chunks.length === 0) return;
  uploadingRef.current = true;
  try {
    const blob = new Blob(chunks, { type: 'audio/webm' });
    chunks = [];
    chunkCount++;

    // 1. IndexedDB FGTAT (survives crashes/power outages)
    await storeAudioChunk(sessionId, chunkCount, blob, mimeType);

    // 2. Server upload (if online)
    if (!navigator.onLine) return; // queued in IDB, flush on reconnect
    const formData = new FormData();
    formData.append('audio', blob, `chunk-${chunkCount}.webm`);
    formData.append('chunk_number', String(chunkCount));
    await api.post(`/session/${id}/audio-chunk`, formData);
  } finally {
    uploadingRef.current = false;
  }
};

// Upload directly in ondataavailable — NO separate timer (prevents race)
recorder.ondataavailable = (e) => {
  if (e.data.size > 0) {
    chunks.push(e.data);
    uploadChunk(); // fires at each timeslice boundary
  }
};
recorder.start(AUDIO_CHUNK_INTERVAL);

// === CLIENT: Online reconnect flush ===
window.addEventListener('online', async () => {
  const flushed = await flushAudioChunksToServer(sessionId);
  if (flushed > 0) toast.success(`Synced ${flushed} audio chunks`);
});

// === CLIENT: Orphaned chunk recovery on page load ===
useEffect(() => {
  (async () => {
    const orphaned = await getOrphanedAudioSessions();
    for (const { sessionId, chunkCount } of orphaned) {
      const flushed = await flushAudioChunksToServer(sessionId);
      if (flushed === chunkCount) await clearAudioChunks(sessionId);
    }
  })();
}, []);

// === CLIENT: Emergency save on tab close ===
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') {
    navigator.sendBeacon(
      `/api/session/${id}/beacon`,
      new Blob([JSON.stringify({ transcript, segments })], { type: 'application/json' })
    );
    saveToLocalStorage(id, segments);
  }
});

// === CLIENT: Stop recording — flush + finalize ===
recorder.onstop = async () => {
  if (chunks.length > 0) await uploadChunk(); // flush last partial chunk
  const flushed = await flushAudioChunksToServer(sessionId);
  await api.post(`/session/${sessionId}/finalize-audio`);
  await clearAudioChunks(sessionId); // cleanup IndexedDB
  clearLocalStorage();
};

// === SERVER: Chunk concatenation ===
async function concatenateChunks(sessionId) {
  const dir = `uploads/audio-chunks/${sessionId}`;
  const files = fs.readdirSync(dir).filter(f => f.startsWith('chunk-')).sort();
  const writeStream = fs.createWriteStream(`uploads/audio/${sessionId}.webm`);
  for (const file of files) {
    writeStream.write(fs.readFileSync(path.join(dir, file)));
  }
  await new Promise((res, rej) => { writeStream.on('finish', res); writeStream.on('error', rej); writeStream.end(); });
  // Cleanup chunk directory
  for (const file of files) fs.unlinkSync(path.join(dir, file));
  fs.rmdirSync(dir);
  return `/uploads/audio/${sessionId}.webm`;
}

// === SERVER: Heartbeat sweep (on page load + auto-save) ===
await sql`
  UPDATE sessions SET status = 'completed',
    metadata = jsonb_set(COALESCE(metadata,'{}'), '{auto_completed}', 'true')
  WHERE status = 'recording'
    AND last_heartbeat < NOW() - INTERVAL '90 seconds'
`;
```

## Implementation Steps

1. **Database:** Add `last_heartbeat TIMESTAMPTZ` column + partial index on `(status, last_heartbeat) WHERE status = 'recording'`
2. **Server routes:** Add `POST /:id/audio-chunk` (multer), `POST /:id/finalize-audio`, `POST /:id/beacon`
3. **Server controller:** Chunk upload saves to `uploads/audio-chunks/{sessionId}/chunk-{N}.webm`, finalize concatenates, beacon returns 204
4. **Server sweep:** Update `getSessions` and `updateSession` to sweep stale sessions (heartbeat >90s)
5. **Client IndexedDB:** Create `lt_audio_buffer` database with `chunks` object store (sessionId index)
6. **Client recording:** Use `recorder.start(10000)` timeslice, upload in `ondataavailable` callback (not separate timer)
7. **Client recovery:** Orphaned chunk flush on mount, online reconnect flush, crash recovery banner from localStorage
8. **Client UI:** Crash recovery banner, offline warning banner, save indicator

## When to Use

- Any browser-based recording feature (audio, video, screen capture)
- Long-running browser sessions where data accumulates in memory
- Applications where users cannot afford to lose hours of work
- Live streaming/teaching/podcast recording tools
- Any MediaRecorder-based application

## When NOT to Use

- Short recordings (<2 minutes) where total loss is acceptable
- Server-side recording (e.g., Twilio, Daily.co) — the server already has the data
- Real-time streaming to a server (WebSocket/WebRTC) — data is already server-side
- File upload workflows where the file exists on disk before upload

## Key Technical Details

### v2.0 Breakthrough: IndexedDB over localStorage for Audio

- **localStorage** can only store strings (base64 encoded blobs = 4x size overhead, 5-10MB limit)
- **IndexedDB** stores raw Blobs natively (no encoding overhead, GB-scale capacity)
- IndexedDB persists through browser crashes, tab closes, and usually power outages (data is on disk)
- Use `uploaded: false` flag to track which chunks need server sync

### Race Condition Fix: ondataavailable vs setInterval

- **v1 bug:** Two independent timers (MediaRecorder timeslice + setInterval) with same interval would race. If both fired simultaneously, chunks could be missed or double-uploaded.
- **v2 fix:** Upload directly inside `ondataavailable` callback. No separate timer needed. MediaRecorder's internal timer is the single source of truth.

### 10s vs 60s Chunk Interval

- 60s timeslice means crash loses up to 60 seconds of audio — unacceptable for lectures
- 10s timeslice: each chunk ~160KB (Opus codec), negligible bandwidth overhead
- 80-second test recording = 8 chunks, ~1.26MB total — verified in production
- 1-hour recording at 10s = ~360 chunks, ~57MB — well within server storage limits

### WebM Chunk Concatenation

- Only chunk 0 has the EBML/WebM header. Subsequent chunks are raw continuation data.
- Simple binary concatenation produces a valid WebM file — no remuxing needed.
- This works because MediaRecorder with timeslice produces a single continuous byte stream, just split at time boundaries.
- **Does NOT work for MP4** — MP4 requires moov atom rewriting. Use WebM/Matroska for this pattern.

### sendBeacon Gotchas

- Cannot set custom headers (no `Authorization: Bearer ...`)
- **Solution:** Use httpOnly cookie for JWT auth, or use a permissive beacon endpoint
- Always returns `true` (queued) or `false` (failed) — no response body
- Server endpoint should always return 204 — browser ignores the response
- `req.body` may be undefined if Express JSON middleware doesn't handle Blob type — add fallback: `const body = req.body || {}`

### Heartbeat Sweep — No Cron Needed

- Piggyback on existing auto-save PUT and getSessions GET: every request also sweeps for abandoned sessions
- PostgreSQL partial index `WHERE status = 'recording'` makes sweep near-zero cost
- Only scans the handful of actively-recording sessions, not the entire table
- Single-user edge case: sweep also runs on page load (getSessions) to catch sessions with no active recorders

## Common Mistakes

- **Using `recorder.start()` without timeslice** — ondataavailable only fires once on stop
- **Using separate setInterval for chunk upload** — races with MediaRecorder's internal timeslice timer. Upload inside ondataavailable instead.
- **Storing audio in localStorage** — localStorage is string-only with 5-10MB limit. Use IndexedDB for binary Blob storage.
- **Trying to play individual chunks** — only chunk 0 is independently playable; the rest need the header
- **Setting sendBeacon auth via headers** — sendBeacon doesn't support custom headers; use cookies
- **Using cron for abandoned session cleanup on shared hosting** — piggyback on existing requests instead
- **Forgetting to clear IndexedDB on successful stop** — orphaned chunks waste disk space
- **Not flushing IndexedDB chunks before finalize** — some chunks may be in IDB but not on server

## Related Skills

- [video-player-integration-guide](./video-player-integration-guide.md) - Video playback patterns
- [MEDIA_PLAYBACK_RESUME_PATTERN](./MEDIA_PLAYBACK_RESUME_PATTERN.md) - Resume playback from last position

## References

- MDN: [MediaRecorder.start() timeslice parameter](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder/start)
- MDN: [Navigator.sendBeacon()](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/sendBeacon)
- MDN: [IndexedDB API](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
- WebM container spec: EBML header only in first cluster
- Industry reference: Riverside.fm local-first recording architecture
- Contributed from: my-other-project (Live Teaching Studio, Feb 2026)
- Production verified: 8 chunks / 1.26MB / 80 seconds — all chunks saved, concatenated, playable
