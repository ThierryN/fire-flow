---
description: Orient on an existing project - understand what's here and what's next
---

# /fire-0-orient

> First contact with an existing project

---

## Purpose

When an AI agent joins an existing project with no prior handoff, this command scans the codebase and project state to understand:
1. What is this project?
2. What's the current state?
3. What should happen next?

This is the "new agent orientation" - like a new employee's first day understanding the codebase.

---

## Arguments

```yaml
arguments:
  --deep:
    required: false
    type: boolean
    default: false
    description: "Perform deep codebase analysis (takes longer)"

  --scan-only:
    required: false
    type: boolean
    default: false
    description: "Only scan, don't recommend next action"

  --output:
    required: false
    type: string
    description: "Save orientation report to file"
```

---

## When to Use

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ USE /fire-0-orient WHEN:                                                   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                             â”‚
â”‚  âœ“ You're a NEW agent on this project                                       â”‚
â”‚  âœ“ No WARRIOR handoff file exists                                           â”‚
â”‚  âœ“ User says "let's get started" or "what's next"                           â”‚
â”‚  âœ“ You're unsure what state the project is in                               â”‚
â”‚  âœ“ Context was reset/compacted and you need to re-orient                    â”‚
â”‚                                                                             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ DON'T USE WHEN:                                                             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                             â”‚
â”‚  âœ— Starting a NEW project â†’ use /fire-1a-new                                â”‚
â”‚  âœ— Handoff file exists â†’ use /fire-6-resume                                â”‚
â”‚  âœ— You already understand the project                                       â”‚
â”‚                                                                             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Process

### Step 1: State Discovery

```
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
                         DOMINION FLOW â–º ORIENTATION
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

â—† Scanning for project state...
```

**Check for existing state files:**

```bash
# Priority order for state discovery
STATE_FILES=(
  ".planning/CONSCIENCE.md"                    # Dominion Flow state
  ".planning/VISION.md"                  # Project roadmap
  ".claude/*.local.md"                    # Sabbath Rest session files
  "C:/Users/FirstName/.claude/warrior-handoffs/*.md"  # WARRIOR handoffs
  "PROJECT.md"                            # Dominion Flow project file
  "README.md"                             # Standard readme
  "package.json"                          # Node.js project info
  ".git"                                  # Git history
)
```

**Discovery Results:**
```
â—† State Discovery Results

  .planning/ directory:     {EXISTS | NOT FOUND}
  CONSCIENCE.md:                 {EXISTS | NOT FOUND}
  VISION.md:               {EXISTS | NOT FOUND}
  Sabbath Rest files:       {count} found
  WARRIOR handoffs:         {count} found
  Git repository:           {YES | NO}
```

### Step 2: Codebase Analysis

If `--deep` flag or no CONSCIENCE.md found:

```
â—† Analyzing codebase structure...
```

**Detect Project Type:**
```
Analysis Points:
â”œâ”€â”€ Language/Framework:    {detected from files}
â”œâ”€â”€ Package Manager:       {npm/yarn/pnpm/pip/etc}
â”œâ”€â”€ Build System:          {webpack/vite/tsc/etc}
â”œâ”€â”€ Database:              {postgres/mongo/prisma/etc}
â”œâ”€â”€ Test Framework:        {jest/vitest/pytest/etc}
â””â”€â”€ Deployment:            {vercel/docker/etc}
```

**Scan for Patterns:**
```bash
# Look for common patterns
grep -r "TODO\|FIXME\|HACK" --include="*.ts" --include="*.tsx" | head -10
git log --oneline -10   # Recent activity
git status              # Uncommitted changes
```

### Step 3: Handoff Check

**Search for recent handoffs:**
```
â—† Checking for session handoffs...

  Location: C:/Users/FirstName/.claude/warrior-handoffs/

  Recent Handoffs Found:
  â”œâ”€â”€ {filename} - {date} - {project}
  â”œâ”€â”€ {filename} - {date} - {project}
  â””â”€â”€ {filename} - {date} - {project}
```

**If handoff matches this project:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ HANDOFF FOUND                                                               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                             â”‚
â”‚  A WARRIOR handoff exists for this project:                                 â”‚
â”‚  {filename}                                                                 â”‚
â”‚  Created: {date}                                                            â”‚
â”‚                                                                             â”‚
â”‚  RECOMMENDATION: Use /fire-6-resume to load full context                   â”‚
â”‚                                                                             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Step 4: State Assessment

