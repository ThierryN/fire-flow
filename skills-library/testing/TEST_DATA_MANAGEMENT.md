---
name: test-data-management
category: testing
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [testing, fixtures, seeds, factories, test-data]
difficulty: easy
---

# Test Data Management

## Problem

Tests break when shared test data changes. Tests depend on specific database state. Seed data grows stale and doesn't match the current schema. Tests that modify data break other tests.

## Solution Pattern

Use factories for dynamic data, seeds for reference data, and transaction rollback for isolation.

## Code Example

```typescript
// Factory pattern — create data on demand
function createTestUser(overrides = {}) {
  return {
    email: `test-${Date.now()}@example.com`,
    name: 'Test User',
    role: 'student',
    ...overrides,
  };
}

function createTestCourse(overrides = {}) {
  return {
    title: `Course ${Date.now()}`,
    description: 'Test course',
    instructor_id: null,
    ...overrides,
  };
}

// Usage in tests
test('enrolled student sees course content', async () => {
  const user = await db('users').insert(createTestUser({ role: 'student' })).returning('*');
  const course = await db('courses').insert(createTestCourse()).returning('*');
  await db('enrollments').insert({ user_id: user[0].id, course_id: course[0].id });

  // Test with fresh, isolated data
  const content = await getCourseContent(user[0].id, course[0].id);
  expect(content).toBeDefined();
});
```

## Key Patterns

1. **Factories > Fixtures** — Generate unique data per test to prevent collisions
2. **Transaction rollback** — Wrap each test in a transaction, rollback after
3. **Minimal data** — Only create what the test needs, nothing more
4. **No shared mutable state** — Each test creates its own data

## When to Use
- Any test that requires database state
- Integration tests with multiple related records
- Tests that verify data relationships

## When NOT to Use
- Unit tests with mocked data
- Tests that don't touch the database
