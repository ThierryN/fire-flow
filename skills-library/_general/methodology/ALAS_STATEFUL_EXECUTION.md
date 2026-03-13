---
name: ALAS Stateful Execution
category: methodology
version: 1.0.0
contributed: 2026-03-08
contributor: fire-research
last_updated: 2026-03-08
tags: [multi-agent, token-reduction, checkpoint, state-management, failure-recovery]
difficulty: medium
---

# ALAS Stateful Execution — Checkpoint/Restore for Token-Efficient Agent Coordination

> and SagaLLM: Transaction Guarantees for Multi-Agent (VLDB 2025, arXiv 2503.11951).
> Results: 60% token reduction, 1.82x speed improvement, 83.7% task success on benchmarks.

## Problem

Current agent execution re-injects full context (BLUEPRINT, CONSCIENCE, skills, episodic recall) into every agent spawn and every retry. When an agent fails and restarts, it receives the entire context again — even though 90% of it hasn't changed. This wastes tokens and degrades reasoning depth as context windows fill with repeated information.

Additionally, when a subtask fails, the entire pipeline restarts from scratch rather than repairing only the broken piece.

## Solution Pattern

### Three-Layer Architecture

```
Layer 1: EXECUTION LOG (versioned, append-only)
  - Every agent action logged with checkpoint ID
  - Restore point = any checkpoint in the log
  - Failed subtask = replay from last valid checkpoint

Layer 2: CONTEXT SLICING (per-agent minimal context)
  - Each agent receives ONLY the context slice it needs
  - Shared context referenced by ID, not copied in full
  - Agent returns a 1-2K token summary, not full transcript

Layer 3: LOCALIZED REPAIR (fix subtask, not pipeline)
  - On failure: identify the minimal broken subtask
  - Spawn repair agent with ONLY the failed task's context
  - Validate repair, then resume from checkpoint
  - Never re-run successful subtasks
```

### Execution Log Format

```json
{
  "session_id": "fire-execute-phase-3",
  "checkpoints": [
    {
      "id": "cp-001",
      "task": "03-01-task-1",
      "status": "completed",
      "files_changed": ["src/auth/middleware.ts"],
      "summary": "Added JWT validation middleware with 15-min expiry",
      "confidence": 85,
      "timestamp": "2026-03-08T10:30:00Z"
    },
    {
      "id": "cp-002",
      "task": "03-01-task-2",
      "status": "failed",
      "error_type": "LOGIC",
      "error": "Refresh token rotation creates duplicate sessions",
      "files_changed": ["src/auth/refresh.ts"],
      "last_valid_checkpoint": "cp-001",
      "timestamp": "2026-03-08T10:35:00Z"
    }
  ]
}
```

### Context Slicing Rules

**BEFORE (wasteful — current pattern):**
```
Agent spawn context = FULL BLUEPRINT (2K tokens)
  + FULL CONSCIENCE.md (1K tokens)
  + ALL skills_to_apply (3-5K tokens)
  + Episodic recall results (1-2K tokens)
  + Full playbook (500 tokens)
  = 8-10K tokens per agent, EVERY spawn
```

**AFTER (ALAS pattern — minimal slicing):**
```
Agent spawn context = TASK SLICE ONLY:
  - Task description + done criteria (200-400 tokens)
  - Relevant file paths (50-100 tokens)
  - Context pointer: "Read BLUEPRINT section 3.2 if needed" (30 tokens)
  - Last checkpoint summary (100-200 tokens)
  - Playbook (rolling 5 entries, 200-300 tokens)
  = 600-1000 tokens per agent

Full context available ON DEMAND — agent reads files only when needed,
not pre-injected into every spawn.
```

**Token savings: ~80% per agent spawn. Across a 5-agent breath: 40-50K tokens saved.**

### Localized Repair Protocol

