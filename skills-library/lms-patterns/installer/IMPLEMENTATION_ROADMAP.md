# Church LMS Installer - Implementation Roadmap

**Version:** 1.0
**Last Updated:** January 11, 2026
**Status:** PLANNING PHASE
**Priority:** HIGH - Next major feature after current branch

---

## Executive Summary

### Project Overview

The Church LMS Installer is a web-based installation wizard designed to make deploying the Melchizedek Priests Ministry LMS accessible to non-technical users, specifically targeting pastors and church administrators. The system will transform the current MongoDB-only MERN stack into a portable, self-installable application supporting both PostgreSQL and MySQL databases commonly available on budget hosting providers.

### Vision Statement

> Enable any church administrator to deploy a fully-functional LMS on their existing cPanel hosting account in under 15 minutes, without requiring technical expertise or expensive infrastructure.

### Goals

1. **Accessibility**: Non-technical users can complete installation without developer assistance
2. **Affordability**: Works on shared hosting ($5-15/month) commonly used by churches
3. **Reliability**: 95%+ installation success rate across major hosting providers
4. **Flexibility**: Support both PostgreSQL and MySQL to maximize hosting compatibility
5. **Sustainability**: License-based model to fund ongoing development and support

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Installation Success Rate | > 95% | Analytics tracking on installer completion |
| Average Install Time | < 15 minutes | Timer from start to first login |
| Support Tickets per Install | < 0.5 | Support system tracking |
| Time to First Course Created | < 30 minutes | User activity tracking |
| cPanel Host Compatibility | Top 10 hosts | Manual testing certification |
| User Satisfaction (NPS) | > 40 | Post-install survey |
| License Activation Rate | > 80% | License server analytics |

### Target Launch Timeline

```
+------------------+------------------+------------------+------------------+
|    Q1 2026       |    Q2 2026       |    Q2 2026       |    Q3 2026       |
|    Jan-Mar       |    Apr-May       |    May-Jun       |    Jul-Aug       |
+------------------+------------------+------------------+------------------+
| Phase 0-1        | Phase 2-3        | Phase 4-5        | Post-Launch      |
| Foundation &     | Wizard &         | Polish &         | Docker &         |
| Core Installer   | Licensing        | Beta Launch      | One-Click        |
+------------------+------------------+------------------+------------------+
```

---

## Timeline Overview (Gantt Chart)

```
2026
Jan         Feb         Mar         Apr         May         Jun         Jul
|-----------|-----------|-----------|-----------|-----------|-----------|
Phase 0: Foundation (2-3 weeks)
[████████████]
            Phase 1: Core Installer (3-4 weeks)
            [████████████████]
                        Phase 2: Complete Wizard (2-3 weeks)
                        [██████████]
                                   Phase 3: Licensing System (2-3 weeks)
                                   [██████████]
                                              Phase 4: Content & Polish (2 weeks)
                                              [███████]
                                                     Phase 5: Testing & Launch (2 weeks)
                                                     [███████]
                                                             Post-Launch
                                                             [████████████...

Legend:
████ = Active Development
---- = Parallel/Support Work
```

---

## Phase Dependencies

```
                    +-------------------+
                    |  Phase 0          |
                    |  Foundation       |
                    |  (DB Abstraction) |
                    +--------+----------+
                             |
                             v
                    +-------------------+
                    |  Phase 1          |
                    |  Core Installer   |
                    |  (PHP Bootstrap)  |
                    +--------+----------+
                             |
              +--------------+--------------+
              |                             |
              v                             v
    +-------------------+         +-------------------+
    |  Phase 2          |         |  Phase 3          |
    |  Complete Wizard  |         |  Licensing System |
    |  (UI/UX)          |         |  (Server-side)    |
    +--------+----------+         +--------+----------+
              |                             |
              +--------------+--------------+
                             |
                             v
                    +-------------------+
                    |  Phase 4          |
                    |  Content & Polish |
                    +--------+----------+
                             |
                             v
                    +-------------------+
                    |  Phase 5          |
                    |  Testing & Launch |
                    +-------------------+
```

