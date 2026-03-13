---
name: text-to-speech-provider-selector
category: creative-multimedia
version: 1.0.0
contributed: 2026-03-10
contributor: dominion-flow-research
last_updated: 2026-03-10
tags: [tts, text-to-speech, audio, podcast, voice-synthesis, elevenlabs, orpheus, chatterbox, google-cloud-tts, bark]
difficulty: medium
---

# Text-to-Speech Provider Selector
## Description

Select the right Text-to-Speech provider for AI-powered audio generation — podcasts, online courses, narration, sermon recordings, and interactive voice applications. This skill provides a structured comparison of open-source and cloud TTS providers, complete integration code, and cost modeling to help you make the right choice without trial-and-error.

## When to Use

- Building a podcast generation pipeline (AI hosts, course narration)
- Adding voice output to any application (chatbots, accessibility, notifications)
- Choosing between local/private TTS and cloud APIs
- Generating multi-speaker audio content (dialogues, interviews)
- Estimating TTS costs for production workloads
- Need emotion control or voice cloning in generated speech

---

## 1. Provider Comparison Matrix

### Open-Source (Local) Providers

#### Orpheus TTS (canopyai/Orpheus-TTS)

The breakthrough model of 2025. Built on a Llama-3b backbone, Orpheus treats speech synthesis as a language modeling task — predicting speech tokens the same way an LLM predicts text tokens. This architectural choice gives it natural prosody and emotional range that rivals ElevenLabs.

- **Architecture:** LLM-backbone (Llama-3b fine-tuned on speech tokens)
- **Model sizes:** 3B (best quality), 1B (balanced), 400M (fast), 150M (edge/mobile)
- **Streaming latency:** ~200ms first-chunk with 3B model
- **Voice cloning:** Zero-shot (provide a reference clip)
- **Emotion:** Natural emotional speech from text context (no explicit slider)
- **Languages:** English primary, community multilingual fine-tunes emerging
- **License:** MIT — fully open, commercial use allowed
- **VRAM:** 3B needs ~8GB, 1B needs ~4GB, 400M needs ~2GB
- **Best for:** Highest-quality local TTS, privacy-sensitive applications, production narration

#### Chatterbox (resemble-ai/chatterbox)

The first open-source model with a dedicated emotion exaggeration parameter. One slider takes output from monotone newsreader to dramatic podcast host. Leading HuggingFace trending models in late 2025.

- **Architecture:** Custom 350M parameter model with emotion conditioning
- **Model size:** 350M params (~1.5GB VRAM)
- **Streaming latency:** ~300ms first-chunk
- **Voice cloning:** 5-second reference clip (zero-shot)
- **Emotion:** Explicit exaggeration slider (0.0 = flat monotone, 1.0 = maximum drama)
- **Languages:** 23 languages supported
- **License:** MIT — fully open, commercial use allowed
- **Watermarking:** Built-in audio watermarking (can be disabled)
- **Best for:** Emotion-controlled narration, multilingual content, podcast personality

#### Bark (suno-ai/bark)

Unique among TTS models — Bark generates not just speech but non-verbal audio: laughter, sighing, throat-clearing, background ambience, and even simple music. Less controllable than purpose-built TTS but uniquely expressive for creative content.

- **Architecture:** Transformer-based, multi-codebook audio generation
- **Streaming:** Not natively streaming (generates full clips)
- **Voice cloning:** Speaker prompts (less precise than Orpheus/Chatterbox)
- **Emotion:** Implicit via text prompts ([laughs], [sighs], [clears throat])
- **Languages:** 13+ languages
- **License:** MIT — fully open, commercial use allowed
- **VRAM:** ~6GB for full model
- **Best for:** Creative audio with sound effects, expressive storytelling, demo/prototype content

#### Coqui TTS / XTTS-v2

The widest language coverage of any TTS model — over 1,100 languages. XTTS-v2 delivers high-quality multi-lingual speech with just a 6-second voice cloning reference.

- **Architecture:** GPT-style autoregressive + VQ-VAE
- **Model size:** ~1.6B params
- **Voice cloning:** 6-second reference clip (zero-shot)
- **Languages:** 1,100+ languages (XTTS-v2 supports 17 well, Coqui TTS covers 1,100+)
- **License:** Coqui Public Model License (CPML) — **non-commercial** for XTTS-v2 model weights. The code is MPL-2.0.
- **VRAM:** ~4-6GB
- **Best for:** Multilingual/minority language content, research, non-commercial projects

> **License warning:** XTTS-v2 model weights are under CPML (non-commercial). For commercial use, train your own model with the Coqui TTS framework or use a different provider.

#### Parler TTS (HuggingFace)

The best developer experience of the open-source options. Clean Python API, solid documentation, and straightforward integration. Describe the voice you want in natural language ("a warm female voice with a slight British accent").

- **Architecture:** Encoder-decoder with text-described voice conditioning
- **Voice control:** Natural language voice description (no reference clip needed)
- **Languages:** English primary, multilingual variants available
- **License:** Apache 2.0 — fully open, commercial use allowed
- **VRAM:** ~4GB
- **Best for:** Quick prototyping, simple integrations, developers who want clean DX

---

### Cloud API Providers

#### ElevenLabs

The industry benchmark for TTS quality. Consistently rated highest in blind listening tests. Offers instant voice cloning, a growing library of pre-made voices, and true real-time streaming.

- **Quality:** Best-in-class (reference standard)
- **Free tier:** 10,000 credits/month (~10 minutes of audio)
- **Pricing:** Starter $5/mo (30k credits), Creator $22/mo (100k credits), Pro $99/mo (500k credits)
- **Per-character cost:** $0.12-$0.30 per 1,000 characters (varies by tier)
- **Voice cloning:** Instant (30s clip) or Professional (30+ minutes for custom model)
- **Streaming:** Yes, WebSocket-based real-time streaming
- **Languages:** 29+ languages
- **Emotion:** Automatic from text context + style controls
- **Best for:** Production-quality content, commercial podcasts, highest fidelity requirements

#### Google Cloud TTS

Reliable, well-documented, and cost-effective for high volume. WaveNet and Neural2 voices sound natural. Strong SSML support for fine-grained control over pronunciation, pauses, and emphasis.

