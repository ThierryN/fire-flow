# Execution Progress Monitor & Heartbeat

> Real-time progress tracking for long-running autonomous sessions with timeout enforcement and health checks.

**When to use:** During `/fire-autonomous` runs, long `/fire-3-execute` sessions, or any multi-phase execution that runs 30+ minutes.

---

## Progress File Pattern

Write a progress file that any external tool can read:

```javascript
// .planning/execution-progress.json
{
  "session_id": "auto-2026-03-09-1430",
  "started_at": "2026-03-09T14:30:00Z",
  "last_heartbeat": "2026-03-09T14:45:23Z",
  "status": "executing",  // executing | verifying | reviewing | blocked | completed
  "current_phase": 3,
  "total_phases": 7,
  "current_task": "Implementing cart checkout API",
  "progress": {
    "phases_completed": 2,
    "phases_remaining": 5,
    "current_phase_progress": 0.6,  // 60% of current phase
    "tasks_completed": 12,
    "tasks_total": 20
  },
  "agents": {
    "active": 2,
    "completed": 5,
    "failed": 0,
    "names": ["executor-backend", "executor-frontend"]
  },
  "metrics": {
    "elapsed_seconds": 923,
    "estimated_remaining_seconds": 1500,
    "tokens_used": 45000,
    "tool_calls": 89
  },
  "last_event": "Completed breath 2 of phase 3 — 4 tasks done, 3 remaining",
  "errors": []
}
```

---

## Heartbeat Integration in fire-3-execute

Add heartbeat updates at key points during execution:

```markdown
### Heartbeat Protocol

Update `.planning/execution-progress.json` at these events:

1. **Phase start:** status = "executing", current_phase = N
2. **Breath complete:** Update current_phase_progress, tasks_completed
3. **Agent spawn:** Increment agents.active, add to agents.names
4. **Agent complete:** Decrement agents.active, increment agents.completed
5. **Agent failure:** Increment agents.failed, add to errors
6. **Verification start:** status = "verifying"
7. **Review start:** status = "reviewing"
8. **Phase complete:** Increment phases_completed
9. **Blocker:** status = "blocked", add to errors
10. **Session end:** status = "completed"

Always update `last_heartbeat` timestamp on every write.
```

---

## Timeout Enforcement

```markdown
### Per-Agent Timeout

When spawning any agent (executor, reviewer, verifier):

  timeout = agent_type == "executor" ? 10 minutes
          : agent_type == "reviewer" ? 5 minutes
          : agent_type == "verifier" ? 5 minutes
          : 3 minutes  # default

  IF agent does not return within timeout:
    1. Log timeout to execution-progress.json errors
    2. Mark agent as failed
    3. Continue with remaining agents (don't block on hung agent)
    4. If critical agent (executor), trigger circuit breaker

### Session Timeout

  max_session_duration = 60 minutes (configurable)

  IF elapsed_seconds > max_session_duration:
    1. Complete current agent (don't interrupt mid-task)
    2. Save progress to execution-progress.json
    3. Create WARRIOR handoff with resume point
    4. Display: "Session timeout — use /fire-autonomous --from-phase {N} to resume"
```

---

## Status Display Command

Read the progress file and display human-readable status:

```markdown
### Progress Display (for /fire-dashboard integration)

Read .planning/execution-progress.json and display:

┌──────────────────────────────────────────────┐
│ EXECUTION PROGRESS                            │
├──────────────────────────────────────────────┤
│ Phase: 3/7 — Cart Checkout API                │
│ Progress: ████████████░░░░░░░░ 60%            │
│ Tasks: 12/20 completed                        │
│ Active agents: 2 (executor-backend, frontend) │
│ Elapsed: 15m 23s | ETA: ~25m                  │
│ Last: Completed breath 2 — 4 tasks done       │
│ Health: ✓ (heartbeat 3s ago)                  │
└──────────────────────────────────────────────┘

IF last_heartbeat > 2 minutes ago:
  Display: "⚠ Heartbeat stale (last update {N}s ago) — agent may be stuck"

IF errors.length > 0:
  Display: "Errors: {errors.length} — {errors[0]}"
```

---

## Kill Switch

```markdown
### Emergency Stop

Create `.planning/.stop-execution` file to signal graceful shutdown:

  IF file_exists('.planning/.stop-execution'):
    1. Finish current task (don't abandon mid-write)
    2. Save progress
    3. Create handoff
    4. Delete .stop-execution file
    5. Display: "Execution stopped by kill switch"

Alternative: Ctrl+C or /fire-loop-stop
```

---

## Sources

- Internal gap analysis: GAP-AGENT-5 (Progress Monitor/Heartbeat)
- Anthropic: Agent Teams progress tracking patterns (2026)
