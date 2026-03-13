---
name: claude-code-token-analytics
category: integrations
version: 1.0.0
contributed: 2026-03-01
contributor: claude-mission-control
last_updated: 2026-03-01
tags: [claude-code, tokens, analytics, stats-cache, usage, billing, dashboard]
difficulty: medium
---

# Claude Code Token Analytics from stats-cache.json

## Problem

Need to display Claude Code token usage, costs, and cache savings in a dashboard. Claude Code stores rich token data locally but no official API exposes it for custom UIs. Key questions:
- How many tokens consumed per day/model?
- What does the API usage cost?
- How much is saved through prompt caching?
- Where are billing period boundaries?

## Solution Pattern

Claude Code maintains two local data sources:

1. **`~/.claude/stats-cache.json`** — Pre-aggregated daily stats (fast, recommended)
2. **`~/.claude/projects/{hash}/{session}.jsonl`** — Raw per-message data (large, slow)

Use `stats-cache.json` for dashboards. It has three arrays:
- `dailyActivity` — messages, sessions, tool calls per day
- `dailyModelTokens` — token counts by model per day
- `modelUsage` — cumulative per-model totals with cache breakdown

### Cache savings calculation

Cache reads are billed at 1/8 of input token price. The savings formula:

```
savings = cache_read_tokens * (input_price - cache_read_price) / 1,000,000
```

Per-model pricing (USD/M tokens):

| Model | Input | Output | Cache Read | Cache Write |
|-------|-------|--------|------------|-------------|
| Opus 4.6 | $15 | $75 | $1.875 | $18.75 |
| Sonnet 4.5/4.6 | $3 | $15 | $0.375 | $3.75 |
| Haiku 4.5 | $0.80 | $4 | $0.10 | $1.00 |

## Code Example

### Backend parser (TypeScript/Express)

```typescript
function parseTokenAnalytics(period: string) {
  const statsPath = path.join(CLAUDE_DIR, 'stats-cache.json')
  if (!existsSync(statsPath)) return { daily: [], totals: {}, usage: {} }

  const stats = JSON.parse(readFileSync(statsPath, 'utf-8'))
  const { modelUsage = {}, dailyModelTokens = [], dailyActivity = [] } = stats

  // Model breakdown with cost calculations
  const modelBreakdown = Object.entries(modelUsage).map(([model, usage]) => {
    const pricing = MODEL_PRICING[model] || DEFAULT_PRICING
    const inputCost = (usage.inputTokens / 1e6) * pricing.input
    const outputCost = (usage.outputTokens / 1e6) * pricing.output
    const cacheReadCost = (usage.cacheReadInputTokens / 1e6) * pricing.cacheRead
    const cacheSavings = (usage.cacheReadInputTokens / 1e6) * (pricing.input - pricing.cacheRead)
    return { model, inputCost, outputCost, cacheReadCost, cacheSavings, ... }
  })

  // Billing period (monthly from first usage date)
  const firstDate = dailyActivity[0]?.date
  const startDay = new Date(firstDate).getDate()
  // ... compute periodStart, periodEnd, daysRemaining

  return { daily: dailyTokens, totals, usage: { todayTokens, periodTokens, ... } }
}
```

### stats-cache.json schema

```typescript
interface StatsCache {
  version: 1
  lastComputedDate: string // "2026-02-28"
  dailyActivity: Array<{
    date: string
    messageCount: number
    sessionCount: number
    toolCallCount: number
  }>
  dailyModelTokens: Array<{
    date: string
    tokensByModel: Record<string, number> // model -> output tokens
  }>
  modelUsage: Record<string, {
    inputTokens: number
    outputTokens: number
    cacheReadInputTokens: number    // billed at 1/8 input price
    cacheCreationInputTokens: number // billed at 1.25x input price
    webSearchRequests: number
    costUSD: number    // always 0 (not computed by Claude Code)
    contextWindow: number
  }>
}
```

### Per-message JSONL schema (for real-time tracking)

```typescript
// Each line in ~/.claude/projects/{hash}/{session}.jsonl
interface SessionEntry {
  type: "assistant" | "user"
  message: {
    model: string
    usage: {
      input_tokens: number
      output_tokens: number
      cache_creation_input_tokens: number
      cache_read_input_tokens: number
      cache_creation: {
        ephemeral_5m_input_tokens: number
        ephemeral_1h_input_tokens: number
      }
    }
  }
  timestamp: string // ISO-8601
  sessionId: string
}
```

## When to Use

- Building a Claude Code dashboard or analytics panel
- Tracking AI usage costs across projects
- Demonstrating cache savings from context engineering
- Computing billing period boundaries and reset dates
- Monitoring daily token consumption trends

## When NOT to Use

- Need real-time token counting during a session (use JSONL instead)
- Tracking non-Claude models (stats-cache only covers Claude models + any models Claude Code uses)
- Need official billing data (use Anthropic Console API for that)

## Common Mistakes

- **stats-cache is stale**: It's updated by Claude Code, not your app. `lastComputedDate` may be yesterday. For today's data, parse the latest session JSONL.
- **tokensByModel is OUTPUT tokens only**: The `dailyModelTokens.tokensByModel` values are output token counts, not total. For full breakdown, use `modelUsage`.
- **costUSD is always 0**: Claude Code doesn't compute costs. You must calculate from per-model pricing.
- **Cache tokens are massive**: cache_read can be billions (10^9). Use proper number formatting (B/M/K suffixes).
- **Model names include dates**: `claude-sonnet-4-5-20250929` — strip the date suffix for display.

## References

- Claude API Pricing: https://docs.anthropic.com/en/docs/about-claude/pricing
- stats-cache.json location: `~/.claude/stats-cache.json`
- Session JSONL location: `~/.claude/projects/{project-hash}/{session-id}.jsonl`
- Contributed from: claude-mission-control Token Analytics feature
