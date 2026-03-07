---
description: Execute a phase with breath-based parallelism and honesty protocols
---

# /fire-3-execute

> Execute phase N with breath-based parallelization and honesty protocols

---

## Purpose

Execute all plans in a specified phase using breath-based parallel execution. Each plan is handled by a fire-executor agent that applies honesty protocols, references skills, and creates unified handoff documents. After execution completes, a fire-verifier validates the work.

---

## Arguments

```yaml
arguments:
  phase_number:
    required: true
    type: integer
    description: "Phase number to execute (e.g., 1, 2, 3)"
    example: "/fire-3-execute 3"

optional_flags:
  --breath: "Execute only a specific breath (e.g., --breath 2)"
  --plan: "Execute only a specific plan (e.g., --plan 03-02)"
  --skip-verify: "Skip verification after execution (not recommended)"
  --continue: "Continue from last checkpoint (for interrupted execution)"
  --auto-continue: "Enable Double-Shot Latte pattern - no 'continue?' interrupts"
  --skip-review: "Skip the parallel code review (not recommended)"
  --autonomous: "Auto-route merge gate verdicts without human checkpoints (DEFAULT in v10.0, used by /fire-autonomous)"
  --manual: "Opt-in to human checkpoints at merge gate (v9.0 behavior)"
  --worktree: "Use git worktree isolation for parallel breath execution (v10.0)"
  --model-split: "Force architect/editor model split for all tasks (v10.0)"
```

---

## Auto-Continuation Mode (Double-Shot Latte Pattern)

When `--auto-continue` is enabled, execution proceeds without "continue?" interrupts:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ AUTO-CONTINUATION ACTIVE                                                    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                             â”‚
â”‚  Breath completion â†’ Automatic checkpoint â†’ Next breath starts immediately      â”‚
â”‚                                                                             â”‚
â”‚  Benefits:                                                                  â”‚
â”‚    â€¢ Uninterrupted execution flow                                           â”‚
â”‚    â€¢ Faster phase completion                                                â”‚
â”‚    â€¢ Progress saved at each breath checkpoint                                 â”‚
â”‚                                                                             â”‚
â”‚  Safety:                                                                    â”‚
â”‚    â€¢ Checkpoints created between breaths                                      â”‚
â”‚    â€¢ Can resume from any breath if interrupted                                â”‚
â”‚    â€¢ Blocking errors still pause execution                                  â”‚
â”‚                                                                             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Usage:**
```bash
# Full auto-execution (review is on by default in v8.0)
/fire-3-execute 2 --auto-continue
```

---

## Process

### Step 1: Load Context (Dominion Flow Standard)

```
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
                         DOMINION FLOW > PHASE {N} EXECUTION
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
```

**Load CONSCIENCE.md:**
```markdown
@.planning/CONSCIENCE.md
```

**Extract:**
- Current phase and status
- Completed plans (if resuming)
- Session context

### Step 2: Discover Plans (Dominion Flow Standard)

**Scan for plans:**
```bash
.planning/phases/{N}-{name}/{N}-*-BLUEPRINT.md
```

**Build execution manifest:**
```markdown
## Phase {N} Execution Manifest

### Plans Discovered
| Plan | Name | Breath | Dependencies | Status |
|------|------|------|--------------|--------|
| {N}-01 | {name} | 1 | none | pending |
| {N}-02 | {name} | 1 | none | pending |
| {N}-03 | {name} | 2 | {N}-01 | pending |
```

### Step 3: Group by Breath (Dominion Flow Standard)

**Breath Grouping Rules:**
- Plans in same breath execute in parallel
- Breath N+1 waits for Breath N to complete
- Dependencies must be in earlier breaths

**Display:**
```
â—† Execution Plan
  Breath 1: 2 plans (parallel)
    â”œâ”€ {N}-01: {name}
    â””â”€ {N}-02: {name}
  Breath 2: 1 plan
    â””â”€ {N}-03: {name} (depends on {N}-01)
```

### Step 3.5: Path Verification Gate (MANDATORY — v5.0)

**Research basis:** SDFT (MIT, 2026) — recovery from own errors > memorizing expert paths.
**Trigger:** The wrong-repo incident (subagent explored `my-other-project` instead of `MY-PROJECT`).

**Before ANY file operation, verify these HARD GATES (no confidence override):**

```
PATH VERIFICATION — ALWAYS RUN (not confidence-gated)

1. WORKING DIRECTORY CHECK
   expected_project = extract from CONSCIENCE.md or VISION.md
   actual_cwd = pwd
   IF actual_cwd does NOT contain expected_project path:
     → HARD STOP. Display:
       "WRONG DIRECTORY: Expected {expected}, got {actual_cwd}"
       "Aborting to prevent cross-project contamination."

2. SUBAGENT PATH INJECTION
   When spawning ANY subagent (Task tool), ALWAYS include:
     <path_constraint>
     MANDATORY: All file operations MUST be within:
       {project_root_path}

     VERIFY before every Read/Write/Edit/Bash:
       - File path starts with {project_root_path}
       - No ../../ escapes above project root
       - Bash commands operate on correct directory

     If you find yourself in the wrong directory: STOP immediately.
     Do NOT read, edit, or delete files outside the project.
     </path_constraint>

3. DELETION SAFETY
   Before deleting files, verify:
     - File path is within project root (absolute path check)
     - File is not in the "keep" list (shared services, core files)
     - Count matches: planned deletions == actual files found
     - If count mismatch: STOP and report discrepancy
       (e.g., "Plan says 28, found 27 — investigate missing file")

4. CROSS-PROJECT CONTAMINATION CHECK
   If multiple working directories exist in session:
     - Explicitly name the TARGET project in every tool call
     - Never use relative paths that could resolve to wrong project
     - Log which project each operation targets
```

**Why this is mandatory (not confidence-gated):**
Confidence gates allow override at HIGH confidence. Path verification does NOT.
A subagent editing the wrong repo at 95% confidence is still catastrophic.
This gate is a circuit breaker, not a confidence check.

