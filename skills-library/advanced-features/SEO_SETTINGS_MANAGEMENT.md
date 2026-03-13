# SEO Settings Management System

**Skill Type:** Admin Feature Implementation
**Difficulty:** ⭐⭐ Medium
**Last Updated:** January 9, 2026
**Project:** MERN Community LMS

---

## Overview

Complete implementation guide for adding SEO and metadata management to an admin settings page. This skill covers dynamic meta tags, Open Graph settings, Twitter Cards, favicon management, and social share previews.

---

## Problem Solved

**Original Issue:** Browser tab title was hardcoded as "Melchizedek Priests Ministry" in `client/index.html`, ignoring the site name configured in the database.

**Full Solution:** Implemented a complete SEO management system allowing admins to edit:
- Page title and meta description
- Open Graph tags (Facebook/LinkedIn sharing)
- Twitter Card settings
- Favicon
- Site verification codes (Google, Bing)
- Live social share preview

---

## Architecture

### Data Flow
```
Database (site_settings table)
    ↓
API (/api/settings)
    ↓
ThemeContext (global state)
    ↓
MainLayout (react-helmet-async)
    ↓
Browser <head> tags
```

### Files Modified

| File | Purpose | Changes |
|------|---------|---------|
| `server/migrations/075_add_seo_settings.sql` | Database migration | Add 17 SEO fields |
| `server/controllers/siteSettingsController.js` | API controller | Add SEO field metadata |
| `client/src/context/ThemeContext.jsx` | Global state | Add SEO defaults |
| `client/src/layouts/MainLayout.jsx` | Meta tag rendering | Dynamic Helmet tags |
| `client/src/pages/admin/Settings.jsx` | Admin UI | SEO settings tab |
| `client/index.html` | Initial HTML | Placeholder title |

---

## Implementation Details

### 1. Database Migration

```sql
-- server/migrations/075_add_seo_settings.sql
INSERT INTO site_settings (setting_key, setting_value, setting_type, category, display_name, description) VALUES
  -- Basic SEO
  ('meta_title', 'School of the Priests', 'text', 'seo', 'Meta Title', 'Page title shown in browser tabs and search results'),
  ('meta_description', 'Join our spiritual community...', 'text', 'seo', 'Meta Description', 'Description for search engines'),
  ('meta_keywords', 'bible study, christian courses...', 'text', 'seo', 'Meta Keywords', 'Keywords for SEO'),

  -- Open Graph (Facebook/LinkedIn)
  ('og_title', 'School of the Priests', 'text', 'seo', 'OG Title', 'Title for social media shares'),
  ('og_description', 'Join our spiritual community...', 'text', 'seo', 'OG Description', 'Description for social shares'),
  ('og_image', '', 'text', 'seo', 'OG Image', 'Image URL (1200x630px recommended)'),
  ('og_type', 'website', 'text', 'seo', 'OG Type', 'Content type'),
  ('og_site_name', 'School of the Priests', 'text', 'seo', 'OG Site Name', 'Site name for social sharing'),

  -- Twitter Card
  ('twitter_card', 'summary_large_image', 'text', 'seo', 'Twitter Card Type', 'summary or summary_large_image'),
  ('twitter_title', 'School of the Priests', 'text', 'seo', 'Twitter Title', 'Title for Twitter shares'),
  ('twitter_description', 'Join our spiritual community...', 'text', 'seo', 'Twitter Description', 'Description for Twitter'),
  ('twitter_image', '', 'text', 'seo', 'Twitter Image', 'Image for Twitter (1200x600px)'),
  ('twitter_handle', '', 'text', 'seo', 'Twitter Handle', '@yourhandle'),

  -- Additional
  ('canonical_url', '', 'text', 'seo', 'Canonical URL', 'Primary site URL'),
  ('google_site_verification', '', 'text', 'seo', 'Google Verification', 'Google Search Console code'),
  ('bing_site_verification', '', 'text', 'seo', 'Bing Verification', 'Bing Webmaster code'),
  ('organization_name', 'School of the Priests', 'text', 'seo', 'Organization Name', 'For structured data')
ON CONFLICT (setting_key) DO NOTHING;
```

