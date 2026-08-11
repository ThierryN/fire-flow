# Database Column Name Mismatch - Detection & Resolution

## The Problem

Application code was querying for a column named `active` (boolean), but the database schema actually used a `status` column (enum with values 'draft', 'active', 'inactive', 'discontinued').

### Error Message
```
Error fetching products: column products.active does not exist
{
  code: '42703',
  details: null,
  hint: null,
  message: 'column "products.active" does not exist'
}
```

### Why It Was Hard

- Error appears in browser console, not terminal (easy to miss)
- Database query syntax is correct - just wrong column name
- TypeScript types don't catch runtime query errors
- Code works in development if you never check the response
- Error only appears when component actually renders
- Multiple files may have the same mistake (composables, components, etc.)

### Impact

- Frontend components fail to load data
- Silent failures with error messages in console
- Poor user experience (empty product lists, loading states that never complete)
- Debugging requires checking browser dev tools, not just server logs

---

## The Solution

### Root Cause

**Mismatch between code assumptions and database schema:**

**Database Schema** (from migration):
```sql
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(500) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft', 'active', 'inactive', 'discontinued')),
  featured BOOLEAN DEFAULT false,
  -- ... other columns
);
```

**Code Assumption** (composable):
```typescript
// ❌ WRONG - assumes boolean `active` column
let query = supabase
  .from('products')
  .select('*')
  .eq('active', true)
```

**Why the mismatch happened:**
1. Developer assumed common pattern (boolean `active` flag)
2. Schema actually uses more flexible enum `status` column
3. No runtime validation caught the mismatch
4. TypeScript types generated from schema but not enforced on queries

### How to Fix

**Step 1: Check the actual database schema**
```bash
# View the migration file
grep -A 20 "CREATE TABLE products" supabase/migrations/*.sql
```

**Step 2: Identify the correct column name and type**
```sql
-- Found in migration:
status VARCHAR(50) NOT NULL DEFAULT 'draft'
  CHECK (status IN ('draft', 'active', 'inactive', 'discontinued'))
```

**Step 3: Update all queries to use correct column**
```typescript
// ✅ CORRECT - uses enum `status` column
let query = supabase
  .from('products')
  .select('*')
  .eq('status', 'active')  // Changed from .eq('active', true)
```

**Step 4: Search codebase for all occurrences**
```bash
# Find all instances of the wrong query
grep -r "\.eq('active'" src/
grep -r '\.eq("active"' src/
```

### Complete Fix Example

**Before (Broken):**
```typescript
// src/features/products/composables/useProducts.ts
export function useProducts(options: UseProductsOptions = {}) {
  const fetchProducts = async () => {
    try {
      let query = supabase
        .from('products')
        .select('*', { count: 'exact' })
        .eq('active', true) // ❌ Column doesn't exist!

      // ... rest of code
    }
  }
}

export function useProduct(id: string) {
  const fetchProduct = async () => {
    const { data, error: fetchError } = await supabase
      .from('products')
      .select('*')
      .eq('id', id)
      .eq('active', true)  // ❌ Column doesn't exist!
      .single()
  }
}
```

**After (Fixed):**
```typescript
// src/features/products/composables/useProducts.ts
export function useProducts(options: UseProductsOptions = {}) {
  const fetchProducts = async () => {
    try {
      let query = supabase
        .from('products')
        .select('*', { count: 'exact' })
        .eq('status', 'active') // ✅ Correct column and value!

      // ... rest of code
    }
  }
}

export function useProduct(id: string) {
  const fetchProduct = async () => {
    const { data, error: fetchError } = await supabase
      .from('products')
      .select('*')
      .eq('id', id)
      .eq('status', 'active')  // ✅ Correct column and value!
      .single()
  }
}
```

---

## Testing the Fix

### Manual Testing

1. **Open browser dev tools** (F12)
2. **Navigate to page** that uses the component
3. **Check Console tab** for errors
4. **Check Network tab** for failed API calls

### Before Fix
```
Console:
❌ Error fetching products: column products.active does not exist

Network:
Status: 400 Bad Request
Response: {"code":"42703","message":"column \"products.active\" does not exist"}
```

### After Fix
```
Console:
✅ No errors

Network:
Status: 200 OK
Response: {"data": [...products...], "count": 5}
```

### Automated Testing
```typescript
// test/composables/useProducts.test.ts
import { useProducts } from '@/features/products/composables/useProducts'

describe('useProducts', () => {
  it('should fetch active products without error', async () => {
    const { products, error, loading } = useProducts({ limit: 10 })

    // Wait for fetch to complete
    await new Promise(resolve => setTimeout(resolve, 1000))

    expect(error.value).toBeNull()
    expect(loading.value).toBe(false)
    expect(products.value).toBeInstanceOf(Array)
  })
})
```

---

## Prevention

### 1. Always Check Schema Before Writing Queries

**Read the migration file first:**
```bash
# Before writing ANY query, check the table structure
cat supabase/migrations/*_create_products_table.sql
```

**Understand the columns:**
- What columns exist?
- What are their types?
- What are the constraints?
- What are the enum values?

