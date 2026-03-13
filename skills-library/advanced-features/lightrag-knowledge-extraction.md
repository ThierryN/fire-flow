---
name: lightrag-knowledge-extraction
category: advanced-features
version: 1.0.0
contributed: 2026-03-10
contributor: dominion-flow-research
last_updated: 2026-03-10
tags: [rag, graph-rag, lightrag, knowledge-graph, knowledge-extraction, document-analysis, entity-extraction]
difficulty: hard
---

# LightRAG Knowledge Extraction

Lightweight Graph RAG implementation achieving GraphRAG-quality answers at 1/10th the token cost. Based on LightRAG (EMNLP 2025, University of Hong Kong, 28k+ GitHub stars).

## Problem: Why Standard RAG Fails for Complex Questions

### The Chunk Isolation Problem

Standard vector RAG works by:
1. Splitting documents into chunks (~500 tokens each)
2. Embedding each chunk into a vector
3. Finding the top-K most similar chunks to a user query
4. Feeding those chunks as context to an LLM

This works well for **single-hop factual questions** like "What is the learning rate used in the experiment?" where the answer lives in one chunk. But it fundamentally breaks for **multi-hop reasoning** questions:

- "How do topics discussed in Chapter 3 relate to the case study in Chapter 7?"
- "What are the common themes across all uploaded research papers?"
- "How does the methodology in Paper A compare to the results in Paper B?"
- "What topics are NOT covered in the uploaded documents?"

### Why Chunks Cannot Connect

```
Standard RAG retrieves isolated islands:

  [Chunk 47: "The study used a sample of 500 participants..."]
  [Chunk 183: "Results showed a 23% improvement when..."]
  [Chunk 312: "The control group methodology followed..."]

  Each chunk is an island. The LLM sees 3 disconnected fragments.
  It cannot reason about HOW these facts relate to each other
  because the connections (entity co-occurrence, causal chains,
  thematic groupings) are invisible to vector similarity.
```

### The GraphRAG Solution (and Its Cost Problem)

Microsoft's GraphRAG (2024) solved this by building a full knowledge graph:
1. Extract entities and relationships from every chunk (multiple LLM passes)
2. Build hierarchical community detection (Leiden algorithm, multiple levels)
3. Pre-compute summaries for every community at every level
4. Query across communities for global understanding

**The result:** Excellent multi-hop reasoning and cross-document synthesis.

**The cost:** 10x more tokens than standard RAG. A 100-page document that costs $0.50 with standard RAG costs $5.00+ with GraphRAG. For a podcast generation pipeline processing dozens of sources, this is prohibitive.

### Where LightRAG Fits

LightRAG achieves 80-90% of GraphRAG's quality at standard RAG token costs by making three key simplifications:
- Single-pass entity extraction (not multi-round)
- Flat community detection (not hierarchical)
- On-demand summarization (not pre-computed for all communities)

---

## LightRAG Architecture

### High-Level Design

```
Document Ingestion:
  Raw Documents (PDF, DOCX, transcripts)
       |
       v
  Text Extraction + Chunking (~500 tokens)
       |
       v
  [PARALLEL]
       |                          |
       v                          v
  Vector Embedding           Entity Extraction (LLM)
  (Gemini text-embedding-004)     |
       |                          v
       v                    Relationship Extraction (LLM)
  pgvector Storage                |
       |                          v
       |                    Knowledge Graph Construction
       |                          |
       |                          v
       |                    Community Detection (simple clustering)
       |                          |
       v                          v
  ============ Combined Storage (PostgreSQL) ============

Query Time:
  User Question
       |
       v
  Query Analysis (determine: local | global | hybrid)
       |
       +--> Local: Entity-focused retrieval (specific facts)
       |         Find relevant entities -> get their neighborhoods
       |
       +--> Global: Community-level retrieval (synthesis)
       |         Find relevant communities -> use summaries
       |
       +--> Hybrid: Both local + global (default, best quality)
       |
       v
  Context Assembly (graph context + vector chunks)
       |
       v
  LLM Generation (grounded in both graph structure and raw text)
```

### Dual-Level Retrieval Explained

**Local level** answers questions about specific entities and their direct relationships:
- "What methodology did Dr. Smith use?" -> Find entity "Dr. Smith" -> traverse to connected "methodology" nodes
- Works like enhanced standard RAG: entity-aware retrieval instead of pure vector similarity

**Global level** answers questions requiring cross-document synthesis:
- "What are the main research themes across all papers?" -> Find all communities -> rank by relevance -> synthesize summaries
- This is what standard RAG fundamentally cannot do

**Hybrid mode** (recommended default) combines both:
1. Retrieve entity-specific context (local)
2. Retrieve community summaries (global)
3. Merge and deduplicate
4. Feed combined context to LLM

### Why LightRAG Is 10x Cheaper Than GraphRAG

| Operation | GraphRAG | LightRAG | Savings |
|-----------|----------|----------|---------|
| Entity extraction | Multi-round with verification | Single pass | 3x fewer tokens |
| Community detection | Hierarchical Leiden (multiple levels) | Flat clustering (one level) | 2x fewer computations |
| Summarization | Pre-compute ALL community summaries | On-demand (only queried communities) | 5x fewer tokens |
| Index updates | Full rebuild required | Incremental (add new nodes/edges) | 10x faster updates |
| **Total indexing cost** | **~$5.00 per 100 pages** | **~$0.50 per 100 pages** | **~10x** |

---

## Implementation with TypeScript

### Type Definitions