- **Quality:** Very good (WaveNet/Neural2), good (Standard)
- **Pricing:** Standard: $4/1M chars, WaveNet: $16/1M chars, Neural2: $16/1M chars
- **Free tier:** 1M Standard chars/mo, 1M WaveNet chars/mo (first 90 days), then Standard only
- **SSML:** Full SSML 1.0 support with custom extensions
- **Streaming:** gRPC streaming supported
- **Languages:** 50+ languages, 220+ voices
- **Voice cloning:** Custom Voice (enterprise only, requires 2+ hours of training data)
- **Best for:** High-volume production, GCP-native apps, SSML-heavy workflows

#### Azure AI Speech

Microsoft's offering stands out for its per-word timestamp feature — essential for subtitle generation, karaoke-style highlighting, and precise audio-text alignment. The HD V2 tier adds context-aware emotion that reads surrounding sentences to modulate delivery.

- **Quality:** Excellent (Neural), Best-in-class for context-aware emotion (HD V2)
- **Pricing:** Neural: $15-16/1M chars, HD V2: $30/1M chars
- **Free tier:** 500K chars/mo (Neural)
- **Unique feature:** Per-word timestamps (viseme + word boundary events)
- **Streaming:** Real-time streaming via WebSocket
- **Languages:** 60+ languages, 400+ voices
- **Voice cloning:** Personal Voice (requires consent + training data)
- **Emotion:** HD V2 reads context to auto-select emotion, plus explicit SSML styles
- **Best for:** Subtitle generation, word-level sync, Azure-native apps, context-aware emotion

---

### Full Comparison Table

| Provider | Quality | Cost | Latency | Languages | Voice Cloning | Emotion Control | License | Best For |
|----------|---------|------|---------|-----------|---------------|-----------------|---------|----------|
| **Orpheus TTS** | Excellent | Free (GPU cost) | ~200ms stream | English+ | Zero-shot | From context | MIT | Best local quality |
| **Chatterbox** | Very Good | Free (GPU cost) | ~300ms stream | 23 | 5-sec clip | Slider (0-1) | MIT | Emotion control |
| **Bark** | Good | Free (GPU cost) | ~2-5s full clip | 13+ | Speaker prompts | Text tags | MIT | Non-speech sounds |
| **Coqui XTTS-v2** | Very Good | Free (GPU cost) | ~500ms | 1,100+ | 6-sec clip | Limited | CPML (non-commercial) | Most languages |
| **Parler TTS** | Good | Free (GPU cost) | ~400ms | English+ | NL description | NL description | Apache 2.0 | Best DX |
| **ElevenLabs** | Best | $0.12-0.30/1k chars | ~150ms stream | 29+ | Instant (30s) | Auto + styles | Proprietary | Production quality |
| **Google Cloud** | Very Good | $4-16/1M chars | ~200ms gRPC | 50+ | Enterprise only | SSML | Proprietary | High volume, SSML |
| **Azure Speech** | Excellent | $15-30/1M chars | ~200ms WS | 60+ | Personal Voice | HD V2 context | Proprietary | Word timestamps |

---

## 2. Decision Tree

Use this flowchart to select your provider:

```
START: What's your primary constraint?
  |
  +-- Budget = $0 (must be free)
  |     |
  |     +-- Need best quality? ---------> Orpheus TTS (3B model)
  |     +-- Need emotion control? ------> Chatterbox (emotion slider)
  |     +-- Need sound effects too? ----> Bark
  |     +-- Need 100+ languages? -------> Coqui TTS (check CPML license)
  |     +-- Need fastest setup? --------> Parler TTS
  |
  +-- Budget available (cloud OK)
  |     |
  |     +-- Need absolute best quality? -----> ElevenLabs
  |     +-- Need per-word timestamps? -------> Azure HD V2
  |     +-- Need cheapest per-character? ----> Google Cloud TTS (Standard)
  |     +-- Need context-aware emotion? -----> Azure HD V2
  |     +-- Already on GCP? -----------------> Google Cloud TTS
  |     +-- Already on Azure? ---------------> Azure AI Speech
  |
  +-- Privacy/compliance (no cloud)
  |     |
  |     +-- Commercial use? -----> Orpheus (MIT) or Chatterbox (MIT)
  |     +-- Research/non-profit? -> Coqui XTTS-v2 (best multilingual)
  |
  +-- Edge/mobile deployment
        |
        +-- Orpheus 150M or 400M (smallest footprint)
```

### Quick Decision Summary

| Scenario | Recommendation |
|----------|---------------|
| Best quality, budget available | ElevenLabs |
| Best open-source quality | Orpheus TTS (3B) |
| Need emotion control slider | Chatterbox |
| Non-speech sounds (laughter, sighs) | Bark |
| 100% local/private, commercial | Orpheus or Chatterbox (MIT) |
| Cheapest cloud API | Google Cloud TTS Standard ($4/1M chars) |
| Per-word timestamps for subtitles | Azure HD V2 |
| Most language coverage | Coqui TTS (1,100+) |
| Fastest prototype / best DX | Parler TTS |
| Edge/mobile deployment | Orpheus 150M-400M |

---

## 3. TypeScript Integration Examples

### 3a. ElevenLabs (REST API with Streaming)

```typescript
import { Readable } from 'stream';
import { writeFile } from 'fs/promises';

interface ElevenLabsConfig {
  apiKey: string;
  voiceId: string;
  modelId?: string; // 'eleven_turbo_v2_5' for speed, 'eleven_multilingual_v2' for quality
  stability?: number; // 0.0-1.0 (lower = more expressive)
  similarityBoost?: number; // 0.0-1.0 (higher = closer to original voice)
}

/**
 * Stream audio from ElevenLabs TTS API.
 * Returns a Buffer of MP3 audio data.
 */
async function generateSpeech(
  text: string,
  config: ElevenLabsConfig
): Promise<Buffer> {
  const {
    apiKey,
    voiceId,
    modelId = 'eleven_multilingual_v2',
    stability = 0.5,
    similarityBoost = 0.75,
  } = config;

  const response = await fetch(
    `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}/stream`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'xi-api-key': apiKey,
      },
      body: JSON.stringify({
        text,
        model_id: modelId,
        voice_settings: {
          stability,
          similarity_boost: similarityBoost,
        },
      }),
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`ElevenLabs API error ${response.status}: ${error}`);
  }

  // Collect streamed chunks into a single buffer
  const chunks: Uint8Array[] = [];
  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }

  return Buffer.concat(chunks);
}

/**
 * Stream ElevenLabs audio directly to a writable stream (e.g., HTTP response).
 * Useful for real-time playback without buffering the entire file.
 */
async function streamSpeechToResponse(
  text: string,
  config: ElevenLabsConfig,
  output: NodeJS.WritableStream
): Promise<void> {
  const { apiKey, voiceId, modelId = 'eleven_turbo_v2_5' } = config;

  const response = await fetch(
    `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}/stream`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'xi-api-key': apiKey,
      },
      body: JSON.stringify({
        text,
        model_id: modelId,
        voice_settings: { stability: 0.5, similarity_boost: 0.75 },
        // Optimize for streaming latency
        optimize_streaming_latency: 3, // 0-4, higher = lower latency but slight quality trade-off
      }),
    }
  );

  if (!response.ok) {
    throw new Error(`ElevenLabs stream error: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    output.write(value);
  }

  output.end();
}

