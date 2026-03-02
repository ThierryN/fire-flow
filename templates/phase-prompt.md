# Phase Prompt Template (Dominion Flow Enhanced)

> **Origin:** Ported from Dominion Flow `phase-prompt.md` with SDLC quality gates.

Template for `.planning/phases/XX-name/{phase}-{plan}-BLUEPRINT.md`

---

## File Template

```markdown
---
phase: XX-name
plan: NN
type: execute|tdd
breath: N
depends_on: []
files_modified: []
autonomous: true|false
user_setup: []
must_haves:
  truths: []
  artifacts: []
  key_links: []
skills_to_apply: []
assumptions: []
risk_level: low|medium|high
warrior_validation:
  code_quality: true
  security: false
  performance: false
  testing: true
---

<objective>
[What this plan accomplishes]
Purpose: [Why this matters]
Output: [What artifacts will be created]
</objective>

<execution_context>
@~/.claude/plugins/dominion-flow/templates/summary.md
</execution_context>

<honesty_precheck>
**What I know:**
- [Facts confirmed about this domain/technology]

**What I'm uncertain about:**
- [Areas where research or skills lookup may be needed]

**Skills to reference:**
- [Relevant skills-library entries]

**Assumptions being made:**
- [VALIDATED: confirmed fact]
- [UNVALIDATED: assumption to verify]
</honesty_precheck>

<context>
@.planning/PROJECT.md
@.planning/VISION.md
@.planning/CONSCIENCE.md
@.planning/BLOCKERS.md
[Relevant source files]
</context>

<tasks>

<task type="auto">
  <name>Task 1: [Action-oriented name]</name>
  <files>path/to/file.ext</files>
  <skills>[skill-library reference if applicable]</skills>
  <action>[Specific implementation]</action>
  <verify>[Command or check]</verify>
  <done>[Acceptance criteria]</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>[What needs verification]</what-built>
  <how-to-verify>[Exact steps]</how-to-verify>
  <resume-signal>Type "approved" or describe issues</resume-signal>
</task>

</tasks>

<verification>
### Test Requirements
- [ ] [Test command]
- [ ] Build passes
- [ ] No new warnings

### WARRIOR Quality Gates
- [ ] Code builds without errors
- [ ] Tests pass (existing + new)
- [ ] No regressions
</verification>

<success_criteria>
- All tasks completed
- All verification checks pass
- WARRIOR validation gates passed
</success_criteria>
```

---

## Frontmatter Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `phase` | Yes | Phase identifier |
| `plan` | Yes | Plan number within phase |
| `type` | Yes | `execute` or `tdd` |
| `breath` | Yes | Execution breath (pre-computed) |
| `depends_on` | Yes | Plan IDs this requires |
| `files_modified` | Yes | Files this plan touches |
| `autonomous` | Yes | `true` if no checkpoints |
| `must_haves` | Yes | Goal-backward verification |
| `skills_to_apply` | No | Skills-library references |
| `assumptions` | No | Key assumptions |
| `risk_level` | No | Verification depth (default: low) |

---

## Scope Guidance

- 2-3 tasks per plan, ~50% context max
- Prefer vertical slices (User: model+API+UI) over horizontal layers
- Split by risk level (high-risk separate from low-risk)
- TDD candidates get separate plans

---

## Task Types

| Type | Use For | Autonomy |
|------|---------|----------|
| `auto` | Everything Claude can do | Fully autonomous |
| `checkpoint:human-verify` | Visual/functional checks | Pauses for user |
| `checkpoint:decision` | Implementation choices | Pauses for user |
| `checkpoint:human-action` | Unavoidable manual steps | Pauses for user |
