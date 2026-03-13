# Dominion Flow Checkpoints Reference

> **Origin:** Ported from Dominion Flow `checkpoints.md` with Dominion Flow WARRIOR validation additions.

## Overview

Plans execute autonomously. Checkpoints formalize the interaction points where human verification or decisions are needed.

**Core principle:** Claude automates everything with CLI/API. Checkpoints are for verification and decisions, not manual work.

---

## Checkpoint Types

### checkpoint:human-verify (Most Common - 90%)

**When:** Claude completed automated work, human confirms it works correctly.

**Use for:** Visual UI checks, interactive flows, functional verification, audio/video playback, animation smoothness, accessibility testing.

```xml
<task type="checkpoint:human-verify" gate="blocking">
  <what-built>[What Claude automated and deployed/built]</what-built>
  <how-to-verify>
    [Exact steps to test - URLs, commands, expected behavior]
  </how-to-verify>
  <resume-signal>[How to continue - "approved", "yes", or describe issues]</resume-signal>
</task>
```

### checkpoint:decision (9%)

**When:** Human must make choice that affects implementation direction.

**Use for:** Technology selection, architecture decisions, design choices, feature prioritization, data model decisions.

```xml
<task type="checkpoint:decision" gate="blocking">
  <decision>[What's being decided]</decision>
  <context>[Why this decision matters]</context>
  <options>
    <option id="option-a">
      <name>[Option name]</name>
      <pros>[Benefits]</pros>
      <cons>[Tradeoffs]</cons>
    </option>
  </options>
  <resume-signal>[How to indicate choice]</resume-signal>
</task>
```

### checkpoint:human-action (1% - Rare)

**When:** Action has NO CLI/API and requires human-only interaction, OR Claude hit an authentication gate.

**Use ONLY for:** Authentication gates, email verification links, SMS 2FA codes, manual account approvals, credit card 3D Secure flows, OAuth app approvals.

**Do NOT use for:** Deploying (use CLI), creating webhooks (use API), creating databases (use CLI), running builds/tests (use Bash), creating files (use Write tool).

```xml
<task type="checkpoint:human-action" gate="blocking">
  <action>[What human must do]</action>
  <instructions>[What Claude already automated + the ONE manual step]</instructions>
  <verification>[What Claude can check afterward]</verification>
  <resume-signal>[How to continue]</resume-signal>
</task>
```

---

## Execution Protocol

When Claude encounters `type="checkpoint:*"`:

1. **Stop immediately** - do not proceed to next task
2. **Display checkpoint clearly** using branded format
3. **Wait for user response** - do not hallucinate completion
4. **Verify if possible** - check files, run tests
5. **Resume execution** - continue only after confirmation

### Display Format

```
+---------------------------------------------------------------+
|  CHECKPOINT: [Verification/Decision/Action] Required           |
+---------------------------------------------------------------+
|                                                                 |
|  Progress: X/Y tasks complete                                  |
|  Task: [task name]                                             |
|                                                                 |
|  [Type-specific content]                                       |
|                                                                 |
|-----------------------------------------------------------------|
|  YOUR ACTION: [resume signal]                                   |
+-----------------------------------------------------------------+
```

---

## Authentication Gates

**Pattern:** Claude tries automation -> auth error -> creates checkpoint -> you authenticate -> Claude retries -> continues

**Gate protocol:**
1. Recognize it's not a failure - missing auth is expected
2. Stop current task - don't retry repeatedly
3. Create checkpoint:human-action dynamically
4. Provide exact authentication steps
5. Verify authentication works
6. Retry the original task
7. Continue normally

---

## Dominion Flow Additions

### WARRIOR Quality Gate Checkpoint

After phase completion, Dominion Flow adds a WARRIOR validation checkpoint:

```xml
<task type="checkpoint:human-verify" gate="blocking">
  <what-built>Phase XX complete - WARRIOR validation results</what-built>
  <how-to-verify>
    Review validation report:
    1. Code quality: [pass/fail]
    2. Security checks: [pass/fail]
    3. Test coverage: [X%]
    4. All must-haves verified: [yes/no]
  </how-to-verify>
  <resume-signal>Type "approved" to proceed to next phase</resume-signal>
</task>
```

### Blocker-Aware Checkpoints

If open blockers exist when checkpoint is reached:

```
+---------------------------------------------------------------+
|  WARNING: Open Blockers Detected                               |
+---------------------------------------------------------------+
|  P1: [blocker description] (blocks tasks 3, 4)                |
|  P2: [blocker description] (non-blocking, tracked)            |
|                                                                 |
|  Options:                                                      |
|    A) Fix P1 blockers before continuing                        |
|    B) Skip blocked tasks, continue with unblocked work         |
|    C) Create workaround and document in BLOCKERS.md            |
+-----------------------------------------------------------------+
```

---

## Anti-Patterns

- Asking human to do work Claude can automate
- Too many checkpoints (verification fatigue)
- Vague verification steps ("check it works")
- Checkpoint before automation (should automate first)
- Missing resume signal

## The Golden Rule

If Claude CAN automate it, Claude MUST automate it.
