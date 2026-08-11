# FFmpeg Command Generator
## Description

Generate precise FFmpeg commands from natural language descriptions. This skill covers the most common media transformation tasks developers encounter: format conversion, extraction, compression, streaming preparation, and audio processing.

## When to Use

- User asks to convert, trim, compress, or transform video/audio files
- Building a media processing pipeline in Node.js
- Preparing video for web streaming (HLS, DASH)
- Extracting audio, thumbnails, or clips from video
- Automating batch media processing

---

## Common FFmpeg Patterns

### Video Format Conversion

```bash
# MP4 (H.264 + AAC) — universal web playback
ffmpeg -i input.mov -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k output.mp4

# WebM (VP9 + Opus) — smaller files, modern browsers
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -c:a libopus -b:a 128k output.webm

# MOV (ProRes 422) — editing/archive quality
ffmpeg -i input.mp4 -c:v prores_ks -profile:v 2 -c:a pcm_s16le output.mov

# AV1 (libaom) — best compression, slow encode
ffmpeg -i input.mp4 -c:v libaom-av1 -crf 30 -b:v 0 -c:a libopus output.mkv
```

### Audio Extraction from Video

```bash
# Extract audio as-is (no re-encoding)
ffmpeg -i input.mp4 -vn -acodec copy output.aac

# Extract and convert to MP3
ffmpeg -i input.mp4 -vn -c:a libmp3lame -q:a 2 output.mp3

# Extract and convert to WAV (uncompressed)
ffmpeg -i input.mp4 -vn -c:a pcm_s16le -ar 44100 output.wav
```

### Audio Format Conversion

```bash
# WAV to MP3 (high quality VBR)
ffmpeg -i input.wav -c:a libmp3lame -q:a 0 output.mp3

# WAV to MP3 (constant bitrate 320k)
ffmpeg -i input.wav -c:a libmp3lame -b:a 320k output.mp3

# FLAC to AAC (256k — Apple-compatible)
ffmpeg -i input.flac -c:a aac -b:a 256k output.m4a

# MP3 to OGG Opus (voice-optimized, 64k)
ffmpeg -i input.mp3 -c:a libopus -b:a 64k -application voip output.opus

# Any format to FLAC (lossless archive)
ffmpeg -i input.wav -c:a flac -compression_level 8 output.flac
```

### Video Thumbnail Extraction

```bash
# Single frame at timestamp
ffmpeg -i input.mp4 -ss 00:00:10 -frames:v 1 -q:v 2 thumbnail.jpg

# Multiple frames — one every 60 seconds
ffmpeg -i input.mp4 -vf "fps=1/60" -q:v 2 thumb_%04d.jpg

# Scene-detection thumbnails (keyframes on scene changes)
ffmpeg -i input.mp4 -vf "select='gt(scene,0.4)',showinfo" -vsync vfr -q:v 2 scene_%04d.jpg

# Grid of thumbnails (4x4 tile sheet)
ffmpeg -i input.mp4 -vf "fps=1/30,scale=320:180,tile=4x4" -frames:v 1 grid.jpg

# Thumbnail at 10% into the video (useful for previews)
ffmpeg -i input.mp4 -vf "thumbnail=300" -frames:v 1 -q:v 2 best_thumb.jpg
```

### Video Trimming / Clipping

```bash
# Trim by start time and end time (fast seek — put -ss before -i)
ffmpeg -ss 00:01:30 -to 00:03:45 -i input.mp4 -c copy clip.mp4

# Trim by start time and duration
ffmpeg -ss 00:01:30 -i input.mp4 -t 00:02:15 -c copy clip.mp4

# Trim with re-encoding (frame-accurate, slower)
ffmpeg -i input.mp4 -ss 00:01:30 -to 00:03:45 -c:v libx264 -crf 23 -c:a aac clip.mp4

# Extract last 30 seconds
ffmpeg -sseof -30 -i input.mp4 -c copy last30.mp4
```

### Video Concatenation

