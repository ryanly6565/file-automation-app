from PySide6.QtWidgets import (
    QDialog,
    QLineEdit,
    QFormLayout,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QCheckBox,
    QScrollArea,
    QWidget,
)
from src.rules import Rule
from src.condition_editor import ConditionEditor
from src.action_editor import ActionsEditor
from pathlib import Path
from src.rule_validation import get_rule_warnings, validate_rule

class RuleEditorDialog(QDialog):
    def __init__(self, rule=None, parent=None):
        super().__init__(parent)

        self.rule = rule

        if self.rule is None:
            # create mode
            self.setWindowTitle("Add Rule")
        else:
            # edit mode
            self.setWindowTitle("Edit Rule")

        self.resize(800, 700)
        
        # outer container with scroll
        main_layout = QFormLayout(self)

        # scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_container = QWidget()
        layout = QFormLayout(content_container)

        # name and folder input fields
        self.name_input = QLineEdit()
        self.folder_input = QLineEdit()

        # auto fill out name and folder if a rule is given
        if rule is not None:
            self.name_input.setText(rule.name)
            folder_text = "" if rule.watch_folder == Path() else str(rule.watch_folder)
            self.folder_input.setText(folder_text)

        layout.addRow("Name:", self.name_input)

        # add the folder input and a button that lets users select a file on their computer
        folder_row = QHBoxLayout()
        folder_row.addWidget(self.folder_input)

        browse_button = QPushButton("Browse")
        browse_button.setObjectName("browseButton")
        browse_button.clicked.connect(self.choose_folder)
        folder_row.addWidget(browse_button)
        layout.addRow("Watch folder:", folder_row)

        # add the recursive toggle
        self.recursive_box = QCheckBox("Include subfolders?")
        if rule is not None:
            self.recursive_box.setChecked(rule.recursive)
        layout.addRow(self.recursive_box)

        # add the condition editor
        condition = None
        if rule is not None:
            condition = rule.condition
        self.condition_editor = ConditionEditor(condition=condition)
        layout.addRow("Condition:", self.condition_editor)

        actions = None
        if rule is not None:
            actions = rule.actions
        self.actions_editor = ActionsEditor(actions=actions)
        layout.addRow("Actions:", self.actions_editor)

        # add test rule
        test_button = QPushButton("Test with File")
        test_button.setObjectName("testRuleButton")
        test_button.clicked.connect(self.test_rule)
        layout.addRow(test_button)

        scroll_area.setWidget(content_container)
        main_layout.addWidget(scroll_area)
        
        # add save and load buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_rule)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)


    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Watch Folder"
        )

        if folder:
            self.folder_input.setText(folder)

    def save_rule(self):
        """ Handler for pressing the save button, validates input and saves rules."""
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self,
                "Invalid Rule",
                "Rule name cannot be empty."
            )
            return

        if not self.folder_input.text().strip():
            QMessageBox.warning(
                self,
                "Invalid Rule",
                "Watch folder cannot be empty."
            )
            return

        try:
            self.result_rule = self.build_rule()
            validate_rule(self.result_rule)
            warnings = get_rule_warnings(self.result_rule)
            if warnings:
                reply = QMessageBox.question(self, "Warning", "\n".join(warnings) + f"\nSave rule anyways?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No)

                if reply != QMessageBox.StandardButton.Yes:
                    return


        except ValueError as e:
            QMessageBox.warning(
                self,
                "Invalid Rule",
                str(e)
            )
            return

        self.accept()

    def build_rule(self):
        """ Creates a new rule based on the data in the rule editor """
        enabled = self.rule.enabled if self.rule is not None else True
        return Rule(
            condition=self.condition_editor.build_condition(),
            actions=self.actions_editor.build_actions(),
            watch_folder=Path(self.folder_input.text().strip()).resolve(),
            name=self.name_input.text().strip(),
            recursive=self.recursive_box.isChecked(),
            enabled=enabled
        )

    def test_rule(self):
        """ Checks if a file satisfies the current rule """
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Sample File")

        if not file_path:
            return

        try:
            rule = self.build_rule()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Rule", str(e))
            return
        
        path = Path(file_path)
        if rule.condition.matches(path):
            actions = "\n".join(f"- {action}" for action in rule.actions)
            QMessageBox.information(
                self,
                "Rule Test",
                f"This file MATCHES the rule.\n\n"
                f"Actions that would run:\n{actions}"
            )
        else:
            QMessageBox.information(self, "Rule Test", "This file does NOT match the rule.")

    