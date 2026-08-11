# Scheduled Content Publishing with node-cron

> Reliable scheduled publishing system using node-cron: timezone-aware, double-publish-safe, with manual trigger endpoint for testing.

**When to use:** Any CMS, blog, or content platform where authors can schedule posts for future publication. Works with the `content-publishing-states.md` state machine.
**Stack:** Node.js/Express or Bun, node-cron, PostgreSQL, TypeScript

---

## node-cron Setup

```bash
npm install node-cron
npm install @types/node-cron
```

### Cron Syntax Reference

```
┌────────────── second (optional, 0-59)
│ ┌──────────── minute (0-59)
│ │ ┌────────── hour (0-23)
│ │ │ ┌──────── day of month (1-31)
│ │ │ │ ┌────── month (1-12 or JAN-DEC)
│ │ │ │ │ ┌──── day of week (0-7 or SUN-SAT, 0 and 7 both = Sunday)
│ │ │ │ │ │
* * * * * *

Common patterns:
'* * * * *'      — every minute
'*/5 * * * *'    — every 5 minutes
'0 * * * *'      — every hour (at minute 0)
'0 9 * * 1-5'   — 9am weekdays
'0 0 * * *'      — midnight daily
'0 0 1 * *'      — midnight first of month
```

---

## Core Scheduler: Publish Scheduled Content

```typescript
// schedulers/content-publisher.ts
import cron from 'node-cron';
import { Pool } from 'pg';
import { logStatusChange } from '../lib/audit-log';

interface SchedulerConfig {
  db: Pool;
  cronExpression?: string;       // default: every minute
  maxBatchSize?: number;         // safety limit per run
  onPublishSuccess?: (contentId: string, title: string) => void;
  onPublishFailure?: (contentId: string, error: Error) => void;
}

export function startContentPublisher(config: SchedulerConfig) {
  const {
    db,
    cronExpression = '* * * * *',   // every minute
    maxBatchSize = 50,
    onPublishSuccess,
    onPublishFailure,
  } = config;

  // Validate the cron expression before registering
  if (!cron.validate(cronExpression)) {
    throw new Error(`Invalid cron expression: ${cronExpression}`);
  }

  const task = cron.schedule(cronExpression, async () => {
    await publishDueContent({ db, maxBatchSize, onPublishSuccess, onPublishFailure });
  }, {
    timezone: 'UTC',       // ALWAYS run cron in UTC, convert for display only
    scheduled: true,
  });

  console.log(`[ContentPublisher] Started. Schedule: ${cronExpression} (UTC)`);
  return task;
}

interface PublishRunOptions {
  db: Pool;
  maxBatchSize: number;
  systemUserId?: string;         // ID of the "system" user for audit logs
  onPublishSuccess?: (contentId: string, title: string) => void;
  onPublishFailure?: (contentId: string, error: Error) => void;
}

export async function publishDueContent(options: PublishRunOptions): Promise<{
  published: string[];
  failed: string[];
}> {
  const { db, maxBatchSize, onPublishSuccess, onPublishFailure } = options;
  const published: string[] = [];
  const failed: string[] = [];

  const client = await db.connect();

  try {
    await client.query('BEGIN');

    // SELECT FOR UPDATE SKIP LOCKED:
    // - Locks the rows so a second scheduler instance can't pick the same posts
    // - SKIP LOCKED means a concurrent process won't wait — it just skips locked rows
    // - This prevents double-publishing even if two server instances run simultaneously
    const { rows: dueContent } = await client.query<{
      id: string;
      title: string;
      scheduled_at: Date;
    }>(`
      SELECT id, title, scheduled_at
      FROM content
      WHERE
        status = 'scheduled'
        AND scheduled_at <= NOW()
      ORDER BY scheduled_at ASC
      LIMIT $1
      FOR UPDATE SKIP LOCKED
    `, [maxBatchSize]);

    if (dueContent.length === 0) {
      await client.query('COMMIT');
      return { published, failed };
    }

    console.log(`[ContentPublisher] Found ${dueContent.length} post(s) due for publishing`);

    // Batch update all due posts to 'published'
    const ids = dueContent.map(r => r.id);
    await client.query(`
      UPDATE content
      SET
        status      = 'published',
        published_at = NOW(),
        scheduled_at = NULL,
        updated_at   = NOW()
      WHERE id = ANY($1::uuid[])
    `, [ids]);

    await client.query('COMMIT');

    // Post-commit: audit logs and notifications (outside transaction)
    for (const post of dueContent) {
      try {
        await logStatusChange(db, {
          contentId:   post.id,
          fromStatus:  'scheduled',
          toStatus:    'published',
          changedBy:   options.systemUserId ?? '00000000-0000-0000-0000-000000000000',
          notes:       `Auto-published at scheduled time: ${post.scheduled_at.toISOString()}`,
          metadata:    { trigger: 'cron', scheduled_at: post.scheduled_at },
        });
        published.push(post.id);
        onPublishSuccess?.(post.id, post.title);
        console.log(`[ContentPublisher] Published: "${post.title}" (${post.id})`);
      } catch (auditErr) {
        // Audit log failure doesn't undo the publish — log and move on
        console.error(`[ContentPublisher] Audit log failed for ${post.id}:`, auditErr);
      }
    }

  } catch (err) {
    await client.query('ROLLBACK');
    console.error('[ContentPublisher] Batch publish failed, rolled back:', err);

    // `failed` is empty here — the batch threw before individual tracking ran.
    // Notify for ALL due items since we don't know which succeeded.
    const allIds = dueContent.map(r => r.id);
    for (const id of allIds) {
      onPublishFailure?.(id, err as Error);
    }
  } finally {
    client.release();
  }

  return { published, failed };
}
```

