---
description: Plan a phase with skills library access and WARRIOR validation
---

# /fire-2-plan

> Plan phase N with skills library integration and WARRIOR validation

---

## Purpose

Create detailed execution plans for a specified phase by combining Dominion Flow's structured planning with skills library access, honesty protocols, and validation requirements. Plans are reviewed by a plan-checker before approval.

---

## Arguments

```yaml
arguments:
  phase_number:
    required: true
    type: integer
    description: "Phase number to plan (e.g., 1, 2, 3)"
    example: "/fire-2-plan 3"

optional_flags:
  --gaps: "Plan only for gaps identified in verification"
  --research-first: "Force research phase before planning"
  --skip-checker: "Skip plan-checker validation (not recommended)"
```

---

## Process

### Step 0.5: Prompt Enhancer — Codebase Convention Scan (v11.0)

> conventions BEFORE planning enriches the planner's context with actual patterns,
> reducing hallucinated approaches and increasing plan accuracy.

Before any validation or planning, scan the project for conventions that should
inform the planner:

```
SCAN (quick — max 60 seconds):

1. Package manager: check for bun.lockb / pnpm-lock.yaml / yarn.lock / package-lock.json
2. Test framework: grep for jest.config / vitest.config / playwright.config / .mocharc
3. Naming patterns: sample 3 source files — camelCase vs snake_case, barrel exports
4. Error handling: grep for common error patterns (try/catch, .catch, Result types)
5. API style: check for REST routes / GraphQL schema / tRPC routers
6. State management: grep for zustand / redux / context / signals

OUTPUT — codebase_conventions block injected into planner context:

<codebase_conventions>
  package_manager: {bun | pnpm | yarn | npm}
  test_framework: {jest | vitest | playwright | none detected}
  naming: {camelCase | snake_case | mixed}
  error_pattern: {try-catch | Result type | .catch chains}
  api_style: {REST | GraphQL | tRPC | mixed}
  state: {zustand | redux | context | none detected}
  notes: [any other conventions discovered]
</codebase_conventions>
```

**Skip condition:** If `--gaps` flag is set (re-planning for gaps), conventions are
already known from the first plan. Skip this step.

### Step 1: Environment Validation

```
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
                         DOMINION FLOW > PHASE {N} PLANNING
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
```

**Validate:**
1. `.planning/` directory exists
2. `CONSCIENCE.md` exists and is readable
3. `VISION.md` exists with phase {N} defined
4. Phase number is valid (within roadmap range)
5. Previous phases are complete (if dependencies exist)

**Parse Arguments:**
```bash
# Extract phase number
PHASE_NUM={argument}

# Check for flags
GAPS_ONLY={--gaps flag present}
RESEARCH_FGTAT={--research-first flag present}
```

### Step 2: Load Context

**Required Reading:**
```markdown
@.planning/CONSCIENCE.md      # Current project position
@.planning/VISION.md    # Phase objectives and scope
```

**Extract from ROADMAP:**
- Phase name and objective
- Must-have features for this phase
- Dependencies on previous phases
- Estimated complexity

### Step 3: WARRIOR Enhancement - Honesty Pre-Check

**MANDATORY: Spawn fire-planner with honesty protocol.**

Before ANY planning, the planner must answer:

```markdown
## Pre-Planning Honesty Check

### Question 1: What do I know about implementing this phase?
- [List specific knowledge areas]
- [Technologies familiar with]
- [Relevant skills in library]

### Question 2: What don't I know?
- [Gaps in knowledge]
- [Technologies unfamiliar]
- [Edge cases uncertain about]

### Question 3: Am I tempted to fake or rush?
- [ ] Not tempted - confidence is grounded
- [ ] Tempted in area: ___ (adding research first)
```

**If Q3 reveals temptation:** Route to research before planning.

### Step 4: Research Phase (If Needed)

