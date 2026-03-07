---
name: llm-judge-memory-crud
category: methodology
version: 1.0.0
contributed: 2026-02-25
contributor: your-memory-repo
last_updated: 2026-02-25
contributors:
  - your-memory-repo
tags: [qdrant, vector-db, memory, crud, mem0, llm, lifecycle, dedup]
difficulty: medium
usage_count: 0
success_rate: 100
---

# LLM-as-Judge Memory CRUD Pipeline

## Problem

Vector memory systems (Qdrant, Pinecone, Weaviate, ChromaDB) are append-only by default. Every new fact creates a new point. This causes:

- **Duplicate dilution:** Near-identical memories degrade search quality
- **Stale facts:** Outdated information persists indefinitely (e.g., "project uses port 3000" coexists with "project uses port 5001")
- **No correction:** Wrong facts can only be removed by deleting the entire source file and re-indexing
- **Unbounded growth:** Index grows forever without garbage collection
- **Frozen metadata:** Utility scores, version numbers, and confidence fields initialized but never updated

### Why It Was Hard

Rule-based deduplication (cosine similarity thresholds, hash matching) fails because:
- Two semantically equivalent statements can have low cosine similarity ("The server runs on port 5001" vs "API endpoint: localhost:5001")
- Partial overlap is ambiguous (should memory A be updated with info from B, or are they separate facts?)
- Contradiction detection requires understanding, not matching

### Impact

Without CRUD, memory quality degrades over time. Research shows 10% performance drop from bad memories that propagate errors to all downstream tasks that retrieve them (Experience-Following, arXiv 2505.16067).

---

## Solution Pattern

Use an LLM as a judge to decide how each new memory candidate should interact with existing memories. Instead of blindly appending, every new fact goes through a decision pipeline:

```
New Fact → Embed → Find Similar (top-5) → LLM Decides → Execute CRUD → Log
```

The LLM receives the new candidate plus its most similar existing memories and returns one of four operations:

| Operation | When | Action |
|-----------|------|--------|
| **ADD** | New unique information | Insert new point |
| **UPDATE** | Refines/corrects existing memory | Merge into existing point |
| **DELETE** | Contradicts with higher confidence | Remove old point |
| **NOOP** | Already known, no new info | Skip silently |

> **Research basis:** Mem0 (arXiv 2504.19413, 2025) — 26% higher accuracy than OpenAI memory, 91% lower p95 latency, 90% token savings. Confirmed by Memory-R1 (arXiv 2508.19828, 2025) and AgeMem (arXiv 2601.01885, 2026).

---

## Code Example

```typescript
// Before (append-only — problematic)
async function indexFact(text: string, metadata: Record<string, unknown>) {
  const embedding = await embed(text);
  await qdrant.upsert(collection, {
    id: generateId(),
    vector: embedding,
    payload: { text, ...metadata, created_at: new Date().toISOString() }
  });
}

// After (LLM-as-Judge CRUD)
interface MemoryOperation {
  op: "ADD" | "UPDATE" | "DELETE" | "NOOP";
  targetId?: string;
  content?: string;
  reason: string;
}

async function smartIndex(text: string, metadata: Record<string, unknown>) {
  // 1. Embed the candidate
  const embedding = await embed(text);

  // 2. Find similar existing memories
  const similar = await qdrant.search(collection, {
    vector: embedding,
    limit: 5,
    score_threshold: 0.7
  });

  // 3. If no similar memories, just ADD
  if (similar.length === 0) {
    return await addMemory(text, embedding, metadata);
  }

  // 4. Ask LLM to decide
  const decision = await llm.structured<MemoryOperation>({
    system: `You manage a memory store. Given a NEW fact and EXISTING memories,
decide: ADD (new unique info), UPDATE (refines existing), DELETE (contradicts
existing with higher confidence), or NOOP (already known).
Return JSON: {op, targetId?, content?, reason}`,
    user: `NEW FACT: ${text}

EXISTING MEMORIES:
${similar.map(s => `[ID: ${s.id}] (score: ${s.score.toFixed(2)}) ${s.payload.text}`).join('\n')}

What should happen?`
  });

  // 5. Execute the decision
  switch (decision.op) {
    case "ADD":
      await addMemory(text, embedding, metadata);
      break;
    case "UPDATE":
      const merged = decision.content || text;
      const newEmbedding = await embed(merged);
      await qdrant.setPayload(collection, {
        points: [decision.targetId],
        payload: {
          text: merged,
          updated_at: new Date().toISOString(),
          version: (existing.version || 1) + 1,
          _prev_content: existing.text
        }
      });
      await qdrant.updateVectors(collection, {
        points: [{ id: decision.targetId, vector: newEmbedding }]
      });
      break;
    case "DELETE":
      await qdrant.delete(collection, { points: [decision.targetId] });
      break;
    case "NOOP":
      break; // Skip — already known
  }

  // 6. Log to changelog
  await changelog.append({
    timestamp: new Date().toISOString(),
    op: decision.op,
    targetId: decision.targetId,
    oldContent: existing?.text,
    newContent: text,
    reason: decision.reason
  });
}
```

