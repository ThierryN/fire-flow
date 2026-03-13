# Difficulty-Aware Agent Routing - Smart Model Selection for Cost & Speed

## The Problem

Dominion Flow currently spawns the SAME agent type (Opus) for ALL tasks regardless of complexity.
A simple config file rename gets the same 200K context Opus agent as a complex multi-file
architecture refactor. This wastes:

- **Tokens**: Simple tasks burn expensive Opus tokens unnecessarily
- **Time**: Large models are slower for trivial operations
- **Context budget**: Small tasks don't need 200K context windows
- **Cost**: DAAO research shows 64% cost reduction with smart routing

### Why It Was Hard

- No existing framework classifies task difficulty BEFORE execution
- "Difficulty" is subjective - what signals actually predict complexity?
- Model capability boundaries aren't well documented (when does Haiku fail?)
- Dynamic re-estimation mid-execution is completely novel

### Impact

- 3x-10x cost reduction on simple tasks
- Faster execution for trivial operations
- Better context utilization (small context = less noise)
- Opus reserved for tasks that genuinely need deep reasoning

---

## The Solution

### Root Cause

One-size-fits-all agent spawning. The orchestrator doesn't classify task difficulty
before selecting which model to use.

### How to Fix: 3-Tier Routing System

**Based on DAAO paper (arxiv:2509.11079) which achieved 64% cost reduction and
11.21% accuracy improvement over homogeneous approaches.**

### Tier 1: Difficulty Classification

Before spawning any agent, classify the task using these signals:

```yaml
difficulty_signals:
  # File Scope (0-1)
  files_to_modify: 1        # 1 file = 0.1, 5+ files = 0.8
  cross_cutting: false      # auth+db+UI = 0.9, single layer = 0.2

  # Complexity (0-1)
  dependency_count: 2       # 0-2 = 0.2, 3-5 = 0.5, 6+ = 0.9
  requires_research: false  # true = +0.3
  novel_pattern: false      # no existing skill matches = +0.3

  # Historical (0-1)
  similar_task_error_rate: 0.1  # from past executions
  plan_uncertainty: 0.3     # from planning phase confidence

  # Calculated
  difficulty_score: 0.25    # weighted average
```

**Difficulty Formula:**
```
d = (file_scope * 0.25) + (complexity * 0.35) + (historical * 0.20) + (uncertainty * 0.20)
```

### Tier 2: Model Routing

| Difficulty Score | Model | Context Budget | Use Case |
|------------------|-------|----------------|----------|
| d < 0.30 | **Haiku** | 8K tokens | Config changes, renames, simple CRUD, boilerplate |
| 0.30 <= d < 0.65 | **Sonnet** | 32K tokens | Feature implementation, standard patterns, testing |
| d >= 0.65 | **Opus** | 200K tokens | Architecture, complex debugging, multi-file refactors |

### Tier 3: Dynamic Re-estimation (Novel)

After each breath, RE-ESTIMATE remaining task difficulty:

```markdown
## Re-estimation Rules

IF executor finished faster than expected + high confidence (>0.8):
  -> Downgrade remaining similar tasks by 0.15
  -> "This pattern is easier than estimated"

IF executor hit blockers OR confidence < 0.5:
  -> Upgrade remaining similar tasks by 0.20
  -> "This pattern is harder than estimated"

IF executor discovered new dependency:
  -> Re-classify affected tasks
  -> May promote Haiku tasks to Sonnet

IF executor applied a skill successfully:
  -> Reduce difficulty for similar future tasks by 0.10
  -> "Skills library makes this easier"
```

### Code Example: Integration with power-2-plan

```yaml
# In BLUEPRINT.md, each task gets difficulty metadata
tasks:
  - id: "3-01"
    name: "Create user model"
    difficulty:
      score: 0.22
      signals:
        files: 1
        cross_cutting: false
        dependencies: 1
        novel: false
      routing: haiku
      context_budget: 8K

  - id: "3-02"
    name: "Implement JWT auth with refresh rotation"
    difficulty:
      score: 0.58
      signals:
        files: 4
        cross_cutting: true  # middleware + routes + models
        dependencies: 3
        novel: false  # skill exists: jwt-refresh-rotation
      routing: sonnet
      context_budget: 32K

  - id: "3-03"
    name: "Design WebSocket auth with room-level permissions"
    difficulty:
      score: 0.82
      signals:
        files: 6
        cross_cutting: true  # real-time + auth + rooms + events
        dependencies: 5
        novel: true  # no matching skill
      routing: opus
      context_budget: 200K
```

