# Integration Architecture

> System design overview for Dominion Flow Architecture

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DOMINION FLOW PLUGIN                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         DOMINION FLOW SHELL                                    │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │ Commands Layer                                                │   │   │
│  │  │  /fire-plan  /fire-execute  /fire-verify  /fire-progress │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                       │   │
│  │                              ▼                                       │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │ Workflow Orchestration                                        │   │   │
│  │  │  • Phase management                                           │   │   │
│  │  │  • Breath-based execution                                       │   │   │
│  │  │  • Parallel agent spawning                                    │   │   │
│  │  │  • Progress tracking                                          │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                       │   │
│  │                              ▼                                       │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │ State Management                                              │   │   │
│  │  │  • CONSCIENCE.md (living memory)                                   │   │   │
│  │  │  • VISION.md (phase planning)                                │   │   │
│  │  │  • BLUEPRINT.md (execution details)                                │   │   │
│  │  │  • RECORD.md (completion records)                            │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        WARRIOR CORE                                  │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │ Quality Enforcement                                           │   │   │
│  │  │  • Validation checklist (60+ items)                           │   │   │
│  │  │  • Honesty protocols (3 questions)                            │   │   │
│  │  │  • Pre-commit checks                                          │   │   │
│  │  │  • Production readiness gates                                 │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                       │   │
│  │                              ▼                                       │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │ Knowledge Layer                                               │   │   │
│  │  │  • Skills library                                             │   │   │
│  │  │  • Pattern references                                         │   │   │
│  │  │  • Implementation guides                                      │   │   │
│  │  │  • Domain expertise                                           │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                       │   │
│  │                              ▼                                       │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │ Session Continuity                                            │   │   │
│  │  │  • WARRIOR handoffs                                           │   │   │
│  │  │  • Context preservation                                       │   │   │
│  │  │  • Knowledge transfer                                         │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      INTEGRATION LAYER                               │   │
│  │                                                                      │   │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐              │   │
│  │   │  Hooks  │  │  Agents │  │Templates│  │  Tests  │              │   │
│  │   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘              │   │
│  │        │            │            │            │                    │   │
│  │        └────────────┴────────────┴────────────┘                    │   │
│  │                           │                                         │   │
│  │                           ▼                                         │   │
│  │              ┌────────────────────────────┐                        │   │
│  │              │    Claude Code Runtime     │                        │   │
│  │              └────────────────────────────┘                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Integration Points

| Integration Point | Source | Target | Purpose |
|-------------------|--------|--------|---------|
| Command Dispatch | Commands | Workflow Orchestration | Route user commands to appropriate handlers |
| State Read/Write | Workflow Orchestration | State Management | Persist and retrieve workflow state |
| Quality Gates | Workflow Orchestration | Quality Enforcement | Enforce standards at checkpoints |
| Skill Lookup | Workflow Orchestration | Knowledge Layer | Find relevant patterns during planning |
| Context Restore | Session Start | Session Continuity | Load previous session context |
| Context Save | Session End | Session Continuity | Preserve context for next session |
| Hook Triggers | Claude Code Runtime | Hooks | Execute hooks on tool use events |
| Agent Spawning | Workflow Orchestration | Agents | Launch parallel execution agents |
| Template Loading | Commands | Templates | Load planning templates |
| Test Validation | Quality Enforcement | Tests | Run validation test suites |

---

## Data Flow

### Planning Flow

```
User Request
     │
     ▼
┌─────────────────┐
│ /fire-plan     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Load CONSCIENCE.md   │────▶│ Current Context │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Search Skills   │────▶│ Relevant Guides │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Apply Honesty   │────▶│ Knowledge Gaps  │
│ Protocols       │     │ Identified      │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Generate BLUEPRINT.md│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Update CONSCIENCE.md │
└─────────────────┘
```

### Execution Flow

