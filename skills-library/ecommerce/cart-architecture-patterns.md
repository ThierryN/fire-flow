# Cart Architecture Patterns

> Server-side cart management, state synchronization, guest-to-user cart merging, and constraint verification for AI-generated e-commerce code.

**When to use:** Building any shopping cart system — from simple single-product checkout to multi-vendor marketplace carts.
**Stack:** Node.js/Express, React/Next.js, PostgreSQL/MySQL

---

## Architecture Decision: Where Does the Cart Live?

### Option 1: Server-Side Cart (Recommended for most apps)

```
Client (React)         Server (Express)         Database
┌──────────┐          ┌──────────────┐          ┌────────┐
│ Cart UI  │──POST───▶│ Cart API     │──INSERT──▶│ carts  │
│ (display │◀─JSON────│ /api/cart    │◀─SELECT───│ items  │
│  only)   │          │              │           │        │
└──────────┘          └──────────────┘          └────────┘
```

**Pros:** Single source of truth, survives page refresh/device switch, supports cart abandonment tracking
**Cons:** Every cart action requires API call, slightly slower UX without optimistic updates
**Use when:** Multi-device support needed, cart abandonment emails, server-side price validation required

### Option 2: Client-Side Cart (Simple use cases only)

```
Client (React)                     Server (Express)
┌──────────────────┐              ┌──────────────┐
│ Cart in          │──POST───────▶│ Checkout only │
│ localStorage/    │  (checkout)  │ /api/checkout │
│ React Context    │              └──────────────┘
└──────────────────┘
```

**Pros:** Instant UI, no API calls for cart operations, works offline
**Cons:** Lost on browser clear, no cross-device, no abandonment tracking, vulnerable to price manipulation
**Use when:** Simple single-page apps, digital downloads, no cart abandonment needed

### Option 3: Hybrid (Best UX)

```
Client reads from local cache (fast)
Client writes through server API (safe)
Server is source of truth
Local cache is optimistic preview
```

**Use when:** You want instant UX AND server-side safety.

---

## Database Schema

```sql
-- Carts table (one per user or session)
CREATE TABLE carts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),       -- NULL for guest carts
  session_token VARCHAR(255),               -- For guest identification
  status VARCHAR(20) DEFAULT 'active',      -- active | merged | abandoned | converted
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '30 days',
  CONSTRAINT chk_cart_owner CHECK (user_id IS NOT NULL OR session_token IS NOT NULL)
);

-- Cart items
CREATE TABLE cart_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cart_id UUID NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
  product_id UUID NOT NULL REFERENCES products(id),
  variant_id UUID REFERENCES product_variants(id),  -- Size, color, etc.
  quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
  price_at_add DECIMAL(10,2) NOT NULL,  -- Snapshot price when added
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(cart_id, product_id, variant_id)  -- One entry per product+variant
);

-- Indexes
CREATE INDEX idx_carts_user ON carts(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_carts_session ON carts(session_token) WHERE session_token IS NOT NULL;
CREATE INDEX idx_carts_status ON carts(status);
CREATE INDEX idx_cart_items_cart ON cart_items(cart_id);
```

---

## API Endpoints

```javascript
// GET /api/cart — Get current cart
router.get('/cart', async (req, res) => {
  const cart = await getOrCreateCart(req.user?.id, req.sessionToken);
  const items = await getCartItems(cart.id);

  // Validate prices are still current
  const validated = await validateCartPrices(items);

  res.json({
    cart_id: cart.id,
    items: validated.items,
    price_changes: validated.changes,  // Alert user if prices changed
    subtotal: validated.subtotal,
    item_count: validated.itemCount,
  });
});

// POST /api/cart/items — Add item
router.post('/cart/items', async (req, res) => {
  const { product_id, variant_id, quantity } = req.body;

  // ALWAYS validate price server-side
  const product = await getProduct(product_id);
  if (!product || !product.is_active) {
    return res.status(404).json({ error: 'Product not available' });
  }

  // Check stock
  const available = await checkStock(product_id, variant_id, quantity);
  if (!available) {
    return res.status(409).json({ error: 'Insufficient stock', available: available.count });
  }

  const cart = await getOrCreateCart(req.user?.id, req.sessionToken);
  const item = await addToCart(cart.id, product_id, variant_id, quantity, product.price);

  res.json({ item, cart_total: await getCartTotal(cart.id) });
});

// PATCH /api/cart/items/:id — Update quantity
router.patch('/cart/items/:id', async (req, res) => {
  const { quantity } = req.body;
  if (quantity < 1) {
    return res.status(400).json({ error: 'Quantity must be at least 1' });
  }
  // Re-check stock at new quantity
  const item = await getCartItem(req.params.id);
  const available = await checkStock(item.product_id, item.variant_id, quantity);
  if (!available) {
    return res.status(409).json({ error: 'Insufficient stock' });
  }
  const updated = await updateCartItemQuantity(req.params.id, quantity);
  res.json(updated);
});

// DELETE /api/cart/items/:id — Remove item
router.delete('/cart/items/:id', async (req, res) => {
  await removeCartItem(req.params.id);
  res.json({ removed: true });
});
```

