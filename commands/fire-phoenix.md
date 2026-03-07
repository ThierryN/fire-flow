---
description: Autonomous Phoenix Rebuild — reverse-engineer intent from messy code, then rebuild clean from scratch
argument-hint: "--source <path> [--target <path>] [--migrate] [--dry-run] [--focus <subsystem>]"
---

# /fire-phoenix

> Burn the Frankenstein. Rise production-ready. Reverse-engineer INTENT from messy code, ask clarifying questions, then rebuild clean in a new folder.

---

## Purpose

Take a messy "vibe coded" project and autonomously rebuild it into a clean, production-quality application. The source folder is **never modified** — the rebuild happens in a new target folder using the full Dominion Flow pipeline.

**What makes this different from refactoring:** Refactoring improves code incrementally. Phoenix burns the old code entirely and rebuilds from extracted INTENT. The result carries the knowledge but none of the accidental complexity.

> **Reference:** @skills-library/_general/methodology/PHOENIX_REBUILD_METHODOLOGY.md

**Core pipeline:**
```
AUTOPSY → INTENT → CLARIFY → VISION → REBUILD → COMPARISON
```

---

## Arguments

```yaml
arguments:
  --source:
    type: path
    required: true
    description: "Path to the messy source project"
    example: "/fire-phoenix --source C:/Projects/my-app"

  --target:
    type: path
    required: false
    default: "{source}-phoenix"
    description: "Path for the clean rebuild output"
    example: "/fire-phoenix --source ./app --target ./app-v2"

  --migrate:
    type: boolean
    default: false
    description: "Enable stack migration mode (propose alternative tech stacks)"

  --dry-run:
    type: boolean
    default: false
    description: "Run Phase 1-3 only (analyze + clarify). No rebuild."

  --focus:
    type: string
    required: false
    description: "Limit analysis to a specific subsystem"
    example: "/fire-phoenix --source ./app --focus auth"
```

---

## Process

### Step 0: Path Verification Gate (MANDATORY)

```
Validate ALL paths before any work:

  1. --source path EXISTS and is a directory
  2. --source contains code files (not empty)
  3. --target path does NOT exist (prevent overwrite)
  4. --source ≠ --target (prevent self-overwrite)
  5. --source is not inside --target or vice versa
  6. Working directory matches expected project context

IF any check fails:
  Display error with specific violation
  STOP — do not proceed

SAFETY RULE: Source folder is READ-ONLY for the entire pipeline.
  - Autopsy documents write to {source}/.phoenix/ (metadata only)
  - All code writes go to {target}/
  - No file in {source}/ outside .phoenix/ is ever modified
```

### Step 1: Display Phoenix Banner

```
+--------------------------------------------------------------+
| PHOENIX REBUILD                                                |
+--------------------------------------------------------------+
|                                                                |
|  Source: {source_path}                                         |
|  Target: {target_path}                                         |
|  Mode: {same-stack | migration}                                |
|  Focus: {all | subsystem}                                      |
|                                                                |
|  Pipeline:                                                     |
|    Phase 1: AUTOPSY    — Map the mess                         |
|    Phase 2: INTENT     — Extract what it was trying to do      |
|    Phase 3: CLARIFY    — Ask user about ambiguities            |
|    Phase 4: VISION     — Design the clean architecture         |
|    Phase 5: REBUILD    — Build it right                        |
|    Phase 6: COMPARISON — Prove it's better                     |
|                                                                |
|  Safety: Source is READ-ONLY. All writes go to target.         |
|                                                                |
+--------------------------------------------------------------+
```

IF `--dry-run`:
```
DRY RUN — will execute Phases 1-3 only (Autopsy + Intent + Clarify).
No rebuild will occur. Remove --dry-run to execute full pipeline.
```

---

### Phase 1: AUTOPSY — Map the Mess

> Understand the source codebase structure, stack, and problems.

