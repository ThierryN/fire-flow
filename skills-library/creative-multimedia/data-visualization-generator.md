# Data Visualization Generator
## Description

Generate accessible, responsive data visualizations for web applications. Covers chart type selection, React integration patterns for Chart.js / Recharts / D3.js, accessibility compliance, real-time updates, and export capabilities.

## When to Use

- Adding dashboards, analytics pages, or reporting features
- Choosing between Chart.js, Recharts, and D3.js for a project
- Building accessible charts that meet WCAG 2.1 AA
- Rendering real-time data streams as live charts
- Exporting visualizations to PNG/SVG for reports or PDFs

---

## Chart Type Selection Guide

| Data Pattern | Chart Type | Library | Complexity |
|-------------|-----------|---------|------------|
| Trend over time | Line chart | Chart.js / Recharts | Low |
| Comparison | Bar chart | Chart.js / Recharts | Low |
| Proportions | Pie / Donut | Chart.js / Recharts | Low |
| Distribution | Histogram | D3.js | Medium |
| Relationship | Scatter plot | Chart.js / D3.js | Low-Medium |
| Hierarchy | Treemap | D3.js | Medium |
| Geographic | Choropleth map | D3.js / Mapbox | High |
| Network | Force-directed graph | D3.js | High |
| Progress | Gauge / Radial | Chart.js (doughnut) | Low |
| Multi-dimensional | Radar chart | Chart.js / Recharts | Low |

### Quick Decision Flow

```
Need it fast with minimal code? --> Chart.js (react-chartjs-2)
Building a React dashboard with many charts? --> Recharts
Need full creative control or unusual chart types? --> D3.js
Need maps? --> D3.js + TopoJSON (static) or Mapbox GL (interactive)
```

### Library Comparison

| Feature | Chart.js | Recharts | D3.js |
|---------|----------|----------|-------|
| Learning curve | Low | Low | High |
| Bundle size | ~200KB | ~130KB | ~240KB (full) |
| Animation | Built-in | Built-in | Manual |
| Responsive | Built-in | Built-in | Manual |
| Accessibility | Partial | Partial | Manual |
| Customization | Medium | Medium | Total |
| React integration | via react-chartjs-2 | Native | useRef + useEffect |

---

## React Component Patterns

### Pattern 1: Chart.js with react-chartjs-2 (Easiest)

**Install:**

```bash
npm install chart.js react-chartjs-2
```

**Setup — register components once at app entry:**

```typescript
// src/lib/chartjs-setup.ts
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);
```

### Pattern 2: Recharts (React-Native, Declarative)

**Install:**

```bash
npm install recharts
```

Recharts uses composable React components — no registration step needed. Each chart is built from primitives like `<XAxis>`, `<YAxis>`, `<Tooltip>`, `<Line>`.

### Pattern 3: D3.js in React (useRef + useEffect)

**Install:**

```bash
npm install d3 @types/d3
```

**The correct pattern — D3 owns the DOM inside a ref:**

```tsx
import { useRef, useEffect } from "react";
import * as d3 from "d3";

interface D3ChartProps {
  data: number[];
  width: number;
  height: number;
}

function D3Chart({ data, width, height }: D3ChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous render

    // D3 drawing code here
    const xScale = d3.scaleBand()
      .domain(data.map((_, i) => String(i)))
      .range([0, width])
      .padding(0.2);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(data) || 0])
      .range([height, 0]);

    svg.selectAll("rect")
      .data(data)
      .join("rect")
      .attr("x", (_, i) => xScale(String(i)) || 0)
      .attr("y", (d) => yScale(d))
      .attr("width", xScale.bandwidth())
      .attr("height", (d) => height - yScale(d))
      .attr("fill", "#6366f1");
  }, [data, width, height]);

  return <svg ref={svgRef} width={width} height={height} role="img" aria-label="Bar chart" />;
}
```

> **Important:** Always call `svg.selectAll("*").remove()` at the start of the effect to prevent duplicate elements on re-render.

---

## Complete Examples

### Example 1: Enrollment Trend Line Chart (React + Chart.js)

