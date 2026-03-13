# Agentic Commerce Protocol (ACP)

> Open standard for AI agents to discover products, initiate checkouts, and complete purchases programmatically.

**When to use:** Building any e-commerce system that should be accessible to AI shopping agents (ChatGPT, Perplexity Shopping, Claude), or integrating AI purchasing capabilities into your own agents.
**Stack:** Any web framework + Stripe (ACP is Stripe-native)

---

## What Is ACP?

Traditional e-commerce: **Human browses website → clicks "Buy" → enters payment**
Agentic commerce: **AI agent discovers product via API → negotiates terms → completes purchase programmatically**

ACP defines a standard protocol so:
1. Merchants expose product catalogs in a machine-readable format
2. AI agents can browse, compare, and purchase without scraping HTML
3. Payment credentials are shared securely via SharedPaymentTokens (SPT)
4. Merchants retain full control of branding, pricing, and fulfillment

---

## Architecture

```
┌─────────────────────────┐     ┌─────────────────────────┐
│     AI Shopping Agent    │     │      Merchant Server     │
│ (ChatGPT, your agent)   │     │                          │
│                          │     │ ┌──────────────────────┐ │
│ 1. Discover products ────┼────▶│ │ ACP Product Catalog  │ │
│                          │     │ │ /acp/products        │ │
│ 2. Get pricing/terms ◀───┼─────│ │ /acp/pricing         │ │
│                          │     │ └──────────────────────┘ │
│ 3. Initiate checkout ────┼────▶│ ┌──────────────────────┐ │
│    (with SPT)            │     │ │ ACP Checkout          │ │
│                          │     │ │ /acp/checkout         │ │
│ 4. Confirm order ◀───────┼─────│ │ → Stripe payment     │ │
│                          │     │ └──────────────────────┘ │
└─────────────────────────┘     └─────────────────────────┘
```

---

## For Merchants: Making Your Store Agent-Accessible

### Step 1: Product Catalog Endpoint

Expose your products in a structured, machine-readable format:

```javascript
// GET /acp/products
router.get('/acp/products', async (req, res) => {
  const { category, query, limit = 20, offset = 0 } = req.query;

  const products = await db.query(
    `SELECT id, name, description, price, currency, images, category,
            availability, variants, attributes
     FROM products
     WHERE is_active = true
     ${category ? 'AND category = $1' : ''}
     ORDER BY name
     LIMIT $${category ? 2 : 1} OFFSET $${category ? 3 : 2}`,
    category ? [category, parseInt(limit), parseInt(offset)]
             : [parseInt(limit), parseInt(offset)]
  );

  res.json({
    products: products.rows.map(p => ({
      id: p.id,
      name: p.name,
      description: p.description,
      price: { amount: p.price, currency: p.currency },
      images: p.images,
      category: p.category,
      availability: p.availability,
      variants: p.variants,
      attributes: p.attributes,  // size, color, material, etc.
    })),
    pagination: { limit: parseInt(limit), offset: parseInt(offset), total: products.rowCount },
  });
});
```

### Step 2: Checkout Endpoint

Allow agents to initiate purchases programmatically:

```javascript
// POST /acp/checkout
router.post('/acp/checkout', async (req, res) => {
  const { items, shipping_address, payment_token } = req.body;

  // Validate items and get current prices
  const validated = await validateAndPriceItems(items);
  if (!validated.valid) {
    return res.status(400).json({ error: validated.errors });
  }

  // Create Stripe Checkout Session
  const session = await stripe.checkout.sessions.create({
    line_items: validated.lineItems,
    mode: 'payment',
    shipping_address_collection: shipping_address ? undefined : { allowed_countries: ['US'] },
    success_url: `${process.env.BASE_URL}/order/confirmed/{CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.BASE_URL}/order/cancelled`,
    metadata: { source: 'acp', agent_id: req.headers['x-agent-id'] || 'unknown' },
  });

  res.json({
    checkout_url: session.url,
    session_id: session.id,
    expires_at: new Date(session.expires_at * 1000).toISOString(),
    total: validated.total,
  });
});
```

### Step 3: Agent-Readable Product Schema

Use structured data (JSON-LD) to make products discoverable:

```html
<!-- Add to product pages for web-crawling agents -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Product Name",
  "description": "Product description",
  "offers": {
    "@type": "Offer",
    "price": "29.99",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock"
  }
}
</script>
```

---

## For AI Agent Developers: Consuming ACP

```javascript
// Example: AI agent purchasing from an ACP-enabled merchant
async function purchaseProduct(merchantUrl, productId, quantity) {
  // 1. Get product details
  const product = await fetch(`${merchantUrl}/acp/products/${productId}`);
  const productData = await product.json();

  // 2. Initiate checkout
  const checkout = await fetch(`${merchantUrl}/acp/checkout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Agent-Id': 'your-agent-id',
    },
    body: JSON.stringify({
      items: [{ product_id: productId, quantity }],
    }),
  });
  const checkoutData = await checkout.json();

  // 3. Return checkout URL for user to complete payment
  return {
    checkout_url: checkoutData.checkout_url,
    total: checkoutData.total,
    expires_at: checkoutData.expires_at,
  };
}
```

---

## Design Principles

1. **Merchants retain control** — pricing, branding, fulfillment stay with the merchant
2. **Agents are intermediaries** — they help users find and purchase, not bypass the merchant
3. **Structured over scraped** — API endpoints beat HTML parsing for reliability
4. **Payment security** — use Stripe's tokenization, never handle raw card data
5. **Agent identification** — track which AI agent initiated a purchase for analytics

---

## Integration with Stripe Agent Toolkit

For existing Stripe merchants, ACP integration can be minimal:

```bash
npm install @stripe/agent-toolkit
```

The toolkit already provides tools for creating products, prices, payment links, and checkout sessions — all ACP needs is a structured catalog endpoint on top of this.

---

## Sources

- Stripe/OpenAI: "Developing an open standard for agentic commerce" (October 2025)
- GitHub: agentic-commerce-protocol/agentic-commerce-protocol (Apache 2.0)
- Stripe: "Agentic Commerce Suite" blog post (2025)
- commercetools: "7 AI Trends Shaping Agentic Commerce" (2025)
- Envive AI: "46 E-Commerce AI Statistics" (2025)
