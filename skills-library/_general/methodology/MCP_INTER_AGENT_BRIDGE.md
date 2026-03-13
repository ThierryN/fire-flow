# MCP Inter-Agent Communication Bridge

> Use an MCP server as a message bus between Claude Code instances for coordinated multi-agent workflows.

**When to use:** When you need two or more Claude Code instances (running in separate terminals) to communicate — beyond what `.claude/agents/` subagents or Agent Teams provide. Useful for: cross-repo review, long-running monitoring, or heterogeneous agent setups.
**Stack:** Node.js/TypeScript, MCP SDK

---

## When to Use This vs Alternatives

| Need | Best Approach |
|------|--------------|
| Single reviewer in same session | `.claude/agents/` subagent file |
| Fire-and-forget CLI review | `claude -p "prompt"` |
| Competing reviewers that discuss | Agent Teams (experimental) |
| Standalone review server | Agent SDK |
| **Cross-instance communication** | **MCP bridge (this skill)** |
| **Persistent message bus** | **MCP bridge (this skill)** |

---

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│ Claude Code          │     │ Claude Code          │
│ Instance A           │     │ Instance B           │
│ (executor)           │     │ (reviewer)           │
│                      │     │                      │
│ MCP Client ──────────┼─────┼─▶ MCP Client         │
│                      │     │                      │
└──────────┬───────────┘     └──────────┬───────────┘
           │                            │
           │    ┌──────────────────┐    │
           └───▶│  MCP Bridge      │◀───┘
                │  Server          │
                │                  │
                │  Tools:          │
                │  - submit_review │
                │  - get_verdict   │
                │  - send_message  │
                │  - get_messages  │
                └──────────────────┘
```

---

## Simple File-Based Bridge (No Server Required)

The simplest MCP-less approach — use the filesystem as a message queue:

```javascript
// Agent A writes a review request
const request = {
  id: crypto.randomUUID(),
  type: 'review_request',
  from: 'executor',
  files: ['src/routes/payment.ts', 'src/controllers/checkout.ts'],
  prompt: 'Review these files for security issues',
  created_at: new Date().toISOString(),
};
fs.writeFileSync('.planning/.agent-inbox/review-request.json', JSON.stringify(request, null, 2));

// Agent B polls for requests and writes verdict
const verdict = {
  id: crypto.randomUUID(),
  request_id: request.id,
  type: 'review_verdict',
  from: 'reviewer',
  verdict: 'APPROVE_WITH_FIXES',
  issues: [{ severity: 'major', file: 'src/routes/payment.ts', line: 42, description: 'Missing auth check' }],
  created_at: new Date().toISOString(),
};
fs.writeFileSync('.planning/.agent-inbox/review-verdict.json', JSON.stringify(verdict, null, 2));

// Agent A reads verdict
const result = JSON.parse(fs.readFileSync('.planning/.agent-inbox/review-verdict.json', 'utf-8'));
```

### Directory Structure

```
.planning/.agent-inbox/
  review-request.json      # Executor → Reviewer
  review-verdict.json      # Reviewer → Executor
  messages.jsonl           # Append-only message log
```

---

## Using claude-code-mcp (steipete)

Run Claude Code itself as an MCP server that other agents can invoke:

```bash
# Install
npx -y @anthropic-ai/claude-code mcp add claude-code-mcp -- npx -y @anthropic-ai/claude-code --dangerously-skip-permissions

# Now any MCP client can call:
# Tool: claude_code
# Input: { "prompt": "Review src/payment.ts for security issues", "workFolder": "/path/to/project" }
```

This gives any Claude Code instance a `claude_code` tool that spawns another Claude Code instance as a one-shot tool call. The "agent in your agent" pattern.

---

## Custom MCP Bridge Server

For more control, build a simple MCP server:

```typescript
// bridge-server.ts
import { McpServer } from "@anthropic-ai/mcp-sdk";

const messages: any[] = [];
const verdicts: Map<string, any> = new Map();

const server = new McpServer({
  name: "agent-bridge",
  version: "1.0.0",
});

server.tool("submit_review_request", {
  description: "Submit code for review by another agent",
  inputSchema: {
    type: "object",
    properties: {
      files: { type: "array", items: { type: "string" } },
      prompt: { type: "string" },
      priority: { type: "string", enum: ["low", "medium", "high"] },
    },
    required: ["files", "prompt"],
  },
  handler: async (input) => {
    const id = crypto.randomUUID();
    messages.push({ id, type: "review_request", ...input, created_at: new Date() });
    return { request_id: id, status: "queued" };
  },
});

server.tool("get_pending_reviews", {
  description: "Get pending review requests",
  inputSchema: { type: "object", properties: {} },
  handler: async () => {
    const pending = messages.filter(m => m.type === "review_request" && !verdicts.has(m.id));
    return { pending };
  },
});

server.tool("submit_verdict", {
  description: "Submit a review verdict",
  inputSchema: {
    type: "object",
    properties: {
      request_id: { type: "string" },
      verdict: { type: "string", enum: ["APPROVE", "APPROVE_WITH_FIXES", "BLOCK"] },
      issues: { type: "array" },
    },
    required: ["request_id", "verdict"],
  },
  handler: async (input) => {
    verdicts.set(input.request_id, input);
    return { status: "recorded" };
  },
});

server.tool("get_verdict", {
  description: "Check if a review verdict is available",
  inputSchema: {
    type: "object",
    properties: { request_id: { type: "string" } },
    required: ["request_id"],
  },
  handler: async (input) => {
    const verdict = verdicts.get(input.request_id);
    return verdict || { status: "pending" };
  },
});

server.start();
```

---

## Practical Recommendation

For most Dominion Flow users, the **file-based bridge** is sufficient:
1. No extra server to run
2. Both agents can read/write to `.planning/.agent-inbox/`
3. JSONL append log provides audit trail
4. Works on all platforms

Use the MCP server approach only when:
- Agents run on different machines
- You need real-time communication (not polling)
- You're building a production orchestration service

---

## Sources

- steipete/claude-code-mcp (GitHub) — Claude Code as MCP server
- GongRzhe/ACP-MCP-Server (GitHub) — ACP-MCP bridge
- Claude Code MCP documentation (2026)
- Internal gap analysis: Auto-connect agents research TODO
