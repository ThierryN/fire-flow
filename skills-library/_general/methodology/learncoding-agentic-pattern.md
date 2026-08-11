---
name: learncoding-agentic-pattern
category: methodology
version: 1.0.0
contributed: 2026-03-04
contributor: dominion-flow-v2
last_updated: 2026-03-04
tags: [learning, walkthrough, cognitive-debt, simon-willison, agentic-engineering, linear-walkthrough, anti-vibe-coding]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Learncoding: Agentic Engineering Walkthrough Pattern

## Problem

Vibe coding (accepting all AI output without understanding) creates **cognitive debt**:
you build things you can't explain, can't debug, and can't confidently extend.
Simon Willison's definition: "If you don't understand the code, your only recourse is
to ask AI to fix it — like paying off credit card debt with another credit card."

Symptoms:
- You can't explain a file you "wrote" with AI
- Bugs require asking AI to fix rather than reasoning yourself
- Architecture decisions feel opaque or arbitrary
- You'd fail a code review on your own code

## Solution Pattern

Apply Simon Willison's **Linear Walkthrough** pattern:

> "Give me a linear walkthrough of the code that explains how it all works in detail."

Combined with his **Hoard Things You Know** principle: once you understand something,
capture it. The walkthrough document becomes your hoard entry.

### The Three Questions Per File

For every file in the walkthrough, answer:
1. **WHAT** — what does this file do for the user of the application?
2. **WHY** — why is it written this way, not the obvious alternative?
3. **PATTERN** — which design pattern is being used and what is its name?

### The Showboat Extraction Rule

Never paraphrase code from memory. Always extract real snippets using shell tools:

```bash
# Extract real code — prevents LLM hallucination of "close but wrong" code
cat src/auth/middleware.ts  # whole file
sed -n '/^export function/,/^}/p' src/auth.ts  # specific function
grep -A 20 "class UserService" src/services/user.ts  # class body
```

This is the core principle from Willison's Showboat tool — agents that
copy code from memory will introduce subtle errors. Shell extraction is exact.

## Code Example

```bash
# The four-step learncoding workflow
# 1. Load source
gh api repos/user/repo/git/trees/HEAD?recursive=1 \
  --jq '.tree[] | select(.type=="blob") | .path' > files.txt

# 2. Detect entry point
cat package.json | jq -r '.main // .scripts.start'

# 3. Extract real snippet (Showboat principle)
gh api repos/user/repo/contents/src/index.ts \
  --jq '.content' | base64 -d

# 4. Walk imports breadth-first from entry point
grep -E "^import.*from ['\"]\./" src/index.ts
```

## When to Use

- Learning a new codebase before contributing
- Recreating a GitHub project from scratch to understand it deeply
- Onboarding to a new tech stack (walk an example project)
- After AI generates a multi-file feature — walk it before committing
- Teaching someone else a codebase
- Any time you feel "I accepted this but I don't fully get it"

## When NOT to Use

- You already understand the codebase well
- Single-file scripts (just read them directly)
- Generated boilerplate with no novel logic
- Time-pressured hotfixes (use a quick `/fire-debug` instead)

## Willison's Golden Rule

> "I won't commit any code to my repository if I couldn't explain exactly
> what it does to somebody else."

Apply this as a pre-commit gate: before every `git commit`, ask yourself if you
could explain the diff to a colleague. If not, run a walkthrough first.

## Related Patterns

- Simon Willison's guide: simonwillison.net/guides/agentic-engineering-patterns/linear-walkthroughs/
- Interactive Explanations: simonwillison.net/guides/agentic-engineering-patterns/interactive-explanations/
- Showboat tool: github.com/simonw/showboat

## References

- [Linear Walkthroughs — Agentic Engineering Patterns](https://simonwillison.net/guides/agentic-engineering-patterns/linear-walkthroughs/)
- [Cognitive Debt](https://simonwillison.net/2026/Feb/15/cognitive-debt/)
- [Not all AI-assisted programming is vibe coding](https://simonwillison.net/2025/Mar/19/vibe-coding/)
- [Showboat GitHub](https://github.com/simonw/showboat)
- Contributed from: dominion-flow-v2 learncoding session 2026-03-04
