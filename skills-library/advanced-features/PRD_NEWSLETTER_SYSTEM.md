# Newsletter System PRD

## Overview
Build a newsletter management system with Puck visual editor for creating email campaigns, subscriber management, and delivery tracking.

## Existing Database Schema

### Tables
```sql
-- Subscribers table
newsletter_subscribers (
  id UUID PRIMARY KEY,
  email VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  unsubscribe_token VARCHAR(100) NOT NULL,
  opted_in BOOLEAN DEFAULT true,
  opt_in_date TIMESTAMPTZ,
  opt_out_date TIMESTAMPTZ,
  opt_in_source VARCHAR(100),  -- 'donation', 'signup', 'import'
  frequency newsletter_frequency_enum DEFAULT 'monthly', -- weekly, monthly, quarterly
  preferred_day_of_week INTEGER,
  preferred_time VARCHAR(5),
  donation_id UUID,  -- Link to donor if from donation
  total_emails_sent INTEGER DEFAULT 0,
  total_opens INTEGER DEFAULT 0,
  total_clicks INTEGER DEFAULT 0,
  last_sent_at TIMESTAMPTZ,
  last_opened_at TIMESTAMPTZ,
  last_clicked_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
)

-- Templates/Campaigns table
newsletter_templates (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT false,
  template_type VARCHAR(50),  -- 'promotional', 'weekly', 'monthly', 'announcement'
  puck_config JSONB DEFAULT '{}',  -- Puck editor data
  subject_line VARCHAR(255),
  preheader_text VARCHAR(255),
  organization_name VARCHAR(255),
  organization_address TEXT,
  contact_email VARCHAR(255),
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  created_by UUID,
  last_used_at TIMESTAMPTZ
)

-- Sent newsletters tracking
sent_newsletters (
  id UUID PRIMARY KEY,
  newsletter_template_id UUID NOT NULL,
  subscriber_id UUID NOT NULL,
  recipient_email VARCHAR(255) NOT NULL,
  delivery_status delivery_status_enum DEFAULT 'pending',  -- pending, sent, delivered, failed, bounced
  sent_at TIMESTAMPTZ,
  delivered_at TIMESTAMPTZ,
  failed_reason TEXT,
  retry_count INTEGER DEFAULT 0,
  opened_at TIMESTAMPTZ,
  opened_count INTEGER DEFAULT 0,
  clicked_at TIMESTAMPTZ,
  clicked_count INTEGER DEFAULT 0,
  unsubscribed_at TIMESTAMPTZ,
  bounced_at TIMESTAMPTZ,
  bounce_reason VARCHAR(255),
  campaign_id VARCHAR(100),
  send_batch_id VARCHAR(100),
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
)
```

### Views Available
- `v_active_newsletter_subscribers` - Active subscribers with engagement metrics
- `v_newsletter_engagement_metrics` - Template-level analytics
- `v_newsletter_unsubscribe_audit` - Unsubscribe tracking

## Features to Implement

### 1. Admin Newsletter Pages

#### NewsletterCampaigns.jsx
- List all newsletter templates/campaigns
- Display: name, type, status (draft/published), last sent date, open rate
- Actions: Create new, Edit, Duplicate, Delete, Send
- Filtering by status and type

#### NewsletterEditor.jsx (Puck-based)
- **REFERENCE: client/src/pages/admin/PageEditor.jsx** (working Puck implementation)
- Visual drag-and-drop editor using Puck
- Subject line and preheader text inputs
- Preview mode
- Save as draft / Publish
- Send test email
- Send to subscribers (with options)

#### NewsletterSubscribers.jsx
- List all subscribers with pagination
- Display: email, name, status, frequency, engagement stats
- Actions: Add manual, Import CSV, Export, Edit, Remove
- Filtering by status (opted_in/out), frequency
- Bulk operations

#### NewsletterSettings.jsx
- Default organization info for CAN-SPAM compliance
- Default sender email/name
- Frequency options
- Unsubscribe page customization

