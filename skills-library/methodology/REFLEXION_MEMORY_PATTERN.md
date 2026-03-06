# Reflexion Memory Pattern — Cross-Session Failure Learning

## The Problem

AI agents repeat the same mistakes across sessions because failure context is lost. Debug sessions resolve issues, but the knowledge dies with the session. The next agent encountering the same symptoms starts from scratch.

### Why It Was Hard

- Debug sessions produce rich context (symptoms, hypotheses, evidence, root causes) but it's trapped in `.planning/debug/` files that are project-specific and not searchable cross-project
- Failed approaches are the most valuable learning — but agents only record what *worked*, not what *didn't*
- Finding the right granularity: too detailed = noise, too abstract = useless
- Integration requires modifying multiple command flows (debug, loop, execute)

### Impact

- Same bugs debugged repeatedly across sessions (hours wasted)
- Silent failures re-investigated from scratch every time
- No institutional memory of "this library is broken on Python 3.14"
- Debug sessions take 3x longer than necessary when prior knowledge exists

---

## The Solution

### Root Cause

Agent systems store *conclusions* (handoffs, skills) but not *journeys* (what was tried, what failed, why). Reflexion research shows that storing the journey as linguistic self-reflection dramatically improves future performance (91% pass@1 vs baselines).

### The Reflection File Format

```markdown
---
type: reflection
date: 2026-02-20
project: claude-voice-bridge
trigger: debug-resolution | test-failure | approach-rotation | stalled-loop
severity: minor | moderate | critical
tags: [pynput, keyboard, hotkeys, python-3.14]
---
# What I tried and why it failed

## The Problem
Hotkeys stopped responding. No errors — completely silent failure.

## What I Tried (and why each failed)
1. **Checked keyboard library hooks** — hooks installed, listener alive,
   but zero callbacks. Root cause: keyboard 0.13.5 broken on Python 3.14.
2. **Switched to pynput with char matching** — pynput works, but Ctrl+M
   sends '\r' not 'm'. Silent mismatch.

## What Actually Worked
Used `KeyCode.from_vk(ord(name.upper()))` — VK codes are stable
regardless of modifier state.

## The Lesson
When a library installs without errors but produces no output, suspect
Python version incompatibility. Always match keyboard keys by VK code,
never by char when modifiers are involved.

## Future Self: Search For This When
- Hotkeys stop working silently
- Keyboard hooks fire zero events
- Ctrl+letter combinations fail to match
```

### Three Integration Points

**1. Pre-Investigation Search (Step 2.5 in debug flow):**
```
Before investigating any issue:
  Search reflections: /fire-remember "{symptoms}" --type reflection

  If match found with >0.75 similarity:
    "I've seen this before — {lesson}. Applying directly."
    Offer: [Apply same fix] [Investigate fresh] [Compare differences]
```

**2. Post-Resolution Capture (Step 7.5 in debug flow):**
```
After root cause found and fix verified:
  Auto-generate reflection from debug file
  Extract: symptoms → failed hypotheses → root cause → fix → lesson

  Severity classification:
    critical: 5+ eliminated hypotheses OR 10+ files changed
    moderate: 2-4 eliminated hypotheses OR multi-file fix
    minor: 1 hypothesis OR single-file fix
```

**3. Loop Failure Capture (Step 9 in loop):**
```
On STALLED (3+ iterations no progress):
  Save reflection with trigger: "stalled-loop"
  Include: what was attempted, measurements, why no progress

On SPINNING (same error repeated):
  Save reflection with trigger: "approach-rotation"
  Include: each failed approach with error hash
```

### Storage & Search

```
Location:     ~/.claude/reflections/
Indexed in:   Qdrant as sourceType: 'reflection'
Search:       /fire-remember "{query}" --type reflection
Command:      /fire-reflect capture|search|list|review
```

---

## Testing the Fix

### Verification Steps

1. Create a reflection file manually in `~/.claude/reflections/`
2. Run `npm run consolidate` to index it
3. Search: `npm run search -- "hotkeys silent failure" --type reflection`
4. Confirm the reflection appears in results with correct sourceType

### Quality Checklist

A good reflection has:
- [ ] Specific symptoms (error messages, observed behaviors)
- [ ] Multiple failed approaches with *reasons* they failed
- [ ] Concrete solution (code, command, config change — not vague advice)
- [ ] One-sentence lesson useful without context
- [ ] Search triggers matching how you'd describe the problem naturally

A bad reflection:
- "Something was wrong with the API" (too vague)
- Only records the solution without the journey
- Lesson is "be more careful" (not actionable)

---

## Prevention

1. Make reflection generation **automatic** after debug resolution — don't rely on manual capture
2. Keep reflections **concise** — the lesson and search triggers are most important
3. Review reflections periodically — merge duplicates, update outdated ones
4. Tag with specific technologies and error patterns for better search

---

## Related Patterns

- [AGENT_SELF_IMPROVEMENT_LOOP](./AGENT_SELF_IMPROVEMENT_LOOP.md) - Full 6-upgrade blueprint
- [CONFIDENCE_GATED_EXECUTION](./CONFIDENCE_GATED_EXECUTION.md) - Reflections feed confidence scoring
- [WARRIOR_WORKFLOW_DEBUGGING_PROTOCOL](./WARRIOR_WORKFLOW_DEBUGGING_PROTOCOL.md) - Debug flow where reflections integrate

---

## Common Mistakes to Avoid

- Capturing reflections for trivial issues (typo fixes, config changes) — noise overwhelms signal
- Writing the "lesson" as a platitude ("always test thoroughly") instead of a specific takeaway
- Not including search triggers — the reflection exists but is unfindable
- Storing reflections per-project instead of globally — defeats cross-session learning
- Skipping the "what I tried" section — the failed approaches are the most valuable part

---

## Resources

- Reflexion (NeurIPS 2023): https://arxiv.org/abs/2303.11366
- "Language Agents with Verbal Reinforcement Learning" — Shinn et al.
- Dominion Flow implementation: `/fire-reflect` command, `fire-debug.md` Steps 2.5 and 7.5

---

## Time to Implement

**2-3 hours** — Create reflection directory, write command, modify debug/loop flows, add to vector index

## Difficulty Level

Stars: 2/5 — Conceptually simple. The hard part is building the discipline to actually search reflections before investigating and to capture them after resolution.

---

**Author Notes:**
The most surprising finding from implementing this: the "Future Self: Search For This When" section is the single most valuable field. It's the bridge between how you describe the problem *now* (with full context) and how a future agent will describe it (with zero context, just symptoms). Writing good search triggers is an act of empathy toward your future self.
