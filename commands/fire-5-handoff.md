---
description: Create comprehensive session handoff for next AI agent
---

# /fire-5-handoff

> Create comprehensive session handoff using WARRIOR 7-step framework

---

## Purpose

Create a comprehensive session handoff document that combines Dominion Flow execution metrics with the WARRIOR 7-step framework (W-A-R-R-I-O-R). This document captures complete session context to enable seamless resumption in the next session with zero information loss.

---

## Arguments

```yaml
arguments: none

optional_flags:
  --quick: "Generate abbreviated handoff (skip detailed sections)"
  --include-code: "Include key code snippets in handoff"
  --no-save: "Display handoff without saving to file"
```

---

## Process

### Step 1: Gather Session Context

```
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
                         DOMINION FLOW > SESSION HANDOFF
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
```

**Read Current CONSCIENCE.md:**
```markdown
@.planning/CONSCIENCE.md
```

**Extract:**
- Project name and core value
- Current phase and status
- Progress percentage
- Skills applied this session
- Decisions made
- Blockers encountered

### Step 2: Collect All Session Summaries

**Find RECORD.md files from current session:**
```bash
# Find summaries modified today or since last handoff
find .planning/phases/ -name "*-RECORD.md" -newer .planning/CONSCIENCE.md
```

**Aggregate from summaries:**
- Tasks completed
- Files created/modified
- Skills applied
- Honesty checkpoints
- Key decisions
- Issues encountered

### Step 3: Compile WARRIOR 7-Step Handoff

Create the handoff document following the W-A-R-R-I-O-R framework:

