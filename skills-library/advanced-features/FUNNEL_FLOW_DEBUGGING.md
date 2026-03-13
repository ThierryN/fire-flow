# Funnel Flow Debugging - Questionnaire & Payment Issues

## The Problem

Users report funnel steps auto-completing, questionnaires not displaying, and "Payment Failed" on free course enrollments even when everything appears configured correctly in the admin UI.

### Common Symptoms

1. **Questionnaire auto-completes** - Shows "[QuestionnaireStep] No questions configured, auto-completing" in console
2. **Payment Failed on success page** - Free course with $0 donation shows payment error
3. **Settings not taking effect** - Admin links questionnaire but step still skips

### Why It Was Hard

- Multiple failure points: frontend settings dialog, backend storage, runtime loading
- JSON field naming mismatch between frontend expectations and database schema
- SurveyJS questionnaire format has nested structure (pages → elements)
- Free enrollment flow has different code path than paid flow
- Success page lookup uses `progress_data->>'id'` which must be explicitly set

### Impact

- Users cannot complete funnel registration
- Free courses become inaccessible
- Questionnaire responses not collected

---

## The Solution

### Issue 1: Questionnaire Not Displaying

**Root Cause:** Frontend was reading `questionnaire.questions` but database stores in `questionnaire.schema`

**Bad Code:**
```javascript
// StepSettingsDialog.jsx - WRONG field name
const schema = typeof questionnaire.questions === 'string'
    ? JSON.parse(questionnaire.questions)
    : questionnaire.questions;
```

**Good Code:**
```javascript
// StepSettingsDialog.jsx - CORRECT field name
let schema = questionnaire.schema;

// Handle multiple levels of JSON encoding (common in PostgreSQL JSONB)
while (typeof schema === 'string') {
    try {
        schema = JSON.parse(schema);
    } catch {
        break;
    }
}
```

### Issue 2: Runtime Questionnaire Fetch Fallback

Even after fixing settings dialog, existing funnels have empty `questions: []` in steps_config.

**Solution:** Add runtime fetch in QuestionnaireStep:

```javascript
// QuestionnaireStep.jsx
useEffect(() => {
    const questionnaireId = step.settings?.questionnaire_id;
    if (questionnaireId && questions.length === 0 && !loadingQuestions) {
        fetchQuestionnaire(questionnaireId);
    }
}, [step.settings?.questionnaire_id]);

const fetchQuestionnaire = async (questionnaireId) => {
    const response = await axios.get(`/api/questionnaires/${questionnaireId}`);
    const questionnaire = response.data.data;

    // Parse schema with multiple encoding levels
    let schema = questionnaire.schema;
    while (typeof schema === 'string') {
        try { schema = JSON.parse(schema); } catch { break; }
    }

    const extractedQuestions = extractQuestionsFromSchema(schema);
    setQuestions(extractedQuestions);
};
```

### Issue 3: Free Enrollment "Payment Failed"

**Root Cause 1:** `completeFreeEnrollment` checks if course has a price and rejects even if funnel is marked as free.

**Fix:**
```javascript
// funnelFlowController.js
const isFunnelFree = funnel.is_free === true;

// Allow if funnel explicitly marked free OR price is $0
if (!isFunnelFree && effectivePrice > 0) {
    return res.status(400).json({
        message: 'This course requires payment.'
    });
}
```

**Root Cause 2:** Success page looks for `progress_data->>'id'` but progressId not stored at top level.

**Fix:**
```javascript
// Explicitly include progressId in progress_data
const progressData = {
    id: progressId, // For getSuccessData lookup
    ...progress
};

await sql`
    INSERT INTO funnel_enrollments (progress_data, ...)
    VALUES (${JSON.stringify(progressData)}, ...)
`;
```

---

## Database Verification Script

