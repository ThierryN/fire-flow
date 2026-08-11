---
name: CONSISTENCY_CHECK_AMBIGUITY_GATE
category: methodology
description: Re-read the full request for consistency before asking a clarifying question
version: 1.0.0
tags: [wizard, clarification, ambiguity, requirements, llm-reliability, clarify-gpt]
---

# Consistency-Check Ambiguity Gate

## Problem

A wizard detects ambiguity and immediately asks a clarifying question. But:

1. The original request already answered the question — the LLM just didn't connect
   the pieces.
2. The clarifying question is redundant with information already given.
3. The user gets asked to repeat themselves.

This is the most common failure mode in requirements-gathering wizards: asking
questions that were already answered.

**User experience:** "I already told you that." Trust erodes. User disengages.

## Solution

Before asking any clarifying question, run a **consistency check**:

```
1. Re-read the full original request (from the beginning of this interaction)
2. Check: Does any part of the existing input already resolve this ambiguity?
3. If YES → extract the answer, proceed without asking
4. If NO (confirmed gap) → ask the clarifying question
```

This is a **silent pre-check** — users never see it unless clarification is genuinely needed.

## Implementation Pattern

Add to any step that generates clarifying questions:

```markdown
**Per-step self-check before asking:**
Ask internally: "Is the answer to this question already implied or stated in what
the user has provided? Re-read from the beginning." If already answerable → resolve
internally. Only ask if genuinely ambiguous after re-reading.
```

### Example: fire-1d-discuss.md Step 3.75

```markdown
### Step 3.75: Consistency-Check Ambiguity Gate

Before asking any clarifying question during phase discussion:
1. Re-read the full original phase description from Step 1
2. Check for implicit answers: stated constraints, mentioned components,
   implied scope limits
3. If the question is answerable from context → resolve internally and proceed
4. Only surface questions that remain genuinely ambiguous after the re-read
```

## When This Fires

- Any wizard step that would generate a follow-up question
- Requirements-gathering after a long initial description
- When the user's input is dense with embedded context

## Measurable Impact

**ClarifyGPT** (arXiv 2310.10996) — Framework for when and how to ask clarifying
questions in code generation. Using consistency-check before generating clarifications:
**+9.84 percentage points improvement in GPT-4 Pass@1** on HumanEval and MBPP
benchmarks.

**Mechanism:** Most ambiguity is *apparent* ambiguity — the answer is present but
requires synthesis across multiple parts of the request. A re-read finds it.
True ambiguity (where the answer is genuinely absent) requires only a focused,
targeted question.

## Connection to Missing-Dimension Detector

These two patterns are complementary:

| Pattern | Fires when | Effect |
|---------|-----------|--------|
| Consistency-Check | About to ask a question | Eliminates redundant questions |
| Missing-Dimension Detector | After collecting answers | Adds missing critical questions |

Together: fewer questions, better coverage.

## Research Basis

> **ClarifyGPT** (arXiv 2310.10996) — Consistency-check before clarification generation.
> +9.84pp GPT-4 Pass@1 on HumanEval + MBPP.
> Applied: Step 3.75 added to fire-1d-discuss.md; per-step self-check added to
> fire-scaffold.md Step 5 in v12.3.
