# PRD: Newsletter Template System with Puck Visual Editor

## Overview

Build a visual newsletter editor using the Puck library that allows administrators to create and edit email newsletter templates with a drag-and-drop interface. All components must render email-safe HTML with inline styles only.

## Goals

1. Provide an intuitive visual editor for creating email newsletters
2. Generate email-compatible HTML (inline styles, table-based layouts)
3. Support CAN-SPAM compliance requirements
4. Enable template reuse and personalization
5. Integrate with existing newsletter subscriber system

## Database Schema (Existing)

### newsletter_templates
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Template name |
| description | TEXT | Template description |
| is_active | BOOLEAN | Active status |
| template_type | VARCHAR(50) | Type classification |
| puck_config | JSONB | Puck editor configuration |
| subject_line | VARCHAR(255) | Email subject |
| preheader_text | VARCHAR(255) | Preview text |
| organization_name | VARCHAR(255) | Org name for footer |
| organization_address | TEXT | Physical address (CAN-SPAM) |
| contact_email | VARCHAR(255) | Contact email |
| created_at | TIMESTAMPTZ | Creation timestamp |
| updated_at | TIMESTAMPTZ | Last update timestamp |
| created_by | UUID | User who created |
| last_used_at | TIMESTAMPTZ | Last time used |

### newsletter_subscribers
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| email | VARCHAR(255) | Subscriber email |
| name | VARCHAR(255) | Subscriber name |
| unsubscribe_token | VARCHAR(100) | Unique unsubscribe token |
| opted_in | BOOLEAN | Subscription status |
| opt_in_date | TIMESTAMPTZ | When subscribed |
| opt_out_date | TIMESTAMPTZ | When unsubscribed |
| opt_in_source | VARCHAR(100) | How they subscribed |
| frequency | ENUM | weekly/monthly/quarterly |
| total_emails_sent | INTEGER | Delivery count |
| total_opens | INTEGER | Open count |
| total_clicks | INTEGER | Click count |

### sent_newsletters
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| newsletter_template_id | UUID | FK to templates |
| subscriber_id | UUID | FK to subscribers |
| recipient_email | VARCHAR(255) | Recipient email |
| delivery_status | ENUM | pending/sent/delivered/failed |
| sent_at | TIMESTAMPTZ | When sent |
| opened_at | TIMESTAMPTZ | First open time |
| clicked_at | TIMESTAMPTZ | First click time |
| unsubscribed_at | TIMESTAMPTZ | If unsubscribed via this email |
| campaign_id | VARCHAR(100) | Campaign identifier |
| send_batch_id | VARCHAR(100) | Batch identifier |

## Puck Component Architecture

### Implementation Pattern (Follow Existing puckConfig.jsx)

```javascript
// puckNewsletterConfig.jsx
import * as Components from './NewsletterComponents';

export const puckNewsletterConfig = {
  components: {
    ComponentName: {
      render: Components.ComponentName,  // Direct reference to component
      fields: {
        fieldName: { type: 'text', label: 'Label' }
      },
      defaultProps: {
        fieldName: 'default value'
      }
    }
  }
};
```

### Email-Safe Component Requirements

1. **Table-based layouts** - No CSS Grid/Flexbox (limited email client support)
2. **Inline styles only** - No external CSS classes
3. **Max width 600px** - Standard email width
4. **Web-safe fonts** - Arial, Georgia, Times New Roman, Verdana
5. **No JavaScript** - Static HTML only
6. **Alt text on images** - Accessibility requirement
7. **Absolute URLs** - All links must be absolute

## Component Specifications

### 1. EmailHeader
Email header with organization branding.

**Fields:**
- `logoUrl` (custom/ImageFieldComponent) - Organization logo
- `organizationName` (text) - Fallback text if no logo
- `headerTitle` (text) - Newsletter title
- `preheaderText` (text) - Preview text (hidden)
- `backgroundColor` (text) - Header background color

**Default Props:**
```javascript
{
  logoUrl: '',
  organizationName: 'School of the Priests',
  headerTitle: 'Monthly Newsletter',
  preheaderText: '',
  backgroundColor: '#f8f9fa'
}
```

### 2. EmailFooter
CAN-SPAM compliant footer.

