---
description: Autonomous Resurrection Mode — reverse-engineer intent from messy code, then rebuild clean from scratch
argument-hint: "--source <path> [--target <path>] [--migrate] [--dry-run] [--focus <subsystem>]"
---

# /fire-resurrect

> Burn the Frankenstein. Rise production-ready. Reverse-engineer INTENT from messy code, ask clarifying questions, then rebuild clean in a new folder.

---

## Purpose

Take a messy "vibe coded" project and autonomously rebuild it into a clean, production-quality application. The source folder is **never modified** — the rebuild happens in a new target folder using the full Dominion Flow pipeline.

**What makes this different from refactoring:** Refactoring improves code incrementally. Resurrection Mode burns the old code entirely and rebuilds from extracted INTENT. The result carries the knowledge but none of the accidental complexity.

> **Reference:** @skills-library/_general/methodology/PHOENIX_REBUILD_METHODOLOGY.md

**Core pipeline:**
```
AUTOPSY → DATABASE → INTENT → CLARIFY → VISION → REBUILD → COMPARISON
```

---

## Arguments

```yaml
arguments:
  --source:
    type: path
    required: true
    description: "Path to the messy source project"
    example: "/fire-resurrect --source C:/Projects/my-app"

  --target:
    type: path
    required: false
    default: "{source}-phoenix"
    description: "Path for the clean rebuild output"
    example: "/fire-resurrect --source ./app --target ./app-v2"

  --migrate:
    type: boolean
    default: false
    description: "Enable stack migration mode (propose alternative tech stacks)"

  --dry-run:
    type: boolean
    default: false
    description: "Run Phases 1-4 only (autopsy + database + intent + clarify). No rebuild."

  --focus:
    type: string
    required: false
    description: "Limit analysis to a specific subsystem"
    example: "/fire-resurrect --source ./app --focus auth"

  --db-strategy:
    type: string
    required: false
    default: "auto"
    description: "Database continuity strategy: 'auto' (detect best), 'reuse' (point to existing), 'clone' (dump+restore), 'fresh' (new empty DB with migrations only), 'skip' (no database)"
    example: "/fire-resurrect --source ./app --db-strategy clone"
```

---

## Process

### Step 0: Path Verification Gate (MANDATORY)

```
Validate ALL paths before any work:

  1. --source path EXISTS and is a directory
  2. --source contains code files (not empty)
  3. --target path does NOT exist (prevent overwrite)
  4. --source ≠ --target (prevent self-overwrite)
  5. --source is not inside --target or vice versa
  6. Working directory matches expected project context

IF any check fails:
  Display error with specific violation
  STOP — do not proceed

SAFETY RULE: Source folder is READ-ONLY for the entire pipeline.
  - Autopsy documents write to {source}/.phoenix/ (metadata only)
  - All code writes go to {target}/
  - No file in {source}/ outside .phoenix/ is ever modified
```

### Step 1: Display Resurrection Banner

```
+--------------------------------------------------------------+
| RESURRECTION MODE                                                |
+--------------------------------------------------------------+
|                                                                |
|  Source: {source_path}                                         |
|  Target: {target_path}                                         |
|  Mode: {same-stack | migration}                                |
|  Focus: {all | subsystem}                                      |
|                                                                |
|  Pipeline:                                                     |
|    Phase 1: AUTOPSY    — Map the mess                         |
|    Phase 2: DATABASE   — Discover, backup, migrate data        |
|    Phase 3: INTENT     — Extract what it was trying to do      |
|    Phase 4: CLARIFY    — Ask user about ambiguities            |
|    Phase 5: VISION     — Design the clean architecture         |
|    Phase 6: REBUILD    — Build it right                        |
|    Phase 7: COMPARISON — Prove it's better                     |
|                                                                |
|  Safety: Source is READ-ONLY. All writes go to target.         |
|                                                                |
+--------------------------------------------------------------+
```

IF `--dry-run`:
```
DRY RUN — will execute Phases 1-4 only (Autopsy + Database + Intent + Clarify).
No rebuild will occur. Remove --dry-run to execute full pipeline.
```

---

