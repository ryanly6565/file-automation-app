
from PySide6.QtWidgets import (
    QApplication, 
    QWidget, 
    QMainWindow, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QFrame, 
    QScrollArea, 
    QPushButton, 
    QMessageBox,
    QCheckBox,
    QFileDialog,
    QMenu,
    QLineEdit,
    QComboBox,
)

from PySide6.QtCore import QTimer
from watchdog.observers import Observer
from src.config_loader import load_rules
from src.history import HistoryStore
from src.rule_editor import RuleEditorDialog
from pathlib import Path
from src.watcher import WatcherHandler
from collections import defaultdict
from src.config_loader import load_rules, save_rules
from src.rules import Rule
import sys
import copy

class HistoryPanel(QFrame):
    def __init__(self, history: HistoryStore):
        super().__init__()
        self.history = history
        self.setObjectName("panel")
        self.build_history_section()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_history)
        self.timer.start(2000)

        self.setStyleSheet("""
            QFrame#historySuccess {
                background-color: #fafafa;
                border: 1px solid #e5e5e5;
                border-radius: 8px;
            }

            QFrame#historyFailure {
                background-color: #fff5f5;
                border: 1px solid #d66;
                border-radius: 8px;
            }

            QLabel#historyFailureTitle {
                color: #b00020;
                font-weight: 700;
            }
            
            QLabel#historyError {
                color: #b00020;
                font-size: 11px;
            }
        """)

    def build_history_section(self) -> None:
        self.setFrameShape(QFrame.Shape.StyledPanel)
        history_layout = QVBoxLayout(self)

        # add the history title and clear button
        header_row = QHBoxLayout()
        history_title = QLabel("History")
        history_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_history)
        export_button = QPushButton("Export")
        export_button.clicked.connect(self.export_history)

        header_row.addWidget(history_title)
        header_row.addStretch()
        header_row.addWidget(export_button)
        header_row.addWidget(clear_button)

        history_layout.addLayout(header_row)

        # add the filter row
        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search history...")

        # combo with status options
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "All",
            "Success",
            "Failed",
        ])
        history_layout.addLayout(filter_row)

        # combo with number of entries
        self.history_count = QComboBox()
        self.history_count.addItems([
            "20",
            "50",
            "100",
        ])

        # add pieces to history
        self.search_input.textChanged.connect(self.refresh_history)
        self.status_filter.currentTextChanged.connect(self.refresh_history)
        self.history_count.currentTextChanged.connect(self.refresh_history)
        filter_row.addWidget(self.search_input)
        filter_row.addWidget(self.status_filter)
        filter_row.addWidget(self.history_count)

        # create history container, which hosts the scroll wheel and list of history entries
        history_scroll = QScrollArea()
        history_scroll.setWidgetResizable(True)
        history_container = QWidget()
        self.history_container_layout = QVBoxLayout(history_container)
        self.refresh_history()
                
        # add the history container and scroll to the frame
        history_scroll.setWidget(history_container)
        history_layout.addWidget(history_scroll)

    def refresh_history(self) -> None:
        self.clear_layout(self.history_container_layout)

        history_entries = self.history.get_filtered(
            search_text=self.search_input.text().strip(),
            status=self.status_filter.currentText(),
            limit=int(self.history_count.currentText()),
        )

        # check that there is history
        if len(history_entries) == 0:
            history_entry_frame = QFrame()
            history_entry_frame.setFrameShape(QFrame.Shape.StyledPanel)
            history_entry_layout = QVBoxLayout(history_entry_frame)
            history_entry_layout.addWidget(QLabel("No history currently."))
            history_entry_frame.setObjectName("card")
            self.history_container_layout.addWidget(history_entry_frame)
            self.history_container_layout.addStretch()

        else:
            # add rules to container
            for history_entry in history_entries:
                history_entry_frame = QFrame()

                # change style if success or failure
                if history_entry.success:
                    history_entry_frame.setObjectName("historySuccess")
                else:
                    history_entry_frame.setObjectName("historyFailure")
                history_entry_frame.setFrameShape(QFrame.Shape.StyledPanel)

                history_entry_layout = QVBoxLayout(history_entry_frame)

                title = QLabel(history_entry.display_title())

                if history_entry.success:
                    title.setStyleSheet("font-weight: 600;")
                else:
                    title.setObjectName("historyFailureTitle")

                history_entry_layout.addWidget(title)

                for detail in history_entry.display_details():
                    label = QLabel(detail)
                    label.setWordWrap(True)
                    # set the error detail to be red and have more space
                    if detail.startswith("Error:"):
                        label.setObjectName("historyError")
                        label.setContentsMargins(0, 6, 0, 0)
                    history_entry_layout.addWidget(label)

                self.history_container_layout.addWidget(history_entry_frame)
            self.history_container_layout.addStretch()


    def clear_layout(self, layout):
        """Clears the panel """
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def clear_history(self):
        """Clears all history """
        result = QMessageBox.question(
            self,
            "Clear history",
            "Erase all history entries (cannot be undone)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if result != QMessageBox.StandardButton.Yes:
            return

        else:
            self.history.clear_history()
            self.refresh_history()

    def export_history(self):
        """Exports history to new file"""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export History Location",
            "history.jsonl",
            "JSONL Files (*.jsonl)",
        )
        self.history.export_history(file_path)
                