---
name: Multi-Project Autonomous Build
category: methodology
version: 1.0.0
contributed: 2026-02-24
tags: [autonomous, multi-project, subagents, methodology, parallel-execution, monitoring, config-first]
difficulty: hard
usage_count: 0
success_rate: 100
---

# Multi-Project Autonomous Build

## Problem

You need to build 3+ independent projects simultaneously without human bottlenecks. Each project has its own repo, stack, and requirements, but they may share infrastructure (dashboards monitoring services, services exposing state to dashboards). Sequential building wastes time. Asking for approval between every step wastes attention. You need an autonomous workflow that plans, executes, verifies, and advances across all projects with minimal human intervention.

## Solution Pattern

**Autonomous execution with subagent parallelism, status sidecars for monitoring, config-first development**

Define all projects in a single plan document. Verify they are independent (no cross-repo file edits). Execute each project through a plan-execute-verify-advance loop using `/fire-autonomous`. Use status sidecars (lightweight HTTP endpoints) on each service so a central dashboard can monitor everything. Start every project with config-first development: define the full config schema with defaults before writing any feature code.

## Architecture

```
Human (User)
    |
    +-- Approves plan document (one-time)
    |
Autonomous Loop (per project)
    |
    +-- Plan Phase: Read requirements, define phases, create STATE.md
    +-- Execute Phase: Build features per phase
    +-- Verify Phase: Run tests, check endpoints, validate UI
    +-- Advance Phase: Update STATE.md, commit, move to next phase
    |
    +-- Status Sidecar (per service)
    |       +-- HTTP JSON endpoint on dedicated port
    |       +-- Exposes: version, uptime, component status, queue sizes
    |
    +-- Central Dashboard (optional)
            +-- Polls all sidecar endpoints
            +-- Watches STATE.md files via Chokidar
            +-- SSE pushes updates to browser

Subagent Strategy:
    +-- Research Agents (parallel, read-only) -- explore docs, APIs, libs
    +-- Execution Agents (sequential within project) -- build features
    +-- Verification Agents (parallel post-execution) -- test, validate
```

## Workflow

### Phase 1: Plan Document

Create a single plan document that defines all projects and their phases. This is the one artifact the human approves before autonomous execution begins.

```markdown
# Multi-Project Build Plan

## Projects

### 1. Voice Bridge v4
- Repo: C:\path\to\repos\voice-bridge-v3
- Stack: Python 3.11, PyQt6, RealtimeSTT, edge-tts
- Independence: Own repo, own venv, no shared code
- Phases:
  1. Config system with deep_merge defaults
  2. STT engine with Qt signal bridge
  3. TTS engine with audio queue
  4. Overlay + system tray
  5. Status sidecar on port 7899
  6. Claude integration + post-processing
  7. Settings dialog

### 2. Mission Control Dashboard
- Repo: C:\path\to\repos\claude-mission-control
- Stack: Vite, React 18, TypeScript, Tailwind, Express
- Independence: Own repo, consumes other projects' APIs (read-only)
- Phases:
  1. Vite + React + Tailwind scaffold + dark theme
  2. Express backend + STATE.md parser
  3. Panel components (Projects, Memory, Git, Debug)
  4. SSE live updates via Chokidar
  5. Voice Bridge status panel (consumes sidecar)

### 3. Ministry-LLM Bible App
- Repo: C:\path\to\repos\ministry-llm
- Stack: React, Vite, Tailwind, Express, Prisma, Qdrant
- Independence: Own repo, own database, no shared code
- Phases:
  1. Theme system (CSS custom properties, 22 themes)
  2. Prisma schema + seed data
  3. Qdrant verse embeddings
  4. Graph canvas with custom nodes
  5. Interlinear viewer
  6. AI analysis integration

## Cross-Project Dependencies (NONE that block parallel execution)
- Dashboard reads Voice Bridge sidecar (port 7899) -- but gracefully handles offline
- Dashboard reads STATE.md files -- but files exist from phase 1 of each project
- No shared source files, no shared databases, no shared build outputs
```

### Phase 2: Independence Verification

Before starting autonomous execution, verify:

```
Independence Checklist:
[x] Each project is in its own repository
[x] No shared source files between projects
[x] No shared database instances (or isolated schemas)
[x] No build output dependencies
[x] Cross-project communication is HTTP only (graceful on failure)
[x] Each project can be built and tested independently
```

