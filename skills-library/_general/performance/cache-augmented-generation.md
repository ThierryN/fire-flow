---
name: cache-augmented-generation
category: performance
version: 1.0.0
contributed: 2026-03-01
contributor: dominion-flow
last_updated: 2026-03-01
contributors:
  - dominion-flow
tags: [caching, llm, rag-alternative, prompt-caching, anthropic, context-window, performance]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Cache Augmented Generation (CAG)

## Problem

RAG (Retrieval Augmented Generation) adds latency and complexity: embedding queries, vector search, re-ranking, then injecting chunks. For **small, stable document sets** that change infrequently, this retrieval overhead is unnecessary. The documents fit in the context window, and paying for retrieval infrastructure (Qdrant, embeddings, chunking pipeline) is architectural overkill.

Common symptoms that CAG is a better fit:
- Corpus is <100K tokens and changes less than weekly
- RAG retrieval adds 200-500ms latency per query
- Chunk boundary issues cause incomplete answers
- Users ask about the SAME reference material repeatedly
- You're maintaining embedding + vector DB infrastructure for a small, static corpus

## Solution Pattern

**Pre-load the entire document corpus into the prompt prefix and cache it.** Instead of retrieving relevant chunks at query time (RAG), load ALL relevant documents into a cached system prompt. The LLM sees everything and selects what's relevant — no retrieval pipeline needed.

This works because:
1. Modern context windows (200K tokens) can hold substantial corpora
2. Anthropic's prompt caching stores the prefix server-side (90% cost reduction on cache hits)
3. LLMs are good at finding relevant information within their context — often better than chunked retrieval

### Architecture Comparison

```
RAG Pipeline:
  Query → Embed → Vector Search → Rerank → Inject Chunks → LLM → Response
  Latency: 500-1500ms | Infrastructure: Embedding model + Vector DB + Chunking pipeline

CAG Pipeline:
  Query → [Cached Prefix: All Docs] + Query → LLM → Response
  Latency: 100-300ms | Infrastructure: None (prompt caching is built-in)
```

## Code Example

### Anthropic Prompt Caching (Python)

```python
import anthropic

# Load your stable corpus once
def load_corpus():
    """Load all reference documents into a single string."""
    docs = []
    for path in REFERENCE_DIR.glob("*.md"):
        docs.append(f"## {path.stem}\n\n{path.read_text()}")
    return "\n\n---\n\n".join(docs)

CORPUS = load_corpus()  # Load once at startup

client = anthropic.Anthropic()

def query_with_cag(user_question: str) -> str:
    """Query against the full cached corpus."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": f"You are an expert assistant. Answer questions using ONLY the reference material below.\n\n{CORPUS}",
                "cache_control": {"type": "ephemeral"}  # Cache this prefix
            }
        ],
        messages=[{"role": "user", "content": user_question}]
    )
    return response.content[0].text
```

### Anthropic Prompt Caching (TypeScript/Node.js)

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

// Load corpus once at startup
const CORPUS = loadAllDocs();  // Returns concatenated document text

async function queryWithCAG(question: string): Promise<string> {
  const response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 4096,
    system: [
      {
        type: 'text',
        text: `You are an expert assistant. Answer using ONLY the reference material below.\n\n${CORPUS}`,
        cache_control: { type: 'ephemeral' },
      },
    ],
    messages: [{ role: 'user', content: question }],
  });
  return response.content[0].type === 'text' ? response.content[0].text : '';
}
```

### Cache Invalidation

```typescript
// Simple: Reload corpus on file change (fs.watch or chokidar)
import { watch } from 'chokidar';

let corpus = loadAllDocs();

watch(REFERENCE_DIR, { ignoreInitial: true }).on('change', () => {
  corpus = loadAllDocs();
  console.log('CAG corpus reloaded — next request uses fresh cache');
});
```

## Implementation Steps

1. Inventory your document corpus — count tokens (use `tiktoken` or Anthropic's token counter)
2. If corpus < 100K tokens AND changes infrequently, CAG is viable
3. Concatenate all documents into a single system prompt string with clear section markers
4. Add `cache_control: { type: "ephemeral" }` to the system message
5. Remove RAG infrastructure (embedding, vector DB, chunking) if CAG covers the entire use case
6. Add file watcher for cache invalidation if documents can change

## When to Use

- Reference material is small (<100K tokens) and stable (changes < weekly)
- Users repeatedly query the SAME document set
- RAG retrieval latency is a pain point
- Chunk boundary issues cause incomplete or fragmented answers
- You want to eliminate embedding/vector DB infrastructure for a specific use case
- Bible corpus, legal documents, company policies, API specs, style guides

## When NOT to Use

- Corpus exceeds context window limits (>150K tokens for safety margin)
- Documents change frequently (hourly/daily) — cache invalidation overhead negates benefits
- You need to search across millions of documents (RAG scales, CAG doesn't)
- Queries need to combine information from different document versions
- Cost is the primary concern and queries are infrequent (cached prefix has per-session cost)
- You need metadata filtering (by date, author, category) — RAG handles this naturally

## Common Mistakes

- Pre-loading a corpus that's too large — causes context window pressure and degrades answer quality
- Forgetting cache invalidation — stale cached responses return outdated information
- Caching with high temperature — non-deterministic outputs make cached patterns unreliable
- Not measuring token count — "small" corpora can be surprisingly large when fully loaded
- Mixing CAG and RAG without clear boundaries — pick one per document set
- Ignoring the 5-minute cache TTL on Anthropic — frequent cold starts negate cost savings

## Related Skills

- [AI_RESPONSE_DATABASE_CACHING](../database-solutions/AI_RESPONSE_DATABASE_CACHING.md) - Response-level caching for expensive LLM calls
- [persistent-analysis-storage](../database-solutions/persistent-analysis-storage.md) - Dual-storage for expensive analysis results

## References

- Anthropic Prompt Caching: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
- CAG concept derived from AITMPL prompt-caching skill analysis (2026-03-01)
- Contributed from: dominion-flow gap analysis (AITMPL audit session)
