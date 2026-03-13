---
name: podcast-quality-evaluation
category: creative-multimedia
version: 1.0.0
contributed: 2026-03-10
contributor: dominion-flow-research
last_updated: 2026-03-10
tags: [podcast, evaluation, quality, metrics, tts, audio-quality, content-verification]
difficulty: medium
---

# Podcast Quality Evaluation
## Description

Evaluate AI-generated podcast audio across three dimensions: text quality, speech quality, and audio quality. This skill provides automated scoring functions, human evaluation rubrics, and pass/fail quality gates for podcast production pipelines. Built on research from PodEval, PodBench, and prosody evaluation literature.

## When to Use

- Building an AI podcast generation pipeline and need quality checks
- Evaluating TTS output before publishing (Google Cloud TTS, Anthropic voice, ElevenLabs, etc.)
- Comparing different TTS engines or voice models for podcast use
- Setting up CI/CD quality gates for automated podcast production
- Auditing existing podcast audio for production quality issues
- Training or fine-tuning voice models and need objective metrics

---

## 1. Three-Dimensional Evaluation Framework

PodEval establishes that podcast quality cannot be captured by a single metric.
Three orthogonal dimensions must be measured independently.

```
┌─────────────────────────────────────────────────────────────┐
│                  PODCAST QUALITY EVALUATION                  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ TEXT QUALITY  │  │SPEECH QUALITY│  │ AUDIO QUALITY│      │
│  │              │  │              │  │              │      │
│  │ • Factual    │  │ • Naturalness│  │ • SNR        │      │
│  │   accuracy   │  │ • Speaker    │  │ • Loudness   │      │
│  │ • Source     │  │   similarity │  │ • Dynamic    │      │
│  │   coverage   │  │ • Prosody    │  │   range      │      │
│  │ • Halluc.    │  │   score      │  │ • Clipping   │      │
│  │   rate       │  │ • Emotion    │  │ • Artifacts  │      │
│  │              │  │   match      │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         v                 v                 v               │
│  ┌─────────────────────────────────────────────────┐       │
│  │           COMPOSITE QUALITY SCORE                │       │
│  │     (weighted by use-case: publish, draft, etc.) │       │
│  └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Dimension Detail

| Dimension | What It Measures | Key Metrics | Tools |
|-----------|-----------------|-------------|-------|
| **Text Quality** | Content accuracy, faithfulness to source material, hallucination avoidance | Factual accuracy score, source coverage %, hallucination rate, topical coherence | Embedding similarity, LLM-as-judge (Claude), ROUGE-L |
| **Speech Quality** | Naturalness of synthesized speech, speaker consistency across segments | MOS (Mean Opinion Score), speaker similarity (cosine), prosody score, emotion alignment | Resemblyzer, librosa, FFmpeg pitch analysis |
| **Audio Quality** | Production quality, mixing, mastering standards | SNR (dB), loudness (LUFS), dynamic range, clipping detection, silence distribution | FFmpeg loudnorm, ebur128, silencedetect filters |

### Weighting by Use Case

Different podcast types demand different weight distributions:

```typescript
interface QualityWeights {
  text: number;    // 0-1
  speech: number;  // 0-1
  audio: number;   // 0-1
}

const WEIGHTS_BY_USE_CASE: Record<string, QualityWeights> = {
  // Educational/news — accuracy is paramount
  'educational':  { text: 0.50, speech: 0.25, audio: 0.25 },

  // Entertainment/storytelling — speech quality matters most
  'entertainment': { text: 0.25, speech: 0.45, audio: 0.30 },

  // Professional/corporate — production quality is key
  'corporate':    { text: 0.35, speech: 0.25, audio: 0.40 },

  // Ministry/sermon — balance of content and delivery
  'ministry':     { text: 0.40, speech: 0.35, audio: 0.25 },

  // Default balanced
  'default':      { text: 0.34, speech: 0.33, audio: 0.33 },
};
```

---

## 2. PodBench Evaluation Methodology

PodBench defines four evaluation axes for AI-generated podcast scripts and audio.
Each axis uses a combination of automated metrics and LLM-based assessment.

### 2.1 Content Fidelity

Does the generated podcast script accurately represent the source material?

**Automated checks:**
- Embedding similarity between source chunks and script segments
- Named entity preservation (all key entities from source appear in script)
- Claim verification (extract claims from script, verify against source)

**LLM-based assessment (using Claude):**

```typescript
const CONTENT_FIDELITY_PROMPT = `
You are a podcast quality evaluator. Compare the generated podcast script
against the source documents.

Source Documents:
{sources}

Generated Script:
{script}

Evaluate on these criteria (score 1-5 each):
1. COVERAGE: Does the script cover the key points from the sources?
2. ACCURACY: Are all claims in the script supported by the sources?
3. HALLUCINATION: Does the script introduce unsupported claims? (5 = no hallucinations)
4. ATTRIBUTION: When the script references facts, could a listener trace them to sources?

Return JSON:
{
  "coverage": { "score": number, "missing_topics": string[] },
  "accuracy": { "score": number, "unsupported_claims": string[] },
  "hallucination": { "score": number, "fabricated_claims": string[] },
  "attribution": { "score": number, "notes": string },
  "overall_fidelity": number
}
`;
```

### 2.2 Structural Compliance

Does the output follow the requested podcast format?

| Format | Required Structure |
|--------|--------------------|
| **Interview** | Host intro, guest introduction, Q&A segments, closing |
| **Deep-dive** | Topic intro, background, main analysis, implications, summary |
| **Debate** | Topic statement, position A, position B, rebuttals, synthesis |
| **News roundup** | Headlines, story segments (3-5), transitions, closing |
| **Sermon recap** | Scripture reading, context, main points, application, prayer |

**Structural compliance checker:**

```typescript
interface StructuralCheck {
  format: string;
  requiredSections: string[];
  foundSections: string[];
  missingSections: string[];
  score: number; // 0-1
}

function checkStructuralCompliance(
  script: string,
  format: string,
  requiredSections: string[]
): StructuralCheck {
  const foundSections: string[] = [];
  const missingSections: string[] = [];

  for (const section of requiredSections) {
    // Use fuzzy matching — section might not be labeled exactly
    const sectionPatterns = getSectionPatterns(section);
    const found = sectionPatterns.some(pattern =>
      new RegExp(pattern, 'i').test(script)
    );

    if (found) {
      foundSections.push(section);
    } else {
      missingSections.push(section);
    }
  }

  return {
    format,
    requiredSections,
    foundSections,
    missingSections,
    score: foundSections.length / requiredSections.length,
  };
}

