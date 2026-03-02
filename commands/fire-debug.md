---
description: Systematic debugging with persistent state, skills library integration, and WARRIOR validation
---

# /fire-debug

> Systematic debugging with scientific method, persistent state recovery, and WARRIOR skills integration

---

## Purpose

Debug issues using scientific method with subagent isolation. Combines Dominion Flow's proven debug orchestration with skills library (debugging patterns, domain knowledge) and honesty protocols.

**Orchestrator role:** Gather symptoms, spawn fire-debugger agent, handle checkpoints, spawn continuations.

**Why subagent:** Investigation burns context fast (reading files, forming hypotheses, testing). Fresh 200k context per investigation. Main context stays lean for user interaction.

---

## Arguments

```yaml
arguments:
  issue_description:
    required: false
    type: string
    description: "Brief description of the issue to debug"
    example: "/fire-debug login fails with 500 error"

optional_flags:
  --diagnose-only: "Find root cause but don't fix (for plan-based fixes)"
  --verbose: "Show detailed investigation progress"
```

---

## Process

### Step 1: Check Active Debug Sessions

```bash
ls .planning/debug/*.md 2>/dev/null | grep -v resolved | head -5
```

**If active sessions exist AND no arguments:**
- Display sessions with status, hypothesis, next action
- User picks number to resume OR describes new issue

**If arguments provided OR user describes new issue:**
- Continue to symptom gathering

### Step 2: WARRIOR Enhancement - Skills Check + Context7 Live Docs

Before investigating, check skills library for relevant debugging patterns:

```
/fire-search "[error type] debugging"
/fire-search "[technology] troubleshooting"
```

Load applicable skills:
- `@skills-library/debugging/` patterns
- `@skills-library/[domain]/` domain knowledge
- `@skills-library/integrations/` if external service involved

**Context7 Live Documentation Lookup (v5.0):**

If the issue involves a specific library/framework, pull current docs:

```
# Resolve the library
mcp__plugin_context7_context7__resolve-library-id(libraryName="{library}")

# Query for relevant API docs, known issues, migration notes
mcp__plugin_context7_context7__query-docs(libraryId="{resolved-id}", query="{specific error}")
```

**When to use Context7 during debugging:**
- Error message references a library API (check if API changed)
- Unexpected behavior from a dependency (check current docs vs assumptions)
- Stack trace points to library internals (understand expected behavior)
- Issue appeared after dependency update (check migration/changelog)

### Step 2.5: Search Past Reflections + Debug Resolutions (NEW — v5.0)

Before investigating, check if this problem has been seen before:

```
# Search reflections for matching symptoms
Search ~/.claude/reflections/ for: "{error symptoms}" "{actual behavior}"

# If vector memory available:
/fire-remember "{symptoms}" --type reflection
/fire-remember "{symptoms}" --type debug_resolution

IF match found with >0.75 similarity:
  Display:
  "I've seen this before:
   Previous issue: {reflection slug}
   Root cause was: {root_cause}
   Fix was: {fix}
   Lesson: {lesson}
   Confidence: {similarity_score}%"

  Offer: [Apply same fix] [Investigate fresh] [Compare differences]

  IF user selects "Apply same fix":
    → Skip to fix application (adapt previous solution to current context)
    → Still verify the fix works

  IF user selects "Investigate fresh":
    → Continue to Step 3 as normal
    → Note in debug file: "Similar past issue: {slug}, chose to investigate fresh"
```

### Step 3.5: Hypothesis Tree (ReflexTree v9.1)

> **Research basis:** ReflexTree (2025) — tree-structured reflection catches root causes
> faster than linear hypothesis lists by enabling branch-and-prune investigation.

Structure debugging as a branching tree, not a flat list.

**Tree file:** `.planning/debug/{slug}-tree.md`

```markdown
# Hypothesis Tree: {slug}

## H1: {hypothesis} [ACTIVE|PRUNED|CONFIRMED]
  Evidence for: ...
  Evidence against: ...
  ### H1.1: {sub-hypothesis} [ACTIVE|PRUNED|CONFIRMED]
    Evidence for: ...
    Evidence against: ...
  ### H1.2: {sub-hypothesis} [ACTIVE|PRUNED|CONFIRMED]
    ...

## H2: {hypothesis} [ACTIVE|PRUNED|CONFIRMED]
  ...
```