### Phase 3: Autonomous Execution Loop

For each project, execute this loop per phase:

```
/fire-autonomous [project-name] [phase-number]

1. READ: Load project plan + STATE.md + current phase requirements
2. PLAN: Break phase into implementation steps
3. EXECUTE: Build each step, commit after each
4. VERIFY: Run tests, check endpoints, validate outputs
5. ADVANCE: Update STATE.md phase status, commit
6. LOOP: Move to next phase or next project
```

### Phase 4: Status Sidecars for Monitoring

Every long-running service exposes a JSON status endpoint:

```python
# Minimal status sidecar (Python)
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class StatusHandler(BaseHTTPRequestHandler):
    state = {"service": "my-app", "status": "running"}

    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(self.state).encode())
        else:
            self.send_error(404)

    def log_message(self, *args):
        pass

def start_sidecar(port, state_dict):
    StatusHandler.state = state_dict
    server = HTTPServer(("127.0.0.1", port), StatusHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
```

```typescript
// Minimal status sidecar (Node.js/Express)
import express from "express";

export function startSidecar(port: number, getState: () => object) {
  const app = express();
  app.get("/status", (_req, res) => {
    res.json(getState());
  });
  app.listen(port, "127.0.0.1");
}
```

### Phase 5: Dashboard Consumes All Endpoints

The central dashboard polls all sidecar endpoints and aggregates state:

```typescript
// Dashboard backend: aggregate all service statuses
const SERVICES = [
  { name: "voice-bridge", url: "http://127.0.0.1:7899/status" },
  { name: "qdrant", url: "http://127.0.0.1:6335/collections" },
  { name: "ollama", url: "http://127.0.0.1:11434/api/tags" },
  { name: "neo4j", url: "http://127.0.0.1:7474" },
];

app.get("/api/services", async (_req, res) => {
  const statuses = await Promise.allSettled(
    SERVICES.map(async (svc) => {
      const resp = await fetch(svc.url, { signal: AbortSignal.timeout(2000) });
      const data = await resp.json();
      return { ...svc, status: "online", data };
    })
  );

  res.json(
    statuses.map((result, i) => {
      if (result.status === "fulfilled") return result.value;
      return { ...SERVICES[i], status: "offline", error: result.reason?.message };
    })
  );
});
```

## Config-First Development

**Define the full config schema with defaults BEFORE building any feature.**

This is the single most important pattern for autonomous builds. When every feature starts as a config entry, you get:
- Self-documenting feature list (the config IS the feature manifest)
- Old config files auto-upgrade via `deep_merge` (new keys get defaults)
- Settings UI can be auto-generated from the config schema
- Feature flags are built-in (just toggle config values)

```python
# Config-first: define EVERYTHING before building anything
DEFAULT_CONFIG = {
    "stt": {
        "enabled": True,
        "model": "base.en",
        "language": "en",
        "wake_word": "hey claude",
        "wake_word_debounce_ms": 2000,
    },
    "tts": {
        "enabled": True,
        "engine": "edge-tts",
        "voice": "en-US-AriaNeural",
    },
    "overlay": {
        "enabled": True,
        "position": "bottom-right",
        "opacity": 0.85,
    },
    "status_server": {
        "enabled": True,
        "port": 7899,
    },
    # ... every feature has a config entry from day 1
}

def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge. Override wins. New base keys auto-appear."""
    from copy import deepcopy
    result = deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result
```

## Subagent Strategy

### Research Agents (Parallel, Read-Only)

Use the Task tool to spawn multiple research agents simultaneously. They explore documentation, APIs, and libraries without modifying any files.

```
Research agents (parallel):
  - Agent 1: "Research PyQt6 transparent overlay patterns"
  - Agent 2: "Research pystray system tray integration with Qt"
  - Agent 3: "Research RealtimeSTT configuration options"

All 3 run simultaneously. Results feed into the execution plan.
```

### Execution Agents (Sequential Within Project)

Within a single project, execution must be sequential. Files change, and concurrent edits to the same repo cause conflicts.