function getSectionPatterns(section: string): string[] {
  const patternMap: Record<string, string[]> = {
    'host_intro': [
      'welcome to', 'hello and welcome', 'hey everyone',
      'good (morning|afternoon|evening)'
    ],
    'guest_introduction': [
      'joining (us|me) today', 'our guest',
      'please welcome', 'i\'m here with'
    ],
    'closing': [
      'thank you for (listening|tuning in)', 'until next time',
      'that\'s (all|it) for today', 'wrap(ping)? up'
    ],
    'scripture_reading': [
      'let\'s (read|turn to|open)', 'the (scripture|passage|verse|text)',
      'reads from'
    ],
    'application': [
      'how (does|can) this apply', 'practical(ly)?',
      'in our (daily )?lives', 'take(away)?'
    ],
  };
  return patternMap[section] || [section.replace(/_/g, '[\\s_-]')];
}
```

### 2.3 Speaker Consistency

Each speaker should maintain a consistent voice, personality, and perspective throughout.

**What to check:**
- **Voice persona** — Does Speaker A stay in character? (e.g., "the skeptic" shouldn't suddenly agree without reason)
- **Language register** — Consistent formality level per speaker
- **Knowledge level** — A "beginner-friendly host" shouldn't suddenly use advanced jargon
- **Catchphrases/patterns** — Recurring verbal patterns feel natural and consistent

**Automated detection:**

```typescript
interface SpeakerSegment {
  speaker: string;
  text: string;
  startTime?: number;
  endTime?: number;
}

interface SpeakerConsistencyReport {
  speakers: Map<string, {
    totalWords: number;
    avgSentenceLength: number;
    vocabularyLevel: 'simple' | 'moderate' | 'advanced';
    formalityScore: number;     // 0 (casual) to 1 (formal)
    questionRatio: number;      // % of sentences that are questions
    consistencyScore: number;   // 0-1 across all segments
  }>;
  overallConsistency: number;
}

function analyzeSpeakerConsistency(
  segments: SpeakerSegment[]
): SpeakerConsistencyReport {
  const speakerTexts = new Map<string, string[]>();

  // Group segments by speaker
  for (const seg of segments) {
    const existing = speakerTexts.get(seg.speaker) || [];
    existing.push(seg.text);
    speakerTexts.set(seg.speaker, existing);
  }

  const speakers = new Map();

  for (const [speaker, texts] of speakerTexts) {
    const allText = texts.join(' ');
    const words = allText.split(/\s+/);
    const sentences = allText.split(/[.!?]+/).filter(Boolean);
    const questions = sentences.filter(s =>
      s.trim().endsWith('?') || s.includes('?')
    );

    // Calculate per-segment metrics for consistency measurement
    const segmentMetrics = texts.map(text => ({
      sentenceLength: text.split(/[.!?]+/).filter(Boolean)
        .reduce((sum, s) => sum + s.split(/\s+/).length, 0)
        / Math.max(1, text.split(/[.!?]+/).filter(Boolean).length),
      questionRatio: (text.match(/\?/g) || []).length
        / Math.max(1, text.split(/[.!?]+/).filter(Boolean).length),
    }));

    // Consistency = inverse of coefficient of variation across segments
    const avgLengths = segmentMetrics.map(m => m.sentenceLength);
    const mean = avgLengths.reduce((a, b) => a + b, 0) / avgLengths.length;
    const stdDev = Math.sqrt(
      avgLengths.reduce((sum, v) => sum + (v - mean) ** 2, 0) / avgLengths.length
    );
    const cv = mean > 0 ? stdDev / mean : 0;
    const consistencyScore = Math.max(0, 1 - cv);

    speakers.set(speaker, {
      totalWords: words.length,
      avgSentenceLength: words.length / Math.max(1, sentences.length),
      vocabularyLevel: classifyVocabulary(allText),
      formalityScore: measureFormality(allText),
      questionRatio: questions.length / Math.max(1, sentences.length),
      consistencyScore,
    });
  }

  const scores = Array.from(speakers.values()).map(
    (s: any) => s.consistencyScore
  );
  const overallConsistency = scores.reduce(
    (a: number, b: number) => a + b, 0
  ) / scores.length;

  return { speakers, overallConsistency };
}

function classifyVocabulary(text: string): 'simple' | 'moderate' | 'advanced' {
  const words = text.toLowerCase().split(/\s+/);
  const avgWordLength = words.reduce((sum, w) => sum + w.length, 0) / words.length;
  if (avgWordLength < 4.5) return 'simple';
  if (avgWordLength < 5.5) return 'moderate';
  return 'advanced';
}

function measureFormality(text: string): number {
  const informalMarkers =
    /\b(yeah|gonna|wanna|kinda|sorta|like|right\?|you know|stuff|things|cool|awesome|hey)\b/gi;
  const formalMarkers =
    /\b(however|furthermore|consequently|nevertheless|regarding|therefore|indeed|certainly|substantial|significant)\b/gi;
  const informal = (text.match(informalMarkers) || []).length;
  const formal = (text.match(formalMarkers) || []).length;
  const total = informal + formal;
  if (total === 0) return 0.5;
  return formal / total;
}
```

### 2.4 Quantitative Constraints

Hard requirements that can be measured precisely:

| Constraint | Target | Tolerance | How to Measure |
|------------|--------|-----------|----------------|
| Duration | Varies (5-60 min) | +/-10% | FFmpeg duration probe |
| Speaker balance | 50/50 (2 speakers) | 40-60% range | Word count or audio time per speaker |
| Segment count | Per format | +/-1 segment | Script section counting |
| Transition presence | Between every segment | 0 missing | Pattern matching for transition phrases |
| Intro length | 30-90 seconds | +/-15 seconds | Timestamp analysis |
| Outro length | 20-60 seconds | +/-10 seconds | Timestamp analysis |

---

## 3. Automated Quality Checks (TypeScript)

### 3.1 Faithfulness Scorer

Compare the generated script against source documents using embedding similarity.
Uses Anthropic Claude for verification.

```typescript
import Anthropic from '@anthropic-ai/sdk';
import { readFileSync } from 'fs';

