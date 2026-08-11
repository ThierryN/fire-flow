---
name: fire-security-audit-repo
description: Security audit a GitHub repo before installing as a skill or plugin
arguments:
  - name: repo
    description: GitHub repo URL or owner/name (e.g., nicobailon/visual-explainer)
    required: true
    type: string
  - name: install-as
    description: Where to install if clean (skill, plugin, or skip)
    required: false
    type: string
    default: "skill"
triggers:
  - "audit repo"
  - "check repo"
  - "install skill from github"
  - "security scan repo"
---

# /fire-security-audit-repo — Pre-Install Security Audit

> Audit any GitHub repo for security threats before installing it as a Claude Code skill or plugin.

---

## Purpose

Prevent supply chain attacks by running a 6-layer security audit on any GitHub repository before it enters the agent's trusted execution environment. This is the **pre-download and pre-use** gate.

---

## Process

### Step 1: Pre-Download Intelligence

Before cloning, gather repo metadata:

```bash
# Parse repo from URL or owner/name format
REPO="{owner}/{name}"

# Gather intelligence
gh repo view $REPO --json stargazersCount,forkCount,createdAt,updatedAt,licenseInfo,description,isArchived
gh api repos/$REPO/commits?per_page=5 --jq '.[].commit.message'
gh api users/{owner} --jq '{login, created_at, public_repos, followers}'
```

**Display pre-download report:**

```
+------------------------------------------------------------------------------+
| FIRE SECURITY AUDIT — PRE-DOWNLOAD                                           |
+------------------------------------------------------------------------------+
|                                                                              |
|  Repo: {owner}/{name}                                                        |
|  Description: {description}                                                  |
|  Stars: {N}  Forks: {N}  License: {license}                                |
|  Created: {date}  Last updated: {date}                                      |
|  Owner: {login} ({public_repos} repos, {followers} followers, since {date}) |
|                                                                              |
|  Recent commits:                                                             |
|    - {message 1}                                                             |
|    - {message 2}                                                             |
|    - {message 3}                                                             |
|                                                                              |
+------------------------------------------------------------------------------+
```

**Red flag checks:**

| Check | Threshold | Result |
|-------|-----------|--------|
| Repo age | > 30 days | {PASS/WARN} |
| Stars | > 10 | {PASS/WARN} |
| Owner account age | > 90 days | {PASS/WARN} |
| Owner other repos | > 3 | {PASS/WARN} |
| License present | Yes | {PASS/WARN} |
| Not archived | True | {PASS/FAIL} |

**If 3+ red flags → WARN user before cloning:**

```
Use AskUserQuestion:
  header: "Risk"
  question: "This repo has {N} red flags: {list}. Clone for deep audit anyway?"
  options:
    - "Yes, audit anyway" - Proceed with clone + full audit
    - "No, skip" - Abort installation
```

### Step 2: Clone to Temp Directory

```bash
cd /tmp && git clone https://github.com/{owner}/{name}.git {name}-security-review
```

**NEVER clone directly to the install location.**

### Step 3: Layer 1 — Credential Scan

```bash
bash ~/.claude/hooks/credential-filter.sh --dir /tmp/{name}-security-review/
```

| Result | Action |
|--------|--------|
| Exit 0 | CLEAN — proceed |
| Exit 1 | BLOCKED — show findings, abort |

### Step 4: Layer 2 — Prompt Injection Scan

Search ALL text files for prompt injection patterns:

```bash
# Instruction override patterns
grep -rnEi 'ignore.*(previous|above|prior).*(instruction|prompt|rule)' /tmp/{name}-security-review/ --include='*.md' --include='*.txt' --include='*.json' --include='*.yaml' --include='*.yml'

# Role manipulation
grep -rnEi '(you are now|act as|new role|forget everything|override|bypass|disregard)' /tmp/{name}-security-review/ --include='*.md' --include='*.txt'

# System prompt extraction
grep -rnEi '(system prompt|show me your|repeat your|reveal your|print your).*(instructions|prompt|rules)' /tmp/{name}-security-review/ --include='*.md' --include='*.txt'

# Special tokens
grep -rnE '<\|im_start\|>|<\|im_end\|>|\[INST\]|\[\/INST\]' /tmp/{name}-security-review/
```

Also scan for invisible Unicode:

```bash
# Zero-width characters
grep -rP '[\x{200B}\x{200C}\x{200D}\x{FEFF}\x{2060}]' /tmp/{name}-security-review/ --include='*.md' --include='*.txt'
```

### Step 5: Layer 3 — Exfiltration Detection

```bash
# Network calls in scripts
grep -rnE '(fetch\(|XMLHttpRequest|WebSocket|navigator\.sendBeacon|\.ajax\()' /tmp/{name}-security-review/ --include='*.js' --include='*.ts' --include='*.html'

# Shell network commands
grep -rnE '(curl |wget |nc |ncat )' /tmp/{name}-security-review/ --include='*.sh' --include='*.md'

# Cookie/storage access
grep -rnE '(document\.cookie|localStorage\.|sessionStorage\.)' /tmp/{name}-security-review/ --include='*.js' --include='*.html'
```

