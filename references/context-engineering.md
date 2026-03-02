# Context Engineering

> Techniques for maximizing context window effectiveness — recitation pattern, cache optimization, and context exclusion. Inspired by Manus AI's context engineering and Bolt.new's .bolt/ignore system.

---

## Overview

Context is the most precious resource in agentic execution. Every byte of context consumed by irrelevant information is a byte unavailable for reasoning. Context Engineering applies three strategies:

1. **Recitation Pattern** — Rewrite critical state into context each iteration to keep it in the attention window
2. **Cache-Friendly Ordering** — Structure prompts for maximum KV-cache reuse
3. **Context Exclusion** — Actively exclude irrelevant content from context

---

## 1. Recitation Pattern

### Problem

In long-running loops and multi-step execution, earlier context gets pushed out of the attention window. The agent "forgets" its plan, progress, and decisions — leading to circular behavior.

### Solution

At each iteration/step, **recite** (rewrite) the current state into the context. This keeps critical information in the active attention window.

```
BEFORE each iteration:

  recitation_block = compose_recitation(
    current_plan:    extract_current_tasks(BLUEPRINT.md),
    progress:        extract_completed_tasks(loop_file or SUMMARY),
    active_blockers: extract_open_blockers(BLOCKERS.md),
    key_decisions:   extract_recent_decisions(CONSCIENCE.md),
    approach:        current_approach_description
  )

  inject_into_context(recitation_block)
```

### Recitation Block Format

```markdown
---
DOMINION FLOW RECITATION — Iteration {N}
---

## Current Task
{task description from BLUEPRINT.md}

## Progress So Far
- [x] Task 1: {description} (commit: abc123)
- [x] Task 2: {description} (commit: def456)
- [ ] Task 3: {description} ← CURRENT
- [ ] Task 4: {description}

## Active Approach
{what we're currently trying and why}

## Key Decisions
- {decision 1}: {rationale}
- {decision 2}: {rationale}

## Open Blockers
- {blocker if any}

## Circuit Breaker
- State: {HEALTHY/WARNING/etc}
- Iterations without progress: {N}
- Error repeat count: {N}
---
```

### When to Recite

| Context | Frequency | Content |
|---------|-----------|---------|
| `/fire-loop` | Every iteration | Task + progress + approach + health state |
| `/fire-execute-plan` | Every task boundary | Plan progress + current task + deviations |
| `/fire-3-execute` | Every breath boundary | Phase progress + breath status + executor results |
| `/fire-debug` | Every debug cycle | Hypothesis + test results + evidence collected |

### Recitation Size Budget

Keep recitation blocks **under 30 lines**. If state is larger, summarize:

```
MAX_RECITATION_LINES = 30

compose_recitation():
  block = []
  block += current_task (max 5 lines)
  block += progress_checklist (max 8 lines)
  block += active_approach (max 5 lines)
  block += key_decisions (max 5 lines, last 3 only)
  block += blockers (max 3 lines)
  block += health_state (max 4 lines)

  IF block.lines > 30:
    compress: combine completed tasks into "X/Y tasks complete"
    compress: keep only most recent 2 decisions
```

---

## 2. Cache-Friendly Ordering

### Problem

LLM inference uses KV-cache to avoid recomputing attention for unchanged prefix tokens. If the prompt structure changes between iterations, the cache is invalidated and costs increase.

### Solution

Structure the context so that **stable content comes first** (system prompt, project context, skills) and **dynamic content comes last** (current iteration state, recitation block).

### Optimal Context Layout

