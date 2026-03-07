---
description: Verify phase completion with must-haves and 70-point validation
---

# /fire-4-verify

> Verify phase N with combined must-haves and WARRIOR 70-point validation

---

## Purpose

Perform comprehensive verification of a completed phase by combining Dominion Flow's goal-backward must-haves verification with 70-point quality validation checklist. Generates a detailed verification report and routes to gap closure if needed.

---

## Arguments

```yaml
arguments:
  phase_number:
    required: true
    type: integer
    description: "Phase number to verify (e.g., 1, 2, 3)"
    example: "/fire-4-verify 3"

optional_flags:
  --detailed: "Include verbose output for all checks"
  --quick: "Run only critical checks (must-haves + security)"
  --report-only: "Generate report without routing to gap closure"
```

---

## Process

### Step 1: Load Verification Context

```
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
                         DOMINION FLOW > PHASE {N} VERIFICATION
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
```

**Load Context:**
```markdown
@.planning/CONSCIENCE.md
@.planning/phases/{N}-{name}/*.BLUEPRINT.md      # All plans
@.planning/phases/{N}-{name}/*-RECORD.md   # All summaries
```

**Extract:**
- All must_haves from plan frontmatter
- All warrior_validation items from plans
- Skills applied during execution
- Key files created/modified

### Step 2: Spawn fire-verifier

```
â—† Spawning fire-verifier for Phase {N}...
```

**Verifier Context:**
```markdown
<verification_scope>
Phase: {N} - {name}
Plans to Verify: {list}
Total Must-Haves: {count}
WARRIOR Checks: 70 items across 8 categories
</verification_scope>

<must_haves>
{Aggregated must_haves from all plans}
</must_haves>

<warrior_checklist>
@references/validation-checklist.md
</warrior_checklist>
```

### Step 2.5: Spawn fire-reviewer in parallel (v8.0)

```
IF --quick flag NOT set:

  â—† Spawning fire-reviewer alongside fire-verifier...

  Task(subagent_type="fire-reviewer", prompt="""
    <review_scope>
    Phase: {N} - {name}
    Review Depth: normal
    </review_scope>

    <files_to_review>
    {key_files from all RECORD.md frontmatter}
    </files_to_review>

    <plan_intent>
    {Quick Summary from each RECORD.md}
    </plan_intent>

    <simplicity_mandate>STRICT</simplicity_mandate>

    Output to: .planning/phases/{N}-{name}/{N}-REVIEW.md
  """)

ELSE:
  # --quick mode: skip review, only run critical checks
```

### Step 3: Must-Haves Verification

**Verify Truths:**
Observable behaviors that must be demonstrable.

```markdown
### Truths Verification

| Truth Statement | Verification Command | Result |
|-----------------|---------------------|--------|
| {statement} | {command} | PASS/FAIL |
```

**Example:**
```bash
# Truth: "User can paginate through results"
curl -s "http://localhost:3000/api/products?limit=5" | jq '.data | length'
# Expected: 5
# Result: PASS
```

**Verify Artifacts:**
Files must exist with expected exports and contents.

```markdown
### Artifacts Verification

| File | Exports | Contains | Result |
|------|---------|----------|--------|
| {path} | {exports} | {patterns} | PASS/FAIL |
```

**Example:**
```bash
# Artifact: server/services/pagination.service.ts exports paginate
grep -n "export.*paginate" server/services/pagination.service.ts
# Expected: Match found
# Result: PASS
```

**Verify Key Links:**
Components must be properly wired together.

```markdown
### Key Links Verification

| From | To | Via | Result |
|------|----|----|--------|
| {component-a} | {component-b} | {integration} | PASS/FAIL |
```

**Example:**
```bash
# Key Link: products-route uses pagination-service
grep -n "import.*pagination" server/routes/products.ts
grep -n "paginate" server/routes/products.ts
# Expected: Both match
# Result: PASS
```

