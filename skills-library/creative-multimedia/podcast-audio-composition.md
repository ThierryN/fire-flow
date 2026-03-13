---
name: podcast-audio-composition
category: creative-multimedia
version: 1.0.0
contributed: 2026-03-10
contributor: dominion-flow-research
last_updated: 2026-03-10
tags: [podcast, audio, ffmpeg, mixing, composition, multi-track, intro-outro, background-music]
difficulty: medium
---

# Podcast Audio Composition
**Related skills:** [ffmpeg-command-generator.md](ffmpeg-command-generator.md), [audio-enhancement-pipeline.md](audio-enhancement-pipeline.md)

## Description

Compose multi-track podcast audio from individual speech segments, background music, intro/outro jingles, and sound effects — all using FFmpeg and Node.js. This skill covers the full production workflow: assembling TTS speech segments in script order, mixing music beds underneath dialogue, adding intro/outro with crossfades, applying per-speaker EQ and spatial separation, and exporting with proper loudness normalization and metadata.

## When to Use

- Building AI-generated podcasts from TTS segments (Google Cloud TTS, Anthropic Claude voice, Gemini TTS)
- Composing multi-speaker audio from individual voice recordings
- Adding background music, intro jingles, and sound effects to speech
- Automating podcast post-production in a Node.js pipeline
- Creating educational narration with chapter breaks and ambient music
- Producing sermon recap audio with multiple speakers

---

## 1. Multi-Speaker Audio Assembly

### Concept

Each speaker's lines are separate audio files (from TTS or recordings). A script JSON defines the assembly order. The composer concatenates them with natural pauses and optional crossfades.

### Script JSON Format

```json
{
  "title": "Episode 42: Faith and Technology",
  "speakers": {
    "host": { "name": "Pastor James", "voice": "en-US-Neural2-D", "role": "host" },
    "guest": { "name": "Dr. Sarah Chen", "voice": "en-US-Neural2-F", "role": "guest" }
  },
  "segments": [
    { "speaker": "host", "file": "segments/001_host_intro.wav", "text": "Welcome to..." },
    { "speaker": "guest", "file": "segments/002_guest_response.wav", "text": "Thanks for having me..." },
    { "speaker": "host", "file": "segments/003_host_question.wav", "text": "So tell us about..." },
    { "speaker": "guest", "file": "segments/004_guest_answer.wav", "text": "Well, the key insight is..." },
    { "speaker": "host", "file": "segments/005_host_followup.wav", "text": "That's fascinating..." },
    { "speaker": "guest", "file": "segments/006_guest_elaboration.wav", "text": "Exactly, and when you consider..." },
    { "speaker": "host", "file": "segments/007_host_closing.wav", "text": "Thank you so much..." }
  ],
  "music": {
    "intro": "assets/intro_jingle.mp3",
    "outro": "assets/outro_jingle.mp3",
    "bed": "assets/ambient_music_bed.mp3"
  }
}
```

### Pause Strategy

Natural conversation has variable pauses. Robotic podcasts use identical gaps.

| Transition | Pause Duration | Rationale |
|-----------|---------------|-----------|
| Same speaker continues | 200ms | Brief breath pause |
| Speaker change (agreement) | 300ms | Natural handoff |
| Speaker change (new topic) | 500ms | Topic transition |
| After a question | 400ms | Thinking pause |
| Chapter break | 1000ms | Clear section separation |
| Before closing remarks | 800ms | Signals wind-down |

---

## 2. FFmpeg Filter Graphs for Podcast Production

### a) Generate Silence Padding

```bash
# Create silence files at 44100 Hz mono (match your TTS sample rate)
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 0.2 silence_200ms.wav
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 0.3 silence_300ms.wav
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 0.5 silence_500ms.wav
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 1.0 silence_1000ms.wav
```

### b) Concatenate Speech Segments with Silence Gaps

Create a `segments.txt` file listing each segment and silence in order:

```
file 'segments/001_host_intro.wav'
file 'silence_300ms.wav'
file 'segments/002_guest_response.wav'
file 'silence_300ms.wav'
file 'segments/003_host_question.wav'
file 'silence_400ms.wav'
file 'segments/004_guest_answer.wav'
file 'silence_300ms.wav'
file 'segments/005_host_followup.wav'
file 'silence_300ms.wav'
file 'segments/006_guest_elaboration.wav'
file 'silence_500ms.wav'
file 'segments/007_host_closing.wav'
```

```bash
# Concatenate all segments + silences into one continuous track
ffmpeg -f concat -safe 0 -i segments.txt -c copy concatenated.wav
```

**Important:** All input files must have the same sample rate, channel count, and codec. If they differ, re-encode first:

```bash
# Normalize all segments to 44100 Hz mono PCM before concatenation
for f in segments/*.wav; do
  ffmpeg -i "$f" -ar 44100 -ac 1 -c:a pcm_s16le "normalized_$(basename $f)"
done
```

### c) Crossfade Between Segments (Smoother Transitions)

For a more polished sound, crossfade instead of hard-cut with silence:

```bash
# Crossfade two segments (0.3s overlap, triangular curve)
ffmpeg -i segment_01.wav -i segment_02.wav \
  -filter_complex "[0:a][1:a]acrossfade=d=0.3:c1=tri:c2=tri" \
  crossfaded.wav
```

For chaining multiple crossfades (3+ segments):

```bash
# Chain 4 segments with 0.3s crossfades
ffmpeg -i seg1.wav -i seg2.wav -i seg3.wav -i seg4.wav \
  -filter_complex \
    "[0:a][1:a]acrossfade=d=0.3:c1=tri:c2=tri[ab]; \
     [ab][2:a]acrossfade=d=0.3:c1=tri:c2=tri[abc]; \
     [abc][3:a]acrossfade=d=0.3:c1=tri:c2=tri" \
  chained.wav
```

**Crossfade curve options:**
- `tri` — triangular (linear fade, natural for speech)
- `qsin` — quarter sine (smooth, slightly musical)
- `esin` — exponential sine (very smooth, best for music transitions)
- `log` — logarithmic (quick fade, punchy)

### d) Mix Background Music Under Speech

