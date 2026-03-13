# Puck Page Templates System

> **Purpose**: Enable admins to create, save, and reuse page designs in the Puck visual page builder. Allows agent-created pages to be converted to editable Puck pages.

## CRITICAL: Unique Component IDs

> **⚠️ CORRECTION NOTICE (January 14, 2026 @ 11:45 PM)**
> The ID placement documented below was INCORRECT. ID must be INSIDE `props`, NOT at top level.
> This was verified against the working home page in schooloftheprophets.club database.
> Previous (wrong) documentation is shown with ~~strikethrough~~.

**Every Puck content item MUST have a unique `id` property INSIDE the `props` object.** Without unique IDs, Puck will duplicate components when rendering.

### ~~WRONG~~ ID Format (causes component duplication)
```javascript
// ❌ WRONG - DO NOT USE
{
  type: 'Hero',
  id: 'Hero-1736445678901-abc123xyz',  // ❌ WRONG LOCATION!
  props: { ... }
}
```

### ✅ CORRECT ID Format (verified working)
```javascript
// ✅ CORRECT - ID must be INSIDE props
{
  type: 'Hero',
  props: {
    id: 'Hero-1736445678901-abc123xyz',  // ✅ CORRECT LOCATION!
    title: 'My Title',
    ...
  }
}
```

### ID Generation Helper
```javascript
function generatePuckId(type) {
  return `${type}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// Usage - ID goes INSIDE props:
{
  type: 'Hero',
  props: {
    id: generatePuckId('Hero'),  // ✅ INSIDE props
    title: 'My Title'
  }
}
```

### When Using Templates
The `useTemplate` controller function automatically regenerates unique IDs when creating a page from a template. This prevents duplicate IDs across different pages.

### Common Bug: Component Duplication
If you see components being duplicated (e.g., 7 QuestionnaireButtons instead of 1), the cause is **missing or duplicate `id` properties** in the `puck_data.content` array.

**Fix**: Ensure every item in the content array has a unique `id` field.

---

## Overview

This skill documents how to implement a Page Templates system for Puck, allowing:
1. **Template Library** - Browse and use pre-designed page templates
2. **Save as Template** - Convert any page into a reusable template
3. **Agent Page Import** - Convert hardcoded React pages to Puck-editable pages

## Database Schema

### page_templates Table

```sql
CREATE TABLE IF NOT EXISTS page_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Template identification
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(255) NOT NULL UNIQUE,
  description TEXT,

  -- Categorization
  category VARCHAR(100) DEFAULT 'general',  -- 'course-landing', 'marketing', 'about', 'contact', etc.

  -- Preview
  thumbnail TEXT,  -- URL to preview image

  -- Puck data (the actual template content)
  puck_data JSONB NOT NULL DEFAULT '{"content":[], "root":{}}',

  -- Status
  is_active BOOLEAN DEFAULT true,
  is_featured BOOLEAN DEFAULT false,

  -- Metadata
  created_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
  use_count INTEGER DEFAULT 0,  -- Track how many times template is used

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_page_templates_category ON page_templates(category);
CREATE INDEX idx_page_templates_is_active ON page_templates(is_active);
CREATE INDEX idx_page_templates_is_featured ON page_templates(is_featured);
CREATE INDEX idx_page_templates_use_count ON page_templates(use_count DESC);
```

## API Endpoints

### Public Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/page-templates` | Get all active templates (with filters) |
| GET | `/api/page-templates/categories` | Get template categories with counts |
| GET | `/api/page-templates/:idOrSlug` | Get single template by ID or slug |

### Admin Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/page-templates/admin/all` | Get all templates including inactive |
| POST | `/api/page-templates` | Create new template |
| PUT | `/api/page-templates/:id` | Update template |
| DELETE | `/api/page-templates/:id` | Delete template |
| POST | `/api/page-templates/:id/use` | Create page from template |
| POST | `/api/page-templates/from-page/:pageId` | Save page as template |

## Controller Implementation

### Key Functions

```javascript
// server/controllers/pageTemplatesController.js

// Create page from template
export const useTemplate = async (req, res) => {
  const { id } = req.params;
  const { title, slug } = req.body;

  // Get template
  const [template] = await sql`
    SELECT * FROM page_templates WHERE id = ${id} AND is_active = true
  `;

  // Create page with template's puck_data
  const [page] = await sql`
    INSERT INTO pages (title, slug, puck_data, status, visibility, author_id)
    VALUES (${title}, ${pageSlug}, ${JSON.stringify(template.puck_data)}::jsonb, 'draft', 'public', ${authorId})
    RETURNING id, title, slug
  `;

  // Increment use count
  await sql`UPDATE page_templates SET use_count = use_count + 1 WHERE id = ${id}`;
};

// Save page as template
export const savePageAsTemplate = async (req, res) => {
  const { pageId } = req.params;
  const { name, description, category } = req.body;

  // Get page's puck_data
  const [page] = await sql`SELECT * FROM pages WHERE id = ${pageId}`;

  // Create template
  const [template] = await sql`
    INSERT INTO page_templates (name, slug, description, category, puck_data, created_by)
    VALUES (${name}, ${slug}, ${description}, ${category}, ${page.puck_data}::jsonb, ${createdBy})
    RETURNING *
  `;
};
```

