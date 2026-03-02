---
description: Conversational User Acceptance Testing with automatic parallel diagnosis on failures
---

# /fire-verify-uat

> Conversational UAT testing with automatic parallel diagnosis when flows fail.

---

## Arguments

```yaml
arguments:
  phase:
    required: false
    type: string
    description: "Phase to test (e.g., 03). Defaults to current phase."
```

---

## Process

### Step 1: Load Phase Context

```
+---------------------------------------------------------------+
|              DOMINION FLOW >>> UAT VERIFICATION                   |
+---------------------------------------------------------------+
```

Read all RECORD.md files from the phase. Extract:
- What was built (from quick summaries)
- Critical flows (from PROJECT.md)
- Must-haves (from BLUEPRINT.md frontmatter)

### Step 2: Generate Test Flows

Create test flows from must-haves truths:

```
Critical Flows to Test:
1. [Must-have truth 1] - Must Pass
2. [Must-have truth 2] - Must Pass
3. [Edge case from PROJECT.md] - Should Pass
```

Present to user: "Ready to start UAT? I'll guide you through each flow."

### Step 3: Guided Testing

For each flow:
1. Present exact steps to test
2. Wait for user result (pass/fail/issue description)
3. Record result

```
+---------------------------------------------------------------+
|  TESTING: Flow 1 of N                                          |
+---------------------------------------------------------------+
|                                                                 |
|  Flow: User can register with email and password               |
|                                                                 |
|  Steps:                                                        |
|    1. Run: npm run dev                                         |
|    2. Visit: http://localhost:3000/register                    |
|    3. Enter email: test@example.com                            |
|    4. Enter password: SecurePass123!                           |
|    5. Click "Register"                                         |
|                                                                 |
|  Expected: Redirect to /dashboard, welcome message             |
|                                                                 |
|-----------------------------------------------------------------|
|  Result? Type "pass", "fail", or describe the issue            |
+-----------------------------------------------------------------+
```

### Step 4: Automatic Diagnosis on Failure

When a flow fails, immediately spawn 3 parallel debug agents:

```javascript
// Agent 1: Component where symptom appears
Task({ subagent_type: "fire-debugger", prompt: "Investigate [failing component]..." });

// Agent 2: What triggers it (parent/caller)
Task({ subagent_type: "fire-debugger", prompt: "Investigate [trigger component]..." });

// Agent 3: Working reference pattern
Task({ subagent_type: "Explore", prompt: "Find working pattern for [similar feature]..." });
```

Present diagnosis results and proposed fix.

### Step 5: Fix and Retest (if failures)

For each failure with diagnosis:
1. Implement fix
2. Commit: `fix({phase}): resolve UAT failure - [description]`
3. Retest the specific flow
4. If still failing: create P1 blocker

### Step 6: Generate UAT Report

```markdown
## UAT Report: Phase XX

### Results
| Flow | Status | Notes |
|------|--------|-------|
| Registration | PASS | |
| Login | PASS | |
| Dashboard | FAIL -> PASS | Fixed: missing redirect |

### Verdict: [PASS / CONDITIONAL PASS / FAIL]
- Blocking issues: [N]
- Fixed during UAT: [N]
- Deferred: [N]
```

### Step 7: Route

| Verdict | Next Action |
|---------|------------|
| PASS | `/fire-transition` to complete phase |
| CONDITIONAL PASS | User decides: proceed or fix |
| FAIL | Fix blockers, rerun `/fire-verify-uat` |

---

## Success Criteria

- [ ] All critical flows tested
- [ ] Failures diagnosed with parallel agents
- [ ] Fixes committed and retested
- [ ] UAT report generated
- [ ] Clear verdict and next action

---

## References

- **Template:** `@templates/UAT.md`
- **Debugging pattern:** CLAUDE.md parallel debugging section
- **Verification:** `@references/verification-patterns.md`