interface FaithfulnessReport {
  overallScore: number;         // 0-1
  claimCount: number;
  verifiedClaims: number;
  unverifiedClaims: string[];
  hallucinations: string[];
  sourceCoverage: number;       // 0-1 — what % of source key points appear
}

async function scoreFaithfulness(
  script: string,
  sources: string[],
  apiKey: string
): Promise<FaithfulnessReport> {
  const client = new Anthropic({ apiKey });

  // Step 1: Extract claims from the script
  const claimExtraction = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 4096,
    messages: [{
      role: 'user',
      content: `Extract all factual claims from this podcast script.
Return as JSON array of strings. Only include verifiable factual statements,
not opinions or conversational filler.

Script:
${script}`
    }],
  });

  const claims: string[] = JSON.parse(
    extractJsonFromResponse(claimExtraction.content[0])
  );

  // Step 2: Verify each claim against sources
  const sourceText = sources.join('\n\n---SOURCE BOUNDARY---\n\n');

  const verification = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 4096,
    messages: [{
      role: 'user',
      content: `Verify each claim against the source documents.

Source Documents:
${sourceText}

Claims to verify:
${JSON.stringify(claims, null, 2)}

For each claim, respond with JSON:
{
  "results": [
    {
      "claim": "...",
      "verified": true/false,
      "hallucination": true/false,
      "note": "..."
    }
  ],
  "source_key_points_missed": ["..."]
}`
    }],
  });

  const results = JSON.parse(
    extractJsonFromResponse(verification.content[0])
  );

  const verified = results.results.filter((r: any) => r.verified);
  const hallucinations = results.results
    .filter((r: any) => r.hallucination)
    .map((r: any) => r.claim);
  const unverified = results.results
    .filter((r: any) => !r.verified && !r.hallucination)
    .map((r: any) => r.claim);

  // Source coverage: key points mentioned vs missed
  const missedPoints = results.source_key_points_missed || [];
  const totalKeyPoints = verified.length + missedPoints.length;
  const sourceCoverage = totalKeyPoints > 0
    ? verified.length / totalKeyPoints
    : 1;

  const overallScore = claims.length > 0
    ? (verified.length / claims.length)
      * (1 - hallucinations.length / claims.length)
    : 0;

  return {
    overallScore: Math.max(0, Math.min(1, overallScore)),
    claimCount: claims.length,
    verifiedClaims: verified.length,
    unverifiedClaims: unverified,
    hallucinations,
    sourceCoverage,
  };
}

function extractJsonFromResponse(content: any): string {
  const text = content.type === 'text' ? content.text : String(content);
  const jsonMatch = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (jsonMatch) return jsonMatch[1].trim();
  const firstBrace = text.indexOf('{');
  const lastBrace = text.lastIndexOf('}');
  if (firstBrace !== -1 && lastBrace !== -1) {
    return text.substring(firstBrace, lastBrace + 1);
  }
  return text;
}
```

### 3.2 Audio Quality Analyzer

Use FFmpeg to measure SNR, loudness, clipping, and silence distribution.

**Note:** These examples use `execFileSync` from `child_process` with argument
arrays for safe subprocess execution. In production, use a wrapper like
`execFileNoThrow` for proper error handling.

```typescript
import { execFileSync } from 'child_process';

interface AudioQualityReport {
  duration: number;               // seconds
  loudness: {
    integrated: number;           // LUFS
    range: number;                // LU
    truePeak: number;             // dBTP
    passesLoudnessTarget: boolean;
  };
  snr: {
    estimated: number;            // dB
    passesThreshold: boolean;
  };
  clipping: {
    detected: boolean;
    clippedSamples: number;
    percentClipped: number;
  };
  silence: {
    segments: SilenceSegment[];
    awkwardPauses: number;        // pauses > 3 seconds
    totalSilence: number;         // seconds
    silenceRatio: number;         // silence / total duration
  };
  overallPass: boolean;
}

interface SilenceSegment {
  start: number;
  end: number;
  duration: number;
}

