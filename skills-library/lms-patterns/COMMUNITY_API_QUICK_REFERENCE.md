# Community API Quick Reference

## Starting the Server

```powershell
cd server
node .\server.js
```

Server runs at: `http://localhost:5000`  
API base: `http://localhost:5000/api/community`

---

## API Endpoints Overview

**22 Total Routes** across 6 categories

### Discussions (CREATE, READ, UPDATE, DELETE, PIN)
```
POST   /discussions                 - Create
GET    /discussions                 - List (paginated)
GET    /discussions/:id             - Get one
PUT    /discussions/:id             - Update (auth)
DELETE /discussions/:id             - Delete (auth)
PUT    /discussions/:id/pin         - Pin/unpin (auth)
```

### Replies (NESTED THREADING SUPPORT)
```
POST   /discussions/:id/replies     - Create (auth)
GET    /discussions/:id/replies     - List replies
GET    /replies/:id/nested          - Get nested replies
PUT    /replies/:id                 - Update (auth)
DELETE /replies/:id                 - Delete (auth)
POST   /replies/:id/flag            - Flag for moderation (auth)
```

### Reactions (EMOJI SUPPORT)
```
POST   /replies/:id/reactions       - Add reaction (auth)
DELETE /replies/:id/reactions/:emoji - Remove reaction (auth)
GET    /replies/:id/reactions       - Get all reactions
```

### Tags (DISCUSSION ORGANIZATION)
```
GET    /tags                        - List all tags
GET    /tags/:id/discussions        - Get by tag
```

### Notifications (ACTIVITY TRACKING)
```
GET    /notifications               - Get user notifications (auth)
PUT    /notifications/:id/read      - Mark as read (auth)
PUT    /notifications/read-all      - Mark all read (auth)
DELETE /notifications/:id           - Delete (auth)
```

### Moderation (ADMIN ONLY)
```
GET    /moderation/flagged          - Get flagged content (admin)
PUT    /moderation/:id/resolve      - Resolve flagged (admin)
```

---

## Database Tables (Supabase PostgreSQL)

7 pre-created tables in `public` schema:

| Table | Purpose |
|-------|---------|
| `community_discussions` | Main threads |
| `community_replies` | Comments/replies with nesting |
| `community_reactions` | Emoji reactions |
| `community_moderation` | Flagged content |
| `community_tags` | Tag definitions |
| `community_discussion_tags` | Discussion-tag junction |
| `community_notifications` | User notifications |

---

## Key Features

✅ **Nested Replies** - Support for threaded discussions  
✅ **Emoji Reactions** - Like/react with emojis  
✅ **Tagging System** - Organize discussions by tags  
✅ **Notifications** - Auto-notify on activity  
✅ **Moderation** - Flag and resolve inappropriate content  
✅ **View Tracking** - Count discussion views  
✅ **Auth Protected** - JWT middleware on sensitive endpoints  
✅ **Pagination** - Handle large datasets efficiently  

---

## Model Classes

### CommunityDiscussion
```javascript
create(data)              // Create new discussion
getById(id)               // Get with auto view increment
list(options)             // Paginated list
update(id, data)          // Update discussion
delete(id)                // Delete (cascades)
togglePin(id, isPinned)   // Pin/unpin
toggleClose(id, isClosed) // Open/close thread
```

### CommunityReply
```javascript
create(data)              // Create reply (updates parent count)
getByDiscussionId(id)     // List replies for discussion
getNestedReplies(id)      // Get child replies
update(id, data)          // Update reply
delete(id)                // Delete (cascades)
flag(id, reason, userId)  // Flag for moderation
```

### CommunityReaction
```javascript
addReaction(replyId, userId, emoji)       // Add/upsert
removeReaction(replyId, userId, emoji)    // Remove & decrement
getReactions(replyId)                     // Group by emoji
```

### CommunityTag
```javascript
getOrCreate(name, color)           // Get or create tag
getAll()                           // List all tags
addToDiscussion(discussionId, tagId)
removeFromDiscussion(discussionId, tagId)
getDiscussionsByTag(tagId, options)
```

### CommunityNotification
```javascript
create(data)              // Create notification
getUserNotifications(userId, options)
markAsRead(id)            // Mark single as read
markAllAsRead(userId)     // Mark all as read
delete(id)                // Delete notification
```

### CommunityModeration
```javascript
getFlaggedContent(options)        // Get pending/resolved
resolve(id, action)               // Resolve with action
```

---

## Example Requests

### Create Discussion
```bash
curl -X POST http://localhost:5000/api/community/discussions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "How to deploy to production?",
    "content": "I need help deploying my app...",
    "category": "deployment",
    "tags": ["deployment", "help"]
  }'
```

### Get Discussions
```bash
curl http://localhost:5000/api/community/discussions?page=1&limit=20
```

### Create Reply
```bash
curl -X POST http://localhost:5000/api/community/discussions/{discussionId}/replies \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "content": "I recommend using Vercel...",
    "parent_reply_id": null
  }'
```

### Add Reaction
```bash
curl -X POST http://localhost:5000/api/community/replies/{replyId}/reactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"emoji_type": "👍"}'
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (GET, PUT with data) |
| 201 | Created (POST successful) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (no/invalid token) |
| 403 | Forbidden (owner/admin check failed) |
| 404 | Not Found (resource doesn't exist) |
| 500 | Server Error |

---

## Files Location

```
server/
├── models/
│   └── CommunityModels.js          (6 model objects)
├── controllers/
│   └── communityController.js       (20+ endpoint handlers)
├── routes/
│   └── communityRoutes.js           (22 API routes)
├── middleware/
│   ├── auth.js                      (JWT protection)
│   └── asyncHandler.js              (Error wrapper)
└── server.js                        (Express app with routes)
```

---

## Next: React Integration

Create hook: `client/src/hooks/useCommunityAPI.js`

```javascript
export const useCommunityAPI = () => {
  const getDiscussions = async (options) => {
    const response = await fetch(`/api/community/discussions?${new URLSearchParams(options)}`)
    return response.json()
  }
  
  const createDiscussion = async (data) => {
    const response = await fetch(`/api/community/discussions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })
    return response.json()
  }
  
  // ... more methods
  
  return { getDiscussions, createDiscussion, ... }
}
```

Then use in components:
```javascript
const { getDiscussions } = useCommunityAPI()
const [discussions, setDiscussions] = useState([])

useEffect(() => {
  getDiscussions().then(data => setDiscussions(data.discussions))
}, [])
```

---

## Troubleshooting

### Server won't start
```powershell
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process on port 5000
taskkill /F /PID {PID}
```

### Database connection failed
- Check `DATABASE_URL` in `.env`
- Verify Supabase tables exist
- Check JWT_SECRET is set

### Auth errors
- Include `Authorization: Bearer {token}` header
- Token must be valid JWT
- User must exist in `profiles` table

---

✅ **Backend complete and ready for React integration!**
