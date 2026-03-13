# Membership System Implementation Guide for MERN Stack

**Project**: MERN Community LMS
**Date**: 2025-11-27

---

## Quick Start Recommendations

### Recommended Technology Stack

**Payment Processing**: Stripe (industry standard, best documentation, handles subscriptions automatically)

**Core Libraries**:
- `stripe` (Node.js SDK)
- `@stripe/stripe-js` (React client)
- `@stripe/react-stripe-js` (React components)
- `node-cron` (scheduled tasks for renewals, reminders)
- `nodemailer` (email notifications)
- `jsonwebtoken` (JWT authentication)

---

## Phase 1: MVP Features (Week 1-2)

### 1. Database Schema (MongoDB)

```javascript
// models/MembershipLevel.js
const membershipLevelSchema = new Schema({
  name: { type: String, required: true, unique: true },
  description: String,
  rank: { type: Number, required: true, unique: true }, // 1 = highest
  price: { type: Number, required: true }, // in cents
  currency: { type: String, default: 'USD' },
  billingPeriod: {
    type: String,
    enum: ['day', 'week', 'month', 'year', 'lifetime'],
    required: true
  },
  trialDays: { type: Number, default: 0 },
  features: [String], // Array of feature names
  stripePriceId: String, // Stripe Price ID
  isActive: { type: Boolean, default: true }
}, { timestamps: true });

// models/UserMembership.js
const userMembershipSchema = new Schema({
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  membershipLevelId: { type: Schema.Types.ObjectId, ref: 'MembershipLevel', required: true },
  status: {
    type: String,
    enum: ['active', 'trialing', 'past_due', 'cancelled', 'expired', 'grace_period'],
    default: 'active'
  },

  // Stripe data
  stripeCustomerId: String,
  stripeSubscriptionId: String,

  // Dates
  trialEndDate: Date,
  startDate: { type: Date, default: Date.now },
  endDate: Date, // null for active subscriptions
  nextBillingDate: Date,
  gracePeriodEnd: Date,
  cancelledAt: Date,

  // Metadata
  cancellationReason: String,
  metadata: Schema.Types.Mixed
}, { timestamps: true });

// Indexes for performance
userMembershipSchema.index({ userId: 1, status: 1 });
userMembershipSchema.index({ nextBillingDate: 1 });
userMembershipSchema.index({ stripeSubscriptionId: 1 });

// models/ContentRule.js
const contentRuleSchema = new Schema({
  contentType: {
    type: String,
    enum: ['course', 'lesson', 'video', 'file', 'page'],
    required: true
  },
  contentId: { type: Schema.Types.ObjectId, required: true },
  requiredLevelId: { type: Schema.Types.ObjectId, ref: 'MembershipLevel' },

  // Drip content settings
  dripDays: { type: Number, default: 0 }, // 0 = immediate access
  dripDate: Date, // null = use dripDays instead

  // Optional prerequisite
  prerequisiteRuleId: { type: Schema.Types.ObjectId, ref: 'ContentRule' },

  isActive: { type: Boolean, default: true }
}, { timestamps: true });

contentRuleSchema.index({ contentType: 1, contentId: 1 });
contentRuleSchema.index({ requiredLevelId: 1 });

// models/Transaction.js
const transactionSchema = new Schema({
  userMembershipId: { type: Schema.Types.ObjectId, ref: 'UserMembership', required: true },
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },

  amount: { type: Number, required: true }, // in cents
  currency: { type: String, default: 'USD' },

  gateway: { type: String, enum: ['stripe', 'paypal', 'manual'], default: 'stripe' },
  gatewayTransactionId: String,

  status: {
    type: String,
    enum: ['pending', 'completed', 'failed', 'refunded'],
    default: 'pending'
  },

  type: {
    type: String,
    enum: ['charge', 'refund', 'renewal', 'trial_conversion'],
    required: true
  },

  metadata: Schema.Types.Mixed
}, { timestamps: true });

transactionSchema.index({ userId: 1, createdAt: -1 });
transactionSchema.index({ gatewayTransactionId: 1 });
```

---

### 2. Stripe Integration

