# Skills Quarantine

Auto-extracted skill candidates land here for review before promotion to the main library.

## Lifecycle

```
Auto-extracted → _quarantine/ → Review → Promote to category/ OR Delete
```

## Review Criteria

- Is the pattern generalizable (not project-specific)?
- Does it solve a non-trivial problem?
- Has it passed the security gate?
- Is it a duplicate of an existing skill?

## Auto-Promotion

Skills applied successfully in 2+ different projects with confidence > 0.85
are auto-promoted from `_quarantine/` to their proper category folder.

## Security Gate

All quarantined skills must pass:
- No `exec()`, `eval()`, `child_process` in code examples
- No hardcoded credentials or API keys
- No destructive operations (DROP, DELETE, rm -rf)

See: `methodology/EVOLUTIONARY_SKILL_SYNTHESIS.md` for full pipeline details.
