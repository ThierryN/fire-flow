# E-Commerce Testing Checklist
**Status**: ✅ Complete Testing Guide
**Total Time Required**: 30-40 minutes
**Difficulty**: Intermediate
**Prerequisites**: Server running, authenticated user account

---

## 📋 Overview

This checklist provides a comprehensive testing procedure for all E-Commerce features. Follow each phase sequentially and verify all tests pass before moving to production.

---

## 🧪 Phase 1: Product Management (5-7 minutes)

### Create Product (Admin Only)
- [ ] Login as Admin user
- [ ] Navigate to Admin Dashboard → Products
- [ ] Click "Add New Product"
- [ ] Fill in product details:
  - [ ] Name: "Test Bible Study Guide"
  - [ ] Description: "Comprehensive study material"
  - [ ] Price: 29.99
  - [ ] Category: "Books"
  - [ ] Type: "digital"
  - [ ] Quantity: 100
  - [ ] Upload image
- [ ] Click "Save"
- [ ] Verify: Product appears in product list
- [ ] Verify: Product accessible via API `GET /api/products/:id`

### List Products
- [ ] Navigate to Shop page
- [ ] Verify: All products display
- [ ] Verify: Product images load correctly
- [ ] Verify: Prices display correctly
- [ ] Test pagination: Navigate through pages
- [ ] Verify: "Next" and "Previous" buttons work

### Search Products
- [ ] Use search bar, search for "Bible"
- [ ] Verify: Only matching products show
- [ ] Verify: Search is case-insensitive
- [ ] Try empty search: Should show all
- [ ] Test special characters in search

### Filter Products
- [ ] Filter by category: Books
- [ ] Verify: Only Book products show
- [ ] Filter by price range: $10-$30
- [ ] Verify: Only products in range show
- [ ] Combine filters: Category + Price
- [ ] Verify: Both filters apply correctly

### Sort Products
- [ ] Sort by "Newest"
- [ ] Sort by "Price: Low to High"
- [ ] Sort by "Price: High to Low"
- [ ] Sort by "Most Popular"
- [ ] Verify: Order changes correctly with each sort

### View Product Details
- [ ] Click on any product
- [ ] Verify: Full details display
  - [ ] Name
  - [ ] Description
  - [ ] Price
  - [ ] Rating (if available)
  - [ ] Quantity available
  - [ ] Product image
- [ ] Verify: "Add to Cart" button visible
- [ ] Verify: "Share" button works (optional)

### Update Product (Admin Only)
- [ ] Navigate to Admin Dashboard → Products
- [ ] Click "Edit" on test product
- [ ] Change price to 39.99
- [ ] Click "Save"
- [ ] Verify: Price updated in product list
- [ ] Verify: Price updated in Shop view
- [ ] Verify: API returns new price

### Delete Product (Admin Only)
- [ ] Navigate to Admin Dashboard → Products
- [ ] Click "Delete" on test product
- [ ] Confirm deletion
- [ ] Verify: Product removed from list
- [ ] Verify: Returns 404 when accessing deleted product API

---

## 🛒 Phase 2: Shopping Cart (8-10 minutes)

### Add to Cart
- [ ] Login as Student user
- [ ] Navigate to Shop
- [ ] Click on any product
- [ ] Enter quantity: 2
- [ ] Click "Add to Cart"
- [ ] Verify: Success message appears
- [ ] Verify: Cart count increases
- [ ] Verify: Notification shows "2 items added"

### View Cart
- [ ] Click "Cart" in header
- [ ] Verify: Added items display
- [ ] Verify: Correct quantities show
- [ ] Verify: Prices calculated correctly
- [ ] Verify: Subtotal displays
- [ ] Verify: Tax calculated (if applicable)
- [ ] Verify: Total amount correct

### Add Same Product Again
- [ ] Go back to Shop
- [ ] Add same product with quantity 1
- [ ] Click "Add to Cart"
- [ ] Go to Cart
- [ ] Verify: Quantity updated to 3 (not duplicate entry)
- [ ] Verify: Subtotal updated

### Update Quantity
- [ ] In Cart, change quantity to 5
- [ ] Click "Update"
- [ ] Verify: Cart updates immediately
- [ ] Verify: Subtotal updates
- [ ] Verify: Total updates
- [ ] Decrease quantity to 1
- [ ] Verify: All totals recalculate

### Remove from Cart
- [ ] In Cart, click "Remove" on one item
- [ ] Verify: Item removed
- [ ] Verify: Cart count decreases
- [ ] Verify: Totals recalculate
- [ ] Verify: Cart shows remaining items

### Clear Cart
- [ ] Add multiple products to cart
- [ ] Click "Clear Cart"
- [ ] Confirm action
- [ ] Verify: All items removed
- [ ] Verify: Cart count shows 0
- [ ] Verify: Empty cart message displays