```bash
# Simple mix: music at 15% volume underneath speech
ffmpeg -i speech.wav -i music.wav \
  -filter_complex "[1:a]volume=0.15[music];[0:a][music]amix=inputs=2:duration=first" \
  mixed.mp3

# Music fades in over 3s, plays at 12% volume, fades out over 3s
ffmpeg -i speech.wav -i music.wav \
  -filter_complex \
    "[1:a]volume=0.12,afade=t=in:d=3,afade=t=out:st=SPEECH_DURATION_MINUS_3:d=3[music]; \
     [0:a][music]amix=inputs=2:duration=first" \
  mixed_with_fades.mp3
```

Replace `SPEECH_DURATION_MINUS_3` with the actual speech duration minus 3 seconds. Use `ffprobe` to measure:

```bash
# Get audio duration in seconds
ffprobe -i speech.wav -show_entries format=duration -v quiet -of csv="p=0"
```

### e) Sidechain Compression (Duck Music Under Speech)

More professional than static volume — music automatically ducks when speech is present:

```bash
# Music ducks under speech using sidechaincompress
ffmpeg -i speech.wav -i music.wav \
  -filter_complex \
    "[1:a]volume=0.25[music]; \
     [music][0:a]sidechaincompress=threshold=0.03:ratio=5:attack=200:release=1000[ducked]; \
     [0:a][ducked]amix=inputs=2:duration=first" \
  ducked_output.mp3
```

**Parameters:**
- `threshold=0.03` — duck when speech exceeds this level (low = sensitive)
- `ratio=5` — how much to reduce music (5:1 compression)
- `attack=200` — how fast music ducks (ms)
- `release=1000` — how fast music returns after speech stops (ms)

### f) Add Intro/Outro with Crossfade

```bash
# Crossfade intro (5s) into main content, then main into outro (5s)
ffmpeg -i intro.mp3 -i main_content.mp3 -i outro.mp3 \
  -filter_complex \
    "[0:a][1:a]acrossfade=d=2:c1=tri:c2=tri[mid]; \
     [mid][2:a]acrossfade=d=2:c1=tri:c2=tri" \
  final_episode.mp3
```

For a hard-cut intro with fade-in on main content:

```bash
# Intro plays fully, main content fades in, outro fades in at end
ffmpeg -i intro.mp3 -i main.mp3 -i outro.mp3 \
  -filter_complex \
    "[1:a]afade=t=in:d=1[main_faded]; \
     [0:a][main_faded]concat=n=2:v=0:a=1[with_intro]; \
     [2:a]afade=t=in:d=1[outro_faded]; \
     [with_intro][outro_faded]concat=n=2:v=0:a=1" \
  final.mp3
```

### g) Loudness Normalization (EBU R128 — Podcast Standard)

Two-pass normalization for broadcast-quality consistency:

```bash
# Pass 1: Measure current loudness (capture JSON output)
ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null NUL 2>&1

# Pass 2: Apply measured values for precise normalization
# Replace the measured_* values with output from Pass 1
ffmpeg -i input.wav \
  -af loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=-23.5:measured_TP=-4.2:measured_LRA=14.1:measured_thresh=-34.8:linear=true \
  -c:a libmp3lame -b:a 192k -ar 44100 \
  normalized.mp3
```

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `I=-16` | -16 LUFS | Integrated loudness target (podcast standard) |
| `TP=-1.5` | -1.5 dBTP | True peak ceiling (prevents clipping on decode) |
| `LRA=11` | 11 LU | Loudness range (dynamic range window) |
| `linear=true` | — | Use linear normalization (preserves dynamics better) |

Single-pass shortcut (less precise but simpler):

```bash
ffmpeg -i input.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:a libmp3lame -b:a 192k normalized.mp3
```

---

## 3. Node.js fluent-ffmpeg Wrapper

### Type Definitions

```typescript
import ffmpeg from 'fluent-ffmpeg';
import { existsSync, writeFileSync, unlinkSync, mkdirSync } from 'fs';
import { join, basename, dirname } from 'path';
import { execFileSync } from 'child_process';

// --- Type Definitions ---

interface AudioSegment {
  speaker: string;
  file: string;
  text?: string;
  pauseAfterMs?: number;  // Override default pause (200-500ms)
}

interface SpeakerProfile {
  name: string;
  voice: string;
  role: 'host' | 'guest' | 'narrator';
  eqPreset?: 'deep' | 'bright' | 'neutral';
  pan?: number;           // -1.0 (full left) to 1.0 (full right)
  volumeAdjust?: number;  // dB adjustment (-3 to +3)
}

interface PodcastMetadata {
  title: string;
  artist: string;
  album?: string;
  date?: string;
  genre?: string;
  comment?: string;
  trackNumber?: number;
  coverArt?: string;      // Path to cover image
}

interface CompositionConfig {
  segments: AudioSegment[];
  speakers: Record<string, SpeakerProfile>;
  music?: {
    intro?: string;
    outro?: string;
    bed?: string;
    bedVolume?: number;    // 0.0 - 1.0, default 0.12
  };
  crossfadeDuration?: number;  // seconds, default 2
  defaultPauseMs?: number;     // default 300
  outputFormat?: 'mp3' | 'wav' | 'ogg';
  outputPath: string;
  metadata?: PodcastMetadata;
  tempDir?: string;
}

// --- Helper Functions ---

/**
 * Get audio duration using ffprobe.
 * Uses execFileSync (no shell) to avoid command injection.
 */
function getAudioDuration(filePath: string): number {
  const output = execFileSync('ffprobe', [
    '-i', filePath,
    '-show_entries', 'format=duration',
    '-v', 'quiet',
    '-of', 'csv=p=0'
  ], { encoding: 'utf-8' });
  return parseFloat(output.trim());
}

/**
 * Run an FFmpeg command safely using execFileSync (no shell).
 * All arguments are passed as an array to prevent injection.
 */
function runFfmpegSync(args: string[]): string {
  return execFileSync('ffmpeg', args, { encoding: 'utf-8', stdio: 'pipe' });
}
```

### PodcastComposer Class

