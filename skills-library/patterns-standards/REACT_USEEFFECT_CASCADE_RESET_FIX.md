# React useEffect Cascade Reset Fix

## Problem

Custom hooks with cascading dropdown state (e.g., Book → Chapter → Verse) use `useEffect` chains where selecting a parent resets child values to `null`. When programmatically navigating to a specific location (e.g., clicking a search result to jump to Genesis 3:15), the cascade effects fire and **destroy the child selections** before the UI can render them.

**Symptoms:**
- Clicking a search result navigates to the correct book/chapter but verse is not highlighted
- Programmatic navigation sets all three values, but useEffect on book change wipes chapter/verse
- The chapter effect then fires again and wipes the verse

## Root Cause

React's `useEffect` chains create a cascade:

```
setSelectedBook("Genesis")  →  useEffect[selectedBook] fires  →  setSelectedChapter(null) ← DESTROYS
                                                                   setSelectedVerse(null)  ← DESTROYS
setSelectedChapter(3)       →  useEffect[selectedChapter] fires →  setSelectedVerse(null) ← DESTROYS
setSelectedVerse(15)        →  Already nullified by cascade
```

Even though all three `setState` calls happen synchronously, React batches them but the effects still run in order, each one resetting the children.

## Solution: Programmatic Navigation Ref Guard

Use a `useRef` flag to skip cascade resets during programmatic navigation:

```typescript
import { useState, useEffect, useCallback, useRef } from 'react'

export function useCascadingNavigation() {
  const [selectedBook, setSelectedBook] = useState<string | null>(null)
  const [selectedChapter, setSelectedChapter] = useState<number | null>(null)
  const [selectedVerse, setSelectedVerse] = useState<number | null>(null)

  // Ref to skip cascade resets during programmatic navigation
  const programmaticNavRef = useRef(false)

  // Update chapters when book changes
  useEffect(() => {
    if (selectedBook) {
      const chapterCount = getChapterCount(selectedBook)
      setChapters(Array.from({ length: chapterCount }, (_, i) => i + 1))

      // Skip reset during programmatic navigation
      if (!programmaticNavRef.current) {
        setSelectedChapter(null)
        setSelectedVerse(null)
      }
    }
  }, [selectedBook])

  // Update verses when chapter changes
  useEffect(() => {
    if (selectedBook && selectedChapter) {
      fetchVerseCount(selectedBook, selectedChapter)

      // Skip verse reset during programmatic navigation
      if (!programmaticNavRef.current) {
        setSelectedVerse(null)
      }
      // Reset flag after chapter effect processes
      programmaticNavRef.current = false
    }
  }, [selectedBook, selectedChapter])

  // Navigate to a specific location without cascade resets
  const navigateToVerse = useCallback((book: string, chapter: number, verse: number) => {
    programmaticNavRef.current = true
    setSelectedBook(book)
    setSelectedChapter(chapter)
    setSelectedVerse(verse)
  }, [])

  // Safety cleanup: ensure flag is always reset after effects process
  useEffect(() => {
    programmaticNavRef.current = false
  })

  return {
    selectedBook, setSelectedBook,
    selectedChapter, setSelectedChapter,
    selectedVerse, setSelectedVerse,
    navigateToVerse,  // Use this for programmatic navigation
  }
}
```

### Key Implementation Details

1. **`programmaticNavRef`** — A ref (not state) because it needs to be set synchronously before effects run, without triggering re-renders.

2. **Flag reset location** — The flag is reset in the **chapter effect** (the last cascade effect that needs guarding), not immediately after setting state. This ensures the flag persists through all cascade effects.

3. **Safety cleanup effect** — An unconditional `useEffect(() => { programmaticNavRef.current = false })` with no dependency array runs after every render, ensuring the flag is always cleaned up even if an effect chain is interrupted.

4. **Consumer usage** — Components call `navigateToVerse()` instead of individual setters:

```typescript
// In BibleViewer.tsx (consumer component)
const { navigateToVerse } = useBibleNavigation()

useEffect(() => {
  if (navigateTo && navigateTo !== prevNavigateToRef.current) {
    prevNavigateToRef.current = navigateTo
    navigateToVerse(navigateTo.book, navigateTo.chapter, navigateTo.verse)
  }
}, [navigateTo, navigateToVerse])
```

## When to Apply This Pattern

- Any cascading dropdown hook (Country → State → City)
- Multi-level navigation (Book → Chapter → Verse, Category → Subcategory → Item)
- Any hook where parent selection resets child selections, AND you need programmatic deep navigation
- Search result → detail view navigation

## Anti-Patterns to Avoid

1. **Don't use state for the flag** — `useState` triggers re-renders and the flag won't be set before effects run
2. **Don't set all values in a single effect** — Still triggers cascades because each `setState` triggers dependent effects
3. **Don't try `flushSync`** — Doesn't prevent effect cascades, just forces synchronous DOM updates
4. **Don't remove the cascade resets entirely** — Manual dropdown selection genuinely needs child resets

## Tech Stack
- React 18+ (hooks, useRef, useEffect, useCallback)
- TypeScript
- Any UI framework with cascading state

## Tags
`react` `useEffect` `cascade` `useState` `navigation` `dropdown` `useRef` `programmatic-navigation`
