---
name: tiered-context-architecture
category: methodology
version: 1.0.0
contributed: 2026-03-06
contributor: dominion-flow
last_updated: 2026-03-06
contributors:
  - dominion-flow
tags: [context-management, ai-agent, llm, token-optimization, memory-tiers]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Tiered Context Architecture (Hot/Warm/Cold)

## Problem

AI agents working on long-running tasks fill their context window with a mix of critical and stale information. Without explicit categorization, all context is treated equally — leading to premature context exhaustion, irrelevant information competing with critical state, and poor compaction decisions that drop important details while preserving noise.

Symptoms:
- Agent "forgets" current task details while retaining old file contents
- Context compaction drops error messages but keeps completed task descriptions
- Agent hits context limits mid-task with no clear eviction strategy
- Output quality degrades because reasoning competes with stale data

## Solution Pattern

Categorize every context segment into three tiers based on access recency and task relevance, then apply tier-specific retention policies:

**HOT** (never compress, ~15% budget): Current task, active errors, recitation block, circuit breaker state, failed approaches list. This is the "working memory" — losing any of it causes immediate task failure.

**WARM** (compressible, ~45% budget): Plan context, loaded skills, recently-read files, recent decisions, episodic recall. Useful for current phase but can be compressed to key points when space is needed.

**COLD** (evictable, 0% budget in window): Files read 5+ iterations ago, completed task details, resolved errors, unused skills. Saved to disk, retrievable on demand, but not occupying context window.

The key insight: tier assignment is **dynamic** — segments promote (COLD→WARM when re-referenced) and demote (HOT→WARM when task changes) based on actual usage patterns, not static rules.

## Code Example

```
// Before (problematic) — flat context, no tiers
context = [
  system_prompt,          // critical
  file_read_10_turns_ago, // stale — wastes space
  current_task,           // critical
  old_error_resolved,     // stale — wastes space
  active_error,           // critical
  completed_task_1,       // stale
  completed_task_2,       // stale
  skill_never_used,       // stale
]
// Result: 60% of context is stale. Compaction randomly drops items.

// After (solution) — tiered context with explicit budgets
HOT = [current_task, active_error, recitation, circuit_breaker, failed_approaches]
WARM = [plan_context, loaded_skills, recent_files, decisions]
COLD = [] // evicted to disk: old_files, completed_tasks, resolved_errors

// Budget enforcement:
IF hot_tokens > 30K: ERROR — hot tier should never exceed budget
IF warm_tokens > 90K: compress WARM to 50% (keep key points)
IF total > 70%: evict all COLD, compress WARM to 30%
IF total > 85%: keep only HOT, trigger handoff

// Dynamic tier transitions:
IF segment.last_accessed > 5 iterations: demote to COLD
IF cold_segment.referenced_by_current_task: promote to WARM
IF warm_segment.is_active_error: promote to HOT
IF hot_segment.error_resolved: demote to WARM → COLD
```

## Implementation Steps

1. Define tier assignment function based on segment type and recency
2. Set token budgets per tier (15% HOT, 45% WARM, 0% COLD)
3. Tag each context segment with its tier on creation/injection
4. Run tier reassignment every 3 iterations (not every iteration — overhead)
5. When context exceeds 70%, compress WARM tier first, then evict COLD
6. Preserve HOT tier unconditionally — never compress or evict
7. Log tier transitions for debugging context management issues

## When to Use

- Any AI agent system with long-running tasks (10+ iterations)
- Multi-phase execution pipelines where old phase context becomes stale
- Agents that read many files but only work on a few at a time
- Systems where context compaction causes "amnesia" of critical state
- When you need to extend useful context life before forced handoff

## When NOT to Use

- Short conversations (< 5 turns) — overhead isn't worth it
- Single-file edits with no accumulated context
- Systems with unlimited context windows (if such a thing existed)
- When all context segments are equally critical (rare but possible)

## Common Mistakes

- Setting HOT budget too large — defeats the purpose of tiering. HOT should be < 20% of window
- Never demoting segments — HOT tier grows unbounded if old errors aren't demoted after resolution
- Compressing HOT tier during context pressure — this causes immediate task failure
- Evicting COLD without saving to disk — you lose the ability to retrieve if needed later
- Running tier reassignment every iteration — the overhead reduces net context benefit

## Related Skills

- [RESEARCH_BACKED_WORKFLOW_UPGRADE](../methodology/RESEARCH_BACKED_WORKFLOW_UPGRADE.md) - Research methodology that discovered this pattern
- [AGENT_SELF_IMPROVEMENT_LOOP](../methodology/AGENT_SELF_IMPROVEMENT_LOOP.md) - Agent improvement patterns

## References

- Spotify "Honk" Architecture (2024) — tiered context management reduces failures by 40%
- ACON "Active Context Compression" (2025-2026) — 26-54% token reduction via selective compression
- PAACE "Plan-Aware Agent Context Engineering" (2025) — plan-aware preservation during compression
- Focus (ACL 2025) — active forgetting for proactive context management
- Contributed from: dominion-flow v10.1 research session
