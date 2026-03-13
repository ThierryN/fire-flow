---
name: credential-security-workflow
category: awesome-workflows
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
last_updated: 2026-02-24
tags: [security, credentials, secrets, git-hooks, prevention]
difficulty: easy
---

# Credential Security Workflow

## Problem

AI agents extract real session work into skill documents, guides, and methodology files. When building integrations (Zoom, Google, Stripe, etc.), real `.env` values get captured verbatim into documentation, then committed to git, then pushed to GitHub — exposing secrets publicly.

**Real incident (2026-02-24):** Google YouTube API key + 2 sets of Zoom S2S credentials leaked through this exact chain across 38 files in 2 repos.

## Solution Pattern

3-layer defense that catches secrets at extraction, at commit, and on-demand:

```
Layer 1: Credential filter in skill extraction (Step 4.6 in /fire-add-new-skill)
Layer 2: Git pre-commit hook (blocks commits with secrets)
Layer 3: On-demand scanner (audit any directory)
```

## Workflow Steps

### 1. Prevention: Skill Extraction Gate

When extracting skills from session work (`/fire-add-new-skill --from session`), Step 4.6 automatically runs the credential scanner on the generated skill content BEFORE saving.

If real secrets detected → skill is NOT saved. Agent must replace values with placeholders first.

### 2. Commit Gate: Pre-Commit Hook

Every `git commit` triggers the pre-commit hook:

```bash
# .git/hooks/pre-commit
SCANNER="$HOME/.claude/hooks/credential-filter.sh"
STAGED=$(git diff --cached --name-only --diff-filter=ACM)
bash "$SCANNER" $STAGED
# Exit 1 = blocked, Exit 0 = allowed
```

### 3. On-Demand Scan: Directory Audit

Scan any directory for leaked secrets:

```bash
bash ~/.claude/hooks/credential-filter.sh --dir ./skills-library/
bash ~/.claude/hooks/credential-filter.sh --dir ./src/
```

### 4. Incident Response

If secrets ARE found in committed code:
1. **Scrub immediately** — Replace all secret values with `YOUR_*` placeholders
2. **Commit the fix** — `security: scrub leaked credentials`
3. **Rotate credentials** — Generate new keys at the provider's console
4. **Update `.env` files** — Replace old values with new rotated ones
5. **Check git history** — If pushing to public, use `git filter-repo` or BFG to rewrite history

### 5. Placeholder Convention

Always use these placeholder formats:

| Secret Type | Placeholder |
|-------------|-------------|
| API keys | `YOUR_API_KEY` or `YOUR_{SERVICE}_API_KEY` |
| Client IDs | `YOUR_CLIENT_ID` or `YOUR_{SERVICE}_CLIENT_ID` |
| Client secrets | `YOUR_CLIENT_SECRET` |
| Account IDs | `YOUR_ACCOUNT_ID` |
| Passwords | `YOUR_PASSWORD` |
| Connection strings | `YOUR_CONNECTION_STRING` |

## Scanner Coverage

The shared scanner (`~/.claude/hooks/credential-filter.sh`) detects 23 patterns:
- Google API keys (`AIzaSy...`)
- AWS access keys (`AKIA...`)
- Anthropic keys (`sk-ant-api03-...`)
- Stripe keys (live + test)
- GitHub PATs (`ghp_`, `github_pat_`)
- Slack tokens (`xox[pboa]-...`)
- OpenAI keys (`sk-proj-...`)
- Connection strings (PostgreSQL, MongoDB, MySQL, Redis)
- Private keys (`-----BEGIN...PRIVATE KEY-----`)
- Generic `API_KEY=`, `CLIENT_SECRET=`, `CLIENT_ID=` patterns

## When to Use

- ALWAYS — this is a mandatory security layer, not optional
- After any session involving third-party API integration
- Before pushing any repo to a remote (especially public)
- When onboarding a new project with existing `.env` files

## When NOT to Use

- Never skip this. There is no scenario where credential scanning is wrong.

## Related Skills

- [deployment-security/](../deployment-security/) — Production security patterns
- [security/](../security/) — Auth and encryption patterns
