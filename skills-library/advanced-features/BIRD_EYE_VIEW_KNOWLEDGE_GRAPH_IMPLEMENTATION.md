# Bird's Eye View Knowledge Graph - Implementation Guide

## The Problem

Building a hierarchical knowledge graph that extracts document structure using AI, displays it in an interactive mind map with React Flow, implements proper caching to save API costs, and provides configurable layout controls with correct connection logic.

### Why It Was Hard

- **AI Extraction:** Getting Gemini API to consistently return 5-level hierarchical structure (Document → Theme → Chapter → Idea → Sentence)
- **API Race Condition:** Module-level initialization caused "403 Forbidden" errors due to .env loading order
- **Cache Invalidation:** Different documents sharing same userId needed separate caches
- **React Flow Integration:** Custom nodes, handle positions, layout algorithms, and connection logic
- **Parent-Child Relationships:** Field name mismatches (`parentNodeId` vs `parentId`) broke expansion
- **Performance:** Large graphs (26+ nodes) caused slow rendering and viewport resets

### Impact

- Provides visual document structure analysis
- Saves money with intelligent caching (avoids regenerating on every page load)
- Interactive exploration of document hierarchy
- Configurable layouts (LR, RL, TB, BT) for different visualization needs

---

## The Solution

### Architecture Overview

```
Frontend (React) ─────► Backend API ─────► Gemini AI
     │                      │                    │
     │                      ├─► Database Cache  │
     │                      │                    │
     └─► React Flow ◄───────┴────────────────────┘
         (Visualization)
```

### Key Components

1. **Backend Service** (`server/services/knowledge-graph.service.ts`)
2. **API Routes** (`server/routes/knowledge-graph.ts`)
3. **React Hook** (`frontend/src/hooks/useKnowledgeGraph.ts`)
4. **Mind Map Component** (`frontend/src/components/KnowledgeTree/KnowledgeTreeFlow.tsx`)
5. **Database Schema** (Prisma `KnowledgeGraph` model)

---

## Implementation Details

### 1. Fixing Gemini API 403 Error - Lazy Initialization

**Problem:** Module-level initialization happened before .env loaded.

**Bad Code:**
```typescript
// Module level - runs before .env loads
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || '');
// ❌ GEMINI_API_KEY is undefined here!
```

**Good Code:**
```typescript
// Lazy initialization pattern
let genAI: GoogleGenerativeAI | null = null;

function getGeminiClient(): GoogleGenerativeAI {
  if (!genAI) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      throw new Error('[KnowledgeGraph] GEMINI_API_KEY not found');
    }
    genAI = new GoogleGenerativeAI(apiKey);
    console.log('[KnowledgeGraph] Gemini client initialized');
  }
  return genAI;
}

// Use in service methods
const client = getGeminiClient();
const model = client.getGenerativeModel({ model: 'gemini-2.0-flash' });
```

**Why This Works:**
- Initialization happens on first API call, after .env is loaded
- Singleton pattern ensures only one client instance
- Clear error message if API key missing

---

### 2. Document-Specific Caching

**Problem:** Cache returned wrong document's graph when multiple documents existed.

**Bad Code:**
```typescript
// Only checks userId, not which documents
const cachedGraph = await this.loadGraphFromDatabase(userId);
// ❌ Returns Priesthood graph when user requested Hebrews
```

**Good Code:**
```typescript
private async loadGraphFromDatabase(
  userId: string,
  documentIds?: string[]
): Promise<KnowledgeGraph | null> {
  const cached = await prisma.knowledgeGraph.findUnique({
    where: { userId },
  });

  // Verify documentIds match
  if (documentIds && documentIds.length > 0) {
    const cachedSourceIds = [...cached.sourceIds].sort();
    const requestedIds = [...documentIds].sort();

    const idsMatch = cachedSourceIds.length === requestedIds.length &&
      cachedSourceIds.every((id, index) => id === requestedIds[index]);

    if (!idsMatch) {
      console.log('[KnowledgeGraph] Cache mismatch');
      return null; // Force regeneration
    }
  }

  return graphData;
}
```

**Key Points:**
- Compare sorted arrays of document IDs
- Return null if documents don't match
- Each document set has its own cache entry

---

### 3. Parent-Child Relationship Field Naming

**Problem:** Backend used `parentNodeId`, frontend expected `parentId` - broke node expansion.

