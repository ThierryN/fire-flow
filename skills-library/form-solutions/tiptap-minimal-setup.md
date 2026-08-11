# TipTap v2 Minimal Rich Text Editor Setup

> Production-ready TipTap v2 React component with toolbar, auto-save, image upload, and word count — the minimum viable rich text editor for content platforms.

**When to use:** Building any content editor in a React/Vite/Next.js app that needs rich text beyond a basic textarea: blog posts, course lessons, knowledge base articles, CMS content.
**Stack:** TipTap v2, React 18+, TypeScript, Tailwind CSS

---

## Installation

```bash
# Core TipTap packages
npm install @tiptap/react @tiptap/pm @tiptap/starter-kit

# Extensions used in this guide
npm install @tiptap/extension-placeholder
npm install @tiptap/extension-link
npm install @tiptap/extension-image
npm install @tiptap/extension-character-count
npm install @tiptap/extension-heading
npm install @tiptap/extension-code-block-lowlight
npm install lowlight              # syntax highlighting for code blocks

# Safe HTML rendering
npm install isomorphic-dompurify
npm install @types/dompurify

# Optional: typography extension for smart quotes, em-dashes
npm install @tiptap/extension-typography
```

**Package summary:**
| Package | Purpose |
|---------|---------|
| `@tiptap/react` | React integration, `useEditor`, `EditorContent` |
| `@tiptap/pm` | ProseMirror peer dependency |
| `@tiptap/starter-kit` | Bold, Italic, Strike, Code, Lists, Blockquote, HorizontalRule, History |
| `@tiptap/extension-link` | Clickable links with href validation |
| `@tiptap/extension-image` | Image embedding |
| `@tiptap/extension-character-count` | Word and character count |
| `@tiptap/extension-placeholder` | Ghost text when editor is empty |
| `isomorphic-dompurify` | Sanitize HTML before rendering — prevents XSS |
| `lowlight` | Syntax highlighting engine for code blocks |

---

## Minimal Editor Component

```tsx
// components/RichTextEditor.tsx
import React, { useCallback, useEffect, useRef } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import Image from '@tiptap/extension-image';
import Placeholder from '@tiptap/extension-placeholder';
import CharacterCount from '@tiptap/extension-character-count';
import Heading from '@tiptap/extension-heading';

import { Toolbar } from './EditorToolbar';

interface RichTextEditorProps {
  initialContent?: string;           // HTML string or JSON string
  onChange?: (html: string, json: object) => void;
  onSave?: (html: string, json: object) => Promise<void>;
  placeholder?: string;
  editable?: boolean;
  wordLimit?: number;
  className?: string;
}

export function RichTextEditor({
  initialContent = '',
  onChange,
  onSave,
  placeholder = 'Start writing...',
  editable = true,
  wordLimit,
  className = '',
}: RichTextEditorProps) {
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isSaving = useRef(false);

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: false,            // We configure heading separately
        codeBlock: false,          // We configure codeBlock separately
      }),
      Heading.configure({
        levels: [2, 3, 4],         // H2, H3, H4 only — no H1 (page title owns that)
      }),
      Link.configure({
        openOnClick: false,        // Don't follow links in editor
        HTMLAttributes: {
          rel: 'noopener noreferrer',
          class: 'text-blue-600 underline hover:text-blue-800',
        },
        validate: (href) => /^https?:\/\//.test(href),
      }),
      Image.configure({
        HTMLAttributes: {
          class: 'max-w-full rounded-lg my-4',
        },
        allowBase64: false,        // Force proper uploads, not inline base64
      }),
      Placeholder.configure({
        placeholder,
        emptyNodeClass: 'before:content-[attr(data-placeholder)] before:text-gray-400 before:float-left before:pointer-events-none before:h-0',
      }),
      CharacterCount.configure({
        limit: wordLimit ? wordLimit * 6 : undefined,  // rough char estimate
      }),
    ],

    content: (() => {
      if (!initialContent) return '';
      // Try to parse as JSON (TipTap JSON format), fall back to HTML
      try {
        return JSON.parse(initialContent);
      } catch {
        return initialContent;   // treat as HTML
      }
    })(),

    editable,

    editorProps: {
      attributes: {
        class: [
          'prose prose-slate max-w-none',
          'focus:outline-none',
          'min-h-[200px] p-4',
          className,
        ].filter(Boolean).join(' '),
      },
    },

    onUpdate: ({ editor }) => {
      const html = editor.getHTML();
      const json = editor.getJSON();

      onChange?.(html, json);

      // Debounced auto-save: wait 1.5s after last keystroke
      if (onSave) {
        if (saveTimer.current) clearTimeout(saveTimer.current);
        saveTimer.current = setTimeout(async () => {
          if (isSaving.current) return;
          isSaving.current = true;
          try {
            await onSave(html, json);
          } finally {
            isSaving.current = false;
          }
        }, 1500);
      }
    },
  });

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (saveTimer.current) clearTimeout(saveTimer.current);
    };
  }, []);

  if (!editor) return null;

  const wordCount = editor.storage.characterCount?.words() ?? 0;
  const charCount = editor.storage.characterCount?.characters() ?? 0;

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      {editable && <Toolbar editor={editor} />}
      <EditorContent editor={editor} />
      <div className="flex justify-end gap-4 px-4 py-2 text-xs text-gray-400 border-t border-gray-100">
        <span>{wordCount} words</span>
        <span>{charCount} characters</span>
      </div>
    </div>
  );
}
```

