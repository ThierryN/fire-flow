---
name: fire-test
description: Run Dominion Flow plugin integration tests to verify all commands and integrations work correctly
arguments:
  - name: suite
    description: "Test suite to run: --e2e, --integration, or --command [name]"
    required: false
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - Edit
---

# /fire-test - Dominion Flow Integration Tests

## Purpose

Run the Dominion Flow plugin test suite to verify all commands and integrations work correctly. Provides comprehensive validation of the entire plugin ecosystem before deployment or after updates.

## Usage

```bash
/fire-test                      # Run all tests (E2E + Integration)
/fire-test --e2e                # Run E2E tests only (8 tests)
/fire-test --integration        # Run integration tests only (3 tests)
/fire-test --command [name]     # Test specific command (e.g., fire-1-new)
```

## Test Suites

### E2E Tests (8 tests)

End-to-end tests verify each command works in isolation:

| Test | Command | Verification |
|------|---------|--------------|
| 1 | `/fire-1-new` | Creates correct .planning/ structure with all required files |
| 2 | `/fire-2-plan` | Generates valid BLUEPRINT.md with skills references and must-haves |
| 3 | `/fire-3-execute` | Completes breath execution with RECORD.md output |
| 4 | `/fire-4-verify` | Runs all Must-Haves + WARRIOR validation checks |
| 5 | `/fire-5-handoff` | Creates unified fire-handoff.md with 7-step format |
| 6 | `/fire-6-resume` | Restores full context from handoff file |
| 7 | `/fire-search` | Finds relevant skills from library by query |
| 8 | `/fire-contribute` | Adds new skill to library with proper structure |

### Integration Tests (3 tests)

Integration tests verify cross-component functionality:

| Test | Scenario | Verification |
|------|----------|--------------|
| 1 | Full Workflow | Complete cycle: new -> plan -> execute -> verify -> handoff -> resume |
| 2 | Skills Sync | Bidirectional sync between project and global skills library |
| 3 | Hooks | SessionStart hook fires and injects context correctly |

## Test Execution Process

```
Step 1: Parse Arguments
â”œâ”€â”€ Check for --e2e, --integration, or --command flags
â”œâ”€â”€ Determine which test suite(s) to run
â””â”€â”€ Validate command name if --command specified

Step 2: Create Temp Test Directory
â”œâ”€â”€ Create isolated test directory: $TEMP/dominion-flow-test-{timestamp}/
â”œâ”€â”€ Initialize minimal project structure
â”œâ”€â”€ Copy test fixtures from tests/fixtures/
â””â”€â”€ Set up clean environment variables

Step 3: Run Selected Test Suite(s)
â”œâ”€â”€ E2E Tests:
â”‚   â”œâ”€â”€ For each command test:
â”‚   â”‚   â”œâ”€â”€ Execute command in test directory
â”‚   â”‚   â”œâ”€â”€ Verify expected outputs exist
â”‚   â”‚   â”œâ”€â”€ Validate file contents/structure
â”‚   â”‚   â””â”€â”€ Record pass/fail status
â”‚   â””â”€â”€ Aggregate E2E results
â”‚
â”œâ”€â”€ Integration Tests:
â”‚   â”œâ”€â”€ Full workflow test:
â”‚   â”‚   â”œâ”€â”€ Run complete workflow sequence
â”‚   â”‚   â”œâ”€â”€ Verify state transitions
â”‚   â”‚   â””â”€â”€ Check final artifacts
â”‚   â”œâ”€â”€ Skills sync test:
â”‚   â”‚   â”œâ”€â”€ Create test skill locally
â”‚   â”‚   â”œâ”€â”€ Sync to global library
â”‚   â”‚   â”œâ”€â”€ Verify bidirectional sync
â”‚   â”‚   â””â”€â”€ Clean up test skills
â”‚   â””â”€â”€ Hooks test:
â”‚       â”œâ”€â”€ Trigger SessionStart event
â”‚       â”œâ”€â”€ Verify context injection
â”‚       â””â”€â”€ Check hook output
â”‚
â””â”€â”€ Command-specific test (if --command used):
    â”œâ”€â”€ Run only the specified command test
    â””â”€â”€ Provide detailed output

Step 4: Capture Results
â”œâ”€â”€ Collect pass/fail for each test
â”œâ”€â”€ Capture any error messages
â”œâ”€â”€ Record execution times
â””â”€â”€ Note any warnings or skipped tests

Step 5: Generate Test Report
â”œâ”€â”€ Create formatted report (see format below)
â”œâ”€â”€ Calculate totals and percentages
â”œâ”€â”€ Highlight failures with details
â””â”€â”€ Provide recommendations for fixes

Step 6: Clean Up
â”œâ”€â”€ Remove temp test directory
â”œâ”€â”€ Restore any modified global state
â””â”€â”€ Clear test environment variables

Step 7: Return Status
â”œâ”€â”€ Exit 0 if all tests passed
â”œâ”€â”€ Exit 1 if any tests failed
â””â”€â”€ Display summary message
```

