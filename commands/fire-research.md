# /fire-research

> Daily AI research-to-upgrade pipeline — search papers, score findings, implement in breaths

---

## Purpose

Systematic daily workflow for finding, evaluating, and implementing AI research improvements into dominion-flow. Eliminates the need to explain the process each session — any fresh agent follows this pipeline autonomously.

**Proven track record:** 7 successful executions (v3.2 through v8.0), producing 70+ implemented enhancements from 200+ papers analyzed.

---

## Arguments

```yaml
arguments:
  focus:
    required: false
    type: string
    description: "Research focus area (e.g., 'memory consolidation', 'failure taxonomy')"
    example: "/fire-research agent confidence calibration"

optional_flags:
  --scan-only: "Research and score papers but don't implement (reconnaissance mode)"
  --from-deferred: "Start from deferred candidates of last version"
  --quick: "Single agent search instead of parallel (faster, less thorough)"
```

---

## Process

### Step 1: Load the Research Pipeline Skill

Read the full methodology skill — it contains scoring matrices, wave templates, and citation formats refined across 7 versions:

```
@skills-library/methodology/RESEARCH_BACKED_WORKFLOW_UPGRADE.md
```

**This is MANDATORY.** The skill contains the paper scoring matrix, gap taxonomy, wave grouping rules, and citation format. Do not skip.

### Step 2: Determine Focus Area

**If arguments provided:** Use as focus area directly.

**If `--from-deferred`:** Check MEMORY.md and recent handoffs for deferred candidates:
```bash
cd ~/.claude/memory
npm run search -- "deferred candidate" --type handoff --limit 5
```

**If no arguments:** Ask user:

```
What area should we research today?

Recent deferred candidates from previous versions:
1. [List from memory search]
2. [List from memory search]

Or describe a new focus area:
> [User input]
```

### Step 3: Launch Parallel Research Agents

Launch 3-4 agents in a SINGLE message for true parallelism:

```
Agent 1: Academic Papers (arXiv, ACL, NeurIPS, ICML, ICLR — 2024-2026)
  - Search: "[focus area] AI agent 2025 2026"
  - Extract per paper: title, venue, date, key finding, measurable result,
    how it maps to our workflow, specific file/step it would modify
  - Return: Top 15 papers ranked by APPLICABILITY

Agent 2: Community Patterns + Industry Tools
  - Search: Manus AI, Replit Agent, Cursor, Devin, SWE-Agent, Claude Code
  - Focus: What do production AI coding tools do that we don't?
  - Return: Top 10 patterns with source links

Agent 3: Internal Gap Analysis (Explore subagent)
  - Read: All workflow files in the dominion-flow plugin directory
  - Classify each gap: MEMORY | REFLECTION | PLANNING | ACTION | SYSTEM
  - Return: Top 10 gaps ranked by impact

Agent 4 (optional): Failure Pattern Mining
  - Search Qdrant: debug_resolution + failure_pattern source types
  - Find recurring failures indicating systemic gaps
  - Return: Top 5 failure patterns
```

### Step 4: Score Papers With Matrix

When agents return, evaluate each finding:

| Criterion | Weight | Scoring |
|-----------|--------|---------|
| Recency | 15% | 2026=5, 2025=4, 2024=3, older=1 |
| Measurable Results | 25% | Has numbers=5, qualitative=3, none=1 |
| Applicability | 30% | Maps to specific file=5, general=3, tangential=1 |
| Novelty | 15% | Don't do this at all=5, partial=3, already done=0 |
| Implementation Cost | 15% | <10 lines=5, <50 lines=3, architectural=1 |

**Threshold:** Score < 3.0 = deferred. Score > 4.0 = Breath 1.

Present scored results to user:

```
=============================================================
            RESEARCH RESULTS — [Focus Area]
=============================================================

Papers/Patterns Analyzed: [N]
Above threshold (≥3.0): [N]
Breath 1 candidates (≥4.0): [N]

-------------------------------------------------------------
TOP FINDINGS (sorted by score)
-------------------------------------------------------------

1. [Paper Name] ([Venue] [Year]) — Score: 4.7
   Finding: [key result]
   Maps to: [specific file/step]

2. [Paper Name] ([Venue] [Year]) — Score: 4.3
   ...

-------------------------------------------------------------
INTERNAL GAPS (from Agent 3)
-------------------------------------------------------------

1. [GAP-MEMORY] [description] — Score: 4.5
2. [GAP-PLANNING] [description] — Score: 3.8

-------------------------------------------------------------
DEFERRED (< 3.0, tracked for next version)
-------------------------------------------------------------

- [Paper] — Score: 2.7 — Reason: [why deferred]

=============================================================
```