**Critical Path:** Phase 0 -> Phase 1 -> Phase 2 -> Phase 4 -> Phase 5

**Parallel Track:** Phase 3 (Licensing) can proceed independently after Phase 1

---

## Phase 0: Foundation (2-3 weeks)

### Objective
Create the database abstraction layer that allows the application to work with both PostgreSQL and MySQL, establishing the foundation for a portable installer.

### Tasks

#### Week 1: Database Abstraction Layer

1. **Research & Design (2 days)**
   - [ ] Evaluate Knex.js vs Sequelize vs TypeORM for multi-database support
   - [ ] Document current Mongoose/postgres.js query patterns in use
   - [ ] Design unified query interface specification
   - [ ] Decision document: Selected ORM/query builder with rationale

2. **Core Abstraction Implementation (3 days)**
   - [ ] Create `server/database/` directory structure
   - [ ] Implement database adapter interface
   - [ ] Create PostgreSQL adapter (wrap existing postgres.js)
   - [ ] Create MySQL adapter skeleton
   - [ ] Implement connection factory pattern

#### Week 2: Migration System

3. **Migration Framework (3 days)**
   - [ ] Design migration file format (timestamp-based)
   - [ ] Create migration runner that detects database type
   - [ ] Implement up/down migration support
   - [ ] Create CLI tool: `npm run migrate`
   - [ ] Document migration writing guidelines

4. **Schema Conversion (2 days)**
   - [ ] Convert existing PostgreSQL schema to migration files
   - [ ] Create MySQL-equivalent migrations
   - [ ] Handle database-specific features (JSONB -> JSON, etc.)
   - [ ] Test both migration paths

#### Week 3: Testing Infrastructure

5. **Dual-Database Testing (3 days)**
   - [ ] Set up MySQL Docker container for local testing
   - [ ] Create test database configuration system
   - [ ] Write integration tests that run against both databases
   - [ ] Set up CI pipeline for dual-database testing

6. **Documentation & Validation (2 days)**
   - [ ] Create DATABASE_ABSTRACTION.md documentation
   - [ ] Write migration writing guide
   - [ ] Validate all existing features work on both databases
   - [ ] Performance comparison baseline testing

### Deliverables

| Deliverable | Description | Acceptance Criteria |
|-------------|-------------|---------------------|
| Database Adapter Interface | Unified API for database operations | Can switch databases with config change |
| PostgreSQL Adapter | Wraps existing postgres.js | All existing tests pass |
| MySQL Adapter | New MySQL implementation | All existing tests pass |
| Migration System | Up/down migrations for both DBs | Can create fresh DB from migrations |
| Migration Files | Schema as code | 43 tables created identically |
| Test Suite | Dual-database tests | 100% pass on both PostgreSQL & MySQL |
| Documentation | Complete technical docs | New developer can understand system |

### Go/No-Go Criteria

- [ ] All 43 tables create successfully on both PostgreSQL and MySQL
- [ ] All existing API tests pass on both databases
- [ ] Migration system can roll back cleanly
- [ ] Performance within 10% of current PostgreSQL-only system
- [ ] Documentation reviewed and approved

### Quick Wins (Can Ship Incrementally)

- Database adapter interface (useful for testing)
- Migration CLI tool (helps development workflow)
- Dual-database Docker setup (aids contributor onboarding)

---

## Phase 1: Core Installer (3-4 weeks)

### Objective
Build the PHP bootstrap installer that runs initial setup on standard cPanel hosting environments.

### Tasks

#### Week 1: PHP Bootstrap

1. **Installer Framework (3 days)**
   - [ ] Create `install/` directory in project root
   - [ ] Build PHP installer entry point (`index.php`)
   - [ ] Create step-based navigation system
   - [ ] Implement session management for multi-step wizard
   - [ ] Design responsive installer UI (mobile-friendly)

