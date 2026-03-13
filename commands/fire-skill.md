---
name: fire-skill
description: Unified skill management CLI — create, import, test, list, stats, and export skills
arguments:
  - name: action
    description: "Action: create, import, test, list, stats, export, browse, upgrade"
    required: true
    type: string
  - name: target
    description: "Skill name, URL, or search query depending on action"
    required: false
    type: string
triggers:
  - "skill create"
  - "skill import"
  - "skill test"
  - "skill list"
  - "skill stats"
  - "manage skills"
  - "fire skill"
---

# /fire-skill - Unified Skill Management CLI

One command for all skill operations. Inspired by `npx skills`, `oh-my-zsh` plugins,
and the Agent Skills ecosystem — but designed for Dominion Flow's security-first approach.

## Subcommands

```
/fire-skill create [name]        Create a new skill (quick or wizard mode)
/fire-skill import [source]      Import skill from URL, file, or marketplace
/fire-skill test [name]          Validate and dry-run a skill
/fire-skill list [filter]        List skills with filtering and stats
/fire-skill stats [name]         Usage analytics for one or all skills
/fire-skill export [name]        Export skill for sharing
/fire-skill browse               Interactive skill browser with preview
/fire-skill upgrade [name]       Upgrade skill to latest template format
```

---

## /fire-skill create

### Quick Mode (one-liner)

```bash
# Minimal — just a name and type, fills defaults
/fire-skill create "retry-backoff" --type api-integration --category api-patterns

# From current session — auto-extracts the pattern you just solved
/fire-skill create --from session

# From a RECORD.md summary
/fire-skill create --from summary
```

### Interactive Mode (default when no --type given)

```bash
/fire-skill create "retry-backoff"
```

<step number="1">
### Select Skill Type (Template)

```
=============================================================
              SKILL CREATION — SELECT TYPE
=============================================================

What kind of skill is this?

  1. debug-pattern       Diagnose & fix a specific bug
                         Has: symptoms, detection, elimination checklist,
                         before/after, verification steps

  2. api-integration     Connect to an external API or service
                         Has: env vars, client setup, retry/resilience,
                         webhook handling, test mocks

  3. ui-component        Reusable UI pattern or component
                         Has: wireframe, props API, responsive behavior,
                         accessibility checklist, state management

  4. architecture        Structural/design pattern
                         Has: Mermaid diagram, principles, trade-offs,
                         migration path, decision criteria

  5. devops-recipe       Infrastructure, CI/CD, deployment
                         Has: prerequisites, step-by-step, verification,
                         rollback plan, monitoring metrics

  6. general             Standard problem/solution skill
                         Has: problem, solution, code example, when to
                         use/not use (current default format)

  Select type (1-6): > _
=============================================================
```

Based on selection, load the corresponding template from:
`~/.claude/plugins/dominion-flow/templates/skill-{type}.md`

If type 6 (general), use the standard template from `/fire-add-new-skill`.
</step>

<step number="2">
### Collect Metadata

For Quick Mode, auto-fill from arguments. For Interactive Mode, prompt:

```
-------------------------------------------------------------
METADATA
-------------------------------------------------------------

Category: [auto-suggested from type, or select from list]
Scope:    [General | Project] (default: General)
Tags:     [auto-suggested from type + category, editable]
Difficulty: [easy | medium | hard]

-------------------------------------------------------------
```

**Auto-suggestion logic:**
- `api-integration` type → suggests `api-patterns` or `integrations` category
- `debug-pattern` type → suggests `quality-safety` or matching domain category
- `ui-component` type → suggests `frontend` category
- `architecture` type → suggests `patterns-standards` or `methodology`
- `devops-recipe` type → suggests `infrastructure` or `automation`
</step>

<step number="3">
### Fill Template Sections

Present each template section one at a time. For each section:

1. Show the section header and placeholder description
2. Collect user input or auto-extract from session context
3. Allow skipping optional sections with `[skip]`
4. Show running preview of completed sections

**Smart defaults from session:**
If `--from session` is used, scan the current conversation for:
- Error messages and stack traces → populate Symptoms
- Code that was changed → populate Before/After
- Test commands run → populate Verification
- Comments about why → populate "Why This Works"
</step>

<step number="4">
### Review, Security Scan, Save