### Phase 1: AUTOPSY — Map the Mess

> Understand the source codebase structure, stack, and problems.

```
Create directory: {source}/.phoenix/autopsy/

Reuse /fire-map-codebase infrastructure:
  Spawn 5 parallel mapper agents targeting {source}/:

  Agent 1 (tech):
    Focus: Technology stack, frameworks, libraries, versions
    Output: {source}/.phoenix/autopsy/STACK.md

  Agent 2 (arch):
    Focus: Architecture patterns, data flow, entry points
    Output: {source}/.phoenix/autopsy/ARCHITECTURE.md

  Agent 3 (quality):
    Focus: Code quality, anti-patterns, test coverage, error handling
    Output: {source}/.phoenix/autopsy/CONCERNS.md

  Agent 4 (concerns):
    Focus: External integrations, APIs, services, databases
    Output: {source}/.phoenix/autopsy/INTEGRATIONS.md

  Agent 5 (database):
    Focus: Database discovery — connection strings, schema, ORM, migrations
    Output: {source}/.phoenix/autopsy/DATABASE.md
    Process:
      1. Find connection strings:
         - .env, .env.local, .env.example, .env.production
         - config/database.*, prisma/schema.prisma, knexfile.*
         - docker-compose.yml (db service definitions)
         - settings.py (Django), application.properties (Spring)
      2. Identify database type: PostgreSQL, MySQL, SQLite, MongoDB, Supabase
      3. Find ORM/query layer: Prisma, Knex, Sequelize, TypeORM, Drizzle, raw SQL
      4. Find migration files: prisma/migrations/, migrations/, db/migrate/
      5. Find seed files: seeds/, prisma/seed.ts, db/seeds/
      6. Extract schema: models, tables, relationships, indexes
      7. Check for Docker DB services (volumes, ports, named databases)
      8. Identify data volume: are there uploads/media tied to DB records?
      9. Flag credentials (DO NOT log actual passwords — note their location only)

    DATABASE.md structure:
      - Database Type: {postgres|mysql|sqlite|mongo|supabase}
      - Connection Source: {env var name, config file path}
      - ORM/Query Layer: {prisma|knex|sequelize|typeorm|drizzle|raw}
      - Migration System: {prisma migrate|knex migrate|custom|none}
      - Migration Count: {N} migration files found
      - Seed Files: {list or "none"}
      - Schema Summary: {N} tables, {N} relationships
      - Docker DB: {yes/no, service name, volume name}
      - Data Volume Estimate: {small (<1GB) | medium (1-10GB) | large (>10GB)}
      - Media/Upload Coupling: {yes/no — files on disk referenced by DB records}
      - Credential Locations: {list of files containing DB credentials}
      - Recommended Strategy: {reuse | clone | fresh} with reasoning

Additionally, the orchestrator produces:

  {source}/.phoenix/autopsy/STRUCTURE.md:
    - Full directory tree (2 levels deep)
    - Entry point files identified
    - Config files listed

  {source}/.phoenix/autopsy/SOURCE-METRICS.md:
    - Total files by extension
    - LOC per file (sorted descending)
    - Dependency list from package.json / requirements.txt / etc.
    - Largest files flagged (>300 LOC)

  IF git history available:
    {source}/.phoenix/autopsy/GIT-HISTORY.md:
      - Last 20 commits with messages
      - Most-changed files (hotspots)
      - Contributors
```

**Completion gate:** All 8 autopsy documents exist and are non-empty (STACK, ARCHITECTURE, CONCERNS, INTEGRATIONS, DATABASE, STRUCTURE, SOURCE-METRICS, GIT-HISTORY).

---

### Phase 2: DATABASE CONTINUITY — Preserve the Data

> The database is often more valuable than the code. This phase ensures data survives the resurrection.

