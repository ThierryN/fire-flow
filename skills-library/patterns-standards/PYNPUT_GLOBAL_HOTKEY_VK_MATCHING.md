# Pynput Global Hotkeys with Virtual Key Code Matching

## The Problem

Building a Windows desktop app with global hotkey detection (e.g., Ctrl+Shift+M for hold-to-talk). Two obstacles:

1. **`keyboard` library (v0.13.5) is broken on Python 3.13+** — its low-level Windows hooks (`SetWindowsHookEx`) install and the listener thread starts, but callbacks never fire. The library was last updated in 2020 and has no fix.

2. **Modifier keys corrupt `pynput` char values** — when Ctrl is held, pressing a letter key changes its `.char` attribute via Windows' control-character mapping (Ctrl+M → `'\r'`, Ctrl+D → `'\x04'`, Ctrl+A → `'\x01'`). Naive char-based matching silently fails for every Ctrl+letter combo.

### Impact

- Hotkeys appear to register (no errors) but never fire — completely silent failure
- Extremely hard to debug because the hook thread is alive, the listener is running, everything *looks* correct
- Every Ctrl+letter hotkey is affected (26 possible combos), not just edge cases

---

## The Solution

### Root Cause

**Issue 1:** The `keyboard` library's `_winkeyboard.py` uses internal threading and ctypes patterns that broke with Python 3.13+'s threading changes. The hook message pump thread runs but never delivers events to callbacks.

**Issue 2:** Windows translates Ctrl+letter keypresses into ASCII control characters at the API level. When pynput's hook receives Ctrl+M, the OS reports `char='\r'` (carriage return, 0x0D) instead of `char='m'`. But the **virtual key code (`vk`)** remains `77` (= `ord('M')`) regardless of modifiers.

### The Fix: Use pynput with VK-based matching

Replace `keyboard` with `pynput.keyboard.Listener` and match keys by `vk` (virtual key code) instead of `char`.

```python
from pynput.keyboard import Key, Listener, KeyCode

# WRONG: Match by char — fails when Ctrl is held
def _to_key_bad(name: str):
    return KeyCode.from_char(name)  # KeyCode(char='m')

def _match_bad(key, target) -> bool:
    # ctrl+m gives key.char='\r', target.char='m' → NEVER MATCHES
    return key.char == target.char


# RIGHT: Match by virtual key code — stable regardless of modifiers
def _to_key_good(name: str):
    return KeyCode.from_vk(ord(name.upper()))  # KeyCode(vk=77)

def _match_good(key, target) -> bool:
    key_vk = getattr(key, 'vk', None)
    target_vk = getattr(target, 'vk', None)
    if key_vk is not None and target_vk is not None:
        return key_vk == target_vk
    # Fallback for special keys
    return key == target
```

### Full Hold-to-Talk Hotkey Manager Pattern

```python
from pynput.keyboard import Key, Listener, KeyCode
import time

# Map config strings → sets of pynput Key objects (left, right, generic)
_MODIFIER_MAP = {
    "ctrl": {Key.ctrl_l, Key.ctrl_r, Key.ctrl},
    "shift": {Key.shift_l, Key.shift_r, Key.shift},
    "alt": {Key.alt_l, Key.alt_r, Key.alt},
}

class HotkeyManager:
    def __init__(self, hotkey_str: str, on_start, on_stop):
        parts = hotkey_str.lower().split("+")
        trigger_name = parts[-1]
        self._mod_names = parts[:-1]

        # Use vk for letter keys, Key enum for special keys
        if len(trigger_name) == 1:
            self._trigger = KeyCode.from_vk(ord(trigger_name.upper()))
        else:
            self._trigger = _SPECIAL_KEYS[trigger_name]  # Key.space, etc.

        self._on_start = on_start
        self._on_stop = on_stop
        self._active = False
        self._held_mods: set[Key] = set()
        self._debounce_s = 0.2
        self._last_time = 0.0
        self._listener = None

    def _key_matches(self, key, target) -> bool:
        if key == target:
            return True
        if isinstance(key, KeyCode) and isinstance(target, KeyCode):
            key_vk = getattr(key, 'vk', None)
            target_vk = getattr(target, 'vk', None)
            if key_vk is not None and target_vk is not None:
                return key_vk == target_vk
        return False

    def _mods_held(self) -> bool:
        for mod_name in self._mod_names:
            if not (self._held_mods & _MODIFIER_MAP.get(mod_name, set())):
                return False
        return True

    def _on_press(self, key):
        # Track modifier state
        for mod_keys in _MODIFIER_MAP.values():
            if key in mod_keys:
                self._held_mods.add(key)
                return

        now = time.monotonic()
        if (
            self._key_matches(key, self._trigger)
            and not self._active
            and self._mods_held()
            and (now - self._last_time) > self._debounce_s
        ):
            self._active = True
            self._last_time = now
            self._on_start()

    def _on_release(self, key):
        # Modifier released while active → stop
        for mod_keys in _MODIFIER_MAP.values():
            if key in mod_keys:
                self._held_mods.discard(key)
                if self._active:
                    self._active = False
                    self._on_stop()
                return

        # Trigger key released → stop
        if self._key_matches(key, self._trigger) and self._active:
            self._active = False
            self._on_stop()

    def register(self):
        self._listener = Listener(on_press=self._on_press, on_release=self._on_release)
        self._listener.start()

    def unregister(self):
        if self._listener:
            self._listener.stop()
            self._listener = None
```

