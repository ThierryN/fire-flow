# Workflow: New Project Orchestration

<purpose>
Initialize a new project with Dominion Flow orchestration and WARRIOR foundation through adaptive questioning, directory structure creation, and comprehensive setup for session continuity. This workflow ensures every project starts with proper planning artifacts and tracking systems.
</purpose>

---

<core_principle>
**Every project deserves a solid foundation.** Before writing a single line of code, establish clear requirements, a realistic roadmap, and the tracking systems needed for sustainable development. Projects that skip this step pay for it later.
</core_principle>

---

<required_reading>
Before executing this workflow, load:
```markdown
@templates/state.md           # CONSCIENCE.md template
@templates/roadmap.md         # VISION.md template
@templates/skills-index.md    # Skills tracking template
@references/honesty-protocols.md  # Foundation for honest planning
@references/ui-brand.md       # Visual output standards
```
</required_reading>

---

<process>

## Step 1: Environment Validation

**Purpose:** Ensure we can create the project structure without conflicts.

```bash
# Check if .planning/ directory already exists
if [ -d ".planning" ]; then
  echo "WARNING: .planning/ directory exists"
  # Route to existing project warning
fi

# Verify write permissions
touch .planning-test-write && rm .planning-test-write

# Check for git repository
if [ ! -d ".git" ]; then
  echo "NOTICE: No git repository found"
  echo "Consider: git init"
fi
```

**If .planning/ exists:**
- Display warning about existing project
- Offer options: Resume existing (`/fire-6-resume`), Delete and restart, or Use different path
- Do NOT proceed without user decision

---

## Step 2: Adaptive Questioning Flow

**Purpose:** Gather comprehensive requirements through intelligent questioning.

### Phase A: Core Identity Questions

```markdown
## Project Identity

**Question 1:** What is this project? (one sentence)
> The project is a ___

**Question 2:** Who is the primary user?
> The primary user is ___

**Question 3:** What is the core value it provides?
> The core value is ___

**Question 4:** What problem does it solve?
> It solves ___
```

### Phase B: Feature Questions

```markdown
## Features

**Question 5:** What are the must-have features? (things that MUST work for v1.0)
> Must-have features:
> 1. ___
> 2. ___
> 3. ___

**Question 6:** What are the nice-to-have features? (can be deferred if needed)
> Nice-to-have features:
> 1. ___
> 2. ___
```

### Phase C: Technical Questions

```markdown
## Technical Context

**Question 7:** What is the tech stack?
> Tech stack:
> - Frontend: ___
> - Backend: ___
> - Database: ___
> - Other: ___

**Question 8:** Are there existing codebases or systems to integrate with?
> Integrations: ___

**Question 9:** What are known technical constraints?
> Constraints:
> 1. ___
> 2. ___
```

### Phase D: Timeline Questions

```markdown
## Timeline

**Question 10:** What's the target completion date for v1.0?
> Target: ___

**Question 11:** What milestones are critical?
> Critical milestones:
> 1. ___
> 2. ___

**Question 12:** How much time per day/week is available for this project?
> Availability: ___
```

### Adaptive Follow-ups

Based on answers, ask clarifying questions:
- If tech stack includes unfamiliar technology: "Have you worked with [tech] before?"
- If must-haves are vague: "Can you be more specific about [feature]?"
- If timeline is aggressive: "What can we defer if needed?"

---

## Step 3: Create Directory Structure

**Purpose:** Set up the planning and tracking directories.

```bash
# Create .planning directory and subdirectories
mkdir -p .planning/phases
mkdir -p .planning/debug

# Create handoffs directory (global, if not exists)
mkdir -p ~/.claude/warrior-handoffs/
```

**Expected Structure:**
```
.planning/
├── PROJECT.md           # Project overview from requirements
├── VISION.md           # Phase-based roadmap
├── CONSCIENCE.md             # Enhanced with WARRIOR fields
├── REQUIREMENTS.md      # Captured requirements
├── SKILLS-INDEX.md      # Skills tracking (empty, ready)
└── phases/              # Empty, ready for phase plans
```

---

## Step 4: Generate PROJECT.md

**Purpose:** Capture requirements in a structured format.

```markdown
# {Project Name}

## Core Value
{One sentence description of what this project does}

## Primary User
{Who uses this}

## Problem Solved
{What problem it addresses}

## Must-Have Features
1. {Feature 1}
2. {Feature 2}
3. {Feature 3}

## Nice-to-Have Features
1. {Feature 1} - Can defer if needed
2. {Feature 2} - Can defer if needed

## Tech Stack
- **Frontend:** {tech}
- **Backend:** {tech}
- **Database:** {tech}
- **Other:** {tech}

## Integrations
- {Integration 1}
- {Integration 2}

## Constraints
- {Constraint 1}
- {Constraint 2}

## Timeline
- **Target v1.0:** {date}
- **Availability:** {time commitment}

## Success Criteria
- {Criterion 1 - measurable}
- {Criterion 2 - measurable}

---
*Created: {YYYY-MM-DD}*
*Last updated: {YYYY-MM-DD}*
```