Run the same review panel, security scan, and credential filter gates
from `/fire-add-new-skill` (Steps 5.5, 4.5, 4.6).

Then save and update the index.
</step>

### Options for create

| Option | Description |
|--------|-------------|
| `--type {type}` | Skip type selection: `debug-pattern`, `api-integration`, `ui-component`, `architecture`, `devops-recipe`, `general` |
| `--category {cat}` | Pre-fill category |
| `--from session` | Auto-extract from current conversation |
| `--from summary` | Auto-extract from most recent RECORD.md |
| `--quick` | Minimal prompts, fill defaults, skip optional sections |
| `--dry-run` | Preview the skill document without saving |

---

## /fire-skill import

Import skills from external sources with mandatory security scanning.

```bash
# Import from a GitHub repo (skills.sh format)
/fire-skill import github:owner/repo/skill-name

# Import from a URL (raw markdown)
/fire-skill import https://example.com/skills/retry-pattern.md

# Import from a local file
/fire-skill import ./my-pattern.md

# Import from skills.sh marketplace
/fire-skill import skills:vercel-labs/skills/find-skills

# Import and assign to category
/fire-skill import github:owner/repo/skill --category api-patterns
```

<step number="1">
### Fetch Source

Download or read the skill content from the specified source.

**Supported sources:**
| Prefix | Source | Example |
|--------|--------|---------|
| `github:` | GitHub repo path | `github:wshobson/commands/code-review` |
| `skills:` | skills.sh registry | `skills:vercel-labs/skills/find-skills` |
| `https://` | Raw URL | `https://raw.githubusercontent.com/...` |
| `./` or path | Local file | `./patterns/retry.md` |

For GitHub sources, fetch using:
```bash
curl -sL "https://raw.githubusercontent.com/{owner}/{repo}/main/{path}/SKILL.md"
```

For skills.sh sources, use the skills.sh API format.
</step>

<step number="2">
### Security Scan (MANDATORY — Deep Mode)

**All imported skills get deep security scanning.**

This is non-negotiable. The Snyk study found 13.4% of marketplace skills
contained critical security issues. External skills run through ALL 6 layers
of the security scanner in `--deep` mode:

1. NFKC normalization
2. Invisible Unicode characters
3. Prompt injection signatures
4. Credential harvesting patterns
5. PII collection patterns
6. Tool poisoning (exfiltration URLs, cross-tool manipulation)

```
-------------------------------------------------------------
IMPORT SECURITY SCAN (Deep Mode)
-------------------------------------------------------------

Source: {source_url}
Size:   {file_size} bytes

Scanning...
  Layer 1: Invisible characters ... {CLEAN | FOUND}
  Layer 2: Prompt injection     ... {CLEAN | FOUND}
  Layer 3: Credential harvesting ... {CLEAN | FOUND}
  Layer 4: PII collection       ... {CLEAN | FOUND}
  Layer 5: Tool poisoning       ... {CLEAN | FOUND}
  Layer 6: Exfiltration URLs    ... {CLEAN | FOUND}

Verdict: {CLEAN | SUSPICIOUS | BLOCKED}
-------------------------------------------------------------
```

**If BLOCKED:** Refuse import. Show findings. No override.
**If SUSPICIOUS:** Show findings. Require explicit user confirmation.
**If CLEAN:** Proceed.
</step>

<step number="3">
### Format Normalization

Convert imported skill to Dominion Flow format if needed:

- Add missing frontmatter fields (version, contributed, tags, difficulty)
- Normalize section headers to match our template structure
- Convert SKILL.md format (skills.sh) to our `.md` format
- Preserve original source attribution in References section

```
-------------------------------------------------------------
FORMAT NORMALIZATION
-------------------------------------------------------------

Original format: {SKILL.md | .cursorrules | plain markdown}
Converted to:    Dominion Flow skill format

Added fields:
  + version: 1.0.0
  + contributed: {today}
  + contributor: imported:{source}
  + difficulty: medium (default — edit if needed)
  + tags: [extracted, from, content]

-------------------------------------------------------------
```
</step>

<step number="4">
### Save with Quarantine Option

For imported skills, offer quarantine:

```
-------------------------------------------------------------
SAVE OPTIONS
-------------------------------------------------------------

  1. Save directly     → skills-library/{category}/{name}.md
  2. Save to quarantine → skills-library/_quarantine/{name}.md
                          (review before promoting to library)
  3. Preview only      → Display without saving
  4. Cancel            → Discard

Select (1-4): > _
-------------------------------------------------------------
```

