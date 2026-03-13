#!/bin/bash
# MIT License - Copyright (c) 2026 ThierryN - https://github.com/ThierryN/dominion-flow
#
# Skill Import Helper
# Downloads and normalizes external skills for the Dominion Flow skills library.
#
# Usage:
#   bash skill-import.sh <source> [--category <category>] [--quarantine]
#
# Sources:
#   github:owner/repo/path     GitHub repository path
#   https://...                 Direct URL to markdown file
#   ./local-file.md             Local file path
#
# Examples:
#   bash skill-import.sh github:wshobson/commands/code-review
#   bash skill-import.sh https://raw.githubusercontent.com/user/repo/main/skill.md
#   bash skill-import.sh ./my-pattern.md --category api-patterns

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$PLUGIN_ROOT/skills-library"
QUARANTINE_DIR="$SKILLS_DIR/_quarantine"
TEMP_DIR="/tmp/dominion-flow-import"

# Parse arguments
SOURCE="${1:-}"
CATEGORY=""
QUARANTINE=false

shift || true
while [[ $# -gt 0 ]]; do
    case "$1" in
        --category)
            CATEGORY="$2"
            shift 2
            ;;
        --quarantine)
            QUARANTINE=true
            shift
            ;;
        *)
            echo "[ERROR] Unknown argument: $1"
            exit 1
            ;;
    esac
done

if [ -z "$SOURCE" ]; then
    echo "Usage: bash skill-import.sh <source> [--category <category>] [--quarantine]"
    echo ""
    echo "Sources:"
    echo "  github:owner/repo/path   GitHub repository path"
    echo "  https://...              Direct URL to markdown file"
    echo "  ./local-file.md          Local file path"
    exit 1
fi

# Create temp directory
mkdir -p "$TEMP_DIR"
mkdir -p "$QUARANTINE_DIR"

