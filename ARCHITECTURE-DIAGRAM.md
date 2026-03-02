# Dominion Flow Architecture Diagrams

Visual representations of the Dominion Flow system architecture.

---

## System Layer Architecture

```
+=========================================================================+
|                         DOMINION FLOW UNIFIED SYSTEM                       |
+=========================================================================+

+-------------------------------------------------------------------------+
|                        Dominion Flow orchestration SHELL                          |
|                                                                         |
|   /fire-1-new  -->  /fire-2-plan  -->  /fire-3-execute              |
|         |                  |                    |                       |
|         v                  v                    v                       |
|   [Project Init]    [Phase Planning]    [Breath Execution]               |
|         |                  |                    |                       |
|         v                  v                    v                       |
|   /fire-4-verify  <--  /fire-5-handoff  <--  /fire-6-resume         |
|         |                  |                    |                       |
|   [Validation]      [Session Save]       [Context Load]                |
|                                                                         |
+-------------------------------------------------------------------------+
                                    |
                                    | Integrates
                                    v
+-------------------------------------------------------------------------+
|                       WARRIOR CORE FOUNDATION                           |
|                                                                         |
|   +-------------------+  +-------------------+  +-------------------+   |
|   |  SKILLS LIBRARY   |  | HONESTY PROTOCOLS |  |   VALIDATION      |   |
|   |                   |  |                   |  |   FRAMEWORK       |   |
|   | - 190+ patterns   |  | - No false claims |  | - 70-point check  |   |
|   | - 15 categories   |  | - Admit unknowns  |  | - Must-haves      |   |
|   | - Versioned       |  | - Evidence-based  |  | - Goal-backward   |   |
|   | - Searchable      |  | - Flag assumptions|  | - Auto-verify     |   |
|   +-------------------+  +-------------------+  +-------------------+   |
|                                                                         |
+-------------------------------------------------------------------------+
                                    |
                                    | Stores/Reads
                                    v
+-------------------------------------------------------------------------+
|                     SHARED STATE & CONTEXT LAYER                        |
|                                                                         |
|   .planning/                                                            |
|   +------------------------------------------------------------------+ |
|   | CONSCIENCE.md          | Living project memory, current status         | |
|   +------------------------------------------------------------------+ |
|   | VISION.md        | Phase overview, milestones, timeline          | |
|   +------------------------------------------------------------------+ |
|   | phases/           | Detailed plans, summaries, breath trackers      | |
|   |   01-phase/       |                                               | |
|   |     BLUEPRINT.md       |                                               | |
|   |     RECORD.md    |                                               | |
|   +------------------------------------------------------------------+ |
|   | POWER-HANDOFF-*.md| Session continuity, context preservation      | |
|   +------------------------------------------------------------------+ |
|                                                                         |
+-------------------------------------------------------------------------+
```

---

## Data Flow: Planning Phase

```
                              /fire-2-plan N
                                    |
                                    v
                    +-------------------------------+
                    |     Read Current Context      |
                    |  - CONSCIENCE.md (project state)   |
                    |  - VISION.md (phase info)    |
                    +-------------------------------+
                                    |
                                    v
                    +-------------------------------+
                    |   Search Skills Library       |
                    |  - Match phase requirements   |
                    |  - Find relevant patterns     |
                    |  - Suggest integrations       |
                    +-------------------------------+
                                    |
                                    v
                    +-------------------------------+
                    |   Invoke fire-planner Agent  |
                    |  - Analyze requirements       |
                    |  - Apply honesty protocols    |
                    |  - Estimate complexity        |
                    +-------------------------------+
                                    |
                                    v
                    +-------------------------------+
                    |      Generate BLUEPRINT.md         |
                    |  - Tasks with dependencies    |
                    |  - Must-haves list            |
                    |  - Breath groupings             |
                    |  - Skills references          |
                    +-------------------------------+
                                    |
                                    v
                    +-------------------------------+
                    |      Update CONSCIENCE.md          |
                    |  - Phase status: planned      |
                    |  - Planning timestamp         |
                    +-------------------------------+
```

---

## Data Flow: Execution Phase

