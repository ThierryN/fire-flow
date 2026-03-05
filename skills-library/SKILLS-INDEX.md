# Dominion Flow Skills Library Index

**Total Skills:** 237 markdown files + Remotion skill (37 rules)
**Categories:** 19 categories + _general scope (7 subcategories) + video-animation (Remotion)
**Last Updated:** 2026-03-01
**Source:** Imported from WARRIOR workflow skills library

---

## Quick Search Tips

- **Find by topic:** Use `Ctrl+F` / `Cmd+F` to search this document
- **Browse by category:** Jump to any category section below
- **File naming:** Uppercase files are guides/references, lowercase are implementation patterns
- **Location:** `C:/Users/FirstName/.claude/plugins/dominion-flow/skills-library/`

---

## Beginner Skills Library

Three tiers of foundational skills for students and new developers. Each skill is self-contained with real code examples.

### Tier 1 — Basics (Start Here)

| Skill | Description |
|-------|-------------|
| [env-variables](basics/env-variables.md) | Keep secrets out of your code using `.env` files |
| [git-commit-conventions](basics/git-commit-conventions.md) | Write clear, readable commit messages |
| [readme-template](basics/readme-template.md) | Document your project so others can use it |
| [error-handling-basics](basics/error-handling-basics.md) | Catch errors gracefully instead of crashing |
| [api-rest-basics](basics/api-rest-basics.md) | Build and call REST APIs the right way |

### Tier 2 — Common Tasks

| Skill | Description |
|-------|-------------|
| [auth-jwt-basics](common-tasks/auth-jwt-basics.md) | User login with JWT tokens and protected routes |
| [database-schema-design](common-tasks/database-schema-design.md) | Design tables that don't break as you grow |
| [async-await-patterns](common-tasks/async-await-patterns.md) | Write async code without callback hell |
| [form-validation](common-tasks/form-validation.md) | Validate user input on both client and server |
| [file-upload-basics](common-tasks/file-upload-basics.md) | Handle file uploads safely |

### Tier 3 — Quality & Safety

| Skill | Description |
|-------|-------------|
| [testing-basics](quality-safety/testing-basics.md) | Write tests that actually catch bugs |
| [security-checklist](quality-safety/security-checklist.md) | The most common security mistakes and how to avoid them |
| [debugging-steps](quality-safety/debugging-steps.md) | Systematic debugging — stop guessing, start finding |
| [deployment-checklist](quality-safety/deployment-checklist.md) | What to verify before going live |

---

## Categories Overview

