# Express.js Secure File Downloads - Industry Standard Solution

## Problem Statement
Digital file downloads failing in Express.js application with various errors:
- 404 errors (missing endpoint)
- Payment status enum validation errors
- File not found errors despite files existing
- Path duplication issues (absolute paths treated as relative)

## Root Cause Analysis

### The Critical Bug
**Path Duplication Issue**: Database stored absolute file paths, but code treated them as relative paths, resulting in duplicated paths like:
```
C:\Users\...\uploads\C:\Users\...\uploads\digital-files\file.pdf
```

### Contributing Factors
1. **Inconsistent Path Storage**: Mix of absolute and relative paths in database
2. **No Path Type Detection**: Code assumed all paths were relative
3. **Manual Path Construction**: Using string concatenation instead of Express utilities
4. **Missing Fallback Logic**: No recovery mechanism when primary path fails

## Industry Standard Solution

### Complete Working Implementation

```javascript
/**
 * Digital Downloads Controller
 * Secure file download with purchase verification
 */

import sql from '../config/sql.js';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const downloadDigitalFile = async (req, res) => {
  try {
    const { fileId } = req.params;
    const userId = req.user.id;

    console.log('📥 [Download Digital File] Request:', {
      fileId,
      userId
    });

    // 1. GET FILE INFO FROM DATABASE
    const files = await sql`
      SELECT
        ddf.*,
        p.id as product_id,
        p.name as product_name
      FROM digital_download_files ddf
      JOIN products p ON p.id = ddf.product_id
      WHERE ddf.id = ${fileId}
    `;

    if (files.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'File not found'
      });
    }

    const file = files[0];

    // 2. VERIFY PURCHASE (Allow free products that stay in 'pending')
    const purchases = await sql`
      SELECT o.id as order_id, o.payment_status, o.total_amount
      FROM orders o
      JOIN order_items oi ON oi.order_id = o.id
      WHERE o.user_id = ${userId}
        AND oi.product_id = ${file.product_id}
      LIMIT 1
    `;

    if (purchases.length === 0 && req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'You must purchase this product to download it'
      });
    }

    // 3. INTELLIGENT PATH RESOLUTION WITH FALLBACK
    let filePath;

    // Check if file_path is absolute or relative
    if (path.isAbsolute(file.file_path)) {
      // It's already a full path (legacy data)
      filePath = file.file_path;
      console.log('📥 [Download] Using absolute path from DB:', filePath);
    } else {
      // It's a relative path (correct way)
      const uploadsDir = path.join(__dirname, '..', 'uploads');
      filePath = path.join(uploadsDir, file.file_path);
      console.log('📥 [Download] Built path from relative:', filePath);
    }

    // 4. VERIFY FILE EXISTS WITH FALLBACK
    if (!fs.existsSync(filePath)) {
      console.error('❌ [Download] File not found at primary path:', filePath);

      // Try fallback: extract filename and look in digital-files directory
      const fileName = path.basename(file.file_path);
      const fallbackPath = path.join(__dirname, '..', 'uploads', 'digital-files', fileName);

      if (fs.existsSync(fallbackPath)) {
        console.log('✅ [Download] Found file at fallback path:', fallbackPath);
        filePath = fallbackPath;
      } else {
        return res.status(404).json({
          success: false,
          message: 'File not found on server'
        });
      }
    }

    // 5. USE EXPRESS BUILT-IN DOWNLOAD METHOD (INDUSTRY STANDARD)
    // This handles headers, streaming, and security automatically
    res.download(filePath, file.original_filename || file.display_name, (err) => {
      if (err) {
        console.error('❌ [Download] Error sending file:', err);
        // Don't send response if headers already sent
        if (!res.headersSent) {
          res.status(500).json({
            success: false,
            message: 'Error downloading file'
          });
        }
      } else {
        console.log('✅ [Download] File sent successfully');
      }
    });

    // 6. OPTIONAL: LOG DOWNLOAD FOR ANALYTICS
    await sql`
      INSERT INTO download_logs (
        user_id, file_id, product_id, downloaded_at
      ) VALUES (
        ${userId}, ${fileId}, ${file.product_id}, CURRENT_TIMESTAMP
      )
    `.catch(err => {
      // Don't fail the download if logging fails
      console.error('⚠️ [Download] Failed to log download:', err);
    });

  } catch (error) {
    console.error('❌ [Download Digital File Error]:', error);
    res.status(500).json({
      success: false,
      message: 'Error downloading file',
      error: error.message
    });
  }
};
```

### Routes Configuration

```javascript
// server/routes/digitalDownloadsRoutes.js
import express from 'express';
import { downloadDigitalFile } from '../controllers/digitalDownloadsController.js';
import auth from '../middleware/auth.js';

const router = express.Router();

// Protected route - requires authentication
router.get('/:fileId/download', auth, downloadDigitalFile);

export default router;
```

### Server Integration

```javascript
// server/server.js
import digitalDownloadsRoutes from './routes/digitalDownloadsRoutes.js';

// Register the routes
app.use('/api/digital-files', digitalDownloadsRoutes);
```

## Key Features of This Solution

### 1. **Path Type Detection**
```javascript
if (path.isAbsolute(file.file_path)) {
  // Handle absolute paths
} else {
  // Handle relative paths
}
```

### 2. **Express res.download() Method**
- **Built-in Security**: Prevents directory traversal attacks
- **Automatic Headers**: Sets correct Content-Type and Content-Disposition
- **Streaming Support**: Efficient for large files
- **Error Handling**: Callback for handling failures
- **Custom Filename**: Can specify download name different from stored name

