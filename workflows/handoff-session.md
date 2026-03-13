# Workflow: Session Handoff Orchestration

<purpose>
Create a comprehensive session handoff document that combines Dominion Flow execution metrics with the WARRIOR 7-step framework (W-A-R-R-I-O-R). This workflow captures complete session context to enable seamless resumption in the next session with zero information loss, ensuring continuity regardless of which AI or human picks up the work.
</purpose>

---

<core_principle>
**Zero context loss between sessions.** The handoff document should contain everything needed to continue exactly where you left off. If someone reading the handoff has questions, the handoff failed. Be thorough, be specific, be honest.
</core_principle>

---

<required_reading>
Before executing this workflow, load:
```markdown
@.planning/CONSCIENCE.md                          # Current project position
@.planning/phases/{N}-{name}/*-RECORD.md    # Execution summaries from current session
@.planning/SKILLS-INDEX.md                   # Skills applied tracking
@templates/fire-handoff.md                  # Unified handoff format
@references/honesty-protocols.md             # WARRIOR foundation
```
</required_reading>

---

<process>

## Step 1: Gather Session Context

**Purpose:** Collect all information about what happened this session.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                         DOMINION FLOW > SESSION HANDOFF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Parse Arguments:**
```yaml
arguments: none

optional:
  --quick: "Generate abbreviated handoff (skip detailed sections)"
  --include-code: "Include key code snippets in handoff"
  --no-save: "Display handoff without saving to file"
```

### Read CONSCIENCE.md

```markdown
@.planning/CONSCIENCE.md

Extract:
- Project name and core value
- Current phase and status
- Progress percentage
- Skills applied this session
- Decisions made this session
- Blockers encountered
- Last activity timestamp
```

### Determine Session Scope

```bash
# Find when session started (if tracked)
SESSION_START=$(grep "session_start" .planning/CONSCIENCE.md | cut -d: -f2)

# If not tracked, use last handoff time
if [ -z "$SESSION_START" ]; then
  LAST_HANDOFF=$(ls -t ~/.claude/warrior-handoffs/${PROJECT}_*.md | head -1)
  SESSION_START=$(stat -c %Y "$LAST_HANDOFF")
fi
```

---

## Step 2: Collect Session Summaries

**Purpose:** Aggregate all work done since last handoff.

### Find Modified RECORD.md Files

```bash
# Find summaries modified since session start
find .planning/phases/ -name "*-RECORD.md" -newer "$LAST_HANDOFF" 2>/dev/null

# Or if no last handoff, find all summaries from today
find .planning/phases/ -name "*-RECORD.md" -mtime 0
```

### Aggregate From Each Summary

For each RECORD.md found:

```markdown
Extract:
- Tasks completed (with commit hashes)
- Files created (with line counts)
- Files modified (with change descriptions)
- Skills applied (with code locations)
- Honesty checkpoints (gaps encountered, how resolved)
- Key decisions (with rationale)
- Issues encountered (with severity)
- Deviations from plan (with reasons)
```

### Compile Git Activity

```bash
# Get commits since session start or last handoff
git log --oneline --since="$SESSION_START" --format="%h %s"

# Get files changed
git diff --stat HEAD~{commit_count}
```

---

## Step 3: Compile WARRIOR 7-Step Handoff

**Purpose:** Structure all information using the W-A-R-R-I-O-R framework.

### Handoff Document Structure

