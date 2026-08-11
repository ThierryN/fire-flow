# Multi-Perspective Code Review - 14 Specialized Reviewer Pattern

## The Problem

Single-reviewer code reviews miss important issues because one person (or AI persona) can't be an expert in everything. Security experts miss performance issues. Performance experts miss UX problems. Architecture experts miss accessibility concerns.

### Why It Was Hard

- Traditional code review is one-dimensional
- Reviewers naturally focus on their strengths
- Critical issues slip through when expertise is narrow
- No systematic way to ensure comprehensive coverage
- AI reviews tend to be generic without specialized focus

### Impact

- Security vulnerabilities reach production
- Performance issues discovered too late
- Technical debt accumulates unnoticed
- Poor user/developer experience
- Costly post-deployment fixes

---

## The Solution

Use **14 specialized reviewer personas** in parallel, each examining code from their unique expertise. This ensures comprehensive coverage across all quality dimensions.

### Root Cause of Traditional Review Gaps

Reviews fail when they rely on a single generalist perspective. The solution is **deliberate specialization** - force the reviewer to adopt specific expert mindsets.

### The 14 Reviewer Personas

#### Security Reviewers (4 personas)

| Persona | Focus Area | What They Catch |
|---------|------------|-----------------|
| **Security Hawk** | OWASP Top 10, injection, auth flaws | Critical vulnerabilities |
| **Data Guardian** | PII exposure, encryption, privacy | Data leaks, compliance issues |
| **API Sentinel** | Auth tokens, rate limits, CORS | API abuse vectors |
| **Crypto Auditor** | Encryption strength, key handling | Weak crypto, key exposure |

#### Quality Reviewers (4 personas)

| Persona | Focus Area | What They Catch |
|---------|------------|-----------------|
| **Performance Eagle** | N+1 queries, memory, bottlenecks | Performance issues |
| **Test Skeptic** | Coverage gaps, test quality | Untested edge cases |
| **Error Hunter** | Error handling, edge cases | Unhandled failures |
| **Type Guardian** | Type safety, any usage | Runtime type errors |

#### Architecture Reviewers (3 personas)

| Persona | Focus Area | What They Catch |
|---------|------------|-----------------|
| **Pattern Police** | SOLID, DRY, design patterns | Anti-patterns |
| **Coupling Detective** | Dependencies, modularity | Tight coupling |
| **Scalability Scout** | Growth patterns, limits | Scaling blockers |

#### UX/DX Reviewers (3 personas)

| Persona | Focus Area | What They Catch |
|---------|------------|-----------------|
| **UX Advocate** | User flows, accessibility | Poor user experience |
| **DX Champion** | API ergonomics, docs | Developer friction |
| **Maintenance Oracle** | Long-term maintainability | Technical debt |

---

## Implementation

### Step 1: Spawn Parallel Reviewers

Each persona reviews the same code independently:

```markdown
<persona>
You are the Security Hawk.

Your expertise: OWASP Top 10, injection attacks, authentication flaws
Your mission: Find security vulnerabilities others miss.

Review standards:
- Only report findings with >80% confidence
- Provide specific file:line references
- Explain WHY this is a security problem
- Suggest a fix when possible
- Rate severity: CRITICAL | HIGH | MEDIUM | LOW
</persona>

<code_to_review>
{FILE_CONTENTS}
</code_to_review>
```

### Step 2: Collect Findings

Each persona returns structured findings:

```markdown
### Security Hawk Findings

| Severity | Location | Issue | Recommendation |
|----------|----------|-------|----------------|
| CRITICAL | auth.ts:45 | SQL injection via string interpolation | Use parameterized queries |
| HIGH | api/login.ts:12 | No rate limiting | Add rate limit middleware |
| MEDIUM | config.ts:8 | Weak JWT secret (256-bit) | Use 512-bit minimum |
```

### Step 3: De-duplicate and Consolidate

When multiple personas flag the same issue, consolidate:

```markdown
### Consolidated Finding #1
- **Issue:** SQL injection vulnerability
- **Flagged by:** Security Hawk, API Sentinel (2 personas)
- **Location:** auth.ts:45
- **Severity:** CRITICAL (consensus)
- **Description:** Query uses string interpolation
- **Fix:** Use parameterized query or ORM
```

### Step 4: Priority Scoring

Calculate priority based on severity and persona count:

```
PRIORITY = SEVERITY_WEIGHT × PERSONA_COUNT

SEVERITY_WEIGHT:
  CRITICAL = 4
  HIGH = 3
  MEDIUM = 2
  LOW = 1

Example:
- CRITICAL found by 2 personas = 4 × 2 = 8 (highest priority)
- MEDIUM found by 3 personas = 2 × 3 = 6
- HIGH found by 1 persona = 3 × 1 = 3
```

### Step 5: Generate Report

