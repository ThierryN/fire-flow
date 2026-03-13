---
name: react-flow-animated-layout-switching
category: frontend
version: 1.0.0
contributed: 2026-02-26
contributor: scribe-bible
last_updated: 2026-02-26
tags: [react-flow, xyflow, animation, css-transitions, layout, graph-visualization]
difficulty: medium
usage_count: 0
success_rate: 100
---

# React Flow Animated Layout Switching

## Problem

React Flow (`@xyflow/react`) nodes snap instantly to new positions when switching between layout algorithms (e.g., dagre → force → radial). This creates a jarring user experience — nodes teleport instead of smoothly transitioning. Framer Motion cannot animate React Flow node positions because React Flow manages the `transform` CSS property internally via its own state.

## Solution Pattern

Use **scoped CSS transitions** on the `.react-flow__node` element's `transform` property. React Flow updates `transform: translate(x, y)` when node positions change — CSS transitions intercept this and animate the movement. Scope with a wrapper class to prevent affecting other React Flow instances in the same app.

The key insight: React Flow already changes the transform. You don't need a JavaScript animation library — just tell CSS to transition the property React Flow is already updating.

## Code Example

```css
/* Scoped to prevent affecting other React Flow instances */
.my-graph .react-flow__node {
  transition: transform 600ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Edge paths also animate when nodes move */
.my-graph .react-flow__edge path {
  transition: d 600ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

```tsx
// Wrap ReactFlow in a div with your scope class
<div className="my-graph">
  <ReactFlow
    nodes={nodes}
    edges={edges}
    fitView
    fitViewOptions={{ padding: 0.3, duration: 600 }} // Match CSS duration
  >
    <Controls />
  </ReactFlow>
</div>
```

```tsx
// When switching layouts, just update node positions — CSS handles animation
const switchLayout = (algorithm: string) => {
  const repositioned = applyLayout(nodes, edges, { algorithm });
  setNodes(repositioned); // React Flow updates transform → CSS transitions animate
};
```

## Implementation Steps

1. Add a wrapper `<div>` around `<ReactFlow>` with a unique class name
2. Add CSS transitions targeting `.wrapper-class .react-flow__node` for `transform`
3. Add CSS transitions targeting `.wrapper-class .react-flow__edge path` for `d` (SVG path data)
4. Match the `fitViewOptions.duration` to your CSS transition duration
5. Use `cubic-bezier(0.4, 0, 0.2, 1)` (standard ease-out) for natural deceleration

## When to Use

- Switching between layout algorithms (dagre, force, radial, custom)
- Expanding/collapsing groups of nodes
- Any scenario where React Flow node positions change programmatically
- When you need smooth transitions without adding Framer Motion or GSAP

## When NOT to Use

- User-initiated drag operations (CSS transitions would fight the drag)
- When you have multiple React Flow instances and only want one animated (use scoping)
- Performance-critical graphs with 500+ nodes (CSS transitions on many elements can jank)
- When nodes are being added/removed (use Framer Motion AnimatePresence for enter/exit)

## Common Mistakes

- Applying transitions globally (affects ALL React Flow instances in the app)
- Forgetting to scope with a wrapper class
- Using `all` instead of `transform` in the transition property (transitions zoom/pan too)
- Not matching fitView duration with CSS duration (viewport pans at different speed than nodes)
- Using `transition-duration` that's too long (>800ms feels sluggish for layout changes)

## Related Skills

- [framer-motion-layoutid-grouping](framer-motion-layoutid-grouping.md) — For non-graph animations
- [domain-specific-layout-algorithms](../_general/patterns-standards/domain-specific-layout-algorithms.md) — Custom layouts to switch between

## References

- React Flow docs: https://reactflow.dev
- Discovered in: scribe-bible parallelism visualization (Phase 1)
- The `d` attribute transition on SVG paths enables edge morphing during layout switches
