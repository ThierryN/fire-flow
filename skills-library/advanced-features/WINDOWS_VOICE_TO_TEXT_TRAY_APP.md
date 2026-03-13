---
name: windows-voice-to-text-tray-app
category: advanced-features
version: 1.0.0
contributed: 2026-02-19
contributor: claude-voice-bridge
last_updated: 2026-02-19
tags: [python, windows, voice, whisper, stt, tray, hotkey, tkinter, pystray, cuda, gpu, desktop-app]
difficulty: hard
---

# Windows Voice-to-Text System Tray App — Complete Architecture

## Problem

Building a local, always-running Windows desktop app that:
- Lives in the system tray (no main window)
- Records audio via hold-to-talk global hotkey
- Transcribes speech locally using GPU-accelerated Whisper
- Pastes text into any active window OR sends to an API
- Has settings GUI, setup wizard, and auto-start with Windows
- Packages as a distributable .exe

This requires coordinating 6+ subsystems (audio, hotkeys, GUI, tray, STT, API) across multiple threads without blocking the tray mainloop.

## Solution Pattern

### Architecture Overview

```
System Tray (pystray) ← main thread, blocks
    │
    ├── HotkeyManager (keyboard lib) ← global hooks, runs in tray setup thread
    │     ├── on_press → start recording
    │     └── on_release → stop recording → spawn transcription thread
    │
    ├── AudioRecorder (sounddevice) ← PortAudio callback thread
    │     └── float32 numpy chunks → concatenate on stop
    │
    ├── Transcriber (faster-whisper) ← lazy-loaded, runs in daemon thread
    │     └── GPU (CUDA) with CPU fallback
    │
    ├── PreviewOverlay (tkinter) ← own thread + mainloop
    │     └── queue-based thread-safe updates
    │
    ├── ChatWindow (tkinter) ← own thread + mainloop
    │     └── streaming text append via queue
    │
    └── Config (YAML) ← ~/.claude/voice-bridge/config.yaml
          └── dataclass-based, hot-reloadable
```

### Key Insight: Threading Model

**The #1 architectural challenge is threading.** pystray blocks the main thread. tkinter requires its own mainloop. Audio callbacks run in a C thread. Hotkeys run via OS hooks. Everything must communicate without deadlocks.

**Solution:** Each GUI component (overlay, chat window) gets its own thread running `tk.mainloop()`. Cross-thread communication uses `queue.Queue` — other threads push lambdas onto the queue, and a `root.after(50, poll)` timer drains the queue on the tk thread.

```python
class ThreadSafeTkComponent:
    def __init__(self):
        self._root = None
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._run_tk, daemon=True)
        self._ready = threading.Event()

    def start(self):
        self._thread.start()
        self._ready.wait(timeout=5)

    def _run_tk(self):
        self._root = tk.Tk()
        self._root.withdraw()
        self._poll()
        self._root.mainloop()

    def _poll(self):
        try:
            while True:
                action = self._queue.get_nowait()
                action()
        except queue.Empty:
            pass
        if self._root:
            self._root.after(50, self._poll)

    def do_something(self, text):
        """Thread-safe — callable from any thread."""
        self._queue.put(lambda: self._update_widget(text))

    def stop(self):
        """Clean shutdown — quit mainloop and join thread."""
        if self._root:
            self._queue.put(lambda: self._root.quit())
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
```

## Complete Module Breakdown

### 16 Source Files — What Each Does

