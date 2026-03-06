# Stone & Scaffold — Handoff Archival with Dormant Project Protection

## The Problem

Handoff files accumulate at ~2/day. Within 2 months, `warrior-handoffs/` has 100+ files. Most are scaffolding — they built the skills (stones) and now just add weight. But some are the ONLY bridge back to a dormant project the user hasn't touched in months. Blindly archiving kills the cold-start path.

### Why It Was Hard

- No distinction between "scaffolding from active work" and "last known state of a sleeping project"
- Archiving by date alone misses project context — a 60-day-old handoff might be the ONLY handoff for a project
- No index means archived handoffs are effectively invisible
- Deleting is irreversible; moving without an index is almost as bad

### Impact

- 100+ files in warrior-handoffs/ slows agent orientation at session start
- Dormant projects lose their resume bridge if archived carelessly
- No way to distinguish "this handoff built a skill" from "this handoff IS the skill for this project"

---

## The Solution

### The Principle

> Skills are the permanent stones. Handoffs are the scaffolding that built them.
> Once the stones are set, move the scaffolding out of the way — don't destroy it,
> just put it where it won't clutter the workspace.

### The Exception: Dormant Project Shield

> **Last In From Project = First One Out At Resume.**
>
> For any project that hasn't been touched in 30+ days, the MOST RECENT handoff
> stays in `warrior-handoffs/`. It's not scaffolding — it's the cold-start bridge.
> When the user opens that project 6 months later, the agent reads this handoff
> and knows exactly where things stand.

### Frequency

| Trigger | Action |
|---------|--------|
| `warrior-handoffs/` > 50 files | Run Stone & Scaffold |
| Milestone completion | Archive that milestone's handoffs |
| Monthly (natural rhythm) | Sweep for scaffolding |
| `/fire-cleanse --poop` or `--shower` | Include as part of Colon batch dump |

### The Process

```
Step 1: INVENTORY
  List all files in warrior-handoffs/
  Group by project (parse filename or read first 5 lines)

Step 2: IDENTIFY DORMANT PROJECTS
  For each project group:
    - Last handoff date > 30 days ago? → DORMANT
    - Last handoff date < 30 days ago? → ACTIVE

Step 3: PROTECT DORMANT PROJECT BRIDGES
  For each DORMANT project:
    - Mark the MOST RECENT handoff as PROTECTED (do not archive)
    - All older handoffs for that project → archive candidates

Step 4: ARCHIVE ACTIVE PROJECT SCAFFOLDING
  For each ACTIVE project:
    - Skills already extracted? (check skills library for matching patterns)
    - Keep the MOST RECENT handoff (current session bridge)
    - All older handoffs → archive candidates

Step 5: WRITE INDEX
  Create INDEX.md in backup location:
    - First line: backup location path
    - One line per archived handoff (filename + one sentence)
    - Last line: recovery instructions
    - Group by date or project for scanability

Step 6: MOVE (NOT DELETE)
  Move archive candidates to backup location
  Verify file counts match expectations
  Leave protected handoffs in warrior-handoffs/
```

### Decision Matrix

```
┌──────────────────────────────────────────────────────────────┐
│              STONE & SCAFFOLD DECISION                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Is this the MOST RECENT handoff for its project?            │
│    YES → Is the project ACTIVE (touched < 30 days)?          │
│           YES → KEEP (current session bridge)                │
│           NO  → KEEP + MARK AS DORMANT BRIDGE                │
│    NO  → Have skills been extracted from this handoff?       │
│           YES → ARCHIVE (scaffolding, stones already set)    │
│           NO  → KEEP until skills extracted                  │
│                                                              │
│  Is this a non-markdown file (image, html)?                  │
│    YES → ARCHIVE (unless referenced by a kept handoff)       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Backup Location

```
C:\Users\FirstName\Documents\warrior-handoff-backup\
  INDEX.md          ← One-page summary of everything archived
  {handoff files}   ← Moved here, intact, recoverable
