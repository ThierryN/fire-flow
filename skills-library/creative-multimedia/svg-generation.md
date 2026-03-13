# Programmatic SVG Generation
**Description:** Complete guide for generating, animating, optimizing, and using SVGs in web applications. Covers fundamentals, chart generation without libraries, React patterns, SMIL and CSS animation, accessibility, and optimization with SVGO.

**When to use:** Any project requiring icons, charts, infographics, logos, loading spinners, or illustrations generated programmatically — especially when you need crisp rendering at any scale, small file sizes, or dynamic data-driven graphics.

---

## SVG Fundamentals for AI Agents

### ViewBox and Coordinate System

```xml
<!-- viewBox="minX minY width height" -->
<!-- The SVG scales to fit its container while preserving the internal coordinate system -->
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <!-- Everything is drawn in a 100x100 coordinate space -->
  <!-- The actual display size is controlled by CSS width/height -->
</svg>
```

**Responsive sizing pattern:**

```xml
<!-- Width fills container, height auto-scales from viewBox aspect ratio -->
<svg viewBox="0 0 400 300" width="100%" xmlns="http://www.w3.org/2000/svg">
  <!-- 4:3 aspect ratio maintained at any container width -->
</svg>
```

### Basic Shapes

```xml
<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <!-- Rectangle -->
  <rect x="10" y="10" width="80" height="60" rx="8" fill="#7c3aed" />

  <!-- Circle -->
  <circle cx="200" cy="50" r="40" fill="#3b82f6" />

  <!-- Ellipse -->
  <ellipse cx="300" cy="50" rx="60" ry="30" fill="#10b981" />

  <!-- Line -->
  <line x1="10" y1="120" x2="390" y2="120" stroke="#94a3b8" stroke-width="2" />

  <!-- Polyline (open shape) -->
  <polyline points="10,200 80,150 150,180 220,140 290,170 360,130"
    fill="none" stroke="#f59e0b" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />

  <!-- Polygon (closed shape) -->
  <polygon points="200,210 230,270 170,270" fill="#ef4444" />

  <!-- Path (the universal shape — can draw anything) -->
  <path d="M 10 290 Q 100 230 200 290 T 390 290"
    fill="none" stroke="#8b5cf6" stroke-width="2" />
</svg>
```

### Path Commands Quick Reference

| Command | Meaning | Parameters |
|---------|---------|------------|
| `M` / `m` | Move to | `x y` |
| `L` / `l` | Line to | `x y` |
| `H` / `h` | Horizontal line | `x` |
| `V` / `v` | Vertical line | `y` |
| `C` / `c` | Cubic bezier | `x1 y1 x2 y2 x y` |
| `Q` / `q` | Quadratic bezier | `x1 y1 x y` |
| `A` / `a` | Arc | `rx ry rotation large-arc sweep x y` |
| `Z` | Close path | — |

Uppercase = absolute coordinates, lowercase = relative to current position.

### Text Elements

```xml
<svg viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg">
  <!-- Embedded font via style block -->
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700');
    .heading { font-family: 'Inter', sans-serif; font-weight: 700; }
    .body { font-family: 'Inter', sans-serif; font-weight: 400; }
  </style>

  <text x="200" y="40" text-anchor="middle" class="heading" font-size="24" fill="#1e293b">
    SVG Heading
  </text>
  <text x="200" y="70" text-anchor="middle" class="body" font-size="14" fill="#64748b">
    Subtitle text centered below
  </text>
</svg>
```

### Gradients and Patterns

```xml
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Linear gradient -->
    <linearGradient id="sunset" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f97316" />
      <stop offset="100%" stop-color="#ec4899" />
    </linearGradient>

    <!-- Radial gradient -->
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#7c3aed" stop-opacity="1" />
      <stop offset="100%" stop-color="#7c3aed" stop-opacity="0" />
    </radialGradient>

    <!-- Repeating pattern -->
    <pattern id="dots" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="10" cy="10" r="2" fill="#cbd5e1" />
    </pattern>
  </defs>

  <rect width="200" height="200" fill="url(#dots)" />
  <circle cx="100" cy="100" r="60" fill="url(#sunset)" />
  <circle cx="100" cy="100" r="80" fill="url(#glow)" />
</svg>
```

---

## Generation Patterns

### Icon Generation from Description

Generate SVG icons programmatically by composing path data:

```ts
// utils/svg-icons.ts

interface IconConfig {
  size?: number;
  color?: string;
  strokeWidth?: number;
}

export function generateCheckIcon({ size = 24, color = "currentColor", strokeWidth = 2 }: IconConfig = {}) {
  return `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M20 6L9 17L4 12" stroke="${color}" stroke-width="${strokeWidth}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`;
}

export function generateMenuIcon({ size = 24, color = "currentColor", strokeWidth = 2 }: IconConfig = {}) {
  return `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 12h18M3 6h18M3 18h18" stroke="${color}" stroke-width="${strokeWidth}" stroke-linecap="round"/>
</svg>`;
}

export function generateSpinnerIcon({ size = 24, color = "#7c3aed" }: IconConfig = {}) {
  return `<svg viewBox="0 0 24 24" width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="10" stroke="${color}" stroke-width="3" fill="none" opacity="0.25"/>
  <path d="M12 2a10 10 0 0 1 10 10" stroke="${color}" stroke-width="3" fill="none" stroke-linecap="round">
    <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
  </path>
</svg>`;
}
```

### Chart SVGs — No Library Required

#### Bar Chart

```ts
interface BarChartData {
  label: string;
  value: number;
}

export function generateBarChart(
  data: BarChartData[],
  width = 400,
  height = 250
) {
  const padding = { top: 20, right: 20, bottom: 40, left: 50 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;
  const maxVal = Math.max(...data.map((d) => d.value));
  const barWidth = chartW / data.length * 0.7;
  const gap = chartW / data.length * 0.3;

  const bars = data.map((d, i) => {
    const barH = (d.value / maxVal) * chartH;
    const x = padding.left + i * (barWidth + gap) + gap / 2;
    const y = padding.top + chartH - barH;

    return `
      <rect x="${x}" y="${y}" width="${barWidth}" height="${barH}" rx="4" fill="#7c3aed" opacity="0.9">
        <animate attributeName="height" from="0" to="${barH}" dur="0.6s" fill="freeze"
          begin="${i * 0.1}s" calcMode="spline" keySplines="0.25 0.46 0.45 0.94"/>
        <animate attributeName="y" from="${padding.top + chartH}" to="${y}" dur="0.6s" fill="freeze"
          begin="${i * 0.1}s" calcMode="spline" keySplines="0.25 0.46 0.45 0.94"/>
      </rect>
      <text x="${x + barWidth / 2}" y="${height - 10}" text-anchor="middle" font-size="11" fill="#64748b">
        ${d.label}
      </text>
      <text x="${x + barWidth / 2}" y="${y - 5}" text-anchor="middle" font-size="11" fill="#1e293b" font-weight="600">
        ${d.value}
      </text>`;
  }).join("");

  // Y-axis labels
  const yLabels = [0, maxVal * 0.25, maxVal * 0.5, maxVal * 0.75, maxVal].map((v, i) => {
    const y = padding.top + chartH - (i / 4) * chartH;
    return `<text x="${padding.left - 8}" y="${y + 4}" text-anchor="end" font-size="10" fill="#94a3b8">${Math.round(v)}</text>
    <line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="#e2e8f0" stroke-width="1"/>`;
  }).join("");

  return `<svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" style="font-family: system-ui, sans-serif">
  ${yLabels}
  ${bars}
</svg>`;
}
```

#### Pie Chart

```ts
interface PieSlice {
  label: string;
  value: number;
  color: string;
}

export function generatePieChart(data: PieSlice[], size = 200) {
  const cx = size / 2;
  const cy = size / 2;
  const r = size * 0.35;
  const total = data.reduce((sum, d) => sum + d.value, 0);

  let cumulativeAngle = -Math.PI / 2; // start at 12 o'clock
  const slices = data.map((d) => {
    const sliceAngle = (d.value / total) * Math.PI * 2;
    const startX = cx + r * Math.cos(cumulativeAngle);
    const startY = cy + r * Math.sin(cumulativeAngle);
    cumulativeAngle += sliceAngle;
    const endX = cx + r * Math.cos(cumulativeAngle);
    const endY = cy + r * Math.sin(cumulativeAngle);
    const largeArc = sliceAngle > Math.PI ? 1 : 0;

    // Label position (midpoint of arc)
    const midAngle = cumulativeAngle - sliceAngle / 2;
    const labelR = r * 1.35;
    const labelX = cx + labelR * Math.cos(midAngle);
    const labelY = cy + labelR * Math.sin(midAngle);

    return `<path d="M ${cx} ${cy} L ${startX} ${startY} A ${r} ${r} 0 ${largeArc} 1 ${endX} ${endY} Z"
      fill="${d.color}" stroke="white" stroke-width="2"/>
    <text x="${labelX}" y="${labelY}" text-anchor="middle" dominant-baseline="central"
      font-size="10" fill="#374151">${d.label} (${Math.round(d.value / total * 100)}%)</text>`;
  }).join("\n  ");

  return `<svg viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg" style="font-family: system-ui, sans-serif">
  ${slices}
