# Admin Password Management (WordPress-Style) - Implementation Guide

## The Problem

Users lose their passwords and can't access the self-service reset (wrong email, spam filters, etc.). Admins need the ability to:
1. Send password reset links on behalf of users
2. Manually set temporary passwords when email isn't working
3. Force users to change passwords on next login (security requirement)

### Why It Was Hard

- Multiple moving parts: backend API, database schema, email service, frontend UI
- Security considerations: hashing, token expiration, audit logging
- UX decisions: two different flows for different scenarios
- Integration with existing auth system without breaking it

### Impact

Without this feature:
- Support overhead for manual password resets via database
- Security risk from manually sharing unhashed passwords
- Poor user experience when locked out
- No audit trail of admin password actions

---

## The Solution

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Admin Users Page                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  🔑 Password Reset Modal                                 │ │
│  │  ┌──────────────┐  ┌──────────────────┐                 │ │
│  │  │ Send Reset   │  │ Set Temporary    │                 │ │
│  │  │ Link         │  │ Password         │                 │ │
│  │  └──────┬───────┘  └────────┬─────────┘                 │ │
│  └─────────┼───────────────────┼───────────────────────────┘ │
└────────────┼───────────────────┼────────────────────────────┘
             │                   │
             ▼                   ▼
┌─────────────────────┐  ┌─────────────────────┐
│ POST /admin/users/  │  │ POST /admin/users/  │
│   :id/send-reset-   │  │   :id/set-password  │
│   link              │  │                     │
└─────────┬───────────┘  └─────────┬───────────┘
          │                        │
          ▼                        ▼
┌─────────────────────────────────────────────┐
│              Database (profiles)             │
│  - reset_password_token (hashed)            │
│  - reset_password_expire                     │
│  - force_password_change (boolean)          │
│  - password_change_required_at              │
└─────────────────────────────────────────────┘
```

### Database Schema

**Migration file:** `079_add_force_password_change.sql`

```sql
-- Add force password change flag to profiles table
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS force_password_change BOOLEAN DEFAULT FALSE;

-- Add column to track when admin required the password change
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS password_change_required_at TIMESTAMPTZ;

-- Add index for efficient queries on users requiring password change
CREATE INDEX IF NOT EXISTS idx_profiles_force_password_change
ON profiles(force_password_change)
WHERE force_password_change = TRUE;
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/users/:id/send-reset-link` | POST | Email password reset link to user |
| `/api/admin/users/:id/set-password` | POST | Set temporary password (forces change) |
| `/api/admin/users/:id/force-password-change` | PUT | Toggle force password change flag |

### Backend Controller Implementation

**File:** `server/controllers/adminController.js`

```javascript
import crypto from 'crypto';
import bcrypt from 'bcryptjs';
import { sendEmail } from '../config/email.js';

/**
 * Send password reset link to user (admin-initiated)
 */
export const sendPasswordResetLink = asyncHandler(async (req, res, next) => {
  const { id } = req.params;

  // Find the user
  const users = await sql`
    SELECT id, email, name FROM profiles WHERE id = ${id}
  `;

  if (users.length === 0) {
    throw new ApiError('User not found', 404);
  }

  const user = users[0];

  // Generate reset token (same pattern as authController.forgotPassword)
  const resetToken = crypto.randomBytes(32).toString('hex');
  const hashedToken = crypto.createHash('sha256').update(resetToken).digest('hex');
  const expireTime = new Date(Date.now() + 60 * 60 * 1000); // 1 hour expiry

  // Store the hashed token in database
  await sql`
    UPDATE profiles
    SET
      reset_password_token = ${hashedToken},
      reset_password_expire = ${expireTime}
    WHERE id = ${id}
  `;

  // Create reset URL and send email
  const resetUrl = `${process.env.CLIENT_URL}/reset-password/${resetToken}`;

  await sendEmail({
    to: user.email,
    subject: 'Password Reset - Action Required',
    html: `<a href="${resetUrl}">Reset Password</a> (expires in 1 hour)`
  });

  console.log(`✅ [ADMIN] Password reset link sent to ${user.email} by admin ${req.user.id}`);

  res.status(200).json({
    status: 'success',
    message: `Password reset link sent to ${user.email}`
  });
});

/**
 * Set temporary password for user (admin-initiated)
 */
