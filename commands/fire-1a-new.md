---
description: Initialize a new project with Dominion Flow (Dominion Flow)
---

# /fire-1a-new

> Initialize a new project — scaffold directory, gather requirements, create .planning/ structure

---

## Purpose

Create the project foundation: directory, requirements gathering, and the complete `.planning/` file structure. This is Step 1 of 3 in project initialization.

**Flow:** `/fire-1a-new` → `/fire-1b-research` → `/fire-1c-setup`

---

## Arguments

```yaml
arguments: none
optional_flags:
  --name: "Project name (will prompt if not provided)"
  --path: "Project path (defaults to current directory)"
  --minimal: "Skip adaptive questioning, use defaults"
```

---

## EXECUTION ORDER

```
STEP 1: Environment Validation  → create NEW project directory
STEP 2: Gather Requirements     → MODE GATE question, backward interview if needed
STEP 3: Create .planning/       → mkdir + touch ALL files (EXACT names, no renaming)
FINAL:  Chain to next command    → tell user to run /fire-1b-research
```

**Complete each step before starting the next. No skipping.**

---

## Step 1: Environment Validation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                         DOMINION FLOW > PROJECT INITIALIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

1. **Create a NEW project directory** — Do NOT initialize inside an existing project. If the current directory has source code, `package.json`, or `.planning/`, create a new directory:
   ```bash
   mkdir -p {project-path}/{project-name}
   cd {project-path}/{project-name}
   git init
   ```
   Use `--path` flag if provided, otherwise ask the user or derive from project name.
2. Check if `.planning/` already exists (warn if so — means project was already initialized)
3. Verify write permissions
4. Create git repo if not present

---

## Step 2: Gather Requirements

**Core Questions:**
1. What is this project? (one sentence)
2. Who is the primary user?
3. What is the core value it provides?
4. What are the non-negotiable features (must-haves)?

**The MODE GATE Question:**

> **"Have you already started building this, or are we starting from scratch?"**

This reveals technical level without asking them to self-assess:

| Answer | Mode |
|--------|------|
| "I already have a React app with Express backend" | **Forward** — validate their stack |
| "I started something but I'm stuck" | **Forward** — audit what exists |
| "Starting from scratch, but I want Python" | **Forward** — build around preference |
| "Starting from scratch" | **Backward** — derive stack from vision |
| "I have an idea but don't know where to start" | **Backward** — full interview |
| "I have a WordPress site and want to add features" | **Forward** — WordPress-aware stack |

**If Forward Mode** (user has code or stated tech preferences):
1. Existing codebases to integrate with?
2. Known technical constraints?
3. *(Anti-Frankenstein gate validates choices later in /fire-1b-research)*

**If Backward Mode** (user described product, not tech):
Use the interview protocol from `@skills-library/_general/methodology/BACKWARD_PLANNING_INTERVIEW.md`:

0. **Visual Input (ALWAYS ask first)** — "Do you have anything visual — screenshot, wireframe, sketch? Drop it here."
   - If provided: Extract requirements, save to `.planning/research/VISUAL-ANALYSIS.md`, skip questions already answered
   - If not: Proceed to question 1
1. **The Walkthrough** — "Walk me through a user's first 60 seconds"
2. **The Money Screen** — "What's the ONE screen where your app delivers the most value?"
3. **The Similar App** — "Name 1-2 apps that feel closest to yours"
4. **The Deal-Breakers** — Yes/no: login, payments, uploads, emails, mobile, real-time
5. **The MVP Gate** — "If you could only ship THREE features, which three?"

**Template Selection (v12.3 — W2-A):**

After determining Forward/Backward mode and gathering core requirements, ask:

```
PROJECT TEMPLATE
────────────────────────────────────────────────────────────────
Which template best matches your vision?

  1. SaaS Application
     Includes: auth, payments, multi-user accounts, subscription tiers
     Pre-populates: user table, billing model, role-based access

  2. Community / LMS Platform
     Includes: courses, lessons, progress tracking, user groups
     Pre-populates: content models, enrollment, progress state

  3. Marketplace
     Includes: products, sellers, orders, reviews, search
     Pre-populates: product catalog, transaction model, seller onboarding

  4. Blog / Content Site
     Includes: posts, categories, SEO, publishing workflow
     Pre-populates: content model, slug routing, feed generation

  5. Internal Tool / Admin Dashboard
     Includes: data views, filters, bulk actions, role-based access
     Pre-populates: CRUD scaffolding, filter patterns, audit log

  6. REST API / Microservice
     Includes: endpoints, auth middleware, rate limiting, versioning
     Pre-populates: route structure, error format, auth pattern

  7. Custom (describe it — I'll derive the template)

Select template (1-7): >
```

**If template selected (1-6):** Pre-fill known requirements in PROJECT.md and
pre-populate phase suggestions in REQUIREMENTS.md based on the template pattern.
Note in REQUIREMENTS.md: `Template: {name} (user-selected)`.

**If Custom (7):** Proceed with standard requirements gathering — no pre-fill.

> and v0.dev gallery pattern + create-t3-app (28k★). Template selection eliminates
> the blank-page problem and pre-populates common phase structures, reducing planning
> time for well-understood project types by 30-50%.

**Timeline Questions:**
1. Target completion date?
2. Critical milestones?

**Save outputs:**
- `.planning/PROJECT.md` — requirements summary
- `.planning/REQUIREMENTS.md` — REQ-IDs for traceability

---

## Step 3: Create .planning/ Structure

**Create directories:**

```bash
mkdir -p .planning/research .planning/phases
```

**Create CONSCIENCE.md** using template from `@templates/state.md`:
- Project name and core value
- Current phase: 1 of N (placeholder until ROADMAP.md exists)
- Status: Ready to research
- WARRIOR Integration section
- Session Continuity section

**After Step 3, these files MUST exist:**

```
.planning/
├── PROJECT.md              # Step 2
├── REQUIREMENTS.md         # Step 2
├── CONSCIENCE.md           # Step 3
├── research/               # empty, ready for /fire-1b-research
└── phases/                 # empty, ready for /fire-2-plan
```

**Verify before proceeding:**
```bash
test -f .planning/PROJECT.md && test -f .planning/REQUIREMENTS.md && test -f .planning/CONSCIENCE.md && echo "ALL FILES PRESENT" || echo "MISSING FILES — go back"
```

---

## Completion

```
+==============================================================================+
| SCAFFOLD COMPLETE                                                            |
|==============================================================================|
|                                                                              |
|  Project: {project_name}                                                     |
|  Mode:    {forward/backward}                                                 |
|  Status:  Ready to research                                                  |
|                                                                              |
|  Created:                                                                    |
|    [x] .planning/PROJECT.md              <- requirements                     |
|    [x] .planning/REQUIREMENTS.md         <- REQ-IDs                          |
|    [x] .planning/CONSCIENCE.md           <- project state                    |
|                                                                              |
|  Pending (created by next commands):                                         |
|    [ ] research/SYNTHESIS.md             <- /fire-1b-research                 |
|    [ ] VISION.md                         <- /fire-1b-research                 |
|    [ ] ROADMAP.md                        <- /fire-1b-research                 |
|    [ ] TOOLING-LOG.md                    <- /fire-1c-setup                    |
|    [ ] WARRIOR handoff                   <- /fire-1c-setup                    |
|                                                                              |
|==============================================================================|
| NEXT UP                                                                      |
|------------------------------------------------------------------------------|
|                                                                              |
|  -> Run /fire-1b-research to spawn researchers and select architecture        |
|                                                                              |
+==============================================================================+
```

---

## Error Handling

### .planning/ Already Exists

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ ⚠ WARNING: Existing Project Detected                                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Options:                                                                    ║
║    A) Use `/fire-6-resume` to continue existing project                     ║
║    B) Delete .planning/ and run `/fire-1a-new` again                         ║
║    C) Use `--path [new-directory]` to initialize elsewhere                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## References

- **Template:** `@templates/state.md` - CONSCIENCE.md template
- **Skill:** `@skills-library/_general/methodology/BACKWARD_PLANNING_INTERVIEW.md`
- **Brand:** `@references/ui-brand.md` - Visual output standards
