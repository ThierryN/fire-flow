# Content Branch Preview

> Edit content on a draft version — preview it at a staging URL — approve to go live
---

## Overview

Content branching lets editors work on a "draft copy" of any content without affecting what's live. They can preview their changes, share the preview link with approvers, and publish when ready. Think of it as "pull requests for content."

**Why this matters for non-technical users:**
- A teacher edits a lesson → students still see the current version
- An admin reviews the draft → shares preview link with pastor
- Pastor approves → one click to publish
- If something goes wrong → one click to revert

**Key difference from TinaCMS:**
TinaCMS uses actual git branches. We use **database-level versioning** — same concept, no git knowledge required. Works with MySQL and PostgreSQL.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Content Record: "Introduction to Prayer"       │
│                                                  │
│  ┌─────────────┐    ┌──────────────┐            │
│  │ LIVE v3     │    │ DRAFT v4     │            │
│  │ (published) │    │ (editing)    │            │
│  │             │    │              │            │
│  │ Students    │    │ Preview URL  │            │
│  │ see this    │    │ /preview/abc │            │
│  └─────────────┘    └──────────────┘            │
│                          │                       │
│                     [Approve]                    │
│                          │                       │
│                     DRAFT v4 → LIVE v4           │
│                     (old LIVE v3 → archived)     │
└─────────────────────────────────────────────────┘
```

---

## Database Schema

### MySQL

```sql
-- Content versions table — stores every version of every content record
CREATE TABLE content_versions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  content_type VARCHAR(64) NOT NULL,       -- 'lesson', 'course', 'announcement'
  content_id VARCHAR(36) NOT NULL,         -- ID of the original record
  version_number INT NOT NULL DEFAULT 1,
  status ENUM('draft', 'in_review', 'approved', 'live', 'archived') DEFAULT 'draft',
  data JSON NOT NULL,                      -- Full snapshot of all fields
  preview_token VARCHAR(64) UNIQUE,        -- Random token for preview URL
  created_by VARCHAR(36) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  published_at TIMESTAMP NULL,
  reviewed_by VARCHAR(36) NULL,
  review_note TEXT NULL,

  INDEX idx_content (content_type, content_id),
  INDEX idx_status (status),
  INDEX idx_preview (preview_token),
  UNIQUE INDEX idx_unique_version (content_type, content_id, version_number),
  FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### PostgreSQL

```sql
CREATE TYPE content_version_status AS ENUM ('draft', 'in_review', 'approved', 'live', 'archived');

CREATE TABLE content_versions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  content_type VARCHAR(64) NOT NULL,
  content_id UUID NOT NULL,
  version_number INT NOT NULL DEFAULT 1,
  status content_version_status DEFAULT 'draft',
  data JSONB NOT NULL,
  preview_token VARCHAR(64) UNIQUE,
  created_by UUID NOT NULL REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  published_at TIMESTAMPTZ,
  reviewed_by UUID REFERENCES users(id),
  review_note TEXT
);

CREATE INDEX idx_cv_content ON content_versions(content_type, content_id);
CREATE INDEX idx_cv_status ON content_versions(status);
CREATE UNIQUE INDEX idx_cv_unique ON content_versions(content_type, content_id, version_number);
```

---

## Content Version Service

