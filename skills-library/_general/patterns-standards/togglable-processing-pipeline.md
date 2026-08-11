---
name: togglable-processing-pipeline
category: patterns-standards
version: 1.0.0
contributed: 2026-02-24
contributor: voice-bridge-v4
last_updated: 2026-02-24
contributors:
  - voice-bridge-v4
tags: [pipeline, config, text-processing, audio, post-processing, fail-fast]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Togglable Processing Pipeline (Config-Driven Feature Ordering)

## Problem

Processing pipelines (text cleanup, audio post-processing, data transformation) often have multiple independent features that should each be toggleable. Common anti-patterns:

- Features hard-coded as if/else blocks that can't be disabled
- All features run regardless of whether the input needs them
- Expensive operations (API calls) run before cheap filters, wasting resources
- No config file support — toggling requires code changes
- Adding a new feature means modifying the pipeline method

## Solution Pattern

Build a **config-driven pipeline** where:

1. Each feature is independently togglable via config (`enabled: true/false`)
2. Features run in a **fail-fast order** — cheapest filters first, expensive operations last
3. A rejected input (e.g., hallucination) short-circuits the entire pipeline returning `None`
4. New features slot into the pipeline at the correct cost position
5. The processor is **stateless per call** — can be recreated from config for live reload

### Pipeline Ordering Principle

```
Cost:   $0          $0          $0          $0         $$$
        ──────────────────────────────────────────────────►
        Hallucination  Dictionary   Fillers    Numbers   AI Cleanup
        Filter         Replace      Remove     Convert   (API call)
        (reject bad)   (regex)      (regex)    (lookup)  (expensive!)
```

Reject garbage first. Don't spend API credits cleaning up "thank you for watching."

## Code Example

```python
# Before (problematic) — monolithic, no toggles, wrong order
def process(text):
    text = call_ai_cleanup(text)  # Expensive! Runs on garbage too
    text = text.replace("um", "").replace("uh", "")
    if text in BAD_PHRASES:
        return None  # Too late — already spent API credits
    return text

# After (solution) — config-driven, ordered, togglable
class TextProcessor:
    def __init__(self, config: dict):
        self.cfg = config.get("post_processing", {})

    def process(self, text: str) -> str | None:
        # Stage 1: Reject (cheapest — regex/set lookup)
        if self.cfg.get("hallucination_filter", {}).get("enabled"):
            if self._is_hallucination(text):
                return None  # Short-circuit: saves all downstream cost

        # Stage 2: Transform (cheap — regex replacement)
        if self.cfg.get("custom_dictionary", {}).get("enabled"):
            text = self._apply_dictionary(text)

        if self.cfg.get("filler_removal", {}).get("enabled"):
            text = self._remove_fillers(text)

        # Stage 3: Convert (moderate — lookup table)
        if self.cfg.get("number_conversion", {}).get("enabled"):
            text = self._convert_numbers(text)

        # Stage 4: AI cleanup (expensive — API call, LAST)
        if self.cfg.get("ai_post_processing", {}).get("enabled"):
            text = self._ai_process(text)

        # Stage 5: Log (side effect — always last)
        if self.cfg.get("transcription_history", {}).get("enabled"):
            self._log_history(text)

        return text
```

### Config Structure

```yaml
post_processing:
  hallucination_filter:
    enabled: true
    patterns: ["thank you for watching", "please subscribe"]
  custom_dictionary:
    enabled: false
    replacements: { "claude": "Claude", "jarvis": "Jarvis" }
  filler_removal:
    enabled: false
    words: ["um", "uh", "like", "basically"]
  number_conversion:
    enabled: false
  ai_post_processing:
    enabled: false
    template: "Clean up: {text}"
    model: "claude-haiku-4-5-20251001"
  transcription_history:
    enabled: true
    max_entries: 10000
```

### Live Reload Pattern

```python
# When settings change, recreate the processor
def _on_settings_changed(self, new_config: dict):
    self.text_processor = TextProcessor(new_config)
    # No restart needed — next call uses new config
```

## Implementation Steps

1. Define pipeline stages in cost order (cheapest → most expensive)
2. Create config structure with `enabled` toggle per feature
3. Build processor class that reads config in `__init__`
4. Pipeline method checks `enabled` before each stage
5. First stage should be a **reject filter** that returns `None` to short-circuit
6. Last stage should be **logging/side effects**
7. Support live reload by recreating processor from new config

## When to Use

- Text post-processing (transcription cleanup, NLP pipelines)
- Audio processing chains (noise reduction, normalization, effects)
- Data validation pipelines (format, clean, validate, enrich)
- Image processing (resize, crop, filter, watermark, compress)
- Any multi-step processing where features should be independently toggleable

## When NOT to Use

- When features have complex interdependencies (use a DAG instead)
- When order doesn't matter (use a simple feature flag set)
- When there's only one processing step (overkill)
- Real-time streaming where you can't buffer (need async pipeline)

## Common Mistakes

- **Wrong order** — Running expensive AI cleanup before cheap hallucination filter wastes money
- **Not short-circuiting** — A rejected input should `return None` immediately, not continue through remaining stages
- **Mutable state between calls** — Each `process()` call should be independent. Don't accumulate state across calls unless explicitly designed (like history logging)
- **Lazy init without cleanup** — If a stage lazily initializes resources (DB connections, API clients), implement `shutdown()` for clean teardown
- **Forgetting the config merge** — If config file doesn't have the new feature section, `deep_merge` with defaults ensures it still works

## Related Skills

- [pyqt6-settings-dialog](../frontend/pyqt6-settings-dialog.md) — GUI for toggling features
- [fail-fast-validation](../patterns-standards/fail-fast-validation.md) — General fail-fast patterns

## References

- Contributed from: voice-bridge-v4
- Pipeline pattern: https://refactoring.guru/design-patterns/chain-of-responsibility
- Real implementation: `voice-bridge-v3/src/voice_bridge_v3/text_processor.py`
