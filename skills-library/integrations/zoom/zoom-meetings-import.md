# Zoom Meetings Import - Complete Implementation Guide

## Overview
Complete solution for importing all scheduled Zoom meetings into your application using Server-to-Server OAuth authentication.

## Problem Statement
- Need to fetch and display all scheduled Zoom meetings from a Zoom account
- Must handle pagination for accounts with many meetings
- Need to avoid duplicate imports
- Must support both bulk import and selective import of specific meetings

## Implementation

### 1. Zoom Config - List Meetings Function

Add this to your `server/config/zoom.js`:

```javascript
/**
 * List all meetings from Zoom account
 * @param {object} options - Query options
 * @param {string} options.type - 'scheduled', 'live', 'upcoming' or 'all'
 * @param {number} options.page_size - Number of results per page (max 300)
 * @param {string} options.next_page_token - Token for pagination
 * @returns {Promise<object>} List of meetings with pagination info
 */
export const listMeetings = async (options = {}) => {
  const accessToken = await getAccessToken();
  const userEmail = process.env.ZOOM_USER_EMAIL || 'me';

  const params = {
    type: options.type || 'scheduled',
    page_size: options.page_size || 100,
  };

  if (options.next_page_token) {
    params.next_page_token = options.next_page_token;
  }

  try {
    const response = await axios.get(
      `${ZOOM_API_BASE}/users/${userEmail}/meetings`,
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
        params
      }
    );

    console.log(`✓ Fetched ${response.data.meetings?.length || 0} meetings from Zoom`);
    return response.data;
  } catch (error) {
    console.error('Zoom list meetings error:', error.response?.data || error.message);
    throw new Error('Failed to list Zoom meetings');
  }
};
```

### 2. Controller - Import Meetings Function

Update your `meetingsController.js`:

```javascript
export const importFromZoom = async (req, res) => {
  try {
    if (req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Only admins can import meetings'
      });
    }

    const { selectiveImport = false, meetingIds = [] } = req.body;

    console.log('📥 Importing meetings from Zoom...');

    // Get list of meetings from Zoom
    let zoomMeetings = [];
    try {
      // Import the Zoom config functions
      const zoomConfig = await import('../config/zoom.js');
      const { listMeetings, getMeeting } = zoomConfig.default || zoomConfig;

      if (selectiveImport && meetingIds.length > 0) {
        // Import specific meetings only
        console.log('📥 Importing specific meetings:', meetingIds);
        zoomMeetings = await Promise.all(
          meetingIds.map(mid => getMeeting(mid))
        );
      } else {
        // Fetch all meetings from Zoom account
        console.log('📥 Fetching all meetings from Zoom...');

        // Get all types of meetings
        const meetingTypes = ['scheduled', 'live', 'upcoming'];
        const allMeetings = [];

        for (const type of meetingTypes) {
          try {
            const response = await listMeetings({ type, page_size: 300 });
            if (response.meetings && response.meetings.length > 0) {
              allMeetings.push(...response.meetings);
              console.log(`✓ Found ${response.meetings.length} ${type} meetings`);
            }

            // Handle pagination if needed
            let nextPageToken = response.next_page_token;
            while (nextPageToken) {
              const nextPage = await listMeetings({
                type,
                page_size: 300,
                next_page_token: nextPageToken
              });
              if (nextPage.meetings && nextPage.meetings.length > 0) {
                allMeetings.push(...nextPage.meetings);
              }
              nextPageToken = nextPage.next_page_token;
            }
          } catch (err) {
            console.warn(`⚠️ Could not fetch ${type} meetings:`, err.message);
          }
        }

        // Remove duplicates based on meeting ID
        const uniqueMeetings = new Map();
        allMeetings.forEach(meeting => {
          if (!uniqueMeetings.has(meeting.id)) {
            uniqueMeetings.set(meeting.id, meeting);
          }
        });

        zoomMeetings = Array.from(uniqueMeetings.values());
        console.log(`✓ Total unique meetings found: ${zoomMeetings.length}`);

        if (zoomMeetings.length === 0) {
          return res.status(404).json({
            success: false,
            message: 'No meetings found in your Zoom account',
            instruction: 'Create some meetings in Zoom first, then try importing again'
          });
        }
      }
    } catch (zoomError) {
      console.warn('⚠️ Zoom API error:', zoomError.message);
      return res.status(400).json({
        success: false,
        message: 'Could not connect to Zoom API',
        error: zoomError.message
      });
    }

    // Import meetings into database
    let importedCount = 0;
    const importedMeetings = [];

    for (const zoomMeeting of zoomMeetings) {
      try {
        // Check if meeting already exists
        const existing = await sql`
          SELECT id FROM virtual_meetings
          WHERE meeting_id = ${zoomMeeting.id}
        `;

        if (existing.length === 0) {
          // Create new meeting record
          const result = await sql`
            INSERT INTO virtual_meetings (
              title, description, platform, scheduled_date, duration_minutes,
              timezone, meeting_url, meeting_id, meeting_password, host_id,
              max_participants, platform_data, created_at, updated_at
            ) VALUES (
              ${zoomMeeting.topic},
              ${zoomMeeting.agenda || null},
              'zoom',
              ${zoomMeeting.start_time},
              ${zoomMeeting.duration || 60},
              ${zoomMeeting.timezone || 'UTC'},
              ${zoomMeeting.join_url},
              ${zoomMeeting.id},
              ${zoomMeeting.password || null},
              ${req.user.id},
              ${zoomMeeting.settings?.max_participants || 100},
              ${{
                imported_from_zoom: true,
                original_zoom_id: zoomMeeting.id,
                recurring: zoomMeeting.type === 8
              }},
              CURRENT_TIMESTAMP,
              CURRENT_TIMESTAMP
            )
            RETURNING id, title, scheduled_date
          `;

          importedMeetings.push(result[0]);
          importedCount++;
        }
      } catch (insertError) {
        console.warn(`Failed to import meeting ${zoomMeeting.id}:`, insertError.message);
      }
    }

    res.json({
      success: true,
      message: `Successfully imported ${importedCount} meetings from Zoom`,
      importedCount,
      data: importedMeetings
    });
  } catch (error) {
    console.error('❌ [Import from Zoom Error]:', error);
    res.status(500).json({
      success: false,
      message: 'Error importing meetings from Zoom',
      error: error.message
    });
  }
};
```