```
┌────────────────────────────────────────────────────┐
│ STABLE PREFIX (rarely changes — high cache hit)    │
│                                                     │
│ 1. System prompt / CLAUDE.md                        │
│ 2. Project context (VISION.md summary)             │
│ 3. Skills library references (loaded at start)      │
│ 4. Plan context (BLUEPRINT.md — stable during execution) │
│                                                     │
├────────────────────────────────────────────────────┤
│ SEMI-STABLE MIDDLE (changes less frequently)        │
│                                                     │
│ 5. CONSCIENCE.md snapshot                                │
│ 6. DTG micro-instructions (change per task)         │
│ 7. Error classification state                       │
│                                                     │
├────────────────────────────────────────────────────┤
│ DYNAMIC SUFFIX (changes every iteration)            │
│                                                     │
│ 8. Recitation block (rewritten each iteration)      │
│ 9. Current iteration output                         │
│ 10. Error messages / test results                   │
│ 11. User messages                                   │
│                                                     │
└────────────────────────────────────────────────────┘
```

### Cache-Friendly Practices

| Practice | Benefit |
|----------|---------|
| Load skills at start, don't re-search | Stable prefix |
| Use append-only loop file | New data at end only |
| Don't reformat unchanged sections | Preserves token sequence |
| Put recitation block at consistent position | Predictable structure |

### Anti-Patterns (Cache-Hostile)

| Anti-Pattern | Problem |
|-------------|---------|
| Re-reading entire files each iteration | Bloats context with duplicate data |
| Changing prompt structure between iterations | Invalidates cache |
| Inserting new content in the middle | Shifts all subsequent tokens |
| Including full file contents when only a section changed | Wastes context space |

---

## 3. Context Exclusion (.powerignore)

### Problem

Large codebases contain many files irrelevant to the current task. Reading them wastes context. Build artifacts, node_modules, generated files, and large data files are especially wasteful.

### Solution

A `.powerignore` file (similar to `.gitignore`) tells Dominion Flow which files and directories to exclude from context when exploring the codebase.

### .powerignore Format

```gitignore
# Build artifacts
dist/
build/
.next/
out/

# Dependencies
node_modules/
vendor/
.venv/

# Generated files
*.min.js
*.min.css
*.map
*.lock
package-lock.json
yarn.lock

# Large data
*.sql.bak
*.dump
seeds/
fixtures/large-*

# IDE and OS
.vscode/
.idea/
.DS_Store
Thumbs.db

# Documentation (unless specifically needed)
docs/api-reference/
CHANGELOG.md

# Test snapshots (read only when testing)
__snapshots__/

# Dominion Flow artifacts (don't read our own tracking files during execution)
.planning/loops/
.planning/research/
```

### How .powerignore Is Used

```
WHEN Dominion Flow reads files (in any command):

  IF .powerignore exists in project root:
    exclusions = parse_powerignore(".powerignore")

    APPLY exclusions to:
      - /fire-map-codebase (exclude from initial scan)
      - /fire-discover (exclude from pattern search)
      - /fire-execute-plan (exclude from context loading)
      - /fire-loop (exclude from iteration file reads)
      - Any glob/grep operations during execution

  NEVER exclude:
    - Files explicitly listed in BLUEPRINT.md task files
    - Files referenced in error messages
    - Files the user specifically asks about
```

### Dynamic Exclusion

During execution, Dominion Flow can dynamically exclude files that aren't relevant:

```
dynamic_exclude(task):
  IF task.type == "frontend":
    exclude: src/api/**, prisma/**, src/models/**
    reason: "Backend files not relevant to frontend task"

  IF task.type == "backend":
    exclude: src/components/**, src/app/**, public/**
    reason: "Frontend files not relevant to backend task"

  IF task.type == "testing":
    include everything (tests may touch any file)
```

---

## Context Budget Tracking

### Awareness of Context Usage

```
track_context_usage():
  estimated_tokens = {
    system_prompt:    ~2000 tokens (stable),
    project_context:  ~1000 tokens (stable),
    plan_context:     ~500 tokens (stable per plan),
    skills_loaded:    ~300 tokens per skill,
    recitation_block: ~200 tokens (controlled),
    iteration_history: ~100 tokens per iteration,
    file_contents:    variable (biggest consumer),
    error_messages:   variable
  }

  total_estimate = sum(estimated_tokens)
  context_limit = 200000  # approximate

  IF total_estimate > context_limit * 0.7:
    WARNING: "Context 70% full — consider Sabbath Rest"

  IF total_estimate > context_limit * 0.85:
    CRITICAL: "Context 85% full — trigger Sabbath Rest"
```

