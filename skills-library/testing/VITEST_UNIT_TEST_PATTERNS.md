---
name: vitest-unit-test-patterns
category: testing
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [testing, vitest, unit-tests, mocking, coverage]
difficulty: easy
---

# Vitest Unit Test Patterns

## Problem

Unit tests are written inconsistently — some test implementation details instead of behavior, mocks leak between tests, and coverage reports show quantity but not quality.

## Solution Pattern

Structure unit tests with the AAA pattern (Arrange-Act-Assert), mock at boundaries, and test behavior not implementation.

## Code Example

```typescript
// Before (testing implementation)
test('calls setUser', () => {
  const spy = vi.spyOn(store, 'setUser');
  login('admin', 'pass');
  expect(spy).toHaveBeenCalledWith({ name: 'admin' });
});

// After (testing behavior)
test('successful login stores user and redirects', async () => {
  // Arrange
  const mockApi = vi.fn().mockResolvedValue({ user: { name: 'admin' } });

  // Act
  const result = await login('admin', 'pass', { api: mockApi });

  // Assert
  expect(result.user.name).toBe('admin');
  expect(result.redirectTo).toBe('/dashboard');
});
```

## Key Patterns

### 1. Mock at Boundaries
Mock: APIs, databases, file system, external services.
Don't mock: internal functions, utilities, pure logic.

### 2. Test Naming Convention
```
test('{action} should {expected result} when {condition}')
```

### 3. Isolation
```typescript
beforeEach(() => { vi.restoreAllMocks(); });
afterEach(() => { vi.clearAllTimers(); });
```

### 4. Coverage That Matters
- Branch coverage > line coverage
- Test error paths, not just happy paths
- Edge cases: empty arrays, null, undefined, max values

## When to Use
- All new functions and modules
- After fixing a bug (write the test that would have caught it)
- During refactoring (tests prove behavior is preserved)

## When NOT to Use
- Simple getters/setters with no logic
- Configuration files
- Generated code
