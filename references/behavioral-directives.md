# Behavioral Directives

> Self-modifying behavioral rules in predicate format that evolve based on experience. Inspired by CoALA's procedural memory, SICA's self-improving coding agent (ICLR 2025), and MPR's predicate-form memory (Sep 2025).

**How it works:** Rules progress through Proposed (confidence 1/5) → Active (confidence 3+/5). Each session confirmation increments confidence. Rules that prove wrong get Retired with a reason.

**Format (v7.0 — MPR):** Rules use predicate format (`IF condition THEN action BECAUSE justification`) for mechanical applicability. Anti-patterns use `IF condition DONT action BECAUSE justification`.

---

## Active Rules

<!-- Seed rules — proven patterns from Dominion Flow v1-v5, converted to predicate format in v7.0 -->

### Rule 1
- **IF:** About to perform file operations (create, edit, delete)
- **THEN:** Verify working directory matches expected project path
- **BECAUSE:** Cross-project contamination destroys work in wrong repo
- **Source:** v5.0 | **Confidence:** 5/5 | **Last applied:** 2026-02-21

### Rule 2
- **IF:** Writing SQL queries with user input
- **THEN:** Use parameterized queries, never string interpolation
- **BECAUSE:** SQL injection is OWASP #1 vulnerability
- **Source:** v5.0 | **Confidence:** 5/5 | **Last applied:** 2026-02-21

### Rule 3
- **IF:** About to write a new function, component, or module
- **THEN:** Check for existing implementations before writing new code
- **BECAUSE:** Prevents duplication and leverages proven solutions
- **Source:** v5.0 | **Confidence:** 5/5 | **Last applied:** 2026-02-21

### Rule 4
- **IF:** About to edit a file
- **THEN:** Read the file first — never edit blind
- **BECAUSE:** Files have complex structure; editing without context causes errors
- **Source:** v5.0 | **Confidence:** 5/5 | **Last applied:** 2026-02-21

### Rule 5
- **IF:** Code change has been made
- **THEN:** Run tests after every code change, not just at the end
- **BECAUSE:** Early test failures catch bugs before they compound
- **Source:** v4.0 | **Confidence:** 4/5 | **Last applied:** 2026-02-21

### Rule 6
- **IF:** A logical unit of work is complete
- **THEN:** Commit after each logical unit, not in bulk
- **BECAUSE:** Granular commits enable targeted rollback and clear history
- **Source:** v4.0 | **Confidence:** 4/5 | **Last applied:** 2026-02-17

### Rule 7
- **IF:** Debugging a failing test or runtime error
- **THEN:** Eliminate hypotheses with evidence before proposing fixes
- **BECAUSE:** Premature fixes mask root causes and waste time
- **Source:** v5.0 | **Confidence:** 5/5 | **Last applied:** 2026-02-21

### Rule 8
- **IF:** About to use a third-party package in code
- **THEN:** Check package.json first — never assume a dependency is installed
- **BECAUSE:** Missing dependencies cause cryptic runtime errors
- **Source:** v3.0 | **Confidence:** 4/5 | **Last applied:** 2026-02-17

### Rule 9
- **IF:** Facing a non-trivial technical problem
- **THEN:** Search the skills library before solving from scratch
- **BECAUSE:** Someone may have already solved this — reuse > reinvent
- **Source:** v4.0 | **Confidence:** 4/5 | **Last applied:** 2026-02-21

### Rule 10
- **IF:** Context compaction is about to trigger
- **THEN:** Preserve stop signals — errors and BLOCKED indicators must survive summarization
- **BECAUSE:** Compaction smooths over failure signals, extending stuck loops by ~15%
- **Source:** v6.0 (JetBrains Dec 2025) | **Confidence:** 3/5 | **Last applied:** 2026-02-21

### Rule 11
- **IF:** Code review finds CRITICAL or 3+ HIGH findings
- **THEN:** Do NOT present work to human for testing
- **BECAUSE:** Shipping critical issues wastes human testing time and erodes trust
- **Source:** v8.0 | **Confidence:** 5/5 | **Last applied:** —

### Rule 12
- **IF:** Writing a new helper, utility, or abstraction
- **THEN:** Verify it has 2+ callers; delete if only 1
- **BECAUSE:** Single-use abstractions add complexity without value. Three similar lines > premature abstraction.
- **Source:** v8.0 | **Confidence:** 4/5 | **Last applied:** —

---

## Anti-Patterns (v7.0 — What NOT to Do)

### Anti-Pattern 1
- **IF:** Debugging a failing test
- **DONT:** Modify the test to make it pass without understanding the root cause
- **BECAUSE:** Masks the real bug, creates false confidence in passing tests
- **Source:** v5.0 | **Confidence:** 5/5

