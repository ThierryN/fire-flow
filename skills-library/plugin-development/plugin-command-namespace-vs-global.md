---
name: plugin-command-namespace-vs-global
category: plugin-development
version: 1.0.0
contributed: 2026-01-23
contributor: my-other-project
last_updated: 2026-01-23
contributors:
  - my-other-project
tags: [claude-code, plugins, commands, slash-commands, vscode, troubleshooting]
difficulty: medium
usage_count: 1
success_rate: 100
---

# Plugin Command Namespace vs Global Registration

## Problem

Custom Claude Code plugin commands are not appearing in VS Code's command palette (`Ctrl+Shift+P`) or in slash command autocomplete, despite:
- Being properly created in the plugin's `commands/` directory
- Having valid YAML frontmatter (description field)
- Plugin being installed and activated
- Other commands from the same plugin working fine

**Symptoms:**
- User types `/command-name` → Command not found
- Command palette search for "command-name" → No results
- VS Code restarts don't help
- Cache sync doesn't help
- Line ending conversions don't help

**Common scenario:** Developer adds new commands to existing plugin, old commands work but new ones are invisible.

## Root Cause

Claude Code has **two distinct command registration locations** with different namespace behaviors:

### 1. Global Commands Directory
**Location:** `~/.claude/commands/` (Windows: `C:\Users\{user}\.claude\commands\`)

**Behavior:** Commands work **without namespace prefix**
- Registration: Automatic on startup
- Access: `/command-name` ✅
- Scope: Available in all projects
- Priority: Takes precedence over plugin commands

### 2. Plugin Commands Directory
**Location:** `~/.claude/plugins/{plugin-name}/commands/`

**Behavior:** Commands require **namespace prefix**
- Registration: Automatic on plugin load
- Access: `/{plugin-name}:command-name` ✅
- Access: `/command-name` ❌ (fails silently)
- Scope: Only when plugin is loaded
- Purpose: Namespace isolation to prevent conflicts

## Solution Pattern

### Quick Fix: Copy to Global Directory

**For commands you want to use without namespace:**

```bash
# Copy command from plugin to global
cp ~/.claude/plugins/{plugin-name}/commands/{command}.md ~/.claude/commands/

# Restart VS Code
# Command now works without prefix
```

**Example:**
```bash
# Before: Only works with namespace
/dominion-flow:power-debug ✅
/fire-debug ❌

# Copy to global
cp ~/.claude/plugins/dominion-flow/commands/fire-debug.md ~/.claude/commands/

# After restart: Works without namespace
/fire-debug ✅
```

### When to Keep in Plugin (Use Namespace)

Keep commands in plugin directory when:
- Command is plugin-specific functionality
- You want to avoid naming conflicts
- Team convention requires namespacing
- Plugin may be uninstalled (commands should disappear with it)

### Migration Strategy for Multiple Commands

```bash
# Copy all commands from plugin to global
cd ~/.claude/plugins/{plugin-name}/commands
cp *.md ~/.claude/commands/

# Verify copy
ls ~/.claude/commands | grep "{command-prefix}"

# Restart VS Code
```

**Windows PowerShell:**
```powershell
# Copy all
Copy-Item "C:\Users\$env:USERNAME\.claude\plugins\{plugin-name}\commands\*.md" `
          "C:\Users\$env:USERNAME\.claude\commands\"

# Verify
dir "C:\Users\$env:USERNAME\.claude\commands" | findstr "{prefix}"
```

## Code Example

### Before (Plugin Directory Only)

**Plugin structure:**
```
~/.claude/plugins/dominion-flow/
├── commands/
│   ├── power-0-orient.md      # ❌ Requires /dominion-flow: prefix
│   ├── power-debug.md          # ❌ Requires /dominion-flow: prefix
│   └── power-todos.md          # ❌ Requires /dominion-flow: prefix
└── .claude-plugin/
    └── plugin.json
```

**User experience:**
```bash
# Fails silently
/fire-debug
# Command not found

# Requires namespace
/dominion-flow:power-debug
# ✅ Works but verbose
```

### After (Global Directory)

**Directory structure:**
```
~/.claude/commands/
├── power-0-orient.md   # ✅ Works without prefix
├── power-debug.md       # ✅ Works without prefix
├── power-todos.md       # ✅ Works without prefix
├── power-1-new.md      # (existing, was already global)
└── power-dashboard.md  # (existing, was already global)

~/.claude/plugins/dominion-flow/
└── commands/
    ├── power-0-orient.md   # Still here (source of truth)
    ├── power-debug.md       # Still here
    └── power-todos.md       # Still here
```

**User experience:**
```bash
# Now works without namespace
/fire-debug
# ✅ Direct access

# Namespace still works (plugin copy)
/dominion-flow:power-debug
# ✅ Also works
```

## Implementation Steps

### Step 1: Verify Command Locations

```bash
# Check if commands exist in plugin
ls ~/.claude/plugins/{plugin-name}/commands/ | grep {command-name}

# Check if already in global
ls ~/.claude/commands/ | grep {command-name}
```

### Step 2: Copy Commands

**Single command:**
```bash
cp ~/.claude/plugins/{plugin}/commands/{command}.md ~/.claude/commands/
```

**All commands:**
```bash
cp ~/.claude/plugins/{plugin}/commands/*.md ~/.claude/commands/
```

### Step 3: Verify Files Copied

```bash
# List all commands in global directory
ls -lh ~/.claude/commands/*.md

# Count commands
ls ~/.claude/commands/*.md | wc -l
```

### Step 4: Restart VS Code

**Complete shutdown required** (not just reload window):
1. Close all VS Code windows
2. Wait 5 seconds
3. Reopen VS Code

### Step 5: Test Commands

**Command Palette Test:**
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type command name (e.g., "power-debug")
3. Verify command appears ✅

**Slash Command Test:**
1. Open Claude Code chat
2. Type `/` to trigger autocomplete
3. Verify command appears in list ✅
4. Type command without namespace and execute ✅

## When to Use

### Use this skill when:
- ✅ Plugin commands don't appear without namespace prefix
- ✅ Command palette search finds nothing for your command
- ✅ Typing `/command` shows "command not found"
- ✅ Other commands from same plugin work fine (inconsistent behavior)
- ✅ You want plugin commands to work like built-in commands
- ✅ Team prefers no namespace prefixes
- ✅ Commands are general-purpose utilities (not plugin-specific)

### Investigate other causes first if:
- Command files have YAML frontmatter errors (invalid fields)
- Plugin is not installed (`/plugin list` to verify)
- File permissions are wrong (can't read command files)
- Command file is in wrong location (not in `commands/` subdirectory)

## When NOT to Use

### Don't copy to global when:
- ❌ You want to enforce plugin namespace (team policy)
- ❌ Command names conflict with other plugins
- ❌ Commands are tightly coupled to plugin functionality
- ❌ Plugin may be uninstalled (commands should go with it)
- ❌ Working with temporary/experimental commands
- ❌ Multiple plugins define same command name (namespace prevents collision)

### Alternative: Use Namespace Prefix

If copying to global isn't appropriate, document the namespace requirement:

```bash
# Instead of /command, use:
/{plugin-name}:command

# Example:
/dominion-flow:power-debug
```

## Common Mistakes

### Mistake 1: Not Restarting VS Code
**Problem:** Copied files but commands still don't appear

**Solution:** VS Code loads commands on startup. **Full restart required** (close all windows, reopen).

### Mistake 2: Copying with Wrong Extension
**Problem:**
```bash
cp command.md ~/.claude/commands/command.txt  # ❌ Wrong
```

**Solution:** Preserve `.md` extension:
```bash
cp command.md ~/.claude/commands/command.md  # ✅ Correct
```

### Mistake 3: Forgetting to Update Global When Plugin Updates
**Problem:** Plugin command gets updated in plugin directory, but global copy is stale.

**Solution:**
- Document where source of truth is
- Re-copy when plugin commands change
- Or maintain only in global directory

### Mistake 4: Assuming Cache Fix Will Work
**Problem:** Trying to copy to cache directory instead of global

**Cache location:** `~/.claude/plugins/cache/local/{plugin}/{version}/commands/`

**This won't help** - cache mirrors plugin structure, still requires namespace.

**Correct location:** `~/.claude/commands/` (global, no cache involved)

### Mistake 5: Deleting Plugin Commands After Copy
**Problem:** Deleting plugin copy breaks `/plugin-name:command` access

**Better approach:** Keep both:
- Plugin directory: Source of truth for updates
- Global directory: Copy for namespace-free access

## Verification Checklist

After copying commands, verify:

- [ ] Files exist in `~/.claude/commands/` with `.md` extension
- [ ] File contents are valid (description in YAML frontmatter)
- [ ] VS Code fully restarted (all windows closed and reopened)
- [ ] Command appears in command palette (`Ctrl+Shift+P`)
- [ ] Command appears in slash autocomplete (`/` in chat)
- [ ] Command executes without namespace prefix
- [ ] No error messages in VS Code developer console (`Ctrl+Shift+I`)

## Troubleshooting

### Commands still don't appear after copying

1. **Check file permissions:**
   ```bash
   ls -l ~/.claude/commands/{command}.md
   # Should be readable (r-- or rw-)
   ```

2. **Check YAML frontmatter:**
   ```bash
   head -5 ~/.claude/commands/{command}.md
   # Should have valid YAML:
   # ---
   # description: Command description
   # ---
   ```

3. **Check VS Code developer console:**
   - Open: `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Opt+I` (Mac)
   - Look for errors mentioning command loading

4. **Verify Claude Code extension is active:**
   - Extensions panel: Search "Claude"
   - Should show "Claude Code" as enabled

### Namespace version works but global doesn't

**This is expected behavior** - means:
- ✅ Command file is valid (works with namespace)
- ✅ Plugin is loaded correctly
- ❌ Global copy either doesn't exist or wasn't loaded

**Solution:** Re-verify global copy exists and restart VS Code completely.

## Related Skills

- [CLAUDE_CODE_COMMAND_REGISTRATION_SILENT_FAILURE](./CLAUDE_CODE_COMMAND_REGISTRATION_SILENT_FAILURE.md) - YAML frontmatter validation
- [Plugin development patterns](./plugin-structure-patterns.md) - Overall plugin architecture (if exists)
- Command caching behavior - Understanding when commands reload (if exists)

## Documentation References

- [Claude Code Plugin Structure](https://platform.claude.com/docs/en/agent-sdk/plugins#plugin-structure-reference)
- [Slash Commands in SDK](https://platform.claude.com/docs/en/agent-sdk/slash-commands)
- [Creating Custom Commands](https://code.claude.com/docs/en/slash-commands)

## Real-World Example

**Scenario:** User added 7 new commands to `dominion-flow` plugin but they didn't appear.

**Investigation attempts:**
1. ❌ Synced plugin cache directory → No effect
2. ❌ Fixed line endings (CRLF→LF) → No effect
3. ❌ Removed invalid YAML fields → No effect (fields were valid)
4. ❌ Version alignment → No effect

**Root cause identified:** Commands in plugin required `/dominion-flow:` prefix, but user's existing commands worked without prefix because they were in global directory.

**Solution:** Copied 7 commands from plugin to global:
```bash
cp ~/.claude/plugins/dominion-flow/commands/fire-{0-orient,1a-discuss,debug,complete-milestone,map-codebase,new-milestone,todos}.md ~/.claude/commands/
```

**Result:** All commands now work without namespace prefix after VS Code restart.

**Time to resolution:** 3 hours (multiple false leads)
**Time with this skill:** 10 minutes (direct to solution)

---

**Key Insight:** Plugin commands are namespaced by design. To use them without namespace, copy to global directory.
