# Expected CONSCIENCE.md Output

This file defines the expected structure and content of a CONSCIENCE.md file after various Dominion Flow operations. Use for validation in tests.

---

## Expected Structure

A valid CONSCIENCE.md MUST contain these sections:

```markdown
# Project State

## Current Phase
[Phase N: Phase Name (Status)]

## Session Context
[Bullet points describing current work context]

## Active Tasks
[Checkbox list of current tasks]

## Blockers
[List of blockers or "None"]

## Last Updated
[ISO timestamp]
```

---

## After /fire-1-new

```markdown
# Project State

## Current Phase
Phase 1: [First Phase Name] (Not Started)

## Session Context
- Project initialized on [DATE]
- Ready to begin Phase 1 planning
- No previous work history

## Active Tasks
- [ ] Plan Phase 1
- [ ] Review VISION.md
- [ ] Set up development environment

## Blockers
None

## Technical Notes
(Optional section - may be empty)

## Files Modified This Session
- .planning/CONSCIENCE.md (created)
- .planning/VISION.md (created)

## Last Updated
[ISO timestamp within last minute]
```

### Validation Rules
- `## Current Phase` must contain "Phase 1"
- `## Active Tasks` must have at least one task
- `## Blockers` must exist (can be "None")
- `## Last Updated` must be valid ISO timestamp

---

## After /fire-2-plan

```markdown
# Project State

## Current Phase
Phase N: [Phase Name] (Planning Complete)

## Session Context
- Phase N planning completed
- BLUEPRINT.md created at .planning/phases/[phase-dir]/[plan-file].md
- Ready for execution with /fire-3-execute

## Active Tasks
- [x] Plan Phase N
- [ ] Execute Phase N
- [ ] Verify Phase N completion

## Blockers
[Any blockers identified during planning, or "None"]

## Technical Notes
[Optional - key decisions from planning]

## Files Modified This Session
- .planning/CONSCIENCE.md (updated)
- .planning/phases/[phase-dir]/[plan-file].md (created)

## Last Updated
[ISO timestamp]
```

### Validation Rules
- `## Session Context` must mention "plan" or "BLUEPRINT.md"
- At least one task should be marked [x] (planning task)
- Plan file path should be mentioned

---

## After /fire-3-execute

```markdown
# Project State

## Current Phase
Phase N: [Phase Name] (Execution Complete | Breath M of W)

## Session Context
- Execution of Phase N [completed | in progress]
- Breath [current] of [total] [completed | in progress]
- [Summary of work done]

## Active Tasks
- [x] Plan Phase N
- [x] Execute Phase N (or [ ] if in progress)
- [ ] Verify Phase N completion

## Blockers
[Any blockers encountered, or "None"]

## Technical Notes
[Key implementations, decisions]

## Files Modified This Session
- .planning/CONSCIENCE.md (updated)
- .planning/phases/[phase-dir]/[plan-file].md (updated - checkboxes)
- [List of created/modified project files]

## Last Updated
[ISO timestamp]
```

### Validation Rules
- If execution complete, current phase should indicate completion
- Created files should be listed
- Task checkboxes should reflect actual progress

---

## After /fire-4-verify

```markdown
# Project State

## Current Phase
Phase N: [Phase Name] (Verified | Incomplete)

## Session Context
- Verification of Phase N completed
- [Result: All criteria passed | X of Y criteria passed]
- VERIFY.md created at .planning/phases/[phase-dir]/[verify-file].md

## Active Tasks
- [x] Plan Phase N
- [x] Execute Phase N
- [x] Verify Phase N completion (or [ ] if incomplete)
- [ ] Plan Phase N+1 (if Phase N complete)

## Blockers
[Any verification failures, or "None"]

## Technical Notes
[Summary of verification results]

## Files Modified This Session
- .planning/CONSCIENCE.md (updated)
- .planning/phases/[phase-dir]/[verify-file].md (created)

## Last Updated
[ISO timestamp]
```

### Validation Rules
- VERIFY.md path should be mentioned
- If verification failed, blockers should reflect issues
- Next phase task should appear if current phase passed

---

## After /fire-5-handoff

```markdown
# Project State

## Current Phase
Phase N: [Phase Name] ([Status])

## Session Context
- Session handoff created
- Handoff file: ~/.claude/warrior-handoffs/[PROJECT]_[DATE].md
- Context preserved for next session

## Active Tasks
[Remaining tasks - unchanged from before handoff]

## Blockers
[Unchanged from before handoff]

## Technical Notes
[Unchanged]

## Files Modified This Session
[Previous files plus handoff]
- ~/.claude/warrior-handoffs/[PROJECT]_[DATE].md (created)

## Last Updated
[ISO timestamp]
```

### Validation Rules
- Session context should mention "handoff"
- Handoff file path should be mentioned
- Other content should be preserved (not cleared)

---

## After /fire-6-resume

```markdown
# Project State

## Current Phase
[Restored from handoff]

## Session Context
- Session resumed from handoff
- Previous session: [DATE/TIME from handoff]
- Continuing from: [Phase/Breath from handoff]

## Active Tasks
[Restored from handoff - pending tasks]

## Blockers
[Restored from handoff]

## Technical Notes
[Restored from handoff]

## Files Modified This Session
- .planning/CONSCIENCE.md (updated - resume)

## Last Updated
[ISO timestamp - current time]
```

### Validation Rules
- Session context should mention "resume" or "restored"
- Active tasks should match handoff's pending tasks
- Last Updated should be current (not from handoff)

---

## Validation Script

```bash
#!/bin/bash
# Validate CONSCIENCE.md structure

STATE_FILE="${1:-.planning/CONSCIENCE.md}"

# Check file exists
[ -f "$STATE_FILE" ] || { echo "FAIL: CONSCIENCE.md not found"; exit 1; }

# Check required sections
SECTIONS=("## Current Phase" "## Session Context" "## Active Tasks" "## Blockers" "## Last Updated")
for section in "${SECTIONS[@]}"; do
    grep -q "$section" "$STATE_FILE" || { echo "FAIL: Missing section: $section"; exit 1; }
done

# Check timestamp format (ISO-like)
TIMESTAMP=$(grep -A1 "## Last Updated" "$STATE_FILE" | tail -1)
[[ "$TIMESTAMP" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2} ]] || { echo "FAIL: Invalid timestamp format"; exit 1; }

echo "PASS: CONSCIENCE.md structure valid"
```

---

## Notes

- Section order may vary
- Additional sections are allowed
- Content within sections may vary based on project
- Timestamps should be reasonably current
