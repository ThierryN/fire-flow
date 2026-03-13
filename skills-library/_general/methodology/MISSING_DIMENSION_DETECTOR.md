---
name: MISSING_DIMENSION_DETECTOR
category: methodology
description: Proactively ask what dimension hasn't been covered before advancing wizard steps
version: 1.0.0
tags: [wizard, proactive-questioning, requirements, information-gathering, llm-reliability]
---

# Missing-Dimension Detector

## Problem

Wizards collect only what they're told to ask. A user building a React component answers
all 4 questions but never mentions authentication. The wizard generates unauthenticated
code. The user didn't know to mention it; the wizard didn't know to ask.

**Result:** Scaffolded or planned output is missing a critical dimension the user
assumed was covered.

## Solution

Before advancing from an information-collection step, the LLM asks itself one internal
question and acts on the answer:

```
Ask internally: "What dimension is commonly required for a {type} of this kind
that hasn't been mentioned yet?"

If a critical missing dimension is detected → ask ONE follow-up question.
If nothing critical is missing → advance to next step.
```

This is a **silent gate** — it runs between every collection step and the next.
The user only sees it if something is actually missing.

## Implementation Pattern

Add this block at the end of each information-collection step in wizard commands:

```markdown
**Missing-dimension check (proactive):**
Ask internally: "What dependency is commonly required for a {type} of this kind
that hasn't been mentioned?" If any critical dependency is missing, ask ONE follow-up.
```

### Example: fire-scaffold Step 4 (Dependencies)

```markdown
**Missing-dimension check (proactive):**
Ask internally: "What dependency is commonly required for a {type} of this kind
that hasn't been mentioned?" If any critical dependency is missing, ask ONE follow-up.
```

### Example: fire-1d-discuss Step 5 (Discuss Phase)

```markdown
**Step Confirmation Checkpoint:**
After completing all questions for an area, check:
- "Is anything missing from what the user described?"
- "Is any dependency or constraint not yet captured?"
If yes → ONE follow-up before advancing.
```

## Rules

1. **Ask internally first** — Do not ask the user if nothing is missing. Silent gate.
2. **ONE follow-up maximum** — Never chain missing-dimension checks. Ask the most
   critical missing item, get the answer, then advance.
3. **Type-specific** — The check must know the current type/context. A missing auth
   check is critical for an API endpoint; not for a CSS utility function.
4. **Dimension, not detail** — Check for entire missing *categories* (auth, rate-limiting,
   database access, error handling) not missing *details* (exact field names).

## Measurable Impact

**Teaching LMs to Gather Information Proactively** (arXiv 2507.21389, 2025):
+18% improvement over o3-mini on proactive question quality when LLMs are explicitly
instructed to identify missing information dimensions before asking users.

**Mechanism:** Without the explicit internal check, LLMs complete collection steps
based on what was asked, not what was needed. The self-check creates a second pass
that catches categorical gaps.

## Research Basis

> **Teaching LMs to Gather Information Proactively** (arXiv 2507.21389, 2025).
> +18% improvement over o3-mini on proactive question quality.
> Applied: Missing-dimension check added to wizard Step 4 (Dependencies) in
> fire-scaffold.md and Step 5 (Discuss Phase) confirmation in fire-1d-discuss.md.
