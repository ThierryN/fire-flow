# Self-Questioning Task Generation - Curiosity-Driven Quality Assurance

## The Problem

After completing a task, agents declare success and move on. Nobody asks:
- "What could go WRONG with what I just built?"
- "What edge cases didn't I consider?"
- "What assumptions am I making that might be wrong?"
- "What would a malicious user try?"

This leaves blind spots that only surface in production.

### Why It Was Hard

- Agents are optimized to COMPLETE tasks, not QUESTION them
- Self-critique requires stepping outside the implementer mindset
- Most edge cases are invisible during normal development
- Security vulnerabilities require adversarial thinking

### Impact

- Bugs caught before verification = cheaper to fix
- Security holes identified before deployment
- Test coverage gaps exposed automatically
- Assumption documentation improves handoff quality

---

## The Solution

### Root Cause

Agents lack a structured "post-implementation reflection" step that generates
challenge questions about their own work.

### The Self-Questioning Protocol

After completing any task (executor, debugger, or loop iteration), the agent
generates 3-5 challenge questions in these categories:

```markdown
## Self-Questions Generated After [Task Name]

### Category 1: Failure Modes
"What happens if [dependency] is unavailable?"
"What happens if [input] is malformed/empty/huge?"
"What happens under concurrent access?"

### Category 2: Security
"Could a user bypass [check] by manipulating [surface]?"
"Is [data] exposed in logs/errors/responses?"
"Does [auth check] apply to ALL entry points?"

### Category 3: Data Integrity
"What happens if [operation] is interrupted mid-way?"
"Is there a race condition between [A] and [B]?"
"Are [related records] cleaned up on deletion?"

### Category 4: Assumptions
"I assumed [X] - is this actually guaranteed?"
"This works because [Y] - what if [Y] changes?"
"I relied on [Z] being present - what if it's not?"
```

### Automatic Test Generation (Novel: Curiosity-Driven Testing)

Each self-question feeds into test generation:

```markdown
## Self-Question -> Test Pipeline

Question: "What happens if the database connection drops during payment processing?"

Analysis:
  - Has test? NO
  - Risk level: CRITICAL (data integrity + financial)
  - Test type: Integration

Generated Test Stub:
```javascript
describe('Payment Processing - Connection Failure', () => {
  it('should rollback transaction if DB drops mid-payment', async () => {
    // Arrange: Set up payment intent
    // Act: Simulate connection drop during processing
    // Assert: Payment not partially committed
    // Assert: User notified of failure
    // Assert: Retry mechanism triggered
    throw new Error('TODO: Implement this critical test');
  });
});
```

Priority: P0 (CRITICAL - no test exists for financial edge case)
```

### Risk-Based Prioritization

Questions are ranked by risk category:

| Priority | Category | Action |
|----------|----------|--------|
| P0 | Security vulnerability | MUST fix before deploy |
| P1 | Data integrity risk | MUST test before deploy |
| P2 | UX degradation | SHOULD test |
| P3 | Performance edge case | NICE TO HAVE |

### Integration with Dominion Flow

**In fire-3-execute Step 10 (after verification):**
```markdown
### Step 10.5: Self-Questioning Reflection

After successful verification, each executor generates self-questions:

1. Review all code written in this plan
2. Generate 3-5 challenge questions per category
3. For each question:
   a. Check if existing test covers it
   b. If not: rate risk level
   c. If P0/P1: generate test stub
   d. Add to VERIFICATION.md "Open Questions" section

Output format in RECORD.md:
```yaml
self_questions:
  asked: 12
  covered_by_tests: 5
  test_stubs_generated: 4
  risk_breakdown:
    p0_security: 1
    p1_data: 2
    p2_ux: 1
    p3_perf: 0
  uncovered_risks:
    - question: "JWT refresh race condition under concurrent tabs"
      risk: P1
      test_stub: "tests/auth/concurrent-refresh.test.ts"
    - question: "File upload without size validation on backend"
      risk: P0
      test_stub: "tests/upload/size-limit.test.ts"
```

**In fire-loop (after each iteration):**
```markdown
## Iteration N Self-Check

Before proceeding to next iteration, ask:
1. "Did I actually verify what I just changed works?"
2. "Did I break anything adjacent to what I changed?"
3. "Is my assumption about [X] still valid?"

