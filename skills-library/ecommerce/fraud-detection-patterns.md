# Fraud Detection & Prevention Patterns

> Velocity checks, geographic anomaly detection, 3D Secure enforcement, and chargeback prevention for AI-generated e-commerce code.

**When to use:** Building any payment system that processes real transactions. Apply as a verification layer alongside PCI compliance.
**Stack:** Node.js/Express, PostgreSQL/MySQL, Stripe Radar (or manual rules)

---

## Stripe Radar (Recommended First Line)

Stripe Radar is built-in and handles most fraud automatically. Enable it:

```javascript
// Radar is enabled by default on Stripe accounts
// Add rules for your specific business:

const paymentIntent = await stripe.paymentIntents.create({
  amount: 5000,
  currency: 'usd',
  payment_method: paymentMethodId,
  confirm: true,
  // Radar evaluates every payment automatically
  // High-risk payments are blocked or flagged for review
});

// Check Radar's risk assessment
if (paymentIntent.charges?.data[0]?.outcome?.risk_level === 'elevated') {
  // Flag for manual review
  await flagForReview(paymentIntent.id, 'elevated_risk');
}
```

---

## Custom Velocity Checks

For risks Radar doesn't catch or for non-Stripe systems:

```javascript
async function checkVelocity(userId, ipAddress, paymentMethodFingerprint) {
  const checks = [];

  // Check 1: Transaction count per card in time window
  const cardCount = await db.query(
    `SELECT COUNT(*) as count FROM orders
     WHERE payment_fingerprint = $1 AND created_at > NOW() - INTERVAL '1 hour'`,
    [paymentMethodFingerprint]
  );
  if (cardCount.rows[0].count >= 5) {
    checks.push({ rule: 'card_velocity', risk: 'high',
      detail: `${cardCount.rows[0].count} transactions in 1 hour` });
  }

  // Check 2: Transaction count per IP
  const ipCount = await db.query(
    `SELECT COUNT(*) as count FROM orders
     WHERE ip_address = $1 AND created_at > NOW() - INTERVAL '1 hour'`,
    [ipAddress]
  );
  if (ipCount.rows[0].count >= 10) {
    checks.push({ rule: 'ip_velocity', risk: 'high',
      detail: `${ipCount.rows[0].count} transactions from same IP` });
  }

  // Check 3: Unusual amount patterns
  const avgAmount = await db.query(
    `SELECT AVG(total) as avg_total FROM orders WHERE user_id = $1`,
    [userId]
  );
  // Flag if order is 5x the user's average
  if (avgAmount.rows[0].avg_total && currentAmount > avgAmount.rows[0].avg_total * 5) {
    checks.push({ rule: 'amount_anomaly', risk: 'medium',
      detail: `Order is ${(currentAmount / avgAmount.rows[0].avg_total).toFixed(1)}x user average` });
  }

  return {
    passed: checks.filter(c => c.risk === 'high').length === 0,
    checks,
    riskLevel: checks.some(c => c.risk === 'high') ? 'high'
             : checks.some(c => c.risk === 'medium') ? 'medium' : 'low',
  };
}
```

---

## 3D Secure / Strong Customer Authentication (SCA)

Required in the EU (PSD2) and recommended everywhere:

```javascript
// Stripe handles 3DS automatically with PaymentIntents
const paymentIntent = await stripe.paymentIntents.create({
  amount: 5000,
  currency: 'eur',
  payment_method: paymentMethodId,
  confirmation_method: 'manual',
  // Stripe automatically triggers 3DS when required
});

// Client-side: handle 3DS authentication
const { error, paymentIntent: confirmed } = await stripe.confirmCardPayment(
  clientSecret
);
// If 3DS is needed, Stripe shows the authentication modal automatically
```

---

## Address Verification (AVS)

```javascript
// Stripe returns AVS results in the charge outcome
const charge = paymentIntent.charges?.data[0];
const avsResult = charge?.payment_method_details?.card?.checks;

if (avsResult?.address_line1_check === 'fail' ||
    avsResult?.address_postal_code_check === 'fail') {
  // Address doesn't match — higher fraud risk
  await flagForReview(paymentIntent.id, 'avs_mismatch');
}
```

---

## Chargeback Prevention

```javascript
// 1. Send email receipts immediately (proves customer was notified)
await sendReceiptEmail(order.email, order);

// 2. Use clear billing descriptor
const paymentIntent = await stripe.paymentIntents.create({
  amount: 5000,
  currency: 'usd',
  statement_descriptor: 'MYSTORE ORDER',      // Max 22 chars
  statement_descriptor_suffix: order.number,   // Appears on statement
});

// 3. Require CVV (Stripe Elements does this by default)
// 4. Log IP address and device info for dispute evidence
await db.query(
  `INSERT INTO order_fraud_metadata (order_id, ip_address, user_agent, fingerprint)
   VALUES ($1, $2, $3, $4)`,
  [orderId, req.ip, req.headers['user-agent'], req.body.deviceFingerprint]
);
```

---

## Safety Gates for AI-Generated Code

Operations an AI agent must NEVER perform without user confirmation:

```
HARD GATES (always require human confirmation):
□ Processing a payment > $500
□ Issuing a refund
□ Changing account email or password
□ Deleting an account
□ Modifying pricing or discounts
□ Bulk operations on orders

SOFT GATES (log but allow in automation):
□ Adding items to cart
□ Viewing order history
□ Updating shipping address
□ Applying a coupon code
```

---

## Sources

- Internal gap analysis: GAP-ECOM-10 (Fraud Detection)
- Amazon-Bench (arXiv:2508.15832) — E-Commerce Agent Safety (Aug 2025)
- PCI DSS 4.0: Requirement 10 (monitoring/logging)
- Stripe Radar documentation (2025)