Based on discovery, determine project state:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ PROJECT STATE ASSESSMENT                                                    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                             â”‚
â”‚  Project: {name from package.json or directory}                             â”‚
â”‚  Type: {detected type}                                                      â”‚
â”‚  Tech Stack: {detected stack}                                               â”‚
â”‚                                                                             â”‚
â”‚  Dominion Flow Status:                                                         â”‚
â”‚  â”œâ”€â”€ Initialized: {YES/NO}                                                  â”‚
â”‚  â”œâ”€â”€ Current Phase: {N of M / NOT SET}                                      â”‚
â”‚  â”œâ”€â”€ Phase Status: {planning/executing/verifying/complete}                  â”‚
â”‚  â””â”€â”€ Last Activity: {date from CONSCIENCE.md or git}                             â”‚
â”‚                                                                             â”‚
â”‚  Sabbath Rest (Session State):                                              â”‚
â”‚  â”œâ”€â”€ dominion-flow.local.md: {status}                                          â”‚
â”‚  â”œâ”€â”€ fire-debugger.local.md: {status}                                      â”‚
â”‚  â””â”€â”€ [other .local.md files]                                                â”‚
â”‚                                                                             â”‚
â”‚  Code Health:                                                               â”‚
â”‚  â”œâ”€â”€ Uncommitted Changes: {count files}                                     â”‚
â”‚  â”œâ”€â”€ TODOs/FIXMEs: {count}                                                  â”‚
â”‚  â””â”€â”€ Recent Commits: {last commit message}                                  â”‚
â”‚                                                                             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Step 4.5: Security Baseline Scan (v5.0)

> **Defense basis:** OWASP ASI04 (Supply Chain Vulnerabilities)
> — First contact with a project is the ideal time to establish a security baseline.

**On first orientation, scan the project's trust surface:**

```
SECURITY BASELINE SCAN
  Scanning project trust surface...

  Skills library: {N files scanned}       ... {CLEAN | N findings}
  Plugin commands: {N files scanned}      ... {CLEAN | N findings}
  Plugin hooks: {N files scanned}         ... {CLEAN | N findings}
  MCP tool descriptions: {N checked}      ... {CLEAN | N findings}

  Verdict: {CLEAN | REVIEW NEEDED}
```

**What to scan:**
1. All `.md` files in the project's skills library (if it has one)
2. All plugin commands and hooks in `~/.claude/plugins/*/`
3. Any `.claude/` config files in the project root
4. MCP tool descriptions currently loaded

**Apply quick scan (Layers 1-5) from `security/agent-security-scanner.md`:**
- Layer 1: Invisible Unicode characters
- Layer 2: Prompt injection signatures
- Layer 3: Credential harvesting patterns
- Layer 4: PII collection indicators
- Layer 5: Tool poisoning markers

**If CLEAN:** Display one-line summary in the State Assessment box and continue.

**If findings detected:**
```
Use AskUserQuestion:
  header: "Security"
  question: "Security baseline found {N} issues in this project. Review before continuing?"
  options:
    - "Show details" - Display all findings with context
    - "Full scan" - Run /fire-security-scan --all-plugins --deep --report
    - "Continue anyway" - Accept risk and proceed to recommendation
```

**Why on orient:** A new agent joining a project is the most vulnerable moment — it has no prior context to judge what's legitimate. Scanning before trusting anything is like checking the locks before sleeping in a new house.

### Step 5: Generate Recommendation

Based on assessment, recommend next action:

**Scenario A: Dominion Flow Not Initialized**
```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ RECOMMENDATION: Initialize Dominion Flow                                        â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  This project exists but Dominion Flow is not set up.                          â•‘
â•‘                                                                              â•‘
â•‘  Detected:                                                                   â•‘
â•‘  â”œâ”€â”€ {tech stack}                                                            â•‘
â•‘  â”œâ”€â”€ {project type}                                                          â•‘
â•‘  â””â”€â”€ {code state}                                                            â•‘
â•‘                                                                              â•‘
â•‘  Options:                                                                    â•‘
â•‘                                                                              â•‘
â•‘  A) Initialize Dominion Flow for this project:                                  â•‘
â•‘     â†’ /fire-1a-new                                                           â•‘
â•‘     Creates: .planning/, CONSCIENCE.md, VISION.md                                â•‘
â•‘                                                                              â•‘
â•‘  B) Work without Dominion Flow (ad-hoc):                                        â•‘
â•‘     â†’ Just ask what you need                                                 â•‘
â•‘     No structured workflow tracking                                          â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

**Scenario B: Dominion Flow Initialized, Phase In Progress**
```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ RECOMMENDATION: Continue Phase Execution                                     â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Project: {name}                                                             â•‘
â•‘  Current: Phase {N} - {name}                                                 â•‘
â•‘  Status: {status}                                                            â•‘
â•‘                                                                              â•‘
â•‘  From CONSCIENCE.md:                                                              â•‘
â•‘  {relevant excerpt}                                                          â•‘
â•‘                                                                              â•‘
â•‘  Options:                                                                    â•‘
â•‘                                                                              â•‘
â•‘  A) View detailed status:                                                    â•‘
â•‘     â†’ /fire-dashboard                                                       â•‘
â•‘                                                                              â•‘
â•‘  B) Continue execution:                                                      â•‘
â•‘     â†’ /fire-3-execute {N}                                                   â•‘
â•‘                                                                              â•‘
â•‘  C) Verify what's done:                                                      â•‘
â•‘     â†’ /fire-4-verify {N}                                                    â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