async function analyzeAudioQuality(
  audioPath: string
): Promise<AudioQualityReport> {
  // --- Loudness (EBU R128) ---
  const loudnessRaw = execFileSync(
    'ffmpeg',
    ['-i', audioPath, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
    { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024, stdio: ['pipe', 'pipe', 'pipe'] }
  );

  const integrated = parseFloat(
    loudnessRaw.match(/I:\s+(-?[\d.]+)\s+LUFS/)?.[1] || '-99'
  );
  const range = parseFloat(
    loudnessRaw.match(/LRA:\s+([\d.]+)\s+LU/)?.[1] || '0'
  );
  const truePeak = parseFloat(
    loudnessRaw.match(/Peak:\s+(-?[\d.]+)\s+dBFS/)?.[1] || '0'
  );

  // Podcast target: -16 to -14 LUFS (Spotify/Apple standard)
  const passesLoudnessTarget = integrated >= -16 && integrated <= -14;

  // --- Duration ---
  const durationRaw = execFileSync(
    'ffprobe',
    ['-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', audioPath],
    { encoding: 'utf-8' }
  );
  const duration = parseFloat(durationRaw.trim());

  // --- SNR estimation ---
  const statsRaw = execFileSync(
    'ffmpeg',
    ['-i', audioPath, '-af', 'astats=metadata=1:reset=1', '-f', 'null', '-'],
    { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024, stdio: ['pipe', 'pipe', 'pipe'] }
  );

  const rmsLevelMatch = statsRaw.match(/RMS level dB:\s+(-?[\d.]+)/);
  const noiseFloorMatch = statsRaw.match(/Noise floor dB:\s+(-?[\d.]+)/);
  const rmsLevel = parseFloat(rmsLevelMatch?.[1] || '-30');
  const noiseFloor = parseFloat(noiseFloorMatch?.[1] || '-60');
  const estimatedSNR = Math.abs(noiseFloor) - Math.abs(rmsLevel);

  // --- Clipping detection ---
  const clipRaw = execFileSync(
    'ffmpeg',
    ['-i', audioPath, '-af', 'astats=metadata=1', '-f', 'null', '-'],
    { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024, stdio: ['pipe', 'pipe', 'pipe'] }
  );

  const clippedMatch = clipRaw.match(/Number of samples clipped:\s+(\d+)/);
  const totalMatch = clipRaw.match(/Number of samples:\s+(\d+)/);
  const clippedSamples = parseInt(clippedMatch?.[1] || '0', 10);
  const totalSamples = parseInt(totalMatch?.[1] || '1', 10);

  // --- Silence detection ---
  const silenceRaw = execFileSync(
    'ffmpeg',
    ['-i', audioPath, '-af', 'silencedetect=noise=-40dB:d=0.5', '-f', 'null', '-'],
    { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024, stdio: ['pipe', 'pipe', 'pipe'] }
  );

  const silenceSegments: SilenceSegment[] = [];
  const silenceStartRegex = /silence_start:\s+([\d.]+)/g;
  const silenceEndRegex =
    /silence_end:\s+([\d.]+)\s*\|\s*silence_duration:\s+([\d.]+)/g;

  let startMatch: RegExpExecArray | null;
  const starts: number[] = [];
  while ((startMatch = silenceStartRegex.exec(silenceRaw)) !== null) {
    starts.push(parseFloat(startMatch[1]));
  }

  let endMatch: RegExpExecArray | null;
  let idx = 0;
  while ((endMatch = silenceEndRegex.exec(silenceRaw)) !== null) {
    silenceSegments.push({
      start: starts[idx] || 0,
      end: parseFloat(endMatch[1]),
      duration: parseFloat(endMatch[2]),
    });
    idx++;
  }

  const awkwardPauses = silenceSegments.filter(s => s.duration > 3).length;
  const totalSilence = silenceSegments.reduce(
    (sum, s) => sum + s.duration, 0
  );

  // --- Composite result ---
  const clippingDetected = clippedSamples > 0;
  const overallPass =
    passesLoudnessTarget &&
    estimatedSNR >= 30 &&
    !clippingDetected &&
    awkwardPauses === 0;

  return {
    duration,
    loudness: { integrated, range, truePeak, passesLoudnessTarget },
    snr: { estimated: estimatedSNR, passesThreshold: estimatedSNR >= 30 },
    clipping: {
      detected: clippingDetected,
      clippedSamples,
      percentClipped: (clippedSamples / totalSamples) * 100,
    },
    silence: {
      segments: silenceSegments,
      awkwardPauses,
      totalSilence,
      silenceRatio: totalSilence / duration,
    },
    overallPass,
  };
}
```

### 3.3 Duration Accuracy

```typescript
interface DurationReport {
  targetSeconds: number;
  actualSeconds: number;
  deviationPercent: number;
  passes: boolean;
}

async function checkDurationAccuracy(
  audioPath: string,
  targetMinutes: number,
  tolerancePercent: number = 10
): Promise<DurationReport> {
  const durationRaw = execFileSync(
    'ffprobe',
    ['-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', audioPath],
    { encoding: 'utf-8' }
  );

  const actualSeconds = parseFloat(durationRaw.trim());
  const targetSeconds = targetMinutes * 60;
  const deviation = Math.abs(actualSeconds - targetSeconds);
  const deviationPercent = (deviation / targetSeconds) * 100;

  return {
    targetSeconds,
    actualSeconds,
    deviationPercent,
    passes: deviationPercent <= tolerancePercent,
  };
}
```

### 3.4 Speaker Balance

```typescript
interface SpeakerBalanceReport {
  speakers: Map<string, {
    wordCount: number;
    percentage: number;
    audioSeconds?: number;
  }>;
  balanced: boolean;             // all speakers within 40-60% for 2-speaker
  dominantSpeaker: string | null; // speaker with >70% airtime
}

function checkSpeakerBalance(
  segments: SpeakerSegment[],
  maxDominance: number = 0.70
): SpeakerBalanceReport {
  const speakerWords = new Map<string, number>();
  let totalWords = 0;

  for (const seg of segments) {
    const words = seg.text.split(/\s+/).filter(Boolean).length;
    speakerWords.set(
      seg.speaker,
      (speakerWords.get(seg.speaker) || 0) + words
    );
    totalWords += words;
  }

  const speakers = new Map<string, {
    wordCount: number;
    percentage: number;
  }>();
  let dominantSpeaker: string | null = null;

  for (const [speaker, words] of speakerWords) {
    const percentage = totalWords > 0 ? words / totalWords : 0;
    speakers.set(speaker, { wordCount: words, percentage });
    if (percentage > maxDominance) {
      dominantSpeaker = speaker;
    }
  }

  // For 2-speaker podcasts, balanced means 40-60% each
  const speakerCount = speakers.size;
  let balanced = true;

  if (speakerCount === 2) {
    for (const { percentage } of speakers.values()) {
      if (percentage < 0.40 || percentage > 0.60) {
        balanced = false;
        break;
      }
    }
  } else {
    // For N speakers, check no one exceeds maxDominance
    balanced = dominantSpeaker === null;
  }

  return { speakers, balanced, dominantSpeaker };
}
```

### 3.5 Silence Detection

Flag awkward pauses (>3 seconds) or completely missing pauses between segments.

```typescript
interface SilenceReport {
  awkwardPauses: SilenceSegment[];     // > 3 seconds
  missingPauses: number[];             // timestamps where pause expected but absent
  naturalPauses: number;               // 0.3-2.0 second pauses (healthy)
  totalSilenceRatio: number;
  assessment: 'good' | 'too-much-silence' | 'too-little-silence' | 'awkward-pauses';
}

function assessSilencePattern(
  silenceSegments: SilenceSegment[],
  totalDuration: number
): SilenceReport {
  const awkwardPauses = silenceSegments.filter(s => s.duration > 3.0);
  const naturalPauses = silenceSegments.filter(
    s => s.duration >= 0.3 && s.duration <= 2.0
  ).length;
  const totalSilence = silenceSegments.reduce(
    (sum, s) => sum + s.duration, 0
  );
  const totalSilenceRatio = totalSilence / totalDuration;

  // Healthy podcast: 15-25% silence (breathing room, natural pauses)
  let assessment: SilenceReport['assessment'];
  if (awkwardPauses.length > 0) {
    assessment = 'awkward-pauses';
  } else if (totalSilenceRatio > 0.30) {
    assessment = 'too-much-silence';
  } else if (totalSilenceRatio < 0.10) {
    assessment = 'too-little-silence';
  } else {
    assessment = 'good';
  }

  return {
    awkwardPauses,
    missingPauses: [],  // Requires segment boundary timestamps to detect
    naturalPauses,
    totalSilenceRatio,
    assessment,
  };
}
```

---

## 4. Prosody Evaluation

Based on "Toward Objective Prosody Evaluation in TTS" (arXiv 2511.02104).
Prosody — the rhythm, stress, and intonation of speech — is the primary differentiator
between robotic and natural-sounding TTS output.

### 4.1 What to Measure

| Feature | Natural Speech | Robotic TTS | How to Extract |
|---------|---------------|-------------|----------------|
| **Pitch variation** | 50-200 Hz range, contextual rises/falls | Flat or exaggerated | FFmpeg `astats` + Python librosa |
| **Speaking rate** | 120-180 WPM, varies by emphasis | Constant pace | Word count / duration per segment |
| **Pause distribution** | Natural clusters around clauses | Evenly spaced or absent | Silence detection |
| **Emphasis** | Key words stressed naturally | Uniform stress or wrong words | Pitch + energy peaks |
| **Sentence-final patterns** | Falling for statements, rising for questions | Monotone endings | Pitch contour analysis |

### 4.2 FFmpeg Pitch Extraction

```bash
# Extract pitch contour using FFmpeg + audio analysis

# Step 1: Convert to mono WAV for consistent analysis
ffmpeg -i podcast.mp3 -ac 1 -ar 16000 -f wav podcast_mono.wav

# Step 2: Extract volume envelope (proxy for emphasis)
ffmpeg -i podcast_mono.wav \
  -af "astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=rms_levels.txt" \
  -f null -

# Step 3: Detect pitch periods (fundamental frequency)
ffmpeg -i podcast_mono.wav \
  -af "aresample=16000,asetnsamples=n=400:p=0,showcqt=s=1920x1080" \
  -frames:v 1 pitch_analysis.png
```

### 4.3 Python Librosa Analysis (Reference)

For deeper prosody analysis, use Python librosa.
(Learning opportunity — Python is on Thierry's learning roadmap.)

```python
"""
Prosody analyzer for AI-generated podcast audio.
Uses librosa for acoustic feature extraction.

Measures:
- Pitch variation (F0 contour)
- Speaking rate estimation
- Energy distribution
- Pause patterns

Requires: pip install librosa numpy soundfile
"""

import librosa
import numpy as np
from dataclasses import dataclass
@dataclass
class ProsodyReport:
    """Results of prosody analysis."""
    pitch_mean: float           # Hz — average fundamental frequency
    pitch_std: float            # Hz — variation (higher = more expressive)
    pitch_range: float          # Hz — max - min
    speaking_rate: float        # estimated syllables per second
    energy_variation: float     # coefficient of variation of RMS energy
    pause_count: int            # number of detected pauses
    avg_pause_duration: float   # seconds
    monotone_score: float       # 0 (very monotone) to 1 (very expressive)
    naturalness_estimate: float # 0-1 composite score
def analyze_prosody(audio_path: str, sr: int = 22050) -> ProsodyReport:
    """
    Analyze prosody features of an audio file.

    Args:
        audio_path: Path to audio file (WAV, MP3, etc.)
        sr: Sample rate for analysis (default 22050 Hz)

    Returns:
        ProsodyReport with all measured features

    How it works (linear walkthrough):
        1. Load audio at target sample rate
        2. Extract pitch (F0) using pyin algorithm — robust for speech
        3. Compute RMS energy per frame — shows emphasis patterns
        4. Count onsets as proxy for syllable rate
        5. Detect silent frames for pause analysis
        6. Calculate monotone score from pitch coefficient of variation
        7. Combine into weighted naturalness estimate
    """
    # Load audio
    y, sr = librosa.load(audio_path, sr=sr)
    duration = librosa.get_duration(y=y, sr=sr)

    # --- Pitch (F0) extraction ---
    # pyin = probabilistic YIN algorithm, robust for speech
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y, fmin=50, fmax=500, sr=sr
    )

    # Filter to only voiced segments (where pitch is detectable)
    voiced_f0 = f0[~np.isnan(f0)]

    pitch_mean = float(np.mean(voiced_f0)) if len(voiced_f0) > 0 else 0
    pitch_std = float(np.std(voiced_f0)) if len(voiced_f0) > 0 else 0
    pitch_range = float(np.ptp(voiced_f0)) if len(voiced_f0) > 0 else 0

    # --- Energy (RMS) ---
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
    energy_mean = float(np.mean(rms))
    energy_std = float(np.std(rms))
    energy_variation = energy_std / energy_mean if energy_mean > 0 else 0

    # --- Speaking rate estimation ---
    # Onset detection as proxy for syllable rate
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
    speaking_rate = len(onsets) / duration if duration > 0 else 0

    # --- Pause detection ---
    # Frames where RMS is below threshold
    silence_threshold = 0.01  # adjust based on recording
    is_silent = rms[0] < silence_threshold
    pause_boundaries = np.diff(is_silent.astype(int))
    pause_starts = np.where(pause_boundaries == 1)[0]
    pause_ends = np.where(pause_boundaries == -1)[0]

    # Align starts and ends
    if len(pause_ends) > 0 and len(pause_starts) > 0:
        if pause_ends[0] < pause_starts[0]:
            pause_ends = pause_ends[1:]
        min_len = min(len(pause_starts), len(pause_ends))
        pause_starts = pause_starts[:min_len]
        pause_ends = pause_ends[:min_len]
        # Convert frames to seconds
        pause_durations = (pause_ends - pause_starts) * 512 / sr
        pause_count = len(pause_durations)
        avg_pause = float(np.mean(pause_durations)) if pause_count > 0 else 0
    else:
        pause_count = 0
        avg_pause = 0.0

    # --- Monotone score ---
    # Natural speech: pitch CV typically 0.15-0.35
    # Monotone TTS: pitch CV typically < 0.08
    pitch_cv = pitch_std / pitch_mean if pitch_mean > 0 else 0
    monotone_score = min(1.0, pitch_cv / 0.25)

    # --- Composite naturalness ---
    # Weighted combination of prosody features
    naturalness_estimate = (
        0.35 * monotone_score
        + 0.25 * min(1.0, energy_variation / 0.5)
        + 0.20 * (1.0 if 3.0 <= speaking_rate <= 6.0 else 0.5)
        + 0.20 * (1.0 if 0.3 <= avg_pause <= 1.5 else 0.5)
    )

    return ProsodyReport(
        pitch_mean=pitch_mean,
        pitch_std=pitch_std,
        pitch_range=pitch_range,
        speaking_rate=speaking_rate,
        energy_variation=energy_variation,
        pause_count=pause_count,
        avg_pause_duration=avg_pause,
        monotone_score=monotone_score,
        naturalness_estimate=min(1.0, naturalness_estimate),
    )