```
Create directory: {source}/.phoenix/autopsy/

Reuse /fire-map-codebase infrastructure:
  Spawn 4 parallel mapper agents targeting {source}/:

  Agent 1 (tech):
    Focus: Technology stack, frameworks, libraries, versions
    Output: {source}/.phoenix/autopsy/STACK.md

  Agent 2 (arch):
    Focus: Architecture patterns, data flow, entry points
    Output: {source}/.phoenix/autopsy/ARCHITECTURE.md

  Agent 3 (quality):
    Focus: Code quality, anti-patterns, test coverage, error handling
    Output: {source}/.phoenix/autopsy/CONCERNS.md

  Agent 4 (concerns):
    Focus: External integrations, APIs, services, databases
    Output: {source}/.phoenix/autopsy/INTEGRATIONS.md

Additionally, the orchestrator produces:

  {source}/.phoenix/autopsy/STRUCTURE.md:
    - Full directory tree (2 levels deep)
    - Entry point files identified
    - Config files listed

  {source}/.phoenix/autopsy/SOURCE-METRICS.md:
    - Total files by extension
    - LOC per file (sorted descending)
    - Dependency list from package.json / requirements.txt / etc.
    - Largest files flagged (>300 LOC)

  IF git history available:
    {source}/.phoenix/autopsy/GIT-HISTORY.md:
      - Last 20 commits with messages
      - Most-changed files (hotspots)
      - Contributors
```

**Completion gate:** All 7 autopsy documents exist and are non-empty.

---

### Phase 2: INTENT EXTRACTION — What Was It Trying to Do?

> **Reference:** @agents/fire-phoenix-analyst.md

```
Spawn 2 fire-phoenix-analyst instances:

  Instance 1 — Feature Analyst:
    Input: All autopsy documents + source code access
    Process: Steps 1-5 from fire-phoenix-analyst.md
    Output: {source}/.phoenix/INTENT.md
      - Project-level intent
      - Technology stack table
      - Feature inventory (per-feature: intent, uniqueness, quality,
        classification, confidence, edge cases, dependencies)
      - Data model intent
      - Business rules catalog
      - Accidental vs essential complexity
      - Items needing clarification

  Instance 2 — Architecture Analyst:
    Input: All autopsy documents + source code access
    Process: Step 6 from fire-phoenix-analyst.md
    Output: {source}/.phoenix/INTENT-GRAPH.md
      - Code → Intent → Clean mapping for all major features
      - Anti-pattern replacement map
      - Current vs target architecture
      - Migration notes
```

**Honesty Protocol:** Both instances apply the Three Questions before analysis. LOW confidence items are flagged, not fabricated.

**Completion gate:** Both INTENT.md and INTENT-GRAPH.md exist with non-empty feature inventories.

---

### Phase 3: CLARIFICATION — Resolve Ambiguities

```
Read {source}/.phoenix/INTENT.md

Collect items needing clarification:
  1. Features with confidence: LOW
  2. Features with classification: UNKNOWN
  3. Edge cases with uncertain KEEP/KILL
  4. Items in the "Items Needing Clarification" section

Additionally, ask:
  "Which features do you NOT want in the rebuild?"
  "Are there any new features or changes you want added?"

Batch questions into rounds (max 3 rounds, 3-4 questions each):

  Round 1: Critical ambiguities (HIGH uniqueness features with LOW confidence)
  Round 2: Feature scope (what to keep, what to drop, what to add)
  Round 3: Remaining clarifications (MEDIUM uniqueness features)

Use AskUserQuestion for each round.

After each round:
  Update {source}/.phoenix/INTENT.md with answers
  Mark clarified items with confidence: HIGH (CLARIFIED)

IF --focus specified:
  Only ask about features in the focused subsystem
  Mark out-of-focus features as "DEFERRED — out of scope for this rebuild"
```

**Completion gate:** No HIGH-uniqueness features remain at confidence: LOW.

---

### Phase 4: VISION — Design the Clean Architecture

