---
name: tauri-ncc-sidecar-bundling
category: infrastructure
version: 1.0.0
contributed: 2026-03-01
contributor: claude-mission-control
last_updated: 2026-03-01
tags: [tauri, ncc, sidecar, bundling, express, node-pty, native-addons]
difficulty: hard
---

# Tauri Backend Sidecar Bundling with @vercel/ncc

## Problem

A Tauri desktop app needs to ship with a Node.js Express backend (70+ endpoints, WebSocket PTY, SSE, file watchers). The backend must:
- Bundle into a single distributable alongside the Tauri binary
- Include native Node.js addons (node-pty `.node` files, DLLs)
- Auto-start on app launch and auto-stop on window close
- Find a free port dynamically to avoid conflicts

Standard approaches fail:
- `pkg` doesn't handle native addons well
- Tauri sidecars expect executables, not Node.js scripts
- Native `.node` files can't be bundled by any JS bundler

## Solution Pattern

Use a 3-layer approach:

1. **@vercel/ncc** bundles the Express server into a single `index.js`
2. **Post-build script** copies native addon binaries alongside the bundle
3. **Tauri Rust launcher** spawns `node index.js` as a child process with port IPC

Key insight: ncc outputs `index.js` (NOT `index.cjs`). This mismatch breaks sidecar launch if the Rust code expects `.cjs`.

## Code Example

### package.json build scripts

```json
{
  "scripts": {
    "build:server": "ncc build server/index.ts -o server-dist/server --minify && node scripts/copy-native-addons.js",
    "build:all": "npm run build && npm run build:server"
  }
}
```

### Native addon copy script (scripts/copy-native-addons.js)

```javascript
import { cpSync, mkdirSync, existsSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const root = join(__dirname, '..')
const outDir = join(root, 'server-dist', 'server')

// node-pty prebuilds for Windows x64
const prebuildsDir = join(root, 'node_modules', 'node-pty', 'prebuilds', 'win32-x64')
const targetPrebuilds = join(outDir, 'prebuilds', 'win32-x64')

if (existsSync(prebuildsDir)) {
  mkdirSync(targetPrebuilds, { recursive: true })
  for (const file of ['pty.node', 'conpty.node', 'conpty_console_list.node']) {
    const src = join(prebuildsDir, file)
    if (existsSync(src)) cpSync(src, join(targetPrebuilds, file))
  }
  // Copy conpty DLL + winpty DLL similarly
}
```

### Rust sidecar launcher (src-tauri/src/lib.rs)

```rust
fn find_free_port(preferred: u16) -> u16 {
    for port in preferred..preferred + 100 {
        if TcpListener::bind(("127.0.0.1", port)).is_ok() {
            return port;
        }
    }
    preferred
}

// In setup:
let resource_dir = app.path().resource_dir().unwrap();
let server_bundle = resource_dir.join("server").join("index.js"); // NOT .cjs!
let port = find_free_port(3101);

let child = Command::new("node")
    .arg(&server_bundle)
    .env("MISSION_CONTROL_PORT", port.to_string())
    .spawn();

app.manage(ServerState { child: Mutex::new(child), port });
```

### tauri.conf.json resource inclusion

```json
{
  "bundle": {
    "resources": {
      "server-dist/server/**/*": "server/"
    }
  }
}
```

## When to Use

- Tauri app that needs a full Node.js backend (Express, Fastify, etc.)
- Backend uses native addons (node-pty, better-sqlite3, sharp, etc.)
- Need single-installer distribution for non-technical users
- Backend and frontend must communicate over localhost (HTTP/WS/SSE)

## When NOT to Use

- Simple Tauri apps that can use Tauri commands (IPC) instead of HTTP
- Backend has no native addons (just use ncc alone, skip the copy script)
- Target platform is mobile (Tauri mobile can't spawn Node.js)
- Backend is a separate microservice (use Docker instead)

## Common Mistakes

- **ncc output filename**: ncc outputs `index.js`, not `index.cjs` or `index.mjs`. The Rust launcher must match.
- **Missing native addons**: ncc silently skips `.node` files. Always verify the server-dist has the expected binaries.
- **Port conflicts**: Always use `find_free_port()` instead of hardcoding. Multiple instances or dev servers can claim the port.
- **Process cleanup**: Register `on_window_event(Destroyed)` to kill the child process. Orphaned Node.js processes leak memory.
- **node-pty conpty bug**: Node.js v24+ with node-pty 1.1.0 shows `AttachConsole failed` errors. The PTY still works but the console list agent crashes. Known issue: microsoft/node-pty PR #886.

## References

- @vercel/ncc: https://github.com/vercel/ncc
- Tauri v2 resources: https://v2.tauri.app/develop/resources/
- node-pty prebuilds: https://github.com/nickolasburr/node-pty-prebuilt
- Contributed from: claude-mission-control Phase 4 (Backend Sidecar Bundling)
