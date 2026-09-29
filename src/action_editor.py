from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QStackedWidget,
    QLineEdit,
    QCheckBox,
    QSpinBox,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QFileDialog,
)
from pathlib import Path
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtCore import Qt
from src.actions import (
    MoveAction,
    CopyAction,
    CompressAction,
    PrefixRenamingAction,
    SuffixRenamingAction,
    ReplaceTextAction,
    ChangeExtensionAction,
    ExecuteScriptAction,
    DeleteAction
)

class ActionsEditor(QWidget):
    def __init__(self, actions=None, parent=None):
        super().__init__(parent)

        self.action_editors = []

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.actions_frame = QFrame()
        self.actions_frame.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum
        )

        self.actions_layout = QVBoxLayout(self.actions_frame)
        self.actions_layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self.actions_frame)

        add_button = QPushButton("+ Add Action")
        add_button.setObjectName("actionAddButton")
        add_button.clicked.connect(lambda: self.add_action())
        self.layout.addWidget(add_button)
        
        if actions is not None:
            for action in actions:
                self.add_action(action)

    def add_action(self, action=None):
        editor = ActionEditor(action=action)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        top_row = QHBoxLayout()

        top_row.addWidget(editor.type_input)

        remove_button = QPushButton("Remove")
        remove_button.setObjectName("actionRemoveButton")
        remove_button.clicked.connect(
            lambda: self.remove_action(editor, container)
        )

        top_row.addStretch()
        top_row.addWidget(remove_button)

        container_layout.addLayout(top_row)
        container_layout.addWidget(editor.stack)

        self.action_editors.append(editor)
        self.actions_layout.addWidget(container)

        self.actions_frame.adjustSize()
        self.adjustSize()
        self.updateGeometry()

    def remove_action(self, editor, container):
        self.action_editors.remove(editor)

        # force the deleted node to be removed immediately
        self.actions_layout.removeWidget(container)
        container.setParent(None)
        container.deleteLater()
        self.actions_layout.invalidate()
        self.actions_layout.activate()
        self.actions_frame.adjustSize()
        self.adjustSize()
        self.updateGeometry()
        self.window().adjustSize()

    def build_actions(self):
        if len(self.action_editors) == 0:
            raise ValueError("Rules need at least one action.")

        return [editor.build_action() for editor in self.action_editors]

