---
name: er-to-ddl-mapping
category: database-solutions
version: 1.0.0
contributed: 2026-03-09
contributor: fire-research
last_updated: 2026-03-09
tags: [erd, ddl, sql, schema-generation, database-design, mapping-rules]
difficulty: hard
---

# ER-to-DDL Mapping


## Problem

Converting a visual ER diagram into executable SQL DDL requires deterministic mapping rules that handle every construct in the ER model: strong entities, weak entities, all relationship cardinalities, multivalued attributes, composite attributes, derived attributes, participation constraints, and n-ary relationships. The mapping must produce correct, dialect-specific SQL for PostgreSQL, MySQL, and SQLite while preserving referential integrity through appropriate FK actions. Ad-hoc or intuition-based conversion leads to missing junction tables, incorrect cascade rules, broken composite keys, and normalization violations.

This skill encodes the complete algorithm: the 7 canonical mapping rules, the generation pipeline, multi-database type mapping, FK action selection, AI-enhanced generation patterns, and a full TypeScript implementation suitable for an ERD Creator tool.

---

## The 7 Canonical Mapping Rules

### Rule 1: Strong Entity --> Table

Every strong entity becomes its own table. This is the foundation of the entire mapping.

**Attribute handling:**
- **Simple attributes** --> columns with appropriate data types
- **Key attribute** --> PRIMARY KEY constraint
- **Composite attributes** --> flatten to leaf-level columns (do NOT create a column for the parent)
- **Multivalued attributes** --> separate table (see Rule 7)
- **Derived attributes** --> skip (compute at query time) OR use generated columns

```sql
-- Entity: Employee
-- Attributes: emp_id (key), name (composite: first, last), age (derived from dob)
CREATE TABLE employees (
    emp_id      INTEGER PRIMARY KEY,
    first_name  VARCHAR(50) NOT NULL,   -- flattened from composite "name"
    last_name   VARCHAR(50) NOT NULL,   -- flattened from composite "name"
    dob         DATE NOT NULL,
    salary      NUMERIC(10,2),
    -- age is DERIVED: skip or use generated column
    age         INTEGER GENERATED ALWAYS AS (
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, dob))
    ) STORED                            -- PostgreSQL syntax
);
```

**Edge cases:**
- Composite within composite: flatten recursively (Address.Street.Number becomes `street_number`)
- Multiple key attributes: composite PK unless one is designated as sole identifier
- No key attribute defined: error state -- every entity MUST have a key

---

### Rule 2: Weak Entity --> Table with Composite PK

A weak entity cannot exist without its identifying (owner) entity. Its table gets a composite primary key: partial key + owner's primary key. The FK to the owner MUST use `ON DELETE CASCADE`.

```sql
-- Weak Entity: Dependent (of Employee)
-- Partial key: dependent_name
-- Owner: Employee (emp_id)
CREATE TABLE dependents (
    dependent_name  VARCHAR(50) NOT NULL,
    emp_id          INTEGER NOT NULL,
    relationship    VARCHAR(20),
    birth_date      DATE,
    CONSTRAINT pk_dependent PRIMARY KEY (dependent_name, emp_id),
    CONSTRAINT fk_dependent_employee FOREIGN KEY (emp_id)
        REFERENCES employees(emp_id)
        ON DELETE CASCADE               -- MUST cascade: dependent cannot exist without employee
        ON UPDATE CASCADE
);
```

**Edge cases:**
- Weak entity owned by another weak entity: chain the PKs (all owner PKs propagate down)
- Weak entity with its own multivalued attribute: apply Rule 7 using the composite PK as FK
- Multiple identifying relationships: include all owner PKs in the composite PK

---

### Rule 3: 1:1 Relationship --> FK on Either Side

Add the PK of one entity as a FK in the other entity's table. The choice of which side gets the FK follows a priority:

1. **Total participation side** gets the FK (the entity that MUST participate -- guarantees no NULL FKs)
2. **If both total**: merge into a single table (valid when both entities always coexist)
3. **If both partial**: put FK on the side with fewer rows, or the side more frequently queried

Relationship attributes go on the table that receives the FK.

```sql
-- 1:1: Department (total) <--manages--> Employee (partial)
-- Every department MUST have a manager, but not every employee manages a department
-- FK goes on Department (total participation side)
ALTER TABLE departments
    ADD COLUMN manager_id INTEGER NOT NULL UNIQUE,  -- NOT NULL enforces total participation; UNIQUE enforces 1:1
    ADD CONSTRAINT fk_dept_manager
        FOREIGN KEY (manager_id) REFERENCES employees(emp_id)
        ON DELETE RESTRICT;                -- RESTRICT: can't delete employee who manages a department
-- Note: total participation = NOT NULL + RESTRICT. If participation is partial, use nullable + SET NULL.

-- Relationship attribute: start_date (when the employee started managing)
ALTER TABLE departments
    ADD COLUMN management_start_date DATE;
```

**Edge cases:**
- Both total with identical lifecycles: merge tables, avoid unnecessary join
- Recursive 1:1 (entity relates to itself): use a self-referencing FK with UNIQUE constraint

---

### Rule 4: 1:N Relationship --> FK on the "Many" Side

Add the PK of the "one" side as a FK column on the "many" side table. This is the most common relationship pattern in relational databases.

```sql
-- 1:N: Department (one) <--works_in--> Employee (many)
-- Each employee works in one department; a department has many employees
ALTER TABLE employees
    ADD COLUMN department_id INTEGER,
    ADD CONSTRAINT fk_emp_dept
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE SET NULL               -- employee survives if department dissolved
        ON UPDATE CASCADE;

-- Always index the FK column on the many side
CREATE INDEX idx_employees_dept ON employees(department_id);
```

**Relationship attributes** go on the many-side table:
```sql
-- If the "works_in" relationship has a "start_date" attribute:
ALTER TABLE employees ADD COLUMN dept_start_date DATE;
```

**Edge cases:**
- Total participation on many side: FK should be `NOT NULL`
- Partial participation on many side: FK is nullable
- Self-referencing 1:N (Employee supervises Employee): `supervisor_id INTEGER REFERENCES employees(emp_id)`

---

### Rule 5: M:N Relationship --> Junction/Bridge Table

Create a new junction table with a composite PK consisting of both entity PKs. This is the ONLY correct way to represent M:N in relational schema.

```sql
-- M:N: Student <--enrolls_in--> Course
-- Relationship attributes: grade, enrollment_date
CREATE TABLE enrollments (
    student_id      INTEGER NOT NULL,
    course_id       INTEGER NOT NULL,
    grade           CHAR(2),
    enrollment_date DATE DEFAULT CURRENT_DATE,
    CONSTRAINT pk_enrollment PRIMARY KEY (student_id, course_id),
    CONSTRAINT fk_enroll_student FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE,              -- if student removed, remove their enrollments
    CONSTRAINT fk_enroll_course FOREIGN KEY (course_id)
        REFERENCES courses(course_id)
        ON DELETE CASCADE               -- if course removed, remove its enrollments
);

-- Index both FK columns (composite PK covers student_id; add index for course_id lookups)
CREATE INDEX idx_enrollment_course ON enrollments(course_id);
```