**Fix:**
```typescript
// Backend: knowledge-graph.service.ts
// Change ALL occurrences from parentNodeId to parentId

// OLD:
node.parentNodeId = parentNode.id;

// NEW:
node.parentId = parentNode.id;
```

**Testing:**
```typescript
// Frontend: Check childrenMap builds correctly
const childrenMap = useMemo(() => {
  const map = new Map<string, string[]>();
  for (const node of graph.nodes) {
    if (node.parentId) {  // ✅ Now works!
      if (!map.has(node.parentId)) {
        map.set(node.parentId, []);
      }
      map.get(node.parentId)!.push(node.id);
    }
  }
  return map;
}, [graph.nodes]);
```

---

### 4. React Flow Layout - Directional Handles

**Problem:** Connections overlapped when layout direction changed.

**Solution:** Dynamic handle positions based on layout direction.

```typescript
// Determine handle positions based on layout
let targetPos: Position, sourcePos: Position;
switch (layoutDirection) {
  case 'LR': // Left to Right
    targetPos = Position.Left;   // Children receive from left
    sourcePos = Position.Right;  // Parents output to right
    break;
  case 'RL': // Right to Left (DEFAULT)
    targetPos = Position.Right;  // Children receive from right
    sourcePos = Position.Left;   // Parents output to left
    break;
  case 'TB': // Top to Bottom
    targetPos = Position.Top;
    sourcePos = Position.Bottom;
    break;
  case 'BT': // Bottom to Top
    targetPos = Position.Bottom;
    sourcePos = Position.Top;
    break;
}

// Apply to node data
data: {
  ...nodeData,
  targetPosition: targetPos,
  sourcePosition: sourcePos,
}
```

**Custom Node Component:**
```typescript
const CustomNode = ({ data, id }: NodeProps<CustomNodeData>) => {
  const isRootNode = data.level === 0;
  const hasChildren = data.hasChildren;

  return (
    <div>
      {/* Target handle - only on non-root nodes */}
      {!isRootNode && (
        <Handle
          type="target"
          position={data.targetPosition}
          id={`${id}-target`}
        />
      )}

      {/* Node content */}
      <div>{data.label}</div>

      {/* Source handle - only on nodes with children */}
      {hasChildren && (
        <Handle
          type="source"
          position={data.sourcePosition}
          id={`${id}-source`}
        />
      )}
    </div>
  );
};
```

**Key Points:**
- Root nodes: Only source handle (output to children)
- Leaf nodes: Only target handle (receive from parent)
- Middle nodes: Both handles
- Handle positions flip with layout direction

---

### 5. Fixing Viewport Reset on Node Expansion

**Problem:** Clicking to expand nodes reset viewport, causing jarring UX.

**Bad Code:**
```typescript
// fitView runs on every update
<ReactFlow
  nodes={nodes}
  edges={edges}
  fitView  // ❌ Resets viewport constantly
/>
```

**Good Code:**
```typescript
const isInitialRender = useRef(true);

useEffect(() => {
  setNodes(initialNodes);
  setEdges(initialEdges);

  // Only fit view on initial render
  if (isInitialRender.current) {
    isInitialRender.current = false;
  }
}, [initialNodes, initialEdges]);

<ReactFlow
  nodes={nodes}
  edges={edges}
  fitView={isInitialRender.current}  // ✅ Only on first load
  fitViewOptions={{
    padding: 0.1,
    minZoom: 0.5,
    maxZoom: 1.2,
  }}
/>
```

---

### 6. Auto-Loading Cached Graph on Document Selection

**Problem:** User had to manually click "Generate" even when cache existed.

**Solution:**
```typescript
// frontend/src/components/KnowledgeTree/KnowledgeTree.tsx
useEffect(() => {
  const loadCachedBirdEyeView = async () => {
    if (activeDocumentFilter && !loading) {
      console.log('[KnowledgeTree] Auto-loading cached graph');
      await generateBirdEyeView([activeDocumentFilter]);
    }
  };
  loadCachedBirdEyeView();
}, [activeDocumentFilter]); // Run when document selection changes
```

**Backend checks cache:**
```typescript
// routes/knowledge-graph.ts
if (!forceRegenerate) {
  const cachedGraph = await knowledgeGraphService.getGraph(userId, documentIds);
  if (cachedGraph && cachedGraph.nodes.length > 0) {
    return res.json({
      nodes: cachedGraph.nodes,
      edges: cachedGraph.edges,
      cached: true,  // ✅ Returns instantly from cache
    });
  }
}
```

---

### 7. ReactFlowProvider Context Fix

