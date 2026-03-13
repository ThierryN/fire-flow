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
  --token-efficient: "Enable ALAS context slicing for reduced token usage (~60% reduction). Default: OFF (full context for best quality). Toggle ON for budget-conscious runs or large phase counts."
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

### Step 3.55: Cross-Phase DAG Validation (v13.0)

> **Source:** turborepo `lib.rs` validate_graph (Tarjan SCC), oxc `no_cycle.rs`.
> See: `@skills-library/_general/methodology/MULTI_AGENT_COORDINATION.md` § Cross-Phase DAG Validation

**Before executing any phase, validate the phase dependency chain:**

```
1. BUILD PHASE GRAPH:
   nodes = all phases from VISION.md
   edges = phase dependencies (phase N depends on phase N-1's outputs)

2. CHECK FOR CYCLES (Tarjan's SCC from turborepo):
   FOR each pair of phases with cross-references:
     IF Phase A depends on Phase B AND Phase B depends on Phase A:
       → Report cycle: "Phase {A} → Phase {B} → Phase {A} creates a cycle."
       → Suggest cut points: "Break by removing one dependency direction."
       → STOP — do not execute with circular dependencies

3. CHECK DEPENDENCY AVAILABILITY:
   FOR current phase's dependencies:
     IF dependency phase status != "complete" in CONSCIENCE.md:
       → FLAG: "Phase {N} depends on Phase {M} which is not complete"
       → IF dependency is NOT in execution range: BLOCK with explanation
       → IF dependency IS in execution range: move dependency to earlier breath,
         rebuild breath groupings from Step 3, display revised manifest

4. VALIDATE CONTRACTS (provides/requires matching):
   IF current phase BLUEPRINT has "requires" in frontmatter:
     FOR each required item:
       Check that a previous phase's BLUEPRINT "provides" it
       IF missing:
         → FLAG: "Phase {N} requires '{item}' but no previous phase provides it"
         → This is a PLANNING gap — route back to /fire-2-plan
```

**Skip condition:** Phase 1 (no dependencies possible). Single-phase execution.

### Step 3.6: Select Execution Mode (Automatic) + Delegation Bounding (v13.0)

**For each breath, automatically determine execution strategy.**

See `@references/execution-mode-intelligence.md` for full algorithm.

> **v13.0 — Semaphore Delegation Bounding:** From turborepo `execute.rs` + mise `task_scheduler.rs`.
> Permit pool limits concurrent agent spawning to prevent depth explosion.
> See: `@skills-library/_general/methodology/MULTI_AGENT_COORDINATION.md` § Semaphore Delegation Bounding

