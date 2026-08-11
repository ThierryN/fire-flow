---
name: plugin-doc-auto-generation
category: plugin-development
version: 1.0.0
contributed: 2026-03-06
contributor: dominion-flow
last_updated: 2026-03-06
contributors:
  - dominion-flow
tags: [bash, plugin, documentation, automation, cli, devops]
difficulty: easy
usage_count: 0
success_rate: 100
---

# Plugin Documentation Auto-Generation

## Problem

Claude Code plugin documentation drifts from reality over time. When you add new commands, agents, or skills, the index files and README stats become stale. Manual counting is error-prone and tedious.

Common symptoms:
- README says "39 commands" but there are actually 42 on disk
- SKILLS-INDEX.md lists 237 skills but 470+ exist in the filesystem
- Agent reference table shows 5 agents but 13 `.md` files exist in `agents/`
- Version numbers are inconsistent across plugin.json, README, and COMMAND-REFERENCE

## Solution Pattern

Create shell scripts that scan the filesystem (the source of truth) and either generate index files or audit documentation for drift. Use `plugin.json` as the single source of truth for the version number, and propagate it to all other files.

Three scripts handle the complete lifecycle:

1. **`generate-skills-index.sh`** — Walks the skills directory tree, counts `.md` files per category, and generates a complete `SKILLS-INDEX.md` with category headers and skill listings.

2. **`generate-command-reference.sh`** — Counts commands, agents, and skills on disk. Outputs an agent reference table. Runs a sync check against `plugin.json` and `README.md` to flag drift.

3. **`sync-version.sh`** — Reads the version from `plugin.json` (or accepts a new version as argument), then `sed`-replaces all version references across documentation files.

## Code Example

```bash
# Before (manual, error-prone)
# Developer manually edits SKILLS-INDEX.md
# Developer manually counts: "ls commands/ | wc -l"
# Developer manually updates README: "Includes 39 slash commands..."
# Result: Numbers drift within days

# After (automated, always accurate)
# Generate skills index from filesystem
bash scripts/generate-skills-index.sh
# Output: SKILLS-INDEX.md regenerated with accurate count

# Audit command/agent counts and check for drift
bash scripts/generate-command-reference.sh
# Output: Stats + sync check showing OK or DRIFT

# Bump version across all files
bash scripts/sync-version.sh 10.1.0
# Output: plugin.json + all docs updated to v10.1.0
```

### generate-skills-index.sh (core pattern)

```bash
#!/bin/bash
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$PLUGIN_ROOT/skills-library"
OUTPUT="$SKILLS_DIR/SKILLS-INDEX.md"

# Count total skills (excluding index/meta files)
TOTAL=$(find "$SKILLS_DIR" -name "*.md" \
    -not -name "SKILLS-INDEX.md" \
    -not -name "README.md" \
    | wc -l | tr -d ' ')

# Get version from plugin.json (source of truth)
VERSION=$(grep '"version"' "$PLUGIN_ROOT/plugin.json" \
    | head -1 \
    | sed 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')

# Generate header
cat > "$OUTPUT" << HEADER
# Skills Library Index
> Auto-generated — $(date +%Y-%m-%d) — v${VERSION}
> **Total skills: ${TOTAL}**
---
HEADER

# Walk each category directory
find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | sort | while read -r dir; do
    DIRNAME=$(basename "$dir")
    [[ "$DIRNAME" == .* ]] && continue
    COUNT=$(find "$dir" -name "*.md" -not -name "README.md" | wc -l | tr -d ' ')
    [ "$COUNT" -eq 0 ] && continue

    TITLE=$(echo "$DIRNAME" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')
    echo "### $TITLE ($COUNT skills)" >> "$OUTPUT"
    echo "" >> "$OUTPUT"

    find "$dir" -name "*.md" -not -name "README.md" | sort | while read -r file; do
        NAME=$(basename "$file" .md)
        DESC=$(grep -m 1 "^# " "$file" 2>/dev/null | sed 's/^# //' || echo "$NAME")
        echo "- \`$NAME\` — $DESC" >> "$OUTPUT"
    done
    echo "" >> "$OUTPUT"
done

echo "Generated: $TOTAL skills indexed"
```

### sync-version.sh (core pattern)

```bash
#!/bin/bash
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NEW_VERSION="${1:-$(grep '"version"' "$PLUGIN_ROOT/plugin.json" \
    | head -1 | sed 's/.*"\([^"]*\)".*/\1/')}"

# Update plugin.json if version was passed as argument
[ $# -ge 1 ] && sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$NEW_VERSION\"/" \
    "$PLUGIN_ROOT/plugin.json"

# Propagate to all documentation files
for file in README.md COMMAND-REFERENCE.md DOMINION-FLOW-OVERVIEW.md; do
    [ -f "$PLUGIN_ROOT/$file" ] || continue
    sed -i "s/v[0-9]\+\.[0-9]\+\(\.[0-9]\+\)\?/v$NEW_VERSION/g" "$PLUGIN_ROOT/$file"
done
```

## Implementation Steps

1. Create a `scripts/` directory in your plugin root
2. Add `generate-skills-index.sh` — scans skills and generates index
3. Add `generate-command-reference.sh` — audits counts and flags drift
4. Add `sync-version.sh` — propagates version from plugin.json
5. Run after any structural change (new commands, agents, or skills)
6. Optionally add to a pre-commit hook or CI pipeline

## When to Use

- After adding new commands, agents, or skills to a plugin
- Before tagging a release (ensures docs match reality)
- When preparing a README for public visibility (accuracy matters)
- As part of a CI pipeline to catch documentation drift

## When NOT to Use

- For plugins with fewer than 10 files (manual is fine)
- When documentation intentionally differs from disk (e.g., hiding internal/experimental commands)
- In non-plugin projects where docs aren't filesystem-derived

## Common Mistakes

- Forgetting to exclude meta files (SKILLS-INDEX.md, README.md) from the count
- Using `wc -l` without `tr -d ' '` — macOS `wc` adds leading spaces
- Not using `set -euo pipefail` — silent failures cause stale output
- Hardcoding version numbers instead of reading from plugin.json

## Related Skills

- [claude-md-archival](../_general/methodology/claude-md-archival.md) — CLAUDE.md management patterns
- [git-worktrees-parallel](../_general/methodology/git-worktrees-parallel.md) — Parallel development workflows

## References

- Contributed from: dominion-flow competitive analysis session (2026-03-06)
- Pattern discovered when audit revealed 39-vs-42 command count drift
