# /fire-research

> Daily AI research-to-upgrade pipeline — search papers, score findings, implement in waves

---

## Purpose

Systematic daily workflow for finding, evaluating, and implementing AI research improvements into fire-flow. Eliminates the need to explain the process each session — any fresh agent follows this pipeline autonomously.

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
  - Read: All workflow files in the fire-flow plugin directory
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

**Threshold:** Score < 3.0 = deferred. Score > 4.0 = Wave 1.

Present scored results to user:

```
=============================================================
            RESEARCH RESULTS — [Focus Area]
=============================================================

Papers/Patterns Analyzed: [N]
Above threshold (≥3.0): [N]
Wave 1 candidates (≥4.0): [N]

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

### Step 5: Group Into Waves

Not tiers (priority) — WAVES (dependency order):

```
Wave 1: Foundation (no dependencies)
  - [changes that can be implemented immediately]

Wave 2: Intelligence (builds on Wave 1)
  - [logic that USES Wave 1 structures]

Wave 3: Decision (builds on Wave 2)
  - [higher-order patterns integrating Wave 1+2]
```

Confirm wave plan with user before implementing.

### Step 6: Implement Wave by Wave

For each wave:
1. Implement changes with inline citations:
   ```
   > **Research basis (vX.Y):** [Paper] ([Venue] [Year]) — [finding].
   > Applied: [what changed and why].
   ```
2. Verify wave works before starting next
3. Track deferred candidates

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
Changes Implemented: [N] across [N] waves

-------------------------------------------------------------
WAVE SUMMARY
-------------------------------------------------------------

Wave 1: [N] changes — [brief description]
Wave 2: [N] changes — [brief description]

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
- [ ] Findings grouped into dependency-ordered waves
- [ ] Each change has inline research citation
- [ ] Deferred candidates tracked
- [ ] Version bumped, report generated, memory indexed

---

## Related Commands

- `/fire-search` — Search existing skills library
- `/fire-add-new-skill` — Contribute individual skill from session
- `/fire-4-verify` — Verify changes after implementation
- `/fire-5-handoff` — Save session state with deferred candidates
