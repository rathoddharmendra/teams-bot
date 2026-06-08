import sys
import threading
import time
from datetime import datetime

import pyautogui

from settings import LOG_PATH

JIGGLE_INTERVAL_SECONDS = 60
JIGGLE_OFFSET = 1  # default; override via ~/.teams-keepalive.json → "jiggle_pixels"
JIGGLE_PAUSE = 0.1

pyautogui.FAILSAFE = False


def _log_jiggle(x: int, y: int, offset: int) -> None:
    line = f"{datetime.now().isoformat(timespec='seconds')} jiggled ({x}, {y}) +{offset}px\n"
    try:
        with LOG_PATH.open("a") as f:
            f.write(line)
    except OSError as exc:
        print(f"log write failed: {exc}", file=sys.stderr)


class Jiggler:
    def __init__(
        self,
        interval_seconds: int = JIGGLE_INTERVAL_SECONDS,
        jiggle_pixels: int = JIGGLE_OFFSET,
    ):
        self.interval_seconds = interval_seconds
        self.jiggle_pixels = jiggle_pixels
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._error: Exception | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            self._pause_event.clear()
            return
        self._stop_event.clear()
        self._pause_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._pause_event.set()

    def shutdown(self) -> None:
        self._stop_event.set()
        self._pause_event.clear()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def toggle(self) -> bool:
        if self.is_running():
            self.stop()
            return False
        self.start()
        return True

    def is_running(self) -> bool:
        return (
            self._thread is not None
            and self._thread.is_alive()
            and not self._pause_event.is_set()
        )

    def set_interval(self, seconds: int) -> None:
        self.interval_seconds = seconds

    @property
    def last_error(self) -> Exception | None:
        return self._error

    def _run(self) -> None:
        while not self._stop_event.is_set():
            if self._pause_event.is_set():
                if self._stop_event.wait(0.5):
                    break
                continue
            if self._stop_event.wait(self.interval_seconds):
                break
            if self._pause_event.is_set() or self._stop_event.is_set():
                continue
            try:
                x, y = pyautogui.position()
                offset = self.jiggle_pixels
                pyautogui.moveTo(x + offset, y, duration=0)
                time.sleep(JIGGLE_PAUSE)
                pyautogui.moveTo(x, y, duration=0)
                _log_jiggle(x, y, offset)
            except Exception as exc:
                self._error = exc
                print(f"jiggler error: {exc}", file=sys.stderr)
                self._stop_event.set()
                break
