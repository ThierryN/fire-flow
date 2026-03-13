#!/bin/bash
# ============================================================
# sanitize-for-publish.sh
# ============================================================
# One-command staging workflow for publishing dominion-flow
# to the fire-flow public GitHub repo.
#
# Creates a staging copy, strips all private content, then
# commits and pushes — your local working copy is NEVER touched.
#
# What it strips:
#   1. Research citations (all 4 formats)
#   2. Research registry (research-improvements.md → stub)
#   3. Private skill files (memory project, breadcrumbs, etc.)
#   4. Breadcrumb references from core workflow files
#   5. Tier 2 (GitHub/OSS) and Tier 3 (Context7) from researcher
#   6. Research visual guide
#
# What it keeps:
#   - Research pipeline agents (sanitized — Tier 1 + Web Search)
#   - All core workflow agents and commands
#   - General skills library (no project-specific content)
#   - CREDITS.md
#
# Usage:
#   bash scripts/sanitize-for-publish.sh              # Dry run
#   bash scripts/sanitize-for-publish.sh --execute     # Stage + commit
#   bash scripts/sanitize-for-publish.sh --push        # Stage + commit + push
#
# Run from Git Bash on Windows (NOT cmd, PowerShell, or WSL).
# ============================================================

set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STAGING_DIR="/tmp/fire-flow-staging"
PUBLISH_BRANCH="fire-flow-publish"
REMOTE_BRANCH="master"
MODE="dry-run"

case "${1:-}" in
  --execute) MODE="execute" ;;
  --push)    MODE="push" ;;
esac

# Counters
CITATION_COUNT=0
CITATION_FILES=0
PRIVATE_FILES_REMOVED=0
BREADCRUMB_FILES_STRIPPED=0
TIER_REFS_STRIPPED=0

echo "============================================================"
echo "  FIRE-FLOW PUBLISH SANITIZER v2.0"
echo "============================================================"
echo ""
echo "  Plugin dir:  $PLUGIN_DIR"
echo "  Staging dir: $STAGING_DIR"
echo "  Mode:        $MODE"
echo ""

# ─────────────────────────────────────────────────────────────
# PRIVATE FILES TO REMOVE FROM STAGING
# ─────────────────────────────────────────────────────────────
# Add paths here when new private files are created.
# These are removed from the staging copy, NOT from your local.

PRIVATE_FILES=(
  # Memory project skills
  "skills-library/_general/methodology/LIVE_BREADCRUMB_PROTOCOL.md"
  "skills-library/_general/methodology/RESEARCH_BACKED_WORKFLOW_UPGRADE.md"
  "skills-library/_general/methodology/RESEARCH_VISUAL_GUIDE.md"
  "skills-library/_general/methodology/llm-judge-memory-crud.md"
  "skills-library/_general/database-solutions/qdrant-blue-green-aliases.md"
  "skills-library/automation/session-memory-lifecycle.md"
  "skills-library/methodology/HEARTBEAT_PROTOCOL.md"
  "skills-library/methodology/PORTAL_MEMORY_ARCHITECTURE.md"
  "skills-library/methodology/PRODUCTION_MEMORY_PATTERNS.md"
  "skills-library/methodology/REFLEXION_MEMORY_PATTERN.md"
  "skills-library/methodology/RESEARCH_BACKED_WORKFLOW_UPGRADE.md"
  "skills-library/vector-memory/"

  # Project-specific skills (LMS, payments, theology, etc.)
  "skills-library/lms-patterns/"
  "skills-library/integrations/zoom/"
  "skills-library/integrations/paypal/"
  "skills-library/integrations/stripe/"
  "skills-library/theology/"
  "skills-library/admin-features/"
  "skills-library/advanced-features/"
  "skills-library/video-media/"
  "skills-library/ecommerce/IRS_TAX_CALCULATIONS.md"
  "skills-library/ecommerce/IRS_TAX_WITHHOLDING_TABLES.md"
  "skills-library/ecommerce/IRS_1099_REPORTING_GUIDE.md"
  "skills-library/ecommerce/DONATION_RECURRING_SYSTEM.md"
  "skills-library/ecommerce/DONATION_TAX_RECEIPT_SYSTEM.md"
  "skills-library/ecommerce/RECURRING_PAYMENT_ARCHITECTURE.md"
  "skills-library/ecommerce/RECURRING_PAYMENT_PATTERNS.md"
  "skills-library/infrastructure/TAURI_DESKTOP_APP.md"
  "skills-library/infrastructure/TAURI_FILE_SYSTEM_OPERATIONS.md"
  "skills-library/infrastructure/TAURI_IPC_BRIDGE_PATTERNS.md"
  "skills-library/infrastructure/TAURI_SELF_UPDATER.md"
  "skills-library/infrastructure/TAURI_SIGNING_GUIDE.md"
  "skills-library/infrastructure/TAURI_WEBVIEW_INTEGRATION.md"
  "skills-library/automation/c3-loop-engine.md"
  "skills-library/automation/NPM_STYLE_BIBLE_IMPORT_SYSTEM.md"
  "skills-library/_general/patterns-standards/fullstack-bible-study-platform.md"

  # Temp/scan files
  "pii_scan.py"
  "pii_report.txt"
  "apply_fixes.py"
)

