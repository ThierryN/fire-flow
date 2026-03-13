# Configurable Autonomy Levels

> Graduated autonomy from fully supervised to fully autonomous — users choose how much control to retain at each decision point.

> agents need configurable autonomy, not binary on/off. Microsoft AutoGen "Human-in-the-Loop
> Patterns" (ICML 2024) — graduated autonomy with explicit checkpoints reduces user anxiety
> and increases adoption by 45%. Manus AI's "confidence-gated escalation" pattern — let the
> agent self-assess when to ask for help vs. proceed autonomously.

---

## Overview

Previous versions offered two modes: `--autonomous` (no checkpoints) and `--manual` (all checkpoints). This was too coarse — users either got interrupted too often or had zero visibility.

Configurable autonomy introduces **4 levels** that control exactly which decision points require human input.

---

## Four Autonomy Levels

### Level 1: SUPERVISED (equivalent to old `--manual`)

Every decision point pauses for human input.

```
Human input required at:
  ✓ Plan approval (BLUEPRINT.md review)
  ✓ Breath completion (approve before next breath)
  ✓ Merge gate (review combined verdict)
  ✓ Skill extraction (approve new skills)
  ✓ Gap closure (decide: fix vs. accept vs. re-plan)
  ✓ Phase completion (approve verification report)
  ✓ Handoff content (review before saving)

Best for:
  - Learning how Dominion Flow works
  - Security-sensitive projects
  - First time using the plugin
  - Projects where mistakes are expensive
```

### Level 2: GUIDED (new — recommended default)

Pauses only at major decision points. Auto-routes routine decisions.

```
Human input required at:
  ✓ Plan approval (BLUEPRINT.md review)
  ✗ Breath completion (auto-advance if no errors)
  ✓ Merge gate ONLY if verdict is REJECTED/BLOCK
  ✗ Skill extraction (auto-create, auto-scan)
  ✓ Gap closure (human decides: fix vs. accept)
  ✓ Phase completion (review verification report)
  ✗ Handoff content (auto-save)

Auto-routed:
  - Successful breath → next breath (logged)
  - APPROVED/CONDITIONAL merge → continue (logged)
  - Skill extraction → auto-create with security scan
  - Handoff → auto-save to warrior-handoffs/

Best for:
  - Day-to-day development
  - Projects you understand well
  - Balanced speed and oversight
```

### Level 3: AUTONOMOUS (equivalent to old `--autonomous`)

Only stops for blockers and failures. Maximum speed.

```
Human input required at:
  ✗ Plan approval (auto-approve if plan follows template)
  ✗ Breath completion (auto-advance always)
  ✓ Merge gate ONLY if REJECTED (critical failures)
  ✗ Skill extraction (auto-create, auto-scan)
  ✗ Gap closure (auto-fix minor, escalate critical)
  ✗ Phase completion (auto-approve if score ≥ 70%)
  ✗ Handoff content (auto-save)

Only stops for:
  - Circuit breaker TRIPPED
  - Verification score < 50% (critical failure)
  - BLOCKED state (external dependency)
  - Security finding (critical severity)

Best for:
  - Experienced users
  - Well-defined projects with good test coverage
  - /fire-autonomous and /fire-loop workflows
  - Overnight or unattended execution
```

### Level 4: SENTINEL (new — maximum autonomy with safety)

Full autonomy with a safety net. The agent runs completely unattended but
maintains a log of all decisions for post-hoc review.

```
Human input required at:
  ✗ Everything auto-routed
  ✓ ONLY stops for circuit breaker TRIPPED

Safety net:
  - ALL auto-decisions logged to .planning/sentinel-log.md
  - Confidence < 50% decisions flagged for review (but not paused)
  - Git tags created at each phase boundary for easy rollback
  - /fire-cost auto-runs every 3 breaths
  - Handoff auto-saved every 30 minutes

Post-hoc review:
  After completion, review .planning/sentinel-log.md:
  | Time | Decision Point | Auto-Action | Confidence | Flag |
  | ... | Merge gate | Auto-proceed | 85% | - |
  | ... | Gap closure | Auto-fixed | 72% | - |
  | ... | Skill extract | Auto-created | 90% | - |
  | ... | Phase verify | Auto-approved 68/70 | 65% | ⚠ LOW |

Best for:
  - Prototyping and experimentation
  - Tasks where speed matters more than precision
  - Projects with comprehensive test suites
  - Users who prefer review-after over approve-before
```

