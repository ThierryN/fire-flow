# Image Optimization Pipeline (Sharp.js)
## Description

Production-ready Node.js image processing pipeline using Sharp (libvips). Covers resizing, format conversion, responsive image generation, metadata handling, compositing, batch processing, and Express/Multer integration.

## When to Use

- Building an upload pipeline that needs thumbnails, responsive sizes, or format conversion
- Optimizing existing images for web delivery (WebP, AVIF)
- Generating watermarked or branded image variants
- Extracting image metadata or dominant colors
- Any server-side image manipulation in Node.js

---

## Sharp.js Core Operations

### Installation

```bash
npm install sharp
# or
bun add sharp
```

Sharp ships prebuilt binaries for most platforms. No native compilation needed.

### Resize

```javascript
import sharp from 'sharp';

// Fit modes control how the image fills the target dimensions
await sharp('input.jpg')
  .resize(800, 600, { fit: 'cover' })   // Crop to fill exactly 800x600 (default)
  .toFile('output-cover.jpg');

await sharp('input.jpg')
  .resize(800, 600, { fit: 'contain', background: '#ffffff' })  // Letterbox, no crop
  .toFile('output-contain.jpg');

await sharp('input.jpg')
  .resize(800, 600, { fit: 'fill' })     // Stretch/squash to exact dimensions
  .toFile('output-fill.jpg');

await sharp('input.jpg')
  .resize(800, 600, { fit: 'inside' })   // Shrink to fit inside 800x600, preserve aspect
  .toFile('output-inside.jpg');

await sharp('input.jpg')
  .resize(800, 600, { fit: 'outside' })  // Shrink so smallest side matches, preserve aspect
  .toFile('output-outside.jpg');

// Resize by width only (auto-calculate height)
await sharp('input.jpg')
  .resize({ width: 1200 })
  .toFile('output-width.jpg');

// Resize with position control for cover mode
await sharp('input.jpg')
  .resize(400, 400, { fit: 'cover', position: 'attention' })  // Smart crop using saliency
  .toFile('output-smart.jpg');
```

### Format Conversion

```javascript
// JPEG to WebP
await sharp('photo.jpg')
  .webp({ quality: 80 })
  .toFile('photo.webp');

// PNG to AVIF
await sharp('image.png')
  .avif({ quality: 65 })
  .toFile('image.avif');

// Any format to JPEG with specific settings
await sharp('input.png')
  .jpeg({
    quality: 85,
    mozjpeg: true,        // Use mozjpeg encoder for smaller files
    chromaSubsampling: '4:4:4',  // Better color for sharp edges
  })
  .toFile('output.jpg');

// Convert to multiple formats from a single read
const pipeline = sharp('source.jpg');
await Promise.all([
  pipeline.clone().webp({ quality: 80 }).toFile('output.webp'),
  pipeline.clone().avif({ quality: 65 }).toFile('output.avif'),
  pipeline.clone().jpeg({ quality: 85, mozjpeg: true }).toFile('output.jpg'),
]);
```

### Responsive Image Generation

```javascript
const WIDTHS = [320, 640, 1024, 1920];

async function generateResponsiveImages(inputPath, outputDir, baseName) {
  const pipeline = sharp(inputPath);
  const metadata = await pipeline.metadata();

  const results = await Promise.all(
    WIDTHS
      .filter(w => w <= metadata.width)  // Don't upscale
      .flatMap(width => [
        pipeline.clone()
          .resize({ width })
          .webp({ quality: 80 })
          .toFile(`${outputDir}/${baseName}-${width}w.webp`),
        pipeline.clone()
          .resize({ width })
          .avif({ quality: 65 })
          .toFile(`${outputDir}/${baseName}-${width}w.avif`),
      ])
  );

  return results;
}

// Usage
await generateResponsiveImages('./uploads/hero.jpg', './public/images', 'hero');
```

### Metadata Extraction and Stripping

```javascript
// Extract metadata
const metadata = await sharp('photo.jpg').metadata();
console.log({
  width: metadata.width,       // 4032
  height: metadata.height,     // 3024
  format: metadata.format,     // 'jpeg'
  space: metadata.space,       // 'srgb'
  channels: metadata.channels, // 3
  hasAlpha: metadata.hasAlpha,  // false
  orientation: metadata.orientation,  // EXIF orientation (1-8)
  exif: metadata.exif,         // Buffer of raw EXIF data
  density: metadata.density,   // DPI (72, 300, etc.)
});

// Strip all metadata (EXIF, IPTC, XMP) for privacy
await sharp('photo-with-gps.jpg')
  .withMetadata(false)  // Strips everything
  .toFile('photo-clean.jpg');

// Keep metadata but fix orientation
await sharp('rotated.jpg')
  .rotate()              // Auto-rotate based on EXIF orientation
  .withMetadata()        // Preserve other metadata
  .toFile('fixed.jpg');
```

