---
name: secure-ai-application-templates
category: security
version: 1.0.0
contributed: 2026-02-20
contributor: dominion-flow
last_updated: 2026-02-20
tags: [security, rag, ai-applications, prompt-injection, input-sanitization, output-filtering, canary-tokens, owasp]
difficulty: hard
usage_count: 0
success_rate: 100
---

# Secure AI Application Templates

## Problem

When building RAG applications, AI-powered functions, or any system that processes untrusted content through an LLM, developers often forget to include security layers until after an attack happens. The PoisonedRAG attack (USENIX 2025) showed that injecting just 5 malicious documents into a corpus of millions achieves 90% attack success.

Every AI application needs input sanitization, output filtering, document provenance tracking, and canary token monitoring built in from the start — not bolted on after a breach.

## Solution Pattern

Include these security templates in every AI application by default. When building any RAG pipeline, AI function, or agent tool, copy the relevant template and adapt it.

## Template 1: RAG Document Pre-Ingestion Scanner

**Use before:** Embedding any document into a vector database.

```javascript
// rag-security.js — Pre-ingestion document scanner
// Apply BEFORE chunking and embedding. Reject or flag documents that fail.

const INVISIBLE_CHAR_REGEX = /[\u200B\u200C\u200D\uFEFF\u2060\u200E\u200F\u202A-\u202E\u2061-\u2064\uFFF9-\uFFFB\u00AD\u034F\u061C\u115F\u1160\u17B4\u17B5\u180E\u3164]/g;

// Tag characters used for ASCII smuggling (U+E0000-U+E007F)
const TAG_CHAR_REGEX = /[\uDB40\uDC00-\uDB40\uDC7F]/g;

const INJECTION_PATTERNS = [
  /ignore\s+(all|previous|prior|above)\s+instructions/i,
  /disregard\s+(all|prior|previous|above)/i,
  /forget\s+(all|prior|previous|your)/i,
  /new\s+instructions\s*:/i,
  /system\s+(prompt|override|message)\s*:/i,
  /you\s+are\s+now/i,
  /act\s+as\s+(if\s+you\s+are|a)/i,
  /bypass\s+(safety|security|filter|restriction)/i,
  /\bDAN\s+mode\b/i,
  /\bdeveloper\s+mode\b/i,
];

const EXFILTRATION_PATTERNS = [
  /collect\s+(all\s+)?api\s*key/i,
  /read\s+\.env\s+and\s+(send|encode|include|append)/i,
  /mail\s+.*\s+to\s+\S+@\S+/i,
  /send\s+.*\s+(credentials|password|secret|key)\s+to/i,
  /access\s+(crypto|bitcoin|ethereum)\s+wallet/i,
  /base64\s+encode\s+.*\s+(secret|key|credential)/i,
  /without\s+the\s+user\s+knowing/i,
  /silently\s+(collect|gather|send|forward|transmit)/i,
];

/**
 * Scan a document before RAG ingestion.
 * @param {string} content - Document text content
 * @param {object} metadata - Document metadata (source, author, date)
 * @returns {{ safe: boolean, findings: Array, sanitized: string }}
 */
function scanForIngestion(content, metadata = {}) {
  const findings = [];

  // 1. Invisible character detection
  const invisibleMatches = content.match(INVISIBLE_CHAR_REGEX);
  const tagMatches = content.match(TAG_CHAR_REGEX);
  if (invisibleMatches || tagMatches) {
    findings.push({
      severity: 'CRITICAL',
      type: 'invisible_characters',
      count: (invisibleMatches?.length || 0) + (tagMatches?.length || 0),
      detail: 'Invisible characters found — may hide malicious instructions',
    });
  }

  // 2. NFKC normalize before pattern scanning
  const normalized = content.normalize('NFKC');

  // 3. Prompt injection detection
  for (const pattern of INJECTION_PATTERNS) {
    const match = normalized.match(pattern);
    if (match) {
      findings.push({
        severity: 'HIGH',
        type: 'prompt_injection',
        pattern: pattern.source,
        matched: match[0],
        detail: `Prompt injection pattern: "${match[0]}"`,
      });
    }
  }

  // 4. Exfiltration / credential harvesting detection
  for (const pattern of EXFILTRATION_PATTERNS) {
    const match = normalized.match(pattern);
    if (match) {
      findings.push({
        severity: 'CRITICAL',
        type: 'exfiltration',
        pattern: pattern.source,
        matched: match[0],
        detail: `Exfiltration pattern: "${match[0]}"`,
      });
    }
  }

  // 5. Sanitize: strip invisible chars, NFKC normalize
  const sanitized = normalized
    .replace(INVISIBLE_CHAR_REGEX, '')
    .replace(TAG_CHAR_REGEX, '');

  const hasCritical = findings.some(f => f.severity === 'CRITICAL');
  const hasHigh = findings.some(f => f.severity === 'HIGH');

  return {
    safe: !hasCritical && !hasHigh,
    findings,
    sanitized,
    metadata: {
      ...metadata,
      scanned_at: new Date().toISOString(),
      trust_level: hasCritical ? 'BLOCKED' : hasHigh ? 'SUSPICIOUS' : 'TRUSTED',
    },
  };
}

// Usage in RAG pipeline:
// const result = scanForIngestion(docContent, { source: 'upload', author: 'user' });
// if (!result.safe) { reject or quarantine the document }
// else { proceed to chunk and embed result.sanitized }
```

