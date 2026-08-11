---
name: self-testing-feedback-loop
category: methodology
version: 1.0.0
contributed: 2026-03-06
contributor: dominion-flow
last_updated: 2026-03-06
contributors:
  - dominion-flow
tags: [circuit-breaker, testing, error-recovery, ai-agent, feedback-loop]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Self-Testing Feedback Loop for Circuit Breakers

## Problem

When AI agents hit errors during code generation, they typically rotate to a different approach — but never verify whether the rotation actually fixed anything before continuing. This creates "blind rotation" where the agent tries approach after approach without feedback, wasting context and iterations. The circuit breaker detects spinning (same error repeated), but the rotation itself has no verification step.

Symptoms:
- Agent rotates approaches but keeps hitting the same underlying error
- Circuit breaker trips after 5 identical errors despite "different" approaches
- Agent reports "trying a new approach" but the test output is identical
- Iterations are wasted on approaches that look different but fail identically

## Solution Pattern

After every approach rotation triggered by the circuit breaker, enforce a **test-classify-feedback** cycle before continuing:

1. **TEST** — Run the most specific available test (failing test > module test > full suite)
2. **CLASSIFY** — Compare test result against the previous error hash
3. **FEEDBACK** — Inject the classification back into the agent's context for the next iteration

The classification has four outcomes:
- **PASS** → Rotation worked. Clear warning state. Continue.
- **NEW ERROR** → Different failure. That's progress. Feed new error into context.
- **SAME ERROR** → Rotation didn't help. Double-increment spin counter (accelerate circuit break).
- **NO TESTS** → Can't verify. Log warning, rely on file-change metrics only.

The key insight: **double-incrementing the spin counter** when a rotation produces the same error. This accelerates the circuit break for approaches that look different but are functionally identical — preventing the agent from exhausting 5 rotation attempts on variations of the same broken strategy.

## Code Example

```
// Before (problematic) — blind rotation
ON circuit_breaker_warning:
  rotation = suggest_new_approach(approaches_tried)
  inject_into_context(rotation)
  continue_execution()  // Hope for the best

// After (solution) — verified rotation with feedback
ON circuit_breaker_warning:
  rotation = suggest_new_approach(approaches_tried)
  inject_into_context(rotation)

  // Execute one iteration with new approach
  result = execute_iteration()

  // TEST: Run most specific available test
  test_result = run_tests(priority=[
    specific_failing_test,    // Best: exact test that's failing
    module_test_file,         // Good: tests for the modified module
    full_suite_if_quick,      // OK: full suite if < 30 seconds
  ])

  // CLASSIFY: Compare against previous error
  IF test_result.passed:
    health = PROGRESS
    spin_counter = 0          // Clear — rotation worked
    record("Rotation successful: {approach}")

  ELIF test_result.error_hash != previous_error_hash:
    health = PROGRESS           // Different error = forward movement
    spin_counter = 0
    feed_new_error(test_result) // New error feeds into next iteration
    record("New error after rotation: {new_hash}")

  ELIF test_result.error_hash == previous_error_hash:
    health = SPINNING
    spin_counter += 2           // DOUBLE increment — rotation failed
    record("Rotation ineffective: same error {hash}")

  ELIF no_tests_available:
    health = UNKNOWN
    record("No tests — manual verification needed")

  // FEEDBACK: Inject result into next iteration
  inject_into_context(
    "SELF-TEST after rotation: {test_result.status}
     Diagnosis: {health}
     Action: {recommended_next_step}"
  )
```

## Implementation Steps

1. Hook into the circuit breaker's approach rotation trigger
2. After rotation, execute exactly ONE iteration before testing
3. Run the most specific available test (don't waste time on full suite if a specific test exists)
4. Hash-compare the new error against the previous error
5. Classify as PASS / NEW_ERROR / SAME_ERROR / NO_TESTS
6. If SAME_ERROR: double-increment the spin counter to accelerate circuit break
7. Inject the test result and classification into the agent's context
8. Record the classification in the loop tracking file

## When to Use

- Any AI agent system with a circuit breaker or loop detection
- Code generation agents that run tests after changes
- Autonomous debugging loops (test-diagnose-fix patterns)
- Any system where "trying a different approach" needs verification
- Long-running execution pipelines with error recovery

## When NOT to Use

- Projects with no test suite (the loop relies on test output)
- Documentation-only changes (no testable code)
- When the circuit breaker is already TRIPPED (we're stopping, not testing)
- Interactive/manual debugging where the human provides feedback
- Single-shot code generation (no iteration loop)

## Common Mistakes

- Running the full test suite when a specific failing test exists — wastes 10x the time
- Not double-incrementing on SAME_ERROR — allows 5 useless rotations before breaking
- Testing before the rotation is applied — tests the old approach, not the new one
- Classifying "different line number, same error type" as progress — normalize error hashes first
- Skipping the feedback injection — agent doesn't know its rotation failed

## Related Skills

- [TIERED_CONTEXT_ARCHITECTURE](../methodology/TIERED_CONTEXT_ARCHITECTURE.md) - Context management that preserves error state
- [AGENT_SELF_IMPROVEMENT_LOOP](../methodology/AGENT_SELF_IMPROVEMENT_LOOP.md) - Broader agent improvement patterns
- [DIFFICULTY_AWARE_AGENT_ROUTING](../methodology/DIFFICULTY_AWARE_AGENT_ROUTING.md) - Route by difficulty level

## References

- SWE-Agent + Reflexion "Test-Diagnose-Fix" loop (NeurIPS 2024) — 37% higher fix rates
- Manus AI error preservation pattern (Feb 2026) — errors are most valuable context
- frankbria's Ralph loop fork — quantitative convergence detection
- Contributed from: dominion-flow v10.1 research session
