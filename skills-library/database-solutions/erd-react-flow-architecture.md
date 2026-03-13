---
name: erd-react-flow-architecture
category: database-solutions
version: 1.0.0
contributed: 2026-03-09
contributor: fire-research
last_updated: 2026-03-09
tags: [react-flow, erd-editor, architecture, tauri, shadcn, typescript, chartdb, drawdb]
difficulty: hard
---

# ERD React Flow Architecture


## Problem

Building a production-quality visual ERD editor with React Flow requires synthesizing patterns from multiple proven implementations. No single OSS project covers the full surface area: ChartDB has the best stack match but lacks multi-dialect DDL generation; DrawDB has gold-standard parsers but uses a custom canvas; React Flow's official DatabaseSchemaNode handles per-column handles but not Crow's Foot notation. A developer starting from scratch will spend weeks discovering patterns that are already solved across these projects.

## Solution Pattern

Combine the best of each reference implementation into a layered architecture:

1. **Data Model** (DrawDB pattern) — Dialect-neutral JSON as the single source of truth
2. **React Flow Visualization** (ChartDB + official DatabaseSchemaNode) — Custom node/edge types with per-column handles
3. **Parser/Generator** (DrawDB pattern) — Separate parser and generator per SQL dialect, all round-tripping through the JSON model
4. **Persistence** (Tauri + Dexie.js fallback) — File system for desktop, IndexedDB for web
5. **MCP Integration** (ERFlow pattern) — Expose schema operations as MCP tools for NL editing

---

## Recommended Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Desktop shell | Tauri 2.x | Rust backend, file system access, <10MB binary |
| UI framework | React 18+ (Vite) | ChartDB uses this exact stack |
| Canvas | React Flow (v12+) | Declarative node/edge system, built-in controls |
| Component library | shadcn/ui | ChartDB + NextERD both use it, Tailwind-based |
| State management | Zustand | React Flow's recommended store, ChartDB uses it |
| Local persistence (web) | Dexie.js (IndexedDB) | ChartDB pattern — instant save, no backend needed |
| Local persistence (desktop) | Tauri fs API | Native file dialogs, .erd.json files |
| DDL parsing | node-sql-parser | Bidirectional SQL-to-AST, multi-dialect |
| Type safety | TypeScript (strict) | All reference implementations use TS |

---

## Data Model

The central JSON model is the most critical architectural decision. Every feature — rendering, parsing, exporting, undo/redo — reads from and writes to this model. DrawDB's approach of a dialect-neutral intermediate representation is the proven pattern.

```typescript
// ============================================================
// Core ERD Data Model — dialect-neutral JSON
// ============================================================

/** Top-level document — serialized as .erd.json */
export interface ERDDocument {
  version: '1.0.0';
  name: string;
  description?: string;
  createdAt: string;       // ISO 8601
  updatedAt: string;
  /** Active notation mode affects rendering only, not the model */
  notation: 'crowsfoot' | 'chen';
  /** Target dialect for DDL export */
  dialect: SQLDialect;
  tables: Table[];
  relationships: Relationship[];
  /** Diagram metadata — positions, viewport, etc. */
  diagram: DiagramMeta;
}

export type SQLDialect = 'postgresql' | 'mysql' | 'sqlite' | 'mariadb' | 'mssql';

export interface Table {
  id: string;              // nanoid or cuid
  name: string;
  schema?: string;         // 'public', 'dbo', etc.
  comment?: string;
  columns: Column[];
  indexes: Index[];
  /** Chen-mode only: which columns to render as separate oval nodes */
  chenAttributeDisplay?: 'inline' | 'ovals';
}

export interface Column {
  id: string;
  name: string;
  type: string;            // Raw SQL type string: 'VARCHAR(255)', 'INTEGER', etc.
  isPrimaryKey: boolean;
  isForeignKey: boolean;
  isNullable: boolean;
  isUnique: boolean;
  isAutoIncrement: boolean;
  defaultValue?: string;
  comment?: string;
  /** For composite PKs — order within the key */
  pkOrdinal?: number;
  /** FK reference (also represented in Relationship[], but stored here for column-level rendering) */
  references?: {
    tableId: string;
    columnId: string;
  };
}

export interface Index {
  id: string;
  name: string;
  columns: string[];       // Column IDs
  isUnique: boolean;
  type?: 'btree' | 'hash' | 'gin' | 'gist';
}

export interface Relationship {
  id: string;
  name?: string;           // e.g., 'fk_orders_customer'
  sourceTableId: string;
  sourceColumnId: string;
  targetTableId: string;
  targetColumnId: string;
  /** Cardinality at source end */
  sourceCardinality: Cardinality;
  /** Cardinality at target end */
  targetCardinality: Cardinality;
  /** ON DELETE behavior */
  onDelete: ReferentialAction;
  /** ON UPDATE behavior */
  onUpdate: ReferentialAction;
}

export type Cardinality = 'exactly-one' | 'zero-or-one' | 'one-or-many' | 'zero-or-many';

export type ReferentialAction = 'CASCADE' | 'SET NULL' | 'SET DEFAULT' | 'RESTRICT' | 'NO ACTION';

export interface DiagramMeta {
  /** Per-table positions on the canvas */
  positions: Record<string, { x: number; y: number }>;
  /** Viewport state for restoring pan/zoom */
  viewport: {
    x: number;
    y: number;
    zoom: number;
  };
  /** Grid snap settings */
  gridSize: number;
  snapToGrid: boolean;
}
```

### JSON Serialization Format (.erd.json)

```json
{
  "version": "1.0.0",
  "name": "E-Commerce Schema",
  "notation": "crowsfoot",
  "dialect": "postgresql",
  "tables": [
    {
      "id": "tbl_001",
      "name": "users",
      "columns": [
        { "id": "col_001", "name": "id", "type": "UUID", "isPrimaryKey": true, "isForeignKey": false, "isNullable": false, "isUnique": true, "isAutoIncrement": false, "defaultValue": "gen_random_uuid()" },
        { "id": "col_002", "name": "email", "type": "VARCHAR(255)", "isPrimaryKey": false, "isForeignKey": false, "isNullable": false, "isUnique": true, "isAutoIncrement": false },
        { "id": "col_003", "name": "created_at", "type": "TIMESTAMPTZ", "isPrimaryKey": false, "isForeignKey": false, "isNullable": false, "isUnique": false, "isAutoIncrement": false, "defaultValue": "NOW()" }
      ],
      "indexes": []
    }
  ],
  "relationships": [],
  "diagram": {
    "positions": { "tbl_001": { "x": 100, "y": 200 } },
    "viewport": { "x": 0, "y": 0, "zoom": 1 },
    "gridSize": 20,
    "snapToGrid": true
  }
}
```

---

## React Flow Node Types

### Table Node (Crow's Foot Mode) — Primary

Based on React Flow's official `DatabaseSchemaNode` pattern, extended with PK/FK icons, nullable indicators, and per-column source/target handles for field-level connections.