**Rules:**
1. Start with 2-3 top-level hypotheses based on symptoms + failure taxonomy
2. Each investigation MUST update evidence for/against on at least one hypothesis
3. When evidence eliminates a hypothesis → mark PRUNED (never delete — APPEND-only)
4. When a hypothesis needs deeper investigation → branch into sub-hypotheses (H1.1, H1.2)
5. Maximum depth: 3 levels (H1 → H1.1 → H1.1.1)
6. When CONFIRMED → stop branching, proceed to fix

**Add to Step 4's debugger prompt (hypothesis_tree block):**

```
<hypothesis_tree>
{contents of .planning/debug/{slug}-tree.md if it exists, otherwise "No tree yet — create one"}
</hypothesis_tree>

INSTRUCTION: Create or update the hypothesis tree after each investigation step.
Mark hypotheses PRUNED when evidence eliminates them.
Branch into sub-hypotheses when root cause is narrowing but not yet isolated.
Write the tree to .planning/debug/{slug}-tree.md after each update.
```

### Step 3: Gather Symptoms (if new issue)

Use AskUserQuestion for each:

1. **Expected behavior** - What should happen?
2. **Actual behavior** - What happens instead?
3. **Error messages** - Any errors? (paste or describe)
4. **Timeline** - When did this start? Ever worked?
5. **Reproduction** - How do you trigger it?

After all gathered, confirm ready to investigate.

### Step 4: Spawn fire-debugger Agent

Fill prompt and spawn:

```markdown
<objective>
Investigate issue: {slug}

**Summary:** {trigger}
</objective>

<path_constraint>
<!-- v5.0: Path Verification Gate — MANDATORY -->
PROJECT_ROOT: {absolute path to current project}
ALLOWED_PATHS: {PROJECT_ROOT}/**
FORBIDDEN: Do NOT read, write, or search files outside PROJECT_ROOT.
If you discover you are in the wrong directory, STOP immediately and report.
</path_constraint>

<symptoms>
expected: {expected}
actual: {actual}
errors: {errors}
reproduction: {reproduction}
timeline: {timeline}
</symptoms>

<plan_context>
<!-- v5.0: Plan-Aware Debugging — compare "intended" vs "actual" -->
**Original plan for this feature/area (if available):**
@.planning/phases/{N}-{name}/*.BLUEPRINT.md

**Key must-haves from plan:**
{Extracted must_haves that relate to the buggy area}

**Assumptions made during planning:**
{Relevant assumptions from ASSUMPTIONS.md or DECISION_LOG.md}
</plan_context>

<library_docs>
<!-- v5.0: Context7 Live Documentation — current API docs for involved libraries -->
**Libraries involved:** {list from error/stack trace}

**Context7 findings:**
{Paste relevant Context7 query-docs results here, if available}

**Doc version vs installed version:** {match/mismatch noted}
</library_docs>

<warrior_context>
**Relevant skills loaded:**
@skills-library/{category}/{skill}.md

**Honesty protocol:** Before proposing fixes, you must:
1. Confirm root cause with evidence (not just theory)
2. Acknowledge what you don't know
3. Document eliminated hypotheses
4. Compare findings against the original plan context above
5. Verify assumptions against Context7 docs (not stale training data)
</warrior_context>

<code_comments>
<!-- v5.0: When writing fix code, include maintenance comments -->
When writing fix code, include simple comments explaining:
- What the fix does and WHY it solves the root cause
- Any assumptions marked with // ASSUMPTION: [reason]
- Reference to the debug session: // Fix for: {slug}
</code_comments>

<mode>
symptoms_prefilled: true
goal: {find_and_fix | find_root_cause_only}
</mode>

<debug_file>
Create: .planning/debug/{slug}.md
</debug_file>
```

```
Task(
  prompt=filled_prompt,
  subagent_type="fire-debugger",
  description="Debug {slug}"
)
```

### Step 5: Handle Agent Return