### Anti-Pattern 2
- **IF:** An API call returns an error
- **DONT:** Wrap it in a try/catch that silently swallows the error
- **BECAUSE:** Silent failures are invisible; they compound into data corruption
- **Source:** v5.0 | **Confidence:** 5/5

### Anti-Pattern 3
- **IF:** A loop iteration is stuck with the same error
- **DONT:** Retry the same approach more than 3 times
- **BECAUSE:** Repeating a failed approach wastes context and never produces different results
- **Source:** v4.0 | **Confidence:** 4/5

### Anti-Pattern 4
- **IF:** Qdrant JS client throws an error
- **DONT:** Assume standard Error shape with `.message` property
- **BECAUSE:** Qdrant client throws ApiError with `.status` and `.data.status.error`, not `.message`
- **Source:** v6.0 | **Confidence:** 3/5

### Anti-Pattern 5
- **IF:** Code works and passes tests
- **DONT:** Add extra error handling, feature flags, or backwards-compat for scenarios that can't happen
- **BECAUSE:** Defensive code for impossible scenarios is over-engineering, not safety
- **Source:** v8.0 | **Confidence:** 4/5

---

## Proposed Rules (Need 3 confirmations to activate)

<!-- Rules suggested by sessions but not yet confirmed -->
<!-- Format: predicate format with IF/THEN/BECAUSE, Source, Confidence, First proposed date -->

---

## Retired Rules (Superseded or wrong)

<!-- Rules that were deactivated with reason -->
<!-- Format: **Rule** — Retired: {date}, Reason: {why it was wrong or superseded} -->

---

## How Rules Evolve

```
NEW INSIGHT discovered during task resolution
  │
  ├── Check: Does similar directive exist?
  │     ├── YES (in Active) → Skip (already known)
  │     ├── YES (in Proposed) → Increment confidence
  │     │     └── If confidence reaches 3/5 → Promote to Active
  │     └── NO → Add to Proposed with confidence 1/5
  │
  └── Check: Did an Active rule prove wrong?
        └── YES → Move to Retired with reason
```

### Hard Admissibility Check (v7.0 — MPR)

> prevent known-bad actions before they execute, not after.

```
Before executing any action, scan Active Rules + Anti-Patterns:

For each rule where IF condition matches current context:
  IF rule is positive (THEN) → inject action into working instructions
  IF rule is anti-pattern (DONT) → inject explicit warning

HAC (Hard Admissibility Check):
  IF an Active Rule with confidence 5/5 explicitly prohibits the planned action:
    → BLOCK execution
    → Display: "HAC BLOCK: Rule {N} prohibits this action: {rule statement}"
    → Require explicit user override to proceed

HAC applies to anti-patterns too:
  IF an Anti-Pattern with confidence 5/5 matches the planned action:
    → BLOCK execution
    → Display: "HAC BLOCK: Anti-Pattern {N}: {DONT statement}"
```

**Trigger points:**
- After task resolution in `/fire-loop` (Step 8.5)
- After debug resolution in `/fire-debug` (Step 7.75)
- After verification failures in `/fire-4-verify`
- During handoff creation in `/fire-5-handoff` (F section review)

---

## Version Performance Registry (v8.0)

> Track outcomes per version. When rules cause more harm than good, the data proves it.

### How It Works

Every time the merge gate (Step 8.5) or post-loop review gate (Step 12.5) produces a verdict, record the outcome:

```
After merge gate or review gate completes:

  Append to .planning/version-performance.md:

  | Date | Version | Gate | Verdict | Override? | Outcome | Notes |
  |------|---------|------|---------|-----------|---------|-------|
  | {date} | v8.0 | merge | BLOCK | yes/no | {correct/false-positive/false-negative} | {brief note} |

  Override = user chose "B) Override with known issues"
  Outcome = filled retroactively after human testing:
    - correct:        gate was right (issue was real)
    - false-positive: gate blocked but code was fine
    - false-negative: gate approved but issue was found later
```

### Degradation Signals

```
AFTER accumulating 5+ gate outcomes for a version, compute:

  override_rate    = overrides / total_gates
  false_positive_rate = false_positives / total_blocks
  false_negative_rate = false_negatives / total_approves

  DEGRADATION DETECTED when ANY of:
    1. override_rate > 40%
       → Users are routinely bypassing the gate. Rules are too strict
          or flagging wrong things.

    2. false_positive_rate > 30%
       → Gate is crying wolf. Blocks are not backed by real issues.

    3. false_negative_rate > 20%
       → Gate is missing real problems. Not strict enough or
          wrong personas prioritized.

    4. Same rule triggers BLOCK 3+ times and gets overridden every time
       → That specific rule is wrong. Retire it.

  Display when degradation detected:
  "+--------------------------------------------------------------+"
  "| VERSION DEGRADATION DETECTED                                   |"
  "+--------------------------------------------------------------+"
  "|                                                              |"
  "|  Version: v{X}                                               |"
  "|  Signal: {which signal fired}                                |"
  "|  Data: {metric} = {value} (threshold: {threshold})           |"
  "|                                                              |"
  "|  Options:                                                    |"
  "|    A) Rollback to v{X-1} rules                               |"
  "|    B) Retire specific rule: {rule that caused most overrides} |"
  "|    C) Adjust threshold and continue                          |"
  "|                                                              |"
  "+--------------------------------------------------------------+"
```

