---
name: use-visible-interval
category: performance
version: 1.0.0
contributed: 2026-03-12
contributor: claude-mission-control
last_updated: 2026-03-12
contributors:
  - claude-mission-control
tags: [react, intersection-observer, polling, performance, hooks]
difficulty: medium
usage_count: 0
success_rate: 100
---

# useVisibleInterval — Visibility-Aware Polling Hook

## Problem

Dashboard panels that poll APIs on intervals (5s, 10s, 30s) continue fetching even when scrolled off-screen. With 6+ panels each polling independently, this creates unnecessary network traffic, server load, and wasted CPU cycles. On mobile or constrained devices, this compounds into visible jank.

**Symptoms:**
- Network tab shows constant API calls from off-screen components
- Server logs show polling from panels the user isn't viewing
- Battery drain on laptops/mobile from unnecessary background fetches

## Solution Pattern

Create a custom hook that wraps `setInterval` with `IntersectionObserver`. The interval only runs while the component's container element is visible in the viewport. When scrolled off-screen, polling pauses. When scrolled back, it resumes immediately with a fresh fetch.

**Why IntersectionObserver?** It's browser-native, non-blocking (runs off main thread), and has zero performance cost compared to scroll event listeners or `getBoundingClientRect()` polling.

## Code Example

```typescript
// Before (wasteful — polls even when off-screen)
useEffect(() => {
  fetchData()
  const id = setInterval(fetchData, 10000)
  return () => clearInterval(id)
}, [])

// After (visibility-aware — pauses when off-screen)
const containerRef = useRef<HTMLDivElement>(null)
useVisibleInterval(fetchData, 10000, containerRef)
// ... <div ref={containerRef}>...</div>
```

**Full hook implementation:**

```typescript
import { useRef, useEffect } from 'react'

export function useVisibleInterval(
  callback: () => void,
  ms: number,
  containerRef?: React.RefObject<HTMLElement | null>,
) {
  const savedCallback = useRef(callback)
  savedCallback.current = callback

  useEffect(() => {
    // No container ref = fall back to standard interval
    if (!containerRef?.current) {
      savedCallback.current()
      const id = setInterval(() => savedCallback.current(), ms)
      return () => clearInterval(id)
    }

    let intervalId: ReturnType<typeof setInterval> | null = null

    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        // Visible: fire immediately + start interval
        savedCallback.current()
        intervalId = setInterval(() => savedCallback.current(), ms)
      } else {
        // Hidden: stop interval
        if (intervalId !== null) {
          clearInterval(intervalId)
          intervalId = null
        }
      }
    }, { threshold: 0 })

    observer.observe(containerRef.current)

    return () => {
      observer.disconnect()
      if (intervalId !== null) clearInterval(intervalId)
    }
  }, [ms, containerRef])
}
```

## Implementation Steps

1. Create the hook file (e.g., `src/hooks/useVisibleInterval.ts`)
2. Add a `containerRef` to each polling component's root element
3. Replace `useEffect` + `setInterval` with `useVisibleInterval(callback, ms, containerRef)`
4. Verify: scroll panel off-screen, confirm no network calls; scroll back, confirm immediate fetch

## When to Use

- Dashboard panels that poll APIs on intervals
- Any component with periodic data refresh that may be off-screen
- Long scrollable pages with multiple independent data sources
- Tab-based layouts where inactive tabs still mount components

## When NOT to Use

- Global state that must stay current regardless of visibility (e.g., auth token refresh)
- WebSocket/SSE connections (those are push-based, not poll-based)
- Components that are always visible (just use `setInterval`)
- Server-side rendering (IntersectionObserver is browser-only)

## Common Mistakes

- Forgetting to attach `containerRef` to the component's root `<div>` — hook falls back to standard interval silently
- Using `threshold: 1` instead of `0` — component must be 100% visible to trigger, causing missed polls for partially-visible panels
- Not cleaning up the observer on unmount — causes memory leaks

## Related Skills

- ref-based-canvas-animation - Another React performance pattern using refs
- liveclock-extraction - Isolating high-frequency state to leaf components

## References

- MDN IntersectionObserver API
- Contributed from: claude-mission-control (Command & Control dashboard)
