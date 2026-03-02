---
description: Complete phase transition with metrics collection, bottleneck detection, auto-skill extraction, and trend analysis
---

# /fire-transition

> Phase completion ceremony: metrics, bottleneck report, skill extraction, trend update, and next phase routing.

---

## Arguments

```yaml
arguments:
  phase:
    required: false
    type: string
    description: "Phase to transition from. Defaults to current phase."
```

---

## Process

### Step 1: Validate Phase Completion

```
+---------------------------------------------------------------+
|             DOMINION FLOW >>> PHASE TRANSITION                    |
+---------------------------------------------------------------+
```

Check:
- [ ] All plans in phase have RECORD.md files
- [ ] UAT verification passed (or user override)
- [ ] No open P0 blockers in BLOCKERS.md
- [ ] No open P1 blockers without acknowledgment

If validation fails: present issues, offer fix or override.

### Step 2: Collect Phase Metrics

Aggregate from all RECORD.md files in the phase:

```yaml
Phase Metrics:
  plans_completed: [N]
  total_duration: [N]m
  avg_plan_duration: [N]m
  total_tasks: [N]
  tasks_blocked: [N]
  files_created: [N]
  files_modified: [N]
  lines_added: [N]
  lines_removed: [N]
  tests_added: [N]
  skills_applied: [N]
  honesty_checkpoints: [N]
  total_commits: [N]
  blocker_count: [N]
  blocker_resolution_rate: [N]%
```

### Step 3: Bottleneck Detection

Run bottleneck detection algorithm (see `references/metrics-and-trends.md`):

| Rule | Condition | Flag |
|------|-----------|------|
| Slow Plan | Duration > 2x phase average | BOTTLENECK:SLOW |
| Blocked Plan | >20% tasks blocked | BOTTLENECK:BLOCKED |
| Failed Verification | >1 verification cycle | BOTTLENECK:QUALITY |
| Fan-Out Blocker | Blocks 2+ downstream plans | BOTTLENECK:CRITICAL_PATH |
| Complexity Spike | Lines > 3x average | BOTTLENECK:COMPLEXITY |

```
+---------------------------------------------------------------+
|  BOTTLENECK REPORT                                             |
+---------------------------------------------------------------+
|                                                                 |
|  Flagged Plans:                                                |
|  | Plan | Flag | Duration | Suggestion |                      |
|  |------|------|----------|------------|                      |
|  | 03-05 | SLOW | 18m (avg: 12m) | Break into smaller plans | |
|                                                                 |
|  Phase Health: Speed 7/10, Quality 9/10, Efficiency 8/10      |
|  Overall: 8/10                                                 |
+-----------------------------------------------------------------+
```

### Step 4: Auto-Skill Extraction

Scan all RECORD.md and handoff files for skill candidates:

**Detection signals:**
1. `/* SKILL: name */` markers in code
2. Honesty checkpoints with research + high-confidence resolution
3. Novel decisions with rationale
4. Repeated file modification patterns across plans
5. Bug fix patterns with root cause + prevention

For each candidate:
```
Detected potential skill: [name]
  Category: [category]
  Source: [phase/plan]
  Save to skills library? (y/n/edit)
```

### Step 5: Update Trend Analysis

Update CONSCIENCE.md trends table:

```markdown
## Trends (Last 5 Phases)
| Metric | P1 | P2 | P3 | P4 | P5 | Trend |
|--------|----|----|----|----|-----|-------|
| Avg Plan Duration | 11m | 12m | 9m | 10m | [new] | [calc] |
| Verification Pass Rate | 100% | 100% | 100% | 100% | [new] | [calc] |
| Skill Reuse | 20% | 25% | 30% | 35% | [new] | [calc] |
| Blocker Rate | 10% | 5% | 0% | 0% | [new] | [calc] |
```

If negative trends detected for 3+ phases, display suggestions.

### Step 6: Update CONSCIENCE.md

- Mark current phase as COMPLETE
- Update phase metrics table
- Add phase to completion history
- Set next phase as CURRENT
- Update progress percentage

### Step 7: Update VISION.md

- Mark phase complete with date
- Update overall progress

### Step 8: Merge Feature Branch

```bash
# If on feature branch
git checkout develop
git merge feature/phase-XX-description
git push origin develop
git branch -d feature/phase-XX-description
```

### Step 9: Create WARRIOR Handoff

Generate phase completion handoff for session continuity:
- What was built
- Key decisions made
- Open blockers carried forward
- Skills extracted
- Next phase context

### Step 10: Route Next Phase

| Condition | Next Action |
|-----------|------------|
| More phases in milestone | `/fire-2-plan` for next phase |
| Milestone complete | `/fire-complete-milestone` |
| User wants to pause | `/fire-5-handoff` |

---

## Success Criteria

- [ ] Phase validated (all plans complete, UAT passed)
- [ ] Metrics collected and aggregated
- [ ] Bottleneck report generated
- [ ] Skills extracted (if candidates found)
- [ ] Trends updated in CONSCIENCE.md
- [ ] Feature branch merged to develop
- [ ] Handoff created for continuity
- [ ] User knows next action

---

## References

- **Metrics:** `@references/metrics-and-trends.md`
- **Skills:** `@references/auto-skill-extraction.md`
- **Blockers:** `@references/blocker-tracking.md`
- **Git:** `@references/git-integration.md`
