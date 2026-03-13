# Live Teaching Studio — Real-Time Transcription & Recording Pattern

> **Category:** LMS Patterns / Real-Time Features
> **Created:** 2026-02-23
> **Project:** MERN Community LMS
> **Reuse:** Any project needing live speech-to-text, audio recording, AI summarization

---

## Overview

Browser-based live teaching studio that combines real-time speech-to-text transcription with audio recording, smart punctuation, domain-specific vocabulary correction, bookmarks, AI summary generation, and integration with downstream systems (Knowledge Base, Content Forge).

**Zero external transcription services required** — uses the browser's native Web Speech API.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  BROWSER (Client)                        │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Web Speech   │  │ MediaRecorder│  │  React UI    │  │
│  │ API          │  │ (WebM/Opus)  │  │  (Controls)  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
│         ▼                 │                 │           │
│  ┌──────────────────┐     │                 │           │
│  │ Speech Pipeline   │     │                 │           │
│  │ 1. Voice correct  │     │                 │           │
│  │ 2. Bible refs     │     │                 │           │
│  │ 3. Punctuation    │     │                 │           │
│  └──────┬───────────┘     │                 │           │
│         │                 │                 │           │
│         ▼                 ▼                 │           │
│  ┌──────────────────────────┐               │           │
│  │  Auto-save every 30s     │◄──────────────┘           │
│  │  PUT /live-teaching/:id  │                           │
│  └──────────┬───────────────┘                           │
│             │                                           │
└─────────────┼───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│                    SERVER (Node.js)                      │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Session CRUD │  │ Audio Upload │  │ AI Summary   │  │
│  │              │  │ (Multer)     │  │ (Gemini)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  PostgreSQL: live_teaching_sessions              │   │
│  │  - transcript TEXT, segments JSONB               │   │
│  │  - audio_url TEXT, bookmarks JSONB               │   │
│  │  - summary TEXT, metadata JSONB                  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  Integrations:                                          │
│  ├─► Knowledge Base (INSERT knowledge_sources)          │
│  └─► Content Forge (sessionStorage handoff)             │
└─────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. Web Speech API (SpeechRecognition)

```javascript
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.continuous = true;
recognition.interimResults = true;
recognition.lang = 'en-US';

recognition.onresult = (event) => {
  // Process only final results for saved transcript
  // Show interim results for live preview
  for (let i = event.resultIndex; i < event.results.length; i++) {
    if (event.results[i].isFinal) {
      const text = event.results[i][0].transcript.trim();
      // Run through speech pipeline
      const processed = addSmartPunctuation(
        formatBibleReferences(
          applyCorrections(text, voiceProfile.corrections)
        )
      );
      appendToTranscript(processed);
    }
  }
};
```

**Key insight:** `recognition.continuous = true` keeps listening but Chrome stops after ~60s of silence. Re-start on `onend` event for continuous recording.

### 2. Speech Processing Pipeline

Three-stage processing applied to every finalized speech segment:

| Stage | Function | Purpose |
|-------|----------|---------|
| 1 | `applyCorrections(text, corrections)` | Voice profile vocabulary corrections (e.g., "profit" → "prophet") |
| 2 | `formatBibleReferences(text)` | Auto-detect and format "Genesis 1:1" style references |
| 3 | `addSmartPunctuation(text)` | Add ? for question words, . for 4+ word statements |

### 3. Audio Recording (MediaRecorder API)

```javascript
function useAudioRecorder() {
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'  // Tiny files: ~8-10MB for 2 hours
    });
    recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
    recorder.start(5000); // Chunk every 5s
  };

  const stopRecording = () => {
    return new Promise(resolve => {
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        resolve(blob);
      };
      recorder.stop();
    });
  };

  return { startRecording, stopRecording, pauseRecording, resumeRecording, isRecording };
}
```

**Why WebM/Opus over MP3/WAV:**
- WAV: ~1.2GB for 2 hours (uncompressed)
- MP3: ~120MB for 2 hours (needs encoding library)
- WebM/Opus: ~8-10MB for 2 hours (native browser support, no library needed)

### 4. Live Bookmarks

Timestamped markers set during recording:

```javascript
const handleAddBookmark = () => {
  const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
  setBookmarks(prev => [...prev, {
    label: `Bookmark ${prev.length + 1}`,
    timestamp_seconds: elapsed,
    created_at: new Date().toISOString()
  }]);
};
```

Stored as JSONB array in PostgreSQL. Displayed in session detail and included in AI summary context.

### 5. Voice Calibration Profile

Instructor-specific vocabulary and correction rules:

```sql
CREATE TABLE voice_calibration (
  instructor_id UUID PRIMARY KEY REFERENCES profiles(id),
  vocabulary JSONB DEFAULT '[]',     -- Domain terms
  corrections JSONB DEFAULT '[]',    -- [{from: "profit", to: "prophet"}, ...]
  calibration_results JSONB DEFAULT '[]',
  settings JSONB DEFAULT '{"auto_correct": true, "language": "en-US"}'
);
```

