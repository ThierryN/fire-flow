# E2E Test: /fire-contribute - Skills Contribution

## Test Name
`skills-contribute`

## Description
Validates that `/fire-contribute` allows users to add new skills to the skills library with proper formatting, categorization, and metadata. Tests the skill creation workflow and validation.

---

## Prerequisites
- Fire Flow plugin installed
- Skills library directory exists at `~/.claude/plugins/fire-flow/skills-library/`
- Write permissions to skills library

---

## Setup Steps

```bash
# 1. Verify skills library exists
SKILLS_LIB="$HOME/.claude/plugins/fire-flow/skills-library"
[ -d "$SKILLS_LIB" ] && echo "Skills library exists" || mkdir -p "$SKILLS_LIB"

# 2. Note existing skills count
BEFORE_COUNT=$(find "$SKILLS_LIB" -name "*.md" -type f | wc -l)
echo "Skills before: $BEFORE_COUNT"

# 3. Ensure target category exists
mkdir -p "$SKILLS_LIB/automation"
```

---

## Execute Steps

### Test Case 1: Interactive Skill Creation
```bash
# In Claude Code session:
/fire-contribute

# Follow prompts:
#   - Skill name: "GitHub Actions CI/CD"
#   - Category: "automation"
#   - Description: "Setting up GitHub Actions for continuous integration and deployment"
#   - Keywords: "github, actions, ci, cd, automation, workflow"
#   - When to use: "When setting up automated testing and deployment pipelines"
```

### Test Case 2: Quick Skill Creation (with arguments)
```bash
# In Claude Code session:
/fire-contribute --name "Docker Multi-Stage Builds" --category "deployment-security"

# Should create skill and prompt for remaining details
```

### Test Case 3: Skill from Current Context
```bash
# After completing a task that could become a skill:
/fire-contribute --from-context

# Should analyze recent work and offer to create skill
```

---

## Verify Steps

### Skill File Created
```bash
# Check skill file exists
SKILL_FILE="$SKILLS_LIB/automation/github-actions-cicd.md"
[ -f "$SKILL_FILE" ] && echo "PASS: Skill file created" || echo "FAIL: Skill file not created"
```

### Skill Format Correct
```bash
# Check required sections exist
grep -q "^# " "$SKILL_FILE" && echo "PASS: Has title" || echo "FAIL: Missing title"
grep -q "## Overview" "$SKILL_FILE" && echo "PASS: Has Overview" || echo "FAIL: Missing Overview"
grep -q "## Keywords" "$SKILL_FILE" && echo "PASS: Has Keywords" || echo "FAIL: Missing Keywords"
grep -q "## When to Use" "$SKILL_FILE" && echo "PASS: Has When to Use" || echo "FAIL: Missing When to Use"
grep -q "## Steps" "$SKILL_FILE" && echo "PASS: Has Steps" || echo "FAIL: Missing Steps"
```

### Filename Convention
```bash
# Check filename follows convention (lowercase, hyphenated)
FILENAME=$(basename "$SKILL_FILE")
if [[ "$FILENAME" =~ ^[a-z0-9-]+\.md$ ]]; then
    echo "PASS: Filename follows convention"
else
    echo "FAIL: Filename convention violated: $FILENAME"
fi
```

### Category Placement
```bash
# Check skill is in correct category directory
SKILL_DIR=$(dirname "$SKILL_FILE")
[ "$SKILL_DIR" == "$SKILLS_LIB/automation" ] && echo "PASS: Correct category" || echo "FAIL: Wrong category"
```

### Keywords Searchable
```bash
# Verify keywords are formatted for search
grep -q "github" "$SKILL_FILE" && echo "PASS: Keywords present" || echo "FAIL: Keywords missing"
grep -q "ci" "$SKILL_FILE" && echo "PASS: Multiple keywords" || echo "FAIL: Missing keywords"
```

### Skills Count Increased
```bash
# Verify skill count increased
AFTER_COUNT=$(find "$SKILLS_LIB" -name "*.md" -type f | wc -l)
[ "$AFTER_COUNT" -gt "$BEFORE_COUNT" ] && echo "PASS: Skills count increased" || echo "FAIL: Count unchanged"
```

---

## Cleanup Steps

```bash
# Remove test skill
rm -f "$SKILLS_LIB/automation/github-actions-cicd.md"
rm -f "$SKILLS_LIB/deployment-security/docker-multi-stage-builds.md"

# Verify cleanup
[ ! -f "$SKILLS_LIB/automation/github-actions-cicd.md" ] && echo "Cleanup complete"
```

---

## Pass/Fail Criteria

| Criterion | Required | Description |
|-----------|----------|-------------|
| Skill file created | YES | .md file in skills library |
| Has title | YES | H1 header with skill name |
| Has Overview section | YES | Brief description of skill |
| Has Keywords section | YES | Searchable keywords |
| Has When to Use section | YES | Usage context |
| Has Steps section | YES | Implementation steps |
| Correct category | YES | File in appropriate subdirectory |
| Filename convention | YES | Lowercase, hyphenated .md |
| Searchable | YES | Can be found via /fire-search |

## Expected Result
**PASS** if all required criteria are met.

---

## Skill Template Reference

```markdown
# Skill Name

## Overview
Brief description of what this skill covers and its purpose.

## Keywords
keyword1, keyword2, keyword3, keyword4

## When to Use
- Scenario 1 when this skill applies
- Scenario 2 when this skill applies
- Scenario 3 when this skill applies

## Prerequisites
- Prerequisite 1
- Prerequisite 2

## Steps

### Step 1: First Step Name
Description and instructions.

```code
code example
```

### Step 2: Second Step Name
Description and instructions.

## Common Issues
- Issue 1 and solution
- Issue 2 and solution

## Related Skills
- related-skill-1.md
- related-skill-2.md

## References
- External documentation links
```

---

## Test Variations

### Variation A: New Category Creation
- Contribute skill to non-existent category
- Should create category directory
- Should add skill to new category

### Variation B: Duplicate Detection
- Try to contribute skill with same name
- Should warn about duplicate
- Offer to update or rename

### Variation C: Minimal Skill
- Only provide name and steps
- Should create with defaults
- Should prompt for missing sections

### Variation D: Code-Heavy Skill
- Skill with multiple code examples
- Code blocks should preserve formatting
- Syntax highlighting hints included

---

## Skill Categories Reference

| Category | Purpose |
|----------|---------|
| automation | CI/CD, scripts, workflows |
| database-solutions | Database setup, queries, migrations |
| deployment-security | Deployment, containers, security |
| document-processing | PDFs, docs, data extraction |
| ecommerce | Shopping, payments, inventory |
| form-solutions | Forms, validation, submissions |
| integrations | Third-party services, APIs |
| patterns-standards | Design patterns, best practices |
| video-media | Video processing, media handling |

---

## Known Issues
- Category validation may be loose (allows arbitrary categories)
- Long skill content may need scrolling

## Related Tests
- `skills-search.test.md` - Finding contributed skills
- `plan-phase.test.md` - Using contributed skills in planning
- `skills-sync.test.md` - Syncing skills with global library
