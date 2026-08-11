# Audio Enhancement Pipeline
## Description

Automate audio post-production using FFmpeg filter chains. This skill provides a structured pipeline for cleaning up, normalizing, and mastering audio — covering podcasts, sermons, music, and voice recordings.

## When to Use

- Cleaning up recorded audio (noise, silence, inconsistent volume)
- Preparing podcast/sermon audio for publishing
- Batch processing multiple audio files with consistent quality
- Building an automated audio pipeline in Node.js
- Mastering music tracks for distribution

---

## The Pipeline (Ordered Steps)

Audio enhancement works best when filters are applied in a specific order. Each step builds on the previous one.

```
Raw Audio
  |
  v
[1] Noise Reduction     -- remove background hiss, hum, ambient noise
  |
  v
[2] Loudness Normalization -- bring to target LUFS (EBU R128)
  |
  v
[3] Silence Trimming    -- remove dead air from start, end, and middle
  |
  v
[4] Compression/Limiting -- tame peaks, even out dynamic range
  |
  v
[5] Format Conversion   -- export to target format(s)
  |
  v
Clean Audio
```

---

## Step 1: Noise Reduction

### FFT-based Denoising (`afftdn`)

Best for stationary noise (constant hiss, fan hum, room tone).

```bash
# Adaptive noise floor — good default for most recordings
ffmpeg -i input.wav -af "afftdn=nf=-25:nt=w:om=o" denoised.wav

# Stronger denoising (may affect voice quality)
ffmpeg -i input.wav -af "afftdn=nf=-20:nt=w:om=o" denoised.wav

# Gentle denoising (preserves natural sound)
ffmpeg -i input.wav -af "afftdn=nf=-35:nt=w:om=o" denoised.wav
```

**Parameters:**
- `nf` — noise floor in dB (lower = less aggressive, `-25` is a good start)
- `nt=w` — noise type: white noise model
- `om=o` — output mode: output cleaned signal

### Non-local Means Denoising (`anlmdn`)

Better for non-stationary noise (variable background sounds).

```bash
# Default non-local means denoising
ffmpeg -i input.wav -af "anlmdn=s=7:p=0.002:r=0.002" denoised.wav

# Stronger denoising
ffmpeg -i input.wav -af "anlmdn=s=10:p=0.005:r=0.005" denoised.wav
```

**Parameters:**
- `s` — denoising strength (higher = more aggressive)
- `p` — patch size factor
- `r` — research size factor

### Hum Removal (50/60Hz electrical hum)

```bash
# Remove 60Hz hum (US power) + harmonics
ffmpeg -i input.wav -af "highpass=f=80,bandreject=f=60:w=2,bandreject=f=120:w=2,bandreject=f=180:w=2" dehum.wav

# Remove 50Hz hum (EU power) + harmonics
ffmpeg -i input.wav -af "highpass=f=65,bandreject=f=50:w=2,bandreject=f=100:w=2,bandreject=f=150:w=2" dehum.wav
```

---

## Step 2: Loudness Normalization (EBU R128)

### Target Levels

| Content Type | Integrated LUFS | True Peak (dBTP) | LRA (LU) |
|-------------|-----------------|-------------------|-----------|
| **Podcast** | -16 LUFS | -1.0 dBTP | 5-10 LU |
| **YouTube** | -14 LUFS | -1.0 dBTP | 7-12 LU |
| **Music streaming** | -14 LUFS | -1.0 dBTP | 7-15 LU |
| **Broadcast TV** | -24 LUFS | -2.0 dBTP | 6-12 LU |
| **Audiobook** | -18 to -20 LUFS | -3.0 dBTP | 3-6 LU |

### Two-Pass Normalization (Most Accurate)

```bash
# Pass 1: Measure current loudness
ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1.0:LRA=11:print_format=json -f null NUL 2>&1

# Read the JSON output — you need: measured_I, measured_TP, measured_LRA, measured_thresh

# Pass 2: Apply with measured values (example values — use YOUR measured values)
ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1.0:LRA=11:measured_I=-23.2:measured_TP=-4.1:measured_LRA=14.5:measured_thresh=-34.2:linear=true normalized.wav
```

### Single-Pass Normalization (Simpler)