```javascript
// services/StripeService.js
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

class StripeService {
  // Create or get customer
  async getOrCreateCustomer(user) {
    // Check if user already has a Stripe customer ID
    const existingMembership = await UserMembership.findOne({
      userId: user._id,
      stripeCustomerId: { $exists: true }
    });

    if (existingMembership && existingMembership.stripeCustomerId) {
      return await stripe.customers.retrieve(existingMembership.stripeCustomerId);
    }

    // Create new customer
    const customer = await stripe.customers.create({
      email: user.email,
      name: user.name,
      metadata: {
        userId: user._id.toString()
      }
    });

    return customer;
  }

  // Create subscription
  async createSubscription(user, membershipLevel, paymentMethodId) {
    const customer = await this.getOrCreateCustomer(user);

    // Attach payment method to customer
    await stripe.paymentMethods.attach(paymentMethodId, {
      customer: customer.id
    });

    // Set as default payment method
    await stripe.customers.update(customer.id, {
      invoice_settings: {
        default_payment_method: paymentMethodId
      }
    });

    // Create subscription
    const subscription = await stripe.subscriptions.create({
      customer: customer.id,
      items: [{ price: membershipLevel.stripePriceId }],
      trial_period_days: membershipLevel.trialDays || undefined,
      metadata: {
        userId: user._id.toString(),
        membershipLevelId: membershipLevel._id.toString()
      }
    });

    // Create UserMembership record
    const userMembership = await UserMembership.create({
      userId: user._id,
      membershipLevelId: membershipLevel._id,
      stripeCustomerId: customer.id,
      stripeSubscriptionId: subscription.id,
      status: subscription.status, // 'trialing' or 'active'
      trialEndDate: subscription.trial_end ? new Date(subscription.trial_end * 1000) : null,
      nextBillingDate: new Date(subscription.current_period_end * 1000)
    });

    return { subscription, userMembership };
  }

  // Cancel subscription
  async cancelSubscription(subscriptionId, immediate = false) {
    if (immediate) {
      // Cancel immediately
      const subscription = await stripe.subscriptions.cancel(subscriptionId);
      return subscription;
    } else {
      // Cancel at period end (recommended)
      const subscription = await stripe.subscriptions.update(subscriptionId, {
        cancel_at_period_end: true
      });
      return subscription;
    }
  }

  // Update subscription (upgrade/downgrade)
  async updateSubscription(subscriptionId, newPriceId, prorationBehavior = 'create_prorations') {
    const subscription = await stripe.subscriptions.retrieve(subscriptionId);

    const updatedSubscription = await stripe.subscriptions.update(subscriptionId, {
      items: [{
        id: subscription.items.data[0].id,
        price: newPriceId
      }],
      proration_behavior: prorationBehavior
    });

    return updatedSubscription;
  }
}

module.exports = new StripeService();
```

---

### 3. Webhook Handler

