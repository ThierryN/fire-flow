#!/bin/bash
# MIT License - Copyright (c) 2026 ThierryN - https://github.com/ThierryN/fire-flow
#
# Dominion Flow Plugin - Session End Hook
#
# WHAT THIS DOES:
#   When a Claude Code session ends, this script runs automatically.
#   It tries to consolidate session memory into a vector database (Qdrant)
#   so future sessions can search past experiences semantically.
#
# HOW IT WORKS:
#   1. Checks if a memory project is configured (via DOMINION_MEMORY_PROJECT env var)
#   2. Checks if Qdrant (vector database) is running on port 6335
#   3. Checks if Ollama (local embedding model) is running on port 11434
#   4. If all three are ready, runs "npm run consolidate" to index new files
#
# THIS IS OPTIONAL:
#   If Qdrant or Ollama are not running, this script exits silently (no error).
#   The flat .md handoff files in ~/.claude/warrior-handoffs/ are always intact
#   and used as the fallback. Memory consolidation is a bonus, not a requirement.
#
# NOTE FOR NEW USERS:
#   Set the DOMINION_MEMORY_PROJECT environment variable to point to your
#   vector indexing project. If not set, this hook skips silently.
#   To set up vector memory, see: https://github.com/ThierryN/fire-flow

echo "=============================================="
echo "  DOMINION FLOW - Session End Consolidation"
echo "=============================================="
echo ""

# Set this to the path of your memory/vector indexing project, if you have one.
# If you don't use a memory project, this hook will skip silently.
MEMORY_PROJECT="${DOMINION_MEMORY_PROJECT:-}"

# =============================================
# 1. Check if memory project is configured and exists
# =============================================
if [ -z "$MEMORY_PROJECT" ] || [ ! -d "$MEMORY_PROJECT" ]; then
    echo "[SKIP] Memory project not configured or not found."
    echo "       Set DOMINION_MEMORY_PROJECT env var to enable consolidation."
    echo "       Memory consolidation skipped."
    exit 0
fi

# =============================================
# 2. Check if Qdrant is running (port 6335)
# =============================================
if ! curl -s http://localhost:6335/healthz > /dev/null 2>&1; then
    echo "[SKIP] Qdrant not running on port 6335."
    echo "       Memory consolidation skipped (no vector DB)."
    echo "       Flat .md files are still available."
    exit 0
fi

# =============================================
# 3. Check if Ollama is running
# =============================================
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "[SKIP] Ollama not running."
    echo "       Memory consolidation skipped (no embeddings)."
    exit 0
fi

# =============================================
# 4. Run light consolidation (index new files only)
# =============================================
echo ">>> Running light memory consolidation..."
echo "    (Index new/changed files only — fast, <30s)"
echo ""

cd "$MEMORY_PROJECT" || exit 0

# Run the consolidate command (indexes new files + extracts facts)
npm run consolidate 2>&1 | tail -20

CONSOLIDATE_EXIT=$?

if [ $CONSOLIDATE_EXIT -eq 0 ]; then
    echo ""
    echo ">>> Memory consolidation complete."
else
    echo ""
    echo "[WARN] Consolidation exited with code $CONSOLIDATE_EXIT"
    echo "       This is non-fatal. Memory files are still intact."
fi

echo ""
echo "=============================================="
echo "  SESSION END CONSOLIDATION COMPLETE"
echo "=============================================="
echo ""