**If `## ROOT CAUSE FOUND`:**
- Display root cause and evidence summary
- Offer options:
  - "Fix now" - spawn fix subagent
  - "Plan fix" - suggest /fire-2-plan --gaps
  - "Manual fix" - done

**If `## CHECKPOINT REACHED`:**
- Present checkpoint details to user
- Get user response
- Spawn continuation agent (see step 6)

**If `## INVESTIGATION INCONCLUSIVE`:**
- Show what was checked and eliminated
- Offer options:
  - "Continue investigating" - spawn new agent with additional context
  - "Manual investigation" - done
  - "Add more context" - gather more symptoms, spawn again

### Step 6: Spawn Continuation Agent (After Checkpoint)

When user responds to checkpoint, spawn fresh agent:

```markdown
<objective>
Continue debugging {slug}. Evidence is in the debug file.
</objective>

<path_constraint>
<!-- v5.0: Path Verification Gate — MANDATORY -->
PROJECT_ROOT: {absolute path to current project}
ALLOWED_PATHS: {PROJECT_ROOT}/**
FORBIDDEN: Do NOT read, write, or search files outside PROJECT_ROOT.
If you discover you are in the wrong directory, STOP immediately and report.
</path_constraint>

<prior_state>
Debug file: @.planning/debug/{slug}.md
</prior_state>

<plan_context>
<!-- v5.0: Re-inject plan context on continuation too -->
@.planning/phases/{N}-{name}/*.BLUEPRINT.md (if available)
Key decisions: @.planning/DECISION_LOG.md (relevant entries)
</plan_context>

<checkpoint_response>
**Type:** {checkpoint_type}
**Response:** {user_response}
</checkpoint_response>

<mode>
goal: find_and_fix
</mode>
```

```
Task(
  prompt=continuation_prompt,
  subagent_type="fire-debugger",
  description="Continue debug {slug}"
)
```

### Step 7.5: Auto-Generate Reflection (NEW — v5.0)

After resolution (root cause found + fix verified), auto-generate a reflection:

```
IF status == "resolved":
  # Extract reflection content from debug file
  Read: .planning/debug/resolved/{slug}.md

  reflection = {
    date: today,
    project: {from debug file},
    trigger: "debug-resolution",
    severity: classify_severity(time_spent, files_changed, hypothesis_count),
    tags: extract_tags(root_cause, technology, symptoms),

    problem: symptoms.actual + symptoms.errors,
    tried: eliminated[].hypothesis + eliminated[].evidence,
    worked: resolution.root_cause + resolution.fix,
    lesson: synthesize_one_sentence(root_cause, fix),
    search_triggers: [
      symptoms.errors (normalized),
      symptoms.actual (keywords),
      technology + "not working"
    ]
  }

  # Write reflection file
  Save to: ~/.claude/reflections/{date}_{slug}.md

  # Notify user
  Display:
  "Reflection captured: {lesson}
   File: ~/.claude/reflections/{date}_{slug}.md
   Future debug sessions will find this automatically."
```

**Severity classification:**
- **critical**: 5+ eliminated hypotheses OR 10+ files changed OR required research
- **moderate**: 2-4 eliminated hypotheses OR multi-file fix
- **minor**: 1 hypothesis OR single-file fix

### Step 7.75: Index Resolved Debug for Replay (NEW — v5.0)

**Research basis:** ECHO (2025) — 80% improvement via experience replay

After resolution, index the debug file into vector memory for future replay:

```
IF status == "resolved" AND vector memory available:
  # Move to resolved directory (if not already)
  mv .planning/debug/{slug}.md → .planning/debug/resolved/{slug}.md

  # Index into Qdrant as debug_resolution
  cd ~/.claude/memory
  npm run index-file -- ".planning/debug/resolved/{slug}.md"

  # The file will be detected as sourceType: 'debug_resolution'
  # Future /fire-debug Step 2.5 will find it via:
  #   /fire-remember "{symptoms}" --type debug_resolution
```

This enables experience replay: future debug sessions search for similar symptoms
and can shortcut investigation by applying known root causes.

### Step 7.8b: Failure Classification (v7.0 — AgentDebug)

> **Research basis:** AgentDebug (Sep 2025) — AgentErrorTaxonomy with 24% higher accuracy;
> PALADIN (ICLR 2026) — structured failure analysis enables targeted prevention strategies.

