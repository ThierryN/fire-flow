# WordPress LMS Course Data Recovery - Extraction & Migration

## The Problem

You have WordPress LMS course data exported as JSON files, and need to extract course structure, find embedded media URLs, and recreate the course in a new LMS system.

### Why It Was Hard

- LMS exports are spread across multiple JSON files (courses, lessons, topics)
- Media URLs are embedded in HTML content fields
- Course iterations create duplicate entries with slug suffixes like `-2-2-2-3`

---

## The Solution

### LMS Export Structure

| File | Post Type | Contains |
|------|-----------|----------|
| `wordpress-courses.json` | `sfwd-courses` | Course metadata |
| `wordpress-lessons.json` | `sfwd-lessons` | Lesson titles, ordering |
| `wordpress-topics.json` | `sfwd-topic` | Sub-lessons with actual content/media |

### Extract Media URLs

```bash
# Find all Castos audio URLs
grep -oE "https://[^\"']*castos[^\"']*\.mp3" wordpress-topics.json | sort -u
```

### Generate Embed HTML

```html
<audio controls style="width:100%">
  <source src="https://episodes.castos.com/.../file.mp3" type="audio/mpeg">
</audio>
```

---

## Key Insight

LMS spreads content across three post types. Lessons often just have titles - the actual content with media is in **Topics**. Always search all three JSON files.

## Difficulty Level

⭐⭐⭐ (3/5)

---

**Author Notes:**
"Activation completed during a live session" means no audio exists - it was conducted live.
