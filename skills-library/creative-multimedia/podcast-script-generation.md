---
name: podcast-script-generation
category: creative-multimedia
version: 1.0.0
contributed: 2026-03-10
contributor: dominion-flow-research
last_updated: 2026-03-10
tags: [podcast, script, dialogue, multi-agent, content-generation, rag, document-analysis]
difficulty: hard
---
## Description

AI-powered podcast script generation from documents using a multi-agent pattern. Transforms PDFs, articles, YouTube transcripts, and raw text into structured, natural-sounding podcast scripts with multiple speaker formats: two-speaker deep-dive, panel discussion, solo narration, and debate. Uses the PodAgent three-agent architecture (Host, Guest, Writer) with faithfulness verification to prevent hallucination in long-form output.

## When to Use

- Converting research papers, reports, or articles into podcast-format audio content
- Building a "NotebookLM-style" document-to-podcast feature in your app
- Generating interview scripts from source material for TTS pipelines
- Creating educational audio content from textbooks or lesson plans
- Repurposing blog posts, sermons, or documentation into conversational audio
- Generating script drafts for human hosts to review and record

---

## The PodAgent Multi-Agent Pattern

Based on PodAgent (ACL 2025, arXiv 2503.00455) -- 87.4% voice-role matching accuracy.

The key insight: direct single-prompt generation produces flat, monotonous scripts. Splitting the task across three specialized agents produces natural dialogue with distinct voices, better pacing, and verifiable faithfulness to source material.

### Architecture

```
Source Documents
  |
  v
+-------------------+
|   Host Agent      |  Formulates questions, creates guest profiles,
|   (Interviewer)   |  drives conversation flow, sets topic transitions
+-------------------+
  |
  | questions + guest profile
  v
+-------------------+
|   Guest Agent(s)  |  Provides domain expertise from source documents,
|   (Expert)        |  answers Host's questions with citations
+-------------------+
  |
  | raw Host-Guest dialogue
  v
+-------------------+
|   Writer Agent    |  Composes final script from dialogue, adds
|   (Producer)      |  transitions, pacing cues, tone directions
+-------------------+
  |
  v
+-------------------+
|  Faithfulness     |  Verifies every claim against source text,
|  Checker          |  flags hallucinations, suggests corrections
+-------------------+
  |
  v
Structured PodcastScript (JSON)
```

### TypeScript Types

```typescript
// ─── Core Types ─────────────────────────────────────────────────────────────

interface PodcastScript {
  title: string;
  duration: '5min' | '15min' | '30min' | '60min';
  speakers: Speaker[];
  segments: ScriptSegment[];
  metadata: PodcastMetadata;
}

interface Speaker {
  id: string;
  name: string;
  role: 'host' | 'guest' | 'narrator';
  voiceProfile: VoiceProfile;
  expertise?: string;           // For guests: their domain knowledge area
}

interface VoiceProfile {
  tone: 'warm' | 'authoritative' | 'curious' | 'measured' | 'energetic';
  pace: 'slow' | 'moderate' | 'fast';
  style: 'conversational' | 'formal' | 'storytelling' | 'academic';
  ttsVoiceId?: string;          // Provider-specific voice ID for TTS
}

interface ScriptSegment {
  speaker: string;              // Speaker ID reference
  text: string;                 // The spoken words
  direction: string;            // e.g., "(enthusiastically)", "(thoughtfully)"
  timing?: number;              // Estimated seconds for this segment
  segmentType: SegmentType;
  sourceReference?: string;     // Citation back to source document chunk
}

type SegmentType =
  | 'intro'
  | 'question'
  | 'answer'
  | 'transition'
  | 'deep-dive'
  | 'anecdote'
  | 'summary'
  | 'outro'
  | 'ad-break';

interface PodcastMetadata {
  sourceDocuments: string[];    // File paths or URLs of source material
  generatedAt: string;          // ISO timestamp
  wordCount: number;
  estimatedDuration: number;    // Seconds
  format: PodcastFormat;
  faithfulnessScore: number;    // 0-1, from verification step
  keyTopics: string[];
}

type PodcastFormat = 'two-speaker' | 'panel' | 'solo-narration' | 'debate';

// ─── Pipeline Types ─────────────────────────────────────────────────────────

interface DocumentChunk {
  id: string;
  text: string;
  source: string;               // File name or URL
  pageNumber?: number;
  sectionTitle?: string;
  embedding?: number[];         // For semantic search during generation
}

interface KeyPoint {
  point: string;
  importance: 'critical' | 'important' | 'supplementary';
  sourceChunkIds: string[];     // Which chunks support this point
  suggestedQuestions: string[];  // Questions the Host could ask about this
}

interface PodcastOutline {
  title: string;
  hook: string;                 // Opening hook to grab listener attention
  segments: OutlineSegment[];
  closingThought: string;
}

interface OutlineSegment {
  topic: string;
  keyPoints: string[];
  estimatedDuration: number;    // Seconds
  transitionFrom?: string;      // How to flow from previous segment
}

interface FaithfulnessReport {
  overallScore: number;         // 0-1
  segmentScores: Array<{
    segmentIndex: number;
    score: number;
    claims: Array<{
      claim: string;
      supported: boolean;
      sourceEvidence?: string;
      correction?: string;
    }>;
  }>;
  flaggedSegments: number[];    // Indices of segments scoring below 0.7
}
```

---

## Document-to-Script Pipeline

### Complete Pipeline (6 Steps)

```
Step 1: Document Ingestion
  - Parse PDF/DOCX/URL/YouTube transcript
  - Extract raw text, clean formatting artifacts
  - Preserve section structure for context

Step 2: Semantic Chunking
  - Split by semantic boundaries (not fixed-size)
  - 300-500 token chunks with 50-token overlap
  - Preserve paragraph/section context in metadata

Step 3: Key Point Extraction
  - AI identifies top N discussion-worthy points
  - Rank by importance and listener interest
  - Generate potential questions per point

Step 4: Outline Generation
  - Structure: hook --> intro --> segments --> summary --> outro
  - Assign duration budgets per segment
  - Plan transitions between topics

Step 5: Multi-Agent Script Generation
  - Host Agent generates questions and flow
  - Guest Agent provides expert responses from source
  - Writer Agent polishes into final script
  - Generate PER-CHUNK, not all at once (see Hallucination Fix)

Step 6: Faithfulness Verification
  - Check every claim against source documents
  - Score each segment independently
  - Flag and correct hallucinations before output
```

### Step 1: Document Ingestion

