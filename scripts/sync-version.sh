#!/bin/bash
# MIT License - Copyright (c) 2026 ThierryN - https://github.com/ThierryN/dominion-flow
#
# Sync version number across all files that reference it.
# Run from the plugin root: bash scripts/sync-version.sh [new-version]
#
# If no version argument is given, reads from plugin.json (source of truth).

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Get version from argument or plugin.json
if [ $# -ge 1 ]; then
    NEW_VERSION="$1"
    # Update plugin.json first (source of truth)
    sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$NEW_VERSION\"/" "$PLUGIN_ROOT/plugin.json"
    echo "Updated plugin.json to v$NEW_VERSION"
else
    NEW_VERSION=$(grep '"version"' "$PLUGIN_ROOT/plugin.json" | head -1 | sed 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    echo "Reading version from plugin.json: v$NEW_VERSION"
fi

echo ""
echo "=== Syncing v$NEW_VERSION across all files ==="

# Files that may reference the version
FILES_TO_CHECK=(
    "README.md"
    "COMMAND-REFERENCE.md"
    "DOMINION-FLOW-OVERVIEW.md"
    "QUICK-START.md"
    "ARCHITECTURE-DIAGRAM.md"
)

UPDATED=0
for file in "${FILES_TO_CHECK[@]}"; do
    FILEPATH="$PLUGIN_ROOT/$file"
    [ ! -f "$FILEPATH" ] && continue

    # Look for version patterns like "v9.0", "v10.0.0", "Version: X.Y.Z"
    if grep -qE "v[0-9]+\.[0-9]+(\.[0-9]+)?" "$FILEPATH" 2>/dev/null; then
        # Replace common version patterns
        sed -i "s/v[0-9]\+\.[0-9]\+\(\.[0-9]\+\)\?/v$NEW_VERSION/g" "$FILEPATH"
        echo "  [UPDATED] $file"
        UPDATED=$((UPDATED + 1))
    else
        echo "  [SKIP] $file (no version references found)"
    fi
done

# Also update SKILLS-INDEX.md if it exists
if [ -f "$PLUGIN_ROOT/skills-library/SKILLS-INDEX.md" ]; then
    sed -i "s/v[0-9]\+\.[0-9]\+\(\.[0-9]\+\)\?/v$NEW_VERSION/g" "$PLUGIN_ROOT/skills-library/SKILLS-INDEX.md"
    echo "  [UPDATED] skills-library/SKILLS-INDEX.md"
    UPDATED=$((UPDATED + 1))
fi

echo ""
echo "=== Version sync complete ==="
echo "  Version: v$NEW_VERSION"
echo "  Files updated: $UPDATED"
echo ""
echo "Source of truth: plugin.json"
echo "Run 'git diff' to review changes before committing."