```
BLUEPRINT.md
   │
   ▼
┌─────────────────┐
│ /fire-execute  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Parse Breaths     │
└────────┬────────┘
         │
         ├──────────────────────────────┐
         ▼                              ▼
┌─────────────────┐          ┌─────────────────┐
│ Breath 1 Tasks    │          │ Breath 1 Tasks    │
│ (Agent 1)       │          │ (Agent 2)       │
└────────┬────────┘          └────────┬────────┘
         │                            │
         └──────────┬─────────────────┘
                    ▼
         ┌─────────────────┐
         │ Breath Checkpoint │
         │ (Quality Gate)  │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Update CONSCIENCE.md │
         │ (Progress)      │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Next Breath...    │
         └─────────────────┘
```

### Verification Flow

```
Implementation Complete
          │
          ▼
┌─────────────────────┐
│ /fire-verify       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Load Validation     │
│ Checklist           │
└──────────┬──────────┘
           │
           ├────────────────┬────────────────┬────────────────┐
           ▼                ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Code Quality │  │ Security     │  │ Performance  │  │ Testing      │
│ Checks       │  │ Checks       │  │ Checks       │  │ Checks       │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │                 │
       └─────────────────┴─────────────────┴─────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────┐
                    │ Aggregate Results   │
                    └──────────┬──────────┘
                               │
                  ┌────────────┴────────────┐
                  ▼                         ▼
         ┌──────────────┐         ┌──────────────┐
         │ ✓ All Pass   │         │ ✗ Failures   │
         │ → RECORD.md │         │ → Fix Items  │
         └──────────────┘         └──────────────┘
```

---

## File Relationships

### Core State Files

```
.planning/
├── PROJECT.md          # Project overview (rarely changes)
│   └── Referenced by: CONSCIENCE.md, VISION.md
│
├── CONSCIENCE.md            # Living memory (frequently updated)
│   ├── Updated by: All commands
│   ├── Read by: All commands
│   └── Contains: Current context, progress, blockers
│
├── VISION.md          # Phase definitions
│   ├── Updated by: /fire-plan
│   ├── Read by: /fire-execute, /fire-progress
│   └── Contains: All phases with status
│
└── phases/
    └── NN-phase-name/
        ├── NN-01-BLUEPRINT.md       # Execution plan
        │   ├── Created by: /fire-plan
        │   ├── Read by: /fire-execute
        │   └── Contains: Tasks, breaths, dependencies
        │
        ├── NN-01-RECORD.md    # Completion record
        │   ├── Created by: /fire-verify
        │   ├── Read by: Future sessions
        │   └── Contains: What was done, skills used
        │
        └── NN-01-EXECUTE.md    # Execution log (optional)
            ├── Updated by: /fire-execute
            └── Contains: Real-time progress
```

### Plugin Structure

```
dominion-flow/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
│
├── commands/
│   ├── power-plan.md         # Planning command
│   ├── power-execute.md      # Execution command
│   ├── power-verify.md       # Verification command
│   ├── power-progress.md     # Status command
│   ├── power-search.md       # Skill search
│   └── power-contribute.md   # Skill contribution
│
├── agents/
│   ├── planner.md            # Planning agent
│   ├── executor.md           # Execution agent
│   └── validator.md          # Validation agent
│
├── hooks/
│   ├── hooks.json            # Hook definitions
│   ├── pre-commit.sh         # Pre-commit validation
│   └── session-start.sh      # Context loading
│
├── templates/
│   ├── PLAN-TEMPLATE.md      # Plan document template
│   ├── SUMMARY-TEMPLATE.md   # Summary document template
│   └── STATE-TEMPLATE.md     # State document template
│
├── skills-library/           # Knowledge base
│   ├── methodology/
│   ├── security/
│   ├── database/
│   └── ...
│
├── references/               # This documentation
│   ├── ui-brand.md
│   ├── honesty-protocols.md
│   ├── validation-checklist.md
│   ├── skills-usage-guide.md
│   └── integration-architecture.md
│
├── workflows/
│   ├── standard-feature.md   # Standard feature workflow
│   ├── bug-fix.md           # Bug fix workflow
│   └── refactoring.md       # Refactoring workflow
│
└── tests/
    ├── command-tests/
    └── integration-tests/
```

