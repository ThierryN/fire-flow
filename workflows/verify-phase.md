# Workflow: Phase Verification Orchestration

<purpose>
Perform comprehensive verification of completed phase work through a dual-layer system: Must-Haves (goal-backward verification) combined with WARRIOR's 70-point validation checklist. This workflow ensures work meets both functional requirements and quality standards, generates detailed reports, and routes to gap closure when needed.
</purpose>

---

<core_principle>
**Verification must be ruthlessly honest.** No rubber-stamping. Every PASS needs evidence. Every FAIL needs specifics. The verification report should tell the truth about the state of the work, not what we hope it to be.
</core_principle>

---

<required_reading>
Before executing this workflow, load:
```markdown
@.planning/CONSCIENCE.md                          # Current project position
@.planning/phases/{N}-{name}/*-BLUEPRINT.md       # All plans with must-haves
@.planning/phases/{N}-{name}/*-RECORD.md    # Execution summaries
@agents/fire-verifier.md                    # Verifier agent configuration
@references/validation-checklist.md          # 70-point WARRIOR checklist
@templates/verification.md                   # Report template
```
</required_reading>

---

<process>

## Step 1: Load Verification Context

**Purpose:** Gather all requirements and execution artifacts for verification.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                         DOMINION FLOW > PHASE {N} VERIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Parse Arguments:**
```yaml
required:
  phase_number: integer

optional:
  --detailed: "Include verbose output for all checks"
  --quick: "Run only critical checks (must-haves + security)"
  --report-only: "Generate report without routing to gap closure"
```

**Load All Plan Must-Haves:**
```bash
# Find all plans for this phase
for plan in .planning/phases/{N}-{name}/{N}-*-BLUEPRINT.md; do
  # Extract must_haves from frontmatter
  extract: must_haves.truths
  extract: must_haves.artifacts
  extract: must_haves.key_links
  extract: must_haves.warrior_validation
done
```

**Aggregate Must-Haves:**
```markdown
## Phase {N} Verification Scope

### Truths to Verify: {count}
1. {truth from plan 01}
2. {truth from plan 01}
3. {truth from plan 02}
...

### Artifacts to Verify: {count}
1. {artifact from plan 01}
2. {artifact from plan 02}
...

### Key Links to Verify: {count}
1. {link from plan 01}
2. {link from plan 02}
...

### WARRIOR Validation Items: {count}
{custom items from plans, plus standard 70-point checklist}
```

---

## Step 2: Spawn fire-verifier Agent

**Purpose:** Execute verification with complete honesty and evidence.

```
Spawning fire-verifier for Phase {N}...
```

**Agent Context Injection:**
```markdown
<verification_scope>
Phase: {N} - {name}
Plans to Verify: {list}
Total Must-Haves: {count}
WARRIOR Checks: 60 items across 6 categories
Mode: {detailed | quick | standard}
</verification_scope>

<must_haves>
{Complete aggregated must-haves from Step 1}
</must_haves>

<warrior_checklist>
@references/validation-checklist.md
</warrior_checklist>

<honesty_protocol>
## Verifier Honesty Declaration

Before starting, confirm:
- [ ] I will run ALL verification commands, not skip any
- [ ] I will report ACTUAL results, not expected results
- [ ] I will fail checks that don't pass, even if "close enough"
- [ ] I will document gaps honestly, not minimize them
- [ ] I will not mark PASS without evidence

**Evidence Requirements:**
- Command output must be included
- "Assumed to pass" is NOT acceptable
- Manual verification must describe exact steps taken
- Screenshots/logs required for UI verification
</honesty_protocol>
```

---

## Step 3: Must-Haves Verification

**Purpose:** Verify goal-backward requirements are met.

### 3.1 Verify Truths

**Definition:** Observable behaviors that prove the work is complete.

```markdown
## Truths Verification

### Truth 1: "{Observable behavior statement}"

**Verification Method:** {Manual | Automated | API Test}

**Command/Steps:**
```bash
{Actual command run}
```

**Expected Result:**
{What should happen}

**Actual Result:**
```
{Actual output captured - MUST be real output}
```

**Status:** PASS | FAIL
**Evidence:** {Screenshot/log reference if applicable}
**Notes:** {Any observations}
```

