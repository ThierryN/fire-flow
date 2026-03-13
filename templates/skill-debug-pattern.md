---
name: {{SKILL_NAME}}
category: {{CATEGORY}}
type: debug-pattern
version: 1.0.0
contributed: {{DATE}}
contributor: {{PROJECT}}
last_updated: {{DATE}}
tags: [{{TAGS}}]
difficulty: {{DIFFICULTY}}
usage_count: 0
success_rate: 100
---

# {{TITLE}}

## Problem

**Symptoms:**
- [What the developer sees / error message]
- [Observable behavior that indicates the bug]

**Root Cause:**
[The actual underlying issue, not just symptoms]

**Why It's Tricky:**
[What makes this hard to debug — misleading errors, race conditions, etc.]

## Detection

How to confirm you're hitting this exact bug:

```{{LANGUAGE}}
// Diagnostic check — run this to confirm
{{DIAGNOSTIC_CODE}}
```

Expected output when bug is present:
```
{{EXPECTED_BAD_OUTPUT}}
```

## Solution Pattern

### Before (Broken)

```{{LANGUAGE}}
{{BEFORE_CODE}}
```

### After (Fixed)

```{{LANGUAGE}}
{{AFTER_CODE}}
```

### Why This Works

[Explain the mechanism — not just "this fixes it" but WHY]

## Elimination Checklist

Before applying this fix, rule out these other causes:

- [ ] [Alternative cause 1 — how to check]
- [ ] [Alternative cause 2 — how to check]
- [ ] [Alternative cause 3 — how to check]

## Verification

After applying the fix, verify with:

```{{LANGUAGE}}
{{VERIFICATION_CODE}}
```

Expected output:
```
{{EXPECTED_GOOD_OUTPUT}}
```

## When to Use

- [Scenario 1]
- [Scenario 2]

## When NOT to Use

- [Anti-pattern 1]
- [Anti-pattern 2]

## Related Skills

- [related-skill] - [description]

## References

- Contributed from: {{PROJECT}}
