# Transcription Pipeline Selector
## Description

Choose and integrate the right speech-to-text service for any project. Covers local (Whisper), streaming (Deepgram), intelligence-rich (AssemblyAI), and ecosystem-aligned (Gemini) providers with working integration code, pre/post-processing pipelines, and cost modeling.

## When to Use

- Adding voice input, transcription, or captioning to an application
- Processing audio/video files into searchable text
- Building voice agents or real-time transcription features
- Migrating between STT providers
- Estimating transcription costs for a project proposal

---

## Decision Matrix

| Provider | Speed | Accuracy | Price/min | Best For | Node SDK |
|----------|-------|----------|-----------|----------|----------|
| Whisper Turbo (local) | 6x realtime | ~96% | $0 (GPU needed) | Privacy, offline, bulk | whisper-node |
| Deepgram Nova-3 | Sub-300ms | Best streaming | $0.0043 | Real-time, voice agents | @deepgram/sdk |
| AssemblyAI | Good | 96%+ | $0.0025 | Intelligence features | assemblyai |
| Google Gemini | Good | 95%+ | Token-based | Already using Gemini | @google/generative-ai |
| OpenAI gpt-4o-transcribe | Fast | Lowest WER | $0.006 | OpenAI ecosystem | openai |

### Quick Decision Flow

```
Need real-time streaming? --> Deepgram Nova-3
Need speaker labels + summaries + sentiment? --> AssemblyAI
Need privacy / no API calls? --> Whisper Turbo (local)
Already using Gemini for other features? --> Gemini Audio
Budget is primary concern for batch? --> AssemblyAI ($0.0025/min)
```

---

## Integration Code

### 1. Whisper Local (faster-whisper via Python subprocess)

The most practical local approach uses faster-whisper (CTranslate2 backend). Call from Node via subprocess.

**Install (Python side):**

```bash
pip install faster-whisper
```

**Python transcription script (`transcribe.py`):**

```python
import sys
import json
from faster_whisper import WhisperModel

def transcribe(audio_path: str, model_size: str = "large-v3-turbo"):
    model = WhisperModel(model_size, device="cuda", compute_type="float16")
    segments, info = model.transcribe(audio_path, beam_size=5)

    results = []
    for segment in segments:
        results.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip(),
            "confidence": round(segment.avg_log_prob, 4),
        })

    return {
        "language": info.language,
        "language_probability": round(info.language_probability, 2),
        "duration": round(info.duration, 2),
        "segments": results,
        "full_text": " ".join(s["text"] for s in results),
    }

if __name__ == "__main__":
    result = transcribe(sys.argv[1])
    print(json.dumps(result))
```

**Node.js caller:**

```typescript
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

interface TranscriptionResult {
  language: string;
  language_probability: number;
  duration: number;
  segments: Array<{
    start: number;
    end: number;
    text: string;
    confidence: number;
  }>;
  full_text: string;
}

async function transcribeLocal(audioPath: string): Promise<TranscriptionResult> {
  const { stdout } = await execFileAsync("python", ["transcribe.py", audioPath], {
    maxBuffer: 50 * 1024 * 1024, // 50MB for long transcriptions
    timeout: 600_000, // 10 min timeout
  });
  return JSON.parse(stdout);
}
```

**Alternative: whisper-node (pure Node binding):**

```typescript
import whisper from "whisper-node";

const transcript = await whisper("audio.wav", {
  modelName: "large-v3-turbo",
  whisperOptions: { language: "auto", word_timestamps: true },
});
// Returns array of { start, end, speech }
```

---

### 2. Deepgram Nova-3 (REST + WebSocket Streaming)

**Install:**

```bash
npm install @deepgram/sdk
```

**Pre-recorded (REST):**

```typescript
import { createClient } from "@deepgram/sdk";

const deepgram = createClient(process.env.DEEPGRAM_API_KEY!);

async function transcribeFile(filePath: string) {
  const { result } = await deepgram.listen.prerecorded.transcribeFile(
    fs.readFileSync(filePath),
    {
      model: "nova-3",
      smart_format: true,
      diarize: true,
      language: "en",
      punctuate: true,
      utterances: true,
    }
  );

  const transcript = result.results.channels[0].alternatives[0];
  return {
    text: transcript.transcript,
    confidence: transcript.confidence,
    words: transcript.words, // includes speaker labels when diarize=true
    paragraphs: transcript.paragraphs,
  };
}
```

**Real-time WebSocket streaming:**