---

## Toolbar Component

```tsx
// components/EditorToolbar.tsx
import React, { useCallback } from 'react';
import type { Editor } from '@tiptap/react';

interface ToolbarProps {
  editor: Editor;
}

export function Toolbar({ editor }: ToolbarProps) {
  const setLink = useCallback(() => {
    const previousUrl = editor.getAttributes('link').href ?? '';
    const url = window.prompt('Enter URL:', previousUrl);

    if (url === null) return;           // cancelled
    if (url === '') {
      editor.chain().focus().extendMarkRange('link').unsetLink().run();
      return;
    }

    // Prepend https:// if missing
    const normalized = url.startsWith('http') ? url : `https://${url}`;
    editor.chain().focus().extendMarkRange('link').setLink({ href: normalized }).run();
  }, [editor]);

  return (
    <div className="flex flex-wrap gap-1 p-2 border-b border-gray-200 bg-gray-50">
      {/* Headings */}
      <ToolbarGroup>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          active={editor.isActive('heading', { level: 2 })}
          title="Heading 2"
        >
          H2
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          active={editor.isActive('heading', { level: 3 })}
          title="Heading 3"
        >
          H3
        </ToolbarButton>
      </ToolbarGroup>

      <Divider />

      {/* Marks */}
      <ToolbarGroup>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBold().run()}
          active={editor.isActive('bold')}
          disabled={!editor.can().chain().focus().toggleBold().run()}
          title="Bold (Ctrl+B)"
        >
          <b>B</b>
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleItalic().run()}
          active={editor.isActive('italic')}
          title="Italic (Ctrl+I)"
        >
          <i>I</i>
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleCode().run()}
          active={editor.isActive('code')}
          title="Inline Code"
        >
          {'</>'}
        </ToolbarButton>
        <ToolbarButton
          onClick={setLink}
          active={editor.isActive('link')}
          title="Add Link (Ctrl+K)"
        >
          Link
        </ToolbarButton>
      </ToolbarGroup>

      <Divider />

      {/* Lists */}
      <ToolbarGroup>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          active={editor.isActive('bulletList')}
          title="Bullet List"
        >
          - List
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          active={editor.isActive('orderedList')}
          title="Numbered List"
        >
          1. List
        </ToolbarButton>
      </ToolbarGroup>

      <Divider />

      {/* Block elements */}
      <ToolbarGroup>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
          active={editor.isActive('blockquote')}
          title="Blockquote"
        >
          Quote
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleCodeBlock().run()}
          active={editor.isActive('codeBlock')}
          title="Code Block"
        >
          {'{ }'}
        </ToolbarButton>
      </ToolbarGroup>

      <Divider />

      {/* History */}
      <ToolbarGroup>
        <ToolbarButton
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().chain().focus().undo().run()}
          title="Undo (Ctrl+Z)"
        >
          Undo
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().chain().focus().redo().run()}
          title="Redo (Ctrl+Shift+Z)"
        >
          Redo
        </ToolbarButton>
      </ToolbarGroup>
    </div>
  );
}

// Sub-components

function ToolbarGroup({ children }: { children: React.ReactNode }) {
  return <div className="flex gap-0.5">{children}</div>;
}

function Divider() {
  return <div className="w-px bg-gray-200 mx-1 self-stretch" />;
}

interface ButtonProps {
  onClick: () => void;
  active?: boolean;
  disabled?: boolean;
  title?: string;
  children: React.ReactNode;
}

