---
description: Start self-iterating loop until completion with circuit breaker, error classification, context engineering, and skills integration
argument-hint: "PROMPT [--max-iterations N] [--completion-promise TEXT]"
---

# /fire-loop

> Self-iterating autonomous loop with quantitative convergence detection, approach rotation, and context-aware execution

---

## Purpose

Start a self-iterating loop that persists until task completion. Integrates Dominion Flow's full v3 intelligence stack:

- **Circuit Breaker** — Hard numerical thresholds that detect stalling, spinning, and degradation
- **Error Classification** — PROGRESS/STALLED/SPINNING/DEGRADED/BLOCKED state machine driving different responses
- **Context Engineering** — Recitation pattern keeps plan in attention window; .powerignore excludes noise
- **Decision-Time Guidance** — Skills library micro-instructions injected at error/decision points
- **Sabbath Rest** — Context rot detection with state persistence for clean resume

**Key difference from `/fire-loop`:** Power Loop is self-aware. It measures its own health, rotates approaches when stuck, and stops before wasting iterations on unsolvable problems.

---

## Arguments

```yaml
arguments:
  prompt:
    required: true
    type: string
    description: "Task description with clear completion criteria"
    example: '/fire-loop "Fix login bug. Tests must pass. Output DONE when fixed."'

options:
  --max-iterations:
    type: number
    default: 50
    description: "Safety limit — stop after N iterations"

  --completion-promise:
    type: string
    default: "DONE"
    description: "Exact text that signals successful completion"

  --checkpoint-interval:
    type: number
    default: 5
    description: "Save checkpoint every N iterations"

  --apply-skills:
    type: boolean
    default: true
    description: "Search and apply relevant skills from library"

  --discover:
    type: boolean
    default: false
    description: "Run /fire-discover at start to find relevant patterns"

  --no-circuit-breaker:
    type: boolean
    default: false
    description: "Disable circuit breaker (not recommended)"

  --aggressive:
    type: boolean
    default: false
    description: "Tighter thresholds: stall=2, spin=3, decline=40%"

  --autonomous:
    type: boolean
    default: false
    description: "Auto-route review gate verdicts without human checkpoints (used by /fire-autonomous)"
```

---

## Process

### Step 0.5: Path Verification Gate (v5.0 — MANDATORY)

Before creating any files or executing any work, verify working directory:

```
expected_project = extract from CONSCIENCE.md or user context
actual_cwd = pwd

IF actual_cwd does NOT contain expected project path:
  → HARD STOP: "Wrong directory. Expected {expected}, got {actual_cwd}."
  → Do NOT create loop files in wrong project.

IF .planning/ directory does not exist:
  → WARN: "No .planning/ directory. Is this the right project?"
  → Ask user to confirm before proceeding.
```

### Step 1: Initialize Loop State

Create loop tracking file with v3 enhanced fields:

```bash
mkdir -p .planning/loops
LOOP_ID=$(date +%Y%m%d-%H%M%S)
LOOP_FILE=".planning/loops/fire-loop-${LOOP_ID}.md"
```

Write initial state:

```markdown
---
id: ${LOOP_ID}
status: active
prompt: |
  [user's prompt]
completion_promise: [promise text]
max_iterations: [N]
current_iteration: 0
started: [timestamp]
last_checkpoint: null
skills_applied: []
context_warnings: 0

# v3 Circuit Breaker State
circuit_breaker:
  state: HEALTHY
  stall_counter: 0
  error_hashes: {}
  output_baseline: null
  output_history: []
  approaches_tried: []

# v3 Error Classification
health_state: PROGRESS
health_history: []
---

## Loop Progress

| Iter | Timestamp | Files Changed | Error Hash | Output Lines | Health | Action |
|------|-----------|--------------|------------|-------------|--------|--------|

## Circuit Breaker State

| Iter | Stall Count | Spin Count | Output % | State |
|------|-------------|------------|----------|-------|

## Approaches Tried

## Checkpoints

## Sabbath Rest Snapshots

## Final Result
```

### Step 2: Context Engineering Setup

```
1. Load .powerignore if present in project root
2. Establish context layout:
   - STABLE: System prompt + project context + skills (loaded once)
   - SEMI-STABLE: Plan context + DTG instructions
   - DYNAMIC: Recitation block + iteration output
3. Set recitation template for this task
```

### Step 3: Run /fire-discover (if --discover)

Before starting, discover relevant patterns:

```
/fire-discover "[task keywords from prompt]"
```

Cache discovered skills — don't re-search each iteration.

### Step 4: Skills Library Search (if --apply-skills)

Search for relevant skills based on task keywords:

```
Search skills library for patterns matching:
- Error patterns mentioned in prompt
- Technology/framework keywords
- Problem domain (auth, api, database, etc.)
```

