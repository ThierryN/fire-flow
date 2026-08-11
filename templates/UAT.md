# UAT Template (Dominion Flow Enhanced)

> **Origin:** Ported from Dominion Flow `UAT.md` with parallel diagnosis integration.

Template for conversational User Acceptance Testing via `/fire-verify-uat`.

---

## UAT Session Format

```markdown
# UAT Session: Phase XX - [Phase Name]

## Session Info
- **Phase:** XX-name
- **Date:** [date]
- **Tester:** [user/AI]
- **Environment:** [local/staging/production]

## Critical Flows to Test

| # | Flow | Priority | Status | Notes |
|---|------|----------|--------|-------|
| 1 | [User registration] | Must Pass | [PASS/FAIL] | |
| 2 | [User login] | Must Pass | [PASS/FAIL] | |
| 3 | [Core feature A] | Must Pass | [PASS/FAIL] | |
| 4 | [Edge case B] | Should Pass | [PASS/FAIL] | |

## Test Execution

### Flow 1: [User Registration]

**Steps:**
1. Navigate to /register
2. Fill in email: test@example.com
3. Fill in password: SecurePass123!
4. Click "Register"

**Expected:** Redirect to /dashboard, welcome message displayed
**Actual:** [result]
**Status:** [PASS/FAIL]

### Flow 2: [User Login]
[...]

## Issues Found

| # | Severity | Description | Flow | Diagnosis |
|---|----------|-------------|------|-----------|
| 1 | Critical | [description] | Flow 1 | [root cause if known] |
| 2 | Minor | [description] | Flow 3 | [root cause if known] |

## Diagnosis Results (if failures found)

For each FAIL, `/fire-diagnose` runs parallel investigation:
- Agent 1: [Component where symptom appears]
- Agent 2: [Component that triggers it]
- Agent 3: [Working reference pattern]

## UAT Verdict

- **Overall:** [PASS / CONDITIONAL PASS / FAIL]
- **Blocking Issues:** [count]
- **Non-Blocking Issues:** [count]
- **Recommendation:** [Proceed to next phase / Fix and retest / Major rework needed]
```

---

## Conversational UAT Protocol

1. **Present flows** - Show user the critical flows to test
2. **Guide testing** - Walk through each flow step by step
3. **Record results** - PASS/FAIL for each flow
4. **On failure** - Immediately spawn parallel diagnosis agents
5. **Report** - Generate UAT report with verdict
6. **Route** - If PASS: `/fire-transition`. If FAIL: fix and retest.

---

## Automatic Diagnosis on Failure

When a UAT flow fails, automatically spawn 3 parallel agents:

```javascript
// Agent 1: Where the symptom appears
Task({ subagent_type: "fire-debugger", prompt: "Investigate [component with failure]..." });

// Agent 2: What triggers it
Task({ subagent_type: "fire-debugger", prompt: "Investigate [parent/caller component]..." });

// Agent 3: Working reference
Task({ subagent_type: "Explore", prompt: "Find working pattern in [similar component]..." });
```

This matches the parallel debugging pattern documented in CLAUDE.md.
