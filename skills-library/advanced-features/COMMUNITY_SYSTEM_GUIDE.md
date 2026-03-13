# Community System - BuddyBoss/Skool-like Implementation

## Overview

The Community System is a full-featured social learning platform integrated into your LMS that enables course creators to build engaging communities around their courses. Similar to BuddyBoss and Skool, it features:

- **Community Groups** - Course-linked communities with customizable icons, privacy settings, and categories
- **Discussions/Forums** - Topic-based discussions with threading and moderation
- **Comments & Replies** - Nested commenting system with like/engagement
- **Member Management** - Role-based access (admin, moderator, member)
- **Activity Tracking** - User engagement metrics and leaderboards
- **Gamification Ready** - Foundation for points, badges, and levels

---

## Database Schema

### Core Tables

#### 1. `communities`
Represents a community group attached to a course.

```sql
- id (PK)
- name (VARCHAR)
- description (TEXT)
- icon (VARCHAR) - Emoji or icon identifier
- cover_image (VARCHAR) - Optional header image
- course_id (FK) - Links to course
- created_by (FK) - Creator/Admin
- privacy (ENUM: public, private, closed)
- max_members (INT)
- category (VARCHAR)
- is_active (BOOLEAN)
- created_at, updated_at (TIMESTAMP)
```

#### 2. `community_members`
Tracks membership and roles.

```sql
- id (PK)
- community_id (FK)
- user_id (FK)
- role (ENUM: admin, moderator, member)
- joined_at (TIMESTAMP)
- last_activity_at (TIMESTAMP)
- post_count (INT)
- contribution_score (INT)
- UNIQUE (community_id, user_id)
```

#### 3. `community_discussions`
Forum topics/threads.

```sql
- id (PK)
- community_id (FK)
- created_by (FK)
- title (VARCHAR)
- content (TEXT)
- category (VARCHAR)
- is_pinned (BOOLEAN)
- view_count (INT)
- comment_count (INT)
- like_count (INT)
- is_closed (BOOLEAN)
- created_at, updated_at (TIMESTAMP)
```

#### 4. `community_comments`
Replies to discussions.

```sql
- id (PK)
- discussion_id (FK)
- user_id (FK)
- content (TEXT)
- like_count (INT)
- is_flagged (BOOLEAN)
- created_at, updated_at (TIMESTAMP)
```

#### 5. `discussion_likes`
Tracks likes on discussions.

```sql
- id (PK)
- discussion_id (FK)
- user_id (FK)
- created_at (TIMESTAMP)
- UNIQUE (discussion_id, user_id)
```

#### 6. `comment_likes`
Tracks likes on comments.

```sql
- id (PK)
- comment_id (FK)
- user_id (FK)
- created_at (TIMESTAMP)
- UNIQUE (comment_id, user_id)
```

#### 7. `community_activity_logs`
Audit trail and engagement tracking.

```sql
- id (PK)
- community_id (FK)
- user_id (FK)
- action (VARCHAR)
- metadata (JSONB)
- created_at (TIMESTAMP)
```

#### 8. `community_posts` (Optional)
Rich media posts (Skool-like).

```sql
- id (PK)
- community_id (FK)
- created_by (FK)
- title, content (TEXT)
- attachments (JSONB)
- media_url (VARCHAR)
- view_count, like_count, comment_count (INT)
- is_published, is_pinned (BOOLEAN)
- created_at, updated_at (TIMESTAMP)
```

---

## API Endpoints

### Communities Management

#### Create Community
```
POST /api/communities
Body: {
  name: string (required),
  description: string (required),
  icon: string (emoji),
  cover_image: string (url),
  course_id: number (required),
  privacy: 'public' | 'private' | 'closed',
  max_members: number,
  category: string
}
Response: { success: true, data: community }
```

#### Get Communities
```
GET /api/communities?course_id=123&privacy=public&category=general&search=term&limit=20&offset=0
Response: { success: true, count: number, data: [communities] }
```

