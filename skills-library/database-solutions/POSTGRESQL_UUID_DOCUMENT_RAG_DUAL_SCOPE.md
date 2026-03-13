# PostgreSQL UUID Document Upload with RAG Dual-Scope Search

## The Problem

When implementing a document RAG (Retrieval-Augmented Generation) system with personal and shared libraries, three critical issues emerged:

### Issue 1: Prisma UUID Validation Failures
```
Invalid 'prisma.knowledgeSource.create()' invocation
Error creating UUID, invalid character: expected an optional prefix of
'urn:uuid:' followed by [0-9a-fA-F-], found '' at 1
```

**Why It Was Hard:**
- PostgreSQL `@db.Uuid` type requires actual UUID format (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
- JavaScript's `||` operator doesn't convert empty strings to `null`
- String IDs like `'user-personal-library-001'` appear valid in code but fail at database layer
- Error message doesn't clearly indicate the source of the problem

### Issue 2: Dual Upload Systems Storing Data in Different Tables
```
DocumentUpload.tsx → /api/documents/upload → workspace_Document table (no userId)
Settings.tsx → /api/knowledge/sources → knowledge_sources table (has userId)
RAG searches → knowledge_sources table only
Result: Documents uploaded via DocumentsPage invisible to RAG
```

**Why It Was Hard:**
- Two separate upload endpoints created during different development phases
- No clear indication that tables were misaligned
- Upload success didn't mean RAG searchability
- Required end-to-end testing to discover

### Issue 3: RAG Not Finding Personal Library Documents
```
User: "search my library"
AI: "No documents detected"
Database: 6 documents with status='READY' and userId='0584cd60-...'
MainLayout: userId='shared-corpus' (converts to null)
Result: userId mismatch prevents RAG from finding documents
```

**Why It Was Hard:**
- Original implementation: Bible-only corpus (userId=null)
- New implementation: Personal library support (userId=UUID)
- No admin toggle to control RAG scope
- Required architectural decision on search strategy

### Impact

- **Personal library uploads failed completely** - Prisma validation errors
- **Uploaded documents invisible to AI** - Wrong table, no RAG integration
- **User confusion and frustration** - Upload succeeds but search fails
- **Dual systems causing maintenance burden** - Two endpoints, two tables
- **No flexibility for admins** - Bible-only vs personal library hard-coded

---

## The Solution

### Root Cause Analysis

**Problem 1: UUID Format**
- Using string IDs instead of valid UUID format for PostgreSQL `@db.Uuid` columns
- Empty string userId values not sanitized to `null`

**Problem 2: Table Misalignment**
- OLD system (Phase 9.0): `/api/documents/upload` → `workspace_Document` (no userId)
- NEW system (Phase 9.1): `/api/knowledge/sources` → `knowledge_sources` (has userId)
- RAG only searches `knowledge_sources` table

**Problem 3: Architecture Evolution**
- Original: Bible corpus only (userId=null)
- Current: Bible + personal library (different userId values)
- Missing: Admin control for RAG search scope

### Fix #1: UUID Validation and Sanitization

**Backend (server/routes/knowledge.ts):**
```typescript
// POST /api/knowledge/sources
router.post('/sources', upload.single('file'), async (req, res) => {
  const { title, userId } = req.body;

  // CRITICAL: Sanitize userId - convert empty strings to null
  const sanitizedUserId = userId?.trim() || null;

  const source = await prisma.knowledgeSource.create({
    data: {
      userId: sanitizedUserId, // NULL = shared corpus, UUID = personal library
      title: title || req.file.originalname,
      fileType: path.extname(req.file.originalname).substring(1),
      filePath: req.file.path,
      fileSize: req.file.size,
      status: 'PENDING',
    }
  });

  res.json(source);
});

// POST /api/knowledge/sources/youtube
router.post('/sources/youtube', async (req, res) => {
  const { url, title, userId } = req.body;

  // CRITICAL: Sanitize userId here too
  const sanitizedUserId = userId?.trim() || null;

  const source = await prisma.knowledgeSource.create({
    data: {
      userId: sanitizedUserId,
      title,
      sourceUrl: url,
      fileType: 'youtube',
      status: 'PENDING',
    }
  });

  res.json(source);
});

// POST /api/knowledge/sources/text
router.post('/sources/text', async (req, res) => {
  const { text, title, userId } = req.body;

  // CRITICAL: Sanitize userId here too
  const sanitizedUserId = userId?.trim() || null;

  const source = await prisma.knowledgeSource.create({
    data: {
      userId: sanitizedUserId,
      title,
      extractedText: text,
      fileType: 'text',
      status: 'PENDING',
    }
  });

  res.json(source);
});
```

**Frontend - Use Valid UUID:**
```typescript
// WRONG: String ID that looks valid but isn't UUID
const PERSONAL_USER_ID = 'user-personal-library-001'; // ❌ Fails PostgreSQL @db.Uuid

// RIGHT: Actual UUID format
const PERSONAL_USER_ID = '0584cd60-2eb8-424c-a789-e68340a9161c'; // ✅ Works
```

### Fix #2: Migrate to Unified Upload System

**DocumentUpload.tsx Migration:**
```typescript
interface DocumentUploadProps {
  onDocumentUploaded?: () => void;
  userId?: string | null; // UUID for personal, null/'shared-corpus' for shared
}

export function DocumentUpload({ onDocumentUploaded, userId }: DocumentUploadProps) {
  const uploadFile = (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', file.name);

    // Add userId if personal library
    if (userId && userId !== 'shared-corpus') {
      formData.append('userId', userId);
    }

    const xhr = new XMLHttpRequest();

    // CHANGED: Use knowledge API instead of old documents API
    xhr.open('POST', '/api/knowledge/sources'); // ✅ Unified endpoint

    xhr.onload = () => {
      if (xhr.status === 200) {
        const data = JSON.parse(xhr.responseText);
        pollStatus(data.id); // Poll for READY status
      }
    };

    xhr.send(formData);
  };

  const pollStatus = async (documentId: string) => {
    const interval = setInterval(async () => {
      // CHANGED: Poll knowledge API for status
      const response = await fetch(`/api/knowledge/sources/${documentId}`);
      const data = await response.json();

      // CHANGED: Check for 'READY' instead of 'vectorized'
      if (data.status === 'READY') {
        clearInterval(interval);
        if (onDocumentUploaded) {
          onDocumentUploaded();
        }
      }
    }, 3000);
  };
}
```

**DocumentsPage.tsx - Library Selection:**
```typescript
const PERSONAL_USER_ID = '0584cd60-2eb8-424c-a789-e68340a9161c';

export const DocumentsPage: React.FC = () => {
  const [uploadToPersonal, setUploadToPersonal] = useState(true);

  return (
    <div>
      {/* Library selection UI */}
      <div className="library-toggle">
        <label>
          <input
            type="radio"
            checked={uploadToPersonal}
            onChange={() => setUploadToPersonal(true)}
          />
          My Personal Library
        </label>
        <label>
          <input
            type="radio"
            checked={!uploadToPersonal}
            onChange={() => setUploadToPersonal(false)}
          />
          Shared Library
        </label>
      </div>

      <DocumentUpload
        userId={uploadToPersonal ? PERSONAL_USER_ID : null}
        onDocumentUploaded={handleRefresh}
      />
    </div>
  );
};
```

**Settings.tsx - Fixed DEFAULT_USER_ID:**
```typescript
// WRONG: null means shared corpus, not personal library
const DEFAULT_USER_ID = null; // ❌

// RIGHT: Valid UUID for personal library
const DEFAULT_USER_ID = '0584cd60-2eb8-424c-a789-e68340a9161c'; // ✅

const { documents, uploadFile } = useDocuments(DEFAULT_USER_ID);
```

### Fix #3: RAG Dual-Scope Search with Admin Toggle

**Frontend - RAG Toggle Component:**
```typescript
// frontend/src/components/Settings/RAGLibraryToggle.tsx
export function RAGLibraryToggle() {
  const [includePersonal, setIncludePersonal] = useState(() => {
    const stored = localStorage.getItem('ragIncludePersonalLibrary');
    return stored === 'true';
  });

  const handleToggle = (checked: boolean) => {
    setIncludePersonal(checked);
    localStorage.setItem('ragIncludePersonalLibrary', checked.toString());

    // Notify MainLayout of change
    window.dispatchEvent(new Event('storage'));
  };

  return (
    <div>
      <label>
        <input
          type="checkbox"
          checked={includePersonal}
          onChange={(e) => handleToggle(e.target.checked)}
        />
        Include Personal Library in RAG Search
      </label>

      {includePersonal && (
        <p className="help-text">
          ✓ Active: Searches 60% personal library + 40% Bible corpus
        </p>
      )}
    </div>
  );
}
```

**Frontend - MainLayout.tsx:**
```typescript
const DEFAULT_USER_ID = 'shared-corpus'; // Bible only
const PERSONAL_USER_ID = '0584cd60-2eb8-424c-a789-e68340a9161c'; // Personal library

export function MainLayout() {
  const [userId, setUserId] = useState(() => {
    const includePersonal = localStorage.getItem('ragIncludePersonalLibrary') === 'true';
    return includePersonal ? PERSONAL_USER_ID : DEFAULT_USER_ID;
  });

  useEffect(() => {
    const handleStorageChange = () => {
      const includePersonal = localStorage.getItem('ragIncludePersonalLibrary') === 'true';
      setUserId(includePersonal ? PERSONAL_USER_ID : DEFAULT_USER_ID);
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return (
    <ChatInterface
      userId={userId} // Dynamically set based on toggle
      conversationId={selectedConversationId}
    />
  );
}
```

**Backend - Dual-Scope RAG Search:**
```typescript
// server/services/rag-query.service.ts
async retrieveContext(query: string, userId: string | null, limit: number = 5): Promise<RAGContext[]> {
  const embedding = await this.embedQuery(query);
  const embeddingString = `[${embedding.join(',')}]`;

  if (!userId) {
    // Search ONLY shared corpus (Bible documents)
    const results = await this.prisma.$queryRaw<RAGContext[]>`
      SELECT
        c.id,
        c.content,
        c.embedding <=> ${embeddingString}::vector as distance,
        1 - (c.embedding <=> ${embeddingString}::vector) as similarity,
        s.title,
        s.file_type as "fileType"
      FROM source_chunks c
      JOIN knowledge_sources s ON c.source_id = s.id
      WHERE s.status = 'READY' AND s.user_id IS NULL
      ORDER BY c.embedding <=> ${embeddingString}::vector
      LIMIT ${limit}
    `;
    return results;
  } else {
    // Search BOTH personal (60%) + shared (40%)
    const personalLimit = Math.ceil(limit * 0.6); // 60% from personal
    const sharedLimit = Math.floor(limit * 0.4);  // 40% from shared

    // Query personal documents
    const personalResults = await this.prisma.$queryRaw<RAGContext[]>`
      SELECT /* ... same fields ... */
      FROM source_chunks c
      JOIN knowledge_sources s ON c.source_id = s.id
      WHERE s.status = 'READY' AND s.user_id = ${userId}::uuid
      ORDER BY c.embedding <=> ${embeddingString}::vector
      LIMIT ${personalLimit}
    `;

    // Query shared documents (Bible)
    const sharedResults = await this.prisma.$queryRaw<RAGContext[]>`
      SELECT /* ... same fields ... */
      FROM source_chunks c
      JOIN knowledge_sources s ON c.source_id = s.id
      WHERE s.status = 'READY' AND s.user_id IS NULL
      ORDER BY c.embedding <=> ${embeddingString}::vector
      LIMIT ${sharedLimit}
    `;

    // Combine and re-rank by similarity
    const combined = [...personalResults, ...sharedResults]
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, limit);

    return combined;
  }
}
```

---

## Testing the Fix

### Test #1: Personal Library Upload (DocumentsPage)

**Steps:**
1. Navigate to Documents page
2. Select "My Personal Library" radio button
3. Upload a PDF document
4. Wait for status to show "ready"
5. Check database

**Expected Results:**
```sql
SELECT id, user_id, title, status FROM knowledge_sources
WHERE user_id = '0584cd60-2eb8-424c-a789-e68340a9161c'
ORDER BY created_at DESC LIMIT 1;

-- Should return:
-- id: uuid
-- user_id: 0584cd60-2eb8-424c-a789-e68340a9161c
-- title: YourDocument.pdf
-- status: READY
```

### Test #2: Settings "My Library" Upload

**Steps:**
1. Navigate to Settings → My Library
2. Upload a document
3. Wait for "READY" status
4. Check database

**Expected Results:**
Same as Test #1 - should appear with personal userId

### Test #3: Shared Library Upload

**Steps:**
1. Navigate to Documents page
2. Select "Shared Library" radio button
3. Upload a document
4. Check database

**Expected Results:**
```sql
SELECT id, user_id, title, status FROM knowledge_sources
WHERE user_id IS NULL
ORDER BY created_at DESC LIMIT 1;

-- Should return:
-- id: uuid
-- user_id: NULL
-- title: SharedDocument.pdf
-- status: READY
```

### Test #4: RAG Search - Bible Only (Toggle OFF)

**Steps:**
1. Settings → Turn OFF "Include Personal Library"
2. Go to Chat page
3. Query: "What does Genesis say about creation?"

**Expected Results:**
- RAG searches with userId=null (shared corpus only)
- Response includes Bible verses
- No personal library documents cited

### Test #5: RAG Search - Personal + Bible (Toggle ON)

**Steps:**
1. Settings → Turn ON "Include Personal Library"
2. Upload a document about "prayer" to personal library
3. Query: "search my library for prayer"

**Expected Results:**
- RAG searches with userId=UUID (dual-scope)
- Response includes 60% from personal library
- Response includes 40% from Bible corpus
- Citations reference both sources

### Test #6: End-to-End Verification

**Database Query:**
```sql
-- Check document distribution
SELECT
  CASE
    WHEN user_id IS NULL THEN 'Shared (Bible)'
    ELSE 'Personal Library'
  END as library_type,
  COUNT(*) as count,
  SUM(CASE WHEN status = 'READY' THEN 1 ELSE 0 END) as ready_count
FROM knowledge_sources
GROUP BY library_type;

-- Check chunk creation
SELECT COUNT(*) as chunks, s.title, s.user_id
FROM source_chunks c
JOIN knowledge_sources s ON c.source_id = s.id
GROUP BY s.title, s.user_id
ORDER BY s.created_at DESC
LIMIT 10;
```

---

## Prevention

### 1. Always Use Valid UUIDs for PostgreSQL `@db.Uuid` Columns

```typescript
// ❌ DON'T: Use string IDs that look valid
const userId = 'user-personal-library-001';

// ✅ DO: Generate or use actual UUIDs
import { randomUUID } from 'crypto';
const userId = randomUUID(); // '0584cd60-2eb8-424c-a789-e68340a9161c'

// ✅ DO: Define constants with valid UUIDs
const PERSONAL_USER_ID = '0584cd60-2eb8-424c-a789-e68340a9161c';
```

### 2. Sanitize userId Input in All Upload Endpoints

```typescript
// Apply this pattern to EVERY endpoint that accepts userId
const sanitizedUserId = userId?.trim() || null;

// Why: JavaScript's || doesn't convert empty strings to null
'' || 'fallback'  // returns '' (still truthy for Prisma validation)
('' || null)      // returns null ✓
```

### 3. Unify Upload Systems - Single Source of Truth

```typescript
// ❌ DON'T: Create multiple upload endpoints
/api/documents/upload → workspace_Document
/api/knowledge/sources → knowledge_sources

// ✅ DO: Use single endpoint for all uploads
/api/knowledge/sources → knowledge_sources (RAG-searchable)

// Then migrate data from old table if needed
```

### 4. Add Admin Toggles for Feature Scope

```typescript
// ✅ DO: Provide UI controls for admins
<RAGLibraryToggle />  // Controls search scope

// ✅ DO: Persist settings in localStorage
localStorage.setItem('ragIncludePersonalLibrary', 'true');

// ✅ DO: React to setting changes dynamically
window.addEventListener('storage', handleSettingChange);
```

### 5. Test End-to-End: Upload → Process → Search

```bash
# Don't just test upload success
# Test the FULL pipeline:

1. Upload document (check database)
2. Wait for processing (status = READY)
3. Verify chunks created (source_chunks table)
4. Test RAG search (query matches document)
5. Verify citations appear in response
```

---

## Related Patterns

- [POSTGRES_SQL_TEMPLATE_BINDING_ERROR.md](./POSTGRES_SQL_TEMPLATE_BINDING_ERROR.md) - SQL binding errors
- [ES_MODULE_SEED_SCRIPT_PATTERN.md](./ES_MODULE_SEED_SCRIPT_PATTERN.md) - Seed scripts
- [CONDITIONAL_SQL_MIGRATION_PATTERN.md](./CONDITIONAL_SQL_MIGRATION_PATTERN.md) - Migrations
- [../integrations/GEMINI_AI_RAG_PIPELINE_COMPLETE_GUIDE.md](../integrations/GEMINI_AI_RAG_PIPELINE_COMPLETE_GUIDE.md) - RAG implementation

---

## Common Mistakes to Avoid

### ❌ Mistake #1: Using String IDs for UUID Columns
```typescript
// This looks valid but FAILS at PostgreSQL
const userId = 'user-personal-library-001';
// Error: invalid character: expected [0-9a-fA-F-]
```

### ❌ Mistake #2: Not Sanitizing Empty Strings
```typescript
// Empty string passes truthy check but fails UUID validation
const userId = formData.get('userId'); // Could be ''
await prisma.create({ data: { userId } }); // FAILS if userId === ''
```

### ❌ Mistake #3: Variable Reuse with Null Mapping
```typescript
// DON'T reuse variable when null has different meanings
let userId = rawUserId === 'shared-corpus' ? null : rawUserId; // For RAG
// ... later ...
await prisma.create({ data: { userId } }); // FAILS - userId can't be null here

// DO separate variables for different purposes
const ragUserId = rawUserId === 'shared-corpus' ? null : rawUserId;
const conversationUserId = rawUserId || 'shared-corpus';
```

### ❌ Mistake #4: Testing Upload Without Testing Search
```typescript
// Upload succeeds → assume it works ✗
// Upload succeeds AND RAG finds it → confirmed ✓
```

### ❌ Mistake #5: Hard-Coding Feature Scope
```typescript
// DON'T hard-code Bible-only or personal-only
const userId = null; // Always Bible

// DO provide admin toggle
const userId = includePersonal ? PERSONAL_UUID : null;
```

---

## Resources

- [PostgreSQL UUID Type](https://www.postgresql.org/docs/current/datatype-uuid.html)
- [Prisma UUID Field](https://www.prisma.io/docs/reference/api-reference/prisma-schema-reference#uuid)
- [Node.js crypto.randomUUID()](https://nodejs.org/api/crypto.html#cryptorandomuuidoptions)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [RAG System Architecture](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

## Time to Implement

**Initial Setup:**
- UUID generation and constants: **5 minutes**
- userId sanitization in endpoints: **15 minutes**
- DocumentUpload migration: **30 minutes**
- RAG toggle component: **20 minutes**
- Dual-scope search implementation: **45 minutes**

**Total: ~2 hours**

**Migration (if needed):**
- Old workspace_Document → knowledge_sources: **1 hour**

---

## Difficulty Level

⭐⭐⭐⭐ (4/5) - Very Hard

**Why Hard:**
- Silent failures (upload succeeds, RAG search fails)
- Multiple layers (frontend, backend, database)
- Architectural evolution (Bible-only → personal library)
- UUID format requirements not obvious from error messages
- Empty string vs null handling subtlety

**Why Worth It:**
- Enables personal knowledge base integration
- Flexible RAG scope control for admins
- Proper PostgreSQL UUID compliance
- Unified upload system for maintainability
- End-to-end searchability verified

---

## Database Schema Reference

```sql
-- knowledge_sources table (unified upload destination)
CREATE TABLE knowledge_sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,  -- NULL = shared corpus (Bible), UUID = personal library
  title TEXT NOT NULL,
  file_type TEXT,
  file_path TEXT,
  source_url TEXT,
  file_size INTEGER,
  status TEXT DEFAULT 'PENDING',  -- PENDING → PROCESSING → CHUNKING → EMBEDDING → READY | FAILED
  processed_at TIMESTAMP,
  error_message TEXT,
  extracted_text TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- source_chunks table (RAG search target)
CREATE TABLE source_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id UUID REFERENCES knowledge_sources(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  chunk_index INTEGER,
  embedding vector(768),  -- pgvector extension
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_source_chunks_embedding ON source_chunks
  USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX idx_knowledge_sources_user_id ON knowledge_sources(user_id);
CREATE INDEX idx_knowledge_sources_status ON knowledge_sources(status);
```

---

## Author Notes

**What Made This Difficult:**

1. **Silent Failures** - Upload succeeded, but RAG search didn't work. No errors in console or logs. Required full end-to-end testing to discover.

2. **UUID Format Confusion** - String IDs like `'user-personal-library-001'` look valid in code, pass frontend validation, but fail at PostgreSQL layer with cryptic error messages.

3. **Empty String vs Null** - JavaScript's `||` operator doesn't convert empty strings to null. This caused Prisma UUID validation failures that were hard to trace.

4. **Architectural Evolution** - System started with Bible-only corpus (userId=null), then added personal library support. Old code assumed null, new code needed UUID. Migration path not obvious.

5. **Dual Upload Systems** - Two separate endpoints created during different phases stored data in different tables. RAG only searched one table, making documents invisible.

**Key Learnings:**

- **Always test end-to-end**: Upload → Processing → RAG Search → Citations
- **UUID validation happens at DB layer**, not in application code
- **Sanitize input at boundaries**: Convert empty strings to null before Prisma
- **Separate variables for different purposes**: Don't reuse when null has different meanings
- **Provide admin flexibility**: Toggles > hard-coded feature scope

**Time Saved for Next Developer:**

Without this skill: **3-5 hours** of debugging UUID errors, tracing table misalignment, and implementing RAG scope controls from scratch.

With this skill: **1-2 hours** following proven patterns with all gotchas documented.

---

**Last Updated:** February 8, 2026
**Status:** ✅ Tested and verified in production
**Project:** Ministry LLM - Biblical Study RAG System