**Edge cases:**
- Junction table with its own key (surrogate PK): valid when enrollments need independent identity (e.g., enrollment_id for referencing from other tables)
- M:N with attributes: attributes become columns in the junction table
- Self-referencing M:N (User friends User): junction table with two FKs to same table, add CHECK constraint to prevent self-friendship

---

### Rule 6: N-ary Relationship --> Junction Table with N FKs

For ternary and higher relationships, create a junction table with FKs to ALL participating entities. The PK composition depends on the cardinality constraints.

```sql
-- Ternary: Supplier <--supplies--> Part <--for--> Project
-- A supplier provides specific parts for specific projects
CREATE TABLE supply (
    supplier_id  INTEGER NOT NULL,
    part_id      INTEGER NOT NULL,
    project_id   INTEGER NOT NULL,
    quantity     INTEGER DEFAULT 0,
    unit_price   NUMERIC(10,2),
    CONSTRAINT pk_supply PRIMARY KEY (supplier_id, part_id, project_id),
    CONSTRAINT fk_supply_supplier FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id) ON DELETE CASCADE,
    CONSTRAINT fk_supply_part FOREIGN KEY (part_id)
        REFERENCES parts(part_id) ON DELETE CASCADE,
    CONSTRAINT fk_supply_project FOREIGN KEY (project_id)
        REFERENCES projects(project_id) ON DELETE CASCADE
);
```

**PK composition rules for n-ary:**
- If all sides are "many": PK = all N FKs (most common)
- If one side is "one": that FK is NOT part of the PK but has a UNIQUE constraint per combination of other FKs
- Analyze the functional dependencies to determine the minimal PK

---

### Rule 7: Multivalued Attribute --> Separate Table

A multivalued attribute (one that can have multiple values per entity instance) becomes its own table with a composite PK of the entity's PK + the attribute value.

```sql
-- Employee has multivalued attribute: phone_numbers
CREATE TABLE employee_phones (
    emp_id        INTEGER NOT NULL,
    phone_number  VARCHAR(20) NOT NULL,
    phone_type    VARCHAR(10) DEFAULT 'work',   -- optional classification
    CONSTRAINT pk_emp_phone PRIMARY KEY (emp_id, phone_number),
    CONSTRAINT fk_emp_phone FOREIGN KEY (emp_id)
        REFERENCES employees(emp_id)
        ON DELETE CASCADE               -- phones deleted when employee deleted
);
```

**Edge cases:**
- Multivalued composite attribute (e.g., previous_degrees with university + year + degree_name): all components become columns, composite PK includes entity PK + all components that form a unique combination
- Multivalued attribute of a weak entity: FK is the weak entity's composite PK

---

## DDL Generation Algorithm

### Full Pseudocode

```
ALGORITHM: ER-to-DDL Mapping
INPUT:  ERDModel (entities, relationships, attributes)
OUTPUT: SQL DDL string (ordered by dependency)

Phase 1: TABLE CREATION (entities)
────────────────────────────────────────────────────
for each strong_entity in model.entities where NOT weak:
    CREATE TABLE entity.name (
        for each attribute in entity.attributes:
            if attribute.type == SIMPLE:
                emit column: name, dataType, constraints
            if attribute.type == KEY:
                emit column: name, dataType, NOT NULL
                collect for PRIMARY KEY
            if attribute.type == COMPOSITE:
                recursively flatten to leaf attributes
                emit each leaf as column
            if attribute.type == DERIVED:
                if dialect supports GENERATED:
                    emit GENERATED ALWAYS AS (expression) STORED
                else:
                    skip (compute at query time)
            if attribute.type == MULTIVALUED:
                defer to Phase 5
        emit PRIMARY KEY constraint
    )

Phase 2: WEAK ENTITY TABLES
────────────────────────────────────────────────────
for each weak_entity in model.entities where IS weak:
    identify owner_entity via identifying_relationship
    CREATE TABLE weak_entity.name (
        emit weak entity's own attributes as columns
        emit owner_pk as FK column
        PRIMARY KEY (partial_key_columns, owner_pk_column)
        FOREIGN KEY (owner_pk_column) REFERENCES owner_table(owner_pk)
            ON DELETE CASCADE ON UPDATE CASCADE
    )

Phase 3: 1:1 RELATIONSHIPS
────────────────────────────────────────────────────
for each relationship where cardinality == ONE_TO_ONE:
    determine FK_side:
        if one side has total participation: FK_side = that side
        if both total: consider merging tables
        if both partial: FK_side = side with fewer expected rows
    ALTER TABLE FK_side
        ADD COLUMN other_pk as FK (with UNIQUE constraint)
        ADD relationship attributes as columns
        FOREIGN KEY REFERENCES other_table
            ON DELETE based on participation (CASCADE if total, SET NULL if partial)

Phase 4: 1:N RELATIONSHIPS
────────────────────────────────────────────────────
for each relationship where cardinality == ONE_TO_MANY:
    many_side = entity on the "many" end
    one_side  = entity on the "one" end
    ALTER TABLE many_side
        ADD COLUMN one_side_pk as FK
        ADD relationship attributes as columns
        FOREIGN KEY REFERENCES one_side_table
            ON DELETE (SET NULL if partial, RESTRICT if critical, CASCADE if dependent)
    CREATE INDEX on many_side(FK_column)

Phase 5: M:N RELATIONSHIPS
────────────────────────────────────────────────────
for each relationship where cardinality == MANY_TO_MANY:
    CREATE TABLE junction_name (
        entity_a_pk column,
        entity_b_pk column,
        relationship attribute columns,
        PRIMARY KEY (entity_a_pk, entity_b_pk),
        FOREIGN KEY (entity_a_pk) REFERENCES entity_a ON DELETE CASCADE,
        FOREIGN KEY (entity_b_pk) REFERENCES entity_b ON DELETE CASCADE
    )
    CREATE INDEX on junction_name(entity_b_pk)   -- composite PK covers entity_a_pk

Phase 6: N-ARY RELATIONSHIPS
────────────────────────────────────────────────────
for each relationship where participants.length > 2:
    CREATE TABLE junction_name (
        for each participant: emit participant_pk as FK column
        emit relationship attributes as columns
        PRIMARY KEY = determine from cardinality analysis
        for each participant: FOREIGN KEY REFERENCES participant ON DELETE CASCADE
    )

Phase 7: MULTIVALUED ATTRIBUTES
────────────────────────────────────────────────────
for each multivalued_attribute collected in Phase 1:
    CREATE TABLE entity_attribute_name (
        owner_pk column(s),
        attribute_value column(s),
        PRIMARY KEY (owner_pk, attribute_value),
        FOREIGN KEY (owner_pk) REFERENCES owner_table ON DELETE CASCADE
    )

Phase 8: DEPENDENCY ORDERING
────────────────────────────────────────────────────
topological_sort all CREATE TABLE statements by FK dependencies
emit in order: tables with no FKs first, then tables referencing those, etc.
```

---

## TypeScript Data Model

These are the type definitions for the internal ERD model that feeds the DDL generator.