### Step 3.6: Select Execution Mode (Automatic)

**For each breath, automatically determine execution strategy.**

See `@references/execution-mode-intelligence.md` for full algorithm.

```
FOR each breath:
  plans_in_wave = plans with matching breath number
  file_sets = [plan.files_modified for each plan]

  IF plans_in_wave.count == 1:
    MODE = SEQUENTIAL

  ELIF plans_in_wave.count >= 3 AND no file overlap between plans:
    MODE = SWARM
    Compose team: Backend/Frontend/Test specialists based on file patterns

  ELIF plans_in_wave.count >= 2 AND no file overlap:
    MODE = SUBAGENT (Task tool parallelism)

  ELIF plans_in_wave.count >= 2 AND file overlap detected:
    MODE = SEQUENTIAL (serialize to avoid conflicts)

  ELSE:
    MODE = SEQUENTIAL (safe default)
```

**Display mode decision:**
```
+---------------------------------------------------------------+
|  EXECUTION MODE: [SWARM/SUBAGENT/SEQUENTIAL]                  |
+---------------------------------------------------------------+
|  Breath {W}: {N} plans                                           |
|  File overlap: [None/Detected]                                 |
|  Rationale: [why this mode was selected]                       |
|                                                                 |
|  [If SWARM:]                                                   |
|  Team composition:                                             |
|    Backend Agent:  Plan {N}-01 (API work)                      |
|    Frontend Agent: Plan {N}-02 (UI work)                       |
|    Test Agent:     Plan {N}-03 (test work)                     |
+-----------------------------------------------------------------+
```

**Override flags:** `--swarm`, `--sequential`, or `--subagent` force a specific mode.

**Fallback chain:** SWARM -> SUBAGENT -> SEQUENTIAL (if higher mode unavailable or fails).

### Step 3.7: Git Worktree Isolation (v10.0 — Optional)

> **Research basis (v10.0):** Cursor's worktree isolation pattern (2025-2026) — parallel agents
> working in isolated git worktrees prevent file conflicts without coordination overhead.
> Google/MIT Scaling Laws (Dec 2025) confirm: isolation removes the 39-70% degradation from
> shared-state contention in parallelizable tasks.

**When `--worktree` flag is set OR execution mode is SWARM/SUBAGENT:**

```
FOR each parallel agent in breath:
  # Create isolated worktree
  branch_name = "fire-execute/{plan_id}"
  worktree_path = ".claude/worktrees/{plan_id}"

  git worktree add -b {branch_name} {worktree_path} HEAD

  # Agent works in isolated copy
  agent.working_directory = {worktree_path}
  agent.path_constraint = {worktree_path}

AFTER all agents in breath complete:
  # Merge worktree branches back to main
  FOR each completed worktree:
    git merge --no-ff {branch_name}

    IF merge conflict:
      → Log conflict files
      → Attempt auto-resolution (accept both sides for additive changes)
      → If unresolvable: flag for human review

    # Clean up
    git worktree remove {worktree_path}
    git branch -d {branch_name}
```

**Benefits over shared-state coordination:**
- Zero file conflicts between parallel agents (each has own copy)
- No `.shared-state.json` needed — git merge handles integration
- Atomic: if one agent fails, its worktree is discarded without affecting others
- Rollback: `git worktree remove` cleanly reverts any agent's work

**When NOT to use worktrees:**
- SEQUENTIAL mode (no parallelism needed)
- Single-plan breaths (no contention possible)
- Tasks that need to see each other's changes in real-time

### Inter-Agent Coordination (SWARM mode)

When running in SWARM mode, agents coordinate via `.planning/.shared-state.json`:

- **Before creating new types/interfaces/exports,** check if another agent already created it by reading `.planning/.shared-state.json`. Duplicate type definitions across agents cause merge conflicts.
- **Append discoveries** to the shared state file using atomic writes. Each agent writes its own key (e.g., `"backend": { "exports": [...] }`).
- **If a file conflict is detected** (two agents modified the same file), PAUSE and log a coordination request in the shared state: `"conflicts": [{ "file": "...", "agents": ["backend", "frontend"] }]`.
- **The Team Lead periodically checks** shared state and resolves conflicts by assigning the contested file to a single agent.

```json
// .planning/.shared-state.json example
{
  "backend": {
    "exports": ["UserService", "AuthMiddleware"],
    "files_modified": ["src/services/user.ts", "src/middleware/auth.ts"]
  },
  "frontend": {
    "exports": ["UserContext", "LoginForm"],
    "files_modified": ["src/contexts/user.tsx", "src/components/LoginForm.tsx"]
  },
  "conflicts": []
}
```

### Reasoning Trace Sharing (MAKER v9.1)

> **Research basis:** MAKER (2025) — Multi-Agent Knowledge Exchange and Reasoning.
> Agents sharing intermediate reasoning (not just outputs) produce better coordinated results.

In SWARM mode, agents write reasoning traces to shared state so other agents can build on their decisions.

**Extended shared-state.json structure:**

```json
{
  "backend": {
    "exports": ["UserService", "AuthMiddleware"],
    "files_modified": ["src/services/user.ts"],
    "reasoning": [
      { "step": "Chose connection pooling over per-request", "why": "10+ concurrent queries expected", "confidence": 85 },
      { "step": "Added index on user_id", "why": "JOIN was full table scan", "confidence": 95 }
    ]
  },
  "frontend": {
    "exports": ["UserContext"],
    "files_modified": ["src/contexts/user.tsx"],
    "reasoning": [
      { "step": "Used React Query over useState+useEffect", "why": "Backend noted 10+ concurrent queries — caching prevents redundant fetches", "confidence": 90 }
    ]
  }
}
```

**Add to SWARM executor prompt:**

```
<shared_reasoning>
Before making architectural decisions, READ .planning/.shared-state.json for reasoning
from other agents. Your decisions should be informed by their context.

After each significant decision, APPEND to your reasoning array:
{ "step": "what you decided", "why": "rationale", "confidence": N }

Focus on decisions that OTHER agents would benefit from knowing about —
API contracts, data shapes, library choices, performance trade-offs.
</shared_reasoning>
```

