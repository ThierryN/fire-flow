---
name: normalization-validator
category: database-solutions
version: 1.0.0
contributed: 2026-03-09
contributor: fire-research
last_updated: 2026-03-09
tags: [normalization, 1nf, 2nf, 3nf, database-quality, validation, ai-normalization]
difficulty: hard
usage_count: 0
success_rate: 100
---

# Normalization Validator


## Problem

Normalization violations in database schemas cause three categories of data anomalies:

1. **Insert anomalies** -- Cannot add data without unrelated data (e.g., cannot add a department without an employee)
2. **Update anomalies** -- Changing one fact requires updating multiple rows (e.g., renaming a department touches every employee row)
3. **Delete anomalies** -- Removing data destroys unrelated facts (e.g., deleting the last employee in a department loses the department name)

These violations are easy to introduce and hard to detect without systematic validation. LLM-generated schemas (per NOMAD) exhibit structural, relationship, and semantic/logical errors at rates high enough to require automated checking.

## First Normal Form (1NF)

A table is in 1NF when every column contains only atomic (indivisible) values, every row is unique, and there is a defined primary key.

### 1NF Violations to Detect

| Violation | Detection Signal | Severity |
|-----------|-----------------|----------|
| **Repeating groups** | Multiple values in a single cell: arrays, comma-separated lists, JSON arrays in non-JSONB columns | ERROR |
| **Missing primary key** | No PK constraint defined on the table | ERROR |
| **Mixed data types** | Column accepts heterogeneous types (e.g., VARCHAR storing both numbers and text interchangeably where a typed column is appropriate) | WARN |
| **Duplicate rows** | No unique constraint and no PK; identical rows can exist | ERROR |
| **Numbered column pattern** | Columns like `phone1`, `phone2`, `phone3` or `skill_a`, `skill_b`, `skill_c` | WARN |

### 1NF Detection Algorithm

```
FOR each table in schema:
  IF table has no PRIMARY KEY → ERROR: "No primary key defined"
  IF table has no UNIQUE constraint AND no PK → ERROR: "Duplicate rows possible"

  FOR each column in table:
    IF column type is TEXT/VARCHAR AND column name suggests plurality
       (ends in 's', contains 'list', 'tags', 'items', 'values') → WARN: "Possible multivalued attribute"
    IF column type is TEXT AND default contains ',' or '[' → WARN: "Possible repeating group"

  IF columns match pattern (name + digit) with 2+ sequential occurrences → WARN: "Numbered column pattern (repeating group)"
```

### 1NF Fix Pattern

Repeating groups become a separate table with a foreign key back to the parent:

```sql
-- BEFORE (violates 1NF): phone_numbers = "555-1234,555-5678"
CREATE TABLE employees (
  id INT PRIMARY KEY,
  name VARCHAR(100),
  phone_numbers TEXT  -- comma-separated = 1NF violation
);

-- AFTER (1NF compliant):
CREATE TABLE employees (
  id INT PRIMARY KEY,
  name VARCHAR(100)
);

CREATE TABLE employee_phones (
  id INT PRIMARY KEY,
  employee_id INT REFERENCES employees(id),
  phone_number VARCHAR(20),
  phone_type VARCHAR(10) -- 'home', 'work', 'mobile'
);
```

## Second Normal Form (2NF)

A table is in 2NF when it is in 1NF AND every non-key attribute depends on the **entire** primary key (no partial dependencies). This rule only applies to tables with composite primary keys.

### 2NF Violations to Detect

| Violation | Detection Signal | Severity |
|-----------|-----------------|----------|
| **Partial dependency** | Non-key column depends on only part of a composite PK | ERROR |
| **Junction table bloat** | Junction table has attributes that depend on only one FK | WARN |

### 2NF Detection Algorithm