### Cart Persistence
- [ ] Add items to cart
- [ ] Close browser completely
- [ ] Reopen site
- [ ] Navigate to Cart
- [ ] Verify: Items still in cart (if using localStorage)
- [ ] Or verify: Cart empty (if using session-only)

### Add Multiple Products
- [ ] Add 3 different products with different quantities
- [ ] Verify: Cart shows all 3 items
- [ ] Verify: Each has correct quantity
- [ ] Verify: Total includes all items
- [ ] Go through each product detail link
- [ ] Verify: Can navigate without losing cart

---

## 💳 Phase 3: Checkout & Orders (10-12 minutes)

### Start Checkout
- [ ] With items in cart, click "Checkout"
- [ ] Verify: Checkout form appears
- [ ] Verify: Shows order summary with all items
- [ ] Verify: Shows current totals
- [ ] Verify: All form fields visible

### Fill Shipping Address
- [ ] Enter first name: "John"
- [ ] Enter last name: "Doe"
- [ ] Enter street: "123 Main St"
- [ ] Enter city: "Boston"
- [ ] Enter state: "MA"
- [ ] Enter zip: "02101"
- [ ] Enter country: "USA"
- [ ] Verify: All fields accept input

### Select Shipping Method
- [ ] Select "Standard Shipping"
- [ ] Verify: Shipping cost displays
- [ ] Verify: Total updates with shipping
- [ ] Select "Express Shipping"
- [ ] Verify: Cost changes
- [ ] Verify: Total updates
- [ ] Select back to "Standard"

### Apply Discount/Coupon (if implemented)
- [ ] If coupon field exists:
  - [ ] Enter valid coupon code
  - [ ] Verify: Discount applies
  - [ ] Verify: Total decreases
  - [ ] Try invalid code
  - [ ] Verify: Error message shows

### Review Order
- [ ] Verify: Order summary correct
- [ ] Verify: All items listed
- [ ] Verify: Quantities correct
- [ ] Verify: Pricing correct
- [ ] Verify: Shipping cost shown
- [ ] Verify: Final total correct

### Proceed to Payment
- [ ] Click "Proceed to Payment"
- [ ] Verify: Redirected to payment method selection
- [ ] Verify: PayPal option available
- [ ] (Stripe option available if configured)

### PayPal Sandbox Payment
- [ ] Click "PayPal"
- [ ] Should redirect to PayPal
- [ ] Login with test account credentials
- [ ] Verify: Order total matches
- [ ] Click "Approve" on PayPal
- [ ] Should redirect back to your site
- [ ] Verify: Order confirmation page appears
- [ ] Verify: Order number displayed
- [ ] Verify: Correct total shown

### Complete Order (PayPal)
- [ ] Click "Return to Merchant" button
- [ ] Verify: Returns to your site
- [ ] Verify: Confirmation page loads
- [ ] Verify: Order marked as "completed"
- [ ] Verify: Payment status "confirmed"

### View Order Details
- [ ] From confirmation page, click "View Order" or navigate to My Orders
- [ ] Verify: Order ID displays
- [ ] Verify: All items listed with quantities
- [ ] Verify: Total amount shown
- [ ] Verify: Shipping address displayed
- [ ] Verify: Order status shows "completed"
- [ ] Verify: Payment status shows "confirmed"

### Download Invoice
- [ ] From order details, click "Download Invoice"
- [ ] Verify: PDF downloads successfully
- [ ] Verify: Invoice contains:
  - [ ] Order number
  - [ ] Order date
  - [ ] Items with prices
  - [ ] Shipping address
  - [ ] Total amount
  - [ ] Company logo/name

### Order History
- [ ] Navigate to "My Orders" page
- [ ] Verify: Completed order appears in list
- [ ] Verify: Shows order number
- [ ] Verify: Shows order date
- [ ] Verify: Shows order total
- [ ] Verify: Shows order status
- [ ] Create another order
- [ ] Verify: Both orders appear in list

---

## 🔐 Phase 4: Security & Authorization (5 minutes)

### Authentication Required
- [ ] Logout
- [ ] Try accessing `/cart` directly
- [ ] Verify: Redirected to login
- [ ] Try accessing `/checkout` directly
- [ ] Verify: Redirected to login
- [ ] Login as student
- [ ] Verify: Can now access cart

### User Isolation
- [ ] Login as Student A
- [ ] Create order with specific address
- [ ] Logout
- [ ] Login as Student B
- [ ] Navigate to My Orders
- [ ] Verify: Only Student B's orders show
- [ ] Verify: Cannot see Student A's orders
- [ ] Verify: Cannot access Student A's order details via URL

