# Advanced Orchestration Patterns

**Version:** 1.0
**Date:** January 2026
**Status:** INTEGRATED from Dominion Flow + RALPH WIGGUM + N8N PATTERNS

A synthesis of best practices from Dominion Flow (Dominion Flow), Ralph Wiggum loops, and n8n workflow patterns for advanced AI agent orchestration.

---

## Executive Summary

Three powerful patterns for AI-assisted development:

1. **State Management** (from Dominion Flow) - Living memory files that enable session continuity
2. **Self-Iterating Loops** (from Ralph Wiggum) - Autonomous iteration with completion promises
3. **Breath-Based Parallel Execution** (from Dominion Flow) - Maximize throughput with dependency-aware parallelism

**Key Insight:** When AI generates code instantly, **feedback mechanisms become the true bottleneck**. These patterns compress feedback loops and enable rapid generate-test-iterate cycles.

---

## Pattern 1: State Management (Living Memory)

### The Problem

Information is captured in summaries, issues, and decisions but not systematically consumed. Sessions start without context. Context is lost across sessions.

### The Solution: CONSCIENCE.md

A single, small file (<100 lines) that's:
- Read first in every workflow
- Updated after every significant action
- Contains digest of accumulated context
- Enables instant session restoration

### Template

```markdown
# Project State

## Project Reference

See: .planning/PROJECT.md (updated [date])

**Core value:** [One-liner describing the ONE thing that matters]
**Current focus:** [Current phase name]

## Current Position

Phase: [X] of [Y] ([Phase name])
Plan: [A] of [B] in current phase
Status: [Ready to plan / Planning / Ready to execute / In progress / Phase complete]
Last activity: [YYYY-MM-DD] — [What happened]

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: [N]
- Average duration: [X] min
- Total execution time: [X.X] hours

**Recent Trend:**
- Last 5 plans: [durations]
- Trend: [Improving / Stable / Degrading]

## Accumulated Context

### Decisions
- [Phase X]: [Decision summary]
- [Phase Y]: [Decision summary]

### Pending Todos
[From pending todos - ideas captured during sessions]

### Blockers/Concerns
[Issues that affect future work]

## Session Continuity

Last session: [YYYY-MM-DD HH:MM]
Stopped at: [Description of last completed action]
Resume file: [Path to continue-here file if exists]
```

### Lifecycle

| Event | Action |
|-------|--------|
| Project Init | Create CONSCIENCE.md after roadmap |
| Every Workflow Start | Read CONSCIENCE.md first |
| After Each Plan | Update position, note decisions |
| Phase Transition | Update progress bar, clear resolved blockers |

### Size Constraint

**Keep under 100 lines.** It's a DIGEST, not an archive. If it's too long, "read once, know where we are" fails.

---

## Pattern 2: Self-Iterating Loops (Ralph Wiggum)

### The Concept

Run the AI agent on the same prompt repeatedly until a stop condition is met. The prompt never changes, but the world does:
- Previous work persisted in files
- Git history of what changed
- Test results, build output, error messages
- Any other artifacts from the last run

### Basic Structure

```bash
/ralph-loop "Build X with tests. Output DONE when all tests pass." \
  --completion-promise "DONE" \
  --max-iterations 50
```

### When to Use

| Good For | Bad For |
|----------|---------|
| Getting test suites to pass | Tasks requiring human judgment |
| Fixing all linter/type errors | Unclear success criteria |
| Building features with clear acceptance criteria | Production debugging |
| Greenfield projects with defined "done" | One-shot operations |

### Key Principles

**1. Completion Promise**
Define success criteria upfront. "Make it better" doesn't work. "All tests pass" does.

**2. Threshold-Based Stopping**
Stop when:
- Self-rating hits target (e.g., 9/10)
- Max iterations reached
- Completion promise detected in output

**3. Regression Detection**
Progress isn't linear. The loop must recognize when it went astray and course-correct.

**4. Specific Self-Critique**
Concrete questions drive improvement:
- Is the test passing now?
- Is there symmetry/consistency?
- Does the structure meet requirements?
- Are edge cases handled?

### Implementation for WARRIOR

```markdown
## Self-Iteration Checklist

Before starting a loop:
- [ ] Define clear success criteria
- [ ] Set max iteration limit
- [ ] Identify what artifacts to check
- [ ] Establish baseline (current state)

During iteration:
- [ ] Compare against baseline
- [ ] Log what changed
- [ ] Rate progress (1-10)
- [ ] Identify specific improvements needed

Stop when:
- [ ] Success criteria met
- [ ] Max iterations reached
- [ ] No meaningful progress for 3 iterations
```

---

## Pattern 3: Breath-Based Parallel Execution

### The Concept

Group independent tasks into breaths. Execute tasks within a breath in parallel. Wait for breath completion before starting the next breath.

### Why It Works

- **Orchestrator context usage:** ~10-15%
- **Each subagent:** Fresh 200k context
- **No polling:** Task tool blocks until completion
- **No context bleed:** Orchestrator never reads workflow internals

### Breath Assignment

```yaml
# Breath 1: No dependencies, can run in parallel
Plan 01:
  breath: 1
  depends_on: []
  files_modified: [src/features/user/]
  autonomous: true

Plan 02:
  breath: 1
  depends_on: []
  files_modified: [src/features/product/]
  autonomous: true

# Breath 2: Depends on Breath 1
Plan 03:
  breath: 2
  depends_on: ["01", "02"]
  files_modified: [src/features/dashboard/]
  autonomous: false  # Has checkpoint
```