```tsx
import { Line } from "react-chartjs-2";
import type { ChartOptions } from "chart.js";

interface EnrollmentData {
  month: string;
  enrollments: number;
  completions: number;
}

function EnrollmentTrendChart({ data }: { data: EnrollmentData[] }) {
  const chartData = {
    labels: data.map((d) => d.month),
    datasets: [
      {
        label: "Enrollments",
        data: data.map((d) => d.enrollments),
        borderColor: "#6366f1",
        backgroundColor: "rgba(99, 102, 241, 0.1)",
        fill: true,
        tension: 0.3,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
      {
        label: "Completions",
        data: data.map((d) => d.completions),
        borderColor: "#10b981",
        backgroundColor: "rgba(16, 185, 129, 0.1)",
        fill: true,
        tension: 0.3,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  };

  const options: ChartOptions<"line"> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: "top" },
      title: {
        display: true,
        text: "Monthly Enrollment & Completion Trends",
        font: { size: 16 },
      },
      tooltip: {
        mode: "index",
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: "Students" },
      },
      x: {
        title: { display: true, text: "Month" },
      },
    },
    interaction: {
      mode: "nearest",
      axis: "x",
      intersect: false,
    },
  };

  return (
    <div style={{ position: "relative", height: "400px", width: "100%" }}>
      <Line
        data={chartData}
        options={options}
        aria-label="Line chart showing monthly enrollment and completion trends"
        role="img"
      />
    </div>
  );
}
```

### Example 2: Revenue Bar Chart with Drill-Down (Recharts)

```tsx
import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface RevenueData {
  category: string;
  revenue: number;
  breakdown?: { name: string; revenue: number }[];
}

function RevenueDrillDownChart({ data }: { data: RevenueData[] }) {
  const [drillDown, setDrillDown] = useState<RevenueData | null>(null);

  const activeData = drillDown ? drillDown.breakdown || [] : data;
  const title = drillDown
    ? `Revenue Breakdown: ${drillDown.category}`
    : "Revenue by Category";

  const COLORS = ["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#ddd6fe", "#10b981", "#34d399"];

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "1rem" }}>
        <h3>{title}</h3>
        {drillDown && (
          <button onClick={() => setDrillDown(null)} aria-label="Go back to category view">
            Back
          </button>
        )}
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={activeData}
          onClick={(e) => {
            if (!drillDown && e?.activePayload) {
              const clicked = data.find((d) => d.category === e.activePayload![0].payload.category);
              if (clicked?.breakdown) setDrillDown(clicked);
            }
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey={drillDown ? "name" : "category"}
            tick={{ fontSize: 12 }}
          />
          <YAxis tickFormatter={(v) => formatCurrency(v)} />
          <Tooltip formatter={(value: number) => formatCurrency(value)} />
          <Legend />
          <Bar
            dataKey="revenue"
            name="Revenue"
            radius={[4, 4, 0, 0]}
            cursor={drillDown ? "default" : "pointer"}
          >
            {activeData.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Accessible data table */}
      <table className="sr-only" aria-label={title}>
        <thead>
          <tr>
            <th>Category</th>
            <th>Revenue</th>
          </tr>
        </thead>
        <tbody>
          {activeData.map((item: any) => (
            <tr key={item.category || item.name}>
              <td>{item.category || item.name}</td>
              <td>{formatCurrency(item.revenue)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### Example 3: Student Activity Heatmap (D3.js)

```tsx
import { useRef, useEffect } from "react";
import * as d3 from "d3";

interface ActivityCell {
  day: number; // 0-6 (Sun-Sat)
  hour: number; // 0-23
  count: number;
}

