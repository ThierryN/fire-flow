---
name: domain-specific-layout-algorithms
category: patterns-standards
version: 1.0.0
contributed: 2026-02-26
contributor: scribe-bible
last_updated: 2026-02-26
tags: [layout, algorithm, graph, visualization, react-flow, spatial, domain-driven]
difficulty: hard
usage_count: 0
success_rate: 100
---

# Domain-Specific Layout Algorithms

## Problem

Generic graph layout algorithms (dagre, force-directed, radial) arrange nodes mathematically but ignore domain semantics. A chiastic literary structure should look like an arc/mirror, not a random force graph. Parallel ideas should be in lanes, not scattered. Your domain has spatial metaphors that users intuitively understand, but no charting library provides layouts that encode domain meaning.

## Solution Pattern

Create a **layout algorithm registry** — a set of pure functions that each take `(nodes, edges, options)` and return repositioned nodes. Each function encodes one domain-specific spatial metaphor. Wire them into your existing layout engine's switch statement so they integrate seamlessly with generic algorithms.

The pattern: layout functions are **pure position calculators**. They don't render anything — they just assign `x, y` coordinates to nodes based on domain rules. The rendering layer (React Flow, D3, Canvas) handles display.

## Code Example

```typescript
// ─── Type Contract ──────────────────────────────────────
interface GraphNode {
  id: string;
  position: { x: number; y: number };
  data: Record<string, any>;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
}

interface LayoutOptions {
  spacing?: number;
  centerX?: number;
  centerY?: number;
}

type LayoutFunction = (
  nodes: GraphNode[],
  edges: GraphEdge[],
  options: LayoutOptions
) => GraphNode[];

// ─── Domain Layout: Mirror Arc (for chiastic/symmetric structures) ─────
export function layoutMirrorArc(
  nodes: GraphNode[],
  edges: GraphEdge[],
  options: LayoutOptions
): GraphNode[] {
  const { spacing = 200, centerX = 400, centerY = 300 } = options;
  const n = nodes.length;
  const mid = Math.floor(n / 2);

  return nodes.map((node, i) => {
    // Distance from center (0 at edges, max at midpoint)
    const distFromMid = Math.abs(i - mid);
    const indent = (mid - distFromMid) * (spacing * 0.4);

    return {
      ...node,
      position: {
        x: centerX + indent,              // Indent toward center = arc shape
        y: (i * spacing * 0.7),           // Vertical stack
      },
    };
  });
}

// ─── Domain Layout: Parallel Lanes (for parallel/synonymous structures) ─
export function layoutParallelLanes(
  nodes: GraphNode[],
  edges: GraphEdge[],
  options: LayoutOptions
): GraphNode[] {
  const { spacing = 200 } = options;

  // Split into pairs (A-line, B-line)
  return nodes.map((node, i) => {
    const pairIndex = Math.floor(i / 2);
    const isLineB = i % 2 === 1;

    return {
      ...node,
      position: {
        x: isLineB ? spacing * 2 : 0,     // Two columns
        y: pairIndex * spacing * 0.8,       // Aligned rows
      },
    };
  });
}

// ─── Domain Layout: Ascending Staircase (for climactic/progressive) ─────
export function layoutAscendingStaircase(
  nodes: GraphNode[],
  edges: GraphEdge[],
  options: LayoutOptions
): GraphNode[] {
  const { spacing = 200 } = options;

  return nodes.map((node, i) => ({
    ...node,
    position: {
      x: i * spacing * 0.6,               // Step right
      y: (nodes.length - 1 - i) * spacing * 0.5, // Step up (y=0 is top)
    },
  }));
}

// ─── Domain Layout: Narrative Arc (parabolic curve) ─────────────────────
export function layoutNarrativeArc(
  nodes: GraphNode[],
  edges: GraphEdge[],
  options: LayoutOptions
): GraphNode[] {
  const { spacing = 200, centerY = 300 } = options;
  const n = nodes.length;
  const peakHeight = spacing * 2;

  return nodes.map((node, i) => {
    const t = n > 1 ? i / (n - 1) : 0.5;    // 0 to 1
    const y = -4 * peakHeight * t * (t - 1);  // Parabola: peak at midpoint

    return {
      ...node,
      position: {
        x: i * spacing,
        y: centerY - y,                       // Invert for screen coords
      },
    };
  });
}

// ─── Registry: Wire into layout engine ──────────────────
const LAYOUT_REGISTRY: Record<string, LayoutFunction> = {
  // Generic algorithms
  'dagre': layoutDagre,
  'force': layoutForce,
  'radial': layoutRadial,
  // Domain-specific algorithms
  'mirror-arc': layoutMirrorArc,
  'parallel-lanes': layoutParallelLanes,
  'ascending-staircase': layoutAscendingStaircase,
  'narrative-arc': layoutNarrativeArc,
};

export function applyLayout(
  nodes: GraphNode[],
  edges: GraphEdge[],
  options: LayoutOptions & { algorithm: string }
): GraphNode[] {
  const layoutFn = LAYOUT_REGISTRY[options.algorithm];
  if (!layoutFn) throw new Error(`Unknown layout: ${options.algorithm}`);
  return layoutFn(nodes, edges, options);
}
```

## Implementation Steps

1. Define a `LayoutFunction` type signature: `(nodes, edges, options) => nodes`
2. Identify your domain's spatial metaphors (what shapes do experts draw on whiteboards?)
3. Implement each metaphor as a pure function that assigns `x, y` positions
4. Create a registry mapping algorithm names to functions
5. Wire the registry into your existing `applyLayout()` switch/dispatch
6. Extend your `LayoutAlgorithm` TypeScript union type with the new names
7. Add UI buttons/dropdown to let users select domain-specific layouts

## When to Use

- You have domain concepts with natural spatial representations (hierarchy, timeline, symmetry, opposition, progression, cycles)
- Generic layouts (force, dagre) produce technically correct but semantically meaningless graphs
- Your users think in domain-specific spatial terms ("chiastic structure", "parallel tracks", "escalation ladder")
- You already have a graph visualization framework (React Flow, D3, Cytoscape)

## When NOT to Use

- Generic data with no domain-specific spatial meaning
- When dagre/force layouts are sufficient for the use case
- Small graphs (<5 nodes) where layout differences are imperceptible
- When users expect standard graph layouts (network diagrams, org charts)

## Common Mistakes

- Making layout functions impure (fetching data, mutating state) — keep them as pure position calculators
- Hardcoding pixel values — use the `spacing` option so layouts scale
- Forgetting edge cases: 0 nodes, 1 node, odd/even counts
- Not providing a fallback layout when node count doesn't match expected structure
- Coupling layout logic to the rendering framework — keep layouts as plain `{x, y}` calculators

## Related Skills

- [react-flow-animated-layout-switching](../_general/frontend/react-flow-animated-layout-switching.md) — Animate transitions between layouts
- [fullstack-bible-study-platform](fullstack-bible-study-platform.md) — Platform where these patterns were proven

## References

- Dagre.js: https://github.com/dagrejs/dagre (generic directed graph layout)
- Discovered in: scribe-bible theological layouts (Phases 1 & 3)
- 14 domain-specific layout algorithms: 7 for parallelism viewer, 7 for shared concept map engine
- Spatial metaphors: chiastic mirror arcs, parallel lanes, antithetical opposing splits, climactic ascending staircases, cascade waterfalls, concentric rings, narrative parabolic arcs