```typescript
// types/lightrag.ts

/** A named entity extracted from text */
interface Entity {
  id: string;
  name: string;
  type: EntityType;
  description: string;
  sourceChunkIds: string[];
  embedding?: number[];
  metadata: Record<string, unknown>;
}

type EntityType =
  | 'PERSON'
  | 'ORGANIZATION'
  | 'CONCEPT'
  | 'METHODOLOGY'
  | 'TECHNOLOGY'
  | 'EVENT'
  | 'LOCATION'
  | 'METRIC'
  | 'DOCUMENT'
  | 'TOPIC';

/** A typed relationship between two entities */
interface Relationship {
  id: string;
  sourceEntityId: string;
  targetEntityId: string;
  type: RelationshipType;
  description: string;
  weight: number; // 0-1, how strong/frequent this relationship is
  sourceChunkIds: string[];
  _sourceName?: string; // Raw entity name from extraction, used during graph resolution
  _targetName?: string; // Raw entity name from extraction, used during graph resolution
}

type RelationshipType =
  | 'USES'
  | 'CREATED_BY'
  | 'PART_OF'
  | 'RELATES_TO'
  | 'CAUSES'
  | 'CONTRADICTS'
  | 'SUPPORTS'
  | 'IMPROVES'
  | 'COMPARED_TO'
  | 'DERIVED_FROM';

/** A cluster of related entities */
interface Community {
  id: string;
  name: string;
  summary: string;
  entityIds: string[];
  keyTopics: string[];
  coherenceScore: number; // 0-1, how tightly related the members are
}

/** Result from dual-level retrieval */
interface RetrievalResult {
  localContext: LocalContext[];
  globalContext: GlobalContext[];
  mergedContext: string;
  retrievalMode: 'local' | 'global' | 'hybrid';
  tokenEstimate: number;
}

interface LocalContext {
  entity: Entity;
  relationships: Relationship[];
  neighborEntities: Entity[];
  relevanceScore: number;
}

interface GlobalContext {
  community: Community;
  summary: string;
  relevanceScore: number;
}

/** Configuration for the LightRAG system */
interface LightRAGConfig {
  /** Which LLM provider to use for extraction */
  llmProvider: 'gemini' | 'claude';
  /** Model ID for entity extraction */
  extractionModel: string;
  /** Model ID for query-time generation */
  generationModel: string;
  /** Maximum entities to extract per chunk */
  maxEntitiesPerChunk: number;
  /** Maximum relationships to extract per chunk */
  maxRelationshipsPerChunk: number;
  /** Minimum community size for summarization */
  minCommunitySize: number;
  /** Embedding dimensions (768 native, 1536 zero-padded for pgvector compat) */
  embeddingDimensions: number;
  /** Number of local context results */
  localTopK: number;
  /** Number of global context results */
  globalTopK: number;
}

const DEFAULT_CONFIG: LightRAGConfig = {
  llmProvider: 'gemini',
  extractionModel: 'gemini-2.0-flash',
  generationModel: 'gemini-2.5-pro',
  maxEntitiesPerChunk: 10,
  maxRelationshipsPerChunk: 15,
  minCommunitySize: 3,
  embeddingDimensions: 1536,
  localTopK: 10,
  globalTopK: 5,
};
```

### Entity Extraction

```typescript
// services/lightrag/entity-extractor.ts

import { GoogleGenerativeAI } from '@google/generative-ai';
import Anthropic from '@anthropic-ai/sdk';

/**
 * Extract entities and relationships from a text chunk using LLM.
 * Single-pass extraction is the key cost saving over GraphRAG.
 */
async function extractEntitiesAndRelationships(
  chunk: string,
  chunkId: string,
  config: LightRAGConfig
): Promise<{ entities: Entity[]; relationships: Relationship[] }> {
  const prompt = buildExtractionPrompt(chunk);

  let responseText: string;

  if (config.llmProvider === 'gemini') {
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
    const model = genAI.getGenerativeModel({ model: config.extractionModel });
    const result = await model.generateContent(prompt);
    responseText = result.response.text();
  } else {
    // Claude extraction
    const anthropic = new Anthropic();
    const result = await anthropic.messages.create({
      model: config.extractionModel,
      max_tokens: 4096,
      messages: [{ role: 'user', content: prompt }],
    });
    responseText = result.content[0].type === 'text' ? result.content[0].text : '';
  }

  return parseExtractionResponse(responseText, chunkId);
}

/**
 * Build the entity/relationship extraction prompt.
 * This is the most critical prompt in the entire system.
 */
function buildExtractionPrompt(chunk: string): string {
  return `You are an expert knowledge graph builder. Extract all meaningful entities and relationships from the following text.

## Rules
1. Extract SPECIFIC, NAMED entities (not generic concepts like "the study" or "the method")
2. Each entity must have a clear type from: PERSON, ORGANIZATION, CONCEPT, METHODOLOGY, TECHNOLOGY, EVENT, LOCATION, METRIC, DOCUMENT, TOPIC
3. Each relationship must connect exactly two extracted entities
4. Relationship types must be from: USES, CREATED_BY, PART_OF, RELATES_TO, CAUSES, CONTRADICTS, SUPPORTS, IMPROVES, COMPARED_TO, DERIVED_FROM
5. Include a brief description for each entity and relationship
6. Assign relationship weights from 0.1 to 1.0 based on how explicitly stated the connection is

## Text to Analyze
${chunk}

## Required Output Format (strict JSON)
{
  "entities": [
    {
      "name": "Entity Name",
      "type": "ENTITY_TYPE",
      "description": "One-sentence description of this entity in context"
    }
  ],
  "relationships": [
    {
      "source": "Source Entity Name",
      "target": "Target Entity Name",
      "type": "RELATIONSHIP_TYPE",
      "description": "One-sentence description of how these entities relate",
      "weight": 0.8
    }
  ]
}

