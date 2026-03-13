# Prisma db push Data Loss Prevention

## Problem

Using `prisma db push` on a database with imported data (lexicons, Bible text, etc.) silently **drops and recreates tables**, wiping all imported data. This is catastrophic when tables contain thousands of rows from time-consuming import processes.

## Root Cause

`prisma db push` is designed for rapid prototyping. When schema changes are incompatible, it drops affected tables without warning. Unlike `prisma migrate dev`, it creates **no migration history** — so there's no `_prisma_migrations` table, and no way to know when data was lost.

### How to Detect It Happened

If your database has **no `_prisma_migrations` table**, `db push` was used instead of `migrate dev`:

```sql
SELECT EXISTS (
  SELECT FROM information_schema.tables
  WHERE table_name = '_prisma_migrations'
);
```

## Solution

### 1. Block `db push` in package.json

Replace the default `db:push` script with a blocker that forces developers to use the explicit `--force` variant:

```json
{
  "scripts": {
    "db:push": "echo '⛔ BLOCKED: prisma db push drops tables and destroys imported data. Use prisma migrate dev instead. If you REALLY need db push, use: npm run db:push:force' && exit 1",
    "db:push:force": "npx prisma db push",
    "db:migrate": "npx prisma migrate dev"
  }
}
```

### 2. Add a Data Health Check Script

Create a quick-check script that verifies critical tables have expected row counts:

```typescript
// server/data/check-data-counts.ts
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

interface TableCheck {
  name: string;
  count: () => Promise<number>;
  minExpected: number;
}

const checks: TableCheck[] = [
  { name: 'bible_text (KJV verses)', count: () => prisma.bibleText.count(), minExpected: 30000 },
  { name: 'hebrew_lexicons', count: () => prisma.hebrewLexicon.count(), minExpected: 9000 },
  { name: 'greek_lexicons', count: () => prisma.greekLexicon.count(), minExpected: 10000 },
];

(async () => {
  console.log('\n  Data Health Check\n  ' + '='.repeat(50));
  let allOk = true;

  for (const check of checks) {
    try {
      const count = await check.count();
      const status = count >= check.minExpected ? 'OK' : 'MISSING';
      const icon = count >= check.minExpected ? '[OK]' : '[!!]';
      if (status === 'MISSING') allOk = false;
      console.log(`  ${icon} ${check.name}: ${count.toLocaleString()} rows`);
    } catch {
      console.log(`  [!!] ${check.name}: TABLE NOT FOUND`);
      allOk = false;
    }
  }

  if (!allOk) {
    console.log('  Some data is missing! Run import scripts to restore.');
  }
  await prisma.$disconnect();
})();
```

Add to package.json:
```json
{
  "scripts": {
    "db:check-data": "npx tsx server/data/check-data-counts.ts"
  }
}
```

### 3. Document Import Restoration Commands

Always have clear import scripts ready:
```json
{
  "scripts": {
    "import-bible": "npx tsx server/data/import-bible.ts",
    "import-lexicons": "npx tsx server/data/run-lexicon-import.ts"
  }
}
```

## Key Takeaways

| Command | Safe? | Use When |
|---------|-------|----------|
| `prisma migrate dev` | Yes | Schema changes in development |
| `prisma migrate deploy` | Yes | Schema changes in production |
| `prisma db push` | **NO** | Never on databases with imported data |
| `prisma db push` | Maybe | Fresh prototyping with no real data |

## Additional Gotcha: Prisma CLI Only Reads `.env`

Prisma CLI reads **only `.env`** — not `.env.local` or `.env.production`. If your project uses `.env.local` for development, you must ensure the correct `DATABASE_URL` is in `.env` before running any Prisma CLI commands (migrations, push, generate).

## Additional Gotcha: dotenv Import Order

When using ESM modules, `PrismaClient` instantiated at the top of a module executes **before** `dotenv.config()` in the importing file, because ESM imports are hoisted. The Prisma client reads `DATABASE_URL` at instantiation time.

**Wrong:**
```typescript
// run-import.ts
import { config } from 'dotenv';
import { importData } from './import-data.js'; // PrismaClient instantiates HERE
config(); // Too late — PrismaClient already read DATABASE_URL
```

**Fix:** Set `DATABASE_URL` as a shell environment variable before running:
```bash
DATABASE_URL="postgresql://user:pass@localhost:5433/db" npx tsx run-import.ts
```

## Tech Stack
- Prisma ORM (any version)
- PostgreSQL / MySQL
- Node.js with ESM modules

## Tags
`prisma` `data-loss` `migration` `db-push` `postgresql` `dotenv` `esm`