### Version Changelog

Track what each version introduced so rollback targets are clear:

| Version | Date | Rules Added | Rules Retired | Key Change |
|---------|------|-------------|---------------|------------|
| v5.0 | 2026-02-20 | Rules 1-4 (seed) | — | Path verification, confidence gates |
| v6.0 | 2026-02-21 | Rules 5-10, AP 1-4 | — | Predicate format, CoALA, ECHO |
| v7.0 | 2026-02-21 | (converted to predicate) | — | MPR predicates, HAC enforcement |
| v8.0 | 2026-02-21 | Rules 11-12, AP 5 | — | Review gate, simplicity enforcement |

### Rollback Protocol

```
TO ROLLBACK a version:

  1. Identify rules introduced in that version (from changelog above)
  2. Move those rules to Retired Rules section with reason:
     "Retired: {date}, Reason: Version performance degradation —
      {metric} = {value}, threshold = {threshold}"
  3. If rolling back the review gate entirely:
     - Change --skip-review default to ON in fire-3-execute.md
     - Remove Step 12.5 from fire-loop.md
     - Add note: "Review gate disabled due to v{X} degradation"
  4. Record rollback in Version Changelog
  5. Performance registry resets for the reverted version

TO ROLLBACK a single rule:
  1. Move rule to Retired Rules with degradation data
  2. If rule was part of HAC (confidence 5/5), HAC stops blocking on it
  3. Keep the registry running — partial rollbacks need continued monitoring

RULE: Never delete performance data. Retired rules keep their history.
       This prevents the same bad rule from being re-proposed later.
```

### Active Performance Data

<!-- Populated automatically by merge gate (Step 8.5) and review gate (Step 12.5) -->
<!-- Location: .planning/version-performance.md in each project -->

```
No data yet — v8.0 just deployed. First 5 gate outcomes will establish baseline.
```

---

---

## Formal Constraints (v11.0 — AgentSpec-Style Enforcement)

> constraints that are enforced at runtime, not just documented. Unlike predicate rules (which
> guide behavior), formal constraints BLOCK execution if violated.

### ALWAYS Constraints (invariants — never false)

```
ALWAYS: working_directory == project_path
  Enforcement: Path Verification Gate (Step 3.5 in fire-executor)
  On violation: HALT — do not proceed under any circumstances

ALWAYS: git_status_clean BEFORE phase_transition
  Enforcement: fire-3-execute Step 7 checks for uncommitted changes
  On violation: BLOCK — commit or stash before advancing

ALWAYS: tests_pass AFTER code_change
  Enforcement: fire-executor Step 3 verification commands
  On violation: WARNING — fix tests before marking task complete
```

### NEVER Constraints (prohibitions — always false)

```
NEVER: commit_real_credentials_to_repo
  Enforcement: credential-filter.sh hook + fire-add-new-skill Step 4.6
  On violation: BLOCK — strip credentials, replace with placeholders

NEVER: delete_file_without_reading_first
  Enforcement: Rule 4 (confidence 5/5) + HAC
  On violation: BLOCK — read file to confirm contents before deletion

NEVER: skip_path_verification_in_autonomous_mode
  Enforcement: fire-autonomous Step 0.5 — MANDATORY even in autonomous
  On violation: HALT — this gate cannot be disabled
```

### WHEN-THEN Constraints (conditional enforcement)

```
WHEN: confidence_score < 30
THEN: create_checkpoint AND search_skills_library
  Enforcement: fire-executor Step 3 confidence computation
  On violation: WARNING — low-confidence work without safety net

WHEN: circuit_breaker == TRIPPED
THEN: stop_execution AND save_state
  Enforcement: circuit-breaker.md state machine
  On violation: BLOCK — cannot continue past a tripped breaker

WHEN: reviewer_verdict == BLOCK
THEN: fix_findings BEFORE presenting_to_human
  Enforcement: Rule 11 (confidence 5/5) + merge gate
  On violation: BLOCK — critical issues must be resolved first
```

**Enforcement levels:**
- **HALT:** Execution stops immediately. No override possible.
- **BLOCK:** Execution pauses. Must resolve the constraint violation to proceed.
- **WARNING:** Logged to handoff. Execution continues but violation is tracked.