// --- Usage ---
async function main() {
  const config: ElevenLabsConfig = {
    apiKey: process.env.ELEVENLABS_API_KEY!,
    voiceId: 'pNInz6obpgDQGcFmaJgB', // "Adam" pre-made voice
    modelId: 'eleven_multilingual_v2',
    stability: 0.4, // More expressive
    similarityBoost: 0.8,
  };

  const audioBuffer = await generateSpeech(
    'Welcome to our podcast. Today we explore the intersection of faith and technology.',
    config
  );

  await writeFile('output.mp3', audioBuffer);
  console.log(`Generated ${audioBuffer.length} bytes of audio`);
}
```

### 3b. Orpheus TTS (Local via Python Subprocess)

Orpheus runs as a Python process. From Node.js/TypeScript, call it via subprocess. This keeps your main app in TypeScript while leveraging the Python ML ecosystem.

```typescript
import { spawn } from 'child_process';
import { writeFile, readFile, unlink } from 'fs/promises';
import { randomUUID } from 'crypto';
import path from 'path';

type OrpheusModelSize = '3B' | '1B' | '400M' | '150M';

interface OrpheusConfig {
  pythonPath?: string; // Path to Python with orpheus installed
  modelsDir?: string; // Where Orpheus models are stored
  outputDir?: string; // Temp directory for audio files
}

/**
 * Generate speech using local Orpheus TTS via Python subprocess.
 * Requires: pip install orpheus-tts torch
 *
 * @param text - The text to synthesize
 * @param modelSize - Model variant: '3B' (best), '1B', '400M', '150M' (fastest)
 * @param config - Path configuration
 * @returns Buffer containing WAV audio data
 */
async function generateLocalTTS(
  text: string,
  modelSize: OrpheusModelSize = '3B',
  config: OrpheusConfig = {}
): Promise<Buffer> {
  const {
    pythonPath = 'python',
    outputDir = '/tmp/orpheus-output',
  } = config;

  const outputFile = path.join(outputDir, `orpheus-${randomUUID()}.wav`);

  // Model name mapping
  const modelMap: Record<OrpheusModelSize, string> = {
    '3B': 'canopyai/Orpheus-TTS-0.1-3B',
    '1B': 'canopyai/Orpheus-TTS-0.1-1B',
    '400M': 'canopyai/Orpheus-TTS-0.1-400M',
    '150M': 'canopyai/Orpheus-TTS-0.1-150M',
  };

  // Python script reads text from stdin to avoid shell injection
  const pythonScript = `
import sys
import torch
from orpheus_tts import OrpheusModel

text = sys.stdin.read()
model = OrpheusModel(model_name="${modelMap[modelSize]}")
audio = model.generate_speech(
    prompt=text,
    voice="tara",  # Default voice; options: tara, leah, jess, leo, dan, mia, zac
)
audio.export("${outputFile.replace(/\\/g, '/')}", format="wav")
print("OK")
`;

  return new Promise((resolve, reject) => {
    const proc = spawn(pythonPath, ['-c', pythonScript], {
      timeout: 120_000, // 2 minute timeout for large texts
    });
    // Pass text via stdin to avoid injection
    proc.stdin.write(text);
    proc.stdin.end();

    let stderr = '';
    proc.stderr.on('data', (data) => { stderr += data.toString(); });

    proc.on('close', async (code) => {
      if (code !== 0) {
        reject(new Error(`Orpheus TTS failed (exit ${code}): ${stderr}`));
        return;
      }

      try {
        const audioBuffer = await readFile(outputFile);
        await unlink(outputFile); // Clean up temp file
        resolve(audioBuffer);
      } catch (err) {
        reject(new Error(`Failed to read Orpheus output: ${err}`));
      }
    });

    proc.on('error', (err) => {
      reject(new Error(`Failed to spawn Python: ${err.message}`));
    });
  });
}

/**
 * Generate speech with a cloned voice using a reference audio clip.
 */
async function generateClonedVoiceTTS(
  text: string,
  referenceAudioPath: string,
  modelSize: OrpheusModelSize = '3B',
  config: OrpheusConfig = {}
): Promise<Buffer> {
  const { pythonPath = 'python', outputDir = '/tmp/orpheus-output' } = config;
  const outputFile = path.join(outputDir, `orpheus-clone-${randomUUID()}.wav`);

  const modelMap: Record<OrpheusModelSize, string> = {
    '3B': 'canopyai/Orpheus-TTS-0.1-3B',
    '1B': 'canopyai/Orpheus-TTS-0.1-1B',
    '400M': 'canopyai/Orpheus-TTS-0.1-400M',
    '150M': 'canopyai/Orpheus-TTS-0.1-150M',
  };

  const pythonScript = `
import sys, torch
from orpheus_tts import OrpheusModel

text = sys.stdin.read()
model = OrpheusModel(model_name="${modelMap[modelSize]}")
audio = model.generate_speech(
    prompt=text,
    reference_audio="${referenceAudioPath.replace(/\\/g, '/')}",
)
audio.export("${outputFile.replace(/\\/g, '/')}", format="wav")
print("OK")
`;

  return new Promise((resolve, reject) => {
    const proc = spawn(pythonPath, ['-c', pythonScript], { timeout: 120_000 });
    proc.stdin.write(text);
    proc.stdin.end();
    let stderr = '';
    proc.stderr.on('data', (data) => { stderr += data.toString(); });

    proc.on('close', async (code) => {
      if (code !== 0) {
        reject(new Error(`Orpheus clone TTS failed (exit ${code}): ${stderr}`));
        return;
      }
      try {
        const buf = await readFile(outputFile);
        await unlink(outputFile);
        resolve(buf);
      } catch (err) {
        reject(new Error(`Failed to read output: ${err}`));
      }
    });

    proc.on('error', (err) => reject(new Error(`Spawn failed: ${err.message}`)));
  });
}

