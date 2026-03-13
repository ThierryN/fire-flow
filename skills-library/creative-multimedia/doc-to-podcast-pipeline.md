---
name: doc-to-podcast-pipeline
category: creative-multimedia
version: 1.0.0
contributed: 2026-03-10
contributor: dominion-flow-research
last_updated: 2026-03-10
tags: [podcast, pipeline, document-to-audio, notebooklm, architecture, end-to-end, ffmpeg, tts, rag]
difficulty: hard
---

# Document-to-Podcast Pipeline
## Description

End-to-end pipeline that transforms any document (PDF, DOCX, URL, YouTube transcript) into a
polished podcast episode with multiple speakers, natural conversation flow, intro/outro music,
and broadcast-quality loudness normalization. Combines RAG-based content understanding, multi-agent
script generation (PodAgent pattern), neural TTS synthesis, and FFmpeg audio composition into a
single automated workflow.

This is the "full stack" audio generation skill -- it orchestrates capabilities from several
sibling skills (transcription-pipeline-selector, ffmpeg-command-generator, audio-enhancement-pipeline,
content-repurposing-pipeline) into one cohesive pipeline.

## When to Use

- Transforming written documents (PDFs, articles, papers) into listenable podcast episodes
- Building a NotebookLM-style "Audio Overview" feature for your application
- Converting sermons, Bible studies, or teaching notes into podcast format
- Creating educational audio content from textbooks or course materials
- Automating podcast production from blog posts or newsletters
- Building an internal tool that generates audio briefings from reports

## Related Skills

- `transcription-pipeline-selector.md` -- Input stage: transcribe audio/video sources before processing
- `ffmpeg-command-generator.md` -- Output stage: all FFmpeg commands for audio composition
- `audio-enhancement-pipeline.md` -- Post-production: loudness normalization, noise reduction
- `content-repurposing-pipeline.md` -- Broader pipeline: podcast is one output format among many
- `podcast-script-generation.md` -- Stage 3 deep-dive: PodAgent multi-agent script writing

---

## Architecture Overview

### The 4-Stage Pipeline

```
Stage 1: INGEST     --> Parse documents, extract text, chunk semantically
Stage 2: UNDERSTAND --> RAG retrieval, key point extraction, outline generation
Stage 3: SCRIPT     --> Multi-agent podcast script generation (PodAgent pattern)
Stage 4: SYNTHESIZE --> TTS audio generation, mixing, post-production
```

### Full Architecture Diagram

```
+--------------------------------------------------+
|              DOCUMENT SOURCES                     |
|  [PDF] [DOCX] [URL] [YouTube] [Audio/Video]      |
+--------------------------------------------------+
                      |
                      v
+--------------------------------------------------+
|         STAGE 1: INGEST                           |
|                                                   |
|  Document Parser (pdf-parse / mammoth / cheerio)  |
|         |                                         |
|         v                                         |
|  [Clean Text + Metadata]                          |
|         |                                         |
|         v                                         |
|  Semantic Chunker (400-600 tokens, 50 overlap)    |
|         |                                         |
|         v                                         |
|  [Chunks + Embeddings --> Vector DB]              |
+--------------------------------------------------+
                      |
                      v
+--------------------------------------------------+
|         STAGE 2: UNDERSTAND                       |
|                                                   |
|  Key Point Extractor (AI)                         |
|         |                                         |
|         v                                         |
|  [Ranked Discussion Points]                       |
|         |                                         |
|         v                                         |
|  Outline Generator (AI)                           |
|         |                                         |
|         v                                         |
|  [Podcast Outline: Intro -> Segments -> Outro]    |
+--------------------------------------------------+
                      |
                      v
+--------------------------------------------------+
|         STAGE 3: SCRIPT                           |
|                                                   |
|  Multi-Agent Script Writer (PodAgent pattern)     |
|    - Host Agent: drives conversation              |
|    - Guest Agent: provides expert responses       |
|    - Writer Agent: structures + verifies          |
|         |                                         |
|         v                                         |
|  [Structured Script JSON]                         |
|    { speaker, text, emotion, duration }[]         |
+--------------------------------------------------+
                      |
                      v
+--------------------------------------------------+
|         STAGE 4: SYNTHESIZE                       |
|                                                   |
|  TTS Engine (per segment, per speaker)            |
|         |                                         |
|         v                                         |
|  [Audio Segments WAV]                             |
|         |                                         |
|         v                                         |
|  FFmpeg Composer                                  |
|    - Concatenate segments                         |
|    - Insert pauses (200-500ms)                    |
|    - Add intro/outro music                        |
|    - Normalize loudness (EBU R128, -16 LUFS)      |
|         |                                         |
|         v                                         |
|  [Final Podcast MP3 + ID3 Metadata]               |
+--------------------------------------------------+
```

---

## Stage 1: Document Ingestion

The ingestion stage accepts multiple document formats and produces clean, chunked text ready
for AI understanding. Each parser extracts both text content and structural metadata (titles,
headings, page numbers) to preserve document context.

### Dependencies

```json
{
  "dependencies": {
    "pdf-parse": "^1.1.1",
    "mammoth": "^1.8.0",
    "@mozilla/readability": "^0.5.0",
    "cheerio": "^1.0.0",
    "linkedom": "^0.18.0",
    "youtube-transcript": "^1.2.1"
  }
}
```

### PDF Parser

```typescript
import pdfParse from 'pdf-parse';
import { readFile } from 'fs/promises';

interface ParsedDocument {
  text: string;
  metadata: {
    title: string;
    author: string;
    source: string;
    sourceType: 'pdf' | 'docx' | 'url' | 'youtube' | 'transcript';
    pageCount?: number;
    wordCount: number;
    extractedAt: string;
  };
  sections: { heading: string; content: string; page?: number }[];
}

async function parsePDF(filePath: string): Promise<ParsedDocument> {
  const buffer = await readFile(filePath);
  const data = await pdfParse(buffer);

  // Split into sections by detecting heading patterns
  const lines = data.text.split('\n');
  const sections: ParsedDocument['sections'] = [];
  let currentSection = { heading: 'Introduction', content: '', page: 1 };

  for (const line of lines) {
    const trimmed = line.trim();
    // Heuristic: short lines in ALL CAPS or Title Case are likely headings
    if (
      trimmed.length > 0 &&
      trimmed.length < 100 &&
      (trimmed === trimmed.toUpperCase() || /^[A-Z][a-z]/.test(trimmed)) &&
      !trimmed.endsWith('.')
    ) {
      if (currentSection.content.trim()) {
        sections.push({ ...currentSection });
      }
      currentSection = { heading: trimmed, content: '', page: currentSection.page };
    } else {
      currentSection.content += trimmed + ' ';
    }
  }
  if (currentSection.content.trim()) {
    sections.push(currentSection);
  }

  return {
    text: data.text,
    metadata: {
      title: data.info?.Title || filePath.split('/').pop()?.replace('.pdf', '') || 'Untitled',
      author: data.info?.Author || 'Unknown',
      source: filePath,
      sourceType: 'pdf',
      pageCount: data.numpages,
      wordCount: data.text.split(/\s+/).length,
      extractedAt: new Date().toISOString(),
    },
    sections,
  };
}
```

### DOCX Parser

```typescript
import mammoth from 'mammoth';
import { readFile } from 'fs/promises';

async function parseDOCX(filePath: string): Promise<ParsedDocument> {
  const buffer = await readFile(filePath);
  const result = await mammoth.extractRawText({ buffer });
  const text = result.value;

  // Also extract with HTML to get heading structure
  const htmlResult = await mammoth.convertToHtml({ buffer });
  const sections = extractSectionsFromHtml(htmlResult.value);

  return {
    text,
    metadata: {
      title: filePath.split('/').pop()?.replace('.docx', '') || 'Untitled',
      author: 'Unknown',
      source: filePath,
      sourceType: 'docx',
      wordCount: text.split(/\s+/).length,
      extractedAt: new Date().toISOString(),
    },
    sections,
  };
}

function extractSectionsFromHtml(html: string): ParsedDocument['sections'] {
  // Use regex to split on h1-h4 tags (lightweight, no DOM needed)
  const headingPattern = /<h[1-4][^>]*>(.*?)<\/h[1-4]>/gi;
  const sections: ParsedDocument['sections'] = [];
  let lastIndex = 0;
  let lastHeading = 'Introduction';
  let match: RegExpExecArray | null;

  while ((match = headingPattern.exec(html)) !== null) {
    const content = html.slice(lastIndex, match.index).replace(/<[^>]*>/g, '').trim();
    if (content) {
      sections.push({ heading: lastHeading, content });
    }
    lastHeading = match[1].replace(/<[^>]*>/g, '').trim();
    lastIndex = match.index + match[0].length;
  }

  // Remaining content after last heading
  const remaining = html.slice(lastIndex).replace(/<[^>]*>/g, '').trim();
  if (remaining) {
    sections.push({ heading: lastHeading, content: remaining });
  }

  return sections;
}
```

