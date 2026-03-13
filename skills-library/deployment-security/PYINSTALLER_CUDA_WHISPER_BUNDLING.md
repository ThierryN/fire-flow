# PyInstaller + CUDA/faster-whisper Bundling — Solution & Implementation

## The Problem

Packaging a Python desktop app that uses **faster-whisper** (CTranslate2 backend with CUDA GPU acceleration) into a distributable Windows `.exe` via PyInstaller. The build either crashes at runtime with missing DLLs, fails to find the Whisper model, or silently falls back to CPU because CUDA libraries weren't bundled.

### Why It Was Hard

- CTranslate2 ships CUDA/cuDNN DLLs as binary extensions that PyInstaller doesn't auto-detect
- `faster-whisper` has implicit imports PyInstaller's analysis misses
- `sounddevice` bundles PortAudio as data files, not standard Python imports
- `pynput`, `pystray`, and `keyboard` all have platform-specific backends (`_win32`) that need explicit hidden imports
- The `anthropic` SDK pulls in `httpx`/`httpcore`/`anyio` — deep async dependency chains
- `--onefile` mode is a trap: CUDA DLLs are 500MB+ and extract to temp on every launch

### Impact

- App won't start (missing DLL errors)
- Whisper transcription fails or runs on CPU (10x slower) instead of GPU
- End users get cryptic `ModuleNotFoundError` at runtime
- Build appears to succeed but the exe is broken

---

## The Solution

### Root Cause

PyInstaller's static analysis can't trace binary extensions loaded via `ctypes`, platform-dispatched backends (e.g., `pystray._win32`), or data files shipped alongside packages. You must explicitly collect these.

### The Spec File Pattern

```python
# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for apps using faster-whisper with CUDA."""
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# KEY INSIGHT: collect_dynamic_libs grabs ALL .dll/.so from the package
# This catches CUDA, cuDNN, and CTranslate2 backend libraries
ctranslate2_binaries = collect_dynamic_libs('ctranslate2')

# sounddevice ships PortAudio as data files, not binaries
sounddevice_data = collect_data_files('sounddevice')

# faster-whisper may include tokenizer assets
faster_whisper_data = collect_data_files('faster_whisper')

a = Analysis(
    ['src/your_app/__main__.py'],
    binaries=ctranslate2_binaries,
    datas=(
        sounddevice_data
        + faster_whisper_data
        + [('assets', 'assets')]  # your app's data files
    ),
    hiddenimports=[
        # -- CUDA transcription backend --
        'ctranslate2',
        'faster_whisper',

        # -- Audio --
        'sounddevice',
        '_sounddevice_data',

        # -- Global hotkeys (if using keyboard lib) --
        'keyboard',

        # -- pynput (platform-specific backends) --
        'pynput.keyboard._win32',
        'pynput.mouse._win32',

        # -- System tray (platform-specific) --
        'pystray._win32',

        # -- Anthropic SDK + HTTP stack --
        'anthropic',
        'httpx', 'httpcore', 'h11',
        'sniffio', 'anyio', 'anyio._backends._asyncio',

        # -- Config --
        'yaml',

        # -- Image handling (Pillow, used by pystray) --
        'PIL', 'PIL.Image',

        # -- GUI --
        'tkinter', 'tkinter.ttk', 'tkinter.font',
        'tkinter.scrolledtext', 'tkinter.messagebox',

        # -- Other --
        'numpy', 'winsound', 'pyperclip',
    ],
    excludes=['pytest', 'setuptools', 'pip', 'wheel'],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# IMPORTANT: Use onedir, not onefile. CUDA DLLs are too large.
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='YourApp',
    console=False,     # GUI/tray app — no console window
    upx=False,         # Don't compress — CUDA DLLs don't compress well
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=False,
    name='YourApp',
)
```

### Critical Decisions Explained

| Decision | Why |
|----------|-----|
| `--onedir` not `--onefile` | CUDA DLLs are 500MB+. Onefile extracts to temp on every launch — 30s+ startup |
| `upx=False` | UPX breaks CUDA DLLs and provides minimal savings on binary extensions |
| `console=False` | Tray/GUI apps shouldn't show a console window |
| `collect_dynamic_libs('ctranslate2')` | The **key** line — grabs CUDA + cuDNN wrapper DLLs |
| `collect_data_files('sounddevice')` | PortAudio is shipped as data, not a Python import |
| Platform-specific hidden imports | `pystray._win32`, `pynput.keyboard._win32` — PyInstaller can't detect dispatch |