### Step 4: WARRIOR 70-Point Validation

**Categories (8 total, 70 checks):**

#### Code Quality (6 checks)
```bash
# 1. Project builds without errors
npm run build

# 2. No TypeScript errors
npm run typecheck

# 3. ESLint compliance
npm run lint

# 4. No console.logs in production code
grep -r "console.log" src/ --include="*.ts" --include="*.tsx" | grep -v ".test." | wc -l
# Expected: 0

# 5. Code comments present on complex functions
# Manual check or AST analysis

# 6. Functions have JSDoc/TSDoc
# Manual check or documentation tool
```

#### Testing (5 checks)
```bash
# 1. Unit tests passing
npm run test

# 2. Integration tests passing
npm run test:integration

# 3. Coverage > threshold (default 80%)
npm run test:coverage

# 4. No skipped tests
grep -r "\.skip\|xit\|xdescribe" **/*.test.* | wc -l
# Expected: 0

# 5. Manual testing complete
# Checkpoint verification
```

#### Security (8 checks)
```bash
# 1. No hardcoded credentials
grep -rE "(password|secret|key)\s*=\s*['\"][^'\"]+['\"]" src/ | grep -v ".test." | wc -l
# Expected: 0

# 2. Input validation implemented
# Check for validation middleware/schemas

# 3. SQL injection prevention
# Check for parameterized queries

# 4. XSS protection
# Check for output encoding

# 5. HTTPS enforced
# Check for SSL/TLS configuration

# 6. CORS configured properly
# Check CORS middleware settings

# 7. Rate limiting active
# Check for rate limiting middleware

# 8. Auth tokens secure (httpOnly, secure flags)
# Check cookie configuration
```

#### Performance (6 checks)
```bash
# 1. Page load times < threshold
# Lighthouse or manual measurement

# 2. Database queries optimized
# Check for N+1, missing indexes

# 3. No N+1 queries
# Query logging analysis

# 4. Indexes exist on queried columns
# Database schema inspection

# 5. No memory leaks
# Memory profiling

# 6. API response times < 200ms
# Load testing or manual measurement
```

#### Documentation (4 checks)
```bash
# 1. README current
# Manual check

# 2. API documentation complete
# Check swagger/OpenAPI spec

# 3. Setup instructions work
# Manual verification

# 4. Code comments explain "why" not "what"
# Manual review
```

#### Database (5 checks)
```bash
# 1. Migrations up to date
npm run db:migrate:status

# 2. Schema matches models
npm run db:validate

# 3. Backup strategy documented
# Manual check

# 4. Connection pooling configured
# Check database config

# 5. Transactions used appropriately
# Code review
```

#### API Design (6 checks)
```bash
# 1. RESTful conventions followed
# Manual review

# 2. Versioning implemented
# Check for /v1/ or header versioning

# 3. Error responses consistent
# Test error endpoints

# 4. Pagination on list endpoints
# Check list endpoints

# 5. Authentication required where needed
# Check protected routes

# 6. Rate limiting per endpoint
# Check rate limit config
```

#### Infrastructure (4 checks)
```bash
# 1. Environment variables documented
# Check .env.example

# 2. Docker/deployment config present
# Check Dockerfile, docker-compose

# 3. CI/CD pipeline configured
# Check .github/workflows or equivalent

# 4. Logging implemented
# Check logging configuration
```

#### E2E Testing - Playwright (10 checks)
```bash
# 1. Playwright installed and configured
npx playwright --version
ls playwright.config.{ts,js}

# 2. Browsers installed
npx playwright install --dry-run

# 3. Critical user flows covered (login, signup, core CRUD)
# Check E2E test files exist

# 4. All E2E tests pass
npx playwright test

# 5. Cross-browser testing (chromium + firefox)
npx playwright test --project=chromium
npx playwright test --project=firefox

# 6. Mobile viewport coverage
# Check for mobile viewport project or responsive checks

# 7. API response assertions in E2E tests
# Check tests validate API responses, not just UI

# 8. Visual regression baselines
npx playwright test --update-snapshots

# 9. Test isolation (no shared state)
npx playwright test --shard=1/3

# 10. No console errors during E2E runs
# Check via Playwright MCP: browser_console_messages level=error
```