Quarantine saves to `_quarantine/` with a `quarantine_reason: "imported"` field.
Promote later with `/fire-skill upgrade {name} --promote`.
</step>

---

## /fire-skill test

Validate a skill's format, completeness, and internal consistency.

```bash
# Test a specific skill
/fire-skill test database-solutions/connection-pool-timeout

# Test all skills in a category
/fire-skill test --category api-patterns

# Test all skills
/fire-skill test --all

# Test with strict mode (all optional sections required)
/fire-skill test --strict database-solutions/connection-pool-timeout
```

<step number="1">
### Validation Checks

Run the following checks on each skill file:

```
=============================================================
            SKILL VALIDATION: {skill-name}
=============================================================

Format Checks:
  [PASS] YAML frontmatter present
  [PASS] Required fields: name, category, version
  [PASS] Tags field is an array
  [WARN] Missing field: difficulty (default: medium)
  [PASS] Version follows semver

Content Checks:
  [PASS] # Title heading present
  [PASS] ## Problem section present
  [PASS] ## Solution Pattern section present
  [WARN] ## Code Example section empty
  [PASS] ## When to Use section present
  [FAIL] ## When NOT to Use section missing

Template Conformance:
  [INFO] Skill type: debug-pattern
  [WARN] Missing template sections: Detection, Elimination Checklist
  [PASS] All required template sections present

Cross-Reference Checks:
  [PASS] Category directory exists
  [WARN] Related skill "retry-backoff" not found in library
  [PASS] No duplicate skill name detected

Security Quick-Scan:
  [PASS] No credential patterns detected
  [PASS] No suspicious URLs detected
  [PASS] No prompt injection signatures

-------------------------------------------------------------
RESULT: 5 PASS | 3 WARN | 1 FAIL
-------------------------------------------------------------

Recommendations:
  1. Add "## When NOT to Use" section (required)
  2. Consider adding code examples
  3. Verify related skill reference "retry-backoff"

=============================================================
```
</step>

### Validation Levels

| Level | What's Checked |
|-------|---------------|
| **Basic** (default) | Frontmatter, required sections, format |
| **Strict** (`--strict`) | All template sections, code examples, references |
| **Security** (`--security`) | Full 6-layer security scan |
| **All** (`--all --strict`) | Everything on every skill |

---

## /fire-skill list

Enhanced skill listing with filtering, sorting, and inline stats.

```bash
# List all skills (compact view)
/fire-skill list

# Filter by category
/fire-skill list --category frontend

# Filter by type
/fire-skill list --type debug-pattern

# Filter by tag
/fire-skill list --tag react

# Filter by difficulty
/fire-skill list --difficulty hard

# Sort by usage
/fire-skill list --sort usage

# Sort by recency
/fire-skill list --sort recent

# Show only general (cross-project) skills
/fire-skill list --scope general

# Show unused skills (discovery mode)
/fire-skill list --unused

# Show quarantined skills
/fire-skill list --quarantine
```

<step number="1">
### Display Format

```
=============================================================
                 SKILLS LIBRARY — {FILTER}
=============================================================

  {N} skills | {M} categories | {X} general | {Y} project

-------------------------------------------------------------
  #   Skill                        Category        Type    Diff  Used
-------------------------------------------------------------
  1.  retry-backoff                api-patterns    api-int  med    12
  2.  connection-pool-timeout      database-sol    debug    hard    8
  3.  react-hooks-order-debugging  frontend        debug    med     6
  4.  jwt-refresh-rotation         security        api-int  hard    4
  5.  liveclock-extraction         performance     ui-comp  med     3
  ...

-------------------------------------------------------------
  Page 1/3 | [n]ext [p]rev [v]iew {#} [s]earch [q]uit
=============================================================
```

**Column abbreviations:**
- Type: `debug` = debug-pattern, `api-int` = api-integration, `ui-comp` = ui-component, `arch` = architecture, `devops` = devops-recipe, `gen` = general
- Diff: `easy`, `med`, `hard`
- Used: times applied across all projects
</step>

---

## /fire-skill stats

Usage analytics for skills — which are most valuable, which are unused.

