---
description: Capture, list, and manage todos during work sessions
---

# /fire-todos

> Capture ideas and tasks during sessions, list pending todos, and select work

---

## Purpose

Quick task capture and review system for ideas, issues, and tasks that surface during Dominion Flow sessions. Enables "thought -> capture -> continue" flow without losing context or derailing current work.

**Commands:**
- `/fire-todos add [description]` - Capture a new todo
- `/fire-todos list [area]` - List pending todos
- `/fire-todos` (no args) - List all pending todos

---

## Arguments

```yaml
arguments:
  action:
    required: false
    type: string
    enum: [add, list]
    default: list
    description: "Action to perform"

  description:
    required: false
    type: string
    description: "For 'add': description of the todo. For 'list': optional area filter"

examples:
  - "/fire-todos" - List all pending todos
  - "/fire-todos add Fix auth token refresh" - Add a new todo
  - "/fire-todos list api" - List todos in 'api' area
```

---

## Process: Add Todo

### Step 1: Ensure Directory

```bash
mkdir -p .planning/todos/pending .planning/todos/done
```

### Step 2: Check Existing Areas

```bash
ls .planning/todos/pending/*.md 2>/dev/null | xargs -I {} grep "^area:" {} 2>/dev/null | cut -d' ' -f2 | sort -u
```

Note existing areas for consistency.

### Step 3: Extract Content

**With arguments:** Use as the title/focus.
- `/fire-todos add Fix auth token refresh` -> title = "Fix auth token refresh"

**Without arguments:** Analyze recent conversation to extract:
- The specific problem, idea, or task discussed
- Relevant file paths mentioned
- Technical details (error messages, line numbers)

Formulate:
- `title`: 3-10 word descriptive title (action verb preferred)
- `problem`: What's wrong or why this is needed
- `solution`: Approach hints or "TBD" if just an idea
- `files`: Relevant paths from conversation

### Step 4: Infer Area

| Path pattern | Area |
|--------------|------|
| `src/api/*`, `api/*` | `api` |
| `src/components/*`, `src/ui/*` | `ui` |
| `src/auth/*`, `auth/*` | `auth` |
| `src/db/*`, `database/*` | `database` |
| `tests/*`, `__tests__/*` | `testing` |
| `docs/*` | `docs` |
| `.planning/*` | `planning` |
| `scripts/*`, `bin/*` | `tooling` |
| No files or unclear | `general` |

### Step 5: Check Duplicates

```bash
grep -l -i "[key words from title]" .planning/todos/pending/*.md 2>/dev/null
```

If potential duplicate found:

Use AskUserQuestion:
- header: "Duplicate?"
- question: "Similar todo exists: [title]. What would you like to do?"
- options:
  - "Skip" - Keep existing todo
  - "Replace" - Update existing with new context
  - "Add anyway" - Create as separate todo

### Step 6: Create File

```bash
timestamp=$(date "+%Y-%m-%dT%H:%M")
date_prefix=$(date "+%Y-%m-%d")
```

Write to `.planning/todos/pending/${date_prefix}-${slug}.md`:

```markdown
---
created: [timestamp]
title: [title]
area: [area]
files:
  - [file:lines]
---

## Problem

[problem description - enough context for future Claude to understand weeks later]

## Solution

[approach hints or "TBD"]
```

### Step 7: Commit

```bash
git add .planning/todos/pending/[filename]
[ -f .planning/CONSCIENCE.md ] && git add .planning/CONSCIENCE.md
git commit -m "$(cat <<'EOF'
docs: capture todo - [title]

Area: [area]
EOF
)"
```

### Step 8: Confirm

```
Todo saved: .planning/todos/pending/[filename]

  [title]
  Area: [area]
  Files: [count] referenced

---

Would you like to:
1. Continue with current work
2. Add another todo
3. View all todos (/fire-todos list)
```

---

## Process: List Todos

### Step 1: Check Exist

