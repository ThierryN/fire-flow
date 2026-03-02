# Integration Test: Full Workflow - End-to-End

## Test Name
`full-workflow-e2e`

## Description
Validates the complete Dominion Flow workflow from project initialization through to completion, including all major commands in sequence: new project, planning, execution, verification, and handoff.

---

## Prerequisites
- Dominion Flow plugin installed and configured
- Claude Code CLI available
- Skills library populated
- Write permissions to test directories
- Network access (for any external validations)

---

## Setup Steps

```bash
# 1. Create isolated test directory
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"
echo "Test directory: $TEST_DIR"

# 2. Initialize git repository
git init
git config user.email "test@example.com"
git config user.name "Test User"

# 3. Create initial README
echo "# Integration Test Project" > README.md
git add .
git commit -m "Initial commit"

# 4. Record test start time
START_TIME=$(date +%s)
echo "Test started at: $(date)"

# 5. Clear any existing handoffs for this test
rm -f "$HOME/.claude/warrior-handoffs/INTEGRATION-TEST_*.md"
```

---

## Execute Steps

### Step 1: Initialize Project with /fire-1-new
```bash
# In Claude Code session:
/fire-1-new

# Inputs:
#   - Project name: "Integration Test Project"
#   - Description: "End-to-end test of Dominion Flow workflow"
#   - Initial phases:
#     1. Setup - Create basic structure
#     2. Implementation - Add core features
#     3. Testing - Validate functionality

# Expected outputs:
#   - .planning/ directory created
#   - CONSCIENCE.md initialized
#   - VISION.md with 3 phases
#   - Phase directories created
```

### Step 2: Plan Phase 1 with /fire-2-plan
```bash
# In Claude Code session:
/fire-2-plan 1

# Context provided:
#   - "Create basic Node.js project structure"
#   - "Include TypeScript configuration"
#   - "Set up ESLint and Prettier"

# Expected outputs:
#   - .planning/phases/01-setup/01-01-BLUEPRINT.md created
#   - Breaths defined (at least 2)
#   - Relevant skills identified
#   - Success criteria defined
```

### Step 3: Execute Phase 1 with /fire-3-execute
```bash
# In Claude Code session:
/fire-3-execute 1

# Expected behaviors:
#   - Breath 1 tasks executed
#   - Breath 2 tasks executed after Breath 1 completes
#   - Task checkboxes updated to [x]
#   - Files/directories created as specified

# Expected outputs:
#   - package.json created
#   - tsconfig.json created
#   - src/ directory created
#   - CONSCIENCE.md updated with progress
```

### Step 4: Verify Phase 1 with /fire-4-verify
```bash
# In Claude Code session:
/fire-4-verify 1

# Expected behaviors:
#   - Each success criterion checked
#   - Verification steps executed
#   - Report generated

# Expected outputs:
#   - .planning/phases/01-setup/01-01-VERIFY.md created
#   - All criteria passing (if execution successful)
#   - CONSCIENCE.md updated
```

### Step 5: Plan and Execute Phase 2 (Abbreviated)
```bash
# In Claude Code session:
/fire-2-plan 2
# Quick plan for implementation phase

/fire-3-execute 2
# Execute implementation tasks
```

### Step 6: Create Handoff with /fire-5-handoff
```bash
# In Claude Code session:
/fire-5-handoff

# Expected outputs:
#   - Handoff file in ~/.claude/warrior-handoffs/
#   - Contains project state
#   - Contains progress summary
#   - Contains next steps
```

### Step 7: Simulate New Session with /fire-6-resume
```bash
# Close and reopen Claude Code session (or simulate)
# In new Claude Code session:
cd "$TEST_DIR"
/fire-6-resume

# Expected behaviors:
#   - Handoff located and loaded
#   - Context restored
#   - Ready to continue Phase 2 or start Phase 3
```

---

## Verify Steps

### Overall Workflow Verification

