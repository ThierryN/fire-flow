---
name: power-skills-sync
description: Synchronize skills between project library and global library
arguments:
  - name: direction
    description: Sync direction (push, pull, both, dry-run)
    required: false
    type: string
    default: "both"
triggers:
  - "sync skills"
  - "push skills"
  - "pull skills"
  - "share skills"
---

# /fire-skills-sync - Sync Local/Global Skills

Synchronize skills between the project skills library and the global skills library.

## Purpose

- Share proven patterns across all your projects
- Pull skills discovered in other projects
- Maintain a central knowledge base
- Resolve skill version conflicts
- Keep skills up-to-date everywhere

## Library Locations

| Library | Path | Purpose |
|---------|------|---------|
| **Project** | `~/.claude/plugins/dominion-flow/skills-library/` | Plugin-bundled skills |
| **Global** | `~/.claude/fire-skills-global/` | User's personal skills across all projects |

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `direction` | No | `both` | Sync direction: `--push`, `--pull`, `--both`, `--dry-run` |

## Usage Examples

```bash
# Bidirectional sync (default)
/fire-skills-sync

# Push project skills to global library
/fire-skills-sync --push

# Pull global skills to project
/fire-skills-sync --pull

# Preview changes without applying
/fire-skills-sync --dry-run

# Force sync (overwrite conflicts with source)
/fire-skills-sync --push --force

# Sync specific category only
/fire-skills-sync --category database-solutions
```

## Process

<step number="1">
### Initialize Global Library

If global library doesn't exist, create it:

```bash
mkdir -p ~/.claude/fire-skills-global
```

Create structure matching project library:
```
~/.claude/fire-skills-global/
├── GLOBAL-INDEX.md           # Master index
├── database-solutions/
├── api-patterns/
├── security/
├── performance/
├── frontend/
├── testing/
├── infrastructure/
├── form-solutions/
├── ecommerce/
├── video-media/
├── document-processing/
├── integrations/
├── automation/
├── patterns-standards/
└── methodology/
```

Initialize git for versioning:
```bash
cd ~/.claude/fire-skills-global
git init
git add .
git commit -m "Initialize global skills library"
```
</step>

<step number="2">
### Compare Libraries

Scan both libraries and categorize skills:

**Comparison Algorithm:**
```
For each skill in project library:
  - Check if exists in global library
  - If exists: Compare versions and last_updated dates
  - If not exists: Mark as "new in project"

For each skill in global library:
  - Check if exists in project library
  - If not exists: Mark as "available from global"
```

**Comparison Categories:**
1. **New in Project** - Skills only in project (can push)
2. **Available from Global** - Skills only in global (can pull)
3. **Identical** - Same version in both (no action)
4. **Project Newer** - Project has newer version (suggest push)
5. **Global Newer** - Global has newer version (suggest pull)
6. **Conflict** - Both modified since last sync (manual resolution)
</step>

<step number="3">
### Display Sync Report

```
=============================================================
                    SKILLS SYNC REPORT
=============================================================

Project Library: ~/.claude/plugins/dominion-flow/skills-library/
Global Library:  ~/.claude/fire-skills-global/

-------------------------------------------------------------
SUMMARY
-------------------------------------------------------------

Total Skills in Project:  {N}
Total Skills in Global:   {M}
Already Synchronized:     {X}

-------------------------------------------------------------
PUSH TO GLOBAL ({count} skills)
-------------------------------------------------------------

New skills from project -> global:

  + database-solutions/connection-pool-timeout.md
    Contributed: 2026-01-22 | Tags: postgresql, prisma
    Problem: Connection pool exhaustion under load

  + api-patterns/retry-with-backoff.md
    Contributed: 2026-01-20 | Tags: api, resilience
    Problem: Transient API failures causing cascading errors

  + security/jwt-refresh-rotation.md
    Contributed: 2026-01-18 | Tags: jwt, auth, security
    Problem: JWT refresh token reuse vulnerabilities

Updated skills (project newer):

  ~ database-solutions/n-plus-1.md
    Project: v2.1.0 (2026-01-22)
    Global:  v2.0.0 (2026-01-15)
    Changes: Added Prisma-specific examples

-------------------------------------------------------------
PULL FROM GLOBAL ({count} skills)
-------------------------------------------------------------

Available skills from global -> project:

  + performance/image-lazy-loading.md
    Contributed: 2026-01-19 | Source: book-writer-app
    Problem: Large images blocking page load

  + frontend/react-memo-patterns.md
    Contributed: 2026-01-17 | Source: ecommerce-platform
    Problem: Unnecessary re-renders in React components

  + testing/snapshot-testing.md
    Contributed: 2026-01-14 | Source: component-library
    Problem: UI regression detection

Updated skills (global newer):

  ~ infrastructure/docker-multi-stage.md
    Global:  v1.2.0 (2026-01-21)
    Project: v1.1.0 (2026-01-10)
    Changes: Added ARM64 build support

-------------------------------------------------------------
CONFLICTS ({count} skills)
-------------------------------------------------------------

Both libraries modified since last sync:

  ! security/input-validation.md
    Project: v2.0.0 (2026-01-22) - Added Zod examples
    Global:  v2.0.0 (2026-01-20) - Added Yup examples

    Resolution options:
    [P] Use project version
    [G] Use global version
    [M] Manual merge
    [S] Skip (resolve later)

    Select (P/G/M/S): > _

-------------------------------------------------------------
ACTIONS
-------------------------------------------------------------

Proceed with sync?

Direction: {push|pull|both}
Skills to push:   {N}
Skills to pull:   {M}
Conflicts:        {X} (must resolve first)

[Y] Yes, proceed
[N] No, cancel
[R] Review changes in detail
[C] Resolve conflicts first

> _

=============================================================
```
</step>

