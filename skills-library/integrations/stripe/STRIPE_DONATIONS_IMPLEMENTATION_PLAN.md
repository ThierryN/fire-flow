# Stripe Donations Implementation Plan

**Date:** November 6, 2025
**Primary Method:** Stripe Payment Element (inline checkout)
**Backup Method:** PayPal Donation SDK
**Target Page:** `/giving` or `/donate`
**Status:** Planning Phase

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│                  (src/pages/Giving.jsx)                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Donation Form Component                  │  │
│  │  ┌──────────────────────────────────────────┐   │  │
│  │  │ Preset Amounts ($10, $25, $50, $100)    │   │  │
│  │  │ Custom Amount Input                     │   │  │
│  │  │ Donation Type: One-Time / Monthly       │   │  │
│  │  │ Donor Info (Name, Email) - Optional     │   │  │
│  │  └──────────────────────────────────────────┘   │  │
│  │                                                  │  │
│  │  ┌──────────────────────────────────────────┐   │  │
│  │  │      Stripe Payment Element              │   │  │
│  │  │   (Card + Apple Pay + Google Pay)        │   │  │
│  │  └──────────────────────────────────────────┘   │  │
│  │                                                  │  │
│  │  ┌──────────────────────────────────────────┐   │  │
│  │  │    OR PayPal Button (Fallback)           │   │  │
│  │  └──────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↓                                │
│               [Donate Button Click]                     │
│                        ↓                                │
└────────────────────────┬────────────────────────────────┘
                         │
                         ↓
         ┌───────────────────────────────┐
         │    Express Backend Server     │
         │  (server/routes/donations)    │
         ├───────────────────────────────┤
         │  POST /create-payment-intent  │
         │  POST /payment-webhook        │
         │  POST /record-donation        │
         └───────────┬───────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ↓                         ↓
  ┌──────────────┐        ┌─────────────────┐
  │ Stripe API   │        │ Database        │
  │ - PayIntent  │        │ (Supabase/DB)   │
  │ - Customer   │        │ - donations     │
  │ - Charge     │        │   table         │
  └──────────────┘        └─────────────────┘
```

---

## Implementation Steps

### Phase 1: Backend Setup

#### Step 1.1: Create Donations Database Table

```sql
CREATE TABLE donations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  donor_name VARCHAR(255),
  donor_email VARCHAR(255),
  amount DECIMAL(10, 2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  donation_type VARCHAR(20) DEFAULT 'one_time', -- 'one_time' or 'monthly'
  stripe_payment_intent_id VARCHAR(255) UNIQUE,
  stripe_charge_id VARCHAR(255) UNIQUE,
  stripe_customer_id VARCHAR(255),
  stripe_subscription_id VARCHAR(255), -- For recurring
  status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'succeeded', 'failed', 'cancelled'
  payment_method VARCHAR(50), -- 'stripe', 'paypal'
  message TEXT,
  anonymous BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata JSONB -- For storing additional data
);

CREATE INDEX idx_donations_user ON donations(user_id);
CREATE INDEX idx_donations_email ON donations(donor_email);
CREATE INDEX idx_donations_stripe_charge ON donations(stripe_charge_id);
```

#### Step 1.2: Create Stripe Service Module

**File:** `server/services/stripeService.js`

```javascript
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

class StripeService {
  /**
   * Create a payment intent for one-time donation
   */
  async createDonationPaymentIntent(amount, metadata = {}) {
    try {
      const paymentIntent = await stripe.paymentIntents.create({
        amount: Math.round(amount * 100), // Convert to cents
        currency: 'usd',
        metadata: {
          type: 'donation',
          ...metadata
        },
        automatic_payment_methods: {
          enabled: true,
        },
      });

      return {
        success: true,
        clientSecret: paymentIntent.client_secret,
        paymentIntentId: paymentIntent.id,
      };
    } catch (error) {
      console.error('Error creating payment intent:', error);
      throw new Error(`Failed to create payment intent: ${error.message}`);
    }
  }

