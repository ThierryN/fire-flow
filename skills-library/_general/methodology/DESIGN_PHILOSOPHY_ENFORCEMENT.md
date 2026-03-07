---
name: design-philosophy-enforcement
category: methodology
version: 1.0.0
contributed: 2026-03-06
contributor: dominion-flow
last_updated: 2026-03-06
contributors:
  - dominion-flow
tags: [architecture, audit, principles, enforcement, agents, meta-design]
difficulty: hard
usage_count: 0
success_rate: 100
---

# Design Philosophy Enforcement

## Problem

Multi-agent systems document design principles (honesty, research-first, plan-before-execute) but fail to **structurally enforce** them. Principles live in philosophy docs while the actual agent wiring contradicts or ignores them. The gap between stated values and implemented behavior grows silently over versions until the system's behavior no longer matches its stated identity.

Common symptoms:
- Agents document uncertainty but don't route to research
- "Plan right, execute once" is stated but execution can skip planning
- Failure states escalate to the user instead of triggering the system's own research capabilities
- One-size-fits-all processes (e.g., 70-point checklists) contradict "on-demand over ceremony"
- Circuit breakers stop the system instead of routing to recovery paths

## Solution Pattern

Audit every principle against three dimensions, then wire missing enforcement into the architecture:

### The Three-Dimensional Audit

For each stated design principle, answer:

1. **STRONG AT** — Where is this principle already structurally enforced? (file:section reference + why it works)
2. **WEAK AT** — Where is it documented but not wired? (file:section reference + what's missing)
3. **CONTRADICTED AT** — Where does the system accidentally work against it? (file:section reference + what conflicts)

### Enforcement Categories

Principles can be enforced at four levels (weakest to strongest):

| Level | Name | Example | Strength |
|-------|------|---------|----------|
| 1 | **Documented** | "Agents should research when stuck" | Weakest — ignored under pressure |
| 2 | **Prompted** | Honesty Gate asks "Am I tempted to rush?" | Medium — agent can answer dishonestly |
| 3 | **Gated** | Plan-checker must approve before execution starts | Strong — blocks progress without compliance |
| 4 | **Structural** | Executor literally cannot start without BLUEPRINT files existing | Strongest — architecturally impossible to violate |

**The audit goal:** Identify principles stuck at Level 1-2 that should be at Level 3-4.

### The Probe Questions

Use these specific questions to find enforcement gaps:

1. **Failure-path routing:** When an agent hits a wall, does the system route to its own research/recovery capabilities, or does it just stop/escalate?
2. **Honesty reward loop:** When an agent admits "I don't know," does the architecture automatically trigger research, or just document the admission?
3. **Ceremony detection:** Are there mandatory processes that run regardless of scope? Do small changes get the same heavyweight treatment as large features?
4. **Skip-ability:** Can agents bypass stated requirements via flags (--skip-verify, --quick) that exist "for convenience" but undermine the principle?
5. **Capability matching:** Do agents that encounter problems have the tools to solve them? (e.g., does the verifier have web search when it encounters unfamiliar failures?)
6. **Cross-gap clustering:** Do enforcement gaps cluster in one area (e.g., all at failure-time transitions, all in one agent, all in one phase)?

### The Fix Pattern

For each gap found, apply the minimum enforcement level that closes it:

```
IF principle is violated because agents don't know about it:
  → Level 2: Add to agent prompt/honesty gate

IF principle is violated because agents can skip it:
  → Level 3: Add a gate (file existence check, status field, approval step)

IF principle is violated because the architecture allows bypass:
  → Level 4: Remove the bypass, restructure the flow

IF principle is contradicted by another mechanism:
  → Resolve the contradiction: one must yield
  → Usually the contradicting mechanism is older and was never updated
```

## Code Example

```markdown
// Before (principle documented but not enforced)

## Design Philosophy
- "Research when hitting a wall" — don't brute-force

## Circuit Breaker (in executor)
IF same error 5+ times:
  → STOP. Escalate to user.
  // Gap: system has a researcher agent but doesn't use it here

// After (principle structurally enforced)

## Circuit Breaker (in executor)
IF same error 3+ times:
  → WARNING: Spawn fire-researcher with error context
  → Researcher returns 2-3 alternatives (ranked by confidence)
  → Retry with top alternative

IF same error 5+ times AND researcher exhausted:
  → STOP. Escalate to user with research findings attached.
  // Now the principle is enforced: research happens before escalation
```

## Implementation Steps

1. **List all stated design principles** — extract from philosophy docs, READMEs, foundational documents
2. **For each principle, audit all agents and commands** — use the STRONG/WEAK/CONTRADICTED framework
3. **Identify enforcement level** for each principle in each location (Level 1-4)
4. **Flag gaps** where enforcement level is below what the principle requires
5. **Check for cross-gap patterns** — do gaps cluster in failure paths? in one agent? in one phase?
6. **Prioritize fixes** by how many principles a single change reinforces simultaneously
7. **Apply minimum viable enforcement** — don't over-gate; the lightest enforcement that closes the gap

## When to Use

- After major version releases of an agent framework (v11 audit before v12 work begins)
- When users report that the system "doesn't feel like it follows its own rules"
- When onboarding new agents or commands — verify they inherit all principle enforcement
- When a post-mortem reveals the system had the capability to prevent a failure but didn't use it
- Quarterly health checks on multi-agent architectures

## When NOT to Use

- On systems too small to have stated principles (single-script tools)
- During active feature development — audit between milestones, not during sprints
- When principles themselves need revision — update the principles first, then audit enforcement

## Common Mistakes

- **Auditing only the happy path** — most enforcement gaps appear at failure-time transitions (circuit breaker trips, low confidence, verification failures), not during successful execution
- **Adding more documentation instead of structural gates** — if agents already ignore Level 1-2 enforcement, adding more docs won't help; move to Level 3-4
- **Over-gating** — not every principle needs Level 4 enforcement; some are genuinely better as prompted guidelines
- **Fixing symptoms not patterns** — if gaps cluster in one area (e.g., all failure-path routing), fix the systemic pattern rather than patching each gap individually

## Related Skills

- [EVIDENCE_BASED_VALIDATION](../../methodology/EVIDENCE_BASED_VALIDATION.md)
- [INSTRUMENTATION_OVER_RESTRICTION](../../methodology/INSTRUMENTATION_OVER_RESTRICTION.md)
- [CONFIDENCE_GATED_EXECUTION](../../methodology/CONFIDENCE_GATED_EXECUTION.md)

## References

- Dominion Flow v11.3 principles audit (2026-03-06) — first application of this methodology
- The "Three Questions" honesty gate pattern — example of Level 2 enforcement done well
- Recovery Research Mode (4-tier cascade) — example of Level 4 structural enforcement
- ACE: Agentic Context Engineering (ICLR 2026) — adaptive playbooks as runtime principle enforcement
