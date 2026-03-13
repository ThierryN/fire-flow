# Membership System Quick Reference

**Last Updated**: 2025-11-27

---

## Top 3 WordPress Plugins by Use Case

### Best Overall: MemberPress
- **Price**: $179.50-$999/year
- **Best For**: Comprehensive features, professional sites
- **Key Features**: Unlimited levels, drip content, courses, coaching, zero transaction fees
- **Why**: Most complete solution with best support

### Best Value: Restrict Content Pro
- **Price**: $99/year (all features)
- **Best For**: Budget-conscious sites needing core features
- **Key Features**: Content restriction, drip content, 34 add-ons
- **Why**: Unbeatable price, no feature gating

### Best Free: Paid Memberships Pro
- **Price**: Free core + $347-$597/year for pro
- **Best For**: Starting out, testing concepts
- **Key Features**: 22/26 standard features, 60+ add-ons, strong free version
- **Why**: Best free option with upgrade path

---

## Top 5 Open Source GitHub Repos

### 1. eddywashere/node-stripe-membership-saas
- **Stack**: Express, MongoDB, Stripe
- **Use**: Full-stack boilerplate
- **Stars**: Popular, well-maintained
- **Link**: https://github.com/eddywashere/node-stripe-membership-saas

### 2. service-bot/servicebot
- **Stack**: Express, React, Redux, Stripe
- **Use**: Complete subscription management
- **Features**: Billing automation, quotes, free trials
- **Link**: https://github.com/service-bot/servicebot

### 3. stripe-samples/subscription-use-cases
- **Stack**: React + 7 server languages
- **Use**: Official Stripe examples
- **Features**: Fixed prices, usage-based billing
- **Link**: https://github.com/stripe-samples/subscription-use-cases

### 4. afaraldo/membership-system
- **Stack**: Node.js, Express, MongoDB
- **Use**: Organization membership management
- **Features**: Renewals, reminders, quotas, reporting
- **Link**: https://github.com/afaraldo/membership-system

### 5. clerk/use-stripe-subscription
- **Stack**: React hooks
- **Use**: Easy Stripe integration
- **Features**: Standardized React SDK for Stripe Billing
- **Link**: https://github.com/clerk/use-stripe-subscription

---

## Must-Have Features Priority

### Tier 1: Launch Essentials
1. User authentication (JWT)
2. 3 membership levels (Free, Standard, Premium)
3. Stripe payment integration
4. Basic content restriction (pages/courses)
5. User dashboard (view/cancel subscription)

### Tier 2: Retention Features
6. Free trials (7-14 days)
7. Drip content (days after enrollment)
8. Grace periods (3-7 days after failed payment)
9. Email notifications (welcome, renewal, payment failed)
10. Basic analytics (MRR, churn, active members)

### Tier 3: Growth Features
11. Discount codes
12. Member directory with privacy controls
13. Advanced analytics dashboard
14. Multiple drip schedules (calendar, prerequisite)
15. Referral/affiliate system

---

## Recommended Database Schema (MongoDB)

```javascript
// Core Collections

membershipLevels {
  name, rank, price, billingPeriod, trialDays, stripePriceId, features[]
}

userMemberships {
  userId, membershipLevelId, status, stripeCustomerId,
  stripeSubscriptionId, trialEndDate, startDate, endDate,
  nextBillingDate, gracePeriodEnd
}

contentRules {
  contentType, contentId, requiredLevelId, dripDays, dripDate
}

transactions {
  userMembershipId, amount, gateway, gatewayTransactionId,
  status, type, createdAt
}
```

---

## Key Metrics to Track

### Financial
- **MRR** (Monthly Recurring Revenue): Primary metric
- **CLV** (Customer Lifetime Value): Long-term profitability
- **ARPU** (Average Revenue Per User): Revenue / Users

### Retention
- **Churn Rate**: (Lost / Total) × 100
- **Retention Rate**: (Retained / Total) × 100
- **Trial Conversion**: Trial → Paid %

### Engagement
- **Active Users**: Daily/Weekly/Monthly
- **Content Access**: Most viewed content
- **Login Frequency**: Engagement indicator

---

## Stripe Best Practices

### Payment Retry Logic
1. Immediate retry
2. 3 days later
3. 7 days later
4. 14 days later

**Recovery Rate**: 70% with proper retries

### Renewal Reminders
- **7 days before**: Preferred by 53% of customers
- **Trial ending**: 7 days before end
- **Payment failed**: Immediate + 3, 7, 14 days

### Grace Periods
- **Duration**: 3-7 days recommended
- **Status**: Set to 'grace_period', maintain access
- **After expiry**: Cancel subscription

---

## Content Protection Methods

### Server-Side (Recommended)
- **Security**: Highest
- **SEO**: Requires partial content/meta tags
- **Best For**: Premium content

### Client-Side
- **Security**: Lower (can be bypassed)
- **SEO**: Better (content in HTML)
- **Best For**: Paywalls, low-security content

### Metered Paywall
- **Model**: N free views, then paywall
- **Example**: NYT (20 articles/month)
- **Tracking**: Cookies, device fingerprinting, accounts

---

## Drip Content Strategies

### Types
1. **Days After Enrollment**: Relative to join date
2. **Calendar Date**: Specific unlock date
3. **Prerequisite**: Unlock after completing X
4. **Group-Based**: Different schedules per group

### Best Practices
- Release at midnight UTC
- Clearly communicate schedule
- Show progress indicators
- Allow preview of locked content

