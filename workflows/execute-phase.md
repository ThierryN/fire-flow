# Workflow: Phase Execution Orchestration

<purpose>
Execute all plans in a specified phase using breath-based parallel execution. Each plan is handled by a fire-executor agent that applies honesty protocols, references skills, creates atomic commits, and produces unified handoff documentation. This workflow ensures work is done correctly while maintaining complete context for verification and session continuity.
</purpose>

---

<core_principle>
**Execute honestly, commit atomically, document thoroughly.** Every task gets a commit. Every uncertainty gets documented. Every skill application gets cited. The handoff document should enable any AI or human to continue exactly where you left off.
</core_principle>

---

<required_reading>
Before executing this workflow, load:
```markdown
@.planning/CONSCIENCE.md                        # Current project position
@.planning/phases/{N}-{name}/*-BLUEPRINT.md     # All plans for this phase
@agents/fire-executor.md                  # Executor agent configuration
@agents/fire-verifier.md                  # Verifier agent configuration
@templates/fire-handoff.md                # Unified handoff format
@references/honesty-protocols.md           # Execution honesty guidance
```
</required_reading>

---

<process>

## Step 1: Load Context and Validate

**Purpose:** Ensure we have valid plans to execute.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                         DOMINION FLOW > PHASE {N} EXECUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Load CONSCIENCE.md:**
```markdown
@.planning/CONSCIENCE.md

Extract:
- Current phase and status
- Completed plans (if resuming with --continue)
- Session context
- Skills applied so far
```

**Parse Arguments:**
```yaml
required:
  phase_number: integer

optional:
  --breath: "Execute only a specific breath (e.g., --breath 2)"
  --plan: "Execute only a specific plan (e.g., --plan 03-02)"
  --skip-verify: "Skip verification after execution (not recommended)"
  --continue: "Continue from last checkpoint (for interrupted execution)"
```

---

## Step 2: Discover and Parse Plans

**Purpose:** Build execution manifest from plan files.

```bash
# Find all plans for this phase
ls .planning/phases/{N}-{name}/{N}-*-BLUEPRINT.md

# Parse each plan's frontmatter for breath assignment
for plan in plans:
  extract: breath, depends_on, autonomous, files_to_create, files_to_modify
```

**Build Execution Manifest:**
```markdown
## Phase {N} Execution Manifest

### Plans Discovered
| Plan | Name | Breath | Dependencies | Autonomous | Status |
|------|------|------|--------------|------------|--------|
| {N}-01 | {name} | 1 | none | true | pending |
| {N}-02 | {name} | 1 | none | true | pending |
| {N}-03 | {name} | 2 | {N}-01 | true | pending |
| {N}-04 | {name} | 2 | {N}-01, {N}-02 | false | pending |

### Breath Summary
- **Breath 1:** 2 plans (can run in parallel)
- **Breath 2:** 2 plans (depends on Breath 1)
```

---

## Step 3: Group Plans by Breath

**Purpose:** Organize plans for parallel execution within breaths.

**Breath Grouping Rules:**
1. Plans in same breath execute in parallel
2. Breath N+1 waits for ALL Breath N plans to complete
3. Dependencies must be in earlier breaths (validated during planning)
4. If `--breath` flag: execute only that breath
5. If `--plan` flag: execute only that plan (ignore breath)

**Display Execution Plan:**
```
Execution Plan
  Breath 1: 2 plans (parallel)
    |- {N}-01: {description}
    |- {N}-02: {description}
  Breath 2: 2 plans
    |- {N}-03: {description} (depends on {N}-01)
    |- {N}-04: {description} (depends on {N}-01, {N}-02)
```

**Handle --continue Flag:**
```bash
# If continuing from checkpoint
if [ "$CONTINUE" = true ]; then
  # Read .continue-here.md if exists
  if [ -f ".planning/phases/{N}-{name}/.continue-here.md" ]; then
    # Load context, skip completed plans
    COMPLETED_PLANS=$(extract completed from .continue-here.md)
  fi
fi
```

---

## Step 4: Execute Breath

**Purpose:** Run all plans in current breath (parallel within breath, sequential across breaths).

For each breath:

```
━━━ DOMINION FLOW > BREATH {W} EXECUTION ━━━
```

### Spawn fire-executor Agents (Parallel)

```
Spawning executors for Breath {W}...
  fire-executor: Plan {N}-01 - {description}
  fire-executor: Plan {N}-02 - {description}
```

