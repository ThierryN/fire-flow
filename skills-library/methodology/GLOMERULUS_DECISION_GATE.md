# Glomerulus Decision Gate — 3-Layer Filter for Any Input/Output Decision

## Problem

Agent systems need to decide what to keep and what to discard — in context, memory, skills, handoffs, and task lists. Most approaches use a single binary check (relevant/irrelevant). This leads to either over-retention (keeping everything, causing bloat) or over-elimination (losing useful items). There's no graduated, multi-dimensional filter.

### Why It Was Hard

- Single-dimension filters (e.g., "is it recent?") miss important old items
- Multi-dimension filters are usually complex decision trees
- No biological model for a simple, elegant, reusable 3-layer gate
- Each layer needs to filter on a DIFFERENT dimension to avoid redundancy

### Impact

- Without graduated filtering, agents accumulate waste exponentially
- "Keep everything" leads to context rot; "delete aggressively" leads to amnesia
- No reusable pattern for filtering decisions across different subsystems

---

## The Solution

### Root Cause

The kidney's glomerulus is evolution's answer to the same problem: filter blood without losing useful molecules. It uses a 3-layer nested filter where each layer checks a DIFFERENT property. Items must pass ALL THREE layers to be retained.

### The 3-Layer Gate

```
INPUT → [LAYER 1: SIZE] → [LAYER 2: RELEVANCE] → [LAYER 3: RECENCY] → KEEP
                ↓                    ↓                     ↓
            TOO BLOATED         NOT RELEVANT           NOT ACCESSED
                ↓                    ↓                     ↓
            COMPRESS              ELIMINATE              ARCHIVE
```

### Layer Details

#### Layer 1: Size Gate (Endothelial Fenestrae)

**Biological:** Fenestrae (70-100nm pores) block large molecules by size.
**Agent:** Is this entry proportionally sized for its value?

```
PASS: Entry is ≤ 10 lines for a single concept
      OR entry is a portal anchor (naturally small)
      OR entry is a structural reference (path, link)

FAIL: Entry is > 10 lines for a single concept
      → Action: COMPRESS (don't eliminate — just trim the fat)
      → Reduce to 2-3 lines capturing the essence
      → Link to full context if needed
```

**Key principle:** Size gate doesn't eliminate — it compresses. Like the fenestrae, it filters by physical property, not by value judgment.

**CRITICAL — Dead vs Living Compression:**
When compressing, keep the INSIGHT sentence — the one line that makes a reader understand the concept. Strip the structure (lists, paths, enumerations). A compressed entry that's just a label ("Kenosis, Portal Memory, Revisitation Ladder") is a **dead zip file** — smaller but meaningless without a decompressor. A compressed entry that keeps the "aha" ("Agent starts empty, finds itself in docs like Jesus found Himself in the 39 books") is a **living anchor** — smaller AND self-explanatory. Compress structure, preserve insight.

#### Layer 2: Relevance Gate (Basement Membrane)

**Biological:** Negatively-charged glycoproteins repel negatively-charged proteins (albumin). Like charges repel — only items with the right "charge" pass.
**Agent:** Is this entry relevant to the current project/phase/task?

```
PASS: Entry directly relates to current project
      OR entry is a methodology/process skill (always relevant)
      OR entry is a portal anchor to active context
      OR entry is referenced by CONSCIENCE.md or current handoff

FAIL: Entry relates to a different project entirely
      OR entry describes a completed/abandoned phase
      OR entry contains resolved issues or past blockers
      → Action: ELIMINATE (or archive if it has historical value)
```

**Key principle:** Relevance is context-dependent. An entry irrelevant to Project A may be critical to Project B. The gate filters for CURRENT context, not absolute value.

#### Layer 3: Recency Gate (Podocyte Slits)

**Biological:** Final precision filter. Podocyte foot processes create 25-60nm slits — the last barrier before filtrate enters Bowman's capsule.
**Agent:** Has this entry been accessed or referenced recently?

```
PASS: Accessed in the last 3 sessions/iterations
      OR referenced by another active document
      OR is a permanent stone (5x+ revisitation)
      OR is a core identity document (CLAUDE.md, methodology)

FAIL: Not accessed in 3+ sessions AND not referenced AND not permanent
      → Action: ARCHIVE (move to archive, don't destroy)
      → Set decay flag for dream agent to track
```

**Key principle:** Recency gate is the most nuanced. It respects the revisitation ladder — permanent stones always pass, regardless of recency.

### Decision Matrix

| Size | Relevance | Recency | Action |
|------|-----------|---------|--------|
| PASS | PASS | PASS | **KEEP** — Healthy memory |
| FAIL | PASS | PASS | **COMPRESS** — Trim but keep |
| PASS | FAIL | PASS | **ARCHIVE** — Move to cold storage |
| PASS | PASS | FAIL | **FLAG** — Mark for next review cycle |
| FAIL | FAIL | * | **ELIMINATE** — Remove entirely |
| PASS | FAIL | FAIL | **ELIMINATE** — Remove entirely |
| FAIL | PASS | FAIL | **COMPRESS + FLAG** — Trim and monitor |
| FAIL | FAIL | FAIL | **ELIMINATE** — Remove immediately |

