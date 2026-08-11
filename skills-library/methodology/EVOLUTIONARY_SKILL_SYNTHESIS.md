---
name: evolutionary-skill-synthesis
category: methodology
version: 1.0.0
contributed: 2026-02-17
contributor: dominion-flow-research
last_updated: 2026-02-17
tags: [self-evolving, skills, automation, cascade, lineage, novel]
difficulty: hard
usage_count: 1
success_rate: 100
status: activated
research_basis: "CASCADE (arxiv:2512.23880), GEA (arxiv:2602.04837), AgentEvolver (arxiv:2511.10395), Agent Skills Survey (arxiv:2602.12430)"
---

# Evolutionary Skill Synthesis

## Problem

Skills are currently created manually via `/fire-add-new-skill`. This has three issues:
1. **Capture gap**: Most valuable patterns are never recorded (developers forget, too busy)
2. **Staleness**: Skills don't evolve based on usage feedback
3. **Isolation**: Skills from one project don't automatically benefit other projects

The result: a static library that grows slowly and may contain outdated patterns.

## Solution Pattern

### Phase 1: Automatic Skill Extraction (from CASCADE)

After every successful phase execution, extract candidate skills:

```markdown
## Skill Extraction Pipeline

1. ANALYZE execution trace:
   - What code patterns were created?
   - What debugging strategies worked?
   - What architectural decisions were made?
   - What workarounds were applied?

2. IDENTIFY reusable patterns:
   - Pattern appears generalizable (not project-specific)
   - Pattern solved a non-trivial problem
   - Pattern involved >3 files or >30 minutes of work
   - Pattern required research or multiple attempts

3. SYNTHESIZE candidate skill:
   - Extract problem description
   - Extract solution pattern
   - Generate code examples (abstracted from project specifics)
   - Determine category and tags
   - Set initial confidence based on evidence

4. QUARANTINE for review:
   - Skill goes to `skills-library/_quarantine/`
   - Security scan runs (no command injection, no credentials)
   - Duplicate check against existing library
   - Human notification: "New skill candidate discovered"
```

### Phase 2: Group Evolution (from GEA)

When running swarm mode with multiple executors:

```markdown
## Group Evolution Pipeline

1. COLLECT evolutionary traces from each executor:
   - Code patches applied
   - Task execution logs
   - Tool invocation patterns
   - Failure modes and recoveries

2. AGGREGATE traces across the breath:
   - Find common patterns across executors
   - Identify successful strategies that one executor used but others didn't
   - Detect complementary approaches

3. GENERATE evolution directives:
   - "Executor A's retry strategy should be shared with all executors"
   - "The API pattern from executor B is more robust than executor C's"
   - "All executors should use the connection pool pattern from skills library"

4. PRODUCE framework patches:
   - Update executor prompts for next breath
   - Inject successful patterns as context
   - Remove patterns that consistently failed
```

### Phase 3: Skill Lineage Tracking (Novel)

Every skill (auto-generated or manual) maintains evolutionary metadata:

```yaml
lineage:
  created_from: "Phase 3, Plan 3-02, MERN-LMS project"
  parent_skills: ["jwt-refresh-rotation", "express-middleware-pattern"]
  derived_skills: ["websocket-auth-pattern"]  # skills that built on this one
  projects_used_in:
    - project: "my-other-project"
      times_applied: 7
      success_rate: 100%
    - project: "binamu-power"
      times_applied: 2
      success_rate: 50%
  fitness_score: 0.85  # calculated from usage + success
  generation: 2  # how many times this skill has been refined
  last_evolution: "2026-02-17"
  evolution_history:
    - v1.0.0: "Initial extraction from JWT auth implementation"
    - v1.1.0: "Refined after failure in WebSocket context"
    - v1.2.0: "Added concurrent refresh handling after race condition discovery"
```

### Phase 4: Fitness-Based Lifecycle

Skills have a lifecycle managed by fitness scores:

```
QUARANTINE (new, unreviewed)
    |
    v [human approves]
ACTIVE (available for use)
    |
    |--> [fitness > 0.9, used > 10x] --> CORE (always loaded)
    |
    |--> [fitness < 0.3, not used > 30 days] --> ARCHIVED
    |
    |--> [security issue found] --> DEPRECATED (with warning)
```

**Fitness Score Calculation:**
```
fitness = (success_rate * 0.4) + (usage_frequency * 0.3) + (project_diversity * 0.2) + (recency * 0.1)
```

Where:
- `success_rate`: % of times skill was applied and task succeeded
- `usage_frequency`: normalized count of applications
- `project_diversity`: number of distinct projects using it
- `recency`: decay factor (skills used recently score higher)

### Security Gate (from Agent Skills Survey)

26.1% of auto-generated skills contain vulnerabilities. Apply 4-tier trust:

| Trust Level | Source | Permissions |
|-------------|--------|-------------|
| CORE | Built into Dominion Flow | Full access |
| VERIFIED | User-created, security-scanned | Full project access |
| COMMUNITY | Shared/imported | Sandboxed, read-only default |
| QUARANTINE | Auto-generated | Review required |

**Security scan checks:**
- No `exec()`, `eval()`, `child_process` in code examples
- No hardcoded credentials or API keys
- No file system access outside project directory
- No network requests to unknown domains
- No destructive operations (DROP, DELETE, rm -rf)

## Implementation in Dominion Flow

### In fire-3-execute (after Step 9 verification):
```markdown
### Step 10.5: Skill Extraction (Auto)

After successful verification:
1. Analyze execution summaries for extractable patterns
2. Run skill extraction pipeline
3. If candidates found:
   - Create quarantine files
   - Log in SKILLS-INDEX.md under "Pending Review"
   - Notify user: "N new skill candidates discovered"
```

### In fire-loop (after completion):
```markdown
### Patterns Discovered (enhanced)

Instead of just listing patterns, auto-generate skill candidates:

| Pattern | Confidence | Quarantine? |
|---------|------------|-------------|
| Retry with exponential backoff | 0.88 | Yes - created |
| Custom WebSocket auth | 0.55 | No - too project-specific |
```

## When to Use

- After every successful phase execution (automatic)
- After long debug sessions with novel solutions (automatic)
- During swarm mode execution (group evolution)
- When `/fire-discover` finds no matching skills for a common pattern

## When NOT to Use

- For project-specific configurations (database schemas, env vars)
- For trivial patterns (basic CRUD, simple routing)
- When the solution is a workaround, not a proper fix

## Common Mistakes

- Extracting project-specific code as "general" skills
- Not running security scan on auto-generated skills
- Promoting skills to CORE too quickly (wait for multi-project validation)
- Archiving skills that are rarely used but highly valuable when needed

## Related Skills

- [CONFIDENCE_ANNOTATION_PATTERN](./CONFIDENCE_ANNOTATION_PATTERN.md) - Confidence for skill quality
- [HEARTBEAT_PROTOCOL](./HEARTBEAT_PROTOCOL.md) - Agent monitoring during extraction

## References

- CASCADE: https://arxiv.org/abs/2512.23880
- GEA: https://arxiv.org/abs/2602.04837
- AgentEvolver: https://arxiv.org/abs/2511.10395
- Agent Skills Survey: https://arxiv.org/abs/2602.12430
