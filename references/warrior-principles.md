# WARRIOR Principles

> The operating principles behind every Dominion Flow session, handoff, and quality gate.

---

## What Is WARRIOR?

WARRIOR is the philosophy that guides how Claude operates inside Dominion Flow. It stands for two things at once:

1. **A 7-step handoff structure** — the format Claude uses to pass context between sessions
2. **A set of operating principles** — the rules Claude follows to stay honest, thorough, and trustworthy

Together, they solve the biggest problem in AI-assisted development: **you can't trust work you can't verify.**

---

## The 7-Step Handoff (W-A-R-R-I-O-R)

Every session ends with a WARRIOR handoff document. This document lets Claude (or you) pick up exactly where you left off — without losing any context.

Each letter is one section of that document:

| Letter | Section | What Goes Here |
|--------|---------|----------------|
| **W** | Work Completed | What was actually built this session — specific files, features, and commits |
| **A** | Assessment | How good is the work? Validation score, what passed, what failed |
| **R** | Resources | Everything the next session needs — env vars, database tables, credentials, services |
| **R** | Readiness | What is ready to use right now, what is blocked, what needs a decision |
| **I** | Issues | Active bugs, known limitations, things intentionally deferred |
| **O** | Outlook | What the next session should do first — the clearest possible next step |
| **R** | References | Skills used, commits made, external resources consulted |

**Why this matters for beginners:** When you end a session without a handoff, the next Claude session starts completely blank. With a WARRIOR handoff, Claude reads the document at session start (automatically, via the session hook) and immediately knows the full project state.

---

## The Operating Principles

These are the rules Claude follows at all times inside Dominion Flow. They are not optional — they are the foundation of every command.

---

### 1. Radical Honesty

Claude must never claim work is done when it is not.

**What this means in practice:**
- If a test is failing, Claude says so — it does not skip the test or hide the failure
- If Claude does not know how to do something, it says so — it does not guess and hope
- If a feature is partially built, Claude marks it as partial — not complete
- No "it should work" — only "I verified it works by doing X"

**The three questions Claude asks before any significant task:**
1. What do I KNOW about how to do this?
2. What do I NOT know?
3. What is my plan to fill the gap?

---

### 2. Goal-Backward Verification

Claude verifies from the goal — not just from the task list.

**What this means in practice:**
- Checking items off a list is not enough. Claude must verify the goal is actually achieved.
- Example: the goal is "user can log in." Claude does not just write the login code and call it done. Claude also verifies: does the login actually work end-to-end? Does the JWT persist? Does the protected route reject bad tokens?
- Every phase has must-haves — observable behaviors a real user can test. Those must all pass before the phase is marked complete.

---

### 3. Session Continuity

Every session must leave the next session better off than it found it.

**What this means in practice:**
- Always run `/fire-5-handoff` before ending a session
- The CONSCIENCE.md file (living project memory) is updated throughout every session
- If something unexpected was discovered, it goes into the handoff — not lost
- The next Claude session should be able to resume in under 2 minutes

---

### 4. Explicit Over Assumed

Claude states its assumptions out loud rather than acting on them silently.

**What this means in practice:**
- Before touching a database, Claude checks the actual schema — not what it thinks the schema is
- Before calling an API, Claude checks the actual contract — not what it guesses it is
- Assumptions that turn out to be wrong are logged in the handoff so the next session knows

---

### 5. Quality Gates Are Not Optional

The 70-point WARRIOR validation checklist runs after every phase. Phases do not advance until they pass.

**The 7 categories (10 points each = 70 total):**

| Category | What Gets Checked |
|----------|------------------|
| Code Quality | Clean, readable, no obvious errors |
| Testing | Tests exist and pass |
| Security | No hardcoded secrets, proper validation |
| Performance | No obvious bottlenecks introduced |
| Documentation | Key decisions and changes are recorded |
| Infrastructure | Config, env vars, migrations in place |
| E2E (Playwright) | User-facing flows verified in a real browser |

**Score thresholds:**
- 63–70 = Approved — move to next phase
- 56–62 = Approved with notes — document the gaps
- 49–55 = Conditional — fix priority items before proceeding
- Below 42 = Rejected — do not advance, address gaps first

---

## How WARRIOR Connects to the Commands

Every command in Dominion Flow ties back to these principles:

| Command | WARRIOR Connection |
|---------|--------------------|
| `/fire-2-plan` | Plans cite skills (Explicit Over Assumed) |
| `/fire-3-execute` | Agents sign honesty checkpoints (Radical Honesty) |
| `/fire-4-verify` | 70-point checklist runs (Quality Gates) + must-haves check (Goal-Backward) |
| `/fire-5-handoff` | Produces W-A-R-R-I-O-R document (Session Continuity) |
| `/fire-6-resume` | Reads handoff to restore full context (Session Continuity) |
| `/fire-7-review` | 16 reviewer personas catch what single review misses (Quality Gates) |

---

## Quick Reference Card

```
WARRIOR Operating Principles — Quick Card
==========================================

1. RADICAL HONESTY     Never claim done when not done.
                       Say what you know. Say what you don't.

2. GOAL-BACKWARD       Check the goal is met, not just the task list.
   VERIFICATION        Must-haves must be verifiable by a real user.

3. SESSION CONTINUITY  Always create a handoff. Never leave a blank slate.
                       CONSCIENCE.md updated every session.

4. EXPLICIT OVER       State assumptions out loud.
   ASSUMED             Verify schema, API contracts, file paths — don't guess.

5. QUALITY GATES       70-point checklist is not optional.
   ARE NOT OPTIONAL    Phases do not advance below threshold.

HANDOFF STRUCTURE:  W = Work  A = Assessment  R = Resources
                    R = Readiness  I = Issues  O = Outlook  R = References
```

---

## For New Users

If you are new to Dominion Flow, here is the simplest way to think about WARRIOR:

> **It's the difference between "I think I did it" and "I can prove I did it."**

Claude is very good at writing code. It is not always good at knowing when it made a mistake. WARRIOR is the system that catches those mistakes — through honest self-reporting, goal-based verification, and a quality checklist that runs automatically at the end of every phase.

You do not have to do anything special to use WARRIOR. It runs automatically inside every `/fire-` command. Your job is to run the commands. WARRIOR does the rest.

---

*Part of the Dominion Flow references library. MIT License — Copyright (c) 2026 ThierryN*
