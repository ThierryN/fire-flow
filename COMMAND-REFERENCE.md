# Dominion Flow Command Reference

Complete reference for all 42 Dominion Flow commands.

---

## Command Tiers

Commands are organized into 8 tiers by function. Every command is a `/fire-*` slash command.

---

### Tier 1 -- Core Workflow (the essential 6+1)

The numbered pipeline that takes a project from idea to done.

| Command | Description |
|---------|-------------|
| `/fire-1-new` | Initialize a new project with Dominion Flow structure |
| `/fire-1a-discuss` | Gather implementation context through adaptive questioning before planning |
| `/fire-2-plan` | Plan a phase with skills library access and WARRIOR validation |
| `/fire-3-execute` | Execute a phase with breath-based parallelism and honesty protocols |
| `/fire-4-verify` | Verify phase completion with must-haves and 70-point validation |
| `/fire-5-handoff` | Create comprehensive session handoff for next AI agent |
| `/fire-6-resume` | Resume from previous session handoff with full context restoration |

---

### Tier 2 -- Autonomous & Loop

Self-iterating and fully autonomous execution modes.

| Command | Description |
|---------|-------------|
| `/fire-autonomous` | Full autopilot -- plan, execute, verify all phases autonomously after PRD is complete |
| `/fire-loop` | Start self-iterating loop until completion with circuit breaker, error classification, context engineering, and skills integration |
| `/fire-loop-resume` | Resume a Power Loop from Sabbath Rest or stopped state |
| `/fire-loop-stop` | Cancel the active Power Loop and save progress |

---

### Tier 3 -- Debugging & Discovery

Investigation, research, and exploration tools.

| Command | Description |
|---------|-------------|
| `/fire-debug` | Systematic debugging with persistent state, skills library integration, and WARRIOR validation |
| `/fire-discover` | AI-powered pattern discovery and skill suggestions |
| `/fire-map-codebase` | Analyze codebase with parallel mapper agents to produce structured documentation |
| `/fire-0-orient` | Orient on an existing project -- understand what's here and what's next |
| `/fire-research` | Research how to implement a phase with 3-level discovery before planning |
| `/fire-brainstorm` | Dedicated ideation and exploration before implementation |

---

### Tier 4 -- Verification & Security

Quality assurance, testing, and security scanning.

| Command | Description |
|---------|-------------|
| `/fire-7-review` | Multi-perspective code review with 14 specialized reviewer personas |
| `/fire-verify-uat` | Conversational User Acceptance Testing with automatic parallel diagnosis on failures |
| `/fire-test` | Run Dominion Flow plugin integration tests to verify all commands and integrations work correctly |
| `/fire-security-scan` | Inspect skills, plugins, MCP tools, and code for prompt injection, PII harvesting, credential theft, and supply chain attacks |
| `/fire-vuln-scan` | AI-powered application vulnerability scanner using OWASP Top 10 -- find what regex-based tools miss |
| `/fire-security-audit-repo` | Security audit a GitHub repo before installing as a skill or plugin |
| `/fire-double-check` | Deep validation before claiming work is complete |

---

### Tier 5 -- Skills Management

Skills library operations: search, add, sync, version control.

| Command | Description |
|---------|-------------|
| `/fire-search` | Search the skills library for patterns, solutions, and best practices |
| `/fire-add-new-skill` | Add a new skill to the skills library when you solve a hard problem |
| `/fire-skills-sync` | Synchronize skills between project library and global library |
| `/fire-skills-history` | View version history for a skill in the skills library |
| `/fire-skills-rollback` | Rollback a skill to a previous version |
| `/fire-skills-diff` | Compare different versions of a skill |

---

### Tier 6 -- Analytics & Project Management

Dashboards, tracking, reflection, and phase transitions.

| Command | Description |
|---------|-------------|
| `/fire-dashboard` | Display visual project dashboard with status and progress |
| `/fire-analytics` | View skills usage analytics and effectiveness metrics |
| `/fire-todos` | Capture, list, and manage todos during work sessions |
| `/fire-reflect` | Capture, search, and review failure reflections for cross-session learning |
| `/fire-assumptions` | List and validate assumptions for a phase before planning or execution |
| `/fire-session-summary` | Auto-generate compact session summary with aggregate status, readiness, outlook, and next steps |
| `/fire-transition` | Complete phase transition with metrics collection, bottleneck detection, auto-skill extraction, and trend analysis |

---

### Tier 7 -- Milestone & Advanced

Milestone lifecycle management and advanced operations.

| Command | Description |
|---------|-------------|
| `/fire-new-milestone` | Start a new milestone cycle with questioning, research, requirements, and roadmap |
| `/fire-complete-milestone` | Archive completed milestone and prepare for next version with WARRIOR validation |
| `/fire-execute-plan` | Execute a single plan with segment-based routing, per-task atomic commits, and test enforcement |
| `/fire-update` | Check for and apply plugin updates from GitHub repository |

---

### Tier 8 -- Learning Mode

Code walkthrough and learning tools.

