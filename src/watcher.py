from watchdog.events import FileSystemEventHandler
from src.rules import Rule
from pathlib import Path
from src.logger import get_logger
from src.history import HistoryEntry, HistoryStore
from src.actions import ActionResult
import datetime
import time

class WatcherHandler(FileSystemEventHandler):
    def __init__(self, rules: list[Rule], history: HistoryStore, recently_processed: dict, recently_processed_lock):
        self.rules = rules
        self.logger = get_logger()
        self.history = history
        self.recently_processed = recently_processed
        self.recently_processed_lock = recently_processed_lock
        self.cooldown_seconds = 2.0

    def on_created(self, event):
        # directories are ignored
        if event.is_directory:
            return
        path = Path(event.src_path)
        self.process_path(path)

    def on_moved(self, event):
        # directories are ignored
        if event.is_directory:
            return
        path = Path(event.dest_path)
        self.process_path(path)

    def update_rules(self, rules: list[Rule]) -> None:
        self.rules = rules

    def process_path(self, path: Path):
        self.prune_recently_processed()

        matching_rule = None
        for rule in self.rules:
            if rule_applies(rule, path):
                matching_rule = rule
                break
            
        if matching_rule is None:
            return


        if not self.claim_path(path):
            return
        
        self.logger.info(
            'Rule: "%s" matches "%s".',
            matching_rule.name,
            path
        )

        try:
            result = matching_rule.execute(path, on_action_complete=self.mark_result)
            self.mark_processed(result.current_path)
            for generated_path in result.generated_paths:
                self.mark_processed(generated_path)

        except Exception as e:
            self.logger.exception(
                'Failed to execute rule: "%s" on %s.',
                matching_rule.name,
                path
            )

            self.history.add(
                HistoryEntry(
                    timestamp=datetime.datetime.now(),
                    rule_name=matching_rule.name,
                    original_path=path,
                    final_path=None,
                    success=False,
                    error=str(e),
                )
            )

        else:
            self.logger.info(
                'Rule "%s" executed successfully | input="%s" | final="%s"',
                matching_rule.name,
                path,
                result.current_path
            )

            self.history.add(
                HistoryEntry(
                    timestamp=datetime.datetime.now(),
                    rule_name=matching_rule.name,
                    original_path=path,
                    final_path=result.current_path,
                    success=True,
                    error=None,
                )
            )

    def mark_processed(self, path: Path) -> None:
        """Marks a path as being recently processed."""
        with self.recently_processed_lock:
            self.recently_processed[path.resolve()] = time.monotonic()

    def prune_recently_processed(self) -> None:
        """Loops through recently processed dict and removes any expired nodes """
        with self.recently_processed_lock:
            expired_paths = []
            now = time.monotonic()
            for path, last_processed in self.recently_processed.items():
                if now - last_processed >= self.cooldown_seconds:
                    expired_paths.append(path)
            for path in expired_paths:
                self.recently_processed.pop(path)

    def claim_path(self, path: Path) -> bool:
        """Claim a path so only one handler processes it."""
        path = path.resolve()
        now = time.monotonic()

        with self.recently_processed_lock:
            # try and claim this path (assuming it is not on cooldown)
            last_processed = self.recently_processed.get(path)
            if (last_processed is not None and now - last_processed < self.cooldown_seconds):
                return False

            self.recently_processed[path] = now
            return True

    def mark_result(self, result: ActionResult) -> None:
        """Helper for marking all paths in the given result. """
        self.mark_processed(result.current_path)

        for generated_path in result.generated_paths:
            self.mark_processed(generated_path)

def rule_applies(rule: Rule, path: Path) -> bool:
    """Checks if a path matches a rule, including factors like recursiveness"""
    watch_folder = rule.watch_folder.resolve()
    path = path.resolve()

    if rule.recursive:
        if watch_folder not in path.parents:
            return False
    else:
        if path.parent != watch_folder:
            return False

    return rule.matches(path)