### URL Parser (Web Articles)

```typescript
import { Readability } from '@mozilla/readability';
import { parseHTML } from 'linkedom';

async function parseURL(url: string): Promise<ParsedDocument> {
  const response = await fetch(url);
  const html = await response.text();

  // linkedom provides a DOM-like environment for Readability
  const { document } = parseHTML(html);
  const reader = new Readability(document as any);
  const article = reader.parse();

  if (!article) {
    throw new Error(`Could not extract readable content from ${url}`);
  }

  const text = article.textContent || '';

  return {
    text,
    metadata: {
      title: article.title || url,
      author: article.byline || 'Unknown',
      source: url,
      sourceType: 'url',
      wordCount: text.split(/\s+/).length,
      extractedAt: new Date().toISOString(),
    },
    sections: [{ heading: article.title || 'Article', content: text }],
  };
}
```

### YouTube Transcript Parser

```typescript
import { YoutubeTranscript } from 'youtube-transcript';

async function parseYouTube(videoUrl: string): Promise<ParsedDocument> {
  const videoId = extractVideoId(videoUrl);
  const transcript = await YoutubeTranscript.fetchTranscript(videoId);

  const text = transcript.map((entry) => entry.text).join(' ');

  // Group transcript into ~2-minute segments as "sections"
  const sections: ParsedDocument['sections'] = [];
  let currentSection = { heading: 'Opening', content: '' };
  let segmentDuration = 0;
  let segmentIndex = 1;

  for (const entry of transcript) {
    currentSection.content += entry.text + ' ';
    segmentDuration += entry.duration;

    if (segmentDuration >= 120) {
      // 2-minute segments
      sections.push({ ...currentSection });
      segmentIndex++;
      currentSection = {
        heading: `Segment ${segmentIndex} (${formatTime(entry.offset)})`,
        content: '',
      };
      segmentDuration = 0;
    }
  }
  if (currentSection.content.trim()) {
    sections.push(currentSection);
  }

  return {
    text,
    metadata: {
      title: `YouTube: ${videoId}`,
      author: 'Unknown',
      source: videoUrl,
      sourceType: 'youtube',
      wordCount: text.split(/\s+/).length,
      extractedAt: new Date().toISOString(),
    },
    sections,
  };
}

function extractVideoId(url: string): string {
  const match = url.match(
    /(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/
  );
  if (!match) throw new Error(`Invalid YouTube URL: ${url}`);
  return match[1];
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}
```

### Unified Document Ingestor

```typescript
type DocumentSource =
  | { type: 'pdf'; path: string }
  | { type: 'docx'; path: string }
  | { type: 'url'; url: string }
  | { type: 'youtube'; url: string }
  | { type: 'text'; content: string; title?: string };

async function ingestDocument(source: DocumentSource): Promise<ParsedDocument> {
  switch (source.type) {
    case 'pdf':
      return parsePDF(source.path);
    case 'docx':
      return parseDOCX(source.path);
    case 'url':
      return parseURL(source.url);
    case 'youtube':
      return parseYouTube(source.url);
    case 'text':
      return {
        text: source.content,
        metadata: {
          title: source.title || 'Direct Text',
          author: 'User',
          source: 'direct-input',
          sourceType: 'transcript',
          wordCount: source.content.split(/\s+/).length,
          extractedAt: new Date().toISOString(),
        },
        sections: [{ heading: source.title || 'Content', content: source.content }],
      };
  }
}
```

### Semantic Chunker

Chunking strategy: 400-600 tokens per chunk with 50-token overlap. This ensures each chunk
has enough context for meaningful embedding while maintaining continuity across chunk boundaries.

```typescript
interface TextChunk {
  id: string;
  text: string;
  index: number;
  sectionHeading: string;
  tokenCount: number;
  embedding?: number[];
}

function semanticChunk(
  doc: ParsedDocument,
  targetTokens: number = 500,
  overlapTokens: number = 50
): TextChunk[] {
  const chunks: TextChunk[] = [];
  let chunkIndex = 0;

  for (const section of doc.sections) {
    const words = section.content.split(/\s+/);
    // Rough token estimate: 1 word ~ 1.3 tokens
    const wordsPerChunk = Math.floor(targetTokens / 1.3);
    const overlapWords = Math.floor(overlapTokens / 1.3);

    let start = 0;
    while (start < words.length) {
      const end = Math.min(start + wordsPerChunk, words.length);
      const chunkText = words.slice(start, end).join(' ');

      if (chunkText.trim().length > 20) {
        // Skip tiny fragments
        chunks.push({
          id: `chunk-${chunkIndex}`,
          text: chunkText,
          index: chunkIndex,
          sectionHeading: section.heading,
          tokenCount: Math.ceil(chunkText.split(/\s+/).length * 1.3),
        });
        chunkIndex++;
      }

      start = end - overlapWords;
      if (start >= words.length - overlapWords) break;
    }
  }

  return chunks;
}
```

### Embedding Generation

Two embedding options: Gemini embedding-001 (768d, cloud) or nomic-embed-text (local via Ollama).

```typescript
// Option A: Gemini Embedding API
async function embedWithGemini(chunks: TextChunk[]): Promise<TextChunk[]> {
  const API_KEY = process.env.GEMINI_API_KEY;
  const BATCH_SIZE = 100; // Gemini supports batch embedding

  for (let i = 0; i < chunks.length; i += BATCH_SIZE) {
    const batch = chunks.slice(i, i + BATCH_SIZE);
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/embedding-001:batchEmbedContents?key=${API_KEY}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          requests: batch.map((chunk) => ({
            model: 'models/embedding-001',
            content: { parts: [{ text: chunk.text }] },
            taskType: 'RETRIEVAL_DOCUMENT',
          })),
        }),
      }
    );

    const data = await response.json();
    for (let j = 0; j < batch.length; j++) {
      batch[j].embedding = data.embeddings[j].values;
    }
  }

  return chunks;
}

// Option B: Local embedding via Ollama (nomic-embed-text, 768d)
async function embedWithOllama(chunks: TextChunk[]): Promise<TextChunk[]> {
  for (const chunk of chunks) {
    const response = await fetch('http://localhost:11434/api/embeddings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'nomic-embed-text',
        prompt: chunk.text,
      }),
    });
    const data = await response.json();
    chunk.embedding = data.embedding;
  }
  return chunks;
}
```

---

## Stage 2: Understanding

The understanding stage transforms raw chunks into a structured podcast outline.
It identifies the most discussion-worthy points, ranks them by importance, and
generates a conversational flow.

### Key Point Extraction

```typescript
import { GoogleGenerativeAI } from '@google/generative-ai';

interface KeyPoint {
  topic: string;
  summary: string;
  relevantChunks: string[]; // chunk IDs
  importance: number; // 1-10
  discussionAngle: string; // how to frame it for conversation
}

interface PodcastOutline {
  title: string;
  description: string;
  targetDuration: string;
  keyPoints: KeyPoint[];
  segments: PodcastSegment[];
}

interface PodcastSegment {
  type: 'intro' | 'discussion' | 'deep-dive' | 'recap' | 'outro';
  title: string;
  keyPointRefs: number[];
  estimatedDuration: number; // seconds
  notes: string;
}

async function extractKeyPoints(
  doc: ParsedDocument,
  chunks: TextChunk[],
  maxPoints: number = 8
): Promise<KeyPoint[]> {
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
  const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });

  const chunkSummaries = chunks
    .map((c) => `[${c.id}] (Section: ${c.sectionHeading}): ${c.text.slice(0, 200)}...`)
    .join('\n');

  const prompt = `You are an expert podcast producer analyzing a document for conversion into a podcast episode.

Document Title: ${doc.metadata.title}
Author: ${doc.metadata.author}
Word Count: ${doc.metadata.wordCount}

Document chunks:
${chunkSummaries}

Identify the top ${maxPoints} most discussion-worthy points from this document.
For each point, provide:
1. A clear topic name
2. A 1-2 sentence summary
3. The chunk IDs that are most relevant (as an array)
4. An importance score (1-10)
5. A discussion angle (how would podcast hosts naturally discuss this?)

Return ONLY valid JSON in this format:
[
  {
    "topic": "string",
    "summary": "string",
    "relevantChunks": ["chunk-0", "chunk-3"],
    "importance": 8,
    "discussionAngle": "string"
  }
]