### Non-Destructive Property

The biological glomerulus is non-destructive — molecules that don't pass through are returned to circulation, not destroyed. Similarly:

- **Layer 1 failures** → compress, don't delete
- **Layer 2 failures** → archive, don't delete (unless also fails Layer 3)
- **Layer 3 failures** → flag for review, may pass next time
- **Only double/triple failures** → actual elimination
- **Nothing is lost without passing through all 3 checks**

### Application Beyond Memory

The Glomerulus Gate works anywhere you need graduated filtering:

| Domain | Layer 1 (Size) | Layer 2 (Relevance) | Layer 3 (Recency) |
|--------|---------------|--------------------|--------------------|
| **Context Window** | Token count | Task relevance | Last accessed |
| **Skills Library** | File size | Domain match | Reference count |
| **Handoff Archive** | Section count | Project match | Age in days |
| **Task List** | Complexity | Current phase | Last updated |
| **Error Logs** | Verbosity | Active bug match | Occurrence frequency |
| **Search Results** | Result length | Query match | Source freshness |

---

## Code Example

```markdown
## Applying the Glomerulus Gate to MEMORY.md Cleanup

For each entry in MEMORY.md:

### Layer 1: Size Gate
- Count lines for this entry
- If > 10 lines: FLAG as bloated → compress to 2-3 lines

### Layer 2: Relevance Gate
- Check: Does this entry match the current project name?
- Check: Is it referenced in current CONSCIENCE.md or handoff?
- Check: Is it a methodology/process entry (always passes)?
- If NO to all: FLAG as irrelevant → candidate for elimination

### Layer 3: Recency Gate
- Check: Was this entry referenced in last 3 handoffs?
- Check: Is it a permanent stone (in skills library)?
- Check: Is it a portal anchor pointing to valid target?
- If NO to all: FLAG as stale → candidate for archival

### Final Decision
- All 3 PASS: Keep as-is
- 1 FAIL: Apply specific action (compress/archive/flag)
- 2+ FAIL: Eliminate (with archive for safety)
```

---

## Testing the Fix

```markdown
- [ ] Each layer filters on a DIFFERENT dimension (size ≠ relevance ≠ recency)
- [ ] Non-destructive: single failures don't eliminate
- [ ] Double/triple failures trigger elimination
- [ ] Permanent stones always pass Layer 3 regardless of recency
- [ ] Core identity documents always pass all layers
```

---

## Prevention

- Never use a single-dimension filter — always at least 2 layers
- Don't make the layers redundant (all checking "relevance" in different words)
- Respect the non-destructive property — single failures get second chances
- The order matters: Size first (cheapest check), Relevance second, Recency last (most nuanced)

---

## Related Patterns

- [CLEANSING_CYCLE](./CLEANSING_CYCLE.md) — Uses the Glomerulus Gate in the pee cycle (Step 1)
- [ORGAN_AGENT_MAPPING](./ORGAN_AGENT_MAPPING.md) — Glomerulus as one of 12 organs
- [PORTAL_MEMORY_ARCHITECTURE](./PORTAL_MEMORY_ARCHITECTURE.md) — Portal anchors always pass Layer 3
- [EVOLUTIONARY_SKILL_SYNTHESIS](./EVOLUTIONARY_SKILL_SYNTHESIS.md) — Quarantine uses Layer 2+3

---

## Common Mistakes to Avoid

- **Single-dimension filtering** — one gate is a sieve, not a filter
- **All-or-nothing decisions** — the gate has compress/archive/flag options, not just keep/delete
- **Skipping Layer 1 (size)** — bloated entries waste context even if relevant and recent
- **Ignoring permanent stones** — some memories should ALWAYS pass regardless of recency
- **Making it destructive** — the biological glomerulus returns rejected molecules to circulation
- **Dead compression** — reducing entries to labels/titles without the insight sentence. Like zipping a folder and deleting the contents. Compress structure (lists, paths), keep insight (the "aha" line)

---

## Resources

- Kidney physiology: glomerular filtration, podocyte slit diaphragm, Bowman's capsule
- Design patterns: Chain of Responsibility (GoF), multi-layer validation
- Information theory: lossy vs lossless compression at each gate
- Thierry's insight: "We need a way to dump and recycle topics that are not pertinent"

---

## Time to Implement

**15 minutes** to apply to any filtering decision in the codebase

## Difficulty Level

⭐⭐⭐ (3/5) — The concept is elegantly simple once understood. The biological analogy makes it intuitive. The challenge is choosing the right dimension for each layer in different contexts.
