# Content Repurposing Pipeline

## Metadata

- **Title:** Automated Content Repurposing Pipeline
- **Category:** Creative/Multimedia
- **Version:** v12.6.0
- **Created:** 2026-03-09
- **Dependencies:** FFmpeg, Sharp, Whisper/Deepgram/AssemblyAI, Claude/Gemini API

## Description

End-to-end pipeline that transforms long-form content (sermons, lectures, podcasts, Bible studies) into multi-format output: short video clips with burned-in captions, audiograms, quote cards, blog drafts, social media posts, and YouTube chapters. This is the "crown jewel" skill that combines FFmpeg, transcription, and image processing into a single automated workflow.

## When to Use

- After recording a sermon, lecture, podcast, or Bible study (30-90 minutes)
- When a ministry or content creator needs a week's worth of social media from one recording
- When repurposing existing video/audio archives into modern formats
- When building a content calendar from long-form source material

---

## Pipeline Overview

```
Long-form content (sermon/lecture/podcast, 30-90 min)
  |
  v
Step 1: Audio extraction (FFmpeg)
  |
  v
Step 2: Transcription (Whisper/Deepgram/AssemblyAI)
  |
  v
Step 3: AI Analysis (Claude/Gemini)
  - Identify key quotes (30-60 sec clips)
  - Generate summary
  - Extract topic segments
  - Create social media captions
  |
  v
Step 4: Generate outputs
  a) Short video clips with burned-in captions
  b) Audiograms (waveform animation + quote text overlay)
  c) Quote cards (image with text overlay)
  d) Blog post draft from transcript
  e) Social media posts (Twitter, Instagram, Facebook)
  f) YouTube chapters from topic segments
```

---

## Node.js Implementation

### Dependencies

```json
{
  "dependencies": {
    "sharp": "^0.33.2",
    "@anthropic-ai/sdk": "^0.39.0",
    "@google/generative-ai": "^0.21.0",
    "deepgram-sdk": "^3.9.0",
    "assemblyai": "^4.8.0"
  }
}
```

### Complete Pipeline Class