  /**
   * Create a recurring donation subscription
   */
  async createRecurringDonation(customerId, amount, interval = 'month', metadata = {}) {
    try {
      // Create or get product
      const product = await stripe.products.create({
        name: 'Monthly Donation',
        metadata: { type: 'donation' }
      });

      // Create price (recurring)
      const price = await stripe.prices.create({
        unit_amount: Math.round(amount * 100),
        currency: 'usd',
        recurring: {
          interval: interval, // 'day', 'week', 'month', 'year'
        },
        product: product.id,
      });

      // Create subscription
      const subscription = await stripe.subscriptions.create({
        customer: customerId,
        items: [{ price: price.id }],
        payment_behavior: 'default_incomplete',
        payment_settings: {
          save_default_payment_method: 'on_subscription',
        },
        metadata: {
          type: 'recurring_donation',
          ...metadata
        },
        expand: ['latest_invoice.payment_intent'],
      });

      return {
        success: true,
        subscriptionId: subscription.id,
        clientSecret: subscription.latest_invoice.payment_intent.client_secret,
      };
    } catch (error) {
      console.error('Error creating subscription:', error);
      throw new Error(`Failed to create subscription: ${error.message}`);
    }
  }

  /**
   * Retrieve payment intent details
   */
  async getPaymentIntentDetails(paymentIntentId) {
    try {
      return await stripe.paymentIntents.retrieve(paymentIntentId);
    } catch (error) {
      throw new Error(`Failed to retrieve payment intent: ${error.message}`);
    }
  }

  /**
   * Create a customer for future charges
   */
  async createCustomer(email, metadata = {}) {
    try {
      return await stripe.customers.create({
        email,
        metadata,
      });
    } catch (error) {
      throw new Error(`Failed to create customer: ${error.message}`);
    }
  }

  /**
   * Handle webhook events
   */
  async handleWebhookEvent(event) {
    switch (event.type) {
      case 'payment_intent.succeeded':
        return { action: 'payment_succeeded', data: event.data.object };

      case 'payment_intent.payment_failed':
        return { action: 'payment_failed', data: event.data.object };

      case 'customer.subscription.updated':
        return { action: 'subscription_updated', data: event.data.object };

      case 'customer.subscription.deleted':
        return { action: 'subscription_cancelled', data: event.data.object };

      default:
        return { action: 'unknown', data: event.data.object };
    }
  }
}

module.exports = new StripeService();
```

#### Step 1.3: Create Donations API Routes

**File:** `server/routes/donations.js`

```javascript
const express = require('express');
const router = express.Router();
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const stripeService = require('../services/stripeService');
const Donation = require('../models/Donation'); // DB model
const { authenticate } = require('../middleware/auth');

/**
 * POST /api/donations/create-payment-intent
 * Create a payment intent for one-time donation
 */
