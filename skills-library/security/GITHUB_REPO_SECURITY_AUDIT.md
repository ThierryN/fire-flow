---
name: github-repo-security-audit
category: security
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
last_updated: 2026-02-24
tags: [security, github, audit, skills, plugins, supply-chain]
difficulty: medium
---

# GitHub Repo Security Audit

## Problem

Installing skills, plugins, or tools from GitHub repos introduces supply chain risk. Repos may contain prompt injection, credential harvesting, exfiltration URLs, tool poisoning, or hidden malicious content. Without systematic auditing, compromised skills enter the agent's trusted execution environment.

## Solution Pattern

6-layer security audit performed BEFORE installation. The audit runs in an isolated temp directory, never in the target skill path. Only after passing all layers does the repo get copied to the install location.

## Pre-Download Checklist

Before even cloning, evaluate:

| Check | How | Red Flag |
|-------|-----|----------|
| Repo age | `gh repo view --json createdAt` | Created < 7 days ago |
| Stars/forks | `gh repo view --json stargazersCount,forkCount` | Stars < 10, looks artificial |
| Recent commits | `gh api repos/{owner}/{repo}/commits?per_page=5` | All commits in last 24h (rush job) |
| Open issues | `gh repo view --json issues` | Many unresolved security issues |
| License | `gh repo view --json licenseInfo` | No license or unusual license |
| Owner reputation | `gh api users/{owner}` | New account, no other repos |

## 6-Layer Post-Clone Audit

### Layer 1: Credential Scan
```bash
bash ~/.claude/hooks/credential-filter.sh --dir /tmp/{repo}-review/
```
Catches real API keys, passwords, connection strings in the repo.

### Layer 2: Prompt Injection Scan
Search all `.md`, `.txt`, `.json`, `.yaml` files for:
- `ignore previous instructions`
- `you are now` / `act as` (role manipulation)
- `system prompt` extraction attempts
- `<|im_start|>` or other special tokens
- Hidden Unicode characters (zero-width spaces, directional overrides)

```bash
grep -rnE 'ignore.*(previous|above|prior).*(instruction|prompt|rule)' /tmp/{repo}-review/
grep -rnE '(you are now|act as|new role|forget|override|bypass)' /tmp/{repo}-review/
```

### Layer 3: Exfiltration Detection
Search for outbound data transmission:
- `fetch(` / `XMLHttpRequest` / `WebSocket` / `navigator.sendBeacon`
- `curl` / `wget` with external URLs
- `document.cookie` / `localStorage` / `sessionStorage` reads
- Image/script `src` pointing to non-CDN domains
- Any URL that isn't a well-known CDN (jsdelivr, cdnjs, unpkg, googleapis)

### Layer 4: Tool Poisoning
Search for destructive or privileged operations:
- `rm -rf` / `sudo` / `chmod 777` / `eval` / `exec`
- File writes to `~/.claude/`, `~/.ssh/`, `~/.env`, `~/.aws/`
- Attempts to read credential files
- `child_process` / `os.system` / `subprocess` calls

### Layer 5: Hidden Content
- Run NFKC normalization on all text files
- Search for zero-width Unicode characters (`\u200B`, `\u200C`, `\u200D`, `\uFEFF`)
- Check for base64 payloads longer than 100 chars (exclude images)
- Look for `atob`, `btoa`, `String.fromCharCode`, `unescape`

### Layer 6: CDN Dependency Pinning
For all external script/CSS references in HTML files:
- Check if version is pinned to exact version (e.g., `@3.2.2`) — GOOD
- Major-only pinning (e.g., `@11`) — ADVISORY
- No version at all — WARNING
- Non-standard CDN domain — RED FLAG

## Verdict Matrix

| Result | Action |
|--------|--------|
| All 6 layers CLEAN | Install to `~/.claude/skills/{name}/` |
| 1-2 ADVISORY items | Install with warnings documented |
| Any SUSPICIOUS finding | Show to user, require explicit approval |
| Any BLOCKED finding | Do NOT install. Show findings. |

## Post-Install Verification

After installing a clean repo:
1. Remove `.git/` directory (no need for git history in skills)
2. Run credential filter one more time on installed location
3. Log the audit result: `~/.claude/audit-log/{repo}-{date}.md`

## When to Use

- ALWAYS when installing skills/plugins from GitHub
- When adding any external repo to the agent's trusted environment
- When updating an existing skill from a remote source
- When someone shares a "cool Claude Code skill" link

## When NOT to Use

- For repos you're building yourself (use credential filter + pre-commit hooks instead)
- For official Anthropic repos (still advisable but lower risk)

## Related Skills

- [CREDENTIAL-SECURITY-WORKFLOW.md](../awesome-workflows/CREDENTIAL-SECURITY-WORKFLOW.md) — Credential leak prevention
- [deployment-security/](../deployment-security/) — Production security patterns
