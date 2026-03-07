---
description: Start a new milestone cycle with questioning, research, requirements, and roadmap
---

# /fire-new-milestone

> Start a new milestone through unified flow: questioning -> research -> requirements -> roadmap

---

## Purpose

Start a new milestone for an existing project. This is the brownfield equivalent of `/fire-1a-new`. The project exists, PROJECT.md has history. This command gathers "what's next" and takes you through the full cycle.

**Creates/Updates:**
- `.planning/PROJECT.md` - Updated with new milestone goals
- `.planning/research/` - Domain research (optional)
- `.planning/REQUIREMENTS.md` - Scoped requirements
- `.planning/VISION.md` - Phase structure
- `.planning/CONSCIENCE.md` - Updated project memory

**After this command:** Run `/fire-2-plan [N]` to start execution.

---

## Arguments

```yaml
arguments:
  milestone_name:
    required: false
    type: string
    description: "Optional milestone name (e.g., 'v1.1 Notifications')"
    example: "/fire-new-milestone v1.1 Notifications"
```

---

## Process

### Phase 1: Validate Project

**MANDATORY FGTAT STEP - Execute these checks before ANY user interaction:**

```bash
[ -f .planning/PROJECT.md ] || { echo "ERROR: No PROJECT.md. Run /fire-1a-new first."; exit 1; }
```

Check for active milestone (VISION.md exists):

```bash
[ -f .planning/VISION.md ] && echo "ACTIVE_MILESTONE" || echo "READY_FOR_NEW"
```

**If ACTIVE_MILESTONE:**

Use AskUserQuestion:
- header: "Active Milestone"
- question: "A milestone is in progress. What would you like to do?"
- options:
  - "Complete current first (Recommended)" - Run /fire-complete-milestone
  - "Continue anyway" - Start new milestone (will archive current)

### Phase 2: Present Context

Display banner:

```
+------------------------------------------------------------------------------+
| DOMINION FLOW > NEW MILESTONE                                                   |
+------------------------------------------------------------------------------+
```

Present what shipped:

```
Last milestone: v[X.Y] [Name] (shipped [DATE])

Key accomplishments:
- [From MILESTONES.md]
- [From MILESTONES.md]

Validated requirements:
- [From PROJECT.md Validated section]

Pending todos:
- [From CONSCIENCE.md if any]
```

### Phase 3: Deep Questioning

Display banner:

```
+------------------------------------------------------------------------------+
| DOMINION FLOW > QUESTIONING                                                     |
+------------------------------------------------------------------------------+
```

**Open the conversation:**

Ask inline (freeform, NOT AskUserQuestion):

"What do you want to build next?"

Wait for response. This gives context for intelligent follow-up questions.

**Follow the thread:**

Based on their response, ask follow-up questions that dig deeper. Use AskUserQuestion with options that probe what they mentioned.

Keep following threads. Each answer opens new threads to explore:
- What excited them
- What problem sparked this
- What they mean by vague terms
- What it would actually look like
- What's already decided

**WARRIOR Enhancement - Honesty Protocol:**

Before finalizing understanding, acknowledge:
- What I understand clearly
- What I'm uncertain about
- What I'm assuming

**Decision gate:**

When ready, use AskUserQuestion:
- header: "Ready?"
- question: "I think I understand what you're after. Ready to update PROJECT.md?"
- options:
  - "Update PROJECT.md" - Move forward
  - "Keep exploring" - Share more / ask more

### Phase 4: Determine Milestone Version

Parse last version from MILESTONES.md and suggest next:

Use AskUserQuestion:
- header: "Version"
- question: "What version is this milestone?"
- options:
  - "v[X.Y+0.1] (patch)" - Minor update
  - "v[X+1].0 (major)" - Major release
  - "Custom" - I'll specify

### Phase 5: Update PROJECT.md

Update `.planning/PROJECT.md` with new milestone section:

```markdown
## Current Milestone: v[X.Y] [Name]

**Goal:** [One sentence describing milestone focus]

**Target features:**
- [Feature 1]
- [Feature 2]
- [Feature 3]
```

Commit:

```bash
git add .planning/PROJECT.md
git commit -m "$(cat <<'EOF'
docs: start milestone v[X.Y] [Name]

[One-liner describing milestone focus]
EOF
)"
```

### Phase 6: Research Decision

Use AskUserQuestion:
- header: "Research"
- question: "Research the domain ecosystem before defining requirements?"
- options:
  - "Research first (Recommended)" - Discover patterns, expected features
  - "Skip research" - I know this domain well

**If "Research first":**

Display banner:
```
+------------------------------------------------------------------------------+
| DOMINION FLOW > RESEARCHING                                                     |
+------------------------------------------------------------------------------+

Researching [domain] ecosystem...
```

