# NotebookLM-Style RAG AI Course Generation

## Problem Solved
Building a full AI-powered course creation pipeline where generated content is grounded exclusively in instructor-uploaded source materials (PDFs, DOCX, audio, video, YouTube transcripts) rather than the LLM's general training data. This is the "NotebookLM approach" — AI generates only from what you feed it.

## When to Use
- Building RAG-based content generation for LMS or educational platforms
- Implementing source-scoped AI generation (content must come from specific documents)
- Integrating Gemini embeddings with PostgreSQL pgvector
- Creating multi-step AI course wizards (sources -> outline -> lessons -> quizzes -> assignments)
- Replacing OpenAI embeddings with Gemini while maintaining existing vector infrastructure

## Architecture Overview

```
Instructor Flow:
  Upload Sources (PDF/DOCX/YouTube/Audio)
       |
       v
  Text Extraction (pdf-parse, mammoth, youtube-transcript)
       |
       v
  Chunking (sentence-based, ~500 tokens per chunk)
       |
       v
  Embedding (Gemini text-embedding-004, 768-dim -> zero-padded to 1536)
       |
       v
  Storage (PostgreSQL pgvector, ai_content_chunks table)
       |
       v
  Source Linking (ai_course_sources junction table)

Generation Flow:
  Teacher selects sources for course
       |
       v
  Query embedded with same model
       |
       v
  pgvector cosine similarity search (<=> operator)
       |
       v
  Top-K relevant chunks retrieved (scoped to linked sources only)
       |
       v
  Chunks injected into LLM prompt as context
       |
       v
  LLM generates content grounded in source material
```

## Key Technical Patterns

### 1. Gemini Embeddings with Zero-Padding for pgvector

**Problem:** Gemini `text-embedding-004` produces 768-dimensional vectors, but existing pgvector columns are `vector(1536)`.

