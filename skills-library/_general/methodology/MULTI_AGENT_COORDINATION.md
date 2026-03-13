---
name: Multi-Agent Coordination Patterns
category: methodology
version: 1.0.0
contributed: 2026-03-08
contributor: fire-research
last_updated: 2026-03-08
tags: [multi-agent, coordination, error-handling, delegation, arbitration, communication]
difficulty: hard
---

# Multi-Agent Coordination — Production Patterns from Open-Source Tools

> lazygit, ruff, oxc, biome, uv, vite, delta, starship, DevToys, it-tools, lapce.
> These patterns are battle-tested in production tools with millions of users.

## 1. Error Classification Taxonomy (Gap #2, #3)

> **Source:** biome `handler.rs`, oxc `service.rs`, ruff `check.rs`
> Pattern: Category-based error routing with isolation boundaries

### Error Categories for Agent Execution

```
SEVERITY LEVELS (route differently):
  PANIC:     Agent crashed unexpectedly
             → Isolate (catch_unwind pattern), emit diagnostic, continue other agents
             → NEVER cascade to sibling agents

  ERROR:     Task failed with known cause
             → Classify by type (see below), route to appropriate handler
             → Increment accumulated_weight in circuit breaker

  WARNING:   Task completed with concerns
             → Log to playbook, continue execution
             → Check cumulative threshold (max_warnings pattern from oxc)

  INFO:      Discovery or observation
             → Add to playbook as DISCOVERY entry
             → No intervention needed

ERROR TYPE ROUTING (different types get different treatment):
  INTERMITTENT: Build failure, API timeout, flaky test
                → Retry up to 2x with same context (each retry adds weight to circuit breaker)
                → Source: ruff IOError rule — check if error type's retry is enabled
                → NOTE: Named INTERMITTENT (not TRANSIENT) to avoid collision with stuck-state TRANSIENT

  LOGIC:        Wrong output, failed assertion, incorrect behavior
                → Re-read requirements, try different approach
                → Source: biome category routing — route to different handler

  ARCHITECTURE: Wrong file structure, circular dependency, contract violation
                → Escalate to planner, do NOT retry locally
                → Source: oxc no-cycle rule — detect and report, don't fix

  ENVIRONMENT:  Missing dependency, wrong version, permission denied
                → Fix environment, then retry task
                → Source: ruff — IOError vs ParseError distinction

CUMULATIVE THRESHOLD (from oxc max_warnings):
  Track warning_count across all tasks in a breath
  IF warning_count > max_warnings (default: 10):
    → Convert accumulated warnings to ERROR
    → Trip circuit breaker
    → "Too many warnings indicate systemic issue — investigate root cause"
```

### Cascade Prevention (catch_unwind pattern from biome)

```
FOR each agent spawned in parallel:
  result = catch_agent_execution(agent, task)

  MATCH result:
    OK(completed) → record success, continue
    OK(failed)    → record failure as diagnostic, continue OTHER agents
    PANIC(error)  → record panic as diagnostic, continue OTHER agents
                     Log: "Agent {name} panicked on task {N}: {error}"
                     The PANIC is captured, NOT propagated.

  CRITICAL: One agent's failure NEVER stops sibling agents.
  Each agent runs in isolation. Failures are collected and reported
  after ALL agents in the breath complete.
```

## 2. Semaphore Delegation Bounding (Gap #7)

> **Source:** turborepo `execute.rs`, mise `task_scheduler.rs`
> Pattern: Permit pool limits concurrent agent spawning

```
max_concurrent_agents = 4  (default, configurable)

semaphore = Semaphore(max_concurrent_agents)

FOR each agent to spawn:
  permit = semaphore.acquire()  // blocks if all permits taken
  spawn_agent(task, permit)

  ON agent completion:
    permit.release()  // next waiting agent can proceed

RULES:
  - Sub-agents spawned BY agents do NOT get separate permits
    (they share their parent's permit — prevents depth explosion)
  - SWARM mode: max_concurrent_agents = min(plan_count, 4)
  - SUBAGENT mode: max_concurrent_agents = min(plan_count, 3)
  - SEQUENTIAL mode: max_concurrent_agents = 1
```