```javascript
// check-funnel.cjs - Run in server/ directory
const postgres = require("postgres");
require("dotenv").config();

const sql = postgres(process.env.VITE_SUPABASE_DB_URL);

(async () => {
    // Check funnel steps_config
    const funnels = await sql`
        SELECT id, title, steps_config
        FROM funnels WHERE is_active = true
    `;

    funnels.forEach(f => {
        console.log("\nFunnel:", f.title);
        const sc = typeof f.steps_config === "string"
            ? JSON.parse(f.steps_config) : f.steps_config;
        sc?.steps?.forEach((s, i) => {
            console.log(`  Step ${i+1}: ${s.type}`);
            console.log(`    settings:`, JSON.stringify(s.settings || {}));
        });
    });

    // Check questionnaire schema format
    const questionnaires = await sql`
        SELECT id, title, schema FROM questionnaires LIMIT 2
    `;
    questionnaires.forEach(q => {
        console.log("\nQuestionnaire:", q.title);
        const schema = typeof q.schema === "string"
            ? JSON.parse(q.schema) : q.schema;
        console.log("Structure:", JSON.stringify(schema, null, 2).substring(0, 500));
    });

    await sql.end();
})();
```

---

## SurveyJS Question Extraction

The questionnaire uses SurveyJS format:

```javascript
const extractQuestionsFromSchema = (schema) => {
    if (!schema) return [];

    const questions = [];
    const pages = schema.pages || [schema];

    pages.forEach(page => {
        const elements = page.elements || page.questions || [];
        elements.forEach(element => {
            const question = {
                id: element.name,
                text: element.title || element.name,
                type: mapQuestionType(element.type),
                required: element.isRequired || false
            };

            if (element.choices) {
                question.options = element.choices.map(choice =>
                    typeof choice === 'string'
                        ? { value: choice, label: choice }
                        : { value: choice.value, label: choice.text }
                );
            }

            questions.push(question);
        });
    });

    return questions;
};

const mapQuestionType = (surveyJsType) => ({
    'text': 'text',
    'comment': 'textarea',
    'radiogroup': 'radio',
    'checkbox': 'checkbox',
    'dropdown': 'select'
}[surveyJsType] || 'text');
```

---

## Testing the Fix

### Verify Questionnaire Loads

1. Open browser DevTools → Network tab
2. Navigate to funnel
3. Check for `GET /api/questionnaires/{id}` request
4. Verify questions array in response has elements

### Verify Free Enrollment

1. Go through funnel with $0 donation
2. Check PM2 logs: `pm2 logs --lines 50`
3. Look for `[completeFreeEnrollment] Processing free enrollment`
4. Verify no 400 error about "requires payment"

### Verify Success Page

1. Check URL has `progressId` parameter
2. Verify `GET /api/funnel-flow/success/{progressId}` returns enrollment
3. If 404, check `funnel_enrollments.progress_data->>'id'` matches progressId

---

## Prevention

1. **Database column naming** - Document actual column names, not assumed ones
2. **Runtime fallbacks** - Always fetch data if settings are missing
3. **Explicit IDs** - Store lookup IDs at top level of JSONB fields
4. **Boolean checks** - Use `=== true` for boolean fields that might be null

---

## Common Mistakes to Avoid

- ❌ Assuming `questionnaire.questions` when it's `questionnaire.schema`
- ❌ Trusting stored `questions: []` array without fallback
- ❌ Checking only `price > 0` without considering `is_free` flag
- ❌ Storing nested progressId without top-level copy for lookups
- ❌ Not handling double-encoded JSON from PostgreSQL

---

## Key Files

| File | Purpose |
|------|---------|
| `client/src/components/funnel/StepSettingsDialog.jsx` | Links questionnaires to steps |
| `client/src/components/funnel/steps/QuestionnaireStep.jsx` | Renders questions, has runtime fetch |
| `client/src/components/funnel/steps/PaymentStep.jsx` | Handles free vs paid flows |
| `server/controllers/funnelFlowController.js` | Backend: completeFreeEnrollment, getSuccessData |
| `client/src/pages/FunnelSuccessPage.jsx` | Shows enrollment or "Payment Failed" |

---

## Debugging Checklist

- [ ] Check browser console for auto-complete messages
- [ ] Query database for steps_config settings
- [ ] Verify questionnaire schema column has data
- [ ] Check PM2 logs for backend errors
- [ ] Verify progress_data->>'id' in funnel_enrollments
- [ ] Confirm funnel.is_free flag in database

---

## Time to Implement

**30-60 minutes** to diagnose and fix all three issues

## Difficulty Level

⭐⭐⭐ (3/5) - Multiple interconnected systems, requires database queries to verify

---

**Author Notes:**
This debugging session revealed how field naming mismatches and missing fallbacks can cascade into user-visible failures. The key insight: always verify database schema matches frontend expectations, and add runtime fallbacks for critical data.
