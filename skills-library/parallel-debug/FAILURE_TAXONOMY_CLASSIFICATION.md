---
name: failure-taxonomy-classification
category: parallel-debug
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [debugging, taxonomy, classification, failure-patterns, agentdebug]
difficulty: medium
---

# Failure Taxonomy Classification

## Problem

Debugging without classification leads to random investigation. Knowing the TYPE of failure immediately narrows the search space. A MEMORY failure needs different tools than a SYSTEM failure.

## Solution Pattern

Classify every failure into one of 5 categories from the AgentDebug taxonomy (2025). Each category has specific investigation steps and common root causes.

## The 5 Categories

### MEMORY — Agent forgets context
**Symptoms:**
- Repeats work already done
- Ignores previous findings
- Contradicts earlier decisions
- Loses track of file changes

**Investigation:**
- Check if context was compacted
- Look for conversation length > 100 turns
- Verify key files are in context window
- Check if WARRIOR handoff was read

**Common fixes:** Re-read handoff, use `/compact Focus on {topic}`, pin critical context

### REFLECTION — Agent doesn't learn from failures
**Symptoms:**
- Same error 3+ times in a row
- Applies same fix that already failed
- Doesn't adjust approach after failure
- Ignores test output

**Investigation:**
- Search debug history for this error pattern
- Check if behavioral directives exist for this pattern
- Verify error output is being read

**Common fixes:** Add behavioral directive (IF/THEN/BECAUSE), record failure pattern to Qdrant

### PLANNING — Wrong approach chosen
**Symptoms:**
- Editing wrong file
- Using wrong API/library
- Building wrong feature
- Missing requirements

**Investigation:**
- Re-read REQUIREMENTS.md or BLUEPRINT.md
- Check CONSCIENCE.md for project rules
- Verify understanding of the task

**Common fixes:** Re-plan with `/fire-2-plan`, check skills library for correct patterns

### ACTION — Correct plan, bad execution
**Symptoms:**
- Typos in code
- Wrong parameters
- Incomplete implementation
- Tests fail on edge cases

**Investigation:**
- Diff the actual code against the plan
- Check for copy-paste errors
- Verify API signatures match documentation

**Common fixes:** Fix the specific error, add test for the edge case

### SYSTEM — External failure
**Symptoms:**
- Database connection refused
- API rate limit hit
- Build tool crash
- Disk full, port in use

**Investigation:**
- Check if service is running
- Verify environment variables
- Check system resources (disk, memory, ports)

**Common fixes:** Restart service, rotate credentials, clear disk space, kill port-holding process

## Classification Flow

```
Error occurs
  → Can you reproduce it?
    No → SYSTEM (intermittent external issue)
    Yes → Has this exact error happened before?
      Yes → REFLECTION (not learning from past)
      No → Is the approach correct?
        No → PLANNING (wrong approach)
        Yes → Is the code correct?
          No → ACTION (execution error)
          Yes → Is context missing?
            Yes → MEMORY (lost context)
            No → SYSTEM (environment issue)
```

## When to Use
- First step of ANY debug session
- Before spawning parallel debug agents
- When recording failures to Qdrant

## When NOT to Use
- Not applicable — always classify before debugging
