# License Key System for SaaS Applications

## Overview
A tiered license key system that gates features based on subscription level. Keys are validated server-side with optional offline capability.

## Key Format
```
XXXX-XXXX-XXXX-XXXX
```
- 16 alphanumeric characters in 4 groups
- First character encodes tier (S=Starter, P=Professional, E=Enterprise, U=Ultimate)
- Includes checksum for basic validation

## Implementation

### Key Generation (server/utils/license.js)
```javascript
const crypto = require('crypto');

const TIERS = {
  STARTER: { prefix: 'S', features: ['basic_courses', 'max_users_50'] },
  PROFESSIONAL: { prefix: 'P', features: ['all_courses', 'max_users_500', 'analytics'] },
  ENTERPRISE: { prefix: 'E', features: ['all_courses', 'unlimited_users', 'api_access'] },
  ULTIMATE: { prefix: 'U', features: ['everything', 'white_label', 'priority_support'] }
};

function generateLicenseKey(tier, metadata = {}) {
  const tierInfo = TIERS[tier.toUpperCase()];
  const prefix = tierInfo.prefix;

  // Generate random parts
  const part1 = prefix + crypto.randomBytes(2).toString('hex').toUpperCase().slice(0, 3);
  const part2 = crypto.randomBytes(2).toString('hex').toUpperCase();
  const part3 = crypto.randomBytes(2).toString('hex').toUpperCase();

  // Checksum for last part
  const checksum = calculateChecksum(part1 + part2 + part3);
  const part4 = checksum.slice(0, 4);

  return `${part1}-${part2}-${part3}-${part4}`;
}

function validateLicenseKey(key) {
  const parts = key.split('-');
  if (parts.length !== 4) return { valid: false, error: 'Invalid format' };

  const tierPrefix = parts[0][0];
  const tier = Object.entries(TIERS).find(([, v]) => v.prefix === tierPrefix);

  if (!tier) return { valid: false, error: 'Invalid tier' };

  // Verify checksum
  const baseString = parts.slice(0, 3).join('');
  const expectedChecksum = calculateChecksum(baseString).slice(0, 4);

  if (parts[3] !== expectedChecksum) {
    return { valid: false, error: 'Invalid checksum' };
  }

  return {
    valid: true,
    tier: tier[0],
    features: tier[1].features
  };
}
```

### Feature Gating (server/utils/licenseFeatures.js)
```javascript
const FEATURE_REQUIREMENTS = {
  'video_hosting': ['PROFESSIONAL', 'ENTERPRISE', 'ULTIMATE'],
  'api_access': ['ENTERPRISE', 'ULTIMATE'],
  'white_label': ['ULTIMATE'],
  'analytics_dashboard': ['PROFESSIONAL', 'ENTERPRISE', 'ULTIMATE'],
  'bulk_enrollment': ['ENTERPRISE', 'ULTIMATE'],
  'custom_certificates': ['PROFESSIONAL', 'ENTERPRISE', 'ULTIMATE'],
  'multi_instructor': ['ENTERPRISE', 'ULTIMATE']
};

function hasFeature(tier, feature) {
  const requiredTiers = FEATURE_REQUIREMENTS[feature];
  if (!requiredTiers) return true; // Feature not gated
  return requiredTiers.includes(tier);
}

function getEnabledFeatures(tier) {
  return Object.entries(FEATURE_REQUIREMENTS)
    .filter(([, tiers]) => tiers.includes(tier))
    .map(([feature]) => feature);
}
```

### Middleware (server/middleware/licenseCheck.js)
```javascript
const { validateLicenseKey, hasFeature } = require('../utils/license');

function requireLicense(requiredFeature = null) {
  return async (req, res, next) => {
    const settings = await getSettings();
    const licenseKey = settings.license_key;

    if (!licenseKey) {
      return res.status(403).json({
        error: 'License required',
        code: 'NO_LICENSE'
      });
    }

    const validation = validateLicenseKey(licenseKey);

    if (!validation.valid) {
      return res.status(403).json({
        error: 'Invalid license',
        code: 'INVALID_LICENSE'
      });
    }

    if (requiredFeature && !hasFeature(validation.tier, requiredFeature)) {
      return res.status(403).json({
        error: `Feature requires ${requiredFeature}`,
        code: 'FEATURE_NOT_AVAILABLE',
        currentTier: validation.tier
      });
    }

    req.license = validation;
    next();
  };
}
```

### API Routes (server/routes/licenseRoutes.js)
```javascript
router.post('/validate', async (req, res) => {
  const { licenseKey } = req.body;
  const result = validateLicenseKey(licenseKey);

  if (result.valid) {
    // Store in settings
    await updateSetting('license_key', licenseKey);
    await updateSetting('license_tier', result.tier);
  }

  res.json(result);
});

router.get('/features', requireLicense(), (req, res) => {
  res.json({
    tier: req.license.tier,
    features: req.license.features,
    enabled: getEnabledFeatures(req.license.tier)
  });
});
```

## Usage in Installer

### Step 3: License Validation
```php
<div class="license-input">
    <input type="text" name="license_key" id="license_key"
           placeholder="XXXX-XXXX-XXXX-XXXX"
           pattern="[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}">
    <button type="button" onclick="validateLicense()">Validate</button>
</div>

<script>
async function validateLicense() {
    const key = document.getElementById('license_key').value;
    const response = await fetch('/api/license/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ licenseKey: key })
    });
    const result = await response.json();

    if (result.valid) {
        showSuccess(`License valid! Tier: ${result.tier}`);
        enableContinue();
    } else {
        showError(result.error);
    }
}
</script>
```

## Tier Comparison

| Feature | Starter | Pro | Enterprise | Ultimate |
|---------|---------|-----|------------|----------|
| Max Users | 50 | 500 | Unlimited | Unlimited |
| Courses | 10 | 100 | Unlimited | Unlimited |
| Video Hosting | No | Yes | Yes | Yes |
| Analytics | Basic | Full | Full | Full |
| API Access | No | No | Yes | Yes |
| White Label | No | No | No | Yes |
| Custom Domain | No | Yes | Yes | Yes |
| Priority Support | No | No | Yes | Yes |

## Security Considerations

1. **Server-side validation** - Never trust client-only validation
2. **Rate limiting** - Prevent brute-force key guessing
3. **Key rotation** - Allow key updates without reinstall
4. **Offline grace period** - Allow temporary offline operation
5. **Audit logging** - Track license validation attempts
