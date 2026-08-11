---
description: Deep validation before claiming work is complete
---

# /fire-double-check

> Verify before you claim victory

---

## Purpose

A rigorous validation command inspired by superpowers:verification-before-completion. Prevents false completion claims by requiring evidence-based verification. Integrates with WARRIOR honesty protocols to ensure claims match reality.

---

## Arguments

```yaml
arguments:
  target:
    required: false
    type: string
    description: "What to verify - defaults to current work"
    examples:
      - "/fire-double-check"  # Verify current work
      - "/fire-double-check 'login feature'"
      - "/fire-double-check phase 2"
      - "/fire-double-check PR#45"

optional_flags:
  --deep: "Run extended verification including edge cases"
  --fast: "Quick sanity check only (not recommended)"
  --focus: "Specific area: tests, security, types, build"
  --fix: "Attempt to fix issues found (default: report only)"
```

---

## Core Principle

**EVIDENCE BEFORE ASSERTION**

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ✗ WRONG: "The tests pass" → then run tests                     │
│  ✓ RIGHT: Run tests → "The tests pass (output: 45/45)"          │
│                                                                 │
│  ✗ WRONG: "I fixed the bug" → hope it works                     │
│  ✓ RIGHT: Reproduce → fix → verify fix → "Bug fixed (proof)"    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Process

### Step 1: Identify Claims

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      DOMINION FLOW ► DOUBLE CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Target: {target or "Current Work"}
Mode: Evidence-Based Verification
```

**Analyze what's being claimed:**
```markdown
## Claims to Verify

Based on context, the following claims need verification:

| # | Implicit Claim | Evidence Required |
|---|----------------|-------------------|
| 1 | Code compiles | Build output |
| 2 | Tests pass | Test runner output |
| 3 | Feature works | Demo or test |
| 4 | No regressions | Full test suite |
| 5 | Types are correct | TypeScript output |
```

### Step 2: Execute Verification Commands

**Run ALL verification commands and capture output:**

```bash
# Claim 1: Code compiles
echo "=== BUILD CHECK ==="
npm run build 2>&1
BUILD_EXIT=$?

# Claim 2: Tests pass
echo "=== TEST CHECK ==="
npm run test 2>&1
TEST_EXIT=$?

# Claim 3: Types correct
echo "=== TYPE CHECK ==="
npm run typecheck 2>&1
TYPE_EXIT=$?

# Claim 4: Lint passes
echo "=== LINT CHECK ==="
npm run lint 2>&1
LINT_EXIT=$?
```

### Step 3: Analyze Results

```markdown
## Verification Results

### Build Check
**Command:** `npm run build`
**Exit Code:** {0 | non-zero}
**Output:**
```
{actual output}
```
**Verdict:** PASS | FAIL

---

### Test Check
**Command:** `npm run test`
**Exit Code:** {0 | non-zero}
**Output:**
```
{actual output showing pass/fail count}
```
**Verdict:** PASS | FAIL ({X}/{Y} tests)

---

### Type Check
**Command:** `npm run typecheck`
**Exit Code:** {0 | non-zero}
**Output:**
```
{actual output}
```
**Verdict:** PASS | FAIL ({X} errors)

---

### Lint Check
**Command:** `npm run lint`
**Exit Code:** {0 | non-zero}
**Output:**
```
{actual output}
```
**Verdict:** PASS | FAIL ({X} warnings, {Y} errors)
```

### Step 4: Deep Verification (if --deep or specific feature)

**For features/bug fixes, verify the actual behavior:**

```markdown
## Feature Verification

### Claim: "User can log in with valid credentials"

**Test Steps:**
1. Start the application
2. Navigate to /login
3. Enter valid credentials
4. Click login button
5. Verify redirect to dashboard

**Evidence:**
```bash
# API test
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  -w "\n%{http_code}"
```

**Output:**
```json
{"token":"eyJ...","user":{"id":1,"email":"test@example.com"}}
200
```

**Verdict:** PASS - Login returns token and 200 status
```

### Step 5: Honesty Protocol Check

**MANDATORY: Answer before claiming complete.**

```markdown
## Honesty Check

### Question 1: Did I actually run these commands?
- [x] Yes, all commands were executed in this session
- [ ] No, I assumed based on previous runs

### Question 2: Am I interpreting the output honestly?
- [x] The output clearly shows success/failure
- [ ] The output is ambiguous, I'm making assumptions

### Question 3: Are there things I'm NOT checking?
- [ ] No, I've verified everything needed
- [x] Yes, I haven't verified: {list what's unchecked}

### Question 4: Would a skeptic be convinced?
- [x] Yes, the evidence is clear
- [ ] No, more verification needed
```

### Step 6: Generate Verification Report

```markdown
## Double-Check Summary

| Check | Command | Result | Evidence |
|-------|---------|--------|----------|
| Build | `npm run build` | PASS | Exit 0 |
| Tests | `npm run test` | PASS | 45/45 |
| Types | `npm run typecheck` | PASS | 0 errors |
| Lint | `npm run lint` | PASS | 0 errors |
| Feature | Manual/API test | PASS | HTTP 200 |

### Overall Verdict

**STATUS:** VERIFIED | ISSUES FOUND | CANNOT VERIFY

### Confidence Level

