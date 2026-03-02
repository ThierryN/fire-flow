# Quantitative Circuit Breaker

> Hard numerical thresholds that detect when loops are spinning, stalling, or degrading — inspired by frankbria's Ralph loop fork and Manus error preservation.

---

## Overview

The Sabbath Rest system detects context rot through subjective signals. The Circuit Breaker adds **quantitative, measurable thresholds** that trigger automatically — no judgment calls needed. It measures three dimensions: file changes, error repetition, and output volume.

**Core principle:** If the numbers say you're stuck, you're stuck — even if it doesn't feel that way.

---

## Three Thresholds

### 1. No File Changes (Stall Detection)

```
THRESHOLD: NO_FILE_CHANGES
  trigger: 3 consecutive iterations with zero file modifications
  severity: WARNING after 3, BREAK after 5
  response: Force approach rotation

  measure():
    files_changed = git diff --stat HEAD~1 (after each iteration)
    IF files_changed == 0:
      stall_counter++
    ELSE:
      stall_counter = 0

    IF stall_counter >= 3:
      RETURN WARNING: "No file changes in 3 iterations"
    IF stall_counter >= 5:
      RETURN BREAK: "No file changes in 5 iterations — stopping"
```

**Why this matters:** If code isn't changing, nothing is happening. The agent may be reading files, thinking, but not actually producing work.

### 2. Same Error Hash (Spin Detection)

```
THRESHOLD: SAME_ERROR_HASH
  trigger: Same error signature appears 5 times
  severity: WARNING after 3, BREAK after 5
  response: Force different approach, escalate to user

  measure():
    error_hash = hash(normalize(error_message))
    error_history[error_hash]++

    IF error_history[error_hash] >= 3:
      RETURN WARNING: "Same error seen 3 times"
    IF error_history[error_hash] >= 5:
      RETURN BREAK: "Same error 5 times — current approach is not working"

  normalize(error):
    # Strip line numbers, timestamps, dynamic values
    # Keep error type, message pattern, file reference
    stripped = remove_line_numbers(error)
    stripped = remove_timestamps(stripped)
    stripped = remove_dynamic_ids(stripped)
    RETURN stripped
```

**Error hash normalization examples:**

| Raw Error | Normalized | Hash |
|-----------|-----------|------|
| `TypeError: Cannot read property 'id' of undefined at line 42` | `TypeError: Cannot read property * of undefined at *` | `a3f2...` |
| `TypeError: Cannot read property 'name' of undefined at line 88` | `TypeError: Cannot read property * of undefined at *` | `a3f2...` (same!) |
| `ECONNREFUSED 127.0.0.1:5432` | `ECONNREFUSED *:5432` | `b7c1...` |

### 3. Output Volume Decline (Degradation Detection)

```
THRESHOLD: OUTPUT_DECLINE
  trigger: Output volume drops >70% from initial iterations
  severity: WARNING after 50% decline, BREAK after 70%
  response: Trigger Sabbath Rest — context is exhausted

  measure():
    current_output_lines = count_lines(iteration_output)
    baseline = average(first_3_iterations_output_lines)

    decline_pct = (baseline - current_output_lines) / baseline * 100

    IF decline_pct >= 50:
      RETURN WARNING: "Output volume 50% below baseline"
    IF decline_pct >= 70:
      RETURN BREAK: "Output volume 70% below baseline — context exhausted"
```

**Why this matters:** When context fills up, Claude produces shorter, less detailed responses. This is a measurable proxy for context rot.

---

## Circuit Breaker State Machine

```
                    ┌──────────┐
                    │  HEALTHY │ ◄── All counters at 0
                    └────┬─────┘
                         │
                    Any WARNING threshold
                         │
                    ┌────▼─────┐
                    │ WARNING  │ ◄── Counter(s) approaching limit
                    └────┬─────┘
                         │
                    ├── User says CONTINUE → reset warning, continue
                    │
                    ├── Auto-action: rotate approach
                    │
                    Any BREAK threshold
                         │
                    ┌────▼─────┐
                    │ TRIPPED  │ ◄── Hard stop
                    └────┬─────┘
                         │
                    ├── Save state, trigger Sabbath Rest
                    ├── Or: escalate to user with diagnosis
                    │
                    ┌────▼─────┐
                    │ RECOVERY │ ◄── After Sabbath Rest or approach change
                    └────┬─────┘
                         │
                    Reset counters → HEALTHY
```

---

## Approach Rotation

When WARNING triggers, the circuit breaker forces a fundamentally different approach:

```
ON circuit_breaker_warning(threshold_type):

  approaches_tried = load_from_loop_state()

  IF threshold_type == "SAME_ERROR_HASH":
    # The current fix strategy isn't working
    rotation_suggestions:
      1. "Tried editing file directly → Try creating new file instead"
      2. "Tried fixing the function → Try replacing the function"
      3. "Tried the same dependency → Try alternative library"
      4. "Tried patching → Try refactoring the caller"

  IF threshold_type == "NO_FILE_CHANGES":
    # Agent is stuck in analysis paralysis
    rotation_suggestions:
      1. "Tried reading more files → Start writing a minimal solution"
      2. "Tried understanding the full system → Focus on one component"
      3. "Tried the complex approach → Try the simplest possible fix"

  IF threshold_type == "OUTPUT_DECLINE":
    # Context is degraded — need fresh start
    rotation_suggestions:
      1. "Save findings to loop file and take Sabbath Rest"
      2. "Summarize progress and restart with fresh context"

  inject_into_context:
    "CIRCUIT BREAKER: {threshold_type} warning.
     Approaches already tried: {approaches_tried}
     You MUST try a fundamentally different approach.
     Suggestions: {rotation_suggestions}
     DO NOT repeat previous approaches."
```

---

## Loop File Tracking

The circuit breaker state is tracked in the loop file:

```markdown
## Circuit Breaker State

| Iteration | Files Changed | Error Hash | Output Lines | State |
|-----------|--------------|------------|--------------|-------|
| 1 | 3 | - | 45 | HEALTHY |
| 2 | 2 | a3f2 | 42 | HEALTHY |
| 3 | 0 | a3f2 | 38 | HEALTHY |
| 4 | 0 | a3f2 | 30 | WARNING (same error 3x) |
| 5 | 0 | a3f2 | 22 | WARNING (no files 3x + same error) |
| 6 | - | - | - | TRIPPED (same error 5x) |

### Approaches Tried
1. [Iteration 1-3] Direct fix in auth.ts — TypeError persists
2. [Iteration 4-5] Tried null check wrapper — same underlying issue
3. [Iteration 6] CIRCUIT BREAKER TRIPPED — rotating approach

### Rotation Applied
- Previous: Patching the consumer of the null value
- New: Fix the data source that produces null values
```

---

### 4. Confidence-Outcome Divergence (v7.0 — Process Reward Hacking Detection)

> **Research basis:** AUQ (Jan 2026) + AgentPRM (Feb 2025) — when step-level confidence
> rises while actual outcomes degrade, the agent is "reward hacking" — optimizing for
> feeling confident rather than producing results.

```
THRESHOLD: CONFIDENCE_OUTCOME_DIVERGENCE
  trigger: Confidence trend positive AND reward trend negative over 3+ iterations
  severity: WARNING immediately, BREAK if divergence persists 2 more iterations
  response: Force external verification, re-assess approach

  measure():
    IF iteration_count < 3: SKIP (not enough data)

    confidence_scores = [iter_N-2.confidence, iter_N-1.confidence, iter_N.confidence]
    reward_scores = [iter_N-2.turn_reward, iter_N-1.turn_reward, iter_N.turn_reward]

    confidence_trend = linear_slope(confidence_scores)
    reward_trend = linear_slope(reward_scores)

    IF confidence_trend > 0 AND reward_trend < 0:
      RETURN WARNING: "Confidence rising ({confidence_trend:+.1f}) but rewards falling ({reward_trend:+.1f})"
      ACTION:
        1. Run tests immediately (don't trust self-assessment)
        2. Check git diff for actual progress (not perceived progress)
        3. If tests fail or no real progress: force approach rotation

    IF divergence persists for 2+ additional iterations:
      RETURN BREAK: "Sustained confidence-outcome divergence — agent is optimizing for confidence, not results"
```

**Why this matters:** This is the agent equivalent of Dunning-Kruger — the less progress the agent makes, the more confident it feels about its approach. The divergence detector catches this before context is wasted.

---

### 5. KPI Drift Bounds (v11.0 — Agent Behavioral Contracts)

> **Research basis:** ABC: Agent Behavioral Contracts (Feb 2026) — monitoring KPI drift
> during execution detects when the agent is active but drifting from plan goals.
> Unlike stall/spin detection, this catches "productive but wrong" behavior.

