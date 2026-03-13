---
name: color-token-migration
category: frontend
version: 1.0.0
contributed: 2026-03-12
contributor: claude-mission-control
last_updated: 2026-03-12
contributors:
  - claude-mission-control
tags: [css, tailwind, design-system, reskin, color-tokens, theming]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Color Token Migration — Systematic App-Wide Color System Swap

## Problem

Rebranding or reskinning an app requires changing the entire color palette consistently across all components. Direct find-and-replace of hex values is error-prone (same hex used for different purposes), and missing a single reference creates visual inconsistencies.

**Symptoms:**
- Scattered hardcoded hex values across components
- Some components still show old brand colors after "reskin"
- Hover/active states don't match the new palette
- Glass/blur effects clash with new color scheme

## Solution Pattern

Use **CSS custom properties (tokens)** mapped through Tailwind's config, then change colors in ONE place (the token definitions). For existing apps without tokens, migrate in this order:

1. **Audit:** Extract all unique color values used
2. **Define tokens:** Create semantic token names (`mc-bg`, `mc-accent`, `mc-success`)
3. **Replace:** Swap hardcoded values for token references
4. **Verify:** Visual diff every component

## Code Example

```css
/* tailwind.config — token definitions (change here = change everywhere) */
:root {
  /* Old (indigo) */
  /* --mc-bg: #09090b; --mc-accent: #6366f1; --mc-success: #22c55e; */

  /* New (purple) */
  --mc-bg: #0a0a0f;
  --mc-card: #12121a;
  --mc-accent: #8b5cf6;
  --mc-success: #10b981;
  --mc-text: #e4e4ef;
  --mc-muted: #8888a0;
  --mc-border: #2a2a3e;
  --mc-surface2: #1a1a2e;
}
```

```typescript
// Components use tokens, not hardcoded colors
<div className="bg-mc-card border-mc-border text-mc-text">
  <button className="bg-mc-accent hover:bg-mc-accent/80">
    Action
  </button>
</div>
```

## Migration Checklist

| Token | Purpose | Old | New |
|-------|---------|-----|-----|
| mc-bg | Page background | #09090b | #0a0a0f |
| mc-card | Card/panel background | #18181b | #12121a |
| mc-accent | Primary brand color | #6366f1 | #8b5cf6 |
| mc-success | Success indicators | #22c55e | #10b981 |
| mc-text | Primary text | #fafafa | #e4e4ef |
| mc-muted | Secondary text | #a1a1aa | #8888a0 |
| mc-border | Borders/dividers | #27272a | #2a2a3e |
| mc-surface2 | Elevated surfaces | (new) | #1a1a2e |

## Implementation Steps

1. Grep all unique hex/RGB values: `grep -roh '#[0-9a-fA-F]\{6\}' src/ | sort -u`
2. Map each to a semantic purpose (background, text, accent, etc.)
3. Define tokens in CSS custom properties + Tailwind extend
4. Replace hardcoded values with token classes (component by component)
5. Also update: glass/blur effects, box-shadows, gradients, inline styles
6. Remove old glass/blur effects if new design is flat

## When to Use

- App rebranding or reskinning
- Dark/light mode implementation
- White-labeling (customer-specific themes)
- Design system migration (Material → custom)

## When NOT to Use

- Single component color changes (just change the one value)
- Prototype/MVP stage (premature abstraction)
- Static sites with no theming needs

## Common Mistakes

- Missing inline `style={{}}` attributes — grep doesn't catch them in JSX
- Forgetting opacity variants (`bg-mc-accent/10`, `border-mc-border/30`)
- Not updating gradient definitions (`linear-gradient(135deg, ...)`)
- Leaving old glow/shadow effects that reference old colors
- SVG `fill` and `stroke` attributes embedded in component JSX

## References

- Tailwind CSS: "Customizing Colors" — extending with CSS custom properties
- Contributed from: claude-mission-control (indigo → purple reskin, ~50 files)
