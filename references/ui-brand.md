# Dominion Flow UI Brand Guide

> Visual patterns for consistent, recognizable user-facing output

---

## Stage Banners

Use stage banners to mark major workflow phases. Always use the Dominion Flow prefix for brand recognition.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                         DOMINION FLOW > DISCOVERY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Standard Stage Names

| Stage | Usage |
|-------|-------|
| `DOMINION FLOW > DISCOVERY` | Gathering requirements, exploring codebase |
| `DOMINION FLOW > PLANNING` | Creating execution plans |
| `DOMINION FLOW > EXECUTION` | Implementing changes |
| `DOMINION FLOW > VERIFICATION` | Testing and validation |
| `DOMINION FLOW > CHECKPOINT` | Mid-execution review points |
| `DOMINION FLOW > COMPLETE` | Task finished successfully |

### Compact Banner (for sub-stages)

```
━━━ DOMINION FLOW > BREATH 1 EXECUTION ━━━
```

---

## Checkpoint Boxes

Use checkpoint boxes for critical decision points and status summaries.

### Standard Checkpoint

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                              CHECKPOINT                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ✓ Database schema created                                                   ║
║  ✓ API routes implemented                                                    ║
║  ○ Frontend components pending                                               ║
║  ○ Tests not started                                                         ║
║                                                                              ║
║  Progress: ████████░░░░░░░░ 50%                                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Decision Checkpoint

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         DECISION REQUIRED                                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Issue: API response format inconsistent with frontend expectations          ║
║                                                                              ║
║  Options:                                                                    ║
║    A) Modify API to match frontend schema                                   ║
║    B) Update frontend to handle current API format                          ║
║    C) Create adapter layer                                                   ║
║                                                                              ║
║  Recommendation: Option A (lower complexity, single change point)           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Status Symbols

### Primary Symbols

| Symbol | Meaning | Usage |
|--------|---------|-------|
| `✓` | Complete/Success | Task finished, test passed |
| `✗` | Failed/Error | Task failed, test failed |
| `◆` | In Progress | Currently executing |
| `○` | Pending | Not yet started |
| `⚡` | Active/Running | Live process, spawned agent |
| `⚠` | Warning | Non-blocking issue |
| `🎉` | Celebration | Major milestone achieved |

### Secondary Symbols

| Symbol | Meaning | Usage |
|--------|---------|-------|
| `→` | Flow/Next | Indicates next step |
| `↳` | Sub-item | Nested task or detail |
| `│` | Vertical line | Tree structure |
| `├` | Branch | Tree branching |
| `└` | Last branch | Final item in tree |

### Usage Examples

```
✓ Build successful
✗ Test failed: authentication.spec.ts
◆ Running database migrations...
○ Deploy to staging (pending)
⚡ Agent spawned: code-review
⚠ Warning: No tests for new endpoint
🎉 Phase 3 Complete!
```

---

## Progress Display

### Standard Progress Bar

```
Progress: ████████████░░░░░░░░ 60%
```

### Detailed Progress

```
Overall: ████████████████░░░░ 80%
├─ Backend:   ████████████████████ 100%
├─ Frontend:  ████████████░░░░░░░░ 60%
└─ Tests:     ████████░░░░░░░░░░░░ 40%
```

### Progress with Context

```
Breath 2 of 4: ██████████░░░░░░░░░░ 50%
  Tasks: 3/6 complete
  Time: ~15 min remaining
```

---

## Spawning Indicators

Use when launching parallel agents or sub-processes.

### Agent Spawn

```
◆ Spawning agents for Breath 2...
  ⚡ Agent 1: Backend API implementation
  ⚡ Agent 2: Database schema updates
  ⚡ Agent 3: Test scaffolding
```

### Single Spawn

```
◆ Spawning code-review agent...
```

### Spawn Complete

```
✓ All agents spawned (3 active)
  ├─ ⚡ Agent 1: Running (backend)
  ├─ ⚡ Agent 2: Running (database)
  └─ ⚡ Agent 3: Running (tests)
```

