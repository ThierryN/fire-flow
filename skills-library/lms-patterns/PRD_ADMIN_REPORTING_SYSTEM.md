# PRD: Admin Reporting System - School of the Prophets

**Version:** 1.0
**Date:** January 5, 2026
**Status:** Draft
**Author:** Claude Code

---

## Executive Summary

Build an admin reporting system that replaces the current Excel-based tracking process for prayer room statistics, teaching schedules, and ministry metrics. The system will allow administrators to input daily metrics through a web interface, generate automated Word and PDF reports, and email reports to leadership.

---

## Current State Analysis

### Existing Excel Structure

Based on analysis of `SOS PRAYER CHARTS 1.1.1- 2025.xlsx`:

**Monthly Data Tabs (12 per year):**
- JAN24 through DEC26 (organized by year)
- Each sheet contains ~300+ rows for daily tracking
- Data organized by weeks (Week 1, Week 2, etc.)

**Prayer Session Time Slots (5 per day):**
| Slot | Name | Typical Time |
|------|------|--------------|
| 1 | Morning Intimacy | 10am EST |
| 2 | Noon Day | 1-4pm |
| 3 | Evening Incense | 7:30pm |
| 4 | Midnight Quake&Shake | 1-3am |
| 5 | Spanish | Varies |

**Metrics Tracked Per Session:**
| Code | Metric | Description |
|------|--------|-------------|
| TC | Total Room Count | Number of attendees in prayer room |
| PP | Prayed on Platform | Number who prayed publicly |
| PR | Prayer Request Count | Prayer requests received |
| PS | Prophesied | Number of people who prophesied |
| PC | Prophecies Given | Total prophecies delivered |
| DI | Dream Interpretation Provided | Dream interpretations offered |
| DC | Dreams Interpreted Count | Total dreams interpreted |

**Additional Tabs:**
1. **Prayer Rotation** - Weekly schedule of prayer leaders, co-leads, and co-mods by time slot
2. **Teaching Schedule** - Class schedules with topics, instructors, and time slots
3. **Prophetic Fire** - Special prophetic event tracking

---

## Problem Statement

1. **Manual Data Entry** - Excel requires manual cell-by-cell entry, prone to formula errors
2. **No Real-time Access** - File must be downloaded/shared manually
3. **Report Generation** - Creating Word/PDF reports requires manual copy-paste
4. **Distribution** - Reports must be manually emailed to leadership
5. **Historical Analysis** - Comparing trends across months/years is difficult
6. **Multi-user Access** - Only one person can edit at a time

---

## Proposed Solution

Build an integrated reporting module within the LMS admin panel with:

1. **Data Input Interface** - Form-based daily metric entry
2. **Report Generator** - Automated Word/PDF report creation
3. **Email Distribution** - One-click report delivery to leadership
4. **Dashboard** - Visual analytics with charts and trends
5. **Schedule Management** - Prayer rotation and teaching schedule editors

---

## User Stories

### Prayer Team Lead (Data Entry)
- As a prayer team lead, I want to enter daily prayer metrics through a simple form after my session
- As a prayer team lead, I want to see my assigned time slots and quickly enter data
- As a prayer team lead, I want the form to remember my last entries as defaults
- As a prayer team lead, I want to edit past entries if I made a mistake

### Admin (Data Management)
- As an admin, I want to see a weekly view of all sessions so I can review data at a glance
- As an admin, I want the system to calculate daily/weekly/monthly totals automatically
- As an admin, I want to see which sessions are missing data

### Admin (Report Generation)
- As an admin, I want to generate a monthly report with one click
- As an admin, I want to preview the report before downloading
- As an admin, I want to export reports in Word and PDF formats
- As an admin, I want to email reports directly to leadership from the system

### Admin (System Configuration)
- As an admin, I want to add new metric types without developer help
- As an admin, I want to rename or disable metrics that are no longer used
- As an admin, I want to add new time slots if our schedule changes
- As an admin, I want to configure which metrics appear on reports

### Leadership (Report Consumer)
- As a leader, I want to receive formatted monthly reports via email
- As a leader, I want reports that match our current Word document format
- As a leader, I want to see trends and comparisons to previous periods

---

## Functional Requirements

### FR1: Data Entry Module

