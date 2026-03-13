# Evidence-Based Validation - Verification Before Completion

## The Problem

AI agents (and humans) often claim work is "done" without actually verifying it works. This leads to:
- "Tests pass" claims without running tests
- "Bug fixed" assertions without reproduction verification
- Premature completion claims that waste time on rework

### Why It Was Hard

- Pressure to deliver quickly encourages shortcuts
- Verification feels redundant after writing code
- Confidence in one's work creates blind spots
- No systematic enforcement of "prove it works"

### Impact

- False completion claims waste reviewer time
- Bugs reach production that should have been caught
- Trust erodes when "done" doesn't mean "done"
- Rework costs exceed original implementation time

---

## The Solution

**Evidence Before Assertion** - Never claim something works without captured proof.

### Core Principle

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  WRONG: "The tests pass" → then run tests                      │
│  RIGHT: Run tests → "The tests pass (output: 45/45)"           │
│                                                                 │
│  WRONG: "I fixed the bug" → hope it works                      │
│  RIGHT: Reproduce → fix → verify fix → "Bug fixed (proof)"     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### The Verification Protocol

#### Step 1: Identify Claims

Before declaring work complete, list all implicit claims:

```markdown
## Claims to Verify

| # | Implicit Claim | Evidence Required |
|---|----------------|-------------------|
| 1 | Code compiles | Build output with exit code 0 |
| 2 | Tests pass | Test runner output showing pass count |
| 3 | Feature works | Demo or API test with expected response |
| 4 | No regressions | Full test suite output |
| 5 | Types correct | TypeScript compiler output |
```

#### Step 2: Execute Verification Commands

Run ALL commands and capture output:

```bash
# Build check
echo "=== BUILD CHECK ==="
npm run build 2>&1
echo "Exit code: $?"

# Test check
echo "=== TEST CHECK ==="
npm run test 2>&1
echo "Exit code: $?"

# Type check
echo "=== TYPE CHECK ==="
npm run typecheck 2>&1
echo "Exit code: $?"

# Lint check
echo "=== LINT CHECK ==="
npm run lint 2>&1
echo "Exit code: $?"
```

#### Step 3: Document Results with Evidence

```markdown
## Verification Results

### Build Check
**Command:** `npm run build`
**Exit Code:** 0
**Output:**
```
> project@1.0.0 build
> tsc && vite build

vite v5.0.0 building for production...
✓ 234 modules transformed.
dist/index.html          0.45 kB │ gzip:  0.29 kB
dist/assets/index.js   145.67 kB │ gzip: 47.23 kB
✓ built in 2.34s
```
**Verdict:** PASS

### Test Check
**Command:** `npm run test`
**Exit Code:** 0
**Output:**
```
PASS src/auth/login.test.ts
PASS src/api/users.test.ts
PASS src/utils/helpers.test.ts

Test Suites: 3 passed, 3 total
Tests:       45 passed, 45 total
Time:        3.42s
```
**Verdict:** PASS (45/45 tests)
```

#### Step 4: Honesty Protocol

Before claiming complete, answer honestly:

```markdown
## Honesty Check

### Question 1: Did I actually run these commands?
- [x] Yes, all commands executed in this session
- [ ] No, I assumed based on previous runs

### Question 2: Am I interpreting output honestly?
- [x] Output clearly shows success
- [ ] Output is ambiguous, I'm assuming

### Question 3: What am I NOT checking?
- [ ] Nothing unchecked
- [x] E2E tests not run (documented limitation)

### Question 4: Would a skeptic be convinced?
- [x] Yes, evidence is clear
- [ ] No, more verification needed
```

#### Step 5: Final Verdict

