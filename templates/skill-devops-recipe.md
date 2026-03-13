---
name: {{SKILL_NAME}}
category: {{CATEGORY}}
type: devops-recipe
version: 1.0.0
contributed: {{DATE}}
contributor: {{PROJECT}}
last_updated: {{DATE}}
tags: [{{TAGS}}]
difficulty: {{DIFFICULTY}}
usage_count: 0
success_rate: 100
---

# {{TITLE}}

## Problem

[What infrastructure/deployment/CI challenge does this solve?]

## Prerequisites

- [ ] [Tool/service 1] installed (version X+)
- [ ] [Tool/service 2] configured
- [ ] [Access/permissions] granted

## Environment Variables

```env
# Required
{{REQUIRED_ENV_VARS}}

# Optional
{{OPTIONAL_ENV_VARS}}
```

## Solution

### Step 1: [Setup]

```bash
{{SETUP_COMMANDS}}
```

### Step 2: [Configuration]

```yaml
# config-file.yml
{{CONFIG_FILE}}
```

### Step 3: [Deployment/Execution]

```bash
{{DEPLOY_COMMANDS}}
```

## Verification

```bash
# Verify the setup works
{{VERIFICATION_COMMANDS}}
```

Expected output:
```
{{EXPECTED_OUTPUT}}
```

## Rollback Plan

If something goes wrong:

```bash
{{ROLLBACK_COMMANDS}}
```

## Monitoring

What to watch after applying:

| Metric | Normal Range | Alert Threshold |
|--------|-------------|----------------|
| [Metric 1] | [Range] | [Threshold] |
| [Metric 2] | [Range] | [Threshold] |

## Common Failures

1. **[Failure 1]** - Cause: [X] - Fix: [Y]
2. **[Failure 2]** - Cause: [X] - Fix: [Y]

## When to Use

- [Scenario 1]
- [Scenario 2]

## When NOT to Use

- [Anti-pattern 1]

## Related Skills

- [related-skill] - [description]

## References

- Contributed from: {{PROJECT}}