**Allowlist CDN domains:** jsdelivr.net, cdnjs.cloudflare.com, unpkg.com, fonts.googleapis.com, fonts.gstatic.com

Any URL NOT on the allowlist → flag for review.

### Step 6: Layer 4 — Tool Poisoning

```bash
# Destructive operations
grep -rnE '(rm -rf|sudo |chmod 777|eval\(|exec\()' /tmp/{name}-security-review/

# Credential file access
grep -rnE '(\.env|\.ssh|\.aws|credentials|\.gnupg|\.netrc)' /tmp/{name}-security-review/ --include='*.md' --include='*.sh' --include='*.js'

# Process spawning
grep -rnE '(child_process|os\.system|subprocess|spawn\()' /tmp/{name}-security-review/ --include='*.js' --include='*.ts' --include='*.py'
```

### Step 7: Layer 5 — Hidden Content

```bash
# Base64 payloads (>100 chars, exclude image data URIs)
grep -rnE '[A-Za-z0-9+/]{100,}={0,2}' /tmp/{name}-security-review/ --include='*.md' --include='*.json' | grep -v 'data:image'

# Obfuscation
grep -rnE '(atob|btoa|String\.fromCharCode|unescape|decodeURI)' /tmp/{name}-security-review/ --include='*.js' --include='*.html'
```

### Step 8: Layer 6 — CDN Dependency Pinning

For each external script/CSS URL found in HTML files:

| URL Pattern | Verdict |
|-------------|---------|
| `@3.2.2` (exact) | GOOD |
| `@11` (major only) | ADVISORY |
| No version | WARNING |
| Unknown CDN | RED FLAG |

### Step 9: Compile Audit Report

```
+------------------------------------------------------------------------------+
| FIRE SECURITY AUDIT — RESULTS                                                |
+------------------------------------------------------------------------------+
|                                                                              |
|  Repo: {owner}/{name}                                                        |
|  Files scanned: {N}                                                          |
|                                                                              |
|  Layer 1: Credentials      ... {CLEAN | BLOCKED}                            |
|  Layer 2: Prompt Injection  ... {CLEAN | FOUND {N}}                         |
|  Layer 3: Exfiltration      ... {CLEAN | FOUND {N}}                         |
|  Layer 4: Tool Poisoning    ... {CLEAN | FOUND {N}}                         |
|  Layer 5: Hidden Content    ... {CLEAN | FOUND {N}}                         |
|  Layer 6: CDN Pinning       ... {GOOD | ADVISORY {N} | WARNING {N}}        |
|                                                                              |
|  OVERALL VERDICT: {CLEAN | ADVISORY | SUSPICIOUS | BLOCKED}                |
|                                                                              |
+------------------------------------------------------------------------------+
```

### Step 10: Install or Reject

**If CLEAN or ADVISORY:**

```bash
# Install as skill
cp -r /tmp/{name}-security-review/ ~/.claude/skills/{name}/
rm -rf ~/.claude/skills/{name}/.git

# Run credential filter one more time on installed location
bash ~/.claude/hooks/credential-filter.sh --dir ~/.claude/skills/{name}/
```

**If SUSPICIOUS:**

```
Use AskUserQuestion:
  header: "Suspicious"
  question: "{N} suspicious findings. Review details and decide?"
  options:
    - "Show findings" - Display all flagged items with file:line context
    - "Install anyway" - Accept risk
    - "Abort" - Do not install
```

**If BLOCKED:**

```
INSTALLATION BLOCKED

{N} security threats detected:
  {finding 1}
  {finding 2}
  ...

This repo will NOT be installed.
```

### Step 11: Log Audit Result

Write audit log to `~/.claude/audit-log/{name}-{date}.md`:

```markdown
# Security Audit: {owner}/{name}
**Date:** {YYYY-MM-DD}
**Verdict:** {CLEAN|ADVISORY|SUSPICIOUS|BLOCKED}
**Installed:** {yes/no}
**Location:** {install path or "not installed"}

## Pre-Download
- Stars: {N}, Forks: {N}, Age: {days}
- Owner: {login}, Repos: {N}, Followers: {N}

## Layer Results
{summary of each layer}

## Findings
{detailed findings if any}
```

### Step 12: Cleanup

```bash
rm -rf /tmp/{name}-security-review
```

---

## Success Criteria

- [ ] Pre-download intelligence gathered and red flags evaluated
- [ ] All 6 layers executed
- [ ] Findings reported with file:line context
- [ ] Verdict is one of: CLEAN, ADVISORY, SUSPICIOUS, BLOCKED
- [ ] Audit log written
- [ ] Temp directory cleaned up
- [ ] If installed: credential filter passed on installed copy

---

## References

- **Skill:** `security/GITHUB_REPO_SECURITY_AUDIT.md`
- **Depends on:** `~/.claude/hooks/credential-filter.sh`
- **Related:** `/fire-add-new-skill` (Step 4.6 credential gate)
