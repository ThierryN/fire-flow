# ASSUMPTIONS.md Template

> **Origin:** Dominion Flow v2.0 - Assumption tracking and validation.
> **Enhanced in v3.2:** Added cross-phase contradiction detection, phase-gate validation,
> and deferred-item impact analysis. Research basis: Gap analysis found assumptions
> accumulate across phases without systematic tracking, leading to contradictions.
> See: references/research-improvements.md (GAP-1, GAP-2, BLIND-SPOT-B)

Template for `.planning/ASSUMPTIONS.md` — created by `/fire-1a-new`.

---

## File Template

```markdown
# Project Assumptions

## Summary
| Status | Count |
|--------|-------|
| Validated | 0 |
| Unvalidated | 0 |
| Invalidated | 0 |

---

## Phase Assumptions

### Phase XX: [Phase Name]

#### ASSUMPTION-001: [Short description]
- **Category:** Technical | Business | Infrastructure | Integration
- **Statement:** [The specific assumption being made]
- **Impact if wrong:** [What breaks if this assumption is false]
- **Validation method:** [How to verify - test, research, user confirmation]
- **Status:** VALIDATED | UNVALIDATED | INVALIDATED
- **Validated by:** [evidence or "pending"]
- **Phase:** [which phase relies on this]
- **Plan:** [which plan relies on this]

---

## Invalidated Assumptions

[Assumptions proven false - with impact assessment and remediation]

### ASSUMPTION-XXX: [description] (INVALIDATED)
- **Original assumption:** [what was assumed]
- **Reality:** [what turned out to be true]
- **Impact:** [what broke or needs changing]
- **Remediation:** [how it was addressed]
- **Blocker created:** [BLOCKER-XXX if applicable]
```

---

## Common Assumption Categories

| Category | Examples |
|----------|---------|
| Technical | "PostgreSQL supports JSON columns", "Next.js 15 has server actions" |
| Business | "Users will register with email", "Free tier limited to 3 projects" |
| Infrastructure | "Vercel supports WebSockets", "Redis available for caching" |
| Integration | "Stripe supports the currency", "OAuth provider supports PKCE" |

---

## When to Create Assumptions

- During `/fire-1a-discuss` (questioning phase)
- During `/fire-2-plan` (plan creation)
- During execution when uncertainty surfaces (honesty checkpoints)
- When research reveals "it should work but I haven't verified"

---

## Validation Triggers

- Before plan execution: validate UNVALIDATED assumptions for that plan
- During honesty pre-check: surface assumptions being relied on
- After phase completion: audit all assumptions for accuracy

---

## Cross-Phase Contradiction Detection (v3.2)

> Research finding: Phase 6 can contradict Phase 1 assumptions buried in old handoffs.
> This section prevents assumption drift across long-running projects.

### Phase-Gate Validation Protocol

At the START of each new phase, the planner MUST:

1. **List all ACTIVE assumptions** from previous phases that this phase relies on
2. **Check for contradictions** between existing assumptions and new plan requirements
3. **Flag stale assumptions** — any UNVALIDATED assumption older than 2 phases
4. **Verify invalidated assumptions** were actually remediated (not just flagged)

### Contradiction Detection Checklist

```markdown
## Phase N Pre-Flight: Assumption Validation

- [ ] Read all ACTIVE assumptions from Phases 1 through N-1
- [ ] No contradictions between existing assumptions and Phase N plan
- [ ] No UNVALIDATED assumptions older than 2 phases that affect this work
- [ ] All INVALIDATED assumptions have completed remediation
- [ ] New assumptions for Phase N are documented below
```

### Deferred Items Impact Analysis

> Research finding: Deferred items multiply without tracking their compound impact.
> Track each deferred item's blast radius to prevent Phase N from discovering
> all deferred items must be done immediately.

```markdown
### DEFERRED-001: [Short description]
- **Deferred in:** Phase N
- **Impact if deferred further:** CRITICAL | HIGH | MEDIUM | LOW
- **Blocking future phases:** [Phase X, Phase Y]
- **Compound risk:** [What happens if this + other deferrals combine]
- **Decision needed by:** Phase N+2 at latest
- **Owner:** [who should resolve this]
```
