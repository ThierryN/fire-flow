# Skills Usage Guide

> How agents discover, use, and contribute to the skills library

---

## Overview

The skills library is a curated collection of implementation patterns, methodologies, and domain knowledge. Agents reference skills during planning and execution to ensure consistent, high-quality implementations.

---

## Searching the Skills Library

### Using /fire-search

The primary way to find relevant skills:

```
/fire-search authentication JWT tokens
```

**Search Behavior:**
1. Searches skill titles and descriptions
2. Searches skill content for keywords
3. Returns ranked results by relevance
4. Shows skill category and file path

**Example Output:**
```
━━━ DOMINION FLOW > SKILL SEARCH ━━━

Query: "authentication JWT tokens"

Results (3 matches):

1. [HIGH] authentication/jwt-implementation.md
   JWT token generation, validation, and refresh patterns
   Category: security

2. [MED] authentication/session-management.md
   Session handling with various token strategies
   Category: security

3. [LOW] api-design/protected-routes.md
   Securing API routes with middleware
   Category: api-design

Use: Read skill with /fire-skill authentication/jwt-implementation
```

### Search Tips

| Goal | Search Query |
|------|-------------|
| Find implementation patterns | `"pattern" + domain` (e.g., "pattern repository") |
| Find security guidance | `"security" + topic` (e.g., "security file upload") |
| Find database patterns | `"database" + operation` (e.g., "database migration") |
| Find testing approaches | `"test" + type` (e.g., "test integration API") |

### Browsing by Category

Skills are organized into categories:

```
skills-library/
├── methodology/           # Development processes
├── complexity-metrics/    # Effort estimation
├── ecommerce/            # E-commerce patterns
├── integrations/         # Third-party integrations
├── video-media/          # Media processing
├── deployment-security/  # DevOps and security
├── database-solutions/   # Database patterns
├── form-solutions/       # Form handling
├── advanced-features/    # Complex implementations
├── automation/           # CI/CD, scripting
├── document-processing/  # File handling
└── patterns-standards/   # General patterns
```

---

## Referencing Skills in Plans

### BLUEPRINT.md Frontmatter

When creating execution plans, reference relevant skills:

```yaml
---
phase: 3
task: "Implement user authentication"
skills_referenced:
  - authentication/jwt-implementation.md
  - database-solutions/user-schema.md
  - testing/auth-test-patterns.md
complexity: medium
estimated_breaths: 3
---
```

### Skill Citation in Plan Body

Reference skills when describing implementation approach:

```markdown
## Implementation Approach

Following the JWT implementation pattern from `authentication/jwt-implementation.md`:

1. **Token Generation** (per skill section 2.1)
   - Use RS256 algorithm for production
   - Include standard claims (iss, sub, exp, iat)
   - Add custom claims for user roles

2. **Token Validation** (per skill section 2.2)
   - Validate signature before claims
   - Check expiration with clock skew tolerance
   - Verify issuer matches expected value
```

### Inline References

During implementation details:

```markdown
### Database Schema

Per `database-solutions/user-schema.md`:
- Use UUID for primary keys
- Include audit timestamps
- Soft delete with deletedAt column

### Password Handling

Per `security/password-hashing.md`:
- Use bcrypt with cost factor 12
- Never store plaintext
- Implement password strength validation
```

---

## Citing Skills in RECORD.md

### Skills Used Section

Always document which skills informed the implementation:

```markdown
## Skills Referenced

| Skill | Usage | Sections Used |
|-------|-------|---------------|
| `authentication/jwt-implementation.md` | Token generation and validation | 2.1, 2.2, 3.1 |
| `database-solutions/user-schema.md` | User table design | Full |
| `testing/auth-test-patterns.md` | Test structure | 1.1, 2.3 |

### Deviations from Skills

1. **JWT Algorithm**: Used HS256 instead of RS256
   - Reason: Simpler key management for MVP
   - Trade-off: Less suitable for distributed systems
   - Future: Migrate to RS256 when scaling
```

### Knowledge Gaps Identified

Document when skills were missing:

```markdown
## Skills Gaps Identified

The following patterns would benefit from skills documentation:

1. **Rate Limiting with Redis**
   - Needed: Distributed rate limiting patterns
   - Currently: Implemented from scratch
   - Recommendation: Create `security/rate-limiting-redis.md`

2. **GraphQL Subscriptions**
   - Needed: WebSocket management patterns
   - Currently: Following Apollo docs only
   - Recommendation: Create `api-design/graphql-subscriptions.md`
```

---

## Contributing New Skills

### Using /fire-contribute

When you've implemented a pattern worth documenting:

```
/fire-contribute "Redis Rate Limiting Pattern"
```

