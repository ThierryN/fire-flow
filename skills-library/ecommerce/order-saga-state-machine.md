# Order Saga Pattern + State Machine

> Model order lifecycle as a finite state machine with saga-pattern compensating transactions for distributed processing.

**When to use:** Building any order processing system — especially those involving payment capture, inventory reservation, and fulfillment coordination across services.
**Stack:** Node.js/Express, PostgreSQL/MySQL, optional message queue (BullMQ, SQS)

---

## Order State Machine

```
                    ┌──────────────────────────────────────────────┐
                    │                                                │
  ┌────────┐    ┌───▼─────┐    ┌──────────┐    ┌──────────┐    ┌───┴──────┐
  │ CREATED│───▶│CONFIRMED│───▶│PROCESSING│───▶│ SHIPPED  │───▶│DELIVERED │
  └───┬────┘    └───┬─────┘    └────┬─────┘    └────┬─────┘    └──────────┘
      │             │               │               │
      │         ┌───▼─────┐    ┌────▼─────┐    ┌────▼─────┐
      └────────▶│CANCELLED│    │  FAILED  │    │ RETURNED │
                └─────────┘    └──────────┘    └──────────┘
                                    │
                               ┌────▼─────┐
                               │ REFUNDED │
                               └──────────┘
```

### State Definitions

```javascript
const ORDER_STATES = {
  CREATED: 'created',           // Order placed, awaiting payment
  CONFIRMED: 'confirmed',       // Payment captured successfully
  PROCESSING: 'processing',     // Being prepared for fulfillment
  SHIPPED: 'shipped',           // Handed to carrier
  DELIVERED: 'delivered',       // Confirmed delivered
  CANCELLED: 'cancelled',       // Cancelled before shipment
  FAILED: 'failed',             // Payment or processing failed
  RETURNED: 'returned',         // Customer returned the order
  REFUNDED: 'refunded',         // Refund issued
};

const VALID_TRANSITIONS = {
  created:    ['confirmed', 'cancelled', 'failed'],
  confirmed:  ['processing', 'cancelled', 'refunded'],
  processing: ['shipped', 'cancelled', 'failed'],
  shipped:    ['delivered', 'returned'],
  delivered:  ['returned'],
  returned:   ['refunded'],
  cancelled:  [],  // Terminal state
  failed:     ['created'],  // Allow retry
  refunded:   [],  // Terminal state
};
```

### Transition Enforcement

```javascript
async function transitionOrder(orderId, newStatus, metadata = {}) {
  const order = await db.query('SELECT * FROM orders WHERE id = $1', [orderId]);
  if (!order.rows[0]) throw new Error(`Order ${orderId} not found`);

  const currentStatus = order.rows[0].status;
  const allowed = VALID_TRANSITIONS[currentStatus];

  if (!allowed || !allowed.includes(newStatus)) {
    throw new Error(
      `Invalid transition: ${currentStatus} → ${newStatus}. ` +
      `Allowed: ${allowed?.join(', ') || 'none (terminal state)'}`
    );
  }

  // Record transition in history
  await db.query(
    `INSERT INTO order_status_history (order_id, from_status, to_status, metadata, created_at)
     VALUES ($1, $2, $3, $4, NOW())`,
    [orderId, currentStatus, newStatus, JSON.stringify(metadata)]
  );

  // Update order
  await db.query(
    'UPDATE orders SET status = $1, updated_at = NOW() WHERE id = $2',
    [newStatus, orderId]
  );

  // Emit event for side effects
  await emitOrderEvent(orderId, newStatus, metadata);
}
```

---

## Checkout Saga (Orchestrated)

The checkout process is a saga — a sequence of steps where each step has a compensating action for rollback:

```javascript
async function executeCheckoutSaga(orderId, cartId, paymentMethodId) {
  const saga = new SagaOrchestrator();

  // Step 1: Validate cart
  saga.addStep({
    name: 'validate_cart',
    execute: async () => {
      const validation = await validateCartForCheckout(cartId);
      if (!validation.valid) throw new Error(`Cart invalid: ${validation.issues[0].message}`);
      return validation;
    },
    compensate: async () => {
      // Nothing to roll back — validation is read-only
    },
  });

  // Step 2: Reserve inventory
  saga.addStep({
    name: 'reserve_inventory',
    execute: async (ctx) => {
      const items = await getCartItems(cartId);
      for (const item of items) {
        await reserveStock(item.product_id, item.variant_id, item.quantity, orderId);
      }
      return { items };
    },
    compensate: async (ctx) => {
      // COMPENSATE: Release reserved inventory
      const items = await getCartItems(cartId);
      for (const item of items) {
        await releaseStock(item.product_id, item.variant_id, item.quantity, orderId);
      }
    },
  });

  // Step 3: Capture payment
  saga.addStep({
    name: 'capture_payment',
    execute: async (ctx) => {
      const paymentIntent = await stripe.paymentIntents.create({
        amount: ctx.validate_cart.subtotal * 100,
        currency: 'usd',
        payment_method: paymentMethodId,
        confirm: true,
        metadata: { order_id: orderId },
      }, {
        idempotencyKey: `checkout-${orderId}`,
      });
      return { paymentIntent };
    },
    compensate: async (ctx) => {
      // COMPENSATE: Refund payment
      if (ctx.capture_payment?.paymentIntent) {
        await stripe.refunds.create({
          payment_intent: ctx.capture_payment.paymentIntent.id,
        });
      }
    },
  });

  // Step 4: Create order record
  saga.addStep({
    name: 'create_order',
    execute: async (ctx) => {
      await transitionOrder(orderId, 'confirmed', {
        payment_intent_id: ctx.capture_payment.paymentIntent.id,
      });
      return { confirmed: true };
    },
    compensate: async (ctx) => {
      // COMPENSATE: Mark order as failed
      await transitionOrder(orderId, 'failed', { reason: 'saga_rollback' });
    },
  });

  // Step 5: Clear cart
  saga.addStep({
    name: 'clear_cart',
    execute: async () => {
      await db.query("UPDATE carts SET status = 'converted' WHERE id = $1", [cartId]);
    },
    compensate: async () => {
      await db.query("UPDATE carts SET status = 'active' WHERE id = $1", [cartId]);
    },
  });

  // Execute saga
  try {
    const result = await saga.run();
    return { success: true, order_id: orderId, ...result };
  } catch (err) {
    // Saga automatically runs compensating actions in reverse order
    return { success: false, error: err.message, rollback: saga.getCompensationLog() };
  }
}
```