### Step 5: Generate Verification Report

**Create:** `.planning/phases/{N}-{name}/{N}-VERIFICATION.md`

```markdown
# Verification Report: Phase {N}

## Summary
- **Must-Haves:** {X}/{Y} PASSED
- **WARRIOR Validation:** {X}/70 PASSED
- **Overall Status:** PASSED | PASSED WITH GAPS | FAILED

---

## Must-Haves: {X}/{Y} {STATUS}

### Truths
| # | Statement | Command | Result |
|---|-----------|---------|--------|
| 1 | {statement} | {command} | âœ“ PASS |
| 2 | {statement} | {command} | âœ— FAIL |

### Artifacts
| # | File | Exports | Contains | Result |
|---|------|---------|----------|--------|
| 1 | {path} | {exports} | {patterns} | âœ“ PASS |

### Key Links
| # | From | To | Via | Result |
|---|------|----|----|--------|
| 1 | {a} | {b} | {via} | âœ“ PASS |

---

## WARRIOR Validation: {X}/70 {STATUS}

### Code Quality (6/6) âœ“
- [x] Project builds without errors
- [x] No TypeScript errors
- [x] ESLint compliance
- [x] No console.logs in production
- [x] Code comments present
- [x] Functions have JSDoc

### Testing (4/5) âš 
- [x] Unit tests passing
- [x] Integration tests passing
- [x] Coverage > 80% (current: 94%)
- [x] No skipped tests
- [ ] E2E tests passing (deferred)

### Security (8/8) âœ“
[All checks passing]

### Performance (6/6) âœ“
[All checks passing]

### Documentation (4/4) âœ“
[All checks passing]

### Database (5/5) âœ“
[All checks passing]

### API Design (6/6) âœ“
[All checks passing]

### Infrastructure (4/4) âœ“
[All checks passing]

---

## Gaps Identified

### Gap 1: E2E Tests (Minor)
- **Category:** Testing
- **Impact:** Low (unit + integration coverage sufficient)
- **Recommendation:** Defer to Phase {N+2} per roadmap
- **Action:** Document in CONSCIENCE.md, proceed

### Gap 2: {name} (if any)
[Details]

---

## Verification Decision

**Status:** APPROVED âœ“ | APPROVED WITH GAPS âš  | REJECTED âœ—

**Recommendation:** {next step}

---

*Verified: {timestamp}*
*Verifier: fire-verifier*
```

### Step 5.5: Merge Verification + Review Results (v8.0)

```
IF reviewer was spawned (--quick NOT set):
  Read .planning/phases/{N}-{name}/{N}-REVIEW.md

  Apply combined verdict matrix (same as fire-3-execute Step 8.5):

  PASSED requires BOTH:
    - verifier: APPROVED (warrior >= 49/70)
    - reviewer: APPROVE (no CRITICAL, <3 HIGH)

  Any BLOCK from reviewer downgrades result to PASSED WITH GAPS minimum.

  DISAGREEMENT HANDLING:
    Verifier PASSED + Reviewer BLOCK:
      → Downgrade to PASSED WITH GAPS
      → "Code passes functional checks but has quality/simplicity issues."

    Verifier FAILED + Reviewer APPROVE:
      → Keep FAILED (functional correctness takes priority)
      → "Code is clean but doesn't work."
```

### Step 5.6: FaR Confidence Calibration (v10.1)

> **Research basis (v10.1):** Xiong et al. "Can LLMs Express Their Uncertainty?" (ACL 2024) —
> Fact-and-Reflection (FaR) prompting reduces Expected Calibration Error by 23.5%.
> Agents that first enumerate known facts, then reflect on uncertainty, produce
> dramatically more accurate confidence scores than agents that just guess a number.
> Applied: Added mandatory FaR step before final verification verdict.