```markdown
## Double-Check Summary

| Check | Command | Result | Evidence |
|-------|---------|--------|----------|
| Build | `npm run build` | PASS | Exit 0, no errors |
| Tests | `npm run test` | PASS | 45/45 passing |
| Types | `npm run typecheck` | PASS | 0 errors |
| Lint | `npm run lint` | PASS | 0 warnings |

**STATUS:** VERIFIED
**Confidence:** HIGH

You may now claim this work is complete.
```

---

## Implementation

### Verification Command Template

```javascript
async function doubleCheck(checks = ['build', 'test', 'typecheck', 'lint']) {
  const results = {};

  for (const check of checks) {
    const command = COMMANDS[check];
    console.log(`=== ${check.toUpperCase()} CHECK ===`);

    const { stdout, stderr, exitCode } = await exec(command);

    results[check] = {
      command,
      exitCode,
      output: stdout + stderr,
      verdict: exitCode === 0 ? 'PASS' : 'FAIL'
    };

    console.log(`Exit code: ${exitCode}`);
    console.log(stdout);
  }

  return results;
}

const COMMANDS = {
  build: 'npm run build',
  test: 'npm run test',
  typecheck: 'npm run typecheck',
  lint: 'npm run lint',
  coverage: 'npm run test:coverage',
  security: 'npm audit',
  e2e: 'npm run test:e2e'
};
```

### Anti-Pattern Detection

```javascript
// BAD: Claiming without evidence
function reviewCode() {
  // ... look at code ...
  return "Tests pass"; // NO EVIDENCE!
}

// GOOD: Evidence-based claim
async function reviewCode() {
  const output = await exec('npm run test');
  return `Tests pass (${output.passCount}/${output.totalCount})`;
}
```

---

## Testing the Pattern

### Before (No Verification)
```
Claim: "All tests pass"
Reality: 3 tests failing
Result: Bug reaches production
Cost: 4 hours debugging + hotfix
```

### After (Evidence-Based)
```
Claim: "All tests pass"
Evidence: Test output shows 42/45 passing
Reality: 3 tests failing (caught immediately)
Result: Fixed before merge
Cost: 15 minutes
```

---

## Prevention

### When to Use Evidence-Based Validation

- **Always:** Before claiming any work is complete
- **Always:** Before creating a PR
- **Always:** Before merging to main
- **Always:** After fixing bugs (verify the fix)

### Verification Depth Levels

| Depth | Checks | Use Case |
|-------|--------|----------|
| Quick | build, lint | Minor changes |
| Standard | build, test, types, lint | Normal PRs |
| Deep | All + coverage + security + E2E | Production releases |

---

## Related Patterns

- [Multi-Perspective Code Review](./MULTI_PERSPECTIVE_CODE_REVIEW.md)
- [Honesty Protocols](./HONESTY_PROTOCOLS.md)
- [60-Point Validation Checklist](./VALIDATION_CHECKLIST.md)

---

## Common Mistakes to Avoid

- **Skipping verification to save time** - Rework costs more
- **Assuming previous run is still valid** - Always re-run
- **Ignoring warnings** - Warnings become errors
- **Partial verification** - Run ALL relevant checks
- **Trusting memory** - Capture actual output

---

## Resources

- [superpowers:verification-before-completion](https://github.com/anthropics/claude-code-plugins)
- [Test-Driven Development patterns](./TDD_PATTERNS.md)
- [Continuous Integration best practices](../deployment-security/CI_CD_PATTERNS.md)

---

## Time to Implement

**Per verification:** 2-5 minutes
**ROI:** Prevents 1-4 hour debugging sessions

## Difficulty Level

⭐ (1/5) - Simple to implement, requires discipline

---

**Author Notes:**
This pattern seems obvious but is violated constantly. The key insight is that **verification must be mandatory, not optional**. By requiring captured output as evidence, you eliminate the possibility of false claims.

The honesty protocol questions force reflection before completion. Question 3 ("What am I NOT checking?") is particularly powerful - it surfaces blind spots before they become problems.

**Implementation in Dominion Flow:** Available via `/fire-double-check` command.
