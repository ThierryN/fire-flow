---
name: daemon-trigger-file-ipc
category: automation
version: 1.0.0
contributed: 2026-03-11
contributor: dominion-flow-memory
last_updated: 2026-03-11
contributors:
  - dominion-flow-memory
tags: [pm2, bun, daemon, hooks, trigger-file, ipc, claude-code, background-process, heartbeat]
difficulty: medium
usage_count: 1
success_rate: 100
---

# Daemon Trigger File IPC Pattern

## Problem

Background daemons (PM2, systemd, etc.) need to be notified when events happen in other processes — like a Claude Code session ending. Direct HTTP calls from hooks are fragile: the daemon might be down, the port might change, timeouts block the hook. You need a reliable, crash-safe IPC mechanism between short-lived hook scripts and long-running daemons.

Symptoms:
- Hook scripts timeout waiting for daemon HTTP response
- Daemon restart causes missed events
- Race conditions when daemon is mid-restart during hook execution
- Hook failures block the parent process (e.g., Claude Code session can't end)

## Solution Pattern

Use a **trigger file** as a message queue between hooks and daemons:

1. **Hook** writes a JSON trigger file to a known location
2. **Daemon** polls for the trigger file on its heartbeat interval
3. **Daemon** reads, processes, then **deletes** the file (atomic consume)
4. If daemon is down, trigger file persists until next startup

This is crash-safe: if the daemon crashes, the trigger file survives on disk and gets picked up on restart. If the hook crashes mid-write, the daemon simply skips the malformed file.

## Code Example

### Trigger Writer (called by hook)

```typescript
// src/daemon/trigger.ts
import { writeFile, mkdir } from 'fs/promises';
import { join } from 'path';

const STATE_DIR = join(
  process.env.HOME || process.env.USERPROFILE || '.',
  '.claude', 'daemon'
);
const TRIGGER_FILE = join(STATE_DIR, 'trigger-consolidate.json');

async function writeTrigger(): Promise<void> {
  const action = process.argv[2] || 'consolidate';
  const validActions = ['consolidate', 'gc', 'expire', 'full'];

  if (!validActions.includes(action)) {
    console.error(`Invalid action: ${action}. Use: ${validActions.join(', ')}`);
    process.exit(1);
  }

  await mkdir(STATE_DIR, { recursive: true });

  const trigger = {
    sessionId: `session-${Date.now()}`,
    timestamp: new Date().toISOString(),
    action,
    metadata: { cwd: process.cwd(), pid: process.pid },
  };

  await writeFile(TRIGGER_FILE, JSON.stringify(trigger, null, 2), 'utf-8');
  console.log(`Trigger written: ${action}`);
}

writeTrigger().catch(console.error);
```

### Trigger Consumer (inside daemon heartbeat)

```typescript
// Inside daemon's heartbeat pulse (runs every 1 minute)
private async checkTriggers(): Promise<void> {
  try {
    const raw = await readFile(TRIGGER_FILE, 'utf-8');
    const trigger = JSON.parse(raw);

    // Delete FIRST to prevent re-processing on crash
    await unlink(TRIGGER_FILE).catch(() => {});

    switch (trigger.action) {
      case 'consolidate':
        await this.maintainPulse();
        break;
      case 'gc':
        await this.gcPulse();
        break;
    }

    this.state.triggersProcessed++;
  } catch {
    // No trigger file or parse error — normal, skip silently
  }
}
```

### Claude Code Hook (Stop event)

```javascript
// ~/.claude/hooks/daemon-trigger.js
const input = [];
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input.push(chunk));
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input.join(''));
    if (data.stop_hook_active) {
      process.stdout.write(JSON.stringify({ ok: true }));
      return;
    }

    const { execFileSync } = require('child_process');
    const path = require('path');
    const bunPath = process.platform === 'win32'
      ? path.join(process.env.USERPROFILE || '', '.bun', 'bin', 'bun.exe')
      : 'bun';

    try {
      execFileSync(bunPath, ['run', 'src/daemon/trigger.ts', 'consolidate'], {
        cwd: 'C:\\NewSource\\repos\\dominion-flow-memory',
        timeout: 10000,
        stdio: 'pipe',
      });
    } catch { /* non-blocking */ }

    process.stdout.write(JSON.stringify({ ok: true }));
  } catch {
    process.stdout.write(JSON.stringify({ ok: true }));
  }
});
```

### Settings Registration

```json
// ~/.claude/settings.json — Stop hooks array
{
  "hooks": [{
    "type": "command",
    "command": "node \"C:/Users/Thierry/.claude/hooks/daemon-trigger.js\""
  }]
}
```

## Implementation Steps

1. Create the trigger writer script (`src/daemon/trigger.ts`)
2. Add `checkTriggers()` to the daemon's heartbeat pulse
3. Create the Claude Code hook script (`~/.claude/hooks/daemon-trigger.js`)
4. Register the hook in `~/.claude/settings.json` under `Stop`
5. Test: write trigger manually, force heartbeat via HTTP, verify `triggersProcessed` increments

## When to Use

- Background daemon needs to react to Claude Code session events
- Long-running process needs crash-safe IPC with short-lived scripts
- PM2/systemd daemon needs event-driven triggers alongside timer-based intervals
- You want non-blocking hooks that never prevent session from ending

## When NOT to Use

- Real-time (<1s) response needed — trigger files are polled, not pushed
- High-throughput IPC (hundreds of events/sec) — use proper message queues
- Two-way communication needed — trigger files are fire-and-forget
- The daemon is always guaranteed to be running — direct HTTP is simpler

## Common Mistakes

- **Writing empty string instead of deleting** — causes JSON.parse('') errors every heartbeat cycle
- **Deleting AFTER processing** — if daemon crashes mid-process, trigger is lost forever
- **Scoping hashMaps inside callbacks** — state shared across batched operations must persist outside the callback
- **Binding HTTP to 0.0.0.0** — always use `127.0.0.1` for localhost-only daemons
- **Missing concurrency guards** — trigger + interval can fire the same pulse simultaneously

## Related Skills

- [session-memory-lifecycle](./session-memory-lifecycle.md) — The capture/inject hooks that feed this daemon
- [PM2_ENVIRONMENT_VARIABLE_CACHING](../deployment-security/PM2_ENVIRONMENT_VARIABLE_CACHING.md) — PM2 env management

## References

- Letta sleep-time compute — daemon architecture inspiration
- Claude Code hooks documentation — SessionStart, Stop events
- PM2 ecosystem.config.cjs — cross-platform process management
- Contributed from: dominion-flow-memory v15.0 (2026-03-11)
