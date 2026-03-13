# Theme System Integration with Installer Wizard

**Version:** 1.0
**Last Updated:** January 11, 2026
**Status:** PLANNING PHASE
**Related Documents:**
- `docs/theme-system/THEME_SYSTEM_ARCHITECTURE.md`
- `docs/theme-system/README.md`
- `docs/installer/IMPLEMENTATION_VISION.md`
- `docs/installer/CPANEL_INSTALLATION_GUIDE.md`

---

## Table of Contents

1. [Overview](#overview)
2. [Default Theme Selection During Install](#1-default-theme-selection-during-install)
3. [Theme Database Schema Compatibility](#2-theme-database-schema-compatibility)
4. [Theme File Structure in Installer Package](#3-theme-file-structure-in-installer-package)
5. [White-Label Configuration](#4-white-label-configuration)
6. [Theme Assets on Shared Hosting](#5-theme-assets-on-shared-hosting)
7. [Post-Install Theme Management](#6-post-install-theme-management)
8. [Starter Theme Specifications](#7-starter-theme-specifications)
9. [Database Migration Scripts](#8-database-migration-scripts)
10. [API Endpoints for Theme Management](#9-api-endpoints-for-theme-management)
11. [Error Handling](#10-error-handling)
12. [Performance Considerations](#11-performance-considerations)
13. [Security](#12-security)
14. [Architecture Diagrams](#architecture-diagrams)

---

## Overview

This document details how the Theme System integrates with the Installer Wizard for the Church LMS platform. The integration is designed to:

- Enable non-technical users (pastors) to select and customize themes during installation
- Support both PostgreSQL and MySQL databases on cPanel shared hosting
- Provide full white-label branding capabilities
- Ensure smooth theme asset deployment on budget hosting environments

### Target Audience

- **Primary:** Pastors and church administrators with no technical background
- **Secondary:** Church volunteers helping with website setup
- **Technical:** Developers extending or customizing the platform

### Key Design Principles

1. **Simplicity First:** One-click theme selection with sensible defaults
2. **Visual Preview:** See theme choices before committing
3. **Database Agnostic:** Theme storage works identically on PostgreSQL and MySQL
4. **Graceful Degradation:** System remains functional if theme loading fails
5. **Budget Hosting Compatible:** Optimized for shared hosting constraints

---

## 1. Default Theme Selection During Install

### 1.1 Theme Selection Wizard Step

The installer wizard includes a dedicated theme selection step that appears after database configuration and before admin account creation.

```
Installation Flow:
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Requirements Check                                      │
│  Step 2: Database Configuration                                  │
│  Step 3: ████ THEME SELECTION ████  <-- This section           │
│  Step 4: Organization Branding                                   │
│  Step 5: Admin Account Creation                                  │
│  Step 6: Email Configuration                                     │
│  Step 7: Final Installation                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 How the Wizard Presents Theme Choices

**Visual Layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│  Choose Your Theme                                    Step 3/7   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Select a visual style for your LMS. You can change this        │
│  anytime from the admin panel after installation.               │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │          │  │          │  │          │  │          │       │
│  │ [Preview]│  │ [Preview]│  │ [Preview]│  │ [Preview]│       │
│  │          │  │          │  │          │  │          │       │
│  ├──────────┤  ├──────────┤  ├──────────┤  ├──────────┤       │
│  │ Church   │  │ Modern   │  │ Youth    │  │ Academic │       │
│  │ Classic  │  │ Ministry │  │ Connect  │  │ Scholar  │       │
│  │ ◉ Active │  │ ○        │  │ ○        │  │ ○        │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                  │
│  [Preview Full Screen]              [Skip - Use Default]        │
│                                                                  │
│                              [← Back]  [Continue →]             │
└─────────────────────────────────────────────────────────────────┘
```

**UI Components:**

| Component | Description | User Action |
|-----------|-------------|-------------|
| Theme Card | Shows screenshot, name, and description | Click to select |
| Preview Button | Opens live preview in modal | View before selecting |
| Radio Selection | Visual indicator of current choice | Auto-updates on click |
| Skip Button | Proceeds with default theme | For users who want quick setup |
| Continue Button | Confirms selection and proceeds | Moves to next step |

### 1.3 Starter Themes Bundled with Installer

The installer package includes four carefully designed starter themes:

| Theme | File Size | Target Audience | Default |
|-------|-----------|-----------------|---------|
| `default` | ~150KB | Universal fallback | Yes |
| `church-classic` | ~280KB | Traditional churches | No |
| `modern-ministry` | ~320KB | Contemporary churches | No |
| `youth-connect` | ~350KB | Youth ministries | No |

### 1.4 Theme Preview During Installation

**Preview Modal Implementation:**

```
┌─────────────────────────────────────────────────────────────────┐
│  Preview: Modern Ministry                              [X Close] │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │                    [Live Preview Area]                   │   │
│  │                                                          │   │
│  │         Rendered with sample content and                 │   │
│  │         organization branding from previous step         │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Device Preview:  [Desktop]  [Tablet]  [Mobile]                 │
│                                                                  │
│                    [Select This Theme]  [Cancel]                │
└─────────────────────────────────────────────────────────────────┘
```

**Preview Features:**

1. **Live Rendering:** Theme CSS applied to sample LMS pages
2. **Responsive Preview:** Toggle between desktop, tablet, and mobile views
3. **Sample Content:** Shows how courses, lessons, and navigation look
4. **Brand Preview:** If logo was uploaded in previous step, shows it in theme
5. **Offline Capable:** Preview works without external resources

### 1.5 Default Theme Auto-Activation

**Activation Logic:**

```javascript
// Pseudo-code for theme activation during install
async function activateSelectedTheme(themeSlug, dbConnection) {
  // 1. Verify theme files exist
  const themePath = path.join(THEMES_DIR, themeSlug);
  if (!fs.existsSync(themePath)) {
    themeSlug = 'default'; // Fallback to default
  }

  // 2. Read theme manifest
  const manifest = JSON.parse(
    fs.readFileSync(path.join(themePath, 'theme.json'))
  );

  // 3. Insert theme record into database
  await dbConnection.query(`
    INSERT INTO themes (slug, name, version, status, installed_at, activated_at, manifest)
    VALUES ($1, $2, $3, 'active', NOW(), NOW(), $4)
  `, [themeSlug, manifest.name, manifest.version, JSON.stringify(manifest)]);

  // 4. Apply default theme settings
  await applyDefaultSettings(manifest.settings, dbConnection);

  // 5. Copy theme assets to public directory
  await copyThemeAssets(themePath);

  return { success: true, theme: themeSlug };
}
```

**Activation Sequence:**

```
Theme Activation Flow:
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ User Selects   │────▶│ Validate Theme │────▶│ Write to       │
│ Theme          │     │ Files Exist    │     │ Database       │
└────────────────┘     └────────────────┘     └───────┬────────┘
                                                       │
                                                       ▼
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ Theme Ready    │◀────│ Copy Assets to │◀────│ Apply Default  │
│ for Use        │     │ Public Dir     │     │ Settings       │
└────────────────┘     └────────────────┘     └────────────────┘
```

---

## 2. Theme Database Schema Compatibility

### 2.1 Schema Design Philosophy

The theme database schema is designed to be:

1. **Database Agnostic:** Works identically on PostgreSQL and MySQL
2. **JSON-Flexible:** Uses TEXT/JSON for flexible configuration storage
3. **Migration Ready:** Supports version upgrades without data loss
4. **Index Optimized:** Key lookups are fast on shared hosting

### 2.2 Theme Storage Schema for PostgreSQL

```sql
-- PostgreSQL Theme Tables
-- Migration: 20260111_001_create_themes_table.sql

-- Main themes table
CREATE TABLE themes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    description TEXT,
    author_name VARCHAR(255),
    author_email VARCHAR(255),
    author_url VARCHAR(500),

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'inactive'
        CHECK (status IN ('active', 'inactive', 'broken')),

    -- Timestamps
    installed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    activated_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- File system
    file_path VARCHAR(500) NOT NULL,

    -- Theme configuration (JSONB for PostgreSQL)
    manifest JSONB NOT NULL DEFAULT '{}',

    -- Metadata
    screenshot_url VARCHAR(500),
    download_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.00,

    -- Indexes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_themes_status ON themes(status);
CREATE INDEX idx_themes_slug ON themes(slug);

-- Theme settings table (user customizations)
CREATE TABLE theme_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    theme_id UUID NOT NULL REFERENCES themes(id) ON DELETE CASCADE,

    -- Settings data (JSONB for flexible structure)
    settings JSONB NOT NULL DEFAULT '{}',

    -- Organization support (for multi-tenant)
    organization_id UUID,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Unique per org+theme
    UNIQUE(theme_id, organization_id)
);

CREATE INDEX idx_theme_settings_theme ON theme_settings(theme_id);
CREATE INDEX idx_theme_settings_org ON theme_settings(organization_id);

-- Theme installation tracking
CREATE TABLE theme_installations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    theme_id UUID NOT NULL REFERENCES themes(id) ON DELETE CASCADE,
    installed_by UUID, -- user who installed
    installation_source VARCHAR(50) DEFAULT 'upload'
        CHECK (installation_source IN ('upload', 'marketplace', 'bundled', 'git')),

    -- Installation metadata
    installation_log TEXT,
    previous_version VARCHAR(20),

    -- Timestamps
    installed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_theme_installations_theme ON theme_installations(theme_id);
```

### 2.3 Theme Storage Schema for MySQL

```sql
-- MySQL Theme Tables
-- Migration: 20260111_001_create_themes_table.sql

-- Main themes table
CREATE TABLE themes (
    id CHAR(36) PRIMARY KEY,
    slug VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    description TEXT,
    author_name VARCHAR(255),
    author_email VARCHAR(255),
    author_url VARCHAR(500),

    -- Status (MySQL ENUM)
    status ENUM('active', 'inactive', 'broken') NOT NULL DEFAULT 'inactive',

    -- Timestamps
    installed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    activated_at DATETIME NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- File system
    file_path VARCHAR(500) NOT NULL,

    -- Theme configuration (JSON type for MySQL 5.7+)
    manifest JSON NOT NULL,

    -- Metadata
    screenshot_url VARCHAR(500),
    download_count INT DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.00,

    -- Created timestamp
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_themes_status (status),
    INDEX idx_themes_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Theme settings table (user customizations)
CREATE TABLE theme_settings (
    id CHAR(36) PRIMARY KEY,
    theme_id CHAR(36) NOT NULL,

    -- Settings data (JSON type)
    settings JSON NOT NULL,

    -- Organization support (for multi-tenant)
    organization_id CHAR(36) NULL,

    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Foreign key
    FOREIGN KEY (theme_id) REFERENCES themes(id) ON DELETE CASCADE,

    -- Unique constraint
    UNIQUE KEY unique_theme_org (theme_id, organization_id),

    -- Indexes
    INDEX idx_theme_settings_theme (theme_id),
    INDEX idx_theme_settings_org (organization_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Theme installation tracking
CREATE TABLE theme_installations (
    id CHAR(36) PRIMARY KEY,
    theme_id CHAR(36) NOT NULL,
    installed_by CHAR(36) NULL,
    installation_source ENUM('upload', 'marketplace', 'bundled', 'git') DEFAULT 'upload',

    -- Installation metadata
    installation_log TEXT,
    previous_version VARCHAR(20),

    -- Timestamps
    installed_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key
    FOREIGN KEY (theme_id) REFERENCES themes(id) ON DELETE CASCADE,

    -- Indexes
    INDEX idx_theme_installations_theme (theme_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 2.4 Migration Scripts for Both Databases

**Knex.js Migration (Database Agnostic):**

```javascript
// migrations/20260111_001_create_themes_tables.js

exports.up = async function(knex) {
  const isPostgres = knex.client.config.client === 'pg';
  const isMysql = knex.client.config.client === 'mysql' ||
                  knex.client.config.client === 'mysql2';

  // Create themes table
  await knex.schema.createTable('themes', (table) => {
    // Primary key - UUID
    if (isPostgres) {
      table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    } else {
      table.string('id', 36).primary();
    }

    table.string('slug', 100).notNullable().unique();
    table.string('name', 255).notNullable();
    table.string('version', 20).notNullable().defaultTo('1.0.0');
    table.text('description');
    table.string('author_name', 255);
    table.string('author_email', 255);
    table.string('author_url', 500);

    // Status
    if (isPostgres) {
      table.string('status', 20).notNullable().defaultTo('inactive');
    } else {
      table.enum('status', ['active', 'inactive', 'broken'])
           .notNullable().defaultTo('inactive');
    }

    // Timestamps
    table.timestamp('installed_at').defaultTo(knex.fn.now());
    table.timestamp('activated_at');
    table.timestamp('updated_at').defaultTo(knex.fn.now());

    // File system
    table.string('file_path', 500).notNullable();

    // Manifest - JSON/JSONB
    if (isPostgres) {
      table.jsonb('manifest').notNullable().defaultTo('{}');
    } else {
      table.json('manifest').notNullable();
    }

    // Metadata
    table.string('screenshot_url', 500);
    table.integer('download_count').defaultTo(0);
    table.decimal('rating', 3, 2).defaultTo(0.00);

    table.timestamp('created_at').defaultTo(knex.fn.now());

    // Indexes
    table.index('status');
    table.index('slug');
  });

  // Create theme_settings table
  await knex.schema.createTable('theme_settings', (table) => {
    if (isPostgres) {
      table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
      table.uuid('theme_id').notNullable()
           .references('id').inTable('themes').onDelete('CASCADE');
      table.uuid('organization_id');
      table.jsonb('settings').notNullable().defaultTo('{}');
    } else {
      table.string('id', 36).primary();
      table.string('theme_id', 36).notNullable()
           .references('id').inTable('themes').onDelete('CASCADE');
      table.string('organization_id', 36);
      table.json('settings').notNullable();
    }

    table.timestamp('created_at').defaultTo(knex.fn.now());
    table.timestamp('updated_at').defaultTo(knex.fn.now());

    table.unique(['theme_id', 'organization_id']);
    table.index('theme_id');
    table.index('organization_id');
  });

  // Create theme_installations table
  await knex.schema.createTable('theme_installations', (table) => {
    if (isPostgres) {
      table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
      table.uuid('theme_id').notNullable()
           .references('id').inTable('themes').onDelete('CASCADE');
      table.uuid('installed_by');
      table.string('installation_source', 50).defaultTo('upload');
    } else {
      table.string('id', 36).primary();
      table.string('theme_id', 36).notNullable()
           .references('id').inTable('themes').onDelete('CASCADE');
      table.string('installed_by', 36);
      table.enum('installation_source', ['upload', 'marketplace', 'bundled', 'git'])
           .defaultTo('upload');
    }

    table.text('installation_log');
    table.string('previous_version', 20);
    table.timestamp('installed_at').defaultTo(knex.fn.now());

    table.index('theme_id');
  });
};

exports.down = async function(knex) {
  await knex.schema.dropTableIfExists('theme_installations');
  await knex.schema.dropTableIfExists('theme_settings');
  await knex.schema.dropTableIfExists('themes');
};
```

### 2.5 Theme Settings JSON Structure

```json
{
  "colors": {
    "primary": "#4F46E5",
    "secondary": "#10B981",
    "accent": "#F59E0B",
    "background": "#FFFFFF",
    "text": "#1F2937"
  },
  "typography": {
    "fontFamily": "Inter",
    "headingFont": "Poppins",
    "baseFontSize": 16,
    "headingWeight": 600
  },
  "layout": {
    "containerWidth": "1280px",
    "headerStyle": "default",
    "sidebarPosition": "left",
    "footerColumns": 4
  },
  "branding": {
    "logo": "/uploads/branding/logo.png",
    "favicon": "/uploads/branding/favicon.ico",
    "ogImage": "/uploads/branding/og-image.jpg"
  },
  "custom": {
    "heroStyle": "fullWidth",
    "courseCardStyle": "modern",
    "enableAnimations": true
  }
}
```

---

## 3. Theme File Structure in Installer Package

### 3.1 Complete Installer Package Structure

```
installer/
├── install.php                    # Main installer entry point
├── install/
│   ├── lib/                       # PHP installer libraries
│   ├── steps/                     # Wizard step handlers
│   │   ├── requirements.php
│   │   ├── database.php
│   │   ├── theme-selection.php    # Theme selection step
│   │   ├── branding.php
│   │   ├── admin.php
│   │   ├── email.php
│   │   └── finalize.php
│   ├── assets/                    # Installer UI assets
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/                 # HTML templates
│
├── themes/                        # Bundled themes
│   ├── default/                   # Minimal default theme
│   │   ├── theme.json
│   │   ├── screenshot.png
│   │   ├── screenshot-thumb.png   # 400x300 thumbnail
│   │   ├── README.md
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Footer.jsx
│   │   │   │   └── Sidebar.jsx
│   │   │   └── common/
│   │   │       ├── Button.jsx
│   │   │       └── Card.jsx
│   │   ├── styles/
│   │   │   ├── theme.css
│   │   │   └── variables.css
│   │   └── assets/
│   │       ├── images/
│   │       └── fonts/
│   │
│   ├── church-classic/            # Traditional church theme
│   │   ├── theme.json
│   │   ├── screenshot.png
│   │   ├── screenshot-thumb.png
│   │   ├── README.md
│   │   ├── components/
│   │   ├── styles/
│   │   └── assets/
│   │
│   ├── modern-ministry/           # Contemporary theme
│   │   ├── theme.json
│   │   ├── screenshot.png
│   │   ├── screenshot-thumb.png
│   │   ├── README.md
│   │   ├── components/
│   │   ├── styles/
│   │   └── assets/
│   │
│   └── youth-connect/             # Youth ministry theme
│       ├── theme.json
│       ├── screenshot.png
│       ├── screenshot-thumb.png
│       ├── README.md
│       ├── components/
│       ├── styles/
│       └── assets/
│
├── server/                        # Node.js backend
├── client/                        # React frontend
├── config/                        # Configuration templates
└── package.json
```

### 3.2 Individual Theme Structure

Each bundled theme follows this exact structure:

```
theme-name/
├── theme.json                     # Required: Theme manifest
├── screenshot.png                 # Required: 1200x900px preview
├── screenshot-thumb.png           # Required: 400x300px thumbnail
├── README.md                      # Optional: Theme documentation
├── LICENSE.md                     # Optional: License file
│
├── components/                    # React component overrides
│   ├── layout/
│   │   ├── Header.jsx            # Header override
│   │   ├── Footer.jsx            # Footer override
│   │   ├── Sidebar.jsx           # Sidebar override
│   │   ├── Navigation.jsx        # Navigation override
│   │   └── Layout.jsx            # Main layout wrapper
│   │
│   ├── common/
│   │   ├── Button.jsx            # Button component
│   │   ├── Card.jsx              # Card component
│   │   ├── Modal.jsx             # Modal component
│   │   ├── Input.jsx             # Form input
│   │   └── Alert.jsx             # Alert/notification
│   │
│   ├── course/
│   │   ├── CourseCard.jsx        # Course listing card
│   │   ├── CourseHeader.jsx      # Course page header
│   │   ├── LessonList.jsx        # Lesson navigation
│   │   └── ProgressBar.jsx       # Progress indicator
│   │
│   └── index.js                   # Component exports map
│
├── layouts/                       # Page layout templates
│   ├── default.jsx               # Standard page layout
│   ├── full-width.jsx            # Full-width layout
│   ├── sidebar-left.jsx          # Left sidebar layout
│   └── course.jsx                # Course-specific layout
│
├── styles/                        # Theme stylesheets
│   ├── theme.css                 # Main theme styles
│   ├── variables.css             # CSS custom properties
│   ├── utilities.css             # Utility classes
│   └── components/               # Component-specific CSS
│       ├── header.css
│       ├── footer.css
│       ├── buttons.css
│       └── cards.css
│
├── assets/                        # Static assets
│   ├── images/
│   │   ├── logo-placeholder.svg
│   │   ├── hero-bg.jpg
│   │   └── patterns/
│   │       ├── pattern-1.svg
│   │       └── pattern-2.svg
│   │
│   ├── fonts/
│   │   ├── primary/
│   │   │   ├── font.woff2
│   │   │   └── font.woff
│   │   └── heading/
│   │       ├── font.woff2
│   │       └── font.woff
│   │
│   └── icons/
│       └── custom-icons.svg
│
├── patterns/                      # Puck content patterns
│   ├── hero-section.json
│   ├── feature-grid.json
│   └── testimonials.json
│
└── templates/                     # Page templates for Puck
    ├── home.json
    ├── about.json
    └── contact.json
```

### 3.3 Theme Manifest (theme.json)

```json
{
  "name": "Church Classic",
  "slug": "church-classic",
  "version": "1.0.0",
  "description": "A timeless, elegant theme for traditional churches featuring stained glass inspired colors and classic typography.",
  "author": {
    "name": "Church LMS Team",
    "email": "themes@churchlms.org",
    "url": "https://churchlms.org"
  },
  "license": "MIT",
  "screenshot": "screenshot.png",
  "thumbnailScreenshot": "screenshot-thumb.png",
  "tags": ["church", "traditional", "elegant", "classic", "ministry"],

  "compatibility": {
    "lmsVersion": ">=1.0.0",
    "react": ">=18.0.0",
    "node": ">=18.0.0"
  },

  "parent": null,

  "support": {
    "childThemes": true,
    "customizer": true,
    "puck": true,
    "darkMode": false,
    "rtl": false
  },

  "features": {
    "responsive": true,
    "accessibility": "WCAG-AA",
    "printStyles": true
  },

  "targetAudience": {
    "type": "traditional-church",
    "description": "Best suited for established churches with traditional worship styles"
  },

  "settings": {
    "colors": {
      "primary": {
        "type": "color",
        "default": "#6B2D5B",
        "label": "Primary Color",
        "description": "Main brand color (purple inspired by liturgical colors)"
      },
      "secondary": {
        "type": "color",
        "default": "#C4A052",
        "label": "Secondary Color",
        "description": "Accent color (gold for elegance)"
      },
      "accent": {
        "type": "color",
        "default": "#1E3A5F",
        "label": "Accent Color",
        "description": "Deep blue for contrast"
      },
      "background": {
        "type": "color",
        "default": "#FDF8F5",
        "label": "Background Color",
        "description": "Warm cream background"
      }
    },
    "typography": {
      "headingFont": {
        "type": "select",
        "default": "playfair",
        "options": [
          { "value": "playfair", "label": "Playfair Display (Elegant)" },
          { "value": "cormorant", "label": "Cormorant Garamond (Serif)" },
          { "value": "lora", "label": "Lora (Classic)" }
        ],
        "label": "Heading Font"
      },
      "bodyFont": {
        "type": "select",
        "default": "source-serif",
        "options": [
          { "value": "source-serif", "label": "Source Serif Pro" },
          { "value": "merriweather", "label": "Merriweather" },
          { "value": "crimson", "label": "Crimson Text" }
        ],
        "label": "Body Font"
      },
      "baseFontSize": {
        "type": "range",
        "default": 17,
        "min": 14,
        "max": 20,
        "step": 1,
        "unit": "px",
        "label": "Base Font Size"
      }
    },
    "layout": {
      "headerStyle": {
        "type": "select",
        "default": "centered",
        "options": [
          { "value": "centered", "label": "Centered Logo" },
          { "value": "left-aligned", "label": "Left Aligned" },
          { "value": "transparent", "label": "Transparent Overlay" }
        ],
        "label": "Header Style"
      },
      "containerWidth": {
        "type": "select",
        "default": "1140px",
        "options": [
          { "value": "960px", "label": "Narrow (960px)" },
          { "value": "1140px", "label": "Standard (1140px)" },
          { "value": "1320px", "label": "Wide (1320px)" }
        ],
        "label": "Content Width"
      }
    },
    "branding": {
      "logo": {
        "type": "image",
        "default": null,
        "label": "Church Logo",
        "description": "Recommended size: 200x60px"
      },
      "favicon": {
        "type": "image",
        "default": null,
        "label": "Favicon",
        "description": "32x32px icon for browser tabs"
      }
    }
  },

  "menus": {
    "primary": {
      "label": "Main Menu",
      "description": "Primary navigation in header"
    },
    "footer": {
      "label": "Footer Links",
      "description": "Quick links in footer"
    }
  },

  "widgets": {
    "sidebar-main": {
      "label": "Main Sidebar",
      "description": "Sidebar for course pages"
    },
    "footer-1": {
      "label": "Footer Column 1"
    },
    "footer-2": {
      "label": "Footer Column 2"
    },
    "footer-3": {
      "label": "Footer Column 3"
    }
  },

  "assets": {
    "styles": [
      "styles/theme.css",
      "styles/variables.css"
    ],
    "fonts": [
      "assets/fonts/primary/font.woff2",
      "assets/fonts/heading/font.woff2"
    ],
    "criticalImages": [
      "assets/images/logo-placeholder.svg"
    ]
  },

  "puck": {
    "componentOverrides": {
      "Hero": "components/puck/Hero.jsx",
      "Button": "components/common/Button.jsx"
    },
    "patterns": [
      "patterns/hero-section.json",
      "patterns/feature-grid.json"
    ]
  }
}
```

---

## 4. White-Label Configuration

### 4.1 How Themes Connect to White-Label Settings

The white-label system layers on top of themes:

```
Configuration Hierarchy:
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: User Customizations (via Theme Customizer)            │
│  - Custom colors, fonts, spacing                                │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: White-Label Branding (via Admin Settings)             │
│  - Logo, favicon, organization name                             │
│  - Footer text, contact info                                    │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: Theme Defaults (from theme.json)                      │
│  - Default colors, typography, layouts                          │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: Platform Defaults (hardcoded fallbacks)               │
│  - Ensures system works if all else fails                       │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Logo, Colors, Fonts Configuration Flow

**During Installation:**

```
Step 3 (Theme)          Step 4 (Branding)           Result
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│ Select      │        │ Upload Logo │        │ Theme +     │
│ Theme       │───────▶│ Set Colors  │───────▶│ Branding    │
│ (defaults)  │        │ Enter Name  │        │ = Final Look│
└─────────────┘        └─────────────┘        └─────────────┘
```

**Configuration Storage:**

```json
// White-label settings (stored in `settings` table)
{
  "organization": {
    "name": "Grace Fellowship Church",
    "tagline": "Growing Together in Faith",
    "description": "A community of believers...",
    "email": "info@gracefc.org",
    "phone": "(555) 123-4567",
    "address": "123 Church Street, Anytown, USA"
  },
  "branding": {
    "logo": "/uploads/branding/logo.png",
    "logoLight": "/uploads/branding/logo-light.png",
    "logoDark": "/uploads/branding/logo-dark.png",
    "favicon": "/uploads/branding/favicon.ico",
    "appleTouchIcon": "/uploads/branding/apple-touch-icon.png",
    "ogImage": "/uploads/branding/og-image.jpg"
  },
  "colors": {
    "override": true,
    "primary": "#6B2D5B",
    "secondary": "#C4A052"
  },
  "social": {
    "facebook": "https://facebook.com/gracefc",
    "youtube": "https://youtube.com/gracefc",
    "instagram": "https://instagram.com/gracefc"
  },
  "footer": {
    "text": "Grace Fellowship Church. All rights reserved.",
    "showPoweredBy": false
  },
  "legal": {
    "privacyPolicyUrl": "/privacy",
    "termsOfServiceUrl": "/terms"
  }
}
```

### 4.3 Brand Customization During Install vs Post-Install

| Setting | During Install | Post-Install | Notes |
|---------|----------------|--------------|-------|
| Logo | Yes | Yes | Can be changed anytime |
| Organization Name | Yes | Yes | Affects email, footer |
| Primary Color | Theme default | Yes | Full customizer access |
| Secondary Color | Theme default | Yes | Full customizer access |
| Fonts | Theme default | Yes | Full customizer access |
| Favicon | Yes | Yes | Can be changed anytime |
| Social Links | No (optional) | Yes | Skip during install |
| Footer Text | No (optional) | Yes | Skip during install |

### 4.4 Theme Customizer Integration

The Theme Customizer allows post-install fine-tuning:

```
┌─────────────────────────────────────────────────────────────────┐
│  Theme Customizer                                    [Save] [X] │
├─────────────────┬───────────────────────────────────────────────┤
│ Colors          │                                               │
│ ├─ Primary      │   ┌──────────────────────────────────────┐   │
│ ├─ Secondary    │   │                                      │   │
│ └─ Accent       │   │        LIVE PREVIEW IFRAME           │   │
│                 │   │                                      │   │
│ Typography      │   │     Shows changes in real-time      │   │
│ ├─ Heading Font │   │                                      │   │
│ ├─ Body Font    │   │                                      │   │
│ └─ Font Size    │   │                                      │   │
│                 │   │                                      │   │
│ Layout          │   └──────────────────────────────────────┘   │
│ ├─ Header Style │                                               │
│ └─ Width        │   [Desktop] [Tablet] [Mobile]                │
│                 │                                               │
│ Branding        │   [Reset to Theme Defaults]                  │
│ ├─ Logo         │   [Import Settings] [Export Settings]        │
│ └─ Favicon      │                                               │
└─────────────────┴───────────────────────────────────────────────┘
```

---

## 5. Theme Assets on Shared Hosting

### 5.1 Asset Storage Location

On cPanel shared hosting, theme assets are stored in the user's home directory:

```
/home/username/
├── public_html/                   # Web root (accessible via URL)
│   ├── index.html                # React app entry
│   ├── assets/                   # Built app assets
│   └── themes/                   # ◄── Theme assets served here
│       ├── default/
│       │   ├── screenshot.png
│       │   ├── styles/
│       │   └── assets/
│       └── church-classic/
│           ├── screenshot.png
│           ├── styles/
│           └── assets/
│
├── lms/                          # Application directory (outside web root)
│   ├── server/                   # Node.js backend
│   ├── themes/                   # ◄── Theme source files here
│   │   ├── default/
│   │   │   ├── theme.json
│   │   │   ├── components/      # React components (not directly served)
│   │   │   ├── styles/
│   │   │   └── assets/
│   │   └── church-classic/
│   │       └── ...
│   └── uploads/                  # User uploaded files
│       └── branding/
│           ├── logo.png
│           └── favicon.ico
```

### 5.2 Why This Structure?

| Location | Content | Reason |
|----------|---------|--------|
| `~/public_html/themes/` | CSS, images, fonts | Must be web-accessible for browser |
| `~/lms/themes/` | React components, theme.json | Keep source separate from served files |
| `~/lms/uploads/` | User uploads | Separate from theme files |

### 5.3 Asset Serving Configuration for cPanel

**.htaccess for Theme Assets:**

```apache
# /public_html/themes/.htaccess

# Enable CORS for fonts
<FilesMatch "\.(ttf|otf|eot|woff|woff2)$">
    Header set Access-Control-Allow-Origin "*"
</FilesMatch>

# Cache static assets
<FilesMatch "\.(css|js|png|jpg|jpeg|gif|svg|woff|woff2)$">
    Header set Cache-Control "max-age=31536000, public"
</FilesMatch>

# Prevent directory listing
Options -Indexes

# Block access to source files accidentally placed here
<FilesMatch "\.(jsx|json|md)$">
    Order Allow,Deny
    Deny from all
</FilesMatch>
```

### 5.4 CDN Considerations for Budget Hosting

For churches on shared hosting, CDN integration is optional but recommended for larger deployments:

**Built-in CDN Support:**

```javascript
// Theme asset URL helper
function getAssetUrl(assetPath, theme) {
  const cdnUrl = process.env.CDN_URL;
  const baseUrl = process.env.BASE_URL || '';

  if (cdnUrl) {
    // Use CDN for production
    return `${cdnUrl}/themes/${theme}/${assetPath}`;
  }

  // Fall back to local serving
  return `${baseUrl}/themes/${theme}/${assetPath}`;
}
```

**Free/Low-Cost CDN Options:**

| Service | Free Tier | Notes |
|---------|-----------|-------|
| Cloudflare | Unlimited | Recommended - easy DNS setup |
| BunnyCDN | $0.01/GB | Very affordable for churches |
| CloudFront | 1TB/month | If using AWS |

**Configuration in Admin:**

```
Admin > Settings > Performance
┌─────────────────────────────────────────────────────────────────┐
│ CDN Configuration                                               │
├─────────────────────────────────────────────────────────────────┤
│ CDN URL: [                                             ]        │
│ (Leave empty to serve assets directly)                         │
│                                                                 │
│ Example: https://cdn.gracefc.org                                │
│                                                                 │
│ [Test CDN Connection]                                           │
└─────────────────────────────────────────────────────────────────┘
```

### 5.5 Image Optimization for Slow Connections

Since many churches have limited hosting resources:

**Automatic Image Optimization:**

```javascript
// Server middleware for image optimization
const imageOptimization = {
  // Maximum dimensions for theme images
  maxWidth: 1920,
  maxHeight: 1080,

  // Quality settings
  jpegQuality: 85,
  pngCompression: 9,

  // WebP generation
  generateWebp: true,

  // Lazy loading
  addLazyAttribute: true
};
```

**Theme Screenshot Requirements:**

| Image | Dimensions | Format | Max Size |
|-------|------------|--------|----------|
| screenshot.png | 1200x900 | PNG/WebP | 500KB |
| screenshot-thumb.png | 400x300 | PNG/WebP | 100KB |
| Hero images | 1920x1080 max | JPEG/WebP | 300KB |
| Pattern images | Any | SVG preferred | 50KB |

---

## 6. Post-Install Theme Management

### 6.1 Admin Panel Theme Browser

```
┌─────────────────────────────────────────────────────────────────┐
│ Themes                                    [Upload Theme] [Refresh]│
├─────────────────────────────────────────────────────────────────┤
│ Active Theme                                                     │
│ ┌───────────────────────────────────────────────────────────┐   │
│ │ [Screenshot]  Church Classic v1.0.0                       │   │
│ │               A timeless, elegant theme...                │   │
│ │               [Customize] [Theme Details]                 │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                  │
│ Installed Themes (3)                                            │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│ │ [Screenshot]│ │ [Screenshot]│ │ [Screenshot]│               │
│ │ Default     │ │ Modern Min. │ │ Youth Con.  │               │
│ │ [Activate]  │ │ [Activate]  │ │ [Activate]  │               │
│ └─────────────┘ └─────────────┘ └─────────────┘               │
│                                                                  │
│ Available for Installation (Future)                             │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ Theme marketplace coming soon...                         │   │
│ │ [Browse Marketplace]                                     │   │
│ └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Theme Upload/Installation Flow

**Step-by-Step Upload Process:**

```
1. User clicks [Upload Theme]
            │
            ▼
2. File picker opens (accepts .zip)
            │
            ▼
3. ZIP uploaded to server
            │
            ▼
4. Server validates theme structure
   ├── Has theme.json?
   ├── Valid manifest schema?
   ├── Has screenshot.png?
   ├── Security scan passed?
   │
   ├── Invalid ──▶ Show error, suggest fixes
   │
   └── Valid ────▶ Continue
            │
            ▼
5. Theme extracted to ~/lms/themes/{slug}/
            │
            ▼
6. Database record created
            │
            ▼
7. Theme assets copied to ~/public_html/themes/{slug}/
            │
            ▼
8. Success message: "Theme installed! [Activate Now] [Later]"
```

### 6.3 Theme Marketplace Integration (Future)

**Planned Marketplace Features:**

```javascript
// Marketplace API (future implementation)
const marketplace = {
  baseUrl: 'https://themes.churchlms.org/api/v1',

  endpoints: {
    browse: '/themes',
    search: '/themes/search',
    details: '/themes/:slug',
    download: '/themes/:slug/download',
    checkUpdates: '/themes/check-updates'
  },

  // License validation required for premium themes
  requiresLicense: true
};
```

**Marketplace UI Preview:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Theme Marketplace                              [Search themes...] │
├─────────────────────────────────────────────────────────────────┤
│ Categories: [All] [Church] [Ministry] [Youth] [Education]       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│ │             │ │             │ │             │ │             ││
│ │ [Preview]   │ │ [Preview]   │ │ [Preview]   │ │ [Preview]   ││
│ │             │ │             │ │             │ │             ││
│ │ Theme Name  │ │ Theme Name  │ │ Theme Name  │ │ Theme Name  ││
│ │ ★★★★☆ (24) │ │ ★★★★★ (89) │ │ ★★★☆☆ (12) │ │ ★★★★☆ (45) ││
│ │ Free        │ │ $29         │ │ Free        │ │ $49         ││
│ │ [Install]   │ │ [Purchase]  │ │ [Install]   │ │ [Purchase]  ││
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
│                                                                  │
│                      [Load More Themes...]                       │
└─────────────────────────────────────────────────────────────────┘
```

### 6.4 Theme Updates and Versioning

**Update Check Process:**

```javascript
// Check for theme updates
async function checkThemeUpdates() {
  const installedThemes = await Theme.findAll({
    where: { installation_source: ['marketplace', 'bundled'] }
  });

  const updateChecks = installedThemes.map(async (theme) => {
    const latestVersion = await marketplace.getLatestVersion(theme.slug);

    if (semver.gt(latestVersion, theme.version)) {
      return {
        slug: theme.slug,
        currentVersion: theme.version,
        latestVersion,
        updateAvailable: true
      };
    }

    return { slug: theme.slug, updateAvailable: false };
  });

  return Promise.all(updateChecks);
}
```

**Version Compatibility Matrix:**

| Theme Version | LMS Version | Compatible |
|---------------|-------------|------------|
| 1.x | 1.x | Yes |
| 2.x | 1.x | With migration |
| 1.x | 2.x | Deprecated warnings |

---

## 7. Starter Theme Specifications

### 7.1 Default Theme

**Name:** Default
**Slug:** `default`
**File Size:** ~150KB
**Target Audience:** Universal fallback, minimalist preference

```json
{
  "name": "Default",
  "slug": "default",
  "version": "1.0.0",
  "description": "A clean, minimal theme that works for any organization. Simple, fast, and accessible.",
  "targetAudience": {
    "type": "universal",
    "description": "Suitable for any organization; serves as the fallback theme"
  },
  "colorPalette": {
    "primary": "#4F46E5",
    "secondary": "#10B981",
    "accent": "#F59E0B",
    "background": "#FFFFFF",
    "text": "#1F2937",
    "muted": "#6B7280"
  },
  "typography": {
    "headingFont": "Inter",
    "bodyFont": "Inter",
    "style": "Modern sans-serif"
  },
  "characteristics": [
    "Neutral, professional appearance",
    "High contrast for accessibility",
    "Minimal decorative elements",
    "Fast loading times",
    "WCAG AA compliant"
  ],
  "componentOverrides": [
    "Header (simple)",
    "Footer (minimal)",
    "Button (standard)"
  ],
  "screenshots": {
    "main": "screenshot.png",
    "thumbnail": "screenshot-thumb.png"
  }
}
```

### 7.2 Church Classic Theme

**Name:** Church Classic
**Slug:** `church-classic`
**File Size:** ~280KB
**Target Audience:** Traditional churches, established congregations

```json
{
  "name": "Church Classic",
  "slug": "church-classic",
  "version": "1.0.0",
  "description": "A timeless, elegant theme inspired by traditional church aesthetics. Features warm colors and classic typography.",
  "targetAudience": {
    "type": "traditional-church",
    "description": "Best for established churches with traditional worship styles, liturgical churches, and denominations with formal traditions"
  },
  "colorPalette": {
    "primary": "#6B2D5B",
    "secondary": "#C4A052",
    "accent": "#1E3A5F",
    "background": "#FDF8F5",
    "text": "#2D2926",
    "muted": "#6B5B5A"
  },
  "typography": {
    "headingFont": "Playfair Display",
    "bodyFont": "Source Serif Pro",
    "style": "Classic serif fonts for elegance"
  },
  "characteristics": [
    "Warm, inviting color palette",
    "Elegant serif typography",
    "Subtle decorative elements",
    "Stained glass-inspired accents",
    "Traditional header with centered logo"
  ],
  "componentOverrides": [
    "Header (centered logo style)",
    "Footer (4-column with cross motif)",
    "Button (subtle rounded)",
    "Card (with subtle border)",
    "Hero (with overlay pattern)"
  ],
  "screenshots": {
    "main": "screenshot.png",
    "thumbnail": "screenshot-thumb.png",
    "homepage": "screenshots/homepage.png",
    "coursePage": "screenshots/course-page.png"
  }
}
```

### 7.3 Modern Ministry Theme

**Name:** Modern Ministry
**Slug:** `modern-ministry`
**File Size:** ~320KB
**Target Audience:** Contemporary churches, multi-site churches

```json
{
  "name": "Modern Ministry",
  "slug": "modern-ministry",
  "version": "1.0.0",
  "description": "A contemporary, bold theme for forward-thinking churches. Clean lines, vibrant colors, and modern typography.",
  "targetAudience": {
    "type": "contemporary-church",
    "description": "Ideal for modern churches, contemporary worship communities, church plants, and multi-site ministries"
  },
  "colorPalette": {
    "primary": "#0891B2",
    "secondary": "#7C3AED",
    "accent": "#F59E0B",
    "background": "#FFFFFF",
    "text": "#0F172A",
    "muted": "#64748B"
  },
  "typography": {
    "headingFont": "Poppins",
    "bodyFont": "Inter",
    "style": "Bold, geometric sans-serif"
  },
  "characteristics": [
    "Bold, vibrant colors",
    "Clean geometric layouts",
    "Large hero sections",
    "Card-based content display",
    "Animated transitions",
    "Mobile-first design"
  ],
  "componentOverrides": [
    "Header (sticky with blur effect)",
    "Footer (modern minimal)",
    "Button (bold with hover animations)",
    "Card (floating with shadow)",
    "Hero (full-width video support)",
    "Navigation (mega-menu style)"
  ],
  "screenshots": {
    "main": "screenshot.png",
    "thumbnail": "screenshot-thumb.png",
    "homepage": "screenshots/homepage.png",
    "coursePage": "screenshots/course-page.png",
    "mobile": "screenshots/mobile.png"
  }
}
```

### 7.4 Youth Connect Theme

**Name:** Youth Connect
**Slug:** `youth-connect`
**File Size:** ~350KB
**Target Audience:** Youth ministries, student groups, young adult communities

```json
{
  "name": "Youth Connect",
  "slug": "youth-connect",
  "version": "1.0.0",
  "description": "An energetic, engaging theme designed for youth and young adult ministries. Features bold colors, dynamic elements, and social-media-inspired layouts.",
  "targetAudience": {
    "type": "youth-ministry",
    "description": "Perfect for youth groups, student ministries, campus organizations, and young adult communities"
  },
  "colorPalette": {
    "primary": "#EC4899",
    "secondary": "#8B5CF6",
    "accent": "#10B981",
    "background": "#0F0F0F",
    "text": "#FFFFFF",
    "muted": "#9CA3AF"
  },
  "typography": {
    "headingFont": "Montserrat",
    "bodyFont": "Nunito",
    "style": "Energetic, approachable fonts"
  },
  "characteristics": [
    "Dark mode default",
    "Gradient accents",
    "Social media-style cards",
    "Emoji-friendly design",
    "Gamification elements",
    "Achievement badges",
    "Instagram-style image grids",
    "TikTok-inspired short content areas"
  ],
  "componentOverrides": [
    "Header (transparent with gradient)",
    "Footer (social-media focused)",
    "Button (gradient with glow effects)",
    "Card (glassmorphism style)",
    "Hero (video background support)",
    "Progress (gamified with badges)",
    "Avatar (ring indicators)",
    "Feed (social media timeline)"
  ],
  "screenshots": {
    "main": "screenshot.png",
    "thumbnail": "screenshot-thumb.png",
    "homepage": "screenshots/homepage.png",
    "coursePage": "screenshots/course-page.png",
    "mobile": "screenshots/mobile.png",
    "gamification": "screenshots/achievements.png"
  }
}
```

### 7.5 Screenshot Requirements for All Themes

| Image | Dimensions | Format | Max Size | Purpose |
|-------|------------|--------|----------|---------|
| `screenshot.png` | 1200x900 | PNG | 500KB | Full preview in browser |
| `screenshot-thumb.png` | 400x300 | PNG | 100KB | Grid display thumbnail |
| `screenshots/homepage.png` | 1920x1080 | PNG | 800KB | Homepage showcase |
| `screenshots/course-page.png` | 1920x1080 | PNG | 800KB | Course page showcase |
| `screenshots/mobile.png` | 375x812 | PNG | 300KB | Mobile view showcase |

---

## 8. Database Migration Scripts

### 8.1 PostgreSQL Theme Tables Migration

```sql
-- Migration: 20260111_001_create_theme_tables_postgresql.sql
-- Database: PostgreSQL 13+
-- Description: Creates theme system tables for Church LMS

BEGIN;

-- Enable UUID extension if not exists
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Main themes table
CREATE TABLE IF NOT EXISTS themes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    description TEXT,
    author_name VARCHAR(255),
    author_email VARCHAR(255),
    author_url VARCHAR(500),

    -- Status with CHECK constraint
    status VARCHAR(20) NOT NULL DEFAULT 'inactive'
        CHECK (status IN ('active', 'inactive', 'broken')),

    -- Timestamps with timezone
    installed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    activated_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- File paths
    file_path VARCHAR(500) NOT NULL,

    -- Theme manifest (JSONB for efficient querying)
    manifest JSONB NOT NULL DEFAULT '{}',

    -- Metadata
    screenshot_url VARCHAR(500),
    download_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.00,

    -- Constraints
    CONSTRAINT unique_theme_slug UNIQUE (slug)
);

-- Indexes for themes
CREATE INDEX IF NOT EXISTS idx_themes_status ON themes(status);
CREATE INDEX IF NOT EXISTS idx_themes_slug ON themes(slug);
CREATE INDEX IF NOT EXISTS idx_themes_created ON themes(created_at);

-- Theme settings table
CREATE TABLE IF NOT EXISTS theme_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    theme_id UUID NOT NULL REFERENCES themes(id) ON DELETE CASCADE,
    organization_id UUID,

    -- Settings JSON
    settings JSONB NOT NULL DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint for org+theme
    CONSTRAINT unique_theme_org_settings UNIQUE (theme_id, organization_id)
);

-- Indexes for theme_settings
CREATE INDEX IF NOT EXISTS idx_theme_settings_theme ON theme_settings(theme_id);
CREATE INDEX IF NOT EXISTS idx_theme_settings_org ON theme_settings(organization_id);

-- Theme installations tracking
CREATE TABLE IF NOT EXISTS theme_installations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    theme_id UUID NOT NULL REFERENCES themes(id) ON DELETE CASCADE,
    installed_by UUID,
    installation_source VARCHAR(50) DEFAULT 'upload'
        CHECK (installation_source IN ('upload', 'marketplace', 'bundled', 'git')),

    -- Metadata
    installation_log TEXT,
    previous_version VARCHAR(20),

    -- Timestamp
    installed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for installations
CREATE INDEX IF NOT EXISTS idx_theme_installations_theme ON theme_installations(theme_id);
CREATE INDEX IF NOT EXISTS idx_theme_installations_date ON theme_installations(installed_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_themes_updated_at
    BEFORE UPDATE ON themes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_theme_settings_updated_at
    BEFORE UPDATE ON theme_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Ensure only one active theme at a time (function)
CREATE OR REPLACE FUNCTION enforce_single_active_theme()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'active' THEN
        UPDATE themes
        SET status = 'inactive', updated_at = CURRENT_TIMESTAMP
        WHERE id != NEW.id AND status = 'active';
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for single active theme
CREATE TRIGGER enforce_single_active_theme_trigger
    BEFORE INSERT OR UPDATE ON themes
    FOR EACH ROW
    EXECUTE FUNCTION enforce_single_active_theme();

-- Insert default theme
INSERT INTO themes (slug, name, version, description, status, file_path, manifest)
VALUES (
    'default',
    'Default',
    '1.0.0',
    'A clean, minimal theme that works for any organization.',
    'active',
    '/themes/default',
    '{
        "name": "Default",
        "slug": "default",
        "version": "1.0.0",
        "settings": {
            "colors": {
                "primary": {"type": "color", "default": "#4F46E5"},
                "secondary": {"type": "color", "default": "#10B981"}
            }
        }
    }'::jsonb
) ON CONFLICT (slug) DO NOTHING;

COMMIT;
```

### 8.2 MySQL Theme Tables Migration

```sql
-- Migration: 20260111_001_create_theme_tables_mysql.sql
-- Database: MySQL 5.7+ / 8.0+
-- Description: Creates theme system tables for Church LMS

-- Main themes table
CREATE TABLE IF NOT EXISTS themes (
    id CHAR(36) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    description TEXT,
    author_name VARCHAR(255),
    author_email VARCHAR(255),
    author_url VARCHAR(500),

    -- Status as ENUM
    status ENUM('active', 'inactive', 'broken') NOT NULL DEFAULT 'inactive',

    -- Timestamps
    installed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    activated_at DATETIME NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- File paths
    file_path VARCHAR(500) NOT NULL,

    -- Theme manifest (JSON type)
    manifest JSON NOT NULL,

    -- Metadata
    screenshot_url VARCHAR(500),
    download_count INT DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.00,

    -- Primary key
    PRIMARY KEY (id),

    -- Unique constraint
    UNIQUE KEY unique_theme_slug (slug),

    -- Indexes
    INDEX idx_themes_status (status),
    INDEX idx_themes_slug (slug),
    INDEX idx_themes_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Theme settings table
CREATE TABLE IF NOT EXISTS theme_settings (
    id CHAR(36) NOT NULL,
    theme_id CHAR(36) NOT NULL,
    organization_id CHAR(36) NULL,

    -- Settings JSON
    settings JSON NOT NULL,

    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Primary key
    PRIMARY KEY (id),

    -- Foreign key
    FOREIGN KEY (theme_id) REFERENCES themes(id) ON DELETE CASCADE,

    -- Unique constraint
    UNIQUE KEY unique_theme_org_settings (theme_id, organization_id),

    -- Indexes
    INDEX idx_theme_settings_theme (theme_id),
    INDEX idx_theme_settings_org (organization_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Theme installations tracking
CREATE TABLE IF NOT EXISTS theme_installations (
    id CHAR(36) NOT NULL,
    theme_id CHAR(36) NOT NULL,
    installed_by CHAR(36) NULL,
    installation_source ENUM('upload', 'marketplace', 'bundled', 'git') DEFAULT 'upload',

    -- Metadata
    installation_log TEXT,
    previous_version VARCHAR(20),

    -- Timestamp
    installed_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Primary key
    PRIMARY KEY (id),

    -- Foreign key
    FOREIGN KEY (theme_id) REFERENCES themes(id) ON DELETE CASCADE,

    -- Indexes
    INDEX idx_theme_installations_theme (theme_id),
    INDEX idx_theme_installations_date (installed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Trigger to enforce single active theme (MySQL version)
DELIMITER //

CREATE TRIGGER enforce_single_active_theme_insert
BEFORE INSERT ON themes
FOR EACH ROW
BEGIN
    IF NEW.status = 'active' THEN
        UPDATE themes SET status = 'inactive' WHERE status = 'active';
    END IF;
END//

CREATE TRIGGER enforce_single_active_theme_update
BEFORE UPDATE ON themes
FOR EACH ROW
BEGIN
    IF NEW.status = 'active' AND OLD.status != 'active' THEN
        UPDATE themes SET status = 'inactive' WHERE id != NEW.id AND status = 'active';
    END IF;
END//

DELIMITER ;

-- Insert default theme (MySQL)
INSERT IGNORE INTO themes (id, slug, name, version, description, status, file_path, manifest)
VALUES (
    UUID(),
    'default',
    'Default',
    '1.0.0',
    'A clean, minimal theme that works for any organization.',
    'active',
    '/themes/default',
    JSON_OBJECT(
        'name', 'Default',
        'slug', 'default',
        'version', '1.0.0',
        'settings', JSON_OBJECT(
            'colors', JSON_OBJECT(
                'primary', JSON_OBJECT('type', 'color', 'default', '#4F46E5'),
                'secondary', JSON_OBJECT('type', 'color', 'default', '#10B981')
            )
        )
    )
);
```

### 8.3 Theme Settings Table Structure

```sql
-- Common settings table structure (works for both databases)

-- Theme settings stores customizations per organization
-- Example data:

/*
+--------------------------------------+--------------------------------------+--------------------------------------+
| id                                   | theme_id                             | organization_id                      |
+--------------------------------------+--------------------------------------+--------------------------------------+
| a1b2c3d4-...                         | default-theme-uuid                   | NULL (global settings)               |
| e5f6g7h8-...                         | church-classic-uuid                  | org-123-uuid                         |
+--------------------------------------+--------------------------------------+--------------------------------------+

settings JSON example:
{
    "colors": {
        "primary": "#6B2D5B",
        "secondary": "#C4A052"
    },
    "typography": {
        "headingFont": "playfair",
        "bodyFont": "source-serif",
        "baseFontSize": 17
    },
    "layout": {
        "headerStyle": "centered",
        "containerWidth": "1140px"
    },
    "branding": {
        "logo": "/uploads/branding/logo.png",
        "favicon": "/uploads/branding/favicon.ico"
    }
}
*/
```

---

## 9. API Endpoints for Theme Management

### 9.1 Theme List Endpoint

```
GET /api/themes
```

**Description:** Returns all available themes (installed and bundled).

**Response:**

```json
{
  "success": true,
  "themes": [
    {
      "id": "uuid-here",
      "slug": "default",
      "name": "Default",
      "version": "1.0.0",
      "description": "A clean, minimal theme...",
      "author": {
        "name": "Church LMS Team",
        "email": "themes@churchlms.org"
      },
      "status": "active",
      "screenshot": "/themes/default/screenshot.png",
      "thumbnail": "/themes/default/screenshot-thumb.png",
      "tags": ["minimal", "universal"],
      "installedAt": "2026-01-11T10:00:00Z",
      "activatedAt": "2026-01-11T10:05:00Z"
    },
    {
      "id": "uuid-here-2",
      "slug": "church-classic",
      "name": "Church Classic",
      "version": "1.0.0",
      "description": "A timeless, elegant theme...",
      "status": "inactive",
      "screenshot": "/themes/church-classic/screenshot.png",
      "tags": ["traditional", "church", "elegant"]
    }
  ],
  "total": 4
}
```

### 9.2 Install Theme Endpoint

```
POST /api/themes/install
Content-Type: multipart/form-data
```

**Request:**
- `file`: ZIP file containing theme

**Response (Success):**

```json
{
  "success": true,
  "message": "Theme installed successfully",
  "theme": {
    "id": "new-uuid",
    "slug": "custom-theme",
    "name": "Custom Theme",
    "version": "1.0.0",
    "status": "inactive"
  }
}
```

**Response (Error):**

```json
{
  "success": false,
  "error": "INVALID_THEME_STRUCTURE",
  "message": "Theme is missing required file: theme.json",
  "details": {
    "missingFiles": ["theme.json"],
    "suggestions": [
      "Ensure your ZIP file contains a theme.json at the root level",
      "Check the theme documentation for required files"
    ]
  }
}
```

### 9.3 Activate Theme Endpoint

```
POST /api/themes/activate
Content-Type: application/json
```

**Request:**

```json
{
  "themeId": "uuid-of-theme-to-activate"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Theme activated successfully",
  "previousTheme": {
    "id": "old-theme-uuid",
    "slug": "default"
  },
  "activeTheme": {
    "id": "new-theme-uuid",
    "slug": "church-classic",
    "name": "Church Classic"
  }
}
```

### 9.4 Get Current Theme Endpoint

```
GET /api/themes/active
```

**Response:**

```json
{
  "success": true,
  "theme": {
    "id": "active-theme-uuid",
    "slug": "church-classic",
    "name": "Church Classic",
    "version": "1.0.0",
    "settings": {
      "colors": {
        "primary": "#6B2D5B",
        "secondary": "#C4A052"
      },
      "typography": {
        "headingFont": "playfair",
        "bodyFont": "source-serif"
      }
    },
    "assets": {
      "stylesheet": "/themes/church-classic/styles/theme.css",
      "variables": "/themes/church-classic/styles/variables.css"
    }
  }
}
```

### 9.5 Save Theme Customizations Endpoint

```
PUT /api/themes/customize
Content-Type: application/json
```

**Request:**

```json
{
  "themeId": "theme-uuid",
  "settings": {
    "colors": {
      "primary": "#7C3AED",
      "secondary": "#10B981"
    },
    "typography": {
      "baseFontSize": 18
    }
  }
}
```

**Response:**

```json
{
  "success": true,
  "message": "Theme customizations saved",
  "settings": {
    "colors": {
      "primary": "#7C3AED",
      "secondary": "#10B981"
    },
    "typography": {
      "headingFont": "playfair",
      "bodyFont": "source-serif",
      "baseFontSize": 18
    }
  }
}
```

### 9.6 Full API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/themes` | List all available themes |
| GET | `/api/themes/:id` | Get theme details by ID |
| GET | `/api/themes/active` | Get currently active theme |
| GET | `/api/themes/:id/settings` | Get theme settings |
| POST | `/api/themes/install` | Upload and install theme |
| POST | `/api/themes/activate` | Activate a theme |
| PUT | `/api/themes/customize` | Save theme customizations |
| PUT | `/api/themes/:id` | Update theme metadata |
| DELETE | `/api/themes/:id` | Uninstall theme |
| POST | `/api/themes/preview` | Generate preview URL |
| GET | `/api/themes/:id/export` | Export theme settings |
| POST | `/api/themes/import` | Import theme settings |
| POST | `/api/themes/reset` | Reset to theme defaults |

---

## 10. Error Handling

### 10.1 Theme Loading Failures During Install

**Scenario Tree:**

```
Theme Selection Step
        │
        ▼
    Load Themes
        │
   ┌────┴────┐
   │         │
 Success   Failure
   │         │
   ▼         ▼
 Show      Check Cause
 Themes         │
           ┌────┼────┐
           │    │    │
        Missing  Corrupt  Permission
        Files    JSON     Error
           │         │         │
           ▼         ▼         ▼
        Use      Remove    Fix Perms
       Default   & Use     & Retry
                Default
```

**Error Handling Code:**

```javascript
async function loadAvailableThemes() {
  const themes = [];
  const errors = [];

  try {
    const themeDirs = await fs.readdir(THEMES_DIR);

    for (const dir of themeDirs) {
      try {
        const themePath = path.join(THEMES_DIR, dir);
        const manifestPath = path.join(themePath, 'theme.json');

        // Check manifest exists
        if (!await fs.pathExists(manifestPath)) {
          errors.push({
            theme: dir,
            error: 'MISSING_MANIFEST',
            message: `Theme "${dir}" is missing theme.json`
          });
          continue;
        }

        // Parse manifest
        const manifest = await fs.readJson(manifestPath);

        // Validate required fields
        const validation = validateManifest(manifest);
        if (!validation.valid) {
          errors.push({
            theme: dir,
            error: 'INVALID_MANIFEST',
            message: validation.message
          });
          continue;
        }

        // Check screenshot exists
        const screenshotPath = path.join(themePath, 'screenshot.png');
        const hasScreenshot = await fs.pathExists(screenshotPath);

        themes.push({
          ...manifest,
          path: themePath,
          hasScreenshot,
          screenshot: hasScreenshot
            ? `/themes/${dir}/screenshot.png`
            : '/assets/images/theme-placeholder.png'
        });

      } catch (themeError) {
        errors.push({
          theme: dir,
          error: 'LOAD_ERROR',
          message: themeError.message
        });
      }
    }

  } catch (dirError) {
    // Cannot read themes directory at all
    return {
      success: false,
      themes: [],
      fallbackToDefault: true,
      error: {
        type: 'THEMES_DIR_ERROR',
        message: 'Cannot access themes directory',
        originalError: dirError.message
      }
    };
  }

  // Ensure default theme is always available
  const hasDefault = themes.some(t => t.slug === 'default');
  if (!hasDefault) {
    // Load embedded default theme
    themes.unshift(getEmbeddedDefaultTheme());
  }

  return {
    success: true,
    themes,
    errors: errors.length > 0 ? errors : null
  };
}
```

### 10.2 Fallback to Default Theme Mechanism

```javascript
class ThemeFallbackManager {
  constructor() {
    this.defaultTheme = {
      slug: 'default',
      name: 'Default',
      version: '1.0.0',
      settings: DEFAULT_THEME_SETTINGS
    };
  }

  async loadTheme(themeSlug) {
    try {
      const theme = await ThemeLoader.load(themeSlug);
      return theme;
    } catch (error) {
      console.error(`Failed to load theme "${themeSlug}":`, error);

      // Log the failure
      await this.logThemeFailure(themeSlug, error);

      // Mark theme as broken in database
      await Theme.update(
        { status: 'broken' },
        { where: { slug: themeSlug } }
      );

      // Activate default theme
      await Theme.update(
        { status: 'active' },
        { where: { slug: 'default' } }
      );

      // Return default theme
      return this.defaultTheme;
    }
  }

  async logThemeFailure(themeSlug, error) {
    await ThemeInstallation.create({
      theme_id: await Theme.findOne({ where: { slug: themeSlug } }).id,
      installation_source: 'error',
      installation_log: JSON.stringify({
        type: 'LOAD_FAILURE',
        message: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString()
      })
    });
  }
}
```

### 10.3 Theme Validation During Upload

```javascript
async function validateThemeUpload(zipFile) {
  const validationResult = {
    valid: true,
    errors: [],
    warnings: []
  };

  const tempDir = path.join(os.tmpdir(), `theme-${Date.now()}`);

  try {
    // Extract ZIP
    await extract(zipFile.path, { dir: tempDir });

    // Check for theme.json
    const manifestPath = path.join(tempDir, 'theme.json');
    if (!await fs.pathExists(manifestPath)) {
      validationResult.valid = false;
      validationResult.errors.push({
        code: 'MISSING_MANIFEST',
        message: 'theme.json file is required',
        suggestion: 'Create a theme.json file with name, slug, and version fields'
      });
      return validationResult;
    }

    // Parse and validate manifest
    let manifest;
    try {
      manifest = await fs.readJson(manifestPath);
    } catch (jsonError) {
      validationResult.valid = false;
      validationResult.errors.push({
        code: 'INVALID_JSON',
        message: 'theme.json contains invalid JSON',
        suggestion: 'Check for syntax errors in theme.json'
      });
      return validationResult;
    }

    // Required fields
    const requiredFields = ['name', 'slug', 'version'];
    for (const field of requiredFields) {
      if (!manifest[field]) {
        validationResult.valid = false;
        validationResult.errors.push({
          code: 'MISSING_FIELD',
          message: `Required field "${field}" is missing from theme.json`,
          suggestion: `Add "${field}" to your theme.json`
        });
      }
    }

    // Slug format validation
    if (manifest.slug && !/^[a-z0-9-]+$/.test(manifest.slug)) {
      validationResult.valid = false;
      validationResult.errors.push({
        code: 'INVALID_SLUG',
        message: 'Slug must contain only lowercase letters, numbers, and hyphens',
        suggestion: `Use slug like "my-theme" instead of "${manifest.slug}"`
      });
    }

    // Check for duplicate slug
    const existing = await Theme.findOne({ where: { slug: manifest.slug } });
    if (existing) {
      validationResult.valid = false;
      validationResult.errors.push({
        code: 'DUPLICATE_SLUG',
        message: `A theme with slug "${manifest.slug}" is already installed`,
        suggestion: 'Uninstall the existing theme first or use a different slug'
      });
    }

    // Check for screenshot
    const screenshotPath = path.join(tempDir, 'screenshot.png');
    if (!await fs.pathExists(screenshotPath)) {
      validationResult.warnings.push({
        code: 'MISSING_SCREENSHOT',
        message: 'Theme is missing screenshot.png',
        suggestion: 'Add a 1200x900px screenshot.png for the theme browser'
      });
    }

    // Security: Check for dangerous files
    const dangerousPatterns = [
      /\.php$/i,
      /\.exe$/i,
      /\.sh$/i,
      /\.bat$/i
    ];

    const allFiles = await glob('**/*', { cwd: tempDir, nodir: true });
    for (const file of allFiles) {
      for (const pattern of dangerousPatterns) {
        if (pattern.test(file)) {
          validationResult.valid = false;
          validationResult.errors.push({
            code: 'DANGEROUS_FILE',
            message: `Potentially dangerous file detected: ${file}`,
            suggestion: 'Remove server-side scripts from your theme'
          });
        }
      }
    }

    return validationResult;

  } finally {
    // Cleanup temp directory
    await fs.remove(tempDir);
  }
}
```

### 10.4 Corrupted Theme Recovery

```javascript
async function recoverCorruptedTheme(themeSlug) {
  const recovery = {
    success: false,
    actions: [],
    theme: null
  };

  try {
    // Step 1: Check if theme files exist
    const themePath = path.join(THEMES_DIR, themeSlug);
    const exists = await fs.pathExists(themePath);

    if (!exists) {
      recovery.actions.push('Theme directory not found');

      // Check if it's a bundled theme we can restore
      if (BUNDLED_THEMES.includes(themeSlug)) {
        await restoreBundledTheme(themeSlug);
        recovery.actions.push(`Restored bundled theme: ${themeSlug}`);
        recovery.success = true;
      } else {
        // Remove from database
        await Theme.destroy({ where: { slug: themeSlug } });
        recovery.actions.push('Removed orphaned database entry');

        // Activate default theme
        await activateDefaultTheme();
        recovery.actions.push('Activated default theme');
      }

      return recovery;
    }

    // Step 2: Validate theme.json
    const manifestPath = path.join(themePath, 'theme.json');
    try {
      const manifest = await fs.readJson(manifestPath);

      // Update database record
      await Theme.update(
        {
          status: 'inactive',
          manifest: manifest
        },
        { where: { slug: themeSlug } }
      );

      recovery.actions.push('Repaired database record from theme.json');
      recovery.success = true;

    } catch (jsonError) {
      // theme.json is corrupted
      if (BUNDLED_THEMES.includes(themeSlug)) {
        // Restore from bundled
        await fs.copy(
          path.join(BUNDLED_SOURCE, themeSlug, 'theme.json'),
          manifestPath
        );
        recovery.actions.push('Restored theme.json from bundled source');
        recovery.success = true;
      } else {
        // Cannot repair - remove theme
        await fs.remove(themePath);
        await Theme.destroy({ where: { slug: themeSlug } });
        recovery.actions.push('Theme was unrepairable and has been removed');

        // Activate default
        await activateDefaultTheme();
        recovery.actions.push('Activated default theme');
      }
    }

    return recovery;

  } catch (error) {
    recovery.error = error.message;
    recovery.actions.push(`Recovery failed: ${error.message}`);
    return recovery;
  }
}
```

---

## 11. Performance Considerations

### 11.1 Theme Asset Caching Strategy

**Browser Caching Headers:**

```javascript
// Express middleware for theme assets
app.use('/themes', express.static(THEMES_PUBLIC_DIR, {
  maxAge: '1y',  // Cache for 1 year (use versioned filenames)
  etag: true,
  lastModified: true,
  setHeaders: (res, path) => {
    // Different cache times for different file types
    if (path.endsWith('.css') || path.endsWith('.js')) {
      res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
    } else if (path.match(/\.(png|jpg|jpeg|gif|svg|webp)$/)) {
      res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
    } else if (path.match(/\.(woff|woff2|ttf|otf)$/)) {
      res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
    }
  }
}));
```

**Server-Side Theme Cache:**

```javascript
class ThemeCache {
  constructor() {
    this.cache = new Map();
    this.ttl = 3600 * 1000; // 1 hour
  }

  async getActiveTheme() {
    const cacheKey = 'active_theme';
    const cached = this.cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < this.ttl) {
      return cached.data;
    }

    // Fetch from database
    const theme = await Theme.findOne({
      where: { status: 'active' },
      include: [ThemeSettings]
    });

    this.cache.set(cacheKey, {
      data: theme,
      timestamp: Date.now()
    });

    return theme;
  }

  invalidate(key = null) {
    if (key) {
      this.cache.delete(key);
    } else {
      this.cache.clear();
    }
  }
}
```

### 11.2 Lazy Loading Theme Components

```javascript
// React component for lazy-loaded theme components
import { lazy, Suspense } from 'react';

const ThemeComponent = ({ componentName, fallback = null, ...props }) => {
  const { activeTheme } = useTheme();

  const LazyComponent = lazy(() => {
    // Try to load from theme
    return import(`@themes/${activeTheme.slug}/components/${componentName}`)
      .catch(() => {
        // Fallback to default component
        return import(`@/components/${componentName}`);
      });
  });

  return (
    <Suspense fallback={fallback || <ComponentSkeleton name={componentName} />}>
      <LazyComponent {...props} />
    </Suspense>
  );
};

// Usage
<ThemeComponent
  componentName="layout/Header"
  fallback={<HeaderSkeleton />}
/>
```

### 11.3 Bundle Size Limits for Themes

| Asset Type | Recommended Max | Hard Limit |
|------------|-----------------|------------|
| Total theme bundle | 500KB | 1MB |
| Main CSS file | 100KB | 200KB |
| JavaScript | 150KB | 300KB |
| Single image | 200KB | 500KB |
| All fonts | 100KB | 200KB |

**Bundle Size Checker:**

```javascript
// Theme validation includes bundle size check
async function checkThemeBundleSize(themePath) {
  const sizes = {
    css: 0,
    js: 0,
    images: 0,
    fonts: 0,
    total: 0
  };

  const files = await glob('**/*', { cwd: themePath, nodir: true });

  for (const file of files) {
    const filePath = path.join(themePath, file);
    const stats = await fs.stat(filePath);
    const sizeKB = stats.size / 1024;

    if (file.endsWith('.css')) {
      sizes.css += sizeKB;
    } else if (file.endsWith('.js')) {
      sizes.js += sizeKB;
    } else if (file.match(/\.(png|jpg|jpeg|gif|svg|webp)$/)) {
      sizes.images += sizeKB;
    } else if (file.match(/\.(woff|woff2|ttf|otf)$/)) {
      sizes.fonts += sizeKB;
    }

    sizes.total += sizeKB;
  }

  const warnings = [];

  if (sizes.total > 1024) {
    warnings.push(`Total bundle size (${Math.round(sizes.total)}KB) exceeds 1MB limit`);
  }
  if (sizes.css > 200) {
    warnings.push(`CSS size (${Math.round(sizes.css)}KB) exceeds 200KB recommendation`);
  }
  if (sizes.images > 500) {
    warnings.push(`Images size (${Math.round(sizes.images)}KB) may slow down loading`);
  }

  return { sizes, warnings };
}
```

### 11.4 CSS/JS Minification

**Build-time Minification:**

```javascript
// vite.config.js for theme builds
import { defineConfig } from 'vite';
import cssnano from 'cssnano';

export default defineConfig({
  css: {
    postcss: {
      plugins: [
        cssnano({
          preset: ['default', {
            discardComments: { removeAll: true },
            normalizeWhitespace: true,
            minifyFontValues: true,
            minifyGradients: true
          }]
        })
      ]
    }
  },
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    cssMinify: true
  }
});
```

---

## 12. Security

### 12.1 Theme Validation and Sanitization

```javascript
async function sanitizeTheme(themePath) {
  const issues = [];

  // 1. Remove any PHP files
  const phpFiles = await glob('**/*.php', { cwd: themePath });
  for (const file of phpFiles) {
    await fs.remove(path.join(themePath, file));
    issues.push(`Removed PHP file: ${file}`);
  }

  // 2. Remove any executable files
  const executablePatterns = ['**/*.exe', '**/*.sh', '**/*.bat', '**/*.ps1'];
  for (const pattern of executablePatterns) {
    const files = await glob(pattern, { cwd: themePath });
    for (const file of files) {
      await fs.remove(path.join(themePath, file));
      issues.push(`Removed executable: ${file}`);
    }
  }

  // 3. Sanitize JavaScript files
  const jsFiles = await glob('**/*.{js,jsx}', { cwd: themePath });
  for (const file of jsFiles) {
    const filePath = path.join(themePath, file);
    let content = await fs.readFile(filePath, 'utf8');

    // Remove eval() calls
    if (content.includes('eval(')) {
      content = content.replace(/eval\s*\(/g, '/* eval removed */Function(');
      issues.push(`Sanitized eval() in: ${file}`);
    }

    // Remove document.write() calls
    if (content.includes('document.write')) {
      content = content.replace(/document\.write\s*\(/g,
        '/* document.write removed */ console.log(');
      issues.push(`Sanitized document.write() in: ${file}`);
    }

    await fs.writeFile(filePath, content);
  }

  // 4. Validate SVG files for XSS
  const svgFiles = await glob('**/*.svg', { cwd: themePath });
  for (const file of svgFiles) {
    const filePath = path.join(themePath, file);
    let content = await fs.readFile(filePath, 'utf8');

    // Remove script tags from SVGs
    if (content.includes('<script')) {
      const DOMPurify = require('isomorphic-dompurify');
      content = DOMPurify.sanitize(content, {
        USE_PROFILES: { svg: true, svgFilters: true }
      });
      await fs.writeFile(filePath, content);
      issues.push(`Sanitized SVG: ${file}`);
    }
  }

  return {
    sanitized: true,
    issues
  };
}
```

### 12.2 Preventing Malicious Theme Uploads

```javascript
// Upload validation middleware
const validateThemeUpload = async (req, res, next) => {
  const file = req.file;

  // 1. Check file type
  if (!file.originalname.endsWith('.zip')) {
    return res.status(400).json({
      success: false,
      error: 'Only ZIP files are accepted'
    });
  }

  // 2. Check file size (max 10MB)
  const MAX_SIZE = 10 * 1024 * 1024;
  if (file.size > MAX_SIZE) {
    return res.status(400).json({
      success: false,
      error: 'Theme package exceeds 10MB limit'
    });
  }

  // 3. Scan with ClamAV if available
  if (process.env.ENABLE_VIRUS_SCAN === 'true') {
    const clamscan = require('clamscan');
    const scanner = await new clamscan().init({
      removeInfected: true
    });

    const { isInfected } = await scanner.isInfected(file.path);
    if (isInfected) {
      await fs.remove(file.path);
      return res.status(400).json({
        success: false,
        error: 'Malware detected in uploaded file'
      });
    }
  }

  // 4. Verify ZIP structure (prevent zip bombs)
  const AdmZip = require('adm-zip');
  const zip = new AdmZip(file.path);
  const entries = zip.getEntries();

  let totalUncompressedSize = 0;
  const MAX_UNCOMPRESSED = 50 * 1024 * 1024; // 50MB

  for (const entry of entries) {
    totalUncompressedSize += entry.header.size;

    if (totalUncompressedSize > MAX_UNCOMPRESSED) {
      await fs.remove(file.path);
      return res.status(400).json({
        success: false,
        error: 'Theme package too large when extracted'
      });
    }

    // Check for directory traversal attempts
    if (entry.entryName.includes('..')) {
      await fs.remove(file.path);
      return res.status(400).json({
        success: false,
        error: 'Invalid file paths detected'
      });
    }
  }

  next();
};
```

### 12.3 CSP Headers for Theme Assets

```javascript
// Content Security Policy for theme assets
app.use((req, res, next) => {
  // Base CSP directives
  const cspDirectives = {
    'default-src': ["'self'"],
    'script-src': [
      "'self'",
      "'unsafe-inline'", // Required for React inline styles
      // Add trusted CDNs if needed
    ],
    'style-src': [
      "'self'",
      "'unsafe-inline'", // Required for theme customizer
      'https://fonts.googleapis.com'
    ],
    'font-src': [
      "'self'",
      'https://fonts.gstatic.com',
      'data:' // For embedded fonts
    ],
    'img-src': [
      "'self'",
      'data:',
      'blob:',
      'https:' // Allow HTTPS images
    ],
    'connect-src': [
      "'self'",
      process.env.API_URL || ''
    ],
    'frame-ancestors': ["'self'"], // Prevent clickjacking
    'base-uri': ["'self'"],
    'form-action': ["'self'"]
  };

  // Build CSP header
  const cspHeader = Object.entries(cspDirectives)
    .map(([key, values]) => `${key} ${values.join(' ')}`)
    .join('; ');

  res.setHeader('Content-Security-Policy', cspHeader);
  next();
});
```

### 12.4 Theme Signing (Future Consideration)

```javascript
// Future: Theme signing for verified marketplace themes
class ThemeSignature {
  constructor() {
    this.publicKey = process.env.THEME_SIGNING_PUBLIC_KEY;
  }

  async verifySignature(themePath) {
    const signaturePath = path.join(themePath, 'signature.sig');
    const manifestPath = path.join(themePath, 'theme.json');

    if (!await fs.pathExists(signaturePath)) {
      return {
        verified: false,
        reason: 'Theme is not signed',
        level: 'warning' // Unsigned themes still allowed
      };
    }

    const signature = await fs.readFile(signaturePath, 'utf8');
    const manifest = await fs.readFile(manifestPath, 'utf8');

    const crypto = require('crypto');
    const verify = crypto.createVerify('SHA256');
    verify.update(manifest);

    const isValid = verify.verify(this.publicKey, signature, 'base64');

    return {
      verified: isValid,
      reason: isValid ? 'Signature verified' : 'Invalid signature',
      level: isValid ? 'success' : 'error'
    };
  }
}
```

---

## Architecture Diagrams

### Theme Installation Flow During Wizard

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    THEME INSTALLATION DURING WIZARD                           │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   User                  Installer                   Server                   │
│    │                       │                          │                      │
│    │  Select Theme         │                          │                      │
│    │──────────────────────>│                          │                      │
│    │                       │                          │                      │
│    │                       │   Validate Selection     │                      │
│    │                       │─────────────────────────>│                      │
│    │                       │                          │                      │
│    │                       │   Theme Manifest         │                      │
│    │                       │<─────────────────────────│                      │
│    │                       │                          │                      │
│    │  Show Preview         │                          │                      │
│    │<──────────────────────│                          │                      │
│    │                       │                          │                      │
│    │  Confirm Selection    │                          │                      │
│    │──────────────────────>│                          │                      │
│    │                       │                          │                      │
│    │                       │   Create DB Records      │                      │
│    │                       │─────────────────────────>│  INSERT themes       │
│    │                       │                          │─────────────────────>│
│    │                       │                          │                      │
│    │                       │   Copy Assets to         │  Database            │
│    │                       │   public_html/themes/    │                      │
│    │                       │─────────────────────────>│                      │
│    │                       │                          │                      │
│    │                       │   Apply Default          │                      │
│    │                       │   Settings               │  INSERT              │
│    │                       │─────────────────────────>│  theme_settings      │
│    │                       │                          │─────────────────────>│
│    │                       │                          │                      │
│    │   Success             │                          │                      │
│    │<──────────────────────│                          │                      │
│    │                       │                          │                      │
│    │  Proceed to           │                          │                      │
│    │  Branding Step        │                          │                      │
│    │──────────────────────>│                          │                      │
│    │                       │                          │                      │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Theme Activation Sequence

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                       THEME ACTIVATION SEQUENCE                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Admin Panel              API Server                  Database               │
│       │                       │                          │                   │
│       │  POST /themes/activate                           │                   │
│       │──────────────────────>│                          │                   │
│       │                       │                          │                   │
│       │                       │  Get current active      │                   │
│       │                       │─────────────────────────>│                   │
│       │                       │  theme_id: 'default'     │                   │
│       │                       │<─────────────────────────│                   │
│       │                       │                          │                   │
│       │                       │  Set old theme inactive  │                   │
│       │                       │─────────────────────────>│                   │
│       │                       │  UPDATE themes           │                   │
│       │                       │  SET status='inactive'   │                   │
│       │                       │<─────────────────────────│                   │
│       │                       │                          │                   │
│       │                       │  Set new theme active    │                   │
│       │                       │─────────────────────────>│                   │
│       │                       │  UPDATE themes           │                   │
│       │                       │  SET status='active'     │                   │
│       │                       │<─────────────────────────│                   │
│       │                       │                          │                   │
│       │                       │  Clear theme cache       │                   │
│       │                       │  ─────────────────       │                   │
│       │                       │                          │                   │
│       │                       │  Load new theme assets   │                   │
│       │                       │  ─────────────────       │                   │
│       │                       │                          │                   │
│       │  { success: true }    │                          │                   │
│       │<──────────────────────│                          │                   │
│       │                       │                          │                   │
│       │  Reload page with     │                          │                   │
│       │  new theme            │                          │                   │
│       │  ─────────────────    │                          │                   │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Theme Customization Data Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    THEME CUSTOMIZATION DATA FLOW                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐        │
│  │   Settings      │     │   Theme         │     │   CSS           │        │
│  │   Panel         │────▶│   Context       │────▶│   Variables     │        │
│  │   (React)       │     │   (Provider)    │     │   (DOM)         │        │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘        │
│          │                       │                       │                   │
│          │                       ▼                       │                   │
│          │               ┌─────────────────┐             │                   │
│          │               │   Live Preview  │             │                   │
│          │               │   (iframe)      │◀────────────│                   │
│          │               └─────────────────┘                                 │
│          │                                                                    │
│          │  Save                                                             │
│          ▼                                                                    │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐        │
│  │   PUT /api/     │────▶│   Validate      │────▶│   Save to       │        │
│  │   themes/       │     │   Settings      │     │   Database      │        │
│  │   customize     │     │   Schema        │     │   (theme_       │        │
│  └─────────────────┘     └─────────────────┘     │    settings)    │        │
│                                                   └─────────────────┘        │
│                                                           │                   │
│                                                           ▼                   │
│                                                   ┌─────────────────┐        │
│                                                   │   Invalidate    │        │
│                                                   │   Cache         │        │
│                                                   └─────────────────┘        │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Database Schema Relationships

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      DATABASE SCHEMA RELATIONSHIPS                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│                          ┌─────────────────────┐                              │
│                          │      themes         │                              │
│                          ├─────────────────────┤                              │
│                          │ id (PK)             │                              │
│                          │ slug (UNIQUE)       │                              │
│                          │ name                │                              │
│                          │ version             │                              │
│                          │ status              │◄─── Only one 'active'        │
│                          │ manifest (JSON)     │                              │
│                          │ file_path           │                              │
│                          └──────────┬──────────┘                              │
│                                     │                                         │
│                    ┌────────────────┴────────────────┐                        │
│                    │                                 │                        │
│                    ▼                                 ▼                        │
│       ┌─────────────────────┐           ┌─────────────────────┐              │
│       │   theme_settings    │           │ theme_installations │              │
│       ├─────────────────────┤           ├─────────────────────┤              │
│       │ id (PK)             │           │ id (PK)             │              │
│       │ theme_id (FK)       │           │ theme_id (FK)       │              │
│       │ organization_id     │           │ installed_by        │              │
│       │ settings (JSON)     │           │ installation_source │              │
│       │                     │           │ installation_log    │              │
│       └─────────────────────┘           └─────────────────────┘              │
│              │                                                                │
│              │ UNIQUE(theme_id, organization_id)                             │
│              │                                                                │
│              ▼                                                                │
│       ┌─────────────────────┐                                                │
│       │   organizations     │                                                │
│       │   (future multi-    │                                                │
│       │    tenant support)  │                                                │
│       └─────────────────────┘                                                │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary

This documentation provides a comprehensive guide for integrating the Theme System with the Church LMS Installer Wizard. Key highlights include:

### For Installers
- Simple 4-theme selection during wizard (Step 3)
- Visual previews before committing
- Default theme auto-activation if selection fails

### For Developers
- Database-agnostic schema (PostgreSQL/MySQL)
- RESTful API endpoints for theme management
- Robust error handling and fallback mechanisms

### For Administrators
- Post-install theme browser in admin panel
- Visual theme customizer with live preview
- Import/export settings capability

### For Security
- Multi-layer validation for theme uploads
- Sanitization of potentially dangerous files
- CSP headers for asset protection

### Performance
- Aggressive caching strategy
- Lazy loading for theme components
- Bundle size limits enforcement

---

**Document Version:** 1.0
**Last Updated:** January 11, 2026
**Status:** Planning Phase
**Next Review:** After Phase 1 completion