After debug resolution, classify the root cause into AgentDebug taxonomy:

```
IF status == "resolved":

  Classify root cause:

  | Category   | Description                              | Example                                         |
  |------------|------------------------------------------|-------------------------------------------------|
  | MEMORY     | Forgot prior context or relevant knowledge | Didn't recall similar bug from last session     |
  | REFLECTION | Wrong self-assessment of progress         | Thought fix was correct but missed edge case    |
  | PLANNING   | Flawed approach selection                 | Started with wrong architecture pattern         |
  | ACTION     | Correct plan, wrong execution            | Typo in command, wrong file path                |
  | SYSTEM     | Environment or tooling failure           | Dependency not installed, port conflict         |

  Store in debug file:
    failure_category: "{MEMORY|REFLECTION|PLANNING|ACTION|SYSTEM}"

  Store in Qdrant payload (when indexing hindsight replay):
    failure_category: "{category}"
    source_type: "failure_pattern"

  This enables future debugging to check:
  "Previous {category} failures for similar symptoms → apply corrective strategy"

  Category-specific strategies:
    MEMORY    → Force episodic recall search before investigating
    REFLECTION → Require external validation (tests, not self-assessment)
    PLANNING   → Review plan context, check alternative approaches first
    ACTION     → Add pre-execution checklist, verify commands before running
    SYSTEM     → Check environment prerequisites before attempting fix
```

### Step 7.8: Hindsight Experience Replay (v6.0 — ECHO)

> **Research basis:** ECHO (Oct 2025) — Hindsight optimization outperforms Reflexion by 80%.
> When a task fails, generating "what should have been done" creates synthetic positive
> examples that dramatically improve future performance. The key insight: learning from
> failures is 80% more effective when you also generate what success looks like.

After debug resolution, generate a structured hindsight replay:

```
IF status == "resolved":

  # 1. Generate hindsight narrative
  hindsight = generate:
    "HINDSIGHT REPLAY — {slug}

    ## Original Symptoms
    {symptoms from debug file — expected, actual, errors}

    ## Wrong Approaches Tried
    {list eliminated hypotheses with why they failed}

    ## Correct Approach
    Given these symptoms, the correct approach was:
    {resolution.root_cause} → {resolution.fix}

    ## Pattern for Future
    When you see: {symptom signature — the trigger pattern}
    The root cause is likely: {root_cause category}
    The fix is: {generalized fix approach}

    ## Key Diagnostic Step
    The diagnostic that cracked it: {the evidence that confirmed root cause}"

  # 2. Save as hindsight replay file
  Save to: .planning/debug/resolved/{slug}-hindsight.md

  # 3. Index into Qdrant as hindsight_replay
  cd ~/.claude/memory
  npm run index-file -- ".planning/debug/resolved/{slug}-hindsight.md"
  # source_type will be detected as 'hindsight_replay'

  # 4. Pre-seed utility score (hindsight replays are high-value)
  npm run track-usage -- --source ".planning/debug/resolved/{slug}-hindsight.md" --helpful true

  Display:
  "Hindsight replay generated: {slug}
   Pattern: {symptom signature} → {fix category}
   Indexed for future debug sessions."
```

**Why this matters:** Future debug sessions (Step 2.5) will find both the raw debug file
AND the hindsight replay. The replay gives a direct "if you see X, do Y" shortcut
instead of requiring the agent to re-derive the solution from raw investigation notes.

---

### Step 7.9: Record Resolution Sequence (v7.0 — AgentRR)

> **Research basis:** AgentRR (May 2025) — dual-level record/replay with check functions;
> RLEP (Jul 2025) — blend replayed with new experiences for faster learning.

After debug resolution, record the exact steps at TWO levels:

```
IF status == "resolved":

  ## Low-Level (Exact Commands — for identical replay)
  resolution_sequence = {
    "preconditions": [
      "file exists: {path}",
      "package installed: {name}",
      "working directory: {dir}"
    ],
    "steps": [
      {"type": "edit", "file": "{path}", "line": N, "old": "...", "new": "..."},
      {"type": "bash", "command": "npm test", "expected_exit": 0}
    ],
    "postconditions": [
      "test passes: {test_name}",
      "no errors in: {file}"
    ]
  }

  ## High-Level (Narrative — for similar-but-different)
  hindsight_narrative =
    "When {symptom pattern}, the root cause is typically {category}.
     Check {diagnostic step} first. The fix involves {general approach}."

  Store both levels:
    .planning/debug/resolved/{slug}-replay.json  (low-level — exact steps)
    .planning/debug/resolved/{slug}-hindsight.md  (high-level — existing from Step 7.8)

  Future debugging (Step 2.5) uses BOTH levels:
    - If identical symptoms + identical preconditions → replay low-level exactly
    - If similar symptoms + different context → adapt from high-level narrative
```

### Step 7: Sabbath Rest - Context Persistence

After resolution or checkpoint, update persistent state:

```markdown
## .claude/dominion-flow.local.md

### Last Debug Session
- Issue: {slug}
- Status: {resolved | checkpoint | inconclusive}
- Root Cause: {if found}
- Files Changed: {list}
- Session: {timestamp}
```

---

## Debug File Protocol

### File Location

```
DEBUG_DIR=.planning/debug
DEBUG_RESOLVED_DIR=.planning/debug/resolved
```

### File Structure

```markdown
---
status: gathering | investigating | fixing | verifying | resolved
trigger: "[verbatim user input]"
created: [ISO timestamp]
updated: [ISO timestamp]
skills_applied: []
---

## Current Focus
<!-- OVERWRITE on each update - reflects NOW -->

hypothesis: [current theory]
test: [how testing it]
expecting: [what result means]
next_action: [immediate next step]

## Symptoms
<!-- Written during gathering, then IMMUTABLE -->

expected: [what should happen]
actual: [what actually happens]
errors: [error messages]
reproduction: [how to trigger]
started: [when broke / always broken]

## Eliminated
<!-- APPEND only - prevents re-investigating -->

- hypothesis: [theory that was wrong]
  evidence: [what disproved it]
  timestamp: [when eliminated]

## Evidence
<!-- APPEND only - facts discovered -->

- timestamp: [when found]
  checked: [what examined]
  found: [what observed]
  implication: [what this means]

## Resolution
<!-- OVERWRITE as understanding evolves -->

root_cause: [empty until found]
fix: [empty until applied]
verification: [empty until verified]
files_changed: []
```

---

## Completion Display

```
+------------------------------------------------------------------------------+
| POWER DEBUG COMPLETE                                                          |
+------------------------------------------------------------------------------+
|                                                                              |
|  Debug Session: .planning/debug/resolved/{slug}.md                           |
|                                                                              |
|  Root Cause: {what was wrong}                                                |
|  Fix Applied: {what was changed}                                             |
|  Verification: {how verified}                                                |
|                                                                              |
|  Files Changed:                                                              |
|    - {file1}: {change}                                                       |
|    - {file2}: {change}                                                       |
|                                                                              |
|  Skills Applied:                                                             |
|    - {skill1}                                                                |
|    - {skill2}                                                                |
|                                                                              |
|  Commit: {hash}                                                              |
|                                                                              |
+------------------------------------------------------------------------------+
| NEXT UP                                                                      |
+------------------------------------------------------------------------------+
|                                                                              |
|  -> Run `/fire-4-verify` to validate the fix didn't break anything          |
|  -> Or continue with `/fire-dashboard` to check project status              |
|                                                                              |
+------------------------------------------------------------------------------+
```

---

## Success Criteria

- [ ] Active sessions checked
- [ ] Skills library searched for relevant patterns
- [ ] Symptoms gathered (if new)
- [ ] fire-debugger spawned with context
- [ ] Checkpoints handled correctly
- [ ] Root cause confirmed before fixing
- [ ] Reflection auto-generated after resolution (Step 7.5)
- [ ] Past reflections searched before investigating (Step 2.5)
- [ ] Sabbath Rest state updated

---

## References

- **Agent:** Uses `fire-debugger` agent (proven debug methodology)
- **Skills:** `@skills-library/debugging/` patterns
- **Protocol:** Scientific method with hypothesis testing
- **Brand:** `@references/ui-brand.md` - Visual output standards