2. **Requirements Checker (2 days)**
   - [ ] PHP version detection (require 7.4+)
   - [ ] Node.js version detection (require 18+)
   - [ ] npm availability check
   - [ ] Required PHP extensions check (mysqli, pdo, json, curl)
   - [ ] File permission verification (write to config directories)
   - [ ] Available disk space check

#### Week 2: Database Configuration

3. **Database Selection UI (2 days)**
   - [ ] Database type selector (PostgreSQL vs MySQL)
   - [ ] Visual guide for finding cPanel database credentials
   - [ ] Tooltip help text for each field
   - [ ] Real-time connection testing

4. **Database Connection Wizard (3 days)**
   - [ ] Host/port/username/password form
   - [ ] Connection test functionality
   - [ ] Database creation option (if user has permissions)
   - [ ] Display helpful error messages for common issues
   - [ ] Support for both local and remote databases

#### Week 3: Environment Configuration

5. **.env File Generation (2 days)**
   - [ ] Template-based .env generation
   - [ ] Secure secret key generation
   - [ ] URL detection (auto-detect installation URL)
   - [ ] Environment variable validation
   - [ ] Backup existing .env if present

6. **Admin Account Creation (3 days)**
   - [ ] Admin registration form
   - [ ] Password strength validation
   - [ ] Email validation
   - [ ] Create admin user in database
   - [ ] Generate first admin JWT token
   - [ ] Auto-login after setup

#### Week 4: Integration & Testing

7. **Node.js Integration (3 days)**
   - [ ] Trigger `npm install` from PHP
   - [ ] Run database migrations
   - [ ] Build frontend assets
   - [ ] Progress feedback during long operations
   - [ ] Error handling and recovery

8. **Finalization (2 days)**
   - [ ] Installation completion page
   - [ ] Security cleanup (remove install directory prompt)
   - [ ] Generate installation report
   - [ ] Quick start guide display
   - [ ] First login redirect

### Deliverables

| Deliverable | Description | Acceptance Criteria |
|-------------|-------------|---------------------|
| PHP Installer Framework | Step-based wizard UI | Works in all modern browsers |
| Requirements Checker | Pre-flight validation | Detects all critical requirements |
| Database Wizard | DB setup UI | Connects to PostgreSQL & MySQL |
| .env Generator | Config file creation | All required vars populated |
| Admin Setup | First user creation | Can login after setup |
| npm Integration | Build automation | Installs deps and builds frontend |
| Security Cleanup | Post-install hardening | Install directory removal prompted |

### Go/No-Go Criteria

- [ ] Complete installation succeeds on clean cPanel environment
- [ ] Requirements checker catches all blocking issues before proceeding
- [ ] Database connection works with both PostgreSQL and MySQL
- [ ] Admin can login after installation completes
- [ ] Installation takes less than 10 minutes on typical hosting

### Quick Wins

- Requirements checker (can be released standalone)
- .env file generator template
- Admin creation API endpoint (useful for dev)

---

## Phase 2: Complete Wizard (2-3 weeks)

### Objective
Enhance the installer with complete site configuration, email setup, and professional user experience.

### Tasks

#### Week 1: Site Configuration

1. **Organization Setup (2 days)**
   - [ ] Church/Organization name input
   - [ ] Logo upload with preview
   - [ ] Color theme selection (predefined themes)
   - [ ] Custom primary/secondary color pickers
   - [ ] Timezone selection
   - [ ] Default language setting

2. **Basic Branding (3 days)**
   - [ ] Favicon upload/generation
   - [ ] Email header logo configuration
   - [ ] Footer text customization
   - [ ] Social media links input
   - [ ] Contact information form

#### Week 2: Email Configuration