---

## Component Responsibilities

### DOMINION FLOW SHELL Components

| Component | Responsibility | Key Files |
|-----------|----------------|-----------|
| **Commands Layer** | Parse user input, route to handlers | `commands/*.md` |
| **Workflow Orchestration** | Manage phases, breaths, parallel execution | `workflows/*.md` |
| **State Management** | Read/write planning documents | Uses `.planning/` |

### WARRIOR Core Components

> For the full explanation of WARRIOR principles and the 7-step handoff, see `references/warrior-principles.md`.

| Component | Responsibility | Key Files |
|-----------|----------------|-----------|
| **Operating Principles** | Radical honesty, goal-backward verification, quality gates | `references/warrior-principles.md` |
| **Quality Enforcement** | Apply validation checklist, gates | `references/validation-checklist.md` |
| **Knowledge Layer** | Skills search, pattern matching | `skills-library/` |
| **Session Continuity** | Handoffs, context preservation | Hooks, CONSCIENCE.md |

### Integration Layer Components

| Component | Responsibility | Key Files |
|-----------|----------------|-----------|
| **Hooks** | Event-triggered actions | `hooks/` |
| **Agents** | Specialized execution agents | `agents/` |
| **Templates** | Document scaffolding | `templates/` |
| **Tests** | Validation test suites | `tests/` |

---

## Event Flow

### Session Start

```
1. Claude Code starts
2. SessionStart hook fires
3. Load most recent WARRIOR handoff
4. Read CONSCIENCE.md for current context
5. Display progress summary
6. Ready for commands
```

### Command Execution

```
1. User issues command (e.g., /fire-plan)
2. Command file loaded
3. Prerequisites checked (CONSCIENCE.md exists, etc.)
4. Command logic executes
5. State files updated
6. UI feedback displayed
7. Next action suggested
```

### Agent Spawning

```
1. /fire-execute determines parallel tasks
2. Breath definition parsed
3. For each parallel task:
   a. Agent spawned with task context
   b. Agent executes independently
   c. Agent reports completion
4. Breath checkpoint reached
5. Quality gate applied
6. Next breath proceeds
```

### Session End

```
1. User signals end or context limit approaching
2. CONSCIENCE.md updated with current progress
3. WARRIOR handoff created
4. Handoff saved to warrior-handoffs/
5. Session terminates
```

---

## Extension Points

### Adding New Commands

1. Create `commands/new-command.md`
2. Define frontmatter (args, description)
3. Implement command logic
4. Add to relevant workflows

### Adding New Agents

1. Create `agents/new-agent.md`
2. Define agent role and capabilities
3. Set triggering conditions
4. Register in relevant commands

### Adding New Skills

1. Search existing skills first
2. Use `/fire-contribute` workflow
3. Follow skill template structure
4. Submit to skills library

### Adding New Hooks

1. Identify trigger event
2. Create hook script
3. Register in `hooks/hooks.json`
4. Test hook execution

---

## Dependency Graph

```
                    ┌─────────────┐
                    │ Claude Code │
                    │   Runtime   │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │   Hooks     │          │  Commands   │
       └──────┬──────┘          └──────┬──────┘
              │                        │
              │     ┌──────────────────┤
              │     ▼                  ▼
              │  ┌─────────────┐  ┌─────────────┐
              │  │   Agents    │  │  Workflows  │
              │  └──────┬──────┘  └──────┬──────┘
              │         │                │
              └─────────┼────────────────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
       ┌─────────────┐     ┌─────────────┐
       │  Templates  │     │   Skills    │
       └─────────────┘     │   Library   │
                           └─────────────┘
                                 │
                                 ▼
                          ┌─────────────┐
                          │ References  │
                          └─────────────┘
```

---

*Architecture evolves. Keep this document updated as components change.*