### Composite / Overlay (Watermarks, Text)

```javascript
// Watermark overlay
await sharp('photo.jpg')
  .composite([{
    input: 'watermark.png',
    gravity: 'southeast',    // Bottom-right corner
    blend: 'over',
  }])
  .toFile('watermarked.jpg');

// Semi-transparent overlay with offset
await sharp('photo.jpg')
  .composite([{
    input: Buffer.from(
      `<svg width="200" height="50">
        <text x="10" y="35" font-size="28" fill="white" opacity="0.7"
              font-family="sans-serif">My Brand</text>
      </svg>`
    ),
    top: 20,
    left: 20,
  }])
  .toFile('branded.jpg');

// Multiple overlays
await sharp('background.jpg')
  .composite([
    { input: 'logo.png', gravity: 'northwest', blend: 'over' },
    { input: 'badge.png', gravity: 'northeast', blend: 'over' },
  ])
  .toFile('composed.jpg');
```

### Blur, Sharpen, Rotate, Flip

```javascript
// Gaussian blur (sigma 1-1000)
await sharp('input.jpg').blur(5).toFile('blurred.jpg');

// Sharpen
await sharp('input.jpg')
  .sharpen({
    sigma: 1.5,       // Gaussian mask size
    m1: 1.0,          // Flat area sharpening
    m2: 2.0,          // Edge sharpening
  })
  .toFile('sharpened.jpg');

// Rotate by exact degrees (background fills empty space)
await sharp('input.jpg')
  .rotate(45, { background: '#00000000' })  // Transparent fill
  .toFile('rotated.png');

// Flip and flop
await sharp('input.jpg').flip().toFile('flipped.jpg');     // Vertical flip
await sharp('input.jpg').flop().toFile('flopped.jpg');     // Horizontal mirror
```

### Extract Dominant Color Palette

```javascript
// Get dominant color via stats
const { dominant } = await sharp('photo.jpg').stats();
console.log(`Dominant: rgb(${dominant.r}, ${dominant.g}, ${dominant.b})`);

// Extract a palette by downscaling heavily, then reading pixels
async function extractPalette(inputPath, colorCount = 5) {
  const { data, info } = await sharp(inputPath)
    .resize(colorCount, 1, { fit: 'cover' })  // Crush to N pixels
    .raw()
    .toBuffer({ resolveWithObject: true });

  const colors = [];
  for (let i = 0; i < info.width; i++) {
    const offset = i * info.channels;
    colors.push({
      r: data[offset],
      g: data[offset + 1],
      b: data[offset + 2],
      hex: `#${data[offset].toString(16).padStart(2, '0')}${data[offset + 1].toString(16).padStart(2, '0')}${data[offset + 2].toString(16).padStart(2, '0')}`,
    });
  }
  return colors;
}

const palette = await extractPalette('sunset.jpg', 5);
// [{ r: 214, g: 87, b: 42, hex: '#d6572a' }, ...]
```

---

## Production Pipeline Pattern

Complete Express middleware that handles upload, resizes to multiple sizes, converts to WebP and AVIF, strips metadata, and saves to disk.

```javascript
import sharp from 'sharp';
import path from 'path';
import fs from 'fs/promises';
import crypto from 'crypto';

const SIZES = {
  thumb:  { width: 320,  quality: { webp: 70, avif: 55 } },
  medium: { width: 640,  quality: { webp: 78, avif: 60 } },
  large:  { width: 1024, quality: { webp: 80, avif: 65 } },
  full:   { width: 1920, quality: { webp: 82, avif: 68 } },
};

const FORMATS = ['webp', 'avif'];
const OUTPUT_DIR = './public/uploads/processed';

async function processImage(inputBuffer, originalName) {
  const id = crypto.randomUUID();
  const baseName = path.parse(originalName).name;
  const imageDir = path.join(OUTPUT_DIR, id);
  await fs.mkdir(imageDir, { recursive: true });

  const pipeline = sharp(inputBuffer).rotate().withMetadata(false);
  const metadata = await pipeline.metadata();

  const variants = [];

  for (const [sizeName, config] of Object.entries(SIZES)) {
    if (config.width > metadata.width) continue;  // Never upscale

    for (const format of FORMATS) {
      const filename = `${baseName}-${sizeName}.${format}`;
      const outputPath = path.join(imageDir, filename);

      await pipeline.clone()
        .resize({ width: config.width, fit: 'inside' })
        [format]({ quality: config.quality[format] })
        .toFile(outputPath);

      variants.push({
        size: sizeName,
        format,
        width: config.width,
        path: `/uploads/processed/${id}/${filename}`,
      });
    }
  }

  return { id, originalName, variants };
}

