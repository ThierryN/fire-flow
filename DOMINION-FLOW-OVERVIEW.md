# Dominion Flow v10.0 -- Complete System Overview

Bird's eye view of the entire Dominion Flow system.

---

```
+==============================================================================+
|                        DOMINION FLOW v10.0 -- COMPLETE SYSTEM MAP             |
+==============================================================================+


===============================================================================
 1. THE LIFECYCLE -- How a project flows from idea to done
===============================================================================

  +-------------+    +--------------+    +--------------+    +--------------+
  | /fire-1-new|--->| /fire-2-plan|--->|/fire-3-exec |--->|/fire-4-verify|
  |  New Project|    |  Plan Phase  |    |Execute Phase |    | Verify Phase |
  +------+------+    +------+-------+    +------+-------+    +------+-------+
         |                  |                    |                   |
    Questions          Research &            Breath-based          Goal-backward
    Research           Planning              Execution           Verification
    Roadmap            + Checking            + Commits           + 70-point
         |                  |                    |                   |
         v                  v                    v                   v
   PROJECT.md          BLUEPRINT.md              RECORD.md        VERIFICATION.md
   VISION.md                                                       |
   CONSCIENCE.md                                                         |
         |                                                     +----+----+
         |                                                     |  PASS?  |
         |                                                     +----+----+
         |                                                   yes/     \no
         |                                                  /           \
  +------+--------------------------------------------------+    +----------+
  |                  NEXT PHASE / MILESTONE                  |    | Gap Plans|
  |              (loop back to /fire-2-plan)                |    | fix & re-|
  +-----------------------------------------------------+    | verify   |
                                                                  +----------+

  AUTONOMOUS PATH (v9.0):
  +------------------------------------------------------------------+
  | /fire-autonomous                                                  |
  |                                                                  |
  | After /fire-1-new completes, runs the ENTIRE pipeline:           |
  |   2-plan --> 3-execute --> 4-verify (per phase, all phases)      |
  | Auto-routes merge gate and review gate verdicts.                 |
  | No human checkpoints required.                                   |
  +------------------------------------------------------------------+

  SESSION BOUNDARIES:
  +--------------+                              +--------------+
  |/fire-5-hand |  === session break ===>      |/fire-6-resum|
  |   off        |   POWER-HANDOFF-*.md         |     e        |
  | Save context |   (WARRIOR 7-step)           | Load context |
  +--------------+                              +--------------+


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
                                skills library, pattern matching,     /fire-1-new
                                and external search                   /fire-2-plan

  fire-verifier.md              Must-haves verification +             /fire-4-verify
                                WARRIOR 70-point validation           /fire-3-execute

  fire-reviewer.md              Independent code review --            /fire-7-review
                                architecture, patterns, perf,         /fire-3-execute
                                maintainability, security             (parallel with verifier)


  AGENT CAPABILITIES:
  +-------------------------+----------+-------+------+------+------+---------+----------+
  | Agent                   | Read     | Write | Edit | Bash | Grep | Web     | Context7 |
  +-------------------------+----------+-------+------+------+------+---------+----------+
  | fire-executor           |    Y     |   Y   |  Y   |  Y   |  Y   |         |          |
  | fire-planner            |    Y     |   Y   |      |  Y   |  Y   | Fetch   |    Y     |
  | fire-researcher         |    Y     |   Y   |      |  Y   |  Y   | Both    |    Y     |
  | fire-verifier           |    Y     |       |      |  Y   |  Y   |         |          |
  | fire-reviewer           |    Y     |       |      |  Y   |  Y   |         |          |
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
 4. NEW PROJECT FLOW -- /fire-1-new deep dive
===============================================================================

  User: "/fire-1-new My LMS Platform"
         |
         v
  +----------------------+
  | Adaptive Questioning |   "What's the core value?"
  | (5-15 questions)     |   "Who are the users?"
  |                      |   "What's v1 scope?"
  +----------+-----------+
             v
  +----------------------+
  | Write PROJECT.md     |   Core value, constraints, users
  | Write REQUIREMENTS   |   REQ-IDs: AUTH-01, CONT-01, etc.
  +----------+-----------+
             v
  +-------------------------------------------------------------+
  | 4 PARALLEL RESEARCHERS (fire-project-researcher x4)         |
  |                                                             |
  |  +----------+ +----------+ +----------+ +----------+      |
  |  | STACK    | | FEATURES | | ARCHITECT| | PITFALLS |      |
  |  | research | | research | | research | | research |      |
  |  +----+-----+ +----+-----+ +----+-----+ +----+-----+      |
  |       |            |            |            |              |
  |       v            v            v            v              |
  |   STACK.md    FEATURES.md  ARCHITECT.md  PITFALLS.md       |
  +-----------------------+-------------------------------------+
                          v
  +----------------------------------+
  | fire-research-synthesizer        |
  | Merges 4 files -> RECORD.md     |
  +------------------+---------------+
                     v
  +----------------------------------+
  | fire-roadmapper                  |
  |                                  |
  |  Requirements -> Phase grouping  |
  |  Dependencies -> Ordering        |
  |  Goal-backward -> Success crit.  |
  |  Coverage validation (100%)      |
  |                                  |
  |  Output: VISION.md + CONSCIENCE  |
  +----------------------------------+


===============================================================================
 5. VERIFICATION SYSTEM -- Dual-layer validation
===============================================================================

  +---------------------------------------------------------+
  | LAYER 1: MUST-HAVES (Goal-Backward)                     |
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
  | LAYER 2: WARRIOR 70-POINT CHECKLIST                     |
  |                                                         |
  |  Code Quality ........... /10   Performance ...... /10  |
  |  Testing ................ /10   Documentation .... /10  |
  |  Security ............... /10   Infrastructure ... /10  |
  |  E2E (Playwright) ...... /10                            |
  |                          ----                           |
  |                          /70                            |
  |                                                         |
  |  63-70 = APPROVED    49-55 = CONDITIONAL                |
  |  56-62 = APPROVED*   <42   = REJECTED                   |
  +---------------------------------------------------------+


===============================================================================
 6. FILE-BASED STATE MACHINE -- .planning/ directory
===============================================================================

  your-project/
  +-- .planning/
      +-- CONSCIENCE.md                    <-- Living project memory (updated constantly)
      +-- VISION.md                  <-- Phase overview + success criteria
      +-- REQUIREMENTS.md             <-- REQ-IDs with traceability
      +-- PROJECT.md                  <-- Core value, users, constraints
      |
      +-- research/                   <-- Created by /fire-1-new
      |   +-- STACK.md
      |   +-- FEATURES.md
      |   +-- ARCHITECTURE.md
      |   +-- PITFALLS.md
      |   +-- RECORD.md
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
      |   |   +-- 01-MEMORY.md       <-- From /fire-1a-discuss
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
 8. SKILLS LIBRARY -- 190+ reusable patterns
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
  | (30+ skills)     |  | (10 skills)      |  | (15 skills)      |
  +------------------+  +------------------+  +------------------+

  /fire-search "stripe webhook" --> finds matching skills
  /fire-add-new-skill           --> add from current session
  /fire-skills-history          --> git log of skill changes
  /fire-skills-rollback         --> revert to previous version


===============================================================================
 9. ALL 39 COMMANDS -- Organized by tier
===============================================================================

  TIER 1: CORE WORKFLOW      TIER 2: AUTONOMOUS       TIER 3: DEBUG/DISCOVERY
  ----------------------     -------------------      -----------------------
  /fire-1-new               /fire-autonomous        /fire-debug
  /fire-1a-discuss          /fire-loop              /fire-discover
  /fire-2-plan              /fire-loop-resume       /fire-map-codebase
  /fire-3-execute           /fire-loop-stop         /fire-0-orient
  /fire-4-verify                                     /fire-research
  /fire-5-handoff                                    /fire-brainstorm
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
         |              Ideas, decisions, approvals             |
         +----------------------+-------------------------------+
                                |
                    +-----------v-----------+
                    |   39 SLASH COMMANDS    |
                    |   (Orchestrators)      |
                    +-----------+-----------+
                                | spawn
              +-----------------+------------------+
              |                 |                   |
    +---------v--------+ +-----v-------+ +---------v-------+
    |  RESEARCHERS     | |   BUILDERS  | |   VALIDATORS    |
    |                  | |             | |                 |
    |  fire-researcher | | fire-       | | fire-verifier   |
    |  (phase/project  | |  executor   | | fire-reviewer   |
    |   research)      | | fire-       | |                 |
    |                  | |  planner    | |                 |
    +--------+---------+ +------+------+ +--------+--------+
             |                  |                  |
             |    +-------------v--------------+   |
             +--->|   .planning/ STATE         |<--+
                  |   (file-based memory)      |
                  +-------------+--------------+
                                |
                  +-------------v--------------+
                  |   190+ SKILLS LIBRARY      |
                  |   (proven patterns)        |
                  +-------------+--------------+
                                |
                  +-------------v--------------+
                  |  WARRIOR HANDOFFS          |
                  |  (session continuity)      |
                  +----------------------------+
```

---

## Version History

| Version | Date | Headline Features |
|---------|------|-------------------|
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

*Generated 2026-02-24 -- Dominion Flow v10.0*
