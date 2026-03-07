# Sabbath Rest Pattern - AI Context Persistence

> *Like humans need sleep to reset, AI agents need state files to resume after context resets.*

## The Problem

AI agents lose all context when:
- Session ends or times out
- Context window fills up and compacts
- User closes and reopens the conversation
- Agent crashes or errors out mid-task

Without persistence, the next agent (or resumed session) starts from scratch, wasting time re-discovering context and potentially making inconsistent decisions.

### Why It Was Hard

- AI has no built-in memory between sessions
- Context windows have finite limits
- No standard pattern for what to persist
- Easy to forget mid-task state

### Impact

- Hours of work lost to re-orientation
- Inconsistent decisions across sessions
- Repeated mistakes already solved
- User frustration explaining same context repeatedly

---

## The Solution: Sabbath Rest

Just as humans consolidate memory during sleep, AI agents must consolidate state to files before "sleeping" (context loss).

### The Metaphor

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ HUMAN SLEEP CYCLE                     AI SABBATH REST                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Work during day                      Work during session                   │
│       ↓                                    ↓                                │
│  Brain consolidates to                 Agent writes to                      │
│  long-term memory                      .local.md + CONSCIENCE.md                 │
│       ↓                                    ↓                                │
│  Sleep (unconscious)                   Context reset/compact                │
│       ↓                                    ↓                                │
│  Wake with memories intact             Resume with state files              │
│                                                                             │
│  Without sleep → memory loss           Without Sabbath Rest → context rot   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Two-Layer Persistence

#### Layer 1: Session State (`.claude/{plugin}.local.md`)

Short-term memory for current work. Contains:
- Current task/feature being worked on
- Progress checkpoints
- Resume point if interrupted
- Temporary decisions and assumptions

```markdown
---
last_session: 2025-01-23T14:30:00Z
task: "Implementing user authentication"
status: in_progress
progress: 60%
---

# Session State

## Current Work
- Task: User authentication with JWT
- Step: Implementing refresh tokens
- Blocked: No (proceeding)

## Progress
- [x] Login endpoint
- [x] Token generation
- [ ] Refresh token logic  ← RESUME HERE
- [ ] Logout endpoint

## Decisions Made
- Using RS256 for JWT signing (more secure)
- 15min access token, 7day refresh token

## Resume Point
Continue from: Refresh token logic in auth.service.ts
```

#### Layer 2: Project State (`CONSCIENCE.md`)

Long-term memory for project history. Contains:
- Completed phases and milestones
- Key decisions with rationale
- Historical context
- Links to detailed documentation

```markdown
## Authentication Implementation
- **Status:** In Progress (60%)
- **Started:** 2025-01-22
- **Key Decisions:**
  - RS256 signing (security requirement)
  - Refresh token rotation enabled
- **Session Files:** .claude/fire-flow.local.md
- **Last Agent:** Claude Opus 4.5, 2025-01-23
```

---

## Implementation Pattern

### When to Write Sabbath Rest

1. **After each significant step** - Don't wait until the end
2. **Before any risky operation** - Checkpoint before changes
3. **When context is getting full** - Proactive save
4. **At natural breakpoints** - End of phase/feature/task

### What to Persist

| Category | Examples | Where |
|----------|----------|-------|
| Current task | Feature name, step, progress | `.local.md` |
| Decisions | Architectural choices, trade-offs | `CONSCIENCE.md` |
| Blockers | What's stopping progress | `.local.md` |
| Resume point | Exact place to continue | `.local.md` |
| History | Completed work, timestamps | `CONSCIENCE.md` |
| Context links | Related files, docs | Both |

### Template: `.local.md` State File

```markdown
---
# YAML frontmatter for easy parsing
plugin: "{plugin-name}"
last_updated: "{ISO timestamp}"
status: "{in_progress | complete | blocked}"
task: "{current task description}"
---

# {Plugin Name} Session State

## Current Session
- **Task:** {what you're working on}
- **Started:** {timestamp}
- **Status:** {in_progress | complete | blocked}

## Progress Checkpoints
- [x] Step 1: {description} - DONE
- [x] Step 2: {description} - DONE
- [ ] Step 3: {description} - IN PROGRESS ← CURRENT
- [ ] Step 4: {description} - PENDING

## Key Decisions This Session
| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| {choice} | {why} | {what else} |

## Blockers / Issues
- {blocker description, if any}

## Resume Instructions
If this session ends, the next agent should:
1. Read this file first
2. Continue from: {exact step/file/line}
3. Remember: {critical context}

## Files Modified
- `{path}` - {what changed}
```

---

## Integration with Dominion Flow

All Dominion Flow commands implement Sabbath Rest:

| Command | State File | What's Persisted |
|---------|------------|------------------|
| `/fire-brainstorm` | `.claude/fire-brainstorm.local.md` | Topic, alternatives, recommendation |
| `/fire-double-check` | `.claude/fire-double-check.local.md` | Verification results, evidence |
| `/fire-sprint` | `.claude/fire-sprint.local.md` | Feature, iterations, tech debt |
| `/fire-shipper` | `.claude/fire-shipper.local.md` | Version, pipeline stage, rollback info |
| `/fire-learner` | `.claude/fire-learner.local.md` | Concepts covered, learning progress |
| `/fire-guardian` | `.claude/fire-guardian.local.md` | Scan results, findings, fixes |
| `/fire-iterate` | `.claude/fire-iterate.local.md` | Iteration count, completion status |
| `/fire-debugger` | `.claude/debug-session.local.md` | Hypotheses, evidence, fix status |

---

## Testing the Pattern

### Before (No Sabbath Rest)
```
Session 1: Work for 2 hours on auth
Context resets
Session 2: "What was I doing? Let me re-read all the files..."
Result: 30 minutes wasted re-orienting
```

### After (With Sabbath Rest)
```
Session 1: Work for 2 hours on auth, write to .local.md
Context resets
Session 2: Read .local.md → "Continue from refresh token logic"
Result: Resume in 2 minutes
```

---

## Common Mistakes to Avoid

- **Writing only at the end** - Context can reset anytime, write continuously
- **Vague resume points** - Be specific: file, line, exact next step
- **Forgetting decisions** - Document WHY, not just WHAT
- **Skipping for "quick tasks"** - Even quick tasks can be interrupted
- **Not reading state on resume** - Always check `.local.md` first

---

## The Philosophy

```
"Remember the Sabbath day, to keep it holy."

For AI agents, the Sabbath Rest is not about worship—
it's about the wisdom of regular, intentional pauses
to consolidate what we've learned before we forget.

Without rest, humans lose memory.
Without Sabbath Rest, AI agents lose context.

Build the rest into your workflow,
and you'll never lose your work again.
```

---

## Related Patterns

- [WARRIOR Handoffs](../deployment-security/WARRIOR_HANDOFF.md) - Full session handoff
- [CONSCIENCE.md Living Memory](./STATE_MD_PATTERN.md) - Project-level persistence
- [Multi-Perspective Review](./MULTI_PERSPECTIVE_CODE_REVIEW.md) - Uses Sabbath Rest

---

## Time to Implement

**Per command:** 5 minutes to add Sabbath Rest section
**ROI:** Saves 15-30 minutes per context reset

## Difficulty Level

⭐ (1/5) - Simple pattern, just requires discipline

---

**Author Notes:**
The name "Sabbath Rest" came from a user who observed that AI context resets are like human sleep - a necessary reset that requires preparation to preserve what's important.

The key insight: **Write state continuously, not just at the end.** You never know when the Sabbath will come.