```
Execution (sequential per project, parallel across projects):
  Project A: Phase 1 → Phase 2 → Phase 3
  Project B: Phase 1 → Phase 2 → Phase 3
  Project C: Phase 1 → Phase 2 → Phase 3

  A, B, C run in parallel (different repos).
  Phases within each project run sequentially (same repo).
```

### Verification Agents (Parallel Post-Execution)

After execution, spawn parallel verification agents:

```
Verification agents (parallel):
  - Agent 1: "Run pytest in voice-bridge-v3, verify all pass"
  - Agent 2: "curl localhost:3101/api/projects, verify JSON response"
  - Agent 3: "Run prisma migrate status in ministry-llm"
```

## Parallel Execution Rules

1. **Projects MUST be independent repos.** Never edit the same repository from multiple execution contexts.
2. **Cross-project communication MUST be HTTP only.** No shared files, no shared databases (or use isolated schemas).
3. **Each project gets its own execution context.** Own working directory, own git state, own STATE.md.
4. **Graceful degradation on cross-project dependencies.** If the dashboard can't reach the voice bridge sidecar, it shows "offline" -- it doesn't crash.
5. **Commit after each phase, not after each line.** Atomic phase commits make rollback clean.
6. **STATE.md is the ground truth.** If a project's STATE.md says Phase 2 is complete, it IS complete. The dashboard reads STATE.md, not internal build state.

## Implementation Steps

1. **Write the plan document** -- Single Markdown file with all projects, phases, and independence checklist.
2. **Get human approval** -- This is the one gate. After approval, autonomous execution begins.
3. **Create STATE.md for each project** -- Initial state: Phase 1, Status: planning.
4. **Execute config-first** -- For each project, define DEFAULT_CONFIG with all features before coding.
5. **Run autonomous loop** -- `/fire-autonomous` per project: plan, execute, verify, advance.
6. **Add status sidecars** -- Each service gets an HTTP /status endpoint on its own port.
7. **Build the dashboard last** -- It consumes everything else. Build it after sidecar endpoints are stable.
8. **Verify cross-project integration** -- Dashboard shows all services, STATE.md files are current, sidecars respond.

## When to Use

- Building 3+ independent projects in a single session
- Projects that will eventually interact (service A exposes API, service B consumes it)
- Hackathon-style builds where time efficiency matters
- When the human wants to approve a plan once and let execution run
- Building a service mesh (multiple services + monitoring dashboard)

## When NOT to Use

- Single project with focused requirements -- autonomous loop overhead is not worth it
- Tightly coupled projects that share source files -- parallel execution will conflict
- Exploratory/research tasks where the plan changes every 10 minutes
- When detailed human review is needed at every step (e.g., security-sensitive code)
- Fewer than 3 projects -- the orchestration overhead exceeds the parallelism benefit

## Common Mistakes

1. **Editing the same repo from multiple agents** -- This causes git conflicts and file corruption. One execution agent per repo at a time.
2. **Not verifying independence before starting** -- If Project A's build output is Project B's input, they're not independent. Restructure first.
3. **Skipping config-first development** -- Without DEFAULT_CONFIG, adding features later breaks existing config files. Users get `KeyError` on upgrade.
4. **Hardcoding sidecar ports** -- Put port numbers in config, not in source code. Two services on the same port crash silently.
5. **Not handling sidecar offline gracefully** -- The dashboard WILL try to reach services that haven't started yet. Return `{ status: "offline" }`, don't throw.
6. **Committing too granularly or too coarsely** -- Commit per phase is the sweet spot. Per-line commits pollute history. Per-project commits make rollback impossible.
7. **Not updating STATE.md** -- If the autonomous loop doesn't update STATE.md after each phase, the dashboard shows stale data and humans lose trust.
8. **Forgetting to seed/migrate databases** -- Each project with a database needs its seed step. Don't assume databases exist from previous sessions.

## Related Skills

- `python-desktop-app-architecture.md` -- One of the projects built with this methodology
- `realtime-monitoring-dashboard.md` -- The dashboard that monitors all projects
- `fullstack-bible-study-platform.md` -- Another project built with this methodology

## References

- Contributed from: **voice-bridge-v4** + **claude-mission-control** + **ministry-llm**
- Repos:
  - `C:\path\to\repos\voice-bridge-v3`
  - `C:\path\to\repos\claude-mission-control`
  - `C:\path\to\repos\ministry-llm`
