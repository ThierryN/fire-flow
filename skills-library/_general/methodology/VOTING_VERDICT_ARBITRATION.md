---
name: Voting-Based Verdict Arbitration
category: methodology
version: 1.0.0
contributed: 2026-03-12
contributor: fire-research
last_updated: 2026-03-13
tags: [multi-agent, voting, conflict-resolution, code-review, verification, arbitration]
difficulty: medium
---

# Voting-Based Verdict Arbitration — Independent Votes Over Weighted Averages

> (ACL 2025) — voting improves reasoning tasks by 13.2%, consensus improves knowledge by 2.8%.
> uv PubGrub `priority.rs` — weighted scoring + fork strategy for conflict resolution.

## Problem

When multiple reviewers (human or AI) evaluate the same work, they often disagree. The naive approach is weighted averaging: verifier gets 60%, reviewer gets 40%, combine scores. This collapses independent perspectives into a single number, losing the signal that comes from disagreement patterns. Weighted averages also create false precision — a 71% combined score PASSES while 69% FAILS, despite being within noise.

## Solution Pattern

Replace weighted scoring with independent voting when multiple perspectives are available:

### Vote Types
```
PASS        — No blocking issues found
SOFT_BLOCK  — Concerns but not critical, can proceed with TODOs
HARD_BLOCK  — Critical issue, must fix before proceeding
```

### Resolution Rules
```
IF hard_block_votes >= 2:
  → BLOCK (multiple independent perspectives see critical issues)

ELIF pass_votes > (soft_block_votes + hard_block_votes):
  → PASS (majority passes, log soft_block items as TODOs)

ELSE:
  → NEEDS_REVIEW (no clear majority — requires deeper analysis)
```

### When to Use Voting vs. Weighted Scoring

| Scenario | Method | Why |
|----------|--------|-----|
| 3+ independent reviewers | **Voting** | Preserves independence |
| 2 reviewers (verifier + reviewer) | **Weighted** | Not enough votes for majority |
| Single reviewer with confidence | **Threshold** | No votes to tally |
| Reasoning task (correctness) | **Voting** | +13.2% improvement (ACL 2025) |
| Knowledge task (factual) | **Consensus** | +2.8% improvement (ACL 2025) |

## Code Example

```python
# Before — weighted scoring (collapses perspectives)
def resolve_conflict(verifier_conf, reviewer_conf):
    combined = (verifier_conf * 0.6) + (reviewer_conf * 0.4)
    return "PASS" if combined > 70 else "FAIL"

# After — independent voting (preserves perspectives)
def resolve_conflict(persona_verdicts: list[str]):
    hard_blocks = sum(1 for v in persona_verdicts if v == "HARD_BLOCK")
    passes = sum(1 for v in persona_verdicts if v == "PASS")
    total = len(persona_verdicts)

    if hard_blocks >= 2:
        return "BLOCK"
    elif passes > (total - passes):
        return "PASS"
    else:
        return "NEEDS_REVIEW"
```

## Implementation Steps

1. Collect independent verdicts from each reviewer/persona (don't let them see each other's votes)
2. Extract vote type from each verdict (map severity of findings to PASS/SOFT_BLOCK/HARD_BLOCK)
3. Tally votes by type
4. Apply resolution rules
5. Log vote breakdown for performance tracking

## Conflict Type Classification

Before voting, classify the conflict — not all disagreements need votes:

```
SCOPE conflict: Verifier checks functionality, reviewer checks quality
  → Both can be right. Apply BOTH sets of fixes. No vote needed.

SEVERITY conflict: One says PASS, another says BLOCK
  → Use voting protocol (this is where voting shines)

CONTRADICTION: One says "add X", another says "remove X"
  → Fork resolution — try both approaches, verify each, pick winner
```

## Fallback

If fewer than 3 independent perspectives are available, fall back to weighted resolution:
```
verifier_weight = 0.6  (functional correctness is primary)
reviewer_weight = 0.4  (code quality is secondary)
```

Voting requires sufficient independent perspectives to be statistically meaningful.

## Conflict History Tracking

Track which personas frequently conflict:
```
After 3+ conflicts from same persona IN CURRENT PHASE:
  → Deprioritize that persona's BLOCK votes (weight 0.2)
  → Reset at start of each new phase
  → A persona wrong in Phase 2 may be right in Phase 5
```

## When to Use

- Multi-reviewer code review with 3+ independent perspectives
- Verifier/reviewer disagreements in automated pipelines
- Any decision requiring synthesis of independent evaluations
- AI-assisted review where multiple "personas" evaluate the same work

## When NOT to Use

- Binary decisions with clear right/wrong answers
- Fewer than 3 independent voters (use weighted scoring instead)
- When voters have vastly different expertise levels (weight by expertise, don't vote)
- Trivial decisions where the overhead exceeds the benefit

## Must Do

- Keep votes independent — don't share one voter's verdict before others vote
- Log vote breakdowns for trend analysis
- Track conflict frequency per persona for calibration

## Must Not Do

- Do not collapse votes into a weighted average (defeats the purpose)
- Do not let one HARD_BLOCK veto when it's the only one (require 2+)
- Do not use voting for factual/knowledge queries (consensus is better per ACL 2025)

## Related Skills

- [MULTI_AGENT_COORDINATION](./MULTI_AGENT_COORDINATION.md) — § Verdict Arbitration Protocol
- [OBSERVATION_MASKING](./OBSERVATION_MASKING.md) — reduces noise before voting
- [AUTO_REVIEWER_SUBAGENT](./AUTO_REVIEWER_SUBAGENT.md) — generates the reviewer verdicts

## References

- "LLM Voting: Understanding When It Helps and When It Doesn't" — ACL 2025
- uv PubGrub `priority.rs` — weighted scoring + fork strategy
- Wired into: `fire-3-execute.md` Step 8.5 Merge Gate