```
FOR each table with composite primary key (pk_col_1, pk_col_2, ...):
  FOR each non-key column C:
    FOR each individual PK component pk_col_i:
      IF C is functionally determined by pk_col_i alone
        → ERROR: "Partial dependency: {C} depends only on {pk_col_i}, not the full key"

  -- Heuristic: if a non-key column name contains or matches a PK column's
  -- referenced table name, it likely depends only on that FK
  FOR each non-key column C:
    IF C.name starts with or contains the entity name of exactly one PK component
      → WARN: "Possible partial dependency: {C} may belong in the {entity} table"
```

### 2NF Fix Pattern

Move partially-dependent columns to the table they actually depend on:

```sql
-- BEFORE (violates 2NF): student_name depends only on student_id
CREATE TABLE enrollments (
  student_id INT,
  course_id INT,
  student_name VARCHAR(100),  -- depends only on student_id (partial dependency)
  enrollment_date DATE,
  PRIMARY KEY (student_id, course_id)
);

-- AFTER (2NF compliant):
CREATE TABLE students (
  student_id INT PRIMARY KEY,
  student_name VARCHAR(100)
);

CREATE TABLE enrollments (
  student_id INT REFERENCES students(student_id),
  course_id INT,
  enrollment_date DATE,
  PRIMARY KEY (student_id, course_id)
);
```

## Third Normal Form (3NF)

A table is in 3NF when it is in 2NF AND no non-key attribute transitively depends on the primary key. In other words: every non-key column must depend on "the key, the whole key, and nothing but the key."

### 3NF Violations to Detect

| Violation | Detection Signal | Severity |
|-----------|-----------------|----------|
| **Transitive dependency** | A non-key column B determines another non-key column C (PK->B->C) | ERROR |
| **Lookup value embedded** | A table stores both a code/ID and its human-readable name (e.g., `dept_id` + `dept_name`) | WARN |

### Common 3NF Violation Patterns

```
Employee table:
  PK: employee_id
  dept_id → dept_name, dept_manager  (transitive: employee_id → dept_id → dept_name)

Order table:
  PK: order_id
  product_id → product_name, product_category  (transitive)

Invoice table:
  PK: invoice_id
  customer_id → customer_name, customer_address  (transitive)
```

### 3NF Detection Algorithm

```
FOR each table T:
  FOR each pair of non-key columns (B, C):
    IF B appears to be a foreign key (name ends in '_id', '_code', '_key')
      AND C's name shares a prefix/entity with B (e.g., dept_id and dept_name):
        → WARN: "Possible transitive dependency: {B} → {C}. Consider a separate {entity} table."

    IF B has a UNIQUE constraint AND C correlates with B:
        → WARN: "Non-key determinant {B} may create transitive dependency on {C}"
```

### 3NF Fix Pattern

Extract transitive dependencies into their own table:

```sql
-- BEFORE (violates 3NF): dept_name depends on dept_id, not employee_id
CREATE TABLE employees (
  employee_id INT PRIMARY KEY,
  employee_name VARCHAR(100),
  dept_id INT,
  dept_name VARCHAR(100),       -- transitive dependency
  dept_manager_name VARCHAR(100) -- transitive dependency
);

-- AFTER (3NF compliant):
CREATE TABLE departments (
  dept_id INT PRIMARY KEY,
  dept_name VARCHAR(100),
  dept_manager_name VARCHAR(100)
);

CREATE TABLE employees (
  employee_id INT PRIMARY KEY,
  employee_name VARCHAR(100),
  dept_id INT REFERENCES departments(dept_id)
);
```

## Anomaly Types with Concrete Examples

### Insert Anomaly

```
-- With the un-normalized employees table above:
-- Cannot record a new department "Marketing" until we hire someone into it.
INSERT INTO employees (employee_id, employee_name, dept_id, dept_name)
VALUES (NULL, NULL, 5, 'Marketing');  -- Fails: employee_id is PK, cannot be NULL
```

### Update Anomaly

