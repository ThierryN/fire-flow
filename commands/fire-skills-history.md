---
name: power-skills-history
description: View version history for a skill in the skills library
arguments:
  - name: skill
    description: Skill identifier in format category/skill-name
    required: true
    type: string
triggers:
  - "skill history"
  - "skill versions"
  - "skill changelog"
---

# /fire-skills-history - View Skill Version History

View the complete version history, changelogs, and contributors for any skill.

## Purpose

- Track how a skill has evolved over time
- See who contributed improvements
- Understand why changes were made
- Find previous versions if needed
- Review skill maturity and stability

## Prerequisites

The skills library must be git-versioned:
- `~/.claude/plugins/dominion-flow/skills-library/.git/`
- `~/.claude/fire-skills-global/.git/` (for global library)

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `skill` | Yes | Skill path: `{category}/{skill-name}` |

## Usage Examples

```bash
# View history for a specific skill
/fire-skills-history database-solutions/n-plus-1

# View history with full commit details
/fire-skills-history security/jwt-auth --verbose

# View history from global library
/fire-skills-history api-patterns/pagination --global

# Show only last N versions
/fire-skills-history performance/caching --limit 5

# Export history to file
/fire-skills-history testing/snapshot --export
```

## Process

<step number="1">
### Validate Skill Exists

Check if the skill file exists:

```bash
# Check project library
ls ~/.claude/plugins/dominion-flow/skills-library/{category}/{skill-name}.md

# Check global library (if --global)
ls ~/.claude/fire-skills-global/{category}/{skill-name}.md
```

If not found:
```
Error: Skill not found: {category}/{skill-name}

Did you mean one of these?
  - {similar-skill-1}
  - {similar-skill-2}

Search for skills: /fire-search "{skill-name}"
```
</step>

<step number="2">
### Retrieve Git History

Query git log for the skill file:

```bash
cd ~/.claude/plugins/dominion-flow/skills-library

git log --follow --format="%H|%ai|%an|%s" -- {category}/{skill-name}.md
```

Parse each commit:
- **Hash**: Full commit SHA
- **Date**: Commit timestamp
- **Author**: Contributor name
- **Message**: Commit description
</step>

<step number="3">
### Extract Version Information

For each commit, extract version from frontmatter:

```bash
git show {commit-hash}:{category}/{skill-name}.md | head -20
```

Parse YAML frontmatter for:
- `version`: Semantic version (e.g., 2.1.0)
- `last_updated`: Date of this version
- `changelog`: Version-specific changes
- `contributors`: List of contributors
</step>

<step number="4">
### Display Version History

```
=============================================================
              SKILL VERSION HISTORY
=============================================================

Skill:    {category}/{skill-name}
Library:  {project|global}
Current:  v{version}
Created:  {creation-date}
Updates:  {total-commits} versions

-------------------------------------------------------------
VERSION TIMELINE
-------------------------------------------------------------

v2.1.0 (2026-01-22) - CURRENT
├─ Author: my-project
├─ Commit: abc1234
├─ Message: feat(skills): add Prisma-specific examples
└─ Changes:
   - Added Prisma eager loading examples
   - Updated TypeScript types
   - Added performance benchmarks

   Files changed: 1 (+45 -12)

-------------------------------------------------------------

v2.0.0 (2026-01-15)
├─ Author: book-writer-app
├─ Commit: def5678
├─ Message: refactor(skills): rewrite for TypeScript ORM patterns
└─ Changes:
   - Rewrote all examples for TypeScript
   - Added Sequelize support
   - Removed raw SQL examples (moved to sql-patterns skill)
   - BREAKING: Changed code examples format

   Files changed: 1 (+120 -85)

-------------------------------------------------------------

v1.2.0 (2026-01-08)
├─ Author: ecommerce-platform
├─ Commit: ghi9012
├─ Message: docs(skills): add when-not-to-use section
└─ Changes:
   - Added anti-patterns section
   - Clarified eager vs lazy loading scenarios
   - Fixed typos

   Files changed: 1 (+25 -5)

-------------------------------------------------------------

v1.1.0 (2025-12-20)
├─ Author: my-project
├─ Commit: jkl3456
├─ Message: feat(skills): add related skills references
└─ Changes:
   - Added links to related skills
   - Updated tags

   Files changed: 1 (+10 -2)

-------------------------------------------------------------

v1.0.0 (2025-12-15) - INITIAL
├─ Author: my-project
├─ Commit: mno7890
├─ Message: feat(skills): add n-plus-1 query solution
└─ Changes:
   - Initial skill creation
   - Basic problem/solution documentation
   - Raw SQL examples

   Files changed: 1 (+75 -0)

=============================================================

-------------------------------------------------------------
CONTRIBUTORS
-------------------------------------------------------------

| Contributor | Versions | First | Last |
|-------------|----------|-------|------|
| my-project | 3 | v1.0.0 | v2.1.0 |
| book-writer-app | 1 | v2.0.0 | v2.0.0 |
| ecommerce-platform | 1 | v1.2.0 | v1.2.0 |

-------------------------------------------------------------
STATISTICS
-------------------------------------------------------------

Total Versions:     5
Age:               38 days
Update Frequency:  ~7.6 days between updates
Lines Added:       +275
Lines Removed:     -104
Net Growth:        +171 lines

Stability:         STABLE (no changes in 7 days)
Maturity:          MATURE (5+ versions, 3+ contributors)

-------------------------------------------------------------
QUICK ACTIONS
-------------------------------------------------------------

[1] View specific version:
    /fire-skills-history {skill} --show v1.0.0

[2] Compare versions:
    /fire-skills-diff {skill} v1.0.0 v2.1.0

[3] Rollback to version:
    /fire-skills-rollback {skill} v2.0.0

[4] View current skill:
    /fire-search --detail {skill}

=============================================================
```
</step>

