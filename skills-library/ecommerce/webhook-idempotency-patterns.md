# Webhook Idempotency Patterns

> Prevent duplicate order processing, double charges, and event replay attacks in payment webhook handlers.

**When to use:** Implementing any webhook handler for Stripe, PayPal, or other payment/event-driven systems. Critical for checkout flows, subscription billing, and order fulfillment.
**Stack:** Node.js/Express, PostgreSQL/MySQL, any message queue (optional)

---

## Why This Matters

Without idempotency:
- Network timeout → Stripe retries → duplicate order created
- Server crash mid-processing → Stripe retries → partial + full order exist
- Load balancer routes retry to different server → two servers process same event
- Manual webhook replay during debugging → duplicate charges

---

## Pattern 1: Event Deduplication Table

The simplest and most reliable approach — track processed event IDs in the database.

### Schema

```sql
CREATE TABLE processed_webhook_events (
  event_id VARCHAR(255) PRIMARY KEY,
  event_type VARCHAR(100) NOT NULL,
  provider VARCHAR(50) NOT NULL DEFAULT 'stripe',
  received_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP,
  status VARCHAR(20) DEFAULT 'processing',  -- processing | completed | failed
  idempotency_key VARCHAR(255),
  CONSTRAINT chk_status CHECK (status IN ('processing', 'completed', 'failed'))
);

CREATE INDEX idx_webhook_events_received ON processed_webhook_events(received_at);
CREATE INDEX idx_webhook_events_status ON processed_webhook_events(status);
```

### Handler Pattern

```javascript
async function handleWebhookEvent(event, provider = 'stripe') {
  // Step 1: Check if already processed
  const existing = await db.query(
    'SELECT status FROM processed_webhook_events WHERE event_id = $1',
    [event.id]
  );

  if (existing.rows.length > 0) {
    if (existing.rows[0].status === 'completed') {
      return { duplicate: true, status: 'already_processed' };
    }
    if (existing.rows[0].status === 'processing') {
      return { duplicate: true, status: 'in_progress' };
    }
    // status === 'failed' → allow retry
  }

  // Step 2: Record event BEFORE processing (crash-safe)
  await db.query(
    `INSERT INTO processed_webhook_events (event_id, event_type, provider, status)
     VALUES ($1, $2, $3, 'processing')
     ON CONFLICT (event_id) DO UPDATE SET status = 'processing'`,
    [event.id, event.type, provider]
  );

  try {
    // Step 3: Process event (business logic)
    await processEvent(event);

    // Step 4: Mark as completed
    await db.query(
      `UPDATE processed_webhook_events
       SET status = 'completed', processed_at = NOW()
       WHERE event_id = $1`,
      [event.id]
    );

    return { success: true };
  } catch (err) {
    // Step 5: Mark as failed (allows retry on next delivery)
    await db.query(
      `UPDATE processed_webhook_events SET status = 'failed' WHERE event_id = $1`,
      [event.id]
    );
    throw err;
  }
}
```

---

## Pattern 2: Idempotency Keys for Outbound Requests

When YOUR code calls Stripe (not webhooks — outbound API calls):

```javascript
import { randomUUID } from 'crypto';

// Every mutating Stripe call gets an idempotency key
const paymentIntent = await stripe.paymentIntents.create(
  {
    amount: 2000,
    currency: 'usd',
    customer: customerId,
  },
  {
    idempotencyKey: `create-pi-${orderId}-${randomUUID()}`,
    // Key format: operation-entity-uniqueId
    // Max 255 characters
  }
);
```

### Key Generation Strategies

```javascript
// Strategy 1: Order-scoped (same order always gets same intent)
const key = `checkout-${orderId}`;  // Retries reuse same key → same result

// Strategy 2: Operation-scoped (each attempt is unique)
const key = `checkout-${orderId}-${Date.now()}`; // Each retry creates new intent

// Strategy 3: User-action-scoped (prevents double-click)
const key = `checkout-${userId}-${cartHash}`; // Same cart = same key
```

Choose based on your needs:
- **Order-scoped** for checkout (prevent duplicate charges on same order)
- **Operation-scoped** for refunds (each refund attempt is independent)
- **User-action-scoped** for one-click buy (prevent accidental double-purchase)

---

## Pattern 3: Webhook Signature Verification

Always verify before processing — never skip, even in development:

### Stripe

```javascript
app.post('/webhooks/stripe',
  express.raw({ type: 'application/json' }),
  (req, res) => {
    const sig = req.headers['stripe-signature'];
    try {
      const event = stripe.webhooks.constructEvent(
        req.body, sig, process.env.STRIPE_WEBHOOK_SECRET
      );
      // Process verified event
    } catch (err) {
      return res.status(400).send(`Signature verification failed`);
    }
  }
);
```

### PayPal

```javascript
app.post('/webhooks/paypal', express.json(), async (req, res) => {
  const verified = await paypal.notification.webhookEvent.verify(
    req.headers, req.body, process.env.PAYPAL_WEBHOOK_ID
  );
  if (verified.verification_status !== 'SUCCESS') {
    return res.status(400).send('Signature verification failed');
  }
  // Process verified event
});
```

---

## Pattern 4: Async Processing with Acknowledge-First

For slow operations, acknowledge immediately and process in background:

```javascript
app.post('/webhooks/stripe',
  express.raw({ type: 'application/json' }),
  async (req, res) => {
    // Verify signature
    const event = stripe.webhooks.constructEvent(/* ... */);

    // Check idempotency
    const isDuplicate = await checkAndRecordEvent(event.id, event.type);
    if (isDuplicate) {
      return res.json({ received: true });
    }

    // Acknowledge immediately (Stripe stops retrying)
    res.json({ received: true });

    // Process in background (won't block response)
    setImmediate(async () => {
      try {
        await processEvent(event);
        await markEventCompleted(event.id);
      } catch (err) {
        await markEventFailed(event.id);
        console.error(`Failed to process event ${event.id}:`, err);
        // Event stays in 'processing' state — manual intervention needed
      }
    });
  }
);
```

---

## Cleanup Job

Prune old events to prevent table bloat:

```javascript
// Run daily via cron or scheduled task
async function cleanupProcessedEvents() {
  const result = await db.query(
    `DELETE FROM processed_webhook_events
     WHERE received_at < NOW() - INTERVAL '30 days'
     AND status = 'completed'`
  );
  console.log(`Cleaned up ${result.rowCount} old webhook events`);
}
```

Stripe retries for max 72 hours, so 30-day retention is generous.

---

## Testing Checklist

```
□ Send same webhook event twice → only one order created
□ Send webhook while server is processing same event → second is rejected
□ Kill server mid-processing → restart → Stripe retries → event processed once
□ Send webhook with invalid signature → rejected with 400
□ Send webhook with old event ID (already completed) → acknowledged, not reprocessed
□ Outbound Stripe call with same idempotency key → returns cached result
□ Cleanup job removes events older than retention period
```

---

## Sources

- Stripe API: "Idempotent Requests" documentation (2025)
- Stripe API: "Handle webhook events" best practices (2025)
- Stigg Engineering: "Best practices I wish we knew when integrating Stripe webhooks" (2025)
- Stripe Blog: "Designing robust and predictable APIs with idempotency" (2025)
