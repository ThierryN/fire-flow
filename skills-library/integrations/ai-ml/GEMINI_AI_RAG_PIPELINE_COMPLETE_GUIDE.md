# Gemini AI RAG Pipeline - Complete Implementation Guide

## The Problem

Building a full AI course generation system with RAG (Retrieval-Augmented Generation) using Google Gemini on a Node 18 production server with PostgreSQL/pgvector. Multiple API changes, ESM compatibility issues, and file path mismatches caused cascading failures.

### Why It Was Hard

- Gemini API models deprecate monthly — `text-embedding-004`, `gemini-2.0-flash-exp` all 404'd
- `@google/generative-ai` SDK defaults to `v1beta` API — some models only on `v1`
- ESM + Node 18 + CJS packages = constant import failures
- `process.cwd()` vs `__dirname` path mismatch for file serving
- postgres.js JSONB handling requires `sql.json()` wrapper
- pgvector expects string format `'[x,y,z]'::vector`, not JS arrays

### Impact

- Production site crashed multiple times during development
- Cover art generated but invisible (wrong save directory)
- Knowledge base ingestion silently failed on PDFs and YouTube

---

## The Solution

### Architecture Overview

```
Knowledge Sources (text/PDF/DOCX)
  → FileProcessorService (text extraction)
  → ChunkingService (split into chunks)
  → EmbeddingService (Gemini REST API → 768d vectors, zero-padded to 1536)
  → PostgreSQL pgvector (ai_source_chunks table)

Course Generation:
  → SourceRAGService (pgvector similarity search)
  → AIProviderFactory (Gemini/Claude/Groq)
  → generateContent → save to DB
```

### Critical Model Names (as of Feb 2026)

| Purpose | Model | Notes |
|---------|-------|-------|
| Text Generation | `gemini-2.5-flash` | Via `@google/generative-ai` SDK |
| Embeddings | `gemini-embedding-001` | Direct REST API to `v1beta` (NOT SDK) |
| Image Generation | `gemini-2.5-flash-image` | `responseModalities: ['TEXT', 'IMAGE']` (uppercase) |

### Embedding Service - Use REST API, Not SDK

```javascript
// WRONG: SDK defaults to v1beta which may 404 for some models
const genAI = new GoogleGenerativeAI(apiKey);
const model = genAI.getGenerativeModel({ model: 'text-embedding-004' });

// RIGHT: Direct REST fetch to specific API version
const response = await fetch(
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key=${apiKey}`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'models/gemini-embedding-001',
      content: { parts: [{ text }] },
      outputDimensionality: 768
    })
  }
);
```

### pgvector Format

```javascript
// WRONG: Pass JS array directly
await sql`... WHERE embedding <=> ${embedding}::vector ...`;

// RIGHT: Convert to string format
const embeddingStr = `[${embedding.join(',')}]`;
await sql`... WHERE embedding <=> ${embeddingStr}::vector ...`;
```

### Zero-Padding (768 → 1536)

```javascript
// Gemini outputs 768 dims, pgvector column is vector(1536)
const padded = new Array(1536).fill(0);
for (let i = 0; i < embedding.length; i++) padded[i] = embedding[i];
return padded;
```

### postgres.js JSONB

```javascript
// WRONG: Plain objects get treated as column-value helpers
await sql`INSERT INTO ... VALUES (${someJsonObject})`;

// RIGHT: Wrap with sql.json()
await sql`INSERT INTO ... VALUES (${sql.json(someJsonObject)})`;
```

### Image Generation - File Path

```javascript
// WRONG: process.cwd() resolves to project root, not server/
const dir = path.join(process.cwd(), 'uploads', 'ai-images');

// RIGHT: Use import.meta.url to resolve relative to server/ directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SERVER_DIR = path.resolve(__dirname, '..', '..');
const dir = path.join(SERVER_DIR, 'uploads', 'ai-images');
```

### PDF Parse ESM Fix

```javascript
// WRONG: Main entry runs test code in ESM (reads ./test/data/05-versions-space.pdf)
const pdfParse = (await import('pdf-parse')).default;

// RIGHT: Import lib directly, skips test runner
const pdfParse = (await import('pdf-parse/lib/pdf-parse.js')).default;
```

---

## Testing the Fix

### Verify Embedding Pipeline
1. Upload text source via Knowledge Library
2. Check `ai_knowledge_sources` status transitions: uploading → processing → chunking → embedding → ready
3. Check `ai_source_chunks` has vectors: `SELECT id, length(embedding::text) FROM ai_source_chunks LIMIT 5;`

### Verify Course Generation
1. Create course via AI Wizard, select knowledge sources
2. Verify all lessons get content (check progress bar completes)
3. Open a lesson — should have rich HTML with callout boxes

### Verify Image Generation
1. Go to CourseBuilder > Settings tab
2. Click "Generate Cover Art"
3. Image should display in preview
4. Click "Use This Image" — saves to course thumbnail

---

## Prevention

1. **Always check model availability** before hardcoding: `npm info @google/generative-ai` won't help — check Google AI docs
2. **Use `ai_settings` table** for model names so admin can update without code changes
3. **Test file paths** on production (cwd vs __dirname)
4. **Wrap JSONB** with `sql.json()` in ALL postgres.js queries
5. **Format pgvector** as string `'[x,y,z]'::vector`

---

## Common Mistakes to Avoid

- Using `text-embedding-004` (deprecated, 404)
- Using `gemini-2.0-flash-exp` (deprecated, 404)
- Using `responseModalities: ['Text', 'Image']` (must be uppercase `['TEXT', 'IMAGE']`)
- Importing `pdf-parse` main entry in ESM (tries to read test file)
- Saving uploads to `process.cwd()` when Express serves from `__dirname`
- Passing JS objects to postgres.js JSONB columns without `sql.json()`
- Passing JS arrays to pgvector without string conversion
- Using `@google/generative-ai` SDK for embeddings (defaults to wrong API version)

---

## Related Patterns

- Skills Library: `deployment-security/NODE18_DEPENDENCY_COMPATIBILITY.md`
- MEMORY.md: AI/RAG System section
- WARRIOR Handoff: `2026-02-06_AI-Course-Generation-RAG-Pipeline.md`

---

## Resources

- [Google AI Gemini Models](https://ai.google.dev/gemini-api/docs/models)
- [pgvector PostgreSQL Extension](https://github.com/pgvector/pgvector)
- [postgres.js JSON/JSONB](https://github.com/porsager/postgres#json)

## Time to Implement

Full pipeline from scratch: ~8-12 hours across multiple sessions
Fixing a single model deprecation: ~15 minutes

## Difficulty Level

Stars: 4/5 - Multiple interacting systems, API instability, ESM/CJS conflicts

---

**Author Notes:**
This was a multi-session marathon. The biggest lesson: Google deprecates AI models aggressively. What works today may 404 next month. Make model names configurable in admin settings — that's the next task. Also, always test the full path from file save to browser display on production, not just locally.