### Code Example: Integration with fire-3-execute

```markdown
### Step 4.5: Difficulty-Aware Agent Spawning

For each plan in breath:
  1. Read difficulty.routing from BLUEPRINT.md
  2. Spawn agent with appropriate model:

  Task(
    prompt: filled_executor_prompt,
    subagent_type: "general-purpose",
    model: difficulty.routing,  # "haiku" | "sonnet" | "opus"
    description: "Execute plan {N}-{NN}"
  )

  3. Set context budget based on difficulty:
     - Haiku: minimal context injection (plan + current file only)
     - Sonnet: standard context (plan + related files + skills)
     - Opus: full context (plan + all related + skills + decision log + assumptions)
```

---

## Testing the Fix

### Before (All Opus)
```
Phase 3 Execution:
  Plan 3-01 (config rename): Opus, 200K context, $0.15, 45 seconds
  Plan 3-02 (JWT auth):      Opus, 200K context, $0.15, 120 seconds
  Plan 3-03 (WebSocket):     Opus, 200K context, $0.15, 300 seconds
  Total: $0.45, ~8 minutes
```

### After (Smart Routing)
```
Phase 3 Execution:
  Plan 3-01 (config rename): Haiku, 8K context, $0.001, 5 seconds
  Plan 3-02 (JWT auth):      Sonnet, 32K context, $0.03, 60 seconds
  Plan 3-03 (WebSocket):     Opus, 200K context, $0.15, 300 seconds
  Total: $0.181, ~6 minutes  (60% cost reduction, 25% faster)
```

### Validation Criteria
- [ ] Simple tasks (d < 0.3) succeed with Haiku 90%+ of the time
- [ ] Medium tasks (0.3-0.65) succeed with Sonnet 85%+ of the time
- [ ] Complex tasks (d > 0.65) maintain current Opus success rate
- [ ] Dynamic re-estimation improves accuracy over 3+ breaths
- [ ] Total cost per phase decreases by 40-60%

---

## Prevention

- Always classify difficulty BEFORE spawning agents
- Review difficulty scores during planning phase
- Track actual vs estimated difficulty for calibration
- Update difficulty signals based on project history

---

## Related Patterns

- [CONFIDENCE_ANNOTATION_PATTERN](./CONFIDENCE_ANNOTATION_PATTERN.md) - Feeds uncertainty into difficulty
- [HEARTBEAT_PROTOCOL](./HEARTBEAT_PROTOCOL.md) - Monitors agent health per tier
- [EVOLUTIONARY_SKILL_SYNTHESIS](./EVOLUTIONARY_SKILL_SYNTHESIS.md) - Skills reduce difficulty scores
- complexity-metrics/complexity-divider - Existing complexity assessment

---

## Common Mistakes to Avoid

- ❌ **Always using Opus "to be safe"** - wastes 10x cost on trivial tasks
- ❌ **Using Haiku for cross-cutting tasks** - will fail and waste retry cost
- ❌ **Not re-estimating after first breath** - initial estimates are often wrong
- ❌ **Ignoring historical data** - past error rates are the best predictor
- ❌ **Routing based on task NAME only** - "create model" could be simple or complex

---

## Resources

- DAAO paper: https://arxiv.org/abs/2509.11079
- Anthropic model comparison: https://docs.anthropic.com/en/docs/about-claude/models
- Production Agentic AI best practices: https://arxiv.org/abs/2512.08769

---

## Time to Implement

**Phase 1 (metadata only):** 30 minutes - Add difficulty fields to plan template
**Phase 2 (routing):** 2 hours - Wire model selection into fire-3-execute
**Phase 3 (re-estimation):** 3 hours - Add dynamic adjustment after each breath

## Difficulty Level

⭐⭐⭐ (3/5) - Conceptually straightforward, but calibrating thresholds requires iteration

---

**Author Notes:**
The DAAO paper achieved 64% cost reduction AND 11% accuracy improvement. The key insight
is that small models often OUTPERFORM large models on simple tasks because they have less
context noise and faster inference. Don't assume bigger = better for every task.

The dynamic re-estimation (Tier 3) is our novel contribution - no paper proposes adjusting
difficulty mid-execution based on actual performance. This creates a feedback loop where
the system gets better at routing over time.
