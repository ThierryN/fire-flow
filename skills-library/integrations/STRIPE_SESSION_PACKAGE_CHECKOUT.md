# Stripe Checkout Session for Session Packages - Complete Implementation

## The Problem

The appointment scheduling system needed a payment flow for session packages (bundles of appointments users can purchase). The existing code had a placeholder alert:

```javascript
alert('Online payment for packages coming soon! Please contact us to purchase.');
```

### Why It Was Hard

- Session packages are different from regular product purchases - they create `user_packages` records
- Payment must complete BEFORE activating the package (can't trust client-side)
- Need to handle the full Stripe Checkout Session flow with server-side verification
- Package activation must be idempotent (prevent double-activation from page refresh)
- Free packages ($0) need a different flow than paid packages

### Impact

- Users couldn't purchase session packages online
- Revenue loss from friction in the sales process
- Manual contact requirement for purchases

---

## The Solution

### Architecture Overview

```
Client                           Server                          Stripe
  |                                |                               |
  |-- POST /packages/:id/checkout-->|                               |
  |                                |-- Create Checkout Session ---->|
  |                                |<-- Session URL -----------------|
  |<-- Redirect to Stripe URL------|                               |
  |                                |                               |
  |-- (User completes payment) ----|------------------------------>|
  |                                |                               |
  |<-- Redirect to success URL ----|                               |
  |                                |                               |
  |-- GET /packages/checkout/success --------------------------->|
  |                                |-- Verify payment_status ----->|
  |                                |<-- "paid" --------------------|
  |                                |-- Create user_package --------|
  |<-- Package activated! ---------|                               |
```

### Root Cause

The placeholder code assumed a different payment model. Session packages need:
1. Stripe Checkout Sessions (not inline payments)
2. Server-side verification after redirect
3. Package activation tied to successful payment

---

## Implementation

### 1. Backend Controller (appointmentController.js)

```javascript
/**
 * Create Stripe Checkout Session for package purchase
 * @route POST /api/appointments/packages/:id/checkout
 */
export const createPackageCheckoutSession = asyncHandler(async (req, res, next) => {
  const { id } = req.params;
  const userId = req.user.id;

  // Get package details
  const pkg = await AppointmentPackageModel.getPackageById(id);

  if (!pkg) {
    return next(new ApiError('Package not found', 404));
  }

  if (!pkg.is_active) {
    return next(new ApiError('This package is no longer available', 400));
  }

  // Initialize Stripe
  const stripe = (await import('stripe')).default(process.env.STRIPE_SECRET_KEY);

  // Create Checkout Session
  const session = await stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    line_items: [
      {
        price_data: {
          currency: 'usd',
          product_data: {
            name: pkg.name,
            description: pkg.description || `${pkg.session_count} session package`,
          },
          unit_amount: Math.round(parseFloat(pkg.price) * 100), // Stripe uses cents
        },
        quantity: 1,
      },
    ],
    mode: 'payment',
    success_url: `${process.env.CLIENT_URL}/session-packages/success?session_id={CHECKOUT_SESSION_ID}&package_id=${pkg.id}`,
    cancel_url: `${process.env.CLIENT_URL}/session-packages`,
    customer_email: req.user.email,
    metadata: {
      user_id: userId,
      package_id: pkg.id,
      package_name: pkg.name,
      session_count: pkg.session_count.toString(),
    },
  });

  res.status(200).json({
    success: true,
    data: {
      sessionId: session.id,
      url: session.url,
    },
  });
});

/**
 * Handle successful checkout - activate the package
 * @route GET /api/appointments/packages/checkout/success
 */
export const handlePackageCheckoutSuccess = asyncHandler(async (req, res, next) => {
  const { session_id, package_id } = req.query;
  const userId = req.user.id;

  if (!session_id) {
    return next(new ApiError('Missing session ID', 400));
  }

  // Verify payment with Stripe
  const stripe = (await import('stripe')).default(process.env.STRIPE_SECRET_KEY);
  const session = await stripe.checkout.sessions.retrieve(session_id);

  // Verify payment was successful
  if (session.payment_status !== 'paid') {
    return next(new ApiError('Payment not completed', 400));
  }

  // Verify user matches
  if (session.metadata.user_id !== userId) {
    return next(new ApiError('Unauthorized', 403));
  }

  // Check if package already activated (idempotency)
  const existingPurchases = await sql`
    SELECT id FROM user_packages
    WHERE user_id = ${userId}
      AND stripe_session_id = ${session_id}
  `;

  if (existingPurchases.length > 0) {
    // Already activated, return the existing package
    const [userPackage] = await sql`
      SELECT up.*, sp.name as package_name, sp.session_count as original_count
      FROM user_packages up
      JOIN session_packages sp ON up.package_id = sp.id
      WHERE up.id = ${existingPurchases[0].id}
    `;

    return res.status(200).json({
      success: true,
      message: 'Package already activated',
      data: userPackage,
    });
  }

  // Get package details
  const pkg = await AppointmentPackageModel.getPackageById(package_id);
  if (!pkg) {
    return next(new ApiError('Package not found', 404));
  }

  // Calculate expiration date
  const validityDays = pkg.validity_days || 365;
  const expiresAt = new Date();
  expiresAt.setDate(expiresAt.getDate() + validityDays);

  // Create user package
  const [userPackage] = await sql`
    INSERT INTO user_packages (
      user_id,
      package_id,
      service_id,
      sessions_remaining,
      expires_at,
      stripe_session_id,
      amount_paid
    ) VALUES (
      ${userId},
      ${pkg.id},
      ${pkg.service_id || null},
      ${pkg.session_count},
      ${expiresAt.toISOString()},
      ${session_id},
      ${session.amount_total / 100}
    )
    RETURNING *
  `;

  // Get complete package info for response
  const [completePackage] = await sql`
    SELECT up.*, sp.name as package_name
    FROM user_packages up
    JOIN session_packages sp ON up.package_id = sp.id
    WHERE up.id = ${userPackage.id}
  `;

  res.status(200).json({
    success: true,
    message: 'Package activated successfully',
    data: completePackage,
  });
});
```

### 2. Routes (appointmentRoutes.js)

```javascript
import { protect } from '../middleware/auth.js';

// Session package checkout
router.post('/packages/:id/checkout', protect, appointmentController.createPackageCheckoutSession);
router.get('/packages/checkout/success', protect, appointmentController.handlePackageCheckoutSuccess);
```

### 3. Frontend - Purchase Handler (SessionPackages.jsx)

```javascript
const handlePurchase = async (pkg) => {
  if (!isAuthenticated) {
    navigate('/login', { state: { from: '/session-packages' } });
    return;
  }

  setPurchasing(pkg.id);
  try {
    // For free packages, purchase directly
    if (pkg.price === 0 || pkg.price === '0.00') {
      await api.post(`/appointments/packages/${pkg.id}/purchase`);
      await fetchMyPackages();
      setPurchasing(null);
      return;
    }

    // For paid packages, create Stripe checkout session
    const response = await api.post(`/appointments/packages/${pkg.id}/checkout`, {
      successUrl: `${window.location.origin}/session-packages/success?session_id={CHECKOUT_SESSION_ID}&package_id=${pkg.id}`,
      cancelUrl: `${window.location.origin}/session-packages`
    });

    if (response.data.success && response.data.data.url) {
      // Redirect to Stripe Checkout
      window.location.href = response.data.data.url;
    } else {
      throw new Error('Failed to create checkout session');
    }
  } catch (err) {
    console.error('Purchase failed:', err);
    setError(err.response?.data?.message || 'Failed to initiate purchase. Please try again.');
    setPurchasing(null);
  }
};
```

### 4. Success Page (SessionPackageSuccess.jsx)

```javascript
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import api from '../services/api';

const SessionPackageSuccess = () => {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [packageData, setPackageData] = useState(null);

  const sessionId = searchParams.get('session_id');
  const packageId = searchParams.get('package_id');

  useEffect(() => {
    if (sessionId) {
      activatePackage();
    } else {
      setError('Missing session information');
      setLoading(false);
    }
  }, [sessionId]);

  const activatePackage = async () => {
    try {
      const response = await api.get('/appointments/packages/checkout/success', {
        params: { session_id: sessionId, package_id: packageId }
      });

      if (response.data.success) {
        setPackageData(response.data.data);
      } else {
        throw new Error(response.data.message || 'Failed to activate package');
      }
    } catch (err) {
      console.error('Activation failed:', err);
      setError(err.response?.data?.message || 'Failed to activate package. Please contact support.');
    } finally {
      setLoading(false);
    }
  };

  // Render loading, error, or success states...
};
```

### 5. Route Registration (App.jsx)

```javascript
const SessionPackageSuccess = lazy(() => import('./pages/SessionPackageSuccess'));

// In routes:
<Route
  path="/session-packages/success"
  element={<PrivateRoute element={<SessionPackageSuccess />} />}
/>
```

---

## Testing the Fix

### Manual Testing Checklist

1. **Free Package ($0)**
   - [ ] Click purchase -> Package activates immediately
   - [ ] No Stripe redirect occurs
   - [ ] Package appears in "My Packages"

2. **Paid Package**
   - [ ] Click purchase -> Redirects to Stripe Checkout
   - [ ] Complete payment -> Redirects to success page
   - [ ] Success page shows "Package Activated!"
   - [ ] Package appears in "My Packages"
   - [ ] Refresh success page -> No duplicate activation (idempotent)

3. **Cancelled Payment**
   - [ ] Click purchase -> Redirects to Stripe
   - [ ] Cancel payment -> Returns to packages page
   - [ ] No package created

4. **Unauthenticated User**
   - [ ] Click purchase -> Redirects to login
   - [ ] After login -> Returns to packages page

### Stripe Test Cards

```
Success:        4242 4242 4242 4242
Decline:        4000 0000 0000 0002
3D Secure:      4000 0025 0000 3155
```

---

## Prevention

### Environment Variables Required

```bash
STRIPE_SECRET_KEY=sk_test_...
CLIENT_URL=http://localhost:3000
```

### Database Schema Required

```sql
-- user_packages table must have stripe_session_id column
ALTER TABLE user_packages ADD COLUMN IF NOT EXISTS stripe_session_id VARCHAR(255);
ALTER TABLE user_packages ADD COLUMN IF NOT EXISTS amount_paid DECIMAL(10,2);
```

### Common Gotchas

1. **Stripe uses cents** - Always multiply price by 100
2. **Idempotency** - Check for existing stripe_session_id before creating
3. **User verification** - Always verify metadata.user_id matches req.user.id
4. **Payment status** - Only activate on `payment_status === 'paid'`

---

## Related Patterns

- [Stripe Payment Integration](./stripe-payment-integration-complete.md)
- [Appointment Scheduler Design](../appointment-scheduler-design.md)

---

## Common Mistakes to Avoid

- ❌ **Trusting client-side payment confirmation** - Always verify with Stripe API
- ❌ **Not handling page refresh** - Use idempotency with stripe_session_id
- ❌ **Wrong price format** - Stripe uses cents, not dollars
- ❌ **Missing error handling** - Always catch Stripe API errors
- ❌ **Not protecting success route** - Requires authentication

---

## Resources

- [Stripe Checkout Sessions](https://stripe.com/docs/payments/checkout)
- [Stripe Node.js SDK](https://github.com/stripe/stripe-node)
- [Checkout Session Object](https://stripe.com/docs/api/checkout/sessions/object)

---

## Time to Implement

**2-3 hours** for complete implementation including:
- Backend controller methods
- Routes
- Frontend purchase flow
- Success page component
- Testing

## Difficulty Level

⭐⭐⭐ (3/5) - Requires understanding of Stripe Checkout flow and server-side verification

---

**Author Notes:**
The key insight is that session packages are NOT like regular products. They create persistent `user_packages` records that track remaining sessions. The payment must be verified server-side before activation.

The idempotency check with `stripe_session_id` is critical - without it, users refreshing the success page would get duplicate packages.
