# Error Classification Layer

> State machine that classifies execution health into PROGRESS / STALLED / SPINNING / DEGRADED / BLOCKED — each state drives different automated responses.

---

## Overview

Instead of treating all problems the same way ("try again"), the Error Classification Layer assigns a **health state** to the current execution and triggers **state-specific responses**. This prevents the common failure mode where an agent keeps retrying the same broken approach.

**Core principle:** Different problems need different responses. Classify first, then act.

---

## Five Health States

```
┌────────────┐    no progress     ┌──────────┐   same error    ┌──────────┐
│  PROGRESS  │──────────────────►│  STALLED  │──────────────►│ SPINNING │
│            │                    │           │                │          │
│ Making     │                    │ No forward│                │ Repeating│
│ measurable │                    │ movement  │                │ same     │
│ progress   │                    │           │                │ error    │
└─────┬──────┘                    └─────┬─────┘                └─────┬────┘
      │                                 │                            │
      │ context filling                 │ external dep               │ 5th repeat
      │                                 │                            │
      ▼                                 ▼                            ▼
┌────────────┐                    ┌──────────┐              ┌──────────────┐
│  DEGRADED  │                    │ BLOCKED  │              │ CIRCUIT BREAK│
│            │                    │          │              │              │
│ Context rot│                    │ External │              │ Hard stop    │
│ declining  │                    │ blocker  │              │ from breaker │
│ output     │                    │ can't    │              │              │
│ quality    │                    │ proceed  │              │              │
└────────────┘                    └──────────┘              └──────────────┘
```

---

## State Definitions

### PROGRESS

**Signals:**
- Files are being modified between iterations
- Test results are changing (even if still failing — different failures = progress)
- New errors replacing old ones (moving forward through the problem)
- Output remains detailed and focused

**Response:** Continue normally. No intervention needed.

```
classify_as_progress():
  files_changed_this_iteration > 0
  OR error_hash != previous_error_hash
  OR test_count_changed
  OR new_files_created
```

### STALLED

**Signals:**
- No file changes for 2+ iterations
- Same test results (no change in pass/fail counts)
- Agent is reading files but not writing
- Output shows analysis but no action

**Response:**
1. Inject urgency: "You have not made file changes in {N} iterations"
2. Suggest concrete next action
3. Search skills library for alternative approaches
4. If persists 3+ iterations → escalate to SPINNING or BLOCKED

```
classify_as_stalled():
  files_changed == 0 for 2+ iterations
  AND no new errors (same or no errors)
  AND output_is_analytical (reading, exploring, but not writing)
```

### SPINNING

**Signals:**
- Same error appearing 3+ times
- Agent is making changes but they don't fix the issue
- Cycle: change file → run test → same error → change file → same error
- Git log shows repeated edits to same files

**Response:**
1. **Approach rotation** (forced): "You have seen this error {N} times. You MUST try a fundamentally different approach."
2. Display error history: "Here are the {N} approaches you've already tried"
3. Inject anti-patterns: "Do NOT do: {list of failed approaches}"
4. Search skills library for the specific error pattern
5. If persists after rotation → CIRCUIT BREAK

```
classify_as_spinning():
  same_error_hash for 3+ iterations
  AND files_changed > 0 (agent IS trying, but failing)
```

### DEGRADED

**Signals:**
- Output volume declining (50%+ below baseline)
- Responses becoming shorter, less structured
- Agent forgetting earlier instructions or context
- Repetitive phrasing or circular logic
- Loss of formatting quality

**Response:**
1. Trigger Sabbath Rest warning
2. Save complete state to loop file
3. Recommend fresh context restart
4. If user forces continue → operate in "minimal mode" (short, focused actions only)

```
classify_as_degraded():
  output_volume < 50% of baseline
  OR response_length_declining for 3+ iterations
  OR instruction_amnesia_detected (re-asking clarified questions)
```

### BLOCKED

**Signals:**
- Error requires external action (missing env var, service down, permission needed)
- Dependency not installed and can't be auto-installed
- API rate limit hit
- File/resource locked by another process
- Requires human decision that wasn't planned for

**Response:**
1. **Stop immediately** — don't waste iterations
2. Classify the blocker (external dependency, permission, decision needed)
3. Create blocker entry in BLOCKERS.md
4. Save state for resume
5. Present clear options to user

```
classify_as_blocked():
  error_type IN [
    "EACCES", "EPERM",           # Permission
    "ECONNREFUSED",              # Service down
    "MODULE_NOT_FOUND",          # Missing dependency
    "rate_limit_exceeded",       # API limit
    "ENOENT" on external resource # Missing external file
  ]
  OR error_message contains ["permission denied", "not authorized",
     "service unavailable", "rate limit", "quota exceeded"]
```

---

## Classification Algorithm

Run this after each iteration/task:

