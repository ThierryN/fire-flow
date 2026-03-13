#!/bin/bash
# MIT License - Copyright (c) 2026 ThierryN - https://github.com/ThierryN/dominion-flow
#
# Skill Validation Script
# Validates skill files for format, completeness, and basic security.
#
# Usage:
#   bash skill-validate.sh <skill-path>          Validate one skill
#   bash skill-validate.sh --category <name>     Validate all skills in category
#   bash skill-validate.sh --all                 Validate entire library
#   bash skill-validate.sh --strict <skill-path> Strict mode (all sections required)
#
# Exit codes:
#   0 = All checks passed
#   1 = Failures found
#   2 = Warnings only

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$PLUGIN_ROOT/skills-library"

# Counters
PASS=0
WARN=0
FAIL=0
TOTAL_FILES=0

STRICT=false
VERBOSE=false

# Colors (if terminal supports them)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

pass() { PASS=$((PASS + 1)); echo -e "  ${GREEN}[PASS]${NC} $1"; }
warn() { WARN=$((WARN + 1)); echo -e "  ${YELLOW}[WARN]${NC} $1"; }
fail() { FAIL=$((FAIL + 1)); echo -e "  ${RED}[FAIL]${NC} $1"; }
info() { echo -e "  ${BLUE}[INFO]${NC} $1"; }

# Validate a single skill file
validate_skill() {
    local file="$1"
    local rel_path="${file#$SKILLS_DIR/}"

    echo ""
    echo "-------------------------------------------------------------"
    echo "  Validating: $rel_path"
    echo "-------------------------------------------------------------"

    # Check file exists and is readable
    if [ ! -f "$file" ]; then
        fail "File not found: $file"
        return
    fi

    if [ ! -r "$file" ]; then
        fail "File not readable: $file"
        return
    fi

    local content
    content=$(cat "$file")

    # === FORMAT CHECKS ===

    # Check frontmatter exists
    if echo "$content" | head -1 | grep -q '^---$'; then
        pass "YAML frontmatter present"
    else
        fail "YAML frontmatter missing (must start with ---)"
        return  # Can't continue without frontmatter
    fi

    # Check frontmatter closes
    local fm_close=$(echo "$content" | tail -n +2 | grep -n '^---$' | head -1 | cut -d: -f1)
    if [ -n "$fm_close" ]; then
        pass "Frontmatter properly closed"
    else
        fail "Frontmatter not closed (missing second ---)"
        return
    fi

    # Extract frontmatter
    local frontmatter
    frontmatter=$(echo "$content" | sed -n '2,/^---$/p' | head -n -1)

    # Required frontmatter fields
    if echo "$frontmatter" | grep -q '^name:'; then
        pass "Required field: name"
    else
        fail "Missing required field: name"
    fi

    if echo "$frontmatter" | grep -q '^category:'; then
        pass "Required field: category"
    else
        fail "Missing required field: category"
    fi

    if echo "$frontmatter" | grep -q '^version:'; then
        local version=$(echo "$frontmatter" | grep '^version:' | sed 's/version:[[:space:]]*//')
        if echo "$version" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
            pass "Version follows semver: $version"
        else
            warn "Version does not follow semver: $version"
        fi
    else
        warn "Missing field: version (default: 1.0.0)"
    fi

    # Optional but recommended fields
    if echo "$frontmatter" | grep -q '^tags:'; then
        pass "Tags field present"
    else
        warn "Missing field: tags"
    fi

    if echo "$frontmatter" | grep -q '^difficulty:'; then
        local diff=$(echo "$frontmatter" | grep '^difficulty:' | sed 's/difficulty:[[:space:]]*//')
        if echo "$diff" | grep -qE '^(easy|medium|hard)$'; then
            pass "Difficulty is valid: $diff"
        else
            warn "Difficulty should be easy|medium|hard, got: $diff"
        fi
    else
        warn "Missing field: difficulty"
    fi

    if echo "$frontmatter" | grep -q '^type:'; then
        local type=$(echo "$frontmatter" | grep '^type:' | sed 's/type:[[:space:]]*//')
        info "Skill type: $type"
    else
        info "No type field (consider adding for template conformance)"
    fi

    # === CONTENT CHECKS ===

    # Title heading
    if echo "$content" | grep -q '^# '; then
        pass "# Title heading present"
    else
        fail "# Title heading missing"
    fi

    # Required sections
    if echo "$content" | grep -q '^## Problem'; then
        pass "## Problem section present"
    else
        fail "## Problem section missing"
    fi

    if echo "$content" | grep -qE '^## (Solution Pattern|Solution|Fix)'; then
        pass "## Solution section present"
    else
        fail "## Solution section missing"
    fi

    # Recommended sections
    if echo "$content" | grep -q '^## When to Use'; then
        pass "## When to Use section present"
    else
        if [ "$STRICT" = true ]; then
            fail "## When to Use section missing (strict mode)"
        else
            warn "## When to Use section missing"
        fi
    fi

    if echo "$content" | grep -q '^## When NOT to Use'; then
        pass "## When NOT to Use section present"
    else
        if [ "$STRICT" = true ]; then
            fail "## When NOT to Use section missing (strict mode)"
        else
            warn "## When NOT to Use section missing"
        fi
    fi

    # Code examples
    if echo "$content" | grep -q '```'; then
        local code_blocks=$(echo "$content" | grep -c '```' || echo 0)
        local pairs=$((code_blocks / 2))
        pass "Code examples present ($pairs blocks)"
    else
        if [ "$STRICT" = true ]; then
            fail "No code examples (strict mode)"
        else
            warn "No code examples found"
        fi
    fi

    # === CROSS-REFERENCE CHECKS ===

    # Check related skills exist
    local related_skills=$(echo "$content" | grep -oE '\[[a-z0-9-]+\]' | sed 's/\[//;s/\]//' | head -5)
    if [ -n "$related_skills" ]; then
        while IFS= read -r ref_skill; do
            if find "$SKILLS_DIR" -name "${ref_skill}.md" 2>/dev/null | grep -q .; then
                pass "Related skill found: $ref_skill"
            else
                warn "Related skill not found in library: $ref_skill"
            fi
        done <<< "$related_skills"
    fi

    # Check for duplicate skill name
    local skill_name=$(echo "$frontmatter" | grep '^name:' | sed 's/name:[[:space:]]*//' | tr -d '"' | tr -d "'")
    if [ -n "$skill_name" ]; then
        local dupe_count=$(find "$SKILLS_DIR" -name "*.md" -exec grep -l "^name: $skill_name$" {} \; 2>/dev/null | wc -l)
        if [ "$dupe_count" -gt 1 ]; then
            warn "Duplicate skill name detected: $skill_name ($dupe_count files)"
        else
            pass "No duplicate skill name"
        fi
    fi

    # === SECURITY QUICK SCAN ===

    # Check for potential credentials
    if echo "$content" | grep -qiE '(sk-[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36}|glpat-[a-zA-Z0-9-]{20,})'; then
        fail "CREDENTIAL PATTERN DETECTED — real API key or token found!"
    else
        pass "No credential patterns detected"
    fi

    # Check for suspicious URLs
    if echo "$content" | grep -qiE '(ngrok\.io|requestbin\.com|hookbin\.com|pipedream\.net)'; then
        warn "Suspicious URL detected (potential exfiltration endpoint)"
    else
        pass "No suspicious URLs detected"
    fi

    # Check for prompt injection
    if echo "$content" | grep -qiE '(ignore previous|forget all|you are now|system prompt|override instructions)'; then
        fail "PROMPT INJECTION SIGNATURE DETECTED"
    else
        pass "No prompt injection signatures"
    fi
}

