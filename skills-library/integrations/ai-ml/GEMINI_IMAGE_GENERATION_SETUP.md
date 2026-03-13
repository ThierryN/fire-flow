# Gemini Image Generation - Setup & Common Pitfalls

## The Problem

Generating images via Google Gemini API for course cover art and infographics. Models deprecate frequently and file serving paths cause invisible-image bugs.

### Why It Was Hard

- `gemini-2.0-flash-exp` deprecated → 404
- `responseModalities` case-sensitive (must be uppercase)
- Images saved to wrong directory (process.cwd vs __dirname)
- No error on save — just broken img tag in browser

---

## The Solution

### Current Working Model (Feb 2026)

```javascript
const model = genAI.getGenerativeModel({
  model: 'gemini-2.5-flash-image',  // NOT gemini-2.0-flash-exp
  generationConfig: {
    responseModalities: ['TEXT', 'IMAGE']  // UPPERCASE required
  }
});

const result = await model.generateContent(prompt);
const imagePart = result.response.candidates?.[0]?.content?.parts
  ?.find(p => p.inlineData);

if (!imagePart) throw new Error('No image generated');

// Save to correct directory (server/uploads, not project root/uploads)
const SERVER_DIR = path.resolve(__dirname, '..', '..');
const dir = path.join(SERVER_DIR, 'uploads', 'ai-images');
await fs.mkdir(dir, { recursive: true });
await fs.writeFile(
  path.join(dir, filename),
  Buffer.from(imagePart.inlineData.data, 'base64')
);
```

### File Path Rule

Express serves static files from `path.join(__dirname, 'uploads')` which is `server/uploads/`. Always save generated files there, not to `process.cwd()/uploads/`.

---

## Common Mistakes

- Using deprecated model names (check Google AI docs monthly)
- Lowercase `responseModalities` values
- Saving to `process.cwd()` instead of `__dirname` relative path
- Not checking if `imagePart` exists before writing

## Difficulty Level

Stars: 2/5 - Simple once you know the gotchas

---

**Author Notes:**
Google renames/deprecates image models roughly every 2-3 months. The admin-configurable model settings feature (planned) will prevent needing code changes each time.