Spawn 4 parallel fire-project-researcher agents:
- Stack research
- Features research
- Architecture research
- Pitfalls research

After completion, spawn synthesizer to create RECORD.md.

**Adversarial Fact-Check (v11.0):**
After the synthesizer writes SYNTHESIS.md, spawn `fire-fact-checker`:
- Reads SYNTHESIS.md
- Independently attempts to disprove top findings
- Produces `.planning/research/CONTESTED-CLAIMS.md`
- Adjusts confidence levels based on adversarial verification
- Any CONTESTED findings are flagged for the roadmapper's risk assessment

```
Spawning fire-fact-checker for adversarial verification...
```

### Phase 7: Define Requirements

Display banner:
```
+------------------------------------------------------------------------------+
| DOMINION FLOW > DEFINING REQUIREMENTS                                           |
+------------------------------------------------------------------------------+
```

**If research exists:** Read FEATURES.md and present by category.

**If no research:** Gather requirements through conversation.

**Scope each category:**

For each category, use AskUserQuestion with multiSelect:
- header: "[Category name]"
- question: "Which [category] features are in this milestone?"
- options: [Feature list]

**Generate REQUIREMENTS.md:**

Create `.planning/REQUIREMENTS.md` with:
- v1 Requirements grouped by category (checkboxes, REQ-IDs)
- v2 Requirements (deferred)
- Out of Scope (explicit exclusions)
- Traceability section

Commit:

```bash
git add .planning/REQUIREMENTS.md
git commit -m "$(cat <<'EOF'
docs: define v[X.Y] requirements

[X] requirements across [N] categories
[Y] requirements deferred to v2
EOF
)"
```

### Phase 8: Create Roadmap

Display banner:
```
+------------------------------------------------------------------------------+
| DOMINION FLOW > CREATING ROADMAP                                                |
+------------------------------------------------------------------------------+

Spawning roadmapper...
```

Spawn fire-roadmapper agent with context:
- PROJECT.md
- REQUIREMENTS.md
- Research RECORD.md (if exists)
- Starting phase number

**Handle roadmapper return:**

**If `## ROADMAP CREATED`:**
- Present roadmap inline
- Ask for approval

**If approved:** Commit roadmap.

### Phase 9: Sabbath Rest - Context Persistence

Update persistent state:

```markdown
## .claude/fire-flow.local.md

### Current Milestone
- Version: v[X.Y]
- Name: [Name]
- Phases: [count]
- Requirements: [count]
- Started: {timestamp}
- Status: Ready to plan
- Next: /fire-2-plan [first_phase]
```

---

## Completion Display

```
+------------------------------------------------------------------------------+
| DOMINION FLOW > MILESTONE INITIALIZED                                           |
+------------------------------------------------------------------------------+
|                                                                              |
|  v[X.Y] [Name]                                                               |
|                                                                              |
|  | Artifact       | Location                    |                            |
|  |----------------|-----------------------------                             |
|  | Project        | .planning/PROJECT.md        |                            |
|  | Research       | .planning/research/         |                            |
|  | Requirements   | .planning/REQUIREMENTS.md   |                            |
|  | Roadmap        | .planning/VISION.md        |                            |
|                                                                              |
|  [N] phases | [X] requirements | Ready to build                             |
|                                                                              |
+------------------------------------------------------------------------------+
| NEXT UP                                                                      |
+------------------------------------------------------------------------------+
|                                                                              |
|  Phase [N]: [Phase Name] - [Goal]                                            |
|                                                                              |
|  -> Run `/fire-1a-discuss [N]` to gather context and clarify approach       |
|  -> Or run `/fire-2-plan [N]` to plan directly                              |
|                                                                              |
|  Tip: Run `/clear` first for fresh context window                            |
|                                                                              |
+------------------------------------------------------------------------------+
```

---

## Success Criteria

- [ ] Project validated (PROJECT.md exists)
- [ ] Previous milestone context presented
- [ ] Deep questioning completed (threads followed)
- [ ] Honesty protocol applied (acknowledged uncertainties)
- [ ] Milestone version determined
- [ ] PROJECT.md updated -> committed
- [ ] Research completed (if selected) -> committed
- [ ] REQUIREMENTS.md created with REQ-IDs -> committed
- [ ] VISION.md created -> committed
- [ ] Sabbath Rest state updated
- [ ] User knows next step is `/fire-2-plan [N]`

---

## References

- **Related:** `/fire-1a-new` - Initialize new project (greenfield)
- **Related:** `/fire-complete-milestone` - Archive completed milestone
- **Related:** `/fire-1a-discuss` - Discuss phase before planning
- **Agent:** Uses `fire-roadmapper` for roadmap creation
- **Agent:** Uses `fire-project-researcher` for domain research
- **Brand:** `@references/ui-brand.md`