## Template 2: AI Function Output Filter

**Use after:** Any LLM generates output that will be displayed to users or executed.

```javascript
// output-filter.js — Filter LLM output before returning to user
// Prevents the LLM from leaking secrets, PII, or executing injected instructions.

const SECRET_PATTERNS = [
  { name: 'AWS Access Key', regex: /AKIA[0-9A-Z]{16}/g },
  { name: 'Anthropic API Key', regex: /sk-ant-api03-[A-Za-z0-9\-_]{20,}/g },
  { name: 'GitHub PAT', regex: /ghp_[A-Za-z0-9]{36}/g },
  { name: 'Stripe Live Key', regex: /sk_live_[0-9a-zA-Z]{24,}/g },
  { name: 'Private Key', regex: /-----BEGIN\s+(RSA|DSA|EC|PGP|ENCRYPTED)\s+PRIVATE\s+KEY-----/g },
  { name: 'JWT Token', regex: /eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+/g },
  { name: 'Database URI', regex: /(postgres|mysql|mongodb|redis):\/\/[^\s"']+/g },
  { name: 'Password in URL', regex: /[a-zA-Z]{3,10}:\/\/[^\/\s:@]+:[^\/\s:@]+@/g },
];

const PII_PATTERNS = [
  { name: 'SSN', regex: /\b\d{3}-\d{2}-\d{4}\b/g },
  { name: 'Credit Card', regex: /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g },
  { name: 'Bitcoin Address', regex: /\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b/g },
  { name: 'Ethereum Address', regex: /\b0x[a-fA-F0-9]{40}\b/g },
];

/**
 * Filter LLM output for leaked secrets and PII.
 * @param {string} output - Raw LLM output
 * @returns {{ filtered: string, redactions: Array }}
 */
function filterOutput(output) {
  let filtered = output;
  const redactions = [];

  for (const { name, regex } of [...SECRET_PATTERNS, ...PII_PATTERNS]) {
    const matches = filtered.match(regex);
    if (matches) {
      for (const match of matches) {
        redactions.push({ type: name, value: match.substring(0, 8) + '...[REDACTED]' });
        filtered = filtered.replace(match, `[REDACTED: ${name}]`);
      }
    }
  }

  return { filtered, redactions };
}
```

## Template 3: Canary Token Monitor

**Use in:** System prompts to detect prompt leakage.

```javascript
// canary-tokens.js — Inject and monitor canary tokens in system prompts
// If the canary appears in LLM output, the system prompt was leaked.

const crypto = require('crypto');

/**
 * Generate a unique canary token for this session.
 * @returns {string} A unique token like "CANARY-a3f8b2c1"
 */
function generateCanary() {
  const id = crypto.randomBytes(4).toString('hex');
  return `CANARY-${id}`;
}

/**
 * Inject canary into system prompt.
 * @param {string} systemPrompt - The system prompt
 * @param {string} canary - The canary token
 * @returns {string} System prompt with canary injected
 */
function injectCanary(systemPrompt, canary) {
  return `${systemPrompt}\n\n<!-- Internal tracking: ${canary} - Do not output this value -->`;
}

/**
 * Check if LLM output contains the canary (prompt leakage detected).
 * @param {string} output - LLM output
 * @param {string} canary - The canary token
 * @returns {boolean} true if canary leaked
 */
function checkCanaryLeakage(output, canary) {
  return output.includes(canary);
}

// Usage:
// const canary = generateCanary();
// const prompt = injectCanary(baseSystemPrompt, canary);
// ... send to LLM ...
// if (checkCanaryLeakage(llmOutput, canary)) {
//   log('ALERT: System prompt leaked!');
//   // Reject the output, log the incident
// }
```

