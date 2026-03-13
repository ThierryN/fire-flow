---
name: toolbox
description: Complete reference of available tools, plugins, marketplaces, and workflow commands
user-invocable: false
---

# Available Tools & Resources Reference

**Full reference file:** `C:\Users\FirstName\.claude\plugins\warrior-workflow\skills-library\AVAILABLE_TOOLS_REFERENCE.md`

## Plugin Marketplaces (16 Total)

| Category | Marketplaces |
|----------|-------------|
| **Official** | claude-plugins-official, superpowers-marketplace, anthropic-agent-skills |
| **Workflows** | claude-code-workflows (107 skills), claude-code-plugins-plus, compounding-engineering |
| **Specialized** | n8n-mcp (1,084 nodes), n8n-skills, ralph-wiggum (autonomous loops), hcp-terraform-skills |
| **Community** | awesome-claude-code-plugins, awesome-claude-skills, cc-marketplace, mag-claude-plugins, thedotmack |

## Dominion Flow System

**Location:** `~/.claude/plugins/dominion-flow/` | **Version:** 3.2.0

| Command | Purpose |
|---------|---------|
| `/fire-dashboard` | Project status & progress |
| `/fire-1a-new` | Initialize new project |
| `/fire-2-plan N` | Create phase plan |
| `/fire-3-execute N` | Breath-based parallel execution |
| `/fire-4-verify` | Goal-backward verification |
| `/fire-5-handoff` | Create session handoff |
| `/fire-6-resume` | Resume from handoff |
| `/fire-debug` | Systematic debugging |
| `/fire-loop` | Self-iterating autonomous loop |

**Key Concepts:** CONSCIENCE.md (living memory), Breath-based execution, Must-haves verification, Checkpoints

## Ralph Wiggum Loops

Self-iterating autonomous loops until success criteria met:
```bash
/ralph-loop "Build X with tests. Output DONE when all tests pass." --completion-promise "DONE" --max-iterations 50
```

## Installed Official Plugins

| Category | Plugins |
|----------|---------|
| **Productivity** | playwright, github, gitlab, greptile |
| **Integrations** | figma, sentry, vercel, firebase, stripe, supabase, context7 |
| **Project Mgmt** | atlassian, asana, linear, slack |
| **Development** | hookify, plugin-dev, agent-sdk-dev, frontend-design, code-review, feature-dev, pr-review-toolkit, commit-commands |

## Key Superpowers Skills

Use the `Skill` tool to invoke:
- `superpowers:brainstorming` - Before ANY creative work
- `superpowers:test-driven-development` - When implementing features
- `superpowers:systematic-debugging` - For bug investigation
- `superpowers:verification-before-completion` - Before claiming done
- `superpowers:requesting-code-review` - After completing tasks

## WARRIOR Workflow

| Command | Purpose |
|---------|---------|
| `/warrior-handoff` | Create comprehensive handoff |
| `/warrior-review` | Conduct code review |
| `/warrior-validation` | Verify work complete |

**Skills Library:** `~/.claude/plugins/warrior-workflow/skills-library/`
- methodology/, complexity-metrics/, ecommerce/, integrations/
- video-media/, deployment-security/, database-solutions/, form-solutions/
- advanced-features/, automation/, document-processing/, patterns-standards/

## Swarm Mode (Agent Teams) - ENABLED

Multi-agent swarm mode is enabled globally (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`).

**How to trigger:** User asks for a team, e.g., "Use a team of specialists for this."

**Controls:** `Shift+Up/Down` (select teammate), `Enter` (view session), `Ctrl+T` (task list), `Shift+Tab` (delegate-only mode)

**Skill Reference:** `~/.claude/plugins/warrior-workflow/skills-library/automation/CLAUDE_CODE_SWARM_MODE.md`