```javascript
// routes/webhooks.js
const express = require('express');
const router = express.Router();
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const UserMembership = require('../models/UserMembership');
const Transaction = require('../models/Transaction');
const EmailService = require('../services/EmailService');

// IMPORTANT: Use raw body for webhook signature verification
router.post('/stripe', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;

  try {
    event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Handle the event
  switch (event.type) {
    case 'customer.subscription.created':
      await handleSubscriptionCreated(event.data.object);
      break;

    case 'customer.subscription.updated':
      await handleSubscriptionUpdated(event.data.object);
      break;

    case 'customer.subscription.deleted':
      await handleSubscriptionDeleted(event.data.object);
      break;

    case 'invoice.payment_succeeded':
      await handlePaymentSucceeded(event.data.object);
      break;

    case 'invoice.payment_failed':
      await handlePaymentFailed(event.data.object);
      break;

    case 'customer.subscription.trial_will_end':
      await handleTrialWillEnd(event.data.object);
      break;

    default:
      console.log(`Unhandled event type: ${event.type}`);
  }

  res.json({ received: true });
});

// Event handlers
async function handleSubscriptionCreated(subscription) {
  // Subscription was already created in createSubscription
  // Update status if needed
  await UserMembership.findOneAndUpdate(
    { stripeSubscriptionId: subscription.id },
    {
      status: subscription.status,
      nextBillingDate: new Date(subscription.current_period_end * 1000)
    }
  );
}

async function handleSubscriptionUpdated(subscription) {
  await UserMembership.findOneAndUpdate(
    { stripeSubscriptionId: subscription.id },
    {
      status: subscription.status,
      nextBillingDate: new Date(subscription.current_period_end * 1000),
      endDate: subscription.cancel_at ? new Date(subscription.cancel_at * 1000) : null
    }
  );
}

async function handleSubscriptionDeleted(subscription) {
  const userMembership = await UserMembership.findOneAndUpdate(
    { stripeSubscriptionId: subscription.id },
    {
      status: 'cancelled',
      endDate: new Date(),
      cancelledAt: new Date()
    },
    { new: true }
  ).populate('userId');

  // Send cancellation email
  if (userMembership) {
    await EmailService.sendCancellationEmail(userMembership.userId);
  }
}

async function handlePaymentSucceeded(invoice) {
  const subscription = await stripe.subscriptions.retrieve(invoice.subscription);
  const userMembership = await UserMembership.findOne({
    stripeSubscriptionId: subscription.id
  });

  if (userMembership) {
    // Update status to active if in grace period
    await UserMembership.findByIdAndUpdate(userMembership._id, {
      status: 'active',
      gracePeriodEnd: null,
      nextBillingDate: new Date(subscription.current_period_end * 1000)
    });

    // Create transaction record
    await Transaction.create({
      userMembershipId: userMembership._id,
      userId: userMembership.userId,
      amount: invoice.amount_paid,
      currency: invoice.currency,
      gateway: 'stripe',
      gatewayTransactionId: invoice.payment_intent,
      status: 'completed',
      type: invoice.billing_reason === 'subscription_create' ? 'charge' : 'renewal'
    });
  }
}

async function handlePaymentFailed(invoice) {
  const subscription = await stripe.subscriptions.retrieve(invoice.subscription);
  const userMembership = await UserMembership.findOne({
    stripeSubscriptionId: subscription.id
  }).populate('userId');

  if (userMembership) {
    // Set grace period (7 days)
    const gracePeriodEnd = new Date();
    gracePeriodEnd.setDate(gracePeriodEnd.getDate() + 7);

    await UserMembership.findByIdAndUpdate(userMembership._id, {
      status: 'grace_period',
      gracePeriodEnd
    });

    // Send payment failed email
    await EmailService.sendPaymentFailedEmail(userMembership.userId, {
      attemptCount: invoice.attempt_count,
      nextRetry: invoice.next_payment_attempt ? new Date(invoice.next_payment_attempt * 1000) : null
    });

    // Create failed transaction record
    await Transaction.create({
      userMembershipId: userMembership._id,
      userId: userMembership.userId,
      amount: invoice.amount_due,
      currency: invoice.currency,
      gateway: 'stripe',
      gatewayTransactionId: invoice.payment_intent,
      status: 'failed',
      type: 'renewal'
    });
  }
}

async function handleTrialWillEnd(subscription) {
  const userMembership = await UserMembership.findOne({
    stripeSubscriptionId: subscription.id
  }).populate('userId');

  if (userMembership) {
    await EmailService.sendTrialEndingEmail(userMembership.userId, {
      trialEndDate: new Date(subscription.trial_end * 1000)
    });
  }
}

module.exports = router;
```

---

### 4. Access Control Middleware