```
-- Department "Engineering" renames to "Product Engineering"
-- Must update EVERY employee row in that department
UPDATE employees SET dept_name = 'Product Engineering' WHERE dept_id = 3;
-- If one row is missed → inconsistent data (some say "Engineering", some say "Product Engineering")
```

### Delete Anomaly

```
-- Delete the last employee in the "Legal" department
DELETE FROM employees WHERE employee_id = 42;
-- The fact that department "Legal" (dept_id=7) exists is now lost entirely
```

## Automated Validation Checklist

Complete list of checks with severity levels, organized by NOMAD error taxonomy categories.

### Structural Checks

| # | Check | Severity | NF |
|---|-------|----------|----|
| 1 | Entity has no primary key defined | ERROR | 1NF |
| 2 | Duplicate rows possible (no PK, no UNIQUE) | ERROR | 1NF |
| 3 | Numbered column pattern detected (`col1`, `col2`, `col3`) | WARN | 1NF |
| 4 | Column name suggests multivalued data (plural, 'list', 'tags', 'items') | WARN | 1NF |
| 5 | Table has >15 columns (may need decomposition) | INFO | -- |
| 6 | Column stores comma-separated or array values in non-array type | ERROR | 1NF |

### Relationship Checks

| # | Check | Severity | NF |
|---|-------|----------|----|
| 7 | M:N relationship has no junction table | WARN | -- |
| 8 | Weak entity has no identifying relationship | WARN | -- |
| 9 | Circular FK dependency without proper cascade strategy | ERROR | -- |
| 10 | Junction table contains non-key attributes depending on single FK | WARN | 2NF |

### Semantic/Logical Checks

| # | Check | Severity | NF |
|---|-------|----------|----|
| 11 | Composite PK with non-key column not depending on full key | WARN | 2NF |
| 12 | Non-key column pair suggests transitive dependency (`x_id` + `x_name`) | WARN | 3NF |
| 13 | Non-key column with UNIQUE constraint determines other non-key columns | WARN | 3NF |
| 14 | Table stores derived/calculated data that could be computed from other columns | INFO | -- |
| 15 | Column has misleading type (e.g., VARCHAR for what should be INT/DATE) | INFO | -- |

## AI-Powered Normalization (Miffie Pattern)

Based on Miffie (arXiv 2508.17693): a dual-LLM self-refinement architecture that achieves high normalization accuracy with zero-shot prompts and no fine-tuning.

### Architecture

```
Schema Input → LLM1 (Suggester) → Normalization Suggestions → LLM2 (Validator) → Refined Output
                    ↑                                                    |
                    └────────────── Feedback Loop ───────────────────────┘
```

### LLM1: Suggester Prompt

```
You are a database normalization expert. Analyze the following schema and identify
all normalization violations up to 3NF.

Schema:
{schema_definition}

For each violation found, provide:
1. The table and columns involved
2. Which normal form is violated (1NF, 2NF, or 3NF)
3. The specific functional dependency causing the violation
4. A concrete fix: the new table structure(s) needed

Format your response as a structured list. Be thorough — check every table for
every normal form sequentially (1NF first, then 2NF, then 3NF).
```

### LLM2: Validator Prompt

```
You are a database normalization reviewer. A colleague analyzed a schema and
proposed normalization fixes. Your job is to validate their analysis.

Original schema:
{schema_definition}

Proposed violations and fixes:
{llm1_output}

For each proposed violation:
1. CONFIRM or REJECT — is this actually a violation?
2. If rejected, explain why (false positive detection)
3. If confirmed, verify the fix is correct and complete
4. Check if the fix introduces any NEW violations
5. Identify any violations the original analysis MISSED

Provide your final validated list of violations and corrected fixes.
```

### Integration: "Normalize My Schema" Flow

