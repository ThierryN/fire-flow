# ES Module Import Hoisting & dotenv - The Silent Initialization Bug

## The Problem

Environment variables from `.env` files are always `undefined` when checked at module load time, even though:
- The `.env` file exists and has correct values
- `dotenv.config()` is called at the top of your entry file
- The server logs show `.env` was loaded

### Error Messages

```
Error: Stripe is not configured. Please set STRIPE_SECRET_KEY environment variable.
```

```
[PaymentService] STRIPE_SECRET_KEY available: false
[PaymentService] Stripe initialized: false
[dotenv@17.2.3] injecting env (46) from .env    ← Notice: dotenv loads AFTER!
[Server] Loaded environment from: .env
```

### Why It Was Hard

- **Counter-intuitive** - `dotenv.config()` is at the TOP of server.js, yet runs AFTER imports
- **Silent failure** - No errors during startup, services just initialize with `null`
- **Misleading logs** - Server says "Loaded environment" but services already failed
- **Works in CommonJS** - The same pattern works fine with `require()`, so developers don't expect it to break with ES Modules
- **Intermittent appearance** - Sometimes works if import order happens to be favorable

### Impact

- Payment processing fails (Stripe)
- Authentication fails (JWT secrets)
- Database connections fail
- Email services fail
- Any service initialized at module load time fails

---

## The Solution

### Root Cause: ES Module Execution Order

In ES Modules, **all imports are hoisted and fully executed** before ANY of the importing module's code runs.

```javascript
// server.js - What you WRITE:
import dotenv from 'dotenv';
dotenv.config();  // You think this runs first

import { paymentService } from './services/paymentService.js';

// server.js - What ACTUALLY HAPPENS:
// 1. paymentService.js is FULLY EXECUTED (including top-level code)
// 2. dotenv module is loaded
// 3. THEN server.js code runs (dotenv.config())
```

So if `paymentService.js` has:

```javascript
// paymentService.js - TOP-LEVEL CODE (runs at import time!)
const stripe = process.env.STRIPE_SECRET_KEY
    ? new Stripe(process.env.STRIPE_SECRET_KEY)
    : null;  // Always null because dotenv hasn't loaded yet!
```

This code runs **before** `dotenv.config()` is called, so `process.env.STRIPE_SECRET_KEY` is always `undefined`.

### How to Fix: Lazy Initialization Pattern

Replace top-level initialization with a getter function that initializes on first use:

**BEFORE (Broken):**
```javascript
// paymentService.js
import Stripe from 'stripe';

// BAD: Runs at import time, before dotenv loads!
const stripe = process.env.STRIPE_SECRET_KEY
    ? new Stripe(process.env.STRIPE_SECRET_KEY)
    : null;

export const createPayment = async () => {
    if (!stripe) throw new Error('Stripe not configured');
    // ...
};
```

**AFTER (Fixed):**
```javascript
// paymentService.js
import Stripe from 'stripe';

// GOOD: Lazy initialization - runs on first use, after dotenv loads
let stripe = null;
let stripeInitialized = false;

const getStripe = () => {
    if (!stripeInitialized) {
        stripeInitialized = true;
        if (process.env.STRIPE_SECRET_KEY) {
            stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
            console.log('[PaymentService] ✅ Stripe initialized successfully');
        } else {
            console.warn('[PaymentService] ⚠️ STRIPE_SECRET_KEY not set');
        }
    }
    return stripe;
};

export const createPayment = async () => {
    const stripeInstance = getStripe();
    if (!stripeInstance) throw new Error('Stripe not configured');
    // Use stripeInstance instead of stripe
};
```

### Alternative Fix: Dynamic Import

If you can't modify the service file, use dynamic import:

```javascript
// server.js
import dotenv from 'dotenv';
dotenv.config();

// Dynamic import - runs AFTER this point
const { paymentService } = await import('./services/paymentService.js');
```

---

## Testing the Fix

### Before Fix - Logs Show Wrong Order
```
[PaymentService] STRIPE_SECRET_KEY available: false   ← Checked BEFORE dotenv
[PaymentService] Stripe initialized: false
[dotenv@17.2.3] injecting env from .env               ← dotenv loads AFTER
[Server] Loaded environment from: .env
```

