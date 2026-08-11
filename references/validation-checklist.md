# Validation Checklist

> 70+ validation items for production-ready code (includes Playwright E2E)

---

## Quick Reference

```
Total Items: 70+
Categories: 9 (8 original + E2E Testing)
Critical Items: 26 (marked with ⚠)
```

Use this checklist before marking any significant work as complete.

---

## 1. Code Quality (6 Items)

| # | Item | Check | Notes |
|---|------|-------|-------|
| 1.1 | ⚠ **Build succeeds** | `npm run build` or equivalent passes | No TypeScript errors, no compilation failures |
| 1.2 | ⚠ **TypeScript strict mode** | No `any` types without justification | Check tsconfig.json strict settings |
| 1.3 | **ESLint passes** | `npm run lint` returns no errors | Warnings acceptable if documented |
| 1.4 | **No console.logs** | Remove debug statements | Use proper logging library instead |
| 1.5 | **Comments are meaningful** | No obvious/redundant comments | Explain "why", not "what" |
| 1.6 | **JSDoc on public APIs** | Functions/classes have documentation | Include params, returns, examples |

### Verification Commands

```bash
# Build check
npm run build

# TypeScript check
npx tsc --noEmit

# Lint check
npm run lint

# Find console.logs
grep -r "console.log" src/ --include="*.ts" --include="*.tsx"
```

---

## 2. Testing (5 Items)

| # | Item | Check | Notes |
|---|------|-------|-------|
| 2.1 | ⚠ **Unit tests exist** | New code has corresponding tests | Aim for 1:1 coverage of functions |
| 2.2 | ⚠ **Unit tests pass** | `npm test` succeeds | No skipped tests without reason |
| 2.3 | **Integration tests** | API endpoints have integration tests | Test real database interactions |
| 2.4 | **Coverage meets threshold** | Usually 80%+ for new code | Check coverage reports |
| 2.5 | **Manual testing done** | Features tested in browser/app | Document test scenarios |

### Additional Testing Considerations

- [ ] Edge cases covered (empty inputs, max values, null)
- [ ] Error paths tested (not just happy path)
- [ ] Async behavior tested correctly
- [ ] Mocks are appropriate (not hiding bugs)
- [ ] E2E tests for critical user flows

### Verification Commands

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- auth.spec.ts

# E2E tests
npm run test:e2e
```

---

## 3. Security (8 Items)

| # | Item | Check | Notes |
|---|------|-------|-------|
| 3.1 | ⚠ **No hardcoded credentials** | No API keys, passwords in code | Use environment variables |
| 3.2 | ⚠ **Input validation** | All user input validated | Use schemas (Zod, Joi) |
| 3.3 | ⚠ **SQL injection prevented** | Use parameterized queries | ORMs typically handle this |
| 3.4 | ⚠ **XSS prevented** | Output properly escaped | React handles most cases |
| 3.5 | ⚠ **HTTPS enforced** | No HTTP in production | Check redirect rules |
| 3.6 | **CORS configured** | Only allow trusted origins | Review cors middleware |
| 3.7 | **Rate limiting** | Protect against abuse | Check rate limit middleware |
| 3.8 | ⚠ **Auth on protected routes** | Middleware applied correctly | Test with/without tokens |

### Security Audit Commands

```bash
# Find potential secrets
grep -rE "(password|secret|api_key|apikey|token).*=.*['\"]" src/

# Check for SQL string concatenation
grep -rE "SELECT.*\+" src/

# Find unvalidated inputs
grep -r "req.body\." src/ --include="*.ts"

# Audit npm packages
npm audit
```

### Security Checklist Detail

- [ ] Sensitive data not logged
- [ ] Session tokens properly invalidated
- [ ] File uploads validated (type, size)
- [ ] Admin routes have role checks
- [ ] Password hashing uses bcrypt/argon2
- [ ] JWT secrets are strong and rotated

---

## 4. Performance (6 Items)

| # | Item | Check | Notes |
|---|------|-------|-------|
| 4.1 | **Page load < 3s** | Test with throttling | Use Lighthouse |
| 4.2 | ⚠ **No N+1 queries** | Check database access patterns | Use query logging |
| 4.3 | **Database indexes** | Queries use indexes | Check EXPLAIN plans |
| 4.4 | **No memory leaks** | Event listeners cleaned up | Check useEffect cleanup |
| 4.5 | **API response < 200ms** | Typical operations are fast | Set up monitoring |
| 4.6 | **Bundle size reasonable** | No unnecessary dependencies | Check with bundle analyzer |

### Performance Verification

```bash
# Check bundle size
npm run build && ls -la dist/

# Analyze bundle
npx webpack-bundle-analyzer

# Database query logging (in dev)
# Add to database config: logging: true

