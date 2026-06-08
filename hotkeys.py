import platform
import subprocess
import sys
import threading

_hotkeys = None


def show_macos_accessibility_prompt() -> None:
    script = (
        'display dialog "Teams Keep-Alive needs Accessibility access for keyboard shortcuts. '
        'Go to System Settings → Privacy & Security → Accessibility and enable TeamsKeepAlive '
        '(or Terminal / Python if running from source)." '
        'buttons {"OK"} default button "OK" with title "Teams Keep-Alive"'
    )
    try:
        subprocess.run(["osascript", "-e", script], check=False)
    except OSError:
        print(
            "Grant Accessibility access in System Settings → Privacy & Security → Accessibility",
            file=sys.stderr,
        )


def register(toggle_fn, quit_fn, *, accessibility_prompted: bool = False) -> bool:
    global _hotkeys

    if _hotkeys is not None:
        return True

    is_mac = platform.system() == "Darwin"
    mod = "cmd" if is_mac else "ctrl"
    combo = {
        f"<{mod}>+<shift>+k": toggle_fn,
        f"<{mod}>+<shift>+q": quit_fn,
    }

    def _setup():
        global _hotkeys
        try:
            from pynput import keyboard

            _hotkeys = keyboard.GlobalHotKeys(combo)
            _hotkeys.start()
        except Exception as exc:
            print(f"hotkeys disabled: {exc}", file=sys.stderr)
            if is_mac and not accessibility_prompted:
                show_macos_accessibility_prompt()

    threading.Thread(target=_setup, daemon=True).start()
    return True


def unregister() -> None:
    global _hotkeys
    if _hotkeys is None:
        return
    try:
        _hotkeys.stop()
    except Exception:
        pass
    _hotkeys = None