function ActivityHeatmap({ data, width = 800, height = 200 }: {
  data: ActivityCell[];
  width?: number;
  height?: number;
}) {
  const svgRef = useRef<SVGSVGElement>(null);
  const margin = { top: 30, right: 20, bottom: 40, left: 60 };

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    const hours = Array.from({ length: 24 }, (_, i) =>
      i === 0 ? "12a" : i < 12 ? `${i}a` : i === 12 ? "12p" : `${i - 12}p`
    );

    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const xScale = d3.scaleBand().domain(hours).range([0, innerWidth]).padding(0.05);
    const yScale = d3.scaleBand().domain(days).range([0, innerHeight]).padding(0.05);

    const maxCount = d3.max(data, (d) => d.count) || 1;
    const colorScale = d3.scaleSequential(d3.interpolateYlOrRd).domain([0, maxCount]);

    // Title
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", 16)
      .attr("text-anchor", "middle")
      .attr("font-size", "14px")
      .attr("font-weight", "bold")
      .text("Student Activity by Day and Hour");

    // Cells
    g.selectAll("rect")
      .data(data)
      .join("rect")
      .attr("x", (d) => xScale(hours[d.hour]) || 0)
      .attr("y", (d) => yScale(days[d.day]) || 0)
      .attr("width", xScale.bandwidth())
      .attr("height", yScale.bandwidth())
      .attr("rx", 2)
      .attr("fill", (d) => (d.count === 0 ? "#f3f4f6" : colorScale(d.count)))
      .attr("role", "img")
      .attr("aria-label", (d) => `${days[d.day]} ${hours[d.hour]}: ${d.count} activities`)
      .append("title")
      .text((d) => `${days[d.day]} ${hours[d.hour]}: ${d.count} activities`);

    // Axes
    g.append("g")
      .call(d3.axisBottom(xScale).tickSize(0))
      .attr("transform", `translate(0,${innerHeight})`)
      .select(".domain")
      .remove();

    g.append("g")
      .call(d3.axisLeft(yScale).tickSize(0))
      .select(".domain")
      .remove();
  }, [data, width, height]);

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      role="img"
      aria-label="Heatmap showing student activity levels by day of week and hour of day"
    />
  );
}
```

---

## Accessibility Requirements

### ARIA Labels on SVG Elements

Every chart must have a `role="img"` and descriptive `aria-label`:

```tsx
<svg role="img" aria-label="Bar chart showing monthly revenue from January to December 2025">
  <title>Monthly Revenue 2025</title>
  <desc>Bar chart with 12 bars. Revenue peaked at $45,000 in March.</desc>
  {/* chart content */}
</svg>
```

For Canvas-based charts (Chart.js), add ARIA to the canvas wrapper:

```tsx
<div role="img" aria-label="Line chart showing enrollment trends increasing 23% over 6 months">
  <canvas id="enrollment-chart" />
</div>
```

### Auto-Generated Alt Text

Generate descriptive alt text from the data:

```typescript
function generateChartAltText(
  chartType: string,
  title: string,
  data: { label: string; value: number }[]
): string {
  const sorted = [...data].sort((a, b) => b.value - a.value);
  const max = sorted[0];
  const min = sorted[sorted.length - 1];
  const total = data.reduce((sum, d) => sum + d.value, 0);
  const avg = Math.round(total / data.length);

  return (
    `${chartType} titled "${title}" with ${data.length} data points. ` +
    `Highest: ${max.label} at ${max.value}. ` +
    `Lowest: ${min.label} at ${min.value}. ` +
    `Average: ${avg}.`
  );
}

// Usage:
// "Bar chart titled "Revenue by Department" with 5 data points.
//  Highest: Engineering at 120000. Lowest: HR at 35000. Average: 72000."
```

### Keyboard Navigation for Interactive Charts

```tsx
function AccessibleBarChart({ data }: { data: { label: string; value: number }[] }) {
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case "ArrowRight":
        e.preventDefault();
        setFocusedIndex((prev) => Math.min(prev + 1, data.length - 1));
        break;
      case "ArrowLeft":
        e.preventDefault();
        setFocusedIndex((prev) => Math.max(prev - 1, 0));
        break;
      case "Home":
        e.preventDefault();
        setFocusedIndex(0);
        break;
      case "End":
        e.preventDefault();
        setFocusedIndex(data.length - 1);
        break;
    }
  };

  return (
    <div
      role="img"
      aria-label="Interactive bar chart. Use arrow keys to navigate between bars."
      tabIndex={0}
      onKeyDown={handleKeyDown}
    >
      {/* Chart rendering */}
      {focusedIndex >= 0 && (
        <div role="status" aria-live="polite" className="sr-only">
          {data[focusedIndex].label}: {data[focusedIndex].value}
        </div>
      )}
    </div>
  );
}
```

### Color-Blind Safe Palettes

**8-color palette (safe for all common types of color blindness):**

```typescript
const COLOR_BLIND_SAFE = {
  // Paul Tol's qualitative palette
  qualitative: [
    "#332288", // indigo
    "#88CCEE", // cyan
    "#44AA99", // teal
    "#117733", // green
    "#999933", // olive
    "#DDCC77", // sand
    "#CC6677", // rose
    "#AA4499", // purple
  ],

  // Sequential (single hue, light to dark)
  sequential: ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#084594"],

  // Diverging (two hues from a neutral center)
  diverging: ["#d73027", "#f46d43", "#fdae61", "#fee090", "#e0f3f8", "#abd9e9", "#74add1", "#4575b4"],
};

