---
name: realtimestt-openwakeword-cuda-windows
category: integrations
version: 1.0.0
contributed: 2026-02-22
contributor: voice-bridge-v3
last_updated: 2026-02-22
tags: [realtimestt, openwakeword, whisper, cuda, wake-word, speech-to-text, windows, pyaudio, torch-multiprocessing, pyqt6]
difficulty: hard
usage_count: 0
success_rate: 100
---

# RealtimeSTT + OpenWakeWord + CUDA on Windows

## Problem

Integrating OpenWakeWord wake word detection via RealtimeSTT's native `wakeword_backend` parameter on Windows with CUDA GPU hits 7 non-obvious failures that each appear as unrelated errors. The combination of RealtimeSTT's `torch.multiprocessing` child processes, OpenWakeWord's ONNX model loading, CUDA's float16 compute, MKL memory allocation, and PyQt6's global state creates a minefield of ordering and configuration gotchas.

**Symptoms you'll see (in order of appearance):**
1. `Wakeword engine oww unknown/unsupported or wake_words not specified`
2. `mkl_malloc: failed to allocate memory`
3. `ValueError: Requested float16 compute type, but the target device or backend do not support efficient float16 computation`
4. `BrokenPipeError` in torch.multiprocessing child process
5. `MemoryError` in openwakeword `_streaming_melspectrogram`
6. Wake word fires 5+ times per single utterance (no debounce)
7. Transcription returns garbage ("Bit.") after fragmented audio

## Solution Pattern

Each error has a specific fix. Apply ALL of them — they're independent failure modes.

### 1. Backend Name + wake_words Parameter (BOTH required)

RealtimeSTT checks: `elif wake_words and self.wakeword_backend in {'oww', 'openwakeword', 'openwakewords'}`

Both conditions must be true. If `wake_words` is empty/missing, the entire wake word system silently skips.

```python
# WRONG — wake_words defaults to empty, silently disables wake word
AudioToTextRecorder(wakeword_backend="openwakeword")

# RIGHT — both backend AND wake_words must be set
AudioToTextRecorder(
    wakeword_backend="openwakeword",
    wake_words="hey_jarvis",  # REQUIRED — comma-separated built-in model names
    wake_words_sensitivity=0.35,
)
```

Built-in models: `alexa`, `hey_jarvis`, `hey_mycroft`, `hey_rhasspy`, `timer`, `weather`.

### 2. MKL Thread Memory (High-Core CPUs)

On CPUs with 16+ threads (i9-12900H has 20), MKL allocates buffers for ALL threads simultaneously while loading OpenWakeWord + Whisper models. Must be set BEFORE any imports.

```python
# MUST be at the very top of your entry point, before ANY imports
import os
os.environ.setdefault("MKL_NUM_THREADS", "4")
os.environ.setdefault("OMP_NUM_THREADS", "4")
```

### 3. CUDA float16 in torch.multiprocessing Context

CTranslate2 CUDA float16 works perfectly in direct tests but fails inside RealtimeSTT's `mp.Process` child processes on Windows. The child processes re-import everything and the CUDA state gets confused.

```python
# WRONG — fails inside RealtimeSTT's multiprocessing context
AudioToTextRecorder(compute_type="float16")

# RIGHT — let CTranslate2 choose the best available type
AudioToTextRecorder(compute_type="auto")
```

### 4. PyQt6 Import Order (Windows only)

PyQt6 creates global state that breaks `torch.multiprocessing` child processes when `enable_realtime_transcription=True`. Initialize STT FGTAT, then import PyQt6.

```python
# WRONG — PyQt6 imported before STT causes BrokenPipeError
from PyQt6.QtWidgets import QApplication
from RealtimeSTT import AudioToTextRecorder
recorder = AudioToTextRecorder(enable_realtime_transcription=True)  # CRASH

# RIGHT — initialize STT before any PyQt6 imports
from RealtimeSTT import AudioToTextRecorder
recorder = AudioToTextRecorder(enable_realtime_transcription=True)
recorder_ready = True  # models loaded, child processes spawned

# NOW safe to import PyQt6
from PyQt6.QtWidgets import QApplication
app = QApplication(sys.argv)
```

### 5. First-Launch Audio Queue Overflow

First run downloads OpenWakeWord models from HuggingFace (~30s). Audio queues up during download. When wake word processing starts, the backlog causes `MemoryError` in `_streaming_melspectrogram`.

**Fix:** Kill and restart. Models are cached after first download, startup drops to ~8s with no backlog. This is a one-time issue.