// --- Usage ---
async function main() {
  // Draft quality (fast) — use 400M for iteration
  const draftAudio = await generateLocalTTS(
    'Testing the Orpheus text-to-speech engine.',
    '400M'
  );
  await writeFile('draft.wav', draftAudio);

  // Final quality — use 3B for production
  const finalAudio = await generateLocalTTS(
    'Welcome to our podcast on faith and technology.',
    '3B'
  );
  await writeFile('final.wav', finalAudio);

  console.log(`Draft: ${draftAudio.length} bytes, Final: ${finalAudio.length} bytes`);
}
```

### 3c. Google Cloud TTS (with SSML)

```typescript
import { TextToSpeechClient, protos } from '@google-cloud/text-to-speech';
import { writeFile } from 'fs/promises';

type AudioEncoding = protos.google.cloud.texttospeech.v1.AudioEncoding;

interface GoogleTTSConfig {
  languageCode?: string;
  voiceName?: string; // e.g., 'en-US-Neural2-D' (male), 'en-US-Neural2-F' (female)
  audioEncoding?: 'MP3' | 'LINEAR16' | 'OGG_OPUS';
  speakingRate?: number; // 0.25 to 4.0 (1.0 = normal)
  pitch?: number; // -20.0 to 20.0 semitones
}

/**
 * Generate speech from SSML using Google Cloud TTS.
 * Requires: npm install @google-cloud/text-to-speech
 * Auth: GOOGLE_APPLICATION_CREDENTIALS env var pointing to service account JSON
 */
async function googleTTS(
  ssml: string,
  config: GoogleTTSConfig = {}
): Promise<Buffer> {
  const {
    languageCode = 'en-US',
    voiceName = 'en-US-Neural2-D',
    audioEncoding = 'MP3',
    speakingRate = 1.0,
    pitch = 0,
  } = config;

  const client = new TextToSpeechClient();

  const encodingMap: Record<string, number> = {
    'MP3': 2,       // protos.google.cloud.texttospeech.v1.AudioEncoding.MP3
    'LINEAR16': 1,  // LINEAR16 (WAV)
    'OGG_OPUS': 3,  // OGG_OPUS
  };

  const [response] = await client.synthesizeSpeech({
    input: { ssml },
    voice: {
      languageCode,
      name: voiceName,
    },
    audioConfig: {
      audioEncoding: encodingMap[audioEncoding] as AudioEncoding,
      speakingRate,
      pitch,
      // Enable EBU R128 loudness normalization for consistent output
      effectsProfileId: ['headphone-class-device'],
    },
  });

  if (!response.audioContent) {
    throw new Error('No audio content in Google TTS response');
  }

  return Buffer.from(response.audioContent as Uint8Array);
}

/**
 * Build SSML markup from structured content.
 * SSML gives fine-grained control over pauses, emphasis, and pronunciation.
 */
function buildSSML(segments: SSMLSegment[]): string {
  const inner = segments.map((seg) => {
    switch (seg.type) {
      case 'text':
        return seg.text;
      case 'pause':
        return `<break time="${seg.duration || '500ms'}"/>`;
      case 'emphasis':
        return `<emphasis level="${seg.level || 'moderate'}">${seg.text}</emphasis>`;
      case 'prosody':
        return `<prosody rate="${seg.rate || 'medium'}" pitch="${seg.pitch || 'medium'}">${seg.text}</prosody>`;
      case 'say-as':
        return `<say-as interpret-as="${seg.interpretAs}">${seg.text}</say-as>`;
      default:
        return seg.text;
    }
  }).join('\n');

  return `<speak>\n${inner}\n</speak>`;
}

interface SSMLSegment {
  type: 'text' | 'pause' | 'emphasis' | 'prosody' | 'say-as';
  text?: string;
  duration?: string; // For pause: '250ms', '1s', '2s'
  level?: 'reduced' | 'moderate' | 'strong'; // For emphasis
  rate?: 'x-slow' | 'slow' | 'medium' | 'fast' | 'x-fast'; // For prosody
  pitch?: 'x-low' | 'low' | 'medium' | 'high' | 'x-high'; // For prosody
  interpretAs?: 'date' | 'time' | 'telephone' | 'cardinal' | 'ordinal' | 'spell-out'; // For say-as
}

// --- Usage ---
async function main() {
  // Simple text
  const simpleAudio = await googleTTS(
    '<speak>Welcome to our podcast on faith and technology.</speak>'
  );
  await writeFile('simple.mp3', simpleAudio);

  // Rich SSML with pauses, emphasis, and prosody
  const ssml = buildSSML([
    { type: 'prosody', text: 'Welcome to Ministry Tech Weekly.', rate: 'slow', pitch: 'low' },
    { type: 'pause', duration: '750ms' },
    { type: 'text', text: 'Today we explore how churches are using' },
    { type: 'emphasis', text: 'artificial intelligence', level: 'strong' },
    { type: 'text', text: 'to reach their communities.' },
    { type: 'pause', duration: '1s' },
    { type: 'prosody', text: "Let's dive in.", rate: 'medium', pitch: 'high' },
  ]);

  const richAudio = await googleTTS(ssml, {
    voiceName: 'en-US-Neural2-D', // Deep male voice
    speakingRate: 0.95,
  });
  await writeFile('rich-ssml.mp3', richAudio);

  console.log(`Simple: ${simpleAudio.length}B, Rich: ${richAudio.length}B`);
}
```

---

## 4. Multi-Speaker Podcast Pattern

Generate a two-speaker podcast where different TTS voices handle Host vs. Guest roles, with natural pauses and transitions composed via FFmpeg.

### Architecture

```
Script (JSON)
  |
  v
[Parse turns] --> Host voice (Voice A) --> audio_001.wav
                  Guest voice (Voice B) --> audio_002.wav
                  Host voice (Voice A) --> audio_003.wav
                  ...
  |
  v
[Generate silence segments] --> silence_500ms.wav, silence_1000ms.wav
  |
  v
[FFmpeg concat] --> raw_podcast.wav
  |
  v
[Post-processing] --> final_podcast.mp3
  (See audio-enhancement-pipeline.md)
