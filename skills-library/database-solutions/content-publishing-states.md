# Content Publishing State Machine

> Production-ready content lifecycle management: DRAFT → IN_REVIEW → SCHEDULED → PUBLISHED → ARCHIVED with full audit trail.

**When to use:** Any CMS, blog engine, LMS, or content platform where content has a lifecycle with approval gates, scheduled publishing, and rollback capability.
**Stack:** PostgreSQL or MySQL, Node.js/Express or Bun, TypeScript, React

---

## State Machine Overview

```
                ┌─────────┐
                │  DRAFT  │◄────────────────────────────┐
                └────┬────┘                             │
                     │ submit_for_review                │ request_changes
                     ▼                                  │
              ┌───────────┐                    ┌────────┴────────┐
              │ IN_REVIEW │────────────────────►│   (back draft)  │
              └─────┬─────┘                    └─────────────────┘
                    │ approve                         ▲
          ┌─────────┼──────────┐                     │ unschedule
          │         │          │                     │
          ▼         ▼          ▼                     │
      publish   schedule   reject               ┌────┴─────┐
          │    (future)        │                │ SCHEDULED │
          │         │          │                └──────┬────┘
          │         └──────────┼─────────────────►     │ (cron fires)
          │                    │                       │
          ▼                    ▼                       ▼
   ┌───────────┐         ┌──────────┐          ┌───────────┐
   │ PUBLISHED │         │ REJECTED │          │ PUBLISHED │
   └─────┬─────┘         └──────────┘          └─────┬─────┘
         │ archive                                    │ archive
         ▼                                            ▼
   ┌──────────┐                               ┌──────────┐
   │ ARCHIVED │                               │ ARCHIVED │
   └──────────┘                               └──────────┘
```

**Valid transitions:**

| From | To | Action |
|------|----|--------|
| DRAFT | IN_REVIEW | submit_for_review |
| IN_REVIEW | DRAFT | request_changes |
| IN_REVIEW | SCHEDULED | approve + schedule date |
| IN_REVIEW | PUBLISHED | approve + publish now |
| IN_REVIEW | REJECTED | reject |
| SCHEDULED | PUBLISHED | cron fires (auto) |
| SCHEDULED | DRAFT | unschedule |
| PUBLISHED | ARCHIVED | archive |
| ARCHIVED | DRAFT | restore (creates new draft) |

---

## Database Schema

### PostgreSQL

```sql
-- Status enum
CREATE TYPE content_status AS ENUM (
  'draft',
  'in_review',
  'scheduled',
  'published',
  'archived',
  'rejected'
);

-- Content table
CREATE TABLE content (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title           TEXT NOT NULL DEFAULT '',
  slug            TEXT UNIQUE,
  body            TEXT NOT NULL DEFAULT '',
  excerpt         TEXT,
  featured_image  TEXT,
  tags            TEXT[] DEFAULT '{}',
  content_type    TEXT NOT NULL DEFAULT 'post',   -- post, page, lesson, etc.

  -- State machine fields
  status          content_status NOT NULL DEFAULT 'draft',
  published_at    TIMESTAMPTZ,                    -- actual publish time
  scheduled_at    TIMESTAMPTZ,                    -- future publish time
  archived_at     TIMESTAMPTZ,

  -- Authorship
  author_id       UUID NOT NULL REFERENCES users(id),
  created_by      UUID NOT NULL REFERENCES users(id),
  updated_by      UUID REFERENCES users(id),
  reviewed_by     UUID REFERENCES users(id),

  -- Review fields
  review_notes    TEXT,                           -- reviewer feedback
  rejection_reason TEXT,

  -- Metadata
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Constraints
  CONSTRAINT published_requires_slug
    CHECK (status != 'published' OR slug IS NOT NULL),
  CONSTRAINT scheduled_requires_date
    CHECK (status != 'scheduled' OR scheduled_at IS NOT NULL),
  CONSTRAINT scheduled_date_in_future
    CHECK (status != 'scheduled' OR scheduled_at > NOW() - INTERVAL '1 minute')
);

-- Indexes
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_scheduled ON content(scheduled_at) WHERE status = 'scheduled';
CREATE INDEX idx_content_author ON content(author_id, status);
CREATE INDEX idx_content_published ON content(published_at DESC) WHERE status = 'published';

-- Audit log table
CREATE TABLE content_status_history (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content_id   UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,
  from_status  content_status,
  to_status    content_status NOT NULL,
  changed_by   UUID NOT NULL REFERENCES users(id),
  changed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  notes        TEXT,                              -- why the change was made
  metadata     JSONB DEFAULT '{}'                -- extra context (IP, etc.)
);

CREATE INDEX idx_status_history_content ON content_status_history(content_id, changed_at DESC);
```

