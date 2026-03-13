# Membership Systems Research Report

**Date**: 2025-11-27
**Purpose**: Research best practices for implementing a membership system in a web application

---

## Table of Contents

1. [WordPress Membership Plugins Analysis](#wordpress-membership-plugins-analysis)
2. [Open Source Projects](#open-source-projects)
3. [Key Features Comparison](#key-features-comparison)
4. [Database Schema Recommendations](#database-schema-recommendations)
5. [Content Protection Methods](#content-protection-methods)
6. [Subscription Management Best Practices](#subscription-management-best-practices)
7. [Analytics and Reporting](#analytics-and-reporting)
8. [Implementation Priorities](#implementation-priorities)

---

## WordPress Membership Plugins Analysis

### 1. MemberPress

**Overview**: Industry-leading WordPress membership plugin with comprehensive features and zero transaction fees.

**Key Features**:
- **Content Restriction**: Restrict pages, posts, categories, tags, custom post types, and files
- **Membership Levels**: Unlimited levels with sophisticated pricing (free trials, graduated pricing, lifetime memberships)
- **Drip Content**: Built-in scheduling without add-ons required
- **Course Builder**: Create lessons with text, video, and quizzes
- **Coaching Integration**: Only membership + coaching plugin for WordPress
- **Paywall**: Display content N times before locking
- **Rules Engine**: Granular content protection with custom registration forms
- **SEO Friendly**: Partial content previews to maintain indexability

**Pricing**:
- Basic: $359/year (1 site) - often discounted to $179.50
- Plus: $599/year (2 sites) + email marketing integrations
- Pro: $799/year (3 sites) + corporate features
- Elite: $999/year (5 sites) + CoachKit

**Strengths**: Most comprehensive feature set, professional support, zero transaction fees

**Sources**:
- [MemberPress Official](https://memberpress.com/)
- [MemberPress Review 2025](https://www.isitwp.com/wordpress-plugins/memberpress/)
- [Features Page](https://memberpress.com/features/)

---

### 2. Restrict Content Pro

**Overview**: Streamlined membership plugin with focus on simplicity and value.

**Key Features**:
- **Content Restriction**: Posts, pages, custom messaging for non-members
- **Drip Content**: Available in paid version
- **Payment Gateways**: PayPal, Stripe, Authorize.net
- **Unified Pricing**: All features for $99/year (no feature gating)
- **Add-ons**: 34 available extensions

**Pricing**:
- 1 Site: $99/year
- 5 Sites: $149/year
- All features included regardless of tier

**Strengths**: Best value, simplified setup, user-friendly interface

**Considerations**: Less extensive than MemberPress but covers core needs

**Sources**:
- [Restrict Content Pro vs Paid Memberships Pro](https://wbcomdesigns.com/restrict-content-pro-vs-paid-memberships-pro/)
- [Pricing](https://restrictcontentpro.com/pricing/)

---

### 3. Paid Memberships Pro

**Overview**: Full-featured platform with extensive add-ons, offers robust free version.

**Key Features**:
- **Core Features**: 22 out of 26 standard membership features
- **Add-ons**: 60+ extensions and integrations
- **Free Version**: Strong free plugin with 33 free add-ons
- **Content Control**: Pages, one-time access, custom post types, drip content
- **Payment Gateways**: PayPal, Stripe, Authorize.net
- **Templating**: Extensive customization for advanced users

**Pricing**:
- Free: Core features + 33 add-ons
- Paid: $347-$597/year
- Plus Plan (most popular): $597/year

**Strengths**: Best free option, highly customizable, extensive ecosystem

**Considerations**: Steeper learning curve, best for advanced users

**Sources**:
- [Paid Memberships Pro vs RCP](https://www.paidmembershipspro.com/pmpro-vs-restrict-content-pro/)
- [Content Controls Documentation](https://www.paidmembershipspro.com/documentation/content-controls/)

---

### 4. LMS

**Overview**: Premium WordPress LMS focused on course delivery with advanced drip features.

**Key Features**:
- **Course Builder**: Drag-and-drop with quizzes, assignments, certificates
- **Drip Content**: Dynamic delivery with prerequisites and learning paths
- **Advanced Dripping**: Calendar dates, days after enrollment, or group-based schedules
- **Focus Mode**: Distraction-free learning environment
- **Video Progression**: Prevent skipping ahead
- **Pricing Models**: One-time, subscriptions, memberships, bundles
- **Payment Gateways**: Stripe, PayPal, WooCommerce (no native membership system)
- **MemberDash Integration**: Adds membership features to LMS

**Drip Features**:
- Release on specific calendar dates
- Days after enrollment
- Group-based scheduling (different groups progress at different rates)
- Multi-tiered dripping (combine LMS + MemberPress for dual schedules)

**Pricing**:
- 1 Site: $199/year
- 10 Sites: $399/year
- Unlimited: $799/year

**Strengths**: Best-in-class course features, sophisticated drip scheduling

**Considerations**: Requires additional plugins for full membership features, no native membership system

**Sources**:
- [LMS Official](https://www.lms.com/)
- [LMS Review](https://www.learningrevolution.net/lms-review-wordpress-lms/)
- [MemberPress Integration](https://memberpress.com/blog/lms-memberpress-integration/)

---

### 5. WooCommerce Memberships

**Overview**: Membership plugin tightly integrated with WooCommerce ecosystem.

**Key Features**:
- **Content Protection**: Pages, posts, custom post types, categories
- **Drip Content**: Delayed access scheduling
- **WooCommerce Integration**: Seamless product/membership management
- **Flexible Models**: Standalone, product purchase, or subscription-based
- **Payment Gateways**: All WooCommerce-supported gateways

**Pricing**: $199/year

**Strengths**: Perfect for existing WooCommerce stores

**Considerations**: Requires WooCommerce Subscriptions add-on for recurring payments

**Sources**:
- [WooCommerce Memberships Review](https://chrislema.com/reviewing-woocommerce-memberships/)

---

### 6. MemberMouse

**Overview**: Revenue-focused membership platform with advanced analytics (serving 18,000+ customers since 2009).

**Key Features**:
- **Core Features**: Unlimited tiers, drip content, member dashboard, SmartTags personalization
- **Analytics**: Advanced revenue metrics (retention, engagement, customer value)
- **1-Click Upsells/Downsells**: Revenue optimization
- **Affiliate Management**: Built-in affiliate system
- **Gifting**: Purchase memberships for others
- **Courses & Quizzes**: Available in higher tiers

**Pricing**:
- Basic: $199.50/year (7 email integrations)
- Plus: $299.50/year (+ quizzes/certificates)
- Pro: $399.50/year (+ priority support)
- Elite: $1,199.50/year (+ Sticky.io integration)

**Strengths**: Best analytics, revenue-focused features

**Considerations**: Not GPL (cannot modify source code)

**Sources**:
- [WordPress Membership Plugins Comparison](https://wpchestnuts.com/best-wordpress-membership-plugins/)

---

### 7. s2Member

**Overview**: Developer-friendly plugin with extensive tools, strong free version.

**Key Features**:
- **Free Version**: 5 membership levels, customizable login/registration, custom fields
- **Content Restriction**: Categories, tags, individual posts/pages, or partial content
- **Developer Tools**: Test site tools, CSS/JS tracking, API tracking
- **Open/Paid Registrations**: Flexible signup models

**Pricing**:
- Free: 5 levels + core features
- Pro (Single): $89 one-time
- Pro (Unlimited): $189 one-time
- Includes lifetime updates + 12 months support

**Strengths**: Best for developers, one-time pricing, extensive free version

**Considerations**: Clunky interface, overwhelming for non-developers, no WooCommerce compatibility

**Sources**:
- [MemberPress vs s2Member vs Ultimate Member](https://wbcomdesigns.com/memberpress-vs-s2member-vs-ultimate-member/)

---

### 8. Ultimate Member

**Overview**: Community-focused plugin with user profiles and directories.

**Key Features**:
- **Community Features**: User profiles, member directories, social login
- **User Registration**: Custom registration forms
- **Profile Privacy**: Users control visibility and directory inclusion
- **Basic Content Protection**: Less advanced than MemberPress/s2Member
- **Payment Integration**: Basic support for payment gateways

**Pricing**: Free with paid add-ons

**Strengths**: Best for community sites, strong profile features

**Considerations**: Weaker on content protection and subscriptions

**Sources**:
- [Ultimate Member Features](https://ultimatemember.com/features/)

---

## Open Source Projects

### Node.js/Express Projects

#### 1. deitch/subscriber
**Repository**: https://github.com/deitch/subscriber

**Features**:
- Subscription tier management (free, regular, pro)
- Request-based restrictions (e.g., 3 clients for free, 10 for regular, 30 for pro)
- Free trial support (14+ days)
- Node.js and Express.js integration

**Use Case**: Control API access based on subscription level

---

#### 2. eddywashere/node-stripe-membership-saas
**Repository**: https://github.com/eddywashere/node-stripe-membership-saas

**Features**:
- Express boilerplate for membership/subscription sites
- Stripe payment integration
- Mailgun email integration
- MongoDB database
- Swig templating

**Use Case**: Full-stack SaaS starter with Stripe

---

#### 3. chimera/membership-app
**Repository**: https://github.com/chimera/membership-app

**Features**:
- Node.js membership application
- Stripe-powered subscriptions
- Heroku-ready deployment
- Uses Stripe Plan metadata (membership = true)

**Use Case**: Simple Stripe-based membership app

---

#### 4. afaraldo/membership-system
**Repository**: https://github.com/afaraldo/membership-system

**Features**:
- Member management (add, update, delete)
- Quota management (monthly, annual, lifetime)
- Payment tracking
- Renewal management with automatic reminders
- Reporting on member activities
- Built with Node.js, Express.js, MongoDB

**Use Case**: Comprehensive membership management for organizations

---

#### 5. pmannle/node-stripe-marketplace-saas
**Repository**: https://github.com/pmannle/node-stripe-marketplace-saas

**Features**:
- Marketplace with Stripe Connected accounts
- Multi-vendor support
- Mailgun, MongoDB, Swig
- Express boilerplate

**Use Case**: Multi-vendor membership marketplace

---

### React/Stripe Projects

#### 1. clerk/use-stripe-subscription
**Repository**: https://github.com/clerk/use-stripe-subscription

**Features**:
- React hooks for Stripe Billing
- Standardized SDK with familiar React patterns
- Uses Stripe Product and Price objects
- One subscription per customer (current limitation)
- No Clerk requirement (despite being sponsored by Clerk)

**Use Case**: Add Stripe billing to React apps quickly

---

#### 2. stripe-samples/subscription-use-cases
**Repository**: https://github.com/stripe-samples/subscription-use-cases

**Features**:
- Official Stripe subscription samples
- Fixed prices and usage-based billing
- React client with react-stripe-js
- Server implementations in 7 languages
- Customer creation and plan subscription

**Use Case**: Reference implementation for Stripe subscriptions

---

#### 3. service-bot/servicebot
**Repository**: https://github.com/service-bot/servicebot

**Features**:
- Open-source subscription management & billing automation
- Service designer linking to Stripe
- Automatic recurring charges
- Quote system for customers
- Free trial support
- Built with Express, React, Redux

**Use Case**: Full subscription management system

---

### Tutorials & Guides

#### GeeksforGeeks: Subscription Management System with Node.js
**Link**: https://www.geeksforgeeks.org/node-js/subscription-management-system-with-nodejs-and-expressjs/

**Features**:
- Step-by-step tutorial
- User authentication with JWT
- MongoDB for users and subscription plans
- Node.js + Express.js

**Use Case**: Learning resource for building from scratch

---

## Key Features Comparison

### Content Restriction

| Feature | Implementation | Best Examples |
|---------|---------------|---------------|
| **Page/Post Restriction** | Restrict entire pages, posts, CPTs | MemberPress, Paid Memberships Pro |
| **Category/Tag Restriction** | Restrict by taxonomy | All major plugins |
| **Partial Content** | Lock portions of content | s2Member, MemberPress |
| **Direct File Protection** | Protect downloads/files | MemberPress |
| **Paywall** | Show content N times before locking | MemberPress |
| **Server-side Protection** | Content hidden at server level (SEO-friendly) | MemberPress, Memberful |
| **Client-side Protection** | Browser-based hiding (faster, less secure) | Various |

---

### Membership Levels/Tiers

| Feature | Implementation | Best Examples |
|---------|---------------|---------------|
| **Unlimited Levels** | No limit on tier count | MemberPress, MemberMouse |
| **Tier Hierarchy** | Cumulative benefits (higher tiers include lower) | All major plugins |
| **Free Tier** | No payment required | Paid Memberships Pro (free core) |
| **Pricing Models** | One-time, recurring, graduated, lifetime | MemberPress, LMS |
| **Custom Registration Forms** | Per-level forms with custom fields | MemberPress, s2Member |

**Recommended Tier Structure**:
- **3 tiers is optimal** (Basic → Standard → Premium)
- Higher tiers should include all lower tier benefits
- Use numerical ranks (1 = highest, 2 = next, etc.)

---

### Drip Content (Time-Released Access)

| Feature | Implementation | Best Examples |
|---------|---------------|---------------|
| **Calendar Date Release** | Specific date unlock | LMS, Thinkific |
| **Days After Enrollment** | Relative to join date | LMS, Restrict Content Pro |
| **Days After Start Date** | Relative to course/product start | Kajabi, LMS |
| **Group-Based Dripping** | Different schedules per group | LMS (via add-on) |
| **Multi-Level Dripping** | Combine membership + course dripping | LMS + MemberPress |
| **Content Prerequisites** | Require completion before access | LMS |

**Implementation Detail**: Most platforms release at midnight UTC on the specified date.

---

### Free Trials & Grace Periods

| Feature | Implementation | Best Examples |
|---------|---------------|---------------|
| **Trial Periods** | 7-30 day free access | Stripe, deitch/subscriber |
| **Trial Reminders** | Email 7 days before trial ends | Stripe (automatic) |
| **Grace Periods** | 3-7 days after failed payment | Stripe dunning |
| **Renewal Reminders** | 1 week before renewal | 53% of customers prefer this |
| **Payment Retries** | Automatic retry schedule (3, 7, 14 days) | Stripe Smart Retries |
| **Dunning Management** | Failed payment recovery workflow | Stripe Billing |

**Best Practice**: 70% of failed payments can be recovered with proper retry logic.

---

### Member Directory

| Feature | Implementation | Best Examples |
|---------|---------------|---------------|
| **Public Profiles** | Searchable member profiles | Ultimate Member, BuddyPress |
| **Profile Privacy** | User-controlled visibility | Ultimate Member, BuddyBoss |
| **Directory Opt-Out** | Hide from member directory | Paid Memberships Pro, Ultimate Member |
| **Search Privileges** | Tier-based search access | Brilliant Directories |
| **Profile Types** | Categorize members (students, teachers, etc.) | BuddyBoss |
| **Social Login** | OAuth integration | Ultimate Member |

---

### Discount Codes

| Feature | Implementation | Best Examples |
|---------|---------------|---------------|
| **Coupon Creation** | Admin-created discount codes | MemberMouse, MemberPress |
| **Percentage/Fixed Discounts** | Flexible discount types | All major plugins |
| **Limited Use** | Single-use or N uses per code | MemberPress |
| **Expiration** | Time-limited codes | All major plugins |
| **Member-Specific** | Codes tied to membership levels | MemberPress |

---

### Analytics & Reporting

| Feature | Implementation | Best Examples |
|---------|---------------|---------------|
| **MRR (Monthly Recurring Revenue)** | Primary KPI for subscriptions | MemberMouse, Stripe |
| **Churn Rate** | Lost customers / total customers × 100 | MemberMouse |
| **Customer Lifetime Value (CLV)** | Total estimated revenue per member | MemberMouse |
| **Retention Metrics** | Track member retention over time | MemberMouse |
| **Trial Conversion Rate** | Trial users → paying customers | Stripe |
| **Net Promoter Score (NPS)** | Customer satisfaction (0-10 scale) | MemberMouse |
| **Engagement Scores** | Member activity tracking | MemberMouse |
| **Real-Time Dashboards** | Live membership statistics | MemberMouse, Recurly |
| **Customizable Reports** | Focus on specific metrics | Association AMS platforms |

**Key Metrics to Track**:
- New sign-ups
- Renewals
- Cancellations
- Revenue trends
- Engagement (logins, content access)
- Payment failures

---

### Payment Gateway Integration

| Gateway | Support Level | Notes |
|---------|--------------|-------|
| **Stripe** | Universal | Most popular, best features |
| **PayPal** | Universal | Widely accepted |
| **Authorize.net** | Common | Enterprise-focused |
| **WooCommerce** | WooCommerce Memberships | All WooCommerce gateways |

---

## Database Schema Recommendations

### Core Principles

1. **Use WordPress Core Tables** (wp_users, wp_usermeta) for compatibility
2. **Avoid Separate User Tables** to maintain plugin integration
3. **Minimize Database Queries** for performance
4. **Follow WordPress Coding Standards** for compatibility

### Recommended Schema Structure

#### Users & Authentication

```sql
-- Use WordPress core tables
wp_users (
  ID bigint(20) unsigned AUTO_INCREMENT PRIMARY KEY,
  user_login varchar(60) NOT NULL,
  user_pass varchar(255) NOT NULL,
  user_email varchar(100) NOT NULL,
  user_registered datetime NOT NULL,
  user_status int(11) NOT NULL DEFAULT 0,
  display_name varchar(250) NOT NULL
)

wp_usermeta (
  umeta_id bigint(20) unsigned AUTO_INCREMENT PRIMARY KEY,
  user_id bigint(20) unsigned NOT NULL,
  meta_key varchar(255),
  meta_value longtext
)
```

#### Membership Tables

```sql
-- Membership Levels/Tiers
CREATE TABLE membership_levels (
  id bigint(20) unsigned AUTO_INCREMENT PRIMARY KEY,
  name varchar(255) NOT NULL,
  description text,
  rank int(11) NOT NULL, -- 1 = highest, 2 = next, etc.
  price decimal(10,2) NOT NULL, -- Use DECIMAL for money, not FLOAT
  billing_period enum('day', 'week', 'month', 'year', 'lifetime') NOT NULL,
  trial_days int(11) DEFAULT 0,
  trial_limit int(11) DEFAULT 0, -- 0 = unlimited trials
  features json, -- Store level-specific features
  created_at datetime NOT NULL,
  updated_at datetime NOT NULL,
  UNIQUE KEY rank (rank)
)

-- User Memberships
CREATE TABLE user_memberships (
  id bigint(20) unsigned AUTO_INCREMENT PRIMARY KEY,
  user_id bigint(20) unsigned NOT NULL,
  membership_level_id bigint(20) unsigned NOT NULL,
  status enum('active', 'pending', 'cancelled', 'expired', 'grace_period') NOT NULL,
  trial_end_date datetime NULL,
  start_date datetime NOT NULL,
  end_date datetime NULL, -- NULL for lifetime
  next_billing_date datetime NULL,
  grace_period_end datetime NULL,
  cancelled_at datetime NULL,
  cancellation_reason text,
  created_at datetime NOT NULL,
  updated_at datetime NOT NULL,
  FOREIGN KEY (user_id) REFERENCES wp_users(ID) ON DELETE CASCADE,
  FOREIGN KEY (membership_level_id) REFERENCES membership_levels(id) ON DELETE RESTRICT,
  INDEX idx_user_status (user_id, status),
  INDEX idx_next_billing (next_billing_date)
)

-- Subscription Transactions (for payment tracking)
CREATE TABLE membership_transactions (
  id bigint(20) unsigned AUTO_INCREMENT PRIMARY KEY,
  user_membership_id bigint(20) unsigned NOT NULL,
  amount decimal(10,2) NOT NULL,
  currency varchar(3) NOT NULL DEFAULT 'USD',
  gateway enum('stripe', 'paypal', 'authorize_net', 'manual') NOT NULL,
  gateway_transaction_id varchar(255),
  status enum('pending', 'completed', 'failed', 'refunded') NOT NULL,
  type enum('charge', 'refund', 'renewal', 'trial') NOT NULL,
  created_at datetime NOT NULL,
  FOREIGN KEY (user_membership_id) REFERENCES user_memberships(id) ON DELETE CASCADE,
  INDEX idx_gateway_txn (gateway, gateway_transaction_id),
  INDEX idx_status_date (status, created_at)
)
```

#### Content Restriction

```sql
-- Content Access Rules
CREATE TABLE content_rules (
  id bigint(20) unsigned AUTO_INCREMENT PRIMARY KEY,
  rule_type enum('post', 'page', 'category', 'tag', 'custom_post_type', 'file') NOT NULL,
  object_id bigint(20) unsigned, -- Post ID, Term ID, etc.
  object_type varchar(50), -- 'post', 'page', 'course', etc.
  required_level_id bigint(20) unsigned NULL, -- NULL = any member
  drip_days int(11) DEFAULT 0, -- Days after enrollment to unlock
  drip_date datetime NULL, -- Specific unlock date
  created_at datetime NOT NULL,
  updated_at datetime NOT NULL,
  FOREIGN KEY (required_level_id) REFERENCES membership_levels(id) ON DELETE SET NULL,
  INDEX idx_rule_type_object (rule_type, object_id)
)

-- User Content Access Log (for analytics)
CREATE TABLE user_content_access (
  id bigint(20) unsigned AUTO_INCREMENT PRIMARY KEY,
  user_id bigint(20) unsigned NOT NULL,
  content_rule_id bigint(20) unsigned NOT NULL,
  access_date datetime NOT NULL,
  FOREIGN KEY (user_id) REFERENCES wp_users(ID) ON DELETE CASCADE,
  FOREIGN KEY (content_rule_id) REFERENCES content_rules(id) ON DELETE CASCADE,
  INDEX idx_user_date (user_id, access_date),
  INDEX idx_content_date (content_rule_id, access_date)
)
```

#### Drip Content Scheduling

```sql
-- Drip Schedule
CREATE TABLE drip_schedules (
  id bigint(20) unsigned AUTO_INCREMENT PRIMARY KEY,
  content_rule_id bigint(20) unsigned NOT NULL,
  schedule_type enum('days_after_enrollment', 'calendar_date', 'days_after_start', 'prerequisite') NOT NULL,
  delay_days int(11) DEFAULT 0, -- For relative schedules
  release_date datetime NULL, -- For calendar schedules
  prerequisite_rule_id bigint(20) unsigned NULL, -- For prerequisite-based
  created_at datetime NOT NULL,
  updated_at datetime NOT NULL,
  FOREIGN KEY (content_rule_id) REFERENCES content_rules(id) ON DELETE CASCADE,
  FOREIGN KEY (prerequisite_rule_id) REFERENCES content_rules(id) ON DELETE CASCADE
)

-- User Drip Progress (track what's unlocked)
CREATE TABLE user_drip_progress (
  id bigint(20) unsigned AUTO_INCREMENT PRIMARY KEY,
  user_id bigint(20) unsigned NOT NULL,
  drip_schedule_id bigint(20) unsigned NOT NULL,
  unlocked_at datetime NULL, -- NULL = not yet unlocked
  FOREIGN KEY (user_id) REFERENCES wp_users(ID) ON DELETE CASCADE,
  FOREIGN KEY (drip_schedule_id) REFERENCES drip_schedules(id) ON DELETE CASCADE,
  UNIQUE KEY user_drip (user_id, drip_schedule_id),
  INDEX idx_user_unlocked (user_id, unlocked_at)
)
```

#### Discount Codes

```sql
-- Coupons/Discount Codes
CREATE TABLE membership_coupons (
  id bigint(20) unsigned AUTO_INCREMENT PRIMARY KEY,
  code varchar(50) NOT NULL UNIQUE,
  description text,
  discount_type enum('percentage', 'fixed_amount') NOT NULL,
  discount_value decimal(10,2) NOT NULL,
  applicable_levels json, -- Array of level IDs, NULL = all levels
  max_uses int(11) DEFAULT 0, -- 0 = unlimited
  current_uses int(11) DEFAULT 0,
  valid_from datetime NULL,
  valid_until datetime NULL,
  created_at datetime NOT NULL,
  updated_at datetime NOT NULL,
  INDEX idx_code_valid (code, valid_until)
)

-- Coupon Usage Tracking
CREATE TABLE coupon_usage (
  id bigint(20) unsigned AUTO_INCREMENT PRIMARY KEY,
  coupon_id bigint(20) unsigned NOT NULL,
  user_id bigint(20) unsigned NOT NULL,
  user_membership_id bigint(20) unsigned NOT NULL,
  used_at datetime NOT NULL,
  FOREIGN KEY (coupon_id) REFERENCES membership_coupons(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES wp_users(ID) ON DELETE CASCADE,
  FOREIGN KEY (user_membership_id) REFERENCES user_memberships(id) ON DELETE CASCADE
)
```

#### Member Directory

```sql
-- Member Profiles (extends wp_users)
CREATE TABLE member_profiles (
  id bigint(20) unsigned AUTO_INCREMENT PRIMARY KEY,
  user_id bigint(20) unsigned NOT NULL UNIQUE,
  bio text,
  avatar_url varchar(255),
  profile_visibility enum('public', 'members_only', 'private') NOT NULL DEFAULT 'public',
  show_in_directory boolean NOT NULL DEFAULT true,
  profile_type varchar(50), -- 'student', 'teacher', 'admin', etc.
  social_links json, -- {twitter, linkedin, website, etc.}
  custom_fields json, -- Extensible custom data
  created_at datetime NOT NULL,
  updated_at datetime NOT NULL,
  FOREIGN KEY (user_id) REFERENCES wp_users(ID) ON DELETE CASCADE,
  INDEX idx_visibility_directory (profile_visibility, show_in_directory)
)
```

#### Reminders & Notifications

```sql
-- Email Reminders/Notifications
CREATE TABLE membership_notifications (
  id bigint(20) unsigned AUTO_INCREMENT PRIMARY KEY,
  user_id bigint(20) unsigned NOT NULL,
  notification_type enum('trial_ending', 'renewal_reminder', 'payment_failed', 'grace_period', 'content_unlocked') NOT NULL,
  scheduled_for datetime NOT NULL,
  sent_at datetime NULL,
  status enum('pending', 'sent', 'failed') NOT NULL DEFAULT 'pending',
  metadata json, -- Additional context (amount, level, etc.)
  created_at datetime NOT NULL,
  FOREIGN KEY (user_id) REFERENCES wp_users(ID) ON DELETE CASCADE,
  INDEX idx_scheduled_status (scheduled_for, status)
)
```

### Naming Conventions

- **Tables**: Use `{prefix}_{table_name}` pattern (e.g., `membership_levels`)
- **Constraints/Indexes**: Use `{tablename}_{columnname(s)}_{suffix}` (e.g., `idx_user_status`)
- **Money Fields**: Always use `DECIMAL(10,2)`, never `FLOAT`

### Relationships

- **One-to-Many**: User → Memberships (foreign key)
- **Many-to-Many**: Memberships ↔ Content Rules (via junction table if needed)
- **Self-Referential**: Prerequisite content rules

### Performance Optimizations

1. **Index frequently queried columns**: user_id, status, dates
2. **Composite indexes**: (user_id, status), (status, created_at)
3. **JSON columns**: For flexible, extensible data (features, metadata)
4. **Cascading deletes**: ON DELETE CASCADE for dependent data
5. **Archive old data**: Move expired/cancelled memberships to archive tables

---

## Content Protection Methods

### Server-Side Protection (Recommended)

**How It Works**: Decision made at server before sending to browser.

**Advantages**:
- Highest security (content never sent to unauthorized users)
- Cannot be bypassed by browser tools

**Disadvantages**:
- SEO challenges (search engines can't index protected content)

**Solution**: Allow partial content or meta tags for SEO

**Best Implementations**: MemberPress, Memberful

---

### Client-Side Protection

**How It Works**: Content sent to browser, then hidden via JavaScript.

**Advantages**:
- Faster implementation
- Better for SEO (content in HTML)

**Disadvantages**:
- Less secure (users can bypass with browser tools)
- Vulnerable to paywall evasion

**Best For**: Low-security content, paywalls

---

### Hybrid/Metered Paywalls

**How It Works**: Allow N free views, then require subscription.

**Example**: New York Times (20 articles/month free)

**Implementation**:
- Track views via cookies (basic)
- Device fingerprinting (advanced)
- Account-based tracking (most secure)

**Challenges**:
- Incognito mode (26.7% of users use weekly)
- Cookie clearing
- VPNs and device switching

**Solutions**:
- Device fingerprinting (OS, browser, hardware)
- IP tracking
- Account-based limits

---

### Protection Techniques

| Technique | Description | Security Level |
|-----------|-------------|----------------|
| **Single Session** | Only one login at a time | Medium |
| **Device Monitoring** | Track and limit devices | High |
| **Account Lockout** | Lock after N failed logins | Medium |
| **Direct URL Protection** | Require auth for file URLs | High |
| **Server-Side Delivery** | Content only after auth check | Highest |

---

## Subscription Management Best Practices

### Renewal Reminders

**Timing**:
- **7 days before renewal**: Preferred by 53% of customers
- **Trial ending**: Reminder sent 7 days before (or immediately if trial < 7 days)

**Best Practices**:
- Personalize messages (mention expiring cards, plan details)
- Multiple reminders (not too many to annoy)
- Include action items (update payment, upgrade plan)

**Implementation**: Stripe Billing handles this automatically

---

### Grace Periods

**Recommended Duration**: 3-7 days after failed payment

**Benefits**:
- Reduces churn (customers can fix payment issues)
- Maintains access during resolution
- Shows empathy

**Implementation**:
1. Set subscription status to "grace_period"
2. Continue access during grace period
3. Send reminders to update payment
4. Retry payment automatically
5. Cancel only after grace period expires

---

### Dunning Management

**Definition**: System to collect accounts receivable (failed payments)

**Components**:
1. **Automated Retries**: Attempt payment multiple times
2. **Customer Reminders**: Email notifications of failures
3. **Grace Periods**: Allow time to fix issues

**Retry Schedule**:
- Immediate retry
- 3 days later
- 7 days later
- 14 days later

**Success Rate**: 70% of failed payments can be recovered with retries

**Stripe Stats**: Smart Retries helped recover $6.5B in revenue (2024)

---

### Failed Payment Recovery

**Statistics**:
- 15% of recurring payments fail on first attempt
- 80% can be recovered within a week with retries

**Best Practices**:
1. **Immediate retry**: Sometimes temporary issues resolve quickly
2. **Scheduled retries**: 3, 7, 14 day intervals
3. **Customer communication**: Notify of failure, provide resolution steps
4. **Update card prompts**: Make it easy to update payment method
5. **Grace period**: Don't cut access immediately

---

### Trial Periods

**Common Durations**: 7, 14, or 30 days

**Implementation**:
- Set `trial_end_date` in user_memberships
- Grant full or limited access during trial
- Send reminder 7 days before trial ends
- Auto-convert to paid or cancel at trial end

**Best Practice**: Track trial conversion rate (trial users → paying customers)

---

## Analytics and Reporting

### Essential KPIs

#### Financial Metrics

1. **Monthly Recurring Revenue (MRR)**: Primary metric for subscription businesses
2. **Customer Lifetime Value (CLV)**: Total estimated revenue per member
3. **Average Revenue Per User (ARPU)**: Total revenue / total users
4. **Revenue Churn**: Lost revenue from cancellations

#### Retention & Growth

1. **Churn Rate**: (Lost customers / Total customers) × 100
2. **Retention Rate**: (Retained customers / Total customers) × 100
3. **Member Growth**: New sign-ups over time
4. **Trial Conversion Rate**: Trial users who become paying customers

#### Engagement

1. **Active Users**: Daily/Weekly/Monthly active users
2. **Content Access**: Which content is most viewed
3. **Login Frequency**: How often members log in
4. **Feature Usage**: Which features are most used

#### Satisfaction

1. **Net Promoter Score (NPS)**: Likelihood to recommend (0-10 scale)
2. **Customer Satisfaction (CSAT)**: Overall satisfaction rating
3. **Support Tickets**: Volume and resolution time

---

### Dashboard Features

**Real-Time Monitoring**:
- New sign-ups
- Cancellations
- Failed payments
- Revenue

**Customizable Reports**:
- Filter by date range, membership level, status
- Export to CSV/PDF
- Scheduled email reports

**Visual Analytics**:
- Charts (line, bar, pie)
- Trends over time
- Cohort analysis

**Centralized Data Access**:
- Single dashboard for all metrics
- Drill-down to granular details
- Historical comparisons

---

### Best Practices

1. **Focus on Few KPIs**: Track 3-5 most important metrics
2. **Set Clear Goals**: Define targets for each KPI
3. **User-Friendly Design**: Avoid clutter, prioritize clarity
4. **Automate Tracking**: Use AMS or analytics platform
5. **Regular Review**: Weekly/monthly metric reviews
6. **Actionable Insights**: Use data to drive decisions

---

## Implementation Priorities

### Phase 1: Core Membership Features (MVP)

**Priority**: Critical for launch

1. **User Authentication**
   - Registration/login (use WordPress core or custom)
   - Password reset
   - Email verification

2. **Membership Levels**
   - Create 3 tiers (Free, Standard, Premium)
   - Define pricing and features
   - Set tier hierarchy (cumulative benefits)

3. **Payment Integration**
   - Stripe integration (recommended)
   - One-time and recurring payments
   - Basic checkout flow

4. **Content Restriction**
   - Restrict pages/posts by membership level
   - Basic access control
   - Non-member messaging

5. **User Dashboard**
   - View current membership
   - Manage subscription (cancel, upgrade)
   - Payment history

---

### Phase 2: Enhanced Features

**Priority**: Important for retention

1. **Drip Content**
   - Days after enrollment scheduling
   - Calendar date scheduling
   - Track user progress

2. **Free Trials**
   - 7-14 day trials for paid tiers
   - Trial end reminders
   - Auto-conversion or cancellation

3. **Grace Periods**
   - 3-7 day grace after failed payment
   - Payment retry logic (3, 7, 14 days)
   - Grace period notifications

4. **Email Notifications**
   - Welcome emails
   - Renewal reminders (7 days before)
   - Payment failure alerts
   - Trial ending notifications

5. **Basic Analytics**
   - MRR tracking
   - Churn rate
   - New sign-ups
   - Active members

---

### Phase 3: Advanced Features

**Priority**: Nice-to-have for growth

1. **Discount Codes**
   - Percentage and fixed-amount coupons
   - Expiration dates
   - Usage limits

2. **Member Directory**
   - Public member profiles
   - Privacy controls
   - Directory opt-out

3. **Advanced Drip Content**
   - Prerequisite-based unlocking
   - Group-based schedules
   - Multi-level dripping

4. **Advanced Analytics Dashboard**
   - CLV calculation
   - Retention cohorts
   - Content engagement
   - Visual charts and graphs

5. **Affiliate/Referral System**
   - Referral tracking
   - Commission calculation
   - Affiliate dashboard

---

### Phase 4: Premium Features

**Priority**: Optional for enterprise/scale

1. **1-Click Upsells/Downsells**
   - Offer upgrades during checkout
   - Downgrade options for canceling users

2. **Gifting**
   - Purchase memberships for others
   - Gift codes

3. **Course Integration**
   - LMS features (lessons, quizzes, certificates)
   - Progress tracking
   - Gradebook

4. **API Access**
   - RESTful API for integrations
   - Webhooks for events
   - Third-party integrations

5. **White-Label Options**
   - Custom branding
   - Remove platform branding
   - Custom domain

---

## Technology Stack Recommendations

### For MERN Stack (Your Current Project)

**Frontend**:
- React for UI
- React Router for navigation
- Stripe Elements for payment forms
- Chart.js or Recharts for analytics

**Backend**:
- Node.js + Express
- MongoDB for database
- Stripe API for payments
- Nodemailer for emails
- Node-cron for scheduled tasks (reminders, renewals)

**Authentication**:
- JWT tokens
- Passport.js (optional)
- bcrypt for password hashing

**Recommended GitHub Projects**:
1. **eddywashere/node-stripe-membership-saas**: Best full-stack starter
2. **afaraldo/membership-system**: Good for membership management logic
3. **clerk/use-stripe-subscription**: React hooks for Stripe
4. **stripe-samples/subscription-use-cases**: Official Stripe examples

---

### Database Choice for MERN

**MongoDB Schema** (NoSQL approach):

```javascript
// users collection (use existing or create)
{
  _id: ObjectId,
  email: String,
  password: String (hashed),
  createdAt: Date
}

// membershipLevels collection
{
  _id: ObjectId,
  name: String,
  rank: Number,
  price: Number,
  billingPeriod: String, // 'month', 'year', 'lifetime'
  trialDays: Number,
  features: [String],
  createdAt: Date
}

// userMemberships collection
{
  _id: ObjectId,
  userId: ObjectId,
  membershipLevelId: ObjectId,
  status: String, // 'active', 'cancelled', 'expired', 'grace_period'
  stripeCustomerId: String,
  stripeSubscriptionId: String,
  trialEndDate: Date,
  startDate: Date,
  endDate: Date,
  nextBillingDate: Date,
  gracePeriodEnd: Date,
  createdAt: Date,
  updatedAt: Date
}

// contentRules collection
{
  _id: ObjectId,
  contentType: String, // 'course', 'lesson', 'file', etc.
  contentId: ObjectId,
  requiredLevelId: ObjectId,
  dripDays: Number, // 0 = immediate access
  dripDate: Date, // null = use dripDays
  createdAt: Date
}

// transactions collection
{
  _id: ObjectId,
  userMembershipId: ObjectId,
  amount: Number,
  currency: String,
  gateway: String, // 'stripe'
  gatewayTransactionId: String,
  status: String, // 'completed', 'failed', 'refunded'
  type: String, // 'charge', 'refund', 'renewal'
  createdAt: Date
}
```

---

## Key Takeaways

### Top Features to Implement

1. **Content Restriction**: Server-side protection for security
2. **Tiered Memberships**: 3 levels with cumulative benefits
3. **Stripe Integration**: Best payment gateway for subscriptions
4. **Drip Content**: Days after enrollment scheduling
5. **Free Trials**: 7-14 days to reduce friction
6. **Grace Periods**: 3-7 days after failed payment
7. **Email Notifications**: Automate reminders and alerts
8. **Basic Analytics**: MRR, churn, new sign-ups
9. **Member Dashboard**: Self-service subscription management
10. **Discount Codes**: Marketing and promotional tool

---

### Recommended Architecture

**Membership System**:
- Node.js + Express backend
- MongoDB database
- Stripe for payments
- React frontend
- JWT authentication

**Content Protection**:
- Middleware to check membership status
- Server-side access control
- Partial content for SEO

**Subscription Management**:
- Stripe webhooks for events (payment_succeeded, payment_failed, etc.)
- Cron jobs for reminders and renewals
- Grace period logic

**Analytics**:
- Aggregate queries for metrics
- Dashboard with charts
- Export to CSV

---

### GitHub Repos Worth Examining

**Full-Stack Starters**:
1. [eddywashere/node-stripe-membership-saas](https://github.com/eddywashere/node-stripe-membership-saas) - Express + Stripe boilerplate
2. [service-bot/servicebot](https://github.com/service-bot/servicebot) - Full subscription management system

**Membership Logic**:
3. [afaraldo/membership-system](https://github.com/afaraldo/membership-system) - Membership management with renewals
4. [deitch/subscriber](https://github.com/deitch/subscriber) - Subscription tier control

**React + Stripe**:
5. [clerk/use-stripe-subscription](https://github.com/clerk/use-stripe-subscription) - React hooks for Stripe
6. [stripe-samples/subscription-use-cases](https://github.com/stripe-samples/subscription-use-cases) - Official Stripe examples

**Database Schema**:
7. [membership/membership.db](https://github.com/membership/membership.db) - SQL schema for user accounts and roles

---

## Sources

### WordPress Membership Plugins
- [MemberPress Official](https://memberpress.com/)
- [MemberPress Review 2025](https://www.isitwp.com/wordpress-plugins/memberpress/)
- [MemberPress Features](https://memberpress.com/features/)
- [MemberPress vs Competitors](https://oddjar.com/wordpress-membership-plugins-2025-memberpress-vs-restrict-content-pro-vs-paid-memberships-pro/)
- [Restrict Content Pro vs Paid Memberships Pro](https://wbcomdesigns.com/restrict-content-pro-vs-paid-memberships-pro/)
- [Paid Memberships Pro Official](https://www.paidmembershipspro.com/pmpro-vs-restrict-content-pro/)
- [LMS Official](https://www.lms.com/)
- [LMS Review](https://www.learningrevolution.net/lms-review-wordpress-lms/)
- [MemberPress + LMS Integration](https://memberpress.com/blog/lms-memberpress-integration/)
- [WooCommerce Memberships Review](https://chrislema.com/reviewing-woocommerce-memberships/)
- [WordPress Membership Plugins Compared](https://wpchestnuts.com/best-wordpress-membership-plugins/)
- [MemberPress vs s2Member vs Ultimate Member](https://wbcomdesigns.com/memberpress-vs-s2member-vs-ultimate-member/)
- [Ultimate Member Features](https://ultimatemember.com/features/)

### Open Source Projects
- [deitch/subscriber](https://github.com/deitch/subscriber)
- [eddywashere/node-stripe-membership-saas](https://github.com/eddywashere/node-stripe-membership-saas)
- [chimera/membership-app](https://github.com/chimera/membership-app)
- [afaraldo/membership-system](https://github.com/afaraldo/membership-system)
- [pmannle/node-stripe-marketplace-saas](https://github.com/pmannle/node-stripe-marketplace-saas)
- [clerk/use-stripe-subscription](https://github.com/clerk/use-stripe-subscription)
- [stripe-samples/subscription-use-cases](https://github.com/stripe-samples/subscription-use-cases)
- [service-bot/servicebot](https://github.com/service-bot/servicebot)
- [GeeksforGeeks Node.js Subscription Tutorial](https://www.geeksforgeeks.org/node-js/subscription-management-system-with-nodejs-and-expressjs/)

### Database Design
- [membership/membership.db](https://github.com/membership/membership.db)
- [Stack Overflow: Relational Database Design Patterns](https://stackoverflow.com/questions/145689/relational-database-design-patterns)
- [Stack Overflow: Membership Payment Schema](https://stackoverflow.com/questions/843748/is-this-good-membership-payment-database-schema)
- [WordPress Database Schema Guide](https://blogvault.net/wordpress-database-schema/)
- [WordPress Simple Membership Development](https://codecanel.com/wordpress-simple-membership-plugins-development/)

### Content Protection
- [How Paywalls Work](https://fingerprint.com/blog/how-paywalls-work-paywall-protection-tutorial/)
- [What is a Paywall?](https://memberful.com/blog/paywall/)
- [Subscription Paywall Integration](https://apiko-software.medium.com/subscription-management-system-integration-what-is-paywall-and-how-does-it-work-for-media-e6dc5486703b)
- [MemberPress Paywall Tutorial](https://memberpress.com/blog/paywall-your-blog/)
- [Protect Content in MemberPress](https://temydeedigital.com/blog/protect-content-in-memberpress/)

### Subscription Management
- [Stripe Subscriptions Overview](https://docs.stripe.com/billing/subscriptions/overview)
- [Stripe Passive Churn Prevention](https://stripe.com/resources/more/passive-churn-101-what-it-is-why-it-happens-and-eight-ways-to-prevent-it)
- [Stripe Trial Periods](https://docs.stripe.com/billing/subscriptions/trials)
- [Stripe Expired Cards](https://stripe.com/resources/more/expired-cards-for-recurring-payments)
- [Stripe Subscription Management](https://stripe.com/resources/more/subscription-management-features-explained-and-how-to-choose-a-software-solution)
- [Stripe Billing](https://stripe.com/billing)
- [Stripe Subscription Changes Best Practices](https://moldstud.com/articles/p-how-to-effectively-manage-subscription-changes-in-stripe-and-avoid-common-pitfalls)

### Analytics & Reporting
- [Membership Analytics Tools](https://www.strikingly.com/blog/posts/unlock-insights-top-6-membership-analytics-tools)
- [Kajabi Membership Analytics](https://kajabi.com/blog/membership-analytics-pay-attention)
- [KPI Dashboards for Associations](https://www.glueup.com/blog/customizable-kpi-dashboard)
- [29 KPIs for Membership Organizations](https://memberclicks.com/blog/kpis-for-membership-organizations/)
- [Subscription Billing KPIs](https://www.inetsoft.com/info/subscription-billing-kpi-dashboard-analytics/)
- [Recurly Analytics](https://recurly.com/product/reporting-analytics/)

### Membership Tiers & Drip Content
- [Membership Tiers Guide](https://www.group.app/blog/membership-tiers/)
- [Naming Membership Tiers 2025](https://blog.membership.io/naming-your-membership-tiers-a-2025-guide)
- [How to Name Membership Levels](https://profilepress.com/how-to-name-membership-levels-tiers/)
- [Drip Schedule - Thinkific](https://support.thinkific.com/hc/en-us/articles/360030741033-Drip-Schedule)
- [Drip Content - Teachable](https://support.teachable.com/hc/en-us/articles/219827227-Drip-Content)
- [Drip Content - Restrict Content Pro](https://restrictcontentpro.com/add-on/drip-content/)
- [Kajabi Drip Content](https://help.kajabi.com/hc/en-us/articles/360037694933-How-to-Use-Drip-Content-to-Release-Product-Lessons-Over-Time)

### Member Directory & Privacy
- [BuddyPress Profile Visibility Manager](https://buddydev.com/plugins/bp-profile-visibility-manager/)
- [BuddyBoss Member Visibility](https://www.buddyboss.com/docs/how-to-manage-user-visibility-in-the-members-directory-network-search-by-profile-type-in-buddyboss-platform/)
- [Paid Memberships Pro Directory Visibility](https://www.paidmembershipspro.com/documentation/add-on-docs/pmpro-member-directory/control-visibility/)
- [Brilliant Directories Hidden Profiles](https://www.brilliantdirectories.com/blog/hidden-member-profiles-plugin-website-member-privacy-search-controls)
- [Ultimate Member Privacy](https://docs.ultimatemember.com/article/40-account-tab)
- [MembershipWorks Privacy](https://membershipworks.com/data-privacy-security/)

---

**End of Report**
