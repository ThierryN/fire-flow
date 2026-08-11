# Video Streaming Integration
**Description:** Complete guide for adding video streaming to web applications. Covers Mux (managed), self-hosted HLS with FFmpeg, DRM basics, progress tracking, adaptive bitrate, and Cloudflare Stream.

**When to use:** Any project that needs video playback beyond a simple `<video>` tag — course platforms, media sites, live streaming, video-on-demand with adaptive quality, DRM-protected content, or resume-from-position functionality.

---

## Path A: Mux (Recommended for Most Projects)

Mux is a video API platform ("Stripe of video") — handles encoding, storage, delivery, and analytics. Best choice when you want to ship fast and not manage infrastructure.

Install: `npm install @mux/mux-node @mux/mux-player-react`

### 1. Upload and Create Asset (Server)

```ts
// server/services/mux.ts
import Mux from "@mux/mux-node";

const mux = new Mux({
  tokenId: process.env.MUX_TOKEN_ID!,
  tokenSecret: process.env.MUX_TOKEN_SECRET!,
});

// Upload from a URL (e.g., after user uploads to S3/R2)
export async function createAssetFromUrl(videoUrl: string) {
  const asset = await mux.video.assets.create({
    input: [{ url: videoUrl }],
    playback_policy: ["public"],        // or "signed" for private content
    encoding_tier: "smart",             // smart = faster + cheaper, baseline = premium quality
    max_resolution_tier: "1080p",
  });

  return {
    assetId: asset.id,
    playbackId: asset.playback_ids?.[0]?.id,
    status: asset.status, // "preparing" → "ready"
  };
}

// Direct upload — returns a URL the client can PUT to
export async function createDirectUpload() {
  const upload = await mux.video.uploads.create({
    cors_origin: process.env.APP_URL,
    new_asset_settings: {
      playback_policy: ["public"],
      encoding_tier: "smart",
    },
  });

  return {
    uploadId: upload.id,
    uploadUrl: upload.url, // Client uploads directly here via PUT
  };
}
```

### 2. Client-Side Direct Upload

```ts
// client/services/upload.ts
import * as UpChunk from "@mux/upchunk";

export function uploadVideo(
  file: File,
  uploadUrl: string,
  onProgress: (pct: number) => void
) {
  const upload = UpChunk.createUpload({
    endpoint: uploadUrl,
    file,
    chunkSize: 5120, // 5MB chunks
  });

  upload.on("progress", (detail) => {
    onProgress(Math.round(detail.detail));
  });

  return new Promise<void>((resolve, reject) => {
    upload.on("success", () => resolve());
    upload.on("error", (err) => reject(err.detail));
  });
}
```

### 3. Webhook Handling (Server)

```ts
// server/routes/webhooks/mux.ts
import { type Request, type Response } from "express";
import Mux from "@mux/mux-node";

const webhooks = new Mux.Webhooks();

export async function handleMuxWebhook(req: Request, res: Response) {
  const event = webhooks.unwrap(
    req.body,
    req.headers,
    process.env.MUX_WEBHOOK_SECRET!
  );

  switch (event.type) {
    case "video.asset.ready": {
      const asset = event.data;
      const playbackId = asset.playback_ids?.[0]?.id;
      const duration = asset.duration; // seconds

      // Update your database
      await db.videos.update({
        where: { muxAssetId: asset.id },
        data: { status: "ready", playbackId, duration },
      });
      break;
    }

    case "video.asset.errored": {
      const asset = event.data;
      await db.videos.update({
        where: { muxAssetId: asset.id },
        data: { status: "error", errorMessage: JSON.stringify(asset.errors) },
      });
      break;
    }

    case "video.asset.deleted": {
      // Clean up local references
      break;
    }
  }

  res.sendStatus(200);
}
```

### 4. Embed with Mux Player (React)