```javascript
// middleware/membershipAuth.js
const UserMembership = require('../models/UserMembership');
const ContentRule = require('../models/ContentRule');
const MembershipLevel = require('../models/MembershipLevel');

// Check if user has active membership
async function requireMembership(req, res, next) {
  try {
    const membership = await UserMembership.findOne({
      userId: req.user._id,
      status: { $in: ['active', 'trialing', 'grace_period'] }
    });

    if (!membership) {
      return res.status(403).json({
        error: 'Active membership required',
        message: 'Please subscribe to access this content'
      });
    }

    req.membership = membership;
    next();
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

// Check if user has access to specific content
async function checkContentAccess(contentType, contentId) {
  return async (req, res, next) => {
    try {
      // Get content rule
      const rule = await ContentRule.findOne({
        contentType,
        contentId,
        isActive: true
      }).populate('requiredLevelId');

      // No rule = public content
      if (!rule) {
        return next();
      }

      // Get user's membership
      const userMembership = await UserMembership.findOne({
        userId: req.user._id,
        status: { $in: ['active', 'trialing', 'grace_period'] }
      }).populate('membershipLevelId');

      // No membership = no access
      if (!userMembership) {
        return res.status(403).json({
          error: 'Membership required',
          requiredLevel: rule.requiredLevelId ? rule.requiredLevelId.name : 'Any membership'
        });
      }

      // Check if membership level has access
      // Lower rank number = higher tier (1 is highest)
      if (rule.requiredLevelId &&
          userMembership.membershipLevelId.rank > rule.requiredLevelId.rank) {
        return res.status(403).json({
          error: 'Insufficient membership level',
          requiredLevel: rule.requiredLevelId.name,
          currentLevel: userMembership.membershipLevelId.name
        });
      }

      // Check drip content
      if (rule.dripDate) {
        // Calendar-based drip
        if (new Date() < rule.dripDate) {
          return res.status(403).json({
            error: 'Content not yet available',
            availableOn: rule.dripDate
          });
        }
      } else if (rule.dripDays > 0) {
        // Days after enrollment
        const enrollmentDate = userMembership.startDate;
        const unlockDate = new Date(enrollmentDate);
        unlockDate.setDate(unlockDate.getDate() + rule.dripDays);

        if (new Date() < unlockDate) {
          return res.status(403).json({
            error: 'Content not yet available',
            availableOn: unlockDate,
            daysRemaining: Math.ceil((unlockDate - new Date()) / (1000 * 60 * 60 * 24))
          });
        }
      }

      // Access granted
      req.contentRule = rule;
      next();
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  };
}

// Helper to get user's current membership
async function getCurrentMembership(userId) {
  return await UserMembership.findOne({
    userId,
    status: { $in: ['active', 'trialing', 'grace_period'] }
  }).populate('membershipLevelId');
}

module.exports = {
  requireMembership,
  checkContentAccess,
  getCurrentMembership
};
```

---

### 5. React Components

```javascript
// components/membership/PricingCard.jsx
import React from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

function CheckoutForm({ membershipLevel, onSuccess }) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!stripe || !elements) return;

    setLoading(true);
    setError(null);

    try {
      // Create payment method
      const { error: pmError, paymentMethod } = await stripe.createPaymentMethod({
        type: 'card',
        card: elements.getElement(CardElement)
      });

      if (pmError) {
        setError(pmError.message);
        setLoading(false);
        return;
      }

      // Create subscription via API
      const response = await fetch('/api/subscriptions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          membershipLevelId: membershipLevel._id,
          paymentMethodId: paymentMethod.id
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Subscription failed');
      }

      // Check if 3D Secure authentication is required
      if (data.requiresAction) {
        const { error: confirmError } = await stripe.confirmCardPayment(
          data.clientSecret
        );

        if (confirmError) {
          setError(confirmError.message);
          setLoading(false);
          return;
        }
      }

      onSuccess(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <CardElement
        options={{
          style: {
            base: {
              fontSize: '16px',
              color: '#424770',
              '::placeholder': { color: '#aab7c4' }
            },
            invalid: { color: '#9e2146' }
          }
        }}
      />

      {error && <div className="error">{error}</div>}

      <button type="submit" disabled={!stripe || loading}>
        {loading ? 'Processing...' : `Subscribe for $${membershipLevel.price / 100}/${membershipLevel.billingPeriod}`}
      </button>
    </form>
  );
}

function PricingCard({ membershipLevel }) {
  const [showCheckout, setShowCheckout] = React.useState(false);

  const handleSuccess = (data) => {
    // Redirect to success page or dashboard
    window.location.href = '/dashboard?subscribed=true';
  };

  return (
    <div className="pricing-card">
      <h3>{membershipLevel.name}</h3>
      <div className="price">
        ${membershipLevel.price / 100}
        <span>/{membershipLevel.billingPeriod}</span>
      </div>

      <ul className="features">
        {membershipLevel.features.map((feature, i) => (
          <li key={i}>{feature}</li>
        ))}
      </ul>

      {membershipLevel.trialDays > 0 && (
        <div className="trial-notice">
          {membershipLevel.trialDays} day free trial
        </div>
      )}

      {!showCheckout ? (
        <button onClick={() => setShowCheckout(true)}>
          Get Started
        </button>
      ) : (
        <Elements stripe={stripePromise}>
          <CheckoutForm
            membershipLevel={membershipLevel}
            onSuccess={handleSuccess}
          />
        </Elements>
      )}
    </div>
  );
}

export default PricingCard;
```

