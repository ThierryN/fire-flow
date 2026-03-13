---
name: api-field-name-mismatch
category: api-patterns
version: 1.0.0
contributed: 2026-03-12
contributor: claude-mission-control
last_updated: 2026-03-12
contributors:
  - claude-mission-control
tags: [api, debugging, fetch, express, silent-errors, 400]
difficulty: easy
usage_count: 0
success_rate: 100
---

# API Field Name Mismatch — Silent 400 Errors from Request Body Mismatches

## Problem

Frontend sends `{ id: "action-1" }` but backend expects `{ actionId: "action-1" }`. The backend returns a 400 error, but the frontend's catch block shows a generic "Failed" status with no output. The user sees the button flash "Done" or "Failed" but never sees any command output. The root cause — a field name mismatch — is invisible without checking the Network tab.

**Symptoms:**
- Quick action / API call appears to work (no crash) but returns no data
- Status briefly shows "error" then resets to idle
- Network tab shows 400 response: `{ error: "actionId is required" }`
- Output area is empty (because the response was an error, not command results)
- No TypeScript error because both frontend and backend compile independently

## Solution Pattern

**Diagnosis:** Open browser DevTools → Network tab → find the POST request → check the request body vs what the server destructures.

**Prevention:** Share types between frontend and backend. If that's not possible, document the API contract clearly and test with curl first.

## Code Example

```typescript
// Frontend (BROKEN — sends "id" instead of "actionId")
const res = await fetch('/api/commands/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ id: action.id })  // WRONG field name
})

// Backend (expects "actionId")
app.post('/api/commands/execute', (req, res) => {
  const { actionId } = req.body  // undefined!
  if (!actionId) return res.status(400).json({ error: 'actionId is required' })
})

// Frontend (FIXED)
body: JSON.stringify({ actionId: action.id })  // Matches server expectation
```

## Implementation Steps

1. Check Network tab for non-200 responses on the endpoint
2. Compare request body field names with server-side destructuring
3. Fix the mismatch
4. Add output display so errors are visible to the user (not silently swallowed)

## When to Use

- API calls that return no data but don't crash
- "It works but nothing happens" debugging
- Any time frontend and backend are developed independently
- After refactoring either frontend or backend API contracts

## When NOT to Use

- When the error is clearly shown in the UI
- Auth failures (different root cause)
- CORS issues (different symptoms)

## Common Mistakes

- Assuming "no crash = working" — a 400 response is still a successful HTTP fetch
- Not checking `res.ok` before parsing the response as success
- Catching errors but not displaying the error message to the user
- Not validating request bodies with schemas (Zod, Joi) that would surface the mismatch immediately

## Prevention Patterns

```typescript
// 1. Shared types (best)
// shared/api-types.ts
interface ExecuteCommandRequest { actionId: string; args?: string }

// 2. Zod validation on server (second best)
const schema = z.object({ actionId: z.string() })
const parsed = schema.safeParse(req.body)
if (!parsed.success) return res.status(400).json({ error: parsed.error.message })

// 3. Always check res.ok on frontend
if (!res.ok) {
  const error = await res.json()
  throw new Error(error.error || `HTTP ${res.status}`)
}
```

## Related Skills

- streaming-command-timeout - Another silent failure pattern with process execution

## References

- Contributed from: claude-mission-control QuickActions panel (actions appeared to work but never showed output)