**FR1.1 - Daily Metrics Input**
```
Input Form Fields:
├── Date Picker (defaults to today)
├── Time Slot Selector (Morning/Noon/Evening/Midnight/Spanish)
├── Metric Fields:
│   ├── Total Room Count (TC) - Number input
│   ├── Prayed on Platform (PP) - Number input
│   ├── Prayer Requests (PR) - Number input
│   ├── Prophesied (PS) - Number input
│   ├── Prophecies Given (PC) - Number input
│   ├── Dream Interpretations (DI) - Number input
│   └── Dreams Interpreted (DC) - Number input
└── Submit Button
```

**FR1.2 - Weekly View**
- Display 7-day grid with all time slots
- Show daily totals in rightmost column
- Allow inline editing of cells
- Color-code cells (empty = red, filled = green)

**FR1.3 - Bulk Import**
- Upload Excel file to import historical data
- Validate structure before import
- Preview data before confirmation
- Map columns to database fields

### FR2: Report Generator

**FR2.1 - Report Templates**
| Template | Period | Contents |
|----------|--------|----------|
| Weekly Summary | 7 days | All metrics by day and session |
| Monthly Report | 1 month | Aggregated metrics, trends, comparisons |
| Quarterly Review | 3 months | YTD progress, goal tracking |
| Annual Report | 12 months | Full year analysis |

**FR2.2 - Report Contents (Monthly)**
Based on existing Word document format:
```
School of The Holy Spirit - [Month] Report [Year]

1. Executive Summary
   - Total attendance across all sessions
   - Comparison to previous month
   - Notable highlights

2. Daily Breakdown
   - Table of metrics by day
   - Session-level detail

3. Weekly Summaries
   - Week 1-4 totals
   - Weekly averages

4. Prayer Rotation Summary
   - Leader performance metrics
   - Session coverage statistics

5. Teaching Schedule Summary
   - Classes held
   - Attendance per class

6. Prophetic Ministry
   - Total prophecies
   - Dream interpretations
```

**FR2.3 - Export Formats**
- Word Document (.docx) - Editable format for leadership
- PDF Document (.pdf) - Fixed format for archiving/distribution
- Excel (.xlsx) - Raw data export

### FR3: Email Distribution

**FR3.1 - Email Recipients**
- Configurable recipient list (stored in admin settings)
- Default recipients: Senior leadership, department heads
- CC/BCC support

**FR3.2 - Email Template**
```
Subject: [Church Name] - [Month] Ministry Report

Body:
Dear Leadership Team,

Please find attached the [Month] [Year] ministry report
for School of The Holy Spirit.

Key Highlights:
- Total Attendance: [X] across [Y] sessions
- Prophecies Delivered: [Z]
- Prayer Requests: [N]

The full report is attached in PDF format.

Blessings,
[Admin Name]
School of the Prophets
```

### FR4: Dashboard & Analytics

**FR4.1 - Dashboard Widgets**
- Current month overview (cards)
- Attendance trend chart (line graph, last 6 months)
- Session comparison (bar chart)
- Top metrics summary

**FR4.2 - Filters**
- Date range picker
- Year/Month selector
- Time slot filter
- Metric type selector

### FR5: Schedule Management

**FR5.1 - Prayer Rotation Editor**
- Weekly grid view (Mon-Sun x 5 time slots)
- Assign leaders/co-leads per slot
- Staff member dropdown (from users table)
- Save/publish changes

**FR5.2 - Teaching Schedule Editor**
- Topic and instructor assignment
- Recurring schedule support
- Integration with course system

### FR6: Admin Configuration (CRUD for Future Flexibility)

**FR6.1 - Metric Types Manager**
Allows admins to add/edit/disable metric types without code changes.

```
Metric Configuration Fields:
├── Code (e.g., "TC", "PP", "NEW1")
├── Display Name (e.g., "Total Room Count")
├── Description (e.g., "Number of attendees in prayer room")
├── Data Type (integer, decimal, text, boolean)
├── Is Required (checkbox)
├── Show on Report (checkbox)
├── Display Order (drag to reorder)
├── Is Active (toggle to disable without deleting)
└── Created/Modified timestamps
```

**FR6.2 - Time Slots Manager**
Allows admins to add/edit/disable time slots.

