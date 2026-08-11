# Inline Visual Editing

> Click-to-edit content directly on the rendered page — no separate admin form needed
---

## Overview

Inline visual editing lets users click on any piece of content on the **actual rendered page** and edit it in place. Instead of filling out a form in an admin panel, teachers and admins see the real page and type directly on it. Changes save back to the database.

**Key difference from a rich text editor (like TipTap):**
- TipTap = a form field where you type formatted text
- Inline editing = the entire rendered page becomes editable. Click a heading, a paragraph, an image caption — edit it right there

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Rendered Page (what students see)              │
│                                                  │
│  ┌──────────────────────────────────┐           │
│  │ "Introduction to Prayer"    ← click to edit  │
│  │  Welcome to this lesson...  ← click to edit  │
│  │  [image]                    ← click to swap   │
│  └──────────────────────────────────┘           │
│                                                  │
│  ┌────────────────────┐                          │
│  │ Editing Sidebar    │  ← appears on click      │
│  │ Field type: text   │                          │
│  │ [Save] [Cancel]    │                          │
│  └────────────────────┘                          │
└─────────────────────────────────────────────────┘

Data flow:
  1. Page loads → fetches content from API
  2. EditableRegion wraps each content block
  3. User clicks → region becomes editable
  4. User types → local state updates (optimistic)
  5. User saves → PATCH to API → database update
  6. Page re-renders with new content
```

---

## Core Pattern: EditableRegion Component

This is the building block. Wrap any content in `<EditableRegion>` and it becomes click-to-edit.

```jsx
// components/cms/EditableRegion.jsx
import { useState, useRef, useEffect } from 'react';
import DOMPurify from 'dompurify';

/**
 * Wraps any content block to make it click-to-edit.
 *
 * Props:
 *   fieldName  — which database column this maps to (e.g., "title", "body")
 *   value      — current content value
 *   onSave     — async function(fieldName, newValue) => save to API
 *   type       — "text" | "richtext" | "image" | "markdown"
 *   editable   — boolean, false for students (only admins/teachers edit)
 */