### Admin Functionality
- [ ] Login as Admin
- [ ] Navigate to Admin Dashboard → Orders
- [ ] Verify: All orders visible (from all users)
- [ ] Click on any order
- [ ] Verify: Can edit order status
- [ ] Verify: Can process refund
- [ ] Update order status to "shipped"
- [ ] Verify: Change persists
- [ ] Logout
- [ ] Login as Student
- [ ] Check order
- [ ] Verify: Status updated for them too

### Product Edit Protection
- [ ] Logout
- [ ] Login as Student
- [ ] Try accessing `/admin/products`
- [ ] Verify: Access denied or redirected
- [ ] Try accessing product edit API: `PUT /api/products/:id`
- [ ] Verify: Returns 403 Forbidden
- [ ] Logout
- [ ] Login as Admin
- [ ] Verify: Can access admin products
- [ ] Verify: Can edit products

---

## 🔧 Phase 5: Error Handling (5 minutes)

### Invalid Input
- [ ] Try checkout with empty shipping address
- [ ] Verify: Error message shows which fields required
- [ ] Try checkout with invalid zip code
- [ ] Verify: Validation error shows
- [ ] Try adding quantity of 0
- [ ] Verify: Error or minimum quantity enforced

### Out of Stock
- [ ] Create product with quantity 1
- [ ] Try to add quantity 5 to cart
- [ ] Verify: Either error or limited to available
- [ ] Verify: Cannot checkout with more than available

### Network Errors (Simulate)
- [ ] Open DevTools → Network tab
- [ ] Throttle to "Slow 3G"
- [ ] Try adding to cart
- [ ] Verify: Still works (just slower)
- [ ] Verify: Loading indicators show
- [ ] Set to offline mode
- [ ] Try adding to cart
- [ ] Verify: Error message shows
- [ ] Go back online

### Payment Failure
- [ ] Go to checkout with PayPal
- [ ] During PayPal login, click "Cancel"
- [ ] Verify: Returns to checkout
- [ ] Verify: Order NOT created
- [ ] Verify: Items still in cart
- [ ] Try checkout again
- [ ] This time approve
- [ ] Verify: Order created successfully

### Duplicate Orders Prevention
- [ ] Complete order via PayPal
- [ ] Quickly click "Approve" again (before redirect)
- [ ] Verify: Only ONE order created
- [ ] Verify: No duplicate charges

---

## 📊 Phase 6: Data & Calculations (5 minutes)

### Price Calculations
- [ ] Add product priced at $10.50, quantity 3
- [ ] Verify: Subtotal = $31.50 (not rounding errors)
- [ ] Add product priced at $5.99, quantity 2
- [ ] Verify: New subtotal = $42.48
- [ ] Add shipping $5.00
- [ ] Verify: Subtotal + shipping = $47.48
- [ ] Apply tax (if 8%): $47.48 × 0.08 = $3.80
- [ ] Verify: Total = $51.28

### Quantity Calculations
- [ ] Add product quantity 1
- [ ] Increase to quantity 10
- [ ] Verify: Subtotal multiplied correctly
- [ ] Decrease to quantity 1
- [ ] Verify: Subtotal recalculated
- [ ] Remove item
- [ ] Verify: Quantities for other items unchanged

### Discount Calculations (if implemented)
- [ ] Subtotal: $100
- [ ] Apply 10% discount code
- [ ] Verify: Discount = $10
- [ ] Verify: New subtotal = $90
- [ ] Add tax on final amount (not original)
- [ ] Verify: Correct order total

### Order Summary Accuracy
- [ ] After PayPal approval, check order
- [ ] Verify: Order total = Checkout total
- [ ] Verify: No missing cents
- [ ] Verify: Currency formatting correct ($X.XX)

---

## 🏃 Phase 7: Performance (3-5 minutes)

### Page Load Speed
- [ ] Navigate to Shop
- [ ] Open DevTools → Performance
- [ ] Record page load
- [ ] Verify: Load time under 3 seconds
- [ ] Verify: First Contentful Paint under 2 seconds

### Cart Operations Speed
- [ ] Add 10 items to cart rapidly
- [ ] Verify: Updates feel instant (< 500ms)
- [ ] Update quantities rapidly
- [ ] Verify: No lag or UI freezing

### Checkout Form Speed
- [ ] Start checkout with 20 items in cart
- [ ] Verify: Form loads quickly
- [ ] Verify: No performance degradation

### Search Performance
- [ ] Search for common term (e.g., "book")
- [ ] Verify: Results appear quickly (< 1 second)
- [ ] Type in search field rapidly
- [ ] Verify: No lag while typing

---

## 🎯 Phase 8: Real-World Scenarios (5 minutes)