function ToolbarButton({ onClick, active, disabled, title, children }: ButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={[
        'px-2 py-1 rounded text-sm font-medium transition-colors',
        'hover:bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed',
        active
          ? 'bg-gray-800 text-white hover:bg-gray-700'
          : 'text-gray-700',
      ].join(' ')}
    >
      {children}
    </button>
  );
}
```

---

## Getting and Setting Content

```typescript
// Get content from editor
const html = editor.getHTML();
// Returns: '<p>Hello <strong>world</strong></p>'

const json = editor.getJSON();
// Returns ProseMirror document JSON — preferred for storage (round-trips perfectly)
/*
{
  "type": "doc",
  "content": [
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "Hello " },
        { "type": "text", "marks": [{ "type": "bold" }], "text": "world" }
      ]
    }
  ]
}
*/

const text = editor.getText();
// Returns: 'Hello world' (plain text, no markup)

// Set content programmatically (e.g., loading saved draft)
editor.commands.setContent('<p>Loaded from DB</p>');           // HTML
editor.commands.setContent(jsonFromDatabase, false);           // JSON, second arg = don't emit update
editor.commands.clearContent();                                // empty editor
```

---

## Saving to Database

```typescript
// hooks/useContentSave.ts
import { useCallback, useRef, useState } from 'react';

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

