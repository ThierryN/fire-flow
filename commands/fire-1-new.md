---
description: Initialize a new project with Dominion Flow (Dominion Flow)
---

# /fire-1-new

> Initialize a new project with Dominion Flow orchestration

---

## Purpose

Initialize a new project with both Dominion Flow project structure and WARRIOR integration. This command gathers requirements through adaptive questioning, creates the project roadmap, sets up the skills tracking system, and prepares session continuity hooks.

---

## Arguments

```yaml
arguments: none
optional_flags:
  --name: "Project name (will prompt if not provided)"
  --path: "Project path (defaults to current directory)"
  --minimal: "Skip adaptive questioning, use defaults"
```

---

## Process

### Step 1: Environment Validation

```
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
                         DOMINION FLOW > PROJECT INITIALIZATION
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
```

**Validate:**
1. Check if `.planning/` directory already exists (warn if so)
2. Verify write permissions in target directory
3. Check for existing git repository (recommend if not present)

### Step 2: Gather Requirements (Dominion Flow Standard)

Run Dominion Flow new-project workflow through adaptive questioning:

**Core Questions:**
1. What is this project? (one sentence)
2. Who is the primary user?
3. What is the core value it provides?
4. What are the non-negotiable features (must-haves)?

**Technical Questions:**
1. What tech stack are you using?
2. Are there existing codebases to integrate with?
3. What are known technical constraints?

**Timeline Questions:**
1. What's the target completion date?
2. What milestones are critical?

### Step 3: Create Project Structure

**Create `.planning/` directory with:**

```
.planning/
â”œâ”€â”€ PROJECT.md           # Project overview from requirements
â”œâ”€â”€ VISION.md           # Phase-based roadmap
â”œâ”€â”€ CONSCIENCE.md             # Enhanced with WARRIOR fields
â”œâ”€â”€ REQUIREMENTS.md      # Captured requirements
â”œâ”€â”€ SKILLS-INDEX.md      # Skills tracking (empty, ready)
â””â”€â”€ phases/              # Empty, ready for phase plans
```

### Step 4: Initialize WARRIOR Handoff System

**Create handoff directory if not exists:**
```bash
mkdir -p ~/.claude/warrior-handoffs/
```

**Create initial handoff file:**
```
~/.claude/warrior-handoffs/{PROJECT_NAME}_YYYY-MM-DD_init.md
```

### Step 5: Set Up SessionStart Hook

**Verify hook configuration in plugin:**
- Hook auto-injects CONSCIENCE.md context on session start
- Hook reminds about WARRIOR handoffs

### Step 6: Create SKILLS-INDEX.md

Initialize empty skills tracking:

```markdown
# Skills Applied to This Project

## Summary
- Total skills applied: 0
- Categories used: 0
- Last skill applied: N/A

## By Phase
*No phases executed yet*

## By Category
*Skills will be tracked here as they're applied during execution*

## Quick Reference
Run `/fire-search [query]` to find relevant skills.
```

---

## Agent Spawning

This command does NOT spawn agents. It runs interactively with the user to gather requirements.

**If `--minimal` flag used:**
- Skip adaptive questioning
- Use project name from current directory
- Create minimal structure with placeholder content
- Display message to run `/fire-2-plan 1` to begin planning

---

## Output Structure

### .planning/PROJECT.md

```markdown
# {Project Name}

## Core Value
{One sentence description of what this project does}

## Primary User
{Who uses this}

## Must-Have Features
1. {Feature 1}
2. {Feature 2}
3. {Feature 3}

## Tech Stack
- {Tech 1}
- {Tech 2}
- {Tech 3}

## Constraints
- {Constraint 1}
- {Constraint 2}

## Success Criteria
- {Criterion 1}
- {Criterion 2}
```

### .planning/VISION.md

```markdown
# Project Roadmap

## Milestone: v{version} - {name}

### Phase 1: {name}
**Objective:** {what this phase accomplishes}
**Estimated:** {time estimate}
**Must-Haves:**
- {Must-have 1}
- {Must-have 2}

### Phase 2: {name}
**Objective:** {what this phase accomplishes}
**Estimated:** {time estimate}
**Must-Haves:**
- {Must-have 1}
- {Must-have 2}

[Additional phases as needed]
```

### .planning/CONSCIENCE.md

Uses template from `templates/state.md` with fields populated:
- Project name and core value
- Current phase: 1 of N
- Status: Ready to plan
- WARRIOR Integration section initialized
- Session Continuity section initialized

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

### Completion Display

```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âœ“ PROJECT INITIALIZED                                                        â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Project: {project_name}                                                     â•‘
â•‘  Phases: {phase_count} defined                                               â•‘
â•‘  Status: Ready to plan                                                       â•‘
â•‘                                                                              â•‘
â•‘  Created:                                                                    â•‘
â•‘    âœ“ .planning/PROJECT.md                                                    â•‘
â•‘    âœ“ .planning/VISION.md                                                    â•‘
â•‘    âœ“ .planning/CONSCIENCE.md                                                      â•‘
â•‘    âœ“ .planning/SKILLS-INDEX.md                                               â•‘
â•‘    âœ“ .planning/phases/                                                       â•‘
â•‘    âœ“ ~/.claude/warrior-handoffs/{project}_init.md                            â•‘
â•‘                                                                              â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘ NEXT UP                                                                      â•‘
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â•‘                                                                              â•‘
â•‘  â†’ Run `/fire-2-plan 1` to create plans for Phase 1                         â•‘
â•‘  â†’ Or run `/fire-dashboard` to view project status                          â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

---

## Error Handling

### .planning/ Already Exists

```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âš  WARNING: Existing Project Detected                                         â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Found existing .planning/ directory.                                        â•‘
â•‘                                                                              â•‘
â•‘  Options:                                                                    â•‘
â•‘    A) Use `/fire-6-resume` to continue existing project                     â•‘
â•‘    B) Delete .planning/ and run `/fire-1-new` again                         â•‘
â•‘    C) Use `--path [new-directory]` to initialize elsewhere                   â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

### Write Permission Denied

```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âœ— ERROR: Cannot Create Project                                               â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  No write permission in: {path}                                              â•‘
â•‘                                                                              â•‘
â•‘  Action: Run from a directory where you have write access                    â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

---

## References

- **Template:** `@templates/state.md` - CONSCIENCE.md template
- **Template:** `@templates/roadmap.md` - ROADMAP template
- **Template:** `@templates/skills-index.md` - Skills tracking template
- **Protocol:** `@references/honesty-protocols.md` - WARRIOR honesty foundation
- **Brand:** `@references/ui-brand.md` - Visual output standards