---

## Registering the Scheduler at App Startup

```typescript
// app.ts or server.ts
import express from 'express';
import { Pool } from 'pg';
import { startContentPublisher } from './schedulers/content-publisher';

const app = express();
const db = new Pool({ connectionString: process.env.DATABASE_URL });

// Start the cron job when the server starts
const publisherTask = startContentPublisher({
  db,
  cronExpression: '* * * * *',   // every minute
  maxBatchSize: 50,
  onPublishSuccess: (id, title) => {
    // Trigger a webhook, send a notification, invalidate CDN cache, etc.
    console.log(`Published: ${title}`);
    // Example: invalidateCache(`/posts/${slug}`);
    // Example: sendPublishNotification(authorId, title);
  },
  onPublishFailure: (id, error) => {
    console.error(`Failed to publish ${id}:`, error.message);
    // Example: alertOpsTeam(error);
  },
});

// Graceful shutdown
process.on('SIGTERM', () => {
  publisherTask.stop();
  db.end();
  process.exit(0);
});
```

---

## Timezone Handling

**Rule: Store everything in UTC. Convert only for display.**

```typescript
// Correct: when a user schedules for "2026-03-15 09:00 America/New_York"
// Convert to UTC before storing:
import { zonedTimeToUtc, utcToZonedTime, format } from 'date-fns-tz';

// npm install date-fns date-fns-tz

function scheduleContentInUserTimezone(
  isoDateString: string,    // e.g. "2026-03-15T09:00"  (no timezone)
  userTimezone: string      // e.g. "America/New_York"
): Date {
  // Convert user's local time to UTC for storage
  return zonedTimeToUtc(isoDateString, userTimezone);
}

function formatScheduledAtForUser(
  utcDate: Date,
  userTimezone: string
): string {
  const localDate = utcToZonedTime(utcDate, userTimezone);
  return format(localDate, "MMM d, yyyy 'at' h:mm a zzz", { timeZone: userTimezone });
}

// Usage in route handler:
router.patch('/content/:id/schedule', async (req, res) => {
  const { scheduled_at_local, timezone } = req.body;
  // scheduled_at_local: "2026-03-15T09:00" (from a datetime-local input)
  // timezone: "America/New_York" (from user profile or request)

  const scheduledAtUtc = scheduleContentInUserTimezone(scheduled_at_local, timezone);

  if (scheduledAtUtc <= new Date()) {
    return res.status(400).json({ error: 'Scheduled time must be in the future' });
  }

  await db.query(
    'UPDATE content SET status = $1, scheduled_at = $2 WHERE id = $3',
    ['scheduled', scheduledAtUtc, req.params.id]
  );

  res.json({
    status: 'scheduled',
    scheduled_at_utc: scheduledAtUtc.toISOString(),
    scheduled_at_display: formatScheduledAtForUser(scheduledAtUtc, timezone),
  });
});
```

**Frontend datetime input handling:**

```tsx
// Use a timezone-aware datetime picker or convert locally:
function ScheduleForm({ onSchedule }: { onSchedule: (utcDate: string, tz: string) => void }) {
  const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const localDatetime = form.get('scheduled_at') as string;  // "2026-03-15T09:00"
    onSchedule(localDatetime, userTimezone);
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Schedule for (your time: {userTimezone})
        <input type="datetime-local" name="scheduled_at" min={new Date().toISOString().slice(0, 16)} />
      </label>
      <button type="submit">Schedule</button>
    </form>
  );
}
```

---

## Double-Publish Prevention

The `SELECT FOR UPDATE SKIP LOCKED` pattern is the correct solution. Here's why it works:

```sql
-- When Instance A runs:
BEGIN;
SELECT id, title FROM content
WHERE status = 'scheduled' AND scheduled_at <= NOW()
FOR UPDATE SKIP LOCKED;
-- Instance A holds locks on rows 1, 2, 3

-- Simultaneously, Instance B runs:
BEGIN;
SELECT id, title FROM content
WHERE status = 'scheduled' AND scheduled_at <= NOW()
FOR UPDATE SKIP LOCKED;
-- Instance B sees rows 1, 2, 3 are locked → SKIPS them
-- Instance B gets 0 rows → does nothing
-- No double-publish
```

**Alternative: PostgreSQL Advisory Locks (for simpler use cases)**

```typescript
// Acquire a session-level advisory lock (lock_id is an arbitrary integer)
const PUBLISHER_LOCK_ID = 123456789;

async function withPublisherLock(db: Pool, fn: () => Promise<void>): Promise<void> {
  const client = await db.connect();
  try {
    // Try to acquire lock — returns immediately if already held
    const { rows } = await client.query(
      'SELECT pg_try_advisory_lock($1) AS acquired',
      [PUBLISHER_LOCK_ID]
    );

    if (!rows[0].acquired) {
      console.log('[ContentPublisher] Another instance is running, skipping');
      return;
    }

    try {
      await fn();
    } finally {
      await client.query('SELECT pg_advisory_unlock($1)', [PUBLISHER_LOCK_ID]);
    }
  } finally {
    client.release();
  }
}

// Usage:
await withPublisherLock(db, () => publishDueContent(options));
```

Use `SELECT FOR UPDATE SKIP LOCKED` for batch row-level locking. Use advisory locks for single-instance "only one cron at a time" protection. In production, use both.

---

## Schedule Route with Validation

```typescript
// routes/content-schedule.ts
import { Router } from 'express';
import { zonedTimeToUtc } from 'date-fns-tz';

const router = Router();

// POST /content/:id/schedule
router.post('/content/:id/schedule', async (req, res) => {
  const { id } = req.params;
  const { scheduled_at, timezone = 'UTC', notes } = req.body;

  // Validate
  if (!scheduled_at) {
    return res.status(400).json({ error: 'scheduled_at is required' });
  }

  let scheduledAtUtc: Date;
  try {
    scheduledAtUtc = timezone === 'UTC'
      ? new Date(scheduled_at)
      : zonedTimeToUtc(scheduled_at, timezone);
  } catch {
    return res.status(400).json({ error: 'Invalid date format or timezone' });
  }

  // Must be at least 1 minute in the future (grace period for clock skew)
  const minimumFuture = new Date(Date.now() + 60_000);
  if (scheduledAtUtc < minimumFuture) {
    return res.status(400).json({
      error: 'Scheduled time must be at least 1 minute in the future',
    });
  }

  // Check content exists and is in a schedulable state
  const { rows } = await db.query(
    'SELECT id, status, title, slug FROM content WHERE id = $1',
    [id]
  );

  if (!rows[0]) return res.status(404).json({ error: 'Content not found' });

  const content = rows[0];

  if (!['in_review', 'draft'].includes(content.status)) {
    return res.status(422).json({
      error: `Cannot schedule content with status '${content.status}'`,
    });
  }

  if (!content.slug) {
    return res.status(422).json({ error: 'Content must have a slug before scheduling' });
  }

  // Update
  await db.query(`
    UPDATE content
    SET status = 'scheduled', scheduled_at = $1, updated_at = NOW(), updated_by = $2
    WHERE id = $3
  `, [scheduledAtUtc, req.user.id, id]);

  res.json({
    status: 'scheduled',
    scheduled_at: scheduledAtUtc.toISOString(),
  });
});

// DELETE /content/:id/schedule — cancel scheduling
router.delete('/content/:id/schedule', async (req, res) => {
  const { id } = req.params;

  const { rows } = await db.query('SELECT status FROM content WHERE id = $1', [id]);

  if (!rows[0]) return res.status(404).json({ error: 'Content not found' });
  if (rows[0].status !== 'scheduled') {
    return res.status(422).json({ error: 'Content is not currently scheduled' });
  }

  await db.query(`
    UPDATE content
    SET status = 'draft', scheduled_at = NULL, updated_at = NOW(), updated_by = $1
    WHERE id = $2
  `, [req.user.id, id]);

  res.json({ status: 'draft' });
});

export default router;
```

---

## Error Handling: What to Do When Scheduled Publish Fails