Return ONLY valid JSON. No markdown fences, no explanation.`;
}

/**
 * Parse the LLM response into typed Entity and Relationship objects.
 * Handles common LLM output quirks (markdown fences, trailing commas).
 */
function parseExtractionResponse(
  responseText: string,
  chunkId: string
): { entities: Entity[]; relationships: Relationship[] } {
  // Strip markdown code fences if present
  let cleaned = responseText
    .replace(/```json\n?/g, '')
    .replace(/```\n?/g, '')
    .trim();

  // Fix trailing commas (common LLM quirk)
  cleaned = cleaned.replace(/,\s*([}\]])/g, '$1');

  try {
    const parsed = JSON.parse(cleaned);

    const entities: Entity[] = (parsed.entities || []).map(
      (e: any, idx: number) => ({
        id: `entity-${chunkId}-${idx}`,
        name: e.name,
        type: e.type as EntityType,
        description: e.description || '',
        sourceChunkIds: [chunkId],
        metadata: {},
      })
    );

    const relationships: Relationship[] = (parsed.relationships || []).map(
      (r: any, idx: number) => ({
        id: `rel-${chunkId}-${idx}`,
        sourceEntityId: '', // Resolved during graph construction
        targetEntityId: '', // Resolved during graph construction
        type: r.type as RelationshipType,
        description: r.description || '',
        weight: Math.min(1, Math.max(0, r.weight || 0.5)),
        sourceChunkIds: [chunkId],
        // Store raw names for resolution
        _sourceName: r.source,
        _targetName: r.target,
      })
    );

    return { entities, relationships };
  } catch (err) {
    console.error(`[LightRAG] Failed to parse extraction for chunk ${chunkId}:`, err);
    return { entities: [], relationships: [] };
  }
}
```

### Knowledge Graph Construction

```typescript
// services/lightrag/knowledge-graph.ts

import { v4 as uuidv4 } from 'uuid';

/**
 * In-memory knowledge graph with community detection.
 * Persisted to PostgreSQL for durability (see pgvector section below).
 */
class KnowledgeGraph {
  private entities: Map<string, Entity> = new Map();
  private relationships: Map<string, Relationship> = new Map();
  private communities: Map<string, Community> = new Map();

  /** Name-to-ID index for entity deduplication */
  private entityNameIndex: Map<string, string> = new Map();

  /**
   * Add an entity, deduplicating by normalized name.
   * If the entity already exists, merge sourceChunkIds.
   */
  addEntity(entity: Entity): string {
    const normalizedName = entity.name.toLowerCase().trim();
    const existingId = this.entityNameIndex.get(normalizedName);

    if (existingId) {
      const existing = this.entities.get(existingId)!;
      // Merge source chunks (entity appears in multiple chunks)
      existing.sourceChunkIds = [
        ...new Set([...existing.sourceChunkIds, ...entity.sourceChunkIds]),
      ];
      // Keep the longer description
      if (entity.description.length > existing.description.length) {
        existing.description = entity.description;
      }
      return existingId;
    }

    const id = uuidv4();
    entity.id = id;
    this.entities.set(id, entity);
    this.entityNameIndex.set(normalizedName, id);
    return id;
  }

  /**
   * Add a relationship between two entities.
   * Resolves entity names to IDs. Skips if either entity is missing.
   */
  addRelationship(
    fromName: string,
    toName: string,
    type: RelationshipType,
    description: string,
    weight: number,
    sourceChunkIds: string[]
  ): void {
    const fromId = this.entityNameIndex.get(fromName.toLowerCase().trim());
    const toId = this.entityNameIndex.get(toName.toLowerCase().trim());

    if (!fromId || !toId) {
      // One or both entities not found -- skip silently
      // This is normal when the LLM references entities it did not formally extract
      return;
    }

    // Check for duplicate relationships
    const existingRel = Array.from(this.relationships.values()).find(
      (r) =>
        r.sourceEntityId === fromId &&
        r.targetEntityId === toId &&
        r.type === type
    );

    if (existingRel) {
      // Merge: increase weight and add source chunks
      existingRel.weight = Math.min(1, existingRel.weight + weight * 0.3);
      existingRel.sourceChunkIds = [
        ...new Set([...existingRel.sourceChunkIds, ...sourceChunkIds]),
      ];
      return;
    }

    const id = uuidv4();
    this.relationships.set(id, {
      id,
      sourceEntityId: fromId,
      targetEntityId: toId,
      type,
      description,
      weight,
      sourceChunkIds,
    });
  }

  /**
   * Simple community detection using connected-component clustering
   * with entity co-occurrence weighting.
   *
   * This is the key simplification vs. GraphRAG's hierarchical Leiden algorithm.
   * One flat level of communities is sufficient for most use cases.
   */
  detectCommunities(): Community[] {
    // Build adjacency list
    const adjacency: Map<string, Set<string>> = new Map();
    for (const entity of this.entities.values()) {
      adjacency.set(entity.id, new Set());
    }

    for (const rel of this.relationships.values()) {
      adjacency.get(rel.sourceEntityId)?.add(rel.targetEntityId);
      adjacency.get(rel.targetEntityId)?.add(rel.sourceEntityId);
    }

    // BFS to find connected components
    const visited = new Set<string>();
    const components: string[][] = [];

    for (const entityId of this.entities.keys()) {
      if (visited.has(entityId)) continue;

      const component: string[] = [];
      const queue = [entityId];

      while (queue.length > 0) {
        const current = queue.shift()!;
        if (visited.has(current)) continue;
        visited.add(current);
        component.push(current);

        for (const neighbor of adjacency.get(current) || []) {
          if (!visited.has(neighbor)) {
            queue.push(neighbor);
          }
        }
      }

      components.push(component);
    }

    // Convert components to communities
    this.communities.clear();
    const result: Community[] = [];

    for (const component of components) {
      if (component.length < 2) continue; // Skip isolated entities

      const communityEntities = component.map((id) => this.entities.get(id)!);
      const keyTopics = this.extractKeyTopics(communityEntities);

      const community: Community = {
        id: uuidv4(),
        name: keyTopics.slice(0, 3).join(', '),
        summary: '', // Generated on-demand (key LightRAG optimization)
        entityIds: component,
        keyTopics,
        coherenceScore: this.computeCoherence(component),
      };

      this.communities.set(community.id, community);
      result.push(community);
    }

    return result;
  }

  /**
   * Extract key topics from a set of entities by frequency and type.
   * CONCEPT and TOPIC entities are weighted higher.
   */
  private extractKeyTopics(entities: Entity[]): string[] {
    const scored = entities.map((e) => ({
      name: e.name,
      score:
        (e.type === 'CONCEPT' || e.type === 'TOPIC' ? 2 : 1) *
        e.sourceChunkIds.length,
    }));

    return scored
      .sort((a, b) => b.score - a.score)
      .slice(0, 5)
      .map((s) => s.name);
  }

  /**
   * Compute how tightly connected a community is.
   * Higher = more internal edges relative to possible edges.
   */
  private computeCoherence(entityIds: string[]): number {
    const idSet = new Set(entityIds);
    let internalEdges = 0;

    for (const rel of this.relationships.values()) {
      if (idSet.has(rel.sourceEntityId) && idSet.has(rel.targetEntityId)) {
        internalEdges++;
      }
    }

    const maxEdges = (entityIds.length * (entityIds.length - 1)) / 2;
    return maxEdges > 0 ? internalEdges / maxEdges : 0;
  }

  /**
   * Local query: find entities matching the question and return their neighborhoods.
   */
  queryLocal(questionEntities: string[], topK: number): LocalContext[] {
    const results: LocalContext[] = [];

    for (const queryName of questionEntities) {
      const normalized = queryName.toLowerCase().trim();
      const entityId = this.entityNameIndex.get(normalized);
      if (!entityId) continue;

      const entity = this.entities.get(entityId)!;

      // Get all relationships involving this entity
      const rels = Array.from(this.relationships.values()).filter(
        (r) => r.sourceEntityId === entityId || r.targetEntityId === entityId
      );

      // Get neighbor entities
      const neighborIds = new Set<string>();
      for (const rel of rels) {
        neighborIds.add(
          rel.sourceEntityId === entityId
            ? rel.targetEntityId
            : rel.sourceEntityId
        );
      }

      const neighbors = Array.from(neighborIds)
        .map((id) => this.entities.get(id)!)
        .filter(Boolean);

      results.push({
        entity,
        relationships: rels,
        neighborEntities: neighbors,
        relevanceScore: 1.0, // Direct match
      });
    }

    return results.slice(0, topK);
  }

  /**
   * Global query: find communities relevant to the question.
   */
  queryGlobal(questionTopics: string[], topK: number): GlobalContext[] {
    const results: GlobalContext[] = [];

    for (const community of this.communities.values()) {
      // Score community by topic overlap
      const topicSet = new Set(
        community.keyTopics.map((t) => t.toLowerCase())
      );
      let score = 0;

      for (const topic of questionTopics) {
        const normalizedTopic = topic.toLowerCase();
        for (const communityTopic of topicSet) {
          if (
            communityTopic.includes(normalizedTopic) ||
            normalizedTopic.includes(communityTopic)
          ) {
            score += 1;
          }
        }
      }

      if (score > 0) {
        results.push({
          community,
          summary: community.summary,
          relevanceScore: score / questionTopics.length,
        });
      }
    }

    return results
      .sort((a, b) => b.relevanceScore - a.relevanceScore)
      .slice(0, topK);
  }

  /** Get graph statistics for monitoring */
  getStats(): { entities: number; relationships: number; communities: number } {
    return {
      entities: this.entities.size,
      relationships: this.relationships.size,
      communities: this.communities.size,
    };
  }

  /** Serialize for persistence */
  toJSON(): object {
    return {
      entities: Array.from(this.entities.values()),
      relationships: Array.from(this.relationships.values()),
      communities: Array.from(this.communities.values()),
    };
  }

  /** Restore from persisted data */
  static fromJSON(data: any): KnowledgeGraph {
    const graph = new KnowledgeGraph();
    for (const entity of data.entities || []) {
      graph.entities.set(entity.id, entity);
      graph.entityNameIndex.set(entity.name.toLowerCase().trim(), entity.id);
    }
    for (const rel of data.relationships || []) {
      graph.relationships.set(rel.id, rel);
    }
    for (const community of data.communities || []) {
      graph.communities.set(community.id, community);
    }
    return graph;
  }
}
```

### Dual-Level Retrieval

```typescript
// services/lightrag/retriever.ts

import { Pool } from 'pg';

/**
 * Hybrid retrieval combining knowledge graph traversal with vector search.
 * This is the core LightRAG query pipeline.
 */
async function hybridRetrieve(
  question: string,
  graph: KnowledgeGraph,
  pool: Pool,
  config: LightRAGConfig
): Promise<RetrievalResult> {
  // Step 1: Analyze the question to extract query entities and topics
  const queryAnalysis = await analyzeQuestion(question, config);

  // Step 2: Determine retrieval mode
  const mode = queryAnalysis.requiresGlobal ? 'hybrid' : 'local';

  // Step 3: Local retrieval (entity-focused)
  const localContext = graph.queryLocal(
    queryAnalysis.entities,
    config.localTopK
  );

  // Step 4: Global retrieval (community-focused)
  let globalContext: GlobalContext[] = [];
  if (mode === 'hybrid' || mode === 'global') {
    globalContext = graph.queryGlobal(
      queryAnalysis.topics,
      config.globalTopK
    );

    // Generate community summaries on-demand (not pre-computed)
    for (const ctx of globalContext) {
      if (!ctx.summary) {
        ctx.summary = await generateCommunitySummary(
          ctx.community,
          graph,
          config
        );
      }
    }
  }

  // Step 5: Vector retrieval for raw text grounding
  const vectorChunks = await vectorSearch(question, pool, config);

  // Step 6: Merge all context
  const mergedContext = assembleContext(localContext, globalContext, vectorChunks);

  // Step 7: Estimate token usage
  const tokenEstimate = Math.ceil(mergedContext.length / 4);

  return {
    localContext,
    globalContext,
    mergedContext,
    retrievalMode: mode,
    tokenEstimate,
  };
}

/**
 * Analyze the question to extract entities and determine if global retrieval is needed.
 */
async function analyzeQuestion(
  question: string,
  config: LightRAGConfig
): Promise<{
  entities: string[];
  topics: string[];
  requiresGlobal: boolean;
}> {
  const prompt = `Analyze this question for knowledge graph retrieval.

Question: "${question}"

Determine:
1. Named entities mentioned (people, organizations, technologies, methods)
2. Abstract topics/themes referenced
3. Whether this requires cross-document synthesis (global=true) or specific fact lookup (global=false)

Global retrieval indicators:
- "across all", "common themes", "compare", "contrast", "overall", "summary"
- Questions about gaps, trends, or patterns
- Questions referencing multiple documents or sources

Return JSON only:
{
  "entities": ["entity1", "entity2"],
  "topics": ["topic1", "topic2"],
  "requiresGlobal": true
}`;

  // Use the faster extraction model for query analysis
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
  const model = genAI.getGenerativeModel({ model: config.extractionModel });
  const result = await model.generateContent(prompt);

  try {
    const cleaned = result.response
      .text()
      .replace(/```json\n?/g, '')
      .replace(/```\n?/g, '')
      .trim();
    return JSON.parse(cleaned);
  } catch {
    // Fallback: treat entire question as a topic
    return {
      entities: [],
      topics: [question],
      requiresGlobal: true,
    };
  }
}

/**
 * Generate a community summary on-demand.
 * This is a core LightRAG optimization: summaries are only generated
 * when a community is actually queried, not during indexing.
 */
async function generateCommunitySummary(
  community: Community,
  graph: KnowledgeGraph,
  config: LightRAGConfig
): Promise<string> {
  const entityDescriptions = community.entityIds
    .map((id) => {
      const entity = (graph as any).entities.get(id);
      return entity ? `- ${entity.name} (${entity.type}): ${entity.description}` : null;
    })
    .filter(Boolean)
    .join('\n');

  const prompt = `Summarize this knowledge cluster in 2-3 sentences.

Entities in this cluster:
${entityDescriptions}

Key topics: ${community.keyTopics.join(', ')}

Write a concise summary capturing what this cluster is about and why these entities are related. Focus on the key insight or theme.`;

  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
  const model = genAI.getGenerativeModel({ model: config.extractionModel });
  const result = await model.generateContent(prompt);

  const summary = result.response.text().trim();
  community.summary = summary; // Cache for future queries
  return summary;
}

/**
 * Standard pgvector similarity search for raw text grounding.
 * Used alongside graph retrieval for maximum context quality.
 */
async function vectorSearch(
  question: string,
  pool: Pool,
  config: LightRAGConfig
): Promise<{ content: string; similarity: number }[]> {
  // Embed the question
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
  const embeddingModel = genAI.getGenerativeModel({
    model: 'text-embedding-004',
  });
  const embResult = await embeddingModel.embedContent(question);
  const queryVector = embResult.embedding.values;

  // Zero-pad to match pgvector column dimensions
  const padded = new Array(config.embeddingDimensions).fill(0);
  for (let i = 0; i < queryVector.length; i++) {
    padded[i] = queryVector[i];
  }

  const vectorStr = `[${padded.join(',')}]`;

  const result = await pool.query(
    `SELECT content, 1 - (embedding <=> $1::vector) AS similarity
     FROM lightrag_chunks
     WHERE embedding IS NOT NULL
     ORDER BY embedding <=> $1::vector
     LIMIT 10`,
    [vectorStr]
  );

  return result.rows;
}

/**
 * Assemble local, global, and vector context into a single string
 * for the final LLM generation call.
 */
function assembleContext(
  localContext: LocalContext[],
  globalContext: GlobalContext[],
  vectorChunks: { content: string; similarity: number }[]
): string {
  const sections: string[] = [];

  // Section 1: Entity-specific knowledge (local)
  if (localContext.length > 0) {
    const entityLines = localContext.map((ctx) => {
      const relLines = ctx.relationships
        .map(
          (r) =>
            `  - ${r.type}: ${r.description} (confidence: ${r.weight.toFixed(2)})`
        )
        .join('\n');
      const neighborNames = ctx.neighborEntities
        .map((n) => n.name)
        .join(', ');

      return `### ${ctx.entity.name} (${ctx.entity.type})
${ctx.entity.description}
Related to: ${neighborNames}
Relationships:
${relLines}`;
    });

    sections.push(`## Entity-Specific Knowledge\n${entityLines.join('\n\n')}`);
  }

  // Section 2: Thematic summaries (global)
  if (globalContext.length > 0) {
    const communityLines = globalContext.map(
      (ctx) =>
        `### ${ctx.community.name}\n${ctx.summary}\nKey topics: ${ctx.community.keyTopics.join(', ')}`
    );

    sections.push(
      `## Cross-Document Themes\n${communityLines.join('\n\n')}`
    );
  }

  // Section 3: Raw text evidence (vector)
  if (vectorChunks.length > 0) {
    const chunkLines = vectorChunks
      .slice(0, 5) // Limit to top 5 for token efficiency
      .map(
        (c, i) =>
          `### Source ${i + 1} (relevance: ${c.similarity.toFixed(3)})\n${c.content}`
      );

    sections.push(`## Source Text Evidence\n${chunkLines.join('\n\n')}`);
  }

  return sections.join('\n\n---\n\n');
}
```

---

## Integration with pgvector (PostgreSQL Schema)

### Database Schema

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- Table 1: Chunks with vector embeddings (standard RAG layer)
-- ============================================================
CREATE TABLE lightrag_chunks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  chunk_index INTEGER NOT NULL,
  token_count INTEGER,
  embedding vector(1536),  -- Gemini 768-dim zero-padded to 1536
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(document_id, chunk_index)
);

-- HNSW index for fast similarity search
CREATE INDEX idx_lightrag_chunks_embedding
  ON lightrag_chunks USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- ============================================================
-- Table 2: Extracted entities with optional embeddings
-- ============================================================
CREATE TABLE lightrag_entities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(500) NOT NULL,
  normalized_name VARCHAR(500) NOT NULL,
  entity_type VARCHAR(50) NOT NULL,
  description TEXT,
  source_chunk_ids UUID[] NOT NULL DEFAULT '{}',
  embedding vector(1536),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(normalized_name)
);

CREATE INDEX idx_lightrag_entities_type ON lightrag_entities(entity_type);
CREATE INDEX idx_lightrag_entities_name ON lightrag_entities(normalized_name);
CREATE INDEX idx_lightrag_entities_embedding
  ON lightrag_entities USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- ============================================================
-- Table 3: Relationships between entities (graph edges)
-- ============================================================
CREATE TABLE lightrag_relationships (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_entity_id UUID NOT NULL REFERENCES lightrag_entities(id) ON DELETE CASCADE,
  target_entity_id UUID NOT NULL REFERENCES lightrag_entities(id) ON DELETE CASCADE,
  relationship_type VARCHAR(50) NOT NULL,
  description TEXT,
  weight REAL NOT NULL DEFAULT 0.5 CHECK (weight >= 0 AND weight <= 1),
  source_chunk_ids UUID[] NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(source_entity_id, target_entity_id, relationship_type)
);

CREATE INDEX idx_lightrag_rel_source ON lightrag_relationships(source_entity_id);
CREATE INDEX idx_lightrag_rel_target ON lightrag_relationships(target_entity_id);
CREATE INDEX idx_lightrag_rel_type ON lightrag_relationships(relationship_type);

-- ============================================================
-- Table 4: Communities (entity clusters)
-- ============================================================
CREATE TABLE lightrag_communities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(500),
  summary TEXT,
  entity_ids UUID[] NOT NULL DEFAULT '{}',
  key_topics TEXT[] NOT NULL DEFAULT '{}',
  coherence_score REAL DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Combined query: search entities by embedding AND graph traversal
-- ============================================================

-- Find entities similar to a query (vector search on entities)
-- Then expand to their neighborhoods (graph traversal)
CREATE OR REPLACE FUNCTION lightrag_local_search(
  query_embedding vector(1536),
  top_k INTEGER DEFAULT 5
)
RETURNS TABLE(
  entity_id UUID,
  entity_name VARCHAR,
  entity_type VARCHAR,
  description TEXT,
  similarity REAL,
  related_entities JSONB
) AS $$
BEGIN
  RETURN QUERY
  WITH matched_entities AS (
    SELECT
      e.id,
      e.name,
      e.entity_type,
      e.description,
      (1 - (e.embedding <=> query_embedding))::REAL AS sim
    FROM lightrag_entities e
    WHERE e.embedding IS NOT NULL
    ORDER BY e.embedding <=> query_embedding
    LIMIT top_k
  ),
  entity_neighborhoods AS (
    SELECT
      me.id AS matched_id,
      jsonb_agg(
        jsonb_build_object(
          'entity_name', neighbor.name,
          'entity_type', neighbor.entity_type,
          'relationship', r.relationship_type,
          'rel_description', r.description,
          'weight', r.weight
        )
      ) AS neighbors
    FROM matched_entities me
    LEFT JOIN lightrag_relationships r
      ON r.source_entity_id = me.id OR r.target_entity_id = me.id
    LEFT JOIN lightrag_entities neighbor
      ON neighbor.id = CASE
        WHEN r.source_entity_id = me.id THEN r.target_entity_id
        ELSE r.source_entity_id
      END
    WHERE neighbor.id IS NOT NULL
    GROUP BY me.id
  )
  SELECT
    me.id,
    me.name,
    me.entity_type,
    me.description,
    me.sim,
    COALESCE(en.neighbors, '[]'::jsonb)
  FROM matched_entities me
  LEFT JOIN entity_neighborhoods en ON en.matched_id = me.id
  ORDER BY me.sim DESC;
END;
$$ LANGUAGE plpgsql;
```

