# Teams Keep-Alive

Keeps Microsoft Teams from showing **Away** by gently nudging your mouse every 60 seconds. Runs in the background — no window, only a tray icon.

---

## Index

| Section | For |
|---------|-----|
| [What it does](#what-it-does) | Everyone |
| [First-time setup (common)](#first-time-setup-common) | Everyone |
| [macOS — first-time setup](#macos--first-time-setup) | Mac users |
| [Windows — first-time setup](#windows--first-time-setup) | Windows users |
| [Daily use](#daily-use) | Everyone |
| [Settings & log files](#settings--log-files) | Everyone |
| [Testing / tuning](#testing--tuning) | Everyone |
| [Build from source](#build-from-source) | Developers |
| [Known issues & troubleshooting](#known-issues--troubleshooting) | Everyone |

---

## What it does

- Moves your mouse **1 pixel** and immediately back on a timer (default: every **60 seconds**)
- Teams sees that as activity and keeps your status **Available**
- Shows a **green dot** in the tray when active, **grey** when paused
- Does not connect to Teams, the network, or any account — everything stays on your machine

---

## First-time setup (common)

These steps apply on **both** Mac and Windows.

### 1. Get the app

Use the pre-built binary (recommended):

| Platform | File to run |
|----------|-------------|
| macOS | `TeamsKeepAlive.app` |
| Windows | `TeamsKeepAlive.exe` |

Or [build it yourself](#build-from-source) from this repo.

### 2. Start it

- **Do not** double-click `main.py` — that opens editors and behaves oddly on Mac
- Run the **built app** (`.app` or `.exe`) by double-clicking it

### 3. Confirm it is running

You should see:

1. A short desktop **notification** (“Teams Keep-Alive is running…”)
2. A **green dot** in the system tray / menu bar
3. **No** main window

### 4. Optional — try the shortcuts

| Action | Mac | Windows |
|--------|-----|---------|
| Toggle on/off | ⌘ Shift K | Ctrl + Shift + K |
| Quit | ⌘ Shift Q | Ctrl + Shift + Q |

You can always use the **tray menu** instead (right-click the dot).

### 5. When you are done

Right-click the tray icon → **Quit**, or use the quit shortcut above.

---

## macOS — first-time setup

### Step 1 — Run the app

**Recommended:** double-click `dist/TeamsKeepAlive.app`

**From Terminal (development):**
```bash
cd /path/to/teams-bot
source .venv/bin/activate
python main.py
```

> Do **not** double-click `main.py` in Finder — macOS may open Script Editor and Python separately.

### Step 2 — Find the tray icon

Look at the **top menu bar** (right side, near the clock) for a small **green dot**.

### Step 3 — Allow permissions (if prompted)

**Accessibility** (for keyboard shortcuts ⌘⇧K / ⌘⇧Q):

1. Open **System Settings**
2. **Privacy & Security** → **Accessibility**
3. Enable **TeamsKeepAlive** (or **Terminal** / **Python** if running from source)
4. Quit and restart the app

The tray menu works even if shortcuts are not granted.

### Step 4 — Verify it works

```bash
tail -f ~/.teams-keepalive.log
```

You should see a new line every time the mouse jiggles (e.g. every 60 seconds).

### macOS build output

`./build_mac.sh` creates two files — they are the **same app**:

| File | Use |
|------|-----|
| `dist/TeamsKeepAlive.app` | Double-click this |
| `dist/TeamsKeepAlive` | Terminal executable (optional) |

---

## Windows — first-time setup

### Step 1 — Run the app

Double-click `dist\TeamsKeepAlive.exe`

**From Command Prompt (development):**
```bat
cd C:\path\to\teams-bot
.venv\Scripts\activate
python main.py
```

### Step 2 — Find the tray icon

Look at the **system tray** (bottom-right, near the clock) for a small **green dot**.

If you do not see it, click the **^** (hidden icons) arrow — Windows may hide new tray icons there.

### Step 3 — Allow through security prompts (if shown)

Windows may block an unsigned `.exe` the first time:

1. If **SmartScreen** appears → **More info** → **Run anyway**
2. If **Windows Defender** quarantines it → add an exclusion or allow the file in your antivirus settings

No administrator rights are required for normal use.

### Step 4 — Verify it works

Open PowerShell or Command Prompt:

```bat
type %USERPROFILE%\.teams-keepalive.log
```

Or watch live:

```bat
powershell -Command "Get-Content $env:USERPROFILE\.teams-keepalive.log -Wait -Tail 5"
```

You should see a new line every time the mouse jiggles.

### Windows build output

`build_windows.bat` creates:

| File | Use |
|------|-----|
| `dist\TeamsKeepAlive.exe` | Double-click this |

---

## Daily use

### Tray menu (right-click the dot)

| Item | What it does |
|------|----------------|
| Status | Shows Active or Paused |
| Start / Stop | Toggle jiggling |
| Interval | 10s, 30s, 60s (default), 120s, 300s |
| Quit | Stop the app completely |

### How to stop the app

1. Tray icon → **Quit**
2. Shortcut: ⌘⇧Q (Mac) or Ctrl+Shift+Q (Windows)
3. If started from Terminal / Command Prompt: **Ctrl+C**
4. Last resort: Task Manager (Windows) or Activity Monitor (Mac) → end `TeamsKeepAlive` or `Python`

### Only one instance

If you start it twice, the second copy shows **“Already running”** and exits. Quit the first instance before starting again.

---

## Settings & log files

| File | Location (Mac) | Location (Windows) |
|------|----------------|-------------------|
| Settings | `~/.teams-keepalive.json` | `C:\Users\<You>\.teams-keepalive.json` |
| Activity log | `~/.teams-keepalive.log` | `C:\Users\<You>\.teams-keepalive.log` |
| Lock file | `~/.teams-keepalive.lock` | `C:\Users\<You>\.teams-keepalive.lock` |

**Settings example** (create or edit the JSON file):

```json
{
  "interval_seconds": 60,
  "start_on_launch": true,
  "jiggle_pixels": 1
}
```

**Log example** (one line per jiggle):

```
2026-06-08T12:34:56 jiggled (842, 512) +1px
```

Restart the app after changing settings.

---

## Testing / tuning

To **see** the jiggle clearly, edit your settings file:

```json
{
  "interval_seconds": 10,
  "jiggle_pixels": 10
}
```

| Setting | Default | Purpose |
|---------|---------|---------|
| `interval_seconds` | `60` | Seconds between jiggles (use `10` for quick tests) |
| `jiggle_pixels` | `1` | How far the cursor moves (`10` is easy to see) |
| `start_on_launch` | `true` | Start jiggling immediately when the app opens |

Set `jiggle_pixels` back to `1` when finished testing.

---

## Build from source

Requires **Python 3.11+**.

### macOS

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py          # run from source
./build_mac.sh          # build → dist/TeamsKeepAlive.app
```

### Windows

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py          REM run from source
build_windows.bat       REM build → dist\TeamsKeepAlive.exe
```

---

## Known issues & troubleshooting

### macOS

| Issue | What to do |
|-------|------------|
| Script Editor + Python icon open when I start the app | You double-clicked `main.py`. Use `TeamsKeepAlive.app` or run `python main.py` from Terminal instead. |
| Keyboard shortcuts do nothing | Grant **Accessibility** for TeamsKeepAlive (or Terminal/Python) in System Settings → Privacy & Security → Accessibility. Restart the app. |
| “App can’t be opened” / Gatekeeper block | Right-click the app → **Open**, or System Settings → Privacy & Security → allow it. |
| No tray icon visible | Check the right side of the menu bar; other menu bar apps may crowd it. |
| Mouse does not move | Grant accessibility-related permissions if prompted; check `~/.teams-keepalive.log` for errors. |

### Windows

| Issue | What to do |
|-------|------------|
| SmartScreen blocks the `.exe` | Click **More info** → **Run anyway**, or build/run from source yourself. |
| Tray icon not visible | Click the **^** arrow in the system tray to show hidden icons. |
| Keyboard shortcuts do nothing | Another app may use Ctrl+Shift+K/Q; use the tray menu instead. Try running the app once as a normal user (not required to be admin). |
| Antivirus removes the `.exe` | Add `TeamsKeepAlive.exe` to your antivirus allow/exclusion list. |
| Mouse does not move | Check `%USERPROFILE%\.teams-keepalive.log`; remote desktop or locked sessions may limit mouse control. |

### Both platforms

| Issue | What to do |
|-------|------------|
| “Already running” notification | Another copy is still active. Quit it from the tray or Task Manager / Activity Monitor. |
| App starts but Teams still shows Away | Confirm the tray icon is **green** (Active). Teams may take a minute to update. Shorten `interval_seconds` to test. |
| Want to autostart on login | **Mac:** System Settings → General → Login Items → add `TeamsKeepAlive.app`. **Windows:** Win+R → `shell:startup` → place a shortcut to `TeamsKeepAlive.exe`. |
| Log file not updating | App may be **Paused** (grey icon). Click **Start** in the tray menu. |
| Changes to settings ignored | Restart the app after editing the JSON file. |

---

## Privacy

- No data is collected or sent anywhere
- Settings and logs stay in your home folder on your machine only