**Better fix (if building a product):** Flush the audio queue after recorder initialization:
```python
recorder = AudioToTextRecorder(**params)
# Flush any audio that queued during model download
while not recorder.audio_queue.empty():
    try:
        recorder.audio_queue.get_nowait()
    except:
        break
```

### 6. Wake Word Callback Debounce

RealtimeSTT fires `on_wakeword_detected` on every overlapping audio chunk that scores above threshold. A single "Hey Jarvis" produces 5+ callbacks in 127ms, fragmenting the audio buffer.

```python
import time

class STTEngine:
    def __init__(self):
        self._wakeword_debounce_sec = 2.0
        self._last_wakeword_time = 0.0

    def _handle_wakeword_detected(self):
        now = time.time()
        if now - self._last_wakeword_time < self._wakeword_debounce_sec:
            return  # duplicate within debounce window
        self._last_wakeword_time = now

        # Process the actual detection
        self.on_wakeword_detected()
```

### 7. Config File Deep-Merge Staleness

If your app creates a config file on first run with wrong defaults, `_deep_merge` preserves old values on subsequent runs. After fixing defaults in code, **delete the on-disk config** to regenerate.

```bash
# If wake word doesn't work after code fix, check the on-disk config
del %USERPROFILE%\.claude\voice-bridge-v3\config.yaml
# Restart app — regenerates with correct defaults
```

## Implementation Steps

1. Set `MKL_NUM_THREADS=4` and `OMP_NUM_THREADS=4` at the very top of entry point
2. Initialize `AudioToTextRecorder` with `compute_type="auto"`, `wakeword_backend="openwakeword"`, `wake_words="hey_jarvis"`
3. THEN import PyQt6/PySide6 (after recorder is initialized)
4. Add 2-second debounce to `on_wakeword_detected` callback
5. On first launch, expect model downloads — kill and restart if MemoryError occurs
6. Delete stale config files after changing defaults

## When to Use

- Building a voice-to-text application with wake word activation on Windows
- Using RealtimeSTT with OpenWakeWord backend and CUDA GPU
- Combining speech-to-text with a Qt-based GUI on Windows
- Any project using `torch.multiprocessing` alongside CUDA and audio processing

## When NOT to Use

- Linux/macOS — torch.multiprocessing uses fork() not spawn(), different behavior
- CPU-only inference — float16 issue doesn't apply
- Porcupine wake word backend — different engine, different issues
- No GUI framework — PyQt6 import order issue doesn't apply

## Common Mistakes

- Setting `wakeword_backend` without `wake_words` — silently disables wake word
- Using `compute_type="float16"` — works in tests, fails in production
- Importing PyQt6 at module top level — breaks multiprocessing child processes
- Not debouncing wake word callbacks — causes fragmented audio transcription
- Forgetting to delete stale config after fixing code defaults
- Setting MKL_NUM_THREADS after importing numpy/scipy — too late, already allocated

## Diagnostic Script

Use this standalone test to verify wake word detection works independently of RealtimeSTT:

```python
"""test_wakeword.py — Tests OpenWakeWord directly with microphone"""
import numpy as np
import pyaudio
from openwakeword.model import Model
import openwakeword

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280  # 80ms at 16kHz
THRESHOLD = 0.35

openwakeword.utils.download_models()
model = Model(inference_framework="onnx")
print(f"Models: {list(model.models.keys())}")

pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16, channels=1,
                 rate=SAMPLE_RATE, input=True,
                 frames_per_buffer=CHUNK_SIZE)
try:
    while True:
        audio = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        pcm = np.frombuffer(audio, dtype=np.int16)
        model.predict(pcm)
        for name in model.prediction_buffer:
            score = list(model.prediction_buffer[name])[-1]
            if score >= THRESHOLD:
                print(f"DETECTED: {name} (score={score:.4f})")
            elif score > 0.05:
                print(f"  heard: {name} (score={score:.4f})")
except KeyboardInterrupt:
    pass
finally:
    stream.close()
    pa.terminate()
```

## Related Skills

- [stripe-payment-integration-complete](../integrations/stripe-payment-integration-complete.md) - Third-party API integration patterns
- [cloudflare-turnstile-debugging](../integrations/cloudflare-turnstile-debugging.md) - Debugging third-party library integration

## References

- RealtimeSTT: https://github.com/KoljaB/RealtimeSTT
- OpenWakeWord: https://github.com/dscripka/openWakeWord
- OpenWakeWord custom model training: https://openwakeword.com/
- CTranslate2 CUDA: https://github.com/OpenNMT/CTranslate2
- Contributed from: voice-bridge-v3 (C:\path\to\repos\voice-bridge-v3)
