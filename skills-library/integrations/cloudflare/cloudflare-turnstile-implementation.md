# Cloudflare Turnstile CAPTCHA - Complete Implementation Guide

## Overview

Cloudflare Turnstile is a CAPTCHA alternative that provides bot protection without user friction. This guide covers complete implementation for a MERN stack application with registration spam protection.

## Prerequisites

1. **Cloudflare Account** with Turnstile access
2. **Site Key** (public, used in frontend)
3. **Secret Key** (private, used in backend verification)

## Setup in Cloudflare Dashboard

1. Go to Cloudflare Dashboard → Turnstile
2. Click "Add Site"
3. Enter your domain (e.g., `schooloftheprophets.club`)
4. Choose widget mode: "Managed" (recommended)
5. Copy the **Site Key** and **Secret Key**

## Environment Variables

### Client (.env or .env.local)
```bash
VITE_TURNSTILE_SITE_KEY=0x4AAAAAAxxxxxxxxxxxxxx
```

### Server (.env)
```bash
TURNSTILE_SECRET_KEY=0x4AAAAAAxxxxxxxxxxxxxx_server_key
```

## Frontend Implementation (React)

### Install Dependencies
```bash
npm install @marsidev/react-turnstile
```

### Register.jsx - Complete Implementation

```jsx
import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { toast } from 'react-hot-toast';
import { Turnstile } from '@marsidev/react-turnstile';
import { useRegister } from '../../hooks/useQueries';
import { parseApiError } from '../../utils/errorUtils';

const TURNSTILE_SITE_KEY = import.meta.env.VITE_TURNSTILE_SITE_KEY;

const Register = () => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false,
  });

  // Turnstile state
  const [turnstileToken, setTurnstileToken] = useState('');
  const [turnstileStatus, setTurnstileStatus] = useState('loading'); // 'loading' | 'ready' | 'expired' | 'error'
  const turnstileRef = useRef(null);

  const navigate = useNavigate();
  const registerMutation = useRegister();

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();

    // Validation
    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (!formData.agreeToTerms) {
      toast.error('Please agree to the terms and conditions');
      return;
    }

    // CRITICAL: Require Turnstile if site key is configured
    if (TURNSTILE_SITE_KEY) {
      console.log('[Register] Turnstile check - token:', turnstileToken ? 'present' : 'missing', 'status:', turnstileStatus);

      if (!turnstileToken) {
        if (turnstileStatus === 'expired') {
          toast.error('CAPTCHA verification expired. Please complete it again.');
        } else if (turnstileStatus === 'error') {
          toast.error('CAPTCHA error. Please refresh the page and try again.');
        } else {
          toast.error('Please complete the CAPTCHA verification');
        }
        return;
      }
    }

    // IMPORTANT: Capture token immediately to prevent race conditions
    const capturedToken = turnstileToken;
    console.log('[Register] Submitting with token:', capturedToken ? capturedToken.substring(0, 20) + '...' : 'none');

    const userData = {
      name: `${formData.firstName} ${formData.lastName}`.trim(),
      email: formData.email,
      password: formData.password,
      turnstileToken: capturedToken || undefined,
    };

    registerMutation.mutate(userData, {
      onSuccess: () => {
        toast.success('Registration successful! Check your email to verify your account.');

        // Reset Turnstile for potential future use
        if (turnstileRef.current) {
          turnstileRef.current.reset();
        }
        setTurnstileToken('');
        setTurnstileStatus('loading');

        // Redirect to login
        setTimeout(() => navigate('/login'), 2000);
      },
      onError: () => {
        // CRITICAL: Reset Turnstile on ANY error
        // Tokens can only be verified ONCE by Cloudflare
        // If we don't reset, retry will fail with "timeout-or-duplicate"
        setTimeout(() => {
          if (turnstileRef.current) {
            turnstileRef.current.reset();
          }
          setTurnstileToken('');
          setTurnstileStatus('loading');
        }, 100);
      }
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields... */}

      {/* Cloudflare Turnstile CAPTCHA */}
      {TURNSTILE_SITE_KEY && (
        <div className="space-y-2">
          <div className="flex justify-center">
            <Turnstile
              ref={turnstileRef}
              siteKey={TURNSTILE_SITE_KEY}
              onSuccess={(token) => {
                console.log('[Turnstile] Success - token received');
                setTurnstileToken(token);
                setTurnstileStatus('ready');
              }}
              onError={() => {
                console.log('[Turnstile] Error');
                setTurnstileToken('');
                setTurnstileStatus('error');
                toast.error('CAPTCHA failed to load. Please refresh the page.');
              }}
              onExpire={() => {
                console.log('[Turnstile] Token expired');
                setTurnstileToken('');
                setTurnstileStatus('expired');
              }}
              options={{
                theme: 'light',
                size: 'normal',
                retry: 'auto',           // Auto-retry on failure
                retryInterval: 3000,     // Retry every 3 seconds
                refreshExpired: 'auto',  // Auto-refresh expired tokens
              }}
            />
          </div>

          {/* Visual feedback for token status */}
          {turnstileStatus === 'expired' && (
            <div className="flex items-center justify-center text-sm text-amber-600 bg-amber-50 border border-amber-200 rounded px-3 py-2">
              <span>Verification expired. Please complete the CAPTCHA again.</span>
            </div>
          )}
          {turnstileStatus === 'error' && (
            <div className="flex items-center justify-center text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
              <span>CAPTCHA error. Please refresh the page.</span>
            </div>
          )}
        </div>
      )}

      <button type="submit" disabled={registerMutation.isPending}>
        {registerMutation.isPending ? 'Creating account...' : 'Create Account'}
      </button>
    </form>
  );
};

export default Register;
```

