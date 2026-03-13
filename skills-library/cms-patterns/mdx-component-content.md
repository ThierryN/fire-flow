# MDX Component Content

> Embed interactive React components (quizzes, video players, code playgrounds) directly inside lesson Markdown text
---

## Overview

MDX = Markdown + JSX. It lets you write regular Markdown (headings, paragraphs, lists) and embed React components inline. A lesson can have text, then a quiz, then more text, then a video player — all in one content file.

**What this looks like for a teacher:**

```mdx
# The Lord's Prayer

In Matthew 6:9-13, Jesus taught his disciples how to pray.

<BibleVerse reference="Matthew 6:9-13" />

## Understanding Each Line

Let's break down the prayer line by line.

<VideoPlayer url="https://youtube.com/watch?v=..." />

### "Our Father in heaven"

This opening acknowledges God as both personal ("our") and sovereign ("in heaven").

<Quiz
  question="What does 'Our Father' tell us about our relationship with God?"
  options={[
    "God is distant and unapproachable",
    "God is a personal, loving parent",
    "God only cares about certain people"
  ]}
  correct={1}
  explanation="By calling God 'Our Father,' Jesus shows that God is personal and relational."
/>

## Reflection

<JournalPrompt prompt="Write a short prayer using the pattern Jesus taught." />
```

**What the student sees:** A beautifully rendered lesson with interactive components inline.

---

## Architecture

```
┌──────────────────────────────────────────┐
│  MDX Content (stored in DB as text)      │
│                                           │
│  # Title                                  │
│  Regular markdown text...                 │
│  <Quiz question="..." />                  │
│  More text...                             │
│  <VideoPlayer url="..." />                │
└─────────────────┬────────────────────────┘
                  │
        ┌─────────▼─────────┐
        │  MDX Compiler     │
        │  (mdx-js/mdx)     │
        │                   │
        │  Markdown → React │
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │  Component Map    │
        │                   │
        │  Quiz → <Quiz/>   │
        │  Video → <Video/> │
        │  Bible → <Bible/> │
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │  Rendered Page    │
        │                   │
        │  Text + interactive│
        │  components mixed  │
        └───────────────────┘
```

---

## Setup: Install MDX Dependencies

```bash
npm install @mdx-js/mdx @mdx-js/react
# or
bun add @mdx-js/mdx @mdx-js/react
```

---

## MDX Renderer Component

```jsx
// components/cms/MDXRenderer.jsx
import { useState, useEffect, useMemo } from 'react';
import * as runtime from 'react/jsx-runtime';
import { evaluate } from '@mdx-js/mdx';
import { MDXProvider } from '@mdx-js/react';
import { mdxComponents } from './mdx-components';

/**
 * Renders MDX content string as React components.
 *
 * Props:
 *   content  — MDX string (Markdown + JSX)
 *   components — optional additional components to make available
 */
export default function MDXRenderer({ content, components = {} }) {
  const [MDXContent, setMDXContent] = useState(null);
  const [error, setError] = useState(null);

  const allComponents = useMemo(
    () => ({ ...mdxComponents, ...components }),
    [components]
  );

  useEffect(() => {
    if (!content) return;

    const compile = async () => {
      try {
        const { default: Content } = await evaluate(content, {
          ...runtime,
          useMDXComponents: () => allComponents,
        });
        setMDXContent(() => Content);
        setError(null);
      } catch (err) {
        console.error('MDX compilation error:', err);
        setError(err.message);
      }
    };

    compile();
  }, [content, allComponents]);

  if (error) {
    return (
      <div style={{
        background: '#fef2f2', border: '1px solid #fecaca',
        padding: '12px', borderRadius: '8px', color: '#991b1b',
      }}>
        <strong>Content rendering error:</strong>
        <pre style={{ fontSize: '13px', marginTop: '8px' }}>{error}</pre>
      </div>
    );
  }

  if (!MDXContent) return <div>Loading content...</div>;

  return (
    <MDXProvider components={allComponents}>
      <div className="mdx-content">
        <MDXContent />
      </div>
    </MDXProvider>
  );
}
```

---

## Component Registry