---

## Step 5: Generate VISION.md

**Purpose:** Break down the project into executable phases.

### Phase Generation Rules

1. **Phase Count:** Typically 3-8 phases for v1.0
2. **Phase Scope:** Each phase should be 1-5 days of work
3. **Dependencies:** Early phases should unblock later phases
4. **Must-Haves First:** Critical features in earlier phases
5. **Buffer Phase:** Include a "Polish & Testing" phase at the end

### Roadmap Template

```markdown
# {Project Name} Roadmap

## Milestone: v1.0 - {milestone_name}

**Target:** {target_date}
**Status:** Planning
**Progress:** [----------] 0%

---

## Phase Overview

| # | Phase | Status | Est. Duration | Description |
|---|-------|--------|---------------|-------------|
| 1 | {name} | Pending | {X days} | {description} |
| 2 | {name} | Pending | {X days} | {description} |
| 3 | {name} | Pending | {X days} | {description} |
| N | {name} | Pending | {X days} | {description} |

---

## Phase Details

### Phase 1: {name}
**Objective:** {what this phase accomplishes}
**Estimated Duration:** {X days}
**Dependencies:** None (starting phase)

**Must-Haves:**
- {Must-have 1}
- {Must-have 2}

**Deliverables:**
- {Deliverable 1}
- {Deliverable 2}

---

### Phase 2: {name}
**Objective:** {what this phase accomplishes}
**Estimated Duration:** {X days}
**Dependencies:** Phase 1

**Must-Haves:**
- {Must-have 1}
- {Must-have 2}

**Deliverables:**
- {Deliverable 1}
- {Deliverable 2}

---

[Continue for all phases]

---

## Dependencies

```mermaid
graph TD
  P1[Phase 1: {name}] --> P2[Phase 2: {name}]
  P1 --> P3[Phase 3: {name}]
  P2 --> P4[Phase 4: {name}]
  P3 --> P4
```

---

## Risk Assessment

| Risk | Impact | Mitigation | Status |
|------|--------|------------|--------|
| {risk 1} | High/Med/Low | {mitigation} | Open |
| {risk 2} | High/Med/Low | {mitigation} | Open |

---

## Success Criteria

### Must-Haves (Required for v1.0)
- [ ] {Must-have 1}
- [ ] {Must-have 2}
- [ ] {Must-have 3}

### Nice-to-Haves (Deferred if needed)
- [ ] {Nice-to-have 1}
- [ ] {Nice-to-have 2}

---

*Created: {YYYY-MM-DD}*
*Last updated: {YYYY-MM-DD}*
```

---

## Step 6: Initialize CONSCIENCE.md

**Purpose:** Create the living memory document for session continuity.

Use the `@templates/state.md` template with these initial values:

```yaml
# Initial CONSCIENCE.md values
project_name: {from questions}
core_value: {from questions}
current_phase: 1
phase_name: {from roadmap}
milestone_version: "1.0"
milestone_status: "Planning"
total_phases: {from roadmap}
current_wave: "N/A"
status: "Ready to plan"
last_activity_date: {today}
last_activity_description: "Project initialized"
progress_percent: 0
total_skills_applied: 0
honesty_checkpoint_count: 0
last_validated_phase: "N/A"
session_start: "N/A"
next_action: "Run /fire-2-plan 1 to begin planning Phase 1"
```

---

## Step 7: Create SKILLS-INDEX.md

**Purpose:** Initialize skills tracking for WARRIOR integration.

```markdown
# Skills Applied to This Project

## Summary
- **Total skills applied:** 0
- **Categories used:** 0
- **Last skill applied:** N/A

## By Phase
*No phases executed yet*

## By Category
*Skills will be tracked here as they're applied during execution*

### Available Categories
| Category | Skills | Description |
|----------|--------|-------------|
| database-solutions | 15+ | Queries, migrations, optimization |
| api-patterns | 12+ | REST, versioning, pagination |
| security | 18+ | Auth, validation, encryption |
| performance | 10+ | Caching, optimization, profiling |
| frontend | 14+ | React, state, rendering |
| testing | 12+ | Unit, integration, E2E |
| methodology | 10+ | Planning, review, handoffs |
| patterns-standards | 15+ | Design patterns, conventions |

## Quick Reference
Run `/fire-search [query]` to find relevant skills.

---
*Initialized: {YYYY-MM-DD}*
*Last updated: {YYYY-MM-DD}*
```