```typescript
async function normalizeSchema(
  schema: SchemaDefinition,
  llm: LLMClient
): Promise<NormalizationReport> {
  // Round 1: Suggest
  const suggestions = await llm.generate({
    model: 'claude-sonnet-4-20250514', // or gemini-2.5-pro
    prompt: buildSuggesterPrompt(schema),
    temperature: 0.2, // low for precision
  });

  // Round 2: Validate
  const validated = await llm.generate({
    model: 'claude-sonnet-4-20250514',
    prompt: buildValidatorPrompt(schema, suggestions),
    temperature: 0.1, // even lower for validation
  });

  // Round 3 (optional): Self-refinement if validator found missed violations
  if (validated.missedViolations.length > 0) {
    const refined = await llm.generate({
      model: 'claude-sonnet-4-20250514',
      prompt: buildRefinementPrompt(schema, suggestions, validated),
      temperature: 0.1,
    });
    return parseNormalizationReport(refined);
  }

  return parseNormalizationReport(validated);
}
```

## AI-Powered Profiling (Cocoon Pattern)

Based on Cocoon (ACM HILDA 2024): combines statistical profiling with LLM semantic understanding to produce human-verifiable explanations for schema issues.

### Approach

1. **Statistical analysis** -- Compute column distributions, null rates, cardinality, pattern frequency
2. **Semantic enrichment** -- Ask the LLM to interpret what the statistics mean for normalization
3. **Human-verifiable output** -- Show concrete data examples that prove each violation

### Profiling Prompt

```
Given these column statistics for table "{table_name}":

{column_statistics_json}

And these sample rows:
{sample_rows}

Analyze for normalization violations. For each violation you find:
1. State the violation type (1NF/2NF/3NF) and the columns involved
2. Quote the SPECIFIC sample rows that demonstrate the violation
3. Explain in plain English WHY this is a violation
4. Show what anomaly (insert/update/delete) would result from this structure

Example output format:
  VIOLATION: 3NF transitive dependency in "orders" table
  COLUMNS: customer_id → customer_name
  EVIDENCE: Rows 3 and 7 both have customer_id=42 with customer_name="Alice"
            — if Alice changes her name, both rows must be updated (update anomaly)
  FIX: Extract customer_name to a "customers" table keyed by customer_id
```

### Why Cocoon Explanations Matter

Raw normalization rules are abstract. Cocoon-style output tells the developer: "Here is row 3 and row 7 from YOUR data that prove this is a problem." This turns theoretical violations into concrete evidence that justifies the refactoring cost.

## Implementation: Validator Function

TypeScript implementation that takes a schema model and returns findings. Designed for integration with an ERD tool or standalone CLI.

