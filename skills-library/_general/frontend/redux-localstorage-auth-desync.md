---
name: redux-localstorage-auth-desync
category: frontend
version: 1.0.0
contributed: 2026-03-06
contributor: ministry-lms
last_updated: 2026-03-06
tags: [redux, react, auth, localStorage, infinite-loop, redirect, login]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Redux + localStorage Auth State Desync (Infinite Login Loop)

## Problem

After a token expires or `getMe()` API call fails, the app enters an infinite redirect loop between `/login` and `/dashboard`:

```
Login → checks localStorage → has token → navigate(/dashboard)
  → PrivateRoute → checks Redux isAuthenticated → false → navigate(/login)
    → Login → checks localStorage → has token → navigate(/dashboard)
      → ... "Maximum update depth exceeded"
```

The browser console shows: `Warning: Maximum update depth exceeded` and the page flickers rapidly between routes.

## Root Cause

**Two auth sources are out of sync:**

1. **Redux store** — `isAuthenticated: false` (correctly cleared by `getMe.rejected`)
2. **localStorage** — still has `token` and `user` (NOT cleared by Redux reducer)

The Login page checks `localStorage.getItem('token')` on mount and auto-redirects to dashboard if a token exists. But `PrivateRoute` checks Redux `isAuthenticated` and bounces back to login. Neither clears localStorage, so the loop never breaks.

## Solution Pattern

**Clear localStorage in the same reducer that clears Redux state.** When the auth verification fails, BOTH state stores must be cleaned:

```javascript
// authSlice.js — getMe.rejected reducer
builder.addCase(getMe.rejected, (state) => {
  state.loading = false;
  state.isAuthenticated = false;
  state.user = null;
  state.token = null;
  // CRITICAL: Clear localStorage to prevent Login→PrivateRoute redirect loop
  localStorage.removeItem('token');
  localStorage.removeItem('user');
});
```

## Code Example

```javascript
// Before (broken) — Redux clears, localStorage doesn't
builder.addCase(getMe.rejected, (state) => {
  state.loading = false;
  state.isAuthenticated = false;
  state.user = null;
  state.token = null;
  // localStorage still has token → Login sees it → redirects to dashboard → loop
});

// After (fixed) — Both stores cleared atomically
builder.addCase(getMe.rejected, (state) => {
  state.loading = false;
  state.isAuthenticated = false;
  state.user = null;
  state.token = null;
  localStorage.removeItem('token');
  localStorage.removeItem('user');
});
```

## Implementation Steps

1. Identify all places where Redux auth state is cleared (rejected thunks, logout)
2. Add `localStorage.removeItem()` calls in each one
3. Verify Login page checks are consistent (Redux OR localStorage, not both independently)
4. Test by manually expiring the token and refreshing the page

## When to Use

- Login page flickers or shows "Maximum update depth exceeded"
- Users can't log in after token expiration (stuck in redirect loop)
- App uses BOTH Redux and localStorage for auth state
- `getMe()` or token verification endpoint returns 401 but user sees login flash

## When NOT to Use

- App uses only Redux for auth (no localStorage persistence)
- App uses only localStorage (no Redux)
- Auth is handled by httpOnly cookies (no client-side token storage)
- The infinite loop is caused by something other than auth state desync

## Common Mistakes

- Clearing only Redux state, not localStorage
- Clearing only on logout, not on token verification failure
- Having Login check localStorage while PrivateRoute checks Redux (inconsistent sources)
- Not clearing on ALL rejection paths (login.rejected, getMe.rejected, etc.)

## Architectural Lesson

**Single source of truth for auth.** If you persist auth in localStorage AND Redux, they MUST be updated atomically. The safest pattern:

1. Redux is the source of truth for the running app
2. localStorage is ONLY for persistence across page reloads
3. On app start: read localStorage → hydrate Redux → then ONLY use Redux
4. On any auth state change: update Redux FIRST, then sync to localStorage
5. On any auth failure: clear BOTH simultaneously

## Related Skills

- [auth-jwt-basics](../../common-tasks/auth-jwt-basics.md) - JWT auth patterns
- [postgresql-to-mysql-runtime-translation](../../database-solutions/postgresql-to-mysql-runtime-translation.md) - The migration that surfaced this bug

## References

- React Router v6 redirect behavior: navigation inside useEffect creates render loops
- Redux Toolkit createAsyncThunk: rejected case must handle side effects
- Discovered during: MINISTRY-LMS PG→MySQL migration (getMe API failing due to DB errors triggered the loop)
- File: `client/src/store/slices/authSlice.js` line 304-312
