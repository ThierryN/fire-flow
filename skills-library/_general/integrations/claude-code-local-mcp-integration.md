---
name: claude-code-local-mcp-integration
category: integrations
version: 1.0.0
contributed: 2026-03-01
contributor: your-memory-repo
last_updated: 2026-03-01
contributors:
  - your-memory-repo
tags: [mcp, claude-code, stdio, local-server, debugging, configuration]
difficulty: easy
usage_count: 0
success_rate: 100
---

# Claude Code Local MCP Server Integration

## Problem

Building an MCP server is well-documented, but registering it with Claude Code, configuring environment variables, debugging startup failures, and testing locally are NOT. Common issues:

- Server configured in `mcp.json` but tools don't appear after restart
- Server works standalone but fails when Claude Code spawns it
- Environment variables not passed through correctly
- No visibility into why a server failed to connect
- Server name shows "not found" in `/mcp` dialog

## Solution Pattern

Follow this integration checklist to reliably register, test, and debug local stdio MCP servers with Claude Code.

## Registration — mcp.json

All MCP servers for Claude Code are registered in `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["tsx", "C:/path/to/my-server.ts"],
      "env": {
        "QDRANT_URL": "http://localhost:6335",
        "API_KEY": "${MCP_MY_SERVER_API_KEY}"
      }
    }
  }
}
```

**Key rules:**
- **Server name** (`my-server`): kebab-case, used in `/mcp` dialog and tool prefixes
- **command**: The executable (`npx`, `node`, `python`, etc.)
- **args**: Arguments passed to the command (for TypeScript, use `["tsx", "/absolute/path.ts"]`)
- **env**: Environment variables passed to the server process
- **`${VAR_NAME}` syntax**: References variables from `~/.claude/.env` — use for secrets
- **Absolute paths**: Always use absolute paths in args; relative paths resolve from Claude Code's CWD, not the server's location

### HTTP Transport Alternative

For remote or shared servers:

```json
{
  "mcpServers": {
    "my-remote-server": {
      "type": "http",
      "url": "https://my-server.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${MCP_MY_SERVER_TOKEN}"
      }
    }
  }
}
```

## Server Lifecycle

1. **Session start**: Claude Code reads `mcp.json` and spawns all configured servers
2. **Connection**: Each server's stdio transport is connected; tools are discovered
3. **Mid-session**: `/mcp` dialog shows status and allows restart
4. **Session end**: All server processes are terminated

**Critical timing**: If a server fails during step 1-2, it will NOT appear in the session. Claude Code does not retry failed servers automatically.

## Testing Before Registration

**Always test the server standalone before registering with Claude Code:**

```bash
# Test 1: Does the server start without errors?
cd /path/to/project
npx tsx src/mcp-server.ts
# Should see startup message on stderr (stdout is reserved for JSON-RPC)

# Test 2: Does it respond to MCP protocol?
# Send a JSON-RPC initialize request on stdin:
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-01-01","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | npx tsx src/mcp-server.ts

# Test 3: Are dependencies running?
curl -s http://localhost:6335/collections  # Qdrant
curl -s http://localhost:11434/api/version  # Ollama
```

## Debugging Startup Failures

When tools don't appear after Claude Code restart:

### Step 1: Check `/mcp` Dialog
Run `/mcp` in Claude Code. Look for:
- Server listed but status "error" → server crashed during startup
- Server not listed at all → invalid mcp.json syntax or server name mismatch

### Step 2: Test Standalone
```bash
# Run with the EXACT same env vars Claude Code would pass
QDRANT_URL=http://localhost:6335 OLLAMA_URL=http://localhost:11434 npx tsx src/mcp-server.ts
```

### Step 3: Check Dependencies
The most common failure: the server starts but crashes connecting to a dependency (Qdrant, Ollama, database) that isn't running.

```bash
# Check Qdrant
curl -s http://localhost:6335/collections && echo "OK" || echo "QDRANT DOWN"

# Check Ollama
curl -s http://localhost:11434/api/version && echo "OK" || echo "OLLAMA DOWN"
```

### Step 4: Check `npx` Resolution
`npx tsx` needs to resolve `tsx` from the project's `node_modules` or globally. If the server is outside a Node project:

```bash
# Install tsx globally as fallback
npm install -g tsx
```

### Step 5: Validate mcp.json Syntax
```bash
# Parse check
node -e "JSON.parse(require('fs').readFileSync(process.env.HOME+'/.claude/mcp.json','utf-8'))" && echo "VALID" || echo "INVALID JSON"
```

## Common Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Server "not found" in `/mcp` | Invalid JSON in mcp.json | Fix syntax, restart session |
| Server listed but no tools | Server crashed after registering | Check stderr logs, test standalone |
| Tools appear but return errors | Dependencies not running | Start Qdrant/Ollama/DB before session |
| `${VAR}` not resolved | Missing from `~/.claude/.env` | Add variable to .env file |
| Works in bash, fails in Claude Code | Different working directory | Use absolute paths everywhere |
| Intermittent failures | Server startup race condition | Add connection retry logic in server |

## Server Code Best Practices

```typescript
// 1. Log to STDERR only (stdout is JSON-RPC transport)
console.error('Server starting...');  // OK
console.log('Debug info');            // BREAKS the protocol

// 2. Graceful dependency checks
async function main() {
  try {
    await checkQdrantConnection();
    await checkOllamaConnection();
  } catch (err) {
    console.error('Dependency check failed:', err.message);
    console.error('Server will start but some tools may fail.');
    // DON'T exit — let the server start so Claude Code can see it
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('MCP server running (stdio)');
}

// 3. Tool-level error handling (never crash the server)
server.tool('my_tool', 'Description', schema, async (params) => {
  try {
    const result = await doWork(params);
    return { content: [{ type: 'text', text: formatResult(result) }] };
  } catch (error) {
    return {
      content: [{ type: 'text', text: `Error: ${error.message}` }],
      isError: true,  // Tells Claude this is an error, not a result
    };
  }
});
```

## Environment Variable Pattern

```
# ~/.claude/.env
MCP_QDRANT_URL=http://localhost:6335
MCP_OLLAMA_URL=http://localhost:11434
MCP_MY_SECRET_KEY=sk-abc123
```

```json
// ~/.claude/mcp.json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["tsx", "C:/path/to/server.ts"],
      "env": {
        "QDRANT_URL": "${MCP_QDRANT_URL}",
        "OLLAMA_URL": "${MCP_OLLAMA_URL}",
        "SECRET_KEY": "${MCP_MY_SECRET_KEY}"
      }
    }
  }
}
```

## When to Use

- Registering any locally-built MCP server with Claude Code
- Debugging why MCP tools don't appear after session restart
- Setting up environment variables for local services (Qdrant, Ollama, databases)
- Troubleshooting server startup failures

## When NOT to Use

- Building the MCP server itself (use the mcp-builder skill instead)
- Deploying remote MCP servers (use Cloudflare Workers MCP skill)
- Using existing marketplace MCP servers (they handle their own registration)

## Common Mistakes

- **Logging to stdout** — breaks JSON-RPC protocol; always use `console.error()`
- **Relative paths in mcp.json** — resolve from Claude Code's CWD, not server location; use absolute paths
- **Crashing on missing dependencies** — let the server start so Claude Code registers it; fail gracefully at the tool level
- **Not testing standalone first** — always verify the server works in isolation before registering
- **Forgetting to restart Claude Code** — MCP servers are discovered at session start; mid-session changes to mcp.json require `/mcp` restart or new session

## Related Skills

- [mcp-composite-tool-orchestration](./mcp-composite-tool-orchestration.md) - Building composite multi-step MCP tools
- [node_mcp_server](../../marketplaces/anthropic-agent-skills/skills/mcp-builder/reference/node_mcp_server.md) - Base MCP server architecture
- [mcp_best_practices](../../marketplaces/anthropic-agent-skills/skills/mcp-builder/reference/mcp_best_practices.md) - Naming, security, transport selection

## References

- Proven on: your-memory-repo codebase-context MCP server (Feb 2026)
- Common failures documented from 3 sessions of MCP debugging
- Claude Code MCP architecture: stdio transport, mcp.json configuration
