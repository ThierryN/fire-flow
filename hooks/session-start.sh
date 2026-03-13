#!/bin/bash
# MIT License - Copyright (c) 2026 ThierryN - https://github.com/ThierryN/dominion-flow
#
# Dominion Flow Plugin - Session Start Hook
#
# WHAT THIS DOES:
#   Every time a Claude Code session starts, this script runs automatically.
#   It looks for two things and prints them into the session context:
#     1. The project's CONSCIENCE.md — a living summary of where the project is right now
#     2. The most recent WARRIOR handoff file — Claude's notes from the last session
#
# WHY THIS MATTERS:
#   Claude has no memory between sessions by default. This hook is what gives
#   Claude its "memory" — it re-injects the previous session's context so Claude
#   can pick up exactly where it left off without you having to explain anything.

echo "=============================================="
echo "  DOMINION FLOW - Session Context Injection"
echo "=============================================="
echo ""

# Get the current working directory (project root)
PROJECT_ROOT="$(pwd)"

# Define WARRIOR handoffs directory
WARRIOR_HANDOFFS="$HOME/.claude/warrior-handoffs"

# =============================================
# 1. Check for .planning/CONSCIENCE.md in project
# =============================================
STATE_FILE="$PROJECT_ROOT/.planning/CONSCIENCE.md"

if [ -f "$STATE_FILE" ]; then
    echo ">>> PROJECT STATE DETECTED <<<"
    echo "Location: $STATE_FILE"
    echo "----------------------------------------------"
    cat "$STATE_FILE"
    echo ""
    echo "----------------------------------------------"
    echo ""
else
    echo "[INFO] No .planning/CONSCIENCE.md found in current project."
    echo "       Path checked: $STATE_FILE"
    echo ""
fi

# =============================================
# 2. Check for WARRIOR Handoffs
# =============================================
echo ">>> WARRIOR HANDOFF CONTEXT <<<"
echo "Location: $WARRIOR_HANDOFFS"
echo ""

if [ -d "$WARRIOR_HANDOFFS" ]; then
    # List recent handoff files (last 5, most recent first)
    HANDOFF_FILES=$(ls -t "$WARRIOR_HANDOFFS"/*.md 2>/dev/null | head -5)

    if [ -n "$HANDOFF_FILES" ]; then
        echo "Recent handoff files:"
        echo "----------------------------------------------"
        for file in $HANDOFF_FILES; do
            FILENAME=$(basename "$file")
            MODIFIED=$(stat -c '%Y' "$file" 2>/dev/null || stat -f '%m' "$file" 2>/dev/null)
            if [ -n "$MODIFIED" ]; then
                # Convert timestamp to readable date
                DATE=$(date -d "@$MODIFIED" '+%Y-%m-%d %H:%M' 2>/dev/null || date -r "$MODIFIED" '+%Y-%m-%d %H:%M' 2>/dev/null || echo "unknown")
                echo "  - $FILENAME ($DATE)"
            else
                echo "  - $FILENAME"
            fi
        done
        echo ""

        # Get the most recent handoff file
        LATEST_HANDOFF=$(echo "$HANDOFF_FILES" | head -1)

        if [ -f "$LATEST_HANDOFF" ]; then
            LATEST_NAME=$(basename "$LATEST_HANDOFF")
            echo ">>> LATEST HANDOFF: $LATEST_NAME <<<"
            echo "----------------------------------------------"

            # Output first 100 lines or full file if shorter
            head -100 "$LATEST_HANDOFF"

            # Check if file was truncated
            TOTAL_LINES=$(wc -l < "$LATEST_HANDOFF")
            if [ "$TOTAL_LINES" -gt 100 ]; then
                echo ""
                echo "... [Truncated - $TOTAL_LINES total lines] ..."
                echo "Use: Read tool on $LATEST_HANDOFF for full content"
            fi
            echo ""
            echo "----------------------------------------------"
        fi
    else
        echo "[INFO] No handoff files found in $WARRIOR_HANDOFFS"
    fi
else
    echo "[INFO] WARRIOR handoffs directory not found: $WARRIOR_HANDOFFS"
fi

echo ""
echo "=============================================="
echo "  SESSION CONTEXT INJECTION COMPLETE"
echo "=============================================="
echo ""
echo "RECOMMENDED ACTIONS:"
echo "  1. Review CONSCIENCE.md for current project phase"
echo "  2. Check latest WARRIOR handoff for pending tasks"
echo "  3. Use /fire-dashboard to see project status"
echo ""
