---
name: QUALITY_GATES_AND_VERIFICATION
category: methodology
description: Industry-proven verification patterns — tiered gates, risk-based testing, error budgets, shift-left, and the 7 principles of testing applied to AI-assisted development
version: 1.0.0
tags: [quality-gates, verification, testing, risk-based-testing, error-budget, shift-left]
sources:
  - "Google SRE — Error Budget Policy (sre.google)"
  - "Netflix — Kayenta Automated Canary Analysis"
  - "SonarSource, Dynatrace, LinearB — Quality Gate frameworks"
  - "Hans-Petter Halvorsen — Software Development: A Practical Approach"
  - "ISTQB — 7 Principles of Testing"
  - "CRISP-ML(Q) — Phase-level risk registers"
---

# Quality Gates and Verification

> **Core insight:** A gate that halts progress is working correctly. Distinguish between "agent failed" and "gate blocked advancement pending better input."

---

## 1. Tiered Verification (Shift-Left)

Structure verification as two tiers — never run expensive checks when cheap ones already fail:

### Tier 1: Fast Gate (seconds, always run)
- Syntax validation / linting
- File existence checks
- Schema conformance
- Import resolution
- Type checking (if applicable)

### Tier 2: Slow Gate (minutes, run only when Tier 1 passes)
- Integration tests
- End-to-end validation
- Performance benchmarks
- Security scans
- Cross-phase contract verification

**Why:** A build that doesn't compile will never pass integration tests. Running integration tests on broken syntax wastes tokens and time.

**Agent action:** fire-verifier should run Tier 1 checks first. If any fail, report immediately without running Tier 2. This alone can save 50%+ of verification time on failed phases.

---

## 2. Risk-Based Testing

Test scope is a function of two variables:

```
Test Priority = Likelihood of Failure × Impact of Failure
```

| Quadrant | Likelihood | Impact | Strategy |
|----------|-----------|--------|----------|
| **Test first, test most** | High | High | Full verification, manual review |
| **Test thoroughly** | Low | High | Targeted deep tests |
| **Test efficiently** | High | Low | Automated regression |
| **Sample or defer** | Low | Low | Spot check, trust |

**Agent action:** Before verification, classify each changed area by this matrix. Don't test everything equally — that's wasteful. Don't skip testing on "small changes" — that's dangerous.

### Change Impact Scoping
```
Config-only change    → verify config loads, skip code tests
Backend-only change   → verify API + DB, skip frontend/E2E
Frontend-only change  → verify rendering + UX, skip backend
Full-stack change     → full verification
Test-only change      → verify tests pass, minimal code review
```

---

## 3. Error Budget for Retry Decisions

Borrowed from Google SRE: every task has a finite retry budget.

```
Task error budget = max_retries (default: 2)

After each retry:
  budget -= 1

  IF budget == 0:
    STOP retrying
    Route to: research → re-plan → or escalate

  NEVER: retry the same approach a 3rd time
```

**Why this works:** An agent that retries the same failing approach 5 times is burning tokens, not solving problems. Two retries catches transient failures. Beyond that, the approach itself is wrong.

**Integration with circuit breaker:** The error budget is the per-task trip threshold. When exhausted, the task-level breaker opens and routes to research.

---

## 4. The 7 Principles of Testing (Applied to AI Development)

From ISTQB, adapted for AI-agent workflows:

| Principle | Original | AI-Agent Translation |
|-----------|----------|---------------------|
| **1. Testing shows presence of bugs** | Testing reduces probability of undiscovered defects but isn't proof of correctness | Verification catches issues but passing doesn't guarantee production-ready |
| **2. Exhaustive testing is impossible** | Test based on risk assessment, not completeness | Scope verification to change impact, don't verify everything |
| **3. Early testing** | Start testing as early as possible | Verify plan coherence before execution, not after |
| **4. Defect clustering** | A small number of modules contain most bugs | Track which phases/tasks cluster failures — invest guards there |
| **5. Pesticide paradox** | Same tests stop finding new bugs | Rotate verification approaches; static checklist misses novel failures |
| **6. Testing is context-dependent** | Different software needs different testing | Backend change ≠ frontend change ≠ config change → different checks |
| **7. Absence of error is a fallacy** | Bug-free software can still be unusable | Code that passes all checks but doesn't meet user requirements is still wrong |

---

## 5. Phase-Level Risk Registers (CRISP-ML(Q))

Before each major phase, generate a short risk assessment:

```markdown
## Phase {N} Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| {most likely failure mode} | {H/M/L} | {H/M/L} | {specific action} |
| {second most likely} | {H/M/L} | {H/M/L} | {specific action} |
| {third most likely} | {H/M/L} | {H/M/L} | {specific action} |
```

**This is 5 lines, not a document.** The point is to think about failure before executing, not to create paperwork.

---

## 6. Definition of Ready / Definition of Done

Two gates that prevent wasted work:

### Definition of Ready (before starting a task)
- [ ] Acceptance criteria are clear and verifiable
- [ ] Dependencies are resolved or documented
- [ ] Scope is bounded (files, tools, operations)
- [ ] Required context is available (MEMORY.md, prior phase output)

### Definition of Done (before declaring complete)
- [ ] All Tier 1 checks pass
- [ ] Tier 2 checks pass (if applicable to scope)
- [ ] No regressions introduced
- [ ] RECORD.md updated with what was done
- [ ] Agent confidence ≥ 70% on the output

**Rule:** If DoR isn't met, send the task back for clarification — don't start it. If DoD isn't met, the task is not done — don't advance.

---

## When Agents Should Reference This Skill

- **fire-verifier:** Apply tiered verification (Tier 1 before Tier 2), risk-based scoping
- **fire-planner:** Include risk register in plan output, define DoR/DoD per task
- **fire-executor:** Check DoR before starting, track error budget per task
- **fire-autonomous:** Use error budget to decide retry vs. escalate