```tsx
// components/nodes/TableNode.tsx
import { memo } from 'react';
import { NodeProps, Handle, Position } from '@xyflow/react';
import { KeyRound, Link2, CircleDot } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Table, Column } from '@/types/erd';

interface TableNodeData {
  table: Table;
  isSelected: boolean;
}

export const TableNode = memo(({ data, selected }: NodeProps<TableNodeData>) => {
  const { table } = data;
  const pkColumns = table.columns.filter(c => c.isPrimaryKey);
  const regularColumns = table.columns.filter(c => !c.isPrimaryKey);

  return (
    <div
      className={cn(
        'rounded-lg border bg-card text-card-foreground shadow-sm min-w-[220px]',
        'transition-shadow duration-200',
        selected && 'ring-2 ring-primary shadow-lg',
      )}
    >
      {/* Table header */}
      <div className="flex items-center gap-2 px-3 py-2 bg-muted/50 rounded-t-lg border-b">
        <CircleDot className="h-4 w-4 text-muted-foreground" />
        <span className="font-semibold text-sm">{table.name}</span>
        <span className="ml-auto text-xs text-muted-foreground">
          {table.columns.length} cols
        </span>
      </div>

      {/* Primary key columns — always on top */}
      {pkColumns.map((col) => (
        <ColumnRow key={col.id} column={col} tableId={table.id} isPk />
      ))}

      {/* Separator between PK and regular columns */}
      {pkColumns.length > 0 && regularColumns.length > 0 && (
        <div className="border-t border-dashed" />
      )}

      {/* Regular columns */}
      {regularColumns.map((col) => (
        <ColumnRow key={col.id} column={col} tableId={table.id} />
      ))}
    </div>
  );
});

TableNode.displayName = 'TableNode';

/** Individual column row with per-column handles */
function ColumnRow({
  column,
  tableId,
  isPk = false,
}: {
  column: Column;
  tableId: string;
  isPk?: boolean;
}) {
  // Handle IDs follow the pattern: {tableId}.{columnId}
  // This enables field-level edge connections
  const handleId = `${tableId}.${column.id}`;

  return (
    <div className="relative flex items-center gap-2 px-3 py-1.5 text-xs hover:bg-muted/30 group">
      {/* Source handle — left side (target for incoming FKs) */}
      <Handle
        type="target"
        position={Position.Left}
        id={`${handleId}-target`}
        className="!w-2 !h-2 !bg-primary/60 !border-primary"
        style={{ top: '50%' }}
      />

      {/* Column icon */}
      {isPk ? (
        <KeyRound className="h-3.5 w-3.5 text-amber-500 shrink-0" />
      ) : column.isForeignKey ? (
        <Link2 className="h-3.5 w-3.5 text-blue-500 shrink-0" />
      ) : (
        <span className="w-3.5 shrink-0" />
      )}

      {/* Column name */}
      <span className={cn('font-mono', isPk && 'font-semibold')}>
        {column.name}
      </span>

      {/* Column type */}
      <span className="ml-auto text-muted-foreground font-mono">
        {column.type}
        {!column.isNullable && (
          <span className="text-red-400 ml-1" title="NOT NULL">*</span>
        )}
      </span>

      {/* Source handle — right side (source for outgoing FKs) */}
      <Handle
        type="source"
        position={Position.Right}
        id={`${handleId}-source`}
        className="!w-2 !h-2 !bg-primary/60 !border-primary"
        style={{ top: '50%' }}
      />
    </div>
  );
}
```

### Entity Node (Chen Mode)

In Chen notation, entities are rectangles and attributes are separate oval nodes connected by lines. The same data model renders differently.

```tsx
// components/nodes/ChenEntityNode.tsx
import { memo } from 'react';
import { NodeProps, Handle, Position } from '@xyflow/react';
import { cn } from '@/lib/utils';

interface ChenEntityNodeData {
  name: string;
  isWeak: boolean;
}

export const ChenEntityNode = memo(({ data, selected }: NodeProps<ChenEntityNodeData>) => (
  <div
    className={cn(
      'px-6 py-3 bg-card border-2 rounded-sm text-center font-semibold',
      data.isWeak && 'border-double border-4',
      selected && 'ring-2 ring-primary',
    )}
  >
    {data.name}
    {/* Handles on all 4 sides for flexible attribute/relationship connections */}
    <Handle type="source" position={Position.Top} id="top" />
    <Handle type="source" position={Position.Right} id="right" />
    <Handle type="source" position={Position.Bottom} id="bottom" />
    <Handle type="source" position={Position.Left} id="left" />
  </div>
));

ChenEntityNode.displayName = 'ChenEntityNode';

// components/nodes/ChenAttributeNode.tsx
export const ChenAttributeNode = memo(({ data, selected }: NodeProps<{
  name: string;
  variant: 'simple' | 'key' | 'multivalued' | 'derived' | 'composite' | 'partial-key';
}>) => (
  <div
    className={cn(
      'px-4 py-2 rounded-full bg-card text-center text-sm border',
      data.variant === 'key' && 'font-bold [&>span]:underline',
      data.variant === 'multivalued' && 'border-double border-4',
      data.variant === 'derived' && 'border-dashed',
      data.variant === 'partial-key' && 'font-bold [&>span]:underline [&>span]:decoration-dashed',
      selected && 'ring-2 ring-primary',
    )}
  >
    <span>{data.name}</span>
    <Handle type="target" position={Position.Top} id="top" />
    <Handle type="target" position={Position.Bottom} id="bottom" />
    <Handle type="target" position={Position.Left} id="left" />
    <Handle type="target" position={Position.Right} id="right" />
  </div>
));

ChenAttributeNode.displayName = 'ChenAttributeNode';

// components/nodes/ChenRelationshipNode.tsx (Diamond shape)
export const ChenRelationshipNode = memo(({ data, selected }: NodeProps<{
  name: string;
  isIdentifying: boolean;
}>) => (
  <div className="relative" style={{ width: 120, height: 80 }}>
    <svg viewBox="0 0 120 80" className="absolute inset-0">
      <polygon
        points="60,2 118,40 60,78 2,40"
        className={cn(
          'fill-card stroke-foreground',
          data.isIdentifying ? 'stroke-[3]' : 'stroke-[1.5]',
          selected && 'stroke-primary',
        )}
      />
      {data.isIdentifying && (
        <polygon
          points="60,8 112,40 60,72 8,40"
          className="fill-none stroke-foreground stroke-[1.5]"
        />
      )}
    </svg>
    <span className="absolute inset-0 flex items-center justify-center text-xs font-medium">
      {data.name}
    </span>
    <Handle type="source" position={Position.Top} id="top" style={{ left: '50%' }} />
    <Handle type="source" position={Position.Right} id="right" style={{ top: '50%' }} />
    <Handle type="source" position={Position.Bottom} id="bottom" style={{ left: '50%' }} />
    <Handle type="source" position={Position.Left} id="left" style={{ top: '50%' }} />
  </div>
));

ChenRelationshipNode.displayName = 'ChenRelationshipNode';
```

### Node Type Registration

```tsx
// lib/node-types.ts
import { TableNode } from '@/components/nodes/TableNode';
import { ChenEntityNode, ChenAttributeNode, ChenRelationshipNode } from '@/components/nodes/ChenNodes';

export const crowsFootNodeTypes = {
  table: TableNode,
} as const;

export const chenNodeTypes = {
  entity: ChenEntityNode,
  attribute: ChenAttributeNode,
  relationship: ChenRelationshipNode,
} as const;
```

---

## React Flow Edge Types

### Crow's Foot Edge — Custom SVG Markers

The key insight from `relliv/crows-foot-notations`: define 4 SVG marker symbols in a `<defs>` block, then reference them as `markerStart`/`markerEnd` on React Flow edges.