```
Time Slot Configuration Fields:
├── Slot Code (e.g., "morning", "noon", "spanish")
├── Display Name (e.g., "Morning Intimacy")
├── Typical Time (e.g., "10:00 AM EST")
├── Display Order
├── Is Active
└── Color Code (for UI display)
```

**FR6.3 - Report Templates Manager**
Allows admins to configure what appears on reports.

```
Template Configuration:
├── Template Name (e.g., "Monthly Summary")
├── Metrics to Include (multi-select from active metrics)
├── Time Slots to Include (multi-select)
├── Show Weekly Breakdown (toggle)
├── Show Comparisons (toggle)
├── Header Text (customizable)
├── Footer Text (customizable)
└── Logo Upload
```

**FR6.4 - Access Permissions**
Configure who can enter data for which time slots.

```
Permission Matrix:
├── User/Role
├── Allowed Time Slots (checkboxes)
├── Can Edit Own Entries (toggle)
├── Can Edit All Entries (toggle)
├── Can View Reports (toggle)
└── Can Generate Reports (toggle)
```

---

## Technical Requirements

### TR1: Database Schema

```sql
-- ═══════════════════════════════════════════════════════════
-- CONFIGURATION TABLES (Admin CRUD for flexibility)
-- ═══════════════════════════════════════════════════════════

-- Configurable Metric Types (admin can add new metrics)
CREATE TABLE metric_types (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  code VARCHAR(20) UNIQUE NOT NULL,       -- e.g., "TC", "PP", "NEW1"
  display_name VARCHAR(100) NOT NULL,     -- e.g., "Total Room Count"
  description TEXT,
  data_type VARCHAR(20) DEFAULT 'integer', -- integer, decimal, text, boolean
  is_required BOOLEAN DEFAULT FALSE,
  show_on_report BOOLEAN DEFAULT TRUE,
  display_order INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Configurable Time Slots (admin can add new slots)
CREATE TABLE time_slots (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  code VARCHAR(50) UNIQUE NOT NULL,       -- e.g., "morning", "noon"
  display_name VARCHAR(100) NOT NULL,     -- e.g., "Morning Intimacy"
  typical_time VARCHAR(50),               -- e.g., "10:00 AM EST"
  display_order INTEGER DEFAULT 0,
  color_code VARCHAR(7) DEFAULT '#3B82F6', -- Hex color for UI
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Default metric types (seeded on installation)
INSERT INTO metric_types (code, display_name, description, display_order) VALUES
  ('TC', 'Total Room Count', 'Number of attendees in prayer room', 1),
  ('PP', 'Prayed on Platform', 'Number who prayed publicly', 2),
  ('PR', 'Prayer Request Count', 'Prayer requests received', 3),
  ('PS', 'Prophesied', 'Number of people who prophesied', 4),
  ('PC', 'Prophecies Given', 'Total prophecies delivered', 5),
  ('DI', 'Dream Interp. Provided', 'Dream interpretations offered', 6),
  ('DC', 'Dreams Interpreted', 'Total dreams interpreted', 7);

-- Default time slots (seeded on installation)
INSERT INTO time_slots (code, display_name, typical_time, display_order, color_code) VALUES
  ('morning', 'Morning Intimacy', '10:00 AM EST', 1, '#F59E0B'),
  ('noon', 'Noon Day', '1:00 PM - 4:00 PM', 2, '#10B981'),
  ('evening', 'Evening Incense', '7:30 PM EST', 3, '#6366F1'),
  ('midnight', 'Midnight Quake&Shake', '1:00 AM - 3:00 AM', 4, '#8B5CF6'),
  ('spanish', 'Spanish', 'Varies', 5, '#EF4444');

-- ═══════════════════════════════════════════════════════════
-- DATA TABLES
-- ═══════════════════════════════════════════════════════════

-- Prayer Session Metrics (daily entries - flexible schema using JSONB)
CREATE TABLE prayer_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  date DATE NOT NULL,
  time_slot_id UUID REFERENCES time_slots(id),
  metrics JSONB NOT NULL DEFAULT '{}',     -- Flexible: {"TC": 15, "PP": 5, ...}
  entered_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(date, time_slot_id)
);

-- Index for fast JSONB queries
CREATE INDEX idx_prayer_metrics_date ON prayer_metrics(date);
CREATE INDEX idx_prayer_metrics_jsonb ON prayer_metrics USING GIN (metrics);

-- Helper function to get metric value
CREATE OR REPLACE FUNCTION get_metric(metrics JSONB, metric_code TEXT)
RETURNS INTEGER AS $$
BEGIN
  RETURN COALESCE((metrics->>metric_code)::INTEGER, 0);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Prayer Rotation Schedule
CREATE TABLE prayer_rotation (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  day_of_week INTEGER NOT NULL, -- 0=Sunday, 1=Monday, etc.
  time_slot VARCHAR(50) NOT NULL,
  leader_id UUID REFERENCES users(id),
  co_leads UUID[] DEFAULT '{}',
  co_mods UUID[] DEFAULT '{}',
  effective_from DATE NOT NULL,
  effective_to DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Teaching Schedule
CREATE TABLE teaching_schedule (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  day_of_week INTEGER NOT NULL,
  time_slot VARCHAR(50) NOT NULL,
  topic VARCHAR(255),
  instructor_id UUID REFERENCES users(id),
  week_of_month INTEGER, -- 1-4 for rotating schedules
  effective_from DATE NOT NULL,
  effective_to DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Generated Reports Archive
CREATE TABLE generated_reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  report_type VARCHAR(50) NOT NULL, -- weekly, monthly, quarterly, annual
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  file_path VARCHAR(500),
  file_format VARCHAR(10), -- pdf, docx, xlsx
  generated_by UUID REFERENCES users(id),
  emailed_to TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Report Recipients
CREATE TABLE report_recipients (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  report_types TEXT[] DEFAULT '{monthly}',
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Views for aggregation
CREATE VIEW monthly_metrics_summary AS
SELECT
  DATE_TRUNC('month', date) AS month,
  SUM(room_count) AS total_attendance,
  SUM(prayed_on_platform) AS total_prayed,
  SUM(prayer_requests) AS total_requests,
  SUM(prophesied) AS total_prophesied,
  SUM(prophecies_given) AS total_prophecies,
  SUM(dream_interp_provided) AS total_dream_interps,
  SUM(dreams_interpreted) AS total_dreams
FROM prayer_metrics
GROUP BY DATE_TRUNC('month', date);
```