```typescript
import { execFileSync } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import sharp from 'sharp';
import Anthropic from '@anthropic-ai/sdk';

// ─── Types ───────────────────────────────────────────────────────────────────

interface TranscriptSegment {
  start: number;    // seconds
  end: number;      // seconds
  text: string;
  confidence: number;
}

interface Transcript {
  segments: TranscriptSegment[];
  fullText: string;
  duration: number; // total seconds
}

interface KeyMoment {
  start: number;
  end: number;
  quote: string;
  context: string;
  emotionalTone: 'inspiring' | 'teaching' | 'prophetic' | 'worship' | 'testimony';
  socialCaption: string;
}

interface TopicSegment {
  start: number;
  end: number;
  title: string;
  summary: string;
}

interface ContentAnalysis {
  title: string;
  summary: string;
  keyMoments: KeyMoment[];
  topicSegments: TopicSegment[];
  blogDraft: string;
  hashtags: string[];
}

interface PipelineConfig {
  outputDir: string;
  brandingLogo?: string;      // path to PNG logo
  brandColor?: string;        // hex color, e.g. '#1a1a2e'
  accentColor?: string;       // hex color, e.g. '#e94560'
  fontPath?: string;          // path to .ttf font for captions
  churchName?: string;
  aiProvider: 'claude' | 'gemini';
  transcriptionProvider: 'whisper' | 'deepgram' | 'assemblyai';
}

// ─── Helper: Safe FFmpeg Execution ───────────────────────────────────────────
// Uses execFileSync to avoid shell injection. All arguments are passed as arrays.

function runFFmpeg(args: string[]): void {
  execFileSync('ffmpeg', args, { stdio: 'pipe' });
}

function runWhisper(args: string[]): void {
  execFileSync('whisper', args, { stdio: 'pipe', timeout: 600_000 });
}

// ─── Pipeline Class ──────────────────────────────────────────────────────────

export class ContentRepurposingPipeline {
  private config: PipelineConfig;
  private anthropic: Anthropic | null = null;

  constructor(config: PipelineConfig) {
    this.config = {
      brandColor: '#1a1a2e',
      accentColor: '#e94560',
      churchName: 'Ministry',
      ...config,
    };

    if (config.aiProvider === 'claude') {
      this.anthropic = new Anthropic();
    }
  }

  // ─── Step 1: Audio Extraction ────────────────────────────────────────────

  /**
   * Extract audio from video file as WAV (16kHz mono for transcription)
   * and as high-quality AAC for audiogram output.
   */
  async extractAudio(videoPath: string): Promise<{ wavPath: string; aacPath: string }> {
    const baseName = path.basename(videoPath, path.extname(videoPath));
    const wavPath = path.join(this.config.outputDir, `${baseName}_audio.wav`);
    const aacPath = path.join(this.config.outputDir, `${baseName}_audio.aac`);

    await fs.mkdir(this.config.outputDir, { recursive: true });

    // WAV for transcription (16kHz mono — optimal for Whisper/Deepgram)
    runFFmpeg([
      '-i', videoPath,
      '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
      wavPath, '-y',
    ]);

    // AAC for audiogram output (high quality stereo)
    runFFmpeg([
      '-i', videoPath,
      '-vn', '-acodec', 'aac', '-b:a', '192k', '-ar', '44100',
      aacPath, '-y',
    ]);

    return { wavPath, aacPath };
  }

  // ─── Step 2: Transcription ───────────────────────────────────────────────

  /**
   * Transcribe audio to text with word-level timestamps.
   * Supports Whisper (local), Deepgram, and AssemblyAI.
   */
  async transcribe(audioPath: string): Promise<Transcript> {
    switch (this.config.transcriptionProvider) {
      case 'whisper':
        return this.transcribeWhisper(audioPath);
      case 'deepgram':
        return this.transcribeDeepgram(audioPath);
      case 'assemblyai':
        return this.transcribeAssemblyAI(audioPath);
      default:
        throw new Error(`Unknown transcription provider: ${this.config.transcriptionProvider}`);
    }
  }

  private async transcribeWhisper(audioPath: string): Promise<Transcript> {
    const outputDir = path.join(this.config.outputDir, 'whisper_out');
    await fs.mkdir(outputDir, { recursive: true });

    // Use whisper CLI (requires: pip install openai-whisper)
    // large-v3 model for best accuracy
    runWhisper([
      audioPath,
      '--model', 'large-v3',
      '--output_format', 'json',
      '--output_dir', outputDir,
      '--language', 'en',
    ]);

    const baseName = path.basename(audioPath, path.extname(audioPath));
    const jsonPath = path.join(outputDir, `${baseName}.json`);
    const result = JSON.parse(await fs.readFile(jsonPath, 'utf-8'));

    const segments: TranscriptSegment[] = result.segments.map((seg: any) => ({
      start: seg.start,
      end: seg.end,
      text: seg.text.trim(),
      confidence: seg.avg_logprob ? Math.exp(seg.avg_logprob) : 0.9,
    }));

    return {
      segments,
      fullText: segments.map(s => s.text).join(' '),
      duration: segments[segments.length - 1]?.end ?? 0,
    };
  }

  private async transcribeDeepgram(audioPath: string): Promise<Transcript> {
    const { createClient } = await import('@deepgram/sdk');
    const deepgram = createClient(process.env.DEEPGRAM_API_KEY!);

    const audioBuffer = await fs.readFile(audioPath);
    const { result } = await deepgram.listen.prerecorded.transcribeFile(audioBuffer, {
      model: 'nova-2',
      smart_format: true,
      paragraphs: true,
      utterances: true,
      diarize: true, // speaker detection — useful for interviews
    });

    const utterances = result.results?.utterances ?? [];
    const segments: TranscriptSegment[] = utterances.map((u: any) => ({
      start: u.start,
      end: u.end,
      text: u.transcript,
      confidence: u.confidence,
    }));

    return {
      segments,
      fullText: segments.map(s => s.text).join(' '),
      duration: segments[segments.length - 1]?.end ?? 0,
    };
  }

  private async transcribeAssemblyAI(audioPath: string): Promise<Transcript> {
    const { AssemblyAI } = await import('assemblyai');
    const client = new AssemblyAI({ apiKey: process.env.ASSEMBLYAI_API_KEY! });

    const transcript = await client.transcripts.transcribe({
      audio: audioPath,
      speaker_labels: true,
      auto_chapters: true, // AssemblyAI auto-generates chapters
    });

    const segments: TranscriptSegment[] = (transcript.utterances ?? []).map((u: any) => ({
      start: u.start / 1000, // AssemblyAI uses milliseconds
      end: u.end / 1000,
      text: u.text,
      confidence: u.confidence,
    }));

    return {
      segments,
      fullText: transcript.text ?? '',
      duration: segments[segments.length - 1]?.end ?? 0,
    };
  }

  // ─── Step 3: AI Content Analysis ─────────────────────────────────────────

  /**
   * Analyze transcript with Claude or Gemini to extract:
   * - Key quotes suitable for 30-60 second clips
   * - Topic segments for YouTube chapters
   * - Summary for blog post
   * - Social media captions
   */
  async analyzeContent(transcript: Transcript): Promise<ContentAnalysis> {
    const prompt = `You are a content strategist for a Christian ministry. Analyze this transcript and extract structured content for repurposing.

