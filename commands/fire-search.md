---
name: power-search
description: Search the skills library for patterns, solutions, and best practices
arguments:
  - name: query
    description: Search keywords, category name, or tag to find relevant skills
    required: true
    type: string
triggers:
  - "search skills"
  - "find skill"
  - "skill for"
  - "pattern for"
---

# /fire-search - Skills Library Search

Search across 172 skills in 15 categories to find proven solutions and patterns.

## Purpose

Find relevant skills from the Dominion Flow skills library to:
- Apply proven patterns to current tasks
- Avoid reinventing solutions
- Learn from past project successes
- Speed up development with tested approaches

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `query` | Yes | Search term: keyword, category, tag, or problem description |

## Usage Examples

```bash
# Search by keyword
/fire-search "database performance"
/fire-search "authentication"
/fire-search "pagination"

# Search by category
/fire-search "category:security"
/fire-search "category:api-patterns"

# Search by tag
/fire-search "tag:prisma"
/fire-search "tag:react"

# Search by problem description
/fire-search "slow queries taking too long"
/fire-search "how to handle API errors"
```

## Process

<step number="1">
### Parse Search Query

Analyze the query to determine search type:
- **Keyword search**: Match against skill names, descriptions, and content
- **Category filter**: `category:X` searches within specific category
- **Tag filter**: `tag:X` searches by skill tags
- **Problem description**: Natural language matching against problem/solution sections

```
Query: "{query}"
Type: [keyword | category | tag | problem]
```
</step>

<step number="2">
### Search Skills Library

Search across all skill files in:
- `~/.claude/plugins/dominion-flow/skills-library/`

Categories to search (15 total):
1. `database-solutions/` - Database patterns, queries, optimization
2. `api-patterns/` - REST, GraphQL, versioning, error handling
3. `security/` - Auth, validation, encryption, OWASP
4. `performance/` - Caching, optimization, bundle size
5. `frontend/` - React, Vue, state management, CSS
6. `testing/` - Unit, integration, E2E, mocking
7. `infrastructure/` - Docker, CI/CD, deployment
8. `form-solutions/` - Validation, multi-step, file uploads
9. `ecommerce/` - Payments, cart, inventory
10. `video-media/` - Streaming, processing, uploads
11. `document-processing/` - PDF, parsing, generation
12. `integrations/` - Third-party APIs, webhooks
13. `automation/` - Scripts, scheduled tasks, workflows
14. `patterns-standards/` - Design patterns, code standards
15. `methodology/` - Process, planning, review patterns

Match criteria:
- Skill name contains query terms
- Description contains query terms
- Tags include query terms
- Problem section matches query
- Solution section matches query
</step>

<step number="3">
### Rank Results

Score matches by relevance:
- **Exact name match**: +100 points
- **Name contains term**: +50 points
- **Tag match**: +40 points
- **Description match**: +30 points
- **Problem section match**: +25 points
- **Solution section match**: +20 points
- **Content match**: +10 points

Additional scoring factors:
- **Usage frequency**: +5 points per application in current project
- **Recency**: +10 points if applied in last 7 days
- **Success rate**: +15 points if >90% success rate

Return top 10 results, sorted by score.
</step>

<step number="4">
### Display Results

Format output with skill details and recommendations.
</step>

## Output Format

```
=============================================================
                    SKILLS SEARCH RESULTS
=============================================================

Query: "{query}"
Found: X matching skills

-------------------------------------------------------------
TOP MATCHES
-------------------------------------------------------------

1. [{category}] {skill-name}
   Score: {score} | Tags: {tags}

   Problem: {brief problem description}
   Solution: {brief solution summary}

   Usage: Applied {N} times | Success: {rate}%

   View: /fire-search --detail {category}/{skill-name}

-------------------------------------------------------------

2. [{category}] {skill-name}
   ...

-------------------------------------------------------------
RECOMMENDATIONS
-------------------------------------------------------------

Based on your query "{query}", consider:

- **Start with**: {top-skill-name}
  Best match for immediate application. Addresses {reason}.

- **Also relevant**: {second-skill-name}
  Useful if you need {specific scenario}.

- **Related patterns**: {related-skills}
  Often used together with the above.

-------------------------------------------------------------
QUICK ACTIONS
-------------------------------------------------------------

[1] View skill detail:   /fire-search --detail {skill}
[2] Apply to plan:       Add to skills_to_apply in BLUEPRINT.md
[3] See more results:    /fire-search "{query}" --limit 20
[4] Search different:    /fire-search "{alternative-query}"

=============================================================
```

