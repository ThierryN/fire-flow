# Checkout UX Conversion Patterns

> Evidence-based checkout design patterns that yield up to 35% conversion lift. Template for AI agents generating checkout flows.

**When to use:** Building or reviewing any checkout flow. Apply these patterns when scaffolding checkout components.
**Stack:** React, Next.js, or any frontend framework

---

## The 10 Checkout Rules

### 1. Guest Checkout First

```jsx
// WRONG: Force account creation before checkout
<Button onClick={() => navigate('/register')}>Create Account to Continue</Button>

// RIGHT: Guest checkout with optional account creation after purchase
<Button onClick={() => navigate('/checkout')}>Continue as Guest</Button>
<Button variant="secondary" onClick={() => navigate('/login')}>Sign In</Button>
// After order confirmation:
<p>Save your info for next time?</p>
<Button onClick={createAccountFromOrder}>Create Account</Button>
```

**Why:** 24% of users abandon when forced to create an account (Baymard).

### 2. Progress Indicator

```jsx
function CheckoutProgress({ currentStep }) {
  const steps = ['Cart', 'Shipping', 'Payment', 'Confirm'];
  return (
    <div className="flex justify-between mb-8" role="progressbar">
      {steps.map((step, i) => (
        <div key={step} className={`flex items-center ${i <= currentStep ? 'text-blue-600' : 'text-gray-400'}`}>
          <span className={`w-8 h-8 rounded-full flex items-center justify-center
            ${i < currentStep ? 'bg-blue-600 text-white' : i === currentStep ? 'border-2 border-blue-600' : 'border border-gray-300'}`}>
            {i < currentStep ? '✓' : i + 1}
          </span>
          <span className="ml-2 text-sm">{step}</span>
        </div>
      ))}
    </div>
  );
}
```

### 3. Inline Validation

```jsx
// WRONG: Validate only on submit, show all errors at top
// RIGHT: Validate each field on blur, show error next to field
<input
  type="email"
  onBlur={(e) => {
    if (!e.target.value.includes('@')) {
      setErrors(prev => ({ ...prev, email: 'Please enter a valid email' }));
    } else {
      setErrors(prev => ({ ...prev, email: null }));
    }
  }}
/>
{errors.email && <span className="text-red-500 text-sm mt-1">{errors.email}</span>}
```

### 4. Transparent Pricing (No Surprise Costs)

```jsx
function OrderSummary({ items, shipping, tax, discount }) {
  const subtotal = items.reduce((sum, i) => sum + i.price * i.quantity, 0);
  const total = subtotal + shipping + tax - discount;

  return (
    <div className="border rounded p-4">
      <h3 className="font-bold mb-4">Order Summary</h3>
      {items.map(item => (
        <div key={item.id} className="flex justify-between text-sm mb-2">
          <span>{item.name} x{item.quantity}</span>
          <span>${(item.price * item.quantity).toFixed(2)}</span>
        </div>
      ))}
      <hr className="my-2" />
      <div className="flex justify-between text-sm">
        <span>Subtotal</span><span>${subtotal.toFixed(2)}</span>
      </div>
      <div className="flex justify-between text-sm">
        <span>Shipping</span>
        <span>{shipping === 0 ? 'FREE' : `$${shipping.toFixed(2)}`}</span>
      </div>
      <div className="flex justify-between text-sm">
        <span>Tax</span><span>${tax.toFixed(2)}</span>
      </div>
      {discount > 0 && (
        <div className="flex justify-between text-sm text-green-600">
          <span>Discount</span><span>-${discount.toFixed(2)}</span>
        </div>
      )}
      <hr className="my-2" />
      <div className="flex justify-between font-bold">
        <span>Total</span><span>${total.toFixed(2)}</span>
      </div>
    </div>
  );
}
```

**Why:** 49% of users abandon when extra costs (shipping, tax) are shown too late (Baymard).

### 5. Trust Signals Near Payment

```jsx
<div className="flex items-center gap-2 text-sm text-gray-600 mt-4">
  <LockIcon className="w-4 h-4" />
  <span>Secure checkout powered by Stripe</span>
</div>
<div className="flex gap-4 mt-2">
  <img src="/visa.svg" alt="Visa" className="h-6" />
  <img src="/mastercard.svg" alt="Mastercard" className="h-6" />
  <img src="/amex.svg" alt="Amex" className="h-6" />
</div>
```

### 6. Mobile-Optimized Touch Targets

```css
/* Minimum 44x44px touch targets (Apple HIG) */
.checkout-button {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 24px;
  font-size: 16px; /* Prevents iOS zoom on focus */
}

.checkout-input {
  min-height: 44px;
  font-size: 16px; /* Critical: prevents auto-zoom on iOS */
  padding: 12px;
}
```

### 7. Prevent Double-Submit

```jsx
function CheckoutButton({ onSubmit }) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleClick = async () => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
      await onSubmit();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <button onClick={handleClick} disabled={isSubmitting}
      className={`w-full py-3 rounded ${isSubmitting ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'} text-white`}>
      {isSubmitting ? 'Processing...' : 'Complete Purchase'}
    </button>
  );
}
```

### 8. Address Autocomplete

```jsx
// Use browser's built-in autocomplete
<input name="street-address" autoComplete="street-address" />
<input name="city" autoComplete="address-level2" />
<input name="state" autoComplete="address-level1" />
<input name="postal-code" autoComplete="postal-code" />
<input name="country" autoComplete="country" />
```

### 9. Edit Cart Without Leaving Checkout

```jsx
// Show editable cart summary in sidebar/drawer during checkout
// Don't force user back to /cart page to change quantities
<CartItem>
  <QuantitySelector value={item.quantity}
    onChange={(qty) => updateCartItem(item.id, qty)} />
  <RemoveButton onClick={() => removeCartItem(item.id)} />
</CartItem>
```

### 10. Clear Error Recovery

```jsx
// After payment failure, show clear next steps
{paymentError && (
  <div className="bg-red-50 border border-red-200 rounded p-4 mb-4">
    <p className="font-medium text-red-800">Payment could not be processed</p>
    <p className="text-sm text-red-600 mt-1">{paymentError.message}</p>
    <p className="text-sm mt-2">You can try a different card or payment method below.</p>
  </div>
)}
```

---

## Verification Checklist

```
□ Guest checkout available (no forced registration)
□ Progress indicator visible
□ Inline field validation on blur
□ All costs shown before payment step
□ Trust signals near payment form
□ Touch targets ≥ 44x44px on mobile
□ Input font-size ≥ 16px (prevents iOS zoom)
□ Submit button disabled after click
□ Address autocomplete attributes set
□ Cart editable from checkout page
□ Clear error messages on payment failure
```

---

## Sources

- Baymard Institute: "Current State of Checkout UX" (2025)
- Amazon-Bench (arXiv:2508.15832) — E-Commerce Agent Safety Benchmark (Aug 2025)
- Apple Human Interface Guidelines: Touch target sizing
