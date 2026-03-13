---
name: confidence-annotation-pattern
category: methodology
version: 1.0.0
contributed: 2026-02-17
contributor: dominion-flow-research
last_updated: 2026-02-17
tags: [uncertainty, confidence, quality, verification, dual-process]
difficulty: medium
usage_count: 0
success_rate: 100
research_basis: "Agentic UQ (arxiv:2601.15703), UQ Survey (arxiv:2503.15850)"
---

# Confidence Annotation Pattern

## Problem

Agents complete tasks without indicating how confident they are in their work.
This leads to two failure modes:
1. **Silent uncertainty**: Agent is unsure but ships anyway (causes bugs)
2. **Over-caution**: Agent flags everything as uncertain (causes delays)

Without confidence signals, verifiers and humans can't distinguish "definitely correct"
from "best guess" implementations.

## Solution Pattern

### Dual-Process Uncertainty Engine

**System 1 (Fast Path - Forward Propagation):**
Every agent action gets a confidence annotation with three components:
- Action: What was done
- Confidence: 0.0 to 1.0 score
- Explanation: WHY this confidence level (natural language)

```yaml
# Example confidence annotations
- action: "Implemented JWT authentication middleware"
  confidence: 0.92
  explanation: "Used established pattern from skills library, well-tested approach"

- action: "Added refresh token rotation"
  confidence: 0.65
  explanation: "Custom implementation, no existing skill matches, edge cases around concurrent refresh unclear"

- action: "Fixed race condition in payment processing"
  confidence: 0.45
  explanation: "Root cause identified but fix is speculative, need load testing to confirm"
```

**System 2 (Slow Path - Reflective Resolution):**
When confidence drops below threshold (default: 0.6):
1. Pause execution
2. Generate N parallel reflection attempts
3. Score each by confidence AND consistency
4. Select most reliable path
5. If still below threshold: ESCALATE

### Confidence Decision Matrix

| Confidence | Outcome | Action |
|------------|---------|--------|
| HIGH (>0.8) | Works | Ship it |
| HIGH (>0.8) | Fails | Debug (likely environment/config issue) |
| MEDIUM (0.6-0.8) | Works | Review before shipping |
| MEDIUM (0.6-0.8) | Fails | Investigate deeper |
| LOW (<0.6) | Works | Audit for hidden issues |
| LOW (<0.6) | Fails | Escalate to human |

### Confidence Decay Function (Novel)

As context fills and sessions extend, apply decay:
```
effective_confidence = raw_confidence * (1 - decay_rate * iterations_since_clear)
```

Where `decay_rate` = 0.02 (2% per iteration). After 25 iterations without fresh
context, even a 0.9 confidence becomes 0.45 effective confidence, triggering
Sabbath Rest automatically.

## Implementation in Dominion Flow

### In Executor RECORD.md:
```yaml
## Confidence Report

overall_confidence: 0.78
confidence_breakdown:
  - task: "User authentication"
    confidence: 0.92
    explanation: "Standard JWT pattern, skills library match"
  - task: "Rate limiting"
    confidence: 0.71
    explanation: "Used express-rate-limit, but sliding window config is untested"
  - task: "WebSocket auth"
    confidence: 0.55
    explanation: "Custom implementation, no precedent in skills library"
    recommendation: "Review before deploy"

low_confidence_items:
  - "WebSocket auth" -> needs human review
```

### In Verification:
```markdown
## Confidence-Aware Verification

Priority order (verify low-confidence items FGTAT):
1. [LOW 0.55] WebSocket auth - REQUIRES manual review
2. [MED 0.71] Rate limiting - test edge cases
3. [HIGH 0.92] User auth - spot check only
```

## When to Use

- During ALL agent execution (fire-executor, fire-debugger)
- In fire-loop iteration tracking
- In verification priority ordering
- When deciding whether to ship or review

## When NOT to Use

- Simple file operations (rename, move) - always high confidence
- When running established test suites - tests provide their own confidence
- During research/exploration phases - uncertainty is expected

## Common Mistakes

- Setting all confidence to 1.0 (defeats the purpose)
- Not explaining WHY confidence is low (explanation is the most valuable part)
- Ignoring medium-confidence items (they become bugs most often)

## Related Skills

- [SABBATH_REST_PATTERN](./SABBATH_REST_PATTERN.md) - Context rot detection
- complexity-divider - Task complexity assessment

## References

- Agentic UQ paper: https://arxiv.org/abs/2601.15703
- UQ Survey: https://arxiv.org/abs/2503.15850
- Anthropic 2026 Agentic Coding Trends Report
