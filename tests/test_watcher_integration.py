import time
import shutil

from watchdog.observers import Observer
from pathlib import Path
from src.actions import MoveAction, CopyAction, PrefixRenamingAction, ReplaceTextAction, ChangeExtensionAction
from src.conditions import ExtensionCondition
from src.history import HistoryStore
from src.rules import Rule
from src.watcher import WatcherHandler
from threading import Lock

def wait_until(predicate, timeout=2.0):
    """Helper to poll until predicate returns True or the timeout expires"""
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        if predicate():
            return True
        time.sleep(0.05)
    return False

def test_cross_folder_loop_is_suppressed_move(tmp_path):
    """Verify that two watched folders cannot bounce the same file forever when doing a move"""
    folder_a = tmp_path / "a"
    folder_b = tmp_path / "b"

    folder_a.mkdir()
    folder_b.mkdir()

    # create the 2 observers that will in theory bounce between another
    history = HistoryStore(tmp_path / "history.jsonl")
    rule_a = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[MoveAction(folder_b)],
        watch_folder=folder_a,
        name="A to B",
    )
    rule_b = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[MoveAction(folder_a)],
        watch_folder=folder_b,
        name="B to A",
    )
    recently_processed = {}
    recently_processed_lock = Lock()
    handler_a = WatcherHandler([rule_a], history, recently_processed, recently_processed_lock)
    handler_b = WatcherHandler([rule_b], history, recently_processed, recently_processed_lock)
    observer = Observer()
    observer.schedule(handler_a, path=str(folder_a), recursive=False)
    observer.schedule(handler_b, path=str(folder_b), recursive=False)

    observer.start()

    try:
        # create the file that will trigger this event
        source = folder_a / "test.txt"
        source.write_text("hello")
        destination = folder_b / "test.txt"

        # confirm the initial rule applied at some point
        assert wait_until(lambda: destination.exists())

        # give watchdog a short opportunity to emit any follow-up events
        time.sleep(0.25)

        # confirm the files look correct for if 1 rule executed
        assert destination.exists()
        assert not source.exists()

        # confirm that exactly 1 rule exeucted
        entries = history.get_recent(10)
        assert len(entries) == 1
        assert entries[0].rule_name == "A to B"

    finally:
        observer.stop()
        observer.join()

def test_cross_folder_loop_is_suppressed_copy(tmp_path):
    """Verify that two watched folders cannot bounce the same file forever when doing a copy"""
    folder_a = tmp_path / "a"
    folder_b = tmp_path / "b"

    folder_a.mkdir()
    folder_b.mkdir()

    # create the 2 observers that will in theory bounce between another
    history = HistoryStore(tmp_path / "history.jsonl")
    rule_a = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[CopyAction(folder_b)],
        watch_folder=folder_a,
        name="A to B",
    )
    rule_b = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[CopyAction(folder_a)],
        watch_folder=folder_b,
        name="B to A",
    )
    recently_processed = {}
    recently_processed_lock = Lock()
    handler_a = WatcherHandler([rule_a], history, recently_processed, recently_processed_lock)
    handler_b = WatcherHandler([rule_b], history, recently_processed, recently_processed_lock)
    observer = Observer()
    observer.schedule(handler_a, path=str(folder_a), recursive=False)
    observer.schedule(handler_b, path=str(folder_b), recursive=False)

    observer.start()

    try:
        # create the file that will trigger this event
        source = folder_a / "test.txt"
        source.write_text("hello")
        destination = folder_b / "test.txt"

        # confirm the initial rule applied at some point
        assert wait_until(lambda: destination.exists())

        # give watchdog a short opportunity to emit any follow-up events
        time.sleep(0.25)

        # confirm the files look correct for if 1 rule executed
        assert destination.exists()
        assert source.exists()

        # confirm that exactly 1 rule exeucted
        entries = history.get_recent(10)
        assert len(entries) == 1
        assert entries[0].rule_name == "A to B"

    finally:
        observer.stop()
        observer.join()

def test_file_moved_triggers_watcher(tmp_path):
    """Verify that moving events can be processed by the watcher"""
    watched_folder = tmp_path / "a"
    original_folder = tmp_path / "b"

    watched_folder.mkdir()
    original_folder.mkdir()

    # create the 2 observers that will in theory bounce between another
    history = HistoryStore(tmp_path / "history.jsonl")
    rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[PrefixRenamingAction("seen_")],
        watch_folder=watched_folder,
        name="A to B",
    )
    recently_processed = {}
    recently_processed_lock = Lock()
    handler = WatcherHandler([rule], history, recently_processed, recently_processed_lock)
    observer = Observer()
    observer.schedule(handler, path=str(watched_folder), recursive=False)

    observer.start()

    try:
        # create the file that will trigger this event
        source = original_folder / "test.txt"
        source.write_text("hello")
        expected_result = watched_folder / "seen_test.txt"
        shutil.move(source, watched_folder / "test.txt")

        # confirm the files look correct for if 1 rule executed
        assert wait_until(lambda: expected_result.exists())
        assert not Path(watched_folder / "test.txt").exists()
        assert not source.exists()

    finally:
        observer.stop()
        observer.join()


