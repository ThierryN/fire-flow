# Agent Self-Improvement Loop — 6-Upgrade Blueprint for Cross-Session Learning

## The Problem

AI agent systems (like Dominion Flow) can accumulate skills and memory, but they don't systematically **learn from their own failures**. Agents make the same mistakes across sessions, don't self-evaluate before acting, and can't adapt their autonomy based on experience. The system captures knowledge but doesn't close the loop.

### Why It Was Hard

- Agent memory systems typically store *what happened*, not *what went wrong and why*
- Self-evaluation adds latency — finding the right balance between thoroughness and speed
- Auto-extracting reusable patterns requires distinguishing project-specific code from generalizable solutions
- Confidence estimation is subjective and easy to game (agent always says "high confidence")
- The 6 capabilities interact — reflection feeds confidence, confidence gates execution, execution produces reflections

### Impact

- Same debugging mistakes repeated session after session
- No systematic recovery from failures (73.5% recovery → 95% with self-evaluation)
- Skills library grows only through manual contribution (capture gap)
- Agent can't distinguish "I know this" from "I'm guessing" — treats all tasks equally

---

## The Solution

### Root Cause

The gap is not in missing systems but in **missing feedback loops**. Most agent frameworks are open-loop: plan → execute → done. Research shows closed-loop agents (plan → execute → reflect → learn → plan better) dramatically outperform open-loop ones.

### The 6-Upgrade Blueprint

Apply these 6 upgrades in order (each builds on the previous):

```
┌──────────────────────────────────────────────────────────┐
│  1. REFLECTION MEMORY        (capture failures)          │
│  2. PRE-ACTION SELF-JUDGE    (catch mistakes early)      │
│  3. EXPERIENCE REPLAY        (index resolved debugs)     │
│  4. SKILL AUTO-EXTRACTION    (learn from success)        │
│  5. AUTO-CONSOLIDATION       (keep memory fresh)         │
│  6. CONFIDENCE GATES         (adapt behavior to certainty)│
└──────────────────────────────────────────────────────────┘

Feedback loop:
  Execute → Self-Judge → Reflect on failures →
  Index for replay → Extract skills from success →
  Consolidate memory → Estimate confidence → Execute better
```

### Upgrade 1: Reflection Memory
**Research:** Reflexion (NeurIPS 2023) — 91% pass@1

Store "what I tried and why it failed" as searchable reflections. Before investigating any issue, search past reflections first.

```
Location: ~/.claude/reflections/{date}_{slug}.md
Format: Problem → Failed approaches → What worked → Lesson → Search triggers
Trigger: After debug resolution, test failure, approach rotation
Search: Before new debug sessions and complex tasks
```

### Upgrade 2: Pre-Action Self-Judge
**Research:** Agent-as-Judge (2025) — 95% error recovery

5-point gut check before marking any task complete:
1. Does this do what the plan asked?
2. Could this break something working?
3. Am I confident or guessing?
4. Did I check obvious things (imports, types, null)?
5. Would I approve this in code review?

If any "no" or "uncertain" → stop and re-examine.

### Upgrade 3: Experience Replay
**Research:** ECHO (2025) — 80% improvement

Index resolved debug sessions into vector memory. Future debug sessions search for similar symptoms and shortcut investigation by applying known root causes.

```
Resolved debug file → Index in Qdrant as 'debug_resolution'
Future debug → Search: /fire-remember "{symptoms}" --type debug_resolution
If match found → "I've seen this before. Root cause was X. Fix was Y."
```

### Upgrade 4: Auto Skill Extraction
**Research:** SAGE (2025) — 8.9% higher completion, 26% fewer steps

After successful verification, scan execution for extractable patterns:
- Generalizable (not project-specific)
- Non-trivial (>3 files or >30 min work)
- Required research or multiple attempts

Auto-extracted → quarantine → human review → approve or reject.

### Upgrade 5: Auto-Consolidation
**Research:** Mem0 (2025) — 91% lower latency

Make memory refresh automatic:
- Index all memory dirs recursively (including skills library)
- Extract facts from handoffs
- Run on session end or manually

### Upgrade 6: Confidence-Gated Actions
**Research:** SAUP (ACL 2025) — uncertainty propagation

Score confidence before each action:
- HIGH (>80%): Proceed autonomously
- MEDIUM (50-80%): Extra validation, search reflections
- LOW (<50%): Pause, escalate, ask for help

Signals: +skill match, +tests available, +familiar tech, -unfamiliar framework, -no tests, -ambiguous requirements.

---

## Testing the Fix

### Verification Criteria

1. **Reflection Memory:** Create a test reflection → search via vector memory → confirm it returns
2. **Self-Judge:** Execute a task → confirm 5-point check runs → "uncertain" creates reflection
3. **Debug Replay:** Resolve a debug → index → search symptoms → confirm resolution surfaces
4. **Skill Extraction:** Complete phase with novel pattern → quarantine candidate generated
5. **Auto-Consolidation:** Run consolidate → verify new files indexed, skills searchable
6. **Confidence Gates:** Execute varying-familiarity tasks → HIGH proceeds, LOW pauses

---

## Prevention

- Wire reflections into debug flow as mandatory step (not optional)
- Self-Judge is 30 seconds — fast enough to never skip
- Auto-consolidation runs on session end (no manual trigger needed)
- Confidence gates are advisory, not blocking (agent can override with justification)

---

## Related Patterns

- [REFLEXION_MEMORY_PATTERN](./REFLEXION_MEMORY_PATTERN.md) - Detailed reflection implementation
- [CONFIDENCE_GATED_EXECUTION](./CONFIDENCE_GATED_EXECUTION.md) - Detailed confidence scoring
- [EVOLUTIONARY_SKILL_SYNTHESIS](./EVOLUTIONARY_SKILL_SYNTHESIS.md) - Skill auto-extraction details
- [SELF_QUESTIONING_TASK_GENERATION](./SELF_QUESTIONING_TASK_GENERATION.md) - Full self-evaluation framework

---

## Common Mistakes to Avoid

- Treating reflection as optional ("I'll write it later" = never)
- Making Self-Judge a 70-point checklist (5 points max — speed is critical)
- Extracting project-specific code as "general" skills (quarantine catches this)
- Confidence score = 100% always (agents tend to be overconfident — calibrate)
- Running full consolidation on every session end (use light mode — index only)
- Skipping pre-investigation reflection search ("I already know this" = confirmation bias)

---

## Resources

- Reflexion (NeurIPS 2023): https://arxiv.org/abs/2303.11366
- SAGE (Dec 2025): https://arxiv.org/abs/2512.17102
- ECHO (2025): Experience replay for agents
- Agent-as-Judge (2025): Self-evaluation patterns
- SAUP (ACL 2025): Uncertainty propagation
- Mem0 (2025): Auto-consolidation architecture

---

## Time to Implement

**10-14 hours** across all 6 upgrades. Can be done incrementally — each upgrade is independently valuable.

## Difficulty Level

Stars: 4/5 — Individual upgrades are straightforward. The challenge is **wiring them together** so they form a coherent feedback loop rather than isolated features.

---

**Author Notes:**
The key research finding that motivated this: **recovery ability, not error avoidance, differentiates top agents** (95% vs 73.5% recovery rate). This means making agents "smarter" isn't about preventing mistakes — it's about learning from them systematically. The 6-upgrade loop closes this gap by making failure data persistent, searchable, and actionable across sessions.