```typescript
// ============================================================
// ERD Model Types — the internal representation of an ER diagram
// ============================================================

/** Supported SQL dialects for DDL generation */
type SQLDialect = 'postgresql' | 'mysql' | 'sqlite';

/** Attribute classification per ER theory */
type AttributeKind =
  | 'simple'
  | 'key'
  | 'partial_key'     // weak entity identifier
  | 'composite'
  | 'multivalued'
  | 'derived';

/** Relationship cardinality */
type Cardinality = '1:1' | '1:N' | 'M:N';

/** Participation constraint */
type Participation = 'total' | 'partial';

/** FK referential actions */
type ReferentialAction = 'CASCADE' | 'SET NULL' | 'RESTRICT' | 'SET DEFAULT' | 'NO ACTION';

// ── Attributes ──────────────────────────────────────────────

interface ERDAttribute {
  id: string;
  name: string;
  kind: AttributeKind;
  dataType: string;                    // logical type: "string", "integer", "date", etc.
  isNullable: boolean;
  defaultValue?: string;
  children?: ERDAttribute[];           // for composite attributes: leaf-level sub-attributes
  derivedExpression?: string;          // for derived attributes: the computation expression
  multivaluedType?: string;            // for multivalued: the value type (e.g., "VARCHAR(20)")
}

// ── Entities ────────────────────────────────────────────────

interface ERDEntity {
  id: string;
  name: string;
  isWeak: boolean;
  attributes: ERDAttribute[];
  /** For weak entities: the ID of the owning strong entity */
  ownerId?: string;
  /** For weak entities: the identifying relationship ID */
  identifyingRelationshipId?: string;
}

// ── Relationships ───────────────────────────────────────────

interface ERDRelationshipParticipant {
  entityId: string;
  cardinality: '1' | 'N' | 'M';
  participation: Participation;
}

interface ERDRelationship {
  id: string;
  name: string;
  participants: ERDRelationshipParticipant[];  // 2 for binary, 3+ for n-ary
  attributes: ERDAttribute[];                  // relationship can have its own attributes
  isIdentifying: boolean;                      // true for weak entity identifying relationships
}

// ── The Complete Model ──────────────────────────────────────

interface ERDModel {
  name: string;                        // database/schema name
  entities: ERDEntity[];
  relationships: ERDRelationship[];
}

// ── DDL Generation Options ──────────────────────────────────

interface DDLGeneratorOptions {
  dialect: SQLDialect;
  useNamedConstraints: boolean;        // e.g., CONSTRAINT fk_emp_dept vs inline
  includeIndexes: boolean;             // auto-create indexes on FK columns
  includeDropIfExists: boolean;        // prepend DROP TABLE IF EXISTS
  schemaName?: string;                 // e.g., "public" for PostgreSQL
  idStrategy: 'serial' | 'uuid' | 'cuid'; // primary key generation strategy
  timestampColumns: boolean;           // auto-add created_at, updated_at
}
```

---

## Multi-Database Type Mapping

### Logical-to-Physical Type Map

```typescript
const TYPE_MAP: Record<string, Record<SQLDialect, string>> = {
  // ── Identifiers ─────────────────────────────────────────
  'serial':       { postgresql: 'SERIAL',           mysql: 'INT AUTO_INCREMENT',      sqlite: 'INTEGER' },
  'bigserial':    { postgresql: 'BIGSERIAL',        mysql: 'BIGINT AUTO_INCREMENT',   sqlite: 'INTEGER' },
  'uuid':         { postgresql: 'UUID',             mysql: 'CHAR(36)',                sqlite: 'TEXT' },
  'cuid':         { postgresql: 'VARCHAR(30)',       mysql: 'VARCHAR(30)',             sqlite: 'TEXT' },

  // ── Strings ─────────────────────────────────────────────
  'varchar':      { postgresql: 'VARCHAR',          mysql: 'VARCHAR',                 sqlite: 'TEXT' },
  'text':         { postgresql: 'TEXT',             mysql: 'TEXT',                    sqlite: 'TEXT' },
  'longtext':     { postgresql: 'TEXT',             mysql: 'LONGTEXT',               sqlite: 'TEXT' },
  'char':         { postgresql: 'CHAR',             mysql: 'CHAR',                   sqlite: 'TEXT' },

  // ── Numbers ─────────────────────────────────────────────
  'integer':      { postgresql: 'INTEGER',          mysql: 'INT',                    sqlite: 'INTEGER' },
  'smallint':     { postgresql: 'SMALLINT',         mysql: 'SMALLINT',               sqlite: 'INTEGER' },
  'bigint':       { postgresql: 'BIGINT',           mysql: 'BIGINT',                 sqlite: 'INTEGER' },
  'decimal':      { postgresql: 'NUMERIC',          mysql: 'DECIMAL',                sqlite: 'REAL' },
  'float':        { postgresql: 'REAL',             mysql: 'FLOAT',                  sqlite: 'REAL' },
  'double':       { postgresql: 'DOUBLE PRECISION', mysql: 'DOUBLE',                 sqlite: 'REAL' },

  // ── Boolean ─────────────────────────────────────────────
  'boolean':      { postgresql: 'BOOLEAN',          mysql: 'TINYINT(1)',             sqlite: 'INTEGER' },

  // ── Date/Time ───────────────────────────────────────────
  'date':         { postgresql: 'DATE',             mysql: 'DATE',                   sqlite: 'TEXT' },
  'time':         { postgresql: 'TIME',             mysql: 'TIME',                   sqlite: 'TEXT' },
  'timestamp':    { postgresql: 'TIMESTAMPTZ',      mysql: 'DATETIME',               sqlite: 'TEXT' },
  'interval':     { postgresql: 'INTERVAL',         mysql: 'VARCHAR(50)',            sqlite: 'TEXT' },

  // ── JSON ────────────────────────────────────────────────
  'json':         { postgresql: 'JSONB',            mysql: 'JSON',                   sqlite: 'TEXT' },

  // ── Binary ──────────────────────────────────────────────
  'blob':         { postgresql: 'BYTEA',            mysql: 'BLOB',                   sqlite: 'BLOB' },

  // ── Enum (special handling) ─────────────────────────────
  'enum':         { postgresql: 'TEXT',             mysql: 'ENUM',                   sqlite: 'TEXT' },
  // PostgreSQL enums require CREATE TYPE; handled separately in generator
};
```

### Dialect-Specific Syntax Differences

| Feature                | PostgreSQL                     | MySQL                          | SQLite                    |
|------------------------|--------------------------------|--------------------------------|---------------------------|
| Auto-increment PK      | `SERIAL PRIMARY KEY`           | `INT PRIMARY KEY AUTO_INCREMENT` | `INTEGER PRIMARY KEY`     |
| UUID generation         | `DEFAULT gen_random_uuid()`    | `DEFAULT (UUID())`             | Application-generated     |
| Boolean literal         | `TRUE / FALSE`                 | `1 / 0`                        | `1 / 0`                   |
| Current timestamp       | `CURRENT_TIMESTAMP`            | `CURRENT_TIMESTAMP`            | `CURRENT_TIMESTAMP`       |
| Generated column        | `GENERATED ALWAYS AS (...) STORED` | `GENERATED ALWAYS AS (...) STORED` | Not supported       |
| IF NOT EXISTS           | `CREATE TABLE IF NOT EXISTS`   | `CREATE TABLE IF NOT EXISTS`   | `CREATE TABLE IF NOT EXISTS` |
| Drop + cascade          | `DROP TABLE IF EXISTS t CASCADE` | `DROP TABLE IF EXISTS t`     | `DROP TABLE IF EXISTS t`  |
| Schema qualification    | `schema.table`                 | `` `database`.`table` ``       | Not applicable            |
| ENUM type               | `CREATE TYPE ... AS ENUM`      | Inline `ENUM('a','b')`        | Use CHECK constraint      |
| Partial index           | `WHERE condition`              | Not supported (use generated column + index) | `WHERE condition` |
| Comment on column       | `COMMENT ON COLUMN ...`        | `COMMENT 'text'` inline       | Not supported             |