### 2. ThemeContext Defaults

```jsx
// client/src/context/ThemeContext.jsx
const [settings, setSettings] = useState({
  // Branding
  site_name: 'School of the Priests',
  site_tagline: 'Ministry',
  favicon: '/favicon.ico',

  // SEO - Basic
  meta_title: 'School of the Priests',
  meta_description: 'Join our spiritual community...',
  meta_keywords: 'bible study, christian courses...',

  // SEO - Open Graph
  og_title: 'School of the Priests',
  og_description: 'Join our spiritual community...',
  og_image: '',
  og_type: 'website',
  og_site_name: 'School of the Priests',

  // SEO - Twitter Card
  twitter_card: 'summary_large_image',
  twitter_title: 'School of the Priests',
  twitter_description: 'Join our spiritual community...',
  twitter_image: '',
  twitter_handle: '',

  // SEO - Additional
  canonical_url: '',
  google_site_verification: '',
  bing_site_verification: '',
  organization_name: 'School of the Priests'
});
```

### 3. MainLayout Dynamic Meta Tags

```jsx
// client/src/layouts/MainLayout.jsx
import { useTheme } from '../context/ThemeContext';
import { Helmet } from 'react-helmet-async';

const MainLayout = ({ children }) => {
  const { settings } = useTheme();

  // Build title with tagline
  const pageTitle = settings.site_tagline
    ? `${settings.meta_title || settings.site_name} - ${settings.site_tagline}`
    : (settings.meta_title || settings.site_name);

  return (
    <>
      <Helmet>
        {/* Basic Meta Tags */}
        <title>{pageTitle}</title>
        <meta name="description" content={settings.meta_description} />
        <meta name="keywords" content={settings.meta_keywords} />

        {/* Open Graph */}
        <meta property="og:type" content={settings.og_type || 'website'} />
        <meta property="og:title" content={settings.og_title || settings.site_name} />
        <meta property="og:description" content={settings.og_description || settings.meta_description} />
        <meta property="og:site_name" content={settings.og_site_name || settings.site_name} />
        {settings.og_image && <meta property="og:image" content={settings.og_image} />}
        {settings.canonical_url && <meta property="og:url" content={settings.canonical_url} />}

        {/* Twitter Card */}
        <meta name="twitter:card" content={settings.twitter_card || 'summary_large_image'} />
        <meta name="twitter:title" content={settings.twitter_title || settings.site_name} />
        <meta name="twitter:description" content={settings.twitter_description || settings.meta_description} />
        {settings.twitter_image && <meta name="twitter:image" content={settings.twitter_image} />}
        {settings.twitter_handle && <meta name="twitter:site" content={settings.twitter_handle} />}

        {/* Verification */}
        {settings.google_site_verification && (
          <meta name="google-site-verification" content={settings.google_site_verification} />
        )}
        {settings.bing_site_verification && (
          <meta name="msvalidate.01" content={settings.bing_site_verification} />
        )}

        {/* Canonical & Favicon */}
        {settings.canonical_url && <link rel="canonical" href={settings.canonical_url} />}
        {settings.favicon && <link rel="icon" href={settings.favicon} />}
      </Helmet>

      {/* Rest of layout */}
    </>
  );
};
```

### 4. Admin Settings SEO Tab

Key features of the SEO settings UI:

```jsx
// Settings tab configuration
const tabs = [
  { id: 'general', label: 'General', icon: 'cog' },
  { id: 'seo', label: 'SEO', icon: 'search' },
  // ... other tabs
];

// Fields to save per section
const settingsToSave = {
  seo: [
    'meta_title', 'meta_description', 'meta_keywords',
    'og_title', 'og_description', 'og_image', 'og_site_name',
    'twitter_card', 'twitter_title', 'twitter_description',
    'twitter_image', 'twitter_handle',
    'canonical_url', 'google_site_verification',
    'bing_site_verification', 'organization_name', 'favicon'
  ],
};
```

