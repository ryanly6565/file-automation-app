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
    QSizePolicy,
)
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtCore import Qt
from src.conditions import (
    ExtensionCondition,
    NameContainsCondition,
    SizeCondition,
    AndCondition,
    OrCondition,
    NameStartsWithCondition,
    NameEndsWithCondition,
    ExactNameCondition
)

class ConditionEditor(QWidget):
    def __init__(self, condition=None, depth=0, parent=None):
        super().__init__(parent)
        self.depth = depth
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum
        )

        layout = QVBoxLayout(self)
        indent = min(self.depth * 12, 48)
        layout.setContentsMargins(indent, 0, 0, 0)

        if self.depth > 0:
            self.setStyleSheet("""
                border-left: 2px solid #d0d0d0;
            """)

        self.type_input = QComboBox()
        self.type_input.addItems([
            "Extension",
            "Name Contains",
            "Size Comparison",
            "Name Starts With",
            "Name Ends With",
            "Name Matches",
            "AND",
            "OR",
        ])

        layout.addWidget(self.type_input)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.extension_page = ExtensionConditionPage()
        self.name_page = NameContainsConditionPage()
        self.size_page = SizeConditionPage()
        self.name_starts_with_page = NameStartsWithConditionPage()
        self.name_ends_with_page = NameEndsWithConditionPage()
        self.name_matches_page = ExactNameConditionPage()
        self.and_page = AndConditionPage(depth=self.depth)
        self.or_page = OrConditionPage(depth=self.depth)

        self.stack.addWidget(self.extension_page)
        self.stack.addWidget(self.name_page)
        self.stack.addWidget(self.size_page)
        self.stack.addWidget(self.name_starts_with_page)
        self.stack.addWidget(self.name_ends_with_page)
        self.stack.addWidget(self.name_matches_page)
        self.stack.addWidget(self.and_page)
        self.stack.addWidget(self.or_page)
        self.type_input.currentIndexChanged.connect(self.on_condition_type_changed)

        if condition is not None:
            self.load_condition(condition)
        self.on_condition_type_changed(self.type_input.currentIndex())

    def build_condition(self):
        page = self.stack.currentWidget()
        return page.build_condition()

    def load_condition(self, condition):
        if isinstance(condition, ExtensionCondition):
            self.type_input.setCurrentText("Extension")
            self.extension_page.load_condition(condition)

        elif isinstance(condition, NameContainsCondition):
            self.type_input.setCurrentText("Name Contains")
            self.name_page.load_condition(condition)

        elif isinstance(condition, SizeCondition):
            self.type_input.setCurrentText("Size Comparison")
            self.size_page.load_condition(condition)

        elif isinstance(condition, NameStartsWithCondition):
            self.type_input.setCurrentText("Name Starts With")
            self.name_starts_with_page.load_condition(condition)

        elif isinstance(condition, NameEndsWithCondition):
            self.type_input.setCurrentText("Name Ends With")
            self.name_ends_with_page.load_condition(condition)

        elif isinstance(condition, ExactNameCondition):
            self.type_input.setCurrentText("Name Matches")
            self.name_matches_page.load_condition(condition)

        elif isinstance(condition, AndCondition):
            self.type_input.setCurrentText("AND")
            self.and_page.load_condition(condition)

        elif isinstance(condition, OrCondition):
            self.type_input.setCurrentText("OR")
            self.or_page.load_condition(condition)

        else:
            raise ValueError(f"Unsupported condition type: {type(condition).__name__}")

    def on_condition_type_changed(self, index):
        self.stack.setCurrentIndex(index)
        current_page = self.stack.currentWidget()

        if current_page is not None:
            # AND and OR have more variable heights than the rest, so catch these cases
            if self.type_input.currentText() in ("AND", "OR"):
                self.stack.setMinimumHeight(0)
                self.stack.setMaximumHeight(16777215)

                current_page.adjustSize()
                self.stack.adjustSize()
            else:
                height = current_page.sizeHint().height()
                if height < 0:
                    height = 0

                self.stack.setFixedHeight(height)

        self.type_input.clearFocus()
        self.setFocus()
        self.updateGeometry()

class ConditionPage(QWidget):
    """A widget that displays ui for the creation or modification of a certain condition"""
    def build_condition(self):
        raise NotImplementedError

    def load_condition(self, condition):
        raise NotImplementedError

class ExtensionConditionPage(ConditionPage):
    """A widget that displays ui for the creation or modification of an extension condition"""
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.extension_input = QLineEdit()
        self.extension_input.setPlaceholderText(".txt")

        layout.addRow("Extension:", self.extension_input)

    def build_condition(self):
        """Creates the actual condition object """
        extension = self.extension_input.text().strip()

        # error validation
        if not extension:
            raise ValueError("Extension cannot be empty.")
        if not extension.startswith("."):
            extension = "." + extension
        return ExtensionCondition(extension)

    def load_condition(self, condition):
        """Sets the extension text box to a specific value """
        self.extension_input.setText(condition.extension)


