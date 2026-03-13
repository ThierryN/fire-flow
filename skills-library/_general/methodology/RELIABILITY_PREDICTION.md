---
name: RELIABILITY_PREDICTION
category: methodology
description: Predict phase reliability before execution using implied scenario detection, sensitivity analysis, and constrained models — catch architectural mismatches before they cost tokens
version: 1.0.0
tags: [reliability, prediction, implied-scenarios, sensitivity-analysis, quality-gates]
sources:
  - "Rodrigues, Rosenblum, Uchitel — Reliability Prediction in Model-Driven Development (UCL/Imperial, 2005)"
  - "CRISP-ML(Q) — Mercedes-Benz AG + TU Berlin, 2020"
---

# Reliability Prediction for AI-Assisted Development

> **Core insight:** "Composition reveals what specification omits." When you connect agents, phases, or tools together, the system produces behaviors no individual specification predicted. Detect these early or pay later.

---

## 1. Two Risk Dimensions Per Phase

Every phase has two independent failure probabilities — assess both before executing:

| Dimension | Question | Example |
|-----------|----------|---------|
| **Transition probability** | If this phase succeeds, does it cleanly advance to the next? | "Auth phase done, but API routes phase expects a different token format" |
| **Component reliability** | What's the probability this agent/tool produces correct output? | "LLM generating boilerplate = 95% reliable. LLM designing novel algorithm = 60% reliable" |

**Agent action:** Before executing a task, estimate both. If component reliability < 60%, research first. If transition probability is unclear, verify the interface contract with the next phase.

---

## 2. Implied Scenario Detection

After any multi-agent or multi-phase interaction, check for unspecified behaviors:

### Positive Implied Scenarios (missing specification)
- The system produced a correct behavior not in the plan
- **Action:** Add it to the phase spec. Document it in PATTERNS.md
- Example: "The auth middleware also handles rate limiting — not planned, but correct and useful"

### Negative Implied Scenarios (architecture mismatch)
- The system permits behavior the specification forbids
- **Action:** Add a constraint (validation gate, type check, pre-condition) — don't patch the agent
- Example: "The executor can write to files outside the declared scope — add scope enforcement"

> **Key finding:** Adding a single constraint improved system reliability from 64.9% to 86.2% in the source study. Constraints beat corrections.

---

## 3. Sensitivity Analysis — Where to Invest Guards

Not all phase failures are equal. Rank by **downstream impact**, not frequency:

```
For each phase that has ever failed:
  1. Fix that phase's reliability to 0% (assume it fails)
  2. Estimate: how many downstream phases break?
  3. Estimate: what's the rework cost?
  4. Rank phases by total downstream damage

Result: The phase with the highest damage multiplier
        gets the most verification investment
```

**Common surprise:** The rarest failure with the highest downstream cost should get the most guard investment. A planning failure that happens 5% of the time but invalidates 3 downstream phases is worse than an execution failure that happens 20% of the time but is locally contained.

---

## 4. Probability Completeness

Every decision diamond must have exhaustive branches. No implicit "otherwise":

```
BAD:  "If verification passes → proceed to handoff"
      (What happens if it fails? Undefined.)

GOOD: "If verification passes → proceed to handoff
       If verification fails with fixable issues → re-execute with gaps
       If verification fails with architectural issues → re-plan
       If verification fails 3 times → dead-end shelf + escalate"
```

**Rule:** If the branches from a decision point don't cover 100% of outcomes, the workflow has a structural defect.

---

## 5. Early Non-Functional Analysis

> "Early evaluation of software properties is important in order to reduce costs before resources have been allocated and decisions have been made."

The highest-leverage phase is **planning** — not because planning is intrinsically valuable, but because:
- Defect caught in planning = 1 iteration to fix
- Same defect caught in execution = 5 iterations
- Caught in production = indefinitely more

**Agent action:** Before executing, verify the plan's non-functional properties: Is the architecture coherent? Are the dependencies resolvable? Is the scope verifiable? These questions cost 30 seconds to check and save hours of rework.

---

## When Agents Should Reference This Skill

- **fire-planner:** Before generating a plan, assess transition probabilities between phases
- **fire-verifier:** After verification, run implied scenario check on multi-agent outputs
- **fire-executor:** Before starting a task with < 60% component reliability, route to research
- **fire-researcher:** When analyzing why a phase failed, use sensitivity analysis to prioritize
