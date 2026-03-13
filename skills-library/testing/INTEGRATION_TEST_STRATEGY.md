---
name: integration-test-strategy
category: testing
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [testing, integration, api, database, supertest]
difficulty: medium
---

# Integration Test Strategy

## Problem

Unit tests pass but the app breaks because components don't work together. Database queries, API routes, middleware chains, and authentication flows have integration seams that unit tests miss.

## Solution Pattern

Test real interactions between components with a test database, actual HTTP requests, and real middleware — but with controlled test data and isolated state.

## Code Example

```typescript
// Express API integration test
import request from 'supertest';
import { app } from '../src/app';
import { db } from '../src/database';

describe('POST /api/courses', () => {
  beforeAll(async () => {
    await db.migrate.latest();
    await db.seed.run();
  });

  afterAll(async () => {
    await db.destroy();
  });

  test('creates course with valid data and auth', async () => {
    const token = await getTestToken('admin');

    const res = await request(app)
      .post('/api/courses')
      .set('Authorization', `Bearer ${token}`)
      .send({ title: 'Test Course', description: 'Integration test' });

    expect(res.status).toBe(201);
    expect(res.body.course.title).toBe('Test Course');

    // Verify side effects
    const saved = await db('courses').where({ id: res.body.course.id }).first();
    expect(saved).toBeTruthy();
  });

  test('rejects unauthenticated request', async () => {
    const res = await request(app)
      .post('/api/courses')
      .send({ title: 'Test' });

    expect(res.status).toBe(401);
  });
});
```

## Key Principles

1. **Real database** — Use test database, not mocks
2. **Real HTTP** — Use supertest, not function calls
3. **Real middleware** — Auth, validation, rate limiting all active
4. **Isolated state** — Each test suite seeds and cleans its own data
5. **Test the contract** — Status codes, response shapes, error formats

## When to Use
- API route testing
- Database query testing with real SQL
- Authentication/authorization flows
- Middleware chain behavior

## When NOT to Use
- Pure business logic (use unit tests)
- UI rendering (use component tests)
- Performance benchmarks (use load testing)
