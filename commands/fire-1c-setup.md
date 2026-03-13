---
description: Install tooling, create handoff, and finalize project initialization (Dominion Flow)
---

# /fire-1c-setup

> Install CLI tools, create WARRIOR handoff, verify all files, show completion

---

## Purpose

Finalize project initialization: install all CLI tools the locked stack requires, create the WARRIOR handoff, and verify every file exists. This is Step 3 of 3 in project initialization.

**Flow:** `/fire-1a-new` → `/fire-1b-research` → **`/fire-1c-setup`**

**Prerequisite:** `.planning/VISION.md` (locked) and `.planning/ROADMAP.md` must exist (created by `/fire-1b-research`).

---

## EXECUTION ORDER

```
STEP 1: Validate prerequisites     → VISION.md + ROADMAP.md exist
STEP 2: WARRIOR Handoff Init       → create handoff file
STEP 3: Zero-Friction Tooling      → install CLIs from VISION.md, write TOOLING-LOG.md
STEP 4: SKILLS-INDEX.md            → create empty tracking file
STEP 4.5: Seed per-project skills/ → create skills/ folder + README.md + .gitkeep
STEP 5: Update CONSCIENCE.md       → set status to "Ready to plan"
STEP 6: MANDATORY FILE GATE        → verify ALL 16 files exist
FINAL:  Completion Display          → show full project summary
```

**Complete each step before starting the next.**

---

## Step 1: Validate Prerequisites

```bash
test -f .planning/VISION.md && test -f .planning/ROADMAP.md && echo "READY" || echo "MISSING — run /fire-1b-research first"
```

If files are missing, stop and tell the user to run `/fire-1b-research` first.

---

## Step 2: WARRIOR Handoff Init

**Create handoff directory if not exists:**
```bash
mkdir -p ~/.claude/warrior-handoffs/
```

**Create initial handoff file:**
```
~/.claude/warrior-handoffs/{PROJECT_NAME}_YYYY-MM-DD_init.md
```

Include: project name, core value, locked stack, phase count, current status, key decisions made, next steps.

---

## Step 3: Zero-Friction Tooling (MANDATORY)

**Claude auto-installs ALL CLI tools the locked VISION.md stack requires.** The user should never manually install anything.

**Read VISION.md and install everything the stack needs.**

Reference: `@skills-library/_general/methodology/ZERO_FRICTION_CLI_SETUP.md`

**Always install (every web project):**
```bash
npm install -D @playwright/test
npx playwright install chromium firefox
```

> Playwright MCP is the primary visual testing tool for verification.

**Install based on VISION.md stack:**

| Stack Requirement | CLI Command |
|------------------|-------------|
| Supabase | `npx supabase init` then `npx supabase start` |
| Stripe payments | `npm install stripe @stripe/stripe-js` |
| Next.js | `npx create-next-app@latest` |
| Prisma ORM | `npx prisma init` then `npx prisma generate` |
| Drizzle ORM | `npm install drizzle-orm` + `npm install -D drizzle-kit` |
| Tailwind CSS | `npm install -D tailwindcss @tailwindcss/vite` |
| shadcn/ui | `npx shadcn@latest init` |
| better-auth | `npx @better-auth/cli generate` |
| Firebase | `npx firebase-tools init` |
| Docker | `docker compose up -d` (if compose.yml exists) |
| ESLint + Prettier | `npm install -D eslint prettier eslint-config-prettier` |
| Husky (git hooks) | `npx husky init` |

**Process:**
1. Read locked VISION.md Technology Stack table
2. Match each technology to its CLI setup command
3. Run all installations sequentially (dependencies first)
4. Verify each tool installed correctly (version check)
5. Log installed tools to `.planning/TOOLING-LOG.md`

**Skip conditions:**
- Backend-only projects skip Playwright and frontend tools
- User explicitly opts out of a specific tool
- Tool already installed (check `package.json` or version command)

---

## Step 4: SKILLS-INDEX.md

```markdown
# Skills Applied to This Project

## Summary
- Total skills applied: 0
- Categories used: 0
- Last skill applied: N/A

## By Phase
*No phases executed yet*

## By Category
*Skills will be tracked here as they're applied during execution*

## Quick Reference
Run `/fire-search [query]` to find relevant skills.
```

---

## Step 4.5: Seed Per-Project Skills Folder

**Create the project-local skills directory:**

```bash
mkdir -p {project_root}/skills
touch {project_root}/skills/.gitkeep
```

**Create `{project_root}/skills/README.md`:**

```markdown
# Project Skills — {project_name}

Project-specific patterns, workarounds, and solutions for this codebase.

## Usage
Add skills here when you discover a pattern worth preserving for this project.
Use the skill name as the filename: `skill-name.md`

## Global Skills
Cross-project skills live in:
`~/.claude/plugins/dominion-flow/skills-library/`

Run `/fire-search` to find skills across both locations.
```

