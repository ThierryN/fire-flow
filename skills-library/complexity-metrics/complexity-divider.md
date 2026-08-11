# Complexity Divider

A reusable compound engineering skill for any project. Drop this file into `.claude/skills/` to enable complexity-driven feedback loops.

## Description

Use complexity metrics as a core feedback loop mechanism to achieve 300-700% development velocity gains. Based on the principle that when code generation becomes nearly instantaneous, **feedback mechanisms become the true bottleneck**.

High complexity is a leading indicator of bugs, slow tests, and maintenance burden. By actively dividing and reducing complexity, you compress feedback loops and enable rapid generate-test-iterate cycles.

> Source: [Compound Engineering](https://www.vincirufus.com/posts/compound-engineering/)

---

## Practical Utility Assessment

### When to Use This Skill

| Scenario | Utility | Why |
|----------|---------|-----|
| **New code/features** | **8/10** | Cheap feedback, easy to act on, context is fresh |
| **Small edits (<20 lines)** | **5/10** | Quick before/after check, builds good habits |
| **Existing legacy code** | **3/10** | Warnings ignored, refactor is expensive and risky |

### Key Insight

For **new code**, the cost to refactor is near-zero. You just wrote it, context is fresh, AI can regenerate quickly.

For **existing code** (e.g., a 1900-line file with complexity 46), refactoring is expensive. The warnings exist but acting on them requires significant effort.

### Limitations

1. **Warnings not errors** - Rules set to `"warn"` so builds pass anyway. No hard enforcement.
2. **Doesn't catch logic bugs** - A 4-line bug fix has more impact than complexity metrics would catch.
3. **Existing violations accumulate** - Legacy code warnings get ignored over time.

### Does NOT Force Refactoring of Existing Code

| Scenario | Result |
|----------|--------|
| Add new function | ✅ Warns if new function is too complex |
| Add code to existing complex function | ⚠️ Warning already existed, count stays same |
| Touch a 1900-line file | ❌ No pressure to refactor it |

The before/after workflow only checks if warnings **increased**. If a file already has complexity 46, adding 5 lines doesn't change the warning count - it was already flagged.

**This skill is a ratchet** - it stops things from getting worse, but doesn't make existing code better.

### Options to Force Legacy Refactoring

1. **Change to "error"** - Blocks commits on ANY violation (including legacy)
   ```javascript
   "complexity": ["error", { max: 15 }]
   ```
   Drawback: Blocks all commits until legacy is fixed.

2. **File-specific overrides** - Strict on new code, lenient on legacy
   ```javascript
   // Strict for new features
   { files: ["src/features/**"], rules: { "complexity": ["error", 15] } }
   // Lenient for legacy
   { files: ["app/student/drills/**"], rules: { "complexity": "off" } }
   ```

3. **Boy Scout Rule** - Policy: "If you touch a file, reduce its warnings by 1"
   Drawback: Requires discipline, not automated.

### Making It More Effective

To add enforcement, either:
```javascript
// Change warn to error in eslint.config.js
"complexity": ["error", { max: 15 }],
```

Or use pre-commit hook with zero tolerance:
```bash
# .husky/pre-commit
npm run lint -- --max-warnings=0
```

### Bottom Line

Use this skill for new code. The before/after workflow catches complexity creep early when it's cheap to fix. For existing code, treat warnings as informational only.

---

## Quick Setup

### 1. Copy this skill
```bash
cp complexity-divider.md /path/to/your/project/.claude/skills/
```

### 2. Add ESLint rules
```javascript
// .eslintrc.cjs or eslint.config.js
rules: {
  'complexity': ['error', { max: 10 }],
  'max-depth': ['error', 3],
  'max-nested-callbacks': ['error', 2],
  'max-lines-per-function': ['warn', { max: 200, skipComments: true }],
  'max-params': ['warn', 4],
}
```

### 3. Add verify scripts
```json
// package.json
{
  "scripts": {
    "verify": "npm run lint && npm run test:run && tsc --noEmit",
    "verify:quick": "vitest run --changed",
    "verify:full": "npm run verify && npx playwright test"
  }
}
```

### 4. Fix CI bypasses
Remove any `|| true` from lint/test commands in CI workflows.

---

## Core Equation (Compound Engineering)

```
Productivity = (Code Velocity) × (Feedback Quality) × (Iteration Frequency)
```

When AI generates code instantly, **feedback quality and iteration frequency** become the multipliers:

```
High Complexity → Hard to Test → Slow Feedback → Reduced Velocity
        ↓ (divide)
Low Complexity → Easy to Test → Fast Feedback → Compound Gains
```

## Mindset Shift

| Traditional | Compound Engineering |
|-------------|----------------------|
| Code writer | System orchestrator |
| Plan thoroughly upfront | Generate, test, iterate rapidly |
| Manual verification | Automated guardrails |
| Mistakes are expensive | Mistakes are cheap and fixable |
| Complexity is technical debt | Complexity is a feedback loop bottleneck |

---

## The Four Pillars

### 1. Testing Frameworks
- **E2E tests** validate critical user paths holistically
- **Unit tests** validate components (easier with low complexity)
- **Parallel execution** essential for sub-minute feedback
- **Property-based testing** finds edge cases in complex logic

### 2. Guardrails as Instructions
- **Complexity thresholds** as executable requirements
- **Strong type constraints** limiting AI generation scope
- **Verification-first prompts** ("implement X, then run tests")
- **Pre-commit hooks** blocking complex code before it spreads

### 3. CI/CD Infrastructure
- **Sub-minute test runs** via parallelization
- **Instant rollback** mechanisms
- **Automated complexity checks** preventing regressions
- **Feature flags** for gradual rollout

### 4. Verification-First Prompting

**Never say:** "Implement feature X"

**Always say:** "Implement X, then run the test suite to verify it passes, and check complexity hasn't regressed"

---

## Verification-First Prompt Template

Use this structured template when requesting AI to implement features. Customize the placeholders for your project.

### Generic Template

```markdown
# Context
- Project: {PROJECT_NAME}
- Architecture: {TECH_STACK}
- Auth pattern: {AUTH_APPROACH}
- Error handling: {ERROR_STRATEGY}

# Task
Implement {feature_name} according to the attached specification.

# Constraints
- Must pass tests in {test_file}
- Must follow existing patterns in {similar_file}
- Must include TypeScript types
- Must handle edge cases: {edge_cases}
- Must not exceed complexity threshold (cyclomatic < 15)

# Verification
After implementation, run:
- npm run test {test_file}
- npm run typecheck
- npm run lint
- npm run verify
```

### Example Configurations

<details>
<summary><strong>React + Express + tRPC</strong></summary>

```markdown
# Context
- Project: {app_name}
- Architecture: React + Express + tRPC + PostgreSQL
- Auth pattern: {Clerk|Auth0|JWT} with provider abstraction
- Error handling: tRPC error codes, never expose internals

# Task
Implement {feature_name}.

# Constraints
- Must pass tests in tests/{feature}.test.ts
- Must follow existing patterns in lib/{domain}/
- Must include Zod schemas for validation
- Must handle edge cases: {edge_cases}

# Verification
After implementation, run:
- npm run test:run tests/{feature}.test.ts
- npm run verify
```
</details>

<details>
<summary><strong>Next.js + PostgreSQL</strong></summary>

```markdown
# Context
- Project: {app_name}
- Architecture: Next.js + PostgreSQL
- Auth pattern: JWT with HTTP-only cookies
- Error handling: Never expose internal errors to clients

# Task
Implement {feature_name} according to the attached specification.

# Constraints
- Must pass tests in {test_file}
- Must follow existing patterns in {similar_feature}
- Must include TypeScript types
- Must handle edge cases: {edge_cases}

# Verification
After implementation, run:
- npm run test {test_file}
- npm run typecheck
- npm run lint
```
</details>

<details>
<summary><strong>Python + FastAPI</strong></summary>

```markdown
# Context
- Project: {app_name}
- Architecture: FastAPI + SQLAlchemy + PostgreSQL
- Auth pattern: JWT Bearer tokens
- Error handling: HTTPException with status codes

# Task
Implement {feature_name}.

# Constraints
- Must pass tests in tests/test_{feature}.py
- Must follow existing patterns in app/{domain}/
- Must include Pydantic models
- Must handle edge cases: {edge_cases}

# Verification
After implementation, run:
- pytest tests/test_{feature}.py
- mypy app/
- ruff check app/
```
</details>

<details>
<summary><strong>Rails + PostgreSQL</strong></summary>

```markdown
# Context
- Project: {app_name}
- Architecture: Rails 7 + PostgreSQL + Hotwire
- Auth pattern: Devise with {strategy}
- Error handling: Rescue handlers, never expose internals

# Task
Implement {feature_name}.

# Constraints
- Must pass tests in spec/{feature}_spec.rb
- Must follow existing patterns in app/{layer}/
- Must include request specs
- Must handle edge cases: {edge_cases}

# Verification
After implementation, run:
- bundle exec rspec spec/{feature}_spec.rb
- bundle exec rubocop
- bundle exec rails test
```
</details>

---

## Complexity Metrics

### Primary Metrics

| Metric | What It Measures | Tool |
|--------|------------------|------|
| **Cyclomatic Complexity** | Independent paths through code (branches, loops) | ESLint, SonarQube, Rubocop |
| **Cognitive Complexity** | How difficult code is to understand | SonarQube, CodeClimate |
| **Halstead Complexity** | Computational complexity based on operators/operands | ESLint |
| **Lines per Function** | Function size (proxy for complexity) | ESLint, Rubocop |

### Thresholds (2026)

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| Cyclomatic (per function) | 1-8 | 9-15 | >15 |
| Cognitive (per function) | 1-10 | 11-20 | >20 |
| Lines per function | 1-200 | 201-300 | >300 |
| File total complexity | 1-40 | 41-75 | >75 |
| Complexity delta (PR) | -any | +0-15% | +>15% |

> **Note:** With AI-assisted development in 2026, longer well-structured functions are acceptable. Focus on cyclomatic complexity (branching paths) over raw line count.

---

## Feedback Loop Integration

### Stage 1: Pre-commit Hook

Block or warn before code leaves the developer's machine.

```javascript
// ESLint complexity rules (2026 thresholds)
{
  "rules": {
    "complexity": ["error", { "max": 15 }],
    "max-depth": ["error", 4],
    "max-nested-callbacks": ["error", 3],
    "max-lines-per-function": ["warn", { "max": 200, "skipComments": true }],
    "max-params": ["warn", 5]
  }
}
```

### Stage 2: CI Pipeline

Track trends and block regressions.

```yaml
- name: Verify
  run: |
    npm run lint
    npm run test:run
    npx tsc --noEmit
    npm run build
```

### Stage 3: Code Review

Auto-flag complex code for extra scrutiny.

```markdown
## Review Checklist (Auto-generated)
- [ ] Function `{name}` has complexity {n} (threshold: 15) - needs refactor
- [ ] File `{file}` total complexity increased by {n}%
- [ ] New function `{name}` needs additional test coverage (complexity: {n})
```

### Stage 4: Test Coverage Correlation

Require higher coverage for complex code.

| Complexity | Required Coverage |
|------------|-------------------|
| 1-5 | 60% minimum |
| 6-10 | 80% minimum |
| >10 | 95% + mandatory refactor |

---

## Dividing Strategies

When complexity exceeds thresholds, apply these patterns:

### 1. Extract Function
```typescript
// Before: Complexity 12
function processOrder(order: Order) {
  // validation logic (complexity +3)
  // pricing logic (complexity +4)
  // fulfillment logic (complexity +5)
}

// After: Each function complexity < 6
function validateOrder(order: Order) { /* ... */ }
function calculatePricing(order: Order) { /* ... */ }
function initiateFulfillment(order: Order) { /* ... */ }
function processOrder(order: Order) {
  validateOrder(order);
  calculatePricing(order);
  return initiateFulfillment(order);
}
```

### 2. Replace Conditionals with Polymorphism
```typescript
// Before: switch with 8 cases (complexity 8)
function getHandler(type: string) {
  switch(type) {
    case 'typeA': /* ... */
    case 'typeB': /* ... */
    // ... 6 more cases
  }
}

// After: Map lookup (complexity 1)
const handlers: Record<string, Handler> = {
  typeA: new TypeAHandler(),
  typeB: new TypeBHandler(),
  // ...
};
function getHandler(type: string) {
  return handlers[type];
}
```

### 3. Early Returns
```typescript
// Before: Nested conditionals (complexity 6)
function isValid(item: Item) {
  if (item.active) {
    if (item.quantity > 0) {
      if (item.price < 10000) {
        return true;
      }
    }
  }
  return false;
}

// After: Guard clauses (complexity 4)
function isValid(item: Item) {
  if (!item.active) return false;
  if (item.quantity <= 0) return false;
  if (item.price >= 10000) return false;
  return true;
}
```

### 4. Decompose Boolean Expressions
```typescript
// Before: Complex condition (hard to test)
if (user.role === 'admin' || (user.role === 'editor' && user.verified && !user.suspended)) {
  // ...
}

// After: Named conditions (easy to test individually)
const isAdmin = user.role === 'admin';
const isVerifiedEditor = user.role === 'editor' && user.verified && !user.suspended;
if (isAdmin || isVerifiedEditor) {
  // ...
}
```

---

## Tooling Setup by Language

### JavaScript/TypeScript (ESLint)

```javascript
// .eslintrc.cjs
module.exports = {
  rules: {
    'complexity': ['error', { max: 15 }],
    'max-depth': ['error', 4],
    'max-nested-callbacks': ['error', 3],
    'max-lines-per-function': ['warn', { max: 200, skipComments: true, skipBlankLines: true }],
    'max-params': ['warn', 5],
  }
};
```

### Python (Ruff/Flake8)

```toml
# pyproject.toml
[tool.ruff]
select = ["C901"]  # McCabe complexity

[tool.ruff.mccabe]
max-complexity = 15
```

### Ruby (Rubocop)

```yaml
# .rubocop.yml
Metrics/CyclomaticComplexity:
  Max: 15

Metrics/PerceivedComplexity:
  Max: 20

Metrics/MethodLength:
  Max: 100
```

### Go (gocyclo)

```bash
# In CI
gocyclo -over 15 ./...
```

---

## Verification Flow

### Before Implementation
```bash
# 1. Establish baseline
npm run lint  # or language-specific linter

# 2. Identify high-complexity areas that will be touched
# 3. Plan refactoring if complexity > threshold
```

### During Implementation
```bash
# After each significant change
npm run lint  # Catches complexity violations immediately
```

### Before Commit
```bash
# Full verification
npm run verify
```

### In Code Review
- Auto-flag functions with complexity > 10
- Require justification for any complexity increase > 15%
- Mandate tests for complex code paths

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Average function complexity | < 8 | Linter report |
| Functions with complexity > 15 | 0 | Linter report |
| Complexity trend (weekly) | Flat or decreasing | CI tracking |
| Test coverage on complex code | > 80% | Coverage correlation |
| Review time for low-complexity PRs | < 30 min | PR metrics |
| Cycle time (idea → production) | < 1 day (small features) | Deployment frequency |

---

## Anti-Patterns

1. **Ignoring complexity warnings**
   - Never use `// eslint-disable-next-line complexity`
   - Fix the root cause, don't suppress the symptom

2. **Accepting "temporary" complexity**
   - Technical debt compounds negatively
   - Divide now, not later

3. **Testing around complexity**
   - Don't write 20 tests for a complex function
   - Divide the function, test the parts

4. **Complexity in the name of DRY**
   - Sometimes duplication is better than the wrong abstraction
   - Prefer simple, slightly repetitive code over complex "clever" solutions

5. **Hiding complexity in utilities**
   - Moving complexity to a util file doesn't reduce it
   - The complexity still needs to be tested and maintained

6. **Bypassing guardrails**
   - Never use `|| true` in CI
   - Never use `--no-verify` on commits

---

## Quick Reference

### Before/After Workflow (Use This!)

```bash
# 1. BEFORE making changes - capture baseline
BEFORE=$(npm run lint 2>&1 | grep -c "warning")
echo "Baseline warnings: $BEFORE"

# 2. Make your changes...

# 3. AFTER changes - compare
AFTER=$(npm run lint 2>&1 | grep -c "warning")
echo "After warnings: $AFTER"

# 4. Only commit if no new warnings
if [ "$AFTER" -le "$BEFORE" ]; then
  echo "✅ No complexity regression - safe to commit"
else
  echo "❌ Added $((AFTER - BEFORE)) warnings - refactor before committing"
fi
```

**One-liner for quick check:**
```bash
npm run lint 2>&1 | grep -E "(complexity|max-depth|max-lines|max-params)" | head -20
```

### Commands
```bash
npm run lint              # Check complexity
npm run verify            # Full check
npm run verify:quick      # Fast check
npm run verify:full       # Including E2E
```

### Thresholds
- Cyclomatic: max 15
- Nesting: max 4
- Callbacks: max 3
- Lines/function: max 200
- Parameters: max 5

### When to Divide
- Any function > 15 complexity
- Any file > 75 total complexity
- Any PR increasing complexity > 15%

---

## Implementation Phases

### Phase 1: Foundation
- [ ] Add complexity rules to linter config
- [ ] Create `npm run verify` (or equivalent) script
- [ ] Remove any CI bypasses (`|| true`)
- [ ] Set up pre-commit hooks

### Phase 2: Guardrails
- [ ] Enable complexity thresholds as blocking
- [ ] Add coverage thresholds (60% minimum)
- [ ] Set up complexity tracking in CI
- [ ] Document exception process

### Phase 3: Optimization
- [ ] Track cycle time metrics
- [ ] Monitor recurring patterns in AI-generated code
- [ ] Refine thresholds based on team data
- [ ] Scale to new services/modules

---

## Common Pitfalls (From Compound Engineering)

1. **Optimizing generation speed while neglecting feedback loops**
   - Fast AI code generation is useless without fast verification

2. **Vague prompts with minimal type constraints**
   - Use strong types and complexity limits to constrain AI output

3. **Insufficient E2E coverage on critical paths**
   - Unit tests alone miss system-level complexity

4. **Manual verification bottlenecks**
   - Automate complexity checks; don't rely on code review

5. **Skipping failure mode testing**
   - Complex error handling paths need coverage too

---

## Attribution

Based on the compound engineering methodology from [vincirufus.com/posts/compound-engineering](https://www.vincirufus.com/posts/compound-engineering/), which defines compound engineering as achieving 300-700% productivity gains through feedback-driven iteration.

---

## License

This skill is open for reuse. Copy to any project's `.claude/skills/` directory.