Load applicable skills into context (max 3 skills, micro-instruction format):

```markdown
## Skills Loaded (cached for session)

### [Skill 1]: {name}
- Pattern: {key pattern}
- Pitfalls: {common pitfalls}

### [Skill 2]: {name}
- Pattern: {key pattern}
- Pitfalls: {common pitfalls}
```

### Step 5: Update CONSCIENCE.md

Add loop tracking to project state:

```markdown
## Active Power Loop

- **ID:** ${LOOP_ID}
- **Started:** [timestamp]
- **Iteration:** 0 / [max]
- **Status:** Running
- **Promise:** "[completion_promise]"
- **Health:** PROGRESS
- **Circuit Breaker:** HEALTHY

To cancel: `/fire-loop-stop`
```

### Step 6: Display Start Banner

```
+------------------------------------------------------------------------------+
| POWER LOOP v3 STARTED                                                        |
+------------------------------------------------------------------------------+
|                                                                              |
|  Loop ID: ${LOOP_ID}                                                         |
|  Max Iterations: [N]                                                         |
|  Completion Promise: "[promise]"                                             |
|                                                                              |
|  Intelligence Stack:                                                         |
|    Circuit Breaker: [ON | OFF]                                               |
|    Error Classification: ON                                                  |
|    Context Engineering: ON                                                   |
|    Decision-Time Guidance: [ON | OFF]                                        |
|    Sabbath Rest: ON                                                          |
|                                                                              |
|  Skills Applied: [count]                                                     |
|    - [skill 1]                                                               |
|    - [skill 2]                                                               |
|                                                                              |
|  Context Exclusions: [.powerignore loaded | none]                            |
|                                                                              |
+------------------------------------------------------------------------------+
| ITERATION 1                                                                  |
+------------------------------------------------------------------------------+
```

---

## ITERATION LOOP (Steps 6.5-11)

### Step 6.5: Difficulty Classification (v7.0)

> **Research basis:** Difficulty-Aware Agent Orchestration (Sep 2025) — +11.21% accuracy at 64% cost
> by routing tasks through different pipeline depths based on complexity.

Classify current task before entering the iteration pipeline:

```
SIMPLE (fast path — skip Steps 7.1, 8.5, 8.8):
  - Single file change
  - Known pattern (exact skill match found)
  - Config/typo/rename tasks
  - Estimated < 5 minutes

MODERATE (standard path — all steps active):
  - 2-5 files affected
  - Requires some investigation
  - Partial skill match or unfamiliar combination

COMPLEX (enhanced path — all steps + extra validation):
  - 6+ files affected or cross-cutting concern
  - No skill match, unfamiliar framework
  - Architecture or security implications
  - Add: double-check step before commit, mandatory episodic injection

Store classification in recitation block: "Difficulty: {SIMPLE|MODERATE|COMPLEX}"

For SIMPLE tasks: skip Step 7.1 (episodic injection), Step 8.5 (directive check),
Step 8.8 (reward scoring). Go directly from Step 7 → Step 8 → Step 9.

### Parallelizability Axis (v10.0)

> **Research basis (v10.0):** Google/MIT "Scaling Laws for Agent Systems" (Dec 2025) —
> multi-agent parallel execution improves parallelizable tasks by 80.9% but DEGRADES
> sequential reasoning by 39-70%. The difficulty axis alone is insufficient — a COMPLEX
> task that is inherently sequential gets WORSE with parallel agents.

After difficulty classification, add a second axis: PARALLEL vs SEQUENTIAL:

```
PARALLEL (can split into independent sub-tasks):
  Signals:
  - Different files with no shared state
  - Independent API endpoints
  - UI components with no prop dependencies
  - Test suites for different modules
  → SWARM/SUBAGENT mode beneficial
  → Agent count scales well

SEQUENTIAL (steps depend on previous results):
  Signals:
  - Migration chains (step N depends on step N-1)
  - Auth flow (login → token → protected route)
  - Data pipeline (extract → transform → load)
  - Debugging (hypothesis → test → narrow → fix)
  → SEQUENTIAL mode MANDATORY
  → Multiple agents DEGRADE performance
  → Single agent with full context is optimal

MIXED (some steps parallel, some sequential):
  → Break into sequential phases, parallelize within each phase
  → Example: "Build API + UI" = parallel, then "Wire API→UI" = sequential
```

**Combined routing matrix:**

| Difficulty | Parallelizability | Mode | Agents |
|-----------|-------------------|------|--------|
| SIMPLE | any | SEQUENTIAL | 1 (Haiku) |
| MODERATE | PARALLEL | SUBAGENT | 2-3 |
| MODERATE | SEQUENTIAL | SEQUENTIAL | 1 |
| COMPLEX | PARALLEL | SWARM | 3-5 |
| COMPLEX | SEQUENTIAL | SEQUENTIAL | 1 (Opus) |
| COMPLEX | MIXED | HYBRID | sequential phases, parallel within |

Store in recitation: "Difficulty: {X} | Parallelizability: {PARALLEL|SEQUENTIAL|MIXED}"
```

