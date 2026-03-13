# Claude Code Command Registration Silent Failure - YAML Frontmatter Fields

## The Problem

New Claude Code plugin commands were not appearing in VS Code's command palette or the Claude Code chat slash command autocomplete, despite being properly created and placed in the plugin's `commands/` directory.

### Error Behavior
- **No error messages** - Commands silently failed to register
- Existing/older commands worked perfectly
- Commands were present in both source and cache directories
- VS Code restarts didn't help
- Line ending conversions didn't help

### Why It Was Hard

1. **Silent failure** - No errors, warnings, or logs to indicate what was wrong
2. **Multiple false leads** - Cache sync issues and line endings seemed plausible but weren't the cause
3. **Working examples existed** - Some commands worked, making it hard to identify the difference
4. **Required deep comparison** - Had to compare working vs non-working files field-by-field
5. **Plugin system documentation gaps** - Not clearly documented which YAML fields are valid

### Impact

- 7 new commands completely invisible to users
- Hours of debugging time across multiple attempts
- Confusion about whether commands were installed correctly
- User productivity blocked

---

## The Solution

### Root Cause

Claude Code's command parser **only accepts specific YAML frontmatter fields**. The parser silently rejects (doesn't register) any command file containing **invalid or unrecognized fields**.

**Valid fields:**
```yaml
---
name: command-name          # Optional
description: Command description here  # Required
---
```

**Invalid field that breaks everything:**
```yaml
---
description: Command description here
argument-hint: "[phase]"    # ❌ THIS CAUSES SILENT FAILURE
---
```

### The Pattern

**Working command (power-dashboard.md):**
```yaml
---
description: Display visual project dashboard with status and progress
---

# Content here...
```

**Non-working command (power-0-orient.md):**
```yaml
---
description: Orient yourself to the project and get a situational brief
argument-hint: "[optional-context]"  # ❌ BREAKS REGISTRATION
---

# Content here...
```

**The `argument-hint` field caused 100% registration failure** across all 7 commands that had it.

### How to Fix

**Step 1: Remove invalid fields from source**

```bash
cd C:\Users\FirstName\.claude\plugins\dominion-flow\commands\

# Edit each affected command file
# Remove any fields besides 'name' and 'description' from YAML frontmatter
```

**Before:**
```yaml
---
description: Debug issues using scientific method
argument-hint: "[issue-description]"
---
```

**After:**
```yaml
---
description: Debug issues using scientific method
---
```

**Step 2: Sync to cache directory**

```bash
# Copy updated files to cache
cp power-0-orient.md C:\Users\FirstName\.claude\plugins\cache\local\dominion-flow\1.0.0\commands\
cp power-1a-discuss.md C:\Users\FirstName\.claude\plugins\cache\local\dominion-flow\1.0.0\commands\
# ... (repeat for all affected commands)
```

**Step 3: Restart VS Code**

- Completely restart VS Code (not just reload window)
- Claude Code extension will reload plugin commands on startup

### Code Example

**Complete working command file structure:**

```markdown
---
description: Complete command description that appears in command palette
---

# /command-name

## Purpose
[What this command does]

## Process
[How it works]

## Success Criteria
[What success looks like]
```

---

## Testing the Fix

### Before Fix
```bash
# Search command palette (Ctrl+Shift+P)
"power-0-orient"  # ❌ Not found

# Slash command autocomplete
/fire-0-orient   # ❌ Not found
```

### After Fix
```bash
# Search command palette (Ctrl+Shift+P)
"power-0-orient"  # ✅ Appears with description

# Slash command autocomplete
/fire-0-orient   # ✅ Appears in list
```

### Verification Checklist

After fix and VS Code restart:

- [ ] Open command palette (`Ctrl+Shift+P`)
- [ ] Search for command name (e.g., "power-0-orient")
- [ ] Verify command appears with correct description
- [ ] Open Claude Code chat interface
- [ ] Type `/` to trigger autocomplete
- [ ] Verify command appears in slash command list
- [ ] Execute command to verify it works
- [ ] Repeat for all previously non-working commands

