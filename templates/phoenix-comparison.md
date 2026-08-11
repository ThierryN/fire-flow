# RESURRECTION-COMPARISON.md — {Project Name}

---
generated_at: "{ISO timestamp}"
generated_by: fire-resurrect
source_path: "{source absolute path}"
target_path: "{target absolute path}"
resurrection_score: "{0-100}%"
verdict: "{APPROVED | CONDITIONAL | REJECTED}"
---

## Side-by-Side Metrics

| Metric | Source (Messy) | Target (Clean) | Change |
|--------|---------------|----------------|--------|
| Total Files | {N} | {N} | {±N} ({±%}) |
| Lines of Code | {N} | {N} | {±N} ({±%}) |
| Avg File Size (LOC) | {N} | {N} | {±N} ({±%}) |
| Max File Size (LOC) | {N} ({filename}) | {N} ({filename}) | {±N} |
| Dependencies (package.json / requirements.txt) | {N} | {N} | {±N} |
| Dev Dependencies | {N} | {N} | {±N} |
| Environment Variables | {N} | {N} | {±N} |
| Test Files | {N} | {N} | {±N} |
| Test Coverage | {N}% | {N}% | {±N}pp |

## Resurrection Verification Checks

| Check | Weight | Score | Details |
|-------|--------|-------|---------|
| PX-1: Feature Parity | 30% | {0-100}% | {N}/{total} INTENT.md features implemented |
| PX-2: Edge Case Coverage | 25% | {0-100}% | {N}/{total} "KEEP" edge cases handled |
| PX-3: Dependency Compatibility | 20% | {0-100}% | {N}/{total} external services connected |
| PX-4: Accidental Complexity Removal | 15% | {0-100}% | {N}/{total} anti-patterns absent from rebuild |
| PX-5: Architecture Improvement | 10% | {0-100}% | File structure, separation, naming |
| **Resurrection Score** | **100%** | **{weighted}%** | **{APPROVED / CONDITIONAL / REJECTED}** |

## Feature Parity Detail (PX-1)

| Feature | Intent | Source Files | Target Files | Status |
|---------|--------|-------------|-------------|--------|
| {feature} | {squint test} | {source files} | {target files} | {IMPLEMENTED / PARTIAL / DROPPED} |

## Anti-Pattern Removal Detail (PX-4)

| Anti-Pattern | Found in Source | Present in Target? | Status |
|-------------|----------------|-------------------|--------|
| {pattern} | {file(s)} | {Yes/No} | {REMOVED / STILL PRESENT} |

## Architecture Comparison (PX-5)

### Source Structure
```
{directory tree excerpt — top 2 levels}
```

### Target Structure
```
{directory tree excerpt — top 2 levels}
```

### Key Improvements
- {improvement 1}
- {improvement 2}
- {improvement 3}

## Items Dropped (User-Approved)

| Feature | Reason for Dropping | Approved In |
|---------|-------------------|-------------|
| {feature} | {reason} | Phase 3 Clarification |

## Verdict

```
Resurrection Score: {score}% — {APPROVED | CONDITIONAL | REJECTED}

  90%+ = APPROVED    — Rebuild is production-ready
  75-89% = CONDITIONAL — Rebuild needs minor fixes before replacing source
  <75% = REJECTED    — Rebuild has significant gaps, review INTENT.md coverage
```