**Scenario C: Phase Complete, Ready for Next**
```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ RECOMMENDATION: Plan Next Phase                                              â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Project: {name}                                                             â•‘
â•‘  Completed: Phase {N-1} - {name}                                             â•‘
â•‘  Next: Phase {N} - {name}                                                    â•‘
â•‘                                                                              â•‘
â•‘  Options:                                                                    â•‘
â•‘                                                                              â•‘
â•‘  A) Discuss phase requirements first:                                        â•‘
â•‘     â†’ /fire-1a-discuss {N}                                                     â•‘
â•‘     Gather context before planning                                           â•‘
â•‘                                                                              â•‘
â•‘  B) Go straight to planning:                                                 â•‘
â•‘     â†’ /fire-2-plan {N}                                                      â•‘
â•‘     Create execution plan                                                    â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

**Scenario D: Handoff Found**
```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ RECOMMENDATION: Resume from Handoff                                          â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  A WARRIOR handoff was found for this project:                               â•‘
â•‘  {handoff filename}                                                          â•‘
â•‘  Created: {date}                                                             â•‘
â•‘                                                                              â•‘
â•‘  The handoff contains full context from the previous session.                â•‘
â•‘                                                                              â•‘
â•‘  Action:                                                                     â•‘
â•‘  â†’ /fire-6-resume                                                           â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

### Step 6: Sabbath Rest

> *Like humans need sleep to reset, AI agents need state files to resume after context resets.*

**Create/Update:** `.claude/dominion-flow.local.md`

```markdown
---
last_session: {timestamp}
command: "orient"
status: complete
project_state: {initialized | not_initialized | in_progress | handoff_found}
recommendation: "{recommended command}"
---

# Orientation Session State

## Last Orientation
- Date: {timestamp}
- Project: {name}
- Result: {summary}

## Detected State
- Dominion Flow: {initialized | not initialized}
- Current Phase: {N or N/A}
- Handoff: {found | not found}

## Recommendation Given
{recommended action}
```

---

## Output Format

### Full Orientation Report

```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘                      DOMINION FLOW â–º ORIENTATION COMPLETE                       â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                              â•‘
â•‘  Project: {name}                                                             â•‘
â•‘  Location: {path}                                                            â•‘
â•‘  Scanned: {timestamp}                                                        â•‘
â•‘                                                                              â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘ PROJECT UNDERSTANDING                                                        â•‘
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â•‘                                                                              â•‘
â•‘  Type: {project type}                                                        â•‘
â•‘  Stack: {tech stack}                                                         â•‘
â•‘  Status: {active | stale | new}                                              â•‘
â•‘                                                                              â•‘
â•‘  Description:                                                                â•‘
â•‘  {from README or package.json description}                                   â•‘
â•‘                                                                              â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘ DOMINION FLOW STATE                                                             â•‘
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â•‘                                                                              â•‘
â•‘  Initialized: {YES/NO}                                                       â•‘
â•‘  Phase: {N of M}                                                             â•‘
â•‘  Status: {planning | executing | verifying | complete}                       â•‘
â•‘  Last Activity: {date}                                                       â•‘
â•‘                                                                              â•‘
â•‘  Sabbath Rest Files:                                                         â•‘
â•‘  {list of .local.md files found}                                             â•‘
â•‘                                                                              â•‘
â•‘  WARRIOR Handoffs:                                                           â•‘
â•‘  {list of relevant handoffs}                                                 â•‘
â•‘                                                                              â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘ RECOMMENDATION                                                               â•‘
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â•‘                                                                              â•‘
â•‘  {recommendation based on state}                                             â•‘
â•‘                                                                              â•‘
â•‘  Suggested Command: {command}                                                â•‘
â•‘                                                                              â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

---

## Routing Logic

```
START
  â”‚
  â”œâ”€â–º Check WARRIOR handoffs
  â”‚     â”œâ”€â–º Found for this project â†’ RECOMMEND /fire-6-resume
  â”‚     â””â”€â–º Not found â†’ Continue
  â”‚
  â”œâ”€â–º Check .planning/CONSCIENCE.md
  â”‚     â”œâ”€â–º Not found â†’ RECOMMEND /fire-1a-new
  â”‚     â””â”€â–º Found â†’ Continue
  â”‚
  â”œâ”€â–º Parse CONSCIENCE.md for current phase
  â”‚     â”œâ”€â–º Phase in progress â†’ RECOMMEND /fire-3-execute or /fire-dashboard
  â”‚     â”œâ”€â–º Phase complete â†’ RECOMMEND /fire-2-plan (next) or /fire-1a-discuss
  â”‚     â””â”€â–º All phases done â†’ RECOMMEND new milestone
  â”‚
  â””â”€â–º END with recommendation
```

---

## Related Commands

- `/fire-1a-new` - Initialize Dominion Flow for new projects
- `/fire-6-resume` - Resume from WARRIOR handoff
- `/fire-dashboard` - View detailed project status
- `/fire-1a-discuss` - Gather context before planning

---

## Examples

```bash
# Quick orientation
/fire-0-orient

# Deep analysis of unfamiliar codebase
/fire-0-orient --deep

# Just scan, don't recommend
/fire-0-orient --scan-only

# Save report to file
/fire-0-orient --output orientation-report.md
```