3. **Email Setup Wizard (3 days)**
   - [ ] SMTP configuration form
   - [ ] Common provider presets (Gmail, Outlook, SendGrid)
   - [ ] Connection test with sample email
   - [ ] Email from name/address configuration
   - [ ] Email template selection (3-4 base templates)

4. **Email Testing (2 days)**
   - [ ] Send test email functionality
   - [ ] Troubleshooting guide for common issues
   - [ ] SPF/DKIM/DMARC guidance
   - [ ] Alternative: built-in email via hosting

#### Week 3: Polish & Error Handling

5. **Progress & Navigation (2 days)**
   - [ ] Visual step progress indicator
   - [ ] Step completion checkmarks
   - [ ] Back/forward navigation with state preservation
   - [ ] Skip optional steps functionality
   - [ ] Summary page before final install

6. **Error Handling & Recovery (3 days)**
   - [ ] Graceful error messages (no technical jargon)
   - [ ] Retry mechanisms for failed steps
   - [ ] Rollback capability for partial installs
   - [ ] Log file generation for support
   - [ ] "Contact Support" integration

### Deliverables

| Deliverable | Description | Acceptance Criteria |
|-------------|-------------|---------------------|
| Site Config UI | Organization branding setup | Logo/colors applied to site |
| Email Wizard | SMTP configuration | Test email sends successfully |
| Progress Indicator | Visual step tracker | Shows current/completed steps |
| Error Recovery | Graceful failure handling | Can resume from failures |
| Skip Functionality | Optional step bypass | Core install completes without optional steps |
| Summary Page | Pre-install review | User confirms all settings before install |

### Go/No-Go Criteria

- [ ] All configuration options save correctly to database/env
- [ ] Email setup works with Gmail, Outlook, and generic SMTP
- [ ] Progress indicator accurately reflects installation state
- [ ] Errors are recoverable without starting over
- [ ] Non-technical users can complete setup (usability testing)

### Quick Wins

- Email provider presets (helps non-technical users)
- Progress indicator component (reusable elsewhere)
- Logo upload functionality (improves current admin)

---

## Phase 3: Licensing System (2-3 weeks)

### Objective
Build a license management system to protect the software while providing a sustainable business model.

### Tasks

#### Week 1: License Server Development

1. **License Server Infrastructure (3 days)**
   - [ ] Deploy license server (separate from main app)
   - [ ] Design license key format (UUID-based or custom)
   - [ ] Create license generation API
   - [ ] Implement cryptographic key signing
   - [ ] Set up secure database for license storage

2. **License Validation API (2 days)**
   - [ ] Activation endpoint (domain + key -> activation)
   - [ ] Validation endpoint (check if license valid)
   - [ ] Deactivation endpoint (release license)
   - [ ] Rate limiting and abuse prevention
   - [ ] Offline grace period support

#### Week 2: Key Management

3. **Key Generation System (2 days)**
   - [ ] License tier definitions (Free, Pro, Enterprise)
   - [ ] Feature flag system per license tier
   - [ ] Expiration date management
   - [ ] Site limit configuration (1 site, 3 sites, unlimited)
   - [ ] Admin key generation interface

4. **License Integration in Installer (3 days)**
   - [ ] License key input step in wizard
   - [ ] Real-time license validation
   - [ ] Feature unlock based on license tier
   - [ ] Grace period for expired licenses
   - [ ] Upgrade prompts for free tier

#### Week 3: Management Portal

5. **License Management Portal (3 days)**
   - [ ] Customer dashboard (view licenses, activations)
   - [ ] Admin panel (generate keys, manage customers)
   - [ ] Activation history and audit log
   - [ ] Deactivation self-service
   - [ ] License transfer capability

6. **Integration & Security (2 days)**
   - [ ] Domain binding verification
   - [ ] Anti-tampering measures
   - [ ] License check caching (minimize server calls)
   - [ ] Graceful degradation if server unreachable
   - [ ] Documentation for customers

