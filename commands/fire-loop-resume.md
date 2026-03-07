---
description: Resume a Power Loop from Sabbath Rest or stopped state
argument-hint: "[LOOP_ID]"
---

# /fire-loop-resume

> Resume Power Loop from Sabbath Rest snapshot with full context restoration

---

## Purpose

Resume a Power Loop that was:
- Paused due to Sabbath Rest (context rot warning)
- Stopped by user via `/fire-loop-stop`
- Interrupted by session end

This command restores context from the Sabbath Rest snapshot and continues the loop with fresh context.

---

## Arguments

```yaml
arguments:
  loop_id:
    required: false
    type: string
    description: "Loop ID to resume (omit to resume most recent)"
    example: "/fire-loop-resume 20260123-143052"
```

---

## Process

### Step 1: Find Loop to Resume

**If LOOP_ID provided:**
```bash
SABBATH_FILE=$(ls .planning/loops/sabbath-${LOOP_ID}*.md 2>/dev/null | head -1)
```

**If no LOOP_ID (resume most recent):**
```bash
# Check Sabbath Rest state first
if [ -f ".claude/fire-flow.local.md" ]; then
  LOOP_ID=$(grep "Loop ID:" .claude/fire-flow.local.md | head -1 | cut -d: -f2 | xargs)
fi

# Or find most recent sabbath file
SABBATH_FILE=$(ls -t .planning/loops/sabbath-*.md 2>/dev/null | head -1)
```

### Step 2: Validate Sabbath File Exists

```bash
if [ ! -f "$SABBATH_FILE" ]; then
  echo "No Sabbath Rest snapshot found for loop ${LOOP_ID}"
  echo "Available loops:"
  ls .planning/loops/*.md
  exit 1
fi
```

### Step 3: Load Sabbath Rest Context

Read the Sabbath snapshot and extract:

```yaml
From sabbath file:
  - loop_id
  - iteration (where we stopped)
  - original prompt
  - files modified
  - hypotheses tested
  - next steps
  - key context to restore
```

### Step 4: Display Context Restoration

```
+------------------------------------------------------------------------------+
| POWER LOOP RESUME                                                            |
+------------------------------------------------------------------------------+
|                                                                              |
|  Restoring Loop: ${LOOP_ID}                                                  |
|  Paused At: Iteration [N]                                                    |
|  Reason: [context_rot | user_stop | session_end]                             |
|                                                                              |
|  Sabbath Rest Snapshot:                                                      |
|    ${SABBATH_FILE}                                                           |
|                                                                              |
+------------------------------------------------------------------------------+
| RESTORED CONTEXT                                                             |
+------------------------------------------------------------------------------+
|                                                                              |
|  Progress Summary:                                                           |
|    [from sabbath file]                                                       |
|                                                                              |
|  Files Modified:                                                             |
|    - [file]: [change]                                                        |
|    - [file]: [change]                                                        |
|                                                                              |
|  Key Context:                                                                |
|    [critical information from sabbath file]                                  |
|                                                                              |
|  Immediate Next Step:                                                        |
|    [exactly what to do]                                                      |
|                                                                              |
+------------------------------------------------------------------------------+
```

### Step 5: Restore Loop State

Recreate active loop config:

```bash
cat > .planning/loops/active-loop.json << 'EOF'
{
  "id": "${LOOP_ID}",
  "prompt": "[original prompt from sabbath file]",
  "completion_promise": "[promise]",
  "max_iterations": [original max],
  "current_iteration": [where we stopped],
  "checkpoint_interval": [N],
  "loop_file": "[original loop file]",
  "resumed_from_sabbath": true,
  "resume_timestamp": "[now]"
}
EOF
```

### Step 6: Update Loop File

Add resume entry:

```markdown
## Sabbath Rest Resume

- **Resumed At:** [timestamp]
- **Previous Iteration:** [N]
- **Context:** Fresh (post-Sabbath Rest)
- **Sabbath File:** ${SABBATH_FILE}

### Restored Context Summary
[Key points from sabbath file]

---

## Loop Progress (Continued)

| Iteration | Timestamp | Action | Result | Context |
|-----------|-----------|--------|--------|---------|
| [N+1] | [now] | Resumed from Sabbath Rest | Fresh context | Fresh |
```

### Step 7: Update CONSCIENCE.md

```markdown
## Active Power Loop (Resumed)

- **ID:** ${LOOP_ID}
- **Resumed:** [timestamp]
- **Iteration:** [N] / [max] (continuing)
- **Status:** Running (fresh context)
- **Promise:** "[completion_promise]"
- **Context Health:** Fresh (post-Sabbath)

To cancel: `/fire-loop-stop`
```

### Step 8: Run /fire-discover (Optional)

If the loop was paused due to being stuck:

```
Would you like to run /fire-discover to find new patterns?
This may help if the loop was stuck before Sabbath Rest.

[Yes - run discovery] [No - continue with existing approach]
```

### Step 9: Display Resume Banner and Continue

```
+------------------------------------------------------------------------------+
| POWER LOOP RESUMED - ITERATION [N+1]                                         |
+------------------------------------------------------------------------------+
|                                                                              |
|  Loop ID: ${LOOP_ID}                                                         |
|  Continuing from: Iteration [N]                                              |
|  Remaining: [max - N] iterations                                             |
|  Context: FRESH                                                             |
|                                                                              |
|  Original Task:                                                              |
|    [prompt]                                                                  |
|                                                                              |
|  Completion Promise: "[promise]"                                             |
|                                                                              |
|  Immediate Action:                                                           |
|    [next step from sabbath file]                                             |
|                                                                              |
+------------------------------------------------------------------------------+
```

Then continue executing the task with fresh context.

---

## Edge Cases

### No Loops to Resume

```
+------------------------------------------------------------------------------+
| NO LOOPS TO RESUME                                                           |
+------------------------------------------------------------------------------+
|                                                                              |
|  No paused or stopped Power Loops found.                                     |
|                                                                              |
|  To start a new loop:                                                        |
|    /fire-loop "Your task" --max-iterations 30                               |
|                                                                              |
|  To list all loop files:                                                     |
|    ls .planning/loops/                                                       |
|                                                                              |
+------------------------------------------------------------------------------+
```

### Multiple Loops Available

```
+------------------------------------------------------------------------------+
| MULTIPLE LOOPS AVAILABLE                                                     |
+------------------------------------------------------------------------------+
|                                                                              |
|  Found multiple paused loops. Specify which to resume:                       |
|                                                                              |
|  1. 20260123-143052 - "Fix auth bug" (iter 15/30, context_rot)              |
|  2. 20260122-091530 - "Build API" (iter 8/50, user_stop)                    |
|  3. 20260121-162045 - "Refactor DB" (iter 22/40, session_end)               |
|                                                                              |
|  Resume with:                                                                |
|    /fire-loop-resume 20260123-143052                                        |
|                                                                              |
+------------------------------------------------------------------------------+
```

---

## Success Criteria

- [ ] Sabbath Rest snapshot found and loaded
- [ ] Context fully restored from snapshot
- [ ] Active loop config recreated
- [ ] Loop file updated with resume entry
- [ ] CONSCIENCE.md updated
- [ ] Fresh context confirmed
- [ ] Loop continues from correct iteration
- [ ] Original prompt and promise preserved

---

## References

- **Related:** `/fire-loop` - Start new loop
- **Related:** `/fire-loop-stop` - Stop active loop
- **Related:** `/fire-discover` - Find patterns when stuck
- **Skills:** `@skills-library/methodology/SABBATH_REST_PATTERN.md`