### 5. Social Share Preview Component

```jsx
{/* Social Share Preview */}
<div className="border-t border-gray-200 pt-8">
  <h3 className="text-lg font-medium text-gray-900 mb-4">Social Share Preview</h3>
  <div className="bg-gray-100 rounded-lg p-4">
    <div className="bg-white rounded-lg shadow-sm overflow-hidden max-w-md">
      <div className="h-52 bg-gray-200 relative">
        {settings.og_image ? (
          <img
            src={settings.og_image}
            alt="OG Preview"
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div
          className="absolute inset-0 flex flex-col items-center justify-center text-gray-400"
          style={{ display: settings.og_image ? 'none' : 'flex' }}
        >
          <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586..." />
          </svg>
          <span className="text-sm">
            {settings.og_image ? 'Image failed to load' : 'No OG image set'}
          </span>
        </div>
      </div>
      <div className="p-4">
        <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">
          {(() => {
            try {
              return settings.canonical_url ? new URL(settings.canonical_url).hostname : 'yoursite.com';
            } catch {
              return 'yoursite.com';
            }
          })()}
        </p>
        <h4 className="font-semibold text-gray-900 mb-1">
          {settings.og_title || settings.meta_title || 'Your Page Title'}
        </h4>
        <p className="text-sm text-gray-600 line-clamp-2">
          {settings.og_description || settings.meta_description || 'Your page description...'}
        </p>
      </div>
    </div>
  </div>
</div>
```

---

## Common Issues & Solutions

### Issue 1: Auth Token Key Mismatch

**Problem:** Settings save failed with "Failed to save meta_title"

**Cause:** Code used `localStorage.getItem('jwt')` but app stores token as `'token'`

**Fix:**
```jsx
// Wrong
'Authorization': `Bearer ${localStorage.getItem('jwt')}`

// Correct
'Authorization': `Bearer ${localStorage.getItem('token')}`
```

### Issue 2: Preview Images Not Loading

**Problem:** Social share preview shows blank gray box

**Causes:**
1. `og_image` field is empty
2. Image path is incorrect
3. Server not serving `/uploads` directory
4. Vite proxy not configured for `/uploads`

**Vite Config:**
```javascript
// client/vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true
  },
  '/uploads': {
    target: 'http://localhost:5000',
    changeOrigin: true
  }
}
```

### Issue 3: URL Parsing Errors

**Problem:** `new URL(invalid_string).hostname` throws error

**Fix:** Wrap in try/catch
```jsx
{(() => {
  try {
    return settings.canonical_url ? new URL(settings.canonical_url).hostname : 'yoursite.com';
  } catch {
    return 'yoursite.com';
  }
})()}
```

---

## Image Path Reference

For OG images and favicon, use paths like:
```
/uploads/media/your-image.png
```

The server serves static files from `server/uploads/` directory:
```javascript
// server/server.js
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
```

---

## Testing Checklist

- [ ] SEO tab appears in admin settings
- [ ] Meta title saves and appears in browser tab
- [ ] Meta description saves and appears in page source
- [ ] OG image preview shows in social share preview
- [ ] Favicon preview shows next to input
- [ ] Favicon appears in browser tab
- [ ] Google/Bing verification codes save
- [ ] Settings persist after page refresh
- [ ] Error handling shows user-friendly messages

---

## Dependencies

- `react-helmet-async` - Dynamic meta tag management
- `axios` - API calls (with token interceptor)

---

## Related Skills

- `PUCK_PAGE_TEMPLATES_SYSTEM.md` - Visual page builder
- `HOME_PAGE_BUILDER_GUIDE.md` - Puck setup
- `ADMIN_PRODUCTS_GUIDE.md` - Admin UI patterns

---

**Created:** January 9, 2026
**Session:** SEO Settings Management Implementation
**Author:** Claude Code (Opus 4.5)