### Deliverables

| Deliverable | Description | Acceptance Criteria |
|-------------|-------------|---------------------|
| License Server | Dedicated validation service | 99.9% uptime target |
| Key Generation | Create license keys | Admin can generate keys |
| Activation API | Domain + key activation | Licenses bind to domains |
| Validation System | Check license status | App validates on startup |
| Customer Portal | Self-service dashboard | Users can view/manage licenses |
| Admin Panel | License administration | Full CRUD on licenses |
| Feature Flags | Tier-based features | Features enable per license |

### Go/No-Go Criteria

- [ ] License server deployed and stable (load tested)
- [ ] Key generation produces unique, valid keys
- [ ] Activation/deactivation flow works correctly
- [ ] Feature flags correctly enable/disable features
- [ ] Customer portal accessible and functional
- [ ] Security review completed (no bypass vulnerabilities)

### License Tier Structure (Proposed)

| Tier | Price | Sites | Features |
|------|-------|-------|----------|
| Free | $0 | 1 | Core LMS, 100 students max |
| Pro | $99/year | 3 | Unlimited students, Email support |
| Enterprise | $299/year | Unlimited | White-label, Priority support, Custom features |

---

## Phase 4: Content & Polish (2 weeks)

### Objective
Create starter content, refine documentation, and ensure accessibility compliance.

### Tasks

#### Week 1: Starter Content

1. **Demo Course Pack (3 days)**
   - [ ] Create "Getting Started" course template
   - [ ] Sample lessons with various content types
   - [ ] Example quiz/assessment
   - [ ] Placeholder video content (or YouTube embeds)
   - [ ] Course completion certificate template

2. **Sample Data (2 days)**
   - [ ] Demo student accounts
   - [ ] Sample community posts
   - [ ] Example categories and tags
   - [ ] Newsletter template
   - [ ] Demo product (if e-commerce used)

#### Week 2: Documentation & Accessibility

3. **User Documentation (2 days)**
   - [ ] Installation guide (step-by-step with screenshots)
   - [ ] Quick start guide for admins
   - [ ] Course creation tutorial
   - [ ] FAQ document
   - [ ] Troubleshooting guide

4. **Accessibility & Polish (3 days)**
   - [ ] WCAG 2.1 AA compliance review
   - [ ] Keyboard navigation testing
   - [ ] Screen reader compatibility
   - [ ] Color contrast verification
   - [ ] Mobile responsiveness testing
   - [ ] Loading state polish
   - [ ] Error message review

### Deliverables

| Deliverable | Description | Acceptance Criteria |
|-------------|-------------|---------------------|
| Starter Course | Demo content pack | Course with 5+ lessons importable |
| Sample Data | Pre-populated content | Site looks alive after install |
| Install Guide | User documentation | Non-technical user can follow |
| Quick Start | Admin orientation | Admin productive in 30 min |
| Accessibility | WCAG compliance | AA level compliance verified |
| Mobile Polish | Responsive installer | Works on tablet/phone |

### Go/No-Go Criteria

- [ ] Starter content imports without errors
- [ ] Documentation reviewed by non-technical user
- [ ] Accessibility audit passes AA standards
- [ ] All installer steps mobile-friendly
- [ ] Help text reviewed for clarity

### Quick Wins

- FAQ document (reduces support tickets)
- Keyboard navigation (accessibility win)
- Loading states (perceived performance)

---

## Phase 5: Testing & Launch (2 weeks)

### Objective
Validate the installer across real hosting environments and execute a staged launch.

### Tasks

#### Week 1: Beta Testing

1. **Internal Testing (2 days)**
   - [ ] Full installation on 5+ cPanel hosts
   - [ ] MySQL and PostgreSQL testing
   - [ ] Error injection testing (what happens when things fail)
   - [ ] Performance testing (slow connections)
   - [ ] Security penetration testing

