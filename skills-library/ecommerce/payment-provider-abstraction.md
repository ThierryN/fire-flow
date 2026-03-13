# Payment Provider Abstraction Layer

> Adapter pattern for swapping payment providers without re-architecting. Supports Stripe, PayPal, and future providers.

**When to use:** Building a payment system that may need to support multiple providers, or creating a provider-agnostic payment API.
**Stack:** Node.js/Express, TypeScript recommended

---

## The Problem

Without abstraction:
- Adding a second payment provider requires changing every payment-related file
- Provider-specific code (Stripe's `client_secret`, PayPal's `order_id`) leaks into business logic
- Testing requires live provider credentials
- Switching providers is a rewrite, not a configuration change

---

## Provider Interface

```typescript
interface PaymentProvider {
  name: string;

  // Create a payment session (checkout)
  createPaymentSession(params: {
    amount: number;          // In smallest currency unit (cents)
    currency: string;        // ISO 4217 (usd, eur, gbp)
    customerId?: string;     // Your internal customer ID
    metadata?: Record<string, string>;
    successUrl?: string;
    cancelUrl?: string;
  }): Promise<PaymentSession>;

  // Capture a previously authorized payment
  capturePayment(sessionId: string): Promise<PaymentResult>;

  // Refund a completed payment
  refundPayment(params: {
    paymentId: string;
    amount?: number;         // Partial refund (omit for full refund)
    reason?: string;
  }): Promise<RefundResult>;

  // Get payment status
  getPaymentStatus(paymentId: string): Promise<PaymentStatus>;

  // Verify webhook signature
  verifyWebhook(params: {
    body: Buffer | string;
    signature: string;
    secret: string;
  }): Promise<WebhookEvent>;
}

interface PaymentSession {
  id: string;                // Provider's session/order ID
  checkoutUrl: string;       // URL to redirect user to
  expiresAt?: Date;
  providerData?: any;        // Raw provider response (for debugging)
}

interface PaymentResult {
  success: boolean;
  paymentId: string;         // Provider's payment/transaction ID
  amount: number;
  currency: string;
  status: 'captured' | 'pending' | 'failed';
}

interface RefundResult {
  success: boolean;
  refundId: string;
  amount: number;
  status: 'completed' | 'pending' | 'failed';
}

type PaymentStatus = 'pending' | 'authorized' | 'captured' | 'failed' | 'refunded' | 'cancelled';

interface WebhookEvent {
  id: string;
  type: string;              // Normalized event type
  paymentId?: string;
  data: Record<string, any>;
}
```

---

## Stripe Implementation

```typescript
import Stripe from 'stripe';

class StripeProvider implements PaymentProvider {
  name = 'stripe';
  private stripe: Stripe;

  constructor(secretKey: string) {
    this.stripe = new Stripe(secretKey);
  }

  async createPaymentSession(params) {
    const session = await this.stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [{
        price_data: {
          currency: params.currency,
          product_data: { name: 'Order' },
          unit_amount: params.amount,
        },
        quantity: 1,
      }],
      mode: 'payment',
      success_url: params.successUrl,
      cancel_url: params.cancelUrl,
      metadata: params.metadata,
    });

    return {
      id: session.id,
      checkoutUrl: session.url,
      expiresAt: new Date(session.expires_at * 1000),
      providerData: session,
    };
  }

  async capturePayment(sessionId) {
    const session = await this.stripe.checkout.sessions.retrieve(sessionId);
    return {
      success: session.payment_status === 'paid',
      paymentId: session.payment_intent as string,
      amount: session.amount_total,
      currency: session.currency,
      status: session.payment_status === 'paid' ? 'captured' : 'pending',
    };
  }

  async refundPayment(params) {
    const refund = await this.stripe.refunds.create({
      payment_intent: params.paymentId,
      amount: params.amount,
      reason: params.reason as any,
    });
    return {
      success: refund.status === 'succeeded',
      refundId: refund.id,
      amount: refund.amount,
      status: refund.status === 'succeeded' ? 'completed' : 'pending',
    };
  }

  async getPaymentStatus(paymentId) {
    const intent = await this.stripe.paymentIntents.retrieve(paymentId);
    const statusMap = {
      succeeded: 'captured',
      processing: 'pending',
      requires_payment_method: 'failed',
      canceled: 'cancelled',
    };
    return statusMap[intent.status] || 'pending';
  }

  async verifyWebhook(params) {
    const event = this.stripe.webhooks.constructEvent(
      params.body, params.signature, params.secret
    );
    return {
      id: event.id,
      type: this.normalizeEventType(event.type),
      paymentId: (event.data.object as any).payment_intent,
      data: event.data.object as any,
    };
  }

  private normalizeEventType(stripeType: string): string {
    const map = {
      'checkout.session.completed': 'payment.completed',
      'payment_intent.succeeded': 'payment.captured',
      'payment_intent.payment_failed': 'payment.failed',
      'charge.refunded': 'payment.refunded',
    };
    return map[stripeType] || stripeType;
  }
}
```

---

## Payment Service (Provider-Agnostic)

```typescript
class PaymentService {
  private providers: Map<string, PaymentProvider> = new Map();
  private defaultProvider: string;

  constructor(defaultProvider: string) {
    this.defaultProvider = defaultProvider;
  }

  registerProvider(provider: PaymentProvider) {
    this.providers.set(provider.name, provider);
  }

  getProvider(name?: string): PaymentProvider {
    const providerName = name || this.defaultProvider;
    const provider = this.providers.get(providerName);
    if (!provider) throw new Error(`Payment provider '${providerName}' not registered`);
    return provider;
  }

  // All business logic uses these methods — never calls providers directly
  async createCheckout(params: { amount: number; currency: string; provider?: string }) {
    return this.getProvider(params.provider).createPaymentSession(params);
  }

  async processRefund(params: { paymentId: string; amount?: number; provider?: string }) {
    return this.getProvider(params.provider).refundPayment(params);
  }
}

// Setup
const paymentService = new PaymentService('stripe');
paymentService.registerProvider(new StripeProvider(process.env.STRIPE_SECRET_KEY));
// paymentService.registerProvider(new PayPalProvider(process.env.PAYPAL_CLIENT_ID));

export { paymentService };
```

---

## Adding a New Provider

1. Implement `PaymentProvider` interface
2. Call `paymentService.registerProvider(new YourProvider(...))`
3. Done — all existing business logic works without changes

---

## Sources

- Internal gap analysis: GAP-ECOM-6 (Payment Method Abstraction)
- Medusa.js v2: Payment Module Provider architecture (2025)
- Stripe Agent Toolkit: Provider interface patterns (2025)
