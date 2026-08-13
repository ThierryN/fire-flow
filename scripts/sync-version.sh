#!/bin/bash
# MIT License - Copyright (c) 2026 ThierryN - https://github.com/ThierryN/fire-flow
#
# Sync version number across all files that reference it.
# Run from the plugin root: bash scripts/sync-version.sh [new-version]
#
# If no version argument is given, reads from plugin.json (source of truth).
#
# Docs are updated by replacing the OLD version string only, never by matching
# any version-shaped text. DOMINION-FLOW-OVERVIEW.md carries the release history
# (v1.0 ... v13.0); a pattern-based replace would rewrite every historical entry.

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

read_json_version() {
    grep '"version"' "$1" | head -1 | sed 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/'
}

# The version currently recorded — what we replace FROM.
OLD_VERSION="$(read_json_version "$PLUGIN_ROOT/plugin.json")"

if [ $# -ge 1 ]; then
    NEW_VERSION="$1"
else
    NEW_VERSION="$OLD_VERSION"
    echo "Reading version from plugin.json: v$NEW_VERSION"
fi

if ! printf '%s' "$NEW_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "ERROR: '$NEW_VERSION' is not a semver x.y.z version." >&2
    exit 1
fi

echo ""
echo "=== Syncing v$OLD_VERSION -> v$NEW_VERSION ==="

# ── JSON manifests: replace the value of the first "version" key ──────────────
JSON_FILES=(
    "plugin.json"
    ".claude-plugin/plugin.json"
    "version.json"
)

UPDATED=0
for file in "${JSON_FILES[@]}"; do
    FILEPATH="$PLUGIN_ROOT/$file"
    [ ! -f "$FILEPATH" ] && { echo "  [SKIP] $file (not present)"; continue; }

    # 0,/re/ limits the substitution to the FIRST match, so a "version" key
    # nested elsewhere in the manifest is left alone.
    sed -i "0,/\"version\"[[:space:]]*:[[:space:]]*\"[^\"]*\"/s//\"version\": \"$NEW_VERSION\"/" "$FILEPATH"
    echo "  [UPDATED] $file"
    UPDATED=$((UPDATED + 1))
done

# ── Docs: replace the OLD version string only ────────────────────────────────
if [ "$OLD_VERSION" = "$NEW_VERSION" ]; then
    echo "  [SKIP] docs (version unchanged)"
else
    DOC_FILES=(
        "README.md"
        "COMMAND-REFERENCE.md"
        "DOMINION-FLOW-OVERVIEW.md"
        "QUICK-START.md"
        "ARCHITECTURE-DIAGRAM.md"
        "skills-library/SKILLS-INDEX.md"
    )

    # Escape dots so 12.9.0 cannot also match 12x9y0.
    OLD_ESC="$(printf '%s' "$OLD_VERSION" | sed 's/\./\\./g')"

    for file in "${DOC_FILES[@]}"; do
        FILEPATH="$PLUGIN_ROOT/$file"
        [ ! -f "$FILEPATH" ] && continue

        if grep -q "v$OLD_VERSION" "$FILEPATH" 2>/dev/null; then
            sed -i "s/v$OLD_ESC/v$NEW_VERSION/g" "$FILEPATH"
            echo "  [UPDATED] $file"
            UPDATED=$((UPDATED + 1))
        else
            echo "  [SKIP] $file (no v$OLD_VERSION reference)"
        fi
    done
fi

echo ""
echo "=== Version sync complete ==="
echo "  Version: v$NEW_VERSION"
echo "  Files updated: $UPDATED"
echo ""
echo "Source of truth: plugin.json"
echo "Note: package.json is the npm version and tracks its own line — not synced here."
echo "Run 'git diff' to review changes before committing."