```bash
# Step 1: Create a file list (concat.txt)
# file 'part1.mp4'
# file 'part2.mp4'
# file 'part3.mp4'

# Step 2: Concatenate (same codec — no re-encoding)
ffmpeg -f concat -safe 0 -i concat.txt -c copy output.mp4

# Concatenate with re-encoding (different codecs/resolutions)
ffmpeg -f concat -safe 0 -i concat.txt -c:v libx264 -crf 23 -c:a aac output.mp4

# Two files directly (filter method — handles different formats)
ffmpeg -i part1.mp4 -i part2.mp4 -filter_complex "[0:v:0][0:a:0][1:v:0][1:a:0]concat=n=2:v=1:a=1[outv][outa]" -map "[outv]" -map "[outa]" output.mp4
```

### HLS Segmentation for Streaming

```bash
# Basic HLS with 6-second segments
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset fast \
  -c:a aac -b:a 128k \
  -hls_time 6 -hls_list_size 0 -hls_segment_filename "segment_%03d.ts" \
  playlist.m3u8

# Multi-bitrate HLS (adaptive streaming)
ffmpeg -i input.mp4 \
  -filter_complex "[0:v]split=3[v1][v2][v3]; \
    [v1]scale=1920:1080[v1out]; \
    [v2]scale=1280:720[v2out]; \
    [v3]scale=854:480[v3out]" \
  -map "[v1out]" -c:v:0 libx264 -b:v:0 5000k -preset fast \
  -map "[v2out]" -c:v:1 libx264 -b:v:1 2500k -preset fast \
  -map "[v3out]" -c:v:2 libx264 -b:v:2 1000k -preset fast \
  -map a:0 -c:a aac -b:a 128k \
  -f hls -hls_time 6 -hls_list_size 0 \
  -master_pl_name master.m3u8 \
  -var_stream_map "v:0,a:0 v:1,a:0 v:2,a:0" \
  stream_%v/playlist.m3u8
```

### Subtitle Burning (Hardcoded)

```bash
# Burn SRT subtitles into video
ffmpeg -i input.mp4 -vf "subtitles=subs.srt" -c:v libx264 -crf 23 -c:a copy output.mp4

# Burn with custom font styling
ffmpeg -i input.mp4 -vf "subtitles=subs.srt:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2'" -c:v libx264 -crf 23 -c:a copy output.mp4

# Burn ASS/SSA subtitles (preserves styling)
ffmpeg -i input.mp4 -vf "ass=subs.ass" -c:v libx264 -crf 23 -c:a copy output.mp4
```

### Audio Normalization (EBU R128)

```bash
# Two-pass loudness normalization (most accurate)
# Pass 1: Measure
ffmpeg -i input.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null NUL

# Pass 2: Apply (use measured_I, measured_TP, measured_LRA, measured_thresh from pass 1)
ffmpeg -i input.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=-23.5:measured_TP=-7.2:measured_LRA=14.3:measured_thresh=-34.5:linear=true -c:v copy output.mp4

# Single-pass normalization (simpler, slightly less accurate)
ffmpeg -i input.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:v copy output.mp4
```

### Video Compression (CRF Quality Control)

```bash
# Light compression (visually lossless) — CRF 18
ffmpeg -i input.mp4 -c:v libx264 -crf 18 -preset slow -c:a copy output.mp4

# Medium compression (good quality) — CRF 23
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k output.mp4

# Heavy compression (small file) — CRF 28
ffmpeg -i input.mp4 -c:v libx264 -crf 28 -preset fast -c:a aac -b:a 96k output.mp4

# Target file size (two-pass encoding for ~100MB target on a 10min video)
ffmpeg -i input.mp4 -c:v libx264 -b:v 1300k -pass 1 -an -f null NUL
ffmpeg -i input.mp4 -c:v libx264 -b:v 1300k -pass 2 -c:a aac -b:a 128k output.mp4
```

### Watermark Overlay

```bash
# Image watermark — bottom-right corner with padding
ffmpeg -i input.mp4 -i watermark.png -filter_complex "overlay=W-w-10:H-h-10" -c:v libx264 -crf 23 -c:a copy output.mp4

# Semi-transparent watermark
ffmpeg -i input.mp4 -i watermark.png -filter_complex "[1:v]format=rgba,colorchannelmixer=aa=0.3[wm];[0:v][wm]overlay=W-w-10:H-h-10" -c:v libx264 -crf 23 -c:a copy output.mp4

# Text watermark
ffmpeg -i input.mp4 -vf "drawtext=text='My Channel':fontsize=24:fontcolor=white@0.5:x=W-tw-10:y=H-th-10" -c:v libx264 -crf 23 -c:a copy output.mp4
```