```

### TypeScript Implementation

```typescript
import { execFile } from 'child_process';
import { writeFile, readFile, unlink, mkdir } from 'fs/promises';
import { promisify } from 'util';
import path from 'path';
import { randomUUID } from 'crypto';

const execFileAsync = promisify(execFile);

// --- Types ---

interface PodcastTurn {
  speaker: 'host' | 'guest';
  text: string;
  emotion?: number; // 0.0-1.0 for Chatterbox, ignored for others
  pauseAfter?: number; // Milliseconds of silence after this turn
}

interface PodcastConfig {
  hostVoice: VoiceConfig;
  guestVoice: VoiceConfig;
  defaultPause: number; // Default pause between turns (ms)
  outputPath: string;
  tempDir?: string;
}

interface VoiceConfig {
  provider: 'elevenlabs' | 'orpheus' | 'chatterbox' | 'google';
  voiceId: string; // Voice ID or model path
  // Provider-specific options
  apiKey?: string;
  modelSize?: '3B' | '1B' | '400M' | '150M';
  emotion?: number;
  speakingRate?: number;
}

// --- Podcast Generator ---

async function generatePodcast(
  script: PodcastTurn[],
  config: PodcastConfig
): Promise<string> {
  const tempDir = config.tempDir || `/tmp/podcast-${randomUUID()}`;
  await mkdir(tempDir, { recursive: true });

  const audioSegments: string[] = [];
  let segmentIndex = 0;

  console.log(`Generating ${script.length} segments...`);

  for (const turn of script) {
    // 1. Generate speech for this turn
    const voiceConfig = turn.speaker === 'host' ? config.hostVoice : config.guestVoice;
    const speechFile = path.join(tempDir, `seg_${String(segmentIndex).padStart(4, '0')}_speech.wav`);

    const audioBuffer = await generateTTSForProvider(turn.text, voiceConfig, turn.emotion);
    await writeFile(speechFile, audioBuffer);
    audioSegments.push(speechFile);
    segmentIndex++;

    // 2. Add pause after this turn
    const pauseDuration = turn.pauseAfter ?? config.defaultPause;
    if (pauseDuration > 0) {
      const silenceFile = path.join(tempDir, `seg_${String(segmentIndex).padStart(4, '0')}_silence.wav`);
      await generateSilence(pauseDuration, silenceFile);
      audioSegments.push(silenceFile);
      segmentIndex++;
    }

    console.log(`  [${segmentIndex}/${script.length * 2}] ${turn.speaker}: "${turn.text.slice(0, 50)}..."`);
  }

  // 3. Concatenate all segments with FFmpeg
  const concatListFile = path.join(tempDir, 'concat_list.txt');
  const concatContent = audioSegments.map((f) => `file '${f}'`).join('\n');
  await writeFile(concatListFile, concatContent);

  const rawOutput = path.join(tempDir, 'raw_podcast.wav');
  await execFileAsync('ffmpeg', [
    '-y',
    '-f', 'concat',
    '-safe', '0',
    '-i', concatListFile,
    '-c:a', 'pcm_s16le',
    '-ar', '44100',
    '-ac', '1',
    rawOutput,
  ]);

  // 4. Post-process: normalize loudness (EBU R128) and export as MP3
  await execFileAsync('ffmpeg', [
    '-y',
    '-i', rawOutput,
    '-af', [
      'loudnorm=I=-16:TP=-1.5:LRA=11', // EBU R128 broadcast standard
      'aresample=44100',                 // Consistent sample rate
    ].join(','),
    '-c:a', 'libmp3lame',
    '-b:a', '192k',
    config.outputPath,
  ]);

  // 5. Clean up temp files
  for (const f of audioSegments) {
    await unlink(f).catch(() => {});
  }
  await unlink(concatListFile).catch(() => {});
  await unlink(rawOutput).catch(() => {});

  console.log(`Podcast saved to: ${config.outputPath}`);
  return config.outputPath;
}

/**
 * Route TTS generation to the configured provider.
 */
async function generateTTSForProvider(
  text: string,
  voice: VoiceConfig,
  emotionOverride?: number
): Promise<Buffer> {
  switch (voice.provider) {
    case 'elevenlabs':
      return generateSpeech(text, {
        apiKey: voice.apiKey!,
        voiceId: voice.voiceId,
      });

    case 'orpheus':
      return generateLocalTTS(text, voice.modelSize || '3B');

    case 'chatterbox':
      return generateChatterboxTTS(text, voice.voiceId, emotionOverride ?? voice.emotion ?? 0.5);

    case 'google':
      return googleTTS(`<speak>${text}</speak>`, { voiceName: voice.voiceId });

    default:
      throw new Error(`Unknown TTS provider: ${voice.provider}`);
  }
}

/**
 * Generate silence of a given duration using FFmpeg.
 */
async function generateSilence(durationMs: number, outputPath: string): Promise<void> {
  const durationSec = durationMs / 1000;
  await execFileAsync('ffmpeg', [
    '-y',
    '-f', 'lavfi',
    '-i', `anullsrc=r=44100:cl=mono`,
    '-t', String(durationSec),
    '-c:a', 'pcm_s16le',
    outputPath,
  ]);
}

/**
 * Generate speech with Chatterbox (emotion slider).
 */
async function generateChatterboxTTS(
  text: string,
  referenceAudioPath: string,
  emotion: number
): Promise<Buffer> {
  const outputFile = `/tmp/chatterbox-${randomUUID()}.wav`;

  const pythonScript = `
import sys, torch
from chatterbox.tts import ChatterboxTTS

text = sys.stdin.read()
model = ChatterboxTTS.from_pretrained(device="cuda" if torch.cuda.is_available() else "cpu")
audio = model.generate(
    text=text,
    audio_prompt_path="${referenceAudioPath.replace(/\\/g, '/')}",
    exaggeration=${emotion},
)
import torchaudio
torchaudio.save("${outputFile}", audio, model.sr)
print("OK")
`;

  return new Promise((resolve, reject) => {
    const proc = spawn('python', ['-c', pythonScript], { timeout: 120_000 });
    proc.stdin.write(text);
    proc.stdin.end();
    let stderr = '';
    proc.stderr.on('data', (d: Buffer) => { stderr += d.toString(); });
    proc.on('close', async (code: number) => {
      if (code !== 0) return reject(new Error(`Chatterbox failed: ${stderr}`));
      try {
        const buf = await readFile(outputFile);
        await unlink(outputFile);
        resolve(buf);
      } catch (e) { reject(e); }
    });
    proc.on('error', (e: Error) => reject(e));
  });
}

