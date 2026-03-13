# Markdown to Word Converter

> Convert any Markdown file in Claude Reports to a formatted .docx Word document

> **Contributed:** 2026-03-10 | **Category:** document-processing | **Difficulty:** easy

---

## Problem

Thierry frequently generates reports as Markdown files in `C:\Users\Thierry\Documents\Claude Reports\` and needs them as Word documents for sharing, printing, or further editing. Manual conversion loses formatting — headings, tables, code blocks, bold/italic, and lists all need to be preserved.

---

## Solution Pattern

Use `python-docx` (already installed on this system) to parse Markdown and generate a styled `.docx` file. The converter handles: headings (H1-H4), bold/italic/inline code, bullet and numbered lists, tables, code blocks (Consolas font), blockquotes, checkboxes, and horizontal rules.

**Dependency:** `python-docx` (`pip install python-docx` — already installed)

---

## Usage

When the user says any of:
- "convert to word"
- "make a docx"
- "I need this as a Word document"
- "convert [file] to Word"

Run the Python script below, replacing `INPUT_PATH` and `OUTPUT_PATH`.

**Default behavior:** Same filename, `.md` → `.docx`, same directory.

---

## Converter Script

```python
# md-to-word.py — Markdown to Word converter
# Requires: pip install python-docx

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re
import os
import sys

def convert_md_to_docx(input_path, output_path=None):
    """Convert a Markdown file to a formatted Word document."""

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + '.docx'

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    doc = Document()

    # -- Style setup --
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    title_style = doc.styles['Title']
    title_style.font.size = Pt(24)
    title_style.font.color.rgb = RGBColor(0x1e, 0x29, 0x3b)
    title_style.font.bold = True

    for level in range(1, 5):
        h = doc.styles[f'Heading {level}']
        h.font.name = 'Calibri'
        h.font.color.rgb = RGBColor(0x1e, 0x40, 0xaf)

    # -- State --
    lines = content.split('\n')
    i = 0
    in_code = False
    code_buf = []
    in_table = False
    table_rows = []

    def flush_code():
        nonlocal code_buf
        if not code_buf:
            return
        p = doc.add_paragraph()
        run = p.add_run('\n'.join(code_buf))
        run.font.name = 'Consolas'
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(0x37, 0x41, 0x51)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        code_buf = []

    def flush_table():
        nonlocal table_rows
        if not table_rows or len(table_rows) < 2:
            table_rows = []
            return
        data = [r for r in table_rows if not re.match(r'^\|[\s\-:]+\|$', r.strip())]
        if not data:
            table_rows = []
            return
        parsed = []
        for row in data:
            cells = [c.strip() for c in row.strip('|').split('|')]
            parsed.append(cells)
        if not parsed:
            table_rows = []
            return
        num_cols = max(len(r) for r in parsed)
        tbl = doc.add_table(rows=len(parsed), cols=num_cols)
        tbl.style = 'Light Grid Accent 1'
        for ri, row_data in enumerate(parsed):
            for ci, cell_text in enumerate(row_data):
                if ci < num_cols:
                    cell = tbl.cell(ri, ci)
                    cell.text = cell_text.strip('*').strip()
                    if ri == 0:
                        for p in cell.paragraphs:
                            for run in p.runs:
                                run.bold = True
        table_rows = []

    def add_formatted(text, style_name='Normal'):
        p = doc.add_paragraph()
        p.style = doc.styles[style_name]
        parts = re.split(r'(\*\*.*?\*\*|`[^`]+`|\*[^*]+\*)', text)
        for part in parts:
            if not part:
                continue
            if part.startswith('**') and part.endswith('**'):
                run = p.add_run(part[2:-2])
                run.bold = True
            elif part.startswith('`') and part.endswith('`'):
                run = p.add_run(part[1:-1])
                run.font.name = 'Consolas'
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(0xbe, 0x18, 0x5d)
            elif part.startswith('*') and part.endswith('*') and not part.startswith('**'):
                run = p.add_run(part[1:-1])
                run.italic = True
            else:
                p.add_run(part)
        return p

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code blocks
        if stripped.startswith('```'):
            if in_code:
                flush_code()
                in_code = False
            else:
                if in_table:
                    flush_table()
                    in_table = False
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # Tables
        if stripped.startswith('|') and '|' in stripped[1:]:
            if not in_table:
                in_table = True
            table_rows.append(stripped)
            i += 1
            continue
        elif in_table:
            flush_table()
            in_table = False

        # Skip empties
        if not stripped:
            i += 1
            continue

        # Horizontal rules
        if stripped in ('---', '***', '___'):
            doc.add_paragraph('_' * 60)
            i += 1
            continue

        # H1 (title)
        if stripped.startswith('# ') and not stripped.startswith('## '):
            doc.add_heading(stripped[2:].strip(), level=0)
            i += 1
            continue

        # H2-H4
        hm = re.match(r'^(#{2,4})\s+(.+)$', stripped)
        if hm:
            doc.add_heading(hm.group(2).strip(), level=len(hm.group(1)) - 1)
            i += 1
            continue

        # Bullets
        bm = re.match(r'^[-*]\s+(.+)$', stripped)
        if bm:
            add_formatted(bm.group(1), 'List Bullet')
            i += 1
            continue

        # Numbered
        nm = re.match(r'^\d+\.\s+(.+)$', stripped)
        if nm:
            add_formatted(nm.group(1), 'List Number')
            i += 1
            continue

        # Checkboxes
        if stripped.startswith('[ ]') or stripped.startswith('[x]') or stripped.startswith('[X]'):
            checked = stripped[1] in ('x', 'X')
            prefix = '> ' if checked else '_ '
            add_formatted(prefix + stripped[3:].strip(), 'List Bullet')
            i += 1
            continue

        # Blockquotes
        if stripped.startswith('>'):
            p = add_formatted(stripped.lstrip('>').strip())
            p.paragraph_format.left_indent = Inches(0.5)
            i += 1
            continue

        # Regular paragraph
        add_formatted(stripped)
        i += 1

    # Flush remaining
    if in_code:
        flush_code()
    if in_table:
        flush_table()

    doc.save(output_path)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"Word document saved: {output_path}")
    print(f"Size: {size_kb:.1f} KB")
    return output_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python md-to-word.py <input.md> [output.docx]")
        sys.exit(1)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    convert_md_to_docx(inp, out)
