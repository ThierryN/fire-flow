# ES Module Seed Script Pattern for PostgreSQL

## The Problem

Creating seed scripts when project uses ES modules and PostgreSQL instead of CommonJS and MongoDB.

### Error Messages
```
SyntaxError: Cannot use import statement outside a module
Error [ERR_REQUIRE_ESM]: require() of ES Module not supported
```

---

## The Solution

### Template

```javascript
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '.env.local'), override: true });
dotenv.config({ path: path.join(__dirname, '.env') });

import sql from './config/sql.js';  // .js extension required!

async function seed() {
  try {
    await sql`INSERT INTO courses (title) VALUES (${'My Course'}) RETURNING *`;
    console.log('Seed complete!');
  } finally {
    await sql.end();
    process.exit(0);
  }
}

seed();
```

### Key Rules
- Use `import` not `require`
- Add `.js` extension to local imports
- Run from project root: `node server/seed.js`
- Close connection with `sql.end()`

## Difficulty Level
⭐⭐ (2/5)
