# Appointment Scheduler Design Patterns

## Problem
Building an appointment scheduling system with video meeting integration (Zoom/Google Meet) for paid consultations, coaching sessions, and pastoral counseling.

---

## Solution: LatePoint-Inspired 5-Step Booking Flow

### Booking Flow Steps
1. **Select Service** - What type of appointment
2. **Select Provider** - Who to meet with
3. **Select Time** - Available date/time slots
4. **Enter Details** - Contact info, notes
5. **Confirm & Pay** - Payment and confirmation

---

## Database Schema

### Core Tables

```sql
-- Services (types of appointments)
CREATE TABLE services (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  duration_minutes INTEGER DEFAULT 60,
  buffer_before INTEGER DEFAULT 0,
  buffer_after INTEGER DEFAULT 15,
  price DECIMAL(10,2) DEFAULT 0,
  is_paid BOOLEAN DEFAULT false,
  color VARCHAR(7) DEFAULT '#3B82F6',
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Providers (staff who provide services)
CREATE TABLE providers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  bio TEXT,
  avatar_url VARCHAR(500),
  zoom_user_id VARCHAR(255),
  google_calendar_id VARCHAR(255),
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Provider availability
CREATE TABLE availability (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id UUID REFERENCES providers(id),
  day_of_week INTEGER, -- 0=Sunday, 6=Saturday
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  is_available BOOLEAN DEFAULT true
);

-- Appointments
CREATE TABLE appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  service_id UUID REFERENCES services(id),
  provider_id UUID REFERENCES providers(id),
  customer_id UUID REFERENCES users(id),
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',
  -- pending, confirmed, cancelled, completed, no_show
  meeting_type VARCHAR(20) DEFAULT 'zoom',
  -- zoom, google_meet, in_person, phone
  meeting_url VARCHAR(500),
  meeting_id VARCHAR(255),
  notes TEXT,
  customer_notes TEXT,
  payment_status VARCHAR(20) DEFAULT 'unpaid',
  payment_id VARCHAR(255),
  amount_paid DECIMAL(10,2),
  cancelled_at TIMESTAMP,
  cancellation_reason TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Time-off / blocked times
CREATE TABLE blocked_times (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id UUID REFERENCES providers(id),
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  reason VARCHAR(255),
  is_recurring BOOLEAN DEFAULT false
);
```

---

## API Endpoints

### Public Booking API
```javascript
// GET /api/booking/services
// List available services
router.get('/services', async (req, res) => {
  const services = await db('services')
    .where({ status: 'active' })
    .orderBy('name');
  res.json(services);
});

// GET /api/booking/providers?service_id=xxx
// List providers for a service
router.get('/providers', async (req, res) => {
  const { service_id } = req.query;
  const providers = await db('service_providers')
    .join('providers', 'providers.id', 'service_providers.provider_id')
    .where({ service_id, 'providers.status': 'active' })
    .select('providers.*');
  res.json(providers);
});

// GET /api/booking/availability?provider_id=xxx&service_id=xxx&date=2026-01-15
// Get available time slots
router.get('/availability', async (req, res) => {
  const { provider_id, service_id, date } = req.query;
  const slots = await getAvailableSlots(provider_id, service_id, date);
  res.json(slots);
});

// POST /api/booking/appointments
// Create new appointment
router.post('/appointments', async (req, res) => {
  const { service_id, provider_id, start_time, customer_info, notes } = req.body;

  // 1. Validate slot is still available
  const isAvailable = await checkSlotAvailable(provider_id, start_time);
  if (!isAvailable) {
    return res.status(409).json({ error: 'Time slot no longer available' });
  }

  // 2. Get service details
  const service = await db('services').where({ id: service_id }).first();

  // 3. Calculate end time
  const end_time = addMinutes(new Date(start_time), service.duration_minutes);

  // 4. Create appointment
  const [appointment] = await db('appointments').insert({
    service_id,
    provider_id,
    customer_id: req.user?.id,
    start_time,
    end_time,
    customer_notes: notes,
    status: service.is_paid ? 'pending_payment' : 'confirmed'
  }).returning('*');

  // 5. Create video meeting if needed
  if (service.meeting_type === 'zoom') {
    const meeting = await createZoomMeeting(appointment);
    await db('appointments')
      .where({ id: appointment.id })
      .update({ meeting_url: meeting.join_url, meeting_id: meeting.id });
  }

  // 6. Send confirmation email
  await sendAppointmentConfirmation(appointment);

  res.status(201).json(appointment);
});
```

---

## Availability Calculation