---

## Frequency-Ranked Core Learnings (v13.0 — Nodeland/Beads Pattern)

> rank behavioral rules by application frequency. Most-used rules are injected first into
> context (highest attention weight), rarely-used rules are demoted. This is natural selection
> for rules: useful ones survive, useless ones fade.

### How It Works

```
EVERY 10 sessions (or when `Last applied` dates are updated):

  1. RANK all Active Rules by recency * frequency:
     score = (1 / days_since_last_applied) * total_applications

  2. TOP 5 rules → "Core Learnings" (injected into every executor prompt)
  3. Rules 6-12 → "Active" (available via DTG lookup, not pre-injected)
  4. Rules with 0 applications in 30 days → "Dormant" (candidate for retirement)

  FORMAT for Core Learnings injection:
    <core_learnings>
    1. [R1] Verify working directory before file operations
    2. [R4] Read files before editing
    3. [R7] Eliminate hypotheses with evidence before fixing
    4. [R5] Run tests after every code change
    5. [R2] Use parameterized queries for user input
    </core_learnings>
```

### Current Rankings (v13.0 baseline)

| Rank | Rule | Last Applied | Status |
|------|------|-------------|--------|
| 1 | R1 (path verification) | 2026-02-21 | Core |
| 2 | R4 (read before edit) | 2026-02-21 | Core |
| 3 | R7 (evidence-based debug) | 2026-02-21 | Core |
| 4 | R5 (tests after change) | 2026-02-21 | Core |
| 5 | R3 (check existing code) | 2026-02-21 | Core |
| 6-12 | R2, R6, R8-R12 | varies | Active |

### Dormancy Protocol

```
IF rule.last_applied > 30 days ago AND rule.total_applications < 3:
  → Move to "Dormant" section
  → Log: "Rule {N} dormant — no applications in 30 days"
  → Dormant rules are NOT deleted — they can be reactivated if relevant again
  → Retirement requires explicit review (dormancy ≠ retirement)
```

---

## CNCF Four Pillars Taxonomy (v13.0 — Rule Classification)

> into four pillars: Observability, Governance, Security, and Lifecycle. Mapping our rules
> to these pillars reveals coverage gaps and makes rule selection faster at decision time.

### Pillar Mapping

| Pillar | Rules | Anti-Patterns | Formal Constraints |
|--------|-------|---------------|-------------------|
| **Observability** | R5 (tests after change), R10 (compaction signals), R11 (review gate) | AP2 (silent errors), AP3 (retry loops) | ALWAYS: tests_pass, WHEN: output_decline |
| **Governance** | R6 (granular commits), R12 (no single-use abstractions) | AP5 (over-engineering) | ALWAYS: git_status_clean, WHEN: reviewer_verdict |
| **Security** | R1 (path verification), R2 (parameterized queries), R4 (read before edit) | AP1 (modify tests to pass) | NEVER: commit_credentials, NEVER: delete_without_reading, ALWAYS: working_directory |
| **Lifecycle** | R3 (check existing code), R7 (evidence-based debugging), R8 (check deps), R9 (search skills) | AP4 (Qdrant error shape) | WHEN: confidence < 30, WHEN: circuit_breaker |

### Coverage Analysis

```
Observability:  5 rules/constraints — GOOD coverage
Governance:     4 rules/constraints — ADEQUATE
Security:       6 rules/constraints — STRONG coverage
Lifecycle:      6 rules/constraints — GOOD coverage

Gap: No OBSERVABILITY rule for monitoring context usage
  → Candidate: "IF context exceeds 70% THEN log warning + trigger tier assessment"
  → Status: PROPOSED (needs 3 confirmations to activate)
```

### Decision-Time Lookup

When DTG (Decision-Time Guidance) fires at a decision point, use pillar classification for fast rule lookup:

```
TOOL_CHOICE decision     → check: Lifecycle pillar rules
ARCHITECTURE decision    → check: Governance + Lifecycle
ERROR_HANDLING decision  → check: Observability + Security
SECURITY decision        → check: Security pillar rules (ALL)
PERFORMANCE decision     → check: Governance (no over-engineering)
SCOPE decision           → check: Governance + Lifecycle
```

---

*Dominion Flow v13.0 — MPR predicate rules + HAC enforcement + review gate + simplicity + version tracking + formal constraints + CNCF taxonomy*
*v7.0: Predicate format + HAC enforcement (2026-02-21)*
*v8.0: Rules 11-12, Anti-Pattern 5, Version Performance Registry (2026-02-21)*
*v11.0: AgentSpec formal ALWAYS/NEVER/WHEN-THEN constraints (2026-03-01)*
*v13.0: CNCF Four Pillars taxonomy mapping (2026-03-12)*