```
IF --migrate:
  Spawn fire-vision-architect (if available) with:
    Input: INTENT.md, INTENT-GRAPH.md
    Task: Propose 2-3 technology stack alternatives
    Output: {target}/.planning/VISION.md with stack branches

  Present branches to user via AskUserQuestion:
    "Which technology stack for the rebuild?"
    Options: [branch summaries with trade-offs]

ELSE (same-stack rebuild — default):
  Auto-generate {target}/.planning/VISION.md:
    - Same technology stack as source (from STACK.md)
    - Clean architecture based on INTENT-GRAPH.md target architecture
    - Phase breakdown derived from INTENT.md feature inventory

Phase breakdown strategy (from PHOENIX_REBUILD_METHODOLOGY):
  Phase 1: FOUNDATION
    - Project scaffold, config, types/interfaces, database schema
    - Environment setup, CI/CD skeleton
  Phase 2: CORE
    - Features with uniqueness CRITICAL and HIGH
    - Ordered by dependency (foundations first)
  Phase 3: SUPPORT
    - Features with uniqueness MEDIUM
    - Ordered by dependency on CORE features
  Phase 4: STANDARD
    - Features with uniqueness LOW and BOILERPLATE
    - Often auto-generated or minimal effort
  Phase 5: INTEGRATION
    - Wire everything together
    - Cross-module flows, API contracts
  Phase 6: HARDENING
    - Error handling, logging, security, edge cases
    - All "KEEP" edge cases from INTENT.md
  Phase 7: TESTING
    - Tests written from INTENT.md assertions
    - Feature parity verification
  Phase 8: DOCUMENTATION
    - README, API docs, deployment guide

Write {target}/.planning/VISION.md with:
  - Project metadata (name, description, stack)
  - Architecture description
  - Phase list with descriptions
  - Success criteria per phase
  - Phoenix verification checks (PX-1 through PX-5)
```

**Initialize target project:**
```
Create {target}/ directory
Create {target}/.planning/ structure:
  .planning/
    VISION.md (just created)
    CONSCIENCE.md (initialized empty)
    MEMORY.md (populated from INTENT.md context)
    phases/ (empty — fire-2-plan creates phase dirs)
```

**Completion gate:** VISION.md exists with phases. Target directory initialized.

---

### Phase 5: REBUILD — Build It Right

> Standard Dominion Flow pipeline, with INTENT.md as the requirements source.

```
FOR each phase in VISION.md (Phase 1 through Phase 8):

  Display:
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    " PHOENIX REBUILD: Phase {N} — {phase_name}"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  Working directory: {target}/

  // ── PLAN ──
  Run /fire-2-plan {N}
    Planner reads INTENT.md as requirements source (via MEMORY.md reference)
    Planner reads INTENT-GRAPH.md for clean implementation guidance
    BLUEPRINT frontmatter includes:
      phoenix_source: "{source_path}"
      phoenix_intent: "{source}/.phoenix/INTENT.md"
      phoenix_checks: [PX-1, PX-2, PX-3, PX-4, PX-5]
      scope_manifest:
        read_allowed: ["{source}/"] # read-only reference
        write_allowed: ["{target}/"]
        forbidden: ["modify {source}/ files"]

  // ── EXECUTE ──
  Run /fire-3-execute {N} --auto-continue
    Executor follows BLUEPRINT tasks
    Source folder referenced as READ-ONLY for code patterns
    All writes go to {target}/

  // ── VERIFY ──
  Run /fire-4-verify {N}
    Standard verification PLUS Phoenix-specific checks:

    PX-1: Feature Parity (weight: 30%)
      FOR each feature in INTENT.md:
        Check: is it implemented in {target}/ OR explicitly marked as dropped?
      Score: implemented_count / total_features * 100

    PX-2: Edge Case Coverage (weight: 25%)
      FOR each edge case marked "KEEP" in INTENT.md:
        Check: is it handled in {target}/ code?
      Score: handled_count / keep_count * 100

    PX-3: Dependency Compatibility (weight: 20%)
      FOR each external integration in INTEGRATIONS.md:
        Check: is the connection configured in {target}/?
      Score: connected_count / total_integrations * 100

    PX-4: Accidental Complexity Removal (weight: 15%)
      FOR each anti-pattern in INTENT-GRAPH.md:
        Check: is the anti-pattern ABSENT from {target}/?
      Score: absent_count / total_antipatterns * 100

    PX-5: Architecture Improvement (weight: 10%)
      Compare: target file structure vs source
      Check: smaller avg file size, proper separation, consistent naming
      Score: qualitative assessment 0-100

    Phoenix Score = (PX-1 * 0.30) + (PX-2 * 0.25) + (PX-3 * 0.20)
                  + (PX-4 * 0.15) + (PX-5 * 0.10)

  // ── EVALUATE ──
  IF verifier_verdict == APPROVED or CONDITIONAL:
    Advance to next phase
    git add -A && git commit -m "phoenix: Phase {N} - {phase_name} complete"

  ELSE (REJECTED):
    attempt += 1
    IF attempt < 3:
      Re-plan with --gaps flag, re-execute
    ELSE:
      Display blocker, STOP with escalation options
```

