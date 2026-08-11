# Agent Teams Guide — Multi-Reviewer Coordination

> Use Claude Code's experimental Agent Teams feature to spawn competing reviewers that discuss findings with each other.

**When to use:** When you want deeper code review than a single reviewer provides — especially for security-critical, performance-sensitive, or architecturally complex changes.
**Prerequisites:** Claude Code v2.0.64+ with experimental teams flag enabled

---

## Setup

Enable the experimental feature flag:

```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

This unlocks these tools in Claude Code:
- `TeamCreate` — spawn a teammate agent
- `TaskCreate` — create tasks with dependencies
- `TaskUpdate` — update task status
- `TaskList` — view all tasks
- `SendMessage` — inbox-based inter-agent messaging

---

## Pattern 1: Competing Reviewers

Spawn specialized reviewers that challenge each other's findings:

```
Create three reviewer teammates:

Teammate 1: "security-reviewer"
  Focus: Authentication bypass, injection attacks, secret exposure, CSRF,
         input validation, authorization checks
  Tools: Read, Grep, Glob (read-only)

Teammate 2: "performance-reviewer"
  Focus: N+1 queries, missing indexes, unnecessary re-renders, memory leaks,
         bundle size impact, caching opportunities
  Tools: Read, Grep, Glob, Bash (for running benchmarks)

Teammate 3: "architecture-reviewer"
  Focus: Coupling, dependency direction, abstraction levels, API design,
         separation of concerns, DRY violations
  Tools: Read, Grep, Glob

Each reviews the files in [phase directory].
When done, each sends their verdict to the lead via SendMessage.
```

### Anti-Conformity (FREE-MAD Pattern)

To prevent reviewers from rubber-stamping each other, include in each teammate's prompt:

```
IMPORTANT: You are an INDEPENDENT reviewer. If you disagree with another
reviewer's findings, SAY SO and explain why. Your job is to find issues
the others missed, not to agree with them.

After completing your review, read other reviewers' findings via inbox.
If you agree: acknowledge and move on.
If you disagree: send a rebuttal message explaining your reasoning.
The lead will synthesize all perspectives.
```

---

## Pattern 2: Research Swarm

Spawn parallel researchers for `/fire-research`:

```
Create four researcher teammates:

Teammate 1: "academic-researcher"
  Task: Search arXiv, ACL, NeurIPS for papers on [topic]

Teammate 2: "community-researcher"
  Task: Search blogs, GitHub, docs from AI coding tools

Teammate 3: "gap-analyst"
  Task: Read internal workflow files, find gaps

Teammate 4: "failure-miner"
  Task: Search past handoffs for recurring failures

When all complete, lead synthesizes findings.
```

---

## Pattern 3: Parallel Executors

For large phases with independent plans:

```
Create executor teammates (one per plan):

Teammate 1: "backend-executor" — Plan 03-01 (API endpoints)
Teammate 2: "frontend-executor" — Plan 03-02 (UI components)
Teammate 3: "test-executor" — Plan 03-03 (test suite)

Dependencies:
  - test-executor waits for backend-executor AND frontend-executor
  - backend and frontend run in parallel

Each works in its own git worktree (isolation: worktree).
```

---

## Verdict Synthesis (Lead Agent)

After all teammates return:

```
1. Collect all verdicts from inbox messages
2. Parse structured verdict envelopes (REVIEWER_VERDICT_START/END)
3. Aggregate:
   - UNANIMOUS APPROVE → APPROVE
   - ANY BLOCK → BLOCK (with specific findings)
   - MIXED → APPROVE_WITH_FIXES (merge all issues)
4. Deduplicate findings (same file:line from multiple reviewers = higher confidence)
5. Resolve conflicts (reviewer A says "add abstraction", B says "keep simple"):
   - Apply the simpler solution unless the complex one has measurable benefit
6. Present consolidated verdict
```

---

## Cost Considerations

| Mode | Cost | Quality | Speed |
|------|------|---------|-------|
| Single reviewer (current) | 1x | Good | Fast |
| 3 specialized reviewers | 3x | Better (catches more) | Same (parallel) |
| 3 reviewers + debate | 4-5x | Best (challenges findings) | Slower |

**Recommendation:** Use single reviewer for routine changes. Use teams for:
- Security-critical code (payment, auth, data handling)
- Architectural decisions (new patterns, major refactors)
- Production deployment gates

---

## Limitations (Experimental)

- API may change — teams feature is in research preview
- Requires tmux for terminal multiplexing on some platforms
- Token cost scales linearly with teammate count
- Teammates share a task list but NOT context (each has fresh window)
- Windows support may require WSL for tmux

---

## Sources

- Claude Code Docs: "Orchestrate teams of Claude Code sessions" (2026)
- Anthropic: "How we built our multi-agent research system" (2026)
- FREE-MAD paper: Anti-conformity debate (+13-16.5% reasoning accuracy)
- ccswarm (nwiizo, GitHub): Multi-agent orchestration in Rust
- claudefa.st: "Claude Code Agent Teams: The Complete Guide 2026"
