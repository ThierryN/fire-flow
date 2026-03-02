# Skill: File Upload Basics

**Category:** Common Tasks
**Difficulty:** Beginner–Intermediate
**Applies to:** Node.js/Express

---

## The Problem

File uploads are one of the easiest ways to get hacked if handled carelessly. Users can upload scripts, oversized files, or files with misleading extensions. Done right, uploads are simple and safe.

---

## Setup

```bash
npm install multer
```

---

## Pattern 1: Upload to Local Disk (Development)

```js
const multer = require('multer');
const path = require('path');

// Configure storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/'); // folder must exist
  },
  filename: (req, file, cb) => {
    // Use timestamp + random to avoid name collisions
    const unique = Date.now() + '-' + Math.round(Math.random() * 1e9);
    cb(null, unique + path.extname(file.originalname));
  }
});

// Configure filters
const fileFilter = (req, file, cb) => {
  const allowed = ['image/jpeg', 'image/png', 'image/webp'];
  if (allowed.includes(file.mimetype)) {
    cb(null, true);  // accept
  } else {
    cb(new Error('Only JPG, PNG, and WebP images allowed'), false); // reject
  }
};

const upload = multer({
  storage,
  fileFilter,
  limits: { fileSize: 5 * 1024 * 1024 } // 5MB max
});
```

---

## Pattern 2: Single File Upload Route

```js
// Single file upload — field name must match the form field
router.post('/upload/avatar', upload.single('avatar'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const fileUrl = `/uploads/${req.file.filename}`;
  res.json({ url: fileUrl, filename: req.file.filename });
});

// Handle multer errors
router.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE')
      return res.status(400).json({ error: 'File too large. Maximum 5MB.' });
    return res.status(400).json({ error: err.message });
  }
  if (err) return res.status(400).json({ error: err.message });
  next();
});
```

---

## Pattern 3: Frontend — Sending a File

```html
<form id="upload-form" enctype="multipart/form-data">
  <input type="file" id="avatar" name="avatar" accept="image/*" />
  <button type="submit">Upload</button>
</form>
```

```js
document.getElementById('upload-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById('avatar');
  if (!fileInput.files[0]) return alert('Please select a file');

  // Client-side size check (convenience only — server also checks)
  if (fileInput.files[0].size > 5 * 1024 * 1024) {
    return alert('File must be under 5MB');
  }

  const formData = new FormData();
  formData.append('avatar', fileInput.files[0]);

  const res = await fetch('/api/upload/avatar', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
    body: formData // Do NOT set Content-Type manually — browser sets it with boundary
  });

  const data = await res.json();
  if (res.ok) {
    document.getElementById('preview').src = data.url;
  } else {
    alert(data.error);
  }
});
```

---

## Serve Uploaded Files

```js
// In app.js — make uploads folder publicly accessible
app.use('/uploads', express.static('uploads'));
```

---

## For Production: Use Cloud Storage

Local disk doesn't work when you have multiple servers or restart loses files. Use cloud storage instead:

| Service | Free Tier | Best For |
|---------|-----------|---------|
| Cloudinary | 25GB | Images with auto-resizing |
| AWS S3 | 5GB/month | Any file type |
| Supabase Storage | 1GB | Projects already on Supabase |

With Cloudinary (simplest for images):
```bash
npm install cloudinary multer-storage-cloudinary
```

---

## Security Checklist

| Check | Why |
|-------|-----|
| Validate MIME type server-side | Extensions can be faked |
| Set file size limit | Prevents server overload |
| Store outside web root (or in cloud) | Prevents direct script execution |
| Rename uploaded files | Prevents overwriting existing files |
| Require authentication for uploads | Prevents anonymous abuse |

---

*Fire Flow Skills Library — MIT License*
