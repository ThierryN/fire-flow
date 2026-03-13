---
name: Full-Stack Bible Study Platform
category: patterns-standards
version: 1.0.0
contributed: 2026-02-24
tags: [react, xyflow, prisma, qdrant, bible, theology, theming, node-graphs, tailwind, postgresql]
difficulty: hard
usage_count: 0
success_rate: 100
---

# Full-Stack Bible Study Platform

## Problem

Building a Logos-quality Bible study platform with interactive node graphs (knowledge trees, typology maps), semantic search across Scripture and study notes, AI-powered analysis, interlinear Greek/Hebrew text with Strong's numbers, and a theming system supporting 22+ visual themes. The platform must feel like a scholarly tool -- not a toy -- while remaining accessible to non-technical users.

## Solution Pattern

**React + Vite + @xyflow/react + Tailwind + Express + Prisma/PostgreSQL + Qdrant + Claude/Gemini**

Use @xyflow/react (v12) for interactive node graphs with custom node types. Build a CSS custom properties theme system that supports dozens of themes without CSS duplication. Use Qdrant for semantic search across verse embeddings, cross-references, and study notes. Integrate dual AI providers: Gemini for content generation, Claude for theological analysis.

## Architecture

```
Browser (React + Tailwind + @xyflow/react)
    |
    +-- Theme System (CSS custom properties via useTheme hook)
    +-- Graph Canvas (@xyflow/react with custom nodes/edges)
    +-- Interlinear Viewer (Greek/Hebrew + Strong's)
    +-- Parallelism Viewer (SVG arcs connecting parallel elements)
    +-- Search Interface (semantic search via Qdrant)
    +-- AI Analysis Panel (Claude for exegesis, Gemini for summaries)
    |
Express Backend (TypeScript)
    |
    +-- Prisma ORM --> PostgreSQL
    |   +-- verses, books, chapters
    |   +-- strongs_entries, greek_words, hebrew_words
    |   +-- cross_references, study_notes
    |   +-- knowledge_trees, graph_nodes, graph_edges
    |   +-- themes, user_preferences
    |
    +-- Qdrant (port 6335)
    |   +-- Collection: bible_verses (768d, nomic-embed-text)
    |   +-- Semantic search: verses, notes, cross-refs
    |
    +-- Ollama (nomic-embed-text for embeddings)
    +-- Anthropic SDK (Claude for analysis)
    +-- Google Generative AI SDK (Gemini for generation)
```

## Code Examples

### CSS Custom Properties Theme System

The theme system uses CSS custom properties so every component reads from the same source of truth. Adding a new theme is just adding a new `ThemeDef` object -- zero CSS changes.

