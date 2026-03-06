#!/bin/bash
# MIT License - Copyright (c) 2026 ThierryN - https://github.com/ThierryN/dominion-flow
#
# Universal hook launcher — works on macOS, Linux, and Windows (Git Bash / WSL)

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
exec bash "$HOOK_DIR/session-end.sh"
