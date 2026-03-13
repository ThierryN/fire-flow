---
name: fire-validate-skills
description: Validate skills library structural integrity — frontmatter, sections, cross-references, markdown syntax
arguments:
  - name: scope
    description: "What to validate: 'all', a category name (e.g., 'database-solutions'), or a specific skill filename"
    required: false
    type: string
triggers:
  - "validate skills"
  - "check skills"
  - "skill validation"
  - "verify skills"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
---

# /fire-validate-skills — Skills Library Structural Validator

Validate that skills in the library are well-formed, internally consistent, and have valid cross-references.

## Purpose

Run after `/fire-add-new-skill`, `/fire-research`, or any bulk skill creation to catch:
- Missing or malformed YAML frontmatter
- Missing required sections
- Broken cross-references (related skills pointing to nonexistent files)
- Unclosed code blocks or malformed tables
- Invalid field values (bad difficulty, tags as strings instead of arrays)

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `scope` | No | `all` | `all` = entire library, `{category}` = one category folder, `{filename.md}` = single file |

## Usage

```bash
/fire-validate-skills                          # Validate entire library
/fire-validate-skills database-solutions       # Validate one category
/fire-validate-skills orm-schema-portability   # Validate single skill
```

---

## Process

### Step 1: Determine Scope

```
SKILLS_ROOT = ~/.claude/plugins/dominion-flow/skills-library/

IF scope == "all" or not provided:
  target_files = glob("{SKILLS_ROOT}/**/*.md") excluding SKILLS-INDEX.md
ELIF scope matches a directory name in SKILLS_ROOT:
  target_files = glob("{SKILLS_ROOT}/**/{scope}/*.md")
ELIF scope matches a filename (with or without .md):
  target_files = find file by name across all categories
ELSE:
  Display: "Unknown scope: {scope}. Use 'all', a category name, or a skill filename."
  STOP
```

### Step 2: Validate Each Skill

For each skill file, run these checks:

#### Check 1: YAML Frontmatter (REQUIRED)

```
Required fields:
  - name: string (must match filename without .md, kebab-case)
  - category: string (must match parent directory name)
  - version: string (semver format: X.Y.Z)
  - contributed: string (YYYY-MM-DD date format)
  - contributor: string (non-empty)
  - last_updated: string (YYYY-MM-DD date format)
  - tags: array (NOT a string — must be [tag1, tag2, ...])
  - difficulty: string (must be one of: easy, medium, hard)

Scoring:
  All present and valid = PASS
  Missing any required field = FAIL
  Invalid value (e.g., difficulty: "extreme") = WARN
```

#### Check 2: Required Sections

```
Must have ALL of these H2 sections (exact heading text may vary):
  - Problem / Overview / Purpose (at least one)
  - Solution Pattern / Complete * / Per-* / How to * (at least one solution section)
  - When to Use
  - When NOT to Use
  - Related Skills (can be empty but must exist)
  - References (can be empty but must exist)

Scoring:
  All present = PASS
  Missing 1-2 = WARN (list which are missing)
  Missing 3+ = FAIL
```

#### Check 3: Cross-Reference Resolution

```
Find all markdown links in "Related Skills" section:
  Pattern: [text](path.md) or [text](../category/path.md)

For each link:
  Resolve relative to current file's directory
  Check if target file EXISTS on disk

Scoring:
  All resolve = PASS
  Any broken = FAIL (list broken references with expected path)
```

#### Check 4: Markdown Syntax