### Agent Profile Selection (ATLAS v9.1)

> **Research basis:** ATLAS (2025) — Adaptive Task-Level Agent Selection.
> Dynamically choosing agent capability per task improves efficiency without sacrificing quality.

After classifying difficulty, select the agent profile:

```
SIMPLE → agent_profile: "lightweight"
  - Skip episodic injection, behavioral directives, reward scoring
  - Single agent, sequential execution
  - No specialist context needed

MODERATE → agent_profile: "standard"
  - All steps active
  - fire-executor with full skill context
  - SUBAGENT or SEQUENTIAL based on file overlap

COMPLEX → agent_profile: "specialist"
  - All steps + mandatory double-check before commit
  - Select specialist based on file patterns:
    * 60%+ backend files (routes/, models/, middleware/) → backend-specialist
    * 60%+ frontend files (components/, pages/, hooks/) → frontend-specialist
    * 60%+ test files (*.test.*, *.spec.*) → test-specialist
    * Mixed or infrastructure files → full fire-executor
  - SWARM mode preferred for cross-cutting changes
  - Extended thinking enabled for architecture decisions
```

**Specialist context injection (COMPLEX only):**

When agent_profile is "specialist", prepend to executor prompt:
```
<specialist_focus>
You are operating as a {domain}-specialist. Prioritize:
- backend-specialist: API contracts, DB queries, middleware chain, error handling
- frontend-specialist: Component composition, state management, UX flows, accessibility
- test-specialist: Coverage gaps, edge cases, integration boundaries, mock accuracy
</specialist_focus>
```

Store in recitation block: "Agent Profile: {lightweight|standard|specialist}"

---

### Step 7: Compose Recitation Block

Before each iteration, recite current state (max 30 lines):

```markdown
---
DOMINION FLOW RECITATION — Iteration {N} of {MAX}
---

## Task
{original prompt — unchanged}

## Progress
- Iterations completed: {N-1}
- Files changed total: {count}
- Last action: {what happened last iteration}
- Current approach: {active approach description}

## Health
- State: {PROGRESS | STALLED | SPINNING | DEGRADED | BLOCKED}
- Circuit Breaker: {HEALTHY | WARNING | TRIPPED}
- Stall counter: {N} / {threshold}
- Spin counter: {N} / {threshold}
- Output trend: {stable | declining N%}
- Confidence: {HIGH >80 | MEDIUM 50-80 | LOW <50}

## Approaches Tried
{numbered list of approaches, most recent first}

## Key Finding
{most important thing learned so far}

## Task Checklist (v10.0)
<!-- Read todos.md if present in .planning/ or project root -->
<!-- Surface unchecked items relevant to current iteration -->
{IF .planning/todos.md exists:}
- [ ] {relevant unchecked item 1}
- [ ] {relevant unchecked item 2}
{ELSE: omit this section}

## Confidence Check (v5.0)
- Score: {0-100} — {HIGH/MEDIUM/LOW}
- Signals: {what raised or lowered confidence}
- Action: {proceed / extra-validation / escalate}
---
```

**Confidence Gate (v5.0):** Before executing, estimate confidence for this iteration:

```
confidence = 50 (baseline)
  + skill_match?     +20 (found matching skill in library)
  + reflection_match? +15 (found matching reflection)
  + tests_available?  +25 (can verify changes)
  + familiar_tech?    +15 (worked with this before)
  - unfamiliar?       -20 (new framework/library)
  - no_tests?         -15 (can't verify)
  - ambiguous?        -20 (unclear what to do)

IF confidence < 50:
  → Search reflections and skills before proceeding
  → If still LOW: ask user for guidance
  → Create checkpoint before attempting
```

**Confidence Propagation (v7.0 — AUQ):**

> **Research basis:** AUQ (Jan 2026) — System 1/System 2 uncertainty split; AgentPRM
> (Feb 2025) — process reward hacking detection. Metacognition limits paper (Sep 2025)
> warns: don't trust self-reported confidence alone.

