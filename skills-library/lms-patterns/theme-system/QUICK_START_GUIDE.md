# Theme System Quick Start Guide

## For Theme Users (Administrators)

### Installing a Theme

#### Method 1: Upload ZIP File
1. Go to Admin Panel → Themes
2. Click "Upload Theme"
3. Select your theme ZIP file
4. Click "Install"
5. Wait for validation to complete
6. Click "Activate" when ready

#### Method 2: Install from Marketplace
1. Go to Admin Panel → Themes → Marketplace
2. Browse available themes
3. Click "Preview" to see theme in action
4. Click "Install" on your chosen theme
5. Click "Activate" after installation

### Customizing Your Theme

1. Go to Admin Panel → Themes → Customize
2. Use the sidebar to change:
   - **Colors:** Primary, secondary, accent colors
   - **Typography:** Fonts, sizes, line heights
   - **Layout:** Container width, header style, spacing
   - **Branding:** Logo, favicon, site name
3. See changes live in the preview pane
4. Click "Save Changes" when satisfied
5. Click "Reset to Defaults" to undo all changes

### Switching Themes

1. Go to Admin Panel → Themes
2. Click "Preview" on any theme to see it first
3. Click "Activate" to switch immediately
4. Your customizations will be saved per-theme
5. Switch back anytime with zero data loss

---

## For Theme Developers

### Creating Your First Theme

#### Step 1: Install CLI Tool
```bash
npm install -g @lms-themes/create-theme
```

#### Step 2: Generate Theme
```bash
npx create-lms-theme my-awesome-theme
```

Follow the prompts:
- Theme name: **My Awesome Theme**
- Slug: **my-awesome-theme**
- Description: **A beautiful theme for educational platforms**
- Template: **Modern** (or Blank/Classic)
- TypeScript: **No** (or Yes)
- Parent theme: *(leave empty for standalone)*

#### Step 3: Navigate to Theme Directory
```bash
cd my-awesome-theme
npm install
```

#### Step 4: Start Development Server
```bash
npm run dev
```

This will start Vite in watch mode with hot module replacement.

### Theme File Structure

```
my-awesome-theme/
├── theme.json              # Required: Theme metadata
├── screenshot.png          # Required: 1200x900px preview
├── README.md              # Recommended: Documentation
│
├── components/            # Component overrides
│   ├── layout/
│   │   ├── Header.jsx
│   │   └── Footer.jsx
│   └── common/
│       └── Button.jsx
│
├── styles/               # Theme styles
│   ├── theme.css        # Main stylesheet
│   └── variables.css    # CSS custom properties
│
└── assets/              # Static files
    ├── images/
    └── fonts/
```

### Creating Your First Component Override

#### 1. Override the Header

Create `components/layout/Header.jsx`:

```jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '@/context/ThemeContext';

const Header = () => {
  const { settings } = useTheme();

  return (
    <header className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            {settings.logo ? (
              <img
                src={settings.logo}
                alt={settings.site_name}
                className="h-12"
              />
            ) : (
              <span className="text-2xl font-bold text-primary-600">
                {settings.site_name}
              </span>
            )}
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-6">
            <Link to="/" className="text-gray-700 hover:text-primary-600">
              Home
            </Link>
            <Link to="/courses" className="text-gray-700 hover:text-primary-600">
              Courses
            </Link>
            <Link to="/about" className="text-gray-700 hover:text-primary-600">
              About
            </Link>
            <Link to="/contact" className="text-gray-700 hover:text-primary-600">
              Contact
            </Link>
          </nav>

          {/* CTA Button */}
          <Link
            to="/register"
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Header;
```

#### 2. Add Custom Styles

Create `styles/theme.css`:

```css
@import './variables.css';

/* Header Styles */
header {
  border-bottom: 2px solid var(--color-primary);
}

/* Custom Button Style */
.btn-primary {
  background: linear-gradient(
    135deg,
    var(--color-primary),
    var(--color-secondary)
  );
  box-shadow: 0 4px 6px rgba(var(--color-primary-rgb), 0.2);
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(var(--color-primary-rgb), 0.3);
}
```

#### 3. Define Theme Variables

Create `styles/variables.css`:

```css
:root {
  /* Colors */
  --color-primary: #4F46E5;
  --color-primary-rgb: 79, 70, 229;
  --color-secondary: #10B981;
  --color-accent: #F59E0B;

  /* Typography */
  --font-family-primary: 'Inter', system-ui, sans-serif;
  --font-size-base: 1rem;
  --line-height-base: 1.5;

  /* Spacing */
  --spacing-unit: 0.25rem;

  /* Layout */
  --container-max-width: 1280px;
  --header-height: 80px;
}
```

### Making Your Theme Customizable

#### Update `theme.json` with settings:

```json
{
  "name": "My Awesome Theme",
  "slug": "my-awesome-theme",
  "version": "1.0.0",
  "description": "A beautiful theme for educational platforms",

  "settings": {
    "colors": {
      "primary": {
        "type": "color",
        "default": "#4F46E5",
        "label": "Primary Color",
        "description": "Main brand color used throughout the theme"
      },
      "secondary": {
        "type": "color",
        "default": "#10B981",
        "label": "Secondary Color"
      }
    },
    "typography": {
      "fontFamily": {
        "type": "select",
        "default": "inter",
        "options": [
          { "value": "inter", "label": "Inter" },
          { "value": "poppins", "label": "Poppins" },
          { "value": "roboto", "label": "Roboto" }
        ],
        "label": "Font Family"
      }
    },
    "branding": {
      "logo": {
        "type": "image",
        "default": null,
        "label": "Logo",
        "description": "Upload your logo (recommended: 200x60px)"
      }
    }
  }
}
```

### Testing Your Theme

#### 1. Local Testing
```bash
npm run dev
```

Visit `http://localhost:5173` to see your theme in action.

#### 2. Validate Theme Structure
```bash
npm run validate
```

This checks:
- Required files exist
- `theme.json` is valid
- Components follow naming conventions
- No syntax errors

#### 3. Build for Production
```bash
npm run build
```

Creates optimized production bundle in `dist/` directory.

### Packaging Your Theme

#### 1. Create Distribution Package
```bash
npm run package
```

This creates `my-awesome-theme.zip` with:
- All theme files
- Optimized assets
- Minified CSS/JS
- README and documentation

#### 2. Test the Package
1. Upload ZIP to test LMS instance
2. Install and activate
3. Test all features
4. Verify customizer works
5. Check responsive design

### Publishing to Marketplace

#### 1. Prepare for Submission
- [ ] Add high-quality screenshot (1200x900px)
- [ ] Write comprehensive README
- [ ] Include changelog
- [ ] Add license file
- [ ] Test in multiple browsers
- [ ] Verify accessibility

#### 2. Submit Theme
1. Go to Theme Marketplace
2. Click "Submit Theme"
3. Upload your ZIP file
4. Fill in metadata
5. Submit for review

#### 3. Review Process
- Security scan: 1-2 days
- Code review: 3-5 days
- Design review: 2-3 days
- Total: ~1 week

---

## Best Practices

### Component Naming
- Use PascalCase: `Header.jsx`, `HeroSection.jsx`
- Group by category: `layout/`, `common/`, `pages/`
- One component per file

### Styling
- Use CSS variables for customizable values
- Leverage Tailwind utilities when possible
- Keep component styles scoped
- Use semantic class names

### Performance
- Lazy load heavy components
- Optimize images (use WebP)
- Minimize CSS/JS bundle size
- Test on slow connections

### Accessibility
- Use semantic HTML
- Add ARIA labels
- Ensure keyboard navigation
- Test with screen readers
- Maintain color contrast ratios

### Responsive Design
- Mobile-first approach
- Test on multiple devices
- Use Tailwind responsive classes
- Avoid fixed pixel widths

---

## Common Issues & Solutions

### Issue: Components Not Loading
**Solution:** Check file paths match exactly:
```javascript
// Correct
components/layout/Header.jsx

// Wrong
components/Layout/header.jsx
components/header.jsx
```

### Issue: Styles Not Applying
**Solution:** Ensure CSS is imported in `theme.json`:
```json
{
  "assets": {
    "styles": [
      "styles/theme.css"
    ]
  }
}
```

### Issue: Theme Not Appearing in Admin
**Solution:** Validate `theme.json` has required fields:
- `name`
- `slug`
- `version`

### Issue: Preview Not Working
**Solution:** Clear browser cache and theme cache:
```bash
# Server-side cache clear
npm run cache:clear

# Or restart dev server
npm run dev
```

---

## Getting Help

### Documentation
- Full Documentation: `/docs/theme-system/`
- API Reference: `/docs/theme-system/API.md`
- Examples: `/themes/examples/`

### Community
- Forum: https://community.lms.example.com
- Discord: https://discord.gg/lms-themes
- GitHub: https://github.com/lms/themes

### Support
- Email: themes@lms.example.com
- Issue Tracker: https://github.com/lms/themes/issues

---

## Next Steps

1. **Study Example Themes**
   - Browse `/themes/examples/`
   - Check out community themes
   - Analyze code patterns

2. **Build Your First Theme**
   - Start with a simple override
   - Gradually add features
   - Test thoroughly

3. **Join the Community**
   - Share your progress
   - Get feedback
   - Help other developers

4. **Publish Your Theme**
   - Polish your work
   - Submit to marketplace
   - Earn from premium themes

Happy theme building! 🎨