```tsx
// client/components/VideoPlayer.tsx
import MuxPlayer from "@mux/mux-player-react";

interface VideoPlayerProps {
  playbackId: string;
  title: string;
  onTimeUpdate?: (currentTime: number) => void;
  startTime?: number;
}

export function VideoPlayer({ playbackId, title, onTimeUpdate, startTime }: VideoPlayerProps) {
  return (
    <MuxPlayer
      playbackId={playbackId}
      metadata={{
        video_title: title,
        viewer_user_id: "user-123", // for Mux Data analytics
      }}
      startTime={startTime}
      accentColor="#7c3aed"
      thumbnailTime={10}
      onTimeUpdate={(e) => {
        const target = e.target as HTMLVideoElement;
        onTimeUpdate?.(target.currentTime);
      }}
      style={{ aspectRatio: "16/9", width: "100%" }}
    />
  );
}
```

### 5. Auto-Generated Captions

```ts
// Request auto-generated captions when creating the asset
const asset = await mux.video.assets.create({
  input: [{ url: videoUrl }],
  playback_policy: ["public"],
  auto_generated_captions: [
    {
      language_code: "en",
      name: "English (auto)",
    },
  ],
});

// Captions become available via the standard <track> mechanism in Mux Player
// No additional client-side code needed — Mux Player handles it automatically
```

### 6. Signed URLs for Private Content

```ts
// server/services/mux.ts
import jwt from "jsonwebtoken";

const MUX_SIGNING_KEY_ID = process.env.MUX_SIGNING_KEY_ID!;
const MUX_SIGNING_PRIVATE_KEY = Buffer.from(
  process.env.MUX_SIGNING_PRIVATE_KEY_BASE64!,
  "base64"
).toString("ascii");

export function getSignedPlaybackToken(playbackId: string, expiresInSec = 3600) {
  return jwt.sign(
    {
      sub: playbackId,
      aud: "v",                           // "v" for video, "t" for thumbnail, "s" for storyboard
      exp: Math.floor(Date.now() / 1000) + expiresInSec,
      kid: MUX_SIGNING_KEY_ID,
    },
    MUX_SIGNING_PRIVATE_KEY,
    { algorithm: "RS256" }
  );
}
```

```tsx
// Client: pass token to Mux Player
<MuxPlayer
  playbackId={playbackId}
  tokens={{
    playback: signedToken,
    thumbnail: thumbnailToken,
    storyboard: storyboardToken,
  }}
/>
```

### Mux Pricing Reference (2025)

| Feature | Cost |
|---------|------|
| Video encoding | $0.015/min |
| Video storage | $0.0055/GB/mo |
| Video delivery | $0.00096/min (streaming) |
| Live streaming | $0.025/min (encoding) |

---

## Path B: Self-Hosted HLS (Full Control)

Use when: you need full control over infrastructure, have existing CDN/storage, or need to minimize per-minute costs at scale.

### FFmpeg: Generate HLS with Multiple Renditions

```bash
#!/bin/bash
# transcode.sh — Generate adaptive bitrate HLS from any input video

INPUT="$1"
OUTPUT_DIR="$2"

mkdir -p "$OUTPUT_DIR/360p" "$OUTPUT_DIR/720p" "$OUTPUT_DIR/1080p"

ffmpeg -i "$INPUT" \
  -map 0:v -map 0:a -map 0:v -map 0:a -map 0:v -map 0:a \
  \
  -c:v:0 libx264 -b:v:0 800k  -maxrate:v:0 856k  -bufsize:v:0 1200k -s:v:0 640x360  -profile:v:0 main  -level 3.0 \
  -c:v:1 libx264 -b:v:1 2500k -maxrate:v:1 2800k -bufsize:v:1 4200k -s:v:1 1280x720 -profile:v:1 main  -level 3.1 \
  -c:v:2 libx264 -b:v:2 5000k -maxrate:v:2 5500k -bufsize:v:2 8000k -s:v:2 1920x1080 -profile:v:2 high -level 4.0 \
  \
  -c:a aac -b:a 128k -ar 48000 \
  \
  -var_stream_map "v:0,a:0 v:1,a:1 v:2,a:2" \
  -master_pl_name master.m3u8 \
  -f hls \
  -hls_time 6 \
  -hls_list_size 0 \
  -hls_segment_filename "$OUTPUT_DIR/%v/seg%03d.ts" \
  "$OUTPUT_DIR/%v/index.m3u8"

echo "Done. Master playlist: $OUTPUT_DIR/master.m3u8"
```

### Bitrate Ladder Recommendations