**Problem:** Custom node types not found - "Node type 'custom' not found" errors.

**Bad Code:**
```typescript
export const KnowledgeTreeFlow = (props) => {
  return (
    <ReactFlow>  {/* ❌ Wrong component */}
      <KnowledgeTreeFlowInner {...props} />
    </ReactFlow>
  );
};
```

**Good Code:**
```typescript
import { ReactFlowProvider } from 'reactflow';

export const KnowledgeTreeFlow = (props) => {
  return (
    <ReactFlowProvider>  {/* ✅ Correct context provider */}
      <KnowledgeTreeFlowInner {...props} />
    </ReactFlowProvider>
  );
};
```

---

## Complete File Structure

```
server/
├── services/
│   └── knowledge-graph.service.ts      # Core AI extraction & caching
├── routes/
│   └── knowledge-graph.ts              # API endpoints
└── database/
    └── prisma/
        └── schema.prisma                # KnowledgeGraph model

frontend/
├── src/
│   ├── hooks/
│   │   └── useKnowledgeGraph.ts        # React hook for API calls
│   └── components/
│       └── KnowledgeTree/
│           ├── KnowledgeTree.tsx       # Main UI component
│           └── KnowledgeTreeFlow.tsx   # Mind map visualization
```

---

## Testing the Implementation

### 1. Test Gemini API Connection
```bash
node scripts/test-gemini-api-key.js
```

Expected output:
```
✅ SUCCESS!
Response: Hello World
```

### 2. Test Bird's Eye View Generation
```bash
node scripts/test-bird-eye-view.js
```

Expected output:
```
✅ SUCCESS
Nodes: 26-33
Edges: 25-32
Generation Time: 6000-10000ms
```

### 3. Test Cache Persistence
1. Generate graph for document A
2. Refresh page
3. Select document A → Should load instantly from cache
4. Select document B → Should load its own cache or generate
5. Switch back to document A → Should load from cache

### 4. Test Layout Controls
- Switch between LR, RL, TB, BT → Connections should flow correctly
- Click nodes to expand/collapse → Viewport should NOT reset
- Click "Auto-Arrange" → Should fit view with smooth animation

---

## Known Issues & Future Improvements

### Current Issues

1. **Root Node Connection Missing**
   - Root node (Document level 0) doesn't show source handle
   - **Cause:** Conditional rendering removes handle when `hasChildren` check fails
   - **Fix Needed:** Verify `childrenMap.has(rootNodeId)` returns true
   - **Workaround:** Check backend parentId relationships for document node

2. **Not All Nodes Visible**
   - 26 nodes reported but not all displayed
   - **Cause:** Expansion state initialization may not include all levels
   - **Fix Needed:** Review initial `expandedNodes` state logic
   - **Check:** Console logs for `visibleNodeIds` vs `graph.nodes.length`

3. **Large Graph Performance**
   - Slow rendering with 50+ nodes
   - **Cause:** React Flow re-renders entire graph on expansion
   - **Fix Needed:** Implement virtual scrolling or progressive loading
   - **Optimization:** Memoize node components, use `React.memo()`

### Future Enhancements

1. **Progressive Disclosure**
   ```typescript
   // Only show first 2-3 levels by default
   // Lazy load deeper levels on expansion
   ```

2. **Search & Filter**
   ```typescript
   // Search within graph, highlight matching nodes
   // Filter by theme (main/interjected), level, or keyword
   ```

3. **Export Formats**
   - PDF export (currently PNG only)
   - JSON export for external tools
   - Markdown outline export

4. **Collaborative Features**
   - Share graph link with read-only view
   - Annotations on nodes
   - Version history of graph changes

5. **AI-Powered Insights**
   - Suggest related concepts across documents
   - Identify gaps in document structure
   - Auto-generate summaries for each level

---

## Common Mistakes to Avoid

- ❌ **Module-level API initialization** - Always use lazy initialization
- ❌ **Ignoring cache documentIds** - Match requested docs with cached docs
- ❌ **Hardcoding handle positions** - Make them dynamic based on layout
- ❌ **Always fitting view** - Only fit on initial render, not updates
- ❌ **Wrong ReactFlow wrapper** - Use `ReactFlowProvider`, not `ReactFlow`
- ❌ **Field name inconsistency** - Use same field names in backend/frontend
- ❌ **No loading indicators** - Show "Loading from cache" vs "Generating new"

---

## Performance Optimization Tips