```
Read {source}/.phoenix/autopsy/DATABASE.md

IF database type is "none" or "skip" or --db-strategy == "skip":
  Display: "No database detected (or --db-strategy skip). Skipping Phase 2."
  GOTO Phase 3

// ── STRATEGY SELECTION ──

IF --db-strategy == "auto":
  Select strategy based on DATABASE.md findings:

    IF SQLite:
      strategy = "clone"  // Just copy the .db file
      reason = "SQLite is a single file — safest to copy"

    IF Docker DB with named volume:
      strategy = "reuse"  // Point new app at same Docker volume
      reason = "Docker volume persists independently of app folder"

    IF cloud/managed DB (Supabase, RDS, PlanetScale):
      strategy = "reuse"  // Same connection string, different app folder
      reason = "Managed DB is external — just update connection string"

    IF local PostgreSQL/MySQL with data:
      strategy = "clone"  // pg_dump/mysqldump → restore into new DB
      reason = "Local DB data must be preserved in new environment"

    IF no data found (empty DB or only migrations):
      strategy = "fresh"  // Run migrations to create clean schema
      reason = "No existing data to preserve — fresh schema is cleanest"

ELSE:
  strategy = --db-strategy value

// ── PRESENT STRATEGY TO USER ──

Display:
  "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  " DATABASE CONTINUITY — Strategy: {strategy}"
  "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  "  Database Type:    {type}"
  "  Current Location: {connection info — host:port/dbname, NOT password}"
  "  Data Volume:      {small|medium|large}"
  "  Migration System: {orm/tool}"
  "  Strategy:         {strategy} — {reason}"
  "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

Use AskUserQuestion:
  header: "Database Strategy"
  question: "Proceed with '{strategy}' strategy? Or choose different."
  options:
    - "Yes, proceed with {strategy}"
    - "Use 'reuse' — point new app at existing DB (zero risk)"
    - "Use 'clone' — dump + restore into new DB (data preserved, isolated)"
    - "Use 'fresh' — empty DB with migrations only (lose existing data)"
    - "Use 'skip' — handle database manually later"

// ── EXECUTE STRATEGY ──

IF strategy == "reuse":
  // Safest — no data movement at all
  1. Copy .env / .env.local from {source} to {target} (DB credentials only)
     OR: Create {target}/.env with same DATABASE_URL / DB_HOST / DB_* vars
  2. Verify connection: test that {target} can reach the database
  3. Write {source}/.phoenix/DATABASE-PLAN.md:
     - Strategy: reuse
     - Connection: {sanitized connection info}
     - Risk: LOW — no data movement
     - Rollback: N/A — source app still works unchanged
  4. IF migration system exists:
     Note: "Run migrations after rebuild to apply any schema changes"

IF strategy == "clone":
  // Safe — old DB untouched, new DB gets a copy
  1. BACKUP FIRST (non-negotiable):

     IF PostgreSQL:
       pg_dump --format=custom --file={source}/.phoenix/db-backup.dump {db_name}
       // Custom format: compressed, parallel restore, selective restore

     IF MySQL:
       mysqldump --single-transaction --routines --triggers \
         {db_name} > {source}/.phoenix/db-backup.sql
       // --single-transaction: consistent snapshot without locking

     IF SQLite:
       cp {source}/{db_file} {source}/.phoenix/db-backup.sqlite
       // Literal file copy — SQLite is a single file

     IF Supabase/managed:
       Use platform CLI: supabase db dump > {source}/.phoenix/db-backup.sql
       // Or pg_dump with the Supabase connection string

  2. CREATE NEW DATABASE:
     New DB name: {original_name}_phoenix (or {original_name}_v2)
     - PostgreSQL: createdb {new_name}
     - MySQL: CREATE DATABASE {new_name}
     - SQLite: new file at {target}/{db_file}

  3. RESTORE:
     IF PostgreSQL:
       pg_restore --dbname={new_name} --jobs=4 {source}/.phoenix/db-backup.dump
       // --jobs=4: parallel restore for speed

     IF MySQL:
       mysql {new_name} < {source}/.phoenix/db-backup.sql

     IF SQLite:
       cp {source}/.phoenix/db-backup.sqlite {target}/{db_file}

  4. UPDATE CONNECTION STRING:
     Create {target}/.env with new database name/path
     Update DATABASE_URL or DB_NAME to point to {new_name}

  5. VERIFY:
     - Connect to new DB
     - Count tables (should match source)
     - Count rows in 3 largest tables (should match source)

  6. COPY UPLOADS/MEDIA (if coupled):
     IF DATABASE.md shows media coupling:
       cp -r {source}/uploads/ {target}/uploads/
       // Or: cp -r {source}/public/uploads/ {target}/public/uploads/

  7. Write {source}/.phoenix/DATABASE-PLAN.md:
     - Strategy: clone
     - Source DB: {original} (UNTOUCHED)
     - Target DB: {new_name}
     - Backup: {source}/.phoenix/db-backup.{ext}
     - Tables: {N} cloned
     - Rows verified: {table1}: {N}, {table2}: {N}, {table3}: {N}
     - Media copied: {yes/no}
     - Risk: LOW — source DB untouched, backup exists
     - Rollback: Drop {new_name}, source still works

IF strategy == "fresh":
  // Clean start — only schema, no data
  1. CREATE NEW DATABASE (same as clone step 2)

  2. RUN MIGRATIONS:
     IF Prisma: npx prisma migrate deploy
     IF Knex: npx knex migrate:latest
     IF Sequelize: npx sequelize-cli db:migrate
     IF Django: python manage.py migrate
     IF Rails: rails db:migrate
     IF Custom: run migration files in order

  3. OPTIONALLY RUN SEEDS:
     IF seed files found in DATABASE.md:
       Ask user: "Run seed data? This populates the DB with starter data."
       IF yes: run seed command

  4. UPDATE CONNECTION STRING (same as clone step 4)

  5. Write {source}/.phoenix/DATABASE-PLAN.md:
     - Strategy: fresh
     - Target DB: {new_name}
     - Migrations applied: {N}
     - Seeds run: {yes/no}
     - Risk: NONE — no existing data involved
     - Note: Old data is NOT migrated. Source DB untouched.
```

