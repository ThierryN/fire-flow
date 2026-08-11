---
name: pyqt6-settings-dialog
category: frontend
version: 1.0.0
contributed: 2026-02-24
contributor: voice-bridge-v4
last_updated: 2026-02-24
contributors:
  - voice-bridge-v4
tags: [pyqt6, python, desktop-app, settings, gui, yaml, config, dark-theme]
difficulty: medium
usage_count: 0
success_rate: 100
---

# PyQt6 Settings Dialog (Replace Raw Config Editing)

## Problem

Python desktop apps store configuration in YAML/JSON/TOML files. The typical "Settings" menu item calls `os.startfile(config_path)` which opens the raw file in Notepad. This creates multiple problems:

- Users must hand-edit YAML syntax (easy to break indentation)
- No discoverability — users can't see what options exist
- No validation — invalid values only crash at runtime
- No live reload — changes require full app restart
- No descriptions — feature names like `hallucination_filter` are cryptic

## Solution Pattern

Build a PyQt6 QDialog that:

1. **Reads config** using your existing `load_config()` function
2. **Renders toggles/combos** programmatically from config keys
3. **Saves on OK** using your existing `save_config()` function
4. **Emits a signal** so the main app can hot-reload affected components
5. **Matches app theme** using a stylesheet (dark theme shown below)

Key architecture decisions:
- Dialog is **modal** (blocks interaction with main window) — prevents race conditions
- Config paths stored as dotted strings (`"post_processing.hallucination_filter"`) for clean mapping
- `settings_changed` signal carries the full new config dict — caller decides what to hot-reload
- Fallback to raw file editor if dialog fails to import (graceful degradation)

## Code Example

```python
# Before (problematic) — opens raw YAML in Notepad
def _open_settings(self) -> None:
    os.startfile(str(CONFIG_FILE))

# After (solution) — proper settings GUI with live reload
def _open_settings(self) -> None:
    from .settings_dialog import SettingsDialog
    dialog = SettingsDialog(parent=self.main_window)
    dialog.settings_changed.connect(self._on_settings_changed)
    dialog.exec()

def _on_settings_changed(self, new_config: dict) -> None:
    # Hot-reload only the components that support it
    self.text_processor = TextProcessor(new_config)
    self.status_server.update(new_config)
```

### Settings Dialog Structure

```python
from PyQt6.QtWidgets import QDialog, QCheckBox, QGroupBox, QComboBox, QDialogButtonBox
from PyQt6.QtCore import pyqtSignal
from .config import load_config, save_config

class SettingsDialog(QDialog):
    settings_changed = pyqtSignal(dict)  # Emitted on save

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = load_config()
        self._checkboxes = {}  # path -> QCheckBox mapping
        self._build_ui()

    def _build_ui(self):
        # Group features logically
        features = [
            ("post_processing.hallucination_filter", "Hallucination Filter",
             "Reject garbage like 'thank you for watching'"),
            ("post_processing.filler_removal", "Filler Removal",
             "Strip um, uh, like, basically"),
            # ... more features
        ]

        for path, label, description in features:
            cb = QCheckBox(label)
            # Navigate nested config: "post_processing.hallucination_filter"
            parts = path.split(".")
            value = self.config
            for part in parts:
                value = value.get(part, {})
            cb.setChecked(value.get("enabled", False))
            self._checkboxes[path] = cb

        # Save/Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)

    def _save(self):
        config = load_config()  # Fresh read to avoid stale state
        for path, cb in self._checkboxes.items():
            parts = path.split(".")
            target = config
            for part in parts[:-1]:
                target = target.setdefault(part, {})
            last_key = parts[-1]
            if isinstance(target.get(last_key), dict):
                target[last_key]["enabled"] = cb.isChecked()
            else:
                target[last_key] = cb.isChecked()

        save_config(config)
        self.settings_changed.emit(config)
        self.accept()
```

### Dark Theme Stylesheet

```python
STYLESHEET = """
QDialog { background-color: #0f0f14; color: #f0f0f5; }
QGroupBox {
    background-color: #1a1a24; border: 1px solid #2a2a3a;
    border-radius: 8px; margin-top: 12px; padding: 16px;
}
QGroupBox::title { color: #6366f1; }
QCheckBox::indicator {
    width: 20px; height: 20px;
    border: 2px solid #2a2a3a; border-radius: 4px;
}
QCheckBox::indicator:checked {
    background-color: #6366f1; border-color: #6366f1;
}
QDialogButtonBox QPushButton {
    background-color: #6366f1; color: white;
    border-radius: 6px; padding: 8px 24px;
}
"""
```

## Implementation Steps

1. Create `settings_dialog.py` alongside your main module
2. Define feature list as `(config_path, label, description)` tuples
3. Build UI with QGroupBox sections for logical grouping
4. Map checkboxes to dotted config paths in `self._checkboxes`
5. On save: navigate config dict, update values, call `save_config()`
6. Emit `settings_changed` signal with full config
7. In main app: connect signal to hot-reload handler
8. Add fallback to `os.startfile()` if dialog import fails

## When to Use

- Any Python desktop app with a YAML/JSON/TOML config file
- When "Settings" currently opens the raw config in a text editor
- When features are togglable and users shouldn't need to understand config syntax
- When you want live reload without full app restart

## When NOT to Use

- Web apps (use a proper web settings page instead)
- CLI-only tools (use command-line flags or interactive prompts)
- When config has only 1-2 simple values (overkill — just use CLI args)
- When config changes ALWAYS require restart (signal adds unnecessary complexity)

## Common Mistakes

- **Reading stale config in `_save()`** — Always `load_config()` fresh before applying checkbox states, because another process or the user might have edited the file
- **Not handling nested dicts** — Config like `{post_processing: {filter: {enabled: true}}}` needs the `isinstance(target.get(last_key), dict)` check to set `.enabled` inside the nested dict rather than replacing it
- **Opening dialog from wrong thread** — If called from a system tray callback (different thread), use Qt signals to marshal to the GUI thread
- **Not providing fallback** — Wrap dialog creation in try/except and fall back to `os.startfile()` for robustness

## Related Skills

- [config-hot-reload](../patterns-standards/config-hot-reload.md) — General pattern for live config reload
- [dark-theme-qt](../frontend/dark-theme-qt.md) — Dark theme patterns for PyQt6

## References

- Contributed from: voice-bridge-v4
- PyQt6 QDialog docs: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QDialog.html
- Real implementation: `voice-bridge-v3/src/voice_bridge_v3/settings_dialog.py`