```typescript
// In the cron handler — after a publish failure:

interface FailedPublish {
  contentId: string;
  failedAt: Date;
  attemptCount: number;
  lastError: string;
}

// Option 1: Retry table (simple, durable)
// Add a publish_attempts column to content:
// ALTER TABLE content ADD COLUMN publish_attempts INT NOT NULL DEFAULT 0;
// ALTER TABLE content ADD COLUMN last_publish_error TEXT;

async function handlePublishFailure(db: Pool, contentId: string, error: Error) {
  await db.query(`
    UPDATE content
    SET
      publish_attempts   = publish_attempts + 1,
      last_publish_error = $1
    WHERE id = $2
  `, [error.message, contentId]);

  // After 3 failures, move to draft and notify author
  const { rows } = await db.query(
    'SELECT publish_attempts, author_id, title FROM content WHERE id = $1',
    [contentId]
  );

  if (rows[0]?.publish_attempts >= 3) {
    await db.query(`
      UPDATE content
      SET status = 'draft', scheduled_at = NULL
      WHERE id = $1
    `, [contentId]);

    // Notify author (implement your notification system)
    await notifyAuthor(rows[0].author_id, {
      type: 'publish_failed',
      contentId,
      title: rows[0].title,
      error: error.message,
    });
  }
}
```

---

## Manual Trigger Endpoint for Testing

**Never wait for a cron to fire during development.** Add a protected endpoint to trigger the publisher manually:

```typescript
// routes/admin.ts
import { publishDueContent } from '../schedulers/content-publisher';

// POST /admin/trigger-publisher
// Only accessible to admins — or only in non-production
router.post('/admin/trigger-publisher', requireRole('admin'), async (req, res) => {
  if (process.env.NODE_ENV === 'production' && !req.user?.isSuperAdmin) {
    return res.status(403).json({ error: 'Manual trigger disabled in production' });
  }

  console.log('[Admin] Manual publisher trigger initiated');

  try {
    const result = await publishDueContent({
      db,
      maxBatchSize: 100,
    });

    res.json({
      published: result.published.length,
      failed: result.failed.length,
      publishedIds: result.published,
      failedIds: result.failed,
    });
  } catch (err) {
    res.status(500).json({ error: (err as Error).message });
  }
});
```

**Testing with a past-dated schedule:**

```bash
# Set a post to "scheduled" with a past date to test immediately
curl -X PATCH http://localhost:3000/api/content/123/schedule \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{"scheduled_at": "2020-01-01T00:00:00Z"}'

# Then trigger the publisher manually
curl -X POST http://localhost:3000/api/admin/trigger-publisher \
  -H "Authorization: Bearer $ADMIN_JWT"
```

---

## Monitoring

Add basic telemetry to the cron job:

```typescript
// Track last run time and publish counts for a /health endpoint
const publisherStats = {
  lastRun: null as Date | null,
  lastRunPublished: 0,
  totalPublished: 0,
  totalFailed: 0,
  consecutiveFailures: 0,
};

cron.schedule('* * * * *', async () => {
  const start = Date.now();
  try {
    const result = await publishDueContent({ db, maxBatchSize: 50 });
    publisherStats.lastRun = new Date();
    publisherStats.lastRunPublished = result.published.length;
    publisherStats.totalPublished += result.published.length;
    publisherStats.totalFailed += result.failed.length;
    publisherStats.consecutiveFailures = 0;
  } catch (err) {
    publisherStats.consecutiveFailures++;
    if (publisherStats.consecutiveFailures >= 5) {
      console.error('[ContentPublisher] 5 consecutive failures — alert ops');
      // alertOpsTeam(err);
    }
  }
  console.log(`[ContentPublisher] Run complete in ${Date.now() - start}ms`);
});

// Expose in /health:
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    publisher: publisherStats,
  });
});
```

---

## Common Gotchas

1. **Never store scheduled times in local time** — always UTC in the database. Display conversion happens at the UI layer.
2. **`SKIP LOCKED` requires PostgreSQL 9.5+** — use advisory locks for older PG versions.
3. **Cron doesn't fire if the server is down** — for critical scheduling, add a startup recovery pass that checks for overdue scheduled posts and publishes them immediately.
4. **Memory leaks from uncleaned cron tasks** — always call `task.stop()` in shutdown handlers and test suites.
5. **node-cron runs in server process** — if you scale horizontally (multiple dynos/containers), every instance runs the cron. The `SELECT FOR UPDATE SKIP LOCKED` pattern prevents double-publishing. Advisory locks prevent duplicate processing at the application level.
6. **1-minute resolution means up to 59s delay** — this is acceptable for blog posts. For time-critical scheduling (newsletters, flash sales), run the cron every 15 or 30 seconds: `'*/30 * * * * *'` (with seconds enabled).