**Fields:**
- `organizationName` (text) - Organization name
- `physicalAddress` (textarea) - Physical address (REQUIRED for CAN-SPAM)
- `contactEmail` (text) - Contact email
- `copyrightText` (text) - Copyright notice

**Default Props:**
```javascript
{
  organizationName: 'School of the Priests',
  physicalAddress: '123 Main St, City, State 12345',
  contactEmail: 'contact@example.com',
  copyrightText: '2024 All rights reserved'
}
```

### 3. TextBlock
Basic paragraph text.

**Fields:**
- `content` (textarea) - Text content
- `fontSize` (select) - 12px, 14px, 16px, 18px
- `color` (text) - Text color hex
- `alignment` (select) - left, center, right
- `fontWeight` (select) - normal, bold

**Default Props:**
```javascript
{
  content: 'Enter your text here...',
  fontSize: '16px',
  color: '#374151',
  alignment: 'left',
  fontWeight: 'normal'
}
```

### 4. HeadingBlock
Section headings.

**Fields:**
- `text` (text) - Heading text
- `level` (select) - h1, h2, h3, h4
- `color` (text) - Text color
- `alignment` (select) - left, center, right

**Default Props:**
```javascript
{
  text: 'Section Heading',
  level: 'h2',
  color: '#1f2937',
  alignment: 'left'
}
```

### 5. ImageBlock
Responsive image with optional link.

**Fields:**
- `src` (custom/ImageFieldComponent) - Image URL
- `alt` (text) - Alt text
- `width` (select) - 100%, 75%, 50%
- `alignment` (select) - left, center, right
- `linkUrl` (text) - Optional link

**Default Props:**
```javascript
{
  src: '',
  alt: 'Image',
  width: '100%',
  alignment: 'center',
  linkUrl: ''
}
```

### 6. ButtonBlock
Call-to-action button.

**Fields:**
- `text` (text) - Button text
- `linkUrl` (text) - Button link
- `backgroundColor` (text) - Button background color
- `textColor` (text) - Button text color
- `alignment` (select) - left, center, right
- `fullWidth` (radio) - true/false

**Default Props:**
```javascript
{
  text: 'Learn More',
  linkUrl: '#',
  backgroundColor: '#2563eb',
  textColor: '#ffffff',
  alignment: 'center',
  fullWidth: false
}
```

### 7. DividerBlock
Horizontal separator line.

**Fields:**
- `color` (text) - Line color
- `thickness` (select) - 1px, 2px, 3px
- `style` (select) - solid, dashed, dotted
- `spacing` (select) - small, medium, large

**Default Props:**
```javascript
{
  color: '#e5e7eb',
  thickness: '1px',
  style: 'solid',
  spacing: 'medium'
}
```

### 8. SpacerBlock
Vertical spacing.

**Fields:**
- `height` (select) - 10px, 20px, 30px, 40px, 60px

**Default Props:**
```javascript
{
  height: '20px'
}
```

### 9. TwoColumnBlock
Two-column layout using tables.

**Fields:**
- `leftContent` (textarea) - Left column content
- `rightContent` (textarea) - Right column content
- `leftWidth` (select) - 30%, 40%, 50%, 60%, 70%
- `gap` (select) - 10px, 20px, 30px

**Default Props:**
```javascript
{
  leftContent: 'Left column content',
  rightContent: 'Right column content',
  leftWidth: '50%',
  gap: '20px'
}
```

### 10. CardBlock
Content card with image, title, description, button.

**Fields:**
- `image` (custom/ImageFieldComponent) - Card image
- `title` (text) - Card title
- `description` (textarea) - Card description
- `buttonText` (text) - Button text
- `buttonLink` (text) - Button link
- `backgroundColor` (text) - Card background
- `borderColor` (text) - Card border color

**Default Props:**
```javascript
{
  image: '',
  title: 'Card Title',
  description: 'Card description goes here.',
  buttonText: 'Read More',
  buttonLink: '#',
  backgroundColor: '#ffffff',
  borderColor: '#e5e7eb'
}
```

### 11. QuoteBlock
Blockquote with attribution.

