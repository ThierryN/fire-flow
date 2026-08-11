---
phase: {phase_number}-{phase_name}
plan: {plan_number}
breath: {wave_number}
autonomous: {autonomous}
depends_on: [{depends_on}]
files_modified: [{files_modified}]
skills_to_apply:
{skills_to_apply_yaml}
validation_required:
{validation_required_yaml}
must_haves:
  truths:
{truths_yaml}
  artifacts:
{artifacts_yaml}
  warrior_validation:
{warrior_validation_yaml}
---

# Plan {phase_number}-{plan_number}: {plan_title}

## Objective
{objective}

## Context
@.planning/CONSCIENCE.md
@.planning/VISION.md
@.planning/phases/{phase_number}-{phase_name}/{phase_number}-RESEARCH.md

## Honesty Pre-Check

**What I know:**
{what_i_know}

**What I'm uncertain about:**
{what_im_uncertain_about}

**Skills to reference:**
{skills_to_reference}

## Tasks

{tasks}

## Verification

### Must-Haves
```bash
{musthave_commands}
```

### WARRIOR Validation
```bash
{warrior_validation_commands}
```

## Success Criteria
- [ ] All tasks complete
- [ ] Must-Haves verified
- [ ] WARRIOR validation passed ({warrior_check_count}/{warrior_check_total} checks)
- [ ] Human verification approved (if required)

## Rollback Plan
{rollback_plan}

---

## Task Template Reference

Use this format for each task:

```markdown
<task type="auto|checkpoint:human-verify|checkpoint:pause">
**Action:** {action_description}
**Skills:** {skill_references}
**Steps:**
1. {step_1}
2. {step_2}
3. {step_3}

**Verification:**
```bash
{verification_command}
```

**Done Criteria:** {done_criteria}
</task>
```

---

*Plan created: {created_date}*
*Estimated duration: {estimated_duration}*
