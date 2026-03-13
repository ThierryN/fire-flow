---
name: multi-format-content-generator
category: creative-multimedia
version: 1.0.0
contributed: 2026-03-10
contributor: dominion-flow-research
last_updated: 2026-03-10
tags: [content-generation, multi-format, notebooklm, slides, flashcards, quiz, podcast, repurposing]
difficulty: medium
---

# Multi-Format Content Generator

## Problem Solved

Generating multiple content formats from a single source document set. One upload produces a podcast script, slide deck, flashcards, quiz questions, summaries, FAQs, infographic data, and a study guide — all grounded exclusively in the source material. This is the "NotebookLM pattern": a shared understanding layer fans out to format-specific generators, ensuring every output traces back to an exact source passage.

## When to Use

- Converting sermon recordings or transcripts into a full week of ministry content
- Transforming research papers, reports, or books into multi-format learning materials
- Building course content from instructor-uploaded sources (the LMS use case)
- Creating study aids (flashcards, quizzes) from any document collection
- Generating presentation slides from written content
- Producing podcast scripts from articles, whitepapers, or meeting notes
- Repurposing Bible study material into multiple engagement formats

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    DOCUMENT SOURCES                      │
│  PDF | DOCX | Transcript | YouTube | Audio | Markdown   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              SHARED UNDERSTANDING LAYER                  │
│                                                         │
│  1. Parse & Chunk Documents                             │
│  2. Extract Key Concepts, Definitions, Relationships    │
│  3. Build Structured Knowledge Representation           │
│  4. RAG Embedding (Gemini text-embedding-004)           │
│  5. Source Linking (every fact → exact passage)          │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
┌─────────────┐ ┌───────────┐ ┌───────────┐
│   PODCAST   │ │  SLIDES   │ │ FLASHCARDS│
│   Script    │ │  Deck     │ │  (Anki)   │
└─────────────┘ └───────────┘ └───────────┘
         │             │             │
         ▼             ▼             ▼
┌─────────────┐ ┌───────────┐ ┌───────────┐
│    QUIZ     │ │  SUMMARY  │ │    FAQ    │
│  Questions  │ │ S / M / L │ │           │
└─────────────┘ └───────────┘ └───────────┘
         │             │
         ▼             ▼
┌─────────────┐ ┌───────────┐
│ INFOGRAPHIC │ │   STUDY   │
│    Data     │ │   Guide   │
└─────────────┘ └───────────┘
```

The key insight: **parse once, generate many**. The Shared Understanding Layer does the expensive work (parsing, chunking, embedding, extraction). Each format generator receives the same `DocumentKnowledge` object and transforms it according to format-specific rules.

---

## 1. Shared Understanding Layer

### Document Parsing

```typescript
import { promises as fs } from 'fs';
import path from 'path';

// ─── Source Types ────────────────────────────────────────────────────────────

interface DocumentSource {
  type: 'pdf' | 'docx' | 'markdown' | 'transcript' | 'youtube' | 'text';
  path?: string;         // File path for local files
  url?: string;          // URL for YouTube or web sources
  content?: string;      // Raw text content (if already extracted)
  metadata: {
    title: string;
    author?: string;
    date?: string;
    tags?: string[];
  };
}

interface DocumentChunk {
  id: string;
  text: string;
  sourceId: string;
  sourceTitle: string;
  pageNumber?: number;
  sectionTitle?: string;
  startOffset: number;
  endOffset: number;
  embedding?: number[];  // Gemini text-embedding-004 vector
}

// ─── Extraction per Source Type ──────────────────────────────────────────────

async function extractText(source: DocumentSource): Promise<string> {
  switch (source.type) {
    case 'pdf': {
      const pdfParse = (await import('pdf-parse')).default;
      const buffer = await fs.readFile(source.path!);
      const result = await pdfParse(buffer);
      return result.text;
    }
    case 'docx': {
      const mammoth = await import('mammoth');
      const result = await mammoth.extractRawText({ path: source.path! });
      return result.value;
    }
    case 'markdown': {
      return await fs.readFile(source.path!, 'utf-8');
    }
    case 'youtube': {
      const { YoutubeTranscript } = await import('youtube-transcript');
      const segments = await YoutubeTranscript.fetchTranscript(source.url!);
      return segments.map(s => s.text).join(' ');
    }
    case 'transcript':
    case 'text': {
      return source.content ?? await fs.readFile(source.path!, 'utf-8');
    }
    default:
      throw new Error(`Unsupported source type: ${source.type}`);
  }
}
```

### Chunking Strategy

```typescript
// ─── Sentence-Based Chunking ─────────────────────────────────────────────────
// ~500 tokens per chunk with 50-token overlap for context continuity.
// Sentence boundaries preserve semantic coherence.

interface ChunkConfig {
  maxTokens: number;      // Target chunk size (default: 500)
  overlapTokens: number;  // Overlap between chunks (default: 50)
  minChunkSize: number;   // Minimum chunk size to avoid fragments (default: 100)
}

function chunkDocument(
  text: string,
  sourceId: string,
  sourceTitle: string,
  config: ChunkConfig = { maxTokens: 500, overlapTokens: 50, minChunkSize: 100 }
): DocumentChunk[] {
  // Split by sentence boundaries
  const sentences = text.match(/[^.!?]+[.!?]+\s*/g) ?? [text];
  const chunks: DocumentChunk[] = [];

  let currentChunk = '';
  let chunkStart = 0;
  let offset = 0;

  for (const sentence of sentences) {
    const estimatedTokens = (currentChunk + sentence).split(/\s+/).length;

    if (estimatedTokens > config.maxTokens && currentChunk.length > 0) {
      chunks.push({
        id: `${sourceId}-chunk-${chunks.length}`,
        text: currentChunk.trim(),
        sourceId,
        sourceTitle,
        startOffset: chunkStart,
        endOffset: offset,
      });

      // Overlap: keep last N tokens of current chunk
      const words = currentChunk.split(/\s+/);
      const overlapWords = words.slice(-config.overlapTokens);
      currentChunk = overlapWords.join(' ') + ' ' + sentence;
      chunkStart = offset - overlapWords.join(' ').length;
    } else {
      currentChunk += sentence;
    }
    offset += sentence.length;
  }

  // Final chunk
  if (currentChunk.trim().split(/\s+/).length >= config.minChunkSize) {
    chunks.push({
      id: `${sourceId}-chunk-${chunks.length}`,
      text: currentChunk.trim(),
      sourceId,
      sourceTitle,
      startOffset: chunkStart,
      endOffset: offset,
    });
  }

  return chunks;
}
```

### Knowledge Extraction

The core data structure that all format generators consume:

```typescript
// ─── Structured Knowledge Representation ─────────────────────────────────────
// This is the "shared understanding" that fans out to all generators.

interface Topic {
  title: string;
  summary: string;
  depth: 'primary' | 'secondary' | 'tertiary';
  sourceRefs: SourceReference[];
}

interface Concept {
  term: string;
  definition: string;
  context: string;
  importance: 'critical' | 'important' | 'supplementary';
  sourceRefs: SourceReference[];
}

interface Definition {
  term: string;
  definition: string;
  sourceRefs: SourceReference[];
}

interface Example {
  description: string;
  relatedConcept: string;
  sourceRefs: SourceReference[];
}

interface Statistic {
  value: string;
  context: string;
  sourceRefs: SourceReference[];
}

interface Relationship {
  from: string;
  to: string;
  type: 'causes' | 'contrasts' | 'supports' | 'depends-on' | 'part-of' | 'similar-to';
  description: string;
  sourceRefs: SourceReference[];
}