<step number="4">
### Handle Conflicts

For each conflict, offer resolution options:

**Option P - Use Project Version:**
```bash
cp project/skills-library/{skill}.md global/fire-skills-global/{skill}.md
```

**Option G - Use Global Version:**
```bash
cp global/fire-skills-global/{skill}.md project/skills-library/{skill}.md
```

**Option M - Manual Merge:**
```
-------------------------------------------------------------
MANUAL MERGE: security/input-validation.md
-------------------------------------------------------------

PROJECT VERSION (v2.0.0 - 2026-01-22):
```markdown
## Code Example

// Using Zod for validation
import { z } from 'zod';

const userSchema = z.object({
  email: z.string().email(),
  age: z.number().min(18)
});
```

GLOBAL VERSION (v2.0.0 - 2026-01-20):
```markdown
## Code Example

// Using Yup for validation
import * as yup from 'yup';

const userSchema = yup.object({
  email: yup.string().email().required(),
  age: yup.number().min(18).required()
});
```

-------------------------------------------------------------

Merge strategy:
[1] Keep both examples (append)
[2] Create project-specific variant
[3] Edit manually now
[4] Skip for later

> _
```

**Option S - Skip:**
Mark conflict as unresolved, continue with other syncs.
</step>

<step number="5">
### Execute Sync

Based on direction:

**Push (project -> global):**
```bash
# For each new/updated skill
cp ~/.claude/plugins/dominion-flow/skills-library/{category}/{skill}.md \
   ~/.claude/fire-skills-global/{category}/{skill}.md

# Update global index
# Merge entries into GLOBAL-INDEX.md

# Git commit
cd ~/.claude/fire-skills-global
git add .
git commit -m "sync: Push {N} skills from {project-name}"
```

**Pull (global -> project):**
```bash
# For each new/updated skill
cp ~/.claude/fire-skills-global/{category}/{skill}.md \
   ~/.claude/plugins/dominion-flow/skills-library/{category}/{skill}.md

# Update project index
# Merge entries into SKILLS-INDEX.md

# Git commit if skills-library is versioned
cd ~/.claude/plugins/dominion-flow/skills-library
git add .
git commit -m "sync: Pull {N} skills from global library"
```

**Both (bidirectional):**
Execute push first, then pull, handling conflicts along the way.
</step>

<step number="6">
### Update Indexes

Update both index files with sync metadata:

**SKILLS-INDEX.md additions:**
```markdown
## Sync History

| Date | Direction | Skills | Source/Destination |
|------|-----------|--------|-------------------|
| 2026-01-22 | pull | 3 | global library |
| 2026-01-20 | push | 2 | global library |
| 2026-01-18 | both | 5 | global library |
```

**GLOBAL-INDEX.md additions:**
```markdown
## Contributing Projects

| Project | Skills Contributed | Last Sync |
|---------|-------------------|-----------|
| my-project | 12 | 2026-01-22 |
| book-writer-app | 8 | 2026-01-20 |
| ecommerce-platform | 15 | 2026-01-18 |
```
</step>

<step number="7">
### Confirmation

```
=============================================================
                    SYNC COMPLETE
=============================================================

Direction: {direction}
Duration:  {time}

-------------------------------------------------------------
RESULTS
-------------------------------------------------------------

Pushed to Global:
  - {skill-1} (new)
  - {skill-2} (updated v2.0.0 -> v2.1.0)
  - {skill-3} (new)

Pulled from Global:
  - {skill-4} (new)
  - {skill-5} (updated v1.1.0 -> v1.2.0)

Conflicts Resolved:
  - {skill-6} (used project version)

Skipped:
  - {skill-7} (conflict unresolved)

-------------------------------------------------------------
LIBRARY STATUS
-------------------------------------------------------------

Project Library: {N} skills
Global Library:  {M} skills
Synchronized:    {X} skills

-------------------------------------------------------------
NEXT STEPS
-------------------------------------------------------------

1. Resolve remaining conflicts:
   /fire-skills-sync --resolve-conflicts

2. View sync history:
   /fire-skills-history --sync-log

3. Search newly available skills:
   /fire-search "category:performance"

=============================================================
```
</step>

## Options

| Option | Description |
|--------|-------------|
| `--push` | Push project skills to global only |
| `--pull` | Pull global skills to project only |
| `--both` | Bidirectional sync (default) |
| `--dry-run` | Preview changes without applying |
| `--force` | Overwrite conflicts with source version |
| `--category {name}` | Sync specific category only |
| `--skill {name}` | Sync specific skill only |
| `--resolve-conflicts` | Interactive conflict resolution |
| `--auto-resolve newest` | Auto-resolve using newer version |
| `--auto-resolve project` | Auto-resolve using project version |
| `--auto-resolve global` | Auto-resolve using global version |

## Conflict Resolution Strategies

| Strategy | When to Use |
|----------|-------------|
| **Newest wins** | When changes are additive/improvements |
| **Project wins** | When project has specific customizations |
| **Global wins** | When global has community-validated updates |
| **Manual merge** | When both versions have unique value |
| **Create variant** | When approaches differ by context |

## Automation

Set up automatic sync on session end:

```json
// In hooks/hooks.json
{
  "event": "SessionEnd",
  "hooks": [{
    "type": "command",
    "command": "/fire-skills-sync --push --auto-resolve newest"
  }]
}
```

## Related Commands

- `/fire-search` - Search skills in current library
- `/fire-contribute` - Add new skill
- `/fire-skills-history` - View version history
- `/fire-skills-diff` - Compare skill versions