| Rendition | Resolution | Video Bitrate | Audio | Use Case |
|-----------|-----------|---------------|-------|----------|
| 360p | 640x360 | 800 kbps | 96k | Mobile / slow connections |
| 720p | 1280x720 | 2,500 kbps | 128k | Default / most devices |
| 1080p | 1920x1080 | 5,000 kbps | 192k | Desktop / high bandwidth |

### HLS.js Player Integration

```tsx
// client/components/HlsPlayer.tsx
import { useEffect, useRef } from "react";
import Hls from "hls.js";

interface HlsPlayerProps {
  src: string; // URL to master.m3u8
  startTime?: number;
  onTimeUpdate?: (time: number) => void;
}

export function HlsPlayer({ src, startTime, onTimeUpdate }: HlsPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const hlsRef = useRef<Hls | null>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    if (Hls.isSupported()) {
      const hls = new Hls({
        startLevel: -1,           // auto-detect best quality
        capLevelToPlayerSize: true, // don't load 1080p on a 360px container
      });

      hls.loadSource(src);
      hls.attachMedia(video);

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        if (startTime) video.currentTime = startTime;
        video.play().catch(() => {}); // autoplay may be blocked
      });

      hls.on(Hls.Events.ERROR, (_, data) => {
        if (data.fatal) {
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              hls.startLoad(); // retry
              break;
            case Hls.ErrorTypes.MEDIA_ERROR:
              hls.recoverMediaError();
              break;
            default:
              hls.destroy();
              break;
          }
        }
      });

      hlsRef.current = hls;
      return () => hls.destroy();
    } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
      // Safari: native HLS support
      video.src = src;
      if (startTime) video.currentTime = startTime;
    }
  }, [src, startTime]);

  return (
    <video
      ref={videoRef}
      controls
      style={{ width: "100%", aspectRatio: "16/9" }}
      onTimeUpdate={() => {
        if (videoRef.current) onTimeUpdate?.(videoRef.current.currentTime);
      }}
    />
  );
}
```

### Serving from S3 / MinIO

```ts
// server/routes/video.ts
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const s3 = new S3Client({
  endpoint: process.env.S3_ENDPOINT,      // MinIO: "http://localhost:9000"
  region: process.env.S3_REGION || "us-east-1",
  credentials: {
    accessKeyId: process.env.S3_ACCESS_KEY!,
    secretAccessKey: process.env.S3_SECRET_KEY!,
  },
  forcePathStyle: true, // Required for MinIO
});

export async function getVideoPlaylistUrl(videoId: string) {
  const command = new GetObjectCommand({
    Bucket: "videos",
    Key: `${videoId}/master.m3u8`,
  });

  // Signed URL expires in 4 hours
  return getSignedUrl(s3, command, { expiresIn: 14400 });
}
```

**CORS for HLS segments:** When serving from S3/MinIO, configure CORS to allow your domain to fetch `.m3u8` and `.ts` files. The player makes cross-origin requests for each segment.

---

## DRM Basics

DRM is needed when: you have premium paid content, licensing agreements require it, or you must prevent screen recording and redistribution.

### Overview

| DRM System | Browser / Platform | License Server |
|---|---|---|
| Widevine (Google) | Chrome, Firefox, Android, Smart TVs | Google or self-hosted (Shaka Packager) |
| FairPlay (Apple) | Safari, iOS, tvOS | Apple-provided, self-hosted key server |
| PlayReady (Microsoft) | Edge, Xbox, Windows apps | Microsoft or self-hosted |

### Simplified Flow

```
1. Client requests playback → Server returns encrypted HLS/DASH manifest
2. Player detects DRM → Requests license from your license server
3. License server validates user → Returns decryption key
4. Player decrypts and plays segments in real-time
```

### Recommendation

For most projects, use a DRM vendor (Mux, BuyDRM, PallyCon, Axinom) rather than implementing from scratch. Mux handles Widevine + FairPlay automatically when you set `playback_policy: ["signed"]`.

---

## Progress Tracking — Resume from Last Position