Focus on points that:
- Would be interesting to a general audience
- Have enough depth for 2-3 minutes of discussion
- Connect to broader themes or real-world applications
- Would benefit from being explained conversationally`;

  const result = await model.generateContent(prompt);
  const text = result.response.text();

  // Extract JSON from response (handle markdown code blocks)
  const jsonMatch = text.match(/\[[\s\S]*\]/);
  if (!jsonMatch) throw new Error('Failed to extract key points JSON from AI response');

  const keyPoints: KeyPoint[] = JSON.parse(jsonMatch[0]);
  return keyPoints.sort((a, b) => b.importance - a.importance).slice(0, maxPoints);
}
```

### Outline Generation

```typescript
async function generateOutline(
  doc: ParsedDocument,
  keyPoints: KeyPoint[],
  config: { format: string; duration: string }
): Promise<PodcastOutline> {
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
  const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });

  const durationSeconds = parseDuration(config.duration);
  const pointsSummary = keyPoints
    .map((kp, i) => `${i + 1}. [Importance: ${kp.importance}] ${kp.topic}: ${kp.summary}`)
    .join('\n');

  const prompt = `You are a podcast producer creating an episode outline.

Document: "${doc.metadata.title}" by ${doc.metadata.author}
Format: ${config.format}
Target Duration: ${config.duration} (${durationSeconds} seconds)

Key discussion points (ranked by importance):
${pointsSummary}

Create a podcast outline with these segments:
1. INTRO (10-15% of duration): Hook the listener, introduce the topic
2. DISCUSSION segments (70-80%): Cover the key points in a logical flow
3. RECAP/OUTRO (10-15%): Summarize takeaways, closing thoughts

For a "${config.format}" format:
- "deep-dive": Thorough exploration, technical depth, expert tone
- "brief": Quick overview, highlight the top 3-4 points only
- "debate": Present contrasting viewpoints on each point
- "narration": Single narrator, storytelling approach

Return ONLY valid JSON:
{
  "title": "Episode title",
  "description": "1-2 sentence episode description",
  "targetDuration": "${config.duration}",
  "segments": [
    {
      "type": "intro|discussion|deep-dive|recap|outro",
      "title": "Segment title",
      "keyPointRefs": [0, 1],
      "estimatedDuration": 120,
      "notes": "Production notes for script writer"
    }
  ]
}

Ensure total estimatedDuration across all segments equals approximately ${durationSeconds} seconds.`;

  const result = await model.generateContent(prompt);
  const text = result.response.text();
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) throw new Error('Failed to extract outline JSON from AI response');

  const outline: PodcastOutline = JSON.parse(jsonMatch[0]);
  outline.keyPoints = keyPoints;
  return outline;
}

function parseDuration(duration: string): number {
  const match = duration.match(/(\d+)\s*min/);
  return match ? parseInt(match[1]) * 60 : 900; // default 15min
}
```

---

## Stage 3: Script Generation

The script generation stage uses the PodAgent pattern (ACL 2025): three specialized AI agents
collaborate to produce a natural, engaging podcast script with faithfulness verification.

### PodAgent Multi-Agent Architecture

```
+-------------------+     +-------------------+     +-------------------+
|   HOST AGENT      |     |   GUEST AGENT     |     |   WRITER AGENT    |
|                   |     |                   |     |                   |
| - Drives convo    |     | - Expert voice    |     | - Structures flow |
| - Asks questions  |     | - Provides depth  |     | - Verifies facts  |
| - Transitions     |     | - Uses analogies  |     | - Controls timing |
| - Engages listener|     | - Cites sources   |     | - Ensures quality |
+-------------------+     +-------------------+     +-------------------+
         |                         |                         |
         +-------------------------+-------------------------+
                                   |
                                   v
                    +-----------------------------+
                    |    STRUCTURED SCRIPT JSON    |
                    |  [{speaker, text, emotion,   |
                    |    duration, segmentRef}]     |
                    +-----------------------------+
```

### Script Data Types

```typescript
interface ScriptLine {
  speaker: 'host' | 'guest';
  text: string;
  emotion: 'neutral' | 'excited' | 'thoughtful' | 'humorous' | 'serious' | 'curious';
  estimatedDuration: number; // seconds (based on ~150 words/minute speaking rate)
  segmentRef: string; // which outline segment this belongs to
}

interface PodcastScript {
  title: string;
  totalDuration: number;
  speakers: {
    host: { name: string; personality: string };
    guest: { name: string; personality: string };
  };
  lines: ScriptLine[];
}
```

### Script Generator

```typescript
async function generateScript(
  outline: PodcastOutline,
  chunks: TextChunk[],
  config: PipelineConfig
): Promise<PodcastScript> {
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
  // Use the most capable model for creative script writing
  const model = genAI.getGenerativeModel({ model: 'gemini-2.5-pro-preview-05-06' });

  const speakerNames = config.speakers.length >= 2
    ? { host: config.speakers[0].name, guest: config.speakers[1].name }
    : { host: 'Alex', guest: 'Jordan' };

  // Gather source material for each segment
  const segmentContext = outline.segments.map((seg) => {
    const relevantPoints = seg.keyPointRefs.map((ref) => outline.keyPoints[ref]);
    const relevantChunkIds = relevantPoints.flatMap((kp) => kp.relevantChunks);
    const sourceText = chunks
      .filter((c) => relevantChunkIds.includes(c.id))
      .map((c) => c.text)
      .join('\n\n');

    return {
      segment: seg,
      sourceText: sourceText.slice(0, 2000), // Token budget management
      points: relevantPoints,
    };
  });

  const prompt = `You are a team of three podcast production agents creating a script.

PODCAST: "${outline.title}"
DESCRIPTION: ${outline.description}
FORMAT: ${config.format}
TARGET DURATION: ${outline.targetDuration}
HOST: ${speakerNames.host} - Curious, engaging, asks great follow-up questions
GUEST: ${speakerNames.guest} - Expert, uses analogies, explains complex ideas simply

SEGMENTS AND SOURCE MATERIAL:
${segmentContext
  .map(
    (sc, i) => `
--- SEGMENT ${i + 1}: ${sc.segment.title} (${sc.segment.type}, ~${sc.segment.estimatedDuration}s) ---
Key Points: ${sc.points.map((p) => p.topic).join(', ')}
Discussion Angles: ${sc.points.map((p) => p.discussionAngle).join('; ')}
Source Material: ${sc.sourceText}
`
  )
  .join('\n')}

SCRIPT RULES:
1. Write natural, conversational dialogue -- NOT robotic or scripted-sounding
2. Host asks questions, makes transitions, keeps energy up
3. Guest provides substance, uses analogies and examples
4. Include verbal fillers sparingly ("you know", "right", "exactly") for naturalness
5. Each speaker turn should be 20-60 words (30 words = ~12 seconds at speaking pace)
6. Total script must hit approximately ${parseDuration(outline.targetDuration)} seconds
7. Speaking rate assumption: 150 words per minute (2.5 words per second)
8. FAITHFULNESS: Every claim must be traceable to the source material. Do not fabricate facts.
9. Include emotional tone markers for TTS guidance

Return ONLY valid JSON:
{
  "title": "${outline.title}",
  "totalDuration": ${parseDuration(outline.targetDuration)},
  "speakers": {
    "host": { "name": "${speakerNames.host}", "personality": "Curious and engaging" },
    "guest": { "name": "${speakerNames.guest}", "personality": "Expert and insightful" }
  },
  "lines": [
    {
      "speaker": "host",
      "text": "Welcome to the show! Today we are diving into...",
      "emotion": "excited",
      "estimatedDuration": 8,
      "segmentRef": "intro"
    }
  ]
}`;

  const result = await model.generateContent(prompt);
  const text = result.response.text();
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) throw new Error('Failed to extract script JSON from AI response');

  const script: PodcastScript = JSON.parse(jsonMatch[0]);

  // Verify faithfulness with a second pass
  const verified = await verifyFaithfulness(script, chunks, genAI);

  return verified;
}
```

### Faithfulness Verification

The Writer Agent's verification pass ensures no hallucinated facts sneak into the script.
This is critical -- the podcast claims must be traceable to source material.

```typescript
async function verifyFaithfulness(
  script: PodcastScript,
  chunks: TextChunk[],
  genAI: GoogleGenerativeAI
): Promise<PodcastScript> {
  const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });

  const sourceText = chunks.map((c) => c.text).join('\n\n').slice(0, 8000);
  const scriptText = script.lines.map((l) => `${l.speaker}: ${l.text}`).join('\n');

  const prompt = `You are a fact-checker for a podcast script. Compare the script against the source material.

SOURCE MATERIAL:
${sourceText}

PODCAST SCRIPT:
${scriptText}

For each line in the script, check if the claims are supported by the source material.
If a line contains unsupported claims, rewrite it to be faithful to the source.
If a line is opinion/transition/question, mark it as OK.

Return ONLY valid JSON -- an array of objects:
[
  { "lineIndex": 0, "status": "ok" },
  { "lineIndex": 3, "status": "revised", "revisedText": "corrected text here" }
]