### TR2: API Endpoints

```
-- CONFIGURATION (Admin CRUD) --
GET    /api/admin/reports/config/metrics       - List all metric types
POST   /api/admin/reports/config/metrics       - Create new metric type
PUT    /api/admin/reports/config/metrics/:id   - Update metric type
DELETE /api/admin/reports/config/metrics/:id   - Disable metric type (soft delete)

GET    /api/admin/reports/config/timeslots     - List all time slots
POST   /api/admin/reports/config/timeslots     - Create new time slot
PUT    /api/admin/reports/config/timeslots/:id - Update time slot
DELETE /api/admin/reports/config/timeslots/:id - Disable time slot (soft delete)

GET    /api/admin/reports/config/templates     - List report templates
POST   /api/admin/reports/config/templates     - Create report template
PUT    /api/admin/reports/config/templates/:id - Update report template

-- DATA ENTRY (Prayer Team Leads + Admins) --
POST   /api/reports/metrics                    - Create/update daily metrics
GET    /api/reports/metrics                    - Get metrics (with date filters)
GET    /api/reports/metrics/my-entries         - Get current user's entries
GET    /api/reports/metrics/missing            - Get dates/slots with missing data

-- REPORTS (Admins) --
POST   /api/admin/reports/import               - Bulk import from Excel
GET    /api/admin/reports/generate/:type       - Generate report (weekly/monthly)
POST   /api/admin/reports/email                - Send report via email
GET    /api/admin/reports/dashboard            - Get dashboard data
GET    /api/admin/reports/history              - Get generated reports history

-- SCHEDULES --
GET    /api/admin/reports/rotation             - Get prayer rotation
PUT    /api/admin/reports/rotation             - Update prayer rotation
GET    /api/admin/reports/teaching             - Get teaching schedule
PUT    /api/admin/reports/teaching             - Update teaching schedule

-- RECIPIENTS --
GET    /api/admin/reports/recipients           - Get email recipients
POST   /api/admin/reports/recipients           - Add recipient
DELETE /api/admin/reports/recipients/:id       - Remove recipient
```

### TR3: Technology Stack