**Safety rules for Phase 2:**
```
NEVER DISABLED:
  1. Source database is NEVER modified (read-only: dump/backup only)
  2. Backup is created BEFORE any restore operation
  3. Credentials are NEVER logged to autopsy documents (paths only)
  4. User confirms strategy before execution
  5. Rollback path is documented in DATABASE-PLAN.md
  6. Connection test verifies new DB works before proceeding
```

**Completion gate:** DATABASE-PLAN.md exists with strategy, connection info, and verification results. If strategy is "clone", backup file exists and row counts match.

---

### Phase 3: INTENT EXTRACTION — What Was It Trying to Do?

> **Reference:** @agents/fire-resurrection-analyst.md

```
Spawn 2 fire-resurrection-analyst instances:

  Instance 1 — Feature Analyst:
    Input: All autopsy documents + source code access
    Process: Steps 1-5 from fire-resurrection-analyst.md
    Output: {source}/.phoenix/INTENT.md
      - Project-level intent
      - Technology stack table
      - Feature inventory (per-feature: intent, uniqueness, quality,
        classification, confidence, edge cases, dependencies)
      - Data model intent
      - Business rules catalog
      - Accidental vs essential complexity
      - Items needing clarification

  Instance 2 — Architecture Analyst:
    Input: All autopsy documents + source code access
    Process: Step 6 from fire-resurrection-analyst.md
    Output: {source}/.phoenix/INTENT-GRAPH.md
      - Code → Intent → Clean mapping for all major features
      - Anti-pattern replacement map
      - Current vs target architecture
      - Migration notes
```

**Honesty Protocol:** Both instances apply the Three Questions before analysis. LOW confidence items are flagged, not fabricated.

**Completion gate:** Both INTENT.md and INTENT-GRAPH.md exist with non-empty feature inventories.

---

### Phase 4: CLARIFICATION — Resolve Ambiguities