class ActionEditor(QWidget):
    def __init__(self, action=None, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # list of action types
        self.type_input = QComboBox()
        self.type_input.addItems([
            "Move",
            "Copy",
            "Compress",
            "Prefix Rename",
            "Suffix Rename",
            "Replace Text",
            "Change Extension",
            "Execute Script",
            "Delete",
        ])

        layout.addWidget(self.type_input)

        # create each possible type of page
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.move_page = MoveActionPage()
        self.copy_page = CopyActionPage()
        self.compress_page = CompressActionPage()
        self.prefix_page = PrefixRenameActionPage()
        self.suffix_page = SuffixRenameActionPage()
        self.replace_text_page = ReplaceTextActionPage()
        self.change_extension_page = ChangeExtensionActionPage()
        self.execute_script_page = ExecuteScriptActionPage()
        self.delete_page = DeleteActionPage()

        self.stack.addWidget(self.move_page)
        self.stack.addWidget(self.copy_page)
        self.stack.addWidget(self.compress_page)
        self.stack.addWidget(self.prefix_page)
        self.stack.addWidget(self.suffix_page)
        self.stack.addWidget(self.replace_text_page)
        self.stack.addWidget(self.change_extension_page)
        self.stack.addWidget(self.execute_script_page)
        self.stack.addWidget(self.delete_page)
        self.type_input.currentIndexChanged.connect(self.on_action_type_changed)

        if action is not None:
            self.load_action(action)

    def build_action(self):
        page = self.stack.currentWidget()
        return page.build_action()

    def load_action(self, action):
        if isinstance(action, MoveAction):
            self.type_input.setCurrentText("Move")
            self.move_page.load_action(action)

        elif isinstance(action, CopyAction):
            self.type_input.setCurrentText("Copy")
            self.copy_page.load_action(action)

        elif isinstance(action, CompressAction):
            self.type_input.setCurrentText("Compress")
            self.compress_page.load_action(action)

        elif isinstance(action, PrefixRenamingAction):
            self.type_input.setCurrentText("Prefix Rename")
            self.prefix_page.load_action(action)

        elif isinstance(action, SuffixRenamingAction):
            self.type_input.setCurrentText("Suffix Rename")
            self.suffix_page.load_action(action)

        elif isinstance(action, ReplaceTextAction):
            self.type_input.setCurrentText("Replace Text")
            self.replace_text_page.load_action(action)

        elif isinstance(action, ChangeExtensionAction):
            self.type_input.setCurrentText("Change Extension")
            self.change_extension_page.load_action(action)

        elif isinstance(action, ExecuteScriptAction):
            self.type_input.setCurrentText("Execute Script")
            self.execute_script_page.load_action(action)

        elif isinstance(action, DeleteAction):
            self.type_input.setCurrentText("Delete")
            self.delete_page.load_action(action)

        else:
            raise ValueError(f"Unsupported action type: {type(action).__name__}")

    def on_action_type_changed(self, index):
        self.stack.setCurrentIndex(index)

        current_page = self.stack.currentWidget()

        if current_page is not None:
            self.stack.setFixedHeight(current_page.sizeHint().height())

        self.updateGeometry()

class ActionPage(QWidget):
    def build_action(self):
        raise NotImplementedError

    def load_action(self, action):
        raise NotImplementedError


class MoveActionPage(ActionPage):
    """A widget that displays ui for the creation or modification of a move action"""
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout(self)
        self.destination_input = QLineEdit()

        destination_row = QHBoxLayout()
        destination_row.addWidget(self.destination_input)

        browse_button = QPushButton("Browse")
        browse_button.setObjectName("browseButton")
        browse_button.clicked.connect(self.choose_folder)
        destination_row.addWidget(browse_button)
        layout.addRow("Destination:", destination_row)

        # combo box for collision policy options
        self.collision_policy_input = QComboBox()
        self.collision_policy_input.addItems(["Rename", "Overwrite", "Skip",])
        layout.addRow("Collision policy:", self.collision_policy_input)

    def choose_folder(self):
        """Turns the selected folder into text form """
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self.destination_input.setText(folder)

    def build_action(self):
        """Creates the actual action object """
        destination = self.destination_input.text().strip()
        if not destination:
            raise ValueError("Move destination cannot be empty.")
        
        policy_map = {"Rename": "rename", "Overwrite": "overwrite", "Skip": "skip",}
        collision_policy = policy_map[self.collision_policy_input.currentText()]
        return MoveAction(Path(destination).resolve(), collision_policy=collision_policy)

    def load_action(self, action):
        """Sets the destination text box to be a value """
        destination_text = "" if action.dst_directory == Path() else str(action.dst_directory)
        self.destination_input.setText(destination_text)
        policy_map = {"rename": "Rename", "overwrite": "Overwrite", "skip": "Skip",}
        self.collision_policy_input.setCurrentText(policy_map[action.collision_policy])


class CopyActionPage(ActionPage):
    def __init__(self, parent=None):
        """A widget that displays ui for the creation or modification of a copy action"""
        super().__init__(parent)

        layout = QFormLayout(self)
        self.destination_input = QLineEdit()

        destination_row = QHBoxLayout()
        destination_row.addWidget(self.destination_input)

        browse_button = QPushButton("Browse")
        browse_button.setObjectName("browseButton")
        browse_button.clicked.connect(self.choose_folder)
        destination_row.addWidget(browse_button)
        layout.addRow("Destination:", destination_row)

        # combo box for collision policy options
        self.collision_policy_input = QComboBox()
        self.collision_policy_input.addItems(["Rename", "Overwrite", "Skip",])
        layout.addRow("Collision policy:", self.collision_policy_input)


    def choose_folder(self):
        """Turns the selected folder into text form """
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self.destination_input.setText(folder)

    def build_action(self):
        """Creates the actual action object """
        destination = self.destination_input.text().strip()
        if not destination:
            raise ValueError("Copy destination cannot be empty.")
        
        policy_map = {"Rename": "rename", "Overwrite": "overwrite", "Skip": "skip",}
        collision_policy = policy_map[self.collision_policy_input.currentText()]
        return CopyAction(Path(destination).resolve(), collision_policy=collision_policy)

    def load_action(self, action):
        """Sets the destination text box to be a value """
        destination_text = "" if action.dst_directory == Path() else str(action.dst_directory)
        self.destination_input.setText(destination_text)
        policy_map = {"rename": "Rename", "overwrite": "Overwrite", "skip": "Skip",}
        self.collision_policy_input.setCurrentText(policy_map[action.collision_policy])


class CompressActionPage(ActionPage):
    def __init__(self, parent=None):
        """A widget that displays ui for the creation or modification of a compress action"""
        super().__init__(parent)

    def build_action(self):
        """Creates the actual action object """
        return CompressAction()

    def load_action(self, action):
        """Does nothing, cause compress has no settings"""
        pass


class PrefixRenameActionPage(ActionPage):
    def __init__(self, parent=None):
        """A widget that displays ui for the creation or modification of a prefix rename action"""
        super().__init__(parent)
        layout = QFormLayout(self)
        self.prefix_input = QLineEdit()
        layout.addRow("Prefix:", self.prefix_input)

    def build_action(self):
        """Creates the actual action object """
        prefix = self.prefix_input.text()
        if not prefix:
            raise ValueError("Prefix cannot be empty.")
        return PrefixRenamingAction(prefix)

    def load_action(self, action):
        """Sets the prefix text box to be a value """
        self.prefix_input.setText(action.new_prefix)


class SuffixRenameActionPage(ActionPage):
    def __init__(self, parent=None):
        """A widget that displays ui for the creation or modification of a suffix rename action"""
        super().__init__(parent)
        layout = QFormLayout(self)
        self.suffix_input = QLineEdit()
        layout.addRow("Suffix:", self.suffix_input)

    def build_action(self):
        """Creates the actual action object """
        suffix = self.suffix_input.text()
        if not suffix:
            raise ValueError("Suffix cannot be empty.")
        return SuffixRenamingAction(suffix)

    def load_action(self, action):
        """Sets the suffix text box to be a value """
        self.suffix_input.setText(action.new_suffix)


class ReplaceTextActionPage(ActionPage):
    def __init__(self, parent=None):
        """A widget that displays ui for the creation or modification of a replace text action"""
        super().__init__(parent)
        layout = QFormLayout(self)
        self.old_str_input = QLineEdit()
        layout.addRow("Target String:", self.old_str_input)
        self.new_str_input = QLineEdit()
        layout.addRow("New String:", self.new_str_input)
        self.first_only_input = QCheckBox()
        self.first_only_input.setChecked(True)
        layout.addRow(
            "Replace First Instance Only:",
            self.first_only_input
        )

    def build_action(self):
        """Creates the actual action object """
        old_str = self.old_str_input.text()
        if not old_str:
            raise ValueError("Target string cannot be empty.")
        new_str = self.new_str_input.text()
        first_only = self.first_only_input.isChecked()
        return ReplaceTextAction(old_str=old_str, new_str=new_str, first_instance_only=first_only)

    def load_action(self, action):
        """Sets the text boxes and checkbox """
        self.old_str_input.setText(action.old_str)
        self.new_str_input.setText(action.new_str)
        self.first_only_input.setChecked(action.first_instance_only)


class ChangeExtensionActionPage(ActionPage):
    def __init__(self, parent=None):
        """A widget that displays ui for the creation or modification of a change extension action"""
        super().__init__(parent)
        layout = QFormLayout(self)
        self.new_ext_input = QLineEdit()
        self.new_ext_input.setPlaceholderText(".txt")
        layout.addRow("New Extension:", self.new_ext_input)

    def build_action(self):
        """Creates the actual action object """
        new_ext = self.new_ext_input.text()
        if not new_ext or new_ext == ".":
            raise ValueError("New extension cannot be empty.")
        return ChangeExtensionAction(new_ext=new_ext)

    def load_action(self, action):
        """Sets the text boxes and checkbox """
        self.new_ext_input.setText(action.new_ext)


class ExecuteScriptActionPage(ActionPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout(self)

        self.script_type_input = QComboBox()
        self.script_type_input.addItems([
            "Python",
            "Bash",
            "Node",
            "PowerShell",
        ])
        layout.addRow("Script Type:", self.script_type_input)

        self.script_type_map = {
            "Python": "python",
            "Bash": "bash",
            "Node": "javascript",
            "PowerShell": "powershell",
        }
        self.script_type_input.currentTextChanged.connect(
            self.on_script_type_changed
        )

        self.script_input = QLineEdit()
        script_row = QHBoxLayout()
        script_row.addWidget(self.script_input)

        browse_button = QPushButton("Browse")
        browse_button.setObjectName("browseButton")
        browse_button.clicked.connect(self.choose_script)
        script_row.addWidget(browse_button)

        self.script_label = QLabel("Python script:")
        layout.addRow(self.script_label, script_row)

    def choose_script(self):
        script_type = self.script_type_map[self.script_type_input.currentText()]
        filters = {
            "python": "Python Files (*.py)",
            "bash": "Bash Files (*.sh);;All Files (*)",
            "javascript": "JavaScript Files (*.js *.mjs *.cjs)",
            "powershell": "PowerShell Files (*.ps1)",
        }

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Script",
            "",
            filters[script_type]
        )

        if file_path:
            self.script_input.setText(file_path)

    def build_action(self):
        script = self.script_input.text().strip()

        if not script:
            raise ValueError("Script path cannot be empty.")

        script_type = self.script_type_map[self.script_type_input.currentText()]
        return ExecuteScriptAction(
            Path(script).resolve(),
            script_type=script_type,
        )

    def load_action(self, action):
        self.script_input.setText(str(action.script))
        reverse_map = {value: key for key, value in self.script_type_map.items()}
        self.script_type_input.setCurrentText(reverse_map[action.script_type])

    def on_script_type_changed(self, text):
        self.script_label.setText(f"{text} script:")

class DeleteActionPage(ActionPage):
    def __init__(self, parent=None):
        """A widget that displays ui for the creation or modification of a delete action"""
        super().__init__(parent)
        layout = QFormLayout(self)
        self.trash_bin_input = QCheckBox()
        self.trash_bin_input.setChecked(True)
        layout.addRow(
            "Move to Trash:",
            self.trash_bin_input
        )

    def build_action(self):
        """Creates the actual action object """
        trash_bin = self.trash_bin_input.isChecked()
        return DeleteAction(trash_bin=trash_bin)

    def load_action(self, action):
        """Sets the checkbox """
        self.trash_bin_input.setChecked(action.trash_bin)