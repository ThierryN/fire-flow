# E2E Test: /fire-6-resume - Session Resume

## Test Name
`session-resume`

## Description
Validates that `/fire-6-resume` properly restores context from a previous session handoff, loads project state, and prepares the session to continue work where the previous session left off.

---

## Prerequisites
- Fire Flow plugin installed
- Existing handoff file in `~/.claude/warrior-handoffs/`
- Project directory accessible

---

## Setup Steps

```bash
# 1. Create temp test directory
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"

# 2. Copy test project fixture
cp -r ~/.claude/plugins/fire-flow/tests/fixtures/test-project/.planning .

# 3. Create a handoff file (simulating previous session)
HANDOFF_DIR="$HOME/.claude/warrior-handoffs"
mkdir -p "$HANDOFF_DIR"
TODAY=$(date +%Y-%m-%d)
HANDOFF_FILE="$HANDOFF_DIR/TEST-PROJECT_${TODAY}.md"

cat > "$HANDOFF_FILE" << 'EOF'
# WARRIOR Handoff: TEST-PROJECT

**Date:** 2026-01-22 14:30:00
**Session Duration:** 2.5 hours
**AI Model:** Claude Opus 4.5

---

## Project Overview

**Project:** Test Project - API Backend
**Repository:** /tmp/test-project-xxxxx
**Technology Stack:** Node.js, TypeScript, Prisma, PostgreSQL

---

## Current State

**Phase:** 2 - API Development
**Breath:** 2 of 3 (In Progress)
**Overall Progress:** 45%

The API development phase is underway. Authentication endpoints are complete,
and work on the product catalog API has begun.

---

## Progress Summary

### Completed This Session
- [x] Implemented auth middleware with JWT validation
- [x] Created /api/auth/login endpoint
- [x] Created /api/auth/register endpoint
- [x] Set up Prisma schema for users

### In Progress
- [ ] Product CRUD endpoints (started)
- [ ] Pagination implementation

---

## Active Tasks

1. **Immediate:** Complete /api/products GET endpoint with filtering
2. **Next:** Implement pagination (cursor-based)
3. **Pending:** Add rate limiting to auth endpoints

---

## Blockers

| Blocker | Impact | Proposed Solution |
|---------|--------|-------------------|
| Pagination strategy undecided | Blocks list endpoints | Use cursor-based (recommended) |
| Rate limiting config needed | Security concern | Use redis-based rate limiter |

---

## Technical Context

### Key Decisions Made
- JWT tokens with 1-hour expiry
- Refresh tokens in HTTP-only cookies
- Zod for request/response validation
- Prisma ORM with PostgreSQL

### Architecture Notes
- RESTful API design
- Service layer pattern
- Middleware for auth, validation, error handling

---

## Files Modified

| File | Status | Changes |
|------|--------|---------|
| server/routes/auth.ts | New | Auth endpoints |
| server/middleware/auth.ts | New | JWT middleware |
| server/services/auth.service.ts | New | Auth business logic |
| prisma/schema.prisma | Modified | User model added |

---

## Next Steps

1. **First:** Read this handoff and restore context
2. **Then:** Continue with /api/products GET endpoint
3. **After:** Implement cursor-based pagination
4. **Finally:** Run verification before next handoff

---

## Resume Commands

```bash
cd /tmp/test-project-xxxxx
/fire-6-resume
```

---

## Notes

- Tests are passing (last run: 2026-01-22 14:00)
- Database migrations are current
- No uncommitted changes
EOF

# 4. Update local CONSCIENCE.md to match handoff
cat > .planning/CONSCIENCE.md << 'EOF'
# Project State

## Current Phase
Phase 2: API Development (Breath 2 of 3)

## Session Context
- Previous session ended mid-breath
- Handoff created at 14:30

## Active Tasks
- [ ] Complete /api/products GET endpoint
- [ ] Implement cursor-based pagination
- [ ] Add rate limiting to auth endpoints

## Blockers
- Pagination strategy: cursor-based (decided)
- Rate limiting: use redis-based limiter

## Last Updated
2026-01-22 14:30:00
EOF
```

---

## Execute Steps

```bash
# 1. Run the resume command
# In Claude Code session:
/fire-6-resume

# 2. Observe context restoration:
#    - Handoff file located and read
#    - CONSCIENCE.md synchronized
#    - Context displayed to user
```

---

## Verify Steps

### Handoff Located
```bash
# Verify the command found the handoff
# (This is verified by command output)
echo "Check Claude Code output for: 'Found handoff: TEST-PROJECT_${TODAY}.md'"
```

### Context Restored
```bash
# Check that current session has context
# This is verified through the Claude Code session itself
# The AI should be able to answer questions about:
#   - Current phase and breath
#   - What was completed
#   - What is blocked
#   - What to do next
```

### CONSCIENCE.md Synchronized
```bash
# Check CONSCIENCE.md was updated if needed
grep -q "Resume\|restored\|continued" .planning/CONSCIENCE.md && echo "PASS: Resume noted in CONSCIENCE.md" || echo "WARN: Resume not noted"
```

### Next Steps Identified
```bash
# The resume command should output next steps
# Verify by checking Claude Code's response mentions:
#   - Continue with /api/products GET endpoint
#   - Cursor-based pagination
echo "Check Claude Code output for next steps from handoff"
```

### No Duplicate Handoff
```bash
# Resume should NOT create a new handoff immediately
NEW_HANDOFFS=$(find "$HANDOFF_DIR" -name "*${TODAY}*.md" -newer "$HANDOFF_FILE" | wc -l)
[ "$NEW_HANDOFFS" -eq 0 ] && echo "PASS: No duplicate handoff created" || echo "WARN: New handoff created on resume"
```

---

## Cleanup Steps

```bash
# Remove temp test directory
cd /
rm -rf "$TEST_DIR"

# Remove test handoff file
rm -f "$HANDOFF_FILE"
```

---

## Pass/Fail Criteria

| Criterion | Required | Description |
|-----------|----------|-------------|
| Handoff file found | YES | Most recent handoff located |
| Handoff parsed | YES | All sections extracted |
| Context displayed | YES | User sees summary of state |
| Current phase identified | YES | Phase and breath known |
| Blockers loaded | YES | Blockers are accessible |
| Next steps identified | YES | Actionable items shown |
| CONSCIENCE.md synchronized | NO | Local state optionally updated |
| No duplicate handoff | YES | Resume doesn't create new handoff |

## Expected Result
**PASS** if all required criteria are met.

---

## Test Variations

### Variation A: No Handoff Exists
- Empty handoff directory
- Should gracefully report "No handoff found"
- Offer to start fresh

### Variation B: Multiple Handoff Files
- Several handoff files exist
- Should offer selection or use most recent

### Variation C: Stale Handoff (>24 hours old)
- Old handoff file
- Should warn about potential staleness
- Offer to continue anyway

### Variation D: Different Project Handoff
- Handoff from different project
- Should detect mismatch
- Confirm with user before loading

---

## Known Issues
- Path matching may fail if project moved
- Large handoff files may truncate in display

## Related Tests
- `handoff.test.md` - Creates handoff files consumed here
- `hooks.test.md` - Tests SessionStart hook that may auto-resume