```
Read {source}/.phoenix/INTENT.md

Collect items needing clarification:
  1. Features with confidence: LOW
  2. Features with classification: UNKNOWN
  3. Edge cases with uncertain KEEP/KILL
  4. Items in the "Items Needing Clarification" section

Additionally, ask:
  "Which features do you NOT want in the rebuild?"
  "Are there any new features or changes you want added?"

Batch questions into rounds (max 3 rounds, 3-4 questions each):

  Round 1: Critical ambiguities (HIGH uniqueness features with LOW confidence)
  Round 2: Feature scope (what to keep, what to drop, what to add)
  Round 3: Remaining clarifications (MEDIUM uniqueness features)

Use AskUserQuestion for each round.

After each round:
  Update {source}/.phoenix/INTENT.md with answers
  Mark clarified items with confidence: HIGH (CLARIFIED)

IF --focus specified:
  Only ask about features in the focused subsystem
  Mark out-of-focus features as "DEFERRED — out of scope for this rebuild"
```

**Completion gate:** No HIGH-uniqueness features remain at confidence: LOW.

---

### Phase 5: VISION — Design the Clean Architecture

```
IF --migrate:
  Spawn fire-vision-architect (if available) with:
    Input: INTENT.md, INTENT-GRAPH.md
    Task: Propose 2-3 technology stack alternatives
    Output: {target}/.planning/VISION.md with stack branches

  Present branches to user via AskUserQuestion:
    "Which technology stack for the rebuild?"
    Options: [branch summaries with trade-offs]

ELSE (same-stack rebuild — default):
  Auto-generate {target}/.planning/VISION.md:
    - Same technology stack as source (from STACK.md)
    - Clean architecture based on INTENT-GRAPH.md target architecture
    - Phase breakdown derived from INTENT.md feature inventory

Phase breakdown strategy (from PHOENIX_REBUILD_METHODOLOGY):
  Phase 1: FOUNDATION
    - Project scaffold, config, types/interfaces, database schema
    - Environment setup, CI/CD skeleton
  Phase 2: CORE
    - Features with uniqueness CRITICAL and HIGH
    - Ordered by dependency (foundations first)
  Phase 3: SUPPORT
    - Features with uniqueness MEDIUM
    - Ordered by dependency on CORE features
  Phase 4: STANDARD
    - Features with uniqueness LOW and BOILERPLATE
    - Often auto-generated or minimal effort
  Phase 5: INTEGRATION
    - Wire everything together
    - Cross-module flows, API contracts
  Phase 6: HARDENING
    - Error handling, logging, security, edge cases
    - All "KEEP" edge cases from INTENT.md
  Phase 7: TESTING
    - Tests written from INTENT.md assertions
    - Feature parity verification
  Phase 8: DOCUMENTATION
    - README, API docs, deployment guide

Write {target}/.planning/VISION.md with:
  - Project metadata (name, description, stack)
  - Architecture description
  - Phase list with descriptions
  - Success criteria per phase
  - Resurrection verification checks (PX-1 through PX-6)
  - Database continuity strategy from DATABASE-PLAN.md
```

**Initialize target project:**
```
Create {target}/ directory
Create {target}/.planning/ structure:
  .planning/
    VISION.md (just created)
    CONSCIENCE.md (initialized empty)
    MEMORY.md (populated from INTENT.md context)
    phases/ (empty — fire-2-plan creates phase dirs)
```

**Completion gate:** VISION.md exists with phases. Target directory initialized.

---

### Phase 6: REBUILD — Build It Right

> Standard Dominion Flow pipeline, with INTENT.md as the requirements source.