```typescript
class PodcastComposer {
  private tempDir: string;
  private tempFiles: string[] = [];

  constructor(tempDir: string = './temp_podcast') {
    this.tempDir = tempDir;
    mkdirSync(this.tempDir, { recursive: true });
  }

  /**
   * Generate a silence file of specified duration.
   */
  private createSilence(durationMs: number): string {
    const outPath = join(this.tempDir, `silence_${durationMs}ms.wav`);
    if (!existsSync(outPath)) {
      runFfmpegSync([
        '-y', '-f', 'lavfi',
        '-i', `anullsrc=r=44100:cl=mono`,
        '-t', String(durationMs / 1000),
        outPath
      ]);
      this.tempFiles.push(outPath);
    }
    return outPath;
  }

  /**
   * Normalize a segment to consistent sample rate and channels.
   */
  private normalizeSegment(inputPath: string, sampleRate: number = 44100): string {
    const outPath = join(this.tempDir, `norm_${basename(inputPath)}`);
    runFfmpegSync([
      '-y', '-i', inputPath,
      '-ar', String(sampleRate),
      '-ac', '1',
      '-c:a', 'pcm_s16le',
      outPath
    ]);
    this.tempFiles.push(outPath);
    return outPath;
  }

  /**
   * Apply speaker-specific EQ profile to a segment.
   */
  private applySpeakerEQ(inputPath: string, profile: SpeakerProfile): string {
    const outPath = join(this.tempDir, `eq_${basename(inputPath)}`);
    const filters: string[] = [];

    // EQ presets for voice differentiation
    switch (profile.eqPreset) {
      case 'deep':
        // Host: warmer, fuller low-mid presence
        filters.push('equalizer=f=200:t=q:w=1.0:g=2');
        filters.push('equalizer=f=3000:t=q:w=1.5:g=1');
        filters.push('highpass=f=60');
        break;
      case 'bright':
        // Guest: clearer, more articulate high-mid
        filters.push('equalizer=f=3500:t=q:w=1.5:g=3');
        filters.push('equalizer=f=6000:t=q:w=2.0:g=1.5');
        filters.push('highpass=f=100');
        break;
      case 'neutral':
      default:
        // Clean pass — minimal processing
        filters.push('highpass=f=80');
        break;
    }

    // Volume adjustment
    if (profile.volumeAdjust) {
      filters.push(`volume=${profile.volumeAdjust}dB`);
    }

    // Stereo panning (convert mono to stereo with pan position)
    if (profile.pan !== undefined && profile.pan !== 0) {
      const leftGain = Math.cos((profile.pan + 1) * Math.PI / 4);
      const rightGain = Math.sin((profile.pan + 1) * Math.PI / 4);
      filters.push(`pan=stereo|c0=${leftGain.toFixed(3)}*c0|c1=${rightGain.toFixed(3)}*c0`);
    }

    if (filters.length === 0) return inputPath;

    const filterChain = filters.join(',');
    runFfmpegSync(['-y', '-i', inputPath, '-af', filterChain, outPath]);
    this.tempFiles.push(outPath);
    return outPath;
  }

  /**
   * Assemble speech segments with silence gaps between them.
   * Normalizes all segments, applies speaker EQ, then concatenates.
   */
  async assembleSpeechSegments(
    segments: AudioSegment[],
    speakers: Record<string, SpeakerProfile> = {},
    defaultPauseMs: number = 300
  ): Promise<string> {
    const outputPath = join(this.tempDir, 'assembled_speech.wav');
    const concatListPath = join(this.tempDir, 'concat_list.txt');
    const lines: string[] = [];

    for (let i = 0; i < segments.length; i++) {
      const seg = segments[i];

      if (!existsSync(seg.file)) {
        throw new Error(`Segment file not found: ${seg.file}`);
      }

      // Normalize to consistent format
      let processed = this.normalizeSegment(seg.file);

      // Apply speaker-specific EQ if profile exists
      const profile = speakers[seg.speaker];
      if (profile) {
        processed = this.applySpeakerEQ(processed, profile);
      }

      lines.push(`file '${processed.replace(/\\/g, '/')}'`);

      // Add silence gap after each segment (except the last)
      if (i < segments.length - 1) {
        const pauseMs = seg.pauseAfterMs || defaultPauseMs;
        const silencePath = this.createSilence(pauseMs);
        lines.push(`file '${silencePath.replace(/\\/g, '/')}'`);
      }
    }

    writeFileSync(concatListPath, lines.join('\n'), 'utf-8');

    runFfmpegSync([
      '-y', '-f', 'concat', '-safe', '0',
      '-i', concatListPath,
      '-c:a', 'pcm_s16le',
      outputPath
    ]);

    this.tempFiles.push(outputPath, concatListPath);
    console.log(`[podcast-composer] Assembled ${segments.length} segments`);
    return outputPath;
  }

  /**
   * Mix background music underneath speech audio.
   * Music volume is reduced and fades in/out gracefully.
   */
  async addBackgroundMusic(
    speechPath: string,
    musicPath: string,
    musicVolume: number = 0.12
  ): Promise<string> {
    const outputPath = join(this.tempDir, 'speech_with_music.wav');
    const speechDuration = getAudioDuration(speechPath);
    const fadeOutStart = Math.max(0, speechDuration - 3);

    const filterGraph =
      `[1:a]volume=${musicVolume},afade=t=in:d=3,` +
      `afade=t=out:st=${fadeOutStart.toFixed(2)}:d=3[music];` +
      `[0:a][music]amix=inputs=2:duration=first`;

    runFfmpegSync([
      '-y', '-i', speechPath, '-i', musicPath,
      '-filter_complex', filterGraph,
      outputPath
    ]);

    this.tempFiles.push(outputPath);
    console.log(`[podcast-composer] Added background music (vol=${musicVolume})`);
    return outputPath;
  }

  /**
   * Add intro and/or outro with crossfade transitions.
   */
  async addIntroOutro(
    mainPath: string,
    intro?: string,
    outro?: string,
    crossfadeSec: number = 2
  ): Promise<string> {
    let currentPath = mainPath;

    // Add intro with crossfade
    if (intro && existsSync(intro)) {
      const withIntro = join(this.tempDir, 'with_intro.wav');
      runFfmpegSync([
        '-y', '-i', intro, '-i', currentPath,
        '-filter_complex', `[0:a][1:a]acrossfade=d=${crossfadeSec}:c1=tri:c2=tri`,
        withIntro
      ]);
      this.tempFiles.push(withIntro);
      currentPath = withIntro;
    }

    // Add outro with crossfade
    if (outro && existsSync(outro)) {
      const withOutro = join(this.tempDir, 'with_intro_outro.wav');
      runFfmpegSync([
        '-y', '-i', currentPath, '-i', outro,
        '-filter_complex', `[0:a][1:a]acrossfade=d=${crossfadeSec}:c1=tri:c2=tri`,
        withOutro
      ]);
      this.tempFiles.push(withOutro);
      currentPath = withOutro;
    }

    console.log(`[podcast-composer] Added intro/outro`);
    return currentPath;
  }

  /**
   * Two-pass EBU R128 loudness normalization.
   * Targets -16 LUFS (podcast standard).
   */
  async normalizeAudio(inputPath: string): Promise<string> {
    const outputPath = join(this.tempDir, 'normalized.wav');

    // Pass 1: Measure current loudness
    // Note: FFmpeg writes loudnorm JSON to stderr, so we capture it
    let measureOutput: string;
    try {
      execFileSync('ffmpeg', [
        '-i', inputPath,
        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json',
        '-f', 'null', 'NUL'
      ], { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] });
      measureOutput = '';
    } catch (err: any) {
      // FFmpeg exits non-zero for -f null but stderr has our data
      measureOutput = err.stderr || '';
    }

    // Parse measured values from JSON output
    const jsonMatch = measureOutput.match(/\{[\s\S]*?"input_i"[\s\S]*?\}/);
    if (!jsonMatch) {
      throw new Error('Failed to parse loudness measurement from FFmpeg output');
    }

    const measured = JSON.parse(jsonMatch[0]);
    const { input_i, input_tp, input_lra, input_thresh } = measured;

    // Pass 2: Apply precise normalization with measured values
    runFfmpegSync([
      '-y', '-i', inputPath,
      '-af', `loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=${input_i}:measured_TP=${input_tp}:measured_LRA=${input_lra}:measured_thresh=${input_thresh}:linear=true`,
      outputPath
    ]);

    this.tempFiles.push(outputPath);
    console.log(`[podcast-composer] Normalized to -16 LUFS (was ${input_i} LUFS)`);
    return outputPath;
  }

  /**
   * Export final podcast with format conversion and metadata tagging.
   */
  async exportFinal(
    inputPath: string,
    format: 'mp3' | 'wav' | 'ogg' = 'mp3',
    metadata?: PodcastMetadata
  ): Promise<string> {
    const ext = format === 'ogg' ? 'ogg' : format;
    const outputPath = join(dirname(this.tempDir), `final_podcast.${ext}`);

    const codecMap: Record<string, { codec: string; bitrate: string }> = {
      mp3: { codec: 'libmp3lame', bitrate: '192k' },
      wav: { codec: 'pcm_s16le', bitrate: '' },
      ogg: { codec: 'libvorbis', bitrate: '192k' },
    };

    const { codec, bitrate } = codecMap[format];

    // Build FFmpeg args array
    const args: string[] = ['-y', '-i', inputPath, '-c:a', codec];

    if (bitrate) {
      args.push('-b:a', bitrate);
    }
    args.push('-ar', '44100');

    // Add metadata flags
    if (metadata) {
      if (metadata.title) args.push('-metadata', `title=${metadata.title}`);
      if (metadata.artist) args.push('-metadata', `artist=${metadata.artist}`);
      if (metadata.album) args.push('-metadata', `album=${metadata.album}`);
      if (metadata.date) args.push('-metadata', `date=${metadata.date}`);
      if (metadata.genre) args.push('-metadata', `genre=${metadata.genre}`);
      if (metadata.comment) args.push('-metadata', `comment=${metadata.comment}`);
      if (metadata.trackNumber) args.push('-metadata', `track=${metadata.trackNumber}`);
    }

    args.push(outputPath);
    runFfmpegSync(args);

    // Embed cover art for MP3 (if provided)
    if (format === 'mp3' && metadata?.coverArt && existsSync(metadata.coverArt)) {
      const withCover = outputPath.replace('.mp3', '_cover.mp3');
      runFfmpegSync([
        '-y', '-i', outputPath, '-i', metadata.coverArt,
        '-map', '0:a', '-map', '1:0',
        '-c', 'copy', '-id3v2_version', '3',
        '-metadata:s:v', 'title=Album cover',
        '-metadata:s:v', 'comment=Cover (front)',
        withCover
      ]);
      unlinkSync(outputPath);
      require('fs').renameSync(withCover, outputPath);
    }

    console.log(`[podcast-composer] Exported final podcast`);
    return outputPath;
  }

  /**
   * Full composition pipeline: assemble -> music -> intro/outro -> normalize -> export.
   * This is the main entry point for end-to-end podcast production.
   */
  async compose(config: CompositionConfig): Promise<string> {
    console.log(`[podcast-composer] Starting composition: ${config.metadata?.title || 'Untitled'}`);
    const startTime = Date.now();

    // Step 1: Assemble speech segments with pauses
    let audioPath = await this.assembleSpeechSegments(
      config.segments,
      config.speakers,
      config.defaultPauseMs
    );

    // Step 2: Mix background music (if provided)
    if (config.music?.bed && existsSync(config.music.bed)) {
      audioPath = await this.addBackgroundMusic(
        audioPath,
        config.music.bed,
        config.music.bedVolume || 0.12
      );
    }

    // Step 3: Add intro/outro (if provided)
    if (config.music?.intro || config.music?.outro) {
      audioPath = await this.addIntroOutro(
        audioPath,
        config.music.intro,
        config.music.outro,
        config.crossfadeDuration || 2
      );
    }

    // Step 4: Loudness normalization (EBU R128, -16 LUFS)
    audioPath = await this.normalizeAudio(audioPath);

    // Step 5: Export to final format with metadata
    const finalPath = await this.exportFinal(
      audioPath,
      config.outputFormat || 'mp3',
      config.metadata
    );

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    console.log(`[podcast-composer] Composition complete in ${elapsed}s`);

    return finalPath;
  }

  /**
   * Clean up temporary files created during composition.
   */
  cleanup(): void {
    for (const file of this.tempFiles) {
      try {
        if (existsSync(file)) unlinkSync(file);
      } catch { /* ignore cleanup errors */ }
    }
    this.tempFiles = [];
    console.log('[podcast-composer] Temp files cleaned up');
  }
}
```