---

## FK Referential Actions

### Action Matrix — When to Use Each

| Action         | Behavior on Parent DELETE              | Use When                                                        |
|----------------|----------------------------------------|-----------------------------------------------------------------|
| **CASCADE**    | Delete all child rows automatically    | Weak entities, junction tables, dependent data that has no meaning without parent |
| **SET NULL**   | Set FK column to NULL                  | Optional relationships where child survives parent deletion (e.g., employee.department_id when department dissolved) |
| **RESTRICT**   | Block parent deletion if children exist | **Safe default.** Critical references where deletion should be prevented (e.g., cannot delete a customer with open orders) |
| **SET DEFAULT**| Set FK to its DEFAULT value            | Rare. When a fallback parent exists (e.g., "unassigned" category) |
| **NO ACTION**  | Like RESTRICT but deferred-checkable   | Same as RESTRICT; use when you need deferred constraint checking within a transaction |

### Decision Tree

```
Is the child entity DEPENDENT on the parent (weak entity, junction table)?
  YES --> CASCADE
  NO  --> Can the child exist without the parent?
            YES --> Is the FK nullable?
                      YES --> SET NULL
                      NO  --> RESTRICT (or add a default parent)
            NO  --> CASCADE
```

### ON UPDATE Actions

Most systems should use `ON UPDATE CASCADE` for all FKs. This handles the (rare) case where a parent PK is updated. Exception: if using immutable surrogate keys (UUID/CUID), ON UPDATE is effectively a no-op.

---

## AI-Enhanced Generation

### Text2Schema Pipeline (arXiv 2025)

Multi-agent decomposition for natural language to DDL. The key insight: breaking the NL-to-DDL task into sub-tasks with specialized agents yields significantly better schemas than single-pass generation.

```
Input: "Build a university system where students enroll in courses
        taught by professors in departments"

Agent Pipeline:
1. ENTITY EXTRACTOR
   --> Student, Course, Professor, Department

2. RELATIONSHIP CLASSIFIER
   --> Student M:N Course (enrollment)
   --> Professor 1:N Course (teaches)
   --> Department 1:N Professor (belongs_to)
   --> Department 1:N Course (offered_by)

3. ATTRIBUTE ENRICHER
   --> Student: student_id (PK), first_name, last_name, email, enrollment_date
   --> Course: course_id (PK), title, credits, max_enrollment
   --> Professor: prof_id (PK), first_name, last_name, email, hire_date
   --> Department: dept_id (PK), name, building, budget

4. CONSTRAINT INTEGRATOR
   --> enrollment junction: grade, semester (relationship attrs)
   --> email UNIQUE on Student, Professor
   --> credits CHECK (credits > 0 AND credits <= 6)

5. DDL CODE ARTICULATOR
   --> Applies the 7 mapping rules
   --> Outputs dialect-specific SQL

6. VERIFIER
   --> Checks 3NF compliance
   --> Validates FK references
   --> Confirms no orphan tables
```

### NOMAD Agent Roles (arXiv 2025)

Similar multi-agent approach but emphasizes the **articulation** step -- translating the abstract model into implementation-ready code. Key pattern: the code articulator agent receives the verified model and must produce syntactically valid, runnable DDL. The verifier then executes it against a test database to confirm.

### Prompt Template for LLM-Assisted Mapping

```
You are a database schema designer. Given the following ER model in JSON format,
generate SQL DDL for {dialect}.

Rules:
1. Strong entities become tables with their simple attributes as columns
2. Key attributes become PRIMARY KEY
3. Composite attributes are flattened to leaf columns
4. Weak entities get composite PK (partial_key + owner_pk) with ON DELETE CASCADE
5. 1:1 relationships: FK on total-participation side with UNIQUE constraint
6. 1:N relationships: FK on the many side
7. M:N relationships: junction table with composite PK
8. Multivalued attributes: separate table with composite PK

Output requirements:
- Named constraints (pk_, fk_, uq_, ck_ prefixes)
- Appropriate ON DELETE actions
- Indexes on all FK columns
- Tables ordered by dependency (no forward references)

ER Model:
{model_json}
```

---

## Implementation Architecture

### DrawDB Parser/Generator Pattern (Gold Standard)

DrawDB is the open-source reference implementation for visual ERD-to-DDL. Its architecture separates concerns cleanly:

```
Visual Editor (React Flow)
    |
    v
Internal JSON Model  <-- the canonical representation
    |
    +--> PostgreSQL Generator
    +--> MySQL Generator
    +--> SQLite Generator
    +--> SQL Server Generator
    |
    v
SQL DDL String Output

Reverse path:
SQL DDL String --> Parser --> Internal JSON Model --> Visual Editor
```

**Key pattern:** Each dialect has its own generator module that reads the same JSON model. The generators share a base class with common logic (constraint naming, dependency sorting) and override dialect-specific methods (type mapping, auto-increment syntax, enum handling).

### node-sql-parser Integration

Bidirectional SQL parsing/generation using AST:

```typescript
import { Parser } from 'node-sql-parser';

const parser = new Parser();

// DDL string --> AST (for importing existing schemas)
const ast = parser.astify('CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50));');

// AST --> DDL string (for generating from modified model)
const sql = parser.sqlify(ast);

// Supports dialect-specific parsing
const pgAst = parser.astify(ddlString, { database: 'PostgreSQL' });
const mysqlAst = parser.astify(ddlString, { database: 'MySQL' });
```

### sql-ddl-to-json-schema

For importing existing DDL into the ERD model:

```typescript
// Parse DDL into JSON Schema (ERD-friendly format)
import { Parser as DDLParser } from 'sql-ddl-to-json-schema';

const ddlParser = new DDLParser('mysql');
ddlParser.feed(existingDDL);
const jsonSchema = ddlParser.results;
// jsonSchema contains tables, columns, constraints, FKs
// Map this into the ERDModel interface for visualization
```

### ERFlow MCP Pattern

ERFlow (MCP Server) demonstrates an agent-driven approach with 25+ tools for schema manipulation:
- Natural language schema edits ("add a status column to orders")
- Checkpoint-based migration generation (diff between schema states)
- Multi-dialect export from a single canonical model

---

## Code Example: TypeScript DDL Generator