### Persistence Layer

```typescript
// services/lightrag/persistence.ts

import { Pool } from 'pg';
import { v4 as uuidv4 } from 'uuid';

/**
 * Persist the in-memory knowledge graph to PostgreSQL.
 * Uses upsert (ON CONFLICT) for idempotent re-indexing.
 */
async function persistGraph(
  graph: KnowledgeGraph,
  pool: Pool
): Promise<void> {
  const data = graph.toJSON() as {
    entities: Entity[];
    relationships: Relationship[];
    communities: Community[];
  };

  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    // Upsert entities
    for (const entity of data.entities) {
      await client.query(
        `INSERT INTO lightrag_entities (id, name, normalized_name, entity_type, description, source_chunk_ids, metadata)
         VALUES ($1, $2, $3, $4, $5, $6, $7)
         ON CONFLICT (normalized_name)
         DO UPDATE SET
           description = CASE
             WHEN LENGTH(EXCLUDED.description) > LENGTH(lightrag_entities.description)
             THEN EXCLUDED.description
             ELSE lightrag_entities.description
           END,
           source_chunk_ids = (
             SELECT ARRAY(SELECT DISTINCT unnest(lightrag_entities.source_chunk_ids || EXCLUDED.source_chunk_ids))
           )`,
        [
          entity.id,
          entity.name,
          entity.name.toLowerCase().trim(),
          entity.type,
          entity.description,
          entity.sourceChunkIds,
          JSON.stringify(entity.metadata),
        ]
      );
    }

    // Upsert relationships
    for (const rel of data.relationships) {
      await client.query(
        `INSERT INTO lightrag_relationships (id, source_entity_id, target_entity_id, relationship_type, description, weight, source_chunk_ids)
         VALUES ($1, $2, $3, $4, $5, $6, $7)
         ON CONFLICT (source_entity_id, target_entity_id, relationship_type)
         DO UPDATE SET
           weight = LEAST(1, lightrag_relationships.weight + EXCLUDED.weight * 0.3),
           source_chunk_ids = (
             SELECT ARRAY(SELECT DISTINCT unnest(lightrag_relationships.source_chunk_ids || EXCLUDED.source_chunk_ids))
           )`,
        [
          rel.id,
          rel.sourceEntityId,
          rel.targetEntityId,
          rel.type,
          rel.description,
          rel.weight,
          rel.sourceChunkIds,
        ]
      );
    }

    // Upsert communities
    for (const community of data.communities) {
      await client.query(
        `INSERT INTO lightrag_communities (id, name, summary, entity_ids, key_topics, coherence_score)
         VALUES ($1, $2, $3, $4, $5, $6)
         ON CONFLICT (id)
         DO UPDATE SET
           summary = EXCLUDED.summary,
           entity_ids = EXCLUDED.entity_ids,
           key_topics = EXCLUDED.key_topics,
           coherence_score = EXCLUDED.coherence_score,
           updated_at = NOW()`,
        [
          community.id,
          community.name,
          community.summary,
          community.entityIds,
          community.keyTopics,
          community.coherenceScore,
        ]
      );
    }

    await client.query('COMMIT');
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}
```

