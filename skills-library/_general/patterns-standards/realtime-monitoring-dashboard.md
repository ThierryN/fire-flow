---
name: Real-Time Monitoring Dashboard
category: patterns-standards
version: 1.0.0
contributed: 2026-02-24
tags: [react, typescript, vite, tailwind, express, sse, chokidar, dashboard, monitoring, dark-theme]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Real-Time Monitoring Dashboard

## Problem

You need a visual dashboard to monitor multiple projects, services, and agents in real-time. Data comes from diverse sources: Markdown state files on disk, vector databases (Qdrant), git repositories, HTTP service endpoints. The dashboard must update live without polling every source continuously, and it needs a polished dark-themed UI with loading states.

## Solution Pattern

**Vite + React 18 + TypeScript + Tailwind + Express backend + SSE push updates + Chokidar file watching**

An Express backend acts as the data aggregation layer, parsing local files, querying APIs, and running git commands. It serves data via REST endpoints and pushes live updates via Server-Sent Events (SSE) when watched files change. A Vite dev server proxies `/api/*` to Express, giving hot module reload for the React frontend while the backend handles the data.

## Architecture

```
Browser (React + Tailwind)
    |
    +-- GET /api/projects        --> Express parses STATE.md files
    +-- GET /api/memory           --> Express queries Qdrant REST API
    +-- GET /api/git-timeline     --> Express runs git log across repos
    +-- GET /api/voice-status     --> Express proxies voice-bridge:7899
    +-- GET /api/debug-tracker    --> Express parses debug/ directories
    +-- SSE /api/events           --> Express pushes Chokidar file changes
    |
Vite Dev Server (port 5173)
    |
    +-- proxy: /api/* --> Express (port 3101)
    |
Express Backend (port 3101)
    |
    +-- Chokidar watching C:\path\to\repos\*\.planning\STATE.md
    +-- Qdrant REST API (port 6335)
    +-- git log subprocess
    +-- HTTP fetch to service sidecars
```

### Panel Architecture

Each dashboard panel is a self-contained React component owning its data fetching, state, error handling, and polling logic.

| Panel | Data Source | Update Strategy |
|-------|------------|-----------------|
| `ProjectOverview` | STATE.md parser | SSE push on file change |
| `PhaseProgress` | ROADMAP.md parser | SSE push on file change |
| `MemoryHealth` | Qdrant REST API | 60s polling |
| `GitTimeline` | `git log --format` | 30s polling |
| `DebugTracker` | `.planning/debug/` dir | SSE push on file change |
| `VoiceBridgeStatus` | HTTP sidecar (:7899) | 10s polling |
| `RecentActivity` | Aggregated from all sources | Derived from other panels |

## Code Examples

### Express Backend with File Parsing

```typescript
// server/index.ts
import express from "express";
import cors from "cors";
import chokidar from "chokidar";
import { readFileSync, existsSync } from "fs";
import { glob } from "glob";
import { execSync } from "child_process";

const app = express();
app.use(cors());

const REPOS_DIR = "C:/path/to/repos";
const PORT = 3101;

// --- SSE Setup ---
const sseClients: Set<express.Response> = new Set();

app.get("/api/events", (req, res) => {
  res.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
  });
  sseClients.add(res);
  req.on("close", () => sseClients.delete(res));
});

function broadcast(event: string, data: unknown) {
  const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
  sseClients.forEach((client) => client.write(payload));
}

// --- Chokidar File Watcher ---
const watcher = chokidar.watch(`${REPOS_DIR}/*/.planning/STATE.md`, {
  ignoreInitial: true,
  awaitWriteFinish: { stabilityThreshold: 500 },
});

watcher.on("change", (filePath) => {
  const project = filePath.split(/[/\\]/)[3]; // Extract repo name
  const state = parseStateMd(filePath);
  broadcast("project-update", { project, state });
});

// --- STATE.md Parser ---
interface ProjectState {
  name: string;
  phase: string;
  status: string;
  lastModified: string;
  tasks: { name: string; done: boolean }[];
}

function parseStateMd(filePath: string): ProjectState | null {
  if (!existsSync(filePath)) return null;
  const content = readFileSync(filePath, "utf-8");
  const lines = content.split("\n");

  const name = lines.find((l) => l.startsWith("# "))?.slice(2).trim() || "Unknown";
  const phase = lines.find((l) => /^## (Current )?Phase/i.test(l))?.replace(/^## (Current )?Phase:?\s*/i, "").trim() || "Unknown";
  const status = lines.find((l) => /^Status:/i.test(l))?.replace(/^Status:\s*/i, "").trim() || "unknown";

  const tasks = lines
    .filter((l) => /^- \[[ x]\]/.test(l))
    .map((l) => ({
      name: l.replace(/^- \[[ x]\]\s*/, "").trim(),
      done: l.includes("[x]"),
    }));

  return { name, phase, status, lastModified: new Date().toISOString(), tasks };
}