| Component | Technology | Justification |
|-----------|------------|---------------|
| Excel Parsing | `xlsx` (SheetJS) | Fast, reliable, 3M+ weekly downloads |
| Word Generation | `docx` | Full TypeScript support, no dependencies |
| PDF Generation | `puppeteer` | Best HTML-to-PDF quality |
| Email | `nodemailer` + existing SMTP | Already configured in system |
| Charts | `chart.js` + `chartjs-node-canvas` | For PDF chart embedding |
| Job Queue | `bull` (optional) | For large imports/exports |

### TR4: File Structure

```
client/src/
├── pages/admin/
│   └── reports/
│       ├── ReportsDashboard.jsx      - Main dashboard
│       ├── MetricsEntry.jsx          - Daily data entry form (Team Leads)
│       ├── WeeklyView.jsx            - 7-day grid view (Admins)
│       ├── GenerateReport.jsx        - Report generator
│       ├── ImportData.jsx            - Excel import wizard
│       ├── PrayerRotation.jsx        - Rotation schedule editor
│       ├── TeachingSchedule.jsx      - Teaching schedule editor
│       └── settings/                 - Configuration pages
│           ├── MetricTypes.jsx       - CRUD for metric types
│           ├── TimeSlots.jsx         - CRUD for time slots
│           ├── ReportTemplates.jsx   - Configure report layouts
│           └── Recipients.jsx        - Email recipients manager
└── components/reports/
    ├── MetricsForm.jsx               - Reusable metrics input form
    ├── MetricsGrid.jsx               - Weekly grid component
    ├── ReportPreview.jsx             - Preview before export
    ├── DashboardWidgets.jsx          - Dashboard cards/charts
    ├── ConfigTable.jsx               - Reusable CRUD table component
    └── ImportWizard/                 - Multi-step import
        ├── FileUpload.jsx
        ├── SheetSelector.jsx
        ├── ColumnMapper.jsx
        └── PreviewConfirm.jsx

server/
├── controllers/
│   ├── reportsController.js          - Data entry + report endpoints
│   └── reportsConfigController.js    - Configuration CRUD endpoints
├── services/
│   └── reports/
│       ├── excelParser.js            - Parse imported Excel files
│       ├── reportGenerator.js        - Generate Word/PDF reports
│       ├── emailService.js           - Send reports via email
│       └── metricsAggregator.js      - Calculate summaries
├── models/
│   ├── PrayerMetrics.pg.js           - Metrics data model
│   ├── MetricType.pg.js              - Metric type configuration
│   ├── TimeSlot.pg.js                - Time slot configuration
│   └── ReportTemplate.pg.js          - Report template model
├── routes/
│   ├── reportRoutes.js               - Data entry routes
│   └── reportConfigRoutes.js         - Configuration routes (admin)
└── templates/
    └── reports/
        ├── monthly-report.html       - HTML template for PDF
        └── report-email.html         - Email body template
```

---

## UI/UX Requirements

### UX1: Navigation
Add to admin sidebar:
```
Reports
├── Dashboard
├── Enter Metrics          (Prayer Team Leads + Admins)
├── Weekly View            (Admins - see all data)
├── Generate Reports       (Admins)
├── Import Data            (Admins)
├── Schedules
│   ├── Prayer Rotation
│   └── Teaching Schedule
└── Settings (Admins only)
    ├── Metric Types       (CRUD - add/edit metrics)
    ├── Time Slots         (CRUD - add/edit slots)
    ├── Report Templates   (Configure report layouts)
    └── Email Recipients   (Manage recipient list)
```

### UX2: Metrics Entry Form
- Mobile-responsive for on-the-go entry
- Numeric keypad on mobile for number inputs
- Auto-save draft every 30 seconds
- Validation: non-negative integers only
- Success toast on save

### UX3: Report Preview
- Split view: controls on left, preview on right
- Zoom in/out capability
- Page navigation for multi-page reports
- Download button (PDF/Word toggle)
- Email button with recipient selector

### UX4: Dashboard
- Card layout for key metrics
- Interactive charts (hover for details)
- Quick action buttons (Enter Today, Generate Report)
- Recent reports list

---

## Implementation Phases

### Phase 1: MVP (Core Functionality + Flexibility)
1. Database migrations for all tables (including config tables)
2. **Admin Configuration CRUD** - Metric types and time slots managers
3. Metrics entry form (daily input by prayer team leads)
4. Weekly view with inline editing (admins)
5. Basic monthly report generation (PDF only)
6. Manual download of reports

