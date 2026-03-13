---
name: "pdf-forms-integration"
description: "Complete guide to integrating official fillable PDF forms (especially GTA forms) into web applications. Covers AcroForm field mapping, pdf-lib usage, field inspection, and hybrid browser-native editing workflow."
---

# PDF Forms Integration Skill

**Purpose**: Guide Claude in integrating official fillable PDF forms (especially GTA forms) into web applications

**Use Cases**:
- Integrating official GTA PDF forms (Form 656, 433-A, 433-B, etc.)
- Auto-populating AcroForm fields from user data
- Allowing users to manually edit PDFs in browser
- Downloading filled PDFs for submission

**Key Technologies**: pdf-lib, PDF.js, React, TypeScript

---

## Overview

This skill helps integrate official PDF forms (with AcroForm fields) into web applications, enabling:
1. Loading official PDFs from GTA or other sources
2. Auto-populating form fields programmatically
3. Allowing users to edit fields directly in the PDF
4. Downloading the completed PDF

---

## Core Concepts

### AcroForm Fields
- **What**: Interactive form fields embedded in PDFs
- **Types**: Text fields, checkboxes, radio buttons, dropdowns
- **Field Names**: Cryptic identifiers like `topmostSubform[0].Page1[0].f1_01[0]`
- **Browser Support**: Chrome, Firefox, Edge, Safari all support editing AcroForms

### pdf-lib Library
- **Best For**: Programmatic PDF manipulation (filling fields, generating PDFs)
- **NOT For**: Interactive editing in browser (use native browser support)
- **Use Cases**: Pre-filling PDFs, batch processing, server-side generation

### PDF.js Library
- **Best For**: Rendering PDFs in browser
- **Limitations**: Not designed for form filling (use pdf-lib or native browser)
- **Use Case**: Custom PDF viewer, annotation tools

---

## Implementation Strategy

### Recommended Approach: Hybrid System

**Step 1**: Use pdf-lib to pre-fill fields from auto-populate
**Step 2**: Display filled PDF in iframe using native browser PDF viewer
**Step 3**: Let users edit directly in PDF (native browser support)
**Step 4**: Users download the edited PDF

**Why This Works**:
- ✅ Pre-filling is fast (pdf-lib)
- ✅ Editing is native (no custom UI needed)
- ✅ Works offline (PDFs cached locally)
- ✅ Legally compliant (official GTA forms)

---

## Phase 1: Download and Store Official PDFs

### Directory Structure
```
public/
  irs-forms/
    f656.pdf           # Form 656 - Offer in Compromise
    f433a.pdf          # Form 433-A - Wage Earner
    f433b.pdf          # Form 433-B - Self-Employed
    f433d.pdf          # Form 433-D - Installment Agreement
    f433f.pdf          # Form 433-F - Collection Info
    f9465.pdf          # Form 9465 - Installment Agreement Request
```

### Download Commands
```bash
# Create directory
mkdir -p public/irs-forms

# Download forms from GTA
curl -o public/irs-forms/f656.pdf https://www.irs.gov/pub/irs-pdf/f656.pdf
curl -o public/irs-forms/f433a.pdf https://www.irs.gov/pub/irs-pdf/f433a.pdf
curl -o public/irs-forms/f433b.pdf https://www.irs.gov/pub/irs-pdf/f433b.pdf
curl -o public/irs-forms/f433d.pdf https://www.irs.gov/pub/irs-pdf/f433d.pdf
curl -o public/irs-forms/f433f.pdf https://www.irs.gov/pub/irs-pdf/f433f.pdf
curl -o public/irs-forms/f9465.pdf https://www.irs.gov/pub/irs-pdf/f9465.pdf
```

### Alternative: Windows PowerShell
```powershell
# Create directory
New-Item -ItemType Directory -Force -Path "public/irs-forms"

# Download forms
Invoke-WebRequest -Uri "https://www.irs.gov/pub/irs-pdf/f656.pdf" -OutFile "public/irs-forms/f656.pdf"
Invoke-WebRequest -Uri "https://www.irs.gov/pub/irs-pdf/f433a.pdf" -OutFile "public/irs-forms/f433a.pdf"
Invoke-WebRequest -Uri "https://www.irs.gov/pub/irs-pdf/f433b.pdf" -OutFile "public/irs-forms/f433b.pdf"
```

---

## Phase 2: Create PDF Field Inspector

**Purpose**: Discover the actual field names in official PDFs

### Create: `src/utils/pdfFieldInspector.ts`

