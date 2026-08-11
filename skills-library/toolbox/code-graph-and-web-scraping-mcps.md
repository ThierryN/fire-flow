---
name: code-graph-and-web-scraping-mcps
category: toolbox
version: 1.0.0
contributed: 2026-02-23
contributor: Power-Flow
last_updated: 2026-02-23
tags: [mcp, refactoring, code-analysis, web-scraping, neo4j, graph-database, firecrawl, codegraphcontext]
difficulty: easy
usage_count: 0
success_rate: 100
---

# Code Graph & Web Scraping MCP Servers for Refactoring

## Overview

Two MCP servers installed for deep code analysis and web research during refactoring:

1. **CodeGraphContext (CGC)** — Indexes codebases into a Neo4j graph database. Provides function call relationships, class hierarchies, dead code detection, dependency tracking, and call chain analysis via MCP tools.

2. **Firecrawl** — Web scraping with JavaScript rendering, anti-bot handling, and proxy rotation. Scrape docs, search the web, map site URLs, and run cloud browser sessions.

## Installation Status

### CodeGraphContext
- **Installed:** `codegraphcontext==0.2.5` via Python 3.12
- **Binary:** `C:\Users\FirstName\AppData\Local\Programs\Python\Python312\Scripts\cgc.exe`
- **Database:** Neo4j 5 Community (Docker: `neo4j-cgc`, ports 7474/7687)
- **Credentials:** `neo4j` / `codegraph123`
- **Config:** `C:\Users\FirstName\.codegraphcontext\.env`
- **MCP:** Added to user scope in `~/.claude.json`
- **Languages:** Python, JavaScript, TypeScript, Java, C/C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin

### Firecrawl
- **CLI Installed:** `firecrawl-cli@1.6.2` (global npm)
- **MCP:** Added to user scope in `~/.claude.json` (via `npx -y firecrawl-mcp`)
- **Auth:** Requires API key — run `firecrawl login --browser` to authenticate
- **Free tier:** Available at https://firecrawl.dev/app/api-keys

## When to Use for Refactoring

### CodeGraphContext — Use When:

- **Understanding call chains:** "What functions call `processPayment()`?" → `cgc find callers processPayment`
- **Dead code detection:** "What functions are never called?" → `cgc analyze dead-code`
- **Dependency mapping:** "What imports does this module use?" → `cgc analyze dependencies`
- **Class hierarchy:** "What extends BaseController?" → `cgc find subclasses BaseController`
- **Impact analysis:** "If I change this function, what breaks?" → `cgc analyze impact functionName`
- **Cyclomatic complexity:** "What are the most complex functions?" → `cgc analyze complexity`
- **Before large refactors:** Index first, query the graph, then plan changes with full dependency knowledge

### Firecrawl — Use When:

- **Reading library docs:** Scrape latest API docs for libraries being refactored into
- **Competitive analysis:** Scrape competitor implementations for design patterns
- **Migration guides:** Extract migration guides from framework websites
- **Stack Overflow research:** Search and scrape specific solutions
- **Changelog analysis:** Scrape release notes to understand breaking changes

## Quick Reference Commands

### CGC CLI (Direct Usage)

```bash
# Set alias for convenience
CGC="C:/Users/FirstName/AppData/Local/Programs/Python/Python312/Scripts/cgc.exe"

# Index a codebase
$CGC index "c:/path/to/my-other-project"

# List indexed repos
$CGC list

# Find function callers
$CGC find callers <function_name>

# Find function callees (what does this call?)
$CGC find callees <function_name>

# Find elements
$CGC find name <exact_name>             # Exact match
$CGC find pattern <substring>           # Substring match (e.g., "Enrollment")
$CGC find type Function                 # All functions
$CGC find variable <var_name>           # Variable lookup
$CGC find content "search text"         # Full-text search in source/docstrings
$CGC find decorator <decorator_name>    # Functions with specific decorator
$CGC find argument <param_name>         # Functions taking specific argument

# Analyze
$CGC analyze callers <function_name>    # What calls this function?
$CGC analyze calls <function_name>      # What does this function call?
$CGC analyze chain <func1> <func2>      # Call chain between two functions
$CGC analyze deps <module_name>         # Module dependencies/imports
$CGC analyze tree <class_name>          # Inheritance hierarchy
$CGC analyze dead-code                  # Unused functions/classes
$CGC analyze complexity                 # Cyclomatic complexity
$CGC analyze overrides <function_name>  # Implementations across classes
$CGC analyze variable <var_name>        # Where defined and used

# Custom Cypher query
$CGC query "MATCH (f:Function)-[:CALLS]->(g:Function) RETURN f.name, g.name LIMIT 20"

# Watch for changes (auto-update graph)
$CGC watch "c:/path/to/my-other-project"

# Doctor/diagnostics
$CGC doctor

# Delete indexed repo
$CGC delete <repo_name>

# Stats
$CGC stats
```