Only include lines that need revision. If all lines are faithful, return an empty array [].`;

  const result = await model.generateContent(prompt);
  const text = result.response.text();
  const jsonMatch = text.match(/\[[\s\S]*\]/);
  if (!jsonMatch) return script; // If parsing fails, return original

  const revisions = JSON.parse(jsonMatch[0]);
  for (const rev of revisions) {
    if (rev.status === 'revised' && rev.revisedText && script.lines[rev.lineIndex]) {
      script.lines[rev.lineIndex].text = rev.revisedText;
    }
  }

  return script;
}
```

### Duration Control

```typescript
function validateScriptDuration(script: PodcastScript): {
  actual: number;
  target: number;
  deviation: number;
  withinTolerance: boolean;
} {
  const actual = script.lines.reduce((sum, line) => sum + line.estimatedDuration, 0);
  const deviation = Math.abs(actual - script.totalDuration) / script.totalDuration;

  return {
    actual,
    target: script.totalDuration,
    deviation,
    withinTolerance: deviation <= 0.15, // 15% tolerance
  };
}

function adjustScriptDuration(script: PodcastScript): PodcastScript {
  const validation = validateScriptDuration(script);
  if (validation.withinTolerance) return script;

  const ratio = script.totalDuration / validation.actual;

  if (ratio < 1) {
    // Script too long -- trim from the middle (keep intro/outro intact)
    const middleLines = script.lines.filter(
      (l) => l.segmentRef !== 'intro' && l.segmentRef !== 'outro'
    );
    const excessSeconds = validation.actual - script.totalDuration;
    let trimmed = 0;

    // Remove the shortest lines from the middle until we are within target
    const sortedByDuration = [...middleLines].sort(
      (a, b) => a.estimatedDuration - b.estimatedDuration
    );
    const linesToRemove = new Set<ScriptLine>();

    for (const line of sortedByDuration) {
      if (trimmed >= excessSeconds) break;
      linesToRemove.add(line);
      trimmed += line.estimatedDuration;
    }

    script.lines = script.lines.filter((l) => !linesToRemove.has(l));
  }

  return script;
}
```

---

## Stage 4: Audio Synthesis

The synthesis stage converts the structured script into a polished podcast audio file.
Each script line is synthesized individually with the appropriate speaker voice, then
composed into a final mix with pauses, optional music, and loudness normalization.

### TTS Provider Interface

```typescript
interface TTSProvider {
  synthesize(text: string, voice: string, emotion?: string): Promise<Buffer>;
  listVoices(): Promise<{ id: string; name: string; gender: string }[]>;
}

interface SpeakerConfig {
  name: string;
  role: 'host' | 'guest' | 'narrator';
  voiceId: string;
  provider: 'elevenlabs' | 'orpheus' | 'chatterbox' | 'google-cloud';
}

interface PodcastAudio {
  filePath: string;
  duration: number;
  format: string;
  fileSize: number;
  metadata: {
    title: string;
    description: string;
    speakers: string[];
    generatedAt: string;
  };
}
```

### ElevenLabs TTS Implementation

```typescript
class ElevenLabsTTS implements TTSProvider {
  private apiKey: string;
  private baseUrl = 'https://api.elevenlabs.io/v1';

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async synthesize(text: string, voiceId: string, emotion?: string): Promise<Buffer> {
    // ElevenLabs supports emotion through stability/similarity settings
    const stability = emotion === 'excited' ? 0.3 : emotion === 'serious' ? 0.8 : 0.5;
    const similarityBoost = 0.75;

    const response = await fetch(`${this.baseUrl}/text-to-speech/${voiceId}`, {
      method: 'POST',
      headers: {
        'xi-api-key': this.apiKey,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        model_id: 'eleven_multilingual_v2',
        voice_settings: {
          stability,
          similarity_boost: similarityBoost,
          style: emotion === 'excited' ? 0.7 : 0.3,
          use_speaker_boost: true,
        },
      }),
    });

    if (!response.ok) {
      throw new Error(`ElevenLabs TTS failed: ${response.status} ${await response.text()}`);
    }

    return Buffer.from(await response.arrayBuffer());
  }

  async listVoices() {
    const response = await fetch(`${this.baseUrl}/voices`, {
      headers: { 'xi-api-key': this.apiKey },
    });
    const data = await response.json();
    return data.voices.map((v: any) => ({
      id: v.voice_id,
      name: v.name,
      gender: v.labels?.gender || 'unknown',
    }));
  }
}
```

### Google Cloud TTS Implementation

```typescript
class GoogleCloudTTS implements TTSProvider {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async synthesize(text: string, voiceId: string, emotion?: string): Promise<Buffer> {
    const response = await fetch(
      `https://texttospeech.googleapis.com/v1/text:synthesize?key=${this.apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: { text },
          voice: {
            languageCode: 'en-US',
            name: voiceId, // e.g., 'en-US-Studio-O' (male) or 'en-US-Studio-Q' (female)
          },
          audioConfig: {
            audioEncoding: 'LINEAR16',
            sampleRateHertz: 24000,
            speakingRate: emotion === 'excited' ? 1.1 : emotion === 'thoughtful' ? 0.9 : 1.0,
            pitch: emotion === 'curious' ? 1.5 : 0,
          },
        }),
      }
    );

    const data = await response.json();
    return Buffer.from(data.audioContent, 'base64');
  }

  async listVoices() {
    const response = await fetch(
      `https://texttospeech.googleapis.com/v1/voices?key=${this.apiKey}`
    );
    const data = await response.json();
    return data.voices
      .filter((v: any) => v.name.includes('Studio') || v.name.includes('Neural2'))
      .map((v: any) => ({
        id: v.name,
        name: v.name,
        gender: v.ssmlGender?.toLowerCase() || 'unknown',
      }));
  }
}
```

### Per-Segment Audio Generation

```typescript
import { writeFile, mkdir } from 'fs/promises';
import { join } from 'path';

async function generateAudioSegments(
  script: PodcastScript,
  speakers: SpeakerConfig[],
  outputDir: string
): Promise<string[]> {
  await mkdir(outputDir, { recursive: true });

  // Create TTS providers for each speaker
  const ttsProviders: Record<string, { provider: TTSProvider; voiceId: string }> = {};

  for (const speaker of speakers) {
    switch (speaker.provider) {
      case 'elevenlabs':
        ttsProviders[speaker.role] = {
          provider: new ElevenLabsTTS(process.env.ELEVENLABS_API_KEY!),
          voiceId: speaker.voiceId,
        };
        break;
      case 'google-cloud':
        ttsProviders[speaker.role] = {
          provider: new GoogleCloudTTS(process.env.GOOGLE_TTS_API_KEY!),
          voiceId: speaker.voiceId,
        };
        break;
      // Add other providers as needed
    }
  }

  const segmentPaths: string[] = [];
  const totalLines = script.lines.length;

  for (let i = 0; i < totalLines; i++) {
    const line = script.lines[i];
    const tts = ttsProviders[line.speaker];

    if (!tts) {
      console.warn(`No TTS provider configured for speaker: ${line.speaker}, skipping`);
      continue;
    }

    console.log(`Synthesizing line ${i + 1}/${totalLines}: ${line.speaker} (${line.emotion})`);

    const audioBuffer = await tts.provider.synthesize(line.text, tts.voiceId, line.emotion);
    const segmentPath = join(outputDir, `segment-${String(i).padStart(4, '0')}.wav`);
    await writeFile(segmentPath, audioBuffer);
    segmentPaths.push(segmentPath);

    // Rate limiting: avoid API throttling
    await new Promise((resolve) => setTimeout(resolve, 200));
  }

  return segmentPaths;
}
```

### FFmpeg Audio Composition

The final composition pipeline concatenates all speech segments with natural pauses,
optionally adds intro/outro music, and normalizes to podcast-standard loudness.

```typescript
import { execFile } from 'child_process';
import { promisify } from 'util';
import { writeFile as writeFileAsync } from 'fs/promises';
import { join } from 'path';

const execFileAsync = promisify(execFile);

/**
 * Run an FFmpeg command safely using execFile (no shell injection risk).
 * For complex filter graphs, use the -filter_complex flag as a single argument.
 */
async function runFFmpeg(args: string[]): Promise<{ stdout: string; stderr: string }> {
  return execFileAsync('ffmpeg', args);
}

