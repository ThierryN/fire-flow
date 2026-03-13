# E-Commerce Analytics & Reporting Patterns

> Funnel analysis, customer lifetime value, cohort analysis, and revenue forecasting for e-commerce dashboards.

**When to use:** Building admin dashboards or reporting features for e-commerce systems.
**Stack:** PostgreSQL (window functions, CTEs), any charting library (Recharts, Chart.js)

---

## Core KPIs

### 1. Revenue Summary

```sql
SELECT
  DATE_TRUNC('month', created_at) as month,
  COUNT(*) as order_count,
  SUM(total) as revenue,
  AVG(total) as avg_order_value,
  COUNT(DISTINCT user_id) as unique_customers
FROM orders
WHERE status IN ('confirmed', 'processing', 'shipped', 'delivered')
  AND created_at > NOW() - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;
```

### 2. Conversion Funnel

```sql
WITH funnel AS (
  SELECT
    COUNT(DISTINCT CASE WHEN event_type = 'product_viewed' THEN session_id END) as viewed,
    COUNT(DISTINCT CASE WHEN event_type = 'item_added' THEN session_id END) as added_to_cart,
    COUNT(DISTINCT CASE WHEN event_type = 'checkout_started' THEN session_id END) as checkout,
    COUNT(DISTINCT CASE WHEN event_type = 'order_completed' THEN session_id END) as purchased
  FROM cart_events
  WHERE created_at > NOW() - INTERVAL '30 days'
)
SELECT
  viewed,
  added_to_cart,
  ROUND(added_to_cart::numeric / NULLIF(viewed, 0) * 100, 1) as view_to_cart_pct,
  checkout,
  ROUND(checkout::numeric / NULLIF(added_to_cart, 0) * 100, 1) as cart_to_checkout_pct,
  purchased,
  ROUND(purchased::numeric / NULLIF(checkout, 0) * 100, 1) as checkout_to_purchase_pct,
  ROUND(purchased::numeric / NULLIF(viewed, 0) * 100, 1) as overall_conversion_pct
FROM funnel;
```

### 3. Customer Lifetime Value (CLV)

```sql
WITH customer_stats AS (
  SELECT
    user_id,
    COUNT(*) as order_count,
    SUM(total) as total_spent,
    MIN(created_at) as first_order,
    MAX(created_at) as last_order,
    AVG(total) as avg_order_value
  FROM orders
  WHERE status NOT IN ('cancelled', 'failed', 'refunded')
  GROUP BY user_id
)
SELECT
  CASE
    WHEN total_spent > 500 THEN 'VIP (>$500)'
    WHEN total_spent > 200 THEN 'Regular ($200-500)'
    WHEN total_spent > 50 THEN 'Casual ($50-200)'
    ELSE 'New (<$50)'
  END as customer_tier,
  COUNT(*) as customer_count,
  ROUND(AVG(total_spent), 2) as avg_clv,
  ROUND(AVG(order_count), 1) as avg_orders,
  ROUND(AVG(avg_order_value), 2) as avg_order_value,
  ROUND(AVG(EXTRACT(EPOCH FROM last_order - first_order) / 86400), 0) as avg_lifespan_days
FROM customer_stats
GROUP BY 1
ORDER BY avg_clv DESC;
```

### 4. Product Performance

```sql
SELECT
  p.name,
  COUNT(oi.id) as units_sold,
  SUM(oi.total_price) as revenue,
  ROUND(AVG(oi.unit_price), 2) as avg_price,
  pv.stock_quantity as current_stock,
  ROUND(COUNT(oi.id)::numeric /
    NULLIF(EXTRACT(DAYS FROM NOW() - MIN(oi.created_at)), 0), 1) as daily_velocity
FROM order_items oi
JOIN products p ON p.id = oi.product_id
LEFT JOIN product_variants pv ON pv.product_id = p.id
JOIN orders o ON o.id = oi.order_id
WHERE o.status NOT IN ('cancelled', 'failed')
  AND o.created_at > NOW() - INTERVAL '30 days'
GROUP BY p.id, p.name, pv.stock_quantity
ORDER BY revenue DESC
LIMIT 20;
```

### 5. Cohort Retention

```sql
WITH first_purchase AS (
  SELECT user_id, DATE_TRUNC('month', MIN(created_at)) as cohort_month
  FROM orders WHERE status NOT IN ('cancelled', 'failed')
  GROUP BY user_id
),
monthly_activity AS (
  SELECT
    fp.cohort_month,
    DATE_TRUNC('month', o.created_at) as activity_month,
    COUNT(DISTINCT o.user_id) as active_customers
  FROM orders o
  JOIN first_purchase fp ON fp.user_id = o.user_id
  WHERE o.status NOT IN ('cancelled', 'failed')
  GROUP BY fp.cohort_month, DATE_TRUNC('month', o.created_at)
)
SELECT
  cohort_month,
  activity_month,
  EXTRACT(MONTH FROM activity_month - cohort_month) as months_since_first,
  active_customers,
  ROUND(active_customers::numeric / FIRST_VALUE(active_customers)
    OVER (PARTITION BY cohort_month ORDER BY activity_month) * 100, 1) as retention_pct
FROM monthly_activity
ORDER BY cohort_month, activity_month;
```

---

## API Endpoints

```javascript
// GET /api/admin/analytics/summary — Dashboard overview
router.get('/admin/analytics/summary', requireAdmin, async (req, res) => {
  const { period = '30d' } = req.query;
  const interval = period === '7d' ? '7 days' : period === '90d' ? '90 days' : '30 days';

  const [revenue, orders, customers, topProducts] = await Promise.all([
    getRevenueSummary(interval),
    getOrderStats(interval),
    getCustomerStats(interval),
    getTopProducts(interval, 10),
  ]);

  res.json({ revenue, orders, customers, topProducts, period });
});

// GET /api/admin/analytics/funnel
router.get('/admin/analytics/funnel', requireAdmin, async (req, res) => {
  const funnel = await getConversionFunnel(req.query.period || '30d');
  res.json(funnel);
});
```

---

## Sources

- Internal gap analysis: GAP-ECOM-9 (E-Commerce Analytics)
- PostgreSQL: Window functions and CTEs documentation