| Module | Purpose | Thread Model |
|--------|---------|-------------|
| `main.py` | Entry point, VoiceBridge orchestrator class | Main thread (blocked by tray) |
| `config.py` | YAML config with dataclasses, load/save | Sync (called from any thread) |
| `logger.py` | RotatingFileHandler + console logging | Thread-safe (stdlib logging) |
| `tray.py` | pystray icon with dynamic color states | Main thread (blocks) |
| `hotkeys.py` | Global keyboard hooks, hold-to-talk detection | Tray setup thread |
| `audio.py` | sounddevice InputStream, numpy chunks | PortAudio C callback thread |
| `chime.py` | winsound.Beep for audio feedback | Spawns daemon threads |
| `transcriber.py` | faster-whisper, lazy model load, GPU fallback | Daemon transcription thread |
| `overlay.py` | Borderless tkinter preview (paste/cancel) | Own tk thread + queue |
| `paste.py` | pynput keyboard simulation, focus restore | Transcription thread |
| `claude_api.py` | anthropic SDK streaming client | Daemon API thread |
| `chat_window.py` | Scrollable Q&A tkinter window | Own tk thread + queue |
| `wizard.py` | First-launch setup wizard (multi-page) | Main thread (before tray) |
| `settings_gui.py` | Tabbed settings window | Own tk instance |
| `autostart.py` | Windows registry Run key management | Sync |
| `__main__.py` | `python -m voice_bridge` entry | Calls main() |

### Hold-to-Talk Flow (Core UX Pattern)

```
User holds Ctrl+Shift+Space
    │
    ├─ 1. HotkeyManager._on_paste_key_down()
    │     └─ check modifiers + debounce (200ms)
    │
    ├─ 2. VoiceBridge._on_paste_start()
    │     ├─ capture foreground window handle (ctypes user32)
    │     ├─ play start chime (winsound.Beep, daemon thread)
    │     ├─ set tray icon → red
    │     └─ AudioRecorder.start() (opens PortAudio stream)
    │
User releases key
    │
    ├─ 3. HotkeyManager._on_paste_key_up()
    │     └─ VoiceBridge._on_paste_stop()
    │           ├─ AudioRecorder.stop() → returns numpy array
    │           ├─ play stop chime
    │           └─ spawn daemon thread → _transcribe(audio, "paste")
    │
    ├─ 4. _transcribe() (background thread)
    │     ├─ set tray icon → orange (processing)
    │     ├─ lazy-load Whisper model (first use only)
    │     ├─ transcriber.transcribe(audio) → text
    │     └─ mode == "paste":
    │           ├─ copy to clipboard (clip.exe)
    │           ├─ restore focus to captured window (SetForegroundWindow)
    │           ├─ simulate Shift+Insert (pynput)
    │           └─ set tray icon → blue (idle)
    │
    └─ Total latency: ~1-2s for 5s audio on GPU
```

### Config System (dataclass + YAML)

```python
from dataclasses import dataclass, field, asdict
from pathlib import Path
import yaml

CONFIG_DIR = Path.home() / ".claude" / "voice-bridge"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

@dataclass
class HotkeyConfig:
    paste_mode: str = "ctrl+shift+space"
    direct_mode: str = "ctrl+shift+d"

@dataclass
class WhisperConfig:
    model_size: str = "small"       # tiny, base, small, medium
    language: str = "en"
    device: str = "cuda"            # cuda or cpu
    compute_type: str = "float16"   # float16 (GPU) or int8 (CPU)

@dataclass
class DirectModeConfig:
    model: str = "claude-haiku-4-5-20251001"
    api_key: str = ""
    max_tokens: int = 1024

@dataclass
class AppConfig:
    hotkeys: HotkeyConfig = field(default_factory=HotkeyConfig)
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    direct_mode: DirectModeConfig = field(default_factory=DirectModeConfig)
    auto_enter: bool = False
    auto_start: bool = True
    chime_enabled: bool = True
    first_run: bool = True

def load_config() -> AppConfig:
    if not CONFIG_FILE.exists():
        config = AppConfig()
        save_config(config)
        return config
    with open(CONFIG_FILE) as f:
        data = yaml.safe_load(f) or {}
    # Build nested config with defaults for missing keys
    return AppConfig(
        hotkeys=HotkeyConfig(**data.get("hotkeys", {})),
        whisper=WhisperConfig(**data.get("whisper", {})),
        direct_mode=DirectModeConfig(**data.get("direct_mode", {})),
        **{k: data[k] for k in data if k not in ("hotkeys", "whisper", "direct_mode")}
    )

def save_config(config: AppConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(asdict(config), f, default_flow_style=False)
```

### System Tray with Dynamic Icon States

