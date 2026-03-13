---
name: settings-gui-generator
category: automation
version: 1.0.0
contributed: 2026-02-24
contributor: voice-bridge-v4
last_updated: 2026-02-24
contributors:
  - voice-bridge-v4
tags: [pyqt6, python, settings, config, code-generation, yaml, dark-theme, gui]
difficulty: medium
usage_count: 0
success_rate: 100
---

# Settings GUI Generator (Config-to-Dialog Pattern)

## Problem

Every Python desktop app with a YAML/JSON/TOML config file eventually needs a settings dialog. The typical anti-pattern:
- `os.startfile(config_path)` opens raw YAML in Notepad
- Users break YAML indentation
- No discoverability — users can't see what options exist
- No validation — invalid values crash at runtime
- No live reload — changes require full restart

Building a settings dialog from scratch takes 30-60 minutes and commonly hits the **cross-thread bug** when called from pystray callbacks.

## Solution Pattern

Map config structure to PyQt6 widgets automatically:

| Config Type | Widget | Example |
|-------------|--------|---------|
| `boolean` | QCheckBox | `enabled: true` → ☑ Enabled |
| `string` (enum) | QComboBox | `backend: "piper"` → dropdown [piper, edge] |
| `number` | QSpinBox / QSlider | `speed: 1.0` → slider 0.5-2.0 |
| `string` (free) | QLineEdit | `voice: "en_US-lessac"` → text input |
| Nested dict with `enabled` | QCheckBox in QGroupBox | Feature group toggle |

### Thread-Safety Pattern (CRITICAL)

System tray callbacks (pystray) run on a background thread. Qt widgets MUST be created on the Qt GUI thread. The dialog will RENDER but be UNCLICKABLE if created from the wrong thread.

**Solution:** Signal marshaling:

```python
# In overlay/main window:
sig_open_settings = pyqtSignal()  # Thread-safe bridge

# Tray callback (WRONG thread):
def _open_settings(self):
    self.overlay.sig_open_settings.emit()  # Just emit signal

# Qt slot (RIGHT thread, auto-marshaled):
def _on_open_settings(self):
    from .settings_dialog import SettingsDialog
    dialog = SettingsDialog(self)
    dialog.settings_changed.connect(self._on_settings_changed)
    dialog.exec()
```

## Code Example

```python
# Before (problematic) — opens raw YAML in Notepad
def _open_settings(self) -> None:
    os.startfile(str(CONFIG_FILE))

# After (solution) — proper settings GUI with live reload
class SettingsDialog(QDialog):
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = load_config()
        self._widgets = {}  # config_path → widget mapping
        self._build_ui()

    def _build_ui(self):
        features = [
            ("post_processing.hallucination_filter", "Hallucination Filter",
             "Reject garbage like 'thank you for watching'"),
            ("post_processing.filler_removal", "Filler Removal",
             "Strip um, uh, like, basically"),
        ]
        for path, label, desc in features:
            cb = QCheckBox(f"{label}\n{desc}")
            value = self._get_nested(self.config, path)
            cb.setChecked(value.get("enabled", False))
            self._widgets[path] = cb

    def _save(self):
        config = load_config()  # Fresh read!
        for path, widget in self._widgets.items():
            self._set_nested(config, path, "enabled", widget.isChecked())
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
QCheckBox::indicator:checked {
    background-color: #6366f1; border-color: #6366f1;
}
QPushButton {
    background-color: #6366f1; color: white;
    border-radius: 6px; padding: 8px 24px;
}
"""
```

### Live Reload Pattern

```python
def _on_settings_changed(self, new_config: dict):
    self.text_processor = TextProcessor(new_config)  # Recreate from config
    # No restart needed — next call uses new settings
```

## Implementation Steps

1. Create `settings_dialog.py` alongside your main module
2. Define feature list as `(config_path, label, description)` tuples
3. Map each config type to appropriate Qt widget
4. Build UI with QGroupBox sections for logical grouping
5. Wire save button: load_config() fresh → apply widget states → save_config()
6. Emit `settings_changed` signal with full config dict
7. In main app: connect signal via Qt signal (NOT direct call from tray)
8. Add fallback to `os.startfile()` if dialog import fails

## When to Use

- Any Python desktop app with a YAML/JSON/TOML config file
- When "Settings" currently opens the raw config in a text editor
- When features are togglable and users shouldn't understand config syntax
- When you want live reload without full app restart

## When NOT to Use

- Web apps (use a proper web settings page)
- CLI-only tools (use command-line flags)
- When config has only 1-2 simple values (overkill)
- When config changes ALWAYS require restart (signal adds complexity)

## Common Mistakes

- **Cross-thread dialog creation** — The #1 bug. ALWAYS use signal marshaling from tray callbacks. The dialog renders but is unclickable without it.
- **Reading stale config in `_save()`** — Always `load_config()` fresh before applying widget states
- **Not handling nested dicts** — Config like `{post_processing: {filter: {enabled: true}}}` needs recursive navigation
- **Missing deep_merge for defaults** — If config file doesn't have new feature sections, `deep_merge(DEFAULT_CONFIG, loaded)` ensures they appear
- **Not writing defaults to disk** — After adding new features, call `load_config()` then `save_config()` to persist the merged defaults

## Related Skills

- [pyqt6-settings-dialog](../frontend/pyqt6-settings-dialog.md) — The pattern this generates
- [togglable-processing-pipeline](../patterns-standards/togglable-processing-pipeline.md) — Config-driven feature ordering

## References

- Contributed from: voice-bridge-v4
- Real implementation: `voice-bridge-v3/src/voice_bridge_v3/settings_dialog.py`
- PyQt6 QDialog docs: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QDialog.html