async function composeAudio(
  segmentPaths: string[],
  config: PipelineConfig,
  outputDir: string,
  title: string
): Promise<string> {
  // Step 1: Generate silence segments for natural pauses
  const pauseDuration = '0.35'; // 350ms between speaker turns
  const longPauseDuration = '0.8'; // 800ms between segments/topics
  const silencePath = join(outputDir, 'silence-short.wav');
  const longSilencePath = join(outputDir, 'silence-long.wav');

  await runFFmpeg([
    '-y', '-f', 'lavfi', '-i', `anullsrc=r=24000:cl=mono`,
    '-t', pauseDuration, silencePath,
  ]);
  await runFFmpeg([
    '-y', '-f', 'lavfi', '-i', `anullsrc=r=24000:cl=mono`,
    '-t', longPauseDuration, longSilencePath,
  ]);

  // Step 2: Build concat file list
  const concatListPath = join(outputDir, 'concat-list.txt');
  const concatEntries: string[] = [];

  for (let i = 0; i < segmentPaths.length; i++) {
    concatEntries.push(`file '${segmentPaths[i].replace(/\\/g, '/')}'`);

    if (i < segmentPaths.length - 1) {
      concatEntries.push(`file '${silencePath.replace(/\\/g, '/')}'`);
    }
  }

  await writeFileAsync(concatListPath, concatEntries.join('\n'));

  // Step 3: Concatenate all segments
  const rawConcatPath = join(outputDir, 'raw-concat.wav');
  await runFFmpeg([
    '-y', '-f', 'concat', '-safe', '0',
    '-i', concatListPath, '-c', 'copy', rawConcatPath,
  ]);

  // Step 4: Optionally add intro/outro music
  let preMasterPath = rawConcatPath;

  if (config.includeMusic) {
    preMasterPath = join(outputDir, 'with-music.wav');
    const introMusicPath = join(outputDir, '..', 'assets', 'intro-music.wav');
    const outroMusicPath = join(outputDir, '..', 'assets', 'outro-music.wav');

    // Overlay intro music (ducked under speech) and append outro
    await runFFmpeg([
      '-y',
      '-i', rawConcatPath,
      '-i', introMusicPath,
      '-i', outroMusicPath,
      '-filter_complex',
      '[1:a]atrim=0:8,afade=t=in:d=1:st=0,afade=t=out:d=2:st=6,volume=0.15[intro_music];' +
      '[2:a]afade=t=in:d=1:st=0,afade=t=out:d=2:st=6,volume=0.15[outro_music];' +
      '[intro_music][0:a][outro_music]concat=n=3:v=0:a=1[mixed]',
      '-map', '[mixed]', preMasterPath,
    ]);
  }

  // Step 5: Loudness normalization (EBU R128, -16 LUFS for podcasts)
  const normalizedPath = join(outputDir, 'normalized.wav');
  await runFFmpeg([
    '-y', '-i', preMasterPath,
    '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json',
    normalizedPath,
  ]);

  // Step 6: Export as final format with metadata
  const outputExt = config.outputFormat || 'mp3';
  const finalPath = join(outputDir, `podcast-final.${outputExt}`);

  if (outputExt === 'mp3') {
    await runFFmpeg([
      '-y', '-i', normalizedPath,
      '-codec:a', 'libmp3lame', '-b:a', '192k',
      '-metadata', `title=${title}`,
      '-metadata', 'artist=Generated Podcast',
      '-metadata', 'album=Document-to-Podcast',
      '-metadata', 'genre=Podcast',
      '-metadata', `date=${new Date().getFullYear()}`,
      finalPath,
    ]);
  } else if (outputExt === 'ogg') {
    await runFFmpeg([
      '-y', '-i', normalizedPath,
      '-codec:a', 'libvorbis', '-q:a', '6',
      '-metadata', `title=${title}`,
      finalPath,
    ]);
  } else {
    // WAV -- just copy
    await runFFmpeg(['-y', '-i', normalizedPath, finalPath]);
  }

  return finalPath;
}
```

### FFmpeg Command Reference (Standalone)

For manual use or debugging, here are the key FFmpeg commands in the pipeline:

```bash
# Generate silence (350ms pause between turns)
ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t 0.35 silence.wav

# Concatenate segments from a file list
ffmpeg -y -f concat -safe 0 -i concat-list.txt -c copy raw-concat.wav

# Normalize to podcast standard (-16 LUFS, EBU R128)
ffmpeg -y -i raw-concat.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11" normalized.wav

# Two-pass loudness normalization (higher precision)
# Pass 1: Measure
ffmpeg -i raw-concat.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" -f null /dev/null
# Pass 2: Apply measured values (replace measured_* with Pass 1 output)
ffmpeg -i raw-concat.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=-23.5:measured_TP=-4.2:measured_LRA=7.1:measured_thresh=-34.0:offset=-0.3:linear=true" normalized.wav

# Export as MP3 with metadata tags
ffmpeg -y -i normalized.wav -codec:a libmp3lame -b:a 192k \
  -metadata title="Episode Title" \
  -metadata artist="Podcast Name" \
  -metadata album="Season 1" \
  -metadata genre="Podcast" \
  podcast-final.mp3

# Add intro music (ducked under speech)
ffmpeg -y -i speech.wav -i intro.wav \
  -filter_complex "[1:a]volume=0.15,afade=t=out:d=2:st=6[music];[music][0:a]concat=n=2:v=0:a=1[out]" \
  -map "[out]" with-intro.wav

# Quick quality check: get loudness stats
ffmpeg -i podcast-final.mp3 -af "loudnorm=print_format=json" -f null /dev/null 2>&1 | tail -20
```

---

## Two Reference Implementations

### A) Full-Scale (GPU Server / Cloud API)

Based on Meta NotebookLlama's tiered model approach. Best quality, requires GPU or API budget.

```
Architecture:
  Stage 1 (Ingest):    pdf-parse / mammoth / readability (same for both)
  Stage 2 (Understand): Gemini 2.5 Pro for key point extraction + outline
                        Gemini embedding-001 for chunk embeddings
                        pgvector for vector storage
  Stage 3 (Script):    Claude Opus / Gemini 2.5 Pro for script generation
                        Gemini Flash for faithfulness verification
                        (Large model = better creative writing)
  Stage 4 (Synthesize): ElevenLabs Multilingual V2 for TTS
                        (Or Orpheus TTS 3B on local GPU -- open source, near-commercial quality)
                        FFmpeg for composition + mastering

Cost estimate (15-min episode from 10-page PDF):
  - Gemini 2.5 Pro: ~$0.15 (input) + $0.30 (output) = ~$0.45
  - Gemini Flash (verification): ~$0.01
  - Gemini Embedding: ~$0.001
  - ElevenLabs TTS: ~$0.50 (15 min at scale tier)
  - Total: ~$1.00 per episode

Hardware: Any machine. All processing is API-based.
Latency: 3-8 minutes for a 15-minute episode.
```

**Meta NotebookLlama Model Tiers (for self-hosted GPU):**

| Stage | Model | Purpose | Why This Size |
|-------|-------|---------|---------------|
| Text cleanup | Llama-3.2-1B | Strip headers, fix OCR errors | Small = fast, simple task |
| Script writing | Llama-3.1-70B (or API) | Creative multi-speaker dialogue | Large = better creativity |
| TTS prep | Llama-3.1-8B | Add SSML/emotion markers | Medium = good enough |
| Audio | Orpheus TTS 3B | Speech synthesis | Specialized model |

Key insight from Meta's research: **do not use the same model for every stage.** Match model
capability to task complexity. Small models are better (faster, cheaper) for mechanical tasks;
large models are needed only for creative generation.

### B) Local / CPU-Only

Based on Mozilla AI's Document-to-Podcast Blueprint. Fully private, zero API cost, runs on
consumer hardware. Lower quality but completely offline.

```
Architecture:
  Stage 1 (Ingest):    Same parsers (pdf-parse, mammoth, readability)
  Stage 2 (Understand): Llama 3.2 3B GGUF via llama_cpp (Q4_K_M quantization)
                        nomic-embed-text via Ollama for embeddings
                        Qdrant (local Docker) for vector storage
  Stage 3 (Script):    Llama 3.1 8B GGUF via llama_cpp (Q5_K_M quantization)
                        Self-verification (same model, second pass)
  Stage 4 (Synthesize): Orpheus TTS 150M (CPU-optimized) or Parler TTS Mini
                        FFmpeg for composition + mastering

Cost: $0.00 (no API calls)

Hardware requirements:
  - RAM: 16GB minimum (8B model needs ~6GB in Q4)
  - Storage: ~15GB for all models
  - CPU: Modern 8-core (Intel 12th+ / AMD 5000+)
  - GPU: None required (but CUDA/Metal accelerates if available)

Latency: 15-45 minutes for a 15-minute episode (CPU-bound on TTS).

Model downloads (one-time):
  # Via Ollama (easiest)
  ollama pull llama3.2:3b       # Understanding stage
  ollama pull llama3.1:8b       # Script generation
  ollama pull nomic-embed-text  # Embeddings

  # Via llama_cpp (more control)
  # Download GGUF from huggingface.co/TheBloke or official repos
