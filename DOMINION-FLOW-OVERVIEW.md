# Dominion Flow v12.2 -- Complete System Overview

Bird's eye view of the entire Dominion Flow system.

**Three Pillars:** Honesty Gate (accept mistakes, never blame) · Live Breadcrumbs (each instance smarter than the last) · Zero-Friction Tooling (ideas in, working app out)

**v12.0 Research-Backed Enhancements:**
- Tiered Verification (fast gate before slow gate — shift-left)
- Stuck-State Classification (6 types, not just "stuck")
- Kill Conditions (Google X pattern — pre-defined trip conditions)
- Scope Manifests (AWS TBAC — bounded file/tool access per task)
- Implied Scenario Detection (composition reveals what specification omits)
- Requirements Decomposition (CMU SEI utility tree — Level 4 before execution)
- Articulation Protocol (rubber duck step — catches 30-40% of stuck cases)
- Sensitivity Analysis (rank failures by downstream impact, not frequency)

---

```
+==============================================================================+
|                        DOMINION FLOW v12.2 -- COMPLETE SYSTEM MAP             |
+==============================================================================+


===============================================================================
 1. THE LIFECYCLE -- How a project flows from idea to done (v12.0)
===============================================================================

  +-------------+    +--------------+    +--------------+    +--------------+
  | /fire-1a-new |--->| /fire-2-plan |--->| /fire-3-exec |--->|/fire-4-verify|
  |  New Project|    |  Plan Phase  |    | Execute Phase|    | Verify Phase |
  |  + Vision   |    |  [H] Honesty |    | [H] Honesty  |    | [H] Honesty  |
  +------+------+    +------+-------+    +------+-------+    +------+-------+
         |                  ^                    |                   |
    Visual Input?           |               Breath-based          Goal-backward
    Mode Gate               |               Execution           Verification
    Vision Architect        |               + Commits           + 70-point
    Zero-Friction CLI       |               + Playwright        + Playwright
    Roadmap                 |                    |                   |
         |                  |                    v                   v
         v                  |                RECORD.md        VERIFICATION.md
   PROJECT.md               |                    |                   |
   VISION.md (LOCKED)       |                    |              +----+----+
   CONSCIENCE.md            |                    |              |  PASS?  |
   TOOLING-LOG.md           |                    |              +----+----+
   breadcrumbs/             |                    |            yes/     \no
         |                  |                    |           /           \
  +------+------------------+--------------------+----------+   +----------------+
  |           NEXT PHASE / MILESTONE                        |   | RECOVERY LOOP  |
  |       (loop back to /fire-2-plan)                      |   | (v11.2)        |
  +--------------------------------------------------------+   |                |
                                                                | 1. Researcher  |
  LIVE BREADCRUMBS (v11.2) -- updated by ALL agents:            |    searches:   |
  +------------------------------------------------------+     |    Skills DB   |
  | breadcrumbs/LESSONS.md     -- what worked              |     |    Context7    |
  | breadcrumbs/FAILURES.md    -- what didn't + why        |     |    Web (last)  |
  | breadcrumbs/PATTERNS.md    -- recurring patterns       |     |                |
  | breadcrumbs/DEPENDENCIES.md -- env, packages, gotchas  |     | 2. Returns 2-3 |
  +------------------------------------------------------+     |    alternatives|
                                                                |    ranked by   |
  DEAD ENDS (v11.3 — merged into FAILURES.md):                   |    confidence  |
  +------------------------------------------------------+     |                |
  | breadcrumbs/FAILURES.md [DEAD-END] tagged entries      |     | 3. Planner     |
  |                                                        |     |    picks best  |
  | Agent hits wall (3+ attempts) --> SHELVE & move on     |     |    alternative |
  | Fresh Claude on /fire-6-resume --> reads shelf,        |     |    NEW blueprint|
  |   attempts highest-priority problem with clean context |     +-------+--------+
  +------------------------------------------------------+             |
                                                                        v
                                                                  back to /fire-2-plan
                                                                  (with new approach)

  AUTONOMOUS PATH (v9.0):
  +------------------------------------------------------------------+
  | /fire-autonomous                                                  |
  |                                                                  |
  | After /fire-1a-new completes, runs the ENTIRE pipeline:           |
  |   2-plan --> 3-execute --> 4-verify (per phase, all phases)      |
  | Auto-routes merge gate and review gate verdicts.                 |
  | Dead ends shelved mid-run, solved on next session.               |
  +------------------------------------------------------------------+

  PHOENIX REBUILD (v12.2):
  +------------------------------------------------------------------+
  | /fire-phoenix --source <path>                                     |
  |                                                                  |
  | Takes a messy "vibe coded" project and rebuilds it clean:        |
  |   AUTOPSY --> INTENT --> CLARIFY --> VISION --> REBUILD --> COMPARE|
  | Source is READ-ONLY. Rebuild goes to new target folder.          |
  | Extracts INTENT (what code was trying to do), asks user about    |
  | ambiguities, then rebuilds using full Dominion Flow pipeline.    |
  | Phoenix Score: PX-1 to PX-5 (feature parity, edge cases, etc.)  |
  +------------------------------------------------------------------+

  SESSION BOUNDARIES:
  +--------------+                              +--------------+
  |/fire-5-hand  |  === session break ===>      |/fire-6-resum |
  |   off        |   POWER-HANDOFF-*.md         |     e        |
  | Save context |   (WARRIOR 7-step)           | Load context |
  | + breadcrumbs|                              | + breadcrumbs|
  +--------------+                              +--------------+

  [H] = Honesty Gate -- mandatory 3-question checkpoint at every agent


===============================================================================
 2. ALL AGENTS -- Who does what
===============================================================================

  AGENT FILE                    DESCRIPTION                           SPAWNED BY
  ----------                    -----------                           ----------
  fire-executor.md              Executes plans with honesty           /fire-3-execute
                                protocols, atomic commits,            /fire-execute-plan
                                creates RECORD.md handoffs            /fire-autonomous

  fire-planner.md               Creates phase plans with skills       /fire-2-plan
                                library integration and               /fire-autonomous
                                WARRIOR validation

  fire-researcher.md            Researches phase context using        /fire-research
                                skills library, pattern matching,     /fire-1a-new
                                and external search. In RECOVERY      /fire-2-plan
                                MODE (v11.2): 3-tier cascade          /fire-planner (on failure)
                                (Skills→Context7→Web) returns         /fire-4-verify (gap research)
                                2-3 ranked alternatives.

  fire-verifier.md              Must-haves verification +             /fire-4-verify
                                WARRIOR 70-point validation           /fire-3-execute

  fire-reviewer.md              Independent code review --            /fire-7-review
                                architecture, patterns, perf,         /fire-3-execute
                                maintainability, security             (parallel with verifier)

  fire-vision-architect.md      Generates 2-3 competing               /fire-1a-new
                                architecture vision branches.         /fire-new-milestone
                                Anti-Frankenstein gate prevents
                                incompatible stack combos.

  fire-phoenix-analyst.md       Reverse-engineers developer intent    /fire-phoenix
                                from messy codebases. Extracts what
                                code was TRYING to do. Produces
                                INTENT.md + INTENT-GRAPH.md.


  AGENT CAPABILITIES:
  +-------------------------+----------+-------+------+------+------+---------+----------+
  | Agent                   | Read     | Write | Edit | Bash | Grep | Web     | Context7 |
  +-------------------------+----------+-------+------+------+------+---------+----------+
  | fire-executor           |    Y     |   Y   |  Y   |  Y   |  Y   |         |          |
  | fire-planner            |    Y     |   Y   |      |  Y   |  Y   | Fetch   |    Y     |
  | fire-researcher         |    Y     |   Y   |      |  Y   |  Y   | Both    |    Y     |
  | fire-verifier           |    Y     |       |      |  Y   |  Y   |         |          |
  | fire-reviewer           |    Y     |       |      |  Y   |  Y   |         |          |
  | fire-vision-architect   |    Y     |   Y   |      |      |  Y   |         |          | ← Forward + Backward modes
  | fire-phoenix-analyst    |    Y     |   Y   |      |  Y   |  Y   |         |          | ← Intent extraction
  +-------------------------+----------+-------+------+------+------+---------+----------+


===============================================================================
 3. BREATH EXECUTION -- How /fire-3-execute parallelizes work
===============================================================================

  BLUEPRINT.md files have frontmatter:  breath: 1, breath: 2, breath: 3 ...

  +---------------------------------------------------------+
  | BREATH 1 (parallel)                                       |
  |                                                         |
  |  +-------------+  +-------------+  +-------------+     |
  |  | Plan 01-01  |  | Plan 01-02  |  | Plan 01-03  |     |
  |  | Foundation  |  | Schema      |  | Config      |     |
  |  |             |  |             |  |             |     |
  |  | executor <--|  | executor <--|  | executor <--|     |
  |  +------+------+  +------+------+  +------+------+     |
  |         |                |                |             |
  |         v                v                v             |
  |      commit           commit           commit           |
  +--------------------------+------------------------------+
                             | all complete
                             v
  +---------------------------------------------------------+
  | BREATH 2 (depends on breath 1)                              |
  |                                                         |
  |  +-------------+  +-------------+                      |
  |  | Plan 01-04  |  | Plan 01-05  |                      |
  |  | API Routes  |  | Auth Flow   |                      |
  |  |             |  |             |                      |
  |  | executor <--|  | executor <--|                      |
  |  +------+------+  +------+------+                      |
  |         |                |                              |
  |         v                v                              |
  |      commit           commit                            |
  +--------------------------+------------------------------+
                             | all complete
                             v
  +---------------------------------------------------------+
  | BREATH 3                                                  |
  |  +-------------+                                        |
  |  | Plan 01-06  |     Then: fire-verifier runs          |
  |  | UI + Tests  |     70-point validation on everything  |
  |  +-------------+     + fire-reviewer in parallel (v8.0) |
  +---------------------------------------------------------+

  MODE SELECTION (auto per breath):
  +------------------------------------------------------+
  | 1 plan in breath  --> Sequential (single executor)     |
  | 2+ plans, no file overlap --> Parallel (Task tool)   |
  | 2+ plans, file overlap --> Sequential (safe)         |
  | 3+ plans, no overlap --> Team/Swarm mode             |
  +------------------------------------------------------+


===============================================================================
 4. NEW PROJECT FLOW -- 3-command chain
===============================================================================

  /fire-1a-new  -->  /fire-1b-research  -->  /fire-1c-setup
  (scaffold)       (research+vision)      (tooling+finalize)

  Each command is <250 lines so agents follow every step.
  Each command gates on the previous (checks files exist).

  ┌─────────────────────────────────────────────────────┐
  │  /fire-1a-new (Steps 1-3)                            │
  │                                                     │
  │  User: "/fire-1a-new My LMS Platform"                │
  │         |                                           │
  │         v                                           │
  │  +----------------------+                           │
  │  | Adaptive Questioning |  "What's the core value?" │
  │  | (5-15 questions)     |  "Who are the users?"     │
  │  +----------+-----------+                           │
  │             |                                       │
  │             v                                       │
  │  +-----------------------------------------+        │
  │  | MODE GATE: "Have you already started    |        │
  │  |  building, or starting from scratch?"   |        │
  │  +--------+------------------+-------------+        │
  │           |                  |                      │
  │    FORWARD MODE      BACKWARD MODE                  │
  │    (has tech)        (vibe coders)                   │
  │           |                  |                      │
  │           v                  v                      │
  │  +----------------------+                           │
  │  | Write PROJECT.md     |  Core value, constraints  │
  │  | Write REQUIREMENTS   |  REQ-IDs                  │
  │  | Create .planning/    |  breadcrumbs/ (on-demand)  │
  │  +----------+-----------+                           │
  │             |                                       │
  │  OUTPUT: 8 files (.planning/ scaffold)              │
  │  NEXT: "Run /fire-1b-research"                       │
  └─────────────────────────────────────────────────────┘
                    |
                    v
  ┌─────────────────────────────────────────────────────┐
  │  /fire-1b-research (Steps 3b-3d)                     │
  │                                                     │
  │  +-----------------------------------------------+  │
  │  | 4 PARALLEL RESEARCHERS (+ GitHub search)      |  │
  │  |  STACK | FEATURES | ARCHITECT | PITFALLS      |  │
  │  |  --> SYNTHESIS.md (merged + GitHub refs)       |  │
  │  +----------------------+------------------------+  │
  │                         v                           │
  │  +--------------------------------------------------│
  │  | fire-vision-architect                            │
  │  |  Anti-Frankenstein (forward) / Capability        │
  │  |  Extraction (backward) --> 2-3 branches          │
  │  |  User picks one --> VISION.md (LOCKED)           │
  │  |  Rejected --> ALTERNATIVES.md                    │
  │  +----------------------+---------------------------│
  │                         v                           │
  │  +--------------------------------------------------│
  │  | fire-roadmapper                                  │
  │  |  Reads LOCKED VISION.md (no stack changes)       │
  │  |  Requirements --> phases --> ROADMAP.md           │
  │  +--------------------------------------------------│
  │                                                     │
  │  OUTPUT: SYNTHESIS.md, VISION.md, ALTERNATIVES.md,  │
  │          ROADMAP.md                                  │
  │  NEXT: "Run /fire-1c-setup"                          │
  └─────────────────────────────────────────────────────┘
                    |
                    v
  ┌─────────────────────────────────────────────────────┐
  │  /fire-1c-setup (Steps 4-6 + FINAL)                  │
  │                                                     │
  │  WARRIOR handoff --> ~/.claude/warrior-handoffs/     │
  │  Zero-friction tooling --> install CLIs from VISION  │
  │  SKILLS-INDEX.md --> empty tracking                  │
  │  Update CONSCIENCE.md --> "Ready to plan"            │
  │                                                     │
  │  ┌─── MANDATORY FILE GATE ─────────────────────┐    │
  │  │ Verify ALL 16 files exist                    │    │
  │  │ If ANY missing --> abort, tell user which     │    │
  │  │ command to re-run                            │    │
  │  └─────────────────────────────────────────────┘    │
  │                                                     │
  │  OUTPUT: TOOLING-LOG.md, SKILLS-INDEX.md, handoff   │
  │  NEXT: "Run /fire-2-plan 1"                         │
  └─────────────────────────────────────────────────────┘


===============================================================================
 5. VERIFICATION SYSTEM -- Triple-layer validation (v12.0)
===============================================================================

  +---------------------------------------------------------+
  | TIER 1: FAST GATE (v12.0 — shift-left, seconds)         |
  |                                                         |
  |  Build compiles?  Types check?  Lint passes?            |
  |  Files exist?     Imports resolve?                      |
  |                                                         |
  |  IF ANY FAIL --> STOP. Don't run Tier 2 or 3.           |
  |  Catches 60%+ of failures in <30 seconds.               |
  +---------------------------------------------------------+
                          +
  +---------------------------------------------------------+
  | TIER 2: MUST-HAVES (Goal-Backward)                      |
  |                                                         |
  |  "What must be TRUE for this phase's goal?"             |
  |                                                         |
  |  Truths:     Observable behaviors users can verify      |
  |  Artifacts:  Files that must exist with specific exports|
  |  Key Links:  Components properly wired together         |
  |                                                         |
  |  Y User can log in with email/password                  |
  |  Y JWT token persists across browser sessions           |
  |  X Password reset email sends (FAIL -> gap plan)        |
  +---------------------------------------------------------+
                          +
  +---------------------------------------------------------+
  | TIER 3: WARRIOR 70-POINT CHECKLIST (scope-adaptive)     |
  |                                                         |
  |  Code Quality ........... /10   Performance ...... /10  |
  |  Testing ................ /10   Documentation .... /10  |
  |  Security ............... /10   Infrastructure ... /10  |
  |  E2E (Playwright) ...... /10                            |
  |                          ----                           |
  |                          /70 (max, adjusted per scope)  |
  |                                                         |
  |  Scoring: percentage of ACTIVE sections only (v11.3)   |
  |  90%+ = APPROVED    70-79% = CONDITIONAL                |
  |  80-89% = APPROVED*  <60%   = REJECTED                  |
  +---------------------------------------------------------+
                          +
  +---------------------------------------------------------+
  | POST-VERIFICATION (v12.0)                                |
  |                                                         |
  |  Implied Scenario Detection:                            |
  |    Positive (correct but unplanned) --> add to spec     |
  |    Negative (incorrect/unintended) --> CRITICAL GAP     |
  |                                                         |
  |  Failure Sensitivity Analysis:                          |
  |    Rank gaps by downstream impact (LOCAL < CASCADING)   |
  |    Fix CASCADING failures first                         |
  +---------------------------------------------------------+


===============================================================================
 6. FILE-BASED STATE MACHINE -- .planning/ directory
===============================================================================

  your-project/
  +-- .planning/
      +-- CONSCIENCE.md                    <-- Living project memory (updated constantly)
      +-- VISION.md                  <-- Phase overview + success criteria (LOCKED)
      +-- REQUIREMENTS.md             <-- REQ-IDs with traceability
      +-- PROJECT.md                  <-- Core value, users, constraints
      +-- TOOLING-LOG.md             <-- CLI tools installed + versions (v11.2)
      |
      +-- breadcrumbs/               <-- Live memory across agents (on-demand, v11.3)
      |   +-- LESSONS.md              <-- What worked (created on first write)
      |   +-- FAILURES.md             <-- What didn't + why + [DEAD-END] entries (created on first write)
      |   +-- PATTERNS.md             <-- Recurring patterns (created on first write)
      |   +-- DEPENDENCIES.md         <-- Env, packages, gotchas (created on first write)
      |
      +-- research/                   <-- Created by /fire-1a-new
      |   +-- STACK.md
      |   +-- FEATURES.md
      |   +-- ARCHITECTURE.md
      |   +-- PITFALLS.md
      |   +-- RECORD.md
      |   +-- ALTERNATIVES.md         <-- Rejected vision branches (v11.2)
      |
      +-- codebase/                   <-- Created by /fire-map-codebase
      |   +-- STACK.md
      |   +-- ARCHITECTURE.md
      |   +-- STRUCTURE.md
      |   +-- CONVENTIONS.md
      |   +-- TESTING.md
      |   +-- INTEGRATIONS.md
      |   +-- CONCERNS.md
      |
      +-- phases/
      |   +-- 01-foundation/
      |   |   +-- 01-01-BLUEPRINT.md       <-- Breath 1
      |   |   +-- 01-02-BLUEPRINT.md       <-- Breath 1
      |   |   +-- 01-03-BLUEPRINT.md       <-- Breath 2
      |   |   +-- 01-01-RECORD.md    <-- After execution
      |   |   +-- 01-VERIFICATION.md  <-- After /fire-4-verify
      |   |   +-- 01-REVIEW.md       <-- After /fire-7-review (v8.0)
      |   |   +-- 01-MEMORY.md       <-- From /fire-1d-discuss
      |   |
      |   +-- 02-authentication/
      |   |   +-- ...
      |   +-- 03-content/
      |       +-- ...
      |
      +-- debug/                      <-- Created by /fire-debug
      |   +-- login-fails.md
      |   +-- resolved/
      |       +-- api-timeout.md
      |
      +-- loops/                      <-- Created by /fire-loop
      |   +-- fire-loop-{ID}.md
      |   +-- sabbath-{ID}-iter{N}.md
      |
      +-- .shared-state.json          <-- SWARM inter-agent coordination (v9.0)
      +-- POWER-HANDOFF-2026-02-14.md <-- Session continuity


===============================================================================
 7. HOOKS & SESSION MANAGEMENT
===============================================================================

  +---------------------------------------------------------+
  | SESSION START                                           |
  |  +-- fire-check-update.js  (check for plugin updates) |
  |  +-- compact-reinject.js    (restore context on /compact|
  |                              re-injects WARRIOR state)  |
  +~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
  | STOP                                                    |
  |  +-- stop-verify.js         (warn if tasks incomplete)  |
  +~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
  | STATUSLINE (always visible)                             |
  |  +-- statusline.js          opus | current task | dir   |
  |                              ^ /fire-update | 45% ctx  |
  +---------------------------------------------------------+


===============================================================================
 8. SKILLS LIBRARY -- 478+ reusable patterns
===============================================================================

  +------------------+  +------------------+  +------------------+
  | advanced-features|  | api-patterns     |  | automation       |
  | (11 skills)      |  | (12 skills)      |  | (7 skills)       |
  +------------------+  +------------------+  +------------------+
  | database-solutions|  | deploy-security  |  | doc-processing   |
  | (12 skills)      |  | (17 skills)      |  | (5 skills)       |
  +------------------+  +------------------+  +------------------+
  | ecommerce        |  | form-solutions   |  | integrations     |
  | (15 skills)      |  | (8 skills)       |  | (20+ skills)     |
  | stripe,paypal,GTA|  |                  |  | stripe,zoom,yt   |
  +------------------+  +------------------+  +------------------+
  | lms-patterns     |  | methodology      |  | patterns-standard|
  | (30+ skills)     |  | (16 skills)      |  | (15 skills)      |
  +------------------+  +------------------+  +------------------+

  v12.0 RESEARCH-BACKED METHODOLOGY SKILLS (6 new):
  +-------------------------+  +-------------------------+  +-------------------------+
  | RELIABILITY_PREDICTION  |  | QUALITY_GATES_AND_      |  | CIRCUIT_BREAKER_        |
  | Implied scenarios,      |  | VERIFICATION            |  | INTELLIGENCE            |
  | sensitivity analysis,   |  | Tiered gates, risk-     |  | 6-type stuck class,     |
  | probability completeness|  | based testing, error    |  | kill conditions,        |
  |                         |  | budgets, DoR/DoD        |  | articulation protocol   |
  +-------------------------+  +-------------------------+  +-------------------------+
  | CONTEXT_ROTATION        |  | AUTONOMOUS_             |  | REQUIREMENTS_           |
  | Fresh-eyes science,     |  | ORCHESTRATION           |  | DECOMPOSITION           |
  | fixation prevention,    |  | Planner/Worker/Judge,   |  | Utility tree (L1→L4),   |
  | navigator pattern       |  | scope manifests, DORA   |  | ATAM tradeoffs, WDM     |
  +-------------------------+  +-------------------------+  +-------------------------+

  /fire-search "stripe webhook" --> finds matching skills
  /fire-add-new-skill           --> add from current session
  /fire-skills-history          --> git log of skill changes
  /fire-skills-rollback         --> revert to previous version


===============================================================================
 9. ALL 46 COMMANDS -- Organized by tier
===============================================================================

  TIER 1: CORE WORKFLOW      TIER 2: AUTONOMOUS       TIER 3: DEBUG/DISCOVERY
  ----------------------     -------------------      -----------------------
  /fire-1a-new               /fire-autonomous        /fire-debug
  /fire-1b-research          /fire-loop              /fire-discover
  /fire-1c-setup             /fire-loop-resume       /fire-map-codebase
  /fire-1d-discuss          /fire-loop-stop         /fire-0-orient
  /fire-2-plan               /fire-phoenix           /fire-research
  /fire-3-execute                                    /fire-brainstorm
  /fire-4-verify
  /fire-5-handoff
  /fire-6-resume

  TIER 4: VERIFICATION       TIER 5: SKILLS MGMT     TIER 6: ANALYTICS/PM
  ----------------------     -------------------      --------------------
  /fire-7-review            /fire-search            /fire-dashboard
  /fire-verify-uat          /fire-add-new-skill     /fire-analytics
  /fire-test                /fire-skills-sync       /fire-todos
  /fire-security-scan       /fire-skills-history    /fire-reflect
  /fire-vuln-scan           /fire-skills-rollback   /fire-assumptions
  /fire-double-check        /fire-skills-diff       /fire-transition

  TIER 7: MILESTONE/ADVANCED
  --------------------------
  /fire-new-milestone
  /fire-complete-milestone
  /fire-execute-plan
  /fire-update


===============================================================================
 10. THE BIG PICTURE -- Everything connected
===============================================================================

         +------------------------------------------------------+
         |                    YOU (the developer)                  |
         |   Ideas, screenshots, wireframes, decisions, approvals |
         +----------------------+-------------------------------+
                                |
                    +-----------v-----------+
                    |   46 SLASH COMMANDS    |
                    |   (Orchestrators)      |
                    +-----------+-----------+
                                | spawn
         +----------------------+----------------------+
         |                      |                      |
  +------v---------+   +-------v-------+   +-----------v------+
  |  RESEARCHERS   |   |   BUILDERS    |   |   VALIDATORS     |
  |                |   |               |   |                  |
  | fire-researcher|   | fire-executor |   | fire-verifier    |
  | fire-vision-   |   | fire-planner  |   | fire-reviewer    |
  |   architect    |   |               |   |                  |
  +------+---------+   +-------+-------+   +--------+---------+
         |                     |                     |
         |     [H] HONESTY GATE at every agent [H]   |
         |                     |                     |
         |     +---------------v--------------+      |
         +---->|   .planning/ STATE           |<-----+
               |   + breadcrumbs/ (on-demand)  |
               |   + TOOLING-LOG.md           |
               +---------------+--------------+
                               |
               +---------------v--------------+
               |   478+ SKILLS LIBRARY        |
               |   (proven patterns)          |
               +---------------+--------------+
                               |
               +---------------v--------------+
               |  WARRIOR HANDOFFS            |
               |  + breadcrumbs preserved     |
               |  + dead ends documented      |
               |  (session continuity)        |
               +------------------------------+
```

