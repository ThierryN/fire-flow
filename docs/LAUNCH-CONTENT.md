# Dominion Flow Launch Content — Three Platforms

Drafted: 2026-03-06
GitHub: https://github.com/ThierryN/fire-flow

---

## PLATFORM 1: Reddit r/ClaudeAI

### Research Notes

- r/ClaudeAI is active with Claude Code discussions; plugin posts perform well when they lead with a real problem and show the solution
- Reddit's 10% rule: no more than 10% of your posting activity should be self-promotion. Engage genuinely in comments before and after posting
- Successful plugin posts on r/ClaudeAI (like claude-mem's launch) lead with the pain point, show concrete examples, and invite feedback
- Composio's approach works: tech-first insights, subtle self-referencing, consistent community engagement
- Flair: Most likely "Productivity" or "Claude Code" or "Tools" — check the subreddit's current flair options before posting

### Best Time to Post

- Tuesday or Wednesday, 8-10 AM EST
- This catches the morning US East Coast crowd and European afternoon users

### Tips for Engagement

- Reply to every comment within the first 2 hours
- Ask a genuine question at the end to invite discussion
- Do NOT link-drop and leave — stay in the thread
- If there is a weekly "Show and Tell" or "Self-Promotion Saturday" thread, consider posting there first to establish good faith

---

### COMPLETE POST — Copy/Paste Ready

**Title:**

```
I built a Claude Code plugin that preserves workflow STATE between sessions, not just memory — Dominion Flow (free, MIT, 42 commands)
```

**Flair suggestion:** "Claude Code" or "Productivity" (check available flairs)

**Body:**

```
I've been using Claude Code daily for months, and the biggest problem I kept hitting wasn't that Claude forgot facts — it's that Claude forgot *where we were*.

Memory plugins are great at "I remember we discussed auth." But what I needed was "Auth is in Phase 2, Step 3. The plan is verified. The database migration is blocking the next task. Here's the 70-point checklist status."

That's a fundamentally different problem. So I built Dominion Flow.

## What it does

Dominion Flow is an orchestration plugin for Claude Code. It gives Claude a structured pipeline:

**Plan → Execute → Verify → Handoff → Resume**

The core differentiator is the WARRIOR Handoff Cycle. When you run `/fire-5-handoff`, Claude writes a comprehensive handoff document that captures:

- What phase you're in and what step you're on
- What's been verified and what's pending
- Active decisions and their rationale
- Blocking issues and their status
- The full project state (not just conversation history)

When you start a new session and run `/fire-6-resume`, Claude reads that handoff and picks up *exactly* where it left off. No re-explaining. No context loss. No "let me re-read your codebase."

## Other things it does

- **42 slash commands** organized into 7 tiers (planning, execution, verification, debugging, skills management, analytics, milestones)
- **Breath-based parallelism** — multiple tasks execute concurrently with safety checks
- **70-point WARRIOR verification checklist** — Claude verifies its own work before claiming it's done
- **Circuit breaker with Sabbath Rest** — if Claude gets stuck in a loop, execution pauses automatically instead of burning tokens
- **190+ reusable skills library** — proven patterns for auth, APIs, databases, etc.
- **`/fire-autonomous`** — full autopilot mode where Claude plans, executes, and verifies entire phases
- **`/fire-learncoding`** — a structured learning mode based on Simon Willison's Linear Walkthrough pattern (anti-vibe-coding). I haven't seen this in any other plugin
- **`/fire-security-scan`** — inspects your code, plugins, and MCP tools for prompt injection, PII harvesting, credential theft, and supply chain attacks
- **`/fire-loop`** — self-iterating execution with error classification and automatic recovery

## Memory plugins vs. Dominion Flow

| | Memory Plugins | Dominion Flow |
|---|---|---|
| Remembers facts | Yes | Yes (via handoffs) |
| Remembers workflow position | No | Yes |
| Knows what's verified vs. pending | No | Yes |
| Has a structured execution pipeline | No | Yes |
| Prevents stuck loops | No | Yes (circuit breaker) |
| Self-verifies work quality | No | Yes (70-point checklist) |

They're complementary, not competing. You can use both. But if you're building real projects across multiple sessions, the handoff cycle is what makes Claude feel like a teammate instead of a stranger you brief every morning.

## Install

```
git clone https://github.com/ThierryN/fire-flow.git
claude install-plugin ./fire-flow
```

Then restart Claude Code and type `/fire-0-orient` to verify it's working.

**Free. MIT license. Works on Mac, Linux, and Windows.**

GitHub: https://github.com/ThierryN/fire-flow

Happy to answer questions about the architecture or design decisions. What workflow pain points are you hitting with Claude Code?
```

---
---

## PLATFORM 2: Hacker News (Show HN)

### Research Notes

- Show HN rules: Must be something people can try. No landing pages, no fundraisers. Title starts with "Show HN:"
- The product must actually exist and be usable — Dominion Flow qualifies since it's installable from GitHub
- Drop all marketing language. HN readers are allergic to it. Use factual, direct language
- Post a top-level comment explaining the backstory and what's different
- Comments are a stronger ranking signal than upvotes — engagement matters more
- HN is skeptical of AI hype. Lead with the engineering, not the pitch
- Don't use your company/project name as your username

### Best Time to Post

- Wednesday, 9-11 AM Pacific Time (to catch US morning + European afternoon)
- Alternatively: Tuesday or Thursday same window
- Avoid weekends — lower traffic

### Tips for Engagement

- Post your backstory comment immediately after submitting
- Be prepared for skepticism — respond honestly and technically
- If someone asks "why not just use CLAUDE.md?" have a clear technical answer ready
- Do NOT ask anyone to upvote
- Stay in the thread for at least 3 hours

---

### COMPLETE POST — Copy/Paste Ready

**Title (in the URL submission field):**

```
Show HN: Dominion Flow – Workflow state preservation for Claude Code (42 commands, MIT)
```

**URL field:** `https://github.com/ThierryN/fire-flow`

**Leave the text field blank.** Post the following as your first comment immediately after submission:

---

**First comment (backstory):**

```
Hi HN, I built this over several months of daily Claude Code usage.

The problem: Claude Code has no memory between sessions. Memory plugins like claude-mem (12.9K stars) solve the fact-recall side — "we talked about auth before." But they don't preserve workflow state.

When I'm in the middle of a multi-phase project and start a new session, I don't just need Claude to remember facts. I need it to know:

- We're in Phase 2 of 5
- Step 3 of the current plan is in progress
- The database migration passed verification
- The API endpoint is blocking on a schema decision we made yesterday
- Here's the 70-point verification checklist status

That's what the WARRIOR Handoff Cycle does. `/fire-5-handoff` serializes the full project state into a structured document. `/fire-6-resume` restores it. Claude picks up exactly where it left off.

The rest of the plugin is a structured pipeline (Plan → Execute → Verify → Handoff) with:

- 42 slash commands in 7 tiers
- Breath-based parallel execution (multiple tasks run concurrently with safety checks)
- A 70-point verification checklist that Claude runs against its own work
- A circuit breaker ("Sabbath Rest") that pauses execution if Claude gets stuck in a retry loop
- 190+ reusable skills (auth patterns, API designs, database solutions, etc.)
- `/fire-autonomous` for full autopilot execution
- `/fire-learncoding` — a structured code learning mode based on Simon Willison's walkthrough pattern

The circuit breaker is worth explaining: Claude Code can get into loops where it tries the same failing approach repeatedly. The circuit breaker detects this pattern (error classification + retry counting) and forces a pause instead of burning tokens. When you resume with `/fire-loop-resume`, it tries a different approach.

Install:

    git clone https://github.com/ThierryN/fire-flow.git
    claude install-plugin ./fire-flow

MIT licensed. No external dependencies required (optional Qdrant integration for vector memory). Works on all platforms.

Interested in feedback on the architecture. The handoff format and the verification checklist are the parts I've iterated on the most.
```

---
---

## PLATFORM 3: Twitter/X

### Research Notes

- Short, punchy, demo-focused content works best
- Thread format: 5-8 tweets, first tweet must hook
- Boris Cherny's viral thread about his Claude Code setup got massive engagement by being specific and practical
- Visual content (screenshots, short screen recordings) dramatically increase engagement
- Tag relevant accounts: @AnthropicAI, @ClaudeCode if applicable
- Use 2-3 relevant hashtags, not more

### Best Time to Post

- Tuesday-Thursday, 9-11 AM EST
- Alternatively: 12-1 PM EST (lunch scroll)

### Tips for Engagement

- Record a 30-60 second screen recording showing the handoff → resume cycle in action
- Include a screenshot of the `/fire-dashboard` output
- Quote-tweet or reply to existing Claude Code discussions with the thread
- Pin the thread to your profile

---

### COMPLETE THREAD — Copy/Paste Ready

**Tweet 1 (Hook):**

```
I built an open-source Claude Code plugin with 42 slash commands.

But the one feature that changed everything: WARRIOR Handoffs.

Memory plugins remember facts. This preserves where you ARE — phase, step, what's verified, what's blocking.

Claude picks up exactly where it left off.

Thread:
```

**Tweet 2 (The Problem):**

```
The problem with Claude Code sessions:

You close the terminal. Open a new one. Claude has no idea what happened.

Memory plugins help: "We talked about auth."

But that's not enough. You need: "Auth is Phase 2, Step 3. Plan verified. DB migration blocking. Here's the checklist."

That's workflow state, not memory.
```

**Tweet 3 (The Solution):**

```
Dominion Flow gives Claude a pipeline:

Plan → Execute → Verify → Handoff → Resume

/fire-5-handoff writes a full state document
/fire-6-resume restores it in the next session

No re-explaining. No context loss. Claude becomes a teammate that keeps notes.
```

**Tweet 4 (The Numbers):**

```
What's in the box:

- 42 slash commands, 7 tiers
- 70-point verification checklist (Claude checks its own work)
- Breath-based parallel execution
- Circuit breaker — auto-pauses stuck loops instead of burning tokens
- 190+ reusable skills library
- /fire-autonomous for full autopilot
- /fire-learncoding for structured learning
```

**Tweet 5 (Circuit Breaker):**

```
The circuit breaker is my favorite feature.

Claude gets stuck in loops. Same error, same fix attempt, over and over.

The Sabbath Rest circuit breaker detects this, classifies the error, and forces a pause.

When you resume, it tries a DIFFERENT approach.

Saves hours of wasted tokens.
```

**Tweet 6 (Differentiator Table):**

```
Memory plugins vs. Dominion Flow:

Memory: remembers facts ✓
Dominion: remembers facts + workflow position + verification status + blocking issues + active decisions

They're complementary. Use both.

But if you build real projects across sessions, the handoff cycle is what you're missing.
```

**Tweet 7 (Install + CTA):**

```
Free. MIT license. Mac/Linux/Windows.

git clone https://github.com/ThierryN/fire-flow.git
claude install-plugin ./fire-flow

Then: /fire-0-orient

No sign-up. No API keys. Just install and go.

github.com/ThierryN/fire-flow

What workflow problems are you hitting with Claude Code?
```

**Hashtags for Tweet 1 or Tweet 7:**
```
#ClaudeCode #AI #OpenSource
```

**Accounts to tag (in Tweet 1 or as a reply):**
```
@AnthropicAI
```

---
---

## Pre-Launch Checklist

Before posting on any platform:

1. [ ] Verify the GitHub repo (https://github.com/ThierryN/fire-flow) is public and the README is polished
2. [ ] Confirm install instructions work fresh: `git clone` + `claude install-plugin` + `/fire-0-orient`
3. [ ] Test on a clean machine or ask someone else to try installing
4. [ ] Record a 60-second screen recording showing: `/fire-5-handoff` then close terminal, reopen, `/fire-6-resume` — show Claude picking up where it left off
5. [ ] Take a screenshot of `/fire-dashboard` output for Twitter visuals
6. [ ] On Reddit: make sure your account has recent non-promotional activity in r/ClaudeAI (comment on other posts first)
7. [ ] On HN: make sure your username is a personal name, not "dominion-flow" or "fire-flow"

## Posting Order

**Recommended sequence:**

1. **Reddit first** (Tuesday/Wednesday 8-10 AM EST) — most forgiving, gets early feedback, can iterate on messaging
2. **Twitter same day** (9-11 AM EST) — cross-reference the Reddit discussion in a reply
3. **Hacker News 1-2 days later** (Wednesday 9-11 AM PT) — use feedback from Reddit to refine the HN comment. HN is the hardest audience; you want your messaging sharp

## Anticipated Questions & Answers

**Q: How is this different from just using CLAUDE.md?**
A: CLAUDE.md is static instructions. It doesn't know what phase you're in, what's been verified, or what's blocking. The handoff is a dynamic state document that changes every session.

**Q: Does this work with claude-mem / other memory plugins?**
A: Yes, they're complementary. Memory plugins handle fact recall. Dominion Flow handles workflow state. Use both.

**Q: 42 commands seems like a lot. Is there a learning curve?**
A: You only need 7 to start (the core pipeline: new, discuss, plan, execute, verify, handoff, resume). Everything else is optional and unlocks as you need it.

**Q: Does this require any external services?**
A: No. It works out of the box. Optional Qdrant integration is available for vector-based memory search, but it's not required.

**Q: Why "WARRIOR"?**
A: It's an acronym for the verification checklist categories. The name stuck because the handoff cycle is about making Claude fight for quality, not just produce output.