```

**Quality Comparison:**

| Aspect | Full-Scale (API) | Local (CPU) |
|--------|-----------------|-------------|
| Script naturalness | 9/10 | 6/10 |
| Voice quality | 9/10 (ElevenLabs) | 5/10 (Orpheus 150M) |
| Faithfulness | 9/10 (separate verifier) | 7/10 (self-verify) |
| Latency (15min ep) | 3-8 min | 15-45 min |
| Cost per episode | ~$1.00 | $0.00 |
| Privacy | Data sent to APIs | Fully local |
| Offline capable | No | Yes |

---

## Complete TypeScript Pipeline Class

```typescript
import { mkdir, writeFile, stat, readFile, rm } from 'fs/promises';
import { join } from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';
import { GoogleGenerativeAI } from '@google/generative-ai';

const execFileAsync = promisify(execFile);

// --- Configuration ---------------------------------------------------------

interface PipelineConfig {
  ttsProvider: 'elevenlabs' | 'orpheus' | 'chatterbox' | 'google-cloud';
  aiProvider: 'gemini' | 'claude';
  format: 'deep-dive' | 'brief' | 'debate' | 'narration';
  duration: '5min' | '15min' | '30min' | '60min';
  speakers: SpeakerConfig[];
  outputFormat: 'mp3' | 'wav' | 'ogg';
  includeMusic: boolean;
  language: string;
  outputDir: string;
  /** If true, keep intermediate files (segments, concat list) for debugging */
  keepIntermediates: boolean;
}

const DEFAULT_CONFIG: PipelineConfig = {
  ttsProvider: 'elevenlabs',
  aiProvider: 'gemini',
  format: 'deep-dive',
  duration: '15min',
  speakers: [
    { name: 'Alex', role: 'host', voiceId: 'pNInz6obpgDQGcFmaJgB', provider: 'elevenlabs' },
    { name: 'Jordan', role: 'guest', voiceId: '21m00Tcm4TlvDq8ikWAM', provider: 'elevenlabs' },
  ],
  outputFormat: 'mp3',
  includeMusic: false,
  language: 'en',
  outputDir: './podcast-output',
  keepIntermediates: false,
};

// --- Pipeline Class --------------------------------------------------------

class DocToPodcastPipeline {
  private config: PipelineConfig;
  private genAI: GoogleGenerativeAI;
  private chunks: TextChunk[] = [];

  constructor(config: Partial<PipelineConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
  }

  /**
   * Run the complete pipeline: Document -> Podcast Audio
   */
  async run(source: DocumentSource): Promise<PodcastAudio> {
    const startTime = Date.now();
    const outputDir = this.config.outputDir;
    const segmentsDir = join(outputDir, 'segments');

    await mkdir(outputDir, { recursive: true });
    await mkdir(segmentsDir, { recursive: true });

    console.log('[Pipeline] Stage 1: Ingesting document...');
    const doc = await this.ingest(source);
    console.log(
      `[Pipeline] Ingested: "${doc.metadata.title}" (${doc.metadata.wordCount} words)`
    );

    console.log('[Pipeline] Stage 2: Analyzing content...');
    const outline = await this.understand(doc);
    console.log(
      `[Pipeline] Outline: ${outline.segments.length} segments, ` +
      `${outline.keyPoints.length} key points`
    );

    console.log('[Pipeline] Stage 3: Generating script...');
    const script = await this.generateScript(outline, doc);
    console.log(
      `[Pipeline] Script: ${script.lines.length} lines, ~${script.totalDuration}s`
    );

    // Save script for reference
    await writeFile(join(outputDir, 'script.json'), JSON.stringify(script, null, 2));

    console.log('[Pipeline] Stage 4: Synthesizing audio...');
    const audio = await this.synthesize(script);

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    console.log(`[Pipeline] Complete in ${elapsed}s -> ${audio.filePath}`);

    // Cleanup intermediates unless debugging
    if (!this.config.keepIntermediates) {
      await rm(segmentsDir, { recursive: true, force: true }).catch(() => {});
    }

    return audio;
  }

  /**
   * Stage 1: Parse document source into clean text with metadata
   */
  async ingest(source: DocumentSource): Promise<ParsedDocument> {
    return ingestDocument(source);
  }

  /**
   * Stage 2: Analyze document, extract key points, generate podcast outline
   */
  async understand(doc: ParsedDocument): Promise<PodcastOutline> {
    // Chunk the document
    const chunks = semanticChunk(doc);

    // Embed chunks (for potential RAG retrieval in future iterations)
    this.chunks = await embedWithGemini(chunks);

    // Extract key points
    const maxPoints = this.config.format === 'brief' ? 4 : 8;
    const keyPoints = await extractKeyPoints(doc, this.chunks, maxPoints);

    // Generate outline
    const outline = await generateOutline(doc, keyPoints, {
      format: this.config.format,
      duration: this.config.duration,
    });

    return outline;
  }

  /**
   * Stage 3: Generate multi-speaker podcast script from outline
   */
  async generateScript(
    outline: PodcastOutline,
    doc?: ParsedDocument
  ): Promise<PodcastScript> {
    const chunks = this.chunks.length > 0 ? this.chunks : semanticChunk(doc!);
    const script = await generateScript(outline, chunks, this.config);
    return adjustScriptDuration(script);
  }

  /**
   * Stage 4: Synthesize audio from script, compose final podcast
   */
  async synthesize(script: PodcastScript): Promise<PodcastAudio> {
    const segmentsDir = join(this.config.outputDir, 'segments');

    // Generate individual audio segments via TTS
    const segmentPaths = await generateAudioSegments(
      script,
      this.config.speakers,
      segmentsDir
    );

    // Compose final audio with FFmpeg
    const finalPath = await composeAudio(
      segmentPaths,
      this.config,
      this.config.outputDir,
      script.title
    );

    // Get file stats
    const fileStat = await stat(finalPath);

    // Calculate actual duration from FFmpeg probe
    let duration = script.totalDuration;
    try {
      const { stdout } = await execFileAsync('ffprobe', [
        '-v', 'quiet',
        '-show_entries', 'format=duration',
        '-of', 'csv=p=0',
        finalPath,
      ]);
      duration = parseFloat(stdout.trim()) || duration;
    } catch {
      // Fall back to estimated duration
    }

    return {
      filePath: finalPath,
      duration,
      format: this.config.outputFormat,
      fileSize: fileStat.size,
      metadata: {
        title: script.title,
        description:
          `Generated podcast from document. ${script.lines.length} script lines.`,
        speakers: [script.speakers.host.name, script.speakers.guest.name],
        generatedAt: new Date().toISOString(),
      },
    };
  }
}
```

### Usage Examples

```typescript
// Example 1: PDF to podcast (cloud API, full quality)
const pipeline = new DocToPodcastPipeline({
  ttsProvider: 'elevenlabs',
  aiProvider: 'gemini',
  format: 'deep-dive',
  duration: '15min',
  outputDir: './output/my-podcast',
  speakers: [
    { name: 'Alex', role: 'host', voiceId: 'pNInz6obpgDQGcFmaJgB', provider: 'elevenlabs' },
    { name: 'Jordan', role: 'guest', voiceId: '21m00Tcm4TlvDq8ikWAM', provider: 'elevenlabs' },
  ],
});

const result = await pipeline.run({
  type: 'pdf',
  path: './documents/research-paper.pdf',
});
console.log(`Podcast: ${result.filePath} (${result.duration}s, ${result.fileSize} bytes)`);

// Example 2: URL to brief podcast
const brief = await new DocToPodcastPipeline({
  format: 'brief',
  duration: '5min',
  outputDir: './output/quick-brief',
}).run({ type: 'url', url: 'https://example.com/article' });

// Example 3: YouTube video to podcast episode
const ytPodcast = await new DocToPodcastPipeline({
  format: 'deep-dive',
  duration: '30min',
  outputDir: './output/yt-episode',
}).run({ type: 'youtube', url: 'https://youtube.com/watch?v=example123' });

// Example 4: Direct text input (e.g., from a database or CMS)
const textPodcast = await new DocToPodcastPipeline({
  format: 'narration',
  duration: '5min',
  speakers: [
    { name: 'Narrator', role: 'narrator', voiceId: 'en-US-Studio-O', provider: 'google-cloud' },
    { name: 'Expert', role: 'guest', voiceId: 'en-US-Studio-Q', provider: 'google-cloud' },
  ],
  outputDir: './output/text-podcast',
}).run({
  type: 'text',
  content: 'Your document text here...',
  title: 'Weekly Update',
});
```

---

## Ministry / Church Use Cases

Since this pipeline is designed with Thierry's ministry application stack in mind, here are
specific configurations for common church content scenarios.

### Sermon to Podcast Episode

Transform a recorded sermon transcript or notes into a polished podcast discussion.

```typescript
const sermonPipeline = new DocToPodcastPipeline({
  format: 'deep-dive',
  duration: '30min',
  aiProvider: 'gemini',
  ttsProvider: 'elevenlabs',
  outputDir: './output/sermon-podcast',
  speakers: [
    { name: 'Pastor Mike', role: 'host', voiceId: 'voice-id-1', provider: 'elevenlabs' },
    { name: 'Dr. Sarah', role: 'guest', voiceId: 'voice-id-2', provider: 'elevenlabs' },
  ],
  includeMusic: true,
});

