# Appointment Scheduling Systems Research

**Date:** January 2026
**Purpose:** Research appointment scheduling systems for integration into the MERN Community LMS
**Primary Reference:** LatePoint (user-preferred UI/UX)

---

## Table of Contents

1. [LatePoint Deep Dive](#1-latepoint-deep-dive-primary-reference)
2. [Feature Comparison Matrix](#2-feature-comparison-matrix)
3. [Video Meeting Integration Analysis](#3-video-meeting-integration-analysis)
4. [Payment Integration for Paid Sessions](#4-payment-integration-for-paid-sessions)
5. [Church/Ministry LMS Use Cases](#5-use-cases-for-churchministry-lms)
6. [UI/UX Patterns from LatePoint](#6-uiux-patterns-to-emulate-from-latepoint)
7. [Database Schema Design](#7-database-schema-design)
8. [API Design](#8-api-design)
9. [Implementation Recommendations](#9-implementation-recommendations)
10. [Open Source Alternatives](#10-open-source-alternatives-calcom)

---

## 1. LatePoint Deep Dive (Primary Reference)

### Overview

**LatePoint** is a premium WordPress appointment booking plugin known for its modern, intuitive UI and comprehensive feature set. It's designed for service-based businesses including salons, clinics, consultants, and coaches.

**Website:** https://latepoint.com
**Documentation:** https://latepoint.com/docs/
**Pricing:** One-time purchase (~$89 for single site, ~$179 for unlimited)

### Key Features

#### Booking Widget
- **Step-by-step booking flow** - Clean, guided process
- **Embeddable widget** - Can be placed anywhere on site
- **Modal/popup option** - Opens as overlay
- **Standalone booking page** - Dedicated full-page option
- **Mobile-responsive** - Adapts to all screen sizes

#### Calendar System
- **Day/Week/Month views** - Multiple calendar perspectives
- **Drag-and-drop rescheduling** - Easy appointment management
- **Color-coded appointments** - Visual status indicators
- **Timeline view** - Horizontal time-based layout
- **Availability overlay** - Shows open vs booked slots

#### Service Management
- **Unlimited services** - No restrictions on service types
- **Service categories** - Organized groupings
- **Duration settings** - Per-service time allocation
- **Pricing tiers** - Multiple price points
- **Service images** - Visual service cards
- **Buffer times** - Before/after appointment padding

#### Staff/Agent Management
- **Individual staff profiles** - Photos, bios, contact info
- **Staff-specific schedules** - Unique availability per person
- **Service assignments** - Which staff provides which services
- **Commission tracking** - Staff payment management
- **Staff dashboard** - Individual portals for agents

#### Customer Management
- **Customer profiles** - Contact info, history
- **Booking history** - Past appointment records
- **Customer notes** - Internal annotations
- **Customer groups** - Segmentation capabilities
- **Guest bookings** - No account required option

### UI/UX Highlights

#### Booking Flow (5 Steps)
1. **Service Selection** - Card-based grid with images, duration, price
2. **Agent Selection** - Staff cards with photos and availability indicator
3. **Date/Time Selection** - Clean calendar with available time slots
4. **Customer Information** - Form fields for contact details
5. **Confirmation** - Summary with edit option and payment

#### Admin Dashboard Layout
- **Left sidebar navigation** - Clean icon-based menu
- **Dashboard overview** - Today's appointments, stats, quick actions
- **Calendar as central element** - Primary workspace view
- **Right panel details** - Appointment/customer info on selection
- **Top bar** - Search, notifications, user menu

#### Visual Design Principles
- **Minimal, clean aesthetic** - White space utilization
- **Rounded corners** - Modern card-based design
- **Subtle shadows** - Depth without heaviness
- **Consistent iconography** - Cohesive icon set
- **Color-coded status** - Green (confirmed), Yellow (pending), Red (cancelled)
- **Smooth animations** - Transitions between steps

### Integrations

| Integration | Support Level |
|-------------|---------------|
| Google Calendar | Full sync (2-way) |
| Zoom | Auto-generate meeting links |
| Stripe | Payment processing |
| PayPal | Payment processing |
| Twilio | SMS notifications |
| Mailchimp | Email marketing |
| Zapier | 3rd party connections |
| WooCommerce | E-commerce integration |

### Add-ons Available
- Google Calendar Sync
- Zoom Meetings
- Stripe Payments
- PayPal Payments
- Twilio SMS
- Recurring Appointments
- Service Extras
- Coupons & Discounts
- Multi-Location
- Custom Work Hours

---

## 2. Feature Comparison Matrix

| Feature | LatePoint | Booknetic | Calendly | Amelia | Cal.com |
|---------|:---------:|:---------:|:--------:|:------:|:-------:|
| **Video Integrations** |
| Zoom integration | Yes (add-on) | Yes | Yes | Yes | Yes |
| Google Meet | Yes | Yes | Yes | Yes | Yes |
| Microsoft Teams | No | Yes | Yes | Yes | Yes |
| Custom video link | Yes | Yes | Yes | Yes | Yes |
| **Payment Processing** |
| Stripe | Yes (add-on) | Yes | Yes | Yes | Yes |
| PayPal | Yes (add-on) | Yes | Yes | Yes | Yes |
| Square | No | Yes | No | Yes | No |
| Deposit payments | Yes | Yes | Yes | Yes | Yes |
| Full upfront | Yes | Yes | Yes | Yes | Yes |
| **Scheduling Features** |
| Recurring appointments | Yes (add-on) | Yes | Yes | Yes | Yes |
| Group bookings | Yes | Yes | Yes | Yes | Yes |
| Buffer time | Yes | Yes | Yes | Yes | Yes |
| Minimum notice | Yes | Yes | Yes | Yes | Yes |
| Max future booking | Yes | Yes | Yes | Yes | Yes |
| Round-robin | No | Yes | Yes | No | Yes |
| **Customization** |
| Custom fields | Yes | Yes | Yes | Yes | Yes |
| Conditional logic | Limited | Yes | Yes | Yes | Yes |
| Custom CSS | Yes | Yes | Limited | Yes | Yes |
| White labeling | Yes | Yes | Paid | Yes | Yes |
| **Notifications** |
| Email reminders | Yes | Yes | Yes | Yes | Yes |
| SMS notifications | Yes (add-on) | Yes | Paid | Yes | Yes |
| WhatsApp | No | Yes | No | Yes | Limited |
| Webhook notifications | Yes | Yes | Yes | Yes | Yes |
| **Calendar Sync** |
| Google Calendar | Yes (add-on) | Yes | Yes | Yes | Yes |
| Outlook/365 | No | Yes | Yes | Yes | Yes |
| Apple Calendar | Via Google | Yes | Yes | Yes | Yes |
| 2-way sync | Yes | Yes | Yes | Yes | Yes |
| **Management** |
| Multi-staff | Yes | Yes | Yes | Yes | Yes |
| Multi-location | Yes (add-on) | Yes | Yes | Yes | Yes |
| Staff dashboard | Yes | Yes | N/A | Yes | Yes |
| Analytics | Basic | Advanced | Advanced | Advanced | Basic |
| **Packages & Pricing** |
| Package deals | Yes | Yes | Yes | Yes | Limited |
| Subscriptions | Limited | Yes | Yes | Yes | Yes |
| Coupons | Yes (add-on) | Yes | No | Yes | Limited |
| **Platform** |
| WordPress native | Yes | Yes | No | Yes | No |
| Standalone SaaS | No | No | Yes | No | Yes |
| Self-hosted | N/A | N/A | No | N/A | Yes |
| Open source | No | No | No | No | Yes |
| **Pricing Model** |
| One-time purchase | Yes ($89+) | Yes ($79+) | No | Yes ($59+) | N/A |
| Monthly subscription | No | No | $8-15/user | No | Free-$15/user |

### Platform-Specific Notes

#### LatePoint
- **Best for:** WordPress sites wanting polished UI
- **Strength:** Clean design, good UX
- **Weakness:** Add-on costs accumulate, WordPress-only

#### Booknetic
- **Best for:** WordPress sites needing all-in-one solution
- **Strength:** Feature-rich out of box, good video integrations
- **Weakness:** UI slightly less polished than LatePoint

#### Calendly
- **Best for:** Quick setup, professional use
- **Strength:** Industry standard, great integrations
- **Weakness:** Per-user pricing expensive for teams, no self-hosted option

#### Amelia
- **Best for:** Service businesses (salons, clinics)
- **Strength:** Beautiful UI, comprehensive features
- **Weakness:** Heavy, can slow WordPress sites

#### Cal.com
- **Best for:** Developers wanting full control
- **Strength:** Open source, self-hosted, API-first
- **Weakness:** Requires technical setup, UI less polished

---

## 3. Video Meeting Integration Analysis

### Zoom API Integration

#### Authentication
```javascript
// Zoom OAuth 2.0 flow
const zoomAuth = {
  authorizationUrl: 'https://zoom.us/oauth/authorize',
  tokenUrl: 'https://zoom.us/oauth/token',
  scopes: ['meeting:write', 'meeting:read', 'user:read']
};
```

#### Creating Meeting Links
```javascript
// POST https://api.zoom.us/v2/users/{userId}/meetings
const createZoomMeeting = async (appointment) => {
  const meetingConfig = {
    topic: `${appointment.serviceName} with ${appointment.providerName}`,
    type: 2, // Scheduled meeting
    start_time: appointment.startTime, // ISO 8601 format
    duration: appointment.duration, // minutes
    timezone: appointment.timezone,
    settings: {
      host_video: true,
      participant_video: true,
      join_before_host: false,
      waiting_room: true,
      auto_recording: 'cloud', // or 'local' or 'none'
      meeting_authentication: false
    }
  };

  const response = await zoomApi.post(`/users/me/meetings`, meetingConfig);
  return {
    meetingId: response.data.id,
    joinUrl: response.data.join_url,
    startUrl: response.data.start_url, // For host
    password: response.data.password
  };
};
```

#### Webhook Events
```javascript
// Zoom webhooks to handle
const zoomWebhookEvents = [
  'meeting.started',
  'meeting.ended',
  'meeting.participant_joined',
  'meeting.participant_left',
  'recording.completed',
  'meeting.updated',
  'meeting.deleted'
];
```

### Google Meet / Calendar API

#### Authentication
```javascript
// Google OAuth 2.0
const googleAuth = {
  scopes: [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
  ]
};
```

#### Creating Calendar Event with Meet Link
```javascript
// Google Calendar API - Auto-generates Meet link
const createGoogleMeetEvent = async (appointment) => {
  const event = {
    summary: `${appointment.serviceName} - ${appointment.customerName}`,
    description: appointment.notes,
    start: {
      dateTime: appointment.startTime,
      timeZone: appointment.timezone
    },
    end: {
      dateTime: appointment.endTime,
      timeZone: appointment.timezone
    },
    attendees: [
      { email: appointment.customerEmail },
      { email: appointment.providerEmail }
    ],
    conferenceData: {
      createRequest: {
        requestId: appointment.id,
        conferenceSolutionKey: { type: 'hangoutsMeet' }
      }
    },
    reminders: {
      useDefault: false,
      overrides: [
        { method: 'email', minutes: 24 * 60 }, // 1 day before
        { method: 'popup', minutes: 30 }        // 30 min before
      ]
    }
  };

  const response = await calendar.events.insert({
    calendarId: 'primary',
    resource: event,
    conferenceDataVersion: 1, // Required for Meet link
    sendUpdates: 'all' // Send invite emails
  });

  return {
    eventId: response.data.id,
    meetLink: response.data.conferenceData.entryPoints[0].uri,
    htmlLink: response.data.htmlLink
  };
};
```

### Microsoft Teams Integration

#### Authentication
```javascript
// Microsoft Graph API OAuth
const msAuth = {
  authorizationUrl: 'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize',
  scopes: [
    'OnlineMeetings.ReadWrite',
    'Calendars.ReadWrite',
    'User.Read'
  ]
};
```

#### Creating Teams Meeting
```javascript
// POST https://graph.microsoft.com/v1.0/me/onlineMeetings
const createTeamsMeeting = async (appointment) => {
  const meeting = {
    startDateTime: appointment.startTime,
    endDateTime: appointment.endTime,
    subject: `${appointment.serviceName} with ${appointment.providerName}`,
    participants: {
      attendees: [
        {
          upn: appointment.customerEmail,
          role: 'attendee'
        }
      ]
    },
    isEntryExitAnnounced: true,
    allowedPresenters: 'organizer',
    lobbyBypassSettings: {
      scope: 'organization',
      isDialInBypassEnabled: true
    }
  };

  const response = await graphApi.post('/me/onlineMeetings', meeting);
  return {
    meetingId: response.data.id,
    joinUrl: response.data.joinWebUrl,
    dialInInfo: response.data.audioConferencing
  };
};
```

### Integration Pattern Summary

| Platform | Auth Method | Meeting Creation | Calendar Sync | Recording |
|----------|-------------|------------------|---------------|-----------|
| Zoom | OAuth 2.0 | POST /meetings | Via webhooks | Cloud/Local |
| Google Meet | OAuth 2.0 | Calendar event | Native | None (Meet) |
| MS Teams | OAuth 2.0 (Graph) | POST /onlineMeetings | Outlook sync | Cloud |

### Best Practices

1. **Store tokens securely** - Encrypt OAuth tokens at rest
2. **Handle token refresh** - Implement automatic token refresh
3. **Webhook verification** - Validate webhook signatures
4. **Meeting cleanup** - Delete meetings on cancellation
5. **Fallback options** - Allow manual link entry if API fails
6. **Time zone handling** - Always store in UTC, convert for display

---

## 4. Payment Integration for Paid Sessions

### Stripe Integration Patterns

#### Setup
```javascript
// Server-side Stripe configuration
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

// Create customer on user registration
const createStripeCustomer = async (user) => {
  const customer = await stripe.customers.create({
    email: user.email,
    name: `${user.firstName} ${user.lastName}`,
    metadata: {
      userId: user._id.toString()
    }
  });
  return customer.id;
};
```

#### Payment Intent for Single Appointment
```javascript
const createAppointmentPayment = async (appointment, customer) => {
  const paymentIntent = await stripe.paymentIntents.create({
    amount: appointment.price * 100, // cents
    currency: 'usd',
    customer: customer.stripeId,
    metadata: {
      appointmentId: appointment._id.toString(),
      serviceId: appointment.serviceId,
      providerId: appointment.providerId
    },
    receipt_email: customer.email,
    description: `${appointment.serviceName} - ${appointment.date}`
  });

  return {
    clientSecret: paymentIntent.client_secret,
    paymentIntentId: paymentIntent.id
  };
};
```

#### Deposit Payment Pattern
```javascript
const createDepositPayment = async (appointment, depositPercent = 25) => {
  const depositAmount = Math.round(appointment.price * (depositPercent / 100));
  const remainingAmount = appointment.price - depositAmount;

  // Create deposit payment
  const depositIntent = await stripe.paymentIntents.create({
    amount: depositAmount * 100,
    currency: 'usd',
    metadata: {
      type: 'deposit',
      appointmentId: appointment._id.toString(),
      remainingAmount: remainingAmount
    }
  });

  return {
    depositAmount,
    remainingAmount,
    clientSecret: depositIntent.client_secret
  };
};
```

#### Package/Bundle Pricing
```javascript
// Create subscription for coaching packages
const createCoachingPackage = async (customer, packageDetails) => {
  // First, create the product and price in Stripe
  const product = await stripe.products.create({
    name: packageDetails.name,
    description: packageDetails.description,
    metadata: {
      sessions: packageDetails.sessionCount,
      validityDays: packageDetails.validityDays
    }
  });

  const price = await stripe.prices.create({
    product: product.id,
    unit_amount: packageDetails.price * 100,
    currency: 'usd',
    // For one-time packages
    // OR for subscriptions:
    // recurring: { interval: 'month' }
  });

  // Create checkout session
  const session = await stripe.checkout.sessions.create({
    customer: customer.stripeId,
    line_items: [{ price: price.id, quantity: 1 }],
    mode: 'payment', // or 'subscription'
    success_url: `${process.env.APP_URL}/booking/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.APP_URL}/booking/cancelled`,
    metadata: {
      packageId: packageDetails._id.toString()
    }
  });

  return session.url;
};
```

#### Refund/Cancellation Handling
```javascript
const handleCancellation = async (appointment, cancellationPolicy) => {
  const hoursUntilAppointment =
    (new Date(appointment.startTime) - new Date()) / (1000 * 60 * 60);

  let refundPercent = 0;

  // Example cancellation policy
  if (hoursUntilAppointment >= 48) {
    refundPercent = 100; // Full refund if 48+ hours notice
  } else if (hoursUntilAppointment >= 24) {
    refundPercent = 50;  // 50% refund if 24-48 hours
  } else {
    refundPercent = 0;   // No refund if less than 24 hours
  }

  if (refundPercent > 0 && appointment.paymentIntentId) {
    const refundAmount = Math.round(
      appointment.amountPaid * (refundPercent / 100)
    );

    await stripe.refunds.create({
      payment_intent: appointment.paymentIntentId,
      amount: refundAmount * 100,
      reason: 'requested_by_customer',
      metadata: {
        appointmentId: appointment._id.toString(),
        cancellationPolicy: `${refundPercent}% refund`
      }
    });
  }

  return { refundPercent, refundAmount };
};
```

### PayPal Integration

```javascript
// PayPal Orders API
const paypal = require('@paypal/checkout-server-sdk');

const createPayPalOrder = async (appointment) => {
  const request = new paypal.orders.OrdersCreateRequest();
  request.prefer('return=representation');
  request.requestBody({
    intent: 'CAPTURE',
    purchase_units: [{
      amount: {
        currency_code: 'USD',
        value: appointment.price.toFixed(2)
      },
      description: appointment.serviceName,
      custom_id: appointment._id.toString()
    }],
    application_context: {
      return_url: `${process.env.APP_URL}/booking/paypal/success`,
      cancel_url: `${process.env.APP_URL}/booking/paypal/cancel`
    }
  });

  const response = await paypalClient.execute(request);
  return {
    orderId: response.result.id,
    approvalUrl: response.result.links.find(l => l.rel === 'approve').href
  };
};
```

### Pricing Models for Coaching/Ministry

| Model | Description | Implementation |
|-------|-------------|----------------|
| **Pay-per-session** | Single appointment charge | PaymentIntent |
| **Deposit + Balance** | % upfront, rest at appointment | Split payments |
| **Package (Credits)** | Buy X sessions, use over time | Credit system |
| **Subscription** | Monthly coaching access | Stripe Subscription |
| **Donation-based** | Pay-what-you-can | Variable amount |
| **Sliding scale** | Income-based pricing | Price tiers |

---

## 5. Use Cases for Church/Ministry LMS

### 1. Pastoral Counseling

**Description:** Private 1-on-1 sessions with pastoral staff for spiritual guidance, marriage counseling, grief support, etc.

**Requirements:**
- Privacy/confidentiality emphasis
- Secure video option (no recordings)
- Flexible duration (30, 60, 90 min)
- Notes visible only to counselor
- Follow-up scheduling
- Crisis/urgent appointment option

**Booking Flow:**
1. Select counseling type (Marriage, Grief, Spiritual Direction, etc.)
2. Choose pastor/counselor (with photos, specialties)
3. Pick available time slot
4. Provide brief description (optional, private)
5. Confirm (no payment typically)

**Special Features:**
- Waiting room for video calls
- Emergency contact capture
- Referral tracking
- Session notes (encrypted)
- Follow-up reminders

### 2. Paid Coaching Sessions

**Description:** Professional mentorship, life coaching, business coaching by trained ministry staff or guest coaches.

**Requirements:**
- Full payment or deposit required
- Package pricing options
- Zoom/Meet integration mandatory
- Session recordings (optional)
- Intake forms
- Progress tracking

**Booking Flow:**
1. Select coaching program
2. Choose coach (credentials, testimonials)
3. Select date/time
4. Complete intake questionnaire
5. Payment (full or deposit)
6. Confirmation with prep materials

**Special Features:**
- Coach certification display
- Session packages (6, 12, 24 sessions)
- Homework/resource sharing
- Progress assessments
- Certificate of completion

### 3. Prayer Appointments

**Description:** Free or donation-based prayer sessions with prayer team members.

**Requirements:**
- Low barrier to entry
- Anonymous option available
- Prayer request capture
- Phone or video options
- Multiple team members available
- Short duration (15-30 min)

**Booking Flow:**
1. Select prayer type (Healing, Guidance, Intercession)
2. Enter prayer request (optional)
3. Choose contact method (phone, video, in-person)
4. Select time
5. Optional donation
6. Confirmation

**Special Features:**
- Prayer request journaling
- Follow-up prayer option
- Praise report submission
- Prayer chain integration
- Anonymous booking option

### 4. Bible Study Consultations

**Description:** Individual or small group sessions to discuss Scripture, theology questions, or course material.

**Requirements:**
- Linked to enrolled courses
- Group booking capability
- Screen sharing for materials
- Recording for review
- Resource recommendations

**Booking Flow:**
1. Select study type (course Q&A, topical, book study)
2. Individual or group (invite others)
3. Select instructor
4. Choose topic/passage
5. Book time
6. Add to calendar

**Special Features:**
- Pre-submit questions
- Resource library link
- Group chat before session
- Recording archive
- Related course suggestions

### 5. Course Office Hours

**Description:** Instructors offer availability for enrolled students to ask questions.

**Requirements:**
- Course enrollment verification
- Instructor availability per course
- Drop-in or scheduled options
- Queue system for popular times
- Screen sharing enabled

**Booking Flow:**
1. Select course (shows enrolled courses only)
2. View instructor's available hours
3. Book slot or join queue
4. Brief question preview
5. Join session

**Special Features:**
- "Next available" option
- Queue position indicator
- Past questions archive
- Student rating after session
- Office hours analytics

### 6. Ministry Team Meetings

**Description:** Internal scheduling for ministry leaders and volunteers.

**Requirements:**
- Role-based access
- Recurring meeting support
- Team calendar view
- Resource booking (rooms)
- Agenda integration

**Booking Flow:**
1. Select meeting type
2. Invite team members
3. Book room/resource
4. Set agenda
5. Send invitations

**Special Features:**
- Ministry team directories
- Room/resource availability
- Meeting minutes integration
- Task assignments
- Attendance tracking

### Ministry-Specific Feature Summary

| Feature | Pastoral | Coaching | Prayer | Bible Study | Office Hours | Team |
|---------|:--------:|:--------:|:------:|:-----------:|:------------:|:----:|
| Payment required | No | Yes | Optional | Optional | No | No |
| Video required | Optional | Yes | Optional | Yes | Yes | Optional |
| Privacy level | High | Medium | High | Low | Low | Medium |
| Recurring | Optional | Yes | No | Optional | Yes | Yes |
| Group booking | No | Optional | No | Yes | No | Yes |
| Course linked | No | Optional | No | Yes | Yes | No |
| Recording | No | Optional | No | Yes | Optional | Optional |
| Follow-up | Yes | Yes | Yes | Yes | No | Yes |

---

## 6. UI/UX Patterns to Emulate from LatePoint

### Booking Widget Design

#### Step Progress Indicator
```
[1] Service  ----  [2] Staff  ----  [3] Time  ----  [4] Details  ----  [5] Confirm
    (active)        (next)          (future)        (future)           (future)
```

**Implementation Notes:**
- Circular numbered steps connected by lines
- Active step highlighted with primary color
- Completed steps show checkmark
- Future steps grayed out
- Clickable to go back (not forward)

#### Service Selection Cards

```
+---------------------------+
|  [Service Image]          |
|                           |
|  Service Name             |
|  Brief description...     |
|                           |
|  Duration: 60 min         |
|  Price: $75               |
|                           |
|  [Select Button]          |
+---------------------------+
```

**Implementation Notes:**
- Grid layout (2-3 columns desktop, 1 mobile)
- Hover effect with subtle shadow increase
- Selected state with border/highlight
- Category tabs above grid
- Search/filter option for many services

### Calendar Picker Interface

#### Month View
```
         January 2026
  Su  Mo  Tu  We  Th  Fr  Sa
                  1   2   3   4
  5   6   7   8   9  10  11
 12  13  14  15  16  17  18
 19  20  21  22  23  24  25
 26  27  28  29  30  31

  [Available]  [Unavailable]  [Selected]
```

**Implementation Notes:**
- Past dates disabled (grayed)
- Available dates normal color
- Unavailable dates crossed out or grayed
- Selected date highlighted with primary color
- Hover shows available slot count tooltip
- Month navigation arrows
- "Today" quick link

### Time Slot Selection

```
Morning (9 AM - 12 PM)
+--------+  +--------+  +--------+  +--------+
| 9:00   |  | 9:30   |  | 10:00  |  | 10:30  |
+--------+  +--------+  +--------+  +--------+

Afternoon (12 PM - 5 PM)
+--------+  +--------+  +--------+  +--------+
| 1:00   |  | 1:30   |  | 2:00   |  | 2:30   |
+--------+  +--------+  +--------+  +--------+
```

**Implementation Notes:**
- Group by time of day
- Button/pill style for slots
- Unavailable slots not shown (or faded)
- Selected slot highlighted
- Timezone displayed with change option
- Duration shown based on selected service

### Staff/Provider Cards

```
+------------------------------------------+
|  +-------+                               |
|  | Photo |  Provider Name                |
|  |       |  Title / Specialty            |
|  +-------+  ****+ (4.8) 127 reviews      |
|                                          |
|  "Short bio or tagline about this       |
|   provider's expertise..."               |
|                                          |
|  Next available: Today at 2:30 PM        |
|                                          |
|  [View Profile]  [Book Now]              |
+------------------------------------------+
```

**Implementation Notes:**
- Horizontal card layout preferred
- Photo should be professional headshot
- Specialties as tags/chips
- Availability indicator
- "Any available" option at top

### Confirmation Screen

```
+------------------------------------------+
|        Booking Confirmed!                |
|                                          |
|  +------------------------------------+  |
|  | Service: Life Coaching Session     |  |
|  | Provider: John Smith               |  |
|  | Date: Tuesday, January 14, 2026    |  |
|  | Time: 2:00 PM - 3:00 PM (EST)      |  |
|  | Location: Zoom (link below)        |  |
|  | Total: $75.00 (Paid)               |  |
|  +------------------------------------+  |
|                                          |
|  Join Link: [Copy to Clipboard]          |
|  https://zoom.us/j/123456789             |
|                                          |
|  [Add to Calendar]  [View Details]       |
|                                          |
|  A confirmation email has been sent to   |
|  your@email.com                          |
+------------------------------------------+
```

### Admin Dashboard Layout

```
+----------------------------------------------------------------+
| Logo    Search [____________]    [Bell] [User Menu]            |
+--------+-------------------------------------------------------+
|        |                                                       |
| [D]    |   Dashboard                                           |
| Home   |   +-------------+  +-------------+  +-------------+   |
|        |   | Today       |  | This Week   |  | Revenue     |   |
| [Cal]  |   | 8 bookings  |  | 42 bookings |  | $3,240      |   |
| Appts  |   +-------------+  +-------------+  +-------------+   |
|        |                                                       |
| [User] |   Today's Schedule                                    |
| Staff  |   +-----------------------------------------------+   |
|        |   | 9:00  | John - Life Coaching        | [View]  |   |
| [Box]  |   | 10:30 | Sarah - Career Consult      | [View]  |   |
| Srvcs  |   | 2:00  | Mike - Bible Study          | [View]  |   |
|        |   | 4:00  | John - Prayer Session       | [View]  |   |
| [Ppl]  |   +-----------------------------------------------+   |
| Cust   |                                                       |
|        |   Quick Actions                                       |
| [Gear] |   [+ New Booking] [+ New Customer] [Block Time]       |
| Settng |                                                       |
+--------+-------------------------------------------------------+
```

### Appointment List View

```
+----------------------------------------------------------------+
| Appointments          [+ New]  [Filter ▼]  [Export]            |
+----------------------------------------------------------------+
| Search: [________________]   Date: [Jan 1 - Jan 31 ▼]          |
+----------------------------------------------------------------+
| Status ▼  | Customer      | Service        | Date/Time | Staff |
+----------------------------------------------------------------+
| [Green]   | Alice Johnson | Life Coaching  | Jan 14    | John  |
| Confirmed |               | 60 min         | 2:00 PM   |       |
+-----------+---------------+----------------+-----------+-------+
| [Yellow]  | Bob Smith     | Career Consult | Jan 14    | Sarah |
| Pending   |               | 45 min         | 10:30 AM  |       |
+-----------+---------------+----------------+-----------+-------+
| [Red]     | Carol White   | Prayer         | Jan 15    | Mike  |
| Cancelled |               | 30 min         | 9:00 AM   |       |
+-----------+---------------+----------------+-----------+-------+

Showing 1-10 of 156 appointments    [< Prev] [1] [2] [3] [Next >]
```

### Color System

```css
/* Status Colors */
--status-confirmed: #22C55E;    /* Green */
--status-pending: #F59E0B;      /* Amber */
--status-cancelled: #EF4444;    /* Red */
--status-completed: #6B7280;    /* Gray */
--status-no-show: #8B5CF6;      /* Purple */

/* Primary UI Colors */
--primary: #3B82F6;             /* Blue - actions, links */
--secondary: #6366F1;           /* Indigo - accents */
--neutral: #F3F4F6;             /* Light gray - backgrounds */

/* Functional Colors */
--success: #10B981;
--warning: #F59E0B;
--error: #EF4444;
--info: #3B82F6;
```

### Key UX Principles from LatePoint

1. **Progressive Disclosure** - Only show relevant options at each step
2. **Clear Visual Hierarchy** - Important info is prominent
3. **Immediate Feedback** - Loading states, confirmations
4. **Error Prevention** - Disable invalid options, validate early
5. **Easy Recovery** - Back buttons, edit options, cancel capability
6. **Accessibility** - Keyboard navigation, screen reader support
7. **Mobile-First** - Touch-friendly targets, responsive design

---

## 7. Database Schema Design

### MongoDB Collections

#### appointments
```javascript
{
  _id: ObjectId,

  // Core relationships
  customerId: ObjectId,          // ref: users
  providerId: ObjectId,          // ref: users
  serviceId: ObjectId,           // ref: services
  locationId: ObjectId,          // ref: locations (optional)

  // Timing
  startTime: Date,               // UTC
  endTime: Date,                 // UTC
  duration: Number,              // minutes
  timezone: String,              // "America/New_York"

  // Status
  status: {
    type: String,
    enum: ['pending', 'confirmed', 'cancelled', 'completed', 'no_show'],
    default: 'pending'
  },

  // Meeting details
  meetingType: {
    type: String,
    enum: ['in_person', 'zoom', 'google_meet', 'ms_teams', 'phone', 'other']
  },
  meetingLink: String,
  meetingId: String,             // External meeting ID (Zoom, etc.)
  meetingPassword: String,

  // Payment
  paymentStatus: {
    type: String,
    enum: ['not_required', 'pending', 'deposit_paid', 'paid', 'refunded'],
    default: 'not_required'
  },
  price: Number,
  depositAmount: Number,
  amountPaid: Number,
  paymentIntentId: String,       // Stripe
  paymentMethod: String,         // 'stripe', 'paypal', 'cash', etc.

  // Package/credits (if using package)
  packageId: ObjectId,           // ref: customer_packages
  creditUsed: Boolean,

  // Booking metadata
  bookedAt: Date,
  bookedBy: ObjectId,            // Who made the booking
  source: String,                // 'website', 'admin', 'api'

  // Communication
  customerNotes: String,         // Notes from customer
  internalNotes: String,         // Staff-only notes

  // Custom fields responses
  customFieldResponses: [{
    fieldId: ObjectId,
    fieldName: String,
    value: Mixed
  }],

  // Reminders sent
  remindersSent: [{
    type: String,                // 'email', 'sms'
    sentAt: Date,
    templateId: String
  }],

  // Cancellation
  cancelledAt: Date,
  cancelledBy: ObjectId,
  cancellationReason: String,
  refundAmount: Number,

  // Recurring appointment
  isRecurring: Boolean,
  recurringPatternId: ObjectId,  // ref: recurring_patterns

  // Group booking
  isGroupSession: Boolean,
  groupSessionId: ObjectId,      // ref: group_sessions

  // Audit
  createdAt: Date,
  updatedAt: Date
}

// Indexes
db.appointments.createIndex({ customerId: 1, startTime: -1 });
db.appointments.createIndex({ providerId: 1, startTime: 1 });
db.appointments.createIndex({ startTime: 1, status: 1 });
db.appointments.createIndex({ status: 1 });
```

#### services
```javascript
{
  _id: ObjectId,

  // Basic info
  name: String,
  slug: String,
  description: String,
  shortDescription: String,

  // Categorization
  categoryId: ObjectId,          // ref: service_categories
  tags: [String],

  // Timing
  duration: Number,              // minutes
  bufferTimeBefore: Number,      // minutes
  bufferTimeAfter: Number,       // minutes

  // Pricing
  price: Number,
  depositRequired: Boolean,
  depositAmount: Number,         // Fixed amount or percentage
  depositType: String,           // 'fixed', 'percentage'

  // Availability
  isActive: Boolean,
  visibility: String,            // 'public', 'private', 'members_only'

  // Booking rules
  minAdvanceBooking: Number,     // hours
  maxAdvanceBooking: Number,     // days
  maxDailyBookings: Number,      // per provider

  // Meeting options
  allowedMeetingTypes: [String], // ['zoom', 'in_person', etc.]
  defaultMeetingType: String,

  // Assigned providers
  providerIds: [ObjectId],       // ref: users

  // Visual
  image: String,
  color: String,                 // For calendar display
  icon: String,

  // Custom fields required
  customFields: [{
    fieldId: ObjectId,
    required: Boolean
  }],

  // Course integration (for LMS)
  linkedCourseId: ObjectId,      // ref: courses
  requiresEnrollment: Boolean,

  // Sorting
  displayOrder: Number,

  createdAt: Date,
  updatedAt: Date
}
```

#### providers (extends users)
```javascript
// Provider profile stored in users collection with role: 'provider'
// Additional provider-specific fields:
{
  _id: ObjectId,
  // ... base user fields ...

  providerProfile: {
    // Professional info
    title: String,
    bio: String,
    specialties: [String],
    credentials: [String],

    // Availability
    timezone: String,
    defaultAvailability: ObjectId,  // ref: availability_schedules

    // Services offered
    serviceIds: [ObjectId],

    // Locations (for multi-location)
    locationIds: [ObjectId],

    // Settings
    acceptsNewClients: Boolean,
    maxDailyAppointments: Number,

    // Calendar sync
    googleCalendarId: String,
    outlookCalendarId: String,

    // Meeting preferences
    zoomUserId: String,
    teamsUserId: String,
    preferredMeetingType: String,

    // Commission (if applicable)
    commissionRate: Number,        // percentage

    // Rating
    averageRating: Number,
    totalReviews: Number
  }
}
```

#### availability_schedules
```javascript
{
  _id: ObjectId,

  name: String,                  // "Regular Hours", "Summer Schedule"
  providerId: ObjectId,
  isDefault: Boolean,

  // Weekly recurring schedule
  weeklySchedule: {
    monday: [{
      startTime: String,         // "09:00"
      endTime: String,           // "17:00"
      locationId: ObjectId       // optional
    }],
    tuesday: [{ /* ... */ }],
    wednesday: [{ /* ... */ }],
    thursday: [{ /* ... */ }],
    friday: [{ /* ... */ }],
    saturday: [{ /* ... */ }],
    sunday: [{ /* ... */ }]
  },

  // Effective dates
  effectiveFrom: Date,
  effectiveTo: Date,

  createdAt: Date,
  updatedAt: Date
}
```

#### booking_rules
```javascript
{
  _id: ObjectId,

  // Scope (can be global, per-service, per-provider)
  scope: String,                 // 'global', 'service', 'provider'
  scopeId: ObjectId,             // serviceId or providerId if scoped

  // Time constraints
  minAdvanceBooking: {
    value: Number,
    unit: String                 // 'hours', 'days'
  },
  maxAdvanceBooking: {
    value: Number,
    unit: String
  },

  // Capacity
  maxBookingsPerDay: Number,
  maxBookingsPerWeek: Number,

  // Slot settings
  slotDuration: Number,          // minutes
  slotInterval: Number,          // minutes (for start times)

  // Buffer enforcement
  enforceBufferTime: Boolean,

  // Customer rules
  maxActiveBookingsPerCustomer: Number,
  requireAccountForBooking: Boolean,

  // Cancellation policy
  cancellationPolicy: {
    allowCancellation: Boolean,
    cutoffHours: Number,         // Hours before appointment
    refundPolicy: [{
      hoursBeforeAppointment: Number,
      refundPercentage: Number
    }]
  },

  // Rescheduling policy
  reschedulingPolicy: {
    allowRescheduling: Boolean,
    cutoffHours: Number,
    maxReschedules: Number
  },

  createdAt: Date,
  updatedAt: Date
}
```

#### payments
```javascript
{
  _id: ObjectId,

  // Relationships
  appointmentId: ObjectId,
  customerId: ObjectId,

  // Payment details
  amount: Number,
  currency: String,              // 'USD'
  type: String,                  // 'full', 'deposit', 'balance', 'refund'

  // Provider info
  provider: String,              // 'stripe', 'paypal'
  transactionId: String,
  paymentIntentId: String,

  // Status
  status: String,                // 'pending', 'completed', 'failed', 'refunded'

  // Timestamps
  paidAt: Date,

  // Refund info
  refundedAmount: Number,
  refundedAt: Date,
  refundReason: String,

  // Metadata
  receiptUrl: String,
  metadata: Object,

  createdAt: Date,
  updatedAt: Date
}
```

#### reminders
```javascript
{
  _id: ObjectId,

  // Template info
  name: String,
  type: String,                  // 'email', 'sms', 'push'
  trigger: String,               // 'before_appointment', 'after_booking'

  // Timing
  triggerTime: {
    value: Number,
    unit: String                 // 'minutes', 'hours', 'days'
  },

  // Template content
  subject: String,               // For email
  body: String,                  // Supports variables like {{customer_name}}

  // Targeting
  isActive: Boolean,
  serviceIds: [ObjectId],        // Empty = all services

  // Variables available
  // {{customer_name}}, {{customer_email}}, {{appointment_date}},
  // {{appointment_time}}, {{service_name}}, {{provider_name}},
  // {{meeting_link}}, {{cancel_link}}, {{reschedule_link}}

  createdAt: Date,
  updatedAt: Date
}
```

#### meeting_links
```javascript
{
  _id: ObjectId,

  appointmentId: ObjectId,

  // Provider info
  provider: String,              // 'zoom', 'google_meet', 'ms_teams'

  // Meeting details
  externalMeetingId: String,
  joinUrl: String,
  hostUrl: String,               // For host to start meeting
  password: String,

  // Status
  status: String,                // 'active', 'started', 'ended', 'cancelled'

  // Recording (if enabled)
  recordingEnabled: Boolean,
  recordingUrl: String,

  // Timestamps
  scheduledStart: Date,
  scheduledEnd: Date,
  actualStart: Date,
  actualEnd: Date,

  // Participants (from webhooks)
  participants: [{
    email: String,
    joinedAt: Date,
    leftAt: Date,
    duration: Number             // minutes
  }],

  createdAt: Date,
  updatedAt: Date
}
```

### Schema Relationships Diagram

```
users (customers/providers)
    |
    +---> appointments <--- services
    |          |                |
    |          |                +---> service_categories
    |          |
    |          +---> payments
    |          |
    |          +---> meeting_links
    |          |
    |          +---> reminders (templates)
    |
    +---> availability_schedules
    |
    +---> customer_packages
              |
              +---> package_definitions
```

---

## 8. API Design

### RESTful Endpoints

#### Appointments

```
# List appointments (with filters)
GET /api/v1/appointments
Query params:
  - status: pending|confirmed|cancelled|completed
  - providerId: ObjectId
  - customerId: ObjectId
  - startDate: ISO date
  - endDate: ISO date
  - page: number
  - limit: number

# Get single appointment
GET /api/v1/appointments/:id

# Create appointment (booking)
POST /api/v1/appointments
Body: {
  serviceId: ObjectId,
  providerId: ObjectId,
  startTime: ISO datetime,
  meetingType: 'zoom' | 'google_meet' | 'in_person',
  customerNotes: String,
  customFieldResponses: [{ fieldId, value }]
}

# Update appointment
PATCH /api/v1/appointments/:id
Body: {
  status: String,
  internalNotes: String,
  ...
}

# Cancel appointment
POST /api/v1/appointments/:id/cancel
Body: {
  reason: String
}

# Reschedule appointment
POST /api/v1/appointments/:id/reschedule
Body: {
  newStartTime: ISO datetime
}

# Complete appointment
POST /api/v1/appointments/:id/complete
Body: {
  notes: String,
  rating: Number (optional)
}
```

#### Services

```
# List services
GET /api/v1/services
Query params:
  - categoryId: ObjectId
  - providerId: ObjectId (services offered by this provider)
  - isActive: boolean

# Get service details
GET /api/v1/services/:id

# Create service (admin)
POST /api/v1/services
Body: {
  name: String,
  description: String,
  duration: Number,
  price: Number,
  categoryId: ObjectId,
  providerIds: [ObjectId],
  ...
}

# Update service (admin)
PATCH /api/v1/services/:id

# Delete service (admin)
DELETE /api/v1/services/:id

# Get service categories
GET /api/v1/service-categories

# Create service category (admin)
POST /api/v1/service-categories
```

#### Providers

```
# List providers
GET /api/v1/providers
Query params:
  - serviceId: ObjectId (providers offering this service)
  - locationId: ObjectId
  - available: boolean

# Get provider details
GET /api/v1/providers/:id

# Get provider's services
GET /api/v1/providers/:id/services

# Get provider's schedule/availability
GET /api/v1/providers/:id/availability
Query params:
  - startDate: ISO date
  - endDate: ISO date

# Update provider profile (self or admin)
PATCH /api/v1/providers/:id
```

#### Availability

```
# Get available time slots
GET /api/v1/availability
Query params:
  - serviceId: ObjectId (required)
  - providerId: ObjectId (optional, any if not specified)
  - date: ISO date (required)
  - timezone: String (default: UTC)

Response: {
  date: "2026-01-15",
  provider: { id, name },
  slots: [
    { startTime: "09:00", endTime: "10:00", available: true },
    { startTime: "10:00", endTime: "11:00", available: false },
    ...
  ]
}

# Get availability for date range
GET /api/v1/availability/range
Query params:
  - serviceId: ObjectId
  - providerId: ObjectId
  - startDate: ISO date
  - endDate: ISO date

Response: {
  dates: [
    { date: "2026-01-15", hasAvailability: true, slotCount: 5 },
    { date: "2026-01-16", hasAvailability: false, slotCount: 0 },
    ...
  ]
}

# Get/Update provider's schedule
GET /api/v1/providers/:id/schedules
POST /api/v1/providers/:id/schedules
PATCH /api/v1/providers/:id/schedules/:scheduleId

# Block time (vacation, busy)
POST /api/v1/providers/:id/blocked-times
Body: {
  startTime: ISO datetime,
  endTime: ISO datetime,
  reason: String,
  recurring: Boolean
}
```

#### Bookings (Public-facing endpoint)

```
# Create booking (customer flow)
POST /api/v1/bookings
Body: {
  serviceId: ObjectId,
  providerId: ObjectId,
  startTime: ISO datetime,
  customer: {
    email: String,
    firstName: String,
    lastName: String,
    phone: String (optional)
  },
  meetingType: String,
  notes: String,
  customFields: [{ fieldId, value }]
}

Response: {
  appointmentId: ObjectId,
  confirmationNumber: String,
  requiresPayment: Boolean,
  paymentClientSecret: String (if payment required)
}

# Confirm booking after payment
POST /api/v1/bookings/:id/confirm-payment
Body: {
  paymentIntentId: String
}

# Get booking by confirmation number (public)
GET /api/v1/bookings/lookup
Query params:
  - confirmationNumber: String
  - email: String
```

#### Webhooks

```
# Zoom webhook
POST /api/v1/webhooks/zoom
Headers: {
  Authorization: Bearer <zoom_webhook_token>
}
Events: meeting.started, meeting.ended, recording.completed

# Google Calendar webhook
POST /api/v1/webhooks/google-calendar
Events: calendar.events.created, calendar.events.updated

# Stripe webhook
POST /api/v1/webhooks/stripe
Events: payment_intent.succeeded, payment_intent.failed, refund.created

# PayPal webhook
POST /api/v1/webhooks/paypal
Events: PAYMENT.CAPTURE.COMPLETED, PAYMENT.CAPTURE.DENIED
```

### API Response Format

```javascript
// Success response
{
  success: true,
  data: { ... },
  meta: {
    page: 1,
    limit: 20,
    total: 150,
    totalPages: 8
  }
}

// Error response
{
  success: false,
  error: {
    code: "SLOT_NOT_AVAILABLE",
    message: "The selected time slot is no longer available",
    details: { ... }
  }
}
```

### Authentication & Authorization

```javascript
// Endpoints by auth level

// Public (no auth required)
GET /api/v1/services                  // List active services
GET /api/v1/providers                 // List active providers
GET /api/v1/availability              // Check availability
POST /api/v1/bookings                 // Create booking

// Customer authenticated
GET /api/v1/me/appointments           // My appointments
POST /api/v1/appointments/:id/cancel  // Cancel my appointment
POST /api/v1/appointments/:id/reschedule

// Provider authenticated
GET /api/v1/provider/appointments     // My appointments as provider
PATCH /api/v1/provider/profile        // Update my provider profile
PATCH /api/v1/provider/schedules      // Update my availability

// Admin only
POST /api/v1/services                 // Create service
DELETE /api/v1/services/:id           // Delete service
PATCH /api/v1/appointments/:id        // Update any appointment
GET /api/v1/reports/*                 // Analytics/reports
```

---

## 9. Implementation Recommendations

### Phase 1: Core Booking (MVP)

**Priority:** Must-have features for initial launch

| Feature | Description | Effort |
|---------|-------------|--------|
| Service Management | CRUD for services with categories | Medium |
| Provider Profiles | Basic provider setup with bio, photo | Low |
| Availability Setup | Weekly recurring schedules | Medium |
| Booking Widget | Step-by-step booking flow | High |
| Calendar View | Admin calendar for managing appointments | Medium |
| Email Notifications | Booking confirmation, reminders | Medium |
| Basic Payments | Stripe integration for paid services | Medium |

**Estimated Timeline:** 4-6 weeks

**Technology Choices:**
- Frontend: React components with Tailwind CSS
- Calendar: FullCalendar.js or react-big-calendar
- Date/Time: date-fns or Day.js with timezone support
- Payments: @stripe/stripe-js, @stripe/react-stripe-js
- Email: Nodemailer with template engine (Handlebars)

### Phase 2: Video Integration

**Priority:** Essential for remote ministry/coaching

| Feature | Description | Effort |
|---------|-------------|--------|
| Zoom Integration | OAuth, auto-create meetings | High |
| Google Meet | Calendar API integration | Medium |
| Meeting Links | Store/display meeting URLs | Low |
| Join Button | One-click meeting access | Low |
| Recording Access | Display recording links (Zoom) | Medium |

**Estimated Timeline:** 2-3 weeks

**Technology Choices:**
- Zoom: @zoom/videosdk or direct REST API
- Google: googleapis npm package
- OAuth: passport.js with google/zoom strategies

### Phase 3: Enhanced Features

**Priority:** Improved user experience

| Feature | Description | Effort |
|---------|-------------|--------|
| SMS Notifications | Twilio integration | Medium |
| Google Calendar Sync | 2-way sync for providers | High |
| Recurring Appointments | Weekly/monthly patterns | High |
| Group Bookings | Multiple participants | Medium |
| Waiting List | Auto-book when slots open | Medium |
| Custom Fields | Dynamic form builder | High |

**Estimated Timeline:** 4-5 weeks

### Phase 4: Ministry-Specific

**Priority:** Features specific to church/ministry use

| Feature | Description | Effort |
|---------|-------------|--------|
| Prayer Appointments | Anonymous/donation-based | Medium |
| Course Integration | Link to enrolled courses | Medium |
| Office Hours | Drop-in queue system | High |
| Pastoral Notes | Encrypted session notes | Medium |
| Counseling Intake | Specialized intake forms | Medium |
| Ministry Team Scheduling | Internal team bookings | Medium |

**Estimated Timeline:** 3-4 weeks

### Component Structure

```
src/
├── components/
│   └── appointments/
│       ├── BookingWidget/
│       │   ├── BookingWidget.jsx
│       │   ├── ServiceSelection.jsx
│       │   ├── ProviderSelection.jsx
│       │   ├── DateTimeSelection.jsx
│       │   ├── CustomerForm.jsx
│       │   ├── BookingConfirmation.jsx
│       │   └── index.js
│       ├── Calendar/
│       │   ├── AppointmentCalendar.jsx
│       │   ├── DayView.jsx
│       │   ├── WeekView.jsx
│       │   ├── MonthView.jsx
│       │   └── TimeSlotPicker.jsx
│       ├── Admin/
│       │   ├── AppointmentList.jsx
│       │   ├── AppointmentDetail.jsx
│       │   ├── ServiceManager.jsx
│       │   ├── ProviderManager.jsx
│       │   └── AvailabilityEditor.jsx
│       └── common/
│           ├── StatusBadge.jsx
│           ├── TimeSlotButton.jsx
│           └── ProviderCard.jsx
├── hooks/
│   └── appointments/
│       ├── useAvailability.js
│       ├── useBooking.js
│       ├── useAppointments.js
│       └── useProviders.js
├── services/
│   └── appointments/
│       ├── appointmentService.js
│       ├── availabilityService.js
│       ├── bookingService.js
│       └── paymentService.js
└── store/
    └── appointmentSlice.js
```

### Integration Priority Order

1. **Stripe** - Most used, best developer experience
2. **Zoom** - Most common video platform
3. **Google Calendar** - Essential for provider scheduling
4. **Google Meet** - Free alternative to Zoom
5. **Twilio SMS** - For reminder notifications
6. **PayPal** - Alternative payment method
7. **Microsoft Teams** - Enterprise users

---

## 10. Open Source Alternatives (Cal.com)

### Overview

**Cal.com** (formerly Calendso) is an open-source scheduling platform that can serve as a reference implementation or starting point.

**Website:** https://cal.com
**GitHub:** https://github.com/calcom/cal.com
**License:** AGPLv3 (open source, but requires derivative works to also be open source)
**Tech Stack:** Next.js, TypeScript, Prisma, tRPC, Tailwind CSS

### Repository Structure

```
cal.com/
├── apps/
│   ├── web/                    # Main Next.js application
│   ├── api/                    # API routes
│   └── console/                # Admin console
├── packages/
│   ├── core/                   # Core business logic
│   ├── prisma/                 # Database schema & migrations
│   ├── trpc/                   # tRPC API layer
│   ├── emails/                 # Email templates
│   ├── embeds/                 # Embed widget code
│   ├── lib/                    # Shared utilities
│   └── ui/                     # UI component library
├── docker/                     # Docker configuration
└── docs/                       # Documentation
```

### Key Features to Analyze

| Feature | Implementation | Adaptable |
|---------|---------------|-----------|
| Event Types | `packages/core/EventType` | Yes |
| Availability | `packages/core/availability` | Yes |
| Booking Flow | `apps/web/pages/book` | Yes |
| Calendar Sync | `packages/core/CalendarManager` | Partial |
| Video Integrations | `packages/core/videoClient` | Yes |
| Webhooks | `packages/core/webhooks` | Yes |
| Embed Widget | `packages/embeds` | Yes |

### Prisma Schema Highlights

```prisma
// From Cal.com's schema - relevant models

model EventType {
  id                      Int                     @id @default(autoincrement())
  title                   String
  slug                    String
  description             String?
  length                  Int                     // Duration in minutes
  hidden                  Boolean                 @default(false)
  userId                  Int?
  teamId                  Int?
  price                   Int                     @default(0)
  currency                String                  @default("usd")
  minimumBookingNotice    Int                     @default(120) // minutes
  bufferTime              Int                     @default(0)
  // ... more fields
}

model Booking {
  id                      Int                     @id @default(autoincrement())
  uid                     String                  @unique
  userId                  Int?
  eventTypeId             Int?
  title                   String
  description             String?
  startTime               DateTime
  endTime                 DateTime
  status                  BookingStatus           @default(ACCEPTED)
  // ... more fields
}

model Availability {
  id                      Int                     @id @default(autoincrement())
  userId                  Int?
  eventTypeId             Int?
  days                    Int[]                   // 0-6 for days of week
  startTime               DateTime
  endTime                 DateTime
  // ... more fields
}
```

### Customization Approach

#### Option 1: Fork and Modify
- Fork the repository
- Modify to fit ministry needs
- Maintain as separate project
- **Pros:** Full control, all features available
- **Cons:** Maintenance burden, AGPLv3 license obligations

#### Option 2: Reference Implementation
- Study Cal.com's architecture
- Build custom implementation inspired by patterns
- No license restrictions
- **Pros:** Clean codebase, no license issues
- **Cons:** More development effort

#### Option 3: Hybrid Approach
- Use Cal.com's open packages (embeds, UI components)
- Build custom backend
- **Pros:** Faster development, partial reuse
- **Cons:** Some license considerations

### Recommended Approach for This Project

Given the ministry LMS context, **Option 2 (Reference Implementation)** is recommended:

1. **Study Cal.com's patterns** for:
   - Availability calculation algorithms
   - Booking conflict detection
   - Calendar sync architecture
   - Embed widget structure

2. **Build custom implementation** that:
   - Integrates with existing MERN stack
   - Supports ministry-specific use cases
   - Doesn't require AGPLv3 licensing
   - Can be closed-source if needed

3. **Borrow UI patterns** from:
   - LatePoint (primary UI reference)
   - Cal.com (functional patterns)
   - Calendly (polish and simplicity)

### Cal.com Code Examples

#### Availability Calculation
```typescript
// Simplified from Cal.com's availability logic
export async function getAvailability({
  eventType,
  startDate,
  endDate,
  userId,
}: GetAvailabilityParams) {
  // Get user's schedule
  const schedule = await getSchedule(userId);

  // Get existing bookings in range
  const bookings = await getBookings(userId, startDate, endDate);

  // Get blocked times (calendar events, etc.)
  const busyTimes = await getBusyTimes(userId, startDate, endDate);

  // Calculate available slots
  const slots = [];
  let current = startDate;

  while (current < endDate) {
    const daySchedule = schedule[current.getDay()];

    for (const period of daySchedule) {
      let slotStart = combineDateTime(current, period.start);
      const periodEnd = combineDateTime(current, period.end);

      while (slotStart + eventType.length <= periodEnd) {
        const slotEnd = slotStart + eventType.length;

        const isAvailable = !hasConflict(slotStart, slotEnd, [
          ...bookings,
          ...busyTimes,
        ]);

        if (isAvailable) {
          slots.push({
            start: slotStart,
            end: slotEnd,
          });
        }

        slotStart = slotStart + eventType.slotInterval;
      }
    }

    current = addDays(current, 1);
  }

  return slots;
}
```

---

## Additional Resources

### Documentation Links

| Platform | Documentation URL |
|----------|-------------------|
| LatePoint | https://latepoint.com/docs/ |
| Booknetic | https://booknetic.com/documentation/ |
| Calendly | https://developer.calendly.com/docs |
| Cal.com | https://cal.com/docs |
| Amelia | https://wpamelia.com/documentation/ |

### API Documentation

| Service | API Docs |
|---------|----------|
| Zoom API | https://marketplace.zoom.us/docs/api-reference |
| Google Calendar API | https://developers.google.com/calendar/api/v3/reference |
| Microsoft Graph | https://docs.microsoft.com/en-us/graph/api/resources/onlinemeetingbase |
| Stripe | https://stripe.com/docs/api |
| Twilio | https://www.twilio.com/docs/sms/api |

### Recommended NPM Packages

```json
{
  "dependencies": {
    // Calendar & Scheduling
    "date-fns": "^2.30.0",
    "date-fns-tz": "^2.0.0",
    "rrule": "^2.7.2",

    // UI Components
    "@fullcalendar/react": "^6.1.0",
    "@fullcalendar/daygrid": "^6.1.0",
    "@fullcalendar/timegrid": "^6.1.0",
    "@fullcalendar/interaction": "^6.1.0",

    // Video Integrations
    "googleapis": "^126.0.0",

    // Payments
    "@stripe/stripe-js": "^2.1.0",
    "@stripe/react-stripe-js": "^2.3.0",
    "stripe": "^13.0.0",

    // Notifications
    "nodemailer": "^6.9.0",
    "twilio": "^4.18.0",

    // Utilities
    "uuid": "^9.0.0",
    "nanoid": "^5.0.0"
  }
}
```

---

## Conclusion

This research provides a comprehensive foundation for building an appointment scheduling system within the MERN Community LMS. The recommended approach is:

1. **Use LatePoint as the primary UI/UX reference** - Its clean, modern design aligns with user preferences
2. **Implement core features in Phase 1** - Services, providers, availability, booking widget
3. **Add video integration in Phase 2** - Zoom and Google Meet are highest priority
4. **Study Cal.com's architecture** - For availability algorithms and booking logic patterns
5. **Build custom implementation** - Avoid AGPLv3 license restrictions, integrate seamlessly with existing LMS

The ministry-specific use cases (pastoral counseling, prayer appointments, coaching) differentiate this from generic scheduling solutions and should guide feature prioritization.