## 3. Task Ownership Protocol (Gap #6)

> **Source:** mise `task_scheduler.rs`, turborepo `visitor/mod.rs`
> Pattern: Explicit ownership with transfer tracking

```
TASK OWNERSHIP (in .planning/.shared-state.json):
{
  "tasks": {
    "03-01-task-1": {
      "owner": "backend-agent",
      "status": "in_progress",
      "claimed_at": "2026-03-08T10:30:00Z",
      "transfer_count": 0
    },
    "03-01-task-2": {
      "owner": null,
      "status": "pending",
      "claimed_at": null,
      "transfer_count": 0
    }
  }
}

CLAIM PROTOCOL:
  1. Agent reads .shared-state.json
  2. Finds task with owner=null and status=pending
  3. Writes owner={agent_name}, status=in_progress, claimed_at=now()
  4. Proceeds with task

TRANSFER RULES:
  - transfer_count tracks how many times a task changed hands
  - IF transfer_count >= 2: escalate to orchestrator (task is toxic)
  - On transfer: previous owner writes failure summary to task entry
  - Source: Academic research — 17x error amplification in unstructured networks

COMPLETION:
  - Agent writes status=completed, adds summary
  - Checks for next unclaimed task
  - IF no unclaimed tasks: agent signals idle
```

## 4. Structured Agent Return Envelope (Gap #9)

> **Source:** biome `FileStatus` enum, mern-community-lms response envelope
> Pattern: Consistent structured output from every agent

```
EVERY agent returns this envelope (not prose, not ad-hoc):

{
  "agent": "{agent_name}",
  "plan": "{N}-{NN}",
  "status": "completed | failed | blocked | partial",
  "summary": "1-2 sentences of what was done",  // MAX 200 tokens
  "tasks": {
    "completed": ["task-1", "task-2"],
    "failed": ["task-3"],
    "skipped": []
  },
  "files_changed": ["path/to/file.ts"],
  "errors": [
    {
      "task": "task-3",
      "category": "INTERMITTENT | LOGIC | ARCHITECTURE | ENVIRONMENT",
      "message": "What went wrong",
      "severity": "ERROR | WARNING | PANIC",
      "retry_eligible": true
    }
  ],
  "warnings_count": 2,
  "confidence": 75,
  "checkpoint_id": "cp-003",
  "next_needs": "Brief note for downstream agent"  // MAX 100 tokens
}

PARSING RULES FOR ORCHESTRATOR:
  - status=completed → proceed to next breath
  - status=partial → some tasks done, check tasks.failed for retry
  - status=failed → check errors[].category for routing
  - status=blocked → read errors[0].message for blocker description
  - warnings_count > 10 → treat as soft failure
```

## 5. Verdict Arbitration Protocol (Gap #5)

> **Source:** uv PubGrub `priority.rs`, turborepo `lib.rs` (Tarjan SCC + cut sets)
> Pattern: Resolve conflicting verdicts with weighted scoring + fork strategy

