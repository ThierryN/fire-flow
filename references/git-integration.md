# Dominion Flow Git Integration Reference

> **Origin:** Ported from Dominion Flow `git-integration.md` with full Git Flow branch strategy.

## Core Principle

**Commit outcomes, not process.** The git log should read like a changelog of what shipped, not a diary of planning activity.

---

## Git Flow Branch Strategy

### Branch Types

| Branch | Purpose | Created From | Merges Into | Lifetime |
|--------|---------|-------------|-------------|----------|
| `main` | Production-ready code | --- | --- | Permanent |
| `develop` | Integration branch | `main` | `main` | Permanent |
| `feature/phase-N-desc` | Per-phase feature work | `develop` | `develop` | Until phase complete |
| `hotfix/description` | Emergency production fixes | `main` | `main` AND `develop` | Until fix deployed |
| `release/vX.Y.Z` | Release preparation | `develop` | `main` AND `develop` | Until release shipped |

### Branch Naming

```
feature/phase-01-foundation
feature/phase-02-auth
feature/phase-03-dashboard
hotfix/fix-login-crash
release/v1.0.0
```

### Branch Lifecycle

**Starting a phase:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/phase-03-dashboard
```

**Completing a phase (after verification passes):**
```bash
git push -u origin feature/phase-03-dashboard
gh pr create --base develop --head feature/phase-03-dashboard \
  --title "Phase 03: Dashboard" --body "..."
```

**Hotfix workflow:**
```bash
git checkout main && git pull origin main
git checkout -b hotfix/fix-login-crash
# Make fix, commit, push
gh pr create --base main --title "Hotfix: Login crash"
# After merge to main, also merge to develop
git checkout develop && git merge main && git push
```

---

## Commit Points

| Event | Commit? | Why |
|-------|---------|-----|
| PROJECT.md + ROADMAP created | YES | Project initialization |
| BLUEPRINT.md created | NO | Intermediate |
| RESEARCH.md created | NO | Intermediate |
| **Task completed** | YES | Atomic unit of work |
| **Plan completed** | YES | Metadata commit |
| **Test written (TDD RED)** | YES | Atomic test commit |
| **Test passing (TDD GREEN)** | YES | Atomic implementation |
| Handoff created | YES | WIP state preserved |
| **Blocker created/resolved** | YES | Track blocker state |

---

## Commit Formats

### Project Initialization

```
docs: initialize [project-name] ([N] phases)

[One-liner from PROJECT.md]

Phases:
1. [phase-name]: [goal]
2. [phase-name]: [goal]

Branch strategy: main -> develop -> feature/phase-N-*
```

### Task Completion (Per-Task Atomic Commits)

```
{type}({phase}-{plan}): {task-name}

- [Key change 1]
- [Key change 2]
```

**Types:** `feat`, `fix`, `test`, `refactor`, `perf`, `chore`, `docs`

**Examples:**
```bash
git add src/api/auth.ts src/types/user.ts
git commit -m "feat(08-02): create user registration endpoint

- POST /auth/register validates email and password
- Returns JWT token on success"

git add src/__tests__/jwt.test.ts
git commit -m "test(07-02): add failing test for JWT generation

- Tests token contains user ID claim
- Tests token expires in 1 hour"
```

### Plan Completion

```
docs({phase}-{plan}): complete [plan-name]

Tasks completed: [N]/[N]
- [Task 1]
- [Task 2]

SUMMARY: .planning/phases/XX-name/{phase}-{plan}-RECORD.md
```

### Handoff (WIP)

```
wip: [phase-name] paused at task [X]/[Y]

Current: [task name]
Branch: feature/phase-XX-description
Blockers: [count] open
```

---

## PR Workflow

### When to Create PRs

| Event | PR Target | Required |
|-------|-----------|----------|
| Phase complete + verified | `develop` | Yes |
| Hotfix ready | `main` | Yes |
| Release ready | `main` | Yes |
| Mid-phase handoff | None (push only) | No |

### PR Template

```bash
gh pr create --base develop --title "Phase XX: Short description" --body "$(cat <<'EOF'
## Summary
- [Key deliverable 1]
- [Key deliverable 2]

## Test Results
- Unit tests: X/X passing
- Build: Clean

## Verification
- [x] Must-haves verified
- [x] WARRIOR quality gates passed
- [x] No P0/P1 blockers open
EOF
)"
```

---

## Example Git Log

```
# Phase 03 - Products (feature/phase-03-products)
3m4n5o docs(03-02): complete product listing plan
6p7q8r feat(03-02): add pagination controls
9s0t1u feat(03-02): implement search and filters
2v3w4x feat(03-01): create product catalog schema

# Phase 02 - Auth (feature/phase-02-auth)
5y6z7a docs(02-02): complete token refresh plan
8b9c0d feat(02-02): implement refresh token rotation
1e2f3g test(02-02): add failing test for token refresh
7k8l9m feat(02-01): add JWT generation and validation

# Phase 01 - Foundation (feature/phase-01-foundation)
6t7u8v feat(01-01): configure Tailwind and globals
9w0x1y feat(01-01): set up Prisma with database
2z3a4b feat(01-01): create Next.js 15 project

# Initialization (develop)
5c6d7e docs: initialize ecommerce-app (5 phases)
```

---

## Why Per-Task Commits?

- **AI context:** `git log --grep="{phase}-{plan}"` shows all work for a plan
- **Failure recovery:** Can revert to last successful task
- **Debugging:** `git bisect` finds exact failing task
- **PR clarity:** Reviewers step through commits individually

---

## Anti-Patterns

- Committing directly to main or develop (use feature branches)
- Giant commits with all plan work (commit per task)
- Committing planning artifacts separately (commit with plan completion)
- Long-lived feature branches (one phase per branch)
- Forgetting to merge hotfixes back to develop
