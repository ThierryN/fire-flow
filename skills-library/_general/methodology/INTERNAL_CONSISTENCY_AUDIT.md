---
name: INTERNAL_CONSISTENCY_AUDIT
category: methodology
version: 1.0.0
contributed: 2026-03-06
contributor: dominion-flow
last_updated: 2026-03-06
tags: [audit, consistency, wiring, cross-reference, versioning, agents, skills]
difficulty: medium
sources:
  - "Dominion Flow v12.0 internal audit — 2026-03-06"
  - "IEEE 1028 — Software Reviews and Audits"
---

# Internal Consistency Audit

> **Core insight:** When a multi-agent system evolves across versions, new patterns get wired into core agents but peripheral commands, supporting agents, and documentation drift out of sync. A structured audit catches these gaps before they cause silent failures at runtime.

---

## Problem

After a major version upgrade (e.g., adding 6 new methodology skills), the system can appear complete because the core agents implement the new patterns. But:

- Peripheral commands (e.g., `/fire-autonomous`) may still operate at the old version
- Supporting agents (e.g., fire-researcher) may not know about new skills that name them
- Documentation (OVERVIEW) may use different terminology than the implementation
- Version footers may be stale
- Interface contracts between agents may have implicit mismatches

These inconsistencies are invisible during normal use because each component works in isolation. They only surface when the full pipeline runs end-to-end.

---

## Solution Pattern

Run a **6-dimension audit** that systematically cross-references every claim against every implementation:

### The Six Audit Dimensions

| Dimension | Question | What It Catches |
|-----------|----------|-----------------|
| **A. Skill-Agent Wiring** | Do skills name agents? Do those agents implement the skill? | Orphan skills, unwired patterns |
| **B. Overview-Agent Consistency** | Does the system map match the territory? | Terminology drift, missing features |
| **C. Internal Agent Consistency** | Are field names, step numbers, and enumerations correct within each agent? | Broken templates, mismatched counts |
| **D. Cross-Agent Flow** | Do agents use identical field names when passing data? | Interface contract mismatches |
| **E. Version Consistency** | Do all files agree on the current version? | Stale version references |
| **F. Completeness** | What's promised but not implemented? What's implemented but not documented? | Peripheral gaps, missing wiring |

### Audit Protocol

```
FOR each dimension (A through F):
  FOR each check in dimension:
    1. Identify the CLAIM (what the system says it does)
    2. Identify the EVIDENCE (what the implementation actually does)
    3. Compare: PASS (match), GAP (missing), CONFLICT (contradicts)
    4. If GAP or CONFLICT: document specific fix needed

OUTPUT: Table per dimension + summary matrix
```

---

## Audit Checklist Template

### A. Skill-Agent Wiring

For each new or modified skill:

```
1. Does the skill have a "When Agents Should Reference" section?
2. Does it name specific agents?
3. Do those named agents contain steps implementing the skill's guidance?
4. Is there a skill that NO agent references? (orphan)
5. Is there an agent step that uses a concept without citing its source skill? (unwired)
```

### B. Overview-Agent Consistency

For each feature claimed in the OVERVIEW:

```
1. Locate the claim (e.g., "Tier 0: Fast Gate")
2. Find the implementing agent step
3. Verify terminology matches (same names, same numbering)
4. Verify behavior matches (same logic, same conditions)
```

### C. Internal Agent Consistency

For each agent file:

```
1. Are all new frontmatter fields present in templates?
2. Do enumerated lists (e.g., "6 stuck types") match their source skill?
3. Are numeric values (weights, thresholds) consistent with source?
4. Do conditional gates actually STOP (not just log)?
5. Are step numbers sequential with no gaps or duplicates?
```

### D. Cross-Agent Flow

For each data handoff between agents:

```
1. Planner creates field X → Executor reads field X → same name?
2. Executor produces output Y → Verifier checks output Y → same format?
3. Verifier returns verdict Z → routing logic uses verdict Z → same values?
```

### E. Version Consistency

```
1. Header version matches?
2. Footer version matches?
3. Banner/system map version matches?
4. version.json matches?
5. No stale prior-version references in modified files?
   (Distinguish version PROVENANCE markers like "(v11.2)" from
    version IDENTITY claims like "Dominion Flow v9.0")
```

### F. Completeness

```
1. Do peripheral commands reference new patterns?
2. Do supporting agents know about new skills that name them?
3. Are "Future" items tracked explicitly (not silently missing)?
4. Are there TODO/FIXME/placeholder markers in modified files?
```

---

## Output Format

### Per-Dimension Table

```markdown
| Check | Verdict | Evidence | Fix Needed |
|-------|---------|----------|------------|
| {check description} | PASS/GAP/CONFLICT | {where you looked, what you found} | {specific action or "None"} |
```

### Summary Matrix

```markdown
| Section | PASS | GAP | CONFLICT |
|---------|------|-----|----------|
| A. Skill-Agent Wiring | N | N | N |
| B. Overview-Agent | N | N | N |
| C. Internal Consistency | N | N | N |
| D. Cross-Agent Flow | N | N | N |
| E. Version Consistency | N | N | N |
| F. Completeness | N | N | N |
| TOTALS | N | N | N |
```

### Priority-Ranked Fixes

Sort fixes into three tiers:
- **Critical:** Breaks runtime behavior or causes silent failures
- **Important:** Creates user confusion or documentation drift
- **Minor:** Cosmetic or single-line fixes

---

## When to Use

- After any major version upgrade that adds new skills or agent steps
- After wiring new patterns into core agents (planner/executor/verifier)
- Before publishing or releasing a new version
- When peripheral commands haven't been updated in 2+ versions
- As a pre-flight check before `/fire-autonomous` runs on a new codebase

## When NOT to Use

- For minor bug fixes that don't change agent architecture
- For skill-only additions that don't claim agent wiring
- During active development (wait until the version stabilizes)

---

## Common Findings Pattern

From the v12.0 audit, the most common gap pattern is **core-vs-periphery drift:**

```
Core agents (planner, executor, verifier) = fully updated
Peripheral commands (autonomous, discuss) = still at prior version
Supporting agents (researcher) = unaware of new skills
Documentation (OVERVIEW) = slightly different terminology
```

This happens because developers naturally focus on the agents they're actively modifying. The fix pattern is always the same: after updating core agents, grep all commands and supporting agents for the skill names — any that should reference them but don't are gaps.

---

## Related Skills

- [QUALITY_GATES_AND_VERIFICATION](QUALITY_GATES_AND_VERIFICATION.md) — the tiered verification pattern this audit checks for
- [CIRCUIT_BREAKER_INTELLIGENCE](CIRCUIT_BREAKER_INTELLIGENCE.md) — stuck-state classification this audit cross-references
- [RELIABILITY_PREDICTION](RELIABILITY_PREDICTION.md) — implied scenario detection this audit verifies
- [AUTONOMOUS_ORCHESTRATION](AUTONOMOUS_ORCHESTRATION.md) — scope manifests and DORA metrics this audit checks
- [REQUIREMENTS_DECOMPOSITION](REQUIREMENTS_DECOMPOSITION.md) — utility tree decomposition this audit verifies wiring for
- [CONTEXT_ROTATION](CONTEXT_ROTATION.md) — articulation protocol this audit cross-references

## References

- First applied: Dominion Flow v12.0 internal consistency audit (2026-03-06)
- Found: 26 PASS, 7 GAP, 1 CONFLICT across 34 checks
- Key finding: Core-vs-periphery drift is the dominant gap pattern
