---
name: git-worktrees-parallel
category: methodology
version: 1.0.0
contributed: 2026-03-04
contributor: global
last_updated: 2026-03-04
tags: [git, worktrees, parallel, agents, isolation, productivity, boris-cherny]
difficulty: easy
scope: general
---

# Git Worktrees — Parallel Claude Sessions

## Why This Matters

> "Do more in parallel. Spin up 3–5 git worktrees at once, each running its own Claude session in parallel. It's the **single biggest productivity unlock**, and the top tip from the team."
> — **Boris Cherny, creator of Claude Code**

Anthropic built native `--worktree` support directly into Claude Code CLI because of this. It's not optional best practice — it's how the Claude Code team itself works.

**The problem without worktrees:** One Claude session works on one branch. Any parallel work means stashing, switching, or risking conflicts between tasks.

**The solution:** Each task gets its own isolated working directory + branch. Sessions never interfere. Work in parallel by default.

## When to Use Worktrees

Use a worktree for any task that:
- Takes more than a few minutes
- Involves more than one or two file changes
- Could conflict with other in-progress work
- Is independent enough to run alongside another task

**Default to worktrees for every non-trivial feature or bugfix.**

## Core Commands

### Start Claude in a Worktree (CLI)

```bash
# Named worktree — name becomes directory and branch name
claude --worktree feature-auth
claude -w bugfix-payment-webhook

# Auto-named (Claude generates a random name)
claude --worktree
```

Worktrees are created at: `<repo>/.claude/worktrees/<name>/`
Branch created: `worktree-<name>`

### In-session Worktree Creation

Tell Claude during an active session:
```
> work in a worktree
> start a worktree named auth-refactor
```

Claude creates and switches to it automatically.

### Name Your Sessions

Name sessions early so you can resume them later:
```
> /rename auth-refactor
```

Resume later:
```bash
claude --resume auth-refactor
```

### Add to .gitignore (one-time setup)

```bash
echo ".claude/worktrees/" >> .gitignore
git add .gitignore && git commit -m "chore: ignore Claude worktrees"
```

Prevents worktree contents appearing as untracked files in the main repo.

## Running 3–5 Sessions in Parallel

```bash
# Terminal 1 — new auth feature
claude --worktree feature-oauth

# Terminal 2 — bug fix in parallel
claude --worktree bugfix-stripe-webhook

# Terminal 3 — UI polish
claude --worktree ui-dashboard-v2

# Terminal 4 — analysis/investigation (read-only)
claude --worktree analysis
```

Each Claude has its own branch, its own files. No conflicts. While one finishes, you're reviewing another.

Some teams create shell aliases (`za`, `zb`, `zc`) to hop between sessions in one keystroke. A dedicated `analysis` worktree for log reading and investigation is a common pattern.

## Subagent Worktree Isolation

When Claude spawns subagents, each can run in its own worktree:

### In the Agent Tool (for orchestrators)

```json
{
  "isolation": "worktree"
}
```

Each subagent gets its own worktree that is automatically cleaned up when the subagent finishes without changes.

### In Custom Subagent Frontmatter (.claude/agents/)

```yaml
---
name: feature-builder
description: Builds new features in isolation
isolation: worktree
---
```

### Tell Claude to Use Worktrees for Its Agents

```
> use worktrees for your agents
> spawn agents with worktree isolation
```

## Cleanup Behavior

Claude handles cleanup automatically on session exit:

| Situation | What Happens |
|-----------|-------------|
| No changes made | Worktree and branch removed automatically |
| Changes or commits exist | Claude prompts: keep or remove? |
| Keep | Directory and branch preserved — resume later |
| Remove | Worktree deleted, branch deleted, uncommitted changes lost |

### Manual Cleanup

```bash
git worktree list                          # see all active worktrees
git worktree remove .claude/worktrees/auth # remove specific one
```

## Plan Before Parallelizing

Before spinning up multiple agents:
1. **Identify independent tasks** — if Task B depends on Task A's output, they can't truly run in parallel
2. **Separate concerns** — frontend/backend, feature/tests, main feature/docs
3. **Plan then execute** — one Claude in plan mode drafts; another reviews; then execute in worktrees

Pattern:
```
> /plan — analyze the feature and identify 3 independent subtasks
```

Then spin up 3 worktrees, one per subtask.

## Integration with Existing Flows

### dominion-flow / power-flow / fire-flow

| Flow Command | Worktree Behavior |
|-------------|-----------------|
| `/fire-3-execute`, `/power-3-execute` | Start a worktree per wave/phase task |
| `/fire-1a-new`, `/power-1-new` | Set up `.gitignore` for `.claude/worktrees/` on project init |
| Subagent spawning (`dispatching-parallel-agents`) | Always use `isolation: "worktree"` for parallel agents |
| `/fire-5-handoff`, `/power-5-handoff` | Note active worktrees in handoff so next session can resume |
| `/fire-6-resume`, `/power-6-resume` | Check for open worktrees, resume named sessions |

### On Project Init

Any new project should immediately:
1. Add `.claude/worktrees/` to `.gitignore`
2. Set up shell aliases for worktree sessions (optional but fast)
3. Note worktree convention in CLAUDE.md

Add to CLAUDE.md:
```markdown
## Worktrees

All feature work runs in worktrees:  `.claude/worktrees/` (gitignored)
Start: `claude --worktree <feature-name>`
```

## Boris Cherny's Full Tips (Relevant Excerpts)

1. **Do more in parallel** — 3-5 worktrees, each its own Claude session. Single biggest unlock.
2. **Plan then execute** — Plan mode (read-only) first, then execute in worktrees. One Claude drafts the plan, another reviews it as "staff engineer."
3. **CLAUDE.md as living rules** — After correcting Claude, ask it to update CLAUDE.md so the mistake doesn't recur.
4. **Subagents for clean context** — Offload subtasks to subagents; keep main context clean.
5. **Dedicated analysis worktree** — One permanent worktree just for reading logs and investigating.

## Quick Reference

```bash
# Start Claude in new isolated worktree
claude --worktree my-feature

# Auto-named worktree
claude -w

# Resume a named session later
claude --resume my-feature

# See all active worktrees
git worktree list

# Clean up manually
git worktree remove .claude/worktrees/my-feature
```

## Common Mistakes

- **Working in main without a worktree** — every non-trivial task should have its own worktree
- **Forgetting `.claude/worktrees/` in .gitignore** — adds noise to `git status`
- **Not naming sessions** — "what was that auth session called?" — always `/rename` early
- **Running dependent tasks in parallel** — if B needs A's output, they can't be parallel; sequence them
- **Skipping cleanup** — old worktrees accumulate; run `git worktree list` periodically

## Sources

- Boris Cherny, creator of Claude Code: [Threads tip #1](https://www.threads.com/@boris_cherny/post/DUMZsVuksVv)
- Boris Cherny on built-in worktree support: [X announcement](https://x.com/bcherny/status/2025007393290272904)
- Anthropic official docs: [Common Workflows — Git Worktrees](https://code.claude.com/docs/en/common-workflows)