TRANSCRIPT (${Math.round(transcript.duration / 60)} minutes):
${transcript.segments.map(s => `[${this.formatTimestamp(s.start)}] ${s.text}`).join('\n')}

Return a JSON object with this exact structure:
{
  "title": "Compelling title for this content",
  "summary": "2-3 paragraph summary suitable for a blog post introduction",
  "keyMoments": [
    {
      "start": <start_seconds>,
      "end": <end_seconds>,
      "quote": "The exact quote text",
      "context": "Brief context of what's being discussed",
      "emotionalTone": "inspiring|teaching|prophetic|worship|testimony",
      "socialCaption": "Ready-to-post social media caption with emojis and call to action"
    }
  ],
  "topicSegments": [
    {
      "start": <start_seconds>,
      "end": <end_seconds>,
      "title": "Segment title",
      "summary": "1-2 sentence summary"
    }
  ],
  "blogDraft": "Full blog post draft (800-1200 words) based on the transcript content. Use headers, paragraphs, and scripture references where applicable.",
  "hashtags": ["relevantHashtag1", "relevantHashtag2"]
}

RULES:
- Select 5-8 key moments, each 30-60 seconds long
- Key moments should be emotionally powerful, quotable, or contain key teaching points
- Topic segments should cover the entire recording (for YouTube chapters)
- First topic segment must start at 0:00
- Social captions should be platform-ready with hashtags
- Blog draft should stand alone without needing to watch the video
- Include scripture references where the speaker quotes or references Bible passages

