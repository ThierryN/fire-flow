# E-Commerce API Reference
**Status**: ✅ Complete & Production Ready
**Base URL**: `/api`
**Authentication**: JWT Required

---

## 📋 API Overview

### Base Endpoints
```
Products:      /api/products
Cart:          /api/cart
Orders:        /api/orders
Payments:      /api/payments
```

---

## 📦 Products API

### Get All Products
```
GET /api/products

Query Parameters:
├── page (default: 1)
├── limit (default: 20)
├── category (optional: "Books", "Digital", etc.)
├── search (optional: search by name)
├── sort (default: "newest")
│   └── Options: newest, price_low, price_high, popular, rating
├── type (optional: "digital", "physical", "subscription")
├── min_price (optional: minimum price)
└── max_price (optional: maximum price)

Example:
GET /api/products?category=Books&sort=price_low&limit=10

Response (200):
{
  "success": true,
  "results": 10,
  "total": 50,
  "page": 1,
  "pages": 5,
  "data": [
    {
      "id": "uuid",
      "name": "Advanced Bible Study",
      "description": "Complete study guide...",
      "price": 29.99,
      "category": "Books",
      "product_type": "physical",
      "image_url": "https://...",
      "quantity": 100,
      "status": "active",
      "created_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

### Get Single Product
```
GET /api/products/:id

URL Parameter:
└── id: Product UUID

Example:
GET /api/products/550e8400-e29b-41d4-a716-446655440000

Response (200):
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Advanced Bible Study Workbook",
    "description": "Complete study guide with worksheets",
    "price": 29.99,
    "category": "Books",
    "product_type": "physical",
    "image_url": "https://...",
    "quantity": 100,
    "status": "active",
    "shipping_cost": 5.00,
    "weight": 2.5,
    "dimensions": "8x10x1 inches",
    "rating": 4.8,
    "reviews": 24,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-20T14:30:00Z"
  }
}

Response (404):
{
  "success": false,
  "message": "Product not found"
}
```

### Create Product (Admin Only)
```
POST /api/products

Authentication: JWT (Admin Role Required)

Body:
{
  "name": "string (required)",
  "description": "string",
  "price": "number (required)",
  "category": "string",
  "product_type": "digital|physical|subscription",
  "quantity": "number",
  "image_url": "string",
  "shipping_cost": "number (for physical products)",
  "weight": "number (for physical products)",
  "dimensions": "string (for physical products)"
}

Example:
POST /api/products
{
  "name": "Daily Devotional Guide",
  "description": "365-day devotional with insights",
  "price": 14.99,
  "category": "Books",
  "product_type": "digital",
  "quantity": 999,
  "image_url": "https://example.com/image.jpg"
}

Response (201):
{
  "success": true,
  "data": {
    "id": "new-uuid",
    "name": "Daily Devotional Guide",
    "price": 14.99,
    ...
  }
}

Response (400):
{
  "success": false,
  "message": "Missing required fields"
}
```

### Update Product (Admin Only)
```
PUT /api/products/:id

Authentication: JWT (Admin Role Required)

Body: (Any field to update)
{
  "name": "Updated Name",
  "price": 19.99,
  "quantity": 50
}

Example:
PUT /api/products/550e8400-e29b-41d4-a716-446655440000
{
  "price": 24.99,
  "quantity": 75
}

Response (200):
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "price": 24.99,
    "quantity": 75,
    ...
  }
}
```

### Delete Product (Admin Only)
```
DELETE /api/products/:id

Authentication: JWT (Admin Role Required)

Response (200):
{
  "success": true,
  "message": "Product deleted successfully"
}

Response (404):
{
  "success": false,
  "message": "Product not found"
}
```

---

## 🛒 Cart API

### View Cart
```
GET /api/cart

Authentication: JWT (Required)

Response (200):
{
  "success": true,
  "data": {
    "id": "cart-uuid",
    "user_id": "user-uuid",
    "items": [
      {
        "product_id": "550e8400-e29b-41d4-a716-446655440000",
        "product_name": "Bible Study Workbook",
        "quantity": 2,
        "price": 29.99,
        "subtotal": 59.98,
        "product_type": "physical"
      }
    ],
    "subtotal": 59.98,
    "shipping": 5.00,
    "tax": 4.68,
    "total": 69.66,
    "item_count": 2
  }
}
```

### Add to Cart
```
POST /api/cart

Authentication: JWT (Required)

