---
description: AI-powered pattern discovery and skill suggestions
---

# /fire-discover

> AI-powered pattern discovery and skill suggestion engine

---

## Purpose

Analyze completed work to detect recurring patterns, problem-solving approaches, and common solutions that could become reusable skills. Automatically suggests creating new skills or updating existing ones based on observed patterns. Helps compound knowledge across projects.

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--phase [N]` | No | Analyze specific phase (default: most recent completed) |
| `--weekly` | No | Generate weekly pattern summary |
| `--auto` | No | Non-interactive mode, auto-defer all suggestions |
| `--depth [level]` | No | Analysis depth: `shallow`, `normal`, `deep` (default: normal) |
| `--export [format]` | No | Export findings as `md` or `json` |

---

## Process

### Step 1: Gather Analysis Data

Collect data from completed work.

```bash
# Data sources for pattern detection
SUMMARIES=".planning/phases/*/RECORD.md"
COMMITS=$(git log --oneline --since="7 days ago")
CHANGED_FILES=$(git diff --stat HEAD~20..HEAD)
CODE_COMMENTS=$(grep -r "// tricky\|// hard\|// discovered\|// pattern" src/)
```

Sources analyzed:
- **RECORD.md files** - Skills applied, problems solved, decisions made
- **Git commits** - Commit messages indicating patterns or solutions
- **Code comments** - Developer annotations about non-obvious solutions
- **File changes** - Structural patterns in code organization
- **Test files** - Testing patterns and edge cases handled

### Step 2: Pattern Detection

Identify recurring patterns using multiple detection methods.

```
Detection Methods:

1. Code Pattern Analysis (via AST concepts)
   - Function signatures that repeat
   - Similar error handling approaches
   - Common utility patterns
   - Component structure templates

2. Problem-Solving Approaches (from commits)
   - "fix:" commits that address similar issues
   - Refactoring patterns that repeat
   - Performance optimization techniques
   - Security hardening approaches

3. Frequency Analysis
   - Code snippets that appear 3+ times
   - Similar file structures
   - Repeated import patterns
   - Common configuration shapes
```

### Step 3: Generate Suggestions

Create actionable suggestions for skill creation or updates.

```
Suggestion Types:

1. NEW SKILL - Pattern not in library
   - Generate skill document template
   - Pre-fill with detected examples
   - Suggest category placement

2. UPDATE SKILL - Variation of existing skill
   - Identify which skill to update
   - Show differences/improvements
   - Propose merged content

3. COMPOUND SKILL - Skills frequently used together
   - Identify co-occurring skills
   - Suggest bundled workflow skill
   - Document integration points
