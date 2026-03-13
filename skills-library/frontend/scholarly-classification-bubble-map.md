---
name: scholarly-classification-bubble-map
category: frontend
version: 1.0.0
contributed: 2026-02-27
contributor: scribe-bible
last_updated: 2026-02-27
contributors:
  - scribe-bible
tags: [react, framer-motion, data-visualization, bubble-chart, classification, canvas-layout, animation]
difficulty: medium
usage_count: 1
success_rate: 100
---

# Scholarly Classification Bubble Map

## Problem

You have a fixed set of items (e.g., 150 psalms, 31 proverbs chapters, 22 revelation chapters) that multiple academic/scholarly systems classify differently. You need a visual explorer that:
- Shows all items as animated bubbles in a golden-angle spiral ("All" mode)
- Groups items into rectangular grid clusters by any selected classification system
- Switches between systems with animated transitions
- Provides hover tooltips with classification details
- Adapts canvas height dynamically to content density

Static lists and tables don't convey the distribution patterns. Users need to *see* how different scholars divide the same corpus.

## Solution Pattern

### Architecture (3-file pattern)

1. **Classification Data File** (`classification-systems.ts`)
   - Define `ClassificationSystem` interface: id, scholar, title, year, methodology, categories[], classifications{}
   - Each category has: id, name, description, color (hex)
   - Each classification maps item number -> { primary, secondary?, notes? }
   - Export helper functions: `getSystem()`, `getItemsByCategory()`, `getCategoryInfo()`, `getSystemStats()`
   - All data is client-side (no API calls needed)

2. **Item Data File** (`item-data.ts`)
   - Item metadata: size values (e.g., verse counts), authors, genres
   - `getBubbleSize(itemNumber)` — maps count to pixel size (32-72px range)
   - Color mappings for non-scholarly groupings

3. **Bubble Map Component** (`ScholarlyOverview.tsx`)
   - Mode selector: "All" + one button per classification system
   - Canvas with absolute-positioned bubbles via existing `PsalmBubble` component
   - Two layout algorithms: `packInCircle()` for spiral, `packInRect()` for grid clusters
   - Group labels positioned above each cluster
   - Hover tooltip with item details + classification info
   - "Color by" selector in "All" mode
   - Category legend when a specific system is selected
   - Scholar info card with name, title, year, methodology

### Layout Algorithms

**Golden-angle spiral** (for "All" mode):
```typescript
function packInCircle(count: number, cx: number, cy: number, maxRadius: number) {
  const goldenAngle = Math.PI * (3 - Math.sqrt(5));
  const positions = [];
  for (let i = 0; i < count; i++) {
    const r = maxRadius * Math.sqrt(i / count) * 0.9;
    const theta = i * goldenAngle;
    positions.push({ x: cx + r * Math.cos(theta), y: cy + r * Math.sin(theta) });
  }
  return positions;
}
```

**Rectangular grid clusters** (for grouped modes):
```typescript
function packInRect(count: number, cx: number, cy: number, avgSize: number, gap: number) {
  const step = avgSize + gap;
  const cols = Math.ceil(Math.sqrt(count * 1.3)); // slightly wider than square
  const rows = Math.ceil(count / cols);
  // Position items in grid centered at (cx, cy)
}
```

**Dynamic canvas height** — compute total height from group count and grid dimensions:
- Few groups (Brueggemann: 3) = short canvas
- Many groups (Gunkel: 16) = tall canvas
- Use `Math.max(computedHeight, 400)` for minimum

### Integration Pattern

Add as a toggle button in the parent page, mutually exclusive with other overview panels:
```tsx
<button onClick={() => { setShowScholarlyOverview(!show); setShowOther(false); }}>
  <Layers /> Scholarly Overview
</button>
{showScholarlyOverview && (
  <ScholarlyOverview onItemSelect={(num) => { setItem(num); setShow(false); }} />
)}
```

## Implementation Steps

1. Research 5-8 scholarly classification systems for your corpus
2. Create `classification-systems.ts` with all systems, categories, and per-item classifications
3. Create or extend `item-data.ts` with size data and helper functions
4. Build the bubble map component following the 3-section pattern:
   - System selector bar (buttons with category counts)
   - Canvas with bubbles + labels + tooltip
   - Legend + info card
5. Integrate into parent page with toggle button
6. Verify: TypeScript clean, all items render, system switching animates

## When to Use

- Visualizing items classified by multiple academic/scholarly frameworks
- Any corpus where different experts categorize the same items differently
- Interactive exploration of classification distributions
- Bible books, literary works, historical artifacts, species taxonomies

## When NOT to Use

- Items without multiple classification systems (just use a simple grouped list)
- Very large datasets (1000+ items) — canvas positioning becomes slow
- When classification data isn't available client-side (would need API)
- Simple category filters (use dropdown + list instead)

## Common Mistakes

- Forgetting to handle items not classified in a system (provide fallback position/color)
- Not making canvas height dynamic — fixed height cuts off groups or wastes space
- Using D3.js when Framer Motion + absolute positioning suffices (simpler, no extra dep)
- Not sorting groups by size (largest first) — layout looks unbalanced otherwise
- Skipping the "Color by" selector in "All" mode — users can't compare systems without it

## Key Dependencies

- `framer-motion` — AnimatePresence + motion.div for tooltip animations
- `PsalmBubble` (or equivalent) — reusable bubble component with spring transitions
- `ResizeObserver` — responsive container sizing
- CSS custom properties for theming (`var(--bg-primary)`, etc.)

## Related Skills

- Canvas Bubble Animation patterns
- React Flow graph visualization
- Data-driven layout algorithms

## References

- Implemented in: scribe-bible (Psalms scholarly classification)
- Files: `ScholarlyOverview.tsx`, `classification-systems.ts`, `psalm-data.ts`
- Path: `frontend/src/components/Poetry/`