interface TimelineEvent {
  date: string;
  event: string;
  significance: string;
  sourceRefs: SourceReference[];
}

interface SourceReference {
  sourceId: string;
  sourceTitle: string;
  chunkId: string;
  passage: string;         // Exact quoted text from source
  pageNumber?: number;
}

interface DocumentKnowledge {
  title: string;
  mainTopics: Topic[];
  keyConcepts: Concept[];
  definitions: Definition[];
  examples: Example[];
  statistics: Statistic[];
  relationships: Relationship[];
  timeline?: TimelineEvent[];
  totalSources: number;
  totalChunks: number;
  processingDate: string;
}
```

### AI Extraction Prompt

This prompt converts raw chunks into the `DocumentKnowledge` structure. Use with Claude or Gemini.

```typescript
// ─── Knowledge Extraction Prompt ─────────────────────────────────────────────

function buildExtractionPrompt(chunks: DocumentChunk[]): string {
  const chunksText = chunks
    .map((c, i) => `[CHUNK ${i + 1} | Source: ${c.sourceTitle} | ID: ${c.id}]\n${c.text}`)
    .join('\n\n---\n\n');

  return `You are a knowledge extraction system. Analyze the following document chunks and extract structured knowledge.

IMPORTANT RULES:
- Extract ONLY information present in the provided chunks
- NEVER use your training data to add facts not in the sources
- Every extracted item MUST include a sourceRef citing the exact chunk and quoted passage
- If the sources are insufficient for a field, omit it rather than fabricate

DOCUMENT CHUNKS:
${chunksText}

Return a JSON object matching this exact structure:
{
  "title": "Inferred title of the overall content",
  "mainTopics": [
    {
      "title": "Topic name",
      "summary": "2-3 sentence summary",
      "depth": "primary|secondary|tertiary",
      "sourceRefs": [{ "chunkId": "source-chunk-N", "passage": "exact quoted text" }]
    }
  ],
  "keyConcepts": [
    {
      "term": "Concept name",
      "definition": "Clear definition",
      "context": "How it's used in this content",
      "importance": "critical|important|supplementary",
      "sourceRefs": [{ "chunkId": "source-chunk-N", "passage": "exact quoted text" }]
    }
  ],
  "definitions": [
    {
      "term": "Term",
      "definition": "Definition",
      "sourceRefs": [{ "chunkId": "source-chunk-N", "passage": "exact quoted text" }]
    }
  ],
  "examples": [
    {
      "description": "What the example illustrates",
      "relatedConcept": "Which concept this example supports",
      "sourceRefs": [{ "chunkId": "source-chunk-N", "passage": "exact quoted text" }]
    }
  ],
  "statistics": [
    {
      "value": "The statistic (e.g., '73% of respondents')",
      "context": "What this statistic means",
      "sourceRefs": [{ "chunkId": "source-chunk-N", "passage": "exact quoted text" }]
    }
  ],
  "relationships": [
    {
      "from": "Concept A",
      "to": "Concept B",
      "type": "causes|contrasts|supports|depends-on|part-of|similar-to",
      "description": "How they relate",
      "sourceRefs": [{ "chunkId": "source-chunk-N", "passage": "exact quoted text" }]
    }
  ],
  "timeline": [
    {
      "date": "Date or time period",
      "event": "What happened",
      "significance": "Why it matters",
      "sourceRefs": [{ "chunkId": "source-chunk-N", "passage": "exact quoted text" }]
    }
  ]
}

Return ONLY valid JSON. No markdown fences. Omit empty arrays.`;
}
```

---

## 2. Format-Specific Generators

### A) Podcast Script Generator

Transforms `DocumentKnowledge` into a conversational podcast script with two hosts.

```typescript
// ─── Podcast Types ───────────────────────────────────────────────────────────

interface PodcastConfig {
  style: 'deep-dive' | 'brief' | 'debate';
  durationMinutes: number;   // Target duration: 10, 20, or 45
  hostNames: [string, string]; // Two host names
  tone: 'casual' | 'professional' | 'academic';
  includeIntro: boolean;
  includeOutro: boolean;
}

interface PodcastSegment {
  speaker: string;
  text: string;
  direction?: string;       // e.g., "(enthusiastic)", "(thoughtful pause)"
  sourceRef?: SourceReference;
}

interface PodcastScript {
  title: string;
  estimatedDuration: number; // minutes
  segments: PodcastSegment[];
  showNotes: string;
  chapters: { timestamp: string; title: string }[];
}
```

**AI Prompt Template — Podcast Script:**

```
You are a podcast script writer creating a {style} episode.

HOSTS: {hostName1} and {hostName2}
TARGET DURATION: {durationMinutes} minutes (~{wordCount} words)
TONE: {tone}

SOURCE KNOWLEDGE:
{JSON.stringify(knowledge, null, 2)}

RULES:
- Create natural, conversational dialogue between the two hosts
- {hostName1} drives the conversation with questions and transitions
- {hostName2} provides deeper explanations and examples
- Include natural speech patterns: "Right, exactly", "That's fascinating", "So what you're saying is..."
- For "deep-dive": cover every major topic thoroughly with examples
- For "brief": hit only the top 3-5 key points, keep it punchy
- For "debate": hosts take opposing perspectives when reasonable, then find common ground
- EVERY factual claim must trace to a source — include sourceRef for verifiable statements
- Include direction cues in parentheses: (laughs), (thoughtful pause), (excited)
- Start with a hook that grabs attention in the first 15 seconds
- End with a clear takeaway or call to action

Return JSON matching the PodcastScript interface.
```

**Cross-reference:** See `content-repurposing-pipeline.md` for turning the script into actual audio using TTS, and `rss-podcast-integration.md` for distribution.

---

### B) Slide Deck Generator

```typescript
// ─── Slide Types ─────────────────────────────────────────────────────────────

interface SlideContent {
  title: string;
  subtitle?: string;
  slides: Slide[];
  theme: SlideTheme;
}

interface Slide {
  type: 'title' | 'content' | 'comparison' | 'timeline' | 'quote' | 'summary'
      | 'image-prompt' | 'two-column' | 'statistics' | 'diagram';
  title: string;
  bulletPoints?: string[];
  speakerNotes?: string;        // What the presenter should say
  imagePrompt?: string;         // Prompt for AI image generation (Gemini Imagen)
  sourceRef?: SourceReference;  // Which source this slide draws from
  leftColumn?: string[];        // For two-column and comparison slides
  rightColumn?: string[];
  leftLabel?: string;
  rightLabel?: string;
  statistic?: { value: string; label: string; context: string };
  quoteText?: string;
  quoteAttribution?: string;
  timelineEvents?: { date: string; event: string }[];
}

interface SlideTheme {
  primaryColor: string;
  secondaryColor: string;
  fontFamily: string;
  backgroundStyle: 'solid' | 'gradient' | 'image';
}

// ─── Slide Defaults ──────────────────────────────────────────────────────────

const DEFAULT_SLIDE_THEME: SlideTheme = {
  primaryColor: '#1a1a2e',
  secondaryColor: '#e94560',
  fontFamily: 'Inter, system-ui, sans-serif',
  backgroundStyle: 'gradient',
};
```

**AI Prompt Template — Slide Deck:**

```
You are a presentation designer. Create a slide deck from the following knowledge base.

TARGET: {slideCount} slides for a {durationMinutes}-minute presentation
AUDIENCE: {audience}

SOURCE KNOWLEDGE:
{JSON.stringify(knowledge, null, 2)}

