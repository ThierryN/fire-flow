# Zoom Webhook Integration - Auto-Publishing Recordings to LMS Lessons

## The Problem

Need to automatically convert Zoom cloud recordings into course lessons immediately after recording completes, without manual intervention. The recording should appear in the course timeline within minutes of the Zoom meeting ending.

### Why It Was Hard

- **Webhook signature verification** - Zoom requires HMAC-SHA256 signature validation
- **Environment variable timing** - PM2 needs `--update-env` flag or changes don't load
- **Missing files in production** - File was committed locally but not pushed to GitHub
- **Asynchronous flow** - Recording processing happens 5-10 minutes after meeting ends
- **Database schema** - Required new tables for chapters and webhook event logs
- **Auto-lesson placement** - Need to intelligently place lessons in course structure

### Impact

Without this:
- ❌ Instructors must manually download recordings
- ❌ Instructors must manually create lessons
- ❌ Instructors must manually upload videos
- ❌ Students wait hours or days for content
- ❌ No automatic sync with LMS

With this:
- ✅ Recordings appear automatically
- ✅ Students see content within 10 minutes
- ✅ Zero manual work for instructors
- ✅ Chapter markers can be added for navigation
- ✅ Progress tracking works immediately

---

## The Solution

### Architecture Overview

```
Zoom Cloud → Recording Completes → Webhook Event → LMS Server → Create Lesson → Students See Content
```

### Components Required

1. **Webhook endpoint** - `/api/webhooks/zoom`
2. **Signature verification** - HMAC-SHA256 with secret token
3. **Event handler** - Process `recording.completed` event
4. **Lesson creator** - Auto-create lesson in course
5. **Database tables** - `webhook_event_logs`, `zoom_recording_chapters`

---

## Implementation Steps

### Step 1: Database Migrations

Create tables for webhook logging and chapter markers:

```sql
-- Migration 108: Add timezone to zoom_meetings
ALTER TABLE zoom_meetings ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC';

-- Migration 109: Create recording chapters and webhook logs
CREATE TABLE IF NOT EXISTS zoom_recording_chapters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recording_id UUID REFERENCES zoom_meetings(id) ON DELETE CASCADE,
  start_time INTEGER NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS webhook_event_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type VARCHAR(100) NOT NULL,
  source VARCHAR(50) NOT NULL,
  payload JSONB NOT NULL,
  status VARCHAR(50) DEFAULT 'pending',
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP
);

CREATE INDEX idx_webhook_logs_source ON webhook_event_logs(source);
CREATE INDEX idx_webhook_logs_status ON webhook_event_logs(status);
```

Run migrations:
```bash
cd ~/mern-app/server
node run-migration.js migrations/108_add_timezone_to_zoom_meetings.sql
node run-migration.js migrations/109_create_recording_chapters.sql
```

### Step 2: Create Webhook Controller

**File:** `server/controllers/zoomWebhookController.js`

```javascript
import crypto from 'crypto';
import sql from '../config/sql.js';

// Verify Zoom webhook signature
const verifySignature = (payload, signature) => {
  const secretToken = process.env.ZOOM_WEBHOOK_SECRET_TOKEN;
  if (!secretToken) {
    throw new Error('ZOOM_WEBHOOK_SECRET_TOKEN not configured');
  }

  const hash = crypto
    .createHmac('sha256', secretToken)
    .update(payload)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(hash)
  );
};

// Handle Zoom webhook events
export const handleZoomWebhook = async (req, res) => {
  try {
    const signature = req.headers['x-zm-signature'];
    const payload = req.rawBody; // Must preserve raw body for signature verification

    // Verify signature
    if (!verifySignature(payload, signature)) {
      return res.status(403).json({ error: 'Invalid signature' });
    }

    const event = req.body;

    // Handle URL validation challenge
    if (event.event === 'endpoint.url_validation') {
      const plainToken = event.payload.plainToken;
      const encryptedToken = crypto
        .createHmac('sha256', process.env.ZOOM_WEBHOOK_SECRET_TOKEN)
        .update(plainToken)
        .digest('hex');

      return res.json({
        plainToken,
        encryptedToken
      });
    }

    // Log webhook event
    await sql`
      INSERT INTO webhook_event_logs (event_type, source, payload, status)
      VALUES (${event.event}, 'zoom', ${JSON.stringify(event)}, 'pending')
    `;

    // Handle recording.completed event
    if (event.event === 'recording.completed') {
      await handleRecordingCompleted(event.payload);
    }

    res.json({ status: 'received' });
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).json({ error: 'Webhook processing failed' });
  }
};

// Auto-create lesson from recording
const handleRecordingCompleted = async (payload) => {
  const meetingId = payload.object.id;
  const recordingUrl = payload.object.recording_files[0]?.download_url;

  // Find associated course
  const meeting = await sql`
    SELECT course_id FROM zoom_meetings WHERE zoom_meeting_id = ${meetingId}
  `;

  if (meeting.length === 0 || !meeting[0].course_id) {
    console.log('Recording not linked to course, skipping auto-lesson');
    return;
  }

  const courseId = meeting[0].course_id;

  // Find or create "Class Recordings" section
  let section = await sql`
    SELECT id FROM course_sections
    WHERE course_id = ${courseId}
    AND title ILIKE '%recording%'
    LIMIT 1
  `;

  if (section.length === 0) {
    section = await sql`
      INSERT INTO course_sections (course_id, title, order_index)
      VALUES (${courseId}, 'Class Recordings', 9999)
      RETURNING id
    `;
  }

  // Create lesson
  await sql`
    INSERT INTO lessons (
      section_id,
      title,
      content_type,
      zoom_recording_id,
      is_published,
      created_at
    ) VALUES (
      ${section[0].id},
      ${payload.object.topic || 'Class Recording'},
      'zoom_recording',
      ${meeting[0].id},
      true,
      NOW()
    )
  `;

  console.log(`✅ Auto-created lesson for recording ${meetingId}`);
};
```

