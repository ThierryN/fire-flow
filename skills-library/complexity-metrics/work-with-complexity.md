# Complexity-Aware Work Protocol

## Description

Apply complexity-divider guardrails to all implementation work. This skill is automatically active during `/compound-engineering:workflows:work` and any code modification tasks.

---

## When This Applies

- Implementing new features
- Fixing bugs
- Refactoring code
- Any task that modifies source files

---

## Protocol

### Phase 1: Before Starting

```bash
# Get baseline complexity
npm run lint
```

1. Identify files that will be touched
2. Note any functions already near threshold (complexity > 10)
3. Plan refactoring if existing code exceeds limits

### Phase 2: During Implementation

**Hard Limits (Block):**
| Metric | Maximum |
|--------|---------|
| Cyclomatic complexity | 15 per function |
| Nesting depth | 4 levels |
| Nested callbacks | 3 levels |

**Soft Limits (Warn):**
| Metric | Maximum |
|--------|---------|
| Lines per function | 200 |
| Function parameters | 5 |

**Rules:**
- If a function exceeds limits, **divide it immediately** - do not continue
- Never use `// eslint-disable` for complexity rules
- Never use `|| true` to bypass lint in scripts

### Phase 3: After Each Significant Change

```bash
npm run lint
```

Fix any violations before proceeding to the next task.

### Phase 4: Before Completing

```bash
npm run verify
```

**Completion Checklist:**
- [ ] No new complexity violations
- [ ] All tests pass
- [ ] Complexity delta < 15% increase
- [ ] Any divided functions have corresponding tests

---

## Dividing Strategies

When complexity exceeds thresholds, apply these patterns:

### 1. Extract Function
```typescript
// Before: complexity 12
function processOrder(order) {
  // validation (complexity +3)
  // pricing (complexity +4)
  // fulfillment (complexity +5)
}

// After: each function < 6
function validateOrder(order) { /* ... */ }
function calculatePricing(order) { /* ... */ }
function initiateFulfillment(order) { /* ... */ }
function processOrder(order) {
  validateOrder(order);
  calculatePricing(order);
  return initiateFulfillment(order);
}
```

### 2. Early Returns (Guard Clauses)
```typescript
// Before: nested ifs (complexity 6)
function isValid(item) {
  if (item.active) {
    if (item.quantity > 0) {
      if (item.price < 10000) {
        return true;
      }
    }
  }
  return false;
}

// After: guard clauses (complexity 4)
function isValid(item) {
  if (!item.active) return false;
  if (item.quantity <= 0) return false;
  if (item.price >= 10000) return false;
  return true;
}
```

### 3. Replace Switch with Map
```typescript
// Before: switch with 8 cases (complexity 8)
function getHandler(type) {
  switch(type) {
    case 'a': return handleA();
    case 'b': return handleB();
    // ... 6 more
  }
}

// After: map lookup (complexity 1)
const handlers = {
  a: handleA,
  b: handleB,
  // ...
};
function getHandler(type) {
  return handlers[type]?.() ?? null;
}
```

### 4. Named Boolean Conditions
```typescript
// Before: complex condition
if (user.role === 'admin' || (user.role === 'editor' && user.verified && !user.suspended)) {
  // ...
}

// After: named conditions
const isAdmin = user.role === 'admin';
const isVerifiedEditor = user.role === 'editor' && user.verified && !user.suspended;
if (isAdmin || isVerifiedEditor) {
  // ...
}
```

---

## Verification Commands

```bash
npm run lint              # Check complexity violations
npm run verify            # Full verification (lint + test + typecheck)
npm run verify:quick      # Only changed files
npm run verify:full       # Includes E2E tests
```

---

## Anti-Patterns (Never Do)

1. **Suppressing warnings:** `// eslint-disable-next-line complexity`
2. **Bypassing CI:** `npm run lint || true`
3. **Skipping hooks:** `git commit --no-verify`
4. **Testing around complexity:** Writing 20 tests for one complex function
5. **Hiding complexity:** Moving it to a util file doesn't reduce it

---

## Integration with workflows:work

When using `/compound-engineering:workflows:work`:

1. Include complexity constraints in task description
2. Run `npm run lint` before starting
3. Divide functions as you go (not at the end)
4. Run `npm run verify` before marking complete

---

## Reference

Full complexity-divider documentation: `.claude/skills/complexity-divider.md`
