# Research-Backed Improvements Reference

> Dominion Flow v3.2 — Research sources, gap analysis findings, and implementation mapping
>
> Every v3.2 enhancement cites a tag from this document (e.g., `GAP-1`, `RECITATION-1`).
> Use this file to trace any inline comment back to its research basis.

---

## Research Sources (2024–2026)

### Academic Papers

| ID | Paper | Key Finding | Applied In |
|----|-------|-------------|------------|
| PLAN-DEBUG-1 | MapCoder (ACL 2024) — "Multi-Agent Code Generation through Planning" | Achieved 93.9% pass@1 by feeding the Debugging Agent the original plan alongside buggy code. Plan-derived debugging significantly outperforms debugging without plan context because the agent can compare "what was intended" vs "what happened." | `/fire-debug` Step 4: `<plan_context>` block |
| RECITATION-1 | Manus AI — Context Engineering (2025) | Without task recitation, agents drift off-topic after ~50 tool calls. Rewriting a compressed todo at the end of context keeps the current plan in the model's recent attention span, preventing the "lost-in-the-middle" problem (transformer attention bias toward recent tokens). | `/fire-loop` Step 7 rule 6, iteration context injection |
| OBSERVE-1 | Mastra — Observational Memory (2025) | Two-agent (Observer/Reflector) compression achieves 5-40x compression with 10x cost reduction over RAG. Observer extracts key facts; Reflector synthesizes patterns. | Future: Tier 2 enhancement |
| JUDGE-1 | Mason (2026) — "Judge Agent Separation" | Dedicated Judge agent that only evaluates (never generates) prevents self-evaluation bias. Separating generation from evaluation improves quality scoring accuracy. | Future: Tier 3 enhancement |
| SWE-1 | SWE-Bench Pro (2025) | Single agent + retries outperforms multi-agent swarms for most routine tasks. Multi-agent overhead only justified for genuinely parallel work. | Informs execution mode intelligence (SWARM threshold) |
| METR-1 | METR Study (2025) — "AI Impact on Developer Productivity" | AI can slow experienced devs 19% on familiar code. AI excels at exploration and unfamiliar codebases, not well-known code. | Informs when to apply AI vs manual work |
| RLCR-1 | MIT RLCR (2025) — "Confidence-Based Escalation" | Route low-confidence items to human review instead of auto-deciding. Confidence thresholds improve decision quality across automated workflows. | Future: Tier 2 enhancement |

### Community Patterns

| ID | Source | Pattern | Applied In |
|----|--------|---------|------------|
| CNCF-1 | CNCF Four Pillars (2025) | Golden Paths, Guardrails, Safety Nets, Manual Review — taxonomy for organizing validation checklists by enforcement level. | Future: restructure 70-point checklist |
| BOLT-1 | Bolt.new — .powerignore (2025) | File-level exclusion patterns prevent context pollution from generated files, node_modules, etc. | v3.0: `.powerignore` in context engineering |
| RALPH-1 | Ralph Wiggum Loops — Circuit Breaker Fork | Stall/spin/degradation detection with automatic recovery. Prevents infinite loops and wasted iterations. | v3.0: Circuit Breaker system |
| REPLIT-1 | Replit Agent — Decision-Time Guidance (2025) | Micro-inject relevant skills at the moment of decision rather than front-loading all knowledge. Reduces context bloat while maintaining quality. | v3.0: DTG system |

---

## Gap Analysis Findings

> Internal analysis of Dominion Flow v3.1 identified these gaps.
> Each gap has a severity, the v3.2 fix applied, and the file modified.

### GAP Series (Structural Gaps)