## Advanced Options

| Option | Description |
|--------|-------------|
| `--detail {skill}` | Show full skill document |
| `--category {name}` | Filter by category |
| `--tag {tag}` | Filter by tag |
| `--scope {scope}` | Filter by scope: `general`, `project`, or `all` (default) (v7.0) |
| `--limit {N}` | Number of results (default: 10) |
| `--json` | Output as JSON for integrations |
| `--applied` | Show only skills applied in current project |
| `--unused` | Show skills never applied (discover new patterns) |

### Scope Filter (v7.0 — SkillRL + SKILL.md)

> Hierarchical skill banks that separate general from task-specific skills improve
> retrieval precision by reducing noise from irrelevant project-specific patterns.

```
--scope options:
  general    — Search only _general/ skills (cross-project patterns)
  project    — Search only project-matching skills (detected from cwd)
  all        — Search everything (default, current behavior)

Auto-detection: If inside a project directory, default to --scope project
with _general/ always included. Explicit --scope all for full search.
```

**Directory structure:**
```
skills-library/
├── _general/          ← Cross-project skills (v7.0)
│   ├── debugging/
│   ├── testing/
│   ├── api-patterns/
│   └── patterns-standards/
├── database-solutions/
├── security/
├── frontend/
└── [project-specific categories]
```

General skills are always included regardless of scope.

## Detailed View Output

When using `--detail`:

```
=============================================================
SKILL: {category}/{skill-name}
=============================================================

Version: {version}
Last Updated: {date}
Contributors: {list}
Tags: {tags}
Difficulty: {easy|medium|hard}

-------------------------------------------------------------
PROBLEM
-------------------------------------------------------------

{Full problem description from skill file}

-------------------------------------------------------------
SOLUTION PATTERN
-------------------------------------------------------------

{Full solution pattern with explanation}

-------------------------------------------------------------
CODE EXAMPLE
-------------------------------------------------------------

// Before (problematic)
{code showing the problem}

// After (solution)
{code showing the fix}

-------------------------------------------------------------
WHEN TO USE
-------------------------------------------------------------

- {scenario 1}
- {scenario 2}
- {scenario 3}

-------------------------------------------------------------
WHEN NOT TO USE
-------------------------------------------------------------

- {anti-pattern 1}
- {anti-pattern 2}

-------------------------------------------------------------
RELATED SKILLS
-------------------------------------------------------------

- {related-skill-1} - {brief description}
- {related-skill-2} - {brief description}

-------------------------------------------------------------
REFERENCES
-------------------------------------------------------------

- {external link 1}
- {external link 2}

-------------------------------------------------------------
USAGE IN THIS PROJECT
-------------------------------------------------------------

Applied: {N} times
Phases: {list of phases where applied}
Success Rate: {rate}%
Last Used: {date}

=============================================================
```

## Integration with Planning

When you find a relevant skill, add it to your plan:

```yaml
# In BLUEPRINT.md frontmatter
skills_to_apply:
  - "database-solutions/n-plus-1"
  - "api-patterns/pagination"
```

The fire-executor will:
1. Load these skills before execution
2. Apply patterns from skills to implementation
3. Document skill application in RECORD.md
4. Update SKILLS-INDEX.md with usage

## Related Commands

- `/fire-contribute` - Add a new skill to the library
- `/fire-skills-sync` - Sync with global skills library
- `/fire-skills-history` - View skill version history
- `/fire-analytics` - See skills usage analytics