### Backend Caching
```typescript
// In-memory cache for hot data
const graphCache = new Map<string, KnowledgeGraph>();

// Database cache for persistence
await prisma.knowledgeGraph.upsert({
  where: { userId },
  update: { graphData, sourceIds, isStale: false },
  create: { userId, graphData, sourceIds }
});
```

### Frontend Optimization
```typescript
// Memoize expensive computations
const childrenMap = useMemo(() => buildChildrenMap(nodes), [nodes]);
const layoutedNodes = useMemo(() => layoutNodes(nodes, direction), [nodes, direction]);

// Use React.memo for custom nodes
export const CustomNode = React.memo(({ data, id }: NodeProps) => {
  // Component implementation
});
```

### Database Indexing
```sql
-- Ensure fast cache lookups
CREATE INDEX idx_knowledge_graph_userid ON knowledge_graphs(user_id);
CREATE INDEX idx_knowledge_graph_source_ids ON knowledge_graphs USING GIN(source_ids);
```

---

## Resources

- [React Flow Documentation](https://reactflow.dev/docs/introduction)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Prisma Caching Strategies](https://www.prisma.io/docs/guides/performance-and-optimization)
- [React Performance Optimization](https://react.dev/learn/render-and-commit)

---

## Time to Implement

- **Initial Setup:** 2-3 hours (API integration, basic structure)
- **Caching System:** 1-2 hours (database model, cache logic)
- **React Flow Integration:** 3-4 hours (custom nodes, layout algorithm)
- **Layout Controls:** 1-2 hours (UI, handle positions)
- **Debugging & Testing:** 2-3 hours (fixing race conditions, field mismatches)

**Total:** ~10-15 hours for complete implementation

## Difficulty Level

⭐⭐⭐⭐ (4/5) - Complex integration of AI, caching, and interactive visualization

---

## Database Schema

```prisma
model KnowledgeGraph {
  id     String @id @default(uuid()) @db.Uuid
  userId String @unique @map("user_id")

  sourceCount Int @map("source_count")
  nodeCount   Int @map("node_count")
  edgeCount   Int @map("edge_count")

  graphData Json @db.JsonB // {nodes: [...], edges: [...]}

  generatedAt  DateTime @map("generated_at") @db.Timestamptz
  generationMs Int      @map("generation_ms")
  modelUsed    String   @map("model_used") @db.VarChar(50)

  sourceIds String[] @map("source_ids")  // Track which docs are cached
  isStale   Boolean  @default(false) @map("is_stale")

  createdAt DateTime @default(now()) @map("created_at") @db.Timestamptz
  updatedAt DateTime @updatedAt @map("updated_at") @db.Timestamptz

  @@map("knowledge_graphs")
}
```

---

## API Endpoints

### GET `/api/knowledge-graph/:userId/bird-eye-view`

**Query Parameters:**
- `documentIds` - JSON array of document IDs (optional)
- `force` - Set to `true` to skip cache and regenerate

**Response:**
```json
{
  "nodes": [
    {
      "id": "uuid",
      "label": "Theme Title",
      "type": "THEME",
      "level": 1,
      "parentId": "parent-uuid",
      "data": {
        "theme": "main",
        "focusScripture": "Hebrews 1:1-4",
        "supportingRefs": ["Psalm 2:7", "2 Samuel 7:14"]
      }
    }
  ],
  "edges": [
    {
      "id": "edge-uuid",
      "source": "parent-uuid",
      "target": "child-uuid",
      "type": "HIERARCHY"
    }
  ],
  "generationTime": 6542,
  "cached": true
}
```

---

**Author Notes:**

This implementation took multiple debugging sessions to get right:

1. **Gemini API 403** - 3 hours debugging, learned about module initialization order
2. **Cache invalidation** - 2 hours figuring out documentIds matching logic
3. **React Flow connections** - 4 hours getting handle positions right for all directions
4. **Field name mismatch** - 1 hour finding parentNodeId vs parentId discrepancy
5. **Performance** - Ongoing optimization for large graphs

**Key Insights:**
- Always use lazy initialization for external API clients
- Cache invalidation is harder than it looks - be specific about what you're caching
- React Flow requires careful handle management - positions matter!
- Field naming consistency across stack saves hours of debugging

**The Payoff:**
- Visual document structure at a glance
- Saves API costs with intelligent caching
- Interactive exploration of complex theological concepts
- Extensible for future AI-powered features

This is one of the most complex features in the system - handle with care and test thoroughly!