export default function EditableRegion({
  fieldName,
  value,
  onSave,
  type = 'text',
  editable = false,
  className = '',
  children,
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState(value);
  const [saving, setSaving] = useState(false);
  const ref = useRef(null);

  // Sync when value changes externally
  useEffect(() => {
    if (!isEditing) setDraft(value);
  }, [value, isEditing]);

  // If not editable (student view), just render children
  if (!editable) return <>{children}</>;

  const handleClick = () => {
    if (!isEditing) setIsEditing(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Sanitize HTML content before saving
      const sanitized = type === 'richtext' ? DOMPurify.sanitize(draft) : draft;
      await onSave(fieldName, sanitized);
      setIsEditing(false);
    } catch (err) {
      console.error(`Failed to save ${fieldName}:`, err);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setDraft(value);
    setIsEditing(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') handleCancel();
    if (e.key === 'Enter' && e.ctrlKey && type === 'text') handleSave();
  };

  return (
    <div
      className={`editable-region ${isEditing ? 'editing' : ''} ${className}`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      style={{
        position: 'relative',
        cursor: editable && !isEditing ? 'pointer' : 'default',
        outline: isEditing ? '2px solid #3b82f6' : 'none',
        outlineOffset: '4px',
        borderRadius: '4px',
      }}
    >
      {/* Hover indicator for editable regions */}
      {!isEditing && (
        <div
          className="edit-hint"
          style={{
            position: 'absolute',
            top: '-8px',
            right: '-8px',
            background: '#3b82f6',
            color: 'white',
            borderRadius: '50%',
            width: '24px',
            height: '24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '12px',
            opacity: 0,
            transition: 'opacity 0.2s',
            pointerEvents: 'none',
          }}
        >
          ✎
        </div>
      )}

      {isEditing ? (
        <EditField
          type={type}
          value={draft}
          onChange={setDraft}
          onSave={handleSave}
          onCancel={handleCancel}
          saving={saving}
          ref={ref}
        />
      ) : (
        children
      )}

      {/* CSS for hover effect */}
      <style>{`
        .editable-region:hover .edit-hint { opacity: 1 !important; }
        .editable-region:hover { background: rgba(59, 130, 246, 0.05); }
      `}</style>
    </div>
  );
}
```

---

## Edit Field Renderers (by type)

```jsx
// components/cms/EditField.jsx
import { forwardRef, useEffect, useRef } from 'react';

const EditField = forwardRef(function EditField(
  { type, value, onChange, onSave, onCancel, saving },
  ref
) {
  const inputRef = useRef(null);

  useEffect(() => {
    // Auto-focus when entering edit mode
    if (inputRef.current) {
      inputRef.current.focus();
      // Place cursor at end for text inputs
      if (type === 'text' && inputRef.current.setSelectionRange) {
        const len = (value || '').length;
        inputRef.current.setSelectionRange(len, len);
      }
    }
  }, []);

  const toolbar = (
    <div style={{ marginTop: '8px', display: 'flex', gap: '8px' }}>
      <button
        onClick={onSave}
        disabled={saving}
        style={{
          background: '#3b82f6',
          color: 'white',
          border: 'none',
          padding: '6px 16px',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '13px',
        }}
      >
        {saving ? 'Saving...' : 'Save'}
      </button>
      <button
        onClick={onCancel}
        style={{
          background: '#e5e7eb',
          border: 'none',
          padding: '6px 16px',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '13px',
        }}
      >
        Cancel
      </button>
      <span style={{ color: '#9ca3af', fontSize: '12px', alignSelf: 'center' }}>
        Ctrl+Enter to save | Esc to cancel
      </span>
    </div>
  );

  switch (type) {
    case 'text':
      return (
        <div>
          <input
            ref={inputRef}
            type="text"
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            style={{
              width: '100%',
              fontSize: 'inherit',
              fontFamily: 'inherit',
              fontWeight: 'inherit',
              padding: '4px 8px',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
            }}
          />
          {toolbar}
        </div>
      );

    case 'richtext':
      // For rich text, integrate your TipTap editor here
      // This is where the tiptap-minimal-setup.md skill connects
      return (
        <div>
          <textarea
            ref={inputRef}
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            rows={8}
            style={{
              width: '100%',
              fontSize: 'inherit',
              fontFamily: 'inherit',
              padding: '8px',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
              resize: 'vertical',
            }}
          />
          {toolbar}
        </div>
      );

    case 'image':
      return (
        <div>
          <div style={{ marginBottom: '8px' }}>
            {value && (
              <img
                src={value}
                alt="Current"
                style={{ maxWidth: '200px', borderRadius: '4px' }}
              />
            )}
          </div>
          <input
            ref={inputRef}
            type="text"
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Image URL or upload path"
            style={{
              width: '100%',
              padding: '4px 8px',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
            }}
          />
          {toolbar}
        </div>
      );

    case 'markdown':
      return (
        <div>
          <textarea
            ref={inputRef}
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            rows={12}
            style={{
              width: '100%',
              fontFamily: 'monospace',
              fontSize: '14px',
              padding: '8px',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
              resize: 'vertical',
            }}
          />
          {toolbar}
        </div>
      );

    default:
      return <div>Unsupported field type: {type}</div>;
  }
});

export default EditField;
```

---

## Using EditableRegion on a Page

```jsx
// pages/LessonView.jsx — Example: making a lesson page inline-editable
import EditableRegion from '../components/cms/EditableRegion';
import DOMPurify from 'dompurify';
import { useAuth } from '../hooks/useAuth';
import { updateLesson } from '../api/lessonApi';

export default function LessonView({ lesson }) {
  const { user } = useAuth();
  const canEdit = user?.role === 'teacher' || user?.role === 'admin';

  const handleSave = async (fieldName, newValue) => {
    await updateLesson(lesson.id, { [fieldName]: newValue });
  };

  return (
    <article className="lesson-view">
      <EditableRegion
        fieldName="title"
        value={lesson.title}
        onSave={handleSave}
        type="text"
        editable={canEdit}
      >
        <h1>{lesson.title}</h1>
      </EditableRegion>

      <EditableRegion
        fieldName="subtitle"
        value={lesson.subtitle}
        onSave={handleSave}
        type="text"
        editable={canEdit}
      >
        <p className="subtitle">{lesson.subtitle}</p>
      </EditableRegion>

      <EditableRegion
        fieldName="cover_image"
        value={lesson.cover_image}
        onSave={handleSave}
        type="image"
        editable={canEdit}
      >
        <img src={lesson.cover_image} alt={lesson.title} />
      </EditableRegion>

      <EditableRegion
        fieldName="body"
        value={lesson.body}
        onSave={handleSave}
        type="richtext"
        editable={canEdit}
      >
        <div
          className="lesson-body"
          dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(lesson.body) }}
        />
      </EditableRegion>
    </article>
  );
}
```

---

## API Endpoint Pattern

```js
// server/routes/content.js — Generic content update endpoint
// Works with any table that has an id column
const DOMPurify = require('isomorphic-dompurify');

router.patch('/api/content/:table/:id', authenticate, authorize(['admin', 'teacher']), async (req, res) => {
  const { table, id } = req.params;
  const updates = req.body;

  // Whitelist allowed tables and fields
  const EDITABLE = {
    lessons: ['title', 'subtitle', 'body', 'cover_image', 'summary'],
    courses: ['title', 'description', 'cover_image'],
    announcements: ['title', 'body'],
    pages: ['title', 'content', 'meta_description'],
  };

  if (!EDITABLE[table]) {
    return res.status(403).json({ error: 'Table not editable' });
  }

  // Filter to only allowed fields and sanitize HTML
  const allowed = {};
  const HTML_FIELDS = ['body', 'content', 'description'];
  for (const [key, val] of Object.entries(updates)) {
    if (EDITABLE[table].includes(key)) {
      allowed[key] = HTML_FIELDS.includes(key) ? DOMPurify.sanitize(val) : val;
    }
  }

  if (Object.keys(allowed).length === 0) {
    return res.status(400).json({ error: 'No valid fields to update' });
  }

  // Build SET clause — works for both MySQL and PostgreSQL
  const setClauses = Object.keys(allowed).map((key) => `${key} = ?`);
  const values = [...Object.values(allowed), id];

  const sql = `UPDATE ${table} SET ${setClauses.join(', ')}, updated_at = NOW() WHERE id = ?`;

  await db.query(sql, values);

  // Return updated record
  const [updated] = await db.query(`SELECT * FROM ${table} WHERE id = ?`, [id]);
  res.json(updated);
});
```

---

## Edit Mode Toggle

Teachers shouldn't always be in edit mode — they also need to preview as students see it.

```jsx
// components/cms/EditModeProvider.jsx
import { createContext, useContext, useState } from 'react';
import { useAuth } from '../hooks/useAuth';

const EditModeContext = createContext({ editMode: false, toggleEditMode: () => {} });

export function EditModeProvider({ children }) {
  const { user } = useAuth();
  const canEdit = user?.role === 'teacher' || user?.role === 'admin';
  const [editMode, setEditMode] = useState(false);

  if (!canEdit) {
    return (
      <EditModeContext.Provider value={{ editMode: false, toggleEditMode: () => {} }}>
        {children}
      </EditModeContext.Provider>
    );
  }

  return (
    <EditModeContext.Provider
      value={{ editMode, toggleEditMode: () => setEditMode((prev) => !prev) }}
    >
      {children}

      {/* Floating toggle button */}
      <button
        onClick={() => setEditMode((prev) => !prev)}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          background: editMode ? '#ef4444' : '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '50px',
          padding: '12px 24px',
          fontSize: '14px',
          fontWeight: 'bold',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          zIndex: 9999,
          transition: 'background 0.2s',
        }}
      >
        {editMode ? 'Exit Editing' : 'Edit Page'}
      </button>
    </EditModeContext.Provider>
  );
}