| ID | Gap Description | Severity | v3.2 Fix | File Modified |
|----|----------------|----------|----------|---------------|
| GAP-1 | No explicit decision log — architectural decisions scattered across handoffs and CONSCIENCE.md with no central tracking | HIGH | Created `DECISION_LOG.md` template with DEC-XXX format, cross-phase impact tracking, and integration points | `templates/DECISION_LOG.md` (new) |
| GAP-2 | Assumptions accumulate across phases without systematic tracking — Phase 6 can contradict Phase 1 assumptions | HIGH | Enhanced `ASSUMPTIONS.md` with cross-phase contradiction detection, phase-gate validation protocol | `templates/ASSUMPTIONS.md` |
| GAP-3 | No cross-phase contradiction detection for decisions | MEDIUM | Decision Log includes "Affected Phases" and cross-phase validation protocol | `templates/DECISION_LOG.md` |
| GAP-4 | Deferred items multiply without compound impact tracking | MEDIUM | Added deferred-item impact analysis template (DEFERRED-XXX format) to Assumptions | `templates/ASSUMPTIONS.md` |
| GAP-5 | Handoff completeness not validated — broken context chains if any session skips proper handoff | HIGH | Added 17-point automated validation checklist as Step 5 in handoff command | `commands/fire-5-handoff.md` |
| GAP-6 | Task recitation missing — agents drift after many iterations in fire-loop | HIGH | Added recitation pattern to iteration context injection with compressed todo rewrite | `commands/fire-loop.md` |
| GAP-7 | Debug loops lack plan context — debugger can't compare intended vs actual behavior | MEDIUM | Added `<plan_context>` block to debugger spawn and continuation prompts | `commands/fire-debug.md` |
| GAP-8 | CONSCIENCE.md doesn't reference Decision Log | LOW | Added Decision Log reference and Assumptions Health section to state template | `templates/state.md` |
| GAP-9 | Handoff success criteria don't include Decision Log or Assumptions sync | LOW | Added 3 new items to handoff success criteria | `commands/fire-5-handoff.md` |
| GAP-10 | No executable handoff validation — relies on manual review | HIGH | 17-point checklist with structural, content, and cross-reference checks | `commands/fire-5-handoff.md` |

### BLIND-SPOT Series (Discovered During Analysis)

| ID | Blind Spot | Impact | v3.2 Fix |
|----|-----------|--------|----------|
| BLIND-SPOT-A | Decisions made in one phase can silently conflict with decisions from earlier phases | Cross-phase bugs, wasted work | Decision Log cross-phase validation protocol |
| BLIND-SPOT-B | Unvalidated assumptions from early phases relied upon in later phases without re-check | Architecture built on unverified foundations | Phase-gate validation: mandatory assumption audit at phase start |
| BLIND-SPOT-C | Context drift in long fire-loop runs leads to repeated mistakes and circular attempts | Wasted iterations, degraded solutions | Task recitation pattern forces model to re-read compressed state |
| BLIND-SPOT-D | Handoff chain breaks permanently if one session skips proper handoff | Complete context loss, restart required | Automated completeness validation prevents saving incomplete handoffs |

---

## Implementation Mapping

### Tier 1 — Implemented in v3.2.0

| Enhancement | Research Basis | Files Changed |
|-------------|---------------|---------------|
| Decision Log template | GAP-1, GAP-3, BLIND-SPOT-A | `templates/DECISION_LOG.md` (new) |
| Assumptions Registry enhancement | GAP-2, GAP-4, BLIND-SPOT-B | `templates/ASSUMPTIONS.md` |
| CONSCIENCE.md Decision/Assumptions references | GAP-8 | `templates/state.md` |
| Handoff Completeness Validator | GAP-5, GAP-9, GAP-10, BLIND-SPOT-D | `commands/fire-5-handoff.md` |
| Task Recitation Pattern | RECITATION-1, GAP-6, BLIND-SPOT-C | `commands/fire-loop.md` |
| Plan-Aware Debugging | PLAN-DEBUG-1, GAP-7 | `commands/fire-debug.md` |
| Plugin version bump + this doc | — | `plugin.json`, `references/research-improvements.md` |

### Tier 2 — Planned for v3.3.0

| Enhancement | Research Basis | Target |
|-------------|---------------|--------|
| Observational Memory (Observer/Reflector agents) | OBSERVE-1 | Handoff compression, cross-session learning |
| Confidence-Based Escalation | RLCR-1 | Route uncertain decisions to user during execution |
| CNCF Four Pillars restructure | CNCF-1 | Reorganize 70-point checklist by enforcement level |
| METR-aware task routing | METR-1 | Route AI to exploration tasks, manual for familiar code |

### Tier 3 — Planned for v3.4.0

| Enhancement | Research Basis | Target |
|-------------|---------------|--------|
| Judge Agent separation | JUDGE-1 | Dedicated evaluation agent for verification |
| SWE-Bench calibrated execution modes | SWE-1 | Better SWARM vs SEQUENTIAL thresholds |
| Skills Library auto-pruning | Community patterns | Remove unused skills, version popular ones |

---

## Version History

| Version | Date | Key Additions |
|---------|------|---------------|
| v3.0.0 | 2026-02-09 | Dominion Flow consolidation, Circuit Breaker, Error Classification, Context Engineering, DTG |
| v3.1.0 | 2026-02-10 | Playwright E2E testing (Step 8), 70-point validation, visual regression |
| v3.2.0 | 2026-02-10 | Research-backed: Task Recitation, Plan-Aware Debug, Decision Log, Assumptions enhancement, Handoff Validator, Code Comments Standard |

---

*Created: 2026-02-10*
*Source: 4-agent parallel research sweep (15 papers + 15 community patterns + 10 testing findings + 10 internal gaps)*