---

## Version History

| Version | Date | Headline Features |
|---------|------|-------------------|
| v12.2 | 2026-03-06 | Phoenix Rebuild: `/fire-phoenix` autonomous rebuild from messy-to-clean. fire-phoenix-analyst agent (intent extraction), PHOENIX_REBUILD_METHODOLOGY skill (anti-pattern map, intent graph, edge case protocol), GOF_DESIGN_PATTERNS_FOR_AI_AGENTS skill, phoenix-comparison template, PX-1 to PX-5 verification checks |
| v12.1 | 2026-03-06 | v12.0 audit fixes: Tier naming alignment, DORA metrics in autonomous, Requirements Decomposition in discuss, researcher skill awareness, circuit breaker weight alignment |
| v12.0 | 2026-03-06 | Research-backed upgrade: 6 new methodology skills (Reliability Prediction, Quality Gates, Circuit Breaker Intelligence, Context Rotation, Autonomous Orchestration, Requirements Decomposition), tiered verification, stuck-state classification, kill conditions, scope manifests, implied scenario detection |
| v11.2 | 2026-03-06 | Branching Vision System + Honesty Gate + Zero-Friction CLI + Dead Ends Shelf: fire-vision-architect (Forward + Backward modes), Anti-Frankenstein gate, Visual Input fast-track (screenshots/wireframes/sketches), BACKWARD_PLANNING_INTERVIEW (10 beginner questions), ZERO_FRICTION_CLI_SETUP (auto-install all tools from VISION.md), DevTools guide for beginners, Honesty Gate universal enforcement (slim 10-line gates referencing canonical protocol), Live Breadcrumb Protocol (LESSONS/FAILURES/PATTERNS/DEPENDENCIES), Dead Ends Shelf (DEAD-ENDS.md — shelve unsolved problems, fresh instance retries on resume), Recovery Research Loop (Skills→Context7→Web), Verifier isolation (fresh instance), Playwright MCP non-negotiable |
| v9.1 | 2026-02-24 | Research-backed intelligence: ReflexTree debugging, MAKER reasoning sharing, MemP failure memory, ATLAS agent selection, CriticGPT review profiles |
| v1.0 | 2026-01 | Initial 6-command workflow (new, plan, execute, verify, handoff, resume) |
| v2.0 | 2026-01 | Skills library integration, breath-based parallel execution |
| v3.0 | 2026-02 | Circuit breaker, error classification, Sabbath Rest, context engineering |
| v3.3 | 2026-02 | Decision-time guidance, .powerignore, recitation pattern |
| v4.0 | 2026-02 | 75 skills, cleansing cycle, evolutionary synthesis |
| v5.0 | 2026-02 | Confidence gates, self-judge, debug replay, SDFT self-distillation, Path Verification Gate |
| v6.0 | 2026-02 | Episodic auto-injection (CoALA), utility scoring (ReMe), GCC checkpoints, turn-level rewards (AgentPRM), behavioral directives |
| v7.0 | 2026-02 | Difficulty-aware routing, predicate-form rules with HAC, AUQ confidence propagation, failure taxonomy (AgentDebug), dual-replay (AgentRR) |
| v8.0 | 2026-02 | Parallel review gate (verifier + reviewer), combined verdict matrix, post-loop review gate, version performance tracking, failure memory collection |
| v9.0 | 2026-02 | /fire-autonomous full autopilot, 39 commands, inter-agent shared state, task-level resume, graceful Qdrant degradation, semantic progress metrics |

---

*Generated 2026-03-06 -- Dominion Flow v12.2*