### Frozen Mode Detection (for autostart, paths, etc.)

```python
import sys

if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    app_dir = sys._MEIPASS          # Extracted temp dir (onefile) or bundle dir (onedir)
    exe_path = sys.executable       # The actual .exe path
else:
    # Running from source
    app_dir = os.path.dirname(__file__)
    exe_path = sys.executable       # Python interpreter
```

### Build Script (Windows)

```bat
@echo off
call .venv\Scripts\activate.bat
pip install pyinstaller>=6.0 >nul 2>&1
pyinstaller voice-bridge.spec --clean --noconfirm
```

---

## Testing the Fix

### Build Verification
```bash
# Build completes without errors
pyinstaller your-app.spec --clean --noconfirm

# Output directory exists with exe + DLLs
dir dist\YourApp\YourApp.exe
dir dist\YourApp\*.dll | find /c ".dll"   # Should show CUDA DLLs
```

### Runtime Verification
```
1. Launch dist\YourApp\YourApp.exe
2. Verify tray icon appears (pystray works)
3. Trigger audio recording (sounddevice works)
4. Trigger transcription (faster-whisper + CUDA works)
5. Check GPU is used: look for "Model loaded on cuda" in logs
```

### Common Runtime Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: ctranslate2` | Missing hidden import | Add `'ctranslate2'` to hiddenimports |
| `Could not load library cudnn` | cuDNN DLLs not bundled | Verify `collect_dynamic_libs('ctranslate2')` is in binaries |
| `No module named 'pystray._win32'` | Platform backend not found | Add `'pystray._win32'` to hiddenimports |
| `PortAudio not found` | sounddevice data not bundled | Add `collect_data_files('sounddevice')` to datas |
| `httpcore not found` | anthropic SDK dependency chain | Add `'httpx', 'httpcore', 'h11'` to hiddenimports |
| App starts but GPU not used | CUDA DLLs missing at runtime | Check `dist/YourApp/` for `cublas*.dll`, `cudnn*.dll` |

---

## Prevention

1. **Always use `collect_dynamic_libs`** for packages with native extensions (ctranslate2, torch, onnxruntime)
2. **Always use `collect_data_files`** for packages that ship non-Python data (sounddevice, transformers)
3. **Test the frozen build immediately** — don't assume build success = runtime success
4. **Log which device** your ML model loads on (cuda vs cpu) so you can catch silent fallbacks
5. **Use `--onedir`** for CUDA apps — `--onefile` is a trap

---

## Related Patterns

- GPU fallback pattern: try CUDA, catch exception, fall back to CPU with logging
- Frozen path detection: `getattr(sys, 'frozen', False)` for all path-dependent code
- Windows autostart with registry: different commands for frozen vs source

---

## Common Mistakes to Avoid

- Using `--onefile` with CUDA libraries (30s+ startup, temp extraction issues)
- Forgetting platform-specific backends (pystray, pynput on Windows)
- Not testing the actual .exe (build succeeding doesn't mean runtime works)
- Using `upx=True` which breaks CUDA DLLs
- Assuming PyInstaller traces `ctypes.cdll.LoadLibrary` calls (it doesn't)

---

## Resources

- [PyInstaller hooks documentation](https://pyinstaller.org/en/stable/hooks.html)
- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [CTranslate2 packaging](https://github.com/OpenNMT/CTranslate2)

---

## Time to Implement

**30-60 minutes** for initial spec file creation and testing. Most time spent on iterating hidden imports after runtime errors.

## Difficulty Level

Stars: 4/5 — Requires understanding of PyInstaller internals, CUDA library loading, and platform-specific Python package dispatch. Hard to debug because errors only appear at runtime in the frozen build.

---

**Author Notes:**
The #1 insight: `collect_dynamic_libs('ctranslate2')` is the magic line. Without it, you get a build that succeeds but an exe that crashes. The second insight: always use `--onedir` for ML/CUDA apps. The `--onefile` mode is tempting but creates a terrible user experience with multi-hundred-MB temp extractions on every launch.
