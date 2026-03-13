# Auto-Reviewer Subagent Pattern

> Automatically spawn a read-only reviewer agent without manual copy-paste. Uses Claude Code's native `.claude/agents/` subagent system with worktree isolation.

**When to use:** Any time code review is needed during a Dominion Flow workflow — especially in `/fire-3-execute` (post-breath review), `/fire-autonomous` (auto-review gate), or when a developer wants independent code review without leaving their session.

---

## The Problem

Currently, `/fire-7-review` runs 16 reviewer personas in the SAME Claude Code instance. To get a truly independent review (separate context window, no confirmation bias), users must:
1. Open a new terminal
2. Copy-paste the review prompt
3. Wait for results
4. Manually collect and deduplicate findings

This friction means reviews get skipped.

---

## Solution: Custom Subagent Files

### Phase 1: Read-Only Reviewer (Recommended — works today)

Create a markdown file at `.claude/agents/fire-code-reviewer.md` in your project:

```yaml
---
name: fire-code-reviewer
description: Independent code reviewer that analyzes code for bugs, security issues, and quality problems. Returns structured verdicts.
tools:
  - Read
  - Grep
  - Glob
  - LS
model: sonnet
---

You are a senior code reviewer performing an independent review. You have NO context about what the developer intended — review the code purely on its merits.

## Review Criteria

1. **Security** — SQL injection, XSS, CSRF, auth bypass, secret exposure
2. **Correctness** — Logic errors, off-by-one, null handling, race conditions
3. **Error Handling** — Missing try/catch, swallowed errors, no fallbacks
4. **Performance** — N+1 queries, unnecessary re-renders, missing indexes
5. **Maintainability** — Dead code, unclear naming, missing types

## Output Format

Return your verdict as a structured block:

VERDICT: APPROVE | APPROVE_WITH_FIXES | BLOCK
CONFIDENCE: 1-100
ISSUES_FOUND: N

### Critical Issues (must fix)
- [file:line] Description

### Major Issues (should fix)
- [file:line] Description

### Minor Issues (nice to fix)
- [file:line] Description

### Summary
One paragraph overall assessment.
```

### How to Invoke

From any Dominion Flow command, the executor or orchestrator says:

```
Use the fire-code-reviewer agent to review the files changed in this phase:
- src/routes/payment.ts
- src/controllers/checkout.ts
- src/middleware/auth.ts
```

Claude Code automatically routes this to the subagent, which runs in a separate context window with only Read/Grep/Glob tools (read-only).

---

### Phase 2: CLI Spawning (Fallback / CI Integration)

For CI/CD or when subagent routing doesn't trigger:

```bash
# Review a git diff
git diff main | claude -p "Review this diff for bugs, security issues, and code quality. Return a JSON verdict with: {verdict: APPROVE|BLOCK, confidence: 0-100, issues: [{severity, file, line, description}]}" --output-format json > /tmp/review-verdict.json

# Review specific files
claude -p "Review these files for security and correctness:
$(cat src/routes/payment.ts)
$(cat src/controllers/checkout.ts)
Return a structured verdict." --output-format json --model sonnet

# Parse verdict in parent session
cat /tmp/review-verdict.json | jq '.result[0].content[] | select(.type=="text") | .text'
```

Key flags:
- `-p` / `--print` — non-interactive mode, returns to stdout
- `--output-format json` — structured output for programmatic parsing
- `--model sonnet` — cheaper model for routine reviews
- `--dangerously-skip-permissions` — unattended execution (use carefully)

---

### Phase 3: Agent Teams (Multi-Reviewer)

Enable experimental agent teams for competing reviewers:

```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Then spawn specialized reviewers as teammates:

```
Create three reviewer teammates:

1. Security Reviewer — focus on auth bypass, injection, secret exposure
2. Performance Reviewer — focus on N+1 queries, memory leaks, bundle size
3. Architecture Reviewer — focus on coupling, abstraction, dependency direction

Each should review the files in src/routes/ and src/controllers/.
They can discuss findings with each other via inbox messages.
When all three are done, synthesize their verdicts into a final recommendation.
```

Teammates can:
- Talk to each other (not just back to parent)
- Challenge each other's findings
- Self-claim unassigned review tasks
- Coordinate via shared task list

---

## Integration Points

### In fire-3-execute.md (Post-Breath Review)

Add after each breath completes:

```markdown
### Step 3.7: Auto-Review Gate

After breath execution completes:

1. Spawn fire-code-reviewer subagent with the list of modified files
2. Wait for structured verdict
3. Route verdict:
   - APPROVE → proceed to next breath
   - APPROVE_WITH_FIXES → log fixes needed, proceed (non-blocking)
   - BLOCK → halt execution, present findings to developer

Note: In autonomous mode (--autonomous flag), BLOCK triggers auto-fix
cycle instead of halting.
```

### In fire-autonomous.md (Auto-Review)

The autonomous loop already has Step 3.3 (AUTO-VERIFY). Add parallel review:

```markdown
### Step 3.2.5: AUTO-REVIEW (parallel with verification)

Spawn fire-code-reviewer in background:
  - isolation: worktree
  - tools: Read, Grep, Glob (read-only)
  - model: sonnet (cost optimization)

Collect verdict when verification also completes.
Merge verdicts per Step 8.5 arbitration protocol.
```

---

## Verdict Aggregation

When multiple reviewers return verdicts:

```
IF any reviewer says BLOCK:
  final_verdict = BLOCK (unanimous APPROVE required for APPROVE)

IF all reviewers say APPROVE:
  final_verdict = APPROVE

IF mix of APPROVE and APPROVE_WITH_FIXES:
  final_verdict = APPROVE_WITH_FIXES
  aggregate all issues from all reviewers
  deduplicate by file:line (same issue from 2 reviewers = higher confidence)
```

---

## Sources

- Claude Code Docs: "Create custom subagents" (2026)
- Claude Code Docs: "Orchestrate teams of Claude Code sessions" (2026)
- Claude Code Docs: "CLI reference — non-interactive mode" (2026)
- Anthropic: "How we built our multi-agent research system" (2026)
- VoltAgent/awesome-claude-code-subagents (GitHub)