---

## Use Cases for Document-to-Podcast

### 1. Cross-Document Synthesis

**Scenario:** Instructor uploads 5 research papers for a podcast episode on "AI in Education."

Without LightRAG (standard RAG):
- System retrieves chunks from individual papers
- Cannot identify that Paper A's "adaptive learning" and Paper C's "personalized tutoring" are the same concept
- Podcast script repeats the same idea with different terminology

With LightRAG:
- Entity extraction recognizes both terms map to the same concept
- Community detection groups all "personalized learning" entities across papers
- Global retrieval produces: "Three of the five papers converge on adaptive learning as the primary benefit, while two focus on assessment automation"

### 2. Multi-Hop Questions

**Scenario:** "How does the methodology in the Stanford paper compare to the results in the MIT study?"

LightRAG pipeline:
1. Local retrieval finds entities: "Stanford paper" -> methodology nodes, "MIT study" -> results nodes
2. Graph traversal reveals shared methodology entities (same experimental framework)
3. Context assembly includes both entity neighborhoods plus relevant raw text
4. LLM generates a structured comparison grounded in actual document content

### 3. Topic Clustering for Podcast Segments

**Scenario:** Generate a podcast outline from 20 uploaded sermon transcripts.

LightRAG pipeline:
1. Entity extraction across all transcripts identifies: Bible verses, theological concepts, life applications, illustrations
2. Community detection clusters sermons by theme (e.g., "Grace and Forgiveness" community, "Leadership" community, "Family" community)
3. Each community becomes a podcast segment with on-demand summaries
4. Knowledge gaps identified: "No sermons cover the topic of grief -- consider adding a segment"