```
## System 1 (UAM — Uncertainty-Aware Memory)
# Propagate uncertainty from previous iterations:
propagated_uncertainty = 0
FOR each prev_iteration in last 3 iterations:
  IF prev_iteration.confidence < 50:
    propagated_uncertainty += (50 - prev_iteration.confidence) * 0.3
    # Uncertainty decays: recent iterations weigh more

adjusted_confidence = raw_confidence - propagated_uncertainty
# A string of low-confidence iterations compounds the penalty

## System 2 (UAR — Triggered Deep Reflection)
# Only fires when System 1 flags a concern:
IF adjusted_confidence < 40 OR propagated_uncertainty > 30:
  → Trigger deep reflection: review last 3 iterations' outcomes
  → Search vector memory for similar situations
  → If reflection finds pattern: adjust approach
  → If no pattern: escalate to user

## Confidence-Outcome Divergence Detector (v7.0 — AgentPRM)
# Process reward hacking: confidence rises while outcomes degrade
IF iteration >= 3:
  confidence_trend = linear_slope(last 3 confidence scores)
  reward_trend = linear_slope(last 3 turn_rewards from Step 8.8)

  IF confidence_trend > 0 AND reward_trend < 0:
    → FLAG: "Confidence rising but outcomes declining — possible reward hacking"
    → Trigger early circuit breaker WARNING
    → Force external verification (run tests, check git diff)
```

### Step 7.1: Per-Turn Episodic Auto-Injection (v6.0)

> **Research basis:** CoALA (Berkeley 2024) — Cognitive architecture requires automatic
> episodic injection every decision cycle, not just on stall or low confidence.
> "Every action cycle should: retrieve relevant episodic memory → inject into working
> context → decide → store outcome."

Before each task execution, automatically recall relevant episodic memory:

```
# 1. Extract keywords from current task
task_keywords = extract_keywords(current_task_description)

# 2. Search vector memory (use two-phase retrieval from Breath 2)
cd ~/.claude/memory
results = npm run search -- "{task_keywords}" --limit 3 --two-phase

# 3. Inject if relevant results found
IF results exist AND top_result.score > 0.7:
  Inject into working context:

  <episodic_context>
  <!-- Auto-injected by CoALA episodic recall (v6.0 Step 7.1) -->
  <!-- These are past experiences relevant to this task -->

  {For each result with score > 0.7:}
  **[{result.sourceType}] {result.title}** (score: {result.score})
  {result.text (first 300 chars)}
  Source: {result.sourceFile} | Date: {result.date}

  </episodic_context>

ELSE:
  # No relevant memories — proceed without injection
  # This is normal for novel tasks
```

**Cost control:** This adds ~500 tokens per iteration when memories are found.
Skip injection if iteration count > 5 (agent should be deep enough by then).

**Graceful Qdrant Degradation (v9.0):**

If Qdrant is unreachable (connection refused on port 6335), log WARNING and fall back to file-based memory search: grep across `~/.claude/warrior-handoffs/` and `~/.claude/reflections/` for keyword matches. This is slower but functional. Do NOT silently skip memory retrieval. The fallback ensures that even without the vector database, the agent still benefits from past session context. Log the degradation:

```
WARNING: Qdrant unreachable on port 6335. Falling back to file-based memory search.
  Searched: ~/.claude/warrior-handoffs/ ({N} files)
  Searched: ~/.claude/reflections/ ({N} files)
  Results: {N} keyword matches found
```

---

### Step 8: Execute Task

Work on the task described in the prompt.

**CRITICAL RULES:**

1. **Completion Promise Integrity:** Only output the completion promise when the task is GENUINELY complete. Do not fake completion to escape the loop.

2. **Check Previous Work:** At each iteration, check:
   - Files modified in previous iterations
   - Git history for recent changes
   - Test results from previous runs
   - Loop file for iteration history

3. **Incremental Progress:** Each iteration should make measurable progress. If stuck:
   - Check recitation block for approaches already tried
   - Run Decision-Time Guidance search for the current error
   - Document what was attempted
   - Try a fundamentally different approach

4. **Context Hygiene:**
   - Don't re-read files already in context
   - Use .powerignore exclusions
   - Summarize large file reads (extract relevant section only)
   - Keep iteration output focused and concise

### Step 8.5: Behavioral Directive Check + HAC Enforcement (v6.0 + v7.0)

> **Research basis:** CoALA procedural memory + SICA self-modifying agent (ICLR 2025)
> v7.0 addition: MPR (Sep 2025) — Predicate-form rules with Hard Admissibility Checks

**(Skip if difficulty = SIMPLE — see Step 6.5)**

**Part A — HAC Pre-Execution Check (v7.0):**

```
BEFORE executing the next action, scan behavioral-directives.md:

For each Active Rule where IF condition matches current context:
  IF rule is positive (THEN) → inject action into working instructions
  IF rule is anti-pattern (DONT) → inject explicit warning

HAC (Hard Admissibility Check):
  IF an Active Rule OR Anti-Pattern with confidence 5/5
  explicitly prohibits the planned action:
    → BLOCK execution
    → Display: "HAC BLOCK: {rule/anti-pattern statement}"
    → Require explicit user override to proceed
```

**Part B — Directive Discovery (v6.0, unchanged):**

