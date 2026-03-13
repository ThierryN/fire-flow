---
name: REVIEW_BACKTRACK_PANEL
category: methodology
description: Show all collected answers before any writes; let the user edit any answer before committing
version: 1.0.0
tags: [wizard, review-panel, undo, multi-step, commit-before-verify, devin-pattern]
---

# Review & Backtrack Panel

## Problem

A multi-step wizard collects 5-7 answers across steps, then immediately generates output.
The user realizes in step 4 that their step 2 answer was wrong. By the time they see
the generated output, reverting requires deleting files, undoing barrel exports, and
re-running from scratch.

**Commit-before-verify anti-pattern:** Acting on collected input before giving the
user a chance to review all answers together.

## Solution

Add a Review Panel step **before any file writes or irreversible actions**. The panel:

1. Displays all collected answers in one view
2. Shows `[Edit]` next to each answer
3. Requires explicit confirmation before proceeding
4. If user edits → return to that step, collect new answer, re-display panel

```markdown
### Step N.5: Review All Answers

REVIEW PANEL
══════════════════════════════════════════════════════════
  {Step 1 label}:    {answer}    [Edit]
  {Step 2 label}:    {answer}    [Edit]
  {Step 3 label}:    {answer}    [Edit]
  {Step 4 label}:    {answer}    [Edit]
══════════════════════════════════════════════════════════

[✓ Proceed]   [Edit a section]   [Cancel]
```

## Rules

1. **Always before writes** — The panel must appear before ANY file is created,
   modified, or any external action taken. Not after.
2. **Edit returns to that step** — Editing step 2 goes back to step 2, collects
   a new answer, then re-displays the full panel. Does not restart from step 1.
3. **Show ALL answers** — Even the ones the user didn't explicitly confirm. If it
   was collected as input, it appears in the panel.
4. **Not a confirmation dialog** — This is a structured summary, not "Are you sure Y/N?"
   The structure lets users catch errors they didn't know they made.

## Implementation Examples

### fire-add-new-skill.md Step 5.5

```markdown
### Step 5.5: Review & Edit All Answers

Before running security scan or saving the skill, display collected answers:

SKILL REVIEW PANEL
══════════════════════════════════════════════════════════
  Problem:      {summary of step 1 answer}    [Edit]
  Category:     {selection}                   [Edit]
  Scope:        {general/project}             [Edit]
  Name:         {skill name}                  [Edit]
  Solution:     {summary of pattern}          [Edit]
  Code:         {yes/no}                      [Edit]
══════════════════════════════════════════════════════════
[✓ Run security scan + save]  [Edit a section]  [Cancel]
```

### fire-scaffold.md Step 5.5

```markdown
STEP 5.5 of 6 — Preview

FILES TO CREATE:
  {output-path}/{Name}.{ext}           ← main file
  {output-path}/{Name}.test.{ext}      ← test file

SKELETON PREVIEW:
  {First 20 lines of generated content}

[✓ Generate these files]  [Edit a previous answer]  [Cancel]
```

### fire-setup.md Step 7 (Review & Save)

```markdown
DEVELOPER PROFILE REVIEW
══════════════════════════════════════════════════════════
  Frontend:     {selection}    [Edit]
  Backend:      {selection}    [Edit]
  Database:     {selection}    [Edit]
  ...
══════════════════════════════════════════════════════════
[✓ Save profile]   [Edit a section]   [Cancel]
```

## When to Skip

**Do NOT add a review panel for:**
- Commands with only 1-2 inputs (trivial to re-run)
- Commands where all steps are reversible (can undo any step freely)
- Read-only commands (nothing is written)

**DO add a review panel for:**
- Wizards with 4+ collection steps
- Any wizard that writes files
- Any wizard that modifies existing files (barrel exports, route registrations)
- Onboarding wizards that write profile/config files

## Measurable Impact

**Devin Interactive Planning** (score 89/100 in wizard creation research): Showing
what will be created BEFORE consuming resources. The preview/review step maps directly
to Devin's plan approval gate — users approve the plan, then execution happens.

**"No Hardware, No Problem"** (ACM C&C 2025): Pre-generation simulation dramatically
improves user confidence and reduces post-generation correction rate.

**UX principle:** Decisions made in a sequential wizard feel isolated. Seeing all
decisions together in one panel reveals inconsistencies the user couldn't detect
across 6 separate steps.

## Research Basis

> **Devin Interactive Planning** (score 89/100) — Show what will be created BEFORE
> consuming resources. Plan approval gate prevents costly generation errors.
>
> **"No Hardware, No Problem"** (ACM C&C 2025) — Pre-generation simulation improves
> confidence and reduces post-generation correction rate.
>
> Applied: Step 5.5 (Review & Edit All Answers) added to fire-add-new-skill.md;
> Step 5.5 (Preview Before Generating) added to fire-scaffold.md;
> Step 7 (Review & Save) in fire-setup.md in v12.3.