### 4. Knowledge Gap Detection

**Scenario:** "What topics are NOT covered in the uploaded curriculum documents?"

LightRAG approach:
1. Build the knowledge graph from all curriculum documents
2. Compare entity types and topics against a reference taxonomy (provided by the instructor or generated from course learning objectives)
3. Identify taxonomy topics with zero or few entity matches
4. Report: "The curriculum covers Chapters 1-8 of the textbook but has no content on Chapter 9 (Ethics) or Chapter 12 (Future Directions)"

---

## Comparison Table

| Feature | Standard RAG | GraphRAG (Microsoft) | LightRAG |
|---------|-------------|---------------------|----------|
| **Token cost (indexing)** | 1x (embedding only) | 10-15x (multi-pass extraction + summarization) | 1-2x (single-pass extraction) |
| **Token cost (querying)** | 1x | 2-3x (community summaries in context) | 1.5x (on-demand summaries) |
| **Multi-hop reasoning** | Poor (chunks are isolated) | Excellent (hierarchical communities) | Good (flat communities + entity traversal) |
| **Cross-document synthesis** | None | Excellent | Good |
| **Setup complexity** | Low (embed + store) | High (extraction + Leiden + summarization) | Medium (extraction + BFS clustering) |
| **Real-time indexing** | Yes (embed new chunks instantly) | Slow (full rebuild for community changes) | Yes (incremental graph updates) |
| **Incremental updates** | Trivial | Requires re-running community detection | Add nodes/edges, re-cluster affected components |
| **Quality ceiling** | Limited by chunk boundaries | Highest (hierarchical global understanding) | 80-90% of GraphRAG quality |
| **Best for** | Factual Q&A, single-document | Research synthesis, large corpora | Most applications, cost-sensitive pipelines |
| **Open-source** | N/A (pattern, not a tool) | Yes (Microsoft) | Yes (28k+ GitHub stars) |
| **Dependencies** | Vector DB only | Vector DB + Graph DB + LLM | Vector DB + LLM (graph in same DB) |