```

---

## Quick Reference for Claude

When converting a report, run this one-liner:

```bash
python3 -c "
from docx import Document
from docx.shared import Inches, Pt, RGBColor
import re, os

# === CHANGE THESE ===
INPUT  = r'C:\Users\Thierry\Documents\Claude Reports\FILENAME.md'
OUTPUT = INPUT.replace('.md', '.docx')
# ====================

# [paste full convert_md_to_docx function body here]
"
```

Or save the script above as `C:\Users\Thierry\scripts\md-to-word.py` and call:

```bash
python3 C:\Users\Thierry\scripts\md-to-word.py "INPUT.md" "OUTPUT.docx"
```

---

## Formatting Support

| Markdown Element | Word Output |
|------------------|-------------|
| `# H1` | Title style (24pt, dark blue) |
| `## H2` - `#### H4` | Heading 1-3 (blue, Calibri) |
| `**bold**` | Bold run |
| `*italic*` | Italic run |
| `` `code` `` | Consolas 9.5pt, pink |
| ```` ```code block``` ```` | Consolas 8.5pt, gray, monospaced block |
| `- bullet` | List Bullet style |
| `1. numbered` | List Number style |
| `> quote` | Indented 0.5in |
| `| table |` | Light Grid Accent 1 table |
| `[ ] / [x]` | Checkbox with _ / > prefix |
| `---` | Underline horizontal rule |

---

## When to Use

- Converting any `.md` file in Claude Reports to `.docx`
- User says "convert to Word", "make a docx", "I need this in Word"
- After generating a research report, architecture doc, or analysis

## When NOT to Use

- For PDFs (use a different tool)
- For complex layouts with images (consider HTML → PDF instead)
- When the user wants to edit in Markdown (keep as `.md`)