// Usage with Chart.js:
const chartData = {
  datasets: [{
    backgroundColor: COLOR_BLIND_SAFE.qualitative.slice(0, data.length),
  }],
};

// Usage with Recharts:
data.map((entry, index) => (
  <Cell key={index} fill={COLOR_BLIND_SAFE.qualitative[index % 8]} />
));
```

> **Rule of thumb:** Never rely solely on color to convey meaning. Use patterns (stripes, dots), labels, or shapes alongside color.

---

## Responsive Patterns

### Container Queries (Modern CSS)

```css
.chart-wrapper {
  container-type: inline-size;
  container-name: chart;
}

@container chart (max-width: 500px) {
  .chart-legend {
    display: none; /* Hide legend on small containers, show as tooltip instead */
  }
  .chart-title {
    font-size: 0.875rem;
  }
}
```

### Aspect Ratio Preservation

```tsx
// Chart.js — built-in
const options = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 16 / 9, // or 2 for wider, 1 for square
};

// Recharts — use ResponsiveContainer
<ResponsiveContainer width="100%" aspect={16 / 9}>
  <LineChart data={data}>{/* ... */}</LineChart>
</ResponsiveContainer>

// D3.js — use viewBox for automatic scaling
<svg
  viewBox={`0 0 ${width} ${height}`}
  preserveAspectRatio="xMidYMid meet"
  style={{ width: "100%", height: "auto" }}
/>
```

### Hook for Responsive Dimensions

```typescript
import { useState, useEffect, useRef } from "react";

function useContainerDimensions() {
  const ref = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    if (!ref.current) return;

    const observer = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setDimensions({ width: Math.floor(width), height: Math.floor(height) });
    });

    observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return { ref, ...dimensions };
}

// Usage:
function Chart() {
  const { ref, width, height } = useContainerDimensions();
  return (
    <div ref={ref} style={{ width: "100%", height: "400px" }}>
      {width > 0 && <D3Chart width={width} height={height} data={data} />}
    </div>
  );
}
```

---

## Real-Time Updates

### WebSocket Data to Chart Animation

```tsx
import { useState, useEffect, useCallback } from "react";
import { Line } from "react-chartjs-2";

const MAX_POINTS = 60; // Keep last 60 data points

function RealtimeChart({ wsUrl }: { wsUrl: string }) {
  const [dataPoints, setDataPoints] = useState<{ time: string; value: number }[]>([]);

  useEffect(() => {
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const newPoint = JSON.parse(event.data);
      setDataPoints((prev) => {
        const updated = [...prev, newPoint];
        return updated.length > MAX_POINTS ? updated.slice(-MAX_POINTS) : updated;
      });
    };

    return () => ws.close();
  }, [wsUrl]);

  const chartData = {
    labels: dataPoints.map((d) => d.time),
    datasets: [
      {
        label: "Live Data",
        data: dataPoints.map((d) => d.value),
        borderColor: "#6366f1",
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.3,
        fill: false,
      },
    ],
  };

  const options = {
    responsive: true,
    animation: { duration: 300 },
    scales: {
      x: { display: false }, // Hide x-axis labels for streaming data
      y: { beginAtZero: false },
    },
    plugins: {
      legend: { display: false },
    },
  };

  return (
    <div style={{ position: "relative", height: "300px" }}>
      <Line data={chartData} options={options} />
    </div>
  );
}
```

### Throttled Updates for High-Frequency Data

```typescript
import { useRef, useCallback } from "react";