### Execution Flow

```
Breath 1: [Plan 01] [Plan 02] [Plan 03]  ← Parallel
           ↓         ↓         ↓
        Complete  Complete  Complete
                    ↓
Breath 2: [Plan 04] [Plan 05]            ← Parallel
           ↓         ↓
        Complete  Checkpoint → User Input → Resume
                    ↓
Breath 3: [Plan 06]                      ← Sequential
           ↓
        Complete + Verify
```

### Checkpoint Types

| Type | Use For | Behavior |
|------|---------|----------|
| `auto` | Everything Claude can do | Fully autonomous |
| `checkpoint:human-verify` | Visual/functional verification | Pauses, returns to user |
| `checkpoint:decision` | Implementation choices | Presents options to user |
| `checkpoint:human-action` | Unavoidable manual steps | Pauses for human action |

### Failure Handling

| Scenario | Response |
|----------|----------|
| Subagent fails mid-plan | RECORD.md won't exist, detect and report |
| Dependency chain breaks | Ask user: continue or stop? |
| All agents in breath fail | Stop, report for investigation |
| Checkpoint won't resolve | Skip plan or abort execution |

---

## Pattern 4: Goal-Backward Verification

### The Problem

Task completion ≠ Goal achievement. A task "create chat component" can complete by creating a placeholder.

### The Solution: Must-Haves

Define what must be TRUE for the goal to be achieved:

```yaml
must_haves:
  truths:                    # Observable behaviors
    - "User can see existing messages"
    - "User can send a message"
    - "Messages persist across refresh"

  artifacts:                 # Files that must exist
    - path: "src/components/Chat.tsx"
      provides: "Message list rendering"
      min_lines: 30
    - path: "src/app/api/chat/route.ts"
      exports: ["GET", "POST"]

  key_links:                 # Connections between artifacts
    - from: "src/components/Chat.tsx"
      to: "/api/chat"
      pattern: "fetch.*api/chat"
```

### Verification Flow

1. Plan-phase derives must_haves from phase goal
2. Execute-phase runs all plans
3. Verification subagent checks must_haves against codebase
4. Gaps found → fix plans created → execute → re-verify
5. All must_haves pass → phase complete

---

## Pattern 5: Context Efficiency

### Orchestrator vs Subagent Roles

| Orchestrator (Lean) | Subagent (Full Context) |
|---------------------|------------------------|
| Read plan frontmatter | Load full workflow |
| Analyze dependencies | Load templates, references |
| Fill template strings | Execute plan with full capacity |
| Spawn Task calls | Create artifacts, commits |
| Collect results | Return structured output |

### Anti-Patterns

- Orchestrator reading full workflow files
- Subagent loading unnecessary context
- Polling for completion (use blocking Task)
- Reflexive dependency chaining

### Prompt Templates

**Subagent Task Prompt:**
```markdown
<objective>
Execute plan {plan_number} of phase {phase_number}-{phase_name}.
Commit each task atomically. Create RECORD.md. Update CONSCIENCE.md.
</objective>

<execution_context>
@~/.claude/plugins/dominion-flow/workflows/execute-plan.md
@~/.claude/plugins/dominion-flow/templates/summary.md
</execution_context>

<context>
Plan: @{plan_path}
Project state: @.planning/CONSCIENCE.md
</context>

<success_criteria>
- [ ] All tasks executed
- [ ] Each task committed individually
- [ ] RECORD.md created
- [ ] CONSCIENCE.md updated
</success_criteria>
```

---

## Integration with WARRIOR Workflow

### Session Start Protocol

1. Read CONSCIENCE.md (if exists) for project context
2. Check WARRIOR handoffs for session continuity
3. Present current position to user
4. Identify next action based on status

### During Execution

1. Use breath-based execution for multi-task phases
2. Apply self-iteration for tasks needing refinement
3. Create checkpoints for human verification
4. Update CONSCIENCE.md after each significant action

### Session End Protocol

1. Update CONSCIENCE.md with final position
2. Create WARRIOR handoff if context exhaustion approaching
3. Log performance metrics
4. Note any blockers for next session

---

## Quick Reference

### Commands Pattern (Dominion-Style)

| Command | Purpose |
|---------|---------|
| `/warrior:status` | Show current CONSCIENCE.md |
| `/warrior:execute` | Run breath-based execution |
| `/warrior:verify` | Run goal-backward verification |
| `/warrior:iterate` | Start self-improvement loop |

### Velocity Metrics

Track these to understand execution patterns:
- Plans completed per session
- Average duration per plan
- Regression count (iterations that got worse)
- Checkpoint approval rate

### Success Indicators

- CONSCIENCE.md under 100 lines
- <15% orchestrator context usage
- Completion within max iterations
- All must_haves verified

---

## Sources

- **Dominion Flow:** [glittercowboy/get-shit-done](https://github.com/glittercowboy/get-shit-done)
- **Ralph Wiggum:** [UtpalJayNadiger/ralphwiggumexperiment](https://github.com/UtpalJayNadiger/ralphwiggumexperiment)
- **n8n-MCP:** [czlonkowski/n8n-mcp](https://github.com/czlonkowski/n8n-mcp)
- **n8n-skills:** [czlonkowski/n8n-skills](https://github.com/czlonkowski/n8n-skills)

---

**Created:** January 2026
**For:** WARRIOR Workflow Integration
**License:** MIT