def test_file_moved_sibling_dir_triggers_watcher(tmp_path):
    """Verify that moving events can be processed by the watcher when moving from a child folder to another"""
    new_folder = tmp_path / "a"
    original_folder = tmp_path / "b"

    new_folder.mkdir()
    original_folder.mkdir()

    # create the 2 observers that will in theory bounce between another
    history = HistoryStore(tmp_path / "history.jsonl")
    rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[PrefixRenamingAction("seen_")],
        watch_folder=tmp_path,
        name="A to B",
        recursive=True
    )
    recently_processed = {}
    recently_processed_lock = Lock()
    handler = WatcherHandler([rule], history, recently_processed, recently_processed_lock)
    observer = Observer()
    observer.schedule(handler, path=str(tmp_path), recursive=True)

    try:
        # create the file that will trigger this event
        source = original_folder / "test.txt"
        source.write_text("hello")
        observer.start()

        expected_result = new_folder / "seen_test.txt"
        shutil.move(source, new_folder / "test.txt")

        # confirm the files look correct for if 1 rule executed
        assert wait_until(lambda: expected_result.exists())
        assert not Path(new_folder / "test.txt").exists()
        assert not source.exists()

    finally:
        observer.stop()
        observer.join()

def test_overlapping_recursive_and_child_watch_only_processes_file_once(tmp_path):
    """Verify overlapping watches do not process the same filesystem event twice."""
    # create folders and files
    parent_folder = tmp_path / "sandbox"
    child_folder = parent_folder / "images"
    parent_destination = tmp_path / "parent_destination"
    child_destination = tmp_path / "child_destination"
    child_folder.mkdir(parents=True)
    parent_destination.mkdir()
    child_destination.mkdir()

    # create overlapping rules
    parent_rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[MoveAction(parent_destination)],
        watch_folder=parent_folder,
        name="parent_rule",
        recursive=True,
    )
    child_rule = Rule(
        condition=ExtensionCondition(".txt"),
        actions=[MoveAction(child_destination)],
        watch_folder=child_folder,
        name="child_rule",
        recursive=False,
    )

    # create handlers and watchers
    history = HistoryStore(tmp_path / "history.jsonl")
    recently_processed = {}
    recently_processed_lock = Lock()
    parent_handler = WatcherHandler(
        [parent_rule],
        history,
        recently_processed,
        recently_processed_lock
    )
    child_handler = WatcherHandler(
        [child_rule],
        history,
        recently_processed,
        recently_processed_lock
    )
    observer = Observer()
    observer.schedule(
        parent_handler,
        str(parent_folder),
        recursive=True,
    )
    observer.schedule(
        child_handler,
        str(child_folder),
        recursive=False,
    )
    observer.start()

    # create the conflicting file
    try:
        source = child_folder / "test.txt"
        source.write_text("test")

        # wait for watchdog to process the event
        deadline = time.time() + 3

        while time.time() < deadline:
            if (
                (parent_destination / "test.txt").exists()
                or (child_destination / "test.txt").exists()
            ):
                break

            time.sleep(0.05)

        # give any duplicate event enough time to occur
        time.sleep(0.5)

        entries = history.get_recent(10)

        assert len(entries) == 1
        assert entries[0].success

        parent_result = parent_destination / "test.txt"
        child_result = child_destination / "test.txt"

        # exactly one rule should have processed the file
        assert parent_result.exists() != child_result.exists()

    finally:
        observer.stop()
        observer.join()

def test_several_actions_do_not_trigger_watcher_processing(tmp_path):
    """Verify that if a rule's action sequnce renames a file in the middle, it will not get processed again."""
    watch_dir = tmp_path / "watch"
    watch_dir.mkdir()

    history = HistoryStore(tmp_path / "history.jsonl")

    rule = Rule(
        condition=ExtensionCondition(".notes"),
        actions=[
            ReplaceTextAction("notes", "pdf", first_instance_only=False),
            ChangeExtensionAction(".pdf"),
        ],
        watch_folder=watch_dir,
        name="make_pdf",
    )

    recently_processed = {}
    recently_processed_lock = Lock()

    handler = WatcherHandler(
        [rule],
        history,
        recently_processed,
        recently_processed_lock,
    )

    observer = Observer()
    observer.schedule(
        handler,
        path=str(watch_dir),
        recursive=False,
    )
    observer.start()

    try:
        source = watch_dir / "notesnotes.notes"
        source.write_text("hello")

        final_file = watch_dir / "pdfpdf.pdf"

        timeout = time.time() + 0.1
        while not final_file.exists() and time.time() < timeout:
            time.sleep(0.05)
        time.sleep(0.1)

        assert final_file.exists()
        assert final_file.read_text() == "hello"

        assert not source.exists()
        assert not (watch_dir / "pdfpdf.notes").exists()

        entries = history.get_recent(10)

        assert len(entries) == 1
        assert entries[0].success is True
        assert entries[0].rule_name == "make_pdf"
        assert entries[0].original_path == source
        assert entries[0].final_path == final_file

    finally:
        observer.stop()
        observer.join()