```markdown
---
# Handoff Metadata
project: {project_name}
session_date: {YYYY-MM-DD}
session_start: "{ISO timestamp}"
session_end: "{ISO timestamp}"
phase: {current_phase}
status: {status}

# Dominion Flow Metrics
phases_completed: [{list}]
plans_executed: {count}
total_duration: "{X} hours"
commits: {count}
files_created: {count}
files_modified: {count}
skills_applied: {count}
validation_score: "{X}/70"

# Session Summary
work_completed: "{brief one-line summary}"
next_action: "{what to do next}"
---

# WARRIOR Handoff: {Project Name}

**Session:** {date}
**Duration:** {X} hours ({start_time} - {end_time})
**Phase:** {N} - {name}
**Status:** {status}

---

## W - Work Completed

### This Session Accomplished

{High-level summary of what was done}

**Phases/Plans Completed:**
- Phase {N}, Plan {NN}: {description} ({X} min, {Y} commits)
- Phase {N}, Plan {NN}: {description} ({X} min, {Y} commits)

**Files Created:**
| File | Lines | Purpose |
|------|-------|---------|
| {path/to/file.ts} | {count} | {purpose} |
| {path/to/file.ts} | {count} | {purpose} |

**Files Modified:**
| File | Changes | Purpose |
|------|---------|---------|
| {path/to/file.ts} | {description} | {purpose} |
| {path/to/file.ts} | {description} | {purpose} |

**Features Implemented:**
1. **{Feature Name}** - {brief description}
   - Key file: {path}
   - Tests: {path/to/test.ts}
2. **{Feature Name}** - {brief description}
   - Key file: {path}

**Tests Added:**
- {test-file.ts}: {X} tests covering {feature}
- {test-file.ts}: {Y} tests covering {feature}

**Commits:**
| Hash | Message | Files |
|------|---------|-------|
| {hash} | {message} | {count} |
| {hash} | {message} | {count} |

---

## A - Assessment

### What's Complete
- [x] {Completed item 1}
- [x] {Completed item 2}
- [x] {Completed item 3}

### What's Partial (In Progress)
- [ ] {In-progress item} - {X}% complete
  - Done: {what's done}
  - Remaining: {what's left}
  - Estimated: {time to complete}

### What's Blocked
- [ ] {Blocked item}
  - **Blocker:** {specific blocker}
  - **Owner:** {who can unblock}
  - **ETA:** {if known}

### Quality Status
| Metric | Value | Status |
|--------|-------|--------|
| Build | {PASSING/FAILING} | {details} |
| Tests | {X}/{Y} passing | {coverage}% |
| Lint | {X errors, Y warnings} | {status} |
| TypeCheck | {status} | {details} |
| Validation | {X}/70 | {status} |

### Known Issues
| Issue | Severity | Location | Notes |
|-------|----------|----------|-------|
| {description} | {HIGH/MED/LOW} | {file:line} | {notes} |

---

## R - Resources

### Environment Variables Required
```bash
# Required for this project
{VAR_NAME}={description or hint}
{VAR_NAME}={description or hint}

