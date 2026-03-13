# Nested CSS backdrop-filter Artifact Fix

## Problem

A white blurry line or haze overlay appears on UI elements when using glassmorphism / frosted glass CSS effects. The artifact is most visible in dark mode and appears as a semi-transparent white strip or blur effect layered on top of content.

## Root Cause

**Nested `backdrop-filter: blur()` declarations** on parent and child elements create compounding blur artifacts. Each `backdrop-filter` creates a new stacking context and compositing layer. When two blur layers overlap, the browser renders an extra semi-transparent white haze at the boundary.

### Example of the Problem

```css
/* Parent element */
.panel-container {
  background-color: rgba(17, 24, 39, 0.85);
  -webkit-backdrop-filter: blur(20px);
  backdrop-filter: blur(20px);
}

/* Child element — REDUNDANT blur causes artifact */
[data-theme='dark'] .bible-viewer {
  background-color: rgba(17, 24, 39, 0.5);  /* Semi-transparent */
  -webkit-backdrop-filter: blur(20px);
  backdrop-filter: blur(20px);
}
```

The child's blur composites on top of the parent's blur, creating a visible white line at the boundary.

## Solution

Remove `backdrop-filter` from the **inner/child** element and use an opaque or semi-opaque background instead:

```css
/* Parent keeps the glass effect */
.panel-container {
  background-color: rgba(17, 24, 39, 0.85);
  -webkit-backdrop-filter: blur(20px);
  backdrop-filter: blur(20px);
}

/* Child uses opaque background — NO blur */
[data-theme='dark'] .bible-viewer {
  background-color: var(--bg-secondary);  /* Opaque, no blur */
}
```

### Rule of Thumb

**Only ONE element in any ancestor chain should have `backdrop-filter`.** If the parent already blurs, children should use:
- Opaque backgrounds (`var(--bg-secondary)`)
- Semi-transparent backgrounds without blur (`rgba(...)` alone)
- `background: inherit` to match the parent

## Debugging Tips

1. **Inspect with DevTools** — Toggle `backdrop-filter` off on each element to find which one is redundant
2. **Check dark mode specifically** — Artifacts are most visible when backgrounds are semi-transparent dark colors
3. **Search for all blur declarations**: `grep -r "backdrop-filter" src/` to find all instances
4. **Test across browsers** — Chrome, Firefox, and Safari handle compositing differently

## When This Happens

- Glassmorphism / frosted glass UI designs
- Dark mode implementations with semi-transparent panels
- Nested panel layouts (sidebar → content → sub-panel)
- CSS frameworks that apply blur at multiple levels

## Tech Stack
- CSS (any framework)
- Tailwind CSS (when using `backdrop-blur-*` utilities)
- Dark mode / theme switching

## Tags
`css` `backdrop-filter` `blur` `glassmorphism` `dark-mode` `visual-artifact` `stacking-context`