## Test Report Format

```markdown
# Dominion Flow Test Report

**Run Date:** YYYY-MM-DD HH:MM:SS
**Duration:** X.Xs
**Plugin Version:** 1.0.0

---

## E2E Tests: X/8

| Status | Test | Duration | Notes |
|--------|------|----------|-------|
| [x] | /fire-1-new creates correct structure | 0.5s | |
| [x] | /fire-2-plan generates valid plans | 0.8s | |
| [x] | /fire-3-execute completes breaths | 1.2s | |
| [x] | /fire-4-verify runs all checks | 0.6s | |
| [x] | /fire-5-handoff creates unified format | 0.4s | |
| [x] | /fire-6-resume restores context | 0.3s | |
| [x] | /fire-search finds relevant skills | 0.2s | |
| [x] | /fire-contribute adds new skills | 0.5s | |

---

## Integration Tests: X/3

| Status | Test | Duration | Notes |
|--------|------|----------|-------|
| [x] | Full workflow end-to-end | 3.5s | |
| [x] | Skills sync bidirectional | 1.2s | |
| [x] | Hooks fire correctly | 0.8s | |

---

## Summary

**Total: X/11 PASSED**

### Failures (if any)

```
Test: [test name]
Error: [error message]
Expected: [expected result]
Actual: [actual result]
Fix: [recommended action]
```

### Warnings (if any)

- [warning 1]
- [warning 2]

---

**Test Environment:**
- OS: [Windows/macOS/Linux]
- Shell: [PowerShell/Bash/Zsh]
- Plugin Path: ~/.claude/plugins/dominion-flow/
- Temp Directory: [path]
```

## Test Fixtures

Located in `tests/fixtures/`:

```
tests/fixtures/
â”œâ”€â”€ test-project/                  # Sample project for testing
â”‚   â”œâ”€â”€ .planning/
â”‚   â”‚   â”œâ”€â”€ PROJECT.md
â”‚   â”‚   â”œâ”€â”€ VISION.md
â”‚   â”‚   â”œâ”€â”€ CONSCIENCE.md
â”‚   â”‚   â””â”€â”€ phases/
â”‚   â”‚       â””â”€â”€ 01-test-phase/
â”‚   â”‚           â”œâ”€â”€ 01-01-BLUEPRINT.md
â”‚   â”‚           â””â”€â”€ 01-01-RECORD.md
â”‚   â””â”€â”€ src/
â”‚       â””â”€â”€ index.ts
â”‚
â”œâ”€â”€ test-skills/                   # Sample skills for testing
â”‚   â”œâ”€â”€ database-solutions/
â”‚   â”‚   â””â”€â”€ test-skill.md
â”‚   â””â”€â”€ api-patterns/
â”‚       â””â”€â”€ test-pattern.md
â”‚
â”œâ”€â”€ test-handoff/                  # Sample handoff for resume testing
â”‚   â””â”€â”€ TEST-PROJECT_2026-01-22.md
â”‚
â””â”€â”€ expected-outputs/              # Expected test outputs for comparison
    â”œâ”€â”€ new-project-structure.json
    â”œâ”€â”€ plan-frontmatter.json
    â””â”€â”€ handoff-structure.json
```

## Success Criteria

### All Tests Must:
1. Complete without unhandled exceptions
2. Produce expected file outputs
3. Maintain proper file structure
4. Preserve data integrity
5. Clean up after themselves

