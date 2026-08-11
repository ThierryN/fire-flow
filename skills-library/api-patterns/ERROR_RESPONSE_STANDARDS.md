---
name: error-response-standards
category: api-patterns
version: 1.0.0
contributed: 2026-02-24
contributor: dominion-flow
tags: [errors, api, rest, error-handling, http-status, responses]
difficulty: easy
---

# Error Response Standards

## Problem

Inconsistent error responses across routes make frontend error handling a nightmare. Some routes return `{ message }`, others `{ error }`, others `{ errors: [] }`. Status codes are used incorrectly (everything is 500 or 200).

## Solution Pattern

One error format for the entire API. Correct HTTP status codes. Machine-readable error codes alongside human-readable messages.

## Standard Error Envelope

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Course title is required",
    "details": [
      { "field": "title", "message": "Required field", "code": "REQUIRED" },
      { "field": "duration", "message": "Must be positive", "code": "INVALID_RANGE" }
    ]
  }
}
```

**Three levels:**
1. `code` — Machine-readable, never changes (clients switch on this)
2. `message` — Human-readable, may change (display to users)
3. `details` — Optional array for field-level errors (forms)

## HTTP Status Code Guide

| Code | When | Example |
|------|------|---------|
| 400 | Client sent bad data | Missing required field, invalid format |
| 401 | Not authenticated | No token, expired token |
| 403 | Authenticated but forbidden | Student accessing admin route |
| 404 | Resource doesn't exist | Course ID not found |
| 409 | Conflict | Duplicate email, already enrolled |
| 422 | Semantically invalid | Valid JSON but business rule violation |
| 429 | Rate limited | Too many requests |
| 500 | Server bug | Unhandled exception, DB down |

**Rules:**
- **Never return 200 with an error body.** Use proper status codes.
- **Never return 500 for client errors.** 4xx means "your fault," 5xx means "our fault."
- **Always return JSON**, even for 404/500 (not HTML error pages).

## Error Middleware (Express)

```javascript
// middleware/errorHandler.js
function errorHandler(err, req, res, next) {
  // Known operational error
  if (err.isOperational) {
    return res.status(err.statusCode).json({
      error: {
        code: err.code,
        message: err.message,
        details: err.details || undefined,
      }
    })
  }

  // Unknown bug — log full error, return generic message
  console.error('Unhandled error:', err)
  res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: 'Something went wrong',
    }
  })
}

// Custom error class
class AppError extends Error {
  constructor(statusCode, code, message, details) {
    super(message)
    this.statusCode = statusCode
    this.code = code
    this.details = details
    this.isOperational = true
  }
}

module.exports = { errorHandler, AppError }
```

## Usage in Routes

```javascript
const { AppError } = require('../middleware/errorHandler')

router.post('/courses', async (req, res, next) => {
  try {
    if (!req.body.title) {
      throw new AppError(400, 'VALIDATION_FAILED', 'Title is required', [
        { field: 'title', message: 'Required field', code: 'REQUIRED' }
      ])
    }

    const existing = await db.findByTitle(req.body.title)
    if (existing) {
      throw new AppError(409, 'DUPLICATE_RESOURCE', 'A course with this title already exists')
    }

    const course = await db.createCourse(req.body)
    res.status(201).json({ data: course })
  } catch (err) {
    next(err)
  }
})
```

## Standard Error Codes

| Code | Status | Meaning |
|------|--------|---------|
| `VALIDATION_FAILED` | 400 | Input didn't pass validation |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `DUPLICATE_RESOURCE` | 409 | Already exists |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server-side bug |

## When to Use

- Every API project, from day one
- Use the error middleware as the first middleware you write

## When NOT to Use

- GraphQL APIs (use GraphQL's built-in error format instead)
- gRPC (use status codes from grpc-status)