---

## Next Up Blocks

Use to show upcoming work and maintain momentum.

### Simple Next Up

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ NEXT UP                                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  → Implement user authentication endpoint                                   │
│  → Add input validation middleware                                          │
│  → Create integration tests                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Next Up

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ NEXT UP: Breath 3                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Priority Tasks:                                                            │
│    1. [HIGH] Fix authentication token refresh                               │
│    2. [MED]  Add error boundary to dashboard                                │
│    3. [LOW]  Update loading spinners                                        │
│                                                                             │
│  Blocked:                                                                   │
│    - Payment integration (waiting on API keys)                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Error Boxes

Use for critical errors that need immediate attention.

### Standard Error

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ ✗ ERROR                                                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Build failed: TypeScript compilation error                                  ║
║                                                                              ║
║  Location: src/services/auth.service.ts:47                                  ║
║  Message: Property 'token' does not exist on type 'User'                    ║
║                                                                              ║
║  Action: Fix type definition before proceeding                              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Warning Box

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ⚠ WARNING                                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  No tests found for: src/components/Dashboard.tsx                           │
│                                                                             │
│  Recommendation: Add unit tests before merge                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Success/Completion Boxes

### Phase Complete

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ 🎉 PHASE COMPLETE                                                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Phase 2: Backend API Implementation                                         ║
║                                                                              ║
║  Achievements:                                                               ║
║    ✓ 12 API endpoints created                                               ║
║    ✓ Authentication middleware added                                         ║
║    ✓ 94% test coverage                                                       ║
║    ✓ Documentation generated                                                 ║
║                                                                              ║
║  Time: 2h 15m | Breaths: 4 | Agents Used: 8                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Anti-Patterns (Avoid These)

### DON'T: Inconsistent symbols

```
❌ Bad:
[x] Task complete
[DONE] Another task
* Third task done
```

```
✓ Good:
✓ Task complete
✓ Another task
✓ Third task done
```

### DON'T: Missing Dominion Flow branding

```
❌ Bad:
=== STARTING PHASE 2 ===
```

```
✓ Good:
━━━ DOMINION FLOW > PHASE 2 EXECUTION ━━━
```

### DON'T: Plain text errors

```
❌ Bad:
Error: Build failed
```

```
✓ Good:
╔══════════════════════════════════════════════════════════════════════════════╗
║ ✗ ERROR: Build failed                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### DON'T: Unclear progress

```
❌ Bad:
Working on it...
Almost done...
```

```
✓ Good:
Progress: ████████████░░░░░░░░ 60%
  ├─ ✓ Schema created
  ├─ ◆ Migrations running
  └─ ○ Seeding pending
```

### DON'T: Emoji overload

```
❌ Bad:
🚀 Starting! 💪 Let's go! 🎯 Targeting API! 🔥 Hot fixes!
```

```
✓ Good:
━━━ DOMINION FLOW > EXECUTION ━━━
◆ Implementing API endpoints...
```

### DON'T: Inconsistent box styles

```
❌ Bad:
+------------------+
| Some content     |
+------------------+

[Another Box]
| Different style |
```

```
✓ Good:
┌─────────────────────────────────────────────────────────────────────────────┐
│ Standard content box                                                        │
└─────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║ Important/checkpoint box                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Quick Reference

| Element | Character Set |
|---------|--------------|
| Stage banners | `━` (heavy horizontal) |
| Checkpoint boxes | `╔ ╗ ╚ ╝ ║ ═ ╠ ╣` (double line) |
| Standard boxes | `┌ ┐ └ ┘ │ ─ ├ ┤` (single line) |
| Progress fill | `█` (full block) |
| Progress empty | `░` (light shade) |
| Tree structure | `│ ├ └ ─` |

---

*Consistent branding builds trust and recognition. Every Dominion Flow output should be immediately identifiable.*
