---
name: canvas-bubble-animation-grouping
category: frontend
version: 1.0.0
contributed: 2026-02-27
contributor: scribe-bible
last_updated: 2026-02-27
tags: [canvas, animation, framer-motion, bubble-chart, grouping, layout-algorithm, data-visualization, react, golden-spiral, rectangular-grid]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Canvas Bubble Animation & Grouping Patterns

## Problem

You have a large collection of items (100-500+) that need to be visualized as bubbles on a canvas. Users switch between multiple view modes (e.g., "by category", "by author", "by feature"), and bubbles should smoothly animate to new positions in each mode. The modes require fundamentally different layouts:

- **Overview**: All items in a single cluster (spiral)
- **Grouped modes**: Items clustered into labeled groups (rectangular grids)
- **Filter modes**: Binary split — items with/without a feature (quadrants)

Flex-wrap layouts can't handle this — you need absolute positioning with computed coordinates, but the items must still animate smoothly between modes.

## Solution Pattern

Use **Framer Motion absolute-positioned bubbles** with a **layout algorithm registry**. Each mode computes `(x, y, opacity, scale)` for every item. When the mode changes, React re-renders with new coordinates, and Framer Motion's `spring` transition animates each bubble to its new position.

Three layout algorithms cover all common data visualization needs:

1. **Golden-angle spiral** — uniform radial distribution for "all items" overview
2. **Rectangular grid packing** — items arranged in rows/columns within labeled group clusters
3. **Binary filter quadrants** — items split into "has feature" / "doesn't have feature" regions

### Architecture

```
ViewMode → layout algorithm → Map<id, {x, y, opacity, scale}> + GroupLabel[]
                                            ↓
                         Framer Motion spring transition animates delta
```

- **Pure functions** compute positions from `(mode, items, canvasWidth, canvasHeight)` — no side effects
- **`useMemo`** recomputes only when mode, items, or container size changes
- **Dynamic canvas height** — grouped modes return `totalHeight` so the container expands to fit content
- **Bubble size by data** — each item's size is proportional to a data attribute (e.g., verse count), scaled down in grouped modes via `GROUPED_BUBBLE_SCALE`

## Code Example

### 1. Golden-Angle Spiral (Overview)

```typescript
function packInCircle(count: number, cx: number, cy: number, maxRadius: number) {
  if (count === 0) return [];
  if (count === 1) return [{ x: cx, y: cy }];

  const goldenAngle = Math.PI * (3 - Math.sqrt(5));
  const positions: { x: number; y: number }[] = [];

  for (let i = 0; i < count; i++) {
    const r = maxRadius * Math.sqrt(i / count) * 0.9;
    const theta = i * goldenAngle;
    positions.push({
      x: cx + r * Math.cos(theta),
      y: cy + r * Math.sin(theta),
    });
  }
  return positions;
}
```

**When**: "Show all N items" mode. Distributes items uniformly in a circle with no gaps or clusters. The golden angle (137.5°) ensures even spacing at any count.

### 2. Rectangular Grid Packing (Grouped Modes)

```typescript
const GROUPED_BUBBLE_SCALE = 0.5;

function packInRect(
  count: number, cx: number, cy: number, avgBubbleSize: number, gap: number,
): { positions: { x: number; y: number }[]; gridW: number; gridH: number } {
  if (count === 0) return { positions: [], gridW: 0, gridH: 0 };
  if (count === 1) return { positions: [{ x: cx, y: cy }], gridW: avgBubbleSize, gridH: avgBubbleSize };

  const step = avgBubbleSize + gap;
  const cols = Math.ceil(Math.sqrt(count * 1.3)); // Slightly wider than tall
  const rows = Math.ceil(count / cols);
  const gridW = cols * step;
  const gridH = rows * step;
  const startX = cx - (gridW - step) / 2;
  const startY = cy - (gridH - step) / 2;

  const positions: { x: number; y: number }[] = [];
  for (let i = 0; i < count; i++) {
    positions.push({
      x: startX + (i % cols) * step,
      y: startY + Math.floor(i / cols) * step,
    });
  }
  return { positions, gridW, gridH };
}
```