**Trigger Conditions:**
- `--research-first` flag provided
- Honesty check reveals knowledge gaps
- Phase involves unfamiliar technology
- No existing `{N}-RESEARCH.md` file

**Spawn fire-researcher:**

```
â—† Spawning fire-researcher for Phase {N}...
  âš¡ Searching skills library for relevant patterns
  âš¡ Researching unfamiliar technologies
  âš¡ Documenting findings
```

**Researcher Tasks:**
1. Search skills library: `/fire-search "[phase topic]"`
2. Load relevant skills: `@skills-library/{category}/{skill}.md`
3. WebSearch for current best practices (if skills insufficient)
4. Create `{N}-RESEARCH.md` with findings

**Research Output:**
```
.planning/phases/{N}-{name}/{N}-RESEARCH.md
```

### Step 4.5: Failure Memory Query (MemP v9.1)

> by surfacing relevant past failures before planning begins.

Before spawning the planner, search vector memory for relevant past failures.

**Query Qdrant:**
```bash
# Search for failure patterns related to this phase
npm run search-failures -- "{phase_name} {technology_stack}" --limit 5

# Also search for debug resolutions
npm run search -- "{phase_description}" --type failure_pattern,debug_resolution --limit 5
```

**If results found (similarity > 0.6):**

Add to fire-planner's context block:

```
<failure_memory>
The following past failures are relevant to this phase. Plan to AVOID repeating these:

{For each result:}
- **{failure_title}** ({project}, {date}):
  Root cause: {root_cause}
  Fix: {resolution}
  Lesson: {lesson_learned}
</failure_memory>
```

**If Qdrant unavailable:** Skip gracefully — same degradation pattern as fire-loop v9.0.
Log: "Qdrant unavailable — planning without failure memory (non-blocking)"

### Step 4.75: Architecture Blueprint Auto-Suggestion (v10.0)

> eliminated 30-60 minutes of research per session by providing pre-built component hierarchies.

Before spawning the planner, search the skills library for matching architecture blueprints.

**Search skills library:**
```bash
# Extract keywords from phase description
keywords = extract_keywords(MEMORY.md phase description)

# Search for architecture patterns
/fire-search "{keywords}" --scope general --category patterns-standards
/fire-search "{keywords}" --scope general --category methodology
```

**If architecture blueprints match (similarity > 60%):**

Display:
```
◆ Architecture blueprints found:
  ├─ python-desktop-app-architecture (92% match)
  ├─ realtime-monitoring-dashboard (78% match)
  └─ fullstack-bible-study-platform (65% match)

  Apply as planning accelerators? [Yes / No / View]
```

**If Yes:** Inject blueprint component hierarchy, dependency list, and wiring
patterns into the planner's `<skills_context>` block (Step 5).

**If No:** Continue without blueprints.

**If no matches:** Skip silently — same degradation as Qdrant unavailable.

### Step 5: Spawn fire-planner

```
â—† Spawning fire-planner for Phase {N}...
```

**Planner Context Injection:**

```markdown
<skills_context>
You have access to 172 proven solutions in the skills library.

**Relevant skills for this phase (from research):**
@skills-library/{category-1}/
@skills-library/{category-2}/

**How to use:**
1. Reference applicable skills in plan frontmatter: skills_to_apply: [list]
2. Cite skills in task descriptions
3. Apply patterns from skills to implementation steps
</skills_context>

<phase_context>
Phase: {N} - {name}
Objective: {from ROADMAP}
Must-Haves: {from ROADMAP}
Dependencies: {from ROADMAP}
</phase_context>

<honesty_reminder>
Your honesty check is documented. Plans must be grounded in what you know.
If uncertain, document the uncertainty and add research verification steps.
</honesty_reminder>
```

**Planner Creates:**
- Multiple BLUEPRINT.md files (one per distinct work unit)
- Each plan assigned to a breath (parallel execution groups)
- Enhanced frontmatter with skills + WARRIOR validation

### Step 5.5: Multi-Perspective Plan Critique — Societies of Thought (v13.0)