**For each truth:**
1. Run the verification command
2. Capture actual output
3. Compare to expected
4. Mark PASS only if criteria met exactly
5. Include evidence

### 3.2 Verify Artifacts

**Definition:** Files must exist with specific exports and contents.

```markdown
## Artifacts Verification

### Artifact: {path/to/file.ts}

**Existence Check:**
```bash
ls -la {path/to/file.ts}
```
**Result:** EXISTS | MISSING

**Exports Check:**
```bash
grep -n "export.*{functionName}" {path/to/file.ts}
```
**Expected:** {functionName} exported
**Actual:**
```
{actual grep output}
```
**Result:** PASS | FAIL

**Contains Check:**
```bash
grep -n "{pattern}" {path/to/file.ts}
```
**Expected:** File contains {pattern}
**Actual:**
```
{actual grep output with line numbers}
```
**Result:** PASS | FAIL

**Overall Artifact Status:** PASS | FAIL
```

### 3.3 Verify Key Links

**Definition:** Components are properly wired together.

```markdown
## Key Links Verification

### Link: {component-a} -> {component-b} via {integration-point}

**Import Verification:**
```bash
grep -n "import.*{component-b}" {component-a-file}
```
**Result:**
```
{actual output}
```

**Usage Verification:**
```bash
grep -n "{integration-point}" {component-a-file}
```
**Result:**
```
{actual output}
```

**Expected:**
- {component-a} imports {component-b}
- {component-a} calls {integration-point}

**Status:** PASS | FAIL
```

---

## Step 4: WARRIOR 60-Point Validation

**Purpose:** Comprehensive quality validation across 6 categories.

### 4.1 Code Quality (10 points)

```markdown
## Code Quality Validation: X/10

### CQ-1: Project Builds Without Errors
```bash
npm run build
```
**Expected:** Exit code 0, no errors
**Actual:**
```
{build output}
```
**Status:** PASS (1pt) | FAIL (0pt)

### CQ-2: No TypeScript Errors
```bash
npx tsc --noEmit
```
**Expected:** No errors
**Actual:** {X errors | No errors}
**Status:** PASS (1pt) | FAIL (0pt)

### CQ-3: ESLint Compliance
```bash
npm run lint
```
**Expected:** No errors (warnings acceptable)
**Actual:** {X errors, Y warnings}
**Status:** PASS (1pt) | FAIL (0pt)

### CQ-4: No Console.logs in Production Code
```bash
grep -rn "console.log" src/ --include="*.ts" --include="*.tsx" | grep -v "test" | grep -v "spec" | wc -l
```
**Expected:** 0 (or only intentional logging)
**Actual:** {count}
**Status:** PASS (1pt) | FAIL (0pt)

### CQ-5: Code Comments Present (Why, Not What)
**Manual Check:** Review new files for explanatory comments
**Files Reviewed:** {list}
**Finding:** {adequate comments explaining rationale | missing comments on complex logic}
**Status:** PASS (1pt) | FAIL (0pt)

### CQ-6: Functions Have JSDoc/TSDoc
```bash
grep -c "@param\|@returns\|@description" {new-files}
```
**Expected:** Public functions documented
**Actual:** {count} documented functions
**Status:** PASS (1pt) | FAIL (0pt)

### CQ-7: No Magic Numbers
```bash
grep -rn "[^0-9][0-9][0-9][0-9][^0-9]" src/ --include="*.ts" | grep -v "const\|enum\|type\|test" | head -5
```
**Expected:** Numbers are named constants
**Actual:** {findings}
**Status:** PASS (1pt) | FAIL (0pt)

### CQ-8: Consistent Naming Conventions
**Manual Check:** camelCase functions, PascalCase components, UPPER_SNAKE constants
**Status:** PASS (1pt) | FAIL (0pt)

### CQ-9: No Dead Code
```bash
npx ts-prune 2>/dev/null | grep -v "test\|spec" | head -10
```
**Expected:** No unused exports in new code
**Actual:** {findings}
**Status:** PASS (1pt) | FAIL (0pt)

### CQ-10: Error Handling Present
**Manual Check:** try/catch blocks, error boundaries, error responses
**Status:** PASS (1pt) | FAIL (0pt)

**Code Quality Score:** X/10
```

