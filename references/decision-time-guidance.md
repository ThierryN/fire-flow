# Decision-Time Guidance System

> Lightweight micro-instruction injection at key decision moments — inspired by Replit Agent's decision-time compute pattern.

---

## Overview

Instead of bloating system prompts with every possible instruction, Decision-Time Guidance (DTG) injects **targeted micro-instructions from the skills library at the exact moment they're needed**. This keeps context lean while ensuring the right guidance is available at decision points.

**Core principle:** Don't pre-load everything. Load the right thing at the right time.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    DECISION POINT DETECTED                    │
│                                                                │
│  Classifier analyzes:                                         │
│    • Current task type (API, UI, DB, test, deploy, debug)     │
│    • File patterns being touched                               │
│    • Error patterns encountered                                │
│    • Technology stack in use                                   │
│                                                                │
│              ┌──────────────┐                                  │
│              │  SKILLS BANK │                                  │
│              │              │                                  │
│              │  190+ skills │──→ Select 1-3 relevant skills    │
│              │  organized   │                                  │
│              │  by domain   │                                  │
│              └──────────────┘                                  │
│                      │                                         │
│              ┌───────▼───────┐                                 │
│              │ MICRO-INJECT  │                                 │
│              │               │                                 │
│              │ Extract key   │                                 │
│              │ patterns and  │──→ Inject into current context  │
│              │ decision      │                                 │
│              │ guidance      │                                 │
│              └───────────────┘                                 │
└──────────────────────────────────────────────────────────────┘
```

---

## Decision Points

DTG activates at these moments in the Dominion Flow pipeline:

### 1. Task Start (in /fire-execute-plan)

**Trigger:** Beginning a new task from BLUEPRINT.md
**Classifier input:** Task description, file paths, technology tags
**Action:** Search skills library for matching patterns, inject relevant guidance

```
BEFORE executing Task {N}:
  keywords = extract_keywords(task.description + task.files)
  skills = search_skills_library(keywords, limit=3)

  IF skills.found:
    inject: "Apply these patterns for this task:"
    FOR each skill:
      inject: skill.key_pattern + skill.common_pitfalls
```

### 2. Error Encountered (in /fire-loop, /fire-debug)

**Trigger:** Test failure, build error, runtime exception
**Classifier input:** Error message, stack trace, file context
**Action:** Search skills library for error patterns, inject fix guidance

```
ON error_detected(error):
  error_keywords = extract_error_signature(error)
  skills = search_skills_library(error_keywords, category="debug")

  IF skills.found:
    inject: "Known pattern for this error:"
    inject: skill.resolution_steps
  ELSE:
    inject: "No known pattern. Apply systematic debugging protocol."
```

### 3. Architecture Decision (checkpoint:decision in plans)

**Trigger:** Reaching a decision checkpoint in plan execution
**Classifier input:** Decision description, options, constraints
**Action:** Search for relevant architecture patterns, inject trade-off analysis

```
ON checkpoint_decision(decision):
  domain = classify_domain(decision)  # auth, api, database, ui
  skills = search_skills_library(domain + "architecture", limit=2)

  inject: "Consider these proven patterns before deciding:"
  FOR each skill:
    inject: skill.pattern_name + skill.trade_offs
```

### 4. Technology Boundary (new framework/library interaction)

**Trigger:** First interaction with a specific technology in the plan
**Classifier input:** Import statements, package.json changes, file extensions
**Action:** Search for integration-specific skills

```
ON technology_detected(tech):
  skills = search_skills_library(tech.name, category="integrations")

  IF skills.found:
    inject: "Integration guidance for {tech.name}:"
    inject: skill.setup_pattern + skill.gotchas
```

### 5. Test Writing (in testing-enforcement gate)

**Trigger:** About to write or modify tests
**Classifier input:** Test framework, component type, coverage target
**Action:** Search for testing patterns specific to the domain

```
ON test_phase(component):
  skills = search_skills_library(
    component.type + "testing",
    category="methodology"
  )

  inject: "Testing patterns for {component.type}:"
  inject: skill.test_structure + skill.assertion_patterns
