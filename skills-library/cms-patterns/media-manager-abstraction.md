# Media Manager Abstraction

> One upload component that works with local disk, S3, or Cloudinary — swap providers without changing app code
---

## Overview

A media manager that abstracts where files are stored. Upload an image in your app — it works the same whether files go to the local server, Amazon S3, Cloudinary, or any future provider. Switch providers by changing one config line, not rewriting upload code.

**Why this matters:**
- **Local dev:** Files go to `./uploads/` — no cloud accounts needed
- **Small VPS:** Files go to disk — no monthly cloud bills
- **Scale up:** Switch to S3 or Cloudinary — zero code changes
- **Ministry context:** Start free (local), upgrade when the church grows

---

## Architecture

```
┌─────────────────────────────────┐
│  React: MediaUploader Component │
│  (drag & drop, paste, browse)   │
│                                  │
│  POST /api/media/upload          │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  Express: MediaService          │
│                                  │
│  ┌───────────────────────────┐  │
│  │ Provider Interface        │  │
│  │                           │  │
│  │  upload(file) → url       │  │
│  │  delete(key) → void       │  │
│  │  list(prefix) → files[]   │  │
│  │  getSignedUrl(key) → url  │  │
│  └───────────┬───────────────┘  │
│              │                   │
│   ┌──────────┼──────────┐       │
│   ▼          ▼          ▼       │
│ Local      S3      Cloudinary   │
│ Disk     Bucket    Account      │
└─────────────────────────────────┘
```

---

## Provider Interface

```js
// server/services/media/MediaProvider.js

/**
 * Abstract interface for media storage providers.
 * All providers must implement these methods.
 */
class MediaProvider {
  /**
   * Upload a file and return its public URL.
   * @param {Buffer} buffer - File content
   * @param {string} filename - Original filename
   * @param {string} mimeType - MIME type (e.g., 'image/jpeg')
   * @param {string} folder - Optional subfolder (e.g., 'lessons', 'avatars')
   * @returns {Promise<{ url: string, key: string, size: number }>}
   */
  async upload(buffer, filename, mimeType, folder = '') {
    throw new Error('upload() not implemented');
  }

  /**
   * Delete a file by its storage key.
   * @param {string} key - Storage key returned from upload()
   * @returns {Promise<void>}
   */
  async delete(key) {
    throw new Error('delete() not implemented');
  }

  /**
   * List files in a folder.
   * @param {string} prefix - Folder prefix to list
   * @param {number} limit - Max results
   * @returns {Promise<Array<{ key: string, url: string, size: number, lastModified: Date }>>}
   */
  async list(prefix = '', limit = 50) {
    throw new Error('list() not implemented');
  }

  /**
   * Get a temporary signed URL for private files.
   * For public providers (local, Cloudinary), this just returns the public URL.
   * @param {string} key - Storage key
   * @param {number} expiresInSeconds - URL expiry (default 3600)
   * @returns {Promise<string>}
   */
  async getSignedUrl(key, expiresInSeconds = 3600) {
    throw new Error('getSignedUrl() not implemented');
  }
}

module.exports = MediaProvider;
```

---

## Provider: Local Disk

```js
// server/services/media/LocalProvider.js
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');
const MediaProvider = require('./MediaProvider');

class LocalProvider extends MediaProvider {
  constructor(config = {}) {
    super();
    this.uploadDir = config.uploadDir || path.join(process.cwd(), 'uploads');
    this.publicPath = config.publicPath || '/uploads';
  }

  async upload(buffer, filename, mimeType, folder = '') {
    const ext = path.extname(filename);
    const hash = crypto.randomBytes(8).toString('hex');
    const safeFilename = `${Date.now()}-${hash}${ext}`;

    const dir = folder
      ? path.join(this.uploadDir, folder)
      : this.uploadDir;

    await fs.mkdir(dir, { recursive: true });

    const filePath = path.join(dir, safeFilename);
    await fs.writeFile(filePath, buffer);

    const key = folder ? `${folder}/${safeFilename}` : safeFilename;
    const url = `${this.publicPath}/${key}`;

    return { url, key, size: buffer.length };
  }

  async delete(key) {
    const filePath = path.join(this.uploadDir, key);
    try {
      await fs.unlink(filePath);
    } catch (err) {
      if (err.code !== 'ENOENT') throw err;
    }
  }

  async list(prefix = '', limit = 50) {
    const dir = prefix
      ? path.join(this.uploadDir, prefix)
      : this.uploadDir;

    try {
      const files = await fs.readdir(dir);
      const results = [];

      for (const file of files.slice(0, limit)) {
        const filePath = path.join(dir, file);
        const stat = await fs.stat(filePath);
        if (stat.isFile()) {
          const key = prefix ? `${prefix}/${file}` : file;
          results.push({
            key,
            url: `${this.publicPath}/${key}`,
            size: stat.size,
            lastModified: stat.mtime,
          });
        }
      }

      return results;
    } catch (err) {
      if (err.code === 'ENOENT') return [];
      throw err;
    }
  }

  async getSignedUrl(key) {
    return `${this.publicPath}/${key}`;
  }
}

module.exports = LocalProvider;
```

