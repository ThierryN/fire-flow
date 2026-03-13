# Shipping & Carrier Integration Patterns

> Rate lookups, label generation, tracking sync, and returns handling for e-commerce fulfillment.

**When to use:** Building any e-commerce system that ships physical products. Applies during the fulfillment phase of order processing.
**Stack:** Node.js/Express, EasyPost or ShipStation API (recommended), or direct carrier APIs

---

## Architecture Decision: Direct vs Aggregator

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **Direct carrier APIs** (FedEx, UPS, USPS) | Full control, no middleman fees | Each carrier = separate integration, different APIs | High volume, single carrier |
| **Aggregator** (EasyPost, ShipStation, Shippo) | One API for all carriers, label generation, tracking | Monthly cost, slight markup on rates | Most e-commerce projects |

**Recommendation:** Use an aggregator unless you have a specific reason not to. EasyPost is developer-friendly with a good free tier.

---

## EasyPost Integration (Recommended)

```bash
npm install @easypost/api
```

### Rate Shopping

```javascript
import EasyPost from '@easypost/api';
const client = new EasyPost(process.env.EASYPOST_API_KEY);

async function getRates(fromAddress, toAddress, parcel) {
  const shipment = await client.Shipment.create({
    from_address: {
      street1: fromAddress.street,
      city: fromAddress.city,
      state: fromAddress.state,
      zip: fromAddress.zip,
      country: fromAddress.country || 'US',
    },
    to_address: {
      street1: toAddress.street,
      city: toAddress.city,
      state: toAddress.state,
      zip: toAddress.zip,
      country: toAddress.country || 'US',
    },
    parcel: {
      length: parcel.length,  // inches
      width: parcel.width,
      height: parcel.height,
      weight: parcel.weight,  // ounces
    },
  });

  // Return sorted rates
  return shipment.rates
    .map(rate => ({
      id: rate.id,
      carrier: rate.carrier,           // 'USPS', 'FedEx', 'UPS'
      service: rate.service,           // 'Priority', 'Ground', 'Express'
      rate: parseFloat(rate.rate),     // Dollar amount
      est_delivery_days: rate.est_delivery_days,
      delivery_date: rate.delivery_date,
    }))
    .sort((a, b) => a.rate - b.rate);
}
```

### Buy Label

```javascript
async function buyShippingLabel(shipmentId, rateId) {
  const shipment = await client.Shipment.retrieve(shipmentId);
  const purchased = await shipment.buy(rateId);

  return {
    tracking_number: purchased.tracking_code,
    tracking_url: purchased.tracker?.public_url,
    label_url: purchased.postage_label.label_url,
    label_format: purchased.postage_label.label_file_type, // 'PDF' or 'PNG'
    carrier: purchased.selected_rate.carrier,
    service: purchased.selected_rate.service,
    cost: parseFloat(purchased.selected_rate.rate),
  };
}
```

### Track Package

```javascript
async function trackPackage(trackingNumber, carrier) {
  const tracker = await client.Tracker.create({
    tracking_code: trackingNumber,
    carrier: carrier,
  });

  return {
    status: tracker.status,                    // 'in_transit', 'delivered', etc.
    est_delivery: tracker.est_delivery_date,
    tracking_details: tracker.tracking_details.map(d => ({
      status: d.status,
      message: d.message,
      datetime: d.datetime,
      city: d.tracking_location?.city,
      state: d.tracking_location?.state,
    })),
  };
}
```

---

## Shipping API Endpoints

```javascript
// POST /api/orders/:id/shipping/rates — Get available rates
router.post('/orders/:id/shipping/rates', requireAuth, async (req, res) => {
  const order = await getOrder(req.params.id);
  const warehouse = await getWarehouseAddress();

  const rates = await getRates(warehouse, order.shipping_address, {
    length: 12, width: 8, height: 6,
    weight: calculateOrderWeight(order.items),
  });

  res.json({ rates });
});

// POST /api/orders/:id/shipping/purchase — Buy label
router.post('/orders/:id/shipping/purchase', requireAdmin, async (req, res) => {
  const { rate_id, shipment_id } = req.body;

  const label = await buyShippingLabel(shipment_id, rate_id);

  await db.query(
    `UPDATE orders SET
       tracking_number = $1, tracking_url = $2,
       shipping_label_url = $3, shipping_carrier = $4,
       shipping_cost = $5, status = 'shipped', shipped_at = NOW()
     WHERE id = $6`,
    [label.tracking_number, label.tracking_url, label.label_url,
     label.carrier, label.cost, req.params.id]
  );

  await sendShippingNotification(req.params.id, label);
  res.json({ label });
});

// GET /api/orders/:id/tracking — Get tracking info
router.get('/orders/:id/tracking', requireAuth, async (req, res) => {
  const order = await getOrder(req.params.id);
  if (!order.tracking_number) {
    return res.json({ status: 'not_shipped' });
  }

  const tracking = await trackPackage(order.tracking_number, order.shipping_carrier);
  res.json(tracking);
});
```

---

## Free Shipping Threshold

```javascript
function calculateShipping(subtotal, shippingRate) {
  const FREE_SHIPPING_THRESHOLD = parseFloat(process.env.FREE_SHIPPING_THRESHOLD || '75');

  if (subtotal >= FREE_SHIPPING_THRESHOLD) {
    return { cost: 0, reason: 'free_shipping_threshold' };
  }

  return {
    cost: shippingRate,
    free_shipping_at: FREE_SHIPPING_THRESHOLD,
    remaining: FREE_SHIPPING_THRESHOLD - subtotal,
  };
}
```

---

## Return Labels

```javascript
async function createReturnLabel(orderId) {
  const order = await getOrder(orderId);
  const warehouse = await getWarehouseAddress();

  // Reverse: customer → warehouse
  const shipment = await client.Shipment.create({
    from_address: order.shipping_address,
    to_address: warehouse,
    parcel: { length: 12, width: 8, height: 6, weight: 16 },
    is_return: true,
  });

  // Buy cheapest option
  const cheapest = shipment.rates.sort((a, b) => a.rate - b.rate)[0];
  const label = await shipment.buy(cheapest.id);

  return {
    tracking_number: label.tracking_code,
    label_url: label.postage_label.label_url,
    cost: parseFloat(cheapest.rate),
  };
}
```

---

## Sources

- Internal gap analysis: GAP-ECOM-8 (Shipping & Carrier Integration)
- EasyPost API Documentation (2025)
- ShipStation API Documentation (2025)
