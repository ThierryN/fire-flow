# SMTP SSL Certificate Hostname Mismatch on Shared Hosting - Solution

## The Problem

When sending emails (e.g., verification emails) from a Node.js application on shared hosting, you get an SSL certificate error:

```
Hostname/IP does not match certificate's altnames:
Host: mail.yourdomain.com. is not in the cert's altnames:
DNS:autoconfig.server1.hostingprovider.com,
DNS:mail.server1.hostingprovider.com,
DNS:server1.hostingprovider.com,
...
```

### Why It Was Hard

- The error message is confusing - it lists hostnames that ARE valid, not what's wrong
- Many developers assume they need to disable SSL entirely (insecure)
- The `rejectUnauthorized: false` setting doesn't always work as expected
- Understanding shared hosting SSL certificate architecture isn't obvious
- Multiple potential solutions exist, unclear which is best

### Impact

- Email verification fails for new users
- Password reset emails don't send
- Any transactional email fails
- Users cannot complete registration/enrollment flows

---

## The Solution

### Root Cause

On shared hosting, your mail subdomain `mail.yourdomain.com` is a DNS alias pointing to the hosting provider's actual mail server (e.g., `mail.server1.hostingprovider.com`).

The SSL certificate on that server covers the **provider's hostnames**, not your domain's hostname. When nodemailer connects to `mail.yourdomain.com`, SSL verification fails because that hostname isn't in the certificate.

### Two Solutions

#### Option A: Use the Provider's Mail Server Hostname (Quick Fix)

Change your `EMAIL_HOST` environment variable to use the hostname that's actually in the certificate:

```bash
# Instead of:
EMAIL_HOST=mail.yourdomain.com

# Use:
EMAIL_HOST=mail.server1.hostingprovider.com
```

**How to find the correct hostname:**
Look at the error message - it lists all valid hostnames. Find the one that starts with `mail.` (e.g., `mail.server1.hostingprovider.com`).

**Why this works:**
- You connect to the hostname that matches the certificate (SSL passes)
- You still authenticate with your email credentials (`user@yourdomain.com`)
- Emails are still sent FROM your domain (controlled by `EMAIL_FROM`)
- Recipients see your domain, not the provider's

#### Option B: Install SSL Certificate for Your Mail Subdomain (Proper Fix)

Get an SSL certificate that covers `mail.yourdomain.com`:

1. **In cPanel:** Go to SSL/TLS Status or AutoSSL
2. **Find your mail subdomain** in the list
3. **Issue/install a certificate** for `mail.yourdomain.com`
4. After installation, keep `EMAIL_HOST=mail.yourdomain.com`

This is cleaner but requires:
- Purchasing or provisioning an SSL cert
- Access to cPanel/hosting control panel
- Waiting for cert issuance (can take minutes to hours)

---

## Code Implementation

### Nodemailer Configuration with TLS Fallback

```javascript
// server/config/email.js
import nodemailer from 'nodemailer';

const createTransporter = () => {
  const config = {
    host: process.env.EMAIL_HOST,
    port: parseInt(process.env.EMAIL_PORT || '465'),
    secure: process.env.EMAIL_PORT === '465',
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASSWORD
    }
  };

  // Allow hostname-mismatched certs for shared hosting
  // Set EMAIL_TLS_REJECT_UNAUTHORIZED=false to enable this
  const rejectUnauthorized = process.env.EMAIL_TLS_REJECT_UNAUTHORIZED !== 'false';

  config.tls = {
    rejectUnauthorized,
  };

  return nodemailer.createTransport(config);
};
```

### Environment Variables

```bash
# .env file

# Option A: Use provider's hostname (recommended for shared hosting)
EMAIL_HOST=mail.server1.hostingprovider.com
EMAIL_PORT=465
EMAIL_USER=noreply@yourdomain.com
EMAIL_PASSWORD=your-email-password
EMAIL_FROM="Your App <noreply@yourdomain.com>"

# Optional: Disable TLS verification (less secure fallback)
# Only use if Option A doesn't work
EMAIL_TLS_REJECT_UNAUTHORIZED=false
```

---

## Testing the Fix

### Before Fix
```
Error: Hostname/IP does not match certificate's altnames
Email sending: FAILED
```

### After Fix (Option A)
```
[EmailService] Connecting to mail.server1.hostingprovider.com:465
[EmailService] Email sent successfully: <message-id@yourdomain.com>
Email sending: SUCCESS
```

### Verification Steps

1. SSH into server
2. Update `.env` with new `EMAIL_HOST`
3. Restart application: `pm2 restart all`
4. Test email sending (e.g., trigger verification email)
5. Check logs for success message

---

## Prevention

1. **Document your hosting's mail server hostname** - Keep it in deployment docs
2. **Use environment variables** - Never hardcode mail server hostnames
3. **Add TLS fallback option** - Include `EMAIL_TLS_REJECT_UNAUTHORIZED` in your config
4. **Test email in staging** - Before deploying to production

---

## Related Patterns

- [env-file-management-production-local.md](./env-file-management-production-local.md) - Environment variable management
- [deployment-changes-not-applying.md](./deployment-changes-not-applying.md) - Debugging deployment issues

---

## Common Mistakes to Avoid

- **Setting `rejectUnauthorized: false` blindly** - This disables ALL certificate verification. Use Option A instead.
- **Assuming your domain has its own mail cert** - On shared hosting, it usually doesn't.
- **Not restarting PM2 after .env changes** - PM2 caches environment variables.
- **Using `pm2 restart` instead of `pm2 delete && pm2 start`** - Sometimes restart doesn't reload env vars.

---

## Hosting Provider Examples

| Provider | Typical Mail Hostname |
|----------|----------------------|
| cPanel shared | `mail.serverX.provider.com` |
| Hostinger | `smtp.hostinger.com` |
| Bluehost | `mail.yourdomain.com` (usually has cert) |
| GoDaddy | `smtpout.secureserver.net` |
| SiteGround | `mail.yourdomain.com` (usually has cert) |

**Always check the error message** - it tells you exactly which hostnames are valid.

---

## Resources

- [Nodemailer TLS Options](https://nodemailer.com/smtp/#tls-options)
- [Let's Encrypt for cPanel](https://docs.cpanel.net/knowledge-base/security/ssl-tls/)
- [Understanding SSL Certificate SANs](https://www.ssl.com/faqs/what-is-a-san-certificate/)

---

## Time to Implement

**Option A:** 5 minutes (just change env var)
**Option B:** 15-60 minutes (depends on SSL provisioning time)

## Difficulty Level

**Diagnosis:** 3/5 - Error message is confusing
**Fix:** 1/5 - Just an env var change once you understand the issue

---

**Author Notes:**

This issue is extremely common on shared hosting but poorly documented. The key insight is understanding that `mail.yourdomain.com` is just a DNS alias - the actual server uses the hosting provider's certificate.

The error message actually gives you the solution - it lists all the valid hostnames. Look for the one starting with `mail.` and use that as your `EMAIL_HOST`.

Don't waste time trying to make `rejectUnauthorized: false` work. Just use the correct hostname. It's simpler, more secure, and works reliably.