// --- Example Podcast Script ---

async function main() {
  const script: PodcastTurn[] = [
    {
      speaker: 'host',
      text: 'Welcome back to Ministry Tech Weekly. I am your host, and today we have an incredible guest joining us.',
      pauseAfter: 800,
    },
    {
      speaker: 'host',
      text: 'We are going to talk about how small churches can leverage AI tools without breaking the budget.',
      pauseAfter: 1200,
    },
    {
      speaker: 'guest',
      text: 'Thanks for having me. This is a topic close to my heart. I have been working with rural congregations for the past five years.',
      emotion: 0.6, // Warm, enthusiastic
      pauseAfter: 600,
    },
    {
      speaker: 'host',
      text: 'So let us start with the basics. What is the first AI tool you recommend to a church with zero tech budget?',
      pauseAfter: 1000,
    },
    {
      speaker: 'guest',
      text: 'Great question. I always say start with transcription. Record your sermons, transcribe them with a free tool, and now you have written content for your website, social media, and email newsletters.',
      emotion: 0.7, // Passionate
      pauseAfter: 500,
    },
    {
      speaker: 'host',
      text: 'That is such a practical starting point. One recording becomes five pieces of content.',
      pauseAfter: 1500,
    },
  ];

  await generatePodcast(script, {
    hostVoice: {
      provider: 'orpheus',
      voiceId: 'leo', // Deep male voice
      modelSize: '3B',
    },
    guestVoice: {
      provider: 'chatterbox',
      voiceId: '/path/to/guest-reference-5sec.wav',
      emotion: 0.5,
    },
    defaultPause: 700,
    outputPath: './ministry-tech-weekly-ep1.mp3',
  });
}
```

### Key Patterns for Natural-Sounding Podcasts

1. **Vary pause lengths:** Short (400-600ms) within a thought, medium (700-1000ms) between topics, long (1200-1500ms) for dramatic effect or topic transitions.

2. **Match voice characteristics:** Pair voices with complementary tones — a deep, steady host with a warmer, more expressive guest.

3. **Use Chatterbox emotion strategically:**
   - `emotion: 0.3` — Calm, informational (reading statistics, facts)
   - `emotion: 0.5` — Conversational (default for most dialogue)
   - `emotion: 0.7` — Enthusiastic (key points, exciting reveals)
   - `emotion: 0.9` — Very dramatic (use sparingly for climactic moments)

4. **Post-process with audio-enhancement-pipeline.md:** After concatenation, run the full enhancement pipeline (noise reduction, loudness normalization, compression) for broadcast-ready output.

---

## 5. Quality Tips

### Audio Normalization (Critical)

Always normalize TTS output to EBU R128 loudness standard. Different providers output at wildly different levels — mixing them without normalization creates jarring volume jumps.

```bash
# Normalize a single file to -16 LUFS (podcast standard)
ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 44100 output.wav

# Two-pass normalization (more accurate, recommended for final output)
# Pass 1: Measure
ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null /dev/null 2>&1

# Pass 2: Apply measured values (use values from pass 1 output)
ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=-23.5:measured_LRA=7.2:measured_TP=-3.1:measured_thresh=-34.2 output.wav
```

### Pacing and Pauses

- Insert 200-400ms silence between sentences for natural breathing rhythm
- Insert 600-1000ms between paragraphs or topic changes
- For dramatic effect, use 1500-2000ms pauses before key reveals
- Never go below 150ms between sentences — it sounds rushed and robotic

### Provider-Specific Tips

**Orpheus TTS:**
- Use 3B model for all final/published output — the quality gap vs 1B is significant
- Use 400M model for drafts, previews, and rapid iteration (4x faster)
- 150M is viable for real-time chat applications where latency matters more than quality
- Pre-load the model once and reuse — cold start takes 10-15 seconds on consumer GPUs
- The model reads emotion from text context. Writing "excited" or "sadly" in the text naturally affects prosody

**Chatterbox:**
- `emotion: 0.3` — News anchors, formal narration, educational content
- `emotion: 0.5` — Default conversational tone, general-purpose
- `emotion: 0.7` — Casual podcast, storytelling, engaging narration
- `emotion: 0.9-1.0` — Use sparingly: dramatic readings, voice acting, emphasis
- The 5-second voice clone reference should be clean audio (no background noise, no music)
- Built-in watermarking is on by default — disable explicitly if not needed

**Bark:**
- Use text tags for non-speech: `[laughs]`, `[sighs]`, `[clears throat]`, `[music]`
- Generates complete clips (not streaming) — best for short segments
- Quality varies between runs — generate 2-3 takes and pick the best
- Not suitable for long-form narration (use Orpheus or ElevenLabs instead)

**ElevenLabs:**
- Lower `stability` (0.2-0.4) for more expressive, varied speech
- Higher `stability` (0.7-0.9) for consistent, professional narration
- Use `eleven_turbo_v2_5` model for speed, `eleven_multilingual_v2` for best quality
- Voice cloning: Instant clone (30s clip) is good; Professional clone (30+ min) is excellent
- Monitor credit usage — credits are consumed per character, not per request

**Google Cloud TTS:**
- Always use Neural2 or WaveNet voices (Standard voices sound robotic)
- SSML `<break>` tags give precise pause control: `<break time="750ms"/>`
- Use `effectsProfileId: ['headphone-class-device']` for optimized podcast output
- Batch requests for cost efficiency — the API charges per character, and each request has overhead

**Azure AI Speech:**
- HD V2 tier reads surrounding context to modulate emotion automatically
- Word boundary events enable subtitle generation with per-word timestamps
- Use SSML `<mstts:express-as>` for explicit emotion: `style="cheerful"`, `style="sad"`, `style="angry"`

### Cross-Reference

For post-processing your TTS output, see the companion skill:
- **audio-enhancement-pipeline.md** — Noise reduction, loudness normalization, compression, format conversion pipeline
- **ffmpeg-command-generator.md** — FFmpeg commands for any audio/video transformation
- **content-repurposing-pipeline.md** — Turn generated audio into social media clips, transcripts, and blog posts

---

## 6. Cost Calculator

### Cost Per Minute of Generated Speech

Average speaking rate: ~150 words/minute, ~750 characters/minute.

| Provider | Cost per 1k chars | Cost per minute | Cost for 30-min episode |
|----------|-------------------|-----------------|-------------------------|
| **Orpheus (local)** | ~$0.01 (electricity) | ~$0.008 | ~$0.24 |
| **Chatterbox (local)** | ~$0.01 (electricity) | ~$0.008 | ~$0.24 |
| **Bark (local)** | ~$0.01 (electricity) | ~$0.008 | ~$0.24 |
| **Parler TTS (local)** | ~$0.01 (electricity) | ~$0.008 | ~$0.24 |
| **ElevenLabs Free** | $0.00 | $0.00 | Free (10 min/mo limit) |
| **ElevenLabs Starter** | ~$0.17 | ~$0.13 | ~$3.75 |
| **ElevenLabs Creator** | ~$0.22 | ~$0.17 | ~$5.00 |
| **ElevenLabs Pro** | ~$0.20 | ~$0.15 | ~$4.50 |
| **Google Cloud Standard** | $0.004 | ~$0.003 | ~$0.09 |
| **Google Cloud WaveNet** | $0.016 | ~$0.012 | ~$0.36 |
| **Google Cloud Neural2** | $0.016 | ~$0.012 | ~$0.36 |
| **Azure Neural** | $0.016 | ~$0.012 | ~$0.36 |
| **Azure HD V2** | $0.030 | ~$0.023 | ~$0.68 |

### Local GPU Electricity Cost Estimate

```
Formula: GPU TDP (watts) * generation_time (hours) * electricity_rate ($/kWh)

