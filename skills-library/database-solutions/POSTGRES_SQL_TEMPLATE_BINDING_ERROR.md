# PostgreSQL Tagged Template Literal Binding Errors - Solution & Prevention

## The Problem

When using the `postgres` (porsager/postgres) library with tagged template literals, nested template compositions cause binding errors. The error message is cryptic and doesn't point to the actual issue.

### Error Message
```
PostgresError: Expected 1 bindings, saw 0
```

Or variations like:
```
PostgresError: bind message supplies 0 parameters, but prepared statement requires 1
```

### Why It Was Hard

- The error doesn't indicate which query or which binding failed
- Nested `sql` template literals appear to work in simple cases
- The SQL-compatibility layer (proxy pattern) masks the actual postgres.js instance
- Dynamic query building with conditionals creates complex nesting that breaks

### Impact

- API endpoints return 500 errors
- Courses, users, or other data fail to load
- The application appears broken with no obvious cause
- Debugging requires understanding postgres.js internals

---

## The Solution

### Root Cause

The postgres.js tagged template literal syntax doesn't support composing nested template literals when building dynamic queries with conditionals.

**Bad Code (Breaks):**
```javascript
export const getCourses = async (filters = {}) => {
  let query = sql`SELECT * FROM courses`;
  let hasWhere = false;

  if (filters.is_published !== undefined) {
    // This creates a nested template that breaks binding
    query = sql`${query} WHERE is_published = ${filters.is_published}`;
    hasWhere = true;
  }

  if (filters.category) {
    const whereOrAnd = hasWhere ? sql`AND` : sql`WHERE`;
    // Another nested composition - bindings get lost
    query = sql`${query} ${whereOrAnd} category = ${filters.category}`;
  }

  return await query; // ERROR: Expected N bindings, saw 0
};
```

### How to Fix

Use `sql.unsafe()` with manual parameterized queries for dynamic query building:

**Good Code (Works):**
```javascript
export const getCourses = async (filters = {}, options = {}) => {
  const conditions = [];
  const values = [];
  let paramIndex = 1;

  // Build conditions dynamically
  if (filters.is_published !== undefined) {
    conditions.push(`is_published = $${paramIndex++}`);
    values.push(filters.is_published);
  }

  if (filters.category) {
    conditions.push(`category = $${paramIndex++}`);
    values.push(filters.category);
  }

  if (filters.instructor_id) {
    conditions.push(`instructor_id = $${paramIndex++}`);
    values.push(filters.instructor_id);
  }

  // Build the complete query
  let queryText = 'SELECT * FROM courses';
  if (conditions.length > 0) {
    queryText += ' WHERE ' + conditions.join(' AND ');
  }
  queryText += ' ORDER BY created_at DESC';

  // Add pagination
  if (options.limit) {
    queryText += ` LIMIT $${paramIndex++}`;
    values.push(options.limit);
  }
  if (options.offset) {
    queryText += ` OFFSET $${paramIndex++}`;
    values.push(options.offset);
  }

  // Execute with sql.unsafe() - handles parameterized queries correctly
  const result = await sql.unsafe(queryText, values);
  return result;
};
```

### When to Use Each Approach

| Scenario | Use This |
|----------|----------|
| Static queries (no conditionals) | `sql`SELECT * FROM users WHERE id = ${id}`` |
| Dynamic queries with conditionals | `sql.unsafe(queryText, values)` |
| INSERT with dynamic columns | `sql.unsafe()` with built column/value lists |
| UPDATE with dynamic fields | `sql.unsafe()` with built SET clause |

### Complete UPDATE Example

```javascript
export const updateCourse = async (id, updateData) => {
  const fieldMapping = {
    isPublished: 'is_published',
    coverImage: 'cover_image',
    // ... map camelCase to snake_case
  };

  const mappedData = {};
  Object.keys(updateData).forEach(key => {
    if (key !== 'id') {
      const dbField = fieldMapping[key] || key;
      mappedData[dbField] = updateData[key];
    }
  });

  const fields = Object.keys(mappedData).filter(
    field => mappedData[field] !== undefined
  );

  if (fields.length === 0) {
    return (await sql`SELECT * FROM courses WHERE id = ${id}`)[0];
  }

  // Build SET clause: "field1" = $1, "field2" = $2
  const setClause = fields.map((f, i) => `"${f}" = $${i + 1}`).join(', ');
  const values = fields.map(f => mappedData[f]);

  // id is the last parameter
  const result = await sql.unsafe(
    `UPDATE courses SET ${setClause} WHERE id = $${values.length + 1} RETURNING *`,
    [...values, id]
  );

  return result[0];
};
```

---

## Testing the Fix

### Before (Broken)
```bash
GET /api/courses?is_published=true
Response: 500 Internal Server Error
Log: PostgresError: Expected 1 bindings, saw 0
```

### After (Working)
```bash
GET /api/courses?is_published=true
Response: 200 OK
Body: [{ id: "...", title: "Course 1", ... }]
```

### Test Cases
```javascript
// Test dynamic filtering
const published = await getCourses({ is_published: true });
const byCategory = await getCourses({ category: 'programming' });
const combined = await getCourses({
  is_published: true,
  category: 'programming',
  instructor_id: 'abc-123'
});
const paginated = await getCourses({}, { limit: 10, offset: 20 });
```

---

## Prevention

1. **Never nest sql template literals** for conditional query building
2. **Use sql.unsafe()** for any dynamic query construction
3. **Track parameter index** manually with `$${paramIndex++}`
4. **Always use parameterized queries** - never interpolate values directly
5. **Test with multiple filter combinations** before deploying

---

## Related Patterns

- Dynamic INSERT queries with variable columns
- Bulk UPDATE operations
- Search queries with optional filters
- Pagination with variable page sizes

---

## Common Mistakes to Avoid

- Using `sql`${sql`...`}`` nesting for dynamic parts
- Forgetting to increment parameter index
- Mixing postgres.js template syntax with raw string interpolation
- Not testing with multiple filter combinations
- Using string interpolation for values (SQL injection risk!)

---

## Resources

- [postgres.js Documentation](https://github.com/porsager/postgres)
- [PostgreSQL Parameterized Queries](https://www.postgresql.org/docs/current/sql-prepare.html)

---

## Time to Implement

**15-30 minutes** to refactor a broken query function

## Difficulty Level

This problem is easy to solve once understood, but hard to diagnose initially.

---

**Author Notes:**
This issue cost 2+ hours of debugging. The error message gives no indication of which query failed or why. The key insight: postgres.js tagged templates are for static queries only. Any dynamic query building needs `sql.unsafe()` with manual parameter tracking.
