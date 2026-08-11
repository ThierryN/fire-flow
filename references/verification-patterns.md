# Dominion Flow Verification Patterns Reference

> **Origin:** Ported from Dominion Flow `verification-patterns.md` with Dominion Flow WARRIOR additions.

## Overview

Goal-backward verification: verify that the GOAL was achieved, not just that tasks were completed. Check observable truths, then artifacts, then wiring between them.

---

## Verification Order

### Level 1: Observable Truths (Most Important)

Can a user actually DO what the phase promised?

```bash
# Example: "Users can register and login"
# Verify the BEHAVIOR, not the code:
curl -X POST /api/auth/register -d '{"email":"test@x.com","password":"Test123!"}' | jq .token
# Expected: Returns JWT token
curl -H "Authorization: Bearer $TOKEN" /api/auth/me | jq .email
# Expected: Returns "test@x.com"
```

### Level 2: Artifact Existence

Do the required files exist with real implementation?

```bash
# Check files exist and have substance
wc -l src/api/auth.ts  # Should be >30 lines (not a stub)
grep -c "function\|const\|export" src/api/auth.ts  # Should have real code
```

**Dominion Flow addition - stub detection:**
```bash
# Flag files with TODO/FIXME/placeholder patterns
grep -rn "TODO\|FIXME\|placeholder\|not implemented" src/ --include="*.ts" --include="*.tsx"
# Any matches = verification WARNING
```

### Level 3: Key Links (Wiring)

Are the pieces actually connected?

```bash
# Check that API route is importable from frontend
grep -r "api/auth" src/app/ --include="*.tsx"  # Frontend calls backend
grep -r "prisma\|db\." src/api/auth.ts          # Backend uses database
```

---

## Verification Patterns by Feature Type

### API Endpoint

```yaml
truths:
  - "POST /api/[resource] returns 201 with valid data"
  - "GET /api/[resource] returns array of items"
  - "Unauthorized request returns 401"
artifacts:
  - path: "src/api/[resource]/route.ts"
    min_lines: 20
    must_contain: ["export async function POST", "export async function GET"]
key_links:
  - from: "src/api/[resource]/route.ts"
    to: "prisma schema"
    pattern: "prisma.[resource]"
```

### UI Component

```yaml
truths:
  - "Component renders without errors"
  - "User interaction produces expected result"
  - "Responsive at mobile/tablet/desktop"
artifacts:
  - path: "src/components/[Component].tsx"
    min_lines: 15
    must_contain: ["export", "return"]
key_links:
  - from: "src/components/[Component].tsx"
    to: "src/app/[page]/page.tsx"
    pattern: "import.*[Component]"
```

### Database Schema

```yaml
truths:
  - "Migration runs without errors"
  - "CRUD operations work on new tables"
artifacts:
  - path: "prisma/schema.prisma"
    must_contain: ["model [ModelName]"]
  - path: "prisma/migrations/"
    must_exist: true
key_links:
  - from: "prisma/schema.prisma"
    to: "src/api/"
    pattern: "prisma.[modelName]"
```

---

## WARRIOR Quality Gates (Dominion Flow Addition)

After goal-backward verification, run quality gates:

### Code Quality Gate
```bash
npm run lint          # Zero new warnings
npm run typecheck     # Zero type errors
npm run build         # Clean build
```

### Security Gate (for auth/data plans)
```bash
# Check for common vulnerabilities
grep -rn "eval(\|innerHTML\|dangerouslySetInnerHTML" src/ --include="*.ts" --include="*.tsx"
# Check for hardcoded secrets
grep -rn "password\|secret\|api_key" src/ --include="*.ts" | grep -v "test\|mock\|example"
```

### Test Gate
```bash
npm test              # All tests pass
npm test -- --coverage # Coverage meets threshold
```

### Performance Gate (for critical-path plans)
```bash
npm run build         # Check bundle size
# Lighthouse audit for web apps
```

---

## Verification Report Format

```markdown
## Verification Report: Phase XX

### Goal Achievement
- [ ] Truth 1: [PASS/FAIL] - [evidence]
- [ ] Truth 2: [PASS/FAIL] - [evidence]

### Artifact Check
- [ ] File 1: [EXISTS/MISSING] - [line count] lines
- [ ] File 2: [EXISTS/MISSING] - [line count] lines

### Wiring Check
- [ ] Link 1: [CONNECTED/BROKEN] - [pattern found/not found]

### WARRIOR Quality Gates
- [ ] Build: [PASS/FAIL]
- [ ] Lint: [PASS/FAIL] - [warning count]
- [ ] Tests: [PASS/FAIL] - [X/Y passing]
- [ ] Security: [PASS/FAIL/SKIPPED]

### Verdict: [PASS / CONDITIONAL PASS / FAIL]
```

---

## Common Failure Patterns

| Pattern | Cause | Fix |
|---------|-------|-----|
| Truth passes but artifact is stub | Hardcoded response | Check file substance |
| Artifact exists but truth fails | Code not wired | Check key_links |
| Tests pass but truth fails | Tests too narrow | Add integration test |
| Build passes but truth fails | Runtime error | Check server logs |

---

## Anti-Patterns

- **Checking task completion, not goal achievement** - "All tasks done" != "Feature works"
- **Only checking artifacts exist** - File can exist but be empty/stub
- **Skipping wiring verification** - Components exist but aren't connected
- **Trusting tests alone** - Tests can be too narrow or test wrong thing
- **Manual-only verification** - Automate everything possible, checkpoint for visual only
