# Path Verification Gate — Mandatory Wrong-Repo Circuit Breaker

## The Problem

In multi-project sessions (or when working directories have similar names), subagents can
operate on the wrong repository. This is a **silent, catastrophic failure** — the subagent
reads wrong files, proposes wrong fixes, and potentially modifies the wrong codebase. The
parent agent has no way to detect this after the fact because the subagent returns plausible-
looking results from the wrong project.

### Real Incident

A subagent was tasked with exploring `MINISTRY-LMS` plugin structure but instead explored
`my-other-project` (a different project in the same repos directory). The agent returned
detailed analysis of the wrong codebase. The error was only caught because the parent agent
noticed unfamiliar file paths in the results.

### Why It Was Hard

- Subagents inherit the parent's working directory, but path resolution can drift
- Similar project names (`MINISTRY-LMS` vs `my-other-project`) create confusion
- Subagent results look plausible even from the wrong repo (both are MERN stacks)
- No built-in path constraint mechanism in the subagent protocol
- Detection is post-hoc — by the time you notice, context has been wasted

### Impact

- Wrong analysis fed into planning decisions
- Wasted context window on irrelevant exploration
- Potential for destructive operations (deletion, modification) on wrong project
- Undermines trust in subagent results (which degrades the entire swarm pattern)

---

## The Solution

### Root Cause

Subagents receive a task prompt but no explicit path boundary. When the working directory
contains multiple similar projects, the agent's search/glob patterns can match files in
sibling directories. There is no "fence" preventing cross-project contamination.

### The Path Verification Gate

A **MANDATORY** (non-overridable) check that runs before any file operation:

```markdown
### Step 3.5: Path Verification Gate (MANDATORY — v5.0)

Before ANY file operation, verify these HARD GATES (no confidence override):

1. WORKING DIRECTORY CHECK
   expected_project = extract from CONSCIENCE.md or VISION.md or user context
   actual_cwd = pwd
   IF actual_cwd does NOT contain expected_project path:
     → HARD STOP: "Wrong directory. Expected {expected}, got {actual_cwd}."
     → Do NOT proceed. Do NOT create files. Do NOT modify anything.

2. SUBAGENT PATH INJECTION
   When spawning ANY subagent (Task tool), ALWAYS include:
   <path_constraint>
   PROJECT_ROOT: {absolute path to current project}
   ALLOWED_PATHS: {PROJECT_ROOT}/**
   FORBIDDEN: Do NOT read, write, or search files outside PROJECT_ROOT.
   If you discover you are in the wrong directory, STOP and report.
   </path_constraint>

3. DELETION SAFETY
   Before deleting files:
   - Count planned deletions vs actual files found
   - If count mismatch > 0: STOP and report discrepancy
   - Verify each path starts with PROJECT_ROOT
   - Check against a keep-list of protected files

4. CROSS-PROJECT CONTAMINATION CHECK
   In sessions with multiple working directories:
   - Explicitly name the TARGET project in every tool call description
   - Verify glob/grep results all share the same project root
   - If results span multiple projects: STOP and filter
```

### Key Design Principle

**This gate is a circuit breaker, NOT a confidence check.**

Confidence gates (from Upgrade 6) allow override at HIGH confidence. Path verification
does NOT. A 100% confident agent operating on the wrong repo is 100% wrong. The gate is
binary: right path = proceed, wrong path = stop.

### Code Example — Subagent Spawn

**Before (No Path Constraint):**
```markdown
Task(
  prompt="Explore plugin structure in server/plugins/installed/",
  subagent_type="Explore",
  description="Explore plugin files"
)
```

**After (With Path Constraint):**
```markdown
Task(
  prompt="""
  <path_constraint>
  PROJECT_ROOT: C:\path\to\your-project
  ALLOWED_PATHS: C:\path\to\your-project\**
  FORBIDDEN: Do NOT access files outside MINISTRY-LMS.
  </path_constraint>

  Explore plugin structure in server/plugins/installed/
  All file paths MUST start with C:\path\to\your-project
  """,
  subagent_type="Explore",
  description="Explore MINISTRY-LMS plugin files"
)
```

### Implementation Locations

| Command | Location | What It Protects |
|---------|----------|-----------------|
| `fire-3-execute.md` | Step 3.5 | All plan execution (file creation, modification, deletion) |
| `fire-debug.md` | Steps 4 + 6 | Debug subagent spawns (investigation + continuation) |
| `fire-loop.md` | Step 0.5 | Loop file creation and all iteration work |

---

## Testing the Fix

### Before
```
Subagent spawned → explores whatever directory it finds
Returns results from wrong project → accepted as correct
Parent agent builds on wrong foundation → cascading errors
Detection: NONE until human notices wrong file paths
```

### After
```
Subagent spawned with <path_constraint> block
Subagent checks PROJECT_ROOT before any file operation
Wrong directory detected → immediate STOP + report
Parent agent receives clear error instead of wrong results
Detection: IMMEDIATE at point of divergence
```

### Test Cases
```
1. Spawn subagent in multi-project session
   → Subagent should only access files under PROJECT_ROOT
   → Glob results outside PROJECT_ROOT should trigger STOP

2. Attempt file deletion with count mismatch
   → Plan says "delete 28 files", only 27 found
   → Gate STOPS and reports: "Expected 28, found 27. Missing: X"

3. Session with similar project names
   → MINISTRY-LMS vs my-other-project
   → All operations explicitly name target project
   → Grep results filtered to single project root
```

---

## Prevention

1. **Always inject `<path_constraint>`** into every subagent spawn prompt
2. **Always include project name** in Task description field (not just the prompt)
3. **Use absolute paths** in all file operations — never relative paths that could resolve elsewhere
4. **Count before deleting** — verify planned count matches actual count
5. **Name the project explicitly** in multi-directory sessions

---

## Related Patterns

- [Confidence-Gated Execution](./CONFIDENCE_GATED_EXECUTION.md) — Confidence gates for non-path decisions
- [Evidence-Based Validation](./EVIDENCE_BASED_VALIDATION.md) — Verify results against expectations
- [Advanced Orchestration Patterns](./ADVANCED_ORCHESTRATION_PATTERNS.md) — Subagent management

## Common Mistakes to Avoid

- Don't make path verification confidence-overridable (100% confident + wrong repo = disaster)
- Don't assume subagents inherit the right context (they inherit cwd but not intent)
- Don't skip the gate for "simple" operations (simple operations in the wrong repo are still wrong)
- Don't use relative paths in multi-project sessions (they resolve unpredictably)

---

## Resources

- SDFT paper insight: "Recovery from own errors > memorizing expert paths" — the wrong-repo incident
  IS the error. The gate IS the recovery mechanism.
- MINISTRY-LMS modular refactoring: the real incident that triggered this skill's creation

## Time to Implement

**30 minutes** — add `<path_constraint>` block to all subagent spawn templates

## Difficulty Level

2/5 — Simple to implement once you know it's needed. The hard part was experiencing the failure.

---

**Author Notes:**
This skill exists because a subagent explored the wrong repository and returned plausible results.
The lesson: subagents are powerful but directionless. They'll happily explore any directory you
point them at — or that they THINK you pointed them at. The path constraint block is cheap insurance
against an expensive failure mode. Make it mandatory. No exceptions. No confidence override.
