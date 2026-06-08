# Teams Keep-Alive — Cursor Build Spec

## Overview

A lightweight cross-platform system tray application that prevents Microsoft Teams from showing "Away" by periodically jiggling the mouse cursor by 1 pixel. Built with Python, packaged as a standalone executable for macOS and Windows. Zero configuration, one click to start/stop.

---

## Goals

- Keep MS Teams status as "Available" by simulating mouse activity
- Run silently in the system tray (menubar on Mac, taskbar tray on Windows)
- Simple keyboard shortcuts to toggle on/off
- No installation required for end users (single binary)
- Works on macOS (Intel + Apple Silicon) and Windows 10/11

---

## Tech Stack

| Component | Library |
|-----------|---------|
| Mouse control | `pyautogui` |
| System tray icon | `pystray` |
| Tray icon image | `Pillow` (PIL) |
| Global hotkeys | `keyboard` |
| Packaging | `PyInstaller` |
| Python version | 3.11+ |

---

## Project Structure

```
teams-keepalive/
├── main.py                  # Entry point
├── tray.py                  # Tray icon + menu logic
├── jiggler.py               # Mouse jiggle logic (background thread)
├── hotkeys.py               # Global keyboard shortcut registration
├── icon.py                  # Programmatically generate tray icon (no asset needed)
├── requirements.txt
├── build_mac.sh             # PyInstaller build script for macOS
├── build_windows.bat        # PyInstaller build script for Windows
└── README.md
```

---

## Core Logic

### `jiggler.py`

- Runs in a daemon `threading.Thread`
- Every **60 seconds** (configurable via constant `JIGGLE_INTERVAL_SECONDS = 60`):
  1. Get current mouse position `(x, y)`
  2. Move mouse to `(x+1, y)`
  3. Wait 0.1 seconds
  4. Move mouse back to `(x, y)`
- Thread checks a `threading.Event` stop flag — stops cleanly when set
- Expose `start()`, `stop()`, `is_running()` functions

### `tray.py`

- Creates a `pystray.Icon` with a custom tray icon (green = active, grey = paused)
- Tray menu items:
  - **Status label** — e.g. `● Active — jiggling every 60s` or `○ Paused`
  - **Toggle** — `Start` / `Stop` (reflects current state)
  - **Interval submenu** — `30s`, `60s` (default), `120s`, `300s`
  - **Separator**
  - **Shortcuts** — non-clickable label showing the hotkeys
  - **Quit** — stops jiggler thread and exits
- On launch, jiggler starts automatically (user can stop it from tray)
- Icon dynamically regenerated (green circle vs grey) on state change using Pillow

### `icon.py`

Generate the tray icon programmatically using Pillow — no external image files needed:
- 64x64 RGBA image
- Green filled circle on transparent background when active
- Grey filled circle when paused
- Export as `generate_icon(active: bool) -> PIL.Image`

### `hotkeys.py`

Register global hotkeys using the `keyboard` library:

| Shortcut (Mac) | Shortcut (Windows) | Action |
|---|---|---|
| `Cmd+Shift+K` | `Ctrl+Shift+K` | Toggle jiggler on/off |
| `Cmd+Shift+Q` | `Ctrl+Shift+Q` | Quit app |

> **Note:** On macOS, `keyboard` library requires Accessibility permissions. Show a one-time dialog on first run prompting the user to grant this in System Preferences → Privacy & Security → Accessibility. If permission denied, hotkeys are silently disabled (tray menu still works fully).

- Detect OS with `platform.system()` — use `ctrl` on Windows, `cmd` on macOS
- Register hotkeys in a separate daemon thread so they don't block the tray loop
- Expose `register(toggle_fn, quit_fn)` and `unregister()` functions

### `main.py`

```
1. Create jiggler instance, start it
2. Register hotkeys (toggle = jiggler.toggle, quit = graceful_exit)
3. Build and run tray icon (blocking call — this is the main loop)
4. On exit: stop jiggler thread, unregister hotkeys, exit cleanly
```

---

## User-Facing Behaviour