```javascript
// server/services/availability.js

const getAvailableSlots = async (providerId, serviceId, date) => {
  const targetDate = new Date(date);
  const dayOfWeek = targetDate.getDay();

  // 1. Get provider's base availability for this day
  const availability = await db('availability')
    .where({ provider_id: providerId, day_of_week: dayOfWeek, is_available: true })
    .first();

  if (!availability) return [];

  // 2. Get service duration
  const service = await db('services').where({ id: serviceId }).first();
  const slotDuration = service.duration_minutes;
  const bufferBefore = service.buffer_before || 0;
  const bufferAfter = service.buffer_after || 15;

  // 3. Get existing appointments for this day
  const startOfDay = startOfDayUTC(targetDate);
  const endOfDay = endOfDayUTC(targetDate);

  const existingAppointments = await db('appointments')
    .where({ provider_id: providerId })
    .whereIn('status', ['confirmed', 'pending'])
    .whereBetween('start_time', [startOfDay, endOfDay]);

  // 4. Get blocked times
  const blockedTimes = await db('blocked_times')
    .where({ provider_id: providerId })
    .where('start_time', '<=', endOfDay)
    .where('end_time', '>=', startOfDay);

  // 5. Generate all possible slots
  const slots = [];
  let currentTime = setTimeOnDate(targetDate, availability.start_time);
  const endTime = setTimeOnDate(targetDate, availability.end_time);

  while (currentTime < endTime) {
    const slotEnd = addMinutes(currentTime, slotDuration);

    // Check if slot is available
    const isBlocked = isTimeBlocked(currentTime, slotEnd, blockedTimes);
    const hasConflict = hasAppointmentConflict(
      currentTime,
      slotEnd,
      existingAppointments,
      bufferBefore,
      bufferAfter
    );

    if (!isBlocked && !hasConflict && slotEnd <= endTime) {
      slots.push({
        start: currentTime.toISOString(),
        end: slotEnd.toISOString(),
        available: true
      });
    }

    // Move to next slot (30-minute intervals)
    currentTime = addMinutes(currentTime, 30);
  }

  return slots;
};
```

---

## Zoom Integration

```javascript
// server/services/zoom.js
const axios = require('axios');

const createZoomMeeting = async (appointment) => {
  const provider = await db('providers')
    .where({ id: appointment.provider_id })
    .first();

  const accessToken = await getZoomAccessToken(provider.zoom_user_id);

  const response = await axios.post(
    `https://api.zoom.us/v2/users/${provider.zoom_user_id}/meetings`,
    {
      topic: `Appointment: ${appointment.service_name}`,
      type: 2, // Scheduled meeting
      start_time: appointment.start_time,
      duration: appointment.duration_minutes,
      timezone: provider.timezone || 'America/New_York',
      settings: {
        host_video: true,
        participant_video: true,
        join_before_host: false,
        waiting_room: true,
        auto_recording: 'none'
      }
    },
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    }
  );

  return {
    id: response.data.id,
    join_url: response.data.join_url,
    start_url: response.data.start_url,
    password: response.data.password
  };
};
```

---

## Google Calendar Integration

```javascript
// server/services/googleCalendar.js
const { google } = require('googleapis');

const createGoogleMeetEvent = async (appointment, provider) => {
  const oauth2Client = await getOAuthClient(provider.google_refresh_token);
  const calendar = google.calendar({ version: 'v3', auth: oauth2Client });

  const event = await calendar.events.insert({
    calendarId: provider.google_calendar_id || 'primary',
    conferenceDataVersion: 1,
    requestBody: {
      summary: `Appointment: ${appointment.service_name}`,
      description: appointment.notes,
      start: {
        dateTime: appointment.start_time,
        timeZone: provider.timezone
      },
      end: {
        dateTime: appointment.end_time,
        timeZone: provider.timezone
      },
      attendees: [
        { email: appointment.customer_email }
      ],
      conferenceData: {
        createRequest: {
          requestId: appointment.id,
          conferenceSolutionKey: { type: 'hangoutsMeet' }
        }
      }
    }
  });

  return {
    event_id: event.data.id,
    meeting_url: event.data.hangoutLink
  };
};
```

---

## React Booking Widget

```jsx
// client/src/components/BookingWidget.jsx
import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';

const BookingWidget = ({ defaultService }) => {
  const [step, setStep] = useState(1);
  const [booking, setBooking] = useState({
    service: null,
    provider: null,
    dateTime: null,
    customerInfo: {}
  });

  const steps = [
    { num: 1, label: 'Service', component: ServiceSelector },
    { num: 2, label: 'Provider', component: ProviderSelector },
    { num: 3, label: 'Date & Time', component: DateTimePicker },
    { num: 4, label: 'Details', component: CustomerDetails },
    { num: 5, label: 'Confirm', component: Confirmation }
  ];

  return (
    <div className="booking-widget">
      <StepIndicator steps={steps} currentStep={step} />
      <div className="booking-content">
        {steps.map(({ num, component: Component }) => (
          step === num && (
            <Component
              key={num}
              booking={booking}
              setBooking={setBooking}
              onNext={() => setStep(s => s + 1)}
              onBack={() => setStep(s => s - 1)}
            />
          )
        ))}
      </div>
    </div>
  );
};
```

---

## Church/Ministry Use Cases

### Pastoral Counseling
- Private 1-on-1 sessions
- Confidential video meetings
- No payment required (ministry service)
- Automated follow-up reminders

### Paid Coaching
- Business/life coaching sessions
- Integrated Stripe payments
- Package deals (5 sessions for $X)
- Recurring appointments

### Prayer Requests
- Short 15-minute prayer slots
- Multiple pastors available
- Phone or video option
- Walk-in availability

### Mentorship Programs
- Match mentors with mentees
- Regular recurring meetings
- Progress tracking
- Session notes

---

## References
- Full documentation: `docs/research/APPOINTMENT_SCHEDULER_RESEARCH.md`
- LatePoint patterns: https://latepoint.com/
- Booknetic patterns: https://booknetic.com/
- Zoom API: https://developers.zoom.us/docs/api/
- Google Calendar API: https://developers.google.com/calendar/api
