# Workflow: Phase Planning Orchestration

<purpose>
Create detailed execution plans for a specified phase by combining Dominion Flow's structured planning methodology with WARRIOR's skills library access, honesty protocols, and validation requirements. This workflow ensures plans are grounded in proven patterns and include comprehensive verification criteria before any code is written.
</purpose>

---

<core_principle>
**Plans must be honest about what we know and don't know.** Before creating any plan, agents must complete the 3-question honesty check. Plans based on false confidence lead to technical debt and rework. When in doubt, research first.
</core_principle>

---

<required_reading>
Before executing this workflow, load:
```markdown
@.planning/CONSCIENCE.md           # Current project position
@.planning/VISION.md         # Phase objectives and scope
@agents/fire-planner.md      # Planner agent configuration
@agents/fire-researcher.md   # Researcher agent configuration
@templates/plan.md            # Plan template with WARRIOR fields
@references/honesty-protocols.md  # 3-question honesty check
```
</required_reading>

---

<process>

## Step 1: Validate Environment and Arguments

**Purpose:** Ensure we have what we need before planning.

```bash
# Check required files exist
if [ ! -f ".planning/CONSCIENCE.md" ]; then
  echo "ERROR: No .planning/CONSCIENCE.md found"
  echo "Run /fire-1a-new to initialize project first"
  exit 1
fi

if [ ! -f ".planning/VISION.md" ]; then
  echo "ERROR: No .planning/VISION.md found"
  echo "Project structure incomplete"
  exit 1
fi

# Parse phase number from arguments
PHASE_NUM=$1

# Validate phase exists in VISION.md
grep -q "Phase $PHASE_NUM:" .planning/VISION.md || {
  echo "ERROR: Phase $PHASE_NUM not found in VISION.md"
  exit 1
}
```

**Argument Validation:**
```yaml
required:
  phase_number: integer (1-N where N is total phases)

optional:
  --gaps: "Plan only for gaps identified in verification"
  --research-first: "Force research phase before planning"
  --skip-checker: "Skip plan-checker validation (not recommended)"
```

---

## Step 2: Load Phase Context

**Purpose:** Understand what this phase needs to accomplish.

### Extract from CONSCIENCE.md
```markdown
Current Position:
- Phase: {current_phase} of {total_phases}
- Status: {status}
- Last activity: {description}
- Skills applied so far: {count}
```

### Extract from VISION.md
```markdown
Phase {N}: {name}
- Objective: {objective}
- Estimated Duration: {duration}
- Dependencies: {list}
- Must-Haves: {list}
- Deliverables: {list}
```

### Check Dependencies
```bash
# Verify previous phases are complete (if dependencies exist)
for dep in $DEPENDENCIES; do
  if [ ! -f ".planning/phases/$dep-*/VERIFICATION.md" ]; then
    echo "WARNING: Dependency $dep may not be complete"
  fi
done
```

---

## Step 3: Execute Honesty Pre-Check

**Purpose:** Ensure planning is grounded in actual knowledge.

**MANDATORY: Complete before ANY planning begins.**

### Question 1: What do I know about implementing this phase?

```markdown
## Pre-Planning Honesty Check

### What I Know
**Technologies familiar with:**
- [List specific technologies from project tech stack]
- [Note experience level: expert/intermediate/beginner]

**Similar implementations:**
- [Reference similar patterns in this codebase]
- [Reference skills library patterns: /fire-search "[topic]"]

**Existing code to build on:**
- [Files that provide foundation]
- [Patterns to follow]
```

### Question 2: What don't I know?

```markdown
### What I Don't Know
**Unfamiliar technologies:**
- [Technology] - [Why it's needed, what to research]

**Unclear requirements:**
- [Requirement] - [What clarification needed]

**Unknown edge cases:**
- [Scenario] - [Needs investigation]

**Performance implications:**
- [Area] - [Needs benchmarking/research]
```

### Question 3: Am I tempted to fake or rush?

```markdown
### Temptation Check
- [ ] NOT tempted - confidence is grounded in evidence
- [ ] TEMPTED to skip research on: ___
  - ACTION: Adding research task first
- [ ] TEMPTED to assume without verifying: ___
  - ACTION: Adding verification step
- [ ] TEMPTED to copy without understanding: ___
  - ACTION: Adding comprehension checkpoint
```

**Critical Decision Point:**
- If ANY temptation checked: Route to Step 4 (Research)
- If all clear: Skip to Step 5 (Planning)

---

## Step 4: Spawn fire-researcher (If Needed)

**Purpose:** Fill knowledge gaps before planning.

### Research Triggering Rules

Trigger research when:
1. `--research-first` flag provided
2. Honesty check reveals knowledge gaps
3. Phase involves unfamiliar technology
4. No existing `{N}-RESEARCH.md` file exists
5. Previous phase had verification gaps related to this phase

