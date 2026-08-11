---
name: Hierarchical Review (MARS Pattern)
category: methodology
version: 1.0.0
contributed: 2026-03-12
contributor: fire-research
last_updated: 2026-03-13
tags: [verification, review, token-optimization, self-check, multi-tier, meta-reviewer]
difficulty: medium
---

# Hierarchical Review (MARS) — Author Self-Check Before Expensive Review

> (arXiv 2509.20502, Sep 2025) — hierarchical author→reviewer→meta-reviewer
> cuts total verification tokens by ~50%.

## Problem

In AI-assisted development, verification is expensive. A full verifier + reviewer pass costs 2,000-5,000 tokens and takes significant time. But 60-70% of issues found by external review are things the author already knew about — low confidence in a section, skipped requirements, known gaps. Running expensive external review to discover what the author could have flagged is wasted computation.

## Solution Pattern

A 3-tier review hierarchy where each tier is a progressively more expensive filter:

```
Tier 1: AUTHOR SELF-CHECK (~100 tokens)
  The executor checks its own work against the plan.
  Catches: missing must-haves, low-confidence tasks, known gaps.
  If this fails → fix BEFORE spawning external review.

Tier 2: EXTERNAL REVIEW (~2,000 tokens)
  Verifier + reviewer check the work independently.
  Catches: logic errors, quality issues, over-engineering.
  Receives self-check summary to avoid redundant checks.

Tier 3: META-REVIEW (~500 tokens, only on disagreement)
  Arbitrates when Tier 2 reviewers disagree.
  Voting, weighted resolution, or fork strategy.
```

### Tier 1: Author Self-Check

```
FOR each executor's output (RECORD.md):
  EXTRACT:
    - files_changed list
    - must_haves_addressed (cross-reference BLUEPRINT)
    - known_gaps (executor's own honesty declarations)
    - test_results (if any)
    - confidence score (from return envelope)

  QUICK VALIDATION:
    1. Every must-have has at least one file addressing it
    2. No must-have is marked "skipped" without documented reason
    3. Executor's own confidence >= 60

  IF self_check_fails:
    → Route BACK to executor for fix BEFORE Tier 2
    → Log: "Self-check failed: {reason} — re-executing"
    → Saves ~2,000 tokens vs. external review finding the same gap

  IF self_check_passes:
    → Proceed to Tier 2
    → Pass self_check_summary as context (reduces redundant checks)
```

### Token Economics

| Scenario | Without MARS | With MARS | Savings |
|----------|-------------|-----------|---------|
| Clean pass (no issues) | 2,500 tokens | 2,600 tokens | -4% (overhead) |
| Self-checkable failure | 5,000 tokens | 600 tokens | 88% |
| External review needed | 2,500 tokens | 2,600 tokens | -4% (overhead) |
| Disagreement arbitration | 3,000 tokens | 3,500 tokens | -17% (overhead) |
| **Weighted average** | **3,250 tokens** | **1,825 tokens** | **~44%** |

The 88% savings on self-checkable failures (which are 60-70% of cases) more than compensates for the small overhead on clean passes.

## Implementation Steps

1. Add self-check step BEFORE spawning external verification
2. Extract structured data from executor output (RECORD.md, return envelope)
3. Cross-reference against BLUEPRINT must-haves
4. Route failures back to executor, passes forward to verification
5. Pass self-check summary to verifier as context

## When to Use

- Any automated verification pipeline with expensive external review
- Multi-phase project execution where each phase is verified
- CI/CD pipelines where you can add a "pre-flight check" before full test suite
- Code review workflows where author self-review precedes peer review

## When NOT to Use

- Single-task executions where the overhead exceeds the benefit
- When the author's self-assessment is unreliable (new contributors, adversarial context)
- When verification is already cheap (< 500 tokens or < 30 seconds)

## Must Do

- Keep Tier 1 lightweight (~100 tokens) — it's a filter, not a review
- Pass Tier 1 results to Tier 2 as context (prevents redundant discovery)
- Preserve the `--skip-self-check` escape hatch for debugging

## Must Not Do

- Do not make Tier 1 as thorough as Tier 2 (defeats the purpose)
- Do not skip Tier 2 just because Tier 1 passes (self-assessment has blind spots)
- Do not use Tier 1 to suppress known issues (it's for catching them, not hiding them)

## Related Skills

- [VOTING_VERDICT_ARBITRATION](./VOTING_VERDICT_ARBITRATION.md) — Tier 3 meta-review pattern
- [OBSERVATION_MASKING](./OBSERVATION_MASKING.md) — reduces token cost at each tier
- [MULTI_AGENT_COORDINATION](./MULTI_AGENT_COORDINATION.md) — parent coordination framework

## References

- "MARS: Meta-reviewer Arbitrated Review System" — arXiv 2509.20502, Sep 2025
- Wired into: `fire-3-execute.md` Step 7.9 (Hierarchical Review — Author Self-Check)
- Complementary to: `fire-3-execute.md` Step 7.85 (Execution Insights Aggregation)
