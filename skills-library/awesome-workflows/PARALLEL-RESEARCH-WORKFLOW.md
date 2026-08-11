---
name: parallel-research-workflow
category: awesome-workflows
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
last_updated: 2026-02-24
tags: [research, parallel-agents, synthesis, papers]
difficulty: medium
---

# Parallel Research Workflow

## Problem

Single-agent research is slow and narrow. One agent reads one paper at a time, follows one thread, and misses cross-domain connections. For complex decisions (architecture, tooling, framework selection), you need breadth AND depth simultaneously.

## Solution Pattern

Spawn 3-4 parallel research agents, each with a distinct focus area. A synthesis agent merges their findings into a unified report with prioritized recommendations.

## Workflow Steps

### 1. Define Research Scopes

Split the research space into non-overlapping focus areas:

```
Agent 1: "Best practices" — Official docs, Anthropic guidance, framework conventions
Agent 2: "Academic research" — 2025-2026 papers, benchmarks, novel techniques
Agent 3: "Tool comparison" — Open-source tools, dashboards, integrations
Agent 4: "Gap audit" — What's missing in current implementation vs. best practices
```

### 2. Spawn Parallel Researchers

```
Task(prompt="Research {focus_area}. Find 10-15 findings.
  For each: title, key insight, how it applies to {project}.
  Save to .planning/research/agent-{N}-{focus}.md",
  subagent_type="Explore", description="Research {focus}")
```

Launch ALL agents simultaneously — they read but don't write code.

### 3. Synthesize Findings

After all agents return:
- Read all `.planning/research/agent-*.md` files
- Merge into a single report with:
  - Top 8-10 findings ranked by impact
  - Full comparison matrices for tool selections
  - Gap audit with severity (HIGH/MEDIUM/LOW)
  - Prioritized action list

### 4. Present Recommendations

```
| # | Finding | Source | Effort | Impact |
|---|---------|--------|--------|--------|
| 1 | ...     | Paper  | Medium | HIGH   |
```

## When to Use

- Before major architecture decisions
- When evaluating frameworks, tools, or approaches
- When upgrading an existing system (find what's changed since last review)
- Before starting a new milestone or project phase

## When NOT to Use

- Simple bug fixes or feature additions
- When the answer is already known and documented
- For tasks that don't benefit from breadth (single-file changes)

## Real Example

Dominion Flow v9.0 used this exact workflow:
- Agent 1: Claude Agent Best Practices (15 findings)
- Agent 2: Agentic AI Research 2025-2026 (20 findings)
- Agent 3: Agent Monitoring Dashboards (15 tools compared)
- Gap Audit: 31 gaps identified (11 HIGH, 14 MEDIUM, 6 LOW)
- Result: All 11 HIGH gaps closed in one session

## Related Skills

- [methodology/WARRIOR_HANDOFF_FORMAT.md](../methodology/) — Document research outcomes
- [parallel-debug/parallel-debug.md](../parallel-debug/) — Same parallel pattern for debugging