## Verbose Output

With `--verbose` flag, show full commit details:

```
-------------------------------------------------------------
VERSION DETAIL: v2.1.0
-------------------------------------------------------------

Commit:     abc1234567890abcdef1234567890abcdef12345
Author:     my-project
Date:       2026-01-22 14:32:15 -0500
Parents:    def5678901234...

Message:
  feat(skills): add Prisma-specific examples

  This update adds comprehensive Prisma examples for solving
  N+1 query problems. Includes:

  - Eager loading with `include`
  - Selective field loading
  - Nested relation handling
  - Performance comparison benchmarks

  Tested against PostgreSQL 15 and MySQL 8.

Diff:
  @@ -45,6 +45,25 @@ ## Code Example

  +### Prisma Example
  +
  +```typescript
  +// Before (N+1): 15 queries
  +const users = await prisma.user.findMany();
  +for (const user of users) {
  +  const profile = await prisma.profile.findUnique({
  +    where: { userId: user.id }
  +  });
  +}
  +
  +// After (eager): 1 query
  +const users = await prisma.user.findMany({
  +  include: { profile: true }
  +});
  +```
  +
  +**Performance:** 250ms -> 45ms (82% improvement)

-------------------------------------------------------------
```

## Options

| Option | Description |
|--------|-------------|
| `--verbose` | Show full commit details and diffs |
| `--global` | Query global library instead of project |
| `--limit {N}` | Show only last N versions |
| `--since {date}` | Show versions since date |
| `--until {date}` | Show versions until date |
| `--show {version}` | Display specific version content |
| `--export` | Export history to markdown file |
| `--json` | Output as JSON |
| `--contributors` | Show only contributor summary |
| `--stats` | Show only statistics |

## Version Comparison Commands

From the history view, you can:

1. **View specific version content:**
   ```bash
   /fire-skills-history database-solutions/n-plus-1 --show v1.0.0
   ```

2. **Compare two versions:**
   ```bash
   /fire-skills-diff database-solutions/n-plus-1 v1.0.0 v2.1.0
   ```

3. **Rollback to previous version:**
   ```bash
   /fire-skills-rollback database-solutions/n-plus-1 v2.0.0
   ```

## Export Format

With `--export`, creates a markdown file:

```markdown
# Version History: database-solutions/n-plus-1

Generated: 2026-01-22 15:00:00

## Summary

- **Current Version:** v2.1.0
- **Total Versions:** 5
- **Contributors:** 3
- **Created:** 2025-12-15
- **Last Updated:** 2026-01-22

## Changelog

### v2.1.0 (2026-01-22)
- Added Prisma-specific examples
- Updated TypeScript types
- Added performance benchmarks

### v2.0.0 (2026-01-15)
- Rewrote all examples for TypeScript
- Added Sequelize support
- BREAKING: Changed code examples format

[... continues for all versions ...]

## Contributors

| Name | Contributions |
|------|--------------|
| my-project | 3 versions |
| book-writer-app | 1 version |
| ecommerce-platform | 1 version |
```

Saved to: `.planning/skill-history-{category}-{skill-name}.md`

## Skill Maturity Indicators

| Indicator | Criteria | Meaning |
|-----------|----------|---------|
| **NEW** | <3 versions, <2 contributors | Recently added, may evolve |
| **DEVELOPING** | 3-5 versions, 2+ contributors | Actively improving |
| **MATURE** | 5+ versions, 3+ contributors | Well-established pattern |
| **STABLE** | No changes in 30+ days | Proven, unlikely to change |

## Related Commands

- `/fire-skills-diff` - Compare two versions
- `/fire-skills-rollback` - Revert to previous version
- `/fire-search --detail` - View current skill content
- `/fire-contribute` - Add new skill