**Solution:** Zero-pad from 768 to 1536. This is mathematically safe for cosine similarity:
- `dot(A_padded, B_padded) = dot(A, B)` (zeros contribute nothing to dot product)
- `|A_padded| = |A|` (zeros don't change vector magnitude)
- Therefore: `cosine_sim(A_padded, B_padded) = cosine_sim(A, B)`

```javascript
// server/services/ai/EmbeddingService.js
import { GoogleGenerativeAI } from '@google/generative-ai';

class EmbeddingService {
  constructor() {
    this.genAI = null;
    this.model = 'text-embedding-004';
    this.nativeDimensions = 768;
    this.dimensions = 1536; // Zero-padded for pgvector compatibility
  }

  padVector(vector) {
    if (vector.length >= this.dimensions) return vector;
    const padded = new Array(this.dimensions);
    for (let i = 0; i < vector.length; i++) padded[i] = vector[i];
    for (let i = vector.length; i < this.dimensions; i++) padded[i] = 0;
    return padded;
  }

  async embed(text) {
    if (!this.genAI) this.initialize();
    const embeddingModel = this.genAI.getGenerativeModel({ model: this.model });
    const result = await embeddingModel.embedContent(text);
    return this.padVector(result.embedding.values);
  }

  async embedBatch(texts) {
    const embeddingModel = this.genAI.getGenerativeModel({ model: this.model });
    const result = await embeddingModel.batchEmbedContents({
      requests: texts.map(text => ({ content: { parts: [{ text }] } }))
    });
    return result.embeddings.map(e => this.padVector(e.values));
  }
}
export const embeddingService = new EmbeddingService();
```

### 2. Source-Scoped RAG Queries

Content generation is scoped to only the instructor's linked sources via a junction table:

```sql
-- Junction table linking courses to knowledge sources
CREATE TABLE ai_course_sources (
  id SERIAL PRIMARY KEY,
  course_id INTEGER REFERENCES courses(id),
  source_id INTEGER REFERENCES ai_knowledge_sources(id),
  linked_at TIMESTAMPTZ DEFAULT NOW()
);

-- RAG query scoped to course sources
SELECT c.content, c.metadata,
       1 - (c.embedding <=> $1::vector) as similarity
FROM ai_content_chunks c
JOIN ai_knowledge_sources s ON c.source_id = s.id
JOIN ai_course_sources cs ON s.id = cs.source_id
WHERE cs.course_id = $2
  AND 1 - (c.embedding <=> $1::vector) > 0.7
ORDER BY c.embedding <=> $1::vector
LIMIT 10;
```

### 3. Async Ingestion Pipeline

Source processing is non-blocking — upload returns immediately, processing happens in background:

```javascript
// Upload endpoint returns fast
res.json({ sourceId, status: 'processing' });

// Background: extract -> chunk -> embed -> store
async function processSource(sourceId) {
  const text = await extractText(source); // pdf-parse, mammoth, etc.
  const chunks = embeddingService.chunkText(text, 500);
  const embeddings = await embeddingService.embedBatch(chunks);
  await storeChunks(sourceId, chunks, embeddings);
  await updateSourceStatus(sourceId, 'ready');
}
```

### 4. Multi-Provider AI Generation

The system supports multiple LLM providers for content generation (NOT OpenAI):

```javascript
// server/services/ai/AIProviderFactory.js
// Supported: Gemini, Claude (Anthropic), Groq
// Selection based on admin settings or per-request override

const provider = AIProviderFactory.getProvider(settings.provider);
const response = await provider.generateContent(prompt, options);
```

### 5. Course Creation Wizard (3-Step)

```
Step 1: Select/Upload Sources
  - Multi-select from existing knowledge base
  - Upload new PDFs, DOCX files
  - Add YouTube URLs for transcript extraction

Step 2: Generate & Edit Outline
  - Configure: title, level, section count, lessons per section
  - AI generates structured outline from source content
  - Inline editing of sections, lessons, objectives

Step 3: Review & Create
  - Final review of complete course structure
  - One-click creation (creates course + sections + lessons)
  - Automatically links selected sources to course
```

## Database Schema (pgvector)

```sql
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Knowledge sources (uploaded materials)
CREATE TABLE ai_knowledge_sources (
  id SERIAL PRIMARY KEY,
  title VARCHAR(500) NOT NULL,
  source_type VARCHAR(50), -- 'pdf', 'docx', 'youtube', 'audio', 'text'
  file_path TEXT,
  original_filename VARCHAR(500),
  content_text TEXT, -- Full extracted text
  status VARCHAR(50) DEFAULT 'pending', -- 'pending','processing','ready','error'
  metadata JSONB DEFAULT '{}',
  uploaded_by INTEGER REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Content chunks with embeddings
CREATE TABLE ai_content_chunks (
  id SERIAL PRIMARY KEY,
  source_id INTEGER REFERENCES ai_knowledge_sources(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  chunk_index INTEGER,
  embedding vector(1536), -- Gemini 768 zero-padded to 1536
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_chunks_source ON ai_content_chunks(source_id);
CREATE INDEX idx_chunks_embedding ON ai_content_chunks USING ivfflat (embedding vector_cosine_ops);
```

## NPM Dependencies

```json
{
  "@google/generative-ai": "^0.x",  // Gemini AI + embeddings
  "@anthropic-ai/sdk": "^0.x",       // Claude provider
  "groq-sdk": "^0.x",                // Groq provider
  "pdf-parse": "1.1.1",              // PDF text extraction
  "mammoth": "^1.x",                 // DOCX text extraction
  "youtube-transcript": "^1.x"       // YouTube transcript fetching
}
```

**NO OpenAI packages. Owner has an absolute ban on OpenAI.**

## File Structure

```
server/
  services/ai/
    EmbeddingService.js          # Gemini embeddings (core)
    RAGService.js                # RAG query engine
    SourceRAGService.js          # Source-scoped RAG
    AIProviderFactory.js         # Multi-provider factory
    ImageGenerationService.js    # Gemini 2.0 Flash images
    providers/
      GeminiProvider.js
      ClaudeProvider.js
      GroqProvider.js
  controllers/
    aiCourseController.js        # All AI course endpoints
    knowledgeBaseController.js   # Source upload/manage
  models/
    aiSettingsModel.js           # AI config (provider, model)
    aiGenerationModel.js         # Generation history
    knowledgeSourceModel.js      # Source CRUD
  routes/
    aiCourseRoutes.js            # /api/ai-course/*
    knowledgeBaseRoutes.js       # /api/knowledge/*
  migrations/
    128_create_ai_rag_infrastructure.sql
    129_create_knowledge_base_schema.sql

client/
  src/components/ai/
    SourceSelector.jsx                    # Source picker for generation
    SourceUploadDialog.jsx                # Upload new sources
    CourseSourceSelector.jsx              # Course-level source linking
    RefinementChat.jsx                    # Conversational refinement
    KnowledgeAwareLessonGenerator.jsx     # Source-aware lesson gen
    KnowledgeAwareQuizGenerator.jsx       # Source-aware quiz gen
    KnowledgeAwareAssignmentGenerator.jsx # Source-aware assignment gen
    CoverArtGenerator.jsx                 # AI cover art
    InfographicGenerator.jsx              # AI infographics
    WizardStepSources.jsx                 # Wizard step 1
    WizardStepOutline.jsx                 # Wizard step 2
    WizardStepReview.jsx                  # Wizard step 3
    QuizGeneratorPanel.jsx                # Standalone quiz gen
  src/pages/teacher/
    CreateWithAI.jsx                      # AI creation landing page
    NewCourseWizard.jsx                   # 3-step wizard container
  src/services/
    aiCourseApi.js                        # All AI API methods
```

## Gotchas & Lessons Learned

1. **Zero-padding is safe for cosine similarity** but NOT for Euclidean distance. Always use `vector_cosine_ops` index, not `vector_l2_ops`.

2. **Gemini batch embedding** uses `batchEmbedContents` with a specific request format: `{ requests: texts.map(text => ({ content: { parts: [{ text }] } })) }`.

3. **AIProviderFactory loads ALL providers at import time.** If any provider SDK is missing (e.g., `groq-sdk`), the entire import chain fails. Install all provider SDKs even if not actively used.

4. **pdf-parse@1.1.1 specifically** — later versions have issues. Pin to 1.1.1.

5. **Source status lifecycle:** `pending` -> `processing` -> `ready` (or `error`). UI should poll or use WebSocket for status updates.

6. **pgvector IVFFlat index** requires training data. For small datasets (<1000 rows), it may not help. Consider switching to HNSW for better small-dataset performance.

## Related Skills
- `deployment-security/NODE18_DEPENDENCY_COMPATIBILITY.md` — Node 18 package compatibility
- `video-media/REACT_VIDEO_PLAYER_REINITIALIZATION_FIX.md` — Parallel debugging pattern
- `database-solutions/` — PostgreSQL patterns

## Date Created
February 5, 2026

## Origin
Phase 08A execution — NotebookLM-style AI upgrade for MERN Community LMS.
Executed across 6 plans in 3 breaths (breath-based parallel execution).
