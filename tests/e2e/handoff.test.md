# E2E Test: /fire-5-handoff - Session Handoff Creation

## Test Name
`handoff-creation`

## Description
Validates that `/fire-5-handoff` creates a comprehensive handoff document in the unified format, capturing current state, progress, blockers, and context needed for the next AI session.

---

## Prerequisites
- Dominion Flow plugin installed
- Project with active work state
- `.planning/CONSCIENCE.md` contains current context

---

## Setup Steps

```bash
# 1. Create temp test directory
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"

# 2. Copy test project fixture
cp -r ~/.claude/plugins/dominion-flow/tests/fixtures/test-project/.planning .

# 3. Create realistic project state
cat > .planning/CONSCIENCE.md << 'EOF'
# Project State

## Current Phase
Phase 2: API Development (Breath 2 of 3)

## Session Context
- Implemented user authentication endpoints
- Started work on product catalog API
- Using Prisma ORM with PostgreSQL

## Active Tasks
- [x] Create auth middleware
- [x] Implement /api/auth/login
- [x] Implement /api/auth/register
- [ ] Implement /api/products CRUD
- [ ] Add pagination to list endpoints

## Blockers
- Need to decide on pagination strategy (cursor vs offset)
- Rate limiting configuration TBD

## Technical Decisions
- Using JWT tokens with 1-hour expiry
- Refresh tokens stored in HTTP-only cookies
- Zod for request validation

## Files Modified This Session
- server/routes/auth.ts (new)
- server/middleware/auth.ts (new)
- server/services/auth.service.ts (new)
- prisma/schema.prisma (modified)

## Last Updated
2026-01-22 14:30:00
EOF

# 4. Create VISION.md
cat > .planning/VISION.md << 'EOF'
# Project Roadmap

## Milestone 1: MVP Backend

### Phases
1. [x] Phase 1: Database Setup - Complete
2. [ ] Phase 2: API Development - In Progress (60%)
3. [ ] Phase 3: Testing & Documentation
4. [ ] Phase 4: Deployment

## Timeline
- Started: 2026-01-20
- Target: 2026-01-31
EOF

# 5. Create sample BLUEPRINT.md
mkdir -p .planning/phases/02-api-development
cat > .planning/phases/02-api-development/02-01-BLUEPRINT.md << 'EOF'
# Phase 2: API Development

## Breaths
### Breath 1: Authentication (Complete)
- [x] Auth middleware
- [x] Login endpoint
- [x] Register endpoint

### Breath 2: Product Catalog (In Progress)
- [ ] CRUD endpoints
- [ ] Pagination

### Breath 3: Order Management
- [ ] Create order
- [ ] Order history
EOF
```

---

## Execute Steps

```bash
# 1. Run the handoff command
# In Claude Code session:
/fire-5-handoff

# 2. If prompted:
#    - Confirm project name or enter manually
#    - Add any additional context notes
```

---

## Verify Steps

### Handoff File Created
```bash
# Check handoff file exists in global location
HANDOFF_DIR="$HOME/.claude/warrior-handoffs"
TODAY=$(date +%Y-%m-%d)
PROJECT_NAME="test-project"  # Or derived from directory name

# Find today's handoff
HANDOFF_FILE=$(find "$HANDOFF_DIR" -name "*${TODAY}*.md" -type f | head -1)
[ -n "$HANDOFF_FILE" ] && echo "PASS: Handoff file created: $HANDOFF_FILE" || echo "FAIL: No handoff file found"
```

