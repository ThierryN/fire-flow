---
name: REQUIREMENTS_DECOMPOSITION
category: methodology
description: Turn vague requirements into testable specifications using utility trees, ATAM tradeoff analysis, and weighted decision matrices — never accept Level 1 input for execution
version: 1.0.0
tags: [requirements, decomposition, utility-tree, atam, weighted-decision-matrix, tradeoffs]
sources:
  - "CMU SEI — How to Address Poorly-Defined Requirements in Software System Design (Nov 2025)"
  - "Dr. Lori Flynn, Lyndsi Hughes — Carnegie Mellon University Software Engineering Institute"
  - "IEEE — Software Quality Definition"
  - "ATAM — Architecture Tradeoff Analysis Method"
---

# Requirements Decomposition

> **Core insight:** "Never accept a vague requirement as input to any agent task — always decompose to Level 4 before beginning execution." A requirement you can't test is a requirement you can't verify.

---

## 1. The Four-Level Decomposition (Utility Tree)

Every requirement must be drilled from vague to testable:

```
Level 1: Quality Attribute (vague)
  "Good security"

Level 2: Sub-factors (decomposed concerns)
  Data Protection, Auth, Security Logging, Compliance

Level 3: Refined Sub-factors (actionable concerns)
  Encrypt data at rest, Restrict access, Log unauthorized access

Level 4: Requirements (specific, testable, implementable)
  "FIPS 140-2 validated encryption", "RBAC with role hierarchy",
  "Failed auth attempts logged with IP + timestamp"
```

**Rule:** You cannot start execution on a Level 1 or Level 2 requirement. If a user says "make it secure" or "add good error handling," decompose FIRST.

**Agent action:** fire-planner decomposes every requirement to Level 4 before generating BLUEPRINT tasks. Each Level 4 entry must have a corresponding test/verification criterion.

---

## 2. Tradeoff Analysis (ATAM)

Requirements exist in tension. You cannot maximize everything:

| Tension | Example |
|---------|---------|
| Security vs. Performance | Encryption adds latency |
| Flexibility vs. Simplicity | More config options = more complexity |
| Speed-to-market vs. Quality | Shortcuts now = rework later |
| Feature richness vs. Maintainability | More features = more surface area |

**The ATAM goal:** "Elicit, concretize, and prioritize the driving quality attribute requirements."

**Agent action:** When a plan has competing quality attributes, surface the tradeoff explicitly:
```markdown
## Tradeoff: {Attribute A} vs. {Attribute B}

Decision: Prioritize {A} because {reason}
Consequence: {B} will be {specific impact}
Mitigation: {what we'll do to limit the downside}
```

**Never silently resolve a tradeoff.** The user should know what they're trading away.

---

## 3. Weighted Decision Matrix (WDM)

When choosing between approaches, score mathematically:

```
Score = Σ (weight_i × rating_i) for each criterion

Where:
  weight_i = stakeholder priority (sum to 1.0)
  rating_i = how well this option satisfies criterion i
```

### Weight Calculation (Rank-to-Linear)
```
weight = 2r / N(N+1)
  where r = priority rank, N = total criteria count
```

### Scaling Convention
- Higher raw value = better → use R directly (coverage %, security score)
- Higher raw value = worse → use 1/R (cost, latency, error rate)
- Normalize to comparable magnitude before multiplying

**Agent action:** When fire-planner or fire-researcher evaluates 2+ approaches, use WDM scoring instead of subjective "I think approach A is better." Present the scored comparison to the user.

---

## 4. Requirements Handoff Gate

Requirements are ready for execution when ALL of these are true:

- [ ] **Tradeoffs are known** — you understand what you're giving up
- [ ] **Threats to quality are mitigated** — identified and addressed
- [ ] **Requirements are precisely defined** — not vague
- [ ] **Requirements are measurable** — you can test and get a number
- [ ] **Requirements are prioritized** — ranked by importance
- [ ] **Requirements have test criteria** — each requirement maps to a verification step

**If this gate fails:** Send back for clarification. Do NOT start building on vague requirements — that's how Frankenstein projects are born.

---

## 5. Behavioral Discovery (Post-Build Requirements)

Some requirements are discovered after building, not before:

| Discovery Type | Action |
|----------------|--------|
| **New behavior we want** | Add as new requirement, add test |
| **Behavior that violates a requirement** | File as defect, fix |
| **Behavior we consciously accept** | Document as acknowledged risk |
| **Behavior not in spec at all** | Classify: is it positive implied scenario or negative? |

This maps to the implied scenario detection pattern from RELIABILITY_PREDICTION.md — composition reveals behaviors no individual specification predicted.

---

## 6. Scenario Elicitation for AI Agents

When gathering requirements from users who don't know exactly what they want:

### Seed Scenario Technique
Present high-level context descriptions to anchor the conversation:
- "This is a SaaS platform for small businesses" (seed)
- "Given that context, what matters most — speed to market, enterprise security, or cost efficiency?" (elicit priority)
- "What could go wrong that would be unacceptable?" (elicit constraints)
- "What must always work, even if other things break?" (elicit critical paths)

### Quality Attribute Building Blocks
For each stated concern, ask three questions:
1. **Concerns:** What are you worried about?
2. **Factors:** What sub-dimensions define this?
3. **Methods:** How will we achieve it?

This converts stakeholder stories into technical requirements without requiring technical language.

---

## When Agents Should Reference This Skill

- **fire-1a-discuss:** Use utility tree decomposition during requirement gathering
- **fire-planner:** Decompose to Level 4 before generating BLUEPRINT tasks
- **fire-researcher:** Use WDM when comparing alternative approaches
- **fire-verifier:** Verify against Level 4 requirements, not Level 1 descriptions
- **fire-vision-architect:** Surface tradeoffs explicitly when presenting architecture branches