**Safety during rebuild:**
```
ENFORCED throughout Phase 5:
  - Source folder is READ-ONLY (scope manifest forbidden list)
  - Circuit breaker active (CIRCUIT_BREAKER_INTELLIGENCE thresholds)
  - HAC enforcement active
  - Path verification on every phase
  - Kill conditions checked before retries
```

**Completion gate:** All rebuild phases reach APPROVED or CONDITIONAL verdict.

---

### Phase 6: COMPARISON — Prove It's Better

> **Reference:** @templates/phoenix-comparison.md

```
Gather metrics from both projects:

  Source metrics:
    - Total files, LOC, avg/max file size
    - Dependency count (from package.json / requirements.txt)
    - Test file count, coverage estimate
    - Anti-pattern count (from INTENT-GRAPH.md)

  Target metrics:
    - Same measurements from {target}/
    - Phoenix verification scores (PX-1 through PX-5)

Write {target}/.planning/PHOENIX-COMPARISON.md using template:
  @templates/phoenix-comparison.md

Calculate final Phoenix Score:
  90%+ = APPROVED — Rebuild is production-ready
  75-89% = CONDITIONAL — Minor fixes needed
  <75% = REJECTED — Significant gaps, review INTENT.md coverage
```

**Display completion banner:**
```
+--------------------------------------------------------------+
| PHOENIX REBUILD COMPLETE                                       |
+--------------------------------------------------------------+
|                                                                |
|  Source: {source_path}                                         |
|  Target: {target_path}                                         |
|                                                                |
|  Before → After:                                               |
|    Files:        {N} → {N} ({change})                          |
|    Lines of Code: {N} → {N} ({change})                         |
|    Dependencies:  {N} → {N} ({change})                         |
|    Test Files:    {N} → {N} ({change})                         |
|    Max File Size: {N} → {N} ({change})                         |
|                                                                |
|  Phoenix Score: {score}% — {verdict}                           |
|    PX-1 Feature Parity:     {score}%                           |
|    PX-2 Edge Case Coverage:  {score}%                          |
|    PX-3 Dependency Compat:   {score}%                          |
|    PX-4 Complexity Removal:  {score}%                          |
|    PX-5 Architecture:        {score}%                          |
|                                                                |
|  Reports:                                                      |
|    {source}/.phoenix/INTENT.md                                 |
|    {source}/.phoenix/INTENT-GRAPH.md                           |
|    {target}/.planning/PHOENIX-COMPARISON.md                    |
|                                                                |
+--------------------------------------------------------------+
| NEXT STEPS                                                     |
+--------------------------------------------------------------+
|                                                                |
|  /fire-dashboard              — View project status            |
|  /fire-4-verify {N}           — Detailed phase verification    |
|  /fire-phoenix --dry-run      — Re-analyze without rebuilding  |
|                                                                |
+--------------------------------------------------------------+
```

IF `--dry-run`:
```
+--------------------------------------------------------------+
| PHOENIX DRY RUN COMPLETE                                       |
+--------------------------------------------------------------+
|                                                                |
|  Analysis produced:                                            |
|    {source}/.phoenix/autopsy/ (7 documents)                    |
|    {source}/.phoenix/INTENT.md                                 |
|    {source}/.phoenix/INTENT-GRAPH.md                           |
|                                                                |
|  Features found: {N} ({N unique, {N ambiguous})                |
|  Edge cases cataloged: {N} ({N keep, {N kill})                 |
|  Anti-patterns detected: {N}                                   |
|  Clarifications resolved: {N}                                  |
|                                                                |
|  To proceed with rebuild:                                      |
|    /fire-phoenix --source {source}                             |
|                                                                |
+--------------------------------------------------------------+
```

---

## Blocker Handling

