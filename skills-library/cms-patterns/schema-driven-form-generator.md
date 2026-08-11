# Schema-Driven Form Generator

> Define fields once in a config file — get a complete admin form with validation, field types, and save logic
---

## Overview

Instead of hand-coding every admin form, you define your content model in a single config file and the system generates the complete form — inputs, validation, labels, help text, and save logic. Change the config, the form updates automatically.

**The problem this solves:**
- MINISTRY-LMS has 27+ plugins, each needing admin forms
- Hand-coding forms is repetitive and error-prone
- Adding a field means editing 3+ files (form, API, validation)
- Schema-driven: add one line to config → form, API, and validation all update

---

## Architecture

```
┌───────────────────────────────┐
│  Content Schema (config file) │  ← Single source of truth
│                                │
│  {                             │
│    name: "lessons",            │
│    fields: [                   │
│      { name: "title",          │
│        type: "text",           │
│        required: true },       │
│      { name: "body",           │
│        type: "richtext" },     │
│      { name: "difficulty",     │
│        type: "select",         │
│        options: [...] }        │
│    ]                           │
│  }                             │
└────────────┬──────────────────┘
             │
    ┌────────┴────────┐
    │                  │
    ▼                  ▼
┌──────────┐    ┌──────────────┐
│ React    │    │ Express API  │
│ Form     │    │ Validation   │
│ (auto)   │    │ (auto)       │
└──────────┘    └──────────────┘
```

---

## Content Schema Definition

```js
// config/content-schemas.js
// Define ALL content types in one place

export const contentSchemas = {
  lessons: {
    label: 'Lesson',
    labelPlural: 'Lessons',
    table: 'lessons',
    icon: 'BookOpen',
    fields: [
      {
        name: 'title',
        type: 'text',
        label: 'Lesson Title',
        required: true,
        maxLength: 200,
        placeholder: 'Enter lesson title...',
      },
      {
        name: 'subtitle',
        type: 'text',
        label: 'Subtitle',
        maxLength: 300,
      },
      {
        name: 'body',
        type: 'richtext',
        label: 'Lesson Content',
        required: true,
        help: 'Use the toolbar to format text, add images, and embed media.',
      },
      {
        name: 'cover_image',
        type: 'image',
        label: 'Cover Image',
        help: 'Recommended: 1200x630px',
      },
      {
        name: 'difficulty',
        type: 'select',
        label: 'Difficulty Level',
        options: [
          { value: 'beginner', label: 'Beginner' },
          { value: 'intermediate', label: 'Intermediate' },
          { value: 'advanced', label: 'Advanced' },
        ],
        defaultValue: 'beginner',
      },
      {
        name: 'duration_minutes',
        type: 'number',
        label: 'Duration (minutes)',
        min: 1,
        max: 480,
      },
      {
        name: 'is_published',
        type: 'toggle',
        label: 'Published',
        defaultValue: false,
      },
      {
        name: 'course_id',
        type: 'reference',
        label: 'Course',
        references: { table: 'courses', labelField: 'title' },
        required: true,
      },
      {
        name: 'tags',
        type: 'tags',
        label: 'Tags',
        help: 'Press Enter to add a tag',
      },
      {
        name: 'publish_at',
        type: 'datetime',
        label: 'Scheduled Publish Date',
        help: 'Leave empty to publish immediately',
      },
    ],
  },

  courses: {
    label: 'Course',
    labelPlural: 'Courses',
    table: 'courses',
    icon: 'GraduationCap',
    fields: [
      {
        name: 'title',
        type: 'text',
        label: 'Course Title',
        required: true,
        maxLength: 200,
      },
      {
        name: 'description',
        type: 'richtext',
        label: 'Description',
      },
      {
        name: 'cover_image',
        type: 'image',
        label: 'Cover Image',
      },
      {
        name: 'category',
        type: 'select',
        label: 'Category',
        options: [
          { value: 'bible-study', label: 'Bible Study' },
          { value: 'leadership', label: 'Leadership' },
          { value: 'worship', label: 'Worship' },
          { value: 'youth', label: 'Youth Ministry' },
          { value: 'outreach', label: 'Outreach' },
        ],
      },
      {
        name: 'instructor_id',
        type: 'reference',
        label: 'Instructor',
        references: { table: 'users', labelField: 'name', filter: { role: 'teacher' } },
      },
    ],
  },

  announcements: {
    label: 'Announcement',
    labelPlural: 'Announcements',
    table: 'announcements',
    icon: 'Megaphone',
    fields: [
      {
        name: 'title',
        type: 'text',
        label: 'Title',
        required: true,
      },
      {
        name: 'body',
        type: 'richtext',
        label: 'Content',
        required: true,
      },
      {
        name: 'priority',
        type: 'select',
        label: 'Priority',
        options: [
          { value: 'normal', label: 'Normal' },
          { value: 'important', label: 'Important' },
          { value: 'urgent', label: 'Urgent' },
        ],
        defaultValue: 'normal',
      },
      {
        name: 'expires_at',
        type: 'datetime',
        label: 'Expiry Date',
      },
    ],
  },
};
```