### Architect/Editor Model Split (v10.0)

> **Research basis (v10.0):** Aider's dual-model architecture (2025-2026) — strong model
> plans changes as a structured diff spec, fast model applies them. Achieves 85% on
> SWE-bench by separating reasoning from execution. Anthropic's own model tiering
> (Opus/Sonnet/Haiku) makes this practical without additional API setup.

**When `--model-split` flag is set OR task difficulty is COMPLEX:**

```
ARCHITECT PHASE (Opus — strong reasoning):
  Input:  BLUEPRINT.md task description + relevant source files
  Output: Structured change specification:

  ## Change Spec for Task {N}
  ### File: {path}
  - Action: CREATE | MODIFY | DELETE
  - Location: line {N} (for MODIFY)
  - Change: {description of what to change and why}
  - New code sketch: {pseudocode or key logic}
  ### Dependencies: {files that must exist first}
  ### Verification: {how to confirm the change works}

EDITOR PHASE (Haiku — fast execution):
  Input:  Change spec from Architect + source files
  Output: Actual file edits using Edit/Write tools

  Rules for Editor:
  - Follow change spec EXACTLY — do not deviate
  - If spec is ambiguous: ask Architect (not user)
  - If spec is impossible: report back with reason
  - Apply code comments standard v3.2 to all changes
```

**Model routing by difficulty (automatic):**

| Difficulty | Architect | Editor | Rationale |
|-----------|-----------|--------|-----------|
| SIMPLE | skip | Haiku | No planning needed, direct edit |
| MODERATE | Sonnet | Haiku | Balance of reasoning + speed |
| COMPLEX | Opus | Sonnet | Maximum reasoning + reliable execution |

**Cost savings:** ~60% of tasks are SIMPLE (Haiku only). MODERATE tasks use Sonnet+Haiku
instead of Opus for everything. Only COMPLEX tasks use full Opus reasoning.

**Override:** `--model-split` forces architect/editor for all tasks regardless of difficulty.

### Task-Level Resume

When resuming with `--continue`, read RECORD.md for the current plan:

- **Skip tasks already marked as completed** -- verify artifacts still exist via `git log` and file existence checks before skipping.
- **Start execution from the first incomplete task** in the current breath.
- **Do NOT re-execute completed tasks** to avoid duplicate commits, redundant file modifications, and wasted context.

```
IF --continue flag is set:
  1. Read .planning/phases/{N}-{name}/{N}-{NN}-RECORD.md for each plan
  2. For each plan with existing RECORD.md:
     - Parse completed tasks from the "Accomplishments" section
     - Verify key_files.created still exist on disk
     - Verify commits exist in git log
     - IF all verified → mark plan as COMPLETE, skip execution
     - IF artifacts missing → mark plan as INCOMPLETE, re-execute
  3. For plans without RECORD.md → execute normally
  4. Resume from the first incomplete breath
```

### Step 4: Execute Breath (Enhanced with WARRIOR + Mode Intelligence)

For each breath, execute using the selected mode:

```
â”â”â” DOMINION FLOW â–º BREATH {W} EXECUTION ({MODE}) â”â”â”
```

**MODE = SWARM:**
```
Team Lead delegates to specialist teammates:
  "Execute Breath {W} as a team.
   - Backend Agent: Plan {N}-01 (@BLUEPRINT.md)
   - Frontend Agent: Plan {N}-02 (@BLUEPRINT.md)
   - Test Agent: Plan {N}-03 (@BLUEPRINT.md)
   Each agent: atomic commits per task, create RECORD.md"
```

**MODE = SUBAGENT:**
```
â—† Spawning executors for Breath {W}...
  âš¡ fire-executor: Plan {N}-01 - {description}
  âš¡ fire-executor: Plan {N}-02 - {description}
```

**MODE = SEQUENTIAL:**
```
â—† Executing Breath {W} sequentially...
  â†’ Plan {N}-01: {description} (executing...)
  [complete]
  â†’ Plan {N}-02: {description} (executing...)
```

**Spawn fire-executor per plan (parallel for SUBAGENT/SWARM):**

```
â—† Spawning executors for Breath {W}...
  âš¡ fire-executor: Plan {N}-01 - {description}
  âš¡ fire-executor: Plan {N}-02 - {description}
```

### Step 5: fire-executor Agent Behavior

Each fire-executor receives:

**Context Injection:**
```markdown
<plan_context>
@.planning/phases/{N}-{name}/{N}-{NN}-BLUEPRINT.md
</plan_context>

<skills_context>
Skills to apply for this plan:
@skills-library/{category}/{skill-1}.md
@skills-library/{category}/{skill-2}.md

Apply these patterns during implementation.
Document which skills you actually used.
</skills_context>

<honesty_protocol>
While executing tasks:

**If uncertain:**
1. Document the uncertainty
2. Search skills library for guidance
3. Research if needed
4. Proceed with transparency

**If blocked:**
1. Admit the blocker explicitly
2. Document what's blocking
3. Request help or create .continue-here.md
4. Don't fake progress

**If assuming:**
1. Document the assumption
2. Mark as assumption in code comments
3. Add to handoff Issues section
</honesty_protocol>

<kv_cache_strategy>
<!-- v10.0: KV-Cache-Aware Context Management -->
<!-- Research basis: Production patterns from Manus AI, Cursor, Devin -->
<!-- Key insight: KV-cache hit rates collapse when context prefix changes -->

**Context Ordering Rule:** Place STABLE context first, DYNAMIC context last.
The KV-cache reuses computation for unchanged prefix tokens.

1. System prompt + project rules     (STABLE — never changes mid-execution)
2. Plan context + skills loaded      (SEMI-STABLE — changes between plans only)
3. Episodic recall + confidence      (DYNAMIC — changes per task)
4. Current task instructions         (DYNAMIC — changes every call)

**Re-injection Strategy:**
- When switching between plans in SWARM mode, re-inject stable prefix unchanged
- Only append/replace the dynamic tail — this preserves KV-cache across tasks
- Avoid re-ordering context blocks between executor calls
- If context exceeds 80% of window, compress episodic recall first (it has lowest reuse value)
</kv_cache_strategy>

<episodic_recall>
<!-- v6.0: CoALA Per-Turn Episodic Auto-Injection -->
<!-- Past experiences relevant to this plan's tasks -->
<!-- Retrieved via: npm run search -- "{plan keywords}" --limit 3 --two-phase -->

{For each relevant memory with score > 0.7:}
**[{sourceType}] {title}** (score: {score}, utility: {utilityScore})
{text excerpt — first 300 chars}
Source: {sourceFile} | Date: {date}

<!-- If no relevant memories found, this block is omitted -->
</episodic_recall>

<confidence_gates>
<!-- v5.0: Confidence-Gated Execution (SAUP-inspired) -->

Before each plan task, estimate confidence:

**Confidence Signals:**
  + Matching skill found in library: +20
  + Similar reflection exists: +15
  + Tests available to verify: +25
  + Familiar technology/framework: +15
  + Clear, unambiguous requirements: +15
  - Unfamiliar framework/library: -20
  - No tests available: -15
  - Ambiguous/incomplete requirements: -20
  - Security-sensitive change: -10
  - Destructive operation (delete, drop, overwrite): -15

**Confidence Levels:**

HIGH (>80%): Proceed autonomously
  → Execute task directly
  → Run Self-Judge after

MEDIUM (50-80%): Proceed with extra validation
  → Search reflections: /fire-remember "{task description}" --type reflection
  → Search skills: /fire-search "{technology}"
  → Run Self-Judge before AND after
  → Log uncertainty reason in RECORD.md

LOW (<50%): Research first, then proceed
  → Search Context7 for current library docs
  → Search skills library: /fire-search "{gap}"
  → Check if this is outside trained domain
  → IF < 30%: Spawn fire-researcher with the specific gap — get alternatives
  → Only escalate to user if research returns no actionable path
  → Create checkpoint before attempting

**Log confidence in RECORD.md:**
```yaml
confidence_log:
  - task: 1
    score: 85
    level: HIGH
    signals: [skill_match, tests_available, familiar_tech]
  - task: 3
    score: 45
    level: LOW
    signals: [unfamiliar_framework, no_tests, ambiguous_requirements]
    action: "Asked user for clarification on WebSocket auth approach"
```
</confidence_gates>
```

### Step 5.1: Populate Episodic Recall (v6.0 — CoALA)

> **Research basis:** CoALA (Berkeley 2024) — Every decision cycle requires episodic memory injection.

Before spawning executors, the orchestrator populates the `<episodic_recall>` block:

```
# 1. Extract keywords from plan tasks
plan_keywords = extract_keywords(BLUEPRINT.md task descriptions)

# 2. Search vector memory with two-phase retrieval
cd ~/.claude/memory
results = npm run search -- "{plan_keywords}" --limit 3 --two-phase

# 3. Fill <episodic_recall> block in executor prompt
IF results exist AND top_result.score > 0.7:
  Fill block with top 3 results (title, score, utility, text excerpt)
ELSE:
  Remove <episodic_recall> block entirely (no noise for novel tasks)
```

**Cost control:** Only inject memories with score > 0.7. Cap at 3 results (~500 tokens).

---

**Executor Creates:**
1. Implements all tasks from BLUEPRINT.md
2. **Runs Quick Self-Judge after each task** (v5.0 — Agent-as-Judge)
3. Runs verification commands for each task
4. Creates `{N}-{NN}-RECORD.md` (fire-handoff.md format)
5. Updates SKILLS-INDEX.md with skills applied

### Step 5.5: Quick Self-Judge (v5.0 — Agent-as-Judge)

**Research basis:** Agent-as-Judge (2025) — 95% error recovery when self-evaluation present

After completing each task in a plan, pause for 30 seconds of self-critique:

```markdown
## Quick Self-Judge (before marking task complete)
1. Does this change do what the plan asked? [Y/N]
2. Could this break something that was working? [Y/N — if Y, what?]
3. Am I confident this is correct, or am I guessing? [confident/uncertain]
4. Did I check for the obvious: imports, types, null cases? [Y/N]
5. Would I approve this in a code review? [Y/N]

IF any N or "uncertain":
  → STOP. Re-examine before proceeding.
  → Document what triggered the pause.

IF "uncertain":
  → Log to ~/.claude/reflections/{date}_uncertain-{task-slug}.md
  → Include: what made you uncertain, what you checked, what you decided
  → trigger: "self-judge-uncertain"
```

**This is NOT a full verification.** It's a 30-second gut check that catches:
- Wrong file edited
- Missing import after refactor
- Accidentally deleted working code
- Copying a pattern that doesn't apply here

**When to skip:** Trivial changes (typo fix, comment update, config value change)

### Step 5.6: Call-Path Verification — Dead Code Prevention (v11.0)

> **Research basis (v11.0):** Failure pattern mining (6+ instances across v10-v12) —
> features declared, committed, and documented but never wired. Examples: findSimilar()
> declared but never called, parentId field added but never populated. The fix: verify
> every new function/export has at least one call site before marking task complete.

After each task that creates new functions, exports, or API endpoints:

```
FOR each new_symbol created in this task:
  call_sites = grep -r "{symbol_name}" src/ --include="*.ts" --include="*.tsx" | grep -v "export\|function\|const.*="

  IF call_sites == 0:
    FLAG: "DEAD CODE: {symbol_name} declared in {file} but never called"
    ACTION: Wire it into the appropriate caller before proceeding

  IF call_sites == 1 AND call_site is only the test file:
    NOTE: "Only called from tests — verify production code path exists"
```

**Skip condition:** Pure type definitions, interfaces, and configuration constants
(these are consumed implicitly by the type system, not called directly).