Return ONLY valid JSON, no markdown code fences.`;

    if (this.config.aiProvider === 'claude') {
      return this.analyzeWithClaude(prompt);
    } else {
      return this.analyzeWithGemini(prompt);
    }
  }

  private async analyzeWithClaude(prompt: string): Promise<ContentAnalysis> {
    if (!this.anthropic) throw new Error('Anthropic client not initialized');

    const response = await this.anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 8192,
      messages: [{ role: 'user', content: prompt }],
    });

    const text = response.content[0].type === 'text' ? response.content[0].text : '';
    return JSON.parse(text);
  }

  private async analyzeWithGemini(prompt: string): Promise<ContentAnalysis> {
    const { GoogleGenerativeAI } = await import('@google/generative-ai');
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
    const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });

    const result = await model.generateContent(prompt);
    const text = result.response.text();
    // Strip markdown fences if Gemini wraps in ```json
    const cleaned = text.replace(/^```json\n?/, '').replace(/\n?```$/, '');
    return JSON.parse(cleaned);
  }

  // ─── Step 4a: Generate Short Video Clips ─────────────────────────────────

  /**
   * Extract short clips from source video with burned-in captions,
   * fade in/out transitions, and optional branding overlay.
   */
  async generateClips(
    videoPath: string,
    moments: KeyMoment[]
  ): Promise<string[]> {
    const clipDir = path.join(this.config.outputDir, 'clips');
    await fs.mkdir(clipDir, { recursive: true });

    const clipPaths: string[] = [];

    for (let i = 0; i < moments.length; i++) {
      const moment = moments[i];
      const clipPath = path.join(clipDir, `clip_${i + 1}.mp4`);
      const srtPath = path.join(clipDir, `clip_${i + 1}.srt`);

      // Generate SRT subtitle file for this clip
      await this.generateSRT(srtPath, moment);

      const duration = moment.end - moment.start;
      const fadeStart = duration - 0.5;

      // Build the complex filter string
      const fontStyle = this.config.fontPath
        ? `FontName=Custom,FontSize=22`
        : `FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1`;

      const srtPathNormalized = srtPath.replace(/\\/g, '/');
      const videoFilter = [
        `subtitles='${srtPathNormalized}':si=0:force_style='${fontStyle}'`,
        `fade=t=in:st=0:d=0.5`,
        `fade=t=out:st=${fadeStart}:d=0.5`,
        `scale=1080:1920:force_original_aspect_ratio=decrease`,
        `pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black`,
      ].join(',');

      const audioFilter = `afade=t=in:st=0:d=0.3,afade=t=out:st=${fadeStart}:d=0.5`;

      runFFmpeg([
        '-ss', String(moment.start), '-i', videoPath, '-t', String(duration),
        '-vf', videoFilter,
        '-af', audioFilter,
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-movflags', '+faststart',
        clipPath, '-y',
      ]);

      clipPaths.push(clipPath);

      // Clean up temp SRT
      await fs.unlink(srtPath).catch(() => {});
    }

    return clipPaths;
  }

  /**
   * Generate an SRT subtitle file from a key moment.
   * Splits quote into ~10-word chunks for readable captions.
   */
  private async generateSRT(srtPath: string, moment: KeyMoment): Promise<void> {
    const words = moment.quote.split(' ');
    const chunkSize = 10;
    const chunks: string[] = [];

    for (let i = 0; i < words.length; i += chunkSize) {
      chunks.push(words.slice(i, i + chunkSize).join(' '));
    }

    const duration = moment.end - moment.start;
    const chunkDuration = duration / chunks.length;

    let srt = '';
    chunks.forEach((chunk, idx) => {
      const start = chunkDuration * idx;
      const end = chunkDuration * (idx + 1);
      srt += `${idx + 1}\n`;
      srt += `${this.formatSRTTime(start)} --> ${this.formatSRTTime(end)}\n`;
      srt += `${chunk}\n\n`;
    });

    await fs.writeFile(srtPath, srt, 'utf-8');
  }

  // ─── Step 4b: Generate Audiograms ────────────────────────────────────────

  /**
   * Create audiogram videos: waveform visualization + quote text overlay
   * on a branded background. Perfect for podcast clips on social media.
   */
  async generateAudiograms(
    audioPath: string,
    quotes: KeyMoment[]
  ): Promise<string[]> {
    const audiogramDir = path.join(this.config.outputDir, 'audiograms');
    await fs.mkdir(audiogramDir, { recursive: true });

    const audiogramPaths: string[] = [];

    for (let i = 0; i < quotes.length; i++) {
      const quote = quotes[i];
      const outputPath = path.join(audiogramDir, `audiogram_${i + 1}.mp4`);
      const bgImagePath = path.join(audiogramDir, `bg_${i + 1}.png`);

      // Create branded background image with quote text
      await this.createAudiogramBackground(bgImagePath, quote.quote, 1080, 1080);

      const duration = quote.end - quote.start;

      // FFmpeg: audio segment + waveform visualization + background image
      const filterComplex = [
        `[0:a]showwaves=s=1080x200:mode=cline:rate=30:colors=${this.config.accentColor}[waves]`,
        `[1:v]scale=1080:1080[bg]`,
        `[bg][waves]overlay=0:750[v]`,
      ].join(';');

      runFFmpeg([
        '-ss', String(quote.start), '-t', String(duration), '-i', audioPath,
        '-loop', '1', '-i', bgImagePath,
        '-filter_complex', filterComplex,
        '-map', '[v]', '-map', '0:a',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-tune', 'stillimage',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest', '-movflags', '+faststart',
        '-t', String(duration),
        outputPath, '-y',
      ]);

      audiogramPaths.push(outputPath);

      // Clean up temp background
      await fs.unlink(bgImagePath).catch(() => {});
    }

    return audiogramPaths;
  }

  /**
   * Create a branded background image for audiogram with quote text overlay.
   */
  private async createAudiogramBackground(
    outputPath: string,
    quoteText: string,
    width: number,
    height: number
  ): Promise<void> {
    // Create gradient background
    const svgBackground = `
      <svg width="${width}" height="${height}">
        <defs>
          <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:${this.config.brandColor};stop-opacity:1" />
            <stop offset="100%" style="stop-color:#16213e;stop-opacity:1" />
          </linearGradient>
        </defs>
        <rect width="${width}" height="${height}" fill="url(#grad)" />
      </svg>`;

    // Word wrap the quote text for SVG overlay
    const maxCharsPerLine = 35;
    const lines = this.wordWrap(quoteText, maxCharsPerLine);
    const lineHeight = 48;
    const startY = 200;

    const textSvg = `
      <svg width="${width}" height="${height}">
        <style>
          .quote { fill: white; font-size: 36px; font-family: Georgia, serif; text-anchor: middle; }
          .attribution { fill: ${this.config.accentColor}; font-size: 20px; font-family: Arial, sans-serif; text-anchor: middle; }
          .open-quote { fill: ${this.config.accentColor}; font-size: 120px; font-family: Georgia, serif; opacity: 0.6; }
        </style>
        <text class="open-quote" x="80" y="180">"</text>
        ${lines.map((line, idx) =>
          `<text class="quote" x="${width / 2}" y="${startY + idx * lineHeight}">${this.escapeXml(line)}</text>`
        ).join('\n')}
        <text class="attribution" x="${width / 2}" y="${startY + lines.length * lineHeight + 40}">
          -- ${this.config.churchName}
        </text>
      </svg>`;

    await sharp(Buffer.from(svgBackground))
      .composite([{
        input: Buffer.from(textSvg),
        top: 0,
        left: 0,
      }])
      .png()
      .toFile(outputPath);
  }

  // ─── Step 4c: Generate Quote Cards ───────────────────────────────────────

  /**
   * Generate shareable quote card images using Sharp.
   * Creates multiple sizes: 1080x1080 (Instagram), 1200x628 (Twitter/FB).
   */
  async generateQuoteCards(quotes: KeyMoment[]): Promise<string[]> {
    const cardDir = path.join(this.config.outputDir, 'quote_cards');
    await fs.mkdir(cardDir, { recursive: true });

    const cardPaths: string[] = [];

    const sizes = [
      { name: 'instagram', width: 1080, height: 1080 },
      { name: 'twitter', width: 1200, height: 628 },
    ];

    for (let i = 0; i < quotes.length; i++) {
      for (const size of sizes) {
        const outputPath = path.join(cardDir, `quote_${i + 1}_${size.name}.png`);
        await this.createQuoteCard(outputPath, quotes[i], size.width, size.height);
        cardPaths.push(outputPath);
      }
    }

    return cardPaths;
  }

  /**
   * Create a single quote card with branded background, text overlay,
   * and optional logo watermark.
   */
  private async createQuoteCard(
    outputPath: string,
    moment: KeyMoment,
    width: number,
    height: number
  ): Promise<void> {
    // Create gradient background
    const svgBg = `
      <svg width="${width}" height="${height}">
        <defs>
          <linearGradient id="cardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:${this.config.brandColor}" />
            <stop offset="50%" style="stop-color:#0f3460" />
            <stop offset="100%" style="stop-color:${this.config.brandColor}" />
          </linearGradient>
        </defs>
        <rect width="${width}" height="${height}" fill="url(#cardGrad)" />
        <!-- Decorative accent line -->
        <rect x="${width * 0.1}" y="${height * 0.12}" width="60" height="4" fill="${this.config.accentColor}" rx="2" />
      </svg>`;

    // Calculate font size based on quote length and card dimensions
    const fontSize = moment.quote.length > 150 ? 28 : moment.quote.length > 80 ? 34 : 42;
    const maxChars = Math.floor((width * 0.8) / (fontSize * 0.55));
    const lines = this.wordWrap(moment.quote, maxChars);
    const lineHeight = fontSize * 1.4;
    const textBlockHeight = lines.length * lineHeight;
    const startY = (height - textBlockHeight) / 2;

    const textSvg = `
      <svg width="${width}" height="${height}">
        <style>
          .q { fill: #ffffff; font-size: ${fontSize}px; font-family: Georgia, 'Times New Roman', serif; text-anchor: middle; }
          .attr { fill: ${this.config.accentColor}; font-size: ${Math.floor(fontSize * 0.5)}px; font-family: Arial, Helvetica, sans-serif; text-anchor: middle; letter-spacing: 2px; }
          .deco { fill: ${this.config.accentColor}; font-size: ${fontSize * 2.5}px; font-family: Georgia, serif; opacity: 0.4; }
        </style>
        <text class="deco" x="${width * 0.08}" y="${startY - 10}">\u201C</text>
        ${lines.map((line, idx) =>
          `<text class="q" x="${width / 2}" y="${startY + idx * lineHeight}">${this.escapeXml(line)}</text>`
        ).join('\n')}
        <text class="deco" x="${width * 0.85}" y="${startY + textBlockHeight + 20}">\u201D</text>
        <text class="attr" x="${width / 2}" y="${height * 0.88}">
          ${this.config.churchName?.toUpperCase() ?? ''}
        </text>
      </svg>`;

    const composites: sharp.OverlayOptions[] = [
      { input: Buffer.from(textSvg), top: 0, left: 0 },
    ];

    // Add logo watermark if provided
    if (this.config.brandingLogo) {
      try {
        const logoBuffer = await sharp(this.config.brandingLogo)
          .resize(120, 120, { fit: 'inside' })
          .png()
          .toBuffer();

        composites.push({
          input: logoBuffer,
          gravity: 'southeast',
        });
      } catch {
        // Logo not found — skip silently
      }
    }

    await sharp(Buffer.from(svgBg))
      .composite(composites)
      .png({ quality: 95 })
      .toFile(outputPath);
  }

  // ─── Step 4d: Generate Social Media Posts ────────────────────────────────

  /**
   * Generate platform-specific social media posts from analysis.
   */
  generateSocialPosts(
    analysis: ContentAnalysis
  ): { twitter: string[]; instagram: string[]; facebook: string[] } {
    const hashtags = analysis.hashtags.map(h => `#${h}`).join(' ');

    const twitter = analysis.keyMoments.map((m) => {
      // Twitter: 280 char limit, concise, with link placeholder
      const caption = m.socialCaption.length > 230
        ? m.socialCaption.substring(0, 227) + '...'
        : m.socialCaption;
      return `${caption}\n\n${hashtags.substring(0, 50)}\n\n[Link to full message]`;
    });

    const instagram = analysis.keyMoments.map((m) => {
      // Instagram: longer captions OK, heavy on hashtags
      return [
        m.socialCaption,
        '',
        `"${m.quote.substring(0, 200)}${m.quote.length > 200 ? '...' : ''}"`,
        '',
        `Watch the full message -- link in bio`,
        '',
        hashtags,
        '#sermon #faith #church #sundayservice #worship #bibleverse',
      ].join('\n');
    });

    const facebook = analysis.keyMoments.map((m) => {
      // Facebook: conversational, encourage sharing
      return [
        m.socialCaption,
        '',
        `"${m.quote}"`,
        '',
        `Share this with someone who needs to hear it today.`,
        '',
        `Watch the full message: [Link]`,
        '',
        hashtags,
      ].join('\n');
    });

    return { twitter, instagram, facebook };
  }

  // ─── Step 4e: Generate YouTube Chapters ──────────────────────────────────

  /**
   * Generate YouTube chapter timestamps from topic segments.
   * Format: "0:00 Introduction\n2:15 First Point\n..."
   */
  generateYouTubeChapters(segments: TopicSegment[]): string {
    return segments
      .map(seg => `${this.formatTimestamp(seg.start)} ${seg.title}`)
      .join('\n');
  }

  // ─── Step 4f: Generate GIFs from Key Moments ────────────────────────────

  /**
   * Create animated GIFs from key moments (useful for Twitter/Discord).
   * Limited to 8 seconds max to keep file size reasonable.
   */
  async generateGifs(
    videoPath: string,
    moments: KeyMoment[]
  ): Promise<string[]> {
    const gifDir = path.join(this.config.outputDir, 'gifs');
    await fs.mkdir(gifDir, { recursive: true });

    const gifPaths: string[] = [];

    for (let i = 0; i < Math.min(moments.length, 5); i++) {
      const moment = moments[i];
      const gifPath = path.join(gifDir, `moment_${i + 1}.gif`);
      const palettePath = path.join(gifDir, `palette_${i}.png`);
      const duration = Math.min(moment.end - moment.start, 8); // Cap at 8 seconds

      // Pass 1: Generate optimized palette
      runFFmpeg([
        '-ss', String(moment.start), '-t', String(duration), '-i', videoPath,
        '-vf', 'fps=12,scale=480:-1:flags=lanczos,palettegen=stats_mode=diff',
        '-y', palettePath,
      ]);

      // Pass 2: Create GIF using palette for better quality
      runFFmpeg([
        '-ss', String(moment.start), '-t', String(duration), '-i', videoPath,
        '-i', palettePath,
        '-lavfi', 'fps=12,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3',
        gifPath, '-y',
      ]);

      // Clean up palette
      await fs.unlink(palettePath).catch(() => {});
      gifPaths.push(gifPath);
    }

    return gifPaths;
  }

  // ─── Full Pipeline Orchestrator ──────────────────────────────────────────

  /**
   * Run the complete pipeline end-to-end.
   * Returns paths to all generated assets.
   */
  async run(inputPath: string): Promise<{
    clips: string[];
    audiograms: string[];
    quoteCards: string[];
    gifs: string[];
    socialPosts: { twitter: string[]; instagram: string[]; facebook: string[] };
    youtubeChapters: string;
    blogDraft: string;
    analysis: ContentAnalysis;
  }> {
    console.log('Step 1/6: Extracting audio...');
    const { wavPath, aacPath } = await this.extractAudio(inputPath);

    console.log('Step 2/6: Transcribing...');
    const transcript = await this.transcribe(wavPath);

    console.log('Step 3/6: Analyzing content with AI...');
    const analysis = await this.analyzeContent(transcript);

    console.log('Step 4/6: Generating video clips...');
    const clips = await this.generateClips(inputPath, analysis.keyMoments);

    console.log('Step 5/6: Generating audiograms and quote cards...');
    const [audiograms, quoteCards, gifs] = await Promise.all([
      this.generateAudiograms(aacPath, analysis.keyMoments),
      this.generateQuoteCards(analysis.keyMoments),
      this.generateGifs(inputPath, analysis.keyMoments),
    ]);

    console.log('Step 6/6: Generating text content...');
    const socialPosts = this.generateSocialPosts(analysis);
    const youtubeChapters = this.generateYouTubeChapters(analysis.topicSegments);

    // Write text outputs to files
    await fs.writeFile(
      path.join(this.config.outputDir, 'youtube_chapters.txt'),
      youtubeChapters, 'utf-8'
    );
    await fs.writeFile(
      path.join(this.config.outputDir, 'blog_draft.md'),
      analysis.blogDraft, 'utf-8'
    );
    await fs.writeFile(
      path.join(this.config.outputDir, 'social_posts.json'),
      JSON.stringify(socialPosts, null, 2), 'utf-8'
    );

    console.log(`\nDone! All assets saved to: ${this.config.outputDir}`);
    console.log(`  - ${clips.length} video clips`);
    console.log(`  - ${audiograms.length} audiograms`);
    console.log(`  - ${quoteCards.length} quote cards`);
    console.log(`  - ${gifs.length} GIFs`);
    console.log(`  - Social posts for 3 platforms`);
    console.log(`  - YouTube chapters`);
    console.log(`  - Blog draft`);

    return {
      clips,
      audiograms,
      quoteCards,
      gifs,
      socialPosts,
      youtubeChapters,
      blogDraft: analysis.blogDraft,
      analysis,
    };
  }

  // ─── Utility Methods ────────────────────────────────────────────────────

  private formatTimestamp(seconds: number): string {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  private formatSRTTime(seconds: number): string {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    const ms = Math.round((seconds % 1) * 1000);
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')},${ms.toString().padStart(3, '0')}`;
  }

  private wordWrap(text: string, maxChars: number): string[] {
    const words = text.split(' ');
    const lines: string[] = [];
    let currentLine = '';

    for (const word of words) {
      if ((currentLine + ' ' + word).trim().length > maxChars) {
        if (currentLine) lines.push(currentLine.trim());
        currentLine = word;
      } else {
        currentLine += ' ' + word;
      }
    }
    if (currentLine.trim()) lines.push(currentLine.trim());
    return lines;
  }

  private escapeXml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  }
}
```

---

## FFmpeg Command Reference

### Clip Extraction with Fade In/Out

```bash
# Extract 45-second clip starting at 12:30, with audio/video fades
ffmpeg -ss 750 -i input.mp4 -t 45 \
  -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=44.5:d=0.5" \
  -af "afade=t=in:st=0:d=0.3,afade=t=out:st=44.5:d=0.5" \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  clip_output.mp4
