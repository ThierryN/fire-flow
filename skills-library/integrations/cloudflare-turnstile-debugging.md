# Cloudflare Turnstile CAPTCHA Debugging Guide

## Overview

This guide documents how to debug Cloudflare Turnstile integration issues, particularly the common "timeout-or-duplicate" error that occurs when registration appears to fail but the root cause is elsewhere.

## The Common Misdiagnosis

**Symptom:** Registration fails with "CAPTCHA verification failed" message.

**Initial assumption:** Turnstile is broken or timing out.

**Reality:** Turnstile often passes successfully, but a downstream error (e.g., database issue) causes the request to fail. The frontend then retries with the same token, which Cloudflare rejects as "timeout-or-duplicate" because tokens can only be used ONCE.

## Debugging Approach

### Step 1: Add Detailed Backend Logging

Add step-by-step logging to identify exactly where the failure occurs:

```javascript
export const register = asyncHandler(async (req, res, next) => {
  try {
    const { name, email, password, turnstileToken } = req.body;
    console.log('[Auth] Register attempt for:', name, email);

    // Turnstile verification
    if (process.env.TURNSTILE_SECRET_KEY) {
      console.log('[Auth] Turnstile token received:', turnstileToken ? turnstileToken.substring(0, 30) + '...' : 'MISSING');
      const turnstileResult = await verifyTurnstile(turnstileToken, clientIp);
      console.log('[Auth] Turnstile result:', JSON.stringify(turnstileResult));
      if (!turnstileResult.success) {
        console.log('[Auth] Turnstile verification FAILED:', turnstileResult['error-codes']);
        return next(new ApiError('CAPTCHA verification failed', 400));
      }
      console.log('[Auth] Turnstile verification PASSED');
    }

    // Step-by-step logging for each operation
    console.log('[Auth] Step 1: Checking if user exists...');
    // ... user check code

    console.log('[Auth] Step 2: Hashing password...');
    // ... password hashing

    console.log('[Auth] Step 3: Generating verification token...');
    // ... token generation

    console.log('[Auth] Step 4: Inserting user into database...');
    try {
      // ... database insert
      console.log('[Auth] User inserted successfully, id:', insertResult[0]?.id);
    } catch (insertError) {
      console.error('[Auth] DATABASE INSERT ERROR:', insertError.message);
      console.error('[Auth] Insert error details:', insertError.code, insertError.detail);
      throw insertError;
    }

    console.log('[Auth] Step 5: Auto-assigning free membership...');
    // ... membership assignment

    console.log('[Auth] Step 6: Sending verification email...');
    // ... email sending

    console.log('[Auth] Step 7: Firing plugin hooks...');
    // ... hooks

    console.log('[Auth] Step 8: Registration complete, sending response...');
    // ... success response

  } catch (error) {
    console.error('[Auth] REGISTRATION ERROR at final catch:', error.message);
    console.error('[Auth] Error stack:', error.stack);
    console.error('[Auth] Error code:', error.code);
    return next(new ApiError('Registration failed', 500));
  }
});
```

### Step 2: Frontend Token Reset on Error

Ensure the frontend resets the Turnstile token on ANY error (since tokens are single-use):

```javascript
registerMutation.mutate(userData, {
  onSuccess: () => {
    // Reset Turnstile for potential future use
    if (turnstileRef.current) {
      turnstileRef.current.reset();
    }
    setTurnstileToken('');
    setTurnstileStatus('loading');
  },
  onError: () => {
    // CRITICAL: Reset Turnstile on error - token can only be used once
    setTimeout(() => {
      if (turnstileRef.current) {
        turnstileRef.current.reset();
      }
      setTurnstileToken('');
      setTurnstileStatus('loading');
    }, 100);
  }
});
```

### Step 3: Add Status Tracking

Track Turnstile widget status for better UX:

```javascript
const [turnstileStatus, setTurnstileStatus] = useState('loading'); // 'loading' | 'ready' | 'expired' | 'error'

<Turnstile
  ref={turnstileRef}
  siteKey={TURNSTILE_SITE_KEY}
  onSuccess={(token) => {
    setTurnstileToken(token);
    setTurnstileStatus('ready');
  }}
  onError={() => {
    setTurnstileToken('');
    setTurnstileStatus('error');
  }}
  onExpire={() => {
    setTurnstileToken('');
    setTurnstileStatus('expired');
  }}
  options={{
    theme: 'light',
    size: 'normal',
    retry: 'auto',
    retryInterval: 3000,
    refreshExpired: 'auto',
  }}
/>
```

## Common Root Causes

### 1. Missing Database Columns

**Error in logs:**
```
column "email_verification_token" of relation "profiles" does not exist
```

**Fix:** Run migration to add missing columns:
```sql
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255);
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email_verification_expire TIMESTAMPTZ;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
```

### 2. Duplicate Token Usage

**Error codes:** `['timeout-or-duplicate']`

**Cause:** Token was already verified (possibly during a failed attempt that reached Cloudflare but then failed elsewhere).

**Fix:** Ensure frontend resets token on ANY error, not just success.

### 3. Token Expiration

**Error codes:** `['timeout-or-duplicate']` with old timestamp

**Cause:** User took too long to fill out the form after completing CAPTCHA.

**Fix:** Add `refreshExpired: 'auto'` option to automatically refresh expired tokens.

## Log Analysis Pattern

When debugging, look for this sequence in PM2 logs:

1. `[Auth] Turnstile verification PASSED` - Token was valid
2. `POST /api/auth/register 500` - Request failed AFTER Turnstile
3. Second request with `timeout-or-duplicate` - Retry with stale token

If you see pattern 1+2, the issue is NOT Turnstile - look at the error between Step 1 and Step 8.

## VPS Log Commands

```bash
# Watch logs in real-time
pm2 logs lms-server --lines 100

# Search for auth-related logs
pm2 logs lms-server --lines 500 | grep "\[Auth\]"

# Check error log specifically
tail -100 ~/.pm2/logs/lms-server-error.log
```

## Related Files

- `server/controllers/authController.js` - Registration logic
- `client/src/pages/auth/Register.jsx` - Frontend form
- `server/migrations/078_add_email_verification_columns.sql` - Missing columns fix

## Session Reference

This debugging pattern was developed during the Jan 9, 2026 session to fix a production registration issue where Turnstile appeared to fail but the real cause was missing `email_verification_token` column in the profiles table.
