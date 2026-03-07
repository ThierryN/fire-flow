# Dominion Flow Quick Start Guide

**Dominion Flow gives Claude a structured way to build your software — with built-in memory, parallel execution, and automatic quality checks. This guide walks you through your first project, one step at a time.**

---

## Why Use This?

Without Dominion Flow, Claude starts fresh every session with no memory of what you were building. Dominion Flow fixes that — and adds a lot more:

- Claude remembers your project between sessions
- Work is verified before moving on (no silent failures)
- Faster execution by running independent tasks at the same time
- A library of 190+ proven patterns Claude can use instead of guessing

---

## What You Need Before Starting

- Claude Code CLI installed and working
- A project directory (new or existing)
- A terminal window open

---

## The 6-Command Workflow

Dominion Flow uses 6 numbered commands that take your project from start to finish. Each command has one clear job.

```
1-new --> 2-plan --> 3-execute --> 4-verify --> 5-handoff --> 6-resume
                                                    |
                                              fire-autonomous
                                           (full autopilot alternative)
```

**Option A — Step by step:** Run each command yourself and review between steps. Good when you want to stay in control.

**Option B — Full autopilot:** After step 1, run `/fire-autonomous` and Claude handles everything automatically.

---

## Step 1: Start a New Project

```bash
/fire-1a-new
```

This command:
- Creates the `.planning/` directory structure
- Initializes `CONSCIENCE.md` with project context
- Creates `VISION.md` with phases
- Sets up skills library integration
- Asks you about project goals, tech stack, and constraints

**What you'll see:**
```
[Dominion Flow] Initializing new project...

What is the project name?
> My Awesome App

Brief description (1-2 sentences)?
> A task management app with calendar integration

Primary tech stack?
> MERN (MongoDB, Express, React, Node.js)

Creating .planning/ structure...
  - CONSCIENCE.md (living project memory)
  - VISION.md (phase overview)
  - phases/ (detailed plans)

Project initialized! Run /fire-2-plan 1 to plan your first phase.
```

---

## Step 2: Plan Your First Phase

```bash
/fire-2-plan 1
```

This command:
- Searches the skills library for relevant patterns
- Creates a detailed `BLUEPRINT.md` for phase 1
- Defines must-have deliverables
- Estimates complexity and time
- Identifies potential blockers

**What you'll see:**
```
[Dominion Flow] Planning Phase 1...

Searching skills library for: authentication, user management...
Found 12 relevant skills:
  - integrations/oauth-patterns.md
  - database-solutions/user-schema.md
  - deployment-security/jwt-auth.md

Creating .planning/phases/01-authentication/BLUEPRINT.md...

Phase 1 Plan Ready:
  - 5 tasks identified
  - 3 must-haves defined
  - Estimated: 2-3 hours
  - Skills referenced: 3

Ready to execute? Run /fire-3-execute 1
```

---

## Step 3: Execute the Phase

```bash
/fire-3-execute 1
```

This command:
- Reads the BLUEPRINT.md for phase 1
- Groups tasks into parallel breaths
- Executes tasks with progress tracking
- Updates CONSCIENCE.md in real-time
- Applies honesty protocols (no false completion claims)

**What you'll see:**
```
[Dominion Flow] Executing Phase 1...

Reading plan from .planning/phases/01-authentication/BLUEPRINT.md

Breath 1 (Parallel):
  [x] Create user schema
  [x] Set up JWT middleware
  [ ] Configure OAuth providers  <-- In Progress

Breath 2 (Depends on Breath 1):
  [ ] Build login endpoint
  [ ] Build registration endpoint

Progress: 2/5 tasks (40%)
CONSCIENCE.md updated.

Continue? (y/n)
```

---

## Step 4: Verify Completion

```bash
/fire-4-verify 1
```

This command:
- Checks all must-haves from the plan
- Runs the 70-point validation checklist
- Verifies code actually works (not just "looks done")
- Flags any gaps or issues
- Updates phase status in CONSCIENCE.md

**What you'll see:**
```
[Dominion Flow] Verifying Phase 1...

Must-Haves Check:
  [x] User can register with email/password
  [x] User can log in and receive JWT
  [x] Protected routes require valid token

Validation Checklist (subset):
  [x] No hardcoded credentials
  [x] Error handling in place
  [x] Input validation present
  [!] Missing: Rate limiting on auth endpoints

Result: PARTIAL PASS
  - 3/3 must-haves complete
  - 1 recommendation flagged

Phase 1 marked as COMPLETE with notes.
Ready for /fire-2-plan 2 or /fire-5-handoff
```