Example: Orpheus 3B on RTX 4090 (450W TDP at ~60% utilization)
- 30 minutes of speech ≈ 15 minutes generation time (2:1 real-time ratio)
- Power: 270W * 0.25 hours = 0.0675 kWh
- Cost: 0.0675 * $0.12/kWh = $0.008

Example: Chatterbox on RTX 3060 (170W TDP at ~80% utilization)
- 30 minutes of speech ≈ 25 minutes generation time
- Power: 136W * 0.42 hours = 0.057 kWh
- Cost: 0.057 * $0.12/kWh = $0.007
```

### Cost Comparison: Weekly Podcast (30 minutes)

| Approach | Monthly Cost | Annual Cost | Notes |
|----------|-------------|-------------|-------|
| **Orpheus 3B (local, RTX 4090)** | ~$1.00 | ~$12 | GPU amortization not included |
| **Chatterbox (local, RTX 3060)** | ~$1.00 | ~$12 | GPU amortization not included |
| **Google Cloud Neural2** | ~$1.44 | ~$17 | Most cost-effective cloud |
| **Azure Neural** | ~$1.44 | ~$17 | Add $1.24/mo for HD V2 |
| **ElevenLabs Starter** | $5.00 | $60 | Fixed monthly (may exceed limits) |
| **ElevenLabs Pro** | $99.00 | $1,188 | Unlimited for heavy use |

### Break-Even: Local GPU vs. Cloud API

```
Break-even calculation: When does buying a GPU pay for itself?

RTX 4090 ($1,600) vs. ElevenLabs Pro ($99/mo):
  Break-even: $1,600 / $99 = ~16 months
  After 16 months, local is essentially free (just electricity)

RTX 3060 ($300) vs. Google Cloud Neural2 ($1.44/mo):
  Break-even: $300 / $1.44 = ~208 months (17+ years)
  Google Cloud is so cheap that a dedicated GPU rarely makes sense for cost alone.
  But: privacy, latency, and offline capability are valid reasons to go local.
```

### Quick Estimation Formula

```
Characters in text ≈ words * 5
Cost = (characters / 1000) * provider_rate_per_1k_chars

Example: 3,000-word blog post narration
  Characters: 3,000 * 5 = 15,000
  ElevenLabs Starter: (15,000 / 1000) * $0.17 = $2.55
  Google Neural2: (15,000 / 1000) * $0.016 = $0.24
  Azure HD V2: (15,000 / 1000) * $0.030 = $0.45
```

---

## 7. Advanced Patterns

### Hybrid Approach: Draft Local, Publish Cloud

Use cheap/fast local models for iteration, then generate final output with the highest-quality provider.

```typescript
interface HybridTTSConfig {
  draftProvider: VoiceConfig;  // Fast, local — for review
  finalProvider: VoiceConfig;  // Best quality — for publishing
}

async function hybridGenerate(
  text: string,
  config: HybridTTSConfig,
  isFinal: boolean = false
): Promise<Buffer> {
  const provider = isFinal ? config.finalProvider : config.draftProvider;
  return generateTTSForProvider(text, provider);
}

// Usage:
const hybrid: HybridTTSConfig = {
  draftProvider: {
    provider: 'orpheus',
    voiceId: 'tara',
    modelSize: '400M', // Fast drafts
  },
  finalProvider: {
    provider: 'elevenlabs',
    voiceId: 'pNInz6obpgDQGcFmaJgB',
    apiKey: process.env.ELEVENLABS_API_KEY!,
  },
};

// Iterate on script with fast local TTS
const draft = await hybridGenerate(scriptText, hybrid, false);
// ... review, adjust script ...

// Generate final with ElevenLabs quality
const final = await hybridGenerate(scriptText, hybrid, true);
```

### Caching Generated Audio

TTS is deterministic for the same input — cache aggressively to avoid regenerating unchanged segments.

```typescript
import { createHash } from 'crypto';
import { readFile, writeFile, access } from 'fs/promises';
import path from 'path';

const CACHE_DIR = '/tmp/tts-cache';

function getCacheKey(text: string, provider: string, voiceId: string): string {
  const hash = createHash('sha256')
    .update(`${provider}:${voiceId}:${text}`)
    .digest('hex')
    .slice(0, 16);
  return hash;
}

async function cachedTTS(
  text: string,
  voice: VoiceConfig,
  cacheDir: string = CACHE_DIR
): Promise<Buffer> {
  const key = getCacheKey(text, voice.provider, voice.voiceId);
  const cachePath = path.join(cacheDir, `${key}.wav`);

  // Check cache first
  try {
    await access(cachePath);
    console.log(`  Cache hit: ${key}`);
    return readFile(cachePath);
  } catch {
    // Cache miss — generate
  }

  const audio = await generateTTSForProvider(text, voice);
  await writeFile(cachePath, audio);
  console.log(`  Cache miss, generated: ${key}`);
  return audio;
}
```

### Long-Form Content Chunking

Most TTS providers have text length limits (typically 5,000 characters). For long content, split at sentence boundaries and concatenate.

```typescript
/**
 * Split text into chunks at sentence boundaries, respecting max character limit.
 */