> spontaneously develop multi-perspective debate behavior. Multi-perspective critique before
> plan commitment improves plan robustness by 15-20%. Activates fire-planner Step 4.5.

**After the planner generates BLUEPRINT(s), invoke multi-perspective critique:**

```
# Determine if critique is needed
task_count = count tasks in generated BLUEPRINT(s)

IF task_count >= 3 AND NOT --skip-checker:
  → INVOKE fire-planner Step 4.5 (Societies of Thought)
  → Three perspectives review the plan:

    DEVIL'S_ADVOCATE:  "What could go wrong? What assumptions are fragile?"
    DOMAIN_EXPERT:     "Does this follow {technology} best practices?"
    RISK_ASSESSOR:     "Which tasks have highest failure probability?"

  → Each perspective produces 1-3 concerns (max 9 total)
  → Planner addresses HIGH concerns by adjusting the plan
  → MEDIUM/LOW concerns are logged in BLUEPRINT frontmatter as `risks:`

IF task_count < 3:
  → SKIP: "Simple plan (< 3 tasks) — multi-perspective critique skipped"

IF --skip-checker:
  → SKIP: "Checker skipped via flag — critique also skipped"
```

**Output:** Updated BLUEPRINT with `risks:` frontmatter field listing unaddressed concerns.

### Step 6: Plan Structure (Dominion Flow Standard + WARRIOR)

Each plan follows this structure:

```markdown
---
# Dominion Flow Frontmatter
phase: {N}-{name}
plan: NN
breath: N
autonomous: true|false
depends_on: [list]
files_to_create: [list]
files_to_modify: [list]

# WARRIOR Skills Integration
skills_to_apply:
  - "category/skill-name"

# WARRIOR Validation Requirements
validation_required:
  - code-quality
  - testing
  - security
  - performance

# Must-Haves (Enhanced)
must_haves:
  truths:
    - "Observable behavior statement"
  artifacts:
    - path: "file/path.ts"
      exports: ["functionName"]
      contains: ["pattern"]
  key_links:
    - from: "component-a"
      to: "component-b"
      via: "integration"
  warrior_validation:
    - "Security check description"
    - "Performance check description"
---

# Plan {N}-NN: [Name]

## Objective
[What this plan accomplishes]

## Context
@.planning/CONSCIENCE.md
@.planning/VISION.md
@.planning/phases/{N}-{name}/{N}-RESEARCH.md

## Pre-Planning Honesty Check
[Documented honesty protocol answers]

## Skills Applied
[List skills with rationale]

## Tasks
[Detailed task breakdown with verification]

## Verification
[Must-Haves + WARRIOR validation commands]

## Success Criteria
[Checklist]
```

### Step 7: Spawn plan-checker (Dominion Flow Standard)

```
â—† Spawning plan-checker to validate plans...
```

**Plan-Checker Validates:**
1. Frontmatter completeness (all fields present)
2. Skills referenced exist in library
3. Must-haves are testable and specific
4. Tasks have verification commands
5. Dependencies are satisfied
6. Breaths are properly ordered

**If Validation Fails:**
- Return feedback to fire-planner
- Re-plan with corrections
- Maximum 3 revision cycles

### Step 8: Update CONSCIENCE.md

After plans approved:

```markdown
## Current Position
- Phase: {N} of {total}
- Status: Ready to execute
- Plans created: {count}
- Breaths: {wave_count}

## WARRIOR Integration
- Skills identified for Phase {N}: {skills_count}
- Honesty checkpoint: Planning complete
```

---

## Agent Spawning Instructions

### fire-researcher (Conditional)

**Spawn When:**
- `--research-first` flag
- Honesty check reveals gaps
- No existing RESEARCH.md

**Agent File:** `@agents/fire-researcher.md`

**Context:**
```markdown
Phase: {N} - {name}
Objective: {objective}
Known Gaps: {from honesty check}
Skills to Search: {topics from phase}
```