### GIF Creation from Video

```bash
# High-quality GIF (two-pass with palette)
ffmpeg -i input.mp4 -ss 00:00:05 -t 3 -vf "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" output.gif

# Simple GIF (lower quality, one command)
ffmpeg -i input.mp4 -ss 00:00:05 -t 3 -vf "fps=10,scale=320:-1" output.gif

# GIF with text overlay
ffmpeg -i input.mp4 -ss 00:00:05 -t 3 -vf "fps=15,scale=480:-1:flags=lanczos,drawtext=text='Hello':fontsize=36:fontcolor=white:x=(w-tw)/2:y=(h-th)/2,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" output.gif
```

---

## Node.js Integration with fluent-ffmpeg

### Installation

```bash
npm install fluent-ffmpeg
# ffmpeg binary must be in PATH, or set path explicitly
```

### Basic Usage Pattern

```javascript
import ffmpeg from 'fluent-ffmpeg';

function convertVideo(input, output) {
  return new Promise((resolve, reject) => {
    ffmpeg(input)
      .output(output)
      .videoCodec('libx264')
      .audioCodec('aac')
      .outputOptions(['-crf 23', '-preset medium'])
      .on('end', () => resolve(output))
      .on('error', (err) => reject(err))
      .run();
  });
}
```

### Progress Tracking

```javascript
import ffmpeg from 'fluent-ffmpeg';

function convertWithProgress(input, output, onProgress) {
  return new Promise((resolve, reject) => {
    ffmpeg(input)
      .output(output)
      .videoCodec('libx264')
      .audioCodec('aac')
      .outputOptions(['-crf 23', '-preset fast'])
      .on('start', (cmd) => {
        console.log('Running:', cmd);
      })
      .on('progress', (progress) => {
        // progress.percent, progress.timemark, progress.currentFps
        if (onProgress) onProgress(progress);
        console.log(`Progress: ${Math.round(progress.percent || 0)}%`);
      })
      .on('end', () => resolve(output))
      .on('error', (err, stdout, stderr) => {
        console.error('FFmpeg stderr:', stderr);
        reject(err);
      })
      .run();
  });
}
```

### Error Handling

```javascript
import ffmpeg from 'fluent-ffmpeg';

async function safeConvert(input, output) {
  // Probe input first to validate
  const metadata = await new Promise((resolve, reject) => {
    ffmpeg.ffprobe(input, (err, data) => {
      if (err) reject(new Error(`Cannot read input: ${err.message}`));
      else resolve(data);
    });
  });

  const duration = metadata.format.duration;
  const hasVideo = metadata.streams.some(s => s.codec_type === 'video');
  const hasAudio = metadata.streams.some(s => s.codec_type === 'audio');

  console.log(`Input: ${duration}s, video=${hasVideo}, audio=${hasAudio}`);

  return new Promise((resolve, reject) => {
    const cmd = ffmpeg(input).output(output);

    if (hasVideo) cmd.videoCodec('libx264').outputOptions(['-crf 23']);
    if (hasAudio) cmd.audioCodec('aac').audioBitrate('128k');

    cmd
      .on('end', () => resolve({ output, duration }))
      .on('error', (err, stdout, stderr) => {
        // Common errors and their fixes
        if (stderr?.includes('No such file or directory')) {
          reject(new Error('Input file not found'));
        } else if (stderr?.includes('Invalid data found')) {
          reject(new Error('Corrupted or unsupported input format'));
        } else if (stderr?.includes('codec not currently supported')) {
          reject(new Error('Codec not available — install ffmpeg with full codec support'));
        } else {
          reject(new Error(`FFmpeg error: ${err.message}`));
        }
      })
      .run();
  });
}
```

### Streaming Output

```javascript
import ffmpeg from 'fluent-ffmpeg';
import { PassThrough } from 'stream';

function streamConvert(inputPath) {
  const passthrough = new PassThrough();

  ffmpeg(inputPath)
    .format('mp4')
    .videoCodec('libx264')
    .audioCodec('aac')
    .outputOptions(['-crf 23', '-movflags frag_keyframe+empty_moov']) // Required for MP4 streaming
    .pipe(passthrough, { end: true });

  return passthrough;
}

// Express.js usage
app.get('/stream/:filename', (req, res) => {
  const inputPath = `/uploads/${req.params.filename}`;
  res.setHeader('Content-Type', 'video/mp4');
  streamConvert(inputPath).pipe(res);
});
```

