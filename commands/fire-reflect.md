# /fire-reflect

> Capture, search, and review failure reflections. Reflexion-style self-reflection for cross-session learning.

---

## Purpose

After any failure (debug resolution, test failure, approach rotation, stalled loop), capture **what was tried, why it failed, and what actually worked** as a persistent reflection. Future sessions search these before investigating.

**Research basis:** Reflexion (NeurIPS 2023) — 91% pass@1 via verbal self-reflection stored as linguistic memory.

---

## Arguments

```yaml
arguments:
  action:
    required: false
    type: string
    description: "Action to perform: capture (default), search, list, review"
    example: "/fire-reflect capture"

optional_flags:
  --from debug: "Auto-extract from most recent resolved debug session"
  --from session: "Extract from current session context"
  --project <name>: "Tag with project name"
  --severity <level>: "minor | moderate | critical (default: moderate)"
  --search <query>: "Search reflections by keyword/symptom"
```

---

## Process

### Step 1: Determine Action

```
IF args contain "search" or --search:
  → Go to Search Mode (Step 5)
IF args contain "list":
  → Go to List Mode (Step 6)
IF args contain "review":
  → Go to Review Mode (Step 7)
ELSE:
  → Capture Mode (Step 2)
```

### Step 2: Gather Reflection Content

**If `--from debug`:**
- Read most recent file in `.planning/debug/resolved/`
- Extract: symptoms, eliminated hypotheses, root cause, fix applied
- Auto-fill reflection fields

**If `--from session`:**
- Review current conversation context
- Identify: failed approaches, what was tried, what worked
- Auto-fill reflection fields

**If interactive (default):**
Ask using AskUserQuestion:

1. **What was the problem?** — Brief symptom description
2. **What did you try that failed?** — Each approach and why it didn't work
3. **What actually worked?** — The solution that resolved it
4. **The lesson** — One-sentence takeaway for future self
5. **Search triggers** — When should future agents find this?

### Step 3: Generate Reflection File

Create file at `~/.claude/reflections/{date}_{slug}.md`:

```markdown
---
type: reflection
date: {YYYY-MM-DD}
project: {project-name}
trigger: debug-resolution | test-failure | approach-rotation | stalled-loop
severity: minor | moderate | critical
tags: [{technology}, {pattern}, {symptom}]
---
# What I tried and why it failed

## The Problem
{Brief description of symptoms — what went wrong, what was observed}

## What I Tried (and why each failed)
1. **{Approach 1}** — {Why it didn't work. What was the evidence?}
2. **{Approach 2}** — {Why it didn't work. What disproved it?}

## What Actually Worked
{The solution. Be specific — include the code pattern, command, or insight.}

## The Lesson
{One-sentence takeaway. This is what a future agent reads first.}

## Future Self: Search For This When
- {Symptom 1 that should trigger finding this reflection}
- {Symptom 2}
- {Error message pattern}
```

### Step 4: Save and Confirm

```
Save to: ~/.claude/reflections/{date}_{slug}.md

Display:
+----------------------------------------------------------------------+
| REFLECTION CAPTURED                                                   |
+----------------------------------------------------------------------+
|                                                                      |
|  File: ~/.claude/reflections/{date}_{slug}.md                        |
|  Project: {project}                                                  |
|  Severity: {severity}                                                |
|  Tags: {tags}                                                        |
|                                                                      |
|  Lesson: {one-sentence lesson}                                       |
|                                                                      |
|  This reflection will be searchable via:                             |
|    /fire-remember "{symptom}" --type reflection                     |
|    /fire-reflect --search "{keyword}"                               |
|                                                                      |
+----------------------------------------------------------------------+
```

### Step 5: Search Mode

When called with `--search` or `search` action:

```
1. Search ~/.claude/reflections/ for matching files
2. Use keyword matching on: tags, problem description, lesson, search triggers
3. If vector memory available:
   /fire-remember "{query}" --type reflection
4. Display matching reflections ranked by relevance

Output:
  1. [{date}] {slug} — Severity: {severity}
     Lesson: {one-sentence lesson}
     Tags: {tags}
     Match: {what matched}

  2. ...
```

### Step 6: List Mode

```
List all reflections sorted by date (newest first):

  # | Date       | Project     | Severity | Lesson
  1 | 2026-02-20 | voice-bridge | critical | VK codes stable, char corrupted by Ctrl
  2 | 2026-02-19 | dominion-flow   | moderate | ...
  ...

  Total: {N} reflections across {M} projects
```

### Step 7: Review Mode

Read a specific reflection and display it formatted:

```
/fire-reflect review {slug-or-number}
```

---

## Auto-Trigger Integration

Reflections are auto-generated by other commands:

| Trigger | Command | When |
|---------|---------|------|
| Debug resolution | `/fire-debug` Step 7.5 | After root cause found and fix verified |
| Stalled loop | `/fire-loop` Step 9 | On STALLED → SPINNING transition |
| Approach rotation | `/fire-loop` Step 9 | On SPINNING state (forced rotation) |

Auto-generated reflections use `--from debug` or `--from session` to extract context automatically.

---

## Pre-Investigation Search

Before starting any debug or complex task, search reflections:

```
Search reflections for: "[error symptoms]"
If match found with relevant lesson:
  "I've encountered this before — {lesson}. Applying directly instead of re-investigating."
```

This is wired into:
- `/fire-debug` Step 2.5 — Search before investigating
- `/fire-loop` iteration start — Check for known failure patterns

---

## Reflection Quality Guidelines

**Good reflection:**
- Specific symptoms (error messages, behaviors)
- Multiple failed approaches with reasons
- Concrete solution (code, command, config change)
- One-sentence lesson that's useful without context
- Search triggers that match how you'd describe the problem

**Bad reflection:**
- Vague ("something was wrong")
- Only records the solution without the journey
- No search triggers
- Lesson is too abstract ("be more careful")

---

## Success Criteria

- [ ] Reflection file created with all sections filled
- [ ] Tags extracted from problem domain
- [ ] Severity classified correctly
- [ ] Search triggers are realistic symptom descriptions
- [ ] Lesson is a single actionable sentence
- [ ] File saved to `~/.claude/reflections/`

---

## References

- **Research:** Reflexion (NeurIPS 2023) — verbal self-reflection, 91% pass@1
- **Storage:** `~/.claude/reflections/` — searchable via vector memory
- **Index:** Qdrant sourceType: `reflection` — auto-indexed by your-memory-repo
- **Related:** `/fire-debug`, `/fire-loop`, `/fire-remember`