---

## Supported Field Types

| Type | Renders As | Validation |
|------|-----------|------------|
| `text` | `<input type="text">` | maxLength, required, pattern |
| `number` | `<input type="number">` | min, max, required |
| `richtext` | TipTap editor or `<textarea>` | required, maxLength |
| `image` | Upload component + preview | file type, max size |
| `select` | `<select>` dropdown | required, options list |
| `toggle` | Switch/checkbox | boolean |
| `reference` | Searchable dropdown (loads from referenced table) | required |
| `tags` | Tag input with autocomplete | maxTags |
| `datetime` | Date + time picker | min/max date |
| `textarea` | `<textarea>` | maxLength, required |
| `email` | `<input type="email">` | email format |
| `url` | `<input type="url">` | URL format |
| `color` | Color picker | hex format |
| `json` | Code editor (monospace) | valid JSON |

---

## SchemaForm Component (The Generator)

```jsx
// components/cms/SchemaForm.jsx
import { useState, useEffect } from 'react';
import DOMPurify from 'dompurify';

/**
 * Auto-generates a complete form from a content schema definition.
 *
 * Props:
 *   schema     — schema object from contentSchemas (e.g., contentSchemas.lessons)
 *   values     — current field values (for editing existing records)
 *   onSubmit   — async function(values) => save to API
 *   mode       — "create" | "edit"
 */
export default function SchemaForm({ schema, values = {}, onSubmit, mode = 'create' }) {
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  // Initialize form data from defaults or existing values
  useEffect(() => {
    const initial = {};
    schema.fields.forEach((field) => {
      initial[field.name] = values[field.name] ?? field.defaultValue ?? '';
    });
    setFormData(initial);
  }, [schema, values]);

  const updateField = (name, value) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error on change
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const validate = () => {
    const newErrors = {};
    schema.fields.forEach((field) => {
      const val = formData[field.name];

      if (field.required && (val === '' || val === null || val === undefined)) {
        newErrors[field.name] = `${field.label} is required`;
      }
      if (field.maxLength && typeof val === 'string' && val.length > field.maxLength) {
        newErrors[field.name] = `${field.label} must be ${field.maxLength} characters or less`;
      }
      if (field.min !== undefined && typeof val === 'number' && val < field.min) {
        newErrors[field.name] = `${field.label} must be at least ${field.min}`;
      }
      if (field.max !== undefined && typeof val === 'number' && val > field.max) {
        newErrors[field.name] = `${field.label} must be at most ${field.max}`;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setSaving(true);
    try {
      // Sanitize any HTML fields before submitting
      const sanitized = { ...formData };
      schema.fields.forEach((field) => {
        if (field.type === 'richtext' && sanitized[field.name]) {
          sanitized[field.name] = DOMPurify.sanitize(sanitized[field.name]);
        }
      });
      await onSubmit(sanitized);
    } catch (err) {
      console.error('Form submit failed:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: '720px' }}>
      <h2>{mode === 'create' ? `New ${schema.label}` : `Edit ${schema.label}`}</h2>

      {schema.fields.map((field) => (
        <FieldRenderer
          key={field.name}
          field={field}
          value={formData[field.name]}
          onChange={(val) => updateField(field.name, val)}
          error={errors[field.name]}
        />
      ))}

      <div style={{ marginTop: '24px', display: 'flex', gap: '12px' }}>
        <button
          type="submit"
          disabled={saving}
          style={{
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            padding: '10px 24px',
            borderRadius: '6px',
            fontSize: '15px',
            cursor: 'pointer',
          }}
        >
          {saving ? 'Saving...' : mode === 'create' ? `Create ${schema.label}` : 'Save Changes'}
        </button>
      </div>
    </form>
  );
}
```