```
classify_health(iteration_data):
  # Priority order: BLOCKED > SPINNING > DEGRADED > STALLED > PROGRESS
  # Higher-severity states take precedence

  # 1. Check for external blockers first
  IF is_external_blocker(iteration_data.error):
    RETURN BLOCKED

  # 2. Check for spinning (same error, agent IS trying)
  IF same_error_count >= 3 AND files_changed_recently:
    RETURN SPINNING

  # 3. Check for degradation (context rot)
  IF output_volume_decline >= 50%:
    RETURN DEGRADED

  # 4. Check for stalling (no progress, no errors)
  IF no_file_changes >= 2 AND no_new_errors:
    RETURN STALLED

  # 5. Default: making progress
  RETURN PROGRESS
```

---

## State Transition Rules

| From | To | Trigger | Auto-Action |
|------|----|---------|-------------|
| PROGRESS | STALLED | 2 iterations no file changes | Inject urgency prompt |
| PROGRESS | DEGRADED | Output drops 50%+ | Sabbath Rest warning |
| PROGRESS | BLOCKED | External error detected | Stop + blocker report |
| STALLED | SPINNING | Same error appears 3x | Force approach rotation |
| STALLED | PROGRESS | Files change again | Clear warning state |
| STALLED | BLOCKED | External error detected | Stop + blocker report |
| SPINNING | CIRCUIT BREAK | 5th same error | Hard stop via circuit breaker |
| SPINNING | PROGRESS | Different error or files change | Clear spin counter |
| DEGRADED | SABBATH REST | Output drops 70%+ | Auto-save + pause |
| DEGRADED | PROGRESS | Output recovers (unlikely) | Clear degradation flag |
| BLOCKED | PROGRESS | Blocker resolved | Resume from checkpoint |

---

## Response Templates

### STALLED Response Injection

```markdown
---
HEALTH CHECK: STALLED (iteration {N})
---

No file changes detected for {count} iterations.

Your recent actions:
- [iter N-2]: Read src/auth.ts, read src/utils.ts
- [iter N-1]: Read src/models/user.ts, ran tests
- [iter N]: Read src/middleware/auth.ts

You are in analysis mode. To make progress, you must:
1. Pick ONE specific change to make
2. Make the change
3. Test it

Suggested actions from skills library:
- {skill_suggestion_1}
- {skill_suggestion_2}
---
```

### SPINNING Response Injection

```markdown
---
HEALTH CHECK: SPINNING (iteration {N})
---

SAME ERROR seen {count} times:
  {normalized_error_message}

Approaches already tried (DO NOT REPEAT):
  1. [iteration X]: {approach_1} → FAILED
  2. [iteration Y]: {approach_2} → FAILED
  3. [iteration Z]: {approach_3} → FAILED

You MUST try a fundamentally different approach.

Consider:
- Instead of fixing WHERE the error appears, fix WHERE the bad data originates
- Instead of patching the consumer, fix the producer
- Instead of adding null checks, ensure non-null at the source
- Check skills library for this error pattern

If you cannot think of a new approach, explain what you've learned
and request help from the user.
---
```

### BLOCKED Response Display

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ EXECUTION BLOCKED                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Blocker Type: [External Dependency | Permission | Decision | Service]      │
│  Error: {error_message}                                                     │
│                                                                             │
│  This error requires action outside the loop:                               │
│    {specific_action_needed}                                                 │
│                                                                             │
│  State saved to: .planning/loops/fire-loop-{ID}.md                        │
│  Resume with: /fire-loop-resume {ID}                                       │
│                                                                             │
│  Added to BLOCKERS.md as BLOCKER-{NNN} [P{priority}]                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tracking in Loop File

```markdown
## Health Classification History

| Iteration | State | Trigger | Action Taken |
|-----------|-------|---------|-------------|
| 1 | PROGRESS | Files changed: 3 | - |
| 2 | PROGRESS | New error (different from iter 1) | - |
| 3 | PROGRESS | Files changed: 2 | - |
| 4 | STALLED | No file changes | Urgency injection |
| 5 | STALLED | No file changes (2nd) | Skills search |
| 6 | SPINNING | Same error 3x | Approach rotation |
| 7 | PROGRESS | Different approach, new error | Cleared spin state |
| 8 | PROGRESS | Files changed: 4 | - |
```

---

## Integration with Circuit Breaker

Error Classification and Circuit Breaker work together:

```
Error Classification → diagnoses WHAT is happening
Circuit Breaker      → enforces WHEN to stop

Example flow:
  1. Error Classification detects SPINNING state
  2. Injects approach rotation prompt
  3. Circuit Breaker tracks: same_error_count = 3 (WARNING)
  4. If rotation doesn't work: same_error_count = 5 (BREAK)
  5. Circuit Breaker triggers hard stop
```

---

## References

- **Inspiration:** Manus AI error preservation, Replit Agent doom loop detection
- **Related:** `references/circuit-breaker.md` — quantitative thresholds
- **Related:** `references/honesty-protocols.md` — "admit when stuck" principle
- **Consumer:** `commands/fire-loop.md` — primary integration point
- **Consumer:** `commands/fire-debug.md` — debug session health tracking