router.post('/create-payment-intent', async (req, res) => {
  try {
    const { amount, donorName, donorEmail, message } = req.body;

    // Validate input
    if (!amount || amount < 1) {
      return res.status(400).json({
        success: false,
        message: 'Donation amount must be at least $1'
      });
    }

    // Create payment intent
    const result = await stripeService.createDonationPaymentIntent(amount, {
      donor_name: donorName,
      donor_email: donorEmail,
      has_message: !!message,
    });

    // Store in database (pending)
    const donation = await Donation.create({
      donor_name: donorName,
      donor_email: donorEmail,
      amount,
      message,
      stripe_payment_intent_id: result.paymentIntentId,
      status: 'pending',
      payment_method: 'stripe',
    });

    res.json({
      success: true,
      clientSecret: result.clientSecret,
      paymentIntentId: result.paymentIntentId,
      donationId: donation.id,
    });
  } catch (error) {
    console.error('Error creating payment intent:', error);
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
});

/**
 * POST /api/donations/confirm-payment
 * Confirm payment and update donation status
 */
router.post('/confirm-payment', async (req, res) => {
  try {
    const { paymentIntentId, donationId } = req.body;

    // Retrieve payment intent from Stripe
    const paymentIntent = await stripeService.getPaymentIntentDetails(paymentIntentId);

    if (paymentIntent.status === 'succeeded') {
      // Update donation to 'succeeded'
      await Donation.update(
        { id: donationId },
        {
          status: 'succeeded',
          stripe_charge_id: paymentIntent.charges.data[0].id,
          updated_at: new Date(),
        }
      );

      res.json({
        success: true,
        message: 'Thank you for your donation!',
        donation: await Donation.findById(donationId),
      });
    } else if (paymentIntent.status === 'requires_payment_method') {
      res.status(400).json({
        success: false,
        message: 'Payment failed. Please try again.',
      });
    } else {
      res.json({
        success: true,
        status: paymentIntent.status,
      });
    }
  } catch (error) {
    console.error('Error confirming payment:', error);
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
});

/**
 * POST /api/donations/create-subscription
 * Create a monthly recurring donation
 */
router.post('/create-subscription', async (req, res) => {
  try {
    const { amount, donorName, donorEmail, interval = 'month' } = req.body;

    // Create or get Stripe customer
    let customer = await stripeService.createCustomer(donorEmail, {
      donor_name: donorName,
    });

    // Create subscription
    const result = await stripeService.createRecurringDonation(
      customer.id,
      amount,
      interval,
      { donor_name: donorName }
    );

    // Store in database
    const donation = await Donation.create({
      donor_name: donorName,
      donor_email: donorEmail,
      amount,
      donation_type: 'monthly',
      stripe_customer_id: customer.id,
      stripe_subscription_id: result.subscriptionId,
      status: 'pending',
      payment_method: 'stripe',
    });

    res.json({
      success: true,
      clientSecret: result.clientSecret,
      subscriptionId: result.subscriptionId,
      donationId: donation.id,
    });
  } catch (error) {
    console.error('Error creating subscription:', error);
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
});

/**
 * POST /api/donations/webhook
 * Stripe webhook endpoint
 */
router.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.headers['stripe-signature'];

  try {
    const event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );

    const webhookResult = await stripeService.handleWebhookEvent(event);

    // Handle different webhook events
    switch (webhookResult.action) {
      case 'payment_succeeded':
        await Donation.updateByStripePaymentIntent(
          event.data.object.id,
          { status: 'succeeded' }
        );
        break;

      case 'payment_failed':
        await Donation.updateByStripePaymentIntent(
          event.data.object.id,
          { status: 'failed' }
        );
        break;

      case 'subscription_cancelled':
        await Donation.updateByStripeSubscription(
          event.data.object.id,
          { status: 'cancelled' }
        );
        break;
    }

    res.json({ received: true });
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(400).send(`Webhook Error: ${error.message}`);
  }
});

/**
 * GET /api/donations (Public - for wall of donors)
 */