```tsx
// client/hooks/useVideoProgress.ts
import { useCallback, useRef } from "react";

const SAVE_INTERVAL_MS = 5000; // Save every 5 seconds

export function useVideoProgress(videoId: string, userId: string) {
  const lastSaved = useRef(0);

  const saveProgress = useCallback(
    async (currentTime: number, duration: number) => {
      const now = Date.now();
      if (now - lastSaved.current < SAVE_INTERVAL_MS) return;
      lastSaved.current = now;

      const progress = duration > 0 ? currentTime / duration : 0;

      await fetch("/api/video-progress", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          videoId,
          userId,
          currentTime: Math.floor(currentTime),
          progress: Math.round(progress * 100), // 0-100
          completed: progress >= 0.9,             // Mark complete at 90%
        }),
      });
    },
    [videoId, userId]
  );

  const loadProgress = useCallback(async () => {
    const res = await fetch(`/api/video-progress?videoId=${videoId}&userId=${userId}`);
    if (!res.ok) return 0;
    const data = await res.json();
    return data.currentTime ?? 0;
  }, [videoId, userId]);

  return { saveProgress, loadProgress };
}
```

```ts
// server/routes/video-progress.ts — Database schema (Supabase/PostgreSQL)
/*
CREATE TABLE video_progress (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) NOT NULL,
  video_id UUID REFERENCES videos(id) NOT NULL,
  current_time INTEGER DEFAULT 0,       -- seconds
  progress INTEGER DEFAULT 0,           -- 0-100 percent
  completed BOOLEAN DEFAULT FALSE,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, video_id)
);

CREATE INDEX idx_video_progress_user ON video_progress(user_id);
*/
```

---

## Adaptive Bitrate (ABR) — How It Works

ABR automatically adjusts video quality based on the viewer's network conditions:

1. **Master playlist** lists available renditions (360p, 720p, 1080p)
2. **Player downloads a segment** and measures download speed
3. **ABR algorithm** compares available bandwidth to rendition bitrates
4. **Player switches** to the highest quality the network can sustain without buffering

**Key settings in HLS.js:**

```ts
const hls = new Hls({
  startLevel: -1,               // -1 = auto-detect, 0 = start at lowest
  capLevelToPlayerSize: true,    // Don't load 1080p if player is 360px wide
  maxBufferLength: 30,           // Buffer up to 30 seconds ahead
  maxMaxBufferLength: 60,        // Hard cap on buffer
  abrEwmaDefaultEstimate: 500000, // Initial bandwidth estimate (bps)
});
```

**When to use ABR:** Always, for any video over 30 seconds. Single-rendition is only acceptable for short clips or controlled LAN environments.

---

## Cloudflare Stream (Simpler Alternative)

Cloudflare Stream is a good middle ground — simpler than DIY HLS, cheaper than Mux at scale.

```ts
// Upload via API
const response = await fetch(
  `https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/stream`,
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${CF_API_TOKEN}`,
    },
    body: JSON.stringify({
      url: "https://your-bucket.s3.amazonaws.com/video.mp4",
    }),
  }
);

const { result } = await response.json();
// result.uid = video ID
// result.playback.hls = HLS URL
// result.playback.dash = DASH URL
```

```tsx
// Embed with iframe (simplest)
<iframe
  src={`https://customer-${SUBDOMAIN}.cloudflarestream.com/${videoUid}/iframe`}
  allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
  style={{ border: "none", width: "100%", aspectRatio: "16/9" }}
/>

// Or use Stream Player Web Component
// <script src="https://embed.cloudflarestream.com/embed/sdk.latest.js" />
<stream src={videoUid} controls />
```

**Cloudflare Stream pricing (2025):** $1/1000 min stored + $1/1000 min delivered. No encoding fees.

---

## Quick Decision Matrix

| Factor | Mux | Self-hosted HLS | Cloudflare Stream |
|--------|-----|-----------------|-------------------|
| Setup time | 1 hour | 1-2 days | 2 hours |
| Encoding | Managed | You run FFmpeg | Managed |
| CDN | Included | BYO (S3+CF) | Included |
| DRM | Built-in (signed URLs) | DIY | Token auth |
| Analytics | Mux Data (detailed) | DIY | Basic |
| Cost at 10K views/mo | ~$15 | ~$5 (infra) | ~$10 |
| Cost at 1M views/mo | ~$1,500 | ~$200 (infra + CDN) | ~$1,000 |
| Best for | Most projects, fast ship | High scale, full control | Mid-range, Cloudflare stack |

---