```
IF task resolution revealed a reusable pattern or anti-pattern:
  1. Read references/behavioral-directives.md
  2. Check: does similar directive already exist?
     ├── In Active Rules → Skip (already known)
     ├── In Proposed Rules → Increment confidence
     │     └── If confidence reaches 3/5 → Promote to Active Rules
     └── Not found → Add to Proposed Rules with confidence 1/5

  New rules use predicate format (v7.0):
    ### Rule {N}
    - **IF:** {condition}
    - **THEN:** {action} (or **DONT:** {anti-action})
    - **BECAUSE:** {justification}
    - **Source:** {current session} | **Confidence:** 1/5 | **First proposed:** {date}

  SKIP this step if:
    - Task was trivial (single-line fix)
    - No novel insight emerged
    - The insight is project-specific, not reusable
```

### Step 8.7: Iteration Checkpoint (v6.0 — GCC)

> **Research basis:** GCC (Jul 2025) — Git-style checkpoints enable structured rollback.

After each iteration that made file changes:

```
IF git_diff_stat(HEAD) shows changes:
  git add {files changed this iteration}
  git commit -m "loop-checkpoint: iteration {i} — {task summary (50 chars max)}"
  checkpoint = git rev-parse HEAD

  # Record in fire-flow.local.md
  Append:
    checkpoint_hash: {checkpoint:7}
    iteration: {i}
    files_changed: {count}
    task: "{task summary}"

  # On resume: can restore to any checkpoint
```

**Skip checkpoint if:** No files changed this iteration (research-only or read-only work).

### Step 8.8: Turn-Level Reward Scoring (v6.0 — AgentPRM)

> **Research basis:** AgentPRM (Feb 2025) — Process reward models that score each turn
> in a multi-turn interaction enable fine-grained learning signals. Binary success/fail
> is like grading pass/fail — you can't improve. Per-turn rewards enable identifying
> which task types the agent handles well vs poorly.

After each iteration, compute turn-level reward:

```
# Score this iteration (each 0-5)
task_completion = IF task_complete THEN 5 ELSE (progress_percentage / 20)
approach_quality = 5 - min(4, retries_needed)    # 5=first try, 1=4+ retries
context_efficiency = 5 - min(4, floor(tokens_used / 20000))  # 5=<20k, 1=>80k tokens

# Weighted turn reward
turn_reward = (0.5 * task_completion) + (0.3 * approach_quality) + (0.2 * context_efficiency)

# Store in fire-flow.local.md
Append to iteration_rewards:
  - iteration: {i}
    reward: {turn_reward, 1 decimal}
    task: "{task description (50 chars)}"
    completion: {task_completion}
    quality: {approach_quality}
    efficiency: {context_efficiency}
```

**Use accumulated rewards to:**
1. Identify which task types score low → pre-load relevant skills next time
2. Detect declining reward trend → trigger approach rotation earlier
3. Compute session average reward → include in WARRIOR handoff for trend tracking

---

### Step 9: Measure and Classify

After each iteration, collect measurements:

```
measurements = {
  files_changed:  git diff --stat HEAD~1 | count,
  error_output:   last error message if any,
  error_hash:     hash(normalize(error_output)),
  output_lines:   count_lines(iteration_output),
  test_results:   {passed: N, failed: N, total: N}
}
```

**Error Classification** (see `@references/error-classification.md`):

```
health = classify_health(measurements)

SWITCH health:
  PROGRESS:
    → Continue normally
    → Record in loop file

  STALLED:
    → Inject urgency: "No file changes in {N} iterations. Make a change."
    → Search skills library for alternative approaches
    → Search reflections: /fire-remember "{current error/goal}" --type reflection
    → If 3+ iterations stalled → escalate check
    → If 3+ iterations stalled → Auto-generate reflection (v5.0):
        Save to ~/.claude/reflections/{date}_loop-stalled-{task-slug}.md
        trigger: "stalled-loop"
        Include: what was attempted, measurements, why no progress

  SPINNING:
    → FORCE approach rotation
    → Display: "Error seen {N} times. Previous approaches: {list}. Try different."
    → Inject anti-patterns: "DO NOT: {failed approaches}"
    → Auto-generate reflection (v5.0):
        Save to ~/.claude/reflections/{date}_loop-spinning-{task-slug}.md
        trigger: "approach-rotation"
        Include: each failed approach with error hash, what was rotated to

  DEGRADED:
    → Trigger Sabbath Rest warning
    → Save state for resume

  BLOCKED:
    → Stop immediately
    → Create blocker in BLOCKERS.md
    → Save state, display recovery options
```

**Semantic Progress Metric (v9.0):**

Augment output volume with semantic progress signals to reduce false positives from verbose error output:

```
semantic_progress = {
  checklist_completion: count completed tasks / total tasks,
  test_pass_delta: (tests_passing_now - tests_passing_last_iter),
  git_diff_ratio: actual_diff_size / expected_diff_size,
  meaningful_change: any new file created OR test status changed OR API endpoint added
}

# Output volume alone is noisy — verbose errors have high volume but zero progress.
# Combine: effective_progress = 0.4 * output_metric + 0.6 * semantic_progress
# Use effective_progress instead of raw output volume for circuit breaker thresholds.
```

**Circuit Breaker Check** (see `@references/circuit-breaker.md`):

```
cb_state = circuit_breaker.check(
  stall_counter,
  error_hash_counts,
  output_volume_vs_baseline,
  semantic_progress          # v9.0: augmented signal
)

IF cb_state == WARNING:
  → Display warning banner
  → Apply approach rotation
  → Continue with new approach

IF cb_state == TRIPPED:
  → Display break banner
  → Save complete state
  → Trigger Sabbath Rest or stop
```

### Step 10: Update Loop File

Record iteration in tracking table:

```markdown
| {N} | {timestamp} | {files_changed} | {error_hash} | {output_lines} | {health} | {action_taken} |
```

Update circuit breaker state table:

```markdown
| {N} | {stall_count} | {spin_count} | {output_pct}% | {cb_state} |
```

### Step 11: Checkpoint (if interval reached)

If iteration % checkpoint_interval == 0:

```
1. Write detailed checkpoint to loop file
2. Update CONSCIENCE.md with current progress
3. Commit checkpoint: git commit -m "checkpoint: fire-loop iteration {N}"
4. Update active-loop.json with current counters
```

### Step 12: Continuation Decision

```
IF completion_promise found in output:
  → COMPLETE: Go to Step 12.5 (review gate)

IF iteration >= max_iterations:
  → MAX REACHED: Go to Step 13

IF circuit_breaker == TRIPPED:
  → CIRCUIT BREAK: Save state, go to Step 13

IF health == BLOCKED:
  → BLOCKED: Save state, go to Step 13

IF health == DEGRADED AND output_decline >= 70%:
  → SABBATH REST: Save state, go to Step 13

ELSE:
  → INCREMENT iteration
  → GO TO Step 7 (compose new recitation block)
```

### Step 12.5: Post-Loop Review Gate (v8.0)

When loop claims completion, run shallow review before presenting to human.

**Autonomous Mode Routing (v9.0):**

```
IF --autonomous flag is set:

  IF review.verdict == "BLOCK":
    Log to autonomous-log: "Review gate: BLOCK (auto-routing to fix iteration)"
    → Increment iteration, back to Step 7 (no display)

  IF review.verdict == "APPROVE WITH FIXES":
    Log to autonomous-log: "Review gate: APPROVE WITH FIXES (auto-proceeding)"
    → Proceed to Step 13 (no display)

  IF review.verdict == "APPROVE":
    → Proceed to Step 13

  // Non-autonomous mode: fall through to standard display below
```

**Standard (non-autonomous) behavior:**

```
IF completion_promise found AND files_changed > 0:

  files_changed = git diff --name-only {first_checkpoint}..HEAD

  Task(subagent_type="fire-reviewer", prompt="""
    Loop: {LOOP_ID}
    Task: {original prompt}
    Review Depth: shallow (5 personas: Simplicity + Security + Perf + Test + Pattern)
    Files: {files_changed}
    <simplicity_mandate>STRICT</simplicity_mandate>
    Output to: .planning/loops/review-{LOOP_ID}.md
  """)

  IF review.verdict == "BLOCK":
    Display:
    "+--------------------------------------------------------------+"
    "| REVIEW GATE — BLOCK                                           |"
    "+--------------------------------------------------------------+"
    "|                                                              |"
    "|  Loop completed task but review found critical issues:       |"
    "|    {list of CRITICAL/HIGH findings}                          |"
    "|                                                              |"
    "|  Loop continues to fix review findings.                      |"
    "|  Incrementing iteration, back to Step 7.                     |"
    "+--------------------------------------------------------------+"
    → Do NOT declare complete. Increment iteration, back to Step 7.
    → Inject review findings into recitation block as "must fix" items.

  ELIF review.verdict == "APPROVE WITH FIXES":
    Display:
    "+--------------------------------------------------------------+"
    "| REVIEW GATE — APPROVE WITH NOTES                              |"
    "+--------------------------------------------------------------+"
    "|                                                              |"
    "|  {N} non-critical findings noted in review.                  |"
    "|  Proceeding to completion.                                   |"
    "+--------------------------------------------------------------+"
    → Proceed to Step 13 (completion) with findings in banner.

  ELSE:
    → Clean pass. Proceed to Step 13.

ELSE IF files_changed == 0:
  → No files changed, skip review. Proceed to Step 13.
```