</svg>`;
}
```

#### Line Chart

```ts
interface LinePoint {
  x: number; // index or timestamp
  y: number;
}

export function generateLineChart(
  data: LinePoint[],
  width = 400,
  height = 200,
  color = "#3b82f6"
) {
  const pad = { top: 20, right: 20, bottom: 30, left: 50 };
  const cw = width - pad.left - pad.right;
  const ch = height - pad.top - pad.bottom;
  const maxY = Math.max(...data.map((d) => d.y)) * 1.1;
  const minY = Math.min(...data.map((d) => d.y)) * 0.9;

  const points = data.map((d, i) => {
    const px = pad.left + (i / (data.length - 1)) * cw;
    const py = pad.top + ch - ((d.y - minY) / (maxY - minY)) * ch;
    return `${px},${py}`;
  });

  const polyline = points.join(" ");

  // Area fill (closed path under the line)
  const firstX = pad.left;
  const lastX = pad.left + cw;
  const bottomY = pad.top + ch;
  const areaPath = `M ${firstX},${bottomY} L ${points.map((p) => `L ${p}`).join(" ")} L ${lastX},${bottomY} Z`;

  // Data point dots
  const dots = points.map((p) => {
    const [x, y] = p.split(",");
    return `<circle cx="${x}" cy="${y}" r="3" fill="${color}" stroke="white" stroke-width="1.5"/>`;
  }).join("\n  ");

  return `<svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" style="font-family: system-ui, sans-serif">
  <defs>
    <linearGradient id="area-fill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${color}" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="${color}" stop-opacity="0.02"/>
    </linearGradient>
  </defs>
  <path d="${areaPath}" fill="url(#area-fill)"/>
  <polyline points="${polyline}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  ${dots}
</svg>`;
}
```

### Logo Generation — Geometric Shapes + Text

```ts
export function generateLogo(
  text: string,
  accentColor = "#7c3aed",
  size = 200
) {
  const firstLetter = text.charAt(0).toUpperCase();

  return `<svg viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="logo-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="${accentColor}"/>
      <stop offset="100%" stop-color="${adjustBrightness(accentColor, -30)}"/>
    </linearGradient>
  </defs>

  <!-- Background shape -->
  <rect width="${size}" height="${size}" rx="${size * 0.2}" fill="url(#logo-bg)"/>

  <!-- Letter -->
  <text x="50%" y="54%" text-anchor="middle" dominant-baseline="central"
    font-family="system-ui, sans-serif" font-weight="800" font-size="${size * 0.5}"
    fill="white" letter-spacing="-2">${firstLetter}</text>
</svg>`;
}

function adjustBrightness(hex: string, amount: number): string {
  const num = parseInt(hex.replace("#", ""), 16);
  const r = Math.min(255, Math.max(0, ((num >> 16) & 0xff) + amount));
  const g = Math.min(255, Math.max(0, ((num >> 8) & 0xff) + amount));
  const b = Math.min(255, Math.max(0, (num & 0xff) + amount));
  return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, "0")}`;
}
```

---

## Animation

### SMIL Animations (Built into SVG)

```xml
<!-- Pulsing circle -->
<circle cx="50" cy="50" r="20" fill="#7c3aed">
  <animate attributeName="r" values="20;25;20" dur="2s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="1;0.6;1" dur="2s" repeatCount="indefinite"/>
</circle>

<!-- Rotating element -->
<rect x="40" y="40" width="20" height="20" fill="#3b82f6">
  <animateTransform attributeName="transform" type="rotate"
    from="0 50 50" to="360 50 50" dur="3s" repeatCount="indefinite"/>
</rect>

<!-- Color transition -->
<rect width="100" height="100" rx="10">
  <animate attributeName="fill" values="#7c3aed;#3b82f6;#10b981;#7c3aed" dur="4s" repeatCount="indefinite"/>
</rect>

<!-- Motion along a path -->
<circle r="5" fill="#ef4444">
  <animateMotion dur="3s" repeatCount="indefinite" path="M 10,80 Q 100,10 200,80 T 390,80"/>
</circle>
```

### CSS Animations on SVG Elements

```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <style>
    @keyframes float {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-8px); }
    }
    @keyframes fadeRotate {
      from { opacity: 0.3; transform: rotate(0deg); }
      to { opacity: 1; transform: rotate(360deg); }
    }
    .floating { animation: float 3s ease-in-out infinite; }
    .spinning { animation: fadeRotate 2s linear infinite; transform-origin: 50px 50px; }
  </style>

  <circle cx="50" cy="50" r="15" fill="#7c3aed" class="floating"/>
  <rect x="35" y="35" width="30" height="30" rx="4" fill="none" stroke="#3b82f6" stroke-width="2" class="spinning"/>