SLIDE STRUCTURE GUIDELINES:
- Slide 1: Title slide with compelling subtitle
- Slide 2: Overview / agenda (3-5 main points)
- Slides 3-{N-2}: Content slides — one key idea per slide
  - Use "comparison" type when contrasting two things
  - Use "timeline" type for chronological content
  - Use "quote" type for powerful source quotes
  - Use "statistics" type for data-driven points
  - Use "two-column" for pros/cons, before/after, etc.
- Slide {N-1}: Key takeaways (3-5 bullet points)
- Slide {N}: Call to action or closing thought

RULES:
- Maximum 5 bullet points per slide (audience reads, not listens, if overloaded)
- Each bullet point: 8-12 words max
- Speaker notes: 2-4 sentences of what to SAY (not what's on the slide)
- Include imagePrompt for slides that benefit from visuals
  - Use descriptive prompts suitable for Gemini Imagen: "Professional photograph of..."
  - NEVER reference copyrighted characters or real people
- Every content slide must have a sourceRef tracing back to source material
- Slides should tell a STORY: setup → conflict/challenge → resolution → action

Return JSON matching the SlideContent interface.
```

**HTML Export (self-contained, single file):**

```typescript
// ─── Slide Deck → Self-Contained HTML ────────────────────────────────────────

function slidesToHTML(deck: SlideContent): string {
  const slideHTML = deck.slides.map((slide, index) => {
    let content = '';

    switch (slide.type) {
      case 'title':
        content = `
          <div class="slide slide-title">
            <h1>${escapeHtml(deck.title)}</h1>
            ${deck.subtitle ? `<p class="subtitle">${escapeHtml(deck.subtitle)}</p>` : ''}
          </div>`;
        break;

      case 'content':
        content = `
          <div class="slide slide-content">
            <h2>${escapeHtml(slide.title)}</h2>
            <ul>${(slide.bulletPoints ?? []).map(bp =>
              `<li>${escapeHtml(bp)}</li>`
            ).join('')}</ul>
          </div>`;
        break;

      case 'comparison':
        content = `
          <div class="slide slide-comparison">
            <h2>${escapeHtml(slide.title)}</h2>
            <div class="columns">
              <div class="column">
                <h3>${escapeHtml(slide.leftLabel ?? 'Option A')}</h3>
                <ul>${(slide.leftColumn ?? []).map(item =>
                  `<li>${escapeHtml(item)}</li>`
                ).join('')}</ul>
              </div>
              <div class="column">
                <h3>${escapeHtml(slide.rightLabel ?? 'Option B')}</h3>
                <ul>${(slide.rightColumn ?? []).map(item =>
                  `<li>${escapeHtml(item)}</li>`
                ).join('')}</ul>
              </div>
            </div>
          </div>`;
        break;

      case 'quote':
        content = `
          <div class="slide slide-quote">
            <blockquote>
              <p>"${escapeHtml(slide.quoteText ?? '')}"</p>
              ${slide.quoteAttribution
                ? `<cite>— ${escapeHtml(slide.quoteAttribution)}</cite>`
                : ''}
            </blockquote>
          </div>`;
        break;

      case 'statistics':
        content = `
          <div class="slide slide-statistics">
            <h2>${escapeHtml(slide.title)}</h2>
            ${slide.statistic ? `
              <div class="stat-block">
                <span class="stat-value">${escapeHtml(slide.statistic.value)}</span>
                <span class="stat-label">${escapeHtml(slide.statistic.label)}</span>
                <p class="stat-context">${escapeHtml(slide.statistic.context)}</p>
              </div>` : ''}
          </div>`;
        break;

      case 'timeline':
        content = `
          <div class="slide slide-timeline">
            <h2>${escapeHtml(slide.title)}</h2>
            <div class="timeline">
              ${(slide.timelineEvents ?? []).map(evt => `
                <div class="timeline-event">
                  <span class="timeline-date">${escapeHtml(evt.date)}</span>
                  <span class="timeline-desc">${escapeHtml(evt.event)}</span>
                </div>
              `).join('')}
            </div>
          </div>`;
        break;

      case 'summary':
        content = `
          <div class="slide slide-summary">
            <h2>${escapeHtml(slide.title)}</h2>
            <ul class="summary-list">${(slide.bulletPoints ?? []).map(bp =>
              `<li>${escapeHtml(bp)}</li>`
            ).join('')}</ul>
          </div>`;
        break;

      default:
        content = `
          <div class="slide slide-content">
            <h2>${escapeHtml(slide.title)}</h2>
            <ul>${(slide.bulletPoints ?? []).map(bp =>
              `<li>${escapeHtml(bp)}</li>`
            ).join('')}</ul>
          </div>`;
    }

    return `<section data-index="${index}">${content}</section>`;
  }).join('\n');

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${escapeHtml(deck.title)}</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: ${deck.theme.fontFamily}; background: #000; overflow: hidden; }
  section { display: none; width: 100vw; height: 100vh; padding: 60px 80px;
    background: linear-gradient(135deg, ${deck.theme.primaryColor}, #16213e);
    color: #fff; }
  section.active { display: flex; flex-direction: column; justify-content: center; }
  h1 { font-size: 3.5rem; margin-bottom: 0.5em; }
  h2 { font-size: 2.5rem; margin-bottom: 1em; color: ${deck.theme.secondaryColor}; }
  h3 { font-size: 1.5rem; margin-bottom: 0.5em; color: ${deck.theme.secondaryColor}; }
  ul { list-style: none; padding-left: 0; }
  li { font-size: 1.5rem; margin-bottom: 0.6em; padding-left: 1.5em;
    position: relative; line-height: 1.4; }
  li::before { content: "\\25B6"; position: absolute; left: 0;
    color: ${deck.theme.secondaryColor}; font-size: 0.8em; }
  .subtitle { font-size: 1.5rem; opacity: 0.8; }
  .columns { display: flex; gap: 60px; }
  .column { flex: 1; }
  blockquote { font-size: 2rem; font-style: italic; line-height: 1.6;
    border-left: 4px solid ${deck.theme.secondaryColor}; padding-left: 30px; }
  cite { display: block; margin-top: 1em; font-size: 1.2rem; opacity: 0.7; }
  .stat-block { text-align: center; margin-top: 2em; }
  .stat-value { font-size: 5rem; font-weight: bold; color: ${deck.theme.secondaryColor}; display: block; }
  .stat-label { font-size: 1.5rem; display: block; margin-top: 0.3em; }
  .stat-context { font-size: 1.1rem; opacity: 0.7; margin-top: 1em; }
  .timeline { position: relative; padding-left: 30px;
    border-left: 3px solid ${deck.theme.secondaryColor}; }
  .timeline-event { margin-bottom: 1.5em; }
  .timeline-date { font-weight: bold; color: ${deck.theme.secondaryColor};
    font-size: 1.2rem; display: block; }
  .timeline-desc { font-size: 1.3rem; }
  .nav-hint { position: fixed; bottom: 20px; right: 30px; font-size: 0.9rem;
    opacity: 0.4; color: #fff; }
  .slide-counter { position: fixed; bottom: 20px; left: 30px; font-size: 0.9rem;
    opacity: 0.4; color: #fff; }
</style>
</head>
<body>
${slideHTML}
<div class="nav-hint">Arrow keys or click to navigate</div>
<div class="slide-counter" id="counter"></div>
<script>
  const sections = document.querySelectorAll('section');
  let current = 0;
  function show(n) {
    sections.forEach(s => s.classList.remove('active'));
    current = Math.max(0, Math.min(n, sections.length - 1));
    sections[current].classList.add('active');
    document.getElementById('counter').textContent = (current + 1) + ' / ' + sections.length;
  }
  show(0);
  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight' || e.key === ' ') show(current + 1);
    if (e.key === 'ArrowLeft') show(current - 1);
    if (e.key === 'Home') show(0);
    if (e.key === 'End') show(sections.length - 1);
  });
  document.addEventListener('click', e => {
    if (e.clientX > window.innerWidth / 2) show(current + 1);
    else show(current - 1);
  });
</script>
</body>
</html>`;
}

function escapeHtml(str: string): string {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
```

---

### C) Flashcard Generator

```typescript
// ─── Flashcard Types ─────────────────────────────────────────────────────────

interface Flashcard {
  front: string;              // Question or concept
  back: string;               // Answer or definition
  difficulty: 'easy' | 'medium' | 'hard';
  tags: string[];
  source: string;             // Which document/page
  sourceRef: SourceReference;
  // Spaced repetition metadata
  sr: {
    interval: number;         // Days until next review (initial: 1)
    easeFactor: number;       // SM-2 ease factor (initial: 2.5)
    repetitions: number;      // Number of successful reviews (initial: 0)
    nextReview: string;       // ISO date string
  };
}

// ─── Generation from DocumentKnowledge ───────────────────────────────────────

function generateFlashcardsFromKnowledge(knowledge: DocumentKnowledge): Flashcard[] {
  const cards: Flashcard[] = [];
  const now = new Date().toISOString();

  // 1. Definition cards (easiest to generate, highest value)
  for (const def of knowledge.definitions) {
    cards.push({
      front: `Define: ${def.term}`,
      back: def.definition,
      difficulty: 'easy',
      tags: ['definition', ...extractTopicTags(def.term, knowledge)],
      source: def.sourceRefs[0]?.sourceTitle ?? 'Unknown',
      sourceRef: def.sourceRefs[0],
      sr: { interval: 1, easeFactor: 2.5, repetitions: 0, nextReview: now },
    });
  }

  // 2. Concept cards (test understanding, not just recall)
  for (const concept of knowledge.keyConcepts) {
    cards.push({
      front: `What is ${concept.term} and why does it matter?`,
      back: `${concept.definition}\n\nContext: ${concept.context}`,
      difficulty: concept.importance === 'critical' ? 'hard' : 'medium',
      tags: ['concept', concept.importance],
      source: concept.sourceRefs[0]?.sourceTitle ?? 'Unknown',
      sourceRef: concept.sourceRefs[0],
      sr: { interval: 1, easeFactor: 2.5, repetitions: 0, nextReview: now },
    });
  }

  // 3. Relationship cards (connect ideas)
  for (const rel of knowledge.relationships) {
    cards.push({
      front: `How does "${rel.from}" relate to "${rel.to}"?`,
      back: `Relationship type: ${rel.type}\n\n${rel.description}`,
      difficulty: 'hard',
      tags: ['relationship', rel.type],
      source: rel.sourceRefs[0]?.sourceTitle ?? 'Unknown',
      sourceRef: rel.sourceRefs[0],
      sr: { interval: 1, easeFactor: 2.5, repetitions: 0, nextReview: now },
    });
  }

  // 4. Example cards (apply knowledge)
  for (const example of knowledge.examples) {
    cards.push({
      front: `Give an example of "${example.relatedConcept}" in practice.`,
      back: example.description,
      difficulty: 'medium',
      tags: ['example', example.relatedConcept],
      source: example.sourceRefs[0]?.sourceTitle ?? 'Unknown',
      sourceRef: example.sourceRefs[0],
      sr: { interval: 1, easeFactor: 2.5, repetitions: 0, nextReview: now },
    });
  }

  // 5. Statistics cards (recall data points)
  for (const stat of knowledge.statistics) {
    cards.push({
      front: stat.context,
      back: stat.value,
      difficulty: 'medium',
      tags: ['statistic'],
      source: stat.sourceRefs[0]?.sourceTitle ?? 'Unknown',
      sourceRef: stat.sourceRefs[0],
      sr: { interval: 1, easeFactor: 2.5, repetitions: 0, nextReview: now },
    });
  }

  return cards;
}

function extractTopicTags(term: string, knowledge: DocumentKnowledge): string[] {
  return knowledge.mainTopics
    .filter(t => t.title.toLowerCase().includes(term.toLowerCase())
      || t.summary.toLowerCase().includes(term.toLowerCase()))
    .map(t => t.title.toLowerCase().replace(/\s+/g, '-'));
}
```

**Export Formats:**

```typescript
// ─── Flashcard Export ────────────────────────────────────────────────────────

// JSON export (universal)
function exportFlashcardsJSON(cards: Flashcard[]): string {
  return JSON.stringify(cards, null, 2);
}

// Anki-compatible CSV (importable via File > Import)
// Format: front<tab>back<tab>tags
function exportFlashcardsAnkiCSV(cards: Flashcard[]): string {
  const header = '#separator:tab\n#html:false\n#tags column:3\n';
  const rows = cards.map(c =>
    `${c.front}\t${c.back.replace(/\n/g, '<br>')}\t${c.tags.join(' ')}`
  );
  return header + rows.join('\n');
}

// Markdown export (human-readable study format)
function exportFlashcardsMarkdown(cards: Flashcard[]): string {
  const grouped = groupBy(cards, c => c.difficulty);
  let md = '# Flashcards\n\n';

  for (const [difficulty, group] of Object.entries(grouped)) {
    md += `## ${difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}\n\n`;
    for (const card of group as Flashcard[]) {
      md += `**Q:** ${card.front}\n\n`;
      md += `**A:** ${card.back}\n\n`;
      md += `*Source: ${card.source}*\n\n---\n\n`;
    }
  }

  return md;
}

function groupBy<T>(arr: T[], fn: (item: T) => string): Record<string, T[]> {
  return arr.reduce((acc, item) => {
    const key = fn(item);
    (acc[key] ??= []).push(item);
    return acc;
  }, {} as Record<string, T[]>);
}
```

---

### D) Quiz Generator

```typescript
// ─── Quiz Types ──────────────────────────────────────────────────────────────

interface QuizQuestion {
  type: 'multiple-choice' | 'true-false' | 'short-answer' | 'fill-blank';
  question: string;
  options?: string[];          // For multiple-choice (4 options, A-D)
  correctAnswer: string;
  explanation: string;         // Why this is the correct answer
  difficulty: 'easy' | 'medium' | 'hard';
  sourceReference: string;     // Cited source passage for verification
  topic: string;               // Which topic this tests
  bloomsLevel: 'remember' | 'understand' | 'apply' | 'analyze' | 'evaluate' | 'create';
}

interface Quiz {
  title: string;
  description: string;
  questions: QuizQuestion[];
  passingScore: number;        // Percentage (e.g., 70)
  timeLimit?: number;          // Minutes
  generatedFrom: string[];     // Source titles
}
```

**AI Prompt Template — Quiz Generation:**

```
You are a quiz generator creating assessment questions from source material.

TARGET: {questionCount} questions across multiple difficulty levels
DISTRIBUTION:
  - 30% easy (remember/understand — definitions, basic facts)
  - 40% medium (apply/analyze — use concepts in scenarios)
  - 30% hard (evaluate/create — judge, compare, synthesize)

QUESTION TYPES (mix all four):
  - multiple-choice: 4 options (A-D), exactly 1 correct
  - true-false: statement that is clearly true or false
  - short-answer: requires 1-3 sentence response
  - fill-blank: sentence with a key term removed

SOURCE KNOWLEDGE:
{JSON.stringify(knowledge, null, 2)}

CRITICAL RULES FOR MULTIPLE-CHOICE DISTRACTORS:
1. All wrong answers must be PLAUSIBLE — they should sound reasonable to someone
   who has not studied the material carefully
2. Avoid obviously wrong answers (e.g., joke answers, completely unrelated terms)
3. Use common misconceptions as distractors when possible
4. Distractors should be similar in length and structure to the correct answer
5. Avoid "all of the above" or "none of the above"
6. Randomize correct answer position (not always B or C)

CRITICAL RULES FOR ALL QUESTIONS:
1. Every question must be answerable from the source material alone
2. Include the exact source passage in sourceReference
3. The explanation must cite the source and explain WHY the answer is correct
4. For true-false: make false statements subtle (change one key detail, not everything)
5. For fill-blank: remove a SPECIFIC TERM, not a generic word
6. Tag each question with its Bloom's taxonomy level
7. NEVER test on information not present in the sources

Return JSON matching the Quiz interface.
```

**Distractor Generation Strategy:**

```typescript
// ─── Distractor Generation Patterns ──────────────────────────────────────────
// These patterns produce plausible wrong answers for multiple-choice questions.

type DistractorStrategy =
  | 'related-concept'     // A real concept from the sources, but not the answer
  | 'partial-truth'       // Correct premise + wrong conclusion
  | 'common-misconception'// What someone might guess without studying
  | 'similar-term'        // A term that sounds like the right answer
  | 'opposite'            // The inverse of the correct answer
  | 'overgeneralization'; // Takes the correct answer too far

// Example: If the correct answer is "Photosynthesis converts CO2 and water into glucose"
// Distractors:
//   related-concept:      "Cellular respiration converts glucose into ATP"
//   partial-truth:        "Photosynthesis converts oxygen and water into glucose"
//   common-misconception: "Photosynthesis converts sunlight directly into food"
//   overgeneralization:   "Photosynthesis converts all gases into glucose"

// The AI prompt above handles this, but for programmatic generation:
function buildDistractorPrompt(
  correctAnswer: string,
  knowledge: DocumentKnowledge,
  strategy: DistractorStrategy
): string {
  return `Generate a plausible but INCORRECT answer using the "${strategy}" strategy.
Correct answer: "${correctAnswer}"
Available concepts: ${knowledge.keyConcepts.map(c => c.term).join(', ')}
The distractor must sound reasonable and be similar in length to the correct answer.
Return ONLY the distractor text, nothing else.`;
}
```

---

### E) Summary Generator

Three lengths for different channels:

```typescript
// ─── Summary Types ───────────────────────────────────────────────────────────

type SummaryLength = 'short' | 'medium' | 'long';

interface SummaryConfig {
  length: SummaryLength;
  audience: 'general' | 'technical' | 'executive' | 'ministry';
  includeSourceCitations: boolean;
}

// ─── Summary Length Specifications ───────────────────────────────────────────

const SUMMARY_SPECS: Record<SummaryLength, { words: string; useCase: string; prompt: string }> = {
  short: {
    words: '25-50',
    useCase: 'Social media post, executive one-liner, email subject preview',
    prompt: `Write a 1-2 sentence summary (25-50 words) that captures the single most important
takeaway. This will be used for social media or as an executive brief. Be punchy and specific.
Do NOT start with "This document..." — start with the insight itself.`,
  },
  medium: {
    words: '100-200',
    useCase: 'Newsletter paragraph, email body, meeting notes',
    prompt: `Write a 1-paragraph summary (100-200 words) covering the main argument, key
supporting points, and conclusion. This will be used in newsletters or email communications.
Use clear, professional language. Cite specific findings or data points from the sources.`,
  },
  long: {
    words: '500-1000',
    useCase: 'Blog post, study guide, comprehensive briefing',
    prompt: `Write a full-page summary (500-1000 words) organized with headers and sections.
Include:
- An introduction that frames the topic
- Key findings or arguments (3-5 sections with headers)
- Supporting evidence and examples from the sources
- A conclusion with implications or action items
- Inline citations referencing specific source passages

Format as Markdown with ## headers. This will serve as a standalone blog post or study guide.`,
  },
};
```

**AI Prompt Template — Summary:**

```
You are a content summarizer. Generate a {length} summary of the following knowledge base.

AUDIENCE: {audience}
LENGTH SPEC: {SUMMARY_SPECS[length].words} words
USE CASE: {SUMMARY_SPECS[length].useCase}

{SUMMARY_SPECS[length].prompt}

SOURCE KNOWLEDGE:
{JSON.stringify(knowledge, null, 2)}

RULES:
- Use ONLY information from the provided sources
- {includeSourceCitations ? 'Include inline citations in [Source: title] format' : 'No citations needed'}
- Match the tone to the audience:
  - general: clear, jargon-free, engaging
  - technical: precise, domain-specific terms OK
  - executive: bottom-line-up-front, action-oriented
  - ministry: warm, scripture-grounded, pastoral

Return the summary as plain text (short/medium) or Markdown (long).
```

---

### F) FAQ Generator

```typescript
// ─── FAQ Types ───────────────────────────────────────────────────────────────

interface FAQ {
  question: string;
  answer: string;
  category: string;           // Topic grouping
  sourceRef: SourceReference;
  confidence: 'high' | 'medium'; // How directly the source addresses this
}

interface FAQCollection {
  title: string;
  description: string;
  faqs: FAQ[];
  generatedFrom: string[];
}
```

**AI Prompt Template — FAQ:**

```
You are generating a FAQ document from source material.

SOURCE KNOWLEDGE:
{JSON.stringify(knowledge, null, 2)}

Generate 10-20 frequently asked questions that a reader would likely have after
encountering this material. Organize by topic category.

QUESTION TYPES TO INCLUDE:
1. "What is...?" — Basic understanding questions (from definitions)
2. "How does...?" — Process/mechanism questions (from relationships)
3. "Why is...important?" — Significance questions (from key concepts)
4. "What's the difference between...?" — Comparison questions (from relationships)
5. "Can you give an example of...?" — Application questions (from examples)
6. "What does the data show about...?" — Evidence questions (from statistics)

RULES:
- Every answer must be grounded in the source material
- Include the exact source passage in the sourceRef
- If the sources don't fully address a likely question, set confidence to "medium"
  and note "Based on available sources..." in the answer
- Never fabricate answers — if the sources don't cover it, skip the question
- Answers should be concise (2-5 sentences) but complete
- Group FAQs by category matching the main topics

Return JSON matching the FAQCollection interface.
```

---

### G) Study Guide Generator

```typescript
// ─── Study Guide Types ───────────────────────────────────────────────────────

interface StudyGuideSection {
  title: string;
  learningObjectives: string[];
  keyTerms: { term: string; definition: string }[];
  conceptSummary: string;
  practiceQuestions: string[];
  reflectionPrompts: string[];  // Open-ended thinking questions
  sourceRefs: SourceReference[];
}

interface StudyGuide {
  title: string;
  overview: string;
  sections: StudyGuideSection[];
  reviewChecklist: string[];    // "I can explain...", "I understand..."
  suggestedReadings: string[];  // From source references
}
```

**AI Prompt Template — Study Guide:**

```
You are creating a study guide from source material for active learning.

SOURCE KNOWLEDGE:
{JSON.stringify(knowledge, null, 2)}

Create a structured study guide with these components per section:
1. Learning objectives (what the student will be able to do after studying)
2. Key terms with definitions
3. Concept summary (2-3 paragraphs)
4. Practice questions (factual recall)
5. Reflection prompts (higher-order thinking — "How would you apply..." or "Compare...")

End with a self-assessment checklist: "After studying, I can..."
- Use "I can explain..." for understanding
- Use "I can compare..." for analysis
- Use "I can apply..." for application

RULES:
- Every fact must trace to source material
- Learning objectives should use Bloom's taxonomy verbs
- Reflection prompts should encourage connections between topics
- Keep language accessible — define jargon on first use

Return JSON matching the StudyGuide interface.
```

---

### H) Infographic Data Extractor

```typescript
// ─── Infographic Data ────────────────────────────────────────────────────────
// Extracts structured data suitable for visual infographic tools
// (Canva, Figma, or programmatic SVG generation).

interface InfographicData {
  title: string;
  subtitle: string;
  sections: InfographicSection[];
}

interface InfographicSection {
  type: 'stat-block' | 'comparison' | 'process-flow' | 'timeline'
      | 'pie-data' | 'bar-data' | 'icon-grid' | 'quote-block';
  title: string;
  data: Record<string, unknown>;
  sourceRef: SourceReference;
}

// Example output:
// { type: 'stat-block', title: 'Key Findings', data: {
//     stats: [
//       { value: '73%', label: 'of churches use digital media', icon: 'church' },
//       { value: '2.5x', label: 'engagement increase with video', icon: 'video' },
//     ]
// }}
```

---

## 3. Complete Pipeline Class

```typescript
// ─── Multi-Format Generator Pipeline ─────────────────────────────────────────

import Anthropic from '@anthropic-ai/sdk';
import { GoogleGenerativeAI } from '@google/generative-ai';

interface GeneratorConfig {
  aiProvider: 'gemini' | 'claude';
  modelOverride?: string;     // Override default model
  maxTokens?: number;         // Override default max tokens (default: 8192)
}

interface MultiFormatOutput {
  knowledge: DocumentKnowledge;
  podcast: PodcastScript;
  slides: SlideContent;
  flashcards: Flashcard[];
  quiz: Quiz;
  summaries: { short: string; medium: string; long: string };
  faq: FAQCollection;
  studyGuide: StudyGuide;
  infographic: InfographicData;
}

class MultiFormatGenerator {
  private config: GeneratorConfig;
  private anthropic: Anthropic | null = null;
  private gemini: GoogleGenerativeAI | null = null;

  constructor(config: GeneratorConfig) {
    this.config = config;

    if (config.aiProvider === 'claude') {
      this.anthropic = new Anthropic();
    } else {
      this.gemini = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
    }
  }

  // ─── Core AI Call ──────────────────────────────────────────────────────

  private async callAI(prompt: string): Promise<string> {
    const maxTokens = this.config.maxTokens ?? 8192;

    if (this.config.aiProvider === 'claude') {
      const model = this.config.modelOverride ?? 'claude-sonnet-4-20250514';
      const response = await this.anthropic!.messages.create({
        model,
        max_tokens: maxTokens,
        messages: [{ role: 'user', content: prompt }],
      });
      return response.content[0].type === 'text' ? response.content[0].text : '';
    } else {
      const model = this.config.modelOverride ?? 'gemini-2.5-pro';
      const genModel = this.gemini!.getGenerativeModel({ model });
      const result = await genModel.generateContent(prompt);
      const text = result.response.text();
      return text.replace(/^```json\n?/, '').replace(/\n?```$/, '');
    }
  }

  private async callAIJSON<T>(prompt: string): Promise<T> {
    const text = await this.callAI(prompt);
    return JSON.parse(text);
  }

  // ─── Step 1: Understand ────────────────────────────────────────────────

  async understand(sources: DocumentSource[]): Promise<DocumentKnowledge> {
    // Parse all sources into text
    const allChunks: DocumentChunk[] = [];

    for (const source of sources) {
      const text = await extractText(source);
      const sourceId = source.metadata.title.toLowerCase().replace(/\s+/g, '-');
      const chunks = chunkDocument(text, sourceId, source.metadata.title);
      allChunks.push(...chunks);
    }

    // Extract knowledge via AI
    const prompt = buildExtractionPrompt(allChunks);
    const knowledge = await this.callAIJSON<DocumentKnowledge>(prompt);

    knowledge.totalSources = sources.length;
    knowledge.totalChunks = allChunks.length;
    knowledge.processingDate = new Date().toISOString();

    return knowledge;
  }

  // ─── Step 2: Generate Individual Formats ───────────────────────────────

  async generatePodcast(
    knowledge: DocumentKnowledge,
    config: PodcastConfig = {
      style: 'deep-dive',
      durationMinutes: 20,
      hostNames: ['Alex', 'Jordan'],
      tone: 'casual',
      includeIntro: true,
      includeOutro: true,
    }
  ): Promise<PodcastScript> {
    const wordCount = config.durationMinutes * 150; // ~150 words/minute spoken
    const prompt = `You are a podcast script writer creating a ${config.style} episode.
HOSTS: ${config.hostNames[0]} and ${config.hostNames[1]}
TARGET DURATION: ${config.durationMinutes} minutes (~${wordCount} words)
TONE: ${config.tone}
${config.includeIntro ? 'Include a 30-second intro hook.' : 'Skip intro, jump straight in.'}
${config.includeOutro ? 'Include a closing summary and call to action.' : 'End after the last point.'}

SOURCE KNOWLEDGE:
${JSON.stringify(knowledge, null, 2)}

Return JSON matching: { title, estimatedDuration, segments: [{ speaker, text, direction?, sourceRef? }], showNotes, chapters: [{ timestamp, title }] }
Every factual claim must include a sourceRef. Return ONLY valid JSON.`;

    return this.callAIJSON<PodcastScript>(prompt);
  }

  async generateSlides(
    knowledge: DocumentKnowledge,
    slideCount: number = 12,
    durationMinutes: number = 15
  ): Promise<SlideContent> {
    const prompt = `You are a presentation designer. Create a ${slideCount}-slide deck for a ${durationMinutes}-minute presentation.

SOURCE KNOWLEDGE:
${JSON.stringify(knowledge, null, 2)}

Use these slide types: title, content, comparison, timeline, quote, summary, statistics, two-column.
Maximum 5 bullet points per slide, 8-12 words each. Include speakerNotes (2-4 sentences of what to SAY).
Include imagePrompt for visual slides (descriptive prompts for Gemini Imagen, no copyrighted content).
Every content slide must have a sourceRef.

Return JSON matching: { title, subtitle?, slides: [{ type, title, bulletPoints?, speakerNotes?, imagePrompt?, sourceRef?, leftColumn?, rightColumn?, leftLabel?, rightLabel?, statistic?, quoteText?, quoteAttribution?, timelineEvents? }], theme: { primaryColor: "#1a1a2e", secondaryColor: "#e94560", fontFamily: "Inter, system-ui, sans-serif", backgroundStyle: "gradient" } }
Return ONLY valid JSON.`;

    return this.callAIJSON<SlideContent>(prompt);
  }

  async generateFlashcards(knowledge: DocumentKnowledge): Promise<Flashcard[]> {
    // Use the programmatic generator for consistency and source fidelity
    return generateFlashcardsFromKnowledge(knowledge);
  }

  async generateQuiz(
    knowledge: DocumentKnowledge,
    questionCount: number = 15
  ): Promise<Quiz> {
    const prompt = `You are a quiz generator. Create ${questionCount} questions.
DISTRIBUTION: 30% easy, 40% medium, 30% hard.
TYPES: multiple-choice, true-false, short-answer, fill-blank (mix all four).

SOURCE KNOWLEDGE:
${JSON.stringify(knowledge, null, 2)}

RULES:
- All questions answerable from sources alone
- Multiple-choice: 4 plausible options, randomize correct answer position
- Distractors must be plausible (related concepts, partial truths, common misconceptions)
- No "all of the above" or "none of the above"
- Every question includes sourceReference (exact passage) and explanation
- Tag each with bloomsLevel: remember|understand|apply|analyze|evaluate|create

Return JSON matching: { title, description, questions: [{ type, question, options?, correctAnswer, explanation, difficulty, sourceReference, topic, bloomsLevel }], passingScore: 70, generatedFrom: [source titles] }
Return ONLY valid JSON.`;

    return this.callAIJSON<Quiz>(prompt);
  }

  async generateSummary(
    knowledge: DocumentKnowledge,
    length: SummaryLength = 'medium'
  ): Promise<string> {
    const spec = SUMMARY_SPECS[length];
    const prompt = `${spec.prompt}

SOURCE KNOWLEDGE:
${JSON.stringify(knowledge, null, 2)}

Use ONLY information from the sources. Include inline citations in [Source: title] format for the long summary.
Return plain text (short/medium) or Markdown (long). No JSON wrapper.`;

    return this.callAI(prompt);
  }

  async generateFAQ(knowledge: DocumentKnowledge): Promise<FAQCollection> {
    const prompt = `Generate 10-20 FAQ entries from this knowledge base. Group by topic category.
Include: "What is...?", "How does...?", "Why is...important?", "What's the difference...?", "Can you give an example...?"

SOURCE KNOWLEDGE:
${JSON.stringify(knowledge, null, 2)}

RULES: Every answer grounded in sources. Include sourceRef with exact passage. 2-5 sentence answers.
Return JSON matching: { title, description, faqs: [{ question, answer, category, sourceRef, confidence }], generatedFrom: [source titles] }
Return ONLY valid JSON.`;

    return this.callAIJSON<FAQCollection>(prompt);
  }

  async generateStudyGuide(knowledge: DocumentKnowledge): Promise<StudyGuide> {
    const prompt = `Create a study guide from this knowledge base.
Per section: learning objectives (Bloom's verbs), key terms, concept summary, practice questions, reflection prompts.
End with self-assessment checklist: "I can explain...", "I can compare...", "I can apply..."

SOURCE KNOWLEDGE:
${JSON.stringify(knowledge, null, 2)}

Return JSON matching: { title, overview, sections: [{ title, learningObjectives, keyTerms: [{ term, definition }], conceptSummary, practiceQuestions, reflectionPrompts, sourceRefs }], reviewChecklist, suggestedReadings }
Return ONLY valid JSON.`;

    return this.callAIJSON<StudyGuide>(prompt);
  }

  async generateInfographic(knowledge: DocumentKnowledge): Promise<InfographicData> {
    const prompt = `Extract structured data for an infographic from this knowledge base.
Section types: stat-block, comparison, process-flow, timeline, pie-data, bar-data, icon-grid, quote-block.
Select the most visually impactful data points.

SOURCE KNOWLEDGE:
${JSON.stringify(knowledge, null, 2)}

Return JSON matching: { title, subtitle, sections: [{ type, title, data: {...}, sourceRef }] }
Return ONLY valid JSON.`;

    return this.callAIJSON<InfographicData>(prompt);
  }

  // ─── Step 3: Generate All Formats ──────────────────────────────────────

  async generateAll(sources: DocumentSource[]): Promise<MultiFormatOutput> {
    console.log(`Processing ${sources.length} source(s)...`);

    // Step 1: Build shared understanding
    console.log('Step 1/3: Building shared understanding layer...');
    const knowledge = await this.understand(sources);
    console.log(`  Extracted: ${knowledge.keyConcepts.length} concepts, ${knowledge.definitions.length} definitions, ${knowledge.relationships.length} relationships`);

    // Step 2: Generate all formats in parallel
    console.log('Step 2/3: Generating all formats in parallel...');
    const [podcast, slides, quiz, shortSummary, mediumSummary, longSummary, faq, studyGuide, infographic] =
      await Promise.all([
        this.generatePodcast(knowledge),
        this.generateSlides(knowledge),
        this.generateQuiz(knowledge),
        this.generateSummary(knowledge, 'short'),
        this.generateSummary(knowledge, 'medium'),
        this.generateSummary(knowledge, 'long'),
        this.generateFAQ(knowledge),
        this.generateStudyGuide(knowledge),
        this.generateInfographic(knowledge),
      ]);

    // Flashcards are generated programmatically (no AI call needed)
    const flashcards = await this.generateFlashcards(knowledge);

    console.log('Step 3/3: Complete!');
    console.log(`  Podcast: ${podcast.segments.length} segments (~${podcast.estimatedDuration} min)`);
    console.log(`  Slides: ${slides.slides.length} slides`);
    console.log(`  Flashcards: ${flashcards.length} cards`);
    console.log(`  Quiz: ${quiz.questions.length} questions`);
    console.log(`  FAQ: ${faq.faqs.length} entries`);
    console.log(`  Study Guide: ${studyGuide.sections.length} sections`);

    return {
      knowledge,
      podcast,
      slides,
      flashcards,
      quiz,
      summaries: { short: shortSummary, medium: mediumSummary, long: longSummary },
      faq,
      studyGuide,
      infographic,
    };
  }
}
```

---

## 4. Ministry / Church Use Cases

### Sermon to Full Content Suite

```
SUNDAY SERMON (45 min video/audio)
  │
  ├── content-repurposing-pipeline.md    ← Video clips, audiograms, quote cards
  │     (FFmpeg + Sharp + transcription)
  │
  └── multi-format-content-generator.md  ← This skill
        │
        ├── Podcast Script     → Two hosts discuss the sermon's key points
        │                        (feed to TTS for audio, or use as study guide)
        ├── Slide Deck         → Small group leader presentation (10 slides)
        ├── Flashcards         → Scripture memory + key terms (Anki export)
        ├── Quiz               → Sunday School assessment or self-study
        ├── Summary (short)    → Social media caption for Monday post
        ├── Summary (medium)   → Wednesday newsletter paragraph
        ├── Summary (long)     → Blog post / sermon notes page
        ├── FAQ                → "Questions from the sermon" web page
        ├── Study Guide        → Mid-week Bible study handout
        └── Infographic Data   → Visual recap for Instagram carousel
```

### Bible Study Material to Learning Suite

```typescript
// Example: Generate full learning suite from Bible study notes

const generator = new MultiFormatGenerator({ aiProvider: 'claude' });

const sources: DocumentSource[] = [
  {
    type: 'pdf',
    path: './resources/romans-8-study-notes.pdf',
    metadata: { title: 'Romans 8 Study Notes', author: 'Pastor James' },
  },
  {
    type: 'markdown',
    path: './resources/romans-8-commentary.md',
    metadata: { title: 'Romans 8 Commentary Excerpts' },
  },
  {
    type: 'youtube',
    url: 'https://youtube.com/watch?v=example123',
    metadata: { title: 'Romans 8 Teaching - Sunday Service', date: '2026-03-09' },
  },
];

const output = await generator.generateAll(sources);

// Export flashcards as Anki deck
const ankiCSV = exportFlashcardsAnkiCSV(output.flashcards);
await fs.writeFile('./output/romans-8-flashcards.csv', ankiCSV);

// Export slides as self-contained HTML
const slidesHTML = slidesToHTML(output.slides);
await fs.writeFile('./output/romans-8-slides.html', slidesHTML);

// Export quiz as JSON for LMS import
await fs.writeFile('./output/romans-8-quiz.json', JSON.stringify(output.quiz, null, 2));

// Export study guide as Markdown
await fs.writeFile('./output/romans-8-study-guide.md', output.summaries.long);
```

### Church Annual Report to Stakeholder Formats

```typescript
// Annual report → multiple audience-specific outputs

const reportSources: DocumentSource[] = [
  { type: 'pdf', path: './reports/2025-annual-report.pdf',
    metadata: { title: '2025 Annual Report' } },
  { type: 'docx', path: './reports/financials-2025.docx',
    metadata: { title: '2025 Financial Summary' } },
];

const knowledge = await generator.understand(reportSources);

// Different summaries for different audiences
const boardBrief = await generator.generateSummary(knowledge, 'short');
// → "Faith Community grew 23% in 2025, launching 3 new ministries..."

const newsletterParagraph = await generator.generateSummary(knowledge, 'medium');
// → Full paragraph for church newsletter

const websitePost = await generator.generateSummary(knowledge, 'long');
// → Full blog post with headers, stats, and citations

// FAQ for congregation
const faq = await generator.generateFAQ(knowledge);
// → "Where did the building fund money go?", "How many new members joined?", etc.

// Infographic data for social media
const infographic = await generator.generateInfographic(knowledge);
// → Stat blocks, pie chart data, timeline of key events
```

---

## 5. Grounded Generation Pattern

The most important architectural principle, borrowed from Google NotebookLM:

### Source-Only Generation

```
┌──────────────────────────────────────────────────────┐
│                    THE GOLDEN RULE                     │
│                                                       │
│  ALL generated content must come from uploaded         │
│  sources. NEVER use AI training data for facts.        │
│  The AI is a TRANSFORMER of source content,            │
│  not a CREATOR of new information.                     │
│                                                       │
│  Training data is used ONLY for:                       │
│    - Language fluency (grammar, phrasing)              │
│    - Format knowledge (how a quiz looks)               │
│    - Structural patterns (how slides flow)             │
│                                                       │
│  Training data is NEVER used for:                      │
│    - Facts, statistics, or claims                      │
│    - Definitions or explanations                       │
│    - Examples or illustrations                         │
│    - Quotes or attributions                            │
└──────────────────────────────────────────────────────┘
```

### Inline Citation Protocol

Every generated item carries a `sourceRef` that traces back to an exact passage:

```typescript
// Every factual claim → exact source passage
interface SourceReference {
  sourceId: string;       // Which document
  sourceTitle: string;    // Human-readable title
  chunkId: string;        // Which chunk within the document
  passage: string;        // EXACT quoted text (not paraphrased)
  pageNumber?: number;    // If available from PDF parsing
}

// Verification: for any generated fact, you can:
// 1. Find the sourceRef
// 2. Look up the chunk by chunkId
// 3. Ctrl+F the exact passage in the original document
// 4. Confirm the generated content faithfully represents the source
```

### Faithfulness Check

Run after generation to verify every claim maps to a source:

```typescript
// ─── Faithfulness Verification ───────────────────────────────────────────────

interface FaithfulnessResult {
  totalClaims: number;
  verifiedClaims: number;
  unverifiedClaims: string[];
  faithfulnessScore: number;  // 0.0 to 1.0
}

async function checkFaithfulness(
  generatedContent: string,
  chunks: DocumentChunk[],
  aiProvider: 'claude' | 'gemini',
  callAI: (prompt: string) => Promise<string>
): Promise<FaithfulnessResult> {
  const prompt = `You are a faithfulness auditor. Compare the generated content against the source chunks.

GENERATED CONTENT:
${generatedContent}

SOURCE CHUNKS:
${chunks.map((c, i) => `[CHUNK ${i + 1} | ${c.sourceTitle}]\n${c.text}`).join('\n\n')}

For EACH factual claim in the generated content:
1. Identify the claim
2. Find the supporting source chunk (if any)
3. Judge: VERIFIED (direct support in sources) or UNVERIFIED (no source support)

Return JSON:
{
  "totalClaims": <number>,
  "verifiedClaims": <number>,
  "unverifiedClaims": ["claim text 1", "claim text 2"],
  "faithfulnessScore": <0.0 to 1.0>
}

Be strict: paraphrasing is OK, but adding facts not in the sources is UNVERIFIED.
Return ONLY valid JSON.`;

  const result = await callAI(prompt);
  return JSON.parse(result);
}
```

### Why This Matters

1. **Trust:** Users know every generated quiz question, flashcard, and summary comes from *their* documents, not the AI's general knowledge.
2. **Accuracy:** Eliminates hallucination for document-grounded tasks. The AI transforms, it does not invent.
3. **Auditability:** Any stakeholder can trace a generated claim back to the exact source passage. Critical for ministry contexts where doctrinal accuracy matters.
4. **Legal safety:** Generated content is derived from user-owned sources, not from AI training data of unknown provenance.

---

## 6. File Output Reference

```
output/
├── knowledge.json           # DocumentKnowledge (shared understanding)
├── podcast-script.json      # PodcastScript with segments and chapters
├── slides.html              # Self-contained HTML presentation
├── slides.json              # Raw slide data (for PPTX generation tools)
├── flashcards.json          # All flashcards with SR metadata
├── flashcards-anki.csv      # Anki-importable CSV
├── flashcards.md            # Human-readable Markdown
├── quiz.json                # Quiz with questions and answers
├── summary-short.txt        # 1-2 sentence summary
├── summary-medium.txt       # 1 paragraph summary
├── summary-long.md          # Full blog post / study guide
├── faq.json                 # FAQ collection
├── study-guide.json         # Structured study guide
├── study-guide.md           # Markdown study guide
├── infographic-data.json    # Structured data for visual tools
└── faithfulness-report.json # Verification results
```

---

## 7. Integration with Existing Skills

This skill is designed to work alongside other Dominion Flow creative-multimedia skills:

| Skill | Role in Pipeline |
|-------|-----------------|
| `content-repurposing-pipeline.md` | **Upstream:** Handles video/audio → clips, audiograms, quote cards. This skill handles document → multi-format text/structured output. Together they cover the full sermon-to-content pipeline. |
| `ffmpeg-command-generator.md` | Used by content-repurposing-pipeline for media processing. This skill does not call FFmpeg directly. |
| `transcription-pipeline-selector.md` | Provides the transcription step that feeds into the understanding layer when starting from audio/video. |
| `NOTEBOOKLM_RAG_AI_COURSE_GENERATION.md` | **Parallel architecture:** Both use RAG + source-grounded generation. NotebookLM skill focuses on LMS course creation (lessons, assignments, grading). This skill focuses on broader format fan-out (slides, cards, quizzes, podcasts). Share the same embedding and chunking infrastructure. |
| `data-visualization-generator.md` | Can consume the `infographic` output from this pipeline to generate actual SVG/chart visuals. |
| `image-optimization-pipeline.md` | Optimizes generated quote cards and infographic images for web delivery. |

---

## 8. Dependencies

```json
{
  "dependencies": {
    "@anthropic-ai/sdk": "^0.39.0",
    "@google/generative-ai": "^0.21.0",
    "pdf-parse": "^1.1.1",
    "mammoth": "^1.8.0",
    "youtube-transcript": "^1.2.1",
    "sharp": "^0.33.2"
  }
}
```

**Required environment variables (pick one AI provider):**

```bash
# Claude (recommended for long-form generation)
ANTHROPIC_API_KEY=your_key_here

# Gemini (recommended for embedding + generation in same ecosystem)
GEMINI_API_KEY=your_key_here
```

---

## Research Citations

---

## Related Skills

- `creative-multimedia/content-repurposing-pipeline.md` -- Video/audio repurposing (FFmpeg + Sharp + transcription)
- `advanced-features/NOTEBOOKLM_RAG_AI_COURSE_GENERATION.md` -- RAG-based course creation with pgvector
- `integrations/rss-podcast-integration.md` -- Podcast distribution after script generation
- `creative-multimedia/data-visualization-generator.md` -- Chart/SVG generation from infographic data
- `creative-multimedia/image-optimization-pipeline.md` -- Image optimization for generated assets
- `creative-multimedia/svg-generation.md` -- SVG patterns for infographic rendering
