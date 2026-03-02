# Dominion Flow TDD Reference

> **Origin:** Ported from Dominion Flow `tdd.md` with Dominion Flow Git Flow integration.

## Overview

Test-Driven Development in Dominion Flow. Plans with `type: tdd` in frontmatter follow the Red-Green-Refactor cycle with atomic commits at each stage.

---

## When to Use TDD Plans

- Pure functions, utilities, validators, formatters
- API endpoints with clear input/output contracts
- Business logic with defined rules
- Data transformations

## When NOT to Use TDD Plans

- UI components (test after build with checkpoint:human-verify)
- Configuration/setup tasks
- Database migrations (test with integration tests)
- One-off scripts

---

## TDD Plan Frontmatter

```yaml
---
phase: XX-name
plan: NN
type: tdd
feature: "[Single feature being tested]"
test_framework: jest|vitest|pytest|go-test
---
```

**One feature per TDD plan.** If features are trivial enough to batch, skip TDD.

---

## Red-Green-Refactor Cycle

### RED - Write failing test

1. Ensure correct feature branch: `feature/phase-XX-description`
2. Create test file following project conventions
3. Write test describing expected behavior
4. Run test - MUST fail
5. If test passes: feature already exists or test is wrong
6. Commit: `test({phase}-{plan}): add failing test for [feature]`

### GREEN - Implement to pass

1. Write minimal code to make test pass
2. No cleverness, no optimization - just make it work
3. Run test - MUST pass
4. If not passing, iterate. Do not move to REFACTOR.
5. Commit: `feat({phase}-{plan}): implement [feature]`

### REFACTOR (if needed)

1. Clean up if obvious improvements exist
2. Run tests - MUST still pass
3. Only commit if changes made: `refactor({phase}-{plan}): clean up [feature]`

**Result:** 2-3 atomic commits on the feature branch per TDD plan.

---

## Test Quality Standards

- **Test behavior, not implementation** - tests should survive refactors
- **One concept per test** - separate tests for valid, empty, malformed input
- **Descriptive names** - "should reject empty email" not "test1"
- **No implementation details** - test public API, observable behavior
- **Meaningful assertions** - NEVER `expect(true).toBe(true)`
- **Cover happy + error paths** - at minimum one of each

---

## Test Types

| Type | When | Speed | Example |
|------|------|-------|---------|
| Unit | Pure functions, utilities | Milliseconds | `validateEmail('bad') === false` |
| Integration | API routes, DB operations | Seconds | `POST /api/register -> 201` |
| E2E | Complete user journeys | Seconds-minutes | Playwright checkout flow |

---

## Branch Integration

TDD work follows Git Flow:

1. Ensure feature branch: `git checkout -b feature/phase-XX-desc develop`
2. RED commit on feature branch
3. GREEN commit on feature branch
4. REFACTOR commit on feature branch
5. Create PR from feature to develop
6. Merge after review. Never directly to main.

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Test doesn't fail in RED | Feature may exist. Investigate before proceeding. |
| Test doesn't pass in GREEN | Keep iterating. Don't skip to REFACTOR. |
| Tests fail in REFACTOR | Undo refactor immediately. Smaller steps. |
| Unrelated tests break | Stop. Investigate coupling. Create P1 blocker if needed. |
| Stuck after 3 GREEN attempts | Create P1 blocker in BLOCKERS.md. |

---

## Commit Pattern

```
test(08-02): add failing test for email validation
- Tests valid email formats accepted
- Tests invalid formats rejected

feat(08-02): implement email validation
- Regex pattern matches RFC 5322
- Returns boolean for validity

refactor(08-02): extract regex to constant (optional)
- No behavior changes, tests still pass
```