// Express middleware
export async function imageProcessingMiddleware(req, res, next) {
  if (!req.file) return next();

  try {
    const result = await processImage(req.file.buffer, req.file.originalname);
    req.processedImage = result;
    next();
  } catch (err) {
    next(new Error(`Image processing failed: ${err.message}`));
  }
}
```

---

## Responsive Image HTML

Serve the processed variants with proper `<picture>` tags:

```html
<picture>
  <!-- AVIF: best compression, modern browsers -->
  <source
    type="image/avif"
    srcset="
      /uploads/processed/abc123/hero-thumb.avif   320w,
      /uploads/processed/abc123/hero-medium.avif  640w,
      /uploads/processed/abc123/hero-large.avif  1024w,
      /uploads/processed/abc123/hero-full.avif   1920w
    "
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 80vw, 1200px"
  />

  <!-- WebP: fallback for older browsers -->
  <source
    type="image/webp"
    srcset="
      /uploads/processed/abc123/hero-thumb.webp   320w,
      /uploads/processed/abc123/hero-medium.webp  640w,
      /uploads/processed/abc123/hero-large.webp  1024w,
      /uploads/processed/abc123/hero-full.webp   1920w
    "
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 80vw, 1200px"
  />

  <!-- JPEG: ultimate fallback -->
  <img
    src="/uploads/processed/abc123/hero-large.jpg"
    alt="Course hero image"
    width="1024"
    height="576"
    loading="lazy"
    decoding="async"
  />
</picture>
```

**`sizes` attribute explained:**
- `(max-width: 640px) 100vw` — on mobile, the image fills the viewport
- `(max-width: 1024px) 80vw` — on tablets, it fills 80% of the viewport
- `1200px` — on desktop, it never exceeds 1200px display width

The browser picks the smallest image from `srcset` that satisfies `sizes`.

---

## Format Decision Matrix

| Use Case | Format | Quality | Why |
|----------|--------|---------|-----|
| Photos (hero, gallery) | WebP 80 / AVIF 65 | High visual | AVIF 50% smaller than JPEG at equivalent quality |
| Thumbnails (cards, lists) | WebP 70 | Small dims reduce quality needs | Fast decode at small sizes matters more than fidelity |
| Icons / logos | SVG or PNG | Lossless | Sharp edges; SVG scales infinitely; PNG for raster icons |
| OG / social images | PNG 90 | High | Social platforms re-compress; start high to survive double encoding |
| User avatars | WebP 75 | Small crops | Typically 128-256px; WebP handles small images well |
| Screenshots / text-heavy | PNG or WebP lossless | Lossless | Text artifacts are very visible in lossy formats |
| Background patterns | WebP 85 | Medium-high | Repeated patterns show banding at low quality |

---

## Batch Processing Script

Convert an entire directory of images to optimized WebP and AVIF:

```javascript
#!/usr/bin/env node
// batch-optimize.mjs — Convert all images in a directory
import sharp from 'sharp';
import fs from 'fs/promises';
import path from 'path';

const INPUT_DIR = process.argv[2] || './images';
const OUTPUT_DIR = process.argv[3] || './images/optimized';
const MAX_WIDTH = 1920;
const CONCURRENCY = 4;  // Process 4 images simultaneously

const IMAGE_EXTENSIONS = new Set(['.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif']);

async function optimizeImage(inputPath, outputDir) {
  const baseName = path.parse(inputPath).name;
  const pipeline = sharp(inputPath).rotate().withMetadata(false);
  const meta = await pipeline.metadata();
  const needsResize = meta.width > MAX_WIDTH;

  const tasks = [
    pipeline.clone()
      .resize(needsResize ? { width: MAX_WIDTH } : undefined)
      .webp({ quality: 80 })
      .toFile(path.join(outputDir, `${baseName}.webp`)),
    pipeline.clone()
      .resize(needsResize ? { width: MAX_WIDTH } : undefined)
      .avif({ quality: 65 })
      .toFile(path.join(outputDir, `${baseName}.avif`)),
  ];

  const [webpResult, avifResult] = await Promise.all(tasks);
  const originalSize = (await fs.stat(inputPath)).size;

  return {
    file: baseName,
    original: `${(originalSize / 1024).toFixed(0)}KB`,
    webp: `${(webpResult.size / 1024).toFixed(0)}KB (${((1 - webpResult.size / originalSize) * 100).toFixed(0)}% smaller)`,
    avif: `${(avifResult.size / 1024).toFixed(0)}KB (${((1 - avifResult.size / originalSize) * 100).toFixed(0)}% smaller)`,
  };
}