```typescript
// ============================================================
// ERD-to-DDL Generator — complete implementation
// ============================================================

/**
 * Resolves a logical data type to a dialect-specific SQL type.
 */
function resolveType(
  logicalType: string,
  dialect: SQLDialect,
  length?: number,
  precision?: number,
  scale?: number
): string {
  const base = TYPE_MAP[logicalType.toLowerCase()]?.[dialect]
    ?? TYPE_MAP['text'][dialect];   // fallback to TEXT

  // Apply length/precision modifiers
  if (length && ['varchar', 'char'].includes(logicalType.toLowerCase())) {
    return `${base}(${length})`;
  }
  if (precision && ['decimal', 'numeric'].includes(logicalType.toLowerCase())) {
    return scale ? `${base}(${precision},${scale})` : `${base}(${precision})`;
  }
  return base;
}

/**
 * Generates a constraint name following naming conventions.
 */
function constraintName(
  type: 'pk' | 'fk' | 'uq' | 'ck' | 'idx',
  tableName: string,
  columnOrDetail: string
): string {
  return `${type}_${tableName}_${columnOrDetail}`.toLowerCase();
}

/**
 * Flattens composite attributes recursively into leaf-level columns.
 */
function flattenAttributes(attrs: ERDAttribute[], prefix = ''): ERDAttribute[] {
  const result: ERDAttribute[] = [];
  for (const attr of attrs) {
    if (attr.kind === 'composite' && attr.children?.length) {
      result.push(...flattenAttributes(attr.children, `${prefix}${attr.name}_`));
    } else if (attr.kind !== 'multivalued') {
      result.push({
        ...attr,
        name: `${prefix}${attr.name}`,
      });
    }
    // multivalued attributes handled separately in Phase 7
  }
  return result;
}

/**
 * Collects all multivalued attributes from an entity (including nested in composites).
 */
function collectMultivalued(
  entity: ERDEntity
): { entityId: string; entityName: string; attr: ERDAttribute }[] {
  const results: { entityId: string; entityName: string; attr: ERDAttribute }[] = [];

  function walk(attrs: ERDAttribute[]) {
    for (const attr of attrs) {
      if (attr.kind === 'multivalued') {
        results.push({ entityId: entity.id, entityName: entity.name, attr });
      }
      if (attr.children) walk(attr.children);
    }
  }

  walk(entity.attributes);
  return results;
}

/**
 * Gets the primary key column names for an entity.
 */
function getPKColumns(entity: ERDEntity): string[] {
  return entity.attributes
    .filter(a => a.kind === 'key' || a.kind === 'partial_key')
    .map(a => a.name);
}

/**
 * Determines the appropriate ON DELETE action based on relationship context.
 */
function determineOnDelete(
  participation: Participation,
  isWeakEntityFK: boolean,
  isJunctionFK: boolean
): ReferentialAction {
  if (isWeakEntityFK || isJunctionFK) return 'CASCADE';
  if (participation === 'total') return 'RESTRICT';
  return 'SET NULL';
}

/**
 * Topologically sorts tables by FK dependencies.
 * Tables with no FK dependencies come first.
 */
function topologicalSort(
  tables: { name: string; dependsOn: string[] }[]
): string[] {
  const sorted: string[] = [];
  const visited = new Set<string>();
  const visiting = new Set<string>();
  const tableMap = new Map(tables.map(t => [t.name, t]));

  function visit(name: string) {
    if (visited.has(name)) return;
    if (visiting.has(name)) {
      // Circular dependency — emit as-is (will need ALTER TABLE for FK)
      sorted.push(name);
      visited.add(name);
      return;
    }
    visiting.add(name);
    const table = tableMap.get(name);
    if (table) {
      for (const dep of table.dependsOn) {
        if (tableMap.has(dep)) visit(dep);
      }
    }
    visiting.delete(name);
    visited.add(name);
    sorted.push(name);
  }

  for (const table of tables) {
    visit(table.name);
  }
  return sorted;
}

// ── Statement Builders ──────────────────────────────────────

interface TableStatement {
  name: string;
  sql: string;
  dependsOn: string[];
}

interface IndexStatement {
  sql: string;
}

/**
 * Main generator function: ERDModel --> SQL DDL string.
 */
function generateDDL(model: ERDModel, options: DDLGeneratorOptions): string {
  const tables: TableStatement[] = [];
  const indexes: IndexStatement[] = [];
  const entityTableMap = new Map<string, string>();  // entity.id -> table name

  // Build entity ID -> table name lookup
  for (const entity of model.entities) {
    entityTableMap.set(entity.id, entity.name.toLowerCase());
  }

  // ── Phase 1: Strong Entity Tables ─────────────────────────

  for (const entity of model.entities.filter(e => !e.isWeak)) {
    const tableName = entity.name.toLowerCase();
    const flatAttrs = flattenAttributes(entity.attributes);
    const pkCols = getPKColumns(entity);
    const columns: string[] = [];

    for (const attr of flatAttrs) {
      const colName = attr.name.toLowerCase();
      const colType = resolveType(attr.dataType, options.dialect);
      const constraints: string[] = [];

      if (attr.kind === 'key') constraints.push('NOT NULL');
      if (!attr.isNullable && attr.kind !== 'key') constraints.push('NOT NULL');
      if (attr.defaultValue) constraints.push(`DEFAULT ${attr.defaultValue}`);

      if (attr.kind === 'derived' && attr.derivedExpression) {
        if (options.dialect !== 'sqlite') {
          columns.push(
            `    ${colName} ${colType} GENERATED ALWAYS AS (${attr.derivedExpression}) STORED`
          );
        }
        // SQLite: skip derived columns
        continue;
      }

      columns.push(`    ${colName} ${colType}${constraints.length ? ' ' + constraints.join(' ') : ''}`);
    }

    // Timestamp columns
    if (options.timestampColumns) {
      const tsType = resolveType('timestamp', options.dialect);
      columns.push(`    created_at ${tsType} NOT NULL DEFAULT CURRENT_TIMESTAMP`);
      columns.push(`    updated_at ${tsType} NOT NULL DEFAULT CURRENT_TIMESTAMP`);
    }

    // PK constraint
    const pkConstraint = options.useNamedConstraints
      ? `    CONSTRAINT ${constraintName('pk', tableName, pkCols.join('_'))} PRIMARY KEY (${pkCols.join(', ')})`
      : `    PRIMARY KEY (${pkCols.join(', ')})`;

    const ddl = [
      `CREATE TABLE ${tableName} (`,
      [...columns, pkConstraint].join(',\n'),
      `);`,
    ].join('\n');

    tables.push({ name: tableName, sql: ddl, dependsOn: [] });
  }

  // ── Phase 2: Weak Entity Tables ───────────────────────────

  for (const entity of model.entities.filter(e => e.isWeak)) {
    const tableName = entity.name.toLowerCase();
    const owner = model.entities.find(e => e.id === entity.ownerId);
    if (!owner) continue;

    const ownerTable = owner.name.toLowerCase();
    const ownerPK = getPKColumns(owner);
    const partialKey = entity.attributes.filter(a => a.kind === 'partial_key').map(a => a.name);
    const flatAttrs = flattenAttributes(entity.attributes.filter(a => a.kind !== 'partial_key'));
    const columns: string[] = [];

    // Partial key columns
    for (const pk of partialKey) {
      const attr = entity.attributes.find(a => a.name === pk)!;
      columns.push(`    ${pk.toLowerCase()} ${resolveType(attr.dataType, options.dialect)} NOT NULL`);
    }

    // Owner PK as FK columns
    for (const ownerCol of ownerPK) {
      const ownerAttr = owner.attributes.find(a => a.name === ownerCol)!;
      columns.push(`    ${ownerCol.toLowerCase()} ${resolveType(ownerAttr.dataType, options.dialect)} NOT NULL`);
    }

    // Other attributes
    for (const attr of flatAttrs) {
      const colType = resolveType(attr.dataType, options.dialect);
      const nullable = attr.isNullable ? '' : ' NOT NULL';
      columns.push(`    ${attr.name.toLowerCase()} ${colType}${nullable}`);
    }

    // Composite PK
    const compositePK = [...partialKey, ...ownerPK].map(c => c.toLowerCase());
    const pkLine = options.useNamedConstraints
      ? `    CONSTRAINT ${constraintName('pk', tableName, compositePK.join('_'))} PRIMARY KEY (${compositePK.join(', ')})`
      : `    PRIMARY KEY (${compositePK.join(', ')})`;

    // FK to owner
    const fkLine = options.useNamedConstraints
      ? `    CONSTRAINT ${constraintName('fk', tableName, ownerTable)} FOREIGN KEY (${ownerPK.join(', ')}) REFERENCES ${ownerTable}(${ownerPK.join(', ')}) ON DELETE CASCADE ON UPDATE CASCADE`
      : `    FOREIGN KEY (${ownerPK.join(', ')}) REFERENCES ${ownerTable}(${ownerPK.join(', ')}) ON DELETE CASCADE ON UPDATE CASCADE`;

    const ddl = [
      `CREATE TABLE ${tableName} (`,
      [...columns, pkLine, fkLine].join(',\n'),
      `);`,
    ].join('\n');

    tables.push({ name: tableName, sql: ddl, dependsOn: [ownerTable] });
  }

  // ── Phase 3-6: Relationships ──────────────────────────────

  for (const rel of model.relationships) {
    if (rel.isIdentifying) continue;  // already handled in Phase 2

    const participants = rel.participants;

    if (participants.length === 2) {
      const [a, b] = participants;
      const cardA = a.cardinality;
      const cardB = b.cardinality;
      const entityA = model.entities.find(e => e.id === a.entityId)!;
      const entityB = model.entities.find(e => e.id === b.entityId)!;
      const tableA = entityA.name.toLowerCase();
      const tableB = entityB.name.toLowerCase();
      const pkA = getPKColumns(entityA);
      const pkB = getPKColumns(entityB);

      // ── 1:1 ──
      if (cardA === '1' && cardB === '1') {
        // FK goes on total participation side (or side A by default)
        const fkSide = b.participation === 'total' ? 'b' : 'a';
        const [fkTable, refTable, refPK] = fkSide === 'b'
          ? [tableB, tableA, pkA]
          : [tableA, tableB, pkB];
        const fkCol = `${refTable}_id`;
        const onDelete = determineOnDelete(
          fkSide === 'b' ? b.participation : a.participation, false, false
        );

        // Find the table statement and add FK column
        const tableStmt = tables.find(t => t.name === fkTable);
        if (tableStmt) {
          const fkColType = resolveType('integer', options.dialect);  // match ref PK type
          const insertBefore = ');';
          const fkLines = [
            `,\n    ${fkCol} ${fkColType} UNIQUE`,
            options.useNamedConstraints
              ? `,\n    CONSTRAINT ${constraintName('fk', fkTable, refTable)} FOREIGN KEY (${fkCol}) REFERENCES ${refTable}(${refPK.join(', ')}) ON DELETE ${onDelete}`
              : `,\n    FOREIGN KEY (${fkCol}) REFERENCES ${refTable}(${refPK.join(', ')}) ON DELETE ${onDelete}`,
          ];
          // Add relationship attributes
          for (const attr of rel.attributes) {
            fkLines.unshift(`,\n    ${attr.name.toLowerCase()} ${resolveType(attr.dataType, options.dialect)}`);
          }
          tableStmt.sql = tableStmt.sql.replace(insertBefore, fkLines.join('') + '\n' + insertBefore);
          tableStmt.dependsOn.push(refTable);
        }
      }

      // ── 1:N ──
      else if (
        (cardA === '1' && (cardB === 'N' || cardB === 'M')) ||
        ((cardA === 'N' || cardA === 'M') && cardB === '1')
      ) {
        const [oneEntity, manyEntity, manyParticipation] =
          cardA === '1'
            ? [entityA, entityB, b.participation]
            : [entityB, entityA, a.participation];
        const oneTable = oneEntity.name.toLowerCase();
        const manyTable = manyEntity.name.toLowerCase();
        const onePK = getPKColumns(oneEntity);
        const fkCol = `${oneTable}_id`;
        const onDelete = determineOnDelete(manyParticipation, false, false);
        const nullable = manyParticipation === 'partial';

        const tableStmt = tables.find(t => t.name === manyTable);
        if (tableStmt) {
          const fkColType = resolveType('integer', options.dialect);
          const nullStr = nullable ? '' : ' NOT NULL';
          const insertBefore = ');';
          const fkLines = [
            `,\n    ${fkCol} ${fkColType}${nullStr}`,
            options.useNamedConstraints
              ? `,\n    CONSTRAINT ${constraintName('fk', manyTable, oneTable)} FOREIGN KEY (${fkCol}) REFERENCES ${oneTable}(${onePK.join(', ')}) ON DELETE ${onDelete}`
              : `,\n    FOREIGN KEY (${fkCol}) REFERENCES ${oneTable}(${onePK.join(', ')}) ON DELETE ${onDelete}`,
          ];
          for (const attr of rel.attributes) {
            fkLines.unshift(`,\n    ${attr.name.toLowerCase()} ${resolveType(attr.dataType, options.dialect)}`);
          }
          tableStmt.sql = tableStmt.sql.replace(insertBefore, fkLines.join('') + '\n' + insertBefore);
          tableStmt.dependsOn.push(oneTable);

          if (options.includeIndexes) {
            indexes.push({
              sql: `CREATE INDEX ${constraintName('idx', manyTable, fkCol)} ON ${manyTable}(${fkCol});`,
            });
          }
        }
      }

      // ── M:N ──
      else if ((cardA === 'N' || cardA === 'M') && (cardB === 'N' || cardB === 'M')) {
        const junctionName = rel.name.toLowerCase() || `${tableA}_${tableB}`;
        const fkColA = `${tableA}_${pkA[0]}`.toLowerCase();
        const fkColB = `${tableB}_${pkB[0]}`.toLowerCase();
        const fkTypeA = resolveType('integer', options.dialect);
        const fkTypeB = resolveType('integer', options.dialect);

        const columns: string[] = [
          `    ${fkColA} ${fkTypeA} NOT NULL`,
          `    ${fkColB} ${fkTypeB} NOT NULL`,
        ];

        // Relationship attributes
        for (const attr of rel.attributes) {
          const colType = resolveType(attr.dataType, options.dialect);
          const nullable = attr.isNullable ? '' : ' NOT NULL';
          const def = attr.defaultValue ? ` DEFAULT ${attr.defaultValue}` : '';
          columns.push(`    ${attr.name.toLowerCase()} ${colType}${nullable}${def}`);
        }

        const pkLine = options.useNamedConstraints
          ? `    CONSTRAINT ${constraintName('pk', junctionName, `${fkColA}_${fkColB}`)} PRIMARY KEY (${fkColA}, ${fkColB})`
          : `    PRIMARY KEY (${fkColA}, ${fkColB})`;

        const fkLineA = options.useNamedConstraints
          ? `    CONSTRAINT ${constraintName('fk', junctionName, tableA)} FOREIGN KEY (${fkColA}) REFERENCES ${tableA}(${pkA.join(', ')}) ON DELETE CASCADE`
          : `    FOREIGN KEY (${fkColA}) REFERENCES ${tableA}(${pkA.join(', ')}) ON DELETE CASCADE`;

        const fkLineB = options.useNamedConstraints
          ? `    CONSTRAINT ${constraintName('fk', junctionName, tableB)} FOREIGN KEY (${fkColB}) REFERENCES ${tableB}(${pkB.join(', ')}) ON DELETE CASCADE`
          : `    FOREIGN KEY (${fkColB}) REFERENCES ${tableB}(${pkB.join(', ')}) ON DELETE CASCADE`;

        const ddl = [
          `CREATE TABLE ${junctionName} (`,
          [...columns, pkLine, fkLineA, fkLineB].join(',\n'),
          `);`,
        ].join('\n');

        tables.push({ name: junctionName, sql: ddl, dependsOn: [tableA, tableB] });

        if (options.includeIndexes) {
          indexes.push({
            sql: `CREATE INDEX ${constraintName('idx', junctionName, fkColB)} ON ${junctionName}(${fkColB});`,
          });
        }
      }
    }

    // ── N-ary (3+ participants) ──
    else if (participants.length > 2) {
      const junctionName = rel.name.toLowerCase();
      const fkCols: { col: string; type: string; table: string; pk: string }[] = [];

      for (const p of participants) {
        const entity = model.entities.find(e => e.id === p.entityId)!;
        const table = entity.name.toLowerCase();
        const pk = getPKColumns(entity);
        fkCols.push({
          col: `${table}_${pk[0]}`.toLowerCase(),
          type: resolveType('integer', options.dialect),
          table,
          pk: pk.join(', '),
        });
      }

      const columns = fkCols.map(fk => `    ${fk.col} ${fk.type} NOT NULL`);

      for (const attr of rel.attributes) {
        columns.push(`    ${attr.name.toLowerCase()} ${resolveType(attr.dataType, options.dialect)}`);
      }

      const pkLine = `    PRIMARY KEY (${fkCols.map(fk => fk.col).join(', ')})`;
      const fkLines = fkCols.map(fk =>
        options.useNamedConstraints
          ? `    CONSTRAINT ${constraintName('fk', junctionName, fk.table)} FOREIGN KEY (${fk.col}) REFERENCES ${fk.table}(${fk.pk}) ON DELETE CASCADE`
          : `    FOREIGN KEY (${fk.col}) REFERENCES ${fk.table}(${fk.pk}) ON DELETE CASCADE`
      );

      const ddl = [
        `CREATE TABLE ${junctionName} (`,
        [...columns, pkLine, ...fkLines].join(',\n'),
        `);`,
      ].join('\n');

      tables.push({
        name: junctionName,
        sql: ddl,
        dependsOn: fkCols.map(fk => fk.table),
      });
    }
  }

  // ── Phase 7: Multivalued Attributes ───────────────────────

  for (const entity of model.entities) {
    const multivaluedAttrs = collectMultivalued(entity);
    for (const { entityName, attr } of multivaluedAttrs) {
      const ownerTable = entityName.toLowerCase();
      const tableName = `${ownerTable}_${attr.name.toLowerCase()}`;
      const ownerPK = getPKColumns(entity);
      const ownerPKType = resolveType('integer', options.dialect);
      const valueType = resolveType(attr.multivaluedType ?? attr.dataType, options.dialect);

      const ddl = [
        `CREATE TABLE ${tableName} (`,
        `    ${ownerPK[0].toLowerCase()} ${ownerPKType} NOT NULL,`,
        `    ${attr.name.toLowerCase()} ${valueType} NOT NULL,`,
        options.useNamedConstraints
          ? `    CONSTRAINT ${constraintName('pk', tableName, `${ownerPK[0]}_${attr.name}`)} PRIMARY KEY (${ownerPK[0].toLowerCase()}, ${attr.name.toLowerCase()}),`
          : `    PRIMARY KEY (${ownerPK[0].toLowerCase()}, ${attr.name.toLowerCase()}),`,
        options.useNamedConstraints
          ? `    CONSTRAINT ${constraintName('fk', tableName, ownerTable)} FOREIGN KEY (${ownerPK[0].toLowerCase()}) REFERENCES ${ownerTable}(${ownerPK[0].toLowerCase()}) ON DELETE CASCADE`
          : `    FOREIGN KEY (${ownerPK[0].toLowerCase()}) REFERENCES ${ownerTable}(${ownerPK[0].toLowerCase()}) ON DELETE CASCADE`,
        `);`,
      ].join('\n');

      tables.push({ name: tableName, sql: ddl, dependsOn: [ownerTable] });
    }
  }

  // ── Phase 8: Dependency Ordering + Output ─────────────────

  const orderedNames = topologicalSort(tables);
  const orderedTables = orderedNames
    .map(name => tables.find(t => t.name === name)!)
    .filter(Boolean);

  const header = [
    `-- Generated by Dominion Flow ERD Creator`,
    `-- Database: ${model.name}`,
    `-- Dialect: ${options.dialect}`,
    `-- Generated: ${new Date().toISOString().split('T')[0]}`,
    ``,
  ].join('\n');

  const dropStatements = options.includeDropIfExists
    ? orderedNames
        .reverse()
        .map(name => {
          const cascade = options.dialect === 'postgresql' ? ' CASCADE' : '';
          return `DROP TABLE IF EXISTS ${name}${cascade};`;
        })
        .join('\n') + '\n\n'
    : '';

  // Re-reverse for CREATE order (drops go in reverse dependency order)
  if (options.includeDropIfExists) orderedNames.reverse();

  const createStatements = orderedTables.map(t => t.sql).join('\n\n');
  const indexStatements = indexes.length
    ? '\n\n-- Indexes\n' + indexes.map(i => i.sql).join('\n')
    : '';

  return header + dropStatements + createStatements + indexStatements + '\n';
}
```

