# PCI DSS 4.0 Compliance Checklist for AI-Generated Code

> Mandatory compliance gate for any payment-handling code. Non-compliance fines: $5,000–$100,000/month.

**When to use:** Before deploying any code that processes, stores, or transmits payment data. This is a HARD GATE — payment features cannot ship without passing this checklist.
**Stack:** Any web application handling payments (Node.js, Python, etc.)

---

## The Rule

**AI-generated code must NEVER handle raw card data.** Period.

The entire purpose of Stripe Elements, Stripe Checkout, and similar tokenization services is to keep card numbers off your servers. If your server never sees a card number, you're in the simplest PCI compliance tier (SAQ A or SAQ A-EP).

The moment raw card data touches your server, you jump to SAQ D — the hardest compliance level, requiring quarterly scans, penetration testing, and extensive documentation.

---

## Scope Minimization Checklist

### Tier 1: MUST Pass (Blockers)

```
□ NO raw card numbers in server code, logs, or database
□ NO card data in URL parameters (GET requests)
□ NO card data in error messages or stack traces
□ NO card data in application logs (including debug mode)
□ NO custom card input fields (use Stripe Elements iframe)
□ NO card data stored in session/cookies
□ Stripe.js loaded from js.stripe.com (not self-hosted)
□ All payment pages served over HTTPS (no mixed content)
□ API keys stored in environment variables (never in code)
□ Secret keys never exposed to client-side code
```

### Tier 2: MUST Pass (Security)

```
□ Restricted API keys with minimal required permissions
□ Webhook signature verification on all webhook endpoints
□ CSRF protection on payment-related forms
□ Rate limiting on payment API endpoints
□ Input validation on all payment-related parameters
□ Amount validation server-side (never trust client amounts)
□ Currency validation (prevent currency confusion attacks)
```

### Tier 3: SHOULD Pass (Best Practices)

```
□ Logging of payment events (event ID and type only, no PCI data)
□ Monitoring/alerting for failed payment attempts
□ Idempotency keys on all payment mutations
□ Graceful error handling (no raw Stripe errors to users)
□ Content Security Policy headers allowing Stripe domains
□ Subresource Integrity (SRI) on Stripe.js if applicable
```

---

## Code Scanning Rules

Run these checks against any AI-generated payment code:

### Pattern 1: Card Number Detection

```
SCAN for: /\b\d{13,19}\b/ in any .js, .ts, .py, .env file
SCAN for: card_number, cardNumber, cc_number, ccNumber in variable names
SCAN for: "4242424242424242" in test files (acceptable ONLY in test config)
ALERT if: Found in server-side code, logs, or database queries
```

### Pattern 2: Secret Key Exposure

```
SCAN for: sk_live_, sk_test_ in source code files (not .env)
SCAN for: STRIPE_SECRET_KEY in client-side bundles
SCAN for: API keys in git history (git log -p | grep sk_)
ALERT if: Secret key found anywhere except .env or secrets manager
```

### Pattern 3: Raw Body Middleware

```
SCAN for: Webhook route handler
CHECK: express.raw() or equivalent used on webhook route
ALERT if: express.json() applied globally before webhook route
REASON: JSON parsing destroys the raw body needed for signature verification
```

### Pattern 4: PCI Data in Logs

```
SCAN for: console.log, logger.info, logger.debug near payment code
CHECK: No card data, CVV, expiry in logged objects
SCAN for: JSON.stringify(req.body) in payment routes
ALERT if: Full request body logged on payment endpoints
```

---

## Compliant Architecture Pattern

```
┌─────────────────────────────────────────────┐
│                  CLIENT                       │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │  Stripe Elements (iframe)                │ │
│  │  Card data NEVER leaves this iframe      │ │
│  │  → Tokenizes card → returns PaymentMethod│ │
│  └─────────────────────────────────────────┘ │
│           │ PaymentMethod ID (pm_xxx)         │
│           ▼                                   │
│  Your JavaScript (no card data here)          │
│           │ pm_xxx + order details             │
└───────────┼───────────────────────────────────┘
            │ HTTPS POST
┌───────────▼───────────────────────────────────┐
│                  SERVER                        │
│                                                │
│  Receives: pm_xxx (token), amount, currency    │
│  NEVER receives: card number, CVV, expiry      │
│                                                │
│  → Validates amount against database prices    │
│  → Creates PaymentIntent with pm_xxx           │
│  → Returns client_secret for confirmation      │
│                                                │
│  Webhook endpoint:                             │
│  → Verifies signature (express.raw body)       │
│  → Processes payment confirmation              │
│  → Updates order status                        │
└────────────────────────────────────────────────┘
```

---

## Content Security Policy for Stripe

```javascript
// Required CSP headers for Stripe Elements
const cspHeaders = {
  'Content-Security-Policy': [
    "default-src 'self'",
    "script-src 'self' https://js.stripe.com",
    "frame-src https://js.stripe.com https://hooks.stripe.com",
    "connect-src 'self' https://api.stripe.com",
    "img-src 'self' https://*.stripe.com",
  ].join('; ')
};
```

---

## Common AI-Generated Violations

| Violation | Why AI Does This | Fix |
|-----------|-----------------|-----|
| Custom `<input>` for card number | Seems simpler than Stripe Elements | Always use `CardElement` from @stripe/react-stripe-js |
| Logging `req.body` on payment routes | Standard debugging pattern | Log only event ID and type |
| `sk_test_*` in source code | Faster than env setup during prototyping | Set up .env from the start |
| Storing card last-4 in user table | Seems useful for display | Retrieve from Stripe API on demand |
| Amount from client `req.body.amount` | Trust client data pattern | Calculate from server-side price lookup |

---

## Compliance Declaration

After verification, the responsible developer signs off:

```
I verify that this payment integration:
- Never handles raw card data on our servers
- Uses Stripe's hosted tokenization (Elements/Checkout)
- Stores API keys only in environment variables
- Validates all amounts server-side
- Verifies webhook signatures
- Logs no PCI-scoped data

Signed: ________________  Date: ________
```

---

## Sources

- PCI Security Standards Council: "AI Principles — Securing the Use of AI in Payment Environments" (Spring 2025)
- PCI SSC: "New Guidance — Integrating AI into PCI Assessments" (2025)
- Stripe Documentation: Elements, Checkout, Webhooks
- PCI DSS 4.0 Requirements (mandatory March 31, 2025)
