---
name: react-hooks-order-debugging
category: frontend
version: 1.0.0
contributed: 2026-03-12
contributor: claude-mission-control
last_updated: 2026-03-12
contributors:
  - claude-mission-control
tags: [react, hooks, debugging, HMR, vite, black-screen]
difficulty: hard
usage_count: 0
success_rate: 100
---

# React Hooks Order Debugging — Diagnosing & Fixing Hooks Crashes

## Problem

React requires hooks to be called in the exact same order on every render. Violations cause the error: `"Rendered more hooks than during the previous render"` or `"Rendered fewer hooks..."`. This often manifests as a complete **black screen** with no visible UI, especially when:

1. A new hook is added at an existing position (e.g., `useMemo` inserted between existing hooks)
2. A hook type changes at an existing position (e.g., replacing `useState` with a Zustand `useStore`)
3. Vite HMR module cache serves stale code after hook changes

**Symptoms:**
- App loads briefly, then goes completely black
- Console shows "change in the order of Hooks called by [Component]"
- Error stack trace lists hook positions: "Previous render: useState (3), Current render: useSyncExternalStore (3)"
- Hard refresh (Ctrl+Shift+R) doesn't fix it
- Only a full Vite cache clear + server restart fixes it

## Solution Pattern

**Diagnosis:** The error message tells you exactly which hook position changed. Map the position numbers to your component's hook calls (count them top-to-bottom: 1st `useState`, 2nd `useState`, 3rd `useEffect`, etc.).

**Three root causes and their fixes:**

### Cause 1: New hook inserted mid-component
Adding `useMemo`, `useCallback`, or any hook between existing hooks shifts all subsequent hook positions.

**Fix:** Add new hooks at the END of the hook section, or restructure to avoid the hook entirely.

### Cause 2: Hook type changed at same position
Replacing `useState` with `useStore()` (Zustand's `useSyncExternalStore`) changes the hook type at that position. React treats different hook types at the same position as a violation.

**Fix:** Keep the original hooks, sync external store data into them via `useEffect`, or wrap the store in a child component.

### Cause 3: Vite HMR cache serving stale modules
After fixing hook issues, Vite's module cache (`.vite/` directory + browser cache) may still serve the old broken version.

**Fix:** Full cache clear: `rm -rf node_modules/.vite && kill vite && restart`

## Code Example

```typescript
// BROKEN: useMemo inserted at position 43 (shifts all hooks after it)
function App() {
  const [a, setA] = useState(false)     // position 1
  const [b, setB] = useState('home')    // position 2
  // ... 40 more hooks from useEffect, useState, etc.
  const memoized = useMemo(() => {...}, []) // position 43 — NEW!
  // All hooks after position 43 are now shifted by 1
}

// BROKEN: useState replaced with useStore (different hook type)
function App() {
  // Was: const [sidebar, setSidebar] = useState(false)    // useState
  const { sidebar } = useAppStore()  // useSyncExternalStore — DIFFERENT TYPE
}

// FIXED: Keep original hooks, don't insert or change types
function App() {
  const [a, setA] = useState(false)     // position 1 — unchanged
  const [b, setB] = useState('home')    // position 2 — unchanged
  // ... all original hooks in original order
  // Add new hooks ONLY at the end, or extract into child components
}
```

## Implementation Steps

1. Read the error: note the hook position number and the type mismatch
2. Count hooks in the component top-to-bottom to find which hook changed
3. Identify root cause: insertion, type change, or conditional
4. Fix: revert the change, move new hooks to end, or extract into child component
5. Clear Vite cache: `rm -rf node_modules/.vite`
6. Kill Vite dev server and restart fresh
7. Hard refresh browser (Ctrl+Shift+R)

## When to Use

- Black screen after code changes in a React component
- "Rendered more/fewer hooks" error in console
- Migrating from local state to external stores (Zustand, Jotai, Redux)
- Adding memoization (`useMemo`/`useCallback`) to large components
- Any HMR-related mysterious crashes

## When NOT to Use

- Build errors (not a hooks issue)
- Runtime errors with stack traces pointing to business logic
- SSR hydration mismatches (different root cause)

## Common Mistakes

- Thinking `Ctrl+Shift+R` is enough — Vite's `.vite/` directory cache persists across browser refreshes
- Amending the fix by adding `useMemo` "at the end" but inside a conditional — hooks can't be inside conditionals
- Replacing `useState` with `useRef` and thinking it's safe — `useRef` IS a hook, changing from `useState` to `useRef` at the same position also violates order rules
- Not killing the Vite dev server — HMR may continue serving cached modules even after file changes

## Recovery Checklist

```bash
# 1. Revert the problematic hook changes
git diff src/App.tsx  # Identify what changed

# 2. Clear ALL caches
rm -rf node_modules/.vite

# 3. Kill Vite completely
taskkill //F //IM node.exe  # Windows
# kill $(lsof -ti:5173)    # Mac/Linux

# 4. Restart fresh
npm run dev

# 5. Hard refresh browser
# Ctrl+Shift+R
```

## Related Skills

- liveclock-extraction - Extract state to avoid hooks in large components
- use-visible-interval - Custom hook that's safe to add (leaf components only)

## References

- React docs: "Rules of Hooks" — hooks must be called in the same order every render
- Vite docs: "Dependency Pre-Bundling" — `.vite/` cache behavior
- Contributed from: claude-mission-control App.tsx (black screen crash from hooks order violation)