```

### INDEX.md Format

```markdown
# Warrior Handoff Backup

**Location:** C:\Users\FirstName\Documents\warrior-handoff-backup\
**Moved from:** C:\Users\FirstName\.claude\warrior-handoffs\
**Date moved:** {YYYY-MM-DD}
**Reason:** Scaffolding archived — skills extracted, stones set.

---

## {Date Group}
- FILENAME.md — One sentence about what this handoff covers

---

**Recovery:** Copy needed files back to C:\Users\FirstName\.claude\warrior-handoffs\
```

---

## Integration with Cleansing Cycle

Stone & Scaffold is the **Colon's handoff-specific batch dump**:

| Cleansing Mode | Stone & Scaffold Role |
|----------------|----------------------|
| Pee | Not triggered (too light for file moves) |
| Poop | Run Step 1-6 as part of Colon batch dump |
| Shower | Full sweep — re-evaluate ALL handoffs including dormant bridges |

The Spleen fitness test applies to handoffs too:
- 4/4 (recent + referenced + project active + skills not yet extracted) → KEEP
- 3/4 → KEEP (probably the dormant bridge)
- 2/4 → Archive candidate
- 0-1/4 → Archive immediately

---

## Example: The Dec 2025 Archive

First real execution (2026-02-17):
- **33 files archived** (26 .md + 3 images + 1 HTML + INDEX.md)
- **Projects covered:** SSD Recovery (complete), WSL Crisis (resolved), Form 656 (skills extracted), Zadok Calendar (dormant — but had no 2026 handoffs to protect)
- **Dormant bridges kept:** BoltBudget and LMS handoffs from Jan 2026 stayed in warrior-handoffs/ (most recent for those projects)
- **Result:** warrior-handoffs/ went from 122 → 89 files

---

## Testing

```markdown
- [ ] Dormant projects have their most recent handoff PROTECTED
- [ ] Active projects keep only the most recent handoff
- [ ] INDEX.md has one line per archived file
- [ ] INDEX.md first line = backup location, last line = recovery instructions
- [ ] No files deleted — only moved
- [ ] File counts match (archived + remaining = original total)
- [ ] Non-markdown files archived (unless referenced by kept handoff)
```

---

## Prevention

- Never archive the ONLY handoff for a project — that's the dormant bridge
- Never delete handoffs — always move to backup with an index
- Don't archive handoffs whose skills haven't been extracted yet
- Run the dormant project check BEFORE any archival
- When resuming a dormant project, the agent reads the bridge handoff FGTAT

---

## Common Mistakes to Avoid

- **Archiving by date alone** — a 6-month-old handoff might be the only bridge to a sleeping project
- **Deleting instead of moving** — the colon absorbs before it eliminates; the backup is the absorption
- **No index** — archived handoffs without an index are effectively lost
- **Archiving too early** — if skills haven't been extracted yet, the handoff IS the skill
- **Forgetting non-markdown files** — images and HTML referenced by handoffs should travel with them

---

## Related Patterns

- [CLEANSING_CYCLE](./CLEANSING_CYCLE.md) — Colon batch dump triggers this protocol
- [PORTAL_MEMORY_ARCHITECTURE](./PORTAL_MEMORY_ARCHITECTURE.md) — Revisitation Ladder: 1x=handoff, 5x+=skill
- [GLOMERULUS_DECISION_GATE](./GLOMERULUS_DECISION_GATE.md) — 3-layer filter applies to handoff triage

---

## Resources

- Revisitation Ladder: Handoffs are 1x use (read, extract, archive). Skills are 5x+ (permanent stones).
- Thierry's insight: "The skills are what truly matter — that's what the handoffs built."
- Thierry's insight: "Last in from project, first one out at resume" — dormant bridge principle.
- Biological analog: Colon absorbs nutrients (skills) from food (handoffs), then eliminates the bulk.

---

## Time to Implement

**2-5 minutes** per archival sweep

## Difficulty Level

⭐⭐ (2/5) — Simple file operations. The nuance is in the dormant project detection.
