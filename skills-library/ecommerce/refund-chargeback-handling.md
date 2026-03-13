# Refund & Chargeback Handling

> Partial refunds, refund authorization flows, chargeback dispute handling, and tax recalculation patterns.

**When to use:** Implementing any refund capability in an e-commerce system. Critical for production systems processing real payments.
**Stack:** Node.js/Express, Stripe, PostgreSQL/MySQL

---

## Refund Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Full refund** | Return entire payment amount | Order cancelled, wrong item shipped |
| **Partial refund** | Return portion of payment | One item from multi-item order, damaged item |
| **Store credit** | Issue credit instead of cash refund | Customer retention, faster processing |

---

## Refund API

```javascript
// Full refund
router.post('/api/orders/:orderId/refund', requireAdmin, async (req, res) => {
  const { reason, items, amount } = req.body;
  const order = await getOrder(req.params.orderId);

  if (!order) return res.status(404).json({ error: 'Order not found' });
  if (!['confirmed', 'processing', 'shipped', 'delivered'].includes(order.status)) {
    return res.status(400).json({ error: `Cannot refund order in ${order.status} status` });
  }

  // Calculate refund amount
  let refundAmount;
  if (amount) {
    // Explicit amount (admin override)
    refundAmount = Math.round(amount * 100); // cents
  } else if (items && items.length > 0) {
    // Partial refund: sum of selected items
    refundAmount = items.reduce((sum, item) => {
      const orderItem = order.items.find(i => i.id === item.id);
      return sum + (orderItem.unit_price * item.quantity * 100);
    }, 0);
  } else {
    // Full refund
    refundAmount = Math.round(order.total * 100);
  }

  // Create Stripe refund
  const refund = await stripe.refunds.create({
    payment_intent: order.payment_intent_id,
    amount: refundAmount,
    reason: reason === 'duplicate' ? 'duplicate'
          : reason === 'fraud' ? 'fraudulent'
          : 'requested_by_customer',
    metadata: { order_id: order.id, admin_id: req.user.id },
  });

  // Record refund
  await db.query(
    `INSERT INTO refunds (order_id, stripe_refund_id, amount, reason, status, created_by)
     VALUES ($1, $2, $3, $4, $5, $6)`,
    [order.id, refund.id, refundAmount / 100, reason, refund.status, req.user.id]
  );

  // Update order status if fully refunded
  const totalRefunded = await getTotalRefunded(order.id);
  if (totalRefunded >= order.total) {
    await transitionOrder(order.id, 'refunded', { refund_id: refund.id });
  }

  // Restore inventory if items returned
  if (items) {
    for (const item of items) {
      await restoreStock(item.product_id, item.variant_id, item.quantity);
    }
  }

  res.json({
    refund_id: refund.id,
    amount: refundAmount / 100,
    status: refund.status,
    total_refunded: totalRefunded + refundAmount / 100,
    order_total: order.total,
  });
});
```

---

## Chargeback/Dispute Handling

When a customer disputes a charge with their bank:

```javascript
// Webhook handler for disputes
async function handleDisputeCreated(event) {
  const dispute = event.data.object;

  // Record dispute
  await db.query(
    `INSERT INTO disputes (stripe_dispute_id, payment_intent_id, amount, reason, status, evidence_due_by)
     VALUES ($1, $2, $3, $4, $5, $6)`,
    [dispute.id, dispute.payment_intent, dispute.amount / 100,
     dispute.reason, dispute.status,
     new Date(dispute.evidence_details.due_by * 1000)]
  );

  // Alert admin immediately
  await sendAdminAlert({
    type: 'DISPUTE_CREATED',
    amount: dispute.amount / 100,
    reason: dispute.reason,
    due_by: new Date(dispute.evidence_details.due_by * 1000),
    order: await getOrderByPaymentIntent(dispute.payment_intent),
  });
}

// Submit evidence
async function submitDisputeEvidence(disputeId) {
  const dispute = await getDispute(disputeId);
  const order = await getOrderByPaymentIntent(dispute.payment_intent_id);
  const metadata = await getOrderFraudMetadata(order.id);

  await stripe.disputes.update(dispute.stripe_dispute_id, {
    evidence: {
      customer_name: order.customer_name,
      customer_email_address: order.customer_email,
      product_description: order.items.map(i => i.name).join(', '),
      billing_address: order.billing_address,
      shipping_address: order.shipping_address,
      shipping_tracking_number: order.tracking_number,
      customer_purchase_ip: metadata.ip_address,
      receipt: order.receipt_url,            // Stripe receipt URL
      // Upload additional evidence files via Stripe File API
    },
  });
}
```

---

## Database Schema

```sql
CREATE TABLE refunds (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL REFERENCES orders(id),
  stripe_refund_id VARCHAR(255),
  amount DECIMAL(10,2) NOT NULL,
  reason VARCHAR(100),
  status VARCHAR(20) DEFAULT 'pending',
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE disputes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  stripe_dispute_id VARCHAR(255) UNIQUE,
  payment_intent_id VARCHAR(255),
  amount DECIMAL(10,2) NOT NULL,
  reason VARCHAR(100),
  status VARCHAR(30) DEFAULT 'needs_response',
  evidence_due_by TIMESTAMP,
  evidence_submitted_at TIMESTAMP,
  outcome VARCHAR(20),  -- won | lost
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Sources

- Internal gap analysis: GAP-ECOM-3 (Refund & Chargeback Handling)
- Stripe API: Refunds and Disputes documentation (2025)
- Stigg Engineering: Webhook best practices (2025)
