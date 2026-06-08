# Teams Keep-Alive

Keeps Microsoft Teams from showing "Away" by gently nudging your mouse every 60 seconds.

## How to use

### macOS
1. Download TeamsKeepAlive
2. Double-click to run (or: open Terminal → `./TeamsKeepAlive`)
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
System Settings → Privacy & Security → Accessibility → enable **TeamsKeepAlive** (or **Terminal** / **Python** when running from source)

## Notes
- The mouse moves by 1 pixel and immediately returns — you won't notice it
- No data is collected or sent anywhere
- Settings saved to `~/.teams-keepalive.json`
- Each jiggle is logged to `~/.teams-keepalive.log`

## Testing / tuning

Edit `~/.teams-keepalive.json` (create it if missing):

```json
{
  "interval_seconds": 10,
  "jiggle_pixels": 10
}
```

- `interval_seconds` — how often to jiggle (use `10` for quick testing)
- `jiggle_pixels` — how far the cursor moves (default `1`; try `10` to see it clearly)

Restart the app after editing. Set `jiggle_pixels` back to `1` for normal use.

## Development

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Build standalone binary:

- macOS: `./build_mac.sh`
- Windows: `build_windows.bat`
