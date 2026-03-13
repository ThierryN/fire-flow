# Claude Code Swarm Mode (Agent Teams)

**Category:** Automation / Multi-Agent Orchestration
**Date Added:** 2026-02-07
**Status:** Active - Globally Enabled

---

## Overview

Claude Code Swarm Mode transforms Claude from a single AI coder into a **Team Lead** that spawns specialist agents working in parallel. Enabled globally via environment variable.

## Configuration

**Location:** `C:\Users\FirstName\.claude\settings.json`

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## How It Works

1. **Team Lead** receives the task and creates a plan
2. Lead **spawns specialist teammates** (e.g., backend, frontend, testing)
3. Teammates work **in parallel** on their assigned subtasks
4. Lead **coordinates** and merges results
5. Inbox-based messaging enables direct agent-to-agent communication

## Usage Patterns

### Basic Team Request
```
"Build the user dashboard. Use a team — one for API endpoints, one for React components, one for tests."
```

### Research Team
```
"Explore this codebase from multiple angles with a team of specialists."
```

### Debugging Team
```
"Debug this auth issue. Have one agent trace the frontend flow, one the backend, and one check the database."
```

## Key Controls

| Shortcut | Action |
|----------|--------|
| `Shift+Up/Down` | Select & message specific teammates |
| `Enter` | View a teammate's session |
| `Escape` | Interrupt a teammate |
| `Ctrl+T` | Toggle task list |
| `Shift+Tab` | Delegate-only mode (lead plans, doesn't code) |

## Display Modes

| Mode | Config | Requirements |
|------|--------|-------------|
| **In-process** (default) | No config needed | None |
| **tmux split panes** | `"teammateMode": "tmux"` | tmux via WSL |
| **iTerm2 panes** | `"teammateMode": "iterm2"` | macOS only |

## When to Use Swarm Mode

- Multi-file feature implementation
- Codebase exploration from multiple angles
- Parallel debugging (frontend + backend + database)
- Full-stack development (API + UI + tests simultaneously)
- Large refactoring across many files

## When NOT to Use

- Simple single-file edits
- Quick bug fixes
- Conversational questions
- Tasks with heavy sequential dependencies

## Relationship to Existing Parallel Patterns

This is **complementary** to the existing parallel agent patterns:
- **Task tool subagents** — still work for programmatic agent spawning
- **Swarm mode** — higher-level orchestration with Team Lead coordination
- **breath execution** — plan-based parallel execution
- The 3-agent debugging pattern in CLAUDE.md still applies

## References

- [Claude Code Agent Teams - Addy Osmani](https://addyosmani.com/blog/claude-code-agent-teams/)
- [Claude Code Swarm Feature - Cyrus](https://www.atcyrus.com/stories/what-is-claude-code-swarm-feature)
- [Claude Code Swarms - Zen van Riel](https://zenvanriel.nl/ai-engineer-blog/claude-code-swarms-multi-agent-orchestration/)
