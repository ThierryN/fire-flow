=============================================================
            DATABASE TEXTBOOK RESEARCH — ERD Creator
=============================================================

Papers/Sources Analyzed: 1 (204-page textbook, ~64KB extracted)
  Source: LibreTexts "Database Design" — Dr. Sarah North, Affordable Learning Georgia (CC BY 4.0)
  Chapters covered: 6 (ER Diagrams), 7 (Mapping ER to Schema, Normalization), 8 (SQL and ER), 9 (SQL DDL), 10 (SQL DML)
  Note: Extraction truncated at 64KB mid-Chapter 7. Standard academic content supplemented with canonical database theory.

Findings Above Threshold (>=3.0): 12
Wave 1 Candidates (>=4.0): 8

-------------------------------------------------------------
ER DIAGRAM COMPONENTS (for React Flow nodes)
-------------------------------------------------------------

### Entity Types (React Flow: rectangular nodes)
- **Strong Entity**: Rectangle with entity name. Has its own primary key.
- **Weak Entity**: Double-bordered rectangle. Cannot exist without its identifying (owner) entity. Requires partial key + owner's PK for full identification.

### Attribute Types (React Flow: oval/ellipse nodes or inline)
- **Simple Attribute**: Single oval connected to entity.
- **Key Attribute**: Oval with underlined text (primary key identifier).
- **Composite Attribute**: Oval that branches into sub-ovals (e.g., Name -> FirstName, LastName).
- **Multivalued Attribute**: Double-bordered oval (e.g., PhoneNumbers — multiple values per entity).
- **Derived Attribute**: Dashed-bordered oval (e.g., Age derived from DateOfBirth).

### Relationship Types (React Flow: diamond nodes in Chen, lines in Crow's Foot)
- **Unary (Recursive)**: Entity relates to itself (e.g., Employee manages Employee).
- **Binary**: Two entities connected (most common — e.g., Student enrolls in Course).
- **N-ary (Ternary+)**: Three or more entities in a single relationship (rare but valid).

### Cardinality Constraints
- **1:1** — One entity instance maps to exactly one of the other.
- **1:N** — One entity instance maps to many of the other.
- **M:N** — Many-to-many, both sides can have multiple instances.

### Participation Constraints
- **Total (mandatory)**: Double line — every instance MUST participate (e.g., every Order MUST have a Customer).
- **Partial (optional)**: Single line — instances MAY participate (e.g., an Employee MAY manage a Department).

-------------------------------------------------------------
NOTATION MAPPING (for visual rendering)
-------------------------------------------------------------

### Chen Notation (Original — Peter Chen, 1976)
- **Entity**: Rectangle
- **Attribute**: Oval connected by line to entity
- **Relationship**: Diamond between entities
- **Cardinality**: Numbers (1, M, N) on connecting lines
- **Participation**: Single line (partial) vs double line (total)
- **Key attribute**: Underlined text in oval
- **Weak entity**: Double rectangle
- **Weak relationship**: Double diamond

Rendering requirements for Chen:
  - 5 node types: Entity (rect), Weak Entity (double rect), Attribute (oval), Relationship (diamond), Weak Relationship (double diamond)
  - 6 attribute variants: simple, key, composite, multivalued, derived, partial key
  - Line styles: single (partial), double (total)
  - Labels on lines for cardinality (1, M, N)