## Backend Implementation (Node.js/Express)

### authController.js - Turnstile Verification

```javascript
import crypto from 'crypto';
import bcrypt from 'bcryptjs';
import sql from '../config/sql.js';
import { ApiError } from '../middleware/errorHandler.js';
import asyncHandler from '../middleware/asyncHandler.js';

/**
 * Verify Cloudflare Turnstile token
 * @param {String} token - Turnstile response token from frontend
 * @param {String} ip - Client IP address (optional, improves security)
 * @returns {Promise<Object>} - Verification result { success: boolean, error-codes: [] }
 */
const verifyTurnstile = async (token, ip = null) => {
  const secretKey = process.env.TURNSTILE_SECRET_KEY;

  // Skip verification if no secret key configured (development mode)
  if (!secretKey) {
    console.warn('[Auth] TURNSTILE_SECRET_KEY not configured - skipping CAPTCHA verification');
    return { success: true, skipped: true };
  }

  try {
    const formData = new URLSearchParams();
    formData.append('secret', secretKey);
    formData.append('response', token);
    if (ip) formData.append('remoteip', ip);

    const response = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    });

    const result = await response.json();
    console.log('[Auth] Turnstile verification response:', JSON.stringify(result));
    return result;
  } catch (error) {
    console.error('[Auth] Turnstile verification error:', error.message);
    return { success: false, error: 'Verification service unavailable' };
  }
};

/**
 * Register user with Turnstile CAPTCHA protection
 */
export const register = asyncHandler(async (req, res, next) => {
  try {
    const { name, email, password, turnstileToken } = req.body;
    console.log('[Auth] Register attempt for:', name, email);

    // Basic validation
    if (!name || !email || !password) {
      return next(new ApiError('Please provide name, email, and password', 400));
    }

    // Verify Turnstile CAPTCHA (if configured)
    if (process.env.TURNSTILE_SECRET_KEY) {
      console.log('[Auth] Turnstile token received:', turnstileToken ? turnstileToken.substring(0, 30) + '...' : 'MISSING');

      if (!turnstileToken) {
        console.log('[Auth] No turnstile token provided');
        return next(new ApiError('Please complete the CAPTCHA verification', 400));
      }

      const clientIp = req.ip || req.connection?.remoteAddress;
      console.log('[Auth] Verifying turnstile with Cloudflare, client IP:', clientIp);

      const turnstileResult = await verifyTurnstile(turnstileToken, clientIp);
      console.log('[Auth] Turnstile result:', JSON.stringify(turnstileResult));

      if (!turnstileResult.success) {
        console.log('[Auth] Turnstile verification FAILED:', turnstileResult['error-codes']);
        return next(new ApiError('CAPTCHA verification failed. Please try again.', 400));
      }
      console.log('[Auth] Turnstile verification PASSED');
    }

    // Check if user exists
    console.log('[Auth] Step 1: Checking if user exists...');
    const userResult = await sql`SELECT * FROM profiles WHERE email = ${email}`;
    if (userResult.length > 0) {
      return next(new ApiError('User already exists', 400));
    }

    // Hash password
    console.log('[Auth] Step 2: Hashing password...');
    const salt = await bcrypt.genSalt(12);
    const hashedPassword = await bcrypt.hash(password, salt);

    // Generate email verification token
    console.log('[Auth] Step 3: Generating verification token...');
    const verificationToken = crypto.randomBytes(32).toString('hex');
    const hashedVerificationToken = crypto.createHash('sha256').update(verificationToken).digest('hex');
    const verificationExpire = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours

    // Insert user
    console.log('[Auth] Step 4: Inserting user into database...');
    const insertResult = await sql.unsafe(
      `INSERT INTO profiles (name, email, password, role, email_verified, email_verification_token, email_verification_expire)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       RETURNING id, name, email, role`,
      [name, email, hashedPassword, 'user', false, hashedVerificationToken, verificationExpire]
    );
    console.log('[Auth] User inserted successfully, id:', insertResult[0]?.id);
    const newUser = insertResult[0];

    // Auto-assign free membership (optional)
    console.log('[Auth] Step 5: Auto-assigning free membership...');
    try {
      const freeLevel = await sql`SELECT id FROM membership_levels WHERE slug = 'free' AND is_active = true LIMIT 1`;
      if (freeLevel.length > 0) {
        await sql`
          INSERT INTO user_memberships (user_id, membership_level_id, status, started_at)
          VALUES (${newUser.id}, ${freeLevel[0].id}, 'active', CURRENT_TIMESTAMP)
        `;
        console.log('[Auth] Free membership assigned');
      }
    } catch (membershipError) {
      console.error('[Auth] Failed to assign free membership:', membershipError.message);
      // Don't fail registration if membership assignment fails
    }

    // Send verification email (non-blocking)
    console.log('[Auth] Step 6: Sending verification email...');
    // ... email sending code ...

    console.log('[Auth] Step 8: Registration complete, sending response...');
    res.status(201).json({
      status: 'success',
      message: 'Registration successful! Please check your email to verify your account.',
      data: newUser,
    });
  } catch (error) {
    console.error('[Auth] REGISTRATION ERROR:', error.message);
    console.error('[Auth] Error stack:', error.stack);
    return next(new ApiError('Registration failed', 500));
  }
});
```