```bash
# Podcast target (-16 LUFS)
ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1.0:LRA=11 normalized.wav

# Music target (-14 LUFS)
ffmpeg -i input.wav -af loudnorm=I=-14:TP=-1.0:LRA=11 normalized.wav

# Broadcast target (-24 LUFS)
ffmpeg -i input.wav -af loudnorm=I=-24:TP=-2.0:LRA=11 normalized.wav
```

---

## Step 3: Silence Trimming

### Remove Leading and Trailing Silence

```bash
# Remove silence from start and end (threshold: -40dB, min silence: 0.5s)
ffmpeg -i input.wav -af "silenceremove=start_periods=1:start_threshold=-40dB:start_duration=0.5:stop_periods=1:stop_threshold=-40dB:stop_duration=0.5" trimmed.wav
```

### Remove All Internal Silence (Pauses)

```bash
# Remove ALL silence segments longer than 1 second
ffmpeg -i input.wav -af "silenceremove=stop_periods=-1:stop_threshold=-40dB:stop_duration=1" trimmed.wav

# Shorten long pauses to 0.5s (keep some natural rhythm)
ffmpeg -i input.wav -af "silenceremove=stop_periods=-1:stop_threshold=-45dB:stop_duration=2:stop_silence=0.5" trimmed.wav
```

### Detect Silence (Without Removing)

```bash
# List all silent segments (useful for chapter detection)
ffmpeg -i input.wav -af silencedetect=noise=-40dB:d=1.0 -f null NUL 2>&1
```

---

## Step 4: Compression / Limiting

### Dynamic Range Compression

```bash
# Gentle compression — evens out volume without squashing dynamics
ffmpeg -i input.wav -af "acompressor=threshold=-20dB:ratio=3:attack=5:release=50:makeup=2" compressed.wav

# Podcast compression — tighter control for consistent voice levels
ffmpeg -i input.wav -af "acompressor=threshold=-18dB:ratio=4:attack=5:release=100:knee=5:makeup=3" compressed.wav

# Aggressive compression — broadcast-style (talk radio feel)
ffmpeg -i input.wav -af "acompressor=threshold=-15dB:ratio=6:attack=2:release=50:knee=3:makeup=5" compressed.wav
```

**Parameters explained:**
- `threshold` — level above which compression kicks in
- `ratio` — how much to reduce (4:1 means 4dB over threshold becomes 1dB)
- `attack` — how fast compression engages (ms)
- `release` — how fast compression releases (ms)
- `knee` — softens the threshold transition (dB)
- `makeup` — gain added after compression to restore volume (dB)

### Hard Limiting (Prevent Clipping)

```bash
# Brick-wall limiter at -1dBTP
ffmpeg -i input.wav -af "alimiter=limit=0.891:attack=5:release=50:level=false" limited.wav
# 0.891 = linear value of -1 dBFS (10^(-1/20))
```

---

## Step 5: Format Conversion

```bash
# High-quality MP3 for podcast distribution
ffmpeg -i enhanced.wav -c:a libmp3lame -b:a 192k -ar 44100 podcast.mp3

# AAC for Apple Podcasts
ffmpeg -i enhanced.wav -c:a aac -b:a 192k -ar 44100 podcast.m4a

# Opus for web (best quality-to-size ratio)
ffmpeg -i enhanced.wav -c:a libopus -b:a 128k podcast.opus

# FLAC for archival
ffmpeg -i enhanced.wav -c:a flac -compression_level 8 archive.flac
```

---

## Complete FFmpeg Command Chains

### Sermon / Podcast Cleanup

Full pipeline: noise reduction, normalize to -16 LUFS, trim silence, gentle compression.

```bash
ffmpeg -i raw_sermon.wav \
  -af "afftdn=nf=-25:nt=w:om=o, \
       highpass=f=80, \
       acompressor=threshold=-20dB:ratio=3:attack=5:release=100:makeup=2, \
       silenceremove=start_periods=1:start_threshold=-40dB:stop_periods=1:stop_threshold=-40dB:stop_duration=0.5, \
       loudnorm=I=-16:TP=-1.0:LRA=11" \
  -c:a libmp3lame -b:a 192k -ar 44100 \
  clean_sermon.mp3
```

### Music Mastering

Normalize, compress for consistent dynamics, limit peaks.