---

## Phase 2: Enhanced Features (Week 3-4)

### 1. Scheduled Tasks (Cron Jobs)

```javascript
// jobs/membershipJobs.js
const cron = require('node-cron');
const UserMembership = require('../models/UserMembership');
const EmailService = require('../services/EmailService');

class MembershipJobs {
  // Run daily at 9 AM
  static initRenewalReminders() {
    cron.schedule('0 9 * * *', async () => {
      console.log('Running renewal reminder job...');

      // Find memberships expiring in 7 days
      const sevenDaysFromNow = new Date();
      sevenDaysFromNow.setDate(sevenDaysFromNow.getDate() + 7);

      const memberships = await UserMembership.find({
        status: 'active',
        nextBillingDate: {
          $gte: new Date(),
          $lte: sevenDaysFromNow
        }
      }).populate('userId membershipLevelId');

      for (const membership of memberships) {
        await EmailService.sendRenewalReminderEmail(
          membership.userId,
          {
            renewalDate: membership.nextBillingDate,
            amount: membership.membershipLevelId.price,
            levelName: membership.membershipLevelId.name
          }
        );
      }

      console.log(`Sent ${memberships.length} renewal reminders`);
    });
  }

  // Check for expired grace periods (run every hour)
  static initGracePeriodCheck() {
    cron.schedule('0 * * * *', async () => {
      console.log('Checking expired grace periods...');

      const expiredMemberships = await UserMembership.find({
        status: 'grace_period',
        gracePeriodEnd: { $lte: new Date() }
      }).populate('userId');

      for (const membership of expiredMemberships) {
        // Cancel the subscription in Stripe
        try {
          await stripe.subscriptions.cancel(membership.stripeSubscriptionId);
        } catch (error) {
          console.error('Failed to cancel subscription:', error);
        }

        // Update membership status
        membership.status = 'expired';
        membership.endDate = new Date();
        await membership.save();

        // Send expiration email
        await EmailService.sendMembershipExpiredEmail(membership.userId);
      }

      console.log(`Expired ${expiredMemberships.length} memberships`);
    });
  }

  static initAll() {
    this.initRenewalReminders();
    this.initGracePeriodCheck();
    console.log('All membership cron jobs initialized');
  }
}

module.exports = MembershipJobs;

// In server.js
const MembershipJobs = require('./jobs/membershipJobs');
MembershipJobs.initAll();
```

---

### 2. Analytics Service