**Per-Executor Context Injection:**
```markdown
<plan_context>
@.planning/phases/{N}-{name}/{N}-{NN}-BLUEPRINT.md
</plan_context>

<skills_context>
Skills to apply for this plan:
@skills-library/{category}/{skill-1}.md
@skills-library/{category}/{skill-2}.md

Apply these patterns during implementation.
Document which skills you actually used and how.
</skills_context>

<state_context>
@.planning/CONSCIENCE.md
Current project position and accumulated context.
</state_context>

<honesty_protocol>
While executing tasks:

**If uncertain:**
1. Document the uncertainty immediately
2. Search skills library: /fire-search "[topic]"
3. Research if needed (WebSearch as last resort)
4. Document what you learned
5. Proceed with transparency, add comments

**If blocked:**
1. Admit the blocker explicitly - don't work around silently
2. Document what's blocking in detail
3. Create .continue-here.md with full context
4. Do NOT fake progress

**If assuming:**
1. Document the assumption
2. Add code comment: // ASSUMPTION: [reason]
3. Add to handoff Issues section for review
4. Proceed transparently
</honesty_protocol>

<commit_rules>
**CRITICAL: Atomic commits per task**

After completing each task:
1. Stage only files related to this task
2. Commit with conventional commit format
3. Reference plan and task number
4. Cite skills applied

Format:
```
{type}({scope}): {description}

- {change 1}
- {change 2}
- Applied skill: {skill-name}

Task {X} of Plan {N}-{NN}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```
</commit_rules>

<deviation_rules>
**When implementation deviates from plan:**

**Auto-fix (no user input needed):**
- Minor syntax adjustments
- Import path corrections
- Variable naming improvements
- Additional error handling

**Ask user (require checkpoint):**
- Different approach than planned
- New dependencies needed
- Scope changes
- Missing requirements discovered
- Architectural decisions

**Document ALL deviations in handoff, regardless of type.**
</deviation_rules>
```

---

## Step 5: Power-Executor Task Execution

**Purpose:** Each executor implements its plan's tasks with full transparency.

### Per-Task Execution Flow

```markdown
## Executing Task {X}: {Task Name}

### Pre-Task Honesty Check
- What I know: {relevant experience/code I've reviewed}
- What I'm uncertain about: {gaps identified}
- Skills to apply: {skill-category/skill-name}

### Skill Application
**Applying:** {category/skill-name}
**Pattern Used:** {specific pattern from skill}
**Adaptation:** {how adapted for this context}
**Code Location:** {file:lines where applied}

### Implementation
{Actual code changes with file:line references}

Created: {file} ({lines} lines)
```typescript
// Key code snippet showing implementation
```

Modified: {file}
- Lines X-Y: {change description}

### Verification
```bash
{Run verification commands from plan}
```
**Result:** PASS | FAIL

### Commit
```bash
git add {files}
git commit -m "$(cat <<'EOF'
{type}({scope}): {description}

- {change 1}
- {change 2}
- Applied skill: {skill-name}

Task {X} of Plan {N}-{NN}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```
**Commit:** {hash}

### Task Honesty Status
- **Certainty Level:** High | Medium | Low
- **Gaps Encountered:** {list or "none"}
- **Assumptions Made:** {list or "none"}
- **Skills Applied:** {list}
- **Blockers:** {list or "none"}
- **Deviations:** {list or "none"}
```

### Handle Checkpoints

For `checkpoint:human-verify` tasks:

```markdown
## CHECKPOINT: Human Verification Required

### What Was Built
{Summary of completed work up to this point}

### Files Created/Modified
- {file1.ts} - {description}
- {file2.ts} - {description}

### How to Verify
1. {Specific step 1}
2. {Specific step 2}
3. {Specific step 3}

### Expected Results
- {Expected behavior 1}
- {Expected behavior 2}

### Commands to Run
```bash
{verification commands}
```

### Resume Command
Type "approved" to continue execution
Type "issues: [description]" to report problems
```

---

## Step 6: Handle Blocking Issues

**Purpose:** Gracefully handle situations where execution cannot proceed.

### Create .continue-here.md

```markdown
# Continue Here: Plan {N}-{NN}

## Blocked At
**Task:** {task number and description}
**Time:** {timestamp}

## Blocker Details
**Type:** {missing-info | missing-access | dependency-issue | technical-issue}
**Description:** {detailed explanation}

## What's Complete
- [x] Task 1: {description} (commit: {hash})
- [x] Task 2: {description} (commit: {hash})
- [ ] Task 3: {BLOCKED}
- [ ] Task 4: {not started}

## What's Needed to Continue
1. {Specific requirement 1}
2. {Specific requirement 2}

## Attempts Made
- {Attempt 1}: {result}
- {Attempt 2}: {result}

## Context for Resumption
{Any important context the next session needs}

## Files in Progress
- {file}: {state - partial implementation at line X}

## Resume Command
```bash
/fire-3-execute {N} --continue
```

---
*Created: {timestamp}*
```

---

## Step 7: Wait for Breath Completion

**Purpose:** Ensure all parallel executors finish before proceeding.

