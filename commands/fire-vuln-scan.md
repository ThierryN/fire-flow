---
description: AI-powered application vulnerability scanner using OWASP Top 10 — find what regex-based tools miss
argument-hint: "[path] [--deep] [--category injection|auth|data|config|mern|all] [--fix-preview] [--report] [--server-only] [--client-only] [--critical-only]"
---

# /fire-vuln-scan

> AI-powered application vulnerability scanner — find what regex-based tools miss

---

## Purpose

Scan application codebases for OWASP Top 10 vulnerabilities using Claude's code reasoning — not pattern matching. Inspired by Anthropic's Claude Code Security (launched 2026-02-20), which found 500+ bugs that humans missed for decades.

**What this is:** Application security scanner (finds SQL injection, XSS, broken auth in YOUR code)
**What this is NOT:** Agent security scanner (that's `/fire-security-scan` — protects Claude from prompt injection)

**Research basis:** Claude Code Security (Anthropic 2026), OWASP Top 10 2021, OWASP Agentic Top 10 2026, Agent-as-Judge self-verification (95% error recovery)

---

## Arguments

```yaml
arguments:
  target_path:
    required: false
    type: string
    description: "Directory or file to scan. Defaults to current project root."
    example: "/fire-vuln-scan c:\\path\\repos\\MY-PROJECT"

optional_flags:
  --deep: "AI-powered reasoning trace per finding (slower, fewer false positives)"
  --category: "Focus on one category: injection | auth | data | config | mern | all (default: all)"
  --fix-preview: "Show suggested fix code for each finding"
  --report: "Save full report to .planning/security/ AND Claude Reports folder"
  --server-only: "Scan only server-side code (skip client/frontend)"
  --client-only: "Scan only client-side code (skip server/backend)"
  --critical-only: "Only report CRITICAL and HIGH severity findings"
```

---

## Process

### Step 1: Enumerate Target Files

```
+------------------------------------------------------------------------------+
|                    POWER VULN SCAN                                            |
+------------------------------------------------------------------------------+
|                                                                              |
|  Target: {path}                                                              |
|  Mode: {quick | deep}                                                        |
|  Category: {all | injection | auth | data | config | mern}                   |
|  Agents: {3-4 parallel scanners}                                             |
|                                                                              |
+------------------------------------------------------------------------------+
```

**File discovery:**
```
Scan target directory for security-relevant files:

Priority 1 (ALWAYS scan):
  - server.js / app.js / index.js (entry points)
  - routes/**/*.js (API endpoints)
  - controllers/**/*.js (request handlers)
  - middleware/**/*.js (auth, validation, error handling)
  - models/**/*.js (database schemas)
  - config/**/*.js (configuration files)
  - .env* files (environment variables — check for secrets)

Priority 2 (scan if --deep or relevant category):
  - services/**/*.js (business logic)
  - utils/**/*.js (utility functions)
  - client/src/**/*.jsx (React components — XSS checks)
  - package.json (dependency vulnerabilities)
  - docker-compose.yml (container config)
  - nginx.conf (proxy config)

Skip:
  - node_modules/
  - .git/
  - dist/ / build/
  - test/ / __tests__/ (unless checking for hardcoded test credentials)
```

**Report file count and estimated scan time.**

### Step 2: Spawn Parallel Scan Agents

Launch 3-4 agents simultaneously, each scanning different OWASP categories.

**Agent A: Injection + XSS Scanner**

```markdown
<objective>
Scan for injection vulnerabilities (OWASP A03) and XSS (OWASP A07) in this codebase.
</objective>

<target>
{list of route, controller, service, and model files}
</target>

<scan_checklist>
INJECTION (A03):
- [ ] NoSQL injection: User input directly in MongoDB queries without type coercion
      Pattern: db.collection.find({ field: req.body.field }) without String() or sanitize
- [ ] Command injection: User input in child_process.exec/spawn/execFile
      Pattern: exec(`command ${userInput}`)
- [ ] Template injection: User input in template literals sent to eval or template engines
- [ ] SSRF: User-controlled URLs in fetch/axios/http.get without allowlist
      Pattern: fetch(req.body.url) or axios.get(req.query.callback)
- [ ] SQL injection: If any SQL database used, raw query with string concatenation
- [ ] LDAP injection: User input in LDAP queries
- [ ] XML injection: User input in XML parsing without entity protection
- [ ] Path traversal: User input in file paths without sanitization
      Pattern: fs.readFile(path.join(uploadDir, req.params.filename))

XSS (A07):
- [ ] React dangerouslySetInnerHTML with unsanitized user content
- [ ] Server-side HTML rendering with unescaped user input
- [ ] URL-based XSS via unvalidated redirect targets
- [ ] DOM XSS via document.write, innerHTML, or eval with user input
- [ ] Stored XSS: User content saved to DB and rendered without escaping
</scan_checklist>

<output_format>
For each finding, provide:
  - VULN-A{NNN}: {title}
  - File: {path}:{line_number}
  - Severity: CRITICAL | HIGH | MEDIUM | LOW
  - Confidence: HIGH (traced exploitable path) | MEDIUM (pattern match) | LOW (theoretical)
  - Code: {the vulnerable code snippet, 3-5 lines}
  - Exploit: {how an attacker would exploit this}
  - Fix: {suggested fix with code}
  - OWASP: {category code}
</output_format>

<rules>
- READ the actual code. Do not guess or assume.
- Trace data flow from user input (req.body, req.params, req.query) to dangerous sinks.
- Check if framework protections exist (Mongoose parameterizes by default for simple queries).
- Check if validation middleware exists upstream before flagging.
- If uncertain, mark confidence as LOW rather than inflating severity.
- Reference: @skills-library/security/application-vuln-patterns.md
</rules>
```

**Agent B: Auth + Access Control Scanner**

```markdown
<objective>
Scan for broken access control (OWASP A01) and authentication failures (OWASP A07) in this codebase.
</objective>

<target>
{list of route files, middleware files, auth-related files}
</target>

<scan_checklist>
BROKEN ACCESS CONTROL (A01):
- [ ] Routes without auth middleware (especially admin/sensitive endpoints)
      Pattern: router.get('/api/admin/...', controller.method) — no protect/auth middleware
- [ ] Missing role-based access control on privileged operations
- [ ] IDOR: User can access other users' resources by changing ID in URL
      Pattern: User.findById(req.params.id) without checking req.user._id === req.params.id
- [ ] Privilege escalation: User can set their own role
      Pattern: User.findByIdAndUpdate(id, req.body) where req.body includes { role: 'admin' }
- [ ] Missing CORS restrictions or overly permissive CORS
      Pattern: cors({ origin: '*' }) or cors() with no config
- [ ] CSRF: State-changing operations without CSRF tokens
- [ ] JWT stored in localStorage (XSS-accessible)
- [ ] JWT without expiration or with very long expiration
- [ ] Password reset without proper token validation

AUTHENTICATION FAILURES (A07):
- [ ] Passwords stored in plaintext or weak hashing (MD5, SHA1)
- [ ] No rate limiting on login endpoints
- [ ] No account lockout after failed attempts
- [ ] Session tokens not invalidated on logout
- [ ] Default credentials in code or config
- [ ] Password requirements too weak or not enforced
</scan_checklist>

<output_format>
Same as Agent A but with VULN-B{NNN} prefix.
</output_format>
```

**Agent C: Data Exposure + Config Scanner**

```markdown
<objective>
Scan for cryptographic failures (OWASP A02), security misconfiguration (OWASP A05),
and insecure design (OWASP A04).
</objective>

<target>
{config files, .env files, server entry point, middleware, package.json}
</target>

<scan_checklist>
CRYPTOGRAPHIC FAILURES (A02):
- [ ] Hardcoded secrets (API keys, passwords, JWT secrets in source code)
      Pattern: const JWT_SECRET = "mysecret" or apiKey: "sk-..."
- [ ] Weak cryptographic algorithms (MD5, SHA1 for passwords)
- [ ] Missing HTTPS enforcement
- [ ] Sensitive data in logs (passwords, tokens, PII)
- [ ] Missing encryption for sensitive data at rest

SECURITY MISCONFIGURATION (A05):
- [ ] Debug mode enabled in production config
- [ ] Verbose error messages exposing stack traces to clients
      Pattern: res.status(500).json({ error: err.stack })
- [ ] Missing security headers (Helmet.js not used)
      Check: X-Content-Type-Options, X-Frame-Options, CSP, HSTS
- [ ] Directory listing enabled
- [ ] Default or sample configurations in production
- [ ] Unnecessary features enabled (TRACE, DEBUG endpoints)
- [ ] Missing rate limiting on API endpoints

INSECURE DESIGN (A04):
- [ ] No input validation on critical operations (payments, account changes)
- [ ] Business logic flaws (e.g., price manipulation in cart)
- [ ] Missing anti-automation on sensitive flows (registration, password reset)
- [ ] Insufficient logging for security events
</scan_checklist>

<output_format>
Same format with VULN-C{NNN} prefix.
</output_format>
```

**Agent D: MERN-Specific Scanner**

```markdown
<objective>
Scan for vulnerabilities specific to the MERN stack (MongoDB, Express, React, Node.js).
</objective>

<target>
{all files — cross-cutting concerns}
</target>

<scan_checklist>
MONGODB:
- [ ] $where operator with user input (JavaScript injection)
- [ ] $regex with user input (ReDoS)
- [ ] Mongoose populate() without field selection (data leakage)
- [ ] Missing schema validation (schemaless collections accepting anything)

EXPRESS:
- [ ] Missing express-rate-limit on all routes
- [ ] Missing helmet() middleware
- [ ] Missing express-mongo-sanitize or similar input sanitizer
- [ ] bodyParser with high limit allowing DoS
- [ ] Missing request size limits on file uploads
- [ ] Error handler exposing internal details

REACT:
- [ ] dangerouslySetInnerHTML with user content
- [ ] eval() or Function() with dynamic input
- [ ] Sensitive data in client-side state/localStorage
- [ ] API keys or secrets in client-side code
- [ ] Missing Content-Security-Policy

NODE.JS:
- [ ] Prototype pollution via Object.assign or spread with user input
- [ ] Buffer.allocUnsafe() without clearing
- [ ] Unhandled promise rejections crashing the server
- [ ] Missing process-level error handlers
- [ ] child_process with unsanitized input
- [ ] Insecure dependencies (known CVEs in package.json)

PLUGIN ARCHITECTURE (if applicable):
- [ ] Plugin code execution without sandboxing
- [ ] Plugin file access without path restrictions
- [ ] Plugin database access without scoping
</scan_checklist>

<output_format>
Same format with VULN-D{NNN} prefix.
</output_format>
```

### Step 3: Self-Verification (Agent-as-Judge)

After all scan agents return, spawn a verification agent:

```markdown
<objective>
You are a security review judge. Re-examine each vulnerability finding and filter false positives.
</objective>

<findings>
{merged findings from all scan agents}
</findings>

<verification_checklist>
For EACH finding, answer:

1. EXPLOITABLE? Is there a real attack path, or does a guard elsewhere prevent exploitation?
   - Check if input validation middleware exists upstream
   - Check if the framework provides built-in protection
   - Check if there's a WAF or reverse proxy that would block this

2. SEVERITY CORRECT? Is the severity rating appropriate?
   - CRITICAL: Remote code execution, auth bypass, data breach possible
   - HIGH: Significant data exposure or access control violation
   - MEDIUM: Information disclosure, missing best practice with some risk
   - LOW: Best practice violation with minimal real-world risk

3. CONFIDENCE? How certain are we?
   - HIGH: Traced full exploit path from input to dangerous sink
   - MEDIUM: Pattern matches but didn't trace full path
   - LOW: Theoretical risk, may be mitigated by unseen code

4. DUPLICATE? Is this the same issue reported by multiple agents?

5. FALSE POSITIVE? Mark as FALSE_POSITIVE if:
   - Framework provides automatic protection (e.g., Mongoose sanitizes simple queries)
   - Guard exists elsewhere that was missed by the scan agent
   - The pattern match is a false alarm (e.g., "password" in a UI label, not actual password)
</verification_checklist>

<output>
Return the VERIFIED findings list with:
- Removed false positives
- Deduplicated entries
- Corrected severity/confidence where needed
- Added verification notes
</output>
```

### Step 4: Merge + Deduplicate

Combine verified findings into a single sorted list:
1. CRITICAL findings first (sorted by confidence HIGH → LOW)
2. HIGH findings
3. MEDIUM findings
4. LOW findings

Deduplicate by file:line (keep the most detailed finding).

### Step 5: Generate Report

```
+==============================================================================+
|                    APPLICATION VULNERABILITY SCAN REPORT                       |
+==============================================================================+
|                                                                              |
|  Target: {path}                                                              |
|  Date: {timestamp}                                                           |
|  Scanner: Dominion Flow /fire-vuln-scan (Claude Opus 4.6)                      |
|  Mode: {quick | deep}                                                        |
|                                                                              |
|  Files Scanned: {count}                                                      |
|  Findings: {total} ({critical} critical, {high} high, {medium} medium)       |
|  False Positives Filtered: {count}                                           |
|                                                                              |
+==============================================================================+
| VERDICT: {SECURE | NEEDS ATTENTION | AT RISK}                                |
+------------------------------------------------------------------------------+
|                                                                              |
|  CRITICAL: {count}                                                           |
|  HIGH:     {count}                                                           |
|  MEDIUM:   {count}                                                           |
|  LOW:      {count}                                                           |
|                                                                              |
+------------------------------------------------------------------------------+
| TOP FINDINGS                                                                  |
+------------------------------------------------------------------------------+
|                                                                              |
|  1. [{severity}] {title}                                                     |
|     File: {path}:{line}                                                      |
|     OWASP: {category}                                                        |
|     Confidence: {level}                                                      |
|                                                                              |
|  2. [{severity}] {title}                                                     |
|     ...                                                                      |
|                                                                              |
+==============================================================================+
```

Display top 10 findings in terminal. Full report saved if `--report` flag.

### Step 6: Save Report

**If `--report` flag:**

Save to two locations:
1. `.planning/security/vuln-scan-{date}.md` — project-local
2. `C:\Users\FirstName\Documents\Claude Reports\{project}-vuln-scan-{date}.md` — global

**Report format:** Full markdown with all findings, severity, confidence, code snippets, suggested fixes, and OWASP mapping.

**Offer next steps:**
```
+------------------------------------------------------------------------------+
| NEXT STEPS                                                                    |
+------------------------------------------------------------------------------+
|                                                                              |
|  Fix critical findings:                                                      |
|    /fire-debug {VULN-ID} — investigate and fix a specific vulnerability     |
|                                                                              |
|  Re-scan after fixes:                                                        |
|    /fire-vuln-scan {path} --category {category}                             |
|                                                                              |
|  Full project verification:                                                  |
|    /fire-4-verify — includes security as verification dimension             |
|                                                                              |
+------------------------------------------------------------------------------+
```

---

## Integration Points

| Command | Integration |
|---------|------------|
| `/fire-4-verify` | Add security check dimension: "Run vuln scan if not done this phase" |
| `/fire-debug` | Can target specific VULN-IDs for investigation |
| `/fire-3-execute` | Optional pre-commit security check on changed files |
| `/fire-dashboard` | Show last scan date and finding count |
| `/fire-loop` | Include vuln-scan in verification stage |

---

## Severity Definitions

| Level | Meaning | Examples |
|-------|---------|---------|
| CRITICAL | Exploitable remotely, leads to data breach or RCE | NoSQL injection with traced exploit path, auth bypass, hardcoded production secrets |
| HIGH | Significant security weakness, likely exploitable | Missing auth on admin routes, IDOR, XSS with user content |
| MEDIUM | Security weakness, requires specific conditions | Missing security headers, verbose errors, weak password policy |
| LOW | Best practice violation, minimal real-world risk | Missing rate limiting on non-sensitive endpoint, deprecated crypto function |

---

## Examples

```bash
# Quick scan of entire project
/fire-vuln-scan C:\path\to\your-project

# Deep scan with full reasoning per finding
/fire-vuln-scan C:\path\to\your-project --deep

# Scan only injection vulnerabilities
/fire-vuln-scan --category injection

# Scan server-side only, save report
/fire-vuln-scan --server-only --report

# Critical findings only
/fire-vuln-scan --critical-only --report

# Scan after fixing, compare to previous
/fire-vuln-scan --report
```

---

## Success Criteria

- [ ] Target files enumerated (routes, controllers, middleware, models, config)
- [ ] 3-4 parallel scan agents spawned with OWASP-mapped checklists
- [ ] All agents returned findings
- [ ] Self-verification judge filtered false positives
- [ ] Findings merged and deduplicated
- [ ] Report generated with severity, confidence, file:line, suggested fixes
- [ ] Report saved (if --report)
- [ ] Next steps offered to user

---

## References

- Claude Code Security (Anthropic 2026): https://www.anthropic.com/news/claude-code-security
- OWASP Top 10 2021: https://owasp.org/Top10/
- OWASP Agentic Top 10 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- Agent-as-Judge Self-Verification: https://arxiv.org/abs/2401.10020
- Express Security Best Practices: https://expressjs.com/en/advanced/best-practice-security.html
- Mongoose Security: https://mongoosejs.com/docs/security.html

## Related Skills

- `security/application-vuln-patterns.md` — MERN vulnerability patterns with code examples
- `security/agent-security-scanner.md` — Agent security (prompt injection, MCP poisoning)
- `deployment-security/SECURITY.md` — Deployment security patterns