```typescript
import { PDFDocument } from 'pdf-lib';

export interface PDFFieldInfo {
  name: string;
  type: string;
  value?: string;
  defaultValue?: string;
}

/**
 * Inspect PDF form fields and return their names and types
 */
export async function inspectPDFFields(pdfUrl: string): Promise<PDFFieldInfo[]> {
  try {
    // Load the PDF
    const response = await fetch(pdfUrl);
    const arrayBuffer = await response.arrayBuffer();
    const pdfDoc = await PDFDocument.load(arrayBuffer);

    // Get the form
    const form = pdfDoc.getForm();
    const fields = form.getFields();

    // Map field information
    const fieldInfo: PDFFieldInfo[] = fields.map(field => ({
      name: field.getName(),
      type: field.constructor.name,
      value: field.constructor.name === 'PDFTextField'
        ? (field as any).getText()
        : undefined,
    }));

    return fieldInfo;
  } catch (error) {
    console.error('Error inspecting PDF fields:', error);
    throw error;
  }
}

/**
 * Log all fields to console for documentation
 */
export async function logPDFFields(pdfUrl: string) {
  const fields = await inspectPDFFields(pdfUrl);

  console.log(`\n=== PDF Field Inspector ===`);
  console.log(`PDF: ${pdfUrl}`);
  console.log(`Total Fields: ${fields.length}\n`);

  fields.forEach((field, index) => {
    console.log(`${index + 1}. ${field.name}`);
    console.log(`   Type: ${field.type}`);
    if (field.value) {
      console.log(`   Value: ${field.value}`);
    }
    console.log('');
  });
}
```

### Usage Example
```typescript
import { logPDFFields } from './utils/pdfFieldInspector';

// In a component or test file
async function inspectForm656() {
  await logPDFFields('/irs-forms/f656.pdf');
}
```

---

## Phase 3: Create Field Mappings

**Purpose**: Map application field names to PDF field names

### Create: `src/lib/irsFieldMappings.ts`

```typescript
export interface FieldMapping {
  appFieldName: string;      // Our field name (e.g., 'taxpayerName')
  pdfFieldName: string;      // PDF's field name (e.g., 'topmostSubform[0].Page1[0].f1_01[0]')
  label: string;             // Human-readable label
  type: 'text' | 'date' | 'number' | 'checkbox' | 'radio';
  format?: (value: any) => string;  // Optional formatter
}

/**
 * Form 656 - Offer in Compromise
 * NOTE: These field names are EXAMPLES - inspect actual PDF for real names
 */
export const FORM_656_FIELD_MAPPING: FieldMapping[] = [
  {
    appFieldName: 'taxpayerName',
    pdfFieldName: 'topmostSubform[0].Page1[0].f1_01[0]',  // EXAMPLE - verify actual name
    label: 'Taxpayer Name',
    type: 'text',
  },
  {
    appFieldName: 'ssn',
    pdfFieldName: 'topmostSubform[0].Page1[0].f1_02[0]',  // EXAMPLE
    label: 'SSN (Last 4 Digits)',
    type: 'text',
  },
  {
    appFieldName: 'dateOfBirth',
    pdfFieldName: 'topmostSubform[0].Page1[0].f1_03[0]',  // EXAMPLE
    label: 'Date of Birth',
    type: 'date',
    format: (value: string) => {
      // Convert YYYY-MM-DD to MM/DD/YYYY
      const date = new Date(value);
      return `${date.getMonth() + 1}/${date.getDate()}/${date.getFullYear()}`;
    },
  },
  // ... more mappings
];

/**
 * Form 433-A - Collection Information Statement (Wage Earner)
 */
export const FORM_433A_FIELD_MAPPING: FieldMapping[] = [
  // TODO: Inspect PDF and add mappings
];

/**
 * Form 433-B - Collection Information Statement (Self-Employed)
 */
export const FORM_433B_FIELD_MAPPING: FieldMapping[] = [
  // TODO: Inspect PDF and add mappings
];

/**
 * Get field mapping for a specific form
 */
export function getFieldMapping(formType: '656' | '433-A' | '433-B'): FieldMapping[] {
  switch (formType) {
    case '656':
      return FORM_656_FIELD_MAPPING;
    case '433-A':
      return FORM_433A_FIELD_MAPPING;
    case '433-B':
      return FORM_433B_FIELD_MAPPING;
    default:
      return [];
  }
}
```

---

## Phase 4: Fill PDF Fields with pdf-lib

### Create: `src/lib/pdfFormFiller.ts`

