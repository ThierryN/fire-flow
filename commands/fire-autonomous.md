---
description: Full autopilot — plan, execute, verify all phases autonomously after PRD is complete
argument-hint: "[--from-phase N] [--to-phase N] [--max-phase-attempts 3]"
---

# /fire-autonomous

> Full autopilot after PRD is complete — plan, execute, verify, advance through all phases independently

---

## Purpose

After discussions and PRD are complete (`/fire-1a-discuss`), this command takes over the entire build pipeline. Claude plans each phase, executes it, verifies the work (verifier + reviewer), fixes any issues, and advances to the next phase — all without human checkpoints.

**Design principle (Boris Cherny):** "You don't trust; you instrument." All verification stays active. Verdicts auto-route to fix cycles instead of pausing for human input. The human reviews the finished product, not intermediate steps.

**Safety:** Path verification, HAC, circuit breaker, fire-verifier, and fire-reviewer all remain active. Autonomous mode removes human pauses, not safety gates.

---

## Arguments

```yaml
arguments:
  --from-phase:
    type: integer
    default: "next incomplete phase from CONSCIENCE.md"
    description: "Start from this phase number"

  --to-phase:
    type: integer
    default: "last phase in VISION.md"
    description: "Stop after completing this phase"

  --max-phase-attempts:
    type: integer
    default: 3
    description: "Max plan-execute-verify cycles per phase before escalating"

  --max-iterations:
    type: integer
    default: 50
    description: "Max iterations per execution loop (passed to fire-3-execute)"

  --dry-run:
    type: boolean
    default: false
    description: "Show what would be done without executing"
```

---

## Process

### Step 1: Validate Prerequisites

```
Read .planning/VISION.md → extract all phases
Read .planning/CONSCIENCE.md → get current status, find next incomplete phase

IF --from-phase not specified:
  from_phase = first phase with status != complete in CONSCIENCE.md

IF --to-phase not specified:
  to_phase = last phase in VISION.md

Validate:
  1. .planning/ directory exists
  2. VISION.md has phases in range [from_phase, to_phase]
  3. For each phase in range: MEMORY.md exists (PRD/discussion complete)
  4. Path Verification Gate (MANDATORY — working directory matches project)

IF any phase lacks MEMORY.md:
  Display:
    "Phase {N} has no MEMORY.md — discussions not complete.
     Run /fire-1a-discuss {N} first.
     Autonomous mode requires all target phases to have context."
  STOP
```

### Step 0.5: Path Verification Gate (v5.0 — MANDATORY)

```
Same as all Dominion Flow commands:
  1. Verify working directory matches expected project path
  2. Check for cross-project contamination risk
  3. Validate subagent path injection safety

This gate is NEVER disabled, not even in autonomous mode.
```

### Step 2: Display Autonomous Mode Banner

```
+--------------------------------------------------------------+
| AUTONOMOUS MODE ACTIVATED                                      |
+--------------------------------------------------------------+
|                                                                |
|  Project: {project name from VISION.md}                       |
|  Phases: {from_phase} to {to_phase} ({count} phases)           |
|  Max attempts per phase: {max_phase_attempts}                  |
|                                                                |
|  Active Safety:                                                |
|    Path verification    — MANDATORY (cannot disable)           |
|    HAC enforcement      — Active (confidence 5/5 rules)        |
|    Circuit breaker      — Active (stall/spin/degrade detect)   |
|    fire-verifier       — 70-point WARRIOR validation          |
|    fire-reviewer       — 15-persona code review               |
|                                                                |
|  Human touchpoints: NONE until completion or blocker           |
|                                                                |
|  To interrupt: Ctrl+C or /fire-loop-stop                      |
|                                                                |
+--------------------------------------------------------------+
```

IF `--dry-run`:
```
DRY RUN — would execute:

  Phase {N}: {name}
    1. /fire-2-plan {N} --skip-checker
    2. /fire-3-execute {N} --auto-continue --autonomous
    3. Read verification + review results
    4. Auto-fix if needed (up to {max_phase_attempts} attempts)

  Phase {N+1}: {name}
    ...

No changes made. Remove --dry-run to execute.
```
STOP

### Step 3: Phase Loop