```
IF any phase fails after max attempts:

+--------------------------------------------------------------+
| PHOENIX REBUILD STOPPED — BLOCKER                              |
+--------------------------------------------------------------+
|                                                                |
|  Completed phases: {list}                                      |
|  Blocked at: Rebuild Phase {N} — {name}                        |
|                                                                |
|  Blocker: {description}                                        |
|                                                                |
|  What was tried:                                               |
|    Attempt 1: {verdict} ({score}/70)                           |
|    Attempt 2: {verdict} ({score}/70)                           |
|    Attempt 3: {verdict} ({score}/70)                           |
|                                                                |
|  Options:                                                      |
|    A) /fire-debug — Investigate the blocker                   |
|    B) /fire-3-execute {N} — Manual execution                  |
|    C) /fire-phoenix --source {source} — Restart               |
|    D) /fire-dashboard — Review current state                  |
|                                                                |
+--------------------------------------------------------------+
```

---

## Safety Guarantees

```
NEVER DISABLED during Phoenix Rebuild:

  1. Source READ-ONLY — No file in {source}/ (except .phoenix/) is ever modified
  2. Path Verification — Source ≠ target, no nesting, paths exist
  3. Scope Manifests — Every rebuild phase has explicit read/write boundaries
  4. Circuit Breaker — CIRCUIT_BREAKER_INTELLIGENCE thresholds active
  5. HAC Enforcement — Known-bad actions blocked before execution
  6. Verification — fire-verifier + Phoenix checks (PX-1 through PX-5)

WHAT .phoenix/ CONTAINS (only metadata written to source):
  .phoenix/
    autopsy/          — 7 analysis documents (stack, arch, concerns, etc.)
    INTENT.md         — Extracted feature intent
    INTENT-GRAPH.md   — Code → Intent → Clean mapping

ALL CODE writes go to {target}/ exclusively.
```

---

## Examples

```bash
# Basic same-stack rebuild
/fire-phoenix --source C:/Projects/my-messy-app

# Custom target path
/fire-phoenix --source ./old-app --target ./old-app-v2

# Analyze only (no rebuild)
/fire-phoenix --source ./app --dry-run

# Focus on auth subsystem
/fire-phoenix --source ./app --focus auth

# Stack migration (propose new tech)
/fire-phoenix --source ./express-app --migrate
```

---

## Agent & Skill References

| Component | Role in Pipeline |
|-----------|-----------------|
| **fire-phoenix-analyst** (agent) | Phase 2 — Extracts INTENT.md and INTENT-GRAPH.md |
| **fire-codebase-mapper** (agent) | Phase 1 — Reused for autopsy mapping |
| **fire-planner** (agent) | Phase 5 — Plans each rebuild phase from INTENT.md |
| **fire-executor** (agent) | Phase 5 — Executes rebuild tasks |
| **fire-verifier** (agent) | Phase 5 — Verifies + Phoenix checks (PX-1 to PX-5) |
| **PHOENIX_REBUILD_METHODOLOGY** (skill) | Knowledge base — intent extraction, anti-patterns, edge cases |
| **GOF_DESIGN_PATTERNS_FOR_AI_AGENTS** (skill) | Architecture reference for clean rebuild |
| **CIRCUIT_BREAKER_INTELLIGENCE** (skill) | Stuck-state handling during rebuild |
| **phoenix-comparison** (template) | Phase 6 — Before/after metrics report |

---

## Success Criteria

```
- [ ] Path verification gate validates source/target paths
- [ ] Source folder is never modified (except .phoenix/ metadata)
- [ ] Phase 1 produces 7 autopsy documents
- [ ] Phase 2 produces INTENT.md + INTENT-GRAPH.md
- [ ] Phase 2 applies Honesty Protocol (LOW confidence items flagged, not fabricated)
- [ ] Phase 3 resolves ambiguities via user questions (max 3 rounds)
- [ ] Phase 4 generates VISION.md with rebuild phases
- [ ] Phase 5 runs full Dominion Flow pipeline per rebuild phase
- [ ] Phase 5 includes Phoenix verification checks (PX-1 through PX-5)
- [ ] Phase 6 produces PHOENIX-COMPARISON.md with before/after metrics
- [ ] Phoenix Score calculated: 90%+ APPROVED, 75-89% CONDITIONAL, <75% REJECTED
- [ ] --dry-run stops after Phase 3 (analysis only)
- [ ] --migrate presents stack alternatives in Phase 4
- [ ] --focus limits analysis to specified subsystem
- [ ] Circuit breaker, HAC, scope manifests all active during rebuild
- [ ] Blocker escalation with clear options when max attempts exceeded
```

---

*Dominion Flow v12.2 — Phoenix Rebuild: burn the mess, rise production-ready.*