Body:
{
  "product_id": "string (UUID, required)",
  "quantity": "number (default: 1)"
}

Example:
POST /api/cart
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "quantity": 2
}

Response (201):
{
  "success": true,
  "message": "Item added to cart",
  "data": {
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "quantity": 2,
    "total_items": 3
  }
}

Response (400):
{
  "success": false,
  "message": "Invalid product or quantity"
}
```

### Update Cart Item
```
PUT /api/cart/:product_id

Authentication: JWT (Required)

Body:
{
  "quantity": "number (required, min: 1)"
}

Example:
PUT /api/cart/550e8400-e29b-41d4-a716-446655440000
{
  "quantity": 5
}

Response (200):
{
  "success": true,
  "data": {
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "quantity": 5
  }
}
```

### Remove from Cart
```
DELETE /api/cart/:product_id

Authentication: JWT (Required)

Response (200):
{
  "success": true,
  "message": "Item removed from cart"
}
```

### Clear Cart
```
DELETE /api/cart

Authentication: JWT (Required)

Response (200):
{
  "success": true,
  "message": "Cart cleared"
}
```

---

## 📦 Orders API

### Create Order (Checkout)
```
POST /api/orders

Authentication: JWT (Required)

Body:
{
  "shipping_address": {
    "first_name": "string (required)",
    "last_name": "string (required)",
    "street": "string (required)",
    "city": "string (required)",
    "state": "string (required)",
    "zip": "string (required)",
    "country": "string (required)"
  },
  "shipping_method": "string (standard|express|overnight)",
  "billing_same_as_shipping": "boolean (default: true)"
}

Example:
POST /api/orders
{
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
}

Response (201):
{
  "success": true,
  "data": {
    "id": "order-uuid",
    "user_id": "user-uuid",
    "status": "pending",
    "total_amount": 69.66,
    "subtotal": 59.98,
    "shipping": 5.00,
    "tax": 4.68,
    "items": [
      {
        "product_id": "uuid",
        "product_name": "Bible Study",
        "quantity": 2,
        "price": 29.99
      }
    ],
    "shipping_address": {...},
    "paypal_redirect_url": "https://...",
    "created_at": "2025-01-25T10:00:00Z"
  }
}
```

### Get Order
```
GET /api/orders/:id

Authentication: JWT (Required - must be order owner or admin)

Response (200):
{
  "success": true,
  "data": {
    "id": "order-uuid",
    "user_id": "user-uuid",
    "status": "completed",
    "total_amount": 69.66,
    "items": [...],
    "shipping_address": {...},
    "tracking_number": "1Z999AA10123456784",
    "expected_delivery": "2025-02-01",
    "payment": {
      "method": "paypal",
      "status": "completed",
      "transaction_id": "txn_123456"
    },
    "invoice_url": "https://...",
    "created_at": "2025-01-25T10:00:00Z",
    "updated_at": "2025-01-26T14:30:00Z"
  }
}
```

### Get All Orders (User's Orders)
```
GET /api/orders

Authentication: JWT (Required)

Query Parameters:
├── page (default: 1)
├── limit (default: 20)
└── status (optional: pending|completed|shipped|delivered)

Response (200):
{
  "success": true,
  "results": 5,
  "page": 1,
  "total": 5,
  "data": [
    {
      "id": "order-uuid",
      "status": "completed",
      "total_amount": 69.66,
      "created_at": "2025-01-25T10:00:00Z"
    }
  ]
}
```

### Update Order Status (Admin Only)
```
PATCH /api/orders/:id/status

Authentication: JWT (Admin Role Required)

Body:
{
  "status": "pending|completed|shipped|delivered",
  "tracking_number": "string (optional)"
}

Example:
PATCH /api/orders/order-uuid/status
{
  "status": "shipped",
  "tracking_number": "1Z999AA10123456784"
}

Response (200):
{
  "success": true,
  "data": {
    "id": "order-uuid",
    "status": "shipped",
    "tracking_number": "1Z999AA10123456784"
  }
}
```

### Get Order Invoice
```
GET /api/orders/:id/invoice

Authentication: JWT (Required - order owner or admin)

Response (200):
Returns PDF file with invoice

Response (404):
{
  "success": false,
  "message": "Invoice not found"
}
```

---

## 💳 Payments API

### Get Payment Status
```
GET /api/payments/:order_id

Authentication: JWT (Required)