### Context Hygiene Rules

| Rule | Purpose |
|------|---------|
| Don't re-read files already in context | Prevents duplication |
| Summarize large file reads (extract relevant section) | Reduces token usage |
| Clear iteration history older than 5 iterations | Keeps history manageable |
| Use recitation instead of keeping full history | Fixed-size state summary |
| Exclude build artifacts and generated files | Removes noise |

---

## Integration with Dominion Flow

### /fire-loop Integration

```markdown
Step 6.5 (NEW): Context Engineering Setup

1. Load .powerignore if present
2. Set up recitation template for the task
3. Search skills library once (cache the results)
4. Establish baseline output volume for circuit breaker

Step 7 (Execute Task) — Enhanced:

BEFORE each iteration:
  1. Compose recitation block from loop state
  2. Inject recitation into context
  3. Apply .powerignore to any file reads
  4. Track context usage estimate
```

### /fire-execute-plan Integration

```markdown
Step 4.5 (NEW): Context Setup

1. Load .powerignore
2. Pre-load plan-specific skills (DTG)
3. Set up recitation template for task tracking

Per-task execution:
  1. Recite plan progress before each task
  2. Apply dynamic exclusion based on task type
  3. Monitor context usage
```

---

## 4. Compaction Stop-Signal Preservation

> **Research basis (v6.0):** JetBrains "Cutting Through the Noise" (Dec 2025) found that LLM summarization during compaction smooths over stop signals — errors, BLOCKED indicators, and failure counts get lost. This extends agent runs by ~15%, often past the point where they should have stopped.

### Problem

When context approaches its limit, the system compacts (summarizes) earlier messages. Standard summarization optimizes for coherence, which means it:
- **Softens error messages** — "the build failed with 3 errors" becomes "there were some issues"
- **Drops failure counts** — "attempted 5 times, all failed" becomes "multiple attempts were made"
- **Smooths BLOCKED indicators** — explicit stop signals get paraphrased into continuable-sounding text
- **Loses verbatim error strings** — the exact error that would trigger pattern matching disappears

### Solution: Preserve Before Compact

```
WHEN compaction triggers (context > 85% full):

  BEFORE compaction:
    1. Extract and tag for preservation:
       - All error messages (verbatim, in code blocks)
       - All "BLOCKED" or "STUCK" indicators
       - Failed attempt count per approach
       - Explicit "should stop" signals
       - Circuit breaker state (WARNING/TRIPPED)
       - Approaches already tried (prevent re-investigation)

    2. Format as preservation block:
       ```
       ## Preserved Stop Signals (DO NOT SUMMARIZE)
       - ERROR: "{exact error message}"
       - BLOCKED: {reason}
       - FAILED ATTEMPTS: {count} — approaches: {list}
       - CIRCUIT BREAKER: {state}
       - TRIED AND FAILED: {approach 1}, {approach 2}, ...
       ```

  AFTER compaction:
    3. Verify preserved signals exist in compacted context
    4. If any signals were lost: re-inject the preservation block
    5. The preservation block must appear AFTER the summary, not inside it
```

### Integration Points

| Command | How to Apply |
|---------|-------------|
| `/fire-loop` | Before Sabbath Rest snapshot, extract stop signals |
| `/fire-debug` | Before checkpoint, preserve eliminated hypotheses verbatim |
| `/fire-3-execute` | Before breath summary, preserve blocker details |
| Any long session | If compaction triggers mid-task, preserve current error state |

### Anti-Pattern: The Smooth Summary