```
Check for:
  - Unclosed code blocks (odd number of ``` lines)
  - Malformed table rows (inconsistent pipe count)
  - Orphaned heading markers (# at start of line without space after)

Scoring:
  No issues = PASS
  Any issue = WARN (list line numbers)
```

#### Check 5: Content Quality (WARN only, never FAIL)

```
Check for:
  - Empty sections (heading with no content before next heading)
  - Very short skills (< 20 lines total — likely incomplete)
  - Very long skills (> 500 lines — consider splitting)
  - Missing code examples in Solution section
  - Tags array has < 2 tags (too few for searchability)

Scoring:
  All good = PASS
  Any issue = WARN (suggestion only)
```

### Step 3: Generate Report

```markdown
+---------------------------------------------------------------+
|          SKILLS LIBRARY VALIDATION REPORT                       |
+---------------------------------------------------------------+

Scope: {all | category | single file}
Files scanned: {N}
Date: {YYYY-MM-DD}

-------------------------------------------------------------
RESULTS SUMMARY
-------------------------------------------------------------

| Status | Count |
|--------|-------|
| PASS   | {N}   |
| WARN   | {N}   |
| FAIL   | {N}   |

-------------------------------------------------------------
FAILURES (must fix)
-------------------------------------------------------------

{For each FAIL:}
  File: {category}/{filename}.md
  Check: {which check failed}
  Issue: {specific problem}
  Fix: {what to do}

-------------------------------------------------------------
WARNINGS (should fix)
-------------------------------------------------------------

{For each WARN:}
  File: {category}/{filename}.md
  Check: {which check warned}
  Issue: {specific problem}
  Suggestion: {what to improve}

-------------------------------------------------------------
ALL PASSING ({N} files)
-------------------------------------------------------------

{List of files that passed all checks — collapsed if > 20}

+---------------------------------------------------------------+
|  VERDICT: {ALL PASS | {N} WARNINGS | {N} FAILURES}            |
+---------------------------------------------------------------+
```

### Step 4: Route on Verdict

| Verdict | Next Action |
|---------|------------|
| ALL PASS | Done — skills are structurally sound |
| WARNINGS only | Display suggestions, no blocking action needed |
| FAILURES | List fixes needed. Offer: "Fix these now? [Y/N]" |

If user chooses to fix:
- Auto-fix simple issues (missing `difficulty: medium` default, missing empty Related Skills section)
- Flag complex issues for manual review (broken cross-refs need human decision on correct target)

---

## Parallel Execution (for scope=all)

When validating the entire library, spawn parallel agents by category for speed:

```
Agent per category:
  - Read all .md files in that category folder
  - Run Checks 1-5 on each
  - Return results array

Orchestrator:
  - Collect results from all agents
  - Merge into single report
  - Sort failures first, then warnings, then passes
```

For small scopes (single category or file), run directly without agents.

---

## Auto-Fix Capabilities

These issues can be auto-fixed with user confirmation:

| Issue | Auto-Fix |
|-------|----------|
| Missing `difficulty` field | Add `difficulty: medium` |
| Missing empty `Related Skills` section | Add `## Related Skills\n\n- None yet\n` |
| Missing empty `References` section | Add `## References\n\n- None yet\n` |
| `tags` as string instead of array | Convert `tags: "foo, bar"` → `tags: [foo, bar]` |
| `last_updated` older than `contributed` | Set `last_updated` = `contributed` |
| Name doesn't match filename | Update `name` field to match filename |

Issues that CANNOT be auto-fixed:
- Broken cross-references (need human decision on correct target)
- Missing solution content (need domain knowledge)
- Unclosed code blocks (need to identify which block is unclosed)

---

## Success Criteria

- [ ] All files in scope are scanned
- [ ] Frontmatter validation catches missing/invalid fields
- [ ] Section validation catches missing required sections
- [ ] Cross-reference validation catches broken links
- [ ] Markdown syntax check catches unclosed blocks
- [ ] Report clearly separates FAIL from WARN
- [ ] Auto-fix offered for simple issues
- [ ] Parallel execution used for full-library scans

---

## Related Commands

- `/fire-add-new-skill` — Create new skills (run validate after)
- `/fire-research` — Bulk skill creation (run validate after)
- `/fire-search` — Search the validated library
- `/fire-test` — Full plugin test suite (includes skill structure tests)

---

*Dominion Flow v12.8 — Trust but verify. Every skill, every field, every reference.*