```tsx
// components/edges/CrowsFootMarkers.tsx
/**
 * SVG marker definitions for Crow's Foot notation.
 * Render this ONCE inside the ReactFlow component.
 *
 * 4 cardinality markers:
 *   exactly-one:   --|--     (single perpendicular line)
 *   zero-or-one:   --O|--   (circle + perpendicular line)
 *   one-or-many:   --<|--   (fork + perpendicular line)
 *   zero-or-many:  --O<--   (circle + fork)
 */
export function CrowsFootMarkerDefs() {
  return (
    <svg style={{ position: 'absolute', width: 0, height: 0 }}>
      <defs>
        {/* Exactly One: perpendicular line */}
        <marker
          id="cf-exactly-one"
          viewBox="0 0 20 20"
          refX="18"
          refY="10"
          markerWidth="20"
          markerHeight="20"
          orient="auto-start-reverse"
          markerUnits="userSpaceOnUse"
        >
          <line x1="18" y1="2" x2="18" y2="18" stroke="currentColor" strokeWidth="2" />
          <line x1="12" y1="2" x2="12" y2="18" stroke="currentColor" strokeWidth="2" />
        </marker>

        {/* Zero or One: circle + perpendicular line */}
        <marker
          id="cf-zero-or-one"
          viewBox="0 0 30 20"
          refX="28"
          refY="10"
          markerWidth="30"
          markerHeight="20"
          orient="auto-start-reverse"
          markerUnits="userSpaceOnUse"
        >
          <circle cx="10" cy="10" r="6" fill="white" stroke="currentColor" strokeWidth="2" />
          <line x1="28" y1="2" x2="28" y2="18" stroke="currentColor" strokeWidth="2" />
        </marker>

        {/* One or Many: fork (crow's foot) + perpendicular line */}
        <marker
          id="cf-one-or-many"
          viewBox="0 0 24 20"
          refX="22"
          refY="10"
          markerWidth="24"
          markerHeight="20"
          orient="auto-start-reverse"
          markerUnits="userSpaceOnUse"
        >
          {/* Perpendicular line */}
          <line x1="22" y1="2" x2="22" y2="18" stroke="currentColor" strokeWidth="2" />
          {/* Fork: three lines diverging from right to left */}
          <line x1="16" y1="10" x2="4" y2="2" stroke="currentColor" strokeWidth="1.5" />
          <line x1="16" y1="10" x2="4" y2="10" stroke="currentColor" strokeWidth="1.5" />
          <line x1="16" y1="10" x2="4" y2="18" stroke="currentColor" strokeWidth="1.5" />
        </marker>

        {/* Zero or Many: circle + fork */}
        <marker
          id="cf-zero-or-many"
          viewBox="0 0 34 20"
          refX="32"
          refY="10"
          markerWidth="34"
          markerHeight="20"
          orient="auto-start-reverse"
          markerUnits="userSpaceOnUse"
        >
          {/* Circle (zero) */}
          <circle cx="8" cy="10" r="6" fill="white" stroke="currentColor" strokeWidth="2" />
          {/* Fork: three lines diverging */}
          <line x1="26" y1="10" x2="16" y2="2" stroke="currentColor" strokeWidth="1.5" />
          <line x1="26" y1="10" x2="16" y2="10" stroke="currentColor" strokeWidth="1.5" />
          <line x1="26" y1="10" x2="16" y2="18" stroke="currentColor" strokeWidth="1.5" />
        </marker>
      </defs>
    </svg>
  );
}

/** Map cardinality enum to marker ID */
export function getMarkerId(cardinality: Cardinality): string {
  const map: Record<Cardinality, string> = {
    'exactly-one': 'url(#cf-exactly-one)',
    'zero-or-one': 'url(#cf-zero-or-one)',
    'one-or-many': 'url(#cf-one-or-many)',
    'zero-or-many': 'url(#cf-zero-or-many)',
  };
  return map[cardinality];
}
```

### Crow's Foot Edge Component

```tsx
// components/edges/CrowsFootEdge.tsx
import { memo } from 'react';
import { EdgeProps, getBezierPath } from '@xyflow/react';
import { getMarkerId } from './CrowsFootMarkers';
import type { Cardinality } from '@/types/erd';

interface CrowsFootEdgeData {
  sourceCardinality: Cardinality;
  targetCardinality: Cardinality;
  relationshipName?: string;
}

export const CrowsFootEdge = memo(({
  id,
  sourceX, sourceY,
  targetX, targetY,
  sourcePosition, targetPosition,
  data,
  selected,
}: EdgeProps<CrowsFootEdgeData>) => {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX, sourceY, targetX, targetY,
    sourcePosition, targetPosition,
  });

  return (
    <>
      {/* Invisible wider path for easier click/hover targeting */}
      <path
        d={edgePath}
        fill="none"
        stroke="transparent"
        strokeWidth={20}
        className="react-flow__edge-interaction"
      />
      {/* Visible edge line */}
      <path
        id={id}
        d={edgePath}
        fill="none"
        stroke={selected ? 'hsl(var(--primary))' : 'hsl(var(--muted-foreground))'}
        strokeWidth={selected ? 2.5 : 1.5}
        markerStart={data ? getMarkerId(data.sourceCardinality) : undefined}
        markerEnd={data ? getMarkerId(data.targetCardinality) : undefined}
      />
      {/* Relationship label */}
      {data?.relationshipName && (
        <foreignObject
          width={120}
          height={24}
          x={labelX - 60}
          y={labelY - 12}
          requiredExtensions="http://www.w3.org/1999/xhtml"
        >
          <div className="text-[10px] text-muted-foreground text-center bg-background/80 rounded px-1">
            {data.relationshipName}
          </div>
        </foreignObject>
      )}
    </>
  );
});

CrowsFootEdge.displayName = 'CrowsFootEdge';
```

### Chen Notation Edge

```tsx
// components/edges/ChenEdge.tsx
// Simpler edge — cardinality labels as text, participation as line style
import { memo } from 'react';
import { EdgeProps, getStraightPath } from '@xyflow/react';

interface ChenEdgeData {
  cardinality?: string;    // '1', 'M', 'N'
  isTotalParticipation: boolean;
}

export const ChenEdge = memo(({
  sourceX, sourceY, targetX, targetY, data, id,
}: EdgeProps<ChenEdgeData>) => {
  const [path, labelX, labelY] = getStraightPath({
    sourceX, sourceY, targetX, targetY,
  });

  return (
    <>
      <path
        id={id}
        d={path}
        fill="none"
        stroke="hsl(var(--foreground))"
        strokeWidth={data?.isTotalParticipation ? 3 : 1.5}
      />
      {data?.cardinality && (
        <text x={labelX} y={labelY - 8} textAnchor="middle" className="text-xs fill-foreground">
          {data.cardinality}
        </text>
      )}
    </>
  );
});

ChenEdge.displayName = 'ChenEdge';
```

### Edge Type Registration

```tsx
// lib/edge-types.ts
import { CrowsFootEdge } from '@/components/edges/CrowsFootEdge';
import { ChenEdge } from '@/components/edges/ChenEdge';

export const crowsFootEdgeTypes = {
  crowsfoot: CrowsFootEdge,
} as const;

export const chenEdgeTypes = {
  chen: ChenEdge,
} as const;
```

---

## Canvas Features

### Core React Flow Setup

```tsx
// components/ERDCanvas.tsx
import { useCallback } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Panel,
  type OnConnect,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { crowsFootNodeTypes } from '@/lib/node-types';
import { crowsFootEdgeTypes } from '@/lib/edge-types';
import { CrowsFootMarkerDefs } from '@/components/edges/CrowsFootMarkers';
import { useERDStore } from '@/store/erd-store';

export function ERDCanvas() {
  const { nodes, edges, onNodesChange, onEdgesChange } = useERDStore();

  const onConnect: OnConnect = useCallback((connection) => {
    // Create relationship from connection
    // Parse handle IDs to get table + column: "tbl_001.col_002-source"
    useERDStore.getState().addRelationship(connection);
  }, []);

  return (
    <div className="h-full w-full">
      <CrowsFootMarkerDefs />
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={crowsFootNodeTypes}
        edgeTypes={crowsFootEdgeTypes}
        snapToGrid
        snapGrid={[20, 20]}
        fitView
        minZoom={0.1}
        maxZoom={4}
        deleteKeyCode={['Backspace', 'Delete']}
        multiSelectionKeyCode="Shift"
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
        <Controls showInteractive={false} />
        <MiniMap
          nodeStrokeWidth={3}
          zoomable
          pannable
          className="!bg-muted/50 !border-border"
        />
        <Panel position="top-right">
          {/* Toolbar: add table, import, export, undo/redo, notation toggle */}
        </Panel>
      </ReactFlow>
    </div>
  );
}
```

### Zustand Store with Undo/Redo