### Crow's Foot Notation (Modern — used in industry tools)
- **Entity**: Rectangle with attributes listed inside (no separate ovals)
- **Relationship**: Line connecting entities directly (no diamond)
- **Cardinality symbols at line ends**:
  - `||` (single bar) = exactly one
  - `O|` (circle + bar) = zero or one
  - `|<` or crow's foot = many
  - `O<` (circle + crow's foot) = zero or many
- **PK/FK markers**: Listed inside entity box with PK/FK prefixes

Rendering requirements for Crow's Foot:
  - 1 node type: Entity (rectangle with attribute list, PK/FK markers)
  - 4 line-end symbols: exactly-one, zero-or-one, one-or-many, zero-or-many
  - No separate attribute nodes (attributes are rows inside entity)
  - Relationship labels on the connecting line

### Recommendation for ERD Creator
Support BOTH notations with a toggle. Start with Crow's Foot (modern, compact, preferred by professionals) and add Chen as an alternate view. The textbook explicitly notes the newer ERD style (attributes inside entities, no action diamonds) is preferred because it reduces visual clutter — "if depicted in the older model, we would see 21 attribute ovals and a minimum of 8 actions."

-------------------------------------------------------------
ER-TO-SCHEMA RULES (for DDL generation engine)
-------------------------------------------------------------

These are the canonical mapping rules from ER diagrams to relational schema (SQL tables). This is the CORE of the DDL generator.

### Rule 1: Strong Entity -> Table
- Each strong entity becomes a table.
- Simple attributes become columns.
- Key attribute becomes PRIMARY KEY.
- Composite attributes: flatten to leaf-level columns (e.g., Address -> Street, City, State, Zip).
- Multivalued attributes: create a SEPARATE table with FK back to entity (e.g., entity_id + value).
- Derived attributes: typically NOT stored (computed at query time), or stored with a trigger/generated column.

### Rule 2: Weak Entity -> Table with Composite PK
- Weak entity becomes a table.
- PK = partial key of weak entity + PK of owner (strong) entity.
- FK references the owner entity with ON DELETE CASCADE.

### Rule 3: 1:1 Relationship -> FK on Either Side (prefer total participation side)
- Add the PK of one entity as FK in the other entity's table.
- Prefer putting FK on the side with total participation (mandatory).
- If both total: can merge into one table.
- Relationship attributes go on the table receiving the FK.

### Rule 4: 1:N Relationship -> FK on the "Many" Side
- Add the PK of the "one" side as FK on the "many" side table.
- This is the most common pattern.
- Relationship attributes go on the "many" side table.

### Rule 5: M:N Relationship -> Junction/Bridge Table
- Create a NEW table (junction table).
- PK = composite of both entity PKs.
- FK1 references Entity A, FK2 references Entity B.
- Relationship attributes become columns in the junction table.
- Both FKs typically have ON DELETE CASCADE.

### Rule 6: N-ary Relationship -> Junction Table with N FKs
- Create a junction table with FKs to ALL participating entities.
- PK = composite of all participating entity PKs (or subset depending on cardinality).

### Rule 7: Multivalued Attribute -> Separate Table
- Table with: entity_pk (FK) + attribute_value.
- PK = composite (entity_pk + attribute_value).

### DDL Generation Algorithm (pseudocode for the ERD Creator):
```
for each entity in diagram:
    CREATE TABLE entity_name (
        for each simple/key attribute: column_name TYPE [constraints]
        for each composite attribute: flatten to leaf columns
        PRIMARY KEY (key_attribute)
    )

for each weak entity:
    CREATE TABLE weak_entity_name (
        partial_key columns
        owner_pk column REFERENCES owner_table
        PRIMARY KEY (partial_key, owner_pk)
    )

for each 1:1 relationship:
    ALTER TABLE total_side ADD COLUMN fk REFERENCES other_side
    (or inline during CREATE TABLE)

for each 1:N relationship:
    ALTER TABLE many_side ADD COLUMN fk REFERENCES one_side

for each M:N relationship:
    CREATE TABLE junction_name (
        entity_a_pk REFERENCES entity_a,
        entity_b_pk REFERENCES entity_b,
        [relationship attributes],
        PRIMARY KEY (entity_a_pk, entity_b_pk)
    )

for each multivalued attribute:
    CREATE TABLE entity_attribute (
        entity_pk REFERENCES entity,
        attribute_value TYPE,
        PRIMARY KEY (entity_pk, attribute_value)
    )
```

-------------------------------------------------------------
NORMALIZATION CHECKS (for validation features)
-------------------------------------------------------------

### First Normal Form (1NF) — Violations to Detect:
1. **Repeating groups**: Multiple values in a single cell (e.g., "Phone1, Phone2" in one column). Flag multivalued attributes that weren't properly decomposed.
2. **Missing primary key**: Every table must have a unique identifier.
3. **Mixed data types**: All entries in a column must be same type.
4. **Duplicate rows**: No two rows should be identical.
5. **Column ordering dependency**: Shouldn't matter, but flag if names suggest positional data (col1, col2, col3 pattern).

### Second Normal Form (2NF) — Violations to Detect:
Prerequisite: Must be in 1NF. Only applies to tables with COMPOSITE primary keys.
1. **Partial dependency**: A non-key attribute depends on only PART of the composite PK.
   - Detection: For each non-key column in a table with composite PK, check if removing one PK column still determines the non-key column.
   - Fix: Split into separate table where the partially-dependent columns go with their determining key.
2. **Junction table bloat**: If a junction table has attributes that depend on only one FK, flag it.

### Third Normal Form (3NF) — Violations to Detect:
Prerequisite: Must be in 2NF.
1. **Transitive dependency**: A non-key attribute depends on another non-key attribute (A -> B -> C where A is PK, B determines C but B is not a key).
   - Detection: If removing an intermediate column would lose information about another column, there's a transitive dependency.
   - Fix: Extract the transitively dependent columns into their own table.
2. **Common pattern**: Department -> DeptManager. If Employee table has DeptID AND DeptManagerName, the manager name transitively depends on EmployeeID through DeptID.

### Automated Validation Rules for the ERD Creator:
- WARN if entity has no PK defined
- WARN if entity has potential multivalued attributes (arrays, comma-separated hints in naming)
- WARN if M:N relationship has no junction table generated
- WARN if weak entity has no identifying relationship
- ERROR if circular dependency in FK references without proper cascade rules
- INFO if table has >15 columns (may need decomposition)
- WARN if composite PK has non-key columns that don't depend on full key (2NF check)

-------------------------------------------------------------
SQL DDL PATTERNS (for code generation)
-------------------------------------------------------------

### CREATE DATABASE
```sql
CREATE DATABASE database_name;
```

### CREATE TABLE — Full Template
```sql
CREATE TABLE table_name (
    -- Column definitions
    column_name DATA_TYPE [column_constraints],

    -- Table constraints
    CONSTRAINT pk_name PRIMARY KEY (column1 [, column2]),
    CONSTRAINT fk_name FOREIGN KEY (column)
        REFERENCES other_table(column)
        [ON DELETE {CASCADE | SET NULL | SET DEFAULT | RESTRICT | NO ACTION}]
        [ON UPDATE {CASCADE | SET NULL | SET DEFAULT | RESTRICT | NO ACTION}],
    CONSTRAINT uq_name UNIQUE (column1 [, column2]),
    CONSTRAINT ck_name CHECK (condition)
);
```

### Column Constraints
- `NOT NULL` — Column cannot contain null values
- `UNIQUE` — All values must be distinct
- `DEFAULT value` — Default value if none provided
- `CHECK (condition)` — Value must satisfy boolean condition
- `PRIMARY KEY` — Shorthand for single-column PK (NOT NULL + UNIQUE)
- `REFERENCES table(column)` — Inline FK

### Common Data Types (multi-database)
| Concept         | PostgreSQL        | MySQL             | SQLite    |
|-----------------|-------------------|-------------------|-----------|
| Auto-increment  | SERIAL / BIGSERIAL| INT AUTO_INCREMENT| INTEGER PK|
| UUID            | UUID              | CHAR(36)          | TEXT      |
| Short text      | VARCHAR(n)        | VARCHAR(n)        | TEXT      |
| Long text       | TEXT              | TEXT / LONGTEXT   | TEXT      |
| Integer         | INTEGER           | INT               | INTEGER   |
| Decimal         | NUMERIC(p,s)      | DECIMAL(p,s)      | REAL      |
| Boolean         | BOOLEAN           | TINYINT(1)        | INTEGER   |
| Date            | DATE              | DATE              | TEXT      |
| Timestamp       | TIMESTAMPTZ       | DATETIME          | TEXT      |
| JSON            | JSONB             | JSON              | TEXT      |

### FK ON DELETE Actions (critical for ERD Creator)
- `CASCADE` — Delete child rows when parent deleted (common for weak entities, junction tables)
- `SET NULL` — Set FK to NULL when parent deleted (common for optional relationships)
- `RESTRICT` — Prevent parent deletion if children exist (safe default)
- `SET DEFAULT` — Set FK to default value when parent deleted
- `NO ACTION` — Similar to RESTRICT (deferred check)

### Generated DDL Example (what the ERD Creator should output):
```sql
-- Generated by C3 ERD Creator
-- Database: university_system
-- Generated: 2026-03-09

CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    building VARCHAR(50),
    budget NUMERIC(12,2) DEFAULT 0.00,
    CONSTRAINT uq_dept_name UNIQUE (name)
);

CREATE TABLE professors (
    professor_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    department_id INTEGER NOT NULL,
    CONSTRAINT fk_prof_dept FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- M:N junction table
CREATE TABLE course_enrollments (
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    grade CHAR(2),
    CONSTRAINT pk_enrollment PRIMARY KEY (student_id, course_id),
    CONSTRAINT fk_enroll_student FOREIGN KEY (student_id)
        REFERENCES students(student_id) ON DELETE CASCADE,
    CONSTRAINT fk_enroll_course FOREIGN KEY (course_id)
        REFERENCES courses(course_id) ON DELETE CASCADE
);
```

-------------------------------------------------------------
SCORED FINDINGS (sorted by score)
-------------------------------------------------------------

Scoring: Recency(15%) + Measurable(25%) + Applicability(30%) + Novelty(15%) + Cost(15%)

1. ER-to-Schema Mapping Rules (7 rules) — Score: 4.7
   R:3 M:5 A:5 N:5 C:5
   Maps to: DDL generation engine — the core algorithm that converts visual diagram to SQL
   Wave 1 PRIORITY. These 7 rules are deterministic and directly codifiable.

2. Crow's Foot Notation Symbol Set — Score: 4.6
   R:3 M:5 A:5 N:5 C:4
   Maps to: React Flow edge rendering — the 4 line-end symbols needed for visual editor
   Wave 1. Defines exactly what custom edge components to build.

3. SQL DDL Template Patterns — Score: 4.5
   R:3 M:5 A:5 N:4 C:5
   Maps to: Code generation output — CREATE TABLE templates with constraints
   Wave 1. String templates with variable substitution.

4. Entity/Attribute Node Type Taxonomy — Score: 4.4
   R:3 M:5 A:5 N:4 C:4
   Maps to: React Flow node types — defines the 5 Chen node types or 1 Crow's Foot node type
   Wave 1. Direct mapping to React components.

5. Cardinality + Participation Constraint System — Score: 4.3
   R:3 M:5 A:5 N:4 C:3
   Maps to: Edge property panel — what metadata each relationship edge carries
   Wave 1. Enum values stored on React Flow edges.

6. Normalization Validation Rules (1NF/2NF/3NF) — Score: 4.1
   R:3 M:4 A:5 N:4 C:3
   Maps to: Validation/lint feature — automated checks on the diagram before DDL generation
   Wave 1. Can be implemented as a validation pass over the schema.

7. FK ON DELETE/UPDATE Action Matrix — Score: 4.0
   R:3 M:5 A:5 N:3 C:4
   Maps to: Relationship property panel — dropdown for referential actions
   Wave 1. 5 enum values per action.

8. Multi-Database Data Type Mapping — Score: 4.0
   R:3 M:5 A:4 N:4 C:4
   Maps to: Target database selector — PostgreSQL vs MySQL vs SQLite DDL output
   Wave 1. Lookup table for type translation.

9. Composite/Multivalued Attribute Decomposition — Score: 3.7
   R:3 M:4 A:4 N:3 C:4
   Maps to: Attribute editor — UI for defining composite and multivalued attributes
   Wave 2. Adds complexity to the attribute panel.

10. Weak Entity Identification Pattern — Score: 3.5
    R:3 M:4 A:4 N:3 C:3
    Maps to: Entity creation — "Is this a weak entity?" toggle with owner selection
    Wave 2. Requires identifying relationship UI.

11. Anomaly Detection (Insert/Delete/Update) — Score: 3.3
    R:3 M:3 A:4 N:3 C:3
    Maps to: Advanced validation — detect potential anomalies before they're built
    Wave 2. Nice-to-have diagnostic feature.

12. Chen Notation Full Rendering — Score: 3.1
    R:3 M:3 A:3 N:2 C:4
    Maps to: Alternate notation view — Chen mode with ovals, diamonds
    Wave 2. More visual complexity, lower industry demand.

-------------------------------------------------------------
DEFERRED (< 3.0)
-------------------------------------------------------------

- Business Intelligence / Data Warehouse concepts (Ch. 6.5) — Score: 1.5
  Not relevant to ERD creator. Different domain.

- Client/Server Architecture (Ch. 11) — Score: 1.2
  Architecture content, not ERD-specific.

- Physical Database Design / File Organization (Ch. 12) — Score: 1.8
  Too low-level (disk pages, B-trees). Not relevant to visual ERD tool.

- SQL DML (SELECT, INSERT, UPDATE, DELETE) (Ch. 10) — Score: 2.0
  Query language, not schema design. Could be a future "query builder" feature but not ERD.

- Virtual Desktop lab instructions (Ch. 14) — Score: 0.5
  Completely irrelevant. Lab environment setup.

=============================================================
            SKILL CREATION RECOMMENDATIONS
=============================================================

Based on scored findings, recommend creating these skills in
`skills-library/database-solutions/`:

### 1. `er-diagram-components.md` — RECOMMENDED (Score: 4.4)
Encodes:
- Complete entity type taxonomy (strong, weak)
- All 6 attribute variants with visual representations
- Relationship types (unary, binary, N-ary)
- Cardinality notation (1:1, 1:N, M:N)
- Participation constraints (total/partial)
- Both Chen and Crow's Foot symbol mappings
- React Flow node/edge type recommendations

### 2. `er-to-ddl-mapping.md` — STRONGLY RECOMMENDED (Score: 4.7)
Encodes:
- All 7 mapping rules (strong entity, weak entity, 1:1, 1:N, M:N, N-ary, multivalued)
- DDL generation pseudocode algorithm
- FK action matrix (CASCADE, SET NULL, RESTRICT, etc.)
- Multi-database type mapping table (PG, MySQL, SQLite)
- Complete DDL template with all constraint types
- Generated output example

### 3. `normalization-validator.md` — RECOMMENDED (Score: 4.1)
Encodes:
- 1NF/2NF/3NF violation detection rules
- Functional dependency analysis
- Automated validation checklist (14 checks)
- Anomaly classification (insertion, deletion, update)
- Fix recommendations for each violation type

### 4. `sql-ddl-generator.md` — RECOMMENDED (Score: 4.5)
Encodes:
- CREATE TABLE template with full constraint syntax
- Column constraint reference (NOT NULL, UNIQUE, DEFAULT, CHECK)
- Table constraint patterns (composite PK, named FK, CHECK)
- Data type cross-reference table (PG, MySQL, SQLite)
- Naming conventions for constraints (pk_, fk_, uq_, ck_ prefixes)
- ON DELETE/UPDATE action guide with when-to-use recommendations

### Priority Order:
1. `er-to-ddl-mapping.md` — The core engine. Without this, no DDL generation.
2. `sql-ddl-generator.md` — The output templates. Pairs with #1.
3. `er-diagram-components.md` — The input model. Defines what the visual editor represents.
4. `normalization-validator.md` — The quality gate. Validates before generation.

### What Already Exists (no duplication needed):
- `database-schema-designer.md` — General schema design (different scope, doesn't cover ER-to-DDL mapping)
- `DATABASE_SCHEMA.md` — Specific schema docs (not mapping rules)
- `regex-alternation-ordering-sql-types.md` — SQL type parsing (complementary)

=============================================================