```typescript
// normalization-validator.ts

interface Column {
  name: string;
  type: string;
  isPrimaryKey: boolean;
  isForeignKey: boolean;
  isUnique: boolean;
  isNullable: boolean;
  referencesTable?: string;
  referencesColumn?: string;
  defaultValue?: string;
}

interface Table {
  name: string;
  columns: Column[];
}

interface Relationship {
  fromTable: string;
  toTable: string;
  type: 'one-to-one' | 'one-to-many' | 'many-to-many';
  throughTable?: string; // junction table name if M:N
}

interface SchemaModel {
  tables: Table[];
  relationships: Relationship[];
}

type Severity = 'ERROR' | 'WARN' | 'INFO';
type NormalForm = '1NF' | '2NF' | '3NF' | 'structural' | 'relationship';

interface Finding {
  severity: Severity;
  normalForm: NormalForm;
  table: string;
  columns: string[];
  message: string;
  fix: string;
}

// Patterns that suggest multivalued attributes
const PLURAL_HINTS = /(?:tags|items|values|skills|phones|emails|addresses|categories|roles|permissions|features|list|array|set)$/i;
const NUMBERED_COL = /^(.+?)(\d+)$/;
const FK_PATTERN = /^(.+?)_(?:id|code|key|fk)$/i;

function validateNormalization(schema: SchemaModel): Finding[] {
  const findings: Finding[] = [];

  for (const table of schema.tables) {
    // === 1NF Checks ===
    findings.push(...check1NF(table));

    // === 2NF Checks ===
    findings.push(...check2NF(table));

    // === 3NF Checks ===
    findings.push(...check3NF(table));

    // === Structural Checks ===
    findings.push(...checkStructural(table));
  }

  // === Relationship Checks ===
  findings.push(...checkRelationships(schema));

  return findings;
}

function check1NF(table: Table): Finding[] {
  const findings: Finding[] = [];
  const pkColumns = table.columns.filter((c) => c.isPrimaryKey);

  // Check 1: No primary key
  if (pkColumns.length === 0) {
    findings.push({
      severity: 'ERROR',
      normalForm: '1NF',
      table: table.name,
      columns: [],
      message: `Table "${table.name}" has no primary key defined.`,
      fix: `Add a PRIMARY KEY column (e.g., "id INT PRIMARY KEY AUTO_INCREMENT" or "id UUID PRIMARY KEY DEFAULT gen_random_uuid()").`,
    });
  }

  // Check 2: Multivalued attribute hints
  for (const col of table.columns) {
    if (PLURAL_HINTS.test(col.name) && !col.isForeignKey) {
      findings.push({
        severity: 'WARN',
        normalForm: '1NF',
        table: table.name,
        columns: [col.name],
        message: `Column "${col.name}" name suggests multivalued data. If it stores multiple values, this violates 1NF.`,
        fix: `Create a separate table (e.g., "${table.name}_${col.name}") with a foreign key back to "${table.name}".`,
      });
    }

    // Check for comma-separated defaults or array-like types stored as TEXT
    if (
      col.type.match(/^(TEXT|VARCHAR|CHAR)/i) &&
      col.defaultValue &&
      (col.defaultValue.includes(',') || col.defaultValue.startsWith('['))
    ) {
      findings.push({
        severity: 'ERROR',
        normalForm: '1NF',
        table: table.name,
        columns: [col.name],
        message: `Column "${col.name}" default value suggests comma-separated or array data in a text column.`,
        fix: `Extract repeating values into a related table with a foreign key.`,
      });
    }
  }

  // Check 3: Numbered column pattern (phone1, phone2, phone3)
  const basenames = new Map<string, string[]>();
  for (const col of table.columns) {
    const match = col.name.match(NUMBERED_COL);
    if (match) {
      const base = match[1];
      if (!basenames.has(base)) basenames.set(base, []);
      basenames.get(base)!.push(col.name);
    }
  }
  for (const [base, cols] of basenames) {
    if (cols.length >= 2) {
      findings.push({
        severity: 'WARN',
        normalForm: '1NF',
        table: table.name,
        columns: cols,
        message: `Numbered column pattern detected: ${cols.join(', ')}. This is a repeating group (1NF violation).`,
        fix: `Create a separate "${table.name}_${base}" table. Each numbered column becomes a row in the new table.`,
      });
    }
  }

  return findings;
}

function check2NF(table: Table): Finding[] {
  const findings: Finding[] = [];
  const pkColumns = table.columns.filter((c) => c.isPrimaryKey);

  // 2NF only applies to composite primary keys
  if (pkColumns.length < 2) return findings;

  const nonKeyColumns = table.columns.filter((c) => !c.isPrimaryKey);
  const pkFKColumns = pkColumns.filter((c) => c.isForeignKey);

  for (const col of nonKeyColumns) {
    // Heuristic: if column name shares entity prefix with exactly one PK component
    for (const pkCol of pkFKColumns) {
      const fkMatch = pkCol.name.match(FK_PATTERN);
      if (!fkMatch) continue;

      const entityName = fkMatch[1]; // e.g., "student" from "student_id"
      if (
        col.name.startsWith(entityName + '_') ||
        col.name.startsWith(entityName)
      ) {
        findings.push({
          severity: 'WARN',
          normalForm: '2NF',
          table: table.name,
          columns: [pkCol.name, col.name],
          message: `Possible partial dependency: "${col.name}" may depend only on "${pkCol.name}", not the full composite key.`,
          fix: `Move "${col.name}" to the "${entityName}" table if it depends solely on "${pkCol.name}".`,
        });
      }
    }
  }

  return findings;
}

function check3NF(table: Table): Finding[] {
  const findings: Finding[] = [];
  const nonKeyColumns = table.columns.filter((c) => !c.isPrimaryKey);

  // Look for FK + related attribute pairs (e.g., dept_id + dept_name)
  const fkColumns = nonKeyColumns.filter((c) => c.isForeignKey);

  for (const fkCol of fkColumns) {
    const fkMatch = fkCol.name.match(FK_PATTERN);
    if (!fkMatch) continue;

    const entityName = fkMatch[1]; // e.g., "dept" from "dept_id"

    for (const otherCol of nonKeyColumns) {
      if (otherCol.name === fkCol.name) continue;

      if (
        otherCol.name.startsWith(entityName + '_') &&
        otherCol.name !== fkCol.name
      ) {
        findings.push({
          severity: 'WARN',
          normalForm: '3NF',
          table: table.name,
          columns: [fkCol.name, otherCol.name],
          message: `Possible transitive dependency: "${otherCol.name}" likely depends on "${fkCol.name}", not the primary key. (PK → ${fkCol.name} → ${otherCol.name})`,
          fix: `Move "${otherCol.name}" to the "${fkCol.referencesTable || entityName}" table. Keep only "${fkCol.name}" as the foreign key reference.`,
        });
      }
    }
  }

  // Look for non-FK UNIQUE columns that determine other columns
  const uniqueNonFK = nonKeyColumns.filter(
    (c) => c.isUnique && !c.isForeignKey
  );
  for (const uCol of uniqueNonFK) {
    const uMatch = uCol.name.match(FK_PATTERN);
    if (!uMatch) continue;

    const entityName = uMatch[1];
    for (const otherCol of nonKeyColumns) {
      if (otherCol.name === uCol.name) continue;
      if (otherCol.name.startsWith(entityName + '_')) {
        findings.push({
          severity: 'WARN',
          normalForm: '3NF',
          table: table.name,
          columns: [uCol.name, otherCol.name],
          message: `Non-key determinant: "${uCol.name}" (UNIQUE) may transitively determine "${otherCol.name}".`,
          fix: `Extract "${uCol.name}" and "${otherCol.name}" into their own table with "${uCol.name}" as primary key.`,
        });
      }
    }
  }

  return findings;
}

function checkStructural(table: Table): Finding[] {
  const findings: Finding[] = [];

  // Column count check
  if (table.columns.length > 15) {
    findings.push({
      severity: 'INFO',
      normalForm: 'structural',
      table: table.name,
      columns: [],
      message: `Table "${table.name}" has ${table.columns.length} columns. Tables with >15 columns often benefit from decomposition.`,
      fix: `Review whether columns can be grouped into related entities (vertical partitioning).`,
    });
  }

  return findings;
}

function checkRelationships(schema: SchemaModel): Finding[] {
  const findings: Finding[] = [];

  // Check M:N without junction table
  for (const rel of schema.relationships) {
    if (rel.type === 'many-to-many' && !rel.throughTable) {
      findings.push({
        severity: 'WARN',
        normalForm: 'relationship',
        table: `${rel.fromTable} <-> ${rel.toTable}`,
        columns: [],
        message: `Many-to-many relationship between "${rel.fromTable}" and "${rel.toTable}" has no junction table.`,
        fix: `Create a junction table (e.g., "${rel.fromTable}_${rel.toTable}") with foreign keys to both tables.`,
      });
    }
  }

  // Check circular FK dependencies
  const fkGraph = new Map<string, Set<string>>();
  for (const table of schema.tables) {
    for (const col of table.columns) {
      if (col.isForeignKey && col.referencesTable) {
        if (!fkGraph.has(table.name)) fkGraph.set(table.name, new Set());
        fkGraph.get(table.name)!.add(col.referencesTable);
      }
    }
  }

  // Cycle detection via recursive DFS with path tracking
  const globalVisited = new Set<string>();
  function detectCycle(node: string, path: string[], visiting: Set<string>): void {
    if (visiting.has(node)) {
      // Found cycle — extract only the cycle portion from the path
      const cycleStart = path.indexOf(node);
      const cyclePath = [...path.slice(cycleStart), node];
      findings.push({
        severity: 'ERROR',
        normalForm: 'relationship',
        table: node,
        columns: [],
        message: `Circular foreign key dependency: ${cyclePath.join(' → ')}.`,
        fix: `Break the cycle by making one FK nullable, using a bridge table, or implementing application-level referential integrity for one link.`,
      });
      return;
    }
    if (globalVisited.has(node)) return;
    visiting.add(node);
    path.push(node);

    const neighbors = fkGraph.get(node);
    if (neighbors) {
      for (const neighbor of neighbors) {
        detectCycle(neighbor, path, visiting);
      }
    }
    path.pop();
    visiting.delete(node);
    globalVisited.add(node);
  }
  for (const startTable of fkGraph.keys()) {
    detectCycle(startTable, [], new Set());
  }

  return findings;
}

// === Entry point for ERD tool integration ===
function runValidator(schema: SchemaModel): {
  findings: Finding[];
  summary: { errors: number; warnings: number; info: number };
} {
  const findings = validateNormalization(schema);
  return {
    findings,
    summary: {
      errors: findings.filter((f) => f.severity === 'ERROR').length,
      warnings: findings.filter((f) => f.severity === 'WARN').length,
      info: findings.filter((f) => f.severity === 'INFO').length,
    },
  };
}

export {
  validateNormalization,
  runValidator,
  type SchemaModel,
  type Table,
  type Column,
  type Relationship,
  type Finding,
  type Severity,
  type NormalForm,
};
```