### Usage Example

```typescript
const composer = new PodcastComposer('./temp_podcast');

try {
  const finalPath = await composer.compose({
    segments: [
      { speaker: 'host', file: 'segments/001_intro.wav', pauseAfterMs: 500 },
      { speaker: 'guest', file: 'segments/002_response.wav', pauseAfterMs: 300 },
      { speaker: 'host', file: 'segments/003_question.wav', pauseAfterMs: 400 },
      { speaker: 'guest', file: 'segments/004_answer.wav', pauseAfterMs: 300 },
      { speaker: 'host', file: 'segments/005_closing.wav' },
    ],
    speakers: {
      host: { name: 'Pastor James', voice: 'en-US-Neural2-D', role: 'host', eqPreset: 'deep', pan: -0.15 },
      guest: { name: 'Dr. Chen', voice: 'en-US-Neural2-F', role: 'guest', eqPreset: 'bright', pan: 0.15 },
    },
    music: {
      intro: 'assets/intro_jingle.mp3',
      outro: 'assets/outro_jingle.mp3',
      bed: 'assets/ambient_bed.mp3',
      bedVolume: 0.12,
    },
    crossfadeDuration: 2,
    defaultPauseMs: 300,
    outputFormat: 'mp3',
    outputPath: './output/episode_042.mp3',
    metadata: {
      title: 'Episode 42: Faith and Technology',
      artist: 'Ministry Podcast',
      album: 'Ministry Podcast Season 3',
      date: '2026',
      genre: 'Podcast',
      comment: 'AI-generated from sermon transcript — produced with Anthropic Claude + Google Gemini TTS',
    },
  });

  console.log('Final podcast:', finalPath);
} finally {
  composer.cleanup();
}
```