# Optional
{VAR_NAME}={description}
```

### Database State
- **Type:** {PostgreSQL/MongoDB/etc.}
- **Migrations:** {status - up to date, pending, etc.}
- **Seed Data:** {status}
- **Connection:** {location of connection config}

### External Services
| Service | Status | Credentials Location |
|---------|--------|---------------------|
| {service} | {active/inactive} | {.env variable name} |
| {service} | {active/inactive} | {.env variable name} |

### Key URLs
- **Local Dev:** {url}
- **API Docs:** {url}
- **Staging:** {url if applicable}
- **Docs:** {url}

### Important Paths
- **Project Root:** {absolute path}
- **Planning Docs:** {path}/.planning/
- **Skills Library:** ~/.claude/plugins/dominion-flow/skills-library/
- **Handoffs:** ~/.claude/warrior-handoffs/

---

## R - Readiness

### Ready For
{What the next session can immediately start on}

1. {Ready item 1} - all prerequisites met
2. {Ready item 2} - dependencies satisfied

### Blocked On
{What's preventing certain progress}

| Item | Blocker | Owner | ETA |
|------|---------|-------|-----|
| {item} | {blocker} | {who} | {when} |

### Dependencies Status

**Satisfied:**
- [x] {Dependency 1}
- [x] {Dependency 2}

**Pending:**
- [ ] {Dependency} - {status, who's responsible}

### Pre-requisites for Next Phase
- [ ] {Prerequisite 1}
- [ ] {Prerequisite 2}

---

## I - Issues

### Current Bugs
| Bug | Severity | File:Line | Status | Notes |
|-----|----------|-----------|--------|-------|
| {description} | {HIGH/MED/LOW} | {location} | {open/investigating} | {notes} |

### Technical Debt
| Item | Reason Deferred | Impact | Planned Resolution |
|------|-----------------|--------|-------------------|
| {item} | {reason} | {impact} | Phase {N} |
| {item} | {reason} | {impact} | Phase {N} |

### Deferred Items
| Item | Reason | Phase |
|------|--------|-------|
| {item} | {reason} | {N} |

### Unresolved Questions
1. **{Question}**
   - Context: {context}
   - Who might know: {person or resource}
   - Impact if unresolved: {impact}

### Assumptions Made (Need Review)
| Assumption | Location | Risk | Review Priority |
|------------|----------|------|-----------------|
| {assumption} | {file:line or decision} | {LOW/MED/HIGH} | {priority} |

---

## O - Outlook

### Next Session Should

**Immediate Priority (Do First):**
1. **{First action}** (~{time estimate})
   - {Sub-task 1}
   - {Sub-task 2}
   - Verification: {how to verify completion}

**Then:**
2. **{Second action}** (~{time estimate})
   - {Details}

3. **{Third action}** (~{time estimate})
   - {Details}

### Recommended Approach
{Specific guidance for how to tackle next work}

- Start with: {specific starting point}
- Watch out for: {potential pitfall}
- Key file to understand first: {path}

### Time Estimates
| Task | Estimate | Confidence |
|------|----------|------------|
| Complete current phase | {X} hours | {HIGH/MED/LOW} |
| Reach next milestone | {X} hours | {HIGH/MED/LOW} |

### Potential Blockers to Watch
- {Potential issue 1} - mitigation: {approach}
- {Potential issue 2} - mitigation: {approach}

### Long-term Context
{Anything important about the bigger picture}

---

## R - References

### Skills Applied This Session
| Skill | Phase/Plan | Application | Impact |
|-------|------------|-------------|--------|
| {category/skill} | {N}-{NN} | {what it helped with} | {measurable result} |
| {category/skill} | {N}-{NN} | {what it helped with} | {measurable result} |

### Key Commits This Session
| Hash | Message | Files | Plan |
|------|---------|-------|------|
| {hash} | {message} | {count} | {N}-{NN} |
| {hash} | {message} | {count} | {N}-{NN} |

### Decisions Made
| Decision | Rationale | Impact | Reversible |
|----------|-----------|--------|------------|
| {decision} | {why} | {what it affects} | {yes/no} |
| {decision} | {why} | {what it affects} | {yes/no} |

### Related Documentation
- {Doc 1}: {path or URL}
- {Doc 2}: {path or URL}

### External Resources Used
- {Resource}: {URL}
- {Resource}: {URL}

### Planning Artifacts
- CONSCIENCE.md: {path}/.planning/CONSCIENCE.md
- VISION.md: {path}/.planning/VISION.md
- Current Phase: {path}/.planning/phases/{N}-{name}/
- Verification: {path}/.planning/phases/{N}-{name}/{N}-VERIFICATION.md

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

# View verification status
cat .planning/phases/{N}-{name}/{N}-VERIFICATION.md
```

---

## Session Metrics

| Metric | Value |
|--------|-------|
| Session Duration | {X} hours |
| Plans Completed | {count} |
| Tasks Completed | {count} |
| Commits | {count} |
| Files Created | {count} |
| Files Modified | {count} |
| Tests Added | {count} |
| Skills Applied | {count} |
| Honesty Checkpoints | {count} |
| Deviations Documented | {count} |
| Blockers Encountered | {count} |

---

*Handoff created: {timestamp}*
*Project: {project_name}*
*Session: {date}*
*Next action: {recommended action}*
```

---

## Step 4: Update CONSCIENCE.md

**Purpose:** Record handoff reference for session continuity.

```markdown
## Session Continuity
- **Last session:** {timestamp}
- **Stopped at:** {description of stopping point}
- **Resume file:** ~/.claude/warrior-handoffs/{project}_{date}.md
- **Next:** {recommended next action}

## Recent Activity
- **{timestamp}:** Session handoff created
- **{previous}:** {previous activity}
```

---

## Step 5: Save Handoff File

**Purpose:** Persist handoff to standard location for retrieval.

### File Naming Convention

```bash
# Standard naming
HANDOFF_FILE=~/.claude/warrior-handoffs/{PROJECT_NAME}_{YYYY-MM-DD}.md

# If multiple sessions same day
HANDOFF_FILE=~/.claude/warrior-handoffs/{PROJECT_NAME}_{YYYY-MM-DD}_{N}.md

# Examples:
# my-project_2026-01-22.md
# my-project_2026-01-22_2.md (second session same day)
```

### Save Process

```bash
# Ensure directory exists
mkdir -p ~/.claude/warrior-handoffs/

# Write handoff file
write {HANDOFF_CONTENT} to {HANDOFF_FILE}

# Verify write
if [ -f "$HANDOFF_FILE" ]; then
  echo "Handoff saved successfully"