---

## Step 8: Create Initial Handoff

**Purpose:** Establish session continuity from the start.

```bash
# Generate handoff filename
HANDOFF_FILE=~/.claude/warrior-handoffs/{PROJECT_NAME}_{YYYY-MM-DD}_init.md
```

**Initial Handoff Content:**

```markdown
---
project: {project_name}
session_date: {YYYY-MM-DD}
type: initialization
status: ready_to_plan
---

# WARRIOR Handoff: {Project Name} - Initialization

**Session:** {date}
**Type:** Project Initialization
**Status:** Ready to Plan

---

## W - Work Completed
- Project requirements gathered
- Planning directory structure created
- Roadmap with {N} phases defined
- CONSCIENCE.md initialized
- Skills tracking prepared

## A - Assessment
- **Project Definition:** Complete
- **Roadmap:** {N} phases defined
- **Next Phase:** Phase 1 - {name}

## R - Resources
**Project Location:** {path}
**Planning Docs:** {path}/.planning/

## R - Readiness
**Ready For:** Phase 1 planning
**Blocked On:** Nothing

## I - Issues
**Known Issues:** None
**Assumptions Made:**
- {Any assumptions from requirements gathering}

## O - Outlook
**Next Session Should:**
1. Run `/fire-2-plan 1` to create Phase 1 plans
2. Review generated plans
3. Begin execution with `/fire-3-execute 1`

## R - References
**Key Files:**
- .planning/PROJECT.md
- .planning/VISION.md
- .planning/CONSCIENCE.md

---
*Handoff created: {timestamp}*
```

---

## Step 9: Configure Hook System

**Purpose:** Ensure automatic context loading on session start.

The Fire Flow plugin includes SessionStart hooks that:
1. Load CONSCIENCE.md context automatically
2. Remind about WARRIOR handoffs
3. Display last activity and next action

**Verify hook configuration:**
```bash
# Check hooks.json exists in plugin
ls ~/.claude/plugins/fire-flow/hooks/hooks.json
```

---

## Step 10: Display Completion Summary

**Purpose:** Confirm initialization and provide next steps.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ PROJECT INITIALIZED                                                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Project: {project_name}                                                     ║
║  Core Value: {core_value}                                                    ║
║  Phases: {phase_count} defined                                               ║
║  Status: Ready to plan                                                       ║
║                                                                              ║
║  Created:                                                                    ║
║    .planning/PROJECT.md                                                      ║
║    .planning/VISION.md                                                      ║
║    .planning/CONSCIENCE.md                                                        ║
║    .planning/SKILLS-INDEX.md                                                 ║
║    .planning/phases/                                                         ║
║    ~/.claude/warrior-handoffs/{project}_init.md                              ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ NEXT UP                                                                      ║
├──────────────────────────────────────────────────────────────────────────────┤
║                                                                              ║
║  Run `/fire-2-plan 1` to create plans for Phase 1                           ║
║  Or run `/fire-dashboard` to view project status                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

</process>

---

## Agent Spawning

This workflow does NOT spawn agents. It runs interactively with the user to gather requirements.

**Rationale:** Project initialization requires human input and decision-making. The AI facilitates the process but doesn't make autonomous decisions about project scope or priorities.

---

## Success Criteria

### Required Outputs
- [ ] `.planning/` directory created
- [ ] `PROJECT.md` with requirements captured
- [ ] `VISION.md` with phases defined
- [ ] `CONSCIENCE.md` initialized with WARRIOR fields
- [ ] `SKILLS-INDEX.md` created (empty)
- [ ] `phases/` directory created
- [ ] Initial handoff file created in `~/.claude/warrior-handoffs/`

### Quality Checks
- [ ] All questions answered (or explicitly deferred)
- [ ] Must-haves are specific and testable
- [ ] Phases have clear objectives
- [ ] Timeline is realistic given availability
- [ ] Dependencies are logical

---

## Error Handling

### .planning/ Already Exists
Route to existing project dialog - offer resume, delete, or new path.

### Write Permission Denied
Display error with specific path and suggest alternatives.

### User Cancels Mid-Workflow
Save partial progress to `~/.claude/warrior-handoffs/{project}_partial.md` for later resume.

### Unclear Requirements
Add follow-up questions rather than assuming. Flag uncertainties in PROJECT.md.

---

## References

- **Template:** `@templates/state.md` - CONSCIENCE.md template
- **Template:** `@templates/roadmap.md` - ROADMAP template
- **Template:** `@templates/skills-index.md` - Skills tracking template
- **Protocol:** `@references/honesty-protocols.md` - WARRIOR honesty foundation
- **Brand:** `@references/ui-brand.md` - Visual output standards
