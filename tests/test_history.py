from src.config_loader import make_actions_from_json
from src.actions import *
from src.history import HistoryEntry, HistoryStore
import pytest
import datetime
from dataclasses import asdict

class TestHistoryEntry:
    def test_history_entry_stores_values(self):
        """Verify that storing a data entry works fine"""
        entry = HistoryEntry(
            timestamp=datetime.datetime.now(),
            rule_name="Sort Notes",
            original_path=Path("input.txt"),
            final_path=Path("sorted/input.txt"),
            success=True
        )

        assert entry.rule_name == "Sort Notes"
        assert entry.original_path == Path("input.txt")
        assert entry.final_path == Path("sorted/input.txt")
        assert entry.success is True
        assert entry.error is None

class TestHistoryStore:
    def test_history_store_adds_entry(self, tmp_path):
        history_file = tmp_path / "history.jsonl"
        store = HistoryStore(history_file)

        entry = HistoryEntry(
            timestamp=datetime.datetime.now(),
            rule_name="Sort Notes",
            original_path=Path("notes.txt"),
            final_path=Path("sorted/notes.txt"),
            success=True
        )

        store.add(entry)

        assert history_file.exists()

        lines = history_file.read_text().splitlines()
        assert len(lines) == 1

    def test_get_history_two_succeeds(self, tmp_path):
        history_file = tmp_path / "history.jsonl"
        store = HistoryStore(history_file)

        entry_1 = self.make_entry(store, "Rule 1", "notes.txt", "sorted/txt/notes.txt", True)
        entry_2 = self.make_entry(store, "Rule 2", "test.md", "sorted/md/test.md", True)
        entry_3 = self.make_entry(store, "Rule 3", "me.img", "sorted/images/me.img", True)

        assert history_file.exists()
        lines = history_file.read_text().splitlines()
        assert len(lines) == 3

        most_recent = store.get_recent(2)
        assert len(most_recent) == 2
        assert most_recent[0] == entry_2
        assert most_recent[1] == entry_3

    def test_get_history_more_than_size_succeeds(self, tmp_path):
        history_file = tmp_path / "history.jsonl"
        store = HistoryStore(history_file)

        entry_1 = self.make_entry(store, "Rule 1", "notes.txt", "sorted/txt/notes.txt", True)
        entry_2 = self.make_entry(store, "Rule 2", "test.md", "sorted/md/test.md", True)
        entry_3 = self.make_entry(store, "Rule 3", "me.img", "sorted/images/me.img", True)

        assert history_file.exists()
        lines = history_file.read_text().splitlines()
        assert len(lines) == 3

        most_recent = store.get_recent(10)
        assert len(most_recent) == 3
        assert most_recent[0] == entry_1
        assert most_recent[1] == entry_2
        assert most_recent[2] == entry_3

    def test_get_history_one_returns_newest(self, tmp_path):
        history_file = tmp_path / "history.jsonl"
        store = HistoryStore(history_file)

        entry_1 = self.make_entry(store, "Rule 1", "notes.txt", "sorted/txt/notes.txt", True)
        entry_2 = self.make_entry(store, "Rule 2", "test.md", "sorted/md/test.md", True)

        assert history_file.exists()
        lines = history_file.read_text().splitlines()
        assert len(lines) == 2

        most_recent = store.get_recent(1)
        assert len(most_recent) == 1
        assert most_recent[0] == entry_2

    def test_get_history_errors_on_invalid(self, tmp_path):
        history_file = tmp_path / "history.jsonl"
        store = HistoryStore(history_file)
        entry_1 = self.make_entry(store, "Rule 1", "notes.txt", "sorted/txt/notes.txt", True)

        assert history_file.exists()
        lines = history_file.read_text().splitlines()
        assert len(lines) == 1

        with pytest.raises(ValueError):
            store.get_recent(0)
        with pytest.raises(ValueError):
            store.get_recent(-12)

    def test_get_history_empty_file(self, tmp_path):
        history_file = tmp_path / "history.jsonl"
        history_file.write_text("")
        store = HistoryStore(history_file)

        assert history_file.exists()
        lines = history_file.read_text().splitlines()
        assert len(lines) == 0

        most_recent = store.get_recent(1)
        assert most_recent == []


    def test_get_history_preserves_failed_entry(self, tmp_path):
        history_file = tmp_path / "history.jsonl"
        store = HistoryStore(history_file)

        entry_1 = self.make_entry(store, "Rule 1", "notes.txt", "sorted/txt/notes.txt", False)

        assert history_file.exists()
        lines = history_file.read_text().splitlines()
        assert len(lines) == 1

        most_recent = store.get_recent(1)
        assert len(most_recent) == 1
        assert most_recent[0] == entry_1

    def make_entry(self, store: HistoryStore, name: str, original_path: str, final_path: str, succeed: bool):
        if succeed:
            entry = \
                HistoryEntry(
                    timestamp=datetime.datetime.now(),
                    rule_name=name,
                    original_path=Path(original_path),
                    final_path=Path(final_path),
                    success=True
                ) 
        else:
            entry = \
                HistoryEntry(
                    timestamp=datetime.datetime.now(),
                    rule_name=name,
                    original_path=Path(original_path),
                    final_path=None,
                    success=False,
                    error="error"
                )
        store.add(entry)
        return entry