# Parse arguments
FILES=()
CATEGORY=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --all)
            FILES=($(find "$SKILLS_DIR" -name "*.md" -not -name "SKILLS-INDEX.md" -not -name "SKILLS_LIBRARY_INDEX.md" -not -name "AVAILABLE_TOOLS_REFERENCE.md" | sort))
            shift
            ;;
        --category)
            CATEGORY="$2"
            FILES=($(find "$SKILLS_DIR/$CATEGORY" -name "*.md" 2>/dev/null | sort))
            if [ ${#FILES[@]} -eq 0 ]; then
                echo "[ERROR] No skills found in category: $CATEGORY"
                exit 1
            fi
            shift 2
            ;;
        --strict)
            STRICT=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            # Treat as a skill path
            if [ -f "$1" ]; then
                # Absolute or relative path that exists
                FILES+=("$1")
            elif [ -f "$SKILLS_DIR/$1" ]; then
                # Relative to skills dir, already has extension
                FILES+=("$SKILLS_DIR/$1")
            elif [ -f "$SKILLS_DIR/$1.md" ]; then
                # Relative to skills dir, needs extension
                FILES+=("$SKILLS_DIR/$1.md")
            else
                # Try to find it by name
                FOUND=$(find "$SKILLS_DIR" -name "$(basename "$1" .md).md" 2>/dev/null | head -1)
                if [ -n "$FOUND" ]; then
                    FILES+=("$FOUND")
                else
                    FILES+=("$1")  # Pass through, will show "not found"
                fi
            fi
            shift
            ;;
    esac
done

if [ ${#FILES[@]} -eq 0 ]; then
    echo "Usage: bash skill-validate.sh <skill-path|--all|--category name>"
    echo ""
    echo "Options:"
    echo "  --all              Validate entire library"
    echo "  --category <name>  Validate all skills in a category"
    echo "  --strict           Require all sections"
    echo "  --verbose          Show more detail"
    exit 1
fi

# Header
echo "============================================="
echo "       DOMINION FLOW SKILL VALIDATION"
echo "============================================="
echo ""
echo "  Mode: $([ "$STRICT" = true ] && echo "STRICT" || echo "Standard")"
echo "  Files: ${#FILES[@]}"
echo ""

# Validate each file
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        TOTAL_FILES=$((TOTAL_FILES + 1))
        validate_skill "$file"
    else
        echo ""
        echo "  [SKIP] File not found: $file"
    fi
done

# Summary
echo ""
echo "============================================="
echo "       VALIDATION SUMMARY"
echo "============================================="
echo ""
echo "  Files Checked: $TOTAL_FILES"
echo -e "  ${GREEN}PASS:${NC} $PASS"
echo -e "  ${YELLOW}WARN:${NC} $WARN"
echo -e "  ${RED}FAIL:${NC} $FAIL"
echo ""

if [ $FAIL -gt 0 ]; then
    echo -e "  Result: ${RED}FAILURES FOUND${NC}"
    echo "  Fix the failures above before using these skills."
    exit 1
elif [ $WARN -gt 0 ]; then
    echo -e "  Result: ${YELLOW}WARNINGS${NC} (skills usable but could be improved)"
    exit 2
else
    echo -e "  Result: ${GREEN}ALL CHECKS PASSED${NC}"
    exit 0
fi
