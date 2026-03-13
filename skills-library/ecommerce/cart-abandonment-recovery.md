# Cart Abandonment Recovery Patterns

> Exit-intent detection, recovery emails, and session analytics to recover 15-25% of abandoned cart revenue.

**When to use:** Any e-commerce system with a checkout flow. Global cart abandonment rate is 70.22% ($260B recoverable US revenue annually).
**Stack:** Node.js/Express, React, email service (SendGrid/Resend), optional analytics

---

## Why Carts Are Abandoned

| Reason | % of Abandonments | Fix |
|--------|-------------------|-----|
| Extra costs too high (shipping, tax) | 49% | Show total upfront |
| Required account creation | 24% | Guest checkout |
| Complex checkout process | 18% | Reduce steps |
| Couldn't calculate total | 17% | Show running total |
| Didn't trust site with card | 17% | Trust signals |
| Delivery too slow | 16% | Show delivery date |
| Website errors | 13% | Test checkout flow |

---

## Pattern 1: Recovery Email Sequence

### Trigger: Cart inactive for X minutes

```javascript
// Check for abandoned carts (run every 15 minutes via cron)
async function findAbandonedCarts() {
  const abandoned = await db.query(
    `SELECT c.*, u.email, u.first_name
     FROM carts c
     JOIN users u ON u.id = c.user_id
     WHERE c.status = 'active'
       AND c.updated_at < NOW() - INTERVAL '1 hour'
       AND c.updated_at > NOW() - INTERVAL '7 days'
       AND c.id NOT IN (SELECT cart_id FROM cart_recovery_emails WHERE sent_at > NOW() - INTERVAL '24 hours')
       AND (SELECT COUNT(*) FROM cart_items WHERE cart_id = c.id) > 0`,
  );
  return abandoned.rows;
}

// Send recovery sequence
async function sendRecoveryEmail(cart, emailNumber) {
  const items = await getCartItems(cart.id);
  const templates = {
    1: { // 1 hour after abandonment
      subject: `You left something behind`,
      delay: '1 hour',
      includeDiscount: false,
    },
    2: { // 24 hours
      subject: `Still thinking about it?`,
      delay: '24 hours',
      includeDiscount: false,
    },
    3: { // 72 hours — include incentive
      subject: `10% off your cart — just for you`,
      delay: '72 hours',
      includeDiscount: true,
      discountPercent: 10,
    },
  };

  const template = templates[emailNumber];

  await sendEmail({
    to: cart.email,
    subject: template.subject,
    template: 'cart-recovery',
    data: {
      firstName: cart.first_name,
      items: items.map(i => ({
        name: i.name,
        image: i.image_url,
        price: i.price,
        quantity: i.quantity,
      })),
      cartUrl: `${process.env.BASE_URL}/cart?recover=${cart.id}`,
      discount: template.includeDiscount ? {
        code: await generateDiscountCode(cart.user_id, template.discountPercent),
        percent: template.discountPercent,
        expires: '48 hours',
      } : null,
      subtotal: items.reduce((sum, i) => sum + i.price * i.quantity, 0),
    },
  });

  await db.query(
    `INSERT INTO cart_recovery_emails (cart_id, email_number, sent_at) VALUES ($1, $2, NOW())`,
    [cart.id, emailNumber]
  );
}
```

### Recovery Email Schema

```sql
CREATE TABLE cart_recovery_emails (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cart_id UUID NOT NULL REFERENCES carts(id),
  email_number INTEGER NOT NULL,  -- 1, 2, or 3
  sent_at TIMESTAMP DEFAULT NOW(),
  opened_at TIMESTAMP,
  clicked_at TIMESTAMP,
  converted BOOLEAN DEFAULT false
);

CREATE INDEX idx_recovery_cart ON cart_recovery_emails(cart_id);
```

---

## Pattern 2: Exit-Intent Detection (Client-Side)

```javascript
// Detect when user is about to leave checkout
function useExitIntent(onExitIntent) {
  useEffect(() => {
    const handleMouseLeave = (e) => {
      // Mouse moves toward browser chrome (top of viewport)
      if (e.clientY <= 0) {
        onExitIntent();
      }
    };

    // Desktop: mouse leaving viewport
    document.addEventListener('mouseleave', handleMouseLeave);

    // Mobile: detect back button or tab switch
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        onExitIntent();
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('mouseleave', handleMouseLeave);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [onExitIntent]);
}

// Usage in checkout component
function Checkout() {
  const [showExitModal, setShowExitModal] = useState(false);

  useExitIntent(() => {
    if (!showExitModal) {
      setShowExitModal(true);
      // Track event
      analytics.track('exit_intent_triggered', { page: 'checkout' });
    }
  });

  return (
    <>
      <CheckoutForm />
      {showExitModal && (
        <Modal onClose={() => setShowExitModal(false)}>
          <h2>Wait! Your cart is saved</h2>
          <p>Complete your purchase now or we'll email you a reminder.</p>
          <Button onClick={() => setShowExitModal(false)}>Continue Checkout</Button>
          <Button variant="secondary" onClick={saveCartAndEmail}>
            Email me my cart
          </Button>
        </Modal>
      )}
    </>
  );
}
```

---

## Pattern 3: Cart Analytics

Track the checkout funnel to find where users drop off:

```javascript
// Server-side event tracking
async function trackCartEvent(userId, sessionId, event, metadata = {}) {
  await db.query(
    `INSERT INTO cart_events (user_id, session_id, event_type, metadata, created_at)
     VALUES ($1, $2, $3, $4, NOW())`,
    [userId, sessionId, event, JSON.stringify(metadata)]
  );
}

// Events to track:
// cart_viewed, item_added, item_removed, quantity_changed,
// checkout_started, shipping_entered, payment_entered,
// order_completed, exit_intent_triggered, recovery_email_opened,
// recovery_email_clicked, recovery_converted
```

### Funnel Query

```sql
SELECT
  event_type,
  COUNT(DISTINCT session_id) as sessions,
  ROUND(
    COUNT(DISTINCT session_id)::numeric /
    FIRST_VALUE(COUNT(DISTINCT session_id)) OVER (ORDER BY
      CASE event_type
        WHEN 'cart_viewed' THEN 1
        WHEN 'checkout_started' THEN 2
        WHEN 'payment_entered' THEN 3
        WHEN 'order_completed' THEN 4
      END
    ) * 100, 1
  ) as conversion_pct
FROM cart_events
WHERE created_at > NOW() - INTERVAL '30 days'
  AND event_type IN ('cart_viewed', 'checkout_started', 'payment_entered', 'order_completed')
GROUP BY event_type
ORDER BY
  CASE event_type
    WHEN 'cart_viewed' THEN 1
    WHEN 'checkout_started' THEN 2
    WHEN 'payment_entered' THEN 3
    WHEN 'order_completed' THEN 4
  END;
```

---

## Sources

- MDPI: Consumer Purchase Behavior Analysis with XAI/SHAP (Feb 2025) — 89% F1 score
- Quickchat AI: Cart abandonment strategy (2025) — 15-25% recovery
- Bloomreach: AI cart abandonment prevention (2025)
- Booking.com: AI chatbot case study — 20% conversion increase (2025)
