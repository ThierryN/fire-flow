---
description: Dedicated ideation and exploration before implementation
---

# /fire-brainstorm

> Explore ideas thoroughly before committing to implementation

---

## Purpose

A dedicated ideation phase inspired by superpowers:brainstorming. Forces divergent thinking, explores alternatives, and documents decisions BEFORE writing code. Prevents premature implementation and ensures requirements are understood.

---

## Arguments

```yaml
arguments:
  topic:
    required: true
    type: string
    description: "What to brainstorm - feature, architecture, problem, etc."
    examples:
      - "/fire-brainstorm 'user authentication system'"
      - "/fire-brainstorm 'how to handle file uploads'"
      - "/fire-brainstorm 'database schema for orders'"

optional_flags:
  --constraints: "Comma-separated constraints to consider"
  --time-box: "Limit brainstorm duration (e.g., '15min')"
  --perspectives: "Number of alternative approaches to explore (default: 3)"
  --output: "Save brainstorm to file (default: .planning/brainstorms/)"
  --no-questions: "Skip clarifying questions, use assumptions"
```

---

## Process

### Step 1: Initialize Brainstorm Session

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      DOMINION FLOW ► BRAINSTORM SESSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Topic: {topic}
Mode: Exploration (no code yet)
```

### Step 2: Clarifying Questions (Unless --no-questions)

**MANDATORY: Understand before exploring.**

```markdown
## Clarifying Questions

Before exploring solutions, I need to understand the problem space.

### Scope Questions
1. What is the primary user/use case for this?
2. What systems/components does this interact with?
3. Are there existing patterns in the codebase to follow?

### Constraint Questions
4. What are the non-negotiables (must-haves)?
5. What are known limitations (tech stack, budget, time)?
6. Are there security/compliance requirements?

### Context Questions
7. Has this been attempted before? What happened?
8. What does "success" look like?
9. Who are the stakeholders?
```

**Wait for user response before proceeding.**

### Step 3: Problem Decomposition

```markdown
## Problem Decomposition

### Core Challenge
{Single sentence describing the essential problem}

### Sub-Problems
1. {Sub-problem 1}
   - Why it matters: {reason}
   - Complexity: Low | Medium | High

2. {Sub-problem 2}
   - Why it matters: {reason}
   - Complexity: Low | Medium | High

3. {Sub-problem 3}
   - Why it matters: {reason}
   - Complexity: Low | Medium | High

### Dependencies
- {Sub-problem 1} must be solved before {Sub-problem 3}
- {Sub-problem 2} can be solved in parallel

### Risk Areas
- {Area with highest uncertainty}
- {Area most likely to change}
```

### Step 4: Explore Alternatives (Divergent Thinking)

**IMPORTANT: Explore at least 3 different approaches.**

```markdown
## Alternative Approaches

### Approach A: {Name}

**Summary:** {One-line description}

**How it works:**
{2-3 sentence explanation}

**Pros:**
- {Pro 1}
- {Pro 2}
- {Pro 3}

**Cons:**
- {Con 1}
- {Con 2}

**Best when:**
{Scenario where this is ideal}

**Complexity:** {Low | Medium | High}

**Skills Library Match:** @skills-library/{category}/{skill}.md

---

### Approach B: {Name}

**Summary:** {One-line description}

**How it works:**
{2-3 sentence explanation}

**Pros:**
- {Pro 1}
- {Pro 2}
- {Pro 3}

**Cons:**
- {Con 1}
- {Con 2}

**Best when:**
{Scenario where this is ideal}

**Complexity:** {Low | Medium | High}

**Skills Library Match:** @skills-library/{category}/{skill}.md

---

### Approach C: {Name}

**Summary:** {One-line description}

**How it works:**
{2-3 sentence explanation}

**Pros:**
- {Pro 1}
- {Pro 2}
- {Pro 3}

**Cons:**
- {Con 1}
- {Con 2}

**Best when:**
{Scenario where this is ideal}

**Complexity:** {Low | Medium | High}

**Skills Library Match:** @skills-library/{category}/{skill}.md
```

### Step 5: Trade-off Analysis

```markdown
## Trade-off Matrix

| Criteria | Weight | Approach A | Approach B | Approach C |
|----------|--------|------------|------------|------------|
| Simplicity | 3 | 8 | 5 | 7 |
| Performance | 2 | 6 | 9 | 7 |
| Maintainability | 3 | 7 | 4 | 8 |
| Time to Implement | 2 | 9 | 3 | 6 |
| Scalability | 2 | 5 | 9 | 7 |
| **Weighted Total** | | **84** | **68** | **82** |

### Analysis

**Approach A wins on:** {criteria}
**Approach B wins on:** {criteria}
**Approach C wins on:** {criteria}