# Lighthouse audit
npx lighthouse http://localhost:3000 --view
```

### Performance Checklist Detail

- [ ] Images optimized (WebP, lazy loading)
- [ ] API responses paginated
- [ ] Heavy computations debounced
- [ ] Caching implemented where appropriate
- [ ] No blocking operations on main thread
- [ ] Database connection pooling configured

---

## 5. Documentation (4 Items)

| # | Item | Check | Notes |
|---|------|-------|-------|
| 5.1 | **Code comments** | Complex logic explained | Focus on "why" |
| 5.2 | **Setup instructions** | New devs can run locally | Test on fresh machine |
| 5.3 | **API documentation** | Endpoints documented | OpenAPI/Swagger preferred |
| 5.4 | **README updated** | Reflects current state | Include new features |

### Documentation Checklist Detail

- [ ] Environment variables documented
- [ ] Database schema explained
- [ ] Architecture decisions recorded
- [ ] Deployment process documented
- [ ] Troubleshooting guide exists
- [ ] Changelog updated

---

## 6. Database (5 Items)

| # | Item | Check | Notes |
|---|------|-------|-------|
| 6.1 | ⚠ **Migrations created** | Schema changes are versioned | Never modify existing migrations |
| 6.2 | ⚠ **Migrations tested** | Up and down migrations work | Test rollback |
| 6.3 | **Indexes added** | Foreign keys and search fields | Check query patterns |
| 6.4 | **Constraints defined** | NOT NULL, UNIQUE, CHECK | Enforce data integrity |
| 6.5 | **Connection pooling** | Pool size appropriate | Prevent connection exhaustion |

### Database Verification

```bash
# Run migrations
npx prisma migrate dev

# Test rollback
npx prisma migrate reset

# Check for missing indexes
# In psql: \di to list indexes

# Verify constraints
npx prisma db pull  # Compare with schema
```

### Database Checklist Detail

- [ ] Backup/restore tested
- [ ] Soft delete implemented where needed
- [ ] Timestamps (createdAt, updatedAt) present
- [ ] Foreign key cascades appropriate
- [ ] Enum types used for fixed values
- [ ] Transactions used for multi-step operations

---

## 7. API Design (6 Items)

| # | Item | Check | Notes |
|---|------|-------|-------|
| 7.1 | **Versioning** | API version in path or header | Plan for breaking changes |
| 7.2 | **Pagination** | List endpoints paginated | Use cursor or offset |
| 7.3 | ⚠ **Error handling** | Consistent error responses | Include error codes |
| 7.4 | ⚠ **Input validation** | Request bodies validated | Return 400 for bad input |
| 7.5 | **Rate limiting** | Endpoints protected | Different limits per tier |
| 7.6 | ⚠ **Authentication** | Protected routes require auth | Return 401/403 correctly |

### API Checklist Detail

- [ ] RESTful conventions followed
- [ ] HTTP status codes correct
- [ ] Response format consistent
- [ ] HATEOAS links where appropriate
- [ ] Idempotent operations are safe to retry
- [ ] Request/response examples documented

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      }
    ]
  }
}
```

---

## 8. Infrastructure (4 Items)

| # | Item | Check | Notes |
|---|------|-------|-------|
| 8.1 | **Docker works** | `docker build` succeeds | Test locally first |
| 8.2 | ⚠ **CI/CD pipeline** | All checks pass | Don't merge red builds |
| 8.3 | **Monitoring** | Errors are captured | Sentry, LogRocket, etc. |
| 8.4 | **Logging** | Structured logs in place | JSON format preferred |

### Infrastructure Verification

```bash
# Build Docker image
docker build -t app .

# Run container
docker run -p 3000:3000 app

# Check CI status
gh pr checks

# Test logging
# Verify logs appear in monitoring tool
```

### Infrastructure Checklist Detail

- [ ] Health check endpoint exists
- [ ] Graceful shutdown implemented
- [ ] Environment-specific configs
- [ ] Secrets in secret manager
- [ ] Auto-scaling configured
- [ ] Disaster recovery plan documented

---

## 9. E2E Testing - Playwright (10 Items)