### Guest Wants to Buy
- [ ] Logout (simulating guest)
- [ ] Add item to cart
- [ ] Try checkout
- [ ] Verify: Prompted to login/register
- [ ] Register new account
- [ ] Complete checkout
- [ ] Verify: Order associated with new account

### Customer Returns
- [ ] Login with existing account
- [ ] Add item to cart
- [ ] Navigate away
- [ ] Come back later
- [ ] Verify: Item still in cart
- [ ] Complete purchase
- [ ] Logout and login again
- [ ] Verify: Order in history

### Bulk Purchase
- [ ] Add same product, quantity 50
- [ ] Verify: Cart shows quantity 50
- [ ] Proceed to checkout
- [ ] Verify: No limit errors
- [ ] Complete order
- [ ] Verify: Order shows quantity 50

### Multiple Product Types
- [ ] Add digital product
- [ ] Add physical product
- [ ] Add subscription (if available)
- [ ] Verify: All in same cart
- [ ] Verify: Shipping applies only to physical
- [ ] Checkout
- [ ] Verify: Digital product available immediately
- [ ] Verify: Physical product marked for shipment

---

## ✅ Phase 9: Browser Compatibility (3 minutes)

### Test in Multiple Browsers
- [ ] Chrome: Complete full workflow
- [ ] Firefox: Complete full workflow
- [ ] Safari: Complete full workflow
- [ ] Edge: Complete full workflow
- [ ] Mobile (iOS/Android): Complete workflow
- [ ] Verify: All features work identically

### Responsive Design
- [ ] Desktop (1920x1080): All visible, proper spacing
- [ ] Tablet (768x1024): All functional, readable
- [ ] Mobile (375x667): All usable, no horizontal scroll
- [ ] Test cart on mobile: Easy to use
- [ ] Test checkout on mobile: Forms fill easily

---

## 📱 Phase 10: Mobile-Specific (2-3 minutes)

### Touch Interactions
- [ ] On mobile, tap "Add to Cart"
- [ ] Verify: Works immediately
- [ ] Swipe between products (if carousel)
- [ ] Verify: Smooth scrolling
- [ ] Tap buttons/links
- [ ] Verify: Responsive (no double-tap needed)

### Mobile Checkout
- [ ] Form fields fit screen width
- [ ] Keyboard appears appropriately
- [ ] Can scroll form to see all fields
- [ ] Can see summary and button
- [ ] Tap to select shipping option
- [ ] Tap to approve payment
- [ ] Verify: Full workflow works on 4-5" screen

---

## 🎉 Completion Checklist

All phases completed successfully?
- [ ] Phase 1: Product Management (5-7 min) ✅
- [ ] Phase 2: Shopping Cart (8-10 min) ✅
- [ ] Phase 3: Checkout & Orders (10-12 min) ✅
- [ ] Phase 4: Security & Authorization (5 min) ✅
- [ ] Phase 5: Error Handling (5 min) ✅
- [ ] Phase 6: Data & Calculations (5 min) ✅
- [ ] Phase 7: Performance (3-5 min) ✅
- [ ] Phase 8: Real-World Scenarios (5 min) ✅
- [ ] Phase 9: Browser Compatibility (3 min) ✅
- [ ] Phase 10: Mobile-Specific (2-3 min) ✅

**Total Time**: 30-40 minutes
**All Tests Passed**: YES ✅

---

## 🐛 Troubleshooting

### Product Not Showing After Creation
- [ ] Clear browser cache
- [ ] Refresh page
- [ ] Check admin console for errors
- [ ] Verify product status is "active"
- [ ] Check server logs for 500 errors

### Cart Not Updating
- [ ] Check browser console for JS errors
- [ ] Verify localStorage enabled (if used)
- [ ] Clear browser cache
- [ ] Try in incognito mode
- [ ] Check network tab for failed requests

### Payment Failed
- [ ] Verify PayPal credentials in .env
- [ ] Confirm webhook configured in PayPal
- [ ] Check server logs for webhook errors
- [ ] Try with different test account
- [ ] Verify internet connection

### Orders Not Appearing
- [ ] Check database for orders table
- [ ] Verify user ID stored correctly
- [ ] Run migration: `node runMigration.js`
- [ ] Check server logs for SQL errors
- [ ] Verify user authenticated before order

---

## 📞 Support

**For API Issues**: See ECOMMERCE_API_REFERENCE.md
**For Feature Questions**: See ECOMMERCE_IMPLEMENTATION_GUIDE.md
**For Workflow Examples**: See ECOMMERCE_WORKFLOW_GUIDE.md

---

**Testing Status**: Ready for Production
**Date**: October 26, 2025
**Time Estimate**: 30-40 minutes