## When to Use

- Designing a new database schema (run before writing migrations)
- Reviewing an LLM-generated schema (NOMAD shows these have high error rates)
- Porting between databases (PG to MySQL, Mongo to SQL) where schema was informally designed
- Adding an ERD validation step to a design tool
- Teaching normalization concepts with concrete, automated feedback

## When NOT to Use

- **Intentional denormalization for read performance** -- Data warehouses, materialized views, and OLAP schemas deliberately violate 3NF for query speed. Document the intent and skip validation.
- **JSONB/document columns in PostgreSQL** -- Storing structured JSON in a JSONB column is not a 1NF violation when the column is queried as a unit or via JSON operators. Only flag it if individual JSON fields are being extracted in WHERE clauses repeatedly.
- **Audit/log tables** -- These are append-only and never updated, so update/delete anomalies do not apply.
- **Schemas already validated by a migration tool with constraints** -- If Prisma/Knex/TypeORM generates the schema from a well-typed model, most structural checks are already covered.

## Related Skills

- `database-solutions/database-schema-designer.md` -- ERD creation tool that can consume these validation results
- `database-solutions/erd-creator-textbook-research.md` -- Research foundation for ERD tooling
- `database-solutions/postgresql-to-mysql-runtime-translation.md` -- Cross-dialect translation where normalization issues surface
- `database-solutions/reserved-word-context-aware-quoting.md` -- SQL dialect handling
- `database-solutions/CONDITIONAL_SQL_MIGRATION_PATTERN.md` -- Idempotent migration patterns for fixes

## References

1. LibreTexts, *Database Design* -- Canonical normalization rules (1NF through BCNF)
2. Miffie -- Dual-LLM Self-Refinement for Database Normalization (arXiv 2508.17693, August 2025)
3. Cocoon -- LLM-Powered Data Profiling (ACM HILDA 2024, arXiv preprint)
4. NOMAD -- Error Taxonomy for LLM-Generated Database Schemas (arXiv 2025)
5. Codd, E.F. -- "A Relational Model of Data for Large Shared Data Banks" (1970) -- foundational normalization theory
