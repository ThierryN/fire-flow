# E2E Test: /fire-4-verify - Phase Verification

## Test Name
`verify-phase-checks`

## Description
Validates that `/fire-4-verify` runs all defined verification steps from the BLUEPRINT.md, checks success criteria, identifies incomplete tasks, and produces a verification report.

---

## Prerequisites
- Fire Flow plugin installed
- Project with completed or partially completed phase execution
- BLUEPRINT.md with defined success criteria and verification steps

---

## Setup Steps

```bash
# 1. Create temp test directory
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"

# 2. Copy test project fixture
cp -r ~/.claude/plugins/fire-flow/tests/fixtures/test-project/.planning .

# 3. Create a completed plan with verification steps
mkdir -p .planning/phases/01-test-phase
cat > .planning/phases/01-test-phase/01-01-BLUEPRINT.md << 'EOF'
# Phase 1: Test Phase - Execution Plan

## Objective
Create basic project structure with configuration files.

## Breaths

### Breath 1: Foundation
- [x] Create src/ directory
- [x] Create tests/ directory
- [x] Initialize package.json

### Breath 2: Configuration
- [x] Create tsconfig.json
- [ ] Create .eslintrc.json  # Intentionally incomplete for testing

## Relevant Skills
- `patterns-standards/project-scaffolding.md`

## Success Criteria
1. src/ and tests/ directories exist
2. package.json is valid JSON with name and version fields
3. tsconfig.json has compilerOptions defined
4. .eslintrc.json has rules defined

## Verification Steps
1. Check directory structure: `ls -la src/ tests/`
2. Validate package.json: `node -e "require('./package.json')"`
3. Validate tsconfig.json: `node -e "require('./tsconfig.json')"`
4. Run type check: `npx tsc --noEmit` (if applicable)
EOF

# 4. Create the artifacts (simulating partial completion)
mkdir -p src tests
cat > package.json << 'EOF'
{
  "name": "test-project",
  "version": "1.0.0"
}
EOF

cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "strict": true
  }
}
EOF

# Note: .eslintrc.json intentionally NOT created to test failure detection

# 5. Update CONSCIENCE.md
cat > .planning/CONSCIENCE.md << 'EOF'
# Project State

## Current Phase
Phase 1: Test Phase (Execution Complete - Pending Verification)

## Session Context
- Execution finished
- Ready for verification

## Active Tasks
- [ ] Verify Phase 1 completion

## Blockers
None

## Last Updated
2026-01-22 11:00:00
EOF
```

---

## Execute Steps

```bash
# 1. Run the verify phase command
# In Claude Code session:
/fire-4-verify 1

# 2. Observe verification process:
#    - Each success criterion checked
#    - Each verification step executed
#    - Report generated
```

---

## Verify Steps

### Verification Report Generated
```bash
# Check verification report exists
VERIFY_FILE=".planning/phases/01-test-phase/01-01-VERIFY.md"
[ -f "$VERIFY_FILE" ] && echo "PASS: Verification report exists" || echo "FAIL: Verification report missing"
```

### Report Structure
```bash
# Check required sections
grep -q "## Verification Summary" "$VERIFY_FILE" && echo "PASS: Has Summary" || echo "FAIL: Missing Summary"
grep -q "## Success Criteria Results" "$VERIFY_FILE" && echo "PASS: Has Criteria Results" || echo "FAIL: Missing Criteria Results"
grep -q "## Verification Step Results" "$VERIFY_FILE" && echo "PASS: Has Step Results" || echo "FAIL: Missing Step Results"
grep -q "## Incomplete Tasks" "$VERIFY_FILE" && echo "PASS: Has Incomplete Tasks" || echo "FAIL: Missing Incomplete Tasks"
```

### Success Criteria Evaluation
```bash
# Check criteria were evaluated
grep -q "src/ and tests/ directories exist.*PASS\|✓" "$VERIFY_FILE" && echo "PASS: Directory check passed" || echo "WARN: Directory check not shown as passed"
grep -q "package.json.*PASS\|✓" "$VERIFY_FILE" && echo "PASS: package.json check passed" || echo "WARN: package.json check not shown"
grep -q "eslintrc.*FAIL\|✗\|missing" "$VERIFY_FILE" && echo "PASS: eslintrc failure detected" || echo "FAIL: eslintrc failure not detected"
```

### Incomplete Task Detection
```bash
# Check incomplete tasks are listed
grep -q "Create .eslintrc.json" "$VERIFY_FILE" && echo "PASS: Incomplete task listed" || echo "FAIL: Incomplete task not listed"
```

### Overall Status
```bash
# Check overall pass/fail status
grep -q "INCOMPLETE\|PARTIAL\|FAIL" "$VERIFY_FILE" && echo "PASS: Correct status (not fully passing)" || echo "FAIL: Wrong status reported"
```

### CONSCIENCE.md Updated
```bash
# Check CONSCIENCE.md reflects verification results
grep -q "verification\|incomplete\|blocker" .planning/CONSCIENCE.md && echo "PASS: CONSCIENCE.md updated" || echo "WARN: CONSCIENCE.md may not be updated"
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
| Verification report created | YES | VERIFY.md file exists |
| Summary section | YES | High-level pass/fail summary |
| Criteria results section | YES | Each criterion evaluated |
| Step results section | YES | Each verification step result |
| Incomplete tasks listed | YES | Missing tasks identified |
| Passing criteria marked | YES | Completed items show pass |
| Failing criteria marked | YES | Incomplete items show fail |
| Overall status accurate | YES | Reflects actual completion state |
| CONSCIENCE.md updated | YES | Blockers/issues reflected |

## Expected Result
**PASS** if all required criteria are met. The phase should be marked as INCOMPLETE due to missing .eslintrc.json.

---

## Test Variations

### Variation A: Fully Complete Phase
- All tasks marked [x]
- All artifacts exist
- Should report COMPLETE/PASS

### Variation B: Verification Step Fails
- Artifact exists but validation fails (e.g., invalid JSON)
- Should report specific failure reason

### Variation C: No Verification Steps Defined
- BLUEPRINT.md lacks Verification Steps section
- Should use default checks (task completion only)

---

## Known Issues
- Complex verification steps may require manual interpretation
- Some checks may need specific tooling (e.g., TypeScript compiler)

## Related Tests
- `execute-phase.test.md` - Creates state for verification
- `handoff.test.md` - Handoff should include verification results