```
autonomous_log = []
phases_completed = 0
start_time = now()

FOR phase_number in range(from_phase, to_phase + 1):

  phase_name = VISION.md phase name
  attempt = 0
  phase_complete = false

  Display:
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    " AUTONOMOUS: Phase {phase_number} — {phase_name}"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  WHILE attempt < max_phase_attempts AND NOT phase_complete:
    attempt += 1

    Display: "  Attempt {attempt}/{max_phase_attempts}..."

    // ──────────────────────────────────────────────────────
    // Step 3.1: AUTO-PLAN
    // ──────────────────────────────────────────────────────

    phase_dir = .planning/phases/{phase_number}-{phase_name}/
    plan_files = glob("{phase_dir}/*.BLUEPRINT.md")

    IF plan_files is empty:
      Display: "  Planning phase {phase_number}..."

      Run /fire-2-plan {phase_number} --skip-checker
      // skip-checker: plan issues surface during verification
      // auto-replan on failure is more effective than blocking on warnings

    ELSE:
      Display: "  Plans exist ({count} plans). Executing..."

    // ──────────────────────────────────────────────────────
    // Step 3.2: AUTO-EXECUTE
    // ──────────────────────────────────────────────────────

    Display: "  Executing phase {phase_number}..."

    Run /fire-3-execute {phase_number} --auto-continue --autonomous
    // --auto-continue: no breath-boundary interrupts
    // --autonomous: merge gate auto-routes verdicts (v9.0)

    // ──────────────────────────────────────────────────────
    // Step 3.3: AUTO-VERIFY (read results)
    // ──────────────────────────────────────────────────────

    verification_file = {phase_dir}/{N}-VERIFICATION.md
    review_file = {phase_dir}/{N}-REVIEW.md

    Read verification_file → extract warrior_score, verifier_verdict
    Read review_file → extract reviewer_verdict, finding_counts

    // ──────────────────────────────────────────────────────
    // Step 3.4: Evaluate Results
    // ──────────────────────────────────────────────────────

    IF verifier_verdict == "APPROVED" AND reviewer_verdict == "APPROVE":
      phase_complete = true
      phase_result = "CLEAN PASS"

      Display: "  Phase {N}: CLEAN PASS (verifier {score}/70, reviewer APPROVE)"

    ELIF verifier_verdict in ["APPROVED", "CONDITIONAL"] AND reviewer_verdict in ["APPROVE", "APPROVE WITH FIXES"]:
      phase_complete = true
      phase_result = "PASSED WITH NOTES"

      Display: "  Phase {N}: PASSED WITH NOTES"
      Display: "    Verifier: {verifier_verdict} ({score}/70)"
      Display: "    Reviewer: {reviewer_verdict} ({finding_counts})"
      Display: "    Non-critical gaps logged to autonomous-log.md"

    ELSE:
      phase_result = "NEEDS FIX"

      Display: "  Phase {N}: NEEDS FIX (attempt {attempt})"
      Display: "    Verifier: {verifier_verdict}"
      Display: "    Reviewer: {reviewer_verdict}"

      IF attempt < max_phase_attempts:
        Display: "  Re-planning for gaps..."
        Run /fire-2-plan {phase_number} --gaps
        // Loop back to Step 3.2 (next WHILE iteration)
      ELSE:
        Display: "  Max attempts reached. Escalating."
        GOTO Step 7 (Escalation)

    // Log attempt
    autonomous_log.append({
      phase: phase_number,
      attempt: attempt,
      verifier: verifier_verdict,
      reviewer: reviewer_verdict,
      warrior_score: score,
      result: phase_result
    })

  // ──────────────────────────────────────────────────────
  // Step 3.5: Phase Transition
  // ──────────────────────────────────────────────────────

  IF phase_complete:
    phases_completed += 1

    Update CONSCIENCE.md:
      Phase {phase_number}: complete
      Autonomous: true
      Attempts: {attempt}
      Verifier: {score}/70
      Reviewer: {reviewer_verdict}

    // Commit checkpoint
    git add -A && git commit -m "autonomous: Phase {phase_number} - {phase_name} complete"

    Display: "  Phase {phase_number} complete. Advancing..."
```

### Step 4: Blocker Detection