## Frontend Components

### Template Library UI

**Location**: `client/src/pages/admin/TemplateLibrary.jsx`

Features:
- Grid display of templates with thumbnails
- Category filtering
- "Use Template" button opens modal
- Creates new page and navigates to editor

```jsx
const TemplateLibrary = () => {
  const [templates, setTemplates] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');

  const handleUseTemplate = async (template) => {
    const response = await axios.post(`/api/page-templates/${template.id}/use`, {
      title: newPageTitle
    });
    navigate(`/admin/pages/${response.data.data.page.id}/edit`);
  };

  return (
    <div className="grid grid-cols-3 gap-6">
      {templates.map(template => (
        <TemplateCard key={template.id} onUse={() => handleUseTemplate(template)} />
      ))}
    </div>
  );
};
```

### Save as Template (PageEditor Enhancement)

**Location**: `client/src/pages/admin/PageEditor.jsx`

Add to existing PageEditor:

```jsx
// State
const [showSaveAsTemplate, setShowSaveAsTemplate] = useState(false);
const [templateName, setTemplateName] = useState('');
const [templateCategory, setTemplateCategory] = useState('general');

// Handler
const handleSaveAsTemplate = async () => {
  await api.post(`/page-templates/from-page/${id}`, {
    name: templateName,
    description: templateDescription,
    category: templateCategory
  });
  toast.success('Template created successfully');
};

// Button in Puck header overrides
{id && (
  <button onClick={openSaveAsTemplateModal} className="bg-purple-600 text-white">
    Save as Template
  </button>
)}
```

## Converting React Pages to Puck

### Seeder Script Pattern

When an agent creates a hardcoded React page, create a seeder to convert it to Puck format:

```javascript
// server/seed-[page-name]-puck-page.js

// CRITICAL: Helper function to generate unique IDs
function generatePuckId(type) {
  return `${type}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

const pageData = {
  content: [
    {
      type: 'Hero',
      // ✅ CORRECT: ID is INSIDE props (verified Jan 14, 2026)
      props: {
        id: generatePuckId('Hero'),  // ✅ INSIDE props!
        title: 'Page Title',
        subtitle: 'Subtitle',
        backgroundColor: 'blue',
        height: 'large'
      }
    },
    {
      type: 'FeaturesGrid',
      // ✅ CORRECT: ID is INSIDE props
      props: {
        id: generatePuckId('FeaturesGrid'),  // ✅ INSIDE props!
        features: [
          { icon: '🎯', title: 'Feature 1', description: 'Description' },
          // ... more features
        ]
      }
    },
    // ... more components (each with unique id INSIDE props!)
  ],
  root: {
    props: { title: 'Page Title' }
  }
};

// Insert into pages table
await sql`
  INSERT INTO pages (slug, title, puck_data, status, visibility)
  VALUES ('page-slug', 'Page Title', ${JSON.stringify(pageData)}::jsonb, 'published', 'public')
`;
```

### Component Mapping

| React Pattern | Puck Component |
|--------------|----------------|
| Hero section with background | `Hero` |
| Feature list/grid | `FeaturesGrid` |
| Section with title + subtitle | `SectionHeader` |
| Card grid layout | `CardsGrid` |
| Text content blocks | `ContentBlock` |
| CTA buttons | `Button` or `Hero` with CTA |
| Form/questionnaire trigger | `QuestionnaireButton` |

## QuestionnaireButton Puck Component

Custom component for triggering questionnaire modals from Puck pages:

### Component Definition

```jsx
// In PuckComponents.jsx
export const QuestionnaireButton = ({
  questionnaireSearch = '',
  buttonText = 'GET STARTED',
  buttonStyle = 'primary',
  buttonSize = 'large',
  alignment = 'center',
  redirectUrl = '/courses',
  requireAuth = true
}) => {
  const handleClick = async () => {
    if (requireAuth && !isAuthenticated) {
      navigate(`/login?redirect=${window.location.pathname}`);
      return;
    }

    const response = await axios.get('/api/questionnaires/active');
    const found = response.data.data.find(q =>
      q.title.toLowerCase().includes(questionnaireSearch.toLowerCase())
    );

    setQuestionnaire(found);
    setShowModal(true);
  };

  return (
    <button onClick={handleClick}>{buttonText}</button>
  );
};
```

### Puck Config

```javascript
// In puckConfig.jsx
QuestionnaireButton: {
  render: Components.QuestionnaireButton,
  fields: {
    questionnaireSearch: { type: 'text', label: 'Questionnaire Search Term' },
    buttonText: { type: 'text', label: 'Button Text' },
    buttonStyle: {
      type: 'select',
      options: [
        { value: 'primary', label: 'Primary (Blue)' },
        { value: 'success', label: 'Success (Green)' },
        // ...
      ]
    },
    buttonSize: { type: 'select', options: [...] },
    alignment: { type: 'select', options: [...] },
    redirectUrl: { type: 'text', label: 'Redirect URL' },
    requireAuth: { type: 'radio', options: [...] }
  },
  defaultProps: {
    questionnaireSearch: '',
    buttonText: 'GET STARTED',
    buttonStyle: 'primary',
    buttonSize: 'large',
    alignment: 'center',
    redirectUrl: '/courses',
    requireAuth: true
  }
}
```

## Routing for Puck Pages

### Remove Hardcoded Routes

When converting a React page to Puck, update App.jsx:

```jsx
// Before
<Route path="/sop1-course" element={<SOP1Course />} />