```python
from PIL import Image, ImageDraw
import pystray

COLOR_IDLE = "#4A90D9"       # Blue — ready
COLOR_RECORDING = "#E74C3C"  # Red — recording
COLOR_PROCESSING = "#F39C12" # Orange — transcribing

def make_icon(color="#4A90D9"):
    """Generate colored circle icon programmatically — no .ico file needed."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((4, 4, 60, 60), fill=color, outline="white", width=2)
    draw.ellipse((24, 24, 40, 40), fill="white")  # Inner dot for recognition
    return img

def set_icon_state(icon, state):
    """Update tray icon color: 'idle', 'recording', 'processing'."""
    colors = {"idle": COLOR_IDLE, "recording": COLOR_RECORDING, "processing": COLOR_PROCESSING}
    icon.icon = make_icon(colors.get(state, COLOR_IDLE))
```

### Global Hotkey Hold-to-Talk Pattern

```python
import keyboard
import time

class HotkeyManager:
    """Hold-to-talk with modifier detection and debounce."""

    def __init__(self, on_start, on_stop, hotkey="ctrl+shift+space"):
        parts = hotkey.lower().split("+")
        self._trigger = parts[-1]        # "space"
        self._modifiers = parts[:-1]     # ["ctrl", "shift"]
        self._active = False
        self._last_time = 0.0
        self._on_start = on_start
        self._on_stop = on_stop

    def _check_mods(self):
        return all(keyboard.is_pressed(m) for m in self._modifiers)

    def _on_key_down(self, event):
        now = time.monotonic()
        if not self._active and self._check_mods() and (now - self._last_time) > 0.2:
            self._active = True
            self._last_time = now
            self._on_start()

    def _on_key_up(self, event):
        if self._active:
            self._active = False
            self._on_stop()

    def register(self):
        keyboard.on_press_key(self._trigger, self._on_key_down, suppress=False)
        keyboard.on_release_key(self._trigger, self._on_key_up, suppress=False)

    def unregister(self):
        keyboard.unhook_all()
```

### Whisper Transcription with GPU Fallback

```python
from faster_whisper import WhisperModel

class Transcriber:
    """Lazy-loaded Whisper with automatic GPU → CPU fallback."""

    def __init__(self, model_size="small", device="cuda"):
        self.model_size = model_size
        self.device = device
        self._model = None

    def _load(self):
        try:
            self._model = WhisperModel(self.model_size, device=self.device, compute_type="float16")
        except Exception:
            if self.device == "cuda":
                # GPU failed — fall back to CPU
                self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            else:
                raise

    def transcribe(self, audio):
        """audio: 1D float32 numpy array at 16kHz."""
        if len(audio) < 4800:  # < 0.3s, skip
            return ""
        if self._model is None:
            self._load()
        segments, _ = self._model.transcribe(audio, language="en", beam_size=5, vad_filter=True)
        parts = [s.text.strip() for s in segments if s.no_speech_prob < 0.6 and s.text.strip()]
        return " ".join(parts)
```

### Clean Shutdown Pattern

```python
import signal, atexit

class App:
    def __init__(self):
        self._shutting_down = False

    def shutdown(self):
        if self._shutting_down:
            return  # Guard against double-shutdown
        self._shutting_down = True

        # Order matters: hotkeys → recorder → GUIs → tray
        for name, cleanup in [
            ("hotkeys", lambda: self.hotkeys.unregister()),
            ("recorder", lambda: self.recorder.stop() if self.recorder.is_recording else None),
            ("overlay", lambda: self.overlay.stop() if self.overlay else None),
            ("chat", lambda: self.chat_window.stop() if self.chat_window else None),
            ("tray", lambda: self.icon.stop() if self.icon else None),
        ]:
            try:
                cleanup()
            except Exception as e:
                logger.error(f"Shutdown error ({name}): {e}")

def main():
    setup_logging()
    app = App(load_config())

    signal.signal(signal.SIGINT, lambda s, f: app.shutdown())
    signal.signal(signal.SIGTERM, lambda s, f: app.shutdown())
    atexit.register(app.shutdown)

    try:
        app.run()
    except Exception:
        logger.critical("Unhandled exception", exc_info=True)
        sys.exit(1)
```

