from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
from collections import deque
import json
import shutil

@dataclass
class HistoryEntry:
    timestamp: datetime
    rule_name: str
    original_path: Path
    final_path: Path | None
    success: bool
    error: str | None = None

    def __str__(self):
        if self.success:
            return f"{self.timestamp.strftime('%Y-%m-%d')} [OK] {self.rule_name} \n{self.original_path} \n→ {self.final_path}"
        else:
            return f"{self.timestamp.strftime('%Y-%m-%d')} [FAIL] {self.rule_name} \n{self.original_path}\n{self.error}"

    def display_title(self) -> str:
        status = "OK" if self.success else "FAIL"
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} [{status}] {self.rule_name}"

    def display_details(self) -> list[str]:
        """ Return a list of the details of this entry, first is the original path, second is the final path if there is one"""
        details = [str(self.original_path)]

        if self.final_path is not None:
            details.append(f"→ {self.final_path}")

        if self.error is not None:
            details.append(f"Error: {self.error}")

        return details

class HistoryStore:
    def __init__(self, history_file: Path):
        self.history_file = history_file
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def add(self, entry: HistoryEntry) -> None:
        """ Add the current history entry to the end of the history file"""
        # convert the dict to a history entry type
        data = asdict(entry)
        data["timestamp"] = entry.timestamp.isoformat()
        data["original_path"] = str(entry.original_path)
        data["final_path"]=(
            str(entry.final_path) if entry.final_path is not None else None
        )

        # write data to file
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with self.history_file.open(mode="a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

    def get_filtered(self, search_text="", status="All", limit=100):
        """Returns at most limit items, only which include search_text in their title and the given status"""
        if not self.history_file.exists():
            return []
        
        history_entries = []
        if limit <= 0:
            raise ValueError("Amount must be greater than 0")

        # read in file data
        with self.history_file.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        search_text = search_text.strip().lower()

        # convert to appropiate type and return
        for line in reversed(lines):
            entry = json.loads(line)

            if (status == "Success" and not entry.get("success")) or (status == "Failed" and entry.get("success")):
                continue

            searchable = " ".join([
                entry["rule_name"],
                entry["original_path"],
                entry["final_path"] or "",
            ]).lower()
            
            if (search_text != "") and (search_text not in searchable):
                continue
            
            history_entries.append(
                HistoryEntry(
                    timestamp=datetime.fromisoformat(entry["timestamp"]),
                    rule_name=entry["rule_name"],
                    original_path=Path(entry["original_path"]),
                    final_path=(
                        Path(entry["final_path"])
                        if entry["final_path"] is not None
                        else None
                    ),
                    success=entry["success"],
                    error=entry["error"]
                )
            )
            if len(history_entries) >= limit:
                break

        return history_entries  

    def get_recent(self, amount: int) -> list[HistoryEntry]:
        """ Returns the amount many most recent history entries"""
        if not self.history_file.exists():
            return []
        
        history_entries = []
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        # read in file data
        with self.history_file.open("r", encoding="utf-8") as f:
            lines = deque(f, maxlen=amount)

        # convert to appropriate type and return
        for line in lines:
            entry = json.loads(line)
            history_entries.append(
                HistoryEntry(
                    timestamp=datetime.fromisoformat(entry["timestamp"]),
                    rule_name=entry["rule_name"],
                    original_path=Path(entry["original_path"]),
                    final_path=(
                        Path(entry["final_path"])
                        if entry["final_path"] is not None
                        else None
                    ),
                    success=entry["success"],
                    error=entry["error"]
                )
            )

        return history_entries

    def clear_history(self) -> None:
        """Clears all history"""
        self.history_file.write_text("", encoding="utf-8")

    def export_history(self, write_path: Path):
        """Exports history to new file"""
        if not self.history_file.exists():
            Path(write_path).write_text("", encoding="utf-8")
            return

        shutil.copy(self.history_file, write_path)