### Firecrawl CLI (Direct Usage)

```bash
# Authenticate (one-time)
firecrawl login --browser

# Search the web
firecrawl search "react query migration guide v5"

# Scrape a page to markdown
firecrawl scrape https://docs.example.com/migration

# Map all URLs on a site
firecrawl map https://docs.example.com

# Check status/credits
firecrawl --status
```

### MCP Tools (Available in Claude Code after restart)

**CodeGraphContext MCP provides:**
- Query function definitions and locations
- Caller/callee relationship queries
- Class hierarchy traversal
- Call chain analysis
- Dead code detection
- Cyclomatic complexity analysis
- Custom Cypher queries against the code graph

**Firecrawl MCP provides:**
- `firecrawl_scrape` — Extract markdown from any URL
- `firecrawl_search` — Web search with optional scraping
- `firecrawl_map` — Discover all URLs on a website
- `firecrawl_crawl` — Extract content from entire websites
- `firecrawl_extract` — Structured data extraction

## Refactoring Workflow Pattern

```
1. INDEX the target codebase with CGC
   cgc index /path/to/project

2. ANALYZE the area you're refactoring
   cgc find callers <function>      # Who uses this?
   cgc analyze impact <function>    # What breaks if I change it?
   cgc analyze dead-code            # What can I safely delete?

3. RESEARCH with Firecrawl (if migrating libraries)
   firecrawl search "library-name migration guide"
   firecrawl scrape <docs-url>

4. PLAN the refactor using graph knowledge
   - You know all callers → safe rename/signature change
   - You know dead code → safe deletion
   - You know call chains → understand blast radius

5. EXECUTE the refactor
   - Use the graph to verify no broken references
   - Re-index after changes to validate

6. VERIFY
   cgc analyze dead-code            # No new dead code introduced?
   cgc stats                        # Graph still consistent?
```

## Prerequisites

| Requirement | Status | Notes |
|-------------|--------|-------|
| Python 3.12 | Installed | `C:\Users\FirstName\AppData\Local\Programs\Python\Python312` |
| Node.js | Installed | Global npm packages available |
| Docker | Running | For Neo4j container |
| Neo4j container | Running | `docker start neo4j-cgc` if stopped |
| Firecrawl API key | PENDING | Run `firecrawl login --browser` |

## Verified Working (2026-02-23)

- **Neo4j Docker:** Running, connected, healthy
- **CGC indexing my-other-project:** 14,900+ variables, 5,306 functions, 1,032 files, 775 modules, 82 directories, 12 classes indexed
- **CGC find pattern:** Returns results with file paths, line numbers, and types
- **CGC analyze:** callers, calls, chain, dead-code, complexity all available
- **MCP server:** Configured in `~/.claude.json` (user scope) — available after Claude Code restart
- **Firecrawl CLI:** v1.6.2 installed globally, auth pending

## Troubleshooting

### Neo4j not connecting
```bash
# Check if container is running
docker ps --filter name=neo4j-cgc
# Start if stopped
docker start neo4j-cgc
# Check doctor
cgc doctor
```

### Firecrawl auth issues
```bash
# Re-authenticate
firecrawl login --browser
# Or set env var
export FIRECRAWL_API_KEY=fc-YOUR-KEY
```

### CGC not in PATH
Use full path: `C:\Users\FirstName\AppData\Local\Programs\Python\Python312\Scripts\cgc.exe`
Or add Python Scripts to PATH.

## Related Skills

- [AVAILABLE_TOOLS_REFERENCE.md](../AVAILABLE_TOOLS_REFERENCE.md) — Full tool inventory
- [power-map-codebase](../../commands/fire-map-codebase.md) — Parallel codebase analysis
- [parallel-explore](../../commands/parallel-explore.md) — Multi-agent code exploration

## References

- [CodeGraphContext GitHub](https://github.com/CodeGraphContext/CodeGraphContext) — 773 stars, 12 language support
- [Firecrawl GitHub](https://github.com/firecrawl/firecrawl-mcp-server) — Official MCP server
- [Firecrawl Claude Plugin](https://github.com/firecrawl/firecrawl-claude-plugin) — Native plugin
- Contributed from: Dominion Flow tooling setup session (2026-02-23)
