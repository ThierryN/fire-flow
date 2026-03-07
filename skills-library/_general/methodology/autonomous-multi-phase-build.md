---
name: autonomous-multi-phase-build
category: methodology
version: 2.0.0
contributed: 2026-02-26
contributor: scribe-bible
last_updated: 2026-02-26
tags: [autonomous, build, multi-phase, workflow, automation, verification, CI]
difficulty: hard
usage_count: 0
success_rate: 100
---

# Autonomous Multi-Phase Build Pipeline

## Problem

You have a multi-phase feature build (3-10 phases) where each phase creates new files, modifies existing ones, and must pass TypeScript compilation + production build before advancing. Manual execution requires constant human attention for plan→execute→verify→fix→advance cycles. Failed builds mid-pipeline waste time if earlier phases introduced issues that compound.

## Solution Pattern

Structure each phase as an **atomic unit** with a strict contract: plan what to create/modify, execute the changes, verify with `tsc --noEmit` + `vite build` (or your build tool), fix any errors automatically, then advance. Track phase status in a conscience/state file so the pipeline can resume from any point.

The key insight: **verify after every phase, not at the end**. A TypeScript error in Phase 1 that goes undetected until Phase 5 requires debugging across 5 phases of changes. Catching it immediately constrains the fix to the current phase's changes.

## Code Example

```markdown
<!-- .planning/CONSCIENCE.md — Phase status tracker -->
| Phase | Name | Status | Attempts | Notes |
|-------|------|--------|----------|-------|
| 1 | Auth System | complete | 1 | 3 files created, 2 modified |
| 2 | Dashboard | complete | 2 | Type error on attempt 1, fixed |
| 3 | API Layer | in-progress | 0 | |
| 4 | Real-time | pending | 0 | |
```

```typescript
// Phase execution contract (pseudocode)
interface PhaseContract {
  // What this phase will do
  creates: string[];      // New files
  modifies: string[];     // Existing files changed
  depends: string[];      // Files from earlier phases

  // Verification
  typeCheck: () => boolean;   // tsc --noEmit
  buildCheck: () => boolean;  // vite build / next build / etc.

  // Recovery
  maxAttempts: number;        // Usually 3
  onFailure: 'fix' | 'replan' | 'escalate';
}
```

```bash
# Verification commands run after each phase
# Phase N complete → verify immediately
npx tsc --noEmit                    # Type safety
npx vite build 2>&1 | tail -20     # Production build
echo $?                             # 0 = pass, non-zero = fail
```

## Implementation Steps

1. **Define phases** in a VISION/roadmap document with clear deliverables per phase
2. **Create phase directories** with context files (what to build, key decisions, API contracts)
3. **For each phase:**
   a. Read phase context + understand what previous phases created
   b. Create/modify files according to the phase plan
   c. Run `tsc --noEmit` — fix any type errors immediately
   d. Run production build — fix any build errors
   e. Update status tracker (CONSCIENCE.md or equivalent)
   f. If build passes: advance to next phase
   g. If build fails after max attempts: stop and report
4. **Write session log** with per-phase results, files created/modified, errors fixed

## Verification Pattern

The critical verification loop per phase:

```
EXECUTE phase changes
  ↓
RUN tsc --noEmit
  ↓ FAIL? → identify error → fix → re-run tsc
  ↓ PASS
RUN vite build (or equivalent)
  ↓ FAIL? → identify error → fix → re-run build
  ↓ PASS
UPDATE status tracker
ADVANCE to next phase
```

Common TypeScript errors to fix automatically:
- **TS6133**: Unused imports → remove them
- **TS2345**: Type mismatch on state hooks → add explicit type parameter (`useState<any>()`)
- **TS2353**: Invalid CSS property in style object → use correct property name
- **TS6192**: All imports unused → remove entire import statement

## When to Use

- Multi-phase feature builds (3+ phases with interdependencies)
- Autonomous/unattended build sessions
- When each phase must be independently verifiable
- Projects with strict TypeScript / build requirements
- When you want resumable progress (interrupted session can continue from last complete phase)

## When NOT to Use

- Single-file changes or bug fixes (overhead isn't justified)
- Exploratory/prototyping work where the plan isn't clear
- When phases have circular dependencies (must restructure first)
- Projects without automated build verification (no TypeScript, no bundler)

## Common Mistakes

- Skipping verification between phases ("I'll check at the end") — errors compound
- Not tracking which files each phase created/modified — makes debugging harder
- Attempting too many phases without committing — risk of losing work
- Not reading what previous phases built before starting the next — causes conflicts
- Setting maxAttempts too high (>3) — if 3 fix attempts fail, the approach is wrong

## Related Skills

- [react-flow-animated-layout-switching](../_general/frontend/react-flow-animated-layout-switching.md) — Technique used in Phase 1
- [domain-specific-layout-algorithms](../_general/patterns-standards/domain-specific-layout-algorithms.md) — Pattern used in Phases 1 & 3

## References

- Dominion Flow `/fire-autonomous` command — full implementation of this pattern
- Proven in: scribe-bible "Psalms Visual Intelligence" milestone — 5 phases, 8 files created, 6 modified, all clean first attempt
- Key metrics: 0 regressions across phases, every type error caught and fixed within the phase that introduced it