---

## Field Renderer (Routes to Correct Input)

```jsx
// components/cms/FieldRenderer.jsx
import { useState, useEffect } from 'react';

export default function FieldRenderer({ field, value, onChange, error }) {
  const wrapperStyle = {
    marginBottom: '20px',
  };

  const labelStyle = {
    display: 'block',
    fontWeight: '600',
    marginBottom: '6px',
    fontSize: '14px',
  };

  const inputStyle = {
    width: '100%',
    padding: '8px 12px',
    border: error ? '1px solid #ef4444' : '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    boxSizing: 'border-box',
  };

  const errorStyle = {
    color: '#ef4444',
    fontSize: '13px',
    marginTop: '4px',
  };

  const helpStyle = {
    color: '#6b7280',
    fontSize: '13px',
    marginTop: '4px',
  };

  const renderField = () => {
    switch (field.type) {
      case 'text':
      case 'email':
      case 'url':
        return (
          <input
            type={field.type}
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder={field.placeholder || ''}
            maxLength={field.maxLength}
            style={inputStyle}
          />
        );

      case 'number':
        return (
          <input
            type="number"
            value={value ?? ''}
            onChange={(e) => onChange(e.target.value ? Number(e.target.value) : '')}
            min={field.min}
            max={field.max}
            style={inputStyle}
          />
        );

      case 'textarea':
      case 'richtext':
        // For production, swap richtext with TipTap from tiptap-minimal-setup.md
        return (
          <textarea
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            rows={field.type === 'richtext' ? 10 : 4}
            style={{ ...inputStyle, resize: 'vertical', fontFamily: 'inherit' }}
          />
        );

      case 'select':
        return (
          <select
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            style={inputStyle}
          >
            <option value="">Select {field.label}...</option>
            {(field.options || []).map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        );

      case 'toggle':
        return (
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={!!value}
              onChange={(e) => onChange(e.target.checked)}
              style={{ width: '18px', height: '18px' }}
            />
            <span>{value ? 'Yes' : 'No'}</span>
          </label>
        );

      case 'datetime':
        return (
          <input
            type="datetime-local"
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            style={inputStyle}
          />
        );

      case 'image':
        return (
          <div>
            {value && (
              <img
                src={value}
                alt="Preview"
                style={{
                  maxWidth: '200px',
                  maxHeight: '120px',
                  borderRadius: '4px',
                  marginBottom: '8px',
                  display: 'block',
                }}
              />
            )}
            <input
              type="text"
              value={value || ''}
              onChange={(e) => onChange(e.target.value)}
              placeholder="Image URL"
              style={inputStyle}
            />
          </div>
        );

      case 'reference':
        return <ReferenceField field={field} value={value} onChange={onChange} style={inputStyle} />;

      case 'tags':
        return <TagsField value={value} onChange={onChange} />;

      case 'color':
        return (
          <input
            type="color"
            value={value || '#000000'}
            onChange={(e) => onChange(e.target.value)}
            style={{ width: '60px', height: '36px', border: 'none', cursor: 'pointer' }}
          />
        );

      case 'json':
        return (
          <textarea
            value={typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
            onChange={(e) => onChange(e.target.value)}
            rows={8}
            style={{ ...inputStyle, fontFamily: 'monospace', fontSize: '13px' }}
          />
        );

      default:
        return <div>Unknown field type: {field.type}</div>;
    }
  };

  return (
    <div style={wrapperStyle}>
      <label style={labelStyle}>
        {field.label}
        {field.required && <span style={{ color: '#ef4444' }}> *</span>}
      </label>
      {renderField()}
      {error && <div style={errorStyle}>{error}</div>}
      {field.help && !error && <div style={helpStyle}>{field.help}</div>}
    </div>
  );
}

// Reference field — loads options from another table
function ReferenceField({ field, value, onChange, style }) {
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const { table, labelField, filter } = field.references;
        let url = `/api/${table}?limit=100`;
        if (filter) {
          Object.entries(filter).forEach(([k, v]) => {
            url += `&${k}=${v}`;
          });
        }
        const res = await fetch(url);
        const data = await res.json();
        setOptions(
          (data.rows || data).map((row) => ({
            value: row.id,
            label: row[labelField] || row.name || row.title || row.id,
          }))
        );
      } catch (err) {
        console.error(`Failed to load ${field.references.table}:`, err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [field.references]);

  if (loading) return <div>Loading...</div>;

  return (
    <select value={value || ''} onChange={(e) => onChange(e.target.value)} style={style}>
      <option value="">Select {field.label}...</option>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}

// Tags field — enter-to-add tag input
function TagsField({ value, onChange }) {
  const tags = Array.isArray(value) ? value : [];
  const [input, setInput] = useState('');

  const addTag = () => {
    const tag = input.trim();
    if (tag && !tags.includes(tag)) {
      onChange([...tags, tag]);
    }
    setInput('');
  };

  const removeTag = (index) => {
    onChange(tags.filter((_, i) => i !== index));
  };

  return (
    <div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '8px' }}>
        {tags.map((tag, i) => (
          <span
            key={i}
            style={{
              background: '#e0e7ff',
              color: '#3730a3',
              padding: '4px 10px',
              borderRadius: '16px',
              fontSize: '13px',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            {tag}
            <button
              type="button"
              onClick={() => removeTag(i)}
              style={{
                background: 'none',
                border: 'none',
                color: '#6366f1',
                cursor: 'pointer',
                padding: '0',
                fontSize: '16px',
                lineHeight: '1',
              }}
            >
              x
            </button>
          </span>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
            addTag();
          }
        }}
        placeholder="Type and press Enter to add"
        style={{
          width: '100%',
          padding: '8px 12px',
          border: '1px solid #d1d5db',
          borderRadius: '6px',
          fontSize: '14px',
        }}
      />
    </div>
  );
}
```

