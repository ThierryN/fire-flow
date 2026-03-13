---
name: power-skills-diff
description: Compare different versions of a skill
arguments:
  - name: skill
    description: Skill identifier in format category/skill-name
    required: true
    type: string
  - name: v1
    description: First version to compare (default current)
    required: false
    type: string
  - name: v2
    description: Second version to compare (default previous)
    required: false
    type: string
triggers:
  - "compare skill versions"
  - "skill diff"
  - "skill changes"
---

# /fire-skills-diff - Compare Skill Versions

Compare two versions of a skill to see what changed between them.

## Purpose

- Understand how a skill evolved
- Review changes before rollback
- Compare project vs global versions
- Audit skill modifications
- Learn from skill improvements

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `skill` | Yes | - | Skill path: `{category}/{skill-name}` |
| `v1` | No | current | First version (base) |
| `v2` | No | previous | Second version (compare) |

## Usage Examples

```bash
# Compare current with previous version
/fire-skills-diff database-solutions/n-plus-1

# Compare two specific versions
/fire-skills-diff database-solutions/n-plus-1 1.0.0 2.0.0

# Compare current with specific version
/fire-skills-diff security/jwt-auth current 1.2.0

# Compare project vs global version
/fire-skills-diff api-patterns/pagination project global

# Side-by-side output
/fire-skills-diff performance/caching 1.0.0 2.0.0 --side-by-side

# Show only specific sections
/fire-skills-diff testing/snapshot --section "Code Example"
```

## Process

<step number="1">
### Resolve Versions

Determine which versions to compare:

**Default behavior:**
- `v1` = current (HEAD)
- `v2` = previous (HEAD~1)

**Special keywords:**
- `current` or `head` = Latest version
- `previous` or `prev` = One version before current
- `project` = Version in project library
- `global` = Version in global library
- `X.Y.Z` = Specific semantic version
- `{commit-hash}` = Specific git commit

```bash
# Resolve v1
if v1 == "current" or v1 == "head":
    v1_ref = "HEAD"
elif v1 == "project":
    v1_ref = "HEAD" (in project library)
elif v1 == "global":
    v1_ref = "HEAD" (in global library)
else:
    v1_ref = find_commit_for_version(skill, v1)

# Resolve v2 similarly
```
</step>

<step number="2">
### Retrieve Version Content

Fetch content for both versions:

```bash
cd ~/.claude/plugins/dominion-flow/skills-library

# Get v1 content
v1_content=$(git show {v1_ref}:{category}/{skill-name}.md)

# Get v2 content
v2_content=$(git show {v2_ref}:{category}/{skill-name}.md)

# For project vs global comparison
v1_content=$(cat ~/.claude/plugins/dominion-flow/skills-library/{category}/{skill-name}.md)
v2_content=$(cat ~/.claude/fire-skills-global/{category}/{skill-name}.md)
```
</step>

<step number="3">
### Generate Diff

Create detailed diff between versions:

```bash
# Unified diff
diff -u <(echo "$v1_content") <(echo "$v2_content")

# Or with git diff for better formatting
git diff {v1_ref} {v2_ref} -- {category}/{skill-name}.md
```
</step>

<step number="4">
### Display Comparison

