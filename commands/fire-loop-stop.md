---
description: Cancel the active Power Loop and save progress
---

# /fire-loop-stop

> Cancel active Power Loop with progress preservation

---

## Purpose

Safely cancel an active Power Loop, preserving all progress made and updating tracking files. Use this when you need to:

- Stop a loop that's not making progress
- Pause work to resume later
- Cancel a loop started with wrong parameters

---

## Process

### Step 1: Check for Active Loop

```bash
if [ ! -f ".planning/loops/active-loop.json" ]; then
  echo "No active Power Loop found."
  exit 0
fi
```

### Step 2: Read Loop State

```bash
LOOP_ID=$(jq -r '.id' .planning/loops/active-loop.json)
LOOP_FILE=$(jq -r '.loop_file' .planning/loops/active-loop.json)
CURRENT_ITERATION=$(jq -r '.current_iteration' .planning/loops/active-loop.json)
MAX_ITERATIONS=$(jq -r '.max_iterations' .planning/loops/active-loop.json)
```

### Step 3: Create Sabbath Rest Snapshot

Save current state for potential resume:

```markdown
## .planning/loops/sabbath-${LOOP_ID}-stopped.md

---
loop_id: ${LOOP_ID}
iteration: [current]
timestamp: [ISO]
reason: user_requested_stop
---

## State at Stop

### Progress Summary
- Iterations completed: [N]
- Last action: [description]

### Files Modified
- [file]: [change summary]

### Next Steps (if resumed)
1. [what to do next]

### Key Context
[Critical information for resume]
```

### Step 4: Update Loop File

Add cancellation entry to loop file:

```markdown
## Final Result

- **Status:** cancelled_by_user
- **Total Iterations:** [current_iteration]
- **Cancelled At:** [timestamp]
- **Reason:** User requested stop via /fire-loop-stop

### Progress at Cancellation
[Summary of what was accomplished]

### Files Changed
- [list of files modified during loop]

### Resume Instructions
To resume this work:
  /fire-loop-resume ${LOOP_ID}
```

### Step 5: Clean Up Active Loop

```bash
# Archive the active loop config
mv .planning/loops/active-loop.json ".planning/loops/stopped-${LOOP_ID}.json"
```

### Step 6: Update CONSCIENCE.md

Remove the "Active Power Loop" section from CONSCIENCE.md.

Add to history:

```markdown
## Recent Loop (Stopped)

- **ID:** ${LOOP_ID}
- **Iterations:** [N] / [MAX]
- **Stopped:** [timestamp]
- **Resume:** `/fire-loop-resume ${LOOP_ID}`
```

### Step 7: Update Sabbath Rest State

```markdown
## .claude/fire-flow.local.md

### Power Loop - Stopped
- Loop ID: ${LOOP_ID}
- Status: stopped_by_user
- Iterations: [N] / [MAX]
- Stopped: [timestamp]
- Resume: /fire-loop-resume ${LOOP_ID}
- Sabbath File: .planning/loops/sabbath-${LOOP_ID}-stopped.md
```

### Step 8: Display Confirmation

```
+------------------------------------------------------------------------------+
| POWER LOOP STOPPED                                                           |
+------------------------------------------------------------------------------+
|                                                                              |
|  Loop ID: ${LOOP_ID}                                                         |
|  Iterations Completed: [N] / [MAX]                                           |
|  Status: Stopped by user                                                     |
|                                                                              |
|  Progress Saved:                                                             |
|    - Loop file: ${LOOP_FILE}                                                 |
|    - Sabbath snapshot: .planning/loops/sabbath-${LOOP_ID}-stopped.md        |
|    - Git commits: [count] iteration commits                                  |
|                                                                              |
|  To resume later:                                                            |
|    /fire-loop-resume ${LOOP_ID}                                             |
|                                                                              |
|  To review progress:                                                         |
|    cat ${LOOP_FILE}                                                          |
|                                                                              |
+------------------------------------------------------------------------------+
```

---

## Edge Cases

### No Active Loop

```
+------------------------------------------------------------------------------+
| NO ACTIVE LOOP                                                               |
+------------------------------------------------------------------------------+
|                                                                              |
|  No Power Loop is currently running.                                         |
|                                                                              |
|  To start a new loop:                                                        |
|    /fire-loop "Your task" --max-iterations 30                               |
|                                                                              |
|  To view past loops:                                                         |
|    ls .planning/loops/                                                       |
|                                                                              |
|  To resume a stopped loop:                                                   |
|    /fire-loop-resume [LOOP_ID]                                              |
|                                                                              |
+------------------------------------------------------------------------------+
```

---

## Success Criteria

- [ ] Active loop detected (or message if none)
- [ ] Sabbath Rest snapshot created
- [ ] Loop file updated with stop status
- [ ] Active loop config archived
- [ ] CONSCIENCE.md updated
- [ ] Sabbath Rest state updated
- [ ] Confirmation displayed with resume instructions

---

## References

- **Related:** `/fire-loop` - Start a new loop
- **Related:** `/fire-loop-resume` - Resume stopped/paused loop
- **Related:** `/fire-debug` - Structured debugging alternative
