import time
from src.watcher import WatcherHandler
from src.history import HistoryStore
from src.watcher import rule_applies
from src.rules import Rule
from src.conditions import ExtensionCondition
from pathlib import Path
from threading import Lock

def test_mark_processed_adds_path(tmp_path):
    """Verify that mark processed actually adds the pat to shared dict """
    shared = {}
    shared_lock = Lock()
    history = HistoryStore(tmp_path / "history.jsonl")
    handler = WatcherHandler([], history, shared, shared_lock)

    path = tmp_path / "test.txt"
    handler.mark_processed(path)
    assert path.resolve() in shared

def test_claim_path_recent_path(tmp_path):
    """Verify that claim_path ignores paths in the shared dict """
    shared = {}
    shared_lock = Lock()
    history = HistoryStore(tmp_path / "history.jsonl")

    handler = WatcherHandler([], history, shared, shared_lock)
    path = tmp_path / "test.txt"
    handler.mark_processed(path)
    assert not handler.claim_path(path) is True

def test_handlers_share_recently_processed_paths(tmp_path):
    """Verify that all handlers share the same processed paths """
    shared = {}
    shared_lock = Lock()
    history = HistoryStore(tmp_path / "history.jsonl")
    handler_a = WatcherHandler([], history, shared, shared_lock)
    handler_b = WatcherHandler([], history, shared, shared_lock)

    path = tmp_path / "test.txt"
    handler_a.mark_processed(path)
    assert not handler_b.claim_path(path)

def test_should_not_ignore_after_cooldown(tmp_path):
    """Verify that all handlers do not ignore a path after its cooldown passes """
    shared = {}
    shared_lock = Lock()
    history = HistoryStore(tmp_path / "history.jsonl")
    handler = WatcherHandler([], history, shared, shared_lock)

    path = tmp_path / "test.txt"
    resolved = path.resolve()
    old_time = time.monotonic() - 10
    shared[resolved] = old_time

    assert handler.claim_path(path)
    assert resolved in shared
    assert shared[resolved] > old_time

def test_recursive_rule_matches_nested_file(tmp_path):
    """Verify that recusive rules will try to match files in children folder"""
    watch_folder = tmp_path / "dir"
    nested_folder = watch_folder / "a" / "b"
    nested_folder.mkdir(parents=True)
    file = nested_folder / "test.txt"
    file.write_text("test")

    rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[],
        watch_folder=watch_folder,
        name="Recursive",
        recursive=True,
    )
    assert rule_applies(rule, file)

def test_recursive_rule_does_not_match_nested_file(tmp_path):
    """Verify that non-recusive rules will not try to match files in children folder"""
    watch_folder = tmp_path / "dir"
    nested_folder = watch_folder / "a" / "b"
    nested_folder.mkdir(parents=True)
    file = nested_folder / "test.txt"
    file.write_text("test")

    rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[],
        watch_folder=watch_folder,
        name="Recursive",
        recursive=False,
    )
    assert not rule_applies(rule, file)

def test_prune_recently_processed_removes_expired(tmp_path):
    """Verify that prune_recently_processed actually removes expired paths"""
    handler = WatcherHandler([], history=None, recently_processed={}, recently_processed_lock=Lock())

    expired_path = tmp_path / "old.txt"
    fresh_path = tmp_path / "fresh.txt"

    now = time.monotonic()

    handler.recently_processed[expired_path.resolve()] = (now - handler.cooldown_seconds - 10)

    handler.recently_processed[fresh_path.resolve()] = now

    handler.prune_recently_processed()

    assert expired_path.resolve() not in handler.recently_processed
    assert fresh_path.resolve() in handler.recently_processed