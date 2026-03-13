---
# Dominion Flow Frontmatter (machine-readable)
project: {project_name}
phase: {phase_number}-{phase_name}
plan: {plan_number}
subsystem: {subsystem}
duration: "{duration_minutes} min"
start_time: "{start_time_iso}"
end_time: "{end_time_iso}"

# Skills & Quality (WARRIOR integration)
skills_applied:
{skills_applied_yaml}
honesty_checkpoints:
{honesty_checkpoints_yaml}
validation_score: {validation_passed}/{validation_total}

# Dominion Flow Execution Metadata
requires: [{requires}]
provides: [{provides}]
affects: [{affects}]
tech_stack_added: [{tech_stack_added}]
patterns_established: [{patterns_established}]
key_files:
  created:
{files_created_yaml}
  modified:
{files_modified_yaml}
key_decisions:
{key_decisions_yaml}
---

# Power Handoff: Plan {phase_number}-{plan_number}

## Quick Summary
{quick_summary}

---

## Dominion Flow Accomplishments

### Task Commits
| Task | Description | Commit | Status |
|------|-------------|--------|--------|
{task_commits_rows}

### Files Created/Modified
**Created ({files_created_count} files):**
{files_created_list}

**Modified ({files_modified_count} files):**
{files_modified_list}

### Decisions Made
{decisions_made_list}

---

## Skills Applied (WARRIOR)

{skills_applied_details}

---

## WARRIOR 7-Step Handoff

### W - Work Completed
{work_completed}

### A - Assessment
{assessment}

### R - Resources
**Environment Variables Required:**
```bash
{env_vars}
```

**Database Tables:**
{database_tables}

**External Services:**
{external_services}

**Credentials/Access:**
{credentials_access}

### R - Readiness
**Ready For:**
{ready_for}

**Blocked On:** {blocked_on}

**Next Steps:**
{next_steps}

### I - Issues
**Current Issues:**
{current_issues}

**Known Limitations (Deferred):**
{known_limitations}

### O - Outlook
**Next Session Should:**
{next_session_should}

**After This Phase:**
{after_this_phase}

### R - References
**Skills Used:**
{skills_used_list}

**Commits:**
{commits_list}

**Related Work:**
{related_work}

**External Resources:**
{external_resources}

---

## Metrics

| Metric | Value |
|--------|-------|
| Execution Time | {duration_minutes} min |
| Files Created | {files_created_count} |
| Files Modified | {files_modified_count} |
| Tests Added | {tests_added_count} |
| Test Coverage | {test_coverage}% |
| Validation Score | {validation_passed}/{validation_total} |
| Skills Applied | {skills_count} |

---

## Resume Instructions

To continue this work in a new session:

```bash
# 1. Read this handoff (auto-injected by SessionStart hook)
# 2. Check current state
/fire-dashboard

# 3. Resume work
/fire-6-resume

# 4. Or continue specific phase
/fire-3-execute {next_phase}
```

---

*Handoff created: {handoff_timestamp}*
*Session ID: {session_id}*
