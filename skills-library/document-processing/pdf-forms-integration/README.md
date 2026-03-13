# PDF Forms Integration Skill

## Overview
Complete guide to integrating official fillable PDF forms (especially GTA forms) into web applications. This skill teaches the hybrid approach of using pdf-lib for programmatic field filling combined with native browser PDF editing for the best user experience.

## What's Inside
- **SKILL.md** - Complete implementation guide with code examples, field mapping strategies, and production-ready components

## Key Topics
1. **AcroForm Fields** - Understanding PDF interactive form fields and field naming conventions
2. **PDF Field Inspector** - Tool to discover actual field names in official PDFs
3. **Field Mapping System** - Mapping application fields to cryptic PDF field names
4. **pdf-lib Integration** - Programmatic PDF manipulation and field filling
5. **Hybrid Workflow** - Combining programmatic filling with native browser editing
6. **UI Components** - React components for PDF preview, editing, and download
7. **GTA Forms Integration** - Specific guidance for Form 656, 433-A, 433-B
8. **Error Handling** - Common issues and solutions for PDF integration

## When to Use This Skill
- **Integrating official forms** - GTA forms, government documents, legal forms
- **Auto-populating PDFs** - Fill form fields programmatically from user data
- **Field mapping challenges** - Discovering and mapping cryptic PDF field names
- **Browser-based editing** - Allow users to edit PDFs without custom UI
- **Compliance requirements** - Using official PDFs without modification
- **Download workflows** - Generating submission-ready PDFs

## Core Concepts
✅ **AcroForm fields** - Interactive PDF form fields with cryptic names like `topmostSubform[0].Page1[0].f1_01[0]`
✅ **pdf-lib for filling** - Use pdf-lib to programmatically pre-fill form fields
✅ **Native browser editing** - Let browsers handle PDF editing natively (no custom UI needed)
✅ **Hybrid approach** - Pre-fill → Display in iframe → User edits → Download
✅ **Field inspection** - Must inspect PDFs to discover actual field names
✅ **Field mapping** - Map application field names to PDF field names with optional formatters
✅ **Legal compliance** - Use official PDFs only, don't modify structure

## Implementation Phases
**Phase 1**: Download and store official PDFs in `public/irs-forms/`
**Phase 2**: Create PDF field inspector utility
**Phase 3**: Create field mappings (app fields → PDF fields)
**Phase 4**: Implement PDF form filler with pdf-lib
**Phase 5**: Build UI component with preview and download
**Phase 6**: Test complete workflow

## Related Skills
- irs-tax-calculations
- react-i18next-internationalization
- critical-coding-patterns

## Technology Stack
- **pdf-lib** - PDF manipulation library
- **React** - UI framework
- **TypeScript** - Type safety
- **Native browser** - Built-in PDF viewer and editor

## Time Estimates
- **Single form integration**: 4-6 hours
- **Three forms integration**: 10-14 hours
- **Per form breakdown**:
  - Download PDFs: 5 min
  - Field inspection: 15 min
  - Field mapping: 1-2 hrs
  - Implementation: 2-3 hrs

## Success Criteria
- ✓ Official PDFs load without CORS errors
- ✓ Field inspector lists all PDF field names
- ✓ Field mappings complete for target forms
- ✓ Auto-populate fills PDF correctly
- ✓ Users can edit in native browser PDF viewer
- ✓ Download produces submission-ready PDF
- ✓ Tested with real user data

## Quick Start
```bash
# 1. Download official PDFs
mkdir -p public/irs-forms
curl -o public/irs-forms/f656.pdf https://www.irs.gov/pub/irs-pdf/f656.pdf

# 2. Inspect PDF fields
import { logPDFFields } from './utils/pdfFieldInspector';
await logPDFFields('/irs-forms/f656.pdf');

# 3. Create field mappings
// Update src/lib/irsFieldMappings.ts with actual field names

# 4. Implement PDF filler
// Use fillAndPreviewPDF() to fill and display

# 5. Test workflow
// Auto-populate → Preview → Edit → Download
```

## Common Issues
- **Field not found** → Inspect PDF to get correct field names
- **Fields not visible** → Call `form.updateFieldAppearances()`
- **Date format wrong** → Add format function in field mapping
- **CORS errors** → Store PDFs locally in `public/` folder

---

**Remember:** The hybrid approach (pdf-lib + native browser) provides the best balance of automation and user control for official form integration.