# --- Usage example ---
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python prosody_analyzer.py <audio_file>")
        sys.exit(1)

    report = analyze_prosody(sys.argv[1])
    print(f"Pitch: mean={report.pitch_mean:.1f}Hz, "
          f"std={report.pitch_std:.1f}Hz, "
          f"range={report.pitch_range:.1f}Hz")
    print(f"Speaking rate: {report.speaking_rate:.1f} syllables/sec")
    print(f"Energy variation: {report.energy_variation:.3f}")
    print(f"Pauses: {report.pause_count} detected, "
          f"avg {report.avg_pause_duration:.2f}s")
    print(f"Monotone score: {report.monotone_score:.2f} "
          f"(0=monotone, 1=expressive)")
    print(f"Naturalness estimate: {report.naturalness_estimate:.2f}")
```

### 4.4 Prosody Red Flags

Automated detection of common TTS prosody failures:

| Red Flag | Detection Method | Threshold |
|----------|-----------------|-----------|
| **Monotone delivery** | Pitch standard deviation | < 15 Hz = FAIL |
| **Unnatural emphasis** | Energy spikes on function words (the, a, is) | > 2x surrounding energy = FLAG |
| **Robotic pacing** | Constant inter-word duration | CV < 0.05 = FAIL |
| **Wrong question intonation** | Pitch doesn't rise at end of questions | < 10% pitch rise = FLAG |
| **Breathing artifacts** | Periodic noise at consistent intervals | Detectable pattern = FLAG |
| **Word boundary glitches** | Sudden pitch/energy discontinuities | > 100Hz jump between frames = FLAG |

---

## 5. Human Evaluation Rubric

When automated metrics pass but you need final human judgment.
Based on PodEval's subjective evaluation protocol with spammer detection.

### 5.1 Scoring Grid

| Criterion | 1 (Poor) | 2 (Below Average) | 3 (Acceptable) | 4 (Good) | 5 (Excellent) |
|-----------|----------|--------------------|-----------------|----------|----------------|
| **Naturalness** | Robotic, clearly AI-generated | Mostly robotic with rare natural moments | Mostly natural, occasional artifacts | Natural with very minor tells | Indistinguishable from human podcast |
| **Engagement** | Boring, monotone, would stop listening | Low engagement, attention wanders | Interesting but uneven pacing | Engaging, holds attention well | Compelling throughout, want to hear more |
| **Accuracy** | Multiple factual errors or fabrications | Several inaccuracies | Minor inaccuracies that don't mislead | Accurate with trivial nitpicks | Fully faithful to sources, well-researched |
| **Flow** | Disjointed, awkward transitions, no coherence | Choppy transitions, some logical gaps | Mostly smooth with a few rough spots | Natural flow with minor hitches | Seamless conversation, natural topic evolution |
| **Production** | Noticeable artifacts, volume issues, distortion | Some audio issues (pops, uneven volume) | Clean but basic production | Good production, professional feel | Broadcast-quality, indistinguishable from major podcasts |

### 5.2 Evaluation Protocol

To get reliable human evaluation results:

1. **Recruit 3-5 evaluators** with diverse listening habits
2. **Blind evaluation** — don't tell evaluators whether content is AI-generated
3. **Include calibration samples** — mix in 2-3 known human-recorded podcast clips
4. **Spammer detection** (from PodEval):
   - Flag evaluators who give the same score for all samples
   - Flag evaluators who complete evaluation in < 30% of audio duration
   - Flag evaluators whose scores are > 2 standard deviations from group mean
   - Remove flagged evaluators and recalculate
5. **Inter-rater reliability** — calculate Krippendorff's alpha (target: > 0.6)

### 5.3 Evaluation Form Template

```markdown
## Podcast Quality Evaluation

