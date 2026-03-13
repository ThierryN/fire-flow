---
name: broadcast-scheduler-shared-execute-function
category: api-patterns
version: 1.0.0
contributed: 2026-02-21
contributor: my-other-project
last_updated: 2026-02-21
tags: [node.js, cron, scheduler, broadcast, express, dry]
difficulty: easy
usage_count: 1
success_rate: 100
---

# Broadcast Scheduler: Shared Execute Function

## Problem

When building a feature that can be triggered both **immediately** (by an admin action) and **on a schedule** (by a cron job), naively duplicating the execution logic creates two maintenance surfaces. If the logic changes, you must update it in two places and keep them in sync.

Typical anti-pattern:

```js
// broadcastController.js — duplicate logic
export const sendNow = async (req, res) => {
  const announcement = await BroadcastAnnouncement.getAnnouncementById(req.params.id);
  if (announcement.send_popup) socketService.broadcastAnnouncement(announcement);
  if (announcement.send_email) await sendBroadcastEmail(announcement);
  await BroadcastAnnouncement.markAsSent(announcement.id, count);
};

// broadcastSchedulerJob.js — same logic duplicated
cron.schedule('* * * * *', async () => {
  const due = await getDueAnnouncements();
  for (const a of due) {
    if (a.send_popup) socketService.broadcastAnnouncement(a);
    if (a.send_email) await sendBroadcastEmail(a);
    await BroadcastAnnouncement.markAsSent(a.id, count);
  }
});
```

## Solution Pattern

Export the execution logic as a named function from the **scheduler job file**. Both the cron handler AND the controller import and call the same function. The cron job calls it for scheduled items; the controller calls it directly for "Send Now."

This makes the scheduler job the **single source of truth** for how a broadcast is executed.

## Code Example

```js
// server/jobs/broadcastSchedulerJob.js

import cron from 'node-cron';
import { getDueAnnouncements, markAsSent } from '../models/BroadcastAnnouncement.pg.js';
import { sendBroadcastEmail } from '../services/broadcastEmailService.js';
import socketService from '../services/SocketService.js';

let schedulerStarted = false;

export const startBroadcastScheduler = () => {
  if (schedulerStarted) return;
  schedulerStarted = true;

  cron.schedule('* * * * *', async () => {
    try {
      const due = await getDueAnnouncements();
      for (const announcement of due) {
        await executeSend(announcement); // Uses shared function
      }
    } catch (err) {
      console.error('[BroadcastScheduler] Error:', err.message);
    }
  });
};

// EXPORTED — both scheduler and controller call this
export const executeSend = async (announcement) => {
  let recipientCount = 0;

  if (announcement.send_popup || announcement.send_in_app) {
    socketService.broadcastAnnouncement(announcement);
  }

  if (announcement.send_email) {
    const result = await sendBroadcastEmail(announcement);
    recipientCount = result.sent;
  }

  await markAsSent(announcement.id, recipientCount);
};
```

```js
// server/controllers/broadcastController.js

import { executeSend } from '../jobs/broadcastSchedulerJob.js';

export const sendNow = async (req, res) => {
  const announcement = await BroadcastAnnouncement.getAnnouncementById(req.params.id);
  if (!announcement) return res.status(404).json({ success: false, message: 'Not found' });
  if (announcement.status === 'sent') {
    return res.status(400).json({ success: false, message: 'Already sent' });
  }

  // Set status to 'sending' first to prevent duplicate sends by the cron job
  await BroadcastAnnouncement.updateAnnouncement(req.params.id, { status: 'sending' });

  // Fire async — don't await (email delivery can take time for large lists)
  executeSend(announcement).catch(err =>
    console.error('[Broadcast] sendNow error:', err.message)
  );

  res.json({ success: true, message: 'Announcement sending' });
};
```

## Implementation Steps

1. Write the execution logic as a standalone async function `executeSend(item)` in the scheduler file
2. Export it with `export const executeSend = async (item) => { ... }`
3. Import it in the controller: `import { executeSend } from '../jobs/schedulerJob.js'`
4. In the controller's "Send Now" handler, set status to `'sending'` (or equivalent) **before** calling `executeSend()` — this prevents the cron job from double-sending the same item in the next minute
5. Call `executeSend()` without `await` in the controller (fire-and-forget), since large email sends could take minutes

## When to Use

- Any feature where items can be sent/triggered both immediately AND on a schedule
- Email newsletters, announcement broadcasts, report generation jobs
- Any pattern where "send now" is a button in the UI AND a cron job checks a DB table

## When NOT to Use

- When the immediate vs. scheduled paths have meaningfully different logic (e.g., different recipients, different templates)
- When the job file has no natural ownership of the logic (put `executeSend` in a service instead)

## Common Mistakes

- **Forgetting the status guard**: Without setting status to `'sending'` before firing, the cron job running in the same minute will double-execute
- **Awaiting in controller**: `executeSend()` may take minutes for large email batches — fire-and-forget with `.catch()` for error logging
- **Circular imports**: If the model imports from the scheduler (or vice versa), you'll get circular dependency errors. Keep the data layer (model) import-free from job files.

## Related Skills

- [EXPRESS_ROUTE_ORDERING_MIDDLEWARE_INTERCEPTION.md](../api-patterns/EXPRESS_ROUTE_ORDERING_MIDDLEWARE_INTERCEPTION.md) — Static routes before dynamic `:id` params
- [PODCAST_PROGRESS_TRACKING_THREE_ROOT_CAUSES.md](../api-patterns/PODCAST_PROGRESS_TRACKING_THREE_ROOT_CAUSES.md)

## References

- Contributed from: my-other-project, Phase 15 Broadcast Announcements (2026-02-21)
- Pattern: DRY principle applied to scheduler/controller shared logic
