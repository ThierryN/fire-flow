# Confidence-Gated Execution — Adaptive Autonomy Through Uncertainty Estimation

## The Problem

AI agents treat all tasks with the same level of autonomy. Whether the agent is implementing a well-understood CRUD endpoint or modifying a security-critical authentication flow, it proceeds with the same approach. This leads to:

- Overconfident execution on unfamiliar tasks (mistakes that could have been prevented by asking)
- Underconfident pausing on familiar tasks (unnecessary user interruptions)
- No learning signal for when to be cautious vs. autonomous

### Why It Was Hard

- Confidence is subjective — agents tend to default to "high confidence" (optimism bias)
- Need concrete, measurable signals rather than vibes
- Gate behavior must be lightweight (can't add 5 minutes of analysis before every action)
- Must integrate with existing execution flows without disrupting them
- Progressive autonomy requires tracking outcomes over time

### Impact

- Without confidence gates: 73.5% error recovery rate
- With self-evaluation (which confidence gates enable): 95% error recovery rate
- Users report 20%→40% auto-approve rate increase over 750 sessions when agents demonstrate appropriate caution

---

## The Solution

### Root Cause

Agents lack a structured way to estimate "how sure am I?" before acting. The SAUP framework (ACL 2025) shows that propagating uncertainty through reasoning steps significantly improves decision quality.

### Signal-Based Confidence Scoring

Instead of asking "how confident are you?" (subjective), compute confidence from concrete signals:

```
confidence = 50 (baseline)

Positive signals (increase confidence):
  + Matching skill found in library:      +20
  + Similar reflection exists:            +15
  + Tests available to verify:            +25
  + Familiar technology/framework:        +15
  + Clear, unambiguous requirements:      +15

Negative signals (decrease confidence):
  - Unfamiliar framework/library:         -20
  - No tests available to verify:         -15
  - Ambiguous/incomplete requirements:    -20
  - Security-sensitive change:            -10
  - Destructive operation:                -15
```

### Three Confidence Levels

```
HIGH (>80%): Proceed Autonomously
  → Execute task directly
  → Run Self-Judge after completion
  → Log confidence in summary

MEDIUM (50-80%): Proceed with Extra Validation
  → Search reflections for similar scenarios
  → Search skills library for guidance
  → Run Self-Judge BEFORE and AFTER
  → Log uncertainty reason for future learning

LOW (<50%): Pause and Escalate
  → Search Context7 for current library docs
  → Check if this is outside trained domain
  → Ask user for guidance before proceeding
  → Create checkpoint before attempting
  → Log what made confidence low
```

### Integration Points

**In fire-3-execute (executor context injection):**
```xml
<confidence_gates>
Before each plan task, estimate confidence using signal scoring.
Log confidence level and signals in RECORD.md.
Gate behavior: HIGH=proceed, MEDIUM=extra-validation, LOW=escalate.
</confidence_gates>
```

**In fire-loop (recitation block):**
```markdown
## Confidence Check (v5.0)
- Score: {0-100} — {HIGH/MEDIUM/LOW}
- Signals: {what raised or lowered confidence}
- Action: {proceed / extra-validation / escalate}
```

**In RECORD.md (execution log):**
```yaml
confidence_log:
  - task: 1
    score: 85
    level: HIGH
    signals: [skill_match, tests_available, familiar_tech]
  - task: 3
    score: 45
    level: LOW
    signals: [unfamiliar_framework, no_tests, ambiguous_requirements]
    action: "Asked user for clarification on WebSocket auth approach"
```

### Code Example: Confidence Estimation

```python
# Conceptual implementation (adapt to your agent framework)

def estimate_confidence(task, skills_library, reflections, test_suite):
    score = 50  # baseline
    signals = []

    # Check skill library
    matching_skills = skills_library.search(task.description)
    if matching_skills:
        score += 20
        signals.append("skill_match")

    # Check reflections
    matching_reflections = reflections.search(task.description)
    if matching_reflections:
        score += 15
        signals.append("reflection_match")

    # Check test availability
    if test_suite.has_tests_for(task.affected_files):
        score += 25
        signals.append("tests_available")
    else:
        score -= 15
        signals.append("no_tests")

    # Check technology familiarity
    if task.technology in KNOWN_TECHNOLOGIES:
        score += 15
        signals.append("familiar_tech")
    else:
        score -= 20
        signals.append("unfamiliar_framework")

    # Check requirement clarity
    if task.has_clear_acceptance_criteria:
        score += 15
        signals.append("clear_requirements")
    else:
        score -= 20
        signals.append("ambiguous_requirements")

    # Security/destructive checks
    if task.is_security_sensitive:
        score -= 10
        signals.append("security_sensitive")
    if task.is_destructive:
        score -= 15
        signals.append("destructive_operation")

    # Clamp to 0-100
    score = max(0, min(100, score))

    level = "HIGH" if score > 80 else "MEDIUM" if score >= 50 else "LOW"
    return score, level, signals
```

---

## Testing the Fix

### Scenario Tests

| Task | Expected Score | Expected Level | Expected Action |
|------|---------------|----------------|-----------------|
| Add CRUD endpoint (known stack, tests exist, skill found) | 90+ | HIGH | Proceed |
| Implement WebSocket auth (unfamiliar, no tests, no skill) | 30-40 | LOW | Escalate |
| Fix CSS layout (familiar, no tests, clear requirement) | 65-75 | MEDIUM | Extra validation |
| Delete user data migration (familiar, tests, destructive) | 55-65 | MEDIUM | Extra validation |
| Integrate new payment provider (unfamiliar, security) | 25-35 | LOW | Escalate |

### Verification

1. Execute tasks of varying familiarity
2. Verify HIGH-confidence tasks proceed without interruption
3. Verify MEDIUM-confidence tasks trigger reflection/skill search
4. Verify LOW-confidence tasks pause for user input
5. Check confidence log in RECORD.md matches observed behavior

---

## Prevention

- Calibrate signals based on actual outcomes (if LOW-confidence tasks consistently succeed, adjust weights)
- Don't let confidence become a checkbox (the score should reflect genuine uncertainty)
- Review confidence logs periodically to identify systematic biases
- Track confidence vs. outcome correlation to improve scoring

---

## Related Patterns

- [AGENT_SELF_IMPROVEMENT_LOOP](./AGENT_SELF_IMPROVEMENT_LOOP.md) - Confidence is upgrade #6 of the loop
- [REFLEXION_MEMORY_PATTERN](./REFLEXION_MEMORY_PATTERN.md) - Reflections feed confidence scoring (+15)
- [SELF_QUESTIONING_TASK_GENERATION](./SELF_QUESTIONING_TASK_GENERATION.md) - Self-Judge runs at MEDIUM+ confidence
- [CONFIDENCE_ANNOTATION_PATTERN](./CONFIDENCE_ANNOTATION_PATTERN.md) - Related annotation approach

---

## Common Mistakes to Avoid

- Setting baseline too high (70+) — makes everything look "confident"
- Ignoring negative signals — agents naturally want to proceed
- Treating confidence gates as hard blockers — they're advisory, agent can override with justification
- Not logging confidence scores — you need the data to calibrate over time
- Applying same weights to all task types — security tasks should weight "security_sensitive" more heavily
- Making confidence estimation take >30 seconds — speed is critical for adoption

---

## Resources

- SAUP (ACL 2025): Uncertainty propagation through reasoning steps
- Anthropic measurement: Progressive autonomy 20%→40% over 750 sessions
- Snorkel AI: 95% vs 73.5% error recovery with self-evaluation
- Dominion Flow implementation: `fire-3-execute.md` confidence_gates, `fire-loop.md` confidence check

---

## Time to Implement

**2-3 hours** — Add confidence scoring to executor context, integrate into loop recitation, add RECORD.md logging

## Difficulty Level

Stars: 3/5 — The signal scoring is simple. The challenge is **calibration**: getting the weights right so the agent isn't overconfident or over-cautious. Requires tracking outcomes over multiple sessions.

---

**Author Notes:**
The most counterintuitive finding: agents that ask for help more often perform better overall. LOW-confidence escalation isn't a failure — it's the agent saying "I know what I don't know." The 95% error recovery rate comes not from avoiding errors, but from knowing when to pause and seek guidance. Confidence gates formalize the difference between "I know this" and "I'm guessing" — and that distinction is worth a 21.5 percentage point improvement in recovery rate.
