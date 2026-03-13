---
name: cascading-failure-diagnosis
category: patterns-standards
version: 1.0.0
contributed: 2026-03-12
contributor: claude-mission-control
last_updated: 2026-03-12
contributors:
  - claude-mission-control
tags: [debugging, react, performance, cascading, diagnosis, layered]
difficulty: hard
usage_count: 0
success_rate: 100
---

# Cascading Failure Diagnosis

## Problem

A UI appears "glitchy" or "broken" with no single clear error. The symptoms are vague — clicks don't respond, the app freezes briefly, components flash or re-render excessively. Traditional debugging (find error → fix) fails because there is no single root cause. Instead, **multiple independent bugs stack** to create a compound failure that looks like one problem but is actually 3-5 layered issues.

**Symptoms:**
- App feels "slow" or "clicky" with no specific error
- Fixing one thing doesn't resolve the overall problem
- Console shows mixed signals (some errors, some warnings, some clean)
- Performance profiler shows multiple hot paths, not one bottleneck

## Solution Pattern

**Layer-by-layer peeling** — instead of looking for THE bug, systematically isolate and fix bugs starting from the lowest layer (infrastructure/connection) upward to the highest (UI/rendering). Each fix reveals the next layer's bug that was previously masked.

### The Diagnostic Stack (bottom to top)

```
Layer 4: UI/Rendering    ← re-render storms, wrong data display
Layer 3: Data Shape      ← API response != client expectation
Layer 2: React Lifecycle ← hooks ordering, effect dependencies
Layer 1: Connection      ← exhausted pools, slow endpoints, timeouts
```

**Always diagnose bottom-up.** A connection issue (Layer 1) can cause timeouts that trigger re-renders (Layer 4), making it look like a UI bug. Fixing Layer 4 first wastes time because the root is at Layer 1.

## Code Example

```javascript
// Real-world example: C3 Dashboard had 4 stacked bugs

// Layer 1: Connection exhaustion
// BEFORE: Health endpoint did heavy I/O, slow responses exhausted Vite proxy pool
app.get('/api/system/health', async (req, res) => {
  const data = await heavyHealthCheck(); // 2-5 second response
  res.json(data);
});
// AFTER: Add zero-I/O ping endpoint for connection checks
app.get('/api/ping', (req, res) => res.json({ ok: true }));

// Layer 2: React hooks crash
// BEFORE: useMemo placed after early return = hook count mismatch
function App() {
  const [loading, setLoading] = useState(true);
  if (loading) return <Loading />;          // early return BEFORE hooks
  const panels = useMemo(() => build(), []); // hook after conditional = crash
}
// AFTER: All hooks before any conditional returns
function App() {
  const [loading, setLoading] = useState(true);
  const panels = useMemo(() => build(), []); // hooks FIRST
  if (loading) return <Loading />;           // conditionals AFTER

// Layer 3: Data shape mismatch
// BEFORE: Server returned array, client expected { loops: [...] }
const data = await fetch('/api/loops').then(r => r.json());
const loops = data.loops; // undefined — server sent raw array
// AFTER: Handle both shapes or fix server response

// Layer 4: Re-render storm
// BEFORE: 25 panel renderers recreated every render
const sections = panels.map(p => ({ render: () => <Panel {...p} /> }));
// AFTER: Memoize panel renderers
const sections = useMemo(() =>
  panels.map(p => ({ render: () => <Panel {...p} /> })), [panels]);
```

## Implementation Steps

1. **Start at Layer 1 (Connection):** Check network tab — are requests timing out, queuing, or returning errors? Fix connection/endpoint issues first.
2. **Move to Layer 2 (Lifecycle):** Check console for React warnings about hooks, effects, or unmounted components. Fix hook ordering and dependency arrays.
3. **Check Layer 3 (Data):** Log API responses — does the shape match what components expect? Fix response parsing.
4. **Finish at Layer 4 (Rendering):** Use React DevTools Profiler — are components re-rendering unnecessarily? Add memoization.
5. **After each layer fix, re-test** — the next layer's symptoms will now be clearer.

## When to Use

- App has vague "it's broken" symptoms with no clear single error
- Fixing one bug doesn't resolve the overall issue
- Performance profiler shows multiple hot paths
- The problem appeared suddenly after multiple changes

## When NOT to Use

- There's a clear, single error message — fix that directly
- The issue is purely visual (CSS/layout) — no cascading involved
- The app crashes with a stack trace pointing to one location

## Common Mistakes

- **Starting at the wrong layer** — fixing UI re-renders when the real issue is connection exhaustion
- **Declaring victory after fixing one layer** — always test all layers after each fix
- **Assuming a single root cause** — cascading failures by definition have multiple independent causes
- **Using console.log debugging only** — use Network tab (Layer 1), React DevTools (Layer 2-4), and Profiler (Layer 4)

## Related Skills

- [react-hooks-order-debugging](../_general/frontend/react-hooks-order-debugging.md) — Layer 2 specific fix
- [ref-based-canvas-animation](../_general/performance/ref-based-canvas-animation.md) — Layer 4 performance pattern

## References

- Contributed from: claude-mission-control C3 Dashboard (4 stacked bugs fixed in one session, 2026-03-12)