```
WHEN verifier and reviewer produce contradictory verdicts:

  1. CLASSIFY CONFLICT TYPE:
     - SCOPE: Verifier checks functionality, reviewer checks quality
       → Both can be right. Apply BOTH sets of fixes.
     - SEVERITY: Verifier says PASS, reviewer says BLOCK
       → Weighted resolution (see below)
     - CONTRADICTION: Verifier says "add X", reviewer says "remove X"
       → Fork resolution (spawn parallel branches)

  2. WEIGHTED RESOLUTION (from uv conflict prioritization):
     verifier_weight = 0.6  (functional correctness is primary)
     reviewer_weight = 0.4  (code quality is secondary)

     FOR each conflicting item:
       IF verifier says PASS and reviewer says BLOCK:
         combined_score = (verifier_confidence * 0.6) + (reviewer_confidence * 0.4)
         IF combined_score > 70: PASS with reviewer's suggestions as TODOs
         IF combined_score <= 70: FAIL — fix required

       IF verifier says FAIL: always FAIL (functional correctness is non-negotiable)

  3. FORK RESOLUTION (from uv fork-based resolver):
     When verdicts are genuinely contradictory:
       Fork A: Apply verifier's recommendation
       Fork B: Apply reviewer's recommendation
       Run verification on BOTH forks
       Accept the fork that passes verification
       If BOTH pass: accept verifier's (functional correctness wins)
       If NEITHER passes: escalate to human

  4. CONFLICT HISTORY TRACKING (from uv incompatibility store):
     Track which reviewer personas frequently conflict with verifier
     After 3+ conflicts from same persona:
       → Deprioritize that persona's BLOCK votes
       → "Persona {X} has conflicted 4 times — reducing weight to 0.2"
```

## 6. Cross-Phase DAG Validation (Gap #8)

> **Source:** turborepo `lib.rs` (validate_graph), oxc `no_cycle.rs`
> Pattern: Validate entire dependency chain before execution

```
BEFORE executing any phase, validate the phase DAG:

  1. BUILD PHASE GRAPH:
     nodes = all phases from VISION.md
     edges = phase dependencies (phase N depends on phase N-1's outputs)

  2. CHECK FOR CYCLES (Tarjan's SCC from turborepo):
     cycles = find_strongly_connected_components(graph)
     IF cycles found:
       → Report ALL cycles (not just the first one)
       → For each cycle, suggest cut points:
         "Phase 3 → Phase 5 → Phase 3 creates a cycle.
          Break by: removing Phase 5's dependency on Phase 3,
          OR removing Phase 3's dependency on Phase 5."
       → STOP — do not execute with circular dependencies

  3. CHECK DEPENDENCY AVAILABILITY:
     FOR each phase in topological order:
       FOR each dependency of this phase:
         IF dependency.status != "complete":
           → FLAG: "Phase {N} depends on Phase {M} which is not complete"
           → IF dependency is in current execution range: reorder
           → IF dependency is outside range: BLOCK with explanation

  4. VALIDATE CONTRACTS:
     FOR each phase boundary (N → N+1):
       outputs_N = phase N's "provides" from BLUEPRINT frontmatter
       inputs_N1 = phase N+1's "requires" from BLUEPRINT frontmatter

       missing = inputs_N1 - outputs_N
       IF missing:
         → FLAG: "Phase {N+1} requires {missing} but Phase {N} doesn't provide it"
         → This is a PLANNING gap — route back to planner
```

## 7. Shared-State Conflict Prevention (Gap #1)

> **Source:** turborepo Walker+Mutex, lazygit AsyncHandler ID ordering
> Pattern: Centralized truth with stale-result rejection

```
ENHANCED .shared-state.json WITH VERSION COUNTER:

{
  "version": 42,
  "last_writer": "backend-agent",
  "last_write_at": "2026-03-08T10:35:00Z",
  "agents": { ... }
}

WRITE PROTOCOL (compare-and-swap):
  1. Read .shared-state.json → note version (e.g., 42)
  2. Make changes in memory
  3. Before writing: re-read file, check version still 42
     IF version changed (another agent wrote):
       → MERGE: combine your changes with theirs
       → Write with version = max(yours, theirs) + 1
     IF version same:
       → Write with version = 43

  This prevents the "last writer wins" data loss problem.

STALE RESULT REJECTION (from lazygit AsyncHandler):
  NOTE: Not yet wired into Dominion Flow commands — tracked for future implementation.
  Pattern preserved here as reference for when multi-session coordination is added.

  Each agent result has a monotonic request_id
  Orchestrator tracks last_processed_id per agent
  IF result.request_id < last_processed_id:
    → Reject (stale result from earlier execution)
    → "Ignoring stale result from {agent} (id {old} < {current})"
```