// From sermon notes (DOCX from pastor's study)
const episode = await sermonPipeline.run({
  type: 'docx',
  path: './sermons/2026-03-10-grace-in-action.docx',
});

// From sermon recording transcript (already transcribed via transcription-pipeline-selector)
const fromRecording = await sermonPipeline.run({
  type: 'text',
  content: transcriptText,
  title: 'Grace in Action - Sunday Sermon Discussion',
});
```

### Bible Study to Discussion Format

Convert Bible study materials into an engaging discussion podcast where the host and guest
explore the passage together.

```typescript
const bibleStudyPipeline = new DocToPodcastPipeline({
  format: 'deep-dive',
  duration: '15min',
  speakers: [
    { name: 'Teacher', role: 'host', voiceId: 'voice-id-1', provider: 'elevenlabs' },
    { name: 'Student', role: 'guest', voiceId: 'voice-id-2', provider: 'elevenlabs' },
  ],
  outputDir: './output/bible-study',
});

// Custom AI prompt override for Bible study context:
// The key point extractor can be tuned to focus on theological themes:
//   - Historical context of the passage
//   - Key Greek/Hebrew word meanings
//   - Practical application points
//   - Cross-references to other scripture
```

### Church Announcement to Brief Audio Update

Quick 2-3 minute audio updates for the congregation.

```typescript
const announcementPipeline = new DocToPodcastPipeline({
  format: 'brief',
  duration: '5min',
  speakers: [
    { name: 'Church Office', role: 'narrator', voiceId: 'en-US-Studio-O', provider: 'google-cloud' },
    { name: 'Pastor', role: 'host', voiceId: 'voice-id-1', provider: 'elevenlabs' },
  ],
  outputDir: './output/announcements',
  includeMusic: true,
});

const announcement = await announcementPipeline.run({
  type: 'text',
  content: `
    This week at Grace Community Church:
    - Sunday Service at 10am: "Walking in Faith" series continues
    - Wednesday Bible Study: Romans Chapter 8, 7pm in Fellowship Hall
    - Youth Group Friday Night: Movie and pizza, 6-9pm
    - Volunteer sign-ups for Easter service are open at the welcome desk
    - Prayer requests can be submitted online at our website
  `,
  title: 'This Week at Grace Community - March 10, 2026',
});
```

### Teaching Recording to Educational Deep-Dive

Transform a lecture or teaching session into a structured educational podcast that
breaks down complex theological or educational topics.

```typescript
const teachingPipeline = new DocToPodcastPipeline({
  format: 'deep-dive',
  duration: '60min',
  speakers: [
    { name: 'Professor', role: 'host', voiceId: 'voice-id-1', provider: 'elevenlabs' },
    { name: 'Teaching Assistant', role: 'guest', voiceId: 'voice-id-2', provider: 'elevenlabs' },
  ],
  outputDir: './output/teaching-series',
});

// From a seminary lecture PDF
const lecture = await teachingPipeline.run({
  type: 'pdf',
  path: './materials/systematic-theology-ch3.pdf',
});

// Integration with content-repurposing-pipeline:
// After generating the podcast, feed the script into the repurposing pipeline
// to create social media clips, quote cards, and blog posts from the same source.
```

### Ministry Integration Architecture

```
[Sermon Recording]  [Bible Study Notes]  [Announcements]  [Teaching Materials]
        |                    |                  |                   |
        v                    v                  v                   v
  [Transcription]      [DOCX Parser]      [Text Input]        [PDF Parser]
        |                    |                  |                   |
        +--------------------+------------------+-------------------+
                                    |
                                    v
                    +-------------------------------+
                    |   DocToPodcastPipeline.run()   |
                    |   (format per content type)    |
                    +-------------------------------+
                                    |
                                    v
                    +-------------------------------+
                    |   Output: MP3 + Script JSON    |
                    +-------------------------------+
                          |              |
                          v              v
                   [Podcast RSS]   [Content Repurposing]
                   [Apple/Spotify]  [Social clips, quotes]
```

---

## Error Handling and Resilience

### Retry Logic for TTS APIs

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delayMs: number = 1000
): Promise<T> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error: any) {
      const isRateLimit = error?.status === 429;
      const isServerError = error?.status >= 500;

      if (attempt === maxRetries || (!isRateLimit && !isServerError)) {
        throw error;
      }

      const backoff = isRateLimit ? delayMs * attempt * 2 : delayMs * attempt;
      console.warn(
        `[Retry ${attempt}/${maxRetries}] ${error.message}. Waiting ${backoff}ms...`
      );
      await new Promise((resolve) => setTimeout(resolve, backoff));
    }
  }
  throw new Error('Unreachable');
}

// Usage in TTS generation:
const audioBuffer = await withRetry(
  () => tts.provider.synthesize(line.text, tts.voiceId, line.emotion),
  3,
  2000
);
```

### Pipeline Checkpointing

For long-running pipelines (60-min episodes), save intermediate state so a failure
in Stage 4 does not require re-running Stages 1-3.

```typescript
interface PipelineCheckpoint {
  stage: 1 | 2 | 3 | 4;
  doc?: ParsedDocument;
  outline?: PodcastOutline;
  script?: PodcastScript;
  segmentPaths?: string[];
  timestamp: string;
}

async function saveCheckpoint(
  checkpoint: PipelineCheckpoint,
  outputDir: string
): Promise<void> {
  await writeFile(
    join(outputDir, 'checkpoint.json'),
    JSON.stringify(checkpoint, null, 2)
  );
}

async function loadCheckpoint(outputDir: string): Promise<PipelineCheckpoint | null> {
  try {
    const data = await readFile(join(outputDir, 'checkpoint.json'), 'utf-8');
    return JSON.parse(data);
  } catch {
    return null;
  }
}

// Enhanced run() with checkpointing:
async function runWithCheckpoints(
  pipeline: DocToPodcastPipeline,
  source: DocumentSource,
  outputDir: string
): Promise<PodcastAudio> {
  const existing = await loadCheckpoint(outputDir);

  let doc: ParsedDocument;
  let outline: PodcastOutline;
  let script: PodcastScript;

  if (existing && existing.stage >= 2 && existing.doc) {
    console.log('[Resume] Skipping Stage 1 (cached)');
    doc = existing.doc;
  } else {
    doc = await pipeline.ingest(source);
    await saveCheckpoint(
      { stage: 1, doc, timestamp: new Date().toISOString() },
      outputDir
    );
  }

  if (existing && existing.stage >= 3 && existing.outline) {
    console.log('[Resume] Skipping Stage 2 (cached)');
    outline = existing.outline;
  } else {
    outline = await pipeline.understand(doc);
    await saveCheckpoint(
      { stage: 2, doc, outline, timestamp: new Date().toISOString() },
      outputDir
    );
  }

  if (existing && existing.stage >= 4 && existing.script) {
    console.log('[Resume] Skipping Stage 3 (cached)');
    script = existing.script;
  } else {
    script = await pipeline.generateScript(outline, doc);
    await saveCheckpoint(
      { stage: 3, doc, outline, script, timestamp: new Date().toISOString() },
      outputDir
    );
  }

  const audio = await pipeline.synthesize(script);
  return audio;
}
```

---

## Performance Optimization

### Parallel TTS Generation

For cloud TTS providers with sufficient rate limits, generate multiple segments in parallel.

