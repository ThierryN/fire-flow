---
name: tauri-dynamic-port-ipc
category: infrastructure
version: 1.0.0
contributed: 2026-03-01
contributor: claude-mission-control
last_updated: 2026-03-01
tags: [tauri, port, ipc, sidecar, rust, react, dynamic-port]
difficulty: medium
---

# Tauri Dynamic Port Discovery with Frontend IPC

## Problem

When a Tauri app launches a backend sidecar (Node.js, Python, etc.), the port can't be hardcoded because:
- Another instance might already use that port
- Dev servers (Vite, webpack) occupy ports during development
- Multiple Tauri apps with sidecars would conflict

Need: Rust finds a free port, tells the frontend, frontend uses it for all API/WebSocket calls.

## Solution Pattern

Three-layer port communication:

1. **Rust** scans for a free port starting from a preferred port
2. **Tauri command** exposes the port to the frontend via IPC
3. **Frontend** initializes API base URL from the Tauri command (with web fallback)

## Code Example

### Rust: Find free port + expose via command

```rust
use std::net::TcpListener;

fn find_free_port(preferred: u16) -> u16 {
    for port in preferred..preferred + 100 {
        if TcpListener::bind(("127.0.0.1", port)).is_ok() {
            return port;
        }
    }
    preferred // fallback
}

struct ServerState { port: u16 }

#[tauri::command]
fn get_server_port(state: tauri::State<'_, ServerState>) -> u16 {
    state.port
}

// In setup:
let port = find_free_port(3101);
app.manage(ServerState { port });
```

### Frontend: API base URL with Tauri/web dual-mode

```typescript
let _apiBase = ''
let _wsBase = ''

export async function initApiBase() {
  if ('__TAURI_INTERNALS__' in window) {
    const { invoke } = await import('@tauri-apps/api/core')
    const port = await invoke<number>('get_server_port')
    _apiBase = `http://127.0.0.1:${port}`
    _wsBase = `ws://127.0.0.1:${port}`
  } else {
    // Web mode: same origin (Vite proxy handles routing)
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
    _apiBase = ''  // relative URLs
    _wsBase = `${proto}//${location.host}`
  }
}

export function getApiBase() { return _apiBase }
export function getWsBase() { return _wsBase }
```

### Frontend: Patch global fetch/EventSource for Tauri mode

```typescript
// Monkey-patch fetch to prepend API base in Tauri mode
const originalFetch = window.fetch
window.fetch = (input, init) => {
  if (typeof input === 'string' && input.startsWith('/api') && _apiBase) {
    return originalFetch(_apiBase + input, init)
  }
  return originalFetch(input, init)
}
```

### Vite proxy for development (web mode)

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    port: 3100,
    proxy: {
      '/api': { target: 'http://localhost:3101' },
      '/ws': { target: 'ws://localhost:3101', ws: true },
      '/events': { target: 'http://localhost:3101' },
    }
  }
})
```

## When to Use

- Tauri app with any backend sidecar (Node.js, Python, Go, etc.)
- Need to support both Tauri desktop AND web browser modes
- Multiple backend processes need distinct ports
- CI/testing where ports may conflict

## When NOT to Use

- Backend is a fixed external service (just use its known URL)
- Tauri IPC commands handle all communication (no HTTP/WS needed)
- Single-user, single-instance app where port conflicts are impossible

## Common Mistakes

- **Race condition**: Find port THEN spawn server. If you spawn first with a hardcoded port, it may already be taken.
- **Binding vs connecting**: `TcpListener::bind()` checks availability. Don't use `TcpStream::connect()` which tries to connect to an existing server.
- **Vite proxy not matching**: Vite proxy paths must match exactly. `/api` proxies `/api/foo` but NOT `/api-foo`. Use separate entries for `/api`, `/ws`, `/events`.
- **WebSocket proxy**: Vite needs `ws: true` in proxy config for WebSocket upgrade. Without it, WS connections fail silently.
- **initApiBase timing**: Call `initApiBase()` in app startup BEFORE any API calls. Use a loading gate to prevent fetch during initialization.

## References

- Tauri v2 Commands: https://v2.tauri.app/develop/calling-rust/
- Vite Server Proxy: https://vite.dev/config/server-options#server-proxy
- Contributed from: claude-mission-control Phase 4