### Step 6: Create fire-handoff.md (Unified Format)

Each executor creates a summary using the unified format:

```markdown
---
# Dominion Flow Frontmatter
phase: {N}-{name}
plan: NN
subsystem: {category}
duration: "{X} min"
start_time: "{ISO timestamp}"
end_time: "{ISO timestamp}"

# Skills & Quality (WARRIOR)
skills_applied:
  - "{category}/{skill}"
honesty_checkpoints:
  - task: {N}
    gap: "{what was uncertain}"
    action: "{how it was resolved}"
validation_score: {X}/70

# Dominion Flow Execution Metadata
requires: [dependencies]
provides: [what this creates]
key_files:
  created: [list]
  modified: [list]
key_decisions:
  - "{decision made during execution}"
---

# Power Handoff: Plan {N}-{NN}

## Quick Summary
{One paragraph of what was accomplished}

## Dominion Flow Accomplishments
{Task commits, files created/modified, decisions}

## Skills Applied (WARRIOR)
{Which skills were used and how}

## WARRIOR 7-Step Handoff
{W-A-R-R-I-O-R sections}
```

### Step 7: Wait for Breath Completion (Dominion Flow Standard)

```
â—† Breath {W} in progress...
  â”œâ”€ âš¡ Plan {N}-01: Running (backend)
  â””â”€ âš¡ Plan {N}-02: Running (frontend)

[After completion]

âœ“ Breath {W} complete
  â”œâ”€ âœ“ Plan {N}-01: Complete (12 min)
  â””â”€ âœ“ Plan {N}-02: Complete (8 min)
```

**Breath Completion Checks:**
- All executors finished
- All RECORD.md files created
- No blocking errors

**If Blocking Error:**
- Create `.continue-here.md` with context
- Pause execution
- Display error and recovery instructions

### Step 7.1: Error Classification Health Check (v10.1)

> **Research basis (v10.1):** Microsoft "AutoGen StateFlow" (ICML 2024) — formal error
> classification at execution boundaries reduces repeat failures by 28%. This integrates
> the existing `references/error-classification.md` into breath-level execution flow.
> Previously, error classification existed as a reference but was not wired into
> the execution pipeline.

**After each breath completes (success OR failure), classify execution health:**

```
INPUTS for classification:
  - files_changed:   count of files in breath RECORD.md key_files
  - error_hash:      normalized hash of any error message from breath
  - previous_errors: error hashes from previous breaths in this phase
  - output_volume:   total lines of code produced vs. baseline
  - error_type:      classification of error (if any)

CLASSIFY using references/error-classification.md algorithm:

  1. BLOCKED?  → External dependency, permission, or service error
     Action: Stop execution. Create BLOCKERS.md entry. Save state.
     Display: EXECUTION BLOCKED banner (see error-classification.md)

  2. SPINNING? → Same error hash seen in 3+ breaths
     Action: Force approach rotation. Inject anti-patterns list.
     Display: "Same error for {N} breaths. You MUST try a different approach."

  3. DEGRADED? → Output volume declined 50%+ from first breath
     Action: Trigger /fire-cost context check. If ORANGE+, compact.
     Display: "Output quality declining. Consider /fire-5-handoff."

  4. STALLED?  → No file changes AND no new errors
     Action: Inject urgency. Search skills for alternative approach.
     Display: "No progress detected. Pick ONE concrete change."

  5. PROGRESS  → Files changed, errors are new/different
     Action: Continue to next breath normally.

RECORD health state in CONSCIENCE.md:
  | Breath | Health | Trigger | Action |
  | {W} | {state} | {trigger} | {action_taken} |
```

**Circuit breaker integration:**
- If health is SPINNING for 2 consecutive breaths → trigger circuit breaker
- If health is DEGRADED → check `/fire-cost` context tier. If RED+, force handoff.
- If health is BLOCKED → do NOT retry. Save state and surface blocker to user.

**Skip condition:** If breath completed successfully with no errors, mark PROGRESS and continue.

### Step 7.4: Post-Feature Config Sync (v10.0)

After breath completion, check if new features need config file updates.

**Trigger conditions:**
- Breath created new feature with `enabled` toggle
- Breath added new config keys referenced in DEFAULT_CONFIG but not in user config
- Breath created settings UI that references config paths

**Actions:**
1. Detect config files in project (*.yaml, *.json, *.toml)
2. If deep_merge/defaults pattern detected:
   - Load config through app's config loader
   - Save back to disk (writes merged defaults)
   - Log: `"Config synced: {file} now includes {N} new feature sections"`
3. If settings dialog exists:
   - Verify all new features appear in GUI widget list
   - Log: `"Settings dialog covers {N}/{M} features"`

**If no config pattern detected:** Skip silently.

### Step 7.5: Versioned Context Checkpoint (v6.0 — GCC)

> **Research basis:** GCC (Jul 2025) — Git-style versioned context management.
> Achieved 48% on SWE-Bench-Lite. Agents spontaneously adopted disciplined behaviors
> when they knew they could checkpoint and rollback.

After each breath completes successfully, create a checkpoint commit:

```
IF breath completed without blocking errors:

  # 1. Stage all modified files from this breath
  git add {files from breath RECORD.md frontmatter: key_files.created + key_files.modified}

  # 2. Create checkpoint commit
  git commit -m "checkpoint: phase {N} breath {W} complete — {summary}

  Files: {count} modified, {count} created
  Plans: {list of plan IDs completed in this breath}
  Dominion Flow v6.0 checkpoint"

  # 3. Record checkpoint hash
  checkpoint_hash = git rev-parse HEAD

  # 4. Update CONSCIENCE.md with checkpoint
  Append to CONSCIENCE.md under ## Checkpoints:
    | Breath | Commit | Date | Plans | Status |
    | {W} | {checkpoint_hash:7} | {date} | {plan IDs} | Complete |

  Display:
  "Checkpoint: {checkpoint_hash:7} — Breath {W} complete ({plans count} plans)"

IF breath FAILED and checkpoint exists:
  # Offer rollback option
  Display:
  "Breath {W} failed. Last checkpoint: {last_checkpoint_hash:7}
   To rollback: git reset --hard {last_checkpoint_hash}
   To continue: fix blocking error and re-run"
```