**Sample ID:** ___________
**Evaluator ID:** ___________
**Date:** ___________

Listen to the complete audio sample before scoring.

### Scores (circle one per row)

| Criterion     |  1  |  2  |  3  |  4  |  5  |
|---------------|-----|-----|-----|-----|-----|
| Naturalness   |  O  |  O  |  O  |  O  |  O  |
| Engagement    |  O  |  O  |  O  |  O  |  O  |
| Accuracy      |  O  |  O  |  O  |  O  |  O  |
| Flow          |  O  |  O  |  O  |  O  |  O  |
| Production    |  O  |  O  |  O  |  O  |  O  |

### Open-ended

1. What was the most noticeable quality issue (if any)?
   _________________________________________________

2. Did anything sound unnatural or AI-generated? What specifically?
   _________________________________________________

3. Would you subscribe to a podcast at this quality level? (Y/N)
   Why? ____________________________________________

**Time to complete evaluation:** _________ minutes
```

---

## 6. Quality Gates for Pipeline

Define pass/fail thresholds for automated CI/CD podcast production.

### 6.1 Gate Definitions

```typescript
interface QualityGate {
  name: string;
  check: (report: any) => boolean;
  severity: 'blocker' | 'warning';
  description: string;
}

const QUALITY_GATES: QualityGate[] = [
  // --- BLOCKERS (must pass to publish) ---
  {
    name: 'faithfulness',
    check: (r: FaithfulnessReport) => r.overallScore >= 0.85,
    severity: 'blocker',
    description:
      'Faithfulness score >= 0.85 (85% of claims verified against sources)',
  },
  {
    name: 'no-hallucinations',
    check: (r: FaithfulnessReport) => r.hallucinations.length === 0,
    severity: 'blocker',
    description: 'Zero hallucinated claims detected',
  },
  {
    name: 'audio-snr',
    check: (r: AudioQualityReport) => r.snr.estimated >= 30,
    severity: 'blocker',
    description: 'Signal-to-noise ratio >= 30 dB',
  },
  {
    name: 'loudness-target',
    check: (r: AudioQualityReport) =>
      r.loudness.integrated >= -16 && r.loudness.integrated <= -14,
    severity: 'blocker',
    description:
      'Integrated loudness between -16 and -14 LUFS (podcast standard)',
  },
  {
    name: 'no-clipping',
    check: (r: AudioQualityReport) => !r.clipping.detected,
    severity: 'blocker',
    description: 'No audio clipping detected',
  },
  {
    name: 'speaker-balance',
    check: (r: SpeakerBalanceReport) => r.balanced,
    severity: 'blocker',
    description:
      'Speaker balance within 40-60% range (2-speaker format)',
  },
  {
    name: 'duration-accuracy',
    check: (r: DurationReport) => r.passes,
    severity: 'blocker',
    description: 'Duration within +/-10% of target',
  },

  // --- WARNINGS (flag but don't block) ---
  {
    name: 'no-awkward-pauses',
    check: (r: AudioQualityReport) => r.silence.awkwardPauses === 0,
    severity: 'warning',
    description: 'No pauses longer than 3 seconds',
  },
  {
    name: 'true-peak',
    check: (r: AudioQualityReport) => r.loudness.truePeak <= -1.0,
    severity: 'warning',
    description: 'True peak <= -1.0 dBTP (headroom for encoding)',
  },
  {
    name: 'silence-ratio',
    check: (r: AudioQualityReport) =>
      r.silence.silenceRatio >= 0.10 && r.silence.silenceRatio <= 0.30,
    severity: 'warning',
    description:
      'Silence ratio between 10-30% (natural breathing room)',
  },
  {
    name: 'source-coverage',
    check: (r: FaithfulnessReport) => r.sourceCoverage >= 0.75,
    severity: 'warning',
    description: 'At least 75% of source key points covered',
  },
  {
    name: 'prosody-naturalness',
    check: (r: any) => r.naturalness_estimate >= 0.6,
    severity: 'warning',
    description: 'Prosody naturalness score >= 0.6',
  },
];
```

### 6.2 Gate Runner

```typescript
interface GateResult {
  gate: string;
  passed: boolean;
  severity: 'blocker' | 'warning';
  description: string;
}

