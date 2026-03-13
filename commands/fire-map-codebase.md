---
description: Analyze codebase with parallel mapper agents to produce structured documentation
---

# /fire-map-codebase

> Analyze existing codebase using parallel agents to produce structured codebase documents

---

## Purpose

Analyze existing codebase using parallel fire-codebase-mapper agents to produce structured codebase documents. Each mapper agent explores a focus area and **writes documents directly** to `.planning/codebase/`. The orchestrator only receives confirmations, keeping context usage minimal.

**Output:** `.planning/codebase/` folder with 7 structured documents about the codebase state.

---

## Arguments

```yaml
arguments:
  focus_area:
    required: false
    type: string
    description: "Optional area to focus mapping on (e.g., 'api', 'auth', 'database')"
    example: "/fire-map-codebase auth"
```

---

## When to Use

**Use /fire-map-codebase for:**
- Brownfield projects before initialization (understand existing code first)
- Refreshing codebase map after significant changes
- Onboarding to an unfamiliar codebase
- Before major refactoring (understand current state)
- When CONSCIENCE.md references outdated codebase info
- Before `/fire-0-orient` when joining existing project

**Skip /fire-map-codebase for:**
- Greenfield projects with no code yet (nothing to map)
- Trivial codebases (<5 files)

---

## Process

### Step 1: Check Existing Map

```bash
ls .planning/codebase/*.md 2>/dev/null | wc -l
```

**If codebase documents exist:**

Use AskUserQuestion:
- header: "Existing Map"
- question: "Codebase map already exists. What would you like to do?"
- options:
  - "Refresh all (Recommended)" - Re-analyze entire codebase
  - "Refresh specific area" - Only update one focus area
  - "Skip" - Keep existing map

### Step 2: Create Directory Structure

```bash
mkdir -p .planning/codebase
```

### Step 3: Display Spawning Banner

```
+------------------------------------------------------------------------------+
| FIRE MAP CODEBASE                                                            |
+------------------------------------------------------------------------------+
|                                                                              |
|  Spawning 4 parallel mapper agents...                                        |
|                                                                              |
|    -> Agent 1: Tech focus (STACK.md, INTEGRATIONS.md)                        |
|    -> Agent 2: Architecture focus (ARCHITECTURE.md, STRUCTURE.md)            |
|    -> Agent 3: Quality focus (CONVENTIONS.md, TESTING.md)                    |
|    -> Agent 4: Concerns focus (CONCERNS.md)                                  |
|                                                                              |
|  Focus area: {focus_area or "entire codebase"}                               |
|                                                                              |
+------------------------------------------------------------------------------+
```

### Step 4: Spawn Parallel Mapper Agents

**Agent 1: Tech Focus**
```
Task(prompt="
<focus>tech</focus>
<area>{focus_area or 'all'}</area>

<instructions>
Analyze the codebase for technology stack and integrations.

Write these files:
1. .planning/codebase/STACK.md
   - Languages and versions
   - Frameworks and libraries
   - Build tools and bundlers
   - Runtime environments

2. .planning/codebase/INTEGRATIONS.md
   - External APIs consumed
   - Third-party services
   - Database connections
   - Message queues / event systems

Use template structure. Write files directly.
Return: 'TECH MAPPING COMPLETE' with line counts.
</instructions>
", subagent_type="fire-codebase-mapper", description="Map tech stack")
```

**Agent 2: Architecture Focus**
```
Task(prompt="
<focus>arch</focus>
<area>{focus_area or 'all'}</area>

<instructions>
Analyze the codebase for architecture and structure.

Write these files:
1. .planning/codebase/ARCHITECTURE.md
   - System architecture overview
   - Component boundaries
   - Data flow patterns
   - Key abstractions

2. .planning/codebase/STRUCTURE.md
   - Directory organization
   - Module boundaries
   - Entry points
   - Configuration locations

Use template structure. Write files directly.
Return: 'ARCH MAPPING COMPLETE' with line counts.
</instructions>
", subagent_type="fire-codebase-mapper", description="Map architecture")
```

**Agent 3: Quality Focus**
```
Task(prompt="
<focus>quality</focus>
<area>{focus_area or 'all'}</area>

<instructions>
Analyze the codebase for conventions and testing.

Write these files:
1. .planning/codebase/CONVENTIONS.md
   - Naming conventions
   - Code style patterns
   - Error handling patterns
   - Logging patterns

2. .planning/codebase/TESTING.md
   - Test framework(s)
   - Test organization
   - Coverage areas
   - Testing patterns

Use template structure. Write files directly.
Return: 'QUALITY MAPPING COMPLETE' with line counts.
</instructions>
", subagent_type="fire-codebase-mapper", description="Map quality patterns")
```