```markdown
---
# Handoff Metadata
project: {project_name}
session_date: {YYYY-MM-DD}
session_start: {ISO timestamp}
session_end: {ISO timestamp}
phase: {current_phase}
status: {status}

# Dominion Flow Metrics
phases_completed: {list}
plans_executed: {count}
total_duration: "{X} hours"
skills_applied: {count}
validation_score: {X}/70

# Session Summary
work_completed: "{brief summary}"
next_action: "{what to do next}"
---

# WARRIOR Handoff: {Project Name}

**Session:** {date}
**Duration:** {X} hours
**Phase:** {N} - {name}
**Status:** {status}

---

## W - Work Completed

### This Session Accomplished:
{Aggregate from all RECORD.md files}

**Phases/Plans Completed:**
- Phase {N}, Plan {NN}: {description}
- Phase {N}, Plan {NN}: {description}

**Files Created:**
| File | Lines | Purpose |
|------|-------|---------|
| {path} | {count} | {purpose} |

**Files Modified:**
| File | Changes | Purpose |
|------|---------|---------|
| {path} | {description} | {purpose} |

**Features Implemented:**
1. {Feature 1} - {brief description}
2. {Feature 2} - {brief description}

**Tests Added:**
- {test file}: {X} tests covering {feature}

---

## A - Assessment

### What's Complete:
- âœ“ {Completed item 1}
- âœ“ {Completed item 2}

### What's Partial:
- â—† {In-progress item} - {percentage complete, what remains}

### What's Blocked:
- âœ— {Blocked item} - {reason, who/what can unblock}

### Quality Status:
- **Build:** PASSING | FAILING
- **Tests:** {X}/{Y} passing
- **Coverage:** {X}%
- **Lint:** {status}
- **Validation:** {X}/70 checks

---

## R - Resources

### Environment Variables Required:
```bash
{env vars needed for this project}
```

### Database State:
- **Migrations:** {status}
- **Seed Data:** {status}
- **Connection:** {connection string location}

### External Services:
| Service | Status | Credentials Location |
|---------|--------|---------------------|
| {service} | {status} | {location} |

### Key URLs:
- **Local Dev:** {url}
- **Staging:** {url}
- **Production:** {url}
- **Docs:** {url}

### Important Paths:
- **Project Root:** {path}
- **Planning Docs:** {path}/.planning/
- **Skills Library:** ~/.claude/plugins/dominion-flow/skills-library/

---

## R - Readiness

### Ready For:
- {What the next session can immediately start on}

### Blocked On:
- {What's preventing progress}
  - **Blocker:** {description}
  - **Owner:** {who can resolve}
  - **ETA:** {if known}

### Dependencies Satisfied:
- âœ“ {Dependency 1}
- âœ“ {Dependency 2}

### Dependencies Pending:
- â—‹ {Dependency} - {status, who's responsible}

---

## I - Issues

### Known Bugs:
| Issue | Severity | File:Line | Notes |
|-------|----------|-----------|-------|
| {description} | HIGH/MED/LOW | {location} | {notes} |

### Technical Debt:
- {Item 1} - {why it was deferred}
- {Item 2} - {planned resolution phase}

### Deferred Items:
| Item | Reason | Planned Phase |
|------|--------|---------------|
| {item} | {reason} | Phase {N} |

### Unresolved Questions:
1. {Question} - {context, who might know}

---

## O - Outlook

### Next Session Should:

**Immediate Priority:**
1. {First thing to do} (~{time estimate})

**Then:**
2. {Second priority} (~{time estimate})
3. {Third priority} (~{time estimate})

### Recommended Approach:
{Specific guidance for how to tackle next work}

### Time Estimate:
- **To complete current phase:** ~{X} hours
- **To reach next milestone:** ~{X} hours

### Watch Out For:
- {Potential issue 1}
- {Potential issue 2}

---

## R - References

### Skills Applied This Session:
| Skill | Phase/Plan | Impact |
|-------|------------|--------|
| {category/skill} | {N}-{NN} | {what it helped with} |

### Key Commits:
| Commit | Message | Files Changed |
|--------|---------|---------------|
| {hash} | {message} | {count} |

### Related Documentation:
- {Doc 1}: {path or URL}
- {Doc 2}: {path or URL}

### Decisions Made:
| Decision | Rationale | Impact |
|----------|-----------|--------|
| {decision} | {why} | {what it affects} |

### External Resources Used:
- {Resource 1}: {URL}
- {Resource 2}: {URL}

---

## F - Feedback Pairs

> **Research basis (v6.0):** CoALA (Berkeley 2024) specifies episodic memory should store both positive and negative outcomes with structured labels, enabling future agents to avoid known pitfalls and replicate successes.

### What Worked
| Pattern | Context | Why It Worked |
|---------|---------|---------------|
| {pattern} | {when/where applied} | {explanation of success} |

### What To Avoid
| Anti-Pattern | Context | Why It Failed | Category (v7.0) |
|-------------|---------|---------------|-----------------|
| {anti-pattern} | {when/where encountered} | {explanation of failure} | {MEMORY\|REFLECTION\|PLANNING\|ACTION\|SYSTEM} |

### Key Insight (if any)
{One-sentence reusable lesson from this session — the kind of thing that should become a behavioral directive if confirmed across 3 sessions}

---

## G — Replay Sequences (v7.0)

> **Research basis:** AgentRR (May 2025) — multi-level record/replay enables
> both exact replay for identical issues and adapted replay for similar ones.

### Replayable Resolutions
| Issue | Preconditions | Steps | Confidence |
|-------|--------------|-------|------------|
| {slug} | {key preconditions} | {step count} steps | {HIGH\|MEDIUM} |

{Link to .planning/debug/resolved/{slug}-replay.json for each resolved debug session}

**HIGH confidence** = identical preconditions likely to hold (same project, same deps).
**MEDIUM confidence** = preconditions may differ (different project, adapted approach).

---

## Quick Resume Commands

```bash
# Check current status
/fire-dashboard

# Resume from this handoff
/fire-6-resume

# Continue execution (if mid-phase)
/fire-3-execute {current_phase}

# Plan next phase (if phase complete)
/fire-2-plan {next_phase}

# View skills applied
cat .planning/SKILLS-INDEX.md
```

---

*Handoff created: {timestamp}*
*Project: {project_name}*
*Session: {date}*
```

### Step 3.5: Handoff Quality Scoring (v10.0)

Before saving, score the handoff on the 5-Factor Completeness Scale:

| Factor | Required? | Points | Check |
|--------|-----------|--------|-------|
| STATE | Yes | 20 | Current phase, task, progress % present |
| FILES | Yes | 20 | Every modified file listed with change summary |
| ISSUES | Yes | 20 | Known bugs, blockers, workarounds documented |
| COMMANDS | Yes | 20 | Build, run, test commands present |
| CONTEXT | Yes | 20 | Decisions made, alternatives rejected, WHY documented |

**Scoring:**
- Each factor: 0 (missing), 10 (partial), 20 (complete)
- Total: 0-100

**Display:**
```
◆ Handoff Quality Score: {N}/100

  STATE:    {score}/20 {✓ | ⚠ partial | ✗ missing}
  FILES:    {score}/20 {✓ | ⚠ partial | ✗ missing}
  ISSUES:   {score}/20 {✓ | ⚠ partial | ✗ missing}
  COMMANDS: {score}/20 {✓ | ⚠ partial | ✗ missing}
  CONTEXT:  {score}/20 {✓ | ⚠ partial | ✗ missing}

  Rating: {Excellent ≥90 | Good ≥70 | Needs Work ≥50 | Incomplete <50}
```

