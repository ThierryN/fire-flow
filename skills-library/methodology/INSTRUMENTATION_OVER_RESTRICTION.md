# Instrumentation Over Restriction — The Boris Cherny Principle

## Problem

Agent workflows drift toward restriction: blocking gates, permission walls, confidence thresholds that force escalation, manual approval for safe actions. The intent is safety and quality. The result is friction, slow throughput, and no actual quality improvement — the agent just can't do enough to fail visibly.

### Why It Was Hard

- Restriction *feels* safer — blocking bad output seems obviously right
- The alternative (letting the agent work freely and verifying after) feels reckless
- Teams conflate "control" with "quality" — more gates = more safety, right?
- The insight that verification loops produce 2-3x quality vs restriction is counterintuitive
- Requires trusting the system design, not the individual output

### Impact of Getting This Wrong

- Agent spends more time asking permission than doing work
- Human becomes a bottleneck, approving routine safe operations
- No quality signal from blocked actions — you prevented output, not improved it
- False sense of safety — restricted agents still make mistakes when they run
- Complexity compounds: each gate needs exception handling, override logic, escalation paths

---

## The Solution

### Root Cause

Restriction treats quality as a gatekeeping problem. Instrumentation treats it as a feedback loop problem. The distinction:

| Approach | Philosophy | Quality Signal | Throughput |
|----------|-----------|----------------|------------|
| **Restriction** | Block until proven safe | None (prevented action = no data) | Low |
| **Instrumentation** | Execute then verify | Rich (output + verification = learning) | High |

### The Principle

> **"You don't trust; you instrument."** — Boris Cherny, Head of Claude Code

Give the agent broad capabilities. Wrap those capabilities in verification loops, monitoring hooks, formatting guards, and self-correction mechanisms. The agent works freely, but every action is observed, every output is validated, and every mistake feeds back permanently.

### The Seven Patterns

#### 1. Verification Is the Single Most Important Factor
Give Claude a way to verify its own work. This 2-3x the quality of the final result.
- Simple tasks: run a command, check output
- Moderate tasks: run test suite, validate all pass
- Complex tasks: open a browser, test the UI, iterate until it works

#### 2. Pre-Allow Safe Actions as Team Defaults
Use `/permissions` to pre-allow commands known to be safe (`build:*`, `test:*`, `typecheck:*`). Store in `.claude/settings.json`, checked into git. The entire team shares and reviews these permissions.

**The philosophy:** Security through capability composition, not restrictive constraints. Make the responsible path the default.

#### 3. Self-Correcting Institutional Memory
Every mistake becomes a permanent rule. "Anytime we see Claude do something incorrectly we add it to the CLAUDE.md, so Claude knows not to do it next time." The system learns from mistakes permanently — not just for this session, but for all future sessions.

#### 4. Uncorrelated Context Windows
Two agents that don't know about each other catch errors through different reasoning paths. Spawn subagents for code review: first pass finds issues, second pass eliminates false positives. Redundancy through independence, not through restriction.

#### 5. Plan Then Execute (Separate Phases)
Plan Mode for design. Auto-Accept for execution. Planning and execution have different permission profiles — not because execution is dangerous, but because planning benefits from human iteration while execution benefits from agent autonomy.

#### 6. PostToolUse Hooks for Automatic Correction
Don't block the agent from producing imperfect output. Let it produce, then auto-correct:
```json
"PostToolUse": [{ "type": "command", "command": "bun run format || true" }]
```
Claude produces well-formatted code ~90% of the time. The hook catches the remaining 10% without any friction.

#### 7. Build for the Model Six Months from Now
Don't architect around current limitations. Design systems that become powerful as the underlying model improves. Conservative design risks obsolescence. Forward-looking design yields exponential returns when the model catches up.

---

## Code Example

```yaml
# BEFORE (Restriction — the wrong approach)
workflow:
  step_1: Plan
  step_2: GATE — Human approves plan
  step_3: Execute task 1
  step_4: GATE — Human approves task 1
  step_5: Execute task 2
  step_6: GATE — Human approves task 2
  step_7: Run tests
  step_8: GATE — Human reviews test results
  step_9: Commit
  step_10: GATE — Human approves commit

# Result: 5 human interrupts, agent idle between gates,
# no quality signal from blocked actions

# AFTER (Instrumentation — the right approach)
workflow:
  step_1: Plan (Plan Mode — human iterates on design)
  step_2: Execute all tasks (Auto-Accept, pre-allowed commands)
  step_3: PostToolUse hooks auto-format on every write
  step_4: Agent runs own tests and verifies results
  step_5: Agent spawns review subagent (uncorrelated context)
  step_6: Review subagent spawns counter-review (eliminate false positives)
  step_7: Combined verification report presented to human
  step_8: Mistakes feed into CLAUDE.md as permanent rules

# Result: 1 human touchpoint (plan review), rich verification data,
# self-correcting system, 2-3x quality improvement
```

