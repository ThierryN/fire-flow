# CRUD Operations for Imported Zoom Meetings

## Problem Statement
When importing meetings from Zoom, these meetings may:
- No longer exist in Zoom (past meetings, deleted meetings)
- Be expired or completed
- Have been modified outside your application

This causes errors when trying to:
- Delete imported meetings (Zoom API returns "Meeting does not exist")
- Edit imported meetings (Zoom API can't find the meeting)
- Sync changes back to Zoom

## Solution Overview
Implement graceful handling that:
1. Detects imported meetings using `platform_data.imported_from_zoom` flag
2. Attempts Zoom sync but continues on failure
3. Allows local-only operations for imported meetings
4. Provides appropriate user feedback

## Implementation

### 1. Enhanced Delete Operation

```javascript
/**
 * Cancel/Delete meeting with graceful Zoom handling
 * @route DELETE /api/meetings/:id
 * @access Private
 */
export const cancelMeeting = async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;

    // Check permissions
    const existing = await sql`
      SELECT * FROM virtual_meetings
      WHERE id = ${id}
    `;

    if (existing.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Meeting not found'
      });
    }

    const meeting = existing[0];
    const isHost = meeting.host_id === userId;
    const isAdmin = req.user.role === 'admin';

    if (!isHost && !isAdmin) {
      return res.status(403).json({
        success: false,
        message: 'Only the host or admin can cancel this meeting'
      });
    }

    // Try to delete from Zoom if it's a Zoom meeting
    // But handle gracefully if the meeting doesn't exist in Zoom anymore
    if (meeting.platform === 'zoom' && meeting.meeting_id) {
      try {
        await deleteZoomMeeting(meeting.meeting_id);
        console.log(`✅ Deleted meeting ${meeting.meeting_id} from Zoom`);
      } catch (zoomError) {
        // Check if it's a "meeting doesn't exist" error
        if (zoomError.message?.includes('does not exist') ||
            zoomError.message?.includes('3001') ||
            zoomError.message?.includes('not found')) {
          console.log(`⚠️ Meeting ${meeting.meeting_id} not found in Zoom (may be already deleted or expired)`);
          // Continue with local deletion
        } else {
          // For other errors, log but continue with local deletion
          console.error(`⚠️ Failed to delete from Zoom:`, zoomError.message);
        }
      }
    }

    // Update database - mark as cancelled or delete entirely based on preference
    if (req.query.hard_delete === 'true' || meeting.platform_data?.imported_from_zoom) {
      // For imported meetings or when hard delete is requested, remove from database
      await sql`
        DELETE FROM virtual_meetings
        WHERE id = ${id}
      `;

      res.json({
        success: true,
        message: 'Meeting deleted successfully'
      });
    } else {
      // For regular meetings, just mark as cancelled
      await sql`
        UPDATE virtual_meetings
        SET
          status = 'cancelled',
          cancelled_at = CURRENT_TIMESTAMP,
          updated_at = CURRENT_TIMESTAMP
        WHERE id = ${id}
      `;

      res.json({
        success: true,
        message: 'Meeting cancelled successfully'
      });
    }
  } catch (error) {
    console.error('❌ [Cancel Meeting Error]:', error);
    res.status(500).json({
      success: false,
      message: 'Error cancelling meeting',
      error: error.message
    });
  }
};
```

### 2. Enhanced Update Operation

```javascript
/**
 * Update meeting with graceful Zoom handling
 * @route PUT /api/meetings/:id
 * @access Private
 */
export const updateMeeting = async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;

    // Check permissions
    const existing = await sql`
      SELECT * FROM virtual_meetings
      WHERE id = ${id}
    `;

    if (existing.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Meeting not found'
      });
    }

    const meeting = existing[0];
    const isHost = meeting.host_id === userId;
    const isAdmin = req.user.role === 'admin';

    if (!isHost && !isAdmin) {
      return res.status(403).json({
        success: false,
        message: 'Only the host or admin can update this meeting'
      });
    }

    const {
      title,
      description,
      scheduled_date,
      duration_minutes,
      timezone,
      max_participants,
      status
    } = req.body;

    // Update Zoom meeting if scheduling details changed AND it's not just an imported meeting
    // Skip Zoom sync for imported meetings that may no longer exist in Zoom
    if ((title || scheduled_date || duration_minutes || timezone) &&
        meeting.platform === 'zoom' &&
        meeting.meeting_id &&
        !meeting.platform_data?.imported_from_zoom) {

      try {
        const updateData = {};
        if (title) updateData.topic = title;
        if (scheduled_date) updateData.start_time = new Date(scheduled_date).toISOString();
        if (duration_minutes) updateData.duration = duration_minutes;
        if (timezone) updateData.timezone = timezone;

        await updateZoomMeeting(meeting.meeting_id, updateData);
        console.log(`✅ Updated meeting ${meeting.meeting_id} in Zoom`);
      } catch (zoomError) {
        // Check if it's a "meeting doesn't exist" error
        if (zoomError.message?.includes('does not exist') ||
            zoomError.message?.includes('3001') ||
            zoomError.message?.includes('not found')) {
          console.log(`⚠️ Meeting ${meeting.meeting_id} not found in Zoom (imported or expired) - updating local record only`);
          // Continue with local update
        } else {
          // For other errors, log but continue with local update
          console.error(`⚠️ Failed to update in Zoom, continuing with local update:`, zoomError.message);
        }
      }
    } else if (meeting.platform_data?.imported_from_zoom) {
      console.log(`ℹ️ Skipping Zoom sync for imported meeting ${meeting.meeting_id} - updating local record only`);
    }

    // Update database
    const result = await sql`
      UPDATE virtual_meetings
      SET
        title = COALESCE(${title}, title),
        description = COALESCE(${description}, description),
        scheduled_date = COALESCE(${scheduled_date}, scheduled_date),
        duration_minutes = COALESCE(${duration_minutes}, duration_minutes),
        timezone = COALESCE(${timezone}, timezone),
        max_participants = COALESCE(${max_participants}, max_participants),
        status = COALESCE(${status}, status),
        updated_at = CURRENT_TIMESTAMP
      WHERE id = ${id}
      RETURNING *
    `;

    res.json({
      success: true,
      message: 'Meeting updated successfully',
      data: result[0]
    });
  } catch (error) {
    console.error('❌ [Update Meeting Error]:', error);
    res.status(500).json({
      success: false,
      message: 'Error updating meeting',
      error: error.message
    });
  }
};
```

### 3. Sync Status Tracking

Add a sync_status field to track the synchronization state:

```sql
-- Add sync status to virtual_meetings table
ALTER TABLE virtual_meetings
ADD COLUMN IF NOT EXISTS sync_status VARCHAR(50) DEFAULT 'synced',
ADD COLUMN IF NOT EXISTS last_sync_attempt TIMESTAMP,
ADD COLUMN IF NOT EXISTS sync_error TEXT;

-- Update sync_status for imported meetings
UPDATE virtual_meetings
SET sync_status = 'local_only'
WHERE platform_data->>'imported_from_zoom' = 'true';
```

### 4. Enhanced Import with Sync Status

```javascript
// When importing meetings, mark their sync status
const result = await sql`
  INSERT INTO virtual_meetings (
    title,
    description,
    platform,
    scheduled_date,
    duration_minutes,
    timezone,
    meeting_url,
    meeting_id,
    meeting_password,
    host_id,
    max_participants,
    platform_data,
    sync_status,  -- Add this
    created_at,
    updated_at
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
      recurring: zoomMeeting.type === 8,
      import_date: new Date().toISOString()
    }},
    'local_only',  -- Mark as local only
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
  )
  RETURNING id, title, scheduled_date