```
=============================================================
                  SKILL VERSION COMPARISON
=============================================================

Skill:     {category}/{skill-name}
Comparing: v{v1} -> v{v2}

-------------------------------------------------------------
VERSION INFO
-------------------------------------------------------------

BASE (v{v1}):
  Date:        {v1-date}
  Commit:      {v1-commit-short}
  Author:      {v1-author}
  Message:     {v1-commit-message}

COMPARE (v{v2}):
  Date:        {v2-date}
  Commit:      {v2-commit-short}
  Author:      {v2-author}
  Message:     {v2-commit-message}

Time between versions: {days} days

-------------------------------------------------------------
SUMMARY OF CHANGES
-------------------------------------------------------------

Sections modified:
  [M] Problem          - Minor clarification
  [+] Solution Pattern - New approach added
  [M] Code Example     - Major rewrite (TypeScript migration)
  [ ] When to Use      - No changes
  [+] When NOT to Use  - New section added
  [M] References       - Links updated

Legend: [+] Added  [-] Removed  [M] Modified  [ ] Unchanged

Statistics:
  Lines added:    +{X}
  Lines removed:  -{Y}
  Net change:     {Z}

-------------------------------------------------------------
DETAILED DIFF
-------------------------------------------------------------

## Frontmatter Changes

  ---
- version: {v1}
+ version: {v2}
- last_updated: {v1-date}
+ last_updated: {v2-date}
  contributors:
    - my-project
+   - book-writer-app
  tags: [database, orm, prisma]
+ difficulty: medium
  ---

-------------------------------------------------------------

## Problem Section

  ## Problem

  When fetching related data in an ORM, naive implementations
- often result in N+1 queries - one query to fetch the parent
- records, then N additional queries to fetch related data for
- each parent.
+ often result in the N+1 query problem, where:
+
+ 1. One query fetches parent records
+ 2. N additional queries fetch related data (one per parent)
+
+ This causes severe performance degradation at scale.

-------------------------------------------------------------

## Solution Pattern Section

  ## Solution Pattern

- Use eager loading to fetch related data in a single query.
+ Use eager loading (also called "include" or "join fetch") to
+ retrieve all related data in a single database query.
+
+ **Key Principle:** Replace lazy loading with explicit includes
+ for data you know you'll need.

-------------------------------------------------------------

## Code Example Section

  ## Code Example

  ```typescript
  // Before (N+1 problem)
  const users = await prisma.user.findMany();
  for (const user of users) {
-   const posts = await prisma.post.findMany({ where: { userId: user.id } });
+   const posts = await prisma.post.findMany({
+     where: { userId: user.id }
+   });
  }

  // After (Eager loading)
  const users = await prisma.user.findMany({
-   include: { posts: true }
+   include: {
+     posts: {
+       select: {
+         id: true,
+         title: true,
+         createdAt: true
+       }
+     }
+   }
  });
  ```
+
+ **Performance Impact:**
+ - Before: 15 queries, 250ms total
+ - After: 1 query, 45ms total
+ - Improvement: 82% faster

-------------------------------------------------------------

## New Section: When NOT to Use

+ ## When NOT to Use
+
+ - When related data is rarely accessed (lazy loading preferred)
+ - When related data set is very large (use pagination instead)
+ - When memory constraints are tight (eager loading loads all data)
+ - When using NoSQL databases with different query patterns

-------------------------------------------------------------

## References Section

  ## References

- - [Prisma Docs](https://prisma.io/docs/concepts/components/prisma-client/relation-queries)
+ - [Prisma Relation Queries](https://prisma.io/docs/concepts/components/prisma-client/relation-queries)
+ - [N+1 Problem Explained](https://dev.to/n-plus-1-queries-explained)
+ - [ORM Performance Patterns](https://example.com/orm-performance)

=============================================================

-------------------------------------------------------------
QUICK ACTIONS
-------------------------------------------------------------

Based on this comparison:

[1] Rollback to v{v1}:
    /fire-skills-rollback {skill} {v1}

[2] Keep v{v2} (no action needed)

[3] Compare with another version:
    /fire-skills-diff {skill} {v1} {other}

[4] View full version history:
    /fire-skills-history {skill}

=============================================================
```
</step>

## Side-by-Side Output

With `--side-by-side` flag:

```
=============================================================
                SIDE-BY-SIDE COMPARISON
=============================================================

Skill: {category}/{skill-name}
Left:  v{v1} ({v1-date})
Right: v{v2} ({v2-date})

-------------------------------------------------------------
## Problem
-------------------------------------------------------------

v{v1}                              | v{v2}
-----------------------------------|-----------------------------------
When fetching related data in an   | When fetching related data in an
ORM, naive implementations often   | ORM, naive implementations often
result in N+1 queries - one query  | result in the N+1 query problem,
to fetch the parent records, then  | where:
N additional queries to fetch      |
related data for each parent.      | 1. One query fetches parent records
                                   | 2. N additional queries fetch
                                   |    related data (one per parent)
                                   |
                                   | This causes severe performance
                                   | degradation at scale.

-------------------------------------------------------------
## Code Example
-------------------------------------------------------------

v{v1}                              | v{v2}
-----------------------------------|-----------------------------------
// After (Eager loading)           | // After (Eager loading)
const users = await prisma.user.   | const users = await prisma.user.
  findMany({                       |   findMany({
  include: { posts: true }         |   include: {
});                                |     posts: {
                                   |       select: {
                                   |         id: true,
                                   |         title: true,
                                   |         createdAt: true
                                   |       }
                                   |     }
                                   |   }
                                   | });
                                   |
                                   | **Performance Impact:**
                                   | - Before: 15 queries, 250ms
                                   | - After: 1 query, 45ms

=============================================================
```

