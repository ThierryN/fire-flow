# E2E Test: /fire-search - Skills Search

## Test Name
`skills-search`

## Description
Validates that `/fire-search` finds relevant skills from the skills library based on keyword and semantic matching, displays results with descriptions, and provides paths for skill loading.

---

## Prerequisites
- Dominion Flow plugin installed
- Skills library populated at `~/.claude/plugins/dominion-flow/skills-library/`
- Multiple skill files with varied content

---

## Setup Steps

```bash
# 1. Ensure skills library exists and has content
SKILLS_LIB="$HOME/.claude/plugins/dominion-flow/skills-library"

# 2. Verify skills library structure
ls "$SKILLS_LIB"

# 3. Create test skills if needed
mkdir -p "$SKILLS_LIB/database-solutions"
mkdir -p "$SKILLS_LIB/patterns-standards"
mkdir -p "$SKILLS_LIB/integrations"

# 4. Create sample skills for testing
cat > "$SKILLS_LIB/database-solutions/prisma-setup.md" << 'EOF'
# Prisma ORM Setup and Configuration

## Overview
Complete guide for setting up Prisma ORM with PostgreSQL in Node.js applications.

## Keywords
prisma, orm, database, postgresql, schema, migration, typescript

## When to Use
- Setting up database layer in new projects
- Migrating from raw SQL to ORM
- Need type-safe database queries

## Steps
1. Install dependencies
2. Initialize Prisma
3. Configure schema
4. Generate client
5. Run migrations

## Code Examples
```typescript
// prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}
```
EOF

cat > "$SKILLS_LIB/database-solutions/mongodb-aggregation.md" << 'EOF'
# MongoDB Aggregation Pipelines

## Overview
Advanced aggregation techniques for MongoDB data processing.

## Keywords
mongodb, aggregation, pipeline, nosql, data processing

## When to Use
- Complex data queries
- Report generation
- Data transformation

## Steps
1. Design pipeline stages
2. Implement $match, $group, $project
3. Optimize with indexes
EOF

cat > "$SKILLS_LIB/integrations/stripe-payments.md" << 'EOF'
# Stripe Payment Integration

## Overview
Integrating Stripe for payment processing in web applications.

## Keywords
stripe, payments, checkout, webhooks, subscriptions

## When to Use
- Adding payment processing
- Subscription billing
- E-commerce checkout

## Steps
1. Configure Stripe SDK
2. Create payment intents
3. Set up webhooks
4. Handle confirmations
EOF
```

---

## Execute Steps

### Test Case 1: Keyword Search
```bash
# In Claude Code session:
/fire-search database

# Expected: Should find prisma-setup.md and mongodb-aggregation.md
```

### Test Case 2: Specific Technology Search
```bash
# In Claude Code session:
/fire-search prisma

# Expected: Should find prisma-setup.md as top result
```

### Test Case 3: Use Case Search
```bash
# In Claude Code session:
/fire-search payments

# Expected: Should find stripe-payments.md
```

### Test Case 4: No Results Search
```bash
# In Claude Code session:
/fire-search kubernetes

# Expected: Should report no matching skills found
```

---

## Verify Steps

### Search Returns Results
```bash
# Verify search results are displayed
# Check Claude Code output for:
#   - Skill names listed
#   - Descriptions/overviews shown
#   - File paths provided
echo "Check output contains skill listings"
```

### Result Relevance
```bash
# For "database" search:
#   - prisma-setup.md should appear
#   - mongodb-aggregation.md should appear
#   - stripe-payments.md should NOT appear (or rank low)
echo "Verify relevant skills ranked higher"
```

### Result Format
```bash
# Each result should include:
#   - Skill name/title
#   - Brief description
#   - Full path to skill file
#   - Match reason (keyword/section)

# Example expected format:
# 1. Prisma ORM Setup and Configuration
#    Path: ~/.claude/plugins/dominion-flow/skills-library/database-solutions/prisma-setup.md
#    Match: keyword "database" in Keywords section
echo "Verify result format includes path and match reason"
```

### Skills Accessible
```bash
# Verify skill files are readable
for SKILL in "database-solutions/prisma-setup.md" "integrations/stripe-payments.md"; do
    [ -f "$SKILLS_LIB/$SKILL" ] && echo "PASS: $SKILL accessible" || echo "FAIL: $SKILL not found"
done
```

### Search Performance
```bash
# Search should complete quickly (< 2 seconds for moderate library)
# This is a manual observation
echo "Observe search completion time"
```

---

## Cleanup Steps

```bash
# No cleanup needed unless test skills should be removed
# Optionally remove test skills:
# rm "$SKILLS_LIB/database-solutions/prisma-setup.md"
# rm "$SKILLS_LIB/database-solutions/mongodb-aggregation.md"
# rm "$SKILLS_LIB/integrations/stripe-payments.md"
```

---

## Pass/Fail Criteria

| Criterion | Required | Description |
|-----------|----------|-------------|
| Search executes | YES | Command runs without error |
| Relevant results returned | YES | Matching skills found |
| Results include path | YES | Full path to skill file |
| Results include description | YES | Skill overview/summary shown |
| Results ranked by relevance | NO | Most relevant first (enhancement) |
| No results handled | YES | Graceful message when no matches |
| Multiple results | YES | Can return multiple matching skills |
| Search < 5 seconds | NO | Performance target |

## Expected Result
**PASS** if all required criteria are met.

---

## Test Variations

### Variation A: Category Search
- Search: "database"
- Should list all skills in database-solutions/

### Variation B: Multi-word Search
- Search: "prisma postgresql"
- Should find prisma-setup.md

### Variation C: Partial Match
- Search: "pris"
- Should find prisma-setup.md (if partial matching enabled)

### Variation D: Case Insensitive
- Search: "STRIPE"
- Should find stripe-payments.md

---

## Search Algorithm Notes

The search should check:
1. Skill title/filename
2. Keywords section (if present)
3. When to Use section
4. Overview/description
5. Full content (lower priority)

Ranking factors:
- Exact keyword match > partial match
- Title match > content match
- Multiple matches in same skill > single match

---

## Known Issues
- Semantic search may require embeddings (future enhancement)
- Large skill libraries may need indexing

## Related Tests
- `skills-contribute.test.md` - Adding new skills
- `plan-phase.test.md` - Uses skill search during planning
