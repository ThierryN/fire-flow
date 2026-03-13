# E2E Test: /fire-3-execute - Phase Execution

## Test Name
`execute-phase-breaths`

## Description
Validates that `/fire-3-execute` properly executes tasks in breath order, updates task checkboxes as completed, handles parallel task execution within breaths, and updates CONSCIENCE.md with progress.

---

## Prerequisites
- Dominion Flow plugin installed
- Project with existing BLUEPRINT.md containing defined breaths
- Test fixtures available

---

## Setup Steps

```bash
# 1. Create temp test directory
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"

# 2. Copy test project fixture
cp -r ~/.claude/plugins/dominion-flow/tests/fixtures/test-project/.planning .

# 3. Create a plan with executable tasks
mkdir -p .planning/phases/01-test-phase
cat > .planning/phases/01-test-phase/01-01-BLUEPRINT.md << 'EOF'
# Phase 1: Test Phase - Execution Plan

## Objective
Create basic project structure with configuration files.

## Breaths

### Breath 1: Foundation (Parallel)
- [ ] Create src/ directory
- [ ] Create tests/ directory
- [ ] Initialize package.json

### Breath 2: Configuration (Sequential - depends on Breath 1)
- [ ] Create tsconfig.json
- [ ] Create .eslintrc.json

### Breath 3: Documentation (Parallel)
- [ ] Create README.md
- [ ] Create CONTRIBUTING.md

## Relevant Skills
- `patterns-standards/project-scaffolding.md`

## Success Criteria
- All directories created
- All configuration files present
- All documentation files present

## Verification Steps
1. Run `ls -la` to verify directory structure
2. Validate JSON files are parseable
3. Check markdown files have content
EOF

# 4. Update CONSCIENCE.md
cat > .planning/CONSCIENCE.md << 'EOF'
# Project State

## Current Phase
Phase 1: Test Phase

## Session Context
- Plan ready for execution
- Starting Breath 1

## Active Tasks
- [ ] Execute Breath 1
- [ ] Execute Breath 2
- [ ] Execute Breath 3

## Blockers
None

## Last Updated
2026-01-22 10:00:00
EOF
```

---

## Execute Steps

```bash
# 1. Run the execute phase command
# In Claude Code session:
/fire-3-execute 1

# 2. Observe breath execution:
#    - Breath 1 tasks should run in parallel
#    - Breath 2 should wait for Breath 1 completion
#    - Breath 3 tasks should run in parallel
```

---

## Verify Steps

### Breath 1 Completion
```bash
# Check Breath 1 tasks are marked complete in BLUEPRINT.md
PLAN_FILE=".planning/phases/01-test-phase/01-01-BLUEPRINT.md"

grep -q "\[x\] Create src/ directory" "$PLAN_FILE" && echo "PASS: src/ task complete" || echo "FAIL: src/ task incomplete"
grep -q "\[x\] Create tests/ directory" "$PLAN_FILE" && echo "PASS: tests/ task complete" || echo "FAIL: tests/ task incomplete"
grep -q "\[x\] Initialize package.json" "$PLAN_FILE" && echo "PASS: package.json task complete" || echo "FAIL: package.json task incomplete"

# Verify artifacts exist
[ -d "src" ] && echo "PASS: src/ directory exists" || echo "FAIL: src/ directory missing"
[ -d "tests" ] && echo "PASS: tests/ directory exists" || echo "FAIL: tests/ directory missing"
[ -f "package.json" ] && echo "PASS: package.json exists" || echo "FAIL: package.json missing"
```