// After (remove the route - let it fall through to catch-all)
{/* Course landing pages are now served from database via /:slug route (Puck pages) */}

// The catch-all route handles it:
<Route path="/:slug" element={<PageRenderer />} />
```

## File Structure

```
server/
├── controllers/
│   └── pageTemplatesController.js
├── routes/
│   └── pageTemplatesRoutes.js
├── migrations/
│   └── 076_create_page_templates.sql
└── seed-[page]-puck-page.js

client/src/
├── pages/admin/
│   ├── TemplateLibrary.jsx
│   └── PageEditor.jsx (modified)
└── components/puck/
    ├── PuckComponents.jsx (add QuestionnaireButton)
    └── puckConfig.jsx (add QuestionnaireButton config)
```

## Usage Workflow

### For Admins

1. **Browse Templates**: Navigate to `/admin/page-templates`
2. **Use Template**: Click "Use Template" → Enter page title → Opens in editor
3. **Save as Template**: While editing any page, click "Save as Template"

### For Agents

1. **Create React Page**: Build the page as a normal React component
2. **Create Seeder**: Write `seed-[page]-puck-page.js` to convert to Puck format
3. **Run Seeder**: `node server/seed-[page]-puck-page.js`
4. **Update Routing**: Remove hardcoded route from App.jsx
5. **Page is now editable** via `/admin/pages`

## Template Categories

| Category | Use Case |
|----------|----------|
| `course-landing` | Course marketing/landing pages |
| `marketing` | General marketing pages |
| `about` | About us pages |
| `contact` | Contact pages |
| `general` | Uncategorized templates |

## Sample Template JSON

**Note:** Each content item MUST have a unique `id` property **INSIDE the `props` object**.

> ⚠️ **CORRECTED January 14, 2026** - Previous examples had `id` at wrong level

```json
{
  "content": [
    {
      "type": "Hero",
      "props": {
        "id": "Hero-tpl-001",
        "title": "THE BEST COURSE",
        "subtitle": "ONLINE.",
        "backgroundColor": "blue",
        "overlayOpacity": 70,
        "height": "large"
      }
    },
    {
      "type": "FeaturesGrid",
      "props": {
        "id": "FeaturesGrid-tpl-002",
        "features": [
          {"icon": "🎯", "title": "Feature 1", "description": "Description"},
          {"icon": "📚", "title": "Feature 2", "description": "Description"}
        ]
      }
    },
    {
      "type": "QuestionnaireButton",
      "props": {
        "id": "QuestionnaireButton-tpl-003",
        "questionnaireSearch": "course registration",
        "buttonText": "REGISTER NOW",
        "buttonStyle": "success",
        "buttonSize": "xlarge"
      }
    }
  ],
  "root": {
    "props": {
      "title": "Course Landing Page"
    }
  }
}
```

## Related Skills

- [HOME_PAGE_BUILDER_GUIDE.md](./HOME_PAGE_BUILDER_GUIDE.md) - Puck setup and components
- [SURVEYJS_QUESTIONNAIRE_SYSTEM.md](../form-solutions/SURVEYJS_QUESTIONNAIRE_SYSTEM.md) - Questionnaire integration

## Verification Checklist

- [ ] Migration applied: `076_create_page_templates.sql`
- [ ] Routes registered in `server.js`
- [ ] QuestionnaireButton added to PuckComponents.jsx
- [ ] QuestionnaireButton config added to puckConfig.jsx
- [ ] TemplateLibrary.jsx created and routed
- [ ] PageEditor.jsx has "Save as Template" button
- [ ] Hardcoded page routes removed from App.jsx
- [ ] Seeder script creates page in database
- [ ] Page renders via PageRenderer at correct slug
- [ ] **CRITICAL**: Every content item has unique `id` property **INSIDE `props`** (not top level!)
- [ ] Controller regenerates IDs when using templates (IDs go inside props)
- [ ] Use `sql.json()` for JSONB inserts with postgres-js (prevents double-encoding)

---

## Change Log

| Date | Change | Agent |
|------|--------|-------|
| January 14, 2026 @ 11:45 PM | **CRITICAL FIX**: Corrected ID placement from top-level to inside `props`. Verified against working home page. Old examples marked with strikethrough. | Claude Opus 4.5 |