If any answer is uncertain: add to Task Recitation as remaining item.
```

**In fire-4-verify (enhanced):**
```markdown
## Verification - Self-Question Audit

Review self-questions from all executors:
- Total questions generated: [N]
- P0 risks without tests: [count] -> BLOCK deployment
- P1 risks without tests: [count] -> WARN
- Assumptions requiring validation: [list]
```

### Example Output

```markdown
## Self-Questions: Phase 3 - User Authentication

### Failure Modes
1. "What happens if Redis cache is down when checking session?"
   -> Test exists: NO -> Risk: P1 -> Stub generated

2. "What if JWT signing key rotates while tokens are in flight?"
   -> Test exists: NO -> Risk: P1 -> Stub generated

### Security
3. "Can a user forge a role claim in the JWT payload?"
   -> Test exists: YES (auth.test.ts:45) -> Covered

4. "Is the refresh token stored securely (httpOnly, secure, sameSite)?"
   -> Test exists: NO -> Risk: P0 -> Stub generated
   -> RECOMMENDATION: Add to security checklist skill

### Data Integrity
5. "What if user is deleted while they have active sessions?"
   -> Test exists: NO -> Risk: P2 -> Noted

### Assumptions
6. "I assumed bcrypt rounds=12 is sufficient for 2026 hardware"
   -> Valid? PROBABLY (NIST recommends 10+ for 2025)
   -> Document in ASSUMPTIONS.md

## Summary
- Questions asked: 6
- Already tested: 1 (17%)
- Test stubs needed: 3 (50%)
- Assumptions documented: 1
- Coverage gap: 83% of self-questions lack tests
```

---

## Testing the Fix

### Validation Criteria
- [ ] Self-questions generated after every plan execution
- [ ] At least 3 questions per execution
- [ ] P0 risks flagged and test stubs created
- [ ] Questions appear in VERIFICATION.md
- [ ] Test stubs are compilable (correct syntax, correct imports)

---

## Prevention

- Run self-questioning as MANDATORY step (not optional)
- Track question-to-test conversion rate over time
- Review "frequently asked" questions to identify systematic blind spots
- Feed high-frequency questions back into skills library

---

## Related Patterns

- [CONFIDENCE_ANNOTATION_PATTERN](./CONFIDENCE_ANNOTATION_PATTERN.md) - Low confidence triggers more questions
- [HEARTBEAT_PROTOCOL](./HEARTBEAT_PROTOCOL.md) - Mood "uncertain" triggers self-questioning
- [EVOLUTIONARY_SKILL_SYNTHESIS](./EVOLUTIONARY_SKILL_SYNTHESIS.md) - Frequent questions become defensive skills

---

## Common Mistakes to Avoid

- ❌ **Generic questions** ("does it work?") - Be SPECIFIC
- ❌ **Skipping security category** - Most critical blind spot
- ❌ **Not generating test stubs** - Questions without tests are just documentation
- ❌ **Only questioning your own code** - Question the INTEGRATION points too
- ❌ **Asking too many questions** - 3-5 high-quality > 20 generic

---

## Resources

- AgentEvolver: https://arxiv.org/abs/2511.10395 (self-questioning mechanism)
- OWASP Top 10: Security question templates
- Anthropic 2026 Report: "Agents learn when to ask for help"

---

## Time to Implement

**Phase 1 (template):** 15 minutes - Add self-questions block to executor summary template
**Phase 2 (test stubs):** 1 hour - Auto-generate test file stubs from questions
**Phase 3 (tracking):** 30 minutes - Add to verification checklist

## Difficulty Level

⭐⭐ (2/5) - Conceptually simple, the hard part is asking GOOD questions

---

**Author Notes:**
The most valuable self-question I've ever generated was: "What happens if two browser
tabs refresh the JWT token simultaneously?" This uncovered a race condition that would
have caused random logouts in production. One question, one test, one critical bug caught.

The key insight from AgentEvolver: curiosity is a SKILL that can be structured.
Don't just ask "what could go wrong?" - ask SPECIFIC questions in SPECIFIC categories.
That's what turns vague anxiety into actionable test coverage.