2. **Beta Partner Testing (3 days)**
   - [ ] Recruit 10-20 beta churches
   - [ ] Provide beta keys and support channel
   - [ ] Collect feedback via survey
   - [ ] Track success/failure metrics
   - [ ] Daily triage of reported issues

#### Week 2: Launch

3. **Launch Preparation (2 days)**
   - [ ] Fix critical issues from beta
   - [ ] Final security audit
   - [ ] Performance optimization
   - [ ] Monitoring and alerting setup
   - [ ] Support documentation final review

4. **Staged Launch (3 days)**
   - [ ] Day 1: Soft launch to beta participants
   - [ ] Day 2: Announce to mailing list
   - [ ] Day 3: Public launch
   - [ ] Active monitoring first 72 hours
   - [ ] Rapid response team on standby

### Deliverables

| Deliverable | Description | Acceptance Criteria |
|-------------|-------------|---------------------|
| Hosting Compatibility | Tested host list | 10+ hosts verified |
| Beta Feedback Report | User testing results | >80% success rate |
| Security Audit | Penetration test results | No critical vulnerabilities |
| Performance Report | Load test results | <10s install per step |
| Launch Checklist | Go-live verification | All items checked |
| Monitoring Dashboard | Real-time metrics | Install success tracked |

### Hosting Provider Test Matrix

| Provider | cPanel | PostgreSQL | MySQL | Node.js | Status |
|----------|--------|------------|-------|---------|--------|
| Hostinger | Yes | No | Yes | Yes | To Test |
| Bluehost | Yes | No | Yes | Yes | To Test |
| SiteGround | Yes | Yes | Yes | Yes | To Test |
| A2 Hosting | Yes | Yes | Yes | Yes | To Test |
| GreenGeeks | Yes | Yes | Yes | Yes | To Test |
| InMotion | Yes | Yes | Yes | Yes | To Test |
| HostGator | Yes | No | Yes | Yes | To Test |
| DreamHost | Yes | Yes | Yes | Yes | To Test |
| Cloudways | No* | Yes | Yes | Yes | To Test |
| DigitalOcean | No* | Yes | Yes | Yes | To Test |

*Note: Cloudways/DigitalOcean are VPS, not shared hosting - different installer path needed

### Go/No-Go Criteria for Launch

- [ ] 90%+ install success rate in beta
- [ ] Zero critical security vulnerabilities
- [ ] Support documentation complete
- [ ] License server stable under load
- [ ] Monitoring and alerting operational
- [ ] Rollback plan documented
- [ ] Support team trained

---

## Technical Dependencies

### New npm Packages Required

| Package | Purpose | Phase |
|---------|---------|-------|
| knex | Database query builder/migrations | 0 |
| mysql2 | MySQL driver | 0 |
| objection | ORM built on Knex (optional) | 0 |
| node-machine-id | Hardware fingerprinting for licensing | 3 |
| crypto-js | Client-side license key handling | 3 |
| @tanstack/react-query | Already installed, ensure latest | - |

### External Services Required

| Service | Purpose | Cost Estimate | Phase |
|---------|---------|---------------|-------|
| License Server Hosting | Run license validation API | $10-50/month (VPS) | 3 |
| Transactional Email | License notifications, support | $0-20/month (SendGrid/Mailgun) | 3 |
| Error Tracking | Monitor install failures | $0-29/month (Sentry) | 5 |
| Analytics | Track install success rates | $0 (self-hosted Plausible) | 5 |
| Documentation Hosting | User docs | $0 (GitHub Pages) | 4 |

### Infrastructure Requirements

```
Production Environment:
+------------------+     +------------------+     +------------------+
|  License Server  |<--->|  Main LMS        |<--->|  Documentation   |
|  (Separate VPS)  |     |  (Customer Host) |     |  (Static Site)   |
+------------------+     +------------------+     +------------------+
       |                         |
       v                         v
+------------------+     +------------------+
|  License DB      |     |  Customer DB     |
|  (PostgreSQL)    |     |  (MySQL/PG)      |
+------------------+     +------------------+
```