## 8. Agent Communication Protocol (Gap #10)

> **Source:** bun BundleThread+Waker, mise channel-based dispatch
> Pattern: Message-passing between agents via shared message queue

```
AGENT MESSAGE TYPES:
  CLAIM:      "I am taking ownership of task {id}"
  COMPLETE:   "Task {id} is done. Summary: {text}"
  BLOCKED:    "I cannot proceed. Reason: {text}. Need: {what}"
  DISCOVERY:  "Found something other agents should know: {text}"
  CONFLICT:   "I need to modify {file} but {other_agent} owns it"
  HANDOFF:    "Transferring task {id} to {target_agent}. Reason: {text}"

MESSAGE QUEUE (append-only file):
  .planning/.agent-messages.jsonl

  Each line is a JSON message:
  {"type":"CLAIM","agent":"backend","task":"03-01-task-1","timestamp":"..."}
  {"type":"DISCOVERY","agent":"backend","data":"API uses camelCase not snake_case","timestamp":"..."}
  {"type":"COMPLETE","agent":"backend","task":"03-01-task-1","summary":"Added auth middleware","timestamp":"..."}

READING PROTOCOL:
  - Agents read new messages since their last read (track line offset)
  - DISCOVERY messages inform all agents' playbooks
  - CONFLICT messages trigger orchestrator intervention
  - BLOCKED messages may unblock when another agent COMPLETEs a dependency

WHY JSONL (not JSON):
  - Append-only = no write conflicts (multiple agents can append simultaneously)
  - Line-based = easy to read incrementally (tail -n +{offset})
  - No parse failures from concurrent writes (each line is independent)
```

## When to Use

- Multi-task execution with 2+ parallel agents (SUBAGENT or SWARM mode)
- Any phase with 3+ tasks where error cascade is a risk
- Long-running autonomous sessions (fire-autonomous)
- Cross-phase validation before autonomous execution

## When NOT to Use

- Single-task phases (overhead exceeds benefit)
- SEQUENTIAL mode with no parallelism
- Simple bug fixes where only one agent is involved

## Must Do

- Classify errors by category BEFORE deciding intervention
- Bound delegation with semaphore (max 4 concurrent agents)
- Track task ownership in shared-state.json
- Return structured envelope from every agent
- Validate phase DAG before execution
- Use JSONL for agent messages (append-only, no conflicts)

## Must Not Do

- Do not let one agent's panic crash sibling agents
- Do not spawn unlimited sub-agents (semaphore enforces bounds)
- Do not retry ARCHITECTURE errors locally (escalate to planner)
- Do not transfer a task more than twice (toxic task → escalate)
- Do not ignore cumulative warnings (10+ warnings = systemic issue)

## Related Skills

- [ALAS_STATEFUL_EXECUTION](./ALAS_STATEFUL_EXECUTION.md) — checkpoint/restore for token-efficient mode
- [CIRCUIT_BREAKER_INTELLIGENCE](./CIRCUIT_BREAKER_INTELLIGENCE.md) — stuck-state classification feeds error routing
- [CONTEXT_ROTATION](./CONTEXT_ROTATION.md) — fresh-eyes pattern for FIXATION-type errors

## References

- turborepo: `crates/turborepo-engine/src/execute.rs` — semaphore bounding, Walker+Mutex
- mise: `src/task/task_scheduler.rs` — full scheduler with graph+channels+semaphore
- biome: `crates/biome_cli/src/runner/handler.rs` — catch_unwind isolation
- oxc: `crates/oxc_diagnostics/src/service.rs` — MPSC diagnostic service, max_warnings
- ruff: `crates/ruff/src/commands/check.rs` — parallel fold/reduce error accumulation
- uv: `crates/uv-resolver/src/pubgrub/priority.rs` — multi-priority conflict resolution
- lazygit: `pkg/tasks/async_handler.go` — stale result rejection via ID ordering
- bun: `src/bundler/BundleThread.zig` — dedicated worker with waker pattern