**When**: Grouping by a categorical attribute (genre, author, category). Each group gets a labeled rectangular region with items laid out in a grid. The `1.3` aspect ratio factor creates rectangles that feel natural (slightly wider than tall).

### 3. Dynamic Grouped Layout with Row-Based Height

```typescript
function calculateGroupedCanvasPositions(
  mode: ViewMode, nodes: Item[], canvasWidth: number,
): { positions: Map<id, Pos>; labels: GroupLabel[]; totalHeight: number } {
  const groups = groupItems(nodes, mode);
  const positions = new Map();
  const labels: GroupLabel[] = [];

  // Pre-compute grid dimensions per group
  const groupMeta = groups.map(([name, items]) => {
    const avgSize = items.reduce((s, n) => s + getSize(n) * GROUPED_BUBBLE_SCALE, 0) / items.length;
    const step = avgSize + gap;
    const cols = Math.ceil(Math.sqrt(items.length * 1.3));
    const rows = Math.ceil(items.length / cols);
    return { name, items, avgSize, gridW: cols * step, gridH: rows * step };
  });

  // Adaptive column count based on group count
  const maxCols = groups.length <= 4 ? 2 : groups.length <= 9 ? 3 : 4;
  const layoutCols = Math.min(maxCols, groups.length);
  const cellW = (canvasWidth - padX * 2) / layoutCols;

  // Compute max height per layout row (for consistent row spacing)
  const rowMaxGridH: number[] = Array(layoutRows).fill(0);
  groupMeta.forEach((g, i) => {
    const row = Math.floor(i / layoutCols);
    rowMaxGridH[row] = Math.max(rowMaxGridH[row], g.gridH);
  });

  // Accumulate Y positions row by row
  let yAccum = 25;
  const rowCenterY: number[] = [];
  for (let r = 0; r < layoutRows; r++) {
    yAccum += labelHeight;
    rowCenterY.push(yAccum + rowMaxGridH[r] / 2);
    yAccum += rowMaxGridH[r] + rowGap;
  }
  const totalHeight = yAccum + 20;

  // Place each group
  groupMeta.forEach((g, i) => {
    const col = i % layoutCols;
    const row = Math.floor(i / layoutCols);
    const cx = padX + cellW * (col + 0.5);
    const cy = rowCenterY[row];

    labels.push({ name: g.name, x: cx, y: cy - g.gridH / 2 - 14, color, count: g.items.length });

    const grid = packInRect(g.items.length, cx, cy, g.avgSize, gap);
    g.items.forEach((item, j) => {
      positions.set(item.id, { ...grid.positions[j], opacity: 0.9, scale: 1 });
    });
  });

  return { positions, labels, totalHeight };
}
```

**Key technique**: The canvas height is **dynamic** — computed from the actual content. The container's `style.height` reads `totalHeight` so groups never overflow or leave empty space.

### 4. Binary Filter Quadrants

```typescript
function calculateFilterPositions(mode: string, nodes: Item[], w: number, h: number) {
  const filter = FILTERS[mode]; // e.g., (item) => item.hasFeature
  const members = nodes.filter(filter);
  const nonMembers = nodes.filter(n => !filter(n));

  const positions = new Map();

  // Members: bright, full-size, in the feature's quadrant
  const memberPositions = packInCircle(members.length, quadrant.cx, quadrant.cy, quadrant.radius);
  members.forEach((node, i) => {
    positions.set(node.id, { ...memberPositions[i], opacity: 1, scale: 1 });
  });

  // Non-members: faded, small, pushed to opposite corner
  const nonMemberPositions = packInCircle(nonMembers.length, fadedCx, fadedCy, fadedRadius);
  nonMembers.forEach((node, i) => {
    positions.set(node.id, { ...nonMemberPositions[i], opacity: 0.12, scale: 0.5 });
  });

  return positions;
}
```

**When**: Showing which items have/don't have a boolean attribute. Members glow in a labeled quadrant; non-members fade to near-invisible in the opposite corner.

### 5. Bubble Component with Spring Animation