### E2E Test Criteria:

| Test | Success Criteria |
|------|------------------|
| fire-1-new | Creates .planning/ with PROJECT.md, VISION.md, CONSCIENCE.md, SKILLS-INDEX.md |
| fire-2-plan | Creates BLUEPRINT.md with valid YAML frontmatter including skills_to_apply |
| fire-3-execute | Creates RECORD.md with task commits and WARRIOR handoff section |
| fire-4-verify | Creates VERIFICATION.md with Must-Haves and WARRIOR validation scores |
| fire-5-handoff | Creates fire-handoff.md with all 7 WARRIOR sections (W-A-R-R-I-O-R) |
| fire-6-resume | Loads handoff, displays status, routes to correct next action |
| fire-search | Returns matching skills with relevance ranking |
| fire-contribute | Creates skill file with proper frontmatter and structure |

### Integration Test Criteria:

| Test | Success Criteria |
|------|------------------|
| Full Workflow | All 6 core commands execute in sequence without errors |
| Skills Sync | Local skill appears in global library after push; global skill available locally after pull |
| Hooks | SessionStart hook outputs context; CONSCIENCE.md and handoff are injected |

## Individual Test Specifications

### Test 1: fire-1-new

```markdown
**Setup:**
- Create empty test directory
- No existing .planning/ folder

**Execute:**
- Run /fire-1-new with test project name

**Verify:**
- .planning/ directory exists
- .planning/PROJECT.md exists and contains project name
- .planning/VISION.md exists with phase placeholders
- .planning/CONSCIENCE.md exists with WARRIOR fields
- .planning/SKILLS-INDEX.md exists and is empty/initialized
- .planning/phases/ directory exists

**Pass:** All files exist with correct structure
**Fail:** Any file missing or malformed
```

### Test 2: fire-2-plan

```markdown
**Setup:**
- Use test-project fixture
- Phase 01 exists in VISION.md

**Execute:**
- Run /fire-2-plan 1

**Verify:**
- .planning/phases/01-test-phase/01-01-BLUEPRINT.md exists
- BLUEPRINT.md has valid YAML frontmatter
- Frontmatter includes: phase, plan, breath, autonomous
- Frontmatter includes: skills_to_apply (array)
- Frontmatter includes: must_haves with truths, artifacts, warrior_validation
- Plan body includes Tasks section

**Pass:** Valid BLUEPRINT.md with all required sections
**Fail:** Missing or invalid frontmatter/sections
```

### Test 3: fire-3-execute

```markdown
**Setup:**
- Use test-project fixture with existing BLUEPRINT.md
- Plan has executable tasks

**Execute:**
- Run /fire-3-execute 1

**Verify:**
- RECORD.md created in phase directory
- RECORD.md has task commits table
- RECORD.md has WARRIOR handoff section
- SKILLS-INDEX.md updated if skills were applied
- CONSCIENCE.md updated with execution progress

**Pass:** RECORD.md complete with all sections
**Fail:** Missing sections or incomplete execution
```

### Test 4: fire-4-verify

```markdown
**Setup:**
- Use test-project fixture with completed execution
- RECORD.md exists

**Execute:**
- Run /fire-4-verify 1

**Verify:**
- VERIFICATION.md created
- Must-Haves section present with pass/fail
- WARRIOR Validation section present with scores
- Overall status determined (PASSED/FAILED)
- Gaps section lists any failures

**Pass:** Complete verification report generated
**Fail:** Missing sections or verification errors
```

### Test 5: fire-5-handoff

```markdown
**Setup:**
- Use test-project fixture with completed phase
- CONSCIENCE.md has current project data

**Execute:**
- Run /fire-5-handoff

**Verify:**
- Handoff file created in ~/.claude/warrior-handoffs/
- Handoff filename matches pattern: PROJECT-NAME_YYYY-MM-DD.md
- Handoff contains all 7 WARRIOR sections:
  - W: Work Completed
  - A: Assessment
  - R: Resources
  - R: Readiness
  - I: Issues
  - O: Outlook
  - R: References
- CONSCIENCE.md updated with handoff reference

**Pass:** Complete handoff file with all sections
**Fail:** Missing sections or file not created
```

