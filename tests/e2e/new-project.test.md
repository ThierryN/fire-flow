# E2E Test: /fire-1-new - New Project Initialization

## Test Name
`new-project-initialization`

## Description
Validates that `/fire-1-new` creates the correct directory structure, initializes CONSCIENCE.md and VISION.md with proper formatting, and sets up the project for Dominion Flow workflow.

---

## Prerequisites
- Dominion Flow plugin installed at `~/.claude/plugins/dominion-flow/`
- Claude Code CLI available
- Write permissions to temp directory

---

## Setup Steps

```bash
# 1. Create temp test directory
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"

# 2. Initialize a git repository (optional but recommended)
git init
echo "# Test Project" > README.md
git add .
git commit -m "Initial commit"

# 3. Record starting state
ls -la > /tmp/before-state.txt
```

---

## Execute Steps

```bash
# 1. Run the new project command
# In Claude Code session:
/fire-1-new

# 2. Answer the prompts:
#    - Project name: "Test Dominion Flow Project"
#    - Project description: "A test project for validating Dominion Flow functionality"
#    - Initial phases: "Setup, Implementation, Testing"
```

---

## Verify Steps

### Directory Structure Verification
```bash
# Check .planning directory exists
[ -d ".planning" ] && echo "PASS: .planning exists" || echo "FAIL: .planning missing"

# Check .planning/phases directory exists
[ -d ".planning/phases" ] && echo "PASS: phases exists" || echo "FAIL: phases missing"

# Check core files exist
[ -f ".planning/CONSCIENCE.md" ] && echo "PASS: CONSCIENCE.md exists" || echo "FAIL: CONSCIENCE.md missing"
[ -f ".planning/VISION.md" ] && echo "PASS: VISION.md exists" || echo "FAIL: VISION.md missing"
```

### CONSCIENCE.md Content Verification
```bash
# Verify CONSCIENCE.md has required sections
grep -q "## Current Phase" .planning/CONSCIENCE.md && echo "PASS: Has Current Phase" || echo "FAIL: Missing Current Phase"
grep -q "## Session Context" .planning/CONSCIENCE.md && echo "PASS: Has Session Context" || echo "FAIL: Missing Session Context"
grep -q "## Active Tasks" .planning/CONSCIENCE.md && echo "PASS: Has Active Tasks" || echo "FAIL: Missing Active Tasks"
grep -q "## Blockers" .planning/CONSCIENCE.md && echo "PASS: Has Blockers" || echo "FAIL: Missing Blockers"
```

### VISION.md Content Verification
```bash
# Verify VISION.md has required sections
grep -q "## Milestone" .planning/VISION.md && echo "PASS: Has Milestone" || echo "FAIL: Missing Milestone"
grep -q "## Phases" .planning/VISION.md && echo "PASS: Has Phases" || echo "FAIL: Missing Phases"
```

### Phase Directory Verification
```bash
# Check at least one phase directory was created
PHASE_COUNT=$(ls -d .planning/phases/*/ 2>/dev/null | wc -l)
[ "$PHASE_COUNT" -ge 1 ] && echo "PASS: Phase directories created ($PHASE_COUNT)" || echo "FAIL: No phase directories"
```

---

## Cleanup Steps

```bash
# Remove temp test directory
cd /
rm -rf "$TEST_DIR"
rm -f /tmp/before-state.txt
```

---

## Pass/Fail Criteria

| Criterion | Required | Description |
|-----------|----------|-------------|
| .planning directory | YES | Must exist at project root |
| .planning/phases directory | YES | Must exist for phase storage |
| CONSCIENCE.md created | YES | Must contain current phase, session context, active tasks, blockers sections |
| VISION.md created | YES | Must contain milestone and phases sections |
| Phase directories | YES | At least one phase directory must be created |
| Git-friendly | NO | Files should not conflict with .gitignore |

## Expected Result
**PASS** if all required criteria are met.

---

## Known Issues
- None currently documented

## Related Tests
- `plan-phase.test.md` - Tests phase planning after project creation
- `full-workflow.test.md` - Tests complete workflow including project creation