---

## Provider: Amazon S3

```js
// server/services/media/S3Provider.js
const { S3Client, PutObjectCommand, DeleteObjectCommand,
        ListObjectsV2Command, GetObjectCommand } = require('@aws-sdk/client-s3');
const { getSignedUrl } = require('@aws-sdk/s3-request-presigner');
const crypto = require('crypto');
const path = require('path');
const MediaProvider = require('./MediaProvider');

class S3Provider extends MediaProvider {
  constructor(config) {
    super();
    this.bucket = config.bucket;
    this.region = config.region || 'us-east-1';
    this.prefix = config.prefix || '';
    this.cdnUrl = config.cdnUrl || null; // Optional CloudFront URL

    this.client = new S3Client({
      region: this.region,
      credentials: config.credentials || undefined, // Uses env vars if not provided
    });
  }

  async upload(buffer, filename, mimeType, folder = '') {
    const ext = path.extname(filename);
    const hash = crypto.randomBytes(8).toString('hex');
    const key = [this.prefix, folder, `${Date.now()}-${hash}${ext}`]
      .filter(Boolean)
      .join('/');

    await this.client.send(new PutObjectCommand({
      Bucket: this.bucket,
      Key: key,
      Body: buffer,
      ContentType: mimeType,
    }));

    const url = this.cdnUrl
      ? `${this.cdnUrl}/${key}`
      : `https://${this.bucket}.s3.${this.region}.amazonaws.com/${key}`;

    return { url, key, size: buffer.length };
  }

  async delete(key) {
    await this.client.send(new DeleteObjectCommand({
      Bucket: this.bucket,
      Key: key,
    }));
  }

  async list(prefix = '', limit = 50) {
    const fullPrefix = [this.prefix, prefix].filter(Boolean).join('/');
    const response = await this.client.send(new ListObjectsV2Command({
      Bucket: this.bucket,
      Prefix: fullPrefix,
      MaxKeys: limit,
    }));

    return (response.Contents || []).map((obj) => ({
      key: obj.Key,
      url: this.cdnUrl
        ? `${this.cdnUrl}/${obj.Key}`
        : `https://${this.bucket}.s3.${this.region}.amazonaws.com/${obj.Key}`,
      size: obj.Size,
      lastModified: obj.LastModified,
    }));
  }

  async getSignedUrl(key, expiresInSeconds = 3600) {
    const command = new GetObjectCommand({ Bucket: this.bucket, Key: key });
    return getSignedUrl(this.client, command, { expiresIn: expiresInSeconds });
  }
}

module.exports = S3Provider;
```

---

## Provider: Cloudinary

```js
// server/services/media/CloudinaryProvider.js
const cloudinary = require('cloudinary').v2;
const crypto = require('crypto');
const MediaProvider = require('./MediaProvider');

class CloudinaryProvider extends MediaProvider {
  constructor(config) {
    super();
    cloudinary.config({
      cloud_name: config.cloudName,
      api_key: config.apiKey,
      api_secret: config.apiSecret,
    });
    this.folder = config.folder || '';
  }

