# Church LMS - Licensing System Design

**Version:** 1.0
**Last Updated:** January 11, 2026
**Status:** DESIGN PHASE
**Related:** [Implementation Roadmap](./IMPLEMENTATION_VISION.md)

---

## Table of Contents

1. [Overview](#1-overview)
2. [License Key Format](#2-license-key-format)
3. [License Server Architecture](#3-license-server-architecture)
4. [Activation Flow](#4-activation-flow)
5. [License Validation](#5-license-validation)
6. [Database Schema](#6-database-schema)
7. [API Endpoints](#7-api-endpoints)
8. [License Types & Features](#8-license-types--features)
9. [Client-Side Implementation](#9-client-side-implementation)
10. [Security Measures](#10-security-measures)
11. [Admin Portal](#11-admin-portal-license-management)
12. [Integration with Installer](#12-integration-with-installer)
13. [Code Examples](#13-code-examples)

---

## 1. Overview

### Purpose

The licensing system serves three primary functions:

1. **Installation Control**: License key required to complete LMS installation
2. **Support & Updates**: Track installations for providing support and delivering updates
3. **Feature Management**: Enable premium features based on license tier

### Design Principles

- **Simplicity**: Easy for non-technical church administrators to understand
- **Reliability**: Graceful degradation when license server is unreachable
- **Security**: Prevent unauthorized use without being overly restrictive
- **Transparency**: Clear communication about license status and limitations

---

## 2. License Key Format

### Key Structure

```
XXXX-XXXX-XXXX-XXXX
 |    |    |    |
 |    |    |    +-- Checksum segment (4 chars)
 |    |    +------- Random segment (4 chars)
 |    +------------ Encoded metadata (4 chars)
 +----------------- Type prefix + version (4 chars)
```

### Format Specification

| Segment | Position | Length | Description |
|---------|----------|--------|-------------|
| Prefix | 1-4 | 4 chars | License type + version identifier |
| Metadata | 5-8 | 4 chars | Encoded creation date + tier info |
| Random | 9-12 | 4 chars | Cryptographically random characters |
| Checksum | 13-16 | 4 chars | Validation checksum |

### Character Set

```
Allowed characters: ABCDEFGHJKLMNPQRSTUVWXYZ23456789
Excluded (ambiguous): I, O, 0, 1, L
Total: 32 characters (5 bits per character)
```

### Type Prefixes

| Prefix | Type | Description |
|--------|------|-------------|
| `TR25` | Trial | Trial license (2025 format) |
| `ST25` | Standard | Standard single-site license |
| `PM25` | Premium | Premium multi-site license |
| `DV25` | Developer | Developer/agency license |
| `ED25` | Educational | Special educational pricing |
| `NP25` | Non-Profit | Discounted non-profit license |

### Checksum Algorithm

The checksum uses a modified Luhn algorithm adapted for the 32-character set:

```javascript
function calculateChecksum(keyWithoutChecksum) {
  const CHARSET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  const chars = keyWithoutChecksum.replace(/-/g, '').split('');

  let sum = 0;
  for (let i = 0; i < chars.length; i++) {
    let value = CHARSET.indexOf(chars[i]);
    if (i % 2 === 0) {
      value *= 2;
      if (value >= 32) value = (value % 32) + Math.floor(value / 32);
    }
    sum += value;
  }

  // Generate 4-character checksum
  const checksum = [];
  let remaining = (32 * 32 * 32 * 32 - (sum % (32 * 32 * 32 * 32)));
  for (let i = 0; i < 4; i++) {
    checksum.unshift(CHARSET[remaining % 32]);
    remaining = Math.floor(remaining / 32);
  }

  return checksum.join('');
}
```

### Example License Keys

```
Trial:     TR25-A3KM-X7PQ-BCDE
Standard:  ST25-H8NR-W2YT-FGHJ
Premium:   PM25-K4VS-M9ZC-KLMN
Developer: DV25-Q6XB-J3DF-PQRS
```

---

## 3. License Server Architecture

### System Overview

```
+-------------------------+       HTTPS        +-------------------------+
|                         |  <-------------->  |                         |
|     LMS Instance        |                    |     License Server      |
|     (Client)            |                    |     (Central API)       |
|                         |                    |                         |
| +---------------------+ |                    | +---------------------+ |
| | License Validator   | |                    | | Express.js API      | |
| +---------------------+ |                    | +---------------------+ |
| | Activation Token    | |                    | | Rate Limiter        | |
| | (stored in .env)    | |                    | +---------------------+ |
| +---------------------+ |                    | | Authentication      | |
|                         |                    | +---------------------+ |
+-------------------------+                    +------------+------------+
                                                            |
                                               +------------v------------+
                                               |                         |
                                               |      PostgreSQL         |
                                               |      Database           |
                                               |                         |
                                               | +---------------------+ |
                                               | | licenses            | |
                                               | | activations         | |
                                               | | validation_logs     | |
                                               | | feature_flags       | |
                                               | +---------------------+ |
                                               +-------------------------+
```

### Component Responsibilities

#### License Server (Central API)
- Validates license keys
- Tracks activations per license
- Issues and verifies activation tokens
- Provides update notifications
- Manages feature flags
- Generates usage analytics

#### LMS Instance (Client)
- Sends activation requests during installation
- Stores activation token locally
- Performs periodic validation checks
- Handles grace period logic
- Displays license status in admin panel

### Technology Stack

| Component | Technology | Justification |
|-----------|------------|---------------|
| API Server | Node.js + Express | Consistent with LMS codebase |
| Database | PostgreSQL | Robust, supports JSONB for metadata |
| Caching | Redis | Fast validation lookups |
| Hosting | DigitalOcean/AWS | Reliable, scalable |
| SSL | Let's Encrypt | Free, automated certificates |

---

## 4. Activation Flow

### Installation Activation Sequence

```
+-------------+     +-------------+     +------------------+
|   User      |     |  Installer  |     |  License Server  |
+------+------+     +------+------+     +--------+---------+
       |                   |                     |
       | 1. Enter license  |                     |
       |   key             |                     |
       +------------------>|                     |
       |                   |                     |
       |                   | 2. POST /activate   |
       |                   |    {key, domain,    |
       |                   |     server_info}    |
       |                   +-------------------->|
       |                   |                     |
       |                   |                     | 3. Validate key
       |                   |                     |    Check limits
       |                   |                     |    Record activation
       |                   |                     |
       |                   | 4. Return           |
       |                   |    {token, features,|
       |                   |     expires_at}     |
       |                   |<--------------------+
       |                   |                     |
       |                   | 5. Store token      |
       |                   |    in .env          |
       |                   |                     |
       | 6. Success        |                     |
       |    message        |                     |
       |<------------------+                     |
       |                   |                     |
```

### Activation Request Payload

```json
{
  "license_key": "ST25-H8NR-W2YT-FGHJ",
  "domain": "churchlms.example.com",
  "ip_address": "203.0.113.42",
  "server_info": {
    "php_version": "8.1.0",
    "node_version": "18.17.0",
    "os": "Linux",
    "hostname": "server1.hostingprovider.com",
    "database_type": "postgresql"
  },
  "installer_version": "1.0.0",
  "timestamp": "2026-01-11T15:30:00Z"
}
```

### Activation Response

```json
{
  "success": true,
  "activation": {
    "id": "act_abc123def456",
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "activated_at": "2026-01-11T15:30:00Z",
    "expires_at": "2027-01-11T15:30:00Z"
  },
  "license": {
    "type": "standard",
    "holder_name": "First Baptist Church",
    "email": "pastor@firstbaptist.org",
    "features": ["core", "certificates", "analytics"],
    "support_level": "email",
    "update_channel": "stable"
  },
  "validation": {
    "next_check": "2026-02-11T15:30:00Z",
    "grace_period_days": 7
  }
}
```

### Activation Failure Responses

| Error Code | HTTP Status | Message | User Action |
|------------|-------------|---------|-------------|
| `INVALID_KEY` | 400 | License key format is invalid | Check key for typos |
| `KEY_NOT_FOUND` | 404 | License key not found | Verify purchase |
| `KEY_EXPIRED` | 403 | License has expired | Renew license |
| `MAX_ACTIVATIONS` | 403 | Maximum activations reached | Deactivate old site or upgrade |
| `KEY_REVOKED` | 403 | License has been revoked | Contact support |
| `DOMAIN_MISMATCH` | 403 | Domain already registered | Transfer license |
| `SERVER_ERROR` | 500 | Internal server error | Retry later |

---

## 5. License Validation

### Validation Strategy

```
+------------------+
|  LMS Admin       |
|  Dashboard Load  |
+--------+---------+
         |
         v
+--------+---------+
| Check cached     |
| validation       |
+--------+---------+
         |
    +----+----+
    | Valid?  |
    +----+----+
         |
    +----+----+---------------+
    |                         |
   YES                        NO
    |                         |
    v                         v
+---+---+            +--------+---------+
| Allow |            | Online           |
| Access|            | Validation       |
+-------+            +--------+---------+
                              |
                         +----+----+
                         | Success?|
                         +----+----+
                              |
                    +---------+---------+
                    |                   |
                   YES                  NO
                    |                   |
                    v                   v
           +--------+------+   +--------+--------+
           | Update cache  |   | Grace period    |
           | Allow access  |   | check           |
           +---------------+   +--------+--------+
                                        |
                                   +----+----+
                                   | Within  |
                                   | grace?  |
                                   +----+----+
                                        |
                               +--------+--------+
                               |                 |
                              YES                NO
                               |                 |
                               v                 v
                      +--------+------+  +-------+-------+
                      | Allow access  |  | Restrict to   |
                      | Show warning  |  | read-only     |
                      +---------------+  +---------------+
```

### Validation Types

#### 1. Online Validation (Preferred)
- Real-time check against license server
- Updates feature flags and license status
- Resets grace period timer

#### 2. Offline Grace Period (7 Days)
- Allows continued operation when server unreachable
- Shows warning banner after 3 days
- Restricts to read-only after 7 days

#### 3. Periodic Re-validation (Monthly)
- Background check every 30 days
- Non-blocking - continues operation during check
- Updates local cache with new features/status

### Domain Binding Options

| Mode | Description | Use Case |
|------|-------------|----------|
| Strict | Exact domain match required | Production sites |
| Subdomain | Allow *.domain.com | Multi-site churches |
| Flexible | Domain can be changed once per month | Development/staging |
| Localhost | Allow localhost for development | Developer licenses only |

### Validation Cache Structure

```javascript
// Stored in database or Redis
{
  "license_key_hash": "sha256:abc123...",
  "last_validated": "2026-01-11T15:30:00Z",
  "validation_result": "valid",
  "features": ["core", "certificates", "analytics"],
  "expires_at": "2027-01-11T15:30:00Z",
  "grace_period_start": null,
  "next_validation": "2026-02-11T15:30:00Z"
}
```

---

## 6. Database Schema

### Complete Schema

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- LICENSES TABLE
-- Core license information
-- ============================================
CREATE TABLE licenses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  license_key VARCHAR(19) UNIQUE NOT NULL,  -- Format: XXXX-XXXX-XXXX-XXXX
  license_key_hash VARCHAR(64) NOT NULL,     -- SHA-256 hash for lookups

  -- Owner information
  email VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  organization VARCHAR(255),

  -- License configuration
  type VARCHAR(20) NOT NULL DEFAULT 'standard'
    CHECK (type IN ('trial', 'standard', 'premium', 'developer', 'educational', 'nonprofit')),
  max_activations INT NOT NULL DEFAULT 1,

  -- Validity
  expires_at TIMESTAMP WITH TIME ZONE,
  is_active BOOLEAN DEFAULT true,
  revoked_at TIMESTAMP WITH TIME ZONE,
  revocation_reason TEXT,

  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- Additional data
  metadata JSONB DEFAULT '{}',
  notes TEXT,

  -- Purchase tracking
  purchase_id VARCHAR(100),       -- Stripe/PayPal ID
  purchase_amount DECIMAL(10,2),
  currency VARCHAR(3) DEFAULT 'USD',

  -- Indexes
  CONSTRAINT valid_max_activations CHECK (max_activations > 0 AND max_activations <= 100)
);

CREATE INDEX idx_licenses_email ON licenses(email);
CREATE INDEX idx_licenses_type ON licenses(type);
CREATE INDEX idx_licenses_key_hash ON licenses(license_key_hash);
CREATE INDEX idx_licenses_active ON licenses(is_active) WHERE is_active = true;

-- ============================================
-- ACTIVATIONS TABLE
-- Track where licenses are activated
-- ============================================
CREATE TABLE activations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  license_id UUID NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,

  -- Activation token
  activation_token TEXT NOT NULL,
  token_hash VARCHAR(64) NOT NULL,

  -- Installation details
  domain VARCHAR(255) NOT NULL,
  ip_address INET,
  server_info JSONB DEFAULT '{}',

  -- Status
  is_active BOOLEAN DEFAULT true,
  deactivated_at TIMESTAMP WITH TIME ZONE,
  deactivation_reason VARCHAR(50),

  -- Validation tracking
  activated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_validated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  validation_count INT DEFAULT 0,
  last_heartbeat TIMESTAMP WITH TIME ZONE,

  -- Version tracking
  lms_version VARCHAR(20),
  installer_version VARCHAR(20),

  -- Constraints
  CONSTRAINT unique_active_domain UNIQUE (license_id, domain)
    DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX idx_activations_license ON activations(license_id);
CREATE INDEX idx_activations_domain ON activations(domain);
CREATE INDEX idx_activations_active ON activations(is_active) WHERE is_active = true;
CREATE INDEX idx_activations_token_hash ON activations(token_hash);

-- ============================================
-- VALIDATION_LOGS TABLE
-- Audit trail of validation attempts
-- ============================================
CREATE TABLE validation_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  activation_id UUID REFERENCES activations(id) ON DELETE SET NULL,
  license_id UUID REFERENCES licenses(id) ON DELETE SET NULL,

  -- Request details
  request_type VARCHAR(20) NOT NULL
    CHECK (request_type IN ('activate', 'validate', 'heartbeat', 'deactivate')),
  ip_address INET,
  user_agent TEXT,

  -- Result
  success BOOLEAN NOT NULL,
  error_code VARCHAR(50),
  error_message TEXT,

  -- Timing
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  response_time_ms INT,

  -- Additional context
  request_data JSONB,
  response_data JSONB
);

CREATE INDEX idx_validation_logs_activation ON validation_logs(activation_id);
CREATE INDEX idx_validation_logs_license ON validation_logs(license_id);
CREATE INDEX idx_validation_logs_created ON validation_logs(created_at);
CREATE INDEX idx_validation_logs_type ON validation_logs(request_type);

-- ============================================
-- FEATURE_FLAGS TABLE
-- Control feature availability by license type
-- ============================================
CREATE TABLE feature_flags (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  feature_key VARCHAR(50) UNIQUE NOT NULL,
  display_name VARCHAR(100) NOT NULL,
  description TEXT,

  -- Availability by license type (JSONB array)
  available_in JSONB NOT NULL DEFAULT '["standard", "premium", "developer"]',

  -- Feature state
  is_enabled BOOLEAN DEFAULT true,
  rollout_percentage INT DEFAULT 100 CHECK (rollout_percentage BETWEEN 0 AND 100),

  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Default feature flags
INSERT INTO feature_flags (feature_key, display_name, description, available_in) VALUES
  ('core', 'Core LMS Features', 'Basic course, lesson, and user management', '["trial", "standard", "premium", "developer", "educational", "nonprofit"]'),
  ('certificates', 'Certificate Generation', 'Generate completion certificates', '["standard", "premium", "developer", "educational", "nonprofit"]'),
  ('analytics', 'Advanced Analytics', 'Detailed progress and engagement analytics', '["standard", "premium", "developer", "educational", "nonprofit"]'),
  ('white_label', 'White Labeling', 'Remove branding, custom logos', '["premium", "developer"]'),
  ('api_access', 'API Access', 'REST API for integrations', '["premium", "developer"]'),
  ('multi_tenant', 'Multi-Tenant Mode', 'Run multiple church sites from one install', '["developer"]'),
  ('priority_support', 'Priority Support', 'Faster response times', '["premium", "developer"]'),
  ('custom_themes', 'Custom Themes', 'Upload and use custom themes', '["premium", "developer"]'),
  ('bulk_import', 'Bulk Import', 'Import users and content from CSV', '["standard", "premium", "developer"]'),
  ('sso_integration', 'SSO Integration', 'SAML/OAuth single sign-on', '["premium", "developer"]');

-- ============================================
-- LICENSE_TRANSFERS TABLE
-- Track license ownership transfers
-- ============================================
CREATE TABLE license_transfers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  license_id UUID NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,

  from_email VARCHAR(255) NOT NULL,
  to_email VARCHAR(255) NOT NULL,

  transferred_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  transferred_by VARCHAR(255),  -- Admin who approved
  reason TEXT,

  -- Verification
  verification_token VARCHAR(100),
  verified_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_transfers_license ON license_transfers(license_id);

-- ============================================
-- UPDATE TRIGGERS
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER licenses_updated_at
  BEFORE UPDATE ON licenses
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER feature_flags_updated_at
  BEFORE UPDATE ON feature_flags
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================
-- VIEWS
-- ============================================

-- Active licenses with activation counts
CREATE VIEW v_license_status AS
SELECT
  l.id,
  l.license_key,
  l.email,
  l.organization,
  l.type,
  l.max_activations,
  l.expires_at,
  l.is_active,
  COUNT(a.id) FILTER (WHERE a.is_active) as active_count,
  COUNT(a.id) as total_activations,
  MAX(a.last_validated) as last_activity,
  CASE
    WHEN l.is_active = false THEN 'revoked'
    WHEN l.expires_at < NOW() THEN 'expired'
    WHEN COUNT(a.id) FILTER (WHERE a.is_active) >= l.max_activations THEN 'maxed'
    ELSE 'available'
  END as availability_status
FROM licenses l
LEFT JOIN activations a ON l.id = a.license_id
GROUP BY l.id;

-- Daily validation statistics
CREATE VIEW v_daily_stats AS
SELECT
  DATE(created_at) as date,
  request_type,
  COUNT(*) as total_requests,
  COUNT(*) FILTER (WHERE success) as successful,
  COUNT(*) FILTER (WHERE NOT success) as failed,
  AVG(response_time_ms) as avg_response_ms
FROM validation_logs
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at), request_type
ORDER BY date DESC, request_type;
```

---

## 7. API Endpoints

### License Server API

Base URL: `https://license.churchlms.com/api/v1`

#### Validate License Key

```
POST /licenses/validate
```

Validates a license key format and checks if it exists (without activating).

**Request:**
```json
{
  "license_key": "ST25-H8NR-W2YT-FGHJ"
}
```

**Response (200 OK):**
```json
{
  "valid": true,
  "license": {
    "type": "standard",
    "holder_name": "First Baptist Church",
    "max_activations": 1,
    "current_activations": 0,
    "expires_at": "2027-01-11T00:00:00Z",
    "features": ["core", "certificates", "analytics"]
  }
}
```

**Error Response (400/404):**
```json
{
  "valid": false,
  "error": {
    "code": "INVALID_KEY",
    "message": "The license key format is invalid"
  }
}
```

---

#### Activate License

```
POST /licenses/activate
```

Activates a license for a specific domain/installation.

**Request:**
```json
{
  "license_key": "ST25-H8NR-W2YT-FGHJ",
  "domain": "lms.firstbaptist.org",
  "ip_address": "203.0.113.42",
  "server_info": {
    "php_version": "8.1.0",
    "node_version": "18.17.0",
    "database_type": "postgresql",
    "os": "Linux"
  },
  "installer_version": "1.0.0"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "activation": {
    "id": "act_7f3d8a2b-1234-5678-9abc-def012345678",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "domain": "lms.firstbaptist.org",
    "activated_at": "2026-01-11T15:30:00Z"
  },
  "license": {
    "type": "standard",
    "expires_at": "2027-01-11T00:00:00Z",
    "features": ["core", "certificates", "analytics"],
    "support_level": "email"
  },
  "validation": {
    "interval_days": 30,
    "grace_period_days": 7,
    "next_check": "2026-02-11T15:30:00Z"
  }
}
```

---

#### Deactivate License

```
POST /licenses/deactivate
```

Deactivates a license from a domain (frees up activation slot).

**Request:**
```json
{
  "activation_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "reason": "moving_to_new_server"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "License deactivated successfully",
  "remaining_activations": 1
}
```

---

#### Get License Status

```
GET /licenses/:key/status
```

Returns current status of a license (requires authentication).

**Headers:**
```
Authorization: Bearer <admin_api_key>
```

**Response (200 OK):**
```json
{
  "license": {
    "key": "ST25-H8NR-****-****",
    "type": "standard",
    "holder": {
      "name": "First Baptist Church",
      "email": "pastor@firstbaptist.org"
    },
    "status": "active",
    "expires_at": "2027-01-11T00:00:00Z",
    "activations": {
      "max": 1,
      "current": 1,
      "list": [
        {
          "domain": "lms.firstbaptist.org",
          "activated_at": "2026-01-11T15:30:00Z",
          "last_validated": "2026-01-11T18:00:00Z",
          "is_active": true
        }
      ]
    }
  }
}
```

---

#### Heartbeat / Periodic Validation

```
POST /licenses/heartbeat
```

Periodic check-in from active installations.

**Request:**
```json
{
  "activation_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "lms_version": "1.2.0",
  "stats": {
    "users": 150,
    "courses": 12,
    "completions": 89
  }
}
```

**Response (200 OK):**
```json
{
  "valid": true,
  "license_status": "active",
  "features": ["core", "certificates", "analytics"],
  "updates": {
    "available": true,
    "latest_version": "1.3.0",
    "release_notes_url": "https://churchlms.com/changelog/1.3.0",
    "severity": "recommended"
  },
  "next_heartbeat": "2026-02-11T15:30:00Z",
  "announcements": [
    {
      "id": "ann_123",
      "type": "info",
      "message": "New theme pack available for Premium users!"
    }
  ]
}
```

---

### Rate Limits

| Endpoint | Rate Limit | Window |
|----------|------------|--------|
| `/validate` | 10 requests | per minute |
| `/activate` | 5 requests | per hour |
| `/deactivate` | 5 requests | per hour |
| `/heartbeat` | 100 requests | per day |
| `/:key/status` | 30 requests | per minute |

---

## 8. License Types & Features

### Pricing Tiers

| Type | Activations | Support | Updates | Features | Price |
|------|-------------|---------|---------|----------|-------|
| **Trial** | 1 | Community | 30 days | Core only | Free |
| **Standard** | 1 | Email (48h) | 1 year | Core + Certs + Analytics | $49/year |
| **Premium** | 3 | Priority (24h) | Lifetime | All features | $149 one-time |
| **Developer** | 10 | Priority (24h) | Lifetime | All + Multi-tenant | $299 one-time |
| **Educational** | 1 | Email (48h) | 1 year | Core + Certs + Analytics | $29/year |
| **Non-Profit** | 1 | Email (48h) | 1 year | Core + Certs + Analytics | $29/year |

### Feature Matrix

| Feature | Trial | Standard | Premium | Developer |
|---------|-------|----------|---------|-----------|
| Core LMS (courses, lessons, users) | Yes | Yes | Yes | Yes |
| Basic Analytics | Yes | Yes | Yes | Yes |
| Certificate Generation | No | Yes | Yes | Yes |
| Advanced Analytics | No | Yes | Yes | Yes |
| Bulk Import/Export | No | Yes | Yes | Yes |
| White Labeling | No | No | Yes | Yes |
| Custom Themes | No | No | Yes | Yes |
| API Access | No | No | Yes | Yes |
| SSO Integration | No | No | Yes | Yes |
| Multi-Tenant Mode | No | No | No | Yes |
| Remove "Powered By" | No | No | Yes | Yes |
| Priority Support | No | No | Yes | Yes |

### Upgrade Paths

```
Trial ──────────────────────────────────────────────────────┐
  │                                                          │
  ▼                                                          ▼
Standard ($49/yr) ──────────────────────────────────> Premium ($149)
  │                                                          │
  │                                                          ▼
  └──────────────────────────────────────────────────> Developer ($299)
```

---

## 9. Client-Side Implementation

### License Check on Admin Dashboard

```javascript
// /server/utils/licenseValidator.js

const jwt = require('jsonwebtoken');
const axios = require('axios');

const LICENSE_SERVER = process.env.LICENSE_SERVER_URL || 'https://license.churchlms.com';
const GRACE_PERIOD_DAYS = 7;
const VALIDATION_INTERVAL_DAYS = 30;

class LicenseValidator {
  constructor() {
    this.cachedValidation = null;
    this.lastCheck = null;
  }

  /**
   * Get activation token from environment
   */
  getActivationToken() {
    return process.env.LICENSE_ACTIVATION_TOKEN;
  }

  /**
   * Decode and verify activation token locally
   */
  decodeToken(token) {
    try {
      // Note: This only decodes, doesn't verify signature
      // Full verification happens server-side
      return jwt.decode(token);
    } catch (error) {
      return null;
    }
  }

  /**
   * Check if validation is needed
   */
  needsValidation() {
    if (!this.lastCheck) return true;

    const daysSinceCheck = (Date.now() - this.lastCheck) / (1000 * 60 * 60 * 24);
    return daysSinceCheck >= VALIDATION_INTERVAL_DAYS;
  }

  /**
   * Check if within grace period
   */
  isWithinGracePeriod() {
    if (!this.cachedValidation?.graceStarted) return true;

    const graceDays = (Date.now() - this.cachedValidation.graceStarted) / (1000 * 60 * 60 * 24);
    return graceDays < GRACE_PERIOD_DAYS;
  }

  /**
   * Perform online validation
   */
  async validateOnline() {
    const token = this.getActivationToken();
    if (!token) {
      return { valid: false, error: 'NO_TOKEN', message: 'No activation token found' };
    }

    try {
      const response = await axios.post(`${LICENSE_SERVER}/api/v1/licenses/heartbeat`, {
        activation_token: token,
        lms_version: process.env.LMS_VERSION || '1.0.0'
      }, {
        timeout: 10000 // 10 second timeout
      });

      this.cachedValidation = {
        valid: true,
        features: response.data.features,
        licenseType: response.data.license_type,
        expiresAt: response.data.expires_at,
        graceStarted: null
      };
      this.lastCheck = Date.now();

      return {
        valid: true,
        features: response.data.features,
        updates: response.data.updates
      };

    } catch (error) {
      // Server unreachable - enter grace period
      if (!this.cachedValidation?.graceStarted) {
        this.cachedValidation = {
          ...this.cachedValidation,
          graceStarted: Date.now()
        };
      }

      if (this.isWithinGracePeriod()) {
        return {
          valid: true,
          gracePeriod: true,
          daysRemaining: GRACE_PERIOD_DAYS - Math.floor(
            (Date.now() - this.cachedValidation.graceStarted) / (1000 * 60 * 60 * 24)
          ),
          features: this.cachedValidation?.features || ['core']
        };
      }

      return {
        valid: false,
        error: 'GRACE_EXPIRED',
        message: 'License validation failed and grace period has expired'
      };
    }
  }

  /**
   * Main validation method
   */
  async validate() {
    // Quick check if we have recent valid cache
    if (!this.needsValidation() && this.cachedValidation?.valid) {
      return {
        valid: true,
        cached: true,
        features: this.cachedValidation.features
      };
    }

    // Perform online validation
    return this.validateOnline();
  }

  /**
   * Check if a specific feature is available
   */
  async hasFeature(featureKey) {
    const validation = await this.validate();
    if (!validation.valid) return false;
    return validation.features?.includes(featureKey) || false;
  }

  /**
   * Get license status for admin display
   */
  async getStatus() {
    const token = this.getActivationToken();
    if (!token) {
      return {
        status: 'not_activated',
        message: 'No license activated'
      };
    }

    const decoded = this.decodeToken(token);
    const validation = await this.validate();

    return {
      status: validation.valid ? 'active' : 'invalid',
      licenseType: decoded?.type || 'unknown',
      domain: decoded?.domain,
      activatedAt: decoded?.iat ? new Date(decoded.iat * 1000) : null,
      expiresAt: decoded?.exp ? new Date(decoded.exp * 1000) : null,
      features: validation.features || [],
      gracePeriod: validation.gracePeriod || false,
      daysRemaining: validation.daysRemaining,
      updates: validation.updates
    };
  }
}

module.exports = new LicenseValidator();
```

### License Status Component (React)

```jsx
// /client/src/components/admin/LicenseStatus.jsx

import React, { useState, useEffect } from 'react';
import { Card, Badge, Button, Alert } from 'react-bootstrap';
import { CheckCircle, AlertTriangle, XCircle, RefreshCw } from 'lucide-react';

const LicenseStatus = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/admin/license/status');
      const data = await response.json();
      setStatus(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch license status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const getStatusBadge = () => {
    if (!status) return null;

    switch (status.status) {
      case 'active':
        return <Badge bg="success"><CheckCircle size={14} /> Active</Badge>;
      case 'grace_period':
        return <Badge bg="warning"><AlertTriangle size={14} /> Grace Period</Badge>;
      case 'expired':
        return <Badge bg="danger"><XCircle size={14} /> Expired</Badge>;
      case 'not_activated':
        return <Badge bg="secondary">Not Activated</Badge>;
      default:
        return <Badge bg="secondary">Unknown</Badge>;
    }
  };

  const getLicenseTypeBadge = (type) => {
    const colors = {
      trial: 'secondary',
      standard: 'primary',
      premium: 'info',
      developer: 'success'
    };
    return <Badge bg={colors[type] || 'secondary'}>{type?.toUpperCase()}</Badge>;
  };

  if (loading) {
    return <Card><Card.Body>Loading license status...</Card.Body></Card>;
  }

  return (
    <Card className="license-status-card">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <h5 className="mb-0">License Status</h5>
        <Button variant="outline-secondary" size="sm" onClick={fetchStatus}>
          <RefreshCw size={14} />
        </Button>
      </Card.Header>
      <Card.Body>
        {error && <Alert variant="danger">{error}</Alert>}

        {status?.gracePeriod && (
          <Alert variant="warning">
            <AlertTriangle size={16} className="me-2" />
            Unable to reach license server. Grace period: {status.daysRemaining} days remaining.
            Please check your internet connection.
          </Alert>
        )}

        <div className="license-info">
          <div className="info-row">
            <span className="label">Status:</span>
            {getStatusBadge()}
          </div>

          <div className="info-row">
            <span className="label">License Type:</span>
            {getLicenseTypeBadge(status?.licenseType)}
          </div>

          <div className="info-row">
            <span className="label">Domain:</span>
            <span>{status?.domain || 'N/A'}</span>
          </div>

          <div className="info-row">
            <span className="label">Activated:</span>
            <span>{status?.activatedAt ? new Date(status.activatedAt).toLocaleDateString() : 'N/A'}</span>
          </div>

          <div className="info-row">
            <span className="label">Expires:</span>
            <span>{status?.expiresAt ? new Date(status.expiresAt).toLocaleDateString() : 'Never'}</span>
          </div>
        </div>

        {status?.features && (
          <div className="features-section mt-3">
            <h6>Enabled Features:</h6>
            <div className="feature-badges">
              {status.features.map(feature => (
                <Badge key={feature} bg="light" text="dark" className="me-1 mb-1">
                  {feature}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {status?.updates?.available && (
          <Alert variant="info" className="mt-3">
            <strong>Update Available:</strong> Version {status.updates.latest_version}
            <br />
            <a href={status.updates.release_notes_url} target="_blank" rel="noopener noreferrer">
              View Release Notes
            </a>
          </Alert>
        )}
      </Card.Body>
    </Card>
  );
};

export default LicenseStatus;
```

### Feature Flag Hook

```jsx
// /client/src/hooks/useFeature.js

import { useState, useEffect, createContext, useContext } from 'react';

const FeatureContext = createContext({});

export const FeatureProvider = ({ children }) => {
  const [features, setFeatures] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadFeatures = async () => {
      try {
        const response = await fetch('/api/license/features');
        const data = await response.json();
        setFeatures(data.features || []);
      } catch (error) {
        console.error('Failed to load features:', error);
        setFeatures(['core']); // Fallback to core features
      } finally {
        setLoading(false);
      }
    };

    loadFeatures();
  }, []);

  return (
    <FeatureContext.Provider value={{ features, loading }}>
      {children}
    </FeatureContext.Provider>
  );
};

export const useFeature = (featureKey) => {
  const { features, loading } = useContext(FeatureContext);
  return {
    enabled: features.includes(featureKey),
    loading
  };
};

// Usage example:
// const { enabled: hasCertificates } = useFeature('certificates');
// if (hasCertificates) { /* show certificate UI */ }
```

---

## 10. Security Measures

### License Key Security

#### 1. Key Hashing in Database

License keys are stored hashed, with only partial key visible for support:

```javascript
const crypto = require('crypto');

function hashLicenseKey(key) {
  return crypto
    .createHash('sha256')
    .update(key + process.env.LICENSE_SALT)
    .digest('hex');
}

function maskLicenseKey(key) {
  // Show first and last segment only: ST25-****-****-FGHJ
  const parts = key.split('-');
  return `${parts[0]}-****-****-${parts[3]}`;
}
```

#### 2. Activation Token Structure (JWT)

```javascript
const jwt = require('jsonwebtoken');

function generateActivationToken(license, activation) {
  return jwt.sign({
    // Standard claims
    iss: 'license.churchlms.com',
    sub: activation.id,
    aud: activation.domain,
    exp: Math.floor(license.expires_at.getTime() / 1000),
    iat: Math.floor(Date.now() / 1000),

    // Custom claims
    lid: license.id,           // License ID
    type: license.type,        // License type
    features: getFeatures(license.type),
    domain: activation.domain,

    // Anti-tampering
    fingerprint: generateFingerprint(activation)
  }, process.env.JWT_SECRET, {
    algorithm: 'HS256'
  });
}

function generateFingerprint(activation) {
  return crypto
    .createHash('sha256')
    .update(`${activation.domain}:${activation.ip_address}:${Date.now()}`)
    .digest('hex')
    .substring(0, 16);
}
```

### Rate Limiting Implementation

```javascript
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const Redis = require('ioredis');

const redis = new Redis(process.env.REDIS_URL);

// Validation endpoint - stricter limit
const validateLimiter = rateLimit({
  store: new RedisStore({
    client: redis,
    prefix: 'rl:validate:'
  }),
  windowMs: 60 * 1000, // 1 minute
  max: 10,
  message: {
    error: 'RATE_LIMITED',
    message: 'Too many validation requests. Please try again later.',
    retryAfter: 60
  },
  standardHeaders: true,
  legacyHeaders: false
});

// Activation endpoint - very strict
const activateLimiter = rateLimit({
  store: new RedisStore({
    client: redis,
    prefix: 'rl:activate:'
  }),
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 5,
  message: {
    error: 'RATE_LIMITED',
    message: 'Too many activation attempts. Please try again in an hour.',
    retryAfter: 3600
  }
});

// Apply to routes
app.post('/api/v1/licenses/validate', validateLimiter, validateHandler);
app.post('/api/v1/licenses/activate', activateLimiter, activateHandler);
```

### Domain Verification

```javascript
async function verifyDomain(claimedDomain, requestIP) {
  const dns = require('dns').promises;

  try {
    // 1. Resolve claimed domain to IP
    const resolvedIPs = await dns.resolve4(claimedDomain);

    // 2. Check if request IP matches resolved IP
    if (!resolvedIPs.includes(requestIP)) {
      // Could be behind proxy - check X-Forwarded-For
      return {
        verified: false,
        reason: 'IP mismatch',
        claimedDomain,
        requestIP,
        resolvedIPs
      };
    }

    // 3. Optional: Check for verification file
    // (for initial activation, require a file at domain/.well-known/churchlms-verify.txt)

    return {
      verified: true,
      claimedDomain,
      requestIP
    };

  } catch (error) {
    return {
      verified: false,
      reason: 'DNS resolution failed',
      error: error.message
    };
  }
}
```

### Tampering Detection

```javascript
// Client-side integrity check
function checkIntegrity() {
  const checks = {
    envExists: !!process.env.LICENSE_ACTIVATION_TOKEN,
    tokenValid: false,
    filesIntact: true
  };

  // Verify token hasn't been modified
  if (checks.envExists) {
    try {
      const decoded = jwt.decode(process.env.LICENSE_ACTIVATION_TOKEN);
      checks.tokenValid = decoded && decoded.exp > Date.now() / 1000;
    } catch {
      checks.tokenValid = false;
    }
  }

  // Check critical files haven't been modified
  const criticalFiles = [
    'server/utils/licenseValidator.js',
    'server/middleware/licenseCheck.js'
  ];

  for (const file of criticalFiles) {
    const hash = calculateFileHash(file);
    if (hash !== expectedHashes[file]) {
      checks.filesIntact = false;
      break;
    }
  }

  return checks;
}
```

### Security Best Practices Summary

| Measure | Implementation | Purpose |
|---------|---------------|---------|
| Key Hashing | SHA-256 + salt | Protect stored keys |
| JWT Tokens | HS256 signed | Secure activation tokens |
| Rate Limiting | Redis-backed | Prevent brute force |
| Domain Binding | DNS verification | Prevent license sharing |
| HTTPS Only | TLS 1.3 required | Secure transmission |
| Token Expiry | Time-limited JWTs | Limit exposure window |
| Audit Logging | All attempts logged | Detect abuse patterns |
| Fingerprinting | Hardware/env hash | Detect cloning |

---

## 11. Admin Portal (License Management)

### Portal Features

#### Dashboard Overview

```
+------------------------------------------------------------------+
|  License Management Portal                              Admin v   |
+------------------------------------------------------------------+
|                                                                   |
|  Quick Stats                                                      |
|  +------------+  +------------+  +------------+  +------------+   |
|  |    1,247   |  |     892    |  |     45     |  |   $12,450  |   |
|  |   Total    |  |   Active   |  |  Expiring  |  |  Revenue   |   |
|  |  Licenses  |  | Activations|  |  (30 days) |  |  (MTD)     |   |
|  +------------+  +------------+  +------------+  +------------+   |
|                                                                   |
|  Recent Activity                                                  |
|  +------------------------------------------------------------+  |
|  | Time       | Event              | License      | Domain     |  |
|  |------------|--------------------|--------------| -----------|  |
|  | 2 min ago  | Activation         | ST25-H8NR... | church.org |  |
|  | 15 min ago | Validation         | PM25-K4VS... | faith.com  |  |
|  | 1 hour ago | Deactivation       | ST25-Q6XB... | hope.net   |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

#### License Generation

```javascript
// Admin API endpoint for generating licenses
router.post('/admin/licenses/generate', adminAuth, async (req, res) => {
  const {
    type,
    email,
    name,
    organization,
    quantity = 1,
    expiresIn, // days
    customExpiry,
    notes
  } = req.body;

  const licenses = [];

  for (let i = 0; i < quantity; i++) {
    const key = generateLicenseKey(type);
    const expiresAt = customExpiry
      ? new Date(customExpiry)
      : expiresIn
        ? new Date(Date.now() + expiresIn * 24 * 60 * 60 * 1000)
        : null;

    const license = await License.create({
      license_key: key,
      license_key_hash: hashLicenseKey(key),
      type,
      email,
      name,
      organization,
      max_activations: getMaxActivations(type),
      expires_at: expiresAt,
      notes,
      metadata: {
        generated_by: req.admin.id,
        generated_at: new Date()
      }
    });

    licenses.push({
      id: license.id,
      key: key, // Full key only shown once
      type,
      expires_at: expiresAt
    });
  }

  // Send email with license key(s) if email provided
  if (email) {
    await sendLicenseEmail(email, licenses, { name, organization });
  }

  res.json({
    success: true,
    count: licenses.length,
    licenses: licenses.map(l => ({
      ...l,
      key: maskLicenseKey(l.key) // Mask for response
    })),
    fullKeys: licenses.map(l => l.key) // Full keys - handle securely!
  });
});
```

#### View & Manage Activations

```jsx
// React component for activation management
const ActivationManager = ({ licenseId }) => {
  const [activations, setActivations] = useState([]);

  const handleDeactivate = async (activationId) => {
    if (!confirm('Deactivate this installation? The site will need to re-activate.')) {
      return;
    }

    await fetch(`/api/admin/activations/${activationId}/revoke`, {
      method: 'POST'
    });

    // Refresh list
    fetchActivations();
  };

  const handleTransfer = async (activationId, newDomain) => {
    await fetch(`/api/admin/activations/${activationId}/transfer`, {
      method: 'POST',
      body: JSON.stringify({ newDomain })
    });
  };

  return (
    <Table>
      <thead>
        <tr>
          <th>Domain</th>
          <th>IP Address</th>
          <th>Activated</th>
          <th>Last Seen</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {activations.map(a => (
          <tr key={a.id}>
            <td>{a.domain}</td>
            <td>{a.ip_address}</td>
            <td>{formatDate(a.activated_at)}</td>
            <td>{formatDate(a.last_validated)}</td>
            <td>
              <Badge bg={a.is_active ? 'success' : 'secondary'}>
                {a.is_active ? 'Active' : 'Inactive'}
              </Badge>
            </td>
            <td>
              {a.is_active && (
                <>
                  <Button size="sm" variant="outline-warning" onClick={() => handleTransfer(a.id)}>
                    Transfer
                  </Button>
                  <Button size="sm" variant="outline-danger" onClick={() => handleDeactivate(a.id)}>
                    Revoke
                  </Button>
                </>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};
```

#### Usage Analytics Dashboard

```sql
-- Analytics queries for admin dashboard

-- Monthly activation trends
SELECT
  DATE_TRUNC('month', activated_at) as month,
  COUNT(*) as activations,
  COUNT(DISTINCT license_id) as unique_licenses
FROM activations
WHERE activated_at > NOW() - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', activated_at)
ORDER BY month;

-- License type distribution
SELECT
  type,
  COUNT(*) as count,
  COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
FROM licenses
WHERE is_active = true
GROUP BY type;

-- Top domains by validation frequency
SELECT
  domain,
  COUNT(*) as validations,
  MAX(last_validated) as last_seen
FROM activations
WHERE is_active = true
GROUP BY domain
ORDER BY validations DESC
LIMIT 20;

-- Failed validation attempts (potential issues)
SELECT
  DATE(created_at) as date,
  error_code,
  COUNT(*) as failures
FROM validation_logs
WHERE success = false
  AND created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at), error_code
ORDER BY date DESC, failures DESC;
```

---

## 12. Integration with Installer

### License Entry Screen Design

```
+------------------------------------------------------------------+
|                                                                   |
|                    [Church LMS Logo]                              |
|                                                                   |
|              Welcome to Church LMS Installation                   |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  Step 2 of 6: License Activation                                  |
|  ═══════════════════════════════                                  |
|                                                                   |
|  Please enter your license key to continue installation.          |
|                                                                   |
|  +------------------------------------------------------------+  |
|  |                                                            |  |
|  |  License Key:                                              |  |
|  |  +--------+  +--------+  +--------+  +--------+           |  |
|  |  | ST25   |  | H8NR   |  | W2YT   |  | FGHJ   |           |  |
|  |  +--------+  +--------+  +--------+  +--------+           |  |
|  |                                                            |  |
|  |  [✓] I agree to the Terms of Service                      |  |
|  |                                                            |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  Don't have a license key?                                        |
|  • Purchase at churchlms.com/pricing                              |
|  • Start a free 30-day trial                                      |
|                                                                   |
|  +------------------+              +------------------+            |
|  |     < Back       |              |  Activate & Continue  →     |
|  +------------------+              +------------------+            |
|                                                                   |
+------------------------------------------------------------------+
```

### Installer License Validation Flow

```php
<?php
// /installer/steps/license.php

class LicenseStep {
    private $licenseServer = 'https://license.churchlms.com';

    public function validateKey($key) {
        // 1. Format validation (local)
        if (!$this->isValidFormat($key)) {
            return [
                'valid' => false,
                'error' => 'INVALID_FORMAT',
                'message' => 'License key format is invalid. Please check for typos.'
            ];
        }

        // 2. Checksum validation (local)
        if (!$this->verifyChecksum($key)) {
            return [
                'valid' => false,
                'error' => 'INVALID_CHECKSUM',
                'message' => 'License key checksum failed. Please verify your key.'
            ];
        }

        // 3. Online validation
        return $this->validateOnline($key);
    }

    private function isValidFormat($key) {
        // XXXX-XXXX-XXXX-XXXX format
        return preg_match('/^[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}$/', $key);
    }

    private function verifyChecksum($key) {
        $parts = explode('-', $key);
        $keyWithoutChecksum = implode('', array_slice($parts, 0, 3));
        $providedChecksum = $parts[3];
        $calculatedChecksum = $this->calculateChecksum($keyWithoutChecksum);

        return $providedChecksum === $calculatedChecksum;
    }

    private function validateOnline($key) {
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $this->licenseServer . '/api/v1/licenses/validate',
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode(['license_key' => $key]),
            CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 30,
            CURLOPT_SSL_VERIFYPEER => true
        ]);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 200) {
            return [
                'valid' => false,
                'error' => 'SERVER_ERROR',
                'message' => 'Could not reach license server. Please check your internet connection.'
            ];
        }

        return json_decode($response, true);
    }

    public function activate($key, $domain, $serverInfo) {
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $this->licenseServer . '/api/v1/licenses/activate',
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode([
                'license_key' => $key,
                'domain' => $domain,
                'ip_address' => $_SERVER['SERVER_ADDR'] ?? null,
                'server_info' => $serverInfo,
                'installer_version' => INSTALLER_VERSION
            ]),
            CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 60
        ]);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode === 201) {
            $data = json_decode($response, true);

            // Store activation token in session for .env writing
            $_SESSION['license_activation'] = [
                'token' => $data['activation']['token'],
                'type' => $data['license']['type'],
                'features' => $data['license']['features']
            ];

            return ['success' => true, 'data' => $data];
        }

        $error = json_decode($response, true);
        return [
            'success' => false,
            'error' => $error['error']['code'] ?? 'UNKNOWN',
            'message' => $error['error']['message'] ?? 'Activation failed'
        ];
    }
}
```

### Error Handling UI

```jsx
// Installer error messages component
const LicenseErrors = ({ error }) => {
  const errorMessages = {
    INVALID_FORMAT: {
      title: 'Invalid License Key Format',
      message: 'The license key you entered doesn\'t match the expected format (XXXX-XXXX-XXXX-XXXX).',
      action: 'Please check your key for typos and try again.'
    },
    KEY_NOT_FOUND: {
      title: 'License Key Not Found',
      message: 'This license key is not registered in our system.',
      action: 'Please verify you\'re using the correct key from your purchase confirmation email.'
    },
    KEY_EXPIRED: {
      title: 'License Has Expired',
      message: 'Your license key has expired and is no longer valid.',
      action: 'Please renew your license at churchlms.com/account or purchase a new one.'
    },
    MAX_ACTIVATIONS: {
      title: 'Activation Limit Reached',
      message: 'This license has reached its maximum number of activations.',
      action: 'Deactivate an existing installation or upgrade to a higher-tier license for more activations.'
    },
    SERVER_ERROR: {
      title: 'Connection Error',
      message: 'Unable to connect to the license server.',
      action: 'Please check your internet connection and try again. If the problem persists, contact support.'
    }
  };

  const errorInfo = errorMessages[error] || {
    title: 'Activation Error',
    message: 'An unexpected error occurred during activation.',
    action: 'Please try again or contact support if the problem continues.'
  };

  return (
    <div className="license-error">
      <div className="error-icon">⚠️</div>
      <h4>{errorInfo.title}</h4>
      <p>{errorInfo.message}</p>
      <p className="action">{errorInfo.action}</p>
      <div className="error-links">
        <a href="https://churchlms.com/support">Contact Support</a>
        <a href="https://churchlms.com/pricing">View Pricing</a>
      </div>
    </div>
  );
};
```

### Offline Installation Option

For environments without internet during installation:

```php
<?php
// Offline activation generates a request code that can be activated
// via web browser on another device

class OfflineActivation {

    public function generateRequestCode($key, $domain, $serverInfo) {
        $requestData = [
            'license_key' => $key,
            'domain' => $domain,
            'server_info' => $serverInfo,
            'timestamp' => time(),
            'nonce' => bin2hex(random_bytes(16))
        ];

        // Encode as base64 for easy copy/paste
        return base64_encode(json_encode($requestData));
    }

    public function displayOfflineInstructions($requestCode) {
        return <<<HTML
        <div class="offline-activation">
            <h4>Offline Activation</h4>
            <p>Your server cannot reach our license server. To activate offline:</p>
            <ol>
                <li>Copy the request code below</li>
                <li>Visit <strong>churchlms.com/activate-offline</strong> on a device with internet</li>
                <li>Paste the request code and click "Generate Response"</li>
                <li>Copy the response code and paste it below</li>
            </ol>

            <div class="code-box">
                <label>Request Code (copy this):</label>
                <textarea readonly onclick="this.select()">{$requestCode}</textarea>
            </div>

            <div class="code-box">
                <label>Response Code (paste here):</label>
                <textarea name="response_code" placeholder="Paste the response code here..."></textarea>
            </div>
        </div>
        HTML;
    }

    public function processResponseCode($responseCode) {
        try {
            $data = json_decode(base64_decode($responseCode), true);

            // Verify signature
            $signature = $data['signature'];
            unset($data['signature']);

            $expectedSignature = hash_hmac('sha256', json_encode($data), OFFLINE_ACTIVATION_SECRET);

            if (!hash_equals($expectedSignature, $signature)) {
                return ['success' => false, 'error' => 'Invalid response code'];
            }

            // Check expiry (response codes valid for 24 hours)
            if ($data['expires'] < time()) {
                return ['success' => false, 'error' => 'Response code has expired'];
            }

            // Store the token
            $_SESSION['license_activation'] = [
                'token' => $data['token'],
                'type' => $data['type'],
                'features' => $data['features'],
                'offline' => true
            ];

            return ['success' => true];

        } catch (Exception $e) {
            return ['success' => false, 'error' => 'Invalid response code format'];
        }
    }
}
```

### Writing License to .env

```php
<?php
// Final step: Write activation token to .env file

function writeLicenseToEnv($envPath, $licenseData) {
    $envContent = file_get_contents($envPath);

    // License configuration block
    $licenseBlock = <<<ENV

# License Configuration
# Generated during installation - DO NOT MODIFY
LICENSE_ACTIVATION_TOKEN="{$licenseData['token']}"
LICENSE_TYPE="{$licenseData['type']}"
LICENSE_FEATURES="{$licenseData['features']}"
LICENSE_ACTIVATED_AT="{$licenseData['activated_at']}"
ENV;

    // Append or replace license block
    if (strpos($envContent, '# License Configuration') !== false) {
        $envContent = preg_replace(
            '/# License Configuration.*?(?=\n\n|\n#|\z)/s',
            trim($licenseBlock),
            $envContent
        );
    } else {
        $envContent .= $licenseBlock;
    }

    file_put_contents($envPath, $envContent);

    // Secure the .env file
    chmod($envPath, 0600);
}
```

---

## 13. Code Examples

### Complete License Key Generator

```javascript
// /license-server/utils/keyGenerator.js

const crypto = require('crypto');

const CHARSET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
const KEY_LENGTH = 16; // 4 segments of 4 characters

class LicenseKeyGenerator {
  constructor(salt) {
    this.salt = salt || process.env.LICENSE_SALT;
  }

  /**
   * Generate a complete license key
   */
  generate(type = 'standard') {
    const prefix = this.getPrefix(type);
    const metadata = this.encodeMetadata(type);
    const random = this.generateRandom(4);

    const keyWithoutChecksum = `${prefix}${metadata}${random}`;
    const checksum = this.calculateChecksum(keyWithoutChecksum);

    return this.formatKey(`${keyWithoutChecksum}${checksum}`);
  }

  /**
   * Get prefix for license type
   */
  getPrefix(type) {
    const year = new Date().getFullYear().toString().slice(-2);
    const prefixes = {
      trial: 'TR',
      standard: 'ST',
      premium: 'PM',
      developer: 'DV',
      educational: 'ED',
      nonprofit: 'NP'
    };
    return (prefixes[type] || 'ST') + year;
  }

  /**
   * Encode metadata into 4 characters
   */
  encodeMetadata(type) {
    // Encode: creation month (1 char) + type tier (1 char) + random (2 chars)
    const month = CHARSET[new Date().getMonth()];
    const tier = CHARSET[['trial', 'standard', 'premium', 'developer'].indexOf(type) || 1];
    const random = this.generateRandom(2);

    return month + tier + random;
  }

  /**
   * Generate random characters
   */
  generateRandom(length) {
    let result = '';
    const randomBytes = crypto.randomBytes(length);
    for (let i = 0; i < length; i++) {
      result += CHARSET[randomBytes[i] % CHARSET.length];
    }
    return result;
  }

  /**
   * Calculate checksum using modified Luhn algorithm
   */
  calculateChecksum(input) {
    let sum = 0;
    const chars = input.split('');

    for (let i = 0; i < chars.length; i++) {
      let value = CHARSET.indexOf(chars[i]);
      if (i % 2 === 0) {
        value *= 2;
        if (value >= 32) {
          value = (value % 32) + Math.floor(value / 32);
        }
      }
      sum += value;
    }

    // Generate 4-character checksum
    const checksum = [];
    let remaining = (Math.pow(32, 4) - (sum % Math.pow(32, 4))) % Math.pow(32, 4);

    for (let i = 0; i < 4; i++) {
      checksum.unshift(CHARSET[remaining % 32]);
      remaining = Math.floor(remaining / 32);
    }

    return checksum.join('');
  }

  /**
   * Format key with dashes
   */
  formatKey(key) {
    return key.match(/.{4}/g).join('-');
  }

  /**
   * Validate a license key format and checksum
   */
  validate(key) {
    // Remove dashes
    const cleanKey = key.replace(/-/g, '');

    // Check length
    if (cleanKey.length !== KEY_LENGTH) {
      return { valid: false, error: 'Invalid length' };
    }

    // Check characters
    if (![...cleanKey].every(c => CHARSET.includes(c))) {
      return { valid: false, error: 'Invalid characters' };
    }

    // Verify checksum
    const keyWithoutChecksum = cleanKey.slice(0, -4);
    const providedChecksum = cleanKey.slice(-4);
    const calculatedChecksum = this.calculateChecksum(keyWithoutChecksum);

    if (providedChecksum !== calculatedChecksum) {
      return { valid: false, error: 'Invalid checksum' };
    }

    return { valid: true };
  }

  /**
   * Hash a license key for storage
   */
  hash(key) {
    return crypto
      .createHash('sha256')
      .update(key.replace(/-/g, '') + this.salt)
      .digest('hex');
  }

  /**
   * Mask a license key for display
   */
  mask(key) {
    const parts = key.split('-');
    return `${parts[0]}-****-****-${parts[3]}`;
  }
}

module.exports = LicenseKeyGenerator;

// Usage:
// const generator = new LicenseKeyGenerator('my-secret-salt');
// const key = generator.generate('premium'); // PM25-A3KM-X7PQ-BCDE
// const isValid = generator.validate(key);   // { valid: true }
// const hashed = generator.hash(key);        // sha256 hash
// const masked = generator.mask(key);        // PM25-****-****-BCDE
```

### Express.js License Server Routes

```javascript
// /license-server/routes/licenses.js

const express = require('express');
const router = express.Router();
const { Pool } = require('pg');
const jwt = require('jsonwebtoken');
const LicenseKeyGenerator = require('../utils/keyGenerator');

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const generator = new LicenseKeyGenerator();

/**
 * POST /api/v1/licenses/validate
 * Validate a license key (without activating)
 */
router.post('/validate', async (req, res) => {
  const { license_key } = req.body;

  // Format validation
  const formatCheck = generator.validate(license_key);
  if (!formatCheck.valid) {
    return res.status(400).json({
      valid: false,
      error: { code: 'INVALID_FORMAT', message: formatCheck.error }
    });
  }

  // Database lookup
  const keyHash = generator.hash(license_key);
  const result = await pool.query(
    `SELECT l.*,
            COUNT(a.id) FILTER (WHERE a.is_active) as active_count
     FROM licenses l
     LEFT JOIN activations a ON l.id = a.license_id
     WHERE l.license_key_hash = $1
     GROUP BY l.id`,
    [keyHash]
  );

  if (result.rows.length === 0) {
    return res.status(404).json({
      valid: false,
      error: { code: 'KEY_NOT_FOUND', message: 'License key not found' }
    });
  }

  const license = result.rows[0];

  // Check status
  if (!license.is_active) {
    return res.status(403).json({
      valid: false,
      error: { code: 'KEY_REVOKED', message: 'License has been revoked' }
    });
  }

  if (license.expires_at && new Date(license.expires_at) < new Date()) {
    return res.status(403).json({
      valid: false,
      error: { code: 'KEY_EXPIRED', message: 'License has expired' }
    });
  }

  // Get features for this license type
  const features = await getFeatures(license.type);

  res.json({
    valid: true,
    license: {
      type: license.type,
      holder_name: license.organization || license.name,
      max_activations: license.max_activations,
      current_activations: parseInt(license.active_count),
      expires_at: license.expires_at,
      features
    }
  });
});

/**
 * POST /api/v1/licenses/activate
 * Activate a license for a domain
 */
router.post('/activate', async (req, res) => {
  const { license_key, domain, ip_address, server_info, installer_version } = req.body;

  const client = await pool.connect();

  try {
    await client.query('BEGIN');

    // Get license
    const keyHash = generator.hash(license_key);
    const licenseResult = await client.query(
      `SELECT l.*,
              COUNT(a.id) FILTER (WHERE a.is_active) as active_count
       FROM licenses l
       LEFT JOIN activations a ON l.id = a.license_id
       WHERE l.license_key_hash = $1
       GROUP BY l.id
       FOR UPDATE`,
      [keyHash]
    );

    if (licenseResult.rows.length === 0) {
      await client.query('ROLLBACK');
      return res.status(404).json({
        success: false,
        error: { code: 'KEY_NOT_FOUND', message: 'License key not found' }
      });
    }

    const license = licenseResult.rows[0];

    // Validation checks
    if (!license.is_active) {
      await client.query('ROLLBACK');
      return res.status(403).json({
        success: false,
        error: { code: 'KEY_REVOKED', message: 'License has been revoked' }
      });
    }

    if (license.expires_at && new Date(license.expires_at) < new Date()) {
      await client.query('ROLLBACK');
      return res.status(403).json({
        success: false,
        error: { code: 'KEY_EXPIRED', message: 'License has expired' }
      });
    }

    // Check activation limit
    if (parseInt(license.active_count) >= license.max_activations) {
      // Check if same domain is being re-activated
      const existingActivation = await client.query(
        `SELECT id FROM activations
         WHERE license_id = $1 AND domain = $2 AND is_active = true`,
        [license.id, domain]
      );

      if (existingActivation.rows.length === 0) {
        await client.query('ROLLBACK');
        return res.status(403).json({
          success: false,
          error: {
            code: 'MAX_ACTIVATIONS',
            message: `Maximum activations (${license.max_activations}) reached`
          }
        });
      }
    }

    // Get features
    const features = await getFeatures(license.type);

    // Generate activation token
    const activationId = require('uuid').v4();
    const token = jwt.sign({
      iss: 'license.churchlms.com',
      sub: activationId,
      aud: domain,
      exp: license.expires_at
        ? Math.floor(new Date(license.expires_at).getTime() / 1000)
        : Math.floor(Date.now() / 1000) + (365 * 24 * 60 * 60), // 1 year if no expiry
      iat: Math.floor(Date.now() / 1000),
      lid: license.id,
      type: license.type,
      features
    }, process.env.JWT_SECRET);

    // Create or update activation
    await client.query(
      `INSERT INTO activations (id, license_id, activation_token, token_hash, domain, ip_address, server_info, lms_version, installer_version)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
       ON CONFLICT (license_id, domain)
       DO UPDATE SET
         activation_token = EXCLUDED.activation_token,
         token_hash = EXCLUDED.token_hash,
         ip_address = EXCLUDED.ip_address,
         server_info = EXCLUDED.server_info,
         is_active = true,
         deactivated_at = NULL,
         last_validated = NOW()`,
      [
        activationId,
        license.id,
        token,
        require('crypto').createHash('sha256').update(token).digest('hex'),
        domain,
        ip_address,
        JSON.stringify(server_info),
        server_info?.lms_version,
        installer_version
      ]
    );

    // Log the activation
    await client.query(
      `INSERT INTO validation_logs (activation_id, license_id, request_type, ip_address, success, request_data)
       VALUES ($1, $2, 'activate', $3, true, $4)`,
      [activationId, license.id, ip_address, JSON.stringify({ domain, server_info })]
    );

    await client.query('COMMIT');

    res.status(201).json({
      success: true,
      activation: {
        id: activationId,
        token,
        domain,
        activated_at: new Date().toISOString()
      },
      license: {
        type: license.type,
        expires_at: license.expires_at,
        features,
        support_level: getSupportLevel(license.type)
      },
      validation: {
        interval_days: 30,
        grace_period_days: 7,
        next_check: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
      }
    });

  } catch (error) {
    await client.query('ROLLBACK');
    console.error('Activation error:', error);
    res.status(500).json({
      success: false,
      error: { code: 'SERVER_ERROR', message: 'Internal server error' }
    });
  } finally {
    client.release();
  }
});

/**
 * POST /api/v1/licenses/heartbeat
 * Periodic validation check from installations
 */
router.post('/heartbeat', async (req, res) => {
  const { activation_token, lms_version, stats } = req.body;

  try {
    // Verify token
    const decoded = jwt.verify(activation_token, process.env.JWT_SECRET);

    // Update activation record
    await pool.query(
      `UPDATE activations
       SET last_validated = NOW(),
           last_heartbeat = NOW(),
           validation_count = validation_count + 1,
           lms_version = COALESCE($1, lms_version)
       WHERE id = $2 AND is_active = true`,
      [lms_version, decoded.sub]
    );

    // Log heartbeat
    await pool.query(
      `INSERT INTO validation_logs (activation_id, license_id, request_type, success, request_data)
       VALUES ($1, $2, 'heartbeat', true, $3)`,
      [decoded.sub, decoded.lid, JSON.stringify({ lms_version, stats })]
    );

    // Check for updates
    const updates = await checkForUpdates(lms_version);

    res.json({
      valid: true,
      license_status: 'active',
      features: decoded.features,
      updates,
      next_heartbeat: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
    });

  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        valid: false,
        error: { code: 'TOKEN_EXPIRED', message: 'Activation token has expired' }
      });
    }

    res.status(401).json({
      valid: false,
      error: { code: 'INVALID_TOKEN', message: 'Invalid activation token' }
    });
  }
});

// Helper functions
async function getFeatures(licenseType) {
  const result = await pool.query(
    `SELECT feature_key FROM feature_flags
     WHERE is_enabled = true AND available_in ? $1`,
    [licenseType]
  );
  return result.rows.map(r => r.feature_key);
}

function getSupportLevel(type) {
  const levels = {
    trial: 'community',
    standard: 'email',
    premium: 'priority',
    developer: 'priority'
  };
  return levels[type] || 'email';
}

async function checkForUpdates(currentVersion) {
  // In production, this would check a releases table
  const latestVersion = '1.3.0';
  const isNewer = compareVersions(latestVersion, currentVersion) > 0;

  return {
    available: isNewer,
    latest_version: latestVersion,
    release_notes_url: `https://churchlms.com/changelog/${latestVersion}`,
    severity: 'recommended'
  };
}

function compareVersions(a, b) {
  const pa = a.split('.').map(Number);
  const pb = b.split('.').map(Number);
  for (let i = 0; i < 3; i++) {
    if (pa[i] > pb[i]) return 1;
    if (pa[i] < pb[i]) return -1;
  }
  return 0;
}

module.exports = router;
```

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| Activation | Process of registering a license to a specific domain/installation |
| Activation Token | JWT token stored locally that proves valid activation |
| Grace Period | Time allowed for offline operation before restrictions apply |
| Heartbeat | Periodic check-in from installation to license server |
| License Key | Unique identifier purchased by customer to enable software |

## Appendix B: Error Codes Reference

| Code | HTTP | Description | Resolution |
|------|------|-------------|------------|
| `INVALID_FORMAT` | 400 | Key format doesn't match pattern | Check for typos |
| `INVALID_CHECKSUM` | 400 | Key checksum validation failed | Verify key is correct |
| `KEY_NOT_FOUND` | 404 | Key not in database | Check purchase email |
| `KEY_EXPIRED` | 403 | License past expiry date | Renew license |
| `KEY_REVOKED` | 403 | License manually revoked | Contact support |
| `MAX_ACTIVATIONS` | 403 | All activation slots used | Deactivate or upgrade |
| `TOKEN_EXPIRED` | 401 | Activation token expired | Re-activate |
| `RATE_LIMITED` | 429 | Too many requests | Wait and retry |
| `SERVER_ERROR` | 500 | Internal error | Retry later |

---

*Document Version: 1.0*
*Last Updated: January 11, 2026*
*Author: Church LMS Development Team*