Before assigning the final verdict, the verifier MUST perform a two-phase confidence assessment:

```
═══════════════════════════════════════════════════════
  FaR CONFIDENCE CALIBRATION
═══════════════════════════════════════════════════════

PHASE 1: FACT ELICITATION
List every concrete, observable fact about this phase's correctness:

  Facts FOR correctness (evidence it works):
    1. {fact} — source: {test output / manual check / code review}
    2. {fact} — source: {specific evidence}
    3. ...

  Facts AGAINST correctness (evidence of problems):
    1. {fact} — source: {test failure / gap / uncertainty}
    2. {fact} — source: {specific evidence}
    3. ...

  Unknown / Untestable:
    1. {thing we cannot verify} — why: {reason}
    2. ...

PHASE 2: REFLECTION
Given the facts above, reflect on overall confidence:

  - How many critical paths have direct evidence? {N}/{total}
  - Are the "against" facts blockers or minor gaps?
  - What is the worst plausible failure mode?
  - If this shipped to production right now, what breaks?

CALIBRATED CONFIDENCE: {0-100}%

  Interpretation:
    90-100% — High confidence. Ship it.
    70-89%  — Moderate confidence. Acceptable with noted gaps.
    50-69%  — Low confidence. Significant unknowns remain.
    <50%    — Very low. Do not approve without more evidence.

═══════════════════════════════════════════════════════
```

**Integration with verdict:**
- FaR confidence is INFORMATIONAL — it does not override the 70-point checklist
- BUT if FaR confidence < 50% AND checklist score ≥ 70%, flag a WARNING:
  "Checklist passes but verifier confidence is low. Review the 'Unknown/Untestable'
  list before approving."
- Include FaR confidence in the verification report under a "Confidence Assessment" section
- Track FaR confidence across phases to detect calibration drift

**Skip condition:** If `--quick` flag is set, skip FaR and use raw checklist score only.

### Step 5.75: Dual-Verification — Read from Authoritative Source (v11.0)

> **Research basis (v11.0):** Failure pattern mining (8 instances of silent persistence
> failures across multiple projects) — write operations appear to succeed but changes
> don't persist. Root causes: column name mismatches, missing server handlers,
> computed fields silently zeroing on UPDATE. The fix: verify by READING from the
> authoritative source, not trusting the write response.

For each must-have that involves a data write (create, update, delete):

```
FOR each must_have WHERE type == "data_persistence":

  1. WRITE: Execute the operation (already done by executor)

  2. READ: Query the authoritative data source directly
     - Database: SELECT from the actual table, not the API response
     - File: Read the file back, don't trust the write return value
     - API: GET the resource after POST/PUT, compare fields

  3. COMPARE: Verify the written values match expected values
     field_by_field_check:
       FOR each field in expected_values:
         IF source_value != expected_value:
           FLAG: "Silent persistence failure: {field} expected={expected} actual={actual}"

  4. REPORT:
     IF all fields match: PASS (verified at source)
     IF mismatches found: FAIL with specific field-level report
```

**Common silent failure patterns to check:**
- `firstName` vs `first_name` column mismatch (frontend sends camelCase, DB uses snake_case)
- Computed/JOINed fields sent to UPDATE that silently zero the value
- API returns `{ success: true }` but handler doesn't actually call the DB
- Frontend shows optimistic update but server rejected the change

**Skip condition:** Must-haves that are purely UI/display or configuration (no data writes).

### Step 6: Route Based on Results

