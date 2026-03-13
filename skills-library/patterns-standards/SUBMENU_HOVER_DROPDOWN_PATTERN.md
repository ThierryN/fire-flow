# Submenu Hover Dropdown Pattern

## Category
patterns-standards / navigation

## Problem

Navigation menus with hierarchical items (parent/child) need hover-to-reveal dropdowns on desktop and accordion expand/collapse on mobile. A common bug is the dropdown disappearing when the mouse crosses the gap between the parent item and the dropdown panel. This happens because the `mouseleave` event fires on the parent before `mouseenter` fires on the dropdown, causing the submenu to close instantly.

Additionally, menu items with `type: 'page'` require backend JOIN queries to resolve page slugs for correct URL generation.

---

## Solution - Desktop Hover with setTimeout Delay

Use a `useRef` for a timeout ID and a `setTimeout` delay pattern. The 150ms delay gives users time to move their mouse from the parent nav item to the dropdown panel without it closing.

```javascript
const submenuTimeoutRef = useRef(null);
const [openSubmenu, setOpenSubmenu] = useState(null);

// On mouse enter parent item:
const handleMouseEnter = (itemId) => {
    if (submenuTimeoutRef.current) {
        clearTimeout(submenuTimeoutRef.current);
        submenuTimeoutRef.current = null;
    }
    setOpenSubmenu(itemId);
};

// On mouse leave (both parent item AND dropdown panel share this):
const handleMouseLeave = () => {
    submenuTimeoutRef.current = setTimeout(() => {
        setOpenSubmenu(null);
    }, 150); // 150ms delay prevents flicker
};
```

### Why This Works

Both the parent menu item and the dropdown panel use the **same** `onMouseEnter` and `onMouseLeave` handlers. When the mouse leaves the parent and enters the dropdown within 150ms, `handleMouseEnter` fires on the dropdown and clears the pending timeout before it can close the submenu.

### JSX Structure (Desktop)

```jsx
{/* Parent wrapper - position: relative for absolute dropdown */}
<div
    className="relative"
    onMouseEnter={() => handleMouseEnter(item.id)}
    onMouseLeave={handleMouseLeave}
>
    {/* Parent nav item */}
    <a href={getItemUrl(item)} className="flex items-center gap-1 px-3 py-2">
        {item.label}
        <ChevronDown className="h-4 w-4" />
    </a>

    {/* Dropdown panel - position: absolute, top: 100% */}
    {openSubmenu === item.id && item.children?.length > 0 && (
        <div
            className="absolute left-0 top-full mt-1 w-48 bg-white shadow-lg rounded-md py-1 z-50"
            onMouseEnter={() => handleMouseEnter(item.id)}
            onMouseLeave={handleMouseLeave}
        >
            {item.children.map(child => (
                <a key={child.id} href={getItemUrl(child)} className="block px-4 py-2 hover:bg-gray-100">
                    {child.label}
                </a>
            ))}
        </div>
    )}
</div>
```

### Cleanup on Unmount

Always clear the timeout when the component unmounts to prevent state updates on unmounted components:

```javascript
useEffect(() => {
    return () => {
        if (submenuTimeoutRef.current) {
            clearTimeout(submenuTimeoutRef.current);
        }
    };
}, []);
```

---

## Solution - Mobile Accordion

On mobile, submenus should expand/collapse via tap using a `Set` to track which items are expanded:

```javascript
const [expandedMobileItems, setExpandedMobileItems] = useState(new Set());

const toggleMobileSubmenu = (itemId) => {
    setExpandedMobileItems(prev => {
        const next = new Set(prev);
        if (next.has(itemId)) next.delete(itemId);
        else next.add(itemId);
        return next;
    });
};
```

### JSX Structure (Mobile)