Based on evidence gathered:
- **High Confidence:** All automated checks pass, feature verified
- **Medium Confidence:** Automated checks pass, manual verification partial
- **Low Confidence:** Some checks skipped or failing
```

---

## Output Display

### All Checks Pass

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ ✓ DOUBLE-CHECK PASSED                                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  All verification checks passed with evidence:                               ║
║                                                                              ║
║    ✓ Build       Exit 0, no errors                                           ║
║    ✓ Tests       45/45 passing (92% coverage)                                ║
║    ✓ Types       0 TypeScript errors                                         ║
║    ✓ Lint        0 errors, 0 warnings                                        ║
║    ✓ Feature     Login returns 200 with token                                ║
║                                                                              ║
║  Confidence: HIGH                                                            ║
║                                                                              ║
║  You may now claim this work is complete.                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Issues Found

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ ✗ DOUBLE-CHECK FAILED                                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Issues found that must be resolved:                                         ║
║                                                                              ║
║    ✓ Build       Exit 0, no errors                                           ║
║    ✗ Tests       42/45 passing (3 FAILING)                                   ║
║    ✓ Types       0 TypeScript errors                                         ║
║    ⚠ Lint        0 errors, 12 warnings                                       ║
║                                                                              ║
║  Failing Tests:                                                              ║
║    - auth.test.ts: "should reject invalid password"                          ║
║    - auth.test.ts: "should rate limit after 5 attempts"                      ║
║    - user.test.ts: "should return 404 for missing user"                      ║
║                                                                              ║
║  DO NOT claim complete until these are fixed.                                ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ NEXT STEPS                                                                   ║
├──────────────────────────────────────────────────────────────────────────────┤
║                                                                              ║
║  → Fix the 3 failing tests                                                   ║
║  → Address lint warnings (optional but recommended)                          ║
║  → Run `/fire-double-check` again                                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Integration with Dominion Flow

### Before Claiming Done
```bash
# After implementing feature
/fire-double-check
# Only proceed if VERIFIED
```

### Before Verification Phase
```bash
/fire-3-execute 2
# ... execution completes ...
/fire-double-check phase 2
# Then
/fire-4-verify 2
```

### Before Commit
```bash
/fire-double-check --focus tests,types
# If passes, safe to commit
```

### Before PR
```bash
/fire-double-check --deep
# Comprehensive check before review request
```

---

## What Gets Checked

### Standard Checks (Always Run)

| Check | Command | What It Verifies |
|-------|---------|------------------|
| Build | `npm run build` | Code compiles |
| Tests | `npm run test` | Tests pass |
| Types | `npm run typecheck` | Type safety |
| Lint | `npm run lint` | Code style |

### Deep Checks (--deep flag)

| Check | Command | What It Verifies |
|-------|---------|------------------|
| Coverage | `npm run test:coverage` | Test coverage threshold |
| Security | `npm audit` | Known vulnerabilities |
| E2E | `npm run test:e2e` | End-to-end flows |
| Performance | `npm run test:perf` | Performance benchmarks |

### Focus Checks (--focus flag)

```bash
--focus tests     # Only test-related checks
--focus security  # Only security checks
--focus types     # Only TypeScript checks
--focus build     # Only build checks
```

---

## Anti-Patterns Blocked

| Anti-Pattern | How Double-Check Prevents |
|--------------|---------------------------|
| "Tests pass" without running | Commands executed and output captured |
| "Fixed the bug" without verification | Requires reproduction + verification |
| Claiming done with failing tests | Exit codes checked, failures reported |
| Ignoring warnings | Warnings counted and displayed |
| Skipping checks to save time | All checks required, no skip option |

---

## Sabbath Rest

> *Like humans need sleep to reset, AI agents need state files to resume after context resets.*

### Update CONSCIENCE.md After Verification

**MANDATORY:** Record verification results in CONSCIENCE.md:

```markdown
## Verification History
| Date | Target | Result | Evidence File |
|------|--------|--------|---------------|
| {timestamp} | {target} | VERIFIED/ISSUES | .planning/verifications/{file}.md |

## Last Verification
- **Target:** {what was verified}
- **Result:** {VERIFIED | ISSUES FOUND}
- **Confidence:** {HIGH | MEDIUM | LOW}
- **Checks:** Build ✓ Tests ✓ Types ✓ Lint ✓
```

### Save Verification Report

**Create:** `.planning/verifications/{target}-{timestamp}.md`

Contains full evidence capture for audit trail.

### Session State (for interrupted verifications)

**Create/Update:** `.claude/fire-double-check.local.md`

```markdown
---
last_run: {timestamp}
target: "{target}"
status: {in_progress | complete}
result: {VERIFIED | ISSUES_FOUND | null}
---

# Double-Check Session State

## Current Verification
- Target: {target}
- Started: {timestamp}
- Checks Completed: [build, test, ...]
- Checks Remaining: [...]

## Results Cache
| Check | Status | Output Hash |
|-------|--------|-------------|
| build | PASS | {hash} |
| test | PASS | {hash} |
```

This ensures:
- Verification results persist in project history
- Interrupted verifications can resume
- Audit trail for compliance

---

## Success Criteria

### Required Outputs
- [ ] All verification commands executed
- [ ] Output captured and displayed
- [ ] Clear PASS/FAIL verdict per check
- [ ] Overall status determined
- [ ] Confidence level stated

### Verification Complete When
- All standard checks pass
- Honesty protocol questions answered
- Evidence supports the claims being made

---

## References

- **Inspiration:** superpowers:verification-before-completion
- **Protocol:** `@references/honesty-protocols.md`
- **Checklist:** `@references/validation-checklist.md`
- **Brand:** `@references/ui-brand.md`