```jsx
// components/cms/mdx-components.jsx
// Register all components available in MDX content

import Quiz from '../interactive/Quiz';
import VideoPlayer from '../interactive/VideoPlayer';
import BibleVerse from '../interactive/BibleVerse';
import JournalPrompt from '../interactive/JournalPrompt';
import Callout from '../interactive/Callout';
import Tabs from '../interactive/Tabs';
import Accordion from '../interactive/Accordion';
import CodeBlock from '../interactive/CodeBlock';
import ImageGallery from '../interactive/ImageGallery';
import PrayerTimer from '../interactive/PrayerTimer';

/**
 * Component registry — maps component names to React components.
 * These names are what teachers use in their MDX content:
 *   <Quiz ... />
 *   <VideoPlayer ... />
 *   <BibleVerse ... />
 *
 * To add a new component:
 * 1. Create it in components/interactive/
 * 2. Import it here
 * 3. Add to this map
 * That's it — teachers can immediately use it in lessons.
 */
export const mdxComponents = {
  // Interactive learning
  Quiz,
  VideoPlayer,
  CodeBlock,

  // Ministry-specific
  BibleVerse,
  JournalPrompt,
  PrayerTimer,

  // Layout helpers
  Callout,
  Tabs,
  Accordion,
  ImageGallery,

  // Override default HTML elements for consistent styling
  h1: (props) => <h1 style={{ fontSize: '2rem', marginTop: '2rem', color: '#1e293b' }} {...props} />,
  h2: (props) => <h2 style={{ fontSize: '1.5rem', marginTop: '1.5rem', color: '#334155' }} {...props} />,
  h3: (props) => <h3 style={{ fontSize: '1.25rem', marginTop: '1.25rem', color: '#475569' }} {...props} />,
  p: (props) => <p style={{ lineHeight: '1.75', marginBottom: '1rem' }} {...props} />,
  blockquote: (props) => (
    <blockquote
      style={{
        borderLeft: '4px solid #6366f1',
        paddingLeft: '16px',
        margin: '1.5rem 0',
        color: '#4b5563',
        fontStyle: 'italic',
      }}
      {...props}
    />
  ),
  img: (props) => (
    <img
      style={{ maxWidth: '100%', borderRadius: '8px', margin: '1rem 0' }}
      loading="lazy"
      {...props}
    />
  ),
};
```

---

## Example Interactive Components

### Quiz Component

```jsx
// components/interactive/Quiz.jsx
import { useState } from 'react';

export default function Quiz({ question, options, correct, explanation }) {
  const [selected, setSelected] = useState(null);
  const [revealed, setRevealed] = useState(false);

  const handleSelect = (index) => {
    setSelected(index);
    setRevealed(true);
  };

  return (
    <div style={{
      background: '#f8fafc', border: '1px solid #e2e8f0',
      borderRadius: '12px', padding: '20px', margin: '24px 0',
    }}>
      <div style={{ fontWeight: '600', fontSize: '16px', marginBottom: '12px' }}>
        {question}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {options.map((opt, i) => {
          let bg = 'white';
          let border = '1px solid #d1d5db';
          if (revealed && i === correct) { bg = '#dcfce7'; border = '1px solid #22c55e'; }
          else if (revealed && i === selected && i !== correct) { bg = '#fef2f2'; border = '1px solid #ef4444'; }

          return (
            <button
              key={i}
              onClick={() => !revealed && handleSelect(i)}
              disabled={revealed}
              style={{
                padding: '12px 16px', background: bg, border,
                borderRadius: '8px', textAlign: 'left',
                cursor: revealed ? 'default' : 'pointer',
                fontSize: '14px', transition: 'all 0.2s',
              }}
            >
              {opt}
            </button>
          );
        })}
      </div>

      {revealed && explanation && (
        <div style={{
          marginTop: '12px', padding: '12px', background: '#eff6ff',
          borderRadius: '8px', fontSize: '14px', color: '#1e40af',
        }}>
          {explanation}
        </div>
      )}
    </div>
  );
}
```

### Video Player Component