```typescript
// store/erd-store.ts
import { create } from 'zustand';
import { temporal } from 'zundo';
import {
  type Node, type Edge,
  applyNodeChanges, applyEdgeChanges,
  type NodeChange, type EdgeChange,
} from '@xyflow/react';
import { nanoid } from 'nanoid';
import type { ERDDocument, Table, Relationship } from '@/types/erd';

interface ERDState {
  document: ERDDocument;
  nodes: Node[];
  edges: Edge[];
  // React Flow handlers
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  // ERD operations
  addTable: (table: Table) => void;
  updateTable: (tableId: string, updates: Partial<Table>) => void;
  removeTable: (tableId: string) => void;
  addRelationship: (connection: any) => void;
  removeRelationship: (relId: string) => void;
  // I/O
  loadDocument: (doc: ERDDocument) => void;
  toDocument: () => ERDDocument;
  // Sync: convert ERDDocument <-> React Flow nodes/edges
  syncFromModel: () => void;
}

/**
 * Zustand store wrapped with zundo for undo/redo.
 * Ctrl+Z / Ctrl+Shift+Z call useTemporalStore().undo() / .redo()
 */
export const useERDStore = create<ERDState>()(
  temporal(
    (set, get) => ({
      document: createEmptyDocument(),
      nodes: [],
      edges: [],

      onNodesChange: (changes) => {
        set({ nodes: applyNodeChanges(changes, get().nodes) });
        // Sync position changes back to document.diagram.positions
        for (const change of changes) {
          if (change.type === 'position' && change.position) {
            get().document.diagram.positions[change.id] = change.position;
          }
        }
      },

      onEdgesChange: (changes) => {
        set({ edges: applyEdgeChanges(changes, get().edges) });
      },

      addTable: (table) => {
        const doc = get().document;
        // Immutable update — required for zundo temporal middleware undo/redo
        set({ document: { ...doc, tables: [...doc.tables, table] } });
        get().syncFromModel();
      },

      updateTable: (tableId, updates) => {
        const doc = get().document;
        // Immutable update — map produces new array, preserving zundo snapshots
        set({
          document: {
            ...doc,
            tables: doc.tables.map(t =>
              t.id === tableId ? { ...t, ...updates } : t
            ),
          },
        });
        get().syncFromModel();
      },

      removeTable: (tableId) => {
        const doc = get().document;
        // Immutable update — filter + destructure, never mutate doc in-place
        const { [tableId]: _, ...remainingPositions } = doc.diagram.positions;
        set({
          document: {
            ...doc,
            tables: doc.tables.filter(t => t.id !== tableId),
            relationships: doc.relationships.filter(
              r => r.sourceTableId !== tableId && r.targetTableId !== tableId
            ),
            diagram: { ...doc.diagram, positions: remainingPositions },
          },
        });
        get().syncFromModel();
      },

      addRelationship: (connection) => {
        // Parse handle IDs: "tbl_001.col_002-source" -> tableId="tbl_001", columnId="col_002"
        const parseHandle = (handleId: string) => {
          const [combined] = handleId.split('-');
          const [tableId, columnId] = combined.split('.');
          return { tableId, columnId };
        };
        const source = parseHandle(connection.sourceHandle);
        const target = parseHandle(connection.targetHandle);
        const rel: Relationship = {
          id: nanoid(),
          sourceTableId: source.tableId,
          sourceColumnId: source.columnId,
          targetTableId: target.tableId,
          targetColumnId: target.columnId,
          sourceCardinality: 'exactly-one',
          targetCardinality: 'zero-or-many',
          onDelete: 'NO ACTION',
          onUpdate: 'NO ACTION',
        };
        const doc = get().document;
        doc.relationships.push(rel);
        set({ document: { ...doc } });
        get().syncFromModel();
      },

      removeRelationship: (relId) => {
        const doc = get().document;
        doc.relationships = doc.relationships.filter(r => r.id !== relId);
        set({ document: { ...doc } });
        get().syncFromModel();
      },

      loadDocument: (doc) => {
        set({ document: doc });
        get().syncFromModel();
      },

      toDocument: () => {
        const state = get();
        // Sync current positions back to document
        for (const node of state.nodes) {
          if (node.position) {
            state.document.diagram.positions[node.id] = node.position;
          }
        }
        state.document.updatedAt = new Date().toISOString();
        return structuredClone(state.document);
      },

      syncFromModel: () => {
        const doc = get().document;
        const nodes: Node[] = doc.tables.map(table => ({
          id: table.id,
          type: 'table',
          position: doc.diagram.positions[table.id] ?? { x: 0, y: 0 },
          data: { table, isSelected: false },
        }));
        const edges: Edge[] = doc.relationships.map(rel => ({
          id: rel.id,
          source: rel.sourceTableId,
          target: rel.targetTableId,
          sourceHandle: `${rel.sourceTableId}.${rel.sourceColumnId}-source`,
          targetHandle: `${rel.targetTableId}.${rel.targetColumnId}-target`,
          type: 'crowsfoot',
          data: {
            sourceCardinality: rel.sourceCardinality,
            targetCardinality: rel.targetCardinality,
            relationshipName: rel.name,
          },
        }));
        set({ nodes, edges });
      },
    }),
    {
      // zundo: limit undo history to 100 steps
      limit: 100,
      // Only track meaningful changes (not every mouse move)
      partialize: (state) => ({
        document: state.document,
      }),
    }
  )
);

function createEmptyDocument(): ERDDocument {
  return {
    version: '1.0.0',
    name: 'Untitled',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    notation: 'crowsfoot',
    dialect: 'postgresql',
    tables: [],
    relationships: [],
    diagram: {
      positions: {},
      viewport: { x: 0, y: 0, zoom: 1 },
      gridSize: 20,
      snapToGrid: true,
    },
  };
}
```

### Auto-Layout (dagre)

```typescript
// lib/auto-layout.ts
import dagre from '@dagrejs/dagre';
import type { Node, Edge } from '@xyflow/react';

/**
 * Auto-layout tables using dagre graph algorithm.
 * ChartDB and Liam ERD both use dagre for auto-layout.
 */
export function autoLayout(
  nodes: Node[],
  edges: Edge[],
  direction: 'TB' | 'LR' = 'LR',
): Node[] {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({
    rankdir: direction,
    nodesep: 60,      // horizontal spacing
    ranksep: 100,     // vertical spacing between ranks
    edgesep: 20,
    marginx: 40,
    marginy: 40,
  });

  // Estimate node dimensions (table height = header + rows * 28px)
  for (const node of nodes) {
    const colCount = node.data?.table?.columns?.length ?? 4;
    const height = 40 + colCount * 28; // header + rows
    g.setNode(node.id, { width: 240, height });
  }

  for (const edge of edges) {
    g.setEdge(edge.source, edge.target);
  }

  dagre.layout(g);

  return nodes.map(node => {
    const pos = g.node(node.id);
    return {
      ...node,
      position: { x: pos.x - 120, y: pos.y - (pos.height / 2) },
    };
  });
}
```

### Performance: Virtual Rendering for 100+ Tables

JointJS insight: when table count exceeds ~50, render only visible nodes. React Flow v12 handles this natively with `nodeExtent` and built-in viewport culling. Additional optimizations:

```typescript
// Performance patterns for large schemas

// 1. Memoize node components (already done with memo())
// 2. Use nodeTypes/edgeTypes outside of the component to prevent re-registration
// 3. Debounce position sync (don't write to store on every pixel of drag)
import { useDebouncedCallback } from 'use-debounce';

const debouncedSync = useDebouncedCallback(() => {
  useERDStore.getState().syncPositionsToDocument();
}, 200);

// 4. For 100+ tables, collapse columns by default and expand on click
// 5. Use React Flow's `hidden` prop to hide tables not matching a filter
// 6. Batch node updates: applyNodeChanges handles arrays efficiently
```

---

## Parser/Generator Architecture (DrawDB Pattern)

DrawDB's architecture is the gold standard: separate parser and generator for each SQL dialect, all converting to/from a central JSON model. This enables round-tripping: `DDL -> JSON -> DDL` without information loss.

```
  +----------------+     +---------------+     +--------------------+
  |  MySQL DDL     |---->|               |---->|  MySQL DDL         |
  +----------------+     |               |     +--------------------+
  +----------------+     |   Central     |     +--------------------+
  | PostgreSQL     |---->|   JSON        |---->|  PostgreSQL DDL    |
  +----------------+     |   Model       |     +--------------------+
  +----------------+     | (ERDDocument) |     +--------------------+
  |  SQLite DDL    |---->|               |---->|  SQLite DDL        |
  +----------------+     |               |     +--------------------+
  +----------------+     |               |     +--------------------+
  |  Prisma .psl   |---->|               |---->|  DBML              |
  +----------------+     +---------------+     +--------------------+
```

### Parser Interface

```typescript
// lib/parsers/types.ts

/** All parsers convert their input format to ERDDocument */
export interface DDLParser {
  dialect: SQLDialect;
  /** Parse DDL string into document model */
  parse(ddl: string): ERDDocument;
  /** Supported file extensions */
  extensions: string[];
}

/** All generators convert ERDDocument to their output format */
export interface DDLGenerator {
  dialect: SQLDialect;
  /** Generate DDL string from document model */
  generate(doc: ERDDocument): string;
  /** File extension for export */
  extension: string;
}
```

### PostgreSQL Parser (using node-sql-parser)