function useThrottledUpdate<T>(callback: (data: T) => void, intervalMs: number) {
  const buffer = useRef<T | null>(null);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  const start = useCallback(() => {
    if (timer.current) return;
    timer.current = setInterval(() => {
      if (buffer.current !== null) {
        callback(buffer.current);
        buffer.current = null;
      }
    }, intervalMs);
  }, [callback, intervalMs]);

  const push = useCallback((data: T) => {
    buffer.current = data;
    start();
  }, [start]);

  const stop = useCallback(() => {
    if (timer.current) {
      clearInterval(timer.current);
      timer.current = null;
    }
  }, []);

  return { push, stop };
}
```

---

## Export Charts

### Chart to PNG (Canvas-based — Chart.js)

```typescript
function exportChartAsPNG(chartRef: React.RefObject<any>, filename: string = "chart.png") {
  const canvas = chartRef.current?.canvas;
  if (!canvas) return;

  const link = document.createElement("a");
  link.download = filename;
  link.href = canvas.toDataURL("image/png", 1.0);
  link.click();
}

// Usage:
const chartRef = useRef(null);
<Line ref={chartRef} data={data} options={options} />
<button onClick={() => exportChartAsPNG(chartRef, "enrollment-trends.png")}>
  Export PNG
</button>
```

### Chart to SVG (D3.js / Recharts)

```typescript
function exportSVG(svgElement: SVGSVGElement, filename: string = "chart.svg") {
  const serializer = new XMLSerializer();
  const svgString = serializer.serializeToString(svgElement);

  // Add XML declaration and styling
  const fullSvg = `<?xml version="1.0" encoding="UTF-8"?>\n${svgString}`;

  const blob = new Blob([fullSvg], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.download = filename;
  link.href = url;
  link.click();

  URL.revokeObjectURL(url);
}

// Convert SVG to PNG (for when you need raster from SVG charts)
function svgToPNG(svgElement: SVGSVGElement, scale: number = 2): Promise<Blob> {
  return new Promise((resolve) => {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d")!;
    const svgData = new XMLSerializer().serializeToString(svgElement);
    const img = new Image();

    canvas.width = svgElement.clientWidth * scale;
    canvas.height = svgElement.clientHeight * scale;
    ctx.scale(scale, scale);

    img.onload = () => {
      ctx.drawImage(img, 0, 0);
      canvas.toBlob((blob) => resolve(blob!), "image/png");
    };

    img.src = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svgData)));
  });
}
```

### Server-Side Export (Node.js — for PDF reports)

```typescript
// Use @napi-rs/canvas for server-side Chart.js rendering
import { createCanvas } from "@napi-rs/canvas";
import { Chart } from "chart.js/auto";

async function renderChartToBuffer(config: any, width = 800, height = 400): Promise<Buffer> {
  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext("2d");

  new Chart(ctx as any, config);

  return canvas.toBuffer("image/png");
}

// Write to file or embed in PDF
const buffer = await renderChartToBuffer({
  type: "bar",
  data: { labels: ["Q1", "Q2", "Q3", "Q4"], datasets: [{ data: [10, 20, 30, 40] }] },
});
fs.writeFileSync("chart.png", buffer);
```

---

## Common Pitfalls

1. **Re-registering Chart.js components** — Call `ChartJS.register()` once at app entry, not inside components. Duplicate registration causes memory leaks.
2. **D3 + React state conflicts** — D3 manages its own DOM. Never let React and D3 fight over the same elements. Use a `ref` and let D3 own everything inside it.
3. **Massive datasets crashing the browser** — For 10,000+ points, downsample before rendering. Chart.js has a `decimation` plugin. D3 can use `d3.bisect` for viewport-based rendering.
4. **Missing `<ResponsiveContainer>`** — Recharts charts have zero size without it. Always wrap in `<ResponsiveContainer width="100%" height={400}>`.
5. **Canvas resolution on Retina displays** — Chart.js handles `devicePixelRatio` automatically. For D3/Canvas, manually set `canvas.width = displayWidth * dpr`.
6. **Forgetting accessible fallbacks** — Always include a hidden `<table>` or `aria-label` with the same data for screen readers.

---