```jsx
// components/interactive/VideoPlayer.jsx
export default function VideoPlayer({ url, title = 'Video' }) {
  // Extract YouTube video ID
  const getYouTubeId = (url) => {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)/);
    return match ? match[1] : null;
  };

  const youtubeId = getYouTubeId(url);

  if (youtubeId) {
    return (
      <div style={{ margin: '24px 0', borderRadius: '12px', overflow: 'hidden' }}>
        <div style={{ position: 'relative', paddingBottom: '56.25%', height: 0 }}>
          <iframe
            src={`https://www.youtube-nocookie.com/embed/${youtubeId}`}
            title={title}
            style={{
              position: 'absolute', top: 0, left: 0,
              width: '100%', height: '100%', border: 'none',
            }}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      </div>
    );
  }

  // Fallback: HTML5 video
  return (
    <div style={{ margin: '24px 0' }}>
      <video
        src={url}
        controls
        style={{ width: '100%', borderRadius: '12px' }}
      >
        Your browser does not support video playback.
      </video>
    </div>
  );
}
```

### Bible Verse Component

```jsx
// components/interactive/BibleVerse.jsx
import { useState, useEffect } from 'react';

export default function BibleVerse({ reference, version = 'KJV' }) {
  const [text, setText] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch from your own API or a public Bible API
    fetch(`/api/bible/verse?ref=${encodeURIComponent(reference)}&version=${version}`)
      .then((r) => r.json())
      .then((data) => setText(data.text))
      .catch(() => setText(`[${reference} — ${version}]`))
      .finally(() => setLoading(false));
  }, [reference, version]);

  return (
    <blockquote style={{
      background: '#fefce8', borderLeft: '4px solid #eab308',
      padding: '16px 20px', margin: '24px 0', borderRadius: '0 8px 8px 0',
    }}>
      {loading ? (
        <em>Loading verse...</em>
      ) : (
        <>
          <p style={{ fontStyle: 'italic', lineHeight: '1.8', margin: '0 0 8px' }}>
            {text}
          </p>
          <cite style={{ color: '#92400e', fontSize: '14px', fontWeight: '600' }}>
            — {reference} ({version})
          </cite>
        </>
      )}
    </blockquote>
  );
}
```

### Journal Prompt Component

```jsx
// components/interactive/JournalPrompt.jsx
import { useState } from 'react';

export default function JournalPrompt({ prompt }) {
  const [response, setResponse] = useState('');
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    try {
      await fetch('/api/journal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, response }),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error('Failed to save journal entry:', err);
    }
  };

  return (
    <div style={{
      background: '#faf5ff', border: '1px solid #d8b4fe',
      borderRadius: '12px', padding: '20px', margin: '24px 0',
    }}>
      <div style={{ fontWeight: '600', color: '#7c3aed', marginBottom: '8px' }}>
        Journal Prompt
      </div>
      <p style={{ marginBottom: '12px' }}>{prompt}</p>
      <textarea
        value={response}
        onChange={(e) => setResponse(e.target.value)}
        rows={4}
        placeholder="Write your reflection here..."
        style={{
          width: '100%', padding: '12px', border: '1px solid #d8b4fe',
          borderRadius: '8px', resize: 'vertical', fontFamily: 'inherit',
          fontSize: '14px', boxSizing: 'border-box',
        }}
      />
      <div style={{ display: 'flex', gap: '8px', marginTop: '8px', alignItems: 'center' }}>
        <button
          onClick={handleSave}
          disabled={!response.trim()}
          style={{
            background: '#7c3aed', color: 'white', border: 'none',
            padding: '8px 20px', borderRadius: '6px', cursor: 'pointer',
          }}
        >
          Save to Journal
        </button>
        {saved && <span style={{ color: '#22c55e', fontSize: '14px' }}>Saved!</span>}
      </div>
    </div>
  );
}
```

### Callout Component

```jsx
// components/interactive/Callout.jsx
export default function Callout({ type = 'info', title, children }) {
  const styles = {
    info: { bg: '#eff6ff', border: '#3b82f6', icon: 'i', titleColor: '#1e40af' },
    warning: { bg: '#fffbeb', border: '#f59e0b', icon: '!', titleColor: '#92400e' },
    success: { bg: '#f0fdf4', border: '#22c55e', icon: '✓', titleColor: '#166534' },
    tip: { bg: '#f5f3ff', border: '#8b5cf6', icon: '★', titleColor: '#5b21b6' },
  };

  const s = styles[type] || styles.info;

  return (
    <div style={{
      background: s.bg, borderLeft: `4px solid ${s.border}`,
      padding: '16px 20px', margin: '24px 0', borderRadius: '0 8px 8px 0',
    }}>
      {title && (
        <div style={{ fontWeight: '700', color: s.titleColor, marginBottom: '4px' }}>
          {s.icon} {title}
        </div>
      )}
      <div style={{ lineHeight: '1.6' }}>{children}</div>
    </div>
  );
}
```

---

## Using MDX in a Lesson Page

```jsx
// pages/LessonView.jsx
import MDXRenderer from '../components/cms/MDXRenderer';
import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';

