# Available Tools & Resources Reference

**Last Updated:** January 2026
**Purpose:** Quick reference for all AI agents on available tools, marketplaces, skills, and plugins.

---

## Quick Start for New Agents

**Before starting work, you have access to:**
- 16 plugin marketplaces with hundreds of skills
- Dominion Flow unified workflow system
- Ralph Wiggum self-iterating loops
- n8n workflow automation knowledge
- WARRIOR workflow for session continuity

**Key commands to remember:**
```bash
/fire-dashboard       # Project status & progress
/fire-debug           # Systematic debugging
/fire-5-handoff       # Create session handoff
```

---

## Plugin Marketplaces (16 Total)

### Official & Core

| Marketplace | Repository | Key Plugins |
|-------------|------------|-------------|
| **claude-plugins-official** | anthropics/claude-plugins-public | figma, sentry, vercel, firebase, stripe, playwright, github |
| **superpowers-marketplace** | obra/superpowers-marketplace | 21 specialized skills for brainstorming, TDD, debugging |
| **anthropic-agent-skills** | anthropics/skills | Official Anthropic example skills |

### Development Workflows

| Marketplace | Repository | Focus |
|-------------|------------|-------|
| **claude-code-workflows** | wshobson/agents | 67 plugins, 99 agents, 107 skills |
| **claude-code-plugins-plus** | jeremylongshore/claude-code-plugins-plus | Comprehensive marketplace & educational hub |
| **compounding-engineering** | EveryInc/compounding-engineering-plugin | Compound engineering practices |
| **claude-code-templates** | davila7/claude-code-templates | Git workflow, testing, documentation |

### Specialized Tools

| Marketplace | Repository | Purpose |
|-------------|------------|---------|
| **n8n-mcp** | czlonkowski/n8n-mcp | n8n workflow automation (1,084 nodes) |
| **n8n-skills** | czlonkowski/n8n-skills | n8n skillset for Claude Code |
| **ralph-wiggum** | UtpalJayNadiger/ralphwiggumexperiment | Self-iterating autonomous loops |
| **hcp-terraform-skills** | hashi-demo-lab/claude-skill-hcp-terraform | HashiCorp Terraform |

### Community Collections

| Marketplace | Repository | Description |
|-------------|------------|-------------|
| **awesome-claude-code-plugins** | ccplugins/awesome-claude-code-plugins | Curated plugins collection |
| **awesome-claude-skills** | ComposioHQ/awesome-claude-skills | Practical skills collection |
| **cc-marketplace** | ananddtyagi/claude-code-marketplace | Community marketplace |
| **mag-claude-plugins** | MadAppGang/claude-code | MAG team's full-stack plugins |
| **thedotmack** | thedotmack/claude-mem | Memory plugins by Alex Newman |

---

## Dominion Flow System

**Location:** `~/.claude/plugins/dominion-flow/`
**Version:** 3.2.0

### Core Commands

| Command | Purpose |
|---------|---------|
| `/fire-1a-new` | Initialize new project with deep context |
| `/fire-new-milestone` | Start a new milestone cycle |
| `/fire-2-plan` | Create detailed execution plan |
| `/fire-3-execute` | Breath-based parallel execution |
| `/fire-4-verify` | Validate features through UAT |
| `/fire-dashboard` | Check status and route to next action |
| `/fire-debug` | Systematic debugging with state |

### Key Concepts

- **CONSCIENCE.md** - Living memory file (<100 lines)
- **Breath-based execution** - Parallel tasks grouped by dependencies
- **Must-haves** - Goal-backward verification (truths, artifacts, key_links)
- **Checkpoints** - Types: auto, human-verify, decision, human-action

### File Structure

```
.planning/
├── PROJECT.md         # Project definition
├── CONSCIENCE.md           # Current position & context
├── VISION.md         # Phase breakdown
├── REQUIREMENTS.md    # Detailed requirements
└── phases/
    └── 01-phase-name/
        ├── 01-BLUEPRINT.md
        ├── 01-RECORD.md
        └── 01-VERIFICATION.md
```

---

## Ralph Wiggum Loops

**Purpose:** Autonomous iteration until success criteria met

### Usage

```bash
/ralph-loop "Build X with tests. Output DONE when all tests pass." \
  --completion-promise "DONE" \
  --max-iterations 50
```

### When to Use

| Good For | Bad For |
|----------|---------|
| Getting test suites to pass | Tasks requiring human judgment |
| Fixing all linter/type errors | Unclear success criteria |
| Features with clear acceptance criteria | Production debugging |

### Key Principles

1. **Completion Promise** - Define success upfront
2. **Threshold Stopping** - Stop at 9/10 or max iterations
3. **Regression Detection** - Recognize mistakes and recover
4. **Specific Critique** - Concrete questions drive improvement

---

## WARRIOR Workflow

**Location:** `~/.claude/plugins/warrior-workflow/`

### Purpose

Session continuity and knowledge preservation across AI agent sessions.

### Key Commands

| Command | Purpose |
|---------|---------|
| `/warrior-handoff` | Create comprehensive handoff package |
| `/warrior-review` | Conduct thorough code review |
| `/warrior-validation` | Verify work is complete and tested |

### Handoff Location

```
C:\Users\FirstName\.claude\warrior-handoffs\
```

### Skills Library Categories

