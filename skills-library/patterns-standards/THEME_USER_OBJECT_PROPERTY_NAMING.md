# Theme User Object Property Naming Mismatch - Solution & Prevention

## The Problem

Theme components display "User" instead of the actual user's first name (e.g., "FirstName") in the header navigation. The profile avatar initial also shows "U" instead of the first letter of the name.

### Error/Symptom
```
Expected: [Avatar] FirstName ▼
Actual:   [Avatar] User ▼
```

No console errors thrown - this is a silent data mismatch.

### Why It Was Hard

- No error messages - the fallback `|| 'User'` silently hides the bug
- The property naming difference is subtle: `first_name` (snake_case) vs `firstName` (camelCase)
- Theme components are isolated from the main app (no shared type system)
- Different themes may use different property names depending on who wrote them
- The backend auth response and localStorage user object aren't documented in any shared schema

### Impact

- Users see "User" instead of their name across the entire site header
- Affects all logged-in users on any theme with the wrong property names
- Professional appearance degraded

---

## The Solution

### Root Cause

The backend `authController.js` login response sends the user object with **camelCase** properties:

```javascript
// server/controllers/authController.js (login response)
{
  id: user.id,
  name: user.name,           // "Userlastname" (full name)
  firstName,                  // "FirstName" (parsed from name)
  lastName,                   // "lastname" (parsed from name)
  email: user.email,
  role: user.role,
  avatar_url: user.avatar_url,
  isVerified: user.email_verified,
  email_verified: user.email_verified,
}
```

But theme components were written using **snake_case** properties:

```javascript
// BAD - Theme Header.jsx
{user?.first_name || 'User'}          // first_name doesn't exist!
{user?.first_name} {user?.last_name}  // Both undefined!
```

### How to Fix

Replace snake_case with camelCase, with fallbacks to `name` parsing:

```javascript
// GOOD - Theme Header.jsx

// Display first name (with fallback to parsing full name)
{user?.firstName || user?.name?.split(' ')[0] || 'User'}

// Display full name in dropdown
{user?.firstName || user?.name?.split(' ')[0]} {user?.lastName || user?.name?.split(' ').slice(1).join(' ')}

// Avatar initial
{user?.firstName?.charAt(0) || user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}

// Alt text
alt={user?.firstName || user?.name || 'User'}
```

### Why the Fallback Pattern

The `user?.name?.split(' ')[0]` fallback handles:
1. Old user objects cached in localStorage before `firstName` was added
2. Any code path that stores only `name` without parsing
3. Edge case where user logs in through a different auth flow

---

## Complete User Object Reference

### From `authController.js` Login Response:
```javascript
{
  id: "uuid",
  name: "Userlastname",       // Full name (always present)
  firstName: "FirstName",         // Parsed first name
  lastName: "lastname",            // Parsed last name
  email: "FirstName@example.com",
  role: "admin",                // admin | manager | moderator | student
  avatar_url: "/uploads/...",   // Profile picture URL
  isVerified: true,
  email_verified: true,
}
```

### Properties NOT Available (common mistakes):
- `first_name` (snake_case) - DOES NOT EXIST
- `last_name` (snake_case) - DOES NOT EXIST
- `avatarUrl` (camelCase) - exists in some contexts but `avatar_url` is primary
- `username` - not used in this LMS
- `displayName` - not used

---

## Testing the Fix

### Before
```
Header shows: [green circle with "U"] User ▼
Dropdown shows: "undefined undefined" and "user@email.com"
```

### After
```
Header shows: [green circle with "T"] User▼
Dropdown shows: "Userlastname" and "FirstName@email.com"
```

### Quick Test
1. Log in as any user
2. Check header navigation - should show first name
3. Open dropdown - should show full name and email
4. Check mobile sidebar - should show first name

---

## Prevention

1. **Always check `authController.js`** for the actual user object shape before using properties in themes
2. **Use camelCase** for user properties in themes: `firstName`, `lastName`, `avatarUrl`
3. **Always add fallbacks**: `user?.firstName || user?.name?.split(' ')[0] || 'User'`
4. **Check ALL themes** when fixing one - there are 8 themes in this project
5. **Document the user object** in THEME_DEVELOPMENT.md so theme authors know the correct properties

### Themes to Check:
```
themes/the-mountain/     (FIXED 2026-02-14)
themes/eden/
themes/aurora-borealis/
themes/celestial/
themes/melchizedek-order/
themes/prophetic-academy/
themes/prosperity/
themes/royal-priesthood/
```

---

## Related Patterns

- Theme components use `window.__LMS_AUTH__` or `localStorage.getItem('user')` for auth
- The `useAuth()` hook in themes reads from these sources
- Main app header (`client/src/components/layout/Header.jsx`) uses Redux store which has different property access

---

## Common Mistakes to Avoid

- Don't use `user?.first_name` (snake_case) - backend sends `firstName` (camelCase)
- Don't use `user?.last_name` (snake_case) - backend sends `lastName` (camelCase)
- Don't assume `firstName` always exists - add `name?.split(' ')[0]` fallback
- Don't forget theme files are in `.gitignore` - use `git add -f themes/...` to stage
- Don't fix only one theme - check all 8 themes for the same issue

---

## Resources

- `server/controllers/authController.js` lines 103-129 - Login response user object
- `themes/THEME_DEVELOPMENT.md` - Theme development guide
- `docs/THEME_COMPLETE_DEVELOPER_GUIDE.md` - Complete theme developer guide

## Time to Implement

**5 minutes per theme** - Simple find/replace of property names with fallbacks

## Difficulty Level

Stars: 2/5 - Easy fix once you know the root cause, hard to diagnose initially because of silent fallback to 'User'

---

**Author Notes:**
This cost ~30 minutes to diagnose because "User" appearing instead of a name could have many causes (auth not loading, user object empty, wrong hook, etc.). The silent `|| 'User'` fallback made it invisible. The key insight: always verify the actual shape of the user object from the backend before writing theme code. Run `JSON.stringify(JSON.parse(localStorage.getItem('user')))` in the browser console to see exactly what's there.
