# Project State

## Project Reference
- **Project:** {project_name}
- **Core value:** {core_value}
- **Current focus:** Phase {current_phase} - {phase_name}
- **Milestone:** v{milestone_version} [{milestone_status}]

## Current Position
- **Phase:** {current_phase} of {total_phases}
- **Breath:** {current_wave}
- **Status:** {status}
- **Last activity:** {last_activity_date} - {last_activity_description}
- **Progress:** [{progress_bar}] {progress_percent}%

## Dominion Flow Progress Tracking
### Phase Status
| Phase | Name | Status | Plans | Completed |
|-------|------|--------|-------|-----------|
{phase_status_rows}

### Recent Completions
{recent_completions}

## WARRIOR Integration
- **Skills Applied:** {total_skills_applied} total
{skills_applied_list}

- **Honesty Checkpoints:** {honesty_checkpoint_count} (agents admitted gaps, researched, proceeded)
- **Validation Status:** Phase {last_validated_phase} passed {validation_score}/70 checks

## Performance Metrics
### Time Tracking
- **Session start:** {session_start}
- **Total time this phase:** {phase_time}
- **Average plan duration:** {avg_plan_duration}

### Quality Metrics
- **Test coverage:** {test_coverage}%
- **Lint errors:** {lint_errors}
- **Build status:** {build_status}

## Accumulated Context

### Skills Library Usage
- **Most used:** {most_used_skill_category} ({most_used_count} applications)
- **Recent:** {recent_skill} (Phase {recent_skill_phase})
- **Categories applied:** {categories_applied}

### Decisions
> Full decision log: `.planning/DECISION_LOG.md` (v3.2 enhancement)
> Quick reference of recent decisions below; see log for full rationale and options considered.

| Date | Decision | Rationale | Phase |
|------|----------|-----------|-------|
{decisions_rows}

### Assumptions Health
> Full registry: `.planning/ASSUMPTIONS.md`

| Status | Count |
|--------|-------|
| Validated | {validated_count} |
| Unvalidated | {unvalidated_count} |
| Invalidated | {invalidated_count} |

### Blockers & Issues
{blockers_list}

## Session Continuity
- **Last session:** {last_session_timestamp}
- **Stopped at:** {stopped_at_description}
- **Resume file:** .planning/WARRIOR-HANDOFF.md
- **Next:** {next_action}

## Quick Resume Commands
```bash
# Check current status
/fire-dashboard

# Resume work
/fire-6-resume

# Continue execution
/fire-3-execute {current_phase}

# View skills applied
/fire-analytics --project
```

---
*Last updated: {last_updated}*
