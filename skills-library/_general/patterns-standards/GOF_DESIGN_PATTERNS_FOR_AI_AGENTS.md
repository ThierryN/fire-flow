---
name: GOF_DESIGN_PATTERNS_FOR_AI_AGENTS
category: patterns-standards
version: 1.0.0
contributed: 2026-03-06
contributor: dominion-flow
last_updated: 2026-03-06
tags: [design-patterns, gof, gang-of-four, agent-architecture, refactoring-guru, software-engineering]
difficulty: hard
usage_count: 0
success_rate: 100
---

# GoF Design Patterns for AI Agent Architecture

## Problem

AI agent systems reinvent classical software engineering patterns without recognizing them. This leads to:
- **Fragile orchestration** — ad-hoc coordination between agents instead of proven structural patterns
- **Monolithic agents** — single agents doing everything instead of composable, single-responsibility components
- **Brittle error handling** — retry-everything approaches instead of classified, pattern-appropriate recovery
- **Undocumented architecture** — no shared vocabulary to describe why an agent system is structured the way it is

The Gang of Four (GoF) design patterns — 22 patterns across Creational, Structural, and Behavioral categories — provide a battle-tested vocabulary and implementation guide. Most AI agent architectures already use these patterns implicitly. Making them explicit improves communication, extensibility, and debugging.

## Solution Pattern

Map each GoF pattern to its AI agent equivalent. Use the classical pattern name when discussing architecture. This gives every agent developer a shared vocabulary backed by 30+ years of software engineering validation.

### Reference: https://refactoring.guru/design-patterns

---

## Creational Patterns — How Agents Are Born

### 1. Factory Method → Agent Spawning

**Classical:** Define an interface for creating objects; let subclasses decide which class to instantiate.

**AI Agent equivalent:** Commands (`/fire-2-plan`, `/fire-3-execute`) decide WHICH agent to spawn based on context. The command is the factory — it reads the project state and instantiates the right agent type.

```
/fire-3-execute → reads BLUEPRINT → spawns fire-executor
/fire-debug     → reads error type → spawns fire-researcher OR fire-executor
/fire-autonomous → reads phase     → spawns planner, executor, OR verifier per step
```

**When to use:** When the agent type needed depends on runtime context (project state, error type, phase).

### 2. Abstract Factory → Agent Family Selection

**Classical:** Create families of related objects without specifying concrete classes.

**AI Agent equivalent:** Stack selection in `/fire-1-new` produces a coherent FAMILY of tools, patterns, and skills. Choosing "MERN stack" selects MongoDB skills + Express patterns + React frontend + Node backend — a compatible family. Choosing "Django stack" selects a different family.

**When to use:** When selecting one technology implies a whole family of related decisions (database, ORM, auth, hosting).

### 3. Builder → BLUEPRINT Construction

**Classical:** Separate construction of a complex object from its representation.

**AI Agent equivalent:** The fire-planner builds BLUEPRINTs step by step — first scope manifest, then risk register, then tasks, then kill conditions. Each step adds a layer. The final BLUEPRINT is complex, but construction is orderly.

```
Step 1: Define scope (allowed_files, forbidden operations)
Step 2: Define risks (risk_register with mitigations)
Step 3: Define tasks (ordered, with dependencies)
Step 4: Define exit criteria (kill_conditions, wake_conditions)
→ Result: Complete BLUEPRINT.md
```

**When to use:** When the plan/configuration object has many optional parts that should be assembled in stages.

### 4. Prototype → Context Cloning for Fresh Agents

**Classical:** Create new objects by copying an existing object.

**AI Agent equivalent:** Context rotation — when a stuck agent spawns a fresh agent, it clones the ESSENTIAL context (dead-end map, constraints, goal) without the fixation baggage. The fresh agent is a "prototype" of the original but with clean working memory.

**When to use:** When functional fixedness sets in and a fresh perspective needs the same problem context without accumulated bias.

### 5. Singleton → Shared State Files

**Classical:** Ensure a class has only one instance with global access.

**AI Agent equivalent:** Files like `CONSCIENCE.md`, `VISION.md`, and `FAILURES.md` are singletons — one per project, globally readable, updated by any agent. They prevent inconsistent state from multiple agents maintaining separate copies.

**When to use:** For project-level state that ALL agents must see the same version of (roadmap, progress, known failures).

---

## Structural Patterns — How Agents Compose

### 6. Adapter → Skill-to-Agent Translation

**Classical:** Convert one interface to another that clients expect.

**AI Agent equivalent:** The skills library contains patterns in a universal format. Each agent ADAPTS the skill's guidance into its own step format. The same CIRCUIT_BREAKER_INTELLIGENCE skill becomes Step 3.5 in executor (runtime classification) and anti-pattern #8 in planner (plan-time kill conditions).