### Test 6: fire-6-resume

```markdown
**Setup:**
- Use test-handoff fixture
- Handoff file exists in warrior-handoffs/

**Execute:**
- Run /fire-6-resume

**Verify:**
- Handoff file is read successfully
- Project status summary is displayed
- Correct next action is identified
- CONSCIENCE.md is updated with resume timestamp

**Pass:** Context restored, next action identified
**Fail:** Failed to read handoff or incorrect routing
```

### Test 7: fire-search

```markdown
**Setup:**
- Skills library populated with test skills
- Known skills exist in database-solutions/

**Execute:**
- Run /fire-search "database performance"

**Verify:**
- Results returned (not empty)
- Results are relevant to query
- Each result has skill name, category, description
- Results are ranked by relevance

**Pass:** Relevant skills found and displayed
**Fail:** No results or irrelevant matches
```

### Test 8: fire-contribute

```markdown
**Setup:**
- Skills library exists
- No existing skill with test name

**Execute:**
- Run /fire-contribute with test skill data

**Verify:**
- Skill file created in correct category folder
- Skill file has valid frontmatter (name, category, version, contributed)
- Skill file has required sections (Problem, Solution, Example)
- SKILLS-INDEX.md updated with new skill

**Pass:** Skill file created with proper structure
**Fail:** File not created or malformed
```

## Error Handling

### Common Errors and Fixes:

| Error | Cause | Fix |
|-------|-------|-----|
| "Plugin not found" | dominion-flow not installed | Install plugin to ~/.claude/plugins/dominion-flow/ |
| "Skills library empty" | Skills not copied | Copy skills from WARRIOR to skills-library/ |
| "Hook not firing" | hooks.json misconfigured | Check hooks/hooks.json syntax |
| "Permission denied" | File permissions | Check write permissions on test directory |
| "Command not recognized" | Commands not registered | Verify plugin.json has all commands listed |

### Test Isolation:

- Each test runs in isolated temp directory
- Tests do not modify global state
- Cleanup runs even if tests fail
- Failed cleanup is logged but doesn't fail tests

## Running Tests

### Prerequisites:
1. Dominion Flow plugin installed at ~/.claude/plugins/dominion-flow/
2. Skills library populated (or will use fixtures)
3. Write access to temp directory
4. Write access to ~/.claude/warrior-handoffs/

### Quick Start:
```bash
# Run all tests
/fire-test

# Run only E2E tests (faster)
/fire-test --e2e

# Test a specific command
/fire-test --command fire-1-new

# Run integration tests (requires full setup)
/fire-test --integration
```

### CI/CD Integration:
```bash
# Exit code 0 = all passed, 1 = failures
/fire-test --e2e && echo "E2E Passed" || echo "E2E Failed"
```

## Execution Instructions

When `/fire-test` is invoked:

1. **Parse arguments** to determine test scope:
   - No args: Run all 11 tests
   - `--e2e`: Run 8 E2E tests only
   - `--integration`: Run 3 integration tests only
   - `--command [name]`: Run single command test

2. **Set up test environment**:
   ```bash
   # Create temp directory
   TEST_DIR="$TEMP/dominion-flow-test-$(date +%s)"
   mkdir -p "$TEST_DIR"

   # Copy fixtures
   cp -r "$PLUGIN_ROOT/tests/fixtures/test-project" "$TEST_DIR/"
   ```

3. **Execute tests sequentially**, capturing output:
   ```
   Running E2E Tests...
   [1/8] Testing /fire-1-new... PASS (0.5s)
   [2/8] Testing /fire-2-plan... PASS (0.8s)
   ...
   ```

4. **Generate and display report** in the format shown above

5. **Clean up**:
   ```bash
   rm -rf "$TEST_DIR"
   ```

6. **Return status**:
   - Display "All tests passed!" or "X tests failed"
   - Return appropriate exit code

## Notes

- Tests are designed to be non-destructive to the actual plugin
- All file operations happen in temp directory
- Skills library tests use copies, not originals
- Handoff tests create files in a test subdirectory
- Integration tests may take longer (5-10 seconds total)
- Individual command tests complete in under 1 second each
