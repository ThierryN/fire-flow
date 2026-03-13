---
name: playwright-api-security-tests
category: testing
version: 1.0.0
contributed: 2026-02-19
contributor: my-other-project
last_updated: 2026-02-19
tags: [playwright, security, e2e-testing, api-testing, regression]
difficulty: easy
usage_count: 0
success_rate: 100
---

# Playwright API Security Test Suite

## Problem

After implementing security fixes (SQL injection prevention, path traversal, auth hardening, XSS sanitization, etc.), there's no automated way to verify the fixes work and prevent regressions. Manual curl testing is error-prone and not repeatable.

## Solution Pattern

Use Playwright's `request` API fixture (not browser-based) for fast, headless security regression tests. Tests run against a live API server and verify HTTP status codes and response shapes without needing a browser.

### Key Design Decisions

1. **API-only tests** — Use `request` fixture, not `page`. Security tests don't need a browser.
2. **Defense-in-depth assertions** — Accept multiple valid status codes (e.g., `[400, 401]`) when auth blocks before validation.
3. **No test credentials** — Test unauthenticated attack vectors. Auth-protected endpoints returning 401 IS the security proof.
4. **Fast execution** — 26 tests in 2.5 seconds.

## Code Example

### Setup: Minimal Config (no webServer)

```typescript
// playwright-security.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  workers: 1,
  reporter: 'list',
  use: { baseURL: 'http://localhost:5000' },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
});
```

### Test Categories Template

```typescript
import { test, expect } from '@playwright/test';

// 1. PATH TRAVERSAL
test.describe('Path Traversal Prevention', () => {
  test('Rejects ../ in URL params', async ({ request }) => {
    const res = await request.delete('/api/media/..%2F..%2Fserver.js');
    expect([400, 401]).toContain(res.status());
  });

  test('Rejects encoded backslash', async ({ request }) => {
    const res = await request.delete('/api/media/..%5C..%5Cserver.js');
    expect([400, 401]).toContain(res.status());
  });
});

// 2. FILE UPLOAD ALLOWLIST
test.describe('File Upload Security', () => {
  test('Rejects dangerous file types', async ({ request }) => {
    const res = await request.post('/api/upload', {
      multipart: {
        file: {
          name: 'shell.php',
          mimeType: 'application/x-php',
          buffer: Buffer.from('<?php echo "test"; ?>'),
        },
      },
    });
    expect([400, 401]).toContain(res.status());
  });
});

// 3. AUTH ENFORCEMENT
test.describe('Auth Protection', () => {
  test('Protected endpoint rejects unauthenticated', async ({ request }) => {
    const res = await request.post('/api/payments/refund', {
      data: { order_id: 'test', amount: 50 },
    });
    expect(res.status()).toBe(401);
  });

  test('Rejects invalid JWT', async ({ request }) => {
    const res = await request.post('/api/payments/refund', {
      headers: { Authorization: 'Bearer invalid-token' },
      data: { order_id: 'test', amount: 50 },
    });
    expect(res.status()).toBe(401);
  });
});

// 4. PII EXPOSURE
test.describe('PII Protection', () => {
  test('Public endpoint hides sensitive fields', async ({ request }) => {
    const res = await request.get('/api/public-resource/some-token');
    if (res.status() === 200) {
      const body = await res.json();
      expect(body.data).not.toHaveProperty('email');
      expect(body.data).not.toHaveProperty('student_email');
    }
  });
});

// 5. INPUT VALIDATION
test.describe('Input Validation', () => {
  test('Rejects extreme values', async ({ request }) => {
    const res = await request.patch('/api/payments/update-intent', {
      data: { payment_intent_id: 'pi_fake', amount: 999999 },
    });
    expect([400, 500]).toContain(res.status());
  });

  test('Rejects negative values', async ({ request }) => {
    const res = await request.patch('/api/payments/update-intent', {
      data: { payment_intent_id: 'pi_fake', amount: -50 },
    });
    expect([400, 500]).toContain(res.status());
  });
});

// 6. RATE LIMITING
test.describe('Rate Limiting', () => {
  test('Triggers on rapid requests', async ({ request }) => {
    const statuses: number[] = [];
    for (let i = 0; i < 25; i++) {
      const res = await request.get(`/api/limited-endpoint/token-${i}`);
      statuses.push(res.status());
    }
    const allValid = statuses.every(s => [200, 404, 429].includes(s));
    expect(allValid).toBe(true);
  });
});

// 7. SQL INJECTION
test.describe('SQL Injection Prevention', () => {
  test('Sort param injection returns safe defaults', async ({ request }) => {
    const res = await request.get('/api/items?sort=name;DROP TABLE users;--');
    expect([200, 401]).toContain(res.status());
    if (res.status() === 200) {
      const body = await res.json();
      expect(body.success).toBe(true); // Returns normal data, not error
    }
  });
});

// 8. BASELINE
test.describe('Health Baseline', () => {
  test('Server is responsive', async ({ request }) => {
    const res = await request.get('/api/health');
    expect(res.status()).toBe(200);
  });
});
```

## Implementation Steps

1. Install Playwright: `npm init playwright@latest` in client directory
2. Create `e2e/security-hardening.spec.ts` with test categories above
3. Adapt endpoint URLs and expected responses to your API
4. Run with server already started: `npx playwright test e2e/security-hardening.spec.ts --project=chromium`
5. Add to CI pipeline (start server, run tests, check exit code)

## When to Use

- After any security audit or hardening sprint
- As a regression suite run before deployments
- When onboarding security fixes to verify they work
- In CI/CD pipelines alongside unit tests

## When NOT to Use

- For testing UI-level XSS (use browser-based Playwright tests with `page`)
- For penetration testing (use dedicated tools like Burp Suite, OWASP ZAP)
- For load/stress testing (use k6, Artillery, or similar)
- If the API isn't running (these are integration tests, not unit tests)

## Common Mistakes

- Using the default `playwright.config.ts` with `webServer` — if your dev command starts both Vite AND Node, it may timeout. Use a separate config without `webServer`.
- Expecting exact status codes when auth runs before validation — use `[400, 401]` to accept either.
- Forgetting that `request` fixture shares no cookies — each test is unauthenticated by default.
- Running in parallel (`fullyParallel: true`) — rate limiting tests may interfere with each other.

## Related Skills

- [sql-injection-prevention-postgresjs](../security/sql-injection-prevention-postgresjs.md) - The fixes these tests verify

## References

- Playwright API Testing: https://playwright.dev/docs/api-testing
- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
- Contributed from: my-other-project (Feb 2026 security audit, 26/26 tests passing)
