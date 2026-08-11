---
description: Research, vision selection, and roadmap generation for a new project (Dominion Flow)
---

# /fire-1b-research

> Spawn researchers, select architecture vision, generate roadmap

---

## Purpose

Research the technology landscape, select a coherent architecture, and generate the project roadmap. This is Step 2 of 3 in project initialization.

**Flow:** `/fire-1a-new` → **`/fire-1b-research`** → `/fire-1c-setup`

**Prerequisite:** `.planning/PROJECT.md` and `.planning/REQUIREMENTS.md` must exist (created by `/fire-1a-new`).

---

## EXECUTION ORDER

```
STEP 1: Validate prerequisites     → PROJECT.md + REQUIREMENTS.md exist
STEP 2: Research Synthesis          → spawn researchers, search GitHub, write SYNTHESIS.md
STEP 3: Vision Branch Selection     → spawn fire-vision-architect, user picks branch, LOCK VISION.md
STEP 4: Roadmap Generation          → spawn fire-roadmapper, write ROADMAP.md
FINAL:  Chain to next command       → tell user to run /fire-1c-setup
```

**Complete each step before starting the next. Each step produces a file — verify it exists before proceeding.**

---

## Step 1: Validate Prerequisites

```bash
test -f .planning/PROJECT.md && test -f .planning/REQUIREMENTS.md && echo "READY" || echo "MISSING — run /fire-1a-new first"
```

If files are missing, stop and tell the user to run `/fire-1a-new` first.

Read `.planning/PROJECT.md` to determine mode (forward/backward) for Step 3.

---

## Step 2: Research Synthesis (MANDATORY)

**Spawn 4 parallel researchers** (or sequential if resources are limited):

| Researcher | Focus | Output |
|-----------|-------|--------|
| STACK | Technology ecosystem, versions, compatibility | `research/STACK.md` |
| FEATURES | Feature implementation patterns, complexity | `research/FEATURES.md` |
| ARCHITECTURE | Folder structure, data flow, API design | `research/ARCHITECTURE.md` |
| PITFALLS | Common mistakes, known issues, anti-patterns | `research/PITFALLS.md` |

**Every researcher MUST search GitHub for open source reference projects:**

Search for 2-3 real open source projects similar to what the user is building:
- Repo name, stars, last updated
- Tech stack used
- Folder structure patterns
- Key patterns worth adopting
- Mistakes visible in their issues/PRs

**Search strategy:**
```
gh search repos "{project type}" --sort stars --limit 5
gh search repos "{project type} {framework}" --sort updated --limit 5
```

**Then synthesize:** Merge 4 files → `.planning/research/SYNTHESIS.md`

Include a "Reference Projects" section listing the best repos found, what to steal, and what to avoid.

> The 4-tier cascade: Skills Library → GitHub/Open Source → Context7 → Web search.

**If token-constrained:** Run a single researcher covering all 4 areas into one SYNTHESIS.md.

**Gate:** SYNTHESIS.md MUST exist before Step 3.

```bash
test -f .planning/research/SYNTHESIS.md && echo "SYNTHESIS READY" || echo "MISSING — complete research first"
```

---

## Step 3: Vision Branch Selection

**Spawn `fire-vision-architect`** with:
- `.planning/research/SYNTHESIS.md`
- `.planning/PROJECT.md`
- Any visual input from Step 2 of `/fire-1a-new`

**Two modes (auto-detected):**

**Forward Mode** — User stated a tech stack → Anti-Frankenstein gate checks compatibility → generate branches.

**Backward Planning Mode** — User described the PRODUCT, not tech:
```
Visual input → capability extraction
  + What does the finished product do?
    → What capabilities does that require?
      → What proven stacks deliver those? → branches
```

**Process:**

1. Mode detection from PROJECT.md
2. Anti-Frankenstein Gate (forward) or Capability Extraction (backward)
3. Generate 2-3 vision branches (often 2 in backward mode)
4. Display via `AskUserQuestion` — one marked "(Recommended)"
5. User picks one
6. **Lock selected branch as `.planning/VISION.md`**
7. **Save rejected branches to `.planning/research/ALTERNATIVES.md`**

**Gate:** VISION.md MUST exist and be LOCKED before Step 4.

```bash
test -f .planning/VISION.md && test -f .planning/research/ALTERNATIVES.md && echo "VISION LOCKED" || echo "MISSING — complete vision selection"
```

---

## Step 4: Roadmap Generation (MANDATORY)

**Spawn `fire-roadmapper`** with locked VISION.md:

1. Reads LOCKED `VISION.md` (does NOT make stack decisions)
2. Reads `REQUIREMENTS.md` for feature list
3. Groups requirements into phases by dependency order
4. Derives success criteria goal-backward from each phase objective
5. Validates 100% requirement coverage (every REQ-ID in a phase)
6. Writes `.planning/ROADMAP.md`

**Gate:** ROADMAP.md MUST exist before completion.

```bash
test -f .planning/ROADMAP.md && echo "ROADMAP READY" || echo "MISSING — complete roadmap generation"
```

> ROADMAP.md is what `/fire-2-plan` reads. Without it, `/fire-2-plan 1` has no Phase 1 definition.

---

## Agent Spawning Summary

| Agent | Input | Output | Step |
|-------|-------|--------|------|
| `fire-project-researcher` (x4) | PROJECT.md, REQUIREMENTS.md | research/*.md → SYNTHESIS.md | 2 |
| `fire-vision-architect` | SYNTHESIS.md, PROJECT.md, visual input | VISION.md, ALTERNATIVES.md | 3 |
| `fire-roadmapper` | VISION.md (locked), REQUIREMENTS.md | ROADMAP.md | 4 |

---

## Completion

```
+==============================================================================+
| RESEARCH & VISION COMPLETE                                                   |
|==============================================================================|
|                                                                              |
|  Project: {project_name}                                                     |
|  Stack:   {locked stack from VISION.md}                                      |
|  Phases:  {N} defined in ROADMAP.md                                          |
|                                                                              |
|  Created:                                                                    |
|    [x] .planning/research/SYNTHESIS.md   <- merged research + GitHub refs    |
|    [x] .planning/VISION.md               <- LOCKED architecture              |
|    [x] .planning/research/ALTERNATIVES.md <- rejected branches               |
|    [x] .planning/ROADMAP.md              <- phase breakdown                  |
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
|  -> Run /fire-1c-setup to install tooling and finalize initialization         |
|                                                                              |
+==============================================================================+
```

---

## Error Handling

### Missing Prerequisites
```
╔══════════════════════════════════════════════════════════════════════════════╗
║ ✗ ERROR: Run /fire-1a-new first                                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Missing: .planning/PROJECT.md or .planning/REQUIREMENTS.md                  ║
║  These are created by /fire-1a-new. Run that command first.                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## References

- **Agent:** `@agents/fire-project-researcher.md`
- **Agent:** `@agents/fire-vision-architect.md`
- **Agent:** `@agents/fire-roadmapper.md`
- **Skill:** `@skills-library/_general/methodology/STACK_COMPATIBILITY_MATRIX.md`
