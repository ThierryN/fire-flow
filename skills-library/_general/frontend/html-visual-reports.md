---
name: html-visual-reports
category: frontend
version: 1.0.0
contributed: 2026-03-06
contributor: dominion-flow
last_updated: 2026-03-06
contributors:
  - dominion-flow
tags: [html, css, visualization, reports, dashboards, data-tables, diagrams, self-contained]
difficulty: medium
usage_count: 0
success_rate: 100
---

# HTML Visual Reports & Dashboards

## Problem

When presenting data to stakeholders — competitive analyses, audit results, feature matrices, architecture overviews — plain text tables in the terminal are hard to read and impossible to share. Screenshots of terminal output look unprofessional. External tools (Google Slides, Figma) require context-switching and manual data entry.

Symptoms:
- ASCII box-drawing tables with 10+ rows are unreadable
- Stakeholders ask "can you put that in a slide?"
- Architecture diagrams drawn with text characters lack clarity
- Data comparisons lose impact without color-coded status indicators
- No way to share Claude's analysis output as a professional artifact

## Solution Pattern

Generate **self-contained HTML files** that open directly in any browser. No build step, no dependencies, no server — just a single `.html` file with inline CSS, Google Fonts via CDN, and optional JavaScript for interactivity. The file IS the deliverable.

### Core Architecture

Every report follows this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Descriptive Title</title>
  <link href="https://fonts.googleapis.com/css2?family=...&display=swap" rel="stylesheet">
  <style>
    /* CSS custom properties for theming */
    /* Full layout, components, animations — all inline */
  </style>
</head>
<body>
  <!-- Semantic HTML: sections, headings, tables, inline SVG -->
  <!-- Optional: <script> for Mermaid, scroll spy, or Chart.js -->
</body>
</html>
```

### Design System (CSS Custom Properties)

Every report defines a complete palette via CSS variables. This enables dark/light theme support and consistent styling:

```css
:root {
  --bg: #0a0e17;
  --surface: #111827;
  --surface2: #1a2236;
  --border: rgba(255, 255, 255, 0.06);
  --text: #e2e8f0;
  --text-dim: #64748b;
  --cyan: #22d3ee;
  --cyan-dim: rgba(34, 211, 238, 0.10);
  --green: #4ade80;
  --green-dim: rgba(74, 222, 128, 0.10);
  --red: #f87171;
  --red-dim: rgba(248, 113, 113, 0.10);
  --amber: #fbbf24;
  --amber-dim: rgba(251, 191, 36, 0.10);
}

@media (prefers-color-scheme: light) {
  :root {
    --bg: #f0f4f8;
    --surface: #ffffff;
    /* ... light overrides ... */
  }
}
```

### Aesthetic Variations

Rotate aesthetics to avoid cookie-cutter output:

| Aesthetic | When to Use | Font Pairing |
|-----------|-------------|--------------|
| Neon Dashboard | Competitive analysis, metrics, KPIs | Orbitron + JetBrains Mono |
| Editorial | Executive summaries, proposals | Instrument Serif + JetBrains Mono |
| Blueprint | Architecture diagrams, technical specs | Space Mono + system-ui |
| Paper/Ink | Documentation, guides | Literata + Fira Code |
| IDE-inspired | Code reviews, debug reports | Use Dracula/Nord/Catppuccin palette |

### Key Components

**KPI Cards** — Large hero numbers with labels, color-coded by meaning:
```html
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-card__value" style="color:var(--cyan)">42</div>
    <div class="kpi-card__label">Commands</div>
  </div>
</div>
```

**Data Tables** — Real `<table>` elements with sticky headers, alternating rows, status badges:
```html
<div class="table-wrap">
  <div class="table-scroll">
    <table class="data-table">
      <thead><tr><th>Feature</th><th>Status</th></tr></thead>
      <tbody>
        <tr><td>Auth</td><td><span class="status status--yes">YES</span></td></tr>
        <tr><td>Caching</td><td><span class="status status--no">NO</span></td></tr>
      </tbody>
    </table>
  </div>
</div>
```

**Status Badges** — Never use emoji. Use styled `<span>` elements:
```css
.status--yes { background: var(--green-dim); color: var(--green); }
.status--no { background: var(--red-dim); color: var(--red); }
.status--partial { background: var(--amber-dim); color: var(--amber); }
```

**Grade Badges** — Letter grades with color-coded borders:
```css
.grade--a { background: var(--green-dim); color: var(--green); border: 1px solid var(--green); }
.grade--f { background: var(--red-dim); color: var(--red); border: 1px solid var(--red); }
```

**Section Navigation** — For pages with 4+ sections, add a sticky sidebar TOC on desktop that collapses to a horizontal scrollable bar on mobile. Use IntersectionObserver for scroll-spy highlighting.

**Staggered Animations** — Use CSS `--i` variable per element for load stagger:
```css
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate {
  animation: fadeUp 0.4s ease-out both;
  animation-delay: calc(var(--i, 0) * 0.05s);
}
```

### Diagram Types and Rendering

| Diagram Type | Approach |
|---|---|
| Architecture (text-heavy cards) | CSS Grid + flow arrows |
| Flowcharts, sequence diagrams | Mermaid.js via CDN |
| Data tables, comparisons | HTML `<table>` element |
| ER / schema diagrams | Mermaid erDiagram |
| Dashboards with charts | CSS Grid + Chart.js via CDN |
| Timelines | CSS central line + alternating cards |

### Mermaid Integration

For flowcharts, sequence diagrams, and ER diagrams, use Mermaid.js with custom theming:

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({
  theme: 'base',
  themeVariables: {
    primaryColor: '#1e293b',
    primaryTextColor: '#e2e8f0',
    lineColor: '#22d3ee'
  }
});
</script>
```