```typescript
// src/themes/theme-types.ts
export interface ThemeDef {
  id: string;
  name: string;
  group: "dark" | "light" | "special";
  description: string;
  colors: {
    // Core
    bgPrimary: string;
    bgSecondary: string;
    bgTertiary: string;
    textPrimary: string;
    textSecondary: string;
    textMuted: string;
    // Accent
    accent: string;
    accentHover: string;
    accentSubtle: string;
    // Borders & Surfaces
    border: string;
    borderSubtle: string;
    surface: string;
    surfaceHover: string;
    // Semantic
    success: string;
    warning: string;
    danger: string;
    info: string;
    // Scripture-specific
    verseHighlight: string;
    jesusWords: string;         // Red-letter
    strongsLink: string;
    crossRefLink: string;
    // Graph-specific
    nodeDefault: string;
    nodeSelected: string;
    edgeDefault: string;
    edgeHighlight: string;
  };
}

// src/themes/themes.ts
export const THEMES: Record<string, ThemeDef> = {
  "obsidian": {
    id: "obsidian",
    name: "Obsidian Night",
    group: "dark",
    description: "Deep dark theme for focused study",
    colors: {
      bgPrimary: "#0a0a0f",
      bgSecondary: "#12121a",
      bgTertiary: "#1a1a25",
      textPrimary: "#e4e4e7",
      textSecondary: "#a1a1aa",
      textMuted: "#71717a",
      accent: "#818cf8",
      accentHover: "#6366f1",
      accentSubtle: "rgba(129, 140, 248, 0.1)",
      border: "#27272a",
      borderSubtle: "#1e1e24",
      surface: "#18181f",
      surfaceHover: "#1f1f28",
      success: "#22c55e",
      warning: "#f59e0b",
      danger: "#ef4444",
      info: "#3b82f6",
      verseHighlight: "rgba(129, 140, 248, 0.08)",
      jesusWords: "#ef4444",
      strongsLink: "#818cf8",
      crossRefLink: "#22d3ee",
      nodeDefault: "#27272a",
      nodeSelected: "#818cf8",
      edgeDefault: "#3f3f46",
      edgeHighlight: "#818cf8",
    },
  },
  "parchment": {
    id: "parchment",
    name: "Ancient Parchment",
    group: "light",
    description: "Warm light theme inspired by ancient manuscripts",
    colors: {
      bgPrimary: "#faf6f0",
      bgSecondary: "#f5ede0",
      bgTertiary: "#ece2d0",
      textPrimary: "#2c1810",
      textSecondary: "#5c4033",
      textMuted: "#8b7355",
      accent: "#8b4513",
      accentHover: "#a0522d",
      accentSubtle: "rgba(139, 69, 19, 0.08)",
      border: "#d4c5a9",
      borderSubtle: "#e8dcc8",
      surface: "#f0e8d8",
      surfaceHover: "#e8dcc8",
      success: "#2d6a4f",
      warning: "#b86e00",
      danger: "#9b2226",
      info: "#1b4965",
      verseHighlight: "rgba(139, 69, 19, 0.06)",
      jesusWords: "#9b2226",
      strongsLink: "#8b4513",
      crossRefLink: "#1b4965",
      nodeDefault: "#e8dcc8",
      nodeSelected: "#8b4513",
      edgeDefault: "#c4b594",
      edgeHighlight: "#8b4513",
    },
  },
  // ... 20 more themes (temple-gold, prophetic-purple, garden-green, etc.)
};
```

### useTheme Hook

```tsx
// src/hooks/useTheme.ts
import { useCallback, useEffect, useState } from "react";
import { THEMES, type ThemeDef } from "../themes/themes";

const THEME_STORAGE_KEY = "ministry-llm-theme";

export function useTheme() {
  const [themeId, setThemeId] = useState<string>(() => {
    return localStorage.getItem(THEME_STORAGE_KEY) || "obsidian";
  });

  const theme = THEMES[themeId] || THEMES["obsidian"];

  // Apply CSS custom properties to document root
  useEffect(() => {
    const root = document.documentElement;
    Object.entries(theme.colors).forEach(([key, value]) => {
      // Convert camelCase to kebab-case: bgPrimary -> --bg-primary
      const cssVar = `--${key.replace(/([A-Z])/g, "-$1").toLowerCase()}`;
      root.style.setProperty(cssVar, value);
    });
    // Set meta theme-color for mobile
    document
      .querySelector('meta[name="theme-color"]')
      ?.setAttribute("content", theme.colors.bgPrimary);
    localStorage.setItem(THEME_STORAGE_KEY, themeId);
  }, [theme, themeId]);

  const setTheme = useCallback((id: string) => {
    if (THEMES[id]) setThemeId(id);
  }, []);

  return { theme, themeId, setTheme, allThemes: THEMES };
}
```

### Tailwind Config Using CSS Variables