### Documentation Requirements

| Document | Purpose | Phase |
|----------|---------|-------|
| DATABASE_ABSTRACTION.md | Technical guide for DB layer | 0 |
| MIGRATION_GUIDE.md | Writing and running migrations | 0 |
| INSTALLER_ARCHITECTURE.md | How installer works | 1 |
| HOSTING_REQUIREMENTS.md | Minimum hosting specs | 1 |
| LICENSE_INTEGRATION.md | How licensing works | 3 |
| INSTALLATION_GUIDE.md | End-user install guide | 4 |
| ADMIN_QUICKSTART.md | Post-install admin guide | 4 |
| TROUBLESHOOTING.md | Common issues and fixes | 4 |
| SUPPORT_RUNBOOK.md | Internal support procedures | 5 |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| cPanel compatibility issues | Medium | High | Test on multiple hosts early in Phase 1; maintain compatibility matrix |
| Database abstraction complexity | High | Medium | Start with proven Knex.js; incremental migration; extensive testing |
| Node.js not available on hosts | Medium | High | Document minimum requirements clearly; provide VPS alternative path |
| MySQL feature gaps (vs PostgreSQL) | Medium | Medium | Identify critical JSONB usage early; design around limitations |
| License server downtime | Low | High | Offline grace period; caching; redundancy |
| Installation taking too long | Medium | Medium | Async operations; progress feedback; skip optional steps |
| Support ticket overload at launch | High | Medium | Extensive documentation; beta testing; staggered launch |
| Security vulnerabilities | Low | Critical | Security audit before launch; regular penetration testing |
| User abandons mid-install | Medium | Medium | Save progress; resume capability; email follow-up |
| Hosting provider blocks installer | Low | High | Test detection/blocking; provide manual alternative |

### Risk Response Plan

**If cPanel Compatibility Fails:**
1. Pivot to Docker-first approach
2. Partner with specific hosting providers
3. Offer managed installation service

**If Database Abstraction Proves Too Complex:**
1. Ship PostgreSQL-only first
2. MySQL support as Phase 6
3. Focus on hosts with PostgreSQL (SiteGround, A2, etc.)

**If Launch Support Is Overwhelming:**
1. Pause public launch
2. Implement automated troubleshooting
3. Create video tutorials for common issues

---

## Resource Requirements

### Development Effort Estimates

| Phase | Duration | Effort (person-weeks) | Skills Required |
|-------|----------|----------------------|-----------------|
| Phase 0 | 2-3 weeks | 3-4 | Backend, Database |
| Phase 1 | 3-4 weeks | 4-5 | PHP, Backend, DevOps |
| Phase 2 | 2-3 weeks | 3-4 | Frontend, UX |
| Phase 3 | 2-3 weeks | 3-4 | Backend, Security |
| Phase 4 | 2 weeks | 2-3 | Content, Design |
| Phase 5 | 2 weeks | 2-3 | QA, DevOps |
| **Total** | **13-17 weeks** | **17-23** | |

### Team Requirements

| Role | Allocation | Phases Active |
|------|------------|---------------|
| Backend Developer | 100% | 0, 1, 3 |
| Frontend Developer | 50-100% | 1, 2, 4 |
| DevOps Engineer | 25-50% | 0, 1, 5 |
| UX Designer | 25% | 2, 4 |
| Technical Writer | 25% | 4 |
| QA Engineer | 50% | 1-5 |
| Project Manager | 25% | All |

### Testing Resources

- 10+ different cPanel hosting accounts for compatibility testing
- Beta program with 10-20 real church installations
- Automated testing infrastructure (CI/CD)
- Load testing environment for license server

### Design/UX Requirements