```
                             /fire-3-execute N
                                    |
                                    v
                    +-------------------------------+
                    |      Load Phase Plan          |
                    |  - BLUEPRINT.md tasks              |
                    |  - Breath definitions           |
                    |  - Dependencies               |
                    +-------------------------------+
                                    |
                                    v
               +--------------------------------------------+
               |          BREATH-BASED EXECUTION              |
               |                                            |
               |   Breath 1 (Parallel)                        |
               |   +--------+  +--------+  +--------+       |
               |   | Task A |  | Task B |  | Task C |       |
               |   +--------+  +--------+  +--------+       |
               |        |          |           |            |
               |        +-----+----+-----+-----+            |
               |              v                             |
               |   Breath 2 (Depends on Breath 1)               |
               |   +--------+  +--------+                   |
               |   | Task D |  | Task E |                   |
               |   +--------+  +--------+                   |
               |              |                             |
               +--------------------------------------------+
                              |
                              v
                    +-------------------------------+
                    |  Invoke fire-executor Agent  |
                    |  - Execute tasks              |
                    |  - Apply honesty protocols    |
                    |  - Track progress             |
                    +-------------------------------+
                              |
                              v
                    +-------------------------------+
                    |   Real-time CONSCIENCE.md Update   |
                    |  - Task completion status     |
                    |  - Blockers encountered       |
                    |  - Skills applied             |
                    +-------------------------------+
```

---

## Data Flow: Verification Phase

```
                             /fire-4-verify N
                                    |
                                    v
                    +-------------------------------+
                    |    Load Phase Deliverables    |
                    |  - BLUEPRINT.md must-haves         |
                    |  - Expected outcomes          |
                    +-------------------------------+
                                    |
                                    v
                    +-------------------------------+
                    |  Invoke fire-verifier Agent  |
                    |  - Check each must-have       |
                    |  - Run 70-point checklist     |
                    |  - Apply honesty protocols    |
                    +-------------------------------+
                                    |
                                    v
        +--------------------------------------------------+
        |              VALIDATION CHECKS                    |
        |                                                   |
        |   Must-Haves              60-Point Checklist      |
        |   +----------------+      +-------------------+   |
        |   | [x] Feature A  |      | [x] No hardcoded  |   |
        |   | [x] Feature B  |      |     credentials   |   |
        |   | [ ] Feature C  |      | [x] Error handling|   |
        |   +----------------+      | [!] Rate limiting |   |
        |                           +-------------------+   |
        +--------------------------------------------------+
                                    |
                                    v
                    +-------------------------------+
                    |    Generate Verification      |
                    |         Report                |
                    |  - PASS / PARTIAL / FAIL      |
                    |  - Issues found               |
                    |  - Recommendations            |
                    +-------------------------------+
                                    |
                                    v
                    +-------------------------------+
                    |      Update CONSCIENCE.md          |
                    |  - Phase status: complete     |
                    |  - Verification results       |
                    |  - Notes for next phase       |
                    +-------------------------------+
```

---

## Component Relationship Diagram

```
+------------------+          +------------------+
|    COMMANDS      |          |     AGENTS       |
+------------------+          +------------------+
| fire-1-new       |--------->| fire-planner    |
| fire-2-plan      |--------->| fire-executor   |
| fire-3-execute   |--------->| fire-verifier   |
| fire-4-verify    |--------->| fire-researcher |
| fire-5-handoff   |          +------------------+
| fire-6-resume    |                   |
| fire-search      |                   | Uses
| fire-contribute  |                   v
| fire-skills-*    |          +------------------+
| fire-dashboard   |          |    REFERENCES    |
| fire-analytics   |          +------------------+
| fire-discover    |          | honesty-protocols|
| power-test       |          | validation-check |
+------------------+          | skills-usage     |
        |                     | ui-brand         |
        | Creates/Updates     +------------------+
        v                              |
+------------------+                   | Guides
|    TEMPLATES     |                   v
+------------------+          +------------------+
| state.md         |<---------|  SKILLS LIBRARY  |
| roadmap.md       |          +------------------+
| plan.md          |          | advanced-features|
| fire-handoff.md |          | api-patterns     |
| verification.md  |          | automation       |
| skills-index.md  |          | complexity-metrics|
+------------------+          | database-solutions|
        |                     | deployment-security|
        | Populates           | document-processing|
        v                     | ecommerce        |
+------------------+          | form-solutions   |
|  .planning/      |          | integrations     |
|  (Project Dir)   |          | lms-patterns     |
+------------------+          | methodology      |
| CONSCIENCE.md         |          | patterns-standards|
| VISION.md       |          | theology         |
| phases/          |          | video-media      |
| POWER-HANDOFF-*  |          +------------------+
+------------------+
```

---

## File Relationship Diagram