### 4.2 Testing (10 points)

```markdown
## Testing Validation: X/10

### T-1: Unit Tests Exist
```bash
find . -name "*.test.ts" -o -name "*.spec.ts" | wc -l
```
**Expected:** Tests exist for new code
**Actual:** {count} test files
**Status:** PASS (1pt) | FAIL (0pt)

### T-2: Unit Tests Pass
```bash
npm run test
```
**Expected:** All tests pass
**Actual:** {X passed, Y failed, Z skipped}
**Status:** PASS (1pt) | FAIL (0pt)

### T-3: Test Coverage > Threshold
```bash
npm run test:coverage
```
**Expected:** > 80% (or project threshold)
**Actual:** {X}%
**Status:** PASS (1pt) | FAIL (0pt)

### T-4: Integration Tests Exist
**Check:** Integration test files present
**Actual:** {list or "none"}
**Status:** PASS (1pt) | FAIL (0pt)

### T-5: Integration Tests Pass
```bash
npm run test:integration
```
**Actual:** {results}
**Status:** PASS (1pt) | FAIL (0pt)

### T-6: Edge Cases Tested
**Manual Check:** Boundary conditions, empty inputs, max values
**Status:** PASS (1pt) | FAIL (0pt)

### T-7: Error Paths Tested
**Manual Check:** Error scenarios have test coverage
**Status:** PASS (1pt) | FAIL (0pt)

### T-8: No Skipped Tests
```bash
grep -rn "\.skip\|xit\|xdescribe" . --include="*.test.ts" --include="*.spec.ts" | wc -l
```
**Expected:** 0 skipped tests in new code
**Actual:** {count}
**Status:** PASS (1pt) | FAIL (0pt)

### T-9: Test Isolation (No Shared State)
**Manual Check:** Tests don't depend on execution order
**Status:** PASS (1pt) | FAIL (0pt)

### T-10: Manual Testing Complete
**Checklist:**
- [ ] Feature works as expected
- [ ] UI renders correctly (if applicable)
- [ ] Error states handled gracefully
**Status:** PASS (1pt) | FAIL (0pt)

**Testing Score:** X/10
```

### 4.3 Security (10 points)

```markdown
## Security Validation: X/10

### S-1: No Hardcoded Credentials
```bash
grep -rn "password.*=.*['\"]" . --include="*.ts" | grep -v ".env\|test\|mock\|example" | wc -l
grep -rn "apiKey.*=.*['\"]" . --include="*.ts" | grep -v ".env\|test\|mock\|example" | wc -l
grep -rn "secret.*=.*['\"]" . --include="*.ts" | grep -v ".env\|test\|mock\|example" | wc -l
```
**Expected:** 0 matches
**Actual:** {count}
**Status:** PASS (1pt) | FAIL (0pt)

### S-2: Input Validation Implemented
**Check:** All user inputs validated (forms, API params)
**Files Checked:** {list}
**Status:** PASS (1pt) | FAIL (0pt)

### S-3: SQL Injection Prevention
```bash
grep -rn "raw\|execute\|\$queryRaw" . --include="*.ts" | grep -v test | head -5
```
**Check:** Raw queries use parameterization
**Status:** PASS (1pt) | FAIL (0pt)

### S-4: XSS Prevention
**Check:** User content escaped, dangerouslySetInnerHTML avoided or sanitized
**Status:** PASS (1pt) | FAIL (0pt)

### S-5: HTTPS Enforced
```bash
grep -rn "http://" . --include="*.ts" | grep -v test | grep -v localhost | wc -l
```
**Expected:** 0 non-localhost HTTP URLs
**Status:** PASS (1pt) | FAIL (0pt)

### S-6: CORS Configured Properly
**Check:** Only necessary origins allowed
**Config Location:** {file}
**Status:** PASS (1pt) | FAIL (0pt)

### S-7: Rate Limiting Active
**Check:** API endpoints have rate limiting
**Status:** PASS (1pt) | FAIL (0pt)

### S-8: Auth Tokens Secure
**Check:** Tokens in httpOnly cookies, appropriate expiry
**Status:** PASS (1pt) | FAIL (0pt)

### S-9: Dependency Audit Clean
```bash
npm audit --audit-level=high
```
**Expected:** No high/critical vulnerabilities
**Actual:** {count} high, {count} critical
**Status:** PASS (1pt) | FAIL (0pt)

### S-10: Secrets in Environment Variables
**Check:** All secrets from process.env, not hardcoded
**Status:** PASS (1pt) | FAIL (0pt)

**Security Score:** X/10
```