```typescript
import { PDFDocument, PDFTextField } from 'pdf-lib';
import { getFieldMapping, FieldMapping } from './irsFieldMappings';

/**
 * Fill PDF form fields with data
 */
export async function fillPDFForm(
  pdfUrl: string,
  formType: '656' | '433-A' | '433-B',
  data: Record<string, any>
): Promise<Uint8Array> {
  try {
    // Load the PDF
    const response = await fetch(pdfUrl);
    const arrayBuffer = await response.arrayBuffer();
    const pdfDoc = await PDFDocument.load(arrayBuffer);

    // Get the form
    const form = pdfDoc.getForm();

    // Get field mappings
    const mappings = getFieldMapping(formType);

    // Fill each field
    for (const mapping of mappings) {
      const value = data[mapping.appFieldName];

      if (!value) {
        console.warn(`No value for field: ${mapping.appFieldName}`);
        continue;
      }

      try {
        // Format value if formatter exists
        const formattedValue = mapping.format
          ? mapping.format(value)
          : String(value);

        // Get PDF field
        const pdfField = form.getTextField(mapping.pdfFieldName);

        // Set the value
        pdfField.setText(formattedValue);

        console.log(`✓ Filled: ${mapping.label} = ${formattedValue}`);
      } catch (fieldError) {
        console.error(`Error filling field ${mapping.pdfFieldName}:`, fieldError);
      }
    }

    // Save the PDF
    const pdfBytes = await pdfDoc.save();
    return pdfBytes;
  } catch (error) {
    console.error('Error filling PDF form:', error);
    throw error;
  }
}

/**
 * Fill PDF and create a blob URL for preview
 */
export async function fillAndPreviewPDF(
  pdfUrl: string,
  formType: '656' | '433-A' | '433-B',
  data: Record<string, any>
): Promise<string> {
  const pdfBytes = await fillPDFForm(pdfUrl, formType, data);
  const blob = new Blob([pdfBytes], { type: 'application/pdf' });
  return URL.createObjectURL(blob);
}

/**
 * Fill PDF and download
 */
export async function fillAndDownloadPDF(
  pdfUrl: string,
  formType: '656' | '433-A' | '433-B',
  data: Record<string, any>,
  filename: string
) {
  const pdfBytes = await fillPDFForm(pdfUrl, formType, data);
  const blob = new Blob([pdfBytes], { type: 'application/pdf' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);

  URL.revokeObjectURL(url);
}
```

---

## Phase 5: Update UI Component

### Update: `src/components/Forms/PDFFormEditor.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { Download, FileText } from 'lucide-react';
import { fillAndPreviewPDF, fillAndDownloadPDF } from '../../lib/pdfFormFiller';

interface PDFFormEditorProps {
  formType: '656' | '433-A' | '433-B';
  formTitle: string;
  fields: Record<string, string>;
}