**If PASSED (all checks):**
```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âœ“ VERIFICATION PASSED                                                        â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Phase {N} - {name}                                                          â•‘
â•‘                                                                              â•‘
â•‘  Must-Haves: {X}/{X} âœ“                                                   â•‘
â•'  WARRIOR Validation: 70/70 âœ"                                                 â•'
â•'  Code Review: {verdict} ({findings summary})                                 â•'
â•'  Simplicity: {N} over-engineering flags                                      â•'
â•'                                                                              â•'
â•'  â†' Phase {N} is COMPLETE                                                     â•‘
â•‘  â†’ Ready for `/fire-2-plan {N+1}` or `/fire-5-handoff`                     â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

**If PASSED WITH GAPS:**
```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âš  VERIFICATION PASSED WITH GAPS                                              â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Phase {N} - {name}                                                          â•‘
â•‘                                                                              â•‘
â•‘  Must-Haves: {X}/{Y} (1 gap)                                             â•‘
â•'  WARRIOR Validation: 65/70 (2 gaps)                                          â•'
â•'  Code Review: {verdict} ({findings summary})                                 â•'
â•'  Simplicity: {N} over-engineering flags                                      â•'
â•'                                                                              â•'
â•'  Gaps:                                                                       â•‘
â•‘    âš  E2E tests not implemented (deferred)                                    â•‘
â•‘    âš  API versioning incomplete                                               â•‘
â•‘                                                                              â•‘
â•‘  Options:                                                                    â•‘
â•‘    A) Accept gaps and proceed: `/fire-2-plan {N+1}`                         â•‘
â•‘    B) Close gaps: `/fire-2-plan {N} --gaps`                                 â•‘
â•‘    C) Create handoff with gaps noted: `/fire-5-handoff`                     â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

**If FAILED:**
```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ âœ— VERIFICATION FAILED                                                        â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Phase {N} - {name}                                                          â•‘
â•‘                                                                              â•‘
â•‘  Must-Haves: {X}/{Y} FAILED                                              â•‘
â•'  WARRIOR Validation: {X}/70 FAILED                                           â•'
â•'  Code Review: {verdict} ({findings summary})                                 â•'
â•'  Simplicity: {N} over-engineering flags                                      â•'
â•'                                                                              â•'
â•'  Critical Failures:                                                          â•‘
â•‘    âœ— Truth: "User can log in" - Not verified                                 â•‘
â•‘    âœ— Security: Hardcoded credentials found                                   â•‘
â•‘    âœ— Testing: Coverage 45% (required 80%)                                    â•‘
â•‘                                                                              â•‘
â•‘  Action Required:                                                            â•‘
â•‘    â†’ Run `/fire-2-plan {N} --gaps` to create gap closure plan               â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

### Step 7: Update CONSCIENCE.md

```markdown
## WARRIOR Integration
- Validation Status: Phase {N} {result} {X}/70 checks
- Gaps: {list or "None"}
- Last verified: {timestamp}
```

### Step 7.25: Post-Verification State Transition (v10.0 — Automatic Routing)

> **Research basis (v10.0):** Internal gap analysis — after verification completes, the user
> must manually decide what to do next. This creates a decision bottleneck. Automatic routing
> based on verification result eliminates the gap between "verified" and "next action."
> SICA (Self-Improving Coding Agent, ICLR 2025) confirms: automated iteration loops
> outperform manual checkpoint-and-continue by eliminating human latency.

**AUTOMATIC routing based on verification result (no user input needed):**

```
SWITCH verification_result:

  CASE "PASSED" (score >= 63/70, all must-haves green):
    # Phase is complete — advance
    1. Update CONSCIENCE.md: phase status = COMPLETE
    2. IF next phase exists in VISION.md:
       → Display: "Phase {N} PASSED. Auto-advancing to Phase {N+1}."
       → Suggest: "/fire-2-plan {N+1}"
    3. IF no next phase (milestone complete):
       → Display: "Milestone COMPLETE. Ready for /fire-5-handoff."
       → Suggest: "/fire-5-handoff"

  CASE "PASSED_WITH_GAPS" (must-haves green, score 49-62/70):
    # Gaps are non-critical — route based on gap severity
    gap_severity = classify_gaps(gaps_list):
      COSMETIC (docs, comments, minor style) → auto-advance, log deferred
      FUNCTIONAL (missing tests, edge cases) → suggest gap closure plan
      SECURITY (any security gap) → BLOCK, force gap closure

    IF all gaps COSMETIC:
      → Display: "Phase {N} PASSED with cosmetic gaps (deferred)."
      → Auto-advance same as PASSED
    ELSE:
      → Display: "Phase {N} has {N} functional gaps. Close before advancing?"
      → Suggest: "/fire-2-plan {N} --gaps"

  CASE "FAILED" (missing must-haves OR score < 49/70):
    # Phase needs re-work — auto-create gap closure plan
    1. Extract failed checks into gap list
    2. Display: "Phase {N} FAILED. Creating gap closure plan."
    3. Auto-generate: /fire-2-plan {N} --gaps --from-failures "{failed_checks}"
    4. Do NOT advance — loop back to execute → verify
