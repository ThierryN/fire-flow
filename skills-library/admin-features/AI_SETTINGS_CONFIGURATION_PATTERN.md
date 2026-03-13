# Admin AI Settings Configuration Pattern

## The Problem

AI models and their parameters were hard-coded in service files, making it impossible to change models, styles, or behavior without code changes and redeployment. Admins had no way to configure AI features through the UI.

### Why It Was Hard

- Multiple services using different AI models (text generation, image generation, embeddings)
- Hard-coded model names scattered across codebase
- No database infrastructure for AI configuration
- Need for admin-only access control
- Settings must take effect immediately without restart

### Impact

- Every model change required code modification
- No A/B testing capability for different models
- Admins couldn't adjust AI behavior for cost/quality trade-offs
- Deployment required for simple configuration changes

---

## The Solution

### Architecture Overview

Create a three-layer system:
1. **Database Layer** - Store settings in `ai_settings` table with JSONB values
2. **Model Layer** - Functions to read/write settings with proper typing
3. **Service Layer** - Services read from settings dynamically
4. **Admin UI** - React page for configuration with immediate effect

### Root Cause

Original design didn't anticipate need for runtime configuration. AI services were written with hard-coded models for simplicity.

### Implementation Steps

#### 1. Database Schema (if not exists)

```sql
CREATE TABLE IF NOT EXISTS ai_settings (
  setting_key VARCHAR(255) PRIMARY KEY,
  setting_value JSONB NOT NULL,
  updated_by UUID REFERENCES profiles(id),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Example settings
INSERT INTO ai_settings (setting_key, setting_value) VALUES
('infographic_model', '{"value": "gemini-2.5-flash-image"}'),
('infographic_style', '{"value": "professional"}'),
('enabled', '{"value": true}');
```

#### 2. Model Layer (aiSettingsModel.js)

```javascript
// server/models/aiSettingsModel.js
import sql from '../config/sql.js';

function extractValue(raw) {
  let val = raw;
  if (typeof val === 'string') {
    try { val = JSON.parse(val); } catch { /* use as-is */ }
  }
  return val?.value ?? val;
}

export const getAISetting = async (key) => {
  const [result] = await sql`
    SELECT setting_value FROM ai_settings WHERE setting_key = ${key}
  `;
  if (!result) return null;
  return extractValue(result.setting_value);
};

export const getAllAISettings = async () => {
  const results = await sql`SELECT setting_key, setting_value FROM ai_settings`;
  return results.reduce((acc, row) => {
    acc[row.setting_key] = extractValue(row.setting_value);
    return acc;
  }, {});
};

export const updateAISetting = async (key, value, userId) => {
  const wrapped = { value };
  const [result] = await sql`
    INSERT INTO ai_settings (setting_key, setting_value, updated_by, updated_at)
    VALUES (${key}, ${sql.json(wrapped)}, ${userId}, NOW())
    ON CONFLICT (setting_key) DO UPDATE
    SET setting_value = ${sql.json(wrapped)},
        updated_by = ${userId},
        updated_at = NOW()
    RETURNING *
  `;
  return result;
};
```

#### 3. Service Layer - Dynamic Model Loading

```javascript
// server/services/ai/ImageGenerationService.js
import { getAISetting } from '../../models/aiSettingsModel.js';

async generateInfographic(lessonTitle, lessonContent, options = {}) {
  if (!this.genAI) this.initialize();
  if (!this.genAI) throw new Error('Gemini API key not configured');

  // Read from AI settings (default to gemini-2.5-flash-image)
  const configuredModel = await getAISetting('infographic_model') || 'gemini-2.5-flash-image';

  const model = this.genAI.getGenerativeModel({
    model: configuredModel,
    generationConfig: { responseModalities: ['TEXT', 'IMAGE'] }
  });

  // ... rest of generation logic
}
```

#### 4. Admin UI Component

```javascript
// client/src/pages/admin/AISettings.jsx
import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import toast from 'react-hot-toast';

const AISettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState({
    infographic_model: 'gemini-2.5-flash-image',
    infographic_style: 'professional',
    enabled: true
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const res = await api.get('/ai-course/settings');
      if (res.data?.settings) {
        setSettings(prev => ({ ...prev, ...res.data.settings }));
      }
    } catch (error) {
      console.error('Failed to load AI settings:', error);
      toast.error('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await api.put('/ai-course/settings', { settings });
      toast.success('AI settings saved successfully!');
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast.error(error?.response?.data?.message || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6">
      <h1>AI Settings</h1>

      <div className="mt-6">
        <label>Image Generation Model</label>
        <select
          value={settings.infographic_model || 'gemini-2.5-flash-image'}
          onChange={(e) => setSettings({ ...settings, infographic_model: e.target.value })}
        >
          <option value="gemini-2.5-flash-image">Gemini 2.5 Flash Image</option>
          <option value="gemini-2.0-flash-image">Gemini 2.0 Flash Image</option>
          <option value="gemini-pro-vision">Gemini Pro Vision</option>
        </select>
      </div>

      <button onClick={handleSave} disabled={saving}>
        {saving ? 'Saving...' : 'Save Settings'}
      </button>
    </div>
  );
};
```

#### 5. Routes and Navigation