---

## Email Notification Schedule

| Event | Timing | Priority |
|-------|--------|----------|
| Welcome | Immediate on signup | High |
| Trial Ending | 7 days before | High |
| Renewal Reminder | 7 days before | High |
| Payment Failed | Immediate | Critical |
| Payment Retry | Before each retry | High |
| Grace Period Ending | 1 day before | Critical |
| Subscription Cancelled | Immediate | Medium |
| Content Unlocked | When dripped | Low |

---

## Membership Tier Design

### Recommended Structure
- **3 tiers**: Sweet spot for choice without overwhelm
- **Cumulative benefits**: Higher tiers include lower
- **Numerical ranks**: 1 = highest, 2 = next, etc.

### Example Naming
- **Value-based**: Basic → Pro → Enterprise
- **Metal tiers**: Bronze → Silver → Gold
- **Achievement**: Member → Champion → Legend
- **Growth**: Starter → Growth → Scale

### Pricing Psychology
- **Anchor high**: Show most expensive first
- **Highlight middle**: "Most popular" badge
- **Free tier**: Lead generation
- **Trial periods**: Reduce friction (7-14 days)

---

## Security Checklist

- [ ] Never expose Stripe Secret Key client-side
- [ ] Validate webhook signatures
- [ ] Use HTTPS in production
- [ ] Store payment methods in Stripe only
- [ ] Rate limit subscription endpoints
- [ ] Log all transactions
- [ ] Sanitize user inputs
- [ ] Hash passwords with bcrypt
- [ ] Use JWT for authentication
- [ ] Implement CORS properly

---

## Technology Stack (MERN)

### Backend
- Node.js + Express
- MongoDB (Mongoose)
- Stripe SDK (`stripe`)
- JWT (`jsonwebtoken`)
- Email (`nodemailer`)
- Cron jobs (`node-cron`)

### Frontend
- React
- Stripe Elements (`@stripe/react-stripe-js`)
- Chart.js (analytics)
- React Router

### Development Tools
- Stripe CLI (webhook testing)
- Postman (API testing)
- MongoDB Compass (database viewer)

---

## Stripe Test Cards

| Scenario | Card Number | Notes |
|----------|-------------|-------|
| Success | 4242 4242 4242 4242 | Always succeeds |
| Decline | 4000 0000 0000 0002 | Generic decline |
| 3D Secure | 4000 0027 6000 3184 | Requires authentication |
| Insufficient Funds | 4000 0000 0000 9995 | Declined |

**Expiry**: Any future date
**CVC**: Any 3 digits
**ZIP**: Any 5 digits

---

## Quick Implementation Timeline

### Week 1-2: MVP
- User auth + JWT
- 3 membership levels
- Stripe integration
- Basic content restriction
- User dashboard

### Week 3-4: Enhancement
- Free trials
- Drip content (days after enrollment)
- Email notifications
- Grace periods
- Basic analytics

### Week 5-6: Growth
- Discount codes
- Member directory
- Advanced drip (calendar, prerequisite)
- Analytics dashboard
- Content engagement tracking

### Week 7-8: Polish
- UI/UX improvements
- Testing & bug fixes
- Documentation
- Beta launch preparation

---

## Common Pitfalls to Avoid

1. **Using FLOAT for money**: Always use DECIMAL or store in cents (integer)
2. **Not handling webhooks**: Critical for subscription updates
3. **Immediate cancellation**: Use cancel_at_period_end instead
4. **No grace periods**: Lose customers over temporary payment issues
5. **Weak drip content**: Let users download everything and cancel
6. **No analytics**: Can't optimize what you don't measure
7. **Poor email notifications**: Customers miss renewal, payment fails
8. **Client-side only protection**: Easily bypassed
9. **No trial reminders**: Users forget they'll be charged
10. **Ignoring churn**: Focus on retention, not just acquisition

---

## Resources

### Documentation
- [Stripe Subscriptions Docs](https://docs.stripe.com/billing/subscriptions/overview)
- [MongoDB Schema Design](https://www.mongodb.com/docs/manual/data-modeling/)
- [React Stripe.js](https://stripe.com/docs/stripe-js/react)

### Tutorials
- [GeeksforGeeks: Node.js Subscription System](https://www.geeksforgeeks.org/node-js/subscription-management-system-with-nodejs-and-expressjs/)
- [Stripe Subscription Samples](https://github.com/stripe-samples/subscription-use-cases)

### Tools
- [Stripe Dashboard](https://dashboard.stripe.com/)
- [Stripe CLI](https://stripe.com/docs/stripe-cli)
- [MongoDB Compass](https://www.mongodb.com/products/compass)

---

## Support Resources

### WordPress Plugins
- MemberPress: https://memberpress.com/support/
- Restrict Content Pro: https://restrictcontentpro.com/support/
- Paid Memberships Pro: https://www.paidmembershipspro.com/documentation/

### Payment Platforms
- Stripe Support: https://support.stripe.com/
- Stripe Community: https://stackoverflow.com/questions/tagged/stripe-payments

### Development
- Stack Overflow: https://stackoverflow.com/questions/tagged/stripe-subscriptions
- GitHub Issues: Check individual repos

---

**For detailed information, see:**
- `MEMBERSHIP_SYSTEMS_RESEARCH.md` - Full research report
- `MEMBERSHIP_IMPLEMENTATION_GUIDE.md` - MERN stack implementation

**End of Quick Reference**
