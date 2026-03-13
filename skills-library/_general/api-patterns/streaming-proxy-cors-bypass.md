---
name: streaming-proxy-cors-bypass
category: api-patterns
version: 1.0.0
contributed: 2026-03-12
contributor: mern-community-lms
last_updated: 2026-03-12
contributors:
  - mern-community-lms
tags: [cors, proxy, streaming, pipeline, node, express, video, cdn]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Streaming Proxy CORS Bypass

## Problem

Third-party CDNs (Zoom, Vimeo, cloud storage) serve media files without CORS headers. When your frontend tries to play or fetch these URLs directly, the browser blocks the request with a CORS error. A common workaround is to redirect the client (302) to the CDN URL, but this still fails because the browser's media element follows the redirect and hits the same CORS wall.

**Symptoms:**
- Video/audio playback fails silently or shows "blocked by CORS policy"
- `fetch()` to CDN URLs returns opaque responses or errors
- 302 redirects work in Postman but fail in browser
- `Access-Control-Allow-Origin` header missing from CDN response

## Solution Pattern

Instead of redirecting the client to the CDN, your server acts as a **streaming proxy** — it fetches the CDN resource server-side (no CORS restriction) and pipes the response body directly to the client using Node.js `stream.pipeline()`. The client only talks to your origin server, so CORS is never an issue.

**Key insight:** Server-to-server requests are not subject to CORS. By interposing your server as a transparent pipe, you eliminate the browser's CORS check entirely while adding minimal latency (streaming, not buffering).

## Code Example

```javascript
// Before (broken — 302 redirect hits CORS wall)
app.get('/api/video/replay/:meetingId', async (req, res) => {
  const downloadUrl = await getZoomDownloadUrl(req.params.meetingId);
  res.redirect(downloadUrl); // Browser follows redirect, CDN blocks CORS
});

// After (streaming proxy — no CORS issue)
import { pipeline } from 'stream/promises';

app.get('/api/video/replay/:meetingId', async (req, res) => {
  const downloadUrl = await getZoomDownloadUrl(req.params.meetingId);

  const cdnResponse = await fetch(downloadUrl, { redirect: 'follow' });

  if (!cdnResponse.ok) {
    return res.status(cdnResponse.status).json({ error: 'CDN fetch failed' });
  }

  // Forward content headers
  res.set('Content-Type', cdnResponse.headers.get('content-type') || 'video/mp4');
  const contentLength = cdnResponse.headers.get('content-length');
  if (contentLength) res.set('Content-Length', contentLength);

  // Stream body directly — no buffering in memory
  await pipeline(cdnResponse.body, res);
});
```

## Implementation Steps

1. Replace `res.redirect(cdnUrl)` with a server-side `fetch(cdnUrl)`
2. Forward relevant headers (`Content-Type`, `Content-Length`, `Content-Disposition`)
3. Use `stream.pipeline()` (or `pipe()`) to stream the response body to the client
4. Handle errors — if CDN returns 403/404, return a clean error to client
5. For authenticated CDNs (Zoom, AWS S3), add auth headers/tokens to the server-side fetch

## When to Use

- CDN serves media without CORS headers and you can't control the CDN config
- Third-party API returns download URLs that work server-side but not in browsers
- You need to proxy large files without buffering them entirely in memory
- OAuth-protected downloads (Zoom, Google Drive) where tokens can't be exposed to client

## When NOT to Use

- You control the CDN and can add CORS headers directly (simpler)
- The CDN already includes proper `Access-Control-Allow-Origin` headers
- Files are small enough to buffer — just use `res.send(await fetch(url).then(r => r.buffer()))`
- Static assets that should be served from a CDN for performance (proxy adds latency)

## Common Mistakes

- **Buffering the entire file in memory** — use `pipeline()` for streaming, not `await response.buffer()`
- **Not following redirects** — CDN URLs often redirect; use `{ redirect: 'follow' }` in fetch
- **Forgetting Content-Type** — browser won't play video if header is `application/octet-stream`
- **Not handling CDN auth expiry** — Zoom/S3 signed URLs expire; refresh token before proxying

## Related Skills

- [streaming-command-timeout](../api-patterns/streaming-command-timeout.md) — Timeout handling for streaming operations

## References

- Node.js `stream.pipeline()` documentation
- Zoom Server-to-Server OAuth API
- Contributed from: mern-community-lms (Zoom replay fix, 2026-03-12)