### Borderless Overlay Without Taskbar Entry (Windows)

```python
import ctypes

# After creating a Toplevel window:
window.overrideredirect(True)      # No title bar
window.attributes("-topmost", True) # Always on top

# Remove from taskbar (Windows-specific)
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000

hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
style = (style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
```

## Tech Stack

| Component | Library | Why |
|-----------|---------|-----|
| System tray | `pystray` | Cross-platform, PIL icon support |
| Audio | `sounddevice` | PortAudio bindings, callback mode, low latency |
| Hotkeys | `keyboard` | Global hooks, modifier detection, no admin required |
| Keyboard sim | `pynput` | Reliable keystroke simulation for paste |
| STT | `faster-whisper` | CTranslate2 backend, 10x faster than OpenAI whisper |
| GPU | CUDA via CTranslate2 | RTX 3080 Ti transcribes 10s audio in <1s |
| GUI | `tkinter` | Ships with Python, no extra install |
| Config | `pyyaml` + dataclasses | Human-readable, typed defaults |
| API | `anthropic` SDK | Streaming responses |
| Packaging | PyInstaller | Single-directory Windows bundle |

## Implementation Steps (Phased)

| Phase | What | Key Files | Depends On |
|-------|------|-----------|------------|
| 1. Foundation | Tray + hotkey + audio recording + chime | tray.py, hotkeys.py, audio.py, chime.py, config.py | — |
| 2. Transcription | faster-whisper with CUDA, lazy loading | transcriber.py | Phase 1 |
| 3. Paste Mode | Preview overlay + clipboard paste | overlay.py, paste.py | Phase 2 |
| 4. Direct Mode | Claude API streaming + chat window | claude_api.py, chat_window.py | Phase 2 |
| 5. Settings | Setup wizard + settings GUI + autostart | wizard.py, settings_gui.py, autostart.py | Phase 3+4 |
| 6. Packaging | PyInstaller, logging, clean shutdown | logger.py, voice-bridge.spec, build.bat | Phase 5 |

**Phases 3 and 4 can run in parallel** (both depend only on Phase 2).

## When to Use

- Building a Windows desktop utility that needs to run in the background
- Voice-to-text input for any application (not just your own)
- System tray apps with global hotkey triggers
- Apps that coordinate audio, GPU ML inference, and GUI in multiple threads
- Any hold-to-talk or push-to-talk pattern

## When NOT to Use

- Web applications (use Web Speech API instead)
- Cross-platform mobile apps (different paradigm entirely)
- Simple CLI tools (don't need tray/GUI complexity)
- Apps that only need cloud STT (just call Whisper API directly)
- Linux/macOS primary target (pystray works but hotkey libs differ)

## Common Mistakes

- **Blocking the tray thread** — pystray.Icon.run() blocks. Never do heavy work on the main thread.
- **Calling tkinter from non-tk thread** — Always use queue.put(lambda: ...) for cross-thread tk updates.
- **Not capturing foreground window BEFORE recording** — By the time recording stops, focus may have shifted.
- **Using --onefile with CUDA** — Extracts 500MB+ to temp on every launch. Use --onedir.
- **Forgetting debounce on hotkeys** — Without 200ms debounce, key repeat fires multiple recordings.
- **Not lazy-loading the Whisper model** — First load takes 2-5 seconds. Do it on first transcription, not app start.

## Related Skills

- [PyInstaller + CUDA Bundling](../deployment-security/PYINSTALLER_CUDA_WHISPER_BUNDLING.md) — Packaging this app as .exe
- Windows autostart via registry — `winreg` HKCU\...\Run key pattern

## References

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — CTranslate2-based Whisper
- [pystray](https://github.com/moses-palmer/pystray) — System tray library
- [keyboard](https://github.com/boppreh/keyboard) — Global hotkeys
- [pynput](https://github.com/moses-palmer/pynput) — Input simulation
- Contributed from: Claude Voice Bridge v1.0.0