### 4.4 Performance (10 points)

```markdown
## Performance Validation: X/10

### P-1: Page Load Time < 2s
**Method:** {Lighthouse | manual timing}
**Actual:** {X}s
**Status:** PASS (1pt) | FAIL (0pt)

### P-2: API Response Time < 200ms
```bash
curl -w "%{time_total}" -o /dev/null -s {endpoint}
```
**Actual:** {X}s
**Status:** PASS (1pt) | FAIL (0pt)

### P-3: Database Queries Optimized
**Check:** EXPLAIN ANALYZE on new queries shows efficient plans
**Status:** PASS (1pt) | FAIL (0pt)

### P-4: No N+1 Queries
**Check:** Query logs show efficient loading (eager loading where needed)
**Status:** PASS (1pt) | FAIL (0pt)

### P-5: Indexes Present
**Check:** Indexes on frequently queried columns
**Status:** PASS (1pt) | FAIL (0pt)

### P-6: No Memory Leaks
**Check:** Memory usage stable over repeated operations
**Status:** PASS (1pt) | FAIL (0pt)

### P-7: Bundle Size Acceptable
**Check:** No unexpectedly large bundles
**Status:** PASS (1pt) | FAIL (0pt)

### P-8: Images Optimized
**Check:** Appropriate formats, lazy loading
**Status:** PASS (1pt) | FAIL (0pt)

### P-9: Caching Implemented
**Check:** Appropriate cache headers, application caching
**Status:** PASS (1pt) | FAIL (0pt)

### P-10: No Render Blocking
**Check:** Critical resources prioritized, scripts deferred
**Status:** PASS (1pt) | FAIL (0pt)

**Performance Score:** X/10
```

### 4.5 Documentation (10 points)

```markdown
## Documentation Validation: X/10

### D-1: Code Comments Explain Why
**Manual Check:** Comments explain rationale, not syntax
**Status:** PASS (1pt) | FAIL (0pt)

### D-2: README Updated
**Check:** New features documented
**Status:** PASS (1pt) | FAIL (0pt)

### D-3: API Documentation Complete
**Check:** Swagger/OpenAPI updated for new endpoints
**Status:** PASS (1pt) | FAIL (0pt)

### D-4: Environment Variables Documented
**Check:** .env.example has new variables
**Status:** PASS (1pt) | FAIL (0pt)

### D-5: Setup Instructions Current
**Check:** README install steps work
**Status:** PASS (1pt) | FAIL (0pt)

### D-6: Architecture Decisions Recorded
**Check:** Significant decisions documented
**Status:** PASS (1pt) | FAIL (0pt)

### D-7: Breaking Changes Noted
**Check:** CHANGELOG updated if breaking changes
**Status:** PASS (1pt) | FAIL (0pt)

### D-8: Inline Examples Present
**Check:** Complex functions have usage examples
**Status:** PASS (1pt) | FAIL (0pt)

### D-9: Error Messages Helpful
**Check:** Errors guide user to resolution
**Status:** PASS (1pt) | FAIL (0pt)

### D-10: Dependencies Justified
**Check:** New deps have documented rationale
**Status:** PASS (1pt) | FAIL (0pt)

**Documentation Score:** X/10
```

### 4.6 Infrastructure (10 points)

