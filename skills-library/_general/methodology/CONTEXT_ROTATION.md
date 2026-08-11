---
name: CONTEXT_ROTATION
category: methodology
description: Fresh-eyes debugging science — when and how to rotate context to break fixation, with cognitive science backing and practical protocols for AI agent handoffs
version: 1.0.0
tags: [context-rotation, fresh-eyes, fixation, incubation, debugging, handoff]
sources:
  - "Duncker (1945) — Functional Fixedness"
  - "Springer Memory & Cognition — Interrupted distributed effort and incubation"
  - "Psychology Today — Rubber Duck Debugging Psychology"
  - "Frontiers in Education — Functional Fixedness in Problem Solving"
  - "The Decision Lab — Functional Fixedness bias"
---

# Context Rotation Protocol

> **Core insight:** A stuck agent with degraded context is the worst possible solver. A fresh agent with full context and documented prior attempts is the best. Context window length is a fixation risk, not just a token limit.

---

## 1. The Science of Getting Stuck

### Functional Fixedness (Duncker, 1945)
Once a problem-solver commits to a conceptual framing, they become blind to alternative framings — even when the solution is obvious in retrospect. Five-year-olds solve certain problems faster than adults because they have less fixation on conventional uses.

**For AI agents:** An agent that has spent 4+ exchanges approaching a bug as a data model issue will continue framing it as a data model issue even when symptoms clearly suggest concurrency. The longer the context window stays focused on one framing, the deeper the fixation.

### Incubation Effect
Research shows approaching problems "briefly and repeatedly" rather than continuously reduces fixation:
- Stopping work BEFORE hitting a wall preserves the ability to restructure
- Incubation specifically benefits **insight problems** (where the wrong approach actively blocks the right one)
- Less effective for **analytical problems** (where grinding produces incremental progress)

**Classification question before rotation:** Is this a grinding problem (try harder) or an insight problem (fixation is the enemy)? The answer determines whether iteration or rotation is correct.

---

## 2. When to Rotate Context

| Signal | Type | Action |
|--------|------|--------|
| Same approach, 3+ syntax variations | Fixation | Rotate immediately |
| Context compaction just happened | Degradation | Consider rotation |
| Agent confidence dropping each attempt | Diminishing returns | Rotate after next failure |
| "I've tried everything I can think of" | Exhaustion | Rotate with full dead-end map |
| Different approach, same class of error | Deeper issue | Research first, then rotate if no resolution |

### When NOT to Rotate
- Transient errors (API timeout, build cache) — retry is cheaper
- Missing information (credentials, config) — human input needed, not fresh eyes
- Making steady progress — don't fix what isn't broken

---

## 3. What the Fresh Agent Receives

**Critical rule:** Give the fresh agent the dead-end MAP, not the dead-end JOURNEY.

### Give:
```markdown
## Problem Context for Fresh Instance

**Goal:** {what needs to be accomplished}
**Current state:** {what exists, what's working}

**Approaches tried (outcome map):**
1. {approach} → Failed because: {root cause}
2. {approach} → Failed because: {root cause}
3. {approach} → Failed because: {root cause}

**Constraints identified:**
- {constraint 1 — verified, not assumed}
- {constraint 2 — verified, not assumed}

**Untested hypotheses:**
- {idea 1 — why it might work}
- {idea 2 — why it might work}

**Relevant files:** {specific paths}
```

### Do NOT give:
- Full conversation history (propagates the original framing/fixation)
- Emotional language ("this is really frustrating", "nothing works")
- Vague descriptions ("I tried a bunch of things")

**Why:** The fresh agent needs boundary knowledge (where NOT to walk) and starting context (where TO start). It does not need the journey narrative — that's what created the fixation in the first place.

---

## 4. Articulation Protocol (Rubber Duck Step)

Before any rotation, require the stuck agent to produce a structured articulation:

```markdown
## Articulation (Pre-Rotation)

1. What I was trying to do: {goal in one sentence}
2. What I expected to happen: {specific expected behavior}
3. What actually happened: {specific actual behavior}
4. What I believe the constraint is: {my theory}
5. What assumption am I making that might be wrong: {honest assessment}
```

**Why this works:** Explaining the problem forces sequential, explicit reconstruction of assumptions. The language encoding activates different cognitive pathways than pattern-matching. Research shows this catches 30-40% of stuck cases without needing rotation — the stuck agent solves it by articulating it.

**Agent action:** Always run the articulation step BEFORE spawning a fresh agent. If the articulation reveals the issue, save the rotation cost.

---

## 5. Context Window as Fixation Accumulator

Every exchange in a long session adds fixation weight:

```
Session start: fixation_risk = LOW
  After 10 exchanges on same topic: fixation_risk = MEDIUM
  After 20 exchanges on same topic: fixation_risk = HIGH
  After context compaction: fixation_risk = ELEVATED
    (compaction removes details but preserves framing bias)
```

**Mitigation strategies (in order of preference):**
1. **Articulation protocol** — cheapest, catches 30-40%
2. **Scope switch** — work on a different task, come back later
3. **Research injection** — read external docs/code to introduce new framing
4. **Fresh agent with dead-end map** — full context rotation
5. **Human clarification** — the human may see what both agents missed

---

## 6. The Navigator Pattern (from Pair Programming)

In pair programming research, the **navigator role** (observer, not typist) has the highest fresh-eyes effect — they see what the driver's fixation hides.

**Applied to Dominion Flow:** The fire-verifier IS the navigator. It reads the executor's output from outside the execution context. This is why verifier isolation (separate instance, fresh context) is architecturally important — not just for objectivity, but for fixation prevention.

**Role rotation frequency:**
- Every task boundary = natural rotation point
- Every phase boundary = mandatory rotation point (WARRIOR handoff)
- Mid-task rotation = only when stuck signals detected

---

## When Agents Should Reference This Skill

- **fire-executor:** Run articulation protocol when stuck, classify grinding vs. insight before retrying
- **fire-verifier:** Leverage navigator advantage — flag issues the executor's fixation may hide
- **fire-6-resume:** Fresh instance = natural context rotation. Read dead-end map, not prior session transcript
- **fire-autonomous:** Monitor fixation risk in long sessions, trigger rotation at HIGH
- **Any agent writing a WARRIOR handoff:** Structure handoff as a dead-end map (outcomes, not journey)