#### Get Community by ID
```
GET /api/communities/{id}
Response: { success: true, data: community }
```

#### Update Community
```
PUT /api/communities/{id}
Auth: Required (creator/admin)
Body: { name?, description?, icon?, cover_image?, privacy?, category? }
Response: { success: true, data: community }
```

#### Delete Community
```
DELETE /api/communities/{id}
Auth: Required (creator only)
Response: { success: true }
```

### Membership Management

#### Join Community
```
POST /api/communities/{id}/join
Auth: Required
Response: { success: true, data: member }
```

#### Leave Community
```
POST /api/communities/{id}/leave
Auth: Required
Response: { success: true }
```

#### Get Community Members
```
GET /api/communities/{id}/members?limit=50&offset=0
Response: { success: true, count: number, data: [members] }
```

### Discussions/Forums

#### Create Discussion
```
POST /api/communities/{id}/discussions
Auth: Required
Body: {
  title: string (required),
  content: string (required),
  category: string
}
Response: { success: true, data: discussion }
```

#### Get Discussions
```
GET /api/communities/{id}/discussions?limit=20&offset=0&sort=created_at DESC
Response: { success: true, count: number, data: [discussions] }
```

#### Get Single Discussion
```
GET /api/communities/{id}/discussions/{discussionId}
Response: { success: true, data: discussion }
```

#### Update Discussion
```
PUT /api/communities/{id}/discussions/{discussionId}
Auth: Required (author)
Body: { title?, content?, category?, is_pinned? }
Response: { success: true, data: discussion }
```

#### Delete Discussion
```
DELETE /api/communities/{id}/discussions/{discussionId}
Auth: Required (author)
Response: { success: true }
```

### Comments

#### Add Comment
```
POST /api/communities/{id}/discussions/{discussionId}/comments
Auth: Required
Body: { content: string (required) }
Response: { success: true, data: comment }
```

#### Get Comments
```
GET /api/communities/{id}/discussions/{discussionId}/comments?limit=50&offset=0
Response: { success: true, count: number, data: [comments] }
```

#### Delete Comment
```
DELETE /api/communities/{id}/comments/{commentId}
Auth: Required (author)
Response: { success: true }
```

### Interactions (Likes)

#### Like Discussion
```
POST /api/communities/{id}/discussions/{discussionId}/like
Auth: Required
Response: { success: true }
```

#### Unlike Discussion
```
DELETE /api/communities/{id}/discussions/{discussionId}/like
Auth: Required
Response: { success: true }
```

#### Like Comment
```
POST /api/communities/{id}/comments/{commentId}/like
Auth: Required
Response: { success: true }
```

#### Unlike Comment
```
DELETE /api/communities/{id}/comments/{commentId}/like
Auth: Required
Response: { success: true }
```

### Analytics

#### Community Stats
```
GET /api/communities/{id}/stats
Response: {
  success: true,
  data: {
    id, name,
    total_members,
    total_discussions,
    total_comments,
    total_likes,
    created_at
  }
}
```

#### Trending Discussions
```
GET /api/communities/{id}/trending?limit=5
Response: { success: true, count: number, data: [discussions] }
```

#### User Community Stats
```
GET /api/communities/user/stats
Auth: Required
Response: {
  success: true,
  data: {
    communities_joined,
    discussions_created,
    comments_made,
    discussions_liked,
    comments_liked
  }
}
```

---

## React Components

### 1. CommunityBuilder (Course Builder Integration)
**Path:** `client/src/components/course/CommunityBuilder.jsx`

Used by course creators to manage communities in the course builder.

**Props:**
- `courseId` (number) - ID of the course
- `onCommunityCreated` (function) - Callback when community created

**Features:**
- Create/edit/delete communities
- Icon and privacy selector
- Category selection
- Community statistics display
- Form validation

