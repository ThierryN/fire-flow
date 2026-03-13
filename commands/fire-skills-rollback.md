---
name: power-skills-rollback
description: Rollback a skill to a previous version
arguments:
  - name: skill
    description: Skill identifier in format category/skill-name
    required: true
    type: string
  - name: version
    description: Target version to rollback to (e.g., 1.2.0 or commit hash)
    required: true
    type: string
triggers:
  - "rollback skill"
  - "revert skill"
  - "restore skill version"
---

# /fire-skills-rollback - Rollback Skill to Previous Version

Restore a skill to a previous version from the git-backed skills library.

## Purpose

- Revert problematic changes to a skill
- Restore a preferred earlier version
- Undo accidental modifications
- Recover from sync conflicts
- Test against older skill patterns

## Prerequisites

The skills library must be git-versioned:
- `~/.claude/plugins/dominion-flow/skills-library/.git/`

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `skill` | Yes | Skill path: `{category}/{skill-name}` |
| `version` | Yes | Target version: semantic version (e.g., `1.2.0`) or commit hash |

## Usage Examples

```bash
# Rollback to specific version
/fire-skills-rollback database-solutions/n-plus-1 1.2.0

# Rollback using commit hash
/fire-skills-rollback security/jwt-auth abc1234

# Rollback with confirmation skip
/fire-skills-rollback api-patterns/pagination 2.0.0 --yes

# Rollback in global library
/fire-skills-rollback performance/caching 1.0.0 --global

# Preview rollback without applying
/fire-skills-rollback testing/snapshot 1.1.0 --dry-run
```

## Process

<step number="1">
### Validate Arguments

Verify skill and version exist:

```bash
# Check skill exists
ls ~/.claude/plugins/dominion-flow/skills-library/{category}/{skill-name}.md

# Find version in git history
cd ~/.claude/plugins/dominion-flow/skills-library
git log --oneline -- {category}/{skill-name}.md | grep -i "v{version}"
```

If version not found, search by semantic version in frontmatter:
```bash
# Search commits for version tag
for commit in $(git log --format=%H -- {category}/{skill-name}.md); do
  version_line=$(git show $commit:{category}/{skill-name}.md 2>/dev/null | grep "^version:")
  if [[ "$version_line" == *"{target-version}"* ]]; then
    echo "Found: $commit"
    break
  fi
done
```

Error if not found:
```
Error: Version {version} not found for skill {category}/{skill-name}

Available versions:
  v2.1.0 (2026-01-22) - abc1234
  v2.0.0 (2026-01-15) - def5678
  v1.2.0 (2026-01-08) - ghi9012
  v1.1.0 (2025-12-20) - jkl3456
  v1.0.0 (2025-12-15) - mno7890

Usage: /fire-skills-rollback {skill} {version}
```
</step>

<step number="2">
### Show Comparison

Display current vs target version:

```
=============================================================
              SKILL ROLLBACK PREVIEW
=============================================================

Skill:    {category}/{skill-name}
Current:  v{current-version} ({current-date})
Target:   v{target-version} ({target-date})

-------------------------------------------------------------
CURRENT VERSION (v{current-version})
-------------------------------------------------------------

{First 50 lines of current skill content}
...

-------------------------------------------------------------
TARGET VERSION (v{target-version})
-------------------------------------------------------------

{First 50 lines of target skill content}
...

-------------------------------------------------------------
CHANGES TO BE REVERTED
-------------------------------------------------------------

The following changes will be undone:

Version History (newest to oldest):

  v{current} -> v{intermediate-1}
  ├─ {change description 1}
  ├─ {change description 2}
  └─ {change description 3}

  v{intermediate-1} -> v{intermediate-2}
  ├─ {change description 4}
  └─ {change description 5}

  v{intermediate-2} -> v{target}
  └─ (target version)

Total changes to revert: {N} commits

-------------------------------------------------------------
DIFF SUMMARY
-------------------------------------------------------------

  {category}/{skill-name}.md

  Lines added (to be removed):   +{X}
  Lines removed (to be restored): -{Y}
  Net change:                     {Z} lines

-------------------------------------------------------------
WARNING
-------------------------------------------------------------

This rollback will:
  - Restore skill to version v{target-version}
  - Remove all changes made after {target-date}
  - Create a new commit documenting the rollback
  - NOT affect the global library (sync separately)

Recent usage of this skill:
  - Applied {N} times since v{target-version}
  - Last used: {date} in Phase {X}

Consider: Are newer patterns still needed in your codebase?

-------------------------------------------------------------
CONFIRMATION
-------------------------------------------------------------

Proceed with rollback?

[Y] Yes, rollback to v{target-version}
[N] No, cancel
[D] Show full diff
[V] View target version content

> _

=============================================================
```
</step>

<step number="3">
### Execute Rollback

Upon confirmation:

```bash
cd ~/.claude/plugins/dominion-flow/skills-library

# Checkout the target version
git show {commit-hash}:{category}/{skill-name}.md > {category}/{skill-name}.md

# Update frontmatter with rollback note
# Add to changelog:
#   - "{date}: Rolled back to v{target} from v{current}"

# Stage changes
git add {category}/{skill-name}.md

# Commit rollback
git commit -m "rollback({category}): revert {skill-name} to v{target-version}

Reverted from v{current-version} to v{target-version}
Reason: User-initiated rollback via /fire-skills-rollback

Changes reverted:
- {list of reverted changes}
"
```
</step>

<step number="4">
### Update SKILLS-INDEX.md

Update the index with rollback information:

```markdown
## Rollback History

| Date | Skill | From | To | Reason |
|------|-------|------|-----|--------|
| 2026-01-22 | database-solutions/n-plus-1 | v2.1.0 | v1.2.0 | User rollback |
```
</step>

<step number="5">
### Confirmation

```
=============================================================
              ROLLBACK COMPLETE
=============================================================

Skill:      {category}/{skill-name}
Previous:   v{current-version}
Restored:   v{target-version}
Commit:     {new-commit-hash}

-------------------------------------------------------------
DETAILS
-------------------------------------------------------------

Changes reverted:
  - {change 1 that was undone}
  - {change 2 that was undone}
  - {change 3 that was undone}

Skill file updated:
  ~/.claude/plugins/dominion-flow/skills-library/{category}/{skill-name}.md

SKILLS-INDEX.md updated:
  - Rollback recorded in history

-------------------------------------------------------------
NEXT STEPS
-------------------------------------------------------------

1. Verify the restored skill:
   /fire-search --detail {category}/{skill-name}

2. Update references in current plans:
   Check if any BLUEPRINT.md references this skill

3. Sync to global library (optional):
   /fire-skills-sync --push --skill {category}/{skill-name}

4. If you need to undo this rollback:
   /fire-skills-rollback {category}/{skill-name} {current-version}

-------------------------------------------------------------
IMPORTANT NOTES
-------------------------------------------------------------

- The global library still has v{current-version}
- Other projects using this skill are not affected
- To propagate this rollback, run /fire-skills-sync --push

=============================================================
```
</step>

## Options

| Option | Description |
|--------|-------------|
| `--yes` / `-y` | Skip confirmation prompt |
| `--dry-run` | Preview changes without applying |
| `--global` | Rollback in global library instead |
| `--reason "{text}"` | Add reason to rollback commit message |
| `--no-commit` | Make changes but don't commit |
| `--preserve-newer` | Keep newer additions while reverting core changes |

## Rollback Strategies

### Strategy 1: Full Rollback (Default)
Completely replaces current version with target version.

```bash
/fire-skills-rollback database-solutions/n-plus-1 1.2.0
```

### Strategy 2: Selective Rollback
Keep certain sections from current version.

```bash
/fire-skills-rollback database-solutions/n-plus-1 1.2.0 --preserve-newer
```

This prompts for which sections to keep:
```
Which sections should keep newer content?

[ ] Problem description
[ ] Solution pattern
[x] Code examples (keep v2.1.0 Prisma examples)
[ ] When to use
[ ] When NOT to use
[x] References (keep newer links)

Proceed with selective rollback? [Y/n]
```

### Strategy 3: Create Branch Version
Instead of replacing, create a variant skill.

```bash
/fire-skills-rollback database-solutions/n-plus-1 1.2.0 --branch classic
```

Creates: `database-solutions/n-plus-1-classic.md` with v1.2.0 content

## Recovery from Rollback

If you need to undo a rollback:

```bash
# Option 1: Rollback to the version before rollback
/fire-skills-rollback {skill} {previous-current-version}

# Option 2: Pull from global (if global has newer)
/fire-skills-sync --pull --skill {skill}

# Option 3: Git reset (advanced)
cd ~/.claude/plugins/dominion-flow/skills-library
git revert HEAD  # Reverts the rollback commit
```

## Safety Features

1. **Confirmation Required**: Always shows preview before rollback
2. **Git Backup**: Original version preserved in git history
3. **Rollback Tracking**: All rollbacks logged in SKILLS-INDEX.md
4. **No Global Impact**: Project rollback doesn't affect global library
5. **Dry Run**: Preview changes with `--dry-run`

## Error Handling

**Skill not found:**
```
Error: Skill not found: {skill}
Available skills in {category}/:
  - skill-1
  - skill-2
```

**Version not found:**
```
Error: Version {version} not found
Available versions: v2.1.0, v2.0.0, v1.2.0, v1.1.0, v1.0.0
```

**Git not initialized:**
```
Error: Skills library is not git-versioned
Initialize with: cd ~/.claude/plugins/dominion-flow/skills-library && git init
```

**Uncommitted changes:**
```
Error: Skills library has uncommitted changes
Commit or stash changes before rollback:
  git add . && git commit -m "WIP"
  OR
  git stash
```

## Related Commands

- `/fire-skills-history` - View version history
- `/fire-skills-diff` - Compare versions before rollback
- `/fire-search --detail` - View current skill content
- `/fire-skills-sync` - Sync rollback to global library