```
Breath {W} in progress...
  |- fire-executor Plan {N}-01: Running (backend)
  |- fire-executor Plan {N}-02: Running (frontend)

[Updates as executors complete]

  |- fire-executor Plan {N}-01: Complete (12 min)
  |- fire-executor Plan {N}-02: Running (frontend)

[After all complete]

Breath {W} complete
  |- Plan {N}-01: Complete (12 min, 4 commits)
  |- Plan {N}-02: Complete (8 min, 3 commits)
```

**Breath Completion Checks:**
- [ ] All executors finished (success or documented failure)
- [ ] All RECORD.md files created
- [ ] No unresolved blocking errors
- [ ] No undocumented deviations

**If Any Executor Blocked:**
- Pause breath execution
- Display blocking issue
- Create consolidated .continue-here.md
- Offer options: resolve and continue, skip plan, create handoff

---

## Step 8: Create fire-handoff.md (Per Plan)

**Purpose:** Each executor creates comprehensive handoff documentation.

**Output Location:**
```
.planning/phases/{N}-{name}/{N}-{NN}-RECORD.md
```

**Unified fire-handoff Format:**
```markdown
---
# Dominion Flow Execution Metadata
phase: {N}-{name}
plan: {NN}
subsystem: {category}
duration: "{X} min"
start_time: "{ISO timestamp}"
end_time: "{ISO timestamp}"

# WARRIOR Skills & Quality
skills_applied:
  - "{category}/{skill-name}"
honesty_checkpoints:
  - task: {N}
    gap: "{what was uncertain}"
    action: "{how it was resolved}"
validation_score: "{preliminary}/70"

# Dominion Flow Dependency Tracking
requires: ["dependency1"]
provides: ["capability1", "capability2"]
affects: ["component1"]
tech_stack_added: ["package@version"]
patterns_established: ["pattern-name"]

# Files Changed
key_files:
  created:
    - "path/to/file.ts"
  modified:
    - "path/to/existing.ts"

# Decisions
key_decisions:
  - "Decision: {what} | Rationale: {why}"
---

# Power Handoff: Plan {N}-{NN} - {Name}

## Quick Summary
{1-2 sentence summary of what was accomplished}

---

## Dominion Flow Accomplishments

### Task Commits
| Task | Description | Commit | Duration | Status |
|------|-------------|--------|----------|--------|
| 1 | {description} | {hash} | {X min} | Complete |
| 2 | {description} | {hash} | {X min} | Complete |

### Files Created
| File | Lines | Purpose |
|------|-------|---------|
| {path} | {count} | {purpose} |

### Files Modified
| File | Changes | Purpose |
|------|---------|---------|
| {path} | {description} | {purpose} |

### Decisions Made
1. **{Decision}:** {rationale}

---

## Skills Applied (WARRIOR)

### {category/skill-name}
- **Problem:** {what problem this solved}
- **Pattern Applied:** {specific pattern from skill}
- **Code Location:** {file:lines}
- **Result:** {measurable improvement or outcome}

---

## WARRIOR 7-Step Handoff

### W - Work Completed
{Detailed list of accomplishments with file:line references}

### A - Assessment
- **Completion:** {X}% of plan tasks
- **Quality:** {assessment}
- **Tests:** {status}

### R - Resources
{Environment variables, database state, external services}

### R - Readiness
- **Ready For:** {what can proceed}
- **Blocked On:** {blockers if any}

### I - Issues
- **Known Issues:** {list}
- **Assumptions:** {list}
- **Technical Debt:** {list}

### O - Outlook
- **Next Steps:** {what should happen next}

### R - References
- **Skills Used:** {list with links}
- **Commits:** {list with hashes}
- **Related Docs:** {links}

---

## Metrics
| Metric | Value |
|--------|-------|
| Duration | {X} min |
| Tasks Completed | {X}/{Y} |
| Commits | {count} |
| Files Created | {count} |
| Files Modified | {count} |
| Skills Applied | {count} |
| Honesty Checkpoints | {count} |
```

---

## Step 9: Spawn fire-verifier (After All Breaths)

**Purpose:** Validate completed work meets requirements.

```
━━━ DOMINION FLOW > PHASE {N} VERIFICATION ━━━

Spawning fire-verifier for Phase {N}...
```

**Verifier Context:**
```markdown
<verification_scope>
Phase: {N} - {name}
Plans Executed: {list}
Total Must-Haves: {count aggregated from all plans}
WARRIOR Checks: 60 items across 6 categories
</verification_scope>

<must_haves>
{Aggregated must_haves from all {N}-*-BLUEPRINT.md files}
</must_haves>

<warrior_checklist>
@references/validation-checklist.md
</warrior_checklist>
```