`;
```

## Zoom API Error Codes

Common error codes to handle:

| Code | Message | Action |
|------|---------|--------|
| 3001 | Meeting does not exist | Continue with local operation |
| 3002 | Meeting is ended | Continue with local operation |
| 300 | Invalid meeting ID | Log error, continue locally |
| 404 | Meeting not found | Continue with local operation |

## Frontend Handling

Update frontend to show sync status:

```javascript
// In VirtualMeetingsList.jsx
{meeting.platform_data?.imported_from_zoom && (
  <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
    <InfoIcon className="w-3 h-3" />
    Local Only
  </span>
)}

{meeting.sync_status === 'error' && (
  <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
    <AlertIcon className="w-3 h-3" />
    Sync Error
  </span>
)}
```

## Best Practices

### 1. Always Try Zoom First
```javascript
try {
  // Attempt Zoom operation
  await zoomOperation();
} catch (error) {
  // Handle gracefully
  handleZoomError(error);
}
// Continue with local operation
```

### 2. Log Appropriately
```javascript
console.log(`✅ Success message`);
console.warn(`⚠️ Warning message`);
console.error(`❌ Error message`);
console.log(`ℹ️ Info message`);
```

### 3. User Feedback
Provide clear messages about what happened:
- "Meeting deleted locally (no longer exists in Zoom)"
- "Meeting updated locally only"
- "Meeting synced with Zoom successfully"