### Hidden Risks

| Approach | Hidden Risk | Mitigation |
|----------|-------------|------------|
| A | {risk} | {mitigation} |
| B | {risk} | {mitigation} |
| C | {risk} | {mitigation} |
```

### Step 6: Recommendation

```markdown
## Recommendation

### Recommended Approach: {A | B | C}

**Why:**
{2-3 sentences explaining the decision}

**Key factors:**
1. {Factor 1}
2. {Factor 2}
3. {Factor 3}

### Implementation Sketch

```
{High-level architecture diagram or flow}
```

### First Steps
1. {First concrete step}
2. {Second concrete step}
3. {Third concrete step}

### Open Questions (To Resolve During Implementation)
- {Question 1}
- {Question 2}

### Decision Record

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| {Decision 1} | {Why} | {What else was considered} |
| {Decision 2} | {Why} | {What else was considered} |
```

### Step 7: Save Brainstorm Document

**Create:** `.planning/brainstorms/{topic-slug}-{timestamp}.md`

### Step 8: Sabbath Rest (Context Persistence)

> *Like humans need sleep to reset, AI agents need state files to resume after context resets.*

**MANDATORY:** Update CONSCIENCE.md to track brainstorm sessions:

```markdown
## Recent Brainstorms
- [{topic}](.planning/brainstorms/{filename}.md) - {timestamp}
  - Recommended: Approach {X}
  - Status: {COMPLETE | PENDING_REVIEW}
  - Next: /fire-2-plan or implementation
```

**Also create/update:** `.claude/fire-brainstorm.local.md`

```markdown
---
last_session: {timestamp}
topic: "{topic}"
status: complete
recommended_approach: "{approach name}"
output_file: ".planning/brainstorms/{filename}.md"
---

# Brainstorm Session State

## Current Session
- Topic: {topic}
- Started: {timestamp}
- Status: {in_progress | complete}

## Session History
| Date | Topic | Outcome | File |
|------|-------|---------|------|
| {date} | {topic} | Approach {X} | {file} |
```

This ensures:
- CONSCIENCE.md tracks all brainstorm decisions for project continuity
- `.local.md` preserves session state if context resets mid-brainstorm

```markdown
# Brainstorm: {Topic}

**Date:** {timestamp}
**Status:** COMPLETE
**Outcome:** Recommended Approach {X}

---

{Full brainstorm content from steps 2-6}

---

## Next Steps

- [ ] Review with stakeholders (if needed)
- [ ] Create detailed plan: `/fire-2-plan` with this as input
- [ ] Begin implementation

---

*Brainstorm facilitated by Dominion Flow*
```

---

## Output Display

```
╔══════════════════════════════════════════════════════════════════════════════╗
║ ✓ BRAINSTORM COMPLETE                                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Topic: {topic}                                                              ║
║  Approaches Explored: 3                                                      ║
║  Recommended: Approach {X} - {name}                                          ║
║                                                                              ║
║  Key Decision: {one-line summary}                                            ║
║                                                                              ║
║  Saved: .planning/brainstorms/{filename}.md                                  ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ NEXT STEPS                                                                   ║
├──────────────────────────────────────────────────────────────────────────────┤
║                                                                              ║
║  → Review the brainstorm document                                            ║
║  → Run `/fire-2-plan` to create detailed implementation plan                ║
║  → Or discuss further if questions remain                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Integration with Dominion Flow

### Before New Project
```bash
/fire-brainstorm "project architecture for {idea}"
# Then
/fire-1a-new
```

### Before Planning Phase
```bash
/fire-brainstorm "how to implement {phase feature}"
# Then
/fire-2-plan N
```

### Standalone Exploration
```bash
/fire-brainstorm "should we use GraphQL or REST"
# Decision documented, no immediate action
```

---

## Anti-Patterns Blocked

- **Jumping to code:** Brainstorm MUST complete before implementation
- **Single solution thinking:** Forces exploration of alternatives
- **Undocumented decisions:** All decisions recorded with rationale
- **Premature optimization:** Focus on understanding, not perfection

---

## Success Criteria

### Required Outputs
- [ ] Problem clearly decomposed
- [ ] At least 3 alternatives explored
- [ ] Trade-offs analyzed with criteria
- [ ] Clear recommendation with rationale
- [ ] Brainstorm document saved

### Quality Markers
- Alternatives are genuinely different (not variations)
- Pros/cons are specific, not generic
- Recommendation matches stated criteria
- Open questions are acknowledged

---

## References

- **Inspiration:** superpowers:brainstorming
- **Template:** `@templates/brainstorm.md`
- **Skills Search:** `/fire-search` for relevant patterns
- **Brand:** `@references/ui-brand.md`
