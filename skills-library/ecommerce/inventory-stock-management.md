# Inventory & Stock Management Patterns

> Race condition prevention, stock reservation, multi-channel sync, and variant tracking for e-commerce systems.

**When to use:** Building any e-commerce system that tracks product quantities — especially when multiple users can purchase simultaneously or products sell across multiple channels.
**Stack:** Node.js/Express, PostgreSQL (row-level locking), Redis (optional for caching)

---

## The Core Problem: Race Conditions

Two customers see "1 left in stock" → both click "Buy" → both get confirmation → one order can't be fulfilled.

---

## Pattern 1: Pessimistic Locking (PostgreSQL FOR UPDATE)

Lock the row while checking and decrementing stock:

```javascript
async function reserveStock(productId, variantId, quantity, orderId) {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    // Lock the row — other transactions wait
    const result = await client.query(
      `SELECT stock_quantity FROM product_variants
       WHERE product_id = $1 AND id = $2
       FOR UPDATE`,
      [productId, variantId]
    );

    if (!result.rows[0]) throw new Error('Variant not found');

    const available = result.rows[0].stock_quantity;
    if (available < quantity) {
      await client.query('ROLLBACK');
      return { success: false, available, requested: quantity };
    }

    // Decrement stock
    await client.query(
      `UPDATE product_variants
       SET stock_quantity = stock_quantity - $1, updated_at = NOW()
       WHERE product_id = $2 AND id = $3`,
      [quantity, productId, variantId]
    );

    // Record reservation
    await client.query(
      `INSERT INTO inventory_reservations (product_id, variant_id, quantity, order_id, status)
       VALUES ($1, $2, $3, $4, 'reserved')`,
      [productId, variantId, quantity, orderId]
    );

    await client.query('COMMIT');
    return { success: true, remaining: available - quantity };
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}
```

### When to use: High-value items, limited stock (concert tickets, flash sales)

---

## Pattern 2: Optimistic Locking (Version Column)

Check-and-set without holding locks:

```javascript
async function reserveStockOptimistic(productId, variantId, quantity) {
  const maxRetries = 3;
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    const current = await db.query(
      `SELECT stock_quantity, version FROM product_variants
       WHERE product_id = $1 AND id = $2`,
      [productId, variantId]
    );

    if (current.rows[0].stock_quantity < quantity) {
      return { success: false, available: current.rows[0].stock_quantity };
    }

    // Update only if version matches (no one else changed it)
    const result = await db.query(
      `UPDATE product_variants
       SET stock_quantity = stock_quantity - $1, version = version + 1, updated_at = NOW()
       WHERE product_id = $2 AND id = $3 AND version = $4
       RETURNING stock_quantity`,
      [quantity, productId, variantId, current.rows[0].version]
    );

    if (result.rowCount > 0) {
      return { success: true, remaining: result.rows[0].stock_quantity };
    }
    // Version mismatch — someone else updated, retry
  }
  return { success: false, reason: 'concurrent_modification' };
}
```

### When to use: General e-commerce, moderate traffic

---

## Pattern 3: Atomic Decrement (Simplest)

Single atomic UPDATE — no locks, no versions:

```sql
UPDATE product_variants
SET stock_quantity = stock_quantity - $1
WHERE product_id = $2 AND id = $3
  AND stock_quantity >= $1
RETURNING stock_quantity;
```

```javascript
async function reserveStockAtomic(productId, variantId, quantity) {
  const result = await db.query(
    `UPDATE product_variants
     SET stock_quantity = stock_quantity - $1, updated_at = NOW()
     WHERE product_id = $2 AND id = $3 AND stock_quantity >= $1
     RETURNING stock_quantity`,
    [quantity, productId, variantId]
  );

  if (result.rowCount === 0) {
    const current = await db.query(
      'SELECT stock_quantity FROM product_variants WHERE product_id = $1 AND id = $2',
      [productId, variantId]
    );
    return { success: false, available: current.rows[0]?.stock_quantity || 0 };
  }
  return { success: true, remaining: result.rows[0].stock_quantity };
}
```

### When to use: Most cases. Simple, fast, race-condition-safe.

---

## Database Schema

```sql
CREATE TABLE product_variants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL REFERENCES products(id),
  sku VARCHAR(100) UNIQUE,
  name VARCHAR(255),             -- "Large / Blue"
  attributes JSONB DEFAULT '{}', -- {"size": "L", "color": "Blue"}
  price DECIMAL(10,2) NOT NULL,
  stock_quantity INTEGER NOT NULL DEFAULT 0,
  low_stock_threshold INTEGER DEFAULT 5,
  track_inventory BOOLEAN DEFAULT true,
  allow_backorder BOOLEAN DEFAULT false,
  version INTEGER DEFAULT 1,     -- For optimistic locking
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE inventory_reservations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL,
  variant_id UUID,
  quantity INTEGER NOT NULL,
  order_id UUID NOT NULL,
  status VARCHAR(20) DEFAULT 'reserved',  -- reserved | committed | released | expired
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '30 minutes'
);

CREATE TABLE inventory_movements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL,
  variant_id UUID,
  quantity INTEGER NOT NULL,     -- Positive = stock in, negative = stock out
  movement_type VARCHAR(30),     -- purchase | return | adjustment | restock | damage
  reference_id UUID,             -- Order ID or adjustment ID
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_variants_product ON product_variants(product_id);
CREATE INDEX idx_variants_sku ON product_variants(sku);
CREATE INDEX idx_variants_low_stock ON product_variants(stock_quantity)
  WHERE track_inventory = true;
CREATE INDEX idx_reservations_expiry ON inventory_reservations(expires_at)
  WHERE status = 'reserved';
CREATE INDEX idx_movements_product ON inventory_movements(product_id, created_at);
```

---

## Low Stock Alerts

```javascript
async function checkLowStock() {
  const lowItems = await db.query(
    `SELECT pv.*, p.name as product_name
     FROM product_variants pv
     JOIN products p ON p.id = pv.product_id
     WHERE pv.track_inventory = true
       AND pv.stock_quantity <= pv.low_stock_threshold
       AND pv.stock_quantity > 0
     ORDER BY pv.stock_quantity ASC`
  );

  if (lowItems.rows.length > 0) {
    await sendAdminAlert({
      type: 'LOW_STOCK',
      items: lowItems.rows.map(i => ({
        product: i.product_name,
        variant: i.name,
        sku: i.sku,
        remaining: i.stock_quantity,
        threshold: i.low_stock_threshold,
      })),
    });
  }
}

// Run hourly via cron
```

---

## Reservation Expiry

Clean up abandoned reservations (cart timeout):

```javascript
async function expireReservations() {
  const expired = await db.query(
    `UPDATE inventory_reservations
     SET status = 'expired'
     WHERE status = 'reserved' AND expires_at < NOW()
     RETURNING product_id, variant_id, quantity`
  );

  // Restore stock for expired reservations
  for (const row of expired.rows) {
    await db.query(
      `UPDATE product_variants
       SET stock_quantity = stock_quantity + $1
       WHERE product_id = $2 AND id = $3`,
      [row.quantity, row.product_id, row.variant_id]
    );
  }

  return { expired: expired.rowCount };
}

// Run every 5 minutes via cron
```

---

## Sources

- Internal gap analysis: GAP-ECOM-7 (Inventory & Stock Management)
- PostgreSQL: Row-level locking (SELECT FOR UPDATE) documentation
- Medusa.js: Inventory Module architecture (2025)