```

### Step 4: Display Discoveries

#### Default Mode (Interactive)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                           POWER ► DISCOVER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◆ Analyzing Phase 3 patterns...
  ├─ ✓ Loaded 6 RECORD.md files
  ├─ ✓ Analyzed 24 commits
  ├─ ✓ Scanned 156 changed files
  ├─ ✓ Found 8 annotated code patterns
  └─ ✓ Pattern detection complete

╔══════════════════════════════════════════════════════════════════════════════╗
║                         PATTERN DISCOVERIES                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Patterns Detected:     5                                                   ║
║  New Skill Candidates:  2                                                   ║
║  Skill Updates:         2                                                   ║
║  Compound Skills:       1                                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ DISCOVERY #1: NEW SKILL CANDIDATE                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Pattern: Retry with Exponential Backoff                                   │
│  Category: api-patterns                                                     │
│  Confidence: HIGH (found in 5 locations)                                   │
│                                                                             │
│  Evidence:                                                                  │
│  ├─ server/services/embedding.service.ts:45-67                             │
│  ├─ server/services/rag.service.ts:112-134                                 │
│  ├─ server/services/youtube.service.ts:78-95                               │
│  ├─ server/routes/chat.ts:156-178                                          │
│  └─ Commit: "feat: add retry logic to API calls"                           │
│                                                                             │
│  Detected Pattern:                                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ async function withRetry<T>(                                         │  │
│  │   fn: () => Promise<T>,                                              │  │
│  │   maxAttempts = 3,                                                   │  │
│  │   baseDelay = 1000                                                   │  │
│  │ ): Promise<T> {                                                      │  │
│  │   for (let attempt = 1; attempt <= maxAttempts; attempt++) {         │  │
│  │     try {                                                            │  │
│  │       return await fn();                                             │  │
│  │     } catch (error) {                                                │  │
│  │       if (attempt === maxAttempts) throw error;                      │  │
│  │       await sleep(baseDelay * Math.pow(2, attempt - 1));             │  │
│  │     }                                                                │  │
│  │   }                                                                  │  │
│  │ }                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  No existing skill matches this pattern.                                   │
│                                                                             │
│  Actions:                                                                  │
│    [C] Create skill: api-patterns/retry-exponential-backoff               │
│    [D] Defer (add to backlog)                                             │
│    [I] Ignore (not worth capturing)                                       │
│                                                                             │
│  Your choice: _                                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ DISCOVERY #2: NEW SKILL CANDIDATE                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Pattern: Prisma Transaction with Rollback                                 │
│  Category: database-solutions                                              │
│  Confidence: MEDIUM (found in 3 locations)                                 │
│                                                                             │
│  Evidence:                                                                  │
│  ├─ server/services/discovery.service.ts:234-267                           │
│  ├─ server/services/embedding.service.ts:189-215                           │
│  └─ server/scripts/ingest-kjv.ts:145-178                                   │
│                                                                             │
│  Detected Pattern:                                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ await prisma.$transaction(async (tx) => {                            │  │
│  │   // Atomic operations                                               │  │
│  │   const result = await tx.model.create({ ... });                     │  │
│  │   await tx.related.createMany({ ... });                              │  │
│  │   // Auto-rollback on any error                                      │  │
│  │   return result;                                                     │  │
│  │ }, {                                                                 │  │
│  │   maxWait: 5000,                                                     │  │
│  │   timeout: 10000,                                                    │  │
│  │   isolationLevel: 'Serializable'                                     │  │
│  │ });                                                                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Similar to: database-solutions/transactions (but Prisma-specific)        │
│                                                                             │
│  Actions:                                                                  │
│    [C] Create skill: database-solutions/prisma-transactions               │
│    [U] Update existing: database-solutions/transactions                   │
│    [D] Defer (add to backlog)                                             │
│    [I] Ignore                                                             │
│                                                                             │
│  Your choice: _                                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ DISCOVERY #3: SKILL UPDATE SUGGESTION                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Pattern: Enhanced N+1 with Batch Loading                                  │
│  Existing Skill: database-solutions/n-plus-1                               │
│  Confidence: HIGH (improvement detected)                                   │
│                                                                             │
│  Current Skill Covers:                                                     │
│  ├─ Prisma includes for eager loading                                      │
│  └─ Basic N+1 detection                                                    │
│                                                                             │
│  Detected Enhancement:                                                     │
│  ├─ DataLoader pattern for batch loading                                   │
│  ├─ Cursor-based pagination with N+1 prevention                            │
│  └─ Conditional includes based on query params                             │
│                                                                             │
│  Example Addition:                                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ // DataLoader pattern for batching                                   │  │
│  │ const userLoader = new DataLoader(async (ids) => {                   │  │
│  │   const users = await prisma.user.findMany({                         │  │
│  │     where: { id: { in: ids } }                                       │  │
│  │   });                                                                │  │
│  │   return ids.map(id => users.find(u => u.id === id));               │  │
│  │ });                                                                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Actions:                                                                  │
│    [U] Update skill: database-solutions/n-plus-1                          │
│    [C] Create new: database-solutions/dataloader-batching                 │
│    [D] Defer                                                              │
│    [I] Ignore                                                             │
│                                                                             │
│  Your choice: _                                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ DISCOVERY #4: SKILL UPDATE SUGGESTION                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Pattern: Streaming Response Handling                                      │
│  Existing Skill: api-patterns/streaming                                    │
│  Confidence: MEDIUM (partial match)                                        │
│                                                                             │
│  Your Implementation:                                                      │
│  ├─ Server-Sent Events for LLM responses                                   │
│  ├─ Backpressure handling                                                  │
│  └─ Client reconnection logic                                              │
│                                                                             │
│  Differs From Existing:                                                    │
│  ├─ Uses SSE instead of WebSocket                                          │
│  ├─ Specific to AI/LLM streaming                                           │
│  └─ Includes citation extraction mid-stream                                │
│                                                                             │
│  Actions:                                                                  │
│    [U] Update skill: api-patterns/streaming                               │
│    [C] Create new: api-patterns/llm-streaming                             │
│    [D] Defer                                                              │
│    [I] Ignore                                                             │
│                                                                             │
│  Your choice: _                                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ DISCOVERY #5: COMPOUND SKILL SUGGESTION                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Pattern: Skills Frequently Used Together                                  │
│  Skills: n-plus-1 + indexing + query-optimization                         │
│  Co-occurrence Rate: 85%                                                   │
│                                                                             │
│  Observation:                                                              │
│  These three skills are almost always applied together when optimizing    │
│  database performance. Consider bundling into a compound skill.            │
│                                                                             │
│  Proposed Compound Skill:                                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Name: database-solutions/query-performance-bundle                    │  │
│  │                                                                      │  │
│  │ Includes:                                                            │  │
│  │ 1. N+1 detection and prevention                                      │  │
│  │ 2. Strategic index creation                                          │  │
│  │ 3. Query analysis with EXPLAIN                                       │  │
│  │                                                                      │  │
│  │ Workflow:                                                            │  │
│  │ 1. Run query analysis → identify slow queries                        │  │
│  │ 2. Check for N+1 patterns → add eager loading                        │  │
│  │ 3. Add indexes for remaining bottlenecks                             │  │
│  │ 4. Verify with EXPLAIN ANALYZE                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Actions:                                                                  │
│    [C] Create compound skill                                              │
│    [D] Defer                                                              │
│    [I] Ignore (prefer individual skills)                                  │
│                                                                             │
│  Your choice: _                                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

╔══════════════════════════════════════════════════════════════════════════════╗
║                           DISCOVERY SUMMARY                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Patterns Analyzed:     5                                                   ║
║  Skills Created:        [based on choices]                                  ║
║  Skills Updated:        [based on choices]                                  ║
║  Deferred:              [based on choices]                                  ║
║  Ignored:               [based on choices]                                  ║
║                                                                              ║
║  Knowledge Compounding: Your skills library grew by X skills this session  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

#### Weekly Summary Mode (`--weekly`)

```
━━━ POWER ► DISCOVER: WEEKLY SUMMARY ━━━

