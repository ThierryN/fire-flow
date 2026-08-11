#!/bin/bash
# MIT License - Copyright (c) 2026 ThierryN - https://github.com/ThierryN/fire-flow
#
# Universal hook launcher — works on macOS, Linux, and Windows (Git Bash / WSL)
# Resolves the actual session-start.sh relative to this script's location.

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
exec bash "$HOOK_DIR/session-start.sh"
