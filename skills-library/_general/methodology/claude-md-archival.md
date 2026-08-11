---
name: claude-md-archival
category: methodology
version: 4.0.0
contributed: 2026-03-03
contributor: global
last_updated: 2026-03-04
tags: [claude-md, context-management, archival, history, fast-start, lazy-loading, housekeeping]
difficulty: easy
scope: general
---

# CLAUDE.md Archival Flow

## Core Concept: Lazy-Loaded Context

CLAUDE.md is a **fast-start index**. It keeps headings and bullet titles for orientation, but replaces full content with **file links** pointing to topic-scoped history files. Claude reads only the file relevant to the current problem — not everything at once.

```
CLAUDE.md
  ## Database Issues
  - Connection pooling fix → history/database.md
  - Migration guide       → history/database.md

  ## Resolved Bugs
  - PayPal webhook 401    → history/debugging.md
  - JWT refresh loop      → history/debugging.md

history/
  phases/
    phase-1-auth/        ← phase plan, notes, screenshots
    phase-2-payments/    ← phase plan, notes, screenshots
  screenshots/           ← general/unphased screenshots
  database.md            ← DB fixes, schema changes, migrations
  debugging.md           ← Resolved bug investigations
  config.md              ← Old/superseded configuration
```

Session start: Claude reads CLAUDE.md (tiny, fast).
Mid-conversation: Claude reads only the specific history file it needs.

## Directory Structure

```
{project-root}/
  CLAUDE.md                          ← Index only. Headings + links. Fast to load.
  history/
    │
    ├── phases/                      ← One subfolder per completed phase
    │   ├── phase-1-{name}/
    │   │   ├── PLAN.md              ← Phase plan moved from root on completion
    │   │   ├── notes.md             ← Phase-specific notes and decisions
    │   │   └── screenshots/         ← UI screenshots captured during this phase
    │   │       ├── login-ui.png
    │   │       └── dashboard-v1.png
    │   ├── phase-2-{name}/
    │   │   ├── PLAN.md
    │   │   └── screenshots/
    │   └── ...
    │
    ├── screenshots/                 ← General screenshots (bug captures, UI reviews)
    │   └── {YYYY-MM-DD}-{label}.png
    │
    ├── database.md                  ← DB: schema changes, migrations, fixes
    ├── debugging.md                 ← Resolved bug investigations
    ├── config.md                    ← Superseded configuration, old ports/keys
    └── integrations.md              ← Third-party history (Stripe, Zoom, etc.)
```

Folders and files are created on demand — only when first archiving into them.

## Link Format in CLAUDE.md

Keep the bullet point title in CLAUDE.md. Replace the content with a filepath:

```markdown
## Database

- **Connection pooling fix** → `history/database.md`
- **RLS policy for enrollments** → `history/database.md`
- **PG-to-MySQL translation layer** → `history/database.md`

## Resolved Bugs

- **PayPal webhook returning 401** → `history/debugging.md`
- **JWT refresh loop on tab focus** → `history/debugging.md`

## Completed Phases

- **Phase 1: Auth + Enrollment** → `history/phases.md`
- **Phase 2: Stripe Payments** → `history/phases.md`
```

The title stays visible in CLAUDE.md so Claude knows what exists. The content lives in the history file. Claude follows the link only when investigating that specific topic.

## Content Classification

### NEVER ARCHIVE — Always Full Content in CLAUDE.md

No matter how large the file: keep these in full, inline, always:

- Active credentials, ports, connection strings
- Rules tagged `NEVER` / `ALWAYS` / `CRITICAL` / `IMPORTANT`
- Current blocking bugs (unresolved)
- Active phase/milestone (what is being built right now)
- Architectural constraints that affect every PR
- The history file index (see below)

### ARCHIVE WITH LINK — Move Content, Keep Title

Content that is resolved, completed, or no longer needed at session init:

- Completed phase notes and summaries
- Resolved bug write-ups and root cause analyses
- Superseded configuration (old ports, old DB names, old env vars)
- Migration history and schema change logs
- Debug sessions that reached a conclusion
- Integration setup notes (once working, rarely referenced)
- Decisions that are stable — no longer need daily reinforcement

### JUDGMENT CALL

- Architectural patterns still being actively applied → keep inline
- "Lessons learned" that prevent recurring mistakes → keep if the pattern still bites you; archive once it's internalized
- Feature notes → keep if in active development, archive once shipped

## History File Format

Each history file uses dated entries, appended at the top (newest first):

```markdown
# {Topic} History
<!-- newest entries at top -->

---
## {YYYY-MM-DD} — {Short Title}
**Reason:** {phase-complete | bug-resolved | config-change | manual}

{Full content here — as detailed as needed}

---
## {YYYY-MM-DD} — {Earlier Entry}
...
```

Rules:
- **APPEND-ONLY** — never delete previous entries
- **Newest at top** — most recent context found first
- **One topic per file** — keeps files small and relevant
- **Preserve headings** — makes files grep-able

