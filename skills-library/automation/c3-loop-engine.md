---
name: c3-loop-engine
category: automation
version: 1.0.0
contributed: 2026-03-12
contributor: c3-server
last_updated: 2026-03-12
contributors:
  - c3-server
tags: [c3, loops, polling, sse, bun, express, automation, mission-control]
difficulty: hard
usage_count: 0
success_rate: 100
---

# C3 Loop Engine — Background Polling Loops with SSE Broadcasting

## Problem

A mission-control system needs automated background loops that:
- Poll files/APIs on configurable intervals (2m, 1h, 6h)
- Execute actions when conditions are met (e.g., unacknowledged commands)
- Broadcast events to connected dashboards via Server-Sent Events
- Start/stop independently without blocking the main server

## Solution Pattern

A loop engine that reads loop definitions from a JSON config, manages `setInterval` timers per loop, and broadcasts status changes via SSE. Each loop is independent: can be started, stopped, and toggled without affecting others.

**Architecture:**
```
c3-automation.json → Loop Engine → setInterval per loop
                                 → SSE broadcast on events
                                 → API endpoints for control
```

## Code Example

```typescript
// Loop definition (from config)
interface C3Loop {
  id: string
  name: string
  command: string      // What to execute on each tick
  interval: string     // "2m", "1h", "6h"
  enabled: boolean
}

// Loop state (runtime)
interface LoopState {
  running: boolean
  lastRun: string | null
  nextRun: string | null
  runCount: number
  intervalId: ReturnType<typeof setInterval> | null
}

// Parse interval strings to milliseconds
function parseInterval(interval: string): number {
  const match = interval.match(/^(\d+)(s|m|h|d)$/)
  if (!match) return 60000
  const [, num, unit] = match
  const multipliers: Record<string, number> = {
    s: 1000, m: 60000, h: 3600000, d: 86400000
  }
  return parseInt(num) * (multipliers[unit] || 60000)
}

// Start a loop
function startLoop(loop: C3Loop, state: LoopState, broadcast: (event: string, data: any) => void) {
  if (state.running) return

  const ms = parseInterval(loop.interval)
  const tick = async () => {
    state.lastRun = new Date().toISOString()
    state.runCount++
    state.nextRun = new Date(Date.now() + ms).toISOString()
    broadcast('c3-loop-update', { id: loop.id, ...state })

    // Execute the loop's command/logic here
    await executeLoopAction(loop)
  }

  tick() // Run immediately on start
  state.intervalId = setInterval(tick, ms)
  state.running = true
  state.nextRun = new Date(Date.now() + ms).toISOString()
  broadcast('c3-loop-update', { id: loop.id, ...state })
}

// API endpoints
app.get('/api/c3/loops', (req, res) => {
  res.json({ loops: loopsWithState })
})

app.post('/api/c3/loops/:id/toggle', (req, res) => {
  const state = loopStates[req.params.id]
  state.running ? stopLoop(id) : startLoop(loop, state, broadcast)
  res.json({ success: true })
})
```

## Implementation Steps

1. Define loop configs in JSON (id, name, command, interval, enabled)
2. Create loop state map: `Map<string, LoopState>`
3. Implement `startLoop()` / `stopLoop()` with `setInterval` management
4. Add SSE broadcasting for real-time dashboard updates
5. Create API endpoints: GET status, POST toggle/start/stop
6. Auto-start enabled loops on server boot
7. Add health endpoint showing all loop states

## When to Use

- Mission control / operations dashboards
- Automated monitoring systems
- Polling-based integrations (file watchers, API checkers)
- Any system needing configurable background tasks

## When NOT to Use

- Use cron for system-level scheduled tasks
- Use message queues (Redis, RabbitMQ) for high-throughput job processing
- Use WebSockets for bidirectional real-time communication

## References

- Contributed from: C3 (Command, Control, Communications) server
- Part of Thierry's mission-control ecosystem