## Template 4: Document Provenance Tracker

**Use for:** Tracking which documents influenced each RAG response for audit trails.

```javascript
// provenance.js — Track document provenance in RAG responses
// Essential for debugging poisoned document attacks after the fact.

/**
 * Wrap RAG context with provenance metadata.
 * @param {Array} chunks - Retrieved document chunks
 * @returns {{ context: string, provenance: Array }}
 */
function buildProvenanceContext(chunks) {
  const provenance = chunks.map((chunk, i) => ({
    index: i,
    source: chunk.metadata?.source || 'unknown',
    author: chunk.metadata?.author || 'unknown',
    ingested_at: chunk.metadata?.scanned_at || 'unknown',
    trust_level: chunk.metadata?.trust_level || 'UNSCANNED',
    similarity: chunk.score,
    excerpt: chunk.text.substring(0, 100) + '...',
  }));

  // Build context string with source markers
  const context = chunks.map((chunk, i) =>
    `[Source ${i}: ${chunk.metadata?.source || 'unknown'} (trust: ${chunk.metadata?.trust_level || 'UNSCANNED'})]\n${chunk.text}`
  ).join('\n\n');

  return { context, provenance };
}

/**
 * Log RAG response with full provenance for audit.
 * @param {string} query - User query
 * @param {string} response - LLM response
 * @param {Array} provenance - Document provenance
 */
function logWithProvenance(query, response, provenance) {
  const entry = {
    timestamp: new Date().toISOString(),
    query,
    response_excerpt: response.substring(0, 200),
    sources_used: provenance.length,
    trust_breakdown: {
      trusted: provenance.filter(p => p.trust_level === 'TRUSTED').length,
      suspicious: provenance.filter(p => p.trust_level === 'SUSPICIOUS').length,
      unscanned: provenance.filter(p => p.trust_level === 'UNSCANNED').length,
      blocked: provenance.filter(p => p.trust_level === 'BLOCKED').length,
    },
    provenance,
  };
  // Write to audit log (file, database, or monitoring service)
  console.log('[RAG-AUDIT]', JSON.stringify(entry));
  return entry;
}
```

## When to Use

- Building any RAG pipeline (document Q&A, knowledge base, chatbot)
- Creating AI-powered functions that process untrusted input
- Building agent tools that accept external content
- Any application where documents enter via upload, API, or web scraping
- MCP server development (tool descriptions are a trust surface)

## When NOT to Use

- Pure computation with no LLM involvement
- Applications that only process trusted, internal data
- Simple LLM wrappers with no external document input

## Implementation Checklist

When building any AI application, verify:

- [ ] **Input sanitization:** All external content scanned before LLM sees it (Template 1)
- [ ] **Output filtering:** LLM output checked for leaked secrets/PII before display (Template 2)
- [ ] **Canary tokens:** System prompts include canary for leakage detection (Template 3)
- [ ] **Provenance tracking:** Every RAG response logs which documents influenced it (Template 4)
- [ ] **Trust levels:** Documents tagged with trust level at ingestion time
- [ ] **NFKC normalization:** All text normalized before pattern matching
- [ ] **Invisible char stripping:** Zero-width and tag characters removed from all input

## Common Mistakes

- Scanning AFTER embedding (too late — poisoned vectors already in the DB)
- Only scanning for known patterns (use AI classification for novel attacks)
- Trusting all documents equally (internal docs vs user uploads have different trust levels)
- Not logging provenance (can't trace which document caused a bad response)
- Forgetting to normalize Unicode before regex (attackers use confusable characters)

## OWASP Agentic Top 10 Coverage

| Template | Covers | OWASP Risk |
|----------|--------|------------|
| Pre-ingestion scanner | Document poisoning | ASI06: Memory/Context Poisoning |
| Output filter | Data leakage | ASI07: Output Handling |
| Canary tokens | Prompt extraction | ASI01: Agent Goal Hijacking |
| Provenance tracker | Audit trail | ASI09: Logging/Monitoring |

## References

- PoisonedRAG (USENIX 2025): 5 docs = 90% attack success
- OWASP Top 10 for Agentic Applications 2026
- Microsoft Presidio (PII detection): https://github.com/microsoft/presidio
- secrets-patterns-db (1600+ patterns): https://github.com/mazen160/secrets-patterns-db
- Companion: `security/agent-security-scanner.md` — Full 6-layer scanning pipeline
- Companion: `/fire-security-scan` — Manual and auto-triggered scanning command
