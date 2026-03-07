# Dominion Flow Plugin Test Suite

This directory contains the complete test suite for the Fire Flow plugin, validating all commands, integrations, and workflows.

---

## Directory Structure

```
tests/
├── README.md                    # This file
├── e2e/                         # End-to-end command tests
│   ├── new-project.test.md      # /fire-1-new
│   ├── plan-phase.test.md       # /fire-2-plan
│   ├── execute-phase.test.md    # /fire-3-execute
│   ├── verify-phase.test.md     # /fire-4-verify
│   ├── handoff.test.md          # /fire-5-handoff
│   ├── resume.test.md           # /fire-6-resume
│   ├── skills-search.test.md    # /fire-search
│   └── skills-contribute.test.md # /fire-contribute
├── integration/                 # Integration tests
│   ├── full-workflow.test.md    # Complete workflow test
│   ├── skills-sync.test.md      # Bidirectional skills sync
│   └── hooks.test.md            # SessionStart hook
└── fixtures/                    # Test data and expected outputs
    ├── test-project/            # Sample project structure
    │   └── .planning/
    │       ├── CONSCIENCE.md
    │       ├── VISION.md
    │       └── phases/
    │           └── 01-test-phase/
    │               └── 01-01-BLUEPRINT.md
    ├── test-skills/             # Sample skills
    │   └── database-solutions/
    │       └── test-skill.md
    ├── test-handoff/            # Sample handoff
    │   └── MY-PROJECT_2026-01-22.md
    └── expected-outputs/        # Validation templates
        ├── expected-conscience.md
        └── expected-verification.md
```

---

## Test Categories

### E2E Tests (`tests/e2e/`)

End-to-end tests that validate individual Dominion Flow commands work correctly in isolation.

| Test File | Command | What It Tests |
|-----------|---------|---------------|
| `new-project.test.md` | `/fire-1-new` | Project initialization, directory structure |
| `plan-phase.test.md` | `/fire-2-plan` | Phase planning, skills integration, breath organization |
| `execute-phase.test.md` | `/fire-3-execute` | Breath execution, task completion, artifact creation |
| `verify-phase.test.md` | `/fire-4-verify` | Verification checks, success criteria, reporting |
| `handoff.test.md` | `/fire-5-handoff` | Handoff creation, unified format, context capture |
| `resume.test.md` | `/fire-6-resume` | Context restoration, handoff loading |
| `skills-search.test.md` | `/fire-search` | Skills discovery, keyword matching |
| `skills-contribute.test.md` | `/fire-contribute` | Skills creation, formatting, categorization |

### Integration Tests (`tests/integration/`)

Tests that validate multiple components working together.

| Test File | What It Tests |
|-----------|---------------|
| `full-workflow.test.md` | Complete project lifecycle from init to completion |
| `skills-sync.test.md` | Bidirectional sync between Dominion Flow and WARRIOR skills |
| `hooks.test.md` | SessionStart hook firing and context injection |

### Fixtures (`tests/fixtures/`)

Static test data used by the test suite.

| Fixture | Purpose |
|---------|---------|
| `test-project/` | Pre-configured project structure for testing |
| `test-skills/` | Sample skill files for search/sync testing |
| `test-handoff/` | Sample handoff file for resume testing |
| `expected-outputs/` | Templates for validating generated outputs |

---

## Running Tests

### Manual Execution

Each test file is a markdown document with executable instructions. To run a test:

1. Open the test file
2. Follow the **Setup Steps** to prepare the environment
3. Follow the **Execute Steps** to run the commands
4. Follow the **Verify Steps** to check results
5. Follow the **Cleanup Steps** to restore state

### Example: Running `new-project.test.md`

```bash
# 1. Setup
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"
git init

# 2. Execute (in Claude Code)
/fire-1-new

# 3. Verify
[ -d ".planning" ] && echo "PASS" || echo "FAIL"
[ -f ".planning/CONSCIENCE.md" ] && echo "PASS" || echo "FAIL"

# 4. Cleanup
cd /
rm -rf "$TEST_DIR"
```

---

## Test Format

Each test file follows a consistent structure:

```markdown
# E2E/Integration Test: [Name]

## Test Name
[unique-identifier]

## Description
[What the test validates]

## Prerequisites
[Requirements before running]

## Setup Steps
[Commands to prepare test environment]

## Execute Steps
[Commands to run the test]

## Verify Steps
[Commands and checks to validate results]

## Cleanup Steps
[Commands to restore environment]

## Pass/Fail Criteria
[Table of required and optional criteria]

## Expected Result
[PASS/FAIL conditions]

## Test Variations
[Alternative scenarios to test]

## Known Issues
[Documented limitations]

## Related Tests
[Links to related tests]
```

---

## Fixtures Usage

### Using `test-project/`

```bash
# Copy fixture to temp directory
cp -r ~/.claude/plugins/fire-flow/tests/fixtures/test-project/.planning .

# Now you have a pre-configured project for testing
```

### Using `test-skills/`

```bash
# Skills are at:
~/.claude/plugins/fire-flow/tests/fixtures/test-skills/

# Copy to skills library for testing
cp -r fixtures/test-skills/* ~/.claude/plugins/fire-flow/skills-library/
```

### Using `expected-outputs/`

```bash
# Compare generated output against expected
diff .planning/CONSCIENCE.md fixtures/expected-outputs/expected-conscience.md

# Or use the validation scripts in expected-outputs files
```

---

## Adding New Tests

### E2E Test Template

1. Create file: `tests/e2e/[command-name].test.md`
2. Use the standard test format
3. Include all sections (setup, execute, verify, cleanup)
4. Add pass/fail criteria table
5. Document any known issues

### Integration Test Template

1. Create file: `tests/integration/[feature-name].test.md`
2. Test multiple commands/components together
3. Include workflow diagram if helpful
4. Document dependencies between steps

### Adding Fixtures

1. Create appropriate subdirectory in `fixtures/`
2. Add clear file names
3. Document purpose in this README
4. Keep fixtures minimal but complete

---

## Pass/Fail Criteria Legend

| Symbol | Meaning |
|--------|---------|
| YES | Required for test to pass |
| NO | Optional (nice to have) |
| PASS | Criterion met |
| FAIL | Criterion not met |
| WARN | Partial or uncertain |

---

## Test Environment Requirements

- **OS:** Windows 10/11 (tests use Windows paths)
- **Shell:** PowerShell or Git Bash
- **Claude Code:** Installed and configured
- **Dominion Flow Plugin:** Installed at `~/.claude/plugins/fire-flow/`
- **Permissions:** Write access to temp directories and plugin directory

---

## Troubleshooting

### Test directory not cleaned up
```bash
# Find and remove orphan test directories
find /tmp -maxdepth 1 -name "tmp.*" -type d -mtime +1 -exec rm -rf {} \;
```

### Fixture files missing
```bash
# Re-copy fixtures from backup or re-generate
# Contact plugin maintainer if fixtures are corrupted
```

### Hook not firing
```bash
# Check hooks.json syntax
python3 -c "import json; json.load(open('hooks/hooks.json'))"

# Verify script permissions
chmod +x hooks/session-start.sh
```

---

## Contributing

When adding or modifying tests:

1. Follow the existing format
2. Test your test (run it manually)
3. Update this README if adding new files
4. Document any new fixtures
5. Keep cleanup steps comprehensive

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-22 | Initial test suite creation |

---

## Maintainer

Dominion Flow Test Suite maintained as part of the Fire Flow plugin.
Location: `~/.claude/plugins/fire-flow/tests/`