- Installer UI mockups and user flow diagrams
- Icon set for step progress
- Color scheme for installer (separate from main app)
- Responsive breakpoints defined
- Accessibility checklist and testing tools

---

## Success Criteria Summary

### Phase Success Criteria

| Phase | Success Defined As |
|-------|-------------------|
| Phase 0 | All tests pass on both PostgreSQL and MySQL |
| Phase 1 | Clean install succeeds on 3+ cPanel hosts |
| Phase 2 | Non-technical user completes install unassisted |
| Phase 3 | License activation/deactivation flow works |
| Phase 4 | Documentation rated "clear" by beta users |
| Phase 5 | 90%+ install success rate in beta |

### Launch Success Criteria

| Metric | 30-Day Target | 90-Day Target |
|--------|---------------|---------------|
| Total Installations | 50+ | 200+ |
| Success Rate | > 90% | > 95% |
| Support Tickets/Install | < 1.0 | < 0.5 |
| Avg Install Time | < 20 min | < 15 min |
| Customer Satisfaction | > 3.5/5 | > 4.0/5 |
| License Conversions | 10% to paid | 20% to paid |

---

## Post-Launch Roadmap

### Phase 6: Docker Support (Q3 2026)

**Goal:** Enable one-command installation via Docker Compose

- Docker Compose configuration
- Pre-built images for app + database
- Documentation for VPS deployment
- Watchtower auto-updates

### Phase 7: One-Click Installers (Q4 2026)

**Goal:** Partner with hosting providers for marketplace presence

- Softaculous integration
- Installatron package
- Cloudways template
- DigitalOcean 1-Click App
- Bitnami image

### Phase 8: Multi-Site Support (2027)

**Goal:** Enable denominational deployments

- Multi-tenant architecture
- Central management dashboard
- Shared user authentication
- Content syndication between sites
- Centralized license management

### Phase 9: White-Label Program (2027)

**Goal:** Enable partners to resell customized versions

- Complete branding removal option
- Custom domain for license server
- Partner API access
- Revenue sharing model
- Custom feature development track

---

## Appendix A: Existing System Analysis

### Current Database Usage (PostgreSQL via postgres.js)

Key patterns that need abstraction:
- Tagged template literals: `` sql`SELECT * FROM courses` ``
- JSONB columns for flexible data
- Array types for tags/categories
- UUID primary keys
- Timestamp with timezone

### Migration Complexity Assessment

| Table | Complexity | Notes |
|-------|-----------|-------|
| profiles | Low | Standard columns |
| courses | Medium | JSONB settings column |
| lessons | Medium | Content as JSONB |
| assessments | High | Complex question structure |
| payments | Low | Standard payment fields |
| certificates | Low | Standard fields |
| *43 tables total* | | |

### Estimated JSONB Usage

- Course settings: 5 tables
- Lesson content: 3 tables
- Assessment questions: 2 tables
- User preferences: 1 table

**Migration Strategy:** Convert JSONB to TEXT/JSON with application-level parsing where native support unavailable.

---

## Appendix B: Related Documentation

- `docs/DATABASE_STRATEGY.md` - Current database approach
- `docs/DEPLOYMENT.md` - Current deployment process
- `docs/CONTINUITY_README.md` - Project status and context
- `docs/installer/research/` - Research documents (to be created)

---

## Document History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-11 | 1.0 | Initial roadmap creation | AI Assistant |

---

## Next Steps

1. **Immediate (This Week)**
   - Review roadmap with stakeholders
   - Get buy-in on Phase 0 approach
   - Set up research folder for additional documentation

2. **Next Week**
   - Begin Phase 0 research (Knex.js evaluation)
   - Document current query patterns
   - Set up MySQL test environment

3. **Within 2 Weeks**
   - Complete Phase 0 design document
   - Begin database abstraction implementation
   - Create first migration files

---

*This document is the master plan for the Church LMS Installer project. All related documents should reference this roadmap for context and alignment.*