**Note:** Only commit files tracked by the plan. Never auto-commit .env, credentials, or
files not in the BLUEPRINT.md scope. This is a lightweight GCC adaptation, not full branching.

---

### Step 7.6: Classify Review Depth (v8.0)

Determine review depth from phase scope:

```
total_files = count of all key_files.created + key_files.modified across SUMMARYs
has_security = any file in auth/, security/, middleware/, crypto/
has_cross_cutting = files span 3+ top-level directories

IF total_files <= 3 AND NOT has_security:
  review_depth = "shallow"  → 5 personas (Simplicity + Security + Perf + Test + Pattern)
ELIF total_files >= 10 OR has_security OR has_cross_cutting:
  review_depth = "deep"  → 16 personas + cross-file analysis
ELSE:
  review_depth = "normal"  → 16 personas
```

---

### Step 7.7: Mandatory Skill Extraction (v10.0)

After each phase completes, automatically evaluate whether the build produced
reusable patterns worth capturing as skills.

**This step is MANDATORY after every build phase.** It runs the skill creation
wizard in auto-detection mode with duplicate checking.

```
# 1. Analyze what was built in this phase
built_files = all key_files.created from phase SUMMARYs
built_patterns = extract_patterns(built_files)
  Patterns to detect:
  - Config-driven feature toggles (togglable pipeline)
  - Settings dialogs generated from config
  - Thread-safety patterns (cross-thread marshaling)
  - API route patterns (CRUD, auth, middleware)
  - Component hierarchies (parent→child wiring)
  - Build/deploy configurations
  - Error handling strategies
  - Data migration patterns

# 2. Check for duplicates against existing skills
FOR each detected pattern:
  /fire-search "{pattern keywords}" --scope general
  IF similarity > 80%:
    Log: "Skill already exists: {existing_skill_name} (skip)"
    CONTINUE
  ELIF similarity > 50%:
    Log: "Similar skill found: {existing_skill_name} — consider updating"
    # Offer to update existing skill with new insights
  ELSE:
    # New pattern — queue for skill creation

# 3. Create skills for novel patterns
IF new_patterns.length > 0:
  Display:
  "◆ Skill extraction found {N} new patterns:
    ├─ {pattern_1_name} (no existing match)
    ├─ {pattern_2_name} (partial match — update candidate)
    └─ ...

   Auto-create skills? [Yes / No / Review each]"

  IF Yes (default in autonomous mode):
    FOR each new_pattern:
      /fire-add-new-skill --from session --quick
      # Uses --quick flag for minimal prompts
      # Security scan + credential filter still run (Steps 4.5, 4.6)

  IF No:
    Log: "Skill extraction skipped by user. Patterns noted in autonomous-log.md"

# 4. Log results
Append to .planning/autonomous-log.md:
  ## Skill Extraction — Phase {N}
  Patterns detected: {count}
  New skills created: {count}
  Duplicates skipped: {count}
  Updates suggested: {count}
```

**In autonomous mode:** Skills are auto-created (Yes is default). The security
scan and credential filter gates in `/fire-add-new-skill` (Steps 4.5, 4.6)
still run to prevent malicious or leaked content.

**In manual mode:** User is prompted for each pattern.

---

### Step 8: Spawn Parallel Verification + Review (v8.0)

After all breaths complete, spawn BOTH agents simultaneously:

```
IF --skip-review NOT set:

  â—† Spawning parallel verification + review for Phase {N}...
    â"œâ"€ fire-verifier: 70-point WARRIOR validation
    â""â"€ fire-reviewer: {review_depth} review (Simplicity + 15 personas)

  # Spawn fire-verifier (existing â€" unchanged)
  Task(subagent_type="fire-verifier", prompt="""
    Phase: {N}, Plans: {list}, Must-Haves: {count}
    @references/validation-checklist.md
  """)

  # Spawn fire-reviewer (NEW â€" v8.0)
  Task(subagent_type="fire-reviewer", prompt="""
    <review_scope>
    Phase: {N} - {name}
    Review Depth: {review_depth}
    </review_scope>

    <files_to_review>
    {all key_files.created + key_files.modified from RECORD.md files}
    </files_to_review>

    <plan_intent>
    {Quick Summary from each RECORD.md â€" what was INTENDED vs what was built}
    </plan_intent>

    <simplicity_mandate>
    STRICT: Flag over-engineering as HIGH.
    Three similar lines > premature abstraction.
    Direct approach > clever approach.
    If a junior dev can't read it in 30 seconds â†' too complex.
    </simplicity_mandate>

    Output to: .planning/phases/{N}-{name}/{N}-REVIEW.md
  """)

ELSE:
  # Only verifier (legacy behavior â€" --skip-review was passed)
  â—† Spawning fire-verifier for Phase {N}... (review skipped)
  Task(subagent_type="fire-verifier", prompt="""
    Phase: {N}, Plans: {list}, Must-Haves: {count}
    @references/validation-checklist.md
  """)
```

**Route based on verifier result (when review skipped):**
- **PASS:** Proceed to Step 9
- **FAIL with gaps:** Create gap closure plan, route to `/fire-2-plan {N} --gaps`

### Step 8.5: Merge Gate â€" Combined Quality Decision (v8.0)

Wait for BOTH agents to complete, then evaluate combined verdict.

**Autonomous Mode Routing (v9.0):**

```
IF --autonomous flag is set:

  IF combined_verdict == "READY FOR HUMAN":
    Log to autonomous-log: "Merge gate: READY FOR HUMAN (auto-proceeding)"
    → Skip display, continue to Step 9 (CONSCIENCE.md update)

  IF combined_verdict contains "FIX":
    Log to autonomous-log: "Merge gate: FIX required (auto-routing to fix cycle)"
    → Route to gap closure automatically (no Options display)

  // Non-autonomous mode: fall through to standard display below
```

