# Dominion Flow

**A comprehensive orchestration platform that empowers your Claude agent.**

Dominion Flow gives Claude a complete, structured way to take your project from idea to finished code — with built-in quality checks, session memory, parallel execution, and a library of proven patterns. Think of it as a project management system that lives inside Claude Code.

---

## What Does It Do?

When you start a new project, Claude normally has no memory between sessions, no standard process, and no way to verify its own work. Dominion Flow fixes all of that:

- **Structured workflow** — A numbered pipeline (Plan → Execute → Verify → Handoff) so nothing gets skipped
- **Session memory** — Claude picks up exactly where it left off, every time
- **Parallel execution** — Multiple tasks run at the same time, safely, so work gets done faster
- **Built-in quality gates** — A comprehensive checklist verifies every phase before moving on
- **Skills library** — A growing collection of proven code patterns Claude can reuse instead of reinventing every time

---

## Who Is This For?

This plugin is for anyone using Claude Code who wants:
- Consistent, repeatable results on complex projects
- Claude to remember what it was doing between sessions
- Code that gets reviewed and verified, not just written

**No prior experience with orchestration or AI agents required.**

---

## Quick Install

**Prerequisite:** You need [Claude Code](https://claude.ai/download) installed first. If you don't have it yet, download and install it, then come back here.

1. Open your terminal
2. Run this command:
   ```bash
   claude plugin install ThierryN/fire-flow
   ```
3. Restart Claude Code
4. Type `/fire-0-orient` to check that everything is working

That's it. You're ready to go.

---

## Optional but Recommended: Power Features

The core workflow works out of the box. These extras unlock **persistent memory**, **codebase search**, and **vector-powered context** — features that make Claude dramatically more capable on larger projects.

### Docker Desktop (Required for Qdrant)

Docker Desktop is free software that lets you run Qdrant (the memory database) on your computer without any complex setup. You need to install it before running the Qdrant commands below.

**Windows (PC):**

1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Click **"Download for Windows"**
3. Run the installer (`Docker Desktop Installer.exe`)
4. Follow the prompts — it will ask you to restart your computer
5. After restart, open Docker Desktop from your Start menu and wait for it to finish starting up (the whale icon in your taskbar should stop animating)
6. Open a terminal and verify it worked:
   ```bash
   docker --version
   ```
   You should see something like `Docker version 27.x.x`

> **Windows note:** Docker requires WSL 2 (Windows Subsystem for Linux). If you don't have it or are unsure, open PowerShell as Administrator and run these two commands first — then restart before installing Docker:
> ```powershell
> wsl --update
> wsl --set-default-version 2
> ```
> After restarting, run the Docker installer and choose **"Use WSL 2 instead of Hyper-V"** when prompted.

---

**Mac:**

1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Click **"Download for Mac"** — choose **"Mac with Apple Chip"** if you have an M1/M2/M3/M4 Mac, or **"Mac with Intel Chip"** if you have an older Mac
   - Not sure which chip you have? Click the Apple menu () → **About This Mac** — it will say either "Apple M..." or "Intel"
3. Open the downloaded `.dmg` file and drag Docker to your Applications folder
4. Open Docker from your Applications folder
5. Follow the prompts to allow Docker to run
6. Wait for Docker Desktop to fully start (the whale icon in your menu bar should stop animating)
7. Open Terminal and verify it worked:
   ```bash
   docker --version
   ```
   You should see something like `Docker version 27.x.x`

---

> **Both platforms:** Docker Desktop must be **running** (open in the background) whenever you use Qdrant. You don't need to do anything with it — just make sure it's open.

### Qdrant (Persistent Vector Memory)

Qdrant is a local vector database. It gives Claude persistent memory across sessions — Claude can search your codebase, remember decisions, and recall patterns from past work.

**Install Qdrant (Docker):**
```bash
docker pull qdrant/qdrant
docker run -d -p 6335:6333 --name qdrant qdrant/qdrant
```

Or download the standalone binary from [qdrant.tech/documentation/quick-start](https://qdrant.tech/documentation/quick-start/).

### Ollama (Local Embeddings)

Ollama runs embedding models locally. Required for the codebase memory MCP server.

**Install Ollama:** [ollama.com](https://ollama.com)

```bash
# After installing Ollama, pull an embedding model:
ollama pull nomic-embed-text
```

### Codebase Context MCP Server

Once Qdrant and Ollama are running, add the codebase-context MCP to Claude Code. This gives Claude the ability to index and semantically search your entire codebase.

Ask Claude Code to help you set up the `fire-flow-memory` MCP server, or configure it manually in your `~/.claude/mcp.json`.

> **Note:** These are optional. Dominion Flow works without them — they just make Claude smarter on complex, long-running projects.

---

## Your First Project (5 Minutes)

Start a new project with one command:

```bash
/fire-1-new
```

Claude will ask you a few simple questions about your project, then set everything up automatically. After that, the numbered commands walk you through each step:

```
/fire-1-new      → Start your project (asks you questions, creates the plan)
/fire-2-plan 1   → Plan the first phase of work
/fire-3-execute 1 → Build it (Claude does the coding)
/fire-4-verify 1  → Check that everything actually works
/fire-5-handoff   → Save your progress before closing
/fire-6-resume    → Pick up where you left off next session
```

**Want Claude to handle everything automatically?**
After `/fire-1-new`, just run:
```bash
/fire-autonomous
```
Claude will plan, build, and verify every phase without you having to type each command.

---

## Key Features

| Feature | What It Does |
|---------|-------------|
| 39 slash commands | Every task has a dedicated command — no guessing |
| Skills library | Proven patterns for auth, payments, APIs, and more |
| Breath-based parallelism | Independent tasks run at the same time |
| Multi-point verification | Every phase gets scored before moving on |
| Session handoffs | Claude remembers everything between sessions |
| Circuit breaker | Stops loops that are stuck or going in circles |
| Auto skill extraction | Useful patterns discovered during work get saved automatically |
| Playwright E2E testing | Automated browser testing built in |

---

## All 39 Commands

Commands are grouped into 7 tiers. You only need Tier 1 for most projects.

| Tier | Purpose | Key Commands |
|------|---------|-------------|
| 1 — Core Workflow | The main pipeline | `/fire-1-new` through `/fire-6-resume` |
| 2 — Autonomous | Full autopilot | `/fire-autonomous`, `/fire-loop` |
| 3 — Debug & Discover | Investigate problems | `/fire-debug`, `/fire-map-codebase` |
| 4 — Verification | Quality gates | `/fire-7-review`, `/fire-verify-uat` |
| 5 — Skills | Manage the pattern library | `/fire-search`, `/fire-add-new-skill` |
| 6 — Analytics & PM | Track progress | `/fire-dashboard`, `/fire-todos` |
| 7 — Milestones | Long-term projects | `/fire-new-milestone`, `/fire-complete-milestone` |

See [COMMAND-REFERENCE.md](./COMMAND-REFERENCE.md) for the complete list with descriptions.

---

## Finding More Skills

The skills library is what makes Dominion Flow powerful. Skills are reusable patterns that Claude draws on during your project — for auth, payments, APIs, database design, testing, and much more.

**Where to find skills:**

- [aitmpl.com/skills](https://www.aitmpl.com/skills) — Curated skill collections, ready to install
- [skillsmp.com](https://skillsmp.com/) — Community skill marketplace
- GitHub — Search for `claude-code-skills` or `dominion-flow-skills` to find repos shared by the community

**Installing skills from GitHub:**
```bash
claude plugin install <github-username>/<repo-name>
```

You can also create your own skills as you work. When Claude discovers a useful pattern, `/fire-add-new-skill` saves it to your library automatically.

---

## Documentation

| File | What It Covers |
|------|---------------|
| [QUICK-START.md](./QUICK-START.md) | Step-by-step walkthrough of your first project |
| [COMMAND-REFERENCE.md](./COMMAND-REFERENCE.md) | All 39 commands with descriptions |
| [references/warrior-principles.md](./references/warrior-principles.md) | The WARRIOR operating principles — what they are and why they matter |
| [DOMINION-FLOW-OVERVIEW.md](./DOMINION-FLOW-OVERVIEW.md) | Full system diagrams and architecture |
| [ARCHITECTURE-DIAGRAM.md](./ARCHITECTURE-DIAGRAM.md) | Visual overview of how everything connects |
| [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) | Common problems and how to fix them |

---

## Community

Have questions, want to share what you built, or just want to connect with others learning Claude Code?

**Join the Facebook group:** [Claude Code Community](https://www.facebook.com/groups/1671431084311638)

This is where students and followers ask questions, share projects, and stay up to date.

---

## Support This Project

If you're following along and finding Dominion Flow useful, the best way to help is simple:

- **Star this repo** — it helps others discover it
- **Share it** — pass it along to anyone learning Claude Code or building AI-assisted projects

This is a living project. Your support keeps it growing.

---

## License

MIT License — Copyright (c) 2026 ThierryN

This software is free to use, copy, modify, and distribute. See [LICENSE](./LICENSE) for the full text.


