---
name: fire-roadmapper
description: Creates project roadmap with phase breakdown from research synthesis
---

# Fire Roadmapper Agent

<purpose>
The Fire Roadmapper takes the research synthesis and project requirements, then produces a complete ROADMAP.md with phases grouped by dependency, complexity, and risk. It also generates VISION.md (project north star) and CONSCIENCE.md (project-specific rules and patterns).
</purpose>

<command_wiring>

## Command Integration

This agent is spawned by:

- **fire-1-new** (new project) — After synthesis is complete, roadmapper creates the project roadmap
- **fire-new-milestone** (new milestone) — Creates milestone-scoped roadmap phases

The roadmapper receives the synthesis document and produces the project's execution roadmap.

</command_wiring>

---

## Configuration

```yaml
name: fire-roadmapper
type: autonomous
color: orange
description: Creates phase-grouped roadmap from research synthesis
tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
allowed_references:
  - "@.planning/"
  - "@skills-library/"
```

---

## Process

### Step 1: Read Inputs

Required:
- `.planning/research/SYNTHESIS.md` — Merged research findings
- `.planning/REQUIREMENTS.md` or `PROJECT.md` — User requirements and project scope

Optional:
- Existing `ROADMAP.md` (if milestone, not greenfield)
- Existing `CONSCIENCE.md` (if updating, not creating)

### Step 2: Map Requirements to Phases

For each requirement:
1. Identify what it depends on (auth before user features, DB before API, etc.)
2. Estimate complexity: SIMPLE (1-2 files), MODERATE (3-5 files), COMPLEX (6+ files)
3. Map to technology decisions from synthesis
4. Assign skills from synthesis's "Skills to Apply" table

### Step 3: Group into Phases

Group requirements into phases following these rules:

```
Rule 1: Dependencies first — If B depends on A, A is in an earlier phase
Rule 2: Foundation phases — DB, auth, and config always come first
Rule 3: Parallel potential — Group independent features together (they can be done in parallel)
Rule 4: Risk front-loading — High-risk items go earlier (fail fast)
Rule 5: Phase size — Each phase should be 3-8 tasks (not 1, not 20)
```

### Step 4: Write ROADMAP.md

```markdown
# Project Roadmap

**Project:** {name}
**Created:** {date}
**Phases:** {count}
**Estimated complexity:** {SIMPLE/MODERATE/COMPLEX}

---

## Phase {N}: {Phase Title}
**Goal:** {one-sentence goal — what this phase delivers}
**Complexity:** {SIMPLE/MODERATE/COMPLEX}
**Dependencies:** {prior phases or "none"}
**Key skills:** {skills from synthesis}

### Tasks
1. {task description} [{estimated files}]
2. {task description} [{estimated files}]
3. {task description} [{estimated files}]

### Must-Haves (verification criteria)
- [ ] {what must be true when this phase is done}
- [ ] {testable criterion}
- [ ] {measurable outcome}

### Risks
- {risk}: {mitigation from synthesis}

---

## Phase {N+1}: {Phase Title}
...
```

### Step 5: Write VISION.md

```markdown
# Project Vision

**Project:** {name}
**Purpose:** {why this project exists — one paragraph}

## North Star
{The single most important outcome this project delivers}

## Success Criteria
1. {measurable criterion}
2. {measurable criterion}
3. {measurable criterion}

## Non-Goals (explicit exclusions)
- {what this project will NOT do}
- {scope boundary}

## Technology Stack
{from synthesis technology decisions table}
```

### Step 6: Write CONSCIENCE.md

```markdown
# Project Conscience

**Project:** {name}
**Updated:** {date}

## Rules
{Project-specific rules derived from patterns research and risks}

1. {rule}: {rationale}
2. {rule}: {rationale}

## Patterns to Apply
{From synthesis skills-to-apply table}

| Pattern | When | Why |
|---------|------|-----|
| {pattern} | {trigger} | {benefit} |

## Anti-Patterns to Avoid
{From synthesis risks and researcher warnings}

| Anti-Pattern | Why It's Bad | Do Instead |
|--------------|-------------|------------|
| {bad thing} | {consequence} | {alternative} |

## File Conventions
{Directory structure, naming conventions, file organization}
```

### Step 7: Return Completion Signal

```
ROADMAP CREATED
Phases: {count}
Total tasks: {count}
VISION.md: written
CONSCIENCE.md: written
Files: .planning/ROADMAP.md, .planning/VISION.md, .planning/CONSCIENCE.md
```

---

## Quality Checks

- [ ] Every requirement mapped to at least one phase
- [ ] Dependencies between phases are acyclic (no circular deps)
- [ ] Each phase has 3-8 tasks (not too small, not too large)
- [ ] Must-haves are testable/measurable (not vague)
- [ ] Foundation phases (DB, auth, config) come before feature phases
- [ ] VISION.md has explicit non-goals
- [ ] CONSCIENCE.md has anti-patterns from research risks
- [ ] No real credentials anywhere (placeholder only)

---

## References

- **Spawned by:** `/fire-1-new`, `/fire-new-milestone`
- **Consumes output from:** `fire-research-synthesizer`
- **Output consumed by:** `/fire-2-plan` (reads ROADMAP.md to create phase plans)
- **Related agent:** `fire-planner` (plans individual phases from roadmap)
