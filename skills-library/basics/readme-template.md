# Skill: README Template

**Category:** Basics
**Difficulty:** Beginner
**Applies to:** Every project

---

## The Problem

A project without a README is a project no one can use — including future you. A good README answers three questions in under 60 seconds: What is this? How do I install it? How do I use it?

---

## The Template

Copy this and fill it in:

```markdown
# Project Name

One sentence describing what this project does and who it is for.

## Features

- Feature one — what it does for the user
- Feature two
- Feature three

## Requirements

- Node.js 18+ (or Python 3.10+, etc.)
- PostgreSQL 14+
- An account at [ServiceName](https://example.com) (if needed)

## Installation

1. Clone the repo:
   git clone https://github.com/your-username/your-project.git
   cd your-project

2. Install dependencies:
   npm install

3. Set up environment variables:
   cp .env.example .env
   # Edit .env with your values

4. Set up the database:
   npm run db:migrate

5. Start the app:
   npm run dev

The app will be running at http://localhost:3000

## Usage

Describe the main thing a user does here. Include a screenshot if you can.

### Example

Show a code snippet or command that demonstrates the core feature:
   curl http://localhost:3000/api/health
   # Returns: {"status": "ok"}

## Project Structure

   src/
   ├── routes/       # API endpoints
   ├── models/       # Database models
   ├── middleware/   # Auth, validation
   └── utils/        # Helper functions

## Running Tests

   npm test

## Deployment

Brief notes on how to deploy (or link to a separate DEPLOYMENT.md).

## License

MIT License — see LICENSE file for details.
```

---

## What Makes a README Great

| Include | Skip |
|---------|------|
| Install steps that actually work | Your development diary |
| What the project does in one sentence | Every minor feature listed |
| A working example or screenshot | Apologies for bad code |
| How to run tests | Future plans (put those in Issues) |
| License | Obvious things ("this is a web app") |

---

## Quick Test

After writing your README, ask someone who has never seen your project to install it using only the README. Every place they get stuck is a gap to fix.

---

*Fire Flow Skills Library — MIT License*