---

## 4. Speaker Voice Differentiation

### EQ Profiles by Role

Different EQ treatments create audible distinction between speakers, even when using similar TTS voices.

```
Host (deep):
  +2dB at 200Hz (warmth)
  +1dB at 3kHz (presence)
  Highpass at 60Hz
  Result: Warm, authoritative

Guest (bright):
  +3dB at 3.5kHz (clarity)
  +1.5dB at 6kHz (air)
  Highpass at 100Hz
  Result: Clear, articulate

Narrator (neutral):
  Highpass at 80Hz
  No boost/cut
  Result: Clean, transparent
```

### FFmpeg EQ Commands

```bash
# Host voice — warm and authoritative
ffmpeg -i host_raw.wav \
  -af "highpass=f=60,equalizer=f=200:t=q:w=1.0:g=2,equalizer=f=3000:t=q:w=1.5:g=1" \
  host_eq.wav

# Guest voice — clear and articulate
ffmpeg -i guest_raw.wav \
  -af "highpass=f=100,equalizer=f=3500:t=q:w=1.5:g=3,equalizer=f=6000:t=q:w=2.0:g=1.5" \
  guest_eq.wav

# Narrator — clean pass
ffmpeg -i narrator_raw.wav \
  -af "highpass=f=80" \
  narrator_eq.wav
```

### Spatial Separation (Stereo Panning)

Subtle panning creates a "two people in a room" feel without being distracting:

```bash
# Pan host slightly left (10-15% — subtle, not jarring)
ffmpeg -i host.wav -af "pan=stereo|c0=1.0*c0|c1=0.7*c0" host_panned.wav

# Pan guest slightly right
ffmpeg -i guest.wav -af "pan=stereo|c0=0.7*c0|c1=1.0*c0" guest_panned.wav

# Narrator stays centered
# (no panning needed — default center)
```

**Guidelines:**
- Keep panning subtle: 10-20% off-center maximum
- Listener should feel spatial presence, not notice panning
- Mono compatibility: verify the mix sounds good summed to mono
- Skip panning for single-speaker podcasts or narration

### Volume Leveling Across Speakers

```bash
# Measure each speaker's average loudness
ffmpeg -i host_segments.wav -af ebur128=peak=true -f null NUL 2>&1
ffmpeg -i guest_segments.wav -af ebur128=peak=true -f null NUL 2>&1

# Apply gain adjustment to match target (-16 LUFS for both)
ffmpeg -i guest_segments.wav -af "volume=2.5dB" guest_leveled.wav
```

---

## 5. Production Templates

### Template A: Simple Two-Speaker Podcast

```
Timeline:
| 2s intro | Host intro | Discussion... | Host outro | 2s outro |
|  jingle  |   (10s)    |  (variable)   |   (10s)    |  jingle  |
         ^              ^                           ^
      crossfade     music bed                   crossfade
       (1.5s)      at 10% vol                    (1.5s)
```

```typescript
const simpleConfig: CompositionConfig = {
  segments: [
    { speaker: 'host', file: 'host_intro.wav', pauseAfterMs: 500 },
    // ... discussion segments ...
    { speaker: 'host', file: 'host_outro.wav' },
  ],
  speakers: {
    host: { name: 'Host', voice: 'en-US-Neural2-D', role: 'host', eqPreset: 'deep' },
    guest: { name: 'Guest', voice: 'en-US-Neural2-F', role: 'guest', eqPreset: 'bright' },
  },
  music: {
    intro: 'assets/jingle_2s.mp3',
    outro: 'assets/jingle_2s.mp3',
    bed: 'assets/soft_ambient.mp3',
    bedVolume: 0.10,
  },
  crossfadeDuration: 1.5,
  defaultPauseMs: 300,
  outputFormat: 'mp3',
  outputPath: './output/simple_episode.mp3',
  metadata: { title: 'Episode Title', artist: 'Podcast Name', genre: 'Podcast', date: '2026' },
};
```