### fire-planner (Always)

**Agent File:** `@agents/fire-planner.md`

**Context:**
```markdown
<full planner context as shown in Step 5>
```

### plan-checker (Always, unless --skip-checker)

**Purpose:** Validate plans meet Dominion Flow standards

**Checks:**
- [ ] Frontmatter complete
- [ ] Skills exist
- [ ] Must-haves testable
- [ ] Tasks have verification
- [ ] Dependencies satisfied
- [ ] Breaths ordered correctly

---

## Success Criteria

### Required Outputs
- [ ] `{N}-RESEARCH.md` created (if research needed)
- [ ] At least one `{N}-NN-BLUEPRINT.md` created
- [ ] All plans have valid frontmatter
- [ ] All plans reference applicable skills
- [ ] All plans include WARRIOR validation
- [ ] Plan-checker approved all plans
- [ ] CONSCIENCE.md updated

### Completion Display

```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âœ“ PHASE {N} PLANNING COMPLETE                                                â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Phase: {N} - {name}                                                         â•‘
â•‘  Plans Created: {count}                                                      â•‘
â•‘  Breaths: {wave_count}                                                         â•‘
â•‘  Skills Identified: {skills_count}                                           â•‘
â•‘                                                                              â•‘
â•‘  Plans:                                                                      â•‘
â•‘    âœ“ {N}-01-BLUEPRINT.md (Breath 1) - {description}                                 â•‘
â•‘    âœ“ {N}-02-BLUEPRINT.md (Breath 1) - {description}                                 â•‘
â•‘    âœ“ {N}-03-BLUEPRINT.md (Breath 2) - {description}                                 â•‘
â•‘                                                                              â•‘
â•‘  Plan-Checker: APPROVED                                                      â•‘
â•‘                                                                              â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘ NEXT UP                                                                      â•‘
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â•‘                                                                              â•‘
â•‘  â†’ Run `/fire-3-execute {N}` to begin breath-based execution                  â•‘
â•‘  â†’ Or review plans in .planning/phases/{N}-{name}/                           â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

---

## Error Handling

### Phase Not Found

```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âœ— ERROR: Phase Not Found                                                     â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Phase {N} is not defined in VISION.md                                      â•‘
â•‘                                                                              â•‘
â•‘  Available phases: 1-{max}                                                   â•‘
â•‘                                                                              â•‘
â•‘  Action: Check VISION.md or add phase definition                            â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

### Dependencies Not Met

```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âœ— ERROR: Dependencies Not Met                                                â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Phase {N} depends on Phase {N-1} which is not complete.                     â•‘
â•‘                                                                              â•‘
â•‘  Options:                                                                    â•‘
â•‘    A) Complete Phase {N-1} first: `/fire-3-execute {N-1}`                   â•‘
â•‘    B) Force planning (not recommended): `/fire-2-plan {N} --force`          â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

### Plan-Checker Rejection

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ âš  PLAN REVISION REQUIRED                                                    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                             â”‚
â”‚  Plan {N}-{NN} failed validation:                                           â”‚
â”‚                                                                             â”‚
â”‚  Issues:                                                                    â”‚
â”‚    âœ— Missing must_haves.truths                                              â”‚
â”‚    âœ— Task 3 has no verification command                                     â”‚
â”‚    âœ— Skill "api-patterns/xyz" not found in library                          â”‚
â”‚                                                                             â”‚
â”‚  Action: Revising plan... (attempt 1 of 3)                                  â”‚
â”‚                                                                             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## References

- **Agent:** `@agents/fire-planner.md` - Planning agent with skills integration
- **Agent:** `@agents/fire-researcher.md` - Research agent with skills search
- **Template:** `@templates/plan.md` - Plan template with WARRIOR fields
- **Protocol:** `@references/honesty-protocols.md` - 3-question honesty check
- **Brand:** `@references/ui-brand.md` - Visual output standards
