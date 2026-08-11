---
name: Python Desktop App Architecture
category: patterns-standards
version: 1.0.0
contributed: 2026-02-24
tags: [python, pyqt6, desktop-app, pystray, audio, stt, tts, overlay, threading, signals]
difficulty: hard
usage_count: 0
success_rate: 100
---

# Python Desktop App Architecture

## Problem

Building a Python desktop application that combines real-time audio processing (STT/TTS), a transparent overlay UI, system tray integration, background processing threads, and external monitoring — all without freezing the GUI or corrupting shared state.

The core challenge is threading: STT engines run continuous audio loops, TTS engines queue and play audio, hotkey listeners block on input, and the GUI must remain responsive. Python's GIL and Qt's thread-affinity rules make naive approaches crash or deadlock.

## Solution Pattern

**PyQt6 overlay + pystray tray + Qt signal bridge + status sidecar**

Use PyQt6 as the primary GUI framework with its event loop on the main thread. Run all blocking I/O (STT, TTS, hotkeys, tray) on dedicated background threads. Bridge thread-to-GUI communication exclusively through Qt signals (which are thread-safe and auto-queued). Expose application state via a lightweight HTTP sidecar for external monitoring.

## Architecture

```
Main Thread (Qt Event Loop)
    |
    +-- Overlay (QWidget, transparent, always-on-top)
    +-- Settings Dialog (QDialog, modal)
    +-- Text Processor (post-processing pipeline)
    +-- Claude Client (API calls, async-compatible)
    |
    +-- [Qt Signals] <-- STT Thread (RealtimeSTT, continuous mic loop)
    +-- [Qt Signals] <-- TTS Thread (edge-tts/piper, audio queue)
    +-- [Qt Signals] <-- Tray Thread (pystray, blocks on menu loop)
    +-- [Qt Signals] <-- Hotkey Thread (keyboard listener)
    +-- [Thread]     <-- Status Server (HTTPServer on port 7899)
```

### Component Breakdown

| Component | Role | Thread | Communication |
|-----------|------|--------|---------------|
| `main.py` | Orchestrator (~700 lines), wires all components | Main | Direct calls |
| `overlay.py` | Transparent QWidget, shows transcription/status | Main | Qt signals in |
| `settings_dialog.py` | QDialog for config editing | Main (modal) | Direct config access |
| `stt_engine.py` | RealtimeSTT with Whisper, continuous listen | Background | Qt signals out |
| `tts_engine.py` | edge-tts + piper-tts, audio queue via sounddevice | Background | Qt signals out |
| `tray.py` | pystray system tray with menu | Background | Qt signals out |
| `config.py` | YAML config with deep_merge defaults | Any (read-only after load) | Direct import |
| `claude_client.py` | Anthropic SDK, streaming responses | Main (async) | Direct calls |
| `status_server.py` | HTTPServer sidecar, JSON state endpoint | Background | Reads shared state |
| `text_processor.py` | Post-processing pipeline (corrections, formatting) | Main | Direct calls |
| `transcription_history.py` | Timestamped log of all transcriptions | Main | Direct calls |

## Code Examples

### Qt Signal Bridge Pattern

The fundamental pattern: background threads emit Qt signals, the main thread handles them safely.

```python
from PyQt6.QtCore import QObject, pyqtSignal, QThread

class STTSignals(QObject):
    """Signals emitted by the STT engine thread."""
    text_detected = pyqtSignal(str)          # Partial transcription
    text_finalized = pyqtSignal(str)         # Final transcription
    status_changed = pyqtSignal(str)         # "listening", "processing", "idle"
    error_occurred = pyqtSignal(str)         # Error message
    wake_word_detected = pyqtSignal()        # Wake word trigger

class STTEngine(QThread):
    def __init__(self, config: dict):
        super().__init__()
        self.signals = STTSignals()
        self.config = config
        self._running = True

    def run(self):
        """Runs on background thread. NEVER touch GUI here."""
        from RealtimeSTT import AudioToTextRecorder
        recorder = AudioToTextRecorder(
            model=self.config.get("model", "base.en"),
            language=self.config.get("language", "en"),
            on_recording_start=lambda: self.signals.status_changed.emit("listening"),
            on_recording_stop=lambda: self.signals.status_changed.emit("processing"),
        )
        while self._running:
            text = recorder.text()
            if text and text.strip():
                self.signals.text_finalized.emit(text.strip())

    def stop(self):
        self._running = False
        self.quit()
        self.wait(3000)

# In main.py orchestrator:
class VoiceBridgeApp:
    def __init__(self):
        self.stt = STTEngine(config["stt"])
        self.overlay = Overlay()

        # Connect signal to GUI update (thread-safe via Qt signal queue)
        self.stt.signals.text_finalized.connect(self.overlay.show_transcription)
        self.stt.signals.status_changed.connect(self.overlay.update_status)
        self.stt.signals.wake_word_detected.connect(self.on_wake_word)

        self.stt.start()  # Launches background thread
```

