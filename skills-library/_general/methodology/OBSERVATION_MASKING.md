---
name: Observation Masking
category: methodology
version: 1.0.0
contributed: 2026-03-12
contributor: fire-research
last_updated: 2026-03-13
tags: [multi-agent, token-optimization, context-engineering, inter-agent-communication]
difficulty: easy
---

# Observation Masking — Strip Raw Output, Keep Action Summaries

> observation masking matches LLM summarization quality at 50% token cost.
> MacNet (ICLR 2025) confirms: propagate only refined artifacts, not full dialogue traces.

## Problem

When agents communicate task results to other agents or orchestrators, the naive approach sends everything: full command output, file contents read, error stack traces, intermediate reasoning. This bloats inter-agent messages, wastes context window tokens, and paradoxically does NOT improve downstream quality — LLMs summarize just as well from a 1-sentence summary as from 500 lines of raw output.

## Solution Pattern

Strip raw tool/environment output from all inter-agent messages. Keep only:
- **Action taken** (what you did)
- **Decision rationale** (why you chose this approach)
- **Result summary** (1 sentence: what happened)
- **Artifacts produced** (file paths, exports, interfaces created)

Exclude:
- Raw command output (build logs, test output, grep results)
- Full file contents read during execution
- Intermediate reasoning traces (keep only final decision)
- Error stack traces (summarize to 1 line)

## Code Example

```
// BAD — 500+ tokens for one task completion message
{
  "type": "COMPLETE",
  "summary": "Ran npm test and got:\n> jest --coverage\nPASS src/auth.test.ts\n  Auth Module\n    ✓ should validate JWT (23ms)\n    ✓ should reject expired tokens (15ms)\n    ✓ should refresh tokens (31ms)\n    ✓ should handle malformed tokens (8ms)\n    ✓ should validate scopes (12ms)\n...[250 more lines of test output]..."
}

// GOOD — 30 tokens, identical downstream quality
{
  "type": "COMPLETE",
  "summary": "Auth module passes all 12 tests (100% coverage). Exports: validateJWT, refreshToken."
}
```

## Implementation Steps

1. Identify all inter-agent communication points (JSONL messages, shared state, return envelopes)
2. At each point, apply the INCLUDE/EXCLUDE filter before writing
3. For error reporting: summarize stack traces to root cause + 1 line
4. For test results: report pass/fail count + coverage, not individual test output
5. For file reads: report what was learned, not what was read

## When to Use

- Any multi-agent system where agents exchange task results
- Long-running autonomous sessions where context accumulates
- Systems with token budgets or context window constraints
- Orchestrator-executor patterns where the orchestrator only needs status, not details

## When NOT to Use

- Debugging sessions where raw output is needed for diagnosis
- Single-agent workflows (no inter-agent communication)
- When the downstream consumer explicitly needs raw data (e.g., log aggregation)

## Must Do

- Apply masking at the WRITE point, not the READ point (sender strips, not receiver)
- Keep decision rationale — this is NOT raw output, it's high-signal context
- Include artifact paths so downstream agents can read files directly if needed

## Must Not Do

- Do not mask within a single agent's own working context (only for messages TO others)
- Do not strip error categories or severity — these are routing signals, not noise
- Do not summarize file paths — exact paths are needed for downstream agents to find files

## Measurable Impact

- **50% token reduction** in inter-agent communication (JetBrains NeurIPS DL4Code 2025)
- **Zero quality loss** — LLM summarization quality matches full observation quality
- **Faster orchestrator processing** — smaller messages = faster parsing

## Related Skills

- [MULTI_AGENT_COORDINATION](./MULTI_AGENT_COORDINATION.md) — parent coordination framework
- [CONTEXT_ROTATION](./CONTEXT_ROTATION.md) — fresh-eyes pattern for context-heavy sessions
- [DISTILL_NOT_DUMP](./DISTILL_NOT_DUMP.md) — same principle applied to handoffs

## References

- "The Complexity Trap" — NeurIPS DL4Code Workshop, JetBrains Research, Dec 2025
- MacNet (ICLR 2025) — Multi-agent cooperation through LLM-based node networks
- Wired into: `fire-executor.md` Step 1.7, `fire-3-execute.md` Step 5 filtered views