```typescript
// lib/parsers/postgres-parser.ts
import { Parser } from 'node-sql-parser';
import type { ERDDocument, Table, Column, Relationship } from '@/types/erd';
import { nanoid } from 'nanoid';

const sqlParser = new Parser();

export function parsePostgres(ddl: string): Partial<ERDDocument> {
  const ast = sqlParser.astify(ddl, { database: 'PostgresQL' });
  const statements = Array.isArray(ast) ? ast : [ast];

  const tables: Table[] = [];
  const relationships: Relationship[] = [];

  for (const stmt of statements) {
    if (stmt.type !== 'create' || stmt.keyword !== 'table') continue;

    const tableName = stmt.table?.[0]?.table ?? 'unknown';
    const tableId = nanoid();
    const columns: Column[] = [];

    // Extract columns
    for (const def of stmt.create_definitions ?? []) {
      if (def.resource === 'column') {
        const colId = nanoid();
        columns.push({
          id: colId,
          name: def.column?.column ?? 'unknown',
          type: formatColumnType(def),
          isPrimaryKey: false,       // Set below from constraints
          isForeignKey: false,
          isNullable: !hasConstraint(def, 'not null'),
          isUnique: hasConstraint(def, 'unique'),
          isAutoIncrement: hasConstraint(def, 'auto_increment'),
          defaultValue: extractDefault(def),
        });
      }

      // PRIMARY KEY constraint
      if (def.resource === 'constraint' && def.constraint_type === 'primary key') {
        for (const keyCol of def.definition ?? []) {
          const col = columns.find(c => c.name === keyCol.column);
          if (col) col.isPrimaryKey = true;
        }
      }

      // FOREIGN KEY constraint
      if (def.resource === 'constraint' && def.constraint_type === 'REFERENCES') {
        const sourceCol = columns.find(c => c.name === def.definition?.[0]?.column);
        if (sourceCol) {
          sourceCol.isForeignKey = true;
          // Relationship will be resolved after all tables are parsed
        }
      }
    }

    tables.push({
      id: tableId,
      name: tableName,
      columns,
      indexes: [],
    });
  }

  // Second pass: resolve FK relationships across tables
  resolveRelationships(tables, statements, relationships);

  return { tables, relationships };
}

function formatColumnType(def: any): string {
  const dt = def.definition?.dataType ?? 'TEXT';
  const length = def.definition?.length;
  return length ? `${dt}(${length})` : dt;
}

function hasConstraint(def: any, type: string): boolean {
  return def.definition?.constraint?.some?.((c: any) =>
    c.type?.toLowerCase() === type
  ) ?? false;
}

function extractDefault(def: any): string | undefined {
  const d = def.definition?.constraint?.find?.((c: any) => c.type === 'default');
  return d?.value?.value?.toString();
}

function resolveRelationships(
  tables: Table[],
  statements: any[],
  relationships: Relationship[]
): void {
  // Build name -> id lookup
  const tableByName = new Map(tables.map(t => [t.name, t]));

  for (const stmt of statements) {
    if (stmt.type !== 'create' || stmt.keyword !== 'table') continue;
    const srcTableName = stmt.table?.[0]?.table;
    const srcTable = tableByName.get(srcTableName);
    if (!srcTable) continue;

    for (const def of stmt.create_definitions ?? []) {
      if (def.resource === 'constraint' && def.constraint_type === 'REFERENCES') {
        const srcColName = def.definition?.[0]?.column;
        const tgtTableName = def.reference_definition?.table?.[0]?.table;
        const tgtColName = def.reference_definition?.definition?.[0]?.column;

        const tgtTable = tableByName.get(tgtTableName);
        const srcCol = srcTable.columns.find(c => c.name === srcColName);
        const tgtCol = tgtTable?.columns.find(c => c.name === tgtColName);

        if (tgtTable && srcCol && tgtCol) {
          srcCol.references = { tableId: tgtTable.id, columnId: tgtCol.id };
          relationships.push({
            id: nanoid(),
            name: def.constraint ?? `fk_${srcTableName}_${srcColName}`,
            sourceTableId: srcTable.id,
            sourceColumnId: srcCol.id,
            targetTableId: tgtTable.id,
            targetColumnId: tgtCol.id,
            sourceCardinality: 'zero-or-many',
            targetCardinality: 'exactly-one',
            onDelete: extractAction(def, 'on_delete') ?? 'NO ACTION',
            onUpdate: extractAction(def, 'on_update') ?? 'NO ACTION',
          });
        }
      }
    }
  }
}

function extractAction(def: any, key: string): ReferentialAction | undefined {
  const action = def.reference_definition?.[key];
  if (!action) return undefined;
  return action.toUpperCase().replace(' ', '_') as ReferentialAction;
}
```

### PostgreSQL Generator

```typescript
// lib/generators/postgres-generator.ts
import type { ERDDocument, Table, Column, Relationship } from '@/types/erd';

export function generatePostgres(doc: ERDDocument): string {
  const lines: string[] = [];
  lines.push('-- Generated by ERD Editor');
  lines.push(`-- Dialect: PostgreSQL`);
  lines.push(`-- Date: ${new Date().toISOString()}\n`);

  for (const table of doc.tables) {
    lines.push(generateCreateTable(table));
    lines.push('');
  }

  // Foreign key constraints as ALTER TABLE (safer for circular references)
  for (const rel of doc.relationships) {
    const srcTable = doc.tables.find(t => t.id === rel.sourceTableId);
    const tgtTable = doc.tables.find(t => t.id === rel.targetTableId);
    const srcCol = srcTable?.columns.find(c => c.id === rel.sourceColumnId);
    const tgtCol = tgtTable?.columns.find(c => c.id === rel.targetColumnId);
    if (srcTable && tgtTable && srcCol && tgtCol) {
      lines.push(
        `ALTER TABLE "${srcTable.name}" ADD CONSTRAINT "${rel.name ?? `fk_${srcTable.name}_${srcCol.name}`}"`,
        `  FOREIGN KEY ("${srcCol.name}") REFERENCES "${tgtTable.name}" ("${tgtCol.name}")`,
        `  ON DELETE ${rel.onDelete} ON UPDATE ${rel.onUpdate};`,
        ''
      );
    }
  }

  return lines.join('\n');
}

function generateCreateTable(table: Table): string {
  const lines: string[] = [];
  lines.push(`CREATE TABLE "${table.name}" (`);

  const colDefs: string[] = table.columns.map(col => {
    const parts: string[] = [`  "${col.name}"`];
    parts.push(col.type);
    if (!col.isNullable) parts.push('NOT NULL');
    if (col.isUnique && !col.isPrimaryKey) parts.push('UNIQUE');
    if (col.defaultValue) parts.push(`DEFAULT ${col.defaultValue}`);
    return parts.join(' ');
  });

  // Primary key constraint
  const pkCols = table.columns.filter(c => c.isPrimaryKey);
  if (pkCols.length > 0) {
    colDefs.push(
      `  PRIMARY KEY (${pkCols.map(c => `"${c.name}"`).join(', ')})`
    );
  }

  lines.push(colDefs.join(',\n'));
  lines.push(');');

  // Table comment
  if (table.comment) {
    lines.push(`COMMENT ON TABLE "${table.name}" IS '${table.comment.replace(/'/g, "''")}';`);
  }

  return lines.join('\n');
}
```

### MySQL Generator (dialect differences)

```typescript
// lib/generators/mysql-generator.ts
import type { ERDDocument, Table } from '@/types/erd';

export function generateMySql(doc: ERDDocument): string {
  const lines: string[] = [];
  lines.push('-- Generated by ERD Editor');
  lines.push(`-- Dialect: MySQL\n`);

  for (const table of doc.tables) {
    lines.push(generateMySqlTable(table));
    lines.push('');
  }

  return lines.join('\n');
}