```
FOR each phase in VISION.md (Phase 1 through Phase 8):

  Display:
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    " RESURRECTION MODE: Phase {N} — {phase_name}"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  Working directory: {target}/

  // ── PLAN ──
  Run /fire-2-plan {N}
    Planner reads INTENT.md as requirements source (via MEMORY.md reference)
    Planner reads INTENT-GRAPH.md for clean implementation guidance
    BLUEPRINT frontmatter includes:
      phoenix_source: "{source_path}"
      phoenix_intent: "{source}/.phoenix/INTENT.md"
      phoenix_checks: [PX-1, PX-2, PX-3, PX-4, PX-5, PX-6]
      scope_manifest:
        read_allowed: ["{source}/"] # read-only reference
        write_allowed: ["{target}/"]
        forbidden: ["modify {source}/ files"]

  // ── EXECUTE ──
  Run /fire-3-execute {N} --auto-continue
    Executor follows BLUEPRINT tasks
    Source folder referenced as READ-ONLY for code patterns
    All writes go to {target}/

  // ── VERIFY ──
  Run /fire-4-verify {N}
    Standard verification PLUS Resurrection-specific checks:

    PX-1: Feature Parity (weight: 28%)
      FOR each feature in INTENT.md:
        Check: is it implemented in {target}/ OR explicitly marked as dropped?
      Score: implemented_count / total_features * 100

    PX-2: Edge Case Coverage (weight: 22%)
      FOR each edge case marked "KEEP" in INTENT.md:
        Check: is it handled in {target}/ code?
      Score: handled_count / keep_count * 100

    PX-3: Dependency Compatibility (weight: 18%)
      FOR each external integration in INTEGRATIONS.md:
        Check: is the connection configured in {target}/?
      Score: connected_count / total_integrations * 100

    PX-4: Accidental Complexity Removal (weight: 12%)
      FOR each anti-pattern in INTENT-GRAPH.md:
        Check: is the anti-pattern ABSENT from {target}/?
      Score: absent_count / total_antipatterns * 100

    PX-5: Architecture Improvement (weight: 8%)
      Compare: target file structure vs source
      Check: smaller avg file size, proper separation, consistent naming
      Score: qualitative assessment 0-100

    PX-6: Database Continuity (weight: 12%)
      Read DATABASE-PLAN.md:
      IF strategy == "skip": Score = N/A (remove from weighting)
      IF strategy == "reuse":
        Check: target .env has correct DATABASE_URL/DB_* vars
        Check: target app can connect to database
        Score: connected ? 100 : 0
      IF strategy == "clone":
        Check: backup file exists at {source}/.phoenix/db-backup.*
        Check: new DB exists and has same table count as source
        Check: row counts match for 3 largest tables
        Check: target .env points to new DB
        Check: media/uploads copied if coupled
        Score: (checks_passed / total_checks) * 100
      IF strategy == "fresh":
        Check: new DB exists
        Check: all migrations applied successfully
        Check: target .env points to new DB
        Score: (checks_passed / total_checks) * 100

    Resurrection Score = (PX-1 * 0.28) + (PX-2 * 0.22) + (PX-3 * 0.18)
                  + (PX-4 * 0.12) + (PX-5 * 0.08) + (PX-6 * 0.12)
    // If PX-6 is N/A (skipped), redistribute its 12% equally to PX-1 through PX-5

  // ── EVALUATE ──
  IF verifier_verdict == APPROVED or CONDITIONAL:
    Advance to next phase
    git add -A && git commit -m "phoenix: Phase {N} - {phase_name} complete"

  ELSE (REJECTED):
    attempt += 1
    IF attempt < 3:
      Re-plan with --gaps flag, re-execute
    ELSE:
      Display blocker, STOP with escalation options
```

**Safety during rebuild:**
```
ENFORCED throughout Phase 6:
  - Source folder is READ-ONLY (scope manifest forbidden list)
  - Circuit breaker active (CIRCUIT_BREAKER_INTELLIGENCE thresholds)
  - HAC enforcement active
  - Path verification on every phase
  - Kill conditions checked before retries
```

**Completion gate:** All rebuild phases reach APPROVED or CONDITIONAL verdict.

---

### Phase 7: COMPARISON — Prove It's Better

> **Reference:** @templates/phoenix-comparison.md

```
Gather metrics from both projects:

  Source metrics:
    - Total files, LOC, avg/max file size
    - Dependency count (from package.json / requirements.txt)
    - Test file count, coverage estimate
    - Anti-pattern count (from INTENT-GRAPH.md)

  Target metrics:
    - Same measurements from {target}/
    - Resurrection verification scores (PX-1 through PX-6)

Write {target}/.planning/PHOENIX-COMPARISON.md using template:
  @templates/phoenix-comparison.md

Calculate final Resurrection Score:
  90%+ = APPROVED — Rebuild is production-ready
  75-89% = CONDITIONAL — Minor fixes needed
  <75% = REJECTED — Significant gaps, review INTENT.md coverage
```