```jsx
<div className="space-y-1">
    {item.children?.length > 0 ? (
        <>
            <button
                onClick={() => toggleMobileSubmenu(item.id)}
                className="w-full flex items-center justify-between px-4 py-2"
            >
                <span>{item.label}</span>
                <ChevronDown className={`h-4 w-4 transition-transform ${
                    expandedMobileItems.has(item.id) ? 'rotate-180' : ''
                }`} />
            </button>
            {expandedMobileItems.has(item.id) && (
                <div className="pl-6 space-y-1">
                    {item.children.map(child => (
                        <a key={child.id} href={getItemUrl(child)} className="block px-4 py-2">
                            {child.label}
                        </a>
                    ))}
                </div>
            )}
        </>
    ) : (
        <a href={getItemUrl(item)} className="block px-4 py-2">
            {item.label}
        </a>
    )}
</div>
```

---

## Solution - Backend: Page-Type Menu Items

Menu items with `type: 'page'` reference a page via `page_id`. The backend MUST JOIN with the `pages` table to include the page slug so the frontend can generate correct URLs:

```sql
SELECT mi.*, p.slug AS page_slug
FROM menu_items mi
LEFT JOIN pages p ON mi.page_id = p.id
WHERE mi.menu_id = ${menu.id}
ORDER BY mi.position ASC
```

### Frontend URL Resolution

The `getItemUrl` helper must check `page_slug` first, then fall back to `page_id` and raw URL:

```javascript
const getItemUrl = (item) => {
    if (item.type === 'page' && item.page_slug) {
        return '/' + item.page_slug;
    }
    if (item.type === 'page' && item.page_id) {
        return item.url || '#'; // fallback
    }
    if (item.url && !item.url.startsWith('http') && !item.url.startsWith('/')) {
        return '/' + item.url;
    }
    return item.url || '#';
};
```

---

## Key Implementation Notes

1. **Both parent and dropdown use the same `onMouseEnter`/`onMouseLeave` handlers** -- this is what makes the gap-crossing work.
2. **Dropdown panel uses `position: absolute`** with `top: 100%` to appear below the parent.
3. **Desktop dropdown wrapper**: `position: relative` on the parent container so the absolute dropdown positions correctly.
4. **Theme compatibility**: For theme files in `/themes/`, use `useRef` and `useState` from React directly (no npm imports allowed -- see `CLAUDE.md` Theme Development CRITICAL RULES).
5. **Cleanup**: Clear timeout on component unmount via `useEffect` return callback.
6. **Mobile sidebar must have `lg:hidden`** on toggle button, panel, and backdrop (three elements).
7. **150ms is the sweet spot** -- shorter causes flicker, longer feels sluggish.

---

## Files Modified (MERN LMS)

| File | Role |
|------|------|
| `client/src/components/layout/Header.jsx` | Classic theme header |
| `themes/aurora-borealis/components/layout/Header.jsx` | Aurora Borealis theme |
| `themes/celestial/components/layout/Header.jsx` | Celestial theme |
| `themes/melchizedek-order/components/layout/Header.jsx` | Melchizedek Order theme |
| `themes/royal-priesthood/components/layout/Header.jsx` | Royal Priesthood theme |
| `themes/prosperity/components/layout/Header.jsx` | Prosperity theme |
| `themes/prophetic-academy/components/layout/Header.jsx` | Prophetic Academy theme |
| `server/controllers/menuController.js` | Backend JOIN fix for page slugs |

---

## When to Use

- Any navigation menu with parent/child hierarchy
- Dropdown menus that appear on hover (desktop)
- Mobile-responsive navigation with accordion submenus
- Page-type menu items that need slug resolution from the database
- Theme components that cannot import npm packages directly

---

## Common Mistakes to Avoid

1. **Forgetting to share handlers between parent and dropdown** -- the dropdown must also call `handleMouseEnter`/`handleMouseLeave` or it will close when the mouse enters it.
2. **Using `onMouseOver`/`onMouseOut` instead of `onMouseEnter`/`onMouseLeave`** -- the former bubble from children and cause erratic behavior.
3. **Not clearing the timeout on unmount** -- leads to "setState on unmounted component" warnings.
4. **Missing the LEFT JOIN on pages** -- page-type menu items will have no slug and render as `#` links.
5. **Importing `react-router-dom` Link in theme files** -- theme files are outside the Vite workspace; use plain `<a>` tags or a local Link wrapper.

---

## Tags

navigation, submenu, hover, dropdown, accordion, mobile, menu, react, setTimeout, useRef, page-slug, backend-join, theme-compatibility