  async upload(buffer, filename, mimeType, folder = '') {
    const uploadFolder = [this.folder, folder].filter(Boolean).join('/');

    return new Promise((resolve, reject) => {
      const stream = cloudinary.uploader.upload_stream(
        {
          folder: uploadFolder,
          resource_type: 'auto',
        },
        (err, result) => {
          if (err) return reject(err);
          resolve({
            url: result.secure_url,
            key: result.public_id,
            size: result.bytes,
          });
        }
      );
      stream.end(buffer);
    });
  }

  async delete(key) {
    await cloudinary.uploader.destroy(key);
  }

  async list(prefix = '', limit = 50) {
    const fullPrefix = [this.folder, prefix].filter(Boolean).join('/');
    const result = await cloudinary.api.resources({
      type: 'upload',
      prefix: fullPrefix,
      max_results: limit,
    });

    return result.resources.map((r) => ({
      key: r.public_id,
      url: r.secure_url,
      size: r.bytes,
      lastModified: new Date(r.created_at),
    }));
  }

  async getSignedUrl(key) {
    return cloudinary.url(key, { sign_url: true, type: 'authenticated' });
  }
}

module.exports = CloudinaryProvider;
```

---

## Media Service (Factory + Database Tracking)

```js
// server/services/media/MediaService.js
const LocalProvider = require('./LocalProvider');
const S3Provider = require('./S3Provider');
const CloudinaryProvider = require('./CloudinaryProvider');

class MediaService {
  constructor(db, config = {}) {
    this.db = db;
    this.provider = MediaService.createProvider(config);
  }

  static createProvider(config) {
    switch (config.provider || 'local') {
      case 'local':
        return new LocalProvider(config.local);
      case 's3':
        return new S3Provider(config.s3);
      case 'cloudinary':
        return new CloudinaryProvider(config.cloudinary);
      default:
        throw new Error(`Unknown media provider: ${config.provider}`);
    }
  }

