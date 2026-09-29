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
)

from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
from watchdog.observers import Observer
from src.history import HistoryStore
from src.history_panel import HistoryPanel
from src.rule_editor import RuleEditorDialog
from pathlib import Path
from src.watcher import WatcherHandler
from collections import defaultdict
from src.config_loader import load_rules, save_rules, rule_to_json
from src.rules import Rule
from src.conditions import ExtensionCondition, OrCondition, SizeCondition
from src.actions import CopyAction
from src.rule_validation import validate_rule
from src.apps_path import RULES_PATH, HISTORY_PATH
from threading import Lock
import sys
import copy
import shutil
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rules_file = RULES_PATH
        self.history = HistoryStore(HISTORY_PATH)
        self.rules = load_rules(self.rules_file)

        # the actual file watcher
        self.observer = None
        self.setup_ui()
        self.setWindowTitle("File Automation")

    def setup_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        self.resize(1000, 600)

        title = QLabel("File Automation")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # retrieve watch folder
        watch_row = QHBoxLayout()
        self.status_label = QLabel("Stopped")
        self.status_label.setObjectName("statusStopped")
        self.folder_label = QLabel(f"")
        self.folder_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 700;
            color: #2f4f5f;
        """)
        watch_row.addWidget(self.status_label)
        watch_row.addWidget(self.folder_label)
        watch_row.addStretch()

        # add the reload and start/stop button
        reload_button = QPushButton("Reload")
        reload_button.clicked.connect(self.reload_config)
        reload_button.setObjectName("secondaryButton")
        self.watch_button = QPushButton("Start")
        self.watch_button.clicked.connect(self.toggle_watching)
        self.watch_button.setMinimumWidth(90)
        self.watch_button.setObjectName("primaryButton")
        watch_row.addWidget(reload_button)
        watch_row.addWidget(self.watch_button)

        layout.addLayout(watch_row)

        # box that has rule and history frames
        content_frame = QFrame()
        content_layout = QHBoxLayout(content_frame)


        # construct central rules panel
        rules_frame = self.build_rules_section()
        rules_frame.setObjectName("panel")
        content_layout.addWidget(rules_frame)

        # construct central history panel
        self.history_panel = HistoryPanel(self.history)
        content_layout.addWidget(self.history_panel)

        content_layout.setSpacing(16)
        content_layout.setStretch(0, 1)
        content_layout.setStretch(1, 1)
        layout.addWidget(content_frame)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }

            QLabel {
                color: #222222;
            }
            QFrame#panel {
                background-color: white;
                border: 1px solid #dddddd;
                border-radius: 10px;
            }

            QFrame#card {
                background-color: #fafafa;
                border: 1px solid #e5e5e5;
                border-radius: 8px;
            }

            QFrame#disabledCard {
                background-color: #f2f2f2;
                border: 1px solid #dddddd;
                border-radius: 8px;
            }

            QPushButton {
                padding: 8px 14px;
                border-radius: 6px;
                font-weight: 600;
            }

            QPushButton#primaryButton {
                background-color: #222222;
                color: white;
                border: none;
            }
            QPushButton#previewButton,
            QPushButton#secondaryButton {
                background-color: white;
                color: #222222;
                border: 1px solid #cccccc;
            }

            QPushButton#dangerButton {
                background-color: #eeeeee;
                color: #222222;
                border: 1px solid #cccccc;
            }

            QPushButton:hover {
                background-color: #dddddd;
            }

            QPushButton:disabled {
                color: #999999;
                background-color: #eeeeee;
            }
            QPushButton#primaryButton:disabled {
                background-color: #eeeeee;
                color: #999999;
                border: 1px solid #dddddd;
            }

            QPushButton#dangerButton:disabled {
                background-color: #eeeeee;
                color: #999999;
                border: 1px solid #dddddd;
            }

            QLabel#statusWatching {
                color: #2e7d32;
                font-weight: bold;
            }

            QLabel#statusStopped {
                color: #777777;
            }

            QPushButton#addRuleButton {
                background-color: white;
                color: #222222;
                border: 1px solid #bcbcbc;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
            }

            QPushButton#addRuleButton:hover {
                background-color: #f0f0f0;
                border-color: #999999;
            }

            QPushButton#conditionAddButton {
                background-color: white;
                border: 1px solid #bcbcbc;
                border-radius: 5px;
                padding: 5px 10px;
            }

            QPushButton#actionAddButton {
                background-color: white;
                border: 1px solid #bcbcbc;
                border-radius: 5px;
                padding: 5px 10px;
            }

            QPushButton#actionRemoveButton {
                background-color: white;
                border: 1px solid #bcbcbc;
                border-radius: 5px;
                padding: 4px 8px;
            }

            QPushButton#actionAddButton:hover,
            QPushButton#conditionAddButton,
            QPushButton#actionRemoveButton:hover {
                background-color: #f0f0f0;
                border-color: #999999;
            }

            QPushButton#browseButton {
                background-color: white;
                color: #222222;
                border: 1px solid #bcbcbc;
                border-radius: 5px;
                padding: 4px 9px;
                font-weight: 500;
            }

            QPushButton#browseButton:hover {
                background-color: #f0f0f0;
                border-color: #999999;
            }

            QPushButton#browseButton:pressed {
                background-color: #e6e6e6;
            }

            QPushButton#testRuleButton {
                background-color: white;
                color: #222222;
                border: 1px solid #bcbcbc;
                border-radius: 6px;
                padding: 7px 12px;
                font-weight: 600;
            }

            QPushButton#testRuleButton:hover {
                background-color: #f0f0f0;
                border-color: #999999;
            }

            QPushButton#testRuleButton:pressed {
                background-color: #e6e6e6;
            }
        """)

    def build_rules_section(self) -> QFrame:
        rules_frame = QFrame()
        rules_frame.setFrameShape(QFrame.Shape.StyledPanel)
        rules_layout = QVBoxLayout(rules_frame)

        # add the rules title
        rules_header = QHBoxLayout()

        rules_title = QLabel("Rules")
        rules_title.setStyleSheet("font-size: 18px; font-weight: bold;")

        # create the import and export buttons
        import_rules_button = QPushButton("Import")
        import_rules_button.clicked.connect(lambda: self.import_rules())
        import_rules_button.setObjectName("secondaryButton")
        export_rules_button = QPushButton("Export")
        export_rules_button.clicked.connect(lambda: self.export_rules())
        export_rules_button.setObjectName("secondaryButton")

        # create add rule menu
        add_rule_button = QPushButton("Add Rule")
        menu = QMenu(add_rule_button)

        # add options of blank rule or template
        blank_action = menu.addAction("Blank Rule")
        blank_action.triggered.connect(lambda: self.open_rule_editor(None))
        menu.addSeparator()
        pdf_action = menu.addAction("Organize PDFs")
        pdf_action.triggered.connect(lambda: self.open_rule_editor_template("pdf"))
        image_action = menu.addAction("Organize Images")
        image_action.triggered.connect(lambda: self.open_rule_editor_template("images"))
        backup_action = menu.addAction("Backup Large Files")
        backup_action.triggered.connect(lambda: self.open_rule_editor_template("backup"))
        add_rule_button.setMenu(menu)

        rules_header.addWidget(rules_title)
        rules_header.addStretch()
        rules_header.addWidget(import_rules_button)
        rules_header.addWidget(export_rules_button)
        rules_header.addWidget(add_rule_button)

        rules_layout.addLayout(rules_header)

        # create rules container, which hosts the scroll wheel and list of rules
        rules_scroll = QScrollArea()
        rules_scroll.setWidgetResizable(True)
        rules_container = QWidget()
        self.rules_container_layout = QVBoxLayout(rules_container)

        self.refresh_rules_display()

        rules_scroll.setWidget(rules_container)
        rules_layout.addWidget(rules_scroll)
        return rules_frame

    def clear_layout(self,layout) -> None:
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    
    def refresh_rules_display(self) -> None:
        """Refresh the displayed rules"""
        self.clear_layout(self.rules_container_layout)

        # check that there are rules
        if len(self.rules) == 0:
            rule_frame = QFrame()
            rule_frame.setFrameShape(QFrame.Shape.StyledPanel)
            rule_layout = QVBoxLayout(rule_frame)
            rule_layout.addWidget(QLabel("No rules currently."))
            rule_frame.setObjectName("card")
            self.rules_container_layout.addWidget(rule_frame)

        else:
            # add rules to container
            rules_by_folder = group_rules_by_folder(self.rules)

            for folder, rules in rules_by_folder.items():
                folder_label = QLabel(str(folder))
                folder_label.setStyleSheet("font-weight: bold; font-size: 18px;")
                folder_label.setWordWrap(True)
                folder_label.setToolTip(str(folder))
                self.rules_container_layout.addWidget(folder_label)

                for index, rule in enumerate(rules):
                    rule_frame = QFrame()
                    rule_frame.setFrameShape(QFrame.Shape.StyledPanel)

                    # create the row containing the rule name and buttons
                    rule_layout = QVBoxLayout(rule_frame)
                    header_row = QHBoxLayout()
                    rule_name_label = QLabel(rule.name)

                    # add enabled/disabled checkbox
                    enabled_checkbox = QCheckBox("Enabled")
                    enabled_checkbox.setChecked(rule.enabled)
                    enabled_checkbox.stateChanged.connect(lambda state, r=rule: self.toggle_rule_enabled(r, state))

                    # add buttons to adjust rule priority
                    up_button = QPushButton("↑")
                    down_button = QPushButton("↓")
                    up_button.setEnabled(index > 0)
                    down_button.setEnabled(index < len(rules) - 1)

                    up_button.setObjectName("ruleMoveButton")
                    down_button.setObjectName("ruleMoveButton")
                    up_button.clicked.connect( lambda checked=False, r=rule: self.move_rule(r, -1))
                    down_button.clicked.connect(lambda checked=False, r=rule: self.move_rule(r, 1))

                    # create more menu button
                    more_button = QPushButton("⋯")
                    more_button.setObjectName("ruleMoreButton")
                    menu = QMenu(more_button)
                    
                    duplicate_action = menu.addAction("Duplicate")
                    duplicate_action.triggered.connect(lambda checked=False, r=rule: self.duplicate_rule(r))
                    menu.addSeparator()
                    delete_action = menu.addAction("Delete")
                    delete_action.triggered.connect(lambda checked=False, r=rule: self.delete_rule(r))
                    more_button.setMenu(menu)

                    # add edit button
                    edit_button = QPushButton("Edit")
                    edit_button.setObjectName("ruleEditButton")
                    edit_button.clicked.connect(lambda checked=False, r=rule: self.open_rule_editor(r))

                    # add features to row
                    header_row.addWidget(rule_name_label)
                    header_row.addStretch()
                    header_row.addWidget(enabled_checkbox)
                    header_row.addWidget(up_button)
                    header_row.addWidget(down_button)
                    header_row.addWidget(edit_button)
                    header_row.addWidget(more_button)
                    rule_layout.addLayout(header_row)

                    # create details panel
                    details_layout = QVBoxLayout()
                    details_layout.setContentsMargins(12, 0, 0, 0)

                    # add condition description
                    condition_label = QLabel("Condition: " + str(rule.condition))
                    condition_label.setWordWrap(True)
                    details_layout.addWidget(condition_label)

                    # add recursive description
                    recursive_label = QLabel(f"Recursive: {'Yes' if rule.recursive else 'No'}")
                    recursive_label.setWordWrap(True)
                    details_layout.addWidget(recursive_label)

                    # create list of actions
                    actions_title = QLabel("Actions:")
                    details_layout.addWidget(actions_title)
                    actions_layout = QVBoxLayout()
                    actions_layout.setContentsMargins(12, 0, 0, 0)

                    # create each rule
                    for action in rule.actions:
                        action_label = QLabel(str(action))

                        if rule.enabled:
                            action_label.setStyleSheet(
                                "color: #4a4a4a; font-size: 12px;"
                            )
                        else:
                            action_label.setStyleSheet(
                                "color: #888888; font-size: 12px;"
                            )

                        action_label.setWordWrap(True)
                        actions_layout.addWidget(action_label)

                    # add details and rules to the main panel
                    details_layout.addLayout(actions_layout)
                    rule_layout.addLayout(details_layout)

                    if rule.enabled:
                        rule_frame.setObjectName("card")
                        rule_name_label.setStyleSheet("""
                            font-size: 13px;
                            font-weight: 600;
                        """)
                        condition_label.setStyleSheet("color: #4a4a4a; font-size: 12px;")
                        recursive_label.setStyleSheet("color: #666666; font-size: 11px;")
                    else:
                        rule_frame.setObjectName("disabledCard")
                        rule_name_label.setStyleSheet("""
                            font-size: 13px;
                            font-weight: 600;
                            color: #888888;
                        """)
                        condition_label.setStyleSheet("color: #888888;")
                        recursive_label.setStyleSheet("color: #888888; font-size: 11px")
                        actions_title.setStyleSheet("color: #888888;")
                    self.rules_container_layout.addWidget(rule_frame)

        self.rules_container_layout.addStretch()

    def reload_config(self):
        """Make the observer refresh the rules to observe the changes in config."""
        was_running = self.observer is not None

        if was_running:
            self.stop_watching()

        try:
            new_rules = load_rules(self.rules_file)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Config Error",
                f"Failed to reload config:\n{e}"
            )

            if was_running:
                try:
                    self.start_watching()

                except FileNotFoundError as e:
                    QMessageBox.warning(
                        self,
                        "Missing Watch Folder",
                        str(e)
                    )
            return

        self.rules = new_rules

        self.refresh_rules_display()
        self.folder_label.setText(f"")

        if was_running:
            try:
                self.start_watching()
            except FileNotFoundError as e:
                QMessageBox.warning(
                    self,
                    "Missing Watch Folder",
                    str(e)
                )

    def open_rule_editor(self, rule=None, is_template=False):
        """Opens the rule editor dialogue, changes if rule is None (creating) vs non-None (editing)."""
        dialog = RuleEditorDialog(rule=rule, parent=self)

        if dialog.exec():
            new_rule = dialog.result_rule
            def apply_change():
                if rule is None or is_template:
                    self.rules.append(new_rule)
                else:
                    index = self.rules.index(rule)
                    self.rules[index] = new_rule

            self.apply_rule_change(apply_change)

    def open_rule_editor_template(self, template_type: str) -> None:
        """Opens a rule editor with a default template """
        if template_type == "pdf":
            rule = Rule(
                condition=ExtensionCondition(".pdf"),
                actions=[],
                watch_folder=Path(),
                name="Organize PDFs",
                recursive=False,
            )

        elif template_type == "images":
            rule = Rule(
                condition=OrCondition([
                    ExtensionCondition(".png"),
                    ExtensionCondition(".jpg"),
                    ExtensionCondition(".jpeg"),
                ]),
                actions=[],
                watch_folder=Path(),
                name="Organize Images",
                recursive=False,
            )

        elif template_type == "backup":
            rule = Rule(
                condition=SizeCondition(100 * 1024 * 1024, "gte"),
                actions=[CopyAction(Path())],
                watch_folder=Path(),
                name="Backup Large Files",
                recursive=False,
            )

        self.open_rule_editor(rule, is_template=True)
    
    def toggle_rule_enabled(self, rule, state):
        rule.enabled = bool(state)
        save_rules(self.rules_file, self.rules)
        self.refresh_rules_display()

    def delete_rule(self, rule):
        reply = QMessageBox.question(self, "Delete Rule", f"Delete {rule.name}?",
                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                  QMessageBox.StandardButton.No)

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.apply_rule_change(lambda: self.rules.remove(rule))

    def duplicate_rule(self, rule):
        def duplicate():
            new_rule = copy.deepcopy(rule)

            # find new name
            base_name = f"{rule.name} Copy"
            new_name = base_name
            number = 2
            existing_names = {r.name for r in self.rules}
            while new_name in existing_names:
                new_name = f"{base_name} {number}"
                number += 1
            new_rule.name = new_name

            index = self.rules.index(rule)
            self.rules.insert(index + 1, new_rule)

        self.apply_rule_change(duplicate)

    def move_rule(self, rule, direction):
        """ Move a rule up or down the priority list. -1 indicates an increase in priority """
        self.apply_rule_change(lambda: move_rule_helper(self.rules, rule, direction))

    def toggle_watching(self):
        if self.observer is None:
            try:
                self.start_watching()
            except FileNotFoundError as e:
                QMessageBox.warning(
                    self,
                    "Missing Watch Folder",
                    str(e)
                )
        else:
            self.stop_watching()

    def import_rules(self):
        """Imports the give file as the rules """
        # select the file path
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Rules",
            "rules.json",
            "JSON Files (*.json)",
        )
        if not file_path:
            return

        # read in file data
        try:
            imported_rules = load_rules(file_path)

            missing_folders = []
            for rule in imported_rules:
                validate_rule(rule)

                if not rule.watch_folder.exists() or not rule.watch_folder.is_dir():
                    missing_folders.append(f'{rule.name}: {rule.watch_folder}')

        except Exception as e:
            QMessageBox.warning(
                self,
                "Invalid Rules File",
                f"Could not import rules:\n{e}"
            )
            return
                
        if missing_folders:
            QMessageBox.warning(
                self,
                "Missing Watch Folders",
                "Some imported rules reference folders that do not exist on this system.\n\n"
                + "\n".join(missing_folders)
                + "\n\nEdit these rules and select valid watch folders before starting the watcher."
            )
        was_running = self.observer is not None
        if was_running:
            self.stop_watching()

        self.rules = imported_rules
        save_rules(self.rules_file, self.rules)
        self.refresh_rules_display()

        if was_running and not missing_folders:
            self.start_watching()
    
    def export_rules(self):
        """Exports list of rules to new file"""
        # select the file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Rules Location",
            "rules.json",
            "JSON Files (*.json)",
        )
        if not file_path:
            return

        # write rule data
        rule_data = [rule_to_json(rule) for rule in self.rules]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"rules": rule_data}, f, indent=4)

    def start_watching(self):
        """ Start watching the requested folders """
        if self.observer is not None:
            return

        rules_by_folder = group_rules_by_folder(self.rules)

        for folder in rules_by_folder:
            folder = Path(folder)

            if not folder.exists() or not folder.is_dir():
                folder_name = str(folder)
                if sys.platform != "win32" and "\\" in folder_name:
                    raise FileNotFoundError(
                        f"Watch folder does not exist: {folder}\n"
                        "This path looks like it may use Windows-style separators.\nEdit the rule and select a Linux path."
                    )

                elif sys.platform == "win32" and folder_name.startswith("/"):
                    raise FileNotFoundError(
                        f"Watch folder does not exist: {folder}\n"
                        "This path looks like it may be a Linux-style path.\nEdit the rule and select a Windows folder."
                    )

                else:
                    raise FileNotFoundError(f"Watch folder does not exist: {folder}")

        self.observer = Observer()

        # all handlers share this so files created/moved by one watched folder
        # can be ignored by handlers watching other folders
        recently_processed = {}
        recently_processed_lock = Lock()

        # for each unique folder create the appropiate observer setup
        for folder, rules in rules_by_folder.items():
            handler = WatcherHandler(
                rules,
                self.history,
                recently_processed,
                recently_processed_lock,
            )

            recursive = any(rule.recursive for rule in rules)

            self.observer.schedule(
                handler,
                path=folder,
                recursive=recursive
            )

        try:
            self.observer.start()
        except Exception:
            self.observer = None
            raise

        # handle display changes
        self.status_label.setText("Watching")
        self.status_label.setObjectName("statusWatching")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

        self.folder_label.setText(
            f"Watching {len(rules_by_folder)} folder(s)."
        )

        self.watch_button.setText("Pause")
        self.watch_button.setObjectName("secondaryButton")
        self.watch_button.style().unpolish(self.watch_button)
        self.watch_button.style().polish(self.watch_button)

    def stop_watching(self):
        if self.observer is None:
            return

        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()

        self.observer = None

        self.status_label.setText("Paused")
        self.status_label.setObjectName("statusStopped")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label) 
        self.folder_label.setText(f"")

        self.watch_button.setText("Start")
        self.watch_button.setObjectName("primaryButton")
        self.watch_button.style().unpolish(self.watch_button)
        self.watch_button.style().polish(self.watch_button)

    def closeEvent(self, event):
        self.stop_watching()
        event.accept()

    def apply_rule_change(self, change_func):
        """ Resets the observer to apply a rule change. """
        was_running = self.observer is not None

        if was_running:
            self.stop_watching()

        change_func()

        save_rules(self.rules_file, self.rules)
        self.refresh_rules_display()

        if was_running:
            self.start_watching()
    
