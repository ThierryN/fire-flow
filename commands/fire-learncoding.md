---
description: Linear code walkthrough learning mode — transforms any repo into a step-by-step learning experience. Based on Simon Willison's Agentic Engineering Patterns.
argument-hint: "[on|off|--from-github URL|--from-path PATH] [--watch|--active] [--step N]"
---

# /fire-learncoding

> Turn any codebase into a linear learning walkthrough. Anti-vibe-coding. Anti-cognitive-debt.
> Grounded in Simon Willison's Agentic Engineering Patterns (simonwillison.net/guides/agentic-engineering-patterns/)

---

## The Philosophy

> "If you don't understand the code, your only recourse is to ask AI to fix it for you —
> like paying off credit card debt with another credit card." — Simon Willison

This mode prevents cognitive debt by walking through every file from the entry point outward,
explaining WHAT each piece does, WHY it's written that way, and WHICH pattern it uses.
Real code is extracted via shell tools (grep, cat, sed) — never paraphrased from memory.

---

## Arguments

```yaml
arguments:
  action:
    required: false
    type: string
    options: [on, off, --from-github, --from-path]
    description: "Toggle mode or load source"

  --from-github:
    type: string
    description: "GitHub repo URL to learn from"
    example: "/fire-learncoding --from-github https://github.com/user/repo"

  --from-path:
    type: string
    description: "Local path to learn from"
    example: "/fire-learncoding --from-path ./src"

  --watch:
    type: boolean
    default: true
    description: "Mode 1: Agent explains + scaffolds. You read and say 'next'."

  --active:
    type: boolean
    default: false
    description: "Mode 2: Agent explains purpose, you write the key logic."

  --step:
    type: integer
    description: "Jump to a specific step (resume)"
    example: "/fire-learncoding --step 5"

  --entry:
    type: string
    description: "Override entry point detection"
    example: "/fire-learncoding --entry src/server.ts"
```

---

## Mode Reference

| Mode | Flag | You do | Agent does |
|------|------|--------|------------|
| Watch | `--watch` (default) | Read + say "next" | Explains, scaffolds file |
| Active | `--active` | Write key logic sections | Explains purpose, marks `// WRITE THIS:` |
| Hybrid | `--hybrid` (future) | Fill in business logic TODOs | Scaffolds all boilerplate |

---

## Process

### Step 0: Load/Check Mode State

```bash
# Read mode config
MODE_FILE=".planning/learncoding.rc"
STEP_FILE=".planning/learncoding-progress.json"
```

**If `on` argument:**
```bash
mkdir -p .planning
echo 'LEARNCODING_MODE=watch' > .planning/learncoding.rc
echo "✓ Learncoding mode ON (--watch). Use /fire-learncoding --from-github URL to start."
exit 0
```

**If `off` argument:**
```bash
rm -f .planning/learncoding.rc .planning/learncoding-progress.json
echo "✓ Learncoding mode OFF."
exit 0
```

**If `--active` flag:**
```bash
echo 'LEARNCODING_MODE=active' > .planning/learncoding.rc
```

**Resume check:** If `.planning/learncoding-progress.json` exists and has `currentStep < totalSteps`:

```
📖 Learncoding session found — Step [N] of [M]
   Source: [repo/path]
   Mode: [watch|active]

→ Type "resume" to continue from Step N
→ Type "restart" to start from Step 1
```

### Step 1: Load Source

**If `--from-github <url>`:**

```bash
# Extract owner/repo from URL
REPO=$(echo "$URL" | sed 's|https://github.com/||')
# e.g. "simonw/datasette"

# Fetch file tree using gh CLI
gh api repos/$REPO/git/trees/HEAD?recursive=1 \
  --jq '.tree[] | select(.type=="blob") | .path' \
  > .planning/learncoding-files.txt

# Fetch key files content as needed per step using:
# gh api repos/$REPO/contents/{path} --jq '.content' | base64 -d
```

**If `--from-path <path>`:**
```bash
find "$PATH" -type f \( -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.rs" \) \
  | grep -v node_modules | grep -v __pycache__ | grep -v .git \
  > .planning/learncoding-files.txt
```

Display:
```
📦 Source loaded: [repo or path]
   Files found: [N]
   Detecting entry point...
```

### Step 2: Detect Entry Point

Spawn `fire-learncoding-walker` agent with the file list.

Walker returns:
```json
{
  "entryPoint": "src/index.ts",
  "steps": [
    { "order": 1, "file": "src/index.ts", "role": "Application entry", "imports": ["src/app.ts", "src/config.ts"] },
    { "order": 2, "file": "src/config.ts", "role": "Configuration loader", "imports": [] },
    { "order": 3, "file": "src/app.ts", "role": "Express app setup", "imports": ["src/routes/index.ts"] }
  ],
  "totalSteps": 12
}
```

Write to `.planning/learncoding-plan.json`.

Display learning plan:
```
╔══════════════════════════════════════════════════════════════╗
║            LEARNCODING — LEARNING PLAN                       ║
║  Source: [repo/path]        Mode: [watch|active]             ║
╠══════════════════════════════════════════════════════════════╣
║  Entry point: src/index.ts                                   ║
║  Total steps: 12                                             ║
╠══════════════════════════════════════════════════════════════╣
║  Step  1: src/index.ts        — Application entry            ║
║  Step  2: src/config.ts       — Configuration loader         ║
║  Step  3: src/app.ts          — Express app setup            ║
║  Step  4: src/routes/index.ts — Route registry               ║
║  ...                                                         ║
╚══════════════════════════════════════════════════════════════╝

Ready to start?
→ Type "start" to begin Step 1
→ Type "start --step N" to jump to a specific step
```

### Step 3: Run the Step Loop

For each step N from current position to totalSteps:

**Update progress:**
```json
{ "currentStep": N, "totalSteps": 12, "mode": "watch", "source": "..." }
```
Write to `.planning/learncoding-progress.json`.

**Spawn `fire-learncoding-explainer`** with:
- `step`: current step object (file path, role, order)
- `mode`: watch | active
- `source`: github repo or local path
- `totalSteps`: for breadcrumb display

**Wait for explainer to complete.**

**Read user input:**
- `next` / `n` / `continue` → advance to step N+1
- `explain more` / `more` → re-spawn explainer with `--deep` flag for deeper dive
- `why` → re-spawn explainer with `--why` flag for architectural reasoning
- `skip` → advance without scaffolding (mark as skipped in progress)
- `exit` / `done` → save progress, exit mode

**If mode is `--active`:** Wait for user to paste their code before accepting "next".

### Step 4: Completion

When all steps complete:

```
╔══════════════════════════════════════════════════════════════╗
║            LEARNCODING — WALKTHROUGH COMPLETE                ║
╠══════════════════════════════════════════════════════════════╣
║  Files walked:  [N]                                          ║
║  Files written: [N]                                          ║
║  Patterns seen: [list of patterns encountered]               ║
║                                                              ║
║  Your code is in: [output directory]                         ║
║                                                              ║
║  What you built:                                             ║
║    "[one sentence summary of what was learned]"              ║
║                                                              ║
║  Recommended next steps:                                     ║
║    1. Run the tests: [test command]                          ║
║    2. Start the app: [start command]                         ║
║    3. Read: simonwillison.net/guides/agentic-engineering-patterns/ ║
╚══════════════════════════════════════════════════════════════╝
```

Save walkthrough document to `.planning/learncoding-walkthrough.md` —
a full record of all steps, snippets, and explanations (reference for later).
