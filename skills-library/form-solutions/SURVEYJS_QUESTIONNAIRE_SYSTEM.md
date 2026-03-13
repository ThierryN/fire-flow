# SurveyJS Questionnaire System - MERN Community LMS

## Overview

This document details the questionnaire/form system implemented for the MERN Community LMS using SurveyJS library. The system enables dynamic form creation for course registration, feedback collection, and assessments.

## Research Sources

- [SurveyJS Documentation](https://surveyjs.io/form-library/documentation/get-started-react)
- [SurveyJS Node.js + PostgreSQL Demo](https://github.com/surveyjs/surveyjs-nodejs-postgresql)
- [SurveyJS GitHub Repository](https://github.com/surveyjs/survey-library)

---

## Architecture Overview

```
server/
├── models/
│   ├── Questionnaire.pg.js        # Questionnaire CRUD operations
│   └── QuestionnaireResponse.pg.js # Response storage & retrieval
├── controllers/
│   └── questionnaireController.js  # API handlers
├── routes/
│   └── questionnaireRoutes.js      # REST endpoints
└── migrations/
    └── 072_create_questionnaires.sql

client/src/
├── components/questionnaire/
│   ├── QuestionnaireRenderer.jsx   # SurveyJS form renderer
│   └── QuestionnaireModal.jsx      # Modal wrapper for enrollment
├── hooks/
│   └── useQuestionnaire.js         # React hooks for questionnaire data
└── pages/admin/
    └── QuestionnaireManager.jsx    # Admin UI for management
```

---

## Database Schema

### Migration: 072_create_questionnaires.sql

```sql
-- 1) questionnaires table
CREATE TABLE IF NOT EXISTS questionnaires (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  schema JSONB NOT NULL,           -- SurveyJS JSON schema
  settings JSONB DEFAULT '{}'::jsonb,
  course_id UUID REFERENCES courses(id) ON DELETE SET NULL,
  page_id UUID REFERENCES pages(id) ON DELETE SET NULL,
  is_required BOOLEAN NOT NULL DEFAULT FALSE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_by UUID REFERENCES profiles(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2) questionnaire_responses table
CREATE TABLE IF NOT EXISTS questionnaire_responses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  questionnaire_id UUID NOT NULL REFERENCES questionnaires(id) ON DELETE CASCADE,
  user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
  enrollment_id UUID REFERENCES enrollments(id) ON DELETE SET NULL,
  responses JSONB NOT NULL,
  is_complete BOOLEAN NOT NULL DEFAULT TRUE,
  score DECIMAL(5,2),             -- Optional scoring
  completed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Key Indexes
```sql
CREATE INDEX questionnaires_course_idx ON questionnaires (course_id);
CREATE INDEX questionnaires_page_idx ON questionnaires (page_id);
CREATE INDEX questionnaires_active_idx ON questionnaires (is_active);
CREATE INDEX questionnaire_responses_questionnaire_idx ON questionnaire_responses (questionnaire_id);
CREATE INDEX questionnaire_responses_user_idx ON questionnaire_responses (user_id);
CREATE INDEX questionnaire_responses_enrollment_idx ON questionnaire_responses (enrollment_id);
CREATE INDEX questionnaire_responses_gin ON questionnaire_responses USING gin (responses);
```

---

## SurveyJS Integration

### Installation

```bash
cd client
npm install survey-core survey-react-ui
```

### SurveyJS JSON Schema Format

```json
{
  "title": "Course Feedback Survey",
  "pages": [
    {
      "name": "page1",
      "title": "General Feedback",
      "elements": [
        {
          "type": "rating",
          "name": "overall_rating",
          "title": "How would you rate this course overall?",
          "rateMin": 1,
          "rateMax": 5,
          "minRateDescription": "Poor",
          "maxRateDescription": "Excellent",
          "isRequired": true
        },
        {
          "type": "comment",
          "name": "feedback",
          "title": "What did you like most about this course?",
          "rows": 4
        },
        {
          "type": "radiogroup",
          "name": "recommend",
          "title": "Would you recommend this course?",
          "choices": ["Yes", "No", "Maybe"],
          "isRequired": true
        }
      ]
    }
  ],
  "showQuestionNumbers": "on",
  "showProgressBar": "top",
  "completedHtml": "<h3>Thank you for your feedback!</h3>"
}
```

### Available Question Types

| Type | Description | Example Use |
|------|-------------|-------------|
| `text` | Single line text | Name, email |
| `comment` | Multi-line textarea | Feedback, description |
| `radiogroup` | Single choice | Yes/No, preference |
| `checkbox` | Multiple choice | Select all that apply |
| `dropdown` | Select dropdown | Country, category |
| `rating` | Star/number rating | Satisfaction score |
| `boolean` | Yes/No toggle | Agreement, confirmation |
| `matrix` | Grid questions | Multiple criteria rating |
| `file` | File upload | Document submission |
| `expression` | Calculated value | Dynamic scoring |

---

## Core Components

### 1. QuestionnaireRenderer.jsx

**Location:** `client/src/components/questionnaire/QuestionnaireRenderer.jsx`

```jsx
import { Model } from 'survey-core';
import { Survey } from 'survey-react-ui';
import 'survey-core/defaultV2.min.css';

const QuestionnaireRenderer = ({
  questionnaireId,
  questionnaire: preloadedQuestionnaire,
  enrollmentId,
  onComplete,
  onPartialSave,
  readOnly = false,
  existingResponse,
  theme = 'defaultV2'
}) => {
  // Creates SurveyJS Model from schema
  // Handles form submission
  // Supports partial saves for multi-page forms
  // Read-only mode for viewing responses
};
```

**Key Features:**
- Loads questionnaire by ID or accepts preloaded data
- Submits responses to API
- Partial save on page change
- Read-only display mode
- Custom themes support

### 2. QuestionnaireModal.jsx

**Location:** `client/src/components/questionnaire/QuestionnaireModal.jsx`

Modal wrapper for showing questionnaires during course enrollment flow.

### 3. useQuestionnaire.js Hook

**Location:** `client/src/hooks/useQuestionnaire.js`

```javascript
// Get questionnaires for a course
const { questionnaires, loading } = useCourseQuestionnaires(courseId);

// Get user's response for a questionnaire
const { response, hasCompleted } = useQuestionnaireResponse(questionnaireId, userId);
```

---

## API Endpoints

**Base URL:** `/api/questionnaires`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all questionnaires (admin) |
| GET | `/:id` | Get single questionnaire |
| POST | `/` | Create questionnaire (admin) |
| PUT | `/:id` | Update questionnaire (admin) |
| DELETE | `/:id` | Delete questionnaire (admin) |
| POST | `/:id/responses` | Submit response |
| GET | `/:id/responses` | Get all responses (admin) |
| GET | `/:id/responses/:responseId` | Get single response |
| PUT | `/:id/responses/:responseId` | Update response |
| GET | `/course/:courseId` | Get questionnaires for course |
| POST | `/:id/clone` | Clone questionnaire (admin) |

---

## Admin UI Features

**Location:** `client/src/pages/admin/QuestionnaireManager.jsx`

**Route:** `/admin/questionnaires`

**Features:**
1. **List View** - All questionnaires with status, course link
2. **JSON Editor** - Edit SurveyJS schema directly
3. **Preview** - Live preview of form
4. **Response Viewer** - View submitted responses
5. **Export** - Export responses to CSV/JSON
6. **Clone** - Duplicate existing questionnaire

---

## Use Cases

### 1. Pre-Course Registration Questionnaire

```javascript
// Link questionnaire to course
const questionnaire = await Questionnaire.create({
  title: 'Pre-Course Requirements',
  course_id: courseId,
  is_required: true,
  schema: {
    pages: [{
      elements: [
        { type: 'text', name: 'experience', title: 'Years of experience?' },
        { type: 'checkbox', name: 'prerequisites', title: 'Select completed prerequisites' }
      ]
    }]
  }
});
```

### 2. Post-Course Feedback

```javascript
// Trigger after course completion
hooks.addAction('course.completed', async ({ userId, courseId }) => {
  const questionnaire = await Questionnaire.findByCourse(courseId, 'feedback');
  if (questionnaire) {
    // Notify user to complete feedback
  }
});
```

### 3. Assessment with Scoring

```javascript
// Schema with correct answers
{
  "pages": [{
    "elements": [{
      "type": "radiogroup",
      "name": "q1",
      "title": "What is 2 + 2?",
      "choices": ["3", "4", "5"],
      "correctAnswer": "4"
    }]
  }],
  "showCorrectAnswer": "afterQuiz"
}
```

---

## Response Data Structure

```json
{
  "id": "uuid",
  "questionnaire_id": "uuid",
  "user_id": "uuid",
  "enrollment_id": "uuid",
  "responses": {
    "overall_rating": 5,
    "feedback": "Great course!",
    "recommend": "Yes"
  },
  "is_complete": true,
  "score": 85.5,
  "completed_at": "2026-01-08T12:00:00Z"
}
```

---

## Troubleshooting

### Form Not Rendering
1. Verify `survey-core` and `survey-react-ui` installed
2. Check JSON schema syntax
3. Import CSS: `import 'survey-core/defaultV2.min.css';`

### Responses Not Saving
1. Check API endpoint accessible
2. Verify user authenticated
3. Check questionnaire_id valid
4. Review server logs for errors

### Styling Issues
1. Default theme: `defaultV2`
2. Custom CSS can override SurveyJS styles
3. Dark mode requires custom theme

---

## Files Reference

| File | Purpose |
|------|---------|
| `server/migrations/072_create_questionnaires.sql` | Database schema |
| `server/models/Questionnaire.pg.js` | Questionnaire CRUD |
| `server/models/QuestionnaireResponse.pg.js` | Response management |
| `server/controllers/questionnaireController.js` | API handlers |
| `server/routes/questionnaireRoutes.js` | REST routes |
| `client/src/components/questionnaire/QuestionnaireRenderer.jsx` | Form renderer |
| `client/src/components/questionnaire/QuestionnaireModal.jsx` | Modal wrapper |
| `client/src/hooks/useQuestionnaire.js` | React hooks |
| `client/src/pages/admin/QuestionnaireManager.jsx` | Admin UI |

---

## Related Skills

- [Plugin System Architecture](../advanced-features/PLUGIN_SYSTEM_ARCHITECTURE.md)
- [Database Patterns](../database-solutions/)
- [API Patterns](../api-patterns/)

---

*Last Updated: January 8, 2026*
*Author: Claude AI Assistant*
*Project: MERN Community LMS*