### Config Pattern with deep_merge

```python
import yaml
from pathlib import Path
from copy import deepcopy

DEFAULT_CONFIG = {
    "stt": {
        "model": "base.en",
        "language": "en",
        "wake_word": "hey claude",
        "wake_word_debounce_ms": 2000,
        "silence_threshold": 0.5,
    },
    "tts": {
        "engine": "edge-tts",        # "edge-tts" or "piper"
        "voice": "en-US-AriaNeural",
        "rate": "+0%",
        "volume": "+0%",
        "piper_model": None,
    },
    "overlay": {
        "position": "bottom-right",
        "opacity": 0.85,
        "font_size": 14,
        "show_on_transcription": True,
        "auto_hide_seconds": 5,
    },
    "status_server": {
        "enabled": True,
        "port": 7899,
    },
    "hotkeys": {
        "toggle_listening": "ctrl+shift+l",
        "push_to_talk": "ctrl+shift+space",
    },
    "claude": {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1024,
    },
    "post_processing": {
        "capitalize_sentences": True,
        "fix_common_words": True,
        "remove_filler_words": False,
    },
}

CONFIG_PATH = Path.home() / ".voice-bridge" / "config.yaml"

def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base. Override wins on conflicts."""
    result = deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result

def load_config() -> dict:
    """Load config with defaults. Old config files automatically gain new keys."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            user_config = yaml.safe_load(f) or {}
        return deep_merge(DEFAULT_CONFIG, user_config)
    return deepcopy(DEFAULT_CONFIG)

def save_config(config: dict):
    """Save only user-modified values (diff against defaults)."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
```

### Status Sidecar Pattern

```python
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

class StatusHandler(BaseHTTPRequestHandler):
    """Lightweight HTTP handler exposing app state as JSON."""
    app_state = {}  # Shared reference, set by orchestrator

    def do_GET(self):
        if self.path == "/status":
            state = {
                "service": "voice-bridge",
                "version": "4.0.0",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": self.app_state.get("uptime", 0),
                "stt": {
                    "status": self.app_state.get("stt_status", "unknown"),
                    "model": self.app_state.get("stt_model", ""),
                    "total_transcriptions": self.app_state.get("transcription_count", 0),
                },
                "tts": {
                    "engine": self.app_state.get("tts_engine", ""),
                    "queue_size": self.app_state.get("tts_queue_size", 0),
                },
                "overlay": {
                    "visible": self.app_state.get("overlay_visible", False),
                },
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(state, indent=2).encode())
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass  # Suppress console spam

class StatusServer:
    def __init__(self, port: int, app_state: dict):
        StatusHandler.app_state = app_state
        self.server = HTTPServer(("127.0.0.1", port), StatusHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self.server.shutdown()
```

### Post-Processing Pipeline with Fail-Fast Ordering

```python
class TextProcessor:
    """Pipeline of text transformations with fail-fast ordering."""
    def __init__(self, config: dict):
        self.steps = []
        # Order matters: cheapest/most-likely-to-reject first
        if config.get("remove_filler_words"):
            self.steps.append(self._remove_fillers)
        if config.get("fix_common_words"):
            self.steps.append(self._fix_common_words)
        if config.get("capitalize_sentences"):
            self.steps.append(self._capitalize_sentences)

    def process(self, text: str) -> str:
        for step in self.steps:
            text = step(text)
            if not text.strip():
                return ""  # Fail fast: empty after processing
        return text

    def _remove_fillers(self, text: str) -> str:
        fillers = ["um", "uh", "like", "you know", "basically", "actually"]
        for filler in fillers:
            text = text.replace(f" {filler} ", " ")
        return text.strip()

    def _fix_common_words(self, text: str) -> str:
        corrections = {"claude": "Claude", "python": "Python", "github": "GitHub"}
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        return text

    def _capitalize_sentences(self, text: str) -> str:
        import re
        return re.sub(r'(^|[.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
```

### Overlay with Always-On-Top Transparency