```markdown
## Infrastructure Validation: X/10

### I-1: Environment Parity
**Check:** Dev/staging/prod configs consistent
**Status:** PASS (1pt) | FAIL (0pt)

### I-2: Health Checks Present
```bash
curl -s {health-endpoint}
```
**Status:** PASS (1pt) | FAIL (0pt)

### I-3: Logging Structured
**Check:** JSON logging with context
**Status:** PASS (1pt) | FAIL (0pt)

### I-4: Error Monitoring Connected
**Check:** Errors captured (Sentry, etc.)
**Status:** PASS (1pt) | FAIL (0pt)

### I-5: Graceful Shutdown
**Check:** SIGTERM handled, connections drained
**Status:** PASS (1pt) | FAIL (0pt)

### I-6: Database Migrations Safe
**Check:** Migrations reversible, no data loss
**Status:** PASS (1pt) | FAIL (0pt)

### I-7: Secrets Management
**Check:** No secrets in repo
**Status:** PASS (1pt) | FAIL (0pt)

### I-8: Backup Strategy
**Check:** Database backups configured
**Status:** PASS (1pt) | FAIL (0pt)

### I-9: CI/CD Pipeline Works
**Check:** Pipeline runs successfully
**Status:** PASS (1pt) | FAIL (0pt)

### I-10: Rollback Possible
**Check:** Can revert to previous version
**Status:** PASS (1pt) | FAIL (0pt)

**Infrastructure Score:** X/10
```

---

## Step 5: Generate VERIFICATION.md Report

**Purpose:** Create comprehensive, honest verification report.

**Output:** `.planning/phases/{N}-{name}/{N}-VERIFICATION.md`

```markdown
---
phase: {N}-{name}
verified_at: "{ISO timestamp}"
verified_by: fire-verifier
musthave_score: "{X}/{Y}"
warrior_score: "{XX}/70"
overall_status: "{APPROVED | CONDITIONAL | REJECTED}"
---

# Verification Report: Phase {N} - {name}

## Executive Summary

| Category | Score | Status |
|----------|-------|--------|
| **Must-Haves** | {X}/{Y} | {PASS/FAIL} |
| **Code Quality** | {X}/10 | {PASS/FAIL} |
| **Testing** | {X}/10 | {PASS/FAIL} |
| **Security** | {X}/10 | {PASS/FAIL} |
| **Performance** | {X}/10 | {PASS/FAIL} |
| **Documentation** | {X}/10 | {PASS/FAIL} |
| **Infrastructure** | {X}/10 | {PASS/FAIL} |
| **WARRIOR Total** | {XX}/70 | |

**Overall Status:** {APPROVED | CONDITIONAL | REJECTED}

---

## Must-Haves: {X}/{Y} {STATUS}

{Detailed truths, artifacts, key_links verification from Step 3}

---

## WARRIOR Validation: {XX}/70

{Detailed 6-category results from Step 4}

---

## Gaps Identified

### Critical Gaps (Must Fix Before Proceeding)
| Gap | Category | Impact | Remediation |
|-----|----------|--------|-------------|
| {gap} | {category} | {High} | {specific fix} |

### Minor Gaps (Should Fix)
| Gap | Category | Impact | Recommendation |
|-----|----------|--------|----------------|
| {gap} | {category} | {Low/Med} | {suggestion} |

### Deferred Items (Acknowledged)
| Item | Reason | Planned Resolution |
|------|--------|-------------------|
| {item} | {reason} | {when/how} |

---

## Recommendations

### Immediate Actions Required
1. {Specific action with steps}
2. {Specific action with steps}

### Suggested Improvements
1. {Improvement}
2. {Improvement}

---

## Verification Decision

**Decision:** {APPROVED | CONDITIONAL | REJECTED}

**Rationale:**
{Explanation of decision based on scores and gaps}

**Conditions (if CONDITIONAL):**
- [ ] {Condition 1 must be met}
- [ ] {Condition 2 must be met}

**Next Steps:**
{Based on decision: proceed, fix gaps, or re-plan}

---

*Verified: {timestamp}*
*Verifier: fire-verifier*
```

---

## Step 6: Route Based on Results

**Purpose:** Direct user to appropriate next action.

### Decision Matrix

