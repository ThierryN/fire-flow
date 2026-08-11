# PostgreSQL License Table Design - Best Practices & Patterns

## The Problem

Designing a software licensing system database that supports:
- License key generation and validation
- Multi-site activation tracking
- Tier-based feature limits
- Payment tracking
- Audit trail

### Why It Was Hard

- Many design decisions with performance implications
- Need to handle case-insensitive domain matching
- Activation counts must stay synchronized
- Money storage has precision/rounding issues
- Foreign key types must match referenced tables

### Impact

Poor database design leads to:
- Race conditions with activation counting
- Case-sensitivity bugs with domain matching
- Rounding errors with money calculations
- Performance issues with missing indexes
- Type mismatches breaking queries

---

## The Solution

### Key Design Principles Applied

1. **Match FK types to referenced tables** - Use UUID if profiles/orders use UUID
2. **Use ENUM for constrained values** - Prevents invalid data
3. **Store money as integer cents** - Avoids floating-point precision issues
4. **Use functional indexes for case-insensitivity** - `lower(domain)`
5. **Auto-sync counts via triggers** - Prevents drift
6. **Row-level locking in triggers** - Prevents race conditions

---

## Complete Migration Example

```sql
-- =====================================================
-- Migration: Create Licenses Table (Best Practices)
-- =====================================================

-- Create ENUM types if they don't exist
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'license_tier') THEN
    CREATE TYPE license_tier AS ENUM ('trial', 'pro', 'enterprise');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'license_status') THEN
    CREATE TYPE license_status AS ENUM ('pending', 'active', 'expired', 'revoked', 'suspended');
  END IF;
END$$ LANGUAGE plpgsql;

-- Create licenses table
CREATE TABLE IF NOT EXISTS licenses (
  -- UUID matches profiles/orders/products tables
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  license_key text NOT NULL UNIQUE,

  -- ENUM constrains valid values
  tier license_tier NOT NULL DEFAULT 'trial',
  status license_status NOT NULL DEFAULT 'pending',

  -- FK types match referenced tables (uuid)
  user_id uuid REFERENCES profiles(id) ON DELETE SET NULL,
  order_id uuid REFERENCES orders(id) ON DELETE SET NULL,
  product_id uuid REFERENCES products(id) ON DELETE SET NULL,

  -- Denormalized for audit trail (survives user deletion)
  user_email text,
  user_name text,
  order_number text,

  -- JSONB for flexible feature flags
  features jsonb NOT NULL DEFAULT '[]'::jsonb,

  -- License limits
  max_students integer NOT NULL DEFAULT 100,
  max_sites integer NOT NULL DEFAULT 1,
  max_courses integer NOT NULL DEFAULT 5,
  max_activations integer NOT NULL DEFAULT 1,  -- -1 = unlimited

  -- Activation tracking (count auto-synced by trigger)
  activation_count integer NOT NULL DEFAULT 0,
  activated_at timestamptz,
  activated_domain text,

  -- Validity period
  valid_from timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz,
  duration_days integer NOT NULL DEFAULT 365,

  -- Money as integer cents (avoids rounding!)
  amount_paid_cents bigint,
  currency varchar(3) NOT NULL DEFAULT 'USD',  -- varchar avoids char padding
  stripe_payment_intent_id text,

  -- Audit trail
  revoked_at timestamptz,
  revoked_reason text,
  revoked_by uuid REFERENCES profiles(id) ON DELETE SET NULL,

  -- Timestamps
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Activations table (no table-level functional constraints!)
CREATE TABLE IF NOT EXISTS license_activations (
  id bigserial PRIMARY KEY,
  license_id uuid NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,

  domain text NOT NULL,  -- Stored as-is, uniqueness via index
  site_name text,

  activated_at timestamptz NOT NULL DEFAULT now(),
  deactivated_at timestamptz,

  server_ip inet,  -- Proper IP type
  php_version text,
  node_version text,

  is_active boolean NOT NULL DEFAULT true
);

-- =====================================================
-- INDEXES
-- =====================================================

-- Case-insensitive unique constraint (NOT table constraint!)
-- WRONG: UNIQUE(license_id, lower(domain)) -- syntax error
-- RIGHT: Functional unique index
CREATE UNIQUE INDEX IF NOT EXISTS ux_license_activations_license_domain
  ON license_activations (license_id, lower(domain));

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_licenses_user_id_status
  ON licenses(user_id, status);
CREATE INDEX IF NOT EXISTS idx_licenses_tier_expires_at
  ON licenses(tier, expires_at);

-- Partial indexes (only index what you query)
CREATE INDEX IF NOT EXISTS idx_licenses_expires_at
  ON licenses(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_licenses_is_active
  ON licenses(is_active) WHERE is_active = true;

-- GIN index for JSONB queries
CREATE INDEX IF NOT EXISTS idx_licenses_features_gin
  ON licenses USING GIN (features);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION set_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_licenses_set_updated_at
BEFORE UPDATE ON licenses
FOR EACH ROW EXECUTE FUNCTION set_updated_at_column();

-- Enforce activation_count <= max_activations
CREATE OR REPLACE FUNCTION enforce_activation_count()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.max_activations != -1 AND NEW.activation_count > NEW.max_activations THEN
    RAISE EXCEPTION 'activation_count (%) cannot exceed max_activations (%)',
      NEW.activation_count, NEW.max_activations;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_licenses_check_activation_count
BEFORE INSERT OR UPDATE ON licenses
FOR EACH ROW EXECUTE FUNCTION enforce_activation_count();

-- Auto-sync activation_count (with row locking!)
CREATE OR REPLACE FUNCTION sync_license_activation_count()
RETURNS TRIGGER AS $$
DECLARE
  active_count integer;
  target_license_id uuid;
BEGIN
  target_license_id := COALESCE(NEW.license_id, OLD.license_id);

  -- Lock row to prevent race conditions
  PERFORM 1 FROM licenses WHERE id = target_license_id FOR UPDATE;

  -- Recount active activations
  SELECT COUNT(*) INTO active_count
  FROM license_activations
  WHERE license_id = target_license_id AND is_active = true;

  -- Update the count
  UPDATE licenses SET activation_count = active_count
  WHERE id = target_license_id;

  -- AFTER triggers should return NULL
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_activation_count
AFTER INSERT OR UPDATE OR DELETE ON license_activations
FOR EACH ROW EXECUTE FUNCTION sync_license_activation_count();
```