---

## Entity Extraction Prompt Template

This is a production-ready prompt template for Claude or Gemini. It includes few-shot examples for consistent output format.

```typescript
/**
 * Production entity extraction prompt with few-shot examples.
 * Supports both Claude and Gemini models.
 */
function buildProductionExtractionPrompt(
  chunk: string,
  documentTitle: string,
  existingEntities: string[] = []
): string {
  return `You are a knowledge graph construction expert. Extract all meaningful entities and their relationships from the provided text.

## Context
Document: "${documentTitle}"
${existingEntities.length > 0
    ? `Previously extracted entities (reuse these names for consistency): ${existingEntities.join(', ')}`
    : ''
  }

## Entity Types
- PERSON: Named individuals (authors, researchers, historical figures)
- ORGANIZATION: Companies, universities, research groups, institutions
- CONCEPT: Abstract ideas, theories, principles, frameworks
- METHODOLOGY: Research methods, algorithms, experimental designs
- TECHNOLOGY: Software, tools, platforms, programming languages
- EVENT: Conferences, experiments, historical events with dates
- LOCATION: Geographic locations relevant to the content
- METRIC: Specific measurements, statistics, benchmarks, scores
- DOCUMENT: Referenced papers, books, standards, specifications
- TOPIC: High-level subject areas or fields of study

## Relationship Types
- USES: Entity A employs/utilizes Entity B
- CREATED_BY: Entity A was made/authored by Entity B
- PART_OF: Entity A is a component/subset of Entity B
- RELATES_TO: General semantic connection
- CAUSES: Entity A leads to/produces Entity B
- CONTRADICTS: Entity A opposes/conflicts with Entity B
- SUPPORTS: Entity A provides evidence for/validates Entity B
- IMPROVES: Entity A enhances/builds upon Entity B
- COMPARED_TO: Entity A is evaluated against Entity B
- DERIVED_FROM: Entity A originates from/is based on Entity B

## Few-Shot Examples

### Example Input
"The transformer architecture, introduced by Vaswani et al. in 2017, revolutionized natural language processing. Google's BERT model, built on transformers, achieved state-of-the-art results on 11 NLP benchmarks."

### Example Output
{
  "entities": [
    {"name": "Transformer Architecture", "type": "METHODOLOGY", "description": "Neural network architecture based on self-attention, introduced in 2017"},
    {"name": "Vaswani et al.", "type": "PERSON", "description": "Research team that introduced the transformer architecture"},
    {"name": "Natural Language Processing", "type": "TOPIC", "description": "Field of AI dealing with human language understanding and generation"},
    {"name": "BERT", "type": "TECHNOLOGY", "description": "Bidirectional Encoder Representations from Transformers, a language model by Google"},
    {"name": "Google", "type": "ORGANIZATION", "description": "Technology company that developed BERT"}
  ],
  "relationships": [
    {"source": "Transformer Architecture", "target": "Vaswani et al.", "type": "CREATED_BY", "description": "Vaswani et al. introduced the transformer architecture in their 2017 paper", "weight": 1.0},
    {"source": "Transformer Architecture", "target": "Natural Language Processing", "type": "IMPROVES", "description": "Transformers revolutionized the NLP field", "weight": 0.9},
    {"source": "BERT", "target": "Transformer Architecture", "type": "DERIVED_FROM", "description": "BERT is built on the transformer architecture", "weight": 1.0},
    {"source": "BERT", "target": "Google", "type": "CREATED_BY", "description": "Google developed the BERT model", "weight": 1.0}
  ]
}

## Text to Analyze
${chunk}

## Instructions
1. Extract 3-10 entities (prefer specific over generic)
2. Extract all meaningful relationships between extracted entities
3. Reuse entity names from the "Previously extracted entities" list when the same concept appears
4. Assign weights: 1.0 for explicitly stated, 0.7 for strongly implied, 0.4 for loosely connected
5. Return ONLY valid JSON matching the example format above. No markdown fences.`;
}
```

### Self-Reflection Check (Agentic RAG Pattern)

Before generating the final answer, validate that retrieved context is sufficient:

```typescript
/**
 * Self-reflection check: is the retrieved context sufficient to answer the question?
 * Based on Agentic RAG patterns (arXiv 2501.09136).
 *
 * Returns true if context is sufficient, false if we need additional retrieval.
 */
async function isContextSufficient(
  question: string,
  context: string,
  config: LightRAGConfig
): Promise<{ sufficient: boolean; missingInfo: string }> {
  const prompt = `You are a retrieval quality assessor. Given a question and retrieved context, determine if the context contains enough information to answer the question accurately.

Question: "${question}"

Retrieved Context:
${context.slice(0, 3000)} ${context.length > 3000 ? '... [truncated]' : ''}

Evaluate:
1. Does the context contain direct evidence to answer the question?
2. Are there obvious gaps (referenced entities not explained, incomplete comparisons)?
3. Would additional retrieval likely improve the answer quality?

Return JSON:
{
  "sufficient": true/false,
  "missingInfo": "Description of what's missing, or empty string if sufficient"
}`;

  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
  const model = genAI.getGenerativeModel({ model: config.extractionModel });
  const result = await model.generateContent(prompt);

  try {
    const cleaned = result.response
      .text()
      .replace(/```json\n?/g, '')
      .replace(/```\n?/g, '')
      .trim();
    return JSON.parse(cleaned);
  } catch {
    return { sufficient: true, missingInfo: '' };
  }
}
```

---

## Full Indexing Pipeline

```typescript
// services/lightrag/indexer.ts

/**
 * Complete indexing pipeline: documents -> chunks -> embeddings + knowledge graph.
 * Call this when new documents are uploaded.
 */
async function indexDocuments(
  documents: { id: string; title: string; content: string }[],
  pool: Pool,
  config: LightRAGConfig = DEFAULT_CONFIG
): Promise<{ graph: KnowledgeGraph; stats: object }> {
  const graph = new KnowledgeGraph();

  for (const doc of documents) {
    console.log(`[LightRAG] Indexing: ${doc.title}`);

    // Step 1: Chunk the document
    const chunks = chunkText(doc.content, 500);

    for (let i = 0; i < chunks.length; i++) {
      const chunkId = `${doc.id}-chunk-${i}`;

      // Step 2: Embed the chunk (for vector search)
      const embedding = await embedChunk(chunks[i], config);

      // Step 3: Store chunk with embedding
      await pool.query(
        `INSERT INTO lightrag_chunks (id, document_id, content, chunk_index, token_count, embedding)
         VALUES ($1, $2, $3, $4, $5, $6)
         ON CONFLICT (document_id, chunk_index) DO UPDATE SET
           content = EXCLUDED.content,
           embedding = EXCLUDED.embedding`,
        [chunkId, doc.id, chunks[i], i, Math.ceil(chunks[i].length / 4), `[${embedding.join(',')}]`]
      );

      // Step 4: Extract entities and relationships (LLM call)
      const { entities, relationships } = await extractEntitiesAndRelationships(
        chunks[i],
        chunkId,
        config
      );

      // Step 5: Add to graph (with deduplication)
      for (const entity of entities) {
        graph.addEntity(entity);
      }
      for (const rel of relationships) {
        graph.addRelationship(
          (rel as any)._sourceName,
          (rel as any)._targetName,
          rel.type,
          rel.description,
          rel.weight,
          rel.sourceChunkIds
        );
      }
    }
  }

  // Step 6: Detect communities
  const communities = graph.detectCommunities();
  console.log(`[LightRAG] Detected ${communities.length} communities`);

  // Step 7: Persist to PostgreSQL
  await persistGraph(graph, pool);

  const stats = graph.getStats();
  console.log(`[LightRAG] Indexing complete:`, stats);

  return { graph, stats };
}

/**
 * Simple sentence-based chunking with overlap.
 */
function chunkText(text: string, targetTokens: number): string[] {
  const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
  const chunks: string[] = [];
  let current = '';

  for (const sentence of sentences) {
    const combined = current + ' ' + sentence;
    if (combined.length / 4 > targetTokens && current.length > 0) {
      chunks.push(current.trim());
      // Keep last sentence for overlap
      current = sentence;
    } else {
      current = combined;
    }
  }

  if (current.trim()) {
    chunks.push(current.trim());
  }

  return chunks;
}

/**
 * Embed a text chunk using Gemini text-embedding-004.
 * Returns zero-padded 1536-dim vector for pgvector compatibility.
 */
async function embedChunk(
  text: string,
  config: LightRAGConfig
): Promise<number[]> {
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
  const model = genAI.getGenerativeModel({ model: 'text-embedding-004' });
  const result = await model.embedContent(text);
  const raw = result.embedding.values;

  // Zero-pad from 768 to 1536
  const padded = new Array(config.embeddingDimensions).fill(0);
  for (let i = 0; i < raw.length; i++) {
    padded[i] = raw[i];
  }

  return padded;
}
```

---

## When to Use LightRAG vs. Alternatives

### Use Standard RAG When:
- Single-document Q&A only
- Questions are simple factual lookups ("What is X?")
- Budget is extremely tight (no LLM calls during indexing)
- Documents are short (<10 pages each)

### Use LightRAG When:
- Multi-document analysis is needed
- Users ask "compare", "synthesize", "what are the themes" questions
- Cost matters (podcast generation pipeline processing many sources)
- Real-time indexing is needed (users upload docs and query immediately)
- You want graph benefits without a separate graph database

### Use Full GraphRAG When:
- Corpus is massive (1000+ documents) and rarely updated
- Highest possible quality is required regardless of cost
- Hierarchical community understanding is essential
- You have infrastructure budget for batch processing

---

## Research Citations
> **Implementation reference:** pgvector zero-padding pattern from Dominion Flow skill `NOTEBOOKLM_RAG_AI_COURSE_GENERATION.md` -- Gemini 768-dim embeddings zero-padded to 1536 for pgvector column compatibility. Mathematically safe for cosine similarity (zeros contribute nothing to dot product or magnitude).

> **Graph construction reference:** Connected-component community detection adapted from Dominion Flow skill `BIRD_EYE_VIEW_KNOWLEDGE_GRAPH_IMPLEMENTATION.md` -- BFS-based clustering is sufficient for most applications and avoids the complexity of hierarchical Leiden algorithm used by Microsoft GraphRAG.