```
THRESHOLD: KPI_DRIFT
  trigger: Execution KPIs diverge from plan expectations over 3+ tasks
  severity: WARNING when drift detected, BREAK if uncorrected after 2 tasks
  response: Re-read plan objectives, realign task approach

  measure():
    # Track 3 KPIs per execution session
    kpi_plan_alignment = tasks_matching_plan_objectives / tasks_completed
    kpi_scope_creep = files_modified_outside_plan / total_files_modified
    kpi_test_coverage_delta = current_coverage - pre_execution_coverage

    IF kpi_plan_alignment < 0.6:
      RETURN WARNING: "Only {pct}% of tasks align with plan objectives"
    IF kpi_scope_creep > 0.4:
      RETURN WARNING: "{pct}% of file changes are outside plan scope"
    IF kpi_test_coverage_delta < -5:
      RETURN WARNING: "Test coverage dropped {delta}% during execution"

    IF any WARNING persists for 2+ additional tasks after being flagged:
      RETURN BREAK: "KPI drift uncorrected — agent drifting from plan"
```

**Why this matters:** An agent can pass all other thresholds (files changing, no error loops, output volume steady) while doing useful-looking work that doesn't advance the plan. ABC drift bounds catch this divergence.

---

## Configuration

```yaml
circuit_breaker:
  # Stall detection
  no_file_changes:
    warning_threshold: 3
    break_threshold: 5

  # Spin detection
  same_error_hash:
    warning_threshold: 3
    break_threshold: 5

  # Degradation detection
  output_decline:
    warning_pct: 50
    break_pct: 70
    baseline_iterations: 3

  # Behavior
  on_warning: rotate_approach  # rotate_approach | pause | ask_user
  on_break: sabbath_rest       # sabbath_rest | stop | ask_user

  # Override
  force_continue: false  # User can set to skip circuit breaker
```

---

## Integration Points

### /fire-loop (primary consumer)

```markdown
# After Step 7 (Execute Task), before Step 8 (Iteration Tracking):

## Circuit Breaker Check
  cb_state = circuit_breaker.measure(
    files_changed = git_diff_stat(),
    error_output = last_error_if_any(),
    output_lines = count_lines(iteration_output)
  )

  IF cb_state == HEALTHY:
    continue normally

  IF cb_state == WARNING:
    display warning banner
    apply approach rotation
    continue with rotated approach

  IF cb_state == TRIPPED:
    display break banner
    save loop state
    trigger sabbath rest OR stop loop
```

### /fire-debug

```markdown
# After each debug cycle:

## Circuit Breaker Check
  Same measurement, but focused on same_error_hash threshold.
  Debug sessions are expected to have no file changes between
  diagnosis steps, so no_file_changes threshold is relaxed to 5/8.
```

### /fire-3-execute

```markdown
# Per-task monitoring during plan execution:

## Circuit Breaker (Lightweight)
  Only track same_error_hash at plan execution level.
  If same build/test error appears 3 times across tasks,
  pause execution and ask user.
```

---

## Display Banners

### WARNING Banner

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CIRCUIT BREAKER WARNING                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Threshold: [NO_FILE_CHANGES | SAME_ERROR_HASH | OUTPUT_DECLINE]           │
│  Count: [N] / [limit]                                                      │
│  Iteration: [current] / [max]                                              │
│                                                                             │
│  Diagnosis:                                                                 │
│    [Human-readable explanation of what's happening]                         │
│                                                                             │
│  Action: ROTATING APPROACH                                                  │
│    Previous: [what was being tried]                                         │
│    New: [what will be tried next]                                           │
│                                                                             │
│  To override: Reply "FORCE CONTINUE"                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### TRIPPED Banner

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CIRCUIT BREAKER TRIPPED                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Threshold: [type] exceeded at iteration [N]                                │
│                                                                             │
│  Summary:                                                                   │
│    Iterations run: [N]                                                      │
│    Files changed: [N] total                                                 │
│    Unique errors: [N]                                                       │
│    Approaches tried: [N]                                                    │
│                                                                             │
│  Loop state saved to: .planning/loops/fire-loop-{ID}.md                   │
│                                                                             │
│  Options:                                                                   │
│    A) /fire-loop-resume {ID}  (fresh context, same state)                 │
│    B) /fire-debug             (switch to structured debugging)             │
│    C) Fix manually, then /fire-loop-resume {ID}                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## References

- **Inspiration:** frankbria's Ralph loop fork (quantitative convergence detection)
- **Related:** `references/error-classification.md` — state machine driving responses
- **Related:** `references/metrics-and-trends.md` — bottleneck detection algorithm
- **Consumer:** `commands/fire-loop.md` — primary integration point
- **Consumer:** `commands/fire-debug.md` — debug cycle integration
