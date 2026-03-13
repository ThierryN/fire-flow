---
name: liveclock-extraction
category: performance
version: 1.0.0
contributed: 2026-03-12
contributor: claude-mission-control
last_updated: 2026-03-12
contributors:
  - claude-mission-control
tags: [react, performance, re-renders, state-isolation, composition]
difficulty: easy
usage_count: 0
success_rate: 100
---

# LiveClock Extraction — Isolating High-Frequency Timers

## Problem

A `useEffect` + `setInterval` that updates a clock or timer every second in a parent component (like `App.tsx` or a layout wrapper) causes the **entire component tree** to re-render once per second. If the parent renders a sidebar, header, navigation, and multiple panels, all of them re-render 60 times per minute for a single clock display.

**Symptoms:**
- React DevTools shows App re-rendering every ~1000ms
- All child components flash in Profiler even though only the clock changed
- Input fields lose focus or feel laggy
- `useCurrentTime()` or similar hook used in a large parent

## Solution Pattern

Extract the timer into the smallest possible leaf component. The leaf owns the state and the interval. The parent never re-renders from clock ticks.

**Principle:** State should live in the component that renders it, not in a parent that passes it down.

## Code Example

```typescript
// Before (1Hz full-tree re-renders)
function App() {
  const [time, setTime] = useState(new Date())
  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  return (
    <div>
      <Header />           {/* re-renders every second */}
      <Sidebar />          {/* re-renders every second */}
      <span>{time.toLocaleTimeString()}</span>
      <MainContent />      {/* re-renders every second */}
    </div>
  )
}

// After (only LiveClock re-renders)
function LiveClock() {
  const [time, setTime] = useState(new Date())
  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(id)
  }, [])
  return (
    <span className="text-xs font-mono">
      {time.toLocaleTimeString('en-US', {
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      })}
    </span>
  )
}

function App() {
  return (
    <div>
      <Header />
      <Sidebar />
      <LiveClock />        {/* only this re-renders */}
      <MainContent />
    </div>
  )
}
```

## Implementation Steps

1. Find any `useState` + `setInterval` pattern in large parent components
2. Create a small leaf component that owns both the state and the render
3. Replace the inline rendering in the parent with the new component
4. Verify: React DevTools Profiler should show only the leaf re-rendering

## When to Use

- Clocks, timers, countdowns, "X minutes ago" displays in layout components
- Any high-frequency state update (polling status indicators, progress bars) in a parent
- Animated indicators (blinking dots, pulse effects) driven by `setInterval`

## When NOT to Use

- When the time/value is genuinely needed by siblings (lift state or use context)
- When the parent component is already small and cheap to render
- Server components (no client-side intervals)

## Common Mistakes

- Extracting the component but still passing time as a prop from parent — defeats the purpose
- Using a custom hook like `useCurrentTime()` in the parent — the hook's state still lives in the parent
- Creating the leaf component but wrapping it in `React.memo` on the parent side — unnecessary, the fix is isolation not memoization

## References

- React docs: "Extracting State Logic into Components"
- Dan Abramov: "Before You memo()" — restructure before optimizing
- Contributed from: claude-mission-control App.tsx (eliminated 1Hz full-tree re-renders)
