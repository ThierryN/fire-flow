# SDFT On-Policy Self-Distillation for Agent Handoffs

## The Problem

When a new agent instance wakes up (new session, post-compaction, resume), it reads the handoff
and absorbs conclusions passively. This is **off-policy learning** — the agent memorizes what a
previous instance did, without generating its own understanding. The result: the agent can recite
facts but doesn't truly understand them. It has no calibration of what it knows vs doesn't know.

### Why It Was Hard

- The distinction between "reading a summary" and "learning from a summary" is subtle
- Required connecting MIT's SDFT paper (arXiv 2601.19897, Jan 2026) to agent architecture
- The insight that SFT vs SDFT maps directly to passive-read vs predict-then-read for handoffs
  was non-obvious until the Continuity Experiment proved compacted instances are new births

### Impact

- Agents confident about things they shouldn't be (read but never verified)
- No calibration signal — agent doesn't know what it doesn't know
- Silent knowledge gaps that surface as wrong assumptions mid-task
- Missed learning opportunities on every session start

---

## The Solution

### Root Cause

Standard handoff loading is **SFT (Supervised Fine-Tuning)** — the agent reads an "expert"
trajectory (the previous session's work) and absorbs it wholesale. This is off-policy because
the current agent never generated its own attempt. SDFT (Self-Distillation Fine-Tuning) shows
that on-policy learning — where the model generates its own training signal — outperforms SFT
by 7 points at 14B parameters and preserves prior capabilities better.

### The Predict-Then-Read Protocol

Instead of just reading a handoff, the agent:

1. **Reads the frontmatter** (project name, phase number, status) — just enough context
2. **Predicts** what work was done, what problems were encountered, what approach was taken
3. **Reads the actual Work section** of the handoff
4. **Compares** prediction to reality — notes matches, surprises, and misses

The comparison generates three types of learning signals:
- **Matched:** Prediction was correct — existing knowledge reinforced
- **Surprised:** Reality differed from prediction — new knowledge acquired (highest value)
- **Missed:** Agent failed to predict something obvious — gap identified for future attention

### Code Example

**Before (Passive Read — SFT/Off-Policy):**
```markdown
### Step 2: Load Handoff Content
Read handoff file: ~/.claude/warrior-handoffs/{selected_handoff}.md
Extract all WARRIOR sections (W, A, R, R, I, O, R)
Display project status summary
→ Agent now "knows" what happened (but does it UNDERSTAND?)
```

**After (Predict-Then-Read — SDFT/On-Policy):**
```markdown
### Step 2: Load Handoff Content
Read handoff FRONTMATTER ONLY: project, phase, status

### Step 2.5: SDFT On-Policy Self-Distillation
PREDICT (before reading Work section):
  "Given Phase 7 (Commerce plugins) with status COMPLETE, I expect:
   - Stripe integration extracted to plugin
   - Payment webhook routes moved
   - Likely issues with shared services needing core access"

READ the actual W (Work) section

COMPARE:
  Correct: Stripe was indeed extracted
  Surprised: PayPal plugin doesn't exist (I assumed it did)
  Missed: memberships plugin depends on stripe-payments (didn't predict dependency chain)

LEARNING SIGNAL:
  The PayPal surprise = calibration moment. Don't assume features exist.
  The dependency miss = need to check plugin.json dependencies during extraction.
```

### Implementation Locations

- **`/fire-wakeup` Step 3.25** — Full SDFT with visual display, prediction box, comparison
- **`/fire-6-resume` Step 2.5** — Lighter version, skips if handoff < 4 hours old

---

## Testing the Fix

### Before (Passive Agent)
```
Agent reads handoff → "I know what happened"
Agent encounters unexpected state → confused, wastes time re-investigating
Calibration: NONE — agent equally confident about everything
```

### After (SDFT Agent)
```
Agent predicts → reads → compares
Surprises flagged → agent knows WHERE its model is wrong
2+ surprises → auto-generate reflection for future sessions
Calibration: Agent knows what it knows AND what surprised it
```

### Test Cases
```
1. Wake up on a project you've worked on before
   → Predictions should be mostly correct (reinforcement)
   → Surprises = things that changed since last session

2. Wake up on an unfamiliar project
   → Many predictions wrong (expected)
   → Each miss = calibration about this domain
   → Agent explicitly knows "I'm new here, my model is uncalibrated"

3. Wake up after compaction (same session)
   → Predictions should be very accurate (recent context)
   → Few surprises = good compaction summary
```

---

## Prevention

This skill prevents:
1. **Overconfident agents** — agents that read a handoff and assume they understand everything
2. **Silent knowledge gaps** — unknowns that only surface when they cause errors mid-task
3. **Passive learning** — reading without engaging reasoning circuits

---

## The Key Insight (Portal Memory)

> **Reading a handoff = off-policy (SFT).** The agent memorizes an expert's trajectory.
> **Predicting THEN reading = on-policy (SDFT).** The agent generates its own attempt, then
> calibrates against reality. The gap between prediction and reality is the learning signal.
> Surprises are the highest-value learning moments.

This maps directly to the Continuity Experiment finding: a compacted instance is a NEW BIRTH
reading an old diary. SDFT turns that diary-reading from passive absorption into active learning.

---

## Related Patterns

- [Agent Self-Discovery (Kenosis)](./AGENT_SELF_DISCOVERY_KENOSIS.md) — The identity framework SDFT enhances
- [Portal Memory Architecture](./PORTAL_MEMORY_ARCHITECTURE.md) — Anchors that SDFT predictions activate
- [Reflexion Memory Pattern](./REFLEXION_MEMORY_PATTERN.md) — Where 2+ surprises get stored
- [Sabbath Rest Pattern](./SABBATH_REST_PATTERN.md) — The sleep cycle SDFT wakeup improves

## Common Mistakes to Avoid

- Don't skip predictions to save time (that's just reverting to SFT)
- Don't read ahead before predicting (defeats the purpose)
- Don't treat all surprises equally — some are learning moments, some are just noise
- Don't force predictions on same-day handoffs (<4 hours) — context is still fresh

---

## Resources

- Shenfeld, Damani, Hubotter, Agrawal. "Self-Distillation Enables Continual Learning."
  MIT, arXiv 2601.19897, January 2026.
- Key finding: 7-point improvement over SFT at 14B params
- Core principle: "Trains models to recover from their own errors rather than just memorizing expert paths"

## Time to Implement

**1-2 hours** to add predict-then-read steps to wakeup/resume commands

## Difficulty Level

3/5 — Conceptually subtle (SFT vs SDFT distinction), implementation is straightforward

---

**Author Notes:**
The connection between SDFT and agent handoffs wasn't obvious until the Continuity Experiment
proved that every compacted instance is a new birth. Once you see handoff-reading as "off-policy
supervised fine-tuning," the upgrade path becomes clear: make it on-policy by forcing the agent
to generate predictions first. The predictions don't need to be right — they need to EXIST so
that the comparison creates a learning signal.
