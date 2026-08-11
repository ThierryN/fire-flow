# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Claude Code skill for generating Excalidraw diagrams programmatically. It provides Python classes (`Diagram`, `Flowchart`, `ArchitectureDiagram`) that output `.excalidraw` JSON files.

## Commands

**Run unit tests:**
```bash
python tests/test_generator.py
```

**Run API integration test (requires ANTHROPIC_API_KEY):**
```bash
ANTHROPIC_API_KEY=sk-... python tests/test_api_skill.py
```

**Generate example diagram:**
```bash
python scripts/excalidraw_generator.py
```

**Create capability zip for Claude.ai web:**
```bash
python scripts/create_capability_zip.py
```

## Architecture

- `SKILL.md` - Skill definition with frontmatter (name, description) and usage documentation for Claude Code
- `scripts/excalidraw_generator.py` - Core Python library with:
  - Low-level element functions: `rectangle()`, `ellipse()`, `diamond()`, `text()`, `arrow()`, `line()`
  - `Diagram` class - Base class for creating diagrams with `box()`, `text_box()`, `arrow_between()`, `line_between()`
  - `Flowchart(Diagram)` - Auto-positioning flowcharts with `start()`, `end()`, `process()`, `decision()`, `connect()`
  - `ArchitectureDiagram(Diagram)` - System architecture with `component()`, `database()`, `service()`, `user()`, `connect()`
- `scripts/create_capability_zip.py` - Packages skill for Claude.ai web upload
- `tests/test_generator.py` - Unit tests for all diagram classes
- `tests/test_api_skill.py` - Integration test using Claude API Skills endpoint

## CI Workflow

The CI workflow (`ci.yml`) runs:
1. Unit tests across Python 3.9-3.12
2. SKILL.md frontmatter validation (must have `name` and `description` fields)
3. Integration test with Claude Code (uses `robtaylor/claude-code-action`)

## Key Implementation Details

- No external dependencies - uses only Python standard library
- Element IDs generated via truncated UUID4
- Each element has a random seed for roughjs hand-drawn rendering
- The `Element` dataclass wraps shape data with position/dimension helpers for arrow calculations
- Arrow connection points auto-detect optimal sides based on relative element positions
- Text elements bound to shapes use `containerId`/`boundElements` linking
