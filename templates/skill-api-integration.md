---
name: {{SKILL_NAME}}
category: {{CATEGORY}}
type: api-integration
version: 1.0.0
contributed: {{DATE}}
contributor: {{PROJECT}}
last_updated: {{DATE}}
tags: [{{TAGS}}]
difficulty: {{DIFFICULTY}}
usage_count: 0
success_rate: 100
---

# {{TITLE}}

## Problem

[What API integration challenge does this solve?]

## API Overview

| Property | Value |
|----------|-------|
| **Service** | [Service name] |
| **Auth Type** | [OAuth2 / API Key / Bearer / etc.] |
| **Base URL** | `https://api.example.com/v1` |
| **Rate Limit** | [X requests per minute/hour] |
| **Docs** | [Link to official docs] |

## Environment Variables

```env
# Required
SERVICE_API_KEY=YOUR_API_KEY
SERVICE_API_SECRET=YOUR_API_SECRET

# Optional
SERVICE_BASE_URL=https://api.example.com/v1
SERVICE_TIMEOUT_MS=5000
```

## Solution Pattern

### Client Setup

```{{LANGUAGE}}
{{CLIENT_SETUP_CODE}}
```

### Core Integration

```{{LANGUAGE}}
{{INTEGRATION_CODE}}
```

### Error Handling

```{{LANGUAGE}}
{{ERROR_HANDLING_CODE}}
```

## Retry & Resilience

```{{LANGUAGE}}
// Exponential backoff with jitter for rate limits
{{RETRY_CODE}}
```

## Webhook Handling (if applicable)

```{{LANGUAGE}}
// Signature verification + idempotency
{{WEBHOOK_CODE}}
```

## Testing

```{{LANGUAGE}}
// Mock setup for tests
{{TEST_MOCK_CODE}}
```

## Common Pitfalls

1. **[Pitfall 1]** - [How to avoid]
2. **[Pitfall 2]** - [How to avoid]
3. **[Pitfall 3]** - [How to avoid]

## When to Use

- [Scenario 1]
- [Scenario 2]

## When NOT to Use

- [Anti-pattern 1]

## Related Skills

- [related-skill] - [description]

## References

- [Official API docs](https://example.com/docs)
- Contributed from: {{PROJECT}}