```

**State transition diagram:**

```
  PASSED ──────────→ /fire-2-plan {N+1} (next phase)
                  └→ /fire-5-handoff (if last phase)

  PASSED_WITH_GAPS
    ├─ cosmetic ──→ auto-advance (gaps deferred)
    └─ functional → /fire-2-plan {N} --gaps

  FAILED ─────────→ /fire-2-plan {N} --gaps --from-failures
                    (loop: plan → execute → verify until PASSED)
```

### Step 7.5: Evolutionary Skill Extraction (v5.0 — Auto-Triggered)

**Research basis:** SAGE (2025) — 8.9% higher completion, 26% fewer steps via skill augmentation

After successful verification (PASS or PASS WITH GAPS), scan the phase for extractable patterns:

```
IF verification_status != "FAILED":

  # 1. Scan execution summaries for skill candidates
  FOR each RECORD.md in phase:
    Analyze:
      - Novel code patterns created
      - Debugging strategies that worked
      - Architectural decisions made
      - Workarounds applied

  # 2. Filter for reusable patterns (from Evolutionary Skill Synthesis)
  candidates = patterns WHERE:
    - Pattern is generalizable (not project-specific)
    - Pattern solved a non-trivial problem
    - Pattern involved >3 files OR >30 minutes of work
    - Pattern required research or multiple attempts

  # 3. For each candidate, create quarantine skill
  IF candidates.length > 0:
    FOR each candidate:
      Generate skill document (problem, solution, code example, tags)
      Save to: ~/.claude/plugins/warrior-workflow/skills-library/_quarantine/{name}.md
      Security scan: no exec(), eval(), hardcoded credentials

    Display:
    "+--------------------------------------------------------------+"
    "| SKILL CANDIDATES DISCOVERED                                   |"
    "+--------------------------------------------------------------+"
    "|                                                              |"
    "|  {N} new skill candidates from Phase {phase}:                |"
    "|    1. {name} — {category} — {one-sentence description}       |"
    "|    2. {name} — {category} — {one-sentence description}       |"
    "|                                                              |"
    "|  Location: skills-library/_quarantine/                       |"
    "|  Review: /fire-search --quarantine                          |"
    "|  Approve: Move to proper category directory                  |"
    "|                                                              |"
    "+--------------------------------------------------------------+"

  ELSE:
    Display: "No new skill candidates found in this phase."
