---
name: streaming-command-timeout
category: api-patterns
version: 1.0.0
contributed: 2026-03-12
contributor: c3-server
last_updated: 2026-03-12
contributors:
  - c3-server
tags: [bun, node, process, timeout, streaming, pm2, ssh, spawn]
difficulty: easy
usage_count: 0
success_rate: 100
---

# Streaming Command Timeout — Preventing Hanging Process Execution

## Problem

When executing shell commands via `Bun.spawn` or `child_process.spawn`, some commands are streaming by default and never exit (e.g., `pm2 logs`, `tail -f`, `docker logs -f`). If you `await` their stdout, the process hangs forever — the API endpoint never responds, the UI spinner runs indefinitely, and server resources are leaked.

**Symptoms:**
- UI button spins forever after clicking "View Logs"
- API endpoint never returns a response
- Server eventually runs out of file descriptors or memory
- `pm2 logs` (without `--nostream`) never exits
- SSH commands to remote servers hang if the remote command streams

## Solution Pattern

Two-layer defense:

1. **Fix the command itself:** Add flags that make commands exit after producing output (`--nostream`, `--lines N`, `-n N`)
2. **Add a timeout wrapper:** Use `Promise.race` between process completion and a timeout timer. On timeout, kill the process and return partial output.

## Code Example

```typescript
// Before (hangs forever on streaming commands)
const proc = Bun.spawn(['bash', '-c', 'pm2 logs --lines 30'], {
  stdout: 'pipe', stderr: 'pipe'
})
const stdout = await new Response(proc.stdout).text()  // HANGS FOREVER

// After (exits cleanly with timeout protection)
const ACTION_TIMEOUT_MS = 30_000

const proc = Bun.spawn(['bash', '-c', 'pm2 logs --lines 30 --nostream'], {
  stdout: 'pipe', stderr: 'pipe'
})

const timeout = new Promise<'timeout'>((resolve) =>
  setTimeout(() => resolve('timeout'), ACTION_TIMEOUT_MS)
)

const result = await Promise.race([
  (async () => {
    const stdout = await new Response(proc.stdout).text()
    const stderr = await new Response(proc.stderr).text()
    const exitCode = await proc.exited
    return { stdout, stderr, exitCode } as const
  })(),
  timeout,
])

if (result === 'timeout') {
  proc.kill()
  const partial = await Promise.race([
    new Response(proc.stdout).text(),
    new Promise<string>((r) => setTimeout(() => r(''), 1000)),
  ])
  return {
    output: (partial || '') + '\n[Timed out after 30s]',
    success: true,  // Partial output is still useful
  }
}
```

## Implementation Steps

1. Audit all commands that can stream: `pm2 logs`, `docker logs`, `tail`, `ssh` with streaming remotes
2. Add exit flags: `--nostream`, `--lines N`, `-n N`
3. Wrap execution in `Promise.race` with a timeout (30s is reasonable for most commands)
4. On timeout: kill process, collect partial output, return with timeout notice
5. Return partial output as success (user still gets useful data)

## Common Streaming Commands & Fixes

| Command | Fix |
|---------|-----|
| `pm2 logs` | Add `--nostream` |
| `docker logs` | Remove `-f`, add `--tail N` |
| `tail -f` | Use `tail -n N` instead |
| `ssh ... 'pm2 logs'` | Add `--nostream` to remote command |
| `kubectl logs -f` | Remove `-f`, add `--tail N` |

## When to Use

- Any API endpoint that executes shell commands
- Quick action / one-click command systems
- Remote command execution via SSH
- CI/CD pipeline step execution
- Any `Bun.spawn` / `child_process.spawn` where the command set is user-configurable

## When NOT to Use

- SSE/WebSocket streaming endpoints (you WANT streaming there)
- Background jobs with their own lifecycle management
- Commands you've verified always exit quickly

## Common Mistakes

- Setting timeout too short (5s) — SSH commands to remote servers can take 10-15s to connect
- Killing the process but not collecting partial output — user gets "timeout" with no useful data
- Forgetting to clean up the timeout timer on successful completion (minor memory leak)
- Not adding `--nostream` AND adding timeout — the timeout alone works but wastes 30s every time

## References

- Bun docs: `Bun.spawn` API
- PM2 docs: `--nostream` flag (outputs then exits)
- Contributed from: c3-server action executor (PM2 logs hanging forever)