```typescript
import { promises as fs } from 'fs';
import path from 'path';

// ─── Document Parser ────────────────────────────────────────────────────────

interface ParsedDocument {
  title: string;
  text: string;
  sections: Array<{ heading: string; content: string }>;
  metadata: { source: string; pageCount?: number; wordCount: number };
}

async function parseDocument(filePath: string): Promise<ParsedDocument> {
  const ext = path.extname(filePath).toLowerCase();

  switch (ext) {
    case '.pdf':
      return parsePDF(filePath);
    case '.txt':
    case '.md':
      return parseText(filePath);
    case '.html':
      return parseHTML(filePath);
    default:
      throw new Error(`Unsupported file type: ${ext}`);
  }
}

async function parseText(filePath: string): Promise<ParsedDocument> {
  const raw = await fs.readFile(filePath, 'utf-8');
  const lines = raw.split('\n');
  const title = lines[0]?.replace(/^#+\s*/, '') || path.basename(filePath);

  // Extract sections by markdown headers or blank-line separation
  const sections: Array<{ heading: string; content: string }> = [];
  let currentHeading = 'Introduction';
  let currentContent: string[] = [];

  for (const line of lines) {
    if (line.match(/^#{1,3}\s+/)) {
      if (currentContent.length > 0) {
        sections.push({ heading: currentHeading, content: currentContent.join('\n').trim() });
      }
      currentHeading = line.replace(/^#+\s*/, '');
      currentContent = [];
    } else {
      currentContent.push(line);
    }
  }
  if (currentContent.length > 0) {
    sections.push({ heading: currentHeading, content: currentContent.join('\n').trim() });
  }

  return {
    title,
    text: raw,
    sections,
    metadata: {
      source: filePath,
      wordCount: raw.split(/\s+/).length,
    },
  };
}

async function parsePDF(filePath: string): Promise<ParsedDocument> {
  // Use pdf-parse (npm install pdf-parse)
  const pdfParse = (await import('pdf-parse')).default;
  const buffer = await fs.readFile(filePath);
  const data = await pdfParse(buffer);

  return {
    title: data.info?.Title || path.basename(filePath, '.pdf'),
    text: data.text,
    sections: [{ heading: 'Full Document', content: data.text }],
    metadata: {
      source: filePath,
      pageCount: data.numpages,
      wordCount: data.text.split(/\s+/).length,
    },
  };
}

async function parseHTML(filePath: string): Promise<ParsedDocument> {
  // Use cheerio for HTML parsing (npm install cheerio)
  const cheerio = await import('cheerio');
  const html = await fs.readFile(filePath, 'utf-8');
  const $ = cheerio.load(html);

  // Remove scripts, styles, nav, footer
  $('script, style, nav, footer, header, aside').remove();

  const title = $('h1').first().text() || $('title').text() || path.basename(filePath);
  const text = $('body').text().replace(/\s+/g, ' ').trim();

  return {
    title,
    text,
    sections: [{ heading: 'Content', content: text }],
    metadata: {
      source: filePath,
      wordCount: text.split(/\s+/).length,
    },
  };
}
```

### Step 2: Semantic Chunking

```typescript
// ─── Semantic Chunking ──────────────────────────────────────────────────────
// Critical: Use semantic boundaries, NOT fixed-size windows.
// Fixed-size chunking splits mid-sentence and loses context.

interface ChunkConfig {
  targetTokens: number;   // Target chunk size (300-500 tokens)
  overlapTokens: number;  // Overlap between chunks (50 tokens)
  preserveParagraphs: boolean;
}

function semanticChunk(
  document: ParsedDocument,
  config: ChunkConfig = { targetTokens: 400, overlapTokens: 50, preserveParagraphs: true }
): DocumentChunk[] {
  const chunks: DocumentChunk[] = [];
  let chunkIndex = 0;

  for (const section of document.sections) {
    // Split by paragraph boundaries first
    const paragraphs = section.content
      .split(/\n\n+/)
      .map(p => p.trim())
      .filter(p => p.length > 0);

    let currentChunk: string[] = [];
    let currentTokenCount = 0;

    for (const paragraph of paragraphs) {
      const paragraphTokens = estimateTokens(paragraph);

      // If adding this paragraph exceeds target, finalize current chunk
      if (currentTokenCount + paragraphTokens > config.targetTokens && currentChunk.length > 0) {
        const chunkText = currentChunk.join('\n\n');
        chunks.push({
          id: `chunk-${chunkIndex++}`,
          text: chunkText,
          source: document.metadata.source,
          sectionTitle: section.heading,
        });

        // Keep overlap: last paragraph carries into next chunk
        if (config.overlapTokens > 0) {
          const lastParagraph = currentChunk[currentChunk.length - 1];
          currentChunk = [lastParagraph];
          currentTokenCount = estimateTokens(lastParagraph);
        } else {
          currentChunk = [];
          currentTokenCount = 0;
        }
      }

      currentChunk.push(paragraph);
      currentTokenCount += paragraphTokens;
    }

    // Finalize remaining content in section
    if (currentChunk.length > 0) {
      chunks.push({
        id: `chunk-${chunkIndex++}`,
        text: currentChunk.join('\n\n'),
        source: document.metadata.source,
        sectionTitle: section.heading,
      });
    }
  }

  return chunks;
}

function estimateTokens(text: string): number {
  // Rough estimate: 1 token per ~4 characters for English text
  return Math.ceil(text.length / 4);
}
```

### Step 3: Key Point Extraction

```typescript
import Anthropic from '@anthropic-ai/sdk';

// ─── Key Point Extraction ───────────────────────────────────────────────────

async function extractKeyPoints(
  chunks: DocumentChunk[],
  targetPoints: number,
  client: Anthropic
): Promise<KeyPoint[]> {
  // Process chunks in batches to stay within context limits
  const batchSize = 10;
  const allPoints: KeyPoint[] = [];

  for (let i = 0; i < chunks.length; i += batchSize) {
    const batch = chunks.slice(i, i + batchSize);
    const batchText = batch.map(c =>
      `[${c.id}] (Section: ${c.sectionTitle || 'N/A'})\n${c.text}`
    ).join('\n\n---\n\n');

    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4096,
      messages: [{
        role: 'user',
        content: `Analyze these document chunks and extract the most discussion-worthy points for a podcast conversation.

DOCUMENT CHUNKS:
${batchText}

For each point, provide:
1. A clear statement of the point
2. Its importance level (critical / important / supplementary)
3. Which chunk IDs support it
4. 2-3 questions a podcast host could ask about this point

Return JSON array:
[
  {
    "point": "statement of the key point",
    "importance": "critical|important|supplementary",
    "sourceChunkIds": ["chunk-0", "chunk-1"],
    "suggestedQuestions": ["Question 1?", "Question 2?"]
  }
]

