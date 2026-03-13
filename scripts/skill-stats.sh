#!/bin/bash
# MIT License - Copyright (c) 2026 ThierryN - https://github.com/ThierryN/dominion-flow
#
# Skill Library Statistics
# Quick stats about the skills library: counts, categories, types, health.
#
# Usage:
#   bash skill-stats.sh              Full dashboard
#   bash skill-stats.sh --summary    One-line summary
#   bash skill-stats.sh --json       JSON output for integrations

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$PLUGIN_ROOT/skills-library"

JSON_MODE=false
SUMMARY_MODE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json) JSON_MODE=true; shift ;;
        --summary) SUMMARY_MODE=true; shift ;;
        *) shift ;;
    esac
done

# Count skills (exclude index files and non-skill markdown)
EXCLUDE_PATTERN="-not -name SKILLS-INDEX.md -not -name SKILLS_LIBRARY_INDEX.md -not -name AVAILABLE_TOOLS_REFERENCE.md -not -name LMS_ZOOM_LEARNING_PATHS_INTEGRATION.md -not -name appointment-scheduler-design.md -not -name wordpress-style-theme-components.md -not -name lms-theme-system.md"

TOTAL=$(find "$SKILLS_DIR" -name "*.md" $EXCLUDE_PATTERN 2>/dev/null | wc -l | tr -d ' ')
GENERAL=$(find "$SKILLS_DIR/_general" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
QUARANTINE=$(find "$SKILLS_DIR/_quarantine" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
PROJECT=$((TOTAL - GENERAL - QUARANTINE))

# Count categories (directories with at least one .md file)
CATEGORIES=$(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d -not -name '_quarantine' | while read -r dir; do
    count=$(find "$dir" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    [ "$count" -gt 0 ] && echo "$dir"
done | wc -l | tr -d ' ')

# Count by type (from frontmatter)
TYPE_DEBUG=$( (grep -rl '^type: debug-pattern' "$SKILLS_DIR" 2>/dev/null || true) | wc -l | tr -d ' ')
TYPE_API=$( (grep -rl '^type: api-integration' "$SKILLS_DIR" 2>/dev/null || true) | wc -l | tr -d ' ')
TYPE_UI=$( (grep -rl '^type: ui-component' "$SKILLS_DIR" 2>/dev/null || true) | wc -l | tr -d ' ')
TYPE_ARCH=$( (grep -rl '^type: architecture' "$SKILLS_DIR" 2>/dev/null || true) | wc -l | tr -d ' ')
TYPE_DEVOPS=$( (grep -rl '^type: devops-recipe' "$SKILLS_DIR" 2>/dev/null || true) | wc -l | tr -d ' ')
TYPE_TYPED=$((TYPE_DEBUG + TYPE_API + TYPE_UI + TYPE_ARCH + TYPE_DEVOPS))
TYPE_UNTYPED=$((TOTAL - TYPE_TYPED))

# Count skills with code examples
WITH_CODE=$( (find "$SKILLS_DIR" -name "*.md" $EXCLUDE_PATTERN -exec grep -l '```' {} \; 2>/dev/null || true) | wc -l | tr -d ' ')

# Count difficulty distribution
DIFF_EASY=$( (grep -rl '^difficulty: easy' "$SKILLS_DIR" 2>/dev/null || true) | wc -l | tr -d ' ')
DIFF_MEDIUM=$( (grep -rl '^difficulty: medium' "$SKILLS_DIR" 2>/dev/null || true) | wc -l | tr -d ' ')
DIFF_HARD=$( (grep -rl '^difficulty: hard' "$SKILLS_DIR" 2>/dev/null || true) | wc -l | tr -d ' ')

# Summary mode
if [ "$SUMMARY_MODE" = true ]; then
    echo "$TOTAL skills | $CATEGORIES categories | $GENERAL general | $PROJECT project | $QUARANTINE quarantine"
    exit 0
fi

# JSON mode
if [ "$JSON_MODE" = true ]; then
    cat << EOF
{
  "total": $TOTAL,
  "general": $GENERAL,
  "project": $PROJECT,
  "quarantine": $QUARANTINE,
  "categories": $CATEGORIES,
  "with_code_examples": $WITH_CODE,
  "types": {
    "debug_pattern": $TYPE_DEBUG,
    "api_integration": $TYPE_API,
    "ui_component": $TYPE_UI,
    "architecture": $TYPE_ARCH,
    "devops_recipe": $TYPE_DEVOPS,
    "untyped": $TYPE_UNTYPED
  },
  "difficulty": {
    "easy": $DIFF_EASY,
    "medium": $DIFF_MEDIUM,
    "hard": $DIFF_HARD,
    "unrated": $((TOTAL - DIFF_EASY - DIFF_MEDIUM - DIFF_HARD))
  }
}
EOF
    exit 0
fi

# Full dashboard
echo "============================================="
echo "       SKILLS LIBRARY DASHBOARD"
echo "============================================="
echo ""
echo "  Library: $SKILLS_DIR"
echo ""
echo "  Total Skills:       $TOTAL"
echo "  General (cross-project): $GENERAL"
echo "  Project-specific:   $PROJECT"
echo "  Quarantined:        $QUARANTINE"
echo "  Categories:         $CATEGORIES"
echo "  With Code Examples: $WITH_CODE / $TOTAL"
echo ""
echo "---------------------------------------------"
echo "  TYPE DISTRIBUTION"
echo "---------------------------------------------"
echo ""

# Bar chart helper
bar() {
    local count=$1
    local total=$2
    local label=$3
    local width=20

    if [ "$total" -gt 0 ]; then
        local filled=$((count * width / total))
        [ "$filled" -eq 0 ] && [ "$count" -gt 0 ] && filled=1
        local empty=$((width - filled))
        printf "  %-18s [" "$label"
        [ "$filled" -gt 0 ] && printf '%0.s=' $(seq 1 $filled) || true
        [ "$empty" -gt 0 ] && printf '%0.s ' $(seq 1 $empty) || true
        printf "] %3d (%d%%)\n" "$count" "$((count * 100 / total))"
    else
        printf "  %-18s [                    ]   0 (0%%)\n" "$label"
    fi
}

bar $TYPE_DEBUG $TOTAL "debug-pattern"
bar $TYPE_API $TOTAL "api-integration"
bar $TYPE_UI $TOTAL "ui-component"
bar $TYPE_ARCH $TOTAL "architecture"
bar $TYPE_DEVOPS $TOTAL "devops-recipe"
bar $TYPE_UNTYPED $TOTAL "untyped/general"

echo ""
echo "---------------------------------------------"
echo "  DIFFICULTY DISTRIBUTION"
echo "---------------------------------------------"
echo ""

bar $DIFF_EASY $TOTAL "easy"
bar $DIFF_MEDIUM $TOTAL "medium"
bar $DIFF_HARD $TOTAL "hard"
bar $((TOTAL - DIFF_EASY - DIFF_MEDIUM - DIFF_HARD)) $TOTAL "unrated"

echo ""
echo "---------------------------------------------"
echo "  CATEGORIES"
echo "---------------------------------------------"
echo ""

find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | sort | while read -r dir; do
    dirname=$(basename "$dir")
    count=$(find "$dir" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    [ "$count" -gt 0 ] && printf "  %-30s %3d skills\n" "$dirname" "$count"
done

echo ""
echo "---------------------------------------------"
echo "  RECOMMENDATIONS"
echo "---------------------------------------------"
echo ""

if [ "$TYPE_UNTYPED" -gt 0 ]; then
    echo "  UPGRADE: $TYPE_UNTYPED skills have no 'type' field."
    echo "           Run: /fire-skill upgrade --all --dry-run"
fi

if [ "$QUARANTINE" -gt 0 ]; then
    echo "  REVIEW: $QUARANTINE skills in quarantine need review."
    echo "           Run: /fire-skill list --quarantine"
fi

if [ "$WITH_CODE" -lt "$((TOTAL * 70 / 100))" ]; then
    echo "  IMPROVE: Only $((WITH_CODE * 100 / TOTAL))% of skills have code examples."
    echo "           Skills with code examples are more useful."
fi

echo ""
echo "============================================="