### Usage Example

```typescript
const universityModel: ERDModel = {
  name: 'university_system',
  entities: [
    {
      id: 'e1', name: 'departments', isWeak: false,
      attributes: [
        { id: 'a1', name: 'department_id', kind: 'key', dataType: 'serial', isNullable: false },
        { id: 'a2', name: 'name', kind: 'simple', dataType: 'varchar', isNullable: false },
        { id: 'a3', name: 'building', kind: 'simple', dataType: 'varchar', isNullable: true },
        { id: 'a4', name: 'budget', kind: 'simple', dataType: 'decimal', isNullable: true, defaultValue: '0.00' },
      ],
    },
    {
      id: 'e2', name: 'professors', isWeak: false,
      attributes: [
        { id: 'a5', name: 'professor_id', kind: 'key', dataType: 'serial', isNullable: false },
        { id: 'a6', name: 'name', kind: 'composite', dataType: 'varchar', isNullable: false,
          children: [
            { id: 'a7', name: 'first_name', kind: 'simple', dataType: 'varchar', isNullable: false },
            { id: 'a8', name: 'last_name', kind: 'simple', dataType: 'varchar', isNullable: false },
          ]},
        { id: 'a9', name: 'email', kind: 'simple', dataType: 'varchar', isNullable: false },
        { id: 'a10', name: 'phone_numbers', kind: 'multivalued', dataType: 'varchar', isNullable: false,
          multivaluedType: 'VARCHAR(20)' },
      ],
    },
    {
      id: 'e3', name: 'students', isWeak: false,
      attributes: [
        { id: 'a11', name: 'student_id', kind: 'key', dataType: 'serial', isNullable: false },
        { id: 'a12', name: 'first_name', kind: 'simple', dataType: 'varchar', isNullable: false },
        { id: 'a13', name: 'last_name', kind: 'simple', dataType: 'varchar', isNullable: false },
        { id: 'a14', name: 'dob', kind: 'simple', dataType: 'date', isNullable: false },
        { id: 'a15', name: 'age', kind: 'derived', dataType: 'integer', isNullable: true,
          derivedExpression: "EXTRACT(YEAR FROM AGE(CURRENT_DATE, dob))" },
      ],
    },
    {
      id: 'e4', name: 'courses', isWeak: false,
      attributes: [
        { id: 'a16', name: 'course_id', kind: 'key', dataType: 'serial', isNullable: false },
        { id: 'a17', name: 'title', kind: 'simple', dataType: 'varchar', isNullable: false },
        { id: 'a18', name: 'credits', kind: 'simple', dataType: 'integer', isNullable: false },
      ],
    },
  ],
  relationships: [
    {
      id: 'r1', name: 'belongs_to', isIdentifying: false,
      participants: [
        { entityId: 'e1', cardinality: '1', participation: 'partial' },
        { entityId: 'e2', cardinality: 'N', participation: 'total' },
      ],
      attributes: [],
    },
    {
      id: 'r2', name: 'enrollments', isIdentifying: false,
      participants: [
        { entityId: 'e3', cardinality: 'M', participation: 'partial' },
        { entityId: 'e4', cardinality: 'N', participation: 'partial' },
      ],
      attributes: [
        { id: 'ra1', name: 'grade', kind: 'simple', dataType: 'char', isNullable: true },
        { id: 'ra2', name: 'enrollment_date', kind: 'simple', dataType: 'date', isNullable: false, defaultValue: 'CURRENT_DATE' },
      ],
    },
  ],
};

const ddl = generateDDL(universityModel, {
  dialect: 'postgresql',
  useNamedConstraints: true,
  includeIndexes: true,
  includeDropIfExists: true,
  idStrategy: 'serial',
  timestampColumns: true,
});

console.log(ddl);
```

