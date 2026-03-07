# /fire-cost — Token & Cost Intelligence

> Track context usage, estimate session costs, and trigger strategic compaction before hitting limits.

---

## Purpose

Provide real-time visibility into context window consumption and session costs. Prevents the silent failure mode where agents hit context limits mid-task with no recovery path.

> **Research basis (v10.1):** Spotify "Honk" Architecture (2024) — tiered context management reduces context-related failures by 40%. Google DeepMind "Cost-Aware Agent Planning" (NeurIPS 2024) — agents that track resource consumption make 31% fewer wasteful API calls.
> Applied: Added explicit context/cost monitoring as a first-class command.

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--detail` | No | Show per-file and per-agent breakdown |
| `--warn` | No | Only show if above 60% context usage |
| `--budget <amount>` | No | Set a session cost budget (e.g., `--budget $5.00`) |

---

## Process

<step number="1">
### Measure Current Context State

Assess the current session's context consumption:

**Context Window Tiers:**
| Tier | Usage | Status | Action |
|------|-------|--------|--------|
| GREEN | 0-50% | Healthy | No action needed |
| YELLOW | 50-70% | Caution | Consider compaction soon |
| ORANGE | 70-85% | Warning | Compact non-essential context NOW |
| RED | 85-95% | Critical | Emergency compaction — preserve only active task |
| BLACK | 95%+ | Terminal | Save state immediately, prepare handoff |

Estimate context usage from:
- Number of files read in session
- Conversation turn count
- Agent spawns and their responses
- Skills loaded
- Tool call results accumulated
</step>

<step number="2">
### Token Cost Estimation

Estimate session costs based on model usage:

**Claude Opus 4 Pricing:**
- Input: $15 / 1M tokens
- Output: $5 / 1M tokens

**Claude Sonnet 4 Pricing:**
- Input: $3 / 1M tokens
- Output: $15 / 1M tokens

**Estimation heuristics:**
- Average file read: ~2,000 tokens
- Average tool call result: ~500 tokens
- Average agent spawn (round-trip): ~8,000 tokens
- Average user message: ~200 tokens
- Average assistant response: ~1,500 tokens

Track cumulative estimates across the session.
</step>

<step number="3">
### Strategic Compaction Recommendations

When context usage exceeds YELLOW tier, recommend specific compaction strategies:

**Priority 1 — Drop stale context:**
- Files read >10 turns ago that aren't referenced in active task
- Completed agent results (keep summary, drop details)
- Resolved error messages and their debug traces

**Priority 2 — Compress active context:**
- Replace full file contents with relevant excerpts
- Summarize long tool outputs
- Collapse completed task details into one-line summaries

**Priority 3 — Archive and handoff:**
- Run `/fire-5-handoff` to save state
- Use `/compact Focus on [active task]` for targeted compaction
- Split remaining work into a new session

</step>

<step number="4">
### Display Dashboard

```
=============================================================
            COST & CONTEXT INTELLIGENCE
=============================================================

Session Duration: {hours}h {minutes}m
Conversation Turns: {N}

-------------------------------------------------------------
CONTEXT WINDOW
-------------------------------------------------------------

Usage: [████████████░░░░░░░░] 62% — YELLOW ⚠️

Files read: {N} (~{tokens} tokens)
Agent spawns: {N} (~{tokens} tokens)
Tool calls: {N} (~{tokens} tokens)
Conversation: {N} turns (~{tokens} tokens)

Estimated total: ~{tokens} tokens

-------------------------------------------------------------
COST ESTIMATE
-------------------------------------------------------------

Input tokens: ~{N} × ${rate} = ${amount}
Output tokens: ~{N} × ${rate} = ${amount}
                              ─────────
Estimated session cost:         ${total}
Budget remaining:               ${remaining} (if --budget set)

-------------------------------------------------------------
RECOMMENDATIONS
-------------------------------------------------------------

{If GREEN: "Context is healthy. No action needed."}
{If YELLOW: "Consider running /compact soon. N files from early session could be dropped."}
{If ORANGE+: "COMPACT NOW. Specific recommendations:
  - Drop: [file1, file2] (read >10 turns ago, not in active task)
  - Compress: [agent results] (keep summaries only)
  - Archive: Run /fire-5-handoff to save state before continuing"}

=============================================================
```
</step>

---

## Budget Alerts

When `--budget` is set, display warnings at these thresholds:

| Threshold | Alert |
|-----------|-------|
| 50% of budget | "Half your budget spent. {N} tokens remaining at current rate." |
| 75% of budget | "Budget warning: ${remaining} left. Consider wrapping up current task." |
| 90% of budget | "Budget critical: ${remaining} left. Save state with /fire-5-handoff." |
| 100% of budget | "Budget exceeded. Recommend ending session after current task." |

---

## Integration Points

- **`/fire-3-execute`** — Check context tier before each breath. If ORANGE+, compact before continuing.
- **`/fire-autonomous`** — Auto-check after every 3 phases. If ORANGE+, trigger handoff.
- **`/fire-loop`** — Include cost check in each loop iteration status.
- **`/fire-5-handoff`** — Include final cost summary in handoff document.

---

## Success Criteria

- [ ] Context tier accurately assessed (GREEN/YELLOW/ORANGE/RED/BLACK)
- [ ] Token estimates within reasonable range
- [ ] Cost estimates calculated with current model pricing
- [ ] Compaction recommendations specific and actionable
- [ ] Budget tracking functional when --budget flag used
- [ ] Dashboard displays cleanly

---

## Related Commands

- `/fire-dashboard` — Project overview (includes cost widget)
- `/fire-5-handoff` — Save session state
- `/fire-autonomous` — Uses cost checks for auto-pause decisions
