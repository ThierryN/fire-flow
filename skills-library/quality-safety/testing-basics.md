# Skill: Testing Basics

**Category:** Quality & Safety
**Difficulty:** Beginner
**Applies to:** Node.js (Jest), any language

---

## Why Test?

Tests catch bugs before your users do. They also let you change code confidently — if the tests still pass, you didn't break anything. Untested code is code you're afraid to touch.

---

## Setup (Jest)

```bash
npm install --save-dev jest
```

```json
// package.json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch"
  }
}
```

---

## What to Test

**Test these:**
- Functions that calculate or transform data
- API endpoints (correct response, correct status code)
- Edge cases — what happens with empty input, null, zero, very large numbers
- Error paths — what happens when the database is down, or input is invalid

**Don't bother testing:**
- Third-party libraries (they have their own tests)
- Simple getters/setters with no logic
- Things that are just passing data through unchanged

---

## Pattern 1: Unit Test (Pure Function)

A unit test tests one function in isolation:

```js
// utils/price.js
function applyDiscount(price, discountPercent) {
  if (price < 0) throw new Error('Price cannot be negative');
  if (discountPercent < 0 || discountPercent > 100) throw new Error('Invalid discount');
  return price * (1 - discountPercent / 100);
}

module.exports = { applyDiscount };
```

```js
// utils/price.test.js
const { applyDiscount } = require('./price');

describe('applyDiscount', () => {
  test('applies 10% discount correctly', () => {
    expect(applyDiscount(100, 10)).toBe(90);
  });

  test('applies 0% discount (no change)', () => {
    expect(applyDiscount(100, 0)).toBe(100);
  });

  test('applies 100% discount (free)', () => {
    expect(applyDiscount(100, 100)).toBe(0);
  });

  test('throws on negative price', () => {
    expect(() => applyDiscount(-10, 10)).toThrow('Price cannot be negative');
  });

  test('throws on invalid discount over 100', () => {
    expect(() => applyDiscount(100, 110)).toThrow('Invalid discount');
  });
});
```

Run: `npm test`

---

## Pattern 2: API Test (Integration Test)

Test your actual routes with real HTTP requests:

```bash
npm install --save-dev supertest
```

```js
// routes/users.test.js
const request = require('supertest');
const app = require('../app');

describe('GET /api/users/:id', () => {
  test('returns 200 and user for valid id', async () => {
    const res = await request(app).get('/api/users/1');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('email');
  });

  test('returns 404 for non-existent user', async () => {
    const res = await request(app).get('/api/users/99999');
    expect(res.status).toBe(404);
    expect(res.body).toHaveProperty('error');
  });
});

describe('POST /api/users', () => {
  test('returns 400 when email is missing', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({ name: 'Jane' }); // no email
    expect(res.status).toBe(400);
  });
});
```

---

## The AAA Pattern

Every test follows this structure:

```js
test('description of what should happen', () => {
  // Arrange — set up the data
  const price = 100;
  const discount = 20;

  // Act — run the thing being tested
  const result = applyDiscount(price, discount);

  // Assert — verify the result
  expect(result).toBe(80);
});
```

---

## Most Useful Jest Matchers

```js
expect(value).toBe(42)              // strict equality (===)
expect(value).toEqual({ a: 1 })     // deep equality for objects
expect(value).toBeTruthy()          // any truthy value
expect(value).toBeNull()
expect(value).toBeGreaterThan(0)
expect(array).toHaveLength(3)
expect(object).toHaveProperty('name')
expect(string).toContain('hello')
expect(fn).toThrow('message')
```

---

## Aim for This Coverage

| Layer | What to Test |
|-------|-------------|
| Utility functions | All branches, all edge cases |
| API endpoints | Happy path + main error cases |
| Auth middleware | Blocked with no token, blocked with bad token, passes with good token |
| Database queries | At least the shape of the returned data |

---

*Fire Flow Skills Library — MIT License*