  async upload(file, folder, userId) {
    // Upload to provider
    const result = await this.provider.upload(file.buffer, file.originalname, file.mimetype, folder);

    // Track in database
    await this.db.query(
      `INSERT INTO media_files (storage_key, url, filename, mime_type, size_bytes, folder, uploaded_by)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [result.key, result.url, file.originalname, file.mimetype, result.size, folder || null, userId]
    );

    return result;
  }

  async delete(key, userId) {
    await this.provider.delete(key);
    await this.db.query(`DELETE FROM media_files WHERE storage_key = ?`, [key]);
  }

  async list(folder = '', page = 1, limit = 20) {
    const offset = (page - 1) * limit;
    let query = `SELECT * FROM media_files`;
    const params = [];

    if (folder) {
      query += ` WHERE folder = ?`;
      params.push(folder);
    }

    query += ` ORDER BY created_at DESC LIMIT ? OFFSET ?`;
    params.push(limit, offset);

    return this.db.query(query, params);
  }

  async search(term) {
    return this.db.query(
      `SELECT * FROM media_files WHERE filename LIKE ? ORDER BY created_at DESC LIMIT 50`,
      [`%${term}%`]
    );
  }
}

module.exports = MediaService;
```

---

## Database Schema for Media Tracking

### MySQL

```sql
CREATE TABLE media_files (
  id INT AUTO_INCREMENT PRIMARY KEY,
  storage_key VARCHAR(500) NOT NULL,
  url VARCHAR(1000) NOT NULL,
  filename VARCHAR(255) NOT NULL,
  mime_type VARCHAR(100) NOT NULL,
  size_bytes INT NOT NULL,
  folder VARCHAR(255),
  alt_text VARCHAR(500),
  uploaded_by VARCHAR(36) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_folder (folder),
  INDEX idx_mime (mime_type),
  INDEX idx_uploader (uploaded_by),
  FOREIGN KEY (uploaded_by) REFERENCES users(id)
);
```

### PostgreSQL

```sql
CREATE TABLE media_files (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  storage_key VARCHAR(500) NOT NULL,
  url VARCHAR(1000) NOT NULL,
  filename VARCHAR(255) NOT NULL,
  mime_type VARCHAR(100) NOT NULL,
  size_bytes INT NOT NULL,
  folder VARCHAR(255),
  alt_text VARCHAR(500),
  uploaded_by UUID NOT NULL REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mf_folder ON media_files(folder);
CREATE INDEX idx_mf_mime ON media_files(mime_type);
```

---

## Configuration

```js
// config/media.js
// Change provider by setting MEDIA_PROVIDER env var

module.exports = {
  provider: process.env.MEDIA_PROVIDER || 'local',

  local: {
    uploadDir: process.env.UPLOAD_DIR || './uploads',
    publicPath: '/uploads',
  },

  s3: {
    bucket: process.env.AWS_S3_BUCKET,
    region: process.env.AWS_REGION || 'us-east-1',
    cdnUrl: process.env.CDN_URL || null,
    credentials: process.env.AWS_ACCESS_KEY_ID ? {
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    } : undefined,
  },

  cloudinary: {
    cloudName: process.env.CLOUDINARY_CLOUD_NAME,
    apiKey: process.env.CLOUDINARY_API_KEY,
    apiSecret: process.env.CLOUDINARY_API_SECRET,
    folder: process.env.CLOUDINARY_FOLDER || 'ministry-lms',
  },
};
```

---

## React: Media Upload Component

```jsx
// components/cms/MediaUploader.jsx
import { useState, useCallback } from 'react';

/**
 * Drag-and-drop media uploader with preview.
 *
 * Props:
 *   folder   — upload folder (e.g., 'lessons', 'avatars')
 *   accept   — accepted MIME types (default: images)
 *   maxSizeMB — max file size in MB (default: 10)
 *   onUpload — callback(result) when upload succeeds
 */
export default function MediaUploader({
  folder = '',
  accept = 'image/*',
  maxSizeMB = 10,
  onUpload,
}) {
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = useCallback(async (file) => {
    setError(null);

    // Validate size
    if (file.size > maxSizeMB * 1024 * 1024) {
      setError(`File too large. Maximum ${maxSizeMB}MB.`);
      return;
    }

    // Validate type
    if (accept !== '*' && !file.type.match(accept.replace('*', '.*'))) {
      setError(`Invalid file type. Accepted: ${accept}`);
      return;
    }

    // Show preview for images
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    }

    // Upload
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('folder', folder);

      const res = await fetch('/api/media/upload', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Upload failed');

      const result = await res.json();
      onUpload?.(result);
    } catch (err) {
      setError('Upload failed. Please try again.');
      console.error(err);
    } finally {
      setUploading(false);
    }
  }, [folder, accept, maxSizeMB, onUpload]);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handlePaste = (e) => {
    const file = e.clipboardData?.files[0];
    if (file) handleFile(file);
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onPaste={handlePaste}
      style={{
        border: `2px dashed ${dragOver ? '#3b82f6' : '#d1d5db'}`,
        borderRadius: '8px',
        padding: '24px',
        textAlign: 'center',
        background: dragOver ? '#eff6ff' : '#fafafa',
        transition: 'all 0.2s',
        cursor: 'pointer',
      }}
    >
      {preview && (
        <img
          src={preview}
          alt="Preview"
          style={{ maxWidth: '200px', maxHeight: '120px', borderRadius: '4px', marginBottom: '12px' }}
        />
      )}

      {uploading ? (
        <p>Uploading...</p>
      ) : (
        <>
          <p style={{ margin: '0 0 8px', fontWeight: '500' }}>
            Drop a file here, paste from clipboard, or click to browse
          </p>
          <input
            type="file"
            accept={accept}
            onChange={(e) => e.target.files[0] && handleFile(e.target.files[0])}
            style={{ display: 'none' }}
            id="media-upload-input"
          />
          <label
            htmlFor="media-upload-input"
            style={{
              background: '#3b82f6',
              color: 'white',
              padding: '8px 20px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Browse Files
          </label>
          <p style={{ color: '#9ca3af', fontSize: '13px', marginTop: '8px' }}>
            Max {maxSizeMB}MB | {accept}
          </p>
        </>
      )}

      {error && (
        <p style={{ color: '#ef4444', fontSize: '13px', marginTop: '8px' }}>{error}</p>
      )}
    </div>
  );
}
```

---

## React: Media Library Browser

```jsx
// components/cms/MediaLibrary.jsx
import { useState, useEffect } from 'react';

/**
 * Browse and select from uploaded media files.
 * Use as a modal/panel when user needs to pick an image.
 */
export default function MediaLibrary({ folder, onSelect, onClose }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const url = search
      ? `/api/media/search?q=${encodeURIComponent(search)}`
      : `/api/media?folder=${folder || ''}`;

    fetch(url)
      .then((r) => r.json())
      .then(setFiles)
      .finally(() => setLoading(false));
  }, [folder, search]);

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
      display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 10000,
    }}>
      <div style={{
        background: 'white', borderRadius: '12px', width: '90%', maxWidth: '800px',
        maxHeight: '80vh', overflow: 'auto', padding: '24px',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
          <h3 style={{ margin: 0 }}>Media Library</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer' }}>
            x
          </button>
        </div>

        <input
          type="text"
          placeholder="Search files..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            width: '100%', padding: '8px 12px', border: '1px solid #d1d5db',
            borderRadius: '6px', marginBottom: '16px', boxSizing: 'border-box',
          }}
        />

        {loading ? (
          <div>Loading...</div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: '12px' }}>
            {files.map((file) => (
              <div
                key={file.storage_key || file.key}
                onClick={() => onSelect(file)}
                style={{
                  cursor: 'pointer', border: '2px solid transparent', borderRadius: '8px',
                  overflow: 'hidden', transition: 'border-color 0.2s',
                }}
                onMouseEnter={(e) => e.currentTarget.style.borderColor = '#3b82f6'}
                onMouseLeave={(e) => e.currentTarget.style.borderColor = 'transparent'}
              >
                {file.mime_type?.startsWith('image/') ? (
                  <img src={file.url} alt={file.filename} style={{ width: '100%', height: '100px', objectFit: 'cover' }} />
                ) : (
                  <div style={{ width: '100%', height: '100px', background: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {file.mime_type?.split('/')[1] || 'file'}
                  </div>
                )}
                <div style={{ padding: '4px 6px', fontSize: '11px', color: '#6b7280', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {file.filename}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## Express Routes

```js
// server/routes/media.js
const multer = require('multer');
const MediaService = require('../services/media/MediaService');
const mediaConfig = require('../../config/media');

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
});

const mediaService = new MediaService(db, mediaConfig);

// Upload
router.post('/api/media/upload', authenticate, authorize(['admin', 'teacher']), upload.single('file'), async (req, res) => {
  const result = await mediaService.upload(req.file, req.body.folder, req.user.id);
  res.json(result);
});

// List
router.get('/api/media', authenticate, async (req, res) => {
  const files = await mediaService.list(req.query.folder, parseInt(req.query.page) || 1);
  res.json(files);
});

// Search
router.get('/api/media/search', authenticate, async (req, res) => {
  const files = await mediaService.search(req.query.q);
  res.json(files);
});

// Delete
router.delete('/api/media/:key(*)', authenticate, authorize(['admin']), async (req, res) => {
  await mediaService.delete(req.params.key, req.user.id);
  res.json({ message: 'Deleted' });
});
```

---

## Switching Providers

```bash
# Local development (default — no config needed)
# Files go to ./uploads/

# Switch to S3
MEDIA_PROVIDER=s3
AWS_S3_BUCKET=ministry-lms-media
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Switch to Cloudinary
MEDIA_PROVIDER=cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

Zero code changes. Same upload component, same API endpoints, different storage backend.

---

## Integration With Existing Skills

| Skill | How It Connects |
|-------|----------------|
| `inline-visual-editing.md` | Image field type uses MediaUploader + MediaLibrary |
| `schema-driven-form-generator.md` | `image` field type renders MediaUploader instead of text input |
| `image-optimization-pipeline.md` | Process images (resize, compress, WebP) before upload |
| `content-repurposing-pipeline.md` | Store generated media (thumbnails, audiograms) via same service |

---

## Security Checklist

- [ ] Validate file types on server (don't trust client MIME type — check magic bytes)
- [ ] Enforce file size limits in multer config
- [ ] Sanitize filenames (remove path traversal characters)
- [ ] Serve uploads from a separate domain or path (prevent XSS via uploaded HTML)
- [ ] Use signed URLs for private content (S3 pre-signed URLs)
- [ ] Rate limit upload endpoints
- [ ] Scan uploads for malware (optional — ClamAV integration)
