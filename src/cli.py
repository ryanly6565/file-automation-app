import sys
import time

from watchdog.observers import Observer

from src.config_loader import load_rules
from src.history import HistoryStore
from src.ui import group_rules_by_folder
from src.watcher import WatcherHandler
from src.apps_path import HISTORY_PATH
from pathlib import Path
from threading import Lock

def main():
    # command arg handling
    if len(sys.argv) != 2:
        print("Usage: python -m src.cli <rules.json>")
        return
    rules_file = Path(sys.argv[1])

    if not rules_file.exists():
        print(f"Rules file does not exist: {rules_file}")
        return

    if not rules_file.is_file():
        print(f"Rules path is not a file: {rules_file}")
        return

    # try to load user rules
    try:
        rules = load_rules(rules_file)
    except Exception as e:
        print(f"Failed to load rules: {e}")
        return

    # set up history and observer
    history = HistoryStore(HISTORY_PATH)
    observer = Observer()

    # group rules by folder and assign handler for each folder
    rules_by_folder = group_rules_by_folder(rules)
    for folder in rules_by_folder:
        folder = Path(folder)

        if not folder.exists() or not folder.is_dir():
            folder_name = str(folder)
            if sys.platform != "win32" and "\\" in folder_name:
                print(
                    f"Watch folder does not exist: {folder}\n"
                    "This path looks like it may use Windows-style separators.\nEdit the rule and select a Linux path."
                )

            elif sys.platform == "win32" and folder_name.startswith("/"):
                print(
                    f"Watch folder does not exist: {folder}\n"
                    "This path looks like it may be a Linux-style path.\nEdit the rule and select a Windows folder."
                )

            else:
                print(f"Watch folder does not exist: {folder}")

            return
    
    recently_processed = {}
    recently_processed_lock = Lock()
    for folder, folder_rules in rules_by_folder.items():
        handler = WatcherHandler(
            folder_rules,
            history,
            recently_processed,
            recently_processed_lock
        )

        recursive = any(
            rule.recursive
            for rule in folder_rules
        )

        observer.schedule(
            handler,
            path=folder,
            recursive=recursive,
        )

    try:
        observer.start()
        print(
            f"Watching {len(rules_by_folder)} folder(s). "
            "Press Ctrl+C to stop."
        )
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping...")

    except Exception as e:
        print(f"Failed to start watcher: {e}")

    finally:
        if observer.is_alive():
            observer.stop()
            observer.join()

if __name__ == "__main__":
    main()