function generateMySqlTable(table: Table): string {
  const lines: string[] = [];
  // MySQL: backtick quoting, no schema prefix, ENGINE specification
  lines.push(`CREATE TABLE \`${table.name}\` (`);

  const colDefs: string[] = table.columns.map(col => {
    const parts: string[] = [`  \`${col.name}\``];
    // Type mapping: PostgreSQL -> MySQL
    parts.push(pgTypeToMySQL(col.type));
    if (col.isAutoIncrement) parts.push('AUTO_INCREMENT');
    if (!col.isNullable) parts.push('NOT NULL');
    if (col.isUnique && !col.isPrimaryKey) parts.push('UNIQUE');
    if (col.defaultValue) parts.push(`DEFAULT ${mysqlDefault(col.defaultValue)}`);
    return parts.join(' ');
  });

  const pkCols = table.columns.filter(c => c.isPrimaryKey);
  if (pkCols.length > 0) {
    colDefs.push(
      `  PRIMARY KEY (${pkCols.map(c => `\`${c.name}\``).join(', ')})`
    );
  }

  lines.push(colDefs.join(',\n'));
  lines.push(') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;');

  return lines.join('\n');
}

/** Map PostgreSQL types to MySQL equivalents */
function pgTypeToMySQL(pgType: string): string {
  const map: Record<string, string> = {
    'UUID': 'CHAR(36)',
    'TIMESTAMPTZ': 'DATETIME',
    'TIMESTAMP WITH TIME ZONE': 'DATETIME',
    'TEXT': 'TEXT',
    'JSONB': 'JSON',
    'BOOLEAN': 'TINYINT(1)',
    'SERIAL': 'INT',
    'BIGSERIAL': 'BIGINT',
    'REAL': 'FLOAT',
    'DOUBLE PRECISION': 'DOUBLE',
  };
  const upper = pgType.toUpperCase();
  return map[upper] ?? pgType;
}

function mysqlDefault(value: string): string {
  // Convert PG functions to MySQL equivalents
  if (value === 'gen_random_uuid()') return '(UUID())';
  if (value === 'NOW()') return 'CURRENT_TIMESTAMP';
  return value;
}
```

### Generator Registry

```typescript
// lib/generators/index.ts
import { generatePostgres } from './postgres-generator';
import { generateMySql } from './mysql-generator';
import type { ERDDocument, SQLDialect } from '@/types/erd';

type GeneratorFn = (doc: ERDDocument) => string;

const generators: Record<SQLDialect, GeneratorFn> = {
  postgresql: generatePostgres,
  mysql: generateMySql,
  sqlite: generateSqlite,     // Same pattern, different type mapping
  mariadb: generateMySql,     // MariaDB is MySQL-compatible with minor differences
  mssql: generateMssql,       // T-SQL square bracket quoting, IDENTITY instead of AUTO_INCREMENT
};

export function generateDDL(doc: ERDDocument, dialect?: SQLDialect): string {
  const target = dialect ?? doc.dialect;
  const gen = generators[target];
  if (!gen) throw new Error(`No generator for dialect: ${target}`);
  return gen(doc);
}
```

---

## Import Flows

### DDL Import (node-sql-parser)

```typescript
// lib/import/ddl-import.ts
import { parsePostgres } from '@/lib/parsers/postgres-parser';
import type { ERDDocument, SQLDialect } from '@/types/erd';
import { autoLayout } from '@/lib/auto-layout';
import { useERDStore } from '@/store/erd-store';

/**
 * Import DDL string: parse -> generate positions -> load into store.
 * Flow: SQL DDL -> node-sql-parser AST -> ERDDocument -> React Flow nodes/edges
 */
export async function importDDL(ddl: string, dialect: SQLDialect): Promise<void> {
  const parsers: Record<string, (ddl: string) => Partial<ERDDocument>> = {
    postgresql: parsePostgres,
    mysql: parseMySql,
    sqlite: parseSqlite,
  };

  const parser = parsers[dialect];
  if (!parser) throw new Error(`No parser for dialect: ${dialect}`);

  const partial = parser(ddl);
  const doc: ERDDocument = {
    version: '1.0.0',
    name: 'Imported Schema',
    notation: 'crowsfoot',
    dialect,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    tables: partial.tables ?? [],
    relationships: partial.relationships ?? [],
    diagram: {
      positions: {},
      viewport: { x: 0, y: 0, zoom: 1 },
      gridSize: 20,
      snapToGrid: true,
    },
  };

  // Auto-layout since imported DDL has no position data
  const store = useERDStore.getState();
  store.loadDocument(doc);
  const laid = autoLayout(store.nodes, store.edges);
  // Write positions back
  for (const node of laid) {
    doc.diagram.positions[node.id] = node.position;
  }
  store.loadDocument(doc);
}
```

### Schema Import (ChartDB "Smart Query" Pattern)

ChartDB's killer feature: paste a single SQL query against your live database, get the full schema as JSON. The query uses `information_schema` to extract tables, columns, constraints, and relationships in one shot.

```sql
-- PostgreSQL "Smart Query" — paste into any SQL client connected to your DB
-- Returns full schema as JSON
SELECT json_build_object(
  'tables', (
    SELECT json_agg(json_build_object(
      'name', t.table_name,
      'schema', t.table_schema,
      'columns', (
        SELECT json_agg(json_build_object(
          'name', c.column_name,
          'type', c.data_type ||
            CASE WHEN c.character_maximum_length IS NOT NULL
              THEN '(' || c.character_maximum_length || ')'
              ELSE '' END,
          'isNullable', c.is_nullable = 'YES',
          'default', c.column_default,
          'isPrimaryKey', EXISTS (
            SELECT 1 FROM information_schema.key_column_usage kcu
            JOIN information_schema.table_constraints tc
              ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND kcu.table_name = c.table_name
              AND kcu.column_name = c.column_name
          )
        ) ORDER BY c.ordinal_position)
        FROM information_schema.columns c
        WHERE c.table_name = t.table_name
          AND c.table_schema = t.table_schema
      ),
      'foreignKeys', (
        SELECT json_agg(json_build_object(
          'column', kcu.column_name,
          'referencedTable', ccu.table_name,
          'referencedColumn', ccu.column_name
        ))
        FROM information_schema.key_column_usage kcu
        JOIN information_schema.table_constraints tc
          ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND kcu.table_name = t.table_name
          AND kcu.table_schema = t.table_schema
      )
    ))
    FROM information_schema.tables t
    WHERE t.table_schema = 'public'
      AND t.table_type = 'BASE TABLE'
  )
) AS schema_json;
```

```sql
-- MySQL equivalent "Smart Query"
SELECT JSON_OBJECT(
  'tables', (
    SELECT JSON_ARRAYAGG(JSON_OBJECT(
      'name', t.TABLE_NAME,
      'columns', (
        SELECT JSON_ARRAYAGG(JSON_OBJECT(
          'name', c.COLUMN_NAME,
          'type', c.COLUMN_TYPE,
          'isNullable', c.IS_NULLABLE = 'YES',
          'default', c.COLUMN_DEFAULT,
          'isPrimaryKey', c.COLUMN_KEY = 'PRI'
        ) ORDER BY c.ORDINAL_POSITION)
        FROM information_schema.COLUMNS c
        WHERE c.TABLE_NAME = t.TABLE_NAME
          AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
      )
    ))
    FROM information_schema.TABLES t
    WHERE t.TABLE_SCHEMA = DATABASE()
      AND t.TABLE_TYPE = 'BASE TABLE'
  )
) AS schema_json;
```

### File Import (Prisma Schema)

