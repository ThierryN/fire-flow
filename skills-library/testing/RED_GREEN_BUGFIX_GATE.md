---
name: red-green-bugfix-gate
category: testing
version: 1.0.0
contributed: 2026-03-10
contributor: scribe-bible
last_updated: 2026-03-10
tags: [debugging, tdd, regression, playwright, vitest, bugfix]
difficulty: medium
scope: general
---

# Red-Green Bugfix Gate

## Problem

Bug fixes applied without tests have three failure modes:
1. **The fix doesn't actually work** — you think it's fixed because the error message changed, but the underlying behavior is still wrong.
2. **The bug comes back** — a future change re-introduces it because nothing enforces the correct behavior.
3. **The fix masks a deeper issue** — the symptom disappears but the root cause persists.

Writing a test AFTER the fix proves nothing — you're just writing a test that passes. The test must fail FIRST (proving it captures the bug), then pass AFTER the fix (proving the fix works).

## Solution Pattern

**Red-Green Gate:** Insert a mandatory step between "root cause confirmed" and "apply fix":

```
ROOT CAUSE CONFIRMED
        │
        ▼
  Write failing test  ← RED: test reproduces the bug
        │
        ▼
    Apply the fix
        │
        ▼
   Run test again     ← GREEN: test passes, proving fix works
        │
        ▼
  Run full test suite ← NO REGRESSIONS
        │
        ▼
     RESOLVED
```

### Decision Matrix: What Kind of Test?

Not every bug needs the same test type. Pick based on where the bug lives:

| Bug Location | Test Type | Tool | Speed |
|-------------|-----------|------|-------|
| Pure function / service logic | Unit test | Vitest | <1s |
| API endpoint response | Integration test | Vitest + supertest | <3s |
| Database query / ORM | Integration test | Vitest + test DB | <5s |
| UI interaction / render | Component test | Vitest + testing-library | <3s |
| Multi-page flow / auth | E2E test | Playwright | <30s |
| Race condition / timing | E2E or manual | Playwright | varies |
| Environment / config | Smoke test or skip | curl / manual | <1s |

### When to SKIP the test gate:

- **Typo fixes** — wrong import path, misspelled variable. The existing test suite catches these.
- **Config/environment bugs** — wrong port, missing env var. Not worth a test.
- **One-line obvious fixes** — wrong model ID, missing `await`. If the fix is self-evident from the root cause AND existing tests cover the area, skip.
- **Third-party API changes** — the bug is external. Mock-based tests would be brittle.

**Rule of thumb:** If you eliminated 2+ hypotheses to find the root cause, the bug is non-obvious enough to deserve a test.

## Code Example

### Before (no test gate — fix applied blind)

```typescript
// Developer sees: "Cannot read properties of undefined (reading 'length')"
// Developer adds optional chaining:
results.entities?.length  // "fixed"
// But: did this actually fix the user-facing behavior? Is the data still wrong?
// No test exists to answer this.
```

### After (Red-Green Gate)

```typescript
// Step 1: RED — Write test that reproduces the bug
test('LightRAG search returns valid result shape even with no data', async () => {
  const res = await request.post('/api/lightrag/search', {
    data: { userId: 'test', query: 'nonexistent', mode: 'hybrid' },
  })
  expect(res.status()).toBe(200)
  const data = await res.json()
  // This is what crashed — accessing .length on undefined arrays
  expect(data.entities).toBeDefined()
  expect(Array.isArray(data.entities)).toBe(true)
})
// Run → FAILS (reproduces the bug) ✓

// Step 2: Apply the fix (optional chaining + default empty arrays)

// Step 3: GREEN — Run same test → PASSES ✓
// Step 4: Run full suite → NO REGRESSIONS ✓
```

### Playwright E2E Example (UI bugs)

```typescript
// RED: Write test that reproduces the UI crash
test('Settings page shows ElevenLabs without crash', async ({ page }) => {
  await page.goto('/settings')
  const apiKeysTab = page.locator('button:has-text("API Keys")')
  await apiKeysTab.click()
  // This crashed before the fix
  await expect(page.locator('text=ElevenLabs').first()).toBeVisible()
  // Verify no JS errors
  const body = page.locator('body')
  await expect(body).not.toContainText('Cannot read properties')
})
```

## Integration with fire-debugger

This gate injects between the existing Steps 4 and 5 of the fire-debugger agent:

```
Step 4: Root Cause Confirmed
              │
     ┌────────┴────────┐
     │  RED-GREEN GATE  │  ← NEW
     │                  │
     │  Skip if:        │
     │  • Typo/config   │
     │  • Existing test │
     │    covers it     │
     │  • Self-evident  │
     │    one-liner     │
     │                  │
     │  Otherwise:      │
     │  1. Write RED    │
     │  2. Verify FAIL  │
     │  3. Apply fix    │
     │  4. Verify GREEN │
     └────────┬────────┘
              │
Step 5: Apply Fix (fix already applied in gate)
Step 6: Verify Fix (test already passes from gate)
Step 7: Regression Check (run full suite)
```

### What to add to fire-debugger.md (Step 4.5):

```markdown
### Step 4.5: Red-Green Bugfix Gate

After confirming root cause, decide: does this bug warrant a regression test?

**Write a test if ANY of:**
- 2+ hypotheses were eliminated (non-obvious bug)
- The bug is in business logic, not config
- The area has no existing test coverage
- The bug could recur from future changes

**Skip the test if ALL of:**
- Fix is a one-line typo/config change
- Existing tests already cover this path
- Bug is environmental (ports, env vars, OS-specific)

**If writing a test:**
1. Write the test BEFORE applying the fix
2. Run it — must FAIL (RED) to prove it captures the bug
3. Apply the fix
4. Run it — must PASS (GREEN) to prove the fix works
5. Continue to Step 7 (regression check)

**Test placement:**
- Unit/integration → alongside existing test files
- E2E → `frontend/e2e/` or project's E2E directory
- Name: `{bug-slug}.regression.test.ts` or add to existing spec
```

## When to Use

- After confirming a bug's root cause, before applying the fix
- When the bug was non-obvious (required hypothesis elimination)
- When the fixed area lacks test coverage
- When the bug could silently recur

## When NOT to Use

- Typo fixes (wrong import, misspelled variable)
- Environment/config bugs (missing env var, wrong port)
- Bugs in third-party dependencies (test the workaround, not the library)
- Emergency hotfixes where time pressure overrides (but file a TODO to add the test later)

## Related Skills

- [VITEST_UNIT_TEST_PATTERNS](./VITEST_UNIT_TEST_PATTERNS.md) — unit test patterns
- [E2E_PLAYWRIGHT_PATTERNS](./E2E_PLAYWRIGHT_PATTERNS.md) — E2E test patterns
- [INTEGRATION_TEST_STRATEGY](./INTEGRATION_TEST_STRATEGY.md) — integration test strategy

## References

- TDD for bug fixes: Kent Beck's "make the failing test pass" principle
- Today's real-world example: Scribe Bible v3.0 — LightRAG crash, FFmpeg lavfi, login rate limiter. The rate limiter bug was only caught because a screenshot (the test's failure artifact) showed "Too many login attempts" — without that test, we'd have debugged auth logic for hours.