---

## Prevention

### Command Creation Guidelines

**When creating new Claude Code plugin commands:**

1. **Only use these YAML frontmatter fields:**
   ```yaml
   ---
   description: Your description here  # Required
   name: command-name                  # Optional (defaults to filename)
   ---
   ```

2. **DO NOT add custom fields** like:
   - `argument-hint`
   - `arguments`
   - `usage`
   - `examples`
   - Any other custom metadata

3. **Put argument documentation in markdown**, not frontmatter:
   ```markdown
   ---
   description: Debug issues systematically
   ---

   # /fire-debug

   ## Arguments

   ```yaml
   arguments: optional
   usage: /fire-debug [issue-description]
   ```
   ```

4. **Test immediately after creating** - Don't create multiple commands before testing

5. **Compare with working examples** - When in doubt, copy a working command's structure

### Cache Sync Strategy

**When developing plugins locally:**

- Changes to source require manual cache sync
- Cache location: `~/.claude/plugins/cache/local/{plugin-name}/{version}/`
- Always copy to cache AND restart VS Code after changes

**Alternative:** Use whatever plugin refresh/reload mechanism Claude Code provides (if available)

---

## Related Patterns

- Plugin development best practices
- YAML frontmatter validation
- Claude Code plugin architecture

---

## Common Mistakes to Avoid

- ❌ **Adding helpful custom fields** - Breaks registration silently
- ❌ **Assuming more metadata is better** - Parser rejects extras
- ❌ **Not testing after each command** - Hard to debug multiple at once
- ❌ **Forgetting cache sync** - Source changes won't appear
- ❌ **Skipping VS Code restart** - Extension needs full reload

---

## Resources

- Claude Code Plugin Documentation: (check official docs for latest)
- Working command examples: Check existing commands in dominion-flow or other plugins
- Plugin development guide: (reference official guides)

---

## Time to Implement

**To fix existing commands:** 10-15 minutes
- 5 minutes to remove invalid fields from all affected files
- 5 minutes to sync to cache
- 1 minute to restart VS Code
- 2 minutes to verify all commands appear

**To prevent in new commands:** 30 seconds per command
- Just use the correct YAML structure from the start

---

## Difficulty Level

⭐⭐⭐⭐ (4/5) - **Very Hard to Debug (Easy to Fix Once Known)**

**Why 4 stars for debugging:**
- Silent failure with zero error messages
- Multiple plausible false leads (cache, line endings)
- Requires field-by-field comparison of working vs non-working files
- Plugin system internals not well-documented

**Why easy to fix:**
- Once identified, it's a simple field removal
- Clear pattern: valid fields only

---

## Author Notes

This took **3 hours and 2 failed fix attempts** to identify:
1. First attempt: Synced cache directory (logical but wrong)
2. Second attempt: Converted CRLF to LF line endings (seemed plausible but wrong)
3. Third attempt: Compared YAML frontmatter field-by-field (found it!)

**The key insight:** When commands silently fail to register, **suspect invalid YAML frontmatter fields first**.

**Pattern recognition:** 100% correlation between `argument-hint` field presence and registration failure across all 7 commands.

**Lesson learned:** For plugin systems with parsers, **less is more** - stick to documented fields only, even if custom fields seem harmless.

---

## Affected Commands (Historical Reference)

The following 7 commands were affected by this issue:
1. `/fire-0-orient`
2. `/fire-1a-discuss`
3. `/fire-debug`
4. `/fire-complete-milestone`
5. `/fire-map-codebase`
6. `/fire-new-milestone`
7. `/fire-todos`

All were fixed by removing the `argument-hint` field from their YAML frontmatter.

---

**Created:** 2026-01-23
**Plugin:** dominion-flow (version 1.3.0)
**Problem Solved:** Silent command registration failure
**Status:** ✅ Verified fix works across all 7 commands