export function useContentSave(contentId: string) {
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const lastSavedContent = useRef<string>('');

  const save = useCallback(async (html: string, json: object) => {
    // Skip if content hasn't changed
    const serialized = JSON.stringify(json);
    if (serialized === lastSavedContent.current) return;

    setSaveStatus('saving');
    try {
      await fetch(`/api/content/${contentId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          body_html: html,
          body_json: json,
        }),
      });
      lastSavedContent.current = serialized;
      setSaveStatus('saved');
      // Reset to 'idle' after 2 seconds
      setTimeout(() => setSaveStatus('idle'), 2000);
    } catch {
      setSaveStatus('error');
    }
  }, [contentId]);

  return { save, saveStatus };
}

// Usage in parent:
function ContentEditPage({ contentId }: { contentId: string }) {
  const { save, saveStatus } = useContentSave(contentId);

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <h1>Edit Content</h1>
        {saveStatus === 'saving' && <span className="text-sm text-gray-400">Saving...</span>}
        {saveStatus === 'saved'  && <span className="text-sm text-green-500">Saved</span>}
        {saveStatus === 'error'  && <span className="text-sm text-red-500">Save failed</span>}
      </div>
      <RichTextEditor
        initialContent={content.body_json}
        onSave={save}
      />
    </div>
  );
}
```

---

## Rendering Saved Content Safely

**SECURITY: Always sanitize HTML before rendering. Raw HTML from any storage must go through DOMPurify.**

**Option A — Sanitize and render HTML:**

```tsx
// components/ContentRenderer.tsx
// NOTE: Always sanitize before rendering to prevent XSS attacks.
import DOMPurify from 'isomorphic-dompurify';

const ALLOWED_TAGS = ['p','h2','h3','h4','strong','em','code','pre','a','ul','ol','li','blockquote','img','hr','br'];
const ALLOWED_ATTR = ['href','src','alt','class','rel','target'];

interface Props {
  html: string;
  className?: string;
}

export function ContentRenderer({ html, className = '' }: Props) {
  // Sanitize BEFORE rendering — this prevents XSS even if DB content is compromised
  const sanitized = DOMPurify.sanitize(html, { ALLOWED_TAGS, ALLOWED_ATTR });

  // eslint-disable-next-line react/no-danger -- intentional: sanitized above with DOMPurify
  return (
    <div
      className={`prose prose-slate max-w-none ${className}`}
      // Content is sanitized by DOMPurify before this assignment
      {...{ dangerouslySetInnerHTML: { __html: sanitized } }}
    />
  );
}
```

**Option B (Preferred) — Render from JSON using TipTap's `generateHTML`:**

```tsx
import { generateHTML } from '@tiptap/html';
import StarterKit from '@tiptap/starter-kit';
import Heading from '@tiptap/extension-heading';
import Link from '@tiptap/extension-link';

// This avoids dangerouslySetInnerHTML entirely — output is always valid markup
function renderContentFromJson(json: object): string {
  return generateHTML(json, [
    StarterKit,
    Heading.configure({ levels: [2, 3, 4] }),
    Link,
  ]);
}

// Then pass the result to ContentRenderer for a final sanitization pass
// or use TipTap's React renderer for fully safe rendering without innerHTML
```

Using JSON + `generateHTML` is safer than storing raw HTML because the JSON round-trip is lossless and the schema is strictly controlled by TipTap's node definitions.

---

## Image Upload Extension

```tsx
// extensions/uploadable-image.ts
import Image from '@tiptap/extension-image';

export const UploadableImage = Image.extend({
  addAttributes() {
    return {
      ...this.parent?.(),
      loading: { default: null },
    };
  },
});

// Upload handler (call from toolbar or drag-drop)
async function uploadImageFile(file: File, editor: Editor): Promise<void> {
  if (!file.type.startsWith('image/')) {
    alert('Please select an image file');
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    alert('Image must be under 5MB');
    return;
  }

  // Insert a placeholder while uploading
  const placeholderSrc = URL.createObjectURL(file);
  editor.chain().focus().setImage({ src: placeholderSrc, alt: 'Uploading...' }).run();

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/api/media/upload', { method: 'POST', body: formData });
    const { url } = await res.json() as { url: string };

    // Replace placeholder with real URL
    editor.chain().focus()
      .updateAttributes('image', { src: url, alt: file.name.replace(/\.[^.]+$/, '') })
      .run();
  } catch {
    // Remove the placeholder if upload failed
    editor.chain().focus().undo().run();
    alert('Image upload failed. Please try again.');
  } finally {
    URL.revokeObjectURL(placeholderSrc);
  }
}
```

**Add drag-and-drop to the editor wrapper:**

```tsx
function EditorWithDrop({ editor, children }: { editor: Editor; children: React.ReactNode }) {
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
    files.forEach(file => uploadImageFile(file, editor));
  }, [editor]);

  return (
    <div onDrop={handleDrop} onDragOver={e => e.preventDefault()}>
      {children}
    </div>
  );
}
```

---

## Word Count Extension Usage

```tsx
// Word count is already installed via CharacterCount extension
// Access via editor.storage:

const words = editor.storage.characterCount.words();
const chars = editor.storage.characterCount.characters();

// With a word limit:
const editor = useEditor({
  extensions: [
    CharacterCount.configure({
      limit: 10000,          // character limit
      mode: 'textSize',      // 'textSize' (default) or 'nodeSize'
    }),
  ],
});

// Check if limit is approached:
const charLimit = 10000;
const currentChars = editor.storage.characterCount.characters();
const isNearLimit = currentChars >= charLimit * 0.9;
const isAtLimit   = currentChars >= charLimit;
```

---

## Common Gotchas

### 1. SSR / Next.js Compatibility

TipTap uses browser APIs. In Next.js, always use dynamic import with `ssr: false`:

```tsx
// pages/edit.tsx or app/edit/page.tsx
import dynamic from 'next/dynamic';

const RichTextEditor = dynamic(
  () => import('../components/RichTextEditor'),
  { ssr: false, loading: () => <div className="h-48 animate-pulse bg-gray-100 rounded" /> }
);
```

### 2. CSS Conflicts with Tailwind's Preflight

Tailwind's preflight resets all heading sizes, margins, etc. The `@tailwindcss/typography` plugin (`prose` class) re-applies them. Always wrap rendered content in `prose`:

```tsx
// Install: npm install @tailwindcss/typography
// tailwind.config.ts: plugins: [require('@tailwindcss/typography')]

<div className="prose prose-slate max-w-none">
  {/* rendered content */}
</div>
```

### 3. `useEditor` Returns `null` Initially

The editor is `null` on the first render. Always guard:

```tsx
if (!editor) return <div className="h-48 bg-gray-50 rounded animate-pulse" />;
```

### 4. Content Sync on External Updates

If you load new content after the editor is initialized (e.g., switching between drafts):

```tsx
useEffect(() => {
  if (editor && initialContent && editor.getHTML() !== initialContent) {
    editor.commands.setContent(initialContent, false);  // false = don't emit update
  }
}, [editor, initialContent]);
```

### 5. Link Extension Click Behavior

By default, `openOnClick: true` causes links to open while editing — confusing for authors. Always set `openOnClick: false` in the editor and handle link clicks in the rendered output separately.

### 6. Bold/Italic Not Working on Safari

ProseMirror requires `contenteditable="true"` for keyboard shortcuts. Safari can be finicky with `tabIndex`. Add `tabIndex={0}` to the EditorContent wrapper if shortcuts don't fire.

### 7. XSS When Rendering Saved HTML

Never render untrusted HTML without sanitization. Even if your own editor wrote the HTML, always run it through DOMPurify before rendering — database compromise or API injection are real attack vectors. Prefer the JSON + `generateHTML` path to avoid innerHTML entirely.
