# Email Campaign Limits and Compliance Requirements

**Last Updated:** 2025-11-29
**Document Owner:** Development Team
**Status:** Active Reference

## Table of Contents

1. [CAN-SPAM Compliance Requirements](#can-spam-compliance-requirements)
2. [2024 Gmail/Yahoo Bulk Sender Requirements](#2024-gmail-yahoo-bulk-sender-requirements)
3. [SMTP Provider Limits](#smtp-provider-limits)
4. [Our Implementation Limits](#our-implementation-limits)
5. [Best Practices](#best-practices)
6. [Configuration Guide](#configuration-guide)
7. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
8. [References](#references)

---

## CAN-SPAM Compliance Requirements

The CAN-SPAM Act of 2003 establishes rules for commercial email, giving recipients the right to stop receiving emails and outlining penalties for violations.

### Required Elements

#### 1. Physical Postal Address

**Requirement:** Every email must include a valid physical postal address.

**Implementation:**
- Include organization's registered address in email footer
- Can be a street address, P.O. Box registered with USPS, or private mailbox registered with commercial mail receiving agency
- Must be currently valid and accessible

**Example:**
```
Holy Spirit Community Church
123 Main Street
Your City, ST 12345
United States
```

#### 2. Unsubscribe Mechanism

**Requirements:**
- Must be clearly visible and conspicuous
- Must function for at least 30 days after email is sent
- Must process opt-out requests within 10 business days
- Cannot require login or payment to unsubscribe
- Cannot sell or transfer email addresses of people who opt out

**Implementation Checklist:**
- [ ] Clear "Unsubscribe" link in email footer
- [ ] One-click unsubscribe process (no login required)
- [ ] Automated processing of unsubscribe requests
- [ ] Confirmation message displayed after unsubscribe
- [ ] Database flag updated within 10 business days
- [ ] Suppression list maintained permanently

#### 3. Accurate Sender Information

**Requirements:**
- "From" name must accurately identify sender
- "From" email address must be valid and monitored
- "Reply-to" address must be functional
- Routing information must be accurate

**Do NOT:**
- Use misleading header information
- Use deceptive "From" names
- Use no-reply addresses without alternative contact method

#### 4. Subject Line Accuracy

**Requirements:**
- Subject line must accurately reflect email content
- No deceptive or misleading subjects
- Must clearly indicate if email is an advertisement (if applicable)

**Examples of Violations:**
- "RE: Your Account" when no prior communication exists
- "Urgent: Action Required" for promotional content
- Subject lines completely unrelated to email body

#### 5. Commercial vs. Transactional Email

**Transactional Emails (Exempt from some CAN-SPAM rules):**
- Course enrollment confirmations
- Password resets
- Account notifications
- Receipt/donation confirmations
- Order status updates

**Commercial Emails (Subject to all CAN-SPAM rules):**
- Newsletter campaigns
- Promotional announcements
- Fundraising appeals
- Event invitations

**Note:** Even transactional emails should include unsubscribe options and accurate sender information as a best practice.

### Penalties

- **Per Violation:** Up to $51,744
- **Violations Multiply:** Each separate email in violation counts
- **Criminal Penalties:** Possible for egregious violations
- **Liability:** Business owners and employees can be held personally liable

### Compliance Quick Checklist

Before sending any bulk email campaign:

- [ ] Valid physical address in footer
- [ ] Working unsubscribe link
- [ ] Accurate "From" information
- [ ] Truthful subject line
- [ ] Content matches subject line promise
- [ ] Unsubscribe processing system tested
- [ ] Suppression list integration verified

---

## 2024 Gmail/Yahoo Bulk Sender Requirements

As of February 2024, Gmail and Yahoo Mail have implemented strict requirements for bulk senders to combat spam and improve email security.

### Threshold Definition

**Bulk Sender:** Anyone sending **5,000 or more emails per day** to Gmail or Yahoo addresses.

**Important:** This is a cumulative count across all campaigns and systems. If your organization sends:
- 2,000 newsletters
- 1,500 course notifications
- 2,000 donation receipts

You total 5,500 emails/day and are considered a bulk sender.

### Authentication Requirements

All bulk senders must implement three email authentication protocols:

#### 1. SPF (Sender Policy Framework)

**Purpose:** Verifies that emails come from authorized mail servers.

**DNS Record Example:**
```
v=spf1 include:_spf.google.com ~all
```

**Testing:**
```bash
nslookup -type=TXT yourdomain.com
```

#### 2. DKIM (DomainKeys Identified Mail)

**Purpose:** Cryptographically signs emails to verify they haven't been tampered with.

**DNS Record Example:**
```
default._domainkey.yourdomain.com TXT
"v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQ..."
```

**Implementation:** Configured through your email service provider (ESP).

#### 3. DMARC (Domain-based Message Authentication)

**Purpose:** Tells receiving servers what to do with emails that fail SPF or DKIM checks.

**DNS Record Example (Start with monitoring):**
```
_dmarc.yourdomain.com TXT
"v=DMARC1; p=none; rua=mailto:dmarc-reports@yourdomain.com"
```

**Progression Path:**
1. `p=none` - Monitor only (start here)
2. `p=quarantine` - Send failures to spam (after monitoring)
3. `p=reject` - Block failures completely (final state)

### Custom Domain Requirement

**Requirement:** Must send from your own domain, not free email providers.

**Acceptable:**
- newsletters@yourdomain.com
- noreply@yourdomain.com
- info@yourdomain.com

**NOT Acceptable:**
- yourorganization@gmail.com
- contact@yahoo.com
- info@outlook.com

### Spam Rate Thresholds

Gmail and Yahoo monitor spam complaint rates through their feedback loops.

**Spam Rate Calculation:**
```
Spam Rate = (Spam Complaints / Emails Delivered) × 100
```

**Thresholds:**
- **Target:** Keep spam rate below **0.10%** (1 complaint per 1,000 emails)
- **Warning:** Spam rates between 0.10% - 0.30% may trigger throttling
- **Critical:** Spam rates above **0.30%** will result in blocking

**Example:**
- Send 10,000 emails
- Receive 15 spam complaints
- Spam rate: (15 / 10,000) × 100 = 0.15% (Warning zone)

### One-Click Unsubscribe

**Requirement:** Bulk senders must support RFC 8058 one-click unsubscribe.

**Implementation:**
```
List-Unsubscribe: <https://yourdomain.com/unsubscribe?id=12345>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

**User Experience:**
- Gmail/Yahoo display unsubscribe button next to sender name
- Clicking button immediately unsubscribes (no page navigation)
- Must process within 2 days (stricter than CAN-SPAM's 10 days)

### Forward and Reverse DNS Alignment

**Requirement:** Your sending IP's reverse DNS (PTR) record should match your domain.

**Verification:**
```bash
# Check PTR record
nslookup -type=PTR 203.0.113.1

# Should return something like:
mail.yourdomain.com
```

### Email Content Requirements

- Valid HTML structure
- Text-only alternative (multipart/alternative)
- Reasonable image-to-text ratio
- No spam trigger words in excessive amounts
- Proper email headers

---

## SMTP Provider Limits

Understanding your SMTP provider's limits is crucial for campaign planning.

### Free/Personal Email Providers

#### Gmail (Free)

- **Daily Limit:** 500 recipients per day
- **Per Message:** 500 recipients maximum
- **Rate Limit:** ~20 emails per minute
- **Rolling Window:** 24-hour rolling period
- **Exceeding Limits:** Account may be temporarily disabled (1-24 hours)

**Use Case:** NOT suitable for bulk sending or organizational newsletters.

#### Outlook.com / Hotmail (Free)

- **Daily Limit:** 300 recipients per day
- **Per Message:** 100 recipients maximum
- **Rate Limit:** ~15 emails per minute
- **Exceeding Limits:** Temporary sending block

**Use Case:** NOT suitable for any bulk operations.

#### Yahoo Mail (Free)

- **Daily Limit:** 500 recipients per day
- **Per Message:** 100 recipients maximum
- **Exceeding Limits:** Account suspension risk

### Business Email Providers

#### Microsoft 365 / Outlook (Business)

- **Daily Limit:** 10,000 recipients per day
- **Per Message:** 500 recipients maximum
- **Rate Limit:** 30 messages per minute
- **Additional:** 10,000 recipient rate limit over 24 hours

**Use Case:** Suitable for moderate organizational email, but not high-volume campaigns.

#### Google Workspace

- **Daily Limit:** 2,000 recipients per day (per user)
- **Per Message:** 2,000 recipients (internal), 500 external
- **Rate Limit:** ~40-60 emails per minute
- **Trial Accounts:** 500 recipients per day for first 30 days

**Use Case:** Better for organizational use, but still limited for large campaigns.

### Transactional Email Service Providers (Recommended)

#### SendGrid

**Free Tier:**
- 100 emails/day forever free
- All features included

**Essentials Plan ($19.95/month):**
- 50,000 emails/month
- 10,000 contacts
- Email API and SMTP relay

**Pro Plan ($89.95/month):**
- 100,000 emails/month
- Dedicated IP option
- Advanced analytics

**Rate Limits:**
- No per-day limits within plan allocation
- API: Varies by plan (typically 600-3,000 requests/second)

#### Mailgun

**Free Tier:**
- 5,000 emails/month for first 3 months
- Then pay-as-you-go

**Flex Plan (Pay-as-you-go):**
- $0.80 per 1,000 emails
- No monthly commitment
- 1,000 email validations/month free

**Foundation Plan ($35/month):**
- 50,000 emails/month
- Email validation included

**Rate Limits:**
- Shared IP: 80 emails/second (288,000/hour)
- Dedicated IP: Negotiable based on reputation

#### Amazon SES (Simple Email Service)

**Pricing:**
- $0.10 per 1,000 emails
- $0.12 per GB of attachments
- No monthly fees

**Limits:**
- **Initial:** 200 emails/day, 1 email/second (sandbox mode)
- **After Approval:** 50,000 emails/day (can be increased)
- **Rate:** Starts at 14 emails/second, scalable

**Use Case:** Best for high-volume, cost-effective sending with AWS infrastructure.

#### Postmark

**Free Tier:**
- 100 emails/month free

**Starter Plan ($15/month):**
- 10,000 emails/month
- Unlimited templates
- 45-day history

**Production Plan ($90/month):**
- 75,000 emails/month
- 1-year history

**Rate Limits:**
- 70,000 emails/hour
- All plans include same features and speed

#### Mailchimp (Marketing-focused)

**Free Tier:**
- 500 contacts
- 1,000 sends/month
- Daily send limit: 500

**Essentials ($13/month for 500 contacts):**
- 5,000 sends/month
- A/B testing
- Custom branding

**Standard ($20/month for 500 contacts):**
- 6,000 sends/month
- Behavioral targeting
- Custom templates

**Note:** Mailchimp is designed for marketing campaigns, not transactional emails.

### Comparison Matrix

| Provider | Best For | Starting Price | Free Tier | Authentication | Support |
|----------|----------|----------------|-----------|----------------|---------|
| SendGrid | Mixed use | $19.95/mo | 100/day | Full SPF/DKIM/DMARC | Email/Chat |
| Mailgun | Developers | Pay-as-you-go | 5K/3mo | Full SPF/DKIM/DMARC | Email |
| Amazon SES | High volume | Pay-as-you-go | None | Full SPF/DKIM/DMARC | AWS Support |
| Postmark | Transactional | $15/mo | 100/mo | Full SPF/DKIM/DMARC | Email/Chat |
| Mailchimp | Marketing | $13/mo | 500 contacts | Full SPF/DKIM/DMARC | Email/Chat |

### Recommendation for This Project

**Current Phase (< 5,000 emails/day):**
- Google Workspace or Microsoft 365 is acceptable
- Implement proper authentication now
- Monitor sending volumes

**Growth Phase (> 5,000 emails/day):**
- Migrate to SendGrid or Mailgun
- Separate transactional and marketing emails
- Implement dedicated IPs for high volume

**Enterprise Phase (> 50,000 emails/day):**
- Consider Amazon SES for cost efficiency
- Dedicated IP addresses required
- Professional deliverability monitoring

---

## Our Implementation Limits

Current email sending configuration and recommended limits for this application.

### Current Rate Limiting

**Configuration Location:** `server/services/NewsletterService.js`

```javascript
const RATE_LIMIT = {
  emailsPerMinute: 50,        // Maximum 50 emails per minute
  delayBetweenEmails: 1200,   // 1.2 seconds between sends
  batchSize: 100,             // Process 100 recipients per batch
  batchDelay: 60000           // 1 minute delay between batches
};
```

**Calculated Throughput:**
- **Per Minute:** 50 emails
- **Per Hour:** 3,000 emails (theoretical maximum)
- **Per Day:** 72,000 emails (theoretical maximum)
- **Actual Recommended:** 10,000-20,000 emails/day (accounting for retries and errors)

### Why These Limits?

1. **Provider Compatibility:** Works within Google Workspace and Microsoft 365 limits
2. **Reputation Management:** Gradual sending helps maintain good sender reputation
3. **Error Handling:** Allows time for retry logic and error processing
4. **Resource Management:** Prevents server overload and database connection exhaustion

### Batch Processing Strategy

**Implementation:**

```javascript
async function sendCampaign(campaignId) {
  const recipients = await getRecipients(campaignId);
  const batches = chunkArray(recipients, RATE_LIMIT.batchSize);

  for (let i = 0; i < batches.length; i++) {
    const batch = batches[i];

    // Process batch
    await processBatch(batch, campaignId);

    // Wait between batches (except for last batch)
    if (i < batches.length - 1) {
      await delay(RATE_LIMIT.batchDelay);
    }
  }
}
```

**Benefits:**
- Prevents timeout errors
- Allows progress tracking
- Enables pause/resume functionality
- Facilitates error recovery

### Daily Sending Limits

**Recommended Limits by Use Case:**

#### Transactional Emails (High Priority)
- **Daily Allocation:** 5,000 emails
- **Examples:** Password resets, enrollment confirmations, receipts
- **Processing:** Immediate, no batching
- **Retry Logic:** Up to 3 attempts with exponential backoff

#### Newsletter Campaigns (Medium Priority)
- **Daily Allocation:** 10,000 emails
- **Examples:** Weekly newsletters, announcements
- **Processing:** Batched with rate limiting
- **Scheduling:** Off-peak hours (2 AM - 6 AM local time)

#### Bulk Campaigns (Lower Priority)
- **Daily Allocation:** 5,000 emails
- **Examples:** Fundraising appeals, event invitations
- **Processing:** Batched with extended delays
- **Scheduling:** Spread over multiple days for large lists

### Environment-Specific Limits

#### Development Environment

```env
EMAIL_RATE_LIMIT_PER_MINUTE=10
EMAIL_DAILY_LIMIT=100
EMAIL_BATCH_SIZE=10
ENABLE_EMAIL_SENDING=false  # Disable by default
```

#### Staging Environment

```env
EMAIL_RATE_LIMIT_PER_MINUTE=25
EMAIL_DAILY_LIMIT=500
EMAIL_BATCH_SIZE=50
ENABLE_EMAIL_SENDING=true
EMAIL_TEST_MODE=true  # Restrict to test domains
```

#### Production Environment

```env
EMAIL_RATE_LIMIT_PER_MINUTE=50
EMAIL_DAILY_LIMIT=20000
EMAIL_BATCH_SIZE=100
ENABLE_EMAIL_SENDING=true
EMAIL_TEST_MODE=false
```

### Monitoring Metrics

Track these metrics to ensure you stay within limits:

1. **Hourly Send Count**
   - Alert if > 3,000/hour

2. **Daily Send Count**
   - Alert if approaching daily limit (80% threshold)

3. **Bounce Rate**
   - Alert if > 5% hard bounces

4. **Spam Complaint Rate**
   - Alert if > 0.08%

5. **Queue Length**
   - Alert if email queue > 1,000 pending

### Emergency Throttling

If you detect deliverability issues:

```javascript
// Reduce sending rate by 50%
RATE_LIMIT.emailsPerMinute = 25;
RATE_LIMIT.delayBetweenEmails = 2400;

// Reduce batch size
RATE_LIMIT.batchSize = 50;

// Increase batch delay
RATE_LIMIT.batchDelay = 120000; // 2 minutes
```

---

## Best Practices

Follow these guidelines to maintain excellent email deliverability and sender reputation.

### List Hygiene and Cleaning

#### Regular Maintenance Schedule

**Weekly:**
- Remove hard bounces (email doesn't exist)
- Remove repeated soft bounces (>3 consecutive)
- Process unsubscribe requests

**Monthly:**
- Remove inactive subscribers (no opens/clicks in 6 months)
- Validate email addresses for new signups
- Clean up duplicate entries

**Quarterly:**
- Run comprehensive email validation service
- Segment inactive users for re-engagement campaign
- Archive permanently bounced addresses

#### Bounce Handling

**Hard Bounces (Permanent Failures):**
```
550 5.1.1 User unknown
550 5.1.2 Domain not found
```
**Action:** Remove immediately from active list

**Soft Bounces (Temporary Failures):**
```
450 4.2.1 Mailbox full
451 4.3.2 Service not available
```
**Action:** Retry up to 3 times over 72 hours, then remove

**Block Bounces (Spam/Policy):**
```
550 5.7.1 Message rejected due to spam
```
**Action:** Investigate immediately, may indicate reputation issue

#### Email Validation

**At Signup:**
- Implement syntax validation
- Check for disposable email domains
- Verify MX records exist
- Consider double opt-in for critical lists

**Bulk Validation Services:**
- ZeroBounce
- NeverBounce
- EmailListVerify
- Hunter.io

**Validation Frequency:**
- Before major campaigns
- After acquiring new lists
- Every 6 months minimum

### Bounce Rate Monitoring

**Acceptable Bounce Rates:**
- **Hard Bounce:** < 2%
- **Soft Bounce:** < 5%
- **Total Bounce:** < 7%

**Warning Signs:**
```
If bounce_rate > 10%:
  - Stop sending immediately
  - Review list quality
  - Check for purchased/scraped lists
  - Verify email content isn't spam

If bounce_rate > 20%:
  - Serious list quality issue
  - High risk of blacklisting
  - Urgent remediation required
```

**Implementation:**

```javascript
function calculateBounceRate(sent, bounced) {
  const rate = (bounced / sent) * 100;

  if (rate > 10) {
    logger.error(`High bounce rate detected: ${rate.toFixed(2)}%`);
    sendAlertToAdmin();
    pauseCampaign();
  } else if (rate > 5) {
    logger.warn(`Elevated bounce rate: ${rate.toFixed(2)}%`);
  }

  return rate;
}
```

### Engagement Metrics to Track

#### Open Rate

**Definition:** Percentage of recipients who open the email

**Calculation:**
```
Open Rate = (Unique Opens / Delivered Emails) × 100
```

**Benchmarks:**
- **Excellent:** > 25%
- **Good:** 15-25%
- **Average:** 10-15%
- **Poor:** < 10%

**Factors Affecting Open Rate:**
- Subject line quality
- Sender name recognition
- Send time optimization
- List segmentation

#### Click-Through Rate (CTR)

**Definition:** Percentage of recipients who click links in the email

**Calculation:**
```
CTR = (Unique Clicks / Delivered Emails) × 100
```

**Benchmarks:**
- **Excellent:** > 3%
- **Good:** 2-3%
- **Average:** 1-2%
- **Poor:** < 1%

#### Click-to-Open Rate (CTOR)

**Definition:** Percentage of openers who clicked

**Calculation:**
```
CTOR = (Unique Clicks / Unique Opens) × 100
```

**Benchmarks:**
- **Excellent:** > 15%
- **Good:** 10-15%
- **Average:** 5-10%
- **Poor:** < 5%

**Insight:** CTOR measures content relevance independent of subject line.

#### Unsubscribe Rate

**Target:** < 0.5% per campaign

**Warning Levels:**
```
< 0.2%  - Excellent
0.2-0.5% - Normal
0.5-1%  - Review content and frequency
> 1%    - Serious issue, investigate immediately
```

**Common Causes of High Unsubscribe:**
- Too frequent sending
- Irrelevant content
- Poor segmentation
- Unclear value proposition

#### Spam Complaint Rate

**Critical Metric:** Must stay below 0.1% (1 per 1,000 emails)

**Calculation:**
```
Spam Rate = (Spam Complaints / Delivered Emails) × 100
```

**Response Actions:**
```
> 0.08%  - Warning: Review content immediately
> 0.1%   - Critical: Pause campaigns
> 0.3%   - Emergency: Risk of permanent blocking
```

### Warm-Up Schedule for New Domains

**Critical:** Never start sending at high volume with a new domain or IP address.

#### Week 1-2: Establish Foundation

**Daily Volume:**
- Day 1: 50 emails
- Day 2: 100 emails
- Day 3: 200 emails
- Day 4: 300 emails
- Day 5: 500 emails
- Day 6-7: 750 emails

**Best Practices:**
- Send to most engaged subscribers only
- Monitor for any bounces or complaints
- Maintain high engagement rates
- Space sends throughout the day

#### Week 3-4: Gradual Increase

**Daily Volume:**
- Week 3: 1,000 emails/day
- Week 4: 2,000 emails/day

**Focus:**
- Continue targeting engaged users
- Monitor deliverability metrics closely
- Check inbox placement rates

#### Week 5-6: Expand Volume

**Daily Volume:**
- Week 5: 5,000 emails/day
- Week 6: 10,000 emails/day

**Activities:**
- Begin including less-engaged subscribers
- Implement segmentation strategies
- Monitor ISP-specific metrics

#### Week 7-8: Full Volume

**Daily Volume:**
- Week 7: 20,000 emails/day
- Week 8+: Full planned volume

**Maintenance:**
- Continue monitoring all metrics
- Adjust based on performance
- Maintain engagement focus

#### Warm-Up for Dedicated IP

If using a dedicated IP address:

**Slower Progression Required:**
```
Week 1:    500/day
Week 2:  1,000/day
Week 3:  2,500/day
Week 4:  5,000/day
Week 5: 10,000/day
Week 6: 20,000/day
Week 7: 50,000/day
Week 8+: Full volume
```

**Why Slower:**
- No established reputation
- ISPs track IP reputation separately
- Higher risk of blocking

### Content Best Practices

#### Subject Lines

**Length:**
- Optimal: 40-50 characters
- Maximum: 60 characters (mobile truncation)

**Avoid:**
- ALL CAPS
- Excessive punctuation (!!!)
- Spam trigger words (FREE, URGENT, ACT NOW)
- Misleading claims

**Effective Patterns:**
- Personalization: "[Name], your course is ready"
- Curiosity: "The surprising truth about..."
- Value: "5 ways to improve your learning"
- Urgency (honest): "Last day to register"

#### Email Content

**HTML Structure:**
- Maximum width: 600-650px
- Mobile-responsive design
- Alt text for all images
- Plain text version included

**Image-to-Text Ratio:**
- Target: 60% text, 40% images
- Never send image-only emails
- Keep total size under 100KB

**Links:**
- Use clear, descriptive link text
- Avoid URL shorteners
- Include unsubscribe link prominently
- Test all links before sending

#### Sender Name and Address

**From Name:**
- Use organization name or person + organization
- Keep consistent across campaigns
- Good: "Holy Spirit Community Church"
- Better: "Pastor John at Holy Spirit Church"

**From Address:**
- Use subdomain for newsletters: newsletters@yourdomain.com
- Different addresses for different types:
  - Transactional: noreply@yourdomain.com
  - Marketing: newsletter@yourdomain.com
  - Support: support@yourdomain.com

### Timing and Frequency

#### Best Send Times (General Guidelines)

**Weekdays:**
- Tuesday-Thursday: Best overall
- 10 AM - 2 PM: Peak open times
- 8 PM - 10 PM: Secondary peak

**Weekends:**
- Saturday morning: Good for B2C
- Sunday: Varies by audience (religious organizations may differ)

**Test Your Audience:**
- Run A/B tests with different send times
- Segment by timezone
- Track engagement by send time

#### Optimal Frequency

**General Recommendations:**
- **Weekly:** Most newsletters
- **Bi-weekly:** Medium engagement expected
- **Monthly:** Low-frequency updates
- **Daily:** Only for time-sensitive content with explicit opt-in

**Warning Signs of Over-Sending:**
- Rising unsubscribe rates
- Declining open rates
- Increased spam complaints

### Segmentation Strategies

#### By Engagement Level

**Highly Engaged (Opened/clicked in last 30 days):**
- Send all campaigns
- Test new content
- Request referrals

**Moderately Engaged (Opened in last 90 days):**
- Send most campaigns
- Focus on value
- Re-engagement attempts

**Low Engagement (No opens in 90+ days):**
- Send only best content
- Win-back campaigns
- Consider removing after 180 days

#### By Demographics

- Location (timezone-based sending)
- Age group
- Membership status
- Interest categories

#### By Behavior

- Course enrollments
- Donation history
- Event attendance
- Website activity

---

## Configuration Guide

Step-by-step instructions for configuring email sending in this application.

### Environment Variables

**Required Variables:**

Create or update `.env` file in the `server` directory:

```env
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=your-email@yourdomain.com
SMTP_PASSWORD=your-app-specific-password

# Sender Information
EMAIL_FROM_NAME=Holy Spirit Community Church
EMAIL_FROM_ADDRESS=noreply@yourdomain.com
EMAIL_REPLY_TO=info@yourdomain.com

# Physical Address (CAN-SPAM Compliance)
ORGANIZATION_NAME=Holy Spirit Community Church
ORGANIZATION_ADDRESS_LINE1=123 Main Street
ORGANIZATION_CITY=Your City
ORGANIZATION_STATE=ST
ORGANIZATION_ZIP=12345
ORGANIZATION_COUNTRY=United States

# Rate Limiting
EMAIL_RATE_LIMIT_PER_MINUTE=50
EMAIL_DAILY_LIMIT=20000
EMAIL_BATCH_SIZE=100
EMAIL_BATCH_DELAY=60000

# Feature Flags
ENABLE_EMAIL_SENDING=true
EMAIL_TEST_MODE=false
EMAIL_LOG_LEVEL=info

# Tracking (Optional)
EMAIL_TRACK_OPENS=true
EMAIL_TRACK_CLICKS=true
TRACKING_DOMAIN=track.yourdomain.com

# Unsubscribe
UNSUBSCRIBE_URL=https://yourdomain.com/unsubscribe
```

**Optional Variables:**

```env
# Advanced Configuration
EMAIL_POOL_SIZE=5
EMAIL_MAX_CONNECTIONS=5
EMAIL_MAX_MESSAGES_PER_CONNECTION=100

# Retry Logic
EMAIL_MAX_RETRY_ATTEMPTS=3
EMAIL_RETRY_DELAY=300000

# Monitoring
EMAIL_ALERT_EMAIL=admin@yourdomain.com
EMAIL_ALERT_THRESHOLD_BOUNCE=5
EMAIL_ALERT_THRESHOLD_SPAM=0.1
```

### SMTP Setup Instructions

#### Option 1: Google Workspace

**Step 1: Enable 2-Step Verification**
1. Go to Google Account settings
2. Navigate to Security
3. Enable 2-Step Verification

**Step 2: Generate App Password**
1. In Security settings, find "App passwords"
2. Select "Mail" and "Other (Custom name)"
3. Enter "Community LMS" as the name
4. Click Generate
5. Copy the 16-character password

**Step 3: Configure Environment**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=your-email@yourdomain.com
SMTP_PASSWORD=your-16-char-app-password
```

**Step 4: Test Connection**
```bash
cd server
node -e "require('./services/EmailService').testConnection()"
```

#### Option 2: Microsoft 365

**Configuration:**
```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=your-email@yourdomain.com
SMTP_PASSWORD=your-password
```

**Additional Settings:**
- Enable SMTP AUTH in Microsoft 365 Admin Center
- Ensure account has appropriate licenses

#### Option 3: SendGrid

**Step 1: Create SendGrid Account**
1. Sign up at https://sendgrid.com
2. Verify your email address
3. Complete sender authentication

**Step 2: Create API Key**
1. Go to Settings > API Keys
2. Click "Create API Key"
3. Name it "Community LMS Production"
4. Select "Full Access"
5. Copy the API key (shown only once)

**Step 3: Configure Environment**
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=apikey
SMTP_PASSWORD=SG.your-actual-api-key-here
```

**Step 4: Authenticate Domain (Required)**
1. Settings > Sender Authentication
2. Click "Authenticate Your Domain"
3. Follow DNS record instructions
4. Wait for verification (can take up to 48 hours)

#### Option 4: Mailgun

**Step 1: Create Mailgun Account**
1. Sign up at https://mailgun.com
2. Add and verify your domain

**Step 2: Get SMTP Credentials**
1. Go to Sending > Domain Settings
2. Find SMTP credentials section
3. Note the hostname and credentials

**Step 3: Configure Environment**
```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=postmaster@yourdomain.com
SMTP_PASSWORD=your-mailgun-password
```

### Domain Authentication (SPF, DKIM, DMARC)

Critical for deliverability. Must be configured in your domain's DNS settings.

#### SPF Record Setup

**Purpose:** Authorize mail servers to send on your behalf

**Steps:**
1. Log into your domain registrar's DNS management
2. Add a new TXT record
3. Use these values:

**For Google Workspace:**
```
Type: TXT
Name: @
Value: v=spf1 include:_spf.google.com ~all
TTL: 3600
```

**For Microsoft 365:**
```
Type: TXT
Name: @
Value: v=spf1 include:spf.protection.outlook.com ~all
TTL: 3600
```

**For SendGrid:**
```
Type: TXT
Name: @
Value: v=spf1 include:sendgrid.net ~all
TTL: 3600
```

**For Multiple Providers:**
```
Type: TXT
Name: @
Value: v=spf1 include:_spf.google.com include:sendgrid.net ~all
TTL: 3600
```

**Verify SPF:**
```bash
nslookup -type=TXT yourdomain.com
```

#### DKIM Record Setup

**Purpose:** Cryptographically sign your emails

**Configuration varies by provider:**

**Google Workspace:**
1. Admin Console > Apps > Google Workspace > Gmail
2. Click "Authenticate email"
3. Select "Generate new record"
4. Copy provided DNS records
5. Add to your DNS:

```
Type: TXT
Name: google._domainkey
Value: v=DKIM1; k=rsa; p=MIIBIjANBgkqhki... (provided by Google)
TTL: 3600
```

**SendGrid:**
1. Settings > Sender Authentication > Authenticate Domain
2. Follow wizard to get DNS records
3. Add to DNS (SendGrid provides exact values):

```
Type: CNAME
Name: s1._domainkey
Value: s1.domainkey.u1234567.wl.sendgrid.net
TTL: 3600

Type: CNAME
Name: s2._domainkey
Value: s2.domainkey.u1234567.wl.sendgrid.net
TTL: 3600
```

**Mailgun:**
1. Domain Settings > DNS Records
2. Copy provided DKIM records
3. Add to DNS:

```
Type: TXT
Name: mailo._domainkey.yourdomain.com
Value: k=rsa; p=MIGfMA0GCSqGSI... (provided by Mailgun)
TTL: 3600
```

**Verify DKIM:**
```bash
nslookup -type=TXT google._domainkey.yourdomain.com
```

#### DMARC Record Setup

**Purpose:** Tell receivers what to do with emails that fail authentication

**Recommended Progression:**

**Phase 1: Monitor Only (Start Here)**
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=none; rua=mailto:dmarc-reports@yourdomain.com; ruf=mailto:dmarc-forensics@yourdomain.com; pct=100
TTL: 3600
```

**Explanation:**
- `p=none` - Monitor only, don't reject
- `rua` - Aggregate reports sent here
- `ruf` - Forensic (failure) reports sent here
- `pct=100` - Apply to 100% of emails

**Phase 2: Quarantine (After 2-4 weeks of monitoring)**
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=quarantine; pct=10; rua=mailto:dmarc-reports@yourdomain.com; ruf=mailto:dmarc-forensics@yourdomain.com
TTL: 3600
```

**Explanation:**
- `p=quarantine` - Send failures to spam
- `pct=10` - Start with 10% of emails

**Phase 3: Reject (After successful quarantine testing)**
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=reject; pct=100; rua=mailto:dmarc-reports@yourdomain.com; ruf=mailto:dmarc-forensics@yourdomain.com; adkim=s; aspf=s
TTL: 3600
```

**Explanation:**
- `p=reject` - Block failures completely
- `adkim=s` - Strict DKIM alignment
- `aspf=s` - Strict SPF alignment

**Verify DMARC:**
```bash
nslookup -type=TXT _dmarc.yourdomain.com
```

**DMARC Reporting Services (Free):**
- Postmark (https://dmarc.postmarkapp.com/)
- DMARC Analyzer (https://www.dmarcanalyzer.com/)
- Google Postmaster Tools

### Verification Checklist

After configuring DNS records, verify everything is working:

**1. DNS Propagation (wait 24-48 hours after adding records)**
```bash
# Check SPF
dig TXT yourdomain.com +short

# Check DKIM
dig TXT google._domainkey.yourdomain.com +short

# Check DMARC
dig TXT _dmarc.yourdomain.com +short
```

**2. Email Authentication Test**

Send a test email to:
- check-auth@verifier.port25.com
- Or use https://www.mail-tester.com/

**3. Gmail Postmaster Tools**
1. Sign up at https://postmaster.google.com
2. Verify domain ownership
3. Monitor reputation and delivery

**4. Application Test**

```bash
# Run application email test
cd server
npm run test:email

# Or manually trigger test
node scripts/test-email-config.js
```

### Troubleshooting Common Issues

**Issue: SPF TXT Record Not Found**
```
Solution:
- Wait 24-48 hours for DNS propagation
- Verify record is added to correct domain
- Check for typos in record value
- Use online DNS checker: https://mxtoolbox.com/spf.aspx
```

**Issue: DKIM Signature Failed**
```
Solution:
- Verify DKIM record is correctly formatted
- Ensure no spaces in TXT record value
- Check that selector matches (google._domainkey, etc.)
- Wait for DNS propagation
```

**Issue: SMTP Authentication Failed**
```
Solution:
- Verify username/password are correct
- For Gmail: Use app-specific password, not account password
- Check if 2FA is enabled (required for app passwords)
- Verify SMTP host and port are correct
- Check firewall isn't blocking port 587
```

**Issue: Emails Going to Spam**
```
Solution:
- Verify SPF, DKIM, DMARC are all passing
- Check sender reputation at https://senderscore.org
- Review email content for spam triggers
- Ensure list hygiene (low bounce rate)
- Warm up new domain/IP properly
```

---

## Monitoring and Troubleshooting

### Key Metrics Dashboard

Implement monitoring for these critical metrics:

#### Real-Time Metrics

**Email Queue Status:**
```javascript
{
  pending: 1250,        // Emails waiting to send
  processing: 50,       // Currently sending
  sent: 15840,         // Successfully sent today
  failed: 23,          // Failed today
  retrying: 5          // In retry queue
}
```

**Current Send Rate:**
```javascript
{
  emailsPerMinute: 48,
  averageDelay: 1250,   // ms between sends
  batchProgress: "3/15" // Current batch / total batches
}
```

#### Daily Metrics

**Delivery Metrics:**
```javascript
{
  sent: 15840,
  delivered: 15650,      // Successfully delivered
  bounced: 190,          // Hard + soft bounces
  hardBounces: 85,       // 0.54% - acceptable
  softBounces: 105,      // 0.66% - acceptable
  bounceRate: 1.20,      // Total bounce rate %
  deliveryRate: 98.80    // % successfully delivered
}
```

**Engagement Metrics:**
```javascript
{
  opens: 3850,           // Unique opens
  openRate: 24.59,       // % of delivered
  clicks: 425,           // Unique clicks
  clickRate: 2.71,       // % of delivered
  clickToOpenRate: 11.04 // % of opens that clicked
}
```

**Reputation Metrics:**
```javascript
{
  spamComplaints: 12,
  spamRate: 0.077,       // 0.077% - good (target < 0.1%)
  unsubscribes: 45,
  unsubscribeRate: 0.29, // 0.29% - acceptable
  listCleanedToday: 190  // Bounces + unsubscribes removed
}
```

### Logging Strategy

**Log Levels:**

```javascript
// INFO: Normal operations
logger.info('Campaign started', {
  campaignId: 123,
  recipientCount: 5000,
  estimatedDuration: '100 minutes'
});

// WARN: Elevated metrics
logger.warn('Bounce rate elevated', {
  campaignId: 123,
  bounceRate: 5.2,
  threshold: 5.0
});

// ERROR: Send failures
logger.error('Email send failed', {
  recipientEmail: 'user@example.com',
  error: 'SMTP timeout',
  retryAttempt: 1
});

// DEBUG: Detailed troubleshooting (dev only)
logger.debug('SMTP response', {
  messageId: 'abc123',
  response: '250 Message accepted'
});
```

**What to Log:**

1. **Campaign Events:**
   - Campaign start/completion
   - Batch progress
   - Pause/resume actions

2. **Delivery Events:**
   - Successful sends (with message ID)
   - Bounce details (type, reason)
   - Spam complaints
   - Unsubscribes

3. **Performance Events:**
   - Send rate fluctuations
   - Queue backlog warnings
   - Rate limit hits

4. **Error Events:**
   - SMTP connection failures
   - Authentication errors
   - Template rendering errors
   - Database errors

### Alert Configuration

**Critical Alerts (Immediate Response Required):**

```javascript
// Spam rate exceeds 0.08%
if (spamRate > 0.08) {
  sendAlert('CRITICAL', 'Spam rate exceeded safe threshold', {
    currentRate: spamRate,
    threshold: 0.08,
    action: 'Pause all campaigns immediately'
  });
}

// Bounce rate exceeds 10%
if (bounceRate > 10) {
  sendAlert('CRITICAL', 'Bounce rate dangerously high', {
    currentRate: bounceRate,
    threshold: 10,
    action: 'Stop sending and review list quality'
  });
}

// Email service authentication failure
if (smtpAuthFailed) {
  sendAlert('CRITICAL', 'SMTP authentication failed', {
    provider: smtpHost,
    action: 'Verify credentials and service status'
  });
}
```

**Warning Alerts (Monitor Closely):**

```javascript
// Bounce rate elevated (5-10%)
// Open rate declining (>20% drop)
// Queue backlog (>1000 pending)
// Daily limit approaching (80% reached)
```

**Info Alerts (Good to Know):**

```javascript
// Campaign completed successfully
// Daily summary reports
// Weekly performance trends
```

### Database Queries for Monitoring

**Daily Send Volume:**
```sql
SELECT
  DATE(sent_at) as send_date,
  COUNT(*) as total_sent,
  SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered,
  SUM(CASE WHEN status = 'bounced' THEN 1 ELSE 0 END) as bounced,
  SUM(CASE WHEN status = 'spam' THEN 1 ELSE 0 END) as spam_complaints
FROM email_logs
WHERE sent_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(sent_at)
ORDER BY send_date DESC;
```

**Bounce Rate by Campaign:**
```sql
SELECT
  c.id,
  c.name,
  COUNT(el.id) as total_sent,
  SUM(CASE WHEN el.bounce_type = 'hard' THEN 1 ELSE 0 END) as hard_bounces,
  SUM(CASE WHEN el.bounce_type = 'soft' THEN 1 ELSE 0 END) as soft_bounces,
  ROUND(
    (SUM(CASE WHEN el.status = 'bounced' THEN 1 ELSE 0 END)::numeric / COUNT(el.id)) * 100,
    2
  ) as bounce_rate_pct
FROM campaigns c
JOIN email_logs el ON c.id = el.campaign_id
GROUP BY c.id, c.name
HAVING COUNT(el.id) > 100
ORDER BY bounce_rate_pct DESC;
```

**Recipients with Repeated Bounces:**
```sql
SELECT
  recipient_email,
  COUNT(*) as bounce_count,
  MAX(bounced_at) as last_bounce,
  array_agg(DISTINCT bounce_reason) as bounce_reasons
FROM email_logs
WHERE status = 'bounced'
  AND bounced_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY recipient_email
HAVING COUNT(*) >= 3
ORDER BY bounce_count DESC;
```

**Engagement Trends:**
```sql
SELECT
  DATE_TRUNC('week', sent_at) as week,
  COUNT(*) as total_sent,
  COUNT(DISTINCT CASE WHEN opened_at IS NOT NULL THEN recipient_email END) as unique_opens,
  COUNT(DISTINCT CASE WHEN clicked_at IS NOT NULL THEN recipient_email END) as unique_clicks,
  ROUND(
    (COUNT(DISTINCT CASE WHEN opened_at IS NOT NULL THEN recipient_email END)::numeric / COUNT(*)::numeric) * 100,
    2
  ) as open_rate_pct,
  ROUND(
    (COUNT(DISTINCT CASE WHEN clicked_at IS NOT NULL THEN recipient_email END)::numeric / COUNT(*)::numeric) * 100,
    2
  ) as click_rate_pct
FROM email_logs
WHERE sent_at >= CURRENT_DATE - INTERVAL '12 weeks'
GROUP BY DATE_TRUNC('week', sent_at)
ORDER BY week DESC;
```

### Common Issues and Solutions

#### Issue: High Bounce Rate

**Symptoms:**
- Bounce rate > 10%
- Many "user unknown" errors
- Old or purchased list

**Solutions:**
1. Immediately stop sending to high-bounce segments
2. Run email validation service on entire list
3. Remove all hard bounces immediately
4. Implement double opt-in for new signups
5. Add CAPTCHA to signup forms (prevents bots)
6. Review list acquisition practices

**Prevention:**
- Regular list cleaning (monthly)
- Email validation at signup
- Remove inactive subscribers (6+ months)

#### Issue: Emails Going to Spam

**Symptoms:**
- Low open rates
- High spam complaint rate
- Gmail/Yahoo blocking

**Solutions:**
1. **Check Authentication:**
   - Verify SPF, DKIM, DMARC all passing
   - Test at mail-tester.com (should score > 8/10)

2. **Review Content:**
   - Remove spam trigger words
   - Improve text-to-image ratio
   - Add plain text version
   - Remove URL shorteners

3. **Sender Reputation:**
   - Check senderscore.org
   - Review Google Postmaster Tools
   - Reduce send volume temporarily
   - Clean list aggressively

4. **List Quality:**
   - Remove unengaged subscribers
   - Segment engaged vs. unengaged
   - Send only to engaged users for 2-4 weeks

#### Issue: Rate Limit Exceeded

**Symptoms:**
- SMTP errors: "421 Too many messages"
- Sending paused unexpectedly
- Connection throttling

**Solutions:**
1. **Immediate:**
   - Reduce EMAIL_RATE_LIMIT_PER_MINUTE by 50%
   - Increase delay between sends
   - Pause campaign for 1 hour

2. **Short-term:**
   - Verify current provider limits
   - Spread sends over more hours
   - Use multiple sending times

3. **Long-term:**
   - Migrate to transactional email service
   - Implement dedicated IP
   - Use multiple sending domains

#### Issue: Low Engagement Rates

**Symptoms:**
- Open rate < 10%
- Click rate < 1%
- Declining trend over time

**Solutions:**
1. **List Segmentation:**
   - Separate engaged from unengaged
   - Create targeted content segments
   - Personalize based on behavior

2. **Content Improvement:**
   - A/B test subject lines
   - Improve preview text
   - Add clear call-to-action
   - Mobile-optimize design

3. **Send Time Optimization:**
   - Test different send times
   - Segment by timezone
   - Track opens by hour sent

4. **Re-engagement Campaign:**
   - Target inactive subscribers
   - Offer special content/incentive
   - Easy resubscribe option
   - Remove permanently inactive after 180 days

#### Issue: SMTP Connection Failures

**Symptoms:**
- "Connection timeout" errors
- "Authentication failed" errors
- Intermittent send failures

**Solutions:**
1. **Verify Credentials:**
   ```bash
   # Test SMTP connection
   telnet smtp.gmail.com 587

   # Or use openssl
   openssl s_client -connect smtp.gmail.com:587 -starttls smtp
   ```

2. **Check Firewall:**
   - Ensure port 587 (or 465) is open
   - Whitelist SMTP server IP
   - Check network security groups (cloud hosting)

3. **Update Authentication:**
   - Regenerate app password (Gmail)
   - Verify 2FA is enabled
   - Check for expired credentials

4. **Connection Pool Settings:**
   ```javascript
   // Adjust pool settings in nodemailer config
   pool: true,
   maxConnections: 5,
   maxMessages: 100,
   rateDelta: 1000,
   rateLimit: 50
   ```

### Performance Optimization

**Database Indexes:**
```sql
-- Speed up email log queries
CREATE INDEX idx_email_logs_sent_at ON email_logs(sent_at);
CREATE INDEX idx_email_logs_status ON email_logs(status);
CREATE INDEX idx_email_logs_campaign_id ON email_logs(campaign_id);
CREATE INDEX idx_email_logs_recipient ON email_logs(recipient_email);

-- Speed up bounce lookups
CREATE INDEX idx_email_logs_bounce_type ON email_logs(bounce_type)
WHERE bounce_type IS NOT NULL;
```

**Queue Management:**
```javascript
// Implement priority queue
const priorityLevels = {
  CRITICAL: 1,    // Password resets, security
  HIGH: 2,        // Transactional emails
  MEDIUM: 3,      // Newsletters
  LOW: 4          // Bulk campaigns
};

// Process higher priority emails first
async function processQueue() {
  const emails = await db.query(`
    SELECT * FROM email_queue
    WHERE status = 'pending'
    ORDER BY priority ASC, created_at ASC
    LIMIT 100
  `);

  // Process batch...
}
```

**Batch Processing Optimization:**
```javascript
// Use Promise.allSettled for parallel processing within batch
async function sendBatch(recipients) {
  const promises = recipients.map(recipient =>
    sendEmail(recipient).catch(error => ({
      status: 'rejected',
      reason: error,
      recipient
    }))
  );

  const results = await Promise.allSettled(promises);

  // Log failures for retry
  const failures = results.filter(r => r.status === 'rejected');
  await queueForRetry(failures);
}
```

---

## References

### Official Documentation

**CAN-SPAM Compliance:**
- FTC CAN-SPAM Compliance Guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- CAN-SPAM Act Full Text: https://www.ftc.gov/legal-library/browse/rules/can-spam-rule
- FTC Enforcement Actions: https://www.ftc.gov/news-events/topics/protecting-consumer-privacy-security/spam

**Gmail/Yahoo Requirements:**
- Google Email Sender Guidelines: https://support.google.com/mail/answer/81126
- Gmail Bulk Sender Guidelines (2024): https://support.google.com/a/answer/81126
- Yahoo Sender Requirements: https://senders.yahooinc.com/best-practices/
- Google Postmaster Tools: https://postmaster.google.com

**Email Authentication:**
- SPF RFC 7208: https://datatracker.ietf.org/doc/html/rfc7208
- DKIM RFC 6376: https://datatracker.ietf.org/doc/html/rfc6376
- DMARC RFC 7489: https://datatracker.ietf.org/doc/html/rfc7489
- DMARC Guide: https://dmarc.org/overview/

**Email Standards:**
- RFC 5321 (SMTP): https://datatracker.ietf.org/doc/html/rfc5321
- RFC 5322 (Email Format): https://datatracker.ietf.org/doc/html/rfc5322
- RFC 8058 (One-Click Unsubscribe): https://datatracker.ietf.org/doc/html/rfc8058

### Testing and Validation Tools

**Email Testing:**
- Mail Tester: https://www.mail-tester.com/
- GlockApps: https://glockapps.com/
- Litmus: https://www.litmus.com/
- Email on Acid: https://www.emailonacid.com/

**DNS and Authentication:**
- MXToolbox: https://mxtoolbox.com/
- DMARC Analyzer: https://www.dmarcanalyzer.com/
- SPF Check: https://mxtoolbox.com/spf.aspx
- DKIM Check: https://mxtoolbox.com/dkim.aspx

**Sender Reputation:**
- Sender Score: https://senderscore.org/
- Talos Intelligence: https://talosintelligence.com/reputation_center
- Barracuda Reputation: https://www.barracudacentral.org/lookups

**Blacklist Checking:**
- MXToolbox Blacklist Check: https://mxtoolbox.com/blacklists.aspx
- MultiRBL: http://multirbl.valli.org/
- SURBL: http://www.surbl.org/surbl-analysis

### SMTP Providers Documentation

**SendGrid:**
- Getting Started: https://docs.sendgrid.com/for-developers/sending-email/getting-started-smtp
- Authentication: https://docs.sendgrid.com/for-developers/sending-email/authentication
- API Documentation: https://docs.sendgrid.com/api-reference

**Mailgun:**
- SMTP Documentation: https://documentation.mailgun.com/en/latest/user_manual.html#sending-via-smtp
- API Reference: https://documentation.mailgun.com/en/latest/api_reference.html
- Email Validation: https://documentation.mailgun.com/en/latest/api-email-validation.html

**Amazon SES:**
- Getting Started: https://docs.aws.amazon.com/ses/latest/dg/send-email-smtp.html
- SMTP Credentials: https://docs.aws.amazon.com/ses/latest/dg/smtp-credentials.html
- Best Practices: https://docs.aws.amazon.com/ses/latest/dg/best-practices.html

**Postmark:**
- SMTP Guide: https://postmarkapp.com/developer/user-guide/send-email-with-smtp
- API Documentation: https://postmarkapp.com/developer/api/overview
- Templates: https://postmarkapp.com/developer/user-guide/templates/overview

### Libraries and Tools

**Node.js Email Libraries:**
- Nodemailer: https://nodemailer.com/
- Email Templates: https://github.com/forwardemail/email-templates
- MJML: https://mjml.io/ (responsive email framework)

**Email Validation:**
- ZeroBounce: https://www.zerobounce.net/
- NeverBounce: https://neverbounce.com/
- Hunter.io: https://hunter.io/email-verifier

**Analytics and Tracking:**
- Google Analytics for Email: https://support.google.com/analytics/answer/1033867
- UTM Parameter Builder: https://ga-dev-tools.google/ga4/campaign-url-builder/

### Industry Best Practices

**Deliverability Resources:**
- Return Path: https://returnpath.com/resources/
- Validity (formerly Return Path): https://www.validity.com/resource-center/
- Mailchimp Email Marketing Guide: https://mailchimp.com/resources/email-marketing-guide/

**Email Design:**
- Really Good Emails: https://reallygoodemails.com/
- Campaign Monitor CSS Guide: https://www.campaignmonitor.com/css/
- Can I Email: https://www.caniemail.com/ (CSS support in email clients)

**Accessibility:**
- WebAIM Email Accessibility: https://webaim.org/techniques/email/
- Litmus Accessibility Guide: https://www.litmus.com/blog/the-ultimate-guide-to-accessible-emails/

### Legal Resources

**Privacy Laws:**
- GDPR Overview: https://gdpr.eu/
- CCPA Information: https://oag.ca.gov/privacy/ccpa
- CASL (Canada): https://crtc.gc.ca/eng/internet/anti.htm

**Compliance Guides:**
- Email Marketing Law Guide: https://www.ftc.gov/business-guidance/resources/email-marketing-law
- International Email Laws: https://www.dma.org.uk/research/gdpr-overview

### Project-Specific Files

**Internal Documentation:**
- `server/config/email.js` - Email configuration
- `server/services/NewsletterService.js` - Newsletter sending logic
- `server/services/EmailService.js` - Core email service
- `server/controllers/newsletterController.js` - Newsletter endpoints

**Database Schema:**
- Email logs table structure
- Subscriber preferences
- Unsubscribe tracking
- Bounce management

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-29 | Development Team | Initial comprehensive documentation |

## Next Review Date

**Scheduled:** 2025-02-29 (Quarterly review)

**Triggers for Earlier Review:**
- New email regulations announced
- Provider requirement changes
- Significant deliverability issues
- Migration to new email service provider

---

## Feedback and Updates

This is a living document. If you encounter:
- Outdated information
- Missing critical details
- Unclear instructions
- New requirements or best practices

Please submit updates via:
1. Create issue in project repository
2. Email development team lead
3. Update during sprint planning sessions

---

**End of Document**