**When to use:** When a reusable pattern needs to be expressed differently for different agents.

### 7. Bridge → Agent/Tool Separation

**Classical:** Decouple abstraction from implementation.

**AI Agent equivalent:** Agents define WHAT to do (abstraction); tools define HOW (implementation). fire-executor says "run tests" — whether that's `npm test`, `pytest`, or `cargo test` depends on the project. The agent's logic is independent of the tool implementation.

**When to use:** When agent logic should work across different tech stacks without modification.

### 8. Composite → Phase/Task Tree

**Classical:** Compose objects into tree structures for part-whole hierarchies.

**AI Agent equivalent:** VISION.md contains phases. Each phase contains BLUEPRINTs. Each BLUEPRINT contains tasks. Each task contains sub-steps. The same operations (execute, verify, report) apply at every level — you can verify a task, a plan, a phase, or the whole project.

```
Project (VISION.md)
├── Phase 1
│   ├── BLUEPRINT 1-1
│   │   ├── Task 1
│   │   └── Task 2
│   └── BLUEPRINT 1-2
├── Phase 2
└── Phase 3
```

**When to use:** When work has a natural tree structure and operations should apply uniformly at any level.

### 9. Decorator → Additive Agent Enhancements (v12.0 Pattern)

**Classical:** Attach additional responsibilities dynamically without modifying existing code.

**AI Agent equivalent:** v12.0 added new steps BETWEEN existing steps (Step 2.5, Step 3.5, Step 3.7) without changing existing step numbers or behavior. Each new step "decorates" the existing flow with additional capability (DoR check, circuit breaker, implied scenarios).

```
Original:  Step 2 → Step 3 → Step 4
Decorated: Step 2 → [2.5: DoR] → [2.7: Scope] → Step 3 → [3.5: Circuit Breaker] → [3.7: Implied Scenarios] → Step 4
```

**When to use:** When extending agent behavior without breaking backward compatibility. The Decorator pattern is why v12.0 was additive, not destructive.

### 10. Facade → OVERVIEW.md

**Classical:** Provide a simplified interface to a complex subsystem.

**AI Agent equivalent:** DOMINION-FLOW-OVERVIEW.md is a facade — it presents the complete system (45 commands, 14 agents, 484+ skills) through a single navigable document. New agents read the OVERVIEW to understand the system without needing to read every individual file.

**When to use:** When the system has grown complex enough that newcomers need an entry point.

### 11. Flyweight → Shared Skills Library

**Classical:** Share common state across many objects to save memory.

**AI Agent equivalent:** Skills are flyweights — stored once in the skills library, referenced by many agents. Instead of each agent containing its own copy of "how to handle circuit breakers," all agents reference the single CIRCUIT_BREAKER_INTELLIGENCE skill.

**When to use:** When multiple agents need the same knowledge. Store it once, reference everywhere.

### 12. Proxy → Scope Manifest

**Classical:** Provide a surrogate to control access to another object.

**AI Agent equivalent:** The scope manifest acts as a proxy for filesystem access. Instead of letting the executor touch any file, the scope manifest controls which files can be read, written, or deleted. It's a protection proxy that enforces boundaries defined at plan time.

```yaml
scope:
  allowed_files: [src/auth/*, src/middleware/*]
  forbidden: [.env, package.json, database/migrations/*]
  max_file_changes: 8
```

**When to use:** When agent access to resources (files, APIs, databases) needs to be bounded per-task.

---

## Behavioral Patterns — How Agents Collaborate

### 13. Chain of Responsibility → Tiered Verification

**Classical:** Pass requests along a chain of handlers until one handles it.

**AI Agent equivalent:** Verification flows through a chain: Tier 1 Fast Gate → Tier 2 Must-Haves → Tier 3 WARRIOR 70-point. Each tier decides whether to handle (reject) or pass to the next tier. If Tier 1 catches a build failure, Tier 2 and 3 never run.

```
Code → [Tier 1: Build/Types/Lint] → FAIL? Stop.
                                   → PASS? → [Tier 2: Must-Haves] → FAIL? Stop.
                                                                    → PASS? → [Tier 3: WARRIOR] → Score
```

**When to use:** When validation has multiple levels of expense and most failures are caught by cheap checks. Shift-left principle.

### 14. Command → BLUEPRINT Tasks

**Classical:** Encapsulate a request as an object.

**AI Agent equivalent:** Each task in a BLUEPRINT is a Command object — it has a description, preconditions (dependencies), expected output, risk level, and can be executed, undone (git revert), or queued. Tasks are first-class entities, not inline instructions.

