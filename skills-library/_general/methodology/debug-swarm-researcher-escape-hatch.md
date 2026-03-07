---
name: debug-swarm-researcher-escape-hatch
category: methodology
version: 1.0.0
contributed: 2026-03-04
contributor: dominion-flow-v2
last_updated: 2026-03-04
tags: [debugging, swarm, multi-agent, escape-hatch, researcher, blocked, orchestration, autonomous-loop]
difficulty: hard
usage_count: 0
success_rate: 100
---

# Debug Swarm Researcher Escape Hatch

## Problem

Multi-agent debug swarms run parallel agents attacking the same bug from different hypotheses. When every hypothesis fails — every agent returns BLOCKED — the orchestrator is stuck. Spinning up identical agents produces identical failures. Halting loses all session context.

**Symptoms:**
- All swarm agents return `{status:"BLOCKED", issue, attempts_made[], error_context}` after N iterations
- No remaining hypotheses to test
- Loop stagnation: circuit breaker fires (`CB_STAGNATION >= limit`)
- Problem requires external knowledge: prior art, community solution, docs deep-dive

**The core trap:** You can't debug your way out of a knowledge gap. The swarm needs new information before it can make progress.

## Solution Pattern

When the swarm hits a collective wall, **escape the debug loop entirely** and spawn a dedicated researcher agent. The researcher searches external sources (skills library, MCP servers, WebSearch, GitHub) and writes structured findings to a persistent file. The findings file is then injected into the next swarm iteration as first-class context.

### The Three-Layer Escape

```
Layer 1: SWARM AGENTS (parallel per hypothesis)
  ↓ All return BLOCKED
Layer 2: ESCAPE TRIGGER (orchestrator detects collective BLOCKED)
  ↓ Spawns fire-researcher instead of re-trying swarm
Layer 3: RESEARCHER (skills lib + MCP + WebSearch + GitHub)
  ↓ Writes .planning/research/YYYY-MM-DD-{slug}.md
  ↓ Returns research summary to orchestrator
Layer 1 again: NEW SWARM AGENTS (with research injected as context)
  ↓ Fresh hypotheses informed by external knowledge
```

**Key insight:** The escape does NOT count as a swarm iteration. The loop counter
stays constant. The researcher is outside the iteration budget.

### BLOCKED Agent Response Contract

Swarm agents signal a wall using a structured response:

```json
{
  "status": "BLOCKED",
  "issue": "Cannot determine why X fails — tried Y and Z",
  "attempts_made": [
    "Checked env variable binding — correct",
    "Added console.log to line 47 — never fires",
    "Tried disabling auth middleware — same result"
  ],
  "error_context": {
    "error": "Cannot read properties of undefined (reading 'id')",
    "file": "src/auth/middleware.ts",
    "line": 23,
    "stack": "..."
  },
  "files_checked": ["src/auth/middleware.ts", "src/routes/users.ts"]
}
```

The orchestrator collects all BLOCKED responses and synthesizes a research brief.

### Orchestrator Escape Logic

```python
def check_escape_condition(swarm_results):
    blocked_count = sum(1 for r in swarm_results if r["status"] == "BLOCKED")
    if blocked_count == len(swarm_results):
        # All agents blocked — trigger escape hatch
        return True
    return False

def build_research_brief(blocked_responses):
    # Synthesize what the swarm tried and where it's stuck
    all_attempts = [a for r in blocked_responses for a in r["attempts_made"]]
    error_patterns = [r["error_context"] for r in blocked_responses]
    return {
        "problem_summary": "...",
        "attempted_approaches": all_attempts,
        "error_signatures": error_patterns,
        "research_queries": [
            "Cannot read properties undefined middleware chain express",
            "JWT auth middleware undefined user id request context"
        ]
    }
```

### Researcher Sources (priority order)

```
1. Skills library search   — Has this been solved before in our patterns?
2. context7 MCP server     — Framework/library official docs
3. WebSearch               — Community solutions, Stack Overflow, GitHub Issues
4. GitHub code search      — Real-world implementations of the pattern
5. Episodic memory search  — Did WE solve a similar issue in a past session?
```

### Research Output Format

Researcher writes to `.planning/research/YYYY-MM-DD-{slug}.md`:

```markdown
# Research: {problem title}
**Date:** YYYY-MM-DD
**Trigger:** Debug swarm collective BLOCKED — N agents, N attempts

## Root Cause Hypothesis (from research)
[What the researcher found that the swarm was missing]

## Solution Approach
[Concrete steps to fix based on external sources]

## Code Reference
```[language]
// From: [source URL or skill name]
[relevant code snippet]
```

## Sources
- [Source 1 with URL]
- [Source 2 with URL]

## Re-injection Prompt
[Ready-to-use context block for injecting into next swarm iteration]
```

### Re-injection Into Next Swarm Iteration

After researcher completes, the orchestrator spawns a fresh swarm with the research pre-loaded:

```
CONTEXT FROM PREVIOUS SWARM + RESEARCHER:

The debug swarm tried N approaches and was blocked. A researcher agent
investigated and found:

[Research summary — from .planning/research/YYYY-MM-DD-{slug}.md]

Known dead ends (do NOT retry):
- [attempt 1]
- [attempt 2]

New hypotheses to test based on research:
- [fresh hypothesis 1 from external sources]
- [fresh hypothesis 2]
```

## Code Example

```markdown
# fire-debug.md — Swarm Orchestrator (key escape section)

## Swarm Mode Orchestrator

```pseudocode
results = await Promise.all(swarm_agents.map(agent => agent.run()))

if results.every(r => r.status === "BLOCKED"):
  # Escape hatch: all agents blocked
  brief = build_research_brief(results)

  research = await spawn_agent(
    "fire-researcher",
    {
      query: brief.problem_summary,
      search_sources: ["skills-library", "context7-mcp", "web-search", "github"],
      write_to: f".planning/research/{today}-{slug}.md"
    }
  )

  # Re-spawn swarm with research context (doesn't count as iteration)
  new_swarm = spawn_swarm(hypotheses=research.new_hypotheses, context=research)
  results = await new_swarm.run()
```
```

## Implementation Steps

1. Define BLOCKED response contract in swarm agent instructions (the JSON shape above)
2. Implement `check_escape_condition()` in orchestrator — triggers when ALL agents blocked
3. Implement `build_research_brief()` — synthesizes blocked responses into research queries
4. Spawn `fire-researcher` (or equivalent) with the brief + write path
5. Researcher writes structured `.planning/research/YYYY-MM-DD-{slug}.md`
6. Orchestrator reads research, builds re-injection context block
7. Spawn fresh swarm iteration with research pre-loaded as context

## When to Use

- Multi-agent debug swarm where ALL agents return BLOCKED simultaneously
- Problem requires external knowledge (docs, prior art, community solutions)
- Stagnation circuit breaker has fired due to repeated identical failures
- The error pattern is unfamiliar — novel framework, obscure edge case, known bug in dependency
- You want to preserve research findings across sessions (write to disk, not just memory)

## When NOT to Use

- Single-agent debugging (use systematic-debugging skill instead)
- Only 1-2 agents blocked (not all) — remaining agents may still find a path
- Problem is clearly a typo or obvious logic error (don't need external research)
- Swarm has only run 1 iteration (premature escape — try more hypotheses first)
- Time-critical hotfix where research delay is unacceptable

## Common Mistakes

- **Counting escape as an iteration** — the researcher escape is outside the iteration budget; resetting the loop counter erases progress tracking
- **Vague research brief** — synthesize specific error signatures and exact code context, not just "it doesn't work". The researcher is only as good as the brief
- **Not writing research to disk** — if findings stay in memory only, they're lost on session compaction. Always write `.planning/research/*.md`
- **Re-injecting all research** — only inject the relevant new hypotheses, not the full research doc. Context window is precious
- **Escaping too early** — require collective BLOCKED (all agents, not just some). Partial blocking means other hypotheses are still viable

## Exit Codes (when used in shell loop)

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Bug fixed after research re-injection | Proceed to verify |
| 2 | Escape triggered, researcher found nothing | Human investigation required |
| 3 | Research found solution, fix not implemented | Apply research manually |

## Related Skills

- [shell-autonomous-loop-fixplan](_general/methodology/shell-autonomous-loop-fixplan.md) — shell-level loop with BLOCKED signal (exit code 2)
- [autonomous-multi-phase-build](_general/methodology/autonomous-multi-phase-build.md) — phase-level orchestration
- [systematic-debugging] — single-agent debugging pattern

## References

- Implemented in: `fire-flow/commands/fire-debug.md` (--swarm mode section)
- Inspired by: RLHF researcher escalation patterns + bmalph/Ralph BLOCKED exit
- Contributed from: dominion-flow-v2 build session 2026-03-04