---

## Step 5: Create a Handoff

```bash
/fire-5-handoff
```

Before ending your session, always create a handoff. This command:
- Captures current CONSCIENCE.md
- Documents what was accomplished
- Lists what's in progress
- Notes any blockers or decisions needed
- Creates a POWER-HANDOFF.md file

**What you'll see:**
```
[Dominion Flow] Creating session handoff...

Current Session Summary:
  - Phase 1: Authentication (COMPLETE)
  - Phase 2: User Dashboard (IN PROGRESS - 40%)
  - Skills used: 5
  - Time spent: ~3 hours

In Progress:
  - Dashboard layout component
  - Task list API endpoint

Blockers:
  - Need to decide on state management (Redux vs Context)

Handoff created: .planning/POWER-HANDOFF-2025-01-22.md

Next session: Run /fire-6-resume to continue.
```

---

## Step 6: Resume Next Session

```bash
/fire-6-resume
```

When you start a new session, this command:
- Reads the latest POWER-HANDOFF.md
- Loads CONSCIENCE.md context
- Displays what was in progress
- Suggests next actions
- Restores full project context

**What you'll see:**
```
[Dominion Flow] Resuming from handoff...

Last session: 2025-01-22 (3 hours ago)

Project: My Awesome App
Current Phase: 2 - User Dashboard (40% complete)

In Progress Tasks:
  1. Dashboard layout component
  2. Task list API endpoint

Pending Decision:
  - State management: Redux vs Context

Suggested Actions:
  1. Continue /fire-3-execute 2
  2. Run /fire-dashboard for overview
  3. Use /fire-search "state management" for guidance

Context restored. Ready to continue!
```

---

## What Happens Automatically

Dominion Flow runs several systems behind the scenes without manual intervention:

- **Confidence Scoring** -- Before each task, the agent estimates confidence (0-100) based on skill matches, test availability, and tech familiarity. LOW confidence (<50) triggers extra research or user escalation.
- **Episodic Memory Injection** -- Each iteration automatically searches vector memory (Qdrant) for past experiences relevant to the current task. Falls back to file-based search if Qdrant is unreachable.
- **Parallel Review Gate** -- After execution, a code reviewer runs in parallel with the verifier. Both must agree before work is marked complete. The stricter verdict always wins.
- **Circuit Breaker** -- During `/fire-loop`, the system monitors for stalling (no progress), spinning (same error repeating), and degradation (output quality declining). It forces approach rotation or Sabbath Rest when thresholds are hit.
- **Auto-Skill Extraction** -- During phase transitions (`/fire-transition`), reusable patterns discovered during work are automatically proposed as new skills for the library.

---

## Command Tiers

Dominion Flow has **39 commands** organized into 7 tiers. The 6-command workflow above is Tier 1. For the complete list including autonomous mode, debugging, security scanning, skills management, analytics, and milestone commands, see [COMMAND-REFERENCE.md](./COMMAND-REFERENCE.md).

---

## Tips for Success

### 1. Always Create Handoffs
Before ending any session, run `/fire-5-handoff`. Future you (or another AI) will thank you.

### 2. Use the Skills Library
Before implementing anything, search for existing patterns:
```bash
/fire-search "payment integration"
/fire-search "file upload"
/fire-search "authentication"
```

### 3. Trust the Verification
Don't skip `/fire-4-verify`. It catches issues before they become problems.

### 4. Keep CONSCIENCE.md Updated
The CONSCIENCE.md file is your living project memory. Review it with `/fire-dashboard`.

### 5. Contribute Back
When you solve a new problem, add it to the library:
```bash
/fire-add-new-skill
```

---

## Common Workflows

### Starting Fresh
```bash
/fire-1a-new
/fire-2-plan 1
/fire-3-execute 1
/fire-4-verify 1
/fire-5-handoff
```

### Full Autopilot (after project init)
```bash
/fire-1a-new
/fire-autonomous
```

### Continuing Work
```bash
/fire-6-resume
/fire-3-execute 2    # Continue current phase
/fire-5-handoff
```

### Research Mode
```bash
/fire-search "caching strategies"
/fire-discover       # AI suggests relevant patterns
/fire-analytics      # See what skills are most used
```

---

## Next Steps

- Read [COMMAND-REFERENCE.md](./COMMAND-REFERENCE.md) for all 39 commands
- Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues and fixes
- Explore [ARCHITECTURE-DIAGRAM.md](./ARCHITECTURE-DIAGRAM.md) for system overview

---

*You're ready to go!*
