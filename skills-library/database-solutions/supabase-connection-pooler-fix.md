# Supabase Connection Pooler - IPv4 Fix

## Problem
VPS cannot connect to Supabase PostgreSQL database. Two errors occur:

### Error 1: IPv6 Unreachable (Direct Connection)
```
Error: connect ENETUNREACH 2600:1f18:2e13:9d18:88be:d4c9:6b70:87e9:5432
```
**Cause:** Direct connection (`db.[project].supabase.co:5432`) resolves to IPv6, but VPS has no IPv6 connectivity.

### Error 2: Connection Timeout (Transaction Pooler)
```
Error: write CONNECT_TIMEOUT aws-1-us-east-1.pooler.supabase.com:6543
```
**Cause:** Transaction pooler on port 6543 may have firewall restrictions or require special configuration.

---

## Solution: Use Session Pooler with URL-Encoded Password

### Working Connection String Format
```
postgresql://postgres.[PROJECT_REF]:[URL_ENCODED_PASSWORD]@aws-1-us-east-1.pooler.supabase.com:5432/postgres
```

### Key Points

1. **Use Session Pooler (port 5432)** - NOT transaction pooler (port 6543)
   - Session pooler: `pooler.supabase.com:5432`
   - Transaction pooler: `pooler.supabase.com:6543`

2. **URL Encode Special Characters in Password**
   - `*` → `%2A`
   - `@` → `%40`
   - `/` → `%2F`
   - `&` → `%26`
   - `#` → `%23`

   Example: `Jubileess_*7*` → `Jubileess_%2A7%2A`

3. **Username Format for Pooler**
   - Direct: `postgres`
   - Pooler: `postgres.[PROJECT_REF]`

---

## Connection String Comparison

### Direct Connection (IPv6 issues)
```
postgresql://postgres:PASSWORD@db.[PROJECT].supabase.co:5432/postgres
```

### Transaction Pooler (may timeout)
```
postgresql://postgres.[PROJECT]:PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

### Session Pooler (RECOMMENDED for VPS)
```
postgresql://postgres.[PROJECT]:URL_ENCODED_PASSWORD@aws-1-us-east-1.pooler.supabase.com:5432/postgres
```

---

## How to Find Your Pooler URL

1. Go to Supabase Dashboard
2. Click "Connect" button
3. Select "Connection String" tab
4. Change "Method" dropdown to "Session pooler"
5. Note: It says "IPv4 compatible" at the bottom

---

## Verification

After updating `.env`, restart the server and check logs:
```bash
pm2 restart all
pm2 logs lms-server --lines 20
```

**Success indicator:**
```
✅ [DATABASE] Connection successful! Supabase PostgreSQL is ready.
```

**Failure indicators:**
```
❌ [DATABASE] Failed to connect to Supabase PostgreSQL
Error: connect ENETUNREACH ...  # IPv6 issue
Error: write CONNECT_TIMEOUT ... # Pooler/firewall issue
```

---

## References
- [Supabase Connection Management](https://supabase.com/docs/guides/database/connection-management)
- [Supabase GitHub Discussion #21789](https://github.com/orgs/supabase/discussions/21789)
- [Supavisor FAQ](https://supabase.com/docs/guides/troubleshooting/supavisor-faq-YyP5tI)