</svg>
```

### Animated Loading Spinners

```xml
<!-- Spinner 1: Rotating arc -->
<svg viewBox="0 0 50 50" width="40" height="40" xmlns="http://www.w3.org/2000/svg">
  <circle cx="25" cy="25" r="20" fill="none" stroke="#e2e8f0" stroke-width="4"/>
  <circle cx="25" cy="25" r="20" fill="none" stroke="#7c3aed" stroke-width="4"
    stroke-linecap="round" stroke-dasharray="80 126">
    <animateTransform attributeName="transform" type="rotate"
      from="0 25 25" to="360 25 25" dur="1s" repeatCount="indefinite"/>
  </circle>
</svg>

<!-- Spinner 2: Three bouncing dots -->
<svg viewBox="0 0 80 20" width="80" height="20" xmlns="http://www.w3.org/2000/svg">
  <circle cx="10" cy="10" r="6" fill="#7c3aed">
    <animate attributeName="cy" values="10;4;10" dur="0.6s" repeatCount="indefinite"/>
  </circle>
  <circle cx="30" cy="10" r="6" fill="#7c3aed">
    <animate attributeName="cy" values="10;4;10" dur="0.6s" begin="0.15s" repeatCount="indefinite"/>
  </circle>
  <circle cx="50" cy="10" r="6" fill="#7c3aed">
    <animate attributeName="cy" values="10;4;10" dur="0.6s" begin="0.3s" repeatCount="indefinite"/>
  </circle>
</svg>

<!-- Spinner 3: Morphing square to circle -->
<svg viewBox="0 0 50 50" width="40" height="40" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="30" height="30" fill="#7c3aed">
    <animate attributeName="rx" values="0;15;0" dur="1.5s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="rotate"
      from="0 25 25" to="360 25 25" dur="1.5s" repeatCount="indefinite"/>
  </rect>
</svg>
```

### Path Drawing Animation (stroke-dasharray + stroke-dashoffset)

```xml
<!-- The classic "drawing" effect -->
<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
  <style>
    .draw-path {
      stroke-dasharray: 500;       /* Total path length (use getTotalLength() to measure) */
      stroke-dashoffset: 500;      /* Start fully hidden */
      animation: draw 2s ease-out forwards;
    }
    @keyframes draw {
      to { stroke-dashoffset: 0; }
    }
  </style>

  <path class="draw-path" d="M 10 80 Q 50 10 100 50 T 190 30"
    fill="none" stroke="#7c3aed" stroke-width="3" stroke-linecap="round"/>
</svg>
```

```tsx
// React: measure path length dynamically
import { useRef, useEffect, useState } from "react";

function DrawingPath({ d, color = "#7c3aed" }: { d: string; color?: string }) {
  const pathRef = useRef<SVGPathElement>(null);
  const [length, setLength] = useState(0);

  useEffect(() => {
    if (pathRef.current) {
      setLength(pathRef.current.getTotalLength());
    }
  }, [d]);

  return (
    <svg viewBox="0 0 200 100">
      <path
        ref={pathRef}
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={3}
        strokeLinecap="round"
        style={{
          strokeDasharray: length,
          strokeDashoffset: length,
          animation: length ? `draw 2s ease-out forwards` : "none",
        }}
      />
    </svg>
  );
}
```

---

## React SVG Patterns

### Inline SVG as JSX Components

```tsx
// components/icons/ArrowRight.tsx
interface IconProps {
  size?: number;
  color?: string;
  className?: string;
}

export function ArrowRight({ size = 24, color = "currentColor", className }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke={color}
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M5 12h14M12 5l7 7-7 7" />
    </svg>
  );
}
```

### SVGR — Import SVG Files as Components

```ts
// vite.config.ts
import svgr from "vite-plugin-svgr";

export default defineConfig({
  plugins: [
    react(),
    svgr({
      svgrOptions: {
        icon: true,           // Replaces width/height with 1em
        svgProps: { role: "img" },
      },
    }),
  ],
});
```

```tsx
// Usage — import SVG file as React component
import Logo from "./assets/logo.svg?react";

function Header() {
  return <Logo className="h-8 w-auto text-purple-600" />;
}
```

### Dynamic SVG with Props (Data-Driven)

```tsx
interface ProgressRingProps {
  progress: number;  // 0-100
  size?: number;
  strokeWidth?: number;
  color?: string;
}

