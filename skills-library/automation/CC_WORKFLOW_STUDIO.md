# CC Workflow Studio - Visual Agent Workflow Designer

**Category:** Automation / Agent Workflow Design
**Date Added:** 2026-02-13
**Status:** Active - Installed as VS Code Extension
**Version:** v3.21.0
**Source:** https://github.com/breaking-brake/cc-wf-studio
**License:** AGPL-3.0

---

## Overview

CC Workflow Studio is a VS Code extension that provides a **visual drag-and-drop editor** for designing Claude Code agent workflows. Instead of hand-writing agent markdown files, you design workflows visually and export them directly to `.claude/agents/` and `.claude/commands/`.

## Installation

Already installed globally as VS Code extension `breaking-brake.cc-wf-studio`.

```powershell
# Verify installation
code --list-extensions | Select-String "cc-wf-studio"

# Reinstall if needed
code --install-extension breaking-brake.cc-wf-studio
```

## How to Launch

1. **VS Code icon** - Click CC Workflow Studio icon in top-right toolbar
2. **Command Palette** - `Ctrl+Shift+P` -> "CC Workflow Studio: Open Editor"

## Key Features

| Feature | Description |
|---------|-------------|
| **Visual Canvas** | Drag-and-drop nodes (agents, conditions, tools) to design workflows |
| **Edit with AI** | Describe changes in natural language, AI modifies the workflow |
| **One-Click Export** | Export to `.claude/agents/`, `.claude/commands/`, or other formats |
| **Run from Editor** | Execute workflows directly without leaving the editor |
| **MCP Server** | Built-in MCP server activates during "Edit with AI" sessions |
| **Save/Load** | Workflows saved as `.json` files for reuse and sharing |

## Export Targets

| Format | Output Path | Use Case |
|--------|-------------|----------|
| Claude Code Agents | `.claude/agents/` | Sub-agent orchestration |
| Claude Code Commands | `.claude/commands/` | Slash commands |
| GitHub Copilot | `.github/prompts/` | Copilot custom prompts |
| GitHub Skills | `.github/skills/` | GitHub agent skills |

## When to Use

- **Building complex multi-agent workflows** with branching logic
- **Designing sub-agent orchestrations** visually before implementing
- **Iterating on agent designs** using natural language ("add error handling", "add a research step")
- **Exporting ready-to-use** `.claude/agents/` files for Claude Code CLI
- **Prototyping** workflow ideas before committing to code

## Workflow Design Tips

1. Start with "Edit with AI" to generate a base workflow from description
2. Fine-tune node connections and conditions on the visual canvas
3. Test with "Run" before exporting
4. Export to your project's `.claude/` directory
5. Test the exported agent/command with Claude Code CLI

## Integration with Swarm Mode

CC Workflow Studio complements Swarm Mode (see `CLAUDE_CODE_SWARM_MODE.md`):
- **Studio** = Design phase (visual planning of agent workflows)
- **Swarm** = Runtime phase (actual multi-agent execution)
- Design your team structure in Studio, then trigger it via Swarm Mode

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Extension not showing | Restart VS Code, check Extensions panel |
| MCP server not connecting | Restart the "Edit with AI" session |
| Export path wrong | Check project root is open in VS Code |
| Workflow not running | Verify Claude Code CLI is accessible in PATH |
