# Auto-Skill Extraction System

## Overview

Automatically detects novel patterns from completed work and prompts for skill library contribution. Triggers after phase transitions and plan completions.

## How It Works

### Trigger Points

1. **After `/fire-transition`** — Scans all RECORD.md files from completed phase
2. **After `/fire-4-verify` PASSED** — Scans verification report for novel patterns
3. **After `/fire-5-handoff`** — Scans handoff for skills_applied and new patterns

### Detection Patterns

The system scans for these signals in RECORD.md and handoff files:

```markdown
## Signal 1: Explicit Skill Markers
Look for: /* SKILL: name */ ... /* END SKILL */
Action: Extract marked block, prompt to save as skill

## Signal 2: Honesty Checkpoints with Research
Look for: "Research Conducted:", "Resolution:", "Confidence After Research: High"
Action: The gap + resolution combo is a potential skill

## Signal 3: Novel Decisions
Look for: "Decision:" or "Assumption:" with "Rationale:"
Action: Decision patterns that could help future phases

## Signal 4: Repeated Patterns
Look for: Same file modification pattern across 2+ plans
Action: Recurring pattern = candidate for abstraction into skill

## Signal 5: Bug Fix Patterns
Look for: "Root Cause:", "Fix:", "Prevention:"
Action: Bug patterns with prevention strategies = high-value skills
```

### Extraction Process

```
1. SCAN completed work artifacts (RECORD.md, handoff, verification)
2. DETECT skill candidates using patterns above
3. CLASSIFY by category:
   - database-solutions/
   - patterns-standards/
   - deployment-security/
   - integrations/
   - video-media/
   - ecommerce/
   - form-solutions/
   - advanced-features/
   - automation/
   - document-processing/
   - methodology/
   - [new: react/, nodejs/, postgresql/, stripe/]
4. PROMPT user:
   "Detected potential skill: [name]
    Category: [category]
    Source: [file:lines]
    Save to skills library? (y/n/edit)"
5. If yes: Write skill file using standard template
6. UPDATE skills-library/SKILLS_LIBRARY_INDEX.md
```

### Skill File Template

```markdown
# [Skill Name]

**Category:** [category]
**Difficulty:** [1-5 stars]
**Date Added:** [auto]
**Source:** [phase/plan that generated it]

## Problem
[What problem this solves]

## Why It's Difficult
[Why this isn't obvious]

## Solution
[Complete solution with code examples]

## Before/After
```code
// Before (broken/inefficient)
[code]

// After (fixed/optimized)
[code]
```

## Prevention
[How to avoid this problem in future]

## Testing
[How to verify the fix works]
```

### Integration with .claude Init

The auto-extraction is referenced in Dominion Flow's session hooks. When a phase completes:

1. Dominion Flow `/fire-transition` command includes extraction step
2. The transition workflow scans artifacts
3. Detected skills are presented to user
4. Approved skills are written to library
5. SKILLS_LIBRARY_INDEX.md is updated

No external hooks needed — it's built into the workflow commands themselves.

### Configuration

In project `.planning/config.json`:
```json
{
  "auto_skill_extraction": {
    "enabled": true,
    "auto_prompt": true,
    "min_confidence": "medium",
    "categories_enabled": "all",
    "skip_patterns": ["console.log", "TODO", "FIXME"]
  }
}
```

### Manual Trigger

```
/fire-search --extract-from .planning/phases/[phase]/
```

Scans a specific phase directory for skill candidates.