**Fields:**
- `quote` (textarea) - Quote text
- `author` (text) - Author name
- `authorTitle` (text) - Author title/role
- `borderColor` (text) - Left border color
- `backgroundColor` (text) - Quote background

**Default Props:**
```javascript
{
  quote: 'Inspirational quote goes here...',
  author: '',
  authorTitle: '',
  borderColor: '#2563eb',
  backgroundColor: '#f9fafb'
}
```

### 12. PersonalizationBlock
Personalized greeting using merge tags.

**Fields:**
- `greeting` (text) - Greeting prefix
- `fallbackName` (text) - Name if not available
- `fontSize` (select) - 16px, 18px, 20px
- `color` (text) - Text color

**Default Props:**
```javascript
{
  greeting: 'Hello',
  fallbackName: 'Friend',
  fontSize: '18px',
  color: '#1f2937'
}
```

**Output:** `Hello {{name|Friend}},`

## Merge Tags (Personalization)

Support these merge tags that get replaced at send time:

| Tag | Description |
|-----|-------------|
| `{{name}}` | Subscriber name |
| `{{email}}` | Subscriber email |
| `{{unsubscribe_url}}` | Unsubscribe link |
| `{{preferences_url}}` | Preference center link |
| `{{tracking_pixel}}` | Open tracking pixel |
| `{{organization_name}}` | Organization name |
| `{{organization_address}}` | Physical address |

## API Endpoints

### Templates

```
GET    /api/newsletter/templates          - List all templates
GET    /api/newsletter/templates/:id      - Get single template
POST   /api/newsletter/templates          - Create template
PUT    /api/newsletter/templates/:id      - Update template
DELETE /api/newsletter/templates/:id      - Delete template
POST   /api/newsletter/templates/:id/duplicate - Duplicate template
```

### Sending

```
POST   /api/newsletter/send               - Send newsletter
POST   /api/newsletter/send/test          - Send test email
GET    /api/newsletter/campaigns          - List campaigns
GET    /api/newsletter/campaigns/:id/stats - Campaign statistics
```

### Subscribers (existing + new)

```
GET    /api/newsletter/admin/subscribers       - List subscribers
GET    /api/newsletter/admin/subscribers/stats - Subscriber statistics (NEW)
POST   /api/newsletter/admin/subscribers       - Add subscriber
PUT    /api/newsletter/admin/subscribers/:id   - Update subscriber
DELETE /api/newsletter/admin/subscribers/:id   - Remove subscriber
```

## File Structure

```
client/src/
├── components/
│   └── puck/
│       ├── puckNewsletterConfig.jsx    # Puck configuration
│       └── NewsletterComponents.jsx    # Email-safe components
│
├── pages/
│   └── admin/
│       ├── NewsletterEditor.jsx        # Template editor page
│       ├── NewsletterCampaigns.jsx     # Campaign management
│       ├── NewsletterSubscribers.jsx   # Subscriber management
│       └── NewsletterSettings.jsx      # Newsletter settings

server/
├── controllers/
│   └── newsletterController.js         # Newsletter CRUD + sending
│
├── routes/
│   └── newsletterRoutes.js             # API routes
│
├── services/
│   └── NewsletterService.js            # Email rendering + delivery
```

## Implementation Steps

1. **Delete broken implementation** - Remove current buggy files
2. **Create fresh NewsletterComponents.jsx** - Simple, email-safe components
3. **Create puckNewsletterConfig.jsx** - Following working puckConfig.jsx pattern
4. **Update NewsletterEditor.jsx** - Use new config
5. **Add missing stats endpoint** - `/api/newsletter/admin/subscribers/stats`
6. **Test in Puck editor** - Verify components render correctly

## Testing Requirements

1. All components render correctly in Puck editor
2. Generated HTML is email-client compatible
3. Merge tags replaced correctly at send time
4. Unsubscribe links work correctly
5. Open/click tracking functional
6. Mobile-responsive preview

## Success Criteria

- [ ] All components display with correct names in Puck sidebar
- [ ] Drag-and-drop works smoothly
- [ ] Field editing updates preview in real-time
- [ ] Save/load templates works correctly
- [ ] Generated HTML renders in major email clients
- [ ] CAN-SPAM compliant footer included by default