```bash
# Overview stats
/fire-skill stats

# Stats for a specific skill
/fire-skill stats retry-backoff

# Stats by category
/fire-skill stats --category api-patterns

# Export as JSON
/fire-skill stats --export json
```

<step number="1">
### Analytics Display

```
=============================================================
              SKILLS ANALYTICS DASHBOARD
=============================================================

Library Health:
  Total Skills:      {N}
  General Skills:    {X} ({X/N}%)
  Project Skills:    {Y} ({Y/N}%)
  Quarantined:       {Q}
  With Code Examples: {C} ({C/N}%)
  Average Difficulty: {avg}

-------------------------------------------------------------
TOP 10 MOST USED SKILLS
-------------------------------------------------------------
  #  Skill                        Uses  Success  Last Used
  1. retry-backoff                 12    100%     2026-03-10
  2. connection-pool-timeout        8     87%     2026-03-09
  3. react-hooks-order             6    100%     2026-03-08
  ...

-------------------------------------------------------------
UNUSED SKILLS (consider archiving or improving)
-------------------------------------------------------------
  - ecommerce/cart-state-machine   (created 2026-01-15, never used)
  - video-media/hls-chunking       (created 2026-01-10, never used)
  ...

-------------------------------------------------------------
CATEGORY BREAKDOWN
-------------------------------------------------------------
  Category             Skills  Used  Avg Success
  api-patterns            12     45    94%
  database-solutions       8     32    91%
  frontend                15     28    96%
  methodology             37      8    85%
  security                 6     18    89%
  ...

-------------------------------------------------------------
SKILL TYPE DISTRIBUTION
-------------------------------------------------------------
  debug-pattern:       [========        ] 25%
  api-integration:     [======          ] 18%
  ui-component:        [====            ] 12%
  architecture:        [===             ] 10%
  devops-recipe:       [==              ]  6%
  general:             [=========       ] 29%

-------------------------------------------------------------
RECOMMENDATIONS
-------------------------------------------------------------

  1. ARCHIVE: {N} skills unused for 60+ days
  2. IMPROVE: {M} skills have <80% success rate
  3. GAP: No skills for category "{category}" — consider adding
  4. UPGRADE: {X} skills still using old format (no type field)

=============================================================
```
</step>

---

## /fire-skill export

Export skills for sharing with other users or projects.

```bash
# Export a single skill as standalone markdown
/fire-skill export retry-backoff

# Export to skills.sh format (SKILL.md in a directory)
/fire-skill export retry-backoff --format skills-sh

# Export a category as a zip-ready directory
/fire-skill export --category api-patterns --output ./export/

# Export all general skills
/fire-skill export --scope general --output ./export/
```

<step number="1">
### Export Process

1. Read the skill file
2. Run credential filter (MANDATORY — never export with real secrets)
3. Convert to requested format
4. Add attribution header

**Credential filter is MANDATORY on export.** Same logic as Step 4.6 in
`/fire-add-new-skill`. Real API keys, passwords, and connection strings
are replaced with `YOUR_*` placeholders.

**skills.sh format conversion:**
```
{skill-name}/
├── SKILL.md           # Frontmatter name + description + body
├── scripts/           # (if skill has runnable scripts)
└── references/        # (if skill has reference files)
```

**Attribution header added to exports:**
```markdown
<!-- Exported from Dominion Flow Skills Library -->
<!-- Original: ~/.claude/plugins/dominion-flow/skills-library/{path} -->
<!-- Export date: {date} -->
```
</step>

---

## /fire-skill browse

Interactive skill browser with preview and apply actions.

```bash
/fire-skill browse
/fire-skill browse --category frontend
```

<step number="1">
### Browse Interface

```
=============================================================
            SKILL BROWSER — {category or "All"}
=============================================================

Categories:
  [1] api-patterns (12)      [2] database-solutions (8)
  [3] frontend (15)          [4] security (6)
  [5] performance (5)        [6] testing (4)
  [7] infrastructure (3)     [8] methodology (37)
  [9] _general (32)         [10] _quarantine (2)

Select category or type search query: > _

-------------------------------------------------------------
```

After selecting a category, show skills with one-line descriptions.
Selecting a skill shows a preview with:
- Problem summary (first 3 lines)
- Tags and difficulty
- Usage count
- Quick actions: [Apply to plan] [View full] [Edit] [Back]