```bash
# 1. Check project structure created
echo "=== Project Structure ==="
ls -la .planning/
ls -la .planning/phases/

# 2. Check CONSCIENCE.md exists and has content
echo "=== CONSCIENCE.md ==="
[ -f ".planning/CONSCIENCE.md" ] && echo "PASS: CONSCIENCE.md exists" || echo "FAIL: CONSCIENCE.md missing"
wc -l .planning/CONSCIENCE.md

# 3. Check VISION.md exists and has phases
echo "=== VISION.md ==="
[ -f ".planning/VISION.md" ] && echo "PASS: VISION.md exists" || echo "FAIL: VISION.md missing"
grep -c "Phase" .planning/VISION.md

# 4. Check Phase 1 plan and verification
echo "=== Phase 1 Artifacts ==="
[ -f ".planning/phases/01-setup/01-01-BLUEPRINT.md" ] && echo "PASS: Phase 1 plan exists" || echo "FAIL: Phase 1 plan missing"
[ -f ".planning/phases/01-setup/01-01-VERIFY.md" ] && echo "PASS: Phase 1 verify exists" || echo "FAIL: Phase 1 verify missing"

# 5. Check handoff was created
echo "=== Handoff ==="
HANDOFF_COUNT=$(ls -1 "$HOME/.claude/warrior-handoffs/INTEGRATION-TEST_"* 2>/dev/null | wc -l)
[ "$HANDOFF_COUNT" -ge 1 ] && echo "PASS: Handoff created ($HANDOFF_COUNT files)" || echo "FAIL: No handoff found"

# 6. Check execution artifacts
echo "=== Execution Artifacts ==="
[ -f "package.json" ] && echo "PASS: package.json created" || echo "FAIL: package.json missing"
[ -d "src" ] && echo "PASS: src/ directory created" || echo "FAIL: src/ missing"
```

### Timing Verification
```bash
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "Total test duration: ${DURATION} seconds"

# Workflow should complete in reasonable time
[ "$DURATION" -lt 600 ] && echo "PASS: Completed within 10 minutes" || echo "WARN: Took longer than expected"
```

### State Consistency Verification
```bash
# Check CONSCIENCE.md reflects actual progress
echo "=== State Consistency ==="

# Should reference Phase 1 as complete (or Phase 2 in progress)
grep -q "Phase 1\|Phase 2" .planning/CONSCIENCE.md && echo "PASS: Phase tracking present" || echo "FAIL: No phase tracking"

# Should have no orphan tasks (tasks in STATE that don't exist)
# (This is a manual check - verify CONSCIENCE.md tasks match actual work)
```

---

## Cleanup Steps

```bash
# 1. Remove test directory
cd /
rm -rf "$TEST_DIR"

# 2. Remove test handoff files
rm -f "$HOME/.claude/warrior-handoffs/INTEGRATION-TEST_"*.md

# 3. Verify cleanup
[ ! -d "$TEST_DIR" ] && echo "Test directory removed"
```

---

## Pass/Fail Criteria

| Step | Criterion | Required |
|------|-----------|----------|
| 1 | Project initialized | YES |
| 1 | CONSCIENCE.md created | YES |
| 1 | VISION.md created | YES |
| 1 | Phase directories created | YES |
| 2 | BLUEPRINT.md generated | YES |
| 2 | Breaths defined | YES |
| 3 | Tasks executed | YES |
| 3 | Checkboxes updated | YES |
| 3 | Artifacts created | YES |
| 4 | VERIFY.md generated | YES |
| 4 | Criteria evaluated | YES |
| 5 | Phase 2 planned | NO |
| 6 | Handoff created | YES |
| 6 | Handoff has all sections | YES |
| 7 | Context restored | YES |
| 7 | Ready to continue | YES |
| - | Total time < 10 min | NO |

## Expected Result
**PASS** if all required criteria are met across all workflow steps.

---

## Workflow Diagram

```
┌─────────────────┐
│  /fire-1-new   │  Project Initialization
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  /fire-2-plan  │  Phase Planning
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ /fire-3-execute│  Phase Execution
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ /fire-4-verify │  Phase Verification
└────────┬────────┘
         │
    ┌────┴────┐
    │ More    │
    │ Phases? │
    └────┬────┘
         │ No
         ▼
┌─────────────────┐
│/fire-5-handoff │  Session Handoff
└────────┬────────┘
         │
    [New Session]
         │
         ▼
┌─────────────────┐
│ /fire-6-resume │  Context Restoration
└─────────────────┘
```

---

## Test Variations

### Variation A: Multi-Phase Completion
- Complete all 3 phases
- Verify VISION.md shows 100% complete
- Final handoff reflects project completion

### Variation B: Interrupted Workflow
- Stop mid-execution
- Create handoff
- Resume and verify context restoration
- Complete remaining work

### Variation C: Parallel Phase Work
- Work on Phase 2 and Phase 3 simultaneously (if independent)
- Verify state tracks multiple active phases

---

## Known Issues
- Long-running executions may timeout
- Complex projects may need multiple sessions
- Network-dependent tasks may fail in isolated environments

## Related Tests
- All E2E tests (individual command validation)
- `skills-sync.test.md` (skills integration)
- `hooks.test.md` (SessionStart integration)