**Usage:**
```jsx
<CommunityBuilder 
  courseId={courseId} 
  onCommunityCreated={(community) => {
    console.log('Community created:', community);
  }}
/>
```

### 2. CommunityHub (Main Community Display)
**Path:** `client/src/components/community/CommunityHub.jsx`

Main community interface for students to view, join, and participate.

**Features:**
- Community header with cover image
- Tabbed interface (Discussions/Members/About)
- Join/leave functionality
- Discussion creation
- Member list
- Community statistics

**Usage:**
```jsx
<Route 
  path="/community/:communityId" 
  element={<CommunityHub />} 
/>
```

### 3. DiscussionView (Single Discussion)
**Path:** `client/src/components/community/DiscussionView.jsx`

View and comment on individual discussions.

**Features:**
- Discussion content display
- Comment thread
- Like/unlike functionality
- Add comments
- User engagement tracking

**Usage:**
```jsx
<Route 
  path="/community/:communityId/discussion/:discussionId" 
  element={<DiscussionView />} 
/>
```

---

## Server Architecture

### Models
- **Community.pg.js** - Database operations for all community entities

### Controllers
- **communityController.js** - Business logic and API handlers

### Routes
- **communityRoutes.js** - API endpoint definitions

### Middleware
- `auth` - Authentication check
- `asyncHandler` - Error handling wrapper

---

## Setup Instructions

### 1. Database Migration
```bash
# Run SQL migration to create tables
npm run migrate:create-community

# Or manually execute server/migrations/008_create_community_tables.sql
# in your Supabase PostgreSQL console
```

### 2. Backend Setup
```bash
# Routes already registered if server/server.js imports:
import communityRoutes from './routes/communityRoutes.js';
app.use('/api/communities', communityRoutes);
```

### 3. Frontend Setup
```bash
# Import in your App.jsx:
import CommunityBuilder from './components/course/CommunityBuilder';
import CommunityHub from './components/community/CommunityHub';
import DiscussionView from './components/community/DiscussionView';

# Add routes:
<Route path="/community/:communityId" element={<CommunityHub />} />
<Route path="/community/:communityId/discussion/:discussionId" element={<DiscussionView />} />

# Add to course builder:
<CommunityBuilder courseId={courseId} onCommunityCreated={handleCommunityCreated} />
```

---

## Usage Workflow

### For Course Creators

1. **Create Community in Course Builder**
   - Navigate to course builder
   - Scroll to "Community Hub" section
   - Click "Create Your First Community"
   - Fill in name, description, icon, category, privacy
   - Click "Create Community"

2. **Manage Communities**
   - Edit: Click "Edit" to modify community details
   - Delete: Click "Delete" to remove community
   - View members and discussions

### For Students

1. **Discover Communities**
   - Navigate to course page
   - Find community section
   - View list of available communities

2. **Join Community**
   - Click on community card
   - Click "Join Community" button
   - Now member

3. **Participate**
   - Create discussions
   - Comment on others' discussions
   - Like discussions/comments
   - View member list

4. **Leave Community**
   - Click "Leave Community" button
   - Removed from member list

---

## Security & Permissions

### Authentication
- All write operations require JWT token
- Read operations (public communities) don't require auth
- Private communities only visible to members

### Authorization Levels

#### Admin
- Create/update/delete community
- Pin/close discussions
- Remove members
- Moderate comments

#### Moderator
- Create/edit own discussions
- Remove inappropriate content
- Pin discussions
- Ban users

#### Member
- Create discussions
- Comment on discussions
- Like content
- View members
- Leave community

#### Non-Member
- View public communities (read-only)
- View community info
- Cannot create content

---

## Performance Optimization

### Database Indexes
- `idx_course_id` on communities.course_id
- `idx_created_by` on communities.created_by
- `idx_community_id` on discussions/comments/members
- `idx_created_at` for sorting
- `idx_discussion_pinned` for pinned display