---

## Cart Merge on Login

When a guest user logs in, their anonymous cart must merge with their account cart:

```javascript
async function mergeCartsOnLogin(userId, sessionToken) {
  const guestCart = await getCartBySession(sessionToken);
  const userCart = await getCartByUser(userId);

  if (!guestCart || guestCart.items.length === 0) return userCart;
  if (!userCart) {
    // Simple case: assign guest cart to user
    await db.query('UPDATE carts SET user_id = $1, session_token = NULL WHERE id = $2',
      [userId, guestCart.id]);
    return guestCart;
  }

  // Merge: guest items into user cart
  for (const guestItem of guestCart.items) {
    const existingItem = userCart.items.find(
      i => i.product_id === guestItem.product_id && i.variant_id === guestItem.variant_id
    );

    if (existingItem) {
      // Same product: take higher quantity (guest was shopping more recently)
      const newQty = Math.max(existingItem.quantity, guestItem.quantity);
      await updateCartItemQuantity(existingItem.id, newQty);
    } else {
      // New product: add to user cart
      await addToCart(userCart.id, guestItem.product_id, guestItem.variant_id,
        guestItem.quantity, guestItem.price_at_add);
    }
  }

  // Mark guest cart as merged
  await db.query("UPDATE carts SET status = 'merged' WHERE id = $1", [guestCart.id]);

  return await getCartByUser(userId);
}
```

---

## Price Validation at Checkout

Never trust the cart's stored prices at checkout time — always re-validate:

```javascript
async function validateCartForCheckout(cartId) {
  const items = await getCartItems(cartId);
  const issues = [];

  for (const item of items) {
    const currentProduct = await getProduct(item.product_id);

    // Product still exists and is active?
    if (!currentProduct || !currentProduct.is_active) {
      issues.push({ item_id: item.id, type: 'unavailable', message: `${item.name} is no longer available` });
      continue;
    }

    // Price changed?
    if (currentProduct.price !== item.price_at_add) {
      issues.push({
        item_id: item.id, type: 'price_change',
        old_price: item.price_at_add, new_price: currentProduct.price,
        message: `Price changed from $${item.price_at_add} to $${currentProduct.price}`
      });
    }

    // Still in stock?
    const stock = await checkStock(item.product_id, item.variant_id, item.quantity);
    if (!stock.available) {
      issues.push({
        item_id: item.id, type: 'stock',
        requested: item.quantity, available: stock.count,
        message: `Only ${stock.count} available (you have ${item.quantity})`
      });
    }
  }

  return { valid: issues.length === 0, issues };
}
```

---

## Session Token Middleware

```javascript
function cartSessionMiddleware(req, res, next) {
  // Authenticated users use their user ID
  if (req.user) {
    req.cartIdentifier = { user_id: req.user.id };
    return next();
  }

  // Guest users get a session token
  let sessionToken = req.cookies?.cart_session;
  if (!sessionToken) {
    sessionToken = crypto.randomUUID();
    res.cookie('cart_session', sessionToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 30 * 24 * 60 * 60 * 1000,  // 30 days
    });
  }
  req.cartIdentifier = { session_token: sessionToken };
  req.sessionToken = sessionToken;
  next();
}
```

---

## Constraint Verification Checklist

Before marking any cart feature complete:

```
□ Prices validated server-side (never from client)
□ Stock checked before adding and at checkout
□ Race condition handled (two users buy last item)
□ Cart expires after configurable period (default 30 days)
□ Guest cart merges correctly on login
□ Price changes shown to user before checkout
□ Unavailable products removed/flagged at checkout
□ Quantity limits enforced (min 1, max per product policy)
□ Cart total calculated server-side (not client sum)
□ Session token is httpOnly, secure, sameSite
```

---

## Sources

- ShoppingComp (arXiv:2511.22978) — LLM Shopping Cart Benchmark (Nov 2025)
- WebMall (arXiv:2508.13024) — Multi-Shop E-Commerce Agent Benchmark (Aug 2025)
- ShoppingBench (arXiv:2508.04266) — Intent-Grounded Shopping Agent Benchmark (Aug 2025)
- Adobe Commerce: `mergeCarts` GraphQL mutation reference
- WooCommerce: Cart data flow documentation (2025)
