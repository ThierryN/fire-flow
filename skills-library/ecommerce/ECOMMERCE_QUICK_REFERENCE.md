# E-Commerce Quick Reference Card
**Purpose**: One-page lookup for commands, endpoints, and common tasks
**Updated**: October 26, 2025

---

## 🚀 Quick Start Commands

```bash
# Start development server
npm run dev

# Run migrations
node runMigration.js

# Test database connection
node test-db-connection.js

# View server logs
npm run logs
```

---

## 📡 API Endpoints Cheat Sheet

### Products
```
GET    /api/products                    → List all products
GET    /api/products/:id               → Get product details
POST   /api/products                   → Create product (admin)
PUT    /api/products/:id               → Update product (admin)
DELETE /api/products/:id               → Delete product (admin)
```

### Cart
```
GET    /api/cart                       → View cart
POST   /api/cart                       → Add to cart
PUT    /api/cart/:product_id           → Update quantity
DELETE /api/cart/:product_id           → Remove item
DELETE /api/cart                       → Clear entire cart
```

### Orders
```
POST   /api/orders                     → Create order (checkout)
GET    /api/orders                     → List user's orders
GET    /api/orders/:id                 → Get order details
PATCH  /api/orders/:id/status          → Update status (admin)
GET    /api/orders/:id/invoice         → Download invoice
```

### Payments
```
GET    /api/payments/:order_id         → Payment status
POST   /api/payments/webhook           → PayPal callback
POST   /api/payments/:order_id/refund  → Process refund (admin)
```

---

## 🔑 Authentication

### Get JWT Token
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@email.com","password":"password"}'
```

### Use JWT in Requests
```bash
curl -X GET http://localhost:5000/api/cart \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Token Storage
- Browser: `localStorage.getItem('token')`
- Requests: `Authorization: Bearer <token>`
- Expires: Check `exp` claim in token

---

## 💾 Database Tables Quick View

### products
```
id (UUID)
name (string)
price (decimal)
description (text)
category (string)
product_type (digital|physical|subscription)
quantity (integer)
image_url (string)
status (active|inactive)
created_at (timestamp)
```

### carts
```
id (UUID)
user_id (UUID)
created_at (timestamp)
```

### cart_items
```
id (UUID)
cart_id (UUID)
product_id (UUID)
quantity (integer)
added_at (timestamp)
```

### orders
```
id (UUID)
user_id (UUID)
status (pending|processing|shipped|delivered|completed)
total_amount (decimal)
subtotal (decimal)
shipping (decimal)
tax (decimal)
created_at (timestamp)
```

### order_items
```
id (UUID)
order_id (UUID)
product_id (UUID)
quantity (integer)
price (decimal)
```

### payments
```
id (UUID)
order_id (UUID)
method (paypal|stripe|card)
status (pending|completed|failed|refunded)
transaction_id (string)
amount (decimal)
created_at (timestamp)
```

---

## 🧪 Common Test Scenarios

### Test Add to Cart
```bash
curl -X POST http://localhost:5000/api/cart \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "quantity": 2
  }'
```

### Test Create Order
```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": {
      "first_name": "John",
      "last_name": "Doe",
      "street": "123 Main St",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    },
    "shipping_method": "standard"
  }'
```

### Test Get Order Status
```bash
curl -X GET http://localhost:5000/api/orders/order-id \
  -H "Authorization: Bearer $TOKEN"
```

### Test Get Products with Filters
```bash
# Search by name
curl "http://localhost:5000/api/products?search=bible"

# Filter by category
curl "http://localhost:5000/api/products?category=Books"

# Sort and paginate
curl "http://localhost:5000/api/products?sort=price_low&page=1&limit=10"

# Price range
curl "http://localhost:5000/api/products?min_price=10&max_price=50"
```

---

## 🔴 Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Invalid/missing JWT | Login again, check token |
| 403 Forbidden | Not admin | Check user role |
| 404 Not Found | Invalid product ID | Verify product exists |
| 400 Bad Request | Missing fields | Check required fields |
| Payment failed | PayPal issue | Verify credentials, check logs |
| Cart not updating | Browser cache | Clear cache, refresh page |
| Email not sent | SMTP error | Check .env email config |

---

## 🔧 Configuration Checklist

### .env Requirements
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# JWT
JWT_SECRET=your-secret-key
JWT_EXPIRE=7d

# PayPal (Live Mode)
PAYPAL_MODE=live
PAYPAL_CLIENT_ID=your-live-client-id
PAYPAL_CLIENT_SECRET=your-live-secret

# Stripe (Optional)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLIC_KEY=pk_live_...

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-password

# Server
NODE_ENV=production
PORT=5000
FRONTEND_URL=https://yoursite.com
```

---

## 📊 Order Status Workflow

```
pending
   ↓
processing (admin confirms payment)
   ↓
shipped (item sent to carrier)
   ↓
delivered (item reaches customer)
   ↓
completed (order finished)

Special Cases:
refunded → Refund processed
cancelled → Order cancelled
```

---

## 💳 Payment Status Workflow

```
pending (waiting for payment)
   ↓
processing (payment being processed)
   ↓
completed (payment successful)

