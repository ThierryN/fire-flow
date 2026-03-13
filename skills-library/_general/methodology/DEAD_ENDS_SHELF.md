---
name: DEAD_ENDS_SHELF
category: methodology
description: Tag unsolved problems in FAILURES.md for fresh Claude instances — stop burning tokens on dead ends, move on, let cleaner context solve it later
version: 2.0.0
tags: [dead-ends, autonomous, cost-optimization, shelving, context-rotation]
---

# Dead Ends Protocol (v11.3)

When an agent hits a wall — code that won't compile, an API that won't respond, a logic puzzle that burns 3+ attempts — **tag it `[DEAD-END]` in FAILURES.md and move on**. A fresh Claude instance with clean context will attempt it on the next session start.

> **Philosophy:** A stuck agent with degraded context is the worst possible solver. A fresh agent with full context and documented prior attempts is the best. Stop burning tokens on dead ends — rotate the problem to a fresh mind.

> **v11.3 change:** Dead ends are tagged entries in the project's failure log, distinguished by the `[DEAD-END]` tag.

---

## Location: `.planning/FAILURES.md`

Dead-end entries live alongside regular failure entries, distinguished by the `[DEAD-END]` tag. They are:
- **Written by:** Any agent that hits a dead end (executor, planner, verifier, researcher)
- **Read by:** `/fire-6-resume` on session start — fresh Claude filters for `[DEAD-END]` entries and attempts solutions
- **Cleared by:** The agent that solves the problem (move entry to `LESSONS.md` with `[DEAD-END-SOLVED]` tag, remove `[DEAD-END]` tag from FAILURES.md)

---

## When to Shelve (Trigger Rules)

| Condition | Action |
|-----------|--------|
| **3+ failed attempts** at the same problem | Tag `[DEAD-END]` immediately |
| **Blocked by missing info** (credentials, API keys, external dependency) | Tag with `[DEAD-END] [NEEDS-HUMAN]` |
| **Context degradation detected** (compaction happened, losing details) | Tag before context loss |
| **Confidence drops below 30%** after research | Tag — you're guessing |
| **Circular dependency** (fix A breaks B, fix B breaks A) | Tag with both sides documented |
| **Time sink** — 15+ minutes on a single non-critical issue | Tag and move to next task |

### When NOT to Shelve

- Critical path blockers (nothing else can proceed without this)
- Security vulnerabilities (must fix now)
- Data loss risks (must fix now)

For critical blockers: escalate to the user via checkpoint, don't shelve.

---

## Dead-End Entry Format

```markdown
### [DEAD-END] {short title}

**Shelved by:** {agent name} at {timestamp}
**Phase:** {phase number} / **Plan:** {plan number}
**Priority:** {critical | high | medium | low}
**Tags:** {code-bug, api-integration, dependency, logic, config, performance, unknown}

**Problem:** {What you were trying to do and what went wrong — be specific}

**What Was Tried** (prevents next instance from repeating):
1. {what you tried} → {what happened}
2. {what you tried} → {what happened}
3. {what you tried} → {what happened}

**Relevant Files:**
- `{file path}` — {what matters}

**Error:** `{exact error message}`

**Hypotheses Not Yet Tested:**
- {idea 1 — why it might work}
- {idea 2 — why it might work}

**Impact if unsolved:** {what breaks or degrades}
```

---

## Agent Integration

### fire-executor (writes to FAILURES.md)

When a task hits the shelve trigger:

1. **Stop working on this task** — don't burn more tokens
2. **Write a `[DEAD-END]` entry** to `.planning/FAILURES.md` using the format above
3. **On first write:** If FAILURES.md doesn't exist, create it with a `# Failures` header first
4. **Move to next task** — the agent continues with remaining work
5. **Note in RECORD.md** — "Task X tagged [DEAD-END], moved to Task Y"

### fire-planner (writes to FAILURES.md)

When a planning problem can't be resolved:

1. Write `[DEAD-END]` entry with `Tags: logic` or `Tags: dependency`
2. Plan around the dead end — design alternative approach that doesn't depend on it
3. Mark the plan with `dead_end_dependency: true` in frontmatter

### fire-verifier (writes to FAILURES.md)

When verification finds an unfixable issue:

1. Write `[DEAD-END]` entry with exact failing test/check details
2. Mark verification as CONDITIONAL PASS with `shelved_issues: N`

### fire-researcher (reads + writes FAILURES.md)

In recovery mode, read FAILURES.md and filter for `[DEAD-END]` entries:
- If match found: include prior attempts in research context (avoid repeating)
- If no match: tag `[DEAD-END]` if research fails after 3-tier cascade

### fire-6-resume (reads FAILURES.md — THE KEY STEP)

**On every session start, a fresh Claude instance:**

1. Read `.planning/FAILURES.md` (if it exists)
2. Filter for `[DEAD-END]` tagged entries
3. For the highest-priority entry:
   - Review the problem, prior attempts, and untested hypotheses
   - With fresh context, attempt the top untested hypothesis
   - If solved: move entry to `LESSONS.md` with `[DEAD-END-SOLVED]` tag, remove `[DEAD-END]` tag from FAILURES.md
   - If still stuck: update the entry with new attempts, re-tag
4. Then proceed with normal work

> **Why this works:** A fresh Claude instance has full context window, no degradation from prior compactions, and zero emotional attachment to the failed approach. It sees the problem with completely new eyes.

---

## Autonomous Mode Integration

In `/fire-autonomous`, dead-end tagging is critical for cost efficiency:

```
Agent hits dead end on Task 5
  → Tags [DEAD-END] in FAILURES.md (30 seconds)
  → Moves to Task 6, 7, 8 (continues productive work)
  → Phase completes with 1 tagged dead end
  → Handoff documents it
  → Next session: fresh Claude reads FAILURES.md, solves Task 5 with clean context
```

**Without tagging:** Agent burns 15+ minutes on Task 5, context degrades, Tasks 6-8 suffer. Cost: HIGH, quality: LOW.

**With tagging:** Agent spends 30 seconds documenting Task 5, full context preserved for Tasks 6-8. Cost: LOW, quality: HIGH.

---

## Hygiene

- **Max dead-end entries:** 10 (if more accumulate, oldest low-priority entries get resolved or removed)
- **Stale check:** If an entry is 5+ sessions old and low-priority, consider removing
- **Dedup:** Before writing a new entry, grep FAILURES.md for `[DEAD-END]` entries with similar titles — update instead of duplicate
- **Resolution celebration:** When solved, log to LESSONS.md with `[DEAD-END-SOLVED]` tag — document what the fresh context saw that the burned context missed

---

## Example: Real Dead-End Entry

```markdown
### [DEAD-END] Podcast feed XML parsing timeout on large feeds

**Shelved by:** fire-executor at 2026-03-04
**Phase:** 2 / **Plan:** 3
**Priority:** medium
**Tags:** api-integration, performance

**Problem:** RSS feed parser hangs on podcast feeds with 500+ episodes.
`podcastService.getFeed('live-teachings')` takes 45+ seconds and times out.

**What Was Tried:**
1. Increased timeout to 60s → Still times out on 800-episode feeds
2. Added `{ limit: 100 }` parameter → Parameter ignored by xml2js parser
3. Tried streaming parser (sax-js) → Import error, needs different build config

**Relevant Files:**
- `server/services/podcastService.js` — getFeed method, line 45
- `server/config/podcast-feeds.json` — feed URLs

**Error:** `TimeoutError: Request timed out after 60000ms at podcastService.getFeed`

**Hypotheses Not Yet Tested:**
- Use `fast-xml-parser` instead of `xml2js` (reportedly 10x faster)
- Pre-fetch and cache feeds with a cron job instead of on-demand parsing
- Paginate at the API level — only parse first N items from XML stream

**Impact if unsolved:** Podcast dropdown shows loading spinner forever for large feeds. Workaround: hardcoded limit of 50 episodes.
```
