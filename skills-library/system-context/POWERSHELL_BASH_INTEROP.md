---
name: powershell-bash-interop
category: system-context
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [powershell, bash, windows, shell, interop, scripts]
difficulty: medium
---

# PowerShell & Bash Interop

## Problem

Claude Code's shell is bash (Git Bash on Windows), but some Windows operations require PowerShell (COM objects, system shortcuts, Windows APIs). Mixing syntax causes cryptic failures.

## Solution Pattern

Know which shell to use for what, and how to call one from the other.

## Shell Selection Guide

| Task | Use | Why |
|------|-----|-----|
| Git operations | Bash | Native git |
| npm/node commands | Bash | Works in both, bash is default |
| File operations (basic) | Bash | `cp`, `mv`, `rm` work fine |
| Desktop shortcuts | PowerShell | Requires COM objects |
| Windows services | PowerShell | `Get-Service`, `Start-Service` |
| Registry access | PowerShell | `Get-ItemProperty` |
| Environment variables (persistent) | PowerShell | `[Environment]::SetEnvironmentVariable` |
| Docker | Bash | CLI is the same everywhere |
| `curl` / `wget` | Bash | PowerShell's `curl` is aliased to `Invoke-WebRequest` |

## Calling PowerShell from Bash

```bash
# One-liner
powershell.exe -Command "Get-Process | Where-Object {$_.ProcessName -eq 'node'}"

# Multi-line script
powershell.exe -Command "
\$desktop = [Environment]::GetFolderPath('Desktop')
\$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut(\"\$desktop\\MyApp.lnk\")
\$shortcut.TargetPath = 'C:\\path\\to\\my-app\\start.bat'
\$shortcut.Save()
"
```

**Key escaping rules in bash → PowerShell:**
- `$` must be escaped as `\$` (bash would expand it otherwise)
- Use single quotes inside PowerShell where possible
- Backslashes in paths must be doubled or use forward slashes

## Calling Bash from PowerShell

```powershell
# Run a bash command
bash -c "git status"

# Run a bash script
bash -c "cd /c/path/to/my-project && npm test"
```

## Common Pitfalls

1. **`curl` in PowerShell** — It's actually `Invoke-WebRequest`, not `curl`. Use bash for real `curl`.
2. **Path separators** — PowerShell uses `\`, bash uses `/`. Both work in most tools on Windows.
3. **Exit codes** — PowerShell `$LASTEXITCODE` vs bash `$?`. They don't bridge cleanly.
4. **`rm`** — In PowerShell it's `Remove-Item`. In bash it's GNU `rm`. Different flags.

## When to Use

- Creating desktop shortcuts (New Application Init Checklist)
- Managing Windows services
- Any task requiring Windows-specific APIs
- Debugging shell-related failures

## When NOT to Use

- Standard dev operations (git, npm, docker) — just use bash
- Linux/Mac environments