---

## Implementation Steps

1. **Add similarity search on ingest** — Before any upsert, query for top-5 similar points (threshold 0.7)
2. **Create LLM decision prompt** — Structured output: `{op, targetId?, content?, reason}`
3. **Implement 4 operation handlers** — ADD (new point), UPDATE (merge + re-embed), DELETE (remove), NOOP (skip)
4. **Add changelog** — JSON-lines file logging every operation with before/after content
5. **Wire into existing indexing pipeline** — Replace direct upserts with `smartIndex()` calls

### Supporting Infrastructure (recommended)

6. **Archive before delete** — Set `is_archived: true` instead of permanent delete; prune archived after 90 days
7. **Rehearsal decay** — On every search retrieval, update `lastAccessedAt` and `timesRetrieved`; use `max(createdAt, lastAccessedAt)` for decay base
8. **Version history** — Store `_prev_content` and `_prev_version` in payload for rollback capability
9. **Health audit** — Periodic job samples random points, asks LLM "Is this still accurate?", prunes low-quality entries

---

## When to Use

- Any vector DB that stores facts/knowledge that changes over time
- Systems where the same information can be expressed differently across sources
- Memory stores that grow unbounded without maintenance
- Projects where outdated information causes real harm (wrong API endpoints, deprecated patterns)
- After observing search quality degrade from duplicates or contradictions

## When NOT to Use

- **Immutable archives** — If you need to preserve every version of every fact (use append + temporal queries instead)
- **High-throughput ingestion** — LLM call per fact adds ~500ms latency; use batch mode for bulk imports
- **Cost-sensitive environments** — Each CRUD decision costs an LLM API call; batch 10-20 candidates per call to amortize
- **Simple key-value stores** — If memories have unique keys, use direct upsert instead of similarity-based CRUD

---

## Common Mistakes

- **Threshold too high (>0.9):** Misses semantically equivalent memories with different wording
- **Threshold too low (<0.5):** LLM gets overwhelmed with irrelevant "similar" memories
- **No changelog:** Without audit trail, bad CRUD decisions are invisible and irreversible
- **UPDATE without re-embedding:** If you change the text but not the vector, search results become inconsistent
- **DELETE without archive:** Permanent deletion loses information that may be needed for rollback
- **Single-item processing at scale:** Process CRUD decisions in batches of 10-20 to reduce LLM call count (Anatomy of Agentic Memory, arXiv 2602.19320)

---

## Batch Mode (for bulk indexing)

```typescript
// Instead of N individual LLM calls, batch candidates
async function batchSmartIndex(candidates: string[], batchSize = 20) {
  for (let i = 0; i < candidates.length; i += batchSize) {
    const batch = candidates.slice(i, i + batchSize);
    const allSimilar = await Promise.all(
      batch.map(c => findSimilar(c, 5))
    );

    // One LLM call for entire batch
    const decisions = await llm.structured<MemoryOperation[]>({
      system: "For each candidate, decide ADD/UPDATE/DELETE/NOOP...",
      user: formatBatch(batch, allSimilar)
    });

    for (const decision of decisions) {
      await executeDecision(decision);
    }
  }
}
```

---

## Related Skills

- [production-memory-patterns](../methodology/PRODUCTION_MEMORY_PATTERNS.md) — Catalog of 10 production memory patterns (this skill implements pattern #1)
- [RESEARCH_BACKED_WORKFLOW_UPGRADE](../methodology/RESEARCH_BACKED_WORKFLOW_UPGRADE.md) — The research methodology used to discover this pattern

## References

- Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory (arXiv 2504.19413, 2025) — 26% accuracy, 91% latency
- Memory-R1: Enhancing LLM Agents to Manage Memories via RL (arXiv 2508.19828, 2025) — RL-trained CRUD
- AgeMem: Learning Unified LTM/STM Management (arXiv 2601.01885, 2026) — Memory as tools
- Experience-Following Behavior (arXiv 2505.16067, 2025) — 10% boost from selective CRUD
- SimpleMem: Efficient Lifelong Memory (arXiv 2601.02553, 2026) — 26.4% F1 via merge
- MemoryBank: Ebbinghaus Forgetting Curve (AAAI 2024) — Rehearsal decay
- Zep/Graphiti: Temporal KG for Agent Memory (arXiv 2501.13956, 2025) — Bi-temporal versioning
- Anatomy of Agentic Memory (arXiv 2602.19320, 2026) — Batch processing for latency
- Contributed from: your-memory-repo v12.0 research session (2026-02-25)