```
ON FAILURE at checkpoint cp-N:
  1. Read execution log → find last_valid_checkpoint (cp-N-1)
  2. Classify failure type (from circuit breaker Step 3.5.2):
     - TRANSIENT → retry same task with same context slice
     - FIXATION → retry with DIFFERENT approach hint from FAILURES.md
     - LOGIC → spawn repair agent with:
         - Failed task description
         - Error message
         - Files changed since last valid checkpoint
         - git diff from cp-N-1 to cp-N (shows exactly what broke)
     - ARCHITECTURE → escalate to planner (not fixable locally)
  3. Repair agent returns:
     - Fixed files
     - 1-2 sentence summary
     - New checkpoint entry
  4. Validate: run task's done criteria tests
  5. IF pass: update checkpoint status to "repaired", continue
  6. IF fail: escalate (max 2 repair attempts per checkpoint)

NEVER re-run completed checkpoints. They stay valid.
```

### Agent Return Protocol (Summary-Only)

```
When a sub-agent completes (success or failure), it returns ONLY:

{
  "status": "completed | failed | blocked",
  "summary": "1-2 sentences of what was done",        // MAX 200 tokens
  "files_changed": ["path/to/file.ts"],                // list only
  "next_agent_needs": "Brief note for downstream",     // MAX 100 tokens
  "checkpoint_id": "cp-003"
}

The orchestrator reads this summary — NOT the agent's full transcript.
Full transcript is available in the execution log if needed for debugging.
```

## Implementation in Dominion Flow

### Where It Plugs In

| Component | Change |
|-----------|--------|
| `fire-executor.md` Step 1 | Replace full context injection with context slice |
| `fire-executor.md` Step 3 | Write checkpoint after each task |
| `fire-executor.md` Step 3.5 | On circuit breaker trip → localized repair, not full restart |
| `fire-executor.md` Step 5 | Checkpoints replace verbose handoff sections |
| `fire-3-execute.md` Step 3.6 | Agent spawning uses minimal context slices |
| `fire-3-execute.md` Step 4 | Breath completion reads summaries, not full transcripts |
| `fire-autonomous.md` | Phase transitions use checkpoint logs for state transfer |

### Execution Log Location

```
.planning/phases/{N}-{name}/execution-log.json
```

Written by the orchestrator. Each executor agent appends its checkpoint.
Verifier reads the log to know what was done without re-reading all code.

## When to Use

- Multi-task execution with 3+ tasks per phase
- Parallel agent spawning (SUBAGENT/SWARM modes)
- Long-running autonomous sessions (fire-autonomous)
- Any retry/repair scenario where full restart is wasteful

## When NOT to Use

- Single-task phases (overhead > savings)
- First task in a phase (no checkpoint to restore from)
- Tasks where the entire context truly is needed (rare — architecture decisions)

## Must Do

- Write checkpoint AFTER each successful task commit
- Use context slices, not full BLUEPRINT injection for sub-agents
- Return summaries (200 tokens max), not transcripts
- Repair locally before restarting globally
- Track token savings in execution log for metrics

## Must Not Do

- Do not skip checkpoints to "save time" — they ARE the savings
- Do not inject full context "just in case" — agents read on demand
- Do not retry more than 2x at the same checkpoint — escalate
- Do not re-run completed checkpoints on failure downstream

## Related Skills

- [CIRCUIT_BREAKER_INTELLIGENCE](./CIRCUIT_BREAKER_INTELLIGENCE.md) — stuck-state classification feeds repair routing
- [CONTEXT_ROTATION](./CONTEXT_ROTATION.md) — fresh-eyes pattern for FIXATION-type failures
- [AUTONOMOUS_ORCHESTRATION](./AUTONOMOUS_ORCHESTRATION.md) — phase-level orchestration uses checkpoint logs

## References

- ALAS: Stateful Multi-LLM Agent Framework — [arXiv 2505.12501](https://arxiv.org/abs/2505.12501)
- ALAS Transactional Update — [arXiv 2511.03094](https://arxiv.org/abs/2511.03094)
- SagaLLM: Context Management and Transaction Guarantees — [VLDB 2025](https://www.vldb.org/pvldb/vol18/p4874-chang.pdf)
- Anthropic: Effective Context Engineering — [anthropic.com/engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- JetBrains Research: Efficient Context Management — [blog.jetbrains.com](https://blog.jetbrains.com/research/2025/12/efficient-context-management/)