### Template B: Professional Production

```
Timeline:
| 5s music | Host    | Sponsor | Main         | Break  | Part 2  | Sponsor | Outro  | 5s music |
|  intro   | welcome |  slot   | discussion   | music  |         |  slot   | w/ CTA |  outro   |
          ^                                   ^                          ^
       crossfade                          3s music                   crossfade
        (2.5s)                           transition                   (2.5s)
```

```typescript
const professionalConfig: CompositionConfig = {
  segments: [
    // Act 1: Welcome + Sponsor
    { speaker: 'host', file: 'seg/welcome.wav', pauseAfterMs: 300 },
    { speaker: 'host', file: 'seg/sponsor_read.wav', pauseAfterMs: 800 },
    // Act 2: Main discussion
    { speaker: 'host', file: 'seg/topic_intro.wav', pauseAfterMs: 400 },
    { speaker: 'guest', file: 'seg/guest_point_1.wav', pauseAfterMs: 300 },
    { speaker: 'host', file: 'seg/host_response_1.wav', pauseAfterMs: 300 },
    { speaker: 'guest', file: 'seg/guest_point_2.wav', pauseAfterMs: 300 },
    // Break marker — handled by pauseAfterMs
    { speaker: 'host', file: 'seg/break_transition.wav', pauseAfterMs: 1000 },
    // Act 3: Part 2 + Outro
    { speaker: 'host', file: 'seg/part2_intro.wav', pauseAfterMs: 400 },
    { speaker: 'guest', file: 'seg/guest_point_3.wav', pauseAfterMs: 300 },
    { speaker: 'host', file: 'seg/sponsor_read_2.wav', pauseAfterMs: 500 },
    { speaker: 'host', file: 'seg/closing_cta.wav' },
  ],
  speakers: {
    host: { name: 'Host', voice: 'en-US-Neural2-D', role: 'host', eqPreset: 'deep', pan: -0.12 },
    guest: { name: 'Guest', voice: 'en-US-Neural2-F', role: 'guest', eqPreset: 'bright', pan: 0.12 },
  },
  music: {
    intro: 'assets/theme_5s.mp3',
    outro: 'assets/theme_5s.mp3',
    bed: 'assets/minimal_beat.mp3',
    bedVolume: 0.08,
  },
  crossfadeDuration: 2.5,
  defaultPauseMs: 300,
  outputFormat: 'mp3',
  outputPath: './output/professional_episode.mp3',
  metadata: {
    title: 'Episode 42: Faith and Technology',
    artist: 'Ministry Podcast',
    album: 'Ministry Podcast Season 3',
    date: '2026',
    genre: 'Podcast',
    comment: 'Produced with Anthropic Claude + Google Gemini TTS',
  },
};
```

### Template C: Educational Narration

```
Timeline:
| Ambient  | Chapter 1  | chime | Chapter 2  | chime | Summary | Music    |
| fade in  | narration  | break | narration  | break |         | fade out |
   ^                                                                ^
 3s fade in                                                     5s fade out
 ambient music bed at 10% volume throughout
```

```typescript
const educationalConfig: CompositionConfig = {
  segments: [
    { speaker: 'narrator', file: 'seg/chapter1_intro.wav', pauseAfterMs: 200 },
    { speaker: 'narrator', file: 'seg/chapter1_body.wav', pauseAfterMs: 1000 },
    // Chapter break — long pause signals section change
    { speaker: 'narrator', file: 'seg/chapter2_intro.wav', pauseAfterMs: 200 },
    { speaker: 'narrator', file: 'seg/chapter2_body.wav', pauseAfterMs: 1000 },
    { speaker: 'narrator', file: 'seg/summary.wav' },
  ],
  speakers: {
    narrator: { name: 'Narrator', voice: 'en-US-Neural2-D', role: 'narrator', eqPreset: 'neutral' },
  },
  music: {
    bed: 'assets/ambient_piano.mp3',
    bedVolume: 0.10,
  },
  crossfadeDuration: 2,
  defaultPauseMs: 200,
  outputFormat: 'mp3',
  outputPath: './output/educational_narration.mp3',
  metadata: {
    title: 'Understanding Grace: Chapter 1-2',
    artist: 'Ministry Teaching Series',
    genre: 'Podcast',
    date: '2026',
    comment: 'AI narration from source document — Anthropic Claude',
  },
};
```

---

## 6. Sound Design Elements

### Sourcing Royalty-Free Audio

