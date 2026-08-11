---
name: session-handoff-workflow
category: awesome-workflows
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
last_updated: 2026-02-24
tags: [handoff, continuity, warrior, session, memory]
difficulty: easy
---

# Session Handoff Workflow

## Problem

AI agents are born fresh every session. Without structured handoffs, each session starts from zero — the new agent reads code but has no context about WHY decisions were made, what was tried and failed, or what's coming next. This wastes 10-30 minutes per session on rediscovery.

## Solution Pattern

WARRIOR 7-step handoff format that captures everything a fresh agent needs to continue seamlessly. Named for the mnemonic: **W**ork, **A**ssessment, **R**esources, **R**eadiness, **I**ssues, **O**utlook, **R**eferences.

## Workflow Steps

### 1. Create Handoff at Session End

At the end of every working session, create a WARRIOR handoff:

```markdown
# WARRIOR Handoff: {Project} — {Phase Description}

**Session:** YYYY-MM-DD
**Phase:** {current phase}
**Status:** {COMPLETE | IN PROGRESS | BLOCKED}

## W — Work Completed
- What was done this session
- Files modified (with paths)
- Commits made (with hashes)

## A — Assessment
- Current project health
- Technical debt introduced or resolved
- Confidence level in the work

## R — Resources
- Key file paths
- URLs needed for next steps
- Credentials or config locations

## R — Readiness
- What's ready for the next session
- What's blocked and needs resolution

## I — Issues
- Known bugs or problems
- Decisions that need user input
- Risks identified

## O — Outlook
- What the next session should do
- Priority order of remaining work
- Estimated complexity

## R — References
- Commit hashes
- Report locations
- External documentation links
```

### 2. Save to Handoff Directory

```
~/.claude/warrior-handoffs/{project}_{date}.md
```

### 3. Start Next Session with Handoff

The next agent reads the handoff BEFORE doing anything:
1. Read the most recent handoff for the project
2. Verify the Work section against actual file state
3. Check Issues for anything that needs immediate attention
4. Follow Outlook for session priorities

### 4. Predict-Then-Read (SDFT Protocol)

For deeper continuity, the fresh agent should:
1. **Predict** what the handoff will say based on project context
2. **Read** the actual handoff
3. **Note surprises** — gaps between prediction and reality are learning signals
4. Write reflections on any surprises

## Handoff Quality Checklist

- [ ] All modified files listed with full paths
- [ ] All commit hashes included
- [ ] Issues section is honest (don't hide problems)
- [ ] Outlook gives clear priorities (not just a wishlist)
- [ ] Resources section has everything needed to continue
- [ ] No real credentials in the handoff (use placeholders)

## When to Use

- End of EVERY working session (non-negotiable)
- When switching between projects
- Before taking a break longer than a few hours
- After completing a milestone or phase

## When NOT to Use

- Mid-session (use `/compact` instead for context preservation)
- For trivial interactions (quick questions, single-file fixes)

## Related Skills

- [methodology/](../methodology/) — Process standards
- [CREDENTIAL-SECURITY-WORKFLOW.md](./CREDENTIAL-SECURITY-WORKFLOW.md) — Ensure handoffs don't contain secrets