## Database Schema Requirements

The profiles table needs these columns for email verification:

```sql
-- Migration: Add email verification columns
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255);
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email_verification_expire TIMESTAMPTZ;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;

-- Index for efficient token lookups
CREATE INDEX IF NOT EXISTS idx_profiles_email_verification_token
ON profiles(email_verification_token)
WHERE email_verification_token IS NOT NULL;
```

## Critical Implementation Notes

### 1. Token Single-Use Behavior

**Cloudflare Turnstile tokens can only be verified ONCE.**

If your backend verification succeeds but the request fails later (e.g., database error), the frontend cannot retry with the same token. Cloudflare will return `timeout-or-duplicate`.

**Solution:** Always reset the Turnstile widget on ANY error:

```javascript
onError: () => {
  setTimeout(() => {
    if (turnstileRef.current) {
      turnstileRef.current.reset();
    }
    setTurnstileToken('');
    setTurnstileStatus('loading');
  }, 100);
}
```

### 2. Token Capture Before Async Operations

Capture the token value BEFORE starting async operations to prevent race conditions where the token state might change:

```javascript
const capturedToken = turnstileToken; // Capture immediately
registerMutation.mutate({ ...userData, turnstileToken: capturedToken });
```

### 3. Status Tracking for UX

Track the widget status to provide appropriate error messages:
- `loading` - Widget is initializing
- `ready` - Token received, ready to submit
- `expired` - Token expired, needs refresh
- `error` - Widget failed to load

### 4. Graceful Degradation

If Turnstile is not configured (no site key), the form should still work:

```javascript
{TURNSTILE_SITE_KEY && (
  <Turnstile ... />
)}
```

Backend should also skip verification if secret key is not set:

```javascript
if (!process.env.TURNSTILE_SECRET_KEY) {
  return { success: true, skipped: true };
}
```

## Debugging Tips

### PM2 Log Analysis

```bash
# Watch logs in real-time
pm2 logs lms-server --lines 100

# Look for auth-specific logs
pm2 logs lms-server --lines 500 | grep "\[Auth\]"
```

### Expected Log Sequence (Success)

```
[Auth] Register attempt for: John Doe john@example.com
[Auth] Turnstile token received: 0.N-XAnnM26LxCGvNp...
[Auth] Verifying turnstile with Cloudflare, client IP: ::ffff:127.0.0.1
[Auth] Turnstile verification response: {"success":true,...}
[Auth] Turnstile verification PASSED
[Auth] Step 1: Checking if user exists...
[Auth] Step 2: Hashing password...
[Auth] Step 3: Generating verification token...
[Auth] Step 4: Inserting user into database...
[Auth] User inserted successfully, id: xxxx-xxxx-xxxx
[Auth] Step 5: Auto-assigning free membership...
[Auth] Free membership assigned
[Auth] Step 6: Sending verification email...
[Auth] Step 8: Registration complete, sending response...
POST /api/auth/register 201 2037.828 ms
```

### Common Error Codes

| Error Code | Meaning | Solution |
|------------|---------|----------|
| `timeout-or-duplicate` | Token already used or expired | Reset widget and get new token |
| `invalid-input-secret` | Wrong secret key | Check TURNSTILE_SECRET_KEY env var |
| `invalid-input-response` | Malformed token | Ensure token is passed correctly |
| `bad-request` | Request format error | Check Content-Type and body format |

## Files Reference

- `client/src/pages/auth/Register.jsx` - Frontend implementation
- `server/controllers/authController.js` - Backend verification
- `server/migrations/078_add_email_verification_columns.sql` - Database schema
- `.claude/skills/cloudflare-turnstile-debugging.md` - Debugging guide

## Session Context

This implementation was completed on January 9, 2026 to add registration spam protection. The initial debugging session revealed that a "Turnstile failure" was actually caused by missing database columns - the Turnstile verification passed but the INSERT failed, causing a retry with a stale token.

Key learnings:
1. Add step-by-step logging to identify exact failure points
2. Turnstile tokens are single-use - reset on ANY error
3. Check database schema when registration fails after Turnstile passes