**Contribution Flow:**
1. Describe the pattern you implemented
2. Answer classification questions
3. Review generated skill draft
4. Submit for library addition

### Skill Document Structure

```markdown
# [Skill Title]

> One-line description of what this skill covers

---

## Overview

Brief explanation of when to use this pattern and why.

## Prerequisites

- Required knowledge
- Dependencies
- Environment setup

## Implementation

### Step 1: [First Step]

Detailed instructions with code examples.

```typescript
// Example code
```

### Step 2: [Second Step]

Continue with clear, actionable steps.

## Variations

### Variation A: [Name]

When to use this variation and how it differs.

### Variation B: [Name]

Alternative approach for different requirements.

## Testing

How to verify the implementation works.

## Common Pitfalls

1. **Pitfall Name**: What goes wrong and how to avoid it
2. **Another Pitfall**: Description and prevention

## References

- External documentation links
- Related skills in the library

---

*Last updated: [Date] | Contributor: [Name/Agent]*
```

### Contribution Guidelines

1. **Be Specific**: Generic advice isn't helpful
2. **Include Code**: Show, don't just tell
3. **Test Your Pattern**: Only document what works
4. **Note Limitations**: Be honest about trade-offs
5. **Update Existing**: Improve skills rather than duplicating

---

## Syncing with Global Library

### Check for Updates

```
/fire-sync check
```

**Output:**
```
━━━ DOMINION FLOW > SKILL SYNC CHECK ━━━

Local Library: v2.3.1
Global Library: v2.4.0

Updates Available:
  + NEW: api-design/graphql-subscriptions.md
  ~ UPD: authentication/jwt-implementation.md (security patch)
  ~ UPD: database-solutions/migration-patterns.md (new examples)

Run /fire-sync pull to update
```

### Pull Updates

```
/fire-sync pull
```

**Behavior:**
1. Downloads new/updated skills
2. Preserves local modifications
3. Shows changelog for updates
4. Reports conflicts if any

### Push Contributions

```
/fire-sync push authentication/custom-sso.md
```

**Behavior:**
1. Validates skill format
2. Runs quality checks
3. Submits to global library
4. Tracks contribution credit

---

## Skill Discovery During Execution

### Automatic Suggestions

During planning, Dominion Flow may suggest relevant skills:

```
━━━ DOMINION FLOW > PLANNING ━━━

Analyzing task: "Add payment processing"

Suggested Skills:
  ├─ ecommerce/payment-integration.md
  │   └─ Stripe, PayPal integration patterns
  ├─ security/pci-compliance.md
  │   └─ Payment data handling requirements
  └─ testing/payment-mocking.md
      └─ How to test without real transactions

Review skills before proceeding? (y/n)
```

### Skill Quick Reference

During execution, quickly check a skill:

```
/fire-skill-quick authentication/jwt-implementation 2.1
```

**Output:**
```
━━━ JWT Implementation - Section 2.1 ━━━

Token Generation:

```typescript
import jwt from 'jsonwebtoken';

const generateToken = (user: User): string => {
  return jwt.sign(
    {
      sub: user.id,
      email: user.email,
      roles: user.roles,
    },
    process.env.JWT_SECRET,
    {
      algorithm: 'RS256',
      expiresIn: '15m',
      issuer: 'your-app-name',
    }
  );
};
```

Key Points:
- Use short expiration (15m) with refresh tokens
- Include minimal claims (reduce token size)
- Always set issuer for validation
```

---

## Best Practices

### When to Search for Skills

1. **Before starting any new feature** - Check if patterns exist
2. **When encountering unfamiliar territory** - Learn from documented experience
3. **Before implementing security features** - Always use vetted patterns
4. **When estimating complexity** - Skills help gauge effort

### When to Create New Skills

1. **After implementing something novel** - Share the knowledge
2. **When you spent significant time researching** - Save others the effort
3. **When you found a better way** - Improve on existing patterns
4. **When you hit undocumented pitfalls** - Prevent others from same mistakes

### Skill Maintenance

1. **Update when patterns evolve** - Keep skills current
2. **Add examples from real implementations** - Concrete beats abstract
3. **Note deprecated approaches** - Warn about outdated patterns
4. **Cross-reference related skills** - Build a connected knowledge base

---

## Quick Command Reference

| Command | Purpose |
|---------|---------|
| `/fire-search <query>` | Find relevant skills |
| `/fire-skill <path>` | Read full skill document |
| `/fire-skill-quick <path> <section>` | Read specific section |
| `/fire-contribute <title>` | Start new skill contribution |
| `/fire-sync check` | Check for library updates |
| `/fire-sync pull` | Download library updates |
| `/fire-sync push <path>` | Submit skill contribution |

---

*The skills library grows with every implementation. Contribute what you learn.*