class NameContainsConditionPage(ConditionPage):
    """A widget that displays ui for the creation or modification of a name contains condition"""
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.text_input = QLineEdit()

        self.case_sensitive_input = QCheckBox()
        self.case_sensitive_input.setChecked(True)

        layout.addRow("Text:", self.text_input)
        layout.addRow(
            "Case sensitive:",
            self.case_sensitive_input,
        )

    def build_condition(self):
        """Creates the actual condition object """
        text = self.text_input.text()

        # error validation
        if not text:
            raise ValueError("Substring cannot be empty.")
    
        return NameContainsCondition(
            text,
            case_matters=self.case_sensitive_input.isChecked(),
        )

    def load_condition(self, condition):
        """Sets the name text box and the case sensitive check box to be a value """
        self.text_input.setText(condition.substr)
        self.case_sensitive_input.setChecked(
            condition.case_matters
        )


class SizeConditionPage(ConditionPage):
    """A widget that displays ui for the creation or modification of a size condition"""
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.comparison_input = QComboBox()
        self.comparison_input.addItems([
            "Greater than",
            "Greater than or equal",
            "Less than",
            "Less than or equal",
            "Equal to"
        ])

        self.size_input = QSpinBox()
        self.size_input.setMinimum(0)
        self.size_input.setMaximum(2_000_000_000)

        size_row = QHBoxLayout()
        size_row.addWidget(self.comparison_input)
        size_row.addWidget(self.size_input)
        size_row.addWidget(QLabel("bytes"))

        layout.addRow("If file size is:", size_row)

    def build_condition(self):
        """Creates the actual condition object """
        comparison_map = {
            "Greater than": "gt",
            "Greater than or equal": "gte",
            "Equal to": "eq",
            "Less than": "lt",
            "Less than or equal": "lte",
        }
        
        comparison = comparison_map.get(self.comparison_input.currentText())

        # error validation
        if self.size_input.value() < 0:
            raise ValueError("Size cannot be negative.")
        
        return SizeCondition(
            size=self.size_input.value(),
            comparison=comparison
        )
    
    def load_condition(self, condition):
        """Sets the size text box and the greater/less than check boxand the scrict checkbox to be a value """
        self.size_input.setValue(condition.size)
        comparison_map = {
            "gt": "Greater than",
            "gte": "Greater than or equal",
            "eq": "Equal to",
            "lt": "Less than",
            "lte": "Less than or equal",
        }

        self.size_input.setValue(condition.size)
        self.comparison_input.setCurrentText(
            comparison_map.get(condition.comparison)
        )


class NameStartsWithConditionPage(ConditionPage):
    """A widget that displays ui for the creation or modification of a name starts with condition"""
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.text_input = QLineEdit()

        self.case_sensitive_input = QCheckBox()
        self.case_sensitive_input.setChecked(True)
        self.include_extension_input = QCheckBox()
        self.include_extension_input.setChecked(True)

        layout.addRow("Text:", self.text_input)
        layout.addRow("Case sensitive:", self.case_sensitive_input,)
        layout.addRow("Include extension:", self.include_extension_input,)

    def build_condition(self):
        """Creates the actual condition object """
        text = self.text_input.text()

        # error validation
        if not text:
            raise ValueError("Substring cannot be empty.")
    
        return NameStartsWithCondition(
            text,
            case_matters=self.case_sensitive_input.isChecked(),
            include_extension=self.include_extension_input.isChecked()
        )

    def load_condition(self, condition):
        """Sets the name text box, case sensitive check box, and include extension check box 
           to be a value based on the given condition """
        self.text_input.setText(condition.substr)
        self.case_sensitive_input.setChecked(condition.case_matters)
        self.include_extension_input.setChecked(condition.include_extension)


class NameEndsWithConditionPage(ConditionPage):
    """A widget that displays ui for the creation or modification of a name ends with condition"""
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.text_input = QLineEdit()

        self.case_sensitive_input = QCheckBox()
        self.case_sensitive_input.setChecked(True)
        self.include_extension_input = QCheckBox()
        self.include_extension_input.setChecked(True)

        layout.addRow("Text:", self.text_input)
        layout.addRow("Case sensitive:", self.case_sensitive_input,)
        layout.addRow("Include extension:", self.include_extension_input,)

    def build_condition(self):
        """Creates the actual condition object """
        text = self.text_input.text()

        # error validation
        if not text:
            raise ValueError("Substring cannot be empty.")
    
        return NameEndsWithCondition(
            text,
            case_matters=self.case_sensitive_input.isChecked(),
            include_extension=self.include_extension_input.isChecked()
        )

    def load_condition(self, condition):
        """Sets the name text box, case sensitive check box, and include extension check box 
           to be a value based on the given condition """
        self.text_input.setText(condition.substr)
        self.case_sensitive_input.setChecked(condition.case_matters)
        self.include_extension_input.setChecked(condition.include_extension)


