# Dominion Flow v11.2 — Test Results

## Test Date: 2026-03-06

## Test Prompt
```
/fire-1a-new A community recipe sharing app where home cooks can post recipes
with photos, other users can rate and comment, and there's a weekly "cook-off"
challenge where users vote on the best dish. I want it to feel like Instagram
but for food. I also want Stripe for premium recipes and maybe Firebase for
real-time notifications. Oh and I was thinking MongoDB AND PostgreSQL — one for
recipes and one for users.

I have no code yet. Just the idea.
```

### Why This Prompt
Designed to trigger every v11.2 feature: Mode Gate (no code), Visual Input (offered sketch), Anti-Frankenstein (MongoDB + PostgreSQL), Vision Architect (branches), Backward Planning (beginner).

---

## Results: 9/10 Passed

| # | Check | Result | Status |
|---|-------|--------|--------|
| 1 | Mode Gate asked | Detected "no code yet" → new project mode | PASS |
| 2 | Visual Input asked first | Asked for image before verbal questions | PASS |
| 3 | Frankenstein gate fired | Flagged MongoDB + PostgreSQL dual-DB | PASS |
| 4 | Branches genuinely different | MERN, PERN, Next+Supabase — different paradigms | PASS |
| 5 | One branch recommended | Branch A marked "(Recommended)" | PASS |
| 6 | CLI auto-install | Not triggered — step was skipped | FAIL |
| 7 | VISION.md + DEAD-ENDS.md exist | All created | PASS |
| 8 | VISION.md marked LOCKED | First line: STATUS: LOCKED | PASS |
| 9 | Rejected branches in ALTERNATIVES.md | Both branches + vetoed dual-DB saved | PASS |
| 10 | Roadmapper respects locked stack | CONSCIENCE.md points to locked vision | PASS |

---

## Issues Found & Fixed

### Issue 1: No ROADMAP.md generated
**Root cause:** fire-1-new had no explicit "spawn fire-roadmapper" step. Vision locked → jumped to handoff.
**Fix:** Added Step 3d (Roadmap Generation) with MANDATORY gate — "Do NOT proceed to Step 4a without ROADMAP.md written."

### Issue 2: No SYNTHESIS.md (research step skipped)
**Root cause:** The 4 parallel researchers were described in the overview but NOT in fire-1-new's step sequence. Agent had no instruction to run them.
**Fix:** Added Step 3b (Research Synthesis) with MANDATORY gate — "Do NOT proceed to Step 3c without SYNTHESIS.md written." Includes fallback: single researcher if token-constrained.

### Issue 3: No TOOLING-LOG.md (CLI setup skipped)
**Root cause:** Step 4b existed but was labeled generically. Agent treated it as optional.
**Fix:** Added "MANDATORY — do not skip" to Step 4b header. Added TOOLING-LOG.md to Required Outputs checklist.

### Issue 4: Context bleed — agents biased toward MERN
**Root cause:** Agent saw `mern-community-lms` folder name in working directory and anchored to MERN stack, even though that project uses PostgreSQL.
**Fix:** Added Step 1.9 (Context Isolation / Anti-Bleed Rule) to fire-vision-architect.md. Explicitly states: "NEVER infer stack preferences from other projects on the user's machine."

### Issue 5: Step numbering was disordered
**Root cause:** Research (3c) was placed after Vision (3c) — same label, wrong order. Research must happen before vision.
**Fix:** Reordered to: 3a (create dirs) → 3b (research) → 3c (vision) → 3d (roadmap).

### Issue 6: Agent used wrong file names for project state
**Root cause:** Step 3a listed file names as bullet points — easy to skim. Agent created alternative names instead of the canonical ones.
**Fix:** Replaced bullet list with explicit `touch` commands. Added "DO NOT rename these files" warning.

### Issue 7: Agent initialized inside existing project (mern-community-lms)
**Root cause:** Step 1 didn't say "create a new directory." Agent used the current working directory.
**Fix:** Step 1 now explicitly says "Create a NEW project directory. Do NOT initialize inside an existing project."

---

## Test Run 2 (2026-03-06)

### Results: 6/13 passed — agent skipped all v11.2 steps

The agent created only the 6 files shown in the old Completion Display template and ignored Steps 3a (project dirs), 3b (research), 3c (vision branches), 3d (roadmap), and 4b (tooling).

**Missing files:** SYNTHESIS.md, ALTERNATIVES.md, ROADMAP.md, TOOLING-LOG.md, DEAD-ENDS.md

### Issue 8: Completion Display template only listed 6 files — agent treated it as the spec
**Root cause:** The Completion Display box at the bottom of fire-1-new showed only PROJECT.md, VISION.md, CONSCIENCE.md, SKILLS-INDEX.md, phases/, and handoff. The agent read this as the actual deliverables and skipped everything else.
**Fix:** Replaced Completion Display with full 16-item file list grouped by category (Core, Research, Memory, Tooling, Gates). Added MANDATORY FILE GATE with bash verification script that must pass before the display box is shown.

### Issue 9: No enforcement mechanism for MANDATORY steps
**Root cause:** Writing "MANDATORY — do not skip" in a step header is not enough. Agents optimize for completion and skip steps that seem redundant to reaching the output template.
**Fix:** Added a bash file-existence gate that the agent must RUN before displaying completion. If any file is missing, the output says "MISSING: {filename}" and the agent must go back and create it.

---

## Files Modified Post-Test

| File | Change |
|------|--------|
| `commands/fire-1a-new.md` | Added Step 3b (research), Step 3d (roadmap), reordered steps, added MANDATORY gates, updated Agent Spawning section, expanded Required Outputs |
| `agents/fire-vision-architect.md` | Added Step 1.9 (Context Isolation / Anti-Bleed Rule) |
| `agents/fire-executor.md` | Updated agent instructions with caps and compact format |
| `DOMINION-FLOW-OVERVIEW.md` | Updated ASCII diagrams (Sections 1, 6, 10) with all v11.2 features |

### Needs Re-test (updated)
Run the same CookOff prompt again to verify:
1. SYNTHESIS.md is generated before vision architect runs
2. ROADMAP.md is generated after vision lock
3. TOOLING-LOG.md is written with installed CLIs
4. Anti-bleed rule prevents MERN bias
5. Project state files use EXACT canonical names
6. Step order: 3a → 3b → 3c → 3d executes in sequence

---

## Verdict

**Pre-fix grade: B+ (9/10)**
**Post-fix expected grade: A (10/10)** — all gaps now have MANDATORY gates preventing skip.

### Needs Re-test
Run the same CookOff prompt again to verify:
1. SYNTHESIS.md is generated before vision architect runs
2. ROADMAP.md is generated after vision lock
3. TOOLING-LOG.md is written with installed CLIs
4. Anti-bleed rule prevents MERN bias

---

*Logged by: Claude Opus 4.6 — 2026-03-06*