# ─────────────────────────────────────────────────────────────
# Step 0: Create staging copy
# ─────────────────────────────────────────────────────────────
echo "--- Step 0: Create Staging Copy ---"

if [ "$MODE" = "dry-run" ]; then
  echo "  WOULD create staging copy at $STAGING_DIR"
  echo "  (using git archive to export only tracked files)"
  echo ""
else
  rm -rf "$STAGING_DIR"
  mkdir -p "$STAGING_DIR"

  # Export only git-tracked files (clean, no .git overhead)
  cd "$PLUGIN_DIR"
  git archive "$PUBLISH_BRANCH" | tar -x -C "$STAGING_DIR"

  echo "  Created staging copy at $STAGING_DIR"
  echo "  Source branch: $PUBLISH_BRANCH"
  echo ""
fi

# ─────────────────────────────────────────────────────────────
# Step 1: Remove private files from staging
# ─────────────────────────────────────────────────────────────
echo "--- Step 1: Remove Private Files ---"

for entry in "${PRIVATE_FILES[@]}"; do
  target="$STAGING_DIR/$entry"
  if [ -e "$target" ]; then
    PRIVATE_FILES_REMOVED=$((PRIVATE_FILES_REMOVED + 1))
    if [ "$MODE" = "dry-run" ]; then
      echo "  WOULD remove: $entry"
    else
      rm -rf "$target"
      echo "  REMOVED: $entry"
    fi
  fi
done

# Remove empty directories left behind
if [ "$MODE" != "dry-run" ]; then
  find "$STAGING_DIR/skills-library" -type d -empty -delete 2>/dev/null || true
fi

echo ""
echo "  Total: $PRIVATE_FILES_REMOVED private files/dirs removed"
echo ""

# ─────────────────────────────────────────────────────────────
# Step 2: Strip research citations (all 4 formats)
# ─────────────────────────────────────────────────────────────
echo "--- Step 2: Strip Research Citations ---"

SEARCH_DIR="$STAGING_DIR"
if [ "$MODE" = "dry-run" ]; then
  SEARCH_DIR="$PLUGIN_DIR"
fi

while IFS= read -r file; do
  # Count ALL citation formats in this file
  m1=$(grep -cE '^\s*>\s*\*\*Research basis' "$file" 2>/dev/null || true)
  m2=$(grep -cE '^\*\*Research basis' "$file" 2>/dev/null || true)
  m3=$(grep -cE '<!--\s*Research basis' "$file" 2>/dev/null || true)
  m4=$(grep -cE '^\s*>\s*Research basis' "$file" 2>/dev/null || true)

  m1=$(echo "$m1" | tr -d '[:space:]'); m1=${m1:-0}
  m2=$(echo "$m2" | tr -d '[:space:]'); m2=${m2:-0}
  m3=$(echo "$m3" | tr -d '[:space:]'); m3=${m3:-0}
  m4=$(echo "$m4" | tr -d '[:space:]'); m4=${m4:-0}

  total=$((m1 + m2 + m3 + m4))

  if [[ "$total" -gt 0 ]]; then
    CITATION_FILES=$((CITATION_FILES + 1))
    CITATION_COUNT=$((CITATION_COUNT + total))
    rel="${file#$SEARCH_DIR/}"

    if [ "$MODE" = "dry-run" ]; then
      echo "  WOULD strip $total citations from: $rel"
    else
      # Format 1: > **Research basis ...
      sed -i '/^\s*>\s*\*\*Research basis/d' "$file"
      # Format 2: **Research basis ... (no blockquote)
      sed -i '/^\*\*Research basis/d' "$file"
      # Format 3: <!-- Research basis: ... --> (HTML comments)
      sed -i '/<!--\s*Research basis/d' "$file"
      # Format 4: > Research basis: ... (no bold)
      sed -i '/^\s*>\s*Research basis/d' "$file"
      # Orphan lines that follow citations
      sed -i '/^\s*>\s*Applied:/d' "$file"
      sed -i '/^\s*>\s*\*\*v[0-9]*\.[0-9]* wiring/d' "$file"
      # Clean double blank lines
      sed -i '/^$/N;/^\n$/d' "$file"
      echo "  STRIPPED $total citations from: $rel"
    fi
  fi