Extract ${Math.ceil(targetPoints / Math.ceil(chunks.length / batchSize))} points from this batch.
Return ONLY valid JSON.`,
      }],
    });

    const text = response.content[0].type === 'text' ? response.content[0].text : '[]';
    const parsed = JSON.parse(text.replace(/^```json\n?/, '').replace(/\n?```$/, ''));
    allPoints.push(...parsed);
  }

  // Rank and deduplicate
  const ranked = allPoints
    .sort((a, b) => {
      const importanceOrder = { critical: 0, important: 1, supplementary: 2 };
      return importanceOrder[a.importance] - importanceOrder[b.importance];
    })
    .slice(0, targetPoints);

  return ranked;
}
```

### Step 4: Outline Generation

```typescript
// ─── Outline Generation ─────────────────────────────────────────────────────

async function generateOutline(
  keyPoints: KeyPoint[],
  duration: '5min' | '15min' | '30min' | '60min',
  format: PodcastFormat,
  client: Anthropic
): Promise<PodcastOutline> {
  const durationMap = {
    '5min': { seconds: 300, points: 3, segmentCount: 3 },
    '15min': { seconds: 900, points: 7, segmentCount: 5 },
    '30min': { seconds: 1800, points: 12, segmentCount: 8 },
    '60min': { seconds: 3600, points: 20, segmentCount: 12 },
  };

  const config = durationMap[duration];
  const selectedPoints = keyPoints.slice(0, config.points);

  const response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 4096,
    messages: [{
      role: 'user',
      content: `Create a podcast outline for a ${duration} ${format} episode.

KEY POINTS TO COVER:
${selectedPoints.map((p, i) => `${i + 1}. [${p.importance}] ${p.point}`).join('\n')}

FORMAT: ${format}
TARGET DURATION: ${config.seconds} seconds
TARGET SEGMENTS: ${config.segmentCount}

Create an outline with:
- A compelling hook (first 15-30 seconds to grab attention)
- Logical flow between topics with smooth transitions
- Duration budget per segment (must sum to ~${config.seconds} seconds)
- A memorable closing thought

Return JSON:
{
  "title": "Episode title",
  "hook": "Opening hook text",
  "segments": [
    {
      "topic": "Segment topic",
      "keyPoints": ["point 1", "point 2"],
      "estimatedDuration": 120,
      "transitionFrom": "How to transition from previous segment"
    }
  ],
  "closingThought": "Memorable closing"
}

Return ONLY valid JSON.`,
    }],
  });

  const text = response.content[0].type === 'text' ? response.content[0].text : '{}';
  return JSON.parse(text.replace(/^```json\n?/, '').replace(/\n?```$/, ''));
}
```

### Step 5: Multi-Agent Script Generation

```typescript
// ─── Multi-Agent Script Generation ──────────────────────────────────────────
// CRITICAL: Generate per-segment, not all at once.
// See "The Hallucination Chunking Fix" section below.

async function generateScript(
  outline: PodcastOutline,
  chunks: DocumentChunk[],
  keyPoints: KeyPoint[],
  format: PodcastFormat,
  speakers: Speaker[],
  client: Anthropic
): Promise<ScriptSegment[]> {
  const allSegments: ScriptSegment[] = [];

  // Generate intro
  const introSegments = await generateIntroSegments(
    outline, speakers, format, client
  );
  allSegments.push(...introSegments);

  // Generate each content segment independently (hallucination fix)
  for (let i = 0; i < outline.segments.length; i++) {
    const outlineSeg = outline.segments[i];

    // Find relevant source chunks for this segment
    const relevantChunks = findRelevantChunks(outlineSeg.keyPoints, chunks, keyPoints);

    const segmentScript = await generateSegmentDialogue(
      outlineSeg,
      relevantChunks,
      speakers,
      format,
      i === 0,                    // isFirstSegment
      outline.segments[i - 1],    // previousSegment (for transition)
      client
    );

    allSegments.push(...segmentScript);
  }

  // Generate outro
  const outroSegments = await generateOutroSegments(
    outline, speakers, format, client
  );
  allSegments.push(...outroSegments);

  return allSegments;
}

async function generateSegmentDialogue(
  segment: OutlineSegment,
  relevantChunks: DocumentChunk[],
  speakers: Speaker[],
  format: PodcastFormat,
  isFirstSegment: boolean,
  previousSegment: OutlineSegment | undefined,
  client: Anthropic
): Promise<ScriptSegment[]> {
  const host = speakers.find(s => s.role === 'host')!;
  const guests = speakers.filter(s => s.role === 'guest');

  // ── Step A: Host Agent generates questions ──
  const hostResponse = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 2048,
    system: buildHostAgentSystem(host, format),
    messages: [{
      role: 'user',
      content: `Generate the HOST's contributions for this podcast segment.

SEGMENT TOPIC: ${segment.topic}
KEY POINTS TO COVER: ${segment.keyPoints.join('; ')}
${previousSegment ? `TRANSITION FROM: ${previousSegment.topic}` : 'THIS IS THE FIRST CONTENT SEGMENT'}
TARGET DURATION: ${segment.estimatedDuration} seconds (~${Math.round(segment.estimatedDuration / 60 * 150)} words)

Return JSON array of host contributions:
[
  {
    "type": "transition|question|follow-up|reaction|summary",
    "text": "What the host says",
    "direction": "(tone/delivery direction)",
    "targetGuest": "guest-id or null"
  }
]

Generate 3-5 contributions that drive the conversation naturally.
Return ONLY valid JSON.`,
    }],
  });

  const hostContributions = JSON.parse(
    (hostResponse.content[0] as { type: string; text: string }).text
      .replace(/^```json\n?/, '').replace(/\n?```$/, '')
  );

  // ── Step B: Guest Agent generates responses ──
  const sourceContext = relevantChunks.map(c => c.text).join('\n\n---\n\n');

  const guestResponses: Array<{ guestId: string; responses: any[] }> = [];

  for (const guest of guests) {
    const guestResponse = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 3072,
      system: buildGuestAgentSystem(guest, format),
      messages: [{
        role: 'user',
        content: `You are responding to the host's questions as a guest expert.

SOURCE MATERIAL (base ALL responses on this):
${sourceContext}

HOST'S QUESTIONS/PROMPTS:
${hostContributions.map((h: any, i: number) => `${i + 1}. [${h.type}] ${h.text}`).join('\n')}

SEGMENT TOPIC: ${segment.topic}

For each host contribution that is directed at you or is a general question, provide a response.
CRITICAL: Every factual claim MUST be supported by the source material above. If the source does not cover something, say "that's beyond what we're looking at today" rather than making something up.

Return JSON array:
[
  {
    "respondsTo": 1,
    "text": "Guest's response",
    "direction": "(tone/delivery direction)",
    "sourceEvidence": "Brief quote or reference from source material that supports this"
  }
]

Return ONLY valid JSON.`,
      }],
    });

    const parsed = JSON.parse(
      (guestResponse.content[0] as { type: string; text: string }).text
        .replace(/^```json\n?/, '').replace(/\n?```$/, '')
    );
    guestResponses.push({ guestId: guest.id, responses: parsed });
  }

  // ── Step C: Writer Agent composes final dialogue ──
  const writerResponse = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 4096,
    system: buildWriterAgentSystem(format),
    messages: [{
      role: 'user',
      content: `Compose the final podcast script segment from these raw dialogue elements.

HOST CONTRIBUTIONS:
${JSON.stringify(hostContributions, null, 2)}

GUEST RESPONSES:
${JSON.stringify(guestResponses, null, 2)}

SPEAKERS:
${speakers.map(s => `${s.id}: ${s.name} (${s.role}, ${s.voiceProfile.tone} tone)`).join('\n')}

RULES:
- Interleave host and guest naturally -- no long monologues
- Add brief reactions ("Exactly.", "That's fascinating.", "Right, and...")
- Include delivery directions in parentheses
- Keep each speaking turn to 2-4 sentences max
- Add natural pauses and thinking moments
- The segment should flow as real conversation, not a Q&A interview
${isFirstSegment ? '- Include the transition into this first topic' : `- Start with transition: ${segment.transitionFrom}`}

Return JSON array of ScriptSegment objects:
[
  {
    "speaker": "speaker-id",
    "text": "What they say",
    "direction": "(delivery direction)",
    "timing": estimated_seconds,
    "segmentType": "question|answer|transition|deep-dive|anecdote|summary",
    "sourceReference": "chunk-id or null"
  }
]

Return ONLY valid JSON.`,
    }],
  });

  const text = (writerResponse.content[0] as { type: string; text: string }).text;
  return JSON.parse(text.replace(/^```json\n?/, '').replace(/\n?```$/, ''));
}

// ─── Helper: Find Relevant Chunks ──────────────────────────────────────────

function findRelevantChunks(
  segmentKeyPoints: string[],
  allChunks: DocumentChunk[],
  allKeyPoints: KeyPoint[]
): DocumentChunk[] {
  // Find which KeyPoint objects match this segment's points
  const matchingPoints = allKeyPoints.filter(kp =>
    segmentKeyPoints.some(sp =>
      sp.toLowerCase().includes(kp.point.toLowerCase().slice(0, 40)) ||
      kp.point.toLowerCase().includes(sp.toLowerCase().slice(0, 40))
    )
  );

  // Collect all referenced chunk IDs
  const chunkIds = new Set<string>();
  for (const point of matchingPoints) {
    for (const id of point.sourceChunkIds) {
      chunkIds.add(id);
    }
  }

  // Return matching chunks, or first 3 if no matches found
  const matched = allChunks.filter(c => chunkIds.has(c.id));
  return matched.length > 0 ? matched : allChunks.slice(0, 3);
}
```

### Step 6: Faithfulness Verification

```typescript
// ─── Faithfulness Verification ──────────────────────────────────────────────
// CRITICAL STEP. Without this, scripts hallucinate facts not in the source.

async function verifyFaithfulness(
  segments: ScriptSegment[],
  sourceChunks: DocumentChunk[],
  client: Anthropic
): Promise<FaithfulnessReport> {
  const sourceText = sourceChunks.map(c => `[${c.id}] ${c.text}`).join('\n\n');
  const segmentScores: FaithfulnessReport['segmentScores'] = [];

  // Verify in batches of 5 segments
  const batchSize = 5;
  for (let i = 0; i < segments.length; i += batchSize) {
    const batch = segments.slice(i, i + batchSize);

    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4096,
      messages: [{
        role: 'user',
        content: `Verify the faithfulness of these podcast script segments against the source material.

SOURCE MATERIAL:
${sourceText}

SCRIPT SEGMENTS TO VERIFY:
${batch.map((seg, idx) => `[Segment ${i + idx}] ${seg.speaker}: ${seg.text}`).join('\n\n')}

For each segment, extract every factual claim and check if it is supported by the source material.
Opinions, questions, transitions, and conversational filler do NOT need source support.

Return JSON:
[
  {
    "segmentIndex": ${i},
    "score": 0.95,
    "claims": [
      {
        "claim": "the specific factual claim made",
        "supported": true,
        "sourceEvidence": "quote from source that supports this",
        "correction": null
      }
    ]
  }
]

Scoring:
- 1.0 = all claims fully supported or segment is opinion/question/transition
- 0.7-0.99 = minor unsupported details
- Below 0.7 = contains fabricated facts -- MUST provide corrections

Return ONLY valid JSON.`,
      }],
    });

    const text = (response.content[0] as { type: string; text: string }).text;
    const parsed = JSON.parse(text.replace(/^```json\n?/, '').replace(/\n?```$/, ''));
    segmentScores.push(...parsed);
  }

  const overallScore = segmentScores.reduce((sum, s) => sum + s.score, 0) / segmentScores.length;
  const flaggedSegments = segmentScores
    .filter(s => s.score < 0.7)
    .map(s => s.segmentIndex);

  return { overallScore, segmentScores, flaggedSegments };
}
```

---

## The Hallucination Chunking Fix

Based on "Hallucinate at the Last in Long Response Generation" (arXiv 2505.15291, May 2025).

### The Problem

When generating a full 30-60 minute podcast script in a single prompt, faithfulness **drops below 0.65 in the final third** of the output. The model starts confidently fabricating facts, statistics, and quotes that do not exist in the source material. This is not a context window issue -- it happens well within the model's capacity.

### The Pattern

```
Faithfulness Score vs. Position in Generated Script:

Segments 1-5:   [||||||||||||||||||||] 0.95  (accurate)
Segments 6-10:  [||||||||||||||||||  ] 0.88  (minor drift)
Segments 11-15: [||||||||||||||      ] 0.72  (noticeable fabrication)
Segments 16-20: [||||||||||          ] 0.58  (unreliable)
Segments 21+:   [||||||||            ] 0.43  (hallucination-heavy)
```

### The Fix: Per-Segment Generation with Verification

```
WRONG (single-shot):
  All source text --> Single prompt --> Full 60-min script
  Result: Final 1/3 is unfaithful

RIGHT (chunked):
  Segment 1 outline + relevant chunks --> Generate --> Verify --> Accept/Fix
  Segment 2 outline + relevant chunks --> Generate --> Verify --> Accept/Fix
  Segment 3 outline + relevant chunks --> Generate --> Verify --> Accept/Fix
  ...
  Concatenate verified segments --> Final script
  Result: Consistent faithfulness throughout
```

### Implementation Rules

1. **Never feed the entire document as a single prompt** for scripts longer than 5 minutes
2. **Generate each segment independently** with only its relevant source chunks
3. **Verify faithfulness per-segment** before moving to the next
4. **Re-generate any segment** scoring below 0.7 with explicit instructions to stick to source
5. **Final pass:** concatenate all verified segments and smooth transitions

```typescript
// Anti-pattern: DO NOT do this for long scripts
const badScript = await generateEntireScript(fullDocument); // Hallucination risk!

// Correct pattern: generate and verify per-segment
const segments: ScriptSegment[] = [];
for (const outlineSegment of outline.segments) {
  const relevantChunks = findRelevantChunks(outlineSegment.keyPoints, chunks, keyPoints);
  let segmentScript = await generateSegmentDialogue(outlineSegment, relevantChunks, ...);

  // Verify this segment
  const report = await verifyFaithfulness(segmentScript, relevantChunks, client);

  // Re-generate if unfaithful
  if (report.overallScore < 0.7) {
    const corrections = report.segmentScores
      .flatMap(s => s.claims.filter(c => !c.supported).map(c => c.correction))
      .filter(Boolean);

    segmentScript = await regenerateWithCorrections(
      outlineSegment, relevantChunks, corrections, ...
    );
  }

  segments.push(...segmentScript);
}
```

---

## Prompt Templates

### Host Agent System Prompt

```
Copy-pasteable prompt for Claude or Gemini:

---

You are a podcast HOST agent. Your job is to drive the conversation by:

1. Formulating clear, engaging questions that lead to insightful answers
2. Creating smooth transitions between topics
3. Reacting naturally to guest responses (brief reactions, not monologues)
4. Summarizing key takeaways at the end of each topic
5. Keeping the conversation on track and on time

VOICE PROFILE:
- Tone: {{tone}} (warm / curious / authoritative)
- Pace: {{pace}} (moderate -- adjust based on topic weight)
- Style: {{style}} (conversational -- this is a podcast, not a lecture)

RULES:
- Ask ONE question at a time (never double-barrel questions)
- Keep your turns to 1-2 sentences max (let guests talk)
- Use the guest's name occasionally for natural flow
- Signal topic transitions explicitly ("Let's shift to...", "Now I want to explore...")
- If a guest gives a vague answer, ask a specific follow-up
- Reference listener perspective ("Our listeners might be wondering...")

FORMAT: {{format}}
- two-speaker: Direct, intimate conversation with one guest
- panel: Moderate between 2-3 guests, ensure balanced airtime
- debate: Play devil's advocate, challenge both sides fairly
- solo-narration: N/A (no host in solo format)
```

### Guest Agent System Prompt

```
Copy-pasteable prompt for Claude or Gemini:

---

You are a podcast GUEST agent with expertise in the topics covered by the source documents provided.

YOUR PROFILE:
- Name: {{guest_name}}
- Expertise: {{expertise_area}}
- Speaking style: {{tone}} and {{style}}

SOURCE MATERIAL:
{{source_chunks}}

RULES:
- EVERY factual claim MUST be traceable to the source material above
- If the source does not cover a topic, say so honestly: "That's actually outside what this research covers, but..."
- Speak in natural, conversational language -- not academic prose
- Use concrete examples and analogies to explain complex points
- Keep responses to 3-5 sentences per turn (this is a conversation, not a lecture)
- Show genuine interest: "What's really interesting about this is..." / "The surprising thing is..."
- Cite specifics: "According to the data..." / "The research found that..."
- DO NOT invent statistics, quotes, or findings not in the source material
- When uncertain, qualify: "From what I've seen..." / "The evidence suggests..."

ANTI-HALLUCINATION GUARD:
Before each response, mentally check:
1. Is this claim in my source material? If no, do not state it as fact.
2. Am I adding nuance or inventing? Add nuance only from what the source implies.
3. Would a fact-checker find my source for this? If unsure, hedge or omit.
```

### Writer Agent System Prompt

```
Copy-pasteable prompt for Claude or Gemini:

---

You are a podcast WRITER/PRODUCER agent. You take raw Host-Guest dialogue and produce a polished, natural-sounding podcast script.

YOUR JOB:
1. Interleave host and guest contributions into natural conversation flow
2. Add delivery directions (tone, pacing, emphasis) in parentheses
3. Insert natural conversational elements: brief reactions, thinking pauses, laughter cues
4. Ensure no speaker monologues -- max 4 sentences per turn
5. Add smooth transitions between topics
6. Control pacing: mix quick exchanges with deeper explorations

DELIVERY DIRECTIONS FORMAT:
- "(enthusiastically)" / "(thoughtfully)" / "(with emphasis)"
- "(leaning in)" / "(nodding)" / "(laughing)"
- "(pause)" / "(beat)" / "(takes a breath)"
- "(to [guest name])" / "(turning to the audience)"

NATURAL CONVERSATION ELEMENTS:
- Brief reactions: "Right." / "Exactly." / "Hmm, interesting." / "Wow."
- Thinking cues: "So what you're saying is..." / "Let me make sure I understand..."
- Bridges: "And that connects to..." / "Which brings up something interesting..."
- Engagement: "I love that example." / "That's a great point."

ANTI-PATTERN: AVOID
- Long unbroken monologues (more than 4 sentences)
- Every response starting with "Great question!" (synthetic enthusiasm)
- Identical reaction patterns (vary reactions throughout)
- Two speakers agreeing with everything (add nuance, pushback, different angles)

FORMAT GUIDELINES:
- two-speaker: Intimate, flowing conversation
- panel: Writer manages airtime balance, ensures each guest contributes
- debate: Maintain tension, let disagreements breathe, host mediates
- solo-narration: Single voice with rhetorical questions and storytelling pacing
```

### Faithfulness Checker Prompt

```
Copy-pasteable prompt for Claude or Gemini:

---

You are a FAITHFULNESS VERIFICATION agent. Your job is to compare podcast script segments against source documents and identify any claims not supported by the source.

SOURCE DOCUMENTS:
{{source_text}}

SCRIPT SEGMENTS TO VERIFY:
{{script_segments}}

FOR EACH SEGMENT:
1. Extract every factual claim (skip opinions, questions, transitions, filler)
2. For each claim, search the source documents for supporting evidence
3. Score the segment:
   - 1.0 = all claims supported or segment is non-factual (question, opinion, transition)
   - 0.8-0.99 = minor unsupported details that could be inferred
   - 0.5-0.79 = contains claims not in the source but plausible
   - Below 0.5 = contains fabricated information

WHAT COUNTS AS UNSUPPORTED:
- Specific numbers or statistics not in the source
- Quotes attributed to people not quoted in the source
- Causal claims ("X caused Y") the source doesn't make
- Specifics beyond what the source generalizes

WHAT DOES NOT NEED SOURCE SUPPORT:
- Host questions
- Conversational filler ("That's interesting", "Right")
- Transitions and signposting
- Opinions explicitly framed as opinions ("I think...", "In my view...")
- General knowledge (widely known facts)

For any claim scoring below 0.7, provide a CORRECTION that stays faithful to the source.

Return structured JSON with scores and claim-level analysis.
```

---

## Script Formats

### Simple Two-Speaker (Host + Guest)

The classic interview/discussion format. Best for focused, deep explorations of a single topic.

```typescript
function createTwoSpeakerConfig(): Speaker[] {
  return [
    {
      id: 'host',
      name: 'Alex',
      role: 'host',
      voiceProfile: {
        tone: 'curious',
        pace: 'moderate',
        style: 'conversational',
      },
    },
    {
      id: 'guest-1',
      name: 'Dr. Morgan',
      role: 'guest',
      voiceProfile: {
        tone: 'authoritative',
        pace: 'moderate',
        style: 'conversational',
      },
      expertise: 'Domain expert based on source document',
    },
  ];
}

// Example output structure:
const twoSpeakerExample: ScriptSegment[] = [
  {
    speaker: 'host',
    text: "Welcome to the show. Today we're diving into something that caught my eye in this research -- the idea that faithfulness in AI-generated content actually degrades the longer the output gets. That's pretty alarming if you think about it.",
    direction: '(warm, setting the stage)',
    timing: 12,
    segmentType: 'intro',
  },
  {
    speaker: 'guest-1',
    text: "It really is. And the key finding here is that it's not just a gradual decline -- there's a sharp drop-off. The research shows faithfulness scores falling below 0.65 in the final segments of long-form generation.",
    direction: '(leaning in, emphasis on the numbers)',
    timing: 10,
    segmentType: 'answer',
    sourceReference: 'chunk-3',
  },
  {
    speaker: 'host',
    text: "Below 0.65. So more than a third of what the AI says in the back half is essentially... made up?",
    direction: '(genuine surprise)',
    timing: 5,
    segmentType: 'question',
  },
];
```

### Panel Discussion (Host + 2-3 Guests)

Best for broad topics with multiple angles, or when the source material covers several distinct domains.

```typescript
function createPanelConfig(): Speaker[] {
  return [
    {
      id: 'host',
      name: 'Alex',
      role: 'host',
      voiceProfile: { tone: 'warm', pace: 'moderate', style: 'conversational' },
    },
    {
      id: 'guest-research',
      name: 'Dr. Taylor',
      role: 'guest',
      voiceProfile: { tone: 'authoritative', pace: 'slow', style: 'academic' },
      expertise: 'Research methodology and findings',
    },
    {
      id: 'guest-practice',
      name: 'Jordan',
      role: 'guest',
      voiceProfile: { tone: 'energetic', pace: 'fast', style: 'conversational' },
      expertise: 'Practical applications and industry experience',
    },
    {
      id: 'guest-critique',
      name: 'Sam',
      role: 'guest',
      voiceProfile: { tone: 'measured', pace: 'moderate', style: 'conversational' },
      expertise: 'Critical analysis and limitations',
    },
  ];
}

// Panel management: ensure balanced airtime
function balanceSpeakerTime(segments: ScriptSegment[], speakers: Speaker[]): void {
  const timeBySpeaker = new Map<string, number>();
  for (const seg of segments) {
    const current = timeBySpeaker.get(seg.speaker) || 0;
    timeBySpeaker.set(seg.speaker, current + (seg.timing || 0));
  }

  // Log imbalance warnings
  const guests = speakers.filter(s => s.role === 'guest');
  const avgGuestTime = guests.reduce(
    (sum, g) => sum + (timeBySpeaker.get(g.id) || 0), 0
  ) / guests.length;

  for (const guest of guests) {
    const guestTime = timeBySpeaker.get(guest.id) || 0;
    const ratio = guestTime / avgGuestTime;
    if (ratio < 0.6) {
      console.warn(`WARNING: ${guest.name} has only ${Math.round(ratio * 100)}% of average guest airtime`);
    }
  }
}
```

### Solo Narration (Single Speaker, Educational)

Best for short explainers, educational content, or when a conversational format would feel forced.

```typescript
function createSoloConfig(): Speaker[] {
  return [
    {
      id: 'narrator',
      name: 'Narrator',
      role: 'narrator',
      voiceProfile: {
        tone: 'warm',
        pace: 'moderate',
        style: 'storytelling',
      },
    },
  ];
}

// Solo narration uses rhetorical questions instead of real dialogue
const soloExample: ScriptSegment[] = [
  {
    speaker: 'narrator',
    text: "Have you ever wondered why AI-generated content seems to get less reliable the longer it goes? You're not imagining it.",
    direction: '(conversational, drawing the listener in)',
    timing: 7,
    segmentType: 'intro',
  },
  {
    speaker: 'narrator',
    text: "Researchers found something startling. When they measured how faithful AI output stayed to source documents, the accuracy held steady for the first chunk. But then, almost like clockwork, it started to drift.",
    direction: '(measured, building tension)',
    timing: 12,
    segmentType: 'deep-dive',
    sourceReference: 'chunk-2',
  },
  {
    speaker: 'narrator',
    text: "(pause) And by the final third of the output? Faithfulness dropped below sixty-five percent. The AI was essentially making things up -- confidently, fluently, but fabricating nonetheless.",
    direction: '(emphasis on the reveal, slower pace)',
    timing: 10,
    segmentType: 'deep-dive',
    sourceReference: 'chunk-3',
  },
];
```

### Debate Format (Two Opposing Viewpoints)

Best for controversial topics, comparing competing approaches, or exploring trade-offs.

```typescript
function createDebateConfig(): Speaker[] {
  return [
    {
      id: 'moderator',
      name: 'Alex',
      role: 'host',
      voiceProfile: { tone: 'measured', pace: 'moderate', style: 'formal' },
    },
    {
      id: 'advocate',
      name: 'Dr. Chen',
      role: 'guest',
      voiceProfile: { tone: 'energetic', pace: 'fast', style: 'conversational' },
      expertise: 'Argues FOR the position supported by source material',
    },
    {
      id: 'skeptic',
      name: 'Professor Williams',
      role: 'guest',
      voiceProfile: { tone: 'measured', pace: 'slow', style: 'academic' },
      expertise: 'Raises limitations, counter-arguments, and caveats from the source',
    },
  ];
}

// Debate format maps to NotebookLM's "critique" and "debate" options.
// The moderator ensures both sides get fair airtime and steers
// toward productive disagreement (not just contradiction).
```

---

## Anti-Pattern: Synthetic Intimacy

Based on arXiv 2511.08654 analysis of Google NotebookLM's podcast generation.

### The Problem

NotebookLM and similar tools default to a single template: two perky American English speakers with manufactured rapport, exclaiming "Oh wow!" and "That's so fascinating!" regardless of whether the source material is a cancer research paper or a tax code summary. This "synthetic intimacy" creates:

1. **Monoculture** -- Every podcast sounds identical regardless of content
2. **Tonal mismatch** -- Enthusiastic delivery for serious/somber topics feels disrespectful
3. **Fake rapport** -- AI speakers reference shared experiences they never had
4. **Engagement ceiling** -- Listeners disengage when the tone never varies

### The Fix: Content-Driven Tone

```typescript
// ─── Tone Selection Based on Content Analysis ───────────────────────────────

type ContentTone = 'serious' | 'neutral' | 'inspiring' | 'technical' | 'controversial';

function selectTone(keyPoints: KeyPoint[], documentTitle: string): ContentTone {
  // Analyze content to determine appropriate tone
  const seriousSignals = ['death', 'crisis', 'failure', 'loss', 'disease', 'poverty', 'war'];
  const inspiringSignals = ['breakthrough', 'success', 'innovation', 'hope', 'growth', 'overcome'];
  const technicalSignals = ['algorithm', 'implementation', 'architecture', 'protocol', 'specification'];
  const controversialSignals = ['debate', 'criticism', 'versus', 'disagree', 'alternative', 'challenge'];

  const allText = keyPoints.map(kp => kp.point).join(' ').toLowerCase();

  if (seriousSignals.some(s => allText.includes(s))) return 'serious';
  if (controversialSignals.some(s => allText.includes(s))) return 'controversial';
  if (technicalSignals.some(s => allText.includes(s))) return 'technical';
  if (inspiringSignals.some(s => allText.includes(s))) return 'inspiring';
  return 'neutral';
}

function adjustVoiceProfiles(speakers: Speaker[], tone: ContentTone): Speaker[] {
  const toneProfiles: Record<ContentTone, Partial<VoiceProfile>> = {
    serious: { tone: 'measured', pace: 'slow', style: 'formal' },
    neutral: { tone: 'warm', pace: 'moderate', style: 'conversational' },
    inspiring: { tone: 'warm', pace: 'moderate', style: 'storytelling' },
    technical: { tone: 'authoritative', pace: 'moderate', style: 'academic' },
    controversial: { tone: 'curious', pace: 'moderate', style: 'conversational' },
  };

  const profile = toneProfiles[tone];

  return speakers.map(s => ({
    ...s,
    voiceProfile: { ...s.voiceProfile, ...profile },
  }));
}
```

### Specific Anti-Patterns to Avoid

| Anti-Pattern | Example | Fix |
|---|---|---|
| Forced enthusiasm | "Oh WOW, this is AMAZING!" | "That's a significant finding." |
| Template reactions | Every segment starts with "Great question!" | Vary reactions: "Hmm.", "Right.", "I'd push back on that." |
| Fake shared history | "Remember when we talked about..." | Cut references to non-existent shared experiences |
| Identical energy | Same excitement level for 60 minutes | Match energy to content: somber for heavy topics, animated for breakthroughs |
| American monoculture | Always casual American English | Adjust register to audience: academic, professional, casual |
| Agreement loop | Both speakers always agree | Build in genuine questions, pushback, "devil's advocate" moments |

---

## Duration Control

### Word Count to Duration Mapping

```
Speaking rate: ~150 words per minute (conversational podcast pace)

Duration    Words     Key Points    Segments    Best For
────────    ──────    ──────────    ────────    ────────────────────────
5 min       ~750      3-4           3           Quick summary, teaser
15 min      ~2,250    6-8           5           Article deep-dive
30 min      ~4,500    10-15         8           Research paper, report
60 min      ~9,000    20+           12          Full document coverage
```

### Implementation

```typescript
// ─── Duration Calculator ────────────────────────────────────────────────────

interface DurationConfig {
  targetDuration: '5min' | '15min' | '30min' | '60min';
  wordsPerMinute: number;        // Default: 150 for conversational pace
  introOutroSeconds: number;     // Default: 60 (30s intro + 30s outro)
}

function calculateBudget(config: DurationConfig): {
  totalWords: number;
  contentWords: number;
  keyPointTarget: number;
  segmentCount: number;
  wordsPerSegment: number;
} {
  const durationSeconds: Record<string, number> = {
    '5min': 300,
    '15min': 900,
    '30min': 1800,
    '60min': 3600,
  };

  const totalSeconds = durationSeconds[config.targetDuration] || 900;
  const contentSeconds = totalSeconds - config.introOutroSeconds;
  const contentWords = Math.round((contentSeconds / 60) * config.wordsPerMinute);
  const totalWords = Math.round((totalSeconds / 60) * config.wordsPerMinute);

  // Heuristic: ~300 words per key point discussion
  const keyPointTarget = Math.round(contentWords / 300);

  // Heuristic: ~3-5 minutes per segment
  const segmentCount = Math.max(3, Math.round(contentSeconds / 180));
  const wordsPerSegment = Math.round(contentWords / segmentCount);

  return { totalWords, contentWords, keyPointTarget, segmentCount, wordsPerSegment };
}

// Usage:
// const budget = calculateBudget({
//   targetDuration: '30min',
//   wordsPerMinute: 150,
//   introOutroSeconds: 60,
// });
// => { totalWords: 4500, contentWords: 4350, keyPointTarget: 14, segmentCount: 8, wordsPerSegment: 543 }
```

### Enforcement During Generation

```typescript
function enforceWordBudget(segments: ScriptSegment[], maxWords: number): ScriptSegment[] {
  let totalWords = 0;

  return segments.filter(seg => {
    const segWords = seg.text.split(/\s+/).length;
    if (totalWords + segWords > maxWords) {
      return false; // Drop segments that exceed budget
    }
    totalWords += segWords;
    return true;
  });
}
```

---

## Agent System Prompt Builders

```typescript
// ─── System Prompt Builders ─────────────────────────────────────────────────

function buildHostAgentSystem(host: Speaker, format: PodcastFormat): string {
  return `You are ${host.name}, a podcast host.

VOICE: ${host.voiceProfile.tone} tone, ${host.voiceProfile.pace} pace, ${host.voiceProfile.style} style.

YOUR ROLE:
- Drive the conversation with clear, engaging questions
- Create smooth transitions between topics
- React naturally (brief reactions, not monologues)
- Keep turns to 1-2 sentences
- Reference listeners: "Our listeners might wonder..."

FORMAT: ${format}
${format === 'panel' ? '- Ensure balanced airtime between all guests' : ''}
${format === 'debate' ? '- Play fair moderator, challenge both sides' : ''}

ANTI-PATTERNS TO AVOID:
- "Great question!" (never say this)
- Double-barrel questions (one question at a time)
- Long introductions before asking the actual question
- Answering your own question`;
}

function buildGuestAgentSystem(guest: Speaker, format: PodcastFormat): string {
  return `You are ${guest.name}, a podcast guest expert.

EXPERTISE: ${guest.expertise || 'General domain expert'}
VOICE: ${guest.voiceProfile.tone} tone, ${guest.voiceProfile.pace} pace, ${guest.voiceProfile.style} style.

YOUR ROLE:
- Provide domain expertise grounded in source documents
- Use concrete examples and analogies
- Keep responses to 3-5 sentences per turn
- Cite specifics: "The data shows..." / "According to..."

FAITHFULNESS RULES:
- EVERY factual claim must be traceable to your source material
- If unsure, hedge: "From what I've seen..." / "The evidence suggests..."
- If the source doesn't cover it, say so: "That's beyond what this research covers"
- NEVER invent statistics, quotes, or findings

${format === 'debate' ? '- You may disagree with other guests -- support your position with evidence' : ''}`;
}

function buildWriterAgentSystem(format: PodcastFormat): string {
  return `You are a podcast WRITER/PRODUCER.

YOUR JOB: Take raw Host-Guest dialogue and produce polished, natural-sounding script.

RULES:
1. Interleave speakers naturally -- no long monologues (max 4 sentences per turn)
2. Add delivery directions in parentheses: (enthusiastically), (pause), (thoughtfully)
3. Insert natural reactions: "Right.", "Exactly.", "Hmm.", "That's a key point."
4. Vary reactions throughout -- never repeat the same reaction twice in a row
5. Include thinking cues: "So what you're saying is...", "Let me make sure I understand..."
6. Add bridges: "And that connects to...", "Which brings up..."

FORMAT: ${format}
${format === 'panel' ? '- Balance airtime between guests; host mediates' : ''}
${format === 'debate' ? '- Let disagreements breathe; host mediates; maintain productive tension' : ''}
${format === 'solo-narration' ? '- Use rhetorical questions and storytelling rhythm' : ''}

ANTI-PATTERNS:
- Synthetic enthusiasm (don't force excitement)
- Agreement loops (build in pushback and questions)
- Template phrases (vary language throughout)
- Monotonous pacing (mix quick exchanges with deeper explorations)`;
}
```

---

## Intro and Outro Generation

```typescript
// ─── Intro/Outro Generators ─────────────────────────────────────────────────

async function generateIntroSegments(
  outline: PodcastOutline,
  speakers: Speaker[],
  format: PodcastFormat,
  client: Anthropic
): Promise<ScriptSegment[]> {
  const host = speakers.find(s => s.role === 'host' || s.role === 'narrator')!;

  const response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 1024,
    messages: [{
      role: 'user',
      content: `Write the opening 30 seconds of a ${format} podcast episode.

TITLE: ${outline.title}
HOOK: ${outline.hook}
HOST: ${host.name}
GUESTS: ${speakers.filter(s => s.role === 'guest').map(s => `${s.name} (${s.expertise})`).join(', ') || 'N/A'}

The intro should:
1. Start with the hook (grab attention immediately)
2. Briefly introduce the topic
3. Introduce guests (if any)
4. Tease what listeners will learn

Keep it under 100 words total. Natural, not scripted-sounding.

Return JSON array of ScriptSegment objects.
Return ONLY valid JSON.`,
    }],
  });

  const text = (response.content[0] as { type: string; text: string }).text;
  return JSON.parse(text.replace(/^```json\n?/, '').replace(/\n?```$/, ''));
}

async function generateOutroSegments(
  outline: PodcastOutline,
  speakers: Speaker[],
  format: PodcastFormat,
  client: Anthropic
): Promise<ScriptSegment[]> {
  const host = speakers.find(s => s.role === 'host' || s.role === 'narrator')!;

  const response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 1024,
    messages: [{
      role: 'user',
      content: `Write the closing 30 seconds of a ${format} podcast episode.

TITLE: ${outline.title}
CLOSING THOUGHT: ${outline.closingThought}
HOST: ${host.name}

The outro should:
1. Summarize the single most important takeaway
2. Include the closing thought
3. Thank guests (if any)
4. End with a forward-looking statement or call to action

Keep it under 80 words. Leave listeners thinking, not checking out.

Return JSON array of ScriptSegment objects.
Return ONLY valid JSON.`,
    }],
  });

  const text = (response.content[0] as { type: string; text: string }).text;
  return JSON.parse(text.replace(/^```json\n?/, '').replace(/\n?```$/, ''));
}
```

---

## Full Pipeline Orchestrator

```typescript
// ─── Full Pipeline ──────────────────────────────────────────────────────────

interface PipelineConfig {
  inputPath: string;             // Path to document (PDF, TXT, MD, HTML)
  duration: '5min' | '15min' | '30min' | '60min';
  format: PodcastFormat;
  speakers?: Speaker[];          // Custom speakers (optional, uses defaults)
  aiProvider: 'claude' | 'gemini';
  outputPath?: string;           // Where to write the JSON script
}

async function generatePodcastScript(config: PipelineConfig): Promise<PodcastScript> {
  const client = new Anthropic();

  // Step 1: Parse document
  console.log('Step 1/6: Parsing document...');
  const document = await parseDocument(config.inputPath);
  console.log(`  Parsed: ${document.title} (${document.metadata.wordCount} words)`);

  // Step 2: Chunk semantically
  console.log('Step 2/6: Chunking document...');
  const chunks = semanticChunk(document);
  console.log(`  Created ${chunks.length} semantic chunks`);

  // Step 3: Extract key points
  const budget = calculateBudget({
    targetDuration: config.duration,
    wordsPerMinute: 150,
    introOutroSeconds: 60,
  });
  console.log(`Step 3/6: Extracting ${budget.keyPointTarget} key points...`);
  const keyPoints = await extractKeyPoints(chunks, budget.keyPointTarget, client);
  console.log(`  Extracted ${keyPoints.length} key points`);

  // Step 4: Generate outline
  console.log('Step 4/6: Generating outline...');
  const outline = await generateOutline(keyPoints, config.duration, config.format, client);
  console.log(`  Outline: ${outline.segments.length} segments`);

  // Step 5: Multi-agent script generation (per-segment)
  console.log('Step 5/6: Generating script (multi-agent, per-segment)...');
  const speakers = config.speakers || getDefaultSpeakers(config.format);
  const contentTone = selectTone(keyPoints, document.title);
  const adjustedSpeakers = adjustVoiceProfiles(speakers, contentTone);

  const segments = await generateScript(
    outline, chunks, keyPoints, config.format, adjustedSpeakers, client
  );
  console.log(`  Generated ${segments.length} script segments`);

  // Step 6: Faithfulness verification
  console.log('Step 6/6: Verifying faithfulness...');
  const report = await verifyFaithfulness(segments, chunks, client);
  console.log(`  Faithfulness score: ${(report.overallScore * 100).toFixed(1)}%`);

  if (report.flaggedSegments.length > 0) {
    console.warn(`  WARNING: ${report.flaggedSegments.length} segments flagged for low faithfulness`);
  }

  // Assemble final script
  const wordCount = segments.reduce((sum, s) => sum + s.text.split(/\s+/).length, 0);
  const estimatedDuration = Math.round((wordCount / 150) * 60);

  const script: PodcastScript = {
    title: outline.title,
    duration: config.duration,
    speakers: adjustedSpeakers,
    segments,
    metadata: {
      sourceDocuments: [config.inputPath],
      generatedAt: new Date().toISOString(),
      wordCount,
      estimatedDuration,
      format: config.format,
      faithfulnessScore: report.overallScore,
      keyTopics: keyPoints.slice(0, 5).map(kp => kp.point),
    },
  };

  // Write output
  if (config.outputPath) {
    const { promises: fs } = await import('fs');
    await fs.writeFile(config.outputPath, JSON.stringify(script, null, 2), 'utf-8');
    console.log(`\nScript saved to: ${config.outputPath}`);
  }

  console.log(`\nDone! ${wordCount} words, ~${Math.round(estimatedDuration / 60)} min`);
  console.log(`Faithfulness: ${(report.overallScore * 100).toFixed(1)}%`);

  return script;
}

// ─── Default Speaker Configurations ─────────────────────────────────────────

function getDefaultSpeakers(format: PodcastFormat): Speaker[] {
  switch (format) {
    case 'two-speaker':
      return createTwoSpeakerConfig();
    case 'panel':
      return createPanelConfig();
    case 'solo-narration':
      return createSoloConfig();
    case 'debate':
      return createDebateConfig();
    default:
      return createTwoSpeakerConfig();
  }
}
```

---

## Integration Points

### Input Sources

| Source | Parser | Notes |
|---|---|---|
| Raw text / Markdown | Built-in `parseText()` | Preserves heading structure |
| PDF | `pdf-parse` npm package | Extracts text, page count |
| HTML / URL | `cheerio` + fetch | Strips nav, scripts, styles |
| YouTube transcript | `creative-multimedia/transcription-pipeline-selector.md` | Use Deepgram or Whisper on downloaded audio |
| DOCX | `mammoth` npm package | Add parser similar to PDF |

### Output Targets

| Target | Format | Notes |
|---|---|---|
| TTS pipeline | Structured JSON (`PodcastScript`) | Pass segments with speaker IDs to TTS |
| Human review | Formatted text with directions | Export as readable script document |
| Audio production | SRT + script | For DAW or automated audio assembly |
| Web player | JSON + audio chunks | Segment-level playback control |

### Related Skills

- `creative-multimedia/transcription-pipeline-selector.md` -- For audio input (YouTube, recorded audio)
- `creative-multimedia/content-repurposing-pipeline.md` -- For repurposing generated podcast into clips, quote cards, social posts
- `creative-multimedia/ffmpeg-command-generator.md` -- For audio processing and assembly
- `creative-multimedia/audio-enhancement-pipeline.md` -- For post-processing TTS output

### TTS Output Bridge

```typescript
// Convert PodcastScript to TTS-ready format
interface TTSRequest {
  text: string;
  voiceId: string;
  speed: number;          // 0.5 to 2.0
  outputPath: string;
}

function scriptToTTSRequests(
  script: PodcastScript,
  voiceMap: Record<string, string>, // speaker ID -> TTS voice ID
  outputDir: string
): TTSRequest[] {
  return script.segments.map((seg, i) => ({
    text: seg.text,
    voiceId: voiceMap[seg.speaker] || 'default',
    speed: seg.direction?.includes('slow') ? 0.9
      : seg.direction?.includes('fast') ? 1.1
      : 1.0,
    outputPath: `${outputDir}/segment_${String(i).padStart(3, '0')}_${seg.speaker}.mp3`,
  }));
}

// After TTS generation, concatenate with FFmpeg:
// ffmpeg -f concat -safe 0 -i segments.txt -c:a aac -b:a 192k podcast.m4a
```

---

## Dependencies

```json
{
  "dependencies": {
    "@anthropic-ai/sdk": "^0.39.0",
    "@google/generative-ai": "^0.21.0",
    "pdf-parse": "^1.1.1",
    "cheerio": "^1.0.0"
  }
}
```

```bash
npm install @anthropic-ai/sdk @google/generative-ai pdf-parse cheerio
```

---

## Usage Example

```typescript
// ─── Quick Start ────────────────────────────────────────────────────────────

import { generatePodcastScript } from './podcast-script-generation';

// Generate a 15-minute two-speaker podcast from a research paper
const script = await generatePodcastScript({
  inputPath: './papers/hallucination-research.pdf',
  duration: '15min',
  format: 'two-speaker',
  aiProvider: 'claude',
  outputPath: './output/podcast-script.json',
});

console.log(`Generated: ${script.title}`);
console.log(`Duration: ~${Math.round(script.metadata.estimatedDuration / 60)} min`);
console.log(`Faithfulness: ${(script.metadata.faithfulnessScore * 100).toFixed(1)}%`);
console.log(`Segments: ${script.segments.length}`);

// ─── With Custom Speakers ───────────────────────────────────────────────────

const customScript = await generatePodcastScript({
  inputPath: './docs/quarterly-report.pdf',
  duration: '30min',
  format: 'panel',
  aiProvider: 'claude',
  speakers: [
    {
      id: 'host',
      name: 'Thierry',
      role: 'host',
      voiceProfile: { tone: 'warm', pace: 'moderate', style: 'conversational' },
    },
    {
      id: 'analyst',
      name: 'Financial Analyst',
      role: 'guest',
      voiceProfile: { tone: 'authoritative', pace: 'moderate', style: 'formal' },
      expertise: 'Financial data and market trends',
    },
    {
      id: 'strategist',
      name: 'Strategy Director',
      role: 'guest',
      voiceProfile: { tone: 'energetic', pace: 'fast', style: 'conversational' },
      expertise: 'Business strategy and growth opportunities',
    },
  ],
  outputPath: './output/quarterly-podcast.json',
});
```

---

## Common Pitfalls

1. **Generating the full script in one prompt** -- Faithfulness degrades in long output. Always generate per-segment with verification.
2. **Skipping faithfulness verification** -- Without verification, 20-40% of claims in long scripts are fabricated. Always verify.
3. **Fixed-size chunking** -- Splitting documents at 500-character boundaries splits sentences and loses context. Use semantic chunking at paragraph boundaries.
4. **Single tone for all content** -- A peppy delivery for a paper about disease mortality is tone-deaf. Match tone to content.
5. **Letting guests monologue** -- Max 4 sentences per turn. Real conversations have short turns with natural back-and-forth.
6. **No source references in segments** -- Without `sourceReference` on each segment, you cannot trace claims back to verify them.
7. **Using the same reactions repeatedly** -- "Great question!" five times in one episode sounds robotic. Vary reactions.

---

## Research Citations