### Spawn fire-researcher Agent

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                         DOMINION FLOW > PHASE {N} RESEARCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Agent Context Injection:**
```markdown
<research_request>
Phase: {N} - {name}
Objective: {objective from ROADMAP}

Knowledge Gaps to Fill:
{list from honesty check Question 2}

Technologies to Research:
{unfamiliar technologies identified}

Specific Questions:
1. {Question from honesty check}
2. {Question from honesty check}
</research_request>

<research_instructions>
1. Search skills library: `/fire-search "[topic]"`
2. Load relevant skills: Read skills-library/{category}/{skill}.md
3. If skills insufficient: WebSearch for current best practices
4. Document ALL findings in {N}-RESEARCH.md
5. Include code examples, not just theory
6. Note any remaining uncertainties
</research_instructions>
```

**Research Output:**
```bash
# Create research file
.planning/phases/{N}-{name}/{N}-RESEARCH.md
```

**Research Document Structure:**
```markdown
# Research: Phase {N} - {name}

## Questions Researched
1. {Question}: {Answer with source}
2. {Question}: {Answer with source}

## Skills Library Findings
### {skill-category/skill-name}
- **Relevance:** {why this helps}
- **Key Pattern:** {pattern to apply}
- **Code Example:** {from skill}

## External Research
### {Topic}
- **Source:** {URL or documentation}
- **Key Insight:** {what we learned}
- **Application:** {how to use in this phase}

## Remaining Uncertainties
- {Uncertainty} - {mitigation plan}

## Recommendations for Planning
1. {Recommendation}
2. {Recommendation}

---
*Researched: {timestamp}*
```

---

## Step 5: Spawn fire-planner Agent

**Purpose:** Create detailed execution plans based on phase requirements.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                         DOMINION FLOW > PHASE {N} PLANNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Spawning fire-planner for Phase {N}...
```

**Agent Context Injection:**
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
Duration: {estimated}
Dependencies: {list}
Must-Haves: {from ROADMAP}
Deliverables: {from ROADMAP}
</phase_context>

<research_context>
{If {N}-RESEARCH.md exists, include its contents}
</research_context>

<honesty_reminder>
Your honesty check is documented. Plans must be grounded in what you know.
If uncertain about any task, document the uncertainty and add verification steps.
Do NOT plan tasks you cannot explain in detail.
</honesty_reminder>
```

### Plan Generation Rules

**How to split work into plans:**
1. **Logical boundaries:** Each plan should be a coherent unit of work
2. **Parallel opportunities:** Plans that can run in parallel go in the same breath
3. **Dependencies:** Plans depending on others go in later breaths
4. **Size:** Each plan should be 30-90 minutes of work
5. **Verification:** Each plan must have testable completion criteria

**Breath Assignment:**
- Breath 1: Foundation work, no dependencies
- Breath 2: Work depending on Breath 1
- Breath 3: Work depending on Breath 2
- etc.

### Plan Structure (Enhanced Frontmatter)

```markdown
---
# Dominion Flow Frontmatter
phase: {N}-{name}
plan: NN
breath: N
autonomous: true|false
depends_on: [list of plan IDs]
files_to_create: [list]
files_to_modify: [list]

# WARRIOR Skills Integration
skills_to_apply:
  - "category/skill-name"
  - "category/skill-name"

# WARRIOR Validation Requirements
validation_required:
  - code-quality
  - testing
  - security
  - performance
  - documentation

# Must-Haves (Enhanced with WARRIOR)
must_haves:
  truths:
    - "Observable behavior statement 1"
    - "Observable behavior statement 2"
  artifacts:
    - path: "file/path.ts"
      exports: ["functionName"]
      contains: ["pattern", "keyword"]
  key_links:
    - from: "component-a"
      to: "component-b"
      via: "integration-point"
  warrior_validation:
    - "Security check: No hardcoded credentials"
    - "Performance check: Response time < 200ms"
    - "Quality check: Test coverage > 80%"
---

# Plan {N}-NN: [Descriptive Name]

## Objective
[Clear statement of what this plan accomplishes]

## Context
@.planning/CONSCIENCE.md
@.planning/VISION.md
@.planning/phases/{N}-{name}/{N}-RESEARCH.md

## Pre-Planning Honesty Check
[Complete documentation from Step 3]

## Skills Applied
[List each skill with rationale for inclusion]

## Tasks
[Detailed task breakdown with verification per task]

## Verification
[Must-Haves + WARRIOR validation commands]

## Success Criteria
[Checklist of completion requirements]
```

---

## Step 6: Spawn plan-checker Agent

**Purpose:** Validate plans meet Dominion Flow standards before approval.

```
Spawning plan-checker to validate plans...
```

**Plan-Checker Validation Checklist:**

### Structural Checks
- [ ] Frontmatter complete (all required fields present)
- [ ] Breath assignment logical (dependencies in earlier breaths)
- [ ] Files to create/modify specified
- [ ] Autonomous flag appropriate for task complexity

### Skills Checks
- [ ] Referenced skills exist in library
- [ ] Skills are relevant to plan tasks
- [ ] Skill patterns are actually applied in tasks

### Must-Haves Checks
- [ ] Truths are observable and testable
- [ ] Artifacts have specific paths and exports
- [ ] Key links identify real integration points
- [ ] WARRIOR validation items are specific