### Saga Orchestrator Implementation

```javascript
class SagaOrchestrator {
  constructor() {
    this.steps = [];
    this.context = {};
    this.completedSteps = [];
    this.compensationLog = [];
  }

  addStep({ name, execute, compensate }) {
    this.steps.push({ name, execute, compensate });
  }

  async run() {
    for (const step of this.steps) {
      try {
        const result = await step.execute(this.context);
        this.context[step.name] = result;
        this.completedSteps.push(step);
      } catch (err) {
        // Run compensating actions in REVERSE order
        for (const completed of [...this.completedSteps].reverse()) {
          try {
            await completed.compensate(this.context);
            this.compensationLog.push({ step: completed.name, status: 'compensated' });
          } catch (compErr) {
            this.compensationLog.push({
              step: completed.name, status: 'compensation_failed',
              error: compErr.message
            });
            // Log but continue — try to compensate remaining steps
          }
        }
        throw new Error(`Saga failed at ${step.name}: ${err.message}`);
      }
    }
    return this.context;
  }

  getCompensationLog() { return this.compensationLog; }
}
```

---

## Database Schema

```sql
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  status VARCHAR(20) NOT NULL DEFAULT 'created',
  subtotal DECIMAL(10,2) NOT NULL,
  tax DECIMAL(10,2) DEFAULT 0,
  shipping DECIMAL(10,2) DEFAULT 0,
  total DECIMAL(10,2) NOT NULL,
  payment_intent_id VARCHAR(255),
  shipping_address JSONB,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL REFERENCES orders(id),
  product_id UUID NOT NULL REFERENCES products(id),
  variant_id UUID REFERENCES product_variants(id),
  quantity INTEGER NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  total_price DECIMAL(10,2) NOT NULL
);

CREATE TABLE order_status_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL REFERENCES orders(id),
  from_status VARCHAR(20),
  to_status VARCHAR(20) NOT NULL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Inventory reservations (for saga rollback)
CREATE TABLE inventory_reservations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL,
  variant_id UUID,
  quantity INTEGER NOT NULL,
  order_id UUID NOT NULL,
  status VARCHAR(20) DEFAULT 'reserved',  -- reserved | committed | released
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '30 minutes'
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_history ON order_status_history(order_id);
CREATE INDEX idx_reservations_order ON inventory_reservations(order_id);
CREATE INDEX idx_reservations_expiry ON inventory_reservations(expires_at)
  WHERE status = 'reserved';
```

---

## Event Hooks

```javascript
async function emitOrderEvent(orderId, newStatus, metadata) {
  const handlers = {
    confirmed: [sendOrderConfirmationEmail, notifyFulfillment],
    processing: [updateInventoryCommit],
    shipped: [sendShippingNotification, generateTrackingPage],
    delivered: [sendDeliveryConfirmation, requestReview],
    cancelled: [sendCancellationEmail, releaseInventory, processRefund],
    failed: [sendFailureNotification, releaseInventory],
    returned: [processReturn, sendReturnConfirmation],
    refunded: [sendRefundConfirmation],
  };

  const fns = handlers[newStatus] || [];
  for (const fn of fns) {
    try {
      await fn(orderId, metadata);
    } catch (err) {
      console.error(`Event handler failed for ${newStatus}:`, err);
      // Log but don't fail the transition — side effects are secondary
    }
  }
}
```

---

## Sources

- microservices.io: Saga Pattern (2025)
- Medusa.js v2: Workflow-based commerce architecture (2025)
- SagaLLM: Transaction Guarantees for Multi-Agent (VLDB 2025, arXiv:2503.11951)
- Sylius: State machines in e-commerce modeling (2025)
- commercetools: Order state machines documentation (2025)
