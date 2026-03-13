---
name: ref-based-canvas-animation
category: performance
version: 1.0.0
contributed: 2026-03-12
contributor: claude-mission-control
last_updated: 2026-03-12
contributors:
  - claude-mission-control
tags: [react, canvas, animation, requestAnimationFrame, performance, refs]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Ref-Based Canvas Animation — Avoiding State in rAF Loops

## Problem

Using `useState` + `setNodes()` inside a `requestAnimationFrame` loop triggers a full React re-render on every frame (~60fps = ~60 re-renders/second). For canvas-based visualizations (knowledge graphs, particle systems, physics simulations), this causes severe jank, dropped frames, and cascading re-renders in parent components.

**Symptoms:**
- React DevTools Profiler shows 300+ re-renders in 5 seconds from one component
- Canvas animation stutters or freezes
- Other UI elements (inputs, buttons) become unresponsive during animation
- `setNodes([...nodes])` called every animation frame

## Solution Pattern

Store simulation state in `useRef` instead of `useState`. The rAF loop reads and mutates refs directly, drawing to canvas via `CanvasRenderingContext2D`. React state is synced **once** when animation ends (or on a debounced timer), not every frame.

**Why this works:** Refs don't trigger re-renders. The canvas is an imperative API — you draw directly to it, bypassing React's virtual DOM entirely. React only needs to know the final state for event handlers and conditional rendering.

## Code Example

```typescript
// Before (300 re-renders in 5 seconds)
const [nodes, setNodes] = useState(initialNodes)
useEffect(() => {
  const loop = () => {
    simulatePhysics(nodes)
    setNodes([...nodes])  // RE-RENDER EVERY FRAME
    requestAnimationFrame(loop)
  }
  loop()
}, [nodes.length > 0])  // Also: boolean dependency never changes

// After (1 re-render at animation end)
const nodesRef = useRef(initialNodes)
const edgesRef = useRef(initialEdges)
const [nodes, setNodes] = useState(initialNodes)

const simulateStep = useCallback(() => {
  const ns = nodesRef.current
  // ... physics calculations mutate ns directly ...
}, [])

useEffect(() => {
  if (nodes.length === 0) return
  nodesRef.current = [...nodes]
  let running = true

  const loop = () => {
    if (!running) return
    simulateStep()
    drawCanvas(ctx, nodesRef.current, edgesRef.current)  // Direct canvas draw
    requestAnimationFrame(loop)
  }
  loop()

  const timeout = setTimeout(() => {
    running = false
    setNodes([...nodesRef.current])  // Sync once at end
  }, 5000)

  return () => { running = false; clearTimeout(timeout) }
}, [nodes.length])  // Number dependency, not boolean
```

## Implementation Steps

1. Create `useRef` mirrors for all animation state (nodes, edges, particles, etc.)
2. Extract canvas drawing into a standalone function: `drawCanvas(ctx, ...refs)`
3. Move physics/simulation logic to operate on refs, not state
4. In the rAF loop: mutate refs → draw canvas → repeat
5. Sync refs back to state once when animation completes or pauses
6. Fix dependency arrays: use `.length` (number), not `.length > 0` (boolean)

## When to Use

- Canvas-based visualizations (graphs, charts, particles, physics)
- Any `requestAnimationFrame` loop in React
- Drag-and-drop with real-time position updates
- Game loops or interactive simulations in React

## When NOT to Use

- DOM-based animations (use CSS transitions or Framer Motion instead)
- Simple animations where React's render cycle is fast enough (opacity, transforms)
- Components where other parts of the tree need frame-by-frame state updates

## Common Mistakes

- Forgetting to sync refs back to state — event handlers (click, hover) read stale state
- Using `[nodes.length > 0]` as dependency — boolean `true` never changes, so the effect only runs once even if nodes are replaced
- Not cleaning up `requestAnimationFrame` on unmount — causes "setState on unmounted component" warnings
- Directly mutating state arrays instead of refs — still triggers re-renders

## Related Skills

- use-visible-interval - Visibility-aware polling to reduce unnecessary work
- liveclock-extraction - Isolating high-frequency updates to leaf components

## References

- React docs: "You Might Not Need an Effect" (imperative APIs)
- Contributed from: claude-mission-control KnowledgeGraph visualization