### 2. Use Generated TypeScript Types

```typescript
// Generate types from database
npm run db:types

// Use types in queries
import type { Database } from '@/shared/types/database.types'
type Product = Database['public']['Tables']['products']['Row']

// TypeScript will warn if you use wrong column names
// (but won't prevent runtime string errors in .eq() calls)
```

### 3. Create Query Helper Functions

```typescript
// src/features/products/lib/queries.ts
import { supabase } from '@/shared/lib/supabase'

export const productQueries = {
  /**
   * Get all active products
   * Note: Uses 'status' column, not 'active' boolean
   */
  getActive: () =>
    supabase
      .from('products')
      .select('*')
      .eq('status', 'active'),

  /**
   * Get product by ID (active only)
   */
  getById: (id: string) =>
    supabase
      .from('products')
      .select('*')
      .eq('id', id)
      .eq('status', 'active')
      .single()
}

// Usage (prevents copy-paste errors):
const { data } = await productQueries.getActive()
```

### 4. Add Schema Documentation

```typescript
// src/shared/types/database.types.ts
/**
 * Products Table Schema Reference
 *
 * Key Columns:
 * - id: UUID (primary key)
 * - name: VARCHAR(500)
 * - status: VARCHAR(50) - ENUM('draft', 'active', 'inactive', 'discontinued')
 *   ⚠️ NOT a boolean 'active' column!
 * - featured: BOOLEAN
 *
 * Common Queries:
 * - Active products: .eq('status', 'active')
 * - Featured products: .eq('featured', true)
 */
export type Product = Database['public']['Tables']['products']['Row']
```

### 5. Lint/Validation Rules

```typescript
// eslint-plugin-supabase-queries (hypothetical)
// Warn on common column name mistakes
{
  "rules": {
    "supabase-queries/no-undefined-columns": "error",
    "supabase-queries/prefer-enum-values": "warn"
  }
}
```

---

## Related Patterns

- [Database Schema Design](./DATABASE_SCHEMA_DESIGN.md)
- [TypeScript Type Generation](./TYPESCRIPT_TYPE_GENERATION.md)
- [Query Abstraction Patterns](../patterns-standards/QUERY_ABSTRACTION.md)
- [Error Handling Best Practices](../patterns-standards/ERROR_HANDLING.md)

---

## Common Mistakes to Avoid

- ❌ **Assuming column names** - Always check the schema first
- ❌ **Copy-pasting queries** - Column names may differ across tables
- ❌ **Ignoring browser console** - Many database errors appear here, not terminal
- ❌ **Using boolean for status** - Enums are more flexible (`status` > `active`)
- ❌ **Not searching codebase** - One fix may need to be applied in multiple places
- ❌ **Trusting old code** - Schema may have changed since code was written

---

## Detection Checklist

When you see an error like "column X does not exist":

1. ✅ **Check browser dev tools console** (not just terminal)
2. ✅ **Read the full error message** (includes table and column name)
3. ✅ **Check the database schema** (migration files)
4. ✅ **Search codebase for all occurrences** (grep/search)
5. ✅ **Verify TypeScript types** (regenerate if schema changed)
6. ✅ **Test manually in browser** (verify fix works)

---

## Real-World Context

**Project:** Binamu Power E-Commerce (Vue 3 + Supabase)
**Error Occurred:** Frontend featured products section showed error
**Files Affected:** `src/features/products/composables/useProducts.ts`
**Fix Location:** Lines 39 and 133 (two query functions)
**Fix Time:** 5 minutes once error was identified
**Debugging Time:** 10 minutes (finding root cause in browser console)

**Key Lesson:** Always check browser dev tools when frontend components fail to load data. The error messages there are more specific than server logs.

---

## Resources

- [Supabase Client API Reference](https://supabase.com/docs/reference/javascript/select)
- [PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html)
- [Vue DevTools](https://devtools.vuejs.org/)
- [Chrome DevTools Network Tab](https://developer.chrome.com/docs/devtools/network/)

---

## Time to Implement

**Detection:** 10-15 minutes (if you check browser console)
**Fix:** 2-5 minutes per file
**Total:** 15-30 minutes for typical codebase

## Difficulty Level

⭐⭐ (2/5) - Easy to fix once found, but can be tricky to detect if you only check terminal output

---

**Author Notes:**

This is an extremely common mistake when:
1. Migrating from other ORMs/frameworks with different column naming conventions
2. Refactoring schema from boolean to enum (or vice versa)
3. Working with legacy code that uses different conventions
4. Multiple developers on a team with different assumptions

**Pro Tip:** When designing new tables, document the schema inline in the migration file with comments explaining non-obvious choices (like why `status` enum instead of `active` boolean).

**Prevention Gold:** Create a `SCHEMA_REFERENCE.md` file that documents all table structures and common query patterns. Update it every time you modify migrations.

---

**Date Created:** 2026-02-08
**Project:** Binamu Power E-Commerce
**Phase:** 2 (Core E-Commerce Features)
**Tech Stack:** Vue 3, Supabase, TypeScript
