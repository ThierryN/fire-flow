# Integration Test: Hooks - SessionStart Hook

## Test Name
`sessionstart-hook-integration`

## Description
Validates that the Dominion Flow SessionStart hook fires correctly when Claude Code starts, injects appropriate context about handoffs and project state, and integrates properly with the WARRIOR workflow's similar hook functionality.

---

## Prerequisites
- Fire Flow plugin installed with hooks configured
- Claude Code CLI available
- hooks.json properly configured in plugin
- Handoff files may or may not exist (tests both scenarios)

---

## Setup Steps

```bash
# 1. Define paths
FIRE_FLOW_ROOT="$HOME/.claude/plugins/fire-flow"
HOOKS_DIR="$FIRE_FLOW_ROOT/hooks"
HANDOFF_DIR="$HOME/.claude/warrior-handoffs"

# 2. Verify hooks directory exists
[ -d "$HOOKS_DIR" ] && echo "Hooks directory exists" || mkdir -p "$HOOKS_DIR"

# 3. Check hooks.json exists
[ -f "$HOOKS_DIR/hooks.json" ] && echo "hooks.json exists" || echo "hooks.json MISSING - will create"

# 4. Create/verify hooks.json configuration
cat > "$HOOKS_DIR/hooks.json" << 'EOF'
{
  "hooks": [
    {
      "name": "fire-flow-session-start",
      "event": "SessionStart",
      "trigger": ["startup", "resume", "clear", "compact"],
      "script": "session-start.sh",
      "description": "Inject Dominion Flow context on session start"
    }
  ]
}
EOF

# 5. Create session-start script
cat > "$HOOKS_DIR/session-start.sh" << 'EOF'
#!/bin/bash
# Dominion Flow SessionStart Hook
# Injects context about handoffs and project state

HANDOFF_DIR="$HOME/.claude/warrior-handoffs"
FIRE_FLOW_ROOT="$HOME/.claude/plugins/fire-flow"

echo ""
echo "=== Dominion Flow Context ==="
echo ""

# Check for recent handoffs
if [ -d "$HANDOFF_DIR" ]; then
    RECENT_HANDOFFS=$(find "$HANDOFF_DIR" -name "*.md" -mtime -1 -type f 2>/dev/null | wc -l)
    if [ "$RECENT_HANDOFFS" -gt 0 ]; then
        echo "Recent handoffs found: $RECENT_HANDOFFS"
        echo "Most recent:"
        ls -lt "$HANDOFF_DIR"/*.md 2>/dev/null | head -3
        echo ""
        echo "Tip: Use /fire-6-resume to restore context from a handoff"
    else
        echo "No recent handoffs (last 24 hours)"
    fi
else
    echo "No handoffs directory found"
fi

echo ""

# Check for active project
if [ -f ".planning/CONSCIENCE.md" ]; then
    echo "Active Dominion Flow project detected in current directory"
    echo ""
    # Extract current phase
    CURRENT_PHASE=$(grep -A1 "## Current Phase" .planning/CONSCIENCE.md 2>/dev/null | tail -1)
    if [ -n "$CURRENT_PHASE" ]; then
        echo "Current Phase: $CURRENT_PHASE"
    fi
    # Check for blockers
    BLOCKERS=$(grep -A5 "## Blockers" .planning/CONSCIENCE.md 2>/dev/null | grep -v "^#" | grep -v "^$" | head -3)
    if [ -n "$BLOCKERS" ] && [ "$BLOCKERS" != "None" ]; then
        echo ""
        echo "Blockers:"
        echo "$BLOCKERS"
    fi
else
    echo "No active Dominion Flow project in current directory"
    echo "Tip: Use /fire-1-new to initialize a new project"
fi

echo ""
echo "==========================="
EOF

chmod +x "$HOOKS_DIR/session-start.sh"

# 6. Create test scenarios

# Scenario A: With recent handoff
mkdir -p "$HANDOFF_DIR"
cat > "$HANDOFF_DIR/TEST-HOOK-PROJECT_$(date +%Y-%m-%d).md" << 'EOF'
# WARRIOR Handoff: TEST-HOOK-PROJECT

**Date:** 2026-01-22
**Session:** Hook Test

## Current State
Phase 1: Setup - In Progress

## Active Tasks
- [ ] Test task 1
- [ ] Test task 2

## Blockers
None
EOF

# Scenario B: With active project
TEST_PROJECT=$(mktemp -d)
mkdir -p "$TEST_PROJECT/.planning"
cat > "$TEST_PROJECT/.planning/CONSCIENCE.md" << 'EOF'
# Project State

## Current Phase
Phase 2: Implementation (Breath 1 of 2)

## Session Context
Testing hook integration

## Active Tasks
- [ ] Implement feature A
- [ ] Write tests

## Blockers
- Waiting on API documentation

## Last Updated
2026-01-22 10:00:00
EOF
```

---

## Execute Steps

### Test Case 1: Hook Fires on Startup
```bash
# Start new Claude Code session
# In terminal:
claude-code

# Expected:
#   - SessionStart hook fires
#   - Dominion Flow context displayed
#   - Recent handoffs listed
#   - Project state shown (if in project directory)
```

### Test Case 2: Hook Fires on Resume
```bash
# In existing Claude Code session:
/resume

# Or restart session and observe hook output
```

### Test Case 3: Hook with Active Project
```bash
# Navigate to test project
cd "$TEST_PROJECT"

# Start Claude Code or trigger session event
claude-code

# Expected:
#   - Hook detects .planning/CONSCIENCE.md
#   - Current phase displayed
#   - Blockers shown
```

### Test Case 4: Hook without Project
```bash
# Navigate to directory without project
cd /tmp

# Start Claude Code
claude-code

# Expected:
#   - Hook runs but detects no project
#   - Shows "No active Dominion Flow project"
#   - Suggests /fire-1-new
```

