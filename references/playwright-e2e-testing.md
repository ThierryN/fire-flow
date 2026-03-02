# Playwright E2E Testing Reference

> Patterns, setup, and integration guide for Playwright E2E testing in Dominion Flow

---

## Quick Reference

```
Tool: Playwright (https://playwright.dev)
Config: playwright.config.ts
Test Dir: tests/e2e/ or e2e/
Run: npx playwright test
Report: npx playwright show-report
Debug: npx playwright test --ui
```

---

## Setup

### Initial Installation

```bash
# Install Playwright
npm init playwright@latest

# Or add to existing project
npm install -D @playwright/test

# Install browsers
npx playwright install
```

### Recommended Config (playwright.config.ts)

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['list'],
    ...(process.env.CI ? [['github'] as const] : []),
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

### Package.json Scripts

```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:report": "playwright show-report",
    "test:e2e:update-snapshots": "playwright test --update-snapshots"
  }
}
```

---

## Test Patterns

### Page Object Model

```typescript
// tests/e2e/pages/login.page.ts
import { type Page, type Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByTestId('email');
    this.passwordInput = page.getByTestId('password');
    this.submitButton = page.getByRole('button', { name: 'Sign In' });
    this.errorMessage = page.getByTestId('error-message');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
```

### Authentication Setup

```typescript
// tests/e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test';

const authFile = 'tests/e2e/.auth/user.json';

setup('authenticate as user', async ({ page }) => {
  await page.goto('/login');
  await page.getByTestId('email').fill('test@example.com');
  await page.getByTestId('password').fill('testpassword');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: authFile });
});
```

### CRUD Flow Pattern

```typescript
// tests/e2e/crud-feature.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Feature CRUD', () => {
  test('create item', async ({ page }) => {
    await page.goto('/items/new');
    await page.getByLabel('Name').fill('Test Item');
    await page.getByRole('button', { name: 'Create' }).click();
    await expect(page.getByText('Item created')).toBeVisible();
  });

  test('read item', async ({ page }) => {
    await page.goto('/items');
    await expect(page.getByText('Test Item')).toBeVisible();
  });

  test('update item', async ({ page }) => {
    await page.goto('/items/1/edit');
    await page.getByLabel('Name').fill('Updated Item');
    await page.getByRole('button', { name: 'Save' }).click();
    await expect(page.getByText('Item updated')).toBeVisible();
  });

  test('delete item', async ({ page }) => {
    await page.goto('/items');
    await page.getByRole('button', { name: 'Delete' }).click();
    await page.getByRole('button', { name: 'Confirm' }).click();
    await expect(page.getByText('Test Item')).not.toBeVisible();
  });
});
```

### API Response Validation

```typescript
test('form submission calls correct API', async ({ page }) => {
  const responsePromise = page.waitForResponse(
    (resp) => resp.url().includes('/api/items') && resp.request().method() === 'POST'
  );

  await page.goto('/items/new');
  await page.getByLabel('Name').fill('Test');
  await page.getByRole('button', { name: 'Create' }).click();

  const response = await responsePromise;
  expect(response.status()).toBe(201);
  const body = await response.json();
  expect(body.name).toBe('Test');
});
```

### Visual Regression

```typescript
test('dashboard renders correctly', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page).toHaveScreenshot('dashboard.png', {
    maxDiffPixels: 100,
  });
});
```

### Network Mocking

```typescript
test('handles API error gracefully', async ({ page }) => {
  await page.route('**/api/items', (route) =>
    route.fulfill({ status: 500, body: 'Server Error' })
  );
  await page.goto('/items');
  await expect(page.getByText('Something went wrong')).toBeVisible();
});
```

---

## Integration with Claude Code Playwright MCP

When running interactive E2E testing during Dominion Flow execution, the Playwright MCP tools provide direct browser control:

### Available MCP Tools

| Tool | Use For |
|------|---------|
| `browser_navigate` | Go to pages |
| `browser_snapshot` | Capture accessibility tree (best for assertions) |
| `browser_click` | Click elements by ref |
| `browser_fill_form` | Fill form fields |
| `browser_type` | Type text into elements |
| `browser_take_screenshot` | Visual captures |
| `browser_console_messages` | Check for JS errors |
| `browser_network_requests` | Validate API calls |
| `browser_evaluate` | Run JS in browser |
| `browser_wait_for` | Wait for text/conditions |

### MCP Testing Pattern

```
1. browser_navigate -> page URL
2. browser_snapshot -> get element refs
3. browser_fill_form -> fill inputs
4. browser_click -> submit
5. browser_wait_for -> expected text
6. browser_snapshot -> verify result
7. browser_console_messages -> check errors
8. browser_take_screenshot -> visual evidence
```

---

## Dominion Flow Integration Points

### In /fire-3-execute (Step 8)

After all breath implementation completes:
1. Detect existing `playwright.config.ts`
2. Run `npx playwright test`
3. If no tests exist for new features, write them
4. Report results before spawning verifier

### In /fire-4-verify (E2E Category)

10-point E2E validation checklist:
- E2E-1: Playwright installed
- E2E-2: Browsers installed
- E2E-3: Critical flows covered
- E2E-4: All tests pass
- E2E-5: Cross-browser
- E2E-6: Mobile viewport
- E2E-7: API assertions
- E2E-8: Visual baselines
- E2E-9: Test isolation
- E2E-10: No console errors

### In fire-executor Agent (Step 6)

Executor runs Playwright after task implementation:
1. Check for existing E2E test files
2. Run full suite
3. Write new tests if missing for new features
4. Report results in handoff

### In fire-verifier Agent (Section 3.7)

Verifier validates E2E coverage and results:
- Run `npx playwright test` with reporter
- Check test count vs feature count
- Verify cross-browser results
- Score 0-10 points

---

## Flags

| Flag | Purpose |
|------|---------|
| `--skip-e2e` | Skip E2E testing step in `/fire-3-execute` |
| `--e2e-only` | Run only E2E tests without re-executing implementation |

---

## Best Practices

1. **Use data-testid attributes** - Don't rely on CSS classes or text that changes
2. **Test user flows, not implementation** - E2E tests should mirror real user behavior
3. **Keep tests independent** - Each test should set up its own state
4. **Use auth setup** - Share auth state via storage state, not repeated logins
5. **Retry on CI only** - Local tests should fail fast for fast feedback
6. **Trace on failure** - Enable trace recording for debugging failed CI tests
7. **Parallel by default** - Let Playwright parallelize for speed
8. **Mobile-first** - Include mobile viewport in default projects

---

*Added to Dominion Flow v3.0 - Playwright E2E Testing Integration (2026-02-10)*