**Display completion banner:**
```
+--------------------------------------------------------------+
| RESURRECTION MODE COMPLETE                                       |
+--------------------------------------------------------------+
|                                                                |
|  Source: {source_path}                                         |
|  Target: {target_path}                                         |
|                                                                |
|  Before → After:                                               |
|    Files:        {N} → {N} ({change})                          |
|    Lines of Code: {N} → {N} ({change})                         |
|    Dependencies:  {N} → {N} ({change})                         |
|    Test Files:    {N} → {N} ({change})                         |
|    Max File Size: {N} → {N} ({change})                         |
|                                                                |
|  Resurrection Score: {score}% — {verdict}                           |
|    PX-1 Feature Parity:      {score}%                          |
|    PX-2 Edge Case Coverage:  {score}%                          |
|    PX-3 Dependency Compat:   {score}%                          |
|    PX-4 Complexity Removal:  {score}%                          |
|    PX-5 Architecture:        {score}%                          |
|    PX-6 Database Continuity: {score}%                          |
|                                                                |
|  Reports:                                                      |
|    {source}/.phoenix/INTENT.md                                 |
|    {source}/.phoenix/INTENT-GRAPH.md                           |
|    {target}/.planning/PHOENIX-COMPARISON.md                    |
|                                                                |
+--------------------------------------------------------------+
| NEXT STEPS                                                     |
+--------------------------------------------------------------+
|                                                                |
|  /fire-dashboard              — View project status            |
|  /fire-4-verify {N}           — Detailed phase verification    |
|  /fire-resurrect --dry-run      — Re-analyze without rebuilding  |
|                                                                |
+--------------------------------------------------------------+
```

IF `--dry-run`:
```
+--------------------------------------------------------------+
| PHOENIX DRY RUN COMPLETE                                       |
+--------------------------------------------------------------+
|                                                                |
|  Analysis produced:                                            |
|    {source}/.phoenix/autopsy/ (8 documents)                    |
|    {source}/.phoenix/INTENT.md                                 |
|    {source}/.phoenix/INTENT-GRAPH.md                           |
|                                                                |
|  Features found: {N} ({N unique, {N ambiguous})                |
|  Edge cases cataloged: {N} ({N keep, {N kill})                 |
|  Anti-patterns detected: {N}                                   |
|  Clarifications resolved: {N}                                  |
|                                                                |
|  To proceed with rebuild:                                      |
|    /fire-resurrect --source {source}                             |
|                                                                |
+--------------------------------------------------------------+
```

---

## Blocker Handling

```
IF any phase fails after max attempts:

+--------------------------------------------------------------+
| RESURRECTION MODE STOPPED — BLOCKER                              |
+--------------------------------------------------------------+
|                                                                |
|  Completed phases: {list}                                      |
|  Blocked at: Rebuild Phase {N} — {name}                        |
|                                                                |
|  Blocker: {description}                                        |
|                                                                |
|  What was tried:                                               |
|    Attempt 1: {verdict} ({score}/70)                           |
|    Attempt 2: {verdict} ({score}/70)                           |
|    Attempt 3: {verdict} ({score}/70)                           |
|                                                                |
|  Options:                                                      |
|    A) /fire-debug — Investigate the blocker                   |
|    B) /fire-3-execute {N} — Manual execution                  |
|    C) /fire-resurrect --source {source} — Restart               |
|    D) /fire-dashboard — Review current state                  |
|                                                                |
+--------------------------------------------------------------+
```

---

## Safety Guarantees

```
NEVER DISABLED during Resurrection Mode:

  1. Source READ-ONLY — No file in {source}/ (except .phoenix/) is ever modified
  2. Path Verification — Source ≠ target, no nesting, paths exist
  3. Scope Manifests — Every rebuild phase has explicit read/write boundaries
  4. Circuit Breaker — CIRCUIT_BREAKER_INTELLIGENCE thresholds active
  5. HAC Enforcement — Known-bad actions blocked before execution
  6. Verification — fire-verifier + Resurrection checks (PX-1 through PX-6)
  7. Database Safety — Source database is NEVER modified (read-only dumps only)

WHAT .phoenix/ CONTAINS (only metadata written to source):
  .phoenix/
    autopsy/          — 8 analysis documents (stack, arch, concerns, database, etc.)
    DATABASE-PLAN.md  — Database continuity strategy and verification
    db-backup.*       — Database backup file (clone strategy only)
    INTENT.md         — Extracted feature intent
    INTENT-GRAPH.md   — Code → Intent → Clean mapping

ALL CODE writes go to {target}/ exclusively.
```