```bash
ffmpeg -i raw_mix.wav \
  -af "acompressor=threshold=-18dB:ratio=2.5:attack=10:release=200:knee=6:makeup=1, \
       alimiter=limit=0.891:attack=5:release=50:level=false, \
       loudnorm=I=-14:TP=-1.0:LRA=11" \
  -c:a flac -compression_level 8 \
  mastered.flac
```

### Voice Recording Enhancement

Noise removal, presence boost (2-5kHz), normalize for clarity.

```bash
ffmpeg -i raw_voice.wav \
  -af "afftdn=nf=-25:nt=w:om=o, \
       highpass=f=80, \
       lowpass=f=12000, \
       equalizer=f=3500:t=q:w=1.5:g=3, \
       acompressor=threshold=-20dB:ratio=3:attack=5:release=100:makeup=2, \
       loudnorm=I=-16:TP=-1.0:LRA=11" \
  -c:a libmp3lame -b:a 192k -ar 44100 \
  enhanced_voice.mp3
```

**EQ breakdown:**
- `highpass=f=80` — removes rumble below 80Hz
- `lowpass=f=12000` — removes harsh sibilance above 12kHz
- `equalizer=f=3500:t=q:w=1.5:g=3` — boosts presence range by 3dB (makes voice cut through)

---

## Node.js Implementation

### Full Pipeline with fluent-ffmpeg

```javascript
import ffmpeg from 'fluent-ffmpeg';
import { existsSync } from 'fs';

/**
 * Audio enhancement pipeline
 * @param {string} inputPath - Path to raw audio file
 * @param {string} outputPath - Path for enhanced output
 * @param {object} options - Pipeline configuration
 */
function enhanceAudio(inputPath, outputPath, options = {}) {
  const {
    type = 'podcast',          // 'podcast' | 'music' | 'voice'
    targetLUFS = -16,          // Target loudness
    noiseFloor = -25,          // Noise reduction strength (dB)
    trimSilence = true,        // Remove leading/trailing silence
    outputFormat = 'mp3',      // 'mp3' | 'aac' | 'flac' | 'opus'
    bitrate = '192k',
    onProgress = null,
  } = options;

  if (!existsSync(inputPath)) {
    return Promise.reject(new Error(`Input file not found: ${inputPath}`));
  }

  // Build filter chain based on content type
  const filters = [];

  // Step 1: Noise reduction
  filters.push(`afftdn=nf=${noiseFloor}:nt=w:om=o`);
  filters.push('highpass=f=80');

  // Step 2: Type-specific processing
  if (type === 'voice') {
    filters.push('lowpass=f=12000');
    filters.push('equalizer=f=3500:t=q:w=1.5:g=3');
  }

  // Step 3: Compression
  const compSettings = {
    podcast: 'threshold=-20dB:ratio=3:attack=5:release=100:makeup=2',
    music:   'threshold=-18dB:ratio=2.5:attack=10:release=200:knee=6:makeup=1',
    voice:   'threshold=-20dB:ratio=3:attack=5:release=100:makeup=2',
  };
  filters.push(`acompressor=${compSettings[type] || compSettings.podcast}`);

  // Step 4: Silence trimming
  if (trimSilence) {
    filters.push(
      'silenceremove=start_periods=1:start_threshold=-40dB:stop_periods=1:stop_threshold=-40dB:stop_duration=0.5'
    );
  }

  // Step 5: Loudness normalization (always last before output)
  filters.push(`loudnorm=I=${targetLUFS}:TP=-1.0:LRA=11`);

  const filterChain = filters.join(',');

  // Codec mapping
  const codecMap = {
    mp3:  { codec: 'libmp3lame', ext: '.mp3' },
    aac:  { codec: 'aac',        ext: '.m4a' },
    flac: { codec: 'flac',       ext: '.flac' },
    opus: { codec: 'libopus',    ext: '.opus' },
  };
  const { codec } = codecMap[outputFormat] || codecMap.mp3;

  return new Promise((resolve, reject) => {
    const cmd = ffmpeg(inputPath)
      .audioFilters(filterChain)
      .audioCodec(codec)
      .audioBitrate(bitrate)
      .audioFrequency(44100)
      .output(outputPath)
      .on('start', (cmdLine) => {
        console.log('[audio-pipeline] Running:', cmdLine);
      })
      .on('progress', (progress) => {
        if (onProgress) onProgress(progress);
      })
      .on('end', () => {
        console.log('[audio-pipeline] Done:', outputPath);
        resolve(outputPath);
      })
      .on('error', (err, stdout, stderr) => {
        console.error('[audio-pipeline] Error:', err.message);
        console.error('[audio-pipeline] stderr:', stderr);
        reject(err);
      });

    cmd.run();
  });
}

// --- Usage Examples ---

// Podcast cleanup
await enhanceAudio('raw_episode.wav', 'episode_001.mp3', {
  type: 'podcast',
  targetLUFS: -16,
  trimSilence: true,
});

// Music mastering
await enhanceAudio('mix.wav', 'mastered.flac', {
  type: 'music',
  targetLUFS: -14,
  outputFormat: 'flac',
  trimSilence: false,
});

// Voice memo cleanup
await enhanceAudio('recording.m4a', 'clean_voice.mp3', {
  type: 'voice',
  targetLUFS: -16,
  noiseFloor: -20,  // more aggressive for noisy recordings
});
```