| Element | Source | License | Notes |
|---------|--------|---------|-------|
| Intro/outro music | [Pixabay Audio](https://pixabay.com/music/) | Pixabay License (free, no attribution) | Search "podcast intro", filter by <10s |
| Transition sounds | [Freesound.org](https://freesound.org) | CC0 / CC-BY | Search "whoosh", "chime", "transition" |
| Background ambient | [Free Music Archive](https://freemusicarchive.org) | CC-BY / CC0 | Search "ambient", "lo-fi", filter instrumental |
| Sound effects | [Mixkit](https://mixkit.co/free-sound-effects/) | Free license | Clean UI, categorized well |
| Chapter chimes | [Zapsplat](https://www.zapsplat.com) | Free with attribution | Large SFX library |

### Recommended Sound Levels

```
Element                   Volume Level    Notes
-------                   ------------    -----
Speech (primary)          0 dB (ref)      Normalized to -16 LUFS
Background music bed      -18 to -24 dB   10-15% of speech level
Intro/outro jingle        -6 to -3 dB     Prominent but not jarring
Transition whoosh/chime   -12 to -9 dB    Noticeable but brief
Ambient room tone         -30 dB          Barely perceptible
```

### FFmpeg Commands for Sound Design

```bash
# Add a short transition chime between sections
ffmpeg -i before.wav -i chime.wav -i after.wav \
  -filter_complex \
    "[1:a]volume=0.3,adelay=0|0[chime]; \
     [0:a][chime]amix=inputs=2:duration=first[with_chime]; \
     [with_chime][2:a]concat=n=2:v=0:a=1" \
  with_transition.wav

# Fade music from full volume to bed volume at speech start
ffmpeg -i music.mp3 \
  -af "volume=1.0,afade=t=out:st=3:d=2,volume=0.12" \
  music_ducked.wav

# Create a "room tone" ambient layer (pink noise, very quiet)
ffmpeg -f lavfi -i "anoisesrc=d=300:c=pink:r=44100:a=0.005" \
  -c:a pcm_s16le room_tone_5min.wav
```

---

## 7. Metadata Tagging

### Full ID3 Tag Set for Podcast Distribution

```bash
# Complete metadata for podcast episode
ffmpeg -i podcast.mp3 \
  -metadata title="Episode 42: Faith and Technology" \
  -metadata artist="Ministry Podcast" \
  -metadata album="Ministry Podcast Season 3" \
  -metadata album_artist="Ministry Podcast" \
  -metadata date="2026" \
  -metadata genre="Podcast" \
  -metadata track="42" \
  -metadata comment="AI-generated from sermon transcript — Anthropic Claude + Google Gemini TTS" \
  -metadata publisher="Ministry Name" \
  -metadata copyright="2026 Ministry Name" \
  -metadata language="eng" \
  -c copy \
  tagged_podcast.mp3
```

### Embed Cover Art

```bash
# Add cover art to MP3 (ID3v2 embedded image)
ffmpeg -i podcast.mp3 -i cover_art.jpg \
  -map 0:a -map 1:0 \
  -c copy -id3v2_version 3 \
  -metadata:s:v title="Album cover" \
  -metadata:s:v comment="Cover (front)" \
  podcast_with_cover.mp3

# Add cover art to M4A/AAC
ffmpeg -i podcast.m4a -i cover_art.jpg \
  -map 0:a -map 1:0 \
  -c:a copy -c:v mjpeg \
  -disposition:v attached_pic \
  podcast_with_cover.m4a
```

### Cover Art Specifications

| Platform | Minimum | Recommended | Max | Format |
|----------|---------|-------------|-----|--------|
| Apple Podcasts | 1400x1400 | 3000x3000 | 3000x3000 | JPEG/PNG |
| Spotify | 640x640 | 3000x3000 | 3000x3000 | JPEG |
| Google Podcasts | 600x600 | 1200x1200 | — | JPEG/PNG |
| ID3 embed | — | 500x500 | 1000x1000 | JPEG (smaller file size) |

### Validate Metadata

```bash
# Read back all metadata from the file
ffprobe -i podcast.mp3 -show_format -show_streams -v quiet -print_format json

# Quick check — just metadata tags
ffprobe -i podcast.mp3 -show_entries format_tags -v quiet -of default=noprint_wrappers=1
```

---

## 8. Quality Verification Checklist

After composition, verify the output meets podcast distribution standards:

```bash
# 1. Measure loudness (target: -16 LUFS, peak below -1.5 dBTP)
ffmpeg -i final_podcast.mp3 -af ebur128=peak=true -f null NUL 2>&1

# 2. Check duration matches expected length
ffprobe -i final_podcast.mp3 -show_entries format=duration -v quiet -of csv="p=0"

# 3. Verify sample rate and bitrate
ffprobe -i final_podcast.mp3 -show_entries stream=sample_rate,bit_rate -v quiet

# 4. Generate waveform for visual inspection
ffmpeg -i final_podcast.mp3 -lavfi showwavespic=s=1920x200:colors=0x2563EB waveform.png

# 5. Generate spectrogram to check for artifacts
ffmpeg -i final_podcast.mp3 -lavfi showspectrumpic=s=1920x1080:mode=combined:scale=log spectrogram.png
```

### Automated Quality Gate (Node.js)

```typescript
interface QualityResult {
  lufs: number;
  truePeak: number;
  lra: number;
  duration: number;
  sampleRate: number;
  pass: boolean;
  issues: string[];
}

async function verifyPodcastQuality(filePath: string): Promise<QualityResult> {
  const issues: string[] = [];

  // Measure loudness (capture stderr where FFmpeg writes the JSON)
  let measureOutput: string;
  try {
    execFileSync('ffmpeg', [
      '-i', filePath,
      '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json',
      '-f', 'null', 'NUL'
    ], { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] });
    measureOutput = '';
  } catch (err: any) {
    measureOutput = err.stderr || '';
  }

  const jsonMatch = measureOutput.match(/\{[\s\S]*?"input_i"[\s\S]*?\}/);
  const measured = jsonMatch ? JSON.parse(jsonMatch[0]) : null;

  if (!measured) {
    return {
      lufs: 0, truePeak: 0, lra: 0, duration: 0, sampleRate: 0,
      pass: false, issues: ['Could not measure loudness']
    };
  }

  const lufs = parseFloat(measured.input_i);
  const truePeak = parseFloat(measured.input_tp);
  const lra = parseFloat(measured.input_lra);

  // Get duration and sample rate
  const probeOutput = execFileSync('ffprobe', [
    '-i', filePath,
    '-show_entries', 'format=duration:stream=sample_rate',
    '-v', 'quiet', '-of', 'json'
  ], { encoding: 'utf-8' });

  const probe = JSON.parse(probeOutput);
  const duration = parseFloat(probe.format?.duration || '0');
  const sampleRate = parseInt(probe.streams?.[0]?.sample_rate || '0', 10);

  // Quality checks
  if (lufs < -18 || lufs > -14) {
    issues.push(`Loudness out of range: ${lufs} LUFS (target: -16 +/- 2)`);
  }
  if (truePeak > -1.0) {
    issues.push(`True peak too high: ${truePeak} dBTP (max: -1.0)`);
  }
  if (lra > 15) {
    issues.push(`Dynamic range too wide: ${lra} LU (max: 15)`);
  }
  if (lra < 3) {
    issues.push(`Dynamic range too narrow: ${lra} LU (min: 3)`);
  }
  if (sampleRate < 44100) {
    issues.push(`Sample rate too low: ${sampleRate} Hz (min: 44100)`);
  }
  if (duration < 10) {
    issues.push(`Duration suspiciously short: ${duration}s`);
  }

  const pass = issues.length === 0;

  console.log(
    `[quality-check] ${pass ? 'PASS' : 'FAIL'}` +
    ` — ${lufs.toFixed(1)} LUFS, ${truePeak.toFixed(1)} dBTP, ${lra.toFixed(1)} LU`
  );
  if (!pass) issues.forEach(i => console.warn(`  - ${i}`));

  return { lufs, truePeak, lra, duration, sampleRate, pass, issues };
}
```

---

## 9. Advanced Techniques

### Batch Episode Production

Generate multiple episodes from a script directory:

```typescript
import { readdir, readFile } from 'fs/promises';

async function batchProduceEpisodes(
  scriptDir: string,
  outputDir: string
): Promise<void> {
  const files = await readdir(scriptDir);
  const scripts = files.filter(f => f.endsWith('.json'));

  console.log(`[batch] Found ${scripts.length} episode scripts`);

  for (const scriptFile of scripts) {
    const scriptPath = join(scriptDir, scriptFile);
    const raw = await readFile(scriptPath, 'utf-8');
    const config: CompositionConfig = JSON.parse(raw);

    config.outputPath = join(outputDir, scriptFile.replace('.json', '.mp3'));

    const composer = new PodcastComposer(join('./temp', scriptFile));
    try {
      const result = await composer.compose(config);
      const quality = await verifyPodcastQuality(result);
      console.log(`[batch] ${scriptFile}: ${quality.pass ? 'PASS' : 'FAIL'}`);
    } finally {
      composer.cleanup();
    }
  }
}
```

### Dynamic Music Ducking with Silence Detection

Instead of static volume, detect speech segments and duck music automatically:

```bash
# Detect silent regions in speech track (pauses where music can be louder)
ffmpeg -i speech.wav -af silencedetect=noise=-35dB:d=0.5 -f null NUL 2>&1

# Use sidechaincompress for real-time ducking
# Music plays at full volume during silence, ducks under speech
ffmpeg -i speech.wav -i music.wav \
  -filter_complex \
    "[1:a]volume=0.25[music]; \
     [music][0:a]sidechaincompress=threshold=0.02:ratio=8:attack=100:release=800:knee=3[ducked]; \
     [0:a][ducked]amix=inputs=2:duration=first:weights=1 0.8" \
  auto_ducked.wav
```

### Chapter Markers for Podcast Players

Some podcast players support chapter markers (MP4/M4A format):

```bash
# Create chapter metadata file (chapters.txt)
# Format: ;FFMETADATA1
cat > chapters.txt << 'CHAPTEREOF'
;FFMETADATA1
[CHAPTER]
TIMEBASE=1/1000
START=0
END=5000
title=Intro

[CHAPTER]
TIMEBASE=1/1000
START=5000
END=120000
title=Welcome & Overview

[CHAPTER]
TIMEBASE=1/1000
START=120000
END=600000
title=Main Discussion

[CHAPTER]
TIMEBASE=1/1000
START=600000
END=660000
title=Closing Thoughts
CHAPTEREOF

# Apply chapters to M4A file
ffmpeg -i podcast.m4a -i chapters.txt -map_metadata 1 -c copy podcast_with_chapters.m4a
```

### Podcast RSS Feed Integration

After producing the audio, generate the RSS enclosure entry:

```typescript
import { statSync } from 'fs';

function generateRSSEnclosure(filePath: string, baseUrl: string): string {
  const stats = statSync(filePath);
  const filename = basename(filePath);
  const duration = getAudioDuration(filePath);
  const minutes = Math.floor(duration / 60);
  const seconds = Math.floor(duration % 60);

  return `
    <item>
      <title>${filename.replace(/\.[^.]+$/, '').replace(/_/g, ' ')}</title>
      <enclosure url="${baseUrl}/${filename}" length="${stats.size}" type="audio/mpeg" />
      <itunes:duration>${minutes}:${seconds.toString().padStart(2, '0')}</itunes:duration>
      <pubDate>${new Date().toUTCString()}</pubDate>
    </item>
  `.trim();
}
```

---

## 10. Troubleshooting

### Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| "Discarding samples" warning | Sample rate mismatch between segments | Normalize all inputs to same sample rate first |
| Clicks between concatenated segments | Hard cut at non-zero crossing | Add 5ms crossfade or 10ms fade-out/fade-in at boundaries |
| Music too loud / drowns speech | `amix` normalizes by default | Use `weights` parameter or set music `volume` lower |
| Output louder than expected | `amix` gain normalization | Add `normalize=0` to `amix` filter |
| Crossfade produces silence gap | Duration > segment length | Crossfade duration must be shorter than shortest segment |
| Mono/stereo mismatch | Mixing mono speech with stereo music | Convert all to same channel layout before mixing |

### Fix Clicks at Boundaries

```bash
# Add 10ms fade-out to end of each segment before concatenation
ffmpeg -i segment.wav -af "afade=t=out:st=DURATION_MINUS_0.01:d=0.01" segment_clean.wav

# Or add 5ms crossfade between every pair during concatenation
# (handled by the PodcastComposer class automatically when crossfade > 0)
```

### Fix amix Volume Normalization

```bash
# Default amix divides volume by number of inputs — speech gets quieter
# Fix: use weights to keep speech at full volume
ffmpeg -i speech.wav -i music.wav \
  -filter_complex "[1:a]volume=0.12[music];[0:a][music]amix=inputs=2:duration=first:weights=1 1:normalize=0" \
  output.mp3
```

---

## References

- FFmpeg filter documentation: https://ffmpeg.org/ffmpeg-filters.html
- EBU R128 loudness standard: https://tech.ebu.ch/docs/r/r128.pdf
- Apple Podcasts requirements: https://podcasters.apple.com/support/823
- Spotify podcast specs: https://podcasters.spotify.com/resources
- FireRedTTS-2: arXiv 2509.02020 (Sep 2025)
- DialoSpeech: arXiv 2510.08373 (Oct 2025)
- Related skills: [ffmpeg-command-generator.md](ffmpeg-command-generator.md), [audio-enhancement-pipeline.md](audio-enhancement-pipeline.md), [transcription-pipeline-selector.md](transcription-pipeline-selector.md), [content-repurposing-pipeline.md](content-repurposing-pipeline.md)