```bash
TODO_COUNT=$(ls .planning/todos/pending/*.md 2>/dev/null | wc -l | tr -d ' ')
```

If count is 0:
```
No pending todos.

Todos are captured during work sessions with /fire-todos add.

---

Would you like to:
1. Continue with current phase (/fire-dashboard)
2. Add a todo now (/fire-todos add)
```

### Step 2: Parse Filter

- `/fire-todos list` -> show all
- `/fire-todos list api` -> filter to area:api only

### Step 3: List Todos

```bash
for file in .planning/todos/pending/*.md; do
  created=$(grep "^created:" "$file" | cut -d' ' -f2)
  title=$(grep "^title:" "$file" | cut -d':' -f2- | xargs)
  area=$(grep "^area:" "$file" | cut -d' ' -f2)
  echo "$created|$title|$area|$file"
done | sort
```

Display as numbered list:

```
Pending Todos:

1. Add auth token refresh (api, 2d ago)
2. Fix modal z-index issue (ui, 1d ago)
3. Refactor database connection pool (database, 5h ago)

---

Reply with a number to view details, or:
- `/fire-todos list [area]` to filter by area
- `q` to exit
```

### Step 4: Handle Selection

Wait for user to reply with a number.

Load selected todo and display full context:

```
## [title]

**Area:** [area]
**Created:** [date] ([relative time] ago)
**Files:** [list or "None"]

### Problem
[problem section content]

### Solution
[solution section content]
```

### Step 5: Offer Actions

**If todo maps to a roadmap phase:**

Use AskUserQuestion:
- header: "Action"
- question: "This todo relates to Phase [N]: [name]. What would you like to do?"
- options:
  - "Work on it now" - Move to done, start working
  - "Add to phase plan" - Include when planning Phase [N]
  - "Brainstorm approach" - Think through before deciding
  - "Put it back" - Return to list

**If no roadmap match:**

Use AskUserQuestion:
- header: "Action"
- question: "What would you like to do with this todo?"
- options:
  - "Work on it now" - Move to done, start working
  - "Create a phase" - Add phase with this scope
  - "Brainstorm approach" - Think through before deciding
  - "Put it back" - Return to list

### Step 6: Execute Action

**Work on it now:**
```bash
mv ".planning/todos/pending/[filename]" ".planning/todos/done/"
```
Update CONSCIENCE.md. Present context. Begin work.

**Add to phase plan:**
Note todo reference in phase planning notes. Keep in pending.

**Create a phase:**
Route to: `/fire-add-phase [description from todo]`

**Brainstorm approach:**
Keep in pending. Start discussion about problem and approaches.

**Put it back:**
Return to list.

---

## Sabbath Rest - Context Persistence

After any todo action, update persistent state:

```markdown
## .claude/dominion-flow.local.md

### Todos
- Pending: [count]
- Last added: [title] ({timestamp})
- Last action: [work|add|brainstorm]
```

---

## Success Criteria

### For Add
- [ ] Directory structure exists
- [ ] Todo file created with valid frontmatter
- [ ] Problem section has enough context
- [ ] No duplicates (checked and resolved)
- [ ] Area consistent with existing todos
- [ ] Committed to git

### For List
- [ ] All pending todos listed with title, area, age
- [ ] Area filter applied if specified
- [ ] Selected todo's full context loaded
- [ ] Roadmap context checked for phase match
- [ ] Appropriate actions offered
- [ ] Selected action executed
- [ ] CONSCIENCE.md updated if todo count changed

---

## Anti-Patterns

- Don't delete todos - move to done/ when work begins
- Don't start work without moving to done/ first
- Don't create elaborate solution sections - captures ideas, not plans
- Don't create todos for work in current plan (that's deviation territory)

---

## References

- **Related:** `/fire-dashboard` - See project status including todo count
- **Related:** `/fire-2-plan` - Plan phase that may include todo work
- **Brand:** `@references/ui-brand.md`