export default function LessonView() {
  const { id } = useParams();
  const [lesson, setLesson] = useState(null);

  useEffect(() => {
    fetch(`/api/lessons/${id}`)
      .then((r) => r.json())
      .then(setLesson);
  }, [id]);

  if (!lesson) return <div>Loading...</div>;

  return (
    <article style={{ maxWidth: '800px', margin: '40px auto', padding: '0 20px' }}>
      <h1>{lesson.title}</h1>
      {lesson.cover_image && (
        <img
          src={lesson.cover_image}
          alt={lesson.title}
          style={{ width: '100%', borderRadius: '12px', marginBottom: '24px' }}
        />
      )}

      {/* Render the lesson body as MDX */}
      <MDXRenderer content={lesson.body} />
    </article>
  );
}
```

---

## Teacher: MDX Content Guide

Provide this reference to teachers who create lessons:

```
AVAILABLE COMPONENTS
====================

<Quiz question="..." options={["A", "B", "C"]} correct={0} explanation="..." />
  → Interactive multiple-choice quiz

<VideoPlayer url="https://youtube.com/watch?v=..." />
  → Embedded video player (YouTube or direct URL)

<BibleVerse reference="John 3:16" version="KJV" />
  → Auto-loaded Bible verse with citation

<JournalPrompt prompt="What did you learn today?" />
  → Text area that saves to student's journal

<Callout type="info" title="Did you know?">
  Content here...
</Callout>
  → Highlighted callout box (info, warning, success, tip)

<Tabs labels={["Tab 1", "Tab 2"]}>
  Content for tab 1

  ---

  Content for tab 2
</Tabs>
  → Tabbed content sections

<PrayerTimer minutes={5} />
  → Countdown timer for prayer/meditation exercises

<ImageGallery images={["/img/1.jpg", "/img/2.jpg"]} />
  → Scrollable image gallery
WRITING TIPS
============

- Regular text uses Markdown: **bold**, *italic*, [links](url)
- Headers: # H1, ## H2, ### H3
- Lists: - bullet or 1. numbered
- Components go on their own line with a blank line before and after
- Everything between <Component> and </Component> is content (for Callout, Tabs, etc.)
```

---

## Server-Side MDX Validation (Optional)

Validate MDX content before saving to catch syntax errors early:

```js
// server/middleware/validateMDX.js
const { compile } = require('@mdx-js/mdx');

async function validateMDX(req, res, next) {
  if (req.body.body && req.body.content_type === 'mdx') {
    try {
      await compile(req.body.body, { outputFormat: 'function-body' });
      next();
    } catch (err) {
      return res.status(400).json({
        error: 'Invalid MDX content',
        details: err.message,
        line: err.line,
        column: err.column,
      });
    }
  } else {
    next();
  }
}

module.exports = validateMDX;
```

---

## Integration With Existing Skills

| Skill | How It Connects |
|-------|----------------|
| `inline-visual-editing.md` | MDX body becomes the richtext editable region |
| `schema-driven-form-generator.md` | Add `mdx` as a field type in the schema |
| `tiptap-minimal-setup.md` | Use TipTap for the editing experience, MDX for the rendering |
| `content-branch-preview.md` | Preview drafted MDX content before publishing |
| `media-manager-abstraction.md` | Images referenced in MDX are managed by the media service |
| `transcription-pipeline-selector.md` | Generate lesson text from audio, then enhance with MDX components |

---

## Adding New Components

To make a new component available in lessons:

1. Create the component in `components/interactive/`
2. Import and add to `mdx-components.jsx` registry
3. Add to the Teacher Guide reference
4. Done — teachers can immediately use `<NewComponent />` in any lesson

No database changes. No API changes. No deployment needed beyond the code update.

---

## When to Use MDX vs. Plain HTML

**Use MDX when:**
- Content needs interactive elements (quizzes, timers, video)
- Teachers create lessons with structured learning components
- Content is educational/instructional

**Use plain HTML/rich text when:**
- Content is simple text + images (announcements, blog posts)
- No interactive elements needed
- Content creators are less technical