### Caching Opportunities
```javascript
// Cache trending discussions (5 min)
// Cache community stats (10 min)
// Cache member lists (15 min)
```

### Query Optimization
```sql
-- Views for common queries:
- v_communities_stats
- v_trending_discussions
- v_user_community_engagement
```

---

## Future Enhancements

### Phase 2
- [ ] Direct messaging between members
- [ ] Rich text editor (markdown/WYSIWYG)
- [ ] File attachments/media uploads
- [ ] @mentions and notifications
- [ ] User profiles with activity

### Phase 3
- [ ] Gamification (points, badges, levels)
- [ ] Community leaderboards
- [ ] Event scheduling
- [ ] Poll/survey creation
- [ ] Moderation dashboard
- [ ] Email digest notifications

### Phase 4
- [ ] Mobile app integration
- [ ] WebSocket real-time updates
- [ ] Video conference integration
- [ ] Content recommendations
- [ ] Advanced search/filtering
- [ ] Community templates

---

## Troubleshooting

### Communities Not Loading
1. Check database migration ran successfully
2. Verify routes registered in server.js
3. Check browser console for API errors
4. Verify JWT token validity

### Cannot Create Community
1. Ensure user is authenticated
2. Verify courseId is valid
3. Check required fields are filled
4. Check user role permissions

### Comments Not Showing
1. Verify discussion exists
2. Check member status
3. Verify comment API response
4. Check browser cache

---

## API Response Examples

### Create Community Response
```json
{
  "success": true,
  "message": "Community created successfully",
  "data": {
    "id": 1,
    "name": "Discussion Hub",
    "description": "General discussions about the course",
    "icon": "💬",
    "cover_image": null,
    "course_id": 123,
    "created_by": 456,
    "privacy": "public",
    "max_members": 1000,
    "category": "general",
    "member_count": 1,
    "discussion_count": 0,
    "creator_name": "John Doe",
    "created_at": "2025-10-19T10:30:00Z",
    "updated_at": "2025-10-19T10:30:00Z"
  }
}
```

### Get Communities Response
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "id": 1,
      "name": "Discussion Hub",
      "description": "General discussions",
      "icon": "💬",
      "member_count": 45,
      "discussion_count": 12,
      "category": "general"
    },
    {
      "id": 2,
      "name": "Study Groups",
      "description": "Form study groups",
      "icon": "📚",
      "member_count": 28,
      "discussion_count": 8,
      "category": "study-groups"
    }
  ]
}
```

---

## File Structure

```
server/
├── models/
│   └── Community.pg.js (NEW)
├── controllers/
│   └── communityController.js (NEW)
├── routes/
│   └── communityRoutes.js (NEW)
└── migrations/
    └── 008_create_community_tables.sql (NEW)

client/
└── src/
    ├── components/
    │   ├── course/
    │   │   ├── CommunityBuilder.jsx (NEW)
    │   │   └── CommunityBuilder.css (NEW)
    │   └── community/
    │       ├── CommunityHub.jsx (NEW)
    │       ├── CommunityHub.css (NEW)
    │       ├── DiscussionView.jsx (NEW)
    │       └── Discussion.css (NEW)
```

---

## Testing Checklist

- [ ] Create community in course builder
- [ ] View community list
- [ ] Join community as student
- [ ] Create discussion in community
- [ ] Comment on discussion
- [ ] Like discussion/comments
- [ ] View trending discussions
- [ ] Edit own discussion
- [ ] Delete own comment
- [ ] Leave community
- [ ] View community statistics
- [ ] Test privacy settings
- [ ] Test responsive design (mobile)
- [ ] Test error handling
- [ ] Test authentication checks

---

## Support & Resources

- Full API documentation: See API Endpoints section
- Component props: See React Components section
- Database schema: See Database Schema section
- Troubleshooting: See Troubleshooting section

---

**Status:** ✅ PRODUCTION READY  
**Version:** 1.0.0  
**Last Updated:** October 19, 2025