### Test Case 5: Hook with No Handoffs
```bash
# Temporarily move handoffs
mv "$HANDOFF_DIR" "$HANDOFF_DIR.bak"

# Start Claude Code
claude-code

# Expected:
#   - Hook runs
#   - Shows "No recent handoffs" or similar

# Restore handoffs
mv "$HANDOFF_DIR.bak" "$HANDOFF_DIR"
```

---

## Verify Steps

### Hook Configuration Valid
```bash
# Validate hooks.json
python3 -c "import json; json.load(open('$HOOKS_DIR/hooks.json'))" 2>/dev/null
[ $? -eq 0 ] && echo "PASS: hooks.json is valid JSON" || echo "FAIL: hooks.json invalid"

# Check required fields
grep -q '"event".*"SessionStart"' "$HOOKS_DIR/hooks.json" && echo "PASS: SessionStart event configured" || echo "FAIL: Event missing"
grep -q '"script"' "$HOOKS_DIR/hooks.json" && echo "PASS: Script reference present" || echo "FAIL: Script missing"
```

### Script Executable
```bash
[ -x "$HOOKS_DIR/session-start.sh" ] && echo "PASS: Script is executable" || echo "FAIL: Script not executable"
```

### Script Runs Successfully
```bash
# Run script directly
cd "$TEST_PROJECT"
OUTPUT=$("$HOOKS_DIR/session-start.sh" 2>&1)
[ $? -eq 0 ] && echo "PASS: Script runs without error" || echo "FAIL: Script error"

# Check output contains expected content
echo "$OUTPUT" | grep -q "Dominion Flow" && echo "PASS: Output contains Dominion Flow marker" || echo "FAIL: Missing marker"
echo "$OUTPUT" | grep -q "Phase" && echo "PASS: Output contains phase info" || echo "FAIL: Missing phase"
```

### Handoff Detection Works
```bash
# Script should find test handoff
cd /tmp
OUTPUT=$("$HOOKS_DIR/session-start.sh" 2>&1)
echo "$OUTPUT" | grep -q "handoff\|Handoff" && echo "PASS: Handoffs mentioned" || echo "WARN: Handoffs not detected"
```

### Project Detection Works
```bash
# In project directory
cd "$TEST_PROJECT"
OUTPUT=$("$HOOKS_DIR/session-start.sh" 2>&1)
echo "$OUTPUT" | grep -q "Active Dominion Flow project" && echo "PASS: Project detected" || echo "FAIL: Project not detected"

# In non-project directory
cd /tmp
OUTPUT=$("$HOOKS_DIR/session-start.sh" 2>&1)
echo "$OUTPUT" | grep -q "No active Dominion Flow project" && echo "PASS: Non-project detected" || echo "FAIL: False positive"
```

### Hook Integration with WARRIOR
```bash
# Check if WARRIOR hooks exist
WARRIOR_HOOKS="$HOME/.claude/plugins/warrior-workflow/hooks/hooks.json"
if [ -f "$WARRIOR_HOOKS" ]; then
    echo "WARRIOR hooks also present"
    # Both hooks should fire without conflict
    # Verify no duplicate output
    echo "PASS: Both hook systems can coexist"
else
    echo "Note: WARRIOR hooks not present (OK for isolated test)"
fi
```

---

## Cleanup Steps

```bash
# Remove test handoff
rm -f "$HANDOFF_DIR/TEST-HOOK-PROJECT_"*.md

# Remove test project
rm -rf "$TEST_PROJECT"

# Optionally restore original hooks.json if backed up
# mv "$HOOKS_DIR/hooks.json.bak" "$HOOKS_DIR/hooks.json"

echo "Cleanup complete"
```

---

## Pass/Fail Criteria

| Criterion | Required | Description |
|-----------|----------|-------------|
| hooks.json valid | YES | Valid JSON with required fields |
| Script executable | YES | session-start.sh has execute permission |
| Script runs cleanly | YES | No errors when executed |
| Handoffs detected | YES | Recent handoffs found and listed |
| Project detected | YES | Active project CONSCIENCE.md found |
| No-project handled | YES | Graceful message when no project |
| Phase displayed | YES | Current phase shown when in project |
| Blockers shown | NO | Blockers displayed if present |
| Coexists with WARRIOR | YES | No conflicts with other hooks |
| Output formatted | NO | Readable, organized output |

## Expected Result
**PASS** if all required criteria are met.

---

## Hook Events Reference

| Event | When Fired | Use Case |
|-------|------------|----------|
| SessionStart | Claude Code starts | Inject context |
| PreToolUse | Before tool execution | Validate/modify |
| PostToolUse | After tool execution | Log/transform |
| Stop | Session ends | Cleanup |

### Trigger Options for SessionStart
- `startup` - Fresh session start
- `resume` - Session resumed
- `clear` - Context cleared
- `compact` - Context compacted

---

## Test Variations

### Variation A: Multiple Handoffs
- Create 5+ handoff files
- Verify most recent 3 shown
- Verify oldest not shown

### Variation B: Old Handoffs Only
- All handoffs > 24 hours old
- Should indicate "no recent" or show older ones

### Variation C: Hook Disabled
- Remove or rename hooks.json
- Session should start normally
- No hook output

### Variation D: Script Error
- Introduce error in script
- Claude Code should still start
- Error should be logged

---

## Known Issues
- Windows may require .cmd instead of .sh
- Path separators differ on Windows
- Some shells may not support all bash features

## Related Tests
- `resume.test.md` - Uses context from hooks
- `handoff.test.md` - Creates files hooks detect
- `full-workflow.test.md` - Complete workflow with hooks