**When to use:** When work units need to be queued, logged, retried, or undone independently.

### 15. Iterator → Breath-Based Execution

**Classical:** Access elements sequentially without exposing the underlying structure.

**AI Agent equivalent:** The breath pattern iterates over tasks without exposing the full plan complexity. Each breath gets 2-4 tasks. The executor doesn't see the entire remaining plan — just the current breath. This prevents overwhelm and maintains focus.

**When to use:** When the full task list would overwhelm context. Feed work in digestible chunks.

### 16. Mediator → fire-autonomous Orchestrator

**Classical:** Define an object that encapsulates how objects interact.

**AI Agent equivalent:** `/fire-autonomous` mediates between planner, executor, and verifier. None of these agents talk to each other directly — autonomous mode reads their outputs and decides what happens next (re-plan, advance, escalate).

**When to use:** When multiple agents need coordination but shouldn't be coupled to each other.

### 17. Memento → WARRIOR Handoffs

**Classical:** Capture and externalize object state for later restoration.

**AI Agent equivalent:** WARRIOR handoffs capture the full session state (files changed, decisions made, blockers hit, phase position) so a new Claude instance can restore context without re-discovering everything. The handoff IS a memento.

**When to use:** When agent sessions end and the next session needs to resume from the same state. Context preservation across the session boundary.

### 18. Observer → Cross-Agent Learning

**Classical:** When one object changes, all dependents are notified.

**AI Agent equivalent:** When any agent discovers a lesson, failure, pattern, or dependency, it records it in shared project state. All subsequent agents read this state on startup — they're "notified" of changes through the file system.

**When to use:** When discoveries by one agent should influence all future agents without explicit coupling.

### 19. State → Circuit Breaker States

**Classical:** Allow an object to alter its behavior when its state changes.

**AI Agent equivalent:** The circuit breaker has three states — CLOSED (normal execution), OPEN (stop, research alternatives), HALF-OPEN (probe with limited scope). The executor's behavior changes completely based on which state it's in. Same agent, different behavior.

```
CLOSED  → execute tasks normally, count errors
OPEN    → stop execution, route to research
HALF-OPEN → try researched alternative with guardrails
```

**When to use:** When an agent needs fundamentally different behavior based on accumulated failure state.

### 20. Strategy → Stuck-State Interventions

**Classical:** Define a family of algorithms and make them interchangeable.

**AI Agent equivalent:** The 6 stuck-state types each have a STRATEGY for intervention. TRANSIENT → retry. FIXATION → context rotation. DEAD_END → shelf with wake conditions. The classification determines which strategy runs. All strategies share the same interface (input: stuck state, output: next action).

| Stuck Type | Strategy |
|------------|----------|
| TRANSIENT | Retry (up to 2x) |
| FIXATION | Context rotation |
| CONTEXT_OVERFLOW | Compact + checkpoint |
| SEMANTIC | Re-read requirements |
| DEAD_END | Shelf with wake conditions |
| SCOPE_DRIFT | Re-read scope manifest |

**When to use:** When the same problem category has multiple valid solutions and the right one depends on classification.

### 21. Template Method → Agent Lifecycle

**Classical:** Define the skeleton of an algorithm; let subclasses override specific steps.

**AI Agent equivalent:** Every Dominion Flow agent follows the same skeleton: Load context → Validate prerequisites → Execute core work → Write results → Report verdict. The SKELETON is fixed. Each agent type overrides the "core work" step — planner creates BLUEPRINTs, executor runs tasks, verifier checks results.

```
Template:
  1. Load context (VISION, CONSCIENCE, project state)   ← fixed
  2. Validate prerequisites (path, phase, DoR)          ← fixed
  3. [OVERRIDE: Core work]                              ← varies by agent
  4. Write artifacts (BLUEPRINT/RECORD/VERIFICATION)    ← fixed
  5. Report verdict                                     ← fixed
```

**When to use:** When all agents share the same lifecycle but differ in their core operation.

### 22. Visitor → Multi-Perspective Code Review

**Classical:** Perform operations on elements of a structure without changing the structure.

**AI Agent equivalent:** The fire-reviewer visits code from 15 different perspectives (Performance Auditor, Security Analyst, UX Champion, etc.) without modifying the code. Each perspective is a "visitor" that examines the same code and produces findings. The code structure doesn't change — only the analysis accumulates.

**When to use:** When the same artifact needs evaluation from multiple independent perspectives.

---

## Quick Reference Matrix