### Batch Processing

```javascript
import { readdir } from 'fs/promises';
import { join, parse } from 'path';

async function batchEnhance(inputDir, outputDir, options = {}) {
  const files = await readdir(inputDir);
  const audioFiles = files.filter(f =>
    /\.(wav|mp3|m4a|flac|ogg|aac|wma)$/i.test(f)
  );

  console.log(`Found ${audioFiles.length} audio files to process`);

  const results = [];
  for (const file of audioFiles) {
    const inputPath = join(inputDir, file);
    const { name } = parse(file);
    const outputPath = join(outputDir, `${name}_enhanced.mp3`);

    try {
      await enhanceAudio(inputPath, outputPath, options);
      results.push({ file, status: 'success', output: outputPath });
    } catch (err) {
      results.push({ file, status: 'error', error: err.message });
      console.error(`Failed: ${file} — ${err.message}`);
    }
  }

  const succeeded = results.filter(r => r.status === 'success').length;
  console.log(`Batch complete: ${succeeded}/${audioFiles.length} succeeded`);
  return results;
}

await batchEnhance('./raw_sermons/', './enhanced_sermons/', {
  type: 'podcast',
  targetLUFS: -16,
});
```

---

## API Alternatives

When local FFmpeg processing is not enough (heavy noise, AI-powered enhancement needed):

### Auphonic API

Best for: Podcast production, automatic leveling, noise reduction.

```javascript
// Auphonic — automated audio post-production
// Docs: https://auphonic.com/api/

const AUPHONIC_TOKEN = process.env.AUPHONIC_TOKEN;

// Create a production
const response = await fetch('https://auphonic.com/api/simple/productions.json', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${AUPHONIC_TOKEN}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'Episode 42',
    input_file: 'https://example.com/raw_audio.wav',
    output_files: [{ format: 'mp3', bitrate: '192' }],
    algorithms: {
      loudnesstarget: -16,       // LUFS
      denoise: true,
      leveler: true,             // Multi-track leveling
      filtering: true,           // Remove low-frequency rumble
    },
  }),
});

const { data } = await response.json();
// Start the production
await fetch(`https://auphonic.com/api/production/${data.uuid}/start.json`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${AUPHONIC_TOKEN}` },
});
```

**Pricing:** Free tier = 2 hours/month. Paid starts at $11/month for 9 hours.

### Dolby.io Media API

Best for: Professional-grade enhancement, noise reduction, loudness correction.

```javascript
// Dolby.io Enhance API
// Docs: https://docs.dolby.io/media-apis/docs/enhance-api-guide

const DOLBY_API_KEY = process.env.DOLBY_API_KEY;

// Step 1: Get upload URL
const uploadResp = await fetch('https://api.dolby.io/media/input', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${DOLBY_API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ url: 'dlb://input/raw_audio.wav' }),
});
const { url: uploadUrl } = await uploadResp.json();

// Step 2: Upload file
await fetch(uploadUrl, {
  method: 'PUT',
  headers: { 'Content-Type': 'audio/wav' },
  body: audioBuffer,
});