| Category | Skills | Description |
|----------|--------|-------------|
| [Root Level](#root-level-skills) | 8 | Top-level guides and cross-cutting references |
| [advanced-features](#advanced-features) | 11 | Admin tools, gamification, plugins, newsletters, SEO |
| [api-patterns](#api-patterns) | 0 | API design patterns (reserved) |
| [automation](#automation) | 2 | Auto-populate, form automation, session memory lifecycle |
| [complexity-metrics](#complexity-metrics) | 2 | Code complexity analysis and management |
| [database-solutions](#database-solutions) | 17 | Schema design, migrations, PostgreSQL, RLS, PG-to-MySQL translation, PL/pgSQL variable conflicts |
| [deployment-security](#deployment-security) | 18 | Production deployment, VPS, security hardening |
| [document-processing](#document-processing) | 5 | PDF forms, file downloads, document AI |
| [ecommerce](#ecommerce) | 15 | Stripe, products, donations, GTA compliance |
| [form-solutions](#form-solutions) | 2 | SurveyJS, fillable PDFs |
| [infrastructure](#infrastructure) | 2 | Tauri sidecar bundling, dynamic port IPC, desktop packaging |
| [integrations](#integrations) | 43 | Stripe, PayPal, Zoom, YouTube, Cloudflare, RealtimeSTT, Claude Code |
| [lms-patterns](#lms-patterns) | 44 | Learning management, themes, quizzes, community |
| [methodology](#methodology) | 13 | WARRIOR workflow, session patterns, debugging, agent learning |
| [patterns-standards](#patterns-standards) | 7 | Coding patterns, error resilience, i18n, plugin structure |
| [security](#security) | 1 | SQL injection, path traversal, input validation |
| [testing](#testing) | 1 | Playwright security tests, E2E regression |
| [theology](#theology) | 1 | Biblical pattern analysis for LLM systems |
| [video-media](#video-media) | 16 | Video players, YouTube, Vimeo, progress tracking, crash-resilient recording |
| [_general/frontend](#general-frontend) | 5 | General-scope frontend patterns (any project) |
| [_general/database-solutions](#general-database-solutions) | 2 | General-scope database persistence and vector DB patterns (any project) |
| [_general/performance](#general-performance) | 1 | General-scope performance and caching patterns (any project) |
| [_general/patterns-standards](#general-patterns-standards) | 6 | General-scope design patterns (any project) |
| [_general/methodology](#general-methodology) | 7 | General-scope development methodology |
| [_general/integrations](#general-integrations) | 2 | General-scope MCP and tool integration patterns |

---

## Recent Additions (2026-03-01)

| Skill | Category | Scope | Description |
|-------|----------|-------|-------------|
| cache-augmented-generation | performance | General | Pre-load stable docs into cached prompt prefix instead of RAG — eliminates retrieval overhead for small corpora |
| qdrant-blue-green-aliases | database-solutions | General | Atomic collection alias swaps for zero-downtime Qdrant reindexing and migrations |
| mcp-composite-tool-orchestration | integrations | General | Consolidate 3-5 sequential MCP tool calls into single composite operations — 58-72% token savings |
| claude-code-local-mcp-integration | integrations | General | Register, configure, debug, and test local stdio MCP servers with Claude Code |
| persistent-analysis-storage | database-solutions | General | Dual-storage (localStorage + DB) with favorites, public sharing (nanoid slugs), cursor pagination |
| canvas-bubble-animation-grouping | frontend | General | Absolute-positioned canvas with 3 layout algorithms (golden spiral, rectangular grid, binary filter) + Framer Motion spring animations for 150+ item data exploration |
| react-flow-animated-layout-switching | frontend | General | CSS transitions on React Flow nodes for smooth layout algorithm switching without Framer Motion |
| svg-sparkline-no-charting-library | frontend | General | Pure SVG sparkline chart — 0KB dependency, full interactivity, percentage-based responsive |
| framer-motion-layoutid-grouping | frontend | General | FLIP animations for data re-sorting/re-grouping with Framer Motion layoutId + spring physics |
| domain-specific-layout-algorithms | patterns-standards | General | Pure-function layout registry encoding domain spatial metaphors (mirror arcs, parallel lanes, narrative parabolas) |
| autonomous-multi-phase-build **v2.0** | methodology | General | Atomic phase contract with per-phase tsc+build verification, status tracking, auto-fix loop |
| session-memory-lifecycle | automation | Project | Auto-capture session memories on end + auto-inject on start via Claude Code hooks + Qdrant |

---

## Root Level Skills

| Skill | Description |
|-------|-------------|
| appointment-scheduler-design | Design patterns for appointment scheduling systems |
| AVAILABLE_TOOLS_REFERENCE | Complete reference of available Claude Code tools and plugins |
| toolbox/code-graph-and-web-scraping-mcps | CodeGraphContext (Neo4j graph) + Firecrawl (web scraping) MCP servers for refactoring |
| installer-wizard-patterns | Patterns for building installer/setup wizards |
| LMS_ZOOM_LEARNING_PATHS_INTEGRATION | Integration guide for Zoom with LMS learning paths |
| lms-theme-system | Theme system architecture for LMS platforms |
| SKILLS_LIBRARY_INDEX | Original WARRIOR skills library index |
| supabase-connection-pooler-fix | Fix for Supabase connection pooling issues |
| wordpress-style-theme-components | WordPress-inspired theme component patterns |

---

## advanced-features

Admin tools, gamification, newsletters, and advanced platform capabilities.

| Skill | Description |
|-------|-------------|
| ADMIN_PASSWORD_MANAGEMENT_WORDPRESS_STYLE | Admin password reset and management (WordPress-style flows) |
| bookmark-chapters-system | Visual bookmarks/chapters system for video players |
| COMMUNITY_SYSTEM_GUIDE | Full-featured social learning platform for LMS |
| EMAIL_CAMPAIGN_LIMITS | Email campaign rate limits and best practices |
| GAMIFICATION_SYSTEM | Points, badges, achievements, and leaderboards |
| HOME_PAGE_BUILDER_GUIDE | Visual page builder for home page customization |
| PLUGIN_SYSTEM_ARCHITECTURE | WordPress-style plugin/hook system for MERN |
| PRD_NEWSLETTER_SYSTEM | Newsletter management with Puck visual editor |
| PRD_NEWSLETTER_TEMPLATE_SYSTEM | Visual newsletter template creation system |
| PUCK_PAGE_TEMPLATES_SYSTEM | Page template management with Puck editor |
| SEO_SETTINGS_MANAGEMENT | SEO configuration and meta tag management |

---

## automation

Form automation and data population systems.

| Skill | Description |
|-------|-------------|
| AUTO_POPULATE_COMPLETE_GUIDE | Auto-populate GTA tax forms with intelligent financial data (80% time savings) |

---

## complexity-metrics

Code complexity analysis and development velocity optimization.

| Skill | Description |
|-------|-------------|
| complexity-divider | Complexity metrics as feedback loop for 300-700% velocity gains |
| work-with-complexity | Complexity-aware guardrails for implementation work |

---

## database-solutions

Database schema design, migrations, and PostgreSQL patterns.

| Skill | Description |
|-------|-------------|
| CONDITIONAL_SQL_MIGRATION_PATTERN | Safe conditional SQL migrations pattern |
| DATABASE_SCHEMA | MongoDB/Mongoose schema definitions for LMS |
| DATABASE_SCHEMA_VERIFICATION_GUIDE | Guide for verifying database schema integrity |
| DATABASE_STRATEGY | Database architecture and strategy decisions |
| ES_MODULE_SEED_SCRIPT_PATTERN | ES module pattern for database seed scripts |
| MIGRATION_GUIDE | Database migration procedures and rollback |
| POSTGRES_SQL_TEMPLATE_BINDING_ERROR | Fix for PostgreSQL template binding errors |
| POSTGRESQL_LICENSE_TABLE_DESIGN | License table design for PostgreSQL |
| RLS_SECURITY_GUIDE | Row Level Security implementation guide |
| SCHEMA_ENHANCEMENTS_GUIDE | Schema enhancement patterns and procedures |
| SCHEMA_MIGRATION_GUIDE | Comprehensive schema migration guide |
| SCHEMA_VERIFICATION_QUICK_REFERENCE | Quick reference for schema verification |
| mariadb-aggregate-function-replacement | MariaDB 10.4 aggregate function replacement with depth-tracking parens |
| postgresql-to-mysql-runtime-translation | Runtime SQL translation layer for PG-to-MySQL migration (20+ rules) |
| regex-alternation-ordering-sql-types | Regex alternation ordering to prevent partial matches in SQL type casts |
| reserved-word-context-aware-quoting | Context-aware reserved word quoting with SAFE_BEFORE set |
| PLPGSQL_VARIABLE_CONFLICT_FIX | Fix PL/pgSQL RETURNS TABLE column name clashes with #variable_conflict use_column |

---

## deployment-security

Production deployment, VPS setup, and security hardening.

| Skill | Description |
|-------|-------------|
| CPANEL_NODE_DEPLOYMENT | Node.js deployment on cPanel hosting |
| DEPLOYMENT | General deployment procedures |
| DEPLOYMENT_CHECKLIST | Pre-deployment verification checklist |
| DEPLOYMENT_PLAN | Deployment planning and staging |
| express-secure-file-downloads | Secure file download implementation for Express |
| KNEX_DATABASE_ABSTRACTION | Database abstraction layer with Knex.js |
| LICENSE_KEY_SYSTEM | Software licensing and key validation |
| PHP_INSTALLER_WIZARD_GUIDE | PHP-based installer wizard implementation |
| PRODUCTION_DEPLOYMENT_GUIDE | Production deployment best practices |
| PRODUCTION_HARDENING_DOCUMENTATION | Security hardening for production systems |
| react-production-deployment-desktop-guide | React production deployment for desktop apps |
| SECURITY | Security implementation and best practices |
| self-hosted-supabase-coolify-guide | Self-hosted Supabase with Coolify |
| SUPABASE_EDGE_FUNCTIONS | Supabase Edge Functions development |
| unique-features-ai-strategy-plaid-security | AI strategy and Plaid security integration |
| VERCEL_GITHUB_DEPLOYMENT_GUIDE | Vercel deployment with GitHub integration |
| VPS_DEPLOYMENT_READINESS | VPS deployment preparation checklist |
| vps-deployment | VPS deployment procedures and configuration |

---

## document-processing

PDF forms, file downloads, and document AI integration.

| Skill | Description |
|-------|-------------|
| document-ai-landingai-integration | Document AI with LandingAI integration |
| express-secure-file-downloads | Secure file downloads in Express.js |
| express-secure-file-downloads-mern | MERN stack secure file downloads |
| pdf-forms-integration/README | PDF forms integration overview |
| pdf-forms-integration/SKILL | PDF forms integration implementation |

---

## ecommerce

E-commerce, Stripe payments, donations, and GTA compliance.

| Skill | Description |
|-------|-------------|
| ADMIN_PRODUCTS_GUIDE | Admin product management interface |
| cart-item-count-indicator | Shopping cart item count badge |
| DONATION_RECEIPT_IMPLEMENTATION_GUIDE | Donation receipt generation guide |
| ECOMMERCE_API_REFERENCE | E-commerce API endpoints reference |
| ECOMMERCE_COMPLETION_SUMMARY | E-commerce implementation completion report |
| ECOMMERCE_IMPLEMENTATION_GUIDE | Complete e-commerce implementation guide |
| ECOMMERCE_QUICK_REFERENCE | Quick reference for e-commerce features |
| ECOMMERCE_TESTING_CHECKLIST | E-commerce testing procedures |
| ECOMMERCE_WORKFLOW_GUIDE | E-commerce workflow documentation |
| GTA_501C3_DONATION_RECEIPT_REQUIREMENTS | GTA 501(c)(3) donation receipt requirements |
| GTA_COMPLIANCE_INDEX | Index of GTA compliance documents |
| GTA_COMPLIANCE_SUMMARY | Summary of GTA compliance requirements |
| GTA_REQUIRED_RECEIPT_LANGUAGE | Required language for GTA-compliant receipts |
| PRODUCT_CREATION_EXPANDED | Expanded product creation workflow |
| stripe-payment-integration-complete | Complete Stripe payment integration solution |

---

## form-solutions

Form builders, surveys, and fillable document systems.

| Skill | Description |
|-------|-------------|
| FILLABLE_PDF_IMPLEMENTATION | Fillable PDF form implementation guide |
| SURVEYJS_QUESTIONNAIRE_SYSTEM | SurveyJS-based questionnaire system |

---

## integrations

Third-party API integrations: payments, meetings, video, security, voice/STT.

| Skill | Description |
|-------|-------------|
| realtimestt-openwakeword-cuda-windows | 7 gotchas integrating RealtimeSTT + OpenWakeWord + CUDA on Windows (wake word, MKL, float16, PyQt6 import order, debounce) |
| cloudflare-turnstile-debugging | Debugging Cloudflare Turnstile CAPTCHA |
| cloudflare-turnstile-implementation | Cloudflare Turnstile implementation guide |
| PAYPAL_DIAGNOSTIC_REPORT | PayPal integration diagnostic report |
| PAYPAL_FIX_DEBUG_REPORT | PayPal debugging and fix report |
| PAYPAL_FIX_QUICK_REFERENCE | Quick fixes for PayPal issues |
| PAYPAL_SDK_IMPLEMENTATION_REPORT | PayPal SDK implementation guide |
| PAYPAL_TESTING_GUIDE | PayPal integration testing procedures |
| rss-podcast-integration | RSS feed and podcast integration |
| STRIPE_CHANGES_QUICK_REFERENCE | Stripe API changes quick reference |
| STRIPE_DEBUG_COMPLETE | Complete Stripe debugging guide |
| STRIPE_DONATIONS_COMPLETE_IMPLEMENTATION | Stripe donations full implementation |
| STRIPE_DONATIONS_IMPLEMENTATION_PLAN | Stripe donations implementation plan |
| STRIPE_ELEMENTS_FIX | Stripe Elements component fixes |
| STRIPE_FIX_SESSION_SUMMARY | Stripe session fix summary |
| STRIPE_PAYMENT_FIX_COMPLETE | Complete Stripe payment fix guide |
| STRIPE_PAYMENT_FIXES | Collection of Stripe payment fixes |
| STRIPE_SESSION_PACKAGE_CHECKOUT | Stripe session-based package checkout |
| STRIPE_TEST_CARDS | Stripe test card numbers reference |
| stripe-payment-integration-complete | Complete Stripe integration solution |
| VIRTUAL_MEETINGS_IMPLEMENTATION | Virtual meetings system implementation |
| WORDPRESS_LMS_DATA_RECOVERY | WordPress LMS data recovery |
| YOUTUBE_API_SETUP | YouTube API configuration guide |
| YOUTUBE_BOOKMARKING_EXPLANATION | YouTube bookmarking system explained |
| YOUTUBE_BOOKMARKING_SOLUTION | YouTube bookmarking implementation |
| YOUTUBE_OAUTH_SETUP_GUIDE | YouTube OAuth setup guide |
| YOUTUBE_VIDEO_FIX_COMPLETE | YouTube video playback fixes |
| ZOOM_API_INTEGRATION_GUIDE | Complete Zoom API integration guide |
| ZOOM_API_TESTING_GUIDE | Zoom API testing procedures |
| ZOOM_CREDENTIAL_FIX | Zoom credential configuration fix |
| ZOOM_CREDENTIALS_VERIFICATION | Zoom credentials verification guide |
| ZOOM_INTEGRATION_SUMMARY | Zoom integration summary |
| ZOOM_MEETING_LIFECYCLE | Zoom meeting lifecycle management |
| ZOOM_NEXT_STEPS | Zoom integration next steps |
| ZOOM_OAUTH2_SETUP | Zoom OAuth2 setup guide |
| ZOOM_RECORDINGS_IMPLEMENTATION | Zoom recordings integration |
| ZOOM_REQUIRED_SCOPES | Required Zoom API scopes |
| ZOOM_SCOPES_CLEANUP | Zoom scopes cleanup guide |
| ZOOM_TESTING_CHECKLIST | Zoom integration testing checklist |
| ZOOM_WEBHOOK_INTEGRATION_AUTO_PUBLISH | Zoom webhook auto-publish integration |
| zoom-meetings-crud-imported | Zoom meetings CRUD operations |
| zoom-meetings-import | Zoom meetings import functionality |
| CLAUDE_CODE_TOKEN_ANALYTICS | Parse Claude Code stats-cache.json for token usage dashboards with cost/cache savings |

---

## infrastructure

Desktop app bundling, sidecar management, port configuration.

| Skill | Description |
|-------|-------------|
| TAURI_NCC_SIDECAR_BUNDLING | Bundle Node.js Express backend as Tauri sidecar using @vercel/ncc with native addon support |
| TAURI_DYNAMIC_PORT_IPC | Dynamic port discovery in Rust with frontend IPC for Tauri sidecar processes |

---

## lms-patterns

Learning Management System patterns, themes, quizzes, and community.

| Skill | Description |
|-------|-------------|
| APPOINTMENT_SCHEDULER_RESEARCH | Appointment scheduler research |
| COMMUNITY_API_QUICK_REFERENCE | Community API quick reference |
| COMMUNITY_IMPLEMENTATION_QUICK_GUIDE | Community implementation quick guide |
| COMMUNITY_SYSTEM_GUIDE | Full community system guide |
| COMPLETION_MODE_MIGRATION_GUIDE | Course completion mode migration |
| installer/CPANEL_INSTALLATION_GUIDE | cPanel installation guide |
| installer/DATABASE_ABSTRACTION | Database abstraction layer |
| installer/IMPLEMENTATION_ROADMAP | Installer implementation roadmap |
| installer/INSTALLER_ARCHITECTURE | Installer architecture design |
| installer/LICENSING_SYSTEM | Software licensing system |
| installer/research/LMS_INSTALLER_ANALYSIS | LMS installer analysis |
| installer/research/WORDPRESS_INSTALLER_ANALYSIS | WordPress installer analysis |
| installer/STARTER_CONTENT_PACK | Starter content pack system |
| installer/THEME_INSTALLER_INTEGRATION | Theme installer integration |
| installer/themes/CLASSIC_THEME | Classic theme specification |
| installer/themes/COLORFUL_MODERN_THEME | Colorful modern theme |
| LMS_IMPLEMENTATION_ROADMAP | LMS implementation roadmap |
| LMS_INDEX | LMS documentation index |
| LMS_QUICK_REFERENCE | LMS quick reference |
| LMS_RESEARCH_SUMMARY | LMS research summary |
| LMS_SETUP_SUMMARY | LMS setup summary |
| LMS_STANDARDS_RESEARCH | LMS standards research |
| LMS_START_HERE_CHECKLIST | LMS getting started checklist |
| MEMBERSHIP_IMPLEMENTATION_GUIDE | Membership system implementation |
| MEMBERSHIP_QUICK_REFERENCE | Membership quick reference |
| MEMBERSHIP_SYSTEMS_RESEARCH | Membership systems research |
| OPENSOURCE_THEME_SYSTEMS | Open source theme systems research |
| PRD_ADMIN_REPORTING_SYSTEM | Admin reporting system PRD |
| QUIZ_DEPLOYMENT_GUIDE | Quiz system deployment guide |
| QUIZ_INTEGRATION_GUIDE | Quiz integration guide |
| QUIZ_SESSION_COMPLETE_OCT19 | Quiz session completion report |
| QUIZ_SYSTEM_SUMMARY | Quiz system summary |
| THEME_COMPLETE_DEVELOPER_GUIDE | Complete theme developer guide |
| THEME_DEVELOPER_HANDBOOK | Theme developer handbook |
| THEME_SYSTEM_DEVELOPER_GUIDE | Theme system developer guide |
| THEME_VITE_REQUIREMENTS | Theme Vite build requirements |
| theme-system/API_REFERENCE | Theme system API reference |
| theme-system/QUICK_START_GUIDE | Theme system quick start |
| theme-system/README | Theme system overview |
| theme-system/THEME_EXAMPLE_PRD | Theme example PRD |
| theme-system/THEME_PRD_TEMPLATE | Theme PRD template |
| theme-system/THEME_SYSTEM_ARCHITECTURE | Theme system architecture |
| UI_DESIGN_REPORTING_SYSTEM | UI design for reporting system |
| VIDEO_PROGRESS_DRIP_FEED_IMPLEMENTATION | Video progress drip feed |
| image-overflow-fix | Fix broken image alt text causing layout overflow in admin pages |

---

## methodology

Development methodology, WARRIOR workflow, and session patterns.

| Skill | Description |
|-------|-------------|
| ADVANCED_ORCHESTRATION_PATTERNS | Advanced AI orchestration patterns |
| CRITICAL_PATTERNS_DOCUMENTATION_COMPLETE | Critical patterns documentation |
| DELIVERABLES_SUMMARY | Project deliverables summary |
| MASTER_COMPLETION_SUMMARY | Master completion summary |
| MASTER_SESSION_COMPLETION | Session completion checklist |
| MERN_QUICK_REFERENCE | MERN stack quick reference |
| QUICK_REFERENCE | General quick reference |
| SESSION_COMPLETION_SUMMARY | Session completion summary |
| SESSION_SUMMARY | Session summary template |
| WARRIOR_WORKFLOW_DEBUGGING_PROTOCOL | WARRIOR debugging protocol - verify schema first |
| PATH_VERIFICATION_GATE | **[NEW v5.0]** Mandatory wrong-repo circuit breaker for subagent spawns |
| SDFT_ONPOLICY_SELF_DISTILLATION | **[NEW v5.0]** Predict-then-read protocol for agent handoff learning (MIT SDFT) |
| INSTRUMENTATION_OVER_RESTRICTION | **[NEW v8.0]** Boris Cherny principle: give tools + context, verify output — don't gate every action (2-3x quality) |

---

## patterns-standards

Coding patterns, error handling, and development standards.

| Skill | Description |
|-------|-------------|
| API_PATTERN_FIX_SUMMARY | API pattern fixes summary |
| claude-code-plugin-structure | **[NEW]** Claude Code local plugin structure, frontmatter, debugging |
| CRITICAL_CODING_PATTERNS | 5 critical patterns that prevent 80% of bugs |
| ERROR_RESILIENCE_IMPLEMENTATION | Error resilience implementation patterns |
| irs-tax-calculations-official-language | GTA tax calculation official language |
| react-i18next-setup | React internationalization with i18next |
| thesys-c1-generative-ui-integration | Thesys C1 generative UI integration |

---

## theology

Biblical analysis and theological computing patterns.

| Skill | Description |
|-------|-------------|
| BIBLICAL_PATTERN_ANALYSIS_LLM | Biblical pattern analysis for LLM systems - ELS, acrostics, typology |

---

## security

SQL injection prevention, path traversal, input validation, and security hardening.

| Skill | Description |
|-------|-------------|
| sql-injection-prevention-postgresjs | **[NEW]** Column whitelists + sanitizeSort() for postgres.js dynamic queries |

---

## testing

E2E testing, security regression, and test automation patterns.

| Skill | Description |
|-------|-------------|
| playwright-api-security-tests | **[NEW]** 26-test Playwright API security regression suite template |

---

## video-media

Video players, streaming, progress tracking, and media integration.

| Skill | Description |
|-------|-------------|
| bookmark-chapters-system | Visual bookmarks/chapters for video players |
| **crash-resilient-recording** | **v2.0 — 6-layer crash resilience: IndexedDB audio buffer, 10s chunks, ondataavailable upload, offline queue + reconnect flush, sendBeacon, heartbeat sweep** |
| COMPLETE_VIDEO_IMPLEMENTATION | Complete video implementation guide |
| fix-reactplayer-youtube-playback | ReactPlayer YouTube playback fixes |
| fix-youtube-bookmark-timestamps | YouTube bookmark timestamp fixes |
| importing-youtube-videos | YouTube video import guide |
| importing-youtube-videos-mern | MERN YouTube video import |
| VIDEO_COMPLETION_MODE_FEATURE | Video completion mode feature |
| VIDEO_PLAYER_ENHANCEMENTS | Video player enhancement features |
| VIDEO_PROGRESS_TRACKING | Video progress tracking system |
| VIDEO_SETUP_COMPLETE | Video setup completion guide |
| VIDEO_SETUP_COMPLETE_GUIDE | Complete video setup guide |
| VIDEO_UPLOAD_ARCHITECTURE_RESEARCH | Video upload architecture research |
| video-player-integration-guide | Video player integration guide |
| VIMEO_API_SETUP | Vimeo API setup guide |
| WARRIOR_VIDEO_STATUS | WARRIOR video implementation status |
| **remotion-best-practices** (external) | Programmatic video creation with React/Remotion — 37 rules covering animations, audio, 3D, captions, charts, transitions, text animations, Tailwind, voiceover. Location: `~/.claude/skills/remotion-best-practices/` (symlink to `~/.agents/skills/`) |

---

## _general/database-solutions {#general-database-solutions}

General-scope database persistence patterns applicable to any project.

| Skill | Description |
|-------|-------------|
| persistent-analysis-storage | Dual-storage (localStorage + PostgreSQL) with favorites, public sharing (nanoid slugs), cursor pagination, tabbed sidebar UI |
| qdrant-blue-green-aliases | **[NEW]** Atomic collection alias swaps for zero-downtime Qdrant reindexing — blue-green deployment pattern with rollback |

---

## _general/performance {#general-performance}

General-scope performance and caching patterns applicable to any project.

| Skill | Description |
|-------|-------------|
| cache-augmented-generation | **[NEW]** Pre-load stable document corpus into cached prompt prefix (Anthropic prompt caching) as alternative to RAG for small, stable corpora |

---

## _general/methodology {#general-methodology}

General-scope methodology skills applicable to any project.

| Skill | Description |
|-------|-------------|
| multi-project-autonomous-build | 3+ project parallel autonomous build workflow |
| autonomous-multi-phase-build **v2.0** | **[NEW]** Atomic phase contract with per-phase tsc+build verification, status tracking, auto-fix loop |
| llm-judge-memory-crud | **[NEW v12.0]** Mem0-style ADD/UPDATE/DELETE/NOOP pipeline for vector memory CRUD — transforms append-only vector DBs into self-maintaining systems |
| claude-md-archival | **[NEW]** Archive oversized CLAUDE.md to `history/claudemdbackup.md` — keeps working context lean while preserving full project history |
| git-worktrees-parallel | **[NEW]** Boris Cherny's #1 tip: 3-5 parallel worktrees each with own Claude session — `claude --worktree <name>`, subagent `isolation: worktree`, full workflow |
| shell-autonomous-loop-fixplan | **[NEW v1.0]** Shell-level autonomous loop (bash spawns fresh `claude --resume` per iteration) + `@fix_plan.md` persistent task tracking — context-limit-immune autonomy with circuit breaker, rate limiting, BLOCKED signal, session management. Inspired by bmalph/Ralph. |
| learncoding-agentic-pattern | **[NEW v1.0]** Simon Willison's Linear Walkthrough pattern — WHAT/WHY/PATTERN per file, Showboat snippet extraction (no hallucination), cognitive debt prevention. Anti-vibe-coding. BFS dependency graph traversal from entry point outward. |
| debug-swarm-researcher-escape-hatch | **[NEW v1.0]** When ALL debug swarm agents return BLOCKED — escape the loop, spawn a researcher (skills lib + MCP + WebSearch + GitHub), write findings to `.planning/research/`, re-inject into fresh swarm iteration. Doesn't count as an iteration. BLOCKED response contract + orchestrator escape logic included. |

---

## _general/patterns-standards {#general-patterns-standards}

General-scope design patterns applicable to any project.

| Skill | Description |
|-------|-------------|
| domain-specific-layout-algorithms | **[NEW]** Pure-function layout registry encoding domain spatial metaphors — mirror arcs, parallel lanes, narrative parabolas, concentric rings |
| fullstack-bible-study-platform | React + xyflow + Prisma + Qdrant Bible study platform blueprint |
| python-desktop-app-architecture | Full PyQt6 + pystray + STT/TTS desktop app blueprint |
| realtime-monitoring-dashboard | Vite + React + Express + SSE real-time dashboard blueprint |
| togglable-processing-pipeline | Config-driven feature pipeline with fail-fast ordering |

---

## _general/frontend {#general-frontend}

General-scope frontend skills applicable to any web project.

| Skill | Description |
|-------|-------------|
| canvas-bubble-animation-grouping | **[NEW]** Absolute-positioned canvas with 3 layout algorithms (golden spiral, rect grid, binary filter) + spring animations for 150+ items |
| react-flow-animated-layout-switching | **[NEW]** CSS transitions on `.react-flow__node` transform for smooth layout algorithm switching — scoped, 600ms, no Framer Motion needed |
| svg-sparkline-no-charting-library | **[NEW]** Pure SVG sparkline chart with viewBox percentage coordinates — 0KB dependency, hover tooltips, click handlers |
| framer-motion-layoutid-grouping | **[NEW]** FLIP animations for data re-sorting/re-grouping — stable layoutId, spring physics (stiffness 400, damping 30), whileHover/whileTap |
| pyqt6-settings-dialog | Dark-themed PyQt6 settings GUI replacing raw YAML editing |
| safari-sw-cache-poisoning | Nuclear SW purge pattern for Safari caching stale service workers for months/years, breaking all API calls |
| safari-csp-theme-color-debugging | Debugging Safari-specific CSP mismatches, theme-color bars, and animation failures on iOS |

---

## _general/integrations {#general-integrations}

General-scope MCP and tool integration patterns applicable to any project.

| Skill | Description |
|-------|-------------|
| mcp-composite-tool-orchestration | **[NEW]** Consolidate 3-5 sequential MCP tool calls into single composite operations — batch_read, multi_search, project_overview, trace_references, search_and_read. 58-72% token savings. |
| claude-code-local-mcp-integration | **[NEW]** Register, configure, debug, and test local stdio MCP servers with Claude Code — mcp.json setup, env vars, startup failure debugging, common failure modes |

---

## Usage Examples

### Find a skill by topic
```bash
# Search for Stripe-related skills
grep -r "Stripe" SKILLS-INDEX.md

# Search for deployment skills
grep -i "deploy" SKILLS-INDEX.md
```

### Read a specific skill
```bash
# Using Claude Code's Read tool
Read: C:/Users/FirstName/.claude/plugins/dominion-flow/skills-library/integrations/STRIPE_TEST_CARDS.md
```

### List all skills in a category
```bash
ls -la C:/Users/FirstName/.claude/plugins/dominion-flow/skills-library/integrations/
```

---

## Contributing

To add new skills:
1. Create a markdown file in the appropriate category folder
2. Include a clear title and description in the first section
3. Update this index with the new skill
4. Commit changes to git

---

*Generated from WARRIOR workflow skills library import*