### Step 3: Add Webhook Routes

**File:** `server/routes/webhookRoutes.js`

```javascript
import express from 'express';
import { handleZoomWebhook } from '../controllers/zoomWebhookController.js';

const router = express.Router();

// Zoom webhook endpoint (no auth - verified by signature)
router.post('/zoom', handleZoomWebhook);

export default router;
```

**Add to server.js:**
```javascript
import webhookRoutes from './routes/webhookRoutes.js';

// IMPORTANT: Preserve raw body for signature verification
app.use('/api/webhooks', express.raw({ type: 'application/json' }), (req, res, next) => {
  req.rawBody = req.body.toString();
  next();
});

app.use('/api/webhooks', webhookRoutes);
```

### Step 4: Configure Environment Variables

Add to `server/.env`:
```env
ZOOM_WEBHOOK_SECRET_TOKEN=your_32_character_secret_from_zoom
```

**Get the secret token:**
1. Go to [Zoom App Marketplace](https://marketplace.zoom.us/)
2. Open your app → Feature tab
3. Event Subscriptions section → Copy "Secret Token"

### Step 5: Deploy to Production

```bash
# On production server
cd ~/mern-app

# Add webhook secret to .env
echo 'ZOOM_WEBHOOK_SECRET_TOKEN=<your_token>' >> server/.env

# Pull latest code
git pull origin student-beautification

# Build client
cd client
npm run build

# Copy to public_html
cd ..
cp -r client/dist/* ~/public_html/

# Create version.json
echo "{\"version\": \"$(date +%s)\", \"updated\": \"$(date)\"}" > ~/public_html/version.json

# Restart server with updated environment
pm2 restart lms-server --update-env

# Verify server started
pm2 logs lms-server --lines 20
```

### Step 6: Validate Webhook in Zoom

1. Go to Zoom App Marketplace → Your App → Feature tab
2. Add Event Subscription
3. Webhook URL: `https://yourdomain.com/api/webhooks/zoom`
4. Subscribe to event: `recording.completed`
5. Click **Validate**

**What happens during validation:**
- Zoom sends `endpoint.url_validation` event with `plainToken`
- Your server encrypts it with the secret token
- Returns `{ plainToken, encryptedToken }`
- Zoom verifies they match → ✅ Validated

---

## Testing the Integration

### Test 1: Validate Webhook

```bash
# After clicking Validate in Zoom, check logs
pm2 logs lms-server | grep webhook
```

Expected output:
```
✅ Webhook validated successfully
```

### Test 2: Record a Meeting

1. Create Zoom meeting linked to a course
2. Start meeting and enable cloud recording
3. End meeting
4. Wait 5-10 minutes for Zoom to process recording

### Test 3: Check Webhook Logs

```sql
SELECT * FROM webhook_event_logs
WHERE source = 'zoom'
ORDER BY created_at DESC
LIMIT 5;
```

Expected: `recording.completed` event with `status = 'processed'`

### Test 4: Verify Lesson Created

```sql
SELECT l.title, l.content_type, c.title as course_name
FROM lessons l
JOIN course_sections cs ON l.section_id = cs.id
JOIN courses c ON cs.course_id = c.id
WHERE l.content_type = 'zoom_recording'
ORDER BY l.created_at DESC;
```

Expected: New lesson appears automatically

---

## Troubleshooting

### Issue 1: "Invalid Signature" Error

**Cause:** Secret token mismatch or not loaded

**Fix:**
```bash
# Verify token is in .env
grep ZOOM_WEBHOOK_SECRET_TOKEN ~/mern-app/server/.env

# Restart with --update-env flag
pm2 restart lms-server --update-env
```

### Issue 2: "Module Not Found" Error

**Cause:** File not committed to GitHub

**Fix:**
```bash
# On local machine
git status server/controllers/
git add server/controllers/zoomWebhookController.js
git commit -m "Add missing webhook controller"
git push origin student-beautification

# On production server
git pull origin student-beautification
pm2 restart lms-server
```

### Issue 3: Webhook Validation Fails

**Cause:** Raw body not preserved for signature verification

**Fix:** Ensure `express.raw()` middleware is before webhook routes:
```javascript
app.use('/api/webhooks', express.raw({ type: 'application/json' }), ...);
```

### Issue 4: Lesson Not Auto-Created

**Causes:**
- Meeting not linked to a course
- Lesson already exists for this recording
- Database error

**Debug:**
```sql
-- Check if meeting is linked
SELECT * FROM zoom_meetings WHERE zoom_meeting_id = '<meeting_id>';

-- Check webhook logs for errors
SELECT error_message FROM webhook_event_logs
WHERE event_type = 'recording.completed'
AND status = 'failed';
```

---

## Prevention & Best Practices

### 1. Always Use Raw Body for Signature Verification
```javascript
app.use('/api/webhooks', express.raw({ type: 'application/json' }));
```

### 2. Log All Webhook Events
Helps with debugging and auditing:
```javascript
await sql`INSERT INTO webhook_event_logs (event_type, source, payload) ...`;
```

### 3. Use `--update-env` When Restarting PM2
Environment variables don't reload without this flag:
```bash
pm2 restart lms-server --update-env
```

### 4. Verify Files Are Committed
Before deploying:
```bash
git status
git log --oneline -5 --name-status
```

### 5. Test Locally with ngrok
```bash
ngrok http 5000
# Use ngrok URL as webhook endpoint for testing
```

---

## Security Considerations

### Signature Verification is Critical
Never skip signature verification - anyone could send fake webhook events without it.

### Use Timing-Safe Comparison
```javascript
crypto.timingSafeEqual(Buffer.from(sig1), Buffer.from(sig2));
```

Prevents timing attacks where attackers measure response time to guess signatures.

### Don't Log Sensitive Data
Recording URLs contain access tokens - don't log them in plaintext.

---

## Related Patterns

- [Webhook Security Best Practices](./WEBHOOK_SECURITY_PATTERNS.md)
- [PM2 Deployment Workflow](../deployment-security/PM2_DEPLOYMENT.md)
- [Environment Variable Management](../deployment-security/ENV_VARS_PRODUCTION.md)

---

## Common Mistakes to Avoid

- ❌ **Forgetting `--update-env`** - New env vars won't load
- ❌ **Not preserving raw body** - Signature verification fails
- ❌ **Missing file commit** - Works locally but fails in production
- ❌ **Wrong PM2 process name** - Use `pm2 status` to check actual name
- ❌ **Skipping signature verification** - Security vulnerability
- ❌ **Not logging webhook events** - Makes debugging impossible

---

## Resources

- [Zoom Webhook Documentation](https://developers.zoom.us/docs/api/rest/webhook-reference/)
- [HMAC-SHA256 Signature Verification](https://en.wikipedia.org/wiki/HMAC)
- [PM2 Environment Variables](https://pm2.keymetrics.io/docs/usage/environment/)
- [Express Raw Body Parser](https://expressjs.com/en/api.html#express.raw)

---

## Time to Implement

**Initial Setup:** 2-3 hours
**Debugging:** 1-2 hours (if issues arise)
**Testing:** 30 minutes

**Total:** ~4-6 hours for first implementation

---

## Difficulty Level

⭐⭐⭐⭐ (4/5) - Complex due to:
- Cryptographic signature verification
- Asynchronous webhook processing
- Production deployment considerations
- Multiple moving parts (database, server, Zoom)

---

## Success Criteria

✅ Webhook validates successfully in Zoom App Marketplace
✅ `recording.completed` events appear in `webhook_event_logs` table
✅ Lessons auto-create within 10 minutes of recording completion
✅ Students can see and play recordings immediately
✅ Chapter markers can be added by instructors
✅ No manual intervention required

---

**Author Notes:**

This integration took ~6 hours to implement and debug. The hardest parts were:
1. Realizing the `zoomRecordingManagement.js` file wasn't committed
2. Understanding PM2's `--update-env` requirement
3. Getting the raw body preservation right for signature verification

The key insight: **Always verify your deployment sequence matches what you tested locally.** Missing files and environment variables cause 90% of production deployment issues.

Once working, this feature is incredibly powerful - recordings appear automatically with zero instructor effort.

---

**Version:** 1.0
**Last Updated:** 2026-01-20
**Tested On:** Node.js 18.x, Express 4.x, PM2 5.x, PostgreSQL 14+