```typescript
import { createClient, LiveTranscriptionEvents } from "@deepgram/sdk";

const deepgram = createClient(process.env.DEEPGRAM_API_KEY!);

function startLiveTranscription(onTranscript: (text: string, isFinal: boolean) => void) {
  const connection = deepgram.listen.live({
    model: "nova-3",
    language: "en",
    smart_format: true,
    interim_results: true,
    utterance_end_ms: 1500,
    vad_events: true,
    encoding: "linear16",
    sample_rate: 16000,
  });

  connection.on(LiveTranscriptionEvents.Open, () => {
    console.log("Deepgram connection opened");
  });

  connection.on(LiveTranscriptionEvents.Transcript, (data) => {
    const transcript = data.channel.alternatives[0].transcript;
    if (transcript) {
      onTranscript(transcript, data.is_final);
    }
  });

  connection.on(LiveTranscriptionEvents.UtteranceEnd, () => {
    onTranscript("", true); // Signal end of utterance
  });

  connection.on(LiveTranscriptionEvents.Error, (err) => {
    console.error("Deepgram error:", err);
  });

  return {
    send: (audioChunk: Buffer) => connection.send(audioChunk),
    close: () => connection.requestClose(),
  };
}

// Usage with microphone (e.g., from a WebSocket client):
// const live = startLiveTranscription((text, isFinal) => {
//   if (isFinal) console.log("Final:", text);
//   else console.log("Interim:", text);
// });
// audioStream.on("data", (chunk) => live.send(chunk));
```

---

### 3. AssemblyAI (Upload + Poll + Webhooks)

**Install:**

```bash
npm install assemblyai
```

**Basic transcription with intelligence features:**

```typescript
import { AssemblyAI } from "assemblyai";

const client = new AssemblyAI({ apiKey: process.env.ASSEMBLYAI_API_KEY! });

async function transcribeWithIntelligence(audioUrl: string) {
  const transcript = await client.transcripts.transcribe({
    audio_url: audioUrl,
    speaker_labels: true,
    auto_chapters: true,
    sentiment_analysis: true,
    entity_detection: true,
    auto_highlights: true,
    language_detection: true,
  });

  if (transcript.status === "error") {
    throw new Error(`Transcription failed: ${transcript.error}`);
  }

  return {
    text: transcript.text,
    confidence: transcript.confidence,
    speakers: transcript.utterances, // speaker-labeled segments
    chapters: transcript.chapters, // auto-generated chapters with summaries
    sentiment: transcript.sentiment_analysis_results,
    entities: transcript.entities,
    highlights: transcript.auto_highlights_result,
  };
}
```

**With webhook (for long files):**

```typescript
async function transcribeAsync(audioUrl: string, webhookUrl: string) {
  const transcript = await client.transcripts.submit({
    audio_url: audioUrl,
    webhook_url: webhookUrl,
    speaker_labels: true,
  });

  return transcript.id; // Poll or wait for webhook
}

// Express webhook handler
app.post("/webhooks/assemblyai", async (req, res) => {
  const { transcript_id, status } = req.body;
  if (status === "completed") {
    const transcript = await client.transcripts.get(transcript_id);
    // Process completed transcript
  }
  res.sendStatus(200);
});
```

**Polling pattern:**

```typescript
async function pollTranscript(transcriptId: string) {
  const transcript = await client.transcripts.get(transcriptId);

  if (transcript.status === "completed") return transcript;
  if (transcript.status === "error") throw new Error(transcript.error);

  // Still processing — wait and retry
  await new Promise((r) => setTimeout(r, 3000));
  return pollTranscript(transcriptId);
}
```

---

### 4. Google Gemini Audio

Since the user prefers Gemini/Claude, this is the most ecosystem-aligned option.

**Install:**

```bash
npm install @google/generative-ai
```

**Transcribe with Gemini:**

```typescript
import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from "node:fs";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

async function transcribeWithGemini(audioPath: string) {
  const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

  const audioData = fs.readFileSync(audioPath);
  const base64Audio = audioData.toString("base64");

  // Determine MIME type
  const ext = audioPath.split(".").pop()?.toLowerCase();
  const mimeMap: Record<string, string> = {
    mp3: "audio/mpeg",
    wav: "audio/wav",
    m4a: "audio/mp4",
    ogg: "audio/ogg",
    flac: "audio/flac",
    webm: "audio/webm",
  };
  const mimeType = mimeMap[ext || ""] || "audio/mpeg";

  const result = await model.generateContent([
    {
      inlineData: {
        mimeType,
        data: base64Audio,
      },
    },
    {
      text: `Transcribe this audio accurately. Return a JSON object with:
- "text": the full transcription
- "segments": array of { "timestamp": "MM:SS", "text": "segment text" }
- "language": detected language code
- "summary": one-paragraph summary