else
  echo "ERROR: Failed to save handoff"
fi
```

---

## Step 6: Display Completion Summary

**Purpose:** Confirm handoff creation and provide next steps.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ HANDOFF CREATED                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Project: {project_name}                                                     ║
║  Session: {date}                                                             ║
║  Duration: {X} hours                                                         ║
║                                                                              ║
║  Summary:                                                                    ║
║    Plans completed: {count}                                                  ║
║    Commits: {count}                                                          ║
║    Files changed: {created + modified}                                       ║
║    Skills applied: {count}                                                   ║
║    Tests: {passing}/{total}                                                  ║
║                                                                              ║
║  Saved To:                                                                   ║
║    {handoff_file_path}                                                       ║
║                                                                              ║
║  CONSCIENCE.md: Updated                                                           ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ NEXT SESSION                                                                 ║
├──────────────────────────────────────────────────────────────────────────────┤
║                                                                              ║
║  Run `/fire-6-resume` to restore full context                               ║
║                                                                              ║
║  Priority: {next recommended action}                                         ║
║  Estimate: {time estimate for next action}                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

</process>

---

## Agent Spawning

This workflow does NOT spawn agents. It compiles information from existing documents created by executors and verifiers.

**Rationale:** Handoff creation is a compilation task, not an execution task. All the information needed already exists in RECORD.md files and CONSCIENCE.md.

---

## Success Criteria

### Required Outputs
- [ ] Handoff file created at `~/.claude/warrior-handoffs/{project}_{date}.md`
- [ ] All 7 WARRIOR sections populated (W-A-R-R-I-O-R)
- [ ] Dominion Flow Metrics included in frontmatter
- [ ] CONSCIENCE.md updated with handoff reference
- [ ] Quick resume commands included

### Handoff Quality Checklist

| Section | Requirement |
|---------|-------------|
| **W (Work)** | All completed work documented with file references and commits |
| **A (Assessment)** | Clear status of complete/partial/blocked items with quality metrics |
| **R (Resources)** | All required env vars, credentials, database state, URLs documented |
| **R (Readiness)** | Clear statement of what's ready vs blocked with owners |
| **I (Issues)** | All bugs, debt, deferred items, questions, assumptions captured |
| **O (Outlook)** | Specific next steps with time estimates and recommended approach |
| **R (References)** | Skills, commits, decisions, and related docs linked |

### Completeness Verification

Before finalizing handoff, verify:
- [ ] Someone reading this could continue without questions
- [ ] All blockers have owners and context
- [ ] All assumptions are flagged for review
- [ ] Time estimates are realistic
- [ ] Paths are absolute, not relative
- [ ] Commands are copy-pasteable

---

## Error Handling

### No CONSCIENCE.md Found

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ ERROR: Project Not Initialized                                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  No .planning/CONSCIENCE.md found.                                                ║
║                                                                              ║
║  Action: Run `/fire-1a-new` to initialize project first.                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### No Work to Handoff

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ WARNING: No Recent Work Detected                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  No RECORD.md files found since last handoff.                              │
│                                                                             │
│  Options:                                                                   │
│    A) Create minimal handoff with current state (state-only)                │
│    B) Cancel handoff creation                                               │
│                                                                             │
│  Note: A minimal handoff still captures project state and next actions.     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Cannot Write to Handoffs Directory

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ ERROR: Cannot Save Handoff                                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Cannot write to: ~/.claude/warrior-handoffs/                                ║
║                                                                              ║
║  Action: Create directory and retry:                                         ║
║    mkdir -p ~/.claude/warrior-handoffs/                                      ║
║                                                                              ║
║  Or use --no-save to display handoff without saving.                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Incomplete Session Data

If some data is missing (e.g., no commits, no SUMMARY files):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ WARNING: Incomplete Session Data                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Missing data for complete handoff:                                         │
│    - No commits found since last handoff                                    │
│    - No RECORD.md files found                                              │
│                                                                             │
│  Proceeding with available data. Some sections may be incomplete.           │
│                                                                             │
│  Sections affected:                                                         │
│    - W (Work): Limited to CONSCIENCE.md changes only                             │
│    - R (References): No commit history                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## References

- **Template:** `@templates/fire-handoff.md` - Unified handoff format
- **Protocol:** `@references/honesty-protocols.md` - WARRIOR foundation
- **Brand:** `@references/ui-brand.md` - Visual output standards