**IF score < 70:**
  Use AskUserQuestion:
    header: "Handoff quality"
    question: "Handoff scored {N}/100. Missing: {list}. Improve before saving?"
    options:
      - "Improve now" — Return to Step 3, fill gaps
      - "Save as-is" — Accept current quality

**IF score >= 70:**
  Proceed to Step 4.

### Step 4: Update CONSCIENCE.md

Add handoff reference:

```markdown
## Session Continuity
- Last session: {timestamp}
- Stopped at: {description}
- Resume file: ~/.claude/warrior-handoffs/{project}_{date}.md
- Next: {recommended action}
```

### Step 5: Save Handoff File

**Save Location:**
```
~/.claude/warrior-handoffs/{PROJECT_NAME}_{YYYY-MM-DD}.md
```

**Naming Convention:**
- Use project name from CONSCIENCE.md
- Use current date
- Example: `my-project_2026-01-22.md`

### Step 6: Display Confirmation

```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âœ“ HANDOFF CREATED                                                            â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Project: {project_name}                                                     â•‘
â•‘  Session: {date}                                                             â•‘
â•‘  Duration: {X} hours                                                         â•‘
â•‘                                                                              â•‘
â•‘  Summary:                                                                    â•‘
â•‘    âœ“ Plans completed: {count}                                                â•‘
â•‘    âœ“ Files changed: {count}                                                  â•‘
â•‘    âœ“ Skills applied: {count}                                                 â•‘
â•‘    âœ“ Tests passing: {X}/{Y}                                                  â•‘
â•‘                                                                              â•‘
â•‘  Saved To:                                                                   â•‘
â•‘    ~/.claude/warrior-handoffs/{project}_{date}.md                            â•‘
â•‘                                                                              â•‘
â•‘  CONSCIENCE.md Updated: âœ“                                                         â•‘
â•‘                                                                              â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘ NEXT SESSION                                                                 â•‘
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â•‘                                                                              â•‘
â•‘  Run `/fire-6-resume` to restore full context                               â•‘
â•‘                                                                              â•‘
â•‘  Priority: {next recommended action}                                         â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

---

## Agent Spawning

This command does NOT spawn agents. It compiles information from existing documents.

---

## Success Criteria

### Required Outputs
- [ ] Handoff file created at `~/.claude/warrior-handoffs/{project}_{date}.md`
- [ ] All 7 WARRIOR sections populated
- [ ] Dominion Flow Metrics included in frontmatter
- [ ] CONSCIENCE.md updated with handoff reference
- [ ] Quick resume commands included

### Handoff Quality Checklist
- [ ] **W (Work):** All completed work documented with file references
- [ ] **A (Assessment):** Clear status of complete/partial/blocked items
- [ ] **R (Resources):** All required env vars, credentials, URLs documented
- [ ] **R (Readiness):** Clear statement of what's ready and what's blocked
- [ ] **I (Issues):** All known bugs, debt, and questions captured
- [ ] **O (Outlook):** Specific next steps with time estimates
- [ ] **R (References):** Skills, commits, decisions, and docs linked

---

## Error Handling

### No CONSCIENCE.md Found

```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âœ— ERROR: Project Not Initialized                                             â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  No .planning/CONSCIENCE.md found.                                                â•‘
â•‘                                                                              â•‘
â•‘  Action: Run `/fire-1-new` to initialize project first.                     â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

### No Work to Handoff

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ âš  WARNING: No Recent Work                                                   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                             â”‚
â”‚  No RECORD.md files found since last handoff.                              â”‚
â”‚                                                                             â”‚
â”‚  Options:                                                                   â”‚
â”‚    A) Create minimal handoff with current state                             â”‚
â”‚    B) Cancel handoff creation                                               â”‚
â”‚                                                                             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Cannot Write to Handoffs Directory

```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âœ— ERROR: Cannot Save Handoff                                                 â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Cannot write to: ~/.claude/warrior-handoffs/                                â•‘
â•‘                                                                              â•‘
â•‘  Action: Check permissions or create directory:                              â•‘
â•‘    mkdir -p ~/.claude/warrior-handoffs/                                      â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

---

## References

- **Template:** `@templates/fire-handoff.md` - Unified handoff format
- **Protocol:** `@references/honesty-protocols.md` - WARRIOR foundation
- **Brand:** `@references/ui-brand.md` - Visual output standards