### MySQL Equivalent

```sql
-- MySQL uses ENUM column type (no separate CREATE TYPE)
CREATE TABLE content (
  id              CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  title           TEXT NOT NULL,
  slug            VARCHAR(255) UNIQUE,
  body            LONGTEXT NOT NULL,
  excerpt         TEXT,
  tags            JSON DEFAULT ('[]'),
  content_type    VARCHAR(50) NOT NULL DEFAULT 'post',

  -- State machine fields
  status          ENUM('draft','in_review','scheduled','published','archived','rejected')
                  NOT NULL DEFAULT 'draft',
  published_at    DATETIME,
  scheduled_at    DATETIME,
  archived_at     DATETIME,

  -- Authorship
  author_id       CHAR(36) NOT NULL,
  created_by      CHAR(36) NOT NULL,
  updated_by      CHAR(36),
  reviewed_by     CHAR(36),
  review_notes    TEXT,
  rejection_reason TEXT,

  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_content_author FOREIGN KEY (author_id) REFERENCES users(id)
);

CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_scheduled ON content(scheduled_at, status);
```

---

## State Transition Validator (TypeScript)

```typescript
// lib/content-state-machine.ts

export type ContentStatus =
  | 'draft'
  | 'in_review'
  | 'scheduled'
  | 'published'
  | 'archived'
  | 'rejected';

export type TransitionAction =
  | 'submit_for_review'
  | 'request_changes'
  | 'approve_and_publish'
  | 'approve_and_schedule'
  | 'reject'
  | 'unschedule'
  | 'archive'
  | 'restore';

interface Transition {
  from: ContentStatus[];
  to: ContentStatus;
  requiredRole?: string[];      // roles allowed to perform this transition
  guard?: (content: ContentRecord) => string | null;  // returns error or null
}

interface ContentRecord {
  id: string;
  title: string;
  slug: string | null;
  status: ContentStatus;
  scheduled_at?: Date | null;
}

const TRANSITIONS: Record<TransitionAction, Transition> = {
  submit_for_review: {
    from: ['draft', 'rejected'],
    to: 'in_review',
    guard: (c) => {
      if (!c.title?.trim()) return 'Title is required before submitting for review';
      return null;
    },
  },
  request_changes: {
    from: ['in_review'],
    to: 'draft',
    requiredRole: ['editor', 'admin'],
  },
  approve_and_publish: {
    from: ['in_review'],
    to: 'published',
    requiredRole: ['editor', 'admin'],
    guard: (c) => {
      if (!c.title?.trim()) return 'Title is required to publish';
      if (!c.slug?.trim()) return 'Slug is required to publish';
      return null;
    },
  },
  approve_and_schedule: {
    from: ['in_review'],
    to: 'scheduled',
    requiredRole: ['editor', 'admin'],
    guard: (c) => {
      if (!c.title?.trim()) return 'Title is required to schedule';
      if (!c.slug?.trim()) return 'Slug is required to schedule';
      if (!c.scheduled_at) return 'Scheduled date is required';
      if (new Date(c.scheduled_at) <= new Date()) return 'Scheduled date must be in the future';
      return null;
    },
  },
  reject: {
    from: ['in_review'],
    to: 'rejected',
    requiredRole: ['editor', 'admin'],
  },
  unschedule: {
    from: ['scheduled'],
    to: 'draft',
  },
  archive: {
    from: ['published'],
    to: 'archived',
    requiredRole: ['editor', 'admin'],
  },
  restore: {
    from: ['archived'],
    to: 'draft',
    requiredRole: ['editor', 'admin'],
  },
};

export function validateTransition(
  action: TransitionAction,
  content: ContentRecord,
  userRole: string
): { valid: boolean; error?: string } {
  const transition = TRANSITIONS[action];

  if (!transition) {
    return { valid: false, error: `Unknown action: ${action}` };
  }

  if (!transition.from.includes(content.status)) {
    return {
      valid: false,
      error: `Cannot ${action} from status '${content.status}'. ` +
             `Valid from: ${transition.from.join(', ')}`,
    };
  }

  if (transition.requiredRole && !transition.requiredRole.includes(userRole)) {
    return {
      valid: false,
      error: `Role '${userRole}' cannot perform '${action}'. ` +
             `Required: ${transition.requiredRole.join(' or ')}`,
    };
  }

  if (transition.guard) {
    const guardError = transition.guard(content);
    if (guardError) return { valid: false, error: guardError };
  }

  return { valid: true };
}

export function getTargetStatus(action: TransitionAction): ContentStatus {
  return TRANSITIONS[action].to;
}
```

