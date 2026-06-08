import atexit
import os
import subprocess
import sys
import threading
from pathlib import Path

from jiggler import Jiggler
from settings import load_settings, save_settings
from tray import TrayApp

LOCKFILE = Path.home() / ".teams-keepalive.lock"
_lock_handle = None


def notify(title: str) -> None:
    safe = title.replace("\\", "\\\\").replace('"', '\\"')
    if sys.platform == "darwin":
        try:
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    f'display notification "{safe}" with title "Teams Keep-Alive"',
                ],
                check=False,
            )
            return
        except OSError:
            pass
    try:
        from plyer import notification

        notification.notify(title=title, timeout=3)
    except Exception:
        pass


def acquire_lock():
    global _lock_handle
    LOCKFILE.parent.mkdir(parents=True, exist_ok=True)
    handle = open(LOCKFILE, "w")
    try:
        if sys.platform == "win32":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (OSError, BlockingIOError):
        handle.close()
        return False
    handle.write(str(os.getpid()))
    handle.flush()
    _lock_handle = handle
    return True


def release_lock():
    global _lock_handle
    if _lock_handle:
        try:
            if sys.platform != "win32":
                import fcntl

                fcntl.flock(_lock_handle.fileno(), fcntl.LOCK_UN)
            _lock_handle.close()
        except OSError:
            pass
        _lock_handle = None
    try:
        LOCKFILE.unlink(missing_ok=True)
    except OSError:
        pass


def main() -> None:
    if not acquire_lock():
        notify("Teams Keep-Alive: Already running")
        sys.exit(0)

    atexit.register(release_lock)

    settings = load_settings()
    jiggler = Jiggler(
        interval_seconds=settings["interval_seconds"],
        jiggle_pixels=settings.get("jiggle_pixels", 1),
    )

    if settings.get("start_on_launch", True):
        jiggler.start()

    tray_app: TrayApp | None = None

    def on_interval_change(seconds: int) -> None:
        settings["interval_seconds"] = seconds
        save_settings(settings)
        jiggler.set_interval(seconds)
        if jiggler.is_running():
            jiggler.stop()
            jiggler.start()

    def on_toggle_notify(active: bool) -> None:
        if active:
            notify("Teams Keep-Alive: Active ✓")
        else:
            notify("Teams Keep-Alive: Paused ✗")

    def on_hotkey_toggle() -> None:
        on_toggle_notify(jiggler.toggle())
        if tray_app:
            tray_app.refresh()

    def graceful_exit() -> None:
        from hotkeys import unregister

        unregister()
        jiggler.shutdown()
        release_lock()
        if tray_app:
            tray_app.stop()
        sys.exit(0)

    from hotkeys import register

    prompted = settings.get("accessibility_prompted", False)
    register(on_hotkey_toggle, graceful_exit, accessibility_prompted=prompted)
    if not prompted and sys.platform == "darwin":
        from hotkeys import show_macos_accessibility_prompt

        threading.Timer(1.0, show_macos_accessibility_prompt).start()
        settings["accessibility_prompted"] = True
        save_settings(settings)

    shortcut_hint = "⌘⇧K" if sys.platform == "darwin" else "Ctrl+Shift+K"
    notify(f"Teams Keep-Alive is running. Press {shortcut_hint} to toggle.")

    tray_app = TrayApp(
        jiggler,
        settings,
        on_interval_change,
        graceful_exit,
        on_toggle_notify,
    )

    try:
        tray_app.run()
    except Exception as exc:
        notify(f"Teams Keep-Alive error: {exc}")
        print(f"fatal error: {exc}", file=sys.stderr)
    finally:
        from hotkeys import unregister

        unregister()
        jiggler.shutdown()
        release_lock()

    if jiggler.last_error:
        notify("Teams Keep-Alive: Mouse control unavailable")
        sys.exit(1)


if __name__ == "__main__":
    main()
