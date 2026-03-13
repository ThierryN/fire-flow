---
name: e2e-playwright-patterns
category: testing
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [testing, e2e, playwright, browser, ui]
difficulty: medium
---

# E2E Playwright Patterns

## Problem

Frontend looks correct in development but breaks in production. User flows span multiple pages, involve authentication, form submissions, and API calls. Manual QA can't cover all paths.

## Solution Pattern

Playwright end-to-end tests that simulate real user behavior: login, navigate, fill forms, click buttons, verify results — all in a real browser.

## Code Example

```typescript
import { test, expect } from '@playwright/test';

test.describe('Course enrollment flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login as student
    await page.goto('/login');
    await page.fill('[name="email"]', 'student@test.com');
    await page.fill('[name="password"]', 'testpass');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('student can browse and enroll in a course', async ({ page }) => {
    // Navigate to courses
    await page.click('text=Browse Courses');
    await expect(page.locator('h1')).toHaveText('Available Courses');

    // Click first course
    await page.click('.course-card >> nth=0');
    await expect(page.locator('.course-title')).toBeVisible();

    // Enroll
    await page.click('button:has-text("Enroll")');
    await expect(page.locator('.enrollment-success')).toBeVisible();

    // Verify in dashboard
    await page.goto('/dashboard');
    await expect(page.locator('.my-courses')).toContainText('Test Course');
  });
});
```

## Key Patterns

### 1. Page Object Model (for complex flows)
```typescript
class LoginPage {
  constructor(private page: Page) {}
  async login(email: string, password: string) {
    await this.page.fill('[name="email"]', email);
    await this.page.fill('[name="password"]', password);
    await this.page.click('button[type="submit"]');
  }
}
```

### 2. Test Isolation
- Each test should be independent
- Use API calls for setup (faster than UI)
- Clean state between tests

### 3. Selectors Priority
1. `getByRole()` — Best (accessibility-driven)
2. `getByText()` — Good (user-visible)
3. `data-testid` — Acceptable (stable but not semantic)
4. CSS selectors — Last resort (fragile)

### 4. Waiting
```typescript
// Good — explicit wait for condition
await expect(page.locator('.result')).toBeVisible({ timeout: 5000 });

// Bad — arbitrary sleep
await page.waitForTimeout(3000);
```

## When to Use
- Critical user flows (login, checkout, enrollment)
- Multi-page interactions
- Form submission and validation
- After major UI changes

## When NOT to Use
- API testing (use integration tests)
- Unit logic (use unit tests)
- Visual regression (use screenshot comparison tools)