### On Launch
- App starts in tray, jiggler is **ON** by default
- Tray icon is green
- macOS: Brief notification "Teams Keep-Alive is running. Press ⌘⇧K to toggle."
- Windows: Brief balloon tip with same message

### Toggle (hotkey or tray menu)
- Jiggler thread pauses/resumes
- Tray icon switches green ↔ grey
- Notification/tooltip briefly shows new state

### Interval Change
- Selecting interval from submenu restarts jiggler with new interval immediately
- Persist last-used interval to `~/.teams-keepalive.json` so it survives restarts

### Quit
- Via tray → Quit, or hotkey `Cmd/Ctrl+Shift+Q`
- Stops thread, removes tray icon, exits process

---

## Settings Persistence

Save/load a tiny JSON file at `~/.teams-keepalive.json`:

```json
{
  "interval_seconds": 60,
  "start_on_launch": true
}
```

---

## Notifications

Use `plyer` library for cross-platform desktop notifications:
- On toggle: `"Teams Keep-Alive: Active ✓"` or `"Teams Keep-Alive: Paused ✗"`
- On quit: no notification (just exit)
- Keep notifications short — title only, no body text

---

## Packaging

### macOS — `build_mac.sh`

```bash
pyinstaller \
  --onefile \
  --windowed \
  --name "TeamsKeepAlive" \
  --osx-bundle-identifier com.keepalive.teams \
  main.py

# Output: dist/TeamsKeepAlive (single binary)
# User double-clicks or runs from terminal
```

### Windows — `build_windows.bat`

```bat
pyinstaller ^
  --onefile ^
  --windowed ^
  --name TeamsKeepAlive ^
  --icon icon.ico ^
  main.py

REM Output: dist\TeamsKeepAlive.exe
```

> **Note on `--windowed`**: Suppresses the terminal window on Windows. Required for clean UX.

---

## README.md Content (ship this with the binary)

```
# Teams Keep-Alive

Keeps Microsoft Teams from showing "Away" by gently nudging your mouse every 60 seconds.

## How to use

### macOS
1. Download TeamsKeepAlive
2. Double-click to run (or: open Terminal → ./TeamsKeepAlive)
3. Look for the green dot in your menu bar

### Windows
1. Download TeamsKeepAlive.exe
2. Double-click to run
3. Look for the green dot in your system tray (bottom right)

## Shortcuts

| Action         | Mac         | Windows          |
|----------------|-------------|------------------|
| Toggle on/off  | ⌘ ⇧ K      | Ctrl + Shift + K |
| Quit           | ⌘ ⇧ Q      | Ctrl + Shift + Q |

You can also right-click the tray icon for the full menu.

## First run on macOS
If hotkeys don't work, go to:
System Preferences → Privacy & Security → Accessibility → enable TeamsKeepAlive

## Notes
- The mouse moves by 1 pixel and immediately returns — you won't notice it
- No data is collected or sent anywhere
- Settings saved to ~/.teams-keepalive.json
```

---

## requirements.txt

```
pyautogui>=0.9.54
pystray>=0.19.5
Pillow>=10.0.0
keyboard>=0.13.5
plyer>=2.1.0
pyinstaller>=6.0.0
```

---

## Edge Cases to Handle

| Scenario | Handling |
|----------|----------|
| macOS Accessibility permission denied | Disable hotkeys silently, log to stderr, tray still works |
| pyautogui fails (Wayland/headless) | Catch exception, show error notification, exit gracefully |
| Multiple instances launched | Check for lockfile `~/.teams-keepalive.lock`, show "already running" notification and exit |
| Machine goes to sleep | On wake, jiggler thread resumes automatically (thread sleep wakes up, checks flag, continues) |
| User is typing/clicking during jiggle | pyautogui jiggle is 1px + immediate return — imperceptible in practice |

---

## Out of Scope

- No GUI config window (tray menu is sufficient)
- No autostart on login (tell users to drag to Login Items / Startup folder manually)
- No Teams API integration
- No installer (.dmg / .msi) — plain binary only for simplicity