| Must-Have Score | WARRIOR Score | Decision |
|-----------|---------------|----------|
| All pass | >= 54 (90%) | APPROVED |
| All pass | 48-53 (80-89%) | APPROVED with notes |
| All pass | 42-47 (70-79%) | CONDITIONAL |
| All pass | < 42 | CONDITIONAL with critical fixes |
| Any fail | Any | REJECTED |

### APPROVED

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ VERIFICATION PASSED                                                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Phase {N} - {name}                                                          ║
║                                                                              ║
║  Must-Haves: {X}/{X}                                                     ║
║  WARRIOR Validation: {XX}/70                                                 ║
║                                                                              ║
║  Phase {N} is COMPLETE                                                       ║
║                                                                              ║
║  Options:                                                                    ║
║    Run `/fire-2-plan {N+1}` to plan next phase                              ║
║    Run `/fire-5-handoff` to create session handoff                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### CONDITIONAL

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ VERIFICATION PASSED WITH GAPS                                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Phase {N} - {name}                                                          ║
║                                                                              ║
║  Must-Haves: {X}/{Y} ({count} gaps)                                      ║
║  WARRIOR Validation: {XX}/70 ({count} gaps)                                  ║
║                                                                              ║
║  Gaps:                                                                       ║
║    - {Gap 1 description}                                                     ║
║    - {Gap 2 description}                                                     ║
║                                                                              ║
║  Options:                                                                    ║
║    A) Accept gaps, proceed: `/fire-2-plan {N+1}`                            ║
║    B) Close gaps: `/fire-2-plan {N} --gaps`                                 ║
║    C) Create handoff with gaps noted: `/fire-5-handoff`                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### REJECTED

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ VERIFICATION FAILED                                                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Phase {N} - {name}                                                          ║
║                                                                              ║
║  Must-Haves: {X}/{Y} FAILED                                              ║
║  WARRIOR Validation: {XX}/70 FAILED                                          ║
║                                                                              ║
║  Critical Failures:                                                          ║
║    - {Critical failure 1}                                                    ║
║    - {Critical failure 2}                                                    ║
║                                                                              ║
║  Action Required:                                                            ║
║    Run `/fire-2-plan {N} --gaps` to create gap closure plan                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Step 7: Update CONSCIENCE.md

**Purpose:** Reflect verification results in project state.

```markdown
## WARRIOR Integration
- **Validation Status:** Phase {N} {APPROVED|CONDITIONAL|REJECTED} {XX}/70 checks
- **Gaps:** {list or "None"}
- **Last verified:** {timestamp}

## Dominion Flow Progress Tracking
### Phase Status
| Phase | Name | Status | Plans | Verification |
|-------|------|--------|-------|--------------|
| {N} | {name} | {Verified} | {X} | {XX}/70 |
```

</process>

---

## Agent Spawning

| Agent | When | Purpose |
|-------|------|---------|
| **fire-verifier** | Always | Execute all verification checks with evidence |

---

## Success Criteria

### Required Outputs
- [ ] All Must-Haves verified (truths, artifacts, key_links)
- [ ] All 60 WARRIOR checks executed
- [ ] `{N}-VERIFICATION.md` created with evidence
- [ ] CONSCIENCE.md updated with verification status
- [ ] Clear routing based on results

### Quality Checks
- [ ] Every PASS has evidence (command output or manual check description)
- [ ] Every FAIL has specific details
- [ ] Gaps categorized by severity
- [ ] Recommendations are actionable

---

## Scoring Thresholds

| Threshold | WARRIOR Score | Action |
|-----------|---------------|--------|
| **Excellent** | 54-60 (90%+) | APPROVED |
| **Good** | 48-53 (80-89%) | APPROVED with notes |
| **Acceptable** | 42-47 (70-79%) | CONDITIONAL |
| **Needs Work** | 36-41 (60-69%) | CONDITIONAL with critical fixes |
| **Insufficient** | <36 (<60%) | REJECTED |

**Override:** Critical security or must-have failures override score thresholds.

---

## References

- **Agent:** `@agents/fire-verifier.md` - Verification agent
- **Template:** `@templates/verification.md` - Report template
- **Checklist:** `@references/validation-checklist.md` - 70-point checklist
- **Brand:** `@references/ui-brand.md` - Visual output standards
