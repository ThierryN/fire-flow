# Starter Content Pack Specification

**For: Non-Technical Pastors Installing a Fresh LMS**

This document specifies the sample content included with the Community LMS to help new administrators understand and explore the system before creating their own content.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Sample Courses](#2-sample-courses)
3. [Sample Users](#3-sample-users)
4. [Sample Pages](#4-sample-pages)
5. [Sample Media Assets](#5-sample-media-assets)
6. [Database Seed Data](#6-database-seed-data)
7. [Content Removal System](#7-content-removal-system)
8. [Installer Integration](#8-installer-integration)
9. [Content Markers](#9-content-markers)
10. [Localization Considerations](#10-localization-considerations)
11. [PostgreSQL Seed Files](#11-postgresql-seed-files)
12. [MySQL Seed Files](#12-mysql-seed-files)

---

## 1. Overview

### Purpose

The Starter Content Pack helps new administrators understand the LMS by providing example content they can:

- **Explore**: See how a fully-functioning LMS looks with real courses
- **Modify**: Practice editing content without fear of breaking anything important
- **Delete**: Remove all sample content with one click when ready to go live

### Design Principles

1. **Educational**: Content teaches users how to use the LMS itself
2. **Realistic**: Shows actual course structures for ministry contexts
3. **Safe**: Clearly marked as sample content, easily removable
4. **Minimal**: Just enough to demonstrate features, not overwhelming

### What is Included

| Content Type | Quantity | Purpose |
|--------------|----------|---------|
| Courses | 3 | Demonstrate free, tutorial, and paid course types |
| Lessons | 15+ | Show different content types (video, text, quiz) |
| Users | 2 | Test student and instructor experiences |
| Pages | 2 | Provide homepage and about page templates |
| Media Files | 6 | Placeholder images for courses and profiles |

---

## 2. Sample Courses

### Course 1: "Welcome to Your LMS" (Tutorial Course)

**Purpose**: Teach administrators how to use the system

| Field | Value |
|-------|-------|
| ID | `sample-course-welcome` |
| Title | Welcome to Your LMS |
| Slug | `welcome-to-lms` |
| Type | Free, Self-Paced |
| Level | Beginner |
| Category | Tutorial |
| Status | Published |
| Price | $0.00 |
| Thumbnail | `course-placeholder-tutorial.jpg` |
| Short Description | Learn how to use your new Learning Management System with this step-by-step tutorial. |

#### Lessons (Section: Getting Started)

| Order | Title | Content Type | Duration | Description |
|-------|-------|--------------|----------|-------------|
| 1 | Introduction to Your LMS Dashboard | Text | 5 min | Overview of the main dashboard, navigation, and key features. |
| 2 | Creating Your First Course | Video (YouTube) | 8 min | Step-by-step guide to creating a course from scratch. |
| 3 | Adding Lessons and Content | Text | 10 min | How to add text, video, and quiz content to your lessons. |
| 4 | Managing Students and Enrollments | Text | 7 min | View enrolled students, track progress, and manage access. |
| 5 | Customizing Your Site Appearance | Text | 5 min | Change colors, logos, and site settings. |
| 6 | Setting Up Payments (Optional) | Text | 8 min | Connect Stripe or PayPal for paid courses. |

#### Learning Objectives

1. Navigate the LMS admin dashboard confidently
2. Create and publish a complete course
3. Add different types of lesson content
4. Monitor student progress and enrollments
5. Customize basic site settings

---

### Course 2: "Sample Bible Study: The Book of John"

**Purpose**: Show a realistic course layout for ministry use

| Field | Value |
|-------|-------|
| ID | `sample-course-bible-study` |
| Title | Sample Bible Study: The Book of John |
| Slug | `sample-bible-study-john` |
| Type | Free, Structured |
| Level | Beginner |
| Category | Bible Study |
| Status | Published |
| Price | $0.00 |
| Thumbnail | `course-placeholder-bible.jpg` |
| Short Description | An example Bible study course showing how to structure scripture-based learning. |

#### Section 1: Introduction to John

| Order | Title | Content Type | Duration | Description |
|-------|-------|--------------|----------|-------------|
| 1 | Introduction to John's Gospel | Text | 10 min | Historical context, authorship, and themes of the Gospel of John. |
| 2 | John Chapter 1: The Word Made Flesh | Video (YouTube) | 15 min | Deep dive into the theological prologue of John's Gospel. |

#### Section 2: Key Teachings

| Order | Title | Content Type | Duration | Description |
|-------|-------|--------------|----------|-------------|
| 3 | John Chapter 3: Born Again | Text | 12 min | Jesus' conversation with Nicodemus about spiritual rebirth. |
| 4 | Quiz: Test Your Knowledge | Quiz | 5 min | 5-question quiz on John chapters 1-3. |
| 5 | Discussion: Reflection Questions | Text | 10 min | Journal prompts and small group discussion questions. |

#### Quiz Questions (Lesson 4)

```json
{
  "questions": [
    {
      "id": "sample-q1",
      "question": "According to John 1:1, what was 'in the beginning'?",
      "type": "multiple_choice",
      "options": ["The World", "The Word", "The Light", "The Law"],
      "correct_answer": 1,
      "explanation": "John 1:1 states 'In the beginning was the Word, and the Word was with God, and the Word was God.'"
    },
    {
      "id": "sample-q2",
      "question": "Who came to Jesus by night in John chapter 3?",
      "type": "multiple_choice",
      "options": ["Peter", "Judas", "Nicodemus", "John the Baptist"],
      "correct_answer": 2,
      "explanation": "Nicodemus was a Pharisee and member of the Jewish ruling council who came to Jesus at night."
    },
    {
      "id": "sample-q3",
      "question": "What famous verse appears in John 3:16?",
      "type": "short_answer",
      "expected_keywords": ["God", "loved", "world", "Son", "eternal life"],
      "explanation": "John 3:16 - 'For God so loved the world that he gave his one and only Son...'"
    },
    {
      "id": "sample-q4",
      "question": "The Word became flesh and dwelt among us.",
      "type": "true_false",
      "correct_answer": true,
      "explanation": "John 1:14 - 'The Word became flesh and made his dwelling among us.'"
    },
    {
      "id": "sample-q5",
      "question": "According to Jesus, you must be born of what two things to enter the kingdom of God?",
      "type": "multiple_choice",
      "options": ["Faith and works", "Water and Spirit", "Law and grace", "Prayer and fasting"],
      "correct_answer": 1,
      "explanation": "John 3:5 - 'Jesus answered, Very truly I tell you, no one can enter the kingdom of God unless they are born of water and the Spirit.'"
    }
  ],
  "passing_score": 70,
  "time_limit": 300
}
```

---

### Course 3: "New Believers Foundations" (Paid Example)

**Purpose**: Demonstrate paid course setup with certificates

| Field | Value |
|-------|-------|
| ID | `sample-course-new-believers` |
| Title | New Believers Foundations |
| Slug | `new-believers-foundations` |
| Type | Paid, Certificate |
| Level | Beginner |
| Category | Discipleship |
| Status | Published |
| Price | $29.00 |
| Thumbnail | `course-placeholder-faith.jpg` |
| Short Description | A comprehensive introduction to the Christian faith for new believers. (This is a sample paid course.) |
| Certificate | Enabled |

#### Section 1: Your New Life

| Order | Title | Content Type | Duration | Description |
|-------|-------|--------------|----------|-------------|
| 1 | Welcome to Your New Life in Christ | Video (YouTube) | 8 min | Congratulations on your decision! Here is what to expect. |
| 2 | Understanding Salvation | Text | 15 min | What happened when you accepted Christ, and what it means. |

#### Section 2: Growing in Faith

| Order | Title | Content Type | Duration | Description |
|-------|-------|--------------|----------|-------------|
| 3 | The Importance of Prayer | Text | 12 min | How to develop a daily prayer life. |
| 4 | Reading Your Bible | Text | 10 min | Practical tips for studying Scripture. |

#### Section 3: Completion

| Order | Title | Content Type | Duration | Description |
|-------|-------|--------------|----------|-------------|
| 5 | Final Assessment | Quiz | 10 min | Complete this assessment to earn your certificate. |

#### Certificate Configuration

```json
{
  "enabled": true,
  "template_id": "sample-certificate-template",
  "title": "Certificate of Completion",
  "subtitle": "New Believers Foundations",
  "issued_by": "Your Church Name",
  "requires_passing_grade": true,
  "passing_grade": 70
}
```

---

## 3. Sample Users

All sample users are marked with `is_sample: true` in the database.

| Username | Email | Role | Password | Purpose |
|----------|-------|------|----------|---------|
| demo_student | student@demo.local | Student | Demo123! | Test student enrollment, progress tracking, course completion |
| demo_instructor | instructor@demo.local | Instructor | Demo123! | Test course creation, student management, grading |

### Demo Student Profile

```json
{
  "id": "sample-user-student",
  "name": "Demo Student",
  "email": "student@demo.local",
  "role": "user",
  "avatar_url": "avatar-placeholder-student.png",
  "bio": "This is a sample student account for testing. You can use this account to see how students experience your courses.",
  "email_verified": true,
  "is_sample": true,
  "metadata": {
    "sample_content": true,
    "created_by": "installer"
  }
}
```

### Demo Instructor Profile

```json
{
  "id": "sample-user-instructor",
  "name": "Demo Instructor",
  "email": "instructor@demo.local",
  "role": "instructor",
  "avatar_url": "avatar-placeholder-instructor.png",
  "bio": "This is a sample instructor account for testing. Log in as this user to see instructor features.",
  "email_verified": true,
  "is_sample": true,
  "metadata": {
    "sample_content": true,
    "created_by": "installer"
  }
}
```

### Sample Enrollments

The demo student is automatically enrolled in all three sample courses:

| Student | Course | Progress | Status |
|---------|--------|----------|--------|
| demo_student | Welcome to Your LMS | 50% | In Progress |
| demo_student | Sample Bible Study | 20% | In Progress |
| demo_student | New Believers Foundations | 0% | Not Started |

---

## 4. Sample Pages

### Home Page Content

**ID**: `sample-page-home`

**Slug**: `home`

```html
<!-- Hero Section -->
<section class="hero">
  <h1>Welcome to [Your Church] Learning</h1>
  <p>Grow in your faith with our online courses and Bible studies.</p>
  <a href="/courses" class="button">Browse Courses</a>
</section>

<!-- Featured Courses Section -->
<section class="featured-courses">
  <h2>Featured Courses</h2>
  <p>Start your learning journey with these popular courses.</p>
  <!-- Courses will be dynamically inserted -->
</section>

<!-- Testimonials Section -->
<section class="testimonials">
  <h2>What Students Are Saying</h2>
  <div class="testimonial">
    <blockquote>
      "This platform has made it so easy to grow in my faith from home. The Bible studies are excellent!"
    </blockquote>
    <cite>- Sarah M., Church Member</cite>
  </div>
  <div class="testimonial">
    <blockquote>
      "I love being able to learn at my own pace. The courses are well-organized and easy to follow."
    </blockquote>
    <cite>- James T., New Believer</cite>
  </div>
</section>

<!-- Call to Action -->
<section class="cta">
  <h2>Ready to Start Learning?</h2>
  <p>Create your free account today and begin your journey.</p>
  <a href="/register" class="button">Sign Up Free</a>
</section>
```

### About Page

**ID**: `sample-page-about`

**Slug**: `about`

```html
<!-- About Hero -->
<section class="about-hero">
  <h1>About [Your Church] Learning</h1>
  <p>Equipping believers for life and ministry through online education.</p>
</section>

<!-- Mission Section -->
<section class="mission">
  <h2>Our Mission</h2>
  <p>
    We believe that everyone should have access to quality biblical education.
    Our online learning platform makes it possible for believers around the world
    to grow in their faith, study God's Word, and develop their gifts for ministry.
  </p>
</section>

<!-- Values Section -->
<section class="values">
  <h2>What We Believe</h2>
  <ul>
    <li><strong>Scripture-Centered:</strong> All our courses are grounded in biblical truth.</li>
    <li><strong>Accessible:</strong> Learning should be available to everyone, everywhere.</li>
    <li><strong>Community:</strong> We learn better together.</li>
    <li><strong>Excellence:</strong> We strive for quality in everything we create.</li>
  </ul>
</section>

<!-- Team Section Placeholder -->
<section class="team">
  <h2>Our Team</h2>
  <p><em>Add your pastoral team and instructors here.</em></p>
  <!-- Team member cards will go here -->
</section>

<!-- Contact Section -->
<section class="contact">
  <h2>Get in Touch</h2>
  <p>Have questions? We would love to hear from you.</p>
  <p>Email: <a href="mailto:info@yourchurch.com">info@yourchurch.com</a></p>
</section>
```

---

## 5. Sample Media Assets

All sample media files are stored in a dedicated `sample-content` folder within the uploads directory.

### Images (Royalty-Free, Included)

| Filename | Dimensions | Purpose | Source |
|----------|------------|---------|--------|
| `course-placeholder-tutorial.jpg` | 1200x630 | Tutorial course thumbnail | Unsplash (CC0) |
| `course-placeholder-bible.jpg` | 1200x630 | Bible study course thumbnail | Unsplash (CC0) |
| `course-placeholder-faith.jpg` | 1200x630 | New believers course thumbnail | Unsplash (CC0) |
| `avatar-placeholder-student.png` | 200x200 | Demo student avatar | Generated (CC0) |
| `avatar-placeholder-instructor.png` | 200x200 | Demo instructor avatar | Generated (CC0) |
| `hero-background.jpg` | 1920x1080 | Homepage hero section | Unsplash (CC0) |

### Video Embeds (Public Domain / Church-Friendly)

For sample video lessons, we embed publicly available YouTube videos that are appropriate for church use:

| Lesson | Video Source | Duration | Description |
|--------|--------------|----------|-------------|
| Creating Your First Course | YouTube Embed | 8:00 | Placeholder tutorial video |
| John 1: The Word | YouTube Embed | 15:00 | Public domain Bible teaching |
| Welcome to New Life | YouTube Embed | 8:00 | Placeholder welcome video |

**Note**: Sample videos use `youtube` as the provider with embed URLs. Church administrators should replace these with their own content.

### File Structure

```
/uploads/sample-content/
├── images/
│   ├── course-placeholder-tutorial.jpg
│   ├── course-placeholder-bible.jpg
│   ├── course-placeholder-faith.jpg
│   ├── avatar-placeholder-student.png
│   ├── avatar-placeholder-instructor.png
│   └── hero-background.jpg
└── metadata.json
```

### Metadata File

```json
{
  "version": "1.0.0",
  "created_at": "2025-01-01T00:00:00Z",
  "is_sample_content": true,
  "files": [
    {
      "filename": "course-placeholder-tutorial.jpg",
      "type": "image/jpeg",
      "size": 245760,
      "dimensions": "1200x630",
      "license": "CC0",
      "source": "unsplash.com"
    }
  ]
}
```

---

## 6. Database Seed Data

### Sample Content IDs

All sample content uses predictable IDs for easy identification and removal:

| Content Type | ID Pattern | Examples |
|--------------|------------|----------|
| Courses | `sample-course-*` | `sample-course-welcome`, `sample-course-bible-study` |
| Lessons | `sample-lesson-*` | `sample-lesson-001`, `sample-lesson-002` |
| Sections | `sample-section-*` | `sample-section-001`, `sample-section-002` |
| Users | `sample-user-*` | `sample-user-student`, `sample-user-instructor` |
| Pages | `sample-page-*` | `sample-page-home`, `sample-page-about` |
| Enrollments | `sample-enrollment-*` | `sample-enrollment-001` |

### Metadata Marking

Every sample content record includes:

```json
{
  "metadata": {
    "sample_content": true,
    "installer_version": "1.0.0",
    "created_at": "2025-01-01T00:00:00Z",
    "removable": true
  }
}
```

---

## 7. Content Removal System

### Admin UI: "Remove Sample Content"

**Location**: Admin > Settings > Sample Content

```
┌─────────────────────────────────────────────────────────────────┐
│  Sample Content Management                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Your site currently has sample content installed.               │
│  You can remove it when you're ready to launch with your own    │
│  courses.                                                        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Sample Content Summary                                     ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  Courses:      3 (15 lessons)                               ││
│  │  Users:        2 (student, instructor)                      ││
│  │  Pages:        2 (home, about)                              ││
│  │  Media Files:  6 images                                     ││
│  │  Enrollments:  3                                            ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Select what to remove:                                          │
│                                                                  │
│  [x] Sample courses and lessons (3 courses, 15 lessons)         │
│  [x] Sample user accounts (2 users)                             │
│  [x] Sample pages (2 pages)                                     │
│  [x] Sample media files (6 files)                               │
│                                                                  │
│  ⚠️  Warning: This action cannot be undone. Sample content      │
│      will be permanently deleted.                                │
│                                                                  │
│  [ Remove Selected ]    [ Remove All Sample Content ]           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Backend API Implementation

```javascript
// server/routes/admin/sampleContent.js

import express from 'express';
import { supabase } from '../../config/supabase.js';
import { protect, authorize } from '../../middleware/auth.js';

const router = express.Router();

// Sample content ID patterns
const SAMPLE_PATTERNS = {
  courses: 'sample-course-%',
  sections: 'sample-section-%',
  lessons: 'sample-lesson-%',
  users: 'sample-user-%',
  pages: 'sample-page-%',
  enrollments: 'sample-enrollment-%'
};

/**
 * GET /api/admin/sample-content
 * Get summary of installed sample content
 */
router.get('/', protect, authorize('admin'), async (req, res) => {
  try {
    const summary = {
      courses: 0,
      lessons: 0,
      sections: 0,
      users: 0,
      pages: 0,
      enrollments: 0,
      mediaFiles: 0
    };

    // Count sample courses
    const { count: courseCount } = await supabase
      .from('courses')
      .select('*', { count: 'exact', head: true })
      .like('id', SAMPLE_PATTERNS.courses);
    summary.courses = courseCount || 0;

    // Count sample lessons
    const { count: lessonCount } = await supabase
      .from('lessons')
      .select('*', { count: 'exact', head: true })
      .like('id', SAMPLE_PATTERNS.lessons);
    summary.lessons = lessonCount || 0;

    // Count sample sections
    const { count: sectionCount } = await supabase
      .from('sections')
      .select('*', { count: 'exact', head: true })
      .like('id', SAMPLE_PATTERNS.sections);
    summary.sections = sectionCount || 0;

    // Count sample users
    const { count: userCount } = await supabase
      .from('profiles')
      .select('*', { count: 'exact', head: true })
      .like('id', SAMPLE_PATTERNS.users);
    summary.users = userCount || 0;

    // Count sample pages
    const { count: pageCount } = await supabase
      .from('pages')
      .select('*', { count: 'exact', head: true })
      .like('id', SAMPLE_PATTERNS.pages);
    summary.pages = pageCount || 0;

    // Count sample enrollments
    const { count: enrollmentCount } = await supabase
      .from('enrollments')
      .select('*', { count: 'exact', head: true })
      .like('id', SAMPLE_PATTERNS.enrollments);
    summary.enrollments = enrollmentCount || 0;

    // Count media files in sample-content folder
    // This would check the file system or storage bucket
    summary.mediaFiles = 6; // Static count for now

    res.json({
      success: true,
      installed: summary.courses > 0,
      summary
    });
  } catch (error) {
    console.error('Error getting sample content summary:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get sample content summary'
    });
  }
});

/**
 * POST /api/admin/sample-content/remove
 * Remove selected sample content
 */
router.post('/remove', protect, authorize('admin'), async (req, res) => {
  const { courses, users, pages, media } = req.body;

  try {
    const deleted = {
      courses: 0,
      sections: 0,
      lessons: 0,
      enrollments: 0,
      lessonProgress: 0,
      users: 0,
      pages: 0,
      mediaFiles: 0
    };

    // Delete in correct order to respect foreign key constraints

    if (courses) {
      // 1. Delete lesson progress for sample lessons
      const { data: sampleLessons } = await supabase
        .from('lessons')
        .select('id')
        .like('id', SAMPLE_PATTERNS.lessons);

      if (sampleLessons?.length) {
        const lessonIds = sampleLessons.map(l => l.id);
        const { count: progressCount } = await supabase
          .from('lesson_progress')
          .delete({ count: 'exact' })
          .in('lesson_id', lessonIds);
        deleted.lessonProgress = progressCount || 0;
      }

      // 2. Delete sample enrollments
      const { count: enrollmentCount } = await supabase
        .from('enrollments')
        .delete({ count: 'exact' })
        .like('id', SAMPLE_PATTERNS.enrollments);
      deleted.enrollments = enrollmentCount || 0;

      // 3. Delete sample lessons
      const { count: lessonCount } = await supabase
        .from('lessons')
        .delete({ count: 'exact' })
        .like('id', SAMPLE_PATTERNS.lessons);
      deleted.lessons = lessonCount || 0;

      // 4. Delete sample sections
      const { count: sectionCount } = await supabase
        .from('sections')
        .delete({ count: 'exact' })
        .like('id', SAMPLE_PATTERNS.sections);
      deleted.sections = sectionCount || 0;

      // 5. Delete sample courses
      const { count: courseCount } = await supabase
        .from('courses')
        .delete({ count: 'exact' })
        .like('id', SAMPLE_PATTERNS.courses);
      deleted.courses = courseCount || 0;
    }

    if (users) {
      // Delete sample users (profiles)
      const { count: userCount } = await supabase
        .from('profiles')
        .delete({ count: 'exact' })
        .like('id', SAMPLE_PATTERNS.users);
      deleted.users = userCount || 0;
    }

    if (pages) {
      // Delete sample pages
      const { count: pageCount } = await supabase
        .from('pages')
        .delete({ count: 'exact' })
        .like('id', SAMPLE_PATTERNS.pages);
      deleted.pages = pageCount || 0;
    }

    if (media) {
      // Delete sample media files
      // This would remove files from the uploads/sample-content folder
      const fs = await import('fs/promises');
      const path = await import('path');

      const sampleContentPath = path.join(
        process.cwd(),
        'uploads',
        'sample-content'
      );

      try {
        await fs.rm(sampleContentPath, { recursive: true, force: true });
        deleted.mediaFiles = 6;
      } catch (fsError) {
        console.error('Error deleting media files:', fsError);
        // Continue even if media deletion fails
      }
    }

    // Log the removal action
    console.log('Sample content removed:', deleted);

    res.json({
      success: true,
      message: 'Sample content removed successfully',
      deleted
    });
  } catch (error) {
    console.error('Error removing sample content:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to remove sample content',
      error: error.message
    });
  }
});

export default router;
```

### React Admin Component

```jsx
// client/src/pages/admin/SampleContentManager.jsx

import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import api from '../../utils/api';

const SampleContentManager = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [removing, setRemoving] = useState(false);
  const [selected, setSelected] = useState({
    courses: true,
    users: true,
    pages: true,
    media: true
  });

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      const response = await api.get('/api/admin/sample-content');
      setSummary(response.data);
    } catch (error) {
      toast.error('Failed to load sample content information');
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (removeAll = false) => {
    const confirmMessage = removeAll
      ? 'Are you sure you want to remove ALL sample content? This cannot be undone.'
      : 'Are you sure you want to remove the selected sample content? This cannot be undone.';

    if (!window.confirm(confirmMessage)) {
      return;
    }

    setRemoving(true);

    try {
      const toRemove = removeAll
        ? { courses: true, users: true, pages: true, media: true }
        : selected;

      const response = await api.post('/api/admin/sample-content/remove', toRemove);

      if (response.data.success) {
        toast.success('Sample content removed successfully');
        fetchSummary();
      }
    } catch (error) {
      toast.error('Failed to remove sample content');
    } finally {
      setRemoving(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading sample content information...</div>;
  }

  if (!summary?.installed) {
    return (
      <div className="sample-content-manager">
        <h2>Sample Content</h2>
        <p className="success-message">
          No sample content is currently installed on your site.
        </p>
      </div>
    );
  }

  return (
    <div className="sample-content-manager">
      <h2>Sample Content Management</h2>

      <p className="description">
        Your site currently has sample content installed.
        You can remove it when you are ready to launch with your own courses.
      </p>

      <div className="summary-box">
        <h3>Sample Content Summary</h3>
        <ul>
          <li>Courses: {summary.summary.courses} ({summary.summary.lessons} lessons)</li>
          <li>Users: {summary.summary.users}</li>
          <li>Pages: {summary.summary.pages}</li>
          <li>Media Files: {summary.summary.mediaFiles}</li>
          <li>Enrollments: {summary.summary.enrollments}</li>
        </ul>
      </div>

      <div className="selection-box">
        <h3>Select what to remove:</h3>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={selected.courses}
            onChange={(e) => setSelected({ ...selected, courses: e.target.checked })}
          />
          Sample courses and lessons ({summary.summary.courses} courses, {summary.summary.lessons} lessons)
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={selected.users}
            onChange={(e) => setSelected({ ...selected, users: e.target.checked })}
          />
          Sample user accounts ({summary.summary.users} users)
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={selected.pages}
            onChange={(e) => setSelected({ ...selected, pages: e.target.checked })}
          />
          Sample pages ({summary.summary.pages} pages)
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={selected.media}
            onChange={(e) => setSelected({ ...selected, media: e.target.checked })}
          />
          Sample media files ({summary.summary.mediaFiles} files)
        </label>
      </div>

      <div className="warning-box">
        <strong>Warning:</strong> This action cannot be undone.
        Sample content will be permanently deleted.
      </div>

      <div className="button-group">
        <button
          className="btn btn-secondary"
          onClick={() => handleRemove(false)}
          disabled={removing || !Object.values(selected).some(v => v)}
        >
          {removing ? 'Removing...' : 'Remove Selected'}
        </button>

        <button
          className="btn btn-danger"
          onClick={() => handleRemove(true)}
          disabled={removing}
        >
          {removing ? 'Removing...' : 'Remove All Sample Content'}
        </button>
      </div>
    </div>
  );
};

export default SampleContentManager;
```

---

## 8. Installer Integration

### Installation Wizard Step

During the installation wizard, users are presented with the option to install sample content:

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 7 of 8: Initial Content                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Would you like to install sample content to help you           │
│  get started?                                                    │
│                                                                  │
│  ( ) Yes, install sample content                                │
│      Recommended for new users                                   │
│                                                                  │
│  ( ) No, start with a blank site                                │
│      For experienced users                                       │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Sample content includes:                                        │
│                                                                  │
│    - 3 example courses (tutorial, Bible study, paid example)    │
│    - 2 demo user accounts (student and instructor)              │
│    - Sample home and about pages                                │
│    - Placeholder images                                         │
│                                                                  │
│  Tip: You can remove sample content at any time from            │
│       Admin > Settings > Sample Content                          │
│                                                                  │
│                                      [ Back ]    [ Next ]        │
└─────────────────────────────────────────────────────────────────┘
```

### Installer Backend Logic

```javascript
// server/installer/steps/sampleContent.js

import { supabase } from '../../config/supabase.js';
import fs from 'fs/promises';
import path from 'path';

/**
 * Install sample content if user selected the option
 */
export async function installSampleContent(options = {}) {
  const { includeCourses = true, includeUsers = true, includePages = true, includeMedia = true } = options;

  const results = {
    courses: [],
    sections: [],
    lessons: [],
    users: [],
    pages: [],
    enrollments: [],
    mediaFiles: []
  };

  try {
    // 1. Install sample users first (needed for instructor_id)
    if (includeUsers) {
      results.users = await installSampleUsers();
    }

    // 2. Install sample courses
    if (includeCourses) {
      const courseData = await installSampleCourses(results.users);
      results.courses = courseData.courses;
      results.sections = courseData.sections;
      results.lessons = courseData.lessons;
    }

    // 3. Install sample pages
    if (includePages) {
      results.pages = await installSamplePages();
    }

    // 4. Install sample media
    if (includeMedia) {
      results.mediaFiles = await installSampleMedia();
    }

    // 5. Create sample enrollments
    if (includeCourses && includeUsers) {
      results.enrollments = await createSampleEnrollments(
        results.users.find(u => u.email === 'student@demo.local'),
        results.courses
      );
    }

    return {
      success: true,
      results
    };
  } catch (error) {
    console.error('Error installing sample content:', error);
    throw error;
  }
}

async function installSampleUsers() {
  const sampleUsers = [
    {
      id: 'sample-user-student',
      name: 'Demo Student',
      email: 'student@demo.local',
      role: 'user',
      avatar_url: '/uploads/sample-content/images/avatar-placeholder-student.png',
      bio: 'This is a sample student account for testing.',
      email_verified: true,
      metadata: { sample_content: true, created_by: 'installer' }
    },
    {
      id: 'sample-user-instructor',
      name: 'Demo Instructor',
      email: 'instructor@demo.local',
      role: 'instructor',
      avatar_url: '/uploads/sample-content/images/avatar-placeholder-instructor.png',
      bio: 'This is a sample instructor account for testing.',
      email_verified: true,
      metadata: { sample_content: true, created_by: 'installer' }
    }
  ];

  const { data, error } = await supabase
    .from('profiles')
    .insert(sampleUsers)
    .select();

  if (error) throw error;
  return data;
}

async function installSampleCourses(users) {
  const instructor = users?.find(u => u.role === 'instructor');

  // Sample courses data
  const courses = [
    {
      id: 'sample-course-welcome',
      title: 'Welcome to Your LMS',
      slug: 'welcome-to-lms',
      short_description: 'Learn how to use your new Learning Management System.',
      description: 'This tutorial course will guide you through all the features of your LMS.',
      level: 'beginner',
      category: 'Tutorial',
      thumbnail: '/uploads/sample-content/images/course-placeholder-tutorial.jpg',
      price: 0,
      is_published: true,
      is_approved: true,
      instructor_id: instructor?.id,
      metadata: { sample_content: true }
    },
    {
      id: 'sample-course-bible-study',
      title: 'Sample Bible Study: The Book of John',
      slug: 'sample-bible-study-john',
      short_description: 'An example Bible study course.',
      description: 'This sample course demonstrates how to structure a Bible study.',
      level: 'beginner',
      category: 'Bible Study',
      thumbnail: '/uploads/sample-content/images/course-placeholder-bible.jpg',
      price: 0,
      is_published: true,
      is_approved: true,
      instructor_id: instructor?.id,
      metadata: { sample_content: true }
    },
    {
      id: 'sample-course-new-believers',
      title: 'New Believers Foundations',
      slug: 'new-believers-foundations',
      short_description: 'A comprehensive introduction to the Christian faith.',
      description: 'This sample paid course shows how to set up certificates and pricing.',
      level: 'beginner',
      category: 'Discipleship',
      thumbnail: '/uploads/sample-content/images/course-placeholder-faith.jpg',
      price: 29.00,
      is_published: true,
      is_approved: true,
      instructor_id: instructor?.id,
      metadata: { sample_content: true }
    }
  ];

  const { data: courseData, error: courseError } = await supabase
    .from('courses')
    .insert(courses)
    .select();

  if (courseError) throw courseError;

  // Install sections and lessons for each course
  const sections = [];
  const lessons = [];

  // Course 1: Welcome to Your LMS
  sections.push({
    id: 'sample-section-welcome-1',
    title: 'Getting Started',
    course_id: 'sample-course-welcome',
    order_index: 1,
    is_published: true,
    metadata: { sample_content: true }
  });

  const welcomeLessons = [
    { title: 'Introduction to Your LMS Dashboard', content_type: 'text', order: 1 },
    { title: 'Creating Your First Course', content_type: 'video', order: 2 },
    { title: 'Adding Lessons and Content', content_type: 'text', order: 3 },
    { title: 'Managing Students and Enrollments', content_type: 'text', order: 4 },
    { title: 'Customizing Your Site Appearance', content_type: 'text', order: 5 },
    { title: 'Setting Up Payments (Optional)', content_type: 'text', order: 6 }
  ];

  welcomeLessons.forEach((lesson, index) => {
    lessons.push({
      id: `sample-lesson-welcome-${index + 1}`,
      title: lesson.title,
      course_id: 'sample-course-welcome',
      section_id: 'sample-section-welcome-1',
      order_index: lesson.order,
      content_type: lesson.content_type,
      content: getSampleLessonContent(lesson.title),
      is_published: true,
      is_free: true,
      metadata: { sample_content: true }
    });
  });

  // Course 2: Bible Study
  sections.push(
    {
      id: 'sample-section-bible-1',
      title: 'Introduction to John',
      course_id: 'sample-course-bible-study',
      order_index: 1,
      is_published: true,
      metadata: { sample_content: true }
    },
    {
      id: 'sample-section-bible-2',
      title: 'Key Teachings',
      course_id: 'sample-course-bible-study',
      order_index: 2,
      is_published: true,
      metadata: { sample_content: true }
    }
  );

  const bibleLessons = [
    { section: 'sample-section-bible-1', title: "Introduction to John's Gospel", type: 'text', order: 1 },
    { section: 'sample-section-bible-1', title: 'John Chapter 1: The Word Made Flesh', type: 'video', order: 2 },
    { section: 'sample-section-bible-2', title: 'John Chapter 3: Born Again', type: 'text', order: 3 },
    { section: 'sample-section-bible-2', title: 'Quiz: Test Your Knowledge', type: 'quiz', order: 4 },
    { section: 'sample-section-bible-2', title: 'Discussion: Reflection Questions', type: 'text', order: 5 }
  ];

  bibleLessons.forEach((lesson, index) => {
    lessons.push({
      id: `sample-lesson-bible-${index + 1}`,
      title: lesson.title,
      course_id: 'sample-course-bible-study',
      section_id: lesson.section,
      order_index: lesson.order,
      content_type: lesson.type,
      content: getSampleLessonContent(lesson.title),
      is_published: true,
      is_free: true,
      metadata: { sample_content: true }
    });
  });

  // Course 3: New Believers
  sections.push(
    {
      id: 'sample-section-believers-1',
      title: 'Your New Life',
      course_id: 'sample-course-new-believers',
      order_index: 1,
      is_published: true,
      metadata: { sample_content: true }
    },
    {
      id: 'sample-section-believers-2',
      title: 'Growing in Faith',
      course_id: 'sample-course-new-believers',
      order_index: 2,
      is_published: true,
      metadata: { sample_content: true }
    },
    {
      id: 'sample-section-believers-3',
      title: 'Completion',
      course_id: 'sample-course-new-believers',
      order_index: 3,
      is_published: true,
      metadata: { sample_content: true }
    }
  );

  const believerLessons = [
    { section: 'sample-section-believers-1', title: 'Welcome to Your New Life in Christ', type: 'video', order: 1 },
    { section: 'sample-section-believers-1', title: 'Understanding Salvation', type: 'text', order: 2 },
    { section: 'sample-section-believers-2', title: 'The Importance of Prayer', type: 'text', order: 3 },
    { section: 'sample-section-believers-2', title: 'Reading Your Bible', type: 'text', order: 4 },
    { section: 'sample-section-believers-3', title: 'Final Assessment', type: 'quiz', order: 5 }
  ];

  believerLessons.forEach((lesson, index) => {
    lessons.push({
      id: `sample-lesson-believers-${index + 1}`,
      title: lesson.title,
      course_id: 'sample-course-new-believers',
      section_id: lesson.section,
      order_index: lesson.order,
      content_type: lesson.type,
      content: getSampleLessonContent(lesson.title),
      is_published: true,
      is_free: false,
      metadata: { sample_content: true }
    });
  });

  // Insert sections
  const { error: sectionError } = await supabase
    .from('sections')
    .insert(sections);

  if (sectionError) throw sectionError;

  // Insert lessons
  const { error: lessonError } = await supabase
    .from('lessons')
    .insert(lessons);

  if (lessonError) throw lessonError;

  return { courses: courseData, sections, lessons };
}

async function installSamplePages() {
  const pages = [
    {
      id: 'sample-page-home',
      title: 'Home',
      slug: 'home',
      content: getHomePageContent(),
      status: 'published',
      is_system: false,
      metadata: { sample_content: true }
    },
    {
      id: 'sample-page-about',
      title: 'About',
      slug: 'about',
      content: getAboutPageContent(),
      status: 'published',
      is_system: false,
      metadata: { sample_content: true }
    }
  ];

  const { data, error } = await supabase
    .from('pages')
    .insert(pages)
    .select();

  if (error) throw error;
  return data;
}

async function installSampleMedia() {
  // Copy sample media files from template directory to uploads
  const sourcePath = path.join(process.cwd(), 'templates', 'sample-content', 'images');
  const destPath = path.join(process.cwd(), 'uploads', 'sample-content', 'images');

  await fs.mkdir(destPath, { recursive: true });

  const files = [
    'course-placeholder-tutorial.jpg',
    'course-placeholder-bible.jpg',
    'course-placeholder-faith.jpg',
    'avatar-placeholder-student.png',
    'avatar-placeholder-instructor.png',
    'hero-background.jpg'
  ];

  const copiedFiles = [];

  for (const file of files) {
    try {
      await fs.copyFile(path.join(sourcePath, file), path.join(destPath, file));
      copiedFiles.push(file);
    } catch (err) {
      console.warn(`Could not copy ${file}:`, err.message);
    }
  }

  return copiedFiles;
}

async function createSampleEnrollments(student, courses) {
  if (!student || !courses?.length) return [];

  const enrollments = courses.map((course, index) => ({
    id: `sample-enrollment-${index + 1}`,
    user_id: student.id,
    course_id: course.id,
    progress: index === 0 ? 50 : index === 1 ? 20 : 0,
    metadata: { sample_content: true }
  }));

  const { data, error } = await supabase
    .from('enrollments')
    .insert(enrollments)
    .select();

  if (error) throw error;
  return data;
}

function getSampleLessonContent(title) {
  // Returns appropriate sample content based on lesson title
  const contentMap = {
    'Introduction to Your LMS Dashboard': `
# Welcome to Your LMS Dashboard

This is your command center for managing your online learning platform.

## What You Will Learn
- Navigate the main menu
- Understand the dashboard widgets
- Access key features quickly

## The Dashboard Layout
When you log in as an administrator, you will see several sections...
    `,
    // Add more content for other lessons...
  };

  return contentMap[title] || `# ${title}\n\nThis is sample lesson content. Replace this with your own material.`;
}

function getHomePageContent() {
  return `<section class="hero"><h1>Welcome to Our Learning Platform</h1><p>Grow in faith through online courses.</p></section>`;
}

function getAboutPageContent() {
  return `<section class="about"><h1>About Us</h1><p>We are dedicated to equipping believers through education.</p></section>`;
}

export default { installSampleContent };
```

---

## 9. Content Markers

All sample content is marked for easy identification and removal.

### Database Markers

Every sample record includes:

```sql
-- ID prefix pattern
id LIKE 'sample-%'

-- Metadata JSON field
metadata->>'sample_content' = 'true'

-- Optional: is_sample boolean column (if added to schema)
is_sample = true
```

### Query Examples

```sql
-- Find all sample courses
SELECT * FROM courses
WHERE id LIKE 'sample-course-%'
   OR metadata->>'sample_content' = 'true';

-- Find all sample lessons
SELECT * FROM lessons
WHERE id LIKE 'sample-lesson-%';

-- Count all sample content
SELECT
  (SELECT COUNT(*) FROM courses WHERE id LIKE 'sample-%') as courses,
  (SELECT COUNT(*) FROM lessons WHERE id LIKE 'sample-%') as lessons,
  (SELECT COUNT(*) FROM sections WHERE id LIKE 'sample-%') as sections,
  (SELECT COUNT(*) FROM profiles WHERE id LIKE 'sample-%') as users,
  (SELECT COUNT(*) FROM pages WHERE id LIKE 'sample-%') as pages;
```

### File System Markers

Sample media files are stored in a dedicated directory:

```
/uploads/sample-content/
```

The directory itself acts as a marker. When sample content is removed, this entire directory is deleted.

---

## 10. Localization Considerations

### Current Implementation

- All sample content is in English (United States)
- Content uses clear, simple language suitable for translation

### Future Translation Support

Sample content is designed to support future localization:

```javascript
// Sample content with translation keys
const sampleCourse = {
  id: 'sample-course-welcome',
  title: 'sample.course.welcome.title', // Translation key
  title_default: 'Welcome to Your LMS',  // Fallback English
  description: 'sample.course.welcome.description',
  description_default: 'Learn how to use your new Learning Management System.'
};

// Translation file structure (future)
// /locales/es/sample-content.json
{
  "sample.course.welcome.title": "Bienvenido a su LMS",
  "sample.course.welcome.description": "Aprenda a usar su nuevo Sistema de Gestión de Aprendizaje."
}
```

### Text Storage Format

All translatable text is stored in a format that supports:

1. **Markdown formatting** for rich content
2. **Plain text** for titles and short descriptions
3. **HTML** for page content (with sanitization)

---

## 11. PostgreSQL Seed Files

### Main Seed File: `seed_sample_content.sql`

```sql
-- ============================================================================
-- STARTER CONTENT PACK - PostgreSQL Seed File
-- ============================================================================
-- This file installs sample content for new LMS installations.
-- All content is marked with 'sample-' prefixed IDs for easy removal.
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. SAMPLE USERS (Profiles)
-- ============================================================================

INSERT INTO profiles (
  id,
  name,
  email,
  role,
  avatar_url,
  bio,
  email_verified,
  created_at,
  updated_at
) VALUES
(
  'sample-user-student'::uuid,
  'Demo Student',
  'student@demo.local',
  'user',
  '/uploads/sample-content/images/avatar-placeholder-student.png',
  'This is a sample student account for testing. You can use this account to see how students experience your courses.',
  true,
  NOW(),
  NOW()
),
(
  'sample-user-instructor'::uuid,
  'Demo Instructor',
  'instructor@demo.local',
  'instructor',
  '/uploads/sample-content/images/avatar-placeholder-instructor.png',
  'This is a sample instructor account for testing. Log in as this user to see instructor features.',
  true,
  NOW(),
  NOW()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 2. SAMPLE COURSES
-- ============================================================================

INSERT INTO courses (
  id,
  title,
  slug,
  short_description,
  description,
  level,
  category,
  thumbnail,
  price,
  is_published,
  is_approved,
  is_featured,
  instructor_id,
  created_at,
  updated_at
) VALUES
(
  'sample-course-welcome'::uuid,
  'Welcome to Your LMS',
  'welcome-to-lms',
  'Learn how to use your new Learning Management System with this step-by-step tutorial.',
  E'# Welcome to Your LMS\n\nThis tutorial course will guide you through all the features of your Learning Management System.\n\n## What You Will Learn\n\n- How to navigate the admin dashboard\n- Creating and managing courses\n- Adding lessons with different content types\n- Managing student enrollments\n- Customizing your site\n\n## Who Is This For?\n\nThis course is designed for administrators and instructors who are new to the platform.',
  'beginner',
  'Tutorial',
  '/uploads/sample-content/images/course-placeholder-tutorial.jpg',
  0.00,
  true,
  true,
  true,
  'sample-user-instructor'::uuid,
  NOW(),
  NOW()
),
(
  'sample-course-bible-study'::uuid,
  'Sample Bible Study: The Book of John',
  'sample-bible-study-john',
  'An example Bible study course showing how to structure scripture-based learning.',
  E'# Sample Bible Study: The Gospel of John\n\nThis is an example course demonstrating how you might structure a Bible study on your LMS.\n\n## Course Overview\n\nThe Gospel of John presents a unique perspective on the life and ministry of Jesus Christ. This sample course covers the first few chapters.\n\n## What This Course Demonstrates\n\n- How to organize content into sections\n- Adding video lessons\n- Creating quizzes\n- Discussion and reflection activities',
  'beginner',
  'Bible Study',
  '/uploads/sample-content/images/course-placeholder-bible.jpg',
  0.00,
  true,
  true,
  false,
  'sample-user-instructor'::uuid,
  NOW(),
  NOW()
),
(
  'sample-course-new-believers'::uuid,
  'New Believers Foundations',
  'new-believers-foundations',
  'A comprehensive introduction to the Christian faith for new believers. (This is a sample paid course.)',
  E'# New Believers Foundations\n\nCongratulations on your decision to follow Christ! This course is designed to help you understand the foundations of the Christian faith.\n\n## What You Will Learn\n\n- What happened when you accepted Christ\n- The importance of prayer and Bible reading\n- How to grow in your faith\n- Connecting with a church community\n\n## Course Certificate\n\nComplete all lessons and pass the final assessment to receive your certificate of completion.\n\n**Note:** This is a sample paid course demonstrating pricing and certificates.',
  'beginner',
  'Discipleship',
  '/uploads/sample-content/images/course-placeholder-faith.jpg',
  29.00,
  true,
  true,
  false,
  'sample-user-instructor'::uuid,
  NOW(),
  NOW()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 3. SAMPLE SECTIONS
-- ============================================================================

INSERT INTO sections (
  id,
  title,
  description,
  course_id,
  order_index,
  is_published,
  created_at,
  updated_at
) VALUES
-- Welcome Course Sections
(
  'sample-section-welcome-1'::uuid,
  'Getting Started',
  'Learn the basics of navigating and using your LMS.',
  'sample-course-welcome'::uuid,
  1,
  true,
  NOW(),
  NOW()
),
-- Bible Study Sections
(
  'sample-section-bible-1'::uuid,
  'Introduction to John',
  'Background and context for the Gospel of John.',
  'sample-course-bible-study'::uuid,
  1,
  true,
  NOW(),
  NOW()
),
(
  'sample-section-bible-2'::uuid,
  'Key Teachings',
  'Core teachings from the first chapters of John.',
  'sample-course-bible-study'::uuid,
  2,
  true,
  NOW(),
  NOW()
),
-- New Believers Sections
(
  'sample-section-believers-1'::uuid,
  'Your New Life',
  'Understanding what happened when you accepted Christ.',
  'sample-course-new-believers'::uuid,
  1,
  true,
  NOW(),
  NOW()
),
(
  'sample-section-believers-2'::uuid,
  'Growing in Faith',
  'Practical disciplines for spiritual growth.',
  'sample-course-new-believers'::uuid,
  2,
  true,
  NOW(),
  NOW()
),
(
  'sample-section-believers-3'::uuid,
  'Completion',
  'Final assessment and certificate.',
  'sample-course-new-believers'::uuid,
  3,
  true,
  NOW(),
  NOW()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 4. SAMPLE LESSONS
-- ============================================================================

INSERT INTO lessons (
  id,
  title,
  description,
  course_id,
  section_id,
  order_index,
  content_type,
  content,
  video,
  is_published,
  is_free,
  is_preview,
  duration,
  created_at,
  updated_at
) VALUES
-- Welcome to LMS Course Lessons
(
  'sample-lesson-welcome-1'::uuid,
  'Introduction to Your LMS Dashboard',
  'Get oriented with the main dashboard and navigation.',
  'sample-course-welcome'::uuid,
  'sample-section-welcome-1'::uuid,
  1,
  'text',
  E'# Introduction to Your LMS Dashboard\n\nWelcome! This lesson will help you understand the main areas of your LMS dashboard.\n\n## The Main Menu\n\nOn the left side of your screen, you will find the main navigation menu. This is where you access:\n\n- **Dashboard** - Your home base with quick stats\n- **Courses** - Create and manage your courses\n- **Students** - View enrolled students and their progress\n- **Settings** - Customize your site\n\n## Dashboard Widgets\n\nThe dashboard shows you important information at a glance:\n\n1. **Total Students** - How many students have enrolled\n2. **Active Courses** - Your published courses\n3. **Recent Activity** - Latest enrollments and completions\n\n## Next Steps\n\nIn the next lesson, we will create your first course together!',
  '{}'::jsonb,
  true,
  true,
  true,
  5,
  NOW(),
  NOW()
),
(
  'sample-lesson-welcome-2'::uuid,
  'Creating Your First Course',
  'Step-by-step guide to creating a course from scratch.',
  'sample-course-welcome'::uuid,
  'sample-section-welcome-1'::uuid,
  2,
  'video',
  E'# Creating Your First Course\n\nWatch this video to learn how to create a course.\n\n## Video Tutorial\n\nThe video above walks through creating a complete course from start to finish.\n\n## Key Steps\n\n1. Click "New Course" from the Courses menu\n2. Add a title and description\n3. Upload a thumbnail image\n4. Set the price (or leave at $0 for free)\n5. Add sections and lessons\n6. Publish when ready',
  '{"provider": "youtube", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "duration": 480}'::jsonb,
  true,
  true,
  false,
  8,
  NOW(),
  NOW()
),
(
  'sample-lesson-welcome-3'::uuid,
  'Adding Lessons and Content',
  'How to add different types of content to your lessons.',
  'sample-course-welcome'::uuid,
  'sample-section-welcome-1'::uuid,
  3,
  'text',
  E'# Adding Lessons and Content\n\nYour LMS supports multiple content types to create engaging lessons.\n\n## Content Types\n\n### Text Lessons\nRich text content with formatting, images, and links. Perfect for reading materials.\n\n### Video Lessons\nEmbed videos from YouTube, Vimeo, or upload your own.\n\n### Quiz Lessons\nCreate assessments with multiple choice, true/false, and short answer questions.\n\n### Assignments\nLet students submit work for review and grading.\n\n## Best Practices\n\n- Mix content types to keep students engaged\n- Keep videos under 15 minutes\n- Add quizzes to check understanding\n- Use images and formatting to break up text',
  '{}'::jsonb,
  true,
  true,
  false,
  10,
  NOW(),
  NOW()
),
(
  'sample-lesson-welcome-4'::uuid,
  'Managing Students and Enrollments',
  'View enrolled students, track progress, and manage access.',
  'sample-course-welcome'::uuid,
  'sample-section-welcome-1'::uuid,
  4,
  'text',
  E'# Managing Students and Enrollments\n\nLearn how to view and manage your students.\n\n## Viewing Enrolled Students\n\nFrom the Students menu, you can see:\n- All students on your platform\n- Which courses they are enrolled in\n- Their progress in each course\n\n## Enrollment Management\n\n### Manual Enrollment\nYou can manually enroll students in any course.\n\n### Self-Enrollment\nStudents can enroll themselves through the course page.\n\n### Bulk Enrollment\nUpload a CSV file to enroll multiple students at once.\n\n## Tracking Progress\n\nThe progress tab shows:\n- Completed lessons\n- Quiz scores\n- Time spent learning\n- Certificate status',
  '{}'::jsonb,
  true,
  true,
  false,
  7,
  NOW(),
  NOW()
),
(
  'sample-lesson-welcome-5'::uuid,
  'Customizing Your Site Appearance',
  'Change colors, logos, and site settings.',
  'sample-course-welcome'::uuid,
  'sample-section-welcome-1'::uuid,
  5,
  'text',
  E'# Customizing Your Site Appearance\n\nMake your LMS reflect your church or organization brand.\n\n## Basic Customization\n\n### Site Title and Logo\n- Upload your logo (recommended: 200x50 pixels)\n- Set your site name\n- Add a tagline\n\n### Colors\n- Primary color (buttons, links)\n- Secondary color (accents)\n- Background colors\n\n### Homepage\n- Choose a hero image\n- Set welcome text\n- Feature specific courses\n\n## Advanced Options\n\n- Custom CSS for developers\n- Email template customization\n- Footer content and links',
  '{}'::jsonb,
  true,
  true,
  false,
  5,
  NOW(),
  NOW()
),
(
  'sample-lesson-welcome-6'::uuid,
  'Setting Up Payments (Optional)',
  'Connect Stripe or PayPal for paid courses.',
  'sample-course-welcome'::uuid,
  'sample-section-welcome-1'::uuid,
  6,
  'text',
  E'# Setting Up Payments\n\nIf you want to sell courses, you will need to connect a payment processor.\n\n## Supported Payment Processors\n\n### Stripe (Recommended)\n- Credit/debit cards\n- Apple Pay / Google Pay\n- Low transaction fees\n\n### PayPal\n- PayPal accounts\n- Credit cards through PayPal\n- Widely trusted\n\n## Setup Steps\n\n1. Create an account with your chosen provider\n2. Get your API keys (test mode first!)\n3. Enter keys in Settings > Payments\n4. Test with a small purchase\n5. Switch to live mode when ready\n\n## Pricing Tips\n\n- Start with lower prices to build audience\n- Offer some free courses as samples\n- Bundle courses for discounts',
  '{}'::jsonb,
  true,
  true,
  false,
  8,
  NOW(),
  NOW()
),
-- Bible Study Course Lessons
(
  'sample-lesson-bible-1'::uuid,
  'Introduction to Johns Gospel',
  'Historical context, authorship, and themes of the Gospel of John.',
  'sample-course-bible-study'::uuid,
  'sample-section-bible-1'::uuid,
  1,
  'text',
  E'# Introduction to Johns Gospel\n\nThe Gospel of John is unique among the four Gospels, offering a distinctive perspective on Jesus Christ.\n\n## Author and Date\n\nTraditionally attributed to John the Apostle, this Gospel was likely written between 90-100 AD.\n\n## Key Themes\n\n### Jesus as the Word (Logos)\nJohn begins with the profound declaration that Jesus is the eternal Word of God.\n\n### Signs and Belief\nJohn records seven miraculous signs designed to produce faith.\n\n### "I Am" Statements\nJesus makes seven "I am" declarations revealing His divine nature.\n\n## Structure\n\n- Prologue (1:1-18)\n- Book of Signs (1:19-12:50)\n- Book of Glory (13:1-20:31)\n- Epilogue (21:1-25)',
  '{}'::jsonb,
  true,
  true,
  true,
  10,
  NOW(),
  NOW()
),
(
  'sample-lesson-bible-2'::uuid,
  'John Chapter 1: The Word Made Flesh',
  'Deep dive into the theological prologue of Johns Gospel.',
  'sample-course-bible-study'::uuid,
  'sample-section-bible-1'::uuid,
  2,
  'video',
  E'# John Chapter 1: The Word Made Flesh\n\nWatch this video teaching on the prologue of Johns Gospel.\n\n## Key Verses\n\n> "In the beginning was the Word, and the Word was with God, and the Word was God." (John 1:1)\n\n> "The Word became flesh and made his dwelling among us." (John 1:14)\n\n## Discussion Questions\n\n1. What does it mean that Jesus is "the Word"?\n2. How does verse 14 describe the incarnation?\n3. What is the significance of "grace and truth"?',
  '{"provider": "youtube", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "duration": 900}'::jsonb,
  true,
  true,
  false,
  15,
  NOW(),
  NOW()
),
(
  'sample-lesson-bible-3'::uuid,
  'John Chapter 3: Born Again',
  'Jesus conversation with Nicodemus about spiritual rebirth.',
  'sample-course-bible-study'::uuid,
  'sample-section-bible-2'::uuid,
  3,
  'text',
  E'# John Chapter 3: Born Again\n\n## The Setting\n\nNicodemus, a Pharisee and member of the Jewish ruling council, comes to Jesus at night.\n\n## Key Teaching\n\n> "Very truly I tell you, no one can see the kingdom of God unless they are born again." (John 3:3)\n\n### What Does "Born Again" Mean?\n\nJesus teaches that spiritual rebirth is necessary to enter Gods kingdom. This is not a physical rebirth, but a spiritual transformation.\n\n### Water and Spirit\n\nVerse 5 mentions being born of "water and the Spirit." This likely refers to:\n- Cleansing (water)\n- New life (Spirit)\n\n## John 3:16\n\nThis famous verse summarizes the gospel message:\n\n> "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life."',
  '{}'::jsonb,
  true,
  true,
  false,
  12,
  NOW(),
  NOW()
),
(
  'sample-lesson-bible-4'::uuid,
  'Quiz: Test Your Knowledge',
  '5-question quiz on John chapters 1-3.',
  'sample-course-bible-study'::uuid,
  'sample-section-bible-2'::uuid,
  4,
  'quiz',
  E'{"questions":[{"id":"sample-q1","question":"According to John 1:1, what was in the beginning?","type":"multiple_choice","options":["The World","The Word","The Light","The Law"],"correct_answer":1,"explanation":"John 1:1 states In the beginning was the Word, and the Word was with God, and the Word was God."},{"id":"sample-q2","question":"Who came to Jesus by night in John chapter 3?","type":"multiple_choice","options":["Peter","Judas","Nicodemus","John the Baptist"],"correct_answer":2,"explanation":"Nicodemus was a Pharisee and member of the Jewish ruling council who came to Jesus at night."},{"id":"sample-q3","question":"The Word became flesh and dwelt among us.","type":"true_false","correct_answer":true,"explanation":"John 1:14 - The Word became flesh and made his dwelling among us."},{"id":"sample-q4","question":"According to Jesus, what must happen to enter the kingdom of God?","type":"multiple_choice","options":["Keep the commandments","Be born again","Give all possessions to the poor","Be baptized"],"correct_answer":1,"explanation":"John 3:3 - Jesus answered, Very truly I tell you, no one can see the kingdom of God unless they are born again."},{"id":"sample-q5","question":"John 3:16 says God gave His Son so that whoever believes will have what?","type":"multiple_choice","options":["Wisdom","Eternal life","Prosperity","Many children"],"correct_answer":1,"explanation":"John 3:16 - whoever believes in him shall not perish but have eternal life."}],"passing_score":70,"time_limit":300}',
  '{}'::jsonb,
  true,
  true,
  false,
  5,
  NOW(),
  NOW()
),
(
  'sample-lesson-bible-5'::uuid,
  'Discussion: Reflection Questions',
  'Journal prompts and small group discussion questions.',
  'sample-course-bible-study'::uuid,
  'sample-section-bible-2'::uuid,
  5,
  'text',
  E'# Discussion: Reflection Questions\n\nTake time to reflect on what you have learned.\n\n## Personal Reflection\n\nAnswer these questions in your journal:\n\n1. What new insight did you gain from studying Johns prologue?\n2. How does understanding Jesus as "the Word" change how you think about Scripture?\n3. What does being "born again" mean to you personally?\n\n## Small Group Discussion\n\nIf you are studying with others, discuss:\n\n1. Why do you think Nicodemus came to Jesus at night?\n2. How would you explain "born again" to someone unfamiliar with Christianity?\n3. How does John 3:16 summarize the gospel message?\n\n## Prayer Focus\n\n- Thank God for sending Jesus as "the Word made flesh"\n- Ask for deeper understanding of spiritual rebirth\n- Pray for opportunities to share Gods love with others',
  '{}'::jsonb,
  true,
  true,
  false,
  10,
  NOW(),
  NOW()
),
-- New Believers Course Lessons
(
  'sample-lesson-believers-1'::uuid,
  'Welcome to Your New Life in Christ',
  'Congratulations on your decision! Here is what to expect.',
  'sample-course-new-believers'::uuid,
  'sample-section-believers-1'::uuid,
  1,
  'video',
  E'# Welcome to Your New Life in Christ\n\nCongratulations! Making the decision to follow Jesus is the most important choice you will ever make.\n\n## What Just Happened?\n\nWhen you accepted Christ:\n- Your sins were forgiven\n- You received new spiritual life\n- You became part of Gods family\n- The Holy Spirit came to live in you\n\n## What to Expect\n\nYour new life in Christ is a journey. This course will help you understand:\n- What salvation means\n- How to grow spiritually\n- Why community matters\n- Your purpose in Gods kingdom',
  '{"provider": "youtube", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "duration": 480}'::jsonb,
  true,
  false,
  true,
  8,
  NOW(),
  NOW()
),
(
  'sample-lesson-believers-2'::uuid,
  'Understanding Salvation',
  'What happened when you accepted Christ, and what it means.',
  'sample-course-new-believers'::uuid,
  'sample-section-believers-1'::uuid,
  2,
  'text',
  E'# Understanding Salvation\n\nLets explore what the Bible teaches about salvation.\n\n## The Problem\n\nAll people have sinned and fall short of Gods glory (Romans 3:23). Sin separates us from God.\n\n## The Solution\n\nGod sent His Son Jesus to pay the penalty for our sins. Through faith in Jesus, we receive:\n\n### Justification\nWe are declared righteous before God.\n\n### Forgiveness\nAll our sins - past, present, and future - are forgiven.\n\n### New Life\nWe are spiritually reborn as new creations.\n\n### Eternal Life\nWe have the promise of life forever with God.\n\n## Assurance of Salvation\n\n> "I write these things to you who believe in the name of the Son of God so that you may know that you have eternal life." (1 John 5:13)',
  '{}'::jsonb,
  true,
  false,
  false,
  15,
  NOW(),
  NOW()
),
(
  'sample-lesson-believers-3'::uuid,
  'The Importance of Prayer',
  'How to develop a daily prayer life.',
  'sample-course-new-believers'::uuid,
  'sample-section-believers-2'::uuid,
  3,
  'text',
  E'# The Importance of Prayer\n\nPrayer is simply talking with God. Its how we build our relationship with Him.\n\n## Why Pray?\n\n- God invites us to come to Him\n- Prayer changes us\n- We can bring anything to God\n- Its how we express dependence on Him\n\n## How to Pray\n\nThere is no "right" way to pray, but a simple structure helps:\n\n### ACTS Model\n\n**A** - Adoration (praise God for who He is)\n**C** - Confession (admit your sins)\n**T** - Thanksgiving (thank God for blessings)\n**S** - Supplication (ask for your needs)\n\n## Getting Started\n\n- Set a regular time each day\n- Find a quiet place\n- Start with 5-10 minutes\n- Be honest with God\n- Listen as well as talk',
  '{}'::jsonb,
  true,
  false,
  false,
  12,
  NOW(),
  NOW()
),
(
  'sample-lesson-believers-4'::uuid,
  'Reading Your Bible',
  'Practical tips for studying Scripture.',
  'sample-course-new-believers'::uuid,
  'sample-section-believers-2'::uuid,
  4,
  'text',
  E'# Reading Your Bible\n\nThe Bible is Gods Word to us. Regular Bible reading is essential for spiritual growth.\n\n## Where to Start\n\nFor new believers, we recommend:\n1. **Gospel of John** - Learn about Jesus\n2. **Psalms** - Express emotions to God\n3. **Proverbs** - Gain practical wisdom\n4. **Romans** - Understand theology\n\n## Bible Reading Tips\n\n### Start Small\nBegin with one chapter per day.\n\n### Be Consistent\nSame time, same place helps build habit.\n\n### Ask Questions\n- What does this teach about God?\n- What does this teach about people?\n- Is there a command to obey?\n- Is there a promise to claim?\n\n### Take Notes\nWrite down insights and questions.\n\n## Bible Study Tools\n\n- Study Bible with notes\n- Bible app (YouVersion, Bible Gateway)\n- Commentary for deeper study',
  '{}'::jsonb,
  true,
  false,
  false,
  10,
  NOW(),
  NOW()
),
(
  'sample-lesson-believers-5'::uuid,
  'Final Assessment',
  'Complete this assessment to earn your certificate.',
  'sample-course-new-believers'::uuid,
  'sample-section-believers-3'::uuid,
  5,
  'quiz',
  E'{"questions":[{"id":"sample-final-q1","question":"What happens to our sins when we accept Christ?","type":"multiple_choice","options":["They are counted against us","They are forgiven","They remain until we do good works","They are partially forgiven"],"correct_answer":1,"explanation":"When we accept Christ, all our sins are forgiven (Colossians 1:14)."},{"id":"sample-final-q2","question":"The ACTS prayer model includes Adoration, Confession, Thanksgiving, and what?","type":"multiple_choice","options":["Scripture","Service","Supplication","Silence"],"correct_answer":2,"explanation":"Supplication means asking God for our needs and the needs of others."},{"id":"sample-final-q3","question":"Which book of the Bible is recommended for new believers to start with?","type":"multiple_choice","options":["Leviticus","Revelation","Gospel of John","Numbers"],"correct_answer":2,"explanation":"The Gospel of John is excellent for new believers because it clearly presents who Jesus is."},{"id":"sample-final-q4","question":"Regular Bible reading is essential for spiritual growth.","type":"true_false","correct_answer":true,"explanation":"The Bible teaches that we grow by feeding on Gods Word (1 Peter 2:2)."},{"id":"sample-final-q5","question":"Salvation is a gift from God received by faith.","type":"true_false","correct_answer":true,"explanation":"Ephesians 2:8-9 - For it is by grace you have been saved, through faith."}],"passing_score":70,"time_limit":600,"is_final":true,"allow_certificate":true}',
  '{}'::jsonb,
  true,
  false,
  false,
  10,
  NOW(),
  NOW()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 5. SAMPLE PAGES
-- ============================================================================

INSERT INTO pages (
  id,
  title,
  slug,
  content,
  status,
  created_at,
  updated_at
) VALUES
(
  'sample-page-home'::uuid,
  'Home',
  'home',
  E'<section class="hero">\n  <h1>Welcome to Our Learning Platform</h1>\n  <p>Grow in your faith with our online courses and Bible studies.</p>\n  <a href="/courses" class="button">Browse Courses</a>\n</section>\n\n<section class="featured-courses">\n  <h2>Featured Courses</h2>\n  <p>Start your learning journey with these popular courses.</p>\n</section>\n\n<section class="testimonials">\n  <h2>What Students Are Saying</h2>\n  <div class="testimonial">\n    <blockquote>"This platform has made it so easy to grow in my faith from home."</blockquote>\n    <cite>- Sarah M., Church Member</cite>\n  </div>\n</section>\n\n<section class="cta">\n  <h2>Ready to Start Learning?</h2>\n  <p>Create your free account today.</p>\n  <a href="/register" class="button">Sign Up Free</a>\n</section>',
  'published',
  NOW(),
  NOW()
),
(
  'sample-page-about'::uuid,
  'About',
  'about',
  E'<section class="about-hero">\n  <h1>About Our Learning Platform</h1>\n  <p>Equipping believers for life and ministry through online education.</p>\n</section>\n\n<section class="mission">\n  <h2>Our Mission</h2>\n  <p>We believe that everyone should have access to quality biblical education. Our online learning platform makes it possible for believers around the world to grow in their faith.</p>\n</section>\n\n<section class="values">\n  <h2>What We Believe</h2>\n  <ul>\n    <li><strong>Scripture-Centered:</strong> All our courses are grounded in biblical truth.</li>\n    <li><strong>Accessible:</strong> Learning should be available to everyone, everywhere.</li>\n    <li><strong>Community:</strong> We learn better together.</li>\n    <li><strong>Excellence:</strong> We strive for quality in everything we create.</li>\n  </ul>\n</section>\n\n<section class="contact">\n  <h2>Get in Touch</h2>\n  <p>Have questions? We would love to hear from you.</p>\n  <p>Email: <a href="mailto:info@example.com">info@example.com</a></p>\n</section>',
  'published',
  NOW(),
  NOW()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 6. SAMPLE ENROLLMENTS
-- ============================================================================

INSERT INTO enrollments (
  id,
  user_id,
  course_id,
  progress,
  enrolled_at,
  created_at,
  updated_at
) VALUES
(
  'sample-enrollment-1'::uuid,
  'sample-user-student'::uuid,
  'sample-course-welcome'::uuid,
  50,
  NOW(),
  NOW(),
  NOW()
),
(
  'sample-enrollment-2'::uuid,
  'sample-user-student'::uuid,
  'sample-course-bible-study'::uuid,
  20,
  NOW(),
  NOW(),
  NOW()
),
(
  'sample-enrollment-3'::uuid,
  'sample-user-student'::uuid,
  'sample-course-new-believers'::uuid,
  0,
  NOW(),
  NOW(),
  NOW()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 7. SAMPLE CERTIFICATE TEMPLATE
-- ============================================================================

INSERT INTO certificate_templates (
  id,
  name,
  description,
  template_data,
  is_default,
  created_at,
  updated_at
) VALUES
(
  'sample-certificate-template'::uuid,
  'Sample Certificate Template',
  'A sample certificate template for the New Believers course.',
  '{"title": "Certificate of Completion", "subtitle": "has successfully completed", "background_color": "#ffffff", "border_color": "#c9a227", "text_color": "#333333", "accent_color": "#c9a227", "font_family": "Georgia, serif", "show_date": true, "show_signature": true, "signature_name": "Ministry Director"}'::jsonb,
  false,
  NOW(),
  NOW()
)
ON CONFLICT (id) DO NOTHING;

COMMIT;

-- ============================================================================
-- REMOVAL SCRIPT (Run this to remove all sample content)
-- ============================================================================
--
-- BEGIN;
--
-- -- Delete in order to respect foreign key constraints
-- DELETE FROM lesson_progress WHERE lesson_id IN (SELECT id FROM lessons WHERE id LIKE 'sample-lesson-%');
-- DELETE FROM enrollments WHERE id LIKE 'sample-enrollment-%';
-- DELETE FROM lessons WHERE id LIKE 'sample-lesson-%';
-- DELETE FROM sections WHERE id LIKE 'sample-section-%';
-- DELETE FROM courses WHERE id LIKE 'sample-course-%';
-- DELETE FROM pages WHERE id LIKE 'sample-page-%';
-- DELETE FROM profiles WHERE id LIKE 'sample-user-%';
-- DELETE FROM certificate_templates WHERE id = 'sample-certificate-template';
--
-- COMMIT;
-- ============================================================================
```

---

## 12. MySQL Seed Files

### Main Seed File: `seed_sample_content_mysql.sql`

```sql
-- ============================================================================
-- STARTER CONTENT PACK - MySQL Seed File
-- ============================================================================
-- This file installs sample content for new LMS installations.
-- All content is marked with 'sample-' prefixed IDs for easy removal.
-- ============================================================================
-- Note: MySQL uses CHAR(36) for UUID storage and NOW() for timestamps
-- ============================================================================

START TRANSACTION;

-- ============================================================================
-- 1. SAMPLE USERS (Profiles)
-- ============================================================================

INSERT INTO profiles (
  id,
  name,
  email,
  role,
  avatar_url,
  bio,
  email_verified,
  created_at,
  updated_at
) VALUES
(
  'sample-user-student',
  'Demo Student',
  'student@demo.local',
  'user',
  '/uploads/sample-content/images/avatar-placeholder-student.png',
  'This is a sample student account for testing. You can use this account to see how students experience your courses.',
  1,
  NOW(),
  NOW()
),
(
  'sample-user-instructor',
  'Demo Instructor',
  'instructor@demo.local',
  'instructor',
  '/uploads/sample-content/images/avatar-placeholder-instructor.png',
  'This is a sample instructor account for testing. Log in as this user to see instructor features.',
  1,
  NOW(),
  NOW()
)
ON DUPLICATE KEY UPDATE updated_at = NOW();

-- ============================================================================
-- 2. SAMPLE COURSES
-- ============================================================================

INSERT INTO courses (
  id,
  title,
  slug,
  short_description,
  description,
  level,
  category,
  thumbnail,
  price,
  is_published,
  is_approved,
  is_featured,
  instructor_id,
  created_at,
  updated_at
) VALUES
(
  'sample-course-welcome',
  'Welcome to Your LMS',
  'welcome-to-lms',
  'Learn how to use your new Learning Management System with this step-by-step tutorial.',
  '# Welcome to Your LMS\n\nThis tutorial course will guide you through all the features of your Learning Management System.\n\n## What You Will Learn\n\n- How to navigate the admin dashboard\n- Creating and managing courses\n- Adding lessons with different content types\n- Managing student enrollments\n- Customizing your site',
  'beginner',
  'Tutorial',
  '/uploads/sample-content/images/course-placeholder-tutorial.jpg',
  0.00,
  1,
  1,
  1,
  'sample-user-instructor',
  NOW(),
  NOW()
),
(
  'sample-course-bible-study',
  'Sample Bible Study: The Book of John',
  'sample-bible-study-john',
  'An example Bible study course showing how to structure scripture-based learning.',
  '# Sample Bible Study: The Gospel of John\n\nThis is an example course demonstrating how you might structure a Bible study on your LMS.\n\n## Course Overview\n\nThe Gospel of John presents a unique perspective on the life and ministry of Jesus Christ.',
  'beginner',
  'Bible Study',
  '/uploads/sample-content/images/course-placeholder-bible.jpg',
  0.00,
  1,
  1,
  0,
  'sample-user-instructor',
  NOW(),
  NOW()
),
(
  'sample-course-new-believers',
  'New Believers Foundations',
  'new-believers-foundations',
  'A comprehensive introduction to the Christian faith for new believers. (This is a sample paid course.)',
  '# New Believers Foundations\n\nCongratulations on your decision to follow Christ! This course is designed to help you understand the foundations of the Christian faith.\n\n## Course Certificate\n\nComplete all lessons and pass the final assessment to receive your certificate.',
  'beginner',
  'Discipleship',
  '/uploads/sample-content/images/course-placeholder-faith.jpg',
  29.00,
  1,
  1,
  0,
  'sample-user-instructor',
  NOW(),
  NOW()
)
ON DUPLICATE KEY UPDATE updated_at = NOW();

-- ============================================================================
-- 3. SAMPLE SECTIONS
-- ============================================================================

INSERT INTO sections (
  id,
  title,
  description,
  course_id,
  order_index,
  is_published,
  created_at,
  updated_at
) VALUES
-- Welcome Course Sections
(
  'sample-section-welcome-1',
  'Getting Started',
  'Learn the basics of navigating and using your LMS.',
  'sample-course-welcome',
  1,
  1,
  NOW(),
  NOW()
),
-- Bible Study Sections
(
  'sample-section-bible-1',
  'Introduction to John',
  'Background and context for the Gospel of John.',
  'sample-course-bible-study',
  1,
  1,
  NOW(),
  NOW()
),
(
  'sample-section-bible-2',
  'Key Teachings',
  'Core teachings from the first chapters of John.',
  'sample-course-bible-study',
  2,
  1,
  NOW(),
  NOW()
),
-- New Believers Sections
(
  'sample-section-believers-1',
  'Your New Life',
  'Understanding what happened when you accepted Christ.',
  'sample-course-new-believers',
  1,
  1,
  NOW(),
  NOW()
),
(
  'sample-section-believers-2',
  'Growing in Faith',
  'Practical disciplines for spiritual growth.',
  'sample-course-new-believers',
  2,
  1,
  NOW(),
  NOW()
),
(
  'sample-section-believers-3',
  'Completion',
  'Final assessment and certificate.',
  'sample-course-new-believers',
  3,
  1,
  NOW(),
  NOW()
)
ON DUPLICATE KEY UPDATE updated_at = NOW();

-- ============================================================================
-- 4. SAMPLE LESSONS
-- ============================================================================

INSERT INTO lessons (
  id,
  title,
  description,
  course_id,
  section_id,
  order_index,
  content_type,
  content,
  video,
  is_published,
  is_free,
  is_preview,
  duration,
  created_at,
  updated_at
) VALUES
-- Welcome to LMS Course Lessons
(
  'sample-lesson-welcome-1',
  'Introduction to Your LMS Dashboard',
  'Get oriented with the main dashboard and navigation.',
  'sample-course-welcome',
  'sample-section-welcome-1',
  1,
  'text',
  '# Introduction to Your LMS Dashboard\n\nWelcome! This lesson will help you understand the main areas of your LMS dashboard.\n\n## The Main Menu\n\nOn the left side of your screen, you will find the main navigation menu.',
  '{}',
  1,
  1,
  1,
  5,
  NOW(),
  NOW()
),
(
  'sample-lesson-welcome-2',
  'Creating Your First Course',
  'Step-by-step guide to creating a course from scratch.',
  'sample-course-welcome',
  'sample-section-welcome-1',
  2,
  'video',
  '# Creating Your First Course\n\nWatch this video to learn how to create a course.',
  '{"provider": "youtube", "url": "https://www.youtube.com/watch?v=example", "duration": 480}',
  1,
  1,
  0,
  8,
  NOW(),
  NOW()
),
(
  'sample-lesson-welcome-3',
  'Adding Lessons and Content',
  'How to add different types of content to your lessons.',
  'sample-course-welcome',
  'sample-section-welcome-1',
  3,
  'text',
  '# Adding Lessons and Content\n\nYour LMS supports multiple content types to create engaging lessons.\n\n## Content Types\n\n- Text Lessons\n- Video Lessons\n- Quiz Lessons\n- Assignments',
  '{}',
  1,
  1,
  0,
  10,
  NOW(),
  NOW()
),
(
  'sample-lesson-welcome-4',
  'Managing Students and Enrollments',
  'View enrolled students, track progress, and manage access.',
  'sample-course-welcome',
  'sample-section-welcome-1',
  4,
  'text',
  '# Managing Students and Enrollments\n\nLearn how to view and manage your students.',
  '{}',
  1,
  1,
  0,
  7,
  NOW(),
  NOW()
),
(
  'sample-lesson-welcome-5',
  'Customizing Your Site Appearance',
  'Change colors, logos, and site settings.',
  'sample-course-welcome',
  'sample-section-welcome-1',
  5,
  'text',
  '# Customizing Your Site Appearance\n\nMake your LMS reflect your church or organization brand.',
  '{}',
  1,
  1,
  0,
  5,
  NOW(),
  NOW()
),
(
  'sample-lesson-welcome-6',
  'Setting Up Payments (Optional)',
  'Connect Stripe or PayPal for paid courses.',
  'sample-course-welcome',
  'sample-section-welcome-1',
  6,
  'text',
  '# Setting Up Payments\n\nIf you want to sell courses, you will need to connect a payment processor.',
  '{}',
  1,
  1,
  0,
  8,
  NOW(),
  NOW()
),
-- Bible Study Course Lessons
(
  'sample-lesson-bible-1',
  'Introduction to Johns Gospel',
  'Historical context, authorship, and themes.',
  'sample-course-bible-study',
  'sample-section-bible-1',
  1,
  'text',
  '# Introduction to Johns Gospel\n\nThe Gospel of John is unique among the four Gospels.',
  '{}',
  1,
  1,
  1,
  10,
  NOW(),
  NOW()
),
(
  'sample-lesson-bible-2',
  'John Chapter 1: The Word Made Flesh',
  'Deep dive into the theological prologue.',
  'sample-course-bible-study',
  'sample-section-bible-1',
  2,
  'video',
  '# John Chapter 1: The Word Made Flesh\n\nWatch this video teaching.',
  '{"provider": "youtube", "url": "https://www.youtube.com/watch?v=example", "duration": 900}',
  1,
  1,
  0,
  15,
  NOW(),
  NOW()
),
(
  'sample-lesson-bible-3',
  'John Chapter 3: Born Again',
  'Jesus conversation with Nicodemus.',
  'sample-course-bible-study',
  'sample-section-bible-2',
  3,
  'text',
  '# John Chapter 3: Born Again\n\nNicodemus came to Jesus at night.',
  '{}',
  1,
  1,
  0,
  12,
  NOW(),
  NOW()
),
(
  'sample-lesson-bible-4',
  'Quiz: Test Your Knowledge',
  '5-question quiz on John chapters 1-3.',
  'sample-course-bible-study',
  'sample-section-bible-2',
  4,
  'quiz',
  '{"questions":[{"id":"q1","question":"What was in the beginning?","type":"multiple_choice","options":["The World","The Word","The Light","The Law"],"correct_answer":1}],"passing_score":70,"time_limit":300}',
  '{}',
  1,
  1,
  0,
  5,
  NOW(),
  NOW()
),
(
  'sample-lesson-bible-5',
  'Discussion: Reflection Questions',
  'Journal prompts and discussion questions.',
  'sample-course-bible-study',
  'sample-section-bible-2',
  5,
  'text',
  '# Discussion: Reflection Questions\n\nTake time to reflect on what you have learned.',
  '{}',
  1,
  1,
  0,
  10,
  NOW(),
  NOW()
),
-- New Believers Course Lessons
(
  'sample-lesson-believers-1',
  'Welcome to Your New Life in Christ',
  'Congratulations on your decision!',
  'sample-course-new-believers',
  'sample-section-believers-1',
  1,
  'video',
  '# Welcome to Your New Life in Christ\n\nCongratulations!',
  '{"provider": "youtube", "url": "https://www.youtube.com/watch?v=example", "duration": 480}',
  1,
  0,
  1,
  8,
  NOW(),
  NOW()
),
(
  'sample-lesson-believers-2',
  'Understanding Salvation',
  'What happened when you accepted Christ.',
  'sample-course-new-believers',
  'sample-section-believers-1',
  2,
  'text',
  '# Understanding Salvation\n\nLets explore what the Bible teaches.',
  '{}',
  1,
  0,
  0,
  15,
  NOW(),
  NOW()
),
(
  'sample-lesson-believers-3',
  'The Importance of Prayer',
  'How to develop a daily prayer life.',
  'sample-course-new-believers',
  'sample-section-believers-2',
  3,
  'text',
  '# The Importance of Prayer\n\nPrayer is talking with God.',
  '{}',
  1,
  0,
  0,
  12,
  NOW(),
  NOW()
),
(
  'sample-lesson-believers-4',
  'Reading Your Bible',
  'Practical tips for studying Scripture.',
  'sample-course-new-believers',
  'sample-section-believers-2',
  4,
  'text',
  '# Reading Your Bible\n\nThe Bible is Gods Word to us.',
  '{}',
  1,
  0,
  0,
  10,
  NOW(),
  NOW()
),
(
  'sample-lesson-believers-5',
  'Final Assessment',
  'Complete to earn your certificate.',
  'sample-course-new-believers',
  'sample-section-believers-3',
  5,
  'quiz',
  '{"questions":[{"id":"fq1","question":"What happens to our sins when we accept Christ?","type":"multiple_choice","options":["Counted against us","Forgiven","Remain","Partial"],"correct_answer":1}],"passing_score":70,"time_limit":600,"is_final":true,"allow_certificate":true}',
  '{}',
  1,
  0,
  0,
  10,
  NOW(),
  NOW()
)
ON DUPLICATE KEY UPDATE updated_at = NOW();

-- ============================================================================
-- 5. SAMPLE PAGES
-- ============================================================================

INSERT INTO pages (
  id,
  title,
  slug,
  content,
  status,
  created_at,
  updated_at
) VALUES
(
  'sample-page-home',
  'Home',
  'home',
  '<section class="hero"><h1>Welcome to Our Learning Platform</h1><p>Grow in your faith with our online courses.</p></section>',
  'published',
  NOW(),
  NOW()
),
(
  'sample-page-about',
  'About',
  'about',
  '<section class="about"><h1>About Us</h1><p>We are dedicated to equipping believers through education.</p></section>',
  'published',
  NOW(),
  NOW()
)
ON DUPLICATE KEY UPDATE updated_at = NOW();

-- ============================================================================
-- 6. SAMPLE ENROLLMENTS
-- ============================================================================

INSERT INTO enrollments (
  id,
  user_id,
  course_id,
  progress,
  enrolled_at,
  created_at,
  updated_at
) VALUES
(
  'sample-enrollment-1',
  'sample-user-student',
  'sample-course-welcome',
  50,
  NOW(),
  NOW(),
  NOW()
),
(
  'sample-enrollment-2',
  'sample-user-student',
  'sample-course-bible-study',
  20,
  NOW(),
  NOW(),
  NOW()
),
(
  'sample-enrollment-3',
  'sample-user-student',
  'sample-course-new-believers',
  0,
  NOW(),
  NOW(),
  NOW()
)
ON DUPLICATE KEY UPDATE updated_at = NOW();

COMMIT;

-- ============================================================================
-- REMOVAL SCRIPT (Run this to remove all sample content)
-- ============================================================================
--
-- START TRANSACTION;
--
-- DELETE FROM lesson_progress WHERE lesson_id LIKE 'sample-lesson-%';
-- DELETE FROM enrollments WHERE id LIKE 'sample-enrollment-%';
-- DELETE FROM lessons WHERE id LIKE 'sample-lesson-%';
-- DELETE FROM sections WHERE id LIKE 'sample-section-%';
-- DELETE FROM courses WHERE id LIKE 'sample-course-%';
-- DELETE FROM pages WHERE id LIKE 'sample-page-%';
-- DELETE FROM profiles WHERE id LIKE 'sample-user-%';
--
-- COMMIT;
-- ============================================================================
```

---

## Summary

The Starter Content Pack provides:

1. **3 Sample Courses** demonstrating different use cases (tutorial, Bible study, paid course)
2. **15+ Sample Lessons** with various content types (text, video, quiz)
3. **2 Demo Users** for testing student and instructor experiences
4. **2 Sample Pages** with homepage and about page templates
5. **6 Media Assets** for course thumbnails and avatars
6. **Complete Removal System** for easy cleanup when ready to go live
7. **Installer Integration** with user-friendly installation wizard
8. **Database Seeds** for both PostgreSQL and MySQL

All content is clearly marked with `sample-` prefixed IDs and metadata flags, making it easy to identify and remove when the administrator is ready to launch their own content.