**If `--scan-only`:** Stop here. Save findings to handoff.

### Step 5: Group Into Breaths

Not tiers (priority) — BREATHS (dependency order):

```
Breath 1: Foundation (no dependencies)
  - [changes that can be implemented immediately]

Breath 2: Intelligence (builds on Breath 1)
  - [logic that USES Breath 1 structures]

Breath 3: Decision (builds on Breath 2)
  - [higher-order patterns integrating Breath 1+2]
```

Confirm breath plan with user before implementing.

### Step 6: Implement Breath by Breath

For each wave:
1. Implement changes with inline citations:
   ```
   ```
2. Verify wave works before starting next
3. Track deferred candidates

### Step 6.5: Review-Fix Loop (v13.0 — Automated Quality Gate)

> **Principle:** Implementation without review is speculation. After each breath, spawn
> reviewer subagents that test with all available tools. Fix findings. Loop until clean
> or circuit breaker trips.

```
FOR each completed breath:

  // ─── SPAWN REVIEWER SUBAGENTS ───────────────────────────
  Launch 2 parallel reviewer agents (code-reviewer subagent_type):

  Reviewer A: Implementation Correctness
    - Read ALL files modified in this breath
    - Grep for inline citations — verify every change has one
    - Check that new patterns don't contradict existing patterns
    - Verify cross-references (step numbers, file paths) are correct
    - Test: Run any available linters, type checks, or test suites
    - Return: structured findings list with severity (CRITICAL/IMPORTANT/MINOR)

  Reviewer B: Integration & Consistency
    - Read the MULTI_AGENT_COORDINATION.md skill (or relevant skill)
    - Cross-check: do command files (fire-3-execute, fire-executor)
      match what the skill document says?
    - Check for naming collisions, taxonomy conflicts, missing mappings
    - Verify: new steps have correct numbering (no duplicates, no gaps)
    - Return: structured findings list with severity

  // ─── COLLECT & CLASSIFY FINDINGS ────────────────────────
  findings = merge(Reviewer_A.findings, Reviewer_B.findings)

  critical_count = count(findings WHERE severity == CRITICAL)
  important_count = count(findings WHERE severity == IMPORTANT)
  minor_count = count(findings WHERE severity == MINOR)

  Display:
    "Breath {N} Review Results:"
    "  CRITICAL: {critical_count}"
    "  IMPORTANT: {important_count}"
    "  MINOR: {minor_count}"

  // ─── FIX-LOOP WITH CIRCUIT BREAKER ──────────────────────
  fix_attempt = 0
  max_fix_attempts = 3
  accumulated_weight = 0.0

  WHILE (critical_count > 0 OR important_count > 0) AND fix_attempt < max_fix_attempts:
    fix_attempt += 1

    Display: "  Fix attempt {fix_attempt}/{max_fix_attempts}..."

    // Apply fixes for all CRITICAL findings first, then IMPORTANT
    FOR each finding in findings WHERE severity IN (CRITICAL, IMPORTANT):
      Apply fix
      Log: "Fixed: {finding.summary}"

    // Re-run reviewers on modified files only
    Re-launch Reviewer A + B on changed files
    findings = merge(new findings)

    critical_count = count(findings WHERE severity == CRITICAL)
    important_count = count(findings WHERE severity == IMPORTANT)

    // Circuit breaker weight tracking
    accumulated_weight += (critical_count * 1.0) + (important_count * 0.5)

    IF accumulated_weight > 5.0:
      Display: "  Circuit breaker: accumulated weight {accumulated_weight} > 5.0"
      Display: "  Classifying stuck state..."
      GOTO dead_end_check

  // ─── EXIT CONDITIONS ────────────────────────────────────
  IF critical_count == 0 AND important_count == 0:
    Display: "  Breath {N}: CLEAN — all findings resolved in {fix_attempt} attempts"
    // MINOR findings logged but don't block progression
    IF minor_count > 0:
      Display: "  {minor_count} MINOR findings logged (non-blocking)"
    PROCEED to next breath

  IF fix_attempt >= max_fix_attempts AND (critical_count > 0 OR important_count > 0):
    GOTO dead_end_check

  // ─── DEAD-END CHECK (Circuit Breaker Escape) ────────────
  dead_end_check:
    Classify stuck type:
      FIXATION:  Same findings reappear after fix → context rotation needed
      LOGIC:     Fixes introduce NEW critical findings → approach is wrong
      ARCHITECTURE: Findings point to structural issue → escalate to planner

    MATCH stuck_type:
      FIXATION:
        Display: "  FIXATION detected — same issues recurring."
        Display: "  Shelving {count} unresolved findings as known gaps."
        Log findings to breath report as DEFERRED_FIXES
        PROCEED to next breath (don't block pipeline)

      LOGIC:
        Display: "  LOGIC error — fixes creating new problems."
        Display: "  Rolling back breath {N} changes and re-implementing."
        IF already_rolled_back_once:
          Tag as DEAD_END, skip breath, PROCEED
        ELSE:
          already_rolled_back_once = true
          GOTO Step 6 for this breath (re-implement with reviewer feedback)

      ARCHITECTURE:
        Display: "  ARCHITECTURE issue — structural problem detected."
        Display: "  STOPPING review loop. Manual intervention needed."
        Display: "  Run /fire-debug to investigate, or /fire-2-plan --gaps"
        STOP (do not proceed to next breath)
```

