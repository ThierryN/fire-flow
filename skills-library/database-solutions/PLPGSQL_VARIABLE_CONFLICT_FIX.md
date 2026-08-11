# PL/pgSQL RETURNS TABLE Column Name Conflicts — #variable_conflict use_column

## The Problem

PostgreSQL functions using `RETURNS TABLE` with column names that match actual table columns cause `42702: column reference "X" is ambiguous` errors at runtime.

```
ERROR: 42702
DETAIL: It could refer to either a PL/pgSQL variable or a table column.
MESSAGE: column reference "user_id" is ambiguous
```

### Why It Was Hard

- `CREATE OR REPLACE FUNCTION` succeeds without error — the ambiguity only surfaces at **call time**
- Table aliases (`up.user_id`) fix SELECT statements but NOT INSERT column lists or ON CONFLICT clauses
- Renaming RETURNS TABLE columns changes the return type, so `CREATE OR REPLACE` silently fails — you must `DROP FUNCTION` first
- The error is identical whether the fix wasn't applied or the function wasn't actually replaced
- Multiple debugging approaches (table aliases, column renaming) address symptoms but not root cause

### Impact

- RPC calls from Supabase/PostgREST return 400 Bad Request
- Application falls back to plaintext storage (security regression)
- Impossible to use encrypted save/load functions

---

## The Solution

### Root Cause

PL/pgSQL `RETURNS TABLE` columns become **local variables** in the function scope. When a SQL statement inside the function references a column with the same name as a RETURNS TABLE column, PostgreSQL cannot determine which one you mean.

```sql
-- This creates a variable called "user_id" in the function scope:
RETURNS TABLE (
  id UUID,
  user_id UUID,  -- <-- becomes a PL/pgSQL variable
  ...
)

-- This is now ambiguous:
INSERT INTO user_profiles (user_id, ...) VALUES (p_user_id, ...);
-- PostgreSQL asks: is "user_id" the RETURNS TABLE variable or the table column?
```

### How to Fix

Add `#variable_conflict use_column` as the FGTAT line inside the function body (after `AS $$`):

```sql
CREATE FUNCTION my_function(p_user_id UUID, ...)
RETURNS TABLE (
  id UUID,
  user_id UUID,
  name TEXT
) AS $$
#variable_conflict use_column
DECLARE
  ...
BEGIN
  -- Now "user_id" always refers to TABLE COLUMNS, not the RETURNS TABLE variable
  -- Use p_user_id (parameter) when you need the input value
  INSERT INTO my_table (user_id, name) VALUES (p_user_id, p_name);

  RETURN QUERY
  SELECT t.id, t.user_id, t.name
  FROM my_table t
  WHERE t.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;
```

### Critical: DROP Before CREATE When Changing Return Type

If you previously tried renaming RETURNS TABLE columns (e.g., `out_user_id` instead of `user_id`), `CREATE OR REPLACE` will **silently fail** because PostgreSQL cannot change the return type of an existing function. You MUST:

```sql
-- Step 1: DROP the old version (with exact parameter types)
DROP FUNCTION IF EXISTS public.my_function(uuid, text, text, date, text);

-- Step 2: CREATE the new version
CREATE FUNCTION my_function(...) ...
```

To find the exact signature for DROP:
```sql
SELECT p.oid, pg_get_function_identity_arguments(p.oid)
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE p.proname = 'my_function' AND n.nspname = 'public';
```

### PostgREST Cache Reload

After any function changes, reload PostgREST's schema cache:
```sql
NOTIFY pgrst, 'reload schema';
```

Without this, Supabase will keep calling the old cached version.

---

## Complete Working Example

```sql
DROP FUNCTION IF EXISTS public.save_encrypted_profile(uuid, text, text, text, date, text, text, text, text, text, text, text, date, text);

CREATE FUNCTION save_encrypted_profile(
  p_user_id UUID,
  p_full_name TEXT,
  p_email TEXT,
  p_dek_base64 TEXT
)
RETURNS TABLE (
  id UUID,
  user_id UUID,
  full_name_encrypted TEXT,
  email_encrypted TEXT
) AS $$
#variable_conflict use_column
DECLARE
  v_dek BYTEA;
BEGIN
  -- "user_id" now always means the TABLE column, not the RETURNS TABLE variable
  -- Use "p_user_id" for the parameter value

  v_dek := decode(p_dek_base64, 'base64');

  INSERT INTO public.user_profiles (user_id, full_name_encrypted, email_encrypted)
  VALUES (p_user_id, pgp_sym_encrypt(p_full_name, v_dek), pgp_sym_encrypt(p_email, v_dek))
  ON CONFLICT (user_id) DO UPDATE SET
    full_name_encrypted = EXCLUDED.full_name_encrypted,
    email_encrypted = EXCLUDED.email_encrypted;

  RETURN QUERY
  SELECT up.id, up.user_id, up.full_name_encrypted, up.email_encrypted
  FROM public.user_profiles up
  WHERE up.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

NOTIFY pgrst, 'reload schema';
```

---

## Testing the Fix

### Before (broken)
```
POST /rest/v1/rpc/save_encrypted_profile → 400 Bad Request
{code: '42702', message: 'column reference "user_id" is ambiguous'}
```

### After (working)
```
POST /rest/v1/rpc/save_encrypted_profile → 200 OK
```

### Verify function was updated
```sql
SELECT prosrc FROM pg_proc WHERE proname = 'save_encrypted_profile';
-- Should contain '#variable_conflict use_column' near the top
```

### Verify only one version exists
```sql
SELECT count(*) FROM pg_proc WHERE proname = 'save_encrypted_profile';
-- Should return 1 (not multiple overloads)
```

---

## Prevention

1. **Always use `#variable_conflict use_column`** in any function with `RETURNS TABLE`
2. **Prefix all parameters with `p_`** to distinguish from column names
3. **Use table aliases** (`up.`, `t.`) in all SELECT/WHERE clauses for clarity
4. **Always DROP before CREATE** when changing RETURNS TABLE definitions
5. **Always run `NOTIFY pgrst, 'reload schema'`** after function changes in Supabase

---

## Common Mistakes to Avoid

- Thinking table aliases alone fix it — they help SELECT but not INSERT/ON CONFLICT
- Using `CREATE OR REPLACE` after changing return column names — silently fails
- Forgetting `NOTIFY pgrst, 'reload schema'` — PostgREST serves stale function
- Assuming the function was updated because the SQL "ran successfully" — check with `prosrc`

---

## Related Patterns

- PostgreSQL docs: [PL/pgSQL Variable Substitution](https://www.postgresql.org/docs/current/plpgsql-implementation.html#PLPGSQL-VAR-SUBST)
- Supabase docs: [Database Functions](https://supabase.com/docs/guides/database/functions)

## Difficulty Level

⭐⭐⭐ (3/5) — Easy fix once you know it, but the debugging path is deceptive. Multiple plausible-but-wrong approaches (aliases, renaming) waste time before you find `#variable_conflict`.

---

**Author Notes:**
This cost ~3 hours across multiple attempts. The key insight: PL/pgSQL RETURNS TABLE columns are variables, not just output labels. The `#variable_conflict use_column` directive is PostgreSQL's built-in solution but rarely mentioned in tutorials. Always check `prosrc` to verify the function body was actually updated.
