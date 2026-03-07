---
description: Archive completed milestone and prepare for next version with WARRIOR validation
---

# /fire-complete-milestone

> Archive milestone, create historical record, and prepare for next cycle with WARRIOR validation

---

## Purpose

Mark milestone complete, archive to milestones/, and update VISION.md and REQUIREMENTS.md. Creates a historical record of what shipped and prepares the project for the next milestone.

**Creates:**
- `.planning/milestones/v{version}-VISION.md` - Archived roadmap
- `.planning/milestones/v{version}-REQUIREMENTS.md` - Archived requirements
- Git tag `v{version}`

---

## Arguments

```yaml
arguments:
  version:
    required: true
    type: string
    description: "Version number to complete (e.g., '1.0', '1.1', '2.0')"
    example: "/fire-complete-milestone 1.0"
```

---

## Process

### Step 0: Pre-flight Check - WARRIOR Validation

**MANDATORY: Check for verification before archiving.**

```bash
ls .planning/v{version}-VERIFICATION.md 2>/dev/null
```

**If no verification file:**
```
+------------------------------------------------------------------------------+
| WARNING: No Verification Found                                                |
+------------------------------------------------------------------------------+
|                                                                              |
|  No verification record found for v{version}.                                |
|                                                                              |
|  Recommended: Run `/fire-4-verify` first to ensure:                         |
|    - All must-haves are met                                                  |
|    - 70-point validation passed                                              |
|    - No critical gaps                                                        |
|                                                                              |
|  Continue anyway? (verification will be noted as "skipped")                  |
|                                                                              |
+------------------------------------------------------------------------------+
```

Use AskUserQuestion:
- header: "Verification"
- question: "No verification found. How do you want to proceed?"
- options:
  - "Run verification first (Recommended)" - Route to /fire-4-verify
  - "Continue without verification" - Proceed with warning noted

### Step 1: Verify Readiness

Check all phases in milestone have completed plans (RECORD.md exists):

```bash
for phase_dir in .planning/phases/*/; do
  [ -f "${phase_dir}RECORD.md" ] && echo "COMPLETE: $phase_dir" || echo "MISSING: $phase_dir"
done
```

Present milestone scope and stats. Wait for confirmation.

### Step 2: Gather Stats

- Count phases, plans, tasks completed
- Calculate git range, file changes, LOC
- Extract timeline from git log

```bash
# Git stats
git log --oneline --since="[milestone start]" | wc -l
git diff --stat $(git log --format="%H" --since="[milestone start]" | tail -1)..HEAD
```

Present summary, confirm.

### Step 3: Extract Accomplishments

Read all phase RECORD.md files in milestone range. Extract 4-6 key accomplishments.

```
+------------------------------------------------------------------------------+
| v{version} ACCOMPLISHMENTS                                                   |
+------------------------------------------------------------------------------+
|                                                                              |
|  Key accomplishments:                                                        |
|    1. {accomplishment from RECORD.md}                                       |
|    2. {accomplishment from RECORD.md}                                       |
|    3. {accomplishment from RECORD.md}                                       |
|    4. {accomplishment from RECORD.md}                                       |
|                                                                              |
|  Stats:                                                                      |
|    - Phases: {count}                                                         |
|    - Plans executed: {count}                                                 |
|    - Requirements fulfilled: {count}/{total}                                 |
|    - Files changed: {count}                                                  |
|                                                                              |
+------------------------------------------------------------------------------+
```

Present for approval.

### Step 4: Archive Milestone

Create `.planning/milestones/v{version}-VISION.md`:
- Extract full phase details from VISION.md
- Include completion timestamps
- Add accomplishment summary

Update VISION.md to one-line summary with link:

```markdown
## Archived Milestones

- [v{version}](milestones/v{version}-VISION.md) - {one-line summary} (shipped {date})
```

### Step 5: Archive Requirements