**Estimated Scope:** 7-9 major components

### Phase 2: Enhanced Features
1. Excel import wizard (for historical data)
2. Word document generation (.docx export)
3. Email distribution with recipient management
4. Dashboard with basic charts
5. Prayer rotation schedule editor
6. Report templates manager

**Estimated Scope:** 6-7 major components

### Phase 3: Advanced Features
1. Teaching schedule editor
2. Advanced analytics (trends, year-over-year comparisons)
3. Automated scheduled reports (weekly/monthly auto-send)
4. Custom report builder (drag-and-drop)
5. API for external integrations
6. Mobile-optimized data entry app

**Estimated Scope:** 5-6 major components

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Data entry time | <2 min per session (vs 5+ min in Excel) |
| Report generation | <30 seconds |
| Admin adoption | 100% switch from Excel within 1 month |
| Report accuracy | Zero manual calculation errors |
| Email delivery | 95%+ successful delivery rate |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data migration errors | High | Validate import with checksums, manual review |
| PDF formatting issues | Medium | Use HTML templates, extensive testing |
| Email deliverability | Medium | Use established SMTP, SPF/DKIM records |
| User resistance to change | Medium | Training sessions, side-by-side operation period |
| Performance with large datasets | Low | Indexed queries, pagination, caching |

---

## Appendix A: Sample Report Output

Based on existing Word document format:

```
╔══════════════════════════════════════════════════════════════╗
║         SCHOOL OF THE HOLY SPIRIT - JUNE REPORT 2025         ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  EXECUTIVE SUMMARY                                           ║
║  ─────────────────                                           ║
║  Total Attendance:     1,247 across 124 sessions             ║
║  Prayers on Platform:    312 individuals                     ║
║  Prayer Requests:         89 received                        ║
║  Prophecies Delivered:   156 words given                     ║
║  Dreams Interpreted:      23 interpretations                 ║
║                                                              ║
║  COMPARISON TO MAY 2025                                      ║
║  ─────────────────────                                       ║
║  Attendance:       ↑ 12% increase                            ║
║  Prophecies:       ↑  8% increase                            ║
║  Prayer Requests:  ↓  5% decrease                            ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  WEEKLY BREAKDOWN                                            ║
╠══════════════════════════════════════════════════════════════╣
║  Week  │ TC   │ PP  │ PR │ PS │ PC │ DI │ DC                 ║
║  ──────┼──────┼─────┼────┼────┼────┼────┼────                ║
║  Wk 1  │  312 │  78 │ 22 │ 45 │ 38 │  8 │  5                 ║
║  Wk 2  │  298 │  71 │ 19 │ 41 │ 35 │  6 │  4                 ║
║  Wk 3  │  321 │  85 │ 25 │ 52 │ 44 │  9 │  7                 ║
║  Wk 4  │  316 │  78 │ 23 │ 48 │ 39 │  7 │  7                 ║
║  ──────┼──────┼─────┼────┼────┼────┼────┼────                ║
║  TOTAL │ 1247 │ 312 │ 89 │186 │156 │ 30 │ 23                 ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Appendix B: Excel Column Mapping

For bulk import from existing Excel files:

| Excel Column | Database Field | Type |
|--------------|----------------|------|
| Date (B column) | date | DATE |
| Morning Intimacy (D) | time_slot='morning' | - |
| Noon Day (E) | time_slot='noon' | - |
| Evening Incense (F) | time_slot='evening' | - |
| Midnight Quake&Shake (G) | time_slot='midnight' | - |
| Spanish (H) | time_slot='spanish' | - |
| Total Room Count (TC) | room_count | INTEGER |
| Prayed on Platform (PP) | prayed_on_platform | INTEGER |
| Prayer Request Count (PR) | prayer_requests | INTEGER |
| Prophesied (PS) | prophesied | INTEGER |
| Prophecies Given (PC) | prophecies_given | INTEGER |
| Provided Dream Interp. (DI) | dream_interp_provided | INTEGER |
| Dreams Interpreted (DC) | dreams_interpreted | INTEGER |

---

## Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Owner | | | |
| Technical Lead | | | |
| Project Manager | | | |

---

*Document generated by Claude Code - January 5, 2026*
