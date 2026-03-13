---
name: tauri-dev-mode-connectivity
category: infrastructure
version: 1.0.0
contributed: 2026-03-01
contributor: claude-mission-control
last_updated: 2026-03-01
tags: [tauri, cors, unc-path, sse, devurl, express, windows, cross-origin]
difficulty: medium
---

# Tauri Dev Mode Connectivity: Three Silent Killers

## Problem

A Tauri v2 desktop app with a bundled Node.js Express backend shows "Initializing" or "OFFLINE" even though the backend server is healthy and responds to curl. The browser (via Vite dev server) works fine, but the Tauri webview does not connect.

This manifests as:
- App stuck on loading screen forever
- SSE EventSource never fires `onopen`
- Health check polls timeout despite server running
- No visible error messages (failures are silent)

## Root Causes (Three Bugs Working Together)

### Bug 1: Windows UNC Extended Path

Tauri's `app.path().resource_dir()` returns a Windows UNC extended path:
```
\\?\C:\Users\user\AppData\Local\app\resources\
```

Node.js cannot handle the `\\?\` prefix — it tries to `realpathSync` on `C:` which fails with `EISDIR: illegal operation on a directory`.

### Bug 2: Missing CORS Headers

In dev mode, Tauri's `devUrl` loads the frontend from `http://localhost:3100` (Vite), but `initApiLayer()` patches fetch/EventSource to hit the backend on `http://localhost:3101` directly. This is a **cross-origin request** that browsers block silently.

In browser-only mode this works because Vite's proxy keeps everything same-origin. The Tauri IPC path bypasses the proxy.

### Bug 3: SSE Connection Never Opens

Express SSE endpoints that don't send an initial response leave `EventSource.onopen` waiting. The browser needs at least one flushed chunk (even a comment) for the connection to register as open.

## Solution Pattern

### Fix 1: Strip UNC Prefix in Rust (lib.rs)

```rust
// Strip Windows UNC extended prefix (\\?\) — Node.js can't handle it
let resource_str = resource_dir.to_string_lossy().to_string();
let resource_clean = if resource_str.starts_with(r"\\?\") {
    std::path::PathBuf::from(&resource_str[4..])
} else {
    resource_dir
};
let server_bundle = resource_clean.join("server-dist").join("server").join("index.js");
```

### Fix 2: Add CORS Middleware (Express server)

```typescript
// CORS: Allow Tauri webview (localhost:3100) to reach API (localhost:3101)
app.use((_req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*')
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization')
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
  if (_req.method === 'OPTIONS') return res.sendStatus(204)
  next()
})
```

### Fix 3: SSE Initial Flush (Express endpoint)

```typescript
app.get('/api/events', (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive',
  })

  // Flush headers + send initial event so EventSource.onopen fires immediately
  res.write(': connected\n\n')

  sseClients.add(res)
  req.on('close', () => sseClients.delete(res))
})
```

## Dev Workflow Fix: beforeDevCommand

Tauri dev mode waits for `devUrl` to be available. Set `beforeDevCommand` to auto-start the frontend:

```json
{
  "build": {
    "devUrl": "http://localhost:3100",
    "beforeDevCommand": "npm run dev:client"
  }
}
```

Run only `npm run tauri dev` — it starts Vite automatically, then the Rust setup hook spawns the bundled backend.

**Do NOT run `npm run dev` alongside `npm run tauri dev`** — both start the backend on the same port, causing EADDRINUSE.

## Tauri Dev Server Bundle Gotcha

When editing JS/TS server files during development:

1. Run `npm run build:server` to rebuild the ncc bundle
2. **Manually copy** to `src-tauri/target/debug/server-dist/` — Tauri only copies resources during Rust recompilation, not when JS changes
3. Restart `npm run tauri dev`

```bash
npm run build:server
cp -r src-tauri/server-dist/ src-tauri/target/debug/server-dist/
```

## When to Use

- Building Tauri v2 apps with Node.js/Express backend sidecars
- Any Tauri app where `devUrl` and backend API are on different ports
- SSE/EventSource connections in Tauri webviews
- Windows deployment of Tauri apps with resource files passed to Node.js

## When NOT to Use

- Tauri apps with no backend (pure frontend)
- Backend compiled as native binary (no Node.js path issues)
- Single-port architectures where frontend and API share a port

## Common Mistakes

- Assuming Vite proxy behavior applies in Tauri mode (it doesn't — IPC patches bypass it)
- Not testing the packaged .exe separately from dev mode (different resource paths)
- Forgetting that `cargo build` must re-run for resource file changes to take effect
- Using `resource_dir()` paths directly with Node.js on Windows

## Related Skills

- [tauri-dynamic-port-ipc](./TAURI_DYNAMIC_PORT_IPC.md) - Port discovery and frontend IPC
- [tauri-ncc-sidecar-bundling](./TAURI_NCC_SIDECAR_BUNDLING.md) - Building the server bundle

## References

- Tauri v2 Resources: https://v2.tauri.app/develop/resources/
- Windows UNC paths: https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file
- SSE specification: https://html.spec.whatwg.org/multipage/server-sent-events.html
- Discovered from: claude-mission-control debug session 2026-03-01