```

### Caption Burning (SRT Subtitle Overlay)

```bash
# Burn subtitles into video with styled text
ffmpeg -i input.mp4 \
  -vf "subtitles='captions.srt':force_style='FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,MarginV=40'" \
  -c:v libx264 -crf 23 \
  -c:a copy \
  output_with_captions.mp4
```

### Audiogram (Audio + Waveform + Static Image)

```bash
# Create audiogram: background image + waveform visualization
ffmpeg -ss 120 -t 45 -i audio.aac \
  -loop 1 -i background.png \
  -filter_complex \
    "[0:a]showwaves=s=1080x200:mode=cline:rate=30:colors=#e94560[waves]; \
     [1:v]scale=1080:1080[bg]; \
     [bg][waves]overlay=0:750[v]" \
  -map "[v]" -map 0:a \
  -c:v libx264 -crf 23 -tune stillimage \
  -c:a aac -b:a 192k \
  -shortest -movflags +faststart \
  audiogram.mp4
```

### GIF Creation (Two-Pass with Palette)

```bash
# Pass 1: Generate optimized palette
ffmpeg -ss 30 -t 6 -i input.mp4 \
  -vf "fps=12,scale=480:-1:flags=lanczos,palettegen=stats_mode=diff" \
  palette.png

# Pass 2: Create GIF using palette for better quality/smaller size
ffmpeg -ss 30 -t 6 -i input.mp4 -i palette.png \
  -lavfi "fps=12,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3" \
  output.gif