```

---

## Classifier Logic

The DTG classifier uses a lightweight keyword-matching approach:

### Input Signals

| Signal | Source | Example |
|--------|--------|---------|
| File extensions | Task files list | `.tsx` → frontend, `.sql` → database |
| Directory patterns | File paths | `src/api/` → backend, `src/components/` → frontend |
| Error signatures | Error output | `ECONNREFUSED` → connection, `TypeError` → type safety |
| Package names | imports/deps | `prisma` → ORM, `stripe` → payments |
| Task verbs | Description | "migrate" → database, "render" → UI, "authenticate" → auth |

### Domain Classification

```
classify_domain(context):
  signals = collect_signals(context)

  domain_scores = {
    backend:  count(signals matching ["api", "route", "middleware", "server", "express"]),
    frontend: count(signals matching ["component", "page", "style", "react", "ui"]),
    database: count(signals matching ["schema", "migration", "query", "model", "prisma"]),
    auth:     count(signals matching ["login", "token", "jwt", "session", "password"]),
    testing:  count(signals matching ["test", "spec", "assert", "mock", "coverage"]),
    deploy:   count(signals matching ["build", "docker", "ci", "deploy", "env"]),
    payments: count(signals matching ["stripe", "payment", "invoice", "subscription"]),
    media:    count(signals matching ["video", "image", "upload", "stream", "player"])
  }

  RETURN top_domains(domain_scores, limit=2)
```

---

## Skills Bank Integration

### Search Protocol

```
search_skills_library(keywords, category=null, limit=3):
  # 1. Exact match on skill filename
  exact = glob("skills-library/**/*{keyword}*.md")

  # 2. Content match in skill files
  content = grep(keywords, "skills-library/**/*.md")

  # 3. Category filter
  IF category:
    results = filter(exact + content, path contains category)
  ELSE:
    results = exact + content

  # 4. Rank by relevance (keyword density in file)
  ranked = sort_by_relevance(results)

  RETURN ranked[:limit]
```

### Micro-Instruction Extraction

Don't inject entire skill files. Extract only the actionable parts:

```
extract_micro_instruction(skill_file):
  sections = parse_markdown_sections(skill_file)

  # Priority extraction order:
  micro = {
    pattern:   sections["## Pattern"] or sections["## Solution"],
    pitfalls:  sections["## Common Pitfalls"] or sections["## Gotchas"],
    checklist: sections["## Checklist"] or sections["## Steps"]
  }

  # Keep it under 20 lines total
  RETURN truncate(micro, max_lines=20)
```

---

## Integration with Dominion Flow Commands

### /fire-execute-plan

```markdown
# In Step 5 (Execute Segments), before each task:

## DTG Check
FOR each task in segment:
  guidance = DTG.classify_and_search(task)
  IF guidance:
    context += "## Guidance for Task {N}\n" + guidance
```

### /fire-loop

```markdown
# In Step 7 (Execute Task), at each iteration:

## DTG Check
IF iteration == 1 OR error_detected OR approach_changed:
  guidance = DTG.classify_and_search(current_context)
  IF guidance != previous_guidance:
    inject(guidance)
```

### /fire-debug

```markdown
# In debug cycle, when new error encountered:

## DTG Check
ON new_error(error):
  guidance = DTG.search_error_pattern(error)
  IF guidance:
    inject: "Known resolution pattern found"
    inject(guidance)
```

---

## Performance Considerations

| Concern | Mitigation |
|---------|-----------|
| Search overhead | Skills library is local filesystem — glob/grep is fast |
| Context bloat | Extract micro-instructions (max 20 lines), not full files |
| Redundant injection | Track injected skills per session, don't re-inject |
| False matches | Require 2+ signal matches before injecting |

---

## Metrics

Track DTG effectiveness in RECORD.md:

```yaml
dtg_metrics:
  activations: [N]        # How many times DTG triggered
  skills_injected: [N]    # Skills that were injected
  skills_useful: [N]      # Skills that influenced the outcome
  missed_guidance: [N]    # Cases where DTG should have fired but didn't
```

---

## References

- **Inspiration:** Replit Agent's "Decision-Time Compute" pattern (inject micro-instructions at decision points instead of front-loading system prompts)
- **Skills Library:** `~/.claude/plugins/warrior-workflow/skills-library/`
- **Skills Index:** `SKILLS_LIBRARY_INDEX.md`
- **Related:** `references/skills-usage-guide.md`
