# Video Player Integration Guide

**Quick Reference for Video-Related Features in MERN LMS**

## Common Video Integration Patterns

### 1. Tracking Video Progress
```javascript
// State Management
const [currentTime, setCurrentTime] = useState(0);
const [duration, setDuration] = useState(0);
const [progress, setProgress] = useState(0);

// ReactPlayer Callback
onProgress={(state) => {
  setCurrentTime(state.playedSeconds);
  setDuration(state.loadedSeconds / state.loaded);
  setProgress(state.played * 100);
}}
```

### 2. Video Provider Detection
```javascript
const getVideoProvider = (url) => {
  if (!url) return 'custom';
  if (url.includes('youtube.com') || url.includes('youtu.be')) return 'youtube';
  if (url.includes('vimeo.com')) return 'vimeo';
  if (url.includes('/api/videos/')) return 'custom';
  return 'direct';
};
```

### 3. YouTube URL Conversion
```javascript
const getYouTubeEmbedUrl = (url) => {
  // Extract video ID from various formats
  let videoId = null;

  if (url.includes('youtube.com/watch?v=')) {
    videoId = url.split('v=')[1]?.split('&')[0];
  } else if (url.includes('youtu.be/')) {
    videoId = url.split('youtu.be/')[1]?.split('?')[0];
  }

  return videoId ? `https://www.youtube.com/embed/${videoId}` : url;
};
```

### 4. Video Seeking with ReactPlayer
```javascript
const playerRef = useRef(null);

const seekToTimestamp = (seconds) => {
  if (playerRef.current) {
    playerRef.current.seekTo(seconds, 'seconds');
  }
};
```

### 5. Playback Speed Control
```javascript
const [playbackRate, setPlaybackRate] = useState(1);

<ReactPlayer
  playbackRate={playbackRate}
  // ... other props
/>

// Speed controls
const speeds = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2];
```

## Common Issues and Solutions

### Issue: Video not playing
**Solution**: Check URL format and CORS settings
```javascript
// For custom videos, ensure proper API endpoint
src={`/api/videos/stream/${lessonId}`}

// For YouTube, ensure proper URL format
src={url.includes('youtube.com') ? url : getYouTubeEmbedUrl(url)}
```

### Issue: Progress not tracking
**Solution**: Set progressInterval
```javascript
<ReactPlayer
  progressInterval={1000} // Update every second
  onProgress={handleProgress}
/>
```

### Issue: Fullscreen not working
**Solution**: Add proper config
```javascript
config={{
  youtube: {
    playerVars: {
      fs: 1, // Enable fullscreen
      modestbranding: 1,
      rel: 0
    }
  }
}}
```

## ReactPlayer Configuration Reference

### Basic Props
- `url`: Video source URL
- `playing`: Boolean to control playback
- `controls`: Show native controls
- `volume`: 0-1 for volume level
- `muted`: Boolean for mute state
- `playbackRate`: Speed multiplier
- `width`/`height`: Player dimensions
- `progressInterval`: ms between onProgress calls

### Event Callbacks
- `onReady`: Player is ready
- `onStart`: Playback started
- `onPlay`: Play event
- `onPause`: Pause event
- `onProgress`: Progress update (most important for tracking)
- `onDuration`: Duration available
- `onSeek`: Seek occurred
- `onEnded`: Video finished
- `onError`: Error occurred

### Provider-Specific Config
```javascript
config={{
  youtube: {
    playerVars: {
      showinfo: 1,
      modestbranding: 1,
      rel: 0,
      start: 0, // Start time in seconds
      end: 300, // End time in seconds
    }
  },
  vimeo: {
    playerOptions: {
      autopause: true,
      byline: false,
      portrait: false,
      title: false,
    }
  },
  file: {
    attributes: {
      crossOrigin: 'anonymous',
      controlsList: 'nodownload',
    },
    tracks: [
      {
        kind: 'subtitles',
        src: '/path/to/captions.vtt',
        srcLang: 'en',
        default: true
      }
    ]
  }
}}
```

## Implementation Checklist

When implementing video features, ensure:

- [ ] ReactPlayer is installed: `npm install react-player`
- [ ] State management for time tracking
- [ ] Progress callback implemented
- [ ] Error handling for failed loads
- [ ] Fallback UI for unsupported videos
- [ ] Mobile responsiveness (aspect-ratio)
- [ ] Keyboard controls (if needed)
- [ ] Accessibility features
- [ ] Performance optimization (lazy loading)
- [ ] CORS configuration for API videos

## Code Snippets

### Complete Video Player Component
```javascript
import React, { useState, useRef, forwardRef } from 'react';
import ReactPlayer from 'react-player';

const VideoPlayer = forwardRef(({
  src,
  poster,
  onTimeUpdate,
  onVideoEnd,
  startTime = 0
}, ref) => {
  const [isReady, setIsReady] = useState(false);

  return (
    <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
      {!isReady && poster && (
        <img src={poster} className="absolute inset-0 w-full h-full object-cover" />
      )}
      <ReactPlayer
        ref={ref}
        url={src}
        controls
        width="100%"
        height="100%"
        playing={false}
        progressInterval={1000}
        onReady={() => setIsReady(true)}
        onProgress={(state) => {
          onTimeUpdate?.(state.playedSeconds);
        }}
        onEnded={onVideoEnd}
        config={{
          file: { attributes: { controlsList: 'nodownload' } },
          youtube: { playerVars: { start: startTime, modestbranding: 1 } }
        }}
      />
    </div>
  );
});
```

### Progress Tracking Hook
```javascript
const useVideoProgress = (lessonId) => {
  const [progress, setProgress] = useState({
    currentTime: 0,
    duration: 0,
    percentage: 0
  });

  const updateProgress = (state) => {
    setProgress({
      currentTime: state.playedSeconds,
      duration: state.loadedSeconds / (state.loaded || 1),
      percentage: state.played * 100
    });
  };

  return { progress, updateProgress };
};
```

---

**Last Updated**: October 25, 2025
**Use Case**: MERN Community LMS Video Features