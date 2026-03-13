---
name: parallel-debug
description: Debug complex issues using competing hypothesis investigation with 3 parallel agents
user-invocable: true
disable-model-invocation: true
---

# Parallel Agent Investigation Pattern (Competing Hypotheses)

> Validated by Anthropic's official Agent Teams docs as the "Competing Hypotheses" pattern.

## When to Use

- Complex bug affecting multiple components
- Root cause unclear after initial analysis
- Time-sensitive production issue
- Issue spans multiple files/layers

## The 3-Agent Pattern

Launch all 3 in a SINGLE message (parallel execution):

```javascript
// Agent 1: Where symptoms appear (child component / output layer)
Task({ subagent_type: "fire-debugger", prompt: "Investigate [symptom location]..." });

// Agent 2: What triggers it (parent/caller / data layer)
Task({ subagent_type: "fire-debugger", prompt: "Investigate [trigger source]..." });

// Agent 3: Working reference (proven patterns in codebase)
Task({ subagent_type: "Explore", prompt: "Find working examples of [similar pattern]..." });
```

## Process

1. Each agent investigates one aspect independently
2. All create research documents in `.planning/research/`
3. Agents should **actively try to disprove** each other's theories (fights anchoring bias)
4. Combined insights reveal root cause
5. Implement fix with confidence
6. Document in Skills Library (`/warrior-add-newskill`)

## Expected Result

Solved in ~1 hour vs 3+ hours sequential debugging.

## Example Success: Video Player Bug (Feb 2, 2026)

YouTube/Vimeo videos stopping after 2-3 seconds in MERN LMS:
- Agent 1: Analyzed VideoPlayer.jsx (player lifecycle issues)
- Agent 2: Analyzed CourseContent.jsx (callback patterns causing re-renders)
- Agent 3: Found ZoomLessonPlayer (working callback refs pattern)
- **Solution:** Callback refs pattern identified and deployed same day

**Skills Library Reference:**
`~/.claude/plugins/warrior-workflow/skills-library/video-media/REACT_VIDEO_PLAYER_REINITIALIZATION_FIX.md`

## Key Insight from Anthropic

> "When the root cause is unclear, a single agent tends to find one plausible explanation and stop looking. The debate structure fights anchoring bias. The theory that survives is much more likely to be the actual root cause."
