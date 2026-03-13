---
name: framer-motion-layoutid-grouping
category: frontend
version: 1.0.0
contributed: 2026-02-26
contributor: scribe-bible
last_updated: 2026-02-26
tags: [framer-motion, animation, FLIP, layout, grouping, sorting, react]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Framer Motion layoutId Bubble Grouping

## Problem

You have a collection of items (cards, bubbles, tiles) that can be sorted/grouped by different criteria. When the user switches sort mode, items should smoothly animate to their new positions in the new groups — not just re-render instantly. Traditional approaches require manually calculating FLIP (First, Last, Invert, Play) coordinates. CSS Grid/Flexbox reflows don't animate.

## Solution Pattern

Use Framer Motion's `layoutId` prop on `motion.div` or `motion.button` elements. When items move between groups (different parent containers), Framer Motion automatically calculates the FLIP animation — measuring the element's position before and after the React re-render, then animating the transform.

The key: each item needs a **stable, unique `layoutId`** that persists across re-renders. When React re-renders with new grouping, Framer Motion finds the same `layoutId` in a different position and animates the transition.

## Code Example

```tsx
import { motion, AnimatePresence } from 'framer-motion';

interface Item {
  id: string;
  name: string;
  category: string;
  author: string;
  size: number;
}

type SortMode = 'category' | 'author' | 'size';

function GroupedBubbles({ items }: { items: Item[] }) {
  const [sortMode, setSortMode] = useState<SortMode>('category');

  // Regroup items whenever sort mode changes
  const groups = useMemo(() => {
    const map = new Map<string, Item[]>();
    items.forEach(item => {
      const key = sortMode === 'size'
        ? (item.size > 100 ? 'Large' : 'Small')
        : item[sortMode];
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(item);
    });
    return map;
  }, [items, sortMode]);

  return (
    <div>
      {/* Sort mode buttons */}
      <div className="flex gap-2 mb-4">
        {(['category', 'author', 'size'] as SortMode[]).map(mode => (
          <button
            key={mode}
            onClick={() => setSortMode(mode)}
            className={sortMode === mode ? 'bg-blue-500 text-white' : 'bg-gray-200'}
          >
            By {mode}
          </button>
        ))}
      </div>

      {/* Grouped items */}
      {Array.from(groups.entries()).map(([group, groupItems]) => (
        <div key={group} className="mb-6">
          <h3 className="text-lg font-bold">{group}</h3>
          <div className="flex flex-wrap gap-2">
            {groupItems.map(item => (
              <motion.button
                key={item.id}
                layoutId={`item-${item.id}`}  // STABLE ID — survives regrouping
                layout="position"              // Only animate position, not size
                transition={{
                  type: 'spring',
                  stiffness: 400,
                  damping: 30,
                }}
                whileHover={{ scale: 1.15 }}
                whileTap={{ scale: 0.95 }}
                className="rounded-full bg-blue-500 text-white flex items-center justify-center"
                style={{
                  width: `${Math.max(32, item.size * 0.4)}px`,
                  height: `${Math.max(32, item.size * 0.4)}px`,
                }}
              >
                {item.name}
              </motion.button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

## Implementation Steps

1. Install Framer Motion: `npm install framer-motion`
2. Wrap each item in a `motion.div` or `motion.button`
3. Assign a **stable `layoutId`** based on the item's unique ID (not array index)
4. Use `layout="position"` to animate only position (not size changes)
5. Configure spring physics: `stiffness: 400, damping: 30` for snappy natural motion
6. Memoize the grouping computation with `useMemo` to prevent unnecessary recalculations
7. Add `whileHover` and `whileTap` for interactive feedback

## When to Use

- Data explorers with multiple sort/group/filter modes
- Card grids that reorganize by category, date, status, etc.
- Tag clouds or bubble charts with dynamic grouping
- Dashboard widgets that can be rearranged
- Any collection where items move between visual groups

## When NOT to Use

- React Flow graphs — use CSS transitions on `.react-flow__node` instead (Framer Motion conflicts with React Flow's transform management)
- Lists with 500+ items — FLIP calculations on many elements cause frame drops
- Simple show/hide — use `AnimatePresence` with `initial`/`animate`/`exit` instead
- Server-side rendered content — `layoutId` animations only work client-side

## Common Mistakes

- Using array index as `layoutId` — items get wrong animations when array reorders
- Forgetting `layout="position"` — size changes also animate, causing distortion
- Setting `stiffness` too low (<200) — bubbles float sluggishly
- Setting `damping` too low (<15) — bubbles bounce excessively
- Not memoizing the grouping logic — React re-renders trigger redundant FLIP measurements
- Mixing `layoutId` with `AnimatePresence` incorrectly — use `layoutId` for movement, `AnimatePresence` for enter/exit

## Related Skills

- [react-flow-animated-layout-switching](react-flow-animated-layout-switching.md) — For graph node animations
- [svg-sparkline-no-charting-library](svg-sparkline-no-charting-library.md) — Lightweight data visualization

## References

- Framer Motion layout animations: https://www.framer.com/motion/layout-animations/
- FLIP technique (First, Last, Invert, Play): https://aerotwist.com/blog/flip-your-animations/
- Discovered in: scribe-bible PsalmsExplorer bubble graph (Phase 2)
- 150 psalm bubbles with 5 sort modes, spring physics, hover tooltips