| # | Item | Check | Notes |
|---|------|-------|-------|
| 9.1 | ⚠ **Playwright installed** | `npx playwright --version` succeeds | Browsers installed via `npx playwright install` |
| 9.2 | ⚠ **Config file exists** | `playwright.config.ts` or `.js` present | Proper baseURL, timeouts, retries configured |
| 9.3 | ⚠ **Critical user flows tested** | Login, signup, core CRUD operations | Happy path + error states |
| 9.4 | **All E2E tests pass** | `npx playwright test` exits 0 | No flaky tests (retry < 3) |
| 9.5 | **Cross-browser coverage** | Tests run on chromium + firefox minimum | webkit optional but recommended |
| 9.6 | **Mobile viewport tested** | Tests include mobile breakpoints | Use `playwright.config.ts` projects for viewports |
| 9.7 | **Network/API assertions** | API responses validated in E2E | Use `page.waitForResponse()` or route interception |
| 9.8 | **Visual regression baseline** | Screenshots captured for key pages | Use `expect(page).toHaveScreenshot()` |
| 9.9 | **Test isolation** | Each test independent, no shared state | Use `beforeEach` for setup, proper teardown |
| 9.10 | **CI-ready configuration** | Tests run headless in CI pipeline | Proper reporter config for CI output |

### Verification Commands

```bash
# Check Playwright installation
npx playwright --version

# Install browsers if missing
npx playwright install

# Run all E2E tests
npx playwright test

# Run specific test file
npx playwright test tests/e2e/auth.spec.ts

# Run with specific browser
npx playwright test --project=chromium

# Run with UI mode (interactive debugging)
npx playwright test --ui

# Run headed (visible browser)
npx playwright test --headed

# Generate HTML report
npx playwright show-report

# Update visual snapshots
npx playwright test --update-snapshots

# Run with trace for debugging failures
npx playwright test --trace on
```

### E2E Test Patterns

```typescript
// Standard page object pattern
import { test, expect } from '@playwright/test';

test.describe('Feature: User Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.fill('[data-testid="email"]', 'user@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="login-button"]');
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="welcome-msg"]')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.fill('[data-testid="email"]', 'bad@example.com');
    await page.fill('[data-testid="password"]', 'wrong');
    await page.click('[data-testid="login-button"]');
    await expect(page.locator('[data-testid="error-msg"]')).toBeVisible();
  });
});
```

### MCP Playwright Tools Integration

When running E2E tests interactively via Claude Code's Playwright MCP, use:
- `browser_navigate` - Navigate to pages
- `browser_snapshot` - Capture accessibility tree (preferred over screenshots for assertions)
- `browser_click` - Interact with elements
- `browser_fill_form` - Fill form fields
- `browser_take_screenshot` - Visual verification
- `browser_console_messages` - Check for JS errors
- `browser_network_requests` - Validate API calls

---

## Checklist Usage

### Pre-Commit Check (Quick)

Focus on items marked with ⚠:
- [ ] 1.1 Build succeeds
- [ ] 1.2 TypeScript strict
- [ ] 2.1 Unit tests exist
- [ ] 2.2 Unit tests pass
- [ ] 3.1 No hardcoded credentials
- [ ] 3.2 Input validation
- [ ] 3.3 SQL injection prevented
- [ ] 3.4 XSS prevented
- [ ] 3.5 HTTPS enforced
- [ ] 3.8 Auth on protected routes
- [ ] 4.2 No N+1 queries
- [ ] 6.1 Migrations created
- [ ] 6.2 Migrations tested
- [ ] 7.3 Error handling
- [ ] 7.4 Input validation
- [ ] 7.6 Authentication
- [ ] 8.2 CI/CD pipeline
- [ ] 9.1 Playwright installed
- [ ] 9.2 Config file exists
- [ ] 9.3 Critical user flows tested

### Pre-Release Check (Full)

Run through all 70+ items systematically.

### Category-Specific Check

Use when working on specific areas:
- **New API endpoint**: Sections 3, 7, 9
- **Database change**: Sections 6, 4
- **Frontend feature**: Sections 1, 2, 4, 9
- **Security fix**: Section 3 (all items)
- **Full feature (frontend + backend)**: Sections 1-4, 7, 9

---

## Automated Validation Script

```bash
#!/bin/bash
# validation-check.sh

echo "━━━ DOMINION FLOW > VALIDATION CHECK ━━━"

# Code Quality
echo "◆ Code Quality..."
npm run build && echo "  ✓ Build passes" || echo "  ✗ Build failed"
npm run lint && echo "  ✓ Lint passes" || echo "  ✗ Lint failed"

# Testing
echo "◆ Testing..."
npm test && echo "  ✓ Tests pass" || echo "  ✗ Tests failed"

# Security
echo "◆ Security..."
grep -rq "console.log" src/ && echo "  ⚠ console.logs found" || echo "  ✓ No console.logs"
npm audit --audit-level=high && echo "  ✓ No high vulnerabilities" || echo "  ⚠ Vulnerabilities found"

# E2E Testing (Playwright)
echo "◆ E2E Testing..."
npx playwright test --reporter=list 2>&1 | tail -5 && echo "  ✓ E2E tests pass" || echo "  ✗ E2E tests failed"

echo "━━━ VALIDATION COMPLETE ━━━"
```

---

*Every item exists because its absence caused a production issue somewhere.*