╔══════════════════════════════════════════════════════════════════════════════╗
║                    WEEKLY PATTERN SUMMARY                                     ║
║                    2026-01-15 to 2026-01-22                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Phases Completed:      2 (Phase 2, Phase 3)                                ║
║  Commits Analyzed:      47                                                  ║
║  Files Changed:         156                                                 ║
║  Patterns Detected:     8                                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ TOP PATTERNS THIS WEEK                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Retry with Exponential Backoff         5 occurrences   → NEW SKILL     │
│  2. Prisma Transaction Patterns            4 occurrences   → NEW SKILL     │
│  3. Streaming Response Handling            3 occurrences   → UPDATE SKILL  │
│  4. Error Boundary with Recovery           3 occurrences   → REVIEW        │
│  5. Type-safe API Responses                2 occurrences   → REVIEW        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ SKILLS LIBRARY CHANGES                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Created This Week:                                                        │
│  ├─ + api-patterns/retry-exponential-backoff                               │
│  └─ + database-solutions/prisma-transactions                               │
│                                                                             │
│  Updated This Week:                                                        │
│  └─ ~ database-solutions/n-plus-1 (added DataLoader patterns)             │
│                                                                             │
│  Deferred (in backlog):                                                    │
│  ├─ api-patterns/llm-streaming                                             │
│  └─ database-solutions/query-performance-bundle                            │
│                                                                             │
│  Library Growth: +2 skills, +1 update                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ KNOWLEDGE COMPOUNDING METRICS                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Skills Applied:        12 this week                                       │
│  Skills Created:         2 from discoveries                                │
│  Reuse Rate:            4.2x (skills applied per unique skill)            │
│  Time Saved:            ~9 hours                                           │
│                                                                             │
│  Trend: ████████████████████░░░░░░░░░░░░ Knowledge growing +15%/week      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ NEXT WEEK RECOMMENDATIONS                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Based on upcoming Phase 4 (Greek/Hebrew Tools):                           │
│                                                                             │
│  ○ Review deferred patterns before Phase 4 starts                          │
│  ○ Consider creating i18n/unicode skills for Hebrew handling              │
│  ○ Search for existing NLP/text-processing skills                         │
│                                                                             │
│  Run: /fire-search "unicode text processing" for relevant skills         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Auto Mode (`--auto`)

Non-interactive mode that defers all suggestions for later review:

```
━━━ POWER ► DISCOVER (Auto Mode) ━━━

◆ Analyzing patterns...
  ├─ ✓ Detected 5 patterns
  ├─ ✓ All suggestions deferred to backlog
  └─ ✓ Summary saved to .planning/discoveries/2026-01-22.md

Deferred Suggestions:
  1. api-patterns/retry-exponential-backoff (NEW)
  2. database-solutions/prisma-transactions (NEW)
  3. database-solutions/n-plus-1 (UPDATE)
  4. api-patterns/streaming (UPDATE)
  5. database-solutions/query-performance-bundle (COMPOUND)

Run /fire-discover without --auto to review interactively.
```