```typescript
// lib/import/prisma-import.ts
// Liam ERD pattern: parse Prisma .prisma files into ERDDocument
import { nanoid } from 'nanoid';
import type { ERDDocument, Table, Column, Relationship } from '@/types/erd';

/**
 * Minimal Prisma parser — extracts models and relations.
 * For production, use @mrleebo/prisma-ast or prisma-schema-parser.
 */
export function parsePrismaSchema(schema: string): Partial<ERDDocument> {
  const tables: Table[] = [];
  const relationships: Relationship[] = [];

  const modelRegex = /model\s+(\w+)\s*\{([^}]+)\}/g;
  let match;

  while ((match = modelRegex.exec(schema)) !== null) {
    const modelName = match[1];
    const body = match[2];
    const tableId = nanoid();
    const columns: Column[] = [];

    for (const line of body.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('//') || trimmed.startsWith('@@')) continue;

      // Field line: name Type modifiers
      const fieldMatch = trimmed.match(/^(\w+)\s+(\w+)(\?)?(\[\])?\s*(.*)/);
      if (!fieldMatch) continue;

      const [, name, type, optional, array, modifiers] = fieldMatch;

      // Skip relation fields (they have @relation)
      if (modifiers.includes('@relation')) continue;

      // Skip Prisma-only types (other model references without @relation)
      const prismaTypes = new Set([
        'String', 'Int', 'Float', 'Boolean', 'DateTime',
        'Json', 'BigInt', 'Decimal', 'Bytes',
      ]);
      if (!prismaTypes.has(type)) continue;

      columns.push({
        id: nanoid(),
        name: extractMapName(modifiers) ?? name,
        type: prismaTypeToSQL(type),
        isPrimaryKey: modifiers.includes('@id'),
        isForeignKey: false,
        isNullable: !!optional,
        isUnique: modifiers.includes('@unique'),
        isAutoIncrement: modifiers.includes('autoincrement()'),
        defaultValue: extractPrismaDefault(modifiers),
      });
    }

    tables.push({
      id: tableId,
      name: extractTableMap(body) ?? modelName.toLowerCase() + 's',
      columns,
      indexes: [],
    });
  }

  return { tables, relationships };
}

function prismaTypeToSQL(prismaType: string): string {
  const map: Record<string, string> = {
    'String': 'TEXT',
    'Int': 'INTEGER',
    'Float': 'REAL',
    'Boolean': 'BOOLEAN',
    'DateTime': 'TIMESTAMPTZ',
    'Json': 'JSONB',
    'BigInt': 'BIGINT',
    'Decimal': 'DECIMAL',
    'Bytes': 'BYTEA',
  };
  return map[prismaType] ?? 'TEXT';
}

function extractMapName(modifiers: string): string | undefined {
  const match = modifiers.match(/@map\("(\w+)"\)/);
  return match?.[1];
}

function extractTableMap(body: string): string | undefined {
  const match = body.match(/@@map\("(\w+)"\)/);
  return match?.[1];
}

function extractPrismaDefault(modifiers: string): string | undefined {
  const match = modifiers.match(/@default\(([^)]+)\)/);
  if (!match) return undefined;
  const val = match[1];
  if (val === 'now()') return 'NOW()';
  if (val === 'cuid()') return 'gen_random_uuid()';
  if (val === 'uuid()') return 'gen_random_uuid()';
  if (val === 'autoincrement()') return undefined; // Handled by isAutoIncrement
  return val;
}
```

---

## Export Flows

### DDL Export (Multi-Dialect)

```typescript
// Already covered in Generator Registry above.
// Usage from UI:
function handleExportDDL(dialect: SQLDialect) {
  const doc = useERDStore.getState().toDocument();
  const ddl = generateDDL(doc, dialect);

  // Desktop (Tauri): save to file
  // Web: download as .sql file
  downloadFile(ddl, `${doc.name}.sql`, 'text/sql');
}
```

### Image Export (PNG/SVG)

```typescript
// lib/export/image-export.ts
import { toPng, toSvg } from '@xyflow/react';

export async function exportAsPng(filename: string): Promise<void> {
  const dataUrl = await toPng(
    document.querySelector('.react-flow') as HTMLElement,
    {
      backgroundColor: '#ffffff',
      quality: 1,
      width: 4096,   // High-res export
      height: 2048,
    }
  );
  downloadDataUrl(dataUrl, `${filename}.png`);
}

export async function exportAsSvg(filename: string): Promise<void> {
  const svg = await toSvg(
    document.querySelector('.react-flow') as HTMLElement,
    { backgroundColor: '#ffffff' }
  );
  downloadDataUrl(svg, `${filename}.svg`);
}

function downloadDataUrl(dataUrl: string, filename: string): void {
  const link = document.createElement('a');
  link.href = dataUrl;
  link.download = filename;
  link.click();
}
```

### DBML Export (dbdiagram.io interop)