### 4. Background Sync (Optional)
Consider implementing a background job to periodically check sync status:

```javascript
// Background job to check meeting existence in Zoom
async function checkMeetingSyncStatus() {
  const meetings = await sql`
    SELECT * FROM virtual_meetings
    WHERE platform = 'zoom'
      AND sync_status != 'local_only'
      AND scheduled_date > CURRENT_DATE - INTERVAL '30 days'
  `;

  for (const meeting of meetings) {
    try {
      await getZoomMeeting(meeting.meeting_id);
      // Meeting exists, mark as synced
      await sql`
        UPDATE virtual_meetings
        SET sync_status = 'synced',
            last_sync_attempt = CURRENT_TIMESTAMP,
            sync_error = NULL
        WHERE id = ${meeting.id}
      `;
    } catch (error) {
      if (error.message?.includes('does not exist')) {
        // Meeting doesn't exist, mark as local only
        await sql`
          UPDATE virtual_meetings
          SET sync_status = 'local_only',
              last_sync_attempt = CURRENT_TIMESTAMP,
              sync_error = ${error.message}
          WHERE id = ${meeting.id}
        `;
      }
    }
  }
}
```

## Testing

### Test Delete Operation
```bash
# Delete an imported meeting
curl -X DELETE http://localhost:5000/api/meetings/MEETING_ID \
  -H "Authorization: Bearer YOUR_TOKEN"

# Hard delete a meeting
curl -X DELETE "http://localhost:5000/api/meetings/MEETING_ID?hard_delete=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Update Operation
```bash
# Update an imported meeting
curl -X PUT http://localhost:5000/api/meetings/MEETING_ID \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Meeting Title",
    "description": "Updated description"
  }'
```

## Troubleshooting

### Issue: "Failed to delete meeting"
**Solution**: Check console logs for specific Zoom error. If it's error 3001, the meeting doesn't exist in Zoom and local deletion should proceed.

### Issue: "Failed to edit meeting"
**Solution**: Check if meeting was imported (`platform_data.imported_from_zoom = true`). Imported meetings should skip Zoom sync.

### Issue: Meetings disappearing after import
**Solution**: Ensure the delete operation checks for imported meetings and handles them appropriately (soft delete vs hard delete).

## Migration Path

For existing systems with imported meetings:

```sql
-- Mark all imported meetings as local_only
UPDATE virtual_meetings
SET platform_data = jsonb_set(
  COALESCE(platform_data, '{}'::jsonb),
  '{imported_from_zoom}',
  'true'
)
WHERE meeting_id IN (
  SELECT meeting_id
  FROM virtual_meetings
  WHERE created_at > '2024-10-01'
    AND platform = 'zoom'
    AND platform_data IS NULL
);

-- Add sync_status column if not exists
ALTER TABLE virtual_meetings
ADD COLUMN IF NOT EXISTS sync_status VARCHAR(50) DEFAULT 'synced';

-- Update sync_status for imported meetings
UPDATE virtual_meetings
SET sync_status = 'local_only'
WHERE platform_data->>'imported_from_zoom' = 'true';
```

---

**Last Updated**: October 31, 2024
**Tested With**: Zoom API v2, PostgreSQL 14+
**Author**: Claude (Anthropic)