```

### Vertical Video (9:16) for Reels/Shorts/TikTok

```bash
# Crop/pad landscape to 9:16 vertical with letterbox
ffmpeg -i input.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
  -c:v libx264 -crf 23 \
  vertical_output.mp4
```

---

## Sharp Command Reference

### Quote Card with Gradient Background

```typescript
import sharp from 'sharp';

// Create gradient background via SVG
const svgBg = `
  <svg width="1080" height="1080">
    <defs>
      <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#1a1a2e" />
        <stop offset="100%" style="stop-color:#16213e" />
      </linearGradient>
    </defs>
    <rect width="1080" height="1080" fill="url(#g)" />
  </svg>`;

// Text overlay via SVG composite
const textSvg = `
  <svg width="1080" height="1080">
    <text x="540" y="480" text-anchor="middle" fill="white"
          font-size="38" font-family="Georgia">Your quote here</text>
  </svg>`;

await sharp(Buffer.from(svgBg))
  .composite([
    { input: Buffer.from(textSvg), top: 0, left: 0 },
    // Logo watermark (bottom-right)
    { input: 'logo.png', gravity: 'southeast' },
  ])
  .png({ quality: 95 })
  .toFile('quote_card.png');
```

### Multiple Sizes

```typescript
const sizes = [
  { name: 'instagram_square', w: 1080, h: 1080 },  // Instagram post
  { name: 'instagram_story',  w: 1080, h: 1920 },  // Instagram/FB story
  { name: 'twitter_card',     w: 1200, h: 628 },   // Twitter/X card
  { name: 'facebook_post',    w: 1200, h: 630 },   // Facebook post
  { name: 'youtube_thumb',    w: 1280, h: 720 },   // YouTube thumbnail
];

