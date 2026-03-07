---
name: shell-autonomous-loop-fixplan
category: methodology
version: 1.0.0
contributed: 2026-03-04
contributor: dominion-flow-v2
last_updated: 2026-03-04
tags: [autonomous, shell-loop, fix_plan, circuit-breaker, session-management, context-limits, ralph-pattern]
difficulty: hard
usage_count: 0
success_rate: 100
---

# Shell-Level Autonomous Loop with @fix_plan.md

## Problem

Conversation-level autonomous loops (`/fire-loop`, while-loops inside a single Claude session)
degrade over time: context fills up, the model loses track of early decisions, and performance
drops. For long-running tasks (10+ iterations, multi-phase builds, complex debugging), the loop
**must** run at the shell level — spawning fresh Claude CLI sessions per iteration while
preserving task continuity through a persistent task file.

**Symptoms of the conversation-loop problem:**
- AI starts repeating work it already did
- Circuit breaker fires due to output decline (context is full, responses get shorter)
- Task list lives only in conversation — lost on restart
- No rate limiting — hits API limits unexpectedly
- Can't reattach to a running loop after terminal disconnect

## Solution Pattern

Implement a **bash loop** that spawns `claude --resume <session_id>` on each iteration.
The AI reads `@fix_plan.md` (a persistent markdown checklist on disk) at the start of
every fresh session, does one task, checks it off, and writes `EXIT_SIGNAL=true` when done.
The shell script detects this signal and exits cleanly.

**Key insight from bmalph/Ralph:** The shell owns the loop. Claude owns the task.
The `@fix_plan.md` file is the shared state between them — it survives context resets,
restarts, disconnects, and rate limit cooldowns.

### The Three-Layer Architecture

```
SHELL LAYER (bash script)
  ├── Rate limiting (MAX_CALLS_PER_HOUR)
  ├── Session management (--resume <id>, expiry after 24h)
  ├── Circuit breaker (stagnation / error / output-decline)
  └── EXIT_SIGNAL + BLOCKED_TASK detection

TASK LAYER (@fix_plan.md on disk)
  ├── [ ] TASK-001: ... AC: ...
  ├── [x] TASK-002: ... (completed)
  └── EXIT_SIGNAL=false → EXIT_SIGNAL=true when done

CLAUDE LAYER (fresh session each iteration)
  ├── Reads @fix_plan.md + PROJECT_CONTEXT.md
  ├── Works on next unchecked task
  ├── Checks it off [x]
  └── Writes EXIT_SIGNAL=true when all done
```

## Code Example

### @fix_plan.md format

```markdown
# @fix_plan — My Project

> AI: Read this at the start of every iteration. Check off completed tasks [x].
> When ALL tasks are checked, write EXIT_SIGNAL=true.

## Phase 1 — Schema

- [ ] TASK-001: Create user table migration
  - AC: `npm run db:migrate` runs without errors
  - Files: prisma/schema.prisma, migrations/

- [ ] TASK-002: Add email + created_at indexes
  - AC: `EXPLAIN` shows index usage on user queries
  - Files: prisma/schema.prisma

## Phase 2 — API

- [ ] TASK-003: Build POST /api/users endpoint
  - AC: Returns 201 + user object, Playwright smoke passes
  - Files: src/routes/users.ts, src/controllers/users.ts

---

EXIT_SIGNAL=false

<!--
  AI: Check boxes [ ] → [x] as you complete tasks.
  If BLOCKED: write BLOCKED_TASK=TASK-NNN on its own line, then
  Reason: [what you tried and why you're stuck]
  When all [x]: change EXIT_SIGNAL=false → EXIT_SIGNAL=true
-->
```

### dominion_loop.sh (core loop)