---

## Common Mistakes to Avoid

### ❌ Using SERIAL when tables use UUID
```sql
-- BAD: Type mismatch with profiles(id) which is uuid
user_id INTEGER REFERENCES profiles(id)

-- GOOD: Match the referenced type
user_id uuid REFERENCES profiles(id)
```

### ❌ Table-level functional UNIQUE constraint
```sql
-- BAD: Syntax error - can't use functions in table constraints
CONSTRAINT uq_domain UNIQUE(license_id, lower(domain))

-- GOOD: Create a functional unique index instead
CREATE UNIQUE INDEX ON table (license_id, lower(domain));
```

### ❌ Storing money as DECIMAL
```sql
-- BAD: Floating-point precision issues
amount_paid DECIMAL(10, 2)  -- $99.99 might become 99.98999...

-- GOOD: Store as integer cents
amount_paid_cents bigint    -- $99.99 = 9999 cents
```

### ❌ Using char(n) for short strings
```sql
-- BAD: char pads with spaces, causes comparison issues
currency char(3)  -- 'USD' becomes 'USD ' internally

-- GOOD: varchar doesn't pad
currency varchar(3)
```

### ❌ Manual count management
```sql
-- BAD: Counts can drift out of sync
UPDATE licenses SET activation_count = activation_count + 1

-- GOOD: Trigger auto-syncs from actual data
-- (see sync_license_activation_count trigger above)
```

### ❌ AFTER trigger returning non-NULL
```sql
-- BAD: Return value is ignored for AFTER triggers
RETURN NEW;

-- GOOD: Return NULL for AFTER triggers
RETURN NULL;
```

---

## Application Code Integration

### Converting dollars to cents
```javascript
// When storing
const amountCents = Math.round(dollarAmount * 100);

// When displaying
const displayAmount = (amountCents / 100).toFixed(2);
```

### Checking unlimited activations
```javascript
const isUnlimited = license.max_activations === -1;
const canActivate = isUnlimited ||
  license.activation_count < license.max_activations;
```

### Domain normalization
```javascript
// Always lowercase domains before storing/comparing
const normalizedDomain = domain.toLowerCase().trim();
```

---

## Testing the Design

### Verify triggers work
```sql
-- Insert an activation
INSERT INTO license_activations (license_id, domain)
VALUES ('uuid-here', 'Example.COM');

-- Check count was auto-updated
SELECT activation_count FROM licenses WHERE id = 'uuid-here';
-- Should be 1

-- Verify case-insensitive uniqueness
INSERT INTO license_activations (license_id, domain)
VALUES ('uuid-here', 'EXAMPLE.com');
-- Should fail: duplicate key violation
```

### Verify enum constraints
```sql
INSERT INTO licenses (license_key, tier)
VALUES ('TEST-KEY', 'invalid_tier');
-- Should fail: invalid input value for enum
```

---

## Prevention Checklist

Before creating any database table:

- [ ] Check FK column types match referenced tables
- [ ] Use ENUM for columns with fixed valid values
- [ ] Store money as integer cents
- [ ] Use `varchar` not `char` for short strings
- [ ] Use `inet` type for IP addresses
- [ ] Functional constraints → use indexes, not table constraints
- [ ] Add `updated_at` trigger for audit trails
- [ ] Use row locking in count-sync triggers
- [ ] Add partial indexes for common filtered queries
- [ ] Add GIN index for JSONB columns you'll query

---

## Related Patterns

- Database Migration Best Practices
- Knex.js Database Abstraction
- Stripe Webhook Integration (for payment flow)

---

## Resources

- [PostgreSQL ENUM Types](https://www.postgresql.org/docs/current/datatype-enum.html)
- [PostgreSQL Partial Indexes](https://www.postgresql.org/docs/current/indexes-partial.html)
- [PostgreSQL Triggers](https://www.postgresql.org/docs/current/plpgsql-trigger.html)
- [Money Storage Best Practices](https://stackoverflow.com/questions/224462/storing-money-in-a-decimal-column-what-precision-and-scale)

---

## Time to Implement

**Initial design:** 2-3 hours
**Applying to existing table:** 30-60 minutes
**With inspector review:** Add 30 minutes for improvements

## Difficulty Level

⭐⭐⭐ (3/5) - Requires understanding of PostgreSQL features, but patterns are reusable

---

**Author Notes:**

This pattern emerged from a Supabase database inspector review. The inspector caught several issues:
1. Table-level functional UNIQUE constraint (syntax error)
2. Missing LANGUAGE clause on DO block
3. char(3) padding issues
4. AFTER trigger return values
5. Race conditions in count sync

The key insight: **PostgreSQL has the right tool for every job** - ENUM for constrained values, functional indexes for case-insensitivity, triggers for derived data, partial indexes for selective queries. Use them!