```typescript
// tailwind.config.ts
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "var(--bg-primary)",
          secondary: "var(--bg-secondary)",
          tertiary: "var(--bg-tertiary)",
        },
        text: {
          primary: "var(--text-primary)",
          secondary: "var(--text-secondary)",
          muted: "var(--text-muted)",
        },
        accent: {
          DEFAULT: "var(--accent)",
          hover: "var(--accent-hover)",
          subtle: "var(--accent-subtle)",
        },
        surface: {
          DEFAULT: "var(--surface)",
          hover: "var(--surface-hover)",
        },
        border: {
          DEFAULT: "var(--border)",
          subtle: "var(--border-subtle)",
        },
        verse: {
          highlight: "var(--verse-highlight)",
          jesus: "var(--jesus-words)",
        },
      },
    },
  },
};
```

### @xyflow/react Custom Node Types

```tsx
// src/components/graph/ConceptNode.tsx
import { Handle, Position, type NodeProps } from "@xyflow/react";

interface ConceptData {
  label: string;
  description: string;
  category: "doctrine" | "person" | "place" | "event" | "symbol";
  verseCount: number;
  selected?: boolean;
}

const CATEGORY_COLORS: Record<string, string> = {
  doctrine: "var(--accent)",
  person: "#22d3ee",
  place: "#22c55e",
  event: "#f59e0b",
  symbol: "#a855f7",
};

export function ConceptNode({ data }: NodeProps<ConceptData>) {
  const borderColor = CATEGORY_COLORS[data.category] || "var(--border)";

  return (
    <div
      className="rounded-lg px-4 py-3 min-w-[160px] shadow-lg transition-all duration-200"
      style={{
        backgroundColor: data.selected ? "var(--node-selected)" : "var(--node-default)",
        border: `2px solid ${borderColor}`,
        color: "var(--text-primary)",
      }}
    >
      <Handle type="target" position={Position.Top} className="!bg-accent !w-2 !h-2" />

      <div className="text-sm font-semibold mb-1">{data.label}</div>
      {data.description && (
        <div className="text-xs opacity-70 mb-2 line-clamp-2">{data.description}</div>
      )}
      <div className="flex items-center gap-1.5 text-xs opacity-50">
        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: borderColor }} />
        <span>{data.category}</span>
        <span className="ml-auto">{data.verseCount} verses</span>
      </div>

      <Handle type="source" position={Position.Bottom} className="!bg-accent !w-2 !h-2" />
    </div>
  );
}

// src/components/graph/GraphCanvas.tsx
import { ReactFlow, Background, Controls, MiniMap, type Node, type Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { ConceptNode } from "./ConceptNode";
import { PassageNode } from "./PassageNode";
import { PersonNode } from "./PersonNode";

const nodeTypes = {
  concept: ConceptNode,
  passage: PassageNode,
  person: PersonNode,
};

interface GraphCanvasProps {
  nodes: Node[];
  edges: Edge[];
  onNodeClick?: (node: Node) => void;
}

export function GraphCanvas({ nodes, edges, onNodeClick }: GraphCanvasProps) {
  return (
    <div className="w-full h-[600px] rounded-xl overflow-hidden border border-border">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodeClick={(_event, node) => onNodeClick?.(node)}
        fitView
        minZoom={0.1}
        maxZoom={2}
        defaultEdgeOptions={{
          style: { stroke: "var(--edge-default)", strokeWidth: 1.5 },
          animated: false,
        }}
      >
        <Background color="var(--border-subtle)" gap={20} />
        <Controls
          className="!bg-surface !border-border !text-text-primary"
          showInteractive={false}
        />
        <MiniMap
          nodeColor="var(--accent)"
          maskColor="rgba(0, 0, 0, 0.7)"
          className="!bg-bg-secondary !border-border"
        />
      </ReactFlow>
    </div>
  );
}
```

### Qdrant Semantic Search Integration

