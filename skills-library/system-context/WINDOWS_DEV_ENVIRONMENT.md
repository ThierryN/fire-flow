---
name: windows-dev-environment
category: system-context
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [windows, development, environment, xampp, node, python, paths]
difficulty: easy
---

# Windows Dev Environment Patterns

## Problem

Windows dev environments juggle multiple runtimes (Node, Python, PHP/XAMPP), services (Docker, Qdrant, Ollama, Neo4j), and path conventions (backslash vs forward slash). Agents frequently trip on path separators, missing executables, and port conflicts.

## Solution Pattern

Standardize environment assumptions and provide quick diagnostics.

## Path Conventions

```javascript
// ALWAYS use forward slashes in code — Node/Git Bash handle them fine on Windows
const repoPath = 'C:/path/to/repos/my-project'

// NEVER hardcode backslashes in strings
const bad = 'C:\\path\\to\\my-project'  // Escape hell

// For path joining, use path.join() — it handles the OS separator
const fullPath = path.join(process.cwd(), 'src', 'index.ts')
```

## Runtime Locations (This System)

| Runtime | Path | Port |
|---------|------|------|
| Node.js | System PATH | — |
| Python 3.12 | `C:\Users\FirstName\AppData\Local\Programs\Python\Python312\` | — |
| XAMPP MySQL | `C:\xampp\mysql\bin\` | 3306 |
| XAMPP Apache | `C:\xampp\apache\bin\` | 80/443 |
| Qdrant (native) | `C:\path\to\qdrant\qdrant.exe` | 6335 |
| Qdrant (Docker) | Docker container | 6333 |
| Neo4j (Docker) | Container `neo4j-cgc` | 7474/7687 |
| Ollama | System PATH | 11434 |

## Port Conflict Resolution

```bash
# Find what's using a port
netstat -ano | findstr :5001

# Kill by PID (from the last column of netstat output)
taskkill /PID 12345 /F
```

## Common Gotchas

1. **XAMPP MySQL vs Docker MySQL** — Both default to 3306. XAMPP wins if started first.
2. **Python `pip` vs `pip3`** — On Windows, `pip` usually maps to Python 3.12 already.
3. **Git Bash vs PowerShell** — Git Bash uses Unix paths (`/c/Users/...`), PowerShell uses Windows paths. Agent shell is bash.
4. **`node_modules/.bin`** — Use `npx` or `npm run` instead of direct paths.

## When to Use

- Setting up a new project on this machine
- Debugging "command not found" or port conflicts
- Choosing between Docker and native service instances

## When NOT to Use

- Linux/Mac environments
- CI/CD pipelines (use Docker there)