async function main() {
  await fs.mkdir(OUTPUT_DIR, { recursive: true });

  const files = (await fs.readdir(INPUT_DIR))
    .filter(f => IMAGE_EXTENSIONS.has(path.extname(f).toLowerCase()));

  console.log(`Processing ${files.length} images (concurrency: ${CONCURRENCY})...\n`);

  // Process in batches to control memory
  for (let i = 0; i < files.length; i += CONCURRENCY) {
    const batch = files.slice(i, i + CONCURRENCY);
    const results = await Promise.all(
      batch.map(f => optimizeImage(path.join(INPUT_DIR, f), OUTPUT_DIR))
    );
    results.forEach(r => console.log(`${r.file}: ${r.original} -> WebP ${r.webp}, AVIF ${r.avif}`));
  }

  console.log('\nDone.');
}

main().catch(console.error);
```

Run: `node batch-optimize.mjs ./photos ./photos/optimized`

---

## Performance Tips

### Streaming vs Buffer

```javascript
// BUFFER MODE — holds entire image in memory (simpler, fine for < 20MB)
const buffer = await sharp(inputBuffer)
  .resize(800)
  .webp()
  .toBuffer();

// STREAMING MODE — lower memory for large images or high concurrency
import { createReadStream, createWriteStream } from 'fs';

const transform = sharp().resize(800).webp();
createReadStream('large-input.tiff')
  .pipe(transform)
  .pipe(createWriteStream('output.webp'));
```

### Sharp Concurrency Settings

```javascript
import sharp from 'sharp';

// Default: uses all CPU cores for libvips thread pool
// In a web server with many concurrent requests, LOWER this to prevent thread contention
sharp.concurrency(2);  // Use only 2 threads per Sharp operation

// Check current setting
console.log(sharp.concurrency());  // 2

// Guideline:
// - CLI batch script: sharp.concurrency(os.cpus().length) — use all cores
// - Web server (low traffic): sharp.concurrency(2)
// - Web server (high traffic): sharp.concurrency(1) — let Node handle parallelism
```

### Memory Management

```javascript
// Sharp caches decoded images by default. In long-running servers, control the cache:
sharp.cache({ memory: 256, files: 20, items: 100 });

// Or disable caching entirely if each image is processed once
sharp.cache(false);

// Always handle pipeline errors to prevent memory leaks
try {
  await sharp(input).resize(800).webp().toFile(output);
} catch (err) {
  console.error(`Failed to process ${input}: ${err.message}`);
  // Sharp cleans up internally on error, but log for monitoring
}

// For very large batches, process sequentially or in small batches
// to avoid opening hundreds of file descriptors simultaneously
```

---

## Integration with Multer

Complete upload endpoint with Multer + Sharp processing:

```javascript
import express from 'express';
import multer from 'multer';
import sharp from 'sharp';
import path from 'path';
import crypto from 'crypto';

const app = express();

// Store in memory buffer for Sharp processing (not disk)
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024,  // 10MB max
  },
  fileFilter: (req, file, cb) => {
    const allowed = /^image\/(jpeg|png|webp|avif|gif|tiff)$/;
    if (allowed.test(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error(`Unsupported image type: ${file.mimetype}`));
    }
  },
});

app.post('/api/upload', upload.single('image'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No image provided' });
  }

  try {
    const id = crypto.randomUUID();
    const outputDir = path.resolve(`./public/uploads/${id}`);
    const { mkdir } = await import('fs/promises');
    await mkdir(outputDir, { recursive: true });

    const pipeline = sharp(req.file.buffer).rotate().withMetadata(false);
    const meta = await pipeline.metadata();

    // Generate thumbnail + main image in WebP
    const [thumb, main] = await Promise.all([
      pipeline.clone()
        .resize(320, 320, { fit: 'cover', position: 'attention' })
        .webp({ quality: 70 })
        .toFile(path.join(outputDir, 'thumb.webp')),
      pipeline.clone()
        .resize({ width: Math.min(meta.width, 1920) })
        .webp({ quality: 80 })
        .toFile(path.join(outputDir, 'main.webp')),
    ]);

    res.json({
      id,
      original: {
        width: meta.width,
        height: meta.height,
        format: meta.format,
        size: req.file.size,
      },
      variants: {
        thumb: { path: `/uploads/${id}/thumb.webp`, size: thumb.size },
        main: { path: `/uploads/${id}/main.webp`, size: main.size },
      },
    });
  } catch (err) {
    res.status(500).json({ error: `Processing failed: ${err.message}` });
  }
});

// Error handler for Multer errors
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    return res.status(400).json({ error: err.message });
  }
  if (err.message.startsWith('Unsupported image type')) {
    return res.status(400).json({ error: err.message });
  }
  next(err);
});
```

---