```typescript
// lib/export/dbml-export.ts
import type { ERDDocument, Cardinality } from '@/types/erd';

export function generateDBML(doc: ERDDocument): string {
  const lines: string[] = [];

  for (const table of doc.tables) {
    lines.push(`Table ${table.name} {`);
    for (const col of table.columns) {
      const attrs: string[] = [];
      if (col.isPrimaryKey) attrs.push('pk');
      if (!col.isNullable) attrs.push('not null');
      if (col.isUnique) attrs.push('unique');
      if (col.defaultValue) attrs.push(`default: '${col.defaultValue}'`);
      if (col.comment) attrs.push(`note: '${col.comment}'`);
      const attrStr = attrs.length > 0 ? ` [${attrs.join(', ')}]` : '';
      lines.push(`  ${col.name} ${col.type}${attrStr}`);
    }
    lines.push('}\n');
  }

  // Relationships
  for (const rel of doc.relationships) {
    const srcTable = doc.tables.find(t => t.id === rel.sourceTableId);
    const tgtTable = doc.tables.find(t => t.id === rel.targetTableId);
    const srcCol = srcTable?.columns.find(c => c.id === rel.sourceColumnId);
    const tgtCol = tgtTable?.columns.find(c => c.id === rel.targetColumnId);
    if (srcTable && tgtTable && srcCol && tgtCol) {
      const symbol = cardinalityToDBML(rel.sourceCardinality, rel.targetCardinality);
      lines.push(`Ref: ${srcTable.name}.${srcCol.name} ${symbol} ${tgtTable.name}.${tgtCol.name}`);
    }
  }

  return lines.join('\n');
}

function cardinalityToDBML(source: Cardinality, target: Cardinality): string {
  // DBML uses: - (one-to-one), < (one-to-many), > (many-to-one), <> (many-to-many)
  if (target === 'zero-or-many' || target === 'one-or-many') return '<';
  if (source === 'zero-or-many' || source === 'one-or-many') return '>';
  return '-';
}
```

---

## MCP Integration (ERFlow Pattern)

ERFlow exposes 25+ MCP tools for natural language schema editing from CLI/IDE. Implement the same pattern for the ERD editor:

```typescript
// mcp/erd-mcp-tools.ts
// Register as MCP tools via the Claude MCP protocol

export const erdMCPTools = {
  'erd.addTable': {
    description: 'Add a new table to the ERD',
    parameters: {
      name: { type: 'string', description: 'Table name' },
      columns: { type: 'array', description: 'Column definitions' },
    },
    handler: async ({ name, columns }: { name: string; columns: any[] }) => {
      const table = createTableFromNL(name, columns);
      useERDStore.getState().addTable(table);
      return { success: true, tableId: table.id };
    },
  },

  'erd.addRelationship': {
    description: 'Add a FK relationship between two tables',
    parameters: {
      from: { type: 'string', description: 'Source table.column' },
      to: { type: 'string', description: 'Target table.column' },
      cardinality: { type: 'string', description: 'one-to-one, one-to-many, many-to-many' },
    },
    handler: async ({ from, to, cardinality }: {
      from: string; to: string; cardinality: string;
    }) => {
      const [srcTable, srcCol] = resolveTableColumn(from);
      const [tgtTable, tgtCol] = resolveTableColumn(to);
      const { source, target } = mapNLCardinality(cardinality);
      useERDStore.getState().addRelationship({
        sourceHandle: `${srcTable.id}.${srcCol.id}-source`,
        targetHandle: `${tgtTable.id}.${tgtCol.id}-target`,
      });
      return { success: true };
    },
  },

  'erd.exportDDL': {
    description: 'Export the current ERD as SQL DDL',
    parameters: {
      dialect: { type: 'string', enum: ['postgresql', 'mysql', 'sqlite'] },
    },
    handler: async ({ dialect }: { dialect: SQLDialect }) => {
      const doc = useERDStore.getState().toDocument();
      return { ddl: generateDDL(doc, dialect) };
    },
  },

  'erd.importDDL': {
    description: 'Import SQL DDL into the ERD',
    parameters: {
      sql: { type: 'string' },
      dialect: { type: 'string' },
    },
    handler: async ({ sql, dialect }: { sql: string; dialect: SQLDialect }) => {
      await importDDL(sql, dialect);
      return {
        success: true,
        tableCount: useERDStore.getState().document.tables.length,
      };
    },
  },

  // Additional tools following ERFlow pattern:
  // erd.renameTable, erd.renameColumn, erd.addColumn, erd.removeColumn,
  // erd.changeColumnType, erd.setNullable, erd.addIndex,
  // erd.generateMigration (checkpoint-based diff)
};
```

---

## Persistence (Tauri)

### Desktop: File System Save/Load

```typescript
// lib/persistence/tauri-fs.ts
import { save, open } from '@tauri-apps/plugin-dialog';
import { writeTextFile, readTextFile } from '@tauri-apps/plugin-fs';
import { appDataDir } from '@tauri-apps/api/path';
import type { ERDDocument } from '@/types/erd';
import { useERDStore } from '@/store/erd-store';

const ERD_FILTER = {
  name: 'ERD Files',
  extensions: ['erd.json'],
};

export async function saveDocument(): Promise<void> {
  const doc = useERDStore.getState().toDocument();
  const filePath = await save({
    defaultPath: `${doc.name}.erd.json`,
    filters: [ERD_FILTER],
  });
  if (filePath) {
    await writeTextFile(filePath, JSON.stringify(doc, null, 2));
  }
}

export async function openDocument(): Promise<void> {
  const filePath = await open({
    filters: [ERD_FILTER],
    multiple: false,
  });
  if (filePath) {
    const content = await readTextFile(filePath as string);
    const doc: ERDDocument = JSON.parse(content);
    useERDStore.getState().loadDocument(doc);
  }
}

/** Auto-save every 30 seconds to a temp file */
export function startAutoSave(intervalMs = 30_000): () => void {
  const timer = setInterval(async () => {
    const doc = useERDStore.getState().toDocument();
    const tempPath = `${await appDataDir()}/autosave.erd.json`;
    await writeTextFile(tempPath, JSON.stringify(doc));
  }, intervalMs);
  return () => clearInterval(timer);
}
```

### Web Fallback: Dexie.js (IndexedDB)

```typescript
// lib/persistence/dexie-store.ts
// ChartDB uses Dexie.js for zero-backend persistence in the browser
import Dexie, { type Table as DexieTable } from 'dexie';
import type { ERDDocument } from '@/types/erd';

class ERDDatabase extends Dexie {
  documents!: DexieTable<ERDDocument & { id: string }, string>;

  constructor() {
    super('erd-editor');
    this.version(1).stores({
      documents: 'id, name, updatedAt',
    });
  }
}

export const db = new ERDDatabase();

export async function saveToIndexedDB(doc: ERDDocument): Promise<void> {
  await db.documents.put({ ...doc, id: doc.name });
}

export async function loadFromIndexedDB(id: string): Promise<ERDDocument | undefined> {
  return db.documents.get(id);
}

export async function listDocuments(): Promise<ERDDocument[]> {
  return db.documents.orderBy('updatedAt').reverse().toArray();
}
```

---

## Project Structure

```
src/
  types/
    erd.ts                      # ERDDocument, Table, Column, Relationship types
  components/
    ERDCanvas.tsx               # Main React Flow canvas wrapper
    nodes/
      TableNode.tsx             # Crow's Foot table card with per-column handles
      ChenEntityNode.tsx        # Chen rectangle entity
      ChenAttributeNode.tsx     # Chen oval attribute
      ChenRelationshipNode.tsx  # Chen diamond relationship
    edges/
      CrowsFootMarkers.tsx      # SVG <defs> for 4 cardinality markers
      CrowsFootEdge.tsx         # Custom edge with markerStart/markerEnd
      ChenEdge.tsx              # Simple line with cardinality label
    panels/
      TableEditor.tsx           # Side panel for editing table/column properties
      ImportDialog.tsx          # DDL paste / file upload dialog
      ExportDialog.tsx          # Dialect picker + DDL preview
  store/
    erd-store.ts                # Zustand + zundo (undo/redo)
  lib/
    node-types.ts               # Node type registry (Crow's Foot + Chen)
    edge-types.ts               # Edge type registry
    auto-layout.ts              # dagre-based auto-layout
    parsers/
      types.ts                  # DDLParser / DDLGenerator interfaces
      postgres-parser.ts        # PG DDL -> ERDDocument
      mysql-parser.ts           # MySQL DDL -> ERDDocument
      prisma-parser.ts          # Prisma schema -> ERDDocument
    generators/
      index.ts                  # Generator registry + generateDDL()
      postgres-generator.ts     # ERDDocument -> PG DDL
      mysql-generator.ts        # ERDDocument -> MySQL DDL
      dbml-generator.ts         # ERDDocument -> DBML
    import/
      ddl-import.ts             # Orchestrates parse + auto-layout + load
      smart-query.ts            # ChartDB-style information_schema queries
    export/
      image-export.ts           # toPng() / toSvg()
    persistence/
      tauri-fs.ts               # Tauri file system save/load/autosave
      dexie-store.ts            # IndexedDB fallback for web
  mcp/
    erd-mcp-tools.ts            # MCP tool definitions for NL editing
```

---

## Reference Implementations — Study Order

| Priority | Project | Why Study It | Key Files to Read |
|----------|---------|-------------|-------------------|
| 1 | **ChartDB** | Closest stack match (React + Vite + ReactFlow + shadcn + Dexie) | `src/pages/editor-page/`, `src/context/chartdb-context/` |
| 2 | **DrawDB** | Gold-standard parser/generator architecture | `src/utils/importFrom/`, `src/utils/exportAs/` |
| 3 | **React Flow DatabaseSchemaNode** | Official per-column handle pattern | `reactflow.dev/ui/components/database-schema-node` |
| 4 | **NextERD** | Simplest React Flow + shadcn integration, good for learning | Full codebase (~small) |
| 5 | **Liam ERD** | 100+ table performance, schema file importers | `src/` layout engine |
| 6 | **dineug/erd-editor** | .erd.json format design, VS Code integration | Format spec |
| 7 | **JointJS 4.2** | Virtual rendering, z-ordering for massive schemas | Docs: ERD shapes API |
| 8 | **ERFlow** | MCP tool design patterns for NL schema editing | Tool definitions |

---

## When to Use

- Building a visual database schema editor with React
- Need Crow's Foot or Chen notation rendering on a canvas
- Importing existing schemas (DDL, Prisma, live database) into a visual editor
- Exporting ERDs to multiple SQL dialects
- Adding MCP/NL editing capabilities to a schema tool

## When NOT to Use

- **Simple static ERD diagrams** — Use Mermaid `erDiagram` syntax instead (see `database-schema-designer.md`)
- **Database migration tooling only** — Use Prisma Migrate, Drizzle Kit, or Alembic directly
- **UML diagrams** — Different domain; use PlantUML or Excalidraw
- **Existing app with JointJS** — JointJS 4.2 has built-in ERD primitives; do not add React Flow on top

## Related Skills

- `er-diagram-components.md` — Canonical reference for all ER notation components (Chen, Crow's Foot, attribute types, cardinality rules). Read this first for theory.
- `erd-creator-textbook-research.md` — Academic research findings behind these patterns
- `database-schema-designer.md` — Schema design methodology (Prisma, Drizzle, RLS, seeds). Use for the data modeling side.
- `reserved-word-context-aware-quoting.md` — Quoting rules for DDL generators
- `regex-alternation-ordering-sql-types.md` — SQL type parsing edge cases
- `postgresql-to-mysql-runtime-translation.md` — PG-to-MySQL type mapping reference

## References

- [ChartDB](https://github.com/chartdb/chartdb) — MIT, React + Vite + ReactFlow + shadcn + Dexie.js
- [DrawDB](https://github.com/drawdb-io/drawdb) — AGPL-3.0, ~24,400 stars, gold-standard DDL parsers
- [Liam ERD](https://github.com/liam-hq/liam) — Apache-2.0, handles 100+ tables, CLI tool
- [NextERD](https://github.com/vaxad/NextERD) — Next.js + React Flow + shadcn, small readable codebase
- [dineug/erd-editor](https://github.com/dineug/erd-editor) — Web Component, VS Code + IntelliJ integration
- [React Flow DatabaseSchemaNode](https://reactflow.dev/ui/components/database-schema-node) — Official per-column handle pattern
- [relliv/crows-foot-notations](https://github.com/relliv/crows-foot-notations) — SVG symbol reference
- [node-sql-parser](https://github.com/nicereporter/node-sql-parser) — Bidirectional SQL-AST, multi-dialect
- [sql-ddl-to-json-schema](https://github.com/nicereporter/node-sql-parser) — DDL-focused, nearley grammar
- [ERFlow](https://github.com/ageborn-dev/erflow) — MCP-based ERD editing, 25+ tools
- [JointJS 4.2](https://www.jointjs.com/) — Built-in ERD shapes + Crow's Foot + virtual rendering
- [zundo](https://github.com/charkour/zundo) — Undo/redo middleware for Zustand
- [@dagrejs/dagre](https://github.com/dagrejs/dagre) — Directed graph auto-layout
