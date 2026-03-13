# Composable Commerce Architecture Selection Guide

> Decision tree for choosing between monolithic, headless, and composable commerce architectures based on project requirements.

**When to use:** Starting a new e-commerce project or evaluating whether to migrate from a monolithic platform. Use during the planning phase to make the architecture decision explicit.
**Stack:** Framework-agnostic (the decision determines the stack)

---

## Architecture Spectrum

```
Simple ◀────────────────────────────────────────────▶ Complex

┌──────────┐    ┌──────────┐    ┌────────────────┐
│ Monolithic│    │ Headless │    │  Composable    │
│ (Shopify, │    │ (Medusa, │    │  (Mix-and-match│
│  WooComm) │    │  Saleor) │    │   best APIs)  │
└──────────┘    └──────────┘    └────────────────┘
     │                │                  │
 All-in-one      Decouple          Decouple
 frontend +      frontend           EVERYTHING
 backend         from backend
```

---

## Decision Tree

### Question 1: Who are your customers?

```
IF single storefront (web only):
  → Monolithic or Headless both work
IF multi-channel (web + mobile + email + kiosks):
  → Headless or Composable (monolithic can't serve multiple frontends)
IF B2B + B2C or marketplace:
  → Composable (different channels have different business logic)
```

### Question 2: How fast do you need to launch?

```
IF < 2 weeks to MVP:
  → Monolithic (Shopify, WooCommerce, Squarespace)
IF 1-3 months:
  → Headless (Medusa.js, Saleor, Shopify Hydrogen)
IF 3+ months, complex requirements:
  → Composable (custom API composition)
```

### Question 3: How custom is your business logic?

```
IF standard catalog + checkout:
  → Monolithic (no need to reinvent)
IF custom pricing, subscriptions, or workflows:
  → Headless (customize backend, own frontend)
IF unique fulfillment, multi-vendor, or complex tax rules:
  → Composable (swap individual components)
```

### Question 4: What's your team's capability?

```
IF non-technical or small team:
  → Monolithic (hosted, managed, minimal code)
IF full-stack developers:
  → Headless (you build the frontend, platform handles commerce)
IF platform/infra team:
  → Composable (you manage multiple services)
```

---

## Platform Comparison

| Feature | Shopify | Medusa.js v2 | Saleor | Composable |
|---------|---------|-------------|--------|------------|
| **Type** | Monolithic (+ Hydrogen headless) | Headless | Headless | Architecture pattern |
| **Frontend** | Themes or Hydrogen (React) | Any | Any | Any |
| **API** | REST + GraphQL | REST + JS SDK | GraphQL only | Mix |
| **Database** | Managed | PostgreSQL | PostgreSQL | Per-service |
| **Payments** | Shopify Payments + 100+ | Stripe module | Stripe/Adyen | Any |
| **Self-host** | No (SaaS) | Yes (open source) | Yes (open source) | Yes |
| **Pricing** | $29-$299/mo + transaction fees | Free (self-host) | Free (self-host) | Varies |
| **Best for** | Quick launch, non-technical | Custom commerce, developers | GraphQL-first, multi-channel | Enterprise, multi-vendor |

---

## Medusa.js v2 Quick Reference

Medusa 2.0 uses composable Workflows made of atomic Steps:

```typescript
// Example: Custom checkout workflow
import { createWorkflow, createStep } from "@medusajs/workflows-sdk";

const validateCartStep = createStep("validate-cart", async (input) => {
  // Validate cart items, prices, stock
  return { valid: true };
});

const capturePaymentStep = createStep("capture-payment", async (input) => {
  // Capture payment via Stripe module
  return { payment_id: "pi_xxx" };
}, {
  // Compensating action if later steps fail
  compensate: async (input) => {
    await refundPayment(input.payment_id);
  }
});

export const checkoutWorkflow = createWorkflow("checkout", (input) => {
  const validation = validateCartStep(input);
  const payment = capturePaymentStep(input);
  return { validation, payment };
});
```

---

## Saleor Quick Reference

GraphQL-native, variant-based checkout:

```graphql
# Create checkout with variant IDs (not product IDs)
mutation {
  checkoutCreate(input: {
    lines: [
      { variantId: "VmFyaWFudDox", quantity: 2 }
    ]
    email: "customer@example.com"
  }) {
    checkout {
      id
      totalPrice { gross { amount currency } }
    }
    errors { field message }
  }
}
```

---

## Recommendation by Project Type

| Project Type | Recommended | Why |
|-------------|-------------|-----|
| Landing page + buy button | Shopify | Fastest to revenue |
| Custom SaaS with billing | Stripe Checkout (no platform) | Direct integration |
| Online course platform | Headless (Medusa/custom) | Custom enrollment logic |
| Marketplace | Composable | Multi-vendor, complex fulfillment |
| Church/nonprofit store | WooCommerce or Shopify | Low cost, familiar |
| B2B with custom pricing | Composable | Price tiers, quotes, contracts |

---

## Sources

- composable.com: "Composable Commerce in 2025" (2025)
- composable.com: "Headless vs Composable Commerce" (2025)
- Medusa.js v2 Architecture Documentation (2025)
- Saleor API Documentation (2025)
- Shopify Hydrogen Winter '26 Update (2025)