## Section-Specific Diff

With `--section "Code Example"`:

```
=============================================================
            SECTION DIFF: Code Example
=============================================================

Skill:     {category}/{skill-name}
Section:   Code Example
Comparing: v{v1} -> v{v2}

-------------------------------------------------------------

  ## Code Example

  ```typescript
  // Before (N+1 problem)
  const users = await prisma.user.findMany();
  for (const user of users) {
-   const posts = await prisma.post.findMany({ where: { userId: user.id } });
+   const posts = await prisma.post.findMany({
+     where: { userId: user.id }
+   });
  }

  // After (Eager loading)
  const users = await prisma.user.findMany({
-   include: { posts: true }
+   include: {
+     posts: {
+       select: {
+         id: true,
+         title: true,
+         createdAt: true
+       }
+     }
+   }
  });
  ```
+
+ **Performance Impact:**
+ - Before: 15 queries, 250ms total
+ - After: 1 query, 45ms total
+ - Improvement: 82% faster

=============================================================
```

## Options

| Option | Description |
|--------|-------------|
| `--side-by-side` | Display versions in columns |
| `--unified` | Standard unified diff (default) |
| `--section "{name}"` | Compare only specific section |
| `--stat` | Show only statistics, no content |
| `--color` | Force colored output |
| `--no-color` | Disable colored output |
| `--context {N}` | Lines of context around changes (default: 3) |
| `--ignore-whitespace` | Ignore whitespace changes |
| `--word-diff` | Show word-level changes |
| `--json` | Output as JSON |
| `--export` | Save diff to file |

## Project vs Global Comparison

Special syntax for comparing libraries:

```bash
# Compare project library version with global library version
/fire-skills-diff database-solutions/n-plus-1 project global
```

Output includes library-specific information:

```
=============================================================
           PROJECT vs GLOBAL COMPARISON
=============================================================

Skill: database-solutions/n-plus-1

PROJECT LIBRARY:
  Path:    ~/.claude/plugins/dominion-flow/skills-library/
  Version: v2.1.0
  Updated: 2026-01-22

GLOBAL LIBRARY:
  Path:    ~/.claude/fire-skills-global/
  Version: v2.0.0
  Updated: 2026-01-15

Status: PROJECT IS NEWER

-------------------------------------------------------------
RECOMMENDATION
-------------------------------------------------------------

Project has updates not in global library.
Consider syncing: /fire-skills-sync --push --skill {skill}

=============================================================
```

## Integration with Other Commands

The diff command integrates with:

1. **History viewing:**
   ```bash
   /fire-skills-history database-solutions/n-plus-1
   # Then use diff to compare specific versions
   /fire-skills-diff database-solutions/n-plus-1 1.0.0 2.0.0
   ```

2. **Before rollback:**
   ```bash
   # Review what will change
   /fire-skills-diff database-solutions/n-plus-1 2.1.0 1.2.0
   # Then rollback if satisfied
   /fire-skills-rollback database-solutions/n-plus-1 1.2.0
   ```

3. **Before sync:**
   ```bash
   # See what's different
   /fire-skills-diff database-solutions/n-plus-1 project global
   # Then sync
   /fire-skills-sync --push
   ```

## Related Commands

- `/fire-skills-history` - View all versions
- `/fire-skills-rollback` - Revert to a version
- `/fire-search --detail` - View current content
- `/fire-skills-sync` - Sync between libraries