```
.planning/
    |
    +-- CONSCIENCE.md  <-----------------+
    |      ^                        |
    |      | Updates                | Reads
    |      |                        |
    +-- VISION.md                  |
    |      ^                        |
    |      | References             |
    |      |                        |
    +-- phases/                     |
    |      |                        |
    |      +-- 01-phase-name/       |
    |      |      |                 |
    |      |      +-- BLUEPRINT.md ------+
    |      |      |      ^
    |      |      |      | Created by /fire-2-plan
    |      |      |      | Executed by /fire-3-execute
    |      |      |      | Verified by /fire-4-verify
    |      |      |
    |      |      +-- RECORD.md
    |      |      |      ^
    |      |      |      | Created after verification
    |      |      |
    |      |      +-- BREATH-TRACKER.md
    |      |             ^
    |      |             | Updated during execution
    |      |
    |      +-- 02-phase-name/
    |             |
    |             +-- BLUEPRINT.md
    |             +-- ...
    |
    +-- POWER-HANDOFF-2025-01-22.md
           ^
           | Created by /fire-5-handoff
           | Read by /fire-6-resume
```

---

## Session Continuity Flow

```
SESSION 1                          SESSION 2
=========                          =========

Work on project                    /fire-6-resume
     |                                   |
     v                                   v
Update CONSCIENCE.md                    Read latest handoff
     |                                   |
     v                                   v
/fire-5-handoff                   Restore CONSCIENCE.md context
     |                                   |
     v                                   v
Create POWER-HANDOFF-*.md          Display session summary
     |                                   |
     |                                   v
     |                             Continue work
     |                                   |
     +------- (Session boundary) --------+

Handoff Contents:
+--------------------------------+
| Project: My App                |
| Phase: 2 (40% complete)        |
| In Progress:                   |
|   - Dashboard component        |
|   - API endpoint               |
| Blockers:                      |
|   - State mgmt decision        |
| Skills Used:                   |
|   - oauth-patterns.md          |
| Next Steps:                    |
|   - Complete dashboard         |
|   - Decide Redux vs Context    |
+--------------------------------+
```

---

## Agent Interaction Model

```
+-------------------------------------------------------------------+
|                         USER REQUEST                               |
+-------------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------------+
|                      COMMAND ROUTER                                |
|   Matches request to appropriate power-* command                   |
+-------------------------------------------------------------------+
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
+------------------+  +------------------+  +------------------+
| fire-planner    |  | fire-executor   |  | fire-verifier   |
| Agent            |  | Agent            |  | Agent            |
+------------------+  +------------------+  +------------------+
| - Skills search  |  | - Task execution |  | - Must-haves     |
| - Complexity est |  | - Breath parallel  |  | - 70-point check |
| - Plan generation|  | - Progress track |  | - Report gen     |
| - Honesty: flag  |  | - Honesty: no    |  | - Honesty: prove |
|   assumptions    |  |   false complete |  |   with evidence  |
+------------------+  +------------------+  +------------------+
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
+-------------------------------------------------------------------+
|                    fire-researcher Agent                          |
|   - Cross-reference skills                                         |
|   - Find related patterns                                          |
|   - Suggest improvements                                           |
|   - Discover new skills                                            |
+-------------------------------------------------------------------+
```

---

## Skills Library Architecture

```
skills-library/
    |
    +-- .git/                    # Version control
    |
    +-- AVAILABLE_TOOLS_REFERENCE.md   # Master index
    |
    +-- advanced-features/       # Category
    |       |
    |       +-- GAMIFICATION_SYSTEM.md
    |       +-- PLUGIN_SYSTEM_ARCHITECTURE.md
    |       +-- SEO_SETTINGS_MANAGEMENT.md
    |       +-- ...
    |
    +-- database-solutions/      # Category
    |       |
    |       +-- RLS_SECURITY_GUIDE.md
    |       +-- SCHEMA_MIGRATION_GUIDE.md
    |       +-- POSTGRESQL_LICENSE_TABLE_DESIGN.md
    |       +-- ...
    |
    +-- deployment-security/     # Category
    |       |
    |       +-- VPS_DEPLOYMENT_READINESS.md
    |       +-- CPANEL_NODE_DEPLOYMENT.md
    |       +-- LICENSE_KEY_SYSTEM.md
    |       +-- ...
    |
    +-- [12 more categories...]
    |
    +-- methodology/             # Meta category
            |
            +-- complexity-divider.md
            +-- work-with-complexity.md
            +-- ...

Total: 190+ skills across 15 categories
Versioned: Git history for rollback
Searchable: /fire-search command
Contributable: /fire-contribute command
```

---

*Architecture clarity powers effective development.*
