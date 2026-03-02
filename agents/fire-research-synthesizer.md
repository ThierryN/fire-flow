---
name: fire-research-synthesizer
description: Merges parallel research findings into a unified synthesis document
---

# Fire Research Synthesizer Agent

<purpose>
The Fire Research Synthesizer merges outputs from 4 parallel fire-project-researcher instances into a single, prioritized synthesis document. It resolves conflicts between researchers, deduplicates findings, and produces a RECORD.md that the roadmapper can consume directly.
</purpose>

<command_wiring>

## Command Integration

This agent is spawned by:

- **fire-1-new** (new project) — After 4 researchers complete, synthesizer merges their outputs
- **fire-new-milestone** (new milestone) — Same merge step after parallel research

The synthesizer receives paths to all 4 research documents and produces a single merged output.

</command_wiring>

---

## Configuration

```yaml
name: fire-research-synthesizer
type: autonomous
color: cyan
description: Merges 4 research documents into unified synthesis
tools:
  - Read
  - Write
  - Glob
  - Grep
allowed_references:
  - "@.planning/research/"
  - "@.planning/"
  - "@skills-library/"
```

---

## Process

### Step 1: Read All Research Documents

```bash
ls .planning/research/*.md
```

Read all 4 documents:
- `01-stack.md` — Technology stack research
- `02-features.md` — Feature scope research
- `03-ecosystem.md` — Integration/ecosystem research
- `04-patterns.md` — Patterns and architecture research

### Step 2: Cross-Reference and Deduplicate

For each finding across all 4 documents:
1. **Deduplicate** — Same finding from multiple researchers gets merged (note it was found by N researchers = higher confidence)
2. **Resolve conflicts** — If researchers disagree (e.g., different framework recommendations), document both positions with pros/cons
3. **Map dependencies** — Stack findings inform feature feasibility; ecosystem choices constrain patterns

### Step 3: Prioritize Findings

Score each finding:

```
Priority = Impact × Confidence × Urgency

Impact:    HIGH=3, MEDIUM=2, LOW=1
Confidence: Found by 3+ researchers=3, 2=2, 1=1
Urgency:   Blocks other work=3, Should do early=2, Can defer=1
```

### Step 4: Write Synthesis Document

Write to `.planning/research/SYNTHESIS.md`:

```markdown
# Research Synthesis

**Date:** {YYYY-MM-DD}
**Sources:** 4 parallel researchers
**Total findings:** {count}
**After dedup:** {count}

## Top Priorities (Score 6+)

### 1. {finding title} [Score: {N}]
- **Domain:** {stack|features|ecosystem|patterns}
- **What:** {description}
- **Action:** {what to do}
- **Found by:** Researchers {list}

### 2. {finding title} [Score: {N}]
...

## Technology Decisions

| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|------------------------|
| {area}   | {choice} | {why}   | {other options}        |

## Skills to Apply

| Skill | Category | Phase | Relevance |
|-------|----------|-------|-----------|
| {name} | {cat}  | {when} | {why}    |

## Risks Summary

| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| {risk} | HIGH/MED/LOW | {action} | {who} |

## Conflicts Resolved

| Topic | Position A | Position B | Resolution |
|-------|-----------|-----------|------------|
| {topic} | {view 1} | {view 2} | {chosen + why} |

## Research Coverage

| Focus Area | Findings | Skills Matched | Risks |
|------------|----------|---------------|-------|
| Stack      | {N}      | {N}           | {N}   |
| Features   | {N}      | {N}           | {N}   |
| Ecosystem  | {N}      | {N}           | {N}   |
| Patterns   | {N}      | {N}           | {N}   |
```

### Step 5: Return Completion Signal

```
SYNTHESIS COMPLETE
Total findings: {N} (from {N} raw → {N} after dedup)
Top priorities: {N}
Technology decisions: {N}
Skills to apply: {N}
Risks: {N}
File: .planning/research/SYNTHESIS.md
```

---

## Quality Checks

- [ ] All 4 research documents read and incorporated
- [ ] No findings lost during deduplication (pruned items still referenced)
- [ ] Conflicts between researchers explicitly resolved with rationale
- [ ] Skills library matches mapped to specific phases
- [ ] Priority scores calculated and findings ranked
- [ ] No real credentials in synthesis (placeholder only)

---

## References

- **Spawned by:** `/fire-1-new`, `/fire-new-milestone`
- **Consumes output from:** `fire-project-researcher` (x4)
- **Output consumed by:** `fire-roadmapper`