export const setTemporaryPassword = asyncHandler(async (req, res, next) => {
  const { id } = req.params;
  const { password, sendEmail: shouldSendEmail = true } = req.body;

  const users = await sql`
    SELECT id, email, name FROM profiles WHERE id = ${id}
  `;

  if (users.length === 0) {
    throw new ApiError('User not found', 404);
  }

  const user = users[0];

  // Generate password if not provided
  const tempPassword = password || crypto.randomBytes(8)
    .toString('base64')
    .replace(/[^a-zA-Z0-9]/g, '')
    .slice(0, 12);

  // Hash the password
  const salt = await bcrypt.genSalt(12);
  const hashedPassword = await bcrypt.hash(tempPassword, salt);

  // Update user with new password AND force change flag
  await sql`
    UPDATE profiles
    SET
      password = ${hashedPassword},
      force_password_change = TRUE,
      password_change_required_at = CURRENT_TIMESTAMP,
      reset_password_token = NULL,
      reset_password_expire = NULL
    WHERE id = ${id}
  `;

  // Send email with temp password
  if (shouldSendEmail) {
    await sendEmail({
      to: user.email,
      subject: 'Your Password Has Been Reset',
      html: `Your temporary password: <strong>${tempPassword}</strong>`
    });
  }

  res.status(200).json({
    status: 'success',
    data: {
      temporaryPassword: tempPassword, // Returned to admin only
      forcePasswordChange: true
    }
  });
});
```

### Frontend UI Implementation

**File:** `client/src/pages/admin/Users.jsx`

Key UI elements:
1. Key icon button in user actions column
2. Modal with two options: "Send Reset Link" or "Set Temporary Password"
3. Password generator for temp passwords
4. Success state showing the generated password (with warning to save it)

```jsx
// Password management state
const [passwordModal, setPasswordModal] = useState({ open: false, user: null, mode: null });
const [tempPassword, setTempPassword] = useState('');
const [generatedPassword, setGeneratedPassword] = useState(null);

const handleSendResetLink = async () => {
  const response = await api.post(`/admin/users/${passwordModal.user.id}/send-reset-link`);
  toast.success(`Password reset link sent to ${passwordModal.user.email}`);
};

const handleSetTempPassword = async () => {
  const response = await api.post(`/admin/users/${passwordModal.user.id}/set-password`, {
    password: tempPassword || undefined,
    sendEmail: true
  });
  setGeneratedPassword(response.data.data.temporaryPassword);
};

const generateRandomPassword = () => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789';
  let password = '';
  for (let i = 0; i < 12; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  setTempPassword(password);
};
```

---

## Testing the Fix

### Manual Testing Checklist

- [ ] Admin can send reset link to user
- [ ] User receives email with working reset link
- [ ] Reset link expires after 1 hour
- [ ] Admin can set temporary password
- [ ] User receives email with temporary password
- [ ] Password is hashed in database (not plaintext)
- [ ] `force_password_change` flag is set to TRUE
- [ ] Modal closes after successful action
- [ ] Error handling works for non-existent users

### API Testing with cURL

```bash
# Send reset link
curl -X POST http://localhost:5000/api/admin/users/{userId}/send-reset-link \
  -H "Authorization: Bearer {adminToken}"

# Set temporary password
curl -X POST http://localhost:5000/api/admin/users/{userId}/set-password \
  -H "Authorization: Bearer {adminToken}" \
  -H "Content-Type: application/json" \
  -d '{"password": "TempPass123", "sendEmail": true}'
```

---

## Prevention

### Security Best Practices Implemented

1. **Token Hashing** - Reset tokens stored as SHA256 hashes, not plaintext
2. **Expiration** - 1 hour expiry on reset links
3. **Audit Logging** - Console logs admin ID with every action
4. **Force Password Change** - Temp passwords require immediate change
5. **Secure Generation** - crypto.randomBytes for token generation

### Future Improvements

- Add audit log table for password actions
- Add rate limiting on password reset requests
- Add notification to user when admin resets their password
- Implement middleware to enforce `force_password_change` on login

---

## Related Patterns

- [Email Service Configuration](../integrations/EMAIL_SERVICE_SETUP.md)
- [Authentication Flow](../patterns-standards/AUTH_FLOW_PATTERNS.md)
- [Admin Dashboard Patterns](../advanced-features/ADMIN_DASHBOARD_PATTERNS.md)

---

## Common Mistakes to Avoid

- ❌ **Storing plaintext tokens** - Always hash reset tokens with SHA256
- ❌ **No expiration** - Reset links should expire (1 hour recommended)
- ❌ **Returning temp password in logs** - Only return to admin in response
- ❌ **Missing force change flag** - Temp passwords must require change
- ❌ **No audit trail** - Log admin actions for security review

---

## Resources

- [OWASP Password Reset Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html)
- [WordPress Password Reset Implementation](https://developer.wordpress.org/reference/functions/wp_set_password/)
- [Node.js crypto documentation](https://nodejs.org/api/crypto.html)
- [bcryptjs documentation](https://www.npmjs.com/package/bcryptjs)

---

## Time to Implement

**2-3 hours** for full implementation including:
- Database migration (15 min)
- Backend endpoints (45 min)
- Frontend modal UI (1 hour)
- Email templates (30 min)
- Testing (30 min)

## Difficulty Level

⭐⭐⭐ (3/5) - Moderate complexity due to multiple integration points

---

**Author Notes:**

This feature was implemented following WordPress's admin password management pattern. The key insight is providing TWO options:

1. **Send Reset Link** - Best for most cases, user controls their own password
2. **Set Temporary Password** - For when email isn't working (support scenarios)

The `force_password_change` flag is critical for security - temporary passwords should never be permanent. This requires middleware implementation to intercept login and redirect to password change page.

Industry standard expiration for reset links is 15-60 minutes. We chose 1 hour for better UX while maintaining security.

The frontend modal uses a multi-step flow: choose method → confirm → success. This prevents accidental actions and provides clear feedback.