```

**Quarantine lifecycle:**
- `_quarantine/` → User reviews → Approved → Move to category dir
- `_quarantine/` → User reviews → Rejected → Delete
- Auto-promoted after 3+ successful uses across 2+ projects

### Step 7.6: Hindsight for Failed Verifications (v6.0 — ECHO)

> **Research basis:** ECHO (Oct 2025) — Hindsight optimization. When verification finds
> failures that are then fixed, generate "what should have been done" as a synthetic
> positive example. Pre-seed utility_score at 0.8 (high value — these are hard-won lessons).

After verification finds must-have failures AND the fix is subsequently applied:

```
IF verification_status == "FAILED" OR verification_status == "PASS_WITH_GAPS":

  FOR each must_have that failed:
    # 1. Record what was expected vs what happened
    gap_record = {
      feature: "{feature name from must-have}",
      expected: "{what the must-have required}",
      actual: "{what verification found instead}",
      category: "{missing | broken | incomplete}"
    }

    # 2. After fix is applied (by /fire-3-execute --gaps or manual fix):
    # Generate hindsight lesson
    hindsight = generate:
      "VERIFICATION HINDSIGHT — Phase {N}: {feature}

      ## The Gap
      Must-have: {expected}
      Reality: {actual}
      Category: {category}

      ## The Lesson
      When building {feature type}, ensure {specific thing to check}
      because {why it was missed — root cause of the gap}.

      ## Prevention Pattern
      During planning: {what should have been in the plan}
      During execution: {what check would have caught this}
      During review: {what self-judge question would have flagged this}"

    # 3. Save and index
    Save to: .planning/phases/{N}-{name}/hindsight-{feature-slug}.md

    cd ~/.claude/memory
    npm run index-file -- ".planning/phases/{N}-{name}/hindsight-{feature-slug}.md"

    # 4. Pre-seed utility score at 0.8 (verification lessons are high-value)
    npm run track-usage -- --source ".planning/phases/{N}-{name}/hindsight-{feature-slug}.md" --helpful true

  Display:
  "+--------------------------------------------------------------+"
  "| VERIFICATION HINDSIGHT GENERATED                              |"
  "+--------------------------------------------------------------+"
  "|                                                              |"
  "|  {N} lesson(s) from failed must-haves:                       |"
  "|    1. {feature}: {one-sentence lesson}                        |"
  "|    2. {feature}: {one-sentence lesson}                        |"
  "|                                                              |"
  "|  Indexed into vector memory (utility: 0.8)                   |"
  "|  Future plans will find these via episodic recall.            |"
  "|                                                              |"
  "+--------------------------------------------------------------+"
```

**Why pre-seed at 0.8:** Verification failures represent hard-won knowledge. They are
lessons discovered only after building and testing — the most valuable kind of memory.
By pre-seeding utility at 0.8, two-phase retrieval (Gap 5) will prioritize these
over generic code snippets, ensuring future phases learn from past mistakes.

---

## Agent Spawning Instructions

### fire-verifier

**Agent File:** `@agents/fire-verifier.md`

**Context:**
```markdown
<phase_context>
Phase: {N} - {name}
Plans: {list}
</phase_context>

<must_haves>
{Aggregated from all plans}
</must_haves>

<warrior_checklist>
@references/validation-checklist.md
</warrior_checklist>
```

**Verifier Outputs:**
- `{N}-VERIFICATION.md`
- Gap analysis
- Recommendations

---

## Success Criteria

### Required Outputs
- [ ] All must-haves verified
- [ ] All WARRIOR checks executed
- [ ] `{N}-VERIFICATION.md` created
- [ ] `{N}-REVIEW.md` created (if --quick not set) (v8.0)
- [ ] Combined verdict evaluated — both verifier and reviewer must agree (v8.0)
- [ ] CONSCIENCE.md updated with verification status
- [ ] Clear routing to next action

### Completion Criteria
- **PASS:** All must-haves + >=63/70 WARRIOR checks
- **PASS WITH GAPS:** All must-haves + >=49/70 WARRIOR checks
- **FAIL:** Missing must-haves OR <49/70 WARRIOR checks

---

## References

- **Agent:** `@agents/fire-verifier.md` - Verification agent (functional checks)
- **Agent:** `@agents/fire-reviewer.md` - Review agent (quality + simplicity) (v8.0)
- **Template:** `@templates/verification.md` - Report template
- **Checklist:** `@references/validation-checklist.md` - 70-point checklist
- **Brand:** `@references/ui-brand.md` - Visual output standards
