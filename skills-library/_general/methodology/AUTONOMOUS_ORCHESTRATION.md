---
name: AUTONOMOUS_ORCHESTRATION
category: methodology
description: Industry patterns for autonomous AI agent orchestration — Planner/Worker/Judge separation, scope manifests, DORA metrics, phase-gate hybrids, and supervised autonomy tiers
version: 1.0.0
tags: [autonomous, orchestration, agents, planner-worker-judge, dora, phase-gate, scope]
sources:
  - "Mike Mason — AI Coding Agents in 2026: Coherence Through Orchestration"
  - "Anthropic Engineering — Effective Harnesses for Long-Running Agents"
  - "OpenHands SDK — arxiv 2511.03690"
  - "Google DORA — State of DevOps 2025"
  - "Robert Cooper — Agile-Stage-Gate Hybrids"
  - "AWS — Agentic AI Security Scoping Matrix (TBAC)"
  - "SWE-Bench Pro — Can AI Agents Solve Long-Horizon Tasks?"
---

# Autonomous Orchestration Patterns

> **Core insight:** "You don't trust; you instrument." (Boris Cherny) — Verification stays active. Verdicts auto-route to fix cycles. The human reviews the finished product, not intermediate steps.

---

## 1. Planner / Worker / Judge Separation

The architecture that consistently outperforms alternatives in autonomous coding research:

| Role | Can Do | Cannot Do | Dominion Flow Equivalent |
|------|--------|-----------|------------------------|
| **Planner** | Read codebase, decompose tasks, set scope | Write code, modify files | fire-planner |
| **Worker** | Execute scoped tasks, write code | Plan, verify own work, exceed scope | fire-executor |
| **Judge** | Run verification, read output, report findings | Fix what it finds broken, modify code | fire-verifier |

**Why this matters:** The most dangerous failure mode in autonomous AI is the agent judging its own work. The worker cannot declare itself done. The judge cannot fix what it finds. This separation is load-bearing architecture, not process overhead.

**Anti-pattern:** "The executor also checks if things work" — this is the worker judging itself. SWE-Bench Pro data shows agents that self-verify have significantly lower success rates than those with independent verification.

---

## 2. Scope Manifests (Task-Based Access Control)

Every task should include a scope boundary:

```yaml
scope:
  allowed_files:
    - "server/routes/auth.js"
    - "server/middleware/auth.js"
    - "server/models/User.js"
  allowed_operations:
    - create_file
    - modify_file
    - run_tests
  forbidden:
    - modify files outside allowed_files
    - install new dependencies without plan approval
    - delete existing tests
  max_file_changes: 5
```

**Why explicit scope:** Agents drift without manifest enforcement. Conversational instructions ("only change the auth files") are less reliable than tool-level constraints. The circuit breaker should trip if the agent attempts out-of-scope actions.

**Agent action:** fire-planner includes scope in BLUEPRINT frontmatter. fire-executor reads scope before starting. fire-verifier checks that changes stayed within scope.

---

## 3. External Structured State > Long Context

From Anthropic's engineering blog: context window amnesia is solved by structured external state, not by longer context windows.

### The Pattern
```
Session start:
  1. Read CONSCIENCE.md → current phase/status
  2. Read latest WARRIOR handoff → prior session context
  3. Read RECORD.md → what was done, what's pending
  4. Read FAILURES.md → dead ends to avoid

Session end:
  1. Update CONSCIENCE.md → new status
  2. Write WARRIOR handoff → structured state for next session
  3. Update RECORD.md → what was accomplished
  4. Commit checkpoint
```

**Why:** A 200K context window that includes irrelevant history is worse than a 50K window with precisely structured state. External state files are the memory — the context window is the working space.

**Key from OpenHands:** Use an append-only event log for mutable state. When history approaches context limits, summarize old events while preserving the full log. Reduced API costs 2x with no performance degradation.

---

## 4. Supervised Autonomy Tiers

The industry is converging on three tiers:

| Tier | Risk Level | Oversight | Dominion Flow Mode |
|------|-----------|-----------|-------------------|
| **Human-in-the-loop** | High | Approval required before action | Manual `/fire-3-execute` |
| **Human-on-the-loop** | Medium | Autonomous with monitoring + escalation | `/fire-autonomous` |
| **Human-out-of-the-loop** | Low | Fully autonomous, periodic audit | Future: batch mode |

**Confidence thresholds drive tier assignment:**
- Routine tasks (boilerplate, config): 80% confidence → auto-proceed
- Business logic tasks: 85% confidence → auto-proceed, flag for review
- Architecture decisions: 90% confidence → require explicit approval

**Industry benchmark:** Operational escalation rates above 15% indicate confidence thresholds are miscalibrated — too much is being auto-approved or too little.

---

## 5. DORA Metrics for AI-Assisted Development

The 2025 DORA Report finding: **AI adoption improves throughput but increases delivery instability.** Faster output with more failures.

| Metric | What It Measures | AI-Agent Equivalent |
|--------|-----------------|-------------------|
| **Deployment Frequency** | How often to production | Phases completed per session |
| **Change Lead Time** | Commit → production | Plan → verified output |
| **Change Failure Rate** | % of deploys causing incidents | % of phases requiring re-execution |
| **Recovery Time** | Mean time to restore | Time from verification FAIL to PASS |

**The key insight:** Optimizing throughput (more phases faster) without measuring stability (failure rate, recovery time) produces more bugs faster. Both dimensions must be tracked.

**Agent action:** The autonomous log should track both: phases completed AND phases that needed retry. A session that completes 3 phases cleanly is better than one that completes 5 phases with 3 retries each.

---

## 6. Phase-Gate + Agile Hybrid

The sweet spot for AI-assisted development:

```
MACRO: Phase-gate discipline at boundaries
  Plan → [GATE] → Execute → [GATE] → Verify → [GATE] → Handoff

  Gates are non-negotiable. The project cannot advance
  without passing verification.

MICRO: Agile flexibility within phases
  Within Execute: iterate freely on tasks
  Within Verify: scope-adaptive checks
  Within Plan: explore alternatives
```

**Definition of Ready (before starting a phase):**
- [ ] Phase requirements clear (MEMORY.md populated)
- [ ] Dependencies from prior phase resolved
- [ ] Scope bounded in BLUEPRINT
- [ ] Kill conditions defined for high-risk tasks

**Definition of Done (before declaring phase complete):**
- [ ] All BLUEPRINT tasks executed
- [ ] Verification APPROVED or CONDITIONAL
- [ ] Review completed (no BLOCK findings)
- [ ] RECORD.md updated
- [ ] CONSCIENCE.md advanced

---

## 7. What Fails in Autonomous Mode

From SWE-Bench Pro and industry analysis — failure modes to watch for:

| Failure Mode | Symptom | Prevention |
|-------------|---------|-----------|
| **Premature termination** | Agent declares "done" before end-to-end verification | Judge must verify, not worker |
| **Scope creep** | Agent fixes "related" issues outside scope | Scope manifest enforcement |
| **Context overflow** | Endless file reading, losing track | Condensation + structured state |
| **Quality degradation at scale** | More output but more bugs | Track change failure rate alongside throughput |
| **Semantic misunderstanding** | Solution passes tests but misses the point | Verify against requirements, not just tests |
| **Self-certification** | Agent says "looks good" without running checks | Mandatory verification gates |

**The hardest failure:** Semantic misunderstanding — the agent produces code that is technically correct but doesn't solve the actual problem. Tests pass because the tests test the wrong thing. This is only caught by requirements-level verification, not code-level verification.

---

## When Agents Should Reference This Skill

- **fire-autonomous:** Apply supervised autonomy tiers, track DORA metrics in autonomous log
- **fire-planner:** Include scope manifests and kill conditions in BLUEPRINTs
- **fire-executor:** Respect scope boundaries, never self-verify
- **fire-verifier:** Independent judge role — verify against requirements, not just tests
- **fire-5-handoff:** Structure handoff as external state for next session (not narrative)