Return ONLY valid JSON, no markdown fences.`,
    },
  ]);

  return JSON.parse(result.response.text());
}
```

**Gemini with speaker diarization prompt:**

```typescript
async function transcribeWithSpeakers(audioPath: string, speakerCount?: number) {
  const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

  const audioData = fs.readFileSync(audioPath);

  const result = await model.generateContent([
    {
      inlineData: {
        mimeType: "audio/wav",
        data: audioData.toString("base64"),
      },
    },
    {
      text: `Transcribe this audio with speaker identification.
${speakerCount ? `There are ${speakerCount} speakers.` : "Detect the number of speakers."}

Return JSON:
{
  "speakers_detected": number,
  "utterances": [
    { "speaker": "Speaker 1", "start": "0:00", "end": "0:05", "text": "..." }
  ],
  "full_text": "Speaker 1: ... Speaker 2: ..."
}

Return ONLY valid JSON.`,
    },
  ]);

  return JSON.parse(result.response.text());
}
```

> **Note:** Gemini audio has a file size limit (~20MB inline). For larger files, use the File API to upload first, then reference the file URI.

---

## Pre-processing Best Practices

### Convert to 16kHz Mono WAV (FFmpeg)

All STT engines perform best with 16kHz mono WAV input. This normalizes any source format:

```bash
# Single file
ffmpeg -i input.mp3 -ar 16000 -ac 1 -c:a pcm_s16le output.wav

# Batch convert directory
for f in *.mp3; do
  ffmpeg -i "$f" -ar 16000 -ac 1 -c:a pcm_s16le "${f%.mp3}.wav"
done
```

**Node.js wrapper using fluent-ffmpeg:**

```typescript
import ffmpeg from "fluent-ffmpeg";

function preprocessAudio(inputPath: string, outputPath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    ffmpeg(inputPath)
      .audioFrequency(16000)
      .audioChannels(1)
      .audioCodec("pcm_s16le")
      .format("wav")
      .on("end", resolve)
      .on("error", reject)
      .save(outputPath);
  });
}
```

### Split Long Files into 10-Minute Chunks

API providers have file size and duration limits. Split at silence boundaries for clean segments:

```bash
# Split at 10-minute intervals with 2-second overlap
ffmpeg -i long_audio.wav -f segment -segment_time 600 \
  -c:a pcm_s16le -ar 16000 -ac 1 chunk_%03d.wav
```

**Smart splitting at silence boundaries:**

```typescript
import ffmpeg from "fluent-ffmpeg";

async function splitAtSilence(inputPath: string, outputDir: string): Promise<string[]> {
  return new Promise((resolve, reject) => {
    const chunks: string[] = [];

    ffmpeg(inputPath)
      .audioFilters("silencedetect=noise=-30dB:d=0.5")
      .format("null")
      .output("/dev/null")
      .on("stderr", (line: string) => {
        // Parse silence timestamps from FFmpeg stderr
        const match = line.match(/silence_end: ([\d.]+)/);
        if (match) chunks.push(match[1]);
      })
      .on("end", () => resolve(chunks))
      .on("error", reject)
      .run();
  });
}
```

### Detect Language Before Choosing Model

```typescript
import { AssemblyAI } from "assemblyai";

// AssemblyAI auto-detects language
const transcript = await client.transcripts.transcribe({
  audio_url: url,
  language_detection: true,
});
console.log(transcript.language_code); // "en", "es", "fr", etc.

// Whisper auto-detects on first 30 seconds
// Pass language="auto" or omit the language parameter

// Deepgram: set detect_language=true
const { result } = await deepgram.listen.prerecorded.transcribeFile(buffer, {
  model: "nova-3",
  detect_language: true,
});
```

---

## Post-processing

### Punctuation Restoration

Most cloud APIs handle this natively (`smart_format: true` for Deepgram, default for AssemblyAI). For local Whisper output that needs cleanup:

```typescript
// Use Gemini to restore punctuation and fix casing
async function restorePunctuation(rawText: string): Promise<string> {
  const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
  const result = await model.generateContent(
    `Fix punctuation, capitalization, and paragraph breaks in this transcript. ` +
    `Do NOT change any words, only add punctuation and formatting:\n\n${rawText}`
  );
  return result.response.text();
}
```

### Speaker Diarization

For providers without built-in diarization, use pyannote.audio (best open-source diarization):

```python
from pyannote.audio import Pipeline

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="YOUR_HF_TOKEN"
)

diarization = pipeline("audio.wav")

for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"[{turn.start:.1f} - {turn.end:.1f}] {speaker}")
```