### Breath 2 Completion
```bash
# Check Breath 2 tasks
grep -q "\[x\] Create tsconfig.json" "$PLAN_FILE" && echo "PASS: tsconfig.json task complete" || echo "FAIL: tsconfig.json task incomplete"
grep -q "\[x\] Create .eslintrc.json" "$PLAN_FILE" && echo "PASS: .eslintrc.json task complete" || echo "FAIL: .eslintrc.json task incomplete"

# Verify artifacts
[ -f "tsconfig.json" ] && echo "PASS: tsconfig.json exists" || echo "FAIL: tsconfig.json missing"
[ -f ".eslintrc.json" ] && echo "PASS: .eslintrc.json exists" || echo "FAIL: .eslintrc.json missing"
```

### Breath 3 Completion
```bash
# Check Breath 3 tasks
grep -q "\[x\] Create README.md" "$PLAN_FILE" && echo "PASS: README.md task complete" || echo "FAIL: README.md task incomplete"
grep -q "\[x\] Create CONTRIBUTING.md" "$PLAN_FILE" && echo "PASS: CONTRIBUTING.md task complete" || echo "FAIL: CONTRIBUTING.md task incomplete"

# Verify artifacts
[ -f "README.md" ] && echo "PASS: README.md exists" || echo "FAIL: README.md missing"
[ -f "CONTRIBUTING.md" ] && echo "PASS: CONTRIBUTING.md exists" || echo "FAIL: CONTRIBUTING.md missing"
```

### CONSCIENCE.md Progress Update
```bash
# Check CONSCIENCE.md reflects completion
grep -q "Phase 1.*complete\|completed\|done" .planning/CONSCIENCE.md && echo "PASS: Phase marked complete" || echo "WARN: Phase completion not marked"

# Check active tasks updated
grep -q "\[x\] Execute Breath" .planning/CONSCIENCE.md && echo "PASS: Breath tasks marked complete" || echo "WARN: Breath tasks not marked"
```

### Execution Order Verification
```bash
# Check execution log if available
if [ -f ".planning/phases/01-test-phase/execution.log" ]; then
    # Breath 2 should appear after Breath 1
    WAVE1_LINE=$(grep -n "Breath 1" .planning/phases/01-test-phase/execution.log | head -1 | cut -d: -f1)
    WAVE2_LINE=$(grep -n "Breath 2" .planning/phases/01-test-phase/execution.log | head -1 | cut -d: -f1)
    [ "$WAVE2_LINE" -gt "$WAVE1_LINE" ] && echo "PASS: Breath order correct" || echo "FAIL: Breath order incorrect"
fi
```

---

## Cleanup Steps

```bash
# Remove temp test directory
cd /
rm -rf "$TEST_DIR"
```

---

## Pass/Fail Criteria

| Criterion | Required | Description |
|-----------|----------|-------------|
| Breath 1 tasks marked [x] | YES | All Breath 1 checkboxes updated |
| Breath 1 artifacts created | YES | Directories and files exist |
| Breath 2 tasks marked [x] | YES | All Breath 2 checkboxes updated |
| Breath 2 artifacts created | YES | Config files exist and valid |
| Breath 3 tasks marked [x] | YES | All Breath 3 checkboxes updated |
| Breath 3 artifacts created | YES | Documentation files exist |
| CONSCIENCE.md updated | YES | Progress reflected in state |
| Breath order respected | YES | Sequential breaths wait for dependencies |
| Parallel execution | NO | Tasks within breath run in parallel (optimization) |

## Expected Result
**PASS** if all required criteria are met.

---

## Test Variations

### Variation A: Partial Execution
- Interrupt after Breath 1
- Resume with `/fire-3-execute 1`
- Should continue from Breath 2

### Variation B: Failed Task
- Simulate task failure
- Verify error handling
- CONSCIENCE.md should reflect blocker

### Variation C: Empty Breath
- Plan with empty Breath 2
- Should skip to Breath 3 gracefully

---

## Known Issues
- Parallel execution depends on Claude Code's ability to run concurrent tool calls
- Very long-running tasks may timeout

## Related Tests
- `plan-phase.test.md` - Creates plans for execution
- `verify-phase.test.md` - Validates execution results
- `resume.test.md` - Tests resuming interrupted execution