| Command | Description |
|---------|-------------|
| `/fire-learncoding` | Linear code walkthrough learning mode -- transforms any repo into a step-by-step learning experience based on Simon Willison's Agentic Engineering Patterns |

---

## Agent Reference

Agents are specialized sub-agents spawned by commands to perform focused work.

| Agent | Description | Tools | Spawned By |
|-------|-------------|-------|------------|
| `fire-executor` | Executes plans with honesty protocols and creates unified handoff documents | Read, Write, Edit, Glob, Grep, Bash, WebSearch, Task, TodoWrite | `/fire-3-execute`, `/fire-execute-plan`, `/fire-autonomous` |
| `fire-planner` | Creates phase plans with skills library integration and WARRIOR validation | Read, Write, Edit, Glob, Grep, Bash, WebSearch, Task, TodoWrite | `/fire-2-plan`, `/fire-autonomous` |
| `fire-researcher` | Researches phase context using skills library and pattern matching | Read, Write, Glob, Grep, Bash, WebSearch, Task | `/fire-research`, `/fire-1-new`, `/fire-2-plan` |
| `fire-verifier` | Combines must-haves verification with WARRIOR 70-point validation | Read, Write, Bash, Glob, Grep | `/fire-4-verify`, `/fire-3-execute` |
| `fire-reviewer` | Independent code reviewer -- architecture, patterns, performance, maintainability | Read, Glob, Grep, Bash (read-only) | `/fire-7-review`, `/fire-3-execute` (parallel with verifier) |
| `fire-codebase-mapper` | Maps architecture, dependencies, patterns, and concerns across a codebase | Read, Glob, Grep, Bash, Write | `/fire-map-codebase` |
| `fire-debugger` | Systematic hypothesis-driven debugging with evidence tracking | Read, Glob, Grep, Bash, Write, Edit | `/fire-debug`, `/fire-verify-uat` |
| `fire-fact-checker` | Adversarial verification agent that attempts to disprove research findings | Read, Glob, Grep, Bash, WebSearch, WebFetch, Write | `/fire-new-milestone` |
| `fire-project-researcher` | Researches a specific domain focus area for new project/milestone initialization | Read, Write, Glob, Grep, Bash, WebSearch, WebFetch | `/fire-new-milestone` |
| `fire-research-synthesizer` | Merges parallel research findings into a unified synthesis document | Read, Write, Glob, Grep | `/fire-new-milestone` |
| `fire-roadmapper` | Creates project roadmap with phase breakdown from research synthesis | Read, Write, Glob, Grep, Bash | `/fire-new-milestone` |
| `fire-learncoding-walker` | Maps dependency graph from entry point and produces ordered linear step list | Shell tools (grep, cat, sed) | `/fire-learncoding` |
| `fire-learncoding-explainer` | Per-step explainer that extracts real code snippets and explains WHAT/WHY/PATTERN | Shell tools (grep, cat, sed) | `/fire-learncoding` |

---

## Template Reference

| Template | Purpose | Created By |
|----------|---------|------------|
| `state.md` | Living project memory tracking | `/fire-1-new` |
| `roadmap.md` | Phase overview and milestones | `/fire-1-new` |
| `plan.md` | Detailed phase execution plan | `/fire-2-plan` |
| `fire-handoff.md` | Session continuity handoff | `/fire-5-handoff` |
| `verification.md` | Verification report format | `/fire-4-verify` |
| `skills-index.md` | Skills library index | `/fire-skills-sync` |

---

## Common Flags Reference

| Flag | Used With | Purpose |
|------|-----------|---------|
| `--auto-continue` | execute | Uninterrupted breath execution (Double-Shot Latte) |
| `--autonomous` | execute, loop | Auto-route gate verdicts without human checkpoints |
| `--breath N` | execute | Execute only a specific breath |
| `--continue` | execute, loop-resume | Resume from last checkpoint |
| `--skip-review` | execute | Skip parallel code review (not recommended) |
| `--skip-verify` | execute | Skip verification (not recommended) |
| `--max-iterations N` | loop | Safety limit for loop iterations |
| `--aggressive` | loop | Tighter circuit breaker thresholds |
| `--no-circuit-breaker` | loop | Disable circuit breaker (not recommended) |
| `--discover` | loop | Run pattern discovery before starting |
| `--dry-run` | skills-sync | Preview changes without applying |
| `--push` | skills-sync | Push project skills to global |
| `--pull` | skills-sync | Pull global skills to project |
| `--both` | skills-sync | Bidirectional sync |
| `--compact` | dashboard | Minimal output |
| `--watch` | dashboard | Auto-refresh display |
| `--json` | dashboard | JSON output format |
| `--category` | analytics | Group by category |
| `--time-saved` | analytics | Show time estimates |
| `--gaps` | analytics | Show skill gaps |
| `--e2e` | test | Full end-to-end tests |
| `--integration` | test | Integration tests only |
| `--command` | test | Test specific command |

---

*Dominion Flow v10.0.0 -- 42 commands, 13 agents, 190+ skills.*