### Expected Output

```sql
-- Generated by Dominion Flow ERD Creator
-- Database: university_system
-- Dialect: postgresql
-- Generated: 2026-03-09

DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS professors_phone_numbers CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS professors CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

CREATE TABLE departments (
    department_id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    building VARCHAR,
    budget NUMERIC DEFAULT 0.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_departments_department_id PRIMARY KEY (department_id)
);

CREATE TABLE professors (
    professor_id SERIAL NOT NULL,
    name_first_name VARCHAR NOT NULL,
    name_last_name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_professors_professor_id PRIMARY KEY (professor_id),
    departments_id INTEGER NOT NULL,
    CONSTRAINT fk_professors_departments FOREIGN KEY (departments_id)
        REFERENCES departments(department_id) ON DELETE RESTRICT
);

CREATE TABLE students (
    student_id SERIAL NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    dob DATE NOT NULL,
    age INTEGER GENERATED ALWAYS AS (EXTRACT(YEAR FROM AGE(CURRENT_DATE, dob))) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_students_student_id PRIMARY KEY (student_id)
);

CREATE TABLE courses (
    course_id SERIAL NOT NULL,
    title VARCHAR NOT NULL,
    credits INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_courses_course_id PRIMARY KEY (course_id)
);

CREATE TABLE enrollments (
    students_student_id INTEGER NOT NULL,
    courses_course_id INTEGER NOT NULL,
    grade CHAR,
    enrollment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT pk_enrollments_students_student_id_courses_course_id
        PRIMARY KEY (students_student_id, courses_course_id),
    CONSTRAINT fk_enrollments_students FOREIGN KEY (students_student_id)
        REFERENCES students(student_id) ON DELETE CASCADE,
    CONSTRAINT fk_enrollments_courses FOREIGN KEY (courses_course_id)
        REFERENCES courses(course_id) ON DELETE CASCADE
);

CREATE TABLE professors_phone_numbers (
    professor_id INTEGER NOT NULL,
    phone_numbers VARCHAR(20) NOT NULL,
    CONSTRAINT pk_professors_phone_numbers_professor_id_phone_numbers
        PRIMARY KEY (professor_id, phone_numbers),
    CONSTRAINT fk_professors_phone_numbers_professors
        FOREIGN KEY (professor_id) REFERENCES professors(professor_id)
        ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_professors_departments_id ON professors(departments_id);
CREATE INDEX idx_enrollments_courses_course_id ON enrollments(courses_course_id);
```