```typescript
async function generateAudioSegmentsParallel(
  script: PodcastScript,
  speakers: SpeakerConfig[],
  outputDir: string,
  concurrency: number = 5
): Promise<string[]> {
  await mkdir(outputDir, { recursive: true });

  const ttsProviders = buildTTSProviders(speakers);
  const segmentPaths: string[] = new Array(script.lines.length);

  // Process in batches of `concurrency`
  for (let i = 0; i < script.lines.length; i += concurrency) {
    const batch = script.lines.slice(i, i + concurrency);
    const promises = batch.map(async (line, batchIdx) => {
      const globalIdx = i + batchIdx;
      const tts = ttsProviders[line.speaker];
      if (!tts) return;

      const audioBuffer = await withRetry(
        () => tts.provider.synthesize(line.text, tts.voiceId, line.emotion),
        3,
        2000
      );
      const segmentPath = join(
        outputDir,
        `segment-${String(globalIdx).padStart(4, '0')}.wav`
      );
      await writeFile(segmentPath, audioBuffer);
      segmentPaths[globalIdx] = segmentPath;
    });

    await Promise.all(promises);
    console.log(
      `[TTS] Completed ${Math.min(i + concurrency, script.lines.length)}` +
      `/${script.lines.length}`
    );
  }

  return segmentPaths.filter(Boolean);
}

function buildTTSProviders(
  speakers: SpeakerConfig[]
): Record<string, { provider: TTSProvider; voiceId: string }> {
  const providers: Record<string, { provider: TTSProvider; voiceId: string }> = {};
  for (const speaker of speakers) {
    switch (speaker.provider) {
      case 'elevenlabs':
        providers[speaker.role] = {
          provider: new ElevenLabsTTS(process.env.ELEVENLABS_API_KEY!),
          voiceId: speaker.voiceId,
        };
        break;
      case 'google-cloud':
        providers[speaker.role] = {
          provider: new GoogleCloudTTS(process.env.GOOGLE_TTS_API_KEY!),
          voiceId: speaker.voiceId,
        };
        break;
    }
  }
  return providers;
}
```

### Streaming Pipeline (Future Enhancement)

For real-time applications, each stage can emit results as they become available
rather than waiting for the entire stage to complete:

```
Stage 1 emits chunks as they are parsed
  --> Stage 2 begins embedding as chunks arrive
    --> Stage 3 begins writing intro while later points are still extracted
      --> Stage 4 begins TTS on early script lines while later ones generate
```

This reduces end-to-end latency by ~40% for long documents but adds significant
implementation complexity. Recommended only for production deployment.

---

## Testing and Validation

### Unit Test Checklist

```typescript
// Tests for each stage (using vitest):
describe('DocToPodcastPipeline', () => {
  // Stage 1
  test('parsePDF extracts text and sections from a known PDF', async () => {
    const doc = await parsePDF('./fixtures/sample.pdf');
    expect(doc.text.length).toBeGreaterThan(100);
    expect(doc.sections.length).toBeGreaterThan(0);
    expect(doc.metadata.sourceType).toBe('pdf');
  });

  test('parseDOCX extracts heading structure', async () => {
    const doc = await parseDOCX('./fixtures/sample.docx');
    expect(doc.sections.some((s) => s.heading !== 'Introduction')).toBe(true);
  });

  test('semanticChunk produces overlapping chunks within token budget', () => {
    const doc = createMockDocument(5000); // 5000 words
    const chunks = semanticChunk(doc);
    expect(chunks.every((c) => c.tokenCount <= 650)).toBe(true); // 500 + buffer
    expect(chunks.every((c) => c.tokenCount >= 50)).toBe(true);  // Not too small
  });

  // Stage 2
  test('extractKeyPoints returns ranked points with chunk references', async () => {
    const points = await extractKeyPoints(mockDoc, mockChunks, 5);
    expect(points.length).toBeLessThanOrEqual(5);
    expect(points[0].importance).toBeGreaterThanOrEqual(points[1].importance);
    expect(points.every((p) => p.relevantChunks.length > 0)).toBe(true);
  });

  // Stage 3
  test('generated script has correct speaker alternation', async () => {
    const script = await generateScript(mockOutline, mockChunks, mockConfig);
    // Host should speak first
    expect(script.lines[0].speaker).toBe('host');
    // Speakers should mostly alternate
    let alternations = 0;
    for (let i = 1; i < script.lines.length; i++) {
      if (script.lines[i].speaker !== script.lines[i - 1].speaker) alternations++;
    }
    expect(alternations / script.lines.length).toBeGreaterThan(0.4);
  });

  test('script duration is within 15% of target', () => {
    const validation = validateScriptDuration(mockScript);
    expect(validation.withinTolerance).toBe(true);
  });

  // Stage 4
  test('FFmpeg concat produces valid audio file', async () => {
    const finalPath = await composeAudio(mockSegments, mockConfig, tmpDir, 'Test');
    const { stdout } = await execFileAsync('ffprobe', [
      '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', finalPath,
    ]);
    expect(parseFloat(stdout)).toBeGreaterThan(0);
  });

  test('output loudness is within EBU R128 spec', async () => {
    const { stderr } = await execFileAsync('ffmpeg', [
      '-i', outputPath,
      '-af', 'loudnorm=print_format=json',
      '-f', 'null', '/dev/null',
    ]);
    const match = stderr.match(/"input_i"\s*:\s*"(-?\d+\.?\d*)"/);
    const loudness = parseFloat(match![1]);
    expect(loudness).toBeCloseTo(-16, 1); // Within 1 LUFS of target
  });
});
```

### Manual Validation Checklist

```
[ ] Document parses correctly (check text extraction, no garbled characters)
[ ] Key points are relevant (not trivial or off-topic)
[ ] Outline has logical flow (intro -> body -> conclusion)
[ ] Script reads naturally when read aloud
[ ] No hallucinated facts in script (compare to source)
[ ] Speaker voices are distinct and appropriate
[ ] Pauses feel natural (not too short, not too long)
[ ] Loudness is consistent throughout (-16 LUFS +/- 1)
[ ] No audio artifacts (clicks, pops, unnatural transitions)
[ ] Total duration matches target within 15%
[ ] MP3 metadata tags are correct (title, artist, genre)
```

---

## Research Citations

> **Meta NotebookLlama (Oct 2024):** Open-source reproduction of Google NotebookLM's "Audio
> Overview" feature. Demonstrates tiered model architecture: Llama-3.2-1B for text cleaning,
> Llama-3.1-70B for script generation, Llama-3.1-8B for TTS transcript preparation. Key insight:
> match model capability to task complexity rather than using one model for everything. Small
> models handle mechanical tasks faster and cheaper; large models are reserved for creative
> generation where quality matters most.
> Source: github.com/meta-llama/llama-recipes/tree/main/recipes/quickstart/NotebookLlama

> **Mozilla AI Document-to-Podcast Blueprint (2024):** Fully local, CPU-only pipeline using
> GGUF quantized models via llama_cpp Python bindings. Demonstrates that consumer hardware
> (16GB RAM, no GPU) can run the complete pipeline with acceptable quality. Uses Parler TTS
> for speech synthesis. Zero API cost makes it suitable for privacy-sensitive or budget-
> constrained deployments.
> Source: github.com/mozilla-ai/document-to-podcast

> **PodAgent (ACL 2025, arXiv 2503.00455):** Multi-agent framework for podcast generation with
> Host, Guest, and Writer agents. The Writer agent performs faithfulness verification by checking
> each generated claim against source material, reducing hallucination rate by 23% compared to
> single-agent approaches. Introduces the "discussion angle" concept where each key point is
> framed as a conversation starter rather than a lecture point.
> Source: arxiv.org/abs/2503.00455

> **EBU R128 Loudness Standard:** European Broadcasting Union recommendation for loudness
> normalization. Podcasts target -16 LUFS (Integrated Loudness) with a True Peak ceiling of
> -1.5 dBTP. This is the de facto standard for Apple Podcasts, Spotify, and YouTube. FFmpeg's
> loudnorm filter implements this standard natively.
> Source: tech.ebu.ch/docs/r/r128.pdf

> **Google Gemini Embedding API:** embedding-001 model produces 768-dimensional dense vectors
> optimized for retrieval tasks. Supports batch embedding (up to 100 texts per request) and
> task-type hints (RETRIEVAL_DOCUMENT vs RETRIEVAL_QUERY) for improved relevance.
> Source: ai.google.dev/gemini-api/docs/embeddings

---

## Appendix: Environment Variables

```bash
# Required for cloud API pipeline
GEMINI_API_KEY=your-gemini-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Optional (for Google Cloud TTS instead of ElevenLabs)
GOOGLE_TTS_API_KEY=your-google-tts-key

# Optional (for Anthropic Claude instead of Gemini for script generation)
ANTHROPIC_API_KEY=your-anthropic-api-key

# Optional (for local pipeline via Ollama)
OLLAMA_BASE_URL=http://localhost:11434
```

## Appendix: npm Dependencies (Complete)

```json
{
  "dependencies": {
    "pdf-parse": "^1.1.1",
    "mammoth": "^1.8.0",
    "@mozilla/readability": "^0.5.0",
    "linkedom": "^0.18.0",
    "cheerio": "^1.0.0",
    "youtube-transcript": "^1.2.1",
    "@google/generative-ai": "^0.21.0",
    "fluent-ffmpeg": "^2.1.3"
  },
  "devDependencies": {
    "@types/fluent-ffmpeg": "^2.1.24",
    "vitest": "^2.0.0"
  },
  "peerDependencies": {
    "ffmpeg": "System-installed FFmpeg 6.x+ required"
  }
}
```
