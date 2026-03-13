# React i18next Setup Skill

## Purpose
Quick reference for setting up internationalization (i18n) in React projects using react-i18next. This skill documents the complete setup process for adding multi-language support to React applications.

## When to Use
- Adding multi-language support to a React application
- Setting up internationalization infrastructure from day 1
- Creating a scalable translation system

## Technology Stack
- `react-i18next` - React integration for i18next
- `i18next` - Core internationalization framework
- TypeScript support included

## Installation

```bash
npm install react-i18next i18next
```

## Setup Steps

### 1. Create i18n Configuration File

**File:** `src/i18n.ts`

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import translations
import enTranslations from './locales/en/common.json';
import esTranslations from './locales/es/common.json';

// Initialize i18next
i18n
  .use(initReactI18next) // Pass i18n instance to react-i18next
  .init({
    resources: {
      en: {
        common: enTranslations,
      },
      es: {
        common: esTranslations,
      },
    },
    lng: 'en', // Default language
    fallbackLng: 'en', // Fallback language if translation is missing
    defaultNS: 'common', // Default namespace
    interpolation: {
      escapeValue: false, // React already escapes by default
    },
    react: {
      useSuspense: false, // Disable suspense (optional)
    },
  });

export default i18n;
```

### 2. Initialize i18n in Application

**File:** `src/main.tsx` (or `src/index.tsx`)

```typescript
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import './i18n'; // Initialize i18n ← ADD THIS LINE

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

### 3. Create Translation Files

#### Folder Structure
```
src/
├── locales/
│   ├── en/
│   │   ├── common.json
│   │   └── feature1.json
│   └── es/
│       ├── common.json
│       └── feature1.json
```

#### English Translation Example
**File:** `src/locales/en/common.json`

```json
{
  "welcome": "Welcome",
  "greeting": "Hello, {{name}}!",
  "buttons": {
    "save": "Save",
    "cancel": "Cancel",
    "continue": "Continue"
  },
  "validation": {
    "required": "This field is required",
    "invalidEmail": "Please enter a valid email"
  }
}
```

#### Spanish Translation Example
**File:** `src/locales/es/common.json`

```json
{
  "welcome": "Bienvenido",
  "greeting": "¡Hola, {{name}}!",
  "buttons": {
    "save": "Guardar",
    "cancel": "Cancelar",
    "continue": "Continuar"
  },
  "validation": {
    "required": "Este campo es obligatorio",
    "invalidEmail": "Por favor ingrese un correo electrónico válido"
  }
}
```

### 4. Using Translations in Components

#### Basic Usage
```typescript
import { useTranslation } from 'react-i18next';

export function MyComponent() {
  const { t } = useTranslation('common');

  return (
    <div>
      <h1>{t('welcome')}</h1>
      <p>{t('greeting', { name: 'John' })}</p>
      <button>{t('buttons.save')}</button>
    </div>
  );
}
```

#### Using Multiple Namespaces
```typescript
import { useTranslation } from 'react-i18next';

export function MyFeature() {
  const { t: tCommon } = useTranslation('common');
  const { t: tFeature } = useTranslation('feature1');

  return (
    <div>
      <h1>{tFeature('title')}</h1>
      <button>{tCommon('buttons.save')}</button>
    </div>
  );
}
```

### 5. Language Switcher Component

```typescript
import { useTranslation } from 'react-i18next';

export function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('language', lng);
  };

  return (
    <div>
      <button
        onClick={() => changeLanguage('en')}
        className={i18n.language === 'en' ? 'active' : ''}
      >
        English
      </button>
      <button
        onClick={() => changeLanguage('es')}
        className={i18n.language === 'es' ? 'active' : ''}
      >
        Español
      </button>
    </div>
  );
}
```

### 6. Persist Language Preference

Add to `src/i18n.ts`:

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Get saved language or use default
const savedLanguage = localStorage.getItem('language') || 'en';

i18n
  .use(initReactI18next)
  .init({
    resources: { /* ... */ },
    lng: savedLanguage, // Use saved language
    fallbackLng: 'en',
    // ... rest of config
  });