```typescript
// server/services/search.ts
import { QdrantClient } from "@qdrant/js-client-rest";

const qdrant = new QdrantClient({ host: "127.0.0.1", port: 6335 });
const COLLECTION = "bible_verses";

async function embedText(text: string): Promise<number[]> {
  const resp = await fetch("http://127.0.0.1:11434/api/embeddings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: "nomic-embed-text", prompt: text }),
  });
  const data = await resp.json();
  return data.embedding; // 768-dimensional vector
}

export async function semanticSearch(query: string, limit = 10) {
  const vector = await embedText(query);
  const results = await qdrant.search(COLLECTION, {
    vector,
    limit,
    with_payload: true,
    score_threshold: 0.5,
  });

  return results.map((hit) => ({
    reference: hit.payload?.reference as string,
    text: hit.payload?.text as string,
    book: hit.payload?.book as string,
    chapter: hit.payload?.chapter as number,
    verse: hit.payload?.verse as number,
    score: hit.score,
  }));
}

export async function findCrossReferences(verseRef: string, limit = 5) {
  // Search for verses semantically similar to the given reference
  const verseText = await getVerseText(verseRef); // From Prisma
  return semanticSearch(verseText, limit);
}

export async function searchStudyNotes(query: string, userId: string, limit = 10) {
  const vector = await embedText(query);
  return qdrant.search(COLLECTION, {
    vector,
    limit,
    with_payload: true,
    filter: {
      must: [
        { key: "type", match: { value: "study_note" } },
        { key: "user_id", match: { value: userId } },
      ],
    },
  });
}
```

### Prisma Schema for Theological Data

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Verse {
  id         Int      @id @default(autoincrement())
  book       String
  bookOrder  Int
  chapter    Int
  verse      Int
  text       String
  textOriginal String?    // Greek/Hebrew
  translation  String     @default("KJV")

  strongsLinks StrongsLink[]
  crossRefsFrom CrossReference[] @relation("fromVerse")
  crossRefsTo   CrossReference[] @relation("toVerse")
  graphNodes    GraphNode[]

  @@unique([book, chapter, verse, translation])
  @@index([book, chapter])
}

model StrongsEntry {
  id           Int      @id @default(autoincrement())
  number       String   @unique   // "H1234" or "G5678"
  language     String              // "hebrew" or "greek"
  lemma        String              // Original word
  transliteration String
  pronunciation   String?
  definition   String
  usage        String?
  derivation   String?

  links StrongsLink[]

  @@index([language])
}

model StrongsLink {
  id        Int    @id @default(autoincrement())
  verseId   Int
  strongsId Int
  wordIndex Int    // Position of word in verse
  word      String // The English word linked

  verse   Verse        @relation(fields: [verseId], references: [id])
  strongs StrongsEntry @relation(fields: [strongsId], references: [id])

  @@index([verseId])
  @@index([strongsId])
}

model CrossReference {
  id         Int    @id @default(autoincrement())
  fromId     Int
  toId       Int
  type       String @default("parallel") // parallel, quote, allusion, typology
  confidence Float  @default(1.0)

  from Verse @relation("fromVerse", fields: [fromId], references: [id])
  to   Verse @relation("toVerse", fields: [toId], references: [id])

  @@index([fromId])
  @@index([toId])
}

model KnowledgeTree {
  id          Int    @id @default(autoincrement())
  name        String
  description String?
  rootNodeId  Int?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  nodes GraphNode[]
  edges GraphEdge[]
}

model GraphNode {
  id           Int    @id @default(autoincrement())
  treeId       Int
  type         String // "concept", "passage", "person", "place", "event", "symbol"
  label        String
  description  String?
  positionX    Float  @default(0)
  positionY    Float  @default(0)
  metadata     Json?

  verseId      Int?
  verse        Verse?        @relation(fields: [verseId], references: [id])
  tree         KnowledgeTree @relation(fields: [treeId], references: [id])

  edgesFrom    GraphEdge[]   @relation("fromNode")
  edgesTo      GraphEdge[]   @relation("toNode")

  @@index([treeId])
}