interface PipelineGateReport {
  results: GateResult[];
  blockersFailed: number;
  warningsFailed: number;
  canPublish: boolean;
  summary: string;
}

function runQualityGates(reports: {
  faithfulness?: FaithfulnessReport;
  audio?: AudioQualityReport;
  speakerBalance?: SpeakerBalanceReport;
  duration?: DurationReport;
  prosody?: any;
}): PipelineGateReport {
  const results: GateResult[] = [];

  const reportMap: Record<string, any> = {
    'faithfulness': reports.faithfulness,
    'no-hallucinations': reports.faithfulness,
    'audio-snr': reports.audio,
    'loudness-target': reports.audio,
    'no-clipping': reports.audio,
    'speaker-balance': reports.speakerBalance,
    'duration-accuracy': reports.duration,
    'no-awkward-pauses': reports.audio,
    'true-peak': reports.audio,
    'silence-ratio': reports.audio,
    'source-coverage': reports.faithfulness,
    'prosody-naturalness': reports.prosody,
  };

  for (const gate of QUALITY_GATES) {
    const report = reportMap[gate.name];
    if (!report) {
      results.push({
        gate: gate.name,
        passed: false,
        severity: gate.severity,
        description: `${gate.description} — SKIPPED (no data)`,
      });
      continue;
    }

    const passed = gate.check(report);
    results.push({
      gate: gate.name,
      passed,
      severity: gate.severity,
      description: gate.description,
    });
  }

  const blockersFailed = results.filter(
    r => !r.passed && r.severity === 'blocker'
  ).length;
  const warningsFailed = results.filter(
    r => !r.passed && r.severity === 'warning'
  ).length;
  const canPublish = blockersFailed === 0;

  const passedCount = results.filter(r => r.passed).length;
  const summary = canPublish
    ? `PASS — ${passedCount}/${results.length} gates passed`
      + ` (${warningsFailed} warnings)`
    : `FAIL — ${blockersFailed} blocker(s) failed,`
      + ` ${warningsFailed} warning(s)`;

  return { results, blockersFailed, warningsFailed, canPublish, summary };
}
```

### 6.3 Quality Gate Summary Table

| Gate | Threshold | Severity | Rationale |
|------|-----------|----------|-----------|
| Faithfulness | >= 0.85 | Blocker | Publishing inaccurate content damages credibility |
| No hallucinations | 0 fabricated claims | Blocker | Any hallucination is a trust violation |
| Audio SNR | >= 30 dB | Blocker | Below 30 dB, noise is audibly distracting |
| Loudness | -16 to -14 LUFS | Blocker | Spotify/Apple podcast loudness standard |
| No clipping | 0 clipped samples | Blocker | Clipping is immediately audible distortion |
| Speaker balance | 40-60% per speaker | Blocker | Unbalanced "conversation" sounds like a monologue |
| Duration accuracy | within +/-10% | Blocker | Missing duration target suggests content issues |
| No awkward pauses | 0 pauses > 3s | Warning | Awkward but not catastrophic — can be edited |
| True peak | <= -1.0 dBTP | Warning | Encoding headroom — matters for lossy formats |
| Silence ratio | 10-30% | Warning | Too little = breathless; too much = dead air |
| Source coverage | >= 75% | Warning | Missing points reduce value but aren't errors |
| Prosody naturalness | >= 0.6 | Warning | Robotic delivery is off-putting but tolerable |

---

## 7. Putting It All Together: Full Evaluation Pipeline

```typescript
/**
 * Complete podcast quality evaluation pipeline.
 * Runs all checks and produces a unified report.
 *
 * Usage:
 *   const report = await evaluatePodcast({
 *     audioPath: './output/episode-42.mp3',
 *     scriptPath: './output/episode-42-script.json',
 *     sourcePaths: ['./sources/article1.txt', './sources/article2.txt'],
 *     targetMinutes: 15,
 *     format: 'deep-dive',
 *     anthropicApiKey: process.env.ANTHROPIC_API_KEY!,
 *   });
 *
 *   if (report.canPublish) {
 *     console.log('Ready to publish!');
 *   } else {
 *     console.log('Issues found:', report.summary);
 *   }
 */

import { readFileSync } from 'fs';

interface EvaluationConfig {
  audioPath: string;
  scriptPath: string;           // JSON with { segments: SpeakerSegment[] }
  sourcePaths: string[];
  targetMinutes: number;
  format: string;
  anthropicApiKey: string;
  useCase?: string;             // for weight selection
}

interface FullEvaluationReport {
  canPublish: boolean;
  summary: string;
  weightedScore: number;        // 0-1 composite
  faithfulness: FaithfulnessReport;
  audioQuality: AudioQualityReport;
  speakerBalance: SpeakerBalanceReport;
  duration: DurationReport;
  silence: SilenceReport;
  gates: PipelineGateReport;
  timestamp: string;
}

async function evaluatePodcast(
  config: EvaluationConfig
): Promise<FullEvaluationReport> {
  console.log('[eval] Starting podcast quality evaluation...');

  // Load script and sources
  const scriptData = JSON.parse(
    readFileSync(config.scriptPath, 'utf-8')
  );
  const segments: SpeakerSegment[] = scriptData.segments;
  const sources = config.sourcePaths.map(p => readFileSync(p, 'utf-8'));
  const fullScript = segments
    .map(s => `${s.speaker}: ${s.text}`)
    .join('\n');

  // Run all evaluations
  console.log('[eval] Running faithfulness check...');
  const faithfulness = await scoreFaithfulness(
    fullScript, sources, config.anthropicApiKey
  );

  console.log('[eval] Running audio quality analysis...');
  const audioQuality = await analyzeAudioQuality(config.audioPath);

  console.log('[eval] Checking speaker balance...');
  const speakerBalance = checkSpeakerBalance(segments);

  console.log('[eval] Checking duration accuracy...');
  const duration = await checkDurationAccuracy(
    config.audioPath, config.targetMinutes
  );

  console.log('[eval] Assessing silence patterns...');
  const silence = assessSilencePattern(
    audioQuality.silence.segments,
    audioQuality.duration
  );

  // Run quality gates
  console.log('[eval] Running quality gates...');
  const gates = runQualityGates({
    faithfulness,
    audio: audioQuality,
    speakerBalance,
    duration,
  });

  // Calculate weighted composite score
  const weights = WEIGHTS_BY_USE_CASE[config.useCase || 'default'];
  const textScore = faithfulness.overallScore;
  const speechScore = speakerBalance.balanced ? 0.8 : 0.4;
  const audioScore = audioQuality.overallPass ? 0.9 : 0.5;
  const weightedScore =
    weights.text * textScore +
    weights.speech * speechScore +
    weights.audio * audioScore;

  const report: FullEvaluationReport = {
    canPublish: gates.canPublish,
    summary: gates.summary,
    weightedScore,
    faithfulness,
    audioQuality,
    speakerBalance,
    duration,
    silence,
    gates,
    timestamp: new Date().toISOString(),
  };

  // Print summary
  console.log('\n========================================');
  console.log('  PODCAST QUALITY EVALUATION REPORT');
  console.log('========================================');
  console.log(`  Can publish: ${report.canPublish ? 'YES' : 'NO'}`);
  console.log(`  Weighted score: ${(report.weightedScore * 100).toFixed(1)}%`);
  console.log(`  ${report.summary}`);
  console.log('');
  console.log('  Gate Results:');
  for (const result of gates.results) {
    const icon = result.passed ? 'PASS' : 'FAIL';
    const sev = result.severity === 'blocker' ? '[BLOCKER]' : '[WARNING]';
    console.log(
      `    ${icon} ${sev} ${result.gate}: ${result.description}`
    );
  }
  console.log('========================================\n');

  return report;
}
```

---

## 8. Industry Reference: Platform Loudness Standards

When targeting specific podcast platforms, use these loudness standards:

| Platform | Target LUFS | True Peak | Notes |
|----------|-------------|-----------|-------|
| **Spotify** | -14 LUFS | -1.0 dBTP | Will normalize louder content down |
| **Apple Podcasts** | -16 LUFS | -1.0 dBTP | Recommended by Apple |
| **YouTube** | -14 LUFS | -1.0 dBTP | Normalizes to -14 |
| **Amazon Music** | -14 LUFS | -2.0 dBTP | Slightly more conservative peak |
| **General podcast** | -16 to -14 LUFS | -1.0 dBTP | Safe range for all platforms |

**Recommendation:** Target -16 LUFS with -1.0 dBTP true peak. This is the
most universally compatible target and avoids normalization artifacts on
any platform.

---

## 9. Troubleshooting Common Issues

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| Faithfulness score < 0.85 | Script hallucinating or drifting from sources | Tighten system prompt, add source quotes in context |
| SNR < 30 dB | TTS model producing noisy output | Switch to higher-quality voice model, add post-processing denoising |
| Loudness out of range | No normalization in pipeline | Add `loudnorm` FFmpeg filter: `ffmpeg -i in.mp3 -af loudnorm=I=-16:TP=-1:LRA=11 out.mp3` |
| Clipping detected | Gain too high before limiting | Reduce input gain, add limiter with -1 dBTP ceiling |
| Speaker imbalance > 60/40 | Script allocates too much to one speaker | Adjust script generation prompt to enforce balance |
| Awkward pauses > 3s | TTS inserting long silences at paragraph breaks | Post-process: trim silences > 2s down to 1.5s |
| Monotone prosody | TTS model lacks expressiveness | Use SSML markup for emphasis, try different voice, add emotion directives |
| Duration off by > 10% | Script too long/short for target | Adjust word count target (avg podcast: ~150 words/minute) |

---

## 10. Research Citations

> **PodEval** (arXiv 2510.00485, Oct 2025) — Three-dimensional evaluation framework
> covering text quality, speech quality, and audio quality. Introduces spammer detection
> methodology for subjective listening tests to improve inter-rater reliability. Key insight:
> single-dimension metrics (e.g., only MOS) miss critical quality failures in AI podcasts.

> **PodBench** (arXiv 2601.14903, Jan 2026) — 800-sample benchmark spanning 4 podcast
> formats with multi-faceted evaluation. Combines quantitative constraint checking
> (duration, speaker balance, structure) with LLM-based quality assessment using
> Claude as evaluator. Key insight: structural compliance and content fidelity are
> orthogonal dimensions — a podcast can sound great but be factually wrong.

> **"Toward Objective Prosody Evaluation in TTS"** (arXiv 2511.02104, Nov 2025) —
> Linguistically motivated prosody evaluation framework. Demonstrates that pitch variation,
> pause distribution, and speaking rate are the three features most correlated with human
> MOS ratings (r > 0.82). Key insight: monotone score (pitch CV) alone predicts 67% of
> human naturalness judgments.

---

## Related Skills

- `audio-enhancement-pipeline` — FFmpeg filter chains for post-production cleanup
- `ffmpeg-command-generator` — Natural language to FFmpeg command conversion
- `transcription-pipeline-selector` — Choose the right STT engine for your use case
- `content-repurposing-pipeline` — Convert podcast audio into social media content