# Fetch the skill content
fetch_skill() {
    local source="$1"
    local output="$TEMP_DIR/imported-skill.md"

    if [[ "$source" == github:* ]]; then
        # Parse github:owner/repo/path format
        local gh_path="${source#github:}"
        local owner=$(echo "$gh_path" | cut -d'/' -f1)
        local repo=$(echo "$gh_path" | cut -d'/' -f2)
        local skill_path=$(echo "$gh_path" | cut -d'/' -f3-)

        # Try SKILL.md first (skills.sh format), then direct path
        local url="https://raw.githubusercontent.com/${owner}/${repo}/main/${skill_path}/SKILL.md"
        echo "[FETCH] Trying: $url"

        if curl -sfL "$url" -o "$output" 2>/dev/null; then
            echo "[OK] Fetched SKILL.md format"
        else
            # Try as direct markdown file
            url="https://raw.githubusercontent.com/${owner}/${repo}/main/${skill_path}.md"
            echo "[FETCH] Trying: $url"
            if curl -sfL "$url" -o "$output" 2>/dev/null; then
                echo "[OK] Fetched markdown file"
            else
                # Try without .md extension
                url="https://raw.githubusercontent.com/${owner}/${repo}/main/${skill_path}"
                echo "[FETCH] Trying: $url"
                curl -sfL "$url" -o "$output" || {
                    echo "[ERROR] Could not fetch from any GitHub path variant"
                    exit 1
                }
                echo "[OK] Fetched raw file"
            fi
        fi

    elif [[ "$source" == https://* ]] || [[ "$source" == http://* ]]; then
        echo "[FETCH] Downloading: $source"
        curl -sfL "$source" -o "$output" || {
            echo "[ERROR] Failed to download from URL: $source"
            exit 1
        }
        echo "[OK] Downloaded"

    elif [ -f "$source" ]; then
        echo "[FETCH] Reading local file: $source"
        cp "$source" "$output"
        echo "[OK] Copied local file"

    else
        echo "[ERROR] Source not found or unrecognized format: $source"
        echo "Supported: github:owner/repo/path, https://..., ./local-file.md"
        exit 1
    fi

    echo "$output"
}

# Extract skill name from content
extract_name() {
    local file="$1"

    # Try frontmatter name field first
    local name=$(grep -m1 '^name:' "$file" 2>/dev/null | sed 's/name:[[:space:]]*//' | tr -d '"' | tr -d "'" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')

    if [ -n "$name" ]; then
        echo "$name"
        return
    fi

    # Try first heading
    name=$(grep -m1 '^# ' "$file" 2>/dev/null | sed 's/^# //' | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')

    if [ -n "$name" ]; then
        echo "$name"
        return
    fi

    # Fallback to filename
    echo "imported-$(date +%Y%m%d-%H%M%S)"
}

# Check if frontmatter exists
has_frontmatter() {
    head -1 "$1" | grep -q '^---$'
}

# Normalize to Dominion Flow format
normalize_skill() {
    local file="$1"
    local name="$2"
    local output="$TEMP_DIR/normalized-skill.md"
    local today=$(date +%Y-%m-%d)

    if has_frontmatter "$file"; then
        # Has frontmatter — ensure all required fields exist
        # Read existing frontmatter
        local has_version=$(grep -c '^version:' "$file" || echo 0)
        local has_contributed=$(grep -c '^contributed:' "$file" || echo 0)
        local has_category=$(grep -c '^category:' "$file" || echo 0)
        local has_difficulty=$(grep -c '^difficulty:' "$file" || echo 0)
        local has_tags=$(grep -c '^tags:' "$file" || echo 0)

        # Copy file and add missing fields after first ---
        cp "$file" "$output"

        if [ "$has_version" -eq 0 ]; then
            sed -i '1,/^---$/{ /^---$/a\version: 1.0.0' -e '}' "$output" 2>/dev/null || true
        fi
        if [ "$has_contributed" -eq 0 ]; then
            sed -i '1,/^---$/{ /^---$/a\contributed: '"$today" -e '}' "$output" 2>/dev/null || true
        fi
        if [ "$has_category" -eq 0 ] && [ -n "$CATEGORY" ]; then
            sed -i '1,/^---$/{ /^---$/a\category: '"$CATEGORY" -e '}' "$output" 2>/dev/null || true
        fi

        echo "[NORMALIZE] Added missing frontmatter fields"
    else
        # No frontmatter — wrap in Dominion Flow format
        cat > "$output" << EOF
---
name: $name
category: ${CATEGORY:-uncategorized}
version: 1.0.0
contributed: $today
contributor: imported:${SOURCE}
last_updated: $today
tags: [imported]
difficulty: medium
usage_count: 0
success_rate: 100
---

EOF
        cat "$file" >> "$output"
        echo "[NORMALIZE] Added Dominion Flow frontmatter"
    fi

    # Add import attribution if not present
    if ! grep -q 'Imported from:' "$output"; then
        echo "" >> "$output"
        echo "## Import Attribution" >> "$output"
        echo "" >> "$output"
        echo "- Imported from: \`$SOURCE\`" >> "$output"
        echo "- Import date: $today" >> "$output"
    fi

    echo "$output"
}

# Main flow
echo "============================================="
echo "       DOMINION FLOW SKILL IMPORT"
echo "============================================="
echo ""
echo "Source: $SOURCE"
echo ""

# Step 1: Fetch
FETCHED=$(fetch_skill "$SOURCE")
echo ""

# Step 2: Extract name
SKILL_NAME=$(extract_name "$FETCHED")
echo "[NAME] Detected skill name: $SKILL_NAME"

# Step 3: Normalize
NORMALIZED=$(normalize_skill "$FETCHED" "$SKILL_NAME")
echo ""

# Step 4: Report
FILE_SIZE=$(wc -c < "$NORMALIZED" | tr -d ' ')
LINE_COUNT=$(wc -l < "$NORMALIZED" | tr -d ' ')

echo "============================================="
echo "       IMPORT READY"
echo "============================================="
echo ""
echo "  Skill Name: $SKILL_NAME"
echo "  Category:   ${CATEGORY:-uncategorized}"
echo "  File Size:  ${FILE_SIZE} bytes"
echo "  Lines:      ${LINE_COUNT}"
echo "  Quarantine: $QUARANTINE"
echo ""

# Step 5: Determine destination
if [ "$QUARANTINE" = true ]; then
    DEST="$QUARANTINE_DIR/${SKILL_NAME}.md"
    echo "  Destination: _quarantine/${SKILL_NAME}.md"
else
    DEST_DIR="$SKILLS_DIR/${CATEGORY:-uncategorized}"
    mkdir -p "$DEST_DIR"
    DEST="$DEST_DIR/${SKILL_NAME}.md"
    echo "  Destination: ${CATEGORY:-uncategorized}/${SKILL_NAME}.md"
fi

# Step 6: Copy to destination
cp "$NORMALIZED" "$DEST"
echo ""
echo "[SAVED] $DEST"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "============================================="
echo "  IMPORTANT: Run security scan before use!"
echo "  /fire-skill test ${CATEGORY:-uncategorized}/$SKILL_NAME"
echo "============================================="