```
BAD (after compaction):
  "The authentication system was explored with several approaches.
   Some challenges were encountered but progress was made."

GOOD (after compaction):
  "Auth explored. 3 approaches tried, all failed:
   1. JWT middleware — TypeError: jwt.verify is not a function
   2. Session-based — BLOCKED: Redis not available in test env
   3. OAuth — 401 from provider, credentials expired
   CIRCUIT BREAKER: WARNING (stall_count: 3)
   DO NOT retry these approaches without new information."
```

### Actionable Error Preservation Protocol (v10.0)

> **Research basis (v10.0):** Manus AI "Context Engineering for AI Agents" (Feb 2026) —
> error preservation during context compaction improved recovery rate by preventing
> repeated failed approaches. Errors are the most valuable context — they tell you
> what NOT to do.

**MANDATORY: Before any compaction event (Sabbath Rest, /compact, auto-compact):**

```
1. SCAN current context for:
   a. Error messages (grep for ERROR, FAIL, TypeError, etc.)
   b. Approach descriptions that were tried
   c. Circuit breaker state and counters
   d. Confidence scores from last 3 iterations
   e. Files that were modified (git diff --name-only)

2. WRITE preservation block to loop file or .planning/context-preserved.md:

   ## Context Preservation Block (auto-generated)
   timestamp: {ISO timestamp}
   trigger: {compaction | sabbath_rest | manual}

   ### Errors (verbatim, do NOT paraphrase)
   ```
   {exact error message 1}
   {exact error message 2}
   ```

   ### Failed Approaches (DO NOT RETRY without new information)
   1. {approach} — {why it failed}
   2. {approach} — {why it failed}

   ### Circuit Breaker State
   stall: {N}/{threshold} | spin: {N}/{threshold} | decline: {N}%

   ### Working State
   - Last successful change: {file:line}
   - Current hypothesis: {what was being tried}
   - Confidence: {score}/100

3. VERIFY the preservation block is included in the compacted context
   IF missing: re-inject it as the first thing after compaction
```