| Pattern | GoF Category | Agent Equivalent | Dominion Flow Example |
|---------|-------------|-----------------|----------------------|
| Factory Method | Creational | Agent spawning | Commands spawn agents by context |
| Abstract Factory | Creational | Stack family selection | `/fire-1-new` stack choice |
| Builder | Creational | BLUEPRINT construction | fire-planner step-by-step |
| Prototype | Creational | Context cloning | Context rotation fresh agent |
| Singleton | Creational | Shared state files | CONSCIENCE.md, VISION.md |
| Adapter | Structural | Skill-to-agent translation | Skills → agent steps |
| Bridge | Structural | Agent/tool separation | "run tests" → npm/pytest/cargo |
| Composite | Structural | Phase/task tree | Project → Phase → Plan → Task |
| Decorator | Structural | Additive enhancements | v12.0 interleaved steps |
| Facade | Structural | System overview | OVERVIEW.md |
| Flyweight | Structural | Shared skills | Skills library |
| Proxy | Structural | Scope manifest | Filesystem access control |
| Chain of Resp. | Behavioral | Tiered verification | Tier 1 → 2 → 3 |
| Command | Behavioral | BLUEPRINT tasks | Encapsulated work units |
| Iterator | Behavioral | Breath-based execution | 2-4 tasks per breath |
| Mediator | Behavioral | Autonomous orchestrator | fire-autonomous |
| Memento | Behavioral | WARRIOR handoffs | Session state capture |
| Observer | Behavioral | Cross-agent learning | Shared project state |
| State | Behavioral | Circuit breaker | CLOSED/OPEN/HALF-OPEN |
| Strategy | Behavioral | Stuck interventions | 6 types × 6 strategies |
| Template Method | Behavioral | Agent lifecycle | Load → Validate → Work → Write → Report |
| Visitor | Behavioral | Multi-perspective review | 15-persona code review |

---

## When to Use

- **Architecture discussions** — Use GoF names as shared vocabulary ("the verification chain of responsibility" is clearer than "the thing that checks stuff in order")
- **Extending Dominion Flow** — Before adding a feature, check which GoF pattern it maps to. If none, question whether the feature is structurally sound.
- **Debugging agent behavior** — Pattern violations indicate bugs ("the mediator is bypassed" → agents talking directly instead of through autonomous mode)
- **Onboarding** — Developers who know GoF patterns instantly understand Dominion Flow's architecture through this mapping
- **New agent system design** — Use this as a checklist: which patterns does your system use? Which is it missing?

## When NOT to Use

- **Simple scripts** — A single-agent, single-task script doesn't need pattern awareness
- **Pattern forcing** — Don't retrofit patterns onto things that work fine without them
- **Over-abstraction** — Recognizing patterns ≠ creating abstract base classes. AI agents are text-configured, not class-hierarchied

## Common Mistakes

- **Confusing Strategy with State** — Strategy = choosing an algorithm. State = changing behavior based on accumulated state. Stuck-type classification is Strategy. Circuit breaker is State.
- **Skipping Facade** — Systems without an OVERVIEW doc force every new agent to read everything. Add a facade early.
- **Missing Observer** — If agent discoveries die with the session, you have no Observer pattern. Add shared state files.

## Related Skills

- [CIRCUIT_BREAKER_INTELLIGENCE](../methodology/CIRCUIT_BREAKER_INTELLIGENCE.md) — State + Strategy patterns in depth
- [AUTONOMOUS_ORCHESTRATION](../methodology/AUTONOMOUS_ORCHESTRATION.md) — Mediator + Template Method patterns
- [CONTEXT_ROTATION](../methodology/CONTEXT_ROTATION.md) — Prototype pattern for fresh agents
- [QUALITY_GATES_AND_VERIFICATION](../methodology/QUALITY_GATES_AND_VERIFICATION.md) — Chain of Responsibility
- [MULTI_PERSPECTIVE_CODE_REVIEW](../methodology/MULTI_PERSPECTIVE_CODE_REVIEW.md) — Visitor pattern
- [RELIABILITY_PREDICTION](../methodology/RELIABILITY_PREDICTION.md) — Observer pattern (implied scenarios)

## References

- https://refactoring.guru/design-patterns — Complete GoF pattern catalog with visual examples
- Gamma, Helm, Johnson, Vlissides — *Design Patterns: Elements of Reusable Object-Oriented Software* (1994)
- Contributed from: Dominion Flow v12.0 session (2026-03-06)

## When Agents Should Reference This Skill

- **fire-planner:** When designing new agent workflows or extending existing ones — ensure structural patterns are used intentionally
- **fire-researcher:** When evaluating architecture approaches — check if they align with established patterns
- **fire-reviewer:** When reviewing agent code — flag pattern violations (bypassed mediator, missing facade, coupled agents)
- **fire-vision-architect:** When proposing architecture branches — name the patterns each branch relies on