Alternatives:
failed (payment declined)
refunded (money returned)
partially_refunded (partial return)
```

---

## 🎯 User Roles & Permissions

### Student
- ✅ View products
- ✅ Manage own cart
- ✅ Create orders
- ✅ View own orders
- ❌ Create/edit products
- ❌ View all orders
- ❌ Process refunds

### Instructor
- ✅ All student permissions
- ✅ Create own products
- ✅ Edit own products
- ❌ Edit other's products
- ❌ Delete any product
- ❌ View all orders

### Admin
- ✅ All permissions
- ✅ Create/edit/delete products
- ✅ View all orders
- ✅ Update order status
- ✅ Process refunds
- ✅ View analytics

---

## 📈 Pricing & Taxes

### Tax Calculation
```
Tax = (Subtotal + Shipping) × Tax Rate
Total = Subtotal + Shipping + Tax
```

### Example
```
Product: $50.00
Quantity: 2
Subtotal: $100.00

Shipping: $10.00
Subtotal + Shipping: $110.00

Tax (8%): $8.80
TOTAL: $118.80
```

### Digital vs Physical
```
Digital Products:
- No shipping cost
- No weight/dimensions
- Instant delivery
- Quantity: unlimited

Physical Products:
- Shipping cost: varies by method
- Requires weight/dimensions
- Standard/Express/Overnight
- Quantity: limited by inventory
```

---

## 🎁 Product Types

| Type | Shipping | Delivery | Quantity |
|------|----------|----------|----------|
| Digital | None | Instant | Unlimited |
| Physical | Required | 2-7 days | Limited |
| Subscription | Optional | Recurring | Limited |

---

## 📧 Email Notifications

Automatically sent for:
- ✉️ Order confirmation (customer)
- ✉️ Payment confirmation (customer)
- ✉️ Shipment notification (customer)
- ✉️ Delivery confirmation (customer)
- ✉️ Refund processed (customer)
- ✉️ New order alert (admin)
- ✉️ New refund request (admin)

---

## 📱 Frontend Component Locations

| Page | Path | Purpose |
|------|------|---------|
| Shop | `/shop` | Browse/search products |
| Product Detail | `/products/:id` | View details, add to cart |
| Cart | `/cart` | Review items, proceed |
| Checkout | `/checkout` | Fill address, select shipping |
| Confirmation | `/order-confirmation/:id` | Order confirmed |
| My Orders | `/orders` | Order history, downloads |
| Admin Products | `/admin/products` | Manage inventory |
| Admin Orders | `/admin/orders` | Fulfill orders |
| Admin Analytics | `/admin/analytics` | Sales reports |

---

## 🔐 Security Checklist

- [ ] JWT tokens validated on every request
- [ ] User cannot access other user's data
- [ ] Admin functions require admin role
- [ ] Passwords hashed with bcrypt
- [ ] PayPal credentials in .env only
- [ ] HTTPS enabled in production
- [ ] CORS configured properly
- [ ] Rate limiting on auth endpoints
- [ ] SQL injection prevented (ORM used)
- [ ] XSS protection enabled

---

## 🚨 Error Response Format

All errors follow this format:
```json
{
  "success": false,
  "message": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": { }
}
```

### Status Codes
- `200` - OK (successful GET/PUT/DELETE)
- `201` - Created (successful POST)
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing/invalid JWT)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `500` - Server Error (internal error)

---

## 🔄 Common API Patterns

### Pagination
```
GET /api/products?page=1&limit=20

Response: {
  "data": [...],
  "page": 1,
  "limit": 20,
  "total": 100,
  "pages": 5
}
```

### Filtering
```
GET /api/products?category=Books&min_price=10&max_price=50
```

### Sorting
```
GET /api/products?sort=price_low
GET /api/products?sort=price_high
GET /api/products?sort=newest
GET /api/products?sort=popular
```

### Search
```
GET /api/products?search=bible
```

---

## 💰 PayPal Integration Notes

- **Webhook Listener**: `/api/payments/webhook`
- **Verification**: Signature validated against PayPal
- **Test Mode**: Use sandbox credentials
- **Live Mode**: Use production credentials (currently active)
- **Redirect**: Customer sent to `paypal_redirect_url` in order response
- **Return**: Customer returns to `/order-confirmation`
- **Callback**: Webhook updates order status automatically

---

## ✅ Pre-Launch Checklist

- [ ] All database migrations applied
- [ ] PayPal/Stripe credentials configured
- [ ] Email SMTP configured
- [ ] HTTPS certificate installed
- [ ] .env configured for production
- [ ] Testing checklist completed
- [ ] Performance optimized
- [ ] Security review completed
- [ ] Backup system in place
- [ ] Monitoring/logging configured

---

## 📚 Documentation Links

| Document | Purpose |
|----------|---------|
| ECOMMERCE_IMPLEMENTATION_GUIDE.md | Architecture & features |
| ECOMMERCE_API_REFERENCE.md | Complete API docs |
| ECOMMERCE_TESTING_CHECKLIST.md | 30-40 min testing |
| ECOMMERCE_WORKFLOW_GUIDE.md | Real-world examples |
| ECOMMERCE_QUICK_REFERENCE.md | This file (one-page lookup) |

---

## 🆘 Getting Help

**For Setup Issues**: Check .env configuration
**For API Issues**: See ECOMMERCE_API_REFERENCE.md
**For Testing**: Follow ECOMMERCE_TESTING_CHECKLIST.md
**For Examples**: See ECOMMERCE_WORKFLOW_GUIDE.md
**For Architecture**: See ECOMMERCE_IMPLEMENTATION_GUIDE.md

---

**Last Updated**: October 26, 2025
**Status**: ✅ Production Ready
**Version**: 1.0