```bash
#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
MAX_CALLS_PER_HOUR="${MAX_CALLS_PER_HOUR:-50}"
MAX_ITERATIONS="${MAX_ITERATIONS:-100}"
CIRCUIT_STAGNATION_LIMIT="${CIRCUIT_STAGNATION_LIMIT:-3}"
CIRCUIT_ERROR_LIMIT="${CIRCUIT_ERROR_LIMIT:-5}"
SESSION_EXPIRY_SECS="${SESSION_EXPIRY_SECS:-86400}"

FIX_PLAN="$PROJECT_DIR/.planning/@fix_plan.md"
SESSION_FILE="$PROJECT_DIR/.planning/.loop-session"

# Load per-project config override
[ -f "$PROJECT_DIR/.planning/dominion.rc" ] && source "$PROJECT_DIR/.planning/dominion.rc"

count_checked() { grep -c '^\- \[x\]' "$FIX_PLAN" 2>/dev/null || echo 0; }

SESSION_ID=""
if [ -f "$SESSION_FILE" ]; then
  SESSION_ID=$(jq -r '.sessionId // empty' "$SESSION_FILE" 2>/dev/null || echo "")
  SESSION_AGE=$(( $(date +%s) - $(jq -r '.createdAt // 0' "$SESSION_FILE" 2>/dev/null) ))
  [ "$SESSION_AGE" -gt "$SESSION_EXPIRY_SECS" ] && SESSION_ID="" && rm -f "$SESSION_FILE"
fi

CALL_WINDOW_START=$(date +%s)
CALLS_THIS_WINDOW=0
CB_STAGNATION=0
CB_ERRORS=0
CB_LAST_CHECKED=0
ITERATION=0

PROMPT="Read .planning/@fix_plan.md and .planning/PROJECT_CONTEXT.md.
Work on the next unchecked task [ ]. Update it to [x] when done.
If BLOCKED after genuine attempts: write BLOCKED_TASK=TASK-NNN then Reason: [why].
When ALL tasks are [x]: write EXIT_SIGNAL=true in @fix_plan.md."

while [ "$ITERATION" -lt "$MAX_ITERATIONS" ]; do
  ITERATION=$(( ITERATION + 1 ))
  CHECKED=$(count_checked)

  # Rate limiting
  NOW=$(date +%s); ELAPSED=$(( NOW - CALL_WINDOW_START ))
  [ "$ELAPSED" -ge 3600 ] && { CALL_WINDOW_START=$NOW; CALLS_THIS_WINDOW=0; }
  [ "$CALLS_THIS_WINDOW" -ge "$MAX_CALLS_PER_HOUR" ] && { sleep $(( 3600 - ELAPSED )); CALL_WINDOW_START=$(date +%s); CALLS_THIS_WINDOW=0; }
  CALLS_THIS_WINDOW=$(( CALLS_THIS_WINDOW + 1 ))

  # Build and run claude command
  RESUME_FLAG=""; [ -n "$SESSION_ID" ] && RESUME_FLAG="--resume $SESSION_ID"
  TMPOUT=$(mktemp)
  HAD_ERROR="false"

  # shellcheck disable=SC2086
  claude --output-format json \
    --allowedTools 'Write,Read,Edit,Glob,Grep,Bash,Task,TodoWrite,WebSearch,WebFetch' \
    $RESUME_FLAG -p "$PROMPT" > "$TMPOUT" 2>&1 || HAD_ERROR="true"

  # Capture session ID on first run
  if [ -z "$SESSION_ID" ]; then
    SID=$(jq -r '.sessionId // empty' "$TMPOUT" 2>/dev/null || echo "")
    [ -n "$SID" ] && SESSION_ID="$SID" && printf '{"sessionId":"%s","createdAt":%s}' "$SID" "$(date +%s)" > "$SESSION_FILE"
  fi

  # Check exit conditions
  grep -q 'EXIT_SIGNAL=true' "$FIX_PLAN" 2>/dev/null && { echo "✓ Done."; rm -f "$TMPOUT"; exit 0; }

  if grep -q 'BLOCKED_TASK=' "$TMPOUT" 2>/dev/null; then
    BLOCKED=$(grep 'BLOCKED_TASK=' "$TMPOUT" | head -1)
    printf '{"blocked":true,"task":"%s","iteration":%s}' "$BLOCKED" "$ITERATION" > "$PROJECT_DIR/.planning/loop-blocked.json"
    echo "⚠ BLOCKED: $BLOCKED"; rm -f "$TMPOUT"; exit 2
  fi

  # Circuit breaker
  NEW_CHECKED=$(count_checked)
  [ "$NEW_CHECKED" -le "$CB_LAST_CHECKED" ] && CB_STAGNATION=$(( CB_STAGNATION + 1 )) || { CB_STAGNATION=0; CB_LAST_CHECKED=$NEW_CHECKED; }
  [ "$HAD_ERROR" = "true" ] && CB_ERRORS=$(( CB_ERRORS + 1 )) || CB_ERRORS=0
  [ "$CB_STAGNATION" -ge "$CIRCUIT_STAGNATION_LIMIT" ] && { echo "⚡ Stagnation. Cooling down 30m."; sleep 1800; CB_STAGNATION=0; }
  [ "$CB_ERRORS" -ge "$CIRCUIT_ERROR_LIMIT" ] && { echo "⚡ Error limit. Halting."; exit 1; }

  rm -f "$TMPOUT"; sleep 2
done
exit 1
```