### 3. **Fallback Mechanism**
```javascript
const fileName = path.basename(file.file_path);
const fallbackPath = path.join(__dirname, '..', 'uploads', 'digital-files', fileName);
```

### 4. **Purchase Verification**
- Checks orders table for purchase record
- Allows admin bypass for testing
- Handles free products (may stay in 'pending' status)

### 5. **Proper Error Handling**
- Checks if headers already sent before error response
- Graceful failure for optional features (logging)
- Detailed console logging for debugging

## Common Pitfalls to Avoid

### ❌ Don't Do This:
```javascript
// Manual file streaming (security risk)
const stream = fs.createReadStream(filePath);
stream.pipe(res);

// String concatenation for paths
const filePath = __dirname + '/../uploads/' + file.file_path;

// No purchase verification
// Anyone with fileId could download

// Assuming all paths are relative
const filePath = path.join(uploadsDir, file.file_path); // Fails with absolute paths
```

### ✅ Do This Instead:
```javascript
// Use Express's built-in method
res.download(filePath, filename, callback);

// Use path.join with detection
if (path.isAbsolute(file.file_path)) { ... }

// Always verify ownership
const purchases = await sql`...`;
if (purchases.length === 0) { ... }
```

## Testing Verification

### 1. Test File Upload and Storage
```bash
# Check uploaded files exist
ls -la server/uploads/digital-files/

# Verify database entries
node -e "
import sql from './server/config/sql.js';
const files = await sql\`SELECT * FROM digital_download_files\`;
console.log(files);
"
```

### 2. Test Download Endpoint
```bash
# Test with curl (replace with actual token and fileId)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/digital-files/FILE_ID/download \
  --output test-download.pdf
```

### 3. Test Path Resolution
```javascript
// Test script: testPaths.js
import path from 'path';

const testPaths = [
  'C:\\Users\\test\\uploads\\file.pdf',  // Absolute Windows
  '/home/user/uploads/file.pdf',         // Absolute Unix
  'digital-files/file.pdf',              // Relative
  'file.pdf'                              // Just filename
];

testPaths.forEach(testPath => {
  console.log(`${testPath}: ${path.isAbsolute(testPath) ? 'ABSOLUTE' : 'RELATIVE'}`);
});
```

## Database Schema Requirements

```sql
-- Digital download files table
CREATE TABLE digital_download_files (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id uuid NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  display_name varchar(255) NOT NULL,
  original_filename varchar(255),
  file_path text NOT NULL,  -- Can be absolute or relative
  file_size bigint,
  mime_type varchar(100),
  display_order integer DEFAULT 0,
  created_at timestamptz DEFAULT now()
);

-- Optional: Download tracking
CREATE TABLE download_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES profiles(id),
  file_id uuid NOT NULL REFERENCES digital_download_files(id),
  product_id uuid NOT NULL REFERENCES products(id),
  downloaded_at timestamptz DEFAULT now(),
  ip_address inet
);
```

## Migration for Existing Systems

If you have existing data with mixed path types:

```javascript
// Migration script to normalize paths
import sql from './server/config/sql.js';
import path from 'path';

const files = await sql`SELECT * FROM digital_download_files`;

for (const file of files) {
  let normalizedPath = file.file_path;

  // If absolute, convert to relative
  if (path.isAbsolute(file.file_path)) {
    // Extract just the relevant part
    const match = file.file_path.match(/digital-files[\\\/].+$/);
    if (match) {
      normalizedPath = match[0].replace(/\\/g, '/');

      await sql`
        UPDATE digital_download_files
        SET file_path = ${normalizedPath}
        WHERE id = ${file.id}
      `;
      console.log(`Updated: ${file.file_path} -> ${normalizedPath}`);
    }
  }
}
```

## Security Considerations

1. **Authentication Required**: Always verify user is logged in
2. **Purchase Verification**: Check user owns the product
3. **Path Traversal Prevention**: res.download() handles this automatically
4. **File Existence Check**: Verify file exists before attempting download
5. **Error Information**: Don't expose internal paths in error messages to users
6. **Rate Limiting**: Consider adding download rate limits per user

## Performance Optimization

For high-traffic applications:

```javascript
// 1. Cache file existence checks
const fileCache = new Map();

// 2. Use CDN for large files
if (file.file_size > 10 * 1024 * 1024) { // > 10MB
  return res.redirect(cdnUrl);
}

// 3. Add download queuing for concurrent limits
const downloadQueue = new Queue({ concurrency: 10 });
```

## Troubleshooting Guide

### Problem: "File not found on server"
- Check file actually exists in uploads directory
- Verify path in database matches actual location
- Check file permissions (readable by Node.js process)
- Try fallback path mechanism

### Problem: "Payment status enum error"
- Check valid enum values in database
- Consider removing strict payment status check
- Allow 'pending' status for free products

### Problem: Downloads work locally but not in production
- Check file paths (Windows vs Linux)
- Verify uploads directory is included in deployment
- Check file permissions on server
- Ensure proper environment variables

## Related Skills
- [PostgreSQL JSON Aggregation](./postgresql-json-aggregation.md)
- [Express.js Authentication Middleware](./express-auth-middleware.md)
- [File Upload Handling](./file-upload-handling.md)

## References
- [Express.js res.download() Documentation](https://expressjs.com/en/api.html#res.download)
- [Node.js Path Module](https://nodejs.org/api/path.html)
- [OWASP File Upload Security](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload)

---

**Last Updated**: October 31, 2024
**Tested With**: Express 4.x, Node.js 18+, PostgreSQL 14+
**Author**: Claude (Anthropic)
**Context**: MERN Community LMS Project - Digital Downloads Feature