### Handoff Structure (Unified Format)
```bash
# Check required sections exist
grep -q "# WARRIOR Handoff" "$HANDOFF_FILE" && echo "PASS: Has title" || echo "FAIL: Missing title"
grep -q "## Project Overview" "$HANDOFF_FILE" && echo "PASS: Has Project Overview" || echo "FAIL: Missing Project Overview"
grep -q "## Current State" "$HANDOFF_FILE" && echo "PASS: Has Current State" || echo "FAIL: Missing Current State"
grep -q "## Progress Summary" "$HANDOFF_FILE" && echo "PASS: Has Progress Summary" || echo "FAIL: Missing Progress Summary"
grep -q "## Active Tasks" "$HANDOFF_FILE" && echo "PASS: Has Active Tasks" || echo "FAIL: Missing Active Tasks"
grep -q "## Blockers" "$HANDOFF_FILE" && echo "PASS: Has Blockers" || echo "FAIL: Missing Blockers"
grep -q "## Technical Context" "$HANDOFF_FILE" && echo "PASS: Has Technical Context" || echo "FAIL: Missing Technical Context"
grep -q "## Files Modified" "$HANDOFF_FILE" && echo "PASS: Has Files Modified" || echo "FAIL: Missing Files Modified"
grep -q "## Next Steps" "$HANDOFF_FILE" && echo "PASS: Has Next Steps" || echo "FAIL: Missing Next Steps"
```

### Content Verification
```bash
# Check key content is included
grep -q "Phase 2" "$HANDOFF_FILE" && echo "PASS: Current phase included" || echo "FAIL: Current phase missing"
grep -q "API Development" "$HANDOFF_FILE" && echo "PASS: Phase description included" || echo "FAIL: Phase description missing"
grep -q "pagination" "$HANDOFF_FILE" && echo "PASS: Blocker context included" || echo "FAIL: Blocker missing"
grep -q "auth.ts" "$HANDOFF_FILE" && echo "PASS: Modified files included" || echo "FAIL: Modified files missing"
grep -q "JWT\|Prisma\|Zod" "$HANDOFF_FILE" && echo "PASS: Technical decisions included" || echo "FAIL: Technical decisions missing"
```

### Timestamp and Metadata
```bash
# Check metadata
grep -q "Date:" "$HANDOFF_FILE" || grep -q "Created:" "$HANDOFF_FILE" && echo "PASS: Has timestamp" || echo "FAIL: Missing timestamp"
grep -q "2026-01-22" "$HANDOFF_FILE" && echo "PASS: Correct date" || echo "FAIL: Wrong date"
```

### Local Copy Created
```bash
# Check local copy in project
[ -f ".planning/handoffs/${TODAY}-handoff.md" ] || [ -f ".planning/HANDOFF.md" ] && echo "PASS: Local copy exists" || echo "WARN: No local copy (optional)"
```

---

## Cleanup Steps

```bash
# Remove temp test directory
cd /
rm -rf "$TEST_DIR"

# Optionally remove test handoff file
# rm "$HANDOFF_FILE"
```

---

## Pass/Fail Criteria

| Criterion | Required | Description |
|-----------|----------|-------------|
| Handoff file created | YES | File in ~/.claude/warrior-handoffs/ |
| Unified format used | YES | Standard WARRIOR handoff sections |
| Project Overview | YES | Project name and description |
| Current State | YES | Phase and breath information |
| Progress Summary | YES | Completion percentage/status |
| Active Tasks | YES | Pending tasks listed |
| Blockers | YES | Known blockers documented |
| Technical Context | YES | Key decisions and tools |
| Files Modified | YES | Changed files listed |
| Next Steps | YES | Actionable next actions |
| Timestamp | YES | Creation date included |
| Local copy | NO | Optional backup in .planning/ |

## Expected Result
**PASS** if all required criteria are met.

---

## Test Variations

### Variation A: Clean State (No Blockers)
- No blockers in CONSCIENCE.md
- Blockers section should indicate "None"

### Variation B: Multiple Phases Active
- Work spanning multiple phases
- All active phases should be documented

### Variation C: First Session (No History)
- Fresh project, first handoff
- Should still generate valid handoff

---

## Known Issues
- Long file lists may be truncated
- Git diff integration may require git repository

## Related Tests
- `resume.test.md` - Tests consuming handoff files
- `full-workflow.test.md` - Tests complete workflow with handoffs