---

## Server-Side Validation (Auto-Generated from Schema)

```js
// server/middleware/schemaValidator.js
// Generates Express validation middleware from the same schema

const { contentSchemas } = require('../../config/content-schemas');

function createValidator(schemaName) {
  const schema = contentSchemas[schemaName];
  if (!schema) throw new Error(`Unknown schema: ${schemaName}`);

  return (req, res, next) => {
    const errors = [];
    const body = req.body;

    schema.fields.forEach((field) => {
      const val = body[field.name];

      if (field.required && (val === '' || val === null || val === undefined)) {
        errors.push({ field: field.name, message: `${field.label} is required` });
      }

      if (val !== undefined && val !== null && val !== '') {
        if (field.maxLength && typeof val === 'string' && val.length > field.maxLength) {
          errors.push({
            field: field.name,
            message: `${field.label} exceeds max length of ${field.maxLength}`,
          });
        }
        if (field.min !== undefined && typeof val === 'number' && val < field.min) {
          errors.push({
            field: field.name,
            message: `${field.label} must be at least ${field.min}`,
          });
        }
        if (field.max !== undefined && typeof val === 'number' && val > field.max) {
          errors.push({
            field: field.name,
            message: `${field.label} must be at most ${field.max}`,
          });
        }
        if (field.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
          errors.push({ field: field.name, message: 'Invalid email format' });
        }
        if (field.type === 'url' && !/^https?:\/\/.+/.test(val)) {
          errors.push({ field: field.name, message: 'Invalid URL format' });
        }
      }
    });

    if (errors.length > 0) {
      return res.status(400).json({ errors });
    }

    next();
  };
}

module.exports = { createValidator };
```

