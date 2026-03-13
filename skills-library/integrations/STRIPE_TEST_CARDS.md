# 💳 Stripe Test Card Numbers

**Last Updated:** November 4, 2024
**Purpose:** Quick reference for testing Stripe payments during development

---

## 🧪 Test Card Scenarios

### ✅ **Successful Payment**
```
Card Number:  4242 4242 4242 4242
Expiry:       12/25 (or any future date)
CVC:          123 (any 3 digits)
Zip Code:     10002 (any zip code)
```
**Result:** Payment succeeds immediately ✅

---

### ❌ **Card Declined**
```
Card Number:  4000 0000 0000 0002
Expiry:       12/25 (or any future date)
CVC:          123 (any 3 digits)
Zip Code:     10002 (any zip code)
```
**Result:** Payment declined (card was declined) ❌
**Use Case:** Test error handling for declined cards

---

### 📍 **Invalid Zip Code**
```
Card Number:  4000 0000 0000 0003
Expiry:       12/25 (or any future date)
CVC:          123 (any 3 digits)
Zip Code:     Any (will fail AVS zip check)
```
**Result:** Payment fails due to zip code mismatch ❌
**Use Case:** Test address validation errors

---

### 🔐 **3D Secure Authentication Required**
```
Card Number:  4000 0027 6000 3184
Expiry:       12/25 (or any future date)
CVC:          123 (any 3 digits)
Zip Code:     10002 (any zip code)
```
**Result:** 3D Secure modal appears, requires authentication 🔐
**Use Case:** Test 3D Secure authentication flow

---

## 🧑‍💼 Test User Credentials

```
Email:    admin@lms.test
Password: Password123
```

---

## 🚀 Testing Workflow

### Test 1: Card Declined → Success (2 Attempts)
1. Add item to cart
2. Go to checkout
3. **FGTAT ATTEMPT** - Use: `4000 0000 0000 0002` (will decline)
4. See error message: "Your card was declined"
5. **SECOND ATTEMPT** - Use: `4242 4242 4242 4242` (will succeed)
6. Payment completes, order marked as "paid"

### Test 2: Quick Success
1. Add item to cart
2. Go to checkout
3. Use: `4242 4242 4242 4242`
4. Payment succeeds on first try ✅

### Test 3: 3D Secure Authentication
1. Add item to cart
2. Go to checkout
3. Use: `4000 0027 6000 3184`
4. 3D Secure modal appears
5. Complete authentication in modal
6. Payment succeeds ✅

---

## 📋 Common Test Details

| Field | Value | Notes |
|-------|-------|-------|
| Card Holder Name | Any name | Test name like "John Doe" |
| Expiry Month | 12 | Use any future month |
| Expiry Year | 25 | 2025 or later |
| CVC | 123 | Any 3 digits work |
| Zip Code | 10002 | Use for successful payments |

---

## 🔗 References

- Stripe Test Mode: https://stripe.com/docs/testing
- Test Cards: https://stripe.com/docs/payments/test-cards
- 3D Secure: https://stripe.com/docs/payments/3d-secure

---

**Keep this file open while testing payment flows!** 🎯
