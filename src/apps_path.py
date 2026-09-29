import os
import sys
from pathlib import Path

APP_NAME = "FileAutomationApp"

def get_data_directory() -> Path:
    """Function for automatically separating the file paths of Windows and Linux rules.config."""
    if sys.platform == "win32":
        base_dir = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base_dir = Path(os.environ.get("XDG_DATA_HOME", Path.home()  / ".local" / "share"))

    data_directory = base_dir / APP_NAME
    data_directory.mkdir(parents=True, exist_ok=True)
    return data_directory

DATA_DIR = get_data_directory()
RULES_PATH = DATA_DIR / "rules.json"
HISTORY_PATH = DATA_DIR / "history.jsonl"