### 3. Frontend - Import UI

In your React component:

```javascript
const handleImportFromZoom = async () => {
  try {
    setImportLoading(true);
    const token = localStorage.getItem('token');

    const response = await fetch('/api/meetings/admin/import-from-zoom', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        selectiveImport: false // Import all meetings
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Failed to import meetings');
    }

    toast.success(data.message || `Imported ${data.importedCount} meetings from Zoom`);
    setShowImportModal(false);

    // Refresh the meetings list
    fetchMeetings();
  } catch (err) {
    toast.error(err.message || 'Failed to import meetings from Zoom');
  } finally {
    setImportLoading(false);
  }
};
```

### 4. Routes Configuration

Add to your `meetingRoutes.js`:

```javascript
router.post('/admin/import-from-zoom', auth, importFromZoom);
```

## Zoom API Key Concepts

### Meeting Types
- **Type 1**: Instant meeting
- **Type 2**: Scheduled meeting
- **Type 3**: Recurring meeting with no fixed time
- **Type 4**: PMI Meeting
- **Type 8**: Recurring meeting with fixed time

### API Endpoint
```
GET /v2/users/{userId}/meetings
```
- Use "me" for current authenticated user
- Maximum page_size is 300
- Returns scheduled meetings only (not instant meetings)

### Response Structure
```json
{
  "page_count": 1,
  "page_number": 1,
  "page_size": 30,
  "total_records": 2,
  "next_page_token": "",
  "meetings": [
    {
      "id": 123456789,
      "topic": "Team Meeting",
      "type": 2,
      "start_time": "2024-10-31T10:00:00Z",
      "duration": 60,
      "timezone": "UTC",
      "created_at": "2024-10-30T12:00:00Z",
      "join_url": "https://zoom.us/j/123456789"
    }
  ]
}
```

## Database Schema Requirements

```sql
CREATE TABLE virtual_meetings (
  id UUID PRIMARY KEY,
  title VARCHAR(255),
  description TEXT,
  platform VARCHAR(50),
  scheduled_date TIMESTAMP,
  duration_minutes INTEGER,
  timezone VARCHAR(100),
  meeting_url TEXT,
  meeting_id VARCHAR(255) UNIQUE,
  meeting_password VARCHAR(100),
  host_id UUID REFERENCES users(id),
  max_participants INTEGER,
  platform_data JSONB,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

## Environment Variables Required

```env
ZOOM_ACCOUNT_ID=your_account_id
ZOOM_CLIENT_ID=your_client_id
ZOOM_CLIENT_SECRET=your_client_secret
ZOOM_USER_EMAIL=me
```

## Error Handling

### Common Errors and Solutions

1. **"No access token"**
   - Ensure ZOOM_CLIENT_ID and ZOOM_CLIENT_SECRET are set
   - Check Server-to-Server OAuth app is activated in Zoom

2. **"Invalid access token"**
   - Token may have expired
   - Regenerate token using the getAccessToken function

3. **"No meetings found"**
   - Zoom account may not have any scheduled meetings
   - Only scheduled meetings are returned (not instant meetings)

4. **"Rate limit exceeded"**
   - Zoom API has rate limits
   - Implement retry logic with exponential backoff

## Testing

### Test Import Function
```bash
curl -X POST http://localhost:5000/api/meetings/admin/import-from-zoom \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"selectiveImport": false}'
```

### Test Selective Import
```bash
curl -X POST http://localhost:5000/api/meetings/admin/import-from-zoom \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "selectiveImport": true,
    "meetingIds": ["123456789", "987654321"]
  }'
```

## Security Considerations

1. **Admin Only**: Only admin users should be able to import meetings
2. **Token Security**: Never expose Zoom credentials to frontend
3. **Rate Limiting**: Implement rate limiting on import endpoint
4. **Duplicate Prevention**: Always check for existing meetings before import
5. **Validation**: Validate all data from Zoom API before inserting

## Performance Optimizations

1. **Pagination**: Handle large meeting lists with pagination
2. **Batch Processing**: Process meetings in batches to avoid timeouts
3. **Caching**: Cache access tokens to reduce API calls
4. **Deduplication**: Use Map for efficient duplicate removal
5. **Selective Import**: Allow importing specific meetings by ID

## Troubleshooting

### Debug Logging
Add detailed logging to track the import process:

```javascript
console.log('📥 Starting Zoom import...');
console.log(`✓ Found ${meetings.length} meetings`);
console.log(`⚠️ Failed to import meeting ${id}`);
console.log('✅ Import completed successfully');
```

### Common Issues

1. **Meetings not appearing after import**
   - Check database connection
   - Verify meeting_id uniqueness constraint
   - Check scheduled_date format

2. **Import timing out**
   - Reduce page_size parameter
   - Implement async queue for large imports
   - Add timeout handling

3. **Duplicate meetings**
   - Ensure deduplication logic is working
   - Check meeting_id is correctly stored

---

**Last Updated**: October 31, 2024
**Tested With**: Zoom API v2, Server-to-Server OAuth
**Author**: Claude (Anthropic)