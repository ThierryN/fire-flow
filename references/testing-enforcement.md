# Dominion Flow Testing Enforcement Reference

> **Origin:** NEW for Dominion Flow v2.0 - Mandatory testing requirements.

## Overview

Dominion Flow enforces testing as a first-class requirement, not an afterthought. Every plan that creates or modifies application code must include test verification. This reference defines what testing is required, when, and how it integrates with the execution pipeline.

---

## Testing Requirements by Plan Type

| Plan Type | Unit Tests | Integration Tests | E2E Tests | Build Check |
|-----------|-----------|------------------|-----------|-------------|
| API endpoint | Required | Required | Optional | Required |
| UI component | Required | Optional | Recommended | Required |
| Database schema | Optional | Required | Optional | Required |
| Utility/helper | Required | Optional | Optional | Required |
| Configuration | Optional | Optional | Optional | Required |
| Documentation | Not needed | Not needed | Not needed | Not needed |

---

## Test Enforcement Points

### 1. During Planning (`/fire-2-plan`)

Every plan's `<verification>` section MUST include:

```xml
<verification>
### Test Requirements
- [ ] [Specific test command] (e.g., npm test -- --testPathPattern=auth)
- [ ] Build passes: npm run build
- [ ] No new lint warnings: npm run lint

### WARRIOR Quality Gates
- [ ] Code builds without errors
- [ ] Tests pass (existing + new)
- [ ] No regressions in existing tests
</verification>
```

Plans without test requirements are flagged during plan review.

### 2. During Execution (`/fire-execute-plan`)

After each segment completes:

```bash
# Auto-detect and run test suite
npm test 2>/dev/null || yarn test 2>/dev/null || pytest 2>/dev/null || go test ./... 2>/dev/null
```

**If tests pass:** Continue to next segment.

**If tests fail:**
- Attempt auto-fix (deviation Rule 1)
- If still failing after 2 attempts, create P1 blocker
- Present options: Fix / Skip (tracked) / Stop

### 3. During Verification (`/fire-4-verify`)

Verification agent checks:
- [ ] All planned tests exist and pass
- [ ] No test files are stubs or placeholders
- [ ] Test assertions are meaningful (not `expect(true).toBe(true)`)
- [ ] Critical flows have test coverage
- [ ] No skipped tests without justification

### 4. During Phase Transition (`/fire-transition`)

Phase metrics include:
- Tests added this phase
- Test coverage delta
- Test pass rate
- Regression count

---

## Test Quality Standards

### Meaningful Assertions

```javascript
// BAD - Tests nothing
expect(true).toBe(true);
expect(1).toBe(1);

// BAD - Only checks existence
expect(result).toBeDefined();

// GOOD - Tests behavior
expect(result.status).toBe(201);
expect(result.body.user.email).toBe('test@example.com');
expect(result.body.token).toMatch(/^eyJ/);

// GOOD - Tests error handling
await expect(login({ email: '' })).rejects.toThrow('Email required');
```

### Test Structure

```javascript
describe('POST /api/auth/register', () => {
  it('creates user with valid credentials', async () => {
    // Happy path - REQUIRED
  });

  it('rejects duplicate email', async () => {
    // Error path - REQUIRED for critical flows
  });

  it('rejects weak password', async () => {
    // Validation - REQUIRED for user input
  });
});
```

### Coverage Expectations

| Flow Type | Minimum Coverage |
|-----------|-----------------|
| Authentication | Happy + 2 error paths |
| Payment | Happy + all error paths |
| Data mutation | Happy + validation + auth check |
| Read-only API | Happy + not-found + auth check |
| UI component | Renders + key interactions |

---

## TDD Integration

When `plan.type === "tdd"` in frontmatter:

1. **RED:** Write failing test first, commit: `test({phase}-{plan}): add failing test for [feature]`
2. **GREEN:** Implement to pass, commit: `feat({phase}-{plan}): implement [feature]`
3. **REFACTOR:** Clean up if needed, commit: `refactor({phase}-{plan}): clean up [feature]`

TDD plans produce 2-3 atomic commits per feature. See `references/tdd.md` for full TDD reference.

---

## Framework Setup

When no test framework exists in the project:

| Stack | Framework | Setup Command |
|-------|-----------|---------------|
| Node.js | Jest | `npm install -D jest @types/jest ts-jest` |
| Node.js (Vite) | Vitest | `npm install -D vitest` |
| Python | pytest | `pip install pytest` |
| Go | testing | Built-in |
| E2E | Playwright | `npm install -D @playwright/test` |

Framework setup is included in the first plan's execution as an auto task.

---

## Anti-Patterns

- **No tests:** Plan creates code without any test verification
- **Stub tests:** Tests exist but assert nothing meaningful
- **Only happy path:** Missing error/edge case coverage
- **Test after:** Writing all code first, then adding tests as afterthought
- **Skipping without reason:** Using `.skip()` without documented justification
- **Testing implementation:** Mocking internals instead of testing behavior
- **Ignoring failures:** Marking failing tests as "known issue" without blocker

---

## Enforcement Levels

Configurable in `.planning/config.json`:

```json
{
  "testing": {
    "enforcement": "strict",
    "min_assertions_per_test": 1,
    "require_error_paths": true,
    "allow_skip_with_reason": true,
    "auto_detect_framework": true
  }
}
```

| Level | Behavior |
|-------|----------|
| `strict` | Tests required for all code changes, block on failure |
| `standard` | Tests required for API/logic, warn on missing UI tests |
| `relaxed` | Tests recommended, never block |