Usage:

```js
// server/routes/lessons.js
const { createValidator } = require('../middleware/schemaValidator');

router.post('/api/lessons', authenticate, createValidator('lessons'), async (req, res) => {
  // req.body is already validated — safe to insert
  // ...
});
```

---

## Auto-Generated CRUD Routes (Optional)

```js
// server/routes/schemaCrud.js
// Generates full CRUD endpoints from schema definitions

const { contentSchemas } = require('../../config/content-schemas');
const { createValidator } = require('../middleware/schemaValidator');

function registerSchemaRoutes(router, schemaName) {
  const schema = contentSchemas[schemaName];
  const table = schema.table;

  // LIST
  router.get(`/api/${table}`, authenticate, async (req, res) => {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;

    const rows = await db.query(`SELECT * FROM ${table} ORDER BY created_at DESC LIMIT ? OFFSET ?`, [limit, offset]);
    const [{ count }] = await db.query(`SELECT COUNT(*) as count FROM ${table}`);

    res.json({ rows, total: count, page, limit });
  });

  // GET ONE
  router.get(`/api/${table}/:id`, authenticate, async (req, res) => {
    const [row] = await db.query(`SELECT * FROM ${table} WHERE id = ?`, [req.params.id]);
    if (!row) return res.status(404).json({ error: 'Not found' });
    res.json(row);
  });

  // CREATE
  router.post(`/api/${table}`, authenticate, authorize(['admin', 'teacher']), createValidator(schemaName), async (req, res) => {
    const fields = schema.fields.map((f) => f.name).filter((f) => req.body[f] !== undefined);
    const values = fields.map((f) => req.body[f]);
    const placeholders = fields.map(() => '?').join(', ');

    await db.query(`INSERT INTO ${table} (${fields.join(', ')}) VALUES (${placeholders})`, values);

    res.status(201).json({ message: `${schema.label} created` });
  });

  // UPDATE
  router.put(`/api/${table}/:id`, authenticate, authorize(['admin', 'teacher']), createValidator(schemaName), async (req, res) => {
    const fields = schema.fields.map((f) => f.name).filter((f) => req.body[f] !== undefined);
    const setClauses = fields.map((f) => `${f} = ?`);
    const values = [...fields.map((f) => req.body[f]), req.params.id];

    await db.query(`UPDATE ${table} SET ${setClauses.join(', ')}, updated_at = NOW() WHERE id = ?`, values);

    res.json({ message: `${schema.label} updated` });
  });

  // DELETE
  router.delete(`/api/${table}/:id`, authenticate, authorize(['admin']), async (req, res) => {
    await db.query(`DELETE FROM ${table} WHERE id = ?`, [req.params.id]);
    res.json({ message: `${schema.label} deleted` });
  });
}

module.exports = { registerSchemaRoutes };
```

---

## Integration With Existing Skills

| Skill | How It Connects |
|-------|----------------|
| `inline-visual-editing.md` | SchemaForm handles admin forms; inline editing handles on-page editing |
| `tiptap-minimal-setup.md` | Swap the `richtext` textarea for TipTap in FieldRenderer |
| `content-publishing-states.md` | Add `status` field type that renders the state machine controls |
| `media-manager-abstraction.md` | Swap the `image` text input for the media manager upload widget |

---

## Adding a New Content Type

To add a completely new content type (e.g., "devotionals"):

1. Add schema to `config/content-schemas.js`
2. Create the database table (MySQL or PostgreSQL)
3. Register routes: `registerSchemaRoutes(router, 'devotionals')`
4. Add to admin nav menu

That's it — 4 steps. The form, validation, and CRUD API are all auto-generated.