**Agent 4: Concerns Focus**
```
Task(prompt="
<focus>concerns</focus>
<area>{focus_area or 'all'}</area>

<instructions>
Analyze the codebase for technical debt and concerns.

Write this file:
1. .planning/codebase/CONCERNS.md
   - Technical debt identified
   - Security considerations
   - Performance bottlenecks
   - Maintainability issues
   - Missing documentation
   - Deprecated patterns

Use template structure. Write file directly.
Return: 'CONCERNS MAPPING COMPLETE' with line counts.
</instructions>
", subagent_type="fire-codebase-mapper", description="Map concerns")
```

### Step 5: Verify Completion

Wait for all 4 agents. Verify all 7 documents exist:

```bash
for doc in STACK INTEGRATIONS ARCHITECTURE STRUCTURE CONVENTIONS TESTING CONCERNS; do
  [ -f ".planning/codebase/${doc}.md" ] && echo "OK: ${doc}.md" || echo "MISSING: ${doc}.md"
done
```

Count lines in each document.

### Step 6: Commit Codebase Map

```bash
git add .planning/codebase/
git commit -m "$(cat <<'EOF'
docs: map codebase structure

Generated 7 codebase documents:
- STACK.md: Technology stack
- INTEGRATIONS.md: External integrations
- ARCHITECTURE.md: System architecture
- STRUCTURE.md: Directory organization
- CONVENTIONS.md: Code conventions
- TESTING.md: Test patterns
- CONCERNS.md: Technical debt

Focus: {focus_area or 'entire codebase'}
EOF
)"
```

### Step 7: Sabbath Rest - Context Persistence

Update persistent state:

```markdown
## .claude/dominion-flow.local.md

### Codebase Map
- Generated: {timestamp}
- Focus: {focus_area or 'entire codebase'}
- Documents: 7
- Location: .planning/codebase/
```

---

## Output Documents

| Document | Contents |
|----------|----------|
| `STACK.md` | Languages, frameworks, dependencies, build tools |
| `INTEGRATIONS.md` | External APIs, services, databases, queues |
| `ARCHITECTURE.md` | System design, components, data flow |
| `STRUCTURE.md` | Directory layout, modules, entry points |
| `CONVENTIONS.md` | Code style, patterns, naming |
| `TESTING.md` | Test framework, organization, coverage |
| `CONCERNS.md` | Tech debt, security, performance issues |

---

## Completion Display

```
+------------------------------------------------------------------------------+
| CODEBASE MAPPING COMPLETE                                                    |
+------------------------------------------------------------------------------+
|                                                                              |
|  Documents created in .planning/codebase/:                                   |
|                                                                              |
|    STACK.md          {lines} lines - Technology stack                        |
|    INTEGRATIONS.md   {lines} lines - External integrations                   |
|    ARCHITECTURE.md   {lines} lines - System architecture                     |
|    STRUCTURE.md      {lines} lines - Directory organization                  |
|    CONVENTIONS.md    {lines} lines - Code conventions                        |
|    TESTING.md        {lines} lines - Test patterns                           |
|    CONCERNS.md       {lines} lines - Technical debt                          |
|                                                                              |
|  Commit: {hash}                                                              |
|                                                                              |
+------------------------------------------------------------------------------+
| NEXT UP                                                                      |
+------------------------------------------------------------------------------+
|                                                                              |
|  -> Run `/fire-1a-new` to initialize project with this context               |
|  -> Or run `/fire-0-orient` if joining an existing project                  |
|  -> Or run `/fire-2-plan` to start planning with codebase knowledge         |
|                                                                              |
+------------------------------------------------------------------------------+
```

---

## Success Criteria

- [ ] `.planning/codebase/` directory created
- [ ] All 7 codebase documents written by mapper agents
- [ ] Documents follow template structure
- [ ] Parallel agents completed without errors
- [ ] Changes committed to git
- [ ] Sabbath Rest state updated
- [ ] User knows next steps

---

## References

- **Agent:** Uses `fire-codebase-mapper` agent (parallel exploration)
- **Related:** `/fire-0-orient` - Uses codebase map for orientation
- **Related:** `/fire-1a-new` - Uses codebase map for project initialization
- **Brand:** `@references/ui-brand.md`
