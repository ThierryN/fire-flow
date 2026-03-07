---
name: CIRCUIT_BREAKER_INTELLIGENCE
category: methodology
description: Intelligent stuck-state detection with type classification, threshold tuning, dead-end engineering from Google X and NASA, and pre-defined kill conditions
version: 1.0.0
tags: [circuit-breaker, stuck-detection, dead-ends, google-x, kill-conditions, recovery]
sources:
  - "Microsoft Azure Architecture Center — Circuit Breaker Pattern"
  - "Martin Fowler — Circuit Breaker (bliki)"
  - "Google X — Moonshot Factory Operating Manual (Astro Teller)"
  - "NASA — Knowledge Transfer and Tacit Knowledge Loss"
  - "PMC — Drug Repurposing / ReFRAME compound library"
---

# Circuit Breaker Intelligence

> **Core insight:** Not all "stuck" states are the same. A syntax error, a fixation loop, and a fundamentally impossible approach each require different interventions. Classify before intervening.

---

## 1. Stuck-State Classification

Before triggering any recovery, classify the stuck type:

| Stuck Type | Symptom | Correct Intervention |
|------------|---------|---------------------|
| **Transient error** | Build/API failure, external dependency timeout | Wait + retry (standard circuit breaker) |
| **Fixation** | Same approach with varied syntax, 3+ attempts | Context rotation — fresh agent with dead-end map only |
| **Context overflow** | Endless file navigation, losing track of changes | Condensation + fresh context window |
| **Semantic misunderstanding** | Solution passes unit tests, fails integration | Human clarification — agent misunderstands the goal |
| **Dead end** | All viable approaches exhausted, research returned nothing | Shelf with wake conditions, escalate or pivot |
| **Scope violation** | Agent drifting outside declared file/tool boundaries | Re-read scope manifest, constrain tools |

**Agent action:** When hitting a wall, classify FIRST. Then apply the matching intervention. Don't use "retry harder" for fixation problems or "fresh eyes" for transient errors.

---

## 2. Three-State Circuit Breaker

```
CLOSED (normal):
  Task executes. Error counter tracks failures.

  IF same error pattern seen {threshold} times:
    → Trip to OPEN

OPEN (tripped):
  Stop executing this approach immediately.
  Route to: research → re-plan → or shelf

  Timeout: After research completes or new session starts
    → Move to HALF-OPEN

HALF-OPEN (probing):
  Try the researched alternative with limited scope.

  IF success: → Reset to CLOSED
  IF failure:  → Back to OPEN (shelf as dead end)
```

### Threshold Tuning
- **Transient errors:** threshold = 3 (retries are cheap)
- **Logic errors:** threshold = 2 (retries are expensive)
- **Architectural errors:** threshold = 1 (retry is pointless)

**Anti-pattern:** Single shared breaker for all failure types. Maintain per-strategy breakers — one broken approach shouldn't mask another healthy one.

---

## 3. Pre-Defined Kill Conditions (Google X Pattern)

> "Run at the hardest problem first." — Astro Teller, Google X

Before any task executes, define what would prove the approach unviable:

```yaml
kill_conditions:
  - "3 consecutive verification failures on same root cause"
  - "approach requires changing >5 files outside declared scope"
  - "same error repeats after 2 different fix strategies"
  - "external dependency does not support required feature"

wake_conditions:
  - "if {blocking dependency} releases version with {feature}"
  - "if {alternative library} becomes available"
  - "if user provides {missing credential/config}"
```

**Why define upfront:** Kill conditions defined AFTER failure are rationalizations. Kill conditions defined BEFORE execution are engineering discipline. Google X kills ~97% of projects at rapid evaluation — before significant resources are allocated.

**Agent action:** fire-planner should include 2-3 kill conditions per high-risk task in BLUEPRINT frontmatter. fire-executor checks these before retrying.

---

## 4. Dead-End Engineering

Dead ends are **first-class knowledge artifacts**, not failures to delete.

### What Makes a Good Dead-End Record

From NASA's knowledge loss lessons: if you only record WHAT failed but not WHY, the next agent will attempt the same approach. The "why" is the asset.

```markdown
### [DEAD-END] {title}

**What:** {what was attempted}
**Why it failed:** {root cause, not just symptom}
**Approaches tried:** {list with expected vs actual for each}
**Fundamental constraint:** {the thing that makes this approach unviable}
**Wake conditions:** {what would make this worth revisiting}
**Status:** SHELVED | ABANDONED | SUPERSEDED BY {task-id}
```

### The ReFRAME Principle (Drug Repurposing)
Pharmaceutical R&D maintains libraries of 12,000+ compounds that "failed" in one context but succeed when retested in new contexts. A dead end in Phase 3 may become the solution in Phase 7 when constraints change.

**Agent action:** Before starting a new task, grep FAILURES.md for `[DEAD-END]` entries with related tags. A prior dead end may now be viable if the context has changed.

---

## 5. Articulation Before Escalation (Rubber Duck Protocol)

Before routing to a fresh agent, human, or research:

```markdown
## STUCK REPORT

**Goal:** {what I was trying to accomplish}
**Approaches tried:**
  1. {approach} → Expected: {X} → Got: {Y}
  2. {approach} → Expected: {X} → Got: {Y}
**Current constraint:** {what is physically preventing progress}
**What a fresh approach needs:** {information or different framing}
**Confidence this approach is viable:** {high/medium/low + reason}
```

**Why this works:** The act of articulating the problem forces assumption reconstruction. In cognitive science research, this catches 30-40% of stuck cases before escalation — the stuck agent solves it by explaining it.

---

## 6. Error Discrimination

Not all errors carry equal signal:

| Error Type | Signal Strength | Action |
|------------|----------------|--------|
| Syntax/typo | Low (weight: 0.25) | Auto-fix, minimal signal toward threshold |
| Import/dependency missing | Medium (weight: 0.5) | Install/resolve, moderate signal |
| Logic error (wrong output) | High (weight: 1.0) | Count fully, consider re-plan after 2 |
| Architecture mismatch | Very high (weight: 2.0) | Count as 2, consider kill condition |
| Cross-phase contract break | Critical (weight: 3.0) | Stop immediately, investigate integration failure |

**Agent action:** Weight errors by type when evaluating circuit breaker thresholds. Three typos ≠ three architectural failures.

---

## When Agents Should Reference This Skill

- **fire-executor:** Classify stuck states, check kill conditions, write stuck reports
- **fire-planner:** Define kill conditions in BLUEPRINT frontmatter for high-risk tasks
- **fire-verifier:** Flag recurring failure patterns as potential dead ends
- **fire-researcher:** Read dead-end records before researching — avoid repeating prior approaches
- **fire-autonomous:** Use error budgets + kill conditions to decide retry vs. shelf vs. escalate
