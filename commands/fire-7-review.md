---
description: Multi-perspective code review with 15 specialized reviewer personas
---

# /fire-7-review

> Comprehensive code review through multiple expert lenses

---

## Purpose

Perform deep code review using 16 specialized reviewer personas (14 original + Simplicity Guardian + Qt Thread Guardian), each examining the code from their unique perspective. Inspired by compounding-engineering's multi-perspective approach, this catches issues that single-reviewer passes miss. In v8.0, also available in automatic mode via the `fire-reviewer` agent.

---

## Arguments

```yaml
arguments:
  target:
    required: true
    type: string
    description: "What to review - can be a file, directory, PR number, or 'phase N'"
    examples:
      - "/fire-7-review src/auth/"
      - "/fire-7-review PR#123"
      - "/fire-7-review phase 2"

optional_flags:
  --perspectives: "Comma-separated list of specific personas to use (default: all)"
  --depth: "shallow | normal | deep (default: normal)"
  --focus: "Security focus area: auth, data, api, all (default: all)"
  --parallel: "Run persona reviews in parallel (default: true)"
  --output: "Report output path (default: .planning/reviews/)"
```

---

## The 14 Reviewer Personas

### Security Reviewers (4)

| Persona | Focus | Catches |
|---------|-------|---------|
| **Security Hawk** | OWASP Top 10, injection, auth flaws | Critical vulnerabilities |
| **Data Guardian** | PII exposure, encryption, privacy | Data leaks, compliance |
| **API Sentinel** | Auth tokens, rate limits, CORS | API abuse vectors |
| **Crypto Auditor** | Encryption strength, key handling | Weak crypto, key exposure |

### Quality Reviewers (5)

| Persona | Focus | Catches |
|---------|-------|---------|
| **Simplicity Guardian** | Over-engineering, unnecessary abstraction, premature optimization | Code that's complex when it could be simple |
| **Performance Eagle** | N+1 queries, memory, bottlenecks | Performance issues |
| **Test Skeptic** | Coverage gaps, test quality | Untested edge cases |
| **Error Hunter** | Error handling, edge cases | Unhandled failures |
| **Type Guardian** | Type safety, any usage | Runtime type errors |

### Architecture Reviewers (4)

| Persona | Focus | Catches |
|---------|-------|---------|
| **Pattern Police** | SOLID, DRY, design patterns | Anti-patterns |
| **Coupling Detective** | Dependencies, modularity | Tight coupling |
| **Scalability Scout** | Growth patterns, limits | Scaling blockers |
| **Qt Thread Guardian** | Qt thread affinity, signal/slot marshaling, worker threads | Cross-thread widget creation, race conditions in Qt event loop |

### UX/DX Reviewers (3)

| Persona | Focus | Catches |
|---------|-------|---------|
| **UX Advocate** | User flows, accessibility | Poor user experience |
| **DX Champion** | API ergonomics, docs | Developer friction |
| **Maintenance Oracle** | Long-term maintainability | Technical debt |

---

## Process

### Step 1: Load Review Context

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    DOMINION FLOW ► MULTI-PERSPECTIVE REVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Parse Target:**
```bash
# File/directory review
TARGET_TYPE="files"
FILES=$(glob "{target}")

# PR review
TARGET_TYPE="pr"
PR_DIFF=$(gh pr diff {number})

# Phase review
TARGET_TYPE="phase"
FILES=$(glob ".planning/phases/{N}-*/**/*.ts")
```

### Step 2: Spawn Parallel Reviewer Agents

```
◆ Spawning 15 reviewer agents in parallel...
  ├─ Security Hawk     ├─ Pattern Police      ├─ UX Advocate
  ├─ Data Guardian     ├─ Coupling Detective  ├─ DX Champion
  ├─ API Sentinel      ├─ Scalability Scout   ├─ Maintenance Oracle
  ├─ Crypto Auditor    ├─ Qt Thread Guardian
  ├─ Performance Eagle ├─ Test Skeptic
  ├─ Error Hunter      └─ Type Guardian
```