**Verification Outputs:**
- `{N}-VERIFICATION.md` with detailed results
- Gap analysis if any checks fail
- Routing recommendation

**Route Based on Result:**
- **PASS:** Proceed to Step 10 (completion)
- **FAIL with gaps:** Display gaps, offer `/fire-2-plan {N} --gaps`

---

## Step 10: Update CONSCIENCE.md and SKILLS-INDEX.md

**Purpose:** Reflect execution completion in project state.

### CONSCIENCE.md Updates
```markdown
## Current Position
- **Phase:** {N} of {total}
- **Breath:** Complete
- **Status:** {Complete | Complete with gaps}
- **Last activity:** {timestamp} - Phase {N} execution complete
- **Progress:** [{progress_bar}] {progress_percent}%

## Dominion Flow Progress Tracking
### Phase Status
| Phase | Name | Status | Plans | Completed |
|-------|------|--------|-------|-----------|
| {N} | {name} | Complete | {X} | {X} |

## WARRIOR Integration
- **Skills Applied:** {new_total} total
  - {skill-1} (Phase {N}, Plan {NN})
  - {skill-2} (Phase {N}, Plan {NN})
- **Honesty Checkpoints:** {count}
- **Validation Status:** Phase {N} {passed/failed} {X}/70 checks
```

### SKILLS-INDEX.md Updates
```markdown
## By Phase

### Phase {N}: {name}
**Plan {N}-01:**
- {category}/{skill-1} - {brief note on application}
- {category}/{skill-2}

**Plan {N}-02:**
- {category}/{skill-3}
```

---

## Step 11: Display Completion Summary

**Purpose:** Confirm execution success and provide next steps.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ PHASE {N} EXECUTION COMPLETE                                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Phase: {N} - {name}                                                         ║
║  Plans Executed: {count}                                                     ║
║  Breaths: {wave_count}                                                         ║
║  Total Time: {duration}                                                      ║
║                                                                              ║
║  Execution Summary:                                                          ║
║    Breath 1:                                                                   ║
║      {N}-01 - {description} (12 min, 4 commits)                              ║
║      {N}-02 - {description} (8 min, 3 commits)                               ║
║    Breath 2:                                                                   ║
║      {N}-03 - {description} (15 min, 5 commits)                              ║
║                                                                              ║
║  Commits: {total_commits}                                                    ║
║  Files Created: {count}                                                      ║
║  Files Modified: {count}                                                     ║
║  Skills Applied: {count}                                                     ║
║  Honesty Checkpoints: {count}                                                ║
║  Validation: {X}/70 checks passed                                            ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ NEXT UP                                                                      ║
├──────────────────────────────────────────────────────────────────────────────┤
║                                                                              ║
║  Run `/fire-4-verify {N}` for detailed validation report                    ║
║  Or run `/fire-2-plan {N+1}` to plan next phase                             ║
║  Or run `/fire-5-handoff` to create session handoff                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

</process>

---

## Agent Spawning Summary

| Agent | When | Quantity | Purpose |
|-------|------|----------|---------|
| **fire-executor** | Per plan in breath | Parallel within breath | Implement plan tasks |
| **fire-verifier** | After all breaths | One | Validate completed work |

---

## Success Criteria

### Required Outputs
- [ ] All plans in phase executed (or documented as blocked)
- [ ] Atomic commits per task (not batch commits)
- [ ] All `{N}-{NN}-RECORD.md` files created (fire-handoff format)
- [ ] All verification commands from plans executed
- [ ] SKILLS-INDEX.md updated with skills applied
- [ ] CONSCIENCE.md updated with execution status
- [ ] `{N}-VERIFICATION.md` created

### Quality Checks
- [ ] No "silent struggling" - all uncertainties documented
- [ ] No hidden assumptions - all assumptions in code comments and handoff
- [ ] Skills properly cited with code locations
- [ ] Deviations from plan documented with rationale
- [ ] Checkpoint tasks handled appropriately

---

## Error Handling

### Executor Blocked
Create .continue-here.md, pause execution, display options to user.

### Verification Failed
Display gaps with severity, route to `/fire-2-plan {N} --gaps` or accept and proceed.

### Breath Timeout
Display status of each executor, offer to continue waiting or interrupt.

### Git Commit Failure
Resolve conflict, document in handoff, continue execution.

---

## References

- **Agent:** `@agents/fire-executor.md` - Execution agent with honesty protocols
- **Agent:** `@agents/fire-verifier.md` - Verification agent with combined checks
- **Template:** `@templates/fire-handoff.md` - Unified summary format
- **Protocol:** `@references/honesty-protocols.md` - Execution honesty guidance
- **Checklist:** `@references/validation-checklist.md` - 70-point validation
- **Brand:** `@references/ui-brand.md` - Visual output standards
