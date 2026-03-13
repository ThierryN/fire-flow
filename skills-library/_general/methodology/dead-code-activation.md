---
name: dead-code-activation
category: methodology
version: 1.0.0
contributed: 2026-03-12
contributor: dominion-flow
last_updated: 2026-03-12
contributors:
  - dominion-flow
tags: [methodology, dead-code, activation, gap-analysis, wiring, upgrade]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Dead Code Activation

## Problem

Large codebases accumulate **documented-but-unwired features** — code, configs, or documentation that describe capabilities which were never connected to the execution path. These features were designed, sometimes even partially implemented, but never called from the main flow. They sit dormant, invisible to users and agents.

This is distinct from unused code (which should be deleted). Dead code activation targets **valuable features that SHOULD be active** but aren't — often because the implementer documented the feature in one file but forgot to wire it into the calling code.

**Symptoms:**
- Documentation describes a feature that doesn't seem to work
- Config files define options that have no effect
- Helper functions exist but are never imported or called
- README mentions capabilities that aren't accessible
- Version history says "added X" but X has no entry point

## Solution Pattern

**Systematic grep-trace-wire cycle:**

1. **Grep for references** — Find all mentions of the feature across docs, configs, and code
2. **Trace the call path** — Follow from entry point (CLI, API, UI) to where the feature should be invoked
3. **Identify the gap** — Find where the call chain breaks (the feature is defined but never called)
4. **Wire it in** — Add the missing import/call/registration at the gap point
5. **Verify end-to-end** — Confirm the feature is now reachable from its intended entry point

### Why This Is the Highest-Impact Upgrade Pattern

Across 4+ consecutive Dominion Flow versions, internal gap analysis consistently scored higher than external research papers. The reason: **activation cost is near-zero** (the feature already exists) while **impact is immediate** (a fully-designed feature goes live). By contrast, implementing a paper requires design, coding, testing, and documentation from scratch.

```
Cost/Impact Matrix:
                    Low Cost    High Cost
High Impact     →  [ACTIVATE]   [Implement paper]
Low Impact      →  [Skip]       [Definitely skip]
```

## Code Example

```javascript
// Example: Error classification was documented but never wired into execution

// File: docs/error-classification.md (EXISTS — documented)
// "Classify errors into 5 health states: GREEN, YELLOW, ORANGE, RED, BLACK"

// File: agents/fire-executor.md (GAP — no step calls classifier)
// Step 3 → Step 4 → Step 5 ... error-classification never referenced

// File: references/error-classification.md (EXISTS — full schema defined)
// { GREEN: "all passing", YELLOW: "warnings", ... }

// FIX: Wire classifier into executor between Step 3 and Step 4
// Added Step 3.6: Health State Classification
// "After task execution, classify result using error-classification.md schema"
// "Route: GREEN→continue, YELLOW→log+continue, ORANGE→retry, RED→escalate"
```

## Implementation Steps

1. **Run gap analysis** — Search for features mentioned in docs/configs but not in execution code:
   ```bash
   # Find features documented but never imported/called
   grep -r "feature-name" docs/ config/ --include="*.md" --include="*.json"
   grep -r "feature-name" src/ --include="*.ts" --include="*.js"
   # If docs have references but src doesn't → dead code candidate
   ```

2. **Map the intended call path** — Read the documentation to understand WHERE the feature was meant to be invoked

3. **Find the break point** — Trace from entry point to feature; identify the missing link

4. **Add the wire** — Usually 1-10 lines: an import, a function call, a step reference, or a config registration

5. **Test the activated feature** — Run the entry point and verify the feature now executes

6. **Score the activation** — Rate by impact (how much value it adds) and risk (how much it could break)

## When to Use

- Starting a new version/upgrade cycle — scan for dead code before writing new features
- After a gap analysis reveals documented-but-unwired capabilities
- When documentation mentions features that users can't access
- When config files define options that have no observable effect
- When you need high-impact improvements with minimal implementation risk

## When NOT to Use

- The "dead code" is genuinely unused and should be deleted (no documentation, no design intent)
- The feature was intentionally deferred (check git blame for "TODO" or "deferred" comments)
- The feature requires dependencies that aren't installed (activation would cause import errors)
- The code is experimental/prototype quality — needs redesign, not just wiring

## Common Mistakes

- **Activating without understanding** — Wire in a feature you don't fully understand; it breaks something downstream
- **Confusing dead code with deprecated code** — Deprecated features were turned OFF intentionally; don't re-enable them
- **Not verifying end-to-end** — Wiring the import but not testing the full path from entry to execution
- **Skipping the gap analysis** — Jumping to implementation of new features when existing dead features would solve the same problem

## Related Skills

- [INTERNAL_CONSISTENCY_AUDIT](../methodology/INTERNAL_CONSISTENCY_AUDIT.md) — Finds contradictions between documentation and code
- [REVIEW_BACKTRACK_PANEL](../methodology/REVIEW_BACKTRACK_PANEL.md) — Review step for catching missed activations

## References

- Dominion Flow v10.0-v12.6: Internal gap analysis consistently scored equal to or higher than academic papers
- Pattern confirmed across 4 consecutive versions with 20+ activations
- Contributed from: dominion-flow plugin (2026-03-12)
