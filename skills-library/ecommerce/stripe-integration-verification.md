# Stripe Integration Verification Checklist

> Mandatory verification gate for any AI-generated Stripe payment code. "Mostly correct" is failure for payments — 100% accuracy required.

**When to use:** After generating or modifying any Stripe payment integration code. Run this checklist before marking any payment feature as complete.
**Stack:** Node.js/Express or Bun, Stripe SDK (`stripe` npm package), Stripe.js (client-side)

---

## The Problem

AI agents generate Stripe code that *looks* correct but fails in production due to:
- Missing webhook signature verification (security vulnerability)
- Raw body middleware conflicts (signature verification fails silently)
- Hardcoded API keys instead of environment variables
- Missing idempotency keys on critical operations
- Client-side token handling that violates PCI scope
- Missing error handling for Stripe-specific error types

---

## Pre-Implementation Gate

Before writing ANY Stripe code, verify:

```
□ Stripe API keys are in environment variables (never hardcoded)
□ Using RESTRICTED keys with minimal required permissions
□ Test mode keys for development (sk_test_*, pk_test_*)
□ Live mode keys ONLY in production environment
□ .env file is in .gitignore
```

---

## Server-Side Verification Checklist

### 1. Checkout Session Creation

```javascript
// CORRECT: Server-side session creation with validation
const session = await stripe.checkout.sessions.create({
  payment_method_types: ['card'],
  line_items: validatedItems.map(item => ({
    price_data: {
      currency: 'usd',
      product_data: { name: item.name },
      unit_amount: Math.round(item.price * 100), // ← CENTS, not dollars
    },
    quantity: item.quantity,
  })),
  mode: 'payment',
  success_url: `${process.env.BASE_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
  cancel_url: `${process.env.BASE_URL}/cancel`,
  idempotency_key: crypto.randomUUID(), // ← REQUIRED for safety
});
```

Verify:
```
□ Prices converted to CENTS (multiply by 100, round to integer)
□ Line items validated server-side (never trust client prices)
□ success_url and cancel_url use environment variable for base URL
□ idempotency_key generated for every session creation
□ mode is correct: 'payment' | 'subscription' | 'setup'
```

### 2. Webhook Handler

```javascript
// CRITICAL: Raw body middleware MUST be configured BEFORE json parser
// This is the #1 AI-generated Stripe bug
app.post('/webhooks/stripe',
  express.raw({ type: 'application/json' }), // ← RAW body, not parsed JSON
  async (req, res) => {
    const sig = req.headers['stripe-signature'];
    let event;

    try {
      event = stripe.webhooks.constructEvent(
        req.body,           // ← Must be raw Buffer, not parsed object
        sig,
        process.env.STRIPE_WEBHOOK_SECRET
      );
    } catch (err) {
      console.error('Webhook signature verification failed:', err.message);
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // Idempotency: check if event already processed
    const alreadyProcessed = await db.query(
      'SELECT 1 FROM processed_stripe_events WHERE event_id = $1',
      [event.id]
    );
    if (alreadyProcessed.rows.length > 0) {
      return res.json({ received: true, duplicate: true });
    }

    // Record event BEFORE processing (crash-safe)
    await db.query(
      'INSERT INTO processed_stripe_events (event_id, type, created_at) VALUES ($1, $2, NOW())',
      [event.id, event.type]
    );

    // Process event
    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutComplete(event.data.object);
        break;
      case 'payment_intent.succeeded':
        await handlePaymentSuccess(event.data.object);
        break;
      case 'payment_intent.payment_failed':
        await handlePaymentFailure(event.data.object);
        break;
      // Handle all relevant event types
    }

    res.json({ received: true });
  }
);
```

Verify:
```
□ express.raw() middleware on webhook route (NOT express.json())
□ Webhook route registered BEFORE global express.json() middleware
□ stripe.webhooks.constructEvent() used for signature verification
□ STRIPE_WEBHOOK_SECRET from environment variable
□ Event ID recorded BEFORE processing (crash-safe idempotency)
□ processed_stripe_events table exists in database schema
□ All relevant event types handled (not just checkout.session.completed)
□ Return 200 quickly — process async if operations are slow
```

### 3. Error Handling

```javascript
try {
  const paymentIntent = await stripe.paymentIntents.create({ /* ... */ });
} catch (err) {
  if (err.type === 'StripeCardError') {
    // Card declined — show user-friendly message
    return res.status(400).json({ error: err.message });
  } else if (err.type === 'StripeRateLimitError') {
    // Too many requests — retry with backoff
  } else if (err.type === 'StripeInvalidRequestError') {
    // Invalid parameters — developer error, log and fix
    console.error('Stripe invalid request:', err.message);
  } else if (err.type === 'StripeAPIError') {
    // Stripe service issue — retry
  } else if (err.type === 'StripeConnectionError') {
    // Network issue — retry with backoff
  } else if (err.type === 'StripeAuthenticationError') {
    // Invalid API key — CRITICAL, alert immediately
    console.error('CRITICAL: Stripe authentication failed');
  }
}
```

Verify:
```
□ Stripe-specific error types handled (not generic try/catch)
□ StripeCardError returns user-friendly message (not raw error)
□ StripeAuthenticationError triggers alert (not silent log)
□ Retry logic for transient errors (RateLimit, API, Connection)
□ No sensitive data in error responses to client
```

---

## Client-Side Verification Checklist

```
□ Using Stripe.js from js.stripe.com (not npm bundle for PCI scope)
□ Publishable key only (pk_test_* or pk_live_*) — never secret key
□ Card element renders in Stripe iframe (never custom input fields)
□ No card data touches your JavaScript (tokenization only)
□ Loading state shown during payment processing
□ Error messages displayed for declined cards
□ Disable submit button after click (prevent double-charge)
□ Redirect to success_url handled (not client-side state)
```

---

## Database Schema Requirements

```sql
-- Processed events table (idempotency)
CREATE TABLE IF NOT EXISTS processed_stripe_events (
  event_id VARCHAR(255) PRIMARY KEY,
  type VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP DEFAULT NOW()
);