### Timestamp Alignment for Subtitles

**Generate SRT format:**

```typescript
interface Segment {
  start: number;
  end: number;
  text: string;
}

function toSRT(segments: Segment[]): string {
  return segments
    .map((seg, i) => {
      const formatTime = (seconds: number) => {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        const ms = Math.round((seconds % 1) * 1000);
        return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")},${String(ms).padStart(3, "0")}`;
      };
      return `${i + 1}\n${formatTime(seg.start)} --> ${formatTime(seg.end)}\n${seg.text}\n`;
    })
    .join("\n");
}

// Output:
// 1
// 00:00:00,000 --> 00:00:04,520
// Hello and welcome to today's session.
```

**Generate VTT format:**

```typescript
function toVTT(segments: Segment[]): string {
  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    const ms = Math.round((seconds % 1) * 1000);
    return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(ms).padStart(3, "0")}`;
  };

  const cues = segments
    .map((seg) => `${formatTime(seg.start)} --> ${formatTime(seg.end)}\n${seg.text}`)
    .join("\n\n");

  return `WEBVTT\n\n${cues}\n`;
}
```

### Confidence Scoring

```typescript
interface QualityReport {
  overall_confidence: number;
  low_confidence_segments: Array<{ start: number; end: number; text: string; confidence: number }>;
  recommendation: string;
}

function assessTranscriptQuality(segments: Segment & { confidence: number }[]): QualityReport {
  const avgConfidence = segments.reduce((sum, s) => sum + s.confidence, 0) / segments.length;
  const lowConfidence = segments.filter((s) => s.confidence < 0.85);

  return {
    overall_confidence: Math.round(avgConfidence * 100) / 100,
    low_confidence_segments: lowConfidence,
    recommendation:
      avgConfidence > 0.95
        ? "High quality — safe for automated processing"
        : avgConfidence > 0.85
          ? "Good quality — spot-check flagged segments"
          : "Low quality — manual review recommended. Consider re-recording or using a different model.",
  };
}
```

---

## Cost Calculator

### Formula

```
Monthly Cost = (hours_of_audio * 60) * price_per_minute
```

### Quick Reference Table

| Provider | 10 hrs/mo | 100 hrs/mo | 1,000 hrs/mo |
|----------|-----------|------------|--------------|
| Whisper (local) | $0 | $0 | $0 (GPU: ~$0.10/hr on cloud) |
| Deepgram Nova-3 | $2.58 | $25.80 | $258.00 |
| AssemblyAI | $1.50 | $15.00 | $150.00 |
| Gemini | ~$0.50* | ~$5.00* | ~$50.00* |
| OpenAI gpt-4o-transcribe | $3.60 | $36.00 | $360.00 |

*Gemini pricing is token-based and varies by audio length/complexity.

### Cost Estimation Function

```typescript
interface CostEstimate {
  provider: string;
  monthly_hours: number;
  monthly_cost: number;
  annual_cost: number;
  cost_per_hour: number;
}

function estimateCost(monthlyHours: number): CostEstimate[] {
  const providers = [
    { name: "Whisper (local)", pricePerMin: 0 },
    { name: "Deepgram Nova-3", pricePerMin: 0.0043 },
    { name: "AssemblyAI", pricePerMin: 0.0025 },
    { name: "Google Gemini", pricePerMin: 0.0008 },
    { name: "OpenAI gpt-4o-transcribe", pricePerMin: 0.006 },
  ];

  return providers.map((p) => {
    const monthly = monthlyHours * 60 * p.pricePerMin;
    return {
      provider: p.name,
      monthly_hours: monthlyHours,
      monthly_cost: Math.round(monthly * 100) / 100,
      annual_cost: Math.round(monthly * 12 * 100) / 100,
      cost_per_hour: Math.round(p.pricePerMin * 60 * 100) / 100,
    };
  });
}
```

---

## Common Pitfalls

1. **Sending stereo audio to APIs** — doubles file size, no accuracy gain. Always convert to mono first.
2. **Not handling API rate limits** — Deepgram allows 100 concurrent streams; AssemblyAI queues automatically. Build retry logic with exponential backoff.
3. **Ignoring audio quality** — background noise kills accuracy. Apply noise reduction before transcription:
   ```bash
   ffmpeg -i noisy.wav -af "afftdn=nf=-25" clean.wav
   ```
4. **Choosing Whisper local without a GPU** — CPU inference is 20-50x slower. On CPU, use `tiny` or `base` models only.
5. **Not chunking long files** — most APIs have 2-hour or file-size limits. Split proactively.

---