Create `.planning/milestones/v{version}-REQUIREMENTS.md`:
- Mark all v1 requirements as complete (checkboxes checked)
- Note requirement outcomes (validated, adjusted, dropped)

Delete `.planning/REQUIREMENTS.md` (fresh one created for next milestone).

### Step 6: Update PROJECT.md

Add "Current State" section with shipped version:

```markdown
## Current State

**Latest Release:** v{version} - {name}
**Shipped:** {date}

Key accomplishments:
- {accomplishment 1}
- {accomplishment 2}

## Next Milestone Goals
<!-- Defined by /fire-1a-new or /fire-new-milestone -->
```

### Step 7: Commit and Tag

Stage all changes:

```bash
git add .planning/milestones/ .planning/PROJECT.md .planning/VISION.md .planning/CONSCIENCE.md
git commit -m "$(cat <<'EOF'
chore: archive v{version} milestone

Key accomplishments:
- {accomplishment 1}
- {accomplishment 2}
- {accomplishment 3}

Phases: {count} | Requirements: {count}
EOF
)"
```

Create annotated tag:

```bash
git tag -a v{version} -m "[milestone summary]"
```

Use AskUserQuestion:
- header: "Push Tag"
- question: "Push tag v{version} to remote?"
- options:
  - "Yes, push tag" - git push origin v{version}
  - "No, keep local" - Done

### Step 8: Sabbath Rest - Context Persistence

Update persistent state:

```markdown
## .claude/fire-flow.local.md

### Milestone Completion
- Version: v{version}
- Completed: {timestamp}
- Accomplishments: {count}
- Next: Run /fire-new-milestone to start next cycle
```

---

## Completion Display

```
+------------------------------------------------------------------------------+
| MILESTONE v{version} ARCHIVED                                                |
+------------------------------------------------------------------------------+
|                                                                              |
|  Archived Files:                                                             |
|    - .planning/milestones/v{version}-VISION.md                              |
|    - .planning/milestones/v{version}-REQUIREMENTS.md                         |
|                                                                              |
|  Git Tag: v{version}                                                         |
|  Commit: {hash}                                                              |
|                                                                              |
+------------------------------------------------------------------------------+
| NEXT UP                                                                      |
+------------------------------------------------------------------------------+
|                                                                              |
|  -> Run `/fire-new-milestone` to start the next milestone cycle             |
|     (questioning -> research -> requirements -> roadmap)                     |
|                                                                              |
|  -> Or run `/fire-5-handoff` to create a session handoff first              |
|                                                                              |
+------------------------------------------------------------------------------+
```

---

## Success Criteria

- [ ] Verification status checked (WARRIOR validation)
- [ ] All phases have RECORD.md files
- [ ] Milestone archived to `.planning/milestones/v{version}-VISION.md`
- [ ] Requirements archived to `.planning/milestones/v{version}-REQUIREMENTS.md`
- [ ] `.planning/REQUIREMENTS.md` deleted (fresh for next milestone)
- [ ] VISION.md collapsed to one-line entry
- [ ] PROJECT.md updated with current state
- [ ] Git tag v{version} created
- [ ] Commit successful
- [ ] Sabbath Rest state updated
- [ ] User knows next steps

---

## Critical Rules

- **Verify before archiving:** Check for /fire-4-verify results
- **Archive before deleting:** Always create archive files before updating/deleting originals
- **One-line summary:** Collapsed milestone in VISION.md should be single line with link
- **Context efficiency:** Archive keeps VISION.md and REQUIREMENTS.md constant size per milestone
- **Fresh requirements:** Next milestone starts with `/fire-new-milestone` which includes requirements definition

---

## References

- **Related:** `/fire-new-milestone` - Start next milestone cycle
- **Related:** `/fire-4-verify` - Verify phase/milestone completion
- **Template:** `@templates/milestone-archive.md`
- **Brand:** `@references/ui-brand.md`
