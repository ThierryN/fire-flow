---
description: Auto-generate compact session summary with aggregate status, readiness, outlook, and next steps
argument-hint: "[--project NAME] [--no-save]"
---

# /fire-session-summary

> Compact forward-looking session summary — fills the gap between full WARRIOR handoffs and the memory system

---

## Purpose

Generate a lightweight session summary capturing what the memory system doesn't: **aggregate status**, **readiness assessment**, **forward planning**, and **concrete next steps**. Saved as a searchable memory point (source type: `session_summary`), indexed automatically by the session-end consolidation hook.

**Not a replacement for /fire-5-handoff.** Use handoffs for milestones. Use this for every session — it's fast, compact, and auto-indexed.

---

## Arguments

```yaml
arguments: none

optional_flags:
  --project: "Override project name detection"
  --no-save: "Display summary without saving to file"
```

---

## Process

### Step 1: Gather Context (30 seconds)

Quickly scan what happened this session. Do NOT re-read entire files — use what you already know from conversation context.

```
Collect from conversation context:
  - What tasks/features were worked on
  - What was completed vs left partial
  - What blockers were hit
  - What decisions were made
  - What files were created/modified

IF in a git repo:
  git log --oneline --since="4 hours ago" 2>/dev/null | head -10

IF .planning/CONSCIENCE.md exists:
  Read current phase and status (first 20 lines only)
```

### Step 2: Detect Project Name

```
Priority order:
  1. --project flag if provided
  2. .planning/VISION.md project name
  3. Git repo name (basename of git root)
  4. Current directory name
  5. "general" (fallback for System32/multi-project sessions)
```

### Step 3: Generate Summary

Write the summary using EXACTLY this template. Keep each section to 2-4 lines max.

```markdown
---
session: {YYYY-MM-DD}
project: {detected project name}
type: session_summary
---

# Session Summary: {YYYY-MM-DD}

## Status
| Item | State | Detail |
|------|-------|--------|
| {work item 1} | DONE / PARTIAL / BLOCKED | {one-line detail} |
| {work item 2} | DONE / PARTIAL / BLOCKED | {one-line detail} |

## Readiness
- **Ready:** {what next session can immediately start on}
- **Blocked:** {external blockers, or "None"}
- **Needs first:** {prerequisites before main work, or "Nothing"}

## Outlook
- **Trajectory:** {on-track / behind / ahead / exploratory}
- **Risk:** {key risk, or "Low"}
- **Momentum:** {what's going well — one line}

## Next Steps
1. **{Priority 1}** — {specific actionable description}
2. **{Priority 2}** — {specific actionable description}
3. **{Priority 3}** — {specific actionable description}

## Decisions Made
- {Decision — rationale in 10 words or less}
```

### Step 4: Save File

```
SUMMARY_DIR = ~/.claude/session-summaries/
FILENAME = {project}_{YYYY-MM-DD}.md

IF file already exists (multiple sessions same day):
  FILENAME = {project}_{YYYY-MM-DD}_{N}.md  (increment N)

Write summary to SUMMARY_DIR/FILENAME

IF --no-save: display only, skip write
```

### Step 5: Confirm

```
Session summary saved: ~/.claude/session-summaries/{filename}
  Status: {X} items ({done} done, {partial} partial, {blocked} blocked)
  Next: {priority 1 — short}
  Auto-indexed on next session end.
```

---

## Integration Points

### Called automatically by:
- `/fire-autonomous` — Step 5.5 (after completion banner, before Sabbath Rest)
- `/fire-5-handoff` — generates session summary alongside full WARRIOR handoff
- Agent stop behavior — agent should call this before ending any substantive session

### Indexed by:
- `session-end.sh` hook → `npm run consolidate` → scans `~/.claude/session-summaries/`
- Source type: `session_summary` in Qdrant
- Searchable via: `npm run search -- "query" --type session_summary`

### Searched by:
- `/fire-6-resume` — checks latest session summary for quick context
- `/fire-0-orient` — reads recent summaries for project state
- Any memory search with `--type session_summary`

---

## Anti-Patterns

```
DO NOT:
  - Write more than 30 lines (this is NOT a handoff)
  - Include code snippets (that's what git is for)
  - List every file changed (memory observations already track this)
  - Repeat information already in CONSCIENCE.md or MEMORY.md
  - Use this instead of /fire-5-handoff for milestones

DO:
  - Be specific in next steps ("Fix the N+1 query in getUserCourses")
  - Be honest in status (PARTIAL means PARTIAL, not DONE)
  - Focus on forward-looking guidance
  - Include decisions that affect future work
  - Keep it under 30 lines of content
```

---

## Examples

### Quick session (bug fix)
```markdown
---
session: 2026-03-01
project: my-other-project
type: session_summary
---

# Session Summary: 2026-03-01

## Status
| Item | State | Detail |
|------|-------|--------|
| Login redirect bug | DONE | Fixed useEffect dependency in AuthContext |
| Dashboard loading | PARTIAL | Skeleton added, API still slow (N+1 query) |

## Readiness
- **Ready:** Optimize getUserCourses query — already identified the N+1 pattern
- **Blocked:** None
- **Needs first:** Nothing

## Outlook
- **Trajectory:** On-track
- **Risk:** Low — isolated bug fixes
- **Momentum:** Auth flow is now solid, dashboard UX improving

## Next Steps
1. **Fix N+1 in getUserCourses** — add JOIN for enrollments instead of per-course query
2. **Add loading states to remaining admin pages** — 4 pages still flash blank
3. **Run full test suite** — haven't run since auth changes

## Decisions Made
- Used skeleton loaders over spinners — better perceived performance
```

### Research session (no code changes)
```markdown
---
session: 2026-03-01
project: your-memory-repo
type: session_summary
---

# Session Summary: 2026-03-01

## Status
| Item | State | Detail |
|------|-------|--------|
| v14.0 research | DONE | 40 findings scored, top 5 identified |
| Implementation | NOT STARTED | Research phase only |

## Readiness
- **Ready:** Implement Wave 1 (top 3 findings, all internal gaps)
- **Blocked:** None
- **Needs first:** Decision on whether to batch Wave 1+2 or ship incrementally

## Outlook
- **Trajectory:** Exploratory — research complete, execution next
- **Risk:** Medium — top finding requires Qdrant schema migration
- **Momentum:** Strong — research agents produced high-quality findings

## Next Steps
1. **Implement finding #1** — add TTL-based auto-expiry to stale points
2. **Implement finding #2** — hybrid BM25+vector scoring pipeline
3. **Decide shipping strategy** — batch vs incremental for v14.0

## Decisions Made
- Internal gaps again outscored academic papers — prioritize gap closure
```

---

## Success Criteria

- [ ] Summary is under 30 lines of content
- [ ] All 5 sections populated (Status, Readiness, Outlook, Next Steps, Decisions)
- [ ] Next Steps are specific and actionable (not vague)
- [ ] File saved to `~/.claude/session-summaries/`
- [ ] Project name detected or specified
- [ ] Status uses DONE/PARTIAL/BLOCKED consistently

---

*Fills the gap between full WARRIOR handoffs and the auto-memory system.*
*Forward-looking context that the memory system doesn't capture.*