```javascript
// services/AnalyticsService.js
const UserMembership = require('../models/UserMembership');
const Transaction = require('../models/Transaction');
const MembershipLevel = require('../models/MembershipLevel');

class AnalyticsService {
  // Monthly Recurring Revenue
  async getMRR() {
    const activeMemberships = await UserMembership.find({
      status: { $in: ['active', 'trialing', 'grace_period'] }
    }).populate('membershipLevelId');

    let mrr = 0;
    for (const membership of activeMemberships) {
      const level = membership.membershipLevelId;

      // Convert to monthly
      let monthlyAmount = level.price;
      if (level.billingPeriod === 'year') {
        monthlyAmount = level.price / 12;
      } else if (level.billingPeriod === 'week') {
        monthlyAmount = level.price * 4.33; // average weeks per month
      } else if (level.billingPeriod === 'day') {
        monthlyAmount = level.price * 30;
      }

      mrr += monthlyAmount;
    }

    return mrr / 100; // Convert from cents to dollars
  }

  // Churn Rate (last 30 days)
  async getChurnRate() {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const startCount = await UserMembership.countDocuments({
      createdAt: { $lte: thirtyDaysAgo },
      status: { $in: ['active', 'trialing'] }
    });

    const cancelledCount = await UserMembership.countDocuments({
      cancelledAt: { $gte: thirtyDaysAgo },
      status: { $in: ['cancelled', 'expired'] }
    });

    if (startCount === 0) return 0;

    return (cancelledCount / startCount) * 100;
  }

  // New sign-ups (last 30 days)
  async getNewSignups(days = 30) {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    return await UserMembership.countDocuments({
      createdAt: { $gte: startDate }
    });
  }

  // Active members
  async getActiveMembers() {
    return await UserMembership.countDocuments({
      status: { $in: ['active', 'trialing', 'grace_period'] }
    });
  }

  // Revenue breakdown by level
  async getRevenueByLevel() {
    const levels = await MembershipLevel.find({ isActive: true });
    const breakdown = [];

    for (const level of levels) {
      const count = await UserMembership.countDocuments({
        membershipLevelId: level._id,
        status: { $in: ['active', 'trialing'] }
      });

      const revenue = count * level.price;

      breakdown.push({
        levelName: level.name,
        memberCount: count,
        revenue: revenue / 100
      });
    }

    return breakdown;
  }

  // Trial conversion rate
  async getTrialConversionRate() {
    const totalTrials = await UserMembership.countDocuments({
      trialEndDate: { $exists: true, $ne: null }
    });

    const convertedTrials = await UserMembership.countDocuments({
      trialEndDate: { $exists: true, $ne: null },
      status: 'active',
      endDate: null // Still subscribed
    });

    if (totalTrials === 0) return 0;

    return (convertedTrials / totalTrials) * 100;
  }

  // Dashboard summary
  async getDashboardSummary() {
    const [mrr, churnRate, newSignups, activeMembers, revenueByLevel, trialConversion] = await Promise.all([
      this.getMRR(),
      this.getChurnRate(),
      this.getNewSignups(),
      this.getActiveMembers(),
      this.getRevenueByLevel(),
      this.getTrialConversionRate()
    ]);

    return {
      mrr: Math.round(mrr * 100) / 100,
      churnRate: Math.round(churnRate * 100) / 100,
      newSignups,
      activeMembers,
      revenueByLevel,
      trialConversion: Math.round(trialConversion * 100) / 100
    };
  }
}

module.exports = new AnalyticsService();
```

---

## Environment Variables

```bash
# .env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# App
JWT_SECRET=your-jwt-secret
NODE_ENV=development
CLIENT_URL=http://localhost:3000
```

---

## Testing Strategy

### 1. Use Stripe Test Mode
- Test card: 4242 4242 4242 4242
- Expiry: Any future date
- CVC: Any 3 digits

### 2. Test Scenarios
- Successful subscription
- Failed payment (card declined: 4000 0000 0000 0002)
- 3D Secure required (4000 0027 6000 3184)
- Trial subscription
- Upgrade/downgrade
- Cancellation

### 3. Webhook Testing
Use Stripe CLI:
```bash
stripe listen --forward-to localhost:5000/webhooks/stripe
```

---

## Security Considerations

1. **Never expose Stripe Secret Key** on client-side
2. **Validate webhook signatures** to prevent fake events
3. **Use HTTPS** in production
4. **Store payment methods in Stripe**, not your database
5. **Implement rate limiting** on subscription endpoints
6. **Log all transactions** for audit trail
7. **Sanitize user inputs** to prevent injection attacks

---

## Deployment Checklist

- [ ] Switch to Stripe Live mode (update keys)
- [ ] Set up production webhook endpoint
- [ ] Configure email service (SendGrid, Mailgun, etc.)
- [ ] Set up cron jobs on server
- [ ] Enable HTTPS
- [ ] Add error monitoring (Sentry, LogRocket)
- [ ] Test all payment flows
- [ ] Create refund/cancellation policy
- [ ] Set up customer support system
- [ ] Backup database regularly

---

## Next Steps

1. **Implement Phase 1 MVP** (2 weeks)
2. **Test thoroughly** with Stripe test mode
3. **Add email notifications** (Phase 2)
4. **Build analytics dashboard** (Phase 2)
5. **Implement drip content** (Phase 3)
6. **Add discount codes** (Phase 3)
7. **Launch beta** with limited users
8. **Iterate based on feedback**

---

**End of Guide**