**Each Agent Context:**
```markdown
<persona>
You are the {PERSONA_NAME}.

Your expertise: {FOCUS_AREA}
Your mission: Find issues that others miss in your domain.

Review standards:
- Only report findings you are confident about (>80% confidence)
- Provide specific file:line references
- Explain WHY this is a problem
- Suggest a fix when possible
- Rate severity: CRITICAL | HIGH | MEDIUM | LOW
</persona>

<code_to_review>
{FILE_CONTENTS or DIFF}
</code_to_review>
```

### Step 3: Aggregate Findings

**Collect from all personas:**
```markdown
## Raw Findings

### Security Hawk
- [CRITICAL] SQL injection in auth.ts:45 - using string interpolation
- [HIGH] Missing rate limit on /api/login endpoint

### Data Guardian
- [MEDIUM] PII logged in error handler at logger.ts:23

### Performance Eagle
- [HIGH] N+1 query in getUserOrders (users.ts:89)

... (all 16 personas)
```

### Step 4: De-duplicate and Prioritize

**Remove duplicates:**
When multiple personas flag the same issue, consolidate:
```markdown
### Consolidated Finding #1
- **Issue:** SQL injection vulnerability
- **Flagged by:** Security Hawk, API Sentinel (2 personas)
- **Location:** auth.ts:45
- **Severity:** CRITICAL (consensus)
- **Description:** {merged description}
- **Fix:** {recommended fix}
```

**Priority Scoring:**
```
PRIORITY = SEVERITY_WEIGHT * PERSONA_COUNT

SEVERITY_WEIGHT:
  CRITICAL = 4
  HIGH = 3
  MEDIUM = 2
  LOW = 1
```

### Step 5: Generate Review Report

**Create:** `.planning/reviews/{target}-review-{timestamp}.md`

```markdown
# Multi-Perspective Code Review

**Target:** {target}
**Date:** {timestamp}
**Depth:** {depth}
**Personas Used:** 16

---

## Executive Summary

| Severity | Count | Action Required |
|----------|-------|-----------------|
| CRITICAL | 2 | Immediate fix |
| HIGH | 5 | Fix before merge |
| MEDIUM | 8 | Address soon |
| LOW | 12 | Optional |

**Overall Assessment:** BLOCK | APPROVE WITH FIXES | APPROVE

---

## Critical Findings (Fix Immediately)

### Finding #1: SQL Injection in Auth Module

| Attribute | Value |
|-----------|-------|
| **Severity** | CRITICAL |
| **Location** | `src/auth/login.ts:45` |
| **Flagged By** | Security Hawk, API Sentinel |
| **Confidence** | 95% |

**Problem:**
```typescript
// VULNERABLE
const query = `SELECT * FROM users WHERE email = '${email}'`;
```

**Fix:**
```typescript
// SAFE
const query = 'SELECT * FROM users WHERE email = $1';
const result = await db.query(query, [email]);
```

**Why This Matters:**
Allows attackers to bypass authentication, exfiltrate data, or destroy the database.

---

### Finding #2: ...

---

## High Priority Findings

[Similar format]

---

## Medium Priority Findings

[Similar format]

---

## Low Priority / Suggestions

[Brief list]

---

## Persona Breakdown

### Security Review (4 personas)
- **Issues Found:** 7
- **Unique Insights:** Rate limit bypass, JWT weak secret

### Quality Review (4 personas)
- **Issues Found:** 12
- **Unique Insights:** Missing error boundaries, uncovered code paths

### Architecture Review (3 personas)
- **Issues Found:** 5
- **Unique Insights:** Circular dependency in services/

### UX/DX Review (3 personas)
- **Issues Found:** 3
- **Unique Insights:** Confusing API response format

---

## Actionable Summary

### Must Fix Before Merge
1. [ ] SQL injection in auth.ts:45
2. [ ] N+1 query in users.ts:89
3. [ ] Missing rate limit on /api/login

### Should Fix Soon
1. [ ] Add error boundaries to React components
2. [ ] Improve test coverage on auth module (currently 45%)

### Consider Later
1. [ ] Refactor services/ to reduce coupling
2. [ ] Add API response type documentation

---

*Review completed: {timestamp}*
*Powered by: Dominion Flow Multi-Perspective Review*
```