```
STOP AUTONOMOUS MODE immediately if ANY of:

  1. Circuit breaker TRIPPED with state = BLOCKED
     → Agent cannot make progress. No amount of retry will help.
     → Display: "Circuit breaker tripped: {reason}"

  2. Path verification gate fails
     → Working directory mismatch or cross-project contamination detected.
     → Display: "PATH VIOLATION: {details}"

  3. HAC HARD BLOCK fires (confidence 5/5 rule match)
     → A known-bad action was attempted.
     → Display: "HAC BLOCK: Rule {N} — {rule statement}"

  4. 3 consecutive phase attempts fail (max_phase_attempts exceeded)
     → Genuine blocker in the phase.
     → Display: "Phase {N} failed after {max_phase_attempts} attempts"

  5. Context degradation detected (output volume decline >50%)
     → Context rot. Fresh session needed.
     → Display: "Context degradation detected. Sabbath Rest recommended."

On ANY blocker: GOTO Step 7 (Escalation)
```

### Step 5: Write Autonomous Log

```
Write .planning/autonomous-log.md:

# Autonomous Session Log

## Session: {timestamp}

| Key | Value |
|-----|-------|
| Phases | {from_phase} to {to_phase} |
| Completed | {phases_completed} of {total} |
| Duration | {elapsed_time} |
| Mode | Full autopilot |

### Phase Results

| Phase | Name | Attempts | Verifier | Reviewer | Result |
|-------|------|----------|----------|----------|--------|
| {N} | {name} | {attempts} | {score}/70 | {verdict} | {result} |
| {N+1} | {name} | {attempts} | {score}/70 | {verdict} | {result} |

### Gaps Noted
{List of non-critical gaps from PASSED WITH NOTES phases}

### Behavioral Directive Proposals
{Any HIGH/CRITICAL findings from reviewer that should become rules}
```

### Step 6: Completion Banner

```
+--------------------------------------------------------------+
| AUTONOMOUS MODE COMPLETE                                       |
+--------------------------------------------------------------+
|                                                                |
|  Phases completed: {phases_completed} of {total}               |
|  Total attempts: {sum of all attempts}                         |
|  Duration: {elapsed_time}                                      |
|                                                                |
|  Results:                                                      |
|  Phase {N}: {result} (verifier {score}/70, reviewer {verdict}) |
|  Phase {N+1}: {result} (...)                                   |
|  ...                                                           |
|                                                                |
|  Gaps noted: {count}                                           |
|  Log: .planning/autonomous-log.md                              |
|                                                                |
+--------------------------------------------------------------+
| NEXT                                                           |
+--------------------------------------------------------------+
|                                                                |
|  Your work is ready for review.                                |
|                                                                |
|  /fire-dashboard          — See project status                |
|  /fire-4-verify {N}      — Detailed verification             |
|  /fire-session-summary   — Auto-generated (see above)        |
|  /fire-5-handoff         — Full WARRIOR handoff (milestones) |
|                                                                |
+--------------------------------------------------------------+
```

### Step 7: Escalation (Blocker Hit)

```
+--------------------------------------------------------------+
| AUTONOMOUS MODE STOPPED — BLOCKER                              |
+--------------------------------------------------------------+
|                                                                |
|  Completed: Phases {from_phase} to {last_completed}            |
|  Blocked at: Phase {blocked_phase}, attempt {attempt}          |
|                                                                |
|  Blocker: {description}                                        |
|  Type: {BLOCKED | PATH_VIOLATION | HAC_BLOCK | MAX_ATTEMPTS |  |
|         CONTEXT_DEGRADATION}                                   |
|                                                                |
|  What was tried:                                               |
|  - Attempt 1: {verifier_verdict} / {reviewer_verdict}          |
|  - Attempt 2: {verifier_verdict} / {reviewer_verdict}          |
|  - Attempt 3: {verifier_verdict} / {reviewer_verdict}          |
|                                                                |
|  Log: .planning/autonomous-log.md                              |
|                                                                |
+--------------------------------------------------------------+
| OPTIONS                                                        |
+--------------------------------------------------------------+
|                                                                |
|  A) /fire-debug — Investigate the blocker                     |
|  B) /fire-3-execute {N} — Manual execution with oversight     |
|  C) /fire-autonomous --from-phase {N} — Retry from here       |
|  D) /fire-dashboard — Review current state                    |
|                                                                |
+--------------------------------------------------------------+
```

### Step 7.5: Auto Session Summary