```javascript
// client/src/App.jsx - Add route
const AISettings = lazy(() => import('./pages/admin/AISettings.jsx'));

<Route path="ai-settings" element={<AISettings />} />

// client/src/layouts/AdminLayout.jsx - Add navigation
{
  name: 'System',
  children: [
    { name: 'Settings', href: '/admin/settings' },
    { name: 'AI Settings', href: '/admin/ai-settings', icon: '...' },
  ]
}
```

#### 6. Controller Endpoints

```javascript
// server/controllers/aiCourseController.js
export const getSettings = async (req, res) => {
  try {
    const settings = await getAllAISettings();
    res.json({ success: true, settings });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

export const updateSettings = async (req, res) => {
  try {
    const { settings } = req.body;
    await updateMultipleAISettings(settings, req.user.id);
    res.json({ success: true, message: 'Settings updated successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};
```

---

## Testing the Implementation

### 1. Verify Settings Load
```bash
# Login as admin, navigate to /admin/ai-settings
# Should load current settings without errors
```

### 2. Test Save Functionality
```bash
# Change model to "gemini-2.0-flash-image"
# Click Save
# Verify success toast appears
# Refresh page - should show new model selected
```

### 3. Test Dynamic Model Usage
```javascript
// Generate an infographic
// Check server logs - should show configured model being used
// Change model in settings
// Generate another infographic immediately
// Should use new model without restart
```

### 4. Test Default Fallback
```javascript
// Delete infographic_model setting from database
// Generate infographic
// Should use 'gemini-2.5-flash-image' as default
```

---

## Prevention & Best Practices

### 1. Always Use Settings for Configurable Values
❌ **Bad:**
```javascript
const model = 'gemini-2.5-flash-image'; // Hard-coded
```

✅ **Good:**
```javascript
const model = await getAISetting('infographic_model') || 'gemini-2.5-flash-image';
```

### 2. Provide Sensible Defaults
Always have a fallback value in case settings are missing or database is unreachable.

### 3. Admin-Only Access
```javascript
router.get('/settings', authorize('admin'), aiCourseController.getSettings);
router.put('/settings', authorize('admin'), aiCourseController.updateSettings);
```

### 4. Immediate Effect
Settings should take effect on next use, no restart required. Read from database on each generation.

### 5. Setting Types
```javascript
// String settings
infographic_model: 'gemini-2.5-flash-image'

// Boolean settings
enabled: true

// Number settings
max_tokens: 2000

// Enum settings (validate on save)
infographic_style: 'professional' | 'educational' | 'modern' | 'creative'
```

---

## Common Mistakes to Avoid

- ❌ **Caching settings** - Don't cache, read fresh on each use for immediate effect
- ❌ **No defaults** - Always provide fallback values
- ❌ **Not validating** - Validate model names exist before saving
- ❌ **Storing as strings** - Use JSONB `{value: "x"}` format for type safety
- ❌ **Public access** - Always restrict to admin role
- ❌ **Not documenting options** - UI should explain what each setting does

---

## Related Patterns

- [Admin Configuration UI Pattern](./ADMIN_CONFIG_UI_PATTERN.md)
- [Database Settings Management](../database-solutions/SETTINGS_TABLE_PATTERN.md)
- [Dynamic Service Configuration](../patterns-standards/DYNAMIC_CONFIG_PATTERN.md)

---

## Resources

- [AI Settings Model Code](../../server/models/aiSettingsModel.js)
- [Image Generation Service](../../server/services/ai/ImageGenerationService.js)
- [Admin AI Settings UI](../../client/src/pages/admin/AISettings.jsx)

---

## Time to Implement

**2-3 hours** for complete implementation:
- Database table: 15 min
- Model layer: 30 min
- Service integration: 30 min
- Admin UI: 60 min
- Testing: 30 min

## Difficulty Level

⭐⭐⭐ (3/5) - Moderate complexity, requires understanding of full stack

---

## Extension Ideas

### Add More Settings
```javascript
// Text generation settings
default_model: 'claude-sonnet-4-20250514'
max_tokens: 2000
temperature: 0.7

// Embedding settings
embedding_provider: 'gemini'
embedding_model: 'text-embedding-004'
embedding_dimensions: 1536

// Feature flags
enable_image_generation: true
enable_text_generation: true
enable_knowledge_base: true
```

### Add Validation
```javascript
export const updateAISetting = async (key, value, userId) => {
  // Validate model exists
  if (key === 'infographic_model') {
    const validModels = ['gemini-2.5-flash-image', 'gemini-2.0-flash-image', 'gemini-pro-vision'];
    if (!validModels.includes(value)) {
      throw new Error(`Invalid model: ${value}`);
    }
  }

  // ... save setting
};
```

### Add Preview Mode
Allow admins to preview AI output with different settings before saving.

---

**Author Notes:**

This pattern solved the hard-coded AI configuration problem elegantly. The key insight was using JSONB for flexibility while maintaining type safety through the extraction function. Settings take effect immediately without restart, which is critical for iterative testing.

The pattern is now reusable for any configurable feature - just add a new setting key and read it in your service.

**Deployed:** February 6, 2026 - Production (schooloftheprophets.club)
**Commit:** `6b315fd` - feat(ai): add admin AI Settings page
