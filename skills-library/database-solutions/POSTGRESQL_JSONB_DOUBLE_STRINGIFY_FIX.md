# PostgreSQL JSONB Double-Stringified JSON - Solution & Prevention

## The Problem

When exporting or displaying data from PostgreSQL JSONB columns, JavaScript's `Object.entries()` iterates **character-by-character** instead of returning key-value pairs.

### Error Symptoms
```
PDF/Screen Output:
0: {
1: "
2: e
3: m
4: a
5: i
6: l
...
```

Instead of:
```
email: user@example.com
name: John Doe
```

### Why It Was Hard

- No error is thrown - code "works" but output is wrong
- Happens silently in production
- Requires understanding of JavaScript type coercion
- PostgreSQL JSONB can return data as stringified JSON string

### Impact

- Export documents (PDF, CSV) are unusable
- Legal documents become invalid for court records
- User-facing data displays garbage
- Silent data corruption in reports

---

## The Solution

### Root Cause

PostgreSQL JSONB columns sometimes return **double-stringified JSON**:
```javascript
// What you expect:
responses = { email: "user@example.com" }

// What you get from database:
responses = '{"email":"user@example.com"}'  // stringified once
// OR
responses = '"{\\"email\\":\\"user@example.com\\"}"'  // double-stringified!
```

When you call `Object.entries()` on a STRING:
```javascript
Object.entries('hello')
// Returns: [["0", "h"], ["1", "e"], ["2", "l"], ["3", "l"], ["4", "o"]]
```

### How to Fix

Always parse JSONB data with **double-parse protection**:

```javascript
// Helper to safely parse JSONB responses
const parseResponses = (resp) => {
  let parsed = resp || {};

  // First parse (if string)
  if (typeof parsed === 'string') {
    try { parsed = JSON.parse(parsed); } catch { parsed = {}; }
  }

  // Second parse (if still string - double-stringified)
  if (typeof parsed === 'string') {
    try { parsed = JSON.parse(parsed); } catch { parsed = {}; }
  }

  return parsed;
};
```

### Code Example

**Before (broken):**
```javascript
// WRONG - crashes if responses is a string
data.forEach(r => {
  Object.entries(r.responses).forEach(([key, value]) => {
    console.log(`${key}: ${value}`);
  });
});
// Output: 0: {, 1: ", 2: e, 3: m...
```

**After (fixed):**
```javascript
// CORRECT - handles all cases
const parseResponses = (resp) => {
  let parsed = resp || {};
  if (typeof parsed === 'string') {
    try { parsed = JSON.parse(parsed); } catch { parsed = {}; }
  }
  if (typeof parsed === 'string') {
    try { parsed = JSON.parse(parsed); } catch { parsed = {}; }
  }
  return parsed;
};

data.forEach(r => {
  const responses = parseResponses(r.responses);
  Object.entries(responses).forEach(([key, value]) => {
    console.log(`${key}: ${value}`);
  });
});
// Output: email: user@example.com, name: John Doe
```

---

## Testing the Fix

### Before
```
PDF Export shows:
0: {
1: "
2: e
...
```

### After
```
PDF Export shows:
Question 1: What is your email?
Answer: user@example.com

Question 2: What is your name?
Answer: John Doe
```

### Quick Test
```javascript
// Test helper function
const testCases = [
  { email: 'test@test.com' },                    // Object
  '{"email":"test@test.com"}',                   // Single stringify
  '"{\\"email\\":\\"test@test.com\\"}"',         // Double stringify
  null,                                           // Null
  undefined,                                      // Undefined
];

testCases.forEach((input, i) => {
  const result = parseResponses(input);
  console.log(`Case ${i}: ${typeof result} - email: ${result.email}`);
});
```

---

## Prevention

1. **Always use parseResponses helper** for any JSONB column data
2. **Check typeof before Object.entries/keys/values**
3. **Add defensive parsing** at the data access layer
4. **Log types during debugging**: `console.log(typeof responses, responses)`
5. **Consider normalizing** at the API/model level

### API-Level Fix (Optional)
```javascript
// In your model or controller
const getResponses = async (id) => {
  const result = await sql`SELECT * FROM questionnaire_responses WHERE id = ${id}`;
  const row = result[0];

  // Normalize at data layer
  if (row && typeof row.responses === 'string') {
    try { row.responses = JSON.parse(row.responses); } catch {}
  }
  if (row && typeof row.responses === 'string') {
    try { row.responses = JSON.parse(row.responses); } catch {}
  }

  return row;
};
```

---

## Related Patterns

- [JSON Data Handling](../patterns-standards/JSON_DATA_HANDLING.md)
- [PostgreSQL JSONB Best Practices](../database-solutions/POSTGRESQL_JSONB_PATTERNS.md)

---

## Common Mistakes to Avoid

- ❌ **Assuming JSONB always returns objects** - It can return strings
- ❌ **Single JSON.parse** - May need double parse
- ❌ **Not handling null/undefined** - Always default to empty object
- ❌ **Catching parse errors silently** - Log them for debugging
- ❌ **Trusting Object.entries blindly** - Check type first

---

## When This Happens

Common scenarios where double-stringify occurs:
1. **ORM serialization** - Some ORMs double-serialize
2. **API responses** - JSON within JSON
3. **Database migrations** - Data inserted as strings
4. **Copy/paste data** - Manual data entry as string
5. **Legacy data** - Old records stored differently

---

## Resources

- [MDN Object.entries](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/entries)
- [PostgreSQL JSONB Docs](https://www.postgresql.org/docs/current/datatype-json.html)
- [postgres.js library](https://github.com/porsager/postgres)

---

## Time to Implement

**5 minutes** - Add helper function and use it where needed

## Difficulty Level

⭐⭐ (2/5) - Easy fix once identified, but hard to diagnose initially

---

**Author Notes:**

This bug wasted 30+ minutes of debugging time. The symptoms (vertical characters in PDF) were bizarre and didn't immediately point to JSON parsing. The key insight was checking `typeof responses` before iterating.

Always ask: **"Is this actually an object, or is it a string that looks like an object?"**

Real-world example: QuestionnaireManager.jsx PDF export for legal documents.