This means the loop literally cannot declare "DONE" if the reviewer finds
critical issues or accumulated over-engineering. It must fix them first.

**VERSION PERFORMANCE TRACKING:**

```
After review gate verdict:
  Record to .planning/version-performance.md:
  | {date} | v8.0 | loop-gate | {verdict} | {overridden?} | pending | Loop {LOOP_ID} |

  If loop was forced past a BLOCK (user said "FORCE CONTINUE"):
    override = yes → contributes to degradation signal tracking
  See: references/behavioral-directives.md § Version Performance Registry
```

---

## SABBATH REST — Context Rot Recovery

### Warning Triggers

1. **Output decline ≥ 50%** from baseline (first 3 iterations average)
2. **Repetitive behavior** — same action 3+ times without progress
3. **Instruction amnesia** — re-asking questions already answered
4. **Iteration count ≥ 15** — mandatory health check
5. **Circuit Breaker WARNING** on output_decline threshold

### Sabbath Rest Snapshot

When warning triggers, automatically save:

```markdown
## .planning/loops/sabbath-${LOOP_ID}-iter${N}.md

---
loop_id: ${LOOP_ID}
iteration: [N]
timestamp: [ISO]
reason: [context_rot | circuit_breaker | manual]
health_state: [current state]
circuit_breaker_state: [current CB state]
---

## State at Sabbath Rest

### Progress Summary
- Iterations completed: [N]
- Last successful action: [description]
- Current blocker: [if any]
- Health trajectory: [improving | stable | declining]

### Circuit Breaker Readings
- Stall counter: [N] / [threshold]
- Spin counter: [N] / [threshold]
- Output decline: [N]%

### Files Modified This Session
- [file]: [change summary]

### Approaches Tried (CRITICAL — don't repeat these)
1. [approach]: [result]
2. [approach]: [result]
3. [approach]: [result]

### Error History
- [error hash]: seen [N] times
- [error hash]: seen [N] times

### Next Steps (for resumed session)
1. [immediate next action — must be DIFFERENT from tried approaches]
2. [follow-up action]

### Skills Applied
- [skill]: [how it helped]

### Key Context to Restore
[Critical information the next session needs to know]

### Preserved Stop Signals (v6.0 — JetBrains Compaction Safety)
<!-- NEVER summarize these — they must survive compaction verbatim -->
- ERRORS: [exact error messages in code blocks]
- BLOCKED: [blocking reason if any]
- FAILED ATTEMPTS: [count] — [list of approaches tried]
- CIRCUIT BREAKER: [current state]
- TRIED AND FAILED: [approach 1: result], [approach 2: result]
```

**Compaction Protocol (v6.0):**

> **Research basis:** JetBrains "Cutting Through the Noise" (Dec 2025) — LLM summarization hides stop signals, extending runs ~15% past useful points.

```
WHEN context approaches limit and compaction triggers:

  BEFORE compaction:
    1. Extract from current context:
       - All error messages verbatim (in code blocks)
       - All BLOCKED/STUCK indicators
       - Failed attempt count and approach list
       - Circuit breaker state
       - Explicit "should stop" signals
    2. Write to Sabbath Rest snapshot under "Preserved Stop Signals"

  AFTER compaction:
    3. Verify preserved signals exist in compacted context
    4. If signals were lost → Re-inject preservation block
    5. Preservation block goes AFTER summary, not inside it

  RULE: The "Tried and Failed" list is the most critical signal.
  Without it, the resumed agent will retry the same failed approaches.
```

### Sabbath Rest Display

```
+------------------------------------------------------------------------------+
| SABBATH REST — CONTEXT REFRESH NEEDED                                        |
+------------------------------------------------------------------------------+
|                                                                              |
|  Context health declining at iteration [N].                                  |
|                                                                              |
|  Health: [DEGRADED]                                                          |
|  Circuit Breaker: [WARNING / TRIPPED]                                        |
|  Output Decline: [N]%                                                        |
|                                                                              |
|  Progress saved to:                                                          |
|    Loop file: .planning/loops/fire-loop-${LOOP_ID}.md                       |
|    Sabbath:   .planning/loops/sabbath-${LOOP_ID}-iter${N}.md                 |
|                                                                              |
|  TO CONTINUE (fresh context):                                                |
|    1. Run /clear or start new session                                        |
|    2. Run /fire-loop-resume ${LOOP_ID}                                      |
|                                                                              |
|  Or force continue (NOT recommended):                                        |
|    Reply "FORCE CONTINUE"                                                    |
|                                                                              |
+------------------------------------------------------------------------------+
```

---

## Step 13: Completion

When loop ends, update loop file with final result:

```markdown
## Final Result

- **Status:** [completed | max_iterations | circuit_break | blocked | sabbath_rest]
- **Total Iterations:** [N]
- **Duration:** [time]
- **Completion Promise Found:** [yes/no]

### Health Summary
- Time in PROGRESS: [N] iterations
- Time in STALLED: [N] iterations
- Time in SPINNING: [N] iterations
- Sabbath Rest Warnings: [count]
- Circuit Breaker Trips: [count]
- Approach Rotations: [count]

### Approaches Tried
1. [approach]: [outcome]
2. [approach]: [outcome]

### Files Changed
- [file list with changes]

### Patterns Discovered
[New patterns learned — consider /fire-add-new-skill]

### Lessons Learned
[What worked, what didn't, what to do differently next time]
```

Display completion banner:

```
+------------------------------------------------------------------------------+
| POWER LOOP COMPLETE                                                          |
+------------------------------------------------------------------------------+
|                                                                              |
|  Loop ID: ${LOOP_ID}                                                         |
|  Status: [Completed | Max Iterations | Circuit Break | Blocked]              |
|  Iterations: [N] / [MAX]                                                     |
|  Duration: [time]                                                            |
|                                                                              |
|  Health Profile:                                                             |
|    PROGRESS: [N] iters | STALLED: [N] | SPINNING: [N]                       |
|    Approach Rotations: [N]                                                   |
|    Circuit Breaker Trips: [N]                                                |
|                                                                              |
|  Files Changed: [count]                                                      |
|  Skills Applied: [count]                                                     |
|                                                                              |
|  New patterns discovered? Run:                                               |
|    /fire-add-new-skill                                                      |
|                                                                              |
+------------------------------------------------------------------------------+
```

---

## Examples

### Debug Until Tests Pass

```bash
/fire-loop "Fix the authentication bug in src/auth/login.ts. Run 'npm test' after each change. Output DONE when all tests pass." --max-iterations 30
```

### With Pattern Discovery

```bash
/fire-loop "Implement pagination for /api/users endpoint. Follow existing patterns. Tests must pass. Output COMPLETE when done." --discover --completion-promise "COMPLETE"
```

### Aggressive Mode (tighter thresholds)

```bash
/fire-loop "Fix CSS layout bug on mobile. Output DONE when responsive." --aggressive --max-iterations 20
```

### Without Circuit Breaker (manual control)

```bash
/fire-loop "Exploratory refactoring of auth module. Output DONE when clean." --no-circuit-breaker --max-iterations 40
```

---

## Best Practices

### 1. Clear Completion Criteria

```markdown
Bad:  "Fix the bug"
Good: "Fix the login bug. Tests in auth.test.ts must pass. Output FIXED."
```

### 2. Use --discover for Unfamiliar Tasks

```bash
/fire-loop "..." --discover
```

### 3. Honor Circuit Breaker Warnings

When the circuit breaker fires, it's telling you the current approach isn't working. Forcing through wastes iterations and degrades context.

### 4. Trust Approach Rotation

When SPINNING is detected, the system forces a different approach. Trust this — repeating the same failed approach will never produce a different result.

### 5. Sabbath Rest Is a Feature, Not a Failure

Taking a fresh context restart after 15-20 iterations is normal and healthy. The state is preserved — you lose nothing.

---

## Success Criteria

- [ ] Loop state file created with v3 fields
- [ ] Context engineering setup (recitation template, .powerignore)
- [ ] Skills library searched and cached
- [ ] CONSCIENCE.md updated with active loop
- [ ] Each iteration measured (files, errors, output)
- [ ] Error classification applied each iteration
- [ ] Circuit breaker monitoring active
- [ ] Approach rotation applied when SPINNING
- [ ] Recitation block composed each iteration
- [ ] Checkpoints saved at interval
- [ ] Sabbath Rest triggered when DEGRADED
- [ ] Completion promise respected (no false escapes)
- [ ] Post-loop review gate applied before declaring complete (v8.0)
- [ ] Final summary with health profile written

---

## References

- **Circuit Breaker:** `@references/circuit-breaker.md` — quantitative thresholds
- **Error Classification:** `@references/error-classification.md` — health state machine
- **Context Engineering:** `@references/context-engineering.md` — recitation + cache + exclusion
- **Decision-Time Guidance:** `@references/decision-time-guidance.md` — skills injection
- **Original:** Ralph Loop by Geoffrey Huntley (https://ghuntley.com/ralph/)
- **Related:** `/fire-loop-stop` — Cancel active loop
- **Related:** `/fire-loop-resume` — Resume from Sabbath Rest
- **Related:** `/fire-discover` — Pattern discovery
- **Related:** `/fire-debug` — Structured debugging (non-loop)
- **Skills:** `@skills-library/methodology/SABBATH_REST_PATTERN.md`
