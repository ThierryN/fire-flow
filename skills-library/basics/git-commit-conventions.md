# Skill: Git Commit Conventions

**Category:** Basics
**Difficulty:** Beginner
**Applies to:** Every project

---

## The Problem

Commit messages like `"fixed stuff"`, `"wip"`, or `"asdfgh"` tell future-you (and your teammates) nothing. When something breaks three months later, you can't figure out what changed or why.

---

## The Solution: Conventional Commits

A simple format that makes your history readable and searchable.

### Format

```
type(scope): short description

optional longer explanation
```

### Types

| Type | Use When |
|------|---------|
| `feat` | Adding a new feature |
| `fix` | Fixing a bug |
| `docs` | Updating documentation only |
| `style` | Formatting, missing semicolons — no logic change |
| `refactor` | Restructuring code without changing behavior |
| `test` | Adding or fixing tests |
| `chore` | Build tools, dependencies, config files |

---

## Examples

```bash
# Good
git commit -m "feat(auth): add JWT login endpoint"
git commit -m "fix(payments): handle declined card error correctly"
git commit -m "docs: update README with install instructions"
git commit -m "chore: upgrade express from 4.18 to 4.19"

# Bad
git commit -m "fixed it"
git commit -m "update"
git commit -m "wip"
git commit -m "changes"
```

---

## The 50/72 Rule

- **Subject line:** 50 characters max. Use imperative mood — "add feature", not "added feature"
- **Body:** 72 characters per line. Explain WHY, not what (the diff shows what)

```bash
git commit -m "fix(auth): prevent login with expired tokens

JWT tokens were not being checked for expiration before
granting access. Added expiry check in the middleware.
Fixes #42."
```

---

## Scope (Optional but Helpful)

The scope is the part of the app you changed:

```
feat(auth): ...        # authentication system
fix(api): ...          # API layer
style(dashboard): ...  # dashboard UI
chore(deps): ...       # dependencies
```

---

## Practical Habits

1. **Commit one thing at a time** — one commit = one logical change
2. **Commit often** — small commits are easier to review and revert
3. **Never commit broken code** — your main branch should always work
4. **Write the message before you forget** — commit right after the change

---

## Check Your Last Commits

```bash
git log --oneline -10
```

If you can't tell what each commit did from the message alone, your messages need work.

---

*Fire Flow Skills Library — MIT License*