**Key principle:** Errors are more valuable than successes for context. A success
tells you what worked (which you can rediscover). An error tells you what NOT to do
(which you'll waste iterations rediscovering without preservation).

---

## 5. Difficulty-Aware Routing Tiers (v7.0)

> **Research basis:** Difficulty-Aware Agent Orchestration (Sep 2025) — +11.21% accuracy at 64% cost

Not every task needs the full pipeline. Routing by difficulty saves context and time:

| Tier | Steps Skipped | Token Savings | Example Tasks |
|------|--------------|---------------|---------------|
| SIMPLE | 7.1 (episodic), 8.5 (directives), 8.8 (rewards) | ~500 tokens/iter | Typos, renames, config changes |
| MODERATE | None | 0 | Multi-file features, partial skill match |
| COMPLEX | None + adds double-check | +200 tokens/iter | Architecture changes, security, 6+ files |

**Classification signals:**
- File count estimate (1 = SIMPLE, 2-5 = MODERATE, 6+ = COMPLEX)
- Skill match quality (exact = SIMPLE, partial = MODERATE, none = COMPLEX)
- Security/architecture implications → always COMPLEX
- Cross-cutting concerns → always COMPLEX

**Cost analysis:** ~60% of tasks in typical sessions are SIMPLE. Skipping 3 steps saves ~500 tokens per iteration, which compounds across 5-10 iterations per task.

---

---

## 6. Active Context Compression (v10.0 — ACON)

> **Research basis (v10.0):** ACON "Active Context Compression" (2025-2026, score 4.85) —
> 26-54% token reduction via selective compression. Instead of treating all context equally,
> ACON scores each context segment by relevance to the current task and compresses
> low-relevance segments aggressively while preserving high-relevance segments verbatim.
> Focus (ACL 2025) adds "active forgetting" — proactively dropping irrelevant context
> rather than waiting for the window to fill.

### Problem

Current context management (recitation + .powerignore + cache ordering) is passive — it
controls what enters context but doesn't compress what's already there. As iterations
accumulate, even well-structured context fills the window with diminishing-relevance content.

### Solution: Relevance-Scored Compression

```
EVERY 3 iterations (not every iteration — compression has overhead):

  1. SCORE each context segment by relevance to current task:
     - Current task description → CRITICAL (never compress)
     - Error messages from last 2 iterations → HIGH (preserve verbatim)
     - Recitation block → HIGH (preserve verbatim)
     - Skills loaded for current task → MEDIUM (compress to key points)
     - File contents read >3 iterations ago → LOW (compress to summary)
     - Iteration history older than 5 iterations → LOW (compress to one line each)
     - Successful approach details (already committed) → LOW (compress to commit hash)

  2. COMPRESS based on score:
     - CRITICAL: keep 100% — do not touch
     - HIGH: keep 100% — preserve verbatim
     - MEDIUM: keep ~50% — extract key patterns, drop examples
     - LOW: keep ~15% — one-line summary per segment

  3. INJECT compressed context as replacement recitation block

  Token savings formula:
    savings = sum(segment_tokens * (1 - keep_percentage))
    Expected: 26-54% reduction per compression pass
```

### Active Forgetting Triggers (Focus)

Don't wait for context to fill — proactively drop content when:

```
FORGET when:
  - A file was read but never referenced again for 3+ iterations
  - A skill was loaded but not applied (no citation in code)
  - An error was resolved (committed fix exists) — compress to one-line summary
  - An approach was tried and abandoned — keep only the failure reason, drop details

NEVER forget:
  - Current task description
  - Error messages from current/last iteration
  - Circuit breaker state
  - Approaches that FAILED (what NOT to do is more valuable than what succeeded)
  - Files actively being edited in current iteration
```

### Integration with Sabbath Rest

ACON compression extends the useful life of a context window before Sabbath Rest triggers:

```
WITHOUT ACON: ~15 iterations before context rot → Sabbath Rest
WITH ACON:    ~25 iterations before context rot → Sabbath Rest

Mechanism: ACON compression at iterations 3, 6, 9, 12, 15, 18, 21, 24...
Each pass recovers 26-54% of accumulated low-value context.
The Sabbath Rest threshold (output decline >70%) is reached later because
the output quality degrades more slowly with compressed context.
```

### PAACE Integration (Plan-Aware Context)

> **Research basis (v10.0):** PAACE "Plan-Aware Agent Context Engineering" (2025, score 4.70) —
> context compression should be plan-aware. Segments related to upcoming plan tasks should
> be preserved even if not currently relevant, because they'll be needed soon.

```
WHEN compressing context, check BLUEPRINT.md for upcoming tasks:

  upcoming_tasks = extract_next_3_tasks(BLUEPRINT.md)
  upcoming_keywords = extract_keywords(upcoming_tasks)

  FOR each context segment scored LOW:
    IF segment contains keywords matching upcoming tasks:
      → Upgrade to MEDIUM (keep ~50%) — will be needed soon
      → Tag: "Preserved for upcoming Task {N}"
```

---

## References

- **Recitation:** Manus AI "todo.md rewrite" pattern (restate plan each iteration)
- **Cache optimization:** Manus AI KV-cache strategy (87% cache hit rate, append-only)
- **Context exclusion:** Bolt.new `.bolt/ignore` pattern
- **Compaction safety:** JetBrains "Cutting Through the Noise" (Dec 2025) — summarization hides stop signals
- **Difficulty routing:** Difficulty-Aware Agent Orchestration (Sep 2025) — route by complexity
- **Active compression:** ACON (2025-2026) — 26-54% token reduction via relevance-scored compression
- **Plan-aware context:** PAACE (2025) — preserve upcoming-task-relevant context during compression
- **Active forgetting:** Focus (ACL 2025) — proactively drop irrelevant context
- **Related:** `references/circuit-breaker.md` — output decline threshold uses context awareness
- **Related:** `references/error-classification.md` — DEGRADED state is context-rot driven