Always add zoom controls (+/-/reset buttons) to Mermaid containers.

## Code Example

```html
<!-- Before: ASCII table in terminal -->
<!--
| Feature    | Us  | Them |
|------------|-----|------|
| Auth       | YES | NO   |
| Memory     | YES | YES  |
| Parallel   | YES | NO   |
Unreadable at scale, can't share, no visual hierarchy
-->

<!-- After: Self-contained HTML report -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Feature Comparison</title>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0a0e17; --surface: #111827; --text: #e2e8f0;
      --text-dim: #64748b; --border: rgba(255,255,255,0.06);
      --cyan: #22d3ee; --cyan-dim: rgba(34,211,238,0.10);
      --green: #4ade80; --green-dim: rgba(74,222,128,0.10);
      --red: #f87171; --red-dim: rgba(248,113,113,0.10);
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: var(--bg); color: var(--text); font-family: system-ui; padding: 40px; }
    h1 { font-family: 'Orbitron'; color: var(--cyan); font-size: 24px; margin-bottom: 24px; }
    .table-wrap { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
    .data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .data-table th { background: #1a2236; font-family: 'JetBrains Mono'; font-size: 10px; text-transform: uppercase; letter-spacing: 1.2px; color: var(--text-dim); padding: 14px; text-align: left; }
    .data-table td { padding: 12px 14px; border-bottom: 1px solid var(--border); }
    .data-table tbody tr:hover { background: var(--cyan-dim); }
    .status { font-family: 'JetBrains Mono'; font-size: 10px; font-weight: 600; padding: 3px 10px; border-radius: 6px; }
    .status--yes { background: var(--green-dim); color: var(--green); }
    .status--no { background: var(--red-dim); color: var(--red); }
  </style>
</head>
<body>
  <h1>Feature Comparison</h1>
  <div class="table-wrap">
    <table class="data-table">
      <thead><tr><th>Feature</th><th>Us</th><th>Competitor</th></tr></thead>
      <tbody>
        <tr><td><strong>Auth</strong></td><td><span class="status status--yes">YES</span></td><td><span class="status status--no">NO</span></td></tr>
        <tr><td><strong>Memory</strong></td><td><span class="status status--yes">YES</span></td><td><span class="status status--yes">YES</span></td></tr>
        <tr><td><strong>Parallel</strong></td><td><span class="status status--yes">YES</span></td><td><span class="status status--no">NO</span></td></tr>
      </tbody>
    </table>
  </div>
</body>
</html>
```

## Implementation Steps

1. Choose an aesthetic that fits the audience and content type
2. Pick a distinctive Google Fonts pairing (never use Inter/Roboto/Arial)
3. Define the full CSS variable palette with both dark and light themes
4. Structure content with semantic HTML (sections, headings, tables)
5. Add KPI cards above tables for visual hook
6. Use status badges (never emoji) for match/gap/partial indicators
7. Add staggered fadeUp animations with `--i` variable
8. Add section navigation if 4+ sections
9. Add `@media (prefers-reduced-motion: reduce)` for accessibility
10. Write to `~/.agent/diagrams/` and open in browser
11. Always respect `overflow-wrap: break-word` and `min-width: 0` on flex/grid children

## When to Use

- Competitive analysis or feature comparisons (4+ rows, 3+ columns)
- Architecture or system diagrams
- Audit results or requirement reviews
- Project dashboards with KPI metrics
- Any data you'd present as an ASCII table — generate HTML instead
- When sharing analysis output with stakeholders who don't use the terminal

## When NOT to Use

- Quick 2-3 line comparisons that fit naturally in chat
- Internal debugging output that doesn't need to be shared
- When the user explicitly asks for plain text output
- Real-time dashboards that need live data (use a proper framework)

## Common Mistakes

- Using flat solid backgrounds (add subtle radial gradients for atmosphere)
- Same animation on everything (use fadeUp for cards, fadeScale for KPIs)
- Forgetting `overflow-x: auto` wrapper on wide tables
- Using `display: flex` on `<li>` for markers (causes overflow — use absolute positioning)
- Not testing both light and dark themes via `prefers-color-scheme`
- Using emoji for status indicators instead of styled `<span>` elements
- Forgetting `min-width: 0` on CSS Grid/Flex children (causes container overflow)

## Related Skills

- [plugin-doc-auto-generation](../plugin-development/plugin-doc-auto-generation.md) — Auto-generate plugin docs from filesystem
- [complexity-divider](../complexity-metrics/complexity-divider.md) — Complexity analysis patterns

## References

- Contributed from: dominion-flow competitive analysis session (2026-03-06)
- Pattern refined across 20+ generated diagrams and dashboards
- Aesthetic catalog: Neon, Editorial, Blueprint, Paper/Ink, IDE-inspired, Hand-drawn
