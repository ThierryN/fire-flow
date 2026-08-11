---
name: claude-code-plugin-structure
category: patterns-standards
version: 1.0.0
contributed: 2026-01-23
contributor: dominion-flow-debugging-session
last_updated: 2026-01-23
contributors:
  - Author
  - Claude-Opus-4.5
tags: [claude-code, plugin, commands, agents, skills, yaml, frontmatter, local-plugin]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Claude Code Plugin Structure

## Problem

Local Claude Code plugin not loading correctly. Symptoms include:
- Plugin shows as enabled in `settings.json` but commands don't appear
- `/plugin-name:command` syntax doesn't work
- Plugin visible in settings but not functional
- Commands work when copied to `~/.claude/commands/` but not from plugin

## Solution Pattern

Claude Code plugins require a **specific directory structure** with **YAML frontmatter** on all component files. The most common issues are:

1. **plugin.json in wrong location** - Must be at `.claude-plugin/plugin.json`, NOT at plugin root
2. **Missing YAML frontmatter** - Commands and agents require frontmatter with specific fields
3. **Wrong frontmatter fields** - Commands need `description`, agents need `name` and `description`

## Directory Structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # REQUIRED - Must be here, NOT at root
├── commands/                 # Slash commands (*.md files)
│   └── my-command.md
├── agents/                   # Agent definitions (*.md files)
│   └── my-agent.md
├── skills/                   # Skills (directories with SKILL.md)
│   └── my-skill/
│       └── SKILL.md
├── hooks/                    # Event handlers
│   └── hooks.json
└── .mcp.json                # MCP server definitions (optional)
```

## Code Example

### plugin.json (Minimal Required)

```json
// WRONG - at root level: my-plugin/plugin.json
// CORRECT - in .claude-plugin/: my-plugin/.claude-plugin/plugin.json

{
  "name": "my-plugin"
}
```

### plugin.json (Recommended)

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Brief description of what plugin does",
  "author": {
    "name": "Your Name",
    "email": "email@example.com"
  },
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"]
}
```

### Command File (commands/*.md)

```markdown
---
description: Brief description of what this command does
---

# Command Name

[Instructions for Claude to follow when command is invoked]
```

### Agent File (agents/*.md)

```markdown
---
name: agent-name
description: Description of agent's purpose and when to use it
---

# Agent Name

[System prompt and instructions for the agent]
```

### Skill File (skills/*/SKILL.md)

```markdown
---
name: skill-name
description: What the skill does and when Claude should use it
---

# Skill Name

## Instructions
[Step-by-step guidance]

## Examples
[Usage examples]
```

## Implementation Steps

1. **Create directory structure**
   ```bash
   mkdir -p my-plugin/.claude-plugin
   mkdir -p my-plugin/commands
   mkdir -p my-plugin/agents
   ```

2. **Create plugin.json in correct location**
   ```bash
   # CORRECT
   echo '{"name": "my-plugin"}' > my-plugin/.claude-plugin/plugin.json

   # WRONG - do NOT put at root
   # echo '{"name": "my-plugin"}' > my-plugin/plugin.json
   ```

3. **Add YAML frontmatter to all commands**
   - Every `.md` file in `commands/` needs `---\ndescription: ...\n---`

4. **Add YAML frontmatter to all agents**
   - Every `.md` file in `agents/` needs `---\nname: ...\ndescription: ...\n---`

5. **Enable plugin in settings.json**
   ```json
   {
     "enabledPlugins": {
       "my-plugin@local": true
     }
   }
   ```

6. **Restart Claude Code** to load the plugin

## When to Use

- Creating a new local Claude Code plugin
- Debugging why a plugin isn't loading
- Converting loose commands into a proper plugin structure
- Sharing plugin with others who report it doesn't work
- Plugin commands don't appear after enabling

## When NOT to Use

- For global commands (use `~/.claude/commands/` directly)
- For simple one-off commands that don't need plugin packaging
- When using marketplace plugins (they're already structured correctly)

## Common Mistakes

1. **plugin.json at root level**
   - WRONG: `my-plugin/plugin.json`
   - CORRECT: `my-plugin/.claude-plugin/plugin.json`

2. **Missing frontmatter on commands**
   - WRONG: Start with `# Command Name`
   - CORRECT: Start with `---\ndescription: ...\n---`

3. **Using `capabilities` object in plugin.json**
   - This is non-standard; stick to basic metadata fields
   - Auto-discovery handles finding commands/agents/skills

4. **Copying `plugin.json` to root AND `.claude-plugin/`**
   - Only need it in `.claude-plugin/`
   - Root-level `plugin.json` is ignored

5. **Wrong frontmatter fields for agents**
   - Commands: only need `description`
   - Agents: need both `name` AND `description`

## Debugging Checklist

```bash
# 1. Check plugin.json location
ls my-plugin/.claude-plugin/plugin.json  # Should exist

# 2. Check frontmatter on commands
head -5 my-plugin/commands/*.md  # Should show --- at line 1

# 3. Check plugin is enabled
grep "my-plugin" ~/.claude/settings.json  # Should show true

# 4. Compare with working plugin
ls ~/.claude/plugins/warrior-workflow/  # Reference structure
```

## Related Skills

- [AVAILABLE_TOOLS_REFERENCE](../AVAILABLE_TOOLS_REFERENCE.md) - Full tools reference
- [Plugin System Architecture](../advanced-features/PLUGIN_SYSTEM_ARCHITECTURE.md) - MERN plugin patterns

## References

- [Official Plugin Structure](https://github.com/anthropics/claude-plugins-official) - GitHub reference
- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) - Official docs
- [SDK Plugins Reference](https://platform.claude.com/docs/en/agent-sdk/plugins) - Technical specs
- [Claude Code Plugins Docs](https://code.claude.com/docs/en/plugins) - Full documentation

## Field Requirements Summary

| Component | Required Fields | Notes |
|-----------|-----------------|-------|
| plugin.json | `name` | Must be in `.claude-plugin/` |
| commands/*.md | `description` | YAML frontmatter |
| agents/*.md | `name`, `description` | YAML frontmatter |
| skills/*/SKILL.md | `name`, `description` | Max 64/1024 chars |

---

*Contributed from: dominion-flow plugin debugging session (2026-01-23)*
*Root cause: plugin.json location + missing YAML frontmatter*
