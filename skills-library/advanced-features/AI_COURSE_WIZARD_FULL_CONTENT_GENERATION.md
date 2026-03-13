# AI Course Wizard - Full Content Generation with Progress Bar

## The Problem

The AI Course Creation Wizard created only skeleton courses (section titles + empty lessons). Instructors expected the wizard to generate actual lesson content from their uploaded knowledge sources.

### Why It Was Hard

- `createFromOutline` didn't return lesson IDs — couldn't target content generation
- `generateLessonFromSources` returned content but didn't save to DB
- Needed to iterate through 30+ lessons sequentially with user-visible progress
- Required graceful failure handling (don't stop if one lesson fails)

### Impact

- Instructors created courses but still had to manually write every lesson
- The wizard was essentially useless without content generation

---

## The Solution

### 1. Return Lesson IDs from createFromOutline

```javascript
// In aiCourseController.js - createFromOutline
const sections = [];
let lessonOrder = 0;
for (const sectionData of outline.sections) {
  const [section] = await sql`
    INSERT INTO sections (...) VALUES (...) RETURNING *
  `;
  const lessons = [];
  for (const lessonData of sectionData.lessons) {
    const [lesson] = await sql`
      INSERT INTO lessons (...) VALUES (...)
      RETURNING id, title, description
    `;
    lessons.push(lesson);
  }
  sections.push({ id: section.id, title: section.title, lessons });
}
res.json({ course, sections, message: 'Course created successfully!' });
```

### 2. Save Content in generateLessonFromSources

```javascript
// When lessonId is provided, save directly to DB
if (lessonId) {
  await sql`
    UPDATE lessons
    SET content = ${result.content},
        ai_generated_metadata = ${sql.json({
          is_ai_generated: true,
          reviewed: false,
          generated_at: new Date().toISOString(),
          sources_used: result.sourcesUsed
        })},
        updated_at = NOW()
    WHERE id = ${lessonId}
  `;
}
```

### 3. WizardStepReview with Progress Bar

Key pattern: iterate through all lessons, update progress state on each, continue on failure.

```jsx
const allLessons = createdSections.flatMap(s =>
  s.lessons.map(l => ({ ...l, sectionTitle: s.title }))
);
let completed = 0;
let failed = 0;

for (const lesson of allLessons) {
  setProgress({
    current: completed + 1,
    total: allLessons.length,
    currentLesson: lesson.title,
    percent: Math.round(((completed) / allLessons.length) * 100)
  });

  try {
    await aiCourseApi.generateLessonFromSources({
      lessonId: lesson.id,
      courseId: newCourse.id,
      topic: lesson.title,
      description: lesson.description
    });
  } catch {
    failed++;
  }
  completed++;
}
```

### 4. Rich HTML Lesson Content

Enhanced the generation prompt to produce styled HTML with custom CSS classes:
- `.lesson-callout` — blue key concept boxes
- `.lesson-example` — green example boxes
- `.lesson-takeaways` — purple summary boxes
- Blockquotes for definitions
- Structured with h2/h3/p/ul/ol tags

All styled in `custom.css` with gradients, accent lines, and dark mode support.

---

## Testing

1. Upload 2+ text sources to Knowledge Library
2. Go to "Create Course with AI" wizard
3. Select sources → Generate outline → Review & Create
4. Watch progress bar iterate through all lessons
5. Open created course — all lessons should have rich formatted content

---

## Difficulty Level

Stars: 3/5 - Straightforward once you understand the data flow

---

**Author Notes:**
The key insight was that course creation and content generation are two separate steps. The wizard needed to create the skeleton first (to get IDs), then fill in content lesson-by-lesson. The progress bar makes a huge UX difference — without it, users think the wizard is frozen during the 2-3 minutes of generation.