```
# ─── v13.0: Delegation bounding (semaphore pattern) ───
max_concurrent_agents = 4  (default, configurable)

# Mode determines the semaphore limit:
#   SWARM mode:      max_concurrent_agents = min(plan_count, 4)
#   SUBAGENT mode:   max_concurrent_agents = min(plan_count, 3)
#   SEQUENTIAL mode: max_concurrent_agents = 1
#
# CRITICAL: Sub-agents spawned BY agents do NOT get separate permits.
# They share their parent's permit — this prevents depth explosion.
# An executor agent that spawns a researcher sub-agent does NOT consume
# a new permit — both run under the original executor's permit.

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
- Atomic: if one agent fails, its worktree is discarded without affecting others
- Rollback: `git worktree remove` cleanly reverts any agent's work

**Worktree + SWARM arbitration rule (v13.0):**
When `--worktree` is active AND SWARM mode is selected:
- File conflict coordination is handled by git merge (no `.shared-state.json` for file tracking)
- BUT `.agent-messages.jsonl` is STILL used for CLAIM/BLOCKED/DISCOVERY messages (append-only = safe across worktrees)
- Task ownership in `.shared-state.json` is STILL used (lives in `.planning/` which is shared, not per-worktree)
- Reasoning traces in `.shared-state.json` are STILL used (same reason)
- Only file_modified tracking moves to git merge

**When NOT to use worktrees:**
- SEQUENTIAL mode (no parallelism needed)
- Single-plan breaths (no contention possible)
- Tasks that need to see each other's changes in real-time

### Inter-Agent Coordination (SWARM mode) — v13.0 Enhanced

> **v13.0:** Enhanced with Task Ownership Protocol, Shared-State Conflict Prevention,
> Agent Communication Protocol, and Cascade Prevention from MULTI_AGENT_COORDINATION skill.
> Sources: turborepo Walker+Mutex, mise task_scheduler, lazygit AsyncHandler, biome catch_unwind, bun BundleThread+Waker.

When running in SWARM mode, agents coordinate via `.planning/.shared-state.json`:

- **Before creating new types/interfaces/exports,** check if another agent already created it by reading `.planning/.shared-state.json`. Duplicate type definitions across agents cause merge conflicts.
- **Append discoveries** to the shared state file using atomic writes. Each agent writes its own key (e.g., `"backend": { "exports": [...] }`).
- **If a file conflict is detected** (two agents modified the same file), PAUSE and log a coordination request in the shared state: `"conflicts": [{ "file": "...", "agents": ["backend", "frontend"] }]`.
- **The Team Lead periodically checks** shared state and resolves conflicts by assigning the contested file to a single agent.

#### Shared-State with Version Counter (v13.0 — Conflict Prevention)

> **Source:** turborepo Walker+Mutex, lazygit AsyncHandler ID ordering.
> See: `@skills-library/_general/methodology/MULTI_AGENT_COORDINATION.md` § Shared-State Conflict Prevention

```json
// .planning/.shared-state.json — enhanced with version counter
{
  "version": 1,
  "last_writer": null,
  "last_write_at": null,
  "tasks": {},
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

```

**Write Protocol (compare-and-swap — prevents "last writer wins" data loss):**
```
1. Read .shared-state.json → note version (e.g., 1)
2. Make changes in memory
3. Before writing: re-read file, check version still matches
   IF version changed (another agent wrote):
     → MERGE: combine your changes with theirs
     → Write with version = max(yours, theirs) + 1
   IF version same:
     → Write with version = version + 1
   Set last_writer = {agent_name}, last_write_at = now()
```

#### Task Ownership Protocol (v13.0)

> **Source:** mise `task_scheduler.rs`, turborepo `visitor/mod.rs`.
> See: `@skills-library/_general/methodology/MULTI_AGENT_COORDINATION.md` § Task Ownership Protocol

```
TASK OWNERSHIP (in .shared-state.json "tasks" key):

  "tasks": {
    "03-01-task-1": {
      "owner": "backend-agent",
      "status": "in_progress",
      "claimed_at": "2026-03-08T10:30:00Z",
      "transfer_count": 0
    }
  }

CLAIM PROTOCOL:
  1. Agent reads .shared-state.json (note version)
  2. Finds task with owner=null and status=pending
  3. Writes owner={agent_name}, status=in_progress, claimed_at=now()
  4. Uses compare-and-swap write protocol above
  5. Proceeds with task

TRANSFER RULES:
  - transfer_count tracks how many times a task changed hands
  - IF transfer_count >= 2: escalate to orchestrator (task is toxic)
  - On transfer: previous owner writes failure summary to task entry
  - Source: 17x error amplification in unstructured networks

COMPLETION:
  - Agent writes status=completed, adds summary
  - Checks for next unclaimed task
  - IF no unclaimed tasks: agent signals idle
```

#### Cascade Prevention (v13.0 — catch_unwind pattern)

> **Source:** biome `handler.rs` catch_unwind isolation.
> See: `@skills-library/_general/methodology/MULTI_AGENT_COORDINATION.md` § Error Classification

```
FOR each agent spawned in parallel (SWARM or SUBAGENT mode):
  result = catch_agent_execution(agent, task)

  MATCH result:
    OK(completed) → record success, continue
    OK(failed)    → record failure as diagnostic, continue OTHER agents
    PANIC(error)  → record panic as diagnostic, continue OTHER agents
                     Log: "Agent {name} panicked on task {N}: {error}"
                     The PANIC is captured, NOT propagated.

  CRITICAL: One agent's failure NEVER stops sibling agents.
  Each agent runs in isolation. Failures are collected and reported
  after ALL agents in the breath complete.
```

#### Agent Communication Protocol (v13.0 — JSONL Message Queue)

> **Source:** bun BundleThread+Waker, mise channel-based dispatch.
> See: `@skills-library/_general/methodology/MULTI_AGENT_COORDINATION.md` § Agent Communication Protocol

```
AGENT MESSAGE TYPES:
  CLAIM:      "I am taking ownership of task {id}"
  COMPLETE:   "Task {id} is done. Summary: {text}"
  BLOCKED:    "I cannot proceed. Reason: {text}. Need: {what}"
  DISCOVERY:  "Found something other agents should know: {text}"
  CONFLICT:   "I need to modify {file} but {other_agent} owns it"
  HANDOFF:    "Transferring task {id} to {target_agent}. Reason: {text}"

MESSAGE QUEUE (append-only file):
  .planning/.agent-messages.jsonl

  Each line is a JSON message:
  {"type":"CLAIM","agent":"backend","task":"03-01-task-1","timestamp":"..."}
  {"type":"DISCOVERY","agent":"backend","data":"API uses camelCase not snake_case","timestamp":"..."}
  {"type":"COMPLETE","agent":"backend","task":"03-01-task-1","summary":"Added auth middleware","timestamp":"..."}

WHY JSONL (not JSON):
  - Append-only = no write conflicts (multiple agents can append simultaneously)
  - Line-based = easy to read incrementally (tail -n +{offset})
  - No parse failures from concurrent writes (each line is independent)

READING PROTOCOL:
  - Agents read new messages since their last read (track line offset)
  - DISCOVERY messages inform all agents' playbooks
  - CONFLICT messages trigger orchestrator intervention
  - BLOCKED messages may unblock when another agent COMPLETEs a dependency
```

### Reasoning Trace Sharing (MAKER v9.1)

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

### Step 3.8: Monitor Agent — Planner-Executor Bridge (v12.9)

> Oct 2025, rev Jan 2026) — semantically equivalent planner outputs cause 7.9%-83.3% performance drops
> in executor agents. A lightweight monitor that checks executor alignment with planner intent fixes
> 40-88% of these failures. Cost: one verification prompt per breath, not a full agent spawn.

**BEFORE spawning executors for each breath, run the Monitor Check:**

```
FOR each plan in current breath:
  monitor_check = {
    plan_requirements: extract all must-haves + task done criteria from BLUEPRINT.md,
    executor_context: the context slice being injected into executor (from Step 5),
    skill_alignment: do loaded skills match the task requirements?
  }

  VERIFY:
  1. Every must-have from BLUEPRINT is represented in executor context
     → IF missing: inject the missing requirement before spawning
     → LOG: "Monitor: injected missing requirement '{req}' into executor context"

  2. Task dependencies are resolvable from executor's available context
     → IF dependency references a file/export from another plan not yet complete:
       FLAG: "Monitor: Task {N} depends on {file} from Plan {M} — not yet available"
       → Move task to next breath OR mark as BLOCKED

  3. No semantic drift between plan language and executor instructions
     → IF plan says "create REST endpoint" but task says "add function":
       CLARIFY in executor context: "This function serves as a REST endpoint"

  REPORT:
    monitor_injections: {count of items added/clarified}
    monitor_flags: {count of dependency issues found}

  IF monitor_injections > 0:
    LOG: "Monitor bridge: {N} context injections, {M} dependency flags"
```

**Skip condition:** SEQUENTIAL mode with single plan (no cross-agent coordination needed).
**Cost:** ~200 tokens per breath. Prevents failures that cost 5,000+ tokens to debug.

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

**Task Queue Initialization (v12.9 — SWARM/SUBAGENT only):**

```
IF mode in [SWARM, SUBAGENT]:
  Initialize task_queue in .planning/.shared-state.json:

  FOR each plan in current breath:
    FOR each task in plan's BLUEPRINT:
      task_queue["{plan_id}-{task_id}"] = {
        "owner": null,
        "status": "pending",
        "claimed_at": null,
        "completed_at": null,
        "transfer_count": 0,
        "failure_summary": null
      }

  Write shared-state.json with CAS (version + 1)
  Log: "Task queue initialized: {N} tasks across {M} plans"
```

> Orchestrator pre-populates the queue; executors claim/release via Step 1.55.

**Spawn fire-executor per plan (parallel for SUBAGENT/SWARM):**

```
â—† Spawning executors for Breath {W}...
  âš¡ fire-executor: Plan {N}-01 - {description}
  âš¡ fire-executor: Plan {N}-02 - {description}
```

### Step 5: fire-executor Agent Behavior (v13.0)

> **v13.0:** Context injection mode depends on the `--token-efficient` flag.
> Default = full context (best quality). Token-efficient = ALAS context slicing (~60% reduction).

**DEFAULT MODE — Full Context Injection:**

Each fire-executor receives the complete plan context:
```markdown
Inject into executor spawn:
- Full BLUEPRINT.md for this plan
- All skills_to_apply (full documents)
- CONSCIENCE.md project context
- Episodic recall (if available)
- Rolling playbook (if available)
- Checkpoint context (if resuming)
- Filtered shared state view (v12.9 — see below)
```

**Filtered State Views (v12.9 — SWARM/SUBAGENT only):**

> share by communicating, not by sharing memory." Each agent sees only what it needs.
> Reduces context noise and prevents agents from being confused by sibling state.

```
IF mode in [SWARM, SUBAGENT]:
  FOR each executor being spawned:
    filtered_state = {
      "my_tasks": [tasks from task_queue where owner=null OR owner={this_agent}],
      "decisions": [all decisions — these are shared knowledge],
      "sibling_status": [
        { "agent": "{name}", "tasks_completed": N, "status": "active|idle|blocked" }
        // Summary only — no full state from siblings
      ]
    }

    Inject as <shared_context> block in executor prompt.

  DO NOT inject:
    - Full .shared-state.json (too much irrelevant context)
    - Other agents' detailed error logs
    - Other agents' playbook entries
    - Raw .agent-messages.jsonl (agents read this themselves when needed)
```

**Scope-Isolated Tool Allowlists (v12.9 — SWARM/SUBAGENT only):**

> contributed to 90% autonomous task completion. Agents with unrestricted tool access
> make more out-of-scope changes. Scope isolation constrains blast radius.

```
IF mode in [SWARM, SUBAGENT]:
  FOR each executor being spawned:
    DERIVE tool_allowlist from BLUEPRINT scope manifest:

    backend_executor:
      allowed_files: "server/**", "shared/**"
      blocked_files: "client/**", "*.config.*"
      allowed_tools: [Read, Write, Edit, Bash, Grep, Glob]

    frontend_executor:
      allowed_files: "client/**", "shared/**"
      blocked_files: "server/**", "migrations/**"
      allowed_tools: [Read, Write, Edit, Bash, Grep, Glob]

    test_executor:
      allowed_files: "**/*.test.*", "**/*.spec.*", "e2e/**"
      blocked_files: [] (tests may read anything)
      allowed_tools: [Read, Write, Edit, Bash, Grep, Glob]

    INJECT as <scope_constraints> in executor prompt:
      <scope_constraints>
      You may ONLY modify files matching: {allowed_files}
      You may NOT modify files matching: {blocked_files}
      If you need changes outside your scope, write a CONFLICT message
      to .agent-messages.jsonl instead of making the change directly.
      </scope_constraints>

  NOTE: This is ADVISORY — Claude Code doesn't enforce file-level permissions.
  The executor's honesty protocol (Step 3) catches scope violations via
  self-assessment. The verifier (Step 1.9) validates no out-of-scope changes.

IF mode == SEQUENTIAL:
  Skip — single agent has full scope access.
```

**TOKEN-EFFICIENT MODE (`--token-efficient`) — ALAS Context Slicing:**

> See: `@skills-library/_general/methodology/ALAS_STATEFUL_EXECUTION.md`

Each fire-executor receives a **context slice** (600-1000 tokens instead of 8-10K):
```markdown
<plan_slice>
Plan: {N}-{NN} — {plan name}
Must-haves: {extracted list from BLUEPRINT frontmatter}
Tasks: {numbered task list with done criteria — extracted, not full BLUEPRINT}
Skills to apply: {skill names only — agent reads full skill on demand}
Scope: {allowed_files glob from scope manifest}
</plan_slice>

<checkpoint_context>
<!-- Only present when resuming or after task 1 -->
Last checkpoint: {cp-id} — {summary}
Playbook: {rolling 5 entries}
Execution log: .planning/phases/{N}-{name}/execution-log.json
</checkpoint_context>
```

**Full documents available ON DEMAND — agent reads only when needed:**
- `@.planning/phases/{N}-{name}/{N}-{NN}-BLUEPRINT.md` — read specific sections
- `@skills-library/{category}/{skill}.md` — read when confidence < 50
- `@.planning/CONSCIENCE.md` — read for phase status only

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

CRITICAL (<20%): Magentic-UI Escalation (v13.0)
  > escalation when agent confidence is critically low. Instead of guessing or
  > spinning, the agent asks the human for the SPECIFIC information it needs.
  → DO NOT attempt implementation
  → Compose targeted question: "I need to know X to proceed. Options: A, B, C."
  → Include: what you tried, what you learned, what specific gap remains
  → IF in autonomous mode (--autonomous): treat as BLOCKED, log to autonomous-log.md
  → IF in manual mode: surface question to user via AskUserQuestion
  → AFTER answer received: re-score confidence (should rise to LOW/MEDIUM)
  → This prevents the "confident but wrong" failure mode where agents produce
    plausible-looking but fundamentally incorrect implementations

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
5. Writes checkpoint to `execution-log.json` after each task (v13.0 — ALAS)
6. Updates SKILLS-INDEX.md with skills applied

**Agent Return Protocol (v13.0 — Structured Envelope):**

> See: `@skills-library/_general/methodology/MULTI_AGENT_COORDINATION.md` § Structured Agent Return Envelope
> Orchestrator reads structured envelope to decide next steps. Full transcript in execution log if needed.

```
When sub-agent completes, it returns a STRUCTURED ENVELOPE:
  {
    "agent": "{agent_name}",
    "plan": "{N}-{NN}",
    "status": "completed | failed | blocked | partial",
    "summary": "1-2 sentences of what was done" (MAX 200 tokens),
    "tasks": {
      "completed": ["task-1", "task-2"],
      "failed": ["task-3"],
      "skipped": []
    },
    "files_changed": ["path/to/file.ts"],
    "errors": [
      {
        "task": "task-3",
        "category": "INTERMITTENT | LOGIC | ARCHITECTURE | ENVIRONMENT",
        "message": "What went wrong",
        "severity": "ERROR | WARNING | PANIC",
        "retry_eligible": true
      }
    ],
    "warnings_count": 0,
    "confidence": 85,
    "checkpoint_id": "cp-003",
    "next_needs": "Brief note for downstream agent" (MAX 100 tokens)
  }

ORCHESTRATOR PARSING RULES:
  status=completed → proceed to next breath
  status=partial   → check tasks.failed for retry routing by error category
  status=failed    → route by errors[].category:
                     INTERMITTENT → retry up to 2x
                     LOGIC → re-read requirements, different approach
                     ARCHITECTURE → escalate to planner (do NOT retry)
                     ENVIRONMENT → fix env, then retry
  status=blocked   → read errors[0].message for blocker description
  warnings_count > 10 → treat as soft failure (oxc cumulative threshold)

Token savings: ~70% per agent return vs full transcript.

NOTE: The executor MUST set `warnings_count` in the envelope to the
`warning_count` accumulated across all tasks from Step 3.5 circuit breaker.
These are the SAME value — the field name uses plural in the envelope
for JSON convention but maps directly from the circuit breaker counter.
```

### Step 5.5: Quick Self-Judge (v5.0 — Agent-as-Judge)


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

### Step 7.05: Merge Only Successes (v12.9)

> to up to 10 workers, merges ONLY successful results. Failed workers are discarded without blocking.

```
IF mode == SWARM or mode == SUBAGENT:
  successful_agents = [agent for agent in breath_agents IF agent.status == "completed"]
  failed_agents = [agent for agent in breath_agents IF agent.status in ["failed", "blocked"]]

  FOR each successful_agent:
    → Merge RECORD.md into phase results
    → Include files_changed in commit

  FOR each failed_agent:
    → Log failure to autonomous-log.md: "Agent {name} failed: {error_summary}"
    → Discard output (do NOT merge failed work)
    → IF agent used git worktree: git worktree remove {path} (clean discard)
    → Add failed tasks back to "unclaimed" pool for next breath or retry

  IF successful_agents.length == 0:
    → ALL agents failed — this is a blocking error
    → GOTO "If Blocking Error" below

  IF failed_agents.length > 0 AND successful_agents.length > 0:
    → LOG: "Breath {W}: {len(successful)} succeeded, {len(failed)} failed — merging successes only"
    → Continue to next breath (failed tasks will be retried or escalated)
```

**Why:** Blocking the entire breath on one agent's failure wastes the work of successful agents. Merge successes, retry failures separately.

### Step 7.06: Dead Task Detection (v12.9)

> by any agent are silently dropped. Without detection, the verifier can PASS a phase that
> has unexecuted tasks (if they're not in must-haves).

```
AFTER breath completes, check task completeness:

  blueprint_tasks = all tasks defined in BLUEPRINT.md for plans in this breath
  completed_tasks = tasks marked completed in RECORD.md files
  skipped_tasks = tasks marked skipped in RECORD.md files
  all_accounted = completed_tasks + skipped_tasks

  missing_tasks = blueprint_tasks - all_accounted

  IF missing_tasks is not empty:
    FOR each missing task:
      LOG: "DEAD TASK: '{task_name}' (Plan {N}-{NN}) was defined but never executed"

    completeness = len(all_accounted) / len(blueprint_tasks) * 100

    IF completeness < 80%:
      → FLAG: "Only {completeness}% of planned tasks accounted for — investigate"
      → Add missing tasks to next breath's plan OR escalate to planner

    IF completeness >= 80% AND completeness < 99%:
      → NOTE: "{N} tasks unaccounted — logging for verifier review"
      → Write missing tasks to phase CONSCIENCE.md entry

    IF completeness >= 99% AND completeness < 100%:
      → WARN: "Near-complete — {N} task(s) missing. Likely skipped intentionally."
      → Log to verifier context for final judgment

  ELSE:
    → LOG: "Task completeness: 100% ({len(blueprint_tasks)} tasks accounted for)"
```

**If Blocking Error:**
- Create `.continue-here.md` with context
- Pause execution
- Display error and recovery instructions

### Step 7.1: Error Classification Health Check (v10.1)

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

### Step 7.85: Execution Insights Aggregation — Executor→Verifier Bridge (v12.9)

> Executor outputs (honesty checkpoints, playbook entries) contain high-signal information
> that the verifier needs but currently doesn't receive. Aggregation bridges this gap
> without dumping raw executor context.

```
AFTER all breaths complete, BEFORE spawning verifier:

  AGGREGATE from executor outputs:
    1. honesty_checkpoints: Extract from RECORD.md → "confidence_trail" array
       → [{task, confidence, note}] for each task where confidence < 80
       → Verifier uses these to focus inspection on low-confidence work

    2. decisions: Extract from .agent-messages.jsonl type=DECISION
       → Verifier checks: do decisions align with BLUEPRINT intent?

    3. discoveries: Extract from .agent-messages.jsonl type=DISCOVERY
       → Verifier checks: were discoveries acted on or ignored?

  COMPILE into <executor_insights> block:
    <executor_insights>
    Low-confidence tasks: {list with reasons}
    Key decisions: {list}
    Discoveries: {list}
    </executor_insights>

  INJECT into verifier spawn prompt (Step 8).

COST: ~150 tokens aggregation. Saves verifier from re-discovering known issues.
SKIP: If no RECORD.md files exist (execution failed before any output).
```

### Step 7.9: Hierarchical Review — Author Self-Check (v12.9)

> (arXiv 2509.20502, Sep 2025 — hierarchical review cuts verification tokens ~50%)

Before spawning expensive external verification, run a lightweight self-check:

```
AUTHOR SELF-CHECK (from executor RECORD.md files):

  FOR each RECORD.md produced by executors:
    EXTRACT:
      - files_changed list
      - must_haves_addressed (from BLUEPRINT cross-reference)
      - known_gaps (executor's own honesty declarations)
      - test_results (if any tests were run)

    QUICK VALIDATION:
      1. Every must-have from BLUEPRINT has at least one file addressing it
      2. No must-have is marked "skipped" without documented reason
      3. Executor's own confidence >= 60 (from return envelope)

    IF self_check fails:
      → Route BACK to executor for fix BEFORE spawning verifier/reviewer
      → Log: "Author self-check failed: {reason} — re-executing before review"
      → This saves ~2,000 tokens vs. full verifier discovering the same gap

    IF self_check passes:
      → Proceed to Step 8 (full verification)
      → Pass self_check summary to verifier as context (reduces redundant checks)

SKIP CONDITION: --skip-self-check flag OR single-task phases (overhead > benefit)
COST: ~100 tokens. Catches 60-70% of obvious gaps before expensive review.
```

### Step 7.95: Background Agent Execution (v13.0 — Async Subagents)

> support. NOW UNBLOCKED: Claude Code shipped async subagents (`run_in_background: true`)
> enabling fire-and-forget execution with notification on completion.

**Use background agents for independent, non-blocking work during phase execution:**

```
ELIGIBLE for background execution:
  - Skill extraction (Step 7.7) — doesn't block next breath
  - fire-researcher spawns from STUCK REPORT (Step 3.5.6) — research while continuing
  - Episodic memory indexing after phase completion
  - Test suite runs that don't gate the next task

NOT eligible (must be foreground):
  - fire-executor (needs results for breath completion)
  - fire-verifier (gates phase advancement)
  - fire-reviewer (gates merge decision)
  - Any agent whose output determines the next step

SPAWN PATTERN:
  Agent(
    subagent_type="fire-researcher",
    prompt="Research: {stuck_report.research_query}",
    run_in_background=true
  )
  → Continue with current work
  → When agent completes, notification arrives
  → Integrate results into playbook if still relevant

  Agent(
    subagent_type="general-purpose",
    prompt="Extract skills from phase {N} RECORD files",
    run_in_background=true
  )
  → Skill creation happens asynchronously
  → Does not block breath execution

SAFETY:
  - Background agents inherit path constraints from parent
  - Background agents do NOT write to shared-state.json (race condition)
  - Background agents use read-only access to codebase
  - Maximum 2 background agents at a time (prevent resource exhaustion)
```

**Why this matters:** Skill extraction (Step 7.7) previously blocked execution for 30-60 seconds. Research spawns from STUCK REPORT blocked the stuck agent from trying alternatives. Background execution eliminates both bottlenecks.

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

### Step 8.4: Structured Verdict Extraction (v12.5)
When both agents return, extract structured verdicts:

```
# Extract verifier verdict
verifier_output = agent_result.text
verifier_json = extract_between(verifier_output, "VERIFIER_VERDICT_START", "VERIFIER_VERDICT_END")
IF verifier_json:
  verifier_verdict = JSON.parse(verifier_json)
  warrior_score = verifier_verdict.warrior_score
  verifier_status = verifier_verdict.verdict  # APPROVED | CONDITIONAL | REJECTED
ELSE:
  # Fallback: parse prose verdict from VERIFICATION.md (legacy behavior)
  verifier_status = parse_prose_verdict(verification_file)

# Extract reviewer verdict
reviewer_output = agent_result.text
reviewer_json = extract_between(reviewer_output, "REVIEWER_VERDICT_START", "REVIEWER_VERDICT_END")
IF reviewer_json:
  reviewer_verdict = JSON.parse(reviewer_json)
  reviewer_status = reviewer_verdict.verdict  # APPROVE | APPROVE_WITH_FIXES | BLOCK
  blocking_count = reviewer_verdict.counts.blocking_issues
ELSE:
  # Fallback: parse prose verdict from REVIEW.md (legacy behavior)
  reviewer_status = parse_prose_verdict(review_file)
```

### Step 8.5: Merge Gate — Combined Quality Decision (v8.0)

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

**DISAGREEMENT HANDLING (v13.0 — Verdict Arbitration Protocol):**

> **Source:** uv PubGrub `priority.rs` weighted scoring + fork strategy.
> See: `@skills-library/_general/methodology/MULTI_AGENT_COORDINATION.md` § Verdict Arbitration Protocol

```
TRIGGER: Only invoke Verdict Arbitration when verifier and reviewer
produce CONTRADICTORY verdicts (not just different severity levels).
If the COMBINED VERDICT MATRIX above resolves cleanly, use that result directly.

WHEN verifier and reviewer produce contradictory verdicts:

  1. CLASSIFY CONFLICT TYPE:
     - SCOPE: Verifier checks functionality, reviewer checks quality
       → Both can be right. Apply BOTH sets of fixes.
       → Set combined_verdict = "FIX BOTH"
     - SEVERITY: Verifier says PASS, reviewer says BLOCK
       → Weighted resolution (see below)
     - CONTRADICTION: Verifier says "add X", reviewer says "remove X"
       → Fork resolution

  2. WEIGHTED RESOLUTION (from uv conflict prioritization):
     verifier_weight = 0.6  (functional correctness is primary)
     reviewer_weight = 0.4  (code quality is secondary)

     FOR each conflicting item:
       IF verifier says PASS and reviewer says BLOCK:
         combined_score = (verifier_confidence * 0.6) + (reviewer_confidence * 0.4)
         IF combined_score > 70: PASS with reviewer's suggestions as TODOs
           → Set combined_verdict = "READY FOR HUMAN"
         IF combined_score <= 70: FAIL — fix required
           → Set combined_verdict = "FIX REVIEW FINDINGS"

       IF verifier says FAIL: always FAIL (functional correctness is non-negotiable)
         → Set combined_verdict = "FIX VERIFIER"

  3. FORK RESOLUTION (from uv fork-based resolver):
     When verdicts are genuinely contradictory:
       Fork A: Apply verifier's recommendation
       Fork B: Apply reviewer's recommendation
       Run verification on BOTH forks
       Accept the fork that passes verification
       If BOTH pass: accept verifier's (functional correctness wins)
         → Set combined_verdict = "READY FOR HUMAN"
       If NEITHER passes: escalate to human
         → Set combined_verdict = "FIX BOTH (critical)"

  4. CONFLICT HISTORY TRACKING (from uv incompatibility store):
     Track which reviewer personas frequently conflict with verifier
     After 3+ conflicts from same persona IN CURRENT PHASE:
       → Deprioritize that persona's BLOCK votes to weight 0.2
     Deprioritization resets at the start of each new phase.
     (A persona wrong in Phase 2 may be right in Phase 5.)

  5. VOTING FOR VERDICTS (v12.9 — replaces pure weighted scoring for SEVERITY conflicts):

     > (ACL 2025 — voting improves reasoning tasks by 13.2%, consensus improves knowledge by 2.8%)

     WHEN conflict type is SEVERITY (verifier PASS vs reviewer BLOCK):

       a. COLLECT INDEPENDENT VOTES from each reviewer persona that participated:
          Each persona casts: PASS | SOFT_BLOCK | HARD_BLOCK
          (Personas already produced findings — extract vote from severity of their findings)

       b. TALLY:
          pass_votes = count(PASS)
          soft_block_votes = count(SOFT_BLOCK)
          hard_block_votes = count(HARD_BLOCK)
          total_votes = pass_votes + soft_block_votes + hard_block_votes

       c. RESOLVE:
          IF hard_block_votes >= 2:
            → combined_verdict = "FIX BLOCKERS" (multiple personas see critical issues)
          ELIF pass_votes > (soft_block_votes + hard_block_votes):
            → combined_verdict = "READY FOR HUMAN" (majority pass)
            → Log soft_block findings as non-critical TODOs
          ELSE:
            → combined_verdict = "FIX REVIEW FINDINGS" (no clear majority)

       d. LOG vote breakdown to .planning/version-performance.md:
          "Personas: {pass_votes}P / {soft_block_votes}S / {hard_block_votes}H"

     FALLBACK: If reviewer ran with fewer than 3 personas, use weighted resolution (step 2) instead.
     Voting requires sufficient independent perspectives to be meaningful.

  OUTPUT: After resolving, the combined_verdict is set above.
  Return to Autonomous Mode Routing / Display with this value.

STANDARD QUICK PATH (no arbitration needed):

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
