---
name: image-overflow-fix
category: lms-patterns
version: 1.0.0
contributed: 2026-02-23
contributor: MINISTRY-LMS
last_updated: 2026-02-23
tags: [react, css, admin, images, overflow, broken-images, tailwind]
difficulty: easy
usage_count: 0
success_rate: 100
---

# Image Overflow Fix — Broken Alt Text Layout Corruption

## Problem

When `<img>` tags return 404 (broken URLs, missing uploads, wrong paths), browsers render the `alt` text as a fallback. This alt text **ignores CSS width/height constraints** on the `<img>` element, causing:

- Long course titles or usernames spilling out of table cells
- Sidebar logos pushing nav items off-screen
- Avatar placeholders breaking card layouts
- Product thumbnails overflowing grid columns

**Symptoms:**
- Text appears where images should be, overlapping other elements
- Layout looks fine until images fail to load
- Problem appears after migration or when CDN/uploads are misconfigured
- Alt text like "Introduction to Advanced Biblical Hermeneutics" breaks a 40x40 avatar container

**Root cause:** The `alt` attribute contains descriptive text (product name, user name, course title) that renders as inline text when the image 404s. CSS `width`, `height`, `object-fit` on `<img>` do NOT constrain the fallback alt text.

## Solution Pattern

**Three-layer defense:**

1. **`overflow-hidden` wrapper div** — CSS containment prevents ANY overflow
2. **`alt=""`** — Empty alt removes fallback text entirely (screen readers skip decorative images)
3. **`onError` handler** — Hides the broken image or replaces with a fallback

## Code Example

```jsx
// BEFORE (problematic) — alt text overflows when image 404s
<img
  src={user.avatar_url}
  alt={user.name}
  className="h-10 w-10 rounded-full object-cover"
/>

// AFTER (solution) — three-layer defense
<div className="flex-shrink-0 h-10 w-10 overflow-hidden rounded-full">
  <img
    src={user.avatar_url}
    alt=""
    className="h-10 w-10 rounded-full object-cover"
    onError={(e) => {
      e.target.onerror = null;
      e.target.style.display = 'none';
    }}
  />
</div>
```

### Variant: With Fallback Initial

```jsx
// Avatar with letter fallback when image fails
<div className="flex-shrink-0 h-10 w-10 overflow-hidden rounded-full">
  <img
    src={user.avatar_url}
    alt=""
    className="h-10 w-10 rounded-full object-cover"
    onError={(e) => {
      e.target.onerror = null;
      e.target.style.display = 'none';
      e.target.parentElement.innerHTML = `
        <div class="h-10 w-10 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600
          flex items-center justify-center text-white font-bold text-lg shadow-lg">
          ${(user?.name?.charAt(0) || 'A').toUpperCase()}
        </div>`;
    }}
  />
</div>
```

### Variant: Product Thumbnail

```jsx
// Product/course thumbnail in table or grid
{product.featured_image && (
  <div className="h-10 w-10 flex-shrink-0 overflow-hidden rounded-lg">
    <img
      src={product.featured_image}
      alt=""
      className="h-10 w-10 rounded-lg object-cover"
      onError={(e) => { e.target.style.display = 'none'; }}
    />
  </div>
)}
```

### Variant: Sidebar Logo

```jsx
// Logo in sidebar/navbar
<div className="h-8 w-8 flex-shrink-0 overflow-hidden">
  <img
    src={settings.admin_logo || '/logo.png'}
    alt=""
    className="h-8 w-8 object-contain"
    onError={(e) => { e.target.style.display = 'none'; }}
  />
</div>
```

## Implementation Steps

1. **Find all `<img>` tags** in admin pages that display user-generated content (avatars, thumbnails, logos)
2. **Wrap each in a div** with matching dimensions + `overflow-hidden` + appropriate rounding
3. **Set `alt=""`** on all decorative images (thumbnails, avatars, logos)
4. **Add `onError` handler** to hide or replace the broken image
5. **Add `flex-shrink-0`** on the wrapper to prevent flex containers from collapsing it

## When to Use

- Any admin panel with user avatars, product images, course thumbnails
- After migrating databases where image URLs may not transfer
- When deploying to a new server where upload paths differ
- In table rows where images sit next to text content
- In sidebar/nav layouts where space is constrained
- On any page where images are loaded from user-provided URLs

## When NOT to Use

- Content images that MUST have alt text for accessibility (article body images)
- Images where the alt text provides essential information to screen reader users
- Images from guaranteed-available sources (bundled assets, SVG icons)
- When a proper image loading component with placeholder is already in use

## Common Mistakes

- **Only adding `onError`** — Alt text renders BEFORE `onError` fires, causing a flash of broken layout
- **Only setting `alt=""`** — Some browsers still render a broken image icon
- **Only adding `overflow-hidden`** — Fixes layout but leaves invisible broken image taking space
- **Using `alt={user.name}`** on decorative images — Screen readers announce every avatar
- **Forgetting `flex-shrink-0`** — Flex layouts can collapse the wrapper to 0 width
- **Not setting `e.target.onerror = null`** in handler — Can cause infinite loop if fallback also fails

## Files Fixed in MINISTRY-LMS (Reference)

| File | Location | Type |
|------|----------|------|
| `AdminLayout.jsx` | Sidebar logo (~line 264) | Logo |
| `AdminLayout.jsx` | Sidebar avatar (~line 290) | Avatar with initial fallback |
| `Enrollments.jsx` | Enrollment table (~line 689) | Student avatar |
| `Enrollments.jsx` | Secondary view (~line 456) | User avatar |
| `Products.jsx` | Product table (~line 578) | Product thumbnail |
| `Users.jsx` | User table (~line 866) | User avatar |
| `CourseStudents.jsx` | Student table (~line 264) | Enrollee avatar |

## Quick Grep to Find Affected Images

```bash
# Find img tags with dynamic alt text (likely overflow candidates)
grep -rn 'alt={' --include="*.jsx" --include="*.tsx" src/pages/admin/
grep -rn 'alt={.*\.name' --include="*.jsx" --include="*.tsx" src/
```

## Related Skills

- [lms-theme-system](./lms-theme-system.md) - Theme system where images are configured
- [wordpress-style-theme-components](./wordpress-style-theme-components.md) - Component patterns

## References

- MDN: [alt attribute](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#alt) — empty string marks decorative images
- Tailwind: `overflow-hidden` = `overflow: hidden` — clips all overflow content
- Contributed from: MINISTRY-LMS MySQL migration session (2026-02-23)