export default i18n;
```

## Advanced Features

### TypeScript Support

Create type-safe translations:

```typescript
// src/types/i18n.d.ts
import 'react-i18next';
import type common from './locales/en/common.json';

declare module 'react-i18next' {
  interface CustomTypeOptions {
    defaultNS: 'common';
    resources: {
      common: typeof common;
    };
  }
}
```

### Pluralization

```json
{
  "items": "{{count}} item",
  "items_plural": "{{count}} items"
}
```

Usage:
```typescript
{t('items', { count: 1 })}  // "1 item"
{t('items', { count: 5 })}  // "5 items"
```

### Date and Number Formatting

```json
{
  "date": "{{date, datetime}}",
  "price": "{{value, currency(USD)}}"
}
```

## Best Practices

### 1. Organize by Feature
```
locales/
├── en/
│   ├── common.json          # Shared translations
│   ├── auth.json            # Authentication
│   ├── dashboard.json       # Dashboard
│   └── settings.json        # Settings
```

### 2. Use Nested Keys
```json
{
  "user": {
    "profile": {
      "title": "User Profile",
      "edit": "Edit Profile",
      "save": "Save Changes"
    }
  }
}
```

### 3. Keep Placeholder Translations
For languages not yet translated, use `[LANG]` prefix:
```json
{
  "title": "[ES] My Title"
}
```

### 4. Translation Key Naming
- Use camelCase or dot notation
- Be descriptive but concise
- Group related translations

```json
{
  "form": {
    "firstName": "First Name",
    "lastName": "Last Name",
    "email": "Email Address"
  },
  "validation": {
    "required": "{{field}} is required",
    "invalid": "Invalid {{field}}"
  }
}
```

### 5. Avoid Hardcoded Strings
❌ Bad:
```typescript
<button>Save</button>
```

✅ Good:
```typescript
<button>{t('buttons.save')}</button>
```

## Common Patterns

### Loading States
```typescript
const { t, ready } = useTranslation();

if (!ready) return <div>Loading translations...</div>;

return <div>{t('welcome')}</div>;
```

### Error Messages
```json
{
  "errors": {
    "network": "Network error occurred",
    "notFound": "{{resource}} not found",
    "unauthorized": "You are not authorized"
  }
}
```

### Form Validation
```json
{
  "validation": {
    "required": "{{field}} is required",
    "minLength": "{{field}} must be at least {{min}} characters",
    "maxLength": "{{field}} must be at most {{max}} characters",
    "email": "Please enter a valid email address"
  }
}
```

## Testing i18n

```typescript
import { render, screen } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';

test('renders translated text', () => {
  render(
    <I18nextProvider i18n={i18n}>
      <MyComponent />
    </I18nextProvider>
  );

  expect(screen.getByText('Welcome')).toBeInTheDocument();
});
```

## Troubleshooting

### Translations Not Loading
1. Check that i18n is imported in main.tsx/index.tsx
2. Verify JSON file paths are correct
3. Check browser console for errors

### Language Not Changing
1. Verify localStorage is working
2. Check that `i18n.changeLanguage()` is being called
3. Ensure component re-renders after language change

### TypeScript Errors
1. Make sure type definitions are in `types/i18n.d.ts`
2. Restart TypeScript server
3. Check that JSON imports are typed correctly

## Migration Strategy

When adding i18n to existing project:

1. **Phase 1:** Set up infrastructure (this guide)
2. **Phase 2:** Extract hardcoded English strings
3. **Phase 3:** Create translation JSON files
4. **Phase 4:** Replace hardcoded strings with `t()` calls
5. **Phase 5:** Add additional languages
6. **Phase 6:** Test all translations

## Resources

- Official Docs: https://react.i18next.com/
- i18next Docs: https://www.i18next.com/
- Translation Tools: https://locize.com/

## Example Projects

See the Form 656 Wizard implementation in BoltBudgetApp for a complete example:
- `src/i18n.ts` - Configuration
- `src/locales/en/form656.json` - English translations
- `src/locales/es/form656.json` - Spanish translations
- `src/components/Form656Wizard/` - Usage examples

---

**Last Updated:** 2025-10-28
**Tested With:** react-i18next v13.x, i18next v23.x
**Project:** BoltBudgetApp - Form 656 Wizard