---

## When to Use

- Building an ERD Creator / visual database design tool
- Implementing a schema-from-diagram code generation feature
- Porting an existing ER diagram from a whiteboard or academic tool to running SQL
- Teaching database design -- the 7 rules are the canonical reference
- Validating that a schema correctly implements an ER model
- Generating multi-dialect DDL from a single source-of-truth model

## When NOT to Use

- **Reverse engineering existing SQL to ERD** -- use `sql-ddl-to-json-schema` or `node-sql-parser` instead, then map the JSON into ERDModel types
- **Schema migration / diffing** -- use Prisma Migrate, Drizzle Kit, or Alembic; this skill generates initial DDL, not incremental changes
- **NoSQL / document databases** -- these mapping rules are exclusively for relational databases
- **Denormalization for performance** -- this produces normalized schemas; deliberate denormalization is a separate concern (see data warehousing patterns)
- **ORM schema definition** -- if you already use Prisma/Drizzle/TypeORM, define schemas in their DSL and let the ORM handle DDL

## Related Skills

- `database-schema-designer.md` -- broader schema design patterns (multi-tenancy, RLS, audit trails, seeding)
- `erd-creator-textbook-research.md` -- raw research findings that feed this skill
- `normalization-validator.md` -- planned: 1NF/2NF/3NF violation detection
- `regex-alternation-ordering-sql-types.md` -- SQL type parsing for DDL import
- `reserved-word-context-aware-quoting.md` -- identifier quoting across dialects
- `postgresql-to-mysql-runtime-translation.md` -- runtime SQL translation patterns

## References

1. **LibreTexts "Database Design"** -- Dr. Sarah North, Chapters 6-10. CC BY 4.0. Canonical ER mapping rules.
2. **Text2Schema (arXiv 2025)** -- Multi-agent NL-to-DDL decomposition. Entity/relationship/constraint extraction pipeline.
3. **NOMAD (arXiv 2025)** -- Agent roles for schema generation: extractor, classifier, integrator, code articulator, verifier.
4. **DrawDB** (github.com/drawdb-io/drawdb) -- OSS visual database designer. Gold standard for dialect-specific DDL generators from JSON model.
5. **ChartDB** (github.com/chartdb/chartdb) -- AI-powered DDL export via LLM prompting.
6. **ERFlow** -- MCP Server with 25+ tools for NL schema edits and checkpoint-based migration generation.
7. **node-sql-parser** (npm) -- Bidirectional SQL-to-AST parsing. `parser.astify()` / `parser.sqlify()`.
8. **sql-ddl-to-json-schema** (npm) -- DDL parser outputting ERD-friendly JSON Schema.
9. **Peter Chen (1976)** -- "The Entity-Relationship Model: Toward a Unified View of Data." Original ER notation.