**COMBINED VERDICT MATRIX:**

| Verifier â†" / Reviewer â†' | APPROVE | APPROVE W/ FIXES | BLOCK |
|--------------------------|---------|------------------|-------|
| APPROVED                 | READY FOR HUMAN | FIX REVIEW FINDINGS | FIX BLOCKERS |
| CONDITIONAL              | FIX VERIFIER GAPS | FIX BOTH | FIX BOTH |
| REJECTED                 | FIX VERIFIER | FIX BOTH | FIX BOTH (critical) |

**RULE:** The stricter verdict ALWAYS wins.

**DISAGREEMENT HANDLING:**

```
Verifier APPROVED + Reviewer BLOCK:
  "Code passes tests but has quality/simplicity issues.
   FIX BEFORE HUMAN TESTING."
  (This is the MOST VALUABLE case â€" why redundancy exists)

Verifier REJECTED + Reviewer APPROVE:
  "Code is clean but doesn't work. Fix functional failures first."
```

**Display combined result:**

```
â•"â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•'  MERGE GATE â€" Phase {N}                                                    â•'
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•'                                                                            â•'
â•'  Verifier:  {X}/70 â€" {APPROVED/CONDITIONAL/REJECTED}                       â•'
â•'  Reviewer:  {verdict} â€" {critical}C / {high}H / {medium}M / {low}L        â•'
â•'  Simplicity: {N} over-engineering flags                                    â•'
â•'                                                                            â•'
â•'  Combined Verdict: {READY FOR HUMAN / FIX REVIEW FINDINGS / FIX BOTH}     â•'
â•'                                                                            â•'
â•'  {If FIX needed:}                                                          â•'
â•'  Issues to resolve:                                                        â•'
â•'    âœ— {file:line â€" description}                                             â•'
â•'    âœ— {file:line â€" description}                                             â•'
â•'                                                                            â•'
â•'  Options:                                                                  â•'
â•'    A) Fix issues                                                           â•'
â•'    B) Override with known issues                                           â•'
â•'    C) Gap closure plan                                                     â•'
â•'                                                                            â•'
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

**FEEDBACK LOOP (Behavioral Directive Proposals):**

```
IF reviewer found CRITICAL or HIGH findings:
  For each finding with severity >= HIGH:
    Add proposed behavioral directive:
      IF: {condition from finding}
      DONT: {the anti-pattern or over-engineering found}
      BECAUSE: {reviewer explanation}
      Source: fire-reviewer Phase {N} | Confidence: 1/5
```

**VERSION PERFORMANCE TRACKING (v8.0):**

```
After gate verdict is displayed and user responds:

  Record outcome to .planning/version-performance.md:

  | Date | Version | Gate | Verdict | Override? | Outcome | Notes |
  | {now} | v8.0 | merge | {verdict} | {A=no, B=yes} | pending | Phase {N} |

  "Override?" = yes if user chose option B (override with known issues)
  "Outcome" = filled retroactively after human testing (correct/false-positive/false-negative)

  AFTER 5+ records exist, check degradation signals:
    - override_rate > 40% → rules too strict, suggest rollback
    - false_positive_rate > 30% → gate crying wolf, retire offending rule
    - Same rule overridden 3+ times → retire that specific rule
  See: references/behavioral-directives.md § Version Performance Registry
```

### Step 8.75: Auto-Route Merge Gate (v10.0 — Default Autonomous)

By default (v10.0), execution auto-routes based on combined_verdict without human pause:

```
IF combined_verdict in ["APPROVED", "APPROVE"]:
  → Auto-advance to next breath. No human pause.
  → Log: "Auto-routed: {verdict} (score {N}/70)"

IF combined_verdict in ["CONDITIONAL", "APPROVE WITH FIXES"]:
  → Auto-advance but log gaps to .planning/autonomous-notes.md
  → Log: "Auto-routed with notes: {N} non-critical gaps"

IF combined_verdict in ["REJECTED", "BLOCK"]:
  → STOP. Display blocker. Request human intervention.
  → This is the ONLY case where execution pauses.

IF --manual flag is set:
  → Revert to v9.0 behavior: display all checkpoints, wait for human.
```

**Safety gates ALWAYS active regardless of mode:**
  - Path verification (MANDATORY — cannot disable)
  - HAC enforcement (confidence 5/5 rules)
  - Circuit breaker (stall/spin/degrade detect)
  - Power-verifier (70-point WARRIOR validation)
  - Power-reviewer (16-persona code review)

### Step 9: Update CONSCIENCE.md and SKILLS-INDEX.md

**CONSCIENCE.md Updates:**
```markdown
## Current Position
- Phase: {N} of {total}
- Status: Complete (or Verified with gaps)
- Last activity: {timestamp} - Phase {N} execution complete

## WARRIOR Integration
- Skills Applied: {new_total} total
  - {skill-1} (Phase {N}, Plan {NN})
  - {skill-2} (Phase {N}, Plan {NN})
- Honesty Checkpoints: {count}
- Validation Status: Phase {N} passed {X}/70 checks
- Code Review: Phase {N} {reviewer_verdict} ({critical}/{high}/{medium}/{low})
- Combined Gate: {combined_verdict}
- Simplicity Findings: {count of Simplicity Guardian findings}
```

**SKILLS-INDEX.md Updates:**
```markdown
## By Phase

### Phase {N}: {name}
**Plan {N}-01:**
- {category}/{skill-1}
- {category}/{skill-2}

**Plan {N}-02:**
- {category}/{skill-3}
```

---

## Agent Spawning Instructions

### fire-executor (Parallel per Plan)

**Agent File:** `@agents/fire-executor.md`

**Spawn Pattern:**
```
For each plan in breath:
  Spawn fire-executor with:
    - Plan file context
    - Skills library context
    - Honesty protocol reminder