---

## Express Middleware

```typescript
// middleware/content-transition.ts
import { Request, Response, NextFunction } from 'express';
import { validateTransition, TransitionAction } from '../lib/content-state-machine';

export function requireValidTransition(action: TransitionAction) {
  return async (req: Request, res: Response, next: NextFunction) => {
    const { id } = req.params;
    const userRole = req.user?.role ?? 'author';

    const content = await db.query(
      'SELECT id, title, slug, status, scheduled_at FROM content WHERE id = $1',
      [id]
    );

    if (!content.rows[0]) {
      return res.status(404).json({ error: 'Content not found' });
    }

    const result = validateTransition(action, content.rows[0], userRole);

    if (!result.valid) {
      return res.status(422).json({ error: result.error });
    }

    // Attach to request for the route handler
    req.contentRecord = content.rows[0];
    next();
  };
}
```

---

## API Endpoints

```typescript
// routes/content-transitions.ts
import { Router } from 'express';
import { requireValidTransition } from '../middleware/content-transition';
import { getTargetStatus } from '../lib/content-state-machine'; // getTargetStatus is exported from lib, not middleware
import { logStatusChange } from '../lib/audit-log';

const router = Router();

// Publish immediately
router.patch(
  '/content/:id/publish',
  requireValidTransition('approve_and_publish'),
  async (req, res) => {
    const { id } = req.params;
    const { notes } = req.body;
    const now = new Date();

    await db.query(`
      UPDATE content SET
        status = 'published',
        published_at = $1,
        scheduled_at = NULL,
        reviewed_by = $2,
        updated_by = $2,
        updated_at = $1
      WHERE id = $3
    `, [now, req.user.id, id]);

    await logStatusChange(db, {
      contentId: id,
      fromStatus: req.contentRecord.status,
      toStatus: 'published',
      changedBy: req.user.id,
      notes,
    });

    res.json({ status: 'published', published_at: now });
  }
);

// Schedule for future publication
router.patch(
  '/content/:id/schedule',
  requireValidTransition('approve_and_schedule'),
  async (req, res) => {
    const { id } = req.params;
    const { scheduled_at, notes } = req.body;

    if (!scheduled_at) {
      return res.status(400).json({ error: 'scheduled_at is required' });
    }

    const scheduleDate = new Date(scheduled_at);
    if (scheduleDate <= new Date()) {
      return res.status(400).json({ error: 'scheduled_at must be in the future' });
    }

    await db.query(`
      UPDATE content SET
        status = 'scheduled',
        scheduled_at = $1,
        reviewed_by = $2,
        updated_by = $2,
        updated_at = NOW()
      WHERE id = $3
    `, [scheduleDate, req.user.id, id]);

    await logStatusChange(db, {
      contentId: id,
      fromStatus: req.contentRecord.status,
      toStatus: 'scheduled',
      changedBy: req.user.id,
      notes,
      metadata: { scheduled_at: scheduleDate },
    });

    res.json({ status: 'scheduled', scheduled_at: scheduleDate });
  }
);

// Archive
router.patch(
  '/content/:id/archive',
  requireValidTransition('archive'),
  async (req, res) => {
    const { id } = req.params;

    await db.query(`
      UPDATE content SET
        status = 'archived',
        archived_at = NOW(),
        updated_by = $1,
        updated_at = NOW()
      WHERE id = $2
    `, [req.user.id, id]);

    await logStatusChange(db, {
      contentId: id,
      fromStatus: req.contentRecord.status,
      toStatus: 'archived',
      changedBy: req.user.id,
    });

    res.json({ status: 'archived' });
  }
);

// Submit for review
router.patch(
  '/content/:id/submit',
  requireValidTransition('submit_for_review'),
  async (req, res) => {
    const { id } = req.params;

    await db.query(`
      UPDATE content SET
        status = 'in_review',
        updated_by = $1,
        updated_at = NOW()
      WHERE id = $2
    `, [req.user.id, id]);

    await logStatusChange(db, {
      contentId: id,
      fromStatus: req.contentRecord.status,
      toStatus: 'in_review',
      changedBy: req.user.id,
    });

    res.json({ status: 'in_review' });
  }
);

export default router;
```

---

## Audit Log Helper