class ExactNameConditionPage(ConditionPage):
    """A widget that displays ui for the creation or modification of an exact name match condition"""
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.text_input = QLineEdit()

        self.case_sensitive_input = QCheckBox()
        self.case_sensitive_input.setChecked(True)
        self.include_extension_input = QCheckBox()
        self.include_extension_input.setChecked(True)

        layout.addRow("Text:", self.text_input)
        layout.addRow("Case sensitive:", self.case_sensitive_input,)
        layout.addRow("Include extension:", self.include_extension_input,)

    def build_condition(self):
        """Creates the actual condition object """
        text = self.text_input.text()

        # error validation
        if not text:
            raise ValueError("Name cannot be empty.")
    
        return ExactNameCondition(
            text,
            case_matters=self.case_sensitive_input.isChecked(),
            include_extension=self.include_extension_input.isChecked()
        )

    def load_condition(self, condition):
        """Sets the name text box, case sensitive check box, and include extension check box 
           to be a value based on the given condition """
        self.text_input.setText(condition.match_str)
        self.case_sensitive_input.setChecked(condition.case_matters)
        self.include_extension_input.setChecked(condition.include_extension)


class AndConditionPage(ConditionPage):
    """A widget that displays ui for the creation or modification of an and condition"""
    def __init__(self, conditions=None, depth=0, parent=None):
        super().__init__(parent)

        self.depth = depth
        self.condition_editors = []

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # container for list of child conditions, add indentation at lower depths
        self.conditions_frame = QFrame()
        self.conditions_frame.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum
        )
        self.conditions_frame.setObjectName("conditionGroup")

        self.conditions_frame.setStyleSheet("""
            QFrame#conditionGroup {
                border: none;
                border-left: 2px solid #888888;
            }
        """)
        self.conditions_layout = QVBoxLayout(self.conditions_frame)
        self.conditions_layout.setContentsMargins(12, 0, 0, 0)

        self.layout.addWidget(self.conditions_frame)

        add_button = QPushButton("+ Add Condition")
        add_button.setObjectName("conditionAddButton")
        add_button.clicked.connect(lambda: self.add_condition())    # added in case an additional argument is given
        self.layout.addWidget(add_button)

        # existing conditions when editing
        if conditions is not None:
            for condition in conditions:
                self.add_condition(condition)

    def add_condition(self, condition=None):
        """ Adds a condition to the list of conditions """
        editor = ConditionEditor(
            condition=condition,
            depth=self.depth + 1,
        )

        self.condition_editors.append(editor)
        self.conditions_layout.addWidget(editor)

        self.conditions_frame.adjustSize()
        self.adjustSize()
        self.updateGeometry()

    def build_condition(self):
        """Creates the actual condition object """
        conditions = [
            editor.build_condition()
            for editor in self.condition_editors
        ]

        # error validation
        if len(conditions) == 0:
            raise ValueError("And conditions need at least one child condition.")
        
        return AndCondition(conditions)

    def load_condition(self, condition):
        """Sets the size text box and the greater/less than check boxand the scrict checkbox to be a value """
        # clear existing editors
        for editor in self.condition_editors:
            editor.deleteLater()

        self.condition_editors.clear()

        for child_condition in condition.conditions:
            self.add_condition(child_condition)

        # make the updated contents appear right away
        self.conditions_frame.adjustSize()
        self.adjustSize()
        self.updateGeometry()

class OrConditionPage(ConditionPage):
    """A widget that displays ui for the creation or modification of an or condition"""
    def __init__(self, conditions=None, depth=0, parent=None):
        super().__init__(parent)

        self.depth = depth
        self.condition_editors = []

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.conditions_frame = QFrame()
        self.conditions_frame.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum
        )
        self.conditions_frame.setObjectName("conditionGroup")

        self.conditions_frame.setStyleSheet("""
            QFrame#conditionGroup {
                border: none;
                border-left: 2px solid #888888;
            }
        """)
        self.conditions_layout = QVBoxLayout(self.conditions_frame)
        self.conditions_layout.setContentsMargins(12, 0, 0, 0)

        self.layout.addWidget(self.conditions_frame)

        add_button = QPushButton("+ Add Condition")
        add_button.clicked.connect(lambda: self.add_condition())
        self.layout.addWidget(add_button)

        if conditions is not None:
            for condition in conditions:
                self.add_condition(condition)

    def add_condition(self, condition=None):
        """ Adds a condition to the list of conditions """
        editor = ConditionEditor(
            condition=condition,
            depth=self.depth + 1,
        )
        self.condition_editors.append(editor)
        self.conditions_layout.addWidget(editor)

        self.conditions_frame.adjustSize()
        self.adjustSize()
        self.updateGeometry()

    def build_condition(self):
        """Creates the actual condition object """
        conditions = [
            editor.build_condition()
            for editor in self.condition_editors
        ]

        # error validation
        if len(conditions) == 0:
            raise ValueError("Or conditions need at least one child condition.")
        
        return OrCondition(conditions)

    def load_condition(self, condition):
        """Sets the size text box and the greater/less than check boxand the scrict checkbox to be a value """
        for editor in self.condition_editors:
            editor.deleteLater()

        self.condition_editors.clear()

        for child_condition in condition.conditions:
            self.add_condition(child_condition)

        # make the updated contents appear right away
        self.conditions_frame.adjustSize()
        self.adjustSize()
        self.updateGeometry()