for (const size of sizes) {
  await createQuoteCard(`output_${size.name}.png`, quote, size.w, size.h);
}
```

---

## Ministry-Specific Patterns

### Sunday Sermon to Monday Content Calendar

```
SUNDAY: Record sermon (30-60 min)
  |
SUNDAY NIGHT: Run pipeline (automated, ~5 min processing)
  |
MONDAY: Schedule the week's content
  - Monday:    Blog post draft (edit + publish)
  - Tuesday:   Quote card #1 (Instagram) + clip #1 (YouTube Shorts)
  - Wednesday: Audiogram #1 (Twitter/X) + Facebook text post
  - Thursday:  Quote card #2 (Instagram) + clip #2 (Reels)
  - Friday:    GIF moment (Twitter/Discord) + behind-the-scenes caption
  - Saturday:  Teaser clip for Sunday's message
  - Sunday:    YouTube upload with chapters + full social push
```

### Bible Study to Lesson Outline + Quiz

```typescript
// Extended analysis prompt for Bible study content
const bibleStudyPrompt = `
Additionally extract:
  "lessonOutline": {
    "passage": "Book Chapter:Verse-Verse",
    "context": "Historical and literary context",
    "keyTerms": [{ "term": "Greek/Hebrew word", "meaning": "definition", "usage": "how it's used here" }],
    "mainPoints": ["Point 1", "Point 2", "Point 3"],
    "applicationQuestions": ["How does this apply to...?"],
    "crossReferences": ["Related passage 1", "Related passage 2"]
  },
  "quizQuestions": [
    {
      "question": "Multiple choice or fill-in-the-blank",
      "options": ["A", "B", "C", "D"],
      "correctAnswer": "B",
      "explanation": "Why this is correct with scripture reference"
    }
  ]
`;
```

### Prophetic Word to Sharable Quote Cards

```typescript
// Prophetic content gets special visual treatment
const propheticConfig = {
  // Use bold, dramatic styling for prophetic declarations
  fontSizeMultiplier: 1.3,
  accentColor: '#FFD700',       // Gold for prophetic authority
  backgroundStyle: 'dramatic',   // Dark with light rays
  prefixText: 'Thus says the Lord:',
  // Always include scripture backing
  requireScriptureReference: true,
};
```

---

## Usage Example

```typescript
const pipeline = new ContentRepurposingPipeline({
  outputDir: './output/sunday-sermon-2026-03-09',
  brandingLogo: './assets/church-logo.png',
  brandColor: '#1a1a2e',
  accentColor: '#e94560',
  churchName: 'Living Word Fellowship',
  aiProvider: 'claude',
  transcriptionProvider: 'deepgram',
});

const results = await pipeline.run('./recordings/sermon-2026-03-09.mp4');

console.log('YouTube Chapters:\n', results.youtubeChapters);
console.log('Blog Draft saved to: output/sunday-sermon-2026-03-09/blog_draft.md');
console.log(`Generated ${results.clips.length} clips, ${results.quoteCards.length} cards`);
```

---

## Prerequisites

```bash
# FFmpeg (required)
# Windows: winget install FFmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# Whisper (if using local transcription)
pip install openai-whisper

# Node.js dependencies
npm install sharp @anthropic-ai/sdk @deepgram/sdk assemblyai @google/generative-ai
```

## Environment Variables

```bash
# Pick ONE transcription provider:
DEEPGRAM_API_KEY=your_key_here
ASSEMBLYAI_API_KEY=your_key_here
# Whisper uses local model — no API key needed

# Pick ONE AI provider:
ANTHROPIC_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

---
---

## Related Skills

- `creative-multimedia/ffmpeg-command-generator.md` -- Standalone FFmpeg command patterns
- `ecommerce/stripe-integration-verification.md` -- For monetizing content (donations, subscriptions)
- `methodology/AUTO_REVIEWER_SUBAGENT.md` -- Auto-review generated content quality
