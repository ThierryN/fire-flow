# Tooltip Blocking Clicks - Pointer Events Solution

## The Problem

Clickable elements (like Strong's numbers, buttons, or links) become unclickable when a tooltip appears over them. The tooltip overlay intercepts click events before they reach the underlying interactive element.

### Symptoms

- Hover works (tooltip appears correctly)
- Click does nothing (no event handler fires)
- Server logs show API calls from hover (tooltip data fetch)
- Browser console shows NO click logs (event never reaches handler)
- User clicks multiple times with no response

### Why It Was Hard

- **Silent failure** - No error messages, clicks just silently fail
- **Timing-dependent** - Only happens when tooltip is visible (after hover delay)
- **Z-index confusion** - High z-index tooltip covers clickable area
- **Event propagation** - Tooltip intercepts events before they bubble down

### Impact

- Feature appears completely broken to users
- Users think the button/link doesn't work
- Frustrating UX - "I'm clicking but nothing happens!"
- Can affect critical workflows (concordance panels, modals, navigation)

---

## The Solution

### Root Cause

The tooltip is absolutely positioned with a high z-index (`z-50`) and appears directly over the clickable element. When the user clicks, the tooltip receives the click event instead of the underlying button/link.

**Bad Code (Blocks Clicks):**
```tsx
<span className="tooltip-wrapper relative inline-block">
  <button onClick={handleClick}>Click Me</button>
  {showTooltip && (
    <span className="absolute z-50 px-2 py-1 bg-gray-900 rounded">
      Tooltip Text
    </span>
  )}
</span>
```

### How to Fix

Add `pointer-events-none` to the tooltip so mouse events pass through to underlying elements:

**Good Code (Allows Clicks):**
```tsx
<span className="tooltip-wrapper relative inline-block">
  <button onClick={handleClick}>Click Me</button>
  {showTooltip && (
    <span className="absolute z-50 px-2 py-1 bg-gray-900 rounded pointer-events-none">
      Tooltip Text
    </span>
  )}
</span>
```

### Complete Working Example

```tsx
import { useState } from 'react';

interface TooltipProps {
  children: React.ReactNode;
  content: string;
}

export function Tooltip({ children, content }: TooltipProps) {
  const [show, setShow] = useState(false);
  const [hoverTimeout, setHoverTimeout] = useState<NodeJS.Timeout | null>(null);

  const handleMouseEnter = () => {
    // 500ms delay before showing tooltip
    const timeout = setTimeout(() => setShow(true), 500);
    setHoverTimeout(timeout);
  };

  const handleMouseLeave = () => {
    if (hoverTimeout) {
      clearTimeout(hoverTimeout);
      setHoverTimeout(null);
    }
    setShow(false);
  };

  return (
    <span
      className="tooltip-wrapper relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      {show && (
        <span className="absolute z-50 px-2 py-1 text-xs font-medium text-white bg-gray-900 rounded shadow-lg whitespace-nowrap -top-8 left-1/2 transform -translate-x-1/2 pointer-events-none">
          {content}
          {/* Tooltip arrow (also needs pointer-events-none on parent) */}
          <span className="absolute w-2 h-2 bg-gray-900 transform rotate-45 -bottom-1 left-1/2 -translate-x-1/2"></span>
        </span>
      )}
    </span>
  );
}

// Usage
<Tooltip content="Click to open concordance">
  <button onClick={() => console.log('Clicked!')}>
    Strong's #H7225
  </button>
</Tooltip>
```

---

## Testing the Fix

### Debugging Strategy

1. **Add console.logs to click handler:**
   ```typescript
   const handleClick = () => {
     console.log('Click event fired!'); // Should see this
     // ... rest of handler
   };
   ```

2. **Test with tooltip hidden:**
   - Click immediately (before tooltip appears)
   - Should work ✅

3. **Test with tooltip visible:**
   - Hover until tooltip appears (wait 500ms)
   - Click while tooltip is visible
   - Should work ✅ (after adding pointer-events-none)

### Before Fix
```
Browser Console: (nothing - click never reaches handler)
Server Logs: GET /api/tooltip/data (hover working)
User Action: Click, click, click... (frustrated)
```

### After Fix
```
Browser Console: "Click event fired!"
Server Logs: GET /api/tooltip/data, POST /api/action (both working)
User Action: Click (success!)
```

---

## Prevention

### Checklist for Interactive Tooltips

- ✅ **Always add `pointer-events-none`** to tooltip overlays
- ✅ **Test clicks while tooltip is visible** (not just when hidden)
- ✅ **Add console.log debugging** to verify events fire
- ✅ **Check z-index values** - high z-index means potential click blocking
- ✅ **Test on different browsers** - event handling can vary

### Code Review Questions

When reviewing tooltip implementations:
1. Does the tooltip have `pointer-events-none`?
2. Can you click the underlying element while hovering?
3. Are there console logs to verify click events?
4. Is the z-index appropriate (not unnecessarily high)?

---

## Related Patterns

- [Modal Dialog Click Outside Detection](./MODAL_CLICK_OUTSIDE_FIX.md)
- [Dropdown Menu Event Handling](./DROPDOWN_EVENT_HANDLING.md)
- [Z-Index Stacking Context Guide](./Z_INDEX_STACKING_MEMORY.md)

---

## Common Mistakes to Avoid

- ❌ **Removing z-index** - Tooltip won't appear on top
- ❌ **Stopping event propagation** - Breaks other handlers
- ❌ **Using display: none on hover** - Tooltip flickers
- ❌ **Not testing with tooltip visible** - Only test when hidden
- ❌ **Assuming clicks work because hover works** - Different events!

---

## CSS Pointer Events Reference

```css
/* No pointer events - clicks pass through */
pointer-events: none;

/* Default - element receives events */
pointer-events: auto;

/* Only on visible parts (ignores transparent areas) */
pointer-events: visible;

/* Never receives events (even when visible) */
pointer-events: none;
```

**Key insight:** `pointer-events: none` makes the element "invisible" to the mouse cursor for interaction purposes, while still being visually displayed.

---

## Resources

- [MDN: pointer-events](https://developer.mozilla.org/en-US/docs/Web/CSS/pointer-events)
- [React Event Handling](https://react.dev/learn/responding-to-events)
- [CSS Z-Index and Stacking Context](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_positioned_layout/Understanding_z-index/Stacking_context)
- [Tooltip Accessibility Best Practices](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/)

---

## Time to Implement

**2 minutes** - Just add `pointer-events-none` to tooltip className

## Difficulty Level

⭐ (1/5) - Extremely simple once you know the solution, but hard to diagnose initially

---

## Real-World Example: Ministry LLM Strong's Numbers

**Context:** Bible study app with Strong's numbers (H7225, G430, etc.) that should open a concordance panel when clicked. Hovering shows Hebrew/Greek text in a tooltip.

**Problem:** Clicking Strong's numbers did nothing. Users couldn't access concordances.

**Diagnosis:**
- Server logs showed tooltip API calls working (`GET /api/strongs/H7225`)
- Browser console showed NO click logs (handler never fired)
- This proved the tooltip was blocking clicks

**Solution:** Added `pointer-events-none` to tooltip at line 79 of StrongsTooltip.tsx

**Result:** Clicks now pass through tooltip to underlying `<sup>` element, concordance panel opens correctly.

---

**Author Notes:**

This bug is **deceptively simple** - the fix is one CSS class, but the debugging process requires understanding:
1. Event propagation and capture
2. Z-index stacking contexts
3. The difference between hover events (work) and click events (blocked)

The key diagnostic insight: **Server logs show hover working, browser console shows no click logs = tooltip blocking clicks.**

Always test interactive elements with overlays visible, not just hidden!

---

**Created:** 2026-02-09
**Last Updated:** 2026-02-09
**Tested With:** React 18, Tailwind CSS, TypeScript