export function PDFFormEditor({ formType, formTitle, fields }: PDFFormEditorProps) {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get the PDF path
  const getPDFPath = (): string => {
    const formMap: Record<string, string> = {
      '656': '/irs-forms/f656.pdf',
      '433-A': '/irs-forms/f433a.pdf',
      '433-B': '/irs-forms/f433b.pdf',
    };
    return formMap[formType];
  };

  // Fill and preview PDF when fields change
  useEffect(() => {
    if (Object.keys(fields).length === 0) return;

    const fillPDF = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const pdfPath = getPDFPath();
        const url = await fillAndPreviewPDF(pdfPath, formType, fields);

        // Clean up old URL
        if (pdfUrl) {
          URL.revokeObjectURL(pdfUrl);
        }

        setPdfUrl(url);
      } catch (err) {
        console.error('Error filling PDF:', err);
        setError('Failed to fill PDF. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fillPDF();

    // Cleanup on unmount
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [fields, formType]);

  const handleDownload = async () => {
    try {
      const pdfPath = getPDFPath();
      const filename = `GTA_Form_${formType}_${new Date().toISOString().split('T')[0]}.pdf`;
      await fillAndDownloadPDF(pdfPath, formType, fields, filename);
    } catch (err) {
      console.error('Error downloading PDF:', err);
      setError('Failed to download PDF. Please try again.');
    }
  };

  return (
    <div className="space-y-6">
      {/* PDF Preview */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {formTitle}
            </h3>
          </div>
          <button
            onClick={handleDownload}
            disabled={!pdfUrl || isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg font-medium hover:from-blue-700 hover:to-blue-800 shadow-sm hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF</span>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        <div className="relative bg-gray-50 dark:bg-gray-900 rounded-lg overflow-hidden" style={{ height: '800px' }}>
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 z-10">
              <div className="text-center">
                <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Filling PDF...</p>
              </div>
            </div>
          )}

          {pdfUrl ? (
            <iframe
              src={pdfUrl}
              className="w-full h-full border-0"
              title="PDF Preview"
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-500 dark:text-gray-400">
                <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium">Fill form fields to generate PDF</p>
                <p className="text-sm mt-2">Use the auto-populate button above</p>
              </div>
            </div>
          )}
        </div>

        {pdfUrl && (
          <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <p className="text-sm text-blue-800 dark:text-blue-200">
              <strong>✓ PDF Ready:</strong> You can now edit fields directly in the PDF above.
              Your browser's native PDF editor allows you to make changes before downloading.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## Common Issues and Solutions

### Issue 1: Field Name Not Found
**Problem**: `Error: Field 'xyz' not found`
**Solution**: Run PDF field inspector to get actual field names

### Issue 2: Fields Not Visible After Filling
**Problem**: Fields are filled but don't show in PDF
**Solution**: Some PDFs need appearance streams. Try:
```typescript
const form = pdfDoc.getForm();
form.updateFieldAppearances();  // Add this before saving
```

### Issue 3: Date Format Issues
**Problem**: Dates display incorrectly
**Solution**: Add format function in field mapping:
```typescript
{
  appFieldName: 'dateOfBirth',
  pdfFieldName: '...',
  type: 'date',
  format: (value) => {
    const date = new Date(value);
    return `${date.getMonth() + 1}/${date.getDate()}/${date.getFullYear()}`;
  },
}
```

### Issue 4: CORS Errors When Loading PDF
**Problem**: Can't load PDF from external URL
**Solution**: Store PDFs locally in `public/` folder or configure CORS on server

---

## Best Practices

### 1. Field Mapping Management
- Keep mappings in separate file (`irsFieldMappings.ts`)
- Document field types and formats
- Add comments with PDF field locations (page number, section)

### 2. Error Handling
- Catch errors for each field individually
- Log which fields fail to fill
- Continue filling other fields even if one fails

### 3. User Experience
- Show loading state while filling PDF
- Display which fields were successfully filled
- Allow users to edit in native PDF viewer
- Provide clear download button

### 4. Legal Compliance
- Use official GTA PDFs only
- Add disclaimer about form revision dates
- Don't modify PDF structure (only fill fields)
- Recommend users verify with tax professional

---

## Integration Checklist

- [ ] Download official PDF forms to `public/irs-forms/`
- [ ] Create PDF field inspector utility
- [ ] Inspect PDFs and document field names
- [ ] Create field mappings file
- [ ] Implement `pdfFormFiller.ts`
- [ ] Update UI component to use filled PDFs
- [ ] Test auto-populate workflow
- [ ] Test manual editing in browser
- [ ] Test download functionality
- [ ] Add error handling
- [ ] Add user instructions
- [ ] Test with real user data

---

## Time Estimates

| Task | Time | Priority |
|------|------|----------|
| Download PDFs | 5 min | HIGH |
| Create field inspector | 30 min | HIGH |
| Inspect Form 656 | 15 min | HIGH |
| Create mappings for Form 656 | 1-2 hrs | HIGH |
| Implement pdfFormFiller | 1 hr | HIGH |
| Update UI component | 1 hr | HIGH |
| Test and debug | 1-2 hrs | HIGH |
| Inspect Form 433-A | 15 min | MEDIUM |
| Mappings for Form 433-A | 1-2 hrs | MEDIUM |
| Inspect Form 433-B | 15 min | MEDIUM |
| Mappings for Form 433-B | 1-2 hrs | MEDIUM |

**Total for Form 656**: 4-6 hours
**Total for all 3 forms**: 10-14 hours

---

## Success Criteria

✅ **Phase 1 Complete When**:
- Official PDFs downloaded and stored
- PDFs load successfully in browser
- No CORS errors

✅ **Phase 2 Complete When**:
- Field inspector lists all PDF field names
- Field names documented in JSON or console
- Field types identified (text, date, number, etc.)

✅ **Phase 3 Complete When**:
- Field mappings file created
- At least 10 fields mapped per form
- Formatters added for dates and currency

✅ **Phase 4 Complete When**:
- PDF fields fill programmatically
- Filled values visible in PDF
- No console errors during filling

✅ **Phase 5 Complete When**:
- UI displays filled PDF
- Users can edit in native PDF viewer
- Download produces correct PDF

✅ **Complete Integration When**:
- Auto-populate fills PDF correctly
- All 12+ fields fill successfully
- Manual editing works in browser
- Download produces submission-ready PDF
- Tested with real user data

---

## Additional Resources

- **pdf-lib Docs**: https://pdf-lib.js.org/docs/api/
- **GTA PDF Forms**: https://www.irs.gov/forms-instructions
- **AcroForms Spec**: https://www.pdftron.com/blog/pdf/what-are-acroforms/
- **Browser PDF Support**: https://caniuse.com/pdf-viewer

---

**Skill Created**: October 28, 2025
**Last Updated**: November 7, 2025
**Status**: Production ready for GTA forms integration