## When to Trigger

1. **Session start feels slow** — CLAUDE.md has grown with resolved/stale content
2. **Phase or milestone completes** — archive that phase's notes
3. **Bug resolved** — move the investigation to `history/debugging.md`
4. **IDE lag** — the file is slowing down tooling (VS Code, etc.)
5. **Manual request** — "archive claude.md", "clean up claude.md"

Do NOT trigger on line count alone. Trigger on content type: is this still needed at session init?

## Implementation Steps

### Step 1: Create history directory (first time only)

```bash
mkdir -p {project-root}/history
```

### Step 2: Classify content

Read CLAUDE.md. For each section:
- NEVER ARCHIVE → leave as-is
- ARCHIVE WITH LINK → identify target history file (`database.md`, `debugging.md`, etc.)
- JUDGMENT CALL → decide based on current active use

### Step 3: Write to topic history file

Append (or create) the relevant `history/{topic}.md` file with a dated entry containing the full content.

### Step 4: Replace content with link in CLAUDE.md

Keep the bullet/heading title. Replace the body with `→ history/{topic}.md`.

### Step 5: Verify

- NEVER ARCHIVE content is still inline in CLAUDE.md
- Each archived item has a title + link in CLAUDE.md
- History files contain the full content with dated headers
- Session start is faster

## Housekeeping: Phase Completion Folder Move

When a phase completes, run the full housekeeping sequence — not just CLAUDE.md archival.

### Step 1: Create the phase subfolder

```bash
mkdir -p history/phases/phase-{N}-{short-name}/screenshots
```

Example: `history/phases/phase-2-payments/screenshots/`

### Step 2: Move phase plan files

Any phase plan, PRD, or roadmap file sitting in the project root gets moved in:

```bash
mv PLAN.md         history/phases/phase-{N}-{name}/PLAN.md
mv ROADMAP.md      history/phases/phase-{N}-{name}/ROADMAP.md
mv PRD.md          history/phases/phase-{N}-{name}/PRD.md
mv STATE.md        history/phases/phase-{N}-{name}/STATE.md
# move any other phase-specific docs found in root
```

Only move files that belong to the completed phase. Leave active docs in root.

### Step 3: Move phase screenshots

Screenshots taken during this phase (UI reviews, before/after comparisons, bug captures related to this phase) move into the phase subfolder:

```bash
mv screenshots/phase-{N}-*.png   history/phases/phase-{N}-{name}/screenshots/
mv screenshots/{YYYY-MM-DD}-*.png history/phases/phase-{N}-{name}/screenshots/
# or move by date range matching the phase
```

General/unphased screenshots (UI audits, ad-hoc captures) stay in `history/screenshots/`.

### Step 4: Update CLAUDE.md index

Add a link entry for the completed phase:

```markdown
## Completed Phases

- **Phase 1 — Auth & Enrollment** → `history/phases/phase-1-auth/`
- **Phase 2 — Stripe Payments**   → `history/phases/phase-2-payments/`
```

### Step 5: Archive phase CLAUDE.md notes

Move the inline phase notes from CLAUDE.md into `history/phases/phase-{N}-{name}/notes.md`, then replace with the link.

### Naming Convention

| Item | Format |
|------|--------|
| Phase folder | `phase-{N}-{kebab-name}` e.g. `phase-3-video-player` |
| Screenshots (phased) | `{label}.png` inside phase screenshots/ folder |
| Screenshots (general) | `{YYYY-MM-DD}-{label}.png` in `history/screenshots/` |
| Phase plan files | Original filename preserved inside phase folder |

## Integration with Existing Flows

| Flow Command | When to Archive |
|-------------|----------------|
| `/fire-5-handoff`, `/power-5-handoff` | Archive completed phase notes → `history/phases.md` |
| `/fire-complete-milestone`, `/power-complete-milestone` | Archive milestone → `history/phases.md` |
| `/fire-debug` (after resolution) | Archive debug session → `history/debugging.md` |
| `/fire-6-resume`, `/power-6-resume` | Check CLAUDE.md for stale inline content |
| `/gsd:complete-milestone` | Archive milestone → `history/phases.md` |
| `/gsd:pause-work` | Archive stale content before pause |

## When Claude Should Read a History File

- Investigating a bug → read `history/debugging.md`
- Reviewing a past architectural decision → read relevant `history/{topic}.md`
- Resuming stale work → read `history/phases.md`
- Database issue → read `history/database.md`
- Only read the file that matches the current problem

## Common Mistakes

- Removing the title from CLAUDE.md when archiving (title must stay as a link anchor)
- Archiving content tagged NEVER/CRITICAL/IMPORTANT
- Archiving active credentials or unresolved bugs
- Creating one giant `claudemdbackup.md` instead of topic-scoped files
- Overwriting history files instead of appending
- Archiving without a dated header