**Key design decisions:**
- **2 reviewers, not 1** — Correctness and consistency are independent concerns
- **Max 3 fix attempts** — Prevents infinite loops (Dominion Flow circuit breaker pattern)
- **Weight-based circuit breaker** — Critical findings weigh more than important ones
- **Dead-end classification** — Uses the stuck-state taxonomy from CIRCUIT_BREAKER_INTELLIGENCE.md
- **MINOR findings don't block** — Only CRITICAL and IMPORTANT require fixes
- **FIXATION allows progression** — If fixes keep recurring, log them and move on (pipeline > perfection)
- **ARCHITECTURE stops the pipeline** — Structural issues can't be fixed by retry

### Step 7: Post-Implementation

After all waves complete:

- [ ] **Version bump** — Update plugin version (semver minor for additions)
- [ ] **Generate report** — Save to `~/Documents/Claude Reports/`
- [ ] **Index into Qdrant** — `cd your-memory-repo && npm run index`
- [ ] **Update MEMORY.md** — Add concise entry with paper count, changes, key insight
- [ ] **Track deferred** — Add to handoff for next session's `/fire-research --from-deferred`

### Completion Display

```
=============================================================
            FIRE RESEARCH COMPLETE
=============================================================

Version: [old] → [new]
Papers Analyzed: [N] from [N] parallel agents
Findings Above Threshold: [N]
Changes Implemented: [N] across [N] breaths

-------------------------------------------------------------
BREATH SUMMARY
-------------------------------------------------------------

Breath 1: [N] changes — [brief description]
Breath 2: [N] changes — [brief description]

Files Modified: [N]
Key Insight: [one sentence]

-------------------------------------------------------------
DEFERRED TO NEXT VERSION
-------------------------------------------------------------

- [paper/pattern] — [reason]

-------------------------------------------------------------
NEXT STEPS
-------------------------------------------------------------

-> Run `/fire-4-verify` to validate changes
-> Run `/fire-5-handoff` to save session state
-> Tomorrow: `/fire-research --from-deferred`

=============================================================
```

---

## Success Criteria

- [ ] Research pipeline skill loaded
- [ ] Focus area determined (from args, deferred, or user)
- [ ] 3-4 parallel research agents launched
- [ ] Papers scored with 5-criterion matrix
- [ ] Findings grouped into dependency-ordered breaths
- [ ] Each change has inline research citation
- [ ] Review-fix loop ran on each wave (Step 6.5)
- [ ] All CRITICAL/IMPORTANT findings resolved or classified as dead-ends
- [ ] Deferred candidates tracked
- [ ] Version bumped, report generated, memory indexed

---

## Related Commands

- `/fire-search` — Search existing skills library
- `/fire-add-new-skill` — Contribute individual skill from session
- `/fire-4-verify` — Verify changes after implementation
- `/fire-5-handoff` — Save session state with deferred candidates
