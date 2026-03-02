# E2E Test: /fire-2-plan - Phase Planning

## Test Name
`plan-phase-generation`

## Description
Validates that `/fire-2-plan` generates valid execution plans that integrate relevant skills from the skills library, include breath-based task organization, and produce actionable BLUEPRINT.md files.

---

## Prerequisites
- Dominion Flow plugin installed
- Existing project with `.planning/` structure
- Skills library available at `~/.claude/plugins/dominion-flow/skills-library/`

---

## Setup Steps

```bash
# 1. Create temp test directory
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"

# 2. Copy test project fixture
cp -r ~/.claude/plugins/dominion-flow/tests/fixtures/test-project/.planning .

# 3. Create a phase directory for testing
mkdir -p .planning/phases/02-database-setup

# 4. Update CONSCIENCE.md to point to phase 2
cat > .planning/CONSCIENCE.md << 'EOF'
# Project State

## Current Phase
Phase 2: Database Setup

## Session Context
- Starting phase planning for database setup
- Need to select appropriate database solution

## Active Tasks
- [ ] Plan database architecture
- [ ] Select ORM/query builder
- [ ] Design schema

## Blockers
None

## Last Updated
2026-01-22 10:00:00
EOF
```

---

## Execute Steps

```bash
# 1. Run the plan phase command
# In Claude Code session:
/fire-2-plan 2

# 2. If prompted, provide context:
#    - "Setting up PostgreSQL database with Prisma ORM"
#    - "Need user authentication tables"
```

---

## Verify Steps

### Plan File Existence
```bash
# Check BLUEPRINT.md was created
PLAN_FILE=".planning/phases/02-database-setup/02-01-BLUEPRINT.md"
[ -f "$PLAN_FILE" ] && echo "PASS: BLUEPRINT.md exists" || echo "FAIL: BLUEPRINT.md missing"
```

### Plan Structure Verification
```bash
# Check required sections exist
grep -q "## Objective" "$PLAN_FILE" && echo "PASS: Has Objective" || echo "FAIL: Missing Objective"
grep -q "## Breaths" "$PLAN_FILE" && echo "PASS: Has Breaths" || echo "FAIL: Missing Breaths"
grep -q "## Relevant Skills" "$PLAN_FILE" && echo "PASS: Has Relevant Skills" || echo "FAIL: Missing Relevant Skills"
grep -q "## Success Criteria" "$PLAN_FILE" && echo "PASS: Has Success Criteria" || echo "FAIL: Missing Success Criteria"
grep -q "## Verification Steps" "$PLAN_FILE" && echo "PASS: Has Verification Steps" || echo "FAIL: Missing Verification Steps"
```

### Breath Structure Verification
```bash
# Check breaths are properly formatted
grep -q "### Breath 1" "$PLAN_FILE" && echo "PASS: Has Breath 1" || echo "FAIL: Missing Breath 1"

# Check tasks have checkboxes
grep -q "\- \[ \]" "$PLAN_FILE" && echo "PASS: Has task checkboxes" || echo "FAIL: Missing task checkboxes"
```

### Skills Integration Verification
```bash
# Check that relevant skills were identified
grep -q "database" "$PLAN_FILE" && echo "PASS: Database skills referenced" || echo "FAIL: No database skills"

# Check skills have file paths
grep -q "skills-library/" "$PLAN_FILE" && echo "PASS: Skills paths included" || echo "FAIL: No skills paths"
```

### CONSCIENCE.md Update Verification
```bash
# Check CONSCIENCE.md was updated
grep -q "Planning complete" .planning/CONSCIENCE.md || grep -q "02-01-PLAN" .planning/CONSCIENCE.md && echo "PASS: CONSCIENCE.md updated" || echo "FAIL: CONSCIENCE.md not updated"
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
| BLUEPRINT.md created | YES | Must exist in phase directory |
| Objective section | YES | Clear description of phase goal |
| Breaths section | YES | Tasks organized into execution breaths |
| Breath 1 exists | YES | At least one breath defined |
| Task checkboxes | YES | Tasks use `- [ ]` format |
| Relevant Skills section | YES | Skills from library identified |
| Skills paths | YES | Full paths to skill files included |
| Success Criteria | YES | Measurable completion criteria |
| Verification Steps | YES | Steps to verify completion |
| CONSCIENCE.md updated | YES | Current state reflects planning |

## Expected Result
**PASS** if all required criteria are met.

---

## Test Variations

### Variation A: Empty Skills Library
- Remove skills library temporarily
- Verify plan still generates (without skills section)
- Should log warning about missing skills

### Variation B: Multiple Matching Skills
- Phase: "API Development"
- Should find and list multiple relevant skills
- Skills should be prioritized by relevance

---

## Known Issues
- Skills matching may be keyword-based; semantic matching is a future enhancement

## Related Tests
- `new-project.test.md` - Prerequisites for this test
- `execute-phase.test.md` - Tests execution of generated plans
- `skills-search.test.md` - Tests skills search independently
