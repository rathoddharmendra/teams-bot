import platform
import sys

import pystray
from PIL import Image

from icon import generate_icon
from settings import VALID_INTERVALS

IS_MAC = platform.system() == "Darwin"
TOGGLE_SHORTCUT = "⌘⇧K" if IS_MAC else "Ctrl+Shift+K"
QUIT_SHORTCUT = "⌘⇧Q" if IS_MAC else "Ctrl+Shift+Q"


class TrayApp:
    def __init__(self, jiggler, settings, on_interval_change, on_quit, notify_fn):
        self.jiggler = jiggler
        self.settings = settings
        self.on_interval_change = on_interval_change
        self.on_quit = on_quit
        self.notify_fn = notify_fn
        self._icon: pystray.Icon | None = None

    def _status_label(self, _item=None) -> str:
        if self.jiggler.is_running():
            return f"● Active — jiggling every {self.jiggler.interval_seconds}s"
        return "○ Paused"

    def _toggle_label(self, _item=None) -> str:
        return "Stop" if self.jiggler.is_running() else "Start"

    def _toggle(self, _icon=None, _item=None) -> None:
        active = self.jiggler.toggle()
        self.refresh()
        self.notify_fn(active)

    def _set_interval(self, seconds: int):
        def handler(_icon, _item):
            self.on_interval_change(seconds)
            self.refresh()

        return handler

    def _build_menu(self) -> pystray.Menu:
        interval_items = [
            pystray.MenuItem(
                f"{s}s{' (default)' if s == 60 else ''}",
                self._set_interval(s),
                checked=lambda item, s=s: self.jiggler.interval_seconds == s,
                radio=True,
            )
            for s in VALID_INTERVALS
        ]
        return pystray.Menu(
            pystray.MenuItem(self._status_label, None, enabled=False),
            pystray.MenuItem(self._toggle_label, self._toggle),
            pystray.MenuItem("Interval", pystray.Menu(*interval_items)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                f"Shortcuts: {TOGGLE_SHORTCUT} toggle, {QUIT_SHORTCUT} quit",
                None,
                enabled=False,
            ),
            pystray.MenuItem("Quit", self._quit),
        )

    def _quit(self, _icon=None, _item=None) -> None:
        self.on_quit()

    def refresh(self) -> None:
        if self._icon is None:
            return
        active = self.jiggler.is_running()
        self._icon.icon = generate_icon(active)
        self._icon.menu = self._build_menu()
        self._icon.title = "Teams Keep-Alive"

    def run(self) -> None:
        active = self.jiggler.is_running()
        self._icon = pystray.Icon(
            "Teams Keep-Alive",
            generate_icon(active),
            "Teams Keep-Alive",
            menu=self._build_menu(),
        )
        self._icon.run()

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()