---

## Pattern Detection Algorithms

### Code Pattern Detection

```
1. Function Signature Analysis
   - Extract function signatures from changed files
   - Group by parameter patterns
   - Identify >3 occurrences with similar structure

2. Import Pattern Analysis
   - Track commonly imported modules
   - Identify utility functions that repeat
   - Flag candidates for extraction

3. Error Handling Patterns
   - Detect try/catch blocks with similar structure
   - Identify common error recovery patterns
   - Note retry/fallback implementations
```

### Commit Message Analysis

```
Keywords that indicate patterns:
- "fix:" repeated fixes for same issue type
- "refactor:" indicates pattern improvement
- "feat:" with similar descriptions
- "perf:" performance patterns
- Comments: "tricky", "hard", "discovered", "pattern"
```

### Complexity Indicators

Patterns worth capturing often have:
- Multiple failed attempts before success (from git history)
- Research queries to external sources (from RECORD.md)
- Code refactoring iterations
- Test failures before passing
- Long implementation duration (>30 minutes)

---

## Interactive Actions

### Create Skill [C]

Launches `/fire-contribute` with pre-filled data:

```
◆ Creating skill: api-patterns/retry-exponential-backoff

Pre-filled from discovery:
├─ Category: api-patterns
├─ Name: retry-exponential-backoff
├─ Problem: API calls fail intermittently, need resilient retry logic
├─ Solution: Exponential backoff with configurable attempts
└─ Examples: [extracted from codebase]

Launching /fire-contribute...
```

### Update Skill [U]

Shows diff and confirms update:

```
◆ Updating skill: database-solutions/n-plus-1

Changes to add:
├─ + DataLoader batching pattern section
├─ + Cursor-based pagination example
└─ + Conditional includes pattern

View full diff? [y/N]: _
Proceed with update? [Y/n]: _
```

### Defer [D]

Adds to discovery backlog for later review:

```
◆ Deferred: api-patterns/retry-exponential-backoff

Added to: .planning/discoveries/backlog.md

Backlog now contains 3 deferred patterns.
Review with: /fire-discover --backlog
```

### Ignore [I]

Marks pattern as not worth capturing:

```
◆ Ignored: [pattern description]

This pattern will not be suggested again unless significantly changed.
```

---

## Discovery Schedule

Pattern discovery runs:
1. **After phase completion** - Automatic trigger via `/fire-4-verify`
2. **Weekly summary** - Manual via `/fire-discover --weekly`
3. **On demand** - Manual via `/fire-discover`

---

## Output Files

### Discovery Log

`.planning/discoveries/YYYY-MM-DD.md`:

```markdown
# Discovery Log: 2026-01-22

## Patterns Detected

### Pattern 1: Retry with Exponential Backoff
- Confidence: HIGH
- Locations: [list]
- Action: CREATED as api-patterns/retry-exponential-backoff

### Pattern 2: Prisma Transactions
- Confidence: MEDIUM
- Locations: [list]
- Action: DEFERRED

## Summary
- Patterns: 5
- Created: 1
- Updated: 0
- Deferred: 3
- Ignored: 1
```

### Backlog

`.planning/discoveries/backlog.md`:

```markdown
# Discovery Backlog

## Pending Review

### api-patterns/llm-streaming
- Detected: 2026-01-22
- Confidence: MEDIUM
- Status: Deferred (needs more examples)

### database-solutions/query-performance-bundle
- Detected: 2026-01-22
- Confidence: HIGH
- Status: Deferred (compound skill - needs review)
```

---

## Success Criteria

- [ ] Pattern detection finds genuine recurring patterns
- [ ] Confidence scores reflect actual pattern frequency
- [ ] Interactive prompts work correctly
- [ ] Create action launches /fire-contribute with correct data
- [ ] Update action shows meaningful diff
- [ ] Defer action properly updates backlog
- [ ] Weekly summary aggregates data correctly
- [ ] Auto mode non-interactively defers all patterns
- [ ] Discovery log files are created and formatted correctly

---

## Related Commands

- `/fire-contribute` - Create new skills
- `/fire-analytics` - View skills usage statistics
- `/fire-search` - Search existing skills
- `/fire-4-verify` - Triggers discovery after phase completion

---

*Discovery compounds knowledge. Run /fire-discover --weekly to track pattern growth over time.*