---

## Examples

```bash
# Basic same-stack rebuild
/fire-resurrect --source C:/Projects/my-messy-app

# Custom target path
/fire-resurrect --source ./old-app --target ./old-app-v2

# Analyze only (no rebuild)
/fire-resurrect --source ./app --dry-run

# Focus on auth subsystem
/fire-resurrect --source ./app --focus auth

# Stack migration (propose new tech)
/fire-resurrect --source ./express-app --migrate
```

---

## Agent & Skill References

| Component | Role in Pipeline |
|-----------|-----------------|
| **fire-resurrection-analyst** (agent) | Phase 3 — Extracts INTENT.md and INTENT-GRAPH.md |
| **fire-codebase-mapper** (agent) | Phase 1 — Reused for autopsy mapping (5 agents incl. database) |
| **fire-planner** (agent) | Phase 6 — Plans each rebuild phase from INTENT.md |
| **fire-executor** (agent) | Phase 6 — Executes rebuild tasks |
| **fire-verifier** (agent) | Phase 6 — Verifies + Resurrection checks (PX-1 to PX-6) |
| **PHOENIX_REBUILD_METHODOLOGY** (skill) | Knowledge base — intent extraction, anti-patterns, edge cases |
| **pg-to-mysql-schema-migration-methodology** (skill) | Phase 2 — Database migration patterns |
| **GOF_DESIGN_PATTERNS_FOR_AI_AGENTS** (skill) | Architecture reference for clean rebuild |
| **CIRCUIT_BREAKER_INTELLIGENCE** (skill) | Stuck-state handling during rebuild |
| **phoenix-comparison** (template) | Phase 7 — Before/after metrics report |

---

## Success Criteria

```
- [ ] Path verification gate validates source/target paths
- [ ] Source folder is never modified (except .phoenix/ metadata)
- [ ] Phase 1 produces 8 autopsy documents (incl. DATABASE.md)
- [ ] Phase 2 discovers database, selects strategy, executes backup/clone/fresh
- [ ] Phase 2 produces DATABASE-PLAN.md with strategy, rollback path, verification
- [ ] Phase 2 source database is NEVER modified (read-only dumps only)
- [ ] Phase 2 clone strategy verifies row counts match after restore
- [ ] Phase 3 produces INTENT.md + INTENT-GRAPH.md
- [ ] Phase 3 applies Honesty Protocol (LOW confidence items flagged, not fabricated)
- [ ] Phase 4 resolves ambiguities via user questions (max 3 rounds)
- [ ] Phase 5 generates VISION.md with rebuild phases
- [ ] Phase 6 runs full Dominion Flow pipeline per rebuild phase
- [ ] Phase 6 includes Resurrection verification checks (PX-1 through PX-6)
- [ ] Phase 6 PX-6 verifies database continuity per strategy
- [ ] Phase 7 produces PHOENIX-COMPARISON.md with before/after metrics
- [ ] Resurrection Score calculated: 90%+ APPROVED, 75-89% CONDITIONAL, <75% REJECTED
- [ ] --dry-run stops after Phase 4 (analysis + database discovery + intent + clarify)
- [ ] --db-strategy overrides auto-detection (reuse/clone/fresh/skip)
- [ ] --migrate presents stack alternatives in Phase 5
- [ ] --focus limits analysis to specified subsystem
- [ ] Circuit breaker, HAC, scope manifests all active during rebuild
- [ ] Blocker escalation with clear options when max attempts exceeded
```

---

*Dominion Flow v12.8 — Resurrection Mode: burn the mess, rise production-ready. Now with database continuity.*