```
Run /fire-session-summary

This generates a compact forward-looking summary with:
  - Aggregate status (DONE/PARTIAL/BLOCKED for each work item)
  - Readiness assessment (what's ready, blocked, needs-first)
  - Outlook (trajectory, risk, momentum)
  - Next steps (3 specific actions)
  - Decisions made

Saved to ~/.claude/session-summaries/{project}_{date}.md
Auto-indexed into Qdrant on next session-end consolidation.

This is NOT a replacement for WARRIOR handoffs — it's the lightweight
forward-looking context that the memory system doesn't capture.
```

### Step 8: Sabbath Rest — Session State

```
Update .claude/dominion-flow.local.md:

---
last_session: {timestamp}
command: "autonomous"
status: {complete | blocked}
phases_completed: {list}
blocked_at: {phase or null}
blocker_type: {type or null}
log: ".planning/autonomous-log.md"
---

# Autonomous Session State

## Last Run
- Date: {timestamp}
- Phases: {from} to {to}
- Completed: {count}/{total}
- Duration: {elapsed}

## Resume Point
IF blocked:
  Resume with: /fire-autonomous --from-phase {blocked_phase}
ELSE:
  All phases complete. Next milestone or new discussions.
```

IF phases_completed > 0:
  Create WARRIOR handoff with autonomous session context.

---

## Safety Guarantees

```
NEVER DISABLED in autonomous mode:

  1. Path Verification Gate (Step 0.5)
     — Wrong-repo editing is catastrophic and irreversible
     — No confidence level justifies skipping this

  2. HAC Hard Blocks (confidence 5/5 anti-patterns)
     — Known-bad actions are blocked BEFORE execution
     — These represent "we know this is wrong" conclusions

  3. Circuit Breaker (BLOCKED state)
     — Agent admits it cannot proceed
     — No amount of retry will fix external blockers

  4. Power-Verifier (70-point WARRIOR validation)
     — Functional correctness checking stays active
     — Verdicts auto-route but are never suppressed

  5. Power-Reviewer (15-persona code review)
     — Quality and simplicity checking stays active
     — BLOCK verdicts force fix cycles, not human pauses

WHAT IS DISABLED in autonomous mode:

  1. "READY FOR HUMAN" pause at merge gate
     — Auto-proceeds to next phase instead of waiting

  2. "Continue?" interrupts between breaths
     — Handled by --auto-continue flag

  3. Plan-checker blocking
     — Handled by --skip-checker flag
     — Plan issues surface in verification instead

  4. Human review of individual phase results
     — Results logged, human sees final product
```

---

## Examples

```bash
# Full autopilot from next incomplete phase to end
/fire-autonomous

# Run phases 3 through 7
/fire-autonomous --from-phase 3 --to-phase 7

# Preview without executing
/fire-autonomous --dry-run

# Custom iteration limits
/fire-autonomous --max-phase-attempts 5 --max-iterations 100
```

---

## Related Commands

- `/fire-1a-discuss` — Gather context BEFORE autonomous mode (required)
- `/fire-2-plan` — Manual planning (autonomous mode auto-plans)
- `/fire-3-execute` — Manual execution (autonomous mode auto-executes)
- `/fire-4-verify` — Manual verification (autonomous mode auto-verifies)
- `/fire-loop` — Task-level loop (autonomous mode is phase-level)
- `/fire-loop-stop` — Emergency stop for autonomous mode
- `/fire-dashboard` — View results after autonomous run

---

## Success Criteria

- [ ] All target phases have MEMORY.md (prerequisite enforced)
- [ ] Path verification gate runs on entry
- [ ] Each phase is auto-planned if no BLUEPRINT.md exists
- [ ] Each phase is auto-executed with --auto-continue --autonomous
- [ ] Verification results read and evaluated automatically
- [ ] FAILED/BLOCK phases auto-replan and re-execute (up to max attempts)
- [ ] PASSED phases auto-advance to next phase
- [ ] Autonomous log written with per-phase details
- [ ] Blocker detection stops autonomous mode cleanly
- [ ] Escalation banner shows options for manual intervention
- [ ] WARRIOR handoff created on completion or blocker
- [ ] Sabbath Rest state updated for resume capability

---

*Dominion Flow v9.0 — Full autopilot with instrumentation over restriction*
*Boris Cherny principle: "You don't trust; you instrument."*