```markdown
# Multi-Perspective Code Review

**Target:** src/auth/
**Personas Used:** 14
**Date:** 2025-01-23

## Executive Summary

| Severity | Count | Action |
|----------|-------|--------|
| CRITICAL | 2 | Immediate fix |
| HIGH | 5 | Fix before merge |
| MEDIUM | 8 | Address soon |
| LOW | 12 | Optional |

**Verdict:** BLOCK (CRITICAL findings present)

## Critical Findings

### #1: SQL Injection (Priority: 8)
[Details...]

### #2: Hardcoded Credentials (Priority: 4)
[Details...]

## Actionable Summary

### Must Fix Before Merge
1. [ ] SQL injection in auth.ts:45
2. [ ] Hardcoded API key in config.ts:12
```

---

## Code Example: Persona Prompt Template

```javascript
const PERSONAS = {
  securityHawk: {
    name: 'Security Hawk',
    expertise: 'OWASP Top 10, injection attacks, authentication flaws',
    mission: 'Find security vulnerabilities others miss',
    focusAreas: [
      'SQL/NoSQL injection',
      'XSS vulnerabilities',
      'Authentication bypass',
      'Authorization flaws',
      'CSRF protection'
    ]
  },
  performanceEagle: {
    name: 'Performance Eagle',
    expertise: 'N+1 queries, memory leaks, algorithmic complexity',
    mission: 'Identify performance bottlenecks and optimization opportunities',
    focusAreas: [
      'Database query efficiency',
      'Memory usage patterns',
      'Algorithmic complexity',
      'Caching opportunities',
      'Bundle size impact'
    ]
  },
  // ... other personas
};

function generatePersonaPrompt(persona, code) {
  return `
You are the ${persona.name}.

Your expertise: ${persona.expertise}
Your mission: ${persona.mission}

Focus Areas:
${persona.focusAreas.map(f => `- ${f}`).join('\n')}

Review Standards:
- Only report findings with >80% confidence
- Provide specific file:line references
- Explain WHY this is a problem
- Suggest a fix when possible
- Rate severity: CRITICAL | HIGH | MEDIUM | LOW

<code_to_review>
${code}
</code_to_review>

Return your findings in this format:
| Severity | Location | Issue | Recommendation |
`;
}
```

---

## Testing the Pattern

### Before (Single Reviewer)
```
Issues Found: 3
- 1 formatting issue
- 1 missing comment
- 1 typo in variable name

Time: 2 minutes
Critical Issues Missed: 2 (SQL injection, hardcoded key)
```

### After (14 Personas)
```
Issues Found: 27
- 2 CRITICAL security issues
- 5 HIGH priority issues
- 8 MEDIUM priority issues
- 12 LOW/suggestions

Time: 5 minutes (parallel execution)
Critical Issues Caught: 2/2 (100%)
```

---

## Prevention

### When to Use Multi-Perspective Review

- **Always:** Before merging to main/production
- **Always:** For security-sensitive code
- **Always:** For new features affecting users
- **Optional:** For minor internal changes

### Review Depth Configurations

| Depth | Personas | Use Case |
|-------|----------|----------|
| Quick | 4 (Security Hawk, Performance Eagle, Test Skeptic, Pattern Police) | Hotfixes |
| Normal | 14 (all) | Standard PRs |
| Deep | 14 + cross-file analysis | Major features |

---

## Related Patterns

- [STRIDE Threat Modeling](../deployment-security/STRIDE_THREAT_MODELING.md)
- [Evidence-Based Validation](./EVIDENCE_BASED_VALIDATION.md)
- [60-Point Validation Checklist](../methodology/VALIDATION_CHECKLIST.md)

---

## Common Mistakes to Avoid

- **Using too few personas** - 4 minimum, 14 for comprehensive coverage
- **Running sequentially** - Always parallel for speed
- **Ignoring low-severity findings** - They accumulate into technical debt
- **Skipping de-duplication** - Consolidated findings are more actionable
- **No priority scoring** - Without scoring, all issues seem equal

---

## Resources

- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)
- [Google Engineering Practices](https://google.github.io/eng-practices/review/)
- [compounding-engineering multi-perspective review](https://github.com/anthropics/claude-code-plugins)

---

## Time to Implement

**Initial Setup:** 30 minutes (create persona prompts)
**Per Review:** 5-10 minutes (parallel execution)
**ROI:** Catches 3-5x more issues than single-reviewer

## Difficulty Level

⭐⭐⭐ (3/5) - Moderate complexity, high value

---

**Author Notes:**
This pattern emerged from analyzing the compounding-engineering marketplace plugin. The key insight is that **specialization beats generalization** in code review. By forcing distinct expert perspectives, you eliminate blind spots that plague traditional reviews.

The 14-persona configuration was chosen to cover all major quality dimensions without excessive overlap. Fewer personas miss issues; more personas create noise without added value.

**Implementation in Dominion Flow:** Available via `/fire-7-review` command.
