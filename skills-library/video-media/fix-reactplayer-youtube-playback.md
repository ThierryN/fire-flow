# Fix ReactPlayer YouTube Playback Issues

**Date**: October 25, 2025
**Project**: MERN Community LMS
**Issue**: YouTube videos not playing, showing 0:00/0:00 duration with black screen
**Solution**: Remove `light` prop for YouTube videos and properly handle ReactPlayer ref methods

## Problem Analysis

### The Original Issues
1. **YouTube videos showing black screen with 0:00/0:00 duration**
2. **`videoRef.current.seekTo is not a function` error when clicking bookmarks**
3. **Infinite re-rendering causing performance issues**

### Root Causes
1. **`light` prop blocking YouTube iframe**: When `light={poster}` is set, ReactPlayer shows preview image instead of loading YouTube iframe
2. **ReactPlayer ref methods not immediately available**: The ref doesn't expose methods until player is ready
3. **Console.log in render causing re-renders**: Debug logging in component body triggered infinite renders

## Complete Solution Implementation

### 1. Fixed Light Prop for YouTube Videos
**File**: `client/src/components/video/VideoPlayer.jsx`

```javascript
const VideoPlayer = forwardRef(({
  src,
  poster,
  captions,
  onProgress,
  onEnded,
  onReady,
  playing = false,
  playbackRate = 1
}, ref) => {
  // Check if this is a YouTube or external video
  const isYouTubeOrVimeo = src && (
    src.includes('youtube.com') ||
    src.includes('youtu.be') ||
    src.includes('vimeo.com')
  );

  return (
    <div className="w-full aspect-video bg-black rounded-lg overflow-hidden">
      <ReactPlayer
        ref={ref}
        url={src}
        controls
        width="100%"
        height="100%"
        playing={playing}
        playbackRate={playbackRate}
        light={isYouTubeOrVimeo ? false : poster} // Don't use light for YouTube/Vimeo
        onProgress={onProgress}
        onEnded={onEnded}
        onReady={onReady}
        progressInterval={1000}
        config={{
          youtube: {
            playerVars: {
              showinfo: 1,
              modestbranding: 1,
              rel: 0
            }
          }
        }}
      />
    </div>
  );
});
```

### 2. Added Player Ready State Tracking
**File**: `client/src/pages/CourseContent.jsx`

```javascript
// Added state to track when player is ready
const [playerReady, setPlayerReady] = useState(false);

// In the VideoPlayer component
<VideoPlayer
  onReady={() => {
    setPlayerReady(true);
    // Get duration when video is ready
    if (videoRef.current) {
      const duration = videoRef.current.getDuration();
      if (duration) {
        setVideoDuration(duration);
      }
    }
  }}
/>
```

### 3. Fixed seekTo Function Calls
**File**: `client/src/pages/CourseContent.jsx`

```javascript
// For bookmark seeking
onSeekToTimestamp={(timestamp) => {
  setCurrentVideoTime(timestamp);
  // Only seek if player is ready
  if (playerReady && videoRef.current && typeof videoRef.current.seekTo === 'function') {
    videoRef.current.seekTo(timestamp, 'seconds');
  } else {
    // Fallback: try again after a short delay
    setTimeout(() => {
      if (videoRef.current && typeof videoRef.current.seekTo === 'function') {
        videoRef.current.seekTo(timestamp, 'seconds');
      }
    }, 500);
  }
}}

// For keyboard shortcuts
case 'ArrowLeft': // Rewind 5 seconds
  e.preventDefault();
  if (videoRef.current && typeof videoRef.current.seekTo === 'function') {
    const newTime = Math.max(0, currentVideoTime - 5);
    videoRef.current.seekTo(newTime, 'seconds');
  }
  break;
```

### 4. Fixed Database Video Provider
**Migration**: `022_fix_fire_school_video_provider.sql`

```sql
-- Sets video_provider to 'youtube' for all YouTube video lessons
UPDATE lessons
SET video_provider = 'youtube'
WHERE course_id = (
  SELECT id FROM courses WHERE slug = 'fire-school-of-the-holy-spirit'
)
AND (video_url LIKE '%youtube.com%' OR video_url LIKE '%youtu.be%');
```

### 5. Reset Player State on Lesson Change
**File**: `client/src/pages/CourseContent.jsx`

```javascript
useEffect(() => {
  // Reset player ready state when lesson changes
  setPlayerReady(false);

  if (activeLesson && (activeLesson.content_type === 'video' || activeLesson.contentType === 'video')) {
    loadVideoProgress();
  } else {
    setVideoProgress(null);
  }

  // Cleanup code...
}, [activeLesson]);
```

## Technical Deep Dive

### Why the Light Prop Breaks YouTube

ReactPlayer's `light` prop is designed for performance - it shows a thumbnail instead of loading the player immediately. However:

1. **YouTube requires iframe for playback**: The YouTube player must be an iframe embed
2. **Light mode uses HTML5 video fallback**: When light is true with YouTube URL, ReactPlayer falls back to HTML5 video element
3. **HTML5 video can't play YouTube URLs**: Regular video elements can't stream from YouTube

### ReactPlayer Ref Architecture

```javascript
// ReactPlayer ref structure
videoRef.current = {
  // Player control methods
  seekTo: (amount, type) => {},
  getCurrentTime: () => number,
  getDuration: () => number,
  getInternalPlayer: () => HTMLVideoElement | YouTubePlayer,

  // Player state
  wrapper: HTMLDivElement,
  // ... other properties
}
```

### Provider Detection Logic

```javascript
// Complete provider detection for video URLs
const getVideoSource = (lesson) => {
  const videoUrl = lesson.videoUrl || lesson.video_url || '';
  const videoProvider = lesson.video_provider || lesson.videoProvider || '';

  // YouTube/Vimeo URLs should use direct URL
  if (videoUrl.includes('youtube.com') ||
      videoUrl.includes('youtu.be') ||
      videoUrl.includes('vimeo.com')) {
    return videoUrl;
  }

  // Provider explicitly set
  if (videoProvider === 'youtube' || videoProvider === 'vimeo') {
    return videoUrl;
  }

  // Custom uploaded videos use streaming endpoint
  return `/api/videos/stream/${lesson.id || lesson._id}`;
};
```

## Files Modified Summary

1. **client/src/components/video/VideoPlayer.jsx**
   - Added conditional logic for `light` prop based on video type
   - Removed debug useEffect that was causing issues

2. **client/src/pages/CourseContent.jsx**
   - Added `playerReady` state
   - Fixed seekTo calls with proper type checking
   - Added fallback timeout for seeking
   - Reset player state on lesson change

3. **server/migrations/022_fix_fire_school_video_provider.sql**
   - Fixed database to properly mark YouTube videos

## Testing Verification

### What to Check
- [x] YouTube videos load and play properly
- [x] Video shows correct duration (not 0:00/0:00)
- [x] Bookmarks can be created at current timestamp
- [x] Clicking bookmarks seeks to correct position
- [x] Keyboard shortcuts work (space, arrows, F)
- [x] Custom uploaded videos still show poster image
- [x] No console errors about seekTo function

### Console Debugging
```javascript
// Add to check player ready state
console.log('Player ready, ref methods:', videoRef.current);

// Add to debug seeking
console.log('Seeking to:', timestamp);
console.log('Player ready:', playerReady);
console.log('Has seekTo:', typeof videoRef.current?.seekTo === 'function');
```

## Common Issues and Solutions

### Issue: YouTube still showing black screen
**Solution**: Verify `light` prop is false for YouTube URLs
```javascript
// Check in React DevTools
ReactPlayer.props.light // Should be false for YouTube
```

### Issue: seekTo still not working
**Solution**: Ensure player is ready before seeking
```javascript
if (playerReady && videoRef.current) {
  videoRef.current.seekTo(timestamp, 'seconds');
}
```

### Issue: Multiple re-renders
**Solution**: Remove console.log from render method
```javascript
// Don't do this in component body
console.log('Active Lesson:', activeLesson); // CAUSES RE-RENDER!

// Do this in useEffect or event handlers instead
useEffect(() => {
  console.log('Active Lesson:', activeLesson);
}, [activeLesson]);
```

## Performance Optimizations

1. **Conditional Light Prop**: Only use preview images for custom videos
2. **Player Ready State**: Prevent unnecessary seekTo attempts
3. **Timeout Fallback**: Handle race conditions gracefully
4. **State Reset on Change**: Clean up when switching lessons

## Migration Commands

```bash
# Run the migration to fix video_provider
cd server
node -e "require('dotenv').config(); const fs = require('fs'); const sql = require('./config/sql.js').default; const migration = fs.readFileSync('./migrations/022_fix_fire_school_video_provider.sql', 'utf8'); const queries = migration.split('BEGIN;')[1].split('COMMIT;')[0].trim(); sql.begin(async (tx) => { await tx.unsafe(queries); }).then(() => { console.log('Migration completed'); process.exit(0); });"
```

## Key Learnings

1. **ReactPlayer's light prop is not compatible with YouTube embeds**
2. **Always check if ref methods exist before calling them**
3. **Track player ready state for reliable control**
4. **Database video_provider field must match actual video source**
5. **Avoid side effects in render - use useEffect**

## References

- [ReactPlayer GitHub Issues - Light prop with YouTube](https://github.com/cookpete/react-player/issues)
- [ReactPlayer Documentation - Config Options](https://github.com/cookpete/react-player#config-prop)
- [YouTube IFrame Player API](https://developers.google.com/youtube/iframe_api_reference)
- [React Ref Forwarding Best Practices](https://react.dev/reference/react/forwardRef)

---

**Implementation completed by**: Claude
**Testing status**: ✅ Complete
**Production ready**: Yes
**Critical fix**: YouTube playback now works with bookmarks