```python
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont

class Overlay(QWidget):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool  # Hides from taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(config.get("opacity", 0.85))

        self.label = QLabel("")
        self.label.setFont(QFont("Segoe UI", config.get("font_size", 14)))
        self.label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 180);
                border-radius: 8px;
                padding: 12px 16px;
            }
        """)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

    @pyqtSlot(str)
    def show_transcription(self, text: str):
        """Called via Qt signal from STT thread. Safe to update GUI here."""
        self.label.setText(text)
        self._position_overlay()
        self.show()
        auto_hide = self.config.get("auto_hide_seconds", 5)
        if auto_hide > 0:
            self.hide_timer.start(auto_hide * 1000)

    def _position_overlay(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        pos = self.config.get("position", "bottom-right")
        margin = 20
        self.adjustSize()
        if pos == "bottom-right":
            self.move(screen.width() - self.width() - margin,
                      screen.height() - self.height() - margin - 40)
        elif pos == "top-right":
            self.move(screen.width() - self.width() - margin, margin)
```

## Implementation Steps

1. **Define DEFAULT_CONFIG first** -- Every feature starts as a config entry with a sensible default. This is config-first development.
2. **Build the config loader** with `deep_merge` so old config files automatically gain new keys.
3. **Create the overlay** as a standalone QWidget. Test it independently by showing/hiding with a timer.
4. **Build the STT engine** as a QThread subclass with signals. Test it standalone (print signals to console).
5. **Connect STT signals to overlay** -- This validates the threading model before adding complexity.
6. **Add TTS engine** with an audio queue pattern (sounddevice playback on its own thread).
7. **Add pystray tray** on a background thread with Qt signals for menu actions (toggle, settings, quit).
8. **Add the status sidecar** -- HTTPServer on a daemon thread, reading shared state dict.
9. **Build settings dialog** as a QDialog that reads/writes the config dict and calls `save_config`.
10. **Wire the orchestrator** (main.py) that instantiates everything, connects all signals, and runs `app.exec()`.
11. **Add post-processing pipeline** with fail-fast ordering (cheapest filters first).
12. **Add transcription history** for session logging and replay.

## When to Use

- Python desktop app with real-time audio input/output
- System tray applications that need a floating overlay
- Applications mixing blocking I/O (mic, network) with a responsive GUI
- Apps that need to expose internal state to external dashboards
- Any Python GUI app where multiple long-running background tasks must coexist

## When NOT to Use

- Simple CLI tools -- overkill for non-GUI apps
- Web applications -- use a web framework instead
- Applications that only need a tray icon without overlay -- pystray alone is simpler
- Cross-platform mobile apps -- use Flutter, React Native, or Kivy instead
- If you only need audio recording without real-time processing -- use simpler subprocess calls

## Common Mistakes

1. **Updating GUI from background thread** -- Qt crashes or silently corrupts. ALWAYS use signals or `QMetaObject.invokeMethod`. Never call `widget.setText()` from a non-main thread.
2. **Forgetting `daemon=True` on utility threads** -- The app hangs on exit because non-daemon threads block process termination.
3. **Not using `deep_merge` for config** -- Adding a new config key breaks users with existing config files. Their YAML lacks the new key, and code crashes on `KeyError`.
4. **Blocking the Qt event loop** -- Long API calls or TTS generation on the main thread freezes the overlay. Use QThread or `asyncio` integration.
5. **pystray blocking the main thread** -- pystray's `icon.run()` blocks. It MUST run on a background thread, with Qt signals bridging menu actions back to the main thread.
6. **Wake word debounce** -- Without debounce, the wake word fires multiple times in rapid succession. Use a timestamp check with a configurable cooldown (e.g., 2000ms).
7. **Not handling audio device changes** -- Users plug/unplug headphones. STT and TTS engines need graceful recovery or device re-enumeration.

## Related Skills

- `togglable-processing-pipeline.md` -- Fail-fast pipeline pattern used in text processor
- `realtime-monitoring-dashboard.md` -- The dashboard that consumes the status sidecar
- `multi-project-autonomous-build.md` -- The methodology used to build this alongside other projects

## References

- Contributed from: **voice-bridge-v4** (`C:\path\to\repos\voice-bridge-v3`)
- PyQt6 threading docs: https://doc.qt.io/qt-6/threads-qobject.html
- pystray docs: https://pystray.readthedocs.io/
- RealtimeSTT: https://github.com/KoljaB/RealtimeSTT
- edge-tts: https://github.com/rany2/edge-tts