```typescript
// lib/audit-log.ts
import { Pool } from 'pg';
import { ContentStatus } from './content-state-machine';

interface LogEntry {
  contentId: string;
  fromStatus: ContentStatus | null;
  toStatus: ContentStatus;
  changedBy: string;
  notes?: string;
  metadata?: Record<string, unknown>;
}

export async function logStatusChange(db: Pool, entry: LogEntry): Promise<void> {
  await db.query(`
    INSERT INTO content_status_history
      (content_id, from_status, to_status, changed_by, notes, metadata)
    VALUES ($1, $2, $3, $4, $5, $6)
  `, [
    entry.contentId,
    entry.fromStatus,
    entry.toStatus,
    entry.changedBy,
    entry.notes ?? null,
    JSON.stringify(entry.metadata ?? {}),
  ]);
}

export async function getContentHistory(db: Pool, contentId: string) {
  const { rows } = await db.query(`
    SELECT
      h.from_status,
      h.to_status,
      h.changed_at,
      h.notes,
      u.name AS changed_by_name,
      u.email AS changed_by_email
    FROM content_status_history h
      JOIN users u ON u.id = h.changed_by
    WHERE h.content_id = $1
    ORDER BY h.changed_at DESC
  `, [contentId]);

  return rows;
}
```

---

## React Status Badge Component

```tsx
// components/ContentStatusBadge.tsx
import React from 'react';

type ContentStatus = 'draft' | 'in_review' | 'scheduled' | 'published' | 'archived' | 'rejected';

const STATUS_CONFIG: Record<ContentStatus, { label: string; className: string }> = {
  draft:     { label: 'Draft',       className: 'bg-gray-100 text-gray-700 border-gray-300' },
  in_review: { label: 'In Review',   className: 'bg-yellow-100 text-yellow-800 border-yellow-300' },
  scheduled: { label: 'Scheduled',   className: 'bg-blue-100 text-blue-800 border-blue-300' },
  published: { label: 'Published',   className: 'bg-green-100 text-green-800 border-green-300' },
  archived:  { label: 'Archived',    className: 'bg-slate-100 text-slate-600 border-slate-300' },
  rejected:  { label: 'Rejected',    className: 'bg-red-100 text-red-700 border-red-300' },
};

interface Props {
  status: ContentStatus;
  scheduledAt?: string | null;
  size?: 'sm' | 'md';
}

export function ContentStatusBadge({ status, scheduledAt, size = 'md' }: Props) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.draft;
  const sizeClass = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1';

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${sizeClass} ${config.className}`}>
      <StatusDot status={status} />
      {config.label}
      {status === 'scheduled' && scheduledAt && (
        <span className="text-xs font-normal ml-1">
          ({new Date(scheduledAt).toLocaleDateString()})
        </span>
      )}
    </span>
  );
}

function StatusDot({ status }: { status: ContentStatus }) {
  const dotColors: Record<ContentStatus, string> = {
    draft:     'bg-gray-400',
    in_review: 'bg-yellow-500 animate-pulse',
    scheduled: 'bg-blue-500',
    published: 'bg-green-500',
    archived:  'bg-slate-400',
    rejected:  'bg-red-500',
  };

  return (
    <span className={`w-1.5 h-1.5 rounded-full ${dotColors[status]}`} />
  );
}
```

---

## Guard Clause Reference

These are the business rules enforced by the state machine:

```
DRAFT → IN_REVIEW:
  ✓ Title must not be empty

IN_REVIEW → PUBLISHED:
  ✓ Title must not be empty
  ✓ Slug must exist and be unique
  ✓ User must have role: editor or admin

IN_REVIEW → SCHEDULED:
  ✓ Title must not be empty
  ✓ Slug must exist
  ✓ scheduled_at must be provided
  ✓ scheduled_at must be in the future
  ✓ User must have role: editor or admin

PUBLISHED → ARCHIVED:
  ✓ User must have role: editor or admin
  ✗ Cannot archive a scheduled post (unschedule first)
  ✗ Cannot publish without first unpublishing (use restore → draft flow)
```

---

## Common Gotchas

1. **Don't use booleans** (`is_published`, `is_draft`) — they can't express multi-state workflows and create contradictory states (`is_published = true AND is_draft = true`).
2. **Store `published_at` separately from `scheduled_at`** — `published_at` is the actual publication timestamp (set when the cron fires or when manually published), `scheduled_at` is the intended time.
3. **Soft deletes vs ARCHIVED** — archived content is still in the DB and readable by admins. Don't conflate with deletion.
4. **MySQL ENUM ordering** — MySQL ENUMs have an implicit ordering based on their definition order. This doesn't affect queries but can cause surprising sort behavior. Always sort by explicit column values, not ENUM ordinal.
5. **Audit log is append-only** — never UPDATE or DELETE audit log rows. Add new rows. This is your forensic trail.
