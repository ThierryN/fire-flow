# Media Playback Resume Pattern - Industry-Standard Implementation

## The Problem

Audio/video playback position not being saved and restored correctly. Users expect:
- Stop Audio 1 at 23:45 → should remember 23:45
- Stop Audio 2 at 43:23 → should remember 43:23
- Dashboard "Resume" → goes to most recent lesson at its saved position
- Click directly on any lesson → resumes at THAT lesson's saved position

### Why It Was Hard

The issue appeared intermittent and was difficult to reproduce consistently. Multiple factors contributed:

1. **Race condition** - API response arriving AFTER `onLoadedMetadata` fired
2. **State vs DOM timing** - React state updates are async, but DOM events need sync access
3. **Multiple save points** - Progress saved during playback but lost on sudden exits
4. **Cross-component state** - Position needed to flow from Dashboard to Course page

### Impact

- Users lost their place in long audio lessons (30+ min podcasts)
- Frustrating UX when returning to continue learning
- No way to pick up where they left off after tab close or crash

---

## The Solution

### Root Cause Analysis

```
User clicks lesson
    ↓
setVideoProgress(null)     ← Clears old progress
    ↓
    ├──→ loadVideoProgress() ← Async API call (100-500ms)
    │
    └──→ <audio> mounts and loads
              ↓
         onLoadedMetadata fires
         videoProgress = null  ← API hasn't returned yet!
         → NO SEEK HAPPENS
              ↓
         API returns, setVideoProgress(data)
              ↓
         useEffect fires but audio already playing at 0:00
```

**The Fix:** Use a `ref` instead of relying on state timing:
- Refs update synchronously and are always current
- `onLoadedMetadata` reads from ref, not state
- No race condition possible

### Industry Standards (Netflix, Spotify, YouTube)

1. **Save Events**: timeupdate (debounced), pause, visibilitychange, beforeunload
2. **Save Method**: Regular API for playing, `navigator.sendBeacon()` for unload
3. **Restore Event**: `loadedmetadata` (when duration becomes available)
4. **Position Storage**: Database (cross-device sync)
5. **Edge Cases**: Don't resume if within 10 seconds of end

---

## Implementation

### Step 1: Add Progress Ref (Fix Race Condition)

```javascript
// Add ref alongside state
const [videoProgress, setVideoProgress] = useState(null);
const savedProgressRef = useRef(null); // Sync access - no race condition
```

### Step 2: Store in Ref When Loading

```javascript
const loadVideoProgress = async () => {
  const lessonId = activeLesson?.id || activeLesson?._id;
  if (!lessonId) return;

  try {
    const res = await api.get(`/video-progress/${lessonId}`);
    const progressData = res.data.data || null;
    setVideoProgress(progressData);
    savedProgressRef.current = progressData;  // ← CRITICAL: Store in ref
  } catch (error) {
    console.error('Error loading video progress:', error);
    setVideoProgress(null);
    savedProgressRef.current = null;
  }
};
```

### Step 3: Read from Ref in onLoadedMetadata

```javascript
onLoadedMetadata={(e) => {
  const duration = e.target.duration;
  setVideoDuration(duration);

  // READ FROM REF - avoids race condition with state
  const progress = savedProgressRef.current;
  if (progress?.playback_position_ms > 0 && !isNaN(duration)) {
    const resumeTime = progress.playback_position_ms / 1000;
    // Don't resume if within 10 seconds of end
    if (resumeTime < duration - 10) {
      console.log(`[Audio Resume] Seeking to ${resumeTime.toFixed(1)}s of ${duration.toFixed(1)}s`);
      e.target.currentTime = resumeTime;
    }
  }
}}
```

### Step 4: Clear Ref on Lesson Change

```javascript
useEffect(() => {
  setPlayerReady(false);
  setVideoProgress(null);
  savedProgressRef.current = null;  // ← Clear ref too

  if (activeLesson) {
    // ... rest of effect
  }
}, [activeLesson]);
```

### Step 5: Remove Competing useEffect

**REMOVE** any useEffect that watches videoProgress state and tries to seek:

```javascript
// REMOVE THIS - causes double-seeking and race conditions
// useEffect(() => {
//   if (videoProgress?.playback_position_ms > 0 && audioElementRef.current) {
//     audioElementRef.current.currentTime = videoProgress.playback_position_ms / 1000;
//   }
// }, [videoProgress]);
```

### Step 6: Add Save on Page Visibility/Close

```javascript
useEffect(() => {
  const saveProgressOnExit = () => {
    const mediaElement = audioElementRef.current;
    const lessonId = activeLesson?.id || activeLesson?._id;

    if (mediaElement && lessonId &&
        !isNaN(mediaElement.currentTime) &&
        !isNaN(mediaElement.duration) &&
        mediaElement.currentTime > 0) {

      const payload = JSON.stringify({
        currentTime: mediaElement.currentTime,
        duration: mediaElement.duration,
        watchTime: 1
      });

      // sendBeacon is reliable during page unload
      navigator.sendBeacon(
        `/api/video-progress/${lessonId}`,
        new Blob([payload], { type: 'application/json' })
      );
    }
  };

  const handleVisibilityChange = () => {
    if (document.visibilityState === 'hidden') {
      saveProgressOnExit();
    }
  };

  document.addEventListener('visibilitychange', handleVisibilityChange);
  window.addEventListener('beforeunload', saveProgressOnExit);

  return () => {
    document.removeEventListener('visibilitychange', handleVisibilityChange);
    window.removeEventListener('beforeunload', saveProgressOnExit);
  };
}, [activeLesson]);
```

### Step 7: Third-Party Audio Player Support

For react-h5-audio-player or similar components:

```javascript
const PodcastPlayer = ({
  episode,
  podcast,
  onListen,
  initialPosition = 0,  // Resume position in seconds
}) => {
  const playerRef = useRef(null);
  const hasResumed = useRef(false);

  // Resume position when audio is ready
  useEffect(() => {
    if (initialPosition <= 0 || hasResumed.current) return;

    const audio = playerRef.current?.audio?.current;
    if (!audio) return;

    const attemptResume = () => {
      const duration = audio.duration;
      if (!isNaN(duration) && initialPosition < duration - 10) {
        console.log(`[PodcastPlayer] Resuming at ${initialPosition.toFixed(1)}s`);
        audio.currentTime = initialPosition;
        hasResumed.current = true;
      }
    };

    if (audio.readyState >= 2) { // HAVE_CURRENT_DATA or higher
      attemptResume();
    } else {
      const handleLoadedMetadata = () => {
        attemptResume();
        audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      };
      audio.addEventListener('loadedmetadata', handleLoadedMetadata);
      return () => audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
    }
  }, [initialPosition]);

  // Reset when episode changes
  useEffect(() => {
    hasResumed.current = false;
  }, [episode?.id, episode?.audioUrl]);

  return (
    <AudioPlayer
      ref={playerRef}
      src={episode.audioUrl}
      onListen={onListen}
      // ... other props
    />
  );
};
```

### Step 8: URL Parameter for Cross-Page Resume

```javascript
// In Dashboard - include position in link
<Link
  to={`/course-content/${course.id}?lesson=${lesson.id}&position=${Math.floor(positionMs / 1000)}`}
>
  Resume
</Link>

// In Course page - read position from URL
const [searchParams] = useSearchParams();
const positionFromUrl = searchParams.get('position');

useEffect(() => {
  if (positionFromUrl && !isNaN(Number(positionFromUrl)) && Number(positionFromUrl) > 0) {
    savedProgressRef.current = {
      playback_position_ms: Number(positionFromUrl) * 1000
    };
  }
}, [positionFromUrl]);
```

---

## Testing the Fix

| Test Case | Steps | Expected Result |
|-----------|-------|-----------------:|
| Basic Resume | Play to 2:00, pause, refresh | Resumes at 2:00 |
| Lesson Switch | Play A to 1:00, go to B, back to A | A resumes at 1:00 |
| Tab Close | Play to 3:00, close tab, reopen | Resumes at 3:00 |
| Dashboard Resume | Play to 2:30, go to Dashboard, click Resume | Goes to lesson at 2:30 |
| Near-End | Play to 5 sec before end | Does NOT resume (starts fresh) |
| Tab Switch | Play to 1:00, switch tabs, return | Position preserved |
| Browser Crash Recovery | Play to 4:00, kill browser | Resumes near 4:00 (last sendBeacon) |

### Console Logs to Watch For

```
[Progress] Pre-set from URL: 150s
[Audio Resume] Seeking to 150.0s of 1842.3s
[PodcastPlayer] Resuming at 150.0s of 1842.3s
```

---

## Prevention

1. **Always use refs for values needed in DOM event handlers**
2. **Don't rely on React state timing for immediate DOM access**
3. **Use sendBeacon for reliable saves during unload**
4. **Test with slow network (throttle API responses)**
5. **Test with rapid lesson switching**

---

## Related Patterns

- [React Video Player Reinitialization Fix](./REACT_VIDEO_PLAYER_REINITIALIZATION_FIX.md) - Similar ref pattern for video
- [API Caching Strategies](../patterns-standards/CACHING_PATTERNS.md) - Progress caching

---

## Common Mistakes to Avoid

- ❌ **Reading state in onLoadedMetadata** - State may not be updated yet
- ❌ **Multiple useEffects trying to seek** - Creates race conditions
- ❌ **Relying only on pause event for save** - Misses tab close, crash
- ❌ **Not checking duration before resume** - Can seek past end
- ❌ **Resuming near end of media** - Confusing UX, use 10s threshold

---

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| loadedmetadata | ✅ | ✅ | ✅ | ✅ |
| sendBeacon | ✅ | ✅ | ✅ | ✅ |
| visibilitychange | ✅ | ✅ | ✅ | ✅ |
| beforeunload | ✅ | ✅ | ⚠️ Limited | ✅ |

Note: Safari has limited beforeunload support. visibilitychange is more reliable cross-browser.

---

## Resources

- [MDN: Navigator.sendBeacon()](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/sendBeacon)
- [MDN: HTMLMediaElement events](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement#events)
- [MDN: Page Visibility API](https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API)
- [Netflix Tech Blog: Video Playback](https://netflixtechblog.com/) - General patterns

---

## Time to Implement

**30-60 minutes** for full implementation across parent component and child player

## Difficulty Level

⭐⭐⭐ (3/5) - Moderate. Requires understanding of:
- React refs vs state timing
- HTML5 media events
- Page lifecycle events
- Browser unload behavior

---

**Author Notes:**

This issue was deceptively hard because it appeared intermittent. The race condition only manifested when the API was slower than the audio load, which varied by network conditions.

Key insight: **When DOM events need data immediately, use refs not state.**

The industry research (Netflix, Spotify, YouTube) confirmed this pattern is universal - they all:
1. Save on multiple events (not just pause)
2. Use sendBeacon for unload reliability
3. Restore on loadedmetadata (when duration is known)
4. Skip resume if near end (prevents confusing restarts)

Tested and deployed to production February 2026. Users confirmed resume working correctly.

---

**Project:** MERN Community LMS (schooloftheprophets.club)
**Phase:** 13 - Audio Playback Resume
**Date:** February 4, 2026
**Commit:** b601db8