</step>

---

## /fire-skill upgrade

Upgrade older skills to the latest template format.

```bash
# Upgrade a specific skill
/fire-skill upgrade database-solutions/connection-pool-timeout

# Upgrade all skills in a category
/fire-skill upgrade --category api-patterns

# Promote a quarantined skill
/fire-skill upgrade quarantined-skill --promote

# Dry-run to see what would change
/fire-skill upgrade --all --dry-run
```

<step number="1">
### Upgrade Process

1. Read the current skill file
2. Detect the skill type from content (or ask if ambiguous)
3. Map existing sections to the new template
4. Add missing sections with `[TODO]` placeholders
5. Add `type` field to frontmatter if missing
6. Preserve all existing content — never delete user-written content
7. Show diff and confirm before saving

```
-------------------------------------------------------------
UPGRADE: {skill-name}
-------------------------------------------------------------

Detected type: debug-pattern
Template:      skill-debug-pattern.md

Changes:
  + Added: type: debug-pattern (frontmatter)
  + Added: ## Detection section ([TODO] placeholder)
  + Added: ## Elimination Checklist section ([TODO] placeholder)
  + Added: ## Verification section ([TODO] placeholder)
  ~ Renamed: ## Fix → ## Solution Pattern
  = Preserved: all existing content

Apply changes? [Y]es [N]o [D]iff [P]review: > _
-------------------------------------------------------------
```

**Promote from quarantine:**
```bash
/fire-skill upgrade imported-skill --promote
```
Moves from `_quarantine/{name}.md` to `{category}/{name}.md`,
removes `quarantine_reason` field, updates index.
</step>

---

## Auto-Skill Detection

> Replaces the auto-contribution triggers from `/fire-add-new-skill`

When active (opt-in via `--auto-detect` in `/fire-loop` or session config),
the system monitors for skill-worthy moments:

**Detection Signals:**
1. **Complexity spike** — task took >30 min or multiple iterations
2. **Research-then-solve** — web searches followed by successful implementation
3. **Debug breakthrough** — multiple failed hypotheses then success
4. **Pattern repetition** — similar code written 3+ times across sessions
5. **Comment markers** — `// tricky:`, `// pattern:`, `// discovered:`

**When detected:**
```
-------------------------------------------------------------
            SKILL-WORTHY MOMENT DETECTED
-------------------------------------------------------------

Signal:    Debug breakthrough (3 hypotheses eliminated)
Pattern:   Connection pool exhaustion under concurrent requests
Solution:  Configured idle timeout + max connections per service

Suggested skill:
  Name:     connection-pool-concurrent-fix
  Type:     debug-pattern
  Category: database-solutions

  [Create now]  [Later]  [Ignore this pattern]
-------------------------------------------------------------
```

Selecting "Create now" launches `/fire-skill create` pre-filled with
the detected context.

---

## Command Aliases

For convenience, these aliases work:

| Alias | Expands To |
|-------|-----------|
| `/fire-skill new` | `/fire-skill create` |
| `/fire-skill add` | `/fire-skill create` |
| `/fire-skill find` | `/fire-search` (existing search command) |
| `/fire-skill ls` | `/fire-skill list` |
| `/fire-skill check` | `/fire-skill test` |
| `/fire-skill info` | `/fire-skill stats` |

---

## Integration Points

| System | How It Connects |
|--------|----------------|
| `/fire-add-new-skill` | `create` action replaces the old wizard (backward-compatible) |
| `/fire-search` | `list` and `browse` complement existing search |
| `/fire-analytics` | `stats` provides the same data in unified format |
| `/fire-skills-sync` | `export`/`import` work with the sync system |
| `/fire-discover` | Auto-detect feeds into `create --from session` |
| `/fire-validate-skills` | `test` consolidates validation |
| Security scanner | `import` always runs deep scan; `create` runs standard scan |
| Credential filter | `export` and `create` both run credential checks |

## Related Commands

- `/fire-add-new-skill` — Original wizard (still works, `create` is the modern path)
- `/fire-search` — Full-featured skill search with scoring
- `/fire-skills-sync` — Bidirectional sync with global library
- `/fire-skills-history` — Version history for skills
- `/fire-analytics` — Detailed usage analytics
- `/fire-discover` — AI-powered pattern discovery
- `/fire-validate-skills` — Batch validation