```js
// server/services/contentVersionService.js
const crypto = require('crypto');

class ContentVersionService {
  constructor(db) {
    this.db = db;
  }

  /**
   * Create a new draft version of existing content.
   * Snapshots the current live data into a new draft record.
   */
  async createDraft(contentType, contentId, userId) {
    // Get the current live version's data
    const [live] = await this.db.query(
      `SELECT * FROM ${contentType} WHERE id = ?`,
      [contentId]
    );

    if (!live) throw new Error(`${contentType} ${contentId} not found`);

    // Get next version number
    const [{ maxVersion }] = await this.db.query(
      `SELECT COALESCE(MAX(version_number), 0) as maxVersion
       FROM content_versions
       WHERE content_type = ? AND content_id = ?`,
      [contentType, contentId]
    );

    const versionNumber = maxVersion + 1;
    const previewToken = crypto.randomBytes(32).toString('hex');

    await this.db.query(
      `INSERT INTO content_versions
       (content_type, content_id, version_number, status, data, preview_token, created_by)
       VALUES (?, ?, ?, 'draft', ?, ?, ?)`,
      [contentType, contentId, versionNumber, JSON.stringify(live), previewToken, userId]
    );

    return { versionNumber, previewToken };
  }

  /**
   * Update a draft version's data.
   */
  async updateDraft(contentType, contentId, versionNumber, updates, userId) {
    const [version] = await this.db.query(
      `SELECT * FROM content_versions
       WHERE content_type = ? AND content_id = ? AND version_number = ? AND status = 'draft'`,
      [contentType, contentId, versionNumber]
    );

    if (!version) throw new Error('Draft not found or not editable');

    const currentData = typeof version.data === 'string' ? JSON.parse(version.data) : version.data;
    const newData = { ...currentData, ...updates };

    await this.db.query(
      `UPDATE content_versions SET data = ?
       WHERE content_type = ? AND content_id = ? AND version_number = ?`,
      [JSON.stringify(newData), contentType, contentId, versionNumber]
    );

    return newData;
  }

  /**
   * Submit a draft for review.
   */
  async submitForReview(contentType, contentId, versionNumber) {
    await this.db.query(
      `UPDATE content_versions SET status = 'in_review'
       WHERE content_type = ? AND content_id = ? AND version_number = ? AND status = 'draft'`,
      [contentType, contentId, versionNumber]
    );
  }

  /**
   * Approve a version (reviewer action).
   */
  async approve(contentType, contentId, versionNumber, reviewerId, note = '') {
    await this.db.query(
      `UPDATE content_versions
       SET status = 'approved', reviewed_by = ?, review_note = ?
       WHERE content_type = ? AND content_id = ? AND version_number = ? AND status = 'in_review'`,
      [reviewerId, note, contentType, contentId, versionNumber]
    );
  }

  /**
   * Publish an approved version — makes it live and archives the old live version.
   */
  async publish(contentType, contentId, versionNumber) {
    const [version] = await this.db.query(
      `SELECT * FROM content_versions
       WHERE content_type = ? AND content_id = ? AND version_number = ?
       AND status IN ('approved', 'draft')`,
      [contentType, contentId, versionNumber]
    );

    if (!version) throw new Error('Version not found or not publishable');

    const data = typeof version.data === 'string' ? JSON.parse(version.data) : version.data;

    // Archive current live version
    await this.db.query(
      `UPDATE content_versions SET status = 'archived'
       WHERE content_type = ? AND content_id = ? AND status = 'live'`,
      [contentType, contentId]
    );

    // Mark this version as live
    await this.db.query(
      `UPDATE content_versions
       SET status = 'live', published_at = NOW()
       WHERE content_type = ? AND content_id = ? AND version_number = ?`,
      [contentType, contentId, versionNumber]
    );

    // Update the actual content table
    const fields = Object.keys(data).filter((k) => k !== 'id' && k !== 'created_at');
    const setClauses = fields.map((f) => `${f} = ?`);
    const values = [...fields.map((f) => data[f]), contentId];

    await this.db.query(
      `UPDATE ${contentType} SET ${setClauses.join(', ')}, updated_at = NOW() WHERE id = ?`,
      values
    );

    return data;
  }

  /**
   * Revert to a previous version.
   */
  async revert(contentType, contentId, targetVersionNumber) {
    return this.publish(contentType, contentId, targetVersionNumber);
  }

  /**
   * Get a version by preview token (for preview URLs).
   */
  async getByPreviewToken(previewToken) {
    const [version] = await this.db.query(
      `SELECT * FROM content_versions WHERE preview_token = ?`,
      [previewToken]
    );

    if (!version) throw new Error('Preview not found');

    return {
      ...version,
      data: typeof version.data === 'string' ? JSON.parse(version.data) : version.data,
    };
  }

  /**
   * List all versions of a content record.
   */
  async listVersions(contentType, contentId) {
    return this.db.query(
      `SELECT cv.*, u.name as author_name
       FROM content_versions cv
       JOIN users u ON cv.created_by = u.id
       WHERE cv.content_type = ? AND cv.content_id = ?
       ORDER BY cv.version_number DESC`,
      [contentType, contentId]
    );
  }
}

module.exports = ContentVersionService;
```

---

## API Routes

```js
// server/routes/contentVersions.js
const ContentVersionService = require('../services/contentVersionService');

const versionService = new ContentVersionService(db);

// Create a new draft
router.post('/api/content/:type/:id/draft', authenticate, authorize(['admin', 'teacher']), async (req, res) => {
  const result = await versionService.createDraft(req.params.type, req.params.id, req.user.id);
  const previewUrl = `${req.protocol}://${req.get('host')}/preview/${result.previewToken}`;
  res.json({ ...result, previewUrl });
});

// Update draft
router.patch('/api/content/:type/:id/version/:version', authenticate, authorize(['admin', 'teacher']), async (req, res) => {
  const data = await versionService.updateDraft(
    req.params.type, req.params.id, parseInt(req.params.version), req.body, req.user.id
  );
  res.json(data);
});

// Submit for review
router.post('/api/content/:type/:id/version/:version/submit', authenticate, authorize(['admin', 'teacher']), async (req, res) => {
  await versionService.submitForReview(req.params.type, req.params.id, parseInt(req.params.version));
  res.json({ message: 'Submitted for review' });
});

// Approve
router.post('/api/content/:type/:id/version/:version/approve', authenticate, authorize(['admin']), async (req, res) => {
  await versionService.approve(
    req.params.type, req.params.id, parseInt(req.params.version), req.user.id, req.body.note
  );
  res.json({ message: 'Approved' });
});