// --- Projects Endpoint ---
app.get("/api/projects", async (_req, res) => {
  const stateFiles = await glob(`${REPOS_DIR}/*/.planning/STATE.md`);
  const projects = stateFiles
    .map((f) => parseStateMd(f))
    .filter(Boolean);
  res.json(projects);
});

// --- Git Timeline Endpoint ---
app.get("/api/git-timeline", async (_req, res) => {
  const repos = await glob(`${REPOS_DIR}/*/.git`, { onlyDirectories: true });
  const commits = repos.flatMap((gitDir) => {
    const repoDir = gitDir.replace(/[/\\]\.git$/, "");
    const repoName = repoDir.split(/[/\\]/).pop();
    try {
      const log = execSync(
        `git -C "${repoDir}" log --format="%H|%s|%an|%aI" -20`,
        { encoding: "utf-8", timeout: 5000 }
      );
      return log.trim().split("\n").filter(Boolean).map((line) => {
        const [hash, message, author, date] = line.split("|");
        return { repo: repoName, hash, message, author, date };
      });
    } catch {
      return [];
    }
  });
  // Sort all commits by date descending
  commits.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  res.json(commits.slice(0, 50));
});

// --- Qdrant Memory Health ---
app.get("/api/memory", async (_req, res) => {
  try {
    const resp = await fetch("http://127.0.0.1:6335/collections/power_flow_memory");
    const data = await resp.json();
    res.json({
      points: data.result?.points_count || 0,
      segments: data.result?.segments_count || 0,
      status: data.result?.status || "unknown",
    });
  } catch {
    res.json({ points: 0, segments: 0, status: "offline" });
  }
});

// --- Voice Bridge Status Proxy ---
app.get("/api/voice-status", async (_req, res) => {
  try {
    const resp = await fetch("http://127.0.0.1:7899/status", { signal: AbortSignal.timeout(2000) });
    const data = await resp.json();
    res.json(data);
  } catch {
    res.json({ service: "voice-bridge", status: "offline" });
  }
});

app.listen(PORT, () => console.log(`Dashboard API on http://localhost:${PORT}`));
```

### Vite Config with Proxy

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:3101",
        changeOrigin: true,
      },
    },
  },
});
```

### React Panel with Polling and SSE

```tsx
// src/components/ProjectOverview.tsx
import { useState, useEffect, useRef } from "react";

interface Project {
  name: string;
  phase: string;
  status: string;
  lastModified: string;
  tasks: { name: string; done: boolean }[];
}

export function ProjectOverview() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Initial fetch
  useEffect(() => {
    fetch("/api/projects")
      .then((r) => r.json())
      .then((data) => {
        setProjects(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // SSE for live updates
  useEffect(() => {
    const es = new EventSource("/api/events");
    eventSourceRef.current = es;

    es.addEventListener("project-update", (e) => {
      const update = JSON.parse(e.data);
      setProjects((prev) =>
        prev.map((p) => (p.name === update.project ? { ...p, ...update.state } : p))
      );
    });

    es.onerror = () => {
      es.close();
      // Reconnect after 5s
      setTimeout(() => {
        eventSourceRef.current = new EventSource("/api/events");
      }, 5000);
    };

    return () => es.close();
  }, []);

  if (loading) return <SkeletonCard lines={4} />;

  return (
    <div className="glass-card">
      <h2 className="text-lg font-semibold text-zinc-100 mb-4">Projects</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {projects.map((project) => (
          <div key={project.name} className="metric-card">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-zinc-200">{project.name}</h3>
              <StatusBadge status={project.status} />
            </div>
            <p className="text-sm text-zinc-400">{project.phase}</p>
            <ProgressBar tasks={project.tasks} />
          </div>
        ))}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    active: "bg-green-500/20 text-green-400",
    blocked: "bg-red-500/20 text-red-400",
    planning: "bg-indigo-500/20 text-indigo-400",
    complete: "bg-zinc-500/20 text-zinc-400",
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full ${colors[status] || colors.planning}`}>
      {status}
    </span>
  );
}

function ProgressBar({ tasks }: { tasks: { done: boolean }[] }) {
  const done = tasks.filter((t) => t.done).length;
  const pct = tasks.length ? Math.round((done / tasks.length) * 100) : 0;
  return (
    <div className="mt-3">
      <div className="flex justify-between text-xs text-zinc-500 mb-1">
        <span>{done}/{tasks.length} tasks</span>
        <span>{pct}%</span>
      </div>
      <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
        <div className="h-full bg-indigo-500 rounded-full transition-all duration-500"
             style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function SkeletonCard({ lines }: { lines: number }) {
  return (
    <div className="glass-card animate-pulse">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="h-4 bg-zinc-800 rounded mb-3"
             style={{ width: `${70 + Math.random() * 30}%` }} />
      ))}
    </div>
  );
}
```

### Dark Theme Design System

```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-zinc-950 text-zinc-100 antialiased;
    font-family: "Inter", system-ui, -apple-system, sans-serif;
  }
}

