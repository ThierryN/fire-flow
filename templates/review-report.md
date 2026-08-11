# Multi-Perspective Code Review

**Target:** {target}
**Date:** {timestamp}
**Depth:** shallow | normal | deep
**Personas Used:** {count}

---

## Executive Summary

| Severity | Count | Action Required |
|----------|-------|-----------------|
| CRITICAL | 0 | Immediate fix |
| HIGH | 0 | Fix before merge |
| MEDIUM | 0 | Address soon |
| LOW | 0 | Optional |

**Overall Assessment:** BLOCK | APPROVE WITH FIXES | APPROVE

---

## Critical Findings (Fix Immediately)

### Finding #1: {Title}

| Attribute | Value |
|-----------|-------|
| **Severity** | CRITICAL |
| **Location** | `{file}:{line}` |
| **Flagged By** | {persona list} |
| **Confidence** | {percentage}% |

**Problem:**
```{language}
// Code showing the issue
```

**Fix:**
```{language}
// Code showing the solution
```

**Why This Matters:**
{Explanation of impact}

---

## High Priority Findings

### Finding #{N}: {Title}

| Attribute | Value |
|-----------|-------|
| **Severity** | HIGH |
| **Location** | `{file}:{line}` |
| **Flagged By** | {persona list} |

**Problem:** {description}

**Fix:** {recommendation}

---

## Medium Priority Findings

| # | Location | Issue | Flagged By |
|---|----------|-------|------------|
| 1 | `{file}:{line}` | {issue} | {persona} |

---

## Low Priority / Suggestions

- {suggestion 1}
- {suggestion 2}

---

## Persona Breakdown

### Security Review ({count} personas)
- **Issues Found:** {count}
- **Unique Insights:** {insights}

### Quality Review ({count} personas)
- **Issues Found:** {count}
- **Unique Insights:** {insights}

### Architecture Review ({count} personas)
- **Issues Found:** {count}
- **Unique Insights:** {insights}

### UX/DX Review ({count} personas)
- **Issues Found:** {count}
- **Unique Insights:** {insights}

---

## Actionable Summary

### Must Fix Before Merge
1. [ ] {item}
2. [ ] {item}

### Should Fix Soon
1. [ ] {item}
2. [ ] {item}

### Consider Later
1. [ ] {item}
2. [ ] {item}

---

*Review completed: {timestamp}*
*Powered by: Dominion Flow Multi-Perspective Review*
