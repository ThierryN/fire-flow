---
name: er-diagram-components
category: database-solutions
version: 1.0.0
contributed: 2026-03-09
contributor: fire-research
last_updated: 2026-03-09
tags: [erd, entity-relationship, database-design, react-flow, crow-foot, chen-notation]
difficulty: medium
---

# ER Diagram Components


## Problem

Building a visual ERD editor requires precise knowledge of all ER diagram components, their visual representations, notation variants, and how they map to UI framework primitives (React Flow nodes/edges). Without a canonical reference, developers mix notation systems, miss attribute variants, or implement incomplete cardinality symbols — producing diagrams that look professional but encode incorrect semantics.

## Solution Pattern

Implement ER diagrams as a layered system:

1. **Data model layer** — TypeScript types for entities, attributes, relationships, cardinality, participation
2. **Notation layer** — Rendering rules that map the data model to visual shapes (Chen or Crow's Foot)
3. **React Flow layer** — Custom node components, edge types, SVG markers, and handle placement
4. **Validation layer** — Cardinality checks, participation constraint enforcement, normalization warnings

Start with Crow's Foot notation (modern, compact, professional standard). Add Chen as an alternate view. The textbook explicitly notes the newer ERD style (attributes inside entities) is preferred because it reduces visual clutter — "if depicted in the older model, we would see 21 attribute ovals and a minimum of 8 actions."

---

## Entity Types

### Strong Entity
- **Visual:** Rectangle with entity name as header
- **Definition:** Has its own primary key. Can exist independently.
- **React Flow node type:** `entityNode` — rectangular card with name header + attribute rows

### Weak Entity
- **Visual:** Double-bordered rectangle
- **Definition:** Cannot exist without its identifying (owner) entity. Requires partial key + owner's PK for full identification.
- **React Flow node type:** `weakEntityNode` — same as entityNode but with `border: double 3px` or nested border via CSS `outline` + `border`
- **Implementation note:** Always paired with an identifying relationship (double diamond in Chen, or a labeled edge with "ID" marker in Crow's Foot)

```typescript
// Entity data model
interface EREntity {
  id: string;
  name: string;
  type: 'strong' | 'weak';
  attributes: ERAttribute[];
  position: { x: number; y: number };
  // Weak entity fields
  ownerEntityId?: string;        // FK to identifying entity
  partialKeyAttributes?: string[]; // attribute IDs forming partial key
}
```

---

## Attribute Types

Six variants exist. In Crow's Foot, all render as rows inside the entity box. In Chen, each has a distinct oval shape.

### 1. Simple Attribute
- **Chen visual:** Single oval connected by line to entity
- **Crow's Foot visual:** Plain row inside entity box (e.g., `first_name VARCHAR(50)`)
- **Example:** `email`, `phone`, `salary`

### 2. Key Attribute (Primary Key)
- **Chen visual:** Oval with **underlined** text
- **Crow's Foot visual:** Row with **PK** prefix marker, bold or key icon
- **Example:** `student_id`, `order_id`
- **Rendering:** Always rendered first/top in entity box

### 3. Composite Attribute
- **Chen visual:** Oval that branches into sub-ovals (tree structure)
- **Crow's Foot visual:** Flattened to leaf-level columns inside entity box (e.g., `Address` becomes `street`, `city`, `state`, `zip`)
- **Example:** `Name` -> `FirstName`, `LastName`; `Address` -> `Street`, `City`, `State`, `Zip`
- **DDL mapping:** Only leaf attributes become columns

### 4. Multivalued Attribute
- **Chen visual:** Double-bordered oval
- **Crow's Foot visual:** Not shown inline — generates a **separate table** with FK back to entity
- **Example:** `PhoneNumbers` (a person can have multiple), `Skills`, `Colors`
- **DDL mapping:** Creates separate table: `entity_attribute(entity_pk FK, attribute_value, PRIMARY KEY(entity_pk, attribute_value))`

### 5. Derived Attribute
- **Chen visual:** Dashed-bordered oval
- **Crow's Foot visual:** Typically omitted or shown with `(derived)` annotation / italic text
- **Example:** `Age` derived from `DateOfBirth`, `TotalPrice` derived from `Quantity * UnitPrice`
- **DDL mapping:** Usually NOT stored. Implemented as computed column (`GENERATED ALWAYS AS`) or application-level calculation.

### 6. Partial Key (Weak Entity Discriminator)
- **Chen visual:** Oval with **dashed underline**
- **Crow's Foot visual:** Row with partial-key marker inside weak entity box
- **Example:** In a weak entity `Dependent` owned by `Employee`, the partial key `dependent_name` uniquely identifies within one employee but not globally
- **DDL mapping:** Combined with owner PK to form composite primary key

```typescript
// Attribute data model
interface ERAttribute {
  id: string;
  name: string;
  type: 'simple' | 'key' | 'composite' | 'multivalued' | 'derived' | 'partial-key';
  dataType: string;            // VARCHAR(50), INTEGER, etc.
  nullable: boolean;
  defaultValue?: string;
  children?: ERAttribute[];    // For composite attributes
  derivedFrom?: string;        // Expression for derived attributes
}
```

---

## Relationship Types

### Unary (Recursive)
- **Definition:** Entity relates to itself
- **Example:** `Employee` manages `Employee`, `Person` is_married_to `Person`
- **React Flow:** Self-loop edge from entity back to itself (use `sourceHandle` and `targetHandle` on different sides of the same node)
- **Cardinality:** Can be 1:1, 1:N, or M:N (e.g., manager is 1:N, married_to is 1:1)

### Binary
- **Definition:** Two entities connected. Most common type (>90% of relationships).
- **Example:** `Student` enrolls_in `Course`, `Order` belongs_to `Customer`
- **React Flow:** Standard edge between two entity nodes

### N-ary (Ternary+)
- **Definition:** Three or more entities in a single relationship
- **Example:** `Doctor` prescribes `Drug` to `Patient` (ternary — the relationship only makes sense with all three)
- **React Flow:** Represented as a diamond node (relationship node) with edges to 3+ entities, OR converted to a junction table entity in Crow's Foot
- **DDL mapping:** Always becomes a junction table with FKs to all participating entities

### Cardinality Constraints

| Notation | Meaning | Example |
|----------|---------|---------|
| **1:1** | One-to-one | Person HAS Passport |
| **1:N** | One-to-many | Department HAS Employees |
| **M:N** | Many-to-many | Student ENROLLS Course |

### Participation Constraints

| Constraint | Visual (Chen) | Visual (Crow's Foot) | Meaning |
|-----------|---------------|----------------------|---------|
| **Total (mandatory)** | Double line | Bar symbol `\|\|` on entity side | Every instance MUST participate |
| **Partial (optional)** | Single line | Circle `O` on entity side | Instances MAY participate |

**Combined reading (Crow's Foot):** Read from each entity toward the relationship. A `Customer` with `\|\|` (total) on its side and `\|<` (one-or-many) on the `Order` side means: "each customer MUST have one or more orders."

```typescript
// Relationship data model
interface ERRelationship {
  id: string;
  name: string;
  type: 'unary' | 'binary' | 'ternary' | 'n-ary';
  entities: {
    entityId: string;
    role?: string;               // "manager", "subordinate" for recursive
    cardinality: '1' | 'N' | 'M';
    participation: 'total' | 'partial';
  }[];
  attributes?: ERAttribute[];    // Relationship can have attributes (e.g., enrollment_date)
  isIdentifying?: boolean;       // True for weak entity identifying relationships
}
```

---

## Notation Systems

### Chen Notation (Peter Chen, 1976)

The original academic notation. Best for teaching and conceptual modeling.

**Node types required (5):**

| Shape | Meaning | CSS/SVG |
|-------|---------|---------|
| Rectangle | Strong Entity | `border: 2px solid` |
| Double Rectangle | Weak Entity | `border: 2px solid; outline: 2px solid; outline-offset: 3px` |
| Oval/Ellipse | Attribute | `border-radius: 50%; border: 2px solid` |
| Diamond | Relationship | `transform: rotate(45deg)` on inner div, or SVG `<polygon>` |
| Double Diamond | Weak/Identifying Relationship | Diamond with double border |

**Attribute variants (6):**

| Variant | Visual Modifier |
|---------|----------------|
| Simple | Plain oval |
| Key | Underlined text (`text-decoration: underline`) |
| Composite | Oval with child ovals branching off |
| Multivalued | Double-bordered oval (`border: double 3px`) |
| Derived | Dashed border (`border-style: dashed`) |
| Partial Key | Dashed underline (`text-decoration: underline; text-decoration-style: dashed`) |

**Line styles:**
- Single line = partial participation
- Double line = total participation
- Cardinality labels (1, M, N) placed near entity on the connecting line

### Crow's Foot Notation (Modern Industry Standard)

Used by ERwin, Lucidchart, dbdiagram.io, draw.io, and most professional tools.

**Node types required (1):**
- Entity box: Rectangle with header (entity name) + rows (attributes with PK/FK markers and data types)

**Line-end symbols (4):**

| Symbol | Name | Meaning | Visual Description |
|--------|------|---------|-------------------|
| `\|\|` | Exactly one | Mandatory single | Two short perpendicular bars |
| `O\|` | Zero or one | Optional single | Circle + perpendicular bar |
| `\|<` | One or many | Mandatory multiple | Bar + crow's foot (three-pronged fork) |
| `O<` | Zero or many | Optional multiple | Circle + crow's foot |

**Reading convention:** Each end of the line describes the cardinality as seen FROM the other entity. The symbol closest to an entity describes how many of THAT entity participate.

**SVG Marker Definitions for Crow's Foot Endpoints:**

```svg
<!-- Define these once in an <svg> <defs> block at the app root -->
<svg style="position: absolute; width: 0; height: 0;">
  <defs>
    <!-- Exactly One: || (two vertical bars) -->
    <marker
      id="crowsfoot-one"
      viewBox="0 0 20 20"
      refX="20"
      refY="10"
      markerWidth="20"
      markerHeight="20"
      orient="auto-start-reverse"
    >
      <line x1="14" y1="2" x2="14" y2="18" stroke="currentColor" strokeWidth="2" />
      <line x1="20" y1="2" x2="20" y2="18" stroke="currentColor" strokeWidth="2" />
    </marker>

    <!-- Zero or One: O| (circle + bar) -->
    <marker
      id="crowsfoot-zero-one"
      viewBox="0 0 30 20"
      refX="30"
      refY="10"
      markerWidth="30"
      markerHeight="20"
      orient="auto-start-reverse"
    >
      <circle cx="10" cy="10" r="6" fill="white" stroke="currentColor" strokeWidth="2" />
      <line x1="24" y1="2" x2="24" y2="18" stroke="currentColor" strokeWidth="2" />
    </marker>

    <!-- One or Many: |< (bar + crow's foot fork) -->
    <marker
      id="crowsfoot-many"
      viewBox="0 0 20 20"
      refX="20"
      refY="10"
      markerWidth="20"
      markerHeight="20"
      orient="auto-start-reverse"
    >
      <line x1="2" y1="2" x2="2" y2="18" stroke="currentColor" strokeWidth="2" />
      <polyline points="20,2 2,10 20,18" fill="none" stroke="currentColor" strokeWidth="2" />
    </marker>

    <!-- Zero or Many: O< (circle + crow's foot fork) -->
    <marker
      id="crowsfoot-zero-many"
      viewBox="0 0 30 20"
      refX="30"
      refY="10"
      markerWidth="30"
      markerHeight="20"
      orient="auto-start-reverse"
    >
      <circle cx="8" cy="10" r="6" fill="white" stroke="currentColor" strokeWidth="2" />
      <polyline points="30,2 14,10 30,18" fill="none" stroke="currentColor" strokeWidth="2" />
    </marker>
  </defs>
</svg>
```

**Applying markers to React Flow edges:**

```typescript
// Map cardinality + participation to marker IDs
function getMarkerIds(
  cardinality: '1' | 'N' | 'M',
  participation: 'total' | 'partial'
): string {
  if (cardinality === '1' && participation === 'total')   return 'crowsfoot-one';
  if (cardinality === '1' && participation === 'partial') return 'crowsfoot-zero-one';
  if (participation === 'total')                          return 'crowsfoot-many';
  return 'crowsfoot-zero-many';
}
```

---

## React Flow Implementation

### DatabaseSchemaNode (Crow's Foot Entity)

Based on React Flow's official `DatabaseSchemaNode` component pattern (reactflow.dev/ui/components/database-schema-node) and the ChartDB architecture (React Flow + shadcn/ui + TypeScript).

```typescript
import { Handle, Position, type NodeProps } from '@xyflow/react';

interface Column {
  id: string;
  name: string;
  type: string;
  isPrimaryKey: boolean;
  isForeignKey: boolean;
  isNullable: boolean;
  defaultValue?: string;
}

interface EntityNodeData {
  name: string;
  type: 'strong' | 'weak';
  columns: Column[];
}

export function EntityNode({ data }: NodeProps<EntityNodeData>) {
  const borderStyle = data.type === 'weak'
    ? 'border-2 border-gray-800 outline outline-2 outline-offset-2 outline-gray-800'
    : 'border-2 border-gray-800';

  return (
    <div className={`bg-white rounded-lg shadow-md min-w-[200px] ${borderStyle}`}>
      {/* Entity name header */}
      <div className="bg-gray-800 text-white px-3 py-2 rounded-t-md font-semibold text-sm">
        {data.name}
      </div>

      {/* Column rows with per-column handles */}
      <div className="divide-y divide-gray-200">
        {data.columns.map((col, index) => (
          <div
            key={col.id}
            className="relative flex items-center gap-2 px-3 py-1.5 text-xs font-mono"
          >
            {/* Left handle — for incoming FK connections */}
            <Handle
              type="target"
              position={Position.Left}
              id={`${col.id}-target`}
              style={{ top: '50%' }}
              className="!w-2 !h-2"
            />

            {/* PK/FK markers */}
            <span className="text-gray-400 w-6 text-right">
              {col.isPrimaryKey && <span className="text-yellow-600">PK</span>}
              {col.isForeignKey && <span className="text-blue-600">FK</span>}
            </span>

            {/* Column name */}
            <span className={col.isPrimaryKey ? 'font-bold' : ''}>
              {col.name}
            </span>

            {/* Data type */}
            <span className="ml-auto text-gray-400">
              {col.type}
              {!col.isNullable && ' NN'}
            </span>

            {/* Right handle — for outgoing PK connections */}
            <Handle
              type="source"
              position={Position.Right}
              id={`${col.id}-source`}
              style={{ top: '50%' }}
              className="!w-2 !h-2"
            />
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Per-Column Handle Placement

The critical pattern from React Flow's official DatabaseSchemaNode: each column row gets its own `Handle` pair (source + target). This enables **field-level relationship connections** — an FK column connects directly to the PK column it references, not just entity-to-entity.

```typescript
// Handle IDs follow the pattern: {columnId}-source / {columnId}-target
// Edge sourceHandle and targetHandle reference these IDs

const edge = {
  id: 'order-customer-fk',
  source: 'orders-entity',          // source node
  target: 'customers-entity',       // target node
  sourceHandle: 'customer_id-source', // FK column handle
  targetHandle: 'id-target',         // PK column handle
  markerStart: 'crowsfoot-many',     // many orders...
  markerEnd: 'crowsfoot-one',        // ...to one customer
  label: 'belongs_to',
};
```

### Custom Edge with Crow's Foot Markers

```typescript
import { BaseEdge, getSmoothStepPath, type EdgeProps } from '@xyflow/react';

interface RelationshipEdgeData {
  label?: string;
  sourceCardinality: '1' | 'N' | 'M';
  sourceParticipation: 'total' | 'partial';
  targetCardinality: '1' | 'N' | 'M';
  targetParticipation: 'total' | 'partial';
}

export function RelationshipEdge(props: EdgeProps<RelationshipEdgeData>) {
  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX: props.sourceX,
    sourceY: props.sourceY,
    targetX: props.targetX,
    targetY: props.targetY,
    sourcePosition: props.sourcePosition,
    targetPosition: props.targetPosition,
    borderRadius: 8,
  });

  const sourceMarker = getMarkerIds(
    props.data?.sourceCardinality ?? '1',
    props.data?.sourceParticipation ?? 'total'
  );
  const targetMarker = getMarkerIds(
    props.data?.targetCardinality ?? 'N',
    props.data?.targetParticipation ?? 'total'
  );

  return (
    <>
      <BaseEdge
        path={edgePath}
        markerStart={`url(#${sourceMarker})`}
        markerEnd={`url(#${targetMarker})`}
        style={{ stroke: '#374151', strokeWidth: 2 }}
      />
      {props.data?.label && (
        <text
          x={labelX}
          y={labelY - 10}
          textAnchor="middle"
          className="fill-gray-600 text-xs"
        >
          {props.data.label}
        </text>
      )}
    </>
  );
}
```

### Registering Node and Edge Types

```typescript
import { ReactFlow } from '@xyflow/react';
import { EntityNode } from './nodes/EntityNode';
import { RelationshipEdge } from './edges/RelationshipEdge';

const nodeTypes = {
  entity: EntityNode,
  // Add Chen notation nodes if supporting both:
  // attribute: AttributeOvalNode,
  // relationship: RelationshipDiamondNode,
};

const edgeTypes = {
  relationship: RelationshipEdge,
};

function ERDEditor() {
  return (
    <>
      {/* SVG defs for crow's foot markers — render once at app root */}
      <CrowsFootMarkerDefs />

      <ReactFlow
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        nodes={nodes}
        edges={edges}
        fitView
      />
    </>
  );
}
```

---

## AI Integration Notes

### LLM Cardinality Weakness (Cogent Education 2025)

The study "Challenges and Feasibility of Multimodal LLMs in ER Diagram Evaluation" found:

1. **LLMs struggle most with cardinality interpretation.** When given an ER diagram image, models frequently misidentify 1:N as M:N or confuse participation constraints (total vs partial).

2. **Chain-of-Thought (CoT) prompting improves Chen notation parsing** — asking the model to "first identify each entity, then list relationships, then determine cardinality for each" produced more accurate results.

3. **CoT has mixed effects on Crow's Foot notation** — the compact visual format with line-end symbols is harder for vision models to parse reliably. The fork/bar/circle symbols are often misread.

4. **Implication for ERD editors with AI features:**
   - Always validate AI-generated cardinality with human confirmation
   - When using AI to suggest relationships, present cardinality as a dropdown the user must explicitly confirm — never auto-commit
   - If implementing AI-powered "describe your schema in plain text" features, use CoT prompting internally and present results as editable suggestions
   - Store cardinality as explicit enum values in the data model, not as visual-only markers

### Recommended AI Integration Pattern

```typescript
// When AI suggests a relationship, always mark it as unconfirmed
interface AIRelationshipSuggestion {
  relationship: ERRelationship;
  confidence: number;          // 0-1
  reasoning: string;           // CoT explanation
  confirmed: false;            // MUST be confirmed by user
}

// UI should show unconfirmed relationships with dashed lines
// and a "Confirm cardinality" button/dropdown
```

---

## When to Use

- Building visual ERD editors with React Flow
- Implementing database diagramming features in any web application
- Choosing between Chen and Crow's Foot notation for a diagram tool
- Mapping ER concepts to React Flow nodes, edges, and handles
- Defining the data model for a schema design tool
- Implementing crow's foot line-end markers with SVG

## When NOT to Use

- Simple schema documentation (use `sql-ddl-generator` instead)
- Runtime database operations (query building, connection pooling)
- Query optimization (indexing strategy, execution plans)
- Generating Mermaid/DBML text diagrams (use `database-schema-designer` ERD section)

## Related Skills

- `er-to-ddl-mapping` — Converting ER diagrams to SQL DDL (the 7 canonical mapping rules)
- `sql-ddl-generator` — DDL output templates with multi-database type mapping
- `normalization-validator` — 1NF/2NF/3NF violation detection and fix recommendations
- `database-schema-designer` — General schema design patterns (Prisma, Drizzle, RLS, seed data)

## References

- LibreTexts "Database Design" — Dr. Sarah North, Affordable Learning Georgia (CC BY 4.0), Chapters 6-10
- Cogent Education 2025 — "Challenges and Feasibility of Multimodal LLMs in ER Diagram Evaluation"
- React Flow Database Schema Node — reactflow.dev/ui/components/database-schema-node
- ChartDB — github.com/chartdb/chartdb (React Flow + shadcn/ui + TypeScript ERD tool)
- DrawDB — github.com/drawdb-io/drawdb (browser-based database diagram editor)
- relliv/crows-foot-notations — github.com/relliv/crows-foot-notations (SVG symbol reference)
- Peter Chen, "The Entity-Relationship Model — Toward a Unified View of Data" (1976)