done < <(find "$SEARCH_DIR" -name "*.md" -not -path "*/node_modules/*" -not -path "*/.git/*")

echo ""
echo "  Total: $CITATION_COUNT citations across $CITATION_FILES files"
echo ""

# ─────────────────────────────────────────────────────────────
# Step 3: Replace research-improvements.md with stub
# ─────────────────────────────────────────────────────────────
echo "--- Step 3: Research Improvements Registry ---"

RESEARCH_FILE="$STAGING_DIR/references/research-improvements.md"
if [ "$MODE" = "dry-run" ]; then
  RESEARCH_FILE="$PLUGIN_DIR/references/research-improvements.md"
fi

if [[ -f "$RESEARCH_FILE" ]]; then
  LINE_COUNT=$(wc -l < "$RESEARCH_FILE")
  LINE_COUNT=$(echo "$LINE_COUNT" | tr -d '[:space:]')
  if [ "$MODE" = "dry-run" ]; then
    echo "  WOULD replace ($LINE_COUNT lines) with stub"
  else
    cat > "$RESEARCH_FILE" << 'STUB'
# Research Improvements

Research citations have been removed from the public release.

See the fire-research command for the research pipeline methodology.
STUB
    echo "  REPLACED with stub ($LINE_COUNT lines -> 5 lines)"
  fi
else
  echo "  NOT FOUND (already handled)"
fi
echo ""

# ─────────────────────────────────────────────────────────────
# Step 4: Strip breadcrumb references from core files
# ─────────────────────────────────────────────────────────────
echo "--- Step 4: Strip Breadcrumb References ---"