---

## Hardware Acceleration

| Platform | Encoder | Flag | Example |
|----------|---------|------|---------|
| NVIDIA (Windows/Linux) | NVENC | `-c:v h264_nvenc` | `ffmpeg -i in.mp4 -c:v h264_nvenc -preset p4 -cq 23 out.mp4` |
| NVIDIA HEVC | NVENC | `-c:v hevc_nvenc` | `ffmpeg -i in.mp4 -c:v hevc_nvenc -preset p4 -cq 28 out.mp4` |
| macOS (Apple Silicon) | VideoToolbox | `-c:v h264_videotoolbox` | `ffmpeg -i in.mp4 -c:v h264_videotoolbox -q:v 60 out.mp4` |
| macOS HEVC | VideoToolbox | `-c:v hevc_videotoolbox` | `ffmpeg -i in.mp4 -c:v hevc_videotoolbox -q:v 60 out.mp4` |
| Linux Intel | VAAPI | `-c:v h264_vaapi` | `ffmpeg -vaapi_device /dev/dri/renderD128 -i in.mp4 -vf 'format=nv12,hwupload' -c:v h264_vaapi out.mp4` |
| Linux AMD | VAAPI | `-c:v h264_vaapi` | Same as Intel VAAPI |
| Windows Intel | QSV | `-c:v h264_qsv` | `ffmpeg -i in.mp4 -c:v h264_qsv -global_quality 23 out.mp4` |

**Check available encoders:**
```bash
ffmpeg -encoders 2>/dev/null | grep -E "nvenc|videotoolbox|vaapi|qsv"
```

---

## Quality Presets

| Preset | Resolution | Video Codec | CRF | Audio | Bitrate (approx) | Use Case |
|--------|-----------|-------------|-----|-------|-------------------|----------|
| **Web** | 1080p | H.264 | 23 | AAC 128k | 3-5 Mbps | Website embeds, social media |
| **Mobile** | 720p | H.264 | 26 | AAC 96k | 1-2 Mbps | Mobile apps, low bandwidth |
| **Archive** | Original | H.264 | 18 | AAC 256k | 8-15 Mbps | Long-term storage, master copies |
| **Streaming** | Adaptive | H.264 | 21 | AAC 128k | 1-5 Mbps | HLS/DASH adaptive bitrate |
| **Thumbnail** | 320px wide | MJPEG | q:v 2 | None | N/A | Preview images |

**Quick preset commands:**

```bash
# Web preset
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -vf scale=-2:1080 -c:a aac -b:a 128k web.mp4

# Mobile preset
ffmpeg -i input.mp4 -c:v libx264 -crf 26 -preset fast -vf scale=-2:720 -c:a aac -b:a 96k mobile.mp4

# Archive preset
ffmpeg -i input.mp4 -c:v libx264 -crf 18 -preset slow -c:a aac -b:a 256k archive.mp4
```

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `No such file or directory` | Input file path wrong or ffmpeg not in PATH | Verify path; run `ffmpeg -version` to confirm installation |
| `Invalid data found when processing input` | Corrupted file or unsupported container | Try `ffprobe input.mp4` to diagnose; re-download source |
| `Unknown encoder 'libx264'` | FFmpeg built without x264 support | Install full build: `brew install ffmpeg` / `choco install ffmpeg-full` |
| `Output file is empty` | `-c copy` used with incompatible trim points | Use re-encoding instead of `-c copy` for frame-accurate cuts |
| `moov atom not found` | Incomplete MP4 (failed download/recording) | Try `ffmpeg -i broken.mp4 -c copy -movflags faststart fixed.mp4` |
| `Avi header missing` | Wrong file extension for actual format | Run `ffprobe` to detect real format, rename accordingly |
| `height not divisible by 2` | Scaling produced odd dimension | Use `scale=-2:720` (the `-2` ensures even numbers) |
| `NVENC not available` | No NVIDIA GPU or drivers too old | Update GPU drivers; fall back to `libx264` |
| `Too many packets buffered for output stream` | Encoding too slow for input rate | Add `-max_muxing_queue_size 1024` |
| `Permission denied` | Output path not writable | Check directory permissions; avoid writing to system dirs |