function chunkText(text: string, maxChars: number = 4500): string[] {
  const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
  const chunks: string[] = [];
  let current = '';

  for (const sentence of sentences) {
    if (current.length + sentence.length > maxChars) {
      if (current.length > 0) {
        chunks.push(current.trim());
        current = '';
      }
      // Handle single sentences longer than maxChars
      if (sentence.length > maxChars) {
        chunks.push(sentence.trim());
        continue;
      }
    }
    current += sentence;
  }

  if (current.trim().length > 0) {
    chunks.push(current.trim());
  }

  return chunks;
}

/**
 * Generate TTS for long-form content by chunking and concatenating.
 */
async function generateLongFormTTS(
  text: string,
  voice: VoiceConfig,
  outputPath: string
): Promise<void> {
  const chunks = chunkText(text);
  const tempFiles: string[] = [];

  console.log(`Generating ${chunks.length} chunks...`);

  for (let i = 0; i < chunks.length; i++) {
    const audio = await cachedTTS(chunks[i], voice);
    const tempFile = `/tmp/longform-${i.toString().padStart(4, '0')}.wav`;
    await writeFile(tempFile, audio);
    tempFiles.push(tempFile);
  }

  // Concatenate with FFmpeg
  const listFile = '/tmp/longform-concat.txt';
  await writeFile(listFile, tempFiles.map((f) => `file '${f}'`).join('\n'));

  await execFileAsync('ffmpeg', [
    '-y', '-f', 'concat', '-safe', '0',
    '-i', listFile,
    '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
    '-c:a', 'libmp3lame', '-b:a', '192k',
    outputPath,
  ]);

  // Cleanup
  for (const f of tempFiles) await unlink(f).catch(() => {});
  await unlink(listFile).catch(() => {});
}
```

---

## 8. Provider Setup Checklists

### ElevenLabs Setup

```bash
# 1. Sign up at elevenlabs.io
# 2. Get API key from Profile → API Keys
# 3. Install (optional — can use raw fetch)
npm install elevenlabs  # Official SDK (optional)

# 4. Set environment variable
export ELEVENLABS_API_KEY=sk_xxxxxxxxxxxxxxxxxxxxxxxx

# 5. Test with curl
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "model_id": "eleven_multilingual_v2"}' \
  --output test.mp3
```

### Orpheus TTS Setup

```bash
# 1. Install Python dependencies
pip install orpheus-tts torch torchaudio

# 2. First run downloads model (~6GB for 3B)
python -c "from orpheus_tts import OrpheusModel; m = OrpheusModel('canopyai/Orpheus-TTS-0.1-3B')"

# 3. Test generation
python -c "
from orpheus_tts import OrpheusModel
model = OrpheusModel('canopyai/Orpheus-TTS-0.1-3B')
audio = model.generate_speech(prompt='Hello world', voice='tara')
audio.export('test.wav', format='wav')
print('Success')
"
```

### Chatterbox Setup

```bash
# 1. Install
pip install chatterbox-tts torch torchaudio

# 2. Test with emotion slider
python -c "
import torch
from chatterbox.tts import ChatterboxTTS

model = ChatterboxTTS.from_pretrained(device='cuda' if torch.cuda.is_available() else 'cpu')
# No reference audio = default voice
audio = model.generate(text='Hello world', exaggeration=0.5)
import torchaudio
torchaudio.save('test.wav', audio, model.sr)
print('Success')
"
```

### Google Cloud TTS Setup

```bash
# 1. Enable Text-to-Speech API in GCP Console
# 2. Create service account and download JSON key
# 3. Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# 4. Install SDK
npm install @google-cloud/text-to-speech

# 5. Test
npx ts-node -e "
import { TextToSpeechClient } from '@google-cloud/text-to-speech';
import { writeFileSync } from 'fs';

const client = new TextToSpeechClient();
async function test() {
  const [response] = await client.synthesizeSpeech({
    input: { text: 'Hello world' },
    voice: { languageCode: 'en-US', name: 'en-US-Neural2-D' },
    audioConfig: { audioEncoding: 2 },
  });
  writeFileSync('test.mp3', response.audioContent as Buffer);
  console.log('Success');
}
test();
"
```

---

## 9. Troubleshooting

### Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Orpheus CUDA out of memory | Model too large for GPU | Use smaller model: 1B or 400M |
| ElevenLabs 401 error | Invalid or expired API key | Regenerate key at elevenlabs.io |
| Google TTS "Permission denied" | Service account missing TTS role | Add `roles/texttospeech.user` to service account |
| Chatterbox sounds distorted | Emotion too high | Reduce `exaggeration` to 0.3-0.5 |
| Audio has clicks at chunk boundaries | Hard cuts between segments | Add 50-100ms crossfade between chunks |
| Inconsistent volume between speakers | No normalization | Apply EBU R128 loudnorm to each segment |
| Bark output varies wildly | Stochastic generation | Generate 3 takes, pick best; set seed for reproducibility |

### Crossfade Between Chunks (Fix Clicking)

```bash
# Add 100ms crossfade between concatenated segments
ffmpeg -i chunk1.wav -i chunk2.wav \
  -filter_complex "[0][1]acrossfade=d=0.1:c1=tri:c2=tri" \
  output.wav
```

### Check GPU VRAM Before Loading Models

```typescript
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

async function getAvailableVRAM(): Promise<number> {
  try {
    const { stdout } = await execFileAsync('nvidia-smi', [
      '--query-gpu=memory.free',
      '--format=csv,noheader,nounits',
    ]);
    return parseInt(stdout.trim(), 10); // MB
  } catch {
    return 0; // No GPU or nvidia-smi not available
  }
}

async function selectModelSize(): Promise<'3B' | '1B' | '400M' | '150M'> {
  const vramMB = await getAvailableVRAM();

  if (vramMB >= 8000) return '3B';
  if (vramMB >= 4000) return '1B';
  if (vramMB >= 2000) return '400M';
  if (vramMB >= 1000) return '150M';

  throw new Error(`Insufficient VRAM (${vramMB}MB). Minimum 1GB required for Orpheus 150M.`);
}
```

---

## 10. Research Citations

> **Related skills:** audio-enhancement-pipeline.md (post-processing), ffmpeg-command-generator.md (media transforms), content-repurposing-pipeline.md (sermon-to-social pipeline), transcription-pipeline-selector.md (speech-to-text, the inverse operation).