---

## Configuration

Set autonomy level per-project in `.planning/config.yml`:

```yaml
autonomy:
  level: guided  # supervised | guided | autonomous | sentinel

  # Override specific decision points regardless of level:
  overrides:
    plan_approval: always_pause      # always_pause | auto_approve | confidence_gated
    merge_gate: on_failure_only      # always_pause | on_failure_only | auto_route
    skill_extraction: auto_with_scan # always_pause | auto_with_scan | skip
    phase_completion: always_pause   # always_pause | score_gated | auto_approve
```

Set via command flags (per-session override):

```bash
# Set level for this execution
/fire-3-execute 2 --autonomy supervised
/fire-3-execute 2 --autonomy guided
/fire-3-execute 2 --autonomy autonomous
/fire-3-execute 2 --autonomy sentinel

# Legacy flags still work (mapped to levels)
/fire-3-execute 2 --manual        # → supervised
/fire-3-execute 2 --autonomous    # → autonomous
```

---

## Confidence-Gated Escalation

At any autonomy level, the agent can escalate to human input when confidence is low:

```
FOR each auto-routed decision:

  confidence = assess_confidence(decision_context)

  IF confidence >= 80%:
    → Auto-route. Log decision.

  IF confidence 50-79% AND level >= AUTONOMOUS:
    → Auto-route. Log with ⚠ flag for post-hoc review.

  IF confidence 50-79% AND level < AUTONOMOUS:
    → Pause for human input. Show confidence and reasoning.

  IF confidence < 50% (any level):
    → Pause for human input. Show full analysis.
    → Exception: SENTINEL level still auto-routes but flags for review.
```

---

## Decision Point Reference

| Decision Point | SUPERVISED | GUIDED | AUTONOMOUS | SENTINEL |
|---------------|-----------|--------|-----------|---------|
| Plan approval | Pause | Pause | Auto | Auto |
| Breath advance | Pause | Auto | Auto | Auto |
| Merge gate (pass) | Pause | Auto | Auto | Auto |
| Merge gate (fail) | Pause | Pause | Pause | Auto + flag |
| Skill extraction | Pause | Auto + scan | Auto + scan | Auto + scan |
| Gap closure (minor) | Pause | Pause | Auto-fix | Auto-fix |
| Gap closure (critical) | Pause | Pause | Pause | Auto + flag |
| Phase completion | Pause | Pause | Auto (≥70%) | Auto |
| Handoff save | Pause | Auto | Auto | Auto |
| Circuit break | Stop | Stop | Stop | Stop |
| Security critical | Stop | Stop | Stop | Stop + flag |

---

## Integration

### /fire-3-execute

The `--autonomy` flag replaces the binary `--autonomous`/`--manual` flags. Legacy flags are mapped:
- `--manual` → `--autonomy supervised`
- `--autonomous` → `--autonomy autonomous`
- No flag → uses `.planning/config.yml` setting, default: `guided`

### /fire-autonomous

Always runs at `autonomous` level. Can be upgraded to `sentinel` with `--sentinel` flag.

### /fire-loop

Inherits autonomy level from the triggering command. Displays current level in loop status.

### /fire-4-verify

Phase completion approval follows the autonomy level's `phase_completion` setting.

---

## References

- **Inspiration:** Devin's guardrails system, Manus AI confidence-gated escalation
- **Related:** `references/circuit-breaker.md` — hard stops override all autonomy levels
- **Related:** `references/error-classification.md` — BLOCKED state overrides all autonomy levels
- **Related:** `commands/fire-cost.md` — auto-runs in SENTINEL mode
- **Consumer:** `commands/fire-3-execute.md` — primary integration (Step 8.75)
- **Consumer:** `commands/fire-autonomous.md` — default AUTONOMOUS level
