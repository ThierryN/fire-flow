#!/bin/bash
# MIT License - Copyright (c) 2026 ThierryN - https://github.com/ThierryN/dominion-flow
#
# Auto-generate command counts and agent counts for documentation.
# Run from the plugin root: bash scripts/generate-command-reference.sh
#
# This script updates version numbers, command counts, and agent counts
# across all documentation files to keep them in sync.

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COMMANDS_DIR="$PLUGIN_ROOT/commands"
AGENTS_DIR="$PLUGIN_ROOT/agents"
SKILLS_DIR="$PLUGIN_ROOT/skills-library"

# Count everything
CMD_COUNT=$(find "$COMMANDS_DIR" -name "*.md" | wc -l | tr -d ' ')
AGENT_COUNT=$(find "$AGENTS_DIR" -name "*.md" | wc -l | tr -d ' ')
SKILL_COUNT=$(find "$SKILLS_DIR" -name "*.md" \
    -not -name "SKILLS-INDEX.md" \
    -not -name "SKILLS_LIBRARY_INDEX.md" \
    -not -name "AVAILABLE_TOOLS_REFERENCE.md" \
    -not -name "README.md" \
    | wc -l | tr -d ' ')

# Get version from plugin.json
VERSION=$(grep '"version"' "$PLUGIN_ROOT/plugin.json" | head -1 | sed 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')

# Count tiers (directories in commands/ that follow tier naming)
TIER_DIRS=$(find "$COMMANDS_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')

echo "=== DOMINION FLOW STATS ==="
echo "  Version:  v$VERSION"
echo "  Commands: $CMD_COUNT"
echo "  Agents:   $AGENT_COUNT"
echo "  Skills:   $SKILL_COUNT"
echo "  Tiers:    $TIER_DIRS (directories)"
echo ""

# Generate agents reference table
echo "=== AGENTS REFERENCE ==="
echo ""
echo "| # | Agent | Description |"
echo "|---|-------|-------------|"

IDX=1
find "$AGENTS_DIR" -name "*.md" | sort | while read -r file; do
    NAME=$(basename "$file" .md)
    # Extract description from first paragraph or heading
    DESC=$(grep -m 1 "^[A-Z]" "$file" 2>/dev/null | head -c 80 || echo "Agent definition")
    echo "| $IDX | \`$NAME\` | $DESC |"
    IDX=$((IDX + 1))
done

echo ""
echo "=== SYNC CHECK ==="

# Check plugin.json description matches
if grep -q "$CMD_COUNT slash commands" "$PLUGIN_ROOT/plugin.json" 2>/dev/null; then
    echo "  [OK] plugin.json command count matches ($CMD_COUNT)"
else
    echo "  [DRIFT] plugin.json command count does not match (expected: $CMD_COUNT)"
fi

if grep -q "$CMD_COUNT" "$PLUGIN_ROOT/README.md" 2>/dev/null; then
    echo "  [OK] README.md references $CMD_COUNT"
else
    echo "  [DRIFT] README.md may have stale command count"
fi

echo ""
echo "Done. Review output above and update files as needed."