model GraphEdge {
  id        Int    @id @default(autoincrement())
  treeId    Int
  fromId    Int
  toId      Int
  label     String?
  type      String @default("relates") // relates, fulfills, prophesies, typifies

  tree KnowledgeTree @relation(fields: [treeId], references: [id])
  from GraphNode     @relation("fromNode", fields: [fromId], references: [id])
  to   GraphNode     @relation("toNode", fields: [toId], references: [id])

  @@index([treeId])
}
```

### Interlinear Text Rendering

```tsx
// src/components/InterlinearVerse.tsx
interface InterlinearWord {
  english: string;
  original: string;       // Greek or Hebrew
  transliteration: string;
  strongsNumber: string;  // "G3056" or "H1697"
  partOfSpeech: string;
}

interface InterlinearVerseProps {
  reference: string;
  words: InterlinearWord[];
  onStrongsClick: (number: string) => void;
}

export function InterlinearVerse({ reference, words, onStrongsClick }: InterlinearVerseProps) {
  return (
    <div className="p-4 bg-surface rounded-lg border border-border">
      <div className="text-sm font-semibold text-accent mb-3">{reference}</div>
      <div className="flex flex-wrap gap-x-4 gap-y-2">
        {words.map((word, i) => (
          <div key={i} className="flex flex-col items-center text-center min-w-[60px]">
            {/* Original language (top) */}
            <span className="text-base font-serif text-text-primary leading-tight"
                  dir={word.strongsNumber.startsWith("H") ? "rtl" : "ltr"}>
              {word.original}
            </span>
            {/* Transliteration */}
            <span className="text-xs text-text-muted italic">{word.transliteration}</span>
            {/* English translation */}
            <span className="text-sm text-text-secondary font-medium">{word.english}</span>
            {/* Strong's number link */}
            <button
              onClick={() => onStrongsClick(word.strongsNumber)}
              className="text-[10px] text-accent hover:text-accent-hover transition-colors cursor-pointer"
            >
              {word.strongsNumber}
            </button>
            {/* Part of speech */}
            <span className="text-[9px] text-text-muted uppercase tracking-wider">
              {word.partOfSpeech}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Parallelism Viewer with SVG Arcs

```tsx
// src/components/ParallelismViewer.tsx
interface ParallelPair {
  lineA: string;
  lineB: string;
  type: "synonymous" | "antithetical" | "synthetic" | "climactic";
}

export function ParallelismViewer({ pairs, reference }: { pairs: ParallelPair[]; reference: string }) {
  const TYPE_COLORS: Record<string, string> = {
    synonymous: "var(--accent)",
    antithetical: "var(--danger)",
    synthetic: "var(--success)",
    climactic: "var(--warning)",
  };

  return (
    <div className="p-4 bg-surface rounded-lg border border-border">
      <h3 className="text-sm font-semibold text-accent mb-3">
        Parallelism in {reference}
      </h3>
      <svg className="w-full" viewBox="0 0 600 200" style={{ minHeight: 120 * pairs.length }}>
        {pairs.map((pair, i) => {
          const y = 60 + i * 100;
          const color = TYPE_COLORS[pair.type];
          return (
            <g key={i}>
              {/* Line A */}
              <text x="50" y={y} fill="var(--text-primary)" fontSize="14" fontFamily="serif">
                {pair.lineA}
              </text>
              {/* Arc connecting parallel elements */}
              <path
                d={`M 30 ${y + 5} C 15 ${y + 30}, 15 ${y + 50}, 30 ${y + 55}`}
                fill="none"
                stroke={color}
                strokeWidth="2"
                strokeDasharray={pair.type === "antithetical" ? "4,4" : "none"}
              />
              {/* Line B */}
              <text x="50" y={y + 60} fill="var(--text-secondary)" fontSize="14" fontFamily="serif">
                {pair.lineB}
              </text>
              {/* Type label */}
              <text x="540" y={y + 30} fill={color} fontSize="10" textAnchor="end"
                    fontWeight="600" textTransform="uppercase">
                {pair.type}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
```

## Implementation Steps

1. **Set up Vite + React + TypeScript + Tailwind** -- Standard scaffold.
2. **Build the theme system first** -- Define ThemeDef, implement useTheme hook, wire CSS custom properties into Tailwind config. This affects every component.
3. **Set up Prisma schema** -- Verses, Strong's entries, cross-references, knowledge trees, graph nodes/edges.
4. **Seed the database** -- Import Bible text, Strong's concordance, cross-reference data.
5. **Embed verses into Qdrant** -- Use nomic-embed-text via Ollama. One vector per verse.
6. **Build the search interface** -- Text input calls backend, backend embeds query, searches Qdrant, returns ranked verses.
7. **Build the interlinear viewer** -- Render word-by-word with Strong's links.
8. **Build the graph canvas** -- @xyflow/react with custom node types. Start with a simple concept graph.
9. **Add AI analysis** -- Gemini for content generation (summaries, outlines), Claude for theological analysis (exegesis, systematic connections).
10. **Build the parallelism viewer** -- SVG-based visual representation of Hebrew poetic structures.
11. **Add knowledge tree CRUD** -- Users can create, edit, and navigate theological concept graphs.
12. **Polish themes** -- Create 22+ themes spanning dark, light, and special categories.

## When to Use

- Building any Bible study or theological research application
- Applications needing interactive node graphs for concept mapping
- Multi-theme applications with 10+ theme variants
- Platforms combining full-text search with semantic/vector search
- Applications rendering multi-script text (Latin, Greek, Hebrew)
- Research tools with cross-referencing between entities

## When NOT to Use

- Simple Bible reader apps -- a static site with text is simpler
- Mobile-first apps -- @xyflow/react is desktop-oriented; consider a simpler graph library for mobile
- Applications without theological content -- the Prisma schema and patterns are domain-specific
- If you only need a theme toggle (dark/light) -- CSS custom properties with 2 themes is simpler

## Common Mistakes

1. **Hardcoding colors instead of using CSS variables** -- Every color must come from `var(--xxx)`. Hardcoded hex values break when users switch themes.
2. **Not setting `dir="rtl"` for Hebrew text** -- Hebrew displays incorrectly without right-to-left direction. Greek does not need RTL.
3. **@xyflow/react v12 import changes** -- v12 renamed imports from `reactflow` to `@xyflow/react`. Old tutorials use wrong package.
4. **Embedding too much text per vector** -- One verse per vector works best for Bible search. Whole chapters dilute semantic specificity.
5. **Not handling Strong's number format** -- Hebrew numbers start with "H" (H1234), Greek with "G" (G5678). Don't mix them up in lookups.
6. **Graph layout without a library** -- Manual positioning is painful. Use dagre for hierarchical layouts or d3-force for organic layouts.
7. **AI hallucinating verse references** -- Always verify AI-generated references against the database. Claude and Gemini both hallucinate verse numbers.
8. **Missing font for original languages** -- Hebrew (Ezra SIL) and Greek (SBL Greek) need specific fonts. System fallbacks often render incorrectly.

## Related Skills

- `realtime-monitoring-dashboard.md` -- Similar React + TypeScript + Tailwind architecture
- `multi-project-autonomous-build.md` -- The methodology used to build this alongside other projects

## References

- Contributed from: **ministry-llm** (`C:\path\to\repos\ministry-llm`)
- @xyflow/react v12 docs: https://reactflow.dev/
- Prisma docs: https://www.prisma.io/docs
- Qdrant JS client: https://github.com/qdrant/js-client-rest
- nomic-embed-text: https://huggingface.co/nomic-ai/nomic-embed-text-v1.5
- Strong's Concordance data: https://github.com/openscriptures/strongs