### 2. Public Pages

#### NewsletterConfirmed.jsx
- Confirmation page after subscribing
- Display success message

#### NewsletterUnsubscribed.jsx
- Confirmation page after unsubscribing
- Optional feedback form

### 3. Backend API Endpoints

#### Routes: /api/newsletter

**Admin Routes (auth required):**
```
GET    /admin/campaigns          - List all campaigns/templates
POST   /admin/campaigns          - Create new campaign
GET    /admin/campaigns/:id      - Get single campaign
PUT    /admin/campaigns/:id      - Update campaign
DELETE /admin/campaigns/:id      - Delete campaign
POST   /admin/campaigns/:id/send - Send campaign to subscribers
POST   /admin/campaigns/:id/test - Send test email

GET    /admin/subscribers        - List subscribers with filters
POST   /admin/subscribers        - Add subscriber manually
PUT    /admin/subscribers/:id    - Update subscriber
DELETE /admin/subscribers/:id    - Remove subscriber
POST   /admin/subscribers/import - Import from CSV
GET    /admin/subscribers/export - Export to CSV

GET    /admin/analytics          - Newsletter analytics
GET    /admin/settings           - Get settings
PUT    /admin/settings           - Update settings
```

**Public Routes:**
```
POST   /subscribe                - Public subscription form
GET    /confirm/:token           - Confirm subscription
GET    /unsubscribe/:token       - Unsubscribe page
POST   /unsubscribe/:token       - Process unsubscribe
GET    /track/open/:sendId       - Track email open (1x1 pixel)
GET    /track/click/:sendId/:url - Track link click
```

### 4. Newsletter Components (Puck)

**REFERENCE: client/src/components/puck/PuckComponents.jsx**

Create email-safe components with inline styles:

```jsx
// Required components for email newsletters
NewsletterHeader    - Branding, title, preheader
NewsletterFooter    - CAN-SPAM compliant footer with unsubscribe
Text               - Email-safe text with inline styles
Heading            - H1-H4 with inline styles
Image              - Images with alt text, responsive width
Button             - CTA buttons with inline styles
Spacer             - Vertical spacing
Divider            - Horizontal line
TwoColumnLayout    - Table-based two columns for email
Card               - Content card with image, title, description
SocialLinks        - Social media icons/links
PersonalizedGreeting - {{name}} variable support
```

### 5. Services

#### NewsletterService.js
- Campaign CRUD operations
- Subscriber management
- Send logic with batching
- Email rendering (Puck config to HTML)
- Tracking pixel/link generation
- Analytics aggregation

## Technical Requirements

### Puck Integration
- Use same pattern as PageEditor.jsx
- Store config in `puck_config` JSONB column
- Render to email-safe HTML (no CSS classes, inline styles only)

### Email Delivery
- Use existing email config (Resend/SMTP)
- Batch sending to avoid rate limits
- Track delivery status
- Handle bounces

### CAN-SPAM Compliance
- Physical mailing address required
- Clear unsubscribe link
- Honor opt-outs within 10 days
- Accurate sender info

### Personalization
- Support {{name}}, {{email}} variables
- Replace at send time

## File Structure

```
client/src/
  pages/
    admin/
      NewsletterCampaigns.jsx
      NewsletterEditor.jsx
      NewsletterSubscribers.jsx
      NewsletterSettings.jsx
    NewsletterConfirmed.jsx
    NewsletterUnsubscribed.jsx
  components/
    puck/
      NewsletterComponents.jsx    - Email-safe Puck components
      puckNewsletterConfig.jsx    - Puck config for newsletters

server/
  controllers/
    newsletterController.js
  routes/
    newsletterRoutes.js
  services/
    NewsletterService.js
```

## Priority Order

1. Backend API (controller, routes, service)
2. NewsletterCampaigns list page
3. NewsletterEditor with Puck
4. NewsletterSubscribers management
5. Public subscribe/unsubscribe pages
6. Settings page
7. Analytics and tracking