router.get('/', async (req, res) => {
  try {
    const donations = await Donation.findAll({
      where: {
        status: 'succeeded',
        anonymous: false,
      },
      order: [['created_at', 'DESC']],
      limit: 50,
    });

    res.json({
      success: true,
      donations,
      total: donations.length,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
});

module.exports = router;
```

---

### Phase 2: Frontend Implementation

#### Step 2.1: Create Giving Page Component

**File:** `client/src/pages/Giving.jsx`

```jsx
import { useState, useEffect } from 'react';
import { Elements, PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import axios from 'axios';
import toast from 'react-hot-toast';

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY);

// Donation amounts to suggest
const SUGGESTED_AMOUNTS = [10, 25, 50, 100];

function DonationForm() {
  const stripe = useStripe();
  const elements = useElements();
  const [amount, setAmount] = useState(25);
  const [donationType, setDonationType] = useState('one_time'); // 'one_time' or 'monthly'
  const [donorName, setDonorName] = useState('');
  const [donorEmail, setDonorEmail] = useState('');
  const [message, setMessage] = useState('');
  const [processing, setProcessing] = useState(false);
  const [clientSecret, setClientSecret] = useState(null);
  const [donationId, setDonationId] = useState(null);

  // Create payment intent when amount or type changes
  useEffect(() => {
    createPaymentIntent();
  }, [amount, donationType]);

  const createPaymentIntent = async () => {
    try {
      const endpoint = donationType === 'one_time'
        ? '/api/donations/create-payment-intent'
        : '/api/donations/create-subscription';

      const { data } = await axios.post(endpoint, {
        amount,
        donorName,
        donorEmail,
        message,
        interval: 'month', // For recurring
      });

      setClientSecret(data.clientSecret);
      setDonationId(data.donationId);
    } catch (error) {
      console.error('Error creating payment intent:', error);
      toast.error('Failed to initialize donation form');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!stripe || !elements) {
      toast.error('Payment system not ready');
      return;
    }

    setProcessing(true);

    try {
      const { error } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/donation-success?id=${donationId}`,
        },
      });

      if (error) {
        toast.error(error.message);
      }
    } catch (err) {
      console.error('Payment error:', err);
      toast.error('Payment failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 bg-white rounded-lg shadow">
      {/* Donation Type Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Donation Type</label>
        <div className="flex gap-4">
          <label className="flex items-center">
            <input
              type="radio"
              value="one_time"
              checked={donationType === 'one_time'}
              onChange={(e) => setDonationType(e.target.value)}
              className="mr-2"
            />
            One-time
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="monthly"
              checked={donationType === 'monthly'}
              onChange={(e) => setDonationType(e.target.value)}
              className="mr-2"
            />
            Monthly
          </label>
        </div>
      </div>

      {/* Amount Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Donation Amount</label>
        <div className="grid grid-cols-4 gap-2 mb-3">
          {SUGGESTED_AMOUNTS.map((suggestedAmount) => (
            <button
              key={suggestedAmount}
              type="button"
              onClick={() => setAmount(suggestedAmount)}
              className={`py-2 rounded font-medium transition ${
                amount === suggestedAmount
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
              }`}
            >
              ${suggestedAmount}
            </button>
          ))}
        </div>
        <input
          type="number"
          min="1"
          step="0.01"
          value={amount}
          onChange={(e) => setAmount(parseFloat(e.target.value))}
          className="w-full px-4 py-2 border rounded"
          placeholder="Custom amount"
        />
      </div>

      {/* Donor Info */}
      <div className="mb-6 space-y-4">
        <input
          type="text"
          placeholder="Your name (optional)"
          value={donorName}
          onChange={(e) => setDonorName(e.target.value)}
          className="w-full px-4 py-2 border rounded"
        />
        <input
          type="email"
          placeholder="Your email (optional)"
          value={donorEmail}
          onChange={(e) => setDonorEmail(e.target.value)}
          className="w-full px-4 py-2 border rounded"
        />
        <textarea
          placeholder="Your message (optional)"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="w-full px-4 py-2 border rounded"
          rows="3"
        />
      </div>

      {/* Stripe Payment Element */}
      {clientSecret && (
        <div className="mb-6">
          <PaymentElement />
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={!stripe || processing}
        className="w-full bg-blue-600 text-white py-3 rounded font-semibold hover:bg-blue-700 disabled:bg-gray-400"
      >
        {processing ? 'Processing...' : `Donate $${amount}`}
      </button>
    </form>
  );
}

function Giving() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Support Our Mission</h1>
          <p className="text-xl text-gray-600">
            Your generous donation helps us continue our ministry work
          </p>
        </div>

        {/* Donation Form */}
        <Elements stripe={stripePromise} options={{ mode: 'payment', currency: 'usd' }}>
          <DonationForm />
        </Elements>

        {/* Info Section */}
        <div className="mt-12 grid md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-bold mb-2">🔒 Secure</h3>
            <p className="text-gray-600">Your payment information is secure and encrypted</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-bold mb-2">💰 Tax Deductible</h3>
            <p className="text-gray-600">Your donation may be tax deductible</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-bold mb-2">🙏 Transparent</h3>
            <p className="text-gray-600">We're committed to using your donation wisely</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Giving;
```

#### Step 2.2: Create Donation Success Page

**File:** `client/src/pages/DonationSuccess.jsx`

```jsx
import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

function DonationSuccess() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [donation, setDonation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDonation = async () => {
      try {
        const donationId = searchParams.get('id');
        const { data } = await axios.get(`/api/donations/${donationId}`);
        setDonation(data.donation);
      } catch (error) {
        console.error('Error fetching donation:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDonation();
  }, [searchParams]);

  if (loading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-green-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg text-center max-w-md">
        <div className="text-6xl mb-4">✅</div>
        <h1 className="text-3xl font-bold mb-4 text-green-600">Thank You!</h1>
        <p className="text-gray-600 mb-6">
          Your donation of ${donation?.amount} has been received.
        </p>
        {donation?.donation_type === 'monthly' && (
          <p className="text-sm text-gray-500 mb-6">
            Your monthly recurring donation has been set up.
          </p>
        )}
        <button
          onClick={() => navigate('/')}
          className="bg-green-600 text-white px-6 py-2 rounded font-semibold hover:bg-green-700"
        >
          Return Home
        </button>
      </div>
    </div>
  );
}

export default DonationSuccess;
```

---

### Phase 3: Configuration

#### Step 3.1: Update Routes in App.jsx

```jsx
import Giving from './pages/Giving';
import DonationSuccess from './pages/DonationSuccess';

// In your router:
<Route path="/giving" element={<Giving />} />
<Route path="/donation-success" element={<DonationSuccess />} />
```

#### Step 3.2: Environment Variables

Ensure these are in your `.env` files:

**Client (`client/.env`):**
```
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_... (already set)
```

**Server (`server/.env`):**
```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## Testing Checklist

### Pre-Implementation
- [ ] Stripe account created and webhook configured
- [ ] Database migration scripts prepared
- [ ] Routes added to App.jsx
- [ ] Environment variables set

### Backend Testing
- [ ] Payment intent creation works
- [ ] Subscription creation works
- [ ] Webhook endpoint responds correctly
- [ ] Database records created properly

### Frontend Testing
- [ ] Donation form renders
- [ ] Amount selection works
- [ ] Payment element loads
- [ ] Form submission sends correct data
- [ ] Success page displays donation details

### End-to-End Testing
- [ ] One-time donation flow completes
- [ ] Monthly donation flow completes
- [ ] Donor information captured correctly
- [ ] Success page shows after payment
- [ ] Email receipt sent (future feature)
- [ ] Database reflects all donations

---

## Nice-to-Have Features (Phase 2)

1. **Email Receipts**
   - Send thank you email after successful donation
   - Include tax information if applicable

2. **Donor Wall**
   - Display recent donations (anonymous or named)
   - Show total raised

3. **Recurring Donation Management**
   - Allow donors to view/update their subscriptions
   - Allow cancellation of monthly donations

4. **Analytics Dashboard**
   - Track total donations
   - Monitor recurring vs one-time
   - Revenue reports

5. **PayPal Integration**
   - Add PayPal button as secondary option
   - Let donors choose preferred payment method

---

## Estimated Timeline

| Phase | Task | Estimated Time |
|-------|------|-----------------|
| 1 | Backend setup (DB, API, Service) | 4-6 hours |
| 2 | Frontend implementation | 3-4 hours |
| 3 | Testing & debugging | 2-3 hours |
| 4 | Deployment & monitoring | 1-2 hours |
| **Total** | **Complete implementation** | **10-15 hours** |

---

## Deployment Checklist

- [ ] Stripe production API keys configured
- [ ] Webhook endpoint live and tested
- [ ] Database migrations applied to production
- [ ] Routes tested in production environment
- [ ] Payment form tested with real payment flow
- [ ] Error handling verified
- [ ] Monitoring/logging set up
- [ ] Support process documented

---

## Summary

This plan provides:
- ✅ Secure payment processing with Stripe
- ✅ Support for one-time and recurring donations
- ✅ Modern, responsive donation form
- ✅ Database to track all donations
- ✅ Webhook handling for payment confirmations
- ✅ Clear success/failure UX
- ✅ Foundation for PayPal backup integration

**Next Step:** Ready to implement Phase 1 (Backend Setup)?