### After Fix - Lazy Init Works
```
[dotenv@17.2.3] injecting env from .env
[Server] Loaded environment from: .env
[Server] Starting...
[PaymentService] ✅ Stripe initialized successfully (lazy)   ← On first use
```

### Verification Test
```javascript
// Add this to verify the fix
console.log('[DEBUG] At import time, STRIPE_SECRET_KEY is:',
    process.env.STRIPE_SECRET_KEY ? 'SET' : 'NOT SET');
```

If this shows "NOT SET" at the top of your service file but "SET" inside a function, you have this bug.

---

## Prevention

### 1. Never Initialize at Top Level
```javascript
// ❌ BAD - Top-level initialization
const client = new ThirdPartyClient(process.env.API_KEY);

// ✅ GOOD - Lazy initialization
let client = null;
const getClient = () => {
    if (!client && process.env.API_KEY) {
        client = new ThirdPartyClient(process.env.API_KEY);
    }
    return client;
};
```

### 2. Use Config Modules with Lazy Loading
```javascript
// config/stripe.js
let stripe = null;
let initialized = false;

export const getStripe = () => {
    if (!initialized) {
        initialized = true;
        if (process.env.STRIPE_SECRET_KEY) {
            stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
        }
    }
    return stripe;
};
```

### 3. Check for This Pattern in Code Reviews

Look for:
```javascript
// Red flags at module top level:
const x = process.env.SOMETHING;
const client = new Client(process.env.KEY);
if (process.env.FEATURE_FLAG) { ... }
```

### 4. Add Startup Verification

```javascript
// server.js - after dotenv.config()
const requiredEnvVars = ['STRIPE_SECRET_KEY', 'JWT_SECRET', 'DATABASE_URL'];
const missing = requiredEnvVars.filter(v => !process.env[v]);
if (missing.length) {
    console.error('Missing required environment variables:', missing);
    process.exit(1);
}
```

---

## Related Patterns

- [PM2 Environment Variable Caching](../deployment-security/PM2_ENVIRONMENT_VARIABLE_CACHING.md)
- [Environment File Management](../deployment-security/env-file-management-production-local.md)

---

## Common Mistakes to Avoid

- ❌ **Top-level `process.env` checks** - Always undefined before dotenv
- ❌ **Assuming import order matters** - ES Modules hoist ALL imports
- ❌ **Using CommonJS patterns in ES Modules** - `require()` order ≠ `import` order
- ❌ **Debug logging at top level** - Shows misleading "not set" messages
- ❌ **Conditional exports based on env** - Will always use the "else" branch

---

## Why This Works in CommonJS But Not ES Modules

### CommonJS (require) - Works
```javascript
// server.js - CommonJS
require('dotenv').config();  // Runs immediately, synchronously

// This import happens AFTER dotenv.config()
const payment = require('./services/payment');
// payment.js top-level code now has access to env vars
```

### ES Modules (import) - Broken
```javascript
// server.js - ES Modules
import dotenv from 'dotenv';
dotenv.config();  // You THINK this runs first...

import { payment } from './services/payment.js';
// BUT payment.js was already FULLY EXECUTED before this line!
```

The key difference: `require()` is a function that runs synchronously at that point in the code. `import` is a declaration that's hoisted and resolved before any code runs.

---

## Resources

- [MDN: ES Modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [Node.js: ES Modules](https://nodejs.org/api/esm.html)
- [dotenv with ES Modules](https://github.com/motdotla/dotenv#how-do-i-use-dotenv-with-import)

---

## Time to Implement

**10-15 minutes** per service - Convert top-level init to lazy getter pattern

## Difficulty Level

⭐⭐⭐⭐ (4/5) - Very hard to diagnose, easy to fix once understood

---

**Author Notes:**

This bug cost 2+ hours of debugging. The symptoms are extremely confusing:
- `.env` file has the right values
- Server logs show "Loaded environment from: .env"
- But services report env vars as undefined

The critical insight: **In ES Modules, ALL imports execute BEFORE your code runs.**

Once you understand this, the fix is obvious. But getting there requires understanding the fundamental difference between CommonJS and ES Modules execution models.

**Key diagnostic:** Look at the LOG ORDER. If service initialization logs appear BEFORE the dotenv loading log, you have this bug.

**Discovery date:** January 2026
**Project:** MERN Community LMS
**Symptom:** "Stripe is not configured" despite valid .env file
