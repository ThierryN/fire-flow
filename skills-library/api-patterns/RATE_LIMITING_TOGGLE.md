---
name: rate-limiting-toggle
category: api-patterns
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [rate-limiting, api, middleware, express, toggle, throttle, bypass]
difficulty: medium
---

# Rate Limiting with Toggle

## Problem

Rate limiting protects APIs from abuse, but during development, testing, or specific workflows you need it OFF. Hardcoded rate limits slow down dev, break integration tests, and frustrate admins who need burst access.

## Solution Pattern

Implement rate limiting as toggleable middleware — on/off globally, per-route, or per-user. Environment variable controls the master switch.

## Implementation

### Express Middleware with Global Toggle

```javascript
// middleware/rateLimiter.js
const rateLimit = require('express-rate-limit')

// Master toggle — set RATE_LIMIT_ENABLED=false to disable
const ENABLED = process.env.RATE_LIMIT_ENABLED !== 'false'

function createLimiter(options = {}) {
  const defaults = {
    windowMs: 15 * 60 * 1000,  // 15 minutes
    max: 100,                   // 100 requests per window
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: 'Too many requests, slow down' },
    skip: () => !ENABLED,       // <-- THE TOGGLE: skip all checks when disabled
    ...options,
  }

  return rateLimit(defaults)
}

// Pre-built tiers
const limiter = {
  // Standard API routes
  standard: createLimiter({ max: 100 }),

  // Auth routes (stricter)
  auth: createLimiter({ max: 20, windowMs: 15 * 60 * 1000 }),

  // Upload routes (lenient)
  upload: createLimiter({ max: 10, windowMs: 60 * 60 * 1000 }),

  // Webhook routes (no limit by default)
  webhook: createLimiter({ max: 1000 }),

  // Custom: pass your own options
  custom: createLimiter,
}

module.exports = { limiter, ENABLED }
```

### Per-Route Toggle

```javascript
// routes/api.js
const { limiter } = require('../middleware/rateLimiter')

// Apply to specific routes
router.use('/auth', limiter.auth)
router.use('/upload', limiter.upload)
router.use('/api', limiter.standard)

// Some routes never rate-limited
router.use('/health', (req, res) => res.json({ ok: true }))
```

### Per-User Bypass (Admin/API Key)

```javascript
// middleware/rateLimiter.js — enhanced skip function
function createLimiter(options = {}) {
  return rateLimit({
    ...defaults,
    skip: (req) => {
      // Master toggle
      if (!ENABLED) return true

      // Admin bypass
      if (req.user?.role === 'admin') return true

      // API key bypass (for trusted integrations)
      if (req.headers['x-api-key'] === process.env.RATE_LIMIT_BYPASS_KEY) return true

      // Per-route disable via route metadata
      if (req.route?.rateLimitDisabled) return true

      return false
    },
    ...options,
  })
}
```

### .env Configuration

```bash
# Production: ON
RATE_LIMIT_ENABLED=true
RATE_LIMIT_BYPASS_KEY=your-secret-key-for-trusted-clients

# Development: OFF
RATE_LIMIT_ENABLED=false

# Testing: OFF (in test setup)
# process.env.RATE_LIMIT_ENABLED = 'false'
```

### Runtime Toggle (No Restart)

```javascript
// For when you need to flip it without restarting the server
// admin route — protected behind auth
router.post('/admin/rate-limit', requireAdmin, (req, res) => {
  const { enabled } = req.body
  process.env.RATE_LIMIT_ENABLED = enabled ? 'true' : 'false'
  res.json({ rateLimitEnabled: enabled })
})
```

## Response Headers (When Active)

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1708934400
```

Clients can read these headers to self-throttle.

## When to Use

- Any API that faces the internet
- APIs with mixed access patterns (humans + bots + admins)
- Development environments where rate limits slow you down

## When NOT to Use

- Internal microservice-to-microservice calls (use circuit breakers instead)
- WebSocket connections (different throttling model)
- When the upstream proxy (nginx, Cloudflare) already handles rate limiting