```tsx
<motion.button
  style={{
    position: 'absolute',
    left: x,
    top: y,
    width: size,
    height: size,
    borderRadius: '50%',
    backgroundColor: color,
    transform: 'translate(-50%, -50%)',
  }}
  animate={{ left: x, top: y, opacity, scale }}
  transition={{
    type: 'spring',
    stiffness: 300,
    damping: 25,
    delay: index * 0.006,  // Staggered animation
  }}
  whileHover={{ scale: 1.3, zIndex: 50 }}
  whileTap={{ scale: 0.9 }}
/>
```

**Stagger delay**: `index * 0.006` creates a wave effect (0.9s total for 150 items) where bubbles fly to their positions in sequence rather than all at once.

## Implementation Steps

1. **Define view modes** as a union type with three categories: overview, grouped (genre/author/category), and filter (has/doesn't have feature)
2. **Create pure layout functions** — each takes `(mode, items, width, height)` and returns `Map<id, {x, y, opacity, scale}>` plus optional labels
3. **Wrap in `useMemo`** keyed on `[viewMode, items, containerSize]`
4. **Use `ResizeObserver`** on the canvas container to get responsive dimensions
5. **Render absolute-positioned Framer Motion elements** with `animate` set to computed coordinates
6. **Compute dynamic canvas height** for grouped modes — return `totalHeight` from the layout function
7. **Scale bubbles** in grouped modes (`GROUPED_BUBBLE_SCALE = 0.5`) to prevent overcrowding
8. **Add group labels** as absolute-positioned divs above each cluster

## When to Use

- Data exploration dashboards with 50-500+ items and multiple grouping modes
- Bubble charts where items have categorical attributes AND a size metric
- Any visualization where items must animate between fundamentally different spatial arrangements
- When you need three+ distinct layout strategies in one component

## When NOT to Use

- Small item counts (<20) — a simple flex-wrap with `layoutId` is simpler (see `framer-motion-layoutid-grouping`)
- Items that only need to sort within the same grid — CSS `order` + `transition` suffices
- Graph/network visualizations — use React Flow or D3 force layouts instead
- Mobile-only UIs — canvas layouts need 700px+ width to be useful

## Common Mistakes

- **Using full emotional tone strings as group keys** — multi-word comma-separated strings create 100+ unique groups. Extract the **primary word** (`tone.split(',')[0].trim()`) to get ~10 meaningful groups.
- **Circle packing for large groups** — `packInCircle` makes dense groups (70+ items) into an indistinguishable blob. Use `packInRect` for grouped modes where individual items must be selectable.
- **Fixed canvas height** — a 700px fixed height works for overview/filter but overflows for grouped modes with 10+ groups. Always compute `totalHeight` from content and set `height: Math.max(totalHeight, minHeight)`.
- **Uniform bubble size in groups** — loses the data dimension. Keep `getSize(item) * GROUPED_BUBBLE_SCALE` so the largest items are still visually prominent within their grid cells.
- **Forgetting `translate(-50%, -50%)`** — bubble positions are computed as center points. Without centering the transform, bubbles offset by half their diameter.
- **Too many grid columns** — with 3 groups, use 2 columns (not 3) for breathing room. Adaptive: `groups.length <= 4 ? 2 : groups.length <= 9 ? 3 : 4`.

## Related Skills

- [framer-motion-layoutid-grouping](framer-motion-layoutid-grouping.md) — Flex-wrap approach for smaller collections (<100 items)
- [domain-specific-layout-algorithms](../patterns-standards/domain-specific-layout-algorithms.md) — Pure-function layout registry pattern
- [svg-sparkline-no-charting-library](svg-sparkline-no-charting-library.md) — Lightweight data visualization with zero dependencies

## References

- Golden angle distribution: https://en.wikipedia.org/wiki/Golden_angle
- Framer Motion spring physics: https://www.framer.com/motion/transition/#spring
- Discovered in: scribe-bible PsalmOverview (150 psalms, 9 view modes, 3 layout algorithms)
- Evolved through 3 iterations: circle packing → content-derived radius → rectangular grid