## Implementation Steps

1. **Generate @fix_plan.md** — run `/fire-implement` (or manually write tasks with `- [ ] TASK-NNN:` format + `AC:` acceptance criteria)
2. **Generate PROJECT_CONTEXT.md** — consolidated planning docs in one file the AI reads per iteration
3. **Copy dominion.rc** — set `MAX_CALLS_PER_HOUR`, `MAX_ITERATIONS`, circuit breaker thresholds
4. **Run the loop** — `bash dominion_loop.sh --project-dir $(pwd)` or via `/fire-loop`
5. **Monitor** — `cat .planning/loop-status.json` or `/fire-dashboard`
6. **Handle BLOCKED** — loop exits code 2, read `.planning/loop-blocked.json`, invoke researcher

## When to Use

- Task requires >10 AI iterations to complete
- Multi-phase feature build (schema → API → UI → tests)
- Long-running autonomous execution where context bloat is a real risk
- You want rate limiting and circuit breaking enforced at the OS level
- Task must survive terminal disconnects or restarts
- You need a reattachable, resumable execution that persists across sessions

## When NOT to Use

- Simple 1-3 iteration tasks (conversation loop is fine)
- No `claude` CLI available in PATH
- Task requires continuous human judgment at each step (use manual `/fire-3-execute`)
- Project has no `.planning/` structure yet (run `/fire-1a-new` first)

## Common Mistakes

- **Vague acceptance criteria** — if AC is unclear, AI marks tasks done prematurely. Write AC as a testable command: `npm test passes`, `Playwright smoke green`, `tsc --noEmit returns 0`
- **Too many tasks per @fix_plan.md** — keep tasks 15-30 min each. Huge tasks cause stagnation (CB fires before completion)
- **Missing PROJECT_CONTEXT.md** — without it, each fresh session lacks planning context and the AI reinvents decisions. Always run `/fire-implement` to generate it
- **Forgetting exit code 2** — if your orchestrator calls the loop, check exit code 2 = BLOCKED (needs researcher), not just 0 = done and 1 = error

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | `EXIT_SIGNAL=true` — all tasks complete | Proceed to verification |
| 1 | Circuit breaker halt or max iterations | Investigate `.planning/loop-status.json` |
| 2 | `BLOCKED_TASK` detected | Read `.planning/loop-blocked.json`, invoke researcher |

## Related Skills

- [autonomous-multi-phase-build](autonomous-multi-phase-build.md) — phase-level orchestration within conversation
- [multi-project-autonomous-build](multi-project-autonomous-build.md) — running multiple projects autonomously

## References

- Inspired by: [bmalph](https://github.com/LarsCowe/bmalph) — Ralph autonomous loop pattern
- Ralph loop architecture: `ralph_loop.sh` in bmalph v2.7.0
- Gap analysis session: 2026-03-04 fire-flow-v2 implementation
- Contributed from: dominion-flow-v2 build session