-- Index for cleanup job
CREATE INDEX idx_stripe_events_created ON processed_stripe_events(created_at);

-- Cleanup: prune events older than 30 days (Stripe retries for 72 hours max)
-- Run as a cron job or scheduled task
DELETE FROM processed_stripe_events WHERE created_at < NOW() - INTERVAL '30 days';
```

---

## Anti-Patterns (Never Do These)

| Anti-Pattern | Why It's Wrong | Correct Approach |
|-------------|---------------|-----------------|
| `app.use(express.json())` before webhook route | Destroys raw body, signature verification fails | Use `express.raw()` on webhook route |
| Hardcoded `sk_live_*` in source code | Secret key in git history = compromised | Environment variables only |
| Trust client-side prices | Customer can modify prices in browser | Validate prices server-side |
| Skip idempotency keys | Network retries cause duplicate charges | `crypto.randomUUID()` on every mutation |
| Log full Stripe event payloads | May contain PCI-scoped payment method data | Log event ID and type only |
| Use `stripe.charges.create()` | Legacy API, doesn't support SCA/3DS | Use `stripe.checkout.sessions.create()` or PaymentIntents |

---

## Stripe Agent Toolkit Integration

For projects using AI agents that interact with Stripe directly:

```bash
npm install @stripe/agent-toolkit
```

```javascript
import { StripeAgentToolkit } from '@stripe/agent-toolkit/ai-sdk';

const toolkit = new StripeAgentToolkit({
  secretKey: process.env.STRIPE_SECRET_KEY, // MUST be restricted key
  configuration: {
    actions: {
      paymentLinks: { create: true },
      products: { create: true },
      prices: { create: true },
    },
  },
});
```
Verify:
```
□ Using restricted API key (not full-access secret key)
□ Only necessary actions enabled in configuration
□ Toolkit scoped to specific operations (not all Stripe APIs)
```

---

## Post-Verification Sign-Off

After all checks pass:
```
□ Test mode: Complete a full checkout flow end-to-end
□ Test mode: Verify webhook receives and processes events
□ Test mode: Test card decline scenario (4000000000000002)
□ Test mode: Test 3D Secure card (4000002760003184)
□ Test mode: Verify idempotency (replay same event, confirm no duplicate)
□ Review: No hardcoded keys, no raw card data, no PCI violations
```

---

## Sources

- Stripe Engineering Blog: "Can AI agents build real Stripe integrations?" (March 2026)
- ShoppingComp (arXiv:2511.22978) — LLM Shopping Cart Benchmark (Nov 2025)
- Stripe Agent Toolkit Documentation (2025)
- Stripe MCP Documentation (2025)
- Stripe Webhook Best Practices (Stigg, 2025)
- Stripe Idempotent Requests API Documentation