if [ "$MODE" != "dry-run" ]; then
  # Find files with breadcrumb references (exclude UI/navigation uses)
  while IFS= read -r file; do
    rel="${file#$STAGING_DIR/}"
    # Skip files that use "breadcrumb" in a UI/navigation context
    case "$rel" in
      skills-library/*/ux-*|skills-library/*/nuxt-*|skills-library/*/icon-*) continue ;;
    esac

    # Remove lines containing breadcrumb (case-insensitive)
    count_before=$(wc -l < "$file")
    sed -i '/[Bb]readcrumb/d' "$file"
    count_after=$(wc -l < "$file")

    removed=$((count_before - count_after))
    if [[ "$removed" -gt 0 ]]; then
      BREADCRUMB_FILES_STRIPPED=$((BREADCRUMB_FILES_STRIPPED + 1))
      echo "  STRIPPED $removed breadcrumb refs from: $rel"
    fi
  done < <(grep -rlI "[Bb]readcrumb" "$STAGING_DIR" --include="*.md" --include="*.html" 2>/dev/null || true)
else
  count=$(grep -rlI "[Bb]readcrumb" "$PLUGIN_DIR" --include="*.md" --include="*.html" 2>/dev/null | wc -l || true)
  count=$(echo "$count" | tr -d '[:space:]')
  echo "  WOULD strip breadcrumb references from ~$count files"
fi

echo "  Total: $BREADCRUMB_FILES_STRIPPED files stripped"
echo ""

# ─────────────────────────────────────────────────────────────
# Step 5: Strip Tier 2/3 from researcher agent
# ─────────────────────────────────────────────────────────────
echo "--- Step 5: Sanitize Researcher Tiers ---"

RESEARCHER="$STAGING_DIR/agents/fire-researcher.md"
if [ "$MODE" = "dry-run" ]; then
  RESEARCHER="$PLUGIN_DIR/agents/fire-researcher.md"
fi

if [[ -f "$RESEARCHER" ]]; then
  tier_refs=$(grep -cE 'TIER [23]:|Context7' "$RESEARCHER" 2>/dev/null || true)
  tier_refs=$(echo "$tier_refs" | tr -d '[:space:]'); tier_refs=${tier_refs:-0}

  if [[ "$tier_refs" -gt 0 ]]; then
    TIER_REFS_STRIPPED=$tier_refs
    if [ "$MODE" = "dry-run" ]; then
      echo "  WOULD strip $tier_refs Tier 2/3/Context7 references"
    else
      # Remove Tier 2 block (line starting TIER 2 through next blank line or TIER)
      sed -i '/^TIER 2:/,/^$/d' "$RESEARCHER"
      # Remove Tier 3 block
      sed -i '/^TIER 3:/,/^$/d' "$RESEARCHER"
      # Remove Context7 tool references
      sed -i '/context7/Id' "$RESEARCHER"
      # Rename Tier 4 to Tier 2
      sed -i 's/TIER 4:/TIER 2:/g' "$RESEARCHER"
      sed -i 's/Tiers 1-3/Tier 1/g' "$RESEARCHER"
      sed -i 's/4-tier search cascade/2-tier search cascade/g' "$RESEARCHER"
      # Clean source references
      sed -i 's|skills-library / Context7 / web|skills-library / web|g' "$RESEARCHER"
      echo "  STRIPPED $tier_refs Tier 2/3/Context7 references"
    fi
  else
    echo "  Already clean (no Tier 2/3 references)"
  fi
else
  echo "  NOT FOUND"
fi
echo ""

# ─────────────────────────────────────────────────────────────
# Step 6: Commit and optionally push
# ─────────────────────────────────────────────────────────────
echo "--- Step 6: Commit & Push ---"

if [ "$MODE" = "dry-run" ]; then
  echo ""
  echo "============================================================"
  echo "  DRY RUN COMPLETE"
  echo "============================================================"
  echo ""
  echo "  Would remove:  $PRIVATE_FILES_REMOVED private files/dirs"
  echo "  Would strip:   $CITATION_COUNT research citations"
  echo "  Would strip:   breadcrumb references"
  echo "  Would strip:   $TIER_REFS_STRIPPED Tier 2/3 references"
  echo "  Would replace: research-improvements.md with stub"
  echo ""
  echo "  To apply:  bash scripts/sanitize-for-publish.sh --execute"
  echo "  To push:   bash scripts/sanitize-for-publish.sh --push"
  echo "============================================================"
  exit 0
fi

# Initialize git in staging, copy from publish branch, commit changes
cd "$STAGING_DIR"

# We need to create a proper git state for committing
# Strategy: clone the repo shallowly, replace contents, commit, push
TEMP_REPO="/tmp/fire-flow-repo"
rm -rf "$TEMP_REPO"

echo "  Preparing git repo for push..."
cd "$PLUGIN_DIR"
git clone --branch "$PUBLISH_BRANCH" --single-branch --depth 1 "." "$TEMP_REPO" 2>/dev/null

# Replace repo contents with sanitized staging
cd "$TEMP_REPO"
# Remove everything except .git
find . -maxdepth 1 -not -name '.git' -not -name '.' -exec rm -rf {} +
# Copy sanitized files in
cp -r "$STAGING_DIR"/. "$TEMP_REPO"/

# Stage all changes
git add -A

# Check if there are changes to commit
if git diff --cached --quiet; then
  echo "  No changes to commit (already sanitized)"
else
  CHANGED=$(git diff --cached --stat | tail -1)
  echo "  Changes: $CHANGED"

  git commit -m "chore: sanitize for public release (automated)"

  if [ "$MODE" = "push" ]; then
    # Set remote to the actual GitHub repo
    git remote set-url origin "https://github.com/ThierryN/fire-flow.git"
    git push origin "$PUBLISH_BRANCH:$REMOTE_BRANCH" --force
    git push origin "$PUBLISH_BRANCH:main" --force
    echo "  Pushed to GitHub (master + main synced)"
  else
    echo "  Committed locally in staging. Use --push to push to GitHub."
  fi
fi

# Cleanup
rm -rf "$STAGING_DIR" "$TEMP_REPO"

echo ""
echo "============================================================"
echo "  SANITIZATION COMPLETE"
echo "============================================================"
echo ""
echo "  Removed:   $PRIVATE_FILES_REMOVED private files/dirs"
echo "  Stripped:  $CITATION_COUNT research citations from $CITATION_FILES files"
echo "  Stripped:  breadcrumb references from $BREADCRUMB_FILES_STRIPPED files"
echo "  Stripped:  $TIER_REFS_STRIPPED Tier 2/3/Context7 references"
echo "  Replaced: research-improvements.md with stub"
echo ""
echo "  Your local working copy was NOT modified."
echo "============================================================"