export function useEditMode() {
  return useContext(EditModeContext);
}
```

Then in EditableRegion, replace the `editable` prop with context:

```jsx
import { useEditMode } from './EditModeProvider';

// Inside EditableRegion:
const { editMode } = useEditMode();
if (!editMode) return <>{children}</>;
```

---

## Auto-Save Pattern (Optional)

For a smoother experience, auto-save after the user stops typing:

```jsx
// hooks/useAutoSave.js
import { useRef, useCallback } from 'react';

export function useAutoSave(saveFn, delayMs = 1500) {
  const timerRef = useRef(null);
  const latestValueRef = useRef(null);

  const scheduleSave = useCallback(
    (fieldName, value) => {
      latestValueRef.current = { fieldName, value };

      if (timerRef.current) clearTimeout(timerRef.current);

      timerRef.current = setTimeout(async () => {
        const { fieldName: f, value: v } = latestValueRef.current;
        try {
          await saveFn(f, v);
        } catch (err) {
          console.error('Auto-save failed:', err);
        }
      }, delayMs);
    },
    [saveFn, delayMs]
  );

  const flushSave = useCallback(async () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    if (latestValueRef.current) {
      const { fieldName, value } = latestValueRef.current;
      await saveFn(fieldName, value);
      latestValueRef.current = null;
    }
  }, [saveFn]);

  return { scheduleSave, flushSave };
}
```

---

## Audit Trail (Database Schema)

Track every inline edit for accountability — who changed what, when.

### MySQL

```sql
CREATE TABLE content_edits (
  id INT AUTO_INCREMENT PRIMARY KEY,
  table_name VARCHAR(64) NOT NULL,
  record_id VARCHAR(36) NOT NULL,
  field_name VARCHAR(64) NOT NULL,
  old_value TEXT,
  new_value TEXT,
  edited_by VARCHAR(36) NOT NULL,
  edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_record (table_name, record_id),
  INDEX idx_editor (edited_by),
  FOREIGN KEY (edited_by) REFERENCES users(id)
);
```

### PostgreSQL

```sql
CREATE TABLE content_edits (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  table_name VARCHAR(64) NOT NULL,
  record_id UUID NOT NULL,
  field_name VARCHAR(64) NOT NULL,
  old_value TEXT,
  new_value TEXT,
  edited_by UUID NOT NULL REFERENCES users(id),
  edited_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_content_edits_record ON content_edits(table_name, record_id);
CREATE INDEX idx_content_edits_editor ON content_edits(edited_by);
```

---

## Integration With Existing Skills

| Skill | How It Connects |
|-------|----------------|
| `tiptap-minimal-setup.md` | Use TipTap as the `richtext` field renderer inside EditField |
| `content-publishing-states.md` | Only allow inline editing on DRAFT content, not PUBLISHED |
| `media-manager-abstraction.md` | Use the media manager for the `image` field type |
| `schema-driven-form-generator.md` | Generate EditableRegion configs from schema definitions |

---

## Security Checklist

- [ ] Server-side field whitelist (EDITABLE map) — never trust client field names
- [ ] Authentication + role check on every PATCH endpoint
- [ ] Sanitize HTML content before saving (DOMPurify on both client and server)
- [ ] Rate limit inline save endpoints (prevent spam)
- [ ] Audit trail records editor identity from JWT, not from client
- [ ] Content Security Policy headers if rendering user HTML

---

## When to Use This Pattern

**Use inline editing when:**
- Content creators are not developers
- The "what you see" matters (visual layout, styling context)
- Edits are small and frequent (fixing typos, updating announcements)
- Multiple content types share the same page layout

**Use a traditional admin form when:**
- Editing involves complex relationships (assigning teachers to courses)
- Bulk operations are common (publish 20 lessons at once)
- The content structure is more important than visual layout

**Best practice:** Use BOTH. Inline editing for content text/images on the rendered page. Admin forms for metadata, relationships, and bulk operations.
