import json
from pathlib import Path

SETTINGS_PATH = Path.home() / ".teams-keepalive.json"
LOG_PATH = Path.home() / ".teams-keepalive.log"
DEFAULT_SETTINGS = {
    "interval_seconds": 60,
    "start_on_launch": True,
    "accessibility_prompted": False,
    "jiggle_pixels": 1,
}

VALID_INTERVALS = (10, 30, 60, 120, 300)


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        return DEFAULT_SETTINGS.copy()
    try:
        with SETTINGS_PATH.open() as f:
            data = json.load(f)
        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)
        if settings["interval_seconds"] not in VALID_INTERVALS:
            settings["interval_seconds"] = 60
        return settings
    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    try:
        with SETTINGS_PATH.open("w") as f:
            json.dump(settings, f, indent=2)
    except OSError:
        pass