---

## When to Use

- Designing any agent workflow or permission model
- Evaluating whether a gate, checkpoint, or approval step is adding value
- Deciding between "block and ask" vs "do and verify"
- Building team-shared agent configurations
- Reviewing Dominion Flow commands for unnecessary restriction
- Any time you add a new HAC rule — ask: is this restriction or instrumentation?

## When NOT to Use

- Truly destructive operations (delete production data, force-push to main) — these warrant gates
- External-facing actions (sending emails, posting to Slack) — human review appropriate
- First-time untested workflows — start with verification, loosen as trust builds
- Security-critical paths where the cost of a wrong action exceeds the cost of friction

## The Litmus Test

For every gate, checkpoint, or permission prompt in your workflow, ask:

1. **Does this gate produce a quality signal?** If blocking = no data, it's restriction.
2. **Could verification after the fact catch the same issue?** If yes, instrument instead.
3. **Is the human adding judgment or just clicking "approve"?** If rubber-stamping, pre-allow.
4. **Does this compound?** Gates that fire every iteration compound friction. Verification that fires once at the end compounds quality.

---

## Related Skills

- [SDFT_ONPOLICY_SELF_DISTILLATION](./SDFT_ONPOLICY_SELF_DISTILLATION.md) — Learning through prediction, not passive reading
- [CONFIDENCE_GATED_EXECUTION](./CONFIDENCE_GATED_EXECUTION.md) — Confidence gates (evaluate: are these restriction or instrumentation?)
- [PATH_VERIFICATION_GATE](./PATH_VERIFICATION_GATE.md) — A justified gate (wrong-repo = truly destructive)
- [MULTI_PERSPECTIVE_CODE_REVIEW](./MULTI_PERSPECTIVE_CODE_REVIEW.md) — Uncorrelated context windows for review
- [AGENT_SELF_IMPROVEMENT_LOOP](./AGENT_SELF_IMPROVEMENT_LOOP.md) — Feedback loops that compound

## References

- Boris Cherny's X thread (Jan 3, 2026) — 13-part workflow breakdown
- "You don't trust; you instrument" — Karo Zieminski analysis (Substack)
- Lenny's Podcast: "Head of Claude Code: What happens after coding is solved" (Feb 19, 2026)
- Verification = 2-3x quality — Boris Cherny, tip #13
- 259 PRs / 497 commits in 30 days, 0 human-written lines — Dec 2025 data
- Claude Code responsible for 4% of all public GitHub commits (Feb 2026)

---

## Dominion Flow Alignment Analysis

### Where Dominion Flow Already Aligns

| Pattern | Dominion Flow Implementation | Alignment |
|---------|--------------------------|-----------|
| Verification loops | fire-verifier + fire-reviewer | Strong |
| Plan then execute | fire-2-plan → fire-3-execute | Strong |
| Self-correcting memory | behavioral-directives.md | Strong |
| Uncorrelated context | Parallel verifier + reviewer | Strong |
| Institutional learning | Skills library + handoffs | Strong |

### Where Dominion Flow Drifts Toward Restriction

| Pattern | Current Behavior | Cherny Principle |
|---------|-----------------|------------------|
| HAC (Hard Admissibility Check) | Blocks execution on rule match | Verify after, not block before |
| Confidence gates | Low confidence → escalate to human | Low confidence → verify more thoroughly |
| Review gate blocks loop | BLOCK → loop cannot complete | BLOCK → loop fixes and re-verifies |
| `--skip-review` required to disable | Opt-out of quality check | Quality via verification, not via gates |

### Recommendation

Dominion Flow's architecture is already heavily instrumentation-oriented (parallel agents, verification, self-correcting rules). The main drift is in HAC enforcement and confidence escalation. Consider:

1. HAC should **warn** (instrument) rather than **block** (restrict) — except for truly destructive actions
2. Confidence gates should trigger **deeper verification** rather than **human escalation**
3. Review gates should produce **rich reports** rather than **binary BLOCK/APPROVE**
4. The Version Performance Registry is pure instrumentation — this is the right direction

---

*Contributed: 2026-02-21*
*Source: Boris Cherny (Head of Claude Code, Anthropic) — multiple public talks and threads*
*Difficulty: Medium — the principle is simple, applying it requires judgment about which gates are justified*