### 6. AI Summary (Server-Side)

```javascript
const provider = await AIProviderFactory.getDefaultProvider(); // Gemini
const messages = [
  { role: 'system', content: 'You are a teaching assistant...' },
  { role: 'user', content: `Title: ${title}\nTranscript:\n${transcript.slice(0, 15000)}` }
];
const result = await provider.chat(messages, { max_tokens: 1500 });
```

### 7. Integration Patterns

**Knowledge Base:** Direct INSERT into existing pipeline
```javascript
await sql`INSERT INTO knowledge_sources (uploaded_by, title, file_type, file_size, status, raw_text)
  VALUES (${userId}, ${title}, 'text_paste', ${fileSize}, 'processing', ${transcript})`;
```

**Content Forge:** sessionStorage handoff + navigation
```javascript
sessionStorage.setItem('forgeTranscript', JSON.stringify({ title, transcript, summary }));
navigate(`/admin/courses/${courseId}/forge`);
```

---

## Database Schema

```sql
-- Migration 156
CREATE TABLE live_teaching_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  instructor_id UUID NOT NULL REFERENCES profiles(id),
  title VARCHAR(500) DEFAULT 'Untitled Session',
  transcript TEXT DEFAULT '',
  segments JSONB DEFAULT '[]',
  duration_seconds INTEGER DEFAULT 0,
  word_count INTEGER DEFAULT 0,
  status VARCHAR(50) CHECK (status IN ('recording','completed','processing','archived')),
  course_id UUID REFERENCES courses(id),
  lesson_id UUID REFERENCES lessons(id),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Migration 157
CREATE TABLE voice_calibration (...);

-- Migration 158
ALTER TABLE live_teaching_sessions ADD COLUMN audio_url TEXT;
ALTER TABLE live_teaching_sessions ADD COLUMN bookmarks JSONB DEFAULT '[]';
ALTER TABLE live_teaching_sessions ADD COLUMN summary TEXT;
```

---

## API Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | /live-teaching/ | Create new session |
| GET | /live-teaching/ | List sessions (paginated) |
| GET | /live-teaching/:id | Get full session |
| PUT | /live-teaching/:id | Auto-save transcript |
| PUT | /live-teaching/:id/complete | Mark completed |
| DELETE | /live-teaching/:id | Delete session |
| GET | /live-teaching/voice-profile/me | Get voice profile |
| PUT | /live-teaching/voice-profile/me | Upsert voice profile |
| POST | /live-teaching/:id/audio | Upload WebM audio |
| POST | /live-teaching/:id/summarize | Generate AI summary |
| POST | /live-teaching/:id/send-to-knowledge | Send to KB pipeline |

All routes require `protect` + `authorize('admin', 'instructor')`.

---

## File Structure

```
client/src/pages/admin/LiveTeaching.jsx    # ~2120 lines, full studio
server/controllers/liveTeachingController.js
server/routes/liveTeachingRoutes.js
server/config/multerAudio.js               # Pre-existing, WebM/200MB
server/migrations/156_create_live_teaching_sessions.sql
server/migrations/157_create_voice_calibration.sql
server/migrations/158_add_live_teaching_audio_bookmarks_summary.sql
```

---

## Reuse for Viral Clip / Social Media Project

This pattern can be adapted for:

1. **Viral clip extraction** — Use bookmarks to mark "clip-worthy" moments, then extract audio segments between bookmark timestamps
2. **Social media content generation** — Pipe AI summary through Content Forge to generate social posts, infographics, short-form content
3. **Podcast production** — WebM/Opus recording + AI summary → show notes
4. **Meeting notes** — Same transcription pipeline with business-focused summary prompts
5. **Student review materials** — Auto-distribute transcripts and summaries to enrolled students

---

## Gotchas & Lessons

1. **Chrome kills SpeechRecognition after ~60s silence** — Always restart on `onend` event
2. **MediaRecorder codec support varies** — Check `MediaRecorder.isTypeSupported('audio/webm;codecs=opus')` and fall back
3. **Web Speech API needs HTTPS** in production (works on localhost for dev)
4. **Auto-save interval of 30s** prevents data loss for 2+ hour sessions
5. **Multer audio config** must accept `audio/webm` MIME type (not just `audio/*`)
6. **Bible reference regex** — Must handle "First Corinthians" / "1 Corinthians" / "I Corinthians" variants
7. **Voice profile corrections** are case-insensitive regex with word boundaries

---

## Future Enhancements

- [ ] Send replay to students/partners (auto-distribute recording)
- [ ] Speaker diarization (identify multiple speakers)
- [ ] Real-time collaborative viewing (WebSocket broadcast)
- [ ] Clip extraction from bookmarked segments
- [ ] Multi-language transcription support
