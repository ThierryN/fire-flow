---
name: svg-sparkline-no-charting-library
category: frontend
version: 1.0.0
contributed: 2026-02-26
contributor: scribe-bible
last_updated: 2026-02-26
tags: [svg, sparkline, chart, visualization, react, lightweight, no-dependencies]
difficulty: easy
usage_count: 0
success_rate: 100
---

# SVG Sparkline Without Charting Library

## Problem

You need a compact frequency/distribution chart (sparkline) in a React app but don't want to add D3.js (~230KB), Chart.js (~180KB), or Recharts (~140KB) as dependencies. The chart is simple — thin bars showing values across categories — but charting libraries bring configuration overhead and bundle bloat for what's essentially a few SVG rectangles.

## Solution Pattern

Build the sparkline as a **pure SVG component** using React. Use `viewBox` with percentage-based bar widths for automatic responsiveness. Each bar is a `<rect>` element with height proportional to its value. Add interactivity with React state for hover/click.

The pattern: `viewBox="0 0 100 {height}"` creates a percentage coordinate system where bar widths are `100 / count` — the SVG scales to any container width automatically via `preserveAspectRatio="none"`.

## Code Example

```tsx
interface SparklineProps {
  data: { label: string; value: number; color: string }[];
  height?: number;
  onBarClick?: (label: string) => void;
}

function Sparkline({ data, height = 60, onBarClick }: SparklineProps) {
  const [hovered, setHovered] = useState<number | null>(null);
  const max = Math.max(...data.map(d => d.value), 1);
  const barWidth = 100 / data.length;
  const gap = 0.15; // percentage gap between bars

  return (
    <div className="relative">
      <svg
        viewBox={`0 0 100 ${height}`}
        preserveAspectRatio="none"
        className="w-full cursor-pointer"
        style={{ height: `${height}px` }}
      >
        {data.map((d, i) => {
          const barH = d.value > 0
            ? Math.max((d.value / max) * (height - 4), 2) // min 2px visible
            : 0;
          return (
            <rect
              key={i}
              x={i * barWidth + gap / 2}
              y={height - barH}
              width={barWidth - gap}
              height={barH}
              fill={d.color}
              opacity={hovered !== null ? (hovered === i ? 1 : 0.3) : 0.75}
              rx={0.3}
              className="transition-opacity duration-150"
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
              onClick={() => d.value > 0 && onBarClick?.(d.label)}
            />
          );
        })}
      </svg>

      {/* Hover tooltip */}
      {hovered !== null && (
        <div
          className="absolute -top-10 bg-gray-900 text-white text-xs rounded px-2 py-1 pointer-events-none"
          style={{
            left: `${(hovered / data.length) * 100}%`,
            transform: 'translateX(-50%)',
          }}
        >
          {data[hovered].label}: {data[hovered].value}
        </div>
      )}
    </div>
  );
}
```

## Implementation Steps

1. Define `viewBox="0 0 100 {height}"` — 100-unit wide coordinate system
2. Calculate `barWidth = 100 / data.length` for even distribution
3. Normalize bar heights: `(value / maxValue) * (height - padding)`
4. Set minimum visible height (e.g., `Math.max(barH, 2)`) so small values aren't invisible
5. Use `preserveAspectRatio="none"` so SVG stretches to container width
6. Add hover state with opacity dimming on non-hovered bars
7. Position tooltip using percentage left offset

## When to Use

- Compact distribution charts (frequency across categories, activity over time)
- Inline sparklines in tables, cards, or dashboards
- When bundle size matters (0KB added vs 140-230KB for a charting library)
- When you need full control over styling (Tailwind classes work directly)
- Simple bar/column charts with <200 data points

## When NOT to Use

- Complex charts (line, area, scatter, pie) — use a library
- Charts with axes, legends, gridlines, zoom, pan — use Recharts/D3
- Real-time streaming data with >60fps updates — use Canvas/WebGL
- Charts that need accessibility features (ARIA roles, keyboard navigation)

## Common Mistakes

- Using `preserveAspectRatio="xMidYMid meet"` (default) — bars don't stretch to fill width
- Forgetting minimum bar height — values of 1 when max is 10000 become invisible
- Not handling zero values — `height={0}` rect still renders a hairline in some browsers
- Using pixel-based widths instead of viewBox percentages — breaks responsiveness
- Placing tooltip inside the SVG — HTML tooltips are easier to style than SVG text

## Related Skills

- [react-flow-animated-layout-switching](react-flow-animated-layout-switching.md) — Graph visualizations
- [framer-motion-layoutid-grouping](framer-motion-layoutid-grouping.md) — Animated data transitions

## References

- SVG viewBox specification: https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/viewBox
- Discovered in: scribe-bible word study frequency sparkline (Phase 5)
- 66-bar Bible book distribution chart — zero dependencies, full interactivity