### Task Checks
- [ ] Each task has clear action description
- [ ] Each task has specific steps (not vague)
- [ ] Each task has verification commands
- [ ] Each task has done criteria
- [ ] Checkpoint tasks clearly marked

### Quality Checks
- [ ] Honesty check is documented (not templated)
- [ ] Uncertainties are acknowledged
- [ ] Research is referenced where applicable

**If Validation Fails:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PLAN REVISION REQUIRED                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Plan {N}-{NN} failed validation:                                           │
│                                                                             │
│  Issues:                                                                    │
│    - Missing must_haves.truths                                              │
│    - Task 3 has no verification command                                     │
│    - Skill "api-patterns/xyz" not found in library                          │
│                                                                             │
│  Action: Revising plan... (attempt 1 of 3)                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Maximum 3 revision cycles.** If still failing, flag for human review.

---

## Step 7: Create Phase Directory Structure

**Purpose:** Organize phase planning artifacts.

```bash
# Create phase directory
mkdir -p .planning/phases/{N}-{name}

# Save all generated files
# - {N}-RESEARCH.md (if research was done)
# - {N}-01-BLUEPRINT.md
# - {N}-02-BLUEPRINT.md
# - etc.
```

**Expected Structure:**
```
.planning/phases/{N}-{name}/
├── {N}-RESEARCH.md        # If research was done
├── {N}-01-BLUEPRINT.md         # Plan 1
├── {N}-02-BLUEPRINT.md         # Plan 2
├── {N}-03-BLUEPRINT.md         # Plan 3
└── ...
```

---

## Step 8: Update CONSCIENCE.md

**Purpose:** Reflect planning completion in project state.

```markdown
## Current Position
- **Phase:** {N} of {total}
- **Breath:** Ready
- **Status:** Ready to execute
- **Last activity:** {timestamp} - Phase {N} planning complete
- **Progress:** [##--------] {progress_percent}%

## Dominion Flow Progress Tracking
### Phase Status
| Phase | Name | Status | Plans | Completed |
|-------|------|--------|-------|-----------|
| {N} | {name} | Planned | {plan_count} | 0 |

## WARRIOR Integration
- **Skills identified for Phase {N}:** {skills_count}
- **Honesty checkpoint:** Planning complete, ready for execution
- **Research conducted:** {yes/no}
```

---

## Step 9: Display Completion Summary

**Purpose:** Confirm planning success and provide next steps.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ PHASE {N} PLANNING COMPLETE                                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Phase: {N} - {name}                                                         ║
║  Plans Created: {count}                                                      ║
║  Breaths: {wave_count}                                                         ║
║  Skills Identified: {skills_count}                                           ║
║                                                                              ║
║  Plans:                                                                      ║
║    {N}-01-BLUEPRINT.md (Breath 1) - {description}                                   ║
║    {N}-02-BLUEPRINT.md (Breath 1) - {description}                                   ║
║    {N}-03-BLUEPRINT.md (Breath 2) - {description}                                   ║
║                                                                              ║
║  Research: {Yes, see {N}-RESEARCH.md | No research needed}                   ║
║  Plan-Checker: APPROVED                                                      ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ NEXT UP                                                                      ║
├──────────────────────────────────────────────────────────────────────────────┤
║                                                                              ║
║  Run `/fire-3-execute {N}` to begin breath-based execution                    ║
║  Or review plans in .planning/phases/{N}-{name}/                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

</process>

---

## Agent Spawning Summary

| Agent | When | Purpose |
|-------|------|---------|
| **fire-researcher** | Honesty check reveals gaps OR `--research-first` | Fill knowledge gaps before planning |
| **fire-planner** | Always | Create detailed execution plans |
| **plan-checker** | Always (unless `--skip-checker`) | Validate plans meet standards |

---

## Success Criteria

### Required Outputs
- [ ] `{N}-RESEARCH.md` created (if research needed)
- [ ] At least one `{N}-NN-BLUEPRINT.md` created
- [ ] All plans have valid frontmatter
- [ ] All plans reference applicable skills
- [ ] All plans include WARRIOR validation requirements
- [ ] All plans include Must-Haves (truths, artifacts, key_links)
- [ ] Plan-checker approved all plans
- [ ] CONSCIENCE.md updated with planning status

### Quality Checks
- [ ] Honesty check is genuine (not templated)
- [ ] Research addresses actual knowledge gaps
- [ ] Plans are specific enough to execute autonomously
- [ ] Verification commands are runnable

---

## Error Handling

### Phase Not Found
Display available phases, suggest checking VISION.md.

### Dependencies Not Met
Show dependency status, offer to plan anyway (with warning) or complete dependencies first.

### Plan-Checker Max Retries
After 3 failed revision attempts, save current state and request human review.

### Research Inconclusive
Document remaining uncertainties, add checkpoint tasks for human input during execution.

---

## References

- **Agent:** `@agents/fire-planner.md` - Planning agent with skills integration
- **Agent:** `@agents/fire-researcher.md` - Research agent with skills search
- **Template:** `@templates/plan.md` - Plan template with WARRIOR fields
- **Protocol:** `@references/honesty-protocols.md` - 3-question honesty check
- **Brand:** `@references/ui-brand.md` - Visual output standards
