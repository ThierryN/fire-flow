---
description: List and validate assumptions for a phase before planning or execution
---

# /fire-assumptions

> Surface Claude's assumptions about a phase approach before planning. Prevents silent improvisation.

---

## Arguments

```yaml
arguments:
  phase:
    required: false
    type: string
    description: "Phase to list assumptions for. Defaults to current phase."
```

---

## Process

### Step 1: Load Context

Read CONSCIENCE.md, VISION.md, and phase description.

### Step 2: Generate Assumptions

For the target phase, list all assumptions Claude is making:

```
+---------------------------------------------------------------+
|           DOMINION FLOW >>> ASSUMPTION VALIDATION                 |
+---------------------------------------------------------------+
|                                                                 |
|  Phase: 03 - Dashboard                                         |
|                                                                 |
|  Assumptions I'm making:                                       |
|                                                                 |
|  TECHNICAL:                                                    |
|  1. [VALIDATED] React 18+ is available (confirmed in pkg.json)|
|  2. [UNVALIDATED] WebSocket support in deployment target       |
|  3. [UNVALIDATED] Chart library compatible with SSR            |
|                                                                 |
|  INFRASTRUCTURE:                                               |
|  4. [VALIDATED] PostgreSQL is the database                     |
|  5. [UNVALIDATED] Redis available for real-time features       |
|                                                                 |
|  INTEGRATION:                                                  |
|  6. [UNVALIDATED] Stripe API supports batch operations         |
|                                                                 |
+-----------------------------------------------------------------+
```

### Step 3: Validate or Acknowledge

For each UNVALIDATED assumption:
- Can it be validated now? (check docs, test, research)
- If yes: validate and update status
- If no: acknowledge risk and document in ASSUMPTIONS.md

### Step 4: Update ASSUMPTIONS.md

Write validated/unvalidated assumptions to `.planning/ASSUMPTIONS.md`.

### Step 5: Route

If all critical assumptions validated: "Ready for `/fire-2-plan`"
If unvalidated critical assumptions: "Consider `/fire-research` before planning"

---

## References

- **Template:** `@templates/ASSUMPTIONS.md`
- **Questioning:** `@references/questioning.md`