### Step 6: Update CONSCIENCE.md (if phase review)

```markdown
## Code Review Status
- Phase {N} reviewed: {timestamp}
- Findings: {critical}/{high}/{medium}/{low}
- Action: {BLOCK | APPROVE WITH FIXES | APPROVE}
```

---

## Persona Depth Configurations

### Shallow (Quick Pass)
- 4 personas: Security Hawk, Performance Eagle, Test Skeptic, Pattern Police
- Focus: Critical issues only
- Time: Fast

### Normal (Default)
- 16 personas: All
- Focus: All severities
- Time: Moderate

### Deep (Thorough)
- 16 personas: All
- Focus: All severities + suggestions + style
- Additional: Cross-file analysis, dependency review
- Time: Comprehensive

---

## Integration with Dominion Flow

### After Execution
```bash
/fire-3-execute 2
# ... execution completes ...
/fire-7-review phase 2
# ... before verification
/fire-4-verify 2
```

### PR Workflow
```bash
/fire-7-review PR#123 --focus security
# Review before merge
```

### Continuous Review
```bash
/fire-7-review src/auth/ --depth deep --perspectives "Security Hawk,API Sentinel,Crypto Auditor"
```

---

## Automatic Mode (v8.0)

When spawned as `fire-reviewer` agent (not manual `/fire-7-review`):

| Aspect | Manual | Automatic |
|--------|--------|-----------|
| Trigger | User runs `/fire-7-review` | Spawned by orchestrator (`fire-3-execute`, `fire-4-verify`, `fire-loop`) |
| Default | OFF (user opt-in) | ON (`--skip-review` to disable) |
| Gate | Informational | BLOCKS human testing |
| Simplicity | Optional persona | MANDATORY persona (always first) |
| Depth | User chooses `--depth` | Mapped from difficulty classification (Step 7.6) |
| Threshold | BLOCK on CRITICAL only | BLOCK on CRITICAL OR 3+ HIGH |
| Output | `.planning/reviews/` | `.planning/phases/{N}-{name}/{N}-REVIEW.md` |

**Automatic mode is stricter** because it gates human testing. Manual mode is informational — the user decides what to act on. Automatic mode enforces: both verifier AND reviewer must independently approve.

### Simplicity Guardian Checklist (v8.0)

The Simplicity Guardian asks on every review:

1. Could this be done with FEWER lines? (not golf — clarity)
2. Are there abstractions that serve only ONE caller?
3. Are there helper/utility functions for one-time operations?
4. Is there error handling for scenarios that can't happen?
5. Are there config/feature flags for non-configurable things?
6. Is there backwards-compatibility code for things nothing depends on?
7. Could a junior dev understand this in 30 seconds?
8. Are comments explaining WHAT instead of WHY? (sign of unclear code)

**Severity:** HIGH for unnecessary abstractions, premature optimization. MEDIUM for verbose-but-functional code.

---

## Success Criteria

### Required Outputs
- [ ] All specified personas executed review
- [ ] Findings aggregated and de-duplicated
- [ ] Review report generated with actionable items
- [ ] CONSCIENCE.md updated (for phase reviews)
- [ ] Clear BLOCK/APPROVE recommendation

### Quality Gates
- **BLOCK:** Any CRITICAL finding
- **APPROVE WITH FIXES:** HIGH findings present, no CRITICAL
- **APPROVE:** Only MEDIUM/LOW findings

---

## References

- **Inspiration:** compounding-engineering multi-perspective review
- **Template:** `@templates/review-report.md`
- **Brand:** `@references/ui-brand.md`