// Publish
router.post('/api/content/:type/:id/version/:version/publish', authenticate, authorize(['admin']), async (req, res) => {
  const data = await versionService.publish(req.params.type, req.params.id, parseInt(req.params.version));
  res.json({ message: 'Published', data });
});

// Preview (public — uses token, no auth needed)
router.get('/preview/:token', async (req, res) => {
  const version = await versionService.getByPreviewToken(req.params.token);
  res.json({ preview: true, ...version });
});

// Version history
router.get('/api/content/:type/:id/versions', authenticate, async (req, res) => {
  const versions = await versionService.listVersions(req.params.type, req.params.id);
  res.json(versions);
});
```

---

## React: Version History Panel

```jsx
// components/cms/VersionHistory.jsx
import { useState, useEffect } from 'react';

export default function VersionHistory({ contentType, contentId, onPreview, onPublish, onRevert }) {
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/content/${contentType}/${contentId}/versions`)
      .then((r) => r.json())
      .then(setVersions)
      .finally(() => setLoading(false));
  }, [contentType, contentId]);

  if (loading) return <div>Loading version history...</div>;

  const statusColors = {
    draft: '#f59e0b',
    in_review: '#8b5cf6',
    approved: '#10b981',
    live: '#3b82f6',
    archived: '#6b7280',
  };

  return (
    <div style={{ maxWidth: '600px' }}>
      <h3>Version History</h3>
      {versions.map((v) => (
        <div
          key={v.version_number}
          style={{
            padding: '12px',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            marginBottom: '8px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div>
            <strong>v{v.version_number}</strong>
            <span
              style={{
                background: statusColors[v.status],
                color: 'white',
                padding: '2px 8px',
                borderRadius: '12px',
                fontSize: '12px',
                marginLeft: '8px',
              }}
            >
              {v.status}
            </span>
            <div style={{ color: '#6b7280', fontSize: '13px', marginTop: '4px' }}>
              by {v.author_name} | {new Date(v.created_at).toLocaleDateString()}
            </div>
          </div>
          <div style={{ display: 'flex', gap: '6px' }}>
            {v.preview_token && (
              <button onClick={() => onPreview(v.preview_token)} style={btnStyle}>
                Preview
              </button>
            )}
            {v.status === 'approved' && (
              <button onClick={() => onPublish(v.version_number)} style={{ ...btnStyle, background: '#10b981' }}>
                Publish
              </button>
            )}
            {v.status === 'archived' && (
              <button onClick={() => onRevert(v.version_number)} style={{ ...btnStyle, background: '#f59e0b' }}>
                Revert
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

const btnStyle = {
  background: '#3b82f6',
  color: 'white',
  border: 'none',
  padding: '4px 12px',
  borderRadius: '4px',
  cursor: 'pointer',
  fontSize: '13px',
};
```

---

## Preview Page Component

```jsx
// pages/PreviewPage.jsx
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

export default function PreviewPage() {
  const { token } = useParams();
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/preview/${token}`)
      .then((r) => r.json())
      .then(setPreview)
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) return <div>Loading preview...</div>;
  if (!preview) return <div>Preview not found or expired.</div>;

  return (
    <div>
      {/* Preview banner */}
      <div
        style={{
          background: '#fef3c7',
          border: '1px solid #f59e0b',
          padding: '12px 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          position: 'sticky',
          top: 0,
          zIndex: 1000,
        }}
      >
        <span>
          <strong>PREVIEW MODE</strong> — Version {preview.version_number} ({preview.status})
        </span>
        <span style={{ color: '#92400e', fontSize: '13px' }}>
          This is not the live version. Only people with this link can see it.
        </span>
      </div>

      {/* Render the content using preview data */}
      <article style={{ maxWidth: '800px', margin: '40px auto', padding: '0 20px' }}>
        <h1>{preview.data.title}</h1>
        {preview.data.subtitle && <p style={{ color: '#6b7280' }}>{preview.data.subtitle}</p>}
        {preview.data.cover_image && (
          <img src={preview.data.cover_image} alt="" style={{ width: '100%', borderRadius: '8px' }} />
        )}
        <div>{preview.data.body}</div>
      </article>
    </div>
  );
}
```

---

## Integration With Existing Skills

| Skill | How It Connects |
|-------|----------------|
| `content-publishing-states.md` | Version status maps to the state machine (draft→in_review→published) |
| `inline-visual-editing.md` | Inline edits save to the draft version, not live |
| `scheduled-content-publishing.md` | Schedule a version to auto-publish at a future date |

---

## When to Use Content Branching

**Use it for:**
- Lessons and courses (high-impact content, needs review)
- Landing pages and announcements
- Any content that goes through an approval workflow

**Skip it for:**
- Chat messages and comments (ephemeral, no review needed)
- User profile updates (personal, no approval needed)
- System settings (admin-only, no preview needed)