def move_rule_helper(rules, rule, direction):
    """This code was split into a helper for testing purposes"""
    sibling_rules = [curr_rule for curr_rule in rules if curr_rule.watch_folder == rule.watch_folder]
    sibling_index = sibling_rules.index(rule)
    new_sibling_index = sibling_index + direction

    if new_sibling_index < 0 or new_sibling_index >= len(sibling_rules):
        return

    rule_to_swap_with = sibling_rules[new_sibling_index]
    rule_to_swap_with_index = rules.index(rule_to_swap_with)
    old_index = rules.index(rule)
    rules[old_index], rules[rule_to_swap_with_index] = (rules[rule_to_swap_with_index], rules[old_index])
    
def group_rules_by_folder(rules: list[Rule]):
    """Given a list of rules, converts them into a dict with the watch_folder as the key"""
    rules_by_folder = defaultdict(list)
    for rule in rules:
        rules_by_folder[rule.watch_folder].append(rule)
    return rules_by_folder

def find_matching_rule(rules, path):
    """Given a list of rules and a path, find the first rule to match the path"""
    for rule in rules:
        if rule.watch_folder == path.parent and rule.matches(path):
            return rule

    return None

def resource_path(relative_path: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    return Path(__file__).resolve().parent.parent / relative_path


if __name__ == "__main__":
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "RyanLy.FileAutomationApp"
        )

    app = QApplication(sys.argv)
    icon = QIcon(str(resource_path("assets/app.ico")))
    app.setWindowIcon(icon)

    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()

    sys.exit(app.exec())