Response (200):
{
  "success": true,
  "data": {
    "order_id": "order-uuid",
    "payment_method": "paypal",
    "amount": 69.66,
    "status": "completed",
    "transaction_id": "PAYID-1234567890",
    "created_at": "2025-01-25T10:00:00Z"
  }
}
```

### PayPal Webhook (Endpoint for PayPal)
```
POST /api/payments/webhook

Headers:
└── X-PAYPAL-TRANSMISSION-ID: string
    X-PAYPAL-TRANSMISSION-TIME: string
    X-PAYPAL-TRANSMISSION-SIG: string
    X-PAYPAL-CERT-URL: string

Body (from PayPal):
{
  "event_type": "PAYMENT.COMPLETED",
  "resource": {
    "id": "PAYID-...",
    "amount": {
      "total": "69.66"
    },
    "links": [
      {
        "rel": "up",
        "href": "https://..."
      }
    ]
  }
}

Response (200):
{
  "success": true,
  "message": "Webhook processed"
}

Response (400):
{
  "success": false,
  "message": "Invalid signature"
}
```

### Refund Order (Admin Only)
```
POST /api/payments/:order_id/refund

Authentication: JWT (Admin Role Required)

Body:
{
  "reason": "string (optional)"
}

Response (200):
{
  "success": true,
  "data": {
    "order_id": "order-uuid",
    "refund_id": "refund-uuid",
    "amount": 69.66,
    "status": "processing"
  }
}

Response (400):
{
  "success": false,
  "message": "Order cannot be refunded"
}
```

---

## 🔐 Authentication

### JWT Header
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Required for:
├── POST /api/cart
├── GET /api/cart
├── DELETE /api/cart/*
├── POST /api/orders
├── GET /api/orders
├── GET /api/orders/:id
└── All admin endpoints
```

### User Roles
```
Student:
├── View products
├── Manage own cart
├── Create own orders
├── View own orders
└── Download own invoices

Instructor:
├── All student permissions
├── View product list (for selling own materials)
└── Create own products

Admin:
├── All permissions
├── Create/edit/delete products
├── View all orders
├── Update order status
├── Process refunds
└── View analytics
```

---

## 🔄 Common Flows

### Customer Purchase Flow
```
1. GET /api/products (browse)
2. GET /api/products/:id (view details)
3. POST /api/cart (add to cart)
4. GET /api/cart (view cart)
5. PUT /api/cart/:id (update quantities)
6. POST /api/orders (create order)
7. GET /api/orders/:id (verify order created)
8. (Redirect to PayPal)
9. /api/payments/webhook (PayPal callback)
10. GET /api/orders/:id (check payment status)
11. GET /api/orders/:id/invoice (download receipt)
```

### Admin Product Management
```
1. POST /api/products (create)
2. GET /api/products (list all)
3. PUT /api/products/:id (update)
4. DELETE /api/products/:id (delete)
5. GET /api/orders (view all orders)
6. PATCH /api/orders/:id/status (update status)
```

---

## 🚨 Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "message": "Description of what went wrong"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "message": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "success": false,
  "message": "You don't have permission"
}
```

### 404 Not Found
```json
{
  "success": false,
  "message": "Resource not found"
}
```

### 500 Server Error
```json
{
  "success": false,
  "message": "Internal server error"
}
```

---

## 📊 Response Codes Summary

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing JWT |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal error |

---

## 🧪 Testing

### Using cURL
```bash
# Get all products
curl -X GET http://localhost:5000/api/products

# Add to cart (requires auth)
curl -X POST http://localhost:5000/api/cart \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"product_id":"uuid","quantity":1}'

# Create order (requires auth)
curl -X POST http://localhost:5000/api/orders \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": {
      "first_name":"John",
      "last_name":"Doe",
      "street":"123 Main St",
      "city":"Boston",
      "state":"MA",
      "zip":"02101",
      "country":"USA"
    }
  }'
```

### Using Postman
1. Import collection
2. Set JWT token in Authorization
3. Test each endpoint
4. Verify responses

---

## 🔗 Related Documentation

**For Implementation Details**:
→ See: ECOMMERCE_IMPLEMENTATION_GUIDE.md

**For Testing Procedures**:
→ See: ECOMMERCE_TESTING_CHECKLIST.md

**For Workflow Examples**:
→ See: ECOMMERCE_WORKFLOW_GUIDE.md

---

**API Version**: 1.0
**Last Updated**: October 26, 2025
**Status**: ✅ Production Ready
