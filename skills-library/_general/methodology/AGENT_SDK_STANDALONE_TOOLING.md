# Agent SDK Standalone Tooling

> Build a standalone review/orchestration server using the Anthropic Claude Agent SDK for programmatic multi-agent workflows outside Claude Code sessions.

**When to use:** Building CI/CD review pipelines, automated code review servers, or standalone orchestration tools that need to programmatically spawn Claude agents.
**Stack:** TypeScript/Node.js, @anthropic-ai/claude-agent-sdk

---

## When to Use SDK vs Subagents vs CLI

| Approach | Use Case | Complexity |
|----------|----------|------------|
| `.claude/agents/` subagent files | In-session review, ad-hoc tasks | Low |
| `claude -p` CLI spawning | CI/CD, cron jobs, fire-and-forget | Low |
| Agent SDK | Standalone servers, custom orchestration, multi-agent pipelines | High |

**Use SDK when:** You need a persistent service that programmatically spawns, monitors, and coordinates agents independent of any Claude Code session.

---

## Installation

```bash
npm install @anthropic-ai/claude-agent-sdk
```

---

## Basic Usage: Single Agent Query

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

async function reviewCode(directory: string): Promise<string> {
  let result = '';

  for await (const message of query({
    prompt: `Review all files in ${directory} for bugs and security issues.`,
    options: {
      model: "sonnet",
      allowedTools: ["Read", "Glob", "Grep"],
      permissionMode: "bypassPermissions",
      maxTurns: 50,
    }
  })) {
    if (message.type === "assistant" && message.content) {
      for (const block of message.content) {
        if (block.type === "text") {
          result += block.text;
        }
      }
    }
  }

  return result;
}
```

---

## Multi-Agent Review Pipeline

```typescript
import { query, AgentDefinition } from "@anthropic-ai/claude-agent-sdk";

// Define specialized reviewer agents inline
const reviewerAgents: Record<string, AgentDefinition> = {
  "security-reviewer": {
    description: "Finds security vulnerabilities",
    prompt: "You are a security expert. Find vulnerabilities in the code.",
    tools: ["Read", "Grep", "Glob"],
    model: "sonnet",
  },
  "quality-reviewer": {
    description: "Finds code quality issues",
    prompt: "You are a code quality expert. Find issues in the code.",
    tools: ["Read", "Grep", "Glob"],
    model: "haiku",
  },
};

async function runParallelReview(directory: string) {
  // Launch both reviewers in parallel using Promise.all
  const reviewPromises = Object.entries(reviewerAgents).map(
    async ([name, agent]) => {
      let output = '';
      for await (const msg of query({
        prompt: `Use the ${name} agent to review code in ${directory}.`,
        options: {
          model: "opus",
          agents: { [name]: agent },
          allowedTools: ["Read", "Glob", "Grep", "Task"],
          permissionMode: "bypassPermissions",
          maxTurns: 100,
        }
      })) {
        if (msg.type === "assistant") {
          for (const block of msg.content || []) {
            if (block.type === "text") output += block.text;
          }
        }
      }
      return { name, output };
    }
  );

  return Promise.all(reviewPromises);
}
```

---

## CI/CD Integration Pattern

```typescript
// ci-review.ts — Run as a GitHub Action step
import { query } from "@anthropic-ai/claude-agent-sdk";
import { execSync } from "node:child_process";

async function ciReview() {
  // Get the diff safely
  const diffOutput = execSync(
    'git diff origin/main...HEAD',
    { encoding: 'utf-8', maxBuffer: 1024 * 1024 }
  );

  let verdict = '';
  for await (const msg of query({
    prompt: `Review this git diff for bugs and security issues.
Return JSON: {verdict: "APPROVE"|"BLOCK", issues: [{severity, description}]}

Diff:
${diffOutput.slice(0, 50000)}`,
    options: {
      model: "sonnet",
      maxTurns: 20,
      permissionMode: "bypassPermissions",
    }
  })) {
    if (msg.type === "result") {
      verdict = msg.content
        ?.map(b => b.type === 'text' ? b.text : '')
        .join('') || '';
    }
  }

  const jsonMatch = verdict.match(/\{[\s\S]*"verdict"[\s\S]*\}/);
  if (jsonMatch) {
    const parsed = JSON.parse(jsonMatch[0]);
    if (parsed.verdict === 'BLOCK') {
      console.error('Review BLOCKED:', parsed.issues);
      process.exit(1);
    }
  }

  console.log('Review APPROVED');
  process.exit(0);
}

ciReview();
```

---

## Key Considerations

- **API key management:** Use `ANTHROPIC_API_KEY` environment variable
- **Cost:** Each agent invocation costs full API tokens — use cheaper models for routine reviews
- **Streaming:** Use `for await` to process streaming responses
- **Error handling:** Wrap in try/catch — agent failures should not crash the CI pipeline
- **Timeout:** Set `maxTurns` to prevent runaway agents
- **Security:** Use `execSync` with explicit args, not string interpolation with user input

---

## Sources

- Anthropic Agent SDK: TypeScript reference (2026)
- npm: @anthropic-ai/claude-agent-sdk (1.85M+ weekly downloads)
- Anthropic: "How we built our multi-agent research system" (2026)