```
skills-library/
├── methodology/           # Patterns, standards, orchestration
├── complexity-metrics/    # Complexity divider, work protocols
├── ecommerce/             # E-commerce implementation
├── integrations/          # Zoom, Stripe, RSS, etc.
├── video-media/           # Video player, YouTube, bookmarks
├── deployment-security/   # Production deployment, Supabase
├── database-solutions/    # RLS, schema enhancements
├── form-solutions/        # PDF forms, SurveyJS
├── advanced-features/     # Plugins, gamification, SEO
├── automation/            # Auto-populate, workflows
├── document-processing/   # Document AI, secure downloads
└── patterns-standards/    # Critical coding patterns
```

---

## Superpowers Skills (21 Total)

### Most Commonly Used

| Skill | When to Use |
|-------|-------------|
| `superpowers:brainstorming` | Before ANY creative work |
| `superpowers:test-driven-development` | When implementing features |
| `superpowers:systematic-debugging` | For any bug investigation |
| `superpowers:verification-before-completion` | Before claiming done |
| `superpowers:requesting-code-review` | After completing tasks |

### Full List

- brainstorming, test-driven-development, systematic-debugging
- verification-before-completion, requesting-code-review
- receiving-code-review, writing-plans, writing-skills
- using-git-worktrees, subagent-driven-development
- executing-plans, finishing-a-development-branch
- dispatching-parallel-agents, using-superpowers

---

## Installed Official Plugins

### Productivity

| Plugin | Purpose |
|--------|---------|
| **playwright** | Browser automation, testing, screenshots |
| **github** | GitHub operations via gh CLI |
| **gitlab** | GitLab operations |
| **greptile** | Code search and understanding |

### Integrations

| Plugin | Purpose |
|--------|---------|
| **figma** | Figma design integration |
| **sentry** | Error tracking and monitoring |
| **vercel** | Vercel deployment |
| **firebase** | Firebase services |
| **stripe** | Payment processing |
| **supabase** | Supabase database |
| **context7** | Library documentation lookup |

### Project Management

| Plugin | Purpose |
|--------|---------|
| **atlassian** | Jira/Confluence integration |
| **asana** | Asana task management |
| **linear** | Linear issue tracking |
| **slack** | Slack messaging |

### Development

| Plugin | Purpose |
|--------|---------|
| **hookify** | Create behavior hooks |
| **plugin-dev** | Plugin development tools |
| **agent-sdk-dev** | Agent SDK development |
| **frontend-design** | Frontend design assistance |
| **code-review** | Code review assistance |
| **feature-dev** | Feature development workflow |
| **pr-review-toolkit** | PR review tools |
| **commit-commands** | Git commit helpers |

---

## MCP Servers Available

| Server | Purpose |
|--------|---------|
| **context7** | Up-to-date library documentation |
| **CodeGraphContext** | Code graph analysis — indexes codebases into Neo4j for call chains, dead code, dependencies, complexity |
| **firecrawl** | Web scraping with JS rendering — scrape docs, search web, map sites (needs API key) |
| **greptile** | Code understanding and PR analysis |
| **playwright** | Browser automation |
| **firebase** | Firebase project management |
| **pinecone** | Vector database for AI search |

---

## Session Start Checklist

Every agent should:

1. **Check WARRIOR handoffs:**
   ```bash
   dir "C:\Users\FirstName\.claude\warrior-handoffs" | Sort-Object LastWriteTime -Descending | Select -First 3
   ```

2. **Check project CONSCIENCE.md** (if using Dominion Flow):
   ```bash
   cat .planning/CONSCIENCE.md 2>/dev/null
   ```

3. **Review recent commits:**
   ```bash
   git log --oneline -10
   ```

4. **Know available tools** (this document)

---

## Quick Command Reference

### Dominion Flow Commands
```bash
/fire-dashboard       # Project status & progress
/fire-1a-new           # Initialize new project
/fire-2-plan N        # Plan phase N
/fire-3-execute N     # Execute phase N
/fire-4-verify        # Validate work
/fire-5-handoff       # Create session handoff
/fire-6-resume        # Resume from handoff
/fire-debug           # Systematic debugging
/fire-loop            # Self-iterating loop
/fire-map-codebase    # Parallel codebase analysis
```

### Superpowers
```bash
# Invoke via Skill tool
superpowers:brainstorming
superpowers:systematic-debugging
superpowers:verification-before-completion
```

### Plugin Skills
```bash
/commit                # Git commit
/review-pr             # Review PR
/feature-dev           # Feature development
/frontend-design       # UI design
```

---

## File Locations Summary

| Resource | Path |
|----------|------|
| Global CLAUDE.md | `C:\Users\FirstName\.claude\CLAUDE.md` |
| WARRIOR Handoffs | `C:\Users\FirstName\.claude\warrior-handoffs\` |
| Plugin Marketplaces | `C:\Users\FirstName\.claude\plugins\marketplaces\` |
| Dominion Flow system | `C:\Users\FirstName\.claude\get-shit-done\` |
| WARRIOR Skills | `C:\Users\FirstName\.claude\plugins\warrior-workflow\skills-library\` |
| Known Marketplaces | `C:\Users\FirstName\.claude\plugins\known_marketplaces.json` |
| Installed Plugins | `C:\Users\FirstName\.claude\plugins\installed_plugins.json` |

---

**Remember:** You have access to powerful tools. Use them proactively to deliver better results faster.
