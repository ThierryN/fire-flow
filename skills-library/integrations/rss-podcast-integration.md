# Skill: RSS Podcast Integration (Castos/Generic)

**Category:** Integrations
**Complexity:** Medium
**Technologies:** Node.js, Express, React, rss-parser, react-h5-audio-player

---

## Overview

Integrate RSS podcast feeds into a web application with support for:
- Public and private (authenticated) feeds
- Membership-based access control
- Episode search and pagination
- Audio playback with speed control
- In-memory or Redis caching

---

## When to Use This Skill

- Adding podcast functionality to an LMS or content platform
- Integrating Castos, Libsyn, Buzzsprout, or any RSS-based podcast service
- Implementing tiered access (free vs premium content)
- Building a podcast aggregator

---

## Implementation Pattern

### 1. Backend Service (Node.js/Express)

```javascript
// server/services/podcastService.js
import Parser from 'rss-parser';

const parser = new Parser({
  customFields: {
    item: [
      ['itunes:duration', 'duration'],
      ['itunes:image', 'image'],
      ['enclosure', 'enclosure']
    ]
  }
});

// Feed configuration
const PODCAST_FEEDS = {
  public: {
    'feed-id': {
      id: 'feed-id',
      name: 'Display Name',
      url: 'https://feeds.castos.com/xxxxx',
      accessLevel: 'member'
    }
  },
  private: {
    'private-feed': {
      id: 'private-feed',
      name: 'Premium Content',
      url: 'https://feeds.castos.com/xxxxx?uuid=AUTH_TOKEN',
      accessLevel: 'partner'
    }
  }
};

// Simple cache
const cache = new Map();
const CACHE_TTL = {
  public: 6 * 60 * 60 * 1000,  // 6 hours
  private: 2 * 60 * 60 * 1000   // 2 hours
};

class PodcastService {
  static async fetchFeed(feedId, user, options = {}) {
    const feed = this.getFeedConfig(feedId);
    if (!feed) throw new Error('Feed not found');

    // Check access
    if (feed.category === 'private' && !this.hasAccess(user)) {
      throw new Error('Access denied');
    }

    // Check cache
    const cached = cache.get(feedId);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL[feed.category]) {
      return cached.data;
    }

    // Fetch fresh
    const data = await parser.parseURL(feed.url);
    cache.set(feedId, { data, timestamp: Date.now() });
    return data;
  }

  static hasAccess(user) {
    if (!user) return false;
    if (user.role === 'admin') return true;
    const partnerTiers = ['partner', 'premium', 'lifetime'];
    return partnerTiers.includes(user.membershipTier?.toLowerCase());
  }
}
```

### 2. API Routes

```javascript
// server/routes/podcastRoutes.js
import express from 'express';
import { protect } from '../middleware/auth.js';
import PodcastService from '../services/podcastService.js';

const router = express.Router();

// List available feeds
router.get('/', protect, async (req, res) => {
  const feeds = PodcastService.getAvailableFeeds(req.user);
  res.json({ success: true, data: feeds });
});

// Get feed with episodes
router.get('/:feedId', protect, async (req, res) => {
  const { limit = 20, offset = 0 } = req.query;
  const podcast = await PodcastService.fetchFeed(
    req.params.feedId,
    req.user,
    { limit: +limit, offset: +offset }
  );
  res.json({ success: true, data: podcast });
});

// Search episodes
router.get('/search/episodes', protect, async (req, res) => {
  const results = await PodcastService.searchEpisodes(
    req.query.q,
    req.user
  );
  res.json({ success: true, data: results });
});

export default router;
```

### 3. Frontend Audio Player

```jsx
// client/src/components/PodcastPlayer.jsx
import AudioPlayer from 'react-h5-audio-player';
import 'react-h5-audio-player/lib/styles.css';

const PodcastPlayer = ({ episode, onPlay, onEnded }) => {
  const [playbackRate, setPlaybackRate] = useState(1);
  const playerRef = useRef(null);

  useEffect(() => {
    if (playerRef.current?.audio?.current) {
      playerRef.current.audio.current.playbackRate = playbackRate;
    }
  }, [playbackRate]);

  return (
    <div className="podcast-player">
      <div className="episode-info">
        <img src={episode.image} alt="" />
        <h3>{episode.title}</h3>
        <span>{formatDuration(episode.duration)}</span>
      </div>

      <AudioPlayer
        ref={playerRef}
        src={episode.audioUrl}
        showJumpControls={true}
        progressJumpSteps={{ backward: 15000, forward: 30000 }}
        customAdditionalControls={[
          <select
            value={playbackRate}
            onChange={(e) => setPlaybackRate(+e.target.value)}
          >
            {[0.5, 0.75, 1, 1.25, 1.5, 2].map(s => (
              <option key={s} value={s}>{s}x</option>
            ))}
          </select>
        ]}
        onPlay={() => onPlay?.(episode)}
        onEnded={() => onEnded?.(episode)}
      />
    </div>
  );
};
```

### 4. Frontend API Service

```javascript
// client/src/services/podcastService.js
import api from './api';

export const getAvailableFeeds = () => api.get('/podcasts');
export const getFeed = (id, { limit, offset }) =>
  api.get(`/podcasts/${id}`, { params: { limit, offset } });
export const searchEpisodes = (q) =>
  api.get('/podcasts/search/episodes', { params: { q } });
```

---

## NPM Dependencies

```bash
# Backend
npm install rss-parser

# Frontend
npm install react-h5-audio-player
```

---

## Key Patterns

### Private Feed Authentication (Castos)

Castos private feeds use UUID tokens in the URL:
```
https://feeds.castos.com/xxxxx?uuid=YOUR_PRIVATE_UUID
```

The UUID acts as authentication - store it in your backend config, never expose to client.

### Caching Strategy

| Feed Type | Cache TTL | Reason |
|-----------|-----------|--------|
| Public | 6 hours | Content rarely changes |
| Private | 2 hours | May have more frequent updates |

For production, consider Redis:
```javascript
import Redis from 'ioredis';
const redis = new Redis(process.env.REDIS_URL);

// Cache with TTL
await redis.setex(`podcast:${feedId}`, CACHE_TTL, JSON.stringify(data));
```

### Membership-Based Access

```javascript
// Check user's membership level from database
const membership = await sql`
  SELECT ml.slug, ml.access_rank
  FROM user_memberships um
  JOIN membership_levels ml ON um.membership_level_id = ml.id
  WHERE um.user_id = ${userId}
    AND um.status = 'active'
`;

// Compare access ranks
const userRank = membership?.access_rank || 0;
const requiredRank = feedConfig.accessLevel === 'partner' ? 2 : 1;
return userRank >= requiredRank;
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| CORS errors fetching RSS | Fetch from backend, not client |
| Duration parsing | Handle both "HH:MM:SS" and seconds formats |
| Missing episode images | Fallback to podcast image or default |
| Audio not playing | Check audio URL, may need proxy for HTTPS |

---

## Testing Checklist

- [ ] Public feeds load for all authenticated users
- [ ] Private feeds blocked for non-partners
- [ ] Admin can access all feeds
- [ ] Search returns results from accessible feeds only
- [ ] Audio plays correctly
- [ ] Playback speed control works
- [ ] Cache invalidates after TTL
- [ ] Pagination works correctly

---

## Related Skills

- `video-media/audio-player-integration.md`
- `api-patterns/membership-access-control.md`
- `deployment-security/caching-strategies.md`

---

**Last Updated:** January 5, 2026
**Author:** Claude Opus 4.5
**Project Reference:** my-other-project