// Step 3: Start enhancement
const enhanceResp = await fetch('https://api.dolby.io/media/enhance', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${DOLBY_API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    input: 'dlb://input/raw_audio.wav',
    output: 'dlb://output/enhanced.mp3',
    content: { type: 'podcast' },   // 'podcast' | 'conference' | 'interview' | 'music'
    audio: {
      noise: { reduction: { enable: true, amount: 'high' } },
      loudness: { enable: true, dialog_intelligence: true },
    },
  }),
});
```

**Pricing:** Pay-per-minute. Enhancement starts at $0.005/min.

### Adobe Podcast API (Enhance Speech)

Best for: Voice-only recordings, AI-powered studio-quality voice isolation.

```
Note: Adobe Podcast "Enhance Speech" is currently a web tool at podcast.adobe.com/enhance.
No public REST API as of 2025 — but Adobe is expanding API access through Firefly Services.
```

**Workaround for automation:** Use browser automation (Playwright) to upload/download through the web UI, or check Adobe's developer portal for API access updates.

---

## Quality Verification

### Measure Loudness (LUFS)

```bash
# Get full loudness stats
ffmpeg -i enhanced.mp3 -af loudnorm=I=-16:TP=-1.0:LRA=11:print_format=json -f null NUL 2>&1

# Quick measurement with ebur128
ffmpeg -i enhanced.mp3 -af ebur128=peak=true -f null NUL 2>&1
```

**What to check in the output:**
- `input_i` — Integrated loudness (should match your target, e.g., -16 LUFS)
- `input_tp` — True peak (should be below -1.0 dBTP)
- `input_lra` — Loudness range (5-10 for speech, 7-15 for music)

### Spectral Analysis

```bash
# Generate a spectrogram image
ffmpeg -i enhanced.mp3 -lavfi showspectrumpic=s=1920x1080:mode=combined:color=intensity:scale=log spectrogram.png

# Generate waveform image
ffmpeg -i enhanced.mp3 -lavfi showwavespic=s=1920x200:colors=0x1DB954 waveform.png
```

**What to look for in the spectrogram:**
- No visible horizontal lines at 50/60Hz (hum removed)
- No constant brightness in high frequencies (noise removed)
- Clean gaps between speech segments (silence trimming worked)
- Even brightness across the file (compression/normalization worked)

### A/B Comparison

```bash
# Create a side-by-side comparison file (original then enhanced)
ffmpeg -i original.wav -i enhanced.mp3 -filter_complex "[0:a][1:a]concat=n=2:v=0:a=1" ab_compare.wav

# Create a 5-second snippet comparison
ffmpeg -i original.wav -ss 30 -t 5 -c:a pcm_s16le snippet_before.wav
ffmpeg -i enhanced.mp3 -ss 30 -t 5 -c:a pcm_s16le snippet_after.wav
```

### Automated Quality Check (Node.js)

```javascript
import ffmpeg from 'fluent-ffmpeg';

function measureLoudness(filePath) {
  return new Promise((resolve, reject) => {
    let stderr = '';
    ffmpeg(filePath)
      .audioFilters('loudnorm=I=-16:TP=-1.0:LRA=11:print_format=json')
      .format('null')
      .output('/dev/null')  // Use 'NUL' on Windows
      .on('stderr', (line) => { stderr += line + '\n'; })
      .on('end', () => {
        // Extract JSON from FFmpeg stderr output
        const jsonMatch = stderr.match(/\{[\s\S]*?"input_i"[\s\S]*?\}/);
        if (jsonMatch) {
          const stats = JSON.parse(jsonMatch[0]);
          resolve({
            lufs: parseFloat(stats.input_i),
            truePeak: parseFloat(stats.input_tp),
            lra: parseFloat(stats.input_lra),
            threshold: parseFloat(stats.input_thresh),
          });
        } else {
          reject(new Error('Could not parse loudness data'));
        }
      })
      .on('error', reject)
      .run();
  });
}

// Usage
const stats = await measureLoudness('enhanced.mp3');
console.log(`LUFS: ${stats.lufs}, True Peak: ${stats.truePeak} dBTP, LRA: ${stats.lra} LU`);

// Validation
const isGood =
  stats.lufs >= -17 && stats.lufs <= -15 &&   // Within 1 LUFS of target
  stats.truePeak <= -0.5 &&                     // Below true peak limit
  stats.lra >= 3 && stats.lra <= 15;            // Reasonable dynamic range

console.log(isGood ? 'PASS — audio meets spec' : 'WARN — check levels');
```