### Critical Design Decisions

| Decision | Why |
|----------|-----|
| `KeyCode.from_vk(ord(name.upper()))` | VK codes are stable when modifiers are held. `from_char()` produces chars that get corrupted by Ctrl. |
| `{Key.ctrl_l, Key.ctrl_r, Key.ctrl}` in modifier map | pynput sometimes reports `Key.ctrl` (generic) instead of `Key.ctrl_l`/`Key.ctrl_r`. Must accept all three. |
| Modifier release also triggers stop | For hold-to-talk: releasing ANY part of the combo should stop. User might release Ctrl before M. |
| 200ms debounce | Prevents double-firing from key repeat when holding the combo. |
| `set` for held modifiers | O(1) intersection check with `_MODIFIER_MAP` sets. |

---

## Windows Ctrl+Key Character Mapping Reference

| Combo | `.char` received | `.vk` | ASCII Control |
|-------|-----------------|-------|---------------|
| Ctrl+A | `'\x01'` | 65 | SOH |
| Ctrl+C | `'\x03'` | 67 | ETX |
| Ctrl+D | `'\x04'` | 68 | EOT |
| Ctrl+M | `'\r'` (0x0D) | 77 | CR |
| Ctrl+H | `'\x08'` | 72 | BS |
| Ctrl+I | `'\t'` (0x09) | 73 | HT |
| Ctrl+J | `'\n'` (0x0A) | 74 | LF |
| Ctrl+[ | `'\x1b'` | 219 | ESC |

Every letter A-Z maps to control code `0x01`-`0x1A` when Ctrl is held. VK is always `ord(letter.upper())`.

---

## Testing the Fix

```python
from pynput.keyboard import Key, Controller, Listener, KeyCode
import time

results = {'start': 0, 'stop': 0}
hm = HotkeyManager("ctrl+shift+m",
    on_start=lambda: results.update({'start': results['start']+1}),
    on_stop=lambda: results.update({'stop': results['stop']+1}))
hm.register()
time.sleep(0.3)

kb = Controller()
kb.press(Key.ctrl_l); kb.press(Key.shift_l)
time.sleep(0.1)
kb.press('m'); time.sleep(0.3); kb.release('m')
time.sleep(0.1)
kb.release(Key.shift_l); kb.release(Key.ctrl_l)
time.sleep(0.3)

hm.unregister()
assert results['start'] == 1 and results['stop'] >= 1
```

---

## Prevention

1. **Never use `keyboard` library with Python 3.13+** — hooks install silently but fire zero events
2. **Never match pynput keys by `.char` when Ctrl is a modifier** — char is corrupted by OS
3. **Always use `KeyCode.from_vk()` for letter keys** in hotkey registration
4. **Include `Key.ctrl` (generic)** alongside `Key.ctrl_l`/`Key.ctrl_r` in modifier maps — pynput behavior varies
5. **Kill stale instances** before debugging hotkey issues — multiple processes registering hooks can cause Windows to silently disable them

---

## Common Mistakes to Avoid

- Using `keyboard.on_press_key()` on Python 3.13+ (silent failure, no error)
- Using `KeyCode.from_char('m')` then comparing with `==` against a key pressed with Ctrl held
- Only checking `Key.shift_l` / `Key.ctrl_l` without the generic `Key.shift` / `Key.ctrl`
- Forgetting modifier-release-as-stop for hold-to-talk patterns (user releases Ctrl before the trigger key)
- Not debouncing — key repeat fires rapid press events when holding a combo

---

## Related Patterns

- Hold-to-talk audio recording: pair with `sounddevice` for mic capture
- System tray integration: `pystray` runs on main thread, hotkey listener runs in background thread
- Frozen mode detection: `getattr(sys, 'frozen', False)` for PyInstaller builds

---

## Resources

- [pynput documentation](https://pynput.readthedocs.io/)
- [keyboard library (abandoned)](https://github.com/boppreh/keyboard) — last release 0.13.5 (2020)
- [Windows Virtual Key Codes](https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes)
- [ASCII Control Characters](https://en.wikipedia.org/wiki/ASCII#Control_characters)

---

## Time to Implement

**15-30 minutes** to replace `keyboard` with the pynput pattern. Most time spent discovering the char corruption issue.

## Difficulty Level

Stars: 3/5 — The fix itself is straightforward once you understand the root cause. The difficulty is **diagnosing** it: hooks install without error, listener threads are alive, everything looks correct, but callbacks never fire (keyboard lib) or silently mismatch (char corruption).

---

**Author Notes:**
The two traps here are *silent*. The `keyboard` library doesn't throw errors — its hooks just never fire on Python 3.13+. And pynput's char corruption doesn't throw errors either — `'\r' != 'm'` just evaluates to False and your hotkey silently never triggers. The VK code is the only stable identifier across all modifier states.