```

**Executor Outputs:**
- Task implementations
- `{N}-{NN}-RECORD.md` (fire-handoff format)
- SKILLS-INDEX.md updates

### fire-verifier (After All Breaths)

**Agent File:** `@agents/fire-verifier.md`

**Context:**
```markdown
Phase: {N} - {name}
Plans Executed: {list}
Must-Haves: {aggregated from all plans}
WARRIOR Validation: {checklist}
```

**Verifier Outputs:**
- `{N}-VERIFICATION.md`
- Gap analysis (if any)

### fire-reviewer (Parallel with Verifier — v8.0)

**Agent File:** `@agents/fire-reviewer.md`

**Context:**
```markdown
<review_scope>
Phase: {N} - {name}
Review Depth: {shallow|normal|deep} (from Step 7.6)
</review_scope>

<files_to_review>
{All key_files.created + key_files.modified from RECORD.md files}
</files_to_review>

<plan_intent>
{Quick Summary from each RECORD.md}
</plan_intent>

<simplicity_mandate>STRICT</simplicity_mandate>
```

**Reviewer Outputs:**
- `{N}-REVIEW.md`
- Severity table (CRITICAL/HIGH/MEDIUM/LOW)
- Proposed behavioral directives for HIGH+ findings

---

## Success Criteria

### Required Outputs
- [ ] All plans in phase executed
- [ ] Quick Self-Judge run after each task (v5.0)
- [ ] All RECORD.md files created (fire-handoff format)
- [ ] All verification commands passed
- [ ] SKILLS-INDEX.md updated
- [ ] CONSCIENCE.md updated
- [ ] VERIFICATION.md created
- [ ] Must-haves verified
- [ ] Code review run in parallel with verification (v8.0)
- [ ] {N}-REVIEW.md created alongside {N}-VERIFICATION.md
- [ ] Combined quality gate evaluated — both must agree
- [ ] CRITICAL/HIGH findings fed into behavioral directives
- [ ] Simplicity Guardian findings surfaced in report

### Completion Display

```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âœ“ PHASE {N} EXECUTION COMPLETE                                               â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Phase: {N} - {name}                                                         â•‘
â•‘  Plans Executed: {count}                                                     â•‘
â•‘  Breaths: {wave_count}                                                         â•‘
â•‘  Total Time: {duration}                                                      â•‘
â•‘                                                                              â•‘
â•‘  Execution Summary:                                                          â•‘
â•‘    Breath 1:                                                                   â•‘
â•‘      âœ“ {N}-01 - {description} (12 min)                                       â•‘
â•‘      âœ“ {N}-02 - {description} (8 min)                                        â•‘
â•‘    Breath 2:                                                                   â•‘
â•‘      âœ“ {N}-03 - {description} (15 min)                                       â•‘
â•‘                                                                              â•‘
â•‘  Skills Applied: {count}                                                     â•‘
â•‘  Honesty Checkpoints: {count}                                                â•‘
â•‘  Validation: {X}/70 checks passed                                            â•‘
â•‘                                                                              â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘ NEXT UP                                                                      â•‘
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â•‘                                                                              â•‘
â•‘  â†’ Run `/fire-4-verify {N}` for detailed validation report                  â•‘
â•‘  â†’ Or run `/fire-2-plan {N+1}` to plan next phase                           â•‘
â•‘  â†’ Or run `/fire-5-handoff` to create session handoff                       â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

---

## Error Handling

### Executor Blocked

```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âš  EXECUTION BLOCKED                                                          â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Plan {N}-{NN} encountered a blocking issue:                                 â•‘
â•‘                                                                              â•‘
â•‘  Issue: {description}                                                        â•‘
â•‘  Task: {task number and description}                                         â•‘
â•‘                                                                              â•‘
â•‘  Created: .planning/phases/{N}-{name}/.continue-here.md                      â•‘
â•‘                                                                              â•‘
â•‘  Options:                                                                    â•‘
â•‘    A) Resolve issue and run `/fire-3-execute {N} --continue`                â•‘
â•‘    B) Skip this plan: `/fire-3-execute {N} --skip {N}-{NN}`                 â•‘
â•‘    C) Create handoff: `/fire-5-handoff`                                     â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

### Verification Failed

```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âš  VERIFICATION GAPS DETECTED                                                 â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Phase {N} execution complete but verification found gaps:                   â•‘
â•‘                                                                              â•‘
â•‘  Gaps:                                                                       â•‘
â•‘    âœ— Must-have: "User can paginate results" - Not verified                   â•‘
â•‘    âœ— WARRIOR: Test coverage 65% (required 80%)                               â•‘
â•‘                                                                              â•‘
â•‘  Options:                                                                    â•‘
â•‘    A) Run `/fire-2-plan {N} --gaps` to plan gap closure                     â•‘
â•‘    B) Run `/fire-4-verify {N}` for detailed report                          â•‘
â•‘    C) Accept gaps and proceed: `/fire-2-plan {N+1}`                         â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

### Breath Timeout

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ âš  WARNING: Breath Timeout                                                     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                             â”‚
â”‚  Breath {W} exceeded expected duration.                                       â”‚
â”‚                                                                             â”‚
â”‚  Status:                                                                    â”‚
â”‚    âœ“ Plan {N}-01: Complete                                                  â”‚
â”‚    â—† Plan {N}-02: Still running (45 min)                                    â”‚
â”‚                                                                             â”‚
â”‚  Action: Continuing to wait... (use Ctrl+C to interrupt)                    â”‚
â”‚                                                                             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## References

- **Agent:** `@agents/fire-executor.md` - Execution agent with honesty protocols
- **Agent:** `@agents/fire-verifier.md` - Verification agent with combined checks
- **Template:** `@templates/fire-handoff.md` - Unified summary format
- **Protocol:** `@references/honesty-protocols.md` - Execution honesty guidance
- **Protocol:** `@references/validation-checklist.md` - 70-point validation
- **Brand:** `@references/ui-brand.md` - Visual output standards