@layer components {
  .glass-card {
    @apply bg-zinc-900/60 backdrop-blur-sm border border-zinc-800/50
           rounded-xl p-6 shadow-lg;
  }

  .metric-card {
    @apply bg-zinc-800/40 border border-zinc-700/30 rounded-lg p-4
           hover:border-indigo-500/30 transition-colors duration-200;
  }

  .accent-glow {
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.15);
  }
}

@layer utilities {
  .animate-fade-in {
    animation: fadeIn 0.3s ease-out;
  }
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
  }
}
```

### Tailwind Config for Dark Theme

```typescript
// tailwind.config.ts
import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: "#09090b",       // zinc-950
          card: "#18181b",     // zinc-900
          accent: "#6366f1",   // indigo-500
          success: "#22c55e",  // green-500
          danger: "#ef4444",   // red-500
          warning: "#f59e0b",  // amber-500
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
```

## Implementation Steps

1. **Scaffold with Vite** -- `npm create vite@latest -- --template react-ts`. Add Tailwind, set up dark theme CSS.
2. **Create Express backend** in `server/` directory. Add TypeScript, nodemon for dev.
3. **Build the STATE.md parser** -- regex-based extraction of phase, status, tasks from Markdown.
4. **Add Chokidar watcher** for `.planning/STATE.md` files. Wire to SSE broadcast.
5. **Build the SSE endpoint** -- `/api/events` with client tracking and reconnection.
6. **Configure Vite proxy** -- `/api/*` forwards to Express port.
7. **Build panels one at a time** -- Start with ProjectOverview (file-based), then add MemoryHealth (API), GitTimeline (subprocess), VoiceBridgeStatus (HTTP proxy).
8. **Add skeleton loaders** -- Every panel shows a pulsing skeleton while its data loads.
9. **Add polling intervals** -- 10s for volatile sources (voice status), 60s for stable sources (memory).
10. **Wire SSE into React** -- `EventSource` in `useEffect` with reconnection logic.
11. **Polish** -- glass-card styling, status badges, progress bars, animate-fade-in on data arrival.

## When to Use

- Monitoring multiple independent projects from a single view
- Aggregating data from diverse sources (files, APIs, databases, git)
- Need live updates without heavy WebSocket infrastructure
- Building an internal developer tools dashboard
- When data sources are heterogeneous (Markdown files, REST APIs, CLI output)

## When NOT to Use

- High-frequency data (>10 updates/sec) -- SSE can lag; use WebSockets or gRPC streaming
- Public-facing dashboards with authentication needs -- add auth middleware first
- Simple single-project monitoring -- a terminal watch command may suffice
- When all data comes from a single database -- use that database's built-in dashboard tools

## Common Mistakes

1. **Not debouncing Chokidar events** -- File saves trigger multiple rapid change events. Use `awaitWriteFinish` with a stabilityThreshold (500ms works well).
2. **SSE reconnection storms** -- If the server goes down, `EventSource` auto-reconnects aggressively. Add exponential backoff in the `onerror` handler.
3. **Polling too frequently** -- Each poll spawns a subprocess (git log) or HTTP request. 10s minimum for active sources, 60s for stable ones.
4. **Forgetting CORS on Express** -- The Vite proxy handles dev, but if anyone accesses Express directly, CORS blocks the response. Always add `cors()` middleware.
5. **Not handling missing STATE.md files** -- Repos without `.planning/STATE.md` should be silently skipped, not crash the parser.
6. **Blocking Express with synchronous git commands** -- `execSync` blocks the event loop. For many repos, use `exec` with promises or a worker thread.
7. **Stale SSE connections** -- Dead clients stay in the set. Clean up on `req.on("close")` and periodically sweep.

## Related Skills

- `python-desktop-app-architecture.md` -- The status sidecar pattern consumed by this dashboard
- `multi-project-autonomous-build.md` -- The methodology that creates multiple projects monitored here

## References

- Contributed from: **claude-mission-control** (`C:\path\to\repos\claude-mission-control`)
- Vite proxy docs: https://vitejs.dev/config/server-options.html#server-proxy
- SSE spec: https://html.spec.whatwg.org/multipage/server-sent-events.html
- Chokidar: https://github.com/paulmillr/chokidar
- Tailwind dark mode: https://tailwindcss.com/docs/dark-mode