export function ProgressRing({
  progress,
  size = 80,
  strokeWidth = 6,
  color = "#7c3aed",
}: ProgressRingProps) {
  const r = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * r;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {/* Background track */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke="#e2e8f0"
        strokeWidth={strokeWidth}
      />
      {/* Progress arc */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        style={{ transition: "stroke-dashoffset 0.5s ease" }}
      />
      {/* Center text */}
      <text
        x="50%"
        y="50%"
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={size * 0.22}
        fontWeight="700"
        fill="#1e293b"
      >
        {Math.round(progress)}%
      </text>
    </svg>
  );
}
```

---

## Optimization

### SVGO (SVG Optimizer)

Install: `npm install -D svgo`

```js
// svgo.config.js
module.exports = {
  multipass: true,
  plugins: [
    "preset-default",          // Includes removeDoctype, removeComments, cleanupIds, etc.
    "removeDimensions",        // Remove width/height, rely on viewBox
    "sortAttrs",               // Consistent attribute order
    {
      name: "removeAttrs",
      params: {
        attrs: ["data-name"],  // Remove editor-specific attributes
      },
    },
  ],
};
```

```bash
# CLI usage
npx svgo input.svg -o output.svg

# Batch optimize entire directory
npx svgo -f ./src/assets/icons -o ./src/assets/icons-optimized

# Show savings
npx svgo input.svg --pretty --indent=2
```

### Manual Optimization Checklist

1. **Remove metadata** — XML declarations, editor comments, `<metadata>` blocks
2. **Remove hidden elements** — layers with `display:none`, elements outside viewBox
3. **Simplify paths** — reduce decimal precision (`d="M 10.000 20.000"` to `d="M10 20"`)
4. **Merge paths** — combine shapes with same fill/stroke into single `<path>`
5. **Use `<use>` for repeated elements** — define once in `<defs>`, reference with `<use href="#id"/>`
6. **Remove unnecessary `<g>` wrappers** — flatten group transforms into child elements
7. **Convert shapes to paths** — when it produces shorter code (SVGO does this)
8. **Use CSS classes** instead of inline styles for repeated visual properties

### Before/After Example

```xml
<!-- BEFORE: 2.1 KB (exported from Figma) -->
<?xml version="1.0" encoding="UTF-8"?>
<svg width="24px" height="24px" viewBox="0 0 24 24" version="1.1"
  xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <!-- Generator: Figma -->
  <title>icon/check</title>
  <desc>Created with Figma.</desc>
  <g id="icon/check" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
    <g id="Group" transform="translate(2.000000, 4.000000)" stroke="#000000" stroke-width="2.00000">
      <polyline id="Path" points="0 8.00000 6.00000 14.0000 18.0000 2.00000"></polyline>
    </g>
  </g>
</svg>

<!-- AFTER: 138 bytes (optimized) -->
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M2 12l6 6L22 6" stroke="#000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

---

## Accessibility

SVGs need proper accessibility attributes, especially when they convey meaning.

### Decorative SVGs (Ignore by Screen Readers)

```tsx
// Purely decorative — hide from assistive technology
<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24">
  <path d="..." />
</svg>
```

### Meaningful SVGs (Icons with Purpose)

```tsx
// Icon that conveys information
<svg viewBox="0 0 24 24" role="img" aria-labelledby="icon-title">
  <title id="icon-title">Warning: unsaved changes</title>
  <path d="..." />
</svg>
```

### Complex SVGs (Charts, Infographics)

```tsx
// Chart or complex graphic
<svg viewBox="0 0 400 300" role="img" aria-labelledby="chart-title chart-desc">
  <title id="chart-title">Monthly Revenue</title>
  <desc id="chart-desc">
    Bar chart showing monthly revenue from January to June 2025.
    Revenue grew from $12K in January to $28K in June.
  </desc>
  {/* chart content */}
</svg>
```

### Full Accessibility Pattern for Icon Buttons

```tsx
// Icon-only button — needs accessible name
<button aria-label="Close dialog" className="icon-btn">
  <svg aria-hidden="true" viewBox="0 0 24 24" width={20} height={20}>
    <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round"/>
  </svg>
</button>
```

### Key Rules

| SVG Role | Required Attributes |
|----------|-------------------|
| Decorative (no meaning) | `aria-hidden="true"` |
| Informational icon | `role="img"` + `<title>` + `aria-labelledby` |
| Interactive (in a button) | `aria-hidden="true"` on SVG, `aria-label` on button |
| Complex (chart/diagram) | `role="img"` + `<title>` + `<desc>` + `aria-labelledby` |

---