**Confirm to user:**
> "Per-project `skills/` folder seeded. Add project-specific patterns here as you discover them."

---

## Step 5: Update CONSCIENCE.md

Update `.planning/CONSCIENCE.md`:
- Status: `Ready to plan`
- Phase count: from ROADMAP.md
- Last Action: `Project initialized via /fire-1a-new → /fire-1b-research → /fire-1c-setup`

---

## Step 6: MANDATORY FILE GATE

**Before showing completion, verify EVERY file exists. If ANY is missing, go back and create it.**

```bash
echo "=== FILE GATE CHECK ==="
test -f .planning/PROJECT.md            || echo "MISSING: PROJECT.md"
test -f .planning/REQUIREMENTS.md       || echo "MISSING: REQUIREMENTS.md"
test -f .planning/CONSCIENCE.md         || echo "MISSING: CONSCIENCE.md"
test -f .planning/SKILLS-INDEX.md       || echo "MISSING: SKILLS-INDEX.md"
test -f .planning/research/SYNTHESIS.md || echo "MISSING: SYNTHESIS.md"
test -f .planning/VISION.md             || echo "MISSING: VISION.md"
test -f .planning/ROADMAP.md            || echo "MISSING: ROADMAP.md"
test -f .planning/research/ALTERNATIVES.md || echo "MISSING: ALTERNATIVES.md"
test -f .planning/TOOLING-LOG.md        || echo "MISSING: TOOLING-LOG.md"
test -d .planning/phases                || echo "MISSING: phases/"
echo "=== GATE COMPLETE ==="
```

**If ANY file is missing, DO NOT show completion. Go back to the step that creates it — or tell the user which prior command to re-run.**

---

## DevTools Guide (Backward Mode Only)

For users who were in backward mode (beginners), save a brief DevTools orientation to `.planning/DEVTOOLS-GUIDE.md`:

```markdown
## Quick DevTools Guide

**Open DevTools:** F12 or Ctrl+Shift+I (Windows) / Cmd+Option+I (Mac)

**3 tabs you'll use:**
1. **Console** — errors show here (red = error, yellow = warning)
2. **Network** — API calls (filter by Fetch/XHR)
3. **Elements** — HTML/CSS inspector (click magnifier icon → click element)

**Pro tip:** When something breaks, open Console, reproduce the error, screenshot the red text, share with Claude.
```

---

## Completion Display

**Show ONLY after file gate passes with zero missing files:**

```
+==============================================================================+
| PROJECT INITIALIZED                                                          |
|==============================================================================|
|                                                                              |
|  Project: {project_name}                                                     |
|  Stack:   {locked stack from VISION.md}                                      |
|  Phases:  {phase_count} defined in ROADMAP.md                                |
|  Status:  Ready to plan                                                      |
|                                                                              |
|  Core Files:                                                                 |
|    [x] .planning/PROJECT.md              <- requirements                     |
|    [x] .planning/REQUIREMENTS.md         <- REQ-IDs                          |
|    [x] .planning/VISION.md               <- LOCKED                           |
|    [x] .planning/ROADMAP.md              <- phase breakdown                  |
|    [x] .planning/CONSCIENCE.md           <- project state                    |
|                                                                              |
|  Research:                                                                   |
|    [x] .planning/research/SYNTHESIS.md   <- merged research + GitHub refs    |
|    [x] .planning/research/ALTERNATIVES.md <- rejected branches               |
|                                                                              |
|  Tooling:                                                                    |
|    [x] .planning/TOOLING-LOG.md          <- installed CLIs                   |
|    [x] WARRIOR handoff                   <- session continuity               |
|                                                                              |
|  Gates Triggered:                                                            |
|    [?] Mode Gate        -> {forward/backward}                                |
|    [?] Anti-Frankenstein -> {conflicts found / clean}                        |
|    [?] Vision Architect -> {N} branches, Branch {X} selected                 |
|    [?] Vision Lock      -> VISION.md marked LOCKED                           |
|                                                                              |
|==============================================================================|
| NEXT UP                                                                      |
|------------------------------------------------------------------------------|
|                                                                              |
|  -> Run /fire-2-plan 1 to create plans for Phase 1                           |
|  -> Or run /fire-dashboard to view project status                            |
|                                                                              |
+==============================================================================+
```

---

## Error Handling

### Missing Prerequisites
```
╔══════════════════════════════════════════════════════════════════════════════╗
║ ✗ ERROR: Run /fire-1b-research first                                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Missing: .planning/VISION.md or .planning/ROADMAP.md                        ║
║  These are created by /fire-1b-research. Run that command first.              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## References

- **Skill:** `@skills-library/_general/methodology/ZERO_FRICTION_CLI_SETUP.md`
- **Protocol:** `@references/honesty-protocols.md` - WARRIOR honesty foundation
- **Template:** `@templates/state.md` - CONSCIENCE.md template
- **Template:** `@templates/skills-index.md